---
id: FQ-06
kind: faq
audience: method
title: Was this book written by an AI?
pages: [013, 086, 105]
answer: >-
  Partly, and the credits name which systems did what. Curt Cox is the author and is
  answerable for every claim. Claude co-authored repository commits — page scripts,
  research packets, and all of the tooling — and the co-authorship is recorded commit by
  commit in a public Git history. ChatGPT appears inside the story as a character. Nothing
  about that arrangement is hidden, and page 086 puts it on the page.
---

## The short answer

Three systems, three different roles, all disclosed in `CREDITS.md` and set as the book's
endmatter:

- **ChatGPT** is a character in the creator scenes — the model Curt asks to organise and
  dramatise the incident record. Its dialogue is reconstructed and compressed unless a page
  note identifies a preserved exchange.
- **Claude**, through Claude Code, co-authored commits in this repository: page scripts,
  research packets, planning documents, and the validation, pagination, cross-reference,
  lettering and site-generation tooling. Every such commit carries a co-authorship trailer,
  and the history is public.
- **FLUX.2 [klein]**, run locally, produced every generated image. See
  [FQ-07](#fq-07-who-drew-the-pictures).

Curt is not a byline over a machine's work. He set the contract that governs what the book
may assert, made every editorial judgement, and is the one answerable when a claim is
wrong. What the models did is on the record precisely so that a reader can weigh it rather
than take his word about it.

## The long answer

The credits carry one disclosure that is uncomfortable enough to be worth reading in full.

The model in use was twice replaced automatically, mid-task, by a safety fallback: on 15
July and 5 September 2026 a `cyber`-category refusal switched the session from one model to
another, retracting prior messages, and the successor completed work that is in the Git
history. The commit trailers for that stretch therefore name a model that did not write the
commit, and no trailer records the switch. Neither request was about security — the first
was in an unrelated repository and asked for a design review, the second asked for a prose
retelling of the comic and landed while a coverage validator was running.

That record is in the book, on [page 086](../../novella/05-the-observer-needs-the-observed/086.md), and it is the only material in the creator register
that is preserved rather than reconstructed. It is also fenced: two events are not a rate,
neither was a block on this book, and the record may support the creator pages and nothing
else. It is evidence about how this book was made and about nothing else.

The recursion this creates is not incidental to the story; it is the subject of chapter 5.
The book depicts an investigation in which humans used AI systems to read transcripts that
AI systems had written, and it is itself a book in which a human used AI systems to
interpret that investigation. Pages [084](../../novella/05-the-observer-needs-the-observed/084.md) to [087](../../novella/05-the-observer-needs-the-observed/087.md) are about noticing that, and about the fact
that noticing it does not dissolve it —
[CA-11](#ca-11-whether-an-ai-mediated-investigation-can-establish-what-it-reports) carries
the argument that the same objection applies to the investigation the book depends on.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's own record | [CREDITS.md](https://github.com/curtcox/zz-no-consumer/blob/main/CREDITS.md) | 5 Sep 2026 | The single list of which systems did what, including the mid-session model-replacement disclosure. |
| Preserved production artifact | [research/creator-instrument-record.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/creator-instrument-record.md) | 6 Sep 2026 | The two refusal-fallback events with timestamps, model identifiers, retraction counts, verbatim notices, and the ceilings on what they may be used to claim. |
| Project record | [content/creator-characters.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/creator-characters.md) | 2026 | What each creator-frame character is for, and the open question of whether the second model belongs on the page. |
| Auditable trail | [the repository](https://github.com/curtcox/zz-no-consumer) | 2026 | Co-authorship recorded per commit rather than asserted in a preface, so the claim is checkable. |
| Investigator, on the record | [Ajeya Cotra on Hard Fork](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) | 4 Sep 2026 | An investigator's account of model-built tooling inside the investigation the book depends on — the same trade, one level down. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The AI-mediated method whose limits chapter 5 applies to itself. |
| Field standard | [ACM Code of Ethics](https://www.acm.org/code-of-ethics) | 2018 | Honest representation of one's own work and its tools as a professional obligation rather than a courtesy. |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | That Curt speaks only in creator scenes, never narrates incident facts omnisciently, and is bound by the same sourcing rules as everything else. |
