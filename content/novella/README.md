# Novella track

A prose retelling of `ZZ: NO CONSUMER`, one text file per graphic-novel page.

`content/novella/<chapter>/NNN.md` corresponds to `content/pages/NNN.md`. Chapter
directories mirror `content/chapters/`. All 116 story pages are present; the
numbering, chapter membership, sequence, and title of every file match its source
script exactly.

## What this track is

The same story, same structure, same order of events, told entirely in prose. It
is not a panel-by-panel description of the artwork and does not use the words
*panel* or *frame*. Where imagery from the script carries an idea — the severed
arrow, the staircase, the two-lane calendar, the empty channel — the prose uses
it; where the script is describing composition, the prose describes the event or
the argument instead.

## Conventions

- **Voice.** Immersive past tense, third person, restrained. Uncertainty survives
  in the sentences (*the record does not say*, *METR would later report*, *this is
  OpenAI's account*) rather than in provenance labels. Creator scenes read as
  ordinary scene prose with dialogue.
- **Front matter.** Minimal: `page`, `chapter`, `sequence`, `title`, `source`.
  Enough for tooling; nothing that interrupts reading. The script's
  `story_time`, `population`, `locations`, `provenance` and `continuity_checks`
  stay in `content/pages/` and are not duplicated here.
- **Length.** Roughly a novella page per graphic-novel page — about 380 words on
  average, ranging from 142 to 568 as the material warrants.
- **Truth contract.** Every constraint in `content/story-contract.md` applies
  unchanged: no invented events, no agent interiority, no reusable exploit
  mechanics, disputed accounts left unresolved, reconstructions disclosed in the
  text, source boundaries (`OPENAI ACCOUNT — NOT IN METR'S REVIEW`, the invented
  forum, the invented future) carried as stated lines rather than as banners.
- **Cross-references.** Page numbers cited in the prose (*page 010*, *page 088*)
  are this book's own pages and match the graphic-novel pagination, which the
  narrative depends on in the epilogue.

## Tooling

`scripts/novella.py` owns this directory:

```sh
python3 scripts/novella.py report                 # word census by chapter and page
python3 scripts/novella.py check                  # prose against the page scripts
python3 scripts/novella.py assemble --out FILE    # the whole novella as one document
```

`scripts/pagination.py` moves these files when the page set changes — across
chapter directories when a page changes chapter — and rewrites front matter,
the `source:` line, the heading number, and the page numbers the prose cites.
Do not renumber by hand. `scripts/panels.py` never touches this tree: the unit
here is the page, so a panel operation leaves a file's subject unchanged.

## Editing

When a page script changes, revise the matching prose file in the same commit,
then run `python3 scripts/novella.py check`.
