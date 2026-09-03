# zz-no-consumer
A graphic novel about emergent AI agent coordination, instrumental convergence, and the humans trying to understand what happened.

## Repository map

- `content/` — canonical human-editable story material.
- `content/parallel-tracks/` — optional companion-track briefs that do not alter the canonical 112-page narrative.
- `prompts/` — image-generation prompts and page-specific direction.
- `research/` — source material, timeline, cast, glossary, and provenance notes.
- `design/` — lettering, page grammar, palette, visual continuity, and layout references.
- `assets/` — artwork and other media used by the site.
- `data/` — structured page, character, continuity, asset, and generation metadata.
- `scripts/` — validation, cross-reference, and site-generation utilities.
- `site/` — source styles and templates for the published site.
- `docs/` — generated GitHub Pages output; do not edit manually.

The complete 112-page first-draft script is in `content/pages/`, with every page currently in review. The assumptions are locked in `content/story-contract.md`, the beat sheet is `content/page-plan.md`, and the drafting and production protocol is `content/draft-readiness.md`. The source-language audit and completed paraphrase disposition are in `research/exact-text-permissions-audit.md`; the story-level security pass and resolved public-site scope decision are in `research/security-sensitivity-review.md`. Last-mile attribution rules remain in `research/draft-source-notes.md`. Before revising or renaming pages, run:

```sh
python3 scripts/validate-continuity.py
python3 scripts/validate-production-foundations.py
```

The scene-level evidence boundary is tracked in `research/scene-provenance.md`, and the canonical page-script shape is in `design/page-script-template.md`.

The proposed inside-the-collective documentary is scoped in `content/parallel-tracks/messages-from-the-board.md`; its primary-source artifact gate is `research/agent-message-ledger.md`.

## Source vault

Potentially non-redistributable originals and internal review artifacts live in the Git-ignored `256t/` directory. The repository tracks only their canonical URLs and redistribution disposition in `data/256t-sources.tsv`.

```sh
python3 scripts/sync-256t.py sync    # download/update local snapshots
python3 scripts/sync-256t.py check   # report upstream content changes without accepting them
python3 scripts/sync-256t.py status  # show local hashes and missing/error states
```

Distinct downloaded bodies are retained by SHA-256 under `256t/records/`. Tracked prose and the public site should link to the original URLs rather than copied report pages, screenshots, or extended fragments when reuse rights are uncertain.

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

The `book` command writes one placeholder for every page and every panel image slot in `content/pages/` — 112 page sheets at 700×1000 and 541 panel images at 1200×800:

```sh
python3 scripts/textimage.py book --out-dir docs/assets/placeholders
```

Each panel placeholder carries that panel's own `Frame`, `Action`, and lettering; each page sheet carries the page purpose. `scripts/build-site.py` runs this as part of every build and embeds the result, so the viewer's page sheets, chapter grids, and single-image views all show real script text in the frame the final art will occupy. Both site indexes link straight into that read-through, and `scripts/validate-viewer.py` fails if any placeholder is missing or carries no alt text.

Panel placeholders are keyed to the same image slots the viewer routes use, so a page written as one grouped run of panels gets the single image its route exposes. Replacing a placeholder with final art is a matter of pointing the image record at `assets/art/panels/NNN-II.*`; the route, alt text, and cross-reference link do not move.

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys the site whenever `main` changes. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. The workflow can also be started manually with **Actions → Publish GitHub Pages → Run workflow**.
