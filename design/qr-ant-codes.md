# QR codes drawn in ants

How [`scripts/qrant.py`](../scripts/qrant.py) turns a 256t content tag into a scannable
symbol whose dark half is ant bodies, what each way of drawing it costs, and which ones are
safe to print. The measurements behind every number here are in
[the scanner comparison](../research/qr-ant-2026-09-10/README.md).

The findings are published as a gallery at `/qr-ant/` on the site, built by
[`scripts/qr_gallery.py`](../scripts/qr_gallery.py) from tracked assets under
`assets/qr-ant/`. Every symbol there encodes a 103-byte placeholder whose own text says it
is one; nothing published resolves anywhere.

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

## Two ways to draw with an ant

The styles fall into two families, and they answer different questions.

**Scattered** styles (`grid`, `swarm`, `dense`, and the looser `bold`, `bolder`, `halftone`,
`wild`) build the dark half out of the *positions* of many small copies of the library ant.
The ant is a mark; the picture is where the marks are.

**Posed** styles (`body-mid`, `body-large`, their `-pile` variants, `body-bold`, and the
`abdomen-*` family) build it out of the ant's own silhouette. Each ant is jointed to fit the ground it covers — gaster and
head pivoting about the thorax, six legs and two antennae solved joint by joint — so a symbol
is drawn with a few hundred visibly individual animals instead of several thousand identical
marks. `scripts/antpose.py` owns the anatomy and the fitting.

Poses **articulate and never stretch**. Every bone keeps the length the asset gives it and
every lobe keeps its radii; `antpose.py check` fails if a joint changes either. That
restriction has two consequences that decide what the posed styles can do:

1. **A large ant has a large gaster, and a gaster has to sit in dark ground.** At six modules
   long the gaster is about two modules across, and only about a third of a QR symbol's dark
   modules lie in a two-by-two block. Measured against the real pattern, **nothing fits above
   about six modules at any tolerance** — a fact about QR patterns, not a limit of the search.
2. **A large ant has proportionally thin legs.** At six modules its legs are a quarter of a
   module wide, so they cannot fill a module. Bodies cover ground; legs are filigree, and the
   fitter's job with them is mostly to keep them out of trouble.

So the posed ladder tops out near six modules and averages under two, because the ant that
finishes a filament is necessarily small. What it buys is a **three-to-five-fold drop in ant
count at no cost to the code**, with every ant individually legible.

## One square, one abdomen

The posed ladder above sizes an ant against the *symbol* — as large as the ground anywhere
will take — and lets whichever part of it lands on a module do the darkening. There is a
second way to set the scale, and it turns out to be the better one: size the ant against a
*single module*, so that the gaster is as wide as the square, and pin the gaster at the
square's centre. Every mark then reads as an abdomen sitting on a module, with the thorax,
head and legs swinging off it onto the ground next door.

The sizing follows from the anatomy without a choice to make. The gaster is 34 × 24 units in
an ant 76 units long, so:

| one module square equals | ant length | gaster, in modules |
| --- | --- | --- |
| the gaster's long axis | 2.24 modules | 1.00 × 0.71 |
| the gaster's short axis | 3.17 modules | 1.42 × 1.00 |

Both are drawn: `abdomen-small` is the first, `abdomen` the second. For comparison, `grid`
draws one ant per module too, but sized to *fit* the module, which leaves its abdomen 0.67 ×
0.47 of a square — half the width of the thing it is standing on, and far too small to read
as the abdomen of an animal.

Two thirds of an abdomen-scaled ant hangs outside the square it was drawn for, and where that
overhang lands is the whole problem; the orientation search is what spends its time on it.
Twelve headings are tried per module and the joints are solved at each.

## Choosing the mask for ant-shaped ground

Any of the eight mask patterns gives a valid symbol; the standard picks one by a penalty
score meant to keep a symbol easy to read. The posed styles pick instead by how much
body-sized ground the mask leaves — the share of dark modules in a two-by-two block, which
varies from 32% to 39% across the eight — breaking ties by the standard's own penalty. There
is no downside beyond that tie-break, and about a fifth more ground for a body to sit on.

