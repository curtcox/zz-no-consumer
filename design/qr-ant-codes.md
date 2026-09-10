# QR codes drawn in ants

How [`scripts/qrant.py`](../scripts/qrant.py) turns a 256t content tag into a scannable
symbol whose dark half is ant bodies, what each way of drawing it costs, and which ones are
safe to print. The measurements behind every number here are in
[the scanner comparison](../research/qr-ant-2026-09-10/README.md).

## Status

**Tool built and measured, 10 September 2026. No symbol is adopted anywhere yet.** The
cover use this was built for is a decision for the owner; this document reports the options
and recommends one.

## This is apparatus, not page art

A QR symbol is a lattice of marks on a fixed grid, in a fixed count, arranged to be read as
data. The ant convention in [the visual bible](../content/visual-bible.md) requires the
opposite of all three: no count, no correspondence between a mark and anything, no reading
off the page. [The density note](ant-density.md) argues the marginal layer's whole defence
is that "its number cannot be read off the page" — a QR code's number can, by machine, on
purpose.

So a symbol from this tool is **apparatus**: a cover, a colophon, a card, a download page.
It never appears in a margin, a gutter or a panel, and it is never adjacent to the marginal
ant layer, where a reader could take the two registers for one. Every generated SVG carries
that statement in its `<desc>`. The two uses share an animal and nothing else, and the
shared animal is deliberate: both are drawn from `assets.ant` in
[`data/storyboard-assets.json`](../data/storyboard-assets.json), so the QR ant cannot drift
away from the ant the pages draw.

This resolves the collision by separation rather than by argument. If the owner would
rather the collision be argued — that a machine-readable count of ants is defensible beside
a deliberately uncountable one — that is a different decision and this document does not
make it.

## The payload sets the symbol

A 256t content tag is 94 characters of base64url: an 8-character length prefix and an
86-character hash. Base64url is mixed case, so **alphanumeric mode cannot hold it** and the
symbol is byte mode. With the shortest useful resolving prefix the payload is about
103 bytes:

```
256t.org/00000056Qw3Qw3…            103 bytes
https://256t.org/00000056Qw3Qw3…    111 bytes
```

That lands on four symbol sizes. The error-correction budget is what art is paid for out
of, so it is the last column that matters:

| ECC | version | modules | byte capacity | slack at 103 | blocks | budget (codewords) |
| --- | --- | --- | --- | --- | --- | --- |
| L | 5 | 37 × 37 | 106 | 3 | 1 | 13 |
| M | 6 | 41 × 41 | 106 | 3 | 4 | 32 |
| Q | 8 | 49 × 49 | 108 | 5 | 6 | 66 |
| H | 10 | 57 × 57 | 119 | 16 | 8 | 112 |

Version 10-H holds up to 119 bytes, so it carries the bare tag and the `https://` form
without changing size — the only row that does. Its 112-codeword budget is also the largest,
and it spreads over 8 blocks rather than 1, which matters because a symbol fails on its
**worst** block, not its average.

## What "data loss" means here

Nothing is lost from the payload: every option below either carries all 103 bytes or does
not scan. What the art spends is **margin** — the damage the symbol could have absorbed
from a scuff, a fold, a bad angle or cheap printing, and now cannot, because the drawing
already spent it.

The tool reports it three ways, because a drawing can pass one and fail another:

- **spent / worst** — the share of the Reed-Solomon budget consumed, in total and in the
  worst single block. This is the margin the art took.
- **cam** — modules read wrong after the raster is put through a local binariser, which is
  what a camera actually does. Ink that misses a module's centre but fills its cell shows up
  here and nowhere else.
- **find** — how many of the three finder patterns a locator could still pick out. Under
  three, nothing else matters: the scanner never gets as far as the data.

`reads` is all three together, plus a decode. `blur` repeats it out of focus.

## The options

Payload 103 bytes, rendered at 12 pixels per module, `python3 scripts/qrant.py options`.
Vision is the system scanner's verdict on the same PNG, from
[the scanner comparison](../research/qr-ant-2026-09-10/README.md).

