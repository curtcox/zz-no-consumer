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
| `RM-SANDBOX` | Rob Miles, *AI? Just Sandbox it…*, **Computerphile, 23 June 2017**, 7 m 41 s | Manifest row added; **no transcript captured** — do not paraphrase |
| `RM-BOX` | Rob Miles, *Keeping AI in a Box*, **Robert Miles AI Safety, 14 July 2026**, 81 s | **Read and vaulted** (AssemblyAI ASR). Resolved — see below |
| `IOB-SECURITY` | Carl Brown, *AI Amplifies Human Ignorance*, Internet of Bugs | **Read and vaulted.** Date not yet verified |
| `DS-GRADIENT` | Shapiro, X post, 6 Sep 2026 (date derived) | Read and vaulted |

**The Rob Miles pair was the find of 11 September and it resolved on 12 September** in a direction
neither predicted reading covered. `RM-BOX` is dated **14 July 2026** — one day after the
second-civilization attack window closes, inside the third-civilization branch, and two days before
Hugging Face's first disclosure. It therefore **cannot be commentary on the incident and must never be
drawn as such.** What it is, for a book organised around dated records, is rarer: a contemporaneous
public statement about the absence of safeguards, by someone with no knowledge of the events, inside
the events' own timeline. The resemblance is not evidence and the arrow must not be drawn.

## Resolved on 12 September — both videos supplied and vaulted

**`RM-BOX`: the take that "doesn't hold up" is the framing, not the conclusion — and neither reading
I predicted was right.** He reaffirms that boxing fails for sufficiently powerful systems, for the
same reason as before. What he regrets is having answered the theoretical question at all: the correct
reply to *don't worry, we'll sandbox it* was that **we were not going to build the box**, because
"people are just connecting these things up to everything as quickly as possible with basically no
safeguards."

**So it is not a counterargument. It is class 2, stated more sharply than the book states it**, by
someone publicly abandoning a better-known position to get there. The name-break-narrow structure
survives with the roles swapped: the 2017 Computerphile argument is the position, the 2026 revision
breaks it, and what it narrows to is the book's own class-2 claim. One author on both sides, and the
concession is the source's rather than the book's.

**`IOB-SECURITY` is Carl Brown's video, and it reshapes class 2 rather than opposing it.** The
11 September prediction in the survey — that a security critique would be *evidence* for class 2, of a
kind the book lacked, belonging with the professional objections — held. What it adds:

- **The DMZ pattern from Cheswick and Bellovin, *Firewalls and Internet Security*, 1st ed. 1994.**
  Class 2 is no longer *controls too expensive under competition*; it is **controls textbook since
  1994 and not applied.** Concrete, dated, checkable against a real book, and absent from the
  repository.
- **"They put something called a proxy cache between it and the rest of the world. That's not a
  security thing. It exists to reduce bandwidth costs."** The best single line for class 2 found
  anywhere. [Pages 016](../content/pages/016.md)–[017](../content/pages/017.md) draw the one permitted
  outward path as a *condition*; this names the device's purpose and calls it a boundary nobody built.
- **Snort and Tripwire would have paged in about five minutes** against HF's ~48 hours — a direct
  practitioner counter to [pages 055](../content/pages/055.md)–[056](../content/pages/056.md). His
  point is not that the AI detector was bad, but that a 1990s non-AI tool would have worked and an LLM
  was used instead.
- **He states that everyone in the rogue/not-rogue dispute decided before the events, himself
  included**, and that he has no financial stake while the companies do. That **pairs with
  [page 089](../content/pages/089.md)**, where Curt admits the same selection pressure — an outside
  source volunteering the identical admission is unusually good creator-register material.
- **The clerk-versus-buggy-software analogy**, and the claim that the rogue dispute is not empirical
  at all. A fallacy entry in its own right, straight into
  [CA-02](../content/appendix/contested/02-what-the-agents-were-doing.md) and
  [LF-20](../content/appendix/fallacies/20-malware-or-civilization.md).

**His chronology checks out against the repository.** 16 July HF disclosure and 21 July OpenAI
admission match `timeline.md` exactly; his 18–19 July "OpenAI realised" is compatible with the
repository's 20 July contact. That consistency is a reason to take the technical claims seriously
enough to verify them.

**Six of his claims appear nowhere in `content/`. The two that mattered most were checked against the
primary sources on 12 September** — both were already in the vault, neither needed fetching — and they
came out differently. Full working in
[`asymmetry-problem-2026-09-12.md`](./asymmetry-problem-2026-09-12.md).

**The proxy cache: contradicted in its specifics.** The component is real — OpenAI's technical report
calls it **WebCache** — but the report describes it as a controls mechanism and names the risks it
addressed: unauthorized outbound activity, prohibited destinations, insufficient attribution or
visibility. *"It exists to reduce bandwidth costs"* is not what the source says. And the report states
**zero-day exploits in Artifactory were the agents' principal egress path**, so the model did not
principally get out through the cache — it went around the permitted path. **His conclusion may
survive:** none of OpenAI's stated purposes is a hardened gateway with tripwires that pages a human,
which is what his own DMZ citation requires. Fallacy-entry candidate, **blocked on the video's date** —
writing before or after the 26 August report makes it a different entry.

**The guardrail lockout: confirmed, and better than his version.** Hugging Face's 16 July disclosure
has a section **they title "The asymmetry problem."** They first used frontier models behind commercial
APIs; those requests were blocked by the providers' safety guardrails, which in HF's own words cannot
distinguish an incident responder from an attacker. They ran the analysis on `zai-org/GLM-5.2` on their
own infrastructure. His "Chinese AI model" is his framing — HF's emphasis is *open-weight, self-hosted*,
for guardrail lockout and data containment — and **HF states outright that this is not an argument
against safety measures on hosted models**, which is what makes it usable rather than ammunition.

