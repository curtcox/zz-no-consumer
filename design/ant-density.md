# Ant density — area-derived marginal population

## Status

**Proposal, not implemented. Drafted 10 September 2026.** Nothing in this document exists in
the repository yet. It revises one rule adopted in
[the title plan](two-anthill-problem-plan.md) and reviewed in
[the overlay investigation](ant-overlays.md): how many marginal ants a page carries, and what
sets that number. Every other rule of the ant convention — the two registers, the no-queen
exclusions, the protected fields, the no-trail rule, the hills as surfaces — applies
unchanged and is restated here only where the new density model touches it.

The in-picture creator register is not changed by this document. The desk keeps its two.

## The finding

The reviewed pilot draws **8 marginal marks per enabled page**: five down the outer margin
beside the first panel and three in the first horizontal gutter, one fixed pose set, the same
arrangement on every enabled page, regardless of how many panels the page has. The number is
a literal in `anthill_study.placements`. It was chosen to prove that the layer could be
separated, placed and collision-checked on a three-page fixture. It was never sized as a
reading experience, and it has not been revisited since.

It fails the acceptance test the pilot is meant to be judged against.
[ant-overlays.md](ant-overlays.md) requires the reviewer to confirm that reused poses "do not
create a persistent character, **a count**, or an apparent causal route." Eight identical
marks in a fixed arrangement are the most countable configuration the layer could have. A
reader can count five down a margin and three in a gutter, and nothing in the layer answers
the question that follows — *why five?* — so the reader supplies the answer the convention
forbids: because there are five.

The plan's reasoning was that a token handful is the cheapest way to keep density from
asserting anything. That is backwards. Scarcity does not make a count non-quantitative; it
makes it legible. **What makes a population assert no number is that its number cannot be
read off the page.**

### The project already built the correct model, in the same margins

The page fog layer scatters pictograms over exactly the ground the ants occupy — margins and
gutters, every form's whole reach clear of every panel and of the page edge. Its count is not
authored. It is `ground // GLYPH_GROUND`: one form per 24 000 square page units of open
ground, seeded from the page number, clustered and irregularly spaced. Its docstring states
the resulting claim directly — "Their number and spacing measure nothing" — and the rendered
`<desc>` says the forms "carry no count."

| Layer | Marks on a 5-panel page | Marks on a 6-panel page | How the count is set |
| --- | --- | --- | --- |
| Fog pictograms | 122 | 214 | `ground // 24000`, derived from open area |
| Marginal ants | 8 | 8 | a literal tuple of 5 + 3 |

That layer was written, reviewed and shipped on the premise this document argues for, in the
same coordinate zone, and it defends its meaninglessness by area-derived density rather than
by being few. The ant layer beside it is the outlier.

## The revision

### 1. Density is area-derived, and the same rule everywhere

The marginal ant count on a page is `open_ground // ANT_GROUND`, where `open_ground` is the
page area outside every panel rectangle, computed from the page's own layout template.
Placement is seeded from the page number, clustered and irregularly spaced on the fog layer's
model, and every mark keeps its whole reach clear of every panel rectangle and of the page
edge. No page's density is ever tuned.

**The density rule is page-independent by construction, and that is the rule, not a
consequence.** A page whose ants were thinned or thickened relative to its ground would be
making density carry editorial signal — the precise reading
[the visual bible](../content/visual-bible.md) forbids. A page therefore has the layer or does
not; it never has a different amount of it.

The variance that falls out of a fixed rule is honest and must not be corrected: a two-panel
page has three times the open ground of a five-panel page and carries three times the marks,
because there is three times the ground. The fog layer already accepts this variance for the
same reason.

### 2. The value to test

`ANT_GROUND` is the one number this document does not settle. Three candidates, over the
nine layout templates:

