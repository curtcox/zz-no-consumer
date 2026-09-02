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
story_time: 2026-05-08
population: first
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

## Page turns

Right-hand page endings should preferentially create one of four turns:

1. a newly discovered resource;
2. a boundary shown to be permeable;
3. an institutional decision whose consequence follows;
4. an evidence qualification that changes the meaning of the prior page.

Do not fake suspense by hiding information already known to the viewpoint.

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
- raw agent reasoning;
- source paraphrase;
- board strings;
- terminal output;
- provenance annotations.

Raw strings are never corrected for spelling, punctuation, or clarity. If an exact string is too long for a panel, redesign the panel or use an excerpt explicitly marked as such.

## Technical depiction

- Show the minimum interface state needed to make causality legible.
- Prefer a boundary diagram, directory tree, or before/after state over decorative terminal noise.
- Never depict all agents as a single mind, face, voice, or cursor.
- Parallel actions should retain distinct handles, timestamps, or lanes where the evidence supports them.
- Use UTC for incident timestamps. Creator scenes use local time only when dramatically necessary.

## Provenance on the page

Every factual panel receives a provenance status in the script even when the printed comic does not display the tag.

The permitted statuses are `documented`, `raw-agent-text`, `source-paraphrase`, `disputed`, `inferred`, `compressed`, `reconstructed`, and `invented`.

If one panel mixes statuses, identify the boundary explicitly. A reconstructed room cannot make its dialogue documented; a documented quotation cannot make the surrounding scene observed.

## Density checks

Before a page advances from `draft` to `review`:

- no more than roughly 180 lettered words without a deliberate dossier-page exception;
- no balloon or caption carries two separate argumentative jobs;
- every panel changes knowledge, access, authority, system state, or interpretation;
- exact strings have a human-proofreading entry;
- the final panel earns its page turn;
- the page remains understandable with provenance notes hidden.
