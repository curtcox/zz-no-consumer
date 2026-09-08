# Storyboard workflow

The first pass is local, deterministic SVG. Scene records let the editor or assistant
change framing, silhouettes, props, and lettering space without calling an image model.
Cloud generation is a later escalation for compositions that cannot be finished well
enough locally. The scene set now covers every reader image slot. These are storyboard-stage placeholders,
with richer candidates retained wherever they already exist.

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
- `lettering_mode`: omit for the original slot convention, or use `manual` to place every
  canonical field in script order. Each lettering box then corresponds to one field,
  including captions and system text. A box may use `role: plain` and `max_size` for
  unboxed title or ending text; ordinary dialogue keeps its speaker header.
- `label_box`: optional node-level box for wrapped graphic labels; `label_size` caps its
  font size. The checker measures fit and clearance from canonical lettering.
- `border`: use `none` only for scripted borderless black fields.
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

The most mature non-rejected version wins. Within that stage, an explicit chosen
version wins, then the newest version breaks ties. Thus a fresh storyboard cannot
silently replace a refined image. The existing viewer keeps alternate versions available.

Use `python3 scripts/panelart.py stage PANEL VARIANT final` to change maturity and the
existing `choose`, `reject`, or `clear` commands to curate. Rebuild after selection changes.
A more mature version supersedes a chosen version at an earlier stage.

`produce.py` looks for non-rejected refined/final artwork when deciding what to skip.
A layout or storyboard, even a chosen one, does not satisfy that requirement. As before,
use `--force` to request another version when refined artwork already exists.

## Refinement handoff

For built-in image-tool work, use the [scripted queue](artwork-automation.md) to
prepare reference packages, save outputs without changing reader selection, render
review sheets, and promote accepted candidates. The manual import recipe below
remains available for other workflows.

The clean SVG excludes the lettering overlay and review guides. Its metadata preserves
the source script, composition, used asset definitions, palette, and renderer version.
Send a rasterized copy to image-conditioning runners that require PNG/WebP; SVG itself
is not universally accepted as model input. The dependency-free renderer intentionally
does not install a rasterizer. The existing letterpress raster-flatten command explains
this boundary instead of silently losing SVG artwork.

For local or cloud refinement, preserve the clean board, source version, reference images,
model revision, prompt, seed, dimensions, and control settings alongside the new output.
Use reference-image or edge/depth/pose conditioning only where the chosen runner supports
it. The current production runner remains prompt-based; this workflow does not add a cloud
client or automatically submit references. Import richer results into the existing version
store and compare them against the board before selecting them.

The next pass refines individual compositions and reusable assets based on visual review.
Use 3D blocking only for shots whose perspective or posing is awkward in the 2D vocabulary.

## First run and outputs

Run from the repository root. For the existing scenes, this is the complete offline path:

```sh
git --no-optional-locks status --short
python3 scripts/storyboards.py generate
python3 scripts/storyboards.py check --complete
python3 scripts/build-site.py
python3 scripts/storyboards.py check --complete --built
python3 scripts/validate-viewer.py
python3 scripts/pagelinks.py check --built
python3 -m http.server 8000 --directory docs --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/storyboards/`; stop the server with Ctrl-C when finished.
The ordinary reader is at `/viewer/`. If the port is occupied, choose another port;
if binding is denied by the environment, use its normal permission mechanism.

| Output | Owner and lifetime |
| --- | --- |
| `docs/assets/placeholders/` | Builder-generated text fallback for every reader image slot, including those without a scene record |
| `assets/art/panels/NNN-II/vNN-storyboard-svg.svg` | Immutable clean board written by `storyboards.py generate` through `panelart.store()` |
| `data/panel-art.tsv` | Refreshed by generation or `panelart.py scan`; carries stage and curation |
| `docs/storyboards/` | Rebuilt workshop: four SVG previews and a JSON export per scene, plus the gallery and spread thumbnails |
| `docs/assets/lettered/` | Builder-generated selected artwork with the controlled lettering overlay |
| `256t/storyboards/` | Default standalone gallery output; ignored, disposable, and regenerated by `gallery` |

`generate` processes all scene records; it has no per-panel selector. It validates them
before writing. Byte-identical existing boards are reused, even if that version has been
rejected: generation does not reverse curation. Changing a used asset can affect several
scenes; changing the palette or renderer metadata can create versions across the scene set.
Layout boxes are a review mode, not automatically registered layout-stage variants.
The builder does not generate missing stored storyboards; run `generate` first.

`gallery` writes previews from the current scene records without registering versions and
without running validation first. Use it for a fast visual experiment, then validate and
generate before publication. `check --built` always checks `docs/storyboards/`; it does
not validate an arbitrary `--output` directory. Preview generation overwrites derived
files; it never overwrites the immutable versions in the art store.

