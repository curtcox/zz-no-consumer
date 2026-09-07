# Git commit and push investigation — 7 September 2026

The institutional image batch was committed as `ea22fce2` and pushed to origin/main.
The recurring staging failure has a reproducible mechanism and a repository-local
mitigation: `diff.autoRefreshIndex=false`. Push networking was a separate sandbox
restriction. No remote, credentials, global Git configuration, or application bundle
was changed.

## Evidence and confidence

The original UI error occurred during `git add -u`, before commit or push. Later
recovery checks repeatedly found empty index locks with no Git process or open
handle. That established a recovery basis, but did not identify their creator.

This investigation compared the two most recent lock timestamps with the desktop's
Git logs. Both land within canceled `review_model` / `review-summary` diff runs:

| Lock inode | Lock modification time, UTC | Background diff interval, UTC | Command ID |
| --- | --- | --- | --- |
| 62751244 | 19:01:10.481311 | 19:01:10.329–19:01:10.526 | ba1ebdf4 |
| 62753423 | 19:06:37.344535 | 19:06:36.897–19:06:37.396 | 197ac485 |

[correlation.json](correlation.json) preserves selected fields and local log locators.
It excludes unrelated log content and environment values. The actual creator PID
was not captured; timing correlation alone is not proof of ownership. Earlier
canceled status operations exist too, but those are not the best match for these
two recurrences.

Read-only inspection of ChatGPT desktop 26.901.51231, build 8109, found that its
bundled Git worker supplies `GIT_OPTIONAL_LOCKS=0`, requests process-tree killing,
and uses `SIGKILL` for that Unix cancellation path. The worker asset hash is saved
in the correlation record; the application was not patched. This evidence corrects
the tempting explanation that the app simply forgot the optional-lock setting.

Git 2.55.0's [diff implementation](https://github.com/git/git/blob/v2.55.0/builtin/diff.c#L222-L234)
takes an index lock in `refresh_index_quietly`; its final refresh call is gated by
`skip_stat_unmatch`, without a `get_optional_locks()` guard at that call site.
The isolated experiments below demonstrate the resulting behavior on both installed
Git versions. The likely sequence is: site rebuild rewrites otherwise identical
files, their cached stat data becomes stale, a background diff refreshes the index,
and cancellation interrupts the refresh while its lock exists. This strongly
supports the mechanism of these recurrences; it does not retroactively identify
every earlier lock's owner.

## Reproduction and checks

Run from the repository root:

```sh
python3 scripts/git_lock_probe.py check
python3 scripts/git_lock_probe.py check --git /usr/bin/git
```

The standard-library diagnostic creates its own temporary Git repository with
1,800 small tracked text files and one binary. It changes their timestamps without
changing content,
watches for a diff refresh lock, and signals only the child it started. It never
signals the user's Git processes or removes the live repository's lock. Fixture
locks are removed only after their child exits. Initial trials with content-only
changes did not reproduce the lock; stale stat data on unchanged content was the
necessary trigger in the successful fixture.

| Case | Git 2.55.0 | Apple Git 2.50.1 |
| --- | --- | --- |
| Default diff, SIGKILL when lock appears | Lock left behind | Lock left behind |
| `--no-optional-locks`, same interruption | Lock left behind | Lock left behind |
| `GIT_OPTIONAL_LOCKS=0`, same interruption | Lock left behind | Lock left behind |
| Default diff, immediate SIGTERM when lock appears | Lock left behind | Lock left behind |
| `diff.autoRefreshIndex=false` | Completed, no observed lock | Completed, no observed lock |
| Raw diff, line counts and diffstat after explicit refresh | Identical with mitigation | Identical with mitigation |
| Staging against an intentional existing fixture lock | Refused, lock preserved | Refused, lock preserved |

Exact outputs: [Homebrew Git](homebrew-git.json), [Apple Git](apple-git.json).
The SIGTERM observation is timing-sensitive; it does not establish that graceful
termination always fails. It does show why changing the signal alone is not the
validated fix here. The diagnostic reports missed reproduction windows separately;
it requires the mitigation and diff/writer checks to pass, rather than requiring a
future Git version to preserve the original defect.

