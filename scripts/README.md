# `scripts/` — the tooling index

Every tool here is `python3`, **standard library only**, run from the repository root:

```bash
python3 scripts/<tool>.py <subcommand> [options]
```

Most take a `report` (print what is there), a `check` (exit non-zero while the tree disagrees
with itself), and sometimes a `generate`/`write`/`assemble`. Identity operations in `pagination.py` and `panels.py`, and `pagelinks.py link`, print a plan
and require `--apply` to write. This is **not a universal dry-run convention**:
`build-site.py`, `paneltypes.py write`, and `panelart.py choose` write immediately.
Read the command's `--help` before running a writer. Validation commands report findings
rather than repairing them.

See [`../AGENTS.md`](../AGENTS.md) for the ownership rules these tools enforce, and
[`../README.md`](../README.md) for the full prose manual of each one.

## Git diagnostics

`python3 scripts/git_lock_probe.py check` reproduces interrupted diff refresh locks
in a disposable repository and checks the `diff.autoRefreshIndex=false` mitigation,
diff-output equivalence after explicit refresh, and mandatory writer locking. It
also reports stat-only binary diff behavior before refresh. Use `--git /usr/bin/git` to
compare another installed Git. POSIX only, standard library only, no network. It
signals only its own fixture processes and never repairs or deletes a live checkout's
lock. A timing-dependent baseline reproduction is reported separately from check
failures. This diagnostic is manual, outside the publication CI sequence. See the
[incident record](../research/git-lock-2026-09-07/README.md) before live recovery.

## Structure: the tools that own identity

These rewrite canonical files. Do the work through them rather than by hand.

| Tool | Owns | Subcommands |
| --- | --- | --- |
| `pagination.py` | the story page number, everywhere it appears | `report` `check` `insert` `delete` `move` |
| `panels.py` | the panel ordinal inside a page | `report` `check` `insert` `delete` `move` |
| `panelart.py` | which generated version of a panel is the chosen one | `scan` `list` `choose` `reject` `clear` `stage` `status` `size` |
| `paneltypes.py` | `data/panel-types.tsv`, the per-panel generator classification | `write` `summary` `show` |
| `pagelinks.py` | the grammar of a page reference, and its links, in prose and in the build | `report` `check` `link` |

`pagination.py` refuses a parity-inverting operation without `--allow-parity-shift`;
`panels.py` refuses to leave the 4–6 panel band without `--allow-rhythm-shift`, or to discard
generated art without `--allow-art-loss`.

Panel prose scanning and renumbering share citation exclusions: explicitly prefixed NIST
publication identifiers and external web-link destinations are foreign references. Link
labels, local link targets, and bare panel keys remain checked. `panels.py check` also
runs offline regression checks for this distinction.

`pagelinks.py` owns the phrase grammar the other two read: `PAGE_PHRASE`, and the rule that
sorts a phrase into a reference, a foreign citation, an abstract rule, or an unpadded
ambiguity. `pagination.py` and `panels.py` import it, and re-derive every link target as part
of the operation, so a renumbering or a chapter move leaves the links pointing at the pages
they name.

## Validation: what CI runs

