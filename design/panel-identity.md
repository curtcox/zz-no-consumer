# Panel identity, insertion, and the rhythm problem

**Status:** design decision, 4 September 2026. Companion to [`page-identity.md`](page-identity.md),
which settled the same question one level up.

## The problem, restated

`page-identity.md` removed the mechanical reason not to add a page. It left the same reason
in place one level down. A page number lives in a hundred places and a tool now owns them
all; a *panel* index lives in fewer places, but none of them were owned by anything, so the
cheap way to add a beat to a full page was to grow an existing panel's **Action** line
instead of writing Panel 6. That is the same distortion — an editorial decision made by the
cost of its mechanical consequence — with a smaller blast radius.

The two costs split the same way they did for pages, but the second one is a different
animal.

**Cost A is mechanical.** A panel index appears in a `## Panel N` heading, in art keys in
`data/panel-art.tsv`, in `assets/art/panels/NNN-II/`, in `prompts/pages/NNN/panel-II.md`, in
the generated classification table and the viewer's image routes, and in forty-four
hand-written sentences that name a panel by number — twelve of which name a panel on
*another* page. Determined once you know the map. This is what a script is for.

**Cost B is not parity.** Panels have no recto and no verso; a panel index is not a physical
position. What a panel has is **rhythm** and **lettering load**, and both are properties of
the page as a whole rather than of the panel you touched.

## Measurements

Counted against the tree on 4 September 2026. Reproducible with
`python3 scripts/panels.py report`.

| Where a panel index lives | Form | Count |
| --- | --- | ---: |
| page script heading | `## Panel N` | 545 |
| page script heading, grouped run | `## Panels 1–9` | 2 pages, 18 panels |
| `data/panel-art.tsv` | key `NNN-II` | 10 keys, 24 variant rows |
| `assets/art/panels/NNN-II/` | directory | 10 |
| `prompts/pages/NNN/panel-II.md` | filename and `# Page NNN — Panel II` | 5 |
| `data/panel-types.tsv` | key `NNN-II` | 547 rows, generated |
| `docs/viewer/pages/NNN/images/II/` | route | generated |
| hand-written prose, local | `Panel 4 is the first time…` | 32 |
| hand-written prose, another page's | `Repeat page 003 panel 2` | 12 |
| code fences and inline backticks | `--panel 001-01` | 16, examples |

Three of those rows decided the design.

**The scripted panel count and the image-slot count are different numbers.** Pages 006 and
007 write a nine-panel grid as one grouped run, `## Panels 1–9`, because the grid is a single
composition and the viewer exposes it as a single image. So the book has 563 scripted panels
and 547 image slots, and the second is the one every key and route is built on. Any tool that
conflates them mis-keys two pages.

**Twelve references name another page's panel.** `Repeat page 003 panel 2` on page 036 is a
composition instruction that has to survive page 003 changing shape. A rewriter that treats
every `panel 2` as local silently breaks the reference; one that ignores cross-page forms
leaves it stale. Both are wrong, so the registry distinguishes them by grammar.

**Panel counts were hard-coded in four places and already disagreed.** `README.md` said 541
panels in four sentences and quoted a 271/78/57 route split; `scripts/paneltypes.py` said 539;
`scripts/imagegen.py` priced the whole book off `PANEL_SLOTS = 541`, which is what the
published cost tables were computed from; `content/production-review.md` said 547 and flagged
itself stale. The true figure was 547. This is invariant 7 of `page-identity.md` — *the count
is not an invariant* — never having been applied to panels.

## Decision

**Panel identity remains the ordinal index inside its page, zero-padded to two digits and
joined to the page as `NNN-II`.** The reasoning is `page-identity.md`'s, unchanged: the
number is what an editor types, the key is what joins the art table to the art tree to the
viewer route, and a slug scheme would migrate all of that to avoid a cost a script reduces to
zero.

`scripts/panels.py` owns every site in the table above and rewrites them from one map. It
also derives the panel count, and `scripts/imagegen.py` and `scripts/make-thumbnails.py` now
read it from there instead of carrying their own.

### Rhythm is to a panel what parity is to a page

Not because they are alike — they are not — but because they occupy the same position in the
design. Both are the part the renumbering cannot fix, both are stated in prose that the
machine can check but must never rewrite, and both are the reason the operation deserves to
be deliberate rather than easy.

[`page-grammar.md`](page-grammar.md) bands a page at four to six panels by default, one to
three for an establishing or revelation page, five to nine for a procedural sequence, and
reserves the nine-panel grid for convergence, scale, or repeated attempts.
[`lettering-slots.md`](lettering-slots.md) anchors four lettering slots per panel, so a fifth
element on a panel has nowhere to go, and the thumbnail wall has always flagged a page over
180 lettered words.

So the operational policy mirrors the parity policy exactly:

