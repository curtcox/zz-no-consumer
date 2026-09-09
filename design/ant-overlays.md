# Separate ant overlays — 9 September 2026

## Finding

Separate ant assets are a practical option. The existing SVG renderer and controlled
lettering layer already support image composition. Use algorithmic SVG for marginal marks;
test separately rendered ants for inside-picture use. Keep base art ant-free and immutable.
The ant convention in [the visual bible](../content/visual-bible.md#ants-and-anthills-edition-convention)
applies to the final composite regardless of how its layers were made.

This is a local architecture assessment and an offline composition experiment. No new model
image was generated, no provider was selected, and no ordinary reader artwork was replaced.

## Working prototype

Run `python3 scripts/anthill_study.py build` and open `256t/anthill-study/index.html`.
The site builder also publishes the study under `docs/anthill-study/`.
For each selected scene containing authored ant nodes, the study exports:

- `NNN-II-base.svg`: the same storyboard with ant nodes omitted.
- `NNN-II-ants.svg`: those ants with a transparent background and the same viewBox.
- `NNN-II-composite.svg`: base plus ant layer, with no new lettering.
- `NNN-II-lettered.svg`: controlled captions and dialogue applied last.

The assets come from `data/storyboard-assets.json`; placements come from the canonical
scene, not a second set of coordinates. `data/anthill-study.json` supplies page references
maintained by pagination. The prototype changes neither stored artwork nor scene records.
It rejects caption/display-label collisions and ant placements whose later foreground
nodes would require an occlusion mask. This is a deliberately bounded flat-geometry test;
its collision checks do not replace visual evidence-field review.

## Asset options

| Option | What it gives us | What still needs work |
| --- | --- | --- |
| Algorithmic SVG silhouettes | Deterministic geometry, true transparency, palette tokens, crisp scaling, editable placement; already working | Hand review of silhouette, apparent scale and repetition. Existing desk shapes are blocking, not a finished lighting treatment. |
| Model-created ant sprites | Potentially richer ink texture and scene-compatible anatomy, generated independently of expensive base art | Generate and review a small pose set; verify actual alpha rather than a painted checkerboard; inspect edges on light and dark backgrounds. Record tool, prompt, references, output hash and any unavailable settings. |
| Algorithmic placement of reviewed sprites | Reuse either asset type with exact scale, rotation, position and layer order | Explicit placement decisions and protected regions. Never derive density from message/run counts or route a trail between incidents. |
| Ants generated with the whole scene | Lighting and occlusion can emerge in one rendering | Moving or removing ants may require another scene generation; silhouettes can become identities or obscure evidence. Remains an option for a difficult physical interaction after comparison. |

For model assets, request an isolated ant in the book’s ink style and the intended view.
An opaque result would need a separately reviewed mask or another generation; do not assume
background removal preserves thin legs and antennae. Preserve the original and mask as
separate versioned inputs. A sprite’s shadow should also be separate when the same pose is
used on different surfaces. Mirroring changes light direction and should not be automatic.

## Proposed production path

1. Prepare an explicitly ant-free base prompt and ant-free reference. Merely adding “no
   ants” while retaining an ant-bearing direction or storyboard is an inconsistent handoff.
   Current generation prompts still honor canonical in-picture ant directions; the prototype
   does not silently change that production behavior.
2. Review and store the base through the existing artwork workflow. Record any crop before
   placement so the overlay and lettering use the final panel dimensions.
3. Choose a reviewed SVG or transparent raster ant asset. Record its content hash, normalized
   position, scale, rotation, register and intended surface in a versioned overlay manifest.
   Page/panel references in a future manifest must join both identity tools before adoption.
4. Compose base → contact shadow → ants → explicit foreground masks → controlled borders and
   lettering. Margin ants belong to page coordinates outside panel rectangles. In-picture
   ants belong to final cropped panel coordinates. Do not mix the two coordinate systems.
5. Save a new composite variant and receipt identifying base, sprite, mask, placement and
   renderer hashes. Preserve the ant-free original. Promote only after the normal visual
   review; base or geometry changes invalidate the composite.

The existing prototype reuses SVG image elements, which can also embed a raster base or
transparent sprite. It does not yet implement a production sprite registry, masking UI,
reader toggle, queue handoff mode or automatic composite promotion. Those belong after the
style comparison, rather than being prerequisites for reviewing this option.

## Acceptance comparison

Compare ant-free base, overlay alone, composite and lettered composite at full size, print
trim and 360 px. Inspect transparency on both paper and ink backgrounds. Confirm that:

- In-picture ants sit on the intended surface with plausible scale, perspective, contact
  and lighting; foreground edges hide them where appropriate.
- Marginal ants read as flat authored marks, and no marks cross evidence, lettering, faces,
  provenance or prohibited diagram fields.
- Reused poses do not create a persistent character, a count, or an apparent causal route.
- Removing the layer does not remove incident evidence or leave an unexplained hole in the
  base. The physical appearance still makes clear that this is authored interpretation.
- Exported SVG/raster composites match the reviewed layer order; no reader interaction is
  needed to understand the convention.

The next artistic comparison is an algorithmic ink sprite against a model-created sprite
on the same reviewed ant-free base. The present prototype establishes separation and
recomposition, not the superiority of either finished style.
