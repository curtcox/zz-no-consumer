---
title: Make quotation the default outcome at gate 9, with a named hazard required to depart from it
status: open
proposed: 2026-09-15
proposed_by: Claude (claude-opus-5)
decision_needed_from: Curt
blocking: false
affects:
  - content/story-contract.md
  - content/draft-readiness.md
  - scripts/working_edition.py
decided:
decided_by:
---

# Make quotation the default outcome at gate 9, with a named hazard required to depart from it

## Decision requested

Approve two edits and the frozen-check change that allows them:

1. The story contract's quotation default says quotation is the expected outcome.
2. Gate 9 records a named hazard for every paraphrase or redaction.

## Why

On 15 September 2026 Curt wrote that he wants the project to be more transparent about sources and
exact quotes than agents tend to be. He wants it to go as close to what fair use allows as helps
readers and researchers see exact details and trace them to their origin. He also noted that he does
only a small fraction of the work. That direction is now recorded in `AGENTS.md` ("Lean toward
transparency") and `.cursor/rules/working-with-curt.mdc`.

The governing documents do not yet say it:

- `content/story-contract.md`, "Default editorial choices", says to quote "wherever it is
  appropriate" and to decide quotation once, at gate 9. It gives no default outcome.
- `content/draft-readiness.md` gate 9 lists three dispositions: **quote as it stands**,
  **paraphrase** or **redact**. They carry equal weight and need no stated reason.

An unweighted choice made late by a cautious agent drifts toward paraphrase. The record already shows
this happening. On 2 September a rights pass removed 23 strings as a blanket precaution. On
12 September one of those removals, page 082, was later cited as a security case. The records do not
support that reading ([correction note](../research/quotation-example-correction-2026-09-15.md);
[working-edition log, 15 September](../editions/three-stream/log/2026-09-15.md)).

Both files are frozen in `editions/three-stream/baseline.json`. `working_edition.py check --draft`
fails if either changes. Neither is published: `docs/` contains neither passage, so the site does
not change.

## Proposal

1. **Story contract, first bullet of "Default editorial choices".** Add after its first sentence:
   *"Lean toward transparency (15 September 2026): quotation is the expected outcome. Go as close to
   what fair use allows as helps a reader trace a detail to its origin. Paraphrase or redaction
   requires a named hazard."*
   The second bullet already names the two hazards that survive: the evidence-class rule and the
   security rule. Leave it as it is.
2. **Gate 9 in `content/draft-readiness.md`.** Make **quote as it stands** the default disposition.
   A **paraphrase** or **redact** disposition must name its hazard: the security rule, the
   evidence-class rule, a rights limit with its fair-use reasoning, or wording that fails
   verification. It must also keep the registration or 256t pointer to the original. General
   caution does not qualify.
3. **Frozen check.** In `scripts/working_edition.py`, add these two files to a named set of
   *governing documents* that `frozen_errors` skips, with a comment linking this proposal. Follow
   the precedent of the orientation files, approved in
   [`2026-09-13-unfreeze-orientation-docs.md`](2026-09-13-unfreeze-orientation-docs.md).
   `baseline.json` stays immutable and still records their original hashes. Add a fixture showing
   that a governing-document edit passes and a page edit still fails.

## Alternatives

- **Rely on `AGENTS.md` alone.** It is already done and needs no approval. But gate 9 is where the
  decision is made, and the contract is what invariant 9 tells every agent to read before writing a
  claim. A default that lives only in orientation can lose to an unweighted gate.
- **Amend only the working edition when its own contract is written.** This keeps the old edition's
  documents byte-identical. The gap stays open until promotion, and gate 9 runs on the live tree.
- **Re-snapshot the baseline.** Rejected, as in the orientation proposal: the baseline identifies the
  old edition.

## Risks

- A named-hazard requirement is only as good as the hazard named. Gate 9's reviewer still has to
  check that a claimed security or rights limit is real. The page 082 case shows a label can be
  mistaken for a reason.
- Loosening the frozen check for two more files could hide an unrelated edit to them. Keep the set
  explicit and small.
- Check: `python3 scripts/working_edition.py check --draft` passes after the edits, and
  `python3 scripts/validate-continuity.py` and `crossref.py check --strict` are unchanged.

## Opinions

<!-- Append entries; never edit someone else's.
### Name (product/model), YYYY-MM-DD — support | oppose | amend | question
Reasoning.
-->

## Decision

<!-- Curt's decision, or an agent's record of it quoting Curt's words and the date. -->
