# Lettering Slots

**Approved 3 September 2026.** The geometry is in
[`../data/lettering-slots.json`](../data/lettering-slots.json), which
`scripts/letterpress.py` reads and `scripts/build-site.py` applies to every panel
that has final art. Changing a number here changes the whole book's lettering, so
re-run `python3 scripts/letterpress.py audit` after any edit.

## What this decides

Generated art cannot be relied on to leave text alone. The book's answer is the one
[`lettering.md`](lettering.md) already gives — every word the book says lives in a
controlled layer applied after the art. This proposal settles the one question that
answer leaves open: **where on the panel does that layer put things?**

The alternative to a convention is authoring a position for every element by hand.
There are 511 lettering elements across 541 panels. A convention is not a
simplification here; it is the difference between a build step and a second book.

## The slots

Every box is a fraction of the panel, so the same convention serves any panel size.
A slot is a *maximum* box with an anchored corner, not a fixed rectangle:
`letterpress.py` measures the text with the Helvetica metrics in `textimage.py` and
shrinks the box to its content, growing away from the anchor.

| Slot | Role | Order | Box | Anchor |
| --- | --- | ---: | --- | --- |
| `tl` | caption | 1 | x .04 y .04 w .34 h .26 | top-left |
| `tr` | caption | 2 | x .62 y .04 w .34 h .26 | top-right |
| `bl` | caption | 3 | x .04 y .70 w .34 h .18 | bottom-left |
| `br` | caption | 4 | x .62 y .70 w .34 h .18 | bottom-right |
| `block-r` | machine, interface | 1 | x .62 y .32 w .34 h .36 | top-right |
| `block-l` | machine, interface | 2 | x .04 y .32 w .34 h .36 | top-left |
| `slate-br` | provenance slate | 1 | x .62 y .90 w .34 h .06 | bottom-right |
| `top`, `bottom` | full-width caption bands | — | x .04 w .92 h .16 | — |

`top` and `bottom` are alternatives to the corner slots and are never used alongside
them. Every other pair is disjoint, which `letterpress.py` verifies on load and
refuses to run if that stops being true.

Placement order is strict raster order — top-left, top-right, bottom-left,
bottom-right — because `lettering.md` requires that reading order be unambiguous
top-to-bottom and left-to-right. A panel's first caption takes `tl`, its second `tr`,
and so on.

## What it covers

Measured across all 112 pages by `python3 scripts/letterpress.py audit`:

| Role | Elements placed |
| --- | ---: |
| Caption | 354 |
| Machine text | 64 |
| Interface voice (ChatGPT) | 23 |
| **Automatic** | **441 of 511 — 86.3%** |
| Manual | 70 across 62 panels |

Nothing overflows its slot at a readable type size; the audit fails the build if
anything does.

## What it deliberately does not cover

**Dialogue.** A speech balloon needs a speaker position, and no convention can derive
that from a script — the script says who talks, not where they stand in the frame.
Those 70 elements across 62 panels stay a manual pass, and `letterpress.py` reports
them by panel rather than guessing. They cluster where you would expect: Curt's home
office in the prologue, the security-response scenes, and the accountability forum.

This is the honest boundary of automation. Attempting to place balloons by convention
would produce tails crossing faces and balloons over evidence, which `lettering.md`
forbids outright.

## Why the corners are quiet

The slots assume the art leaves those areas dark and empty. That assumption is now
carried in [`../prompts/global-style.md`](../prompts/global-style.md), which asks for
quiet near-empty corners with no drawn caption box, plate, sign, or lettered screen.

This matters more than it sounds. An overlay only hides what it is larger than, and
the convention cannot know how big a box the model drew. On the first real test the
lettered caption covered (48,32)–(456,131) while the generated caption box occupied
(44,34)–(288,146): a 15-pixel band of invented lettering survived along the bottom
edge. The fix is not a bigger box — it is art with no box in it. Asking a model to
"reserve a caption field" invites exactly the thing the overlay then has to hide.

## Open before this is approved

**Trim size.** At 1200×800 a panel is 4″×2.67″ at 300 dpi, which is small for print.
Every type size here is expressed in panel pixels and scales with the panel, so the
convention survives a resolution change — but the minimum sizes in
`data/lettering-slots.json` were chosen against the current panel and need a proof at
intended trim size before they are trusted. `content/production-review.md` already
requires that proof before any page reaches `locked`.

**Whether four caption slots is enough.** No panel in the current draft needs a fifth,
but three pages carry captions that span panels (`**Caption — across panels …**`),
which this proposal treats as ordinary captions on the first panel of the run. If a
spanning caption should be drawn across the gutter instead, that needs a slot of its own.

## Trying it

```sh
python3 scripts/letterpress.py slots     # the convention, and a rendered slot map
python3 scripts/letterpress.py audit     # coverage across all 112 pages
python3 scripts/letterpress.py panel --page 001 --image 1 --art PATH
```

`scripts/build-site.py` letters every panel that has final art in
`assets/art/panels/` with no further change.
