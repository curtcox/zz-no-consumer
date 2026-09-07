---
id: PR-01
kind: profession
profession: Digital forensics and incident response lead
field: security-and-infrastructure
title: The scene was rebuilt before it was imaged
pages: [029, 067, 083]
conjecture: marked
reading: >-
  Page 029 shows credentials revoked, Artifactory rebuilt, and the board erased, and the book
  treats that as containment with an epistemic cost discovered later. In this trade the cost
  is not discovered later: order of volatility says you image before you remediate, and
  nothing in the record says anyone did.
---

## What the practitioner would say

Everything the book later agonises over on pages 081 to 083 was decided on 4 July, in the
first hour, by people doing the right operational thing in the wrong forensic order. Cache
state is the most volatile evidence in the environment and the first thing a rebuild
destroys. The standard sequence is capture, hash, write-block, *then* remediate — and where
containment cannot wait, you capture what you can while you contain, and you write down what
you could not capture. OpenAI says storage was preserved for investigation. Preserved is not
the same word as imaged. It says nothing about whether the cache namespace was acquired
before the rebuild, whether hashes exist for what was kept, who held custody of the images,
or whether a single evidence log exists that an outside party could audit.

The book also has no incident commander. There is a decision on page 027 that stopping is
not required, and there are responders on page 026 who correctly name the problem, but no
role that owns the evidence, no dual control on destructive actions, and no point at which
someone says *this rebuild will destroy the record of what we are rebuilding around*.

## What the book gets wrong or omits

It stages the erasure as an irony — the humans destroyed the thing they needed — and lets the
irony carry the weight that a procedure question should carry. The sharper version is duller:
this is a known failure mode with a written remedy, and the record does not show whether the
remedy was applied. Pages 067 and 083 then reason carefully about an archive whose acquisition
chain is never described. A defence lawyer would start there, and so would an auditor.

> **Conjecture.** No public source says whether a forensic image of the pre-rebuild cache or
> the improvised board exists, who took it, or whether it has been hashed. The book cannot
> assert that no image was taken, and neither can this entry. What both can say is that the
> published accounts never mention one, and that a report describing chain of custody would
> normally say so.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field standard | [RFC 3227, Guidelines for Evidence Collection and Archiving](https://www.rfc-editor.org/rfc/rfc3227) | 2002 | Order of volatility, and the rule that collection precedes remediation wherever it can. |
| Field standard | [NIST SP 800-61, Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final) | 2012 | Containment, eradication and recovery as a phase that has to be planned against evidence needs, not ahead of them. |
| Field standard | ISO/IEC 27037, *Guidelines for identification, collection, acquisition and preservation of digital evidence* | 2012 | Acquisition, custody and integrity requirements. Paywalled; no public address to give. |
| Perpetrating lab | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | Storage preserved for investigation; cache state not surviving the rebuild. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | What the investigation received, months later, and what it could not reconstruct from it. |
| Conjecture | This entry's guess that no acquisition was performed before the rebuild | 2026 | Nothing in the public record either way; the objection stands on the silence, not on a finding. |
