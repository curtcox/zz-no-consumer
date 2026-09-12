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
