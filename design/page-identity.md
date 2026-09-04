# Page identity, insertion, and the parity problem

**Status:** design decision, 4 September 2026. Written before the tooling, per `tasks/page-identity.md`.

## The problem, restated

A page that belonged in Chapter 1 was folded into an existing page to avoid renumbering. The
editorial decision was made by the cost of the mechanical consequence. This note decides what
identity a story page has, and what has to happen when the set of pages changes.

Insertion has two costs, and they are not the same kind of thing.

**Cost A is mechanical.** A page number appears in a filename, in front matter, in three
manifests, in a beat sheet, in eight chapter briefs, in a sequence ledger, in panel keys, in
viewer routes, and in several hundred sentences of hand-written prose. Moving them all is
tedious, error-prone by hand, and completely determined once you know the old-to-new map. This
is what a script is for. It is not the reason insertion is scary.

**Cost B is semantic.** Story page 1 is a recto. Inserting an odd number of pages swaps recto
and verso for every page after the insertion point. The book asserts parity in prose 89 times, 71 of
them as art direction, and choreographs 21 named page turns that only work because an
even page faces an odd one. None of that is repaired by getting the numbers right.

**This note's central claim: no identifier scheme addresses Cost B, because parity is a property
of a page's position in the ordering, not of its name.** Renaming a page does not move it. The
answer to Cost B is not a naming decision; it is a checker plus an operational policy. So the
identity question should be settled on the merits of Cost A alone — which is exactly where the
obvious answer stops being obvious.

## Measurements

Counted against the tree at `fb0e112`, 4 September 2026. Method for each is reproducible with
`python3 scripts/pagination.py report`.

| Where a page number lives | Form | Count |
| --- | --- | ---: |
| `content/pages/NNN.md` | filename | 112 |
| page front matter | `page: N` | 112 |
| `data/pages.yaml` | `{id: "041", …}` + `story_pages: 112` | 112 + 1 |
| `data/chapters.yaml` | `first_page` / `last_page` | 16 |
| `content/page-plan.md` | beat row `\| 41 \|` | 112 |
| `content/story-contract.md` | canonical map rows | 8 |
| `content/chapters/*.md` | `**Pages:** 16–29` | 8 |
| `research/scene-provenance.md` | ledger `Target pages` | 39 |
| `research/chapter-source-packets/*.md` | `supports story pages 016–029` | 8 |
| `data/panel-art.tsv` | panel key `NNN-II` | 24 rows |
| `assets/art/panels/NNN-II/` | directory | 11 |
| `data/panel-types.tsv` | panel key `NNN-II` | 547 rows, generated |
| `docs/viewer/pages/NNN/…` | route | 1,335 routes, generated |
| `scripts/validate-continuity.py` | `EXPECTED_CHAPTERS`, `range(1, 113)` | 8 + 3 |
| `scripts/build-site.py` | literal `112` in generated copy | 4 |
| page script heading | `# Page NNN` | 113 |
| **hand-written prose, padded form** | `page 003`, `pages 019–021`, `page-003` | **376 + 131 + 27** |
| hand-written prose, bare form | `page 3`, `printed pages 6–8` | 37 |

Two of those rows are the interesting ones.

**The scripts are reference sites.** `validate-continuity.py` hard-codes all eight chapter page
ranges and asserts `list(range(1, 113))` three times; `build-site.py` writes the literal `112`
into four strings of generated copy. The validators currently enforce the 112-page count as if
it were an invariant. The brief says explicitly that it is not one. Any tooling that renumbers
pages while the validator hard-codes the old numbers is stillborn.

**Not every "page N" is a story page.** Thirteen references in the tree name printed pages of the
OpenAI technical report — `printed pages 6–8`, `printed page 35` — including four inside page
scripts, three of them in `**Provenance:**` lines. A rewriter that treats `pages 6–8` as a story reference
silently falsifies a citation. This single fact drives the reference-registry design below.

### The parity population

