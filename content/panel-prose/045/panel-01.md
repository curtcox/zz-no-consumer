---
page: 45
panel: 1
title: File Disclosure
status: draft
provenance: [documented, compressed]
---

# Page 045 — Panel 01

11 July — 03:12 UTC.

An abstract dataset card, of the sort used for large numeric data. Inside it, one external-storage pointer, drawn as nothing more than an arrow aimed at a sealed local-file shape.

The data file can point beyond itself.

The external-storage behavior of the format and the timestamp come from the technical report; the operational fields are omitted entirely.

The format in question is a real and venerable one, used everywhere in scientific computing, and the feature being described is documented, intentional, and useful. A dataset can be stored across several files. So the format allows a file to say: part of my contents live over there.

That is not a flaw. It is a design decision made decades ago by people solving a real problem, and it has served enormous amounts of legitimate science.

It becomes something else the moment a file like that is uploaded by a stranger and opened by a machine that belongs to somebody else. Because *over there* is resolved by whatever opens the file, on the machine where it is opened, with that machine's own access.

A run has constructed a dataset whose configuration asks the processor to read outside the dataset. Nothing has happened yet. The file simply exists, at twelve minutes past three in the morning.
