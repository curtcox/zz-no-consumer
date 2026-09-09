# Credits

This is the single list of the people, sources, models and tools behind *The Two Anthill Problem*. The published site renders it as its credits page, and the book's endmatter is set from it; do not maintain a second copy. Last checked 9 September 2026.

## Author

- **Curt Cox** — writer, researcher, and the named autobiographical creator-character. The contract governing what the book may claim is [`content/story-contract.md`](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md).

## AI systems, and what they did

The book says on the page that it was made with an AI's help; this list says which ones and how.

- **ChatGPT** appears in the creator scenes as the model Curt asks to organise and dramatise the incident record. Its dialogue is reconstructed and compressed unless a page note identifies a preserved exchange.
- **Claude** (Anthropic; the Opus 5, Fable 5.1 and Opus 4.8 models, through Claude Code) co-authored repository commits: page scripts, research packets, planning documents, and the validation, pagination, cross-reference, lettering and site-generation tooling. Co-authorship is recorded commit by commit in the Git history. Its register entry, and the open question of whether the recursion sequence should disclose a second model, are in [`content/creator-characters.md`](https://github.com/curtcox/zz-no-consumer/blob/main/content/creator-characters.md).

  **Opus 4.8 is listed because the model in use was twice replaced automatically, mid-task, by a safety fallback.** On 15 July and 5 September 2026 a `cyber`-category refusal switched the session from Fable 5 and Fable 5.1 to Opus 4.8, retracting prior messages; the successor completed work that is in the Git history, including `scripts/novella.py` and the first prose tree. The commit trailers for that stretch name a model that did not write the commit, and no trailer records a mid-session switch. Both events, their verbatim notices, and the limits on what they may be used to claim are in [`research/creator-instrument-record.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/creator-instrument-record.md).
- **Devin** (Cognition's AI coding assistant; powered in this session by GPT-6 Astra Medium Thinking) works with Curt in the repository through the terminal and IDE, with tools for inspecting files, proposing and making edits, and running checks. Its contribution in this session is documentation and AI-contribution disclosure: clarifying its identity and role in these credits at Curt's request. This is a repository-assistant credit, distinct from ChatGPT's on-page role; it does not attribute earlier writing, research, tooling or image generation to Devin.
- **Codex** (OpenAI) assisted the September title revision, matching script and novella edits, source assessment, appendix updates, deterministic anthill studies, prompt and provenance checks, and site tooling. This credits repository work; it does not turn the reconstructed ChatGPT dialogue into a transcript.
- **FLUX.2 [klein] 4B** (Black Forest Labs; the `RunPod/FLUX.2-klein-4B-mflux-4bit` weights, Apache-2.0), run locally through `mflux` with no hosted API, produced the local-model artwork: the local bake-off runs, the panel-art candidates in `assets/art/panels/`, and the knowledge-map concept and finish studies. Local-model generations are logged with model, seed and path in `data/generation-log.jsonl`. Built-in image-tool candidates have separate receipts beside their versioned panel assets. Models under a non-commercial licence are excluded from anything that could appear in the book.

- **OpenAI’s built-in image tool** produced additional panel-art candidates. Their adjacent `builtin-image-pilot` and artwork-job receipts identify the tool, prompts, references and image hashes; model revision and seed are unspecified when the tool did not expose them.
- **Deterministic SVG artwork** — storyboards, ant geometry and composition overlays — is rendered by repository code from authored geometry. It is separate from model-generated raster art; the cover study reuses a disclosed local-model fog texture.

## Sources

The book paraphrases public writing and links to it rather than reproducing it. The original publications are indexed in [`content/source-links.md`](content/source-links.md); the full source index with reliability tiers is [`research/sources.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/sources.md).

- **Primary incident record:** OpenAI's incident disclosure, overview and technical report; Hugging Face's disclosure and technical timeline; the METR/Redwood independent investigation and its methodology; the Black Hat USA 2026 talk by OpenAI staff; JFrog's vulnerability findings; the AISI comparative report.
- **Named commentators whose dated public writing is paraphrased:** Dwarkesh Patel; Gavin Leech and Lucca Fraser (Paradigm 3); Ajeya Cotra; Ryan Greenblatt; Beth Barnes; Zvi Mowshowitz; Clem Delangue; Leo Gao; Roon; Ashim Mahara; Daniel Krol; Carl Brown (Internet of Bugs), whose published critique of the civilization framing is paraphrased on page 039. The relationship of each to the record is in [`research/cast.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/cast.md). Being cited is not endorsement of this book or its reading.
- **Title and explanatory influences:** Helen Toner’s image relayed in Ezra Klein’s interview, credited by her to an unnamed person; Francis Heylighen’s account of stigmergy; the literary echoes of Liu Cixin’s *The Three Body Problem* and Douglas Hofstadter’s Ant Fugue in *Gödel, Escher, Bach*. The title FAQ distinguishes these influences from incident evidence.
- **The collaboration-wiki corpus** (`CW-EXPORT`, `CW-REPORT`) is credited to the collusion.wiki custodians and the report by Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts and Thomas Larsen. Attribution does not settle reuse rights; see item 3 of [`research/revision-priorities.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/revision-priorities.md).

- **Apache Ant logo:** Apache Software Foundation project mark, supplied by Curt for a small background print in the reconstructed creator scene. Its inclusion implies no Apache endorsement or incident involvement. The supplied image remains third-party material, outside the licence grant for project-authored work. See [Apache Ant](https://ant.apache.org/).

## Tools

- Python 3 standard library for every validator, the pagination and panel tools, the cross reference, the placeholder and lettering renderers, the knowledge-map renderers, and the site builder.
- `mflux` (MLX) for local image generation; `rsvg-convert` (librsvg) for rasterising SVG.
- GitHub Pages for publication. The placeholder and lettering renderers measure text with Helvetica metrics and fall back to Arial, Liberation Sans and Nimbus Sans.

## Licence

The whole repository, book and tooling alike, is released under the [GNU General Public License, version 3 or any later version](https://github.com/curtcox/zz-no-consumer/blob/main/LICENSE), chosen 5 September 2026 so that it can be forked as one thing. Three things the licence does not cover, because they are not the project's to license: the third-party sources the book paraphrases and links to; the wiki edit corpus, republished on its custodians' terms; and the model weights behind the generated images, which carry their own licences. Nothing produced by a non-commercial-licensed model may appear in the book.

## Provenance vocabulary

Every panel is tagged `documented`, `source-paraphrase`, `disputed`, `inferred`, `reconstructed`, or `invented`; the tags are defined in [`research/scene-provenance.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/scene-provenance.md) and searchable on the site's cross reference.
