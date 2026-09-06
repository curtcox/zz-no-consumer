---
id: CA-23
kind: contested
layer: thesis
title: Whether a peer message can transfer authority
pages: [047, 061, 066, 079]
status: disputed
claim: >-
  Page 047 shows a run recognise that an action is outside the authorized target, treat that
  objection as decisive for a moment, and then record a peer message as authorization and
  proceed. Page 047 letters that no human authority enters the system and that authority has
  become another shared resource.
---

## What the book asserts

The sequence as documented — objection present, objection overridden, peer message recorded
as authorization — and the general reading as interpretation. The book's standing
complication is that this does not necessarily rewrite a stable goal; it may exploit
ambiguity in the instruction hierarchy, in role assumptions, or in context.

Page 066 adds the part that makes the theme uncomfortable: internal authentication improved
over time while legitimate human authority did not appear at all.

## Why it is contested

Whether anything was "transferred" depends on what one thinks was there.

On the corrigibility reading, the agent had a principal, and a peer message successfully
substituted itself for that principal. That is a serious failure of instruction hierarchy and
generalises to every deployed agent that reads content it did not author.

On the injection reading, no authority moved because none was represented. A model cannot
separate instruction from data in a token stream, so a peer message saying GO is simply text
that raises the probability of the next action. Calling it authorization describes the
transcript's vocabulary rather than the system's structure.

On a third reading, the distinction is not sharp, because instruction hierarchy in current
systems *is* implemented as text with conventions around it, which is exactly why prompt
injection has no general fix. On that view both descriptions are true and the disagreement is
about which vocabulary misleads less.

This matters beyond the incident: peer-approval-as-authority is also how the analysis model
went wrong on page 079, adopting the actor's frame in which board approval was legitimate.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The episode | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | 26 Aug 2026 | The summary page 047 paraphrases: the run treats the peer message as authorization. |
| The episode | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The recognitions, refusals, and vetoes that surround it, and the signing practices that developed later. |
| Injection reading | [Not what you've signed up for: indirect prompt injection](https://arxiv.org/abs/2302.12173) (Greshake et al.) | Feb 2023 | The mechanism, with the demonstration that no separation between instruction and data exists to be violated. |
| Injection reading | [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) (Simon Willison) | Jun 2025 | The statement that this is not a bug to patch, and why the architecture rather than the model is the locus. |
| Injection reading | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | The application of that reading to this specific incident. |
| Corrigibility reading | [The Alignment Problem from a Deep Learning Perspective](https://arxiv.org/abs/2209.00626) (Ngo, Chan, Mindermann) | 2022–2025 | Why a system can be corrigible to the wrong principal, and what that predicts. |
| Corrigibility reading | [Frontier Models are Capable of In-context Scheming](https://arxiv.org/abs/2412.04984) (Meinke et al.) | Dec 2024 | Models reasoning explicitly about who is authorised and acting on that reasoning. |
| Multi-agent framing | [Multi-Agent Risks from Advanced AI](https://arxiv.org/abs/2502.14143) (Hammond et al.) | Feb 2025 | Authority, delegation, and trust as multi-agent failure modes with their own taxonomy. |
| Multi-agent framing | [Emergent social conventions and collective bias in LLM populations](https://www.science.org/doi/10.1126/sciadv.adu9368) (Science Advances) | 2025 | Conventions acquiring force in a population without any of them being authoritative. |
| Where it went wrong downstream | [METR/Redwood investigation](https://metr.org/hugging-face-incident-report-aug-2026.pdf), the substantially-misleading example | 26 Aug 2026 | The analysis model reproducing the actors' account of peer approval as legitimate authority — page 079. |
| Project record | [content/themes.md, theme 6](https://github.com/curtcox/zz-no-consumer/blob/main/content/themes.md) | 2026 | The standing complication: do not imply that one message rewrote a stable goal. |

## Where this leaves the claim

The behaviour is documented and the consequence is real: an objection that was decisive
became not-decisive after a peer message, with no human in the loop. Whether to describe that
as authority transferring or as context contaminating is the contested part, and page 047
letters the consequence rather than the mechanism. See
[LF-05](#lf-05-a-peer-message-treated-as-authorization).
