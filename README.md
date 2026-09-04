# zz-no-consumer
A graphic novel about emergent AI agent coordination, instrumental convergence, and the humans trying to understand what happened.

## Repository map

- `content/` — canonical human-editable story material.
- `content/parallel-tracks/` — optional companion-track briefs that do not alter the canonical narrative.
- `prompts/` — image-generation prompts and page-specific direction.
- `research/` — source material, timeline, cast, glossary, and provenance notes.
- `design/` — lettering, page grammar, palette, visual continuity, and layout references.
- `assets/` — artwork and other media used by the site.
- `data/` — structured page, character, continuity, asset, and generation metadata.
- `scripts/` — validation, cross-reference, and site-generation utilities.
- `site/` — source styles and templates for the published site.
- `docs/` — generated GitHub Pages output; do not edit manually.
- `tasks/` — development task briefs for tooling work, written to be handed to a fresh session.

The complete first-draft script — 112 pages today, and the count is a measurement rather than a commitment — is in `content/pages/`, with every page currently in review. The assumptions are locked in `content/story-contract.md`, the beat sheet is `content/page-plan.md`, and the drafting and production protocol is `content/draft-readiness.md`. The source-language audit and completed paraphrase disposition are in `research/exact-text-permissions-audit.md`; the story-level security pass and resolved public-site scope decision are in `research/security-sensitivity-review.md`. Last-mile attribution rules remain in `research/draft-source-notes.md`. Before revising or renaming pages, run:

```sh
python3 scripts/validate-continuity.py
python3 scripts/validate-production-foundations.py
python3 scripts/pagination.py check
```

Add, remove, or move a page with `scripts/pagination.py` rather than by hand — see **Pagination** below.

The scene-level evidence boundary is tracked in `research/scene-provenance.md`, and the canonical page-script shape is in `design/page-script-template.md`. The training and evaluation configuration — the single-sourced material behind the whole incident, and the weights channel the cache wipe could not reach — is in `research/training-configuration.md`. The proposed fog-of-war knowledge apparatus is specified in `design/knowledge-map.md` and is not yet applied to pages.

The proposed inside-the-collective documentary is scoped in `content/parallel-tracks/messages-from-the-board.md`; its primary-source artifact gate is `research/agent-message-ledger.md`.

## Source vault

Potentially non-redistributable originals and internal review artifacts live in the Git-ignored `256t/` directory. The repository tracks only their canonical URLs and redistribution disposition in `data/256t-sources.tsv`.

```sh
python3 scripts/sync-256t.py sync    # download/update local snapshots
python3 scripts/sync-256t.py check   # report upstream content changes without accepting them
python3 scripts/sync-256t.py status  # show local hashes and missing/error states
```

Distinct downloaded bodies are retained by SHA-256 under `256t/records/`. Tracked prose and the public site should link to the original URLs rather than copied report pages, screenshots, or extended fragments when reuse rights are uncertain.

## Pagination

`scripts/pagination.py` owns every place a story page number lives: page filenames and front matter, `data/pages.yaml`, `data/chapters.yaml`, the beat sheet, the story-contract map, the eight chapter briefs, the sequence ledger's page ranges, the production-review turn and revision tables, panel keys in `data/panel-art.tsv` and `data/assets.yaml`, the `assets/art/panels/` and `prompts/pages/` directories, and every padded reference in hand-written prose. Adding or removing a page is therefore one deterministic rewrite, not a reason to fold a page into its neighbour.

```sh
python3 scripts/pagination.py report                       # page map, parity map, turn audit, reference census
python3 scripts/pagination.py check                        # exit non-zero while the tree disagrees with itself
python3 scripts/pagination.py insert --at 045 --chapter 03 --sequence 16 --title "Title"
python3 scripts/pagination.py delete 079
python3 scripts/pagination.py move 029 --chapter 02 --sequence 12
```

Operations print a plan and touch nothing without `--apply`. After applying, regenerate the derived artifacts:

```sh
python3 scripts/paneltypes.py write
python3 scripts/build-site.py
```

