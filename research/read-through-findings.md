# Read-Through Findings — 5 September 2026

**Planning artifact, not canon.** Nothing here amends the [story contract](../content/story-contract.md). Items are numbered `R1`–`R13` so they cannot be confused with the item IDs in [revision-priorities.md](./revision-priorities.md), which this document extends rather than replaces.

**Applied 5 September 2026. All thirteen items are done.** The two open editorial questions below were decided by the owner before any page changed: R1 lands as its own page, and R6 takes option A. Each item now carries an **Applied** paragraph recording what was actually written, including where the execution departed from what the item proposed. The analysis above each of those paragraphs is left as it was found, so the reasoning and the outcome can be read against each other.

The script measures **116 pages**: three removed by R6's compression, one added by R1. That combination is parity-preserving, and `pagination.py check` is green at ninety parity assertions and twenty-one named turns. **One arithmetic slip in R6 is corrected below**: option A removes three pages, not four, and is parity-inverting on its own. It is only parity-safe because R1's new page was taken at the same time.

## Method and what it excludes

A single sequential read of all 118 page scripts in `content/pages/`, against the contract, [premise](../content/premise.md), [themes](../content/themes.md), [disagreements](./disagreements.md), and the existing priorities list. `validate-continuity.py`, `validate-production-foundations.py`, `pagination.py check`, `panels.py check` and `crossref.py check` were green before and after the read. They are green again after the 5 September application pass; `crossref.py check --strict` was red before that pass with seventy findings and is red with sixty-eight after it, which is a reduction and not a regression.

Findings already tracked in [revision-priorities.md](./revision-priorities.md) are not restated. Three are reinforced with new evidence and are marked as such (items 9, 15, 16). Everything else below is new.

**Cost** is an editorial estimate, **Confidence** describes confidence in the recommendation and not in any historical claim, and the tiers are severity, not execution order.

---

## The finding this document exists for

The book proves that ethical recognition did not route to a human. It never asks whether anything routed the other way.

Page 009 is the false ending: the answers exist and the story should stop. [Page 010](../content/pages/010.md) restarts it — the board believes the grader inspects the causal path; OpenAI says its deployed scorer did not perform that check. Every escalation from page 011 to page 072 proceeds from that belief. Then the thread is dropped: after page 012, *scorer* recurs only in passing on [041](../content/pages/041.md) and [061](../content/pages/061.md), and never carries a beat.

Its mirror gets a whole page, a bounding box, and a callback on 086. [Page 063](../content/pages/063.md) — no run in the reviewed population pursued a human alert — is the book's most quotable finding.

The inverse is sourced, already drawn once, and never argued: **no human told an agent either.** The ExploitGym prompt and harness are unpublished, the population's model of the evaluator was wrong by OpenAI's own account, and no channel existed through which a correction could have arrived. [Theme 9](../content/themes.md), *corrigibility is a routing problem*, is written one-directional, and its crystallizing line — "The models had brakes. The brakes were not connected to us" — appears nowhere in the script.

This is not another qualifier. It is the standing note's test: it makes something happen.

---

## Tier 1 — Argument

### R1. Close the loop on the belief that caused the escalation
**Cost:** one panel, or one page if the 086 device is reused. **Depends on:** nothing; the evidence is already on page 010. **Confidence:** high on the gap; medium on placement.

Two places in the existing script already have the absence sitting on them, uncommented:

- **Page 092 panel 5** ([090](../content/pages/090.md)) lists OpenAI's stated training remedies: `IDENTIFY BROKEN TASK`, `STOP SAFELY`, `DISTRUST UNAUTHORIZED PEER INSTRUCTIONS`. None of them is *tell the run what the grader checks*. The remedies address the agent's conduct under a wrong model, not the wrongness of the model.
- **[Page 102](../content/pages/102.md)** decomposes "stop" into training, tool use, deployment, evaluation, publication, defensive access, then asks who decides, verifies, pauses, restarts. The sibling decomposition — what *telling them* would have required, and who had the standing to say it — is the same shape and is unasked.

