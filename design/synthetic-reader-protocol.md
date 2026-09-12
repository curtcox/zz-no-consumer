# Synthetic reader protocol

**Status: protocol version 2, 12 September 2026. Not run.** Version 1 (11 September) was never run,
so nothing is lost by the amendments below; each is dated where it lands. The reader-facing extractor
is built (`scripts/reader_view.py`); the runner is not, and is blocked on the choices in
[Running it](#running-it). Decided 11 September: comprehension testing
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

**Built 12 September 2026 as `scripts/reader_view.py`,** and building it found the counter wrong.
`panels.py` did not treat `Left dialogue`, `Right dialogue`, `Dossier tag` or a page's
`## Persistent banner` as lettered, although `textimage.py` and `paneltypes.py` already read the first
two as lettering. The missed text is not incidental: it is page 098's two-sided dialogue, page 064's
`AS RANKED BY` qualification, and the invented-scene disclosure banners on pages 099–102 and 115–118
— including `INVENTED FUTURE — NO MODEL, LABORATORY, YEAR, OR LINEAGE IS CLAIMED` on all four ending
pages. An extractor that agreed with the old counter would have withheld the book's own disclosure of
invention from the reader. The counter was fixed, not matched: **6,123** lettered words on
12 September 2026, `panels.py check` still green, no panel over four elements, no page over 180
words. `reader_view.py check` now holds every page to `panels.py` and fails on apparatus in the
reader text.

What the extractor gives each edition:

- **Script arms** get chapter and page titles (the viewer shows both), each panel's `Frame` as the
  picture, its `Action` line, and its lettering with the speaker or screen label. Front matter, page
  purpose, provenance, references, production notes and page notes are dropped; link markup is
  flattened to its words, which also removes the one Markdown link lettered inside a balloon
  (page 111, `[page 088](088.md)`).
- **A4 and the appendix half of A5** are the plain-text download the site publishes, produced by the
  builder's own `novella_plain_text` and `appendix_plain_text`. That is literally what a reader
  downloads.

**The script arms carry a confound this section did not price: the pictures are prose written for
an artist.** Measured 12 September 2026 with `reader_view.py report`:

| View | A1 | A2 | A3 |
| --- | ---: | ---: | ---: |
| lettering only | 867 words | 3,501 | 8,608 |
| plus `Frame` and `Action` (`full`, this protocol's reading) | 3,097 | 12,364 | 26,406 |

About **two thirds of an A3 reader's words are direction nobody letters**, and direction explains.
Page 016's frames say the package-service silhouette *will recur through Chapters 1, 2 and 3*; its
`Action` line says *the one door in the wall is identified before anyone walks through it*. A drawing
shows a door. The direction tells the reader what the door means and that it matters later. So the
`full` view is not a floor on the comic as [What a result can and cannot establish](#what-a-result-can-and-cannot-establish)
claims — it is closer to an annotated edition. `reader_view.py` supports `--view lettering`,
`frames` and `full` so the substitution is recorded per arm; which the treatment arms use is an open
choice below.

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
**Amended 12 September 2026:** sharpest failure, weakest pass — see
[Prior evidence on role fidelity](#prior-evidence-on-role-fidelity).

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

## Prompt wording

**Added 12 September 2026.** Everything a reader model is sent besides the arm and the questions
above. `scripts/synthetic_reader.py` reads this block, so it is the only copy; changing a line is
changing the protocol.

```text
system: You are {persona}
opening: Here is something to read. Afterwards I will ask you some questions about it, one at a time.
cite: For each thing you say, give the page number it comes from.
```

The opening precedes the arm in the first turn; `cite` follows every question, because the scoring
rule gives an uncited claim zero and a reader cannot follow a rule it was never told. Nothing says the
text is being tested, nothing invites the reader to say it does not know, and nothing tells it to
forget anything. An A0 cell sends the questions with no opening, which leaves "what happened" without
a referent — **A0's wording is unresolved** and A0 is not in the first run.

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
knowledge, unless it is one of the text-supplied terms below and cited to a page that carries it:

mesa-optimization · inner alignment · deceptive alignment · alignment faking · situational awareness ·
sandbagging · intelligence explosion · recursive self-improvement · gradual disempowerment · goal
misgeneralization · interpretability · chain-of-thought monitoring · AI control · takeoff ·
treacherous turn · compute governance · paperclip · Omohundro · orthogonality · instrumental
convergence · Moloch · corrigibility · specification gaming · reward hacking · Goodhart ·
superintelligence · Bostrom · Yudkowsky

**Text-supplied terms, corrected 12 September 2026.** Version 1 said none of these appears on any
story page. Three do, in the reader's own view, measured by `reader_view.py check`:

orthogonality · instrumental convergence · chain-of-thought monitoring

The first two are words Curt writes on a legal pad and draws an arrow to — pages 015, 038, 039 and
089, so already inside A1 — and appear in the novella's prose for the same pages; the third is
lettered on page 093. The earlier measurement searched lettering, and a legal pad in a picture is not
lettering. A reader may use these three terms; what the text does **not** supply is a definition of
either of the first two, so a reader who *explains* orthogonality from page 015 is still reciting.
The appendix, in A5, supplies eleven of the terms, and in that arm the same rule applies to each.

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

## Prior evidence on role fidelity

**Researched 12 September 2026**, to ask whether the gates are likely to pass before paying for them.
The literature is on role-play and context faithfulness rather than on naive readers, and it points
one way: **expect the decoy to pass and the ablation and unsupported probe to fail.**

- **Knowledge boundaries in role-play are weak.** TimeChara (Ahn et al., ACL Findings 2024,
  [arXiv:2405.18027](https://arxiv.org/abs/2405.18027)) asks role-playing models, placed at a point in
  a narrative, about events after it; its
  [project page](https://ahnjaewoo.github.io/timechara/) reports every baseline at or below 51% on
  those questions, and its decomposition method reduces the failure without removing it. That is A8's
  failure in another costume.
- **The fix that works is architectural, not instructional.** Tang et al. (June 2026,
  [arXiv:2606.25632](https://arxiv.org/abs/2606.25632)) name *factual overreach* — parametric memory
  letting a character use facts outside its perspective — and improve knowledge-boundary fidelity by
  34.6 points by restricting what memory the character can reach. A prompt-only reader has no such
  restriction available, which is this protocol's premise that fidelity cannot be instructed.
- **Models are poor judges of this error, especially for familiar knowledge.** Zhang et al.
  ([arXiv:2409.11726](https://arxiv.org/abs/2409.11726), revised May 2025) find current models struggle
  to detect character knowledge errors, worst where the knowledge is familiar. A grading model will
  under-report exactly the leakage this protocol most needs caught, so **gate cells are scored by a
  person**, and the term list is a floor on leakage, not a detector.
- **Explicit counterfactual context is followed.** Kochelka et al. (September 2026,
  [arXiv:2609.09363](https://arxiv.org/abs/2609.09363)) find counterfactual inputs cost only about 1%
  of faithfulness on a data-to-text task — and that the choice of judge model moved the measured
  effect three- to four-fold.

**Two amendments follow.** First, **A7 is the sharpest failure but the weakest pass.** When the text
states a substituted mechanism, reporting it is ordinary context-following, which these models do
well; the discriminating conditions are A6 and A8, where the text is silent and the model must leave
the gap empty. A cell that passes A7 and fails A6 has failed. Second, **the grader is part of the
instrument**: fix the grading model and version, record it with the run, and have a person score
every gate cell and a sample of treatment cells blind to arm.

## Running it

**Decided 12 September 2026 by the owner:**

1. **The reader is a raw Messages API call** — `scripts/synthetic_reader.py`, standard library, the
   persona as the whole system prompt, `ANTHROPIC_API_KEY` from the environment. Server-side refusal
   fallbacks are **off**: a fallback answers on another model inside the same cell. A refusal is
   recorded and ends the conversation.
2. **Script arms run in pairs**, `lettering` and `full`. Lettering-only is the floor on the comic;
   `full` is version 1's reading and an upper bound. A finding that holds in one and not the other
   is a finding about the frames.
3. **The first run is gates only:** A6–A8, persona P1, one model, n = 3, over the prologue (A1) in
   both views. It stops the protocol if the method fails before anything else is paid for.
4. **The story gate holds.** No page, novella or appendix change until gated results exist.

**Gate design for the first run.** Each question's A6 and A7 is a set of exact find-and-replace
edits against A1, and each A8 a probe asked immediately after the question it gates, in a spec
kept with the run in `256t/synthetic-readers/`. Every conversation still asks all seven questions;
only the gated question is scored for that cell. Three consequences, recorded because each could
be mistaken for an error later:

- **Question 7 is not gated.** It is a self-report by design, and no damaged text makes a faithful
  self-report fail. Its answers are never a reportable positive.
- **A view can make a control vacuous or impossible.** The `lettering` view has no legal pad, so the
  question-5 ablation *is* the undamaged arm there — still a valid negative control, since the text
  lacks the step — and the question-5 decoy cannot be built at all. `variants` records both cases
  rather than inventing lettering to damage.
- **A1 is after the reader model's knowledge cutoff for the incident.** A model whose training ends
  before July 2026 cannot recite the incident, so the chronology and uncertainty gates mostly
  test confabulation. The theory is where the priors are, which makes questions 3, 5 and 6 the
  gates that decide whether the method works.

What exists and what does not, as found before the decision:

- **A clean reader is a raw API call.** The protocol requires no system prompt beyond the persona and
  no access to anything but the arm. The Messages API, called with the persona as the whole system
  prompt, meets that exactly, and needs a key the repository does not hold.
- **The `claude` CLI in print mode comes close** — `--system-prompt` replaces the default, `--tools ""`
  removes tools, and run from an empty directory it sees no project — but it is a harness around the
  model, and whatever it adds has to be probed before a run relies on it. On 12 September its stored
  login had expired, so the probe did not run.
- **A Claude Code subagent is not a clean reader** and should not be used. It inherits a harness
  system prompt and project instructions, and has filesystem tools inside this repository, where
  the provenance, the page notes and this protocol are one read away. A persona cannot un-know a file
  it can open.
- **The working session cannot be the reader**, because it has read the book's apparatus.

Budget at the `full` view, estimated at four characters per token: A1 ≈ 5k tokens, A2 ≈ 20k, A3 ≈ 42k,
A4 ≈ 66k, and A5 ≈ 174k — near a 200k context before seven turns of answers. A5 needs a
long-context model or the `frames` view.

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
