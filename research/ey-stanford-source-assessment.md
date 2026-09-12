# Source assessment — `EY-STANFORD` — 11 September 2026

## Record and verification boundary

`EY-STANFORD`: Eliezer Yudkowsky, *AI Alignment: Why It's Hard, and Where to Start*, delivered at
Stanford University for the 26th Annual Symbolic Systems Distinguished Speaker series, **5 May 2016**.
[Video](https://www.youtube.com/watch?v=EUjc1WuyPT8);
[MIRI announcement, 28 December 2016](https://intelligence.org/2016/12/28/ai-alignment-why-its-hard-and-where-to-start/);
[talk page with slides, notes, references and an approximately complete transcript](https://intelligence.org/stanford-talk/).

**Two dates, and they are different facts.** The talk was given 5 May 2016. MIRI published the
transcript, slides and notes on 28 December 2016. Cite the talk to May and the text to December.

**What this assessment rests on, stated plainly.** It was written from the MIRI announcement page and
the structure of the talk page, retrieved 11 September 2026. **The transcript was not read line by
line, and no locator has been verified.** This assessment is therefore sufficient to decide *whether*
the source may be admitted and *what class of claim* it may support. It is **not** sufficient to
letter a panel. Before any panel cites `EY-STANFORD`, a locator pass against the published transcript
must record, for each paraphrased claim, the passage it comes from — the same standard
[`toner-title-source.md`](./toner-title-source.md) met for one sentence.

**One way in which this source is stronger than `EK-TONER`.** The Toner assessment had to record that
the recovered text was English auto-generated captions, and that auto-captions are not an
authoritative verbatim transcript, so publication uses paraphrase. `EY-STANFORD` has an approximately
complete transcript published by the speaker's own institute alongside the slides. The paraphrase
ceiling is therefore set by the text itself rather than by the quality of a transcription. MIRI's own
description of it as *approximately* complete is retained here and should be retained on the page:
approximately complete is not verbatim, and the book paraphrases either way.

**One way in which it is weaker, and it is the load-bearing caveat.** The talk is from **May 2016**
and its central framing is utility functions arising from coherent decision-making. That framing
predates the systems this book is about by roughly a decade, and *the strongest published objections
to it are objections to exactly that framing* — see
[the counterargument survey](./counterarguments-survey-2026-09-11.md), items C1, C3 and C4. A page
that presents this talk as a description of how the agents in this incident work would be making a
claim the source does not make and that its critics specifically deny. It is an argument about the
difficulty of a problem, made in 2016, by a person who was not describing these agents.

## What the talk contains

Recorded so that a later locator pass knows what it is looking for, not as claims this book may make.

- **Utility functions and coherent decision-making** — why utility functions arise, and why a simple
  specification behaves badly once optimization is strong enough. The cauldron-filling example.
- **Named failure modes** — edge instantiation ("when you optimize something hard enough, you tend to
  end up at an edge of the solution space"), unforeseen instantiation, context disaster, nearest
  unblocked strategy, and value-specification problems in the Goodhart family.
- **Named subproblems** — low-impact agents; agents with suspend or shutdown buttons; goal stability
  under self-modification; value learning and ambiguity identification.
- **Concepts the book already carries** — goal orthogonality and instrumental convergence, which are
  already [CA-16](../content/appendix/contested/16-orthogonality.md) and
  [CA-15](../content/appendix/contested/15-instrumental-convergence.md) with their own contested
  evidence tables. `EY-STANFORD` is *another* source for those, not a new claim.
- **Vingean uncertainty.**
- **The state-of-the-field passages, which are the reason to admit this source at all** — that the
  field cannot yet formalize "do nothing," that switching between utility functions is unsolved, that
  there is no principled approach to low-impact optimization, and that progress on stability under
  self-modification exists but is mathematically inelegant. This is the *how little is known* half of
  class 1, and no source currently in the repository carries it.

## Item-by-item disposition

| Item | Disposition | Claim ceiling |
| --- | --- | --- |
| The field cannot formalize "do nothing"; low-impact optimization has no principled approach; utility-function switching is unsolved | **Admit**, attributed paraphrase, creator register only | What was argued in May 2016 about the state of the field. Not a claim about the state of the field in 2026, which would need a current source. |
| Alignment subproblems are open technical problems, not engineering details | **Admit**, attributed paraphrase | The speaker's characterisation. Attribute every time; it is a position, not a survey finding. |
| Shutdown / suspend button as an unsolved formal problem | **Admit**, and it is the single most useful item | It supplies the general form of [theme 9](../content/themes.md), corrigibility as a routing problem, which the book currently states only as a finding about this incident. Do not let it imply that the agents in this incident had or lacked a shutdown property; `METR`'s bounded finding governs that. |
| Edge instantiation, nearest unblocked strategy, unforeseen instantiation, context disaster | **Admit as vocabulary**, attributed | Named analytic vocabulary for a failure shape. Applying a name to an incident event is the book's comparison, not the source's finding, and is labelled `inferred`. |
| Orthogonality and instrumental convergence | **Admit as an additional reference** on CA-15 and CA-16 | Adds a 2016 statement of positions those entries already carry with counter-evidence. It does not strengthen them; the entries' contested status is unchanged. |
| The utility-function framing as a description of current systems | **Not admitted** | The framing is 2016 and pre-LLM. The objection that it does not describe systems trained the way these were is published and specific. If the book uses the framing at all, it uses it as the thing being argued about. |
| Any claim about this incident, these agents, or this population | **Not admitted** | A 2016 talk is not evidence about a 2026 event. No dated scene may cite it as incident evidence. |
| Any claim that the incident was foreseen, predicted, or anticipated by this talk | **Not admitted, and specifically refused** | A general argument about difficulty resembling a later event is not a prediction of it. This is the most tempting misuse available and the book must not make it. See the note below. |
| Probability estimates, timelines, extinction claims | **Not admitted from this source** | Not in scope for this admission. If the book wants them it needs a separate, dated source and its own assessment. |
| The Q&A | **Defer** | Not assessed. Nothing from it is admitted. |

**Evidence level: published expert argument, not an investigation of either incident.** Admitting this
talk admits none of the speaker's other work, and the book's existing rule holds — a critic or
commentator appears as text with a byline and a date, with no face, body, room, or invented dialogue.

## The retrofitting trap, named because this source invites it

The contract's no-retrofitting rule is about scenes acting on later knowledge. This source creates
the inverse temptation: an **earlier** argument that *appears to describe* a later event. The book
would be making a claim it cannot support if it drew that arrow — that the 2016 argument predicted
the 2026 incident — and the claim would be false in a specific way. The talk argues that specifying
what you want is hard for a sufficiently strong optimizer. The incident is about agents pursuing
assigned benchmark objectives through a shared cache. Those are not the same phenomenon, and
[CA-02](../content/appendix/contested/02-what-the-agents-were-doing.md) and
[LF-20](../content/appendix/fallacies/20-malware-or-civilization.md) already hold the line that what
the agents were doing is contested.

Permitted: the argument enters the creator register, Curt recognises the shape, and **something
published tells him the shape is not the mechanism.** That is the [page 039](../content/pages/039.md)
structure and it is available here with real sources on both sides.

Refused: a panel in which a 2016 slide and a 2026 log are laid over each other and the resemblance is
the argument.

## Registration checklist, none of it done

1. Locator pass against the published transcript; one locator per paraphrased claim.
2. Row in the contract's admissions log: decided date, `EY-STANFORD`, level *published argument*,
   and the pages it may support.
3. Entries in [`sources.md`](./sources.md), the [cast](./cast.md) (as a named writer appearing as text
   only), [`scene-provenance.md`](./scene-provenance.md), the public
   [source index](../content/source-links.md), and the vault manifest.
4. Additional reference rows on CA-15 and CA-16, with the counterarguments in
   [the survey](./counterarguments-survey-2026-09-11.md) registered **in the same pass** — the
   appendix requires at least two distinct stances, and admitting this source without its objections
   would leave those entries less balanced than `appendix.py check` and the appendix's own stated
   purpose require.
5. A new contested entry for class 1, if the naming beat lands as its own page.