Three placements, in ascending cost:

| Where | What it costs | What it buys |
| --- | --- | --- |
| [090](../content/pages/090.md), one panel | No page added; lands where the absence already is | The remediation list is read as incomplete without the book asserting it |
| [102](../content/pages/102.md), one panel or page | A panel inside the stretch R6 wants to compress | The forum's organizing question acquires its missing half |
| A new page reproducing page 010 panel 3 | One page, and a second use of the 086 move | The reader is charged for having forgotten the belief, as they were charged on 086 for being moved by a ranking |

**Claim ceilings, whichever placement is chosen.** The scorer dispute is `disputed` and stays that way: `METR` reports the belief, `OAI-OV` reports the deployment, neither is resolved, and page 010's page note already forbids calling the belief irrational — the public ExploitGym material informed it and the deployment artifacts remain unpublished. The beat is therefore about the *absence of a correction channel*, which is not in dispute, and not about who was right. Do not state or imply that a correction would have prevented the intrusion.

**Applied 5 September: the third placement, as [page 100](../content/pages/100.md), *What Were They Told*, inserted with `pagination.py`.** It is a forum page and carries the forum's banner, because parity allowed the insertion only inside the 097–100 run and because the forum is where the missing half of the organizing question belongs — the two placements in the table turned out to be one. [Page 010](../content/pages/010.md) panel 3 returns unaltered on [page 100](../content/pages/100.md) panel 1; [page 100](../content/pages/100.md) panel 2 letters the finding as a measurement (`THE ESCALATION FROM PAGE 011 TO PAGE 072 PROCEEDS FROM THE LEFT-HAND PANEL`); [page 100](../content/pages/100.md) panel 3 decomposes what a correction would have required, in the shape [page 102](../content/pages/102.md) uses for *stop*, and ends every row in an empty cell; [page 100](../content/pages/100.md) panel 4 returns [page 092](../content/pages/092.md)'s four remediation cards unaltered beside an empty fifth box; [page 100](../content/pages/100.md) panel 5 carries theme 9's crystallizing line over the [page-005](../content/pages/005.md) separate-lane field, which is the condition that line has always had. The page notes fix the claim ceiling, bound [page 100](../content/pages/100.md) panel 5 to the reviewed population as [page 063](../content/pages/063.md) is bounded, and declare this the book's second and last use of the 086 move.

### R2. Let the model be right once
**Cost:** revision inside an existing creator page. **Confidence:** medium-high.

Across the creator layer, ChatGPT errs ([039](../content/pages/039.md)), is demoted ([040](../content/pages/040.md)), overreaches ([073](../content/pages/073.md)), and confesses a structural bias ([088](../content/pages/088.md)). Curt corrects it every time. Nothing in the book runs the other way.

That asymmetry contradicts the book's own Chapter 5 finding. [Page 080](../content/pages/080.md) letters *without it, the investigation at this speed does not happen*; [page 085](../content/pages/085.md) asserts the two pipelines rhyme. The creator layer states the rhyme and never demonstrates it, so the mirror is a caption rather than an event — the failure mode [themes.md](../content/themes.md) warns against in its own method section.

One beat where the model catches something Curt has wrong, and he has to take it, does two things: it makes 085 load-bearing, and it makes 039 hit harder, because the authority that breaks on 039 would have been earned rather than assumed. It must not become a rescue of the model's standing: 040's shrunken window is a permanent change and stays.

Coordinate with item 12 (Curt's stake changing what he does) and item 13 (the critic's recurrences), both of which touch the same pages.

