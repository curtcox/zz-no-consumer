# Three-stream restructuring: implementation workspace

**Unfinished. No new manuscript page count has been allocated.** The initial
condensed chronology is withdrawn as a manuscript candidate. It compressed long
causal sequences into summary panels and cannot meet the requested level of detail.
Its generated pages are retained only as a labelled study, not as a capacity plan,
target, final script or handoff for resynchronizing the novella.

The owner's implementation clarification fixes the collaboration rows as **Curt,
Codex, Claude**. Curt's entrance starts with Twitter posts to be determined by later
research. Codex and Claude activity must be established from this Mac, the other
Mac and the GitHub repository. No invented exchange substitutes for that work.

## What to work from

- [Detailed scene draft](manuscript-review.md): readable, generated review of the
  authored sequences in [manuscript/](manuscript/). These now include decomposed
  incident action, failed attempts, counterexamples and selected dated production
  messages. They are unallocated scene drafts; overlapping uncertain intervals
  still need reconciliation. This is separate from the withdrawn chronology study.
- [Manuscript coverage](manuscript-coverage.json): derived counts and candidate
  old-panel associations, preserving all old quotation registrations for review.
  Association does not certify full preservation; individual detail reviews remain
  pending. No page count is derived from the number of beats.
- [Source-detail review](detail-review.md): element-by-element decisions authored
  in `detail-review.json`. The opening task sequence now separates the documented
  discarded-output finding from the old invented input/timing tests. Each decision
  names its destination or gives an omission reason. Source and destination hashes
  invalidate decisions when reviewed text changes; unlisted panels remain pending.
- [Detailed source inventory](detail-inventory.json): every old panel, its frame,
  action, lettering, provenance and references. Each extracted element awaits
  individual decomposition/disposition. Extraction is not editorial completion.
- [Frozen panel inventory](old-panels.json): original wording and registrations,
  keyed by old edition and panel. Grouped grids keep their shared-composition flag;
  they are not nine independently observed events.
- [Chronology seeds](ledger.json): sourced high-level chronology and new research
  leads. Expand these into actions, exchanges, discoveries, failures and responses.
  They are not complete replacements for the panels they reference.
- [Collaboration candidates](collaboration-candidates.json): fourteen selected
  request/first-response locators across seven local tasks. Original selected
  message records are preserved in ignored `256t/editions/selected-messages/`.
- [Source admissions](sources.json): scoped to the working edition. The published
  registry and its dependent editions are unchanged.
- [Readiness](readiness.json): unfinished work, enforced by the completion check.
- [Withdrawn chronology preview](generated/preview/index.html): useful for seeing
  the row convention only. Its page count says nothing about the manuscript's needs.

The initial [dispositions](dispositions.json) and [mapping](generated/mapping.json)
are **candidate associations for the withdrawn study**, not certification that a
summary preserves every old beat. `defer` means unfinished work, not an omission.
The undated future coda is explicitly retired under the task's default ending;
its original project-authored strings remain in the frozen record.

## Working boundary and recovery

The complete old edition is commit
`332b5ed6326206a15cc599eadfc1fdc37cf9e9d7`. [baseline.json](baseline.json) records
its frozen-file hashes and the hash of a complete local `git archive` tar in
ignored `256t/editions/`. This includes tracked scripts, prose, manifests, source
registrations, references, code, historical logs and artwork. Back up that tar
alongside the vault. The commit is a second recovery path. Extract either into a
separate directory, never over the live working tree.

Every old reference still names the old scene. Every generated mapping includes
the frozen edition identifier; study destinations explicitly name
`three-stream-chronology-study`. No old prose link resolves to a new scene solely
because of a reused number. No artwork was promoted, relabelled or regenerated.
Immutable versions and historical generation logs are preserved.

## Identity and layout tools

From the repository root:

```sh
python3 scripts/working_edition.py inventory
python3 scripts/working_edition.py manuscript
python3 scripts/pagination.py edition --root editions/three-stream --draft
python3 scripts/pagination.py edition --root editions/three-stream --draft --apply
python3 scripts/working_edition.py check --draft
```

The dry run prints **all** old/event/new mappings before any write. Allocation is
owned by `pagination.py edition`, using the existing `panels` script splitter,
lettering parser and `crossref` quotation parser. The bulk model supports splits,
merges and explicit omissions. Existing default identity commands still operate
on the published editions together; their behavior and validators are unchanged.

