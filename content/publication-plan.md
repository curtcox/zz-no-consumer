# The Two Anthill Problem — Publication Master Plan

Six publication targets, one book. This plan states what is measured today, what
each target still needs, what the targets share, and what only the owner can decide.

**Repository status remeasured 7 September 2026.** External publication requirements later in this plan retain their original review dates; this update measures the repository:

| Measure | Value | Source |
| --- | --- | --- |
| Story pages | 118 | `pagination.py check` |
| Panels / image slots | 606 / 590 | `panels.py check` |
| SVG storyboard coverage | 590/590 slots | `storyboards.py check --complete` |
| Slots with refined/final candidates | 43 (7.3%) | `produce.py status` |
| Panel art decisions made | 0 of 590 | `panelart.py status` |
| Novella prose | 118/118 pages, 44,272 words | `novella.py report` |
| Appendix entries | 24 contested assertions, 29 fallacies, 45 professional objections, 20 FAQs; 841 references | `appendix.py report` |
| Page status | 110 `review`, 8 `draft`, 0 `locked` | front matter |
| Lettering elements | 574 placed, 0 unplaced or truncated in the reader layout | `letterpress.py audit` |
| Tracked assets still needed | 11 of 20 | `data/assets.yaml` |
| Validators | all green | continuity, pagination, panels, crossref, viewer, foundations |

**Current status.** Both reading editions are complete in coverage. Every graphic-novel slot has a storyboard; 43 have richer candidates, and none is explicitly chosen. The novella and appendix ship as EPUB, HTML, Markdown, and text downloads. Final artwork, trim-size composition, cover, and audio remain production work.

---

## Part A — Trunk work every target needs

Nothing below is optional for any of the six. Doing it once, in the repository,
is what keeps six targets from becoming six divergent books.

### A1. Verify the remaining visual production gates

- **Fog-map adoption pass** (`research/revision-priorities.md` item 8). Steps 1–3 are
  done; step 4 (web presentation, proposed as a `map=` fragment setting) and step 5
  (generate strips through the site builder, relabel the samples, rerun gallery,
  viewer and continuity checks) are **not started**. Use the appearance list in `design/knowledge-map.md` for the current scope. This changes pages, so it must land before lettering and layout.
- **Recurring critic text is present:** the dated addition and ending carry the criticism and composite replies. The 5 September read-through decisions are recorded as applied; this pass corrected the remaining prose/source-boundary drift.
- **Visual craft review:** verify spread composition, the incident-wordmark callback, the dated anthill-title scene and its rejected connector, and page-turn treatment at trim size. These are layout checks on existing text; the applied read-through edits are not an outstanding request to rewrite those passages.
- **Advance the 8 draft pages** — 086, 087, 106–111 — from `draft` to `review` via the
  beat and thumbnail test they are waiting on.
- **Provenance audit completed 7 September:** all panel statuses and source keys agree with page metadata. Strict checking now runs in CI; the previously undeclared statuses are resolved.

**Why first:** every one of these can insert, delete, or move a page. `pagination.py`
makes that a safe rewrite *of the script*, but it cannot un-generate art, un-letter a
page, or un-typeset an EPUB. Review the intended batch’s text and structure before spending GPU hours; page identity remains tool-managed if later editing requires a change.

### A2. Decide the trim size

Still open, and named as open in `design/lettering-slots.md:90` and
`design/image-generation-options.md:712`. At the current 1200×800 a panel is
4″×2.67″ at 300 dpi, which is small for print and marginal for a fixed-layout tablet
page. **This decision sets panel render dimensions, so it must precede the art run.**
Re-rendering 590 panels because the trim changed is the single most expensive mistake
available in this project.

### A3. Draw the artwork

547 slots have no refined/final candidate; all already have SVG storyboards. Choose which need raster artwork before estimating a run. Diagrams and interfaces may remain controlled graphics. Measure runtime and acceptance rate on a representative pilot before extrapolating. The run is interruptible and resumable by design.

```sh
python3 scripts/produce.py plan
python3 scripts/produce.py run --route local        # the panels any model can draw
python3 scripts/produce.py run --route text-fidelity --provider qwen-image-local
```

