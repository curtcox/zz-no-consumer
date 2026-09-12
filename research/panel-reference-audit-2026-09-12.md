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

## Follow-up editorial review — 12 September 2026

The initial coverage pass above is retained as a record. This follow-up changes the
script and synchronizes affected novella passages. It does not replace source
records or decide publication rights. Existing summaries now disclose their wording
as paraphrased; no new third-party quotation was introduced and gate 9 remains open.

The whole-book reference inventory was checked again. Broad METR locators were
sharpened in 166 existing rows, and the investigation-method panels received 16
individual printed-page locators. The separate refusal account now appears as a
0.80 supporting reference on the two OpenAI refusal panels. The later-branch
dossier also now cites the OpenAI event table it displays, at 0.85. Scores retain their
absolute meaning: direct claim support is normally 0.90–0.95, partial support or
corroboration 0.75–0.85, and context for an authored inference 0.40–0.60. No score is
a confidence estimate, rights clearance, or proof of independent corroboration.

Source checks used the [METR PDF](https://metr.org/hugging-face-incident-report-aug-2026.pdf),
[OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf),
[Hugging Face timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline),
[wiki researchers’ report](https://collusion.wiki/), and the local wiki manifest.
PDF locators use printed page numbers, not zero-based PDF indexes. This was an
editorial source check, not a fresh forensic investigation of every incident claim.

| Panel(s) | Correction and supporting locator |
| --- | --- |
| 041-05 | Lack of an established causal link no longer becomes proof of no causal link. |
| 042-05 | Root-access reference corrected to 9 July 11:34 UTC, OpenAI §X, p. 34; 08:30 refers to an earlier execution event. |
| 043-02–03 | The 08:46 public-utility route belongs to Artifactory. It is drawn alongside the customer-workload foothold; the opening no longer implies one ordered operator sequence. OpenAI §X, p. 34. |
| 059-04–05 | Prior answer exposure is distinguished from an already unrecoverable target. The gate depicts the decision, without inventing an observed execution or outcome. METR pp. 53–54. |
| 075–077 | Separate locators identify corpus units, access limits, nested delegation, preprocessing, and manual review rather than sending every panel to the same broad method description. |
| 096-01, 096-04 | Reference support notes corrected to describe their actual panels: initial inference pause and smaller-scale continuation respectively. |
| 107-03 | The 5,217 deletions and 5,144 distinct pages cover **4 June–14 July**, not May–June or the June 19 scene alone. The totals are explicitly retrospective. Their manifest population is `dse_admin_deletions`. |
| 107-03, 107-05 | Removal records establish neither the maintainer’s knowledge nor arrivals outrunning deletions. The last panel instead shows the 1,246 deleted pages without held revisions: a limit of archive coverage. Source: `manifest.facts.dse_admin_deleted_pages_without_held_page`, same population and window. |
| 108-03, 108-05 | Backup activity is dated 14:09–14:44; deletion timestamps do not reveal adjacency in the maintainer’s private list. The alphabetical-sweep claim remains the post’s explanation. |
| 109-03 | The last held revision bounds this export; it does not establish universal inactivity. The novella already carried this boundary. |
| 110-01, 111-04 | No claim that nobody previously found the wiki or that the critic privately lacked knowledge of it. The narrower statement concerns the published post. |

Eleven existing summary panels received visible paraphrase labels, clearing the
baseline quotation-shape warnings without rewriting their summarized statements.
The corrections fit existing panels; no page or panel was inserted, deleted, or
renumbered. Revised storyboard geometry removes the experimental gate-crossing
arrows, labels the Artifactory route correctly, and replaces the unsupported
arrival-rate comparison with missing-content evidence. Earlier art versions remain
in the store.

Validation for this follow-up: the full 32-step local CI sequence passed. After the
final label-format and reference additions, the affected source, lettering and built
checks were repeated. Visual review caught that a second em dash in a field header
was discarded by the existing letterer; parenthesized paraphrase labels now survive
in all eleven rendered headers. The revised archive panel and decision gate were
also inspected in the browser. The cross-reference JSON and site were regenerated.

Final census on 12 September: 118 pages, 606 panels, 590 reference blocks, 596
reference rows, and 91 explicit `none` blocks. Lettering remains within four slots
per panel and 180 words per page; the total is 6,144 lettered words. No unresolved
structural or lettering errors remain. Source-access limits, disputed incident
accounts, and gate 9’s quotation decisions remain explicitly open.