| style | ants (H) | fit | spent | worst | light cell | reads | Vision | at 6–20 px/module |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 0 | — | 0% | 0% | 0.00 | yes | reads | reads |
| `grid` | 1 873 | 100% | 0% | 0% | 0.08 | yes | reads | reads at all five |
| `swarm` | 4 760 | 88% | 0% | 0% | 0.13 | yes | reads | reads at all five |
| `dense` | 8 799 | 75% | 3% | 7% | 0.15 | yes | reads | reads at all five |
| `bold` | 5 006 | 72% | 54% | 86% | 0.22 | no | reads 3 of 4 | reads at 1 of 5 |
| `bolder` | 5 009 | 65% | 107% | 107% | 0.33 | no | not found | — |
| `halftone` | 6 334 | 62% | 107% | 107% | 0.39 | no | not found | — |
| `wild` | 3 468 | 83% | 107% | 107% | 0.69 | no | not found | — |

*fit* is the share of the ants the style offered that found room. It is the honest cost of
the constraint: `dense` wants a third more ants than the code will accept, and the tool
declines them rather than drawing them and failing.

**Three styles cost nothing at all.** `grid`, `swarm` and `dense` spend no meaningful part
of the budget, read under every test, and read on a real scanner at every resolution tried.
The choice among them is purely a picture:

- **`grid`** — one ant per dark module. The ants are individually legible, the lattice is
  obvious, and the drawing reads as *a QR code made of ants*. Least ink (27%), so it prints
  and photocopies best.
- **`swarm`** — ants scattered off the lattice, sized and turned at random. The lattice
  stops being visible as a grid of cells and the picture reads as *a swarm that happens to
  be a QR code*. This is the best-looking option.
- **`dense`** — as many ants as the constraint will take. Nearly twice `swarm`'s ants, but
  they crowd into a mass in which individual ants are harder to see; at reading size it
  starts to look like texture rather than animals.

**Everything past those three fails.** The tool reports `bold` as failing and Vision reads
it three times in four — but at five render resolutions it read once. A symbol that reads
sometimes is worse than one that never does, because it passes proofing and fails in a
reader's hands. `bolder`, `halftone` and `wild` are over budget everywhere and are kept only
so the far end of the trade is visible rather than asserted.

There is no middle. The curve does not run smoothly from safe to pretty; it runs flat and
then falls off, because the binding constraint is not the error-correction budget at all —
it is how much ink a light module's cell can hold before a camera's local threshold moves.
That constraint is met or it is not.

## Recommendation

**`swarm` at ECC H.** Best picture of the three that cost nothing, the largest and
best-spread correction budget left entirely intact for real-world damage, and the only
version that carries the `https://` form of the tag without growing. It reads at every
resolution tested on a real scanner.

Take `grid` instead if the symbol has to survive a photocopier, a fax-grade scan or printing
at under about 25 mm, where less ink and a visible lattice are worth more than the picture.
Take `dense` only if the mass is the point.

## How ink is made

Two registers, both available:

- **Vector**, the default: the edition's own ant from `assets.ant`, rasterised in pure
  Python for measurement and emitted as SVG with one `<defs>` ant and one `<use>` per mark
  — the economy [the density note](ant-density.md) worked out for the marginal layer, which
  matters more here, at thousands of marks per symbol.
- **Photographic**, with `--photos DIR`: PNGs of real ants, resampled and rotated per mark.
  Alpha is used where present, otherwise darkness. **No ant photographs are in the
  repository**; supply them and record their source and licence in
  [`CREDITS.md`](../CREDITS.md) before any published use. What a QR code needs from a
  photograph is its silhouette, so the metrics above are a good guide to what a
  photographic run will cost, but re-measure rather than assuming.

## What is not settled

1. **Which symbol, if any, goes on the cover**, and at what printed size. Every measurement
   here is of a rendered raster; ink spread, paper and lighting are not modelled.
   Proof it and scan the proof with real phones before adopting.
2. **The prefix.** `256t.org/` is assumed to resolve. If it does not, the payload is
   111 bytes with `https://`, which only version 10-H absorbs without changing size — the
   recommendation is unaffected, but nothing smaller survives the change.
3. **Whether photographic ants are wanted at all**, and if so their sourcing and licence.
4. **Where a generated symbol is stored.** Nothing is committed yet; `qrant.py` writes where
   it is told and no build step calls it.
