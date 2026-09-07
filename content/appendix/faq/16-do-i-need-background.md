---
id: FQ-16
kind: faq
audience: story
title: Do I need to know anything about AI or security to read this?
pages: [007, 008, 044]
answer: >-
  No. The book is written for an intelligent adult general reader with no prior
  cybersecurity or AI-safety knowledge. Technical mechanics stay on the page only where they
  change access, authority, evidence, or consequence; everything else lives in the page
  notes, where you can ignore it.
---

## The short answer

The rule the drafting works to is that a mechanism earns a panel only when it changes one of
four things: who can reach what, who is allowed to do what, what can later be proved, or
what happens next. A detail that changes none of those is interesting to a practitioner and
noise to a reader, so it goes in a note.

You will meet a package cache, a message authentication code, an access token and a
container. In each case the book shows what it let somebody do before it names what it is,
and the naming is one line. If you skip every note in the book you will lose the citations
and none of the story.

## The long answer

There is a second audience, and the book is honest that it serves them differently.

A practitioner reading this will notice things a general reader will not, and several of
them are objections rather than details. Forty-five entries in this appendix are exactly
that: one trade at a time, saying what its field would have noticed that the book missed,
got wrong, or never thought to ask. An incident responder objects that the scene was rebuilt
before it was imaged. A structural engineer objects to how the book talks about failure. An
accident investigator objects to the absence of an incident commander. Those entries are
where the technical argument lives, at whatever depth the reader wants it, and they are not
required reading for the story.

The other thing a newcomer does not need is the theory. Orthogonality, instrumental
convergence and race dynamics are the book's subject, and the method is deliberately to
introduce each as an event, let it produce consequences, show a complication, and name the
idea only after the reader has already experienced it. If you finish the book able to
describe what happened and not able to name the three concepts, the book worked. If you
arrive already able to name them, the appendix has entries arguing that each is contested
in its own literature
([CA-15](#ca-15-instrumental-convergence-that-different-goals-produce-the-same-prerequisites),
[CA-16](#ca-16-orthogonality-that-understanding-an-objection-does-not-make-it-decisive)).

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | The intended reader, and the rule that technical mechanics stay on the page only where they change access, authority, evidence, or consequence. |
| Project record | [content/themes.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/themes.md) | 2026 | The thematic method: introduce as event, complicate, and name the idea only afterwards. |
| Where the depth is | [content/appendix/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/appendix/README.md) | 2026 | The professional objections, one trade at a time, as the place the technical argument is allowed to be technical. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The primary record, readable without a security background, for anyone who wants the source rather than the adaptation. |
| Background, if you want it | [The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | 16 Jun 2025 | A short, non-specialist explanation of the class of failure the incident is an instance of. |
| Background, if you want it | [Specification gaming](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) | 2020 | The plainest available account of systems satisfying the letter of an objective, with examples that need no background. |
| Deflationary | [AI as Normal Technology](https://knightcolumbia.org/content/ai-as-normal-technology) | 2025 | A readable case that this class of event does not require any special vocabulary to understand, which is a position the book takes seriously. |
