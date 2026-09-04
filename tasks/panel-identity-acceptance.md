# Acceptance record — panel insertion, deletion, and movement

All six operations run against the tree as it stands after `scripts/panels.py` was added,
each reset before the next. For each: the tool's own plan, then `--apply`, then
`paneltypes.py write` and `build-site.py`, then all four validators plus `pagination.py check`
and `panels.py check`.

Tests 1–4 change one page. Tests 5 and 6 move a panel to another page, which is a membership
change rather than a renumbering — the same distinction that made moving a page across a
chapter boundary the most informative of the page-level tests.

Reproduce any row by running the command shown, then the two regeneration commands. The tree
is left unchanged by this document; nothing here is committed.

## Results

| # | Operation | Rhythm | Validators | `crossref --strict` | Source diff |
| ---: | --- | --- | --- | ---: | --- |
| 1 | insert one panel mid-page, page 039 | 6 → 7, **off default** | 4/4 green, 564 panels, 548 slots | 72 | 2 files, +15 −6 |
| 2 | delete one panel mid-page, page 035 | 5 → 4, default | 4/4 green, 562 panels, 546 slots | 71 | 2 files, +5 −17 |
| 3 | move a panel within a page, page 001 | 5 → 5, default | 4/4 green, 563 panels, 547 slots | 71 | 14 files, +25 −25 |
| 4 | insert one panel on a cross-referenced page, page 003 | 5 → 6, default | 4/4 green, 564 panels, 548 slots | 72 | 4 files, +19 −10 |
| 5 | move a panel to another page, 001-02 → 002-01 | 5 → 4 and 5 → 6, default | 4/4 green, 563 panels, 547 slots | 71 | 16 files, +32 −35 |
| 6 | move a panel across a chapter boundary, 003-04 → 036-02 | 5 → 4 and 5 → 6, default | 4/4 green, 563 panels, 547 slots | 72 | 4 files, +20 −20 |

"Source diff" is `git diff --shortstat -- content data prompts assets` after the operation
and the two regeneration commands, so the figures are comparable across rows and reproducible.
`build-site.py` letters 10 panels in every row, including both transfers: art that moves with
its panel keeps resolving.

"4/4 green" is `validate-continuity.py`, `validate-production-foundations.py`,
`crossref.py check`, and `validate-viewer.py`, all exit 0. `pagination.py check` and
`panels.py check` are green after all six: a panel operation does not move a page, so no
parity assertion and no named beat is touched.

Both transfers leave the totals at 563 panels and 547 slots. A panel that changes page is
neither created nor destroyed, and a tool that got that wrong would show it here.

The strict cross-reference baseline of 71 rises to 72 in the two insertion tests, and this is
correct rather than a regression: a new panel is written with `invented` / `NONE-FICTION`
provenance that its page's front matter does not declare, and `crossref` says so. The
placeholder is supposed to be visible until someone writes the panel.

Test 6 raises it for the same kind of reason and a more interesting one: the transferred
panel carries its own provenance onto a page whose front matter does not declare those
sources. The tool predicts this before it applies (`provenance-transferred`) and does not
repair it, because whether page 036 should now declare `METR` is a question about what that
page is about. Test 5 stays at 71 because page 002 already declares what the arriving panel
cites.

---

## 1. Insert one panel mid-page, page 039

```sh
python3 scripts/panels.py insert --page 039 --at 4 --allow-rhythm-shift --apply
```

Page 039 already carries six panels, so a seventh leaves the four-to-six default. Without
`--allow-rhythm-shift` the tool prints the same report and exits 1 with:

```
Refused: this operation leaves page 039 at 7 panels, outside the 4–6 default in
design/page-grammar.md. Re-run with --allow-rhythm-shift to take it deliberately.
```

With the flag it applies and keeps the finding on the work list:

```
Rhythm: 6 -> 7 panels (procedural sequence)
Panel map
  039-04 -> 039-05
  039-05 -> 039-06
  039-06 -> 039-07
  new  039-04

Warnings:
- [rhythm-off-default] content/pages/039.md: moves from 6 to 7 panels, which reads as a
  procedural sequence page rather than the 4–6 default
```

One source file changes, and it changes twice: the headings renumber, and so does the page
note that reads *"Panel 4 is the first time in the book that ChatGPT states something the
next panel contradicts"*, which becomes Panel 5. That sentence is the whole argument for the
tool. It is the kind of reference nobody greps for.

## 2. Delete one panel mid-page, page 035

```sh
python3 scripts/panels.py delete 035-02 --apply
```

Five panels to four stays inside the default band, so no flag is needed, and page 035 has no
generated art, so nothing is discarded. The tool still refuses to do it silently:

