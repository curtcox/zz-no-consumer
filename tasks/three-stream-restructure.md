# Graphic novel restructuring plan: incident streams, then collaborating actors

Planning draft, 12 September 2026. No manuscript migration is authorized by this
document alone. This task plans the graphic novel; rewriting the novella, appendix,
and other dependent editions is deferred. Open editorial questions are listed below.

Implementation was subsequently authorized by the owner's request to implement this
task. Work and remaining findings are recorded in
[`editions/three-stream/README.md`](../editions/three-stream/README.md).
The initial condensed chronology was rejected as insufficiently detailed and is
withdrawn as a manuscript candidate. It supplies no page-count target. The rewrite
must proceed from the detailed source-panel inventory and expand to retain the full
causal sequences, failures, responses and counterexamples.

Owner clarification during implementation: actor row order is **Curt, Codex, Claude**.
Curt's entrance begins with Twitter posts to be determined by later research. Codex
and Claude activity is to be established from this Mac, one other Mac, and the GitHub
repository. Preserved product identities must not be substituted for one another.
The other Mac's records are collected with
[`other-mac-production-records.md`](other-mac-production-records.md).

Owner decisions, 13 September 2026:

- **The collaboration movement ends when the collaborators finish the book.** There is no
  earlier cutoff date. The production ledger is therefore collected incrementally and
  re-inventoried until completion; the restructuring work itself is production history.
- **No fictional coda.** The book closes on documented developments and the
  collaborators' work, with unresolved questions intact.
- **Commit metadata does not identify the authoring agent.** Curt switches among agents,
  and the committing agent (often Devin, sometimes Curt by hand) is frequently not the
  one that wrote the change. Commits establish when repository state existed; session
  transcripts establish who authored it. Do not infer Codex or Claude participation from
  a commit's author, committer or trailers alone.

Working rule for analysis in the collaboration movement, 13 September 2026: an analytic or
interpretive point enters a collaborator's row only as the dated act that produced it.
Resolve each point by the first case that applies:

1. A preserved message or file change made the point: place the beat at that record's time,
   in that actor's row, and show the artifact rather than summarizing it in a caption.
2. The point exists only in an old script panel: the act is the writing of that panel, at
   its origin commit's window and by the session that typed it. A later correction by
   another actor is a separate beat with its own record.
3. The point was produced during the restructuring itself: it is collaboration material at
   its own dated time, since the movement runs until the book is finished.
4. No act can be found: the point stays out of the rows and waits for the deferred appendix
   and novella resynchronization. Do not attach it to an unrelated record's clock, and do
   not add a narrator layer outside the rows.

`scripts/production_history.py` finds origin commits and typing sessions (`panel`, `commit`);
`scripts/working_edition.py audit` lists beats that do not yet satisfy this rule.

## Governing form

- Pages advance chronologically, without the existing cold open and rewind.
- Every page shows its beginning timestamp at upper left and ending timestamp at
  lower right. Every depicted event falls within that interval.
- Every page has exactly three rows. The first movement follows three incident streams;
  the second follows three collaborating actors: Curt, Codex, and Claude. Row identities
  change once at an explicit transition on a page boundary. Within each movement, their
  order stays fixed. Panels within each row advance left to right.
- Empty intervals remain empty panels or empty rows. A quiet stream never lends its
  row to a busy stream. No decorative activity, invented reactions, or repeated events
  fill the space.
- Row order does not establish the order of events across rows. Page bounds are shared;
  panels in different rows need not represent the same instant. Panel timestamps clarify
  interleaving when necessary. Explain this reading convention once, outside the action.
- Page count grows to fit the complete story. The existing 118-page count, measured
  with `pagination.py report` on 12 September 2026, is neither a target nor a ceiling.
- Confirmed by the owner: begin with incident history. Curt, Codex, and Claude enter
  only from the specified Twitter break onward, as the second set of three rows.
- Confirmed by the owner: HuggingFace includes the complete Artifactory prehistory and
  later OpenAI infrastructure branch. Use late July–early August as the provisional
  creator-entrance planning window; the owner's exact first-view date is unknown.

## Provisional stream definitions and order

These are findings from the repository's existing research, not a new verification of
the external sources. Confirm the qualifying first event for each stream before fixing
the order in the new contract.