- Every operation reports the page's new panel count and the band it lands in.
- `plan` always prints the impact report and touches nothing.
- `apply` refuses an operation that leaves the four-to-six default unless
  `--allow-rhythm-shift` is passed, and refuses one that discards generated art unless
  `--allow-art-loss` is. With the flag it applies the operation *and* prints the work list.
- An operation never repairs lettering. It reports every panel left holding more elements
  than there are slots, every lettered element a deletion removes from the book, and every
  page left over the density line.
- Renaming a panel's art directory is reported at note level with the reason: the image was
  drawn for the old beat, and the tool has no opinion about whether it suits the new one.

`check` exits non-zero whenever the tree disagrees with itself — panel headings out of order,
a key naming a panel no script declares, a classification table out of date, a reference to a
panel that does not exist. It is green today, and it is meant to stay green: a permanently
red checker is a baseline, not a work list.

### Alternatives rejected

**Fold panel operations into `pagination.py`.** Rejected. The two tools share a shape but not
a model: pagination maps page numbers across the whole book, panels map indices inside one
page. Merging them would put a page-scoped map and a book-scoped map behind one set of flags,
and `--allow-parity-shift` and `--allow-rhythm-shift` would have to coexist on operations
where only one can apply. They import the same `crossref` model and stay separate.

**Let the tool rebalance a page that leaves its band** — moving a panel to the next page to
restore four-to-six. Rejected for the same reason `pagination.py` never rebalances chapters:
where a beat sits is the editorial decision the tool exists to serve, not one it should make.
A page that wants seven panels should have seven, and the flag is how the editor says so.

**Support moving a panel to another page.** Not rejected, not built. It is a real editorial
operation and it is the panel-level analogue of moving a page across a chapter boundary,
which turned out to be the most useful page operation. It needs cross-page art and prompt
migration and a two-page rhythm report, and it is the obvious next increment.

**Rewrite the two grouped runs into nine headings each so every page has the same shape.**
Rejected. `## Panels 1–9` records that the grid is one composition and one image, which is a
statement about the art, not a shorthand. The tool reports such a page and refuses to operate
inside it.

## The reference registry

One rule per grammar, conservative in the same way pagination's is:

- **local** — a bare `panel 4`, `Panel 5's`, `panels 3–6` in a page script or a
  `prompts/pages/NNN/` file, which is scoped to exactly one page. Rewritten when that page's
  panels move. 32 sites.
- **cross** — `page 003 panel 2`, `Page 016 panel 5`, and the `# Page 001 — Panel 02` heading
  of a prompt file. Rewritten only when the page it names changes. 12 sites.
- **key** — a bare `NNN-II` in prose. Rewritten. None outside code today.
- **example** — anything inside a code fence or inline backticks. It quotes a form rather
  than pointing at a panel, so it is reported and never rewritten. 16 sites, including the
  `--panel 001-01` command lines in `README.md` and `panel-versions.md`, and this document's
  own illustrations. Without this rule, documenting the tool corrupts the tool's input.
- **ambiguous** — a bare panel reference in a file that is scoped to no page. Reported, never
  guessed. None today.

`data/generation-log.jsonl` and `design/image-generation-options.md` are dated records of runs
that happened and are never rewritten; `data/panel-types.tsv` and `docs/` are regenerated.

## Invariants

| # | Invariant | How it holds |
| ---: | --- | --- |
| 1 | Four validators green; `crossref --strict` stays at 71 findings | `panels.py` is additive. Verified after each acceptance test; the count rises only when a new panel carries provenance its page has not declared, which is the correct editorial signal. |
| 2 | Where a beat sits stays editorially chosen | The tool never rebalances and never moves a panel between pages. |
| 3 | Panel references stay correct and readable | Prose keeps saying `panel 4`. Round-tripping is trivial because the form never changes. |
| 4 | Art and prompts follow their panel | Both are renamed with the index, and the complete old-to-new map is printed. |
| 5 | The scripted count and the slot count stay distinguishable | Grouped runs are modelled explicitly and expose one slot. |
| 6 | The panel count is not an invariant | `report` derives it; `imagegen.py` and `make-thumbnails.py` read it; prose that quotes it says when it was measured. |
| 7 | The page model is not duplicated | `panels.py` imports `crossref`, and `make-thumbnails.py` imports `panels` rather than keeping its own copy of `panel_count` and `visible_text`. |

## Known limits

- No cross-page move. See above.
- Rhythm is checked against the default band, not against the page's *kind*. The grammar
  bands an establishing page at one to three and a procedural page at five to nine, but no
  page declares which it is, so the tool cannot tell a legitimate three-panel revelation page
  from an accident. It reports the band and asks.
- The lettering check counts elements, not measured type. `letterpress.py audit` is what
  proves a slot actually fits; this tool only knows when there are more elements than slots.
- A permutation of a page's art directories is recorded by git as content changes rather than
  renames, because the filenames inside the directories are identical. The panel map printed
  by `apply` is the record of what moved where.
- Deleting a panel deletes its lettering. That is the operation working, not a bug, but it is
  reported at warning level with the word count so it cannot happen silently.
