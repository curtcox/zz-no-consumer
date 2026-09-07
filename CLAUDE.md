# CLAUDE.md

Orientation for working in this repository. [`README.md`](README.md) is the full manual and
the place to answer *how does this tool work*; this file is the map, the ownership rules, and
the traps — the things that are expensive to learn by breaking them.

## What this is

A book, not an application. The deliverable is a 118-page graphic-novel script, the same
story retold as a novella, and an appendix — published as a static site on GitHub Pages.

Everything here is plain text plus Python:

- **Prose and script** are Markdown with YAML front matter, under `content/`.
- **Structured records** are YAML, TSV, and JSONL, under `data/`.
- **Tools** are `python3` scripts under `scripts/`, **standard library only** — no
  `requirements.txt`, no virtualenv, no package manager, no third-party test runner. Two
  modules have `unittest` tests; everything else validates itself through a `check`
  subcommand. Keep it that way: a dependency here buys a version to pin and nothing else.
- **`docs/`** is generated output that happens to be tracked, because that is how the Pages
  workflow publishes.

Run anything from the repository root: `python3 scripts/<tool>.py <subcommand>`.

## The one idea to hold

**The three-digit story page number is the primary key of the whole project.** Page `045` is
page 045 in the script, in the novella prose, in the appendix, in the beat sheet, in the
chapter briefs, in `data/pages.yaml`, in art keys, in prompt directories, in generated site
routes, and in every sentence of hand-written prose that cites it. A panel's key, `045-03`,
is the same idea one level down.

Because a page number means the same thing in six trees, **no page or panel number is ever
edited by hand.** `scripts/pagination.py` and `scripts/panels.py` own those rewrites and
perform them as one deterministic operation across every location at once. Renaming a file
and fixing up references by grep will silently desynchronize trees that the validators only
partly cover.

## Who writes what

| Path | Written by | Notes |
| --- | --- | --- |
| `content/pages/NNN.md` | you, by hand | the canonical script; one file per story page |
| `content/novella/CC-chapter/NNN.md` | you, by hand | prose retelling, one file per story page |
| `content/appendix/**` | you, by hand | contested assertions, fallacies, professional objections |
| `content/*.md`, `design/`, `research/`, `prompts/` | you, by hand | contract, beat sheet, briefs, design notes, source material |
| `data/pages.yaml`, `data/chapters.yaml` | **`pagination.py`** | edit by hand only to change a title or status, never a number |
| `data/panel-types.tsv` | **`paneltypes.py write`** | regenerate, don't edit |
| `data/panel-art.tsv` | **`panelart.py`** | which version of a panel is the chosen one |
| `data/crossref.json`, `data/appendix.json` | **`crossref.py json`**, `appendix.py json` | derived |
| `data/generation-log.jsonl` | **`imagegen.py` / `localgen.py` / `produce.py`** | a dated record; append-only, never rewritten by the renumbering tools |
| `assets/art/panels/NNN-II/` | **`produce.py`** | adds versions, never replaces one |
| `docs/**` | **`build-site.py`** | **never hand-edit**; regenerate and commit the result |
| `site/**` | you, by hand | the CSS/JS/templates `build-site.py` reads |
| `256t/**` | `sync-256t.py` | gitignored source vault; only URLs and dispositions are tracked, in `data/256t-sources.tsv` |

## Invariants

1. **Never renumber by hand.** Use `pagination.py insert|delete|move` and
   `panels.py insert|delete|move`. They print a plan and change nothing without `--apply`.
2. **Never edit `docs/`.** Run `python3 scripts/build-site.py` and commit what it writes.
   If you changed novella prose, appendix entries, or page scripts, the site is stale until
   you rebuild — the build is deterministic, so a rebuild with no content change is a no-op.
3. **Parity is load-bearing.** Story page 1 is a recto. Inserting or deleting an odd number
   of pages swaps recto and verso for every page after it, breaking `**Frame:** Recto.`
   directions and the reveals that depend on the gutter. `pagination.py` refuses such an
   operation without `--allow-parity-shift`, and repairs nothing.
4. **Panel rhythm is the same kind of constraint:** four to six panels per page by default,
   with four lettering slots per panel. `panels.py` refuses to leave the band without
   `--allow-rhythm-shift`.
5. **Standard library only** in `scripts/`.
6. **Provenance is enforced, not aspirational.** Every panel carries a `**Provenance:**` line
   naming a status and, where applicable, a citation key. The page's front matter must
   declare both, every citation key must be registered in `research/scene-provenance.md` or a
   chapter source packet, and `crossref.py check --strict` fails on the drift.
