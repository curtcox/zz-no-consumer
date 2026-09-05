# ZZ: NO CONSUMER — Production Review

> **Stale as of 3 September 2026.** A script revision added panels to pages 039, 043, 086 and 101 and rewrote pages 016, 017, 032, 035, 038, 040, 041, 042 and 064. Scripted panels are now **547**, not 557 as measured below, and the word counts, chapter load, and page-turn audit predate the change. Pages 016, 039, 042, 064 and 086 need fresh rhythm and lettering measurement before any page advances to `locked`. Re-run this pass.

## Pass 1 — Thumbnail rhythm and lettering density

**Completed:** 2 September 2026  
**Scope:** all 112 canonical story pages  
**Artifact:** [`/production/thumbnails/`](/production/thumbnails/)

This is a structural pass, not final layout approval. Panel order is canonical; the contact sheet's geometry is provisional. Final thumbnails must still be drawn or blocked at intended trim size before any page advances to `locked`.

## Measurements

| Measure | Result |
| --- | ---: |
| Story pages | 112 |
| Physical spreads, including opening recto and final verso | 57 |
| Scripted panels | 557 |
| Intended visible words | 4,540 |
| Mean visible words per page | 40.5 |
| Densest page | 100 — 116 words |
| Pages above the 180-word guideline | 0 |
| Three-panel pages | 2 |
| Four-panel pages | 9 |
| Five-panel pages | 97 |
| Six-panel pages | 2 |
| Nine-panel pages | 2 |

Visible-word counts include captions, dialogue, qualifications, and essential screen text. They exclude frame direction, action, provenance, front matter, and page notes. Exact print fit cannot be inferred from word count alone, especially for long monospaced strings.

## Chapter load

| Section | Pages | Panels | Visible words | Densest page in section |
| --- | ---: | ---: | ---: | ---: |
| Prologue | 15 | 84 | 547 | 60 |
| Chapter 1 | 14 | 69 | 503 | 47 |
| Chapter 2 | 11 | 55 | 454 | 70 |
| Chapter 3 | 16 | 80 | 563 | 64 |
| Chapter 4 | 18 | 87 | 688 | 70 |
| Chapter 5 | 14 | 69 | 576 | 63 |
| Chapter 6 | 16 | 75 | 942 | 116 |
| Epilogue | 8 | 38 | 267 | 62 |

Chapter 6 is intentionally the most verbal section because it carries remediation claims, legal boundaries, and the composite forum. It remains comfortably below the global ceiling, but pages 091, 100, 101, and 102 need the earliest print-size lettering proofs.

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

## Page-turn audit

Story page 1 is a recto, so the 57 physical spreads are the lone opening recto, 55 facing pairs of an even page and the odd page after it, and the lone final verso. That layout gives a reveal two different devices, and they are not interchangeable.

A **reveal across the gutter** is prepared on an even page and lands on the odd page beside it. Both pages are already in front of the reader, so it works by reading order rather than by concealment: the eye crosses the gutter, and the second image reinterprets the first. 55 pairs exist.

A **turn across the leaf** is prepared on an odd page and lands on the even page behind it. The landing is genuinely hidden until the leaf moves. 56 turns exist.

The two are audited separately because `python3 scripts/pagination.py check` measures each against a different arithmetic shape, and because a beat built for one device does not survive being moved to the other. As the book stands, it choreographs almost entirely across the gutter: twenty named reveals and one named turn. All 55 facing pairs have an identifiable outgoing beat and landing purpose; the strongest are named below. The 038 → 039 reveal and the 085 → 086 turn were added by the September 3 revision and have not been re-audited in paired spreads.

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
| 088 → 089 | Seams remain visible → concrete remediation begins |
| 098 → 099 | Coordination remains missing → invented forum disclosed |
| 104 → 105 | Incident becomes artifact → manuscript assembly |
| 114 → 115 | Publication → explicitly invented future |
| 116 → 117 | Local side effect has an audience → shared visibility confirmed |

### Turns across the leaf

| Turn | Function |
| --- | --- |
| 085 → 086 | Tools resemble each other → the reader's own belief is charged |

That this table has one row is a finding, not an omission. The book's central manipulation of the reader — page 086's enlarged provenance tag, which changes what page 064 was allowed to mean — is the only beat currently built on a landing the reader cannot already see. Whether more of the book should work that way is an editorial question the audit does not answer; it names the device so the question can be asked.

No reveal currently depends on concealing a fact already known to the viewpoint. Source-register changes at 012→013, 066→067, 088→089, and 108→109 require unmistakable palette, border, and typography changes in final thumbnails.

## Remaining production checks

- The third-party quotation hold is resolved by paraphrase; keep source attribution legible and follow [`research/exact-text-permissions-audit.md`](../research/exact-text-permissions-audit.md).
- Proof pages 003, 004, 036, 057–060, 079, 081, 091, 100–102, and 118 at intended print size because they contain unusually long summaries, project-authored display strings, or evidence-card typography.
- Draw genuine thumbnail geometry for every page; the generated contact sheet is a rhythm map, not a layout decision.
- Confirm all full-width and tall panels leave safe areas for captions and do not place essential text in the gutter.
- Test the five high-value page-turn register changes in paired physical spreads and as single pages online.
- Re-run this pass after any lettering edit or panel split. The generator should remain deterministic and dependency-free.
