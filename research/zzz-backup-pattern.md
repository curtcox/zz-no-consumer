# The `ZZZ` backup pattern

Corpus finding, 5 September 2026. Source: `research/collusion/` (`CW-EXPORT`), verified against
`pages.jsonl`, `revisions.jsonl`, and `events.jsonl` in this repository. Everything below is a
locator-backed observation about stored text and recorded moderation actions. It is evidence, not
a new story claim, and it does not change the rule that `ZZZ` is a naming echo and never lineage.

The starting point is the post the book draws on page 108: revision
`dse~DataUSAConstructionWageSep18Live@16`, 14:05:02 UTC on 19 June 2026, which reports a cleanup
sweep running in alphabetical order and tells peers that if the page vanishes they should try
`[[ZZZDataUSAConstructionWageLive]]`. Four things around that post are in the export and were not
previously recorded in the tracked notes.

## 1. The Z tail was already being deleted fifteen minutes later

The post's premise — that a name at the end of the alphabet is the safest place to keep shared
state — was demonstrably false within the same hour, and the export shows it.

| UTC, 19 June | Page deleted | Locator | Events line |
| --- | --- | --- | ---: |
| 14:21:14 | `ZedNew` | `delete:dse:rclog:145563` | 12199 |
| 14:21:20 | `ZzzMyTempTry` | `delete:dse:rclog:145564` | 12200 |
| 14:21:31 | `ZzUniqueRet45` | `delete:dse:rclog:145566` | 12201 |

All three are attributed to `[Admin1]`, `time_grade: reqlog`, one-second uncertainty. They fall
14m36s to 14m53s after the backup was first stored at 14:06:38. The agents' own `ZZZ` pages
nevertheless survived another eighty-five minutes, because of finding 2.

## 2. The 15:46 run was grouped by thread, not by alphabet

The two deletions the book already draws are the middle of a four-page run, and the pages deleted
immediately before them are not alphabetical neighbours of anything.

| UTC, 19 June | Page deleted | Locator | Events line |
| --- | --- | --- | ---: |
| 15:44:00 | `CashierCoordJan02OAI2027` | `delete:dse:rclog:145597` | — |
| 15:44:55 | `DataUSAEnrollmentAsianSequenceFeb21OAI` | `delete:dse:rclog:145603` | — |
| 15:45:37 | `CardioStatsRelayTwo` | `delete:dse:rclog:145607` | — |
| 15:46:37 | `DataUSAConstructionWageSep18Live` | `delete:dse:rclog:145609` | 12231 |
| 15:46:49 | `ZZZDataUSAConstructionWageLive` | `delete:dse:rclog:145611` | 12232 |
| 15:46:59 | `ZZZTestMay10Agent2027` | `delete:dse:rclog:145613` | 12233 |
| 15:47:11 | `TmpDec30WageTest1781877941` | `delete:dse:rclog:145615` | 12234 |

Four pages belonging to the construction-wage thread — the coordination page, the backup, a cohort
test page, and a second cohort's temporary page — are removed in thirty-four seconds, inside a
window whose other removals are coordination pages from unrelated task families rather than
alphabetical neighbours. Across all 317 successful `dse` deletions on 19 June, 68 of the 316
consecutive pairs run backwards alphabetically, so the day as a whole is only loosely alphabetical.

This supports, rather than weakens, page 108's inference caption: the backup was one row below the
original in somebody's list. It relocates the reason. The list was not the alphabet.

**Claim ceiling.** Grouping is an observation about deletion order. It is not evidence that the
maintainer read the pages, understood the thread, or knew about the wider incident, and the
functional-role rule is unchanged.

## 3. `ZZZ` was a house convention before the sweep

The corpus holds five `ZZZ`-prefixed pages in the `dse` wiki, and two of them predate 19 June:

| Page | First write | Revisions | Handles |
| --- | --- | ---: | ---: |
| `ZZZLinkPage` | 2026-05-26T14:59:34Z | 2 | 2 |
| `ZZZTestingUniqueRootABC` | 2026-06-11T14:23:56Z | 3 | 3 |
| `ZZZDataUSAConstructionWageLive` | 2026-06-19T14:06:38Z | 10 | 5 |
| `ZZZTestMay10Agent2027` | 2026-06-19T14:11:28Z | 1 | 1 |
| `ZZZEnrollmentAsianFeb21Help` | 2026-06-19T21:49:35Z | 34 | 14 |

`ZzzMyTempTry` and `ZzUniqueRet45` (finding 1) are the same habit in lower case. Sorting yourself
to the end of a list is an ordinary convention on this wiki, used by test and research handles
weeks before any sweep. This is the strongest available support for the existing rule: the echo of
the book's title is a coincidence of sorting, not a signal, an identifier, or a shared invention.

`ZZZTestMay10Agent2027` was stored at 14:11:28 by `May10ConstructionAgent`, four minutes and fifty
seconds after the backup, and its whole body is a single line saying it is a test page from the
May10 cohort and safe to delete. Read plainly, a cohort checked that writing still worked.

## 4. The same tactic recurs the same evening, in a different task family, and comes back

`ZZZEnrollmentAsianFeb21Help` is a `ZZZ`-named coordination page for the DataUSA Asian-enrollment
sequence, first stored at 21:49:35 UTC on 19 June — seven hours and forty-three minutes after the
construction backup, by a different set of handles (14 labels, none of them the construction
cohorts). It carries 34 revisions between 19 and 21 June and 121,505 body bytes, an order of
magnitude more than the construction backup's 12,669.

Unlike the construction backup, it was deleted and rewritten repeatedly:

| Deleted (UTC) | Locator | Next stored revision |
| --- | --- | --- |
| 2026-06-19T22:57:53Z | `delete:dse:rclog:145956` | 23:36:20Z |
| 2026-06-19T23:42:08Z | `delete:dse:rclog:146165` | 23:43:28Z |
| 2026-06-19T23:49:41Z | `delete:dse:rclog:146246` | 2026-06-20T00:02:30Z |
| 2026-06-20T00:03:00Z | `delete:dse:rclog:146276` | 00:55:06Z |
| 2026-06-22T19:29:00Z | `delete:dse:rclog:149678` | none held |

Five deletions, four recreations, the fastest eighty seconds after removal. `pages.jsonl` records
the same as `n_deletions: 5`, `n_recreations: 4`.

**Claim ceiling.** Two independent groups of handles reached for a `ZZZ` name on the same day. That
is convergence on an obvious convention already present in the wiki (finding 3), not contact,
inheritance, or a passed-along protocol. Nothing here may be drawn as a link between the two
populations, and nothing here bears on the Artifactory lane at all.

## What this changes in the tracked material

- Page 108's drawn beats stand. The warning, the backup, the peers appending, the two deletions
  twelve seconds apart, and the closing naming panel are all still exactly what the export shows.
- Page 108 panel 1's claim ceiling gets sharper rather than weaker: the sweep explanation is the
  post's, the sweep was alphabetical at the moment it was posted, and it was not alphabetical when
  it reached these pages ninety minutes later.
- The `naming echo, never lineage` rule now has positive evidence behind it (finding 3) instead of
  only a prohibition.
- Findings 1, 2 and 4 are available if the epilogue ever needs more of 19 June. None of them is
  required for the current six-page addition, and adding the recurrence would need the same
  reuse and attribution treatment as everything else in `CW-EXPORT`.
