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

## Local, open-weight options

Every candidate above rents someone else's weights. Open-weight models running on
the drafting Mac change the economics completely: no marginal cost per image, no
vendor that can move the model underneath a half-finished book, and a style LoRA
that belongs to us. They also introduce two constraints the hosted models do not
have — a licence that may forbid the only thing this repository exists to do, and
a wall clock.

### The licence split decides most of it

This is a graphic novel intended for publication. An image generated by weights
licensed for non-commercial use cannot go in it, and that rules out most of what
the "best local model" guides recommend:

| Model | Parameters | Licence | Usable in the book |
| --- | ---: | --- | --- |
| FLUX.2 [klein] 4B | 4B | Apache 2.0 | Yes |
| Z-Image / Z-Image Turbo | 6B | Apache 2.0 | Yes |
| Chroma1-HD | 8.9B | Apache 2.0 | Yes |
| FLUX.1 [schnell] | 12B | Apache 2.0 | Yes |
| Qwen-Image | 20B | Apache 2.0 | Yes |
| SDXL 1.0 | 2.6B | CreativeML OpenRAIL++-M | Yes |
| Stable Diffusion 3.5 | 2.5B / 8B | Stability Community | Yes below $1M revenue |
| FLUX.1 [dev] | 12B | FLUX.1-dev non-commercial | Evaluation only |
| FLUX.2 [klein] 9B | 9B | FLUX.2-dev non-commercial | Evaluation only |
| FLUX.2 [dev] | 32B | FLUX.2-dev non-commercial | Evaluation only |

The distinction is self-hosting, not the model. Renting FLUX.2 [dev] through fal,
BFL, or OpenRouter carries commercial terms; downloading the same weights and
running them here does not. So the recommendation earlier in this document stands:
the hosted FLUX.2 [dev] pipeline is licensed for the book. What changes is that
"just run it locally instead" is not a free substitute for it.

### What fits 16 GB

macOS wants roughly 5 GB on top of the model, which leaves about 11 GB. In order
of usefulness to this book:

1. **SDXL 1.0** (6.94 GB) — the practical answer for a trained style. It is the
   oldest model here and the least impressive out of the box, but it renders at
   1216×832, close enough to the 1200×800 panel slot to need no reframing, and
   Draw Things trains LoRAs on-device on a 16 GB machine. For a book whose binding
   constraint is style consistency rather than raw fidelity, a trained SDXL beats an
   untrained better model.
2. **FLUX.2 [klein] 4B** (7.75 GB weights, ~13 GB pipeline) — the best image quality
   that is both Apache 2.0 and small enough to run here. Tight at 16 GB; use the
   4-bit or 8-bit quantisation in mflux, which tracks Klein releases.
3. **Z-Image Turbo** (6B) — distilled to 8 steps, so it is the fastest thing on the
   list by a wide margin. Wrong model to finish a panel with, right model for the
   framing sweeps the roster currently assigns to Qwen-Image, at zero cost.
4. **Chroma1-HD** (8.9B) — FLUX.1-schnell rebuilt as a neutral finetuning base and
   relicensed Apache 2.0. Quantised it will run, barely. Its reason to exist is
   being trained on, which is the next tier's job.

Do not use FLUX.1 [dev] here, however often it is recommended. It is the standard
16 GB suggestion and it is the wrong licence for this repository.

### What fits 48 GB

48 GB removes quantisation compromises rather than unlocking a different class of
model, because the models that would use the extra room are the non-commercial ones.

1. **Chroma1-HD at bf16 or fp8** — the strongest commercially usable base to train a
   style on. It was built to be finetuned, it inherits FLUX's contour and blacks, and
   at 8.9B it fits with room for the training run itself. This is the local analogue
   of the hosted FLUX.2 [dev] + LoRA recommendation, and the only one that ends with
   a style we own outright.
2. **FLUX.2 [klein] 4B at full precision** — no longer squeezed, so it can render
   above panel size and be downsampled, which is how to get printable grain.
3. **Qwen-Image Q8** (21.8 GB) — fits comfortably, and is Apache 2.0. Its advantage is
   text rendering, which this book actively does not want, so it earns its place only
   as a second opinion on composition.
4. **Evaluation-only, if you want to know what you are giving up:** FLUX.1 [dev] Q8
   (12.7 GB), FLUX.2 [klein] 9B fp8 (~14–16 GB), and FLUX.2 [dev] GGUF Q4 (19.3 GB)
   all fit. Score them in the bake-off, then buy the winner through an API rather
   than shipping its output from here.

### Installing them

Verified on the drafting Mac (M1 Pro, 16 GB) on 2 September 2026:

```sh
uv tool install mflux --python 3.12    # MLX-native; 37 commands, one per model family
uv tool list                           # the exact command names, which move between releases
```

Two things only became clear once it was installed, and both matter more than any
benchmark:

