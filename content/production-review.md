# ZZ: NO CONSUMER — Production Review

> **Counts remeasured 6 September 2026, after the Chapter 5 insertion.** Pages 086 and 087 were added on 6 September; the tables below are measured from the current script and supersede the 5 September figures, which superseded the 2 September ones.
>
> **Counts remeasured 5 September 2026, after the read-through pass.** The measurement, chapter-load, and rhythm tables below are derived from the current script by `scripts/panels.py report` and the lettering definition in `scripts/cadence.py`, and they supersede the 2 September figures. Two staleness notices — one from 3 September, one from earlier on 5 September — are discharged by this remeasurement and have been removed.
>
> **What is still open is human work, not arithmetic.** No thumbnail has been drawn at trim size; the contact sheet remains a rhythm map, and it has no six-panel geometry, which twelve pages now need. Seventeen pages carry panel art and two carry prompt directories; the pages added or rebuilt on 5 September — now 098, 099, 100 and the new panels on 014, 052, 075 and 111 — carry neither, and neither do 086 and 087, added on 6 September. Fourteen pages now need six-panel geometry rather than twelve. The print-size lettering proofs listed below have not been run. The page-turn audit is not remeasured here because it is not a measurement: `python3 scripts/pagination.py check` verifies every parity assertion and turn row against arithmetic on every run, and it is green.

## Pass 1 — Thumbnail rhythm and lettering density

**Completed:** 2 September 2026. **Counts remeasured:** 5 September 2026.  
**Scope:** every canonical story page  
**Artifact:** [`/production/thumbnails/`](/production/thumbnails/)

This is a structural pass, not final layout approval. Panel order is canonical; the contact sheet's geometry is provisional. Final thumbnails must still be drawn or blocked at intended trim size before any page advances to `locked`.

## Measurements

| Measure | Result | 2 Sep |
| --- | ---: | ---: |
| Story pages | 118 | 112 |
| Physical spreads, including opening recto and final verso | 60 | 57 |
| Scripted panels | 606 | 557 |
| Intended visible words | 6,000 | 4,540 |
| Mean visible words per page | 50.8 | 40.5 |
| Densest page | 101 — 155 words | 100 — 116 |
| Pages above the 180-word guideline | 0 | 0 |
| Three-panel pages | 2 — 067, 118 | 2 |
| Four-panel pages | 4 — 029, 064, 081, 095 | 9 |
| Five-panel pages | 95 | 97 |
| Six-panel pages | 14 | 2 |
| Seven-panel pages | 1 — 088 | 0 |
| Nine-panel pages | 2 — 006, 007 | 2 |

Of the 594 panels, 576 are individually scripted and 18 belong to the two grouped nine-panel runs on pages 006 and 007, which are written as one block each and are not operated on panel by panel.

The **2 Sep** column reproduces that pass's figures as it recorded them; they were not re-derived under the current definition, so the deltas below are indicative rather than exact arithmetic on one method.

Visible-word counts include captions, dialogue, qualifications, and essential screen text. They exclude frame direction, action, provenance, front matter, and page notes. Exact print fit cannot be inferred from word count alone, especially for long monospaced strings.

**The book got denser, not just longer.** Mean visible words per page rose from 40.5 to 49.6 between 2 and 5 September — a 22 percent increase against a 4 percent increase in page count. Most of it is the dated wiki addition and the creator-register expansions, both of which are text-heavy by construction. Nothing is over the 180-word line and nothing is close to it, but the trend is the thing to watch at the next pass: the guideline was set against a forty-word mean.

## Chapter load

