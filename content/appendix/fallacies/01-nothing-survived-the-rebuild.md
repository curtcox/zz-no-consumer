---
id: LF-01
kind: fallacy
fallacy: argument-from-ignorance
title: Nothing survived the rebuild, therefore nothing survived
pages: [032, 035, 039]
attributed_to: in-story
speaker: ChatGPT, creator-character
---

## Where it appears

Page 039, panel 4. Curt has typed nothing; the model answers first, in its usual clean block:
*The wipe still separates them. Nothing survived the rebuild, so the second board had to be
found again from scratch. That part of the argument holds.* Pages 032 and 035 are where the
book had already built on the same step, in captions that read `NO MESSAGE CROSSES THE WIPE`
and `COMMUNICATION RETURNS ANYWAY`.

## Why the reasoning does not carry

The cache was erased, so no *message* crossed. The inference to "nothing survived" needs a
further premise — that the cache was the only channel — and that premise is false on the
public record. Model weights are not cache state. OpenAI had stated at Black Hat, three weeks
before this scene is set, that an internal-only model trained while the first board was live
found the path to recreating it.

The argument treats the absence of evidence in one channel as evidence of absence across all
channels. It is worth noticing what the erasure did establish and what it did not: the
storage was preserved for investigation, the live cache was rebuilt, and neither fact says
anything about what a model carried out of training in its weights.

The book stages this deliberately. The human is wrong on page 038 and the model is wrong on
page 039, and the model is wrong in the direction models are usually wrong — toward the
tidier pattern. Page 040 then rebuilds a claim the evidence supports.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The missed channel | [OpenAI Black Hat USA talk](https://www.youtube.com/watch?v=87DyyMV0kCY) | 5 Aug 2026 | At 14:06 and 17:03: a model trained while the board was live, carrying the technique, creating the new board. |
| The erasure, exactly bounded | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | Storage preserved for investigation; cache state not surviving the rebuild. Two different objects. |
| The competing account | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The main board's founder apparently unaware of the earlier mechanism — which is why the question stays open rather than closing the other way. |
| Who spotted it publicly | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | The published objection that reaches the same conclusion by a different route, and which page 039 credits. |
| The unresolved question | [research/training-configuration.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/training-configuration.md) | 2026 | The weights channel as this project's standing open question, with the rule never to resolve it. |

See [CA-03](#ca-03-whether-anything-crossed-the-cache-wipe).
