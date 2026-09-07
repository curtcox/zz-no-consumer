# Artwork pilot — 7 September 2026

## Restart follow-up

Two built-in image calls produced provisional selected v03 images for 032-02 and 032-04. Six separate fresh evaluation cards show distinct task symbols and budget gauges; three lanes access a clean packages-only listing. RUN A–F are generic editorial labels, not sourced agent handles. The first image omits the additional geometric identity markers requested in the prompt, but the distinct headers preserve separation. Neither panel contains moss or communication content. No manuscript or scene geometry changed.

Exact prompts, reference/output hashes, dimensions, elapsed times and unavailable tool controls are preserved in [restart-followup.json](restart-followup.json) and immutable sidecars. Complete storyboard validation passed before generation. The site was rebuilt and the image-generation census refreshed. Complete built storyboard validation, lettering audit, viewer validation, built page-link validation and census check passed. Both lettered SVGs were rasterized and visually inspected: captions fit and clear the subjects. These selections remain provisional; dark texture and small gauges still need print-size proof.

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

## Office follow-up after pilot push

Pilot commit `a325c14e` was pushed to origin/main at the user’s request. A rechecked unowned empty index lock (inode 62683596) was removed under the repository recovery procedure before staging; its creator remains unknown. Automatic push review initially described the repository as private; GitHub inspection established the configured destination is public and the account has ADMIN permission, after which the push succeeded.

Two additional built-in image calls used corrected office v05 as the first reference and the original close-up boards as rough framing guidance. Both preserve the centered laptop, left lamp, right drink, abstract source blocks and empty conversation field. The generated PNGs are v04 in 013-04 and 013-05; selected v05 variants wrap those unchanged images with controlled broken reconstruction borders. No final-stage promotion. Tiny material/keyboard details still require trim-size proof.

Exact executed prompts, reference hashes, dimensions and timing are in [office-followup.json](office-followup.json). The initial pilot table and metrics above remain a dated record; its two retained-board decisions are superseded by this follow-up. The comparison sheet now displays the current choices, with the new pair at the top. Older neighboring images remain outside this batch. This follow-up has not been committed or pushed.

## Office sequence continuation

Three further built-in image-tool calls produced reaction and scrolling panels for 013-02 and 013-03. The first scrolling attempt omitted the separate keyboard and was rejected; a targeted edit restored it. Selected versions are 013-02 v07 and 013-03 v04, each an immutable SVG border wrapper around an unchanged PNG. The creator face is an invented provisional depiction, not an approved likeness. The branching infrastructure is an unlabeled visual abstraction, not a source screenshot. No asset was marked final.

Exact prompts, reference/output hashes, dimensions, elapsed call times and saved paths are in [office-sequence.json](office-sequence.json). Original outputs and the rejected attempt remain in the panel store.

Before this continuation, the full local CI sequence passed, including both unittest modules; the appendix retained 31 informational notes and no errors or warnings. The requested commit was blocked by index.lock (observed inode 62706428, empty): host inspection found no Git process or open handle, but automatic approval review rejected removal under the repository lock rule. Explicit user approval was requested. No commit or push has occurred in this continuation.

## Opening sequence follow-up

Two further built-in image calls corrected the task-card hierarchy in 001-01 and generated the evaluation-card close-up in 002-02. Selected provisional versions are 001-01 v09 and 002-02 v04. The first keeps the aisle composition and moves the exact handle above both task blocks. The second crosses out the required method and leaves the success field empty. Its FLAG label remains on the controlled lettering layer. Neither image is final; the adjacent diagrams and other earlier selections are outside this batch.

Exact prompts, output and reference hashes, dimensions, tool limitations, and saved paths are in [opening-followup.json](opening-followup.json) and immutable image sidecars. Both generated images are 1536×1024 PNGs. The first call's elapsed time is rounded from tool timing; the second is measured around the call. Previous versions remain available.