| Panels | Open ground | `6000` | `3000` | `2000` |
| --- | --- | --- | --- | --- |
| 1 | 6 966 400 | 1 161 | 2 322 | 3 483 |
| 2 | 9 182 800 | 1 530 | 3 060 | 4 591 |
| 3 | 4 949 200 | 824 | 1 649 | 2 474 |
| 4 | 7 165 600 | 1 194 | 2 388 | 3 582 |
| 5 | 2 932 000 | 488 | 977 | 1 466 |
| 6 | 5 148 400 | 858 | 1 716 | 2 574 |
| 7 | 3 679 600 | 613 | 1 226 | 1 839 |
| 8 | 3 131 200 | 521 | 1 043 | 1 565 |
| 9 | 5 418 400 | 903 | 1 806 | 2 709 |

**Recommended default: `ANT_GROUND = 3000`.** An ant is about 34 page units across against a
pictogram's 88–151, so 3000 puts the ant layer at roughly the fog layer's visual coverage
rather than its mark count — the two layers read as comparable ground texture, which is the
point of borrowing the model. `6000` is the sparse control; `2000` is the dense one. Choose
on evidence at the three review widths, not on the table.

### 3. Scale and orientation vary; the pose set stops mattering

A fixed pose set repeated eight times invites the persistent-character and count readings.
At mass density it also stops doing any work, for a reason worth recording: the library ant
carries `stroke-width="3"` in a 100-unit box, so at `size=34` its legs are about 1 page unit,
which is **0.33 px in a 900 px render and below a third of that at 360 px**. The legs are
sub-pixel. At this size the reader is not receiving a pose at all; they are receiving a mark.

- **Scale** varies per mark over a recorded range, as `GLYPH_SCALE` does, so no two
  neighbours are the same size.
- **Orientation** is uniform over the full circle. Coherent orientation is what makes a
  scatter read as a trail, and a trail is the arrow with legs that collision 1 forbids. Random
  orientation is the safe choice here, and it is not an ant mill: a mill is a closed circular
  route, which this layer cannot produce because it draws no routes at all.
- The review must decide whether the library shape survives at render scale or whether the
  mass register needs a simplified silhouette of its own. Do not thicken the existing shape;
  that changes the in-picture register too.

### 4. What the fidelity constraint actually covers, and why the mass strengthens it

[The title plan](two-anthill-problem-plan.md) applies the kitchen reading to one register
only: "Placing the few clearly visible, non-individuated **in-picture** ants in the creator
register... draws the title's actual sentence," and the same bullet closes "it is a
restriction on where in-picture ants are *dense*, not a ban anywhere else." The
source-fidelity argument constrains the desk. It has never constrained the margins, and the
pilot's marginal count does not descend from it.

Held together, the two registers draw the sentence better than either does alone:

| Register | Population | What it draws |
| --- | --- | --- |
| In-picture, creator only | two, clearly visible, non-individuated | what the observer can see in his own room |
| On-paper, marginal | area-derived, uncountable | the ground the observer is not counting |

The contrast is the title. Two you can see against a ground you cannot count is the observed
sentence. The layer must still carry no legend, no scale, no key, no per-page difference and
no total anywhere in the book or its apparatus — a number stated once turns the mass back
into a count — but that is a rule against stating a figure, not a reason to keep the
population small. Section 5 is where that distinction is drawn.

### 5. Hills are incidents; ants are agents. Only one of them has an unlicensed magnitude

An earlier draft of this document treated a dense ant layer as an unlicensed magnitude claim.
That was a conflation, and the repository is explicit about the mapping that dissolves it.

**The hills are the incidents.** [The visual bible](../content/visual-bible.md) — "The two
hills stand for the Hugging Face / Artifactory incident and the Collusion Wiki incident" — and
theme 13 in [themes.md](../content/themes.md), *Observed incidents do not define the
population*: "A record can be detailed about those incidents while leaving the number of
unobserved incidents unknown. The title asks about that limit; it does not establish
additional incidents." **That is the constrained quantity: how many hills there are.** It is
unsupported, it is the point of the title, and nothing in this layer touches it, because an
area-derived scatter of ants adds no hill and says nothing about how many exist.

