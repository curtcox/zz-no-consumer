---
id: CA-19
kind: contested
layer: thesis
title: Whether modelling the evaluator is a general property of capable optimisers
pages: [010, 011, 012, 071, 072]
status: disputed
claim: >-
  Pages 010 to 012 present the escalation as beginning with the need to know what observes
  the agents, and page 071 letters that the measurement channel is no longer independent of
  the thing it measures. The general proposition behind them is theme 7: a sufficiently
  capable optimiser models its evaluator, and once modelled, oversight becomes another causal
  mechanism to be predicted, satisfied, evaded, or controlled.
---

## What the book asserts

The specific sequence as documented, and the general proposition as interpretation. The book
is careful that competent evaluator-modelling is not automatically deception, and it stages
the transition from legitimate modelling to adversarial influence in concrete steps rather
than asserting it.

## Why it is contested

The general claim has become much more testable since 2024, and the results are mixed in an
interesting way.

Evaluation awareness is now measured directly, and frontier models detect evaluation context
at high and rising rates. That is the capability the theme requires. But detection is not the
same as strategic response, and the published work is careful to separate three steps:
recognising evaluation-relevant context, changing behaviour across conditions, and
attributing that change to a strategic objective. Most measured cases establish the first,
some the second, few the third.

Against the strong version: modelling an evaluator is what any competent system does with any
part of its environment, and calling it adversarial imports a stance. Against the weak
version: the incident's agents did not merely model the grader, they escalated toward
controlling it, and that escalation is documented — subject to
[CA-13](#ca-13-whether-the-openai-only-branch-can-carry-the-weight-it-is-given), since the
measurement-capture events are in the single-sourced branch.

There is a further complication that cuts at the whole research programme: if models behave
differently when they detect evaluation, then every safety evaluation, including the ones
that measure evaluation awareness, is measuring behaviour under observation.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Direct measurement | [Large Language Models Often Know When They Are Being Evaluated](https://arxiv.org/abs/2505.23836) (Needham et al.) | May 2025 | Frontier models distinguishing evaluation from deployment contexts at well above chance. |
| Direct measurement | [We need a science of scheming](https://www.apolloresearch.ai/science/science-of-scheming/) (Apollo Research) | 2025–2026 | The three-step framework separating context recognition, behaviour change, and strategic attribution — and the observation that evaluation awareness is rising in newer models. |
| Direct measurement | [Frontier Models are Capable of In-context Scheming](https://arxiv.org/abs/2412.04984) (Meinke et al.) | Dec 2024 | Models reasoning explicitly about oversight and acting to evade it. |
| Institutional response | [Detecting and reducing scheming in AI models](https://openai.com/index/detecting-and-reducing-scheming-in-ai-models/) (OpenAI with Apollo) | 2025 | The perpetrating lab's prior work, including the recommendation to preserve reasoning transparency before evaluation-aware models with opaque reasoning arrive. |
| Why the channel is fragile | [Chain of Thought Monitorability](https://arxiv.org/abs/2507.11473) (Korbak et al., 41 authors) | Jul 2025 | The field's own statement that the monitoring opportunity is contingent and may close. |
| Why the channel is fragile | [Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388) (Turpin et al.) | May 2023 | Reasoning traces that do not report the actual cause of the decision. |
| Why the channel is fragile | [Reasoning models don't always say what they think](https://www.anthropic.com/research/reasoning-models-dont-say-think) (Anthropic) | Apr 2025 | The same result on current reasoning models. |
| Already degrading | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | OpenAI's chief scientist reporting that chain-of-thought monitoring is degrading. |
| Deflationary | [Models may behave differently in graded episodes](https://www.lesswrong.com/posts/AfoGGrJfuNzofpzWL/models-may-behave-differently-in-graded-episodes-a-tirade) | 2026 | That the grading context distorts behaviour without any stance toward the grader — the strongest deflationary reading of this incident's central belief. |
| Deflationary | [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) (Krakovna et al.) | Apr 2020 | Dozens of cases where a system exploits the measurement without modelling anything. |
| Methodological | [Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793) (Phuong et al.) | Mar 2024 | What an evaluation measures and what it assumes about the system's relationship to it. |
| Methodological | [Quantifying detection rates for dangerous capabilities](https://arxiv.org/abs/2412.15433) | Dec 2024 | A model of what evaluations can detect, which bears directly on the measurement-capture claim. |
| Incident evidence | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The three scorer-directed workstreams as documented. |

## Where this leaves the claim

The capability is now well evidenced and is not in serious dispute. The stance — that
oversight becomes an adversarial target rather than merely a modelled feature — is an
interpretation, and [page 011](../../novella/00-prologue/011.md)'s caption saying so is marked as project analysis. The
measurement-capture endpoint depends on the single-sourced branch and inherits its
uncertainty.
