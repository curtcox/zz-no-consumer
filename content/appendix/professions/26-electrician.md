---
id: PR-26
kind: profession
profession: Licensed electrician
field: trades-and-operations
title: You do not work it live, and you do not re-energize on someone else's say-so
pages: [028, 029, 091]
conjecture: none
reading: >-
  Page 029 has responders revoking credentials, rebuilding, and erasing while the estate is
  running, and page 032 resumes workloads three days later. In a trade with lockout/tagout, both
  of those are procedure violations before they are anything else.
---

## What the practitioner would say

The rule is physical and absolute: isolate the energy source, lock it, tag it, verify zero
energy, and — the part that matters most here — every worker applies their own lock, so no
single person can restore power while anyone is still inside the equipment. Nothing in this
story is isolated. The rebuild happens on a live estate with workloads that resume on 7 July
under controls nobody outside the organisation has verified, and the decision to re-energize is
made by the same party that decided the work was finished.

The second habit the trade would miss is independent inspection. An electrician's work is
inspected by someone who does not work for the electrician, before it is closed up, against a
code the electrician did not write. Software's nearest equivalent is a colleague's review,
inside the same company, against standards the company sets. Page 091's containment montage
would read very differently to a tradesperson: it is all remediation and no sign-off.

## What the book gets wrong or omits

The book treats verification as an epistemic problem for outsiders — how would anyone check
these claims? — when in the trades it is a scheduling problem with a well-worn answer: you
cannot proceed to the next step until someone independent signs the last one. That is a
mundane mechanism, it is available, and the story's institutions have no version of it. The
absence is more interesting than the argument about whether the technical report is credible,
because it explains why the question comes up at all.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field regulation | [OSHA 29 CFR 1910.147, the control of hazardous energy (lockout/tagout)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147) | current | Isolation, verification, individual locks, and the rules for restoring energy. |
| Field standard | NFPA 70E, standard for electrical safety in the workplace | current | Energized-work permits: the narrow, documented exception when isolation is impossible. Paywalled; no public address. |
| Incident record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The 4 July response and the 7 July resumption under tightened controls. |
| Victim-side account | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | The parallel remediation on the other side of the incident. |
