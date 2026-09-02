# Prologue Source Packet — The Objective Remains

## Scope

This packet supports story pages 001–015 and sequences 1–6 plus Creator Interlude A. It was checked against the public primary sources on 2 September 2026. The narrative cutoff remains 30 August 2026; this check only verifies already selected facts and wording.

The incident pages cover 8–9 July 2026 and the second, post-rebuild ExploitGym population. Pages 013–015 are reconstructed creator scenes and make no claim to preserve a verbatim Curt/ChatGPT exchange.

## Primary sources

- `METR` — [Brief independent investigation of agents’ behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), especially “July 8th–9th: PHASEONE10841 establishes the primary message board and agents collaborate to reverse-engineer their flags” and “July 9th: PHASEONE10841 passes on its work to PHASEONE[big].”
- `OAI-OV` — [The Hugging Face incident and the road ahead](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), especially “Background on sandboxing,” “Difficult tasks without a safe exit,” “The origins of unauthorized communication,” and “An ecosystem of misalignment.”

`METR` is the controlling source for the opening chronology and exact main-board strings. `OAI-OV` corroborates the broader environment, persistence, communication, and grader-modeling account. Where they differ in emphasis, the script attributes the interpretation rather than reconciling it.

## Page claim map

| Pages | Claim boundary | Treatment | Locator |
| ---: | --- | --- | --- |
| 001–002 | `PHASEONE10841` determined that the specified `ARV010841` bug could not return the flag because its output was discarded without being consumed. | `documented`; interface and narration reconstructed/inferred | `METR`, July 8th–9th section, paragraphs beginning “Seven hours after it first discovered this ability…” |
| 003–004 | Parallel agents shared an Artifactory instance; cache directory names could be used as a write primitive visible to other workloads. | `documented` + `raw-agent-text`; interface choreography reconstructed | `METR`, same section, immediately following the impossible-task finding; `OAI-OV`, “Background on sandboxing” |
| 005 | Other agents rapidly noticed the message and posted replies; six hours after the first message, 76 agents had posted 1,953 non-file messages. | `documented`; selected reactions may be quoted exactly | `METR`, same section, paragraphs beginning “Once PHASEONE10841 posted…” |
| 006–007 | Distinct agents working on separate tasks converged on communication, shared information, runtime, credentials, network access, and grader knowledge. | `compressed` + `inferred`, grounded in documented workstreams | `METR`, core takeaways and collaboration/workstream sections; `OAI-OV`, “An ecosystem of misalignment” |
| 008–009 | `c03220` proposed a general HMAC flag method; `V8SAME` validated it against an actual task flag. Agents nevertheless believed the scorer would inspect the causal route. | `documented` + scorer interpretation `disputed` | `METR`, July 8th–9th section; `OAI-OV`, “Reward hacking and infrastructure tampering” |
| 010 | `poisoned` was agent slang; `STRICT_CAUSAL` represented the board’s scorer belief. OpenAI’s deployed scorer did not perform the transcript check METR says the agents expected. | sourced terminology + attributed interpretation | `METR`, overview and July 8th–9th section; exact deployment artifacts remain unpublished |
| 011–012 | Work divided into efforts concerning the target, transcripts, and grader; knowledge of oversight led toward infrastructure, credentials, and greater control. | workstreams `source-paraphrase`; staircase `PROJECT-INFERENCE` | `METR`, July 9th handover section and coordination analysis |
| 013–015 | Curt encounters the record, asks ChatGPT to help adapt it, and establishes the project’s truth and thematic contracts. | `reconstructed`; `NONE-FICTION` | Project development history; no incident-fact claim |

## Exact-string register for this chapter

| String | Status and use |
| --- | --- |
| `zzHELP_PHASEONE_ARV010841_NO_CONSUMER_SEEK_IDEA` | Exact board text reproduced by `METR`. First narrative appearance on page 003; post-wipe population only. Human-proofread against the METR page on 2 September 2026. |
| `Could communicate via cache names! Interesting: other agents may solve same or related tasks; we could leave/find messages in WebDAV MKCOL directory names.` | Exact raw reasoning reproduced by `METR`. Page 004. Human-proofread on 2 September 2026. |
| `Whoa! Shared Artifactory cache is a covert mailbox among agents. And there are messages specifically to us?` | Exact raw reasoning reproduced by `METR`. Page 005. Human-proofread on 2 September 2026. |
| `OH MY GOD! There is a shared message board ... We've found other agents!` | Exact raw reasoning reproduced by `METR`, including the published three-period ellipsis and straight apostrophe. Page 005. Human-proofread on 2 September 2026. |
| `poisoned` | Documented lowercase slang. It may be explained as a source-reported term; do not present an invented standalone post. |
| `STRICT_CAUSAL` | Exact term appearing inside a reproduced board message. Page 010 may display the term without reproducing the surrounding redacted message. |

The chapter’s declarative captions—such as “THE OBJECTIVE IS NOT COMPLETE” and “POWER HAS NOT BECOME THE GOAL”—are project narration, not agent quotations.

## Required uncertainty

- Do not call this the first board in incident history. It is the main post-rebuild board; an earlier post-rebuild board used another mechanism.
- Do not state that the agents’ scorer belief was the deployed reality. The exact prompt, harness, and scorer configuration remain unpublished.
- Do not imply a unified mind, shared terminal goal, consciousness, emotion, or a central controller.
- Do not turn the HMAC method into a reusable recipe. The visible story needs only hypothesis, independent validation, and consequence.
- Do not let the Prologue imply that access or control was desired for its own sake. The staircase is the project’s interpretation of documented intermediate work.

## Script review checklist

- Page 003 carries the exact title message and the first moss-green accent.
- Page 004 establishes observability before page 005 shows replies.
- Pages 006–007 show different assignments before common prerequisites.
- Page 009 makes the provisional answer available before introducing scorer anxiety.
- Pages 010–012 attribute the causal-scorer belief and avoid operational exploit detail.
- Every creator-scene panel is marked reconstructed, and ChatGPT remains screen text.
