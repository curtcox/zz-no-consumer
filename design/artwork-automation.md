# Scripted artwork handoff and review

`python3 scripts/art_jobs.py` handles preparation, a durable queue, exact image
receipts, bounded retries, controlled borders, review sheets, and promotion. It
uses the existing storyboards, prompt composer, lettering layout, and artwork
store. It never calls a model, purchases generation, commits, or pushes.

## One batch

Run from the repository root. These commands demonstrate one existing panel;
choose a new descriptive job name for a different experiment.

```sh
python3 scripts/art_jobs.py prepare handover-board 037-03 --max-attempts 3
python3 scripts/art_jobs.py status
python3 scripts/art_jobs.py claim --job handover-board
```

Preparation rasterizes the current clean board with `rsvg-convert` (required on
PATH for preparation only). It saves the complete composed prompt without token
truncation, actual lettering exclusion boxes, source and style hashes, scene,
lettering layout, and board PNG. `--prompt-file PATH` replaces the base prompt;
production constraints are appended. `--reference PATH` adds an inspected PNG
continuity reference; repeat it for multiple references. The initial adapter
accepts noninterlaced 8-bit gray/RGB/RGBA PNGs only. It does not convert originals.

Inspect the exported prompt and reference images before generation. A complete
prompt is not necessarily a good prompt: conflicting art direction, scene intent,
source interpretation, and which exact graphic labels to draw still need judgment.
The clean storyboard can contain controlled labels; it excludes canonical lettering.

`claim` chooses the highest-priority eligible job if `--job` is omitted. It records
an attempt before returning the exact built-in image-tool arguments, including
absolute reference paths. The assistant invokes `image_gen.imagegen` using that
handoff and the current image-generation skill. A second claim cannot duplicate
the in-flight attempt. The tool remains an assistant-session operation; this
script does not expose or imitate a private image-generation endpoint.

Once the tool returns an output, save it with one command:

```sh
python3 scripts/art_jobs.py receive handover-board /absolute/path/to/output.png --seconds 30
```

`--seconds` is optional; omit it when not measured. The receiver validates PNG
chunk CRCs, dimensions and decompressed scanlines, then stores the exact bytes,
SHA-256, prompt, references, and available controls in one database transaction.
The current target is exactly 1536×1024; unexpected sizes fail explicitly.
Repeated delivery of the same latest output does not allocate another attempt.
Different bytes cannot overwrite a saved attempt. Model revision, seed and other
controls unavailable from the built-in tool stay null/unavailable.

Every successful mutation regenerates the review page, exact handoff files,
`status.json`, and `STATUS.md` under `256t/art-jobs/review/`. No extra recordkeeping
or HTML editing is needed. `export` can regenerate them after an interrupted write:

```sh
python3 scripts/art_jobs.py export
python3 -m http.server 8018 --directory 256t/art-jobs/review --bind 127.0.0.1
```

Open `http://127.0.0.1:8018/`. The self-contained sheet compares saved boards,
current reader art, and every lettered attempt, including rejected attempts. Each
job directory also contains the original PNGs and lettered SVGs for image-tool
inspection. The browser checks actual SVG text bounds against lettering boxes
and reports unloaded images after fonts load. Results are also available as
`window.artReviewReport`; this is a browser check, not a headless browser dependency
or an automatic visual-approval mechanism. It cannot identify labels generated
inside the raster, subject occlusion, or incorrect narrative implications.

Review the panel, lettered output, and neighboring reader pages. Then record one
concise decision, preferably with a defect category such as `text`, `clearance`,
`continuity`, `source-boundary`, `geometry`, or `palette`:

```sh
python3 scripts/art_jobs.py review handover-board reject --note 'clearance: category label overlaps caption'
python3 scripts/art_jobs.py retry handover-board --prompt-file /absolute/path/to/correction.txt
python3 scripts/art_jobs.py claim --job handover-board
```

The retry prompt is exact, with no appended boilerplate. A received prior output
becomes the edit reference; prior attempts remain available. Rejected and blocked
jobs do not automatically spend another call. The default limit is three attempts
and can be set to 1–10 at preparation. At the limit, retain the current reader art
and reconsider the composition before deliberately preparing a new experiment.

For a successful reviewed output, use:

```sh
python3 scripts/art_jobs.py review handover-board accept --note 'Action, source boundary, lettering and adjacent sequence reviewed'
python3 scripts/art_jobs.py verify
```

