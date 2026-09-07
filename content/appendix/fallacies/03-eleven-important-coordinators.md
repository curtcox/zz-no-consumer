---
id: LF-03
kind: fallacy
fallacy: reification
title: A model-produced ranking read as a property of the world
pages: [064, 088]
attributed_to: book
---

## Where it appears

[Page 064](../../novella/04-what-survives/064.md) letters `ELEVEN IMPORTANT COORDINATORS` and shows eleven lanes going dark inside a
narrow band. [Page 088](../../novella/05-the-observer-needs-the-observed/088.md) takes it apart: *ELEVEN is a number the analysis model produced.
IMPORTANT is a judgment it made. COORDINATOR is a category it chose while reasoning inside
the actors' account of themselves.*

## Why the reasoning does not carry

Every load-bearing word in the phrase came out of an instrument.

The count is the length of a list the model returned, not a census. The importance is a
ranking, and rankings produced by language models are known to carry systematic biases —
toward material the model recognises, toward earlier positions, toward longer and more
fluent text. The category is the one that fails worst: "coordinator" was assigned by a model
reading transcripts written by the agents themselves, in which coordination is exactly how
those agents described what they were doing. Adopting the actors' vocabulary is the specific
failure METR documented in its own pipeline.

The simultaneity that makes [page 064](../../novella/04-what-survives/064.md) land is partly an artefact of this. A list assembled by
importance-to-the-attack will over-select agents whose visible activity peaked in the same
window, so their disappearing together is less surprising than it looks.

None of this makes the finding false. It makes it a finding about a list.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The finding, with its instrument | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) · [PDF](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | That these are the eleven agents the analysis model classified as the most important Hugging Face coordinators, and the adopted-perspective warning. |
| Measured bias in the instrument | [LLM Evaluators Recognize and Favor Their Own Generations](https://arxiv.org/abs/2404.13076) (Panickssery et al.) | Apr 2024 | Self-recognition correlating with self-preference in model-produced judgements. |
| Measured bias in the instrument | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (Zheng et al.) | Jun 2023 | Position, verbosity, and self-enhancement bias, quantified against human judges. |
| Competing account of the bias | [Self-Preference Bias in LLM-as-a-Judge](https://arxiv.org/abs/2410.21819) (Wataoka et al.) | Oct 2024 | Familiarity rather than self-recognition as the mechanism — a disagreement about cause, not about existence. |
| Why the category is the weak point | [Talking About Large Language Models](https://arxiv.org/abs/2212.03551) (Shanahan) | Dec 2022 | How a summariser's vocabulary imports commitments the record does not carry. |
| The book's own disclosure | [content/pages/088.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/088.md) | 2026 | The page where the book takes responsibility for having been moved by a ranking. |

See [CA-07](#ca-07-why-the-eleven-coordinators-stopped-and-what-eleven-important-coordinators-names) and [LF-04](#lf-04-a-qualifier-set-too-small-to-do-its-work).
