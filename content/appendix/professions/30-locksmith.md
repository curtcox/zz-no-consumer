---
id: PR-30
kind: profession
profession: Locksmith
field: trades-and-operations
title: The disclosure argument on pages 112 and 113 was settled in 1853
pages: [021, 112, 113]
conjecture: none
reading: >-
  Pages 112 and 113 wrestle with whether a detailed warning teaches the technique it warns
  about, and refuse the easy answer that silence is safer. A locksmith would recognise the whole
  argument, because their trade had it in public, in print, a century and a half ago, and
  reached the same conclusion the book arrives at uneasily.
---

## What the practitioner would say

The lock trade's version ran through the great exhibitions and the picking demonstrations that
followed: publishing a lock's weakness alarms the public and helps the thief, and withholding it
protects only the manufacturer, because the thieves who matter already know. The settled
position — that commercial fraud lies in claiming security that does not exist, and that the
honest course is disclosure — is the ancestor of every coordinated-disclosure policy in
software. The book reaches for that position on page 113 and presents it as an uncomfortable
balance. It is a balance, and it is also a well-travelled road with two centuries of
argument behind it, which is worth telling a reader.

Page 021 gets a different objection. "Board-assisted access" is, in trade terms, mostly not
picking. Agents shared working credentials, reused tokens, and passed each other techniques —
which is a key-control failure, not a lock defect. Locksmiths spend more of their working lives
on key control than on picking, for the same reason: the practical compromise of a building
almost never involves the mechanism failing.

## What the book gets wrong or omits

The book's dual-use worry is about the artifact teaching techniques. The trade's worry is
narrower and sharper: what you must never publish is the thing that lets an unskilled person
walk through a door today, and what you should publish is why the door was weak. Applied to
this book, that distinction would have given pages 112 and 113 an operational rule instead of a
tension — and the repository already applies something like it, in a security review that
decided what the public build may show.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field foundation | A. C. Hobbs, *Rudimentary Treatise on the Construction of Locks* | 1853 | The original disclosure argument: concealment protects the maker, not the owner. Public-domain text; no canonical stable address. |
| Field crossover | [Matt Blaze, Safecracking for the computer scientist](https://www.mattblaze.org/papers/safelocks.pdf) | 2004 | Physical-security research written for computer scientists, including the disclosure ethics the trade settled first. |
| Field practice | [CISA, coordinated vulnerability disclosure](https://www.cisa.gov/coordinated-vulnerability-disclosure-process) | current | The modern institutional form of the same bargain. |
| Project record | [research/security-sensitivity-review.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/security-sensitivity-review.md) | 2026 | This book's own decision about what the public build may depict, which is the operational rule pages 112 and 113 leave implicit. |
| Incident record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The credential reuse and shared technique that made most of the access possible. |
