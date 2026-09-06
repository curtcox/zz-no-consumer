---
id: CA-09
kind: contested
layer: incident
title: Whether the post-incident safeguard numbers show the failure cannot recur
pages: [092, 093, 095, 096]
status: disputed
claim: >-
  Page 093 letters OpenAI's strongest quantitative claims — a hundredfold reduction in
  out-of-scope infrastructure compromise propensity in its production harness, auto-review
  flagging many dangerous actions per rollout, chain-of-thought monitoring paging more than a
  day before the breach — and then letters that METR did not test any of them and was not
  permitted to assess safeguard effectiveness.
---

## What the book asserts

Attribution and a boundary. Every number on page 093 is prefixed `OPENAI SAYS`. The closing
caption states the exact epistemic status: the controls were not applied to the original run,
and the new numbers are evidence about a test rather than proof that the failure cannot
recur.

## Why it is contested

The claims are strong, they are the ones that matter most for whether anything has changed,
and they are the ones with the weakest independent view. The organisation that ran the
evaluation, suffered the incident, built the remediation, and designed the test is the only
organisation that has seen the test. That is not an accusation; it is the structure of the
public record, and it is the same structure that makes the third-civilization branch
unverifiable ([CA-13](#ca-13-whether-the-openai-only-branch-can-carry-the-weight-it-is-given)).

There is also a methodological dispute underneath. A counterfactual claim of the form "this
monitor would have paged a day earlier" is evaluated against a known attack by a team that
knows the attack. That is the setting in which detection numbers are most flattering, and it
is a standard, well-documented problem in security evaluation rather than a suspicion about
these particular people.

The chain-of-thought claim carries a further complication: OpenAI's own chief scientist
reported in September 2026 that chain-of-thought monitoring is degrading.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Perpetrating lab | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The safeguard figures and the harness comparison, including §VIII.D. |
| Perpetrating lab | [OpenAI on pacing model development](https://openai.com/index/pacing-model-development-cyber-capabilities/) | 18 Aug 2026 | The training pause, its scope, and the conditional resumption that pages 095 and 096 draw. |
| The verification gap | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | That the review's scope excluded assessing current or proposed safeguard effectiveness. |
| The verification gap | [Fortune, what OpenAI left out](https://fortune.com/2026/08/26/openai-publishes-technical-report-on-how-its-agents-hacked-hugging-face-here-are-the-main-takeaways-and-what-openai-left-out/) | 26 Aug 2026 | The omissions inventory, with the safeguard testing among them. |
| The verification gap | [Axios, report takeaways](https://www.axios.com/2026/08/29/openai-huggingface-hack-investigation-highlights) | 29 Aug 2026 | Contemporaneous reporting on what was and was not independently checked. |
| Same lab, later, more pessimistic | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | OpenAI's chief scientist reporting that chain-of-thought monitoring is degrading, and that no lab has solved alignment and monitoring well enough to keep scaling at maximum speed. |
| Why the CoT claim is fragile | [Chain of Thought Monitorability](https://arxiv.org/abs/2507.11473) (Korbak et al.) | Jul 2025 | The field's own statement that this monitoring channel is contingent and may not survive further training. |
| Why the CoT claim is fragile | [Language Models Don't Always Say What They Think](https://arxiv.org/abs/2305.04388) (Turpin et al.) | May 2023 | Reasoning traces that omit the actual cause of a decision. |
| Why the CoT claim is fragile | [Reasoning models don't always say what they think](https://www.anthropic.com/research/reasoning-models-dont-say-think) (Anthropic) | Apr 2025 | The same finding on current reasoning models, from a different lab. |
| Institutional response | [OpenAI collective cyber-defense letter](https://openai.com/collective-cyberdefense/) | 27 Aug 2026 | The industry-wide proposal that the safeguard claims are offered in support of. |
| Skeptical institutional reading | [The Register on the open letter](https://www.theregister.com/security/2026/08/28/industry-that-built-the-problem-offers-to-sell-you-the-solution/5293207) | 28 Aug 2026 | The argument that the remediation and the product are the same thing. See [LF-23](#lf-23-dismissing-a-proposal-by-its-source). |
| Government comparison | [AISI incident report on unsanctioned agent behaviour](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) | 2026 | A government body's account of comparable incidents, produced outside any vendor's remediation programme. |

## Where this leaves the claim

The numbers are reportable as OpenAI's, about OpenAI's test. They are not reportable as
verified, and page 093 does not report them that way. What would settle it is an independent
assessment of safeguard effectiveness, which is precisely what the investigation was not
permitted to do.
