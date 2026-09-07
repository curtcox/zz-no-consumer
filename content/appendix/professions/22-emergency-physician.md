---
id: PR-22
kind: profession
profession: Emergency physician
field: medicine-and-health
title: Under-triage is a measured rate, not a moral event
pages: [025, 026, 056]
conjecture: marked
reading: >-
  Page 056 shows a system that understood an attack and did not summon anyone, and reads it as
  understanding without prioritisation. An emergency physician would recognise under-triage —
  which their field treats as an expected, quantified, audited rate with an agreed acceptable
  value, not as a failure of comprehension.
---

## What the practitioner would say

Triage is explicitly a sorting error problem. Set the threshold to catch every serious case and
you flood the department with the well; set it to protect capacity and you will, at a known
rate, send someone home who should have stayed. Trauma systems therefore publish a target
under-triage rate, review every case that missed it, and treat the review as routine rather
than as scandal. The question page 056 invites — how could it see and not act? — has a
deflating clinical answer: because someone chose a threshold, and thresholds have a false
negative rate by construction.

What a physician would want from the book is the audit. Was this miss reviewed? Was it inside
the expected rate or far outside it? Were there other misses that month, and did the review
change the criteria? Page 025's alert did page someone, which means the system had a working
escalation path — so the interesting comparison is between two triage decisions by the same
institution, one correct and one not, and the book uses only the second.

## What the book gets wrong or omits

The book has no equivalent of the resuscitation-room hierarchy: one person, at any moment, who
owns the patient. Its response scenes have people who understand and people who decide, and no
role that both understands and can commit resources. That is the structural difference between
pages 026 and 056 and any emergency department, and it is more explanatory than the theme the
pages carry.

> **Conjecture.** No public source gives an alert-review process, a miss rate, or a
> retrospective for the Hugging Face detection. That such a review is standard practice is a
> fact about emergency medicine, not a claim about what that security team did or did not do.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field standard | American College of Surgeons Committee on Trauma, *Resources for Optimal Care of the Injured Patient* | current | Published under-triage and over-triage targets, and mandatory review of misses. Paywalled; no public address. |
| Field standard | Emergency Severity Index implementation handbook | current | Five-level acuity assignment with explicit resource prediction; the anatomy of a triage threshold. No stable public address. |
| Incident record | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | The correlation, its severity, and the absence of a page. |
| Incident record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The 27 June alert that did reach humans, for the comparison the book does not make. |
| Conjecture | This entry's assumption that no published miss review exists | 2026 | Nothing in the record describes one; absence of a published review is not absence of a review. |