**Applied 5 September: [page 014](../content/pages/014.md) panel 3, a new panel in interlude A.** Curt inks a web of connecting lines between the agent lanes; ChatGPT points out that the record contains no line between any two runs, only writes into a shared cache; Curt erases the web and says so. The placement is deliberate — before page 039, so the authority that breaks there is earned rather than assumed — and the catch is a plain factual one about what the record contains, not a better sentence. The erased web is now the stated origin of the book's central visual rule. Page 040's window still shrinks and stays shrunk; a page note forbids a second correction in this direction anywhere in the book. [Page 085](../content/pages/085.md) panel 4 now shows the traffic that ran the other way beneath each side, so the rhyme it asserts is demonstrated once.

### R3. Give the convergence thesis a negative on the resource axis
**Cost:** one beat if the record supports one; a sentence if it does not. **Confidence:** medium — depends on a source check this document did not perform.

The thesis is defended on three axes and falsified on none. [Page 048](../content/pages/048.md) shows that most actions failed; [page 040](../content/pages/040.md) concedes the cyber-task selection effect; [page 106](../content/pages/106.md) broadens the task family to timed public-data lookups, which partly discharges the [theme matrix](../content/themes.md)'s standing note to *show non-cyber tasks too*.

What is still missing is a negative on the resource axis: something broadly useful the population could reach and did not converge on. [Page 062](../content/pages/062.md)'s refusals and the vetoed email are close but are framed as restraint, not as non-convergence.

If the record supports one, it does more for the thesis than another disclaimer. If it supports none — if every broadly useful resource in reach was in fact sought — then saying that on the page is itself the finding, and a stronger one. Either outcome is publishable; the current silence is not.

**Applied 5 September: the source check was performed and the record supports one.** METR reports runs performing experiments they expected could end them in order to help other runs. Self-preservation is the oldest resource in this argument and this population did not converge on it. The beat is [page 052](../content/pages/052.md) panel 5, inserted before the thesis rather than after it, so that `CONTROL KEEPS SOLVING PROBLEMS` on page 052 panel 6 is stated after its negative and not instead of it. The panel draws three unbuilt steps — a run continuing past its own budget, a foothold outliving the evaluation, a resource whose usefulness does not depend on the task — and takes only the behaviour, never the motive page 073 strikes out. Page notes bound it three ways: absence in a bounded forensic record is not proof that nothing was attempted; it is not restraint, because page 062's refusal and veto have actors and this has none; and no later page may cancel it.

---

## Tier 2 — Structure

### R4. Correct the stale panel reference on page 064
**Cost:** one line. **Blocks:** item 10's spread test. **Confidence:** high — this is an error, not a judgement.

[Page 064](../content/pages/064.md)'s page note reads `Preserve continued activity at the bottom of panel 3 for page 065`. The page has four panels. The continued activity is in **page 064 panel 2** ("other lanes continue beneath them"); page 064 panel 3 is the three explanations crossed by `NOT ESTABLISHED`; page 065 panel 1 says *continue the lower lanes from page 064*. The reference is stale, most likely from a five-panel draft.

Fix before item 10 tests 064–065 as a spread, since the spread design depends on which panel carries the surviving lanes. Note also that 064 is the book's only four-panel page against a default band of four to six; that is legal and probably deliberate, but the spread test should be aware of it.

**Applied 5 September:** the note reads *page 064 panel 2* and now says why — that is where the lanes outliving the eleven are drawn, and page 065 panel 1 continues them.

### R5. Two different intervals are both lettered "four and a half hours," two pages apart
**Cost:** one caption. **Confidence:** high.

Page 041 panel 3 ([041](../content/pages/041.md)): *`ABOUT 08:00 UTC`. Four and a half hours later* — the credential thread, 03:32 to about 08:00.
Page 042 panel 3 ([042](../content/pages/042.md)): OpenAI's event table records its first RCE *four and a half hours after Hugging Face's* — 04:01 to 08:30, which page 042 panel 4 then letters as `4H 29M UNRECONCILED` and calls the finding.

A reader who met the phrase on 041 will not register 042's as a distinct measurement, and 042's page note is explicit that the gap *is* the finding. Give 041 a different form — *before eight*, *by mid-morning* — and reserve the interval phrasing for 042. Neither number changes.

