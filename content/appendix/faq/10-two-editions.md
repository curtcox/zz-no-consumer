---
id: FQ-10
kind: faq
audience: method
title: Why is there both a graphic novel and a novella?
pages: [001, 105, 114]
answer: >-
  Because the same story answers different questions in the two forms, and because a comic
  is expensive to read on a phone and a prose file is expensive to read as a page turn.
  They share one pagination — page 045 is page 045 in both — so a reader holding either can
  use this appendix, and every citation in either edition resolves in the other.
---

## The short answer

One story, two renderings, one set of page numbers.

The graphic novel is the primary text. It is built page by page and panel by panel, with
recto and verso load-bearing: a reveal prepared at the end of an even page lands on the odd
page beside it, which the reader can already see, and a turn prepared at the end of an odd
page lands on the page behind the leaf, which is hidden until the leaf moves. Those are
different devices and the book names them separately.

The novella is the same events in prose, one file per story page, in chapter directories
mirroring the script's. It carries what a panel cannot: the sentence that has to be read
slowly, the qualifier that would not fit in a caption, the transition between two moments
that a gutter leaves implicit.

Neither is a summary of the other. Where they diverge in meaning, that is a defect, and no
tool catches it — the coverage validator can prove every page has prose and cannot tell
whether the prose says the same thing.

## The long answer

The shared pagination is the design decision everything else follows from, and it is worth
being explicit about why.

An appendix keyed to a page number is only useful if the page number means one thing. This
project makes the three-digit story page number the primary key of the entire tree: page
045 is [page 045](../../novella/03-control-keeps-solving-problems/045.md) in the script, in the prose, in this appendix, in the beat sheet, in the art
keys, in the generated site routes, and in every sentence of hand-written prose that cites
it. That is what lets 107 appendix entries serve two editions at once, and it is why no page
number in this repository is ever edited by hand — a single tool rewrites every occurrence
in one operation, and refuses to change the book's parity without being told to.

The practical consequence for a reader is that the four novella downloads — EPUB,
self-contained HTML, Markdown and plain text — each carry the full appendix with the same
page numbers and the same links. The EPUB carries the page numbers as real page breaks. The
plain-text build prints every URL in full rather than dropping it, because an appendix whose
purpose is to point at evidence must not throw the pointers away because the format has no
anchors.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | The physical page assumptions, the recto/verso parity rule, and the distinction between a reveal across the gutter and a turn across the leaf. |
| Where it is enforced | [CLAUDE.md](https://github.com/curtcox/zz-no-consumer/blob/main/CLAUDE.md) | 2026 | The page number as primary key across six trees, and the invariant that it is never edited by hand. |
| Tooling record | [scripts/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/scripts/README.md) | 2026 | The pagination, prose-coverage and site-build tools, and what each of them owns. |
| Project record | [content/page-plan.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/page-plan.md) | 2026 | The beat sheet both editions are drawn from, page by page. |
| Field practice | [EPUB page-list practice, via the published downloads](https://github.com/curtcox/zz-no-consumer) | 2026 | Real page breaks in the EPUB, so a citation to [page 045](../../novella/03-control-keeps-solving-problems/045.md) lands in a reading app as well as on paper. |
| The reason it matters here | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The evidentiary record the page-level citations resolve to; a citation scheme that broke between editions would break the book's central promise. |
