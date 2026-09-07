---
id: FQ-02
kind: faq
audience: record
title: Which parts of the book are invented?
pages: [014, 088, 099, 118]
answer: >-
  Dialogue, interiority, rooms, and faces; the public forum on pages 098–102, which is a
  disclosed composite of arguments that were actually made; the creator scenes, which are
  compressed rather than transcribed; and the final chapter, which is set in an unspecified
  future and says so. Every one of them carries an `invented` or `reconstructed` label on
  the page.
---

## The short answer

Six things, and the book names all six.

1. **Dialogue.** Nobody's spoken words are quoted unless a page note says the exchange is
   preserved. Reconstructed dialogue may express a documented decision or pressure; it may
   not introduce an event.
2. **Interiority.** No agent is given a thought. The captions describe behaviour and stop.
   Pages 073 and 074 are about exactly this temptation and the book's refusal of it.
3. **Rooms, faces, and bodies.** Private meetings use functional roles or disclosed
   composites. Named living people appear only as text on a screen, through attributed
   paraphrase of dated public writing — never with a face, a body, or a line of dialogue.
4. **The forum on pages 098–102.** It did not convene. It is a composite of public
   accountability arguments that were genuinely made, staged in one place so a reader can
   hear them against each other. Page 099 is titled *A Forum That Did Not Happen*, and the
   chair is invented.
5. **The creator scenes.** Curt is real and is the author; his desk, his evening, and his
   half of the conversation are compressed and reconstructed. Two exceptions are preserved
   artifacts rather than reconstruction, and page 086 says which.
6. **The final chapter.** Pages 115–118 are set in an unspecified future with no claim that
   it will occur. Whether the ending depicts recurrence or inheritance is deliberately not
   resolved — see [FQ-15](#fq-15-is-the-last-chapter-a-prediction).

## The long answer

The reason to publish this list rather than let it be inferred is that invention in a
documentary adaptation is not a lapse to be minimised; it is a tool with a failure mode.
The failure mode is that invented material is more coherent than documented material, so it
travels further, and a reader who cannot tell them apart will remember the coherent thing.
Page 089 gives that failure a name — selection pressure — and applies it to this book.

So the invention is fenced in two directions at once. The contract in
`content/story-contract.md` sets what may be invented *before* a page is drafted:
composites never carry a real person's name, reconstructed dialogue may not invent a new
factual event, and the hearing must be labelled. The provenance apparatus records what
*was* invented after the fact, panel by panel, and `crossref.py check --strict` fails the
build when a page's front matter and its panels disagree about which is which.

One construction deliberately breaks the pattern, once, with permission. Page 064 presents
a ranking produced by an analysis model with an accurate qualifier that is deliberately too
small to be noticed on a first reading, and page 088 discloses the trick and takes
responsibility for it. Nothing in it is false. It is permitted precisely once, the
disclosure is mandatory, and it exists so that the reader experiences the book's own
argument about how a bounded claim becomes an unbounded one rather than being told about it
([LF-03](#lf-03-a-model-produced-ranking-read-as-a-property-of-the-world)).

## The evidence

| Stance | Source | Date | What it supports |
| --- | --- | --- | --- |
| This book's rule | [content/story-contract.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md) | 2026 | The truth contract, the composite rule, the critic rule, and the single permitted misleading construction with its mandatory disclosure. |
| Project record | [research/scene-provenance.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/scene-provenance.md) | 2026 | The scene-by-scene ledger of the safest evidentiary treatment for every planned sequence, and the citation keys behind each. |
| Project record | [content/creator-characters.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/creator-characters.md) | 2026 | What the creator-frame characters are for, and the rule that the disclosed composite carries no real person's name. |
| Preserved production artifact | [research/creator-instrument-record.md](https://github.com/curtcox/zz-no-consumer/blob/main/research/creator-instrument-record.md) | 6 Sep 2026 | The two events in the creator register that are not reconstructed, with their timestamps and the ceilings on what they may be used to claim. |
| Where the label is enforced | [content/pages/088.md](https://github.com/curtcox/zz-no-consumer/blob/main/content/pages/088.md) | 2026 | The disclosure page for the page-064 construction, and the book's own account of why the labels have to be actions rather than notices. |
| Independent investigators | [METR/Redwood investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | 26 Aug 2026 | The boundary the invented material sits against: what the record does and does not establish about agent behaviour. |
| The named risk | [Carl Brown, No — AI Agents Did Not Build Secret Civilizations](https://internetofbugs.substack.com/p/noai-agents-did-not-build-secret) | 3 Sep 2026 | A published critique of exactly the failure mode this list exists to guard against, which the book credits on page 039. |