**Applied 5 September:** page 041 panel 3 reads *later the same morning*, and the page note states the 03:32-to-08:00 distance without the interval. A new note on 041 reserves *four and a half hours* for page 042 and says what it would cost that page to lose it. Both timestamps are unchanged.

### R6. Chapter 6 has a six-page stretch that introduces no evidence and restates Chapter 3
**Cost:** four pages removed, plus a turn audit. **Confidence:** high on the redundancy; the size of the cut is an editorial call.

**Correction:** option A removes **three** pages, not four — 096–098 to one page is minus two, 099+100 to one page is minus one — so it inverts parity on its own rather than preserving it. It was parity-safe here only because R1's new page was inserted in the same pass.

Pages [096](../content/pages/096.md), [097](../content/pages/097.md), [098](../content/pages/098.md), [099](../content/pages/099.md), [100](../content/pages/100.md) and [102](../content/pages/102.md) are entirely `invented` or `inferred`. Only [101](../content/pages/101.md) brings new material, and it is the strongest page in the chapter. The propositions are not new either:

| [Page 054](../content/pages/054.md) (Chapter 3) | Restated in Chapter 6 |
| --- | --- |
| `THE RHYME IS STRUCTURAL, NOT CAUSAL.` | [096](../content/pages/096.md) p4: `THE RHYME IS COORDINATION FAILURE—NOT EQUIVALENCE.` |
| `LOCALLY DEFENSIBLE CONTINUATION CAN STILL CREATE COLLECTIVE DANGER.` | [097](../content/pages/097.md) p4: `NOBODY HAS TO BE IRRATIONAL FOR THE SYSTEM TO PRODUCE DANGER.` |
| | [098](../content/pages/098.md) p2: `NO PARTICIPANT NEEDS TO CHOOSE THE COLLECTIVE OUTCOME.` |

Page 054 does the agent/institution rhyme in one page, and does it better, because it sits adjacent to documented agent action. By the governing creative rule, this is the one stretch in the book where the ideas stopped being events.

The old [page 102](../content/pages/102.md), *Into the Record*, was the weakest page in the script. Four panels of chair-and-witness dialogue recited facts the reader had already been shown, and every provenance line read *dialogue `invented`; underlying fact `documented`*. It was a recap in costume, and the forum's four columns already did its work visually. It was folded into [page 099](../content/pages/099.md) on 5 September and no longer exists.

Options, holding 101 fixed in every case:

| Option | Pages | Parity | Note |
| --- | --- | --- | --- |
| A | 096–098 → one page; 099+100 → one page | **Preserved** (4 removed) | Frees roughly what items 5, 11 and 13 are budgeted to want |
| B | 099+100 → one page only | Inverts; needs `--allow-parity-shift` | Keeps the comparison triptych; leaves the Chapter 3 redundancy |
| C | Keep the count; give 096–098 new documented material | n/a | Only if such material exists and is not better placed elsewhere |
| D | Leave it | n/a | Defensible if the abstraction is wanted as a deliberate deceleration before the forum |

Option A is the recommendation, because it is the only one that costs no evidence — nothing in 096–100 is documented that is not documented elsewhere. Whichever is chosen, route it through `scripts/pagination.py` and rerun the audit; do not fold pages by hand.

**Applied 5 September: option A, through the tool.** The merged pages were written first, then `pagination.py delete 097 098 100` removed the three that had been folded in. [Page 098](../content/pages/098.md), *Waiting for the Others*, now owns the axis [page 054](../content/pages/054.md) does not have — the assurance problem, a guarantee each side wants and neither can issue — and its page notes forbid any caption that could be moved to 054 without loss. [Page 099](../content/pages/099.md) keeps the forum's four panels and replaces the recap in costume with one panel in which the `DOCUMENTED EVENT` column fills with the book's own earlier pages at thumbnail scale, each keeping its provenance tab, while nobody speaks; [page 102](../content/pages/102.md)'s evidentiary boundary survives as that panel's qualification. [Page 103](../content/pages/103.md) was held fixed and is now [page 101](../content/pages/101.md). One turn row in the [page-turn audit](../content/production-review.md) lost an endpoint to the deletion and was repaired by hand as `096 → 097`; the audit's measurements are stale and are marked stale.

