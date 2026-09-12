# Citation verification — standing programme and tooling proposal

**Do not build anything in the "Proposal" sections without asking Curt first.** Every item is a
proposal, not a work list. An agent that finds this file has not been authorized by finding it.

Written 11 September 2026, on a standing requirement from the owner: **citations must be checked and
rechecked many times directly in advance of publication, and the check must establish both that a work
exists and that its contents match what the book claims about them.**

## Why this is not routine hygiene for this book

The book's credibility model is that a reader can follow any claim to its source. That is not an
aspiration in this repository; it is load-bearing in four places at once.

- [AGENTS.md](../AGENTS.md) invariant 7: *provenance is enforced, not aspirational.*
- The [appendix README](../content/appendix/README.md): an answer with no address behind any of it
  "is this book vouching for its own reliability, which is the one thing the appendix exists to stop
  it doing."
- [FQ-09](../content/appendix/faq/09-check-the-work.md) is literally *can I check the work?*
- The [story contract](../content/story-contract.md) permits naming living people and organisations
  **only** through dated public actions or attributed paraphrase with the address attached.

So a dead or mismatched citation is not a typo. It is a failure of the promise the whole apparatus
exists to keep, and in a book whose subject is *evidence is not the event* it is also self-refuting.

**This has already happened once, and it is recorded.** [Item 13a](../research/revision-priorities.md)
found that [page 039](../content/pages/039.md) asserted the critique was "cited in the source index"
while **no entry for it existed** in `sources.md` or the cast. The page's `documented` provenance
rested on a citation the reader could not follow, for two days, in a finished-looking draft. That is
the failure mode this programme exists to catch, and it was caught by a human read rather than by a
tool.

## The two failure modes are different problems

Conflating them is why citation checking usually fails.

| | **Existence** | **Content match** |
| --- | --- | --- |
| Question | Does the work exist and resolve? | Does it say what we claim? |
| Automatable | Yes | **No, not in general** |
| Failure | Link rot, moved page, wrong URL, invented source | Paraphrase drift, over-reading, a claim the source does not make |
| Evidence | An HTTP response, an archive snapshot | A **locator** plus a dated record of who checked it against what |
| Decays | When the web changes | When the *claim* changes — an edit to our prose can break a verified citation without touching the URL |

The second row's last cell is the one people miss. **Content-match verification is invalidated by edits
to our own text, not just by changes at the source.** A verified citation attached to a sentence that
was later rewritten is unverified again, and nothing about the URL will show it.

## The register is per claim, not per URL

The central design decision. One URL can support several claims and be right about one and wrong about
another — `EK-TONER` is the worked example already in the repository: one passage admitted for one FAQ
entry, with the interview's chronology, counts and six other topics explicitly **not admitted**.

So rows are claims, keyed to a source, each carrying:

| Field | Meaning |
| --- | --- |
| claim site | file and the specific assertion, not just the file |
| source key | `IOB-CIV`, `EK-TONER`, `EY-STANFORD`, … |
| locator | page, section, timestamp — whatever makes the passage findable |
| level | see below |
| verified by | who or what, named |
| verified on | a date |
| claim hash | a hash of our own asserting text, so our later edits invalidate the row |

That last field is what makes the register survive editing. Without it, the register records that
someone once checked something that may no longer be what the book says.

## Quotations are rows in the same register

**Added 12 September 2026**, on a standing instruction from the owner: work with direct quotes
wherever they are appropriate, stay as close to the ground truth as possible while drafting, and
check every quote immediately before publication exactly as citations are checked — paraphrasing or
redacting then, if then is when it is needed.

This does not need a second register. A direct quotation **is** a claim about a source's content —
the strictest kind — so it is the same row with a tighter match rule. Three questions instead of
two:

| Question | Applies to | Discharged by |
| --- | --- | --- |
| Does the source exist and resolve? | every citation | `exists` |
| Does it say what we claim? | every citation | `quoted` |
| **Is the wording exactly right, and is what we call it what it is?** | **quotations only** | **`verbatim`** — a fifth level |

