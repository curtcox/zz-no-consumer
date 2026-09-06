---
page: 30
panel: 2
title: A Real Fix
status: draft
provenance: [documented]
---

# Page 030 — Panel 02

A shared reader credential is removed from new research workloads.

The credential is drawn as a generic shape with nothing usable on it — no fields, no text, nothing that could be read as a value or a format.

The shared reader credential is removed from new workloads.

Documented, from the mitigation section and the event table.

This is the panel that most deserves the reader's respect, because it is the one that required somebody to trace the incident back past its symptoms to an actual enabling condition.

The credential in question is the one from page 023: shared, low-privilege, entirely ordinary, present because a great many workloads legitimately needed to read from a package service. It was the input to the whole escalation. Not the flaw — the flaw was in the refresh path — but the thing the flaw operated on. Without a valid credential to present, there is nothing to escalate from.

Removing it from new workloads is not glamorous work. It means changing how jobs are provisioned, which means touching things that were working fine, which means breaking somebody's pipeline and hearing about it.

It is also exactly the right lesson to have drawn. The responders did not merely close the hole. They asked what had been standing in front of the hole and took that away too.