| Row | Stream | Earliest event in the local record | Scope |
| --- | --- | --- | --- |
| Top | HuggingFace | 20 April 2026, 07:59 UTC: Artifactory file write | Confirmed: training-era prehistory, July attack, and later OpenAI infrastructure branch. Investigation and responses remain covered; after the transition they enter through the collaborators' dated work. |
| Middle | GemStuffer | 5 May 2026: earliest package attributed by September researchers | Registry activity, effects on maintainers, package analysis, relevant remediation, later attribution and responses. Attribution remains attributed. |
| Bottom | Collusion Wiki | Exported events begin 17 May 2026; held revisions begin 24 May | Check the earliest event's type and relevance before treating it as the stream's first incident event. Include the four self-hosted wikis, moderation, investigation, and September reporting. |

Sources: [incident timeline](../research/timeline.md),
[GemStuffer assessment](../research/gemstuffer-2026-09-12.md), and
[wiki corpus guide](../research/collusion/README.md).

The July OpenAI account also mentions a RubyGems attack chain. Do not transfer that
scene to GemStuffer merely because it names the same service. Record the evidence for
its stream assignment and any supported relationship separately. Likewise, wiki/package
file overlap does not by itself establish shared agent identity or coordinated action.

## The transition to Curt, Codex, and Claude

The owner proposes that incident action has finished by the Twitter break. The local
timeline puts Hugging Face's first disclosure on 16 July, later OpenAI infrastructure
activity on 19 July, and OpenAI's first admission on 21 July. The entrance research below
supports a public-discussion anchor on 21–22 July, with Curt aware by 6 August according
to his recollection. Plan his entrance in late July–early August, visibly reconstructed;
do not claim a recovered first-view timestamp or insist that he recover a forgotten tweet.

This proposed window follows the last currently listed intrusion action on 19 July.
It does not mean all responses had finished: the local record includes quarantine on
25 July, later remediation, investigation, and September attribution. Preserve those
developments through the collaboration movement as specified below. Check the completed
event ledger for any additional active incident events before fixing the transition.

The final incident page and first collaboration page share a clear chronological boundary.
Keep three rows, the two corner timestamps, chronological reading, and intentional blanks.
Change the row labels visibly at the page turn. This is a change in subjects, with no
implied identity or inheritance between an incident stream and the actor occupying its
former position. Do not create a fourth row or alternate back and forth between row sets.

Confirmed actor order is Curt, Codex, Claude, as explicitly fixed by the owner during
implementation. It does not depend on first-known participation. A row remains empty until
its actor first participates. Do not backdate participation to fill the new layout.

The second movement tells collaboration through observable work: questions, assignments,
research, edits, proposed interpretations, checks, disagreements, corrections, and decisions.
Assign a panel to the actor performing its central action. A request belongs to its sender;
the response belongs to its responder at the response time. Use message times and shared
artifact references where needed to make exchanges across rows legible. Do not invent
direct Codex–Claude communication when Curt or a file mediated the exchange.

Later reports, attribution, remediation updates, and public responses enter as dated
material the collaborators encounter and work on. Record publication time separately
from their encounter time; do not imply they read a report immediately on release.
Earlier incident facts can be examined as records without restarting the incident action.
The reader has seen the events; now the collaborators must discover, interpret, and tell
them with the evidence actually available to them.

Codex and Claude are the named collaborating systems for this version. Revise the existing
ChatGPT-centered character and dialogue plan deliberately. Preserve actual product/model
identities in source records and quotations; do not relabel a preserved ChatGPT exchange
as a Codex exchange. Reconstructed collaboration remains visibly reconstructed. Changes
to the character contract and visual rules belong to the later implementation pass.

### Entrance evidence and recollection

Owner's wording, retained from this planning conversation:

> I don't know when the story first broke on Twitter. My guess is some time in August.
> I listen to This Week in Tech and This Week in Tech intelligent machines. I was already
> well aware of it whenever it broke there, but I don't think they were all that much
> behind Twitter -- possibly as much as a week, but my guess is less.

