# Page Grammar

## Script unit

The canonical writing unit is the page. Chapter files are assembly views; individual page scripts remain the source of truth for lettering, art, provenance, and continuity.

Each page script uses this shape:

```markdown
---
page: 1
chapter: prologue
sequence: 1
title: The Objective Remains
status: draft
story_time: 2026-07-08T16:00:00Z/2026-07-08T23:00:00Z
population: second
locations:
  - evaluation-container
provenance:
  - status: documented
    source: OAI-TR-X
exact_strings: []
continuity_checks:
  - no-moss-green-before-first-message
  - agent-has-no-human-form
---

# Page 001

## Page purpose

One sentence naming the causal change and intended page-turn question.

## Panel 1

**Frame:** Shot size, angle, environment, actors or system surfaces, and visible state.

**Action:** Only what changes during the panel.

**Caption:**
> Lettered text.

**Screen / system text:**
`Exact text when applicable.`

**Provenance:** `documented` — citation key and claim boundary.

**References:**
- `KEY` `locator` — 0.95 — what this reference supports in this panel.

## Page notes

- Continuity and visual-state notes.
- Disclosures for compression, reconstruction, composites, or invention.
- Optional alternates that do not change canon.
```

Omit unused dialogue categories rather than leaving empty headings.

## Page rhythm

- Default: four to six panels.
- Establishing or revelation page: one to three panels.
- Procedural sequence: five to nine panels, with repeated geometry when parallel work matters.
- Dossier/investigation page: three to six evidence blocks; it may break the normal grid but must retain a clear reading order.
- Nine-panel grids are reserved for convergence, scale, or repeated attempts.
- Splash pages are rare and reserved for a change in conceptual scope, never merely spectacle.
- No page should depend on more than two dense technical explanations. Move the rest to later pages or provenance notes.

## Page turns and spreads

Story page 1 is a right-hand recto; odd pages are recto and even pages are verso. A reveal prepared at the end of an even page lands on the odd page beside it, which the reader can already see: that is a reveal across the gutter, and it works by reading order. A reveal prepared at the end of an odd page lands on the even page behind it, which is concealed until the leaf moves: that is a turn across the leaf. Choose the device deliberately; `content/production-review.md` audits them separately. Prefer one of four reveal functions:

1. a newly discovered resource;
2. a boundary shown to be permeable;
3. an institutional decision whose consequence follows;
4. an evidence qualification that changes the meaning of the prior page.

Do not fake suspense by hiding information already known to the viewpoint.

Two-page spreads are optional and rare. They may be used for scale, convergence, or dossier structure, but may not cross a chapter boundary, place essential lettering in the gutter, or make the digital single-page reading order ambiguous.

## Panels and gutters

- Stable rectangular gutters indicate documented chronological progression.
- Wider gutters indicate elapsed time, population discontinuity, or a source gap.
- A broken or overprinted gutter may indicate disputed evidence, but never silently imply corruption.
- Reconstructed human scenes use slightly softer borders or a small provenance mark.
- Creator scenes may show annotations crossing panel borders; incident scenes may not.

## Text hierarchy

Keep these visually and typographically distinct in scripts:

- narrator captions;
- creator dialogue;
- reconstructed human dialogue;
- attributed summaries of agent reasoning;
- registered quotation and raw agent text;
- source paraphrase;
- summarized board artifacts;
- terminal output;
- provenance annotations.

Third-party strings are quoted where appropriate and registered in the page's `exact_strings` front matter with source, locator, verification and rights; the full original stays in the ignored source vault and the publisher's link. A quotation is set on the lettering layer in its registered wording, never approximated by an image model. Where the page summarises instead, the lettering must not take a shape that reads as the source's words. Quote, paraphrase or redact is decided at gate 9. Project-authored display strings may be proofread and fitted normally.

## Technical depiction

- Show the minimum interface state needed to make causality legible.
- Prefer a boundary diagram, directory tree, or before/after state over decorative terminal noise.
- Never depict all agents as a single mind, face, voice, or cursor.
- Parallel actions should retain distinct handles, timestamps, or lanes where the evidence supports them.
- Use UTC for incident timestamps. Creator scenes use local time only when dramatically necessary.

## Provenance on the page

Every factual panel receives a provenance status in the script even when the printed comic does not display the tag.

The permitted distributed-page statuses are `documented`, `raw-agent-text`, `quotation`, `source-paraphrase`, `disputed`, `inferred`, `compressed`, `reconstructed`, and `invented`. `raw-agent-text` and `quotation` say the lettering is the source's own words, so `validate-continuity.py` fails a panel declaring either unless a registered string appears in it. `raw-agent-text` is agent output as the source record preserves it — never a source author's summary of that output (reopened 12 September 2026; it had been reserved for private research).

