# Panel reference coverage — 12 September 2026

The canonical graphic-novel scripts now carry the reference pool specified by
`design/page-grammar.md`. Measured on this date: 118 story pages, 606 panels, 590
reference blocks (the two nine-panel grids each share a block), 593 reference
rows using 21 source keys, and 91 explicit `none` blocks.

Each row identifies a registered source, a locator, an absolute relevance score,
and the particular part of the panel it supports. The score describes relevance,
not reliability, permission, confidence, or a probability. Direct records, separate
accounts of disputed events, and background for project inferences are distinguished
in the notes. A high score on an institutional account does not make it independent.
Invented scenes and the speculative future do not acquire incident provenance merely
because they resemble earlier events.

## Source work

The sequence ledger, chapter packets, current panel direction and provenance were
read together. The packets contain some historical page-map descriptions that no
longer match the current scripts; current panel content governed the assignments.
The existing source locators were supplemented with panel-specific event dates,
footnotes, recording timestamps, revision IDs and manifest populations.

Public-source spot checks used the linked originals in the source packets:
the METR investigation, OpenAI technical report, Hugging Face technical timeline,
the collusion.wiki report, Carl Brown’s critique, the pacing announcement, the
multistate letter, Alabama’s subpoena and Apache Ant’s own site. This is reference
coverage work, not a fresh independent forensic investigation or quotation proof.
The wiki schema and named facts were checked against the local corpus manifest;
stored posts remain evidence of what was posted, not verified evaluation outcomes.

Three previously implicit reference targets received keys:

- `BB-OVERSIGHT`: Barnes’s already-indexed public caution. The original X endpoint
  did not expose readable text in this pass; the search-indexed contemporaneous
  archive supplied the matching post and date. The chapter packet records this
  retrieval limitation. It does not settle the existing lettering warning.
- `PROJECT-CREDITS`: the project’s own tooling-contribution record, including the
  warning about the limits of Git trailers after model switches.
- `APACHE-ANT`: the identity of an existing supplied visual prop, with the exact
  asset and receipt kept distinct from the reconstructed wall placement.

Neither the statements nor the dialogue were rewritten. Removing the added
reference blocks reproduces all 118 pre-change scripts byte for byte. No quotation
registration, source record, page identity, panel identity, or relevance-driven QR
selection was changed. The novella therefore needs no narrative synchronization.

## Validation and maintenance

`crossref.py check --strict` now checks reference-block presence and placement,
registered source keys, score format and ordering, duplicate key/locator pairs,
explicit provenance-key coverage (including continuation lines), and sources of
registered quotation text appearing in a panel. These checks cannot establish
semantic support or choose an editorial score. JSON export keeps references
separate from provenance assertions while including their sources in page indexes.
New page and panel placeholders explicitly say `References: none`.

Reference direction is excluded from quotation-shape inspection and storyboard
composition snapshots. The reader extractor already excluded it. The full reader
extraction remained byte-identical, the existing 590 storyboard compositions
passed their checks, and sampled normal, grouped, disputed, creator and future
image prompts contained no reference apparatus. The deterministic knowledge-map
manifest was regenerated because it hashes the changed source scripts; its drawings
did not change.

The full local check sequence in `AGENTS.md` completed successfully after that
manifest refresh, including the rebuilt site, downloads, EPUB links, reader and
storyboard validation. Additional source/built panel-layout checks and the reader
extractor check passed. `git diff --check` reported no whitespace errors. The
existing continuity warning list was unchanged.

The existing quotation-shape and ambiguous-reference warnings remain separate
editorial work, including the Barnes panel. This pass does not discharge gate 9 or
resolve conflicting incident accounts. The citation pool is ready for review;
later rendering still decides whether to print any reference as a QR code.
