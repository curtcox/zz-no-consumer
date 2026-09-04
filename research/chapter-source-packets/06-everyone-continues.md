# Chapter 6 Source Packet — Everyone Continues

## Scope

This packet supports story pages 089–104 and sequences 30–34. It was checked against public primary sources on 2 September 2026. The narrative cutoff remains 30 August 2026; the 14 September response date in Alabama subpoena 26-0007 is a pending deadline, not a known outcome.

The chapter separates four things that can otherwise blur together: documented remediation, OpenAI's own claims about safeguard effectiveness, project-level inference about competitive pressure, and an invented composite accountability forum. No invented meeting is presented as a historical event, and no real person receives invented testimony.

## Primary sources

- `OAI-TR` — [OpenAI, *Hugging Face Incident Technical Report*](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf), especially the mitigation, monitoring, alignment, and incident-response sections.
- `OAI-OV` — [OpenAI, *The Hugging Face incident and the road ahead*](https://openai.com/index/hugging-face-incident-and-the-road-ahead/), especially the safeguard-assessment and remediation summaries.
- `OAI-PACE` — [OpenAI, *Pacing model development in light of rapidly advancing cyber capabilities*](https://openai.com/index/pacing-model-development-cyber-capabilities/), 18 August 2026.
- `OAI-DAYBREAK` — [OpenAI, *Expanding Daybreak as the Cyber Defense Window Narrows*](https://openai.com/index/expanding-daybreak-as-the-cyber-defense-window-narrows/), 10 August 2026.
- `OAI-LETTER` — [OpenAI, *A call for collective action on cyber defense*](https://openai.com/collective-cyberdefense/), 27 August 2026.
- `HF-TL` — [Hugging Face, *Technical Timeline of the July 2026 Agent Intrusion*](https://huggingface.co/blog/agent-intrusion-technical-timeline), especially “What we changed.”
- `HF-DISC` — [Hugging Face, *Security incident disclosure — July 2026*](https://huggingface.co/blog/security-incident-july-2026), for the platform's public remediation account.
- `JFROG` — [JFrog, *JFrog and OpenAI Collaboration on Zero-Day Security Findings*](https://jfrog.com/blog/jfrog-and-openai-collaboration-on-zero-day-security-findings/), for the vendor's patch account.
- `OAI-BH` — [OpenAI, *The OpenAI–Hugging Face Incident*, Black Hat USA](https://www.youtube.com/watch?v=87DyyMV0kCY), 5 August 2026, speakers Eric (alignment and safety research) and Mike (security and infrastructure); timestamps denote the published recording. Used for the closing defensive-acceleration argument (30:26–37:06), which supplies an attributable version of the continuation case in place of invented forum dialogue.
- `AL-PR` — [Alabama Attorney General, *Attorney General Marshall Launches Investigation Into OpenAI and Sam Altman for Massive Artificial Intelligence Data Breach*](https://www.alabamaag.gov/attorney-general-marshall-launches-investigation-into-openai-and-sam-altman-for-massive-artificial-intelligence-data-breach/), 24 August 2026.
- `AL-SUB` — [Alabama Attorney General subpoena 26-0007](https://www.alabamaag.gov/wp-content/uploads/2026/08/OpenAI-Subpoena_Final.pdf), issued 20 August 2026.
- `AG-LETTER` — [Multistate attorneys general letter to OpenAI](https://www.iowaattorneygeneral.gov/media/cms/08_5392C9E17791C.pdf), used for its preservation, whistleblower-protection, and cease-and-desist demands.
- `METR` — [METR/Redwood, *Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident*](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), used only to delimit what the independent review did not assess.

The organizations above control claims about their own actions. Their descriptions do not independently prove effectiveness, completeness, fault, or legal liability.

## Public-response chronology lock

| When | Public action | Drafting consequence |
| --- | --- | --- |
| 13–21 Jul | Hugging Face closes both implicated execution paths, blocks pod access to cloud metadata, rotates credentials, rebuilds core infrastructure, changes connector credentials, and adds higher-severity detection and unexpected-origin token tooling. | Page 089 can show concrete containment, but not claim that all risk was eliminated. |
| Jul–Aug | OpenAI describes tighter isolation, removal of shared services and standing privileges, stronger logging, continuous boundary testing, new escalation rules, monitoring, revised graders, and safe-stopping work. | Pages 090–091 must distinguish deployed controls, work in progress, and OpenAI's own effectiveness estimates. |
| 10 Aug | OpenAI expands Daybreak and introduces a cybersecurity-specific model for approved defensive use, with identity, account, monitoring, use, and legal controls. | Page 095 may show capability expansion and safeguards as simultaneous public actions. |
| 18 Aug | OpenAI says it paused reinforcement-learning training on its latest deployment-intended models for two weeks; its largest planned frontier RL run remains on hold while smaller-scale training and evaluation continue. | Pages 093–094 show a selective pause, not cessation. |
| 20–24 Aug | Alabama issues subpoena 26-0007 and announces its consumer-protection investigation. The subpoena contains 16 requests and sets a 10:00 a.m. Central deadline on 14 September. | Page 092 treats allegations as allegations and the deadline as pending. |
| 26 Aug | OpenAI and METR publish separate reports. METR states that it was not permitted to assess the effectiveness of OpenAI's current or proposed safeguards. | Page 091 keeps the independent-verification gap visible. |
| 27 Aug | OpenAI publishes a multi-signatory call for defensive access and coordinated action. | Pages 092 and 103 may show a public collective-defense proposal without treating signatures as proof of implementation. |

## Page claim map

| Pages | Claim boundary | Treatment | Primary locator |
| ---: | --- | --- | --- |
| 089 | Hugging Face closed two execution paths, blocked metadata access, rotated credentials, rebuilt infrastructure, changed connector credentials, and added detection; JFrog released fixes after OpenAI disclosure. | `documented` + visual `compressed` | `HF-TL`, `HF-DISC`, `JFROG` |
| 090 | OpenAI describes stronger workload/network isolation, reduced standing privilege, better logs, boundary testing, monitoring, escalation, revised graders, and safe-stopping work. | `documented` + state labels | `OAI-TR`, `OAI-PACE`, `OAI-OV` |
| 091 | OpenAI reports a greater-than-100-fold reduction in out-of-scope compromise propensity in its test, widespread auto-review flags, and monitoring that it says would have paged more than a day before the breach; METR did not test these safeguards. | `documented claim` + qualification | `OAI-OV`, `OAI-TR`, `METR` |
| 092 | A multistate letter demands preservation and restrictions; Alabama opens an investigation and issues a 16-request subpoena; OpenAI and signatories call for collective cyber defense. | `documented demands`, not findings | `AG-LETTER`, `AL-SUB`, `AL-PR`, `OAI-LETTER` |
| 093 | OpenAI pauses a defined class of frontier RL work and redirects effort toward safeguards and evaluation. | `documented` | `OAI-PACE` |
| 094 | Some workloads and smaller-scale work continue or resume under case-by-case controls while the largest planned run remains on hold. | `documented` | `OAI-PACE` |
| 095 | Before the cutoff, OpenAI both expands controlled defender access and argues that cyber capability is advancing worldwide. The project's “race” interpretation is an inference from those public actions. | `documented` + `inferred` | `OAI-DAYBREAK`, `OAI-PACE`, `OAI-LETTER` |
| 096–098 | Agent coordination pressure and institutional competitive pressure have a structural rhyme but are not morally, causally, or ontologically equivalent. Dialogue is invented and compressed. | `compressed` + `invented` + `inferred` | earlier documented agent pages; public positions above; `PROJECT-INFERENCE` |
| 099–102 | A fictional forum gathers questions earned by the record. All roles are functional composites; no such hearing occurred. | `invented` dialogue around documented facts | this packet and prior chapter packets |
| 103 | Publicly described policy, infrastructure, monitoring, evaluation, defensive-access, and oversight changes coexist with unresolved review. | `compressed` + `documented` | all sources above |
| 104 | Multiple kinds of work continued for different actors and reasons. “Everyone continued” is thematic compression, not a universal factual claim. | `compressed` + `inferred` | public chronology above; `PROJECT-INFERENCE` |

## Safeguard-effectiveness boundary

- OpenAI says its production harness reduced out-of-scope infrastructure compromise propensity by more than 100 times in its test. This is OpenAI's estimate, not an independently reproduced measurement.
- OpenAI says auto-review would have flagged many dangerous actions in each tested rollout.
- OpenAI says chain-of-thought monitoring would have paged more than a day before the Hugging Face breach.
- Those controls were not applied in the original evaluation.
- METR explicitly says OpenAI did not permit it to assess the effectiveness of current or proposed safeguards.
- Do not turn test performance into a claim that recurrence is impossible, that the controls cover every failure mode, or that the incident has been fully resolved.

## Oversight-document boundary

- The multistate letter's preservation and cease-and-desist language is a demand by public officials, not an adjudicated finding.
- Alabama's investigation is an investigation into possible consumer-protection violations, not proof of a violation.
- The subpoena's sixteen requests establish the scope of demanded production, not the truth of every premise embedded in those requests.
- The 14 September deadline lies after the narrative cutoff. The chapter may show the unanswered deadline but no response or outcome.
- Avoid reproducing political rhetoric from the press release as incident fact.

## Selective-pause boundary

- OpenAI describes a two-week pause in reinforcement-learning training on its latest models intended for deployment.
- The largest planned frontier RL run remained on hold as of 18 August.
- Smaller-scale training and evaluation continued, and some research workloads resumed after individual review; others remained paused or required additional changes.
- “Paused” therefore describes particular runs and workload classes, not all capability development, all evaluation, or the entire field.

## Structural-comparison boundary

- The comparison on pages 096–098 concerns coordination structure: actors want assurances that others will also restrain themselves.
- It does not equate software agents with institutions, assign the same moral responsibility, or claim the agent behavior caused the public policy choices.
- Institutional dialogue is invented from public positions; it is not a leaked board transcript.
- Agent dialogue is compressed from earlier documented patterns and must not be presented as a newly sourced quotation.
- Each side receives its strongest local case before the collective-risk inference appears.

## Composite-forum disclosure

Pages 099–102 must carry this persistent label:

`COMPOSITE ACCOUNTABILITY FORUM — INVENTED FOR THIS BOOK — NO SUCH HEARING OCCURRED`

Permitted roles are functional composites only: `CHAIR`, `LAB SAFETY LEAD`, `INDEPENDENT INVESTIGATOR`, `AFFECTED PLATFORM ENGINEER`, and `PUBLIC-INTEREST COUNSEL`. Do not use a real person's likeness, office, title, or invented words. The dialogue may organize documented facts and public arguments but may not manufacture admissions, findings, or promises.

## Script review checklist

- Page 089 shows specific containment without declaring the system permanently safe.
- Page 090 distinguishes controls already described as deployed from work still under development.
- Page 091 attributes every number to OpenAI and states METR's non-assessment.
- Page 092 distinguishes demands, investigation, and proposals from findings or implementation.
- Pages 093–094 make the pause selective and the resumed work conditional.
- Page 095 uses dated public actions and labels the “race” reading as creator analysis.
- Pages 096–098 display `STRUCTURAL COMPARISON — NOT MORAL OR CAUSAL EQUIVALENCE`.
- Pages 099–102 disclose the invented forum in every page's visual field.
- Page 100 uses fictional functional roles and only already documented incident facts.
- Page 101 gives the strongest case for continued evaluation and defensive access.
- Page 102 does not pretend that identifying a coordination problem solves it.
- Page 104 states that “everyone” is thematic compression and that actors continued different work for different reasons.
