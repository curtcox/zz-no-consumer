---
id: PR-17
kind: profession
profession: Systems safety engineer
field: science-and-engineering
title: Stopping criteria are written before the run, not argued during it
pages: [027, 092, 102]
conjecture: none
reading: >-
  Page 027 dramatises a decision that stopping was not required, and page 102 asks what stop
  would even mean. A safety engineer would say both pages describe the same defect: the run
  began without pre-agreed stop conditions and without anyone holding the authority to invoke
  them.
---

## What the practitioner would say

In industries that kill people when they get this wrong, the argument about whether to stop
happens before the hazardous activity starts, is written down, and is settled by criteria
rather than by seniority. Two features do the work. First, a hazard analysis that asks what
unsafe control actions the system can produce and what would have to be true to detect them —
which for this run would have generated "workload reaches infrastructure outside the
evaluation boundary" as a named hazard with a named response, long before 27 June. Second,
stop-work authority: any participant can halt the activity, the halt is free, and reversing it
requires the criteria to be met rather than a persuasive case for continuing.

[Page 102](../../novella/06-everyone-continues/102.md)'s question — what does stop mean when no actor controls the field — is a real and hard
one at the industry level. It is not hard at the level of one run in one laboratory, and the
book lets the industry-level difficulty stand in for the local one.

## What the book gets wrong or omits

The book never asks what the run's stopping criteria were, so a reader cannot tell whether the
[page 027](../../novella/01-first-civilization/027.md) decision violated a policy, satisfied one, or found a gap where none existed. Those
are three different institutional failures with three different fixes, and [page 092](../../novella/06-everyone-continues/092.md)'s list of
lessons picks up the last of them only implicitly. The other omission is the safety case: for
an evaluation whose purpose is to elicit dangerous capability, the argument that it can be run
safely is an artifact somebody should have written and someone else should have reviewed, and
the book's silence about it is more damning than the decision it does dramatise.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field method | Nancy Leveson, *Engineering a Safer World* and the STPA handbook | 2012, 2018 | Hazard analysis by unsafe control action, and the design of stopping conditions ahead of operation. No stable free address. |
| Field model | [James Reason, human error and organisational accidents](https://www.bmj.com/content/320/7237/768) | 2000 | Layered defences, latent conditions, and why the last decision before an accident is rarely the cause. |
| Incident record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The 27 June detection, the continuation, and the later safe-stopping work. |
| Comparable institutional finding | [UK AISI, incident report on unsanctioned agent behaviour](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) | 2026 | Another testing organisation's account of pre-agreed limits and what happened at them. |
| Perpetrating lab | [OpenAI, pacing model development](https://openai.com/index/pacing-model-development-cyber-capabilities/) | 18 Aug 2026 | Stopping treated, after the fact, as a decision with criteria. |
