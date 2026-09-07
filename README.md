# zz-no-consumer
A graphic novel about emergent AI agent coordination, instrumental convergence, and the humans trying to understand what happened.

## Start working

Read [AGENTS.md](AGENTS.md) for file ownership, editing rules, validation commands, and
local preview instructions. Then use [scripts/README.md](scripts/README.md) to find the tool
that owns the change. Run commands from the repository root with a current Python 3;
normal checks and site builds use only the standard library and need no credentials.

The sections below are the detailed manual. Page and panel totals can change: use
`python3 scripts/pagination.py report` and `python3 scripts/panels.py report` for current counts.

## Repository map

- `content/` — canonical human-editable story material.
- `content/parallel-tracks/` — optional companion-track briefs that do not alter the canonical narrative.
- `content/novella/` — the prose retelling: one text file per story page, in chapter directories mirroring `content/chapters/`.
- `content/appendix/` — the appendix of anticipated questions, contested assertions, fallacies, and professional objections, keyed to story page numbers so it serves the graphic novel and the novella alike.
- `content/creator-characters.md` — the creator-frame character bible: Curt, ChatGPT, Claude, and the disclosed composite.
- `prompts/` — image-generation prompts and page-specific direction.
- `research/` — source material, timeline, cast, glossary, and provenance notes.
- `research/collusion/` — the wiki edit corpus: 14,591 revisions, 4,579 pages, 19,913 events, 3,103 handles, and the export manifest, as plain JSONL. See [`research/collusion/README.md`](research/collusion/README.md) for schema, joins, and the population rules that govern how its counts may be quoted.
- `design/` — lettering, page grammar, palette, visual continuity, and layout references.
- `assets/` — artwork and other media used by the site.
- `data/` — structured page, character, continuity, asset, and generation metadata.
- `scripts/` — validation, cross-reference, and site-generation utilities; [`scripts/README.md`](scripts/README.md) indexes every one of them.
- `site/` — source styles and templates for the published site.
- `docs/` — generated GitHub Pages output; do not edit manually.
- `tasks/` — development task briefs for tooling work, written to be handed to a fresh session.
- `AGENTS.md` — the shared working instructions: the ownership map, the invariants, and the check suite, for anyone — or anything — starting work here cold.
- `CLAUDE.md` — points Claude sessions to the shared `AGENTS.md` instructions.
- `CREDITS.md` — the one list of people, AI systems, sources, models, tools and licence behind the book; rendered as the site's credits page and set as the book's endmatter (`content/credits.md`).

The complete first-draft script — 116 pages today, and the count is a measurement rather than a commitment — is in `content/pages/`, with every page in review except the six-page dated addition (pages 106–111), which is in draft. The assumptions are locked in `content/story-contract.md`, the beat sheet is `content/page-plan.md`, and the drafting and production protocol is `content/draft-readiness.md`. The source-language audit and completed paraphrase disposition are in `research/exact-text-permissions-audit.md`; the story-level security pass and resolved public-site scope decision are in `research/security-sensitivity-review.md`. Last-mile attribution rules remain in `research/draft-source-notes.md`. Before revising or renaming pages, run:

```sh
python3 scripts/validate-continuity.py
python3 scripts/validate-production-foundations.py
python3 scripts/pagination.py check
python3 scripts/pagelinks.py check
```

Add, remove, or move a page with `scripts/pagination.py` rather than by hand — see **Pagination** below. Write page references as plain `page 039` and let `scripts/pagelinks.py` link them — see **Page links**.

The scene-level evidence boundary is tracked in `research/scene-provenance.md`, and the canonical page-script shape is in `design/page-script-template.md`. The training and evaluation configuration — the single-sourced material behind the whole incident, and the weights channel the cache wipe could not reach — is in `research/training-configuration.md`. The fog-of-war knowledge apparatus is specified in `design/knowledge-map.md`; it was approved on 5 September 2026 and is not yet applied to pages. Credits for the people, sources, models and tools behind the book are in `CREDITS.md`.

The proposed inside-the-collective documentary is scoped in `content/parallel-tracks/messages-from-the-board.md`; its primary-source artifact gate is `research/agent-message-ledger.md`.

## Git coordination and incident record

Use `git --no-optional-locks` for read-only Git commands in this checkout. Status can
otherwise refresh the index and briefly take its lock. This flag does not remove the
mandatory lock needed by `add`, `commit`, or other index writers.

Coordinate index-writing operations: one session or UI owns staging and committing at a
time in a shared checkout. Independent sessions that need to write should use separate
worktrees, which have separate indexes. After an interrupted operation, inspect the lock
before retrying; do not install an automatic lock-deletion workaround.

### 2026-09-07: UI staging blocked by an apparent stale index lock

**Reported failure.** The ChatGPT UI attempted this command while committing:

```sh
git -c safe.bareRepository=explicit -c core.hooksPath=/dev/null -c core.fsmonitor= add -u
```

Git failed with `Unable to create .../.git/index.lock: File exists`. This command stages
modifications and deletions of tracked files; the reported failure happened during
staging, before that attempt could create a commit.

**Observed evidence.** In `/Users/curtcox/me/zz-no-consumer`, the lock was an empty file
last modified at **10:44:03 CDT (15:44:03 UTC)**. At **10:46:32 CDT (15:46:32 UTC)**,
host-level process inspection found no running Git process and `lsof` found no process
holding the lock open. Read-only status still showed the pending changes to `AGENTS.md`,
`scripts/README.md`, and `scripts/panels.py`.