The authoritative sequence is in [the Pages workflow](../.github/workflows/pages.yml);
[AGENTS.md](../AGENTS.md#checks) provides the equivalent local commands. Run checks to
establish current status.

| Tool | Checks |
| --- | --- |
| `validate-continuity.py` | the story contract, chapter map, and drafted page metadata agree |
| `validate-production-foundations.py` | palette, visual-continuity, prompt, and asset foundations exist and agree |
| `crossref.py check --strict` | citation keys resolve, sequences are in range; CI also fails on panel/front-matter provenance drift |
| `novella.py check` | one prose file per scripted page, front matter matching the script, prose that is not a stub |
| `appendix.py check` | two-stance minimum, fixed fallacy vocabulary, conjecture declarations, live page references |
| `pagelinks.py check` | every story-page reference in `content/` is a link, pointing at the page it names |
| `knowledge_maps.py check` | the committed controlled knowledge-map SVGs match what the generator produces |
| `knowledge_maps_fog.py check` | the same for the fog-of-war studies |
| `knowledge_map_local.py check` | committed local-model concept images and their recorded provenance |
| `knowledge_map_finish.py check` | structure-preserving finish studies, and that their v1 sources have not moved |
| `storyboards.py check` | scene geometry, source drift, lettering clearance, deterministic assets, stage selection, and production skip behavior; `--complete` requires every reader slot |
| `panel_layout.py check [--built]` | shared rectangle geometry, selected image ratio/resolution, crop regression fixtures, and published panel positions; see [panel fit](../design/panel-fit.md) |
| `validate-viewer.py` | every generated viewer route, control, and view setting resolves |
| `validate-novella.py` | one anchor per page in one chapter, linked from contents; the four downloads are complete |
| `validate-site-links.py` | every local HTML and EPUB link target and fragment exists; Markdown downloads have explicit fragment anchors; anchors are unique; includes offline regression fixtures. Run after building; `--out PATH` selects another build tree. External URLs are not fetched. |
| `validate-knowledge-map-gallery.py` | the published gallery, without rebuilding any assets |
| `pagelinks.py check --built` | every page reference in `docs/` — HTML, Markdown, and the EPUB — is a link a reader can follow |

CI also runs `python3 -m unittest discover -s scripts -p 'test_knowledge_map_*.py'`, which
covers `test_knowledge_map_local.py` and `test_knowledge_map_finish.py` — the offline
generation boundaries, so a CI run can never reach for an image model.

**`pagination.py check`, `panels.py check`, and `letterpress.py audit` run in CI.** The lettering audit checks the effective reader layout, including storyboard boxes, and fails on unplaced or truncated text. Run the structural checks directly whenever you touch pages or panels.

## Publishing

| Tool | Does |
| --- | --- |
| `build-site.py` | builds all of `docs/` from `content/`, `data/`, `site/`, and `assets/`. `--internal` builds the full review site into the gitignored `256t/site/` instead. Takes about five seconds. |
| `epub.py` | writes the novella EPUB 3, page list and all. Deterministic for a given day; byte-identical across machines with `SOURCE_DATE_EPOCH` set. Called by the builder. |
| `make-thumbnails.py` | the provisional recto/verso spread contact sheet, into the internal build |
| `textimage.py` | flows text into an image of exactly the requested size, in pure Python. `book` writes a placeholder for every page and panel slot, which is why the whole book is readable before any art exists. |
| `storyboards.py` | deterministic SVG scene previews, versioned placeholder assets, and a comparison workshop (`generate` `check` `gallery`); see [the workflow](../design/storyboard-workflow.md) |
| `letterpress.py` | composes the controlled lettering layer over panel art (`slots` `panel` `page` `audit`) |

## Reading the record

| Tool | Answers |
| --- | --- |
| `crossref.py report` | which sources and provenance statuses a page rests on, and which pages rest on a source |
| `novella.py report` / `assemble` | word census by chapter and page; the whole novella as one document |
| `appendix.py report` / `assemble` / `json` | census, page coverage, stance and field spread |
| `cadence.py report` / `list` | the negation cadence of the visible lettering. **No `check`, deliberately** — which aphorisms to thin is an editorial judgement no exit code should make. |

## Artwork

Panel dimensions and reviewed crop derivatives are governed by
[the panel-fit workflow](../design/panel-fit.md) and `data/panel-layouts.json`.
`panel_layout.py fit` records a crop without overwriting its source; the builder
refuses selected artwork that does not fit its target rectangle.

`image_crop.py inspect IMAGE --review REVIEW.html` detects flat border bands and,
when local Tesseract is available, text boxes. The self-contained review includes
editable crop coordinates, edge-text exclusion buttons, a live preview, and PNG/receipt
downloads. `crop` saves an explicitly reviewed rectangle as a new lossless PNG;
`check` runs offline fixtures without OCR. No generation or reader selection changes.
See [the cropping manual](../README.md#image-cropping) for formats, OCR limits, and
the pixel-preserving receipt workflow.

For textured off-white model frames, add `--white-border` to `inspect`. This
requires pale bands on all four sides and rejects blank/ambiguous images; review
the suggested rectangle for irregular corners and edge labels before fitting.
WebP sources can be analyzed through a temporary PNG conversion, then cropped
with `panel_layout.py fit` using the original WebP. See the
[reviewed border crops](../design/model-border-crops.md). Use `panelart.selected`
or `panelart.pick` to inventory reader artwork: candidates can be selected even
without an explicit `chosen` flag.

`art_jobs.py` automates built-in image-tool handoffs: `prepare`, `claim`, `receive`,
`review`, `retry`, `block`, `status`, `export`, `verify`, and offline `check`.
Its durable local SQLite queue holds pending images outside reader selection;
accepted images use the existing version store, controlled borders and lettering.
Prompts, reference snapshots, review sheets and receipts are generated automatically.
It does not call a model. See [the automation workflow](../design/artwork-automation.md)
for batch operation, dependencies, recovery, the required preparation rasterizer,
and the gitignored queue's backup boundary. `art_jobs_checks.py` contains its
disposable offline fixtures, invoked through `art_jobs.py check`.

`python3 scripts/image_generation_status.py write` refreshes the single repository
summary, [IMAGE-GENERATION-STATUS.md](../IMAGE-GENERATION-STATUS.md), including the
remaining slots by page, chapter totals, and available refined/final candidates.
Run it after artwork or slot changes; `check` detects stale output in CI, and `report`
prints without writing. This census is offline and does not generate artwork.

`panel_candidates.py plan|run|check` generates one local candidate for every reader
slot without an existing **chosen refined/final** image. A chosen storyboard, an
unreviewed candidate, or a missing accepted file does not count as accepted.
It defaults to the configured `flux2-klein-4b` model and includes all panel types,
including diagrams and interfaces that will need careful visual review.

```sh
python3 scripts/panel_candidates.py plan
python3 scripts/panel_candidates.py run
python3 scripts/panel_candidates.py run --all
python3 scripts/panel_candidates.py run --limit 10
python3 scripts/panel_candidates.py check
```

Candidates, exact prompts, model settings, image hashes, and receipts are saved in
`256t/panel-candidates/`, outside reader selection. This directory is gitignored;
back it up to preserve pending work. Generation also appends to the usual generation
log. Nothing is accepted, imported, or published automatically. Review the output
before importing through the existing artwork workflow.

Repeat the same command to resume: saved candidates with the same prompt, model
configuration, dimensions, and seed are verified and skipped. Change `--seed` for
another pass; changed prompts/settings also produce a separate candidate. Existing
attempts are preserved. `--limit` applies after accepted and completed slots are
removed. For an overnight pass, `run --all` explicitly processes every remaining
panel, the same as omitting `--limit`. `--all` and `--limit` cannot be combined.
The script prints `[current/total] Generating NNN-II...` before each model call
and flushes progress immediately, including when output is redirected to a log.
It finishes when the pending batch is exhausted, or stops on failure/interruption.
`--provider` selects another configured local model; `--out-dir` selects
another review directory. `plan` performs no generation or writes. `check` uses
only disposable offline fixtures, with the model and generation log mocked.

Runs are sequential and protected by a POSIX process lock per output directory
(Mac/Linux). Coordinate runs using different directories to avoid competing for
model memory. Ctrl-C requests a stop after the current image; a second Ctrl-C
interrupts immediately. A generation/storage failure stops the batch with a nonzero
exit code; fix the cause and resume. Corrupted completed output requires inspection
instead of silent regeneration. Runner installation does not guarantee cached
weights: the existing local runner may download missing weights on first use.

These cost money or hours. None of them run in CI.

| Tool | Does | Needs |
| --- | --- | --- |
| `produce.py` | generates the book's panel art locally, by slot, page, range, chapter, or all of it (`status` `registers` `plan` `run`) | local weights |
| `localgen.py` | runs the bake-off prompts on open weights on this machine (`doctor` `estimate` `run`) | local weights; `data/local-models.json` is the roster |
| `bakeoff.py` | the published generator comparison through one OpenRouter key (`models` `estimate` `run`) | `OPENROUTER_API_KEY` |
| `imagegen.py` | the candidate roster, the prompt composer, and direct per-vendor calls (`providers` `prompts` `estimate` `sample` `sheet` `rank`) | a per-vendor key; `sample --dry-run` needs none |
| `knowledge_maps.py` / `_fog.py` | generate the design-study SVGs; dependency-free, no model | — |
| `knowledge_map_local.py` / `_finish.py` | the local-model knowledge-map studies (`generate` / `check`) | cached weights, forced offline |

`produce.py` adds a version rather than replacing one, so `--force` means *draw another* and
no run can destroy an earlier attempt. Runs are built to be interrupted: Ctrl-C stops after
the current panel, and re-running continues where it stopped.

## The source vault

`sync-256t.py` (`sync` `check` `status` `import`) maintains private local snapshots of tracked
original-source URLs under the gitignored `256t/`. Only the URLs and their redistribution
disposition are tracked, in `data/256t-sources.tsv`. Prose and the public site link to the
original URL rather than to a copied page.

## How they fit together

Six modules carry the shared models, and the rest import them rather than re-deriving:

- **`crossref.py`** — the page/chapter/sequence/provenance graph. Imported by `pagination.py`,
  `panels.py`, `novella.py`, `appendix.py`, and the builder.
- **`panels.py`** — the panel and lettering model. Imported by `imagegen.py`, `novella.py`,
  `make-thumbnails.py`.
- **`pagelinks.py`** — the page-reference grammar and the link rewriter. Imported by
  `pagination.py`, `panels.py`, and the builder, which asks it for one resolver per edition.
- **`imagegen.py`** — the generator roster and the prompt composer. Imported by `bakeoff.py`,
  `localgen.py`, `produce.py`, `paneltypes.py`, and the knowledge-map studies.
- **`storyboards.py`** — structured scene previews and explicit manual lettering placements. Imported by the builder, lettering, and identity tools.
- **`textimage.py`** — the pure-Python text-into-image primitive. Imported by everything that
  draws.

`art_jobs.py` composes these existing modules rather than parsing panel scripts or
inventing a separate reader selection policy. Its PNG validation and operational
queue are local to the image handoff boundary.

`build-site.py` imports several of these modules, which is why a change to any of those modules can move
generated output in `docs/`. Rebuild and look at the diff.

## Local synchronized displays

`python3 scripts/local_viewer.py serve` starts one LAN server for multiple browsers
and windows. Each window chooses its own display; any page selector drives the shared
page number. `--port 8765`, `--host 127.0.0.1`, and `--page 39` override the defaults
(all IPv4 interfaces, port 8000, page 001). Stop with Ctrl-C.

`viewer_overlays.py` holds the four shared preview layers that selector drives: panel art,
lettering, ants, and a fog of war — hillshaded relief with draped pictograms on the margins
and gutters, under a veil computed per page from the panel rectangles. It reads authored ant
geometry from scenes and `anthill_study.py`, rebuilds the fog with the terrain, drape and
veil constants of `knowledge_maps_fog.py` in that module's own units, borrows its pictogram
vocabulary without its family meaning, invents no placement of its own, and writes nothing.
A layer is withheld only where it is separable; a stored image that cannot give one up is
marked instead. Every pictogram keeps clear of every panel with room for the drape, open
ground never thins past what a panel keeps, and the fog is authored texture, never an
evidence-state model. A page's ground is a raster: it takes a second or two, and
`FOG_CACHED_PAGES` rendered pages are kept so the displays on one spread share the work.

`python3 scripts/local_viewer.py check` runs offline HTTP and rendering regression
checks with a temporary loopback server. It needs permission to bind a local socket.
The tool imports the publication Markdown renderer and existing novella, panel art,
text-image, and lettering models. It renders on demand and does not write `docs/`.
See [the local display manual](../README.md#local-synchronized-displays).

## Anthill composition study

`python3 scripts/anthill_study.py build` writes a standalone study to `256t/anthill-study/`;
`check` resolves page references from `data/anthill-study.json` (relocated by `pagination.py`), checks marginal placements against
protected panel rectangles, and verifies deterministic SVG and retained fog/re-fog states.
The production-foundations validator runs this check; the site builder emits the study at
`docs/anthill-study/`. It changes no ordinary reader overlays or raster selections.
`book_metadata.py` supplies the current title, description and masthead mark to the builder,
novella assembler and thumbnail generator. Technical addresses stay independent.

Study selectors are page-level records; panel insertion and deletion resolve the current
panel rectangles at build time. Deleting a selected page removes its study with a pagination
warning. Titles are presentation labels and may be changed without breaking selection.
The ant prompt convention is scoped to directions mentioning ants and ranked ahead of
optional style blocks. Artwork-job snapshots include the visual bible and continuity/map
rules so edits invalidate prepared work.

The study also exports ant-free bases, transparent authored-ant layers, composites and
lettered composites for selected ant-bearing scenes. It checks transparency, deterministic
output, protected lettering and foreground ordering. See [the overlay investigation](../design/ant-overlays.md)
for algorithmic/model asset options and the proposed versioned production workflow.