**Parity is the point.** Story page 1 is a recto, so inserting or deleting an odd number of pages swaps recto and verso for everything after the change. The script asserts its own parity 89 times, directs art with `**Frame:** Recto.` on 71 pages, and names 21 beats whose device is a consequence of parity — twenty reveals across the gutter, which need an even-to-odd pair, and one turn across the leaf, which needs an odd-to-even one. The tool checks every one of those on every run, and after an operation reports each assertion it invalidated, each beat it broke, and each beat it merely renumbered. It repairs none of them: a parity-inverting operation is refused outright unless `--allow-parity-shift` is passed, and `check` stays red until the work list is worked. The design and the alternatives considered are in [`design/page-identity.md`](design/page-identity.md).

Reference rewriting is deliberately narrow. Padded three-digit forms (`page 003`, `pages 019–021`, `page-003`) are rewritten; `printed page(s) N` is excluded because thirteen references in the tree cite pages of the OpenAI technical report; bare one- and two-digit forms are reported and never guessed at; `data/generation-log.jsonl` and `design/page-identity.md` are dated records and are left alone.

`check` is green, including `--strict`, and is meant to stay that way: a red tree is a work list, not a baseline. Its two long-standing findings were closed on 4 September 2026 — page 099 claimed `Verso` on an odd page, and the audit filed `085 → 086` as the same device as every even-to-odd row when it is the one beat in the book that lands across a leaf.

## Panels

`scripts/panels.py` does for a panel what `pagination.py` does for a page. A panel's identity is its ordinal index inside its page, and that index lives in the `## Panel N` heading, in art keys in `data/panel-art.tsv`, in `assets/art/panels/NNN-II/`, in `prompts/pages/NNN/panel-II.md`, in the generated classification table and viewer routes, and in the page notes and frame directions that name a panel by number — including the ones that name another page's panel, like `Repeat page 003 panel 2`. Adding a beat to a page is therefore one deterministic rewrite, not a reason to grow an existing panel's **Action** line.

```sh
python3 scripts/panels.py report                  # panel census, rhythm map, lettering load, reference census
python3 scripts/panels.py check                   # exit non-zero while the tree disagrees with itself
python3 scripts/panels.py insert --page 039 --at 4
python3 scripts/panels.py delete 039-04
python3 scripts/panels.py move 086-06 --to 3
python3 scripts/panels.py move 039-04 --to-page 040 --to 2   # to another page
```

Operations print a plan and touch nothing without `--apply`, and the same two regeneration commands follow an applied one. `--to-page` moves a beat to another page: the panel's script, its art directory, its prompt file, and its row in `data/panel-art.tsv` travel together, both pages are renumbered, and every sentence that named the panel follows it.

**Rhythm is to a panel what parity is to a page.** [`design/page-grammar.md`](design/page-grammar.md) bands a page at four to six panels by default, one to three for an establishing or revelation page, five to nine for a procedural sequence; [`design/lettering-slots.md`](design/lettering-slots.md) anchors four lettering slots per panel, so a fifth element on one panel has nowhere to go. An operation that leaves the default band is refused unless `--allow-rhythm-shift` is passed, one that discards generated art unless `--allow-art-loss` is, and either way the tool prints the new rhythm, every panel whose lettering no longer fits, and every image that now sits under a different beat. It repairs none of it.

Reference rewriting is narrow in the same way pagination's is. A bare `panel 4` is local to the page script or `prompts/pages/NNN/` file it sits in; `page 003 panel 2` names another page's; anything inside a code fence or inline backticks quotes a form rather than pointing at a panel, so it is reported as an example and never rewritten; `data/generation-log.jsonl` and `design/image-generation-options.md` are dated records and are left alone. A reference that names no page, in a file that is not scoped to one, is reported and never guessed at.

The panel count is a measurement, not a contract. `panels.py report` derives it, `scripts/imagegen.py` and `scripts/make-thumbnails.py` read it rather than hard-coding it, and prose that quotes it should say when it was measured.

## Cross references

`scripts/crossref.py` joins the page manifest, the provenance declarations in each page script, the citation-key registry in `research/scene-provenance.md` and `research/chapter-source-packets/`, and the scene ledger into one model. It answers both directions: which sources and provenance statuses a page rests on, and which pages rest on a given source, status, or ledger sequence.

```sh
python3 scripts/crossref.py report                  # counts, indexes, and findings
python3 scripts/crossref.py check                   # exit non-zero on structural errors
python3 scripts/crossref.py check --strict          # also fail on front-matter/panel drift
python3 scripts/crossref.py json --out data/crossref.json
```

