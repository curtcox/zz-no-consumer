# Credits

This is the single list of the people, sources, models and tools behind *ZZ: NO CONSUMER*. The published site renders it as its credits page, and the book's endmatter is set from it; do not maintain a second copy. Last checked 5 September 2026.

## Author

- **Curt Cox** — writer, researcher, and the named autobiographical creator-character. The contract governing what the book may claim is [`content/story-contract.md`](https://github.com/curtcox/zz-no-consumer/blob/main/content/story-contract.md).

## AI systems, and what they did

The book says on the page that it was made with an AI's help; this list says which ones and how.

- **ChatGPT** appears in the creator scenes as the model Curt asks to organise and dramatise the incident record. Its dialogue is reconstructed and compressed unless a page note identifies a preserved exchange.
- **Claude** (Anthropic; the Opus 5 and Fable 5.1 models, through Claude Code) co-authored repository commits: page scripts, research packets, planning documents, and the validation, pagination, cross-reference, lettering and site-generation tooling. Co-authorship is recorded commit by commit in the Git history.
- **FLUX.2 [klein] 4B** (Black Forest Labs; the `RunPod/FLUX.2-klein-4B-mflux-4bit` weights, Apache-2.0), run locally through `mflux` with no hosted API, produced every generated image committed so far: the local bake-off runs, the panel-art candidates in `assets/art/panels/`, and the knowledge-map concept and finish studies. Each generation is logged with model, seed and path in `data/generation-log.jsonl`. No hosted image provider has produced a committed image. Models under a non-commercial licence are excluded from anything that could appear in the book.

## Sources

The book paraphrases public writing and links to it rather than reproducing it. The original publications are indexed in [`content/source-links.md`](content/source-links.md); the full source index with reliability tiers is [`research/sources.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/sources.md).

- **Primary incident record:** OpenAI's incident disclosure, overview and technical report; Hugging Face's disclosure and technical timeline; the METR/Redwood independent investigation and its methodology; the Black Hat USA 2026 talk by OpenAI staff; JFrog's vulnerability findings; the AISI comparative report.
- **Named commentators whose dated public writing is paraphrased:** Dwarkesh Patel; Gavin Leech and Lucca Fraser (Paradigm 3); Ajeya Cotra; Ryan Greenblatt; Beth Barnes; Zvi Mowshowitz; Clem Delangue; Leo Gao; Roon; Ashim Mahara; Daniel Krol; Carl Brown (Internet of Bugs), whose published critique of the civilization framing is paraphrased on page 039. The relationship of each to the record is in [`research/cast.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/cast.md). Being cited is not endorsement of this book or its reading.
- **The collaboration-wiki corpus** (`CW-EXPORT`, `CW-REPORT`) is credited to its custodians once its reuse terms are recorded; see item 3 of [`research/revision-priorities.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/revision-priorities.md).

## Tools

- Python 3 standard library for every validator, the pagination and panel tools, the cross reference, the placeholder and lettering renderers, the knowledge-map renderers, and the site builder.
- `mflux` (MLX) for local image generation; `rsvg-convert` (librsvg) for rasterising SVG.
- GitHub Pages for publication. The placeholder and lettering renderers measure text with Helvetica metrics and fall back to Arial, Liberation Sans and Nimbus Sans.

## Licence

The whole repository, book and tooling alike, is released under the [GNU General Public License, version 3 or any later version](https://github.com/curtcox/zz-no-consumer/blob/main/LICENSE), chosen 5 September 2026 so that it can be forked as one thing. Three things the licence does not cover, because they are not the project's to license: the third-party sources the book paraphrases and links to; the wiki edit corpus, republished on its custodians' terms; and the model weights behind the generated images, which carry their own licences. Nothing produced by a non-commercial-licensed model may appear in the book.

## Provenance vocabulary

Every panel is tagged `documented`, `source-paraphrase`, `disputed`, `inferred`, `reconstructed`, or `invented`; the tags are defined in [`research/scene-provenance.md`](https://github.com/curtcox/zz-no-consumer/blob/main/research/scene-provenance.md) and searchable on the site's cross reference.