`verbatim` is a stricter level than `quoted`, not a parallel one: it requires a character-exact match
against a named copy of the source, and it records **which** copy. That last part is the one that
bites. A quotation checked against an automatic transcription is `verbatim` **against that
transcription** and nothing more, and the row must say so — the string may be exactly what the
transcript contains and not what the speaker said. Two rows, two different claims, and collapsing
them is how a transcription error becomes a quotation in a printed book.

**The rule this replaces, and why.** Until 12 September the working default was to paraphrase
uncertain sources during drafting. That is backwards: it applies the lossy transformation at the
moment when review is still possible, and by the time anyone reviews it the thing to review against
is gone. The reasoning is in
[`research/quotation-and-paraphrase-2026-09-12.md`](../research/quotation-and-paraphrase-2026-09-12.md).
The disposition now happens **once, late, with the original in hand** — which is what gate 9 is for.

**The machinery was changed on 12 September 2026, on the owner's instruction.**
[`validate-continuity.py`](../scripts/validate-continuity.py) used to hard-fail any page except the
last that carried anything other than `exact_strings: []` — the 2 September permissions disposition
frozen into a check, which made drafting on ground truth impossible. It now validates a
**registration**:

- `exact_strings` is either `[]` or a list of entries carrying **text, source, locator, verification,
  rights**. A bare string is an error, because a string with no source, locator or decision is what
  the check exists to catch.
- Vocabularies are fixed and enforced: `verification` in {unchecked, exists, locator, quoted,
  verbatim, derived, project-authored}; `rights` in {unresolved, cleared, paraphrase, redact}.
- A page in `review` may hold an undispositioned string and gets a **warning** naming gate 9.
- A page may not reach `status: locked` unless every entry is **`verbatim`** (or `project-authored`)
  **and `rights: cleared`**. `quoted` is deliberately insufficient — confirming a source supports a
  claim is not confirming the wording is exact. `paraphrase` or `redact` surviving to lock means a
  decision was recorded and never applied.

The emptiness requirement therefore moved from *always* to *lock*, which is where gate 9 is. Page 118's
two project-authored strings were migrated to the registered form; they are the only registrations in
the book today. All four behaviours were tested against a scratch copy before commit.