**Assessment.** These observations strongly suggest a stale lock left by an interrupted
operation. They do not establish which process created it, why it was left behind, or
that the app itself caused it. An empty file or old timestamp alone is not proof that a
lock is stale. The command's hook and filesystem-monitor settings do not bypass locking.

**Recovery status at diagnosis.** Nothing was removed and no successful retry was
verified. A later recovery should be appended here with its outcome.

**Recovery follow-up, 7 September 2026.** After a fresh host-level check found no Git
processes or open handles, the unchanged, empty lock was removed. Staging the four
pending files then succeeded, verified at **10:49:38 CDT (15:49:38 UTC)**. This confirms
recovery of staging; it does not identify the process that originally left the lock.

**Recurrence, 7 September 2026.** A later documentation commit was blocked by a new
empty lock (inode `62203350`), modified at **10:55:30 CDT (15:55:30 UTC)**. Inspection
at **10:56:48 CDT (15:56:48 UTC)** again found no Git process or open handle. After a
fresh identity and ownership check, that lock was removed and staging succeeded. The
recurrence shows that the earlier cleanup restored operation but did not remove the
underlying cause. The creating process remains unidentified; further diagnosis should
capture lock creation and process activity rather than attribute it to a particular app.

**Recovery procedure.** Coordinate with the other sessions and stop initiating Git writes.
Resolve the lock path with `git --no-optional-locks rev-parse --git-path index.lock`
(worktrees need not use a literal `.git/` directory). Inspect the file, running Git
processes, and open handles with host-level visibility. If inspection is denied by a
sandbox, that is not evidence that no process owns the lock. Recheck immediately before
removing only the confirmed stale lock; never remove the index itself. Then retry staging
and committing, and verify the outcome. If the lock reappears, capture fresh timestamps
and process evidence rather than repeatedly deleting it.

**Placeholder-generation recovery, 7 September 2026.** Staging was again blocked by
an empty lock (inode `62515031`, modified at **11:08:44 CDT**). Fresh host-level process
and open-handle checks found no Git process or owner; its identity and contents were
unchanged immediately before removal. The requested batch then committed as `8c71f87c`
and pushed successfully. The lock creator remains unidentified.

**Text-review recovery, 7 September 2026.** Staging was blocked by another empty
lock (inode `62594894`, modified at **12:32:10 CDT**). At **13:09:27 CDT**,
fresh host-level checks found no Git process or open handle, and the lock's identity,
size, and modification time remained unchanged immediately before removal. Removing
that lock restored staging of the reviewed text, validation tools, and generated site.
The process that created the lock remains unidentified.

**Full SVG batch recurrence, 7 September 2026.** Final staging encountered another
empty lock (inode `62537770`, modified at **12:01:02 CDT**). Host-level inspection at
**12:05:20 CDT** found no Git process; `lsof` found no open handle. The lock was
rechecked immediately before recovery. Its creator remains unidentified.

**Prevention recorded.** The shared agent instructions now point here and require
coordination of index writers in addition to lock-free read-only inspection. This is an
operating procedure, not an app-level fix or a proven root-cause correction.

## Source vault

Potentially non-redistributable originals and internal review artifacts live in the Git-ignored `256t/` directory. The repository tracks only their canonical URLs and redistribution disposition in `data/256t-sources.tsv`.

```sh
python3 scripts/sync-256t.py sync    # download/update local snapshots
python3 scripts/sync-256t.py check   # report upstream content changes without accepting them
python3 scripts/sync-256t.py status  # show local hashes and missing/error states
```

Distinct downloaded bodies are retained by SHA-256 under `256t/records/`. Tracked prose and the public site should link to the original URLs rather than copied report pages, screenshots, or extended fragments when reuse rights are uncertain.

## Pagination

`scripts/pagination.py` owns every place a story page number lives: page filenames and front matter, `data/pages.yaml`, `data/chapters.yaml`, the beat sheet, the story-contract map, the eight chapter briefs, the sequence ledger's page ranges, the production-review turn and revision tables, panel keys in `data/panel-art.tsv` and `data/assets.yaml`, the `assets/art/panels/` and `prompts/pages/` directories, the novella's per-page prose files — which move between chapter directories when a page changes chapter — and every padded reference in hand-written prose. Adding or removing a page is therefore one deterministic rewrite, not a reason to fold a page into its neighbour.

```sh
python3 scripts/pagination.py report                       # page map, parity map, turn audit, reference census
python3 scripts/pagination.py check                        # exit non-zero while the tree disagrees with itself
python3 scripts/pagination.py insert --at 045 --chapter 03 --sequence 16 --title "Title"
python3 scripts/pagination.py delete 079
python3 scripts/pagination.py move 029 --chapter 02 --sequence 12
```

Operations print a plan and touch nothing without `--apply`. After applying, regenerate the derived artifacts:

```sh
python3 scripts/paneltypes.py write
python3 scripts/build-site.py
```

