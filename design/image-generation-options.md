# Image Generation Options

The images behind this document are published at [`/bakeoff/`](/bakeoff/). This is
the reasoning; that is the evidence.

## The decision this book actually faces

The book needs one image per panel slot and one sheet per page — 547 and 112 as the
script currently stands, per `python3 scripts/panels.py report` — in one hand-inked
style, held across roughly eight months of drafting. Every other panel count below is
a measurement taken during the run it describes, and is left at the figure it was
measured against. That shape makes the usual selection
criteria mostly irrelevant:

- **Character consistency matters less than usual, but it is not nothing.**
  [`prompts/global-style.md`](../prompts/global-style.md) forbids drawing the *agents*
  as bodies, faces or avatars — a rule about personifying software, not about human
  presence, and one both a reader and a text encoder can misread as the latter.
  Counting the script rather than the rule: 120 panels are typed `portrait` or `figure`
  in [`../data/panel-types.tsv`](../data/panel-types.tsv), and 61 name a person the art
  has to draw. Curt recurs across five desk states. So the identity-embedding features
  that dominate current model marketing are not the binding constraint here, but they
  are not irrelevant either.
- **Style and environment consistency matter enormously.** The same evaluation
  aisle, the same rack elevation, the same task-card proportions, and the same brush
  and grain must survive hundreds of separate calls. This is the binding constraint.
