---
id: FQ-17
kind: faq
audience: objection
title: Is a book about AI risk, written with AI help, self-serving?
pages: [084, 085, 086, 087]
answer: >-
  It is at least compromised, and the book says so rather than defending itself. The reply
  it offers is not that the objection fails; it is that the same objection applies to the
  investigation the book depends on, and that the only available response in both cases is
  to publish the method and let a reader discount it.
---

## The short answer

Take the objection in its strongest form. A book warning that capable systems outrun the
oversight applied to them was assembled with capable systems, under oversight applied by one
person who is also its author, its editor and its only reviewer. If the systems shaped what
the book concluded, the book has no way to know it, and the parts a model produced most
fluently are the parts most likely to survive editing. That is not a hypothetical mechanism;
it is the mechanism the book names on [page 089](../../novella/05-the-observer-needs-the-observed/089.md) and applies to itself.

There is no clean answer to that. What there is instead is disclosure at a level that makes
the objection checkable: which systems, doing what, recorded per commit, with the tooling
and the research tree public, and with the two occasions the instrument changed mid-task on
the page.

## The long answer

The reason this is a chapter rather than a disclaimer is that the recursion is not the
book's private embarrassment — it goes all the way down.

The investigation the book relies on used analysis models to read transcripts that other
models had written. Investigators have said so publicly and described the tooling. That is
the responsible way to review 1,300 hours of machine output, and it also means the findings
passed through an instrument of the same kind as the thing being measured. Pages [075](../../novella/05-the-observer-needs-the-observed/075.md) to [080](../../novella/05-the-observer-needs-the-observed/080.md)
are about that, and
[CA-11](#ca-11-whether-an-ai-mediated-investigation-can-establish-what-it-reports) carries
the argument on both sides, including the case that the objection proves too much: applied
consistently, it would invalidate most competent review of large machine-generated corpora,
including review that has since been corroborated.

[Page 087](../../novella/05-the-observer-needs-the-observed/087.md) is titled *The Same Trade*, and that is the honest position. The book is not
claiming to have escaped the problem it describes. It is claiming that the trade — accept a
mediated instrument, disclose it, bound what it may support — is the trade the investigators
made, the trade this book made, and a trade that has to be argued about rather than
concealed.

Two things would make this answer worse and are worth naming so a reader can check for them.
If the disclosure were vaguer than the practice, it would be decoration. And if the book
used the disclosure as a shield — *we told you, so the objection is answered* — it would be
doing the thing [page 088](../../novella/05-the-observer-needs-the-observed/088.md) accuses it of elsewhere. The appendix entry that follows this one
([FQ-19](#fq-19-why-should-i-trust-a-book-that-documents-its-own-mistakes)) is about that
second failure directly.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's own record | [CREDITS.md](https://github.com/curtcox/zz-no-consumer/blob/main/CREDITS.md) | 5 Sep 2026 | Which systems did what, at the level of detail that makes the objection checkable rather than rhetorical. |
| Preserved production artifact | [research/creator-instrument-record.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/creator-instrument-record.md) | 6 Sep 2026 | The two mid-task instrument changes, with their verbatim notices and the explicit ceilings on what they may be used to argue. |
| Investigator, on the record | [Ajeya Cotra on Hard Fork](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) | 4 Sep 2026 | An investigator describing model-built tooling inside the investigation — the same trade, made by people with more standing to make it. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) · [propensities method](https://metr.org/blog/2026-07-28-investigating-ai-propensities-after-incidents/) | Jul–Aug 2026 | The AI-mediated method and its published limits. |
| The objection, formalised | [Reasoning models don't always say what they think](https://www.anthropic.com/research/reasoning-models-dont-say-think) | 2025 | Evidence that a model's stated reasoning is not a reliable account of its processing, which is what makes the objection bite. |
| The objection, generalised | [LLM-as-a-judge, and its biases](https://arxiv.org/abs/2306.05685) | 2023 | Measured failure modes of using models to evaluate model output, including the ones that favour fluency. |
| Skeptical commentary | [The Register, the industry that built the problem](https://www.theregister.com/security/2026/08/28/industry-that-built-the-problem-offers-to-sell-you-the-solution/5293207) | 28 Aug 2026 | The general form of this objection, aimed at institutions with far more to gain from it than this book has. |
| The book applying it to itself | [content/pages/089.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/089.md) | 2026 | Selection pressure named as a defect of this book's own production, not only of its subject. |
