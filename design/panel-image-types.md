# Panel Image Types

The key for routing panels to generators. The classification of every panel is
[`../data/panel-types.tsv`](../data/panel-types.tsv), written by
`scripts/paneltypes.py` from the page scripts themselves. How many there are is a
measurement, not a constant: `python3 scripts/panels.py report` prints it.

## Why a key at all

No one model is best at everything this book needs. A dark aisle with no text wants
whatever is cheapest per image; a two-column source comparison carrying a
thirty-seven-character header wants a model that can spell; a panel showing Curt
cannot be drawn at all until an approved reference sheet exists. Sending every
panel to one generator means either paying premium rates for the plain scenes,
which are 41% of the book, or failing the 15% that need long strings spelled
correctly. `python3 scripts/paneltypes.py summary` prints the current shares.

Each panel gets a **type**, describing what the image is, and a **route**,
describing the capability a model must have to draw it. Types are many-to-one onto
routes, because several different-looking panels make the same demand.

## Types

Assigned in this order. The first that matches wins, because the order runs from
most binding demand to least: a dossier page carrying a long header is routed on the
header, since that is the part a model will fail.

| Type | What the description shows | Panels | Route |
| --- | --- | ---: | --- |
| `portrait` | A named recurring individual, in practice Curt, or any figure in the creator register | 57 | `reference` |
| `text-heavy` | A display string over 15 characters, or more than 24 characters of display text in total | 78 | `text-fidelity` |
| `figure` | Anonymous or functional people — a responder, a chair, counsel, hands on a keyboard | 63 | `figures` |
| `dossier` | Paper structure dominates: columns, a page field, a grid, an archive, a persistent top strip | 29 | `structure` |
| `diagram` | An abstract diagram, boundary map, arrows, branches — geometry rather than a place | 43 | `structure` |
| `text-light` | A physical scene carrying only short display strings | 43 | `local` |
| `scene` | A physical environment with no people and no display text | 228 | `local` |

## Routes, and what each demands

| Route | Panels | The capability that decides it | Where it can go today |
| --- | ---: | --- | --- |
| `local` | 271 (50%) | None beyond the house style. Short strings need a spelling check, nothing more. | Any local model. FLUX.2 [klein] 4B on a 16 GB machine handles these. |
| `structure` | 72 (13%) | Clean geometry and flat fields; texture matters less than legible construction. | Cheapest tier. Several of these could be drawn rather than generated. |
| `text-fidelity` | 78 (14%) | Long strings spelled correctly. Measured: klein 4B is reliable to about 8 characters and unreliable past 15. | Qwen-Image (Apache 2.0, 20B, needs 48 GB) locally, or Gemini 3 Pro Image / GPT Image 2 hosted. |
| `figures` | 63 (12%) | Competent anatomy and hands, without identity continuity. | Mid tier. Worth a bake-off column of its own; hands are where cheap models fail. |
| `reference` | 57 (11%) | Multi-image reference conditioning, so the same person is the same person across 57 panels. | Gemini 3 Pro Image, whose reference conditioning is the strongest available. **Blocked**: `visual-continuity.md` forbids an identifiable portrait until an approved reference sheet exists, and `data/assets.yaml` still lists the sheets as `needed`. |

## What the mix buys

Just over half the book needs nothing a 16 GB laptop cannot do. The expensive
capabilities are concentrated: 78 panels need text fidelity and 57 need reference
conditioning, together a quarter of the book.

**Recounted 3 September 2026.** The person, dossier and diagram patterns matched only
singular forms, so "Three human investigators stand before the evidence field" read as
an empty scene. Twenty panels were retyped once the patterns allowed plurals — ten of
them from `scene` to `figure` — which is why local-route runs kept inventing people
into panels that were supposed to have none. Four words stay singular deliberately:
this book calls software `workers` and uses `chairs` as furniture, and `leads` and
`faces` are usually verbs.

At Gemini 3 Pro Image's batch rate, routing only the 135 panels that need premium
capability costs about **$54 at six attempts each**, against $263 for sending the
whole book there. The other 406 panels cost electricity.

That is the argument for the key: the premium models are worth their price on a
quarter of the book and wasted on the rest.

## Using it

```sh
python3 scripts/paneltypes.py summary            # counts by type and route
python3 scripts/paneltypes.py show --type text-heavy
python3 scripts/paneltypes.py write              # refresh the table
python3 scripts/produce.py run --type scene      # generate one type
python3 scripts/produce.py run --route local     # or one route
```

## Keeping it honest

The classification is derived from each panel's own `Frame` and `Action` text, its
display strings, and its page front matter. It is regenerated, not authored, so it
stays correct when the script changes — which also means hand-editing
`data/panel-types.tsv` is pointless. Fix a wrong call by sharpening a rule in
`scripts/paneltypes.py` and re-running `write`.

Two rules earned their complexity from being wrong first. Page scripts routinely say
"No face, avatar, or speech balloon", so a bare word match classified panels as the
very thing they exclude; matches inside a negated clause are now ignored. And `card`
was too broad for `dossier` — a `UI-TASK-CARD` inset into a dark aisle is a scene
with a card in it, not a dossier page — so only structure that dominates the panel
counts.

Both were caught by spot-checking known panels against the table. Any future rule
change deserves the same check before the table is trusted.
