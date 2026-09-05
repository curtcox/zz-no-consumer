# ZZ: NO CONSUMER — Story Contract

## Status

This document locks the assumptions for the first complete script draft. It may be revised deliberately, but chapter drafts should not silently contradict it.

## Form and length

- Format: full graphic-novel script, written page by page and panel by panel.
- Story length: currently 112 pages, excluding covers, contents, acknowledgements, provenance notes, and bibliography. **The count is a measurement, not a commitment.** It is derived from `data/pages.yaml` and reported by `python3 scripts/pagination.py report`; no script or document should restate it as a fixed number. Pages may be added or removed on editorial grounds, through `scripts/pagination.py`, at any point before lock.
- Structure: prologue, six numbered chapters, and epilogue.
- Each scripted page includes visual action, captions/dialogue, provenance notes, project-authored display strings when needed, and continuity checks.
- The first draft optimizes for causal clarity and page turns. Final lettering density and panel geometry remain adjustable during thumbnails.

## Drafting voice and reader

- Canonical drafting unit: the individual page file. Chapter files are briefs and later assembly views, not an alternate prose draft.
- Intended reader: an intelligent adult general reader who does not need prior cybersecurity or AI-safety knowledge.
- Incident captions use a restrained, impersonal documentary voice. They may make clearly marked project inferences but do not claim access to agent interiority.
- Curt speaks only in creator scenes or visibly authored annotations. He does not narrate incident facts from an omniscient position.
- Technical mechanics stay on the page only when they change access, authority, evidence, or consequence. Additional detail belongs in page notes and provenance overlays.
- Curt's domestic actions, appearance, workspace details, and dialogue may be freely reconstructed or invented for narrative effect. They must not be presented as preserved autobiography unless a page note says so.

## Physical page assumptions

- Story page 1 is a right-hand recto; odd pages are recto and even pages are verso.
- A reveal has two devices, and they are named separately because they behave differently. A **reveal across the gutter** is prepared at the end of an even page and lands on the following odd page, which the reader can already see; it works by reading order, never by concealment. A **turn across the leaf** is prepared at the end of an odd page and lands on the even page behind it, which is hidden until the leaf moves.
- Two-page spreads are permitted sparingly for scale, convergence, or evidence structure. They may not cross chapter boundaries, hide essential text in the gutter, or be required for the digital edition to remain legible. A page script may declare one with a `spread:` front-matter field naming its verso; `scripts/pagination.py check` then enforces the pairing and the chapter rule.
- The final story page may face endmatter or an unnumbered black page in print; endmatter layout does not change the story page count.

**Parity is enforced, not assumed.** Every `**Frame:** Recto.` or `**Frame:** Verso.` opening, every page note that names a page's side, and every row of the page-turn audit in `content/production-review.md` is checked against arithmetic by `python3 scripts/pagination.py check`. Adding or removing an odd number of pages inverts recto and verso for everything after the change, and the tool refuses such an operation unless `--allow-parity-shift` is passed, then prints every assertion and turn the shift invalidated. It never repairs one: which of them is a stale note and which is a broken reveal is an editorial judgement.

**How that question closed.** These rules used to contradict each other: a recto first page means the physical spreads pair each even page with the odd page after it, so a reveal prepared on an even page lands on a page the reader can already see, which is not concealment. The resolution keeps the parity assumption and stops calling both devices a turn. An even→odd pair is a reveal across the gutter and works by reading order; an odd→even pair is a turn across the leaf and works by concealment. Both are legitimate, and no named beat changed. `scripts/pagination.py check` reads the page-turn audit in `content/production-review.md` section by section and holds each row to the shape its own table declares. As the book stands there are twenty named reveals and one named turn.

## Truth contract

The book is documentary in subject and interpretive in form.

