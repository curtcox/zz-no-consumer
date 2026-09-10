# Ant QR codes — measured against a scanner, 10 September 2026

Evidence behind [`scripts/qrant.py`](../../scripts/qrant.py) and its metrics. The tool
reports how much of a QR symbol's error correction a drawing spends. That report is only
worth reading if the model behind it agrees with a real scanner, so this directory records
what happened when the two were compared, including the places they still disagree.

Everything here was produced on macOS 15 with the system Vision framework. **Nothing in
this directory is needed to build the book or run the checks**, and no Python tool imports
it. The two Swift files are diagnostics, kept because the findings below cannot be
reproduced without them.

## What the comparison found

### 1. A round trip proves nothing about a codec

`qr_core.py` encoded and decoded its own symbols correctly while carrying two bugs that
made those symbols unreadable to anything else: an inverted finder pattern (the dark
three-by-three core drawn as a light ring and back) and a transposed format-information
placement (the first copy written along row 8 instead of down column 8). Both survived
every self-consistency test, because the decoder made the same mistake as the encoder.

Both died immediately against a symbol produced elsewhere. `reference.swift` generates one
with CoreImage's `CIQRCodeGenerator` and dumps its modules; the encoder now reproduces it
module for module. That symbol is pinned in `qr_core.py` as
`COREIMAGE_HELLO_WORLD_1M2` and checked on every run.

Over 60 random byte-mode payloads, the matrices are byte-identical whenever the two
implementations pick the same mask, and this decoder read all 60 CoreImage symbols. Mask
*selection* agrees 42 times in 60; the standard's four penalty rules leave ties to break
either way and any mask gives a valid symbol.

### 2. Correct module centres are not enough

The first drawing engine placed ants so that every module's *sampling point* was correct,
and its decoder confirmed a clean read with zero correction spent. The system scanner could
not find those symbols at all.

The quantity that separated the symbols that scanned from the ones that did not was ink in
the **whole cell** of a light module, not at its centre:

| Drawing | mean light cell | light cells over 0.30 | Vision |
| --- | --- | --- | --- |
| plain squares | 0.00 | 0 | reads |
| one ant per module | 0.09 | 3 | reads |
| off-lattice scatter | 0.32 | 821 | not found |
| dense scatter | 0.57 | 1402 | not found |

A scanner binarises against a local neighbourhood before it samples anything, so ink that
misses every centre but fills the space around it still moves the threshold it will be
sampled against. `qrant.py` now constrains the cell mean (`light_cap`), and that constraint
is the dial the whole tool turns.

### 3. Locating fails before decoding does

With cell ink capped, off-lattice drawings decoded perfectly under the tool's own decoder
and were still not found by Vision. The cause was the finder patterns: their modules were
untouched, but ink pressed against the outside of their separators broke the 1:1:3:1:1 run
a locator scans for.

Giving each finder a clear margin fixed it. Measured over styles, ECC levels and
resolutions:

| clear margin around each finder | symbols found by Vision |
| --- | --- |
| none | 9 of 16 |
| 1 module | 12 of 16 |
| 2 modules | 14 of 16 |
| 3 modules | 13 of 16 |

`FENCE_MARGIN = 2` is what the tool ships. Dilating *every* functional pattern rather than
the finders alone scored better still, but the timing patterns run the width of the symbol
and dilating those puts a five-module blank band through the middle of the picture.

`qrant.py` now runs the same finder scan itself and reports `find` as a count out of three,
so the failure that matters most is visible in the tool's own output rather than only in an
external scanner's.

### 4. A cell can stay under budget and still lose its module

Found while adding the posed styles, and it invalidated part of the first set's results.

The constraint from finding 2 is on the mean ink in a light module's **whole cell**, because
that is what a local binariser thresholds against. It is not sufficient. A jointed ant's leg
can run straight through a light module's **centre** — the single point a decoder samples —
while the cell's mean stays well under the cap, because a leg is thin and the cell is mostly
empty. Every such module is silently lost:

| style | peak light cell | cell cap | modules lost | all of them |
| --- | --- | --- | --- | --- |
| `body-fine` | 0.22 | 0.22 | 38 | light modules read dark |
| `body-large` | 0.22 | 0.22 | 10 | light modules read dark |