If one panel mixes statuses, identify the boundary explicitly. A reconstructed room cannot make its dialogue documented; a documented quotation cannot make the surrounding scene observed.

## References on the panel

**Added 12 September 2026.** Every panel lists the references most relevant to that panel, each with a relevancy score. The list is the pool a rendering run draws on: a run may turn some or all of a page's references into QR codes added to the page. **Which references are used, and what each code encodes** — a publisher URL, a 256t content tag, a byte range within a vault copy — are decided later, by rendering, not in the script. The script records relevance and nothing else.

This example uses [page 045](../content/pages/045.md), panel 3, to show the form. Its scores and notes are illustrative, not a checked disposition for that panel.

```markdown
**Provenance:** `documented` — disclosure and timestamp from `OAI-TR` and `HF-TL`.

**References:**
- `OAI-TR` `§X` — 0.90 — event-table row timing the processor's disclosure.
- `HF-TL` — 0.85 — Hugging Face's own account of the same disclosure.
- `METR` — 0.45 — the investigators' line between file disclosure and code execution, which the next panel draws.
```

- **Placement.** `**References:**` is the last field in a panel, directly after `**Provenance:**`. It is direction, not lettering. Keeping it after the provenance line keeps it out of everything the tools hand to lettering and image models, which read only the fields before it or the labels they know. A grouped run (`## Panels 1–9`) carries one block for the run, as it carries one provenance line.
- **One line per reference:** the citation key in its own code span, an optional locator in a second code span, the score, and a short note saying what the reference supports *in this panel*.
- **Keys are registered keys.** Use only keys registered in `research/scene-provenance.md` or a chapter source packet — the same registry the provenance line draws on. A source worth listing that has no key gets registered first. `NONE-FICTION` and `PROJECT-INFERENCE` are not references: they name the project's own origin, not something a reader could consult. A panel with nothing to cite writes `**References:** none`.
- **What goes in.** Every registered key the provenance line cites, the source of any quotation registered for a string the panel letters, and any other registered source a reader checking this panel would want. List the most relevant, not every source that touches the scene.
- **Locators** are as precise as the source allows: a section (`§X`), a recording timestamp (`31:32`), a PDF page (`p. 14`), a corpus manifest key, or a `t256:` copy and inclusive byte range in the pointer form `AGENTS.md` describes. Keep locators in their code span. `pagelinks.py` skips code spans, but it links the words *page* plus three digits anywhere else as a story page — so write a source's page as `p. 14` in the note as well. One key may appear on several lines with different locators; two parts of one report are two references and can deserve different scores.
- **Order** the lines by score, highest first.

**The score** is a decimal from `0.00` to `1.00` with two places. It measures how directly the reference bears on what this panel shows or says. It is not the source's reliability, which the provenance status records, and not the source's importance to the book. Scores are **absolute, not normalised within a panel**: a rendering run may apply one cutoff across the whole book, so a panel whose best reference is only context does not get `1.00`.

| Score | Meaning |
| --- | --- |
| 0.90–1.00 | The controlling record for the panel's central claim, or the source of a quotation the panel letters. |
| 0.70–0.89 | Direct support for part of the panel, or independent corroboration of its central claim. |
| 0.40–0.69 | Context a reader needs to check the panel: the account it answers, the dispute it sits in. |
| 0.00–0.39 | Background. List it only when the panel has nothing stronger. |

A score is an editorial judgment, made in the script where it can be reviewed. Do not raise one so that a reference is more likely to become a code, and do not write code direction — payload, size, placement — into `**Frame:**` or `**Action:**`. A reference that a rendering run prints as a QR code is a citation in the book and passes [gate 9](../content/draft-readiness.md) like any other; a score is not a verification.

**Not yet settled or enforced (12 September 2026).** No tool reads or checks this block yet. Pages drafted before this date don't carry one; add it when drafting or revising a panel. The placeholder panels that `panels.py insert` and `pagination.py insert` write don't include one either. Where a code may sit is also open: [QR codes drawn in ants](qr-ant-codes.md) currently says a symbol never appears in a panel, gutter or margin. Codes added to story pages mean revisiting that rule, and that belongs to the later rendering decision (see its open question 6).

## Density checks

Before a page advances from `draft` to `review`:

- no more than roughly 180 lettered words without a deliberate dossier-page exception;
- no balloon or caption carries two separate argumentative jobs;
- every panel changes knowledge, access, authority, system state, or interpretation;
- project-authored display strings have a human-proofreading entry;
- the final panel earns its page turn;
- the page remains understandable with provenance notes hidden.