## The options

Payload 103 bytes, rendered at 12 pixels per module, `python3 scripts/qrant.py options`.
Vision is the system scanner's verdict on the same PNG, from
[the scanner comparison](../research/qr-ant-2026-09-10/README.md).

At ECC H, version 10, 57 × 57 modules:

| style | ants | fit | mean ant | longest | spent | worst | light cell | reads | Vision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `plain` | 0 | — | — | — | 0% | 0% | 0.00 | yes | reads |
| `grid` | 1 869 | 100% | 1.4 | 1.6 | 0% | 0% | 0.08 | yes | reads |
| `swarm` | 4 744 | 88% | 1.2 | 2.2 | 0% | 0% | 0.13 | yes | reads |
| `dense` | 8 782 | 75% | 1.2 | 2.6 | 0% | 0% | 0.15 | yes | reads |
| **`body-mid`** | **1 172** | 78% | 1.7 | 4.0 | **0%** | 0% | 0.08 | yes | reads |
| **`body-large`** | **1 066** | 92% | 1.9 | 3.9 | **0%** | 0% | 0.08 | yes | reads |
| **`body-mid-pile`** | **1 072** | 80% | 1.9 | 4.0 | **0%** | 0% | 0.10 | yes | reads |
| **`body-large-pile`** | **1 018** | 93% | 1.9 | 3.9 | **0%** | 0% | 0.08 | yes | reads |
| **`body-bold`** | **991** | 96% | 1.9 | **6.0** | **0%** | 0% | 0.08 | yes | reads |
| **`abdomen`** | **920** | 95% | **2.2** | 3.2 | **0%** | 0% | 0.07 | yes | reads |
| **`abdomen-small`** | **1 039** | **99%** | **2.1** | 2.2 | **0%** | 0% | **0.02** | yes | reads |
| **`abdomen-full`** | 1 118 | 92% | **2.8** | 3.2 | **0%** | 0% | 0.08 | yes | reads |
| **`abdomen-bold`** | **851** | 94% | **2.3** | **3.6** | **0%** | 0% | 0.09 | yes | reads |
| `bold` | 5 058 | 73% | 1.4 | 3.0 | 0% | 0% | 0.22 | yes | reads |
| `bolder` | 5 252 | 69% | 1.6 | 3.4 | 0% | 0% | 0.33 | yes | reads |
| `halftone` | 6 039 | 60% | 1.2 | 2.4 | 0% | 0% | 0.36 | yes | not found |
| `wild` | 3 212 | 77% | 2.1 | 4.0 | 71% | 86% | 0.42 | no | not found |

The same at ECC L, version 5, 37 × 37 — the size at which the ants are largest relative to
the symbol, and the one that looks most zoomed in:

| style | ants | longest ant | spent | Vision |
| --- | --- | --- | --- | --- |
| `swarm` | 1 845 | 2.2 | 0% | reads |
| `dense` | 3 397 | 2.6 | 0% | reads |
| **`body-large`** | **407** | **4.8** | **0%** | reads |
| **`body-large-pile`** | **386** | **4.8** | **0%** | reads |
| **`body-bold`** | **363** | **4.8** | **0%** | reads |
| **`abdomen-bold`** | **331** | 3.6 | **0%** | reads |
| **`abdomen`** | **344** | 3.2 | **0%** | reads |
| **`abdomen-small`** | 383 | 2.2 | **0%** | reads |

*fit* is the share of the ants a style offered that found room; *mean* and *longest* are ant
lengths in modules. Every `body-*` symbol at every error-correction level reads on the system
scanner, and all twenty spend **nothing** of the correction budget.

**Everything that costs nothing is on the table.** After the fitter was made to respect both
constraints a scanner applies — the whole cell's ink, which sets a local threshold, and the
cell's centre, which is what gets sampled — the correction budget stopped being the binding
constraint for every style except `wild`. What separates the options now is the picture and
how much margin is left for the real world.

