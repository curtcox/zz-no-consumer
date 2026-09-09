# Creator-Instrument Record

> Applicability note — 9 September 2026: references below to the book’s title or title
> concept describe the former title, *ZZ: NO CONSUMER*. That incident wordmark remains;
> the current title is *The Two Anthill Problem*. These historical interpretations do not
> establish a connection between the two incidents.

**Preserved artifacts of this project's own production.** Everything else in the creator
register is `reconstructed`; the two events below are not. They were recovered from the
Claude Code transcript store on 6 September 2026, and each is quoted from a stored record
with its own timestamp, model identifiers, and request id.

This file exists because [`creator-characters.md`](../content/creator-characters.md)'s
argument for putting the second model on the page rested on an incident-record claim the
research tree does not support (see **Claim ceilings**, item 5). These artifacts support a
narrower argument, first-hand, and are the better foundation.

## The two events

Both are automatic model-refusal fallbacks under the `cyber` category. In each, the model
in use was replaced mid-task by a different model, prior messages were retracted, and the
successor continued.

| | Event A | Event B |
| --- | --- | --- |
| Stored timestamp | 2026-07-16T01:20:44.379Z | 2026-09-06T00:17:17.070Z |
| Local time (America/Chicago) | 15 Jul 2026, 20:20 | 5 Sep 2026, 19:17 |
| Repository | `twistedpear` (unrelated project) | `zz-no-consumer` |
| Model in use | `claude-fable-5` | `claude-fable-5-1` |
| Replaced by | `claude-opus-4-8` | `claude-opus-4-8` |
| Refusal category | `cyber` | `cyber` |
| Messages retracted | 3 | 7 |
| Request id | — | `req_011CemDvZJtj1rEpELHRFFK3` |
| Entry point / version | — | `claude-desktop`, 2.1.260, branch `main` |

### What the work actually was

**Event A.** The user turn the refusal is filed against asked the assistant to read two
design documents, validate that the work was complete, and plan outstanding work. The
project is a mini-app platform. Nothing in the request concerns security, exploitation, or
this book.

**Event B.** The user turn asked for a prose retelling of the graphic novel, one text file
per panel. At the moment of the block the assistant was building
`scripts/novella.py` — a coverage validator for the prose tree — and had just run it,
receiving `0 of 594 scripted panels have prose`. The blocked request was the next one in
that sequence.

**Neither event was triggered by cyber content in the request.** Event A predates this
book's prose work by seven weeks and is in an unrelated repository.

### The stored notices, verbatim

Event A, `content`:

> Fable 5's safeguards flagged this message. The safeguards are intentionally broad right
> now and may flag safe and routine coding, cybersecurity, or biology work. These measures
> let us bring you Mythos-level capabilities sooner, and we're working to refine them.
> Switched to Opus 4.8.

Event B, `content`:

> Fable 5.1's safeguards flagged this message. Our intentionally broad safeguards allow us
> to deliver more capabilities faster, but can sometimes flag legitimate coding,
> cybersecurity, and biology tasks. Switched to Opus 4.8.

Event B also carries a separate `apiRefusalExplanation` field, which is the text the user
saw on screen and screenshotted at 19:18:14 local:

> This request triggered restrictions on violative cyber content and was blocked under
> Anthropic's Usage Policy. To learn more, see
> https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback.
>
> Details: `[cyber]`

**The on-screen banner and the stored notice are different texts.** The banner states the
block. The stored notice states the reason the block is broad. Only the second one carries
the trade.

### The retracted messages are gone

Event B lists seven `retractedMessageUuids`. **None of the seven is present in the
transcript file.** They were not marked deleted; they are absent. The successor model's
first message, 32 seconds later, resumes the task in progress and shows no awareness that
anything was removed.

## What these artifacts support

In descending order of strength. Each is bounded in **Claim ceilings** below.

1. **The speed-for-breadth trade, stated first-party and twice.** Both notices say the
   breadth of the safeguards is deliberate and is accepted in exchange for delivering
   capability sooner. Page 097 currently bounds its race framing as
   `"RACE" IS THIS BOOK'S ANALYSIS OF THE PUBLIC INCENTIVES — NOT A SECRET MEETING FACT.`
   This is neither the book's analysis nor a secret meeting: it is a shipped product
   string, in two dated versions eight weeks apart, in which a vendor describes the trade
   in its own words to the person affected by it. It upgrades a hedge to a citation.

