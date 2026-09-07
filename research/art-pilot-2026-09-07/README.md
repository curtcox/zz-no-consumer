# Artwork pilot — 7 September 2026

**Result: continue with small reviewed batches; do not start an unattended full-book run.** Eight built-in image-tool calls across six slots produced four provisionally selected renders. Four attempts were rejected. Two office slots retain their controlled boards. A seventh slot, 003-05, is a deterministic long-text control. No asset was marked final.

Open [the comparison sheet](index.html) for source boards, prior selections, selected lettered results, every attempt, and neighboring reader pages. Serve the repository root locally so the sheet can resolve its linked assets and the built reader.

## Decisions

| Slot | Decision | Evidence and remaining limitation |
| --- | --- | --- |
| 001-01 | Select v07 | Rack placement, dark separation and exact handle survive. Widened the controlled caption box after browser text bounds revealed overflow that the audit missed. Handle remains below the two task blocks; refine header hierarchy before final art. |
| 013-01 | Select v06, a controlled SVG wrapper over generated v05 | Initial v04 introduced pseudo-writing. Targeted edit v05 removed it while preserving the office and obscured face. Added a deterministic broken reconstruction border, which the lettering emitter does not automatically supply. Screens convey layout, not source prose; still a provisional reference. |
| 013-04 | Retain storyboard v02; reject generated v03 | Printer-paper pseudo-writing and small UI/hardware marks persist despite instructions. |
| 013-05 | Retain storyboard v02; reject generated v03 | Laptop moves from center to right; pseudo-writing persists. Plausible hands alone do not establish continuity. |
| 026-04 | Select generated v05 | Three headings spelled correctly, cards lie on table, responders stay peripheral, caption clears subjects. Repaired the board's seated figures before generation. |
| 026-05 | Select generated v07; reject generated v06 | Initial close-up changed landscape cards into portrait sheets. Targeted edit restores wide cards and leaves STOP RUN? unanswered. Repaired the board's one-card shorthand to show all three evidence cards before generation. Exact prop dimensions still need final reference-sheet review. |
| 003-05 | Select storyboard v02 as control | Both long editorial-summary strings remain on the controlled lettering layer. No image call was spent on this graphic. This is not a test of model-generated long text. |

## Method and reproducibility

- Built-in `image_gen.imagegen`, with one call per asset/variant. This pilot did not use the local production runner and does not benchmark local throughput.
- Composition PNGs were rendered from saved clean SVG boards with installed `rsvg-convert -w 1200 -h 800`. Input source snapshots are in [inputs.json](inputs.json); exported boards and raster references are in `references/`. These are dated experiment inputs, not new canonical scene records.
- All eight exact generated PNGs are preserved in the immutable panel store at 1536×1024. [run.json](run.json) records exact prompts, references, SHA-256 hashes, output paths, dimensions, and observed call durations. Each stored output has a matching JSON sidecar. [prompts.json](prompts.json) holds the initial prompt set; the authoritative exact prompt for each executed call is in run.json, including additional constraints and the two edit prompts.
- The tool did not expose model revision, seed, sampler, edit strength, or billing. Those values are explicitly unavailable. No API key, model download, training, or local model run was involved. The tool-managed generation log was not manually edited.
- Close-ups used the first rendered room as a second reference. This transmitted useful style and also unwanted markings. Only a reviewed reference should seed a larger batch.
- Reconstruction border composition is a separate SVG operation, not a ninth model call. The original corrected PNG is unchanged; its hash is recorded beside the wrapper.
- The pilot uses the existing 3:2 reader ratio. 1536×1024 supports 5.12×3.41 inches at 300 dpi, before any cropping. This does not settle book trim, final panel shapes, stock, or physical proof approval.

## Measured effort

Eight successful tool calls consumed **598.3 seconds summed elapsed call time** (35.6–131.2 seconds each). Calls ran in three dependency groups with independent calls overlapping, so this is not total session wall time. Dividing by four selected renders gives **149.6 seconds of call time per selected panel**, including failed attempts. It excludes preparation, visual review, importing, controlled composition, building, and checks. This small heterogeneous sample is not a forecast for the whole book.

## What the pilot changes about the next run

1. Use reviewed room/prop references, not merely the first attractive render. Record laptop position, monitor proportions, card orientation, lighting and negative space explicitly.
2. Generate short labels selectively; retain controlled rendering for long prose, diagrams, provenance, captions and dialogue.
3. Review the actual lettered browser output. The mechanical audit checks its own font estimates, not browser glyph bounds; the opening caption passed that audit while overrunning its box. The pilot repairs that slot only, not the global measurement discrepancy.
4. Apply reconstruction borders as controlled production geometry. The current lettering emitter does not automatically reapply the storyboard's border to a raster candidate. The pilot supplies one explicit wrapper; a reusable production policy remains work.
5. Resolve trim and final panel geometry before scaling resolution or volume. Do a physical proof, especially of dark equipment separation and small in-scene labels.
6. Repeat the office close-ups against the corrected office reference in a subsequent small run. Do not accept them based on palette or anatomy alone.

Facing-pair inspection also shows older neighboring raster candidates with different office geography, appearance and text treatment. The pilot does not approve those earlier candidates or establish whole-page continuity; curate those neighbors before locking the sequence.

No training set or all-book reference library was approved here. The selected office can support another experiment, but its screen layouts and final source treatment remain provisional. All previous artwork and all failed attempts remain available; selection is reversible through panelart.py.

## Validation

Before edits, storyboard coverage/built checks and the lettering audit passed. After changes, all 21 validation/build commands and both unittest modules passed. The appendix checker retained 31 informational notes, with zero errors or warnings. Browser review found no horizontal lettering overflow in the seven selected pilot/control panels, and all 50 comparison/sequence images loaded. Inspect the final check log in [validation.txt](validation.txt). The comparison sheet also supports browser checks of lettered SVG text bounds and image loading. Generated docs are rebuilt through the site builder; no docs files are hand-edited. No commit, push, or deployment is part of this pilot.
