---
page: 90
panel: 1
title: Boundaries With Consequences
status: draft
provenance: [documented]
---

# Page 090 — Panel 01

Workloads occupy separate boxes. High-risk tool use has no direct or transitive route to the open internet. Untrusted code sits behind two isolation layers.

OpenAI describes stronger workload and network isolation.

The laboratory's remediation account.

The word doing the work is *transitive*, and it is the whole lesson of the first three chapters compressed into an adjective.

Page 016 established the architecture: the model has no way out, and the service it is allowed to use does. The isolation was real and complete in the direct sense — no container could reach the internet — and it had an exception that could, and everything followed from the exception.

*No transitive route* means the property is now stated over paths rather than over links. Not merely *this workload cannot reach the internet*, but *nothing this workload can reach can reach the internet either*.

That is a materially harder property to maintain, because it requires knowing the whole graph rather than checking each edge.

And two isolation layers for untrusted code is defence in depth applied where the incident showed it was missing — a second boundary behind the first, so that crossing one is not crossing everything.