| Kind of parity dependence | Where | Count |
| --- | --- | ---: |
| Art direction: `**Frame:** Recto.` / `**Frame:** Verso.` | page scripts | 71 pages |
| Self-assertion: `- Page 020 is verso; the next recto shows…` | page notes | 17 pages |
| Assertion about another page: `recto page 003` | page notes | 2 |
| Named load-bearing turns | `content/production-review.md` | 21 |
| Global parity rule | contract, beat sheet, draft-readiness, page-grammar | 4 statements |

88 distinct pages carry at least one parity word. Checking all 89 in-script assertions against
arithmetic today finds **one that is already wrong**: `content/pages/099.md` line 34 opens
`**Frame:** Verso.` and 99 is odd, so it is a recto. Nobody caught this by reading. That is the
first argument for the checker, and it is independent of whether any page ever moves.

## Decision

**Story page identity remains the ordinal page number, zero-padded to three digits.** No stable
slugs, no UUIDs, no `order:` field. What changes is that the number stops being maintained by
hand: a single tool owns every site where it appears, and rewrites all of them atomically from
one old-to-new map.

Alongside it, and carrying the actual weight of this task, a parity and choreography model that
is checked on every run and re-checked after every operation, and that **reports** rather than
repairs.

### Why numbers keep the identity

1. **Prose readability is an invariant** (brief, invariant 3). `page 003` is the natural way a
   comics script refers to a page, it is what an editor types, and it survives a rewrite
   perfectly because the padded three-digit form is unambiguous — every one of the 376 padded
   occurrences in the tree is a story reference, and none of the thirteen `printed page`
   citations use it. A
   slug scheme has to either replace those with tokens (`[[no-consumer]]`), which degrades the
   source, or build a round-tripping renderer, which is strictly more machinery than the
   renumberer it was supposed to replace.
2. **Panel identity is an invariant** (invariant 4). `NNN-II` keys join `data/panel-art.tsv`,
   `data/panel-types.tsv`, `assets/art/panels/NNN-II/`, and 1,335 viewer routes. Under stable
   IDs every one of those changes shape in a one-time migration and the art directories move
   anyway. Under ordinal identity they move only when the page actually moves, and the tool
   emits the old-to-new mapping as an auditable artifact.
3. **The number is the thing the book is about.** Parity, spreads, and page turns are all
   properties of the number. Hiding the number behind a generated layer does not remove those
   properties; it removes the reader's and the checker's view of them. The 89 hand-written
   parity assertions would become statements about a value that no longer appears in any file a
   human edits.
4. **The cost being avoided is Cost A**, and Cost A is fully automatable. Paying a 112-file
   migration and a permanent readability tax to avoid a cost a script already reduces to zero is
   a bad trade.

The one genuinely good idea in the stable-ID camp is *auditability of the mapping*. That is
adopted without the rest of it: every `apply` writes the complete old-to-new page map and the
complete panel-key map to stdout, so art migration and review have a record.

### Alternatives rejected

**Stable identifiers with numbers generated at output time.** Rejected. It solves Cost A, which
a script already solves, at the price of degrading hand-written references, migrating every
panel key and art directory, and putting the page number outside the editable source. It leaves
Cost B untouched: after an odd insertion, 89 prose assertions are still false and 21 turns are
still broken. You would still need everything in the second half of this note, plus a migration
an order of magnitude larger.

**Make the spread the atomic editorial unit, so insertions are always even.** Rejected as the
whole answer, adopted as the default. It is a real constraint that would genuinely eliminate
parity inversion — but the brief's own acceptance tests require deleting a single page mid-Chapter
5 and moving one page across a chapter boundary, and the ask is that pages be addable and
removable "on editorial grounds alone." Forbidding odd operations replaces one distortion of
editorial judgment with another. The right posture is that **odd operations are legal and
expensive, and the tool prices them** — the price being a printed work list, not a refusal. So
parity-preserving is the default and parity-inverting requires `--allow-parity-shift`.

**Flex pages that absorb a parity shift.** Rejected. A page whose only job is to absorb parity is
a blank page, and inserting a blank page is itself an editorial act with a cost the editor should
choose deliberately rather than have a script choose for them. It also adds a third kind of
structural object to a contract that currently has exactly two — the page and the sequence — for
the sole benefit of hiding a consequence that should stay visible.

