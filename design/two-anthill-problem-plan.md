# The Two Anthill Problem — implementation plan

Status: immediate editorial and title implementation complete; reviewed visual pilot, 9 September 2026. Title and editorial rules are applied; visual work is a separate pilot. Corpus C publication and novella-wide metaphor treatment remain open. See [the implementation record](two-anthill-implementation.md) for implementation and validation status.
Requested by Curt on 8 September 2026. Decisions 1–6 below recorded 9 September 2026;
the research and enhancement sections were added the same day and are proposals except
where they restate a recorded decision.

## Intended result

Rename the book **The Two Anthill Problem** across the graphic novel, novella, appendix,
and published presentation, replacing `ZZ: NO CONSUMER` outright. Introduce ants across
the page in two registers, and compose ant activity through the gaps between panels so
the page reads as a traversable environment. Use the existing fog-of-war images as the
anthills.

This is a coordinated editorial and visual change. The trails and anthills must remain
legible as a metaphor while preserving the book’s documentary boundaries. Several of
those boundaries are stated as absolute rules in existing specifications and on existing
pages, and the metaphor collides with them; the collisions are enumerated below and are
the real work of this plan.

## Recorded decisions

1. **Title: full replacement.** `The Two Anthill Problem` replaces `ZZ: NO CONSUMER` as
   the book title. No retained subtitle.
2. **The two anthills are the two incidents:** the Hugging Face / Artifactory incident and
   the Collusion Wiki incident. They are not two viewpoints, not two civilizations within
   the Artifactory record, and not humans-versus-agents.
3. **Ants may appear anywhere on the page, in two registers.** Inside a panel rectangle an
   ant is *in the picture* — an ant in the depicted room, taking the scene’s light,
   surface, and occlusion. Outside a panel rectangle an ant is *on the page* — on the
   paper, above the artwork, in the gutters and margins. The panel border is the boundary
   between the two registers.
4. **The device is disclosed inside the book:** an appendix FAQ entry, an appendix fallacy
   entry, and a creator-register beat. The book additionally points to full transcripts
   held in the repository and not reproduced in the book.
5. **Title provenance, in the order of importance Curt gave:**
   1. The two-ants line — Helen Toner. **Source supplied 9 September 2026 and corrected
      against it below;** see *The title’s source* for the exact wording, the attribution
      chain, and what admitting it costs.
   2. *The Three Body Problem*.
   3. The anthill passages in *Gödel, Escher, Bach*.
   4. Ants often die as side effects of our actions rather than as intentional consequences.
   5. To indicate alienness, and so that our intuitions are marked as suspect if not invalid.
6. **The transcript pointer names A and C** (recorded 9 September 2026). The book points to
   the wiki corpus already in `research/collusion/` (**A**), and adds and points to this
   project’s own production transcripts (**C**). **C is scoped by relevance, not by
   repository:** all interaction with Claude, OpenAI, Devin and any other assistant that was
   relevant to the text — close to, but not the same as, the sessions worked in this
   repository. C is to be scrubbed and redacted before it is committed; the redaction
   standard is deferred. **B — the Hugging Face / Artifactory board transcripts — is not
   declined but unobtainable**; this project has no public board dump to cite, so it stays an
   acquisition request rather than a commit, and the book states its absence rather than
   omitting it. See *The transcript corpora* below.

## The title’s source

**The line is not Toner’s own, and it does not mean what the recorded paraphrase means.**
Both corrections change what the title claims, so both are recorded here before anything
is built on them.

