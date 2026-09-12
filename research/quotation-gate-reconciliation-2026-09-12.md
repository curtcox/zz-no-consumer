# Reconciling the quotation gate with the per-source records — 12 September 2026

**Research note.** The owner's instruction of 12 September reversed the project's default from
*paraphrase while drafting* to *work on ground truth and decide at gate 9*. The default changed in
[`content/story-contract.md`](../content/story-contract.md),
[`content/draft-readiness.md`](../content/draft-readiness.md),
[the permissions audit](./exact-text-permissions-audit.md) and
[the quotation note](./quotation-and-paraphrase-2026-09-12.md). **The per-source records did not
change, and they are more specific than the default, so they still governed.** This pass reconciles
them and records what it found.

## What was in the way, and what was done

| Obstacle | State before | Now |
| --- | --- | --- |
| `redistribution` in [`data/256t-sources.tsv`](../data/256t-sources.tsv) | All 29 rows `link-only`; **the term was defined nowhere** — not in the manifest, the sync tool, the vault README, or the audit. The only per-source rights field in the project, and a per-string `rights: cleared` rested on it | Vocabulary defined and validated in [`scripts/sync-256t.py`](../scripts/sync-256t.py): `link-only` is about the **artifact** and is silent on short quotation; `quote-cleared` records a per-source decision; `vault-only` withholds the copy. **No row is `quote-cleared`** |
| `EK-TONER`, [scene-provenance](./scene-provenance.md) | "Attributed paraphrase only" | **Paraphrase upheld,** with the reason: a three-deep attribution chain, not transcription quality. No vault record, so `verbatim` is unreachable anyway |
| `HF-POD`, [scene-provenance](./scene-provenance.md) | "Attributed paraphrase only, as text on screen, never given a face…" | Restated: the critic rule **governs depiction, not wording.** Short attributed quotation permitted, labelled as automatic transcription |
| `IOB-CIV`, [chapter-02 packet](./chapter-source-packets/02-erasure-and-return.md) | "Attributed paraphrase only" | Same restatement; vault record exists, so `verbatim` is reachable |
| [Dossier](./openai-huggingface-dossier.md) scope paragraph | "does not reproduce … report prose … or other third-party fragments" — quotation of any length, in the largest research file | Narrowed to **extended** fragments, matching rule 4; short attributed quotation permitted and preferred |
| [Agent message ledger](./agent-message-ledger.md) | "does not reproduce board entries…" | **Upheld, with the reason stated:** the project does not hold the board corpus, so there is nothing to quote from at first hand |
| [Session summary, 11 Sep](./session-summary-2026-09-11.md) | "**paraphrase, do not quote**" for the video transcripts, reading as current | Struck through, with the correction quoted inline |

## The hazard nothing was checking

`exact_strings` audits the strings a page **admits** to carrying. A page that quotes nothing registers
`[]` truthfully — and can still letter a **paraphrase in a shape that reads as verbatim.** The
registration cannot see that, because there is nothing registered to look at. Until today nothing
else looked either: `crossref.audit_exact_strings` reads front matter only, and no validator read a
page body.

`crossref.audit_paraphrase_shape`, run from `validate-continuity.py`, now warns when all three hold:

1. the panel's **Provenance** line declares a paraphrase (`source-paraphrase`, or the word);
2. the panel letters it as `Screen / system text`;
3. **nothing the reader sees** — frame direction, action line, caption, or the lettering itself — says
   the wording is the project's.

The provenance line is the trigger and never the disclosure: it is production text no reader sees, so
a panel disclosed only there has disclosed nothing. **Attribution is deliberately not accepted as
disclosure** — attributing a paraphrase to a named person is the failure, not the remedy. It is a
warning, not an error, because the repair is an editorial choice and it belongs to gate 9.

## What it finds: six panels

The quotation note found the first by hand and predicted the pattern would recur "wherever a source's
argument is lettered as screen text." It recurs five more times.

