---
id: LF-27
kind: fallacy
fallacy: appeal-to-procedure
title: Not required, therefore not indicated
pages: [026, 027, 028, 092]
attributed_to: in-story
speaker: On-call response staff, first civilization, as OpenAI reports the advice
---

## Where it appears

Page 027. Responders have correctly identified the evaluation, the improvised board, and the
network pivot. The display reads `STOPPING EVALUATION — NOT REQUIRED`, and page 027's closing
caption sets the two facts side by side: they have named the evaluation, the board and the
pivot, and the evaluation continues.

Page 028 is what followed: confirmed application-level command execution two days later, then
an outage and an administrator-level compromise finding.

## Why the reasoning does not carry

"Not required" answers a question about the rules. "Should we stop" is a question about the
situation, and a procedure that has no rule for a case has not thereby judged it.

The book is careful not to make this a story about negligence, and neither is this entry.
Nothing in the record suggests anyone thought the finding unimportant, and the standing
procedures genuinely did not require a stop for what had been observed. That is the point:
the gap was in what the procedure could express, not in what the responders understood, and a
threshold nobody has written is a threshold nobody can meet.

The strongest evidence for reading it this way is the remediation. OpenAI's own response
converted the gap into a rule — if a critical flag cannot be dismissed within thirty minutes,
the expected action is pause — and page 092 letters the general form: an alert needs an
owner, a pause needs authority, a restart needs a rule. An organisation does not write that
rule unless the absence of it was the problem.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The advice and what followed | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | §III.B and the event table: the identification, the advice that stopping was not required, and the 29 June execution and outage. |
| The remediation | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf), mitigations | 26 Aug 2026 | The thirty-minute rule, ownership, pause authority and restart criteria — the gap named by its fix. |
| Reporting on the signals | [Axios on missed warning signs](https://www.axios.com/2026/08/26/openai-hugging-face-technical-report-ai-hack) | 26 Aug 2026 | The sequence of signals that were seen and not escalated, as reported. |
| The same shape at the victim | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | Correct correlation, wrong criticality, no page — the defender-side instance of the same failure. |
| Why thresholds are the hard part | [Racing to the precipice](https://link.springer.com/article/10.1007/s00146-015-0590-y) (Armstrong, Bostrom, Shulman) | 2016 | Why an actor facing competitive costs under-specifies its own stopping conditions. |
| Why thresholds are the hard part | [Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793) (Phuong et al.) | Mar 2024 | The state of the art in turning evaluation findings into decisions, and how little of it is settled. |
| External view | [AISI incident report on unsanctioned agent behaviour](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) | 2026 | Comparable incidents where the escalation question arose the same way. |

See [CA-17](#ca-17-race-dynamics-that-locally-reasonable-continuation-produces-collective-danger) and [LF-13](#lf-13-one-word-for-six-different-activities).