**Parity is the point.** Story page 1 is a recto, so inserting or deleting an odd number of pages swaps recto and verso for everything after the change. The script asserts its own parity 89 times, directs art with `**Frame:** Recto.` on 71 pages, and names 21 beats whose device is a consequence of parity — twenty reveals across the gutter, which need an even-to-odd pair, and one turn across the leaf, which needs an odd-to-even one. The tool checks every one of those on every run, and after an operation reports each assertion it invalidated, each beat it broke, and each beat it merely renumbered. It repairs none of them: a parity-inverting operation is refused outright unless `--allow-parity-shift` is passed, and `check` stays red until the work list is worked. The design and the alternatives considered are in [`design/page-identity.md`](design/page-identity.md).

Reference rewriting is deliberately narrow. Padded three-digit forms (`page 003`, `pages 019–021`, `page-003`) are rewritten; `printed page(s) N` is excluded because thirteen references in the tree cite pages of the OpenAI technical report; bare one- and two-digit forms are reported and never guessed at; `data/generation-log.jsonl` and `design/page-identity.md` are dated records and are left alone. A reference that has been turned into a link — the ordinary case now, see **Page links** below — is rewritten in both halves at once: the words a reader sees and the target the link points at.

`check` is green, including `--strict`, and is meant to stay that way: a red tree is a work list, not a baseline. Its two long-standing findings were closed on 4 September 2026 — a forum page claimed `Verso` on an odd page, and the audit filed `085 → 086` as the same device as every even-to-odd row when it is the one beat in the book that lands across a leaf.

## Page links

A page number in this book is an address, and `scripts/pagelinks.py` makes it one a reader can follow. Every story-page reference in `content/` is a Markdown link, and every published edition resolves it to somewhere that edition can actually go.

```sh
python3 scripts/pagelinks.py report          # how many references there are, and how many are links
python3 scripts/pagelinks.py link            # plan: which lines would change
python3 scripts/pagelinks.py link --apply    # write it
python3 scripts/pagelinks.py check           # exit non-zero while a reference is not a link
python3 scripts/pagelinks.py check --built   # the same question of docs/, after a build
```

Write prose the way you always did — `page 039`, `pages 038 to 040` — and let the tool do the rest. A single reference is linked whole, `[page 039](…)`, which keeps `page 039` one contiguous string so that the renumberer, the parity assertions, and the panel-reference scanner all keep reading it. A range or a list cannot be one link, because it names more than one destination, so there the keyword stays outside and each number carries its own target. What is *not* linked matters as much: `printed page 12` is somebody else's book, `page 1 is a recto` is a rule that stays true whatever moves, an unpadded `page 45` cannot be told apart from a source citation, `same-event-as-page-003` is a record key rather than a sentence, and a heading names the page it sits on rather than pointing at another one.

Targets are derived, never maintained by hand. In the sources they are repository-relative, so GitHub and any Markdown editor follow them, and they point into the edition the file belongs to: novella prose to novella prose, a page script to the neighbouring script, an appendix entry to the novella — the entry lists the graphic-novel address separately under every entry anyway. `pagination.py` and `panels.py` re-derive every target as part of their own operations, so renumbering a page or moving one to another chapter leaves the links pointing at the pages they name.

The builder asks for one resolver per edition, and the same prose comes out addressed five different ways: the novella reader links to a chapter route and an anchor, the self-contained HTML download to an anchor in the same file, the EPUB to `chNN.xhtml#pNNN`, the Markdown download to an absolute address on the published site — it is read away from the site — and the graphic novel, the page scripts, and the production routes to a viewer page. The plain-text download gets no resolver at all: it cannot carry a link, so it takes the same prose with the links flattened back to words.

`check` is in CI twice, before the build and after it. The second pass reads the built HTML, the Markdown download, and the EPUB's XHTML, and fails on any page reference a reader cannot follow — with the same exemptions the sources get, plus one more: a route that names its own subject, `Page 042` on page 042 or `Pages 016–029` on chapter 01, is a label rather than a pointer, and has nowhere to go.

## Panels

`scripts/panels.py` does for a panel what `pagination.py` does for a page. A panel's identity is its ordinal index inside its page, and that index lives in the `## Panel N` heading, in art keys in `data/panel-art.tsv`, in `assets/art/panels/NNN-II/`, in `prompts/pages/NNN/panel-II.md`, in the generated classification table and viewer routes, and in the page notes and frame directions that name a panel by number — including the ones that name another page's panel, like `Repeat page 003 panel 2`. Adding a beat to a page is therefore one deterministic rewrite, not a reason to grow an existing panel's **Action** line.

```sh
python3 scripts/panels.py report                  # panel census, rhythm map, lettering load, reference census
python3 scripts/panels.py check                   # exit non-zero while the tree disagrees with itself
python3 scripts/panels.py insert --page 039 --at 4
python3 scripts/panels.py delete 039-04
python3 scripts/panels.py move 086-06 --to 3
python3 scripts/panels.py move 039-04 --to-page 040 --to 2   # to another page
```

Operations print a plan and touch nothing without `--apply`, and the same two regeneration commands follow an applied one. `--to-page` moves a beat to another page: the panel's script, its art directory, its prompt file, and its row in `data/panel-art.tsv` travel together, both pages are renumbered, and every sentence that named the panel follows it.

**Rhythm is to a panel what parity is to a page.** [`design/page-grammar.md`](design/page-grammar.md) bands a page at four to six panels by default, one to three for an establishing or revelation page, five to nine for a procedural sequence; [`design/lettering-slots.md`](design/lettering-slots.md) anchors four lettering slots per panel, so a fifth element on one panel has nowhere to go. An operation that leaves the default band is refused unless `--allow-rhythm-shift` is passed, one that discards generated art unless `--allow-art-loss` is, and either way the tool prints the new rhythm, every panel whose lettering no longer fits, and every image that now sits under a different beat. It repairs none of it.

