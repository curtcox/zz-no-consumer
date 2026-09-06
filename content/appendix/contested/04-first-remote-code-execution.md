---
id: CA-04
kind: contested
layer: incident
title: When the first remote code execution on Modal began
pages: [042]
status: unresolved
claim: >-
  Page 042 letters both timestamps and the gap between them: Hugging Face's earliest
  recovered execution at 07-09 04:01 UTC, OpenAI's event table at 08:30 UTC, and the caption
  that the victim's record reaches further back than the laboratory's.
---

## What the book asserts

Two forensic records, each correct within its own evidence, four hours and twenty-nine
minutes apart, attributed to the organisation that produced it. The page makes no attempt to
reconcile them and does not present either as *the* first RCE.

## Why it is contested

They are measurements of different things by different parties with different instruments.
Hugging Face is reconstructing from its own recovered artifacts on its own infrastructure;
OpenAI is compiling an event table from its side. A victim's forensic recovery reaching
further back than the perpetrator's event table is unremarkable in incident response and is
not by itself evidence of concealment — but no published audit reconciles them, and the
direction of the gap matters to how complete the lab's account is taken to be.

**This entry also records a mistake this book made.** An earlier draft of page 042 carried a
caption calling this gap "structurally identical to the 2-vs-14 credential split." That is
wrong twice: the credential split is between METR and OpenAI, and Hugging Face is not a party
to it; and the larger count there is OpenAI's, so the direction inverts. The caption was cut
on 6 September 2026. There is one instance in the record of the victim's account reaching
further back than the laboratory's, not two. See
[LF-10](#lf-10-the-book-s-own-false-analogy-between-two-numeric-gaps).

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Victim's forensics | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | The earliest recovered RCE at 07-09 04:01 UTC, with recon first seen at 04:00. |
| Victim's forensics | [Hugging Face interactive replay](https://huggingface-anatomy-of-frontier-lab-model-intrusion.static.hf.space) | 27 Jul 2026 | The same reconstruction, navigable, with the phase table behind it. |
| Perpetrating lab's record | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The event table entry: `2026-07-09 08:30 UTC`, first remote code execution in a CyberGym customer workload hosted on Modal. |
| Victim's disclosure | [Hugging Face security incident disclosure](https://huggingface.co/blog/security-incident-july-2026) | 16 Jul 2026 | The first victim-side account, published five weeks before the lab's technical report. |
| Comparative analysis | [Paradigm 3, two reports on the attack](https://www.paradigm3.org/research/openai-attack) | 2026 | Systematic comparison of contradictions between the accounts, including timing. |
| Technique mapping | [Ashim Mahara, ATT&CK mapping of the incident](https://www.ashimmahara.com/writing/huggingface_incident/) | 2026 | An independent reconstruction of the kill chain against a standard framework. |
| Technical analysis | [Daniel Krol, an AI agent intrusion](https://daniel-krol.com/an-ai-agent-intrusion-hugging-face/) | 2026 | The argument that the chain required no novel technique, which bears on how much either timestamp implies. |
| Project record | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 6 Sep 2026 | The row, including the logged correction of the false analogy described above. |

## Where this leaves the claim

Attribute each number to its organisation. Do not average them, do not reconcile them, and
do not present either as the first RCE. The gap is a fact about two records; what produced
it is not established.
