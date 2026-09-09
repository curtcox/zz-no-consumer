---
id: FQ-11
kind: faq
audience: method
title: Why does the book paraphrase its sources instead of quoting them?
pages: [003, 019, 088]
answer: >-
  Two reasons, and only one of them is legal. Reuse rights for several of the primary
  documents are uncertain, so the book links to the original rather than reproducing it.
  And a paraphrase that has to be written cannot hide behind a quotation's authority — the
  book has to state what it thinks a source says, in its own words, where it can be checked
  against the source.
---

## The short answer

The rule is: paraphrase, attribute, link, and keep the original at its publisher's address.

That applies to the incident reports, to the agents' own message text, and to the named
commentators. A named living critic appears in this book only as attributed paraphrase of
dated public writing, shown as text on a screen — never with a face, a body, a room, or a
line of invented dialogue. The appendix holds the same line: a fallacy entry attributed to a
real person or organisation must carry the URL and date of the statement it characterises,
and `appendix.py check` fails the entry that does not.

Exact display strings retained in the script are project-authored. The source-language
audit in `research/exact-text-permissions-audit.md` records the removal of third-party
exact strings; reproducing one would require a new, specific rights decision.

## The long answer

The uncomfortable half of this answer concerns the retained incident wordmark,
`ZZ: NO CONSUMER`. It is the book’s authored treatment of language in a documented help
request left in a shared cache — a request saying, in effect, that its task had produced
nothing usable. The original wording stays at the linked source. The project-authored
future prefix remains deliberately ambiguous, and the final chapter turns on it. Neither
mark gives the book custody of the source’s words.

The current title, *The Two Anthill Problem*, comes from a different act of interpretation.
The title FAQ attributes the kitchen image relayed by Helen Toner and distinguishes it
from this book’s invented hills ([FQ-21](#fq-21-why-is-it-called-the-two-anthill-problem)).

The second half is about what quotation does to an argument. A quoted sentence arrives with
its author's authority attached and resists being examined; a paraphrase is the writer's
own claim about what a source says, and it is falsifiable by anyone who follows the link.
Given that this book's subject is what happens when a bounded finding loses its qualifier in
retelling, writing every source claim as an exposed paraphrase is the version of the method
the book can defend. It also produces the failure mode honestly: where the paraphrase is
wrong, it is wrong in the book's voice, and the link is right there.

Sources whose redistribution terms are unresolved are handled the same way one level up.
Potentially non-redistributable originals live in a directory Git ignores; the repository
tracks only their canonical URLs and their redistribution disposition. The wiki edit corpus
is credited to its custodians and its reuse terms are recorded as an open item rather than
assumed.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Project record | [research/exact-text-permissions-audit.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/exact-text-permissions-audit.md) | 2026 | The source-language audit, the paraphrase disposition, and the list of strings the book prints exactly. |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | Attributed paraphrase for source-derived agent language, the critic rule, and the instruction to keep exact originals out of the tracked tree. |
| Project record | [content/source-links.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/source-links.md) | 2026 | The index of original publications the book links to instead of reproducing. |
| Unresolved reuse terms | [research/collusion/reuse-inquiry.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/collusion/reuse-inquiry.md) | 2026 | The wiki corpus reuse question, recorded as open rather than assumed. |
| What is not published | [data/256t-sources.tsv](https://github.com/curtcox/zz-no-consumer/blob/main/data/256t-sources.tsv) | 2026 | Canonical URLs and redistribution dispositions tracked; the originals themselves deliberately untracked. |
| Field practice | [Documentary Filmmakers' Statement of Best Practices in Fair Use](https://cmsimpact.org/code/documentary-filmmakers-statement-of-best-practices-in-fair-use/) | 2005 | The adjacent field's working norms for quoting the material a documentary is about. |
| The source most often paraphrased | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The investigation whose findings most of the book's first half restates in its own words, with the link attached each time. |
