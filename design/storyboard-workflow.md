# Storyboard workflow

The first pass is local, deterministic SVG. Scene records let the editor or assistant
change framing, silhouettes, props, and lettering space without calling an image model.
Cloud generation is a later escalation for compositions that cannot be finished well
enough locally. The pilot is a small set of representative panels, not whole-book coverage.

## Inner loop

1. Read the panel script and its neighbors. The script and story contract remain authoritative.
2. Edit `data/storyboards.json`. Each key is an existing panel identity; never renumber it
   by hand. `pagination.py` and `panels.py` move or delete these records in their plans.
3. Run `python3 scripts/storyboards.py generate`. Only changed scenes acquire another
   immutable SVG version in the existing panel art store. An unchanged run adds nothing.
4. Run `python3 scripts/storyboards.py check` and `python3 scripts/build-site.py`.
5. Open `/storyboards/` in the built site. Compare layout boxes, clean storyboard,
   lettering, and the current book selection. Toggle lettering zones and focal points;
   inspect the complete neighboring pages in their physical recto/verso pairing.
6. Refine the composition before spending time on a richer image. Keep earlier attempts.

For a standalone preview: `python3 scripts/storyboards.py gallery --output /tmp/storyboards`.
The workshop exports clean SVG references and JSON scene records. It works without a
model, credentials, package installation, or network access. SVG source generation is
byte-identical for identical inputs; font rasterization can differ between browsers.

## Scene records

- `source`: the canonical panel body captured when its composition was reviewed. If the
  script changes, the checker requires another review. After reviewing the change, copy
  the current body from the shared `panels` parser into this field; never dismiss drift
  merely by refreshing the snapshot.
- `shot`, `title`, `intent`: the shot description and the visual decision being tested.
  Shot is descriptive; geometry comes from the boxes, not from an implicit camera model.
- `background`: a named palette color.
- `nodes`: back-to-front drawing order. Every node names an asset, a palette color, and
  a normalized `[x, y, width, height]` box. Optional `flip` mirrors a pose; `label` is
  controlled project-authored graphic text; `focus` protects the subject from lettering.
- `lettering`: explicit normalized boxes for the fields the existing lettering convention
  cannot place, in their script order. Dialogue retains its speaker and mixed case and
  uses a provisional rectangular treatment. These are blocking positions, not final balloons.
- `reconstructed`: broken outer border for reconstructed scenes. Internal scene/evidence
  boundaries can use the separate reconstructed-box asset.

`data/storyboard-assets.json` contains project-authored SVG primitives on a 100×100 local
coordinate system. Their `currentColor` is supplied by the scene. The initial vocabulary
includes rooms, racks, monitors, desks, cards, hands, silhouettes, and diagram elements.
Human shapes are blocking figures, not approved likenesses. Add reusable geometry here;
do not ask a model to rediscover the same desk or camera framing each time.

Focal boxes and lettering must not overlap. The checker also checks missing panels,
invalid geometry, stale source snapshots, truncated/missing lettering, current generated
assets, version selection, backward-compatible art records, and the production skip rule.

## Stages and selection

`data/panel-art.tsv` now has a `stage` column, independent of candidate/chosen/rejected:
`layout`, `storyboard`, `refined`, `final`. Existing raster candidates default to refined;
this does not approve them. The storyboard renderer registers its SVGs as storyboard.

An explicit chosen version wins. Otherwise the most mature non-rejected candidate wins,
with the newest version breaking ties within that stage. Thus a fresh storyboard cannot
silently replace a refined image. The existing viewer keeps alternate versions available.

Use `python3 scripts/panelart.py stage PANEL VARIANT final` to change maturity and the
existing `choose`, `reject`, or `clear` commands to curate. Rebuild after selection changes.
Stage changes alone do not override a chosen version.

`produce.py` looks for non-rejected refined/final artwork when deciding what to skip.
A layout or storyboard, even a chosen one, does not satisfy that requirement. As before,
use `--force` to request another version when refined artwork already exists.

## Refinement handoff

The clean SVG excludes the lettering overlay and review guides. Its metadata preserves
the source script, composition, used asset definitions, palette, and renderer version.
Send a rasterized copy to image-conditioning runners that require PNG/WebP; SVG itself
is not universally accepted as model input. The dependency-free renderer intentionally
does not install a rasterizer. The existing letterpress raster-flatten command explains
this boundary instead of silently losing SVG artwork.

For local or cloud refinement, preserve the clean board, source version, reference images,
model revision, prompt, seed, dimensions, and control settings alongside the new output.
Use reference-image or edge/depth/pose conditioning only where the chosen runner supports
it. The current production runner remains prompt-based; this pilot does not add a cloud
client or automatically submit references. Import richer results into the existing version
store and compare them against the board before selecting them.

The next expansion is broader scene coverage and assets based on what the pilot reveals.
Use 3D blocking only for shots whose perspective or posing is awkward in the 2D vocabulary.
