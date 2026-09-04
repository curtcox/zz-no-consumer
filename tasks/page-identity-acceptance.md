# Acceptance record — page insertion, deletion, and movement

All four operations run against a clean tree at `d7815cf`, each reset before the next. For
each: the tool's own plan, then `--apply`, then `paneltypes.py write` and `build-site.py`,
then all four validators plus `pagination.py check`.

Reproduce any row by running the command shown, then the two regeneration commands. The
tree is left unchanged by this document; nothing here is committed.

## Results

| # | Operation | Parity | Validators | `crossref --strict` | Source diff |
| ---: | --- | --- | --- | ---: | --- |
| 1 | insert one page mid-Chapter 3 | **inverting** | 4/4 green, 113 pages, 1,339 routes | 71 | 95 files, +2,653 −2,617 |
| 2 | delete one page mid-Chapter 5 | **inverting** | 4/4 green, 111 pages, 1,323 routes | 70 | 59 files, +1,316 −1,410 |
| 3 | move the last page of Chapter 1 to the start of Chapter 2 | preserving | 4/4 green, 112 pages, 1,335 routes | 71 | 8 files, +12 −12 |
| 4 | insert two pages at a chapter boundary | preserving | 4/4 green, 114 pages, 1,343 routes | 71 | 85 files, +2,429 −2,357 |

"4/4 green" is `validate-continuity.py`, `validate-production-foundations.py`,
`crossref.py check`, and `validate-viewer.py`, all exit 0. The strict cross-reference
baseline of 71 findings never increases; test 2 lowers it to 70 because the deleted page
carried one. Existing panel art moved with its page in every renumbering test — git detects
the four `assets/art/panels/109-*` files as pure renames to `110-*`, and
`data/panel-art.tsv` keys follow.

`pagination.py check` is red after tests 1, 2 and 4 by design. That is the work list, and it
is the point of the exercise: two of these operations are not safe, and the repository says
so until a human resolves them.

---

## 1. Insert a page mid-Chapter 3

```sh
python3 scripts/pagination.py insert --at 048 --chapter 03 --sequence 17 \
    --title "Inserted Test Page" --allow-parity-shift --apply
```

Without `--allow-parity-shift` the tool prints the same report and exits 1 with:

> Refused: this operation inverts recto/verso for 65 pages. The findings above are the work
> list. Re-run with --allow-parity-shift to take it deliberately.

Applied: 65 pages renumbered, 1 created, 91 files written, 65 removed, 2 art directories
renamed. Reported and **not** fixed:

- **46 invalidated parity assertions**, every one an `error` because they are `**Frame:**`
  art direction. For example `content/pages/064.md:35` — *"Verso. Eleven active coordination
  lanes…"* — becomes page 065, a recto.
- **11 broken page turns**, including `064 → 065` ("Coordinator silence → organization
  persists through artifacts") becoming `065 → 066`.
- 4 soft choreography lines on pages that changed side.
- 1 assertion incidentally repaired: `content/pages/099.md` claims Verso and is wrong today;
  at 100 it becomes right.
- 2 historical records named but not rewritten.

Mechanically correct afterwards: sequence 17's ledger range widens `48–51 → 48–52` while 18
shifts `52–55 → 53–55`; Chapter 3 becomes `41–57`; the beat sheet gains a placeholder row in
the Chapter 3 section; page 087 (was 086) now reads *"the qualifier on page 065 was accurate
and deliberately small"*, following the page it points at.

## 2. Delete a page mid-Chapter 5

```sh
python3 scripts/pagination.py delete 079 --allow-parity-shift --apply
```

Applied: 33 pages renumbered, 1 deleted. Reported and not fixed:

- **1 dangling parity assertion** — `content/pages/079.md:35` claims page 079 is recto, and
  079 is the page being deleted.
- **5 dangling prose references** to a page that will no longer exist, in
  `content/pages/088.md`, `content/production-review.md`, and three places in
  `research/chapter-source-packets/05-the-observer-needs-the-observed.md`. The references are
  left as written; renumbering them to something else would have been a lie.
- **14 invalidated parity assertions** and **6 broken turns**, including `104 → 105`
  ("Incident becomes artifact → manuscript assembly") becoming `103 → 104`.

## 3. Move a page from the end of Chapter 1 to the start of Chapter 2

```sh
python3 scripts/pagination.py move 029 --chapter 02 --sequence 12 --apply
```

Page 029 already sits immediately before Chapter 2, so this is a membership change, not a
renumbering: 0 pages move, parity is untouched, and the whole thing is 8 files and 12 lines.

```
content/chapters/01-first-civilization.md   - **Pages:** 16–29   →  16–28
content/chapters/02-erasure-and-return.md   - **Pages:** 30–40   →  29–40
content/page-plan.md                        row 29 moves to the Chapter 2 section, seq 11 → 12
content/pages/029.md                        chapter: "01" → "02", sequence: 11 → 12
content/story-contract.md                   map rows 16–29/30–40 → 16–28/29–40
data/chapters.yaml                          last_page 29 → 28, first_page 30 → 29
data/pages.yaml                             manifest row 029 reassigned
research/scene-provenance.md                seq 11 range 28–29 → 28, seq 12 range 30–32 → 29–32
```

Nothing else in the tree changed, because nothing else needed to. The only finding is the
pre-existing one on page 099.

This is the shape the task was asking for: an editorial decision that costs eight lines
instead of a renumbering.

## 4. Insert two pages at a chapter boundary

```sh
python3 scripts/pagination.py insert --at 057 --chapter 04 --sequence 20 \
    --title "Boundary Page A" --title "Boundary Page B" --apply
```

The case most likely to break spread and turn rules, and the one that shows why an even
insertion is not automatically safe. 56 pages renumbered, parity **preserving**, so 9 of the
11 turns after the insertion point simply renumber and keep working:

```
- [turn-renumbered] 064 → 065: becomes 066 → 067 and still turns
- [turn-renumbered] 066 → 067: becomes 068 → 069 and still turns
  … seven more …
```

One turn does not survive, and it is exactly the one that straddled the insertion point:

```
- [turn-broken] 056 → 057: becomes 056 → 059, which is not an even-to-odd turn:
  No human page → reset becomes collective experiment
```

Two pages were inserted *between* an outgoing beat and its landing. No amount of correct
renumbering repairs that; only an editor can decide whether the Chapter 3 → Chapter 4
transition still works. That finding is the entire justification for the tool reporting
relations rather than positions.

## Standing findings on the unmodified tree

`python3 scripts/pagination.py check` on a clean tree reports two errors and one warning, all
pre-existing and all editorial. They are described in `README.md` and
`design/page-identity.md` and are deliberately not fixed here: this task was infrastructure.

1. `content/pages/099.md:34` opens a panel `**Frame:** Verso.` on an odd page.
2. The `085 → 086` row of the page-turn audit is odd-to-even where every other row of the
   audit is even-to-odd.
3. The contract's two physical assumptions do not close: a recto page 1 makes each
   (even, odd) pair a facing spread, so a reveal prepared on an even page lands where the
   reader can already see it.