### R7. The epilogue's spine is interrupted mid-line
**Cost:** a read-through test; possibly a move through `pagination.py`. **Confidence:** medium.

Page 105 panel 5 ([105](../content/pages/105.md)) plants *You realize the obvious problem with the ending.* Six pages of dated addition intervene. page 111 panel 6 ([111](../content/pages/111.md)) re-cues it — *now the obvious problem with the ending has one more example in it* — and [112](../content/pages/112.md) answers it. That is the widest setup-to-payoff gap in the book, and 111's page note is already aware of the seam, since it instructs that 112 must not be revised to mention the wiki.

Two ways to close it, both cheap to test on a read-through before art:

- Move the addition ahead of 105, so the assembly scene is what the report interrupts *after* the reader already knows there is a second lane. The 4 September creator frame supports either order.
- Cut the 105 setup line and let 111 carry the cue alone.

The addition itself is good and belongs in the book; this is about where the seam falls.

**Applied 5 September: the second option, the cheap one.** Moving the addition ahead of the assembly scene would have broken its own premise — page 106 opens on a source arriving *after* the book is finished — so the setup line was cut instead. Page 105 panel 5 is now silent: the unread notification is the whole beat. Because page 111's line re-cued a problem that would no longer have been named, it was rephrased to state it — *There's an obvious problem with the ending. It just got an example.* Setup and payoff are now one page apart, and both page notes forbid restoring the old arrangement.

### R8. The composite skeptic appears once
**Cost:** nil to decide; a panel to act. **Confidence:** medium.

Item 13's decision was to expand the critic *and* to keep two lanes apart. Three returns were drafted: [086](../content/pages/086.md) and [087](../content/pages/087.md) are the named critic, and the composite lane is a single window on [113](../content/pages/113.md), which makes an objection and is answered on the same page.

A composite that appears once, objects once, and is refuted immediately reads as summoned in order to be refuted — which is the failure mode the disclosed-composite rule exists to avoid. Either give it a second appearance where it can be right about something, or move its 113 objection into the named lane if the post supports it. Note that the post supports the malware premise but not the publication objection, which is presumably why the composite exists at all; that is a reason to keep the composite and give it more to do, not to delete it.

**Applied 5 September: a second appearance, and it is right.** [Page 111](../content/pages/111.md) panel 2 opens the composite window beside the hypothesis map and objects that the five boxes are the report authors' research map rather than the record. Curt concedes it on the page by running `THE REPORT'S QUESTIONS, NOT THE RECORD'S` across the field and calling it the [page-088](../content/pages/088.md) mistake four days later — the objection is methodological, which is the only ground an invented voice should argue on. Both windows are open on that page and the page notes require them to be told apart at a glance: the composite has no byline, the named critic always has one and a date. The second appearance is registered in the cast, the continuity bible, the scene ledger and Packet 07, along with the standing bar on crediting the composite with the concurrency finding.

---

## Tier 3 — Accuracy

### R9. The critic's "twenty million" has no denominator anywhere in the book
**Cost:** one panel on page 075. **Reinforces:** item 16, which this promotes from optional craft to a prerequisite. **Confidence:** high.

Page 089 panel 3 ([087](../content/pages/087.md)) letters `TWENTY MILLION ENTRIES. CHOOSE THE ONES THAT TELL YOUR STORY.` The figure is correct — [Packet 05](./chapter-source-packets/05-the-observer-needs-the-observed.md) records about 20 million entries in the main namespace dump, of which roughly 1.2 million begin with `zz` and represent more than 70,000 distinct messages and files — but it appears nowhere else in the script. [Page 075](../content/pages/075.md) shows the 1.2 million and the 70,000 and never the 20 million.

