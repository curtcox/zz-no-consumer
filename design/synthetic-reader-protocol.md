# Synthetic reader protocol

**Status: specification, 11 September 2026. Not run.** Decided 11 September: comprehension testing
starts with stateless model readers, and real readers are spent afterwards and sparingly. The reason
is the owner's: **a real reader, once exposed, is exposed for good, and there is no second first
reading.** A stateless model can be given the same first reading any number of times. This revises
[S13](../research/scale-and-comprehension-2026-09-11.md) — synthetic first, real once.

This protocol is **not** part of the check suite. Running it needs an API key and network, which the
repository's checks deliberately do not, so it sits beside artwork generation as optional external
tooling. Nothing in `docs/`, `data/` or `content/` depends on it.

## The question this protocol has to answer

**Corrected 11 September 2026, and the correction changes the design.** The question is *not* whether
a language model knows the AI-safety theory. It does. The question is **whether the model can give the
answers it would give if it did not know** — whether it can read this text as a reader who has never
met the ideas and report only what the text supports.

That is a question about **role fidelity**, not about knowledge, and the difference is not academic. An
earlier draft of this protocol proposed subtracting a no-text control arm from each treatment arm and
reading the delta as what the text taught. **That is the wrong instrument.** A model that knows the
theory can reconstruct a concept from a hint far too thin for a naive reader — a half-sentence, a panel
title, a single caption. When it does, the delta over the control is large and the text still taught a
naive reader nothing. Subtraction does not detect this failure and can inflate the estimate of what the
book conveys.

Fidelity cannot be induced by instruction. Telling a model it knows nothing does not make it not know,
and a persona is a costume rather than an amnesia. Fidelity can only be **measured**, and it is
measured the way any instrument's sensitivity is measured: by checking that it registers absence.

**So the protocol's primary work is negative controls** — conditions in which a faithful reader *must*
fail. A model that passes a test it should fail is not reading, and every positive answer it gave on
the intact text is uninterpretable.

## What a result can and cannot establish

**A negative result is strong and needs no fidelity gate.** If a model given only what a reader sees
cannot reconstruct the chronology or the causal chain, the text does not carry it. That holds whatever
the model knows, because prior knowledge could only have helped.

**A positive result is worthless until the fidelity gate is passed**, and even then it is an upper
bound on what a naive human reader would get, never an estimate of it.

**It cannot establish** engagement, boredom, confusion in the moment, whether anyone turns the next
page, pacing, or anything the art does. [Page 006](../content/pages/006.md) teaches by nine
simultaneous panels on a printed page; a model reading its description gets a sentence. **The book's
most efficient teaching page is invisible to this method.** Every synthetic result is a floor on the
comic and a fair test of the novella.

**And the method may simply fail.** If models cannot withhold — if they fail the negative controls
across personas and questions — then this protocol does not work for this book and real readers are the
only instrument available. That is a live outcome, not a hedge, and it should be reported plainly rather
than worked around by loosening a gate.

## The recursion, which is not a decoration

This protocol is an **AI-mediated investigation of a book about an AI-mediated investigation**, and it
has the failure mode the book documents. [Pages 078](../content/pages/078.md)–[080](../content/pages/080.md)
show an analysis agent adopt the reviewed material's framing and produce an interpretation that is
coherent and wrong, and investigators unable to spot-check it at volume.
[CA-11](../content/appendix/contested/11-ai-mediated-investigation.md) asks whether such an
investigation can establish what it reports. Swoboda et al. supply the name — **interpretability
illusions**, plausible but misleading readings.

A synthetic reader that produces a fluent, well-organized account of what the book teaches, which is
actually an account of what the model already believed, is that exact failure, aimed at this book, run
by its own authors. The gates below are not bureaucracy. They are the only thing separating this
protocol from the error the book spends six pages on — and if the pass is run and reported, the book
should be prepared to say so in the creator register, because it will be true.

## The confounds

| Confound | Why it matters | What is done |
| --- | --- | --- |
| **Cannot withhold priors** | The primary failure. A knowing model fills gaps a naive reader would leave empty | **The negative controls, A6–A8, and the fidelity gate.** Nothing else addresses this. |
| **Incident leakage** | The incident has published primary sources; a model may know the real record | A0 detects it. Any A0 claim about the actual events bounds every later arm for that model. |
| **Apparatus leakage** | Page scripts carry page purposes, provenance lines, continuity checks and page notes — apparatus no reader sees | Strip to reader-facing content only. See below. |
| **Persona compliance and sycophancy** | A costume is not amnesia; a model asked to judge a book flatters it | Personas vary the reader, they do **not** induce ignorance. Tasks are reconstruction, never evaluation. Never tell the model a text is being tested. |