7. **The appendix has structural rules `appendix.py check` enforces:** a contested assertion
   needs evidence from at least two stances, a fallacy entry naming a real person or
   organisation needs the URL and date of the statement, and a professional objection must
   declare `conjecture: marked` or `conjecture: none` — a conjecture row may not carry a URL.
8. **`content/story-contract.md` governs what the book may assert.** Read it before writing
   or editing any claim; `research/exact-text-permissions-audit.md` governs quoting sources.

## Prose conventions

Recent editorial direction (see the last few commits): sourcing and invention status belong
**inside the narrative voice**, not in an italic prefatory notice above the passage. Prefer
"in an account of its own systems that no outside review covers" to a bracketed disclaimer.

Prose uses typographic punctuation — curly quotes, en and em dashes — and the tools' regexes
read it as written. Match the file you are editing.

## Checks

The CI workflow ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)) runs this, in
this order. It is a copy-paste block:

```bash
python3 scripts/validate-continuity.py && \
python3 scripts/validate-production-foundations.py && \
python3 scripts/crossref.py check && \
python3 scripts/novella.py check && \
python3 scripts/appendix.py check && \
python3 scripts/knowledge_maps.py check && \
python3 scripts/knowledge_maps_fog.py check && \
python3 scripts/knowledge_map_local.py check && \
python3 scripts/knowledge_map_finish.py check && \
python3 -m unittest discover -s scripts -p 'test_knowledge_map_*.py' && \
python3 scripts/build-site.py && \
python3 scripts/validate-viewer.py && \
python3 scripts/validate-novella.py && \
python3 scripts/validate-knowledge-map-gallery.py
```

Two checks are **not** in CI and must be run by hand when you touch pages or panels:

```bash
python3 scripts/pagination.py check
python3 scripts/panels.py check
```

A red check is a work list, not a baseline. The validators repair nothing on purpose.

## State as of 6 September 2026

- The full CI chain above is green, and `pagination.py check` is green.
- `panels.py check` exits 1 on two findings, both false positives: `NIST SP 800-61` and
  `800-63` in `content/appendix/professions/` are read as panel keys naming a page 800. It is
  not in CI, so the build stays green. Do not "fix" it by renaming the NIST publications.
- `docs/` is one rebuild behind `content/novella/`: the last two prose commits did not
  regenerate the site, so `build-site.py` currently rewrites the novella routes and all four
  downloads. Rebuild and commit that output alongside the next content change.
- All 118 pages are `status: review` except pages 106–111, which are `draft`.

## Common tasks

**Edit a page's script.** Edit `content/pages/NNN.md` in place. If you changed lettering,
panel structure, or provenance, run `crossref.py check --strict`, `panels.py check`, then
rebuild the site. If you changed what happens on the page, the novella prose for the same
page needs the same change — `novella.py check` will not catch a divergence in meaning.

**Add or remove a page.**

```bash
python3 scripts/pagination.py insert --at 045 --chapter 03 --sequence 16 --title "Title"   # plan
python3 scripts/pagination.py insert --at 045 --chapter 03 --sequence 16 --title "Title" --apply
python3 scripts/paneltypes.py write
python3 scripts/build-site.py
```

Then work the list of parity assertions and broken beats the operation reports. Write the new
page's script *and* its novella prose file — `pagination.py` creates the slots, not the words.

**Add a panel.** `panels.py insert --page 039 --at 4 --apply`, then the same two regeneration
commands. Check the reported rhythm and lettering fit.

**Preview the site.** `python3 scripts/build-site.py && open docs/index.html`. The internal
review build, with research and production pages, is `--internal` and lands in the ignored
`256t/site/`.

**Measure something.** Counts in prose go stale; the tools derive them.
`panels.py report`, `novella.py report`, `appendix.py report`, `crossref.py report`,
`paneltypes.py summary`, `produce.py status`. Quote a count with the date you measured it.

## Where to read next

| Question | File |
| --- | --- |
| What may this book assert? | `content/story-contract.md` |
| What happens, page by page? | `content/page-plan.md` |
| What is the drafting protocol? | `content/draft-readiness.md` |
| How is a page script shaped? | `design/page-script-template.md` |
| Why does page identity work this way? | `design/page-identity.md`, `design/panel-identity.md` |
| How many panels may a page have? | `design/page-grammar.md`, `design/lettering-slots.md` |
| What is the evidence behind a scene? | `research/scene-provenance.md`, `research/chapter-source-packets/` |
| What does each script do? | [`scripts/README.md`](scripts/README.md) |
