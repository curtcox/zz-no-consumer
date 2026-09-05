# Reuse inquiry — the wiki material

**Purpose.** Item 3 of [revision-priorities.md](../revision-priorities.md): before the book reproduces screenshots or extended excerpts of the wiki material, its custodians are asked which material may be reproduced and on what terms. Until they answer, the book uses attributed paraphrase and links, which need no permission. This file says what the material is, exactly where it is, and what to ask. Contact is a message the project owner sends; the project does not send it.

## What the material is

Three things, which the source index keeps under three keys:

| Key | What it is | Where | Form |
| --- | --- | --- | --- |
| `CW-EXPORT` | The corpus: every stored revision of the agent-written pages on four small self-hosted wikis (`dse`, `probier`, `fractal`, `dorfwiki`), the save/delete/revert/probe events around them, and per-handle rollups. 14,591 revisions with full body text, 4,579 pages, 19,913 events, 3,103 handles, a manifest with 58 named facts and 13 self-checks, and SHA-256 sums. Revisions run 24 May to 2 July 2026; events run 17 May to 14 July. | In this repository, [`research/collusion/`](./README.md): `pages.jsonl`, `revisions.jsonl`, `events.jsonl`, `labels.jsonl`, `manifest.json`, `SHA256SUMS`. Exported 3 September 2026 by the report's `explorer-schema-2` tool from a SQLite database whose hash the manifest records. | Plain JSONL. Verify with `cd research/collusion && shasum -a 256 -c SHA256SUMS`. |
| `CW-REPORT` | The authors' report: *Discovery of a new OpenAI agent message board*, 4 September 2026, by Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts and Thomas Larsen. It interprets the corpus: about 18,000 posts by autonomous agents using the public internet during a web-retrieval task; attribution of the traffic to OpenAI by inference; the assessment that this population was probably distinct from the Hugging Face swarm; and the statement that, as of 4 September, OpenAI had not publicly disclosed the wiki incident. | [https://collusion.wiki/](https://collusion.wiki/) | Web page. No licence, copyright notice, or terms of use appear on it. |
| `CW-EXPLORER` | The authors' hosted, redacted copy of the wikis, with deleted pages reconstructed, readable page by page with revision histories and diffs, and a download option. Example page histories the proposal cites: the [construction-wage thread](https://collusion.wiki/explorer/page/dse~DataUSAConstructionWageSep18Live.html), its [`ZZZ` backup](https://collusion.wiki/explorer/page/dse~ZZZDataUSAConstructionWageLive.html), the [OECD precision thread](https://collusion.wiki/explorer/page/dse~OECDJun26PrecisionScout.html), and the [heartbeat history](https://collusion.wiki/explorer/page/dse~Apr23CVDHorizonBeacon2025.html). | Linked from the report; explorer pages under `https://collusion.wiki/explorer/page/…`. During the 4 September review these pages showed a draft, non-sharing notice even though the report invites analysis. | Web pages and a download. The notice is why this inquiry exists. |

The wikis themselves are third-party public sites. The report names prowiki.org's DSE wiki ([https://prowiki.org/dse/](https://prowiki.org/dse/), which warns that it logs IP addresses) as where the agents wrote. The live wiki is the original; the authors' copy is redacted (personal data removed, non-agent traffic excluded except moderator deletions) and reconstructs deleted pages from histories.

## How to get it

1. **The corpus** is already here. Clone the repository, run the checksum command above, and read [`README.md`](./README.md) for the schema, joins, and the population rules that govern how counts may be quoted.
2. **The report** is the web page at collusion.wiki. A link-only record of it is in the vault manifest ([`data/256t-sources.tsv`](../../data/256t-sources.tsv), id `collusion-wiki-report`); `python3 scripts/sync-256t.py sync` fetches a local snapshot into the ignored `256t/` directory.
3. **The explorer** is reached from the report's links. Its download option provides the same corpus the repository holds; use the repository copy for anything the book cites, so every quotation is checksummed.

## Who to ask, and what

**Custodians:** the four authors. The report gives one contact: **sydney@nightingalecollective.org** (Sydney Von Arx, Nightingale Collective, [https://nightingalecollective.org/](https://nightingalecollective.org/)).

**What the book wants to know:**

1. Whether the explorer's draft, non-sharing notice still applies, and to what: the explorer pages, the download, the report text, or all three.
2. Whether screenshots of explorer page histories, or excerpts of stored revisions longer than a sentence, may be reproduced in a published graphic novel and on its public site, and under what attribution.
3. Whether the corpus export may remain in a public repository as it is now (it is already public in this repository; if they object, it moves to the ignored vault and the site links to their copy instead).
4. How they wish to be credited, and whether the Nightingale Collective affiliation should appear.
5. Whether they know of any reuse restriction on the underlying wikis' content that the book should observe.

**What the book does not ask for:** raw request logs, unredacted data, or identities. The proposal's list of evidence that could discriminate between the connection hypotheses ([collusion-story-revision.md](../collusion-story-revision.md), "What could discriminate") is a research wish-list for the custodians of the *OpenAI* records, not for these authors.

## A message the owner could send

> Subject: Reuse of the collusion.wiki material in a documentary graphic novel
>
> I am writing a documentary graphic novel about the OpenAI / Hugging Face incident (repository: https://github.com/curtcox/zz-no-consumer). Your 4 September report and the wiki corpus are the only public record of the wiki activity, and the book would like to depict a small part of it: the construction-wage thread, its ZZZ backup, and the administrator's deletions on 19 June, as dated historical scenes with your attribution.
>
> Your explorer pages showed a draft, non-sharing notice when I reviewed them. Could you tell me (1) whether that notice still applies and to what, (2) whether screenshots of explorer page histories or excerpts of stored posts may be reproduced in the book and on its public site, and under what credit, (3) whether the JSONL export may stay in the public repository, and (4) how you would like to be credited?
>
> Until I hear from you the book uses only attributed paraphrase and links to your site, which I will do in any case if you prefer.

## Record the answer here

| Date | From | Answer | Effect on the book |
| --- | --- | --- | --- |
| — | — | not yet sent | paraphrase and links only |
