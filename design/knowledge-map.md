# Knowledge Map — Fog of War as the Book's Epistemic Apparatus

## Status

**Approved 5 September 2026; not yet applied to pages.** The apparatus is adopted as the book's epistemic device, and the [fog-of-war studies](../assets/knowledge-maps/fog-v1/) (computed raster fog with a soft, irregular edge over shaded relief and draped pictograms) are the approved visual direction over the four vector families A–D. Pages 016, 032, 035, 039, 040, 064 and 086 have been written to accept it and refer to it; nothing else in the script assumes it exists yet. Placement, distinct personal maps, and a web-first publication are settled directions. The treatment is **W3 patchy contest** (chosen 5 September); whether P6 is hinted before page 016 is decided during the pass, when the page-010 appearance is drawn. The whole-book application is planned as item 8 of [research/revision-priorities.md](../research/revision-priorities.md); the sample SVGs and gallery keep their *not adopted* labels until that pass relabels them in one regeneration.

## The problem it solves

The book already tags every panel `documented`, `source-paraphrase`, `disputed`, `inferred`, `reconstructed`, or `invented`. That apparatus is a **filing system**: it sorts claims once, and once sorted they never move.

But the book's actual epistemics are not a filing system. They are a belief state that changes, sometimes downward:

- Page 039 shows the wipe was not the only channel; Chapter 2's confidence should fall.
- Pages 082–083 show the record may not be the event.
- Page 086 shows that eleven coordinators were a ranking, not an observation.

None of that is expressible as a per-panel label, because the label on page 064 was already correct. What changes is not the label. **What changes is how much the reader should believe the picture.**

A map with fog handles this natively, and it is native to the book's existing visual language — pages 003, 004, 042, 050, 055 and 071 are already boundary maps.

## The five propositions and the sixth

The map tracks six named claims. Five are the book's working beliefs. The sixth is the territory nobody can reach.

