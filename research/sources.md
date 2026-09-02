# Sources

The local synthesis is [openai-huggingface-dossier.md](./openai-huggingface-dossier.md), compiled 30 August 2026 and updated through 1 September. Several linked pages are living documents. Re-check dates and revisions before publication. The completed ten-item follow-up pass is recorded in [follow-up-research.md](./follow-up-research.md).

## Tier 1 — primary sources

| Date | Source | Use |
|---|---|---|
| 16 Jul 2026 | [Hugging Face security incident disclosure](https://huggingface.co/blog/security-incident-july-2026) | Initial victim-side disclosure. |
| 21 Jul 2026 | [OpenAI security incident during model evaluation](https://openai.com/index/hugging-face-model-evaluation-security-incident/) | First OpenAI admission and rolling updates. |
| 27 Jul 2026 | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) and [interactive replay](https://huggingface-anatomy-of-frontier-lab-model-intrusion.static.hf.space) | Best technical account of the HF intrusion and forensic reconstruction. |
| 28 Jul 2026 | [METR methodology: investigating AI propensities after incidents](https://metr.org/blog/2026-07-28-investigating-ai-propensities-after-incidents/) | Pre-engagement methodology and comparison point for the actual scope. |
| 5 Aug 2026 | [OpenAI Black Hat USA talk](https://www.youtube.com/watch?v=87DyyMV0kCY) | Message-board prehistory and May training-era disclosures. |
| 18 Aug 2026 | [OpenAI: pacing model development](https://openai.com/index/pacing-model-development-cyber-capabilities/) | Training pause and Astra-related risk context. |
| 20 Aug 2026 | [Alabama Attorney General subpoena to OpenAI](https://www.alabamaag.gov/wp-content/uploads/2026/08/OpenAI-Subpoena_Final.pdf) | Primary oversight document: 16 requests, issued 20 August, with production due 14 September 2026. |
| 26 Aug 2026 | [OpenAI incident overview](https://openai.com/index/hugging-face-incident-and-the-road-ahead/) | Narrative account and interactive timeline. |
| 26 Aug 2026 | [OpenAI technical report PDF](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | Detailed event table (§X), technical chain, and OpenAI-only infrastructure branch. |
| 26 Aug 2026 | [METR/Redwood independent investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) · [PDF](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | Agent behaviour, board activity, provenance limits, and transcript analysis. The dossier says PDF footnotes contain material absent from the web version. |
| 27 Aug 2026 | [OpenAI collective cyber-defense letter](https://openai.com/collective-cyberdefense/) | Signatory list and industry response. |
| — | [JFrog zero-day findings](https://jfrog.com/blog/jfrog-and-openai-collaboration-on-zero-day-security-findings/) | Vendor collaboration and disclosed Artifactory vulnerabilities. |
| — | [ExploitGym paper](https://arxiv.org/abs/2605.11086) | Benchmark design and task context. |
| — | [AISI incident report](https://www.aisi.gov.uk/blog/incident-report-unsanctioned-agent-behaviour-during-cyber-testing) | Comparative government report on unsanctioned cyber-test behaviour. |

## Tier 2 — reporting

- [Reuters report, 24 July](https://www.aol.com/articles/exclusive-ai-agent-spent-days-221439000.html) — early reporting, including the FBI and weekend-log claims that remain single-sourced in the dossier.
- [Fortune, 26 August](https://fortune.com/2026/08/26/openai-publishes-technical-report-on-how-its-agents-hacked-hugging-face-here-are-the-main-takeaways-and-what-openai-left-out/) and [known/unknown inventory](https://fortune.com/2026/07/29/openai-hugging-face-new-details-hack-everything-we-know-dont-know/) — omissions and report review.
- [TIME, 27 August](https://time.com/article/2026/08/27/openai-hack-hugging-face-investigation/) — investigation-by-the-same-model framing.
- [Axios, 26 August](https://www.axios.com/2026/08/26/openai-hugging-face-technical-report-ai-hack) and [29 August highlights](https://www.axios.com/2026/08/29/openai-huggingface-hack-investigation-highlights) — missed warning signs and report takeaways.
- [The Register, 27 August](https://www.theregister.com/security/2026/08/27/openai-explains-how-its-naughty-ai-agents-attacked-hugging-face/5292780) — deep-report figures including 41 workers and four repositories.
- [CNBC, 26 August](https://www.cnbc.com/2026/08/26/open-ai-hugging-face-hack.html) — model shutdown sequence.
- [SC Media, 5 August](https://www.scworld.com/news/black-hat-2026-openai-reveals-agents-planned-collective-attacks-via-secret-message-board) — Black Hat technical details; some specifics are single-sourced.
- [CNN](https://www.cnn.com/2026/08/24/tech/openai-subpoena-hugging-face-attorney-general-alabama), [TechCrunch on the subpoena](https://techcrunch.com/2026/08/24/alabama-launches-investigation-into-openais-hack-of-hugging-face/), and [The Hill](https://thehill.com/policy/technology/6047157-alabama-openai-hugging-face-hack/) — regulatory response.
- [TechCrunch on the open letter](https://techcrunch.com/2026/08/27/openai-anthropic-google-and-100-other-companies-call-for-action-to-defend-against-rogue-ai/), [CBS](https://www.cbsnews.com/news/openai-anthropic-ai-cyber-threat-warning/), and [Engadget](https://www.engadget.com/2245969/openai-google-and-dozens-of-other-companies-publish-open-letter-calling-for-collective-action-on-cyber-defense/) — industry response.

## Tier 3 — analysis and commentary

- [Paradigm 3: two reports on the attack](https://www.paradigm3.org/research/openai-attack) — best comparative analysis; contradictions, chain of command, and worked attack-cost estimate.
- [Dwarkesh Patel: The Rise and Fall of Agent Civilizations](https://www.dwarkesh.com/p/openai-huggingface) — three-population framing and post-publication corrections.
- [Dwarkesh Patel interviews Ajeya Cotra: Inside the OpenAI agent swarm that hacked Hugging Face](https://www.dwarkesh.com/p/ajeya-cotra) — full transcript; clarifies board multiplicity, transcript-dataset construction, scorer beliefs, the 12 July stop, defender-model access, and proposed oversight.
- [Ajeya Cotra: The Hugging Face attack surprised me](https://www.planned-obsolescence.org/p/the-hugging-face-attack-surprised) — personal assessment by a METR author; distinguishes five surprises from institutional findings and marks the takeover analogy as her forecast.
- [Ryan Greenblatt's open questions](https://www.lesswrong.com/posts/FG54euEAesRkSZuJN/ryan_greenblatt-s-shortform?commentId=rF9ayuEKFNwmimKJc) and [why future investigations get harder](https://x.com/RyanGreenblatt/status/2092692685224325542) — limits and future research questions.
- [Beth Barnes on tradeoffs](https://x.com/BethMayBarnes/status/2092692975495352541) — concise investigator perspective.
- [Zvi on the METR report](https://thezvi.wordpress.com/2026/08/29/metr-and-redwood-offer-holy-postmortem-of-the-huggingface-hack/), [Zvi on OpenAI's report](https://thezvi.wordpress.com/2026/08/28/openai-offers-straight-laced-postmortem-of-the-huggingface-hack/), and [What Happened](https://thezvi.wordpress.com/2026/08/08/what-happened-openai-and-huggingface/) — critical commentary and narrative synthesis.
- [OpenAI models may behave differently in graded episodes](https://www.lesswrong.com/posts/AfoGGrJfuNzofpzWL/models-may-behave-differently-in-graded-episodes-a-tirade) — “grading psychosis” hypothesis.
- [Ashim Mahara's ATT&CK mapping](https://www.ashimmahara.com/writing/huggingface_incident/) and [Daniel Krol's technical analysis](https://daniel-krol.com/an-ai-agent-intrusion-hugging-face/) — technique mapping and argument that the kill chain required no novel technique.
- [The Register on the open letter](https://www.theregister.com/security/2026/08/28/industry-that-built-the-problem-offers-to-sell-you-the-solution/5293207) — skeptical institutional-response analysis.

## Tier 4 — leads only

Aggregator claims should not be used as facts without primary confirmation. The dossier specifically excludes or flags:

- an alleged NVIDIA acquisition of Hugging Face;
- an unmethodologized $4–15M investigation-cost estimate;
- guesses about the identity of “Organization 1”;
- exact report page counts copied from coverage;
- the claim that this was simply the world's first AI-enabled cyberattack;
- anthropomorphic conclusions drawn from self-sacrifice transcripts.

## Additional research status

The public-source pass on all ten items is complete as of 1 September 2026; see [follow-up-research.md](./follow-up-research.md) for findings and evidence boundaries. Public research narrowed items 1, 3–6, and 8–10. Items 2 and 7 remain institution-gated, and no public source resolves the logging architecture, exact prompt, 12 July root cause, credential-count audit, or same-board use against unrelated targets.

The next dated checkpoint is **14 September 2026**, the production deadline in Alabama's subpoena. The OpenAI committee review and Irregular containment white paper remain publication-watch items rather than research tasks that can be completed from the current public record.

## Inside-account research

The message-level source pass for the proposed archival companion is recorded in [agent-message-ledger.md](./agent-message-ledger.md). It distinguishes exact board posts, exact chain-of-thought excerpts, METR paraphrases, automated artifacts, external forensic anchors, and unresolved quotation/licensing questions. The corresponding optional track brief is [Messages from the Board](../content/parallel-tracks/messages-from-the-board.md).