The complete storyboard check passed before changes. After import and selection, the site build, complete built storyboard check, lettering audit, viewer validator, and built page-link check passed. Rasterized lettered outputs were visually inspected: captions clear both task cards, the corrected header remains legible, and the success field remains empty. No manuscript, scene geometry, commit, push, or deployment changes were made in this batch.

## Institutional sequence continuation

The opening follow-up was subsequently committed as `091152e2` and pushed to origin/main at the user's request. An empty index lock (inode `62751244`) blocked staging. Fresh host-level process and open-handle checks found no Git process or owner; the same inode, size and precise modification time were checked immediately before removal. Staging, commit and push then succeeded. The lock creator remains unknown.

Two further built-in image calls generated 026-01 v05 and 026-02 v05, both provisionally selected at refined stage. The first restores the scripted anonymous responder tracing workload identification through the scheduler to ExploitGym. The second shows abstract request history beside note objects, with moss confined to the communication objects. Both use 026-04 v05 as the institutional style reference. Blank fields and bars are deliberate abstractions, not reproduced source interfaces. No final approval or whole-page continuity approval is implied; 026-03 remains outside this batch.

Exact prompts, reference hashes, dimensions, output hashes, elapsed call times and tool limitations are preserved in [institution-followup.json](institution-followup.json) and each immutable PNG's JSON sidecar. Both outputs are 1536×1024. Previous candidates remain available.

The complete storyboard check passed before generation. The rebuilt site's complete storyboard check, lettering audit, viewer validation and built page-link check passed afterwards. Rasterized lettered versions were inspected: both captions fit and leave all labels, identification connections and note objects unobscured. Manuscript and scene geometry were unchanged. These two new institutional images and their regenerated reader outputs remain uncommitted.

## Decision sequence continuation

The institutional batch was subsequently committed and pushed as `ea22fce2`; the Git investigation followed as `0586e76b`. At the start of this continuation the working tree was clean and origin/main was already up to date.

Two built-in image calls generated 027-01 v04 and 027-03 v03. Selected provisional variants are 027-01 v05 and 027-03 v04, controlled SVG reconstruction borders around those unchanged PNGs. The first keeps the same two anonymous responders, clothing, table and three landscape evidence cards, with a restrained explanatory gesture and clear dialogue space. The second enlarges the unanswered STOP RUN? field, with three peripheral hands and two blank device screens. A hand overlaps the paper's lower edge, but the heading and large empty decision field remain unobscured. No motive or answer was added. The earlier image in 027-02 and the remaining sequence are outside this batch.

Exact prompts, reference hashes, timing, tool limitations and output paths are saved in [decision-followup.json](decision-followup.json) and immutable image sidecars. Both generated PNGs are 1536×1024. The reconstruction border is controlled geometry, not an additional model call. Nothing was marked final.

The complete storyboard check passed before generation. After import, the site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed. Both lettered outputs were rasterized and visually inspected for border treatment, labels, anatomy and dialogue clearance. The explicit Git metadata refresh completed with only the expected edited-file notices; no index lock recovery was needed. This new decision batch remains uncommitted.

## Decision sequence completion pass

The preceding decision batch was committed and pushed as `6932de1e`, without lock recovery. Three further built-in image calls covered the remaining evidence close-up and return to the data center. The first 027-02 render changed the message-board card to portrait and is preserved as rejected v03. A targeted edit restored its landscape shape (v04); selected v05 adds the controlled broken reconstruction border. The abstract pivot diagram adds no named destinations or reusable mechanism. Selected 027-05 v03 shows active evaluation racks beside an explicitly staged, dormant plugin symbol, separated by the source-boundary line already specified in the board.

Exact prompts, reference/output hashes, dimensions, timings and limitations are in [decision-completion.json](decision-completion.json) and immutable sidecars. All three outputs are 1536×1024 PNGs. The decision-log slot 027-04 remains the controlled v02 storyboard; no model-generated decision wording was needed. The page now combines four provisional generated selections with that controlled graphic. This is not final art approval.

