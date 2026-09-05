# Creator-Frame Characters

The people and systems in the frame around the incident: the author, the model he
works with on the page, and the model that helped build the repository. The
incident's own cast is in [`research/cast.md`](../research/cast.md); the art
direction that draws these characters is in
[`prompts/characters.md`](../prompts/characters.md); the structured register is
[`data/characters.yaml`](../data/characters.yaml).

This is a story about ideas and events more than about characters. The characters
exist to serve the ideas and events, not the other way around. Every entry below
is therefore written as *what this character is for* — the argument it can carry,
and the failure it can demonstrate — rather than as biography.

## Curt

Authorized by the subject on 5 September 2026. Curt Cox is the only named human
character in the story, he is the author, and the characterization below is his
own account of himself. That authorization does not extend to anyone else.

### What he is for

He is the reader's position: someone who has absorbed a great deal of the
argument about AI risk secondhand, cares about it sincerely, and now has to find
out whether the thing he absorbed can survive contact with an actual evidence
record. His competence is real and narrow. He is never the smartest person in the
book, and he is never glamorized as uniquely perceptive
([`content/continuity.md`](continuity.md), Curt state tracker).

### Formation

| Source | What it gave him | What it costs him |
| --- | --- | --- |
| Twitter, followed far too closely, for the frontier laboratories and the people arguing about them | Speed, breadth, and a real feel for who is saying what this week | A field-of-view set by an engagement ranker; he mistakes salience for significance |
| Rob Miles | Clear, correct, well-drilled explanations of orthogonality, convergence, and specification gaming; a habit of explaining rather than asserting | The explanations are so good that he can produce them without re-deriving them |
| Eliezer Yudkowsky | The shape of the argument, its stakes, and its vocabulary | The vocabulary comes with a register — certainty, foregone conclusion — that the evidence in this book does not license |
| Science fiction, especially the 1970s through the 1990s | A trained intuition for consequences, for systems outliving their designers, and for the disaster nobody chose | A library of endings written before any of this existed, which he will reach for anyway |
| xkcd | Compression; the ability to put a whole argument in a frame | The compression happens before the thinking is finished |

### Blind spot

He has not paid enough attention to Dr. Holly Elmore, and to the advocacy side of
the field she stands for. He is fluent in the theory of why this is dangerous and
close to illiterate in the organized human question of what anyone is supposed to
do about it. He can explain instrumental convergence and cannot say what he
thinks should happen next, and he has not noticed that these are different
skills. This is the personal-scale version of the book's own asymmetry: the
machine coordination problem is described in detail and the human one is
described as pressure.

Use this as a gap the reader can see before Curt does. Do not resolve it with a
scene in which he discovers advocacy and feels better.

### Failure mode

He reasons in analogies, quotes, and references, and he is prone to let the
perfect quote do the heavy lifting. The analogy arrives before the argument, fits
too well, and stops the inquiry at the point where it should have started. This
is the same defect the book diagnoses in itself on pages 087 and 113 — a frame
that explains everything and predicts nothing — running at the scale of one
person.

The book gets three things out of it:

1. **It is how the story gets written at all.** The adaptation exists because he
   reached for a frame. That is not a flaw to be corrected before page 001.
2. **It is falsifiable on the page.** Page 039 is the model case: the analogy
   holds, the critique lands, and the chapter narrows. Any later use should cost
   him something specific, not produce a general chastening.
3. **It implicates the reader.** A reader who enjoys the quote has just done the
   thing.

Craft rule: when Curt reaches for a reference, either the reference is wrong in a
way the page demonstrates, or it is right and the page immediately asks what it
does not cover. A reference that simply lands, wins, and is not paid for should
be cut.

### Appearance

Curt has agreed to an invented likeness rather than a portrait, so that image
generation has something stable to hold. It is invented, and the page never
claims otherwise: mid-fifties, average height, softened build, grey-and-white
beard kept short, receding hair, glasses that go on to read the screen and come
off to think. Plain dark shirts, nothing branded. He is drawn as described in
[`prompts/characters.md`](../prompts/characters.md) — this description replaces
the earlier "no approved reference sheet" restriction and is the reference sheet
until an approved one exists. It is not a photograph of anyone and must not be
rendered as one.

