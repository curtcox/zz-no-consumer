---
title: Split the three-stream research handoff into current state and a dated log
status: done
proposed: 2026-09-13
proposed_by: Claude (claude-opus-5)
decision_needed_from: Curt
blocking: false
affects:
  - editions/three-stream/research-handoff.md
  - editions/three-stream/validation.json
decided: 2026-09-13
decided_by: Curt
---

# Split the three-stream research handoff into current state and a dated log

## Decision requested

Replace the single append-only `research-handoff.md` with a short current-state file and a
separate dated work log, and stop recording `/tmp` log paths in `validation.json`.
Codex has written most of this file and should give an opinion before anyone changes it.

## Why

On 13 September `editions/three-stream/research-handoff.md` was 1,154 lines of appended
session entries. Nearly every entry ends by restating that the Twitter entrance, other-Mac
history, semantic review and page allocation remain open, so the current state is spread
across the whole file and a newcomer has to read all of it to learn what is actually open.
`validation.json` points at `/tmp/three-stream-check-*.log`, which do not survive a reboot
and are not in the repository.

## Proposal

1. `editions/three-stream/status.md`: open questions, blockers and next steps only,
   rewritten rather than appended, each item naming its evidence or owner decision.
2. `editions/three-stream/log/YYYY-MM-DD.md`: the dated entries moved verbatim from the
   current file, one file per day, so history is preserved unchanged.
3. `validation.json` keeps commands and exit codes; logs, if kept, go under the ignored
   `256t/editions/validation/`.
4. The edition README links `status.md` where it now links the handoff.

## Alternatives

- **Leave it as is.** Costs every new session the full read.
- **Trim the old entries.** Rejected: they are production history for the collaboration
  movement and must not be rewritten.

## Risks

A moved entry could be mistaken for an edit; move text verbatim in one commit with no
other changes, so `git log --follow` and the diff show a pure move.

## Opinions

## Decision

Approved by Curt on 13 September 2026, in chat: "Adopt all 3 proposals." Recorded by
Claude (claude-opus-5), which then carried it out:

- Commit `8ac9cd9ba`: `research-handoff.md` moved verbatim to `log/2026-09-13.md` with no
  other change. Every entry was written on 13 September UTC, so one day file holds it all.
- New `editions/three-stream/status.md`, rewritten rather than appended, with owner
  decisions in force, open items with evidence, next steps and checks.
- Edition README and `.cursor/rules/three-stream-edition.mdc` point to `status.md` and the
  log convention; `validation.json` keeps commands and exit codes only;
  `production_history.py` indexes `status.md` and `log/`.
- Codex did not give an opinion before adoption; Curt's approval did not require one.
