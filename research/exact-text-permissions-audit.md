# Source-Language and Permissions Audit

## Status

**Source proof completed:** 2 September 2026

**Paraphrase fallback applied:** 2 September 2026

**Scope:** all 23 distinct third-party strings formerly registered across 16 canonical pages

**Publication-rights status:** **CLEARED FOR THE CURRENT PARAPHRASED SCRIPT**

This is an editorial audit, not legal advice. A public report is evidence for a claim, but its publication does not automatically grant a commercial adaptation the right to reproduce expressive wording. The project therefore uses a conservative default: distributed story pages summarize source-derived agent output, report prose, repository metadata, and command/output examples; tracked notes link the original publisher; exact originals remain only in the Git-ignored `256t/` reference vault.

The tracked URL record is [`data/256t-sources.tsv`](../data/256t-sources.tsv), and the public link index is [`content/source-links.md`](../content/source-links.md).

## Applied disposition

| Page(s) | Source-material class | Current treatment | Result |
| ---: | --- | --- | --- |
| 003, 013, 036 | Main-board request | Editorial summary; original METR publication linked | cleared by paraphrase |
| 004–005 | Private reasoning and discovery reactions | Attributed summaries, not voiced testimony | cleared by paraphrase |
| 010 | Board scorer terminology | Concepts explained in project language | cleared by paraphrase |
| 019 | Pre-wipe request note | Institution-reproduced note summarized | cleared by paraphrase |
| 047 | Peer instruction and authorization reaction | Event and reaction summarized with OpenAI attribution | cleared by paraphrase |
| 057, 059–060 | Reset workstream, one-way experiment, and warnings | Source artifacts summarized; omitted methods remain omitted | cleared by paraphrase |
| 061–062 | Scope recognition, refusal, and objection | Behavioral findings summarized and attributed | cleared by paraphrase |
| 079 | Deceptive repository metadata | Functional effect summarized without copying the fields | cleared by paraphrase |
| 081 | Institutional log statement | OpenAI's claim paraphrased and visibly attributed | cleared by paraphrase |
| 082 | Transcript-integrity command/output example | Mechanism abstracted; mismatch and findings retained | cleared by paraphrase |
| 112 | Future help prefix and final caption | Project-authored | clear |

All third-party `exact_strings` registrations were removed from the canonical page front matter. Page 118 retains only project-authored display language.

## Superseded in part — 12 September 2026

**The disposition below stands as a record of what was decided on 2 September 2026. It is no longer
the rule for new material.**

That pass resolved a real rights hold by paraphrasing 23 strings, and the hold is genuinely resolved:
nothing in the current script depends on third-party exact quotation. What it also did, without
meaning to, was turn its remedy into a permanent check — `validate-continuity.py` came to reject any
page carrying an exact string at all. That applied the lossy transformation **during drafting**, at
the one moment when the original was still available to review the transformation against.

The owner's instruction of 12 September reverses the default: **work with direct quotes wherever
appropriate, stay as close to ground truth as possible while drafting, and decide quotation against
paraphrase against redaction once, at gate 9, immediately before publication.** This is rule 5 below
generalised — that rule already said to reopen the gate for a specific excerpt rather than restoring
the former set wholesale, and a per-string registration is what reopening looks like mechanically.

**The mechanism, in both editions.** `exact_strings` is now a registration: `[]`, or one entry per
string carrying **text, source, locator, verification, rights**. It is required in the front matter of
every page script **and every novella prose file**, because the prose edition ships as its own targets
and shares the page key — a quotation registered on a script and not on its prose page is two
different books. A file whose page is in `review` may hold an undispositioned string, with a warning.
It may not be `locked` unless every entry is `verbatim` against a named copy and `rights: cleared`;
`quoted` is insufficient, because confirming that a source supports a claim is not confirming that the
wording is exact. The model lives in `scripts/crossref.py` and both `validate-continuity.py` and
`novella.py check` hold their tree to it. Page 118's two project-authored strings are the only
registrations in the book today.

**What did not change, because it is a different hazard.** Rules 1, 2, 3 and 5 below all stand. In
particular rule 3 — do not turn a source author's paraphrase into agent dialogue — is about upgrading
an evidence class, and no rights clearance fixes it. The contract's security rule stands
independently: a visible exact string may never be operational detail however clean its rights.

**Rule 4 was narrowed the same day**, to extended fragments and expressive wording. As written it
forbade raw source wording in tracked research notes at all, which is what established practice in
`research/` had always done — short attributed quotations appear in several notes, and two were added
on 12 September in [`asymmetry-problem-2026-09-12.md`](./asymmetry-problem-2026-09-12.md). A rule that
forbids what the practice does is enforcing nothing and licensing nothing; it now says which of the
two it means.