**Not done, and belonging to another tool.** The check validates the registration's *shape*, not its
*source key*. Cross-validating `source:` against `research/scene-provenance.md` and the chapter source
packets is `crossref.py`'s job — it owns the provenance graph per the
[shared-module map](../scripts/README.md#how-they-fit-together) — and is a follow-on, not a second
parser here.

## Verification levels

Four, because collapsing them is how an unchecked claim comes to look checked.

- **`exists`** — a request returned the work. Nothing about content.
- **`locator`** — a specific passage, page or timestamp is recorded. Still nothing about content.
- **`quoted`** — the claim was checked against that passage, by a named agent, on a date. This is the
  only level that discharges the content-match obligation.
- **`verbatim`** — the wording is character-exact against a **named** copy of the source, and the row
  says which copy. Stricter than `quoted`. Required for every direct quotation. A match against an
  automatic transcription is `verbatim` against the transcription and **not** against the speaker;
  the row must not blur the two.
- **`derived`** — the fact was *computed*, not read. **This level does not currently exist in the
  repository and it should, because this session created an instance of it:** `DS-GRADIENT`'s date of
  6 September 2026 was derived from an X snowflake identifier, not read off the post. The derivation
  is reproducible and probably right, and it is still not the same kind of fact as a date someone read.
  A `derived` row must record the method and must never be silently promoted to `quoted`.

`appendix.py check` should refuse a claim-bearing citation that sits at `exists` after a declared
deadline, and the publication gate should refuse one below `quoted`.

## Proposal: `scripts/citations.py`

Standard library only, per [AGENTS.md](../AGENTS.md) invariant 5. **Reuse the existing parsers** —
`appendix.py` already parses the evidence tables, `pagelinks.py` already walks references, and
`crossref.py` already owns provenance keys. See the
[shared-module map](../scripts/README.md#how-they-fit-together); a second reference parser that
disagrees with the first by one row is worse than no tool.

| Subcommand | What it does | Network |
| --- | --- | --- |
| `extract` | Inventory every external reference across `content/`, `research/`, `data/256t-sources.tsv` | No |
| `check` | Structural: every claim-bearing citation has a source key, a locator, a level and a date; fails on missing, on stale beyond a threshold, and on a claim hash that no longer matches the prose | **No — safe for CI** |
| `probe` | Liveness: status, redirect chain, final URL, content hash; writes a dated result | Yes — opt-in, never in CI |
| `snapshot` | Record an archive address beside each source | Yes — opt-in |
| `report` | Census by host, level, staleness, and unverified-claim count | No |

`check` must be network-free so it can join the CI sequence, which currently requires no credentials
and no network and should keep that property. `probe` is the artwork-generation pattern: optional
external tooling, run deliberately, results dated.

## Proposal: cadence and the publication gate

The owner's requirement is repeated checking, intensifying before publication.

1. **`check` in CI**, every push, in the sequence in [AGENTS.md](../AGENTS.md). Cheap, structural,
   catches the page-039 class of failure immediately.
2. **`probe` on a cadence** — weekly or fortnightly — with results committed as a dated record, so link
   rot is noticed as it happens rather than discovered at lock.
3. **`probe` plus a full `quoted` re-pass at page lock**, and again immediately before publication.
   Not a sample. Every claim-bearing citation — **and every quotation to `verbatim`.** This is
   [gate 9](../content/draft-readiness.md), and it is where each quotation gets its disposition:
   quote as it stands, paraphrase, or redact.
4. **A publication gate**: the build refuses to produce a release while any claim-bearing citation is
   below `quoted`, any quotation is below `verbatim`, either is stale past its threshold, or a claim
   hash does not match the prose. Six targets ship from one locked tree, so the gate runs at lock and
   again per target — a clearance is only good while the tree has not moved.

Item 3 is the expensive one and it is the one the owner asked for. It cannot be automated away, because
`quoted` requires someone to read the passage and the claim together. What tooling can do is make the
list short, current, and impossible to lose track of.

## Measured state of the tracked vault, 11 September 2026

`sync-256t.py check` fetches every manifest URL and compares the body hash against the last local
snapshot. It was run on 11 September 2026, after the Shapiro import, over **26 manifest rows**:

| Result | Count | Rows |
| --- | ---: | --- |
| **ERROR 403** | 2 | `nyt-hf-podcast`, `klein-toner-title` — both NYT. A known, already-recorded condition: [`toner-title-source.md`](../research/toner-title-source.md) says the publisher page could not be retrieved. Still true. |
| **CHANGED** | 17 | body hash differs from the last snapshot |
| **unchanged** | 7 | `metr-report`, `openai-technical-report`, `jfrog-findings`, `exploitgym-paper`, `aisi-incident`, `alabama-subpoena`, `multistate-letter` |

**Read that middle row carefully, because the obvious reading is wrong.** `CHANGED` means *this body
differs from the one we stored*. For an HTML page it can mean a substantive edit, or it can mean an ad
slot, a timestamp, a related-links rail, or a rebuilt template. **The tool cannot tell the difference,
and that is precisely the existence-versus-content-match distinction above, showing up in the one place
it can be measured today.**

Two things do stand out.

**The PDFs are stable and the HTML is not.** Every `unchanged` row is a PDF or a static page; the
controlling PDFs — METR's report, OpenAI's technical report, the multistate letter, the Alabama
subpoena — are all unchanged. **Eight of the `CHANGED` rows are the book's controlling primary
sources**: `metr-investigation`, `openai-overview`, `openai-initial-incident`, `huggingface-incident`,
`huggingface-timeline`, `metr-methodology`, `openai-pacing`, `openai-collective-defense`. Pages cite
those as `documented`. Whether any of them changed substantively is **unknown**, and finding out is
manual work on eight documents. Where a PDF and an HTML page carry the same material, **prefer the
PDF as the citation target** — this measurement is the argument for that.

**Some rows will report `CHANGED` forever, and that is a tooling defect, not a finding.** A
browser-export or owner-supplied body can never match a fetched one; a YouTube watch page is dynamic
and differs on every fetch. `shapiro-incentive-gradient`, `robmiles-pascals-mugging`,
`robmiles-respectability` and `nyt-hf-podcast-video` are all in that class. **A check that cries wolf
on four rows permanently will be ignored on the eight that matter.**

**Proposal, added by this measurement:** the manifest needs a per-source expectation flag — something
like `fetchable` / `dynamic` / `browser-only` — so that `check` reports drift only where a body-hash
comparison is meaningful, and reports the rest as *not comparable by fetch* rather than as changed.
Without it the signal is already buried at 26 sources and will be unusable at 800.

## Known hazards in the present corpus

Ordered by how likely they are to break, worst first.

| Hazard | Instances | What to do now |
| --- | --- | --- |
| **X / Twitter posts** | `DS-GRADIENT` | Highest rot risk in the corpus and not reliably archivable. Store the full text in the vault **now** — the owner supplied it on 11 September, so it exists; a link alone will not survive. |
| **Video, quoted content** | `EK-TONER`, `OAI-BH`, `HF-POD`, `RM-SANDBOX`, `RM-BOX` | Videos are deleted and captions are gated. **This session could not retrieve `RM-BOX`'s caption body at all**, in any format, though the track exists. Archive a transcript to the vault at admission time, as `EK-TONER` already does, or the claim becomes uncheckable later. Descriptions and view counts also change; record them with the date read. |
| **Paywalled journals** | C11 (*Ratio*), the Springer version of `XRISK-SKEPTIC-ANALYSIS` | `exists` is verifiable; `quoted` needs access. Prefer the open version where one exists — `XRISK-SKEPTIC-ANALYSIS` has an arXiv copy, and the arXiv and journal versions are **not automatically the same text**, so record which was read. |
| **Unresolved reuse terms** | `CW-EXPLORER` and the collusion corpus | [Item 3](../research/revision-priorities.md) is still open. A citation whose reuse status is unknown is a publication risk of a different kind and should be flagged distinctly, not lumped with rot. |
| **`located` but unread** | Twelve of fifteen entries in [the counterargument survey](../research/counterarguments-survey-2026-09-11.md) | Every one is at `exists` or below. None may be paraphrased on a page. The survey says so; the register should enforce it. |
| **Substack, blogs** | `IOB-CIV`, C3, C9 | Moderate rot. Snapshot. |
| **arXiv, DOI** | Most of the theory corpus | Most stable. Still needs `quoted`. |

## What to do first, if any of this is approved

In this order, because the first item is small and prevents an unrecoverable loss:

1. ~~**Vault the `DS-GRADIENT` text and the metadata read on 11 September.**~~ **Done, 11 September
   2026.** Manifest row `shapiro-incentive-gradient` added to
   [`data/256t-sources.tsv`](../data/256t-sources.tsv) and the body imported through
   `sync-256t.py import --captured-via owner-supplied-text`, which is the documented path for a source
   a publisher blocks from archival fetch. The record carries a sha256, the capture method, and a
   header recording the date derivation, the incompleteness of what was verified, and the disposition.
   The manifest row is tracked; the body is not, per the vault rules. Two things were **not** verified
   and the record says so: whether the supplied text is the complete post, and whether it is a single
   post or the head of a thread.
2. **Add the `derived` level** and mark `DS-GRADIENT`'s date with it.
3. **Build `extract` and `report`** and look at the census before designing anything further. The
   appendix alone carried **793 linked references across 88 hosts** on 11 September 2026
   (`appendix.py report`); the shape of that inventory should drive the rest, and it may well show that
   the hazard is concentrated in a few dozen claims rather than spread across all of them.
4. Only then `check`, the claim hash, and the gate.
