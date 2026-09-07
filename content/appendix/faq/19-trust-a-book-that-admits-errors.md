---
id: FQ-19
kind: faq
audience: objection
title: Why should I trust a book that documents its own mistakes?
pages: [064, 088, 089]
answer: >-
  You shouldn't trust it. You should be able to check it, which is a different thing and the
  only one a book can honestly offer. The recorded errors are not a credential; they are the
  two the process happened to catch, and the useful question is what else the same process
  would miss.
---

## The short answer

There is a version of error-disclosure that is a rhetorical move: admit something small,
buy credibility, spend it on something large. The book is exposed to that charge and cannot
refute it by asserting good faith.

What it can do is make the disclosures load-bearing rather than decorative. [Page 064](../../novella/04-what-survives/064.md)
presents a ranking produced by an analysis model with a qualifier deliberately too quiet to
survive a first reading, and [page 088](../../novella/05-the-observer-needs-the-observed/088.md) discloses the construction, names the fallacy, and
takes responsibility for it. That is not a small admission offered cheaply; it is the book
demonstrating its own central claim on the reader, on purpose, and then paying for it. It is
permitted exactly once, nothing in it is false, and the disclosure is mandatory rather than
optional.

The other recorded error was involuntary. The book had reasoned that nothing crossed the
cache wipe because the cache was erased — an argument from ignorance, since model weights
are not cache state and OpenAI had said as much at Black Hat three weeks earlier. Somebody
else published the objection first. The book credits him.

## The long answer

The right way to use this appendix is adversarially.

Two documented errors out of a book this size is not a reassuring ratio; it is a lower
bound, and it says more about how many were checkable than about how many there were. The
errors that got caught share a property: they were errors about the *relationship between
sources*, which is the thing this project's tooling and research register are built to
surface. Errors of framing, emphasis, omission, and tone are not caught by any of that, and
those are the errors a single-author book with model assistance is most likely to make
([FQ-17](#fq-17-is-a-book-about-ai-risk-written-with-ai-help-self-serving)).

So the appendix is organised to be used against the book rather than in support of it. Every
contested entry is required to carry evidence from at least two stances, and the check fails
an entry that quotes one side. Every fallacy attributed to a real person must cite the dated
public statement it characterises. Forty-five professional objections say what one trade
each would notice that the book missed, and several of them object to something the book
does deliberately and say so.

The one thing that would genuinely undermine this answer is if the disclosures were
comfortable. Read [page 088](../../novella/05-the-observer-needs-the-observed/088.md) and the entry behind it, and judge whether the book chose an
error that costs it anything. That judgement is yours and the material to make it is
published.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The book applying it to itself | [content/pages/088.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/088.md) | 2026 | The disclosure of the [page 064](../../novella/04-what-survives/064.md) construction, in the story rather than in a note. |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | That the misleading construction is permitted precisely once, that nothing in it may be false, and that the disclosure is mandatory. |
| The error somebody else caught | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | The published objection that reached the book's cache-wipe error by a different route, credited on [page 039](../../novella/02-erasure-and-return/039.md). |
| The missed channel | [OpenAI at Black Hat USA 2026](https://www.youtube.com/watch?v=87DyyMV0kCY) | 5 Aug 2026 | The evidence that had been public for three weeks while the book was reasoning past it. |
| Project record | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 2026 | The register the caught errors were caught by, and the class of error it can and cannot surface. |
| Where the rules are enforced | [content/appendix/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/appendix/README.md) | 2026 | The structural requirements this appendix is held to, including the two-stance rule and the dated-statement rule. |
| Field practice | [Google SRE, postmortem culture](https://sre.google/sre-book/postmortem-culture/) | — | The argument that a record built to surface its own failures is more useful than one built to appear correct — and the conditions under which that stops being true. |
| Field practice | [NASA Aviation Safety Reporting System](https://asrs.arc.nasa.gov/) | — | A long-running instance of the same bet, with decades of evidence about what self-reported error records do and do not capture. |
