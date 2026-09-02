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
- `scripts/` — validation and site-generation utilities.
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

The generated site also includes an isolated viewer validation section at `docs/viewer/`. It publishes stable directory-style routes for the viewer home, chapter overviews, pages, panel images, and their information views before final artwork exists. Every view exposes up, down, left, right, in, out, and home links; the matching keyboard shortcuts are Arrow keys, Enter, Escape, and H.

Validate the entire generated route graph with:

```sh
python3 scripts/validate-viewer.py
```

Generate the provisional 57-spread production contact sheet with:

```sh
python3 scripts/make-thumbnails.py
```

The result is `256t/site/production/thumbnails/index.html`. Its panel geometry is a private review aid rather than locked layout; findings and required print proofs are tracked in `content/production-review.md`.

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys the site whenever `main` changes. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. The workflow can also be started manually with **Actions → Publish GitHub Pages → Run workflow**.