| Section | Pages | Panels | Visible words | Words per page | Densest page in section |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prologue | 15 | 85 | 580 | 38.7 | 014 — 92 |
| Chapter 1 | 14 | 70 | 613 | 43.8 | 016 — 120 |
| Chapter 2 | 11 | 56 | 580 | 52.7 | 039 — 139 |
| Chapter 3 | 16 | 82 | 624 | 39.0 | 053 — 64 |
| Chapter 4 | 18 | 87 | 745 | 41.4 | 067 — 84 |
| Chapter 5 | 16 | 84 | 933 | 58.3 | 089 — 106 |
| Chapter 6 | 14 | 72 | 1,019 | 72.8 | 101 — 155 |
| Epilogue | 14 | 70 | 906 | 64.7 | 106 — 140 |

Chapter 6 is intentionally the most verbal section because it carries remediation claims, legal boundaries, and the composite forum. **It is now the most verbal by a wider margin than before, on two fewer pages:** the 5 September compression removed three pages of abstraction that were also comparatively light, and page 100 added a dense one, so the section's words per page rose from 58.9 to 71.6 while its total barely moved. That is the intended trade — evidence in place of restatement — but it puts the whole chapter first in the lettering-proof queue rather than a few pages of it.

The epilogue is the second-densest section, at 62.5 words per page, entirely because of the dated wiki addition; before that addition it was the lightest section in the book.

The eight pages to proof first, in order: 099 (156), 039 (139), 104 (138), 109 (136), 016 (121), 098 (112), 087 (106), 040 (104).

## Rhythm findings and revisions

Panel count alone overstated uniformity because five-panel pages already describe different shot scales and repeated geometries. Even so, five equal beats had been used for several moments that should feel like conceptual stops. This pass revised:

| Page | Change | Production reason |
| ---: | --- | --- |
| 029 | Five panels → four | Let rebuild and cache erasure occupy one tall before/after state change. |
| 064 | Five panels → four | Let eleven coordinator lanes terminate in one sustained timeline image. |
| 067 | Five panels → three | Make the METR/OpenAI source boundary read as a hard evidentiary stop. |
| 081 | Five panels → four | Keep the missing logging architecture and rejected reconciliation in one comparison field. |
| 118 | Four panels → three | Remove the didactic lineage caption and preserve silence between the project-authored help prefix and the final line. |

Pages 006–007 retain the only paired nine-panel grids. Page 012 retains six ascending beats plus the title landing. The provisional contact sheet alternates wide-top, wide-bottom, tall-left, and tall-right geometry for five-panel pages so final thumbnailing begins from varied silhouettes rather than identical grids.

### Rhythm changes since, 3–5 September

The six-panel band grew from two pages to twelve and a seven-panel page appeared, which is the main structural difference from the 2 September contact sheet. Page 095 also moved from five panels to four. The pages that changed:

| Page | Panels | Why |
| ---: | ---: | --- |
| 088 | 7 | The book's central disclosure decelerates on panels 1–2 and then moves; the extra beat is the pacing. |
| 012, 028, 039, 043 | 6 | Earlier revisions, 3 September. |
| 014 | 6 | The model-corrects-creator beat, added 5 September. |
| 052 | 6 | The convergence argument's negative on the resource axis, placed before the thesis rather than after it. |
| 075 | 6 | The twenty-million denominator, so the three units of scale never share a shape. |
| 098 | 6 | Three pages of structural comparison compressed into one. |
| 099 | 5 | Two forum pages compressed into one; the record enters as a single visual panel rather than a page of dialogue. |
| 100 | 6 | New page. |
| 101 | 6 | The cited Black Hat case, unchanged in the compression. |
| 106, 109 | 6 | The dated addition. |

Twelve six-panel pages against ninety-five five-panel pages is still a narrow band, but it is no longer a rarity, and the contact sheet's five-panel geometry rotation does not cover it. The next thumbnail pass needs six-panel silhouettes as well.

## Page-turn audit

Story page 1 is a recto, so the 57 physical spreads are the lone opening recto, 55 facing pairs of an even page and the odd page after it, and the lone final verso. That layout gives a reveal two different devices, and they are not interchangeable.