The scoped command renders and validates before replacing its owned `generated/`
tree. It never writes `docs/`. Authored inputs have stable event and window IDs;
only the identity tool assigns numbered scripts. Do not edit generated numbers.
The extracted detail inventory is derived; record editorial decisions separately
when the full rewrite is authored.

The `manuscript` command checks authored sequence identities, row ownership, source
admissions, bounds and quotation registrations, then regenerates the readable
review and conservative coverage report. It also checks complete element coverage
within each submitted detail review, explicit omission reasons and reviewed-text
hashes. These checks detect drift; they do not replace editorial judgment about
whether a rewrite preserves a claim. `check --draft` also rejects stale review
output. It does not assign canonical identities or certify editorial completeness.
The quoted production messages and selected wiki fragment retain unresolved rights
registrations for the late quotation gate.

Every window specifies inclusive UTC bounds, movement, chapter, purpose and three
rows in fixed order. Each row has one to three positions. JSON `null` means an
intentional blank with no panel ID, art, lettering, provenance claim or art job.
Entirely empty pages are rejected. Ordinary pages use two positions per row; this
is not a page-count ceiling. The busiest row determines the needed pages.

Rows have equal height. Row names and corner clocks are page furniture and remain
legible without color. Day-only dates and minute-only timestamps do not acquire
invented seconds. Events preserve their own bounds and source availability.
Overlapping broad intervals are visibly flagged for editorial allocation, not
silently given a fabricated order. The completion check rejects unresolved overlap,
deferred panels, missing transition, unfinished readiness and the withdrawn study.
`check --draft` passing never means the book is complete or approved.

## Dependency inventory

| Identity consumer | Graphic-only working edition | Frozen / deferred |
| --- | --- | --- |
| Script, page manifest, chapter map, sequence and beat ledgers | New script and consecutive chapters after detailed allocation | Old scripts, manifests, chapter briefs and population allocations |
| `pagination.py`, `panels.py`, `pagelinks.py`, `crossref.py` | Explicit bulk path; shared parsing; edition-qualified mappings | Ordinary rewriters, links and full-edition checks |
| Novella and appendix trees / validators | None | Prose, FAQs, contested assertions, fallacies, objections and their references |
| `site`, `build-site.py`, `docs` | Separate generated graphic preview | Public routes, navigation, downloads and EPUBs |
| Panel layouts, storyboards, lettering and reader views | Explicit rows, occupied slots and blanks | Old geometry and placement records |
| `panel-art.tsv`, immutable panel assets, chooser | No art reuse approved yet | Selections and versions remain keyed to old scenes |
| Generation logs, receipts, prompts, classifiers and art queues | No generation needed for script review | Historical logs unchanged; no jobs for blanks |
| SVG components and derived geometry exports | Independent definitions available for later reviewed reuse | Existing defaults and pinned versions unchanged |
| Anthill / knowledge-map / QR studies and local viewers | None | All ancillary page/panel selectors and old routes |
| Parity, spreads, page-turn audits and production review | Fresh choreography required after allocation | Old reveals are history, not inherited constraints |
| Research, source vault and quotation registrations | Read-only evidence; preserve wording and limits | Original records and t256 pointers unchanged |

Before publication, deferred materials must either be offered as a clearly separate
old edition or withheld from new-edition navigation. Promotion is not implemented
as a shortcut around that gate.

## Verification and remaining work

Baseline continuity, strict cross-reference, pagination and panel checks passed
with existing warnings. Scoped offline fixtures exercise row order, containment,
repeated assignment, future knowledge, visible reconstruction, reciprocal mapping,
quotation preservation, intentional blanks, deterministic output, no-write dry
runs, stale output, frozen-file drift and metadata-only transcript inventory.

The full-detail rewrite is underway. Complete old-beat disposition, further
source-level decomposition, the complete collaboration ledger, final matrix, illustrated
thumbnails, complete read-through, print-size checks and final handoff remain open.
The current text preview is neither approved artwork nor final lettering. Do not
infer readiness from a generated file or a passing draft check.

See [research-handoff.md](research-handoff.md) for evidence already found and the
missing production records. Counts are measurements from the tools, not promises
about how long this book should be.
