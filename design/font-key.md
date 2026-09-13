# Font key

The key applies to every story page, including words inside illustrations. Its
machine-readable source is `data/font-key.json`. A font identifies the kind of
utterance, not whether the utterance is true. Source attribution, dates and the
words `PARAPHRASED`, `RECONSTRUCTED` or `INVENTED` retain their ordinary force.
Never use a typeface as the only disclosure of uncertainty or invention.

| Key | Face and fallbacks | Meaning |
| --- | --- | --- |
| `narration` | Georgia; Times New Roman; serif | The book tells or explains the story. An inference must still identify itself in words. |
| `human` | Arial; Helvetica; sans serif | A human speaks. Reconstructed and composite speakers keep their scene disclosures. |
| `interface` | Verdana; DejaVu Sans; sans serif | A model or authored interface voice speaks. This does not imply an inner experience or an exact transcript. |
| `machine` | Courier New; Liberation Mono; monospace | Machine-shaped fields, identifiers and commands. Reconstruction still needs its label. |
| `editorial` | Arial Bold; Helvetica Bold; sans serif bold | Source summaries, diagram labels, environmental annotations, source headers and qualifications supplied by the book. |
| `quotation` | Georgia Italic; Times New Roman Italic; serif italic | Registered third-party wording. Registration and visible attribution remain mandatory; the face does not assert completed verification. |

A source-summary card uses `editorial` even when it sits on a screen. An actual
registered machine transcript uses `machine`, with an explicit raw-text label.
A human quotation uses `quotation`. Do not change a word, its case, or punctuation
to make it resemble another font category. Project-authored machine strings may
use `machine` without claiming documentary status.

## Source grammar

Each page declares `font_key: data/font-key.json`, `font: editorial` for titles and
source apparatus, and `illustration_font: editorial` for readable labels described
in Frame or Action directions. A deliberate exception to the illustration default
must become an explicit lettering field or a storyboard label with its own `font`.
Incidental marks that have no assigned wording remain illegible or absent.

Every Caption, Dialogue, Screen / system text, Qualification and Dossier tag is
immediately preceded by its own declaration:

```markdown
**Font:** `narration`

**Caption:**
> A RUN CAN LEAVE WORK FOR THE NEXT RUN TO FIND.
```

Put the font declaration immediately before a Persistent banner heading. It applies
to every line in that banner. Multiple paragraphs inside one lettering field use
the same font; use separate fields for distinct voices. Source comments and font
keys are production directions, never words to letter inside the art.

Every readable storyboard node label has a `font` property. Composition boxes
control placement; they do not override the source font. Existing raster artwork
is immutable: any accidental drawn glyphs require an artwork correction, not a
font metadata edit. All intentional story lettering belongs to the controlled
SVG overlay or to controlled vector labels, never to image-model approximations.

## Rendering and checks

`letterpress.py audit` checks the source declarations and effective lettering fit.
Both automatic slots and manual storyboard placements retain the source key.
The SVG carries `data-font-key`, an explicit family, style and weight. Font-specific
conservative widths and explicit SVG line lengths keep wrapping deterministic
across fallback faces. These width allowances are layout bounds, not a claim of
exact font metrics. Inspect a print proof before locking pages. Raster flattening
requires the specified local face and fails rather than silently substituting it.

Keep captions near the existing density guideline; extra text should explain a
term, a causal step, or an evidence boundary. Do not fill a silent panel merely
because it has room. The final caption remains the last readable story text.
