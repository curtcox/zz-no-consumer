# `scripts/` — the tooling index

Every tool here is `python3`, **standard library only**, run from the repository root:

```bash
python3 scripts/<tool>.py <subcommand> [options]
```

Most take a `report` (print what is there), a `check` (exit non-zero while the tree disagrees
with itself), and sometimes a `generate`/`write`/`assemble`. **Every mutating operation prints
a plan and touches nothing without `--apply`.** No tool repairs what it finds; a red `check`
is a work list.

See [`../CLAUDE.md`](../CLAUDE.md) for the ownership rules these tools enforce, and
[`../README.md`](../README.md) for the full prose manual of each one.

## Structure: the tools that own identity

These rewrite canonical files. Do the work through them rather than by hand.

| Tool | Owns | Subcommands |
| --- | --- | --- |
| `pagination.py` | the story page number, everywhere it appears | `report` `check` `insert` `delete` `move` |
| `panels.py` | the panel ordinal inside a page | `report` `check` `insert` `delete` `move` |
| `panelart.py` | which generated version of a panel is the chosen one | `scan` `list` `choose` `reject` `clear` `status` `size` |
| `paneltypes.py` | `data/panel-types.tsv`, the per-panel generator classification | `write` `summary` `show` |

`pagination.py` refuses a parity-inverting operation without `--allow-parity-shift`;
`panels.py` refuses to leave the 4–6 panel band without `--allow-rhythm-shift`, or to discard
generated art without `--allow-art-loss`.

## Validation: what CI runs

In workflow order. All are green as of 6 September 2026.

| Tool | Checks |
| --- | --- |
| `validate-continuity.py` | the story contract, chapter map, and drafted page metadata agree |
| `validate-production-foundations.py` | palette, visual-continuity, prompt, and asset foundations exist and agree |
| `crossref.py check` | citation keys resolve, sequences are in range; `--strict` also fails on panel/front-matter provenance drift |
| `novella.py check` | one prose file per scripted page, front matter matching the script, prose that is not a stub |
| `appendix.py check` | two-stance minimum, fixed fallacy vocabulary, conjecture declarations, live page references |
| `knowledge_maps.py check` | the committed controlled knowledge-map SVGs match what the generator produces |
| `knowledge_maps_fog.py check` | the same for the fog-of-war studies |
| `knowledge_map_local.py check` | committed local-model concept images and their recorded provenance |
| `knowledge_map_finish.py check` | structure-preserving finish studies, and that their v1 sources have not moved |
| `validate-viewer.py` | every generated viewer route, control, and view setting resolves |
| `validate-novella.py` | one anchor per page in one chapter, linked from contents; the four downloads are complete |
| `validate-knowledge-map-gallery.py` | the published gallery, without rebuilding any assets |

CI also runs `python3 -m unittest discover -s scripts -p 'test_knowledge_map_*.py'`, which
covers `test_knowledge_map_local.py` and `test_knowledge_map_finish.py` — the offline
generation boundaries, so a CI run can never reach for an image model.

**`pagination.py check` and `panels.py check` are not in CI.** Run them by hand whenever you
touch pages or panels.

## Publishing

| Tool | Does |
| --- | --- |
| `build-site.py` | builds all of `docs/` from `content/`, `data/`, `site/`, and `assets/`. `--internal` builds the full review site into the gitignored `256t/site/` instead. Takes about five seconds. |
| `epub.py` | writes the novella EPUB 3, page list and all. Deterministic for a given day; byte-identical across machines with `SOURCE_DATE_EPOCH` set. Called by the builder. |
| `make-thumbnails.py` | the provisional recto/verso spread contact sheet, into the internal build |
| `textimage.py` | flows text into an image of exactly the requested size, in pure Python. `book` writes a placeholder for every page and panel slot, which is why the whole book is readable before any art exists. |
| `letterpress.py` | composes the controlled lettering layer over panel art (`slots` `panel` `page` `audit`) |

## Reading the record

| Tool | Answers |
| --- | --- |
| `crossref.py report` | which sources and provenance statuses a page rests on, and which pages rest on a source |
| `novella.py report` / `assemble` | word census by chapter and page; the whole novella as one document |
| `appendix.py report` / `assemble` / `json` | census, page coverage, stance and field spread |
| `cadence.py report` / `list` | the negation cadence of the visible lettering. **No `check`, deliberately** — which aphorisms to thin is an editorial judgement no exit code should make. |

## Artwork

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

Four modules carry the shared models, and the rest import them rather than re-deriving:

- **`crossref.py`** — the page/chapter/sequence/provenance graph. Imported by `pagination.py`,
  `panels.py`, `novella.py`, `appendix.py`, and the builder.
- **`panels.py`** — the panel and lettering model. Imported by `imagegen.py`, `novella.py`,
  `make-thumbnails.py`.
- **`imagegen.py`** — the generator roster and the prompt composer. Imported by `bakeoff.py`,
  `localgen.py`, `produce.py`, `paneltypes.py`, and the knowledge-map studies.
- **`textimage.py`** — the pure-Python text-into-image primitive. Imported by everything that
  draws.

`build-site.py` imports eight of them, which is why a change to any of those modules can move
generated output in `docs/`. Rebuild and look at the diff.
