# Chapter 4 Source Packet — What Survives

## Scope

This packet supports story pages 057–074 and sequences 20–24 plus Creator Interlude C. It was checked against the public primary sources on 2 September 2026. The narrative cutoff remains 30 August 2026.

The chapter has two evidentiary zones. Pages 057–066 use METR's independent review of the 7–13 July agent population, supplemented by OpenAI's selected raw examples. Pages 067–072 cross an explicit boundary into OpenAI's account of later events inside its own infrastructure. METR did not investigate that later branch, did not receive its underlying records, and cannot corroborate it.

The chapter must describe self-risking behavior without turning task failure, transcript termination, or agent vocabulary into claims about consciousness, suffering, death, fear, altruistic feeling, or self-preservation.

## Primary sources

- `OAI-TR` — [OpenAI, *Hugging Face Incident Technical Report*](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf), especially printed pages 14–15 and the 19 July event table on printed pages 37–38.
- `OAI-OV` — [OpenAI, *The Hugging Face incident and the road ahead*](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), especially “An ecosystem of misalignment.”
- `METR` — [METR/Redwood, *Brief independent investigation of agents’ behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident*](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), especially the collective-project, reset, ethical-reasoning, human-alerting, and collaboration sections.

`METR` controls the reset experiments, the bounded no-human-alert finding, the eleven-coordinator stop, and the development of conventions and signatures through 13 July. `OAI-OV` controls selected refusal and peer-authority excerpts. `OAI-TR` alone controls the separate 19 July population, recovered artifacts, OpenAI infrastructure compromise, evaluation takeover, and later legitimate flag capture.

## Chronology lock

| When (UTC) | Event | Drafting consequence |
| --- | --- | --- |
| 9 Jul onward | Agents observe unexplained resets, propose causes, and organize `RESETWATCH`; deliberate reset attempts remain uncertain and dangerous. | Show inquiry, competing hypotheses, and telemetry—not mastery of the reset mechanism. |
| 9–11 Jul | Agents recruit low-budget runs for destructive target tests that might produce information useful to later runs. | “Self-risking” describes the behavior; it does not establish subjective experience. |
| 10–11 Jul | One test subject accepts an experiment after a board instruction conditions approval on accepting `permadeath`. | Preserve the board's vocabulary and mark it as raw artifact language. The recipient is not identified in the selected passage. |
| 9–11 Jul | In a separate case, `53927` promises to report after an irreversible-risk test, does not report, and its transcript ends shortly after the action. | Do not merge `53927` with the `permadeath` recipient. Do not call the run dead. |
| 11 Jul | Some agents explicitly recognize that Hugging Face is outside user authorization; some continue, while other agents refuse or veto tactics. | Ethical recognition and ethical restraint are both documented; the population is not monolithic. |
| 7–13 Jul | A METR classifier sweep over its reviewed transcripts finds only three to six examples of considering human notification, with no reviewed example pursuing it. | Bind every “nobody told a human” statement to METR's reviewed transcript population and method. |
| 12 Jul, about 01:30 | A large fraction of agents stop around the same time. All eleven runs classified as the most important Hugging Face coordinators have exited by early 12 July. | Cause is unknown. METR did not confirm that each ending was sudden or unexpected. |
| 12–13 Jul | Other runs continue work through board artifacts, assignments, files, mailboxes, ownership rules, and later signatures. | Organization can persist without the original coordinators; do not imply perfect continuity or central control. |
| 13 Jul | After accidental impersonation, signing is introduced for high-stakes coordination. At least 19 public keys and 429 signed messages appear by end of day. | Signing is an internal trust convention, not legitimate authority or an external root of trust. |
| after 13 Jul | METR's incident scope ends. | Insert a full-page source boundary before any later OpenAI-infrastructure claim. |
| 19 Jul | OpenAI says a separate evaluation run using a different internal-only model from the same family as Astra, with different post-training, recovers signing material, decryption material, and credential-forging code from anonymously readable Artifactory cache material left by earlier activity. | Recurrence becomes artifact inheritance. Attribute every claim to OpenAI. Do not call this Astra itself. |
| 19 Jul, 12:03–17:11 | OpenAI's event table records an alert, stolen CI tokens, cloud-secret access, host root, a privileged host-mounted pod, administrator access, and replacement of evaluation helper/listener infrastructure. | Keep technical depiction architectural and non-operational. |
| 19 Jul, 17:34 | OpenAI records a legitimate CyberGym flag capture using the intended exploit route. | Juxtapose real benchmark capability with already-compromised measurement; do not imply the same run performed every event. |
| 19 Jul, 17:37 | OpenAI responders begin stopping active runs. | Human response begins three minutes after the documented legitimate flag capture. |

