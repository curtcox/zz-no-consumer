# Scale and Comprehension — 11 September 2026

**Session index:** [`session-summary-2026-09-11.md`](./session-summary-2026-09-11.md) is the one-page
map of this document, the two source documents beside it, the six decisions, and the list of what is
blocked on the owner.

**Planning artifact, not canon.** Nothing here amends the [story contract](../content/story-contract.md),
and nothing here authorizes a page insertion. Items are numbered `S1`–`S14` so they cannot be
confused with `R1`–`R13` in [read-through-findings.md](./read-through-findings.md) or the numbered
items in [revision-priorities.md](./revision-priorities.md), both of which this document extends
rather than replaces.

**Three decisions were taken on 11 September 2026, after the measurements below were reported.**
They are recorded at the points they govern (S3, S5, S10) and summarised in
[Decided on 11 September](#decided-on-11-september). In short: **name after earning**;
*Watchmen* scale is an **outer bound, not a target**; and the **reader test in S13 runs before any
page is committed**. A fourth decision on 11 September set the **scope of the teaching as two classes
of argument rather than a list of literature concepts** (S15), and two more adopted the supplement
trial and novella lockstep (S5, S14). Only the video inventory in S15 remains open.

**The question this document answers.** The owner's premise, stated 11 September 2026: the book
should cover *both* the incidents *and* the background of AI safety — how things could get out of
control — deeply enough that a reader arriving with no knowledge of either understands both after
reading, and the current page and panel count may not be adequate for that. This document tests
that premise against measurement, sets out what expansion to *Watchmen* scale would actually cost,
and lists the decisions only the owner can make.

## Method and what it excludes

Measurements were taken on **11 September 2026** from the working tree at `c9fdf7bd` with fourteen
untracked candidate images present. Structural counts come from the tools that own them
(`pagination.py report`, `panels.py report`, `novella.py report`, `appendix.py report`,
`panelart.py status`). Per-register lettered-word splits were computed ad hoc by scanning the
lettering blocks in `content/pages/*.md` and total **5,932** against `panels.py`'s authoritative
**6,020**; the split is an approximation of a number the tool owns, accurate to about one percent,
and should not be quoted as a tool output.

The concept inventory in S4 is a substring search of `content/`, not a semantic audit. A concept
can be taught without its name appearing. The inventory establishes what is *nameable* to a
reader, which is the specific thing the premise asks about.

No reader test has been run. Every claim below about what a newcomer would understand is inference
from structure, and the single most valuable thing that could be done before spending pages is to
replace that inference with evidence — see S13.

---

## The measurements

| Surface | Quantity (11 Sep 2026) |
| --- | --- |
| Story pages | 118, in 8 chapters and 39 sequences |
| Scripted panels | 606, exposed as 590 image slots |
| Panel rhythm | 5 panels on 95 pages; 4–6 is the default band; two nine-panel pages |
| Lettered words, whole book | 6,020 — a mean of **51 per page** |
| Density ceiling the project sets itself | **180** lettered words per page; **0** pages over |
| Densest page actually written | ~156 words ([page 101](../content/pages/101.md), the continuation case) |
| Pages over 100 lettered words | 11 |
| Creator-register pages | 19, carrying ~1,466 lettered words |
| Novella prose | 44,394 words, mean 376 per page |
| Appendix | 120 entries, 72,338 words |
| Panel art | 590 of 590 slots filled; **139 decided**, 451 provisional |

*Watchmen*, for the comparison the premise invokes: twelve issues of 26 comics pages, filling 32
ad-free story pages per issue, so roughly **312 comics pages** plus something like 44–66 pages of
interleaved prose supplement behind chapters 1–11; the 2014 collected edition runs 448 pages with
covers and front matter. Issue 1 carries **196 panels over 26 pages — 7.5 per page** — and only
nine of its twenty-six pages are true nine-panel grids. Verify the per-issue supplement split
before building on it; the sources found were consistent on the 32-page figure and vague on the
backmatter breakdown.

---

## S1. The premise is half right, and the half it gets right is the important half

Split the question, because the two halves have different answers.

**On the incidents, the page count is adequate and possibly generous.** 118 pages carry the
April–July chronology, the rebuild, the second population, the Hugging Face attack chain, the
investigation, the aftermath, and the September wiki addition, with 108 of 118 pages carrying at
least one appendix entry. [Item 22](./revision-priorities.md) is currently arguing that seven
pages of June forensic development could be five. That is not the profile of a section starved for
room.

**On the background — what AI safety is, and how a reader should think about things getting out of
control — the count is not the binding constraint, and the premise misidentifies what is.** The
book is not short of pages for that material. It is short of three other things, in this order:
permission (S3), nameable concepts (S4), and lettered words (S2). Adding 200 pages without
changing the first two would produce a longer book that teaches the same three ideas.

## S2. The binding constraint today is density, not pagination

The book sets its own ceiling at 180 lettered words per page and runs at a mean of 51. Nothing is
over. The densest page in the manuscript is about 156 words, and the pages nearest that ceiling are
exactly the argument pages — [039](../content/pages/039.md) at ~139, [101](../content/pages/101.md)
at ~156, [110](../content/pages/110.md) at ~126, [111](../content/pages/111.md) at ~136. They work.
The form demonstrably carries argument at roughly 140 words a page.

So the existing 118 pages could carry something on the order of **three and a half times** their
current verbal content before touching a constraint the project has already accepted. In round
numbers: 6,020 words now, about 21,000 available.

This has a direct consequence for the premise. The whole creator register — every page on which the
book is licensed to argue in its own voice — is **19 pages and about 1,466 lettered words**. That is
the entire explicit-explanation budget of the graphic novel: less than six minutes of speech. If the
requirement is to teach a dozen background ideas nameably, at the ~140-word density the book has
proven it can sustain, the cost is roughly **1,700 words of new explicit argument** — more than the
creator register presently contains in total, and about 8% of the headroom available inside the
current page count.

**Therefore:** the teaching requirement, priced on its own, costs something like **20 dense pages,
or 40–60 pages at the book's normal density if the ideas are dramatized rather than asserted.** It
does not cost 200. Expansion to *Watchmen* scale is a legitimate ambition, but it must be justified
by something other than the comprehension gap, because the comprehension gap is not that expensive.

## S3. The real obstacle is a locked contract decision, not a number

[`content/themes.md`](../content/themes.md) opens with the thematic method: *"The themes are not a
lecture track running beside the plot."* Introduce as event, produce consequences, complicate, and
**name the idea only after the reader has already experienced it.**

[FQ-16](../content/appendix/faq/16-do-i-need-background.md) then states the goal in terms that
directly contradict the new premise:

> If you finish the book able to describe what happened and not able to name the three concepts,
> the book worked.

That is a deliberate, documented, defensible choice — and it is the opposite of "comprehensible to
someone coming in without an existing knowledge of either." One of the two has to give. The premise
is not asking for more pages. **It is asking to revise the book's theory of how it teaches**, and the
page count is downstream of that.

Three positions are available, and the owner has to pick one before any page is inserted:

| Position | What it means | What it costs |
| --- | --- | --- |
| **Hold the method** | The comic stays experiential; comprehension of the theory is the appendix's and novella's job. Fix the *routing* to them instead. | Nearly nothing in pages. Rejects the premise. |
| **Name after earning** | Keep event-first, but add an explicit naming and generalizing beat once per concept, in the register already licensed for it. | ~20–40 pages; amends `themes.md`'s method and rewrites FQ-16. |
| **Teach directly** | A lecture track — a primer, concept chapters, interleaved explainers. | 50–80 pages; contradicts the method outright and puts the book's restraint at risk. |

**Decided 11 September 2026: name after earning.** The middle position. Event-first survives; the
book acquires an explicit naming and generalizing beat once per concept, in the creator register,
and the two documents that promise otherwise are amended rather than quietly contradicted —
`themes.md`'s naming clause and FQ-16, which currently promises this decision's opposite. The
standing note applies at full strength: a naming beat that does not change what happens next is the
alibi, not the method. S5–S10 are costed against this position.

## S4. What is actually absent: the concept inventory

Thirty-one named ideas from the AI-safety literature were searched across `content/`. **None of the
thirty-one appears on any of the 118 story pages.** That is the method working as designed, not a
defect.

The finding that matters is the second column. These appear **nowhere in `content/` at all** — not
in the appendix, not in the themes, not in the novella:

mesa-optimization · inner alignment · deceptive alignment · alignment faking · situational
awareness · sandbagging · evaluation-gaming · intelligence explosion · recursive self-improvement
(twice, in passing) · gradual disempowerment · goal misgeneralization · interpretability ·
chain-of-thought monitoring · AI control as a named research agenda · takeoff speeds · compute
governance · treacherous turn · Omohundro's basic drives

These appear in `content/`, but **only in the appendix**: instrumental convergence, orthogonality,
race dynamics, corrigibility, power-seeking, specification gaming, reward hacking, Goodhart,
superintelligence, scheming, Bostrom, Yudkowsky, Turner.

Two observations follow.

**The appendix is deep where it goes.** [CA-15](../content/appendix/contested/15-instrumental-convergence.md)
alone carries seventeen references across formal defence, counterargument, deflationary readings and
published rebuttal. 72,338 words of appendix is not a book that skimped on theory.

**But it is narrow.** The theory it covers is the theory the *incident illustrates*. A reader who
finishes this book understands one failure mode extremely well and has never encountered the
argument that a system might behave differently when it believes it is being evaluated — which is,
for a book whose subject is an evaluation, a conspicuous hole. `AI control` is absent by name even
though **Redwood Research co-authored the investigation the book is about.** Gradual disempowerment
is absent even though the ending is about everyone continuing.

That is the specific shape of the gap the premise senses. It is not "not enough pages." It is
**"the conceptual map stops at the edge of this incident."**

**Superseded in part, 11 September 2026.** This inventory is a literature checklist, and the owner
replaced it with two classes of *argument* (S15). The inventory remains useful as a coverage
measurement and as the source of appendix work under S9, but it is no longer the scope decision.
S15 governs what gets a naming beat.

## S5. Expansion options

Six, costed independently. They are not exclusive, and the first two are the ones that survive
scrutiny.

### Option A — Interleaved supplements (the actual *Watchmen* mechanism)

*Watchmen* does not teach through panels. It teaches through backmatter: Hollis Mason's memoir, the
Nova Express interview, Rorschach's psychiatric file, the ornithology monograph — in-world documents
behind chapters 1–11, filling out each 32-page issue.

This project has **72,338 words of appendix already written** and sitting *after* the book, addressed
by page number. Converting a selected part of it into interleaved, in-world chapter-end supplements —
a METR report excerpt, a Black Hat slide, a plain explainer blog post, a transcript fragment, a
practitioner's objection as a published letter — reaches for *Watchmen*'s structure using material
that already exists and already passes `appendix.py check`.

- **Pages:** 8 chapter boundaries × 4–6 pages ≈ **32–48 pages**, and they need not be story pages.
- **New writing:** low. This is selection, re-registration and re-voicing, not drafting.
- **Risk:** the appendix's current strength is that it refuses to settle anything. An in-world
  document has a voice and therefore a position. Anything moved into this lane needs a disclosed
  author and must not acquire authority it has not earned.
- **Invariant note:** supplements outside the numbered story count do not touch parity and do not go
  through `pagination.py`. That is the cheapest structural change available anywhere in this document.
- **Decided 11 September 2026: adopted, one boundary trialled first.** Build a single chapter-end
  supplement and read it in place before committing the remaining seven. The risk above is the thing
  the trial is testing: whether a document with a disclosed author and therefore a position can sit
  behind a chapter without acquiring authority the appendix deliberately withholds from itself.

### Option B — Name-after-earning beats in the creator register

The register is already licensed to argue, already carries the book's densest pages, and already
does exactly this on [038](../content/pages/038.md)–[040](../content/pages/040.md): Curt names
instrumental convergence, a published critic breaks it, and [040](../content/pages/040.md) rebuilds
a smaller claim. That three-page shape — **name it, break it, narrow it** — is the book's own
working method for teaching a concept, and it has been used once.

Applied to S15's two classes of argument rather than to a list of concepts:

- **Pages:** **18–30**, expanding the creator register from 19 pages to ~40.
- **Contract cost:** amend the naming clause in `themes.md`; rewrite FQ-16, which currently promises
  the opposite.
- **Why it is the strongest option:** it does not invent a new formal device, it does not require a
  reader to accept a lecture, and every concept arrives already contested — which is the only way
  this particular book can teach theory without becoming the advocacy document it refuses to be.
- **Risk, and it is the real one:** the [standing note](./revision-priorities.md) in the priorities
  list. *"If a further revision makes the account only more qualified without making anything happen,
  it has stopped being this book's method and started being its alibi."* A naming beat that does not
  change what happens next fails that test. Each of the eight to twelve needs a consequence.

### Option C — A primer chapter before the prologue

12–16 pages teaching the background cold, before the incident starts.

- **Pages:** 12–16, and parity-neutral if even.
- **Verdict: recommend against.** It front-loads a lecture onto a book whose opening is its strongest
  asset, and it is the one thing *Watchmen* never does. If a reader needs the primer to proceed, the
  180-word ceiling and the creator register were the wrong tools all along. Keep this in reserve as a
  site-only or edition-only front section, where it costs no story pages.

### Option D — An objections register (see S11)

The external-argument lane expanded from three returns into a standing voice.

- **Pages:** 10–20, depending on how many arguments are admitted and whether they fit inside existing
  creator pages as [item 13](./revision-priorities.md) planned.

### Option E — Widening the incident lanes

More of the wiki population, the third civilization, the investigation, the defensive side.

- **Pages:** 20–60, effectively unbounded.
- **Verdict: does not serve the premise.** It deepens the incident, which S1 finds is the half already
  adequately covered. Pursue it if the incident wants it, not as a comprehension fix.

### Option F — Two volumes

Volume 1 the incident; Volume 2 the argument and the aftermath. Combined, *Watchmen* scale.

- **Verdict: the honest structural answer if the owner genuinely wants 312 pages.** A 312-page single
  volume of this material is a different book with different pacing problems. Two volumes let the
  argument volume be as explicit as it needs to be without the incident volume losing its restraint.
  It is also a publication decision, not an editorial one, and belongs with
  [`content/publication-plan.md`](../content/publication-plan.md).

### The recommendation

**A + B, in that order,** at a combined **56–84 new pages**, taking the book to roughly 175–200 story
pages plus supplements. That is short of *Watchmen* and, on the measurements in S2, it is the size the
comprehension requirement actually justifies.

**Decided 11 September 2026: *Watchmen* scale is an outer bound, not a target.** The size is set by
the comprehension requirement and not by the envelope, which puts the book at roughly 175–200 story
pages plus 32–48 pages of supplement. Options C and E are not pursued for this purpose. Option F is
not adopted and is not foreclosed: it remains the route if a later decision wants 312 pages, and it
belongs with [`content/publication-plan.md`](../content/publication-plan.md) when it is taken. The
consequential figures move with the bound — **+21,000 to +31,000 novella words** and **+290 to +410
image slots**, not S7's tripling.

## S6. Panel count is a separate decision from page count

*Watchmen* averages **7.5 panels per page**. This book averages **5.1**, with the 4–6 band as its
default and nine-panel grids reserved for convergence, scale, or repeated attempts. Ninety-five of
118 pages carry exactly five.

Reaching a *Watchmen*-like **~2,340 panels** therefore requires more than adding pages. At 312 pages
and the current 5.1 average the book would land near 1,590 panels. Getting to 2,340 means amending
[`design/page-grammar.md`](../design/page-grammar.md)'s default band or reclassifying a large number
of pages as procedural sequences, and `panels.py` refuses to leave the band without
`--allow-rhythm-shift`.

Whether that is desirable is a genuine open question and not obviously yes. The nine-panel grid on
[page 006](../content/pages/006.md) — nine lanes, nine failures, six captions, seven lettered words —
is the single most efficient teaching page in the book *because* it is the exception. A book that is
all grid loses that.

## S7. What Watchmen scale would cost the rest of the project

Page count is the cheapest part of the expansion. The four surfaces keyed to it are not.

| Surface | At 118 pages | At ~312 pages | Cost |
| --- | --- | --- | --- |
| Novella prose | 44,394 words | ~117,000 | **+73,000 words**, at mean 376 per page |
| Image slots | 590 | ~1,560 | **+970 slots** to generate, review and choose |
| Art decided | 139 of 590 (24%) | 139 of 1,560 (9%) | the decision backlog roughly triples |
| Appendix page keys | 108 of 118 pages covered | ~194 new pages uncovered | re-keying, plus new entries to keep coverage |

The novella is the one that is easy to underestimate: **the prose edition is a per-page obligation,
and it is 100% complete today.** Every page added is a prose page owed. At 44,394 words for 118
pages, tripling the book means writing a second novella longer than the first.

The art backlog is the one that is easy to overestimate, because `produce.py` and the panel chooser
already scale. But 139 decided of 590 is 24% after a full generation pass, and a 1,560-slot book at
that rate has 1,180 provisional panels in it.

## S8. Invariants any expansion plan has to respect

1. **Parity.** Story page 1 is a recto. Inserting an odd number of pages inverts recto and verso for
   everything after it and invalidates 92 parity assertions and 21 named page-turn beats.
   **Build every expansion unit in even numbers**, or budget an explicit repair pass. `pagination.py`
   refuses without `--allow-parity-shift` and repairs nothing.
2. **Chapter membership is editorial.** Page *ranges* are derived; membership is chosen. Adding pages
   means choosing chapters and sequences for them, in one tool operation.
3. **Nothing is renumbered by hand**, in six trees at once.
4. **Supplements outside the numbered count** (Option A) are exempt from 1–3. This is a strong reason
   to try Option A first.

## S9. Cheap fixes that should be tried before spending any pages

These cost nothing structural and may move the comprehension needle more per unit of effort than
pages will.

- **Raise the density of existing argument pages.** The mean is 51 against a self-imposed 180. Twenty
  existing creator and forum pages taken from ~60 words to ~130 adds ~1,400 words of explicit
  argument — roughly the size of the entire current creator register — **for zero new pages.**
  This is the highest-leverage single move in this document.
- **Route the reader to the appendix from inside the reading experience.** 72,338 words of theory
  exist and the comic gives a newcomer no reason to know that. The web edition can do this without
  touching a page script.
- **Fill the second column of S4 in the appendix first.** Entries for evaluation awareness, AI
  control, gradual disempowerment and goal misgeneralization are prose work under existing rules,
  need no page insertions, and will reveal which concepts actually want a naming beat.
- **Rewrite FQ-16 to say what the book now intends.** It currently promises the premise's opposite.

## S10. Sequencing

Order matters more than the totals here, because S3's decision invalidates or authorizes everything
after it.

1. **Decide S3** — hold the method, name after earning, or teach directly. Nothing below is safe
   before this.
2. **Run S13's reader test.** Two or three newcomers, the existing 118 pages, and the question *what
   do you now think could go wrong and why*. This is the evidence the premise currently lacks.
3. **Do S9's zero-page work.** Measure again.
4. **Try Option A** on one chapter boundary. Supplements are parity-exempt; a single trial is cheap.
5. **Try Option B** on two concepts, one of them from S4's second column, as a three-page
   name-break-narrow unit. Test the pacing before committing to eight more.
6. **Only then** price the full expansion, with S7's novella and art costs in the same budget.

---

## External arguments: what exists, and what scaling it needs

## S11. The mechanism is already built, tested, and under-used

[Page 039](../content/pages/039.md) is the template and it is a strong one. A published critique
enters as a window beside the ChatGPT window — byline and date on-panel, `CARL BROWN — INTERNET OF
BUGS — 3 SEPTEMBER 2026` — as attributed paraphrase, set as text on a screen. No face, no body, no
room, no invented dialogue. Its opening frame makes the formal point that the reader cannot tell the
two windows apart by looking; the model then defends the book's thesis and is contradicted by the very
next frame; Curt concedes at the foot of the page.

The contract already licenses this in two lanes: **the real critic**, by attributed paraphrase of
dated public writing, and **a disclosed composite foil** for objections no dated writing makes,
currently used once as `SKEPTIC — COMPOSITE` on [page 113](../content/pages/113.md).
[Item 13](./revision-priorities.md) decided on 5 September to expand the critic into a recurring
voice and drafted three returns inside existing panels. Two rows of its candidate table — the
September discovery and the ending — are still open.

So the owner's third question is not asking for a new capability. **It is asking to scale a lane
that is built, decided, and running at three returns.** The open work is source admission, not
invention.

## S12. Admitting a YouTube video: the protocol that exists

Three video or audio sources are already admitted, each with an item-by-item assessment file:

| Key | Source | Assessment |
| --- | --- | --- |
| `OAI-BH` | OpenAI Black Hat USA talk, 5 Aug 2026 | timestamp locators 14:06, 17:03, transcript in the vault |
| `HF-POD` | Hard Fork, Roose and Newton interview Cotra, 4 Sep 2026 | [cotra-hardfork-interview.md](./cotra-hardfork-interview.md) |
| `EK-TONER` | Klein interview with Toner, 18 Aug 2026 | [toner-title-source.md](./toner-title-source.md) |

[`toner-title-source.md`](./toner-title-source.md) is the reusable pattern, and it is strict in ways
worth stating before the owner picks videos:

- a **locator** — the timestamp where the passage begins, and the surrounding context timestamp;
- **caption verification**, with the explicit note that auto-generated captions are not an
  authoritative verbatim transcript, so publication uses paraphrase;
- an **item-by-item disposition table** — admit / defer / not admitted — with a **claim ceiling** per
  item;
- an **evidence level**: expert commentary is not an investigation, and admitting one passage admits
  nothing else from the same interview.

`EK-TONER` admits exactly one formulation, for one FAQ entry, and explicitly declines the
interview's incident chronology, its counts, and six other topics. That is the bar.

Three consequences for the videos the owner wants to include:

1. **A YouTube argument enters as a creator-register window, not as narration.** It can change what
   Curt does next; it cannot become an incident fact. An argument about how things could get out of
   control is *evidence of what was argued*, never evidence of what happened.
2. **Each video needs its own assessment file and its own admissions-log row** in the contract, with
   a date and an evidence level. That is a real per-source cost — the Toner assessment is a careful
   document for a single sentence — and it is the cost that makes the on-panel citation followable.
3. **An argument nobody has published a response to is the interesting case and the hardest one.**
   The book's device is that a critique *breaks something*. If the argument has never been addressed,
   there is no published counter to paraphrase, and the book's own answer becomes the project's
   inference — which is permitted, labelled `inferred`, but it puts Curt in the position of answering
   rather than conceding. That is a different beat from [page 039](../content/pages/039.md) and it
   should be designed deliberately, not reached by default. The composite-foil lane exists precisely
   for objections no dated writing makes; an unanswered *real* argument sits awkwardly between the
   two lanes and may need a third rule.

## S13. The measurement this whole document is missing

No reader test has been run. Every judgement above about newcomer comprehension — including S1's —
is structural inference.

Before spending 56 or 200 pages: give two or three people with no AI-safety and no security
background the existing 118 pages, and afterwards ask them to say in their own words what happened
and what they now think could go wrong and why. If they can do the first and not the second, S3's
middle position is correct and the page budget is real. If they can do neither, the problem is not
the background material. If they can do both, FQ-16 was right and the premise is answered without
spending a page.

This is the cheapest item in this document and the only one that produces evidence rather than
argument.

**Decided 11 September 2026: the test runs before any page is committed.** It gates step 3 onward in
S10. Record the design and the outcome here, including the reader count and the exact question asked,
so a later reader can tell the evidence from the inference above it.

## S14. Open questions for the owner

These are decisions no amount of further research resolves. **Questions 1 and 2 were decided on
11 September 2026** and are kept here, struck through, so the order of reasoning stays legible.

1. ~~**S3.** Hold the method, name after earning, or teach directly?~~ **Decided: name after earning.**
2. ~~**Is *Watchmen* scale a target or a ceiling?**~~ **Decided: an outer bound; ~175–200 story pages
   plus supplements. Option F deferred, not foreclosed.**
3. **Panel density** (S6): amend the 4–6 band, or keep 5.1 and let the page count carry the growth?
4. ~~**Which concepts from S4's second column are in scope?**~~ **Decided: neither eight nor twelve.
   Two classes of argument instead — see S15.**
5. **Which videos**, and what is each one's argument? **Partly answered:** class 1's source is
   identified in S15. Class 2 has no video yet. Still needed per video: the URL, the timestamp, and
   one sentence on the claim.
6. ~~**Does the novella follow the expansion page for page?**~~ **Decided: lockstep. +21,000 to
   +31,000 words at the adopted bound; the shared page key holds across both editions.**
7. ~~**Is the appendix to be partly re-voiced as interleaved in-world supplements?**~~ **Decided:
   yes, trialling one chapter boundary first.**

## S15. The scope of the teaching: two classes of argument

**Decided 11 September 2026.** The naming beats do not cover a list of literature concepts. They
cover **two classes of argument**, chosen by the owner. This is a better scope than S4's inventory
for a specific reason: each class is an *argument that can be broken and narrowed*, which is what
Option B's three-page unit needs, whereas a concept name is only a label. S4's list survives as a
coverage measurement and as appendix work under S9.

### Class 1 — Why alignment is hard, and how little is known about how to do it

**Source identified.** Eliezer Yudkowsky, *AI Alignment: Why It's Hard, and Where to Start*,
Stanford University, 26th Annual Symbolic Systems Distinguished Speaker series, **5 May 2016**;
[video](https://www.youtube.com/watch?v=EUjc1WuyPT8), posted by MIRI 28 December 2016 with slides,
notes, references and an approximately complete transcript at
[intelligence.org/stanford-talk](https://intelligence.org/stanford-talk/) and the announcement at
[intelligence.org/2016/12/28](https://intelligence.org/2016/12/28/ai-alignment-why-its-hard-and-where-to-start/).
Proposed key: `EY-STANFORD`. **Not yet admitted** — it needs its own assessment file and an
admissions-log row before any panel cites it. The assessment is drafted at
[`ey-stanford-source-assessment.md`](./ey-stanford-source-assessment.md), and the objections it must
be registered alongside are surveyed in
[`counterarguments-survey-2026-09-11.md`](./counterarguments-survey-2026-09-11.md).

Three properties make this an unusually clean admission by this project's standards:

1. **An authoritative transcript exists**, published by the speaker's own institute. `EK-TONER` rests
   on auto-generated captions and [its assessment](./toner-title-source.md) says plainly that those
   are not an authoritative verbatim record. This source has no such weakness, so the paraphrase
   ceiling is set by the text rather than by the transcription.
2. **It predates the incident by ten years**, so it raises no dated-record problem at all. It cannot
   retrofit a scene and cannot act as incident evidence. It enters as background argument, which is
   the only thing the book wants from it.
3. **The counter-literature is already registered.** [CA-15](../content/appendix/contested/15-instrumental-convergence.md)
   already cites the deflationary and skeptical side — *AI as Normal Technology*, the LessWrong
   counterarguments post, Turner's *reward is not the optimization target*, and the critique of
   Turner et al. So this class can be named, broken and narrowed with dated sources on both sides,
   which is exactly the [page 039](../content/pages/039.md) shape.

**One correction to the owner's framing, stated because it changes the beat.** This class is *not* an
argument that has never been addressed. It has a large published counter-literature, some of it
already in this appendix. That is a feature: it means Curt can concede to a real dated answer rather
than the project having to invent one. The genuinely unaddressed material is class 2.

**What the book must not take from this source.** It is a 2016 talk about open technical problems.
It is evidence of what was argued, in 2016, about the difficulty of the problem. It is not evidence
about the 2026 incident, not evidence that any specific later event was foreseen, and not a finding
about any agent population in this book. The claim ceiling is the talk's own claim.

### Class 2 — Race dynamics suppress the security practices you would otherwise require

Air gaps, adequate firewalls, network isolation, regulation including disclosure requirements,
third-party audit. The argument is that competitive pressure does not merely accelerate capability
work — it makes the ordinary, boring, well-understood security controls unaffordable to the actor
who adopts them unilaterally.

**This is the real gap, and the measurement is unambiguous.** Searched across the whole of
`content/` on 11 September 2026:

| Term | Story pages | Anywhere in `content/` |
| --- | ---: | ---: |
| air gap / airgap | **0** | **0** |
| firewall | **0** | **0** |
| disclosure requirement | **0** | **0** |
| third-party audit | **0** | **0** |
| safety case | 0 | 1 |
| insurance | 0 | 1 |
| liability | 5 | 19 |
| isolation | 5 | 16 |

The book has race dynamics as [theme 4](../content/themes.md), but framed as *unilateral restraint
in capability development is costly*. Class 2 is a different argument in the same family: a claim
about **security engineering and governance**, not about model training. The book has never made it.

**And the book has already staged all the evidence for it.** This is what makes class 2 the single
strongest naming-beat candidate in this document — it names something the reader has already been
shown, six times, without being told what it was:

| Already on the page | The class-2 claim it supports |
| --- | --- |
| [Page 016](../content/pages/016.md)–[017](../content/pages/017.md): one permitted outward path in the evaluation configuration, single-sourced | The air gap was not there, and the reason was operational |
| [Page 027](../content/pages/027.md): responders describe the problem correctly and stopping is not required | Correct description does not produce escalation |
| [Page 043](../content/pages/043.md): the launchpad becomes staging, egress, and command-and-control | An evaluation with an internet base |
| [Pages 055](../content/pages/055.md)–[056](../content/pages/056.md): the detector correlates the attack correctly and fails to page the on-call team | Detection quality and policy quality are separate |
| [Page 094](../content/pages/094.md): the multistate letter's preservation, whistleblower and cease-and-desist demands | Disclosure and preservation as external requirements, not voluntary practice |
| [Page 110](../content/pages/110.md): the disclosure gap, attributed and dated | What non-disclosure does to the record |

So class 2 costs *less* than class 1, because the events already exist and only the naming and
generalizing beat is missing. Provisionally **one three-page unit for class 1 and two for class 2**,
the second of class 2's being the remedy set — air gap, firewall, disclosure, audit — named as things
that exist, are well understood, and were not adopted.

**The hard part of class 2, flagged early.** The owner is right that it is under-addressed, and that
cuts both ways: there is little published counter-argument to paraphrase. Under S12's third
consequence this puts Curt in the position of *answering* rather than *conceding*, which is a
different beat from [page 039](../content/pages/039.md) and needs its own design. Two routes exist
and the choice should be deliberate: the disclosed-composite foil lane, which the contract already
licenses for objections no dated writing makes; or admitting a dated source on the security side —
the AISI comparative report, the collective cyber-defence letter, and the attorney-general letters
are all already registered and all speak to required practice. Prefer the second where it reaches.

**Still open.** The owner referred to *specific YouTube videos* raising arguments they have not seen
addressed. Only class 1's source is identified. Class 2 has no video source yet, and per S12 each
video needs a URL, a locator timestamp, and one sentence on its claim before assessment work can
start.

### S15.1 — Where the breaks come from

The naming beat needs a published objection at each break, and
[the counterargument survey](./counterarguments-survey-2026-09-11.md) collects them. Three findings
from it change the plan above.

- **The owner's observation that genuine counterarguments are scarce is itself published.**
  Swoboda et al., *Examining Popular Arguments Against AI Existential Risk*
  ([arXiv:2501.04064](https://arxiv.org/abs/2501.04064), *Ethics and Information Technology*, 2025),
  states that skepticism toward the existential-risk discourse has received limited rigorous
  treatment in the academic literature. That is a citable version of the complaint, from authors
  trying to fix it, and it belongs in the appendix.
- **Class 1's break is cheap, because the book already drew the counterexample.** Aaronson's
  *Why am I not terrified of AI?* rejects the practically-relevant version of orthogonality, and
  [page 062](../content/pages/062.md) — agents refusing, objecting, and showing restraint — is
  evidence for his side that the book has never acknowledged as such.
- **Class 2's break is not a governance argument.** The strongest objection is methodological:
  air-gapping an evaluation destroys the evaluation's fidelity, so the missing air gap has a second
  sufficient explanation that competition does not supply. [Pages 016](../content/pages/016.md)–[017](../content/pages/017.md)
  already draw the one permitted outward path as a condition; this reads it as a defensible design
  decision. That is a break, not a debate.

## Decided on 11 September

| Decision | Recorded where |
| --- | --- |
| Name after earning: event-first kept, one explicit naming beat per concept in the creator register | S3; amends `themes.md`'s naming clause and FQ-16 |
| *Watchmen* scale is an outer bound; the size is ~175–200 story pages plus 32–48 supplement pages | S5 recommendation; Option F deferred, not foreclosed |
| The S13 reader test runs before any page is committed | S13; gates S10 step 3 onward |
| Scope is two classes of argument, not a literature list; S4's inventory demoted to measurement | S15 |
| Option A adopted, one chapter boundary trialled before the other seven | S5 Option A |
| The novella stays in lockstep, page for page | S14 Q6; +21k–31k words |

Consequences that follow from the second decision and are not yet applied anywhere else: the
novella obligation is **+21,000 to +31,000 words**, not +73,000; the art obligation is **+290 to
+410 image slots**, not +970. S7's table describes the 312-page case, which is no longer the plan.

## Standing note

The premise is right that something is missing and wrong about what. The missing thing is not room.
It is **permission to name what the book is about**, and a conceptual map that does not stop at the
edge of this incident. Both are contract decisions. The page count is what those decisions cost, and
on the measurements here they cost less than the premise assumes.