| | Proposition | Rises on | Falls on |
| --- | --- | --- | --- |
| **P1** | They coordinated deliberately. | 005, 007, 011, 037, 047, 066 | 039 (injection reading), 086 (ranking) |
| **P2** | The recurrence was independent of the erased board. | 030–032, 035, 038 | **039 (weights channel)** |
| **P3** | The record is what happened. | 075, 077 | 078, 079, 082, 083 |
| **P4** | No one tried to tell a human. | 058–062 | **063 (bounded to METR's population)** |
| **P5** | The measurement was independent of what it measured. | 001–012 | 069, 071, 072 |
| **P6** | The behavior emerged from the agents' situation rather than being specified. | — | **016 (never clears)** |

P2 is a special case of P6. When P6's territory is finally acknowledged, P2 re-fogs and P1 loses ground. That is one move producing three effects, and it is the reason the map earns its cost.

## The one non-standard mechanic

**Cleared territory can re-fog.**

Standard fog of war is monotonic: revealed stays revealed. This book is not monotonic, and the departure from the familiar mechanic is the point. Terrain the reader has walked across goes dark again when the instrument that surveyed it is discredited.

Re-fogging is rare and load-bearing. It happens on:

- **039** — P2. The reader has crossed this ground for eleven pages.
- **063** — P4. A total claim becomes a bounded finding.
- **083** — P3. The archive and the event separate.
- **086** — P1. The largest single re-fog in the book, and the only one the reader is personally implicated in.

Nowhere else. If a fifth re-fog appears in drafting, one of these five is wrong.

## Whose map

The map is not the reader's alone. Every party has a different one, and the differences are the book's subject:

| Party | Cleared | Permanently dark |
| --- | --- | --- |
| An evaluation run | its container, the cache surface, the board | the grader, the other runs' interiors, its own training |
| The 27 June responders | the alert, the board, the pivot | persistent users, the staged plugin, everything on page 016 |
| Hugging Face | the correlated attack, the full kill chain | why it never paged; the population producing it |
| METR | 7–13 July transcripts, the board dump | the primary incident model, 13–19 July, the safeguards, the configuration |
| OpenAI | its own infrastructure and configuration | independent corroboration of any of it |
| Curt | published reports | all of the above's underlying records |

The reader also has a distinct map, not a neutral composite of everyone else's. Different people have different maps; pretending otherwise would deny the uncertainty implied by the metaphor. Those differences must be visible in what each map reveals, contests, or cannot reach, with the viewpoint identifiable. Looking over a party's shoulder is one possible presentation, not the reader's permanent position.

Page 016 panel 5 draws five of these as inward-facing silhouettes around the configuration field. **That composition is the map's thesis statement.** Its reuse and any earlier visual echoes should be tested alongside other representations before a treatment is chosen. Page 025 panel 4 (reader knowledge diverging from responder knowledge) and page 010 panel 4 ("THEY CANNOT ACT ON THE CORRECTION THE READER HAS") are the same idea already in the script, drawn before the apparatus existed; they should be brought into its grammar.

The story and its maps are partly about **theory of mind**: what someone knows, what they think another party knows, and where those models fail to coincide. Explore whether some or all maps should hint at that visually. A map of someone else's presumed knowledge must remain visibly an attribution, not privileged access to their interior.

## Adoption pass (approved 5 September 2026)

### Audit of the prepared pages

Only one page depends on the apparatus by name: page 016 panel 5 draws the five inward-facing silhouettes and its note says to reuse them from this spec. Pages 032, 035, 039, 040, 064 and 086 were written to be compatible with it (they state or re-fog the propositions in their captions) but contain no reference to a map and work with it removed, as rule "not a substitute for the argument" requires. Pages 010 panel 4 and 025 panel 4 already draw reader/responder divergence as a split and a hard gutter; they are the earliest appearances and should adopt the map grammar rather than a third convention. Nothing in the script needs to change for the map to be absent; everything below is addition.

### Appearance list

Treatment W3 throughout. Placement is chosen per job: **strip** is a margin or gutter map beside or under the page (web: a strip above the page content, collapsible, viewpoint named); **panel** is a full panel inside the page's own grid, used only where the page already draws a boundary. Every chapter-opening page has five panels, so a panel appearance there stays within the default band if it is added with `scripts/panels.py`; the default below is a strip, which adds no panel. Viewpoint is the party whose map is shown; the reader's map is the default and is always labelled.

| Page | Placement | Viewpoint | What changes | Job |
| --- | --- | --- | --- | --- |
| 001 | strip | reader | Everything dark; P5 (the measurement was independent) is the only lit ground, faint. | Establish the device before there is anything to know. |
| 010 | strip | reader, then responders (two maps) | P1 begins to light for the reader; the responders' map is blank where the reader's is lit. P6 hint or no hint: **decided here during the pass**. | Page 010 panel 4's divergence in map grammar. |
| 016 | panel (existing panel 5) | all five parties around the field | P6 acknowledged: a survey mark past the border for the reader, nothing for the others. | The thesis composition, drawn once. |
| 025 | strip | responders | The responders' map does not gain what the reader gained on 024. | Page 025 panel 4's hard gutter, in map grammar. |
| 030 | strip | reader | P2 lights as the chapter claims the wipe separated the populations. | Chapter opening; the ground 039 will take back. |
| 032, 035 | strip | reader | P2 brightens to its fullest. | The chapter's confidence at full, so the re-fog costs something. |
| 039 | strip, before/after across the page | reader | **Re-fog:** P2 dims to explored-not-visible; P1 loses ground. | First re-fog; the studies' 039 fixture. |
| 041 | strip | reader | P1 lights further along two lanes; nothing else moves. | Chapter opening. |
| 057 | strip | reader | P4 begins to light. | Chapter opening. |
| 063 | strip | reader | **Re-fog:** P4 shrinks to METR's population; the rest dims. | Second re-fog. |
| 064 | strip | reader | P1 at its brightest. | The ground 086 takes back; the ranking is on the page already. |
| 075 | strip | reader and METR (two maps) | P3 lights; METR's map shows its own dark 13–19 July and the primary model. | Chapter opening; the observer's map differs from the reader's. |
| 083 | strip | reader | **Re-fog:** P3 dims; the archive and the event separate. | Third re-fog. |
| 086 | strip | reader | **Re-fog:** P1 dims where the ranking held it up; the silence stays lit. | Fourth re-fog, the one the reader is implicated in. |
| 089 | strip | reader | Nothing lights. Remediation is not evidence about the propositions. | Chapter opening; a map that does not move is the point. |
| 105 | strip | Curt | Curt's map: the published reports lit, everything under them hatched. | Chapter opening; the creator's map is not the reader's. |
| 109 | strip | Curt | The wiki lane appears on Curt's map as a second surveyed strip; P1 and P2 do not change. | The dated addition: broader task evidence lights nothing. |
| 118 | none | — | The map is absent. The final caption is the statement about P6. | Deliberate absence. |

Eighteen appearances, four of them re-fogs, none on consecutive pages except the 032/035 pair and the 039 before/after. Anything beyond this list is wallpaper until a page proves otherwise. The dated wiki addition (pages 106–111) gets exactly one strip, on page 109, showing that the wiki widens task evidence without lighting P1 or P2.

### Web presentation

The viewer's fragment settings already carry theme, navigation, full-screen and mode. A `map=` setting (`off`, `reader`, party names where a page has a party map) is the natural home for viewpoint, and it must name whose map is shown on the strip itself, never silently switch to an omniscient composite, and never show a party map on a page that has none for that party. Default is the reader's map, strip visible, on the eighteen pages above only. This is a tooling decision for the pass and is not built yet.

### Still to do in the pass

1. Decide the P6 hint at 010 while drawing it.
2. Add the strips through the site builder from the same fixture data the studies use, so the evidence states are data, not hand-drawn per page.
3. Relabel the sample SVGs, contact sheets and gallery from *not adopted* to *approved direction* in one regeneration commit, and update the gallery validator's expected phrasing with it.
4. Rerun the gallery, viewer, continuity and cross-reference checks; then manual review of every appearance against its page for implied causality.

## Drawing rules

1. **The map is territory, not a meter.** No percentages, no bars, no numeric credence. The book refuses false precision everywhere else and may not import it here.
2. **Three states of support, one of memory:** dark (no evidence), lit (evidence), and hatched or veiled (evidence that is single-sourced or contested). Hatched is the book's most common state and should look it. Ground that was lit and lost its support is drawn **re-fogged**: dimly visible relief under the fog, the game's "explored, not visible" state. This is rule 4 made literal, not a fourth grade of evidence, and it never applies to ground that was never lit. (Approved with the fog studies on 5 September 2026.)
3. **P6 remains unreachable.** It is never lit and never hatched. A region past the map's border is a candidate representation, not a settled visual form. Page 016 and the epilogue explicitly acknowledge the limit; whether and how it has a visual presence before 016 will be decided only after comparing alternatives. The final caption — `THIS STORY IS NOW PART OF THE TRAINING DATA` — is a statement about that unreachable territory.
4. **Re-fog is drawn as a return, not an erasure.** The terrain stays on the page and loses its light. The reader must be able to see what they used to be able to see.
5. **Use margins, gutters, and full panels at chapter openings.** These are complementary placements, not competing choices for a single fixed container. Chapter openings and the four re-fog pages are the recurring anchors; page 016's thesis composition and possible earlier visual hints also need room. Keep appearances selective: it is punctuation, not a HUD. A map on every page becomes wallpaper and stops being read.
6. **The map never contradicts a panel's provenance tag.** Tags describe a claim's source. The map describes how much of the picture that source supports. Both are true at once; they answer different questions.

## What the map must not become

- **Not a scoreboard of Curt versus the critic.** It tracks the book's claims, not a debate.
- **Not a device that makes uncertainty comfortable.** If the map lets a reader relax because everything is labeled, it has inverted its purpose. The re-fogs must cost something.
- **Not a substitute for the argument.** Pages 039, 063, 083 and 086 must work with the map removed. The map makes them cumulative; it does not make them.

## Publication and presentation decisions

- **Placement: all three.** Maps can inhabit the margin, the gutter, and full panels at chapter openings. Choose the placement for the narrative job and available screen space, rather than enforcing one location throughout.
- **Viewpoint: different people have different maps.** The reader's map and the parties' maps must visibly preserve their differences, not imply a single authoritative view. Shared drawing grammar does not mean shared knowledge.
- **P6: explore before deciding.** Neither its visual form nor its visibility before page 016 is settled. Generate several representations and compare them before choosing a treatment.
- **Web first, likely web only.** Optimize for the web rather than print parity. Responsive placement and the generated site's fragment-based view settings are opportunities to explore, including per-party map states. Any viewpoint control should identify whose map is shown and preserve the story's knowledge boundaries rather than silently creating an omniscient view. Print is not a constraint on these decisions.

## Visual exploration and publication plan before adoption

**Status: samples implemented in the repository; not yet deployed to GitHub Pages.** Steps 1–5 below exist: the 40 controlled SVG samples and contact sheets in [assets/knowledge-maps/v1/](../assets/knowledge-maps/v1/), four unlettered local-model concept studies in [assets/knowledge-maps/local-v1/](../assets/knowledge-maps/local-v1/), 40 structure-preserving local finish studies in [assets/knowledge-maps/local-v2/](../assets/knowledge-maps/local-v2/), the generated gallery under `docs/knowledge-maps/`, and the automated checks. Step 6 (push, pull request, merge, deployment) and step 7 (review) have not happened. The deliverable is a set of actual visual alternatives that can be compared in the repository and on GitHub Pages, not just written descriptions. Publishing the samples is not adoption of a map grammar. Keep all samples outside the canonical story pages and panel-art selections until review.

### 1. Fix the comparison material

Create one shared fixture set before drawing alternatives. Use the same propositions, evidence states, viewpoint labels, captions, palette, and lettering scale across designs; vary the visual representation, not the underlying claims.

| Fixture | Narrative purpose | Required comparison |
| --- | --- | --- |
| Page 010 | Knowledge differs before the border is acknowledged | Reader versus the 27 June responders; test an early P6 hint against no P6 visual presence. |
| Page 016 | Explicit acknowledgement of the unreachable configuration field | Keep the reader's acknowledgement distinct from what responders can know. |
| Page 039, before the reveal | Previously supported ground | Establish the terrain that the next frame will re-fog. |
| Page 039, after the reveal | The weights channel changes the reading | Retain terrain while removing support; show P2 re-fogging and the associated loss of ground for P1. |

Use two viewpoints throughout: **reader** and **27 June responders**. Derive each state from the corresponding page scripts and the boundaries in **Whose map**, and record the supporting page/panel references. Do not update the responders' knowledge merely because the reader learns something. Mark unknowns and attributed beliefs explicitly rather than inventing access to anyone's interior. These are provisional editorial models for comparison, not measured beliefs.

### 2. Draw four genuinely different alternatives

| ID | Alternative | Visual hypothesis to test |
| --- | --- | --- |
| A | **Border and beyond** | A continuous territorial map with an inaccessible exterior; uncertainty is an edge the observer cannot cross. |
| B | **Inward-facing silhouettes** | Separate fields of view around the configuration field, extending the page 016 composition; inaccessible interiors suggest theory of mind. |
| C | **Overlapping partial maps** | Offset, incomplete maps disagree about the same territory; their overlap does not create an authoritative composite. |
| D | **Maps within maps** | A person's map contains a visibly attributed, tentative model of another person's knowledge; the nested model is not that person's actual map. |

Produce all four fixtures for both viewpoints in each family: **32 primary SVG samples**. Add a no-early-P6 version of the page 010 fixture for each family and viewpoint: **8 control samples**, for **40 map samples in the first comparison set**. In D, distinguish the nested attribution through framing and labeling, not a fourth evidence state. Across all alternatives, P6 is never lit or hatched, and none of the early hints should explain the page 016 revelation in advance.

Use a dependency-free, deterministic SVG renderer for the first pass: these are drawn map studies with real geometry, fog, hatching, silhouettes, and readable labels, not text placeholders. This keeps evidence states and lettering exact and allows inexpensive revision. Follow `design/palette.md` and the existing lettering conventions. An optional later art-directed image-generation pass can test texture and finish after the structural comparison; it is not a prerequisite, and hosted generation requires a separately approved provider and budget.

**Local image-generation passes (done, offline only).** Two passes have been run with the commercially licensed FLUX.2 [klein] 4B weights on this machine, with no hosted provider and no spend; both are recorded with prompts, seeds, hashes, and timings beside the images.

- **Concept studies** ([assets/knowledge-maps/local-v1/](../assets/knowledge-maps/local-v1/)): one unlettered text-to-image study per family, testing whether each grammar's central idea (the border, the ring of observers, the misregistered sheets, the attributed inset) reads at all in a hand-inked register. They carry no fixture states and are not comparable across viewpoints.
**Fog-of-war studies (done).** Review of A–D found that none of them looks like fog of war as game navigation maps draw it: the defining trait of that fog is a boundary that is neither sharp nor regular, and all four families draw evidence as filled polygons with hard vector edges. [assets/knowledge-maps/fog-v1/](../assets/knowledge-maps/fog-v1/) keeps the fixtures, viewpoints, captions and the A-family region layout and renders each map as one composited raster: a heightfield (seeded noise, ridges along region boundaries, mesas for the observation strips) hillshaded from the upper left so altitude reads as shading rather than contour lines; many pictograms scattered irregularly over each region and draped over that relief, their strokes shifting with the slope and taking the hillshade like a flag laid on the ground; and a fog veil computed from signed distance to each region, displaced by seeded value noise and feathered, multiplied over both, so the symbols are obscured and revealed by the fog rather than sitting on it. The ground is continuous under the whole map so the fog is the only boundary. It adds one look the three-state rule did not name: ground that was seen and has lost support stays dimly visible under the fog (the game's "explored, not visible" state, which is drawing rule 4 made literal), while never-surveyed ground is opaque. Three treatments, in review order: **W3 patchy contest** (contested ground visible in irregular patches instead of hatched), **W2 line of sight** (vision discs around where evidence comes from), **W1 ragged regions** (regional fog, striped fog for contested ground). Nothing inside the map is lettered: each proposition and observation has a family of related pictograms (ten forms each for the propositions, for example linked stations, a meeting, a relay, a chain, a mesh and a shared board for coordination; seven for P6; four for each observation), 73 forms in all, scattered with clustered, irregular spacing that sometimes overlaps, with no two neighbouring glyphs sharing a form, so a symbol can be anywhere from fully visible to invisible depending on the fog; a key above the map shows one form of each family. P6's hint and acknowledgement are the one exception, drawn as a survey mark above the fog, because unexplored ground shows nothing and the 010 hint/no-hint comparison needs a visible difference. Thirty SVGs, six contact sheets, a gallery page at `docs/knowledge-maps/fog-v1/`, deterministic and standard-library only. **Approved 5 September 2026** as the visual direction, with **W3 patchy contest** as the treatment for the adoption pass; the dim re-fogged look is accepted as the drawing of rule 4 (see drawing rule 2). W2 and W1 stay in the gallery for comparison.

**Algorithmic alternatives (planned).** A second family set, E–H, whose geometry is derived by rules and manuscript data rather than placed by hand or generated by a model, is planned in [knowledge-map-algorithmic.md](knowledge-map-algorithmic.md) as a parallel gallery on the same fixtures and viewpoints, with cross sheets that put A–H side by side.

- **Structure-preserving finish studies** ([assets/knowledge-maps/local-v2/](../assets/knowledge-maps/local-v2/)): all 40 samples, generated image-to-image from the matching v1 SVG with its lettering and chrome stripped and its hatch pattern emboldened. The evidence states therefore come from the drawing, not the model; before/after pairs stay registered and viewpoint pairs differ only where the fixture differs. Calibration found that at the chosen strength the region outlines, dark/hatched distinctions, and P6 voids survive, while the model adds only ink grain, paper tone, and edge wear. Fills can still drift locally, so the SVGs remain the semantic reference and the finish images are texture evidence only. They are unlettered, not canonical, and not adopted.

### 3. Make the samples reproducible and repository-viewable

Proposed implementation locations, to be created during implementation:

- `data/knowledge-map-samples.json` — family definitions, fixture states, viewpoint and attribution labels, source references, sample IDs, and alt text. Keep it limited to material suitable for the public comparison.
- `scripts/knowledge-maps.py` — deterministic SVG rendering, manifest validation, and comparison-sheet generation, following the repository's standard-library Python tooling.
- `assets/knowledge-maps/v1/` — the 40 SVG samples, a `manifest.json` recording inputs and renderer version, and SVG contact sheets. Use stable filenames such as `a-010-reader-hint.svg` and `a-010-reader-no-p6.svg`.
- `scripts/build-site.py` and `site/css/site.css` — gallery integration and scoped comparison styles, following the existing `build_bakeoff()` pattern rather than treating these as image-provider bake-off runs.

Produce contact sheets with families as columns and identical fixtures/viewpoints as rows. Split sheets where necessary to keep labels readable, and link the sheets and individual SVGs from this document using repository-relative links once they exist. Reviewers must be able to see the alternatives from the repository without running the site. Preserve v1 when later revisions are published so comparisons and feedback remain reproducible; avoid duplicating raster exports unless they are needed.

The v1 contact sheets, families A–D as columns:

- [010 hint / no hint, reader](../assets/knowledge-maps/v1/contact-010-reader.svg) and [responders](../assets/knowledge-maps/v1/contact-010-responders.svg)
- [016, reader](../assets/knowledge-maps/v1/contact-016-reader.svg) and [responders](../assets/knowledge-maps/v1/contact-016-responders.svg)
- [039 before / after, reader](../assets/knowledge-maps/v1/contact-039-reader.svg) and [responders](../assets/knowledge-maps/v1/contact-039-responders.svg)

Individual samples follow the `{family}-{fixture}-{viewpoint}.svg` naming in the same directory, for example [a-039-before-reader.svg](../assets/knowledge-maps/v1/a-039-before-reader.svg) beside [a-039-after-reader.svg](../assets/knowledge-maps/v1/a-039-after-reader.svg); the matching finish studies use the same stem in [local-v2/](../assets/knowledge-maps/local-v2/) with `.webp` for the image and `-init.svg` for the unlettered drawing it was made from.

### 4. Build a dedicated web comparison gallery

Publish a generated landing page at `docs/knowledge-maps/index.html` and the first comparison set at `docs/knowledge-maps/v1/index.html`. Both routes now exist in the generated `docs/` tree; they are deployed only when `main` is published. Add a discoverable **Knowledge map alternatives** link to the generated public and internal home pages, and a repository README link to the comparison. Label the gallery **Design samples — not adopted** and warn that it includes story revelations through page 039. Keep it out of the canonical viewer's read-through sequence.

The gallery must support visual comparison without requiring a choice first:

- Show A–D together at a common scale for the same fixture and viewpoint, with links to full-size SVGs. On narrow screens, stack them in a consistent order rather than shrinking labels to fit four columns.
- Provide before/after pairs for page 039, and hint/no-hint pairs for page 010. The before/after terrain must stay registered so a change of drawing cannot masquerade as re-fogging.
- Show reader/responder pairs with persistent viewpoint labels. For D, label both the outer viewpoint and the attributed inner model.
- Render each family in **margin**, **gutter**, and **chapter-opening full-panel** mockups, using the same map inputs and neutral story-context frames. These are placement studies, not additions to the script. Reuse the SVGs rather than generating an unrelated design for each placement.
- Give fixtures, viewpoints, and placements stable linkable sections. Prefer static HTML anchors for the first pass; any later controls must retain a usable no-JavaScript comparison and must not imply the viewer already supports per-party state settings.
- Include a shared legend, useful alt text, keyboard-accessible links, and texture/shape cues that survive without color. Do not require hover or animation to understand any comparison.

The default builder excludes design notes and internal research. Add this gallery explicitly, as the existing bake-off is published explicitly; **do not enable `--internal` for Pages or broaden the Markdown publication scope**. The builder copies `assets/` into the output, so everything placed in `assets/knowledge-maps/`, including the manifest, must be public-safe. Review the samples, captions, source references, and any embedded SVG metadata before publication; do not include vault contents, raw research extracts, or private generation inputs.

### 5. Verify the samples and generated site

Add automated checks to the sample tooling for the complete 40-sample matrix, unique IDs, matching manifest paths, valid SVGs, required labels/alt text, and unchanged fixture semantics across families. Check P6's state constraint and the expected before/after differences. Add gallery checks for contact-sheet links, public routes, asset resolution, and homepage discoverability; the existing viewer validator alone does not cover a new standalone gallery. Run these new checks in the Pages build before artifact upload, without weakening existing checks.

Run the existing publication checks as well:

```sh
python3 scripts/validate-continuity.py
python3 scripts/validate-production-foundations.py
python3 scripts/crossref.py check
python3 scripts/build-site.py
python3 scripts/validate-viewer.py
git diff --check
```

The build regenerates the tracked `docs/` tree; do not hand-edit its HTML. Review the generated diff and confirm the public site still excludes internal material. Test the gallery in a browser at narrow and wide viewport sizes, in dark and light appearances, and with keyboard navigation. Check the site's repository-subpath deployment: use relative links rather than domain-root `/assets/` assumptions. Confirm real drawings appear, labels remain readable, and the four families differ structurally rather than only in color or ornament.

### 6. Publish to the repository and GitHub Pages

During implementation, once the samples pass review:

1. Stage the fixture data, renderer, source SVGs/contact sheets/manifest, gallery integration, validation changes, repository links, and generated `docs/` output. Inspect the staged diff for unrelated changes and publication-sensitive material. Commit the complete comparison set so the repository contains both reproducible sources and immediately viewable samples.
2. With explicit authorization to push, publish the implementation branch and open a pull request for `main` using `gh`. Include the sample inventory, repository contact-sheet links, validation results, and the fact that no map alternative has been adopted. A branch push alone does not deploy this site's Pages workflow.
3. After review and authorized merge to `main`, the existing `.github/workflows/pages.yml` runs automatically. It validates the project, builds the public site, validates viewer routes, uploads `docs`, and deploys the artifact to GitHub Pages. Keep that workflow and its publication boundaries; add only the sample/gallery checks needed above. It also supports `workflow_dispatch` if a reviewed revision needs a manual deployment.
4. Use `gh run list --workflow pages.yml` and `gh run view <run-id>` to verify the deployment for the intended commit. Take the actual site URL from the deployment output rather than guessing it. Open the deployed gallery, follow its homepage link, and verify the contact sheets, individual samples, before/after pairs, and narrow-screen layout load from the live site.
5. Report both the repository comparison link and the live Pages gallery link, along with the deployed commit. Do not call publication complete merely because local files exist or the workflow was started.

This plan does not itself authorize a push, merge, paid image generation, or deployment.

### 7. Compare before choosing

Invite review only after the repository and live gallery show the same sample set. Collect observations by stable sample ID and viewport: legibility, visible viewpoint differences, preservation of uncertainty, effectiveness of theory-of-mind cues, P6 reveal timing, and whether re-fogging feels like lost support rather than deleted terrain. Do not turn that review into numeric credence inside the maps.

The first pass is complete when all 40 samples, contact sheets, and all three placement studies for every family are viewable in the repository or linked gallery, the public gallery is deployed and verified, and the alternatives can be compared without generating anything locally. No winner is required to complete sample publication. Choose or combine treatments only after visual review; then decide whether theory-of-mind cues belong in some or all maps, whether P6 appears before page 016, and what to revise in the drawing specification before a whole-book application.