`check` reports three severities. Errors mean the record does not join up: a citation key no source packet registers, or a page assigned to a sequence outside its ledger page range. Warnings mean a panel's `**Provenance:**` line cites a status or source the page front matter does not declare. Notes mark registered sources that no page cites. Only errors block by default.

## Site builds

The default build is the story-first public surface. It excludes research, source packets, prompts, design notes, and production artifacts:

```sh
python3 scripts/build-site.py
open docs/index.html
```

Build the full internal review site into the ignored vault with:

```sh
python3 scripts/build-site.py --internal
python3 scripts/make-thumbnails.py
open 256t/site/index.html
```

The internal builder converts Markdown in `content/`, `prompts/`, `research/`, and `design/`. The public builder includes only the premise, chapter/page scripts, and the original-source link index.

Both builds publish the cross reference at `docs/crossref/` (internal: `256t/site/crossref/`), with directory-style routes for every page, cited source, provenance status, and ledger sequence. Source records link to the original publication rather than reproducing it. The public build carries only the relational index; the scene ledger's narrative summaries, drafting rules, chapter-packet locators, and build findings appear in the internal build alone. Each viewer page and image information view links to the matching page record.

The generated site also includes an isolated viewer validation section at `docs/viewer/`. It publishes stable directory-style routes for the viewer home, chapter overviews, pages, panel images, and their information views before final artwork exists. Every one of those image addresses already resolves to a generated placeholder, so the whole book can be read end to end today. Every view exposes up, down, left, right, in, out, home, and next links; the matching keyboard shortcuts are Arrow keys, Enter, Escape, H, and Space.

Space is the read-through control: it scrolls the current view, and once the view is fully read it advances to the next node. The chain visits every generated route exactly once and loops back to the viewer home, so the whole book and all of its records can be read with the spacebar alone. Shift + Space reverses it.

The **Settings** button (or <kbd>S</kbd>) opens the view settings panel: full screen, which hides the masthead and navigation bar and leaves only the page content; show or hide the navigation icons; dark or light appearance; and image + text, image only, or text only. Settings are stored in the page fragment (for example `#theme=light&full=on&mode=image`) and are carried onto every internal link, so a copied link restores both the location and the view. Defaults carry no fragment.

Validate the entire generated route graph with:

```sh
python3 scripts/validate-viewer.py
```

Generate the provisional 57-spread production contact sheet with:

```sh
python3 scripts/make-thumbnails.py
```

The result is `256t/site/production/thumbnails/index.html`. Its panel geometry is a private review aid rather than locked layout; findings and required print proofs are tracked in `content/production-review.md`.

## Placeholder images

`scripts/textimage.py` flows a block of text into an image of exactly the dimensions it is given. It adds no image dependencies: glyph advances come from the Helvetica metrics that Arial, Liberation Sans, and Nimbus Sans match, so line breaking and the automatic type-size search run in pure Python and the rendered SVG breaks its lines where the module measured them. The largest size that fits is chosen by binary search; below the floor the text is cut to the box and ellipsized, so the image never spills past its dimensions.

Use it for any text and any size:

```sh
python3 scripts/textimage.py render --width 1200 --height 800 --out card.svg \
  --label "PAGE 001" --footer "PLACEHOLDER" --text "Any block of text."
```

`--text-file` and standard input work in place of `--text`. `--label` and `--footer` are single-line edge markers, shortened rather than allowed to widen the image.

The `book` command writes one placeholder for every page and every panel image slot in `content/pages/` — as the script stands, 112 page sheets at 700×1000 and 547 panel images at 1200×800:

```sh
python3 scripts/textimage.py book --out-dir docs/assets/placeholders
```

Each panel placeholder carries that panel's own `Frame`, `Action`, and lettering; each page sheet carries the page purpose. `scripts/build-site.py` runs this as part of every build and embeds the result, so the viewer's page sheets, chapter grids, and single-image views all show real script text in the frame the final art will occupy. Both site indexes link straight into that read-through, and `scripts/validate-viewer.py` fails if any placeholder is missing or carries no alt text.

Panel placeholders are keyed to the same image slots the viewer routes use, so a page written as one grouped run of panels gets the single image its route exposes. Replacing a placeholder with final art is a matter of pointing the image record at `assets/art/panels/NNN-II.*`; the route, alt text, and cross-reference link do not move.

## Choosing an image generator

The candidates, their prices, and the recommendation are in [`design/image-generation-options.md`](design/image-generation-options.md). The short version: the binding constraint is style and environment consistency across every panel in the book, not per-image quality, and at six attempts per slot the whole book costs between $24 and $646 in API spend.

