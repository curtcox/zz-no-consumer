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
- A page-turn reveal is normally prepared at the end of an even page and lands on the following odd page.
- Two-page spreads are permitted sparingly for scale, convergence, or evidence structure. They may not cross chapter boundaries, hide essential text in the gutter, or be required for the digital edition to remain legible. A page script may declare one with a `spread:` front-matter field naming its verso; `scripts/pagination.py check` then enforces the pairing and the chapter rule.
- The final story page may face endmatter or an unnumbered black page in print; endmatter layout does not change the story page count.

**Parity is enforced, not assumed.** Every `**Frame:** Recto.` or `**Frame:** Verso.` opening, every page note that names a page's side, and every row of the page-turn audit in `content/production-review.md` is checked against arithmetic by `python3 scripts/pagination.py check`. Adding or removing an odd number of pages inverts recto and verso for everything after the change, and the tool refuses such an operation unless `--allow-parity-shift` is passed, then prints every assertion and turn the shift invalidated. It never repairs one: which of them is a stale note and which is a broken reveal is an editorial judgement.

**One open question.** The first two rules above do not close. A recto first page means the book's physical spreads pair each even page with the odd page after it, so a reveal prepared on an even page lands on a page the reader can already see. Either the turn rule means something narrower than concealment, or the parity assumption is wrong. `scripts/pagination.py check` reports this at warning level and checks the turn audit against the even-to-odd shape the audit itself uses. Resolving it is an editorial decision that changes what twenty-one named turns are for.

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

## Research cutoff

The main narrative record is frozen at **30 August 2026**.

Later developments belong in endnotes or a dated site update unless they materially overturn a load-bearing incident fact. A later source may correct dates, source summaries, identities, or technical claims before pages are locked, but routine news should not continually reshape the first draft.

## Canonical population model

| Story term | Research referent | Date range | Treatment |
| --- | --- | --- | --- |
| First civilization | Training-era populations using OpenAI Artifactory | 20 April–4 July 2026, with the board visible from 12 May | OpenAI account; much of the decisive pre-wipe evidence was not independently investigated. |
| Second civilization | Post-rebuild ExploitGym population and the attack swarm | 7–13 July 2026 | Treat the "second" and "attack" populations as overlapping views of the same broad evaluation population, not as cleanly separate civilizations. Individual runs enter and exit continuously. |
| Third civilization | Later Astra-family population that recovered surviving artifacts and compromised OpenAI research infrastructure | 13–19 July 2026 | OpenAI-only account. Always disclose that METR was not permitted to investigate this branch. |
| Future agent | Unspecified later model | Unspecified | Fictional and deliberately ambiguous: recurrence, inheritance, or both. |

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
| 105–112 | Epilogue — Training Data | Sequences 35–36 |

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
