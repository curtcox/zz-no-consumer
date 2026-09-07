---
id: FQ-09
kind: faq
audience: method
title: Can I check the book's work?
pages: [088, 105, 114]
answer: >-
  Yes, all of it. The manuscript, the research, the source index, the disagreement register,
  the tooling, and the site generator are one public GPL-licensed repository. Every claim
  resolves to a citation key, every key to a source, and every source to a public address
  where one exists.
---

## The short answer

Start wherever your doubt is.

- **Doubt a claim on a page?** The page file in `content/pages/` carries its provenance
  statuses and source keys; `research/scene-provenance.md` resolves the keys;
  `research/sources.md` resolves the sources with reliability tiers.
- **Doubt the reading of a source?** `research/disagreements.md` is the register of every
  place two sources conflict and what this project concluded about each.
- **Doubt what the book may assert at all?** `content/story-contract.md` is the contract,
  written before the drafting, including the sentences the book is forbidden to write.
- **Doubt a number?** Do not trust a number in prose. The tools derive them:
  `pagination.py report`, `panels.py report`, `novella.py report`, `appendix.py report`.
  Counts in prose go stale, which is why the contract forbids restating the page count as a
  fixed number anywhere, including in the contract.
- **Doubt this appendix?** `python3 scripts/appendix.py check` fails when an entry cites a
  page the book no longer has, when a contested entry quotes only one side, when a fallacy
  attributed to a named person lacks the dated statement it characterises, or when a
  professional objection files a guess with a source attached.

## The long answer

The reason a graphic novel ships with a validator suite is that the book makes a specific
promise — every claim carries its evidentiary status — and a promise of that shape decays
silently. Someone edits a caption to tighten it and the tightened version asserts slightly
more than the label allows. Someone moves a page and forty-one references in six trees now
point at the wrong number. Neither of those failures announces itself.

So the invariants are held by tooling instead of by memory. The three-digit page number is
the primary key of the whole project — the same number in the script, the prose, the
appendix, the beat sheet, the art keys and the site routes — and no page number is ever
edited by hand; `pagination.py` rewrites every occurrence in one deterministic operation and
refuses to change the recto/verso parity of the book without being told to. The continuous
integration workflow runs fourteen checks in sequence and the site does not publish if any
of them fails.

None of that makes the book right. It makes the book's mistakes findable, which is a
different and more achievable thing. Two of them are already documented in this appendix:
[LF-01](#lf-01-nothing-survived-the-rebuild-therefore-nothing-survived) is a step the book
took and had to withdraw, and [LF-03](#lf-03-a-model-produced-ranking-read-as-a-property-of-the-world)
is a construction it made on purpose and then disclosed on page 088. If you find a third,
the machinery for recording it already exists.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Auditable trail | [the repository](https://github.com/curtcox/zz-no-consumer) | 2026 | The manuscript, research, tooling and site generator in public, under one licence, with a full commit history. |
| Project record | [research/sources.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/sources.md) | 2026 | The canonical source index with reliability tiers, and the dates each source became available. |
| Project record | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 2026 | Every conflict between sources, with this project's working assessment of each. |
| Tooling record | [scripts/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/scripts/README.md) | 2026 | What each of the tools does, and which of them owns which files. |
| Where the rules live | [CLAUDE.md](https://github.com/curtcox/zz-no-consumer/blob/main/CLAUDE.md) | 2026 | The invariants, the ownership map, and the check suite that has to pass before the site publishes. |
| Licence | [LICENSE](https://github.com/curtcox/zz-no-consumer/blob/main/LICENSE) | 5 Sep 2026 | GPL-3.0-or-later, chosen so the book and its tooling can be forked as one thing. |
| Field practice | [Google SRE, postmortem culture](https://sre.google/sre-book/postmortem-culture/) | — | The argument that a record designed to make its own errors findable outperforms one designed to look correct. |
| What the repository cannot show | [data/256t-sources.tsv](https://github.com/curtcox/zz-no-consumer/blob/main/data/256t-sources.tsv) | 2026 | The source vault is deliberately not published: only canonical URLs and redistribution dispositions are tracked, because reuse rights are uncertain. |
