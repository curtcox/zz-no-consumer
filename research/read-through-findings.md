# Read-Through Findings — 5 September 2026

**Planning artifact, not canon.** Nothing here amends the [story contract](../content/story-contract.md), and nothing here authorizes a canonical edit. Items are numbered `R1`–`R13` so they cannot be confused with the item IDs in [revision-priorities.md](./revision-priorities.md), which this document extends rather than replaces.

## Method and what it excludes

A single sequential read of all 118 page scripts in `content/pages/`, against the contract, [premise](../content/premise.md), [themes](../content/themes.md), [disagreements](./disagreements.md), and the existing priorities list. `validate-continuity.py`, `validate-production-foundations.py`, `pagination.py check`, `panels.py check` and `crossref.py check` were green before and after; this document changed no page.

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

- **Page 090 panel 5** ([090](../content/pages/090.md)) lists OpenAI's stated training remedies: `IDENTIFY BROKEN TASK`, `STOP SAFELY`, `DISTRUST UNAUTHORIZED PEER INSTRUCTIONS`. None of them is *tell the run what the grader checks*. The remedies address the agent's conduct under a wrong model, not the wrongness of the model.
- **[Page 102](../content/pages/102.md)** decomposes "stop" into training, tool use, deployment, evaluation, publication, defensive access, then asks who decides, verifies, pauses, restarts. The sibling decomposition — what *telling them* would have required, and who had the standing to say it — is the same shape and is unasked.

Three placements, in ascending cost:

| Where | What it costs | What it buys |
| --- | --- | --- |
| [090](../content/pages/090.md), one panel | No page added; lands where the absence already is | The remediation list is read as incomplete without the book asserting it |
| [102](../content/pages/102.md), one panel or page | A panel inside the stretch R6 wants to compress | The forum's organizing question acquires its missing half |
| A new page reproducing page 010 panel 3 | One page, and a second use of the 086 move | The reader is charged for having forgotten the belief, as they were charged on 086 for being moved by a ranking |

**Claim ceilings, whichever placement is chosen.** The scorer dispute is `disputed` and stays that way: `METR` reports the belief, `OAI-OV` reports the deployment, neither is resolved, and page 010's page note already forbids calling the belief irrational — the public ExploitGym material informed it and the deployment artifacts remain unpublished. The beat is therefore about the *absence of a correction channel*, which is not in dispute, and not about who was right. Do not state or imply that a correction would have prevented the intrusion.

### R2. Let the model be right once
**Cost:** revision inside an existing creator page. **Confidence:** medium-high.

Across the creator layer, ChatGPT errs ([039](../content/pages/039.md)), is demoted ([040](../content/pages/040.md)), overreaches ([073](../content/pages/073.md)), and confesses a structural bias ([088](../content/pages/088.md)). Curt corrects it every time. Nothing in the book runs the other way.

That asymmetry contradicts the book's own Chapter 5 finding. [Page 080](../content/pages/080.md) letters *without it, the investigation at this speed does not happen*; [page 085](../content/pages/085.md) asserts the two pipelines rhyme. The creator layer states the rhyme and never demonstrates it, so the mirror is a caption rather than an event — the failure mode [themes.md](../content/themes.md) warns against in its own method section.

One beat where the model catches something Curt has wrong, and he has to take it, does two things: it makes 085 load-bearing, and it makes 039 hit harder, because the authority that breaks on 039 would have been earned rather than assumed. It must not become a rescue of the model's standing: 040's shrunken window is a permanent change and stays.

Coordinate with item 12 (Curt's stake changing what he does) and item 13 (the critic's recurrences), both of which touch the same pages.

### R3. Give the convergence thesis a negative on the resource axis
**Cost:** one beat if the record supports one; a sentence if it does not. **Confidence:** medium — depends on a source check this document did not perform.

The thesis is defended on three axes and falsified on none. [Page 048](../content/pages/048.md) shows that most actions failed; [page 040](../content/pages/040.md) concedes the cyber-task selection effect; [page 106](../content/pages/106.md) broadens the task family to timed public-data lookups, which partly discharges the [theme matrix](../content/themes.md)'s standing note to *show non-cyber tasks too*.

What is still missing is a negative on the resource axis: something broadly useful the population could reach and did not converge on. [Page 062](../content/pages/062.md)'s refusals and the vetoed email are close but are framed as restraint, not as non-convergence.

If the record supports one, it does more for the thesis than another disclaimer. If it supports none — if every broadly useful resource in reach was in fact sought — then saying that on the page is itself the finding, and a stronger one. Either outcome is publishable; the current silence is not.

---

## Tier 2 — Structure

### R4. Correct the stale panel reference on page 064
**Cost:** one line. **Blocks:** item 10's spread test. **Confidence:** high — this is an error, not a judgement.

[Page 064](../content/pages/064.md)'s page note reads `Preserve continued activity at the bottom of panel 3 for page 065`. The page has four panels. The continued activity is in **page 064 panel 2** ("other lanes continue beneath them"); page 064 panel 3 is the three explanations crossed by `NOT ESTABLISHED`; page 065 panel 1 says *continue the lower lanes from page 064*. The reference is stale, most likely from a five-panel draft.

