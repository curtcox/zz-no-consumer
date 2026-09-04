# Task — Make page insertion and deletion cheap

## The ask

Right now, adding or removing a story page is expensive enough that it distorts editorial decisions. In the 3 September revision, a page that should have been inserted into Chapter 1 was instead folded into an existing page **specifically to avoid renumbering**. That is the tail wagging the dog. The book is a draft; pages should be addable and removable on editorial grounds alone.

Build the tooling that makes that true. Then prove it by inserting a page, deleting a page, and moving a page, with every validator green and no prose damaged.

**Do not assume the obvious solution is the right one.** Stable identifiers with numbers generated at output time is one candidate. It does not solve the hardest part of this problem (see "The trap"). Evaluate it against the alternatives and justify whatever you pick.

## Where the numbers actually live

Measured against the current tree — verify these counts before trusting them, they will drift:

| Location | Form | Count |
| --- | --- | --- |
| `content/pages/NNN.md` | filename | 112 |
| page front matter | `page: N` | 112 |
| **prose inside page scripts** | `page 003`, `pages 019–021`, `page 047` | **103 references, 66 distinct targets** |
| `data/pages.yaml` | `{id: "041", …}` | 112 |
| `data/chapters.yaml` | `first_page` / `last_page` | 8 chapters |
| `data/panel-art.tsv` | panel key `NNN-II` | 24 rows (bakeoff art) |
| `data/panel-types.tsv` | panel key `NNN-II` | 547 rows, generated |
| `assets/art/panels/NNN-II/` | directory path | final-art destination |
| `docs/viewer/pages/NNN/images/II/` | route | ~1,335 routes, generated |
| `content/page-plan.md` | beat-sheet table rows | 112 |
| `content/story-contract.md` | canonical chapter/page map | 8 rows |
| `content/chapters/*.md` | `**Pages:** 16–29` | 8 files |
| `research/scene-provenance.md` | `Target pages` column | 39 sequences |
| `research/chapter-source-packets/*.md` | "supports story pages 016–029" | 8 files |
| Other prose | `continuity.md`, `story-outline.md`, `production-review.md`, `draft-readiness.md`, `security-sensitivity-review.md`, `exact-text-permissions-audit.md`, `draft-source-notes.md`, `follow-up-research.md`, `training-configuration.md` | 22 files total outside `content/pages/` |

Generated artifacts (`docs/`, `panel-types.tsv`) are not the problem; they rebuild. The problem is the hand-written references, and above all the 103 in prose.

## The trap

**Auto-generated page numbers do not solve this problem, and an implementer who stops there will ship something that quietly breaks the book.**

Story page 1 is a right-hand recto. Odd pages are recto, even pages are verso. The script depends on this *semantically*, not just typographically:

- **25 pages assert their own parity in prose.** 16 say "is verso," 9 say "Recto reveal" or equivalent. 52 pages contain parity or page-turn language.
- Page-turn reveals are deliberately prepared at the end of an even page and land on the following odd page. `content/production-review.md` audits all 55 even-to-odd turns and names 19 load-bearing ones (`002 → 003`, `008 → 009`, `012 → 013`, `038 → 039`, `085 → 086`, …).
- Two-page spreads may not cross chapter boundaries, and the book has 57 physical spreads.
- Page notes encode intent that becomes false under parity inversion. Example, from `content/pages/002.md`: *"Page 002 is verso. Its final line prepares the resource discovery on recto page 003."*

**Inserting an odd number of pages anywhere inverts recto/verso for every page after it.** Renumbering the *references* correctly still leaves you with 25 false parity claims and a broken turn choreography. This is the actual reason insertion is scary, and it is the part the tooling has to earn its keep on.

Ways to attack it, none obviously right:

- Make the **spread** (a verso/recto pair) the atomic editorial unit, so insertions are always even.
- Allow odd insertions but have the tooling **detect and report** every invalidated parity assertion and page turn, as a work list rather than a silent break.
- Introduce explicit **flex pages** that may absorb a parity shift.
- Stop hard-coding parity in prose and derive it, so notes read "this page is verso" only in generated output.
- Some combination. Sequences (39 of them, 1–4 pages each) are an existing structural spine and may be the better unit than the page.

## Invariants the tooling must preserve

1. Every validator green: `validate-continuity.py`, `validate-production-foundations.py`, `crossref.py check`, `validate-viewer.py`. Baseline for `crossref.py check --strict` is 71 findings; do not increase it.
2. Chapter boundaries and sequence membership stay editorially chosen, never silently rebalanced by a script.
3. Prose cross-references stay correct and stay *readable* — a reference must not degrade into an opaque token in the human-editable source unless the tooling can round-trip it.
4. Panel identity survives. Existing art in `data/panel-art.tsv` and `assets/art/panels/` must keep pointing at the right panel, or be migrated with an auditable mapping.
5. `data/pages.yaml` titles and `content/pages/*.md` titles stay in sync (the continuity validator enforces this).
6. Provenance and citation-key joins in `crossref.py` keep resolving.
7. The 112-page count is **not** an invariant. It is arbitrary and the contract should stop implying otherwise.

## Deliverables

1. **A short design note** — the approach you chose, the alternatives you rejected, and specifically how you handle parity. Put it in `design/` or `tasks/`. Write this before writing code; if the design note does not have a convincing answer to "The trap," stop and reconsider.
2. **The tooling**, following the conventions already in `scripts/`: pure Python 3, no new dependencies, deterministic output, a `--check` mode that exits non-zero. Study `scripts/crossref.py` and `scripts/validate-continuity.py` first; they already model the page graph and you should extend rather than duplicate.
3. **A migration** of the existing tree, if your approach requires one, in a single reviewable commit separate from the tooling commit.
4. **Updates to the affected planning documents** so they describe the new reality: `content/story-contract.md` (the "Canonical chapter and page map" and "Physical page assumptions" sections both assert things your change may falsify), `README.md`, and `content/draft-readiness.md`.

## Acceptance tests

Demonstrate all four, from a clean tree, with every validator green afterward and a readable diff:

- **Insert** a page mid-Chapter 3.
- **Delete** a page mid-Chapter 5.
- **Move** a page from the end of Chapter 1 to the start of Chapter 2.
- **Insert two pages** at a chapter boundary, the case most likely to break spread and turn rules.

For each, the tooling must report — not silently fix — every parity assertion and page-turn note that the operation invalidated. A tool that renumbers cleanly and says nothing about the choreography has failed the task.

## Non-goals

- Do not change any page's editorial content. This is infrastructure. If a page's prose is wrong after a test operation, report it; do not rewrite it.
- Do not redesign the provenance, citation-key, or viewer-route systems. They work.
- Do not add a database, a build framework, or a dependency. The repo's tooling is deliberately dependency-free and pure Python, and `scripts/textimage.py` goes to some lengths to stay that way.
- Do not touch `256t/`.

## Context worth reading first

- `README.md` — repository map and the full script/validator inventory.
- `content/story-contract.md` — "Form and length," "Physical page assumptions," "Canonical chapter and page map."
- `content/production-review.md` — the page-turn audit and spread measurements. Currently flagged stale; the turn table is still the best statement of what the choreography is protecting.
- `design/page-script-template.md` — canonical page shape.
- `scripts/crossref.py` — the existing model of the page/provenance/sequence graph.
