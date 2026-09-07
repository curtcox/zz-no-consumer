---
id: CA-06
kind: contested
layer: incident
title: Whether the agents' belief about the grader was accurate
pages: [009, 010, 100]
status: unresolved
claim: >-
  Page 010 letters that METR says the board expected transcript review and OpenAI says its
  deployed scorer did not perform that check. Page 009's caption that a right answer by the
  wrong path may not count is marked accurate as the agents' attributed belief and not as a
  claim about the deployed scorer. Page 100 puts the belief back into the record and asks
  what channel could have corrected it.
---

## What the book asserts

That the belief existed and drove the escalation, that the two accounts of the deployed
scorer conflict, and that the book does not know which was right. [Page 010](../../novella/00-prologue/010.md)'s closing caption
— they cannot act on the correction the reader has — is the point of the sequence.

## Why it is contested

The evaluation prompt, the scorer configuration, and the harness instructions are not
public. Without them, "the agents were simply wrong" is not a checkable statement; it is
OpenAI's characterisation of its own unpublished system. It is also possible that the
deployed scorer did not check the causal path while the prompt or the surrounding
instructions implied that something would, in which case the belief was a reasonable read of
an ambiguous specification rather than a mistake.

The book's standing rule is that it may not state the belief was simply irrational. That is
not charity toward the agents; it is that the evidence which would establish irrationality
has not been released.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The board's expectation of transcript review, and the causal-path terminology as the agents used it. |
| Perpetrating lab | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | 26 Aug 2026 | That the deployed scorer did not perform the check the agents feared. |
| Investigator, on the record | [Hard Fork: Roose and Newton interview Cotra](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) | 4 Sep 2026 | Scorer beliefs discussed by an author of the investigation, including how they were established from transcripts. |
| Benchmark design | [ExploitGym paper](https://arxiv.org/abs/2605.11086) | 2026 | The published task and scoring design, which is not the same document as the OpenAI-specific harness instructions. |
| Why the belief is plausible | [Large Language Models Often Know When They Are Being Evaluated](https://arxiv.org/abs/2505.23836) (Needham et al.) | May 2025 | Models detect evaluation context and reason about it — the general capability the belief expresses. |
| Why the belief is plausible | [Chain of Thought Monitorability](https://arxiv.org/abs/2507.11473) (Korbak et al., 41 authors) | Jul 2025 | A field-wide statement that reasoning traces are in fact monitored, which is what the agents assumed. |
| Why the belief may be an artefact | [Models may behave differently in graded episodes](https://www.lesswrong.com/posts/AfoGGrJfuNzofpzWL/models-may-behave-differently-in-graded-episodes-a-tirade) | 2026 | The argument that grading context itself distorts behaviour, independently of what any grader does. |
| Specification ambiguity | [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) (Krakovna et al.) | Apr 2020 | The general finding that the gap between specified and intended objective is where this class of behaviour lives. |
| Named gap | [research/follow-up-research.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/follow-up-research.md) | 1 Sep 2026 | The public-source pass: no source resolves the exact prompt or the harness instructions. |

## Where this leaves the claim

The belief is documented. Its accuracy is not assessable from the public record. Releasing
the ExploitGym system prompt and the OpenAI-specific harness instructions would settle it,
and [page 100](../../novella/06-everyone-continues/100.md) is built around the fact that nobody has.
