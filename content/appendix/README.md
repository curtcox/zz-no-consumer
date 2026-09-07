# Appendix — Contested Assertions, Logical Fallacies, and Professional Objections

This appendix is addressed by story page number. The graphic novel and the novella carry the
same pagination, so an entry keyed to page 039 is an entry about page 039 in either edition,
and a reader holding one can use the appendix with the other.

It has three parts.

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

**Professional objections** are the criticisms a practitioner of one trade would make of this
book. Each entry takes one profession — incident response, structural engineering, translation,
triage, arms control, forty-five of them — and states what that field would notice that the book
missed, got wrong, or never thought to ask. The practitioner is hypothetical and every entry
says so; the objection is written in the field's own terms, and the evidence under it is real.
Where the field has published something that carries the point, the entry cites it. Where it has
not, the entry marks the claim as conjecture, in the prose and in the evidence table both, and
`check` refuses an entry that guesses without saying so or that files a guess with a source
attached. A profession entry is not a verdict on the book any more than a fallacy entry is a
verdict on a person: several of them object to something the book does deliberately, and say so.

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
python3 scripts/appendix.py report                 # census, page coverage, stance, fallacy and field spread
python3 scripts/appendix.py check                  # exit non-zero while the appendix disagrees with itself
python3 scripts/appendix.py json --out data/appendix.json
python3 scripts/appendix.py assemble --out FILE    # the whole appendix as one document
```

### Layout

- `contested/NN-slug.md` — one contested assertion, id `CA-NN`.
- `fallacies/NN-slug.md` — one fallacy, id `LF-NN`.
- `professions/NN-slug.md` — one professional objection, id `PR-NN`.

`check` refuses an entry filed under another kind's directory, and refuses an id whose prefix
does not match its kind.

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

Professions:

```yaml
---
id: PR-01
kind: profession
profession: Digital forensics and incident response lead   # unique across the appendix
field: security-and-infrastructure     # from the vocabulary in scripts/appendix.py
title: ...
pages: [029, 067, 083]
conjecture: marked                     # marked | none
reading: >-
  The objection in one or two sentences, in the practitioner's voice.
---
```

`field` comes from a fixed list for the same reason the fallacy vocabulary is fixed: so the
shape of the coverage is visible, and so a domain cannot be invented to hold one entry.

### Sections

A contested entry carries `## What the book asserts`, `## Why it is contested`, and
`## The evidence`. A fallacy entry carries `## Where it appears`,
`## Why the reasoning does not carry`, and `## The evidence`. A profession entry carries
`## What the practitioner would say`, `## What the book gets wrong or omits`, and
`## The evidence`. `check` fails on a missing one.

### Conjecture

A profession entry declares `conjecture: marked` or `conjecture: none`, and `check` holds it to
the declaration. An entry that declares `marked` carries at least one `> **Conjecture.**`
blockquote saying what it is guessing and why the guess is not evidence. An entry that declares
`none` carries neither that marker nor a `Conjecture` row. A row whose stance is `Conjecture`
must carry no URL — a claim with a source is evidence, and belongs in the table as evidence —
and those rows are exempt from the missing-address note for the same reason. Every profession
entry also needs at least one reference with a public URL: an objection with no address behind
any of it is an opinion, and `check` says so.

### The evidence table

One table, four columns, one row per reference:

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Formal defence | [Optimal Policies Tend to Seek Power](https://arxiv.org/abs/1912.01683) | 2019/2021 | … |

The **Stance** cell is the position the source occupies in the disagreement, not a quality
score. `check` requires a contested entry to carry at least two distinct stances, and warns a
contested or profession entry below four references. A row whose source cell carries no link is
allowed — some of the best evidence has no stable public address — and is reported as a note so
the gap stays visible.

### Renumbering

`scripts/pagination.py` owns the page numbers here as it does everywhere else: it rewrites
the padded references in the prose and the `pages:` list in the front matter, and
`scripts/appendix.py check` fails afterwards on any entry left pointing at a page the book no
longer has. Do not renumber by hand.