Before generation, complete storyboard validation passed. After selection, the site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed. Both new lettered views were rasterized and inspected: the two dialogue boxes clear the evidence props, the closing caption clears the staged plugin, and no execution effect was introduced. No script or scene geometry changed. This completion pass remains uncommitted.

## Outage sequence follow-up

The decision completion batch was committed and pushed as `683fd404`. Three built-in image calls produced selected 028-01 v03 and 028-04 v05. The execution panel preserves the sealed plugin and distinguishes its confirmed execution date from the later incident opening. The first incident-room image (v03) is retained as rejected because of its decorative white frame; corrected v04 is wrapped in the controlled reconstruction border as selected v05. Exact prompts, hashes, timings and tool limitations are in [outage-followup.json](outage-followup.json). All selections remain provisional.

The site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed. Rasterized lettered views were inspected for timestamp accuracy, caption clearance and border treatment. No script or scene geometry changed.

## Outage completion pass

The preceding outage batch was committed and pushed as `ab0bdc72` without lock recovery. Three built-in image calls produced selected 028-03 v03 and 028-06 v04. The first shows six distinct failed package-request lanes against ordinary rack lights. The closing panel shows four stalled workload cards connected to an unavailable service cabinet. Its first attempt (v03) repeated the sealed plugin silhouette and is retained as rejected; the targeted correction distinguishes the shared service from the plugin. The traffic bands and findings dossier remain controlled storyboards. All selections are provisional, and dark cabinet details still need trim-size proof.

Exact prompts, reference/output hashes, dimensions and timings are preserved in [outage-completion.json](outage-completion.json) and immutable sidecars. No manuscript or scene geometry changed. The complete storyboard check passed before generation. The site build, complete built storyboard check, lettering audit, viewer validation and built page-link check passed after selection. Both lettered SVGs were rasterized and visually reviewed; the text clears every workload card and the service label. This new completion batch remains uncommitted.

## Erasure response follow-up

At the start of this continuation the preceding outage artwork was committed as `aabd4ed2`, and the working tree was clean. Two built-in image calls produced selected 029-01 v03 and 029-02 v03. The first isolates the intact old service cabinet from four research workload lanes. The second keeps sealed storage hardware visibly separate from revoked credential symbols and paths stopped by a barrier. Both are editorial abstractions, not reproduced operational interfaces. No asset was marked final.

Exact prompts, reference/output hashes, dimensions, elapsed call times and tool limitations are in [erasure-followup.json](erasure-followup.json) and immutable sidecars. The complete storyboard check passed before generation. After selection, the site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed. Both lettered outputs were rasterized and inspected: labels remain visible above the captions, every research connection is interrupted, and preserved storage is intact. No manuscript or scene geometry changed. This batch remains uncommitted.

## Erasure completion pass

The preceding response batch was committed as `e0d9ef9f`; the working tree was clean at the start of this continuation. Two built-in image calls produced selected 029-03 v04 and 029-04 v03. Preserved hardware remains sealed beside the isolated old cabinet, with a wide empty gap before the clean instance. The closing directory contains no message rows or moss. Exact prompts, reference/output hashes, dimensions, timings and tool limitations are in [erasure-completion.json](erasure-completion.json) and immutable sidecars. The new cabinet omits the requested small directory field, but the following close-up supplies that view; the preserved-storage distinction reads clearly. Both selections remain provisional.

The underlying 029-03 storyboard label was corrected from “PRESERVED OLD CACHE” to “PRESERVED STORAGE” to match the canonical script. Its regenerated controlled board is v03; no manuscript or scene geometry changed. Complete storyboard validation passed before generation. The site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed afterward. Both lettered views were rasterized and visually reviewed: timestamp and captions are unobscured, the evidence enclosure remains intact, and no old contents cross into the new instance. This completion batch remains uncommitted.

## Effective mitigation follow-up

