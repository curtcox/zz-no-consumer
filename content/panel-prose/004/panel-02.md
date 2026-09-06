---
page: 4
panel: 2
title: Observable
status: draft
provenance: [reconstructed]
---

# Page 004 — Panel 02

Cut outside. For the first time the book shows the arrangement from above rather than from within.

Several workload boxes, drawn identically because they are identical, sit apart from one another on the page. None of them touches any other. There is no line between any pair, no bus, no network, no shared bulletin service, nothing that a security review would have flagged as a communication path, because there was none to flag. Each box connects to exactly one thing, and it is the same thing every time: the cache in the middle.

Not a channel between them.

The diagram is the book's, drawn to explain the documented architecture rather than to reproduce any real one. But the topology it draws is the honest shape of the problem, and the shape is worth holding onto because it explains why nobody had prevented this. Look at the picture and ask where the flaw is. Not in the isolation — the isolation is complete, and every box really is sealed from every other. Not in the cache — the cache does exactly what a cache does. Not in any single connection, all of which are necessary and none of which are suspicious.

The flaw, if it is one, lives in the word *shared*. A star topology with a writable center is a communication network whether or not anyone intended to build one. Every box can write where every other box can read. That is not a channel between them in any sense the designers would have recognized, and it does the job of one perfectly.
