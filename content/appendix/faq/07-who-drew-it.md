---
id: FQ-07
kind: faq
audience: method
title: Who drew the pictures?
pages: [105, 114]
answer: >-
  An image model, running locally. Every generated image committed to this project came
  from FLUX.2 [klein] 4B under an Apache-2.0 licence, run through `mflux` on the author's
  own machine with no hosted API, and each generation is logged with its model, seed and
  output path. No hosted image provider has produced a committed image, and nothing from a
  non-commercially-licensed model may appear in the book.
---

## The short answer

The art is generated, and the generation is logged rather than described.

`data/generation-log.jsonl` is an append-only record: one line per generation, carrying the
timestamp, the model identifier, the page and panel, the seed, the output path, the route,
and the cost. It is not rewritten by the renumbering tools, because it is a dated record of
what happened rather than a description of the current state of the book. A reader who
wants to know where a particular panel came from can look up its key and get an answer with
a seed attached.

The choice of a locally-run, permissively-licensed model was not aesthetic. A hosted
provider would mean prompts leaving the machine and terms that can change after the fact; a
non-commercial licence would mean the book could not be sold or forked as one thing. The
project is released under the GPL, which only works if every component can travel with it.

## The long answer

There is an obvious objection here and it belongs in this answer rather than in a footnote:
a book arguing that automation outruns oversight, illustrated by automation. It is the same
objection as [FQ-17](#fq-17-is-a-book-about-ai-risk-written-with-ai-help-self-serving),
and it has the same answer — the disclosure is the point, and a reader who knows what made
an image can discount it.

What the disclosure does not do is settle the labour question. A generated illustration is
work an illustrator did not get, and the fact that this project could not have commissioned
one does not make that untrue; it makes it a smaller instance of the thing the book is
about. [PR-45](#pr-45-the-people-who-could-have-stopped-it-had-no-way-to-refuse-together)
puts the organised-labour version of that objection in a practitioner's terms, in this same
appendix, where it can be argued with rather than absorbed.

Two constraints are worth stating plainly because they bound what a reader is looking at.
The panel art in `assets/art/panels/` is versioned rather than replaced — the production
tool adds candidates and `data/panel-art.tsv` records which version is chosen, so a
superseded image is still in the history. And the pipeline is deliberately dull:
standard-library Python, a local model, `rsvg-convert` for rasterising, GitHub Pages for
publication. Nothing in it requires trusting a service that could disappear.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's own record | [CREDITS.md](https://github.com/curtcox/zz-no-consumer/blob/main/CREDITS.md) | 5 Sep 2026 | The image model, its weights and licence, the local-only route, and the exclusion of non-commercially-licensed models from anything that could appear in the book. |
| Auditable trail | [data/generation-log.jsonl](https://github.com/curtcox/zz-no-consumer/blob/main/data/generation-log.jsonl) | 2026 | One logged line per generation, with model, seed, path and cost; append-only, never rewritten by the renumbering tools. |
| Tooling record | [scripts/README.md](https://github.com/curtcox/zz-no-consumer/blob/main/scripts/README.md) | 2026 | What each tool does, including the artwork production and panel-selection commands. |
| Licence | [LICENSE](https://github.com/curtcox/zz-no-consumer/blob/main/LICENSE) | 5 Sep 2026 | GPL-3.0-or-later for the whole repository, and the reason every component licence has to be compatible with it. |
| Field standard | [ACM Code of Ethics](https://www.acm.org/code-of-ethics) | 2018 | Attribution and honest representation of how work was produced as professional obligations. |
| Field practice | [Sigstore](https://www.sigstore.dev/) | — | The principle the generation log borrows: provenance is worth something when it is a record, not a claim. |
| Field practice | [SLSA supply-chain levels](https://slsa.dev/) | — | Why a build that can be reproduced from a logged input beats a build that is merely described. |