## Add a composition for an existing panel

Choose an existing reader slot from `storyboards.source_bodies()` and confirm it is also
in `textimage.book_scripts()`. Grouped script runs occupy one reader slot containing the
whole grid, not an independently generated image for every numbered cell. Their source
snapshot includes the complete canonical grouped script, including provenance and notes. Compose the entire grid explicitly; the
tool does not infer geometry or expand grouped runs.

The following is a construction recipe, not a scene to apply unchanged. Replace `NNN-II`
with the existing key, read its source, and design the nodes before writing. This adds a
composition; it does not create or renumber a story panel.

```python
import sys
sys.path.insert(0, "scripts")
import storyboards

panel = "NNN-II"  # Replace with an existing, reviewed reader slot.
data = storyboards.load()
source = storyboards.source_bodies()[panel]
assert panel not in data["scenes"], "Edit the existing scene instead of replacing it."
scene = {
    "title": "Short composition name",
    "intent": "The visual decision this preview will test",
    "shot": "wide",
    "source": source,
    "background": "ink",
    "reconstructed": True,  # Set according to the script's treatment.
    "nodes": [
        {"asset": "monitor", "box": [0.35, 0.35, 0.30, 0.35],
         "color": "steel", "focus": True}
    ],
    "lettering": []  # Supply boxes for any unplaced fields before generation.
}
# After composing and reviewing this scene:
data["scenes"][panel] = scene
storyboards.DATA.write_text(storyboards.encoded(data), encoding="utf-8")
```

Coordinates start at the upper-left. For example, `[0.35, 0.35, 0.30, 0.35]` places
an object 35% across and 35% down, with 30% panel width and 35% panel height. These are
bounding boxes, not perspective-aware cameras or pose joints. Changing `shot` alone does
not reframe anything; edit the boxes, node order, asset, or `flip`.

To discover which lettering needs explicit placement, call `letterpress.layout_panel`
with `textimage.lettering_fields(page_id).get(index, [])`, `letterpress.load_slots()`,
and `*textimage.PANEL_SIZE`. Its second return value lists unplaced `(field, text)` pairs.
Create one `lettering` box per unplaced pair, in that order. Do not duplicate text in the
scene: the lettering layer reads the canonical script. Focal protection checks node
boxes against lettering boxes; it does not detect every collision involving decorative
nodes, labels below boxes, or art generated later. Visual inspection remains necessary.

## How the assistant should iterate

Work one visual question at a time: framing, subject placement, reading order, contrast,
then detail. Write the intended improvement in `intent`, change the relevant geometry,
and compare the resulting board with the prior version. Reuse asset definitions for
recurring props and poses. If natural-language feedback is used, translate it into saved
scene edits; there is no model call inside the deterministic render loop.

Before promoting a composition, inspect:

- The panel alone: the intended action and focal subject read at thumbnail size.
- The lettered view: captions and dialogue are complete and subjects remain visible.
- The neighboring panels: recurring props, screen positions, and action direction agree.
- The spread: ordering and recto/verso pairing support the intended reveal. Workshop
  spreads use a provisional two-column grid, not the script's final panel dimensions.
- The source boundary: diagrams do not add unsupported causal links, agents acquire no
  bodies, and reconstructed human scenes do not become apparent documentary evidence.

Keep a successful board when extra detail does not improve understanding. Diagrams and
interfaces can remain controlled graphics in final art; every panel need not pass through
an image model. A new candidate is not automatically an improvement.

## Local refinement and cloud escalation

After a board is useful, inspect the available local runners and plan a small run:

```sh
python3 scripts/localgen.py doctor
python3 scripts/produce.py plan --slot NNN-II
python3 scripts/produce.py run --slot NNN-II --takes 1
```

Replace `NNN-II` with the target slot. The last command performs generation and can take
time; the first two inspect readiness and cost estimates. Use `--provider MODEL_ID` to
select a configured runner and `--seed NUMBER` to record a repeatable starting point.
Use `--force` on `run` when another refined/final candidate already exists; it appends a
version. The plan can also take `--force` to explain that work before running it.

This runner composes a text prompt from the canonical material. It does **not** consume
the storyboard automatically. For image-conditioned refinement, use a separately
configured local runner that accepts reference images. If local output cannot adequately
preserve identity, pose, composition, or required detail, escalate that selected panel to
a cloud service with appropriate reference/editing support. Do not send the whole book
merely because one panel needs escalation.