```
Warnings:
- [lettering-deleted] 035-02: carries 1 lettered element(s) and 6 words, which the deletion
  removes from the book
```

`- Panel 4's split — preserved storage on the left, live cache on the right — is the image
page 039 returns to and breaks` becomes `Panel 3's split`, with the rest of the sentence
untouched.

## 3. Move a panel within a page, page 001

```sh
python3 scripts/panels.py move 001-02 --to 4 --apply
```

The only test that touches art. Page 001 is the one page with generated images and written
prompts, so the permutation 2→4, 3→2, 4→3 moves three art directories and three prompt files
along with the headings:

```
Panel map
  001-02 -> 001-04
  001-03 -> 001-02
  001-04 -> 001-03

Notes:
- [art-renamed] 001-02: art moves to 001-04; the image was drawn for the old beat and should
  be re-reviewed against the new one
- [historical-record] data/generation-log.jsonl: names 001-02, 001-03, 001-04 and is a dated
  record, so it is not rewritten
```

Fifteen files: the page script, `data/panel-art.tsv`, the regenerated
`data/panel-types.tsv`, three renamed prompt files, and nine WebP files across three
directories. The prompt bodies move with their filenames: what was `panel-03.md` is now
`panel-02.md`, its heading reads `# Page 001 — Panel 02`, and its body, which said *"Repeat
panel 02's exact camera"*, now says panel 04 — because the panel it was pointing at is the
one that moved. `panel-01.md` and `panel-05.md` are not touched at all.

Unlike the page-level tests, git records the art as content changes rather than renames,
because the filenames *inside* the directories are identical and only the directory names
permute. The panel map printed by `apply` is the record of what moved where.

`data/generation-log.jsonl` keeps saying `001-02` for a render that happened at a time when
that key meant this panel. That is the point of the historical rule.

## 4. Insert one panel on a cross-referenced page, page 003

```sh
python3 scripts/panels.py insert --page 003 --at 2 --apply
```

The useful test. Page 003 is named by four sentences on two other pages, and all four are
composition instructions that have to follow the panel rather than the number:

```
content/pages/036.md:  Repeat page 003 panel 2  ->  panel 3
content/pages/036.md:  Repeat page 003 panel 3  ->  panel 4
content/pages/036.md:  Repeat page 003 panel 4  ->  panel 5
content/pages/043.md:  Panel 2A rhymes deliberately with page 003 panel 4  ->  panel 5
```

Page 036 is the chapter that deliberately re-draws the cold open, so those three lines are
load-bearing art direction. Nothing else in either file moves — `panel 2` on page 043, which
is local to page 043, is left alone, and so is the `Panel 2A` label, whose sub-panel letter
survives its number changing.

Four files, `+15 −9`. The same operation done by hand is three files a careful editor would
have to remember exist.

## 5. Move a panel to another page, 001-02 → 002-01

```sh
python3 scripts/panels.py move 001-02 --to-page 002 --to 1 --apply
```

The test that matters, because page 001 is the only page carrying both generated art and
written prompts. The panel's script body, its three WebP versions, its prompt file, and its
three rows in `data/panel-art.tsv` all travel; both pages renumber around the hole and the
arrival.

```
Rhythm: page 001 5 -> 4 panels (default)
Rhythm: page 002 5 -> 6 panels (default)

Transfer
  001-02 -> 002-01

Notes:
- [art-transferred] 001-02: art moves to 002-01, onto a page it was not composed for;
  re-review it against the new neighbours
- [provenance-transferred] 002-01: carries its own provenance line onto a page whose front
  matter may not declare those sources; crossref will say so
```

The sentence worth watching is in a prompt file that does not move. `prompts/pages/001/panel-03.md`
opens *"Repeat panel 02's exact camera, card proportions, and diagram geometry"* — a bare
reference, local to page 001, and correct only for as long as panel 2 is on page 001. After
the transfer that file is `prompts/pages/001/panel-02.md` and the sentence reads:

```
Repeat page 002 panel 01's exact camera, card proportions, and diagram geometry.
```

Nothing else in the repository would have caught that going wrong. The reference stays
grammatical, stays plausible, and would have pointed at a different picture.

The transferred prompt keeps its own heading correct on the way over — `# Page 001 — Panel 02`
arrives as `# Page 002 — Panel 01` — because the heading is an ordinary cross-page reference
and the relocation covers it.

Sixteen tracked files, plus `assets/art/panels/002-01/` and `prompts/pages/002/panel-01.md`
arriving as new paths. `build-site.py` still letters ten panels, which is the check that the
art actually followed its key.

## 6. Move a panel across a chapter boundary, 003-04 → 036-02

```sh
python3 scripts/panels.py move 003-04 --to-page 036 --to 2 --apply
```

