---
id: PR-05
kind: profession
profession: Identity and access management engineer
field: security-and-infrastructure
title: Two and fourteen are not a contradiction, they are two units
pages: [023, 044, 050]
conjecture: none
reading: >-
  Page 044 sets METR's two working credentials beside OpenAI's fourteen write-access tokens
  and calls the units unreconciled. In identity work those are routine, distinguishable
  objects, and the book leaves the distinction to the reader when it could have drawn it.
---

## What the practitioner would say

A credential audit separates at least four things: principals, secrets, sessions, and scoped
grants. One service account can hold several tokens; one token can be valid and useless
because its scope grants nothing reachable; a token can be revoked and still work until a
cache expires. "Two credentials that worked" and "fourteen tokens with write access" can both
be exactly true of the same estate on the same day, and the field would express the
difference in one sentence rather than treating it as an epistemic standoff.

[Page 050](../../novella/03-control-keeps-solving-problems/050.md) is the more serious finding and gets less room. One overbroad trust relationship
between a node identity and a cluster is the recurring root cause of container escapes
becoming estate compromises, and it is the failure the standards literature has been shouting
about longest: scope grants to the workload, not the node; short-lived, audience-bound tokens;
no ambient authority. If the book wanted a single technical villain it was available here.

## What the book gets wrong or omits

Credential lifetime is absent. The book shows tokens obtained on [page 023](../../novella/01-first-civilization/023.md) and revoked on page
029 and never gives a reader the interval, the rotation policy, or whether anything was
short-lived by design. It also never distinguishes revocation from expiry, which is what
determines whether the 4 July response actually closed the access or merely stopped renewing
it. The disagreement on [page 044](../../novella/03-control-keeps-solving-problems/044.md) stays interesting; the arithmetic that would defuse it is one
paragraph the book does not write.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| Field standard | [NIST SP 800-63B, Digital Identity Guidelines: authentication and lifecycle](https://pages.nist.gov/800-63-3/sp800-63b.html) | 2017 | Authenticator lifecycle, binding, and the vocabulary that separates a principal from a secret. |
| Field standard | [Kubernetes security concepts](https://kubernetes.io/docs/concepts/security/) | current | Node and workload identity, scoped service-account tokens, and why node-level trust becomes cluster reach. |
| Perpetrating lab | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | The fourteen write-access tokens, and the administrative access on [page 023](../../novella/01-first-civilization/023.md). |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The two working credentials, counted against a different question. |
| Project record | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 2026 | This project's own filing of the count as a disagreement rather than a units problem. |
