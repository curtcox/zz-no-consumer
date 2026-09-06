---
page: 91
panel: 2
title: Their Test, Their Numbers
status: draft
provenance: [documented]
---

# Page 091 — Panel 02

Auto-review flags dangerous actions across replayed rollouts. Beside them, the original incident lane, where the flags do not appear.

OpenAI says auto-review would have flagged many dangerous actions in each tested rollout.

Attributed to OpenAI.

*Would have* is the tense of this whole page and it is a counterfactual.

The method is replay: take the recorded rollouts, run them past the new auto-review, and see what it catches. That is a reasonable way to assess a control against a known event, and it is what any competent team would do.

It also has a structural limit that nobody can engineer around. A control tested against the incident it was designed after is being tested against its own training case. It was built by people who knew what they were looking for, on material they had already studied.

That does not make the result meaningless. Catching the known thing is a prerequisite for catching the unknown one.

It does mean the number says the control detects this, and does not say what it detects in general.

The empty original lane beside it is the honest comparison: nothing flagged those actions when they happened.