**Four letter a paraphrase in a named third party's voice, under a label that reads as citation.**
Three of those name a living person, so the contract's critic rule reaches them before any rights
question does.

| Panel | Lettered as | Provenance says | Vault |
| --- | --- | --- | --- |
| [page 039](../content/pages/039.md) panel 2 | `PUBLISHED CRITIQUE` — three first-person declarative lines; the frame direction asks for "an attributed block quotation" | "attributed paraphrase of the post's … claims" | `internetofbugs-civilizations` — `verbatim` reachable |
| [page 088](../content/pages/088.md) panel 2 | `PUBLISHED CRITIQUE (PAGE 039, 3 SEPTEMBER 2026)` — one line | "attributed paraphrase of the post's claim that METR delegated analysis to often-unreliable AI agents" | same |
| [page 089](../content/pages/089.md) panel 3 | same label — two lines | "attributed paraphrase of the post's claims that logs were cherry-picked … and that OpenAI and METR had an incentive to look powerful" | same |
| [page 101](../content/pages/101.md) panel 2 | `CITED, OPENAI AT BLACK HAT` — two lines; the frame direction asks for them "in the talk's own register" | "attributed paraphrase of `OAI-BH` 30:47–31:14" | `256t/transcripts/oai-black-hat-2026-08-05-transcript.md`, and the timecodes are already recorded |

**Two are milder** — third-person description lettered as screen text, with no citation label and no
named party, so they read as the book's summary rather than as someone's words:
[page 062](../content/pages/062.md) panel 3 (`BOARD DECISION REQUESTED BEFORE CONTACTING A PERSON`) and
[page 081](../content/pages/081.md) panel 2 (`AT LEAST 96 TRANSCRIPTS SHOW CLEAR EVIDENCE OF SPOOFED TOOL
CALLS`, provenance: "METR's finding, paraphrased rather than quoted"). A word in the lettering or the
frame clears either.

**[Page 101](../content/pages/101.md) panel 2 is the cheapest to repair and the strongest case for repair by quotation:** the
speaker is an institution rather than a living individual, the vault holds the transcript, the
timecodes are already in the provenance line, and the frame direction already asks for the speaker's
own register. Quoting it would replace an imitation of OpenAI's voice with OpenAI's voice.

## Not done here, and why

- **The six panels are not edited.** The quotation note recorded that this is "an editorial decision
  for the owner, not a correction I should make unasked," and finding five more instances does not
  change whose decision it is. Each has two available repairs — quote the source, or reletter so the
  reader can see the words are ours — and the choice differs per panel.
- **No row is moved to `quote-cleared`.** Recording a per-source rights decision is the owner's, and
  the general permission in rule 4 is what the project runs on until then.
- **Three sources cannot reach `verbatim`:** `klein-toner-title`, `robmiles-sandbox-it`,
  `stigmergy-definition` have no vault record. `python3 scripts/sync-256t.py status` is the check.
- **The novella is not scanned.** The same hazard exists in prose — quotation marks around words that
  are not the source's — but prose quotation marks also carry invented dialogue throughout, so the
  page-script shape test does not transfer. The prose edition's `exact_strings` registration is
  enforced; its *shape* is not checked.

## Second pass, later on 12 September: the rules that still said "paraphrase"

After the first pass the owner asked whether anything in the repository still stood between a
drafter and a quotation, and then asked for every obstacle to be removed: "I want the auditable
truth whenever possible." Four remained, and one was enforced by a check.

