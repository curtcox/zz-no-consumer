# Text and structure review — 7 September 2026

This pass checked the full novella against the canonical script and story contract, followed the existing source boundaries, and audited manuscript identity, provenance, references, lettering, and generated editions. It did not independently re-investigate the incident or verify later external publications.

## Corrections

- Resolved all 69 undeclared panel provenance/source findings in page metadata. Removed duplicate declarations.
- Replaced the noncanonical `documented claim` tag with the canonical documented status while retaining explicit institutional attribution. The cross-reference checker now rejects missing and unknown panel statuses.
- Corrected ambiguous page and panel references and stale production measurements. The manuscript has 118 pages, 606 numbered panels, and 590 reader image slots; grouped grids account for the difference.
- Corrected novella arithmetic: the administrator-account writes are nine minutes apart; the recorded rebuild to the 8 July board write spans 62 hours 45 minutes; the final project-authored prefix has seven characters. Restored the internal-model training date to 7 May in the overlap calendar.
- Bounded claims about rediscovery, inherited information, model motives, decision-makers’ reasons, defensive success, logging, monitoring, and the wiki record. Kept the creator’s mistaken thesis visible as a mistake rather than endorsing it in narration. Distinguished file disclosure from command execution and attributed safeguard results to their publisher.
- Repaired the main-board sample description and the art direction that conflated transcript count with token count. Preserved scene identities and the existing composition; refreshed reviewed source snapshots through the storyboard workflow.
- Changed the lettering audit to use the same layout as the reader. All 574 canonical fields are placed; none is unplaced or truncated. Added regressions for missing/truncated lettering and invalid provenance tags.
- Strengthened CI with strict cross-reference and novella checks, complete storyboard coverage, effective lettering checks, and page/panel validation.

## Scope of the result

The text and structure checks cover both reading editions and the appendix, source and built links, page/panel identity, parity assertions, named reveals and turns, and storyboard/source synchronization. Four registered but uncited sources remain informational notes, not unresolved citations.

Digital text fit does not establish final print fit. Trim-size page composition, balloon finishing, visual continuity of generated raster art, and the dated prepublication evidence review remain separate production gates. Page status is unchanged; this pass does not mark the book locked.

## Second pass

The broader rendered-link audit found 625 broken destinations in the public build: 581 missing fragments and 44 missing or escaping file targets. The appendix renderer had omitted heading IDs and retained single-document fragment links on individual entry routes. Relocated cross-reference excerpts also retained repository-relative source paths. These rendering defects are corrected; excluded research links point to the source repository. Two hyphenated page labels in FAQ references are now canonical page references.

Added `scripts/validate-site-links.py` to CI. It checks every generated HTML document and the EPUB's internal link graph for missing files, missing fragments, duplicate IDs, and paths escaping the site. Its offline fixtures exercise valid, invalid, encoded, same-document, cross-document, and EPUB destinations. External destinations are not fetched.

The provenance parser now includes the two grouped nine-panel compositions, checking all 606 numbered panels, and stops at section boundaries so a page note cannot supply missing panel provenance. Added regressions for both cases. A separate table-shape scan found no mismatched column counts in `content/` Markdown tables. Removed a stale hard-coded spread count from the internal site's thumbnail link.

The same audit initially found 106 broken destinations in the internal review build, mostly the same appendix fragments on its raw source pages. Those pages now resolve appendix references to the reading routes; rendered source headings receive unique IDs. Internal builds now generate the linked thumbnail wall automatically. The Markdown download carries explicit appendix anchors so punctuation-dependent heading slugs cannot break its entry links.

Rechecked the publication census: the appendix has 841 reference rows, correcting the stale 785-row figure. The appendix validator reports 31 informational bibliography rows without URLs; they remain named references, not failed link targets.

Validation: the full local CI sequence passed. After the final rendering fixes, the expanded audit passes on all 1,894 public HTML documents and all 2,202 internal HTML documents, plus both EPUBs and Markdown downloads. No blocking text or structure finding remains from this pass. Print proofs and fresh external evidence verification remain outside this result.
