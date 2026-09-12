# The Two Anthill Problem — Drafting and Production Protocol

## Status

The complete first-draft page script was assembled and validated on 2 September 2026, at 112 pages. It has changed since: the dated wiki addition of 5 September and that day's read-through pass both moved the count, which is derived from `data/pages.yaml` and reported by `python3 scripts/pagination.py report` rather than restated here. Every page file is in `review` except the eight pages added on 5–6 September, which remain in `draft` pending the beat and thumbnail test.

The chapter-drafting gate is closed. The novella is now drafted in `content/novella/`; keep each prose page aligned with its canonical script. Revisions continue in the canonical page files and advance to `locked` only after the production gates below.

The drafting loop used for each chapter was:

1. Review its rows in `content/page-plan.md` and `research/scene-provenance.md`.
2. Confirm the source packet for attributed paraphrases and disputed claims.
3. Draft each `content/pages/NNN.md` page panel by panel.
4. Run `python3 scripts/validate-continuity.py`.
5. Review factual boundaries, reading order, lettering density, and page turns before beginning the next chapter.

## Post-draft production gates

The following work remains before final art and page lock:

1. **Thumbnail and page-turn pass:** lay out every page as recto/verso thumbnails; verify reveals, spreads, gutters, and visual rhythm in physical and digital order.
2. **Lettering-density pass:** count visible words per panel and page, reduce pages that exceed the intended reading load, and reserve space for source labels that must remain legible.
3. **Source-language and permissions pass:** the 23 held third-party strings were replaced with attributed paraphrases and the disposition is recorded in [`research/exact-text-permissions-audit.md`](../research/exact-text-permissions-audit.md). [Page 118](pages/118.md) retains only project-authored exact display language. **Revised 12 September 2026:** that pass applied its remedy early, and the working default is now the opposite — **stay as close to the ground truth as possible while drafting, use direct quotation wherever it is appropriate, and decide quotation against paraphrase against redaction at gate 9, immediately before lock.** A transformation applied during drafting cannot be reviewed later, because the thing it would be reviewed against is gone. This gate's completed disposition stands as a record of what was decided on 2 September; it is no longer the rule for new material.
4. **Security and sensitivity pass:** the story scripts pass with final-art controls. [`research/security-sensitivity-review.md`](../research/security-sensitivity-review.md) records the resolved distribution split: a story-first public build and a full private build under Git-ignored `256t/`.
5. **Visual continuity pass:** palette tokens, creator desk states, population/register transitions, recurring interfaces, and canonical environment geometry are specified in [`design/palette.md`](../design/palette.md) and [`design/visual-continuity.md`](../design/visual-continuity.md). Reference sheets and the eight-page trim proof set remain.
6. **Prompt and asset pass:** global style, character, environment, and negative prompts are specified; [page 001](pages/001.md) has a complete five-panel production brief; [`data/assets.yaml`](../data/assets.yaml) tracks the remaining reference sheets and proof assets. Complete later page briefs before generating their final artwork.
7. **Dated endnote check:** after the 14 September subpoena deadline and before publication lock, assess only whether a new public fact requires an endnote or corrects a load-bearing claim. Preserve the dated-scene and later-admission rules in the story contract; 30 August is the aftermath scene date, not a research cutoff.
8. **Final proof and lock:** validate source links, page metadata, reading order, accessibility text, print dimensions, and the web viewer before changing page status from `review` to `locked`. **No page locks before gate 9 passes.**
9. **Quote and citation verification, immediately before publication:** every direct quotation and every citation in the book, checked one at a time against its source. Two separate questions per item — *does the source exist and resolve*, and *does it say what we claim it says* — and for a quotation a third: *is the wording exactly right, and is what we call it what it is.* Each item leaves this gate with a disposition: **quote as it stands**, **paraphrase**, or **redact**. A quotation may not pass on the strength of having been checked earlier: an edit to our own asserting text invalidates the check without touching the source. A panel reference that a rendering run prints as a QR code is a citation in the book: its source must resolve and its locator must say what the reference's note claims. Its relevancy score is an editorial judgment, not a verification. The programme, the register, and the tooling proposal are in [`tasks/citation-verification.md`](../tasks/citation-verification.md); it runs at lock and again immediately before each target ships, because [Part B](./publication-plan.md) ships six targets from one locked tree and a quotation cleared for one is cleared for all of them only if the tree has not moved.

No unresolved research question currently blocks the thumbnail or lettering passes. Unknowns listed in `content/continuity.md` remain content constraints, not invitations to invent answers.

The first structural thumbnail and density pass is recorded in [`content/production-review.md`](./production-review.md). It found no page above the 180-word guideline and revised five conceptual-stop pages for stronger rhythm. Final trim-size proof remains required.

The source-language pass checked all 27 former registrations on 17 pages against their controlling primary locators, then retired all 23 distinct third-party strings in favor of attributed summaries. The two [page-118](pages/118.md) strings are project-authored.

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
- Prepare major physical page-turn reveals on even pages and land them on the following odd page. See the open question about these two rules in `content/story-contract.md`; `python3 scripts/pagination.py check` reports it and checks the audit against the even-to-odd shape.
- Do not state a page's own parity in new prose. Existing recto/verso lines are maintained assertions and are verified on every run; new pages should let the tool derive the side.
- Keep most pages to four–six panels and roughly 180 lettered words or fewer.
- Every panel must change knowledge, access, authority, system state, or interpretation.
- Every factual panel gets a provenance label and a precise claim boundary in the script.
- Every panel lists the references most relevant to it, each with a relevancy score from `0.00` to `1.00`, in a `**References:**` block after its provenance line. A rendering run may turn some or all of them into QR codes added to the page. Which references it uses, and what each code encodes, are decided later. The form, the scoring bands, and what is still open are in [`design/page-grammar.md`](../design/page-grammar.md#references-on-the-panel).
- Exact strings go in front matter and receive human proofreading before review status.
- Two-page spreads are optional, rare, and must also work as two ordered single pages online. Declare one with a `spread:` front-matter field naming its verso so the pairing and the chapter rule are checked.
- Add, remove, and move pages with `scripts/pagination.py`, never by hand. It owns every place a page number lives, refuses parity-inverting operations unless they are asked for, and prints the assertions and turns each operation invalidated.

## Draft gate

Before the first panel is written:

- the page manifest must contain every page exactly once, and its `story_pages` field must agree with the row count;
- `python3 scripts/pagination.py check` must pass;
- the page plan must assign every page to a chapter and sequence;
- the continuity validator must pass without pre-draft warnings;
- the opening message must be fixed to [page 003](pages/003.md);
- no second-population convention may be assigned to Chapter 1;
- unresolved factual questions must remain explicitly unresolved.

These conditions are mechanical gates, not requests for further general research. New evidence dated after the 30 August aftermath scenes enters by recorded admission in the story contract's log, as a dated frame or endnote, unless it corrects a load-bearing fact before page lock.
