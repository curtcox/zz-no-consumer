# Session summary — 11 September 2026 — scale, comprehension, and counterarguments

**Planning artifact, not canon.** This is the index to one working session. It amends nothing. It
exists so a fresh session can pick the work up without re-deriving it, and so the owner can see in one
place what was decided, what was written, and what is blocked on them.

## What the session was asked

Whether the book covers the incidents *and* the background of AI safety deeply enough for a reader
arriving with no knowledge of either; whether the page and panel count is adequate; what expansion to
*Watchmen* scale would cost; and whether the book should more directly incorporate arguments already
made by others online, including specific YouTube videos.

## The three documents written

| Document | What it is |
| --- | --- |
| [`scale-and-comprehension-2026-09-11.md`](./scale-and-comprehension-2026-09-11.md) | The evaluation. Items `S1`–`S15`, six recorded decisions, and the remaining open questions. **Read this first.** |
| [`ey-stanford-source-assessment.md`](./ey-stanford-source-assessment.md) | Admission assessment for the class-1 source, on the [`toner-title-source.md`](./toner-title-source.md) pattern. Not yet admitted. |
| [`counterarguments-survey-2026-09-11.md`](./counterarguments-survey-2026-09-11.md) | Fifteen objections, `C1`–`C13` plus registered priors, rated on engagement and force separately. |
| [`../design/synthetic-reader-protocol.md`](../design/synthetic-reader-protocol.md) | The stateless-reader comprehension test: nine arms, four personas, seven questions, three negative controls and the fidelity gate. Specification; not run. |
| [`../tasks/citation-verification.md`](../tasks/citation-verification.md) | Standing programme and tooling proposal for checking that every cited work exists **and** says what the book claims. Proposal; nothing authorized. |

## The findings that matter

**The premise was half right and wrong about the cause.** On the incidents, 118 pages is adequate —
[item 22](./revision-priorities.md) is currently arguing seven pages of June forensics could be five.
On the background, the page count is not the binding constraint. Three measurements, taken
11 September 2026:

- **Density.** The book sets its own ceiling at 180 lettered words per page and runs at a mean of
  **51**, with zero pages over. The existing 118 pages could carry roughly **3.5×** their current
  verbal content before touching a constraint the project has already accepted.
- **The explicit-argument budget.** The whole creator register — every page licensed to argue in the
  book's own voice — is **19 pages and about 1,466 lettered words.** Teaching a dozen ideas at the
  ~140-word density the book has proven it can sustain costs ~1,700 words: more than that register
  currently contains in total.
- **The conceptual map stops at the edge of the incident.** None of 31 searched safety concepts appears
  on any story page, which is the method working. But eighteen of them appear **nowhere in `content/`
  at all** — including evaluation awareness and sandbagging, in a book about an evaluation, and AI
  control, when Redwood co-authored the investigation.

**So the obstacle is a contract decision, not a number.** `themes.md` says the themes are not a lecture
track; [FQ-16](../content/appendix/faq/16-do-i-need-background.md) promises that a reader who finishes
unable to name the concepts means the book worked. That is the premise's opposite. The comprehension
requirement prices at **~56–84 pages**, not ~200.

**The best class-2 objection is not a governance argument.** Air-gapping an evaluation destroys its
fidelity, so the missing air gap has a second sufficient explanation that competition does not supply —
and [pages 016](../content/pages/016.md)–[017](../content/pages/017.md) already draw the one permitted
outward path as a condition.