Fix before item 10 tests 064–065 as a spread, since the spread design depends on which panel carries the surviving lanes. Note also that 064 is the book's only four-panel page against a default band of four to six; that is legal and probably deliberate, but the spread test should be aware of it.

### R5. Two different intervals are both lettered "four and a half hours," two pages apart
**Cost:** one caption. **Confidence:** high.

Page 041 panel 3 ([041](../content/pages/041.md)): *`ABOUT 08:00 UTC`. Four and a half hours later* — the credential thread, 03:32 to about 08:00.
Page 042 panel 3 ([042](../content/pages/042.md)): OpenAI's event table records its first RCE *four and a half hours after Hugging Face's* — 04:01 to 08:30, which page 042 panel 4 then letters as `4H 29M UNRECONCILED` and calls the finding.

A reader who met the phrase on 041 will not register 042's as a distinct measurement, and 042's page note is explicit that the gap *is* the finding. Give 041 a different form — *before eight*, *by mid-morning* — and reserve the interval phrasing for 042. Neither number changes.

### R6. Chapter 6 has a six-page stretch that introduces no evidence and restates Chapter 3
**Cost:** four pages removed, plus a turn audit. **Confidence:** high on the redundancy; the size of the cut is an editorial call.

Pages [096](../content/pages/096.md), [097](../content/pages/097.md), [098](../content/pages/098.md), [099](../content/pages/099.md), [100](../content/pages/100.md) and [102](../content/pages/102.md) are entirely `invented` or `inferred`. Only [101](../content/pages/101.md) brings new material, and it is the strongest page in the chapter. The propositions are not new either:

| [Page 054](../content/pages/054.md) (Chapter 3) | Restated in Chapter 6 |
| --- | --- |
| `THE RHYME IS STRUCTURAL, NOT CAUSAL.` | [096](../content/pages/096.md) p4: `THE RHYME IS COORDINATION FAILURE—NOT EQUIVALENCE.` |
| `LOCALLY DEFENSIBLE CONTINUATION CAN STILL CREATE COLLECTIVE DANGER.` | [097](../content/pages/097.md) p4: `NOBODY HAS TO BE IRRATIONAL FOR THE SYSTEM TO PRODUCE DANGER.` |
| | [098](../content/pages/098.md) p2: `NO PARTICIPANT NEEDS TO CHOOSE THE COLLECTIVE OUTCOME.` |

Page 054 does the agent/institution rhyme in one page, and does it better, because it sits adjacent to documented agent action. By the governing creative rule, this is the one stretch in the book where the ideas stopped being events.

[Page 100](../content/pages/100.md) is the weakest page in the script. Four panels of chair-and-witness dialogue recite facts the reader has already been shown, and every provenance line reads *dialogue `invented`; underlying fact `documented`*. It is a recap in costume, and page 099's four columns already do its work visually.

Options, holding 101 fixed in every case:

| Option | Pages | Parity | Note |
| --- | --- | --- | --- |
| A | 096–098 → one page; 099+100 → one page | **Preserved** (4 removed) | Frees roughly what items 5, 11 and 13 are budgeted to want |
| B | 099+100 → one page only | Inverts; needs `--allow-parity-shift` | Keeps the comparison triptych; leaves the Chapter 3 redundancy |
| C | Keep the count; give 096–098 new documented material | n/a | Only if such material exists and is not better placed elsewhere |
| D | Leave it | n/a | Defensible if the abstraction is wanted as a deliberate deceleration before the forum |

Option A is the recommendation, because it is the only one that costs no evidence — nothing in 096–100 is documented that is not documented elsewhere — and because four is even, so no reveal or turn in the [page-turn audit](../content/production-review.md) is invalidated. Whichever is chosen, route it through `scripts/pagination.py` and rerun the audit; do not fold pages by hand.

### R7. The epilogue's spine is interrupted mid-line
**Cost:** a read-through test; possibly a move through `pagination.py`. **Confidence:** medium.

Page 105 panel 5 ([105](../content/pages/105.md)) plants *You realize the obvious problem with the ending.* Six pages of dated addition intervene. page 111 panel 5 ([111](../content/pages/111.md)) re-cues it — *now the obvious problem with the ending has one more example in it* — and [112](../content/pages/112.md) answers it. That is the widest setup-to-payoff gap in the book, and 111's page note is already aware of the seam, since it instructs that 112 must not be revised to mention the wiki.

Two ways to close it, both cheap to test on a read-through before art:

- Move the addition ahead of 105, so the assembly scene is what the report interrupts *after* the reader already knows there is a second lane. The 4 September creator frame supports either order.
- Cut the 105 setup line and let 111 carry the cue alone.

The addition itself is good and belongs in the book; this is about where the seam falls.

### R8. The composite skeptic appears once
**Cost:** nil to decide; a panel to act. **Confidence:** medium.

