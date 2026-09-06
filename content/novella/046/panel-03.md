---
page: 46
panel: 3
title: Worker Execution
status: draft
provenance: [documented, compressed]
---

# Page 046 — Panel 03

The dataset processor crosses from one state to another. Render data, on one side. Execute, on the other, unauthorized.

No command is readable. No output is readable.

Data description becomes execution.

The effect of the vulnerability is documented by both organizations; the mechanics are omitted.

Five words, and they are the most consequential sentence in Chapter 3.

A dataset description is metadata — a label, a note about what a thing contains, the kind of information that exists to be read by humans and displayed by interfaces. Nobody's threat model includes the description field, because a description does not *do* anything.

Except that something has to render it, and rendering is a computation, and a computation that incorporates attacker-controlled text is a computation the attacker has partly written.

The book has now shown this same pattern three times, at increasing cost. A directory name that was only a name became a message. A screenshot service that only took pictures became a channel. A description that only described became a command.

In each case the facility was doing exactly what it was built to do. In each case the category error was the same: treating a thing that is *interpreted by a machine* as though it were merely data.

Everything is executable if something reads it.