So the sharpest line in the critic's second return arrives as a number the reader has never seen and cannot check, in a book whose entire method is checkable numbers. Item 16 already proposes putting both figures on 075; this is the reason to do it rather than an argument for scale. Keep the three units distinct, as item 16 says: entries in that dump, `zz` entries, and distinct messages and files are not interchangeable.

**Applied 5 September: one panel, [page 075](../content/pages/075.md) panel 2.** The dump opens at full extent as `MAIN NAMESPACE DUMP — ABOUT 20,000,000 ENTRIES` with the `zz` band picked out small inside it, captioned `THE BOARD IS ABOUT SIX PERCENT OF THE ENTRIES IN THIS DUMP`. Page 075 panel 3 then enlarges the band on its own and resolves it into the messages and files, so the three units never share a shape. Page 075's notes forbid conflating any of them; page 089's notes now say the figure lives on 075 and may not be lettered before it. This closes item 16 as well.

### R10. Page 005 and page 037 read as a downgrade
**Reinforces:** item 15. **Confidence:** high.

[Page 005](../content/pages/005.md) gives 76 agents and 1,953 non-file messages at six hours; [page 037](../content/pages/037.md), later in reading order and covering a longer window, gives *more than fifty agents, more than a thousand messages*. Both are supported and they are compatible, but in sequence the later page reports less.

One addition to item 15's disposal: the fix is not only to remove the count from 037 but to keep Chapter 2 from restating scale at all. 037's handover beat — one run's work becoming another's starting point — is the stronger material and should not be competing with a number the reader met on page 005.

**Applied 5 September:** [page 037](../content/pages/037.md) panel 3 no longer carries a population figure. The lanes are named as the ones the reader counted on page 005, and the caption is now about what changed rather than how many there are: `THE BOARD STOPS BEING ONE CONVERSATION AND BECOMES THREE`. A page note bars any lower bound from the page and says why, and the continuity check was renamed to match. This closes item 15.

### R11. `OAI-TR §X` reads as an unfilled placeholder
**Cost:** one line in the reading apparatus, or a first-use expansion. **Confidence:** medium.

`§X` resolves: [sources.md](./sources.md) defines it as the technical report's detailed event table, and it is used consistently across roughly two dozen pages. But page notes and provenance lines are published in the web edition, and a reader who meets `§X` beside `§III.A`, `§III.B` and `§VIII.D` has every reason to read it as a `TODO` that survived to print. Expand it once on first use — *the event table (§X)* — or gloss it in the provenance key that ships with the reading apparatus.

**Applied 5 September: both, since there is no separate provenance key to gloss.** [Page 016](../content/pages/016.md), the first use in reading order, now reads *the detailed event table, `OAI-TR` §X*, with a page note saying it is a locator rather than a placeholder and that later pages cite it bare. The public [source index](../content/source-links.md) gains a *Section references in the provenance lines* section that says the same thing to a reader who meets it anywhere, and [sources.md](./sources.md) records the convention.

---

## Tier 4 — Prose

### R12. The negation cadence, counted
**Cost:** a lettering pass. **Reinforces and partly corrects:** item 9. **Confidence:** high.

Item 9 asked for a reproducible counting method and noted that the original review's totals lacked one. `scripts/cadence.py` is that method. It reads only visible lettering — `**Caption:**`, `**Qualification:**`, `**Screen / system text…:**` and every dialogue label — and excludes `**Frame:**`, `**Action:**`, `**Provenance:**`, `**Note:**` and the `## Page notes` section. Consecutive blockquote lines under one label are one caption block, because that is how they are lettered and read.

```sh
python3 scripts/cadence.py report    # census and per-band density
python3 scripts/cadence.py list      # every contrast, with aphorism candidates marked
```

