# Two Anthill implementation — 9 September 2026

## Applied

- Current book branding is *The Two Anthill Problem*. The builder, novella assembler and
  thumbnail generator share `scripts/book_metadata.py`. Browser titles, reader masthead,
  landing page and download titles use it. The masthead mark has two unconnected surfaces.
- Current editorial headings, credits and licence title are renamed. Repository slug,
  routes and download filenames stay stable. The historical name is explained in the README
  and source apparatus. Receipts and historical research remain historical.
- The page 012 wordmark remains incident treatment, explicitly authored rather than a
  self-chosen population name. Its check and the chapter/beat-sheet references are renamed.
- Page 108 retains the naming echo. Its caption no longer relies on the old book title;
  its storyboard has no vertical barrier. The alphabetical-sweep qualification remains.
- The publication-relative creator scene on page 114 carries the dated title decision,
  the visibly rejected connector, separate kept hills and reconstructed dialogue. The
  novella mirrors the editorial action without extending the metaphor across incident prose.
- The visual bible defines both ant registers, no individual-run correspondence,
  nonquantitative density, surface-only hills, protected evidence fields and no causal
  connectors. Continuity, themes, story contract and map guidance carry the same boundary.
- FQ-21 explains the title, attribution, literary influences, stigmergy comparison and the
  limits of corpora A/B/C. LF-30 records the conscious-superorganism inference risk. FQ-09
  no longer promises access to the whole record. The wiki README’s obsolete “uncited” claim
  is corrected.
- `EK-TONER` has a narrow source admission and assessment. The video’s auto-captions confirm
  the supplied passage at 28:00 (context 27:53; repeated in the cold open). Date is supplied
  with the source; the public text paraphrases. The full raw export stays in the ignored
  vault. Additional interview claims and the named-person LF-22 example remain unadmitted.

## Visual study

The site builder generates `docs/anthill-study/`: a cover using existing fog texture,
unchanged labelled reader/responder and before/after re-fog maps, and canonical storyboard
compositions with a separate static margin/gutter layer. The cover is authored texture,
not a wiki proposition model. The study explicitly identifies that remaining design work.

`anthill_study.py check` resolves current page identities by title, rejects ant overlap with
panel rectangles, checks deterministic output and retained re-fog. It runs in the existing
production-foundations validator. No independent page-keyed data needs renumbering.

The ordinary reader uses updated versioned storyboards for the changed scenes. Its overlays
and raster selections are not expanded throughout the book. Previous art versions remain.
New reusable ant and surface-hill shapes enter the existing storyboard library.

Visual review covered the cover, creator composition, original map comparisons and the
360 px study setting; the ordinary reader was checked at 360 px in dark and light themes
and image/text modes. Tiny ants remain small marks at that width; this is an explicit
limitation of the fixed-page composition, not a claim that every detail is readable there.

## Validation and local operational effects

Baseline: strict cross-references, novella, appendix and complete storyboards passed;
118 story pages and 590 storyboard slots were measured before editing. The appendix had
31 existing informational notes about references without public URLs, with no errors or
warnings. Identity checks retain informational ambiguous-reference warnings for a README
example and a historical artwork note; the plan’s ambiguous panel references were qualified. The revised appendix has 120 entries, including the two new entries.

The full local CI sequence was run. Its first run found two actionable follow-ons:
`knowledge_maps.py` needed regenerated manifest source hashes, and the changed story contract
invalidated the contract hash of three prepared local artwork jobs. Inspection also found
older target-size/lettering snapshots in those jobs; their geometry needs review before replacement. All other steps passed, including build,
lettering, identity tools, both unittest modules and built-site/link checks. The two failed
checks were rerun successfully after repair. Final source/build verification also passed: 1,898 HTML documents and EPUB/Markdown links
had zero link findings; viewer, novella, built storyboard and page-link validators passed,
as did `git diff --check`. The EPUB title and HTML title inventory were checked directly.
Detailed first-run command output remains in `/tmp/anthill-validation.log`.

The three original `handover-*` jobs have zero attempts and are explicitly blocked with
reasons. Their saved inputs are preserved. The queue checker now accepts stale source hashes
for explicitly blocked history while still checking image integrity; claim, retry and
acceptance still reject stale work. An offline fixture checks that a blocked stale job
cannot return to generation. Replacement preparation needs review of their existing geometry and lettering snapshots.

## Remaining decisions and work

- Review the cover and pilot before whole-book ant placements or raster regeneration.
- Define the wiki-specific proposition/viewpoint model before adopting fog-map hills in
  the story. Existing Artifactory viewpoints are not relabelled as the second incident.
- The novella-wide metaphor treatment remains deferred by the owner.
- Corpus C needs the owner’s deferred redaction decision, actual vendor exports and a
  reviewed public cut. `design/production-corpus-release.md` supplies a concrete proposed
  inclusion/omission and redaction protocol. Add citation validation against real release
  locators when that cut exists; no placeholder transcript corpus is advertised as published.
- Preserve the no-rate ceiling: relevance-selected transcripts do not supply an unbiased
  denominator. Preserved exchanges do not automatically upgrade reconstructed scenes.
- Board-dump acquisition and wiki reuse correspondence remain external actions. No messages,
  commit, push or deployment were performed by this implementation.

## Old-title inventory

Intentional current occurrences: page 012’s incident wordmark, its novella counterpart,
the page 003 scene title, and editorial explanations of those distinctions. Historical
research, prior artwork versions, prompts saved with those versions, and the append-only
generation log retain their original identity. Technical URLs and filenames retain the
repository slug. No blanket replacement was applied to `zz`, `ZZZ` or `zzHELP_`.