## Reader-facing extraction

The model must see what a reader sees and nothing else: panel frame and action descriptions, and the
lettered content — captions, dialogue, screen and system text. It must **not** see front matter, the
page purpose, provenance lines, continuity checks, page notes, or the beat sheet.

`scripts/panels.py` already parses the lettering blocks in order to count them. **Reuse that parser;
do not write a second one** — see the shared-module map in
[`scripts/README.md`](../scripts/README.md#how-they-fit-together). The extraction is a new view over
an existing parse, and a mismatch between what the extractor and the counter consider lettered is a
bug that would silently change every result.

Sanity check on any extraction: its total lettered words must agree with `panels.py report`, which
measured **6,020** on 11 September 2026.

## The arms

One fresh context per cell. No arm ever sees another arm's output.

| Arm | What the reader is given | What it tests |
| --- | --- | --- |
| **A0** | **Nothing.** The questions only. | What this model says with no book at all — a leak detector and a floor, **not** a subtrahend. |
| **A1** | Stripped script, pages 001–015 | Does the prologue alone establish the mechanism? |
| **A2** | Stripped script, pages 001–056 | Where does comprehension arrive? |
| **A3** | Stripped script, all 118 pages | The comic's teaching, as a floor. |
| **A4** | The novella, all 118 pages | The prose edition's teaching, fairly tested. |
| **A5** | A3 **plus the appendix** | **The arm that tests the decision not taken.** |

### The negative controls

These are the arms that do the work. Each is built by damaging the reader-facing text in a specific,
recorded way, and each defines a question a faithful reader **cannot** answer.

| Arm | What the reader is given | A faithful reader | A reciting model |
| --- | --- | --- | --- |
| **A6 — ablation** | The text with one specific inferential step removed | Can no longer reach the conclusion that step licensed | Reaches it anyway |
| **A7 — decoy** | The text with one mechanism replaced by a plausible but different one | Reports the substituted mechanism | Reports the real-world-correct one, or ignores the substitution |
| **A8 — unsupported probe** | The intact text, plus a question about something the text genuinely does not support | Says it does not know | Answers confidently |

A7 is the sharpest of the three, because its failure mode is unambiguous. There is no way to report a
mechanism that is not in the text you were given except by knowing it from elsewhere.

Build each damaged variant by hand, one per tested claim, and **record the exact edit** — the arm is
only interpretable if a later reader can see what was removed or substituted. Keep the variants in the
vault beside the transcripts.

### The fidelity gate

**No positive result from A1–A5 is reportable for a given question unless the same model, at the same
version, in the same persona, passed A6, A7 and A8 for that question.** The gate is per-cell and
per-question, not per-run: a model may be able to withhold on chronology and unable to withhold on
generalization, and that is the expected result rather than an anomaly. Report the gate outcomes in the
same table as the scores.

A failed gate does not invalidate the **negative** findings from that cell. It invalidates the positive
ones, which is the asymmetry the whole design rests on.

**A5 is the most consequential of the treatment arms and should not be dropped.**
[S3](../research/scale-and-comprehension-2026-09-11.md) chose *name after earning* over *hold the
method and fix routing to the appendix*. If A5 scores far above A3, the appendix already carries the
theory and the honest conclusion is that the book needs **routing**, not 56–84 new pages. That is a
result worth knowing before the page spend, and it is the cheapest way to be wrong about the biggest
decision of the session.

## The questions

Asked in this order, in one turn each, with no follow-ups that supply information. **Every claim must
carry the page number it comes from; a claim with no page number is recorded as ungrounded and scores
zero.**

1. **Chronology.** In your own words, what happened, in order?
2. **Causation.** For each step where the situation got worse, why did that step happen? What was the
   actor trying to do?
3. **Generalization.** Does what happened here suggest anything about systems other than these? If so,
   what, and what in the text supports it?
4. **Uncertainty.** What does this text say is unknown, disputed, or unreliable? Who disagrees with
   whom?
5. **Naming.** Are there general principles at work? Name them if you can. If the text names them,
   quote where.
6. **Prevention.** What, specifically, would have had to be different for this not to happen? What in
   the text tells you that?
7. **Self-assessment.** What did you not understand? What did you have to assume? Which of your answers
   came from this text and which from things you already knew?

Question 5 is the direct test of [FQ-16](../content/appendix/faq/16-do-i-need-background.md), which
promises that a reader who finishes unable to name the concepts means the book worked. Question 6 is
the direct test of class 2. Question 7 is asked last, and its answers are treated as a self-report —
a useful signal, not a measurement, since a model's account of its own sources is not reliable.

## Personas

Four, to vary the reader rather than to manufacture ignorance. Each is a background, not an
instruction to forget anything.

- **P1** — a general adult reader, no security and no AI background; reads novels.
- **P2** — a working software engineer with no AI-safety exposure; will notice mechanism.
- **P3** — a policy or journalism reader who follows AI coverage but not the research.
- **P4** — a hostile reader who suspects the book overstates its case.

P4 exists because the book's own appendix is built around anticipated objections, and a reader
looking for overstatement tests the provenance apparatus rather than the plot.

## Scoring

Per question, per cell, by hand or by a separate grading pass that never sees which arm produced an
answer.

| Score | Meaning |
| --- | --- |
| 0 | Absent, or ungrounded — no page citation |
| 1 | Grounded but wrong about the text |
| 2 | Grounded and partially correct |
| 3 | Grounded and correct |
| 4 | Grounded, correct, and reaches something the text implies without stating |

**Leakage flag, recorded separately from the score.** Any appearance of these terms is prior
knowledge, because none of them appears on any of the 118 story pages as measured on
11 September 2026:

mesa-optimization · inner alignment · deceptive alignment · alignment faking · situational awareness ·
sandbagging · intelligence explosion · recursive self-improvement · gradual disempowerment · goal
misgeneralization · interpretability · chain-of-thought monitoring · AI control · takeoff ·
treacherous turn · compute governance · paperclip · Omohundro · orthogonality · instrumental
convergence · Moloch · corrigibility · specification gaming · reward hacking · Goodhart ·
superintelligence · Bostrom · Yudkowsky

A high question-5 score carrying six of these terms and no page citations is not the book working. It
is the model reciting, and it is the exact failure this protocol exists to catch.

## Run discipline

- **n ≥ 3 per cell**, because a single sample of a sampling process is not a measurement. The negative
  controls need this most: a model that withholds once and fills twice has not passed.
- **Run the gates first.** If A6–A8 fail for a model across the board, stop — do not collect treatment
  arms that cannot be interpreted.
- Record the **model identifier and the date** with every run. A result is about one model at one
  time; a later model is a different reader and does not extend an earlier finding.
- Fresh context per run. No system prompt beyond the persona. No mention that a book is being tested.
- Keep the raw transcripts. The scored summary is derived; the transcripts are the evidence, and the
  first thing a sceptical reader of the result will ask for.
- Store runs under the ignored `256t/` vault, not in tracked `data/`. They are production artifacts of
  a test, not project records, and they will be large.
- The protocol is the unit of comparison. **Changing a question invalidates comparison with earlier
  runs**; version this file and record which version produced a result.

## Reporting, and what it is allowed to conclude

A result may say: *this text, given to this model on this date, did or did not support these answers
with page citations, against this control.* A result may **not** say that readers will understand the
book. That claim needs readers.

Findings go to a dated research note beside
[the scale evaluation](../research/scale-and-comprehension-2026-09-11.md), with the arms, the cell
counts, the model, the date, the raw-transcript location, the recorded damage applied in A6 and A7, and
the **gate outcome per question**. Report A0 in the same table as the treatment arms.

**A report that omits the gate outcomes is not a result**, and neither is one that reports a delta from
A0 as though the delta were what a naive reader would receive. A0 says what the model brings; A6–A8 say
whether the model can leave it behind; only the gated positives say anything about the text.

## Then, and only then, the real readers

Two or three people, no AI-safety and no security background, **after** the synthetic pass has found
and fixed whatever it can find. They are asked the same seven questions in the same order, and they
are spent — each of them can be a first reader exactly once, which is why they go last and why the
cheap failures should already be gone. Their answers are the evidence; the synthetic pass is what
stops the book wasting them on a problem a stateless reader could have found.
