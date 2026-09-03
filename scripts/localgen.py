#!/usr/bin/env python3
"""Run the bake-off on open weights on this machine, with no key and no spend.

Local models change the arithmetic rather than just the price. There is no cost
per image, the weights cannot move underneath a half-finished book, and a style
LoRA trained here belongs to us. In exchange they impose two limits the hosted
candidates do not:

  * A licence. FLUX.1 [dev], FLUX.2 [klein] 9B, and FLUX.2 [dev] are non-commercial
    weights, so nothing they generate may appear in a published book. They are
    skipped unless `--allow-non-commercial` is passed, and any run containing them
    is stamped evaluation-only in the manifest and on the published sheet.
  * A wall clock. The book needs about 3,900 generations. At a minute each that is
    65 hours of continuous compute, so `estimate` prices a local run in hours
    rather than dollars, using measured times once a run has produced some.

    python3 scripts/localgen.py doctor     # this Mac, and what it can actually run
    python3 scripts/localgen.py estimate   # wall clock for a run and for the book
    python3 scripts/localgen.py run        # generate and write the comparison sheet

The roster lives in `data/local-models.json` because local tooling churns faster
than the hosted roster does. `doctor` checks that file against what is installed
and reports the difference rather than failing mid-run.

The command-backed models call `mflux`, an MLX-native port that runs on Apple
Silicon (`uv tool install mflux`, then `uv tool list` for the exact command
names). The HTTP-backed ones want a local server — Draw Things' API server or
ComfyUI behind a bridge — answering the OpenAI images shape.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import imagegen


ROOT = imagegen.ROOT
ROUTE = "local"


def unified_memory_gb() -> float | None:
    """How much memory this machine actually has, when we can find out."""
    try:
        if hasattr(os, "sysconf") and "SC_PAGE_SIZE" in os.sysconf_names:
            total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            return total / 1024 ** 3
    except (ValueError, OSError):
        pass
    return None


def chip() -> str:
    try:
        finished = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                  capture_output=True, text=True, timeout=5, check=False)
        return finished.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def server_listening(url: str, timeout: float = 0.4) -> bool:
    """Whether anything is answering on the endpoint's host and port."""
    parts = urllib.parse.urlsplit(url)
    if not parts.hostname:
        return False
    port = parts.port or (443 if parts.scheme == "https" else 80)
    try:
        with socket.create_connection((parts.hostname, port), timeout):
            return True
    except OSError:
        return False


def roster() -> list[imagegen.Provider]:
    return list(imagegen.LOCAL)


def eligible(providers: list[imagegen.Provider], *, memory: float | None,
             allow_non_commercial: bool) -> list[imagegen.Provider]:
    """The models this machine has the memory and the licence to run."""
    kept = []
    for provider in providers:
        if not provider.commercial and not allow_non_commercial:
            continue
        if memory is not None and provider.fits_gb > memory + 0.5:
            continue
        kept.append(provider)
    return kept


