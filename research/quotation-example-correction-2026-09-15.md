# Correcting the operational-detail example — 15 September 2026

**Research note.** The [quotation note](./quotation-and-paraphrase-2026-09-12.md) ends with a table,
"Where paraphrase remains correct", so that the 12 September return to quotation does not become a
licence to quote anything. Its first row is **operational detail**: when the wording is a reusable
attack procedure, abstract the mechanism and keep the consequence. The example it gives is
[page 082](../content/pages/082.md), cited through the page's row in
[the permissions audit](./exact-text-permissions-audit.md).

**The example is wrong, and the rule stands.** Page 082's command/output pair was removed in a
publication-rights pass, not for security. The project's own security review judged the pair benign
both before and after that removal. The story contract's security rule is unaffected. The table now
has no verified example of it.

The quotation note and page 082 are frozen files of the old edition (see
[`editions/three-stream/baseline.json`](../editions/three-stream/baseline.json)). By owner decision
of 15 September 2026, **this note corrects them without editing them**. The frozen note remains the
record of what was believed on 12 September.

## What the records show

All times are UTC. The 2 September acts are in Codex session `01a06270` on this Mac; the
12 September acts are in Claude session `45bdeb91`. Each record is admitted in the working edition and
placed in [`collaboration-analysis-limits-drafting.json`](../editions/three-stream/manuscript/collaboration-analysis-limits-drafting.json).

| When | Act | Reason recorded |
| --- | --- | --- |
| 2 Sep 15:45 | The chapter source packet registers METR's test command and its output as exact strings and calls the command innocuous | — |
| 2 Sep 15:48 | Page 082 is drafted with both strings lettered and registered, plus a note not to reproduce the spoofing mechanism | — |
| 2 Sep 16:49 | [The security review](./security-sensitivity-review.md) is written. It calls the pair a benign transcript-integrity demonstration, not an attack procedure | security: pass |
| 2 Sep 19:24–19:29 | A pass over 23 third-party strings held for publication rights removes the pair from page 082 and the exact wording from pages 079 and 081 | rights |
| 2 Sep 19:32 | The permissions audit's row for page 082 reads "Mechanism abstracted; mismatch and findings retained", with the result "cleared by paraphrase" | rights |
| 2 Sep 19:36 | The security review is edited to say page 082 now abstracts the demonstration. It still calls the demonstration benign | security: still benign |
| 12 Sep 15:30–15:41 | The audit row is read as the reason page 082 is abstracted under the security rule, and page 082 becomes the table's example | security (inferred from the rights row) |

No record in the 12 September session shows the security review's page 082 line being read.
METR prints both strings in the body of its report (p. 19, vault PDF). The mechanism is a separate
description, in its footnote 38, and it was never in the strings. The trap is general: an audit row
that *describes* a change is not the change's reason. Read the act that removed the text.

## Pages 079 and 081

The same rights pass removed verbatim source text from two neighbouring pages:

- **Page 079** lost the three pull-request metadata fields METR reproduces (p. 64). They are
  now summaries lettered as screen text.
- **Page 081** lost OpenAI's log-assurance sentence (technical report, printed p. 20). Its
  replacement drops "ultimately" and turns "attempts" into manipulation. The page's METR card is
  labelled a paraphrase, but it is METR's own sentence with two words removed (p. 19).

By the same owner decision, **the frozen pages stay as they are**. The three-stream working edition
registers all six strings with `rights: unresolved`, so quotation, paraphrase or redaction is decided
once, at [gate 9](../content/draft-readiness.md). The detailed account, with each string measured
against the vault copies, is in the
[working-edition log for 15 September](../editions/three-stream/log/2026-09-15.md).

## What this changes

- The operational-detail row of the quotation note should be read as a **rule without an example**.
  Do not cite page 082 as precedent for withholding a quotation on security grounds.
- A future example must show a security act, not a rights row. That means a security review, or a
  recorded decision naming the rule, that finds the wording itself would work as a procedure.
- Nothing here clears any string for publication. Rights remain unresolved until gate 9.