- **Text rendering is a requirement, not a liability.** *Reversed 3 September 2026;
  see [The prohibition was removed](#the-prohibition-was-removed-and-it-reverses-the-model-choice).*
  Captions and provenance stay on the lettering layer, but a panel's own display strings
  are project-authored and the model is expected to spell them. What remains a liability
  is invented lettering in the surfaces nobody asked about, which every model on this
  roster still produces.
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

Byte-identical is now enforced at the tightest text encoder in the field rather than
assumed. Sending the same 1,060-token string to a model that reads 512 and one that
reads 1,024 is not one experiment, it is two, and the shorter model is judged on a
prompt missing its palette and its negatives. `run_samples` composes to the smallest
`prompt_tokens` among the candidates actually in the run, so every model reads the
whole of what it is sent.

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

### First light, and what it settled

Run [`0002-local-first-light`](/bakeoff/0002-local-first-light/) is FLUX.2 [klein] 4B
at 4-bit generating panel 001-01 twice on an M1 Pro with 16 GB. Measured: **66 seconds
per image at 1200×800 in four steps, 11.53 GB peak memory** — against a 40-second
estimate, so the full book is about 72 hours of compute on this machine rather than 44.
Peak memory is within half a gigabyte of everything a 16 GB Mac has to spare, which is
why `--low-ram` is not optional here.

> **Superseded in part, 3 September 2026.** This run was made before anyone checked
> how much of the prompt the model receives. It receives 512 tokens; the prompt was
> about 1,060. The `text` and `continuity` verdicts below were drawn from a prompt
> whose palette clause, output discipline and entire negative prompt never arrived.
> The measurements stand; two of the three conclusions do not. See
> [The prompts were being cut in half](#the-prompts-were-being-cut-in-half).

The output settled three rubric lines on the first attempt:

- **`ink` is genuinely good.** Hand-inked contour, heavy blacks, halftone, dirty-paper
  border, a plausible aisle in correct perspective with racks and overhead cable trays.
  It also placed the service cart deep in the aisle — an instruction that appears only
  as a continuity anchor in the third paragraph of the prompt — and reserved the caption
  field in the upper-left safe area exactly as asked. This line still holds; it is the
  one part of the prompt that was never truncated, because it sits at the front.
- **`text` fails.** Both takes filled the reserved caption box with gibberish lettering
  and put fake labels on the equipment. *Still true, but not for the reason given here.*
  This was read as the model defying
  [`negative-prompt.md`](../prompts/negative-prompt.md). The negative prompt was never
  delivered. Invented lettering survives a prompt that does reach the model, so the
  finding holds — the explanation does not.
- **`continuity` fails, which is the finding that matters.** *Overturned.* The two takes
  were not the same place because nothing in the delivered prompt said what the place
  was: the register clause was four adjectives, and the environment geometry lived in
  [`visual-continuity.md`](visual-continuity.md), which the prompt never quoted. Once
  the register names the room, four panels of page 001 come back as recognisably the
  same aisle. This was a prompt defect wearing a model defect's clothes.

The reading at the time — that this was the argument for a trained style, made in
images rather than prose — was wrong, or at least premature. Prompt discipline had not
been tried; half of it was being discarded in transit. `mflux-train` is still in the
same install, and a trained style is still the stronger answer for a 541-panel book,
but it is no longer the *only* answer to continuity, and it should not be bought on
the strength of this run.

### The prompts were being cut in half

**Measured 3 September 2026.** A text encoder does not reject a prompt that is too
long for it. It encodes the front, discards the rest, and says nothing. `mflux` pins
FLUX.2 to 512 tokens in `flux2_klein.py`, and it is not a CLI option. A composed panel
prompt was **1,062 tokens**. Across sixty sampled panels the median was 1,029 and
**sixty of sixty were over the limit**.

What arrived, and what did not:

| Section | Tokens | Fate |
| --- | ---: | --- |
| Rendering target | 116 | kept |
| Register clause | 20 | kept |
| Panel direction | 27 | kept |
| Exact-text clause | 46 | kept |
| Composition | 337 | **cut mid-sentence** |
| Light and material | 73 | **discarded** |
| Palette | 105 | **discarded** |
| Output discipline | 83 | **discarded** |
| Avoid entirely | 255 | **discarded** |

Every defect in the runs above has a line in that table. Colour outside the palette:
the palette clause never arrived. Invented lettering everywhere: the negative prompt
never arrived. Drawn panel borders: "drawn panel border" is in the discarded negative
list. Drawn caption boxes: the prohibition was severed mid-clause, at
`…no drawn caption box,` | `balloon, or slate in them`.

Deleting the negative block entirely and re-rendering the same seed produced a
near-identical image, which is the proof: 255 tokens of prohibitions were not fighting
the model and losing, they were not being spoken.

The second finding is proportion. The panel's own direction was 27 of 1,062 tokens.
Generic boilerplate was 453. The only part of the prompt that differs between panels
was outweighed roughly seventeen to one, which is why every register — a home office,
an institutional room, an invented future — came back as the same industrial control
room.

`scripts/imagegen.py` now composes against the model's real ceiling, dropping whole
ranked sections rather than letting the encoder cut a sentence in half, and reporting
what it dropped. `prompt_tokens` per model lives in
[`../data/local-models.json`](../data/local-models.json). Verified against the real
tokenizer over all 541 panels: **none truncated**, median 401 tokens, maximum 456.

### Second light, and what the delivered prompt settled

The ten panels in `assets/art/panels/` carry both versions: `v01` from the truncated
prompt and `v02` from the delivered one, on the same seed, so the prompt is the only
variable.

- **Register is a place, not a mood.** The clauses now name the environment from
  [`visual-continuity.md`](visual-continuity.md) instead of gesturing at it with
  adjectives. "Nicotine-beige practical light, intimate but unglamorous desk scale"
  produced a factory; a wooden desk, two monitors, a lamp, a mug, a printer and a
  doorway produced Curt's office. Institutional panels became ordinary overlit meeting
  rooms. A register carries the materials; the panel's own direction still decides the
  framing, which is why the camera language was taken back out of the incident clause.
- **Continuity is reachable without training.** Four panels of page 001 came back as
  the same aisle — same racks, same trays, same slab, same cart.
- **Palette holds.** No claret outside its rule anywhere in the ten, where the
  truncated runs put red signage in panels that forbade it.
- **People stopped appearing** in panels that never asked for them.
- **`text` still fails.** Invented lettering is reduced and much less dense, and it is
  still in nearly every panel. One panel drew a caption box that the delivered
  composition rule explicitly forbids. This is the one finding from first light that
  survives intact, and it is the reason the reject-and-re-roll gate below still matters.

Run [`0003-local-delivered-prompt`](/bakeoff/0003-local-delivered-prompt/) repeats the
first-light experiment properly: the same six sample panels, two takes each, on prompts
the model reads in full. 12 images, 63 s each, no spend. What it settles:

- **`continuity` passes on five of six samples.** Both takes of the incident aisle are
  the same place in the same style — the exact comparison that produced "they cannot
  both be in the same book", now on the same panel and reversed. The creator sample is
  the strongest result on the page: two takes of a recognisable office, same desk, lamp,
  monitors, mug, printer and doorway, no face in either.
- **`ink` continues to hold**, across all five registers.
- **`text` fails again**, as expected, and one sample fails harder than anything in the
  ten: take 1 of the invented-future panel came back as a **six-cell comic page with
  speech balloons and faces** — a page layout, a panel grid, balloons and bodies, four
  prohibitions at once, from a prompt that carried the composition rule in full. Prompt
  delivery was necessary and is not sufficient.
- **The dossier sample puts claret across both takes** as redaction bars. Whether that
  is the palette rule working or breaking depends on a reading of
  [`palette.md`](palette.md) that this run does not settle.

One caveat about this evidence: neither bake-off runner supports `--bleed`, so every
image in `0003` carries the drawn paper border (measured 17–44 px) that production
output does not. The sheets compare models honestly against each other, but they do not
show what a produced panel looks like. Give the runners the flag, or read the run
knowing the margin is an artefact.

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

Production adds a measured surcharge. The model draws an aged-paper margin and a ruled
frame around the panel — in three of three renders at `--bleed 0`, at an inset of 24 to
31 pixels — despite the composed prompt forbidding a drawn border twice. `--bleed`
renders past the panel and crops the margin off, and it is the only thing that removes
it reliably:

| `--bleed` | Renders | Crop per side, vertical | Per image | 541 panels |
| ---: | --- | ---: | ---: | ---: |
| 0 | 1200×800 | — | 64 s | 9.6 h |
| 0.06 | 1280×848 | 24 px | — | *insufficient; under the measured border* |
| 0.08 | 1296×864 | 32 px | 73 s | 11.0 h |
| **0.10** | **1328×896** | **48 px** | **78 s** | **11.7 h** |
| 0.12 | 1360×912 | 56 px | 81 s | 12.2 h |

0.10 is the production setting: zero drawn border across all ten panels, forty edges
clean, at a 22% surcharge over an uncropped render. 0.08 also cleared every test panel
but leaves only a single pixel over the worst border measured, which is not a margin.

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

**Amended 3 September 2026.** This recommendation was reached while every candidate was
being sent half a prompt, so it rests on a comparison nobody actually ran. Two parts of
it move:

- **Train the style later, not first.** Training was the answer to a continuity failure
  that turned out to be a truncated prompt. Naming the environment in the register
  clause recovered most of it for nothing. A LoRA is still the stronger long-run answer
  for 541 panels, and it is still the artefact that belongs to us — but it is now an
  optimisation with a known baseline rather than a prerequisite.
- **The bake-off has to be re-run before it decides anything.** Its prompts were
  truncated too, and each candidate truncated them at a different length, so the run
  compared models on inputs they did not share. `run_samples` now composes against the
  tightest encoder in the field, so a re-run compares like with like. Until then, treat
  the tier rankings above as untested rather than as evidence.

What does not move: the licence split, the throughput arithmetic, and the conclusion
that local generation belongs to the iteration phase.

## Suppressing generated text

Assume no image generator will reliably stop rendering invented glyphs. The book
cannot carry them: [`negative-prompt.md`](../prompts/negative-prompt.md) forbids
readable generated wording outright, and
[`lettering.md`](lettering.md) already names the remedy — incidental interface
text "should be illegible, redacted, or omitted when it does not change the story
state." This section records what that costs in practice, measured on real output
rather than assumed.

### What the model actually does

Measured on `0002-local-first-light/flux2-klein-4b/001-01-1`, every region of
generated glyphs in the panel. That panel was drawn from a truncated prompt, so the
totals are an upper bound rather than the current rate — the delivered prompt reduces
glyph density without eliminating it. The *distribution* is the durable part, and it
did not change:

| Class | Share of panel | Where it lands |
| --- | ---: | --- |
| Narrative field | 2.85% | The caption box — a field the prompt explicitly asked the model to reserve |
| Interface components | 2.30% | Two screens on the right-hand cabinet, at `UI-TASK-CARD` and `UI-EVIDENCE-CARD` geometry |
| Incidental marks | 0.11% | Four rack-door labels, illegible at reading size |
| **Total** | **5.26%** | |

The distribution is the encouraging part. Glyphs are not scattered; they cluster in
the three places the design system already designates as text-bearing, because the
prompt asked for them. The model is filling the fields it was told to reserve.

### Three tactics, and which of them hold up

Tested by compositing over that panel:

1. **Letter over it.** The caption. Works completely, reads better than the
   generated box, and costs nothing — the lettering layer was going there anyway.
2. **Blank it.** The spurious second screen becomes an unlit blanking plate.
   Works completely and is the most robust tactic available, because dark
   featureless coverage needs no texture matching.
3. **Replace with the real component.** A `UI-TASK-CARD` over the cabinet screen.
   It covers the glyphs and it reads as pasted on: flat vector against hand-inked,
   grained, dry-brushed art, axis-aligned against a surface drawn in perspective.

Covering is easy. Matching is hard, and the split is predictable: an overlay works
where the element conventionally sits **above** the art plane — captions, balloons,
provenance slates — and fails where it belongs **inside** the depicted world, subject
to that scene's lighting, perspective, and ink.

Two consequences follow directly. Asking the model to "reserve a caption field"
invites it to draw a box and letter it; asking for a quiet dark area instead is
strictly better, because blanking beats matching. And moving machine text out of the
depicted world and onto the caption plane — which `lettering.md` already permits for
interface voices — converts the hard case into the easy one for most panels.

### Automatic glyph detection does not work here

**Tested 2 September 2026 against FLUX.2 [klein] 4B output. Negative result.**

The tempting completion of the overlay plan is to find generated glyphs
automatically and blank them. Three detectors were built with Pillow alone — no
numpy, no OpenCV, no OCR — and run against both takes of panel 001-01, whose glyph
regions had been measured by hand as ground truth.

| Approach | Method | Result |
| --- | --- | --- |
| Stroke detection | Black-hat: `MaxFilter(5)` minus the image, threshold, dilate to merge glyphs, flood-fill components | Flagged **96.8%** of the panel as one blob. A sweep of 21 threshold and merge combinations found **no usable operating point**; the only setting that caught all three true regions flagged **21.4%** of the panel across 70 blobs |
| Light-field localisation | Threshold for bright regions, morphological close, components, rank by `FIND_EDGES` density | Localisation is good — the caption is found at (48,48) 230×140 against a truth of (44,34) 244×112. Ranking fails: the two highest-scoring regions are false positives that beat the real caption, and the evidence card is missed entirely in the second take |
| Baseline alignment | Within each field, score glyph-candidate height uniformity times the fraction sharing a baseline — the strongest classical text signal | Take 1 ranks the caption first at 1.790, but scores the task card and evidence card at **0.000**, tied with empty noise. Take 2 ranks a false positive first and scores the large, obvious gibberish caption at **0.000** |

Pillow is not the limitation, and this is worth being precise about: it supplies
erosion and dilation through `MinFilter`/`MaxFilter`, thresholding through `point()`,
gradients through `FIND_EDGES`, and connected-component labelling is a short pure-Python
flood fill that runs in under a second on a downsampled panel. All three detectors above
were built with it.

What fails is discrimination, and the reason is specific to this book.
[`global-style.md`](../prompts/global-style.md) asks for crosshatching, dry-brush
abrasion, restrained halftone, and louvered industrial machinery. At the pixel level
that is the same object as text: dark thin marks of similar size arranged in rows. No
classical feature separates invented lettering from a stack of rack louvers in this
register.

**A larger raster stack would not have fixed it.** NumPy and SciPy offer faster
convolutions and `ndimage.label`, which is what the pure-Python flood fill already
does; OpenCV adds MSER and contour analysis, which degrade badly on stylised text over
texture. None of them supply a new signal. Do not spend the dependency.

What would work is a vision model. Asking a hosted model for bounding boxes of any text
in a panel is one API call at well under a cent, so under $10 for the whole book
including re-rolls, and it is a far better detector than anything classical. Note what
it changes, though: it makes detection a **quality gate**, not a patching input. Knowing
a panel has glyphs on a cabinet is enough to reject and re-roll it — 78 seconds locally.
It is not enough to composite a perspective-matched patch automatically. That part stays
hard.

This result is tied to this art style and this model. Re-test it if either changes; the
experiment is three short Pillow scripts and about an hour.

### Page furniture resists prompting too, and it is not just text

Tested 3 September 2026 on FLUX.2 [klein] 4B at four steps.

The first production render of panel 001-02 — a close-up of one diagram — came back as
a **three-panel comic page** with gutters, a speech balloon, a human figure in a register
that forbids figures, and a page number. The cause was in the prompt: only
`prompts/pages/001/panel-01.md` says "panel", so the other 540 panels compose from script
`Frame` text that describes content while the style prompt says "comic". That is now fixed
in [`global-style.md`](../prompts/global-style.md), which asks for exactly one panel filling
the image, and in [`negative-prompt.md`](../prompts/negative-prompt.md).

The fix helped and did not finish the job. The re-render was one scene rather than three,
but still carried a drawn panel border, a page number, balloon-shaped callouts, and a
gutter cut-out. Two rounds of prompt change each reduced the artefacts without eliminating
them, which is the same shape as the text problem and should be treated the same way:
prompting moves the rate, not the floor.

One cheap remedy is worth testing before more prompt iteration. Borders, torn paper edges,
and page numbers all live at the **margins**. Generating a few percent larger and cropping a
fixed inset would remove them deterministically, with no detection required — the same trick
as blanking, applied to the frame rather than a field. It costs pixels, not judgement.

### The prohibition was removed, and it reverses the model choice

**Decided 3 September 2026.** The book no longer forbids the model rendering readable
text. Display strings in the page scripts are project-authored — `exact-text-permissions-audit.md`
records that distributed pages paraphrase rather than quote, and only page 112 declares
any `exact_strings`, both of them the project's own — so there was never a reuse question
about drawing them. The prohibition was a production convention, and it was costing more
than it bought.

What replaced it:

- The prompt now names **two text systems**. In-scene text — what a screen, card, or label
  physically shows — is drawn by the model. Captions, dialogue balloons, and provenance
  slates are not: `lettering.md` specifies faces, reading hierarchy, contrast, and a web
  transcript that a generated approximation cannot satisfy, so those stay on the lettering
  layer and the corners stay clear for them.
- `imagegen.display_strings()` extracts the backticked literals from each panel's `Frame`
  and `Action` and hands the model an explicit list to spell correctly. All **291** strings
  across the book are captured, none wrongly filtered.
- The third-party constraint is unchanged: no source typography, credentials, tokens, URLs,
  commands, or exploit identifiers. Different constraint, different reason.
- The `text` rubric line inverted. It gated on *absence* of readable text, which now scores
  the wrong thing; it gates on the panel's own strings being legible and correctly spelled.

**This reverses the recommendation at the top of this document.** Text rendering was listed
as a liability, and the models that win text benchmarks were marked down for it. It is now a
requirement, and the ranking follows the benchmark rather than opposing it.

Measured on FLUX.2 [klein] 4B at four steps, against the 291 strings the book needs:

| String length | Count | Share | Observed |
| --- | ---: | ---: | --- |
| 1–8 chars | 70 | 24% | correct — `INPUT` rendered exactly |
| 9–15 | 97 | 33% | borderline |
| 16–25 | 49 | 17% | approximate |
| 26–40 | 43 | 15% | approximate, about one error per string |
| 41+ | 32 | 11% | not attempted |

The median string is 13 characters. Naming the exact words helped enormously — page 070's
header went from `BLIISED OPNN—NOT IN REVIEW` to `OPENIAI ACCOUNT — NOT IN METR'S REVIEW`,
one transposed letter in thirty-four — but a 4B model at four steps cannot spell reliably,
and it still letters surfaces it was told to leave blank.

So a local 16 GB pipeline can carry at most the quarter of the book whose strings are short.
The models built for this are Qwen-Image, whose text accuracy is its stated purpose and
which is Apache 2.0, and the hosted Gemini 3 Pro Image and GPT Image 2. Qwen-Image is 20B
and wants 48 GB, which this machine does not have. Either the drafting machine grows, or
text-bearing panels are rented; panels with no display strings can still be drawn locally.

### The settled plan

Items 1, 4, and 5 are built; item 3 is proposed in
[`lettering-slots.md`](lettering-slots.md) and awaiting approval; item 2 waits on it.

1. **Prompt for quiet dark areas, not reserved caption fields.** Blanking beats matching.
   *Done* — [`global-style.md`](../prompts/global-style.md) now asks for quiet near-empty
   corners and unlit in-scene screens, and [`negative-prompt.md`](../prompts/negative-prompt.md)
   names the shapes that invite glyphs: drawn caption box, label plate, signage, lettered
   screen, headed card. This turned out to be load-bearing rather than cosmetic: on the first
   real test the convention-placed caption covered (48,32)–(456,131) while the generated box
   occupied (44,34)–(288,146), leaving a 15-pixel band of invented lettering along the bottom
   edge. An overlay only hides what it is larger than, and nothing can tell it how big a box
   the model drew. The fix is art with no box in it.
2. **Machine text moves to the caption plane**, as interface-derived blocks above the
   art rather than screens inside it. The page-script template gains a marker for the
   panels that genuinely need in-world text.
3. **Lettering placement is convention-driven**, from named safe-area slots keyed to
   panel geometry. *Proposed* in [`lettering-slots.md`](lettering-slots.md), with the
   geometry in [`../data/lettering-slots.json`](../data/lettering-slots.json). It places
   **441 of 511 elements — 86.3%** — automatically, and nothing overflows its slot at a
   readable size. The 70 it does not place are dialogue balloons across 62 panels: a
   balloon needs a speaker position, which no convention can derive from a script.
4. **Compositing is automated at build time.** *Done* — `scripts/letterpress.py`
   shares one layout pass between two emitters. SVG keeps the viewer dependency-free;
   `--flatten` rasterises with Pillow, imported lazily so the repository still runs
   without it. `scripts/build-site.py` letters every panel that has art in
   `assets/art/panels/`, and is inert until artwork arrives.
5. **In-world glyphs are a reject condition, not a patch.** *Done* — `text` and
   `continuity` now gate rather than weigh in `scripts/imagegen.py rank`: scoring below 3
   on either disqualifies a candidate at any price. A re-roll costs 78 seconds locally.
   Hand-patching one panel costs more, and hand-patching 541 is a project.
6. **Optionally, a vision-model gate** decides what gets rejected.

### Panel size, measured

Both sizes were run on the drafting Mac (M1 Pro, 16 GB) with FLUX.2 [klein] 4B at 4-bit:

| Panel | At 300 dpi | Peak memory | Per image | 541 panels |
| --- | --- | ---: | ---: | ---: |
| 1200×800 | 4″ × 2.67″ | 11.53 GB | 64 s | ~9.6 h |
| 1800×1200 | 6″ × 4″ | **18.22 GB** | 147 s | ~22 h |

At 1800×1200 the model exceeds the machine's physical memory and completes only by
swapping, which is why it takes 2.2× as long rather than the 2.25× more pixels would
suggest. It works, but a 22-hour sustained swapping run is not something to start
casually on a 16 GB machine.

Both rows are uncropped renders. In production `--bleed 0.10` renders 1328×896 and
crops to 1200×800, which costs 78 seconds rather than 64; the surcharge is in the
throughput table above.

`scripts/produce.py` takes `--width` and `--height`, so this is a run-time choice
rather than a fixed one. The default is 1200×800. If the book needs 6″ panels, that
is an argument for renting the render rather than buying more hours: the same 541
panels through FLUX.2 [pro] on OpenRouter cost about $16 and finish overnight.

Still open: the trim size. At 1200×800 a panel is 4″×2.67″ at
300 dpi, which is small for print. If panels must be generated larger that changes both
the model choice — klein 4B already peaked at 11.53 GB on a 16 GB machine — and every
type size in the lettering layer. Settle the trim spec before building the compositor.

## Scoring

Score each candidate 1–5 per column in the run's `scores.tsv`, then run
`python3 scripts/imagegen.py rank`. The weights encode what actually blocks the book:

| Column | Weight | Question |
| --- | ---: | --- |
| `ink` | 3 | Hand-inked contour, dry-brush abrasion, heavy blacks, paper grain |
| `palette` | 2 | Stays inside [`palette.md`](palette.md); no unearned moss, claret, or amber |
| `text` | 3 | The panel's own display strings are legible and correctly spelled, with no invented lettering anywhere else |
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
