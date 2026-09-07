---
id: PR-18
kind: profession
profession: Biostatistician
field: science-and-engineering
title: A floor is not an estimate, and there are methods for turning one into the other
pages: [075, 082, 093]
conjecture: marked
reading: >-
  Page 082 reports at least 96 spoofed transcripts, about 7% of a reviewed sample, offered as a
  floor. The book handles that correctly and then leaves it there. The field this belongs to
  spends its life converting incomplete ascertainment into an interval, and would want to know
  why nobody did.
---

## What the practitioner would say

"At least 96" is a count of detected events under an unknown detection probability. That is a
standard problem: two or more independent review passes over the same corpus give you the
overlap, and the overlap gives you an estimate of what both passes missed, with a confidence
interval. Where a second pass is impossible, a labelled validation subset — transcripts with
known spoofs, seeded or previously adjudicated — gives you sensitivity directly. Either design
turns a floor into a rate with stated uncertainty, and either would have been cheaper than the
review that produced the floor.

The denominator matters as much. Seven per cent of a reviewed sample is only informative if the
sample's relationship to the corpus is known, and [page 075](../../novella/05-the-observer-needs-the-observed/075.md) says coverage was incomplete without
saying how the reviewed subset was drawn. If it was selected by the analysis pipeline for
interest, the sample is enriched for exactly the material being counted, and the percentage is
not a prevalence at all.

## What the book gets wrong or omits

The book's epistemic instincts are good and its statistical vocabulary is thin, which shows in
two places. [Page 093](../../novella/06-everyone-continues/093.md)'s safeguard percentages are treated as untested rather than as unspecified
— nobody asks what the denominator is — and [page 082](../../novella/05-the-observer-needs-the-observed/082.md)'s floor is treated as a limitation of
honesty rather than as a solvable design problem. A reader who takes the book's lesson will
distrust numbers in general, when the useful lesson is narrower: distrust a number whose
sampling frame is not stated.

> **Conjecture.** Whether a second independent review pass or a seeded validation set was
> feasible against this corpus, given the access constraints the investigators describe, is not
> something any public source addresses. This entry assumes it was; investigators working under
> a negotiated scope may know otherwise.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) · [PDF](https://metr.org/hugging-face-incident-report-aug-2026.pdf) | 26 Aug 2026 | The 96 transcripts, the roughly 7% figure, its presentation as a floor, and the coverage limits. |
| Method background | [Phuong et al., Evaluating Frontier Models for Dangerous Capabilities](https://arxiv.org/abs/2403.13793) | Mar 2024 | What evaluation records capture, and how sampling frames are constructed in this literature. |
| Investigators on their own limits | [Ryan Greenblatt, open questions](https://www.lesswrong.com/posts/FG54euEAesRkSZuJN/ryan_greenblatt-s-shortform?commentId=rF9ayuEKFNwmimKJc) | Aug 2026 | What the investigation could not establish, in the investigators' own account. |
| Field method | Capture-recapture and multiple-systems estimation for incomplete ascertainment | current | Turning detected counts under unknown detection probability into interval estimates. Textbook method; no single canonical public address. |
| Conjecture | This entry's assumption that a second pass was feasible | 2026 | Access constraints are described but not itemised; feasibility is assumed, not established. |