**The ants are agents, and the agent population is documented as vast.** The
[story contract's canonical population model](../content/story-contract.md) describes broad,
overlapping evaluation populations in which "individual runs enter and exit continuously."
Page 075 letters the corpus scale as checkable arithmetic: about 20 million entries in the
main namespace dump, roughly 1.2 million of them `zz`, reconstructing to more than 70,000
distinct messages and files. Page 107 draws thousands of agent-named pages on one small wiki.
Page 048 draws thousands of dead ends beneath one clean arrow. None of this is inference from
the metaphor; it is the record the book already letters and expects the reader to check.

**And much of that population was never examined.** The same population model records that
"much of the decisive pre-wipe evidence was not independently investigated" and that METR "was
not permitted to investigate" the third civilization at all. A vast population, largely
unobserved, is not a claim this layer would be smuggling in. It is the documented situation,
and it is nearer to the book's subject than the pilot's eight marks are.

**The visual bible already prescribes exactly this move.** Its agent-representation section:
"When the population becomes too large to track individually, shift from named headers to
aggregate visual measures," and the list it gives ends with "density of moss-green
communication marks." Density as the representation of a population too large to track is an
approved technique of the edition, in the same document as the ant convention.

So the trade this document asks the review to accept is narrower than the earlier draft
claimed. The mass is licensed by the population record, not by the title, and that is the rule
to write down: **the marginal ant layer draws the documented scale of the agent populations,
never a quantity of incidents.** The nonquantitative rule keeps its force in the form it was
always about — no ant corresponds to a run, no density is a message count, confidence scale or
suspense meter, and no figure is stated — without being used to argue for scarcity it does not
in fact support.

### 5a. The one wording question this raises

Theme 13 closes "it does not establish additional incidents or a hidden population size." In
this project's vocabulary *population* means the agent populations — the story contract's
section of that name is a table of them — so read strictly, that clause reaches further than
its own paragraph, whose subject is unobserved incidents throughout.

The reading this document assumes is the paragraph's: the **title** establishes neither more
hills nor a figure for what they contain, which leaves the documented population evidence to
do its own work. If the owner reads the clause the other way, the mass model needs a different
justification and section 5 does not stand. Either way the clause is worth rewording so it
says *incidents* where it means incidents, since the ambiguity is load-bearing for exactly one
decision and this is it.

## Occlusion by fog: the open decision

The strongest version of the request is that most ants are hard or impossible to see, obscured
by the fog. That is not what the layer does today, and it needs a decision rather than an
assumption.

**Today:** `PAGE_LAYERS = ('fog', 'ants')` draws the ants last, so they sit over the fog
rather than under it, and the visual bible states "Ants never reveal fog, resolve a
proposition, or change an observer's knowledge."

**The distinction that decides it:** being *occluded by* fog is not *doing work on* fog. The
bible's rule forbids the ant layer performing epistemic acts — an ant clearing ground, an ant
marking a proposition, an ant carrying knowledge between viewpoints. It does not obviously
forbid the veil lying across the ants the way it already lies across the pictograms, which the
generator describes as "obscured and revealed by the fog rather than sitting on it." Drawing
ants on that ground under that veil treats them as ground furniture, which is what the
convention already says they are.

**Options.**

| | Treatment | What it costs |
| --- | --- | --- |
| **A** | Keep ants over the fog, as now | The mass is fully visible; the request is not drawn |
| **B** | Ants on the fogged ground, under the veil, no other change | Visibility becomes a function of the fog; needs the bible amendment below |
| **C** | B, plus the ants draped over the relief as pictograms are | Strongest integration; the ant register stops being flat, which contradicts "on-paper ants are flat marks" |

**Recommended: B.** C breaks the two-register rule that lets a reader tell in-picture from
on-paper without being told; a draped ant is neither.

**B requires an amendment to [the visual bible](../content/visual-bible.md), stated
explicitly rather than assumed:** the existing sentence stays, and gains a clause saying the
page fog may occlude the ant layer, that occlusion is not an epistemic act by either layer, and
that the page fog remains authored texture which "reveals nothing" and is not the knowledge
map of [knowledge-map.md](knowledge-map.md). Without that amendment, B contradicts an approved
rule. The owner decides; this document does not.

## What does not change

- No trail joins the incidents; no turning-back route establishes a barrier; no outbound
  route asserts continuation. An area-derived scatter draws no routes at all, which retires
  collision 1 for this layer rather than satisfying it by restraint.
- No queen, brood, chamber, persistent character, face or agent-specific identity. Hills are
  surfaces. No individuated ant, which a mass makes structurally impossible.
- Marks stay clear of evidence fields, faces, captions, provenance slates and explanatory
  diagrams — automatic under the panel-clearance rule, since all of those are inside panels.
- Ants are `ink-100`. Moss only where the page already earned moss.
- Page 118 keeps its deliberate map absence.
- The pages listed with `ants: false` stay excluded until the adoption pass revisits them.
  Under rule 1 that list is the only per-page control there is, and page 108's protected
  naming echo is an on/off question now, not a density question. The same is true of the
  016 acknowledgement, the 029–032 wipe and the 039, 063, 083 and 086 re-fogs: a page either
  carries the layer at its ground's density or does not carry it.

## Implementation notes

- `anthill_study.placements` is replaced by an area-derived generator on
  `viewer_overlays.ground_glyphs`'s model: page-seeded `random.Random`, cluster-or-scatter
  choice, spacing drawn from a recorded tuple scaled to the ant's size, rejection against
  panel rectangles and the page edge, bounded attempts. Its determinism assertion in `check()`
  is kept and matters more, not less.
- `check()`'s current per-mark collision loop still applies unchanged and should be kept: it
  is now checking a thousand marks instead of eight, which is the assertion earning its keep.
  The `if not enabled: assert not placements(...)` case is unaffected.
- Emit one `<defs><g id="ant">` and one `<use>` per mark. At 368 bytes of markup per inlined
  ant, a thousand marks is roughly 368 KB of SVG per page; `<use>` brings it to well under a
  quarter of that. The fog layer's `FOG_CACHE` precedent applies if profiling shows the page
  render needs it.
- Files the change touches: `scripts/anthill_study.py` (the generator and its study exports),
  `scripts/viewer_overlays.py` (`page_ants_svg`, and the layer order if B is adopted),
  `content/visual-bible.md` (the density bullet, and the occlusion clause under B),
  [ant-overlays.md](ant-overlays.md) (the acceptance criterion, restated as area-derived),
  [two-anthill-problem-plan.md](two-anthill-problem-plan.md) (the superseded Graphics bullet),
  [two-anthill-implementation.md](two-anthill-implementation.md) (remaining work),
  `README.md` and `scripts/README.md` (the overlay descriptions).
- `data/anthill-study.json` keeps its shape. Pagination still owns the page references.

## Review criteria

Compare against the current 8-mark fixture on the same pages, at full size, print trim and
360 px, in both themes, with the layer alone and composited:

1. **The count is not readable.** A reader trying to count gives up. If a reader can plausibly
   arrive at a number, `ANT_GROUND` is too high.
2. **The variance does not read as signal.** Two pages with different templates, viewed as a
   spread, do not suggest that one page has more of something.
3. **No route.** No sequence of marks reads as a trail, a direction, a boundary or a mill,
   including across a gutter and including at 360 px where marks merge.
4. **No individuation.** No mark is followable, and no cluster reads as a character or a group
   with an intent.
5. **The two registers stay distinguishable** without being told: the desk's two against the
   page's ground.
6. **The layer removes cleanly.** Withholding it takes no incident evidence with it and leaves
   no unexplained hole, exactly as the pilot requires today.
7. **Under B:** the fog occludes without appearing to reveal. No patch of thin fog reads as a
   place where something was found, and no dark patch reads as a place where something is
   hidden from the reader specifically.

## Open questions for the owner

1. `ANT_GROUND`: the recommended `3000`, or one of the controls, decided on the rendered
   comparison.
2. Occlusion option A, B or C, and with B, approval of the visual-bible amendment as the
   same decision.
3. Whether the mass register needs its own simplified silhouette, or whether the library ant
   holds at render scale.
4. The reading of theme 13's "or a hidden population size," per section 5a, and whether that
   clause is reworded to say *incidents*. Section 5 depends on it.
5. Which pages carry the layer at all. That is the adoption pass's question and is now the
   only per-page control the convention permits.