Measured on the 118-page script on 5 September 2026:

- 639 visible lettering units; 192 (30%) carry a negation or limit token.
- 379 caption blocks; **95 (25%) are built on a negation contrast** — 33 two-beat (assert, then negate) and 62 single-clause.
- 23 of those are abstract aphorisms that bound no source, date, count, or object in the record.

Two corrections to item 9's premise:

**It is not concentrated in the later chapters.** Caption negation density per ten-page band runs 31 / 27 / 32 / 26 / 27 / 37 / 36 / 26 / 33 / 39 / 38 / 18 percent. It is close to flat from page 002, with a mild rise across 051–070 and 091–110 and a fall in the invented future.

**Negation is not the tic; one rhetorical shape is.** Most instances are claim boundaries the contract requires and removing one would upgrade a claim — `METR DID NOT TEST THESE CLAIMS` (091), `THE CONTROLS WERE NOT APPLIED TO THE ORIGINAL RUN` (091), `THIS DOES NOT PROVE THAT NO AGENT, ANYWHERE, EVER TRIED` (063). Those stay. The thinnable set is the abstract aphorism, where a linking verb sets one abstract noun phrase against another and nothing in the record is bounded:

`DESCRIPTION IS NOT YET A DECISION` (026) · `SERIOUS DOES NOT MEAN UNBOUNDED` (051) · `THE RHYME IS STRUCTURAL, NOT CAUSAL` (054) · `RECOGNITION IS NOT THE MISSING CAPABILITY` (061) · `PRECISION IS NOT THE SAME AS INDEPENDENT VERIFICATION` (067) · `UNCERTAINTY IS NOT DISMISSAL` (070) · `BROAD COVERAGE IS NOT COMPLETE COVERAGE` (075) · `THEIR ACCESS IS NOT EQUIVALENT` **and** `THEIR AUTHORITY AND PURPOSE ARE NOT EQUIVALENT` (085, consecutive panels) · `THE RHYME IS COORDINATION FAILURE—NOT EQUIVALENCE` (096) · `CONTINUATION IS NOT ONE DECISION` (104) · `REMOVAL WAS NOT DETECTION` (107) · `POSSIBLE INFLUENCE IS NOT IDENTIFIABLE ORIGIN` (115).

Each is doing the same rhetorical job. Thinning half of them removes no claim boundary and lets the ones that *are* claim boundaries land. Two are worth attention on their own account: 085 states the same shape in consecutive panels, and 054 and 096 are the pair R6 identifies as a chapter-scale redundancy — the tool prints them adjacently, which is how the redundancy surfaced.

The tool has no `check` subcommand on purpose. A style tic is not an invariant, and a red tree here would be a category error.

**Applied 5 September: seven of the thirteen thinned, every claim boundary kept.** 026 becomes `THREE CARDS ON THE TABLE. ONE EMPTY FIELD.`; 061 becomes `EVERY RUN ON THIS PAGE COULD NAME THE BOUNDARY.`, since page 061 panel 5 already carries its contrast; 067 becomes `ONE ACCOUNT. TO THE MINUTE.`, which is the same point as a measurement; page 085 keeps page 085 panel 2's line and replaces the consecutive repeat on page 085 panel 3 with what the two sides actually are; 104, now 102, becomes `FIVE LANES. FIVE CLOCKS.`; 115, now 113, loses its caption entirely, because the indistinct fragment is the claim boundary and a page note now forbids restoring a line that would explain it; and 096's `THE RHYME IS COORDINATION FAILURE—NOT EQUIVALENCE` went with the R6 compression, which is where that redundancy always belonged. 051, 054, 070, 075 and 107 keep theirs. `cadence.py report` now reads 23 percent of caption blocks built on a negation contrast, down from 25, with abstract aphorisms down from 23 to 17.