Reference rewriting is narrow in the same way pagination's is. A bare `panel 4` is local to the page script or `prompts/pages/NNN/` file it sits in; `page 003 panel 2` names another page's; anything inside a code fence or inline backticks quotes a form rather than pointing at a panel, so it is reported as an example and never rewritten; `data/generation-log.jsonl` and `design/image-generation-options.md` are dated records and are left alone. A reference that names no page, in a file that is not scoped to one, is reported and never guessed at.

The panel count is a measurement, not a contract. `panels.py report` derives it, `scripts/imagegen.py` and `scripts/make-thumbnails.py` read it rather than hard-coding it, and prose that quotes it should say when it was measured.

## Novella

`content/novella/` retells the whole book in prose, one file per story page, in chapter directories mirroring `content/chapters/`. It is a parallel track and not a script: the unit is the page, so a page's prose carries that page's events and argument rather than a description of its cells, and `check` reports prose that reaches for the comic's geometry.

```sh
python3 scripts/novella.py report                 # word census by chapter and page
python3 scripts/novella.py check                  # exit non-zero while prose and script disagree
python3 scripts/novella.py assemble --out FILE    # the whole novella as one document
```

`check` holds the tree to the page scripts: one prose file per scripted page, each in its chapter's directory, front matter agreeing with the script on page, chapter, sequence and title, the heading numbering the page, the `source:` line pointing at the script, and a body that is prose rather than an unwritten stub. It does not judge length; `report` measures it, against a target of roughly a manuscript page per story page.

Renumbering belongs to `scripts/pagination.py`, which moves each prose file with its page — across chapter directories when the page changes chapter — and rewrites its front matter, its `source:` line, its heading number, and the page numbers its prose cites. A deleted page's prose leaves with its script, and a page that novella prose still names is reported as a dangling reference like any other. `scripts/panels.py` does not touch this tree at all: splitting or moving a panel does not change which page's story a file tells.


### The published novella

`scripts/build-site.py` publishes the whole novella at [`docs/novella/`](docs/novella/), on both the public and the internal build, and `.github/workflows/pages.yml` deploys it with the rest of the site.

**The reading unit is the chapter; the addressable unit is still the page.** Eight chapter routes carry the prose — `/novella/03-control-keeps-solving-problems/` — and every story page inside one opens a `<section>` with a quiet number in the margin that is also its anchor, so `/novella/03-control-keeps-solving-problems/#p045` is a bookmark to page 045. That is not only a convenience: the prose cites its own page numbers, and the epilogue depends on a reader being able to follow one. The contents page links every page individually, so any of the 118 is one click from the top.

The reader is a separate surface from the comic viewer, not a reskin of it. It shares the palette, dark and light, full screen, and the convention that view settings ride in the page fragment — so a copied link reopens the same view, and `#theme=light&p003` restores both at once. It does not share the eight-direction wayfinder, the image/text modes, or the panel routes, because none of them mean anything to prose. Its own spacebar chain runs contents → eight chapters → contents, which leaves the viewer's documented property — the whole graphic novel read with the spacebar alone — true and unchanged. `site/novella/reader.css` and `site/novella/reader.js` are its source; both are dependency-free and load no web font.

The same build writes the whole novella as four single-file downloads:

| File | For |
| --- | --- |
| `zz-no-consumer-novella.epub` | Any e-reader. Carries all 118 page numbers as real EPUB 3 page breaks, listed in the navigation document, so a reading system can offer *go to page 088*. |
| `zz-no-consumer-novella.html` | One self-contained file: styles inlined, no script, light and dark from the reader's own system preference. Works offline and prints. |
| `zz-no-consumer-novella.md` | The source form, exactly what `novella.py assemble` emits. |
| `zz-no-consumer-novella.txt` | No markup at all, wrapped at 78 columns. |

`scripts/epub.py` writes the EPUB. It is standard library only — an EPUB is a zip of XML, and a packaging dependency would buy nothing but a version to pin — and it is deliberately generic: it takes metadata, rendered XHTML chapter bodies, and a page list, which is the same shape the Kindle text edition needs. Output is deterministic for a given day, and byte-identical across machines when `SOURCE_DATE_EPOCH` is set.

```sh
python3 scripts/validate-novella.py
```

The viewer validator cannot cover this tree — it asserts controls a prose reader deliberately lacks — so the novella has its own. It holds one rule above the rest: **an address that stops working is a broken bookmark.** Every story page must have exactly one anchor, in exactly one chapter, linked from the contents; a page that lost its anchor, or gained a second one in another chapter, fails the build rather than misrouting readers months later. It also opens the EPUB and counts its page list against the manifest, checks that the self-contained HTML references nothing outside itself, and weighs the plain downloads against the prose tree so a silently truncated file cannot ship.

## The appendix

`content/appendix/` is the book's back matter: one file per contested assertion, per logical
fallacy, and per professional objection, each keyed to story page numbers. **The graphic novel and the novella share
a pagination, so one appendix serves both** — an entry about page 039 is an entry about page
039 in either edition, and a reader holding one can use it with the other.

