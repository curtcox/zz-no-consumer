# The Two Anthill Problem — implementation plan

Status: planned; no title, narrative, artwork, or viewer changes implemented.
Requested by Curt on 8 September 2026.

## Intended result

Rename the book **The Two Anthill Problem** across the graphic novel, novella,
appendix, and published presentation. Introduce ants selectively within panel
images, and compose ant trails through the gaps between panels so the page reads
as a traversable environment. Use the existing fog-of-war images as the anthills
between which the ants travel.

This is a coordinated editorial and visual change. The trails and anthills must
remain legible as a metaphor while preserving the book’s documentary boundaries.

## Decisions to resolve

Questions sent to Curt while preparing this plan:

1. What do the two anthills represent: a recurring visual motif retaining distinct
   observer viewpoints, humans and AI agents, or two specific agent populations?
   Record the answer before assigning hill identities or drawing connecting routes.
   The existing story has more than two populations and more than two viewpoints;
   the new title does not by itself establish which pair is intended.
2. Should travel be suggested by static poses and trails, or should ants actually
   move in the web edition? Static composition is the proposed starting point;
   animation, if requested, must also have a complete static presentation.

Other implementation defaults: web-first graphic-novel treatment; sparse,
naturalistic ant silhouettes consistent with the surrounding artwork; no added
dialogue or anthropomorphic ant characters; novella changes only where needed
for the rename or for fidelity to a changed story event. These are proposals,
not recorded user decisions.

## Existing foundations and constraints

- Read [the story contract](../content/story-contract.md),
  [visual continuity](visual-continuity.md), and
  [the quotation audit](../research/exact-text-permissions-audit.md) before
  editing narrative claims or source-derived lettering.
- [The knowledge-map specification](knowledge-map.md) adopts W3 “patchy
  contest,” distinct observer maps, selective appearances, retained terrain
  under re-fogging, and unreachable P6. Build from that direction and
  `data/knowledge-map-samples.json` / `scripts/knowledge_maps_fog.py`.
  The apparatus is specified but not yet applied throughout the story.
- Reconcile the appearance list against current scripts and page identities
  before using it as production data. Its prose contains historical counts and
  chapter-opening descriptions; derive current structure with the tools.
- Ant movement must not silently clear fog, grant one party another’s knowledge,
  establish consciousness, or imply an undocumented transfer between populations.
  In particular, the wiki population has no established bridge to Artifactory.
  An ambiguous connection should be redesigned or explicitly handled as authored
  metaphor, never treated as incident evidence.
- Preserve the deliberate final map absence unless an explicit editorial revision
  changes it. Do not turn selective map appearances into a map on every page.
- Page and panel identities remain stable. If a later design requires insertion,
  use `pagination.py` or `panels.py`, including their parity and rhythm checks.
  Any new page/panel-keyed records must join those tools’ rewrite coverage.
- `docs/` is generated. Scripts remain standard-library-only. Preserve existing
  art versions and append-only generation receipts.

## Work sequence

### 1. Establish the visual meaning and a small pilot

- [ ] Record Curt’s answers above and define what an ant, an anthill, and a trail
  mean. Distinguish ants physically present in a scene from ants drawn as an
  authored visual overlay. Decide how two recurring hill identities coexist with
  the existing multiple observer maps; do not collapse viewpoints by convenience.
- [ ] Write the adopted rules into the knowledge-map and visual-continuity
  specifications. Revise the story contract deliberately if the metaphor changes
  its assumptions.
- [ ] Make a compact comparison using an ordinary panel page, an existing
  reader/responder divergence, and a before/after re-fog. Include a narrow-screen
  version. Show actual fog-map terrain serving as the hills, connected by ants
  through panel gaps; generic mound icons alone do not fulfill the request.
- [ ] Compare ant size, density, edge crossings, hill entrances, and trail contrast.
  Verify the trails guide reading order without suggesting unsupported causality.
  Review a concrete pilot before applying its treatment throughout the book.

Deliverable: reviewed pilot assets and a short visual specification with recorded
hill identities, ant treatment, permitted connections, and motion decision.

### 2. Rename the book comprehensively

- [ ] Inventory `ZZ: NO CONSUMER`, `NO CONSUMER`, case variants, and the repository
  slug in editable source trees. Classify each occurrence as current book branding,
  historical/source language, or a technical address before replacing anything.
- [ ] Update current title headings, cover/title-page directions and lettering,
  novella counterparts, credits, introductory copy, and production documents.
  Inspect the title lettering in `content/pages/012.md` and its prose counterpart.
- [ ] Update title output in `scripts/build-site.py`, including the viewer masthead
  and `NOVELLA_TITLE`, plus `scripts/make-thumbnails.py` and any other title emitters.
  Use a shared title source where multiple outputs would otherwise drift.
- [ ] Cover browser titles, navigation, landing pages, text/HTML downloads, and
  EPUB metadata and visible title pages. Check narrow mastheads for the longer name.
- [ ] Preserve source-derived incident language and historical records. Keep the
  repository slug, existing URLs, stable routes, and download addresses unless a
  separate migration is intended; changing the book title does not require moving
  the repository. Inspect references to the old title’s origin for editorial repair.

Deliverable: the new title on all current reader-facing title surfaces, with any
remaining old-title occurrences explicitly accounted for.

### 3. Add ants within appropriate panel images