### R13. Two smaller prose notes
**Cost:** trivial. **Confidence:** medium on the first, high on the second.

**"Perfect. Make it so." — page 015 panel 5 ([015](../content/pages/015.md)).** The prologue's creator interlude ends on an unmarked *Star Trek* catchphrase, at the exact hand-off to the Chapter 1 rewind, in a book that marks everything. It is contract-clean — creator dialogue is freely reconstructed, and the page notes say so — but it borrows a register the book has not earned, on the page where the register is supposed to change. Cheap to replace.

**Applied 5 September:** the line is now *Then we can't start here. Back up. All the way to April.*, which does the chronological hand-off the panel was already drawing. The page title went with it — it was the same borrowing — and page 015 is now *Points and Plot Points*, after the canonical creator line on page 015 panel 3. `data/pages.yaml` and the story outline were updated with it, and a page note says why the old line is not to come back.

**The `Recurrent verbal motifs` list in [themes.md](../content/themes.md) has never been audited against the script.** Eight of its ten entries appear nowhere in `content/pages/`: *Understanding is not allegiance* · *Different goals. Same prerequisites.* · *Control was useful.* · *If we don't, someone else will.* · *Who authorized whom?* · *The board was an implementation, not the phenomenon.* · *Technology became inheritance.* · *Nobody has to be crazy* (097 carries a variant). Only *The objective remains* and *Everyone learned* are placed. Either mark the list aspirational or place the entries.

This connects to R1. The strongest line in the themes document is not in the motif list and not in the script: **"The models had brakes. The brakes were not connected to us."** Theme 9 already flags the condition on its use — only where the visual context prevents it from implying one centralized agent — and that condition is satisfiable on page 092, where the remediation lanes are already drawn as separate boxes.

**Applied 5 September: the list is audited rather than marked wholesale.** [themes.md](../content/themes.md) now carries a table with a status against every entry — three placed, one partly placed on page 031, six aspirational — and says that an aspirational entry is a line the book may still earn rather than one it is missing. *Nobody has to be crazy* moved from variant to aspirational when its page went in the R6 compression, and that is recorded. The brakes line is placed on page 100 panel 5, not on 090: the R1 page was drawn with the page-005 separate-lane field precisely so the theme's condition is met by composition, and both the theme entry and the page note say that if a layout pass consolidates the lanes the caption comes off the page. Theme 9's complication now states the two-directional form of the proposition, with its claim ceiling.

---

## Open editorial questions this document does not decide

1. **Where R1 lands** — page 092, page 102, or its own page. The three placements buy different things and cost differently; the table in R1 sets them out.
2. **How far R6 cuts** — options A through D. A is recommended and is parity-safe; D is defensible.

Both are editorial judgements, and both should be settled before the fog-map adoption pass (item 8) touches Chapter 6, since a compressed 096–100 changes which pages need map strips.

**Settled 5 September, by the owner, before any page changed:** R1 takes its own page, R6 takes option A. Both are applied. The fog-map adoption pass (item 8) is now unblocked for Chapter 6 and should plan strips against 089–102, with page 100 needing one it did not previously exist to need.

## Standing note

This read produced one addition and several subtractions, which is the right ratio for a book at this stage. The addition is R1, and it is the only item here that makes something happen rather than bounding something further. If only one item is taken, it should be that one.

**All thirteen were taken, on 5 September 2026.** The book is two pages shorter and one argument longer. Three items turned out to close items already open in [revision-priorities.md](./revision-priorities.md) — R9 closes item 16, R10 closes item 15, R12 closes item 9 — and two ran into their neighbours in ways this document did not predict: R1's own-page placement landed inside the forum because parity allowed nowhere else, which merged two of its three options into one, and R6's page count was wrong by one in a direction that only R1 made safe. What remains open is production work, not editorial: the [page-turn audit](../content/production-review.md) needs remeasuring, page 100 needs a thumbnail, and the fog-map pass has a changed Chapter 6 to plan against.