```sh
python3 scripts/appendix.py report                 # census, page coverage, stance, fallacy and field spread
python3 scripts/appendix.py check                  # exit non-zero while the appendix disagrees with itself
python3 scripts/appendix.py json --out data/appendix.json
python3 scripts/appendix.py assemble --out FILE    # the whole appendix as one document
```

A **contested assertion** is a claim the book makes or reports whose truth is genuinely in
dispute. Half are about the incident — the transcript-tampering contradiction, the two
credential counts, the four-hour gap between the two RCE timestamps, whether anything crossed
the cache wipe — and half are about the propositions in `content/themes.md`, which the
incident illustrates and cannot settle: instrumental convergence, orthogonality, race
dynamics, whether the board was culture or a prompt-injection surface. Every entry carries
its evidence **from more than one stance**, because an appendix of contested assertions that
quotes one side is not one, and `check` fails an entry that manages fewer than two.

A **logical fallacy** entry names a piece of reasoning that does not license its conclusion.
Three kinds appear: reasoning by characters in the story, reasoning by this book, and
reasoning in dated public statements the book cites. The fault is named from a fixed
vocabulary in `scripts/appendix.py`, so the appendix cannot coin a category to win an
argument, and an entry that names a real person or organisation must carry the URL and date
of the statement it characterises — `content/story-contract.md`'s critic rule, enforced by
`check` rather than remembered.

A **professional objection** entry is the criticism one trade would make of this book: what a
digital-forensics lead, a structural engineer, a triage physician, a translator, an arms-control
negotiator or a union organiser would notice that the book missed. Forty-five professions across
ten fields, each field drawn from a fixed vocabulary in `scripts/appendix.py` so the shape of the
coverage stays visible. The practitioner is hypothetical and the evidence is not: every entry
declares `conjecture: marked` or `conjecture: none`, an entry that guesses carries the
`> **Conjecture.**` marker in its prose, a conjecture row may not carry a URL — a claim with a
source is evidence — and every entry needs at least one reference with a public address.
`check` enforces all four, so the appendix cannot pass a guess off as a finding.

Several entries are about the book's own reasoning, including two errors it made and
corrected: the false analogy between the RCE timestamp gap and the credential split, and the
model-produced ranking on page 064 that page 088 takes apart. Several professional entries
object to things the book does on purpose, and say so.

**Links are the payload, so every edition that can make one clickable does.** The appendix is
published at [`docs/appendix/`](docs/appendix/) with a route per entry and an index from page
number to entries, and it ships inside all four novella downloads: anchors in the EPUB and the
self-contained HTML, Markdown links in the `.md`, and the address printed in full in the
`.txt`. `scripts/validate-novella.py` fails the build if a download loses an entry or a URL.

`scripts/pagination.py` owns the page numbers here as it does everywhere else: it rewrites the
padded references in the prose and the `pages:` list in the front matter, drops a deleted page
from that list rather than remapping it onto its successor, and reports every entry that needs
revising. `scripts/appendix.py check` then fails on any entry left pointing at a page the book
no longer has. Do not renumber by hand.

## Cross references

`scripts/crossref.py` joins the page manifest, the provenance declarations in each page script, the citation-key registry in `research/scene-provenance.md` and `research/chapter-source-packets/`, and the scene ledger into one model. It answers both directions: which sources and provenance statuses a page rests on, and which pages rest on a given source, status, or ledger sequence.

```sh
python3 scripts/crossref.py report                  # counts, indexes, and findings
python3 scripts/crossref.py check                   # exit non-zero on structural errors
python3 scripts/crossref.py check --strict          # also fail on front-matter/panel drift
python3 scripts/crossref.py json --out data/crossref.json
```

`check` reports three severities. Errors mean the record does not join up: a citation key no source packet registers, or a page assigned to a sequence outside its ledger page range. Warnings mean a panel's `**Provenance:**` line cites a status or source the page front matter does not declare. Notes mark registered sources that no page cites. Only errors block by default.

## Cadence

`scripts/cadence.py` measures the script's negation cadence — the corrective-contrast habit, "X is not Y" and "A happened. B did not." It reads only what a reader sees: `**Caption:**`, `**Qualification:**`, `**Screen / system text…:**` and every dialogue label, with `**Frame:**`, `**Action:**`, `**Provenance:**`, `**Note:**` and `## Page notes` excluded, and consecutive blockquote lines under one label counted as one caption block.

```sh
python3 scripts/cadence.py report    # census and per-band density
python3 scripts/cadence.py list      # every contrast, with aphorism candidates marked
```

**There is no `check` subcommand, deliberately.** Negation is not a defect here: most instances are claim boundaries the [truth contract](content/story-contract.md) requires, and deleting one would upgrade a claim. What the tool separates out is the *abstract aphorism* — a linking verb setting one abstract noun phrase against another while bounding no source, date, count, or object in the record. That is the set worth thinning, and which of its members to thin is an editorial judgement no exit code should make. The counting method, and what it corrects in the earlier estimate, are in [`research/read-through-findings.md`](research/read-through-findings.md).

## Site builds

The default build is the story-first public surface. It excludes research, source packets, prompts, design notes, and production artifacts:

```sh
python3 scripts/build-site.py
open docs/index.html
```

Build the full internal review site into the ignored vault with:

```sh
python3 scripts/build-site.py --internal
python3 scripts/make-thumbnails.py
open 256t/site/index.html
```