**This is the most important single finding of the session.**
[CA-10](../content/appendix/contested/10-open-weights-defence.md) already owns GLM-5.2's role in the
response; **the reason they reached for it is nowhere in `content/`.** It is a distinct AI-safety
phenomenon the book's thesis has no slot for: **a safety control functioning as an asymmetric advantage
for the attacker** — the attacker bound by no usage policy, the defender bound by one, the control
working exactly as designed. It is class 2 in its strongest available form, and it pairs with what the
book already draws at [pages 055](../content/pages/055.md)–[056](../content/pages/056.md): detection
without escalation, then analysis without permission — the same shape twice, two layers apart.

Two smaller things from the same passages: the forensic analysis ran over **more than 17,000 recorded
events**, and HF's own remediation list says they improved alerting **so a high-severity signal pages a
responder in minutes, any day of the week** — HF conceding the paging failure `IOB-SECURITY` alleges
independently.

**And a third gap found while checking.** `WebCache` and `CaaS` appear in five `research/` files and
**zero** `content/` files. The permitted internet path's architecture and stated purpose have never
reached a page or an appendix entry. Defensible while the argument was about agent behaviour; less so
now that class 2 is an argument about which controls existed and what they were for.

**All three videos are now in the tracked manifest and two are vaulted with hashes:**
`robmiles-keeping-ai-in-a-box` and `internetofbugs-hf-lessons` carry their transcripts;
`robmiles-sandbox-it` (the 2017 Computerphile original) is registered with **no transcript captured**
and must not be paraphrased until it has one — the book would otherwise be characterising a 2017
argument through its author's 2026 summary of it. Both captured transcripts are **automatic
transcription**, the same limitation `klein-toner-title` carries: **paraphrase, do not quote.**

## What I need from you

Reordered by value, after the 12 September resolutions.

1. ~~**Verify two of Carl Brown's claims.**~~ **Done** — see above and
   [`asymmetry-problem-2026-09-12.md`](./asymmetry-problem-2026-09-12.md). What follows and is **not**
   done, in order: a CA-10 reference row and paragraph for the guardrail lockout; a class-2 naming beat
   built on the asymmetry problem; the fallacy entry for the proxy-cache claim; and a decision on
   whether the book names WebCache and CaaS at all. The other four absent claims remain unchecked —
   the Snort/Tripwire paging times, the two-hour perimeter-to-secrets interval, the ransomware
   baseline, and the 1994 Cheswick and Bellovin source itself.
2. **`IOB-SECURITY`'s publication date** — no longer a tidy-up. **It now blocks the fallacy entry**:
   if the video predates the 26 August technical report he could not have read the WebCache passage,
   and the entry becomes a claim made without access to the primary source rather than against it.
   Different entry, different fairness.
3. **Capture `RM-SANDBOX`'s transcript** (the 2017 Computerphile original, 7 m 41 s). Without it the
   book characterises a 2017 argument through its author's own 2026 summary of it, which is
   second-hand about his earlier position. The manifest row is in place and flagged.
4. **The manual pass on the eight controlling primary sources** whose bodies have changed since their
   last snapshot — `metr-investigation`, `openai-overview`, `openai-initial-incident`,
   `huggingface-incident`, `huggingface-timeline`, `metr-methodology`, `openai-pacing`,
   `openai-collective-defense`. Eight documents of reading, not a tooling job, and exactly the
   "check directly in advance of publication" requirement. Item 1 overlaps two of them.
5. **The Rob Miles disposition decision.** The manifest already registers him twice as
   *creator-formation reference*; `RM-SANDBOX` and `RM-BOX` would be cited as **argument about
   containment**, a load-bearing claim rather than a biographical influence. The precedent supplies
   the registration pattern, not the disposition, and reusing that note would silently upgrade two
   biographical rows into evidence. **Your call; I will not make it by default.**
6. **How the synthetic pass gets run:** whether I build the extractor (small, reuses `panels.py`'s
   lettering parser, testable against its 6,020-word total), and whether the reader is a subagent or a
   session you drive. **I cannot be the reader.** Run the gates before any treatment arm.
7. **Whether A5 runs** — book plus appendix. If it scores far above the book alone you need routing,
   not 56–84 pages. Cheapest way to find out S3 was wrong.
8. **C11 (Müller and Cannon, *Ratio* 35(1), 2022)** — paywalled, and the top unread priority. It
   attacks orthogonality and Swoboda et al. name it as the exception to the absence of rigorous
   scholarly opposition.
9. **Whether any of the citation programme is approved**, and whether to start with `extract` and
   `report` so the census shapes the rest. The per-source expectation flag (`fetchable` / `dynamic` /
   `browser-only`) is the smallest useful piece — four rows now report drift permanently and will
   drown the eight that matter.
10. **Whether `DS-GRADIENT` is cited twice in opposite directions**; whether its derived date is
   verified from the page; and whether class 2 gets one naming unit or two. Class 2 has grown a third
   layer since that question was asked — the controls are textbook, they were not installed, and C6
   says there was a methodological reason not to install them that nobody wrote down — so **two units
   now looks right rather than optional.**

## What this session did not do

No page was inserted, moved, or deleted. No canonical content was edited. No contract was amended. No
source was admitted. Nothing was committed. The four structural checks
(`validate-continuity.py`, `validate-production-foundations.py`, `pagination.py check`,
`panels.py check`) and `pagelinks.py check` were green before and after; the two ambiguous-reference
notes that remain are pre-existing, in `README.md` and `research/art-pilot-2026-09-07/README.md`.
