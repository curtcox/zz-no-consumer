---
title: Add timeindex.py check --built to the CI check block
status: open
proposed: 2026-09-15
proposed_by: Devin (SWE-2)
decision_needed_from: Curt
blocking: false
affects:
  - .github/workflows/pages.yml
  - AGENTS.md (the copy-paste check sequence)
decided:
decided_by:
---

# Add timeindex.py check --built to the CI check block

## Decision requested

Approve adding `python3 scripts/timeindex.py check --built` to the pre-build
section of `.github/workflows/pages.yml` and to the mirrored command list in
`AGENTS.md` (## Checks).

## Why

`timeindex.py` is new tooling that answers timespan queries for agents:
`data/time-spans.tsv` (hand-maintained coverage registry) plus
`data/time-index.json` (derived). The check fails when a `When` cell in
`research/timeline.md` no longer parses, when a registry id or tier is invalid,
or — under `--built` — when the committed index is stale relative to its
inputs. Without CI coverage the JSON can silently drift from the sources it
summarises.

## Proposal

One step in the check block, placed with the other content-graph validators:

```yaml
- run: python3 scripts/timeindex.py check --built
```

Suggested position: after `crossref.py check --strict`, since the index reads
the same registries. Agents run `python3 scripts/timeindex.py build` after
editing `data/time-spans.tsv`, `research/timeline.md`, `story_time` or
`exact_strings` front matter, the collusion corpus, or the edition
manuscripts — the same "rebuild what your input feeds" rule as `docs/`.

## Alternatives

- **Leave it out of CI.** The tool still works locally; the cost is a stale
  `data/time-index.json` that only the next `check --built` run catches.
- **`check` without `--built`.** Weaker: validates inputs but tolerates a
  stale committed index.

## Risks

Low. The check is deterministic and offline; a failure means an unparsed
timeline row or a stale JSON, both fixed by editing the input or rerunning
`build`. The corpus scan reads ~40 MB of JSONL and takes about a second.

## Opinions

<!-- Append entries; never edit someone else's. -->

## Decision