The owner also identifies these two videos as points by which he already knew:
[Ryan Greenblatt interview](https://www.youtube.com/watch?v=-RXD4bTuFTo), 11 August,
and the [Black Hat recording](https://www.youtube.com/watch?v=87DyyMV0kCY), 6 August.
His qualification about the earlier point is preserved verbatim:

> but I had probably known about it for days not weeks a that point.

Public-source check during this planning pass:

| Date, 2026 | Anchor | What it establishes |
| --- | --- | --- |
| 21 July | [OpenAI disclosure](https://openai.com/index/hugging-face-model-evaluation-security-incident/) | The company publicly attributed the incident to its models. |
| By 22 July, 04:20 ET | [Dated Techmeme snapshot](https://www.techmeme.com/260722/h0420) | Captures incident discussion on X, including OpenAI, Altman, and Delangue posts. This is evidence of circulation by then, not proof of the first tweet. |
| 22 July | [Intelligent Machines 880](https://twit.tv/shows/intelligent-machines/episodes/880) | The episode page dates coverage of OpenAI's responsibility to this day. |
| 26 July | [This Week in Tech 1094](https://twit.tv/shows/this-week-in-tech/episodes/1094) | The episode page lists the incident in its topics. |
| 5 / 6 August | [OpenAI's dated chronology](https://openai.com/hugging-face-incident-and-misalignment/) | Distinguishes the Black Hat presentation on 5 August from the recording's publication on 6 August. |
| 11 August | [Dwarkesh's Ryan Greenblatt episode](https://www.dwarkesh.com/p/ryan-greenblatt) | Publisher page confirms the interview date and links the supplied video. |

The X posts linked by Techmeme include
[OpenAI](https://x.com/openai/status/2079658951264920020) and
[Sam Altman](https://x.com/sama/status/2079661132302995790). Direct retrieval returned
403 in this pass; rely on the dated snapshot for the limited circulation claim, not a
purported direct inspection of either post. Exact source wording and timestamps would
need capture before a specific tweet is lettered in the script.

Keep three dates separate: public disclosure/discussion, Curt's first awareness, and the
start of collaboration on the book. The podcast release dates do not establish when Curt
listened. His recollection of knowing before their coverage and his estimate of only days
before 6 August do not identify one unambiguous date. Retain both without forcing a match.

Editorial working assumption: late July–early August, using 21 July–6 August as a useful
planning bracket, not a verified bound on personal awareness or a finished page interval.
The final page matrix must give the reconstructed entrance an explicitly marked date or
range and place subsequent scenes consistently; it must not invent a precise timestamp.
No claim that Curt read Altman's or OpenAI's particular post is admitted. His first
awareness also does not establish that Codex or Claude was already working on this book.

## Work sequence

### 1. Preserve the old edition and define the working boundary

Record the baseline commit and preserve a recoverable complete edition, including its
manifests, source registrations, scripts, prose, references, and artwork selections.
Use an isolated working edition for the restructuring; do not leave the published tree
half migrated. Keep frozen dependents explicitly tied to the old edition's identities.

Inventory every consumer of page/panel identity. Divide the inventory into graphic-novel
essentials and deferred dependents. The new script, page manifest, panel structure,
provenance, layout, lettering, and a readable graphic-only preview are essential. Novella,
appendix, downloads, ancillary studies, and their old references remain deferred.

Existing identity tools deliberately rewrite both editions together. Before any migration,
extend their shared model to support an explicitly scoped working edition and a dry-run
mapping, or an equivalent isolated-root migration. Preserve the existing default behavior.
Do not hand-renumber files, skip the rewriters, or disable the main edition's validators.

Deliverable: baseline record, dependency inventory, and a tested isolation/migration design.

### 2. Build an event ledger independent of page numbers

Inventory the current script panel by panel, then add the wiki and GemStuffer material
needed for complete coverage. Break existing montages and argumentative scenes into
individual events, claims, and interpretive beats before allocating new pages.

Each ledger entry records:

- A stable event/beat identifier, movement, incident subject, and row owner (incident
  stream in the first movement; collaborating actor in the second).
- Event start/end, original time zone, normalized UTC bounds, precision, and uncertainty.
- Source publication/availability date, citation key, exact locator, and evidence status.
- What changed, who acted, and which claims remain disputed or unknown.
- Existing source panel identities, quotation registrations, and reusable artwork, if any.
- Narrative purpose and disposition: retain, split, combine, rewrite, or omit with a reason.

Separate an event from a later report about it. May actions belong in May; September
attribution belongs in September. An earlier scene can use later evidence, with its source
status visible where needed, but its characters cannot know the later report. A September
panel can show people examining an old record; it must read as a September act of review,
not an unmarked replay of May action.

Admit GemStuffer sources to the story registry deliberately, retaining the assessment's
limits on attribution, attempted versus successful theft, and unresolved dates. For the
wiki, select representative sequences plus consequential exceptions; “complete story”
does not mean drawing every stored revision. Maintain a coverage table for the important
phases and claims so selection is reviewable.

Deliverable: sourced ledger and complete disposition list for the old script.

For the collaboration movement, also inventory preserved project exchanges, commits,
drafts, and correction records. Record actor identity and send/receive times where known,
distinguish parallel work from sequential handoffs, and identify which scenes require
reconstruction. Keep incident evidence separate from evidence of the book's production.

### 3. Establish timestamp and blank-space rules

Use UTC for the page clock. Retain source-local times in provenance. Show dates without
invented seconds when the source supplies only a day; mark approximate times and ranges.
Where sources disagree, retain both and explain the disagreement rather than selecting
the more convenient chronology.

Use nondecreasing, ordinarily nonoverlapping page intervals. A shared boundary does not
duplicate an event. Equal-time events can span adjacent pages if the record cannot order
them, with simultaneity made explicit. Never fabricate subsecond times to make pages sort.
Events known only to a broad interval need a page wide enough to contain that uncertainty,
or a later dated report panel. If that creates an irresolvable ordering problem, flag it
for editorial decision rather than silently imposing an order.

Proposed default geometry: three equal-height rows, each with one to three panel positions
as the action needs. Test two positions per row as the ordinary six-panel form; do not
make that a ceiling. Empty positions have no art or lettering. Stream labels and page
clocks live in the page furniture. A one-time legend explains that a blank means no event
depicted from the available record, not proof of inactivity.

Deliverable: revised page grammar and explicit clock/empty-slot metadata specification.

### 4. Allocate chronological page windows

Merge the event ledgers by event time within each movement, preserving within-row order. Start a new
page when the busiest row needs more room for readable action or lettering. The sparse
rows stay sparse. Page intervals can span seconds, hours, or days; chapter breaks can
skip periods with no selected events. Do not add entirely empty pages just to count days.

First lay out the whole chronology as a matrix: movement, beginning, ending, three named
rows, narrative purpose, and evidence questions. Use temporary window
identifiers, not hand-assigned canonical page numbers. Derive the total after the matrix
fits the story, then expand further if script or thumbnail review reveals crowding.

The chronological passes to cover are:

| Period | Material to allocate, subject to verified dates |
| --- | --- |
| April–early May | Earliest qualifying events and necessary context; empty rows before their first events. |
| May | Artifactory notes and responses; GemStuffer publication burst, maintainer response and Socket analysis; first wiki events. |
| June | Coordination, moderation and adaptation in the wiki; further package activity; Artifactory access expansion and warning signs. |
| Early July | Wiki's last held revisions and later moderation/probes; outage, rebuild, resumed workloads; relevant RubyGems remediation. |
| 8–13 July | Dense board and intrusion chronology, refusals and experiments at their supported times, defenders' actions, coordinator stop, and containment. |
| Mid–late July | Later OpenAI branch, evidence collection and disclosures; position the Twitter transition only after its date is settled. Later developments enter the collaboration movement through dated encounters. |
| August | If after the transition: Curt, Codex, and Claude work with available investigation reports, public arguments, institutional decisions and documented oversight actions. |
| September | The collaborators encounter wiki and GemStuffer reporting, compare evidence, examine responses, and revise the book. |

Rebuild chapters as consecutive date ranges after this pass. Retire the existing
population-based chapter allocations; retain population distinctions as evidence labels
inside the HuggingFace row. Do not manufacture a synchronized climax for all streams.

Deliverable: complete page-window matrix with a derived count and coverage report.

### 5. Rewrite the script for the new form

Rewrite scene by scene from the ledger. Do not merely shrink an old full page into a row.
Replace the prologue/rewind with forward chronology. Move the wiki action out of the
epilogue and into its dates; keep its discovery and attribution later. Give GemStuffer a
complete causal account with its own actors and consequences.

Introduce Curt at the selected Twitter moment and begin the collaboration movement.
Give Codex and Claude their own rows, entering when their dated participation begins.
Apply the transition and exchange rules above. The new structure replaces creator
interludes embedded in incident rows with a sustained account of the three actors' work.

Move retrospective analysis and interpretive diagrams into dated acts of investigation,
publication, or creator discussion. Undated montages need decomposition. Proposed treatment
for the invented hearing: preserve its strongest questions in dated creator discussion or
documented oversight scenes, without depicting a hearing as a historical event. The
existing deliberately misleading ranking/reveal requires a fresh decision; do not preserve
its old page choreography automatically. Reconsider the two-incident title after the new
three-stream narrative exists.

The undated fictional future ending is retired (owner decision, 13 September 2026). Close
on the latest selected documented developments and the collaborators' work, with
unresolved questions intact. No fictional coda.

Keep source wording and quotation registrations through the rewrite; apply the existing
late quotation gate. Retain consequential contradictory evidence and counterexamples.

Deliverable: complete new graphic-novel script, with no unassigned old beats or new stubs.

### 6. Adapt layout and identity tools, then produce a readable preview

Represent page bounds, movement, its approved row order, row membership, panel order, and intentional empty
slots explicitly. Distinguish empty layout slots from missing scripts and missing artwork.
Replace assumptions that every slot requires an event, image-generation job, provenance
claim, or lettering. Preserve the standard-library-only toolchain.

Extend existing shared parsers and identity owners rather than adding competing page
parsers. Add a reviewed bulk migration path if current single-page/single-panel operations
cannot express the many-to-many restructuring. Have it print all mappings before applying.
Retain immutable art versions and historical generation records; reuse art only after its
new event, composition, and time bounds are checked. No bulk artwork regeneration is
required to establish the script and layout.

Use a graphic-only preview from the working edition. Keep the ordinary published edition
and its full CI coherent during the transition. When the graphic novel is ready, promotion
must either present deferred material as an explicitly separate old edition or withhold
it from new-edition navigation until resynchronization. Never resolve an old prose link
to a new scene solely because it has inherited the same number.

Deliverable: generated, readable three-row preview and deterministic identity mapping.

### 7. Verify the entire graphic novel

Establish relevant baseline checks before implementation and rerun them afterward. Add
meaningful checks for the new invariants:

- Exactly three rows in the approved fixed order for each movement, with exactly one
  explicit change from incident subjects to collaborating actors at a page boundary.
- All depicted events contained by the visible bounds; pages and each row chronological.
- Uncertain and conflicting dates represented without false precision or invented order.
- No creator appearance before the chosen entrance; no later knowledge acted upon early.
- No actor participation or communication invented merely to fill a row; preserved
  exchanges retain their actual identities and reconstructed scenes are identified.
- Intentional blanks stay empty and are accepted by layout, artwork, and lettering checks.
- Every required ledger beat assigned; each omitted old beat has a recorded reason.
- Sources, quotation registrations, and evidence limitations survive redistribution.
- Old identities map without silent loss; frozen dependent files remain unchanged.

Review representative thumbnails early: a page with only one active stream, a busy
three-stream page, a seconds-long sequence, uncertain dates, the Twitter entrance, and
the September disclosures. Then read the entire new script and preview in page order.
Check clock legibility at print size and on screen, row recognition without color, blank
space, lettering fit, and recto/verso page turns. Rebuild reveals from the new chronology;
never reorder facts to rescue an old turn.

Deliverable: a fully readable graphic novel with passing scoped checks and all remaining
editorial findings explicitly recorded. Full cross-edition synchronization is a later gate.

### 8. Hand off deferred resynchronization

Export a many-to-many mapping from old edition/page/panel to stable event identifiers and
new edition/page/panel. Include split, merged, new, and removed material, with reasons and
source registrations. Store the frozen edition identifier alongside every old key.

Provide the measured final page count, revised chapter map, source admissions, and the
dependency inventory. This is the handoff for later novella and appendix rewriting,
reference repair, ancillary asset migration, and combined-site rebuilding. Do not attempt
those rewrites as part of the graphic-novel restructuring.

## Confirmed decisions and remaining questions

Confirmed: start with incident history; include the complete HuggingFace/Artifactory
history; continue from the Twitter break with Curt, Codex, and Claude as three collaborating
actors. The former proposal to retain incident rows for creator scenes is superseded.

The ending is settled: documented developments, no fictional coda.

The Twitter entrance remains open for implementation research under the owner's
subsequent clarification. The documented circulation and recollection above are
planning context; they do not identify a post Curt read. Continue independent
incident and production work while the source posts are determined. Do not assign
a specific post or first-view time merely to close the page matrix.

Actor order is confirmed as Curt, Codex, Claude. Participation dates determine when
their rows gain content, not their order. No canonical page numbers or dependent files
have been changed.