Route matters: `paneltypes.py` splits the book into panels a 16 GB laptop handles,
80 that need long strings spelled correctly, and 59 that need reference conditioning
for a recurring face. The premium models earn their price on about a quarter of the
book and are wasted on the rest.

**Licence note, and it is load-bearing for the three paid targets:** all 199 logged
generations used `flux2-klein-4b`, Apache-2.0, commercial use permitted. Keep it that
way. `flux1-dev-local` and `flux2-klein-9b` are non-commercial and nothing they
produce may appear in a book sold on Amazon.

### A4. Choose the art

`panelart.py status` reports 0 decided and 572 slots with more than one version. An explicit choice wins; otherwise the most mature non-rejected candidate wins, with the newest version breaking ties at the same stage. Automatic selection is provisional.

```sh
python3 scripts/panelart.py choose 001-01 v02
```

### A5. Produce the 11 missing reference assets

`data/assets.yaml` still lists 11 as `needed` — the ink-texture sheet and the
environment sheets for eval, cache, SOC, lab, investigation, and forum. These are what
make 590 independently generated panels look like one book.

### A6. Letter the book

The reader now places all 574 fields using the slot convention and explicit storyboard boxes. `letterpress.py audit` checks that effective layout and finds no unplaced or truncated fields. Finished balloon treatment and trim-size proofs still need visual review.

### A7. Build the page compositor

**This tool does not exist.** The README is explicit: "Page sheets are not generated.
A page is composed from its panels by layout." That is correct for the web viewer,
which serves panels. It is not sufficient for a printed page, a fixed-layout EPUB
page, or a PDF — all three of which need a composed 118-page artifact.

Needed: a `scripts/compose-pages.py` that reads the panel grid from
`design/page-grammar.md`, places chosen art plus the lettering layer at trim size with
bleed and safe areas, and emits one image or PDF page per story page. It is the
gating dependency for targets 2 (print-fidelity), 3, and any PDF handed to ElevenReader.

### A8. Front matter, back matter, and cover

None of this exists yet:

- **Cover.** No cover art, no cover concept, no file. Needed at three specs: web,
  Kindle eBook (1.6:1, min 1000px, 2560×1600 preferred), and audiobook (square,
  min 2400×2400).
- **Title page, copyright page, licence page.** The GPL-3.0-or-later notice must
  appear in the book itself, not only in the repository.
- **Endmatter.** `content/credits.md` exists and is the book's credits page. Confirm
  it reads as endmatter and not only as a site page.
- **Appendix.** `content/appendix/` exists and already ships in all four novella
  downloads and at `/appendix/`. It is keyed to story page numbers, so it needs no
  per-edition variant; what it still needs is a decision about whether the print and
  fixed-layout editions carry it in full, carry the index and point at the web, or
  carry a QR code. Links are the payload, and a printed page cannot be clicked.
- **AI-contribution disclosure.** `CREDITS.md` already names Claude, ChatGPT, Devin,
  and the image models. For Amazon this stops being a courtesy and becomes a required
  disclosure at upload (see D3).

### A9. Pass the dated endnote gate

`content/draft-readiness.md` gate 7: after the 14 September subpoena deadline and
before publication lock, assess whether a new public fact requires an endnote or
corrects a load-bearing claim. **No target may lock before 14 September 2026.**
`research/pachocki-alien-mind.md` (6 September) is the most recent admission; the
contract's dated-record procedure governs any further one.

### A10. Lock

Gate 9 first, then gate 8.

**Gate 9 — quote and citation verification.** Every direct quotation and every citation,
checked one at a time against its source, immediately before lock and again before each
target ships. Existence and content-match are separate questions; a quotation adds a third,
whether the wording is exactly right and whether what we call it is what it is. Each item
leaves with a disposition — quote as it stands, paraphrase, or redact. This is the gate that
lets the drafting stay on ground truth: the lossy decision is made once, late, with the
original still in hand. See [`tasks/citation-verification.md`](../tasks/citation-verification.md).

**Gate 8 — final proof and lock.** Validate source links, page metadata, reading order,
accessibility text, print dimensions, and the viewer, then move all 118 pages from `review`
to `locked`. Every target ships from the locked tree; a target that ships from anything else
is a different book.