Both constraints have to hold together, and the fitter now enforces both. Doing so did not
only fix the posed styles: it took `bold` and `bolder` from spending half the correction
budget to spending none, and from unreliable on a real scanner to reading. **The first
version of this record's conclusion — that only three styles are free and everything past
them fails — was too pessimistic and has been superseded** by `metrics-report.txt`.

### 5. Two bugs the drawing hid

Two more that no assertion caught, both found by looking at numbers that seemed wrong:

* `try_place` rebuilt each candidate mark to try shrinking it, and rebuilt it without the
  posed geometry. Every fitted ant was being rasterised as an *unposed* library ant. The
  drawing looked plausible, the metrics were real, and none of it measured what it claimed.
* The fitter kept its own estimate of what was covered, separate from the raster. The two
  drifted, and the fitter spent about a third of the correction budget on ink the raster
  never delivered. It now measures each ant back off the grid it was drawn on.

### 6. Sizing the ant to the module beats sizing it to the symbol

The posed styles were first built to put the largest ant the symbol would take anywhere it
would fit. Sizing instead against a *single* module — gaster as wide as the square, pinned at
its centre — is better on every measurement taken, and the margin is not small:

| style | scale set against | ants at ECC H | fit | mean light cell | binariser errors |
| --- | --- | --- | --- | --- | --- |
| `grid` | fits inside one module | 1 869 | 100% | 0.08 | 5 |
| `swarm` | scattered, symbol-scaled | 4 744 | 88% | 0.13 | 17 |
| `body-large` | the whole symbol | 1 066 | 92% | 0.08 | 36 |
| **`abdomen-small`** | **one module** | **1 039** | **99%** | **0.02** | **5** |

The mean light cell is the quantity finding 2 identified as deciding whether a scanner finds
a symbol at all, and `abdomen-small` leaves it four times cleaner than anything else here —
cleaner than the lattice-bound `grid`, which was the previous best. All sixteen combinations
of the four abdomen styles and the four correction levels were read by Vision, and
`abdomen-small` and `abdomen-bold` were read at 6, 10 and 20 pixels per module.

The reason appears to be that pinning the gaster puts the ant's one thick part exactly where
the ink is wanted, so the thin parts — which are what stray onto light ground — have to cover
much less. Sizing against the symbol leaves the thick part wherever it lands and asks the
legs to make up the difference.

## Where the model and the scanner still disagree

`scan-styles.tsv` records Vision's verdict on all 68 style and ECC combinations in
`metrics-report.txt`. The two agree except at the margins: the tool's decoder reads
`halftone` at every level and Vision finds none of them, which is the tool being optimistic
about the one style that inks the light field on purpose, and `body-large` at ECC M and
`body-mid-pile` at ECC L are reported as failing a local binariser that Vision reads without
trouble, which is the tool being conservative. Every other row matches.

`scan-resolution.tsv` records symbols rendered at 6, 8, 10, 14 and 20 pixels per module. All
four posed styles read at every resolution tested, as do `grid`, `swarm` and `dense`.

## Where this is published

The findings these measurements support are laid out at `/qr-ant/` on the site, from tracked
assets under `assets/qr-ant/`. `scripts/qr_gallery.py` reads `scan-styles.tsv` from this
directory for the scanner column on that page, so a verdict recorded here is the verdict a
reader sees.

## Reproducing it

```sh
swiftc -O -o /tmp/qr-scan research/qr-ant-2026-09-10/scan.swift
swiftc -O -o /tmp/qr-ref  research/qr-ant-2026-09-10/reference.swift
python3 scripts/qrant.py options --text "$(cat your-tag.txt)" --style all --ecc all --out /tmp/qr
/tmp/qr-scan /tmp/qr/*.png
```

`scan.swift` prints `<path>\tOK\t<payload>` or `<path>\tFAIL\t<reason>` per file.
`reference.swift` takes a payload, an ECC letter and an output path, and writes the
reference symbol's modules as rows of `0` and `1` with a one-module quiet zone.

A verdict from one scanner is evidence, not proof. Vision is not the decoder in any
particular phone, and a printed symbol adds ink spread, paper and lighting that none of
this measures. Before a symbol goes on a cover, scan the actual proof with actual phones.