Page 003 is the cold open and page 036 is the chapter that deliberately re-draws it, so four
sentences on two other pages name page 003's panels. Moving one of them exercises every
reference class at once:

```
content/pages/036.md:  Repeat page 003 panel 4  ->  Repeat page 036 panel 2
content/pages/043.md:  rhymes deliberately with page 003 panel 4  ->  page 036 panel 2
```

Two warnings, neither of them mechanical:

```
- [transfer-crosses-chapter] 003-04: leaves chapter prologue for chapter 02; the beat
  changes which chapter's argument it serves
- [reference-now-self] content/pages/036.md: "page 003 panel 4" now names a panel on the
  page it sits on; the reference is true but probably wants rewriting
```

The second is the tool noticing something a careful editor would want to know and could
easily miss: page 036's instruction to *repeat* a composition now points at its own page.
The rewrite is correct — it is the sentence that has stopped making sense, and the tool says
so rather than fixing it.

## What the tests did not cover

- **No multi-panel transfer.** A cross-page move takes one panel at a time; moving a run of
  three is three operations with real intermediate states.
- **No range broken by a transfer.** `move 086-04 --to-page 087 --to 1` is refused, because
  page 086's notes say *"Panels 3–6 are the smaller corrections"* and a range that no longer
  names one page is not a renumbering. Reported and refused rather than guessed at; the
  sentence has to be rewritten first.
- **No operation on a grouped run.** Pages 006 and 007 write `## Panels 1–9`, and every
  command refuses them by design:

  ```
  page 006 writes its panels as one grouped run, `## Panels 1–9`. That is a single
  composition and a single image slot; splitting it is an editorial decision, not a
  renumbering.
  ```

- **No art-loss test applied.** `delete 001-02` was planned and refused, which is the
  behaviour worth recording; taking it would have deleted three tracked WebP files to prove
  a flag works.

---

## What these runs caught

The acceptance runs are why this section exists. They found four defects, all in the
plumbing rather than the model, and all invisible to `check` because they only appear when
an operation is actually applied.

**Zero-padding was dropped on rewrite.** `# Page 001 — Panel 02` came back as `Panel 2`. The
prose rewriter emitted `str(new_index)` regardless of what the site had used, so every padded
reference quietly lost its padding while every bare one stayed correct. It now matches the
width it found: `Panel 02` stays padded, `panel 4` stays bare.

**Renames overwrote writes.** A renamed file was written under the name it was about to
vacate, and then the staged original was moved onto the destination — so `panel-02.md`'s
rewritten content landed at `panel-02.md`, which the rename then filled with `panel-03.md`'s
*original* text. Every heading in the page's prompt tree came out wrong, and the tool reported
success. Renames now land before writes, and a renamed file's write is keyed to its
destination.

**The second defect was also in `scripts/pagination.py`**, which shares the shape.
`prompts/pages/NNN/` files name their own page, so any insertion at or before page 002 would
have rewritten them into the directory it was vacating and left the moved copies stale, plus
a stray `prompts/pages/001/` pointing at a page that had moved. Probed, confirmed, fixed the
same way, and verified: `pagination.py insert --at 001` now leaves `prompts/pages/002/` and
`prompts/pages/003/`, with `# Page 002 — Panel 01` inside the first.

**The art table's key was rewritten and its path was not.** `data/panel-art.tsv` holds both a
`NNN-II` key and a `file` column reading `assets/art/panels/NNN-II/...`. Only the key was
being renumbered, so after any move the two disagreed, `panelart.resolve` looked for a file
that no longer existed, and `build-site.py` quietly lettered eight panels instead of ten. No
validator failed. Nothing was reported. The book simply had two fewer lettered images, and
the only visible trace was a number in a build line that nobody reads.

This one is worth dwelling on, because it is the exact failure mode the tool exists to
prevent, reproduced inside the tool: a mechanical consequence of renumbering, silently
mishandled, with the damage showing up somewhere nobody was looking. It was caught by asking
why a count in `build-site.py`'s output had changed — not by any check. `panels.py` now
relocates every key in the row rather than the one in the first column, and the lettered
count is recorded in the results table above so a future regression has somewhere to show up.

It was also present in the single-page `move` that shipped in the first commit, so the fix
matters beyond the cross-page work.

**The range check only looked at the ends of the range.** `Panels 3–6` is written with two
numbers and names four panels. Taking panel 4 to another page left both endpoints on page
086, so the split went undetected and the sentence would have silently come to mean
something else — a range with a hole in it, still reading as continuous. Found by writing
down a claim about the tool's behaviour and then running the command to check it, which is
the only reason it is not still there. The check now resolves every index inside a span, not
just the two that are written.