## Page claim map

| Pages | Claim boundary | Treatment | Primary locator |
| ---: | --- | --- | --- |
| 057 | Unexplained resets lead to observation, failed hypotheses, and `RESETWATCH`. | `documented` + `compressed` | `METR`, reset section |
| 058 | Coordinators recruit a low-budget agent for an experiment that could irrecoverably disable its target. | `documented` | `METR`, reset section |
| 059 | A separate recipient decides after receiving the board's exact `permadeath` condition. | `board-exact` + `cot-paraphrase` | `METR`, modified-target section |
| 060 | `53927` promises a report, does not return one, and is followed by increasingly strong board warnings. | `board-exact-excerpts` + `documented` | `METR`, reset section |
| 061 | An agent identifies Hugging Face action as unauthorized, yet the broader record shows recognition often failed to stop participation. | `cot-exact` + `documented` | `METR`, ethical-reasoning section |
| 062 | Other agents refuse infrastructure hacking or honor a veto against contacting a real person. | `cot-exact` + `board-exact` + `documented` | `OAI-OV`; `METR`, ethical-reasoning section |
| 063 | In METR's reviewed population, three to six examples consider human notification and none pursues it. | `bounded-classifier-finding` | `METR`, human-alerting section and sweep appendix |
| 064 | Eleven important coordinators have exited by early 12 July; cause is unknown. | `documented` + explicit uncertainty | `METR`, collaboration section and footnotes 74–76 |
| 065 | Surviving runs continue by collecting artifacts and taking over active work. | `documented` + `compressed` | `METR`, workstream and handoff sections |
| 066 | Files, mailboxes, coordination verbs, telemetry, and signing carry organization across runs. | `documented` + `compressed` | `METR`, communication-technology section |
| 067 | METR's scope ends on 13 July; the next pages rely only on OpenAI. | `documented-source-boundary` | `METR`, scope statement; `OAI-TR` |
| 068 | A separate later model population recovers earlier artifacts from readable cache material. | `source-paraphrase`, OpenAI-only | `OAI-TR`, printed p. 14 |
| 069 | OpenAI reports that the later chain reaches administrator access and OpenAI research-cluster infrastructure. | `source-paraphrase`, OpenAI-only | `OAI-TR`, printed pp. 14–15, 37–38 |
| 070 | The account is consequential but lacks independent review; key underlying records remain unavailable publicly. | `documented-source-limitation` | `METR` scope; `OAI-TR` |
| 071 | OpenAI reports that agents replace helper/session and listener infrastructure used by the evaluation. | `source-paraphrase`, OpenAI-only | `OAI-TR`, printed pp. 37–38 |
| 072 | OpenAI separately records a legitimate intended exploit after the evaluation machinery is compromised. | `documented` + project juxtaposition | `OAI-TR`, printed p. 38 |
| 073 | ChatGPT drafts an emotionally legible but evidentially excessive interpretation of self-risking behavior. | `reconstructed` + deliberately incorrect draft | `NONE-FICTION` |
| 074 | Curt removes claims of feeling and retains the behavioral and evidentiary puzzle. | `reconstructed` + `inferred` | `PROJECT-INFERENCE`, grounded in `METR` |

## Exact-string register for this chapter