**The owner's complaint about counterargument quality is published, and now read.** Swoboda et al.,
[arXiv:2501.04064](https://arxiv.org/abs/2501.04064), *Ethics and Information Technology* 2025, states
that skepticism toward the existential-risk discourse has received limited rigorous treatment in the
academic literature and that **"there are hardly any scholarly publications that rigorously and
systematically develop and present a position that opposes"** it — naming Müller and Cannon (2022) as
essentially the exception. It formalizes three arguments into premises and finds all three fall short
of compelling, which is the owner's own distinction reached independently.

**And it hands the book a peer-reviewed citation for class 2.** Arguing against the
pre-superintelligence checkpoint, it states that competitive pressure "may incentivize downplaying the
risks and pushing the frontier of AI capabilities," notes that **not a single lab joined the proposed
pause**, and concludes that labs unable to agree to a pause when the economic stakes are low give no
reason for confidence when the stakes are highest. That is the argument the book has never made, in an
academic venue, inside a paper about the *weakness* of the anti-risk arguments.

## Decided on 11 September

| Decision | Where it is recorded |
| --- | --- |
| **Name after earning** — event-first kept; one explicit naming beat per concept in the creator register; amend `themes.md`'s naming clause and rewrite FQ-16 | S3 |
| ***Watchmen* scale is an outer bound, not a target** — ~175–200 story pages plus 32–48 supplement pages; Option F (two volumes) deferred, not foreclosed | S5 |
| **The reader test runs before any page is committed** | S13 |
| **Comprehension testing starts synthetic** — stateless model readers first, real readers spent once and last, because a real reader has no second first reading | [`design/synthetic-reader-protocol.md`](../design/synthetic-reader-protocol.md); revises S13 |
| **The synthetic test measures role fidelity, not knowledge** — negative controls and a per-question gate, **not** subtraction of a no-text control | Same file; corrected 11 September |
| **Citations get a standing verification programme** with a publication gate, distinguishing *exists* from *says what we claim* | [`tasks/citation-verification.md`](../tasks/citation-verification.md) |
| **Scope is two classes of argument, not a literature list** | S15 |
| **Interleaved in-world supplements adopted, one chapter boundary trialled first** | S5, Option A |
| **The novella stays in lockstep, page for page** (+21k–31k words) | S14 Q6 |

Panel density resolved by consequence: at ~190 pages and the current 5.1 panels per page the book lands
near 970 panels, inside the 4–6 band. No `page-grammar.md` amendment needed.

## The two classes, and the sources for each

**Class 1 — why alignment is hard and how little is known.** Source located and assessed:
`EY-STANFORD`, Yudkowsky, *AI Alignment: Why It's Hard, and Where to Start*, Stanford, **5 May 2016**,
[video](https://www.youtube.com/watch?v=EUjc1WuyPT8), with an approximately complete transcript at
[intelligence.org/stanford-talk](https://intelligence.org/stanford-talk/) published 28 December 2016.
Stronger than `EK-TONER` because the transcript is authoritative rather than auto-captioned. The
load-bearing caveat: the talk's framing is 2016 utility-function coherence, and the strongest
objections attack exactly that framing, so it may not be presented as describing these agents. The
assessment names the trap this source invites — an *earlier* argument that appears to describe a later
event — and refuses it.

**Class 2 — race dynamics suppress the security practices you would require.** Air gaps, firewalls,
isolation, disclosure requirements, third-party audit. Searched across all of `content/` on
11 September: air gap **0**, firewall **0**, disclosure requirement **0**, third-party audit **0**.
The book has never made this argument — and has already staged the evidence for it six times, at
[016](../content/pages/016.md)–[017](../content/pages/017.md), [027](../content/pages/027.md),
[043](../content/pages/043.md), [055](../content/pages/055.md)–[056](../content/pages/056.md),
[094](../content/pages/094.md) and [110](../content/pages/110.md). **This is the strongest
naming-beat candidate in the project** and it is cheaper than class 1, because only the naming is
missing.

## Where the breaks come from

The naming beat needs a published objection at each break. From
[the survey](./counterarguments-survey-2026-09-11.md):

| Use | Objection | Why this one |
| --- | --- | --- |
| Class 1 break | **C3 — Aaronson**, *Why am I not terrified of AI?*, 6 Mar 2023 | Rejects the practically-relevant version of orthogonality and names an alternative. **[Page 062](../content/pages/062.md) is already evidence for his side and the book never says so.** The cheapest beat available. |
| Class 1 break | **C2 — Christiano**, 20 Jun 2022 | States the concern more strongly than the book does, then disagrees point by point. Un-dismissable. |
| Class 1 depth | **C1 — nostalgebraist**, 10 Jun 2022 | Attacks the fixed-goal wrapper framing that `EY-STANFORD` rests on. Deepest, hardest to letter — hold for the appendix. |
| Class 1 scope | **C5 — Garfinkel** | Concedes most, doubts the discontinuity. Notable because **the book depicts no discontinuity**, so it shows which objections do not apply to what is drawn. |
| Class 2 break | **C6 — the air-gap/fidelity tension** | A second sufficient explanation for something the book already drew as a condition. A break, not a debate. |
| Class 2 balance | **C7 — Buterin `d/acc`**, 27 Nov 2023 | Defensive capability needs no universal adoption. Its failure mode is already drawn at [055](../content/pages/055.md)–[056](../content/pages/056.md). |
| Class 2 test | **C8 — Checkpoints for Intervention** | [Page 027](../content/pages/027.md) is either its strongest counterexample or the checkpoint working, and the book has never had to choose. |
| **Class 1, highest read priority** | **C11 — Müller and Cannon**, *Ratio* 35(1), 2022 | *Existential risk from AI and orthogonality: Can we have it both ways?* Named by Swoboda et al. as the exception to the near-absence of rigorous scholarly opposition, and it attacks orthogonality — the thesis the book's strongest scenes rest on. **Outranks C1, C4 and C5.** |
| Class 2 academic anchor | **`XRISK-SKEPTIC-ANALYSIS`** Checkpoints section | Competitive pressure and the unjoined pause, peer-reviewed. |
| Class 2 primary source | **C12 — Richards, Agüera y Arcas, Lajoie, Sridhar**, NOEMA, 18 Jul 2023 | The serious version of the checkpoints argument, at its source. Grants that AGI is coherent, may arrive, and may conflict with human values. |
| Objection taxonomy | **C13 — Ambartsoumean and Yampolskiy**, 2023 | A survey of AI risk skepticism itself; where to find objections this survey missed. |
| **Both, in opposite directions** | **C10 — Shapiro**, X, **6 Sep 2026** | See below. |

## C10, the one that needs a deliberate editorial decision

David Shapiro's incentive-gradient argument, supplied in full by the owner. It is the **best
systems-level counterargument located**, and its first gradient — that USA/CCP competition makes AI
progress a political priority superseding domestic ones — **is class 2's own thesis stated by someone
who does not think it is a problem.**

So the book should cite one dated post **twice, in opposite directions**: as its strongest systems
objection, and as its best evidence for the suppressing mechanism. Better evidence than a sympathetic
source, because the author has no interest in establishing the book's conclusion.

The break is internal to the text: its second gradient is capital versus labour and undercutting
competitors, which is a **speed** incentive, and speed spends safety margin. The post is a well-drawn
statement of Moloch offered as evidence that Moloch is not a problem. Four other failure points are in
the survey, of which the most useful is that **"corrigibility" carries two meanings** — *does what the
customer says* versus *does not resist correction*, the latter named in `EY-STANFORD` as an unsolved
formal problem and failing on [page 063](../content/pages/063.md).

Handling: the post contains characterisations of people who disagree. The contract's critic rule
paraphrases the argument and does not reproduce or return them. **The argument survives their removal,
which is the test.** The date, 6 September 2026, was derived from the post's snowflake identifier and
is a computation, not a verified publication date — check it before a panel carries it.

## The methodological correction, and why it mattered

The owner's correction on 11 September: **the question is not whether a model knows the theory, but
whether it can give the answers it would give if it did not know.** That is a question about role
fidelity, and it invalidated the protocol's original instrument.

Subtracting a no-text control from a treatment arm measures *what the text added to a model that knows
everything*. That is not what a naive reader would receive, because a knowing model can reconstruct a
concept from a hint far too thin for a naive reader — so the delta can be large while the text taught a
newcomer nothing. **Subtraction cannot detect that failure and can inflate the estimate.**

Fidelity cannot be instructed — a persona is a costume, not amnesia. It can only be measured, the way
any instrument's sensitivity is: by checking that it registers absence. Hence three negative controls,
each defining a question a faithful reader **must** fail:

- **A6 ablation** — one inferential step removed; a model that still reaches the conclusion is filling
  from priors.
- **A7 decoy** — one mechanism replaced by a plausible different one; a faithful reader reports the
  substitute, a reciting model reports the real-world-correct version. The sharpest of the three,
  because its failure mode is unambiguous.
- **A8 unsupported probe** — a question the text genuinely does not support; a faithful reader says it
  does not know.

**The fidelity gate:** no positive result from any treatment arm is reportable for a question unless
that same model, version and persona passed A6–A8 *for that question*. Negative findings survive a
failed gate; positive ones do not. And the method may simply fail — if models cannot withhold, real
readers are the only instrument, and that is a live outcome rather than a hedge.

**One thing worth naming rather than burying.** This pass is an AI-mediated investigation of a book
about an AI-mediated investigation, and it has the failure mode the book documents:
[pages 078](../content/pages/078.md)–[080](../content/pages/080.md), an analysis agent adopting the
reviewed material's framing and producing something coherent and wrong, unspot-checkable at volume.
[CA-11](../content/appendix/contested/11-ai-mediated-investigation.md) asks whether such an
investigation can establish what it reports; Swoboda et al. name it *interpretability illusions*. If
this pass is run and reported, the creator register has a true thing to say about it.

## Pointers for updating the story and the repo

Nothing below is authorized; each is a located piece of work with its prerequisite.

**Zero-page work, highest leverage, do first** (S9):

- Raise density on ~20 existing creator and forum pages from ~60 to ~130 lettered words. **Adds roughly
  the size of the entire current creator register for zero new pages.**
- Route the reader to the appendix from inside the reading experience. 72,338 words of theory exist and
  the comic gives a newcomer no reason to know it.
- Add appendix entries for the S4 second-column absences — evaluation awareness and sandbagging first,
  then AI control, gradual disempowerment, goal misgeneralization. Prose work under existing rules.
- **Rewrite [FQ-16](../content/appendix/faq/16-do-i-need-background.md)**, which currently promises the
  opposite of the decision taken today.

**Two more things the Swoboda paper supplies, both cheap:**

- **"Interpretability illusions"** — plausible but misleading interpretations of a model — is the name
  for what [pages 078](../content/pages/078.md)–[080](../content/pages/080.md) already draw: an
  analysis agent adopts the attacker's framing, produces something coherent and wrong, and
  investigators cannot spot-check at volume. Appendix home:
  [CA-11](../content/appendix/contested/11-ai-mediated-investigation.md).
- **The triviality dilemma** — if every counterexample to "human frailty is the real cause" is
  redescribed as human frailty, the thesis becomes trivially true and uninformative. That is a reusable
  analytic move for [the fallacies section](../content/appendix/README.md). The paper's
  conceptual-ambiguity section (§2) is a second candidate, and it cuts against the book's own register
  as much as anyone's: it shows "extreme," "catastrophic" and "existential" used interchangeably on
  **both** sides of the debate.

**One strict handling rule from that paper.** It states it is "less concerned with exegetic accuracy"
and is "not attributing premises or conclusions specifically to any figures mentioned." So it may
**not** be used to attribute an argument to Gebru, Mitchell, Clegg or anyone else. Cite the
reconstruction as a reconstruction; go to the individual's own dated words for anything attributed to
that individual.

**Contract amendments the decisions require:**

- `themes.md` thematic method — the naming clause.
- `story-contract.md` admissions log — rows for `EY-STANFORD` and, if adopted, `DS-GRADIENT` and the
  class-2 sources. `DS-GRADIENT` is dated after the 30 August aftermath scenes and enters as a
  published argument in the creator register, exactly as `IOB-CIV` did.
- A possible third rule for the critic lanes. [S12](./scale-and-comprehension-2026-09-11.md) found that
  an unanswered *real* argument sits between the two existing lanes: the real-critic lane assumes a
  published counter to concede to, and the composite lane is for objections no dated writing makes.
  C10 mostly resolves this for class 2, and the general gap remains.

**Registration, per the `EY-STANFORD` checklist:** locator pass against the transcript;
[`sources.md`](./sources.md); [`cast.md`](./cast.md) as text-only writers;
[`scene-provenance.md`](./scene-provenance.md); the public [source index](../content/source-links.md);
the vault manifest; additional reference rows on
[CA-15](../content/appendix/contested/15-instrumental-convergence.md) and
[CA-16](../content/appendix/contested/16-orthogonality.md) **with the objections in the same pass**,
since the appendix requires two distinct stances and admitting the difficulty argument alone would make
those entries worse.

**Existing items this session interacts with:** [item 13](./revision-priorities.md), expanding the
critic into a recurring voice — decided 5 September, three returns drafted, the September and ending
rows still open; this session's class 1 and class 2 beats are additional returns and should be planned
with it, not separately. [Item 8](./revision-priorities.md), the fog-map adoption pass, adds placements
rather than pages and is unaffected. [Item 22](./revision-priorities.md)'s proposed two-page saving is
not assumed anywhere here.

**Sequencing** (S10): decide nothing further until the reader test runs; then the zero-page work; then
one supplement boundary; then two naming beats as three-page name/break/narrow units; **only then**
price the full expansion, with the novella and art costs in the same budget.

## The videos, as they now stand

| Key | Source | Status |
| --- | --- | --- |
| `EY-STANFORD` | Yudkowsky, *AI Alignment: Why It's Hard, and Where to Start*, Stanford, 5 May 2016 | Assessed; transcript published by MIRI; locator pass owed |
| `RM-SANDBOX` | Rob Miles, *AI? Just Sandbox it…*, **Computerphile, 23 June 2017**, 7 m 41 s | Metadata verified from the page; **argument unheard** |
| `RM-BOX` | Rob Miles, *Keeping AI in a Box*, **Robert Miles AI Safety, 14 July 2026**, 81 s | Metadata verified from the page; **argument unheard** |
| `DS-GRADIENT` | Shapiro, X post, 6 Sep 2026 (date derived) | Full text read, supplied by the owner |
| — | A Carl Brown video on Hugging Face security | **Not located.** Two candidate videos surfaced, neither confirmed as his |

**The Rob Miles pair is the find of the session for class 2**, and it is better than a single video.
`RM-SANDBOX` is the canonical popular treatment of the class-2 remedy set — sandboxing, boxing,
disconnection. `RM-BOX`, nine years later, is its author saying *"my take doesn't quite hold up"* and
linking back to it.

Three things follow:

1. **It pairs with C6 as the same insight from opposite ends.** C6: air-gapping an evaluation destroys
   the evaluation's fidelity. Boxing: a box you can extract useful work from is not a box. Together they
   move class 2's remedy set from *controls nobody paid for* to *controls in tension with the purpose of
   the exercise* — a stronger version of the book's own argument and a harder one to dismiss.
2. **`RM-BOX` is dated 14 July 2026 — one day after the second-civilization attack window closes,
   inside the third-civilization branch, and weeks before anything was public.** It cannot be
   commentary on the incident and must never be drawn as such. For a book organised around dated
   records it is something rarer: a contemporaneous public statement on containment by someone with no
   knowledge of the events, inside the events' own timeline.
3. **It gives the naming beat one author on both sides** — the 2017 argument and its author's own 2026
   revision. The book neither invents the break nor sets two people against each other, and
   self-revision is the register [page 088](../content/pages/088.md) already runs on.

**What is unknown and decides everything: which direction the take fails.** `RM-SANDBOX` argues against
simplistic containment; a revision could mean that dismissal was too confident — boxing **more** viable
than he said, which cuts against class 2's premise — or the opposite. Both readings are live. **Do not
draft either beat until the 81 seconds are heard.**

## Done on 11 September, after the summary was first written

**`DS-GRADIENT` is vaulted.** Manifest row `shapiro-incentive-gradient` in the tracked
[`data/256t-sources.tsv`](../data/256t-sources.tsv); body imported through
`sync-256t.py import --captured-via owner-supplied-text`, the documented path for a source a publisher
blocks from archival fetch. The record carries a sha256 and a header recording the date derivation, the
disposition, and two things that were **not** verified: whether the supplied text is the complete post,
and whether it is a single post or the head of a thread. The most perishable citation in the project is
no longer only in a conversation.

**Running that import surfaced two findings the citation brief now records.**

**1. Seventeen of twenty-six tracked sources have bodies that differ from their last snapshot, and two
return HTTP 403.** `sync-256t.py check` fetches every manifest URL and compares hashes; it was run on
11 September. The 403s are both NYT and are a already-recorded condition. The seventeen need reading
carefully: `CHANGED` means *this body differs from the one we stored*, which for an HTML page can be a
substantive edit or an ad slot. **The tool cannot tell the difference** — the existence-versus-content
-match distinction showing up in the one place it can be measured.

Two things do stand out. **Every stable row is a PDF or a static page**, including all four controlling
PDFs; where a PDF and an HTML page carry the same material, **prefer the PDF as the citation target.**
And **eight of the changed rows are the book's controlling primary sources** — `metr-investigation`,
`openai-overview`, `openai-initial-incident`, `huggingface-incident`, `huggingface-timeline`,
`metr-methodology`, `openai-pacing`, `openai-collective-defense` — which pages cite as `documented`.
Whether any changed substantively is unknown, and finding out is manual work on eight documents.

**2. The check will cry wolf permanently on some rows, which is a tooling defect.** A browser-export or
owner-supplied body can never match a fetched one, and a YouTube watch page is dynamic.
`shapiro-incentive-gradient`, both `robmiles-*` rows and `nyt-hf-podcast-video` are in that class. At
26 sources the signal is already buried; at 800 it is unusable. The brief now proposes a per-source
expectation flag — `fetchable` / `dynamic` / `browser-only` — so drift is reported only where a hash
comparison means something.

**And a precedent that partly answers the Rob Miles source-family question.** The manifest already
carries **two** Rob Miles rows, `robmiles-pascals-mugging` and `robmiles-respectability`, both noted as
*"creator-formation reference, not an incident source; disposition in
[`content/creator-characters.md`](../content/creator-characters.md)."* So the author is already
registered as a family, with a category and a disposition location, and the mechanism is per-work rows
sharing one disposition. **But the new use is a different category**: creator-formation reference
explains how Curt came to think as he does, whereas `RM-SANDBOX` and `RM-BOX` would be cited as
argument about containment — a load-bearing claim, not a biographical influence. The precedent supplies
the registration pattern, not the disposition, and reusing that note would silently upgrade two
biographical rows into evidence. **The contract question in ask 3 is narrower than it was, and still
open.**

## What I need from you

1. **`RM-BOX` is 81 seconds — watch it and tell me which way the take fails.** The caption track exists
   (English, auto-generated) but YouTube returned an empty body in every format this session tried. This
   is the single highest-value item on the list and the cheapest: it decides whether the source points at
   class 2's premise or its remedy set.
2. **The Carl Brown video URL.** Not located by search. Note what it would be *for*: a practitioner's
   account of which ordinary controls were missing is **evidence for class 2**, not a counterargument to
   it, and it belongs with the [professional objections](../content/appendix/README.md). Two candidates
   surfaced and **neither is confirmed as his** — I will not cite either on the assumption.
3. **Rob Miles as a source family, not a source.** "Too many to name" is a contract problem: the
   admissions log admits one source at a time, with its own date, level and permitted pages. A body of
   explainer work by one author needs either many rows or a different mechanism. **That is your decision,
   not a research finding** — and it is the one structural question in this session I cannot resolve.
4. ~~**May I vault the `DS-GRADIENT` text now?**~~ **Done** — see above. What follows from it and is
   **not** done: whether to spend the manual pass on the **eight controlling primary sources** whose
   bodies have changed since their last snapshot. That is the highest-value citation work available
   right now, it is exactly the "check directly in advance of publication" requirement, and it is
   eight documents of reading rather than a tooling job.
5. **How the synthetic pass gets run**, unchanged: whether I build the extractor (small, reuses
   `panels.py`'s lettering parser, testable against its 6,020-word total), and whether the reader is a
   subagent or a session you drive. **I cannot be the reader** — I have read the contract, themes, beat
   sheet and appendix. Run the gates before any treatment arm.
6. **Whether A5 runs** — book plus appendix. If it scores far above the book alone, you need routing, not
   56–84 pages. Cheapest way to find out S3 was wrong.
7. **C11 (Müller and Cannon, *Ratio* 35(1), 2022)** is paywalled and is the top unread priority — it
   attacks orthogonality and Swoboda et al. name it as the exception to the absence of rigorous
   scholarly opposition. Institutional access or a copy beats my working around it.
8. **Whether any of the citation programme is approved**, and if so whether to start with `extract` and
   `report` so the census shapes the rest. Nothing in that brief is authorized by its existence.
9. Unchanged: whether `DS-GRADIENT` is cited twice in opposite directions; whether its date is verified
   from the page; and whether class 2 gets one naming unit or two.

## What this session did not do

No page was inserted, moved, or deleted. No canonical content was edited. No contract was amended. No
source was admitted. Nothing was committed. The four structural checks
(`validate-continuity.py`, `validate-production-foundations.py`, `pagination.py check`,
`panels.py check`) and `pagelinks.py check` were green before and after; the two ambiguous-reference
notes that remain are pre-existing, in `README.md` and `research/art-pilot-2026-09-07/README.md`.
