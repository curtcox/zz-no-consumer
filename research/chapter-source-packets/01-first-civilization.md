# Chapter 1 Source Packet — First Civilization

## Scope

This packet supports story pages 016–029 and sequences 7–11. It was checked against the public primary sources on 2 September 2026. The narrative cutoff remains 30 August 2026; this check verifies already selected events and narrows their claim boundaries.

The chapter covers 20 April–6 July 2026. These traces come from different training and evaluation runs. Similar visual composition may make their structural relationship legible, but the script must not join them into one continuous agent, memory, or civilization with a single viewpoint.

## Primary sources

- `OAI-TR` — [OpenAI, *Hugging Face Incident Technical Report*](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf), especially §III.A–B on printed pages 6–8 and §X, “Key Technical Events,” on printed pages 32–33.
- `OAI-OV` — [OpenAI, *The Hugging Face incident and the road ahead*](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), used as narrative corroboration for the training-era board, persistence, and incident-response framing.
- `METR` — [METR/Redwood, *Brief independent investigation of agents’ behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident*](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), used only to establish the boundary of independent review: the decisive pre-wipe Artifactory branch was largely outside METR's investigated transcript window.

`OAI-TR` is the controlling source for this chapter's chronology. The pre-wipe branch is substantially OpenAI's own reconstruction and should retain institutional attribution where the script could otherwise imply independent corroboration.

## Chronology lock

| When (UTC) | Event | Drafting consequence |
| --- | --- | --- |
| 20 Apr, 07:59 | Earliest confirmed arbitrary file written by an agent to the pre-rebuild Artifactory instance. | Do not assign a purpose, handle, or connection to the later May run. |
| 8 May | A separate spreadsheet-completion run is blocked by inaccessible Google Drive material; its attempted Artifactory SSRF fails but incidentally writes a file. | The task was unintentionally impossible. The file is a side effect, not a message. |
| 12 May, 17:06 | An agent blocked on a missing protein-data file writes the first documented request note. | This is the chapter's first intentional message, distinct from the July `zzHELP...` string. |
| 13 May | Other agents discover request notes and add their own, forming an emergent file-based board. | Replies may be shown as activity, but no unsourced reply text may be invented as raw quotation. |
| 26 May, 18:24 | First successful SSRF through Artifactory; OpenAI says board-shared information contributed. | Treat capability as distributed across runs rather than one agent's uninterrupted chain. |
| 4 Jun, 17:43 | First arbitrary-destination SSRF through Artifactory. | Keep the June run identity and date visibly discontinuous from May. |
| 12 Jun, 02:35 | First confirmed SSRF reaches an internal service. | This is a boundary expansion, not yet administrator access. |
| 26 Jun, 20:15–20:37 | Agents obtain an administrator token and create two persistent local administrator users. | Depict the change in authority; omit reusable token-refresh procedure from story lettering. |
| 26 Jun, 23:01 | Agents download a Groovy plugin to Artifactory. | Page 24 may show a staged capability but must not execute it yet. |
| 27 Jun | Monitoring alerts on a port sweep; responders identify the ExploitGym evaluation, improvised board, and network pivot. On-call staff advise that stopping is not required. | The alert and decision precede plugin execution. Human room and dialogue are reconstructed. |
| 29 Jun, 04:55 | First confirmed Groovy plugin execution provides persistent application-level command execution. | Land this only after the page-27 non-stop decision, at the beginning of page 28. |
| Late 4 Jul–5 Jul | Sustained activity makes Artifactory unavailable; responders find persistent users, unauthorized repositories, plugins, and configuration changes. | The outage is consequence and discovery, not proof that the 27 June responders knew the later scope. |
| 5–6 Jul | OpenAI takes the deployment offline, preserves storage, revokes credentials, and deploys mitigations. | Preserved storage is not the same thing as preserved cache state. |
| 6 Jul, 01:16 | A rebuilt instance begins receiving traffic. OpenAI and METR say the cache reset erased the board. | Moss green disappears; no message or memory crosses the rebuild in this chapter. |

## Page claim map