Prepare a handoff containing the clean board, reviewed scene JSON, desired dimensions,
character/prop references, and a short instruction specifying what must stay fixed and
what may change. Convert SVG to PNG/WebP with an available external renderer when needed,
verify the aspect ratio and absence of lettering/guides, and keep the conversion settings.
The exported SVG still contains controlled graphic labels such as diagram node names;
“clean” means no lettering overlay or review guides, not necessarily no visible text.

Retain the exact output and reference files. Record provider/model revision, prompt,
seed if supported, dimensions, steps/sampler/strength or other available controls,
reference hashes, and generation time. A seed alone does not guarantee identical output
across model revisions, runners, hardware, or hosted service changes. Existing local
production runs log themselves; do not hand-edit `data/generation-log.jsonl` for an
external import.

## Import an externally generated candidate

There is no `panelart.py import` command. Use its existing Python store API, then scan.
Run this only after downloading the intended image and recording its generation settings.
Replace both placeholders; the guard checks that the target is a real reader slot.

```python
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
import panelart
import textimage

panel = "NNN-II"
image = Path("/absolute/path/to/downloaded-candidate.webp")
slots = {f"{s.id}-{p.index:02d}" for s in textimage.book_scripts() for p in s.panels}
assert panel in slots
assert image.suffix.lower() in (".webp", ".png", ".jpg", ".jpeg")
stored = panelart.store(panel, image.read_bytes(), image.suffix.lower(),
                        provider="external-import")
rows, _, _ = panelart.scan()
panelart.write_table(rows)
print(stored)
```

Verify the downloaded file's actual image format before importing; the store is not a
format converter. Use a simple provider slug if replacing `external-import`. Store the
provenance/settings in a uniquely named JSON sidecar beside the new image, using its
returned basename; never overwrite another version's metadata. Such a sidecar is a
manual record, not a new tool-managed schema. It travels with the panel directory during
renumbering, but its contents are not rewritten or validated. Prefer reference hashes and
variant basenames over embedded panel paths; any historical identifiers remain historical.

Importing defaults to candidate/refined. It may therefore become the displayed image if
there is no chosen version. To hold the display steady while experimenting, explicitly
choose the current version first. Imported images do not inherit storyboard geometry;
inspect their lettering and composition again.

## Choose, reject, restore, and finish

Replace `NNN-II` and `vNN` with the key and version shown by `list`:

```sh
python3 scripts/panelart.py list --panel NNN-II
python3 scripts/panelart.py choose NNN-II vNN --note "Composition reviewed in sequence"
python3 scripts/panelart.py reject NNN-II vNN --note "State the specific defect"
python3 scripts/panelart.py clear NNN-II vNN
python3 scripts/panelart.py stage NNN-II vNN final
```

These are alternative actions, not a batch to execute on the same version. `choose`
replaces the prior choice; `reject` keeps the file but excludes it; `clear` returns it to
candidate status without changing its stage. To restore an earlier image, choose it by
version, then rebuild. To return to automatic selection, clear the chosen version.
Marking a candidate final increases its fallback priority, so do that only after review;
marking it final still does not override a different explicitly chosen version.

Finish with the first-run check/build sequence above, inspect the reader, and review
`git --no-optional-locks diff --stat` plus the affected source and generated files. Include
the scene/library changes, new immutable assets, curated table, and builder output in the
same commit when committing the work. Coordinate Git writers as described in the README.

## Troubleshooting and limitations

| Symptom | Next action |
| --- | --- |
| `script changed` | Compare the captured `source` with the current panel, revise the composition, then refresh only that reviewed source snapshot and generate |
| `current board missing` | Run `generate`; a site build or gallery alone does not register boards |
| Focal subject overlaps lettering | Move/resize the subject or the explicit lettering box; do not simply remove `focus` to silence the check |
| Missing/truncated lettering | Supply the missing boxes or enlarge/reposition them; edit canonical wording only as an editorial decision |
| New board does not appear in reader | Check `list`: a chosen or more mature variant takes precedence; inspect the workshop's current-selection mode |
| Rejected board is not recreated | Identical bytes are reused; explicitly clear its rejection if wanted again, or change the composition |
| Local production skips a panel | It already has non-rejected refined/final art; use `--force` for another candidate |
| Old export files remain in standalone gallery | Use a fresh disposable output directory; the standalone command does not clean obsolete exports |
| Board changes after renumbering | Identity tools move records/assets, but changed source snapshots may require a new generated version; run `generate`, checks, and rebuild |

Use `check --complete` to require a scene for every current reader slot; ordinary `check`
also supports partial scene sets during editing. It does not infer
scenes, judge visual quality, implement drag editing or 3D posing, register layout-mode
exports, rasterize SVG, or orchestrate cloud reference uploads. Those are explicit later
extensions. Final lettering remains a separate craft pass; provisional rectangular
speech treatments are not finished balloons.
