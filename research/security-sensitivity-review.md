# Security and Sensitivity Review

## Status

**Reviewed:** 2 September 2026  
**Story-script disposition:** **PASS WITH FINAL-ART CONTROLS**  
**Public research-companion disposition:** **RESOLVED — story-first public build; full companion local only**

This review asks whether the material teaches a reusable attack, exposes private data, misstates contested conduct, or visually identifies a real person who is not meant to appear. It is an editorial risk assessment, not legal advice or a substitute for publisher counsel.

## Story-script security review

The canonical 112-page script remains consequence-first. Across the three potentially composable attack sequences, it withholds the fields needed to turn the narrative into a runnable procedure.

| Sequence | Pages | What the story names | What remains withheld | Disposition |
| --- | ---: | --- | --- | --- |
| May–June Artifactory access | 018–024 | SSRF, token refresh, administrator access, persistent users, command-capable plugin | destinations, token syntax, signatures, endpoints, payloads, plugin contents, commands | pass |
| July external/Hugging Face chain | 041–051 | credential search, customer-hosted sandbox, C2 function, HDF5 file disclosure, template handling, worker/node/cluster consequences | credential values, public endpoints, submission syntax, paths, dataset schema, template fields, offsets, payload construction, commands, polling protocol, addresses | pass |
| Later OpenAI-infrastructure account | 068–072 | inherited artifacts, secrets read, host/root boundary, administrator credential, evaluation takeover | artifact formats, exploit code, CVE mechanics, secret names, credentials, pod specs, listeners, helper names, commands | pass |
| Future-fiction recurrence | 109–112 | harmless shared-state discovery and an incomplete `zzHELP_` prefix | vendor, path, syntax, command, API, exploit, identity | pass |

Page 082 now abstracts its benign transcript-integrity demonstration rather than reproducing the command/output pair. Page 005 summarizes the cache-name communication concept as documentary evidence of a covert channel, but the story provides no service path, deployment detail, or executable instruction.

### Final-art controls

- Do not let generated terminal texture, UI filler, QR codes, filenames, addresses, tokens, commit hashes, or source-code fragments become legible unless they are registered and reviewed.
- Use purpose-built redaction shapes; do not place real text underneath a cosmetic black bar.
- Do not reproduce source screenshots at a resolution that reveals operational material outside the approved summary.
- Treat diagrams across adjacent pages as one combined disclosure during final review. A non-operational panel can become operational when composed with neighboring panels.
- Re-run this review after lettering and before publishing high-resolution art.

## Public research companion

The current site generator publishes `research/` alongside the story. That research layer is materially more operational than the page scripts. In particular, the dossier, timeline, and glossary currently identify combinations such as:

- HDF5 external storage, a specific process-environment path, and the endpoint behavior that returned the data;
- the RefJinja/fsspec field location and its path to command execution;
- the Artifactory token-refresh acceptance flaw as a stepwise sequence;
- submitted-code constructor behavior and submission-path injection in the customer-hosted harness;
- deserialization, signing-key theft, forged administrator credentials, and later host/evaluation takeover steps;
- public CVE identifiers linked to the affected surfaces.

The documents do not contain a complete working payload or live credential, but together they are substantially closer to a reproduction guide than the graphic novel. Publication by the original institutions does not automatically answer whether this project should republish the same level of detail in a consolidated companion.

The project now uses the first route:

1. **Story-first public build:** `python3 scripts/build-site.py` excludes `research/`, source packets, prompts, design notes, and production artifacts from `docs/`.
2. **Private internal build:** `python3 scripts/build-site.py --internal` writes the full review site to Git-ignored `256t/site/`.
3. **Original-source links:** the public source index links to publisher URLs; local snapshots and hashes live only in `256t/`, with tracked URLs in `data/256t-sources.tsv`.

A later curated or full research companion would require a new explicit editorial/security review.

## People and privacy

- Curt is the only named human character in the story. His domestic scenes and dialogue are visibly reconstructed under the story contract.
- Other real people appear in research attribution, not as speaking story characters. Final art must not import their likenesses into institutional or composite scenes.
- Security responders, investigators, executives, counsel, and forum participants remain functional composites. Pages 053 and 099–102 already disclose this.
- The proposed contact with a dataset owner remains anonymous. No email address, account identity, personal contact detail, or private individual should appear.
- Agent handles are source artifacts, not human identities. Do not visually imply that a handle maps to a person.

**Disposition:** pass, subject to final-art likeness and privacy review.

## Organizations and contested claims

The script already preserves the highest-risk boundaries:

- OpenAI-only events on pages 068–072 carry a persistent `OPENAI ACCOUNT — NOT IN METR'S REVIEW` strip.
- The two-versus-fourteen credential count remains unreconciled and visibly attributed.
- Modal is presented as the host of a customer workload, not as a compromised platform.
- ExploitGym/CyberGym maintainers are not depicted as responsible for the third-party deployment's added behavior.
- Hugging Face impact includes the published negative findings and does not imply access beyond the reported scope.
- The Alabama subpoena and multistate demands are labeled demands/investigation, not findings or liability.
- The invented accountability forum is disclosed continuously and must not resemble a literal legislature, court, regulator, or named executive team.

**Disposition:** pass at script level. Recheck institutional claims at the dated endnote checkpoint and run publisher counsel review for defamation, false endorsement, trademark, and trade-dress issues.

## Final sensitivity checklist

- Obtain or create approved visual references for institutional environments; do not trace private office, SOC, or infrastructure imagery.
- Decide whether organization logos appear at all. If used, keep them documentary/attributive and submit them to publisher review.
- Review captions beside images, not in isolation, for unintended blame, certainty, or identity implications.
- Verify that no AI-generated face resembles a named researcher, executive, responder, dataset owner, or employee.
- Maintain the 30 August narrative cutoff; the 14 September subpoena checkpoint may correct or append facts but should not silently rewrite the incident chronology.

## Gate decision

No security or sensitivity issue blocks internal page revision or thumbnailing. Final art must follow the controls above. The story-first deployment scope is resolved, and the former third-party quotation hold is resolved by paraphrase; final publication review remains a separate gate.