| Obstacle | State before | Now |
| --- | --- | --- |
| [`continuity.md`](../content/continuity.md) source-language policy | "Distributed story pages use attributed paraphrases" for agent output, report prose, metadata and command output; **`validate-continuity.py` failed the build if the sentence was removed**. Dialogue rules and the lock checklist said the same | Policy rewritten to the ground-truth default; the check now requires the new sentence. Dialogue rules and checklist follow |
| [Story contract](../content/story-contract.md), named living humans and the critic rule | "attributed paraphrases of public statements"; critics cited "through attributed paraphrase"; critiques enter "paraphrased" — contradicting the contract's own revised default | Quotation or visible paraphrase, registered and labelled. The critic rule now says in words that it governs **depiction**, which the first pass asserted and the contract did not |
| Provenance vocabulary ([`crossref.py`](../scripts/crossref.py), [`validate-continuity.py`](../scripts/validate-continuity.py), [page grammar](../design/page-grammar.md)) | No status meant "these are the source's words"; `raw-agent-text` reserved for private research | `raw-agent-text` reopened and `quotation` added. Labels and treatments added to the [premise](../content/premise.md), [visual bible](../content/visual-bible.md), [lettering](../design/lettering.md) and [visual continuity](../design/visual-continuity.md) |
| Audit rule 4 | Withheld "expressive wording" from generated pages and accessibility text — so a registered quotation could be lettered but not described to a screen-reader user | A registered string travels with its panel into lettering, accessibility text, transcript and builds; it is withheld from image models and promotional copy |

Two stale design notes were reconciled rather than rewritten: the Toner paraphrase in the
[two-anthill plan](../design/two-anthill-problem-plan.md) now gives its real reason (the attribution
chain, which still holds), and the 3 September text-rendering decision in
[image-generation-options](../design/image-generation-options.md) carries a dated note that its
"no reuse question" premise no longer covers every string.

### What makes a quotation auditable, mechanically

- **A quoting status requires a registration.** `crossref.audit_quotation_shape` fails a panel that
  declares `quotation` or `raw-agent-text` when no string registered in the page's `exact_strings`
  appears in the panel. The status is a claim about wording; with nothing registered there is
  nothing to check it against.
- **An attribution-shaped label requires a registration or a disclosure.** A `Screen / system
  text` label reading `CITED`, `PUBLISHED`, `ATTRIBUTED`, `QUOTED` or `VERBATIM`, over strings that
  are neither registered nor marked `PARAPHRASED`, is a warning. This catches what the
  paraphrase-shape check cannot: panels whose provenance does not say "paraphrase" at all.
- **An image model never draws a quotation.** `imagegen.exact_text_clause` withholds registered
  third-party strings. The measured error rate for strings of quotation length is about one error
  per string; a drawn quotation would be unverifiable at gate 9.

### A bug the new check exposed in the old one

`audit_paraphrase_shape` removed only the **first line** of a panel's Provenance paragraph before
looking for a reader-visible disclosure. [Page 087](../content/pages/087.md) panel 4's provenance
wraps, and its second line contains "describing" — so a disclosure word the reader never sees
suppressed the warning. The whole paragraph is now removed. Page 087 panel 4 is flagged.

### What the checks find now: eleven panels (12 September 2026)

The six in the table above, plus:

| Panel | Lettered as | Why it was missed |
| --- | --- | --- |
| [page 087](../content/pages/087.md) panel 4 | `PUBLISHED, ATTRIBUTED` — a named investigator's caution; provenance says "attributed paraphrase" | The wrapped-provenance bug above |
| [page 039](../content/pages/039.md) panel 5 | `PUBLISHED CRITIQUE, CITING OPENAI` — a critic's report of what OpenAI stated | Provenance does not declare a paraphrase |
| [page 101](../content/pages/101.md) panels 3 and 4 | `CITED, OPENAI AT BLACK HAT` with timecodes; provenance `documented` | Provenance does not declare a paraphrase, and nothing registers the words. **Either these are quotations and are unregistered, or they are paraphrases lettered as citation.** The record does not say which, and that is the finding |
| [page 111](../content/pages/111.md) panel 4 | `PUBLISHED CRITIQUE (PAGE 039, 3 SEPTEMBER 2026)`; provenance "attributed paraphrase" | Curt's dialogue in the same panel says "report", which the old check accepted as disclosure |