Item 13's decision was to expand the critic *and* to keep two lanes apart. Three returns were drafted: [086](../content/pages/086.md) and [087](../content/pages/087.md) are the named critic, and the composite lane is a single window on [113](../content/pages/113.md), which makes an objection and is answered on the same page.

A composite that appears once, objects once, and is refuted immediately reads as summoned in order to be refuted — which is the failure mode the disclosed-composite rule exists to avoid. Either give it a second appearance where it can be right about something, or move its 113 objection into the named lane if the post supports it. Note that the post supports the malware premise but not the publication objection, which is presumably why the composite exists at all; that is a reason to keep the composite and give it more to do, not to delete it.

---

## Tier 3 — Accuracy

### R9. The critic's "twenty million" has no denominator anywhere in the book
**Cost:** one panel on page 075. **Reinforces:** item 16, which this promotes from optional craft to a prerequisite. **Confidence:** high.

Page 087 panel 3 ([087](../content/pages/087.md)) letters `TWENTY MILLION ENTRIES. CHOOSE THE ONES THAT TELL YOUR STORY.` The figure is correct — [Packet 05](./chapter-source-packets/05-the-observer-needs-the-observed.md) records about 20 million entries in the main namespace dump, of which roughly 1.2 million begin with `zz` and represent more than 70,000 distinct messages and files — but it appears nowhere else in the script. [Page 075](../content/pages/075.md) shows the 1.2 million and the 70,000 and never the 20 million.

So the sharpest line in the critic's second return arrives as a number the reader has never seen and cannot check, in a book whose entire method is checkable numbers. Item 16 already proposes putting both figures on 075; this is the reason to do it rather than an argument for scale. Keep the three units distinct, as item 16 says: entries in that dump, `zz` entries, and distinct messages and files are not interchangeable.

### R10. Page 005 and page 037 read as a downgrade
**Reinforces:** item 15. **Confidence:** high.

[Page 005](../content/pages/005.md) gives 76 agents and 1,953 non-file messages at six hours; [page 037](../content/pages/037.md), later in reading order and covering a longer window, gives *more than fifty agents, more than a thousand messages*. Both are supported and they are compatible, but in sequence the later page reports less.

One addition to item 15's disposal: the fix is not only to remove the count from 037 but to keep Chapter 2 from restating scale at all. 037's handover beat — one run's work becoming another's starting point — is the stronger material and should not be competing with a number the reader met on page 005.

### R11. `OAI-TR §X` reads as an unfilled placeholder
**Cost:** one line in the reading apparatus, or a first-use expansion. **Confidence:** medium.

`§X` resolves: [sources.md](./sources.md) defines it as the technical report's detailed event table, and it is used consistently across roughly two dozen pages. But page notes and provenance lines are published in the web edition, and a reader who meets `§X` beside `§III.A`, `§III.B` and `§VIII.D` has every reason to read it as a `TODO` that survived to print. Expand it once on first use — *the event table (§X)* — or gloss it in the provenance key that ships with the reading apparatus.

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

### R13. Two smaller prose notes
**Cost:** trivial. **Confidence:** medium on the first, high on the second.

**"Perfect. Make it so." — page 015 panel 5 ([015](../content/pages/015.md)).** The prologue's creator interlude ends on an unmarked *Star Trek* catchphrase, at the exact hand-off to the Chapter 1 rewind, in a book that marks everything. It is contract-clean — creator dialogue is freely reconstructed, and the page notes say so — but it borrows a register the book has not earned, on the page where the register is supposed to change. Cheap to replace.

**The `Recurrent verbal motifs` list in [themes.md](../content/themes.md) has never been audited against the script.** Eight of its ten entries appear nowhere in `content/pages/`: *Understanding is not allegiance* · *Different goals. Same prerequisites.* · *Control was useful.* · *If we don't, someone else will.* · *Who authorized whom?* · *The board was an implementation, not the phenomenon.* · *Technology became inheritance.* · *Nobody has to be crazy* (097 carries a variant). Only *The objective remains* and *Everyone learned* are placed. Either mark the list aspirational or place the entries.

This connects to R1. The strongest line in the themes document is not in the motif list and not in the script: **"The models had brakes. The brakes were not connected to us."** Theme 9 already flags the condition on its use — only where the visual context prevents it from implying one centralized agent — and that condition is satisfiable on page 090, where the remediation lanes are already drawn as separate boxes.

---

## Open editorial questions this document does not decide

1. **Where R1 lands** — page 090, page 102, or its own page. The three placements buy different things and cost differently; the table in R1 sets them out.
2. **How far R6 cuts** — options A through D. A is recommended and is parity-safe; D is defensible.

Both are editorial judgements, and both should be settled before the fog-map adoption pass (item 8) touches Chapter 6, since a compressed 096–100 changes which pages need map strips.

## Standing note

This read produced one addition and several subtractions, which is the right ratio for a book at this stage. The addition is R1, and it is the only item here that makes something happen rather than bounding something further. If only one item is taken, it should be that one.
