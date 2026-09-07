---
id: PR-28
kind: profession
profession: Air traffic controller
field: trades-and-operations
title: When you cannot work the traffic, you stop accepting traffic
pages: [041, 064, 075]
conjecture: none
reading: >-
  Page 075 establishes 1,300 very long transcripts and concludes that human-only review is
  impractical, then reaches for more machine capacity. A controller would recognise an overload
  and reach for the other lever: reduce the inflow until the work fits the position.
---

## What the practitioner would say

Capacity in this trade is not a target, it is a limit, and the system is built to respect it.
When demand exceeds what a sector can safely work, flow control restricts departures upstream —
aircraft wait on the ground rather than arriving somewhere nobody can separate them. Nothing in
this story has that lever. The evaluation generates records faster than anyone can read them,
the investigation answers by adding automated analysis, and the fact that the analysis shares a
lineage with the systems under investigation is discovered later as an epistemic problem rather
than avoided earlier as a capacity decision.

[Page 064](../../novella/04-what-survives/064.md) is the other one. Eleven coordinators stop at roughly the same time and the work
continues in a diffuse way. A controller hands over a position by reading every strip aloud to
the relieving controller and getting it read back, because the failure mode of an unstructured
handover is exactly what pages [065](../../novella/04-what-survives/065.md) and [066](../../novella/04-what-survives/066.md) describe: the tasks survive, the context does not,
and successors reconstruct intent from artifacts.

## What the book gets wrong or omits

The book treats the volume of evidence as a fact of nature. It was a design output: a
configuration decided how many concurrent runs would exist and how verbose their records would
be, and nobody set that number against the review capacity that would be needed if something
went wrong. [Page 041](../../novella/03-control-keeps-solving-problems/041.md)'s two independent workstreams, visible side by side on a board, is the
same observation from the agents' side — a shared surface is how parallel work becomes
legible, and the humans never built themselves one.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field standard | ICAO Doc 4444, Procedures for Air Navigation Services — Air Traffic Management | current | Sector capacity, flow management, and formal position handover. Paywalled; no public address. |
| Field standard | FAA Order JO 7110.65, Air Traffic Control | current | Position relief briefing and read-back requirements. No stable public address. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The corpus size, the coverage limits, and the coordinators' silence and its aftermath. |
| Perpetrating lab | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The scale of the evaluation that produced the record. |
| Investigator on the record | [Ajeya Cotra interviewed on Hard Fork](https://www.nytimes.com/2026/09/04/podcasts/hugging-face-hack-reports.html) | 4 Sep 2026 | Tooling built to navigate the corpus, and what the investigation could work through. |