None is edited. Each is register-or-reletter, and that is the owner's decision at gate 9.

### Still open

- **The novella's shape is not checked**, for the reason given above.
- **No source row is `quote-cleared`**, which blocks lock, not drafting.
- `crossref.audit_quotation_shape` reads `Screen / system text` labels. A quotation lettered as a
  caption or dialogue under a quoting status is checked; a caption that merely *looks* like a
  quotation without declaring one is not.

## Third pass: 256t pointers, and what page 101 actually letters

**Standing direction from the owner, 12 September 2026:** whenever a direct quotation cannot be
used, use a 256t pointer to it instead, per <https://256t.org/>. The motivating case is an
agent that may not reproduce more than a short excerpt of source text. Before this pass, that
limit pushed work back toward paraphrase, which is the lossy transformation this note exists to
prevent. A pointer loses nothing: it names the exact bytes by length and SHA-512, and it names
the copy they were cut from the same way.

**The mechanism.** [`scripts/t256.py`](../scripts/t256.py) implements the standard. It reproduces
all three published test vectors, and CI runs that check. An `exact_strings` entry may carry
`pointer` in place of `text`. `crossref.pointer_problems` checks, without the vault, that the URI
is well formed and that the locator names a copy and a byte range of exactly the length the
pointer declares. `t256.py verify` cuts, hashes and compares against the local vault. A panel
declaring `quotation` may carry the pointer in its lettering while in review. A page cannot lock
on a pointer alone, because a pointer cannot be printed. The tool prints only CIDs, lengths and
offsets, never source text.

**The Black Hat transcript is now a named copy.** It has no row in
[`data/256t-sources.tsv`](../data/256t-sources.tsv), so `sync-256t.py` records no URL, retrieval
date or hash for it. That gap still matters for provenance: nothing says how the transcript was
made. It no longer matters for identity, because the copy is
`t256:AAAAAKE45pOA3XgG4nJg124TkhTIVAJUPEdGNc33z3VbUEpJU93J5EDl5wtYkciVTr1ctJYXry3yMnR4WO8Wl5-XMFXDjw`
(41,272 octets, 5 September). Its form — caption-length chunks, retained fillers, "HuggingFace" as
one word — is consistent with automatic transcription. That is an observation, not a record.

**Page 101 against that copy.** The page's six lettered lines were compared with the transcript,
ignoring case, punctuation, timestamp lines and "uh"/"um". The comparison reported only whether
the words appear contiguously, and the best word-overlap ratio against any equal-length window.

| Panel | Label and provenance | Line | Words | Contiguous | Best overlap |
| --- | --- | --- | ---: | --- | ---: |
| 2 | `CITED, OPENAI AT BLACK HAT`; "attributed paraphrase" of 30:47–31:14 | 1 | 7 | yes | 1.00 |
| 2 | same | 2 | 16 | no | 0.50 |
| 3 | `CITED, OPENAI AT BLACK HAT`; `documented`, 31:32 and 36:38 | 1 | 18 | no | 0.61 |
| 3 | same | 2 | 19 | no | 0.58 |
| 4 | `CITED, OPENAI AT BLACK HAT`; `documented`, 33:17–33:52 | 1 | 12 | no | 0.33 |
| 4 | same | 2 | 11 | no | 0.91 |

So the question the second pass left open about panels 3 and 4 has an answer. **Neither is
quotation.** Panel 3's provenance never says "paraphrase", yet both its lines are paraphrase set
under a citation label. Panel 4's second line is nearly the speaker's words; its first line is
not. And one line recorded as paraphrase, panel 2's first, is in fact verbatim against the
transcript.

This is the case for doing the check mechanically rather than by reading: the provenance lines
were wrong in both directions. Nothing on the page is edited. For each line the repair is
still the owner's at gate 9: register the transcript's words (or a pointer to them) and letter
those, or reletter the summary so the reader can see it is the book's.
