# Independent SVG components

The component workshop separates what a thing looks like from where it appears in a
storyboard. Characters, objects, connections and locations each have a stable ID, a
visual purpose, a selected default and any number of saved SVG versions.

## Use the workshop

```bash
python3 scripts/svg_components.py serve --port 8767
```

Open <http://127.0.0.1:8767/>. Search by name, ID or purpose; filter by category; select
a component and a saved version. The two canvases compare versions at the same size,
ink and surface. Guides, transparency and dark surfaces help inspect shape and edges.

Edit the SVG source or import a file, describe the change, and **Save new version**.
The previous files stay intact. A version can be based on any earlier version; its
parent and change note remain in the history. **New component** creates an independent
definition and its first version. SVG downloads also work from unsaved previews.

Saving an alternative does not change the default. **Use selected version as default**
updates the component reference used by unpinned scene nodes. The workshop reports which
storyboards follow the default and which have pins. **Apply to storyboards** then runs
the existing artwork generator and site builder. Only changed scenes gain new artwork
versions; the existing selection rules still apply. A failed build reports its error.
Default selection and generation are separate steps so alternatives can accumulate
without repeatedly rebuilding the book.

To roll back, select an older saved version, choose it as default and apply again.
No historical component or panel artwork is deleted. Multiple workshop windows reject
stale writes; reload a stale window before continuing. Unsaved drafts live in the browser
and must be saved or downloaded before closing it.

## Definition and storage

| File | Role |
| --- | --- |
| `data/svg-components.json` | Canonical identities, categories, purposes, defaults and version metadata |
| `assets/svg-components/ID/v001.svg` | Complete, independently viewable SVG; never overwrite an accepted version |
| `data/storyboard-assets.json` | Derived export of default geometry, retained for ant and other existing tools |
| `data/storyboards.json` | Scene instances: component references, placement, color, labels and optional pins |

Versions use `v001`, `v002`, and so on, without a fixed count limit. Each records a
SHA-256 digest, creation time, change note and optional parent. The checker detects edits
to historical files. The catalog is authoritative: `svg_components.py export` repairs
the compatibility export after an interrupted write. If a write leaves an unregistered
SVG or a lock, inspect and recover it explicitly; never remove it just because it is old.

A scene node follows its component's selected default:

```json
{"asset": "person-seated", "box": [0.1, 0.2, 0.3, 0.5], "color": "steel"}
```

Add `"asset_version": "v002"` to pin that instance. Two instances may use different
versions of the same component in one scene. Rendered source snapshots preserve the
geometry actually used; SVG IDs are scoped per instance so gradients and clips do not
collide. Existing unpinned scenes retain their original output until a default changes.

Components use `viewBox="0 0 100 100"`. Put presentation attributes on inner groups and
use `currentColor` for scene-controlled ink. Paths, shapes, local gradients, clips,
masks and embedded raster images are supported. Scripts, CSS, external resources,
nested SVG viewports and arbitrary root presentation attributes are rejected. Keep
lettering in the existing scene lettering system. A location should normally leave
characters and movable objects separate so it supports multiple scenes.

The library ships the original vocabulary unchanged as `v001`, along with optional
alternatives and a separate reconstructed creator-workroom location. These are staging
designs, not approved likenesses or documentary interiors. The visual purpose is an
editorial instruction, not proof that the drawing already communicates it successfully.

See the [story location audit](story-location-audit.md) for setting-specific additions,
canonical panel anchors and the distinction between physical rooms and logical environments.

## CLI and published gallery

```bash
python3 scripts/svg_components.py add arrow --svg /tmp/arrow.svg --parent v001 --note "Clearer endpoint"
python3 scripts/svg_components.py choose arrow v002
python3 scripts/svg_components.py check
python3 scripts/storyboards.py generate
python3 scripts/storyboards.py check --complete
python3 scripts/build-site.py
python3 scripts/svg_components.py check --built
python3 scripts/storyboards.py check --complete --built
```

The site builder exports `/components/`, linked from the storyboard workshop. The
published app supports browsing, comparison, local draft previews and downloads.
Repository writes require the local workshop; a static site cannot save files back to
the repository. A standalone gallery is also available with
`python3 scripts/svg_components.py gallery --output /tmp/components`; serve that directory
over HTTP so the browser can load its catalog.

The local service binds only to loopback. Mutations require its session token, matching
origin when supplied, and the current catalog revision. Saves and rebuilds share a lock.
The checker exercises preservation, rollback, stale-write rejection, invalid SVGs,
missing version pins, two-version rendering and isolated SVG IDs using temporary data.