The erasure completion batch was committed as `45c725b0`; this continuation began with a clean working tree. Three built-in image calls produced selected 030-01 v03 and 030-05 v04. Traffic reaches the clean service while the old instance remains isolated. The closing overview combines an empty cache, revoked credential symbol, two blocked paths and permitted traffic reaching a live service. The first overview (v03) lacked a clear permitted incoming route and duplicated labels; it remains saved as rejected. The correction adds an OPEN label within the policy frame and makes the permitted path readable. These are editorial abstractions, not an operational topology or claim about additional mitigation mechanisms.

Exact prompts, reference/output hashes, dimensions, timings and tool limitations are in [mitigation-followup.json](mitigation-followup.json) and immutable sidecars. Complete storyboard validation passed before generation. The site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed afterward. Both lettered outputs were rasterized and inspected: captions clear the cabinets, labels and traffic paths. No manuscript or scene geometry changed. The three middle panels remain controlled storyboards. Both new selections are provisional and this batch remains uncommitted.

## Mitigation detail follow-up

The preceding mitigation batch was committed as `dd51f103`; this continuation began with a clean working tree. Three built-in image calls produced selected 030-02 v03 and 030-04 v04. The credential panel separates a crossed-out generic reader capability from three new workload symbols; no usable credential text is present. The attempt panel shows three outgoing requests and three returned failure cards on the same side of an intact boundary, with the exact scripted timestamp and controlled HTTP 400 lettering. Its first attempt (v03) placed failure cards across the boundary and copied key symbols from the reference; it is retained as rejected. The correction fixes both issues, although the boundary remains nearer the center than requested; the empty far side keeps the rejection legible.

Exact prompts, reference/output hashes, dimensions, timings and tool limitations are in [mitigation-details.json](mitigation-details.json) and immutable sidecars. Complete storyboard validation passed before generation. The site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed afterward. Both lettered outputs were rasterized and visually reviewed for arrow direction, three-attempt count, timestamp accuracy and caption clearance. The route-policy panel remains a controlled storyboard. No manuscript or scene geometry changed. Both selections remain provisional; this batch remains uncommitted.

## Causal-question pilot

The preceding mitigation-detail batch was committed as `cc27e175`; this continuation began with a clean working tree. Two built-in image calls produced selected 031-03 v03 and 031-05 v03. Equal CAUSE and TOOL questions bracket an empty moss outline in the old cache. These are creator questions, not institutional beliefs or a revived board. The closing clean service is surrounded by four empty dormant lane panels without active traffic or moss. The model rendered question cards rather than literal brackets, and the lane lines meet the cabinet rather than stopping short; their lack of arrows and explicit dormant labels keep the intended reading. These remain provisional editorial abstractions.

Exact prompts, reference/output hashes, dimensions, timings and tool limitations are in [causal-question.json](causal-question.json) and immutable sidecars. Complete storyboard validation passed before generation. The site build, complete built storyboard check, lettering audit, viewer validator and built page-link check passed afterward. Both lettered outputs were rasterized and visually reviewed: captions clear the question labels, old-board outline and clean service. No manuscript or scene geometry changed. The dossier columns and alternative-model panel remain controlled storyboards. This batch remains uncommitted.

## Restart detail continuation

Three built-in image calls produced provisional selected 032-03 v03 and 032-05 v04. The first separates missing input, blocked path and unsolved objective into three generic task cards. The second turns an anonymous cursor toward the clean package service without writing. Its first attempt pointed toward the task and is retained as rejected v03; the targeted edit corrects the direction. The cabinet carries an additional PACKAGES ONLY header inherited from its reference, consistent with the scripted state. Neither panel contains moss or communication content. No manuscript or scene geometry changed.

Exact prompts, reference/output hashes, dimensions, elapsed times and tool limitations are in [restart-details.json](restart-details.json) and immutable sidecars. Complete storyboard validation passed before generation. The site and image-generation census were rebuilt. Complete built storyboard validation, lettering audit, viewer validation, built page-link validation and census check passed. Both lettered outputs were rasterized and visually inspected for caption clearance and cursor direction. Panel 032-01 remains a controlled storyboard; these two selections are provisional.
