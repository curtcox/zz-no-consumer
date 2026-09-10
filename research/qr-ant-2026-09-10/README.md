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

## Where the model and the scanner still disagree

`scan-styles.tsv` records Vision's verdict on all 32 style and ECC combinations in
`metrics-report.txt`. They agree on 28. All four disagreements are the `bold` style, where
the tool reports failure and Vision reads the symbol anyway — the tool is conservative, and
on the safe side. `bold` is not recommended for that reason and for the one below.

`scan-resolution.tsv` records the same styles rendered at 6, 8, 10, 14 and 20 pixels per
module. `grid`, `swarm` and `dense` read at every resolution tested. `bold` read at one of
five, which is the finding that settles it: a style that reads sometimes is not a style to
put on a cover.

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