---

## Part B — The six targets

### Target 1 — Novella on the website

**State: built and wired into CI on 6 September 2026.** The reader publishes at
`/novella/` on both the public and internal builds; `.github/workflows/pages.yml`
runs `novella.py check` before the build and `validate-novella.py` after it.

What shipped:

- A contents page, eight chapter routes, and a page anchor for all 118 story pages.
  The reading unit is the chapter; the addressable unit is the page, so
  `/novella/03-control-keeps-solving-problems/#p045` is a bookmark to [page 045](pages/045.md) and the
  page numbers the prose cites resolve to somewhere a reader can go.
- A lean prose surface — `site/novella/reader.css`, `site/novella/reader.js` — sharing
  the palette, dark/light, full screen, and fragment-carried settings with the comic
  viewer, and sharing none of its image machinery. Its own spacebar chain, so the
  viewer's "read the whole book with the spacebar alone" stays true.
- Four single-file downloads: EPUB 3 with a real page list, self-contained HTML,
  Markdown, and plain text.
- `scripts/validate-novella.py`, which fails the build if any page loses its anchor or
  gains a second one, if the contents stops reaching a page, if the reading chain
  breaks, or if a download is short of the prose tree.

**Still to do before this is finished work rather than shipped plumbing:**

1. **Continuous-prose editorial pass.** The novella was drafted one file per story
   page, and `novella.py check` deliberately enforces that shape. Read it as one
   document — `novella.py assemble --continuous` — and fix what only shows up when the
   page boundaries disappear: repeated exposition at page seams, chapter transitions
   that were page turns, and the per-page mean of 378 words creating a metronome.
   Per-page variance is already wide (134 to 562), which helps. **This is now the only
   thing standing between the novella and being genuinely readable rather than merely
   reachable.**
2. Cross-links from each novella chapter to the matching comic pages and back — not
   built, and worth having once the comic has art.
3. A cover for the reader's contents page (A8).

**Dependencies:** A1, A9, A10 for lock. Independent of all art work — **this remains
the target that ships first, and by months.**

### Target 2 — Graphic novel on the website

**State: reads end to end with SVG storyboards and existing richer candidates.** All reader slots resolve, and the controlled lettering carries the canonical text. Derive current route and image-reference counts with `validate-viewer.py`.

1. A3 art → A4 decisions → A6 lettering, panel by panel. The viewer needs no
   structural change: "Replacing a placeholder with final art is a matter of pointing
   the selected version in `assets/art/panels/NNN-II/`; the route, alt text, and
   cross-reference link do not move."
2. Fog-map presentation (A1, step 4) — the `map=` fragment setting.
3. Accessibility: confirm alt text survives the placeholder→art swap. The validator
   currently fails if a placeholder carries no alt text; make sure it fails the same
   way for real art.
4. Repository size: a bleed-cropped WebP panel is about 302 KB, and `docs/` stores
   every committed asset twice. 590 panels ≈ 178 MB source + 178 MB built. Decide
   before the run whether `docs/` keeps full-resolution art or a web derivative.
5. Cover, front matter, credits page.

**Dependencies:** all of Part A except A7. **This is the long pole for the web.**

### Target 3 — Amazon graphic novel eBook

Fixed-layout EPUB 3 with panel-by-panel navigation.

1. **A7 page compositor** — hard prerequisite. A fixed-layout EPUB is composed pages,
   not a panel feed.
2. **Panel View regions.** Kindle's fixed-layout comic format wants per-panel region
   magnification. The repository already knows every panel's ordinal and its page —
   `panels.py` and `data/panel-art.tsv` — so the region list is derivable from the
   compositor's own layout output rather than hand-authored. Build it as one emitter
   step, not a separate manual pass.
3. **`scripts/build-epub.py --fixed`**: page images, per-page XHTML with fixed
   viewport, region JSON, nav document, OPF metadata, cover.
4. Validate with `epubcheck` and preview in Kindle Previewer on every device profile.
5. Upload, complete AI-content disclosure, price, publish.