## Mitigation applied

```sh
git config --local diff.autoRefreshIndex false
git --no-optional-locks config --show-origin --get diff.autoRefreshIndex
```

The second command returned `file:.git/config false`. No previous local value was
present. This is a documented [Git setting](https://git-scm.com/docs/git-config#Documentation/git-config.txt-diffautoRefreshIndex).
It stops porcelain diff from doing its automatic index-stat refresh. It leaves
staging and commit locking intact. It is local to this repository configuration
and must be set explicitly in a new clone. A command-line
`-c diff.autoRefreshIndex=false` supplies the same policy for a single diff.

**Tradeoff found during the live rebuild:** unchanged binary assets appeared in
`git diff --stat` with identical before/after sizes, while `git status` correctly
reported only the real edits. Refresh their cached stat data explicitly after a
rebuild, with one session owning the index write:

```sh
git update-index --refresh
```

This does not stage content. Exit 1 with `needs update` lines can identify genuine
modified/deleted files while successfully refreshing unchanged files; inspect the
output rather than accepting every exit 1. An index-lock or other fatal error is
still a blocker. The live refresh listed only the three edited instruction files,
and the subsequent diffstat listed only those files. The improved fixture compares
both HEAD and unstaged raw/diffstat output, using timestamps several seconds apart
to avoid depending on nanosecond stat support. Its before/after-refresh results
document the tradeoff. Keep this refresh explicit and coordinated; putting it in
an automatically canceled background operation would restore the original risk.
Repeated comparisons before refresh may also do extra work.

Continue using `--no-optional-locks` for read-only commands, particularly status.
Git's [optional-lock documentation](https://git-scm.com/docs/git#Documentation/git.txt-GITOPTIONALLOCKS)
describes the background-status use case, but that flag alone did not protect the
tested diff refresh path. Continue serializing writers; this mitigation does not
prevent every possible lock conflict or interrupted mandatory write.

Rollback, if needed: `git config --local --unset diff.autoRefreshIndex`. That restores
the previously unset state and re-enables the default refresh behavior. Do not use
automatic lock deletion. Follow the [live recovery procedure](../../README.md#git-coordination-and-incident-record)
if a lock recurs, and capture fresh evidence instead of assuming the same cause.

A site rebuild with the desktop active exercises the original rewrite trigger.
[build-check.json](build-check.json) records the build result and 10 ms lock polling;
polling can miss brief locks and cannot guarantee absence of all future recurrences.
The fixture is stronger evidence for the mechanism than a short quiet observation.

## Push diagnosis

Sandboxed `git ls-remote` reported `Could not resolve host: github.com`. The authorized
host-level `git push origin main` succeeded, advancing `091152e2` to `ea22fce2`.
This is evidence for restricted network access in the command environment, not a
broken remote, bad credentials, branch divergence, or index corruption. No force
push is needed. Use the normal network approval path and compare local HEAD with
the actual remote ref after pushing; a cached remote-tracking ref alone is weaker
verification. A push to main triggers this repository's Pages workflow, whose
deployment status is separate from Git push success.

Commit sequences should stop on a failed stage or commit (`subprocess.run(...,
check=True)` or shell `&&`). A prior guarded cleanup initially compared a rounded
timestamp with nanoseconds and correctly refused removal; its following unguarded
shell commands nevertheless tried staging and commit. The corrected recovery used
the precise timestamp and fail-fast subprocess calls. No failed command changed
the index. Keep recovery checks and Git writes sequential.

## Upstream follow-up

The durable app-side correction would explicitly disable diff auto-refresh in
background review commands, in addition to optional locks, and retain orderly
cancellation/cleanup. The repository setting is a workaround, not an installed
application update. No issue or message has been sent. This record contains the
version, reproduction, selected timing evidence and limits needed for a report.
Official [desktop troubleshooting](https://learn.chatgpt.com/docs/reference/troubleshooting)
documents feedback and log locations. [Worktree guidance](https://learn.chatgpt.com/docs/environments/git-worktrees)
helps isolate independent writers, but a worktree alone does not eliminate an
interrupted background refresh of its own index.
