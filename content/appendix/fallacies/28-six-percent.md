---
id: LF-28
kind: fallacy
fallacy: base-rate-neglect
title: Six percent read as a size
pages: [075]
attributed_to: book
---

## Where it appears

Page 075: `ENTRIES BEGINNING WITH zz ARE ABOUT SIX PERCENT OF THIS DUMP.` — set among
captions establishing that most transcripts run to millions of tokens, that broad coverage is
not complete coverage, and that the available human review window was six days.

## Why the reasoning does not carry

Six percent invites two opposite misreadings and the page depends on neither.

Read as small, it suggests a marginal phenomenon inside a large corpus. Read as large, it
suggests that a twentieth of everything the evaluation produced was board activity. Neither
follows, because the denominator is a dump of entries and the numerator is entries with a
naming convention, and an entry is not an agent, a message, a transcript, or an hour of
activity. The book's own population rules say this in general terms: entries, messages,
transcripts and agents are not interchangeable and must never be summed across units.

The figure's actual work on the page is different and smaller. It establishes that the
board-related material was findable by a string match, which is why an AI-assisted search
could be pointed at it at all — and, by implication, that anything not carrying the
convention was not found this way.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The figure and its context | [METR/Redwood investigation](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | The corpus description, the proportion, and the review window. |
| Method | [METR investigation methodology](https://metr.org/blog/2026-07-28-investigating-ai-propensities-after-incidents/) | 28 Jul 2026 | How the corpus was made queryable, which is what the proportion is a proportion of. |
| Other counts, other units | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | 76 agents and 1,953 non-file messages at six hours, roughly 1,300 transcripts — different units over different windows. |
| The unit rule, stated | [research/collusion/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/collusion/README.md) | 2026 | The population rules governing how counts of distinct object types may be quoted and combined. |
| Where the same error appears | [research/cotra-hardfork-interview.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/cotra-hardfork-interview.md) | 6 Sep 2026 | The assessment of host-supplied agent counts, and why unit-mixing makes them unusable rather than wrong. |
| A second naming convention | [Discovery of a new OpenAI agent message board](https://collusion.wiki/) | 4 Sep 2026 | Sort-last naming as an independent habit in a separate population — evidence that the convention is a behaviour, not an index. |

See [CA-11](#ca-11-whether-an-ai-mediated-investigation-can-establish-what-it-reports) and [LF-25](#lf-25-hedged-speculation-carried-forward-as-a-finding).
