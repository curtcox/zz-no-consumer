# Git index-lock contention — diagnosis and follow-up steps

**Do not act on anything in the "Follow-up steps" section without asking Curt first.**
Every item below is a proposal, not a work list. They are recorded so the reasoning is not
re-derived from scratch, and each one changes either the publishing setup or how sessions are
run. Raise the item, get an explicit yes, then do it. An agent that finds this file has not
been authorized by finding it.

Investigated 2026-09-07 after two `.git/index.lock` failures — one on the morning of
7 September, one the evening of 6 September or the early morning of 7 September.

## What was happening

Several AI agent sessions were live in the same working tree at once. At 10:27 on
7 September, 25 processes had their working directory set to the repository root: three
ChatGPT/Codex sessions started at 08:50, 08:55 and 09:11 with newer process groups at 10:18
and 10:21, one Claude Code session, a `python3 -m http.server 8765 --directory docs`, and two
interactive shells. The Codex rollout logs show those sessions running `git status --short`,
`git diff --check`, `git diff --stat` and `git diff --numstat` against this repository
through the morning.

Both failures fall inside those windows. The 08:48 commit (536 files) and the 08:53 commit
sit between Codex sessions starting at 08:50 and 08:55; the 10:24 commit (159 files) sits
between the 10:18/10:21 Codex groups and a Claude Code session at 10:26.

**A plain `git status` is a write command.** It rewrites the index whenever stat data is
stale, which means it takes `.git/index.lock`. Measured in a scratch repository:

```
no-optional-locks: before=1788794960.332690163 after=1788794960.332690163  changed=NO
plain status:      before=1788794960.332690163 after=1788794969.673073193  changed=YES
```

Two things widened the collision window recently. `docs/` is tracked generated output —
3,256 tracked files, 2,790 of them rewritten on 7 September — so every build dirties the
whole stat cache and the next `git status` from every session has to re-stat and rewrite a
546 KB index instead of doing a fast no-op. And recent commits are unusually broad (536, 159
and 116 files) against 30–50 file commits earlier in the week. A warm `git status --porcelain`
measures 0.05 s, which is why the failures are occasional rather than constant.

A second mechanism produces the *stale* locks that do not clear on retry: a git process
killed mid-write strands its lock file. Codex runs sandboxed and Claude Code kills bash
commands on interrupt, so either can leave one behind.

## Done

- **AGENTS.md now specifies `git --no-optional-locks` for read-only git calls** in "Start
  here" steps 1 and 4, with the reason inline so it is not silently reverted. This removes
  the largest lock-taker: the status call every session makes before it does anything else.

## Ruled out

- **Per-agent `git worktree`.** Rejected by Curt on 7 September 2026. Serial working
  discipline is the intended mitigation instead.
- **Deliberate parallel agent sessions.** Same decision. The intent is to run one agent at a
  time.

## Follow-up steps

Again: **ask Curt before doing any of these.**

1. **Write the serial-working discipline into AGENTS.md.** Since worktrees are ruled out,
   the guard against overlap is that only one session works at a time. Worth stating, with
   the check that makes it real — before starting, confirm no other agent is live:

   ```sh
   lsof -a -d cwd "$PWD" | grep -vE 'lsof|grep'
   ```

   Open question for Curt: whether this belongs in AGENTS.md as an instruction to agents, or
   stays a habit on his side. An agent cannot enforce it on itself, which argues for the
   latter.

2. **Document stale-lock hygiene.** When a lock error appears, distinguish contention from a
   stranded lock before deleting anything:

   ```sh
   pgrep -fl "git " ; ls -la .git/*.lock
   ```

   No git process listed means the lock is stale and safe to remove. A process listed means
   wait. Unresolved: whether this goes in AGENTS.md, README.md, or nowhere.

3. **Reconsider tracking `docs/` on `main`.** This is the structural cause of the wide
   collision window, and the largest change proposed here. Building rewrites ~2,790 tracked
   files, turning every subsequent status call into a full index rewrite. Publishing from CI
   or a `gh-pages` branch would take that churn off the main index. It touches the GitHub
   Pages workflow and invariant 2 in AGENTS.md ("Never edit `docs/`"), so it is only worth
   doing if lock failures continue after the serial discipline settles.

4. **Close `git gui` while an agent is running.** It appears in shell history (`git gui &`)
   and rescans on a timer, competing for the same lock. Nothing was running during this
   investigation, so this is precautionary.

## Reproducing the measurements

```sh
lsof -a -d cwd "$PWD"                      # sessions live in this working tree
git --no-optional-locks status --short     # does not touch .git/index.lock
git ls-files docs | wc -l                  # tracked generated output
git log --oneline --shortstat -6           # commit breadth
```
