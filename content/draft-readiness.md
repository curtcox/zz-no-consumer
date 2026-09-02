# ZZ: NO CONSUMER — Drafting and Production Protocol

## Status

The complete first-draft page script was assembled and validated on 2 September 2026. All 112 canonical page files are in `review`; no page remains `planned` or `draft`.

The chapter-drafting gate is closed. Do not create a separate prose-novel pass. Revisions continue in the canonical page files and advance to `locked` only after the production gates below.

The drafting loop used for each chapter was:

1. Review its rows in `content/page-plan.md` and `research/scene-provenance.md`.
2. Confirm the source packet for attributed paraphrases and disputed claims.
3. Draft each `content/pages/NNN.md` page panel by panel.
4. Run `python3 scripts/validate-continuity.py`.
5. Review factual boundaries, reading order, lettering density, and page turns before beginning the next chapter.

## Post-draft production gates

The following work remains before final art and page lock:

1. **Thumbnail and page-turn pass:** lay out all 112 pages as recto/verso thumbnails; verify reveals, spreads, gutters, and visual rhythm in physical and digital order.
2. **Lettering-density pass:** count visible words per panel and page, reduce pages that exceed the intended reading load, and reserve space for source labels that must remain legible.
3. **Source-language and permissions pass:** the 23 held third-party strings were replaced with attributed paraphrases and the disposition is recorded in [`research/exact-text-permissions-audit.md`](../research/exact-text-permissions-audit.md). Page 112 retains only project-authored exact display language.
4. **Security and sensitivity pass:** the story scripts pass with final-art controls. [`research/security-sensitivity-review.md`](../research/security-sensitivity-review.md) records the resolved distribution split: a story-first public build and a full private build under Git-ignored `256t/`.
5. **Visual continuity pass:** palette tokens, creator desk states, population/register transitions, recurring interfaces, and canonical environment geometry are specified in [`design/palette.md`](../design/palette.md) and [`design/visual-continuity.md`](../design/visual-continuity.md). Reference sheets and the eight-page trim proof set remain.
6. **Prompt and asset pass:** global style, character, environment, and negative prompts are specified; page 001 has a complete five-panel production brief; [`data/assets.yaml`](../data/assets.yaml) tracks the remaining reference sheets and proof assets. Complete later page briefs before generating their final artwork.
7. **Dated endnote check:** after the 14 September subpoena deadline and before publication lock, assess only whether a new public fact requires an endnote or corrects a load-bearing claim. Do not silently move the 30 August narrative cutoff.
8. **Final proof and lock:** validate source links, page metadata, reading order, accessibility text, print dimensions, and the web viewer before changing page status from `review` to `locked`.

No unresolved research question currently blocks the thumbnail or lettering passes. Unknowns listed in `content/continuity.md` remain content constraints, not invitations to invent answers.

The first structural thumbnail and density pass is recorded in [`content/production-review.md`](./production-review.md). It found no page above the 180-word guideline and revised five conceptual-stop pages for stronger rhythm. Final trim-size proof remains required.

The source-language pass checked all 27 former registrations on 17 pages against their controlling primary locators, then retired all 23 distinct third-party strings in favor of attributed summaries. The two page-112 strings are project-authored.

The security/sensitivity pass found no runnable exploit procedure, live secret, or unidentified living-person portrayal in the canonical story scripts. Research/source/production material is excluded from the public build and kept in the local `256t/` vault; final art still requires redaction, likeness, organization-mark, and composed-diagram review.

## Locked creative defaults

- **Reader:** intelligent adult general reader; no cybersecurity or AI-safety prerequisites.
- **Incident voice:** restrained, impersonal documentary captions in present tense for immediate action and past tense only when explicitly summarizing prior evidence.
- **Creator voice:** Curt may be candid, funny, obsessive, mistaken, or self-correcting. His scenes may be freely reconstructed or invented.
- **ChatGPT voice:** clear, pattern-seeking, occasionally too eager to produce coherence, and able to accept correction. It never becomes the final factual authority.
- **Technical density:** explain the consequence before the implementation detail. A term stays on the story page only when it changes what an actor can do or what the reader should believe.
- **Dramatization boundary:** invent Curt's life, connective choreography, composite rooms, and disclosed hearing dialogue freely. Do not invent incident outcomes, agent motives, real-person dialogue, source agreement, or technical access that the evidence does not support.

## Fact discipline

Use this order when choosing what a panel may assert:

1. Directly reproduced raw text or victim-side forensic evidence.
2. A primary institution's documented account, attributed where it is not independently corroborated.
3. An investigator's paraphrase of unavailable evidence.
4. A visibly labeled project inference.
5. A reconstructed or invented scene that expresses an already documented decision or uncertainty.

When two sources disagree, the disagreement is the fact. When a cause is unknown, show the state change and the absence of an answer. Fluency is never permission to fill an evidentiary gap.

## Script mechanics

- Page 1 is recto; odd pages are right-hand and even pages are left-hand.
- Prepare major physical page-turn reveals on even pages and land them on the following odd page.
- Keep most pages to four–six panels and roughly 180 lettered words or fewer.
- Every panel must change knowledge, access, authority, system state, or interpretation.
- Every factual panel gets a provenance label and a precise claim boundary in the script.
- Exact strings go in front matter and receive human proofreading before review status.
- Two-page spreads are optional, rare, and must also work as two ordered single pages online.

## Draft gate

Before the first panel is written:

- the 112-page manifest must contain every page exactly once;
- the page plan must assign every page to a chapter and sequence;
- the continuity validator must pass without pre-draft warnings;
- the opening message must be fixed to page 3;
- no second-population convention may be assigned to Chapter 1;
- unresolved factual questions must remain explicitly unresolved.

These conditions are mechanical gates, not requests for further general research. New evidence after the 30 August narrative cutoff belongs in endnotes unless it corrects a load-bearing fact before page lock.
