---
title: Record source-supported event order without inventing clock times
status: done
proposed: 2026-09-13
proposed_by: Claude (claude-opus-5)
decision_needed_from: Curt
blocking: false
affects:
  - editions/three-stream/manuscript/*.json
  - scripts/edition_detail.py
  - tasks/three-stream-restructure.md
decided: 2026-09-13
decided_by: Curt
---

# Record source-supported event order without inventing clock times

## Decision requested

Allow a manuscript beat to name beats it must follow or precede (`after` / `before`), each
with a source locator, and validate that ordering in the draft check.

## Why

The plan requires every depicted event to fall within its page's printed interval, and
beats carry only absolute bounds. On 13 September, 8–12 July held 117 incident beats with
day-only bounds beside 96 with clock times. Any page holding a day-only beat must span
that whole day, so the densest part of the book either collapses onto a few day-wide pages
or cannot be ordered at all. Sources such as METR's report often narrate order ("before",
"after", "then") without clocks; that order is evidence the ledger currently cannot record.

This is separate from the page-count question Curt deferred: it concerns what can be known
about order, not how many pages result.

## Proposal

1. Optional beat fields `after` and `before`: lists of `{beat, source, locator}`.
2. `manuscript_errors` rejects unknown beat IDs, cycles, and constraints that contradict
   absolute bounds (an `after` target whose earliest start is later than this beat's latest
   end).
3. The later allocator narrows each beat's feasible interval by propagating constraints,
   and prints the narrowed interval with the constraint chain that produced it. Pages still
   print only bounds the evidence supports.
4. Add a sentence to the plan's timestamp rules: a source-supported order is evidence; an
   order chosen for layout is not.

## Alternatives

- **Leave bounds absolute** and accept day-wide pages in July.
- **Split day-only beats into guessed sub-day intervals.** Rejected: invented precision.
- **Encode order only in array position within a scene.** Already implicit, but it cannot
  cross scenes or rows, and it is unchecked (the audit found a backwards beat in
  `june-persistent-users`).

## Risks

Constraints written from a misreading would propagate silently; each needs its own locator
so review can check it. More fields for the authoring agent to maintain.

## Opinions

## Decision

Approved by Curt on 13 September 2026, in chat: "Adopt all 3 proposals." Recorded by
Claude (claude-opus-5), which then carried it out:

- `scripts/edition_detail.py`: optional `after` / `before` beat fields (`beat`, `source`,
  `locator`); `manuscript_errors` requires an admitted source and locator and rejects unknown
  targets, cycles and contradictions with absolute bounds; `ordering()` propagates feasible
  starts; the generated scene review prints constraints when present.
- Order fields are excluded from `beat_digest`, so adding a constraint does not invalidate an
  element-level review (a consequence found while implementing; it keeps the proposal's
  intent without forcing re-review).
- `scripts/working_edition.py order [beat…]`: narrowed intervals with their constraint
  chains. The allocator does not exist yet; it should consume `ordering()`.
- Fixtures in `scripts/working_edition_checks.py`; plan sentence added to the timestamp rules.
- No constraints have been authored yet; that is manuscript work.