- **The published weights are usually far larger than the memory footprint.**
  Hugging Face serves FLUX.2 [klein] 4B at 22.1 GB and Z-Image Turbo at 30.6 GB,
  both bf16. Neither is a download this machine has the disk for. The prequantized
  MLX build `RunPod/FLUX.2-klein-4B-mflux-4bit` is **4.3 GB**, and it is the only
  reason a 16 GB laptop can run any of this today. Prefer a prequantized repository
  over quantising locally; `data/local-models.json` records both numbers.
- **mflux ships `mflux-train`.** Local LoRA training is a command, not a project.
  That is the half of the recommendation below that actually matters.

### Running them

`scripts/localgen.py` puts these models in the same bake-off as the hosted ones,
against the same prompts and the same rubric:

```sh
python3 scripts/localgen.py doctor     # this Mac, and what it can actually run
python3 scripts/localgen.py estimate   # wall clock for a run and for the book
python3 scripts/localgen.py run        # generate and write the comparison sheet
```

It filters by the two constraints above without being asked: models larger than the
machine's memory are excluded, and non-commercial weights are skipped unless
`--allow-non-commercial` says otherwise, in which case the run is stamped
evaluation-only in its manifest and on the published sheet. The roster lives in
`data/local-models.json` rather than in Python, because command names, repository
ids, and quantisation move faster here than the hosted prices do.

### Throughput is the real constraint

The book needs about 3,900 generations at six attempts per slot. Published figures
are for M4-class chips: FLUX.1 [dev] at Q6 takes 50–90 seconds for one 1024×1024
image at 20 steps on an M4 Pro, SDXL lands between 10 and 40 seconds on 16 GB, and
a few-step distilled model like Z-Image Turbo is far quicker. The drafting machine
here is an M1 Pro, which is materially slower than any of those numbers.

At 60 seconds per image the full book is about 65 hours of continuous compute; at
120 seconds it is closer to 130. That is weeks of wall clock next to a hosted run
that costs $114 and finishes overnight. The conclusion is not that local generation
is wrong — it is that local generation is for the phase where iteration count
matters more than throughput.

### Recommendation

Use local models for style development, not for bulk production.

- **Train the style locally, on either machine.** A style LoRA is a few thousand
  steps over a few dozen approved reference images — exactly the workload where
  free iteration beats fast throughput, and the artefact it produces is ours
  permanently. On 16 GB train SDXL; on 48 GB train Chroma1-HD.
- **Sweep framing locally.** Z-Image Turbo replaces the Qwen-Image sweep line in the
  roster at no cost, which removes the cheapest paid tier entirely.
- **Render finals through the API.** The hosted pipeline keeps its commercial terms,
  finishes in hours rather than weeks, and — with the local LoRA in hand — no longer
  depends on prompt discipline to hold the style.

The one thing that would change this: if a trained local model scores as well on the
rubric as the hosted candidates, the wall clock stops being a cost and becomes a
schedule. Score it in the same bake-off before deciding.

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

## Sources

### Hosted pricing

Prices were collected in September 2026 and are recorded in `scripts/imagegen.py`
so estimates stay in one place. OpenRouter meters each call, so a live run's
manifest records what was actually charged rather than what was predicted.

- [OpenRouter unified Image API](https://openrouter.ai/blog/announcements/image-api/) and its [image model catalogue](https://openrouter.ai/collections/image-models)
- [Nano Banana Pro (Gemini 3 Pro Image) API pricing](https://openrouter.ai/google/gemini-3-pro-image)
- [GPT Image 2 pricing breakdown](https://unifically.com/blogs/gpt-image-2)
- [FLUX.2 [dev] LoRA on fal](https://fal.ai/models/fal-ai/flux-2/lora) and [FLUX LoRA training](https://fal.ai/models/fal-ai/flux-lora-fast-training)
- [Replicate and fal image model pricing](https://pricepertoken.com/image)
- [Image Generation API Pricing 2026 — CostLayer](https://costlayer.ai/blog/image-generation-api-pricing-2026-complete-cost-comparison)

### Local and open weight

- [FLUX.2 [klein] 4B on Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) — Apache 2.0; the 9B is not
- [FLUX.2 [klein] 9B on Hugging Face](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B)
- [Chroma1-HD](https://huggingface.co/lodestones/Chroma1-HD) — 8.9B, Apache 2.0, built as a finetuning base
- [Z-Image Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) — 6B, Apache 2.0, 8-step distilled
- [Qwen-Image](https://github.com/QwenLM/Qwen-Image) — 20B, Apache 2.0
- [Local image generation on Mac, by RAM tier](https://modelfit.io/guides/local-image-generation-mac/)
- [Draw Things on-device LoRA training](https://wiki.drawthings.ai/wiki/LoRA_Training)
- [Metal FlashAttention 2.0 — on-device inference and training on Apple Silicon](https://engineering.drawthings.ai/p/metal-flashattention-2-0-pushing-forward-on-device-inference-training-on-apple-silicon-fe8aac1ab23c)
