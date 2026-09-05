# Knowledge Map — Algorithmic Alternatives

## Status

**Plan, not implemented.** Nothing in this document exists in the repository yet. It extends the comparison in [knowledge-map.md](knowledge-map.md) with a second family set whose geometry is produced by rules and data rather than by hand-placed coordinates or an image model. Publishing the samples is not adoption of a map grammar. All drawing rules, propositions, fixtures, and viewpoints in [knowledge-map.md](knowledge-map.md) apply unchanged.

## Why a third kind of drawing

The comparison so far has two kinds of picture:

| Set | Where the geometry comes from | What it can tell us |
| --- | --- | --- |
| v1 A–D | Fixed polygons an author placed by hand in `scripts/knowledge_maps.py` | Whether a grammar (border, ring, sheets, inset) carries the six propositions and two viewpoints legibly |
| local-v1 / local-v2 | A diffusion model, unconstrained or constrained by the v1 geometry | Whether hand-inked texture and finish help or hurt, given a fixed structure |

Neither answers a question the book's method raises: **could the map be derived rather than drawn?** The book's apparatus is a rule system (tags, sources, boundaries). A map whose terrain is computed from that rule system, deterministically, would stay honest as the script changes, could not be quietly tuned to flatter a claim, and would make the four re-fog pages consequences of a rule rather than editorial decisions about a drawing. Whether such maps are also *legible* is the thing to test. That is the purpose of this set.

The hypothesis is not that algorithmic maps win. It is that four structurally different derivations, placed beside A–D on identical rows, will show which properties of a knowledge map come from grammar and which from authorship.

## The four algorithmic families

Families keep the fixture matrix of v1 and take the next letters so the two sets can share contact sheets and anchors. Each family answers one of the four generation questions chosen for this study.

| ID | Family | Generation | Visual hypothesis to test |
| --- | --- | --- | --- |
| **E** | **Grown terrain** | Seeded procedural terrain | A noise field partitioned by six seeds grows coastlines and contours that no one drew; fog is a fill on grown regions. Does terrain that looks found rather than made change how uncertainty reads? |
| **F** | **Manuscript terrain** | Data-driven from the page scripts | Each proposition's territory is assembled from cells, one per page that bears on it, laid in reading order and textured by that page's provenance tags. Does tying terrain to the actual manuscript make the map feel like evidence rather than illustration? |
| **G** | **Access graph** | Graph and force layout | Propositions, observations, and parties are nodes; evidence and access are edges; a deterministic force layout places them. Fog is the part of the graph a viewpoint cannot traverse. Does a graph make theory of mind visible better than territory does? |
| **H** | **Surveyed fog** | Fog as a simulated process | Light propagates over a cell grid from observation sources page by page, blocked by access boundaries. The map at a fixture is the state of that process. Does a frontier that visibly advanced and then withdrew make re-fogging feel like lost support rather than a redrawn picture? |

### E · Grown terrain

- A value-noise field on a lattice, seeded from a fixed integer recorded in the data file, interpolated with a smoothstep; no external noise library.
- Six seed points partition the field by nearest-seed distance weighted by the noise, giving irregular regions with shared coastlines. P1's foothold is the outer band of P1's region where the noise exceeds a threshold, so it is a real sub-territory, not a stripe.
- Contours come from marching squares at three thresholds and are drawn on every fixture regardless of state; they are the retained terrain that re-fogging must leave in place.
- P6's seed lies outside a survey radius. Inside the radius the field is drawn; outside it nothing is drawn but the P6 coastline, so the region is present as an edge and never as a fill. In the no-hint control the radius clips the coastline as well.
- The seed is per family, never per fixture or viewpoint, so all ten samples share identical terrain.

### F · Manuscript terrain

