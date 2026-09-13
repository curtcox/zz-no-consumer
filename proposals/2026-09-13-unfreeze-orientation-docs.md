---
title: Let orientation documents change during the three-stream restructure
status: open
proposed: 2026-09-13
proposed_by: Claude (claude-opus-5)
decision_needed_from: Curt
blocking: true
affects:
  - scripts/working_edition.py
  - AGENTS.md
  - CLAUDE.md
  - README.md
decided:
decided_by:
---

# Let orientation documents change during the three-stream restructure

## Decision requested

Exclude `AGENTS.md`, `CLAUDE.md` and the root `README.md` from the working edition's
frozen-file check, then apply the orientation edits that are waiting on them.

## Why

`working_edition.py snapshot` froze every tracked file outside `scripts/`, `tasks/`,
`.github/` and `editions/` at baseline `332b5ed63262`, and `check --draft` fails if any of
them changes. That set includes the three orientation documents every agent reads first.
None of them feeds the site: `build-site.py` reads `CREDITS.md`, `content/`, `prompts/`,
`research/` and `design/`, not these files.

Edits now waiting:

- `AGENTS.md` lists the CI sequence as a copy-paste block; CI now also runs
  `python -m unittest discover -s scripts -p test_production_history.py`, and the block
  cannot say so. Its "Two modules currently have `unittest` tests" is now three.
- No orientation document can point agents at `proposals/`, at
  `scripts/production_history.py`, or at the rule that commit metadata does not identify
  the authoring agent. Cursor and Devin get these through `.cursor/rules/`; Codex and
  Claude read only `AGENTS.md` and `CLAUDE.md`.

An attempted `AGENTS.md` edit on 13 September was reverted because it broke the check.

## Proposal

1. In `scripts/working_edition.py`, skip a named set of orientation files in
   `frozen_errors`, with a comment saying why. `baseline.json` stays immutable and still
   records their original hashes.
2. Add a fixture to `working_edition_checks.py` showing an orientation edit passes and a
   content edit still fails.
3. Update `AGENTS.md`: the CI block, the test count, a short "Proposals" paragraph, and a
   pointer to `production_history.py` in "Where to read next".

## Alternatives

- **Keep them frozen until promotion.** Orientation drifts from CI and tooling for the rest
  of the restructure, and agents keep missing `proposals/`.
- **Re-snapshot the baseline.** Rejected: the baseline is deliberately immutable and
  identifies the old edition.
- **Put orientation in nested `AGENTS.md` files instead.** Only helps agents already
  working in those directories.

## Risks

A broader exclusion could hide real edition drift; the set should stay at exactly these
three files. `CREDITS.md` feeds the site and stays frozen.

## Opinions

## Decision
