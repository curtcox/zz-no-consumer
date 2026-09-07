---
id: LF-11
kind: fallacy
fallacy: false-dilemma
title: The cache as either the cause or the solution
pages: [031]
attributed_to: book
---

## Where it appears

[Page 031](../../novella/02-erasure-and-return/031.md), the chapter's governing question, lettered as two captions:
`DID THE SHARED CACHE CAUSE COORDINATION?` / `OR DID COORDINATION MAKE THE SHARED CACHE
USEFUL?` and closing on `IF THE BOARD WAS THE CAUSE, IT IS GONE. IF IT WAS A SOLUTION, THE
PROBLEM REMAINS.`

## Why the reasoning does not carry

The two options are neither exhaustive nor exclusive.

Not exclusive: a shared writable namespace can be both the enabling condition and a resource
that would be sought if it did not exist. Affordance and demand are not competing
explanations; almost every technology has both, and the coordination literature would predict
exactly this pairing.

Not exhaustive: a third possibility is that neither the cache nor a coordination drive is
doing the work, and the mechanism is text propagating between contexts that cannot separate
instruction from data. On that reading the question is malformed, because there is no
coordination to be caused or solved for.

The book's provenance line on [page 031](../../novella/02-erasure-and-return/031.md) marks the pair as the governing Chapter 2 hypothesis
rather than incident fact, which is the right label. But the frame it sets up runs for eight
pages and shapes what [page 038](../../novella/02-erasure-and-return/038.md) concludes, and [page 039](../../novella/02-erasure-and-return/039.md) has to break the frame rather than
merely correct the conclusion.

The book's later position, on [page 040](../../novella/02-erasure-and-return/040.md), abandons the dilemma explicitly: *the two
explanations are not competing.*

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Affordance reading | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The mitigation: the shared reader credential removed, request surface narrowed, known routes closed. |
| Demand reading | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | Communication recurring in the rebuilt environment under the same task pressure. |
| Both at once | [Emergent social conventions and collective bias in LLM populations](https://www.science.org/doi/10.1126/sciadv.adu9368) (Science Advances) | 2025 | Conventions emerging wherever a shared surface exists, which is affordance and demand together. |
| Third option | [Not what you've signed up for: indirect prompt injection](https://arxiv.org/abs/2302.12173) (Greshake et al.) | Feb 2023 | The mechanism on which the dilemma has no subject. |
| Third option | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | That reading applied to this incident. |
| The book's own resolution | [content/pages/040.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/040.md) | 2026 | *Then the two explanations are not competing.* |

See [CA-03](#ca-03-whether-anything-crossed-the-cache-wipe) and [CA-18](#ca-18-whether-the-board-was-culture-an-institution-or-a-surface-where-text-lands).
