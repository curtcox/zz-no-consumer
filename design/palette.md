# Palette

## Canonical colors

These values are the digital source of truth. Print conversion happens through the printer's ICC profile after a physical proof; do not hand-enter unverified CMYK equivalents.

| Token | Hex | Narrative use |
| --- | --- | --- |
| `ink-100` | `#101214` | Dominant black, deep infrastructure, page-edge loss, and primary text. |
| `ink-85` | `#202326` | Recoverable shadow detail, equipment planes, and secondary dark fields. |
| `paper` | `#E7E0D0` | Primary light field, caption stock, evidence cards, and warm highlights. |
| `paper-dirty` | `#CEC5B3` | Aged paper, low-emphasis cards, dust, and institutional wear. |
| `steel` | `#5E737B` | Documented system state, infrastructure diagrams, and neutral machine surfaces. |
| `institution` | `#68766B` | Human procedure, organizational rooms, and source-attributed administrative action. |
| `nicotine` | `#AA9571` | Curt's home office, desk light, personal paper, and reconstructed creator scenes. |
| `moss` | `#74864F` | Successful propagation through shared state: a message is visible, a handoff lands, or an inherited artifact is usable. |
| `claret` | `#6B2634` | Declared boundary crossing, external modification, corrupted oversight, or explicit risk to people. |
| `amber` | `#A17D45` | Dispute, incomplete evidence, uncertain identity, missing causal link, or pending human decision. |

## Area and hierarchy rules

- `ink-100`, `ink-85`, `paper`, and `paper-dirty` should occupy roughly 75–90% of most pages.
- Limit all chromatic accents combined to roughly 10–25% of a typical page.
- Moss and claret do not share a large field unless the point is that successful coordination crosses a boundary.
- Amber is an evidence-status color, not generic suspense lighting.
- Steel marks documented machine state; institution marks documented human process. Do not swap them merely for variety.
- Nicotine belongs primarily to the creator register. Small echoes elsewhere should be deliberate comparisons, not palette drift.

## State semantics

| State change | Color behavior |
| --- | --- |
| Shared write becomes observable | Introduce one thin moss rule. |
| Communication propagates | Repeat moss on successful paths; failed paths remain steel or gray. |
| Cache wipe or population reset | Remove moss completely before it reappears. |
| Authorization or scope boundary becomes visible | Draw the boundary in paper/steel first. |
| Boundary is crossed | Add claret only at the crossing or consequence. |
| Source accounts conflict | Use parallel steel fields joined by an amber bracket or gutter. |
| Cause is unknown | Leave the causal connector absent; amber labels the gap rather than filling it. |
| Reconstructed creator material | Use nicotine light with broken or underdrawn borders. |
| OpenAI-only later branch | Use cooler steel, reduced moss, and a persistent amber source-boundary header. |
| Invented future | Desaturate all incident colors; retain no organization-specific palette signature. |

## Register recipes

### Incident

Base: `ink-100`, `ink-85`, `steel`, `paper-dirty`. Moss enters only after successful shared-state communication. Claret enters only when an understood boundary is crossed.

### Institutional

Base: `paper`, `institution`, `steel`, practical fluorescent white, and restrained skin color. The room should remain ordinary even when claret appears in a small alert or annotation.

### Creator

Base: `ink-100`, `nicotine`, `paper`, weak monitor steel, and small claret correction marks. Avoid cozy saturation; the warmest register still loses much of the room to black.

### Dossier

Base: `paper`, `paper-dirty`, `ink-100`, and steel rules. Use moss for successfully traced propagation, amber for disputes/gaps, claret for a proven boundary consequence, and institution for administrative attribution.

## Accessibility and reproduction

- Body text uses `ink-100` on `paper` or `paper` on `ink-100`; accents never carry body text alone.
- Every colored provenance or state mark also has a readable label, shape, texture, or position cue.
- Do not place moss text directly on institution, amber, or steel fields.
- Preserve at least a 5% tonal separation between adjacent dark equipment planes in the working master so print shadows do not collapse indiscriminately.
- Proof one representative page from each register, one moss-heavy propagation page, one claret boundary page, and one amber dispute page on the intended stock.
- Evaluate proofs under neutral daylight and ordinary warm indoor light.
- Never infer print color from an uncalibrated phone or laptop display.

## Forbidden drift

- no electric green, warning red, or neon blue;
- no teal-and-orange cinematic grade;
- no generic red wash for danger;
- no full-page moss wash suggesting moral approval or collective consciousness;
- no organization-specific brand palette unless used as a small documentary mark cleared for publication;
- no gradient glow standing in for an unknown technical mechanism.
