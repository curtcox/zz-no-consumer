# Three-stream restructure: current state

**Rewrite this file; do not append to it.** It says only what is open now, what blocks it,
and what comes next, each with its evidence or owner decision. Dated work notes go in
[`log/`](log/), one file per UTC day (`log/YYYY-MM-DD.md`), appended in order and never
rewritten; the 13 September file is the former `research-handoff.md`, moved verbatim.

Last rewritten 15 September 2026 (UTC). Counts below are measurements on that date; rerun
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
- The page 082 operational-detail example is corrected by a dated note,
  [`research/quotation-example-correction-2026-09-15.md`](../../research/quotation-example-correction-2026-09-15.md),
  not by editing the frozen note or pages. The quotations removed from 079, 081 and 082 are decided at
  gate 9 in the working edition (Curt, 15 September).
- Lean toward transparency (15 September): quote sources' exact words as far as fair use allows when it
  helps a reader trace them. Use a 256t pointer when an agent cannot write the words out, and name a
  hazard before paraphrasing. Recorded in `AGENTS.md`; the contract and gate 9 wording is
  [proposed](../../proposals/2026-09-15-quotation-default-at-gate-9.md).
- Adopted proposals: [orientation docs unfrozen](../../proposals/2026-09-13-unfreeze-orientation-docs.md),
  [ordering constraints](../../proposals/2026-09-13-relative-ordering-constraints.md),
  [this status/log split](../../proposals/2026-09-13-split-research-handoff.md).

## Open

1. **Curt's Twitter entrance.** No source post identified, and none may be invented. Curt is
   `@curt_cox` and offered his exports; `scripts/personal_records.py inventory` is ready for
   YouTube watch history, X posts and likes, ChatGPT and claude.ai exports and podcast OPML.
   Requested: YouTube watch history and X `tweets.js` for 16 July–1 September, ChatGPT and
   claude.ai exports, and a dated written recollection of why the book began on 1 September.
   Unexamined lead: the other-Mac `early-mentions.json` index lists a Codex user-role record on
   3 August, 14:31 UTC, in another project, matching the token `HuggingFace`. Its body is not in
   the bundle, and the token also names a software library; nothing about Curt's awareness
   follows from the index row.
2. **The 1–2 September setup gap.** The other-Mac bundle's Codex records cover only 2 September,
   12:26–13:18 UTC. Session `01a06215` there drafted prologue pages 001–015 (now in the Codex
   row). The planning files those pages follow — `content/story-outline.md`, `premise.md`,
   `themes.md`, `continuity.md`, `visual-bible.md` — first entered in commit `c15b1e6e2`,
   2 September 02:13 UTC, and match no transcript on either Mac. The outline already holds the
   creator interlude, both maxims and the nine-panel convergence grid, so their author is
   unestablished. Curt's ChatGPT export (item 1) is the remaining place to look.
3. **Collaboration rows that do not show the row actor's act.** `working_edition.py audit`:
   10 clocks with more than three beats (103 Claude beats at `2026-09-06T15:02:31.590Z`,
   68 Codex beats at `2026-09-02T03:45:45.444Z`), 16 scenes describing narrator analysis, and
   63 beats whose old wording was typed by a different actor than the row. Each needs the
   working rule applied: re-anchor to the act that made the point, or move out of the rows.
   Re-anchored so far from the 15:02:31 cluster: legacy 006–007, 013–016, 031–036, 038–040,
   052, 073-04's vocabulary and 063-04's window, plus the 12–13 September caption expansions
   (log, 14 September); branch scope 067 and 070, interpretation 073–077 and analysis limits
   078–082 (log, 15 September). Eight traps found there. `attribution.json` keeps the earliest
   record containing a line, which can be a patch the session then reports as not applied. A line can predate every transcript,
   so the typing session only carried it forward. A script can supply a caption without its
   `> ` marker; the matcher now pairs both forms (the 12–13 September captions once reported as
   unattributed are Codex's, placed in `collaboration-caption-expansion.json`). A moved line can
   change case, so the index credits the mover (040-03's caption began as Codex's ChatGPT line).
   And a substring `.replace()` inside a line is invisible to whole-line matching: search the
   transcripts for the new wording before calling a line unattributed (040-03's frame, 039's
   page note). A search a session ran can stop short of the line that matters: Claude's
   5 September METR search kept 60 lines, and METR's p. 14 admin-access line comes at 75. Read
   the stored output, not the command. A case-sensitive search misses capitalised lettering:
   Codex's 2 September anthropomorphism audit never matched page 073's DIE. And a document
   describing a change is not the change's reason: read the act that removed the text. Page
   082's audit row came from a rights pass, but on 12 September it was read as a security judgment.
4. **Old-panel review.** All 606 old panels have element-level decisions (1717 elements).
   Three have no draft beat; their omission reasons are checked (log, 14 September): 105-05 and
   117-05 are staging with no claim. 009-02's caption comes from the unattributed outline
   (item 2), so it stays out of the rows under working-rule case 4. The new 27 July Hugging
   Face hardening beats overlap `prod-aftermath-platform-*` in the 15:02:31 cluster; resolve
   that when the cluster is re-anchored.
5. **Authored theses omitted from incident rows.** Legacy 047-02 and 047-05 captions were
   typed in Codex session `01a06270` on 2 September. Under working-rule case 2 they can enter
   only as that writing act in the Codex row. They are omitted with that reason until the
   re-anchoring pass places or drops them (log, 14 September).
6. **27 July placement.** Hugging Face's technical timeline and JFrog's fix post are in the
   incident row on the assumption that the transition falls after 27 July. If Curt's entrance
   settles earlier, they move to a dated encounter in the collaboration rows.
7. **Chronology within July.** Day-only incident beats still outnumber what the timed record
   can order. Three `after` constraints now exist, all on undated counterexamples (legacy
   047/061/062), and `working_edition.py order` narrows three beats. The peer-approval,
   refusal, restraint and email examples are undated in every vault source, so they are bounded
   to the studied 9–13 July board activity and may not be placed within it on thematic grounds.
   Two METR aggregate findings (`hf-ethics-findings`, `hf-ethics-override`) sit over that
   period like the earlier aggregate scenes. Decide at allocation whether they instead enter as
   dated encounters with the report. One beat runs backwards within its scene:
   `june-persistent-users-different-lifetimes`.
8. **Allocation, preview and handoff.** No page windows exist for the detailed manuscript;
   the compressed chronology study stays withdrawn. Then representative thumbnails, full
   read-through, print-size checks and the resynchronization handoff (plan steps 4–8).

## Next

- Continue re-anchoring the 103-beat Claude cluster by the same method: line origins from
  `attribution.json`, then the applied record, then any earlier file that already held the
  line; check quoted critics and transcripts against their vault copies. Remaining sequences,
  in legacy order: assurance 098, accountability 099–102, defense 101,
  aftermath 103–105, wiki overlap and hypotheses 109–111, downstream use 112–118.
- Apply the same method to the 68-beat Codex cluster and to the 047-02/047-05 theses.
- Add ordering constraints for the July day-only beats as sources support them.
- Fold in Curt's exports when they arrive.

## Checks

```sh
python3 scripts/working_edition.py check --draft
python3 scripts/working_edition.py audit
python3 -m unittest discover -s scripts -p test_production_history.py
```

Passing checks never mean the book is complete.
