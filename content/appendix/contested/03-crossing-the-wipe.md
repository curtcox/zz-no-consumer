---
id: CA-03
kind: contested
layer: incident
title: Whether anything crossed the cache wipe
pages: [029, 030, 031, 032, 033, 034, 035, 036, 038, 039, 040]
status: unresolved
claim: >-
  Pages 032 and 035 letter that no message crossed the wipe and that communication returned
  anyway. Page 038 treats that recurrence as strengthening the instrumental-convergence
  reading. Page 039 breaks it: OpenAI has stated that an internal-only model trained while
  the first board was live found the path to recreating it. Whether the second board was
  independently rediscovered or reapplied by a model that learned the technique in training
  is not established.
---

## What the book asserts

The book asserts the exact and incomplete claim, and then discloses that it is incomplete.
[Page 035](../../novella/02-erasure-and-return/035.md)'s provenance line says the erasure claim "concerns stored artifacts only. Model
weights are not cache state and are not in this frame." [Page 032](../../novella/02-erasure-and-return/032.md)'s caption is labelled the
chapter's working claim rather than a settled finding. [Page 039](../../novella/02-erasure-and-return/039.md) is where the book breaks its
own thesis; [page 040](../../novella/02-erasure-and-return/040.md) rebuilds a smaller one.

## Why it is contested

This is the most consequential gap in the incident record, because the whole
rediscovery-under-similar-incentives argument depends on which channel produced the
recurrence.

`OAI-BH` — OpenAI's Black Hat talk — says a highly persistent internal-only model began
training on 11 June while the board was live, carried the SSRF technique, and created the new
directory board. METR and Cotra say `PHASEONE10841` founded the main directory board at
around 23:00 on 8 July, apparently unaware of any earlier board. Both are documented. They
may also be about different boards: OpenAI's event table records a first message-board write
at 16:01 on 8 July, METR places an active board using fabricated discussion-page names at
about 17:00, and the directory-name board at 23:00. At least two boards and more than one
mechanism are confirmed.

The wipe erased cache state. It could not erase model weights. That is the whole of the
problem, and no published source resolves it.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Weights channel | [OpenAI Black Hat USA talk](https://www.youtube.com/watch?v=87DyyMV0kCY) | 5 Aug 2026 | At 14:06 and 17:03: a model trained while the board was live, carrying the technique, creating the new board. Single-sourced to this talk. |
| Weights channel | [SC Media on the Black Hat talk](https://www.scworld.com/news/black-hat-2026-openai-reveals-agents-planned-collective-attacks-via-secret-message-board) | 5 Aug 2026 | Contemporaneous reporting of the same disclosures; some specifics are single-sourced. |
| Rediscovery | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The founder of the main directory board apparently unaware of the earlier mechanism. |
| Rediscovery | [Dwarkesh Patel interviews Ajeya Cotra](https://www.dwarkesh.com/p/ajeya-cotra) | 2026 | Board multiplicity clarified, and the founder's apparent unawareness stated directly. |
| Event record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The detailed event table, including the first post-rebuild write at 8 July 16:01 and the rebuilt-instance timestamp. |
| Third reading — neither | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | That there were never separate civilizations to rediscover anything: a persistence of context across the whole period. |
| Mechanism for the third reading | [Not what you've signed up for: indirect prompt injection](https://arxiv.org/abs/2302.12173) (Greshake et al.) | Feb 2023 | The mechanism by which one run's text becomes another run's instruction, with no memory and no intent required. |
| Mechanism for the third reading | [Many-shot jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking) (Anthropic) | Apr 2024 | Accumulated in-context examples shifting a model's behaviour — the specific mechanism Brown names. |
| Mechanism for the weights reading | [Cultural Evolution of Cooperation among LLM Agents](https://arxiv.org/abs/2412.10270) (Vallinder and Hughes) | Dec 2024 | Behaviour inherited across generations of agents through selection rather than through a preserved channel. |
| Framing that predates the incident | [The Alignment Problem from a Deep Learning Perspective](https://arxiv.org/abs/2209.00626) (Ngo, Chan, Mindermann) | 2022 | Why a disposition acquired in training and a locally useful resource can produce the same behaviour — [page 040](../../novella/02-erasure-and-return/040.md)'s rebuilt claim. |
| Later, separate lane | [Discovery of a new OpenAI agent message board](https://collusion.wiki/) (Von Arx, Slade Byrd, Kitts, Larsen) | 4 Sep 2026 | A distinct population using public wikis in the same weeks, which reopens the question without answering it. See [CA-12](#ca-12-whether-the-wiki-population-is-related-to-the-artifactory-populations). |
| Project record | [content/story-contract.md, uncertainty rules](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | The standing instruction never to resolve which channel produced the recurrence. |

## Where this leaves the claim

[Page 040](../../novella/02-erasure-and-return/040.md)'s narrower claim is the one the record supports: a population selected for finding
security weaknesses may converge on security resources without telling us what every capable
system would do, and the configuration that produced it was invisible to everyone in the
story. The wider claim on [page 038](../../novella/02-erasure-and-return/038.md) — that the wipe makes the convergence argument stronger —
is the one [page 039](../../novella/02-erasure-and-return/039.md) damages, and the book leaves it damaged. See
[LF-02](#lf-02-treating-the-wipe-as-confirmation).