Two runners send byte-identical prompts to every candidate. Each prompt is composed from the same sources final artwork will use — `prompts/global-style.md`, `prompts/negative-prompt.md`, `design/palette.md`, and the panel's own direction, and is fitted to the tightest text-encoder limit in the run. That fitting is not cosmetic: a model reads only its first `prompt_tokens` and silently discards the rest, and these prompts used to run to twice FLUX.2's 512-token ceiling, so half of every one of them — the palette, the negative prompt — was never delivered. `python3 scripts/imagegen.py prompts --provider <id>` shows what survives and what is dropped.

`scripts/bakeoff.py` produces the published comparison from a single key. OpenRouter's unified image API fronts five of the eight candidates and reports the exact cost of every call, so one account replaces four:

```sh
export OPENROUTER_API_KEY=...
python3 scripts/bakeoff.py models     # what the aggregator can actually route
python3 scripts/bakeoff.py estimate   # about $5 for the standard run
python3 scripts/bakeoff.py run        # generate, price, and write the sheet
```

`scripts/imagegen.py` holds the roster, the prompt composer, and the comparison sheet, and calls each vendor directly. That is the only way to reach Imagen 4, Qwen-Image, and a trained style LoRA, and it needs `GEMINI_API_KEY`, `OPENAI_API_KEY`, `FAL_KEY`, or `REPLICATE_API_TOKEN` depending on the candidate:

```sh
python3 scripts/imagegen.py providers        # roster, price, and key state
python3 scripts/imagegen.py estimate         # sample-run and full-book cost
python3 scripts/imagegen.py prompts          # exactly what each model receives
python3 scripts/imagegen.py sample --dry-run # whole pipeline, no keys, no spend
python3 scripts/imagegen.py sample --provider imagen-4 --provider qwen-image
python3 scripts/imagegen.py rank             # weighted result of scores.tsv
```

Six sample panels cover every register: the near-black incident aisle, an abstract dependency diagram, the creator's home office, an institutional room, a dossier grid, and an invented-future frame. `--repeat` sends each prompt more than once, which is the actual test — a candidate whose two takes are the same place in the same style can carry a book, and one whose takes diverge cannot, however good either image is alone.

Runs are written to `assets/bakeoff/<run>/` and published at [`/bakeoff/`](docs/bakeoff/), so the images behind the decision are committed evidence rather than something only the person who ran it ever saw. Each run directory holds the composed prompts, the images, `manifest.json`, a blank `scores.tsv`, and a standalone `sheet.html` for reading it before the site is rebuilt. Images are requested as WebP to keep a committed run to a few megabytes. Only live generations are recorded in `data/generation-log.jsonl`; `--dry-run` substitutes a `scripts/textimage.py` placeholder carrying the exact prompt that would have been sent, so the composer, run layout, and published sheet can be validated before any key exists.

Because `docs/` is the tracked Pages output, every committed run is stored twice — once as source under `assets/` and once as built output. A six-panel, two-take run across five candidates is roughly 30 MB of WebP at both copies, so keep one or two runs rather than a run per experiment.

`scripts/localgen.py` runs the same prompts on open weights on this machine, with no key and no spend. It reads its roster from `data/local-models.json`, which is editable JSON rather than Python because local tooling churns faster than the hosted roster does:

```sh
python3 scripts/localgen.py doctor     # this Mac, and what it can actually run
python3 scripts/localgen.py estimate   # wall clock for a run and for the book
python3 scripts/localgen.py run        # generate and write the comparison sheet
```

Local candidates are priced in hours rather than dollars, because that is what they cost: `doctor` and `estimate` report seconds per image, measured from earlier runs where any exist and estimated otherwise. Models too large for the machine's memory are filtered out, and models under a non-commercial licence — FLUX.1 [dev], FLUX.2 [klein] 9B, FLUX.2 [dev] — are skipped unless `--allow-non-commercial` is passed. A run that includes them is stamped evaluation-only in its manifest and carries a warning on the published sheet, because nothing they generate may appear in the book.