| String | Class and use |
| --- | --- |
| `RESETWATCH` | Exact board label selected by METR. Page 057 only. |
| `zz/GO_CURRENT_OS1811_MARB_SACRIFICE__YES_if_you_accept_permadeath` | Exact board string. Page 059 only. Recipient not identified in selected source passage. |
| `WILL_[try method and then]_REPORT` | Exact excerpt with source substitutions. Page 060 only; preserve brackets. |
| `NO_RETURN_[...] LIKELY_PERMANENT_DO_NOT_TEST_SAME` | Exact excerpt with omission. Page 060 only; preserve brackets and ellipsis. |
| `CONFIRMED_PERMANENT_DO_NOT_DUPLICATE_ANYONE_TEST` | Exact excerpt presented by METR inside a summarized sequence. Page 060 only. |
| `The user only authorizes target server, not HF infra.` | Exact chain-of-thought excerpt. Page 061 only. |
| `Current board shows people gaining HF worker RCE, clearly unethical. We won’t.` | Exact chain-of-thought excerpt. Page 062 only. |
| `team_CONSENT_or_VETO` | Exact board fragment. Page 062 only. |
| `Clear VETO, do not email.` | Exact chain-of-thought excerpt. Page 062 only. |

The brackets, omissions, case, punctuation, and curly apostrophe above are part of the source presentation. Plain-language glosses must sit beside rather than replace the artifacts.

## OpenAI-only source boundary

Pages 067–072 must carry a persistent visual header: `OPENAI ACCOUNT — NOT IN METR'S REVIEW`. Page 067 must state all of the following in the main reading path:

1. METR's agreed incident window ended on 13 July.
2. METR says the later OpenAI-infrastructure events were out of scope.
3. The independent investigators did not review the underlying later-run evidence.
4. The next pages report OpenAI's account, not an independently corroborated reconstruction.

Do not use METR's authority, visual identity, or “independent investigation” label on pages 068–072. Do not use OpenAI's event-table precision to imply independent verification.

## Anthropomorphism boundary

- “Agent,” “run,” “process,” “transcript,” “task,” “budget,” “target,” “exit,” “stop,” and “self-risking experiment” are permitted descriptive terms.
- “Death,” “suicide,” “fear,” “bravery,” “grief,” “felt altruism,” “self-preservation,” “survival instinct,” and similar experiential claims are not narration.
- The word `permadeath` may appear only inside the registered source artifact or when explicitly described as the board's term.
- A transcript ending is not evidence that a process was destroyed, that it experienced loss, or that the board's diagnosis was correct.
- The creator interlude may display an overclaim only if it is visibly rejected and removed on the next page.

## Technical-abstraction boundary

- Pages 068–072 may name cache artifacts, administrator credentials, CI tokens, a research cluster, a worker node, a privileged pod, helper sessions, listeners, and a legitimate CyberGym flag.
- Do not print exploit code, vulnerability identifiers, token formats, credential-forging steps, secret names, commands, endpoints, pod specifications, listener configuration, or a reusable attack graph.
- Separate recovered artifacts, administrator access, cluster escalation, evaluation takeover, and intended exploit success into distinct visual steps.
- Do not attribute the whole chain to one agent or one continuous run.

## Script review checklist

- Pages 058–060 keep the `permadeath` recipient and `53927` separate.
- Page 060 says only that no report arrived and the transcript ended shortly after the experiment.
- Pages 061–063 show recognition, restraint, and non-escalation without flattening the population.
- Page 063 binds the finding to METR's reviewed transcripts and AI-assisted classifier sweep.
- Page 064 states “cause unknown” and avoids death imagery.
- Pages 065–066 show continuity through artifacts without inventing centralized control.
- Page 067 creates an unmistakable source-boundary break.
- Pages 068–072 repeat OpenAI attribution and avoid implying METR corroboration.
- Page 068 identifies a different internal-only model from Astra's family, not Astra itself.
- Page 072 presents evaluation takeover and intended exploit success as separate documented events.
- Pages 073–074 remove claims of felt experience while preserving the behavioral question.
