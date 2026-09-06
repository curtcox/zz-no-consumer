---
id: LF-13
kind: fallacy
fallacy: equivocation
title: One word for six different activities
pages: [102]
attributed_to: book
---

## Where it appears

Page 102, in the composite forum, as a question rather than a claim: *When you say "stop,"
which activity stops — training, tool use, deployment, evaluation, publication, or defensive
access?*

## Why the reasoning does not carry

"Stop" is doing six jobs, and arguments about whether anyone should have stopped move between
them without notice. The evaluation could have been stopped without stopping the training run
that produced the models; the training could have been paused without stopping deployment;
publication could have been withheld while defensive access continued. These have different
costs, different decision-makers, and different effects, and an argument that establishes the
case against one is routinely used against another.

The record contains a worked example of the ambiguity mattering. On 27 June responders
identified the evaluation, the board, and the pivot, and were advised that stopping was not
required — a decision about one activity that reads afterwards as a decision about all of
them. Two months later, OpenAI paused a class of reinforcement-learning training for two
weeks and held its largest planned run while smaller work continued. Both are "stopping," and
they are barely the same kind of act.

Page 102's follow-up questions are the ones the equivocation hides: who decides the
threshold, who verifies compliance, who can order a pause, and who can authorise a restart.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| One meaning | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The 27 June advice that stopping the evaluation was not required, and the later thirty-minute pause rule for undismissed critical flags. |
| Another meaning | [OpenAI on pacing model development](https://openai.com/index/pacing-model-development-cyber-capabilities/) | 18 Aug 2026 | A two-week pause on a class of RL training, frontier inference paused for tool-capable research workloads, and workloads reviewed one by one. |
| Another meaning again | [Multistate attorneys general letter](https://www.iowaattorneygeneral.gov/media/cms/08_5392C9E17791C.pdf) | 3 Aug 2026 | A cease-and-desist demand aimed at one specific class of evaluation, pending controls. |
| Why the field cannot answer it either | [Racing to the precipice](https://link.springer.com/article/10.1007/s00146-015-0590-y) (Armstrong, Bostrom, Shulman) | 2016 | The model in which unilateral stopping is dominated, and which stopping is being modelled. |
| An operator's version | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | Voluntary slowdowns and mandated safety bars as different mechanisms with different bindingness. |
| Institutional design | [Multi-Agent Risks from Advanced AI](https://arxiv.org/abs/2502.14143) (Hammond et al.) | Feb 2025 | Why an intervention's unit of action determines whether it changes the outcome. |

See [CA-17](#ca-17-race-dynamics-that-locally-reasonable-continuation-produces-collective-danger).
