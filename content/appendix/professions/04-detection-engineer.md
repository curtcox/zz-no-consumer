---
id: PR-04
kind: profession
profession: Detection engineer
field: security-and-infrastructure
title: An alert that does not page is a tuning decision someone made in advance
pages: [025, 055, 056]
conjecture: marked
reading: >-
  Pages 055 and 056 present correct correlation followed by under-classification as an
  orthogonality lesson at institutional scale. A detection engineer would say the severity was
  set months earlier, by a person, against a false-positive budget, and that the book never
  looks for that person.
---

## What the practitioner would say

Detections do not assign severity. Engineers do, and they do it under a constraint the book
never mentions: how many times a week the on-call team can be woken before it starts ignoring
the channel. Every severity threshold is a trade against alert fatigue, and the trade is
usually documented in the detection's own definition — author, hypothesis, data source,
false-positive rate, tuning history, and the runbook the page would have opened. That
artifact is the missing character on page 056. Not a model that failed to escalate; a rule
someone wrote, tuned, and owned.

Page 025 is stronger, because a port sweep is exactly the kind of high-precision signal that
does page, and it did. The book has the pair right and the moral slightly wrong. What
separated the two was not comprehension. It was that one behaviour matched a narrow,
well-understood detection and the other matched a correlation whose precision nobody had
measured.

## What the book gets wrong or omits

It omits the counterfactual a detection team asks first: what would have paged? If the answer
is "an escalation rule that did not exist", the finding is a coverage gap and belongs on page
092 with the other institutional lessons. It also omits the other half of the tuning question —
what else that threshold suppressed in the same period — which is the number that would tell a
reader whether this was one bad call or a systemic setting. And it never notes that an
AI-assisted correlation engine that under-escalates is being asked to do the thing detection
tooling has always been worst at: estimating consequence rather than recognising pattern.

> **Conjecture.** No public source gives the severity model, the tuning history, or the
> escalation policy behind the Hugging Face correlation. That the threshold was a deliberate,
> documented setting rather than an emergent property of the system is this entry's inference
> from ordinary practice in security operations, not a claim about that team.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Victim-side account | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | The correlation, the severity assigned, and the page that did not happen. |
| Field practice | [Sigma, open detection rule format](https://sigmahq.io/) | current | Detections as authored artifacts with stated logic, level, and false-positive notes. |
| Field reference | [MITRE ATT&CK](https://attack.mitre.org/) | current | The technique coverage a detection programme measures itself against. |
| Comparable institutional finding | [UK AISI, incident report on unsanctioned agent behaviour](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) | 2026 | Another organisation's account of monitoring that saw and did not act. |
| Conjecture | This entry's inference that the threshold was set deliberately in advance | 2026 | Standard practice; no published severity model for this detection. |
