# zz-no-consumer
A graphic novel about emergent AI agent coordination, instrumental convergence, and the humans trying to understand what happened.

## Repository map

- `content/` — canonical human-editable story material.
- `prompts/` — image-generation prompts and page-specific direction.
- `research/` — source material, timeline, cast, glossary, and provenance notes.
- `design/` — lettering, page grammar, palette, and layout references.
- `assets/` — artwork and other media used by the site.
- `data/` — structured page, character, continuity, and generation metadata.
- `scripts/` — validation and site-generation utilities.
- `site/` — source styles and templates for the published site.
- `docs/` — generated GitHub Pages output; do not edit manually.

The first-draft assumptions are locked in `content/story-contract.md`. The 112-page beat sheet is `content/page-plan.md`, the working protocol is `content/draft-readiness.md`, and last-mile quotation rules are in `research/draft-source-notes.md`. Before drafting or renaming pages, run:

```sh
python3 scripts/validate-continuity.py
```

The scene-level evidence boundary is tracked in `research/scene-provenance.md`, and the canonical page-script shape is in `design/page-script-template.md`.

## Local site build

The site builder uses only Python's standard library:

```sh
python3 scripts/build-site.py
open docs/index.html
```

The builder converts Markdown in `content/`, `prompts/`, `research/`, and `design/` into a browsable HTML site and copies files from `assets/` and `site/` as appropriate.

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys the site whenever `main` changes. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. The workflow can also be started manually with **Actions → Publish GitHub Pages → Run workflow**.