Acceptance adds the storyboard's controlled outer border, including its broken
reconstruction treatment or explicit borderless treatment. It stores a new refined,
chosen SVG variant through `panelart.store`, losslessly embedding the original PNG.
The normal builder adds canonical lettering exactly once. The raw PNG and input
references are also archived by content hash under `assets/art/job-references/`;
the variant sidecar preserves the snapshot, prompt, hashes and decision. This
provenance survives deletion of the local queue. No asset is marked final.

Pending and rejected outputs stay outside `assets/art/panels/`, so they cannot win
reader selection or make `produce.py` skip an unfinished slot. Existing selection
policy is unchanged; a previously final image still outranks this refined result.

`verify` runs the source storyboard and lettering checks, refreshes the repository
image census, rebuilds through the site builder, and runs built storyboard, viewer,
site-link, page-link and census checks. It stops at the first failure and saves
`256t/art-jobs/verification.json`, including output and exit codes. Run this once
at a reviewed batch boundary. If scripts or manuscript content changed, also run
the full repository CI sequence. Review the generated diff before publishing.

## Dependencies, interruption, and ownership

`prepare ... --depends OTHER_JOB` waits for that existing job to be accepted and
adds its accepted original PNG as a continuity reference when claimed. Dependencies
must already exist, preventing cycles. `--priority INTEGER` selects higher values
first. A prepared job whose dependency is rejected or blocked waits; `status` and
its exported job record explain the dependency. Run unrelated eligible jobs while
the blocked sequence is being resolved.

For an interrupted image call, first retrieve and `receive` its output if available.
If the output is unavailable, explicitly record that before retrying:

```sh
python3 scripts/art_jobs.py block handover-board --note 'Call interrupted; output recovery found no returned image'
python3 scripts/art_jobs.py retry handover-board --prompt-file /absolute/path/to/retry.txt
```

There is no automatic timeout-based requeue: a timed-out external call may still
have produced an image. Attempt counts include interrupted calls. Preparation,
claim, retry and acceptance validate source identity/composition; receive still
preserves an output if its source changed during generation. A stale job must be
reviewed and replaced by a new job, never silently retargeted or refreshed. Explicitly block
stale prepared jobs with the reason. `check` verifies their saved image integrity while
allowing historical source hashes; `claim`, `retry` and acceptance still refuse stale inputs.

The default SQLite queue is `256t/art-jobs/queue.sqlite3`. It is persistent local
operational state, **gitignored and not backed up by Git**. Keep the entire
`256t/art-jobs/` directory when backing up pending work. `--db PATH` before the
subcommand selects another local queue. Exported JSON/PNGs are review artifacts;
the database is authoritative. A new checkout does not inherit pending jobs.

SQLite transactions serialize this tool's writers and recover after process exit.
No stale-lock deletion is implemented. Coordinate other artwork writers and the
site builder: this database cannot lock unrelated `panelart.py` or `produce.py`
processes. Promotion recovers an interrupted store write by job/attempt identity
and exact composed bytes, avoiding duplicate versions. Repeat acceptance with the
original note if a partial promotion left a receipt. Interrupted table updates use
an atomic replacement; all earlier variants and curation remain preserved.

Queue panel keys are historical job inputs. Pagination and panel tools do not
rewrite this ignored operational database; source fingerprints prevent using stale
jobs after identity changes. Accepted sidecars are also historical records, not
live references. Continue to use identity tools for canonical page/panel changes.

## Validation and boundaries

`python3 scripts/art_jobs.py check` runs offline disposable fixtures covering corrupt
PNG rejection, duplicate delivery, pending-image isolation, stale source rejection,
dependency ordering, bounded retry, interrupted promotion recovery, concurrent
writers, and transaction rollback. If the selected queue exists, it additionally
checks its saved image hashes and active source snapshots. CI runs the fixtures
without any local queue, rasterizer, image model, credentials, or network.

The automation currently composes outer borders and existing canonical lettering.
It does not automatically place new exact in-scene labels, connectors, or evidence
markers. Such authored overlays need their own reviewed geometry. Nor does it
perform semantic image scoring, approve final print art, settle trim dimensions,
or run unattended generation. Those are later extensions; the present workflow
removes the repeated preparation/import/documentation/build plumbing.
