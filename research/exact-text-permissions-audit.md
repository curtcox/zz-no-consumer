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

**The mechanism.** `exact_strings` in a page's front matter is now a registration: `[]`, or one entry
per string carrying **text, source, locator, verification, rights**. A page in `review` may hold an
undispositioned string, with a warning. A page may not reach `locked` unless every entry is
`verbatim` against a named copy and `rights: cleared`; `quoted` is insufficient, because confirming
that a source supports a claim is not confirming that the wording is exact. Page 118's two
project-authored strings were migrated to that form and are the only registrations in the book today.

**What did not change, because it is a different hazard.** Rules 1, 2, 3 and 5 below all stand. In
particular rule 3 — do not turn a source author's paraphrase into agent dialogue — is about upgrading
an evidence class, and no rights clearance fixes it. The contract's security rule stands
independently: a visible exact string may never be operational detail however clean its rights.

**Rule 4 needs the owner's decision.** As written it forbids raw source wording in tracked research
notes without a new documented rights decision. Established practice in `research/` is otherwise —
short attributed quotations appear in several notes, and two were added on 12 September in
[`asymmetry-problem-2026-09-12.md`](./asymmetry-problem-2026-09-12.md). The new working rule makes
that practice deliberate rather than incidental, so rule 4 should either be narrowed to extended
fragments and expressive wording, or it should be enforced. It is currently neither.

## Editorial rules going forward

1. Link the controlling original publication instead of pasting a report page, screenshot, or extended fragment.
2. Attribute institutional findings and preserve disputes, evidentiary limits, redactions, and unresolved causes.
3. Do not turn a source author's paraphrase into agent dialogue.
4. Keep raw source wording in `256t/` only; do not add it to tracked research notes, prompts, generated pages, accessibility text, or promotional copy without a new documented rights decision.
5. If exact quotation later becomes artistically indispensable, reopen this gate for that specific excerpt and context rather than restoring the former set wholesale.

## Gate decision

The current canonical script no longer depends on third-party exact quotation, so quotation permission is not a prerequisite for internal page lock. Final publication review should still assess attribution, trademarks, privacy, false endorsement, and the completed artwork, but the former 23-string hold is resolved by paraphrase.