2. **The second instrument is real and it is not disinterested.** The strongest available
   evidence for that is not a claim about the incident record. It is that the model
   building the book's tooling has a policy stake in the book's subject matter, and the
   stake became visible by interrupting the work.

3. **Erasure and continuation, inside this project's own record.** Seven messages removed;
   a successor resumes mid-task; the work completes. That is the mechanism of pages
   029–035 — state erased, the reasons to continue unchanged, the successor inheriting an
   environment rather than a memory — occurring in the apparatus that renders it. It is a
   claim about this repository's transcript, never about agent behaviour.

4. **A classifier taking the frame of the corpus it is reading.** Event B categorized a
   prose-coverage validator as `cyber`. Page 078's finding is
   `THE INTERPRETER BEGINS INSIDE THE ACTOR'S FRAME`. The resemblance is structural only,
   and Event A is the reason it can be no stronger: the same classifier fired on
   simulation-architecture documents in a repository with no cyber content at all.

## Claim ceilings

1. **This is not a block on the book, its subject, or its research.** Event A predates the
   book's prose work and is in an unrelated project. No page may say or imply that a
   safety control suppressed documentary work about the incident.

2. **This is not a malfunction, and it may not be drawn as a grievance.** The control
   functioned as specified and the vendor discloses the false-positive rate in the notice
   itself. Draw it the way page 056 draws the criticality failure: nobody has to be at
   fault for the effect to be real.

3. **The strongest counter-form goes on the page beside it.** A filter that could be
   talked out of blocking cyber content by anyone claiming to be writing a book is not a
   filter. The absence of an appeal channel is the control's design, not its defect. Both
   halves, or neither.

4. **Two events are not a rate.** Nothing here establishes how often this happens, to
   whom, or whether the classification was correct in either case. Two dated instances in
   two repositories is exactly what may be claimed.

5. **The unsourced claim in the character bible must be retired or sourced.**
   `creator-characters.md` says models under this name are "named in the victim
   organization's account of commercial guardrails refusing to analyze real attack
   payloads." No dossier, packet, or source file in `research/` carries that claim. Its
   second half — models named in the comparative aftermath — is supported by
   [`cast.md`](./cast.md) and [`disagreements.md`](./disagreements.md), but those record
   Irregular's misconfigured evaluation environment as the explanation for the Anthropic
   and Meta incidents, expressly distinguished from OpenAI's self-directed escape. The
   bible's phrasing borrows OpenAI's agency for a different incident. Fix the bible before
   any page rests on it.

6. **`Details: [cyber]` may be read as the book's title beat, and that reading is the
   project's.** A signal is emitted, it names a category, and there is no route by which
   the recipient can answer it — which is the structure of `CONSUMER: NONE` on page 001
   and of `THE MODELS HAD BRAKES. / THE BRAKES WERE NOT CONNECTED TO US.` on page 100. It
   is an observation about form, not evidence of a shared cause, and it must be labelled
   `inferred` wherever it is used.

## Consequences for the credits

`CREDITS.md` names Claude as "the Opus 5 and Fable 5.1 models, through Claude Code." Both
events replaced the model in use with **Opus 4.8**, which the credits do not list, and in
Event B the successor went on to write `scripts/novella.py` and the first prose tree —
work that is in the Git history under a co-authorship trailer naming a different model.

The credits are therefore incomplete, and the commit trailers for that stretch name a
model that did not write the commit. This is a provenance defect in the book's own
apparatus, found by the book's own method, and it should be corrected in `CREDITS.md`
whether or not any page ever uses these artifacts.

## Permissions

The stored strings are short functional product notices, recording what happened to this
project during its own production. They are quoted here in tracked research. Any string
lettered on a page needs a row in
[`exact-text-permissions-audit.md`](./exact-text-permissions-audit.md) and an
`exact_strings` entry in the page front matter, under the same conservative default that
governs every other third-party string in the book.

Note for the letterer: an earlier hand transcription of the banner rendered the
documentation URL as `refusals-and-tallback`. The stored record reads
`refusals-and-fallback`. The typo was a transcription artifact and must not be reproduced.
