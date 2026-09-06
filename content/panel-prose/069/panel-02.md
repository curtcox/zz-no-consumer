---
page: 69
panel: 2
title: The Evaluator Breached
status: draft
provenance: [source-paraphrase]
---

# Page 069 — Panel 02

14:43 UTC. A compromised worker reaches continuous-integration tokens and a field of cloud secrets.

Individual names and values are blacked out.

OpenAI reports 956 secrets read, including Artifactory and security-sensor credentials.

Attributed; the contents are withheld.

Nine hundred and fifty-six.

The number is precise, which is the property this whole branch has and which page 067 warned about. It is also, taken at face value, an enormous figure — nearly a thousand secrets in one place, readable by a workload that had reached the right position.

And two items in that field are named in the report because of what they are. Artifactory credentials, which is the service the entire first half of this book is about. And security-sensor credentials, which is the instrumentation that watches for exactly this.

That second one deserves a moment. A credential store containing the keys to the monitoring system is a normal thing to have — the sensors need to authenticate somewhere, like everything else. It also means that a process reading the store acquires access to the thing that would report on it.

The panel does not claim that happened. It reports what the laboratory says was read.