- [ ] Audit canonical scripts and selected art by panel key. Produce a placement
  list recording the visual reason, physical-versus-metaphorical treatment,
  proposed entry/exit points, and any script/prose implications for each candidate.
  Record intentional exclusions rather than adding ants indiscriminately.
- [ ] Favor scenes where scale, ground, boundaries, networks, or collective work
  support the motif. Keep ants clear of evidence, faces, captions, and diagrams
  whose meaning an added mark could change.
- [ ] Update scene directions, storyboard records and prompts together. Preserve
  provenance status for the underlying event and disclose invented visual treatment
  in the appropriate notes. Mirror actual story changes in novella prose.
- [ ] Follow [the storyboard workflow](storyboard-workflow.md) for SVG scene work
  and [the artwork queue workflow](artwork-automation.md) for generated panel edits.
  Inspect queue status and resume existing jobs. For raster edits, inspect the
  current image first and use the image-generation workflow during implementation.
- [ ] Import candidates as new versions, review their actual appearance, and select
  accepted art through `panelart.py`. Check lettering and crops after selection.

Deliverable: a reviewed, selective set of ant-bearing panel images with reproducible
placement records, provenance, and retained previous versions.

### 4. Build the inter-panel ant layer

- [ ] Inspect the image-page composition in `scripts/build-site.py`,
  `scripts/panel_layout.py`, and `site/viewer/viewer.css` / `viewer.js` before
  choosing the overlay boundary. Keep margin art distinct from selected panel art.
- [ ] Create reusable SVG ant poses and deterministic route geometry. Store routes
  against stable panel/page identities and edge anchors, not fixed viewport pixels.
  Reuse existing parsers and layout information rather than adding duplicate models.
- [ ] Compose trails in the actual gaps between panels and outer margins, with
  plausible transitions to chosen panel edges and hill entrances. Protect lettering,
  panel controls, keyboard focus, and reading order; decorative overlays should not
  intercept clicks or create screen-reader noise.
- [ ] Provide deliberate layouts for wide grids and narrow stacked panels. Routes
  must adapt or select a prepared narrow layout rather than cut across panel images
  after reflow. Handle absent art, alternate images, and text-only views gracefully.
- [ ] If animation is selected, make it subtle, honor reduced-motion preferences,
  provide a stop/off control, and preserve the route’s meaning without animation.
  Static output must remain useful with JavaScript disabled.

Deliverable: ants visibly inhabiting the cracks between panels at supported sizes,
with no obscured text, inaccessible controls, or accidental factual connections.

### 5. Integrate fog-map anthills

- [ ] Extend the approved fog-map renderer/composition to make the maps function
  visually as anthills. Preserve terrain registration, proposition states,
  observation islands, legends, and visible viewpoint labels.
- [ ] Keep map state driven by evidence data. Ant positions, counts, routes, and
  animation must not act as an undeclared confidence score or reveal mechanism.
- [ ] Implement reviewed appearances through the builder from validated state and
  placement records. Use existing map placements where suitable; reconcile the
  earlier collapsible-strip proposal with the new connected-gutter composition.
- [ ] Provide descriptive alternatives for meaningful hill/route relationships;
  individual decorative ants can remain hidden from assistive technology.
- [ ] Regenerate affected study assets and gallery labels when adoption actually
  occurs, retaining prior study versions for comparison. Make map hiding or viewpoint
  changes remove/re-route dependent ants without dangling trails or false connections.

Deliverable: the fog images themselves read as the ants’ destinations while still
communicating whose knowledge is shown and what remains uncertain.

### 6. Validate, rebuild, and review

- [ ] Before implementation, run the relevant existing checks and record findings.
  Use `pagination.py report` for current page counts. Resolve failing checks rather
  than accepting them as a permanent baseline.
- [ ] Add focused checks for new placement records: valid keys and assets, valid
  route endpoints, supported viewpoints, preserved P6 and re-fog semantics, and
  deterministic generation. Extend existing `check` tooling; add no dependencies.
- [ ] Run the full local CI sequence in [AGENTS.md](../AGENTS.md), including the site
  rebuild, both identity checks, strict cross-references and novella checks, artwork
  and lettering checks, knowledge-map checks, and built-site/link validators.
  Run `pagelinks.py link --apply` for new plain page references in content.
- [ ] Review every changed image and map appearance. Exercise the graphic-novel
  viewer at wide and narrow widths, both themes, image/text modes, keyboard use,
  map settings if implemented, and reduced motion if animated. Verify the GitHub
  Pages repository-subpath URLs and downloads.
- [ ] Inspect source and generated changes with
  `git --no-optional-locks -c diff.autoRefreshIndex=false diff --stat` and the same
  safe command with `--check`; review affected files and account for EPUB timestamp
  changes. Coordinate any index writes separately.

Completion means all four requested changes are visible in the rebuilt edition,
the title is consistent across editions, the ant routes work at supported layouts,
the maps retain their evidence boundaries, and validation findings are resolved.
Report changed sources, reviewed examples, check results, and any remaining decisions.
Publishing follows the repository’s existing GitHub Pages workflow when requested.

## Scope of this planning task

This file is the deliverable for the current request. Implementation checkboxes
remain unchecked intentionally. No artwork generation, source rename, site rebuild,
commit, or publication is performed just by creating this plan.