**Stop hard-coding parity in prose; derive it into generated output only.** Rejected as a
migration, adopted as a forward rule. Rewriting 89 assertions is changing editorial content,
which the brief forbids as a non-goal. And `**Frame:** Recto.` is not boilerplate that a
generator could re-emit: it is art direction about which side of the gutter the composition sits
on, where the eye enters, and which margin the binding eats. Going forward, page scripts created
by the tool carry no hard-coded parity, and the checker treats every existing hard-coded parity
as a *maintained assertion* — something a human owns and the machine verifies — never as truth.

**Use the sequence as the unit of insertion instead of the page.** Not a rival; already true where
it matters. The sequence ledger stores ranges, so an insertion inside a sequence widens exactly
one range and shifts the rest. That is mechanical, and the tool does it. Sequences do not help
with parity, because a sequence of odd length inverts parity exactly like an odd page count does.

## How parity is actually handled

Parity dependence is not one problem. It is three, and they need different treatment.

### 1. Assertions — verifiable, so verify them always

The 89 in-script parity claims are statements of arithmetic in three recognizable grammars:

```
**Frame:** Recto.                     # art direction, 71 pages
**Frame:** Verso. …                   #
- Page 020 is verso; …                # self-assertion in page notes, 17 pages
… recto page 003 …                    # assertion about another page, 2
```

`pagination.py check` evaluates every one against `page % 2`. This runs on the current tree, not
just after an operation, and it fails today on page 099. Assertions are **never** rewritten: an
assertion that disagrees with arithmetic is either a stale note or a real editorial intent that
the numbering broke, and only a human can tell which.

### 2. Choreography — relational, so compute what survived

A page turn is a relation between two pages, not a property of one. The turn `002 → 003` works
because 2 is verso, 3 is recto, and they are consecutive. Under a renumbering map `M`, that turn
survives if and only if `M(3) = M(2) + 1` and `M(2)` is even — that is, if both endpoints shift by
the same even amount.

For every operation the tool evaluates all 21 named turns in `content/production-review.md`'s
audit and reports each as `intact`, `renumbered` (the relation holds, the labels moved), or
**`broken`** (the relation no longer holds). It also collects the softer choreography sentences —
`prepares the … on page 003`, `the next recto shows`, `the turn to page 013` — and lists the pages
carrying them whose parity changed.

The tool cannot tell you whether a broken turn still works dramatically. It tells you exactly
which turns changed shape, and stops.

### 3. Composition — highest severity, because art follows it

`**Frame:** Recto.` on 71 pages is an instruction to an artist, and 11 panel directories already
hold generated art. A parity inversion does not merely make 71 sentences false; it points 71
pages of art direction at the wrong side of the gutter. These are reported at `error` severity
even when everything else is clean, and the report names them page by page with the line number.

### The operational policy

- Every operation is classified before it runs. **Parity-preserving** means every page's shift is
  even. **Parity-inverting** means some page's shift is odd.
- `plan` always prints the impact report and touches nothing.
- `apply` refuses a parity-inverting operation unless `--allow-parity-shift` is passed. With the
  flag, it applies the operation *and* prints the full work list of invalidated assertions, turns
  and compositions.
- `check` exits non-zero whenever the tree's assertions disagree with its arithmetic. So an
  editor who takes a parity shift knowingly cannot forget about it: the repository stays red
  until the work list is worked.

That is the whole answer to the trap. The tooling does not make an odd insertion safe. It makes
an odd insertion *legible*, immediately, exhaustively, and repeatedly until it is resolved.

### Spreads

The contract permits two-page spreads and forbids them from crossing chapter boundaries, but no
page currently declares one, so the rule is unenforceable. The tool adds an optional
`spread: <first-page>` front-matter field and checks declared spreads for verso/recto pairing and
chapter containment. Nothing in the tree uses it yet; it costs one check and makes an existing
contract rule real.

## The reference registry

One declarative table maps every reference site to a grammar and a rewrite rule. The registry is
conservative in a specific way that follows directly from the `printed pages 6–8` problem:

Every match falls into exactly one of four classes.

- **`reference`** — rewritten. Padded three-digit forms: `page 003`, `pages 019–021`,
  `pages 003, 004 and 036` (including the 131 continuation numbers after a comma, `and`, or a
  dash), `page-003`, `story pages 016–029`, and the `page-003`-style slugs inside
  `continuity_checks`. 376 head sites plus their continuations, all unambiguously story
  references.
- **`foreign`** — never rewritten. `printed page(s) N` is excluded by an explicit negative rule
  applied before any other match. 13 sites.
- **`rule`** — never rewritten. Statements about an ordinal position in the abstract rather than
  about a particular page: `Story page 1 is a right-hand recto`. These stay true no matter what
  moves, because they describe the first page, not a page that happens to be first. 3 sites.
- **`ambiguous`** — reported, never guessed. Bare one- and two-digit forms that are not `foreign`
  or `rule`. There are 21: 17 in planning-document prose and 4 inside
  `scripts/validate-continuity.py`. The migration resolves all 21 — the prose by normalizing to
  the padded form, the script by deriving its numbers instead of hard-coding them — leaving the
  ambiguous set empty. **No page-script prose is normalized**, because that would be editorial
  content; no page script contains a bare story reference.
- Structured sites — front matter, manifests, ledger ranges, beat rows, chapter briefs, panel
  keys, art directories — are rewritten by their own parsers, not by prose regexes.

Anything the registry cannot classify is reported, never guessed.

## What the migration does

Separate commit, mechanical, no editorial content changed.

1. `scripts/validate-continuity.py` derives the chapter map from `data/chapters.yaml` and the page
   count from `data/pages.yaml` instead of hard-coding `EXPECTED_CHAPTERS` and `range(1, 113)`.
   Every existing check is kept; only the source of the numbers changes.
2. `scripts/build-site.py` derives its four literal `112`s.
3. The 17 bare story-page references in planning-document prose are normalized to the padded
   form. Page-script prose is untouched. The three parity *rule* statements and the thirteen
   `printed page` citations are left exactly as they are.
4. `content/story-contract.md`, `README.md` and `content/draft-readiness.md` are updated to
   describe the new reality: the page count is a measurement, not a contract, and page structure
   changes go through the tool.

## Invariants

| # | Invariant | How it holds |
| ---: | --- | --- |
| 1 | Four validators green; `crossref --strict` stays at 71 findings | `pagination.py` is additive; the migration only changes where existing checks read their numbers. Verified after each acceptance test. |
| 2 | Chapter boundaries and sequence membership stay editorially chosen | The tool never rebalances. `insert` requires an explicit `--chapter` and `--sequence`; `move` requires an explicit destination. Ranges shift only to keep the pages the editor named. |
| 3 | Cross-references stay correct and readable | Prose keeps saying `page 003`. Nothing becomes a token. Round-tripping is trivial because the form never changes. |
| 4 | Panel identity survives | Panel keys and `assets/art/panels/NNN-II/` are renamed together with the page, and the complete old-to-new panel map is printed and recorded. |
| 5 | Manifest and page titles stay in sync | Titles are carried through the map untouched; `insert` writes the same title to both files. |
| 6 | Provenance and citation-key joins keep resolving | `pagination.py` builds its model by importing `crossref.py` rather than reparsing, so sequence ranges and citation keys move through the same model that validates them. |
| 7 | 112 is not an invariant | The migration removes the hard-coded count from both scripts and demotes it in the contract to a measurement. |

## Known limits

- The tool decides nothing dramatic. It cannot tell a stale parity note from a broken page turn;
  it tells you the set and stops.
- No page script contains a bare story reference today, but if one is written the tool will report
  it and refuse to guess. The four bare references that page scripts do contain are source-document
  citations and are excluded by name.
- `data/panel-types.tsv` and `docs/` are regenerated, not rewritten. `apply` prints the two
  commands and `check` fails until they have been run.
- Parity inversion has no automated remedy and this note does not propose one. That is the
  finding, not a gap.
