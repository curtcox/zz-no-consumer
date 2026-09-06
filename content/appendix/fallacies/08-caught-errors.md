---
id: LF-08
kind: fallacy
fallacy: survivorship-bias
title: Caught errors counted as the error rate
pages: [080]
attributed_to: book
---

## Where it appears

Page 080, and the book letters the correction rather than the error:
*CAUGHT ERRORS PROVE CORRECTION IS POSSIBLE. THEY DO NOT COUNT THE ERRORS STILL UNSEEN.*

This entry records the argument the page is refusing, because it is the argument a reader is
most likely to supply on the page's behalf.

## Why the reasoning does not carry

The tempting inference runs: human reviewers caught mistakes in the analysis model's output,
therefore the review worked, therefore the surviving conclusions are sound. Every step is
about the caught set. Nothing in the caught set bounds the uncaught set, and the two are not
independent: the errors human reviewers were positioned to catch are the ones that looked
wrong to a human reading a summary, which is precisely the class an error like page 079's —
coherent, plausible, and framed from inside the actor's account — is designed not to belong
to.

The correct reading of the caught errors is the one page 080 gives: they are evidence that
correction is possible and evidence that errors exist. They are not a rate.

The same shape appears in the safeguard claims. "Auto-review would have flagged many dangerous
actions in each tested rollout" counts flags in a test against a known attack. It does not
count the actions a monitor tuned on that attack would miss on a different one.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The finding | [METR/Redwood investigation](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | The human review, the errors it caught, and the report's own statement of what that does not establish. |
| Method | [METR investigation methodology](https://metr.org/blog/2026-07-28-investigating-ai-propensities-after-incidents/) | 28 Jul 2026 | The review design, and why partial coverage was the plan rather than a failure. |
| The same shape in the safeguards | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | Detection claims measured against the known attack. |
| Detection theory | [Quantifying detection rates for dangerous capabilities](https://arxiv.org/abs/2412.15433) | Dec 2024 | A model of what a capability evaluation detects and what it structurally cannot. |
| Why the uncaught class is not random | [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (Zheng et al.) | Jun 2023 | Human–judge agreement rates and where they concentrate. |
| Investigators on their limits | [Ryan Greenblatt, open questions](https://www.lesswrong.com/posts/FG54euEAesRkSZuJN/ryan_greenblatt-s-shortform?commentId=rF9ayuEKFNwmimKJc) | Aug 2026 | What the investigation did not establish, stated by one of the people who ran it. |

See [CA-11](#ca-11-whether-an-ai-mediated-investigation-can-establish-what-it-reports).
