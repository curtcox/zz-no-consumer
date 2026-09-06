---
id: LF-18
kind: fallacy
fallacy: equivocation
title: Two product names for one mitigation test
pages: [093]
attributed_to: named-source
speaker: OpenAI, across its own incident documents
source_url: https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf
said: 26 August 2026
---

## Where it appears

Not on any page, deliberately. The book cites the mitigation effect without naming the
product, and this entry records why.

## Why the reasoning does not carry

OpenAI's blog account describes the production harness used in the safeguard comparison as
ChatGPT in one place; §VIII.D of the technical report calls it Codex. These are different
products with different harnesses, different tool surfaces, and different default
permissions. Whichever is correct, a claim of the form "our production harness reduced the
propensity by more than a hundredfold" cannot be evaluated by a reader who does not know
which harness was tested.

This is a small inconsistency and it is not evidence of anything beyond itself. It is in the
appendix because it is the kind of ambiguity that becomes load-bearing when a number travels:
a reader who takes the figure as being about the assistant they use has been told something
the documents do not jointly support.

The book's rule is therefore to cite the effect and not the product name, which is a
concession that the record is ambiguous rather than a claim that anyone misrepresented it.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| One naming | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | 26 Aug 2026 | The blog description of the harness used in the comparison. |
| The other naming | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf), §VIII.D | 26 Aug 2026 | The technical report's naming of the same test. |
| Why harness identity matters | [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Simon Willison) | Jun 2025 | That the harness — what the agent can read, run, and reach — largely determines the risk, independently of the model. |
| Why harness identity matters | [Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793) (Phuong et al.) | Mar 2024 | Harness and scaffold as first-order variables in any capability or propensity measurement. |
| Project record | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 2026 | The row recording the internal inconsistency and the resulting citation rule. |

See [CA-09](#ca-09-whether-the-post-incident-safeguard-numbers-show-the-failure-cannot-recur).
