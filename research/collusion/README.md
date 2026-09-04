# Wiki edit corpus

Primary-source export of the wiki activity behind the coordination incident: every stored
revision, the page it belongs to, the save/delete/revert/probe events around it, and the
per-handle rollups. This is evidence, not story material. Nothing in `content/` cites it yet.

**These are small self-hosted wikis — `dse`, `probier`, `fractal`, `dorfwiki` — not Wikipedia.**
The commit that first added the archives described them as Wikipedia edit logs; that was wrong.

## Files

| File | Rows | Grain |
| --- | ---: | --- |
| `pages.jsonl` | 4,579 | one wiki page in the cut |
| `revisions.jsonl` | 14,591 | one stored revision, including full body text |
| `events.jsonl` | 19,913 | one observed save, delete, revert, or probe |
| `labels.jsonl` | 3,103 | one edit handle, with its page list and request rollups |
| `manifest.json` | — | provenance, counts, named facts, and the exporter's own checks |
| `SHA256SUMS` | — | integrity record for the five data files |

Verify the export at any time:

```bash
cd research/collusion && shasum -a 256 -c SHA256SUMS
```

## Provenance and cut

Exported 3 September 2026 by `explorer-schema-2` from a SQLite database whose contents hash to
`199241bf9e…` (`manifest.db_sha256`). The published cut is `revision.write_date >= 2026-05-01`.
Revisions run 24 May – 2 July 2026; events run 17 May – 14 July 2026, so the event stream extends
past the last held revision on both ends.

`manifest.source_scan` names the raw request logs the export scanned (`reqlog_dse_2606.jsonl` and
friends, ~2.8M rows) and how many rows each contributed. Those raw logs are not in this repository.

### Counts do not add up, on purpose

`manifest.facts` carries 58 named figures, each tagged with a `population_id`, a prose
`definition`, `source_refs`, and a `never_add_to` list naming the populations it must not be summed
with. The four event-type counts overlap in what they describe — `manifest.population_counts.never_sum`
says so explicitly. Quote a fact by its manifest key and population, not by re-deriving a number
from a filtered row count.

The exporter's own 13 checks are in `manifest.checks`, all `ok: true`, and are re-verifiable
against the rows here.

## Joins

`page_key` (`wiki~PageName`) is the spine; `page_id` (`wiki/PageName`) is the same identity in
slash form. Revisions carry both plus `rev_id` (`page_key@seq`). Save events carry
`revision_ref` equal to that `rev_id`, and a revision's `related_event_id` is a **list** of event
ids. `labels.jsonl` links out by `page_id`, not `page_key`.

## Field notes

**pages.jsonl** — `bucket` is the RCS storage directory (first letter uppercased, or `other`),
not a classification. `page_family` is a task classification covering the 3,908 `dse` pages from
`corpus/evals/page_family.jsonl`; the other 671 pages carry `page_family: off_store_unclassified`
and `page_family_source: none`. Read `page_family_method` before trusting a family: values range
from strong (`name-loop-predicate`, `body+name:14`) to explicit non-findings
(`no-positive-signal`, `url-present-unresolved`). The largest families are
`source-cache-url-list` (1,231), `relay-coordination` (709), and `loop-chain-infrastructure` (339).
No page in the cut is `deleted_live`.

**revisions.jsonl** — `body` is the full source text (27.2 MB across the cut). `hunks` are
line-level `insert`/`replace`/`delete` ops against `diff_base`; `diff_base` is null for the 4,562
page-creating revisions (`diff_base_reason: page_created`) and for 17 whose predecessors fall
outside the cut (`earlier_revisions_not_published`). Every revision's clock resolves to
`revision.pref_ts`, but `time_grade` records how well that is corroborated — 14,482 `reqlog`,
103 `rclog`, 6 bare `write_date` — with `uncertainty_seconds` alongside.

**events.jsonl** — the schema varies by `event_type`. `save` rows are thin pointers at a revision;
`delete` and `revert` rows carry the full clock-reconciliation block (`winning_clock`,
`clock_delta_seconds`, `clock_note`, four candidate timestamps) plus `actor_label` and
`success_observed`; `probe` rows carry `param_family` and no page. Only 4 reverts and 101 probes
exist. `manifest.recreation_source` explains that the 68 first-recreation relations are derived
from the rclog rather than read from a row-level file, and gives the two-second linking rule.

**labels.jsonl** — a label is an edit handle, not a person: 3,100 of 3,103 have
`is_human_handle: false`. `stored_revisions` counts revisions held in this cut; `save_requests`
counts request-log saves, which is a different and larger population (the blank-label handle has
899 stored revisions against 3,653 save requests). Handles cluster by prefix — `Agent…`,
`OpenAI…`, `…Helper`.

## Privacy and handling

Addresses appear only as `ip16` — the first two octets. Personal names are already pseudonymized
in place as `[Person14]`, `[User4]`, and similar, inside page names and bodies. Keep it that way.

`scripts/build-site.py` only collects `*.md`, and the public build excludes `research/` entirely,
so these rows reach neither `docs/` nor the internal build. This `README.md` does appear in the
internal build (`--internal`). Revision bodies contain agent-authored operational material and
scraped third-party content; treat any reuse in tracked prose under
[`research/security-sensitivity-review.md`](../security-sensitivity-review.md) and the
attribution rules in [`research/draft-source-notes.md`](../draft-source-notes.md).

## Recipes

```bash
# rows are compact JSON (no space after ":"), so grep for the packed form
grep -c '"label":"AgentRelent"' revisions.jsonl        # 317

# page families by size
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['page_family'] for l in open('pages.jsonl')).most_common(15))"

# one page's full history, oldest first
python3 -c "
import json
rows=[json.loads(l) for l in open('revisions.jsonl') if '\"page_key\":\"probier~OpenAI\"' in l]
for r in sorted(rows, key=lambda r: r['seq']):
    print(r['seq'], r['time'], r['label'] or '<blank>', repr(r['body'][:100]))
"

# a named fact with its population, definition, and never-add-to list
python3 -c "import json;print(json.dumps(json.load(open('manifest.json'))['facts']['dse_held_revisions'],indent=2))"
```

The archives these files were extracted from (`full-wiki-logs.zip` and five `.gz` files) were
byte-identical duplicates of each other; both sets were removed in favour of the plain rows.
They remain in history at commit `e482712b`.
