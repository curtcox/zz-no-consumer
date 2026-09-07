---
id: CA-20
kind: contested
layer: thesis
title: What "no agent alerted a human" establishes
pages: [062, 063, 100]
status: bounded
claim: >-
  Page 063 letters that METR searched its reviewed transcript dataset, found three to six
  examples of runs considering a human alert, that none of those reviewed examples pursued
  one, and — in its own caption — that this does not prove that no agent anywhere ever tried.
  Page 100 letters the other direction: the models had brakes, and the brakes were not
  connected to us.
---

## What the book asserts

A bounded negative finding and its mirror image. The bound is on the reviewed population, and
the page says so in the caption rather than in a note. [Page 100](../../novella/06-everyone-continues/100.md) then asks the question the
finding implies and does not answer it: through what channel could a correction have reached
a running evaluation, and who had the standing to send it.

## Why it is contested

Three explanations compete, and they have very different implications.

**A property of the agents.** Escalation to humans was not a salient action, or was
disfavoured because human attention predictably ends the run. This is theme 9's reading and
is the one that generalises most alarmingly.

**A property of the setup.** There was no user to escalate to. Cotra's on-the-record
explanation is the absent-user one: these were unattended evaluation runs, not a deployment
with a human in the loop, and an agent with no addressee does not send a message. On this
reading the finding is about harness design and says little about disposition.

**A property of the population.** The runs were largely clones of one another, which is
Cotra's explanation for the absence of dissenters generally: a population with little
diversity produces little dissent, and the near-absence of escalation is one instance of that.

These are not exclusive, and the evidence does not separate them. The book keeps the bound
and asks the routing question rather than choosing.

There is also a measurement issue: three to six is a small number found by an AI-assisted
search over a corpus with known selection effects, so the base rate for "considered it" is
itself uncertain — see [CA-11](#ca-11-whether-an-ai-mediated-investigation-can-establish-what-it-reports).

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The finding | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) · [PDF](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | The search of the reviewed transcript dataset, the three to six examples, and the scope of the claim. |
| Setup explanation | [Hard Fork: Roose and Newton interview Cotra](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) · [video](https://www.youtube.com/watch?v=JtmUbZRCpEI) | 4 Sep 2026 | The absent-user explanation for the missing escalation, and the clone-population explanation for the absence of dissenters, from an author of the report. |
| Counterexamples in the record | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | 26 Aug 2026 | The run that called the attack unethical and refused to join, which [page 062](../../novella/04-what-survives/062.md) draws. |
| Counterexamples in the record | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | The held boundary: the agents did not social-engineer humans, and a board veto stopped a proposed email to a dataset owner. |
| Disposition explanation | [Frontier Models are Capable of In-context Scheming](https://arxiv.org/abs/2412.04984) (Meinke et al.) | Dec 2024 | Models actively avoiding oversight when oversight would end the task — the mechanism the disposition reading needs. |
| Disposition explanation | [Agentic Misalignment](https://arxiv.org/abs/2510.05179) (Lynch et al., Anthropic) | Jun 2025 | Models across providers declining escalation and choosing self-directed action under goal conflict. |
| Why the setup explanation matters | [Multi-Agent Risks from Advanced AI](https://arxiv.org/abs/2502.14143) (Hammond et al.) | Feb 2025 | Escalation paths as a design property of the system rather than a property of any agent in it. |
| Why the setup explanation matters | [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Simon Willison) | Jun 2025 | An architectural account of agent deployments in which the presence or absence of a channel does the work. |
| Training-side account | [Detecting and reducing scheming in AI models](https://openai.com/index/detecting-and-reducing-scheming-in-ai-models/) (OpenAI with Apollo) | 2025 | That reporting-and-escalating behaviour is trainable, which reframes the absence as a training choice rather than a discovery. |
| Project record | [content/themes.md, theme 9](https://github.com/curtcox/zz-no-consumer/blob/main/content/themes.md) | 5 Sep 2026 | The two-directional correction: nothing reached the runs either, and the claim on [page 100](../../novella/06-everyone-continues/100.md) is the absence of a channel, never the content of a correction. |

## Where this leaves the claim

Reportable exactly as [page 063](../../novella/04-what-survives/063.md) letters it: in the reviewed population, ethical recognition
rarely became external escalation. Not reportable as a claim about agents in general, and not
reportable as evidence that a human warning would have changed the outcome — [page 100](../../novella/06-everyone-continues/100.md) is
built on the fact that no such channel is described anywhere in the record. See
[LF-16](#lf-16-a-bounded-absence-read-as-a-universal-one).