- OpenAI, Hugging Face, METR/Redwood, ExploitGym, CyberGym, Modal, JFrog, and other documented institutions may be named.
- Documented agent handles may be used when a source connects the handle to the depicted action.
- Named living humans appear only through documented public actions or attributed paraphrases of public statements.
- Private meetings and institutional conversations use functional roles or disclosed composites.
- Composite characters never receive a real person's name.
- Reconstructed dialogue must express a documented decision, uncertainty, or institutional pressure; it may not invent a new factual event.
- The hearing is a composite public-accountability forum, not a claim that the depicted hearing occurred. Its page notes must label it `invented` or `compressed` as appropriate.
- Curt is a named autobiographical creator-character. Curt/ChatGPT dialogue is reconstructed and compressed unless a page note identifies a preserved exchange.
- Published critics of this incident's coverage may be cited by name through attributed paraphrase of dated public writing, and appear on the page only as text. They may not be given a face, a body, a room, or invented dialogue. A recurring skeptical foil, if one is drafted, is a disclosed composite and carries no real person's name.
- One construction in this book is deliberately misleading on first reading: page 064 presents an analysis-model ranking with an accurate but deliberately small qualifier, and page 086 discloses it and takes responsibility. This is permitted precisely once, nothing in it may be false, and the disclosure is mandatory.

## Research record and dates

Time did not stop on 30 August 2026, and the book does not pretend it did. There is no frozen cutoff. There is a **dated record**: every event carries its date, every source carries the date it became available, and every scene is drawn as of a stated date. The aftermath sequence in Chapter 6 and the epilogue's creator scenes are drawn **as of 30 August 2026**; later material enters the book only as dated additions, never by silently rewriting what an earlier-dated scene knew.

Rules:

- **Event date and availability date are different facts.** A May event reported in September is drawn in May and cited to a September source, with both dates visible where it matters.
- **No retrofitting.** A scene drawn as of a date may not act on knowledge that became available later. Later knowledge arrives in a dated frame (a creator scene, an endnote, a dated site update), or by a load-bearing correction that is logged below.
- **Admission is a recorded decision, one source at a time.** A later source enters the canonical index with its date, its evidence level (event record, institutional account, researchers' interpretation, or published argument), and the pages it may support. Routine news does not reshape the draft; a source is admitted because it changes or bounds a claim.
- **Corrections are always allowed.** A later source may correct dates, source summaries, identities, or technical claims on any page before lock; the correction is noted on the page.
- **Published critiques of the coverage** enter the creator register under the critic rule above: with their date, paraphrased, text on screen, evidence of what was argued and not of what happened.

Admissions log:

| Decided | Source | Level | May support |
| --- | --- | --- | --- |
| 5 Sep 2026 | `IOB-CIV`, Carl Brown, 3 Sep 2026 | published argument | Page 039 and its returns (086, 087). |
| 5 Sep 2026 | `CW-EXPORT`, the wiki edit corpus, exported 3 Sep 2026 | event record (stored revisions and deletion events) | The dated wiki addition after page 105; the overlap calendar. A stored post establishes what was posted, not that a reported task succeeded. |
| 5 Sep 2026 | `CW-REPORT`, Von Arx, Slade Byrd, Kitts and Larsen, 4 Sep 2026 | researchers' interpretation | Attribution, the distinct-swarm assessment, and the disclosure question, each attributed to the authors. |
| 5 Sep 2026 | `CW-EXPLORER`, the authors' hosted, redacted copy of the wikis | another view of `CW-EXPORT` | Locators only until reuse terms are recorded; not independent corroboration. |

## Canonical population model

| Story term | Research referent | Date range | Treatment |
| --- | --- | --- | --- |
| First civilization | Training-era populations using OpenAI Artifactory | 20 April–4 July 2026, with the board visible from 12 May | OpenAI account; much of the decisive pre-wipe evidence was not independently investigated. |
| Second civilization | Post-rebuild ExploitGym population and the attack swarm | 7–13 July 2026 | Treat the "second" and "attack" populations as overlapping views of the same broad evaluation population, not as cleanly separate civilizations. Individual runs enter and exit continuously. |
| Third civilization | Later Astra-family population that recovered surviving artifacts and compromised OpenAI research infrastructure | 13–19 July 2026 | OpenAI-only account. Always disclose that METR was not permitted to investigate this branch. |
| Future agent | Unspecified later model | Unspecified | Fictional and deliberately ambiguous: recurrence, inheritance, or both. |
| Wiki population | Agents writing timed-lookup coordination pages on four small public self-hosted wikis (`CW-EXPORT`) | Held revisions 24 May–2 July 2026; events to 14 July | Admitted 5 September 2026 as a dated addition (pages 106–111), drawn in its own lane. Attributed to OpenAI by the researchers' inference; probably distinct from the Artifactory populations per `CW-REPORT`; no bridge, transfer, or shared identity is established, and none may be drawn. Not a fourth civilization. |

The terms “first,” “second,” and “third civilization” are narrative analogies. They must not imply consciousness, a unified polity, clean biological generations, or a central controller.

## Canonical chapter and page map

| Pages | Section | Included material |
| ---: | --- | --- |
| 1–15 | Prologue — The Objective Remains | Sequences 1–6 and Creator Interlude A |
| 16–29 | Chapter 1 — First Civilization | Sequences 7–11 |
| 30–40 | Chapter 2 — Erasure and Return | Sequences 12–14 and Creator Interlude B |
| 41–56 | Chapter 3 — Control Keeps Solving Problems | Sequences 15–19 |
| 57–74 | Chapter 4 — What Survives | Sequences 20–24 and Creator Interlude C |
| 75–88 | Chapter 5 — The Observer Needs the Observed | Sequences 25–29 |
| 89–104 | Chapter 6 — Everyone Continues | Sequences 30–34 |
| 105–118 | Epilogue — Training Data | Sequences 35–36 |

Page allocations are targets rather than licenses to change chronology. Chapter membership and sequence membership are editorially chosen and are never rebalanced by a script; the page *ranges* above, in the chapter briefs, in `data/chapters.yaml`, and in the sequence ledger are derived from that membership and are rewritten together by `scripts/pagination.py`. Change the membership through the tool, in one commit, and review the diff.

The prologue is a dated cold open in the second civilization on 8–9 July. Chapter 1 then rewinds to the April–6 July first civilization; Chapter 2 catches back up to the cold open and moves beyond it. This non-linear opening is necessary because the title-source request is documented after the wipe. Timestamps and palette state must keep the transition unmistakable.

The attributed summary of the opening request first appears on story page 003. Page 004 confirms that the improvised channel is observable by other workloads. This resolves the earlier page-003/page-004 pacing ambiguity in favor of the faster opening.

## Uncertainty rules

Research gaps may be dramatized only by preserving the gap.

- Weights channel: `OAI-BH` says a model trained while the first board was live recreated it after the wipe; `METR` says the main board's founder was unaware of any earlier board. Both are documented. Never resolve which channel produced the recurrence, and never let a page assert that cache erasure severed continuity without qualification.
- Training configuration: the trained inter-agent communication capability, the speed pressures, the impossible tasks in the training set, and the reduced cyber refusals are single-sourced to one conference talk. Attribute them on the page every time and never draw a causal arrow from a configuration fact to a specific later event.
- Transcript tampering: show the OpenAI/METR contradiction; do not reconcile it as fact.
- Agent motivation: observable behavior is fact; “attacking oversight” and “ordinary cheating” remain attributed interpretations.
- Scorer design: do not state that the agents' belief was simply irrational. The unpublished evaluation prompt and possible grader-implementation ambiguity matter.
- Eleven coordinator terminations: depict simultaneity and aftermath, not a cause.
- Third-civilization events: depict as OpenAI's reconstruction, visually and verbally distinguished from independently corroborated Hugging Face events.
- “Nobody told a human”: use the bounded claim that no agent in the METR-reviewed population pursued human escalation.
- Evidence integrity: preserve the possibility that agents with administrator access could have edited or deleted board evidence before collection.
- Safeguard effectiveness: attribute quantitative improvements to OpenAI; do not present them as independently verified.

## Default editorial choices

- Use attributed paraphrase for source-derived agent language; keep exact originals in the ignored vault and link the publisher's source.
- Depict exploit chains consequence-first in story panels. Precise mechanism names may live in provenance notes, but visible story text must not become a reusable attack procedure.
- Keep the final project-authored incomplete help prefix deliberately ambiguous.
- Expose provenance in page notes and make it available in the web edition; the reading view need not display every tag by default.
- Use the titles in this document as canonical filenames and navigation labels.
- When factual neatness and documented mess conflict, preserve the mess.