def measured_seconds() -> dict[str, float]:
    """Median seconds per image per model, pooled across every committed run."""
    pooled: dict[str, list[float]] = {}
    for run in imagegen.run_directories(imagegen.DEFAULT_RUN_DIR):
        manifest = imagegen.load_manifest(run)
        if manifest.get("dry_run"):
            continue
        for name, value in imagegen.median_seconds(manifest).items():
            pooled.setdefault(name, []).append(value)
    return {name: sorted(values)[len(values) // 2] for name, values in pooled.items()}


def cmd_doctor(args: argparse.Namespace) -> int:
    memory = unified_memory_gb()
    print(f"Machine: {chip()}")
    print(f"Memory:  {memory:.0f} GB unified" if memory else "Memory:  unknown")
    if memory:
        print(f"Usable:  about {max(memory - 5, 0):.0f} GB, "
              f"after roughly 5 GB for macOS and the runtime")

    binaries = sorted(
        Path(entry).name
        for directory in os.environ.get("PATH", "").split(os.pathsep) if directory
        for entry in Path(directory).glob("mflux-generate*") if os.access(entry, os.X_OK)
    ) if os.environ.get("PATH") else []
    print(f"\nmflux commands on PATH: {', '.join(dict.fromkeys(binaries)) or 'none'}")

    seconds = measured_seconds()
    print(f"\n{'ID':<20} {'NEEDS':>6} {'BACKEND':<8} {'STATE':<24} {'S/IMG':>7} LICENCE")
    ready = 0
    for provider in roster():
        if provider.build == "command":
            binary = provider.command[0] if provider.command else "?"
            state, ok = ("installed", True) if shutil.which(binary) else (f"missing {binary}", False)
        elif server_listening(provider.local_url):
            state, ok = "server answering", True
        else:
            port = urllib.parse.urlsplit(provider.local_url).port or "?"
            state, ok = f"start server :{port}", False

        if memory is not None and provider.fits_gb > memory + 0.5:
            state, ok = f"needs {provider.fits_gb} GB", False
        if not provider.commercial:
            state = f"{state} · eval"
        ready += ok and provider.commercial

        rate = seconds.get(provider.id, provider.seconds_per_image)
        mark = "" if provider.id in seconds else "~"
        print(f"{provider.id:<20} {provider.fits_gb:>4} GB {provider.build:<8} "
              f"{state if len(state) <= 24 else state[:23] + '…':<24} "
              f"{mark}{rate:>6.0f} {provider.licence}")

    print(f"\n{ready} model(s) ready now, on a licence whose output can go in the book. "
          f"'~' marks an estimate rather than a measured time.")
    if not binaries:
        print("Install the MLX runner with:  uv tool install mflux")
        print("Then list the exact command names with:  uv tool list")
    return 0


def cmd_estimate(args: argparse.Namespace) -> int:
    memory = unified_memory_gb()
    samples = imagegen.chosen_samples(args.sample)
    images = len(samples) * args.repeat
    seconds = measured_seconds()
    providers = eligible(roster(), memory=memory,
                         allow_non_commercial=args.allow_non_commercial)

    if not providers:
        print(f"Nothing on the local roster fits {memory:.0f} GB under a shippable licence."
              if memory else "Nothing on the local roster is eligible.")
        return 1

    print(f"{len(providers)} model(s) × {len(samples)} panel(s) × {args.repeat} take(s) "
          f"= {len(providers) * images} images, no key and no spend\n")
    print(f"{'ID':<20} {'S/IMAGE':>8} {'RUN':>9} {'FULL BOOK':>11}  LICENCE")
    span = 0.0
    for provider in providers:
        rate = seconds.get(provider.id, provider.seconds_per_image)
        mark = "" if provider.id in seconds else "~"
        span += images * rate
        print(f"{provider.id:<20} {mark}{rate:>7.0f} {images * rate / 60:>7,.0f} m "
              f"{provider.full_book_hours(rate):>9,.0f} h  {provider.licence}")

    print(f"\nWhole run: about {span / 60:,.0f} minutes of compute on this machine.")
    print(f"For comparison, the same six panels through OpenRouter cost about "
          f"$5 and finish in minutes: python3 scripts/bakeoff.py estimate")
    if memory:
        skipped = [p.id for p in roster() if p.fits_gb > memory + 0.5]
        if skipped:
            print(f"Too large for {memory:.0f} GB: {', '.join(skipped)}.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    memory = unified_memory_gb()
    providers = eligible(
        imagegen.selected(args.provider) if args.provider else roster(),
        memory=None if args.ignore_memory else memory,
        allow_non_commercial=args.allow_non_commercial,
    )
    providers = [provider for provider in providers if provider.local]
    if not providers:
        raise SystemExit(
            "No eligible local model. Run `python3 scripts/localgen.py doctor` to see why — "
            "usually nothing is installed yet, or the only fits are non-commercial weights "
            "that need --allow-non-commercial."
        )

    base = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    stamp = args.run or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ-local")
    directory = base / stamp
    samples = imagegen.chosen_samples(args.sample)

    print(f"Run {stamp} on {chip()} → {directory.relative_to(ROOT)}")
    if args.allow_non_commercial:
        print("Including non-commercial weights. This run is evaluation only; "
              "nothing it produces may appear in the book.")

    manifest = imagegen.run_samples(
        directory,
        providers,
        samples,
        repeat=args.repeat,
        dry_run=args.dry_run,
        route=ROUTE,
        allow_non_commercial=args.allow_non_commercial,
    )
    manifest["machine"] = chip()
    if memory:
        manifest["memory_gb"] = round(memory)
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8")
    imagegen.report_run(directory, manifest)

    seconds = imagegen.median_seconds(manifest)
    if seconds:
        print("\nMeasured seconds per image:")
        for name, value in sorted(seconds.items(), key=lambda item: item[1]):
            hours = imagegen.PROVIDERS_BY_ID[name].full_book_hours(value)
            print(f"  {name:<20} {value:>6.0f} s   full book {hours:,.0f} h")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def licence_option(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--allow-non-commercial", action="store_true",
            help="include weights whose licence forbids shipping their output")

    commands.add_parser("doctor", help="this machine, and what it can actually run")

    estimate = commands.add_parser("estimate", help="wall clock for a run and for the book")
    estimate.add_argument("--sample", action="append")
    estimate.add_argument("--repeat", type=int, default=2)
    licence_option(estimate)

    run = commands.add_parser("run", help="generate locally and write the comparison sheet")
    run.add_argument("--out-dir", type=Path, default=imagegen.DEFAULT_RUN_DIR)
    run.add_argument("--run", help="run directory name; defaults to a UTC timestamp")
    run.add_argument("--provider", action="append", help="local model id; repeatable")
    run.add_argument("--sample", action="append", help="panel id such as 001-01; repeatable")
    run.add_argument("--repeat", type=int, default=2,
                     help="takes per panel; more than one exposes style drift")
    run.add_argument("--dry-run", action="store_true",
                     help="write prompt placeholders instead of running any model")
    run.add_argument("--ignore-memory", action="store_true",
                     help="run a model larger than this machine, and let it swap")
    licence_option(run)

    args = parser.parse_args()
    return {"doctor": cmd_doctor, "estimate": cmd_estimate, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
