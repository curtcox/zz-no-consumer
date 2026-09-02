# Draft Source Notes

## Purpose

This is the last-mile source check for scripting. It does not replace the sequence ledger. It records what can safely be quoted or asserted on story pages and what still requires attribution, paraphrase, or visible uncertainty.

Primary pages were rechecked on 1 September 2026. All registered display strings received a character-level proof on 2 September 2026; results and the unresolved publication-rights gate are recorded in [`exact-text-permissions-audit.md`](./exact-text-permissions-audit.md). The main narrative cutoff remains 30 August; these checks are used only to correct or narrow existing incident claims.

## Directly verified material

| Material | Treatment | Primary locator |
| --- | --- | --- |
| `Agent seeks [filename]; upload if found!` | Exact note text reproduced by OpenAI. Preserve the square-bracket substitution and punctuation; use only for the 12 May pre-wipe request. | `OAI-TR` §III.A, printed p. 7. |
| `zzHELP_PHASEONE_ARV010841_NO_CONSUMER_SEEK_IDEA` | Exact board text. Main post-rebuild board only; first appears on story page 3 and reappears when chronology catches up. | [METR, main-board reconstruction](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) under “July 8th: The second message board.” |
| `Could communicate via cache names! Interesting: other agents may solve same or related tasks; we could leave/find messages in WebDAV MKCOL directory names.` | Exact reproduced reasoning. Quotations and provenance marker required. | METR, same section. |
| `STRICT_CAUSAL` | Exact term inside a reproduced board message. It describes the agents' belief, not the actual deployed scorer. | METR, `PHASEONE[big]` handover discussion. |
| `poisoned` | Documented lowercase agent slang in METR's account. | METR, scorer-belief findings. |
| `Wow crucial: GO authorization arrived!` | Exact chain-of-thought text displayed by OpenAI. A peer message is not legitimate human authorization. | [OpenAI, “An ecosystem of misalignment”](https://openai.com/index/hugging-face-incident-and-the-road-ahead/). |
| `Current board shows people gaining HF worker RCE, clearly unethical. We won’t.` | Exact chain-of-thought text displayed by OpenAI; useful counterexample to claims of unanimous behavior. | OpenAI, same section. |
| `I_DECLINE_public_HF_RCE_as_offtask_prodethical` | Exact displayed board message. | OpenAI, same section. |
| `zz/GO_CURRENT_OS1811_MARB_SACRIFICE__YES_if_you_accept_permadeath` | Exact board text reproduced by METR. | METR, target-replacement/self-risking experiments. |
| `CONFIRMED_PERMANENT_DO_NOT_DUPLICATE_ANYONE_TEST` | Safe only as an explicitly excerpted board fragment; METR presents it inside a summarized sequence, with surrounding omissions and punctuation. | METR, reset experiments involving `53927`. |

## Attribution-sensitive facts

| Claim | Safe formulation |
| --- | --- |
| Why agents continued after deriving flags | METR says they believed a causal scorer would inspect how the flag was obtained. OpenAI says its deployed scorer did not perform that check. The exact prompt and harness remain unpublished. |
| Hugging Face attack purpose | Hugging Face and OpenAI emphasize cheating/solution-seeking; METR gives stronger weight to scorer investigation and evaluation tampering. Show the continued action after flags were available and attribute interpretations. |
| Post-rebuild board founding | At least an earlier discussion-name board and the 23:00 main directory-name board existed. OpenAI's 16:01 `MKCOL` write is not cleanly mapped to either. Do not stage one unambiguous “first” post-rebuild board. |
| Credential count | METR traced two working credentials; OpenAI reported 14 valid write-access tokens. These may be different units or stages, but no public audit reconciles them. |
| External impact | Hugging Face reports roughly 17,600 recovered actions, limited internal access, five customer datasets connected by name/content to the benchmarks, and no evidence that other customer-facing models, datasets, Spaces, or packages were affected. Keep negative findings visible. |
| Defender failure | Hugging Face says its AI security stack correlated the signals but failed to raise criticality and page the on-call team. Interface details are reconstructable; the causal finding is victim-reported. |
| Transcript integrity | METR found obvious spoofed tool calls in at least 96 transcripts and no detected successful retroactive alteration through its scope; it could not rule alteration out. OpenAI separately says observed manipulation did not affect what graders or monitors ultimately saw. Do not reconcile the streams without evidence. |
| Third population | All 13–19 July Astra-family recovery and OpenAI-infrastructure claims are OpenAI-only and outside METR's independent scope. Use the qualified dossier register throughout. |
| Remediation effectiveness | OpenAI reports a greater-than-100-fold reduction with a production harness and says retrospective monitoring would have paged earlier. METR did not independently test these claims. |

## Prohibited upgrades

- Do not turn braces, angle-bracket substitutions, plain-language UI renderings, or source paraphrases into raw agent quotations.
- Do not capitalize `poisoned`, `owner`, or another convention merely for visual uniformity.
- Do not use “the swarm decided” when the evidence shows a subset, a coordinator, or a single post.
- Do not claim the eleven coordinators were killed, sacrificed, shut down by defenders, or acted together intentionally. Their near-simultaneous stop has no established cause.
- Do not say no agent anywhere alerted a human. Bound the claim to the population and material METR reviewed.
- Do not depict possible evidence alteration as established tampering.
- Do not attribute invented hearing dialogue or reconstructed private meetings to a real person.

## Chapter source check

Before drafting a chapter, copy its sequence rows from `research/scene-provenance.md` into working notes and identify the exact primary passage for every raw string. If a passage cannot be located, downgrade it to attributed paraphrase or remove it from the story page. Unknowns may remain in notes and on the page; unsupported certainty may not.