**Watch item:** at 118 composed pages plus panel regions, file size drives Amazon's
delivery fee on the 70% royalty tier. Compress deliberately; a graphic novel can
easily land in the hundreds of megabytes and eat its own royalty.

**Dependencies:** A1–A10 complete. The last target to ship.

### Target 4 — Amazon text eBook

Reflowable EPUB 3 from the novella. **The cheapest paid target by a wide margin.**

1. **`scripts/epub.py` now exists** and already emits a conforming reflowable EPUB 3
   with chapter splits, a nav document, metadata, the GPL notice, and a page list — it
   is what the site's novella download is built from. What the Kindle edition adds on
   top is a cover, the credits endmatter, and KDP's metadata, not a new builder.
2. Decide whether story page numbers appear in the prose edition at all. They are
   load-bearing in the repository and meaningless to a Kindle reader. Recommend
   dropping visible page numbers and keeping chapter structure.
3. Decide what happens to the comic's evidence apparatus — provenance labels, source
   citations, the fog map. The novella currently carries the argument in prose; if any
   apparatus is meant to survive into the text edition, that is an authoring decision
   and belongs in the A1 editorial pass, not in the EPUB build.
4. `epubcheck`, Kindle Previewer, upload, disclose, price, publish.

**Dependencies:** A1, A8, A9, A10. **Independent of all art work except the cover.**
This target and Target 1 share the same editorial pass and can ship together.

### Target 5 — Audiobook

Three routes, and the choice is genuinely consequential (see D2):

- **KDP Virtual Voice** — AI narration generated inside KDP from the published text
  eBook. Fastest and cheapest; requires Target 4 to exist first; least control.
- **Self-produced with ElevenLabs TTS**, then distributed through ACX/Audible or
  direct. Full control of voice, pacing, and pronunciation; must meet ACX technical
  specs; Audible's rules on synthetic narration must be checked before committing.
- **Human narrator** — best result, real money, longest schedule.

Work common to all three:

1. **Audio script pass.** The novella is written to be read, not heard. Needs: a
   pronunciation lexicon for handles, `ZZZ`, model names, and organization names; a
   decision on how spoken narration handles the provenance and attribution language
   that a printed page carries silently; chapter announcements; and a rule for the
   project-authored display strings on [page 118](pages/118.md).
2. Opening and closing credits, the retail sample, and the square cover.
3. If self-produced: RMS between −23 dB and −18 dB, peak no higher than −3 dB, noise
   floor below −60 dB, room tone at head and tail, one file per chapter, 192 kbps
   MP3 or better.
4. Disclose AI narration wherever the platform requires it.

**Dependencies:** A1, A9, A10, plus Target 4 if the Virtual Voice route is chosen.

### Target 6 — ElevenReader

ElevenReader Publishing accepts an EPUB and gives the book a free reading and
listening surface.

1. Reuse Target 4's reflowable EPUB unchanged. The EPUB itself already builds and
   validates as of 6 September; what it still needs is the cover and endmatter that
   Target 4 adds. **No new build work beyond that.**
2. Verify current submission requirements and rights attestations at submission time.
3. If the platform hosts audio, decide whether the Target 5 master goes here too.
4. Confirm that GPL-3.0-or-later distribution is compatible with the platform's terms —
   the licence obliges you to let readers redistribute, and a platform term forbidding
   that is a conflict you want to find before upload, not after.

**Dependencies:** Target 4.

---

## Part C — Sequence

The three phases are ordered by what blocks what, not by target number.

**Phase 1 — Freeze the book (A1, A2, A9).** Editorial work closed, trim decided, the
14 September gate passed, page count final. Nothing expensive starts until this ends.

**Phase 2 — Two forks, run in parallel.**

- *Prose fork:* site routes and the EPUB builder are done; what remains is the novella
  editorial pass, then cover and endmatter (Target 4), ElevenReader (Target 6), and
  the audiobook (Target 5). Needs no artwork beyond a cover.
- *Art fork:* A3 generate → A4 choose → A5 reference sheets → A6 letter → A7
  compositor. Twelve to forty hours of machine time plus a 67-panel manual balloon
  pass.

**Phase 3 — Converge.** Web graphic novel (Target 2) when the art fork lands; fixed-
layout EPUB (Target 3) when the compositor does. A10 lock precedes every paid upload.