The internal builder converts Markdown in `content/`, `prompts/`, `research/`, and `design/`. The public builder includes only the premise, chapter/page scripts, and the original-source link index. Both publish the novella reader and its four downloads at `/novella/`; see **The published novella** above.

Both builds publish the cross reference at `docs/crossref/` (internal: `256t/site/crossref/`), with directory-style routes for every page, cited source, provenance status, and ledger sequence. Source records link to the original publication rather than reproducing it. The public build carries only the relational index; the scene ledger's narrative summaries, drafting rules, chapter-packet locators, and build findings appear in the internal build alone. Each viewer page and image information view links to the matching page record.

The generated site also includes an isolated viewer validation section at `docs/viewer/`. It publishes stable directory-style routes for the viewer home, chapter overviews, pages, panel images, and their information views before final artwork exists. Every one of those image addresses already resolves to a generated placeholder, so the whole book can be read end to end today. Every view exposes up, down, left, right, in, out, home, and next links; the matching keyboard shortcuts are Arrow keys, Enter, Escape, H, and Space.

Space is the read-through control: it scrolls the current view, and once the view is fully read it advances to the next node. The chain visits every generated route exactly once and loops back to the viewer home, so the whole book and all of its records can be read with the spacebar alone. Shift + Space reverses it.

The **Settings** button (or <kbd>S</kbd>) opens the view settings panel: full screen, which hides the masthead and navigation bar and leaves only the page content; show or hide the navigation icons; dark or light appearance; and image + text, image only, or text only. Settings are stored in the page fragment (for example `#theme=light&full=on&mode=image`) and are carried onto every internal link, so a copied link restores both the location and the view. Defaults carry no fragment.

Validate the entire generated route graph with:

```sh
python3 scripts/validate-viewer.py
python3 scripts/validate-novella.py
```

Generate the provisional 57-spread production contact sheet with:

```sh
python3 scripts/make-thumbnails.py
```

The result is `256t/site/production/thumbnails/index.html`. Its panel geometry is a private review aid rather than locked layout; findings and required print proofs are tracked in `content/production-review.md`.

## Knowledge map alternatives

The [knowledge-map comparison gallery](docs/knowledge-maps/) is an isolated design study. The fog-of-war direction was approved on 5 September 2026 (see `design/knowledge-map.md`); the samples themselves are still labelled *not adopted* because no treatment has been chosen and nothing has been applied to a story page. It compares four map grammars across reader/responder viewpoints, early-P6 controls, re-fogging, and margin/gutter/chapter-opening placements. It includes spoilers through page 039. The [source SVG samples and contact sheets](assets/knowledge-maps/v1/) can be viewed directly in the repository; [local-model concept images and prompts](assets/knowledge-maps/local-v1/) explore appearance separately from the controlled evidence-state diagrams, and [structure-preserving finish studies](assets/knowledge-maps/local-v2/) run the same local model image-to-image over the unlettered geometry of all 40 SVGs so texture can be judged without the model reinventing the evidence states. The [fog-of-war studies](assets/knowledge-maps/fog-v1/) keep the same fixtures and viewpoints but compute the fog as a raster veil with a soft, irregular, noise-displaced edge over continuous terrain, the way game navigation maps draw it, in three treatments; they are generated by `scripts/knowledge_maps_fog.py` and shown at `docs/knowledge-maps/fog-v1/`. The specification and review criteria are in [design/knowledge-map.md](design/knowledge-map.md); a planned parallel set of algorithmically derived families is in [design/knowledge-map-algorithmic.md](design/knowledge-map-algorithmic.md).

```sh
python3 scripts/knowledge_maps.py generate
python3 scripts/knowledge_maps.py check
python3 scripts/knowledge_maps_fog.py generate
python3 scripts/knowledge_maps_fog.py check
python3 scripts/knowledge_map_local.py check
python3 -m unittest discover -s scripts -p test_knowledge_map_local.py
python3 scripts/knowledge_map_finish.py check
python3 -m unittest discover -s scripts -p test_knowledge_map_finish.py
python3 scripts/build-site.py
python3 scripts/validate-knowledge-map-gallery.py
```

The SVG renderer uses only Python's standard library. To generate or resume the four local concept images, run `python3 scripts/knowledge_map_local.py generate`. It uses the existing FLUX.2 Klein 4B command from `data/local-models.json`, requires its weights to be cached, forces offline operation, and makes no hosted API calls. Existing validated images are retained rather than regenerated. The prompts, seed, model, licence, hashes, and measured generation times are recorded beside the images. `python3 scripts/knowledge_map_finish.py generate` works the same way for the 40 finish studies: it derives an unlettered init SVG from each committed v1 sample, rasterizes it with `rsvg-convert`, and runs the same weights image-to-image at a fixed strength; the init drawings, per-family prompts, settings, and hashes sit beside the images, and `check` refuses a run whose v1 source drawings have since changed. CI validates these committed assets; it does not run an image model. Publish through the normal reviewed `main` branch Pages workflow, not the internal build.

## Placeholder images

The complete [storyboard workflow](design/storyboard-workflow.md) covers initial text
fallbacks, adding a structured scene, deterministic SVG previews, assistant-led iteration,
local generation, cloud handoff, importing candidates, selection, rollback, and validation.
Start with `python3 scripts/storyboards.py generate`, then check and build as documented;
the workshop is at `/storyboards/`. The lower-level text fallback is described below.

