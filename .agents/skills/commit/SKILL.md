---
name: commit
description: Commit the current working tree for Curt on the current branch, with a specific message and no branch, push or authorship claim.
argument-hint: "[what to include, if not everything]"
triggers: ["user"]
---

# Commit for Curt

Curt often has one agent (usually Devin) commit work that Codex, Claude or Cursor wrote.
Your job is to record the working tree accurately, not to change it and not to claim its
authorship.

## Rules

- Commit on the current branch (normally `main`). **Never create a branch.**
- **Never push** unless Curt asks in this session. A push to `main` deploys the site.
- Never amend, rebase, reset or force anything, and never delete `.git/index.lock`. If a lock
  blocks you, follow "Git coordination and incident record" in `README.md` and tell Curt.
- Read-only git calls carry `--no-optional-locks`; diffs also carry
  `-c diff.autoRefreshIndex=false` (see `AGENTS.md`, "Start here").
- Do not edit files to make a check pass. Report failures and ask.
- **Do not add `Co-Authored-By` for an agent that did not write the change**, including
  yourself when you only committed. Commit metadata is not authorship evidence here;
  transcripts are.

## Procedure

1. `git --no-optional-locks status --short` and
   `git --no-optional-locks -c diff.autoRefreshIndex=false diff --stat`. If `$ARGUMENTS`
   names a scope, commit only that. Otherwise commit all tracked changes and new files that
   belong to the project.
2. **Stop and ask** about: untracked tool scratch (`.playwright-mcp/`, `tmp/`, `.DS_Store`),
   anything that looks like a credential, large binaries outside `assets/`, and edits to files
   the three-stream baseline freezes (`python3 scripts/working_edition.py check --draft`
   names them). Also ask if the tree still looks mid-edit, e.g. a check reports stale
   generated output right after another session's change.
3. Run the checks that match what changed:

   | Changed | Run |
   | --- | --- |
   | `editions/three-stream/**`, `scripts/working_edition*.py`, `scripts/edition_detail.py` | `python3 scripts/working_edition.py check --draft` |
   | `scripts/production_history.py`, `scripts/personal_records.py` | `python3 -m unittest discover -s scripts -p test_production_history.py` |
   | `content/pages/**`, panel structure | `python3 scripts/crossref.py check --strict`, `python3 scripts/pagination.py check`, `python3 scripts/panels.py check` |
   | `content/novella/**` | `python3 scripts/novella.py check --strict` |
   | `content/appendix/**` | `python3 scripts/appendix.py check` |
   | any page reference in `content/` | `python3 scripts/pagelinks.py check` |

   The full CI sequence in `AGENTS.md` rebuilds `docs/`; run it only when Curt asks.
4. `git --no-optional-locks -c diff.autoRefreshIndex=false diff --check` for whitespace errors.
5. Stage explicitly by path (`git add -- <paths>`), then commit. Message:
   - **Subject** says specifically what changed: sequence or scene IDs, panel keys, tool
     names, proposal file names. Not "Update project content", "Expand story content" or
     "Update supporting data".
   - **Body**: one bullet per area changed, then the checks run and their results, then
     `Committed-by: <your product>` (e.g. `Committed-by: Devin`). If Curt told you which
     agent wrote the work, add `Authored-by: <agent>`; otherwise say nothing about authorship.
6. Report the commit SHA, files committed, checks and results, and anything left uncommitted.
