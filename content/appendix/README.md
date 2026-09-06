# Appendix — Contested Assertions and Logical Fallacies

This appendix is addressed by story page number. The graphic novel and the novella carry the
same pagination, so an entry keyed to page 039 is an entry about page 039 in either edition,
and a reader holding one can use the appendix with the other.

It has two halves.

**Contested assertions** are claims the book makes, or reports, whose truth is genuinely in
dispute. Each entry states the assertion as the book puts it, says why it is contested, and
then sets out the best available evidence — deliberately from more than one stance, because
an appendix of contested assertions that quotes one side is not one. Where a public address
exists, the reference carries it, and every edition that can make a URL clickable does:
the web reader, the self-contained HTML, and the EPUB all render the links; the plain-text
download prints the address in full rather than dropping it.

**Logical fallacies** are pieces of reasoning that do not license their conclusion. Three
kinds appear: reasoning by characters inside the story, reasoning by this book itself, and
reasoning in dated public statements the book cites. The fault is named from a fixed
vocabulary, which is in `scripts/appendix.py` and enforced by `check`, so the appendix
cannot coin a category to win an argument.

Naming a fallacy is not a verdict on the person or the conclusion. A bad argument may reach
a true conclusion, and several entries here record exactly that: an objection that was right
about one thing and wrong about another, or a claim that survived the argument that first
supported it. Where an entry names a real person or organisation, it does so only through a
dated public statement, quoted or paraphrased, with the address of that statement attached —
the same rule `content/story-contract.md` places on the story pages. An entry never
characterises a private belief, a motive, or anything anyone said off the record.

Several entries are about this book's own reasoning, including two mistakes it made and
corrected while it was being written. Those are here for the same reason the provenance
labels are on the pages: a reader who cannot see where the argument was weak has no way to
judge where it is strong.

An entry does not settle anything. It says what is asserted, what would have to be true, and
where a reader can go to decide.

<!-- editorial -->

## Editorial conventions

Everything below this line is repository apparatus and does not appear in the book.

```sh
python3 scripts/appendix.py report                 # census, page coverage, stance and fallacy spread
python3 scripts/appendix.py check                  # exit non-zero while the appendix disagrees with itself
python3 scripts/appendix.py json --out data/appendix.json
python3 scripts/appendix.py assemble --out FILE    # the whole appendix as one document
```

### Layout

- `contested/NN-slug.md` — one contested assertion, id `CA-NN`.
- `fallacies/NN-slug.md` — one fallacy, id `LF-NN`.

`check` refuses a `contested` entry filed under `fallacies/`, or the reverse, and refuses an
id whose prefix does not match its kind.

### Front matter

Contested assertions:

```yaml
---
id: CA-01
kind: contested
layer: incident          # incident | thesis
title: ...
pages: [081, 082, 083]
status: unresolved       # unresolved | disputed | bounded | open
claim: >-
  The assertion as the book puts it, in one or two sentences.
---
```

`layer: incident` is a claim about the July 2026 events. `layer: thesis` is a claim about how
capable systems behave in general — the propositions in `content/themes.md`, which the
incident illustrates but cannot settle.

Fallacies:

```yaml
---
id: LF-01
kind: fallacy
fallacy: argument-from-ignorance     # from the vocabulary in scripts/appendix.py
title: ...
pages: [039]
attributed_to: in-story              # in-story | book | named-source
speaker: ChatGPT, creator-character
source_url: https://...              # required when attributed_to is named-source
said: 5 August 2026                  # required when attributed_to is named-source
---
```

### Sections

A contested entry carries `## What the book asserts`, `## Why it is contested`, and
`## The evidence`. A fallacy entry carries `## Where it appears`,
`## Why the reasoning does not carry`, and `## The evidence`. `check` fails on a missing one.

### The evidence table

One table, four columns, one row per reference:

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Formal defence | [Optimal Policies Tend to Seek Power](https://arxiv.org/abs/1912.01683) | 2019/2021 | … |

The **Stance** cell is the position the source occupies in the disagreement, not a quality
score. `check` requires a contested entry to carry at least two distinct stances, and warns
below four references. A row whose source cell carries no link is allowed — some of the best
evidence has no stable public address — and is reported as a note so the gap stays visible.

### Renumbering

`scripts/pagination.py` owns the page numbers here as it does everywhere else: it rewrites
the padded references in the prose and the `pages:` list in the front matter, and
`scripts/appendix.py check` fails afterwards on any entry left pointing at a page the book no
longer has. Do not renumber by hand.