A **reveal across the gutter** is prepared on an even page and lands on the odd page beside it. Both pages are already in front of the reader, so it works by reading order rather than by concealment: the eye crosses the gutter, and the second image reinterprets the first. 55 pairs exist.

A **turn across the leaf** is prepared on an odd page and lands on the even page behind it. The landing is genuinely hidden until the leaf moves. 56 turns exist.

The two are audited separately because `python3 scripts/pagination.py check` measures each against a different arithmetic shape, and because a beat built for one device does not survive being moved to the other. As the book stands, it choreographs almost entirely across the gutter: twenty named reveals and one named turn. All 55 facing pairs have an identifiable outgoing beat and landing purpose; the strongest are named below. The 038 → 039 reveal was added by the September 3 revision and has not been re-audited in paired spreads. The book's one turn across the leaf was 085 → 086 until the 6 September insertion of pages 086 and 087; its landing is unchanged and is still the provenance disclosure, but its outgoing page is now 087, which ends on the shared-trade finding rather than on the mirror. The beat is stronger for it and has not been re-audited in paired spreads either.

### Reveals across the gutter

| Facing pair | Function |
| --- | --- |
| 002 → 003 | Impossible task → newly discovered shared resource |
| 004 → 005 | Persistent message → first reply |
| 008 → 009 | Apparent solution → grader uncertainty reopens the problem |
| 012 → 013 | Book title → creator layer revealed |
| 018 → 019 | Failed access attempt → persistent side effect becomes communication |
| 028 → 029 | Shared resource becomes incident → board erased by genuine response |
| 032 → 033 | Clean rebuild → communication recurs |
| 046 → 047 | Execution foothold → peer instruction becomes operational authority |
| 054 → 055 | Local rationality → detection succeeds technically |
| 056 → 057 | No human page → reset becomes collective experiment |
| 064 → 065 | Coordinator silence → organization persists through artifacts |
| 066 → 067 | Actionable inheritance → independent-evidence boundary closes |
| 072 → 073 | Evaluations shut down → creator rejects the neat emotional reading |
| 038 → 039 | Creator confidence peaks → a published critique breaks the thesis |
| 080 → 081 | AI analysis is necessary → conflicting log claims appear |
| 090 → 091 | Seams remain visible → concrete remediation begins |
| 098 → 099 | Coordination remains missing → invented forum disclosed |
| 104 → 105 | Incident becomes artifact → manuscript assembly |
| 114 → 115 | Publication → explicitly invented future |
| 116 → 117 | Local side effect has an audience → shared visibility confirmed |

### Turns across the leaf

| Turn | Function |
| --- | --- |
| 087 → 088 | Three instruments, one shared trade → the reader's own belief is charged |

That this table has one row is a finding, not an omission. The book's central manipulation of the reader — page 088's enlarged provenance tag, which changes what page 064 was allowed to mean — is the only beat currently built on a landing the reader cannot already see. Whether more of the book should work that way is an editorial question the audit does not answer; it names the device so the question can be asked.

No reveal currently depends on concealing a fact already known to the viewpoint. Source-register changes at 012→013, 066→067, 088→089, and 108→109 require unmistakable palette, border, and typography changes in final thumbnails.

## Remaining production checks

- The third-party quotation hold is resolved by paraphrase; keep source attribution legible and follow [`research/exact-text-permissions-audit.md`](../research/exact-text-permissions-audit.md).
- Proof pages 003, 004, 036, 057–060, 079, 081, 093, 099, 101, 102, and 118 at intended print size because they contain unusually long summaries, project-authored display strings, or evidence-card typography.
- Draw genuine thumbnail geometry for every page; the generated contact sheet is a rhythm map, not a layout decision.
- Confirm all full-width and tall panels leave safe areas for captions and do not place essential text in the gutter.
- Test the five high-value page-turn register changes in paired physical spreads and as single pages online.
- Re-run this pass after any lettering edit or panel split. The generator should remain deterministic and dependency-free.