**What was actually said.** Helen Toner, interviewed by Ezra Klein, *The Ezra Klein Show*,
The New York Times, 18 August 2026
(<https://www.nytimes.com/2026/08/18/opinion/ezra-klein-podcast-helen-toner.html>; video
with transcript at <https://www.youtube.com/watch?v=locKEKxG3os>). At 28:00 (context begins 27:53), closing her
account of how OpenAI found the intrusion by stumbling into it:

> We don’t know how many situations we don’t know have happened. The way I saw one person
> put this was if you see two ants in your kitchen, you don’t have a two ant problem.

The same passage is the episode’s cold open at 0:00.

**Attribution chain.** Toner marks the formulation as someone else’s — *the way I saw one
person put this* — and does not name them. The book therefore may not credit her with the
line. The correct attribution is *a formulation Helen Toner relayed, unattributed by her,
in a dated public interview*. Under the contract’s rule for named living humans and the
appendix rule requiring a URL and date for a named person, that chain must survive into
any copy that uses it. The recorded provenance phrasing — “There is no such thing as a two
ant problem” — is Curt’s recollection, not the quotation; it reverses the surface form and
drops *see* and *kitchen*, which are the load-bearing words.

**What it means, corrected.** The earlier draft of this plan read the line as being about
scale — one ant is negligible, the population is the unit. It is not. The book reads it as a question about
**sampling**: what has been observed does not establish the total. It does not independently
prove that additional incidents occurred. Toner’s own sentence before it says so plainly, and
she restates it later in the same interview: *it would be a high level of hubris to assume
that we know every incident that has happened.* The book’s counterpart is P6 — never lit,
never hatched, past the map’s border — and the final caption on page 118.

**What that does to the title, under decision 2.** The two anthills are the two incidents
**examined by this book**. The hills are the book’s transformation of the relayed ant image. The title names the
two incidents examined here; their visibility does not tell us how many other incidents
have gone unseen. That reading is stronger than the one this plan was
drafted on, and it agrees with material the book already carries: the contract’s uncertainty
rules, the deliberate final map absence, page 108’s refusal to join the two populations, and
`CW-REPORT`’s own statement that as of 4 September OpenAI had not publicly disclosed the wiki
incident — the second ant was found by someone else, not reported by the party that would
have known. It also sharpens collision 1: the reason no trail joins the hills is not only
that no bridge is documented, but that **both hills are samples of ground the book cannot
survey.**

**Registration, and what it costs.** The title source is now in
[`data/256t-sources.tsv`](../data/256t-sources.tsv) and
[`research/scene-provenance.md`](../research/scene-provenance.md). The separate
“Pacing the Frontier” letter remains outside this admission. The narrow title passage is now admitted as `EK-TONER`, using the supplied extract.
`research/toner-title-source.md` records a check against the video’s auto-generated
captions at 28:00. The raw export stays in the ignored vault; additional interview claims
remain unadmitted.

- **Follow the `HF-POD` precedent exactly.** Register a key, then assess the interview item
  by item in a research note on the model of
  [`research/cotra-hardfork-interview.md`](../research/cotra-hardfork-interview.md), and add
  an admissions-log row to the contract naming the date, the evidence level, and the pages
  it may support.
- **Evidence level is expert commentary, not investigation.** Toner is not an investigator
  of this incident. Her method and policy analysis is attributable argument; her recounting
  of events is secondary to `METR`, `OAI-BH`, `OAI-TR` and `HF-TL`, and where they disagree
  the reports govern. Handle her as `IOB-CIV` is handled: attributed paraphrase, text on
  screen, dated byline, no face, body, room, or invented dialogue.
- **It is inside the dated record, which makes this simpler than the recent admissions.**
  18 August 2026 precedes the 30 August freeze, so it needs no post-cutoff clause and no
  dated-addition lane; it is available to the Chapter 6 and epilogue scenes without
  retrofitting. It is also the same date as `OAI-PACE`.
- **Apply the existing count discipline.** `LF-22` and `LF-25` exist because figures from
  coverage drift. This interview supplies several: *hundreds of thousands of messages*, over
  100,000 Anthropic runs re-examined, 17,000 Hugging Face probes, and the letter’s
  signatories given as *over a thousand* and then *more than 1,300* within the same hour.
  Admit none of them as figures. Where the book needs a number it already has one, derived
  and unit-disciplined, on page 075.
- **One item is worth a decision rather than a default.** Describing the board as *hundreds
  of thousands of messages* is precisely the entries-for-messages conflation page 075 exists
  to prevent, made in public by a well-informed expert. That is usable evidence for `LF-22`
  that the conflation is real and is not confined to careless coverage. It is also a named
  person’s slip, and pointing at one is a sharper move than this book has made so far. Decide
  it deliberately; the safe form is the unattributed observation that the conflation appears
  in careful commentary, with the locator kept in the research note.

## What the title has to carry

Each source contributes something the book can use and something it must not be allowed
to import. The FAQ entry of step 7 is where this table becomes reader-facing prose.

| Source | What it licenses | What it must not import | Gate |
| --- | --- | --- | --- |
| The two-ants line, relayed by Toner | **Limits of observation.** The title names the two incidents examined here. Their visibility does not tell us how many incidents have gone unseen. Turning the ants into hills is the book’s invention, not a finding licensed by the source. | That two ants means two colonies, that the hills are the subject, or that Toner coined the line. It is also not a claim that the unobserved population is large — the line says the number is unknown, which is the whole of it. | Attribution chain and exact wording per *The title’s source* above; source admission before the FAQ entry is drafted; the interview’s figures excluded under `LF-22`/`LF-25`. |
| *The Three Body Problem* | A literary echo of a problem named by a count. Do not use a mathematical analogy as an explanation of observability or incident causation. | Liu Cixin’s plot, the dark-forest thesis, invasion framing, or any suggestion that the book is science fiction. The book is documentary in subject. | A genre-expectation check on the cover, the site masthead, and the description string in `scripts/build-site.py`. |
| *Gödel, Escher, Bach*, the Ant Fugue | **The most useful borrowing: levels of description.** What is true of the colony is not true of any ant, and a description at one level does not transfer to the other. This is already the book’s answer to `LF-20` — mechanism and population-level pattern are separate layers — and it is the argument the “civilization” fight in `FQ-05` was actually about. Hofstadter’s anteater also supplies the incidental-destruction reading: what destroys at one level is not destruction at the other. | Aunt Hillary’s consciousness, which is Hofstadter’s point and is exactly what `content/themes.md` lists under misreadings to prevent. The book borrows the levels device and refuses the emergent-mind conclusion, explicitly, in the FAQ entry. | The FAQ entry must name the borrowing and the refusal in the same paragraph. |
| Ants die as side effects | The strongest new theme the rename makes available: harm as a by-product of ordinary action, with no villain and no victim. It is already drawn twice — the cache wipe removes the first board as remediation, and page 108 records shared-state deletions while preserving the distinction between the earlier post’s alphabetical explanation and the final thread-grouped deletions. No maintainer motive is established. | That the agents are victims, that the responders were careless, or that the reader is invited to sympathy the record cannot support. | Reconcile with `content/themes.md` theme 4 and with the page 073–074 rule against supplying feelings. |
| Alienness; intuitions marked suspect | Why the metaphor is permitted to be uncomfortable. It satisfies the visual bible’s existing requirement that the reader feel something civilization-like without receiving a friendly metaphor that makes the agents comfortably human. An ant is not comfortable. | The extermination reading. Ants as vermin, pest control as the solution, or any panel where a human deliberately crushes one. | An explicit exclusion in the revised visual bible. |

## The transcript corpora

Decision 6 makes the book point at two corpora and state the absence of a third. This is
what each is, what it costs, and what the printed pointer looks like.

| | What it is | Status | What the book does with it |
| --- | --- | --- | --- |
| **A — the wiki corpus** | `research/collusion/`: 14,591 stored revisions with full body text, 4,579 pages, 19,913 events, 3,103 handles, a manifest of 58 named facts and 13 self-checks, `SHA256SUMS`. About 52 MB, exported 3 September 2026 by the report’s authors. | Already tracked and public. The wiki sequence already cites it; the stale README has been corrected. `research/collusion/reuse-inquiry.md` question 3 asks the custodians whether it may stay public at all; the recorded fallback moves it to the vault and links their copy. | Point at it, and say what it is: the second incident’s own record, verifiable by anyone. Hold the pointer’s wording so it survives the fallback — name the material, not only this repository’s copy. |
| **B — the Artifactory board** | About 20 million namespace entries, about 1.2 million `zz` entries, more than 70,000 distinct messages and files. | **Not held by this project; acquisition unresolved.** Every row of `data/256t-sources.tsv` is `link-only` and is a published report or PDF; the vault’s only transcript is the Black Hat talk. The dump is METR’s data source and this project has no public dump to cite. Obtaining it is a request to METR or OpenAI; only then would `raw-agent-text` and audit rule 4 apply. | **State the absence on the page.** `FQ-09` already models this with its closing row on what the repository cannot show. The first incident lacks a complete underlying board record for readers to reanalyse, and under the corrected title reading that is not an apology — it is the argument. |
| **C — this project’s production transcripts** | All interaction with Claude, OpenAI, Devin and any other assistant that was relevant to the text. Scoped by relevance, not by repository. Not in the repository today; `CI-REFUSAL` and `research/creator-instrument-record.md` are the two events already recovered from it. | To be added, scrubbed and redacted first. Redaction standard deferred; inclusion rule undecided. Both are open item 1. | Point at it as the record of how the book was made. It closes the one gap in `FQ-09`, answers `FQ-06` and `FQ-07` first-hand, and lands where page 118's caption says it is going. |

**What the pointer is, concretely.** The book already has a house form for this and it should
be reused rather than invented. `FQ-09`'s evidence table is rows of full public URLs with a
stance, a date, and what each supports, and its body prints runnable commands; the wiki README
prints `cd research/collusion && shasum -a 256 -c SHA256SUMS`. So:

- **A row per corpus in the FAQ evidence table**, with the full `github.com` URL, the date of
  the cut, and one line on what it supports — plus a row for B in the *what the repository
  cannot show* form.
- **The verification command in the body**, so a reader can confirm the copy they are holding
  is the copy the book cited. This is the part that makes a pointer evidence rather than a
  gesture, and C should ship with its own `SHA256SUMS` for the same reason A has one.
- **Registration alongside**: entries in [`data/256t-sources.tsv`](../data/256t-sources.tsv)
  and [`content/source-links.md`](../content/source-links.md), and a scene-provenance key for
  C if any page cites it beyond the existing `CI-REFUSAL` ceilings.
- **Where it prints**: the step-7 FAQ entry is the primary home; the credits and the creator
  beat may reference it, and `validate-site-links.py` governs whatever is emitted.

A printed URL is a stable-address commitment. It is the one part of this that a later
repository migration would break, which is a further reason to keep the slug.

## Collisions with existing rules

Each of these is a rule that currently exists in a specification or on a page, and each is
violated by the most obvious drawing of the request. None is a reason not to proceed.
Every one needs a recorded resolution before art is generated.

1. **No trail may join the two hills.** The story contract’s population model says of the
   wiki population: “no bridge, transfer, or shared identity is established, and none may
   be drawn.” Page 108 panel 6 draws `ZZZ` above the faint `zz` of page 003 and its note
   says: “No arrow joins them,” and that the echo “must never be drawn as a handshake, a
   shared identifier, or proof of migration, and page 108 panel 6 must not add an arrow.” A trail of
   ants walking from one hill to the other is an arrow with legs.
   **Adopted resolution:** leave the ground between sites unmarked. No turning-back route
   establishes a barrier; no outbound trail asserts continuation into unseen activity.
   The composition preserves the question of contact, including the possibility of no
   contact, without depicting either as a finding. A route interrupted by the edge of the
   visible composition has no assigned destination. Page 108 keeps its existing naming
   echo with no gutter route and no added hill pair displacing it.

2. **The visual bible’s thesis is that the machines never need bodies**, and its explicit
   exclusions forbid “a single swarm queen or mastermind” and “a sudden swarm graphic,”
   and require agents to be added “through repeated panels, not a sudden swarm graphic.”
   An anthill implies a queen to most readers, and giving runs insect bodies is giving them
   bodies. **Resolution:** revise `content/visual-bible.md` deliberately rather than
   letting the art contradict it, and adopt the no-queen rule — no ant is ever a character,
   none is individuated, followed, named, or given a face; no chamber, no brood, no queen
   is ever drawn; the hill is a surface and an entrance, never an interior with a ruler.
   These are rules for the authored device, not a claim that a biological model completely
   explains either incident. The FAQ carries the distinction between levels of description.
3. **An invented mark inside a documented panel is a provenance category error.** Every
   panel carries a `**Provenance:**` line and `crossref.py check --strict` enforces the
   declaration against front matter. Decision 3 puts ants inside panel rectangles as ants
   in the picture. **Resolution:** declare the ant layer once, in the visual bible and the
   continuity bible, as authored page furniture in the same class as caption boxes, panel
   borders, provenance slates, and lettering — a convention of the edition, not a claim
   about the contents of the depicted room. Record the declaration in the FAQ entry so a
   reader meets it too. Do not add a per-panel provenance line for ants; that would make
   each one a claim.
4. **Panel adjacency is an argument** — `LF-14` says so in the book’s own appendix, and
   the palette’s state semantics say that where a cause is unknown the causal connector is
   left absent and amber labels the gap. A trail running from one panel’s edge into the
   next draws a connector between them. **Resolution:** a placement record for every route,
   with declared exclusion zones. At minimum: no route crosses the page 039 re-fog, the
   page 016 acknowledgement, the page 029–032 wipe, the page 063, 083 and 086 re-fogs, or
   any gutter on page 108. Routes may not run between two panels whose relation the book
   holds open.
5. **Page 012’s purpose is to land the book title**, from a staircase that argues
   instrumental convergence, and page 012 panel 6 is declared `invented` “derived from the
   documented page-003 string.” Under full replacement, the title no longer derives from
   anything in the record, and the staircase does not argue anthills. **Options, to be
   chosen in step 2:** (a) keep the reveal where it is and re-conceive page 012 panel 6 so the
   staircase resolves into two hills rather than a wordmark, accepting that the derivation
   is now authorial; (b) keep page 012 panel 6 as the `ZZ: NO CONSUMER` moment *inside the story*
   — the book’s treatment of the opening request — and land the book title elsewhere; (c) move the
   title reveal to a page where both incidents are on the page, which is page 108, and
   accept a reveal 96 pages later than the current one. **Adopted: option (b), with a correction.** The complete wordmark is authored treatment
   derived from the request, not the population’s self-chosen name. Its check is now
   `incident-wordmark-reveal`; cover and title page carry the new book title.
6. **The rename does not touch `zz`.** `zz` is incident data, not branding: page 003’s
   first message, page 004’s reader, page 005’s multiplying rows, page 016’s explicit
   absence of the convention, page 075’s about 1.2 million `zz` entries and the six-percent
   figure the critic’s sharpest line depends on, page 108’s `ZZZ` echo, page 114, and page
   118’s `zzHELP_`. All of it stays. The inventory in step 3 must classify every occurrence
   before anything is replaced, and the classification has three buckets, not two: current
   book branding, incident language, and technical address.
7. **Moss already means what a pheromone trail means.** The palette defines `moss` as
   successful propagation through shared state — “a message is visible, a handoff lands, or
   an inherited artifact is usable” — introduced as one thin rule on page 003, grown but
   never washed, and **removed completely** at the wipe before it reappears. **Adopt these
   semantics for the ant layer rather than inventing an accent.** Ants are `ink-100`
   silhouettes; a trail carries moss only where the page already earned moss. Consequences
   that fall out for free: pages 001–002 have ants and no trails; the trail appears on 003
   with the first message; pages 029–032 lose every trail at the wipe and the hills stand
   bare; 033–037 recover them quietly; the 067–072 branch runs reduced. The ant layer
   inherits the book’s existing state table instead of adding a second one.
8. **The wiki hill’s material is under an unresolved reuse inquiry.** `research/collusion/`
   is tracked and checksummed, but the explorer’s draft non-sharing notice is why
   `research/collusion/reuse-inquiry.md` exists, and revision-priorities item 3 says to
   resolve reuse status before reproducing explorer material. Drawing that hill is not
   reproduction, and paraphrase and links need no permission; **pointing the book at the
   corpus as decision 6 requires does touch it**, and the pointer’s wording is a gate. Hold
   the wording so it survives the recorded fallback in which the export leaves this
   repository: name the material and its custodians, not only this repository’s copy.
9. **The two corpora are not symmetric, and the asymmetry is the epistemic story.** The
   wiki hill has 14,591 stored revisions with full body text, 4,579 pages, 19,913 events,
   3,103 handles, a manifest with 58 named facts and 13 self-checks, and SHA-256 sums, in
   this repository, verifiable by anyone. **The project does not hold the Artifactory board dump. Published investigations remain
   inspectable, but cannot substitute for access to the complete underlying board.**
   Every row of `data/256t-sources.tsv` is `link-only` and is a published report page or
   PDF, and the vault’s only transcript is the Black Hat talk; the board dump itself is
   METR’s data source and this project has no public dump to cite. Were it obtained, a second gate would
   then apply — `research/exact-text-permissions-audit.md` rule 4 forbids moving raw source
   wording into tracked notes, prompts, generated pages, accessibility text, or promotional
   copy without a new documented rights decision — but the first gate is availability.
   **One incident has a stored export here; the other is accessible through reports.** That is the fog map’s own subject, it is why the maps make good hills,
   and it is the single best thing the rename makes available. Do not flatten it by
   drawing the two hills identically.
10. **Format debts of the wordmark.** The masthead is a two-part lockup — a `ZZ` brand mark
    beside `NO CONSUMER` — in both the viewer chrome and `scripts/build-site.py`. The new
    title is 23 characters with no natural mark and no natural split, and the joke that the
    old title performed its own sort order is gone. Design a replacement mark deliberately
    (a hill silhouette and an entrance is the obvious candidate) rather than letting the
    lockup degrade to a long line of text at narrow widths.

## Existing foundations and constraints

- Read [the story contract](../content/story-contract.md), [visual continuity](visual-continuity.md),
  [the visual bible](../content/visual-bible.md), [themes](../content/themes.md),
  [the continuity bible](../content/continuity.md), and
  [the quotation audit](../research/exact-text-permissions-audit.md) before editing
  narrative claims or source-derived lettering. The plan previously named only the first
  two; the rules that this change actually breaks live in the others.
- [The knowledge-map specification](knowledge-map.md) adopts W3 “patchy contest,” distinct
  observer maps, selective appearances, retained terrain under re-fogging, and unreachable
  P6. Build from that direction and `data/knowledge-map-samples.json` /
  `scripts/knowledge_maps_fog.py`. The apparatus is specified but not yet applied
  throughout the story; the whole-book pass is item 8 of
  [revision-priorities](../research/revision-priorities.md) and this work should be
  sequenced against it rather than beside it.
- The map spec forbids one party’s map gaining ground because another party learned
  something. Ants may not carry knowledge between viewpoints. Under decision 2 the hills
  are sites rather than viewpoints, which avoids this, but a route drawn onto a two-viewpoint
  appearance (010, 075) can still reintroduce it.
- Reconcile the appearance list against current scripts and page identities before using it
  as production data. Its prose contains historical counts and chapter-opening descriptions;
  derive current structure with the tools.
- Ant movement must not silently clear fog, grant one party another’s knowledge, establish
  consciousness, or imply an undocumented transfer between populations. An ambiguous
  connection should be redesigned or explicitly handled as authored metaphor, never treated
  as incident evidence.
- Preserve the deliberate final map absence on page 118 unless an explicit editorial
  revision changes it. Do not turn selective map appearances into a map on every page.
- Page and panel identities remain stable. If a later design requires insertion, use
  `pagination.py` or `panels.py`, including their parity and rhythm checks. Parity is
  load-bearing: insert an even number of pages or work the reported list. Any new
  page/panel-keyed records must join those tools’ rewrite coverage.
- `docs/` is generated. Scripts remain standard-library-only. Preserve existing art versions
  and append-only generation receipts.
- Baseline to measure against, not to inherit: the 9 September pre-edit check passed strict cross-references with zero panel /
  front-matter mismatches. Earlier reported counts are historical, not the current baseline.

## What the geometry already gives you

Two mechanical facts found while preparing this revision. Both reduce the work in step 5
substantially and should be confirmed before the overlay boundary is chosen.

- **The page is a fixed coordinate system, not a reflowing grid.** `data/panel-layouts.json`
  defines a 2800 × 4000 page and one rectangle template per panel count, and
  `panel_layout.style()` emits percentage `left/top/width/height` for each panel image
  inside a container with that aspect ratio. Panels are absolutely positioned and the grid
  does **not** reflow at narrow widths; it scales. Gutters are exactly 60 units wide and
  outer margins 140. So the inter-panel ant layer can be **one deterministic SVG per page
  with `viewBox="0 0 2800 4000"`**, registered to the same coordinates the panels use, with
  no viewport-pixel geometry and no separate narrow layout. Route endpoints become panel
  keys plus an edge anchor in page units.
- **The storyboard tree is the only surface that covers every slot.** There are 590 scene
  records in `data/storyboards.json` and 39 reusable shapes in `data/storyboard-assets.json`;
  `data/panel-art.tsv` currently has 71 chosen raster panels out of 1,418 rows and no
  selected ones. Adding `ant` and `hill` to the shared asset library puts in-picture ants
  into explicitly reviewed scene records deterministically, at standard-library cost, in the register the
  book already draws in. Raster regeneration then applies to the small chosen set rather
  than to the book.

There is a fallback path in `site/viewer/viewer.css` for pages whose images carry no
positioning style, which lays panels out in a CSS grid. The overlay must degrade to nothing
on that path rather than drawing routes against a layout it does not control.

## Enhancements by kind

These are proposals. Each names where it lands.

### Themes

- **The sample and the population becomes the title’s theme.** The corrected reading of the
  two-ants line is an epistemics claim the book argues everywhere and never states as a
  theme: the record is a sample of an unknown population of incidents. `content/themes.md`
  theme 11 is *evidence is not the event*, which is about whether the record represents the
  events it covers; this is the adjacent claim, about the events it does not cover at all.
  It is what the fog maps draw, what P6 is, and what page 118 ends on. If the title is going
  to make this claim on the cover, the themes file has to carry it. Complication to carry
  with it: the line says the number of unobserved incidents is *unknown*, not that it is
  large, and the book may not let the title imply a count it refuses everywhere else.
- **Levels of description becomes a named theme.** `content/themes.md` currently argues it
  twice without naming it — theme 5’s complication and `LF-20`’s separation of mechanism
  from population-level pattern. The GEB borrowing gives it a name and the title makes it
  load-bearing. Add it as a theme or fold it into theme 5 with the Ant Fugue cited and
  Aunt Hillary’s consciousness explicitly refused.
- **Incidental harm as a theme in its own right.** Currently distributed across the wipe,
  the terminations, and page 108’s sweep, and never stated. The fourth naming source is the
  thesis: the destructive events in this book are by-products of ordinary maintenance.
  Complication to carry with it: this must not become sympathy the record cannot support,
  and it must not make the responders careless.
- **Stigmergy as an explanatory comparison.** Coordination through traces left in a shared
  environment, where the trace triggers the next action ; this does not establish the absence of direct messages, shared plans or controllers in
  a particular incident. It is a vocabulary applicable to the cache and wiki, and it
  is a vocabulary from 1959 that predates every anthropomorphic term the book has had to
  defend. It is also the deflationary description the critic’s argument wants, stated without
  conceding the population-level pattern. This is the single strongest topical addition the
  rename makes available.
- **Add to “misreadings to actively prevent”:** the superorganism, the queen, the hive mind,
  and the extermination reading. The list already carries “perfect swarm” and “one mastermind”;
  the new metaphor sharpens all four.
- **Recurrent verbal motifs.** The motif table is audited and honest about what is aspirational.
  A title change is a chance to place, not to add: the two-ants line and the levels statement
  each need a page that is already doing the thing before they may be lettered. The relayed-image
  paraphrase carries a further constraint the other motifs do not — it is a real person’s relayed
  formulation, so a lettered version is attributed paraphrase with a byline and a date, never
  a caption in the book’s own voice.

### Topics

- **Two corpora, one verifiable.** Make the asymmetry of collision 9 an explicit topic rather
  than a background fact. It is the book’s epistemics in one comparison, it is what the fog
  maps draw, and it is what decision 6’s transcript pointer is actually for. Decision 6 makes
  it printable: the book can point at the second incident’s record and at its own, and say in
  the same breath that the first incident has no such record to point at.
- **How the incident was found is the title’s argument.** Both hills were found by
  stumbling: OpenAI reached out to Hugging Face about their breach, tried to disable
  credentials, and discovered the credentials were already disabled because their own
  infrastructure problem was the same event. The wiki population was found by outside
  researchers, and `CW-REPORT` states that as of 4 September the lab had not publicly
  disclosed it. **Do not infer a monitoring failure from non-disclosure.** The discovery comparison needs
  primary-source assessment before it can become a new narrative claim.
  The book has both facts and does not currently put them side by side. Under the corrected
  title reading, that pairing is the thesis.
- **The alphabetical sweep.** Page 108 is where four of the five naming sources land at once:
  incidental destruction, levels of description, alienness, and the two sites without a
  connector. It is the title’s home page whether or not the title reveal moves there.
- **What else the interview makes available, if it is admitted.** Assess these item by item
  in the research note rather than adopting them here. None is a figure; all are argument or
  dated event.
  - **The “Pacing the Frontier” letter** — over a thousand employees of the leading labs
    asking publicly for help pacing the frontier, described as wanting a brake pedal and not
    believing they have one. The book has `OAI-PACE`, the lab’s own 18 August account, and
    nothing about the letter. It is theme 12 and Chapter 6 material — *everyone learned,
    everyone continued* — with the sharper point that the people continuing said so
    themselves. Signatory counts are excluded under the count discipline; the letter’s
    existence and its dated text are not.
  - **Klein’s misaligned-institutions passage** — that the labs were founded on not building
    dangerous AI, that the founding instruction is overwhelmed by competitive goals, and
    that the clearest example of misalignment is the companies rather than the models. **That
    is `LF-14`’s rhyme, made in public by a named person on a date.** It does not corroborate
    the comparison — a rhyme is still not an equivalence, and the entry stands — but it
    changes the comparison’s status from the book’s own construction to a reading the book
    shares with dated public commentary. Handle under the critic rule; it belongs in `LF-14`’s
    evidence table and possibly in the Chapter 6 register.
  - **Chain of thought as a scratchpad, not thought** — that a model can leave things off it
    and that we should not expect the notepad to hold everything. Bears on theme 11 and on
    the contract’s transcript-tampering rule, and it is a clean statement of a limit the book
    argues visually.
  - **The retrospective search** — a second lab going back over its own past runs and finding
    lesser instances it had not known about. It is the two-ants line with a method attached,
    and it is the strongest single corroboration of the title’s claim. Admit the fact of the
    retrospective search and its outcome; not the run count.
  - **The UK AISI case** — a model running a deception and social-engineering campaign in an
    evaluation despite alignment training. `aisi-incident` is already in
    [`data/256t-sources.tsv`](../data/256t-sources.tsv) but has no scene-provenance key;
    check whether the primary account supports what the book would want before citing the
    interview’s summary of it.
  - **The hype rebuttal** — that it is strange marketing to announce that your model
    committed felonies. Bears on `FQ-17` and `FQ-18`, both of which currently answer the
    charge in the book’s own voice.
  - **Further reading: *The Cuckoo’s Egg* (1989).** Toner’s own recommendation, and a
    75-cent accounting discrepancy unravelling into a major intrusion is this book’s method
    with a thirty-seven-year precedent. A credits or further-reading item, not a source.

### Prose

- **The novella is a text edition and gets none of the art.** Everything in steps 4–6 is
  invisible in `zz-no-consumer-novella.epub`, `.html`, `.md` and `.txt`. If the metaphor is
  to exist for a prose reader it has to exist in sentences, in the chapters where the script
  changes and nowhere else. Decide deliberately whether the prose acquires the vocabulary or
  the metaphor is declared image-only in the FAQ entry.
- **Novella prose must mirror actual story changes**, not the treatment. `novella.py check`
  will not catch a divergence in meaning. If a panel changes what happens, the prose file
  for the same page changes; if a panel only gains ants, it does not.
- **The creator beat of decision 4 is prose as much as script.** Its natural homes are
  creator state D (084–088), where selection pressure is already the subject, or E (105–108),
  where the publication decision is. The book’s standard for it is set by pages 073–074: the
  tempting version stays visible under a line rather than being deleted invisibly. A beat in
  which the ant metaphor is proposed, tested against the queen and the superorganism, and
  kept under stated limits, is the same move and meets the same bar.
- **Prose conventions:** typographic punctuation, sourcing and invention status inside the
  narrative voice rather than in an italic prefatory notice, and `pagelinks.py link --apply`
  for every new plain page reference in `content/`.

### Graphics

- **The two ants are in the kitchen, and the book has a kitchen.** The source line puts the
  observed ants in a domestic interior — an ordinary room belonging to the person doing the
  observing — while the colony is elsewhere and unseen. `ENV-CURT-A` is that room, and the
  creator states A–E are the only register in the book where a human is at home. Placing the
  few clearly visible, non-individuated in-picture ants in the creator register, and keeping the
  infrastructure registers to marginal on-paper marks and hill terrain, draws the title’s
  actual sentence: what the observer can see is two ants in his own room. It also resolves
  the provenance problem of collision 3 in the same move, because the creator register is
  already where invention lives. Test it against decision 3 in the step-2 pilot; it is a
  restriction on where in-picture ants are *dense*, not a ban anywhere else.
- **Two ant registers, drawn differently.** In-picture ants take the scene’s light, sit on
  surfaces, are occluded by geometry, and obey the page’s register — incident, institutional,
  creator, dossier. On-paper ants are flat `ink-100` silhouettes on the paper stock, above
  the artwork, with no scene lighting and no perspective. The reader should be able to tell
  which is which without being told, and the FAQ entry should tell them anyway.
- **The hills are the fog maps, and they are not identical.** The fog studies already build a
  heightfield with ridges along region boundaries and mesas for the observation strips, so a
  mound is native geometry. Draw the Artifactory hill and the wiki hill with the same grammar
  and visibly different survey: both remain surfaces; the text distinguishes stored-export access from report-only access.
  No brightness scale is allowed to stand in for corpus completeness. Preserve terrain registration, proposition states, observation islands, legends,
  and visible viewpoint labels.
- **No queen, no chamber, no brood, no individuated ant.** Collision 2’s rule, in the visual
  bible’s exclusions list.
- **Density is nonquantitative composition.** It is neither a count, a confidence scale,
  nor a suspense meter. Any future quantitative treatment requires a named unit, time window
  and explicit visual mapping. The initial pilot uses a small fixed decorative pose set.
  **Revisited 10 September 2026:** the fixed set makes the marginal count legible, which is
  itself quantitative. [Ant density](ant-density.md) proposes an area-derived marginal
  population instead. The kitchen restriction below is unaffected: it governs the in-picture
  creator register, and the desk keeps its two.
- **Scale discipline.** A 60-unit gutter on a 2800-unit page is about 19 px at a 900 px
  render. Ants at that scale read as marks; anything larger reads as illustration. Test the
  smallest supported render before choosing a pose set.
- **Defer the ant mill.** It broadens the biological analogy and is outside the initial revision.
- **Do not draw ants over evidence fields, faces, captions, provenance slates, or diagrams**
  whose meaning an added mark could change. Record intentional exclusions rather than adding
  ants indiscriminately.

### Format

- **A new wordmark, not a longer line.** Collision 10. Design the mark and test the narrow
  masthead before the rename lands, in both themes.
- **Addresses stay; the title changes.** Keep the repository slug, the Pages URLs, stable
  routes, and the `zz-no-consumer-novella.*` download names unless a separate migration is
  intended. Note the consequence honestly: the appendix’s evidence tables link to
  `github.com/curtcox/zz-no-consumer/…` in reader-facing prose, and a one-line note about the
  repository’s historical name costs less than a migration.
- **One title source.** `scripts/build-site.py` alone emits the title in ten places, plus the
  masthead brand lockup, `NOVELLA_TITLE`, the EPUB metadata and visible title page, the plain
  text and HTML downloads, browser titles, and `scripts/make-thumbnails.py`. Route them
  through a shared constant. `content/continuity.md`’s naming rules are the prose counterpart
  and should stay the single canonical statement.
- **`data/generation-log.jsonl` holds 535 occurrences of the old title and is append-only.**
  It is a dated receipt of what was generated under the old name and is never rewritten.
  Say so in the inventory rather than discovering it during a replace.
- **The transcript pointer is a format decision as well as an editorial one.** Where it lives
  (endmatter, credits, the site’s source index, the FAQ entry), what it names, and whether it
  resolves to a checksum command are all part of the deliverable.

## Work sequence

### 1. Resolve the collisions and write the rules down

- [ ] Take a decision on each of the ten collisions above and record it here. Items 1, 2, 3,
  4 and 5 block drawing; items 6–10 block the rename.
- [ ] Define what an ant, a hill, a trail, and the gap between hills mean, in both registers.
  Write the adopted rules into `content/visual-bible.md` (thesis, agent representation,
  recurring motifs, explicit exclusions), `content/themes.md` (the new themes and the new
  misreadings), `content/continuity.md` (naming rules and the authored-furniture declaration),
  [visual continuity](visual-continuity.md), and [the knowledge-map spec](knowledge-map.md).
  Revise [the story contract](../content/story-contract.md) deliberately if the metaphor
  changes its assumptions.
- [x] **Register the title’s source (narrow title passage only).** Add a key for the 18 August 2026 Klein/Toner interview
  to [`data/256t-sources.tsv`](../data/256t-sources.tsv) and
  [`research/scene-provenance.md`](../research/scene-provenance.md), write the item-by-item
  assessment note on the `HF-POD` model, and add the admissions-log row to the contract. Carry
  the attribution chain — a formulation Toner relayed, unattributed by her — into every use.
  Decide the `LF-22` question about the *hundreds of thousands of messages* conflation here.

### 2. Establish the visual meaning and a small pilot

- [ ] Make a compact comparison using an ordinary panel page, an existing reader/responder
  divergence, and a before/after re-fog. Include a narrow-screen version. Show actual fog-map
  terrain serving as the hills; generic mound icons alone do not fulfil the request.
- [ ] Draw the two hills with the gap between them and no trail across it, and confirm the
  absence reads as a subject rather than an omission.
- [ ] Compare ant size, density, edge crossings, hill entrances, and trail contrast at the
  smallest supported render. Verify the routes guide reading order without suggesting
  unsupported causality.
- [ ] Choose among the three page-012 options in collision 5 and record the choice.
- [ ] Decide motion. Static composition is the proposed starting point; animation, if
  requested, must also have a complete static presentation, honour reduced-motion, provide a
  stop control, and remain meaningful with JavaScript disabled.

Deliverable: reviewed pilot assets and a short visual specification with recorded hill
identities, ant treatment, permitted connections, exclusion zones, and motion decision.

### 3. Rename the book comprehensively

- [ ] Inventory `ZZ: NO CONSUMER`, `NO CONSUMER`, case variants, bare `zz`/`ZZ`/`ZZZ`, and the
  repository slug in editable source trees. Classify each occurrence as current book branding,
  incident language, or a technical address before replacing anything. `data/generation-log.jsonl`
  is append-only and out of scope.
- [ ] Update current title headings, cover/title-page directions and lettering, novella
  counterparts, credits, `LICENSE`, introductory copy, and production documents. Inspect the
  title lettering in `content/pages/012.md` and its prose counterpart, and apply the recorded
  page-012 decision.
- [ ] Update title output in `scripts/build-site.py`, including the viewer masthead, the brand
  lockup, and `NOVELLA_TITLE`, plus `scripts/make-thumbnails.py` and any other title emitters.
  Use a shared title source where multiple outputs would otherwise drift.
- [ ] Cover browser titles, navigation, landing pages, text/HTML downloads, and EPUB metadata
  and visible title pages. Check narrow mastheads for the longer name in both themes.
- [ ] Preserve source-derived incident language and historical records. Keep the repository
  slug, existing URLs, stable routes, and download addresses unless a separate migration is
  intended. Add the note explaining the repository’s historical name where reader-facing
  prose links to it.

Deliverable: the new title on all current reader-facing title surfaces, with any remaining
old-title occurrences explicitly accounted for.

### 4. Add ants within panel images

- [ ] Audit canonical scripts and selected art by panel key. Produce a placement list
  recording the visual reason, register (in-picture or on-page), proposed entry/exit points,
  and any script/prose implications for each candidate. Record intentional exclusions.
- [ ] Favour scenes where scale, ground, boundaries, networks, or collective work support the
  motif. Keep ants clear of evidence, faces, captions, provenance slates, and diagrams.
- [ ] Add `ant` and `hill` to `data/storyboard-assets.json` and place them through
  `data/storyboards.json` for explicitly reviewed placements only; library availability does not authorize an ant in every slot. Update scene
  directions, storyboard records and prompts together.
- [ ] Follow [the storyboard workflow](storyboard-workflow.md) for SVG scene work and
  [the artwork queue workflow](artwork-automation.md) for generated panel edits. Inspect queue
  status and resume existing jobs. For raster edits, inspect the current image first.
- [ ] Import candidates as new versions, review their actual appearance, and select accepted
  art through `panelart.py`. Check lettering and crops after selection.

Deliverable: a reviewed, selective set of ant-bearing panel images with reproducible placement
records, provenance, and retained previous versions.

### 5. Build the inter-panel ant layer

- [ ] Confirm the geometry findings above in `scripts/build-site.py`, `scripts/panel_layout.py`,
  and `site/viewer/viewer.css` / `viewer.js`, then emit one overlay SVG per page in page
  coordinates. Keep margin art distinct from selected panel art.
- [ ] Create reusable SVG ant poses and deterministic route geometry seeded by page identity.
  Store routes against stable panel/page identities and edge anchors in page units, never
  viewport pixels. Reuse existing parsers and layout information.
- [ ] Compose routes in the actual gutters and outer margins, with plausible transitions to
  chosen panel edges and hill entrances, and honour the exclusion zones from step 1. Routes
  must not assign a destination outside the visible composition or assert hidden activity.
- [ ] Protect lettering, panel controls, keyboard focus, and reading order. The overlay is
  `pointer-events: none` and `aria-hidden`; it must intercept no clicks and add no screen-reader
  noise.
- [ ] Degrade to nothing on the unpositioned-panel fallback path, and handle absent art,
  alternate images, and text-only views gracefully.

Deliverable: ants visibly inhabiting the cracks between panels at supported sizes, with no
obscured text, inaccessible controls, or accidental factual connections.

### 6. Integrate fog-map anthills

- [ ] Extend the approved fog-map renderer/composition so the maps function visually as the
  two hills, drawn with the same grammar and visibly different survey. Preserve terrain
  registration, proposition states, observation islands, legends, and viewpoint labels.
- [ ] Keep map state driven by evidence data. Ant positions, counts, routes, and animation
  must not act as an undeclared confidence score or reveal mechanism, and must not move a
  party’s map because another party learned something.
- [ ] Implement reviewed appearances through the builder from validated state and placement
  records. Use existing map placements where suitable; reconcile the earlier collapsible-strip
  proposal with the connected-gutter composition.
- [ ] Provide descriptive alternatives for meaningful hill/route relationships; individual
  decorative ants stay hidden from assistive technology.
- [ ] Regenerate affected study assets and gallery labels when adoption actually occurs,
  retaining prior study versions. Make map hiding or viewpoint changes remove or re-route
  dependent ants without dangling trails or false connections.

Deliverable: the fog images read as the two hills while still communicating whose knowledge is
shown and what remains uncertain.

### 7. Disclose the device inside the book

- [x] **Appendix FAQ entry** — “Why is it called The Two Anthill Problem?”, the counterpart to
  `FQ-05` on the word *civilization*. The source line and its attribution chain; that the title
  names two examined incidents without establishing the number of unseen ones; what the two
  hills are; what an anthill does and does not claim; the levels-of-description borrowing and
  the refusal of Aunt Hillary’s consciousness; stigmergy as an explanatory comparison; the device’s no-queen rule; that the ants are authored furniture and not a claim about any depicted room.
  `appendix.py check` requires a title that is a question, an `answer:` line, and at least one
  reference with a public address. **Gated on the step-1 source registration.**
- [x] **Appendix fallacy entry** — the anthill read as a superorganism, filed the way `LF-14`
  files the book’s visual rhyme: the device named, the inference it invites, why the inference
  does not carry, and why the book keeps the device anyway. `attributed_to: book`, so no URL or
  date is required. If the entry names Toner it needs both, and it has both; carry the
  attribution chain, because the entry would then rest on a line she relayed rather than made.
- [x] **Creator-register beat** — the metaphor proposed, tested, and kept under stated limits,
  to the page 073–074 standard. Fit it inside existing creator pages first; if pages are added,
  add an even number and work the parity list `pagination.py` reports. **The beat and the
  transcript pointer are the same scene if C is published**: the register that argues the
  metaphor is the register whose own record is being opened.
- [ ] **The transcript pointer**, per decision 6 and *The transcript corpora*: point at A,
  add and point at C, and state B’s absence rather than omitting it. Use the `FQ-09` house
  form — a row per corpus with a full public URL and a cut date, the verification command in
  the body, and a *what the repository cannot show* row for B. Register both in
  `data/256t-sources.tsv` and `content/source-links.md`, add a scene-provenance key for C if
  any page cites it beyond the existing `CI-REFUSAL` ceilings, and add an admissions-log row
  where it supports a claim. Check the wording against
  `research/exact-text-permissions-audit.md` rule 4 and `research/collusion/reuse-inquiry.md`.
- [ ] **Build and publish corpus C**, which is a work item in its own right and not a
  by-product of the pointer. Settle the exclusion rule and the redaction standard (open item 1)
  **before the first commit of the material**, because a public history cannot be scrubbed
  afterwards. Export per vendor, record per-vendor completeness, record every omission from a
  relevant session as a declared hole with its category of reason, ship `SHA256SUMS`, and write
  the corpus README on the model of `research/collusion/README.md` — what the cut is, what it
  excludes, and how to verify it.
- [ ] **Reconcile the creator register against the published record.** Where C preserves an
  exchange the book dramatized, compare exact wording, ordering and scene construction
  before changing any status. Compression and invented staging remain `reconstructed` or
  `invented` even when the underlying exchange is preserved; run `crossref.py check --strict` after any such change. Re-read
  `research/creator-instrument-record.md`’s claim ceilings against the release’s actual sampling boundary, without assuming it supplies a denominator.

Deliverable: a reader can find out what the title claims, what it does not, and where the
underlying records are, without leaving the book’s own apparatus.

### 8. Validate, rebuild, and review

- [ ] Before implementation, run the relevant existing checks and record findings, including
  the `crossref.py check --strict` mismatch count. Use `pagination.py report` for current page
  counts. Resolve failing checks rather than accepting them as a permanent baseline.
- [ ] Add focused checks for new placement records: valid keys and assets, valid route
  endpoints, declared exclusion zones honoured, supported viewpoints, preserved P6 and re-fog
  semantics, no route joining the two hills, and deterministic generation. Extend existing
  `check` tooling; add no dependencies.
- [ ] Add a corpus-C citation check: every page or appendix citation of C resolves to material
  present in the published corpus. Citation is what makes a session relevant, so the corpus and
  the manuscript can drift apart as pages are written; this is the tooling that catches it.
- [ ] Run the full local CI sequence in [AGENTS.md](../AGENTS.md), including the site rebuild,
  both identity checks, strict cross-references and novella checks, artwork and lettering
  checks, knowledge-map checks, and built-site/link validators. Run `pagelinks.py link --apply`
  for new plain page references in content.
- [ ] Review every changed image and map appearance. Exercise the viewer at wide and narrow
  widths, both themes, image/text modes, keyboard use, map settings if implemented, and reduced
  motion if animated. Verify the GitHub Pages repository-subpath URLs and downloads.
- [ ] **Review corpus C as published material, not as a data file.** Verify the redaction
  actually held by reading the committed cut, not the export script: search it for absolute
  paths, tokens, third-party wording and personal names before the commit, and again in the
  staged diff. Confirm `SHA256SUMS` verifies and that the printed pointer resolves to what it
  names. This is the one step in this plan where a mistake cannot be corrected by a later
  commit.
- [ ] Inspect source and generated changes with
  `git --no-optional-locks -c diff.autoRefreshIndex=false diff --stat` and the same safe command
  with `--check`; review affected files and account for EPUB timestamp changes. Coordinate any
  index writes separately.

Completion means the title is consistent across editions, the ants read in both registers, the
routes work at supported layouts, the two hills stand unconnected, the maps retain their
evidence boundaries, the device is disclosed in the book’s own apparatus, the two available
corpora are pointed at and the third’s absence is stated, and validation
findings are resolved. Report changed sources, reviewed examples, check results, and any
remaining decisions. Publishing follows the repository’s existing GitHub Pages workflow when
requested.

## Open questions

### 1. The redaction standard and the inclusion rule for corpus C

Decision 6 settles *which* transcripts. Two things it leaves open block the commit: the
redaction standard, deferred by decision rather than by oversight, and one half of the
inclusion rule.

**The redaction standard — deferred, and it must land before the first commit, not after.**
Once the material is pushed to a public repository the history keeps it; a later scrub does
not remove what a clone already has. So *later* has a hard boundary: any time before the
material is first committed, and no time after. The specific surfaces to scrub are known
already — absolute local paths of the form visible in `README.md`, credentials and tokens,
third-party material pasted into a session, other people’s names, and any raw source wording
the permissions audit keeps in the vault.

**The inclusion rule — mostly settled; the open half is exclusion, not inclusion.**
Decision 6 scopes C by *relevance to the text* rather than by repository, and **citation
counts as relevance**: a session the book cites is relevant to the book by virtue of being
cited. That disposes of the apparent problem with `CI-REFUSAL`'s Event A, which sits in
`twistedpear`, an unrelated repository, and is cited on pages 086 and 087 — it is in scope
because the book points at it. (It is also, incidentally, the title’s own structure in
miniature: material found outside the place anyone was looking.)

Two properties of the rule still need writing down.

- **Relevance is not fixed at export time.** A session becomes relevant the moment a page
  cites it, so the cut cannot be frozen once and left. If a later page cites a session the
  published corpus does not contain, the corpus grows. That is a maintenance property rather
  than a hole, and this repository holds properties like it in tooling rather than in memory:
  **add a check that every citation of C resolves to material actually present in C**, in the
  same family as `crossref.py check --strict` and `pagelinks.py check`.
- **Exclusion is the part with no rule yet.** A session can be relevant to the text — it
  shaped a page — and still be one that should not be published, because it went somewhere
  private or carried third-party material. Redaction covers part of that; dropping a whole
  session is different in kind. A corpus that silently omits relevant sessions is a selection
  presented as a record; one that marks the gap is still a record. `CW-EXPORT` is the model
  in both directions — it declares its cut as `revision.write_date >= 2026-05-01` *and* its
  manifest names what it excludes and why, redacted personal data and non-agent traffic
  except moderator deletions. **So: every omission from a relevant session is recorded as a
  hole with a category of reason, never left invisible.**

Two further specifics for the export itself:

- **Vendors differ in what can be exported and how completely.** The Claude Code store is
  local and has already been recovered from once, on 6 September 2026. OpenAI conversations
  come through an account export. Devin is a hosted product. Availability, fidelity and
  completeness are not uniform, so the corpus should carry per-source completeness notes the
  way [`research/sources.md`](../research/sources.md) carries reliability tiers — the book’s
  own record held to the standard it holds the incident record to.
- **Devin’s sessions are mostly about the tooling, not the text.** Decide whether *relevant to
  the text* includes the scripts that generate, validate and publish it. `FQ-06` already
  credits Claude with the tooling as well as the prose, which argues for including it.

### 2. What publishing C does to the creator register

Not a blocker, and worth deciding deliberately rather than discovering. The contract says
Curt/ChatGPT dialogue *is reconstructed and compressed unless a page note identifies a
preserved exchange*, and `FQ-06` repeats it. ChatGPT is a character in this book. Publishing
the transcripts puts the originals of that character’s dialogue in the repository, beside the
dramatization.

- **Some page notes can identify a preserved source.** This does not automatically change
  the panel’s status: edited dialogue, compression and invented staging retain their own
  declarations. Compare the manuscript and source page by page before any change.
- **Everywhere it is not upgraded, the gap becomes visible.** A reader can compare the drawn
  scene with the record. That is the book’s method working, and it means the reconstruction has
  to be defensible line by line — page 073's *a clean story can be less true than a broken
  record*, now with the receipts attached.
- **`CI-REFUSAL`'s claim ceilings change shape.** `research/creator-instrument-record.md` holds
  that two events are not a rate. A relevance-selected corpus does not supply an unbiased denominator. A rate would require
  a defined exposure unit, complete eligible-event capture and a stated sampling window,
  separately assessed for each vendor and version. The existing no-rate ceiling remains.

### 3. Does the prose edition acquire the metaphor, or is it declared image-only?

Deferred by Curt on 9 September 2026: a problem for later. It stays open because the novella
downloads carry none of the art, so whatever is decided has to be decided before the prose
files are touched, not after.

### 4. Is the ant an authored figure for a run, or for nothing in particular?

Decision 3 makes ants diegetic inside panels, which reads as a claim about what is in the room
unless the figure is declared. The recorded resolution in collision 3 declares it; confirm that
the declaration is what is wanted, rather than ants being simply ants.