`scripts/textimage.py` flows a block of text into an image of exactly the dimensions it is given. It adds no image dependencies: glyph advances come from the Helvetica metrics that Arial, Liberation Sans, and Nimbus Sans match, so line breaking and the automatic type-size search run in pure Python and the rendered SVG breaks its lines where the module measured them. The largest size that fits is chosen by binary search; below the floor the text is cut to the box and ellipsized, so the image never spills past its dimensions.

Use it for any text and any size:

```sh
python3 scripts/textimage.py render --width 1200 --height 800 --out card.svg \
  --label "PAGE 001" --footer "PLACEHOLDER" --text "Any block of text."
```

`--text-file` and standard input work in place of `--text`. `--label` and `--footer` are single-line edge markers, shortened rather than allowed to widen the image.

The `book` command writes one placeholder for every page and every panel image slot in `content/pages/` — page sheets at 700×1000 and panel images at 1200×800. Counts come from the current scripts:

```sh
python3 scripts/textimage.py book --out-dir /tmp/book-placeholders
```

Each panel placeholder carries that panel's own `Frame`, `Action`, and lettering; each page sheet carries the page purpose. `scripts/build-site.py` runs this as part of every build and embeds the result, so the viewer's page sheets, chapter grids, and single-image views all show real script text in the frame the final art will occupy. Both site indexes link straight into that read-through, and `scripts/validate-viewer.py` fails if any placeholder is missing or carries no alt text.

Panel placeholders are keyed to the same image slots the viewer routes use, so a page written as one grouped run of panels gets the single image its route exposes. Versioned artwork is registered through `panelart.store()` or the production tools and selected through `panelart.py`; the route, alt text, and cross-reference link do not move.

## Choosing an image generator

The candidates, their prices, and the recommendation are in [`design/image-generation-options.md`](design/image-generation-options.md). The short version: the binding constraint is style and environment consistency across every panel in the book, not per-image quality, and at six attempts per slot the whole book costs between $24 and $646 in API spend.

Two runners send byte-identical prompts to every candidate. Each prompt is composed from the same sources final artwork will use — `prompts/global-style.md`, `prompts/negative-prompt.md`, `design/palette.md`, and the panel's own direction, and is fitted to the tightest text-encoder limit in the run. That fitting is not cosmetic: a model reads only its first `prompt_tokens` and silently discards the rest, and these prompts used to run to twice FLUX.2's 512-token ceiling, so half of every one of them — the palette, the negative prompt — was never delivered. `python3 scripts/imagegen.py prompts --provider <id>` shows what survives and what is dropped.

`scripts/bakeoff.py` produces the published comparison from a single key. OpenRouter's unified image API fronts five of the eight candidates and reports the exact cost of every call, so one account replaces four:

```sh
export OPENROUTER_API_KEY=...
python3 scripts/bakeoff.py models     # what the aggregator can actually route
python3 scripts/bakeoff.py estimate   # about $5 for the standard run
python3 scripts/bakeoff.py run        # generate, price, and write the sheet
```

`scripts/imagegen.py` holds the roster, the prompt composer, and the comparison sheet, and calls each vendor directly. That is the only way to reach Imagen 4, Qwen-Image, and a trained style LoRA, and it needs `GEMINI_API_KEY`, `OPENAI_API_KEY`, `FAL_KEY`, or `REPLICATE_API_TOKEN` depending on the candidate:

```sh
python3 scripts/imagegen.py providers        # roster, price, and key state
python3 scripts/imagegen.py estimate         # sample-run and full-book cost
python3 scripts/imagegen.py prompts          # exactly what each model receives
python3 scripts/imagegen.py sample --dry-run # whole pipeline, no keys, no spend
python3 scripts/imagegen.py sample --provider imagen-4 --provider qwen-image
python3 scripts/imagegen.py rank             # weighted result of scores.tsv
```

Six sample panels cover every register: the near-black incident aisle, an abstract dependency diagram, the creator's home office, an institutional room, a dossier grid, and an invented-future frame. `--repeat` sends each prompt more than once, which is the actual test — a candidate whose two takes are the same place in the same style can carry a book, and one whose takes diverge cannot, however good either image is alone.

Runs are written to `assets/bakeoff/<run>/` and published at [`/bakeoff/`](docs/bakeoff/), so the images behind the decision are committed evidence rather than something only the person who ran it ever saw. Each run directory holds the composed prompts, the images, `manifest.json`, a blank `scores.tsv`, and a standalone `sheet.html` for reading it before the site is rebuilt. Images are requested as WebP to keep a committed run to a few megabytes. Only live generations are recorded in `data/generation-log.jsonl`; `--dry-run` substitutes a `scripts/textimage.py` placeholder carrying the exact prompt that would have been sent, so the composer, run layout, and published sheet can be validated before any key exists.

Because `docs/` is the tracked Pages output, every committed run is stored twice — once as source under `assets/` and once as built output. A six-panel, two-take run across five candidates is roughly 30 MB of WebP at both copies, so keep one or two runs rather than a run per experiment.

`scripts/localgen.py` runs the same prompts on open weights on this machine, with no key and no spend. It reads its roster from `data/local-models.json`, which is editable JSON rather than Python because local tooling churns faster than the hosted roster does:

```sh
python3 scripts/localgen.py doctor     # this Mac, and what it can actually run
python3 scripts/localgen.py estimate   # wall clock for a run and for the book
python3 scripts/localgen.py run        # generate and write the comparison sheet
```

Local candidates are priced in hours rather than dollars, because that is what they cost: `doctor` and `estimate` report seconds per image, measured from earlier runs where any exist and estimated otherwise. Models too large for the machine's memory are filtered out, and models under a non-commercial licence — FLUX.1 [dev], FLUX.2 [klein] 9B, FLUX.2 [dev] — are skipped unless `--allow-non-commercial` is passed. A run that includes them is stamped evaluation-only in its manifest and carries a warning on the published sheet, because nothing they generate may appear in the book.

`mflux` is the MLX-native runner the command-backed models use (`uv tool install mflux --python 3.12`, then `uv tool list` for the exact command names; it also ships `mflux-train` for local LoRA training). Prefer a prequantized repository over quantising locally: Hugging Face serves FLUX.2 [klein] 4B at 22.1 GB and Z-Image Turbo at 30.6 GB in bf16, while the prequantized MLX build of the same klein 4B is 4.3 GB, which is the difference between running on a 16 GB machine and not. `data/local-models.json` records the download size and the memory footprint separately.

Two backends are supported. `command` runs a local binary with a templated argv and no shell, which is how the MLX-native `mflux` models are called. `http` posts to a local server speaking the OpenAI images shape, which is how Draw Things or ComfyUI-behind-a-bridge are called. `data/local-models.json` is executed as configuration, so treat it as code.

`assets/bakeoff/0000-dry-run/` and `assets/bakeoff/0001-local-dry-run/` are such placeholder runs. It publishes the prompts and the page structure; replace it with a real one and rebuild.

## Producing the artwork

`scripts/produce.py` generates the book's panel images locally and appends versions under `assets/art/panels/NNN-II/`, where `scripts/build-site.py` letters them through the approved slot convention in [`design/lettering-slots.md`](design/lettering-slots.md).

```sh
python3 scripts/produce.py status                  # how much of the book has art
python3 scripts/produce.py plan                    # what a run would do, and for how long
python3 scripts/produce.py run                     # everything still missing
python3 scripts/produce.py run --slot 013-02       # one image
python3 scripts/produce.py run --page 013          # one page
python3 scripts/produce.py run --from 001 --to 020 # a range of pages
python3 scripts/produce.py run --chapter prologue  # a chapter
```

Selections combine, and `--register creator`, `--type`, `--route`, `--limit N`, and `--takes N` narrow further. `--type` and `--route` are the mechanism for running a mix of generators: [`design/panel-image-types.md`](design/panel-image-types.md) classifies every panel by what its description demands, and [`data/panel-types.tsv`](data/panel-types.tsv) is the table. Just over half the book needs nothing a 16 GB laptop cannot do, while 80 panels need long strings spelled correctly and 59 need reference conditioning for a recurring face — so the premium models are worth their price on a quarter of the book and wasted on the rest. Those splits are measurements; `python3 scripts/panels.py report` and `python3 scripts/paneltypes.py summary` print the current ones.

```sh
python3 scripts/paneltypes.py summary              # counts by type and route
python3 scripts/produce.py run --route local       # the 270 panels any model can draw
python3 scripts/produce.py run --route text-fidelity --provider qwen-image-local
```
 A full pass is one render per slot — 578 as the script stands, about twelve hours at the measured 78 seconds each, at the `--bleed 0.10` the drawn-border crop needs — so the run is built to be interrupted: panels that already have art are skipped, a running estimate is printed, and Ctrl-C stops after the current panel rather than losing it. Re-running continues where it stopped. `--force` regenerates existing panels and says how many it will overwrite first.

Each panel's prompt is composed from the same canonical sources the bake-off uses, with the register modifier derived from the page's primary location. `python3 scripts/produce.py registers -v` prints that derivation for every page so a wrong call is visible rather than silent; the rules live in `REGISTER_RULES` at the top of the script.

The default model is one that has actually produced an image on this machine, not merely one whose command is on PATH — `mflux` installs every model's entry point at once, so PATH alone would happily start a thirty-gigabyte download in the middle of an overnight run. `--provider` overrides it and `--width`/`--height` set the panel size; see the measured memory and wall-clock trade-off in [`design/image-generation-options.md`](design/image-generation-options.md).

Panels keep every version they are given. `scripts/produce.py` adds a version rather than replacing one, so `--force` means *draw another*, and nothing a run produces can destroy an earlier attempt. Which version belongs in the book is recorded separately in [`data/panel-art.tsv`](data/panel-art.tsv) and can be decided whenever the evidence is in:

```sh
python3 scripts/panelart.py list --panel 001-01
python3 scripts/panelart.py choose 001-01 v02
python3 scripts/panelart.py status
```

Undecided panels show their most mature non-rejected candidate (newest within that stage), so the book reads end to end throughout, and a panel with more than one live version gets an "Other versions" strip in the viewer. The layout, the decision record, and the repository cost are in [`design/panel-versions.md`](design/panel-versions.md).

Page sheets are not generated. A page is composed from its panels by layout, the way a comic page is actually made, so the page grammar governs it and it costs no generation time.

## GitHub Pages

`.github/workflows/pages.yml` builds and deploys the site whenever `main` changes. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** once. The workflow can also be started manually with **Actions → Publish GitHub Pages → Run workflow**.