- Inputs are the page scripts as read by `scripts/crossref.py`: page order, each panel's provenance statuses, and the propositions' page references in `data/knowledge-map-samples.json` and the rises/falls table in [knowledge-map.md](knowledge-map.md).
- A proposition's territory is a chain of equal-sized cells, one per referenced page, laid along a path through the map in reading order. Cells are unlabeled. Their ornament (contour density, stipple, a small glyph) is derived from the page's dominant provenance tag; their **fill is the fixture state and nothing else**. A page that has not yet been reached at the fixture point is drawn as a cell outline only.
- Observations become cells on the same paths at the pages that establish them. P6's path exists (pages 016 and 039 reference it) but its cells are never filled and the path leaves the drawn area.
- The number of cells is visible. This is the family's risk under drawing rule 1: cell count could read as a score. The mitigation is that cells are equal, unnumbered, and the same across viewpoints; the review must decide whether that is enough or whether F is disqualified by the rule.

### G · Access graph

- Nodes: P1–P6, the four observations, and the six parties in **Whose map**. Edges: a proposition to the pages that raise or lower it, an observation to the propositions it bears on, a party to what its map clears. Edge attributes carry single-sourced or contested, which draws hatched.
- Layout is a fixed-iteration force simulation with a recorded seed and integer arithmetic where possible, so the result is identical on every machine. Positions are computed once per family and reused for every fixture.
- A viewpoint's map is the subgraph reachable from that party's node without crossing an access boundary. Unreachable nodes and edges are drawn dark and unlabeled. P6 has no traversable edge from any party, so it is always beyond a cut, drawn as a node with severed edge stubs.
- Re-fog: an edge that was reachable and is discredited loses its ink and becomes a dashed ghost with its endpoints still placed. Terrain is the layout; the layout never changes.

### H · Surveyed fog

- A cell grid (about 96 × 64) over a fixed proposition layout borrowed from E's partition so the two are comparable. Observation sources sit at fixed cells; access boundaries are impassable cell walls derived from **Whose map**.
- Light propagates from a source by breadth-first flooding limited to a radius that depends on the fixture's page reach, with hatched light when the source is single-sourced or contested. The simulation runs page by page up to the fixture page for that viewpoint; the 27 June responders' run stops at their boundary and never advances.
- The fixture states are authoritative. The process decides only the **frontier shape** inside a region and the marks left behind: cells that were lit and are now dark keep a survey outline. A check asserts that the aggregate state of every region equals the fixture state; if the rule cannot reproduce a fixture, the rule is wrong, not the fixture.
- P6's cells are walled on every side. No flood reaches them. In the no-hint control the wall is not drawn.

## What every family must share

These are the conditions that make the eight families comparable and keep the algorithmic set inside the book's rules.

1. **Same inputs.** Fixture states, viewpoints, captions, source labels, alt-text template, and the P6 presence values come verbatim from `data/knowledge-map-samples.json`. No family may add a state model.
2. **Same chrome.** The header, caption bar, source line, and legend are rendered by the v1 frame code, imported rather than copied, so only the map layer differs.
3. **Three states, one texture each.** Dark, lit, hatched, with the v1 fills and hatch pattern. Algorithms may vary shape, density, and ornament; they may not introduce gradients of light, partial fills, or a fourth treatment for attribution.
4. **P6 never lit or hatched**, in every family, every fixture, every viewpoint, enforced by the check.
5. **Registration.** Within a family, the retained terrain layer is byte-identical across all ten samples. The check compares the layer, not the whole SVG, so re-fogging can be verified as a change of fill only.
6. **No meters.** Nothing may encode evidence quantity as size, length, brightness, or number. Family F is the explicit test case; the review decides whether equal unnumbered cells pass.
7. **Determinism.** Regenerating from the same inputs produces the same bytes on any machine: seeded stdlib `random`, no floating-point accumulation whose rounding differs across platforms in the layout loops, and a recorded seed and iteration count in the manifest.
8. **Stdlib only, static SVG.** Same tooling boundary as v1; no numpy, no animation. Animated transitions are a possible later web pass and are out of scope here.

## Implementation

Proposed locations, to be created during implementation:

- `data/knowledge-map-algorithmic.json` — family definitions for E–H, seeds, iteration counts, grid sizes, radii, the party and edge tables for G and H, and the page-reference tables F needs that are not already in `data/knowledge-map-samples.json`. Public-safe; no vault material.
- `scripts/knowledge_maps_algo.py` — stdlib renderer with `generate`, `check`, and `test`, importing the fixture loader, state helpers, frame, legend, and hatch pattern from `scripts/knowledge_maps.py`. Value noise, marching squares, nearest-seed partition, force layout, and grid flooding live here as small pure functions with unit tests on tiny inputs.
- `assets/knowledge-maps/algo-v1/` — 40 SVGs named `e-010-reader-hint.svg` through `h-039-after-responders.svg`, a `manifest.json` recording inputs, seeds, renderer version, and the sha256 of every v1 sample embedded in cross sheets, and contact sheets: six per-viewpoint sheets with E–H as columns (as v1), plus six **cross sheets** with A–H as eight columns for the same rows.
- `scripts/build-site.py` — a `docs/knowledge-maps/algo-v1/` page built by the same function as v1, parametrized by version folder and family set, with the same sections: all families per row, 039 before/after, 010 hint/no hint, reader/responders, placement mocks reusing fixture 016, contact sheets, and a **Beside v1** section that shows the cross sheets. The landing page gains a second card and jump links, and each v1 row links to its algorithmic counterpart and back.
- `scripts/validate-knowledge-map-gallery.py` — generalized to validate both version folders and the cross-links between them; the local-v1 and local-v2 checks stay attached to v1 only.
- `.github/workflows/pages.yml` — one added step, `python scripts/knowledge_maps_algo.py check`, before the site build.

Sequence:

1. Data file and the shared helper import in `knowledge_maps.py` (expose the frame and legend as functions if they are not already), with a check that the v1 output is byte-identical afterwards.
2. Family E, since H borrows its partition; then H; then G; then F, which needs the crossref model.
3. Contact and cross sheets, manifest, checks, and tests.
4. Gallery page, validator, workflow step, README and [knowledge-map.md](knowledge-map.md) links.
5. Full validation, browser check at narrow and wide widths, commit.

Rough scale: four renderers of 150–300 lines each, one data file, and gallery changes that mostly reuse v1 code. No image model, no spend, no new dependency.

## Verification

Automated, added to the algorithmic tooling and run in the Pages build:

- 40 samples, unique IDs, E–H × five fixtures × two viewpoints, manifest paths present, valid SVG with viewBox, title, desc, and metadata.
- Fixture semantics unchanged: the `data-state` of every proposition region, foothold, and observation equals the fixture state from the shared data file.
- P6 constraint: no P6 element ever carries `lit` or `hatched`; no-hint controls contain no P6 element.
- Registration: the retained-terrain layer is identical across a family's ten samples; the 039 before/after pair differs only in fill attributes.
- No numerals in any map-layer `<text>` other than proposition labels; no `stop`, `linearGradient`, or opacity below 1 in the map layer.
- Determinism: a second generate run in the check reproduces the manifest hash.
- Family H: the simulated aggregate equals the fixture for every region, or the check fails.
- Gallery: routes, links, anchors, cross-sheet links in both directions, alt text, homepage discovery.

Manual, at review:

- Legibility of each family at contact-sheet scale and at margin size.
- Whether E's found-looking terrain, F's manuscript cells, G's cut edges, and H's withdrawn frontier each make re-fogging read as lost support.
- Whether F survives drawing rule 1, and whether G's parties make theory of mind clearer than B's silhouettes or D's inset.
- Whether any derived family is more convincing than A–D or only more defensible, and which properties of the better hand-drawn families could be adopted by a derived one.

## Publication

Same path as v1: commit sources, samples, sheets, gallery integration, and the regenerated `docs/` tree together; push, pull request, merge, and deployment happen only with explicit authorization, through the existing Pages workflow. Report the repository cross-sheet links and the live gallery link with the deployed commit. No winner is required; the set is complete when all 40 algorithmic samples, the twelve sheets, and the parallel gallery are viewable in the repository and linked from the landing page.

## Decisions taken in this plan

- Family letters E–H continue the v1 series so anchors, sheets, and review notes can address all eight families uniformly.
- H reuses E's partition rather than growing its own, to keep the process comparison about the frontier rather than the terrain.
- The manuscript-derived family F uses page references and provenance tags only; it does not read research files or the vault.
- Animated before/after transitions and a local-model finish pass over the algorithmic set are deferred until the structural comparison has been reviewed.
