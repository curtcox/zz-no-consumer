# Panel geometry and artwork fit

`data/panel-layouts.json` is the shared page geometry. Its templates map the number
of reader slots to ordered `[x, y, width, height]` rectangles within a 2800×4000
page. These are reader slots, including grouped script runs, not new panel IDs.
Templates have no page keys to renumber. A new slot count must have an explicit
template; unsupported counts, fractional coordinates, overlaps and out-of-page
rectangles are errors.

The initial templates preserve the existing 3:2 compositions. Odd counts use a
wide first row, with a taller first image, followed by pairs. Even counts use
pairs. Groups are vertically centered on the page. This intentionally replaces
the provisional equal-height grid: crops of several existing illustrations would
remove embedded labels. No existing artwork was cropped, stretched or replaced.
Page margins and gutters are outside image rectangles; they are not letterboxing.

`panel_layout.size(page, index)` derives an exact-ratio production canvas from
the rectangle, at least 1200 pixels wide. The raster minimum is half that canvas
in both dimensions. It is a publication floor, not a claim of print readiness.
The browser uses the same rectangles as percentages, so responsive display does
not change a panel's proportions. Page size also comes from this file.

## Production

The placeholder generator, storyboard renderer, letterpress, local display and
site builder share the target geometry. Lettering is laid out on the target
canvas after image fitting. `produce.py` requests the target size for each slot;
explicit width and height overrides must preserve that ratio and meet the
resolution floor. The artwork queue snapshots target dimensions, includes them
in prompts and rejects received or promoted PNGs with an incompatible ratio or
insufficient resolution. Older queue snapshots remain compatible only when their
entire original snapshot still matches and the target remains 1200×800.

When a model cannot emit the exact target size, generate a larger composition
that protects the intended crop area. Keep that output. Review the source and
crop together, checking essential subjects, embedded labels, neighboring panels,
and space reserved for lettering. Do not approve a crop merely because its
numbers pass. The existing `image_crop.py inspect` workflow helps detect borders
and text baked into raster artwork; geometry checks cannot distinguish deliberate
flat backgrounds from unwanted bands inside an image.

For a reviewed source in the artwork store:

```sh
python3 scripts/panel_layout.py fit 001-01 assets/art/panels/001-01/SOURCE.png \
  --box LEFT TOP RIGHT BOTTOM --note "Describe the reviewed framing and label clearance"
python3 scripts/panelart.py choose 001-01 VERSION
```

Use actual source and version names. The fit tool saves a new SVG derivative with
the original bytes embedded losslessly, an explicit crop viewport and a JSON
receipt containing the source path, SHA-256, crop, target size and review note.
It does not crop the lettering layer. Raster crops cannot fall below the
publication resolution floor. The existing PNG crop tool remains available when
a raster derivative is needed. Neither route calls a model.

Selection rejects incompatible dimensions. The builder checks every selected
source **before replacing its output directory**. A matching outer canvas alone
does not establish visual quality; embedded borders and meaningful crop contents
remain review responsibilities.

## Verification

```sh
python3 scripts/panel_layout.py check
python3 scripts/storyboards.py check --complete
python3 scripts/letterpress.py audit
python3 scripts/build-site.py
python3 scripts/panel_layout.py check --built
```

The first check includes offline regression fixtures. The built check also
compares published image proportions, page aspect ratios and every rendered
panel's declared position against the shared geometry. CI runs both checks.
For browser inspection, `window.auditPanelFit()` reports missing images and
rendered aspect differences greater than half a CSS pixel. It never repairs a
mismatch. Hidden image views are skipped until displayed.

Changing a template can require new artwork or reviewed crops. Update the layout,
render and review the affected storyboards, fit the selected artwork, run the
lettering audit, then rebuild. The build fails closed while any selected image
still has the old proportions.

## Compatibility and visible-panel regression checks

Positioned pages declare `data-panel-layout="2"`. CSS applies absolute positioning
only to that version. Unversioned markup from an older server retains a grid
fallback, so its images cannot all occupy the same location. The fallback may
letterbox: it preserves readability until the old server is restarted.

The local server snapshots its UI assets alongside its loaded code. API responses
and response headers identify the running build and layout version. Changing code,
UI assets or panel geometry marks the session as requiring a restart; new page and
panel rendering returns HTTP 409. Existing displayed pages remain readable. After
a restart, a connected client with a different build asks for a reload. Published
viewer asset URLs include content hashes to avoid stale CSS/JavaScript caches.

The shared browser audit checks panel count, image loading, dimensions, coordinates,
page containment, ancestor clipping, overlapping rectangles and sampled occlusion.
Local art views run it after images load and display an error on a failed check.
The static viewer exposes the same `window.auditPanelFit()` for browser checks.
Run the audit on an image view; deliberately hidden image views are not a pass.

`panel_browser_checks.py write --out /tmp/panel-check.html` creates a standalone
browser regression page using the actual renderer and local/static stylesheets.
It exercises each currently used layout at mobile and desktop widths, local
left/right/spread modes, old markup with new CSS, and deliberately broken fixtures.
The report must prove both that good cases pass and that the bad cases are detected.
CI opens it in headless Chrome and verifies the report with
`panel_browser_checks.py verify --out /tmp/panel-check-result.html`.

`local_viewer.py check` additionally verifies every page's image count and explicit
coordinates, immutable assets, restart detection and HTTP 409 after source drift.
A newly started fixture server is not a substitute for inspecting a user's existing
server when investigating an upgrade failure.
