---
id: FQ-08
kind: faq
audience: method
title: What do the provenance labels on the pages mean?
pages: [014, 088, 090]
answer: >-
  Each panel carries a status — `documented`, `source-paraphrase`, `disputed`, `inferred`,
  `reconstructed`, or `invented` — and a key naming the source it rests on. The label says
  where a claim came from, not how confident the book is in it, and a validator fails the
  build when a page's declarations and its panels disagree.
---

## The short answer

Six statuses, in descending order of how much of the claim the record carries:

| Status | What it means |
| --- | --- |
| `documented` | A published source states this. The key names which one. |
| `source-paraphrase` | A published source states this in its own words; the book paraphrases rather than quotes. |
| `disputed` | Two sources state incompatible versions, and the book shows both. |
| `inferred` | This project drew the conclusion from cited events, and the page shows the reasoning. |
| `reconstructed` | Connective material — a room, a moment, an exchange — built to carry a documented decision without claiming to have observed it. |
| `invented` | No claim of correspondence to anything that happened. |

The key beside the status names the source: `METR` for the independent investigation,
`OAI-TR` for OpenAI's technical report, `OAI-BH` for the Black Hat talk, `HF-TL` for Hugging
Face's timeline, `PROJECT-INFERENCE` for the book's own reasoning, `NONE-FICTION` for
invention. The full list is in `research/scene-provenance.md`, the labels are searchable on
the published site's cross reference, and the book's endmatter prints the vocabulary as a
key so a reader who skipped the page notes can decode the panels on the way out.

## The long answer

The important thing about the labels is what they do not do. `documented` is not a
confidence rating. A documented claim can be wrong: it means an organisation published it,
and organisations publish things about their own incidents for reasons. `inferred` is not a
lower grade of `documented`; it is a different kind of object, and some inferences in this
book are better supported than some documented statements in the sources.
[PR-43](#pr-43-provenance-labels-are-source-descriptions-not-confidence-statements) is a
practitioner's objection to exactly this, and it is a fair one: the labels tell you where a
claim came from, and a reader who wants to know whether to believe it still has to do the
rest of the work. That is what the rest of this appendix is for.

The apparatus is enforced rather than aspirational. A page's front matter declares its
provenance statuses and source keys; each panel carries a `**Provenance:**` line; every key
must be registered in `research/scene-provenance.md` or a chapter source packet; and
`crossref.py check --strict` fails when any of those disagree. That is why the labels can
be trusted to be complete even where they are unflattering — nobody has to remember to add
one.

Page 088 is where this becomes part of the story rather than apparatus around it. Having
spent a chapter arguing that a bounded finding turns into an unbounded claim when the
qualifier is too quiet to survive retelling, the book applies the diagnosis to its own page
064 and takes responsibility for it. Provenance as an action, in the page's own title,
rather than a notice.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Project record | [research/scene-provenance.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/scene-provenance.md) | 2026 | The citation keys, the sequence ledger, and the safest evidentiary treatment for every planned scene. |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | That a page script may narrow a claim's status but may never silently upgrade it. |
| Where it is enforced | [CLAUDE.md](https://github.com/curtcox/zz-no-consumer/blob/main/CLAUDE.md) | 2026 | The invariant that provenance is checked by tooling, and the command that fails the build on drift. |
| The book applying it to itself | [content/pages/088.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/088.md) | 2026 | The disclosure page for page 064, where the apparatus becomes an action in the story. |
| Field standard | [Wikipedia's verifiability policy](https://en.wikipedia.org/wiki/Wikipedia:Verifiability) | — | The older version of the same idea: the threshold is attribution to a published source, not truth. |
| Field practice | [SPJ Code of Ethics](https://www.spj.org/ethicscode.asp) | 2014 | Identifying sources and distinguishing fact from inference as a working obligation. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The source most `documented` labels in the first half of the book resolve to, and its own statements about its limits. |
