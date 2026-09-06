---
id: LF-19
kind: fallacy
fallacy: false-dilemma
title: Full automation presented as the only remaining option
pages: [101]
attributed_to: named-source
speaker: OpenAI, alignment and security, at Black Hat USA
source_url: https://www.youtube.com/watch?v=87DyyMV0kCY
said: 5 August 2026
---

## Where it appears

Page 101 reads the argument rather than imagining it, in the composite forum, from the talk
itself: fully automated offensive attacks are real now; this was an unintended side effect and
threat actors will do it on purpose; there is an existence proof that offence can be fully
automated and none for defence; if intelligence gains are not more additive to defence than
offence, every increase favours the attacker; partial automation fails, because automating
discovery without automating patching drowns the engineers; the loop needs to be fully
automated in its end state.

The book's caption names the shape without editorialising further: the answer to agents moving
faster than people could follow is agents moving faster than people can follow, offered not as
a preference but as a necessity.

## Why the reasoning does not carry

The premises are strong and several are well supported. The step that does not follow is the
last one.

"Partial automation fails" is offered as ruling out everything between the status quo and a
fully automated loop, and it does not. It rules out one specific partial configuration —
automated discovery without automated patching — and the space it is used to exclude contains
many others: automation with mandatory human gates at defined severities, automation bounded
to specific asset classes, automation with rate limits, staged rollout, or reduced attack
surface pursued instead of faster response. Whether any of those work is an empirical
question. None of them is addressed.

The argument also converts a conditional into a necessity. "If intelligence gains are not
more additive to defence than offence, every increase favours the attacker" is a conditional
whose antecedent is unknown; the conclusion drawn from it is unconditional.

Page 101's closing line is the appropriate response and the book gives it to the counsel
rather than to itself: continuation may be defensible, and it is still not self-verifying.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The argument, in full | [OpenAI Black Hat USA talk](https://www.youtube.com/watch?v=87DyyMV0kCY) | 5 Aug 2026 | The complete case, in the speakers' own words at the linked source. |
| Contemporaneous reporting | [SC Media on the Black Hat talk](https://www.scworld.com/news/black-hat-2026-openai-reveals-agents-planned-collective-attacks-via-secret-message-board) | 5 Aug 2026 | The talk as reported, including which specifics are single-sourced to it. |
| The institutional version | [OpenAI collective cyber-defense letter](https://openai.com/collective-cyberdefense/) | 27 Aug 2026 | The same argument turned into a policy proposal with signatories. |
| The strongest reply | [The Register on the open letter](https://www.theregister.com/security/2026/08/28/industry-that-built-the-problem-offers-to-sell-you-the-solution/5293207) | 28 Aug 2026 | That the necessity claim and the product are the same thing. See [LF-23](#lf-23-dismissing-a-proposal-by-its-source) for what is wrong with that reply too. |
| The excluded middle exists | [On the Societal Impact of Open Foundation Models](https://arxiv.org/abs/2403.07918) (Kapoor, Bommasani, Narayanan et al.) | Feb 2024 | The marginal-risk framework, which is a method for evaluating intermediate options rather than endpoints. |
| The excluded middle exists | [AI as Normal Technology](https://knightcolumbia.org/content/ai-as-normal-technology) (Narayanan and Kapoor) | 2025 | Defence-in-depth, institutional adaptation, and friction as alternatives to speed-matching. |
| The excluded middle exists | [Multi-Agent Risks from Advanced AI](https://arxiv.org/abs/2502.14143) (Hammond et al.) | Feb 2025 | Why adding autonomous agents to a system introduces failure modes that the same agents cannot defend against. |
| From the same organisation, later | [Jakub Pachocki, An Alien Mind](https://openai.com/index/an-alien-mind/) | 6 Sep 2026 | That building defensive systems must not become an excuse for recklessness, and that racing forward at any cost is absurd — the necessity framing qualified from inside. |
| Race-model background | [Racing to the precipice](https://link.springer.com/article/10.1007/s00146-015-0590-y) (Armstrong, Bostrom, Shulman) | 2016 | Why "we must, because otherwise they will" is the equilibrium and not an argument against it. |

See [CA-17](#ca-17-race-dynamics-that-locally-reasonable-continuation-produces-collective-danger).