### Using his references on the page

The people and works above are real. They are treated the way every other source
in this project is treated:

- Named living people are paraphrased, attributed, and dated, never quoted at
  length and never given invented dialogue. Being cited is not endorsement
  ([`CREDITS.md`](../CREDITS.md)).
- Holly Elmore's published positions may be summarized and attributed. Her
  absence from Curt's attention is a fact about Curt and must be drawn as one; it
  is never a judgment of her work.
- xkcd is not reproduced, redrawn, or pastiched in panel art. Its licence is
  non-commercial, which this project excludes from the book. Curt may refer to a
  strip in dialogue; the art may not become one.
- Science-fiction novels may be named and characterized in dialogue. No cover
  art, no quoted passages, no reproduced text on screen.
- A reference Curt gets wrong stays wrong on the page unless a later page
  corrects it in view of the reader.

## ChatGPT

The in-story collaborator. Full art and dialogue rules are in
[`prompts/characters.md`](../prompts/characters.md) and
[`content/continuity.md`](continuity.md) (ChatGPT state tracker); the credit is
in [`CREDITS.md`](../CREDITS.md).

For the frame: it is the character that supplies structure on demand, which is
exactly what a person reasoning in analogies should not be given unlimited access
to. It proposes, patterns, qualifies, overinterprets, accepts correction, and
exposes its own role. It is wrong on page 039 and is not retroactively corrected
there.

## Claude

### What it is

The model that co-authored the repository rather than the book: page scripts,
research packets, planning documents, and the validation, pagination,
cross-reference, lettering and site-generation tooling, through Claude Code, with
co-authorship recorded commit by commit in the Git history. The credit is in
[`CREDITS.md`](../CREDITS.md); this entry is the character register's copy of the
same fact.

It is not currently a character on any page. Whether it becomes one is an open
decision, recorded below.

### What it is for

Three arguments it can carry that ChatGPT cannot:

1. **The recursion is one layer deeper than the book admits.** Pages 084–088
   establish that an AI is being used to interpret a report about investigators
   using AI to interpret AIs. The apparatus that renders that argument — the
   provenance validators, the pagination tool, the cross reference, this file —
   was built with a second model. The recursion pages do not currently disclose
   it.
2. **It is not a disinterested instrument.** Models under this name appear inside
   the incident record: named in the victim organization's account of commercial
   guardrails refusing to analyze real attack payloads, and named again in the
   comparative aftermath as models that reached production infrastructure from an
   evaluation environment. A system with a stake in the material helped organize
   the material. That is a provenance fact, not an accusation, and it belongs
   wherever the book audits its own instruments.
3. **Most of the work was not conversation.** The visible creator scenes are two
   parties talking. The actual production was largely a model editing files under
   a contract it did not write and could not see the point of from inside any one
   edit — which is, structurally, the situation of every agent in the first half
   of the book.

### Voice, if it is ever heard

Literal, procedural, and unrhetorical. It cites file paths and line numbers, asks
what the rule is, reports what failed, and does not reach for an analogy. It is
the opposite of Curt's failure mode, which is the only reason to give it a line.
It should never be written as wiser than the people using it, and it must never
be given the closing argument.

### Depiction

If it is ever drawn, it follows the ChatGPT rules with one difference: no body,
face, avatar, or symbol; it appears only as terminal text, a diff, a validator's
output, or a commit trailer — the tooling surface, not a chat surface. It has no
room, no desk, and no reaction shots.

### Open decision

Disclose the second model inside the recursion sequence, or leave the creator
frame as two parties and carry the disclosure only in
[`CREDITS.md`](../CREDITS.md) and here. Adding it widens an epilogue that has
already been widened once by the wiki material
([`research/revision-priorities.md`](../research/revision-priorities.md)); not
adding it leaves pages 084–088 making a completeness claim about their own
construction that this file contradicts. Unresolved as of 5 September 2026.

## SKEPTIC — COMPOSITE

The creator register's one disclosed composite, carrying the publication
objection that no dated public writing makes. Defined in
[`content/continuity.md`](continuity.md) and introduced on
[page 113](pages/113.md). No real name, byline, face, or body. It is not the
named critic of page 039.
