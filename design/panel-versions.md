# Panel Versions

Every panel keeps every version it has been given. Which one belongs in the book is
a separate decision, recorded separately, and deliberately made late.

## Why

A panel is rarely right on the first attempt, and "right" is not a property of the
panel alone — it depends on the panels either side of it, on whether the sequence
reads, and on a style that is still settling. Choosing at the moment of generation
forces that judgement before the evidence exists, and destroys the alternative.

The routing key in [`panel-image-types.md`](panel-image-types.md) makes this sharper:
different models will draw the same panel, and comparing them is the whole point of
having a mix. That comparison needs both versions to still exist.

## Layout

```
assets/art/panels/001-01/v01-flux2-klein-4b-1001.webp
assets/art/panels/001-01/v02-flux2-klein-4b-2001.webp
assets/art/panels/001-01/v03-qwen-image-1001.webp
```

A directory per panel, one file per version. The filename carries the version
number, the model, and the seed, so the store is legible without the table; the
table is still the authority.

Generation never overwrites. `scripts/produce.py` adds a version through
`panelart.store()`, and `--force` means *draw another version*, not *replace the
one you have*. Nothing a run produces can destroy an earlier attempt.

## The decision record

[`../data/panel-art.tsv`](../data/panel-art.tsv) has one row per version. Every
column is a fact discovered from disk except one:

| status | meaning |
| --- | --- |
| `candidate` | in the running; the default for anything newly generated |
| `chosen` | the version that belongs in the book |
| `rejected` | set aside, kept on disk, never shown |

`panelart scan` refreshes the facts and preserves the decisions, so the table can be
regenerated at any time without losing curation. Choosing is a one-line command:

```sh
python3 scripts/panelart.py list --panel 001-01
python3 scripts/panelart.py choose 001-01 v02
python3 scripts/panelart.py reject 001-01 v01 --note "hands"
python3 scripts/panelart.py status
```

Choosing a version clears any previous choice for that panel, so exactly one wins.

## What the book shows while the choice is open

`panelart.resolve()` returns the chosen version where a choice has been made, and
the newest candidate where it has not. Undecided panels therefore still render, and
the book stays readable end to end throughout — which is the property
`validate-viewer.py` exists to protect.

Nothing about the pipeline downstream changes: `scripts/letterpress.py` letters
whatever resolves, and `scripts/build-site.py` publishes it.

## What the reader sees

A panel with more than one live version gets an **Other versions of this panel**
strip under the image in the viewer, listing each alternate with its version number
and the model that drew it, linking to the full image. The strip states that the
choice is still open, so an alternate is never mistaken for a correction.

The strip is part of the image view rather than a route of its own. That keeps the
eight-direction navigation and the spacebar reading chain exactly as they are, which
is worth more than giving each alternate its own address.

## Repository cost

Versions are the expensive part of this design, so the accounting is explicit:

- The source store is **not** copied into `docs/`. The resolved version's pixels
  travel inside its lettered SVG, so publishing the tree as well would store every
  chosen image twice.
- Alternates are copied once, only for panels that have them.

`python3 scripts/panelart.py size` projects the store from what is actually there.
Measured on real output — bleed-cropped WebP at 1200x800 — a panel is about 302 KB,
so 541 panels cost roughly **160 MB per version kept**: 319 MB for two each, 479 MB
for three. Two is a reasonable working ceiling; three is worth a deliberate decision
rather than a drift, and a larger panel size would move all three figures.

Rejecting a version keeps it on disk. If the store needs to shrink, rejected
versions are the first thing to delete, and the table records what was there.