`mflux` is the MLX-native runner the command-backed models use (`uv tool install mflux --python 3.12`, then `uv tool list` for the exact command names; it also ships `mflux-train` for local LoRA training). Prefer a prequantized repository over quantising locally: Hugging Face serves FLUX.2 [klein] 4B at 22.1 GB and Z-Image Turbo at 30.6 GB in bf16, while the prequantized MLX build of the same klein 4B is 4.3 GB, which is the difference between running on a 16 GB machine and not. `data/local-models.json` records the download size and the memory footprint separately.

Two backends are supported. `command` runs a local binary with a templated argv and no shell, which is how the MLX-native `mflux` models are called. `http` posts to a local server speaking the OpenAI images shape, which is how Draw Things or ComfyUI-behind-a-bridge are called. `data/local-models.json` is executed as configuration, so treat it as code.

`assets/bakeoff/0000-dry-run/` and `assets/bakeoff/0001-local-dry-run/` are such placeholder runs. It publishes the prompts and the page structure; replace it with a real one and rebuild.

## Producing the artwork

`scripts/produce.py` generates the book's panel images locally and writes them to `assets/art/panels/NNN-II.webp`, where `scripts/build-site.py` letters them through the approved slot convention in [`design/lettering-slots.md`](design/lettering-slots.md).

```sh
python3 scripts/produce.py status                  # how much of the book has art
python3 scripts/produce.py plan                    # what a run would do, and for how long
python3 scripts/produce.py run                     # everything still missing
python3 scripts/produce.py run --slot 013-02       # one image
python3 scripts/produce.py run --page 013          # one page
python3 scripts/produce.py run --from 001 --to 020 # a range of pages
python3 scripts/produce.py run --chapter prologue  # a chapter
```

Selections combine, and `--register creator`, `--type`, `--route`, `--limit N`, and `--takes N` narrow further. `--type` and `--route` are the mechanism for running a mix of generators: [`design/panel-image-types.md`](design/panel-image-types.md) classifies every panel by what its description demands, and [`data/panel-types.tsv`](data/panel-types.tsv) is the table. Just over half the book needs nothing a 16 GB laptop cannot do, while 80 panels need long strings spelled correctly and 59 need reference conditioning for a recurring face — so the premium models are worth their price on a quarter of the book and wasted on the rest. Those splits are measurements; `python3 scripts/panels.py report` and `python3 scripts/paneltypes.py summary` print the current ones.

```sh
python3 scripts/paneltypes.py summary              # counts by type and route
python3 scripts/produce.py run --route local       # the 270 panels any model can draw
python3 scripts/produce.py run --route text-fidelity --provider qwen-image-local
```
 A full pass is one render per slot — 547 as the script stands, about twelve hours at the measured 78 seconds each, at the `--bleed 0.10` the drawn-border crop needs — so the run is built to be interrupted: panels that already have art are skipped, a running estimate is printed, and Ctrl-C stops after the current panel rather than losing it. Re-running continues where it stopped. `--force` regenerates existing panels and says how many it will overwrite first.

Each panel's prompt is composed from the same canonical sources the bake-off uses, with the register modifier derived from the page's primary location. `python3 scripts/produce.py registers -v` prints that derivation for every page so a wrong call is visible rather than silent; the rules live in `REGISTER_RULES` at the top of the script.

The default model is one that has actually produced an image on this machine, not merely one whose command is on PATH — `mflux` installs every model's entry point at once, so PATH alone would happily start a thirty-gigabyte download in the middle of an overnight run. `--provider` overrides it and `--width`/`--height` set the panel size; see the measured memory and wall-clock trade-off in [`design/image-generation-options.md`](design/image-generation-options.md).

Panels keep every version they are given. `scripts/produce.py` adds a version rather than replacing one, so `--force` means *draw another*, and nothing a run produces can destroy an earlier attempt. Which version belongs in the book is recorded separately in [`data/panel-art.tsv`](data/panel-art.tsv) and can be decided whenever the evidence is in:

```sh
python3 scripts/panelart.py list --panel 001-01
python3 scripts/panelart.py choose 001-01 v02
python3 scripts/panelart.py status
```

Undecided panels show their newest candidate, so the book reads end to end throughout, and a panel with more than one live version gets an "Other versions" strip in the viewer. The layout, the decision record, and the repository cost are in [`design/panel-versions.md`](design/panel-versions.md).

Page sheets are not generated. A page is composed from its panels by layout, the way a comic page is actually made, so the page grammar governs it and it costs no generation time.

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys the site whenever `main` changes. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. The workflow can also be started manually with **Actions → Publish GitHub Pages → Run workflow**.