- **`abdomen-small`** — the cleanest drawing the tool makes. Its light field carries **0.02**
  mean ink, less than `grid`'s 0.08 and by far the lowest of any ant style; 99% of the ants it
  offers find room; and a local binariser misreads none of it at ECC L. Each abdomen is a
  module long, and the ants are plainly animals rather than marks.
- **`abdomen-bold`** — the fewest ants of any style that reads: 331 at ECC L, 851 at ECC H,
  with abdomens slightly wider than their square and ants up to 3.6 modules long.
- **`abdomen`** and **`abdomen-full`** — the same idea with a wider abdomen, and with one on
  *every* dark module rather than only where one is still needed. `abdomen-full` is the
  densest, and its abdomens run together into strings; individual animals get lost.
- **`body-large-pile`** — the fewest ants of the symbol-scaled ladder, allowed to lie across
  each other. Ants up to 4.8 modules long at ECC L — the longest anything reaches — plainly
  individual, in varied attitudes.
- **`body-large`** — the same, kept apart so no ant is occluded by another. Slightly more
  ants and a slightly sparser look; every animal is whole.
- **`body-bold`** — the largest ants of all (6.0 modules at ECC H) and the highest fit rate,
  bought with a looser whole-cell budget that costs nothing measurable.
- **`body-mid`** — a shorter ladder, so more ants and fewer very large ones. Closer to the
  scattered styles in feel.
- **`swarm`** / **`dense`** — the scattered family: mass rather than animals, four to eight
  times the ant count, and a texture rather than a cast.
- **`halftone`** and **`wild`** — kept only to show the far end. `halftone` is not found by a
  real scanner despite the tool's decoder reading it; `wild` fails everything.

## Recommendation

**`abdomen-small` at ECC H**, with the same style at ECC L as the alternative when the symbol
can be printed large enough.

Sizing the ant to the module rather than to the symbol wins on every measurement that matters.
It leaves the light field cleaner than any other ant style — 0.02 mean cell ink against
`grid`'s 0.08 and `swarm`'s 0.13 — which is the quantity that decides whether a real scanner
finds the symbol at all. It wastes almost nothing: 99% of the ants it offers find room,
against 75–93% everywhere else. It costs no correction budget, it reads crisp and out of
focus, and all sixteen combinations of the four abdomen styles and the four levels were read
by the system scanner, at 6, 10 and 20 pixels per module.

ECC H for the same two reasons as before: the full 112-codeword budget over eight blocks is
left intact for real-world damage, and version 10 is the only size that carries the
`https://` form of the tag without growing. Drop to ECC L for 383 ants instead of 1 039, each
correspondingly larger against the whole, when the printed symbol will be big enough that the
margin is not needed.

Take **`abdomen-bold`** if the fewest and longest ants are the point, or **`body-large-pile`
at ECC L** for the longest ants anything reaches — 4.8 modules. Take **`swarm` at ECC H**
only if the mass, rather than the individual animal, is what the picture is for.

## What the second pass changed

The posed styles were added after the scattered ones, and building them found a mistake in
the first set's measurements worth recording. The fitter placed ants whose *whole cell* ink
stayed under budget but whose legs ran straight through a light module's **centre** — the
one point a scanner actually samples. Every one of those was a lost module the cell-mean
constraint could not see.

Enforcing both constraints together fixed the posed styles and improved the scattered ones
at the same time: `bold` and `bolder` went from spending half the correction budget to
spending none, and from unreliable to reading. The first set's headline — that three styles
are free and everything past them fails — was **too pessimistic**, and the corrected table
above replaces it. The claim that survives is narrower and still worth holding onto: what
constrains an ant QR code is not the error-correction budget but where the ink lands
relative to the module grid, at two different scales at once.

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
5. **Whether the posed ant needs its own review as a drawing.** The fitter bends joints
   within a range this document set by eye — 38 degrees at the gaster, 32 at the head, 62 and
   75 at the leg joints, 55 at the antennae. Those are plausible rather than researched, and
   at a few hundred ants per symbol a wrong range is a hundred wrong animals. Someone who
   knows what an ant can do should look at a rendered sheet before this goes on a cover.