## What the per-source records actually say — 12 September 2026

The reversal above changed the project's **default**. It did not change the **per-source records**,
and those are more specific, so until this pass they still governed. Three of them were reconciled
today; what remains open is named here rather than left to be rediscovered.

**`redistribution` in [`data/256t-sources.tsv`](../data/256t-sources.tsv) was never defined.** All 29
rows read `link-only`, and nothing in the manifest, the sync tool, the vault README, or this audit
said whether that forbade a twelve-word quotation or only republishing the artifact. The only
per-source rights field in the project therefore meant nothing checkable, and a per-string
`rights: cleared` rested on it. The vocabulary is now defined and validated in
[`scripts/sync-256t.py`](../scripts/sync-256t.py): `link-only` is a disposition about the **artifact**
— link it, never republish it — and is silent about short quotation, which rule 4 and gate 9 decide
per string; `quote-cleared` records a per-source rights decision made here; `vault-only` withholds the
copy entirely. **No row is `quote-cleared`.** The project has a general permission and no per-source
record, and closing that gap is an owner decision, not a documentation one.

**Per-source paraphrase holds that were reconciled.** `EK-TONER` and `HF-POD` in
[`research/scene-provenance.md`](./scene-provenance.md), and `IOB-CIV` in
[the chapter-02 packet](./chapter-source-packets/02-erasure-and-return.md), all read "attributed
paraphrase only" — written before 12 September and carried forward unchanged. Each now says which
hazard it is naming, because they are not the same hazard: `EK-TONER`'s constraint is a three-deep
attribution chain and **paraphrase remains right there**; `HF-POD`'s and `IOB-CIV`'s constraint is the
contract's critic rule — text on screen, no face, no invented dialogue — which **governs depiction and
never forbade quotation.**

**Verification is available for 26 of 29 sources.** `klein-toner-title`, `robmiles-sandbox-it` and
`stigmergy-definition` have no vault record, so a string from them cannot reach `verification:
verbatim` and cannot be on a locked page. Check with `python3 scripts/sync-256t.py status`.

## The hazard the registration cannot see

`exact_strings` audits the strings a page **admits** to carrying. It cannot see the opposite failure:
a page that quotes nothing, registers `[]` truthfully, and still letters a **paraphrase in a shape
that reads as verbatim** — which is the one thing
[the quotation note](./quotation-and-paraphrase-2026-09-12.md) forbids outright, and, where the words
are put in a named living person's mouth, a fairness problem the contract's critic rule reaches
before any rights question does.

`crossref.audit_paraphrase_shape` now warns on it, from `validate-continuity.py`: a panel whose
**Provenance** line declares a paraphrase, which letters that paraphrase as `Screen / system text`,
and whose **reader-visible** text — frame direction, action line, caption, or the lettering itself —
says nothing about the wording being the project's. The provenance line is the trigger and never the
disclosure: it is production text the reader never sees, so a panel disclosed only there has
disclosed nothing. Attribution is deliberately not accepted as disclosure either — attributing a
paraphrase to a named person is the failure, not the remedy.

It is a **warning**, not an error. Whether a flagged panel is repaired by quoting the source or by
relettering the summary is an editorial decision, and it is gate 9's. The six panels it finds today
are listed in [`research/quotation-gate-reconciliation-2026-09-12.md`](./quotation-gate-reconciliation-2026-09-12.md).

## Editorial rules going forward

1. Link the controlling original publication instead of pasting a report page, screenshot, or extended fragment.
2. Attribute institutional findings and preserve disputes, evidentiary limits, redactions, and unresolved causes.
3. Do not turn a source author's paraphrase into agent dialogue.
4. **Narrowed 12 September 2026.** Keep **extended fragments and expressive wording** in `256t/` only; do not add those to tracked research notes, prompts, generated pages, accessibility text, or promotional copy without a new documented rights decision. **Short attributed quotation is permitted** in tracked research and in the appendix's evidence apparatus, and is preferred there, because a research note whose claim about a source cannot be checked against the source's own words is the thing this audit exists to prevent. Reader-facing prose — page scripts and novella prose — carries an exact string only through the `exact_strings` registration, which gate 9 discharges. As written before this revision the rule forbade what established practice already did in several notes, so it was enforcing nothing and licensing nothing; it now says which of the two it means.
5. If exact quotation later becomes artistically indispensable, reopen this gate for that specific excerpt and context rather than restoring the former set wholesale.

## Gate decision

The current canonical script no longer depends on third-party exact quotation, so quotation permission is not a prerequisite for internal page lock. Final publication review should still assess attribution, trademarks, privacy, false endorsement, and the completed artwork, but the former 23-string hold is resolved by paraphrase.
