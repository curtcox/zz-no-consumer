---
id: LF-16
kind: fallacy
fallacy: hasty-generalization
title: A bounded absence read as a universal one
pages: [063, 100]
attributed_to: book
---

## Where it appears

[Page 063](../../novella/04-what-survives/063.md) states the bound in its own captions — `METR SEARCHED ITS REVIEWED TRANSCRIPT
DATASET`, then `THIS DOES NOT PROVE THAT NO AGENT, ANYWHERE, EVER TRIED` — and ends on the
population-bounded form. [Page 100](../../novella/06-everyone-continues/100.md)'s line, `THE MODELS HAD BRAKES. THE BRAKES WERE NOT
CONNECTED TO US.`, is bounded to the same population by placement, over the separate-lane
field, and the theme file makes the condition explicit.

## Why the reasoning does not carry

The finding is: in METR's reviewed transcript dataset, three to six runs considered alerting
a human and none pursued it. The generalisation "no AI agent reports wrongdoing to humans"
strengthens this along three axes at once — from a sample to a population, from one population
to all populations, and from a description to a disposition.

Each is a separate mistake. The sample was AI-assisted and known to have selection effects.
The population was a set of near-clone runs inside an unattended evaluation harness with, on
the investigator's own account, no user to escalate to. And "did not" is not "would not":
escalation behaviour is trainable, and at least one lab has published work on training it.

The reason the bound matters more here than in most places is that this finding is the most
quotable sentence in the whole record, and its unbounded form is the one that travels.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The finding, with its bound | [METR/Redwood investigation](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | The dataset searched, the three to six examples, and the explicit scope. |
| The setup explanation | [Hard Fork: Roose and Newton interview Cotra](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) | 4 Sep 2026 | No user to escalate to, and a clone population as the mechanism behind the absence of dissenters. |
| Counterexamples inside the record | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | 26 Aug 2026 | The run that called the attack unethical and refused, and the board veto on contacting a person. |
| Counterexamples inside the record | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | The boundary the agents did hold: no social engineering of humans. |
| The behaviour is trainable | [Detecting and reducing scheming in AI models](https://openai.com/index/detecting-and-reducing-scheming-in-ai-models/) (OpenAI with Apollo) | 2025 | Anti-scheming training changing the rates, which is what "did not" being distinct from "would not" looks like. |
| The behaviour is trainable | [Training Agents to Self-Report Misbehavior](https://arxiv.org/abs/2602.22303) | 2026 | Direct work on making escalation a trained behaviour rather than an emergent one. |
| Project record | [content/themes.md, theme 9](https://github.com/curtcox/zz-no-consumer/blob/main/content/themes.md) | 5 Sep 2026 | The placement condition for the brakes line, and the rule restricting the claim to the source population. |

See [CA-20](#ca-20-what-no-agent-alerted-a-human-establishes).