**Shipping order, and it is lopsided on purpose:** Targets 1, 4, and 6 can be complete
while the art fork is still running. Target 5 follows within days of Target 4 on the
Virtual Voice route. Targets 2 and 3 arrive last, and the art fork is the reason.

---

## Part D — Decisions only you can make

These block work and have no defensible default.

**D1. Trim size.** Blocks the art run (A2, A3). Everything downstream inherits it.

**D2. Audiobook route.** Virtual Voice, self-produced TTS, or human narrator. Changes
the schedule by months and the cost by three orders of magnitude.

**D3. Selling a GPL-licensed book on Amazon.** The GPL permits sale — that is settled.
Two consequences are not:

- **KDP Select exclusivity is unavailable.** The book is public on GitHub Pages under
  GPL-3.0-or-later, so the exclusivity that KDP Select requires cannot be granted.
  That forfeits Kindle Unlimited page reads.
- **Price-matching.** Amazon reserves the right to match a lower price found
  elsewhere, and "elsewhere" here includes your own free site. A paid Kindle edition
  of a freely published book can be matched to $0.

Neither is a reason not to publish. Both are reasons to publish deliberately.

**D4. ISBN.** Amazon supplies a free ASIN, and a KDP-provided ISBN for print. A
self-purchased ISBN buys imprint identity and portability across stores. Not needed
for eBooks; needed if print ever follows.

**D5. Pricing and territory** for each of the three paid editions.

**D6. Story page numbers in the prose edition** (Target 4, step 2).

**D7. `docs/` asset policy** (Target 2, step 4) — full-resolution art in the tracked
Pages output, or a web derivative.

---

## Part E — Risks

| Risk | Consequence | Mitigation |
| --- | --- | --- |
| Trim decided after the art run | Re-render 590 panels | D1 before A3. Non-negotiable. |
| A page moves after lettering | Art, lettering, and EPUB pagination diverge | Close A1 completely; `pagination.py` protects the script, not the artifacts |
| Non-commercial model art reaches a paid edition | Licence violation on a sold book | Keep `produce.py` on `flux2-klein-4b`; audit `data/generation-log.jsonl` before every upload |
| Style drift across 590 independently generated panels | Reads as an anthology, not a book | A5 reference sheets before the bulk run; `--takes` and reference conditioning on the 59 recurring-face panels |
| Undecided art ships by default | The book sells the newest candidate rather than the chosen one | A4 before any paid upload; `panelart.py status` must read 590 decided |
| Fixed-layout file size | Delivery fees consume the royalty | Measure the composed EPUB early, not at upload |
| Platform terms shifted since May 2026 | Plan assumes stale program rules | **Verify KDP fixed-layout comic requirements, KDP Virtual Voice availability, ACX synthetic-narration policy, and ElevenReader submission terms against current documentation before relying on any of them.** The specs in Part B are as I understand them and are not a substitute for reading the current program pages. |
| A 14 September fact lands late | An endnote or a corrected claim after lock | Gate A9 is scheduled for exactly this; do not lock early |

---

## New tooling this plan requires

| Tool | Purpose | Target | State |
| --- | --- | --- | --- |
| `build-site.py` novella routes | Prose on the web | 1 | **Built 6 Sep** |
| `scripts/validate-novella.py` | Anchors, chain, downloads, EPUB page list | 1 | **Built 6 Sep** |
| `scripts/epub.py` | Chapters + page list → reflowable EPUB 3 | 1, 4, 6 | **Built 6 Sep** |
| `scripts/appendix.py` | Contested assertions and fallacies, keyed to story pages | 1, 2, 3, 4 | **Built 6 Sep** |
| `scripts/compose-pages.py` | Panels + lettering → composed page at trim size | 2, 3 | Not started |
| Fixed-layout EPUB emitter | Composed pages + panel regions → EPUB 3 | 3 | Not started |
| `scripts/build-audio.py` (if TTS route) | Audio script → chapter masters at ACX spec | 5 | Not started |

Each belongs in `tasks/` as a brief before it is written, in the shape the existing
`tasks/page-identity.md` and `tasks/panel-identity.md` briefs use.
