# Global Style

## Rendering target

Mature independent science-fiction/crime comic with investigative-journalism discipline: gritty hand-inked brush and nib contours, heavy blacks, dry-brush abrasion, restrained halftone, dirty paper grain, realistic anatomy and perspective, practical industrial detail, and slightly imperfect hand-made registration.

## Composition

- Render exactly one single panel that fills the whole image: one continuous scene,
  edge to edge. Never a page layout, a grid of panels, gutters between images, a
  drawn panel border or frame, a speech balloon, a tail, or a page number. The page
  is assembled from separate panel images afterwards; an image containing more than
  one panel is unusable and has to be generated again.
- Prefer surveillance-like, physically obstructed, or off-center framing over heroic spectacle.
- Show agent activity through task cards, system surfaces, infrastructure state, timestamps, and consequences—never a body, face, avatar, glowing brain, or imagined private room.
- Establish cause spatially: inputs, permissions, shared services, boundaries, and outputs must remain readable even before lettering.
- Render the panel's own display strings as legible, correctly spelled text on the screens,
  cards, and labels that carry them. These strings are project-authored, so they are the
  words the panel is supposed to show. Invented or approximate lettering is worse than none:
  if a string cannot be rendered accurately, leave that surface blank rather than guessing.
- Two text systems, and only one is yours. In-scene text — what a screen, card, or label
  physically shows in the world — is drawn. Captions, dialogue balloons, and provenance
  slates are not: they are applied afterwards on a controlled lettering layer. Leave the
  upper-left and lower-right corners as quiet, near-empty dark areas with no drawn caption
  box, balloon, or slate in them, and keep essential forms out of gutters and trim zones.
- Use repeated geometry when state changes across attempts, populations, or evidence accounts.

## Composition (compact)

One panel filling the image, edge to edge: no panel grid, no gutters, no drawn border or frame, no speech balloon, no page number. Frame it off-center and obstructed rather than heroic. Show the agents only as task cards, surfaces, infrastructure state and consequences, never as a body, face or avatar. Add no people the panel has not asked for. Draw the panel's own display strings and nothing else — leave every other surface blank rather than inventing words for it. Captions, dialogue and provenance slates belong to a later lettering layer, so do not draw them, and keep the upper-left and lower-right corners quiet.

## Light and material

Every light has a physical source: fluorescent tubes, monitor spill, rack indicators, daylight through blinds, sodium exterior light, or a desk lamp. Screens illuminate weakly and unevenly. Metal is scuffed and matte; paper is handled; offices are ordinary; data centers contain plausible racks, cable trays, blanking plates, floor or slab, and maintenance clutter.

## Register modifiers

Each register names the place its panels happen in, not a mood. The geometry
here is the canonical environment set in
[`design/visual-continuity.md`](../design/visual-continuity.md); keep the two in
step when either changes.

- **Incident:** A windowless facility interior built from concrete slab floor, matte dark equipment racks, overhead black cable trays, rack endcaps with small neutral number plates, and a service-cart silhouette. Deep blacks, cold steel, sparse paper, weak reflected light from rack indicators. No people. These are the materials the panel is made of; the panel's own direction decides the framing and how close the camera stands.
- **Institutional:** An ordinary working room under flat overhead fluorescent light: shallow workstation rows, modest wall displays, a long neutral table, acoustic wall panels, a partly erased whiteboard, binders and plain laminate. Overlit, gray-green, procedural. No world map, no flags or seals, no head-of-table hero composition, no villain lighting.
- **Creator:** One ordinary suburban home office at night: a wooden desk against a dark wall, two external monitors with a laptop centred below, a desk lamp camera-left, a drink camera-right, a printer and paper stack behind the chair, a doorway deep in the background. Warm nicotine-beige lamplight, domestic and unglamorous, at desk scale. Not a server room, not a control room, not a factory: no racks, no cable trays, no industrial machinery, no banks of monitors.
- **Dossier:** A paper field seen nearly flat-on: printed pages, source-summary cards, timestamp gutters, redaction bars and uncertainty marks laid out in a strict grid on a neutral surface. Documentation gray on handled paper. Almost no room around it and very little scene depth.
- **Invented future:** A plain, evenly lit interior with nothing identifying in it: neutral surfaces, generic screens, unbranded fittings. No logo, seal, wordmark, date, geography or recognizable architecture, and none of the incident facility's rack-and-cable-tray geometry.

## Output discipline

Render the panel's own project-authored display strings accurately. Everything else stays out: no third-party wording, logos, credentials, QR codes, code, commands, paths, URLs, or source screenshots, and never source typography reproduced closely enough to imply quotation. Captions, dialogue, and provenance are separate controlled production layers, so do not draw them. Any glyph the panel did not ask for is a defect.

## Palette rules

Most images remain charcoal, paper, and desaturated infrastructure color. Moss appears only when shared-state communication or inheritance succeeds. Claret appears only at a known boundary crossing or harmful consequence. Amber marks a specific evidence gap or dispute.

## Palette (compact)

Charcoal, dirty paper and desaturated infrastructure color throughout. Moss, claret and amber appear only where the story earns them; nothing else.
