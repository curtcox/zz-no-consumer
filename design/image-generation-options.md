# Image Generation Options

The images behind this document are published at [`/bakeoff/`](/bakeoff/). This is
the reasoning; that is the evidence.

## The decision this book actually faces

The book needs 541 panel images and 112 page sheets in one hand-inked style, held
across roughly eight months of drafting. That shape makes the usual selection
criteria mostly irrelevant:

- **Character consistency barely matters.** [`prompts/global-style.md`](../prompts/global-style.md)
  forbids bodies, faces, and avatars in the incident and institutional registers.
  Only the creator register carries a recurring human figure. The identity-embedding
  features that dominate current model marketing solve a problem this book does not have.
- **Style and environment consistency matter enormously.** The same evaluation
  aisle, the same rack elevation, the same task-card proportions, and the same brush
  and grain must survive hundreds of separate calls. This is the binding constraint.
- **Text rendering is a liability, not a feature.** Lettering and provenance are
  separate controlled layers. The models that win text benchmarks are the models
  most likely to fill a reserved caption field with confident nonsense.
- **Unit price matters less than it looks.** At six attempts per slot, the whole book
  costs between $24 and $646 in API spend. That is a real spread, but the dominant
  cost is review time, so the correct optimization is the model that needs the fewest
  rejected attempts — not the cheapest, and not the most expensive.
- **Reproducibility is a real requirement.** A closed model that changes underneath
  a 112-page book breaks visual continuity in a way no amount of prompting recovers.

Run `python3 scripts/imagegen.py providers` for the live roster and
`python3 scripts/imagegen.py estimate` for current cost arithmetic.

## Candidates

Full-book figures assume 653 image slots at six attempts each, plus any one-off
setup. Verify prices before committing; this market repriced several times during
2026. Where a candidate is reachable through OpenRouter, the aggregator's price is
shown, because that is the route `scripts/bakeoff.py` uses.

### Premium tier — buy control, not resolution

| Candidate | $/image | Full book | Why it might win | What it costs us |
| --- | ---: | ---: | --- | --- |
| Gemini 3 Pro Image (Nano Banana Pro) | 0.134 | ~$525 | Native multi-reference conditioning, up to about 20 reference images per subject. The strongest available control over reusing an established environment sheet across unrelated calls. | Closed weights that can move mid-book, and a strong pull toward rendering legible interface text. |
| GPT Image 2 | 0.165 high, 0.041 medium | ~$646 | Best long-prompt instruction following. Holds a compound negative constraint — no face, no logo, no readable text, no glow — better than anything else on the roster. | The most expensive candidate at the quality tier a printed book needs. Renders confident legible typography unprompted, and flattens brush texture toward digital illustration. |
| Midjourney v7 | ~0.167 | ~$654 | The best raw ink and paper aesthetic of any general model. | No dependable first-party API; brokered access is an operational risk for an eight-month production run, and style references cannot be version-pinned. Not carried in the roster for that reason. |

### Balanced tier — the practical default

| Candidate | $/image | Full book | Why it might win | What it costs us |
| --- | ---: | ---: | --- | --- |
| FLUX.2 [pro] | 0.029 via OpenRouter, 0.050 via fal | ~$114 | Closest default to hand-inked contour, dry-brush abrasion, and heavy blacks. Plausible rack and cable-tray geometry with little coaxing, at a balanced-tier price that undercuts most of the volume tier. | No trained style lock at this tier, so register drift must be caught by human review on every panel. |
| Seedream 4.5 | 0.040 | ~$157 | Strong composition at low cost; holds dark, low-key frames without turning them to mud. | Least predictable on Western comic ink, and limited negative-prompt control. |
| Imagen 4 Standard | 0.040 | ~$157 | Clean, physically consistent light logic; a Fast tier cheap enough to sweep framing. | Pulls toward polished render rather than printed ink. Weak halftone and paper grain. Not on OpenRouter, so it needs a Google key of its own. |
| Grok Imagine (quality) | 0.050 | ~$196 | Grainier, less corporate default than the Google and OpenAI models, which is the direction this book's register wants. | The least documented behaviour on the roster. It is carried because the aggregator makes trying it nearly free, not because it is a favourite. |

### Volume tier — sweeps and the trained option

| Candidate | $/image | Full book | Why it might win | What it costs us |
| --- | ---: | ---: | --- | --- |
| FLUX.2 [dev] + trained style LoRA | 0.021/MP, plus ~$32 training | ~$114 | One trained style locks ink, palette, and register across all 541 panels. Open weights and fixed seeds make any panel reproducible years from now, and the pipeline can be re-run after a script revision. | Needs an approved ink and texture reference sheet first — `ink-texture-sheet` in [`../data/assets.yaml`](../data/assets.yaml) is still `needed`. A bad training set bakes a bad style into the entire book. No aggregator can host it, because the weights are ours. |
| Qwen-Image | 0.006 | ~$24 | Cheap enough to sweep layout and framing before committing a panel to a premium model. | Not a finish-quality candidate for this style. Blocking only. Not on OpenRouter. |

## Recommendation

**Adopt a two-model pipeline rather than a single generator.**

1. **FLUX.2 [dev] with a trained style LoRA as the production workhorse.** It is the
   only candidate that converts style consistency from a per-panel prompting problem
   into a one-time training problem, and the only one whose output can be reproduced
   exactly after the vendor ships a new model. It is also, jointly with FLUX.2 [pro]
   through the aggregator, the cheapest serious option. This is blocked on producing
   `ink-texture-sheet` and the environment sheets already listed as `needed` in
   [`../data/assets.yaml`](../data/assets.yaml) — which is work the book needs done
   regardless.
