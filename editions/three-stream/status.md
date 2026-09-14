# Three-stream restructure: current state

**Rewrite this file; do not append to it.** It says only what is open now, what blocks it,
and what comes next, each with its evidence or owner decision. Dated work notes go in
[`log/`](log/), one file per UTC day (`log/YYYY-MM-DD.md`), appended in order and never
rewritten; the 13 September file is the former `research-handoff.md`, moved verbatim.

Last rewritten 14 September 2026 (UTC). Counts below are measurements on that date; rerun
the named command before relying on one.

## Owner decisions in force

- Movements: incident history first (HuggingFace, GemStuffer, Collusion Wiki), then
  collaborating actors in the fixed order **Curt, Codex, Claude**.
  [Plan](../../tasks/three-stream-restructure.md).
- The collaboration movement runs until the collaborators finish the book; this
  restructuring is itself production history. No fictional coda.
- Commit author, committer and trailers do not identify the authoring agent; transcripts do.
- Analysis enters a collaborator's row only as the dated act that produced it (the plan's
  four-case working rule).
- The page count is not a target, and the scale question is deferred by Curt.
- Adopted proposals: [orientation docs unfrozen](../../proposals/2026-09-13-unfreeze-orientation-docs.md),
  [ordering constraints](../../proposals/2026-09-13-relative-ordering-constraints.md),
  [this status/log split](../../proposals/2026-09-13-split-research-handoff.md).

## Open

1. **Curt's Twitter entrance.** No source post identified, and none may be invented. Curt is
   `@curt_cox` and offered his exports; `scripts/personal_records.py inventory` is ready for
   YouTube watch history, X posts and likes, ChatGPT and claude.ai exports and podcast OPML.
   Requested: YouTube watch history and X `tweets.js` for 16 July–1 September, ChatGPT and
   claude.ai exports, and a dated written recollection of why the book began on 1 September.
2. **Other-Mac production records.** Collected: `256t/editions/other-mac-bundle-20260913T2302Z.tar`
   is extracted, and the current `256t/editions/attribution.json` indexes its 24 records from
   three Codex sessions on 2 September, 12:26–13:18 UTC. One of them (`01a06215`) supplied
   lines in legacy 084–085 and 088–090. Not yet re-examined: whether these records close the
   1–2 September setup and incident-dossier gap, whose first commit carries a −0700 offset.
3. **Collaboration rows that do not show the row actor's act.** `working_edition.py audit`:
   10 clocks with more than three beats (203 Claude beats at `2026-09-06T15:02:31.590Z`,
   68 Codex beats at `2026-09-02T03:45:45.444Z`), 25 scenes describing narrator analysis, and
   134 beats whose old wording was typed by a different actor than the row. Each needs the
   working rule applied: re-anchor to the act that made the point, or move out of the rows.
4. **Old-panel review.** 591 of 606 old panels have element-level decisions; pending are
   047, 061 and 062. Four have no draft beat: 009-02, 061-02, 105-05, 117-05. Source:
   `manuscript-coverage.json`. Legacy 083–091 were reviewed under the working rule, at their
   origin sessions' records, not on the 15:02:31 cluster (log, 14 September).
   The new 27 July Hugging Face hardening beats overlap `prod-aftermath-platform-*` in that
   cluster; resolve the overlap when the cluster is re-anchored.
5. **Unresolved clocks** in legacy 047, 061 and 062 (last recorded next step in the log).
6. **27 July placement.** Hugging Face's technical timeline and JFrog's fix post are in the
   incident row on the assumption that the transition falls after 27 July. If Curt's entrance
   settles earlier, they move to a dated encounter in the collaboration rows.
7. **Chronology within July.** 8–12 July held 117 incident beats with day-only bounds beside
   96 timed beats. Record source-supported order with `after` / `before` constraints and read
   narrowed intervals with `working_edition.py order`. One beat runs backwards within its
   scene: `june-persistent-users-different-lifetimes`.
8. **Allocation, preview and handoff.** No page windows exist for the detailed manuscript;
   the compressed chronology study stays withdrawn. Then representative thumbnails, full
   read-through, print-size checks and the resynchronization handoff (plan steps 4–8).

## Next

- Finish review of 047, 061 and 062 and their unresolved clocks.
- Apply the collaboration working rule to the audit findings, starting with the 203-beat
  Claude cluster, using `production_history.py panel` for origin sessions.
- Add ordering constraints for the July day-only beats as sources support them.
- Check the other-Mac records against the 1–2 September gap; fold in Curt's exports when they arrive.

## Checks

```sh
python3 scripts/working_edition.py check --draft
python3 scripts/working_edition.py audit
python3 -m unittest discover -s scripts -p test_production_history.py
```

Passing checks never mean the book is complete.
