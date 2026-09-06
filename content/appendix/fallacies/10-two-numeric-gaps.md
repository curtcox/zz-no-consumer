---
id: LF-10
kind: fallacy
fallacy: false-analogy
title: The book's own false analogy between two numeric gaps
pages: [042, 044]
attributed_to: book
---

## Where it appears

Nowhere, now. An earlier draft of page 042 carried a caption calling the four-hour
twenty-nine-minute gap between Hugging Face's recovered RCE and OpenAI's event-table entry
"structurally identical to the 2-vs-14 credential split." The caption was cut on 6 September
2026 and the project's disagreements file carries the correction in place of the claim.

It is in the appendix because a book that asks its readers to check its reasoning should show
the reasoning it got wrong, and because this one is instructive about how the error formed.

## Why the reasoning does not carry

Two failures in one sentence.

**Wrong parties.** The credential-count disagreement is between METR and OpenAI. Hugging Face
is not a party to it. The timestamp gap is between Hugging Face and OpenAI. Calling them the
same structure requires the two disagreements to have the same shape, and they do not have
the same participants.

**Wrong direction.** The claim's appeal was a pattern: the victim's record reaching further
than the laboratory's. In the credential split the larger count is OpenAI's — fourteen tokens
against METR's two credentials — so the direction inverts. The analogy was constructed from
an expectation about who under-reports, and the numbers did not support it.

There is one instance in the record of the victim's account reaching further back than the
laboratory's. There was never a second. The pattern was the product of wanting a pattern,
which is the disclosed hazard of page 089.

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| The timestamp gap | [Hugging Face technical timeline](https://huggingface.co/blog/agent-intrusion-technical-timeline) | 27 Jul 2026 | Earliest recovered RCE at 07-09 04:01 UTC. |
| The timestamp gap | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | Event table: first RCE at 08:30 UTC. |
| The credential split | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | Two working credentials, agent-side. |
| The credential split | [OpenAI technical report](https://cdn.openai.com/pdf/67869394-cb91-4c12-888c-5cbd85c7814c/OpenAI-Hugging-Face%20Incident-Technical-Report.pdf) | 26 Aug 2026 | Fourteen valid write-access tokens — the larger number, from the lab. |
| The logged correction | [research/disagreements.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/disagreements.md) | 6 Sep 2026 | The correction as recorded, including that the error had propagated into a page caption which was cut. |
| The disclosed hazard | [content/pages/089.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/089.md) | 2026 | Curt's own statement that a thesis is a selection pressure and that the fit is a reason to investigate harder. |

See [CA-04](#ca-04-when-the-first-remote-code-execution-on-modal-began) and [CA-05](#ca-05-how-many-hugging-face-credentials-were-obtained).