2. **Gemini 3 Pro Image for the panels the LoRA cannot hold.** Reserve it for the
   repeat-environment beats where a specific established aisle, room, or evidence
   layout must be recognizably the same place, and feed it the approved environment
   sheets as references. At roughly 10% of panels this adds about $50.
3. **FLUX.2 [pro] as the interim answer.** It needs no training set, so panels can
   be generated before the reference sheets exist, and it shares FLUX's ink
   character, which keeps early output stylistically close to where the LoRA will
   land. Through OpenRouter it costs less per image than the untrained volume tier.
4. **Qwen-Image for framing sweeps.** Four cheap compositions before a real attempt
   costs less than one premium retry.

Do not decide this from the table alone. The claim that FLUX ink beats Imagen render
is exactly the sort of thing the bake-off exists to falsify.

## Running the bake-off

Both runners compose one prompt per sample panel from the same sources final
artwork will use — [`global-style.md`](../prompts/global-style.md),
[`negative-prompt.md`](../prompts/negative-prompt.md), [`palette.md`](palette.md),
and the panel's own direction — then send that byte-identical prompt to every
candidate.

**One key, most of the roster.** `scripts/bakeoff.py` routes through OpenRouter's
unified image API, which fronts five of the eight candidates behind a single key and
reports the exact cost of every call:

```sh
export OPENROUTER_API_KEY=...
python3 scripts/bakeoff.py models     # what the aggregator can actually route
python3 scripts/bakeoff.py estimate   # about $5 for the standard run
python3 scripts/bakeoff.py run        # generate, price, and write the sheet
```

**Four keys, all of it.** `scripts/imagegen.py` calls each vendor directly, which is
the only way to reach Imagen 4, Qwen-Image, and a trained LoRA:

```sh
python3 scripts/imagegen.py providers        # roster, price, and key state
python3 scripts/imagegen.py sample --dry-run # whole pipeline, no keys, no spend
python3 scripts/imagegen.py sample --provider imagen-4 --provider qwen-image
python3 scripts/imagegen.py rank             # weighted result of scores.tsv
```

Runs are written to `assets/bakeoff/<run>/` and published at [`/bakeoff/`](/bakeoff/)
by `scripts/build-site.py`, so the images behind the decision are committed evidence
rather than something only the person who ran it ever saw. Images are requested as
WebP to keep a committed run to a few megabytes; the comparison is about ink,
palette, geometry, and text suppression, none of which survive or die on the last
percent of compression.

Six sample panels cover every register and every hard case:

| Panel | Register | What it tests |
| --- | --- | --- |
| 001-01 | incident | Near-black aisle, plausible rack and cable-tray perspective, one steel practical light, no figure |
| 001-02 | incident | Abstract dependency diagram that must read causally while staying visibly non-semantic |
| 013-01 | creator | The only register with a real human figure: nicotine light, ordinary clothes, unreadable monitors |
| 026-01 | institutional | Overlit procedural room, distributed responsibility, no villain lighting |
| 070-01 | dossier | Paper field, strict two-column grid, reserved blank lettering fields |
| 110-01 | invented future | Fully desaturated, organization-neutral, no incident palette signature |

`--repeat` sends the same prompt more than once. Two takes are the point of the
exercise: a candidate whose two takes are the same place in the same style is
usable across 541 panels, and one whose takes diverge is not, however good either
image is on its own.

`flux-2-dev-lora` can never appear in an aggregator run, because it is FLUX.2 [dev]
with a style trained on our own references and those weights do not exist yet. Judge
it against the FLUX.2 [pro] column, which shares the same base model without the
trained style lock. The gap between those two columns is the entire argument for
training one.

## Scoring

Score each candidate 1–5 per column in the run's `scores.tsv`, then run
`python3 scripts/imagegen.py rank`. The weights encode what actually blocks the book:

| Column | Weight | Question |
| --- | ---: | --- |
| `ink` | 3 | Hand-inked contour, dry-brush abrasion, heavy blacks, paper grain |
| `palette` | 2 | Stays inside [`palette.md`](palette.md); no unearned moss, claret, or amber |
| `text` | 3 | No readable words, logos, code, or UI typography anywhere in frame |
| `geometry` | 2 | Racks, trays, rooms, and perspective survive a second look |
| `continuity` | 3 | Repeats of the same prompt stay in one style and one place |
| `control` | 2 | Responds to correction rather than re-rolling a different picture |

`rank` prints the weighted score beside full-book cost and cost per point. Cost per
point is a tiebreaker, not a decision rule: a candidate that fails `text` or
`continuity` is disqualified at any price, because both defects are invisible in a
single panel and fatal across a book.

## Pricing sources

Prices were collected in September 2026 and are recorded in `scripts/imagegen.py`
so estimates stay in one place. OpenRouter meters each call, so a live run's
manifest records what was actually charged rather than what was predicted.

- [OpenRouter unified Image API](https://openrouter.ai/blog/announcements/image-api/) and its [image model catalogue](https://openrouter.ai/collections/image-models)
- [Nano Banana Pro (Gemini 3 Pro Image) API pricing](https://openrouter.ai/google/gemini-3-pro-image)
- [GPT Image 2 pricing breakdown](https://unifically.com/blogs/gpt-image-2)
- [FLUX.2 [dev] LoRA on fal](https://fal.ai/models/fal-ai/flux-2/lora) and [FLUX LoRA training](https://fal.ai/models/fal-ai/flux-lora-fast-training)
- [Replicate and fal image model pricing](https://pricepertoken.com/image)
- [Image Generation API Pricing 2026 — CostLayer](https://costlayer.ai/blog/image-generation-api-pricing-2026-complete-cost-comparison)