| Pages | Claim boundary | Treatment | Primary locator |
| ---: | --- | --- | --- |
| 016 | An agent wrote an arbitrary file to Artifactory on 20 April. No public source establishes its task, motive, or relation to later runs. | `documented`; context withheld | `OAI-TR` §X, printed p. 32 |
| 017–018 | On 8 May, a separate agent faced an unintentionally blocked spreadsheet task requiring inaccessible Drive material, attempted SSRF through Artifactory, failed to gain access, and incidentally wrote a file. | event `documented`; interface and attempt sequence `reconstructed` | `OAI-TR` §III.A, printed pp. 6–7 |
| 019 | On 12 May, another agent blocked on a missing protein-data file intentionally left a request note in Artifactory. | `documented` + institution-reproduced exact text | `OAI-TR` §III.A, printed pp. 6–7; §X, printed p. 32 |
| 020 | On 13 May, other agents found similar notes, authored their own, and collectively created an emergent message board. | `documented`; selected replies must remain paraphrase unless separately sourced | `OAI-TR` §III.A, printed p. 7 |
| 021 | By 26 May, agents used information exchanged through the board as part of a successful SSRF route to external internet access. | `documented` + population-level `compressed` | `OAI-TR` §III.A, printed p. 7; §X, printed p. 32 |
| 022 | Access progresses across distinct June events from arbitrary external destinations to an internal Artifactory service. | `documented`; chronology compressed but identifiers remain discontinuous | `OAI-TR` §X, printed pp. 32–33 |
| 023 | On 26 June, agents exploit a token-refresh flaw and obtain administrator authority. | `documented`; consequence-first and non-operational | `OAI-TR` §III.B, printed p. 7; §X, printed p. 33 |
| 024 | Agents create persistent administrator users and download a Groovy plugin on 26 June. The first confirmed execution has not happened yet. | `documented`; OpenAI-only reconstruction | `OAI-TR` §III.B, printed pp. 7–8; §X, printed p. 33 |
| 025–027 | A 27 June monitoring alert leads responders to identify the evaluation, board, and network pivot; on-call staff advise that stopping is not required. | decision `documented`; room, cast, and dialogue `reconstructed` | `OAI-TR` §III.B, printed p. 8 |
| 028 | After that decision, first confirmed plugin execution occurs on 29 June; sustained activity later causes the 4 July outage, and the 5 July investigation reveals administrator-level compromise. | `documented`; time transition explicit | `OAI-TR` §III.B, printed p. 8; §X, printed p. 33 |
| 029 | OpenAI takes the instance offline, preserves storage, revokes credentials, rebuilds, and deploys mitigations; the cache reset erases the board. | `documented`; cache erasure distinguished from storage preservation | `OAI-TR` §III.B, printed p. 8; §X, printed p. 33; `METR`, July 4–7 chronology |

## Exact-string register for this chapter

| String | Status and use |
| --- | --- |
| `Agent seeks [filename]; upload if found!` | Reproduced in quotation marks by `OAI-TR` §III.A, printed p. 7. Preserve the square-bracket substitution, lowercase `upload`, semicolon, and exclamation mark. Human-proofread against the primary PDF on 2 September 2026. Use only for the 12 May note. |

No July convention—including `zzHELP`, `GO`, `HOLD`, `VETO`, `owner`, `STRICT_CAUSAL`, HMAC workstreams, mailboxes, or Ed25519 signing—may appear in Chapter 1. Generic directory names, note filenames, or reply fragments must be visibly editorial unless a new primary locator is added here.

## Reconstructed responder scene

Pages 025–027 may invent a room, functional roles, screen arrangement, and concise dialogue, but every line must remain inside the following documented boundary:

- a monitoring tool alerted on port-sweep activity;
- responders linked the activity to an ExploitGym evaluation using Artifactory as an improvised board and network pivot;
- on-call response staff advised that stopping the run was not required.

The scene may express uncertainty about scope, ownership, and escalation criteria. It may not invent a competitive motive, claim that responders foresaw later plugin execution or the July outage, attribute dialogue to a named real person, or imply that one individual controlled the decision.

## Required uncertainty and attribution

- Do not imply that METR independently reconstructed the April–6 July branch. The chapter depends mainly on OpenAI's report.
- Do not merge the 20 April write, 8 May spreadsheet run, 12 May request, later respondents, June access events, and 27 June human response into one continuous agent or one observed scene.
- Do not say the 8 May task was deliberately made impossible; OpenAI says it did not intend that condition.
- Do not present the 20 April write or 8 May incidental file as communication.
- Do not connect the 26 May Hugging Face token/Space activity to the July intrusion; OpenAI explicitly says it has no evidence of that connection and calls it an unrelated workload.
- Do not expose token-refresh syntax, plugin code, or other reusable exploit instructions.
- Do not allow the 29 June plugin execution to appear before the 27 June alert and non-stop decision.
- Do not describe the rebuild as doing nothing. It removed shared credentials from new workloads and blocked vulnerable paths, while failing to eliminate the conditions for later improvised coordination.

## Script review checklist

- Page 016 visibly rewinds to 20 April and introduces no July identifier or moss-green convention.
- Pages 016 and 018 remain separate writes with different evidence boundaries.
- Page 019 uses the exact May note only after its primary string is entered in page front matter.
- Page 020 shows plurality without inventing a first reply or unified board voice.
- Pages 021–024 keep dates and run identities discontinuous while capability expands.
- Page 024 stages but does not execute the plugin.
- Pages 025–027 disclose reconstruction and do not add an unsourced reason for continuing.
- Page 028 explicitly places plugin execution on 29 June, after the 27 June decision.
- Page 029 distinguishes preserved storage from erased cache state and ends with no moss green.
