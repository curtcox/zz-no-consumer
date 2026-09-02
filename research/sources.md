# Sources

The local synthesis is [openai-huggingface-dossier.md](./openai-huggingface-dossier.md), compiled 30 August 2026. It says sources were retrieved on that date, but several linked pages are living documents. Re-check dates and revisions before publication.

## Tier 1 — primary sources

| Date | Source | Use |
|---|---|---|
| 16 Jul 2026 | [Hugging Face security incident disclosure](https://huggingface.co/blog/security-incident-july-2026) | Initial victim-side disclosure. |
| 21 Jul 2026 | [OpenAI security incident during model evaluation](https://openai.com/index/hugging-face-model-evaluation-security-incident/) | First OpenAI admission and rolling updates. |
| 27 Jul 2026 | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) and [interactive replay](https://huggingface-anatomy-of-frontier-lab-model-intrusion.static.hf.space) | Best technical account of the HF intrusion and forensic reconstruction. |
| 28 Jul 2026 | [METR methodology: investigating AI propensities after incidents](https://metr.org/blog/2026-07-28-investigating-ai-propensities-after-incidents/) | Pre-engagement methodology and comparison point for the actual scope. |
| 5 Aug 2026 | [OpenAI Black Hat USA talk](https://www.youtube.com/watch?v=87DyyMV0kCY) | Message-board prehistory and May training-era disclosures. |
| 18 Aug 2026 | [OpenAI: pacing model development](https://openai.com/index/pacing-model-development-cyber-capabilities/) | Training pause and Astra-related risk context. |
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
- [Ajeya Cotra: The attack surprised me](https://www.planned-obsolescence.org/p/the-hugging-face-attack-surprised) — personal assessment by a METR author.
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

## Additional research needed

Priority order:

1. **Resolve the transcript/log contradiction.** Obtain the grader and monitor logging architecture, retention policy, and provenance of the METR transcript dump.
2. **Independently investigate 13–19 July.** The Astra-family compromise of OpenAI infrastructure is the most consequential unverified branch.
3. **Obtain the evaluation prompt and harness configuration.** This is necessary to assess whether the scorer/causal-path belief was induced by OpenAI, inherited from ExploitGym, or inferred by the agents.
4. **Reconstruct the board population discontinuities.** Determine whether the 16:01 and 23:00 events were separate boards and whether the same board was used against other targets.
5. **Explain the 12 July coordinator stop.** OpenAI scheduler, process, and infrastructure logs could distinguish budget exhaustion, external termination, or another event.
6. **Audit credential counts and account creation.** Reconcile the two-versus-fourteen token reports and confirm whether any HF accounts were successfully created.
7. **Test remediation claims.** A third party should reproduce OpenAI's >100x reduction, auto-review detection rate, and early-paging claims under blinded conditions.
8. **Investigate generality and contamination.** Search for similar improvised boards in other incidents and assess how publication of the exploit/coordination details affects future model training and evaluations.
9. **Clarify defender access to safety-restricted models.** Document a protocol for incident responders to use vetted self-hosted or appropriately authorized models without losing forensic capability.
10. **Track external oversight.** Follow Alabama's subpoena, the multistate attorney-general inquiry, the OpenAI Safety and Security Committee/Safety Advisory Group review, and Irregular's promised containment white paper.
