# Working in this repository

Orientation for working in this repository. [`README.md`](README.md) is the full manual and
the place to answer *how does this tool work*; this file is the map, the ownership rules, and
the traps — the things that are expensive to learn by breaking them.

## What this is

The deliverable is a graphic-novel script, the same story retold as a novella, and an
appendix — published as a static site on GitHub Pages. Derive current page counts with
`python3 scripts/pagination.py report` rather than relying on counts in prose.

Everything here is plain text plus Python:

- **Prose and script** are Markdown with YAML front matter, under `content/`.
- **Structured records** are YAML, TSV, and JSONL, under `data/`.
- **Tools** are `python3` scripts under `scripts/`, **standard library only** — no
  `requirements.txt`, no virtualenv, no package manager, no third-party test runner. Two
  modules currently have `unittest` tests; everything else validates itself through a `check`
  subcommand. Keep it that way: a dependency here buys a version to pin and nothing else.
- **`docs/`** is generated output that happens to be tracked, because that is how the Pages
  workflow publishes.

Run anything from the repository root: `python3 scripts/<tool>.py <subcommand>`.
Use a current Python 3; CI selects `3.x`. Building and checking require no model weights,
API keys, or source-vault downloads. Optional artwork generation has separate external
runners or servers and weights; see [the tooling index](scripts/README.md#artwork).

## Start here

1. Run `git --no-optional-locks status --short` to identify existing work before
   editing. The flag matters: a plain `git status` rewrites the index when stat data is
   stale, so it takes `.git/index.lock` like a write command does. Read-only git calls
   in this repository carry `--no-optional-locks`. This protects status, but the tested
   Git versions still refresh the index after `diff`; each fresh checkout also needs
   `git config --local diff.autoRefreshIndex false` (or pass
   `-c diff.autoRefreshIndex=false` on individual diff commands). See the
   [reproduction and mitigation](research/git-lock-2026-09-07/README.md).
   After rebuilding, unchanged binaries may appear in diff output until an explicit
   `git update-index --refresh` refreshes their stat data. This is an index write:
   coordinate it, inspect its result, and do not confuse it with staging content.
   Coordinate staging and committing so only one session writes the shared index at a
   time; use separate worktrees for independent writers. If `index.lock` blocks a write,
   follow the [Git incident and recovery procedure](README.md#git-coordination-and-incident-record).
   Do not automatically delete locks or infer staleness from age alone. The initial
   UI failure has no captured creator PID; later recurrences correlate with canceled
   background diffs, and their lock mechanism has been reproduced in isolated fixtures.
2. Read the ownership table below and [scripts/README.md](scripts/README.md) for the
   affected tool. Read the story contract before changing narrative claims.
3. Run the relevant checks before and after your change, so existing findings remain
   distinguishable from regressions. The full local CI sequence is below.
4. Rebuild when changing published inputs, inspect `git --no-optional-locks diff --stat`
   and the affected source and generated files, and report validation results with any
   unresolved findings.
   Orientation-only edits to this file, `CLAUDE.md`, `README.md`, or `scripts/README.md`
   do not feed the site and need no rebuild.

Search the source trees first: `docs/` duplicates the book, `assets/` contains many generated
files, and `research/collusion/` is a large evidence corpus. For example:

```sh
rg -n 'PATTERN' scripts site content data design prompts
rg --files scripts site data
```

Use [research/collusion/README.md](research/collusion/README.md) before querying or quoting
corpus counts. Use [scripts/README.md#how-they-fit-together](scripts/README.md#how-they-fit-together)
for the shared-module map before adding another parser or reference rewriter.

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
| page links in `content/**/*.md` | **`pagelinks.py link --apply`** | write `page 039`; the tool makes it a link |
| `content/novella/CC-chapter/NNN.md` | you, by hand | prose retelling, one file per story page |
| `content/appendix/**` | you, by hand | questions, contested assertions, fallacies, professional objections |
| `content/*.md`, `design/`, `research/`, `prompts/` | you, by hand | contract, beat sheet, briefs, design notes, source material |
| `data/pages.yaml`, `data/chapters.yaml` | **`pagination.py`** | edit by hand only to change a title or status, never a number |
| `data/panel-types.tsv` | **`paneltypes.py write`** | regenerate, don't edit |
| `data/storyboards.json`, `data/storyboard-assets.json` | you, by hand | composition and reusable geometry; identity tools own panel-key rewrites |
| `data/panel-art.tsv` | **`panelart.py`** | which version of a panel is the chosen one |
| `data/crossref.json`, `data/appendix.json` | **`crossref.py json`**, `appendix.py json` | derived |
| `data/generation-log.jsonl` | **`imagegen.py` / `localgen.py` / `produce.py`** | a dated record; append-only, never rewritten by the renumbering tools |
| `assets/art/panels/NNN-II/` | **`produce.py` / `storyboards.py`** | adds versions, never replaces one |
| `docs/**` | **`build-site.py`** | **never hand-edit**; regenerate and commit the result |
| `site/**` | you, by hand | the CSS/JS/templates `build-site.py` reads |
| `256t/**` | `sync-256t.py` | gitignored source vault; only URLs and dispositions are tracked, in `data/256t-sources.tsv` |

## Invariants

1. **Never renumber by hand.** Use `pagination.py insert|delete|move` and
   `panels.py insert|delete|move`. They print a plan and change nothing without `--apply`.
2. **Never edit `docs/`.** Run `python3 scripts/build-site.py` and commit what it writes.
   If you changed novella prose, appendix entries, or page scripts, the site is stale until
   you rebuild. The builder replaces its output directory. EPUB timestamps use the current
   UTC day unless `SOURCE_DATE_EPOCH` is set, so an unchanged source tree can still produce
   an EPUB diff on a later day.
3. **Parity is load-bearing.** Story page 1 is a recto. Inserting or deleting an odd number
   of pages swaps recto and verso for every page after it, breaking `**Frame:** Recto.`
   directions and the reveals that depend on the gutter. `pagination.py` refuses such an
   operation without `--allow-parity-shift`, and repairs nothing.
4. **Panel rhythm is the same kind of constraint:** four to six panels per page by default,
   with four lettering slots per panel. `panels.py` refuses to leave the band without
   `--allow-rhythm-shift`.
5. **Standard library only** in `scripts/`.
6. **A page number in prose is a link.** Write `page 039` and run
   `pagelinks.py link --apply`; it becomes `[page 039](…)` pointing into the edition the file
   belongs to — novella prose links to novella prose, a page script to the neighbouring
   script, the appendix to the novella. Ranges and lists link each number separately, because
   one link cannot name two destinations. The keyword stays inside the brackets on a single
   reference so that `page 039` remains one contiguous string and every regex that reads a
   page phrase keeps reading it. `pagelinks.py check` fails on a reference that is not a link
   or points at the wrong page; `check --built` fails on a built page, download, or EPUB that
   prints one a reader cannot follow. Never hand-write the link: the targets are derived, and
   `pagination.py` and `panels.py` re-derive them as part of their own operations.
7. **Provenance is enforced, not aspirational.** Every panel carries a `**Provenance:**` line
   naming a status and, where applicable, a citation key. The page's front matter must
   declare both, every citation key must be registered in `research/scene-provenance.md` or a
   chapter source packet, and `crossref.py check --strict` fails on the drift.
8. **The appendix has structural rules `appendix.py check` enforces:** a contested assertion
   needs evidence from at least two stances, a fallacy entry naming a real person or
   organisation needs the URL and date of the statement, a professional objection must
   declare `conjecture: marked` or `conjecture: none` — a conjecture row may not carry a URL —
   and a faq entry needs a title that is a question, an `answer:` line, and at least one
   reference with a public address.
9. **`content/story-contract.md` governs what the book may assert.** Read it before writing
   or editing any claim; `research/exact-text-permissions-audit.md` governs quoting sources.

## Prose conventions

Recent editorial direction (see the last few commits): sourcing and invention status belong
**inside the narrative voice**, not in an italic prefatory notice above the passage. Prefer
"in an account of its own systems that no outside review covers" to a bracketed disclaimer.

Prose uses typographic punctuation — curly quotes, en and em dashes — and the tools' regexes
read it as written. Match the file you are editing.

## Checks

The CI workflow ([`.github/workflows/pages.yml`](.github/workflows/pages.yml)) runs this, in
this order. It is a copy-paste block; the build step rewrites tracked `docs/`:

```bash
python3 scripts/validate-continuity.py && \
python3 scripts/validate-production-foundations.py && \
python3 scripts/crossref.py check --strict && \
python3 scripts/novella.py check --strict && \
python3 scripts/appendix.py check && \
python3 scripts/pagelinks.py check && \
python3 scripts/knowledge_maps.py check && \
python3 scripts/knowledge_maps_fog.py check && \
python3 scripts/knowledge_map_local.py check && \
python3 -m unittest discover -s scripts -p test_knowledge_map_local.py && \
python3 scripts/knowledge_map_finish.py check && \
python3 -m unittest discover -s scripts -p test_knowledge_map_finish.py && \
python3 scripts/storyboards.py check --complete && \
python3 scripts/art_jobs.py check && \
python3 scripts/image_crop.py check && \
python3 scripts/letterpress.py audit && \
python3 scripts/pagination.py check && \
python3 scripts/panels.py check && \
python3 scripts/build-site.py && \
python3 scripts/storyboards.py check --complete --built && \
python3 scripts/validate-viewer.py && \
python3 scripts/validate-novella.py && \
python3 scripts/validate-site-links.py && \
python3 scripts/validate-knowledge-map-gallery.py && \
python3 scripts/pagelinks.py check --built
```

These structural checks also run in CI; run them directly when you touch pages or panels:

```bash
python3 scripts/pagination.py check
python3 scripts/panels.py check
```

A red check is a work list, not a baseline. The validators repair nothing on purpose.

## Common tasks

**Continue built-in image pilots.** Use the [artwork queue workflow](design/artwork-automation.md)
and `scripts/art_jobs.py` for preparation, claims, receipts, review, and promotion.
Inspect `status` before creating new jobs; resume existing work rather than recreating
it. The persistent queue is local and gitignored under `256t/art-jobs/`; accepted
images and provenance enter the tracked artwork store. Within an authorized batch,
continue through eligible prepared jobs and bounded corrections without stopping
after an arbitrary pair. Stop for the requested batch limit, unresolved visual/source
decisions, unavailable generation, or exhausted attempts. Generation and visual
review remain assistant tasks; bookkeeping and batch verification are scripted.

**Generate or improve placeholders.** Follow [the storyboard workflow](design/storyboard-workflow.md)
for new scene records, local SVG generation, visual iteration, model handoff, importing,
selection, and rollback. The README links it under Placeholder images. Run
`storyboards.py generate`, `storyboards.py check`, the site builder, and
`storyboards.py check --built` after reviewed scene changes. All reader slots now have scene records; `check --complete` enforces coverage.

**Edit a page's script.** Edit `content/pages/NNN.md` in place. Write page references as
plain `page 039` and run `pagelinks.py link --apply` to link them. If you changed lettering,
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

**Preview the site.** Run `python3 scripts/build-site.py`, then
`python3 -m http.server 8000 --directory docs --bind 127.0.0.1` and visit
<http://127.0.0.1:8000/>. Stop the server with Ctrl-C. The internal review build, with
research and production pages, is `python3 scripts/build-site.py --internal` and lands in
the ignored `256t/site/`; serve that directory to preview it. A push to `main` triggers the
Pages workflow, which builds and deploys `docs/`.

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
