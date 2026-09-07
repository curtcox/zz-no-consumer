#!/usr/bin/env python3
"""Reproduce canceled diff refresh locks in a disposable repository, never this checkout.

The check kills only subprocesses it creates. It removes only fixture locks after
their owning child has exited. This is not a live-repository lock recovery tool.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time


def check(git):
    # Exclude inherited Git routing/configuration without printing the environment.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Lock probe", GIT_AUTHOR_EMAIL="probe@example.invalid",
               GIT_COMMITTER_NAME="Lock probe", GIT_COMMITTER_EMAIL="probe@example.invalid")
    failures = []
    with tempfile.TemporaryDirectory(prefix="git-lock-probe-") as directory:
        root = Path(directory)

        def run(*args, extra_env=None):
            return subprocess.run([git, *args], cwd=root,
                                  env={**env, **(extra_env or {})},
                                  capture_output=True, check=True, timeout=30).stdout

        run("init", "-q")
        files = [root / f"file-{i:04}.txt" for i in range(1800)]
        for i, path in enumerate(files):
            path.write_text(f"unchanged fixture {i}\n", encoding="utf-8")
        binary = root / "unchanged.bin"
        binary.write_bytes(b"\x00" + bytes(range(256)) * 32)
        files.append(binary)
        run("add", ".")
        run("commit", "-qm", "fixture baseline")
        lock = root / ".git" / "index.lock"
        index = root / ".git" / "index"
        diff = ["diff", "HEAD", "--find-renames", "--raw", "--no-abbrev", "--numstat", "-z"]

        touch_count = 0

        def touch():
            nonlocal touch_count
            touch_count += 1
            # Deliberately stale stat data, but unchanged contents. No sleep or
            # wall-clock-second race with the just-written index is needed.
            timestamp = time.time_ns() + touch_count * 10_000_000_000
            for path in files:
                if path.exists():
                    os.utime(path, ns=(timestamp, timestamp))

        observations = []
        cases = [
            ("default-SIGKILL", [], {}, signal.SIGKILL),
            ("no-optional-locks-SIGKILL", ["--no-optional-locks"], {}, signal.SIGKILL),
            ("env-no-optional-locks-SIGKILL", [], {"GIT_OPTIONAL_LOCKS": "0"}, signal.SIGKILL),
            ("default-SIGTERM", [], {}, signal.SIGTERM),
            ("auto-refresh-disabled", ["-c", "diff.autoRefreshIndex=false"], {}, signal.SIGKILL),
        ]
        for name, flags, extra_env, stop_signal in cases:
            touch()
            index_hash = hashlib.sha256(index.read_bytes()).hexdigest()
            if lock.exists():
                raise RuntimeError("Unexpected fixture lock before spawning a child")
            observed = False
            timed_out = False
            with subprocess.Popen([git, *flags, *diff], cwd=root,
                                  env={**env, **extra_env}, stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL) as child:
                deadline = time.monotonic() + 15
                try:
                    while child.poll() is None:
                        if lock.exists():
                            observed = True
                            child.send_signal(stop_signal)
                            break
                        if time.monotonic() >= deadline:
                            timed_out = True
                            child.kill()
                            break
                    child.wait(timeout=5)
                finally:
                    if child.poll() is None:
                        child.kill()
                        child.wait()
            leftover = lock.exists()
            observations.append(dict(case=name, observed_lock=observed,
                                     exit_code=child.returncode, leftover_lock=leftover,
                                     timed_out=timed_out))
            if timed_out:
                failures.append(f"{name}: subprocess timed out")
            if name == "auto-refresh-disabled" and (observed or leftover or child.returncode != 0):
                failures.append("Disabling diff auto-refresh did not prevent the lock")
            if name == "auto-refresh-disabled" and hashlib.sha256(index.read_bytes()).hexdigest() != index_hash:
                failures.append("Disabling auto-refresh still changed the fixture index")
            # Safe only because this is our private fixture and its child is reaped.
            if leftover:
                lock.unlink()

        # Disabling auto-refresh can report stat-only binary changes. Compare
        # both raw and display output, then verify explicit refresh resolves them.
        files[0].write_text("real edit\n", encoding="utf-8")
        files[1].unlink()
        files[2].rename(root / "renamed.txt")
        run("add", "file-0002.txt", "renamed.txt")
        comparisons = [diff, ["diff", "HEAD", "--stat"],
                       ["diff", "--stat"], ["diff", "--raw", "--numstat", "-z"]]
        outputs = []
        for setting in ("true", "false"):
            values = []
            for command in comparisons:
                touch()
                values.append(run("-c", f"diff.autoRefreshIndex={setting}", *command))
            outputs.append(values)
        same_before_refresh = outputs[0] == outputs[1]
        # --refresh exits 1 for known content edits/deletions while refreshing
        # unchanged files. Other exit codes are failures, not stale-lock recovery.
        refresh = subprocess.run([git, "update-index", "--refresh"], cwd=root,
                                 env=env, capture_output=True, timeout=30)
        if refresh.returncode not in (0, 1):
            failures.append("Explicit fixture refresh failed")
        refreshed = [run("-c", "diff.autoRefreshIndex=false", *command)
                     for command in comparisons]
        same_after_refresh = outputs[0] == refreshed and bool(refreshed[0])
        if not same_after_refresh:
            failures.append("Diff output changed after the explicit fixture refresh")

        # Optional refresh is disabled, but a mandatory writer must still honor
        # an existing lock. This fixture lock is intentional and never live data.
        lock.write_bytes(b"fixture lock\n")
        try:
            result = subprocess.run([git, "-c", "diff.autoRefreshIndex=false", "add", "."],
                                    cwd=root, env=env, capture_output=True, timeout=30)
            writer_blocked = result.returncode != 0 and b"index.lock" in result.stderr
            if not writer_blocked or lock.read_bytes() != b"fixture lock\n":
                failures.append("Mandatory writer did not preserve the existing fixture lock")
        finally:
            lock.unlink()

        return dict(git=run("--version").decode().strip(), observations=observations,
                    diff_output_unchanged_before_refresh=same_before_refresh,
                    diff_output_unchanged_after_refresh=same_after_refresh,
                    explicit_refresh_exit_code=refresh.returncode,
                    mandatory_writer_blocked=writer_blocked,
                    baseline_reproduced=observations[0]["leftover_lock"], failures=failures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check"])
    parser.add_argument("--git", default="git", help="Git executable to test")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("This SIGKILL/SIGTERM diagnostic requires a POSIX host")
    git = shutil.which(args.git)
    if git is None:
        parser.error(f"Git executable not found: {args.git}")
    result = check(str(Path(git).resolve()))
    print(json.dumps(result, indent=2))
    # A missed timing window or a future Git fix need not reproduce the defect;
    # report that separately. The mitigation and semantic checks must pass.
    return bool(result["failures"])


if __name__ == "__main__":
    raise SystemExit(main())
