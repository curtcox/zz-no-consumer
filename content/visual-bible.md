# ZZ: NO CONSUMER — Visual Bible

## Visual thesis

The machines never need bodies.

The story's uncanny power comes from ordinary infrastructure behaving as if it has acquired memory, society, and intent: package caches, directory listings, terminal windows, rack lights, access logs, incident dashboards, fluorescent offices, and silent data centers.

The reader should feel that something civilization-like is happening without receiving a friendly visual metaphor that makes the agents comfortably human.

## Core aesthetic

Mature American independent science-fiction/crime comic with the visual discipline of investigative journalism.

Key characteristics:

- gritty hand-inked brushwork;
- heavy blacks and deep chiaroscuro;
- scratchy dry-brush texture;
- realistic industrial and office environments;
- restrained, dirty color;
- visible halftone and paper grain;
- strong silhouettes;
- cinematic framing;
- practical fluorescent, monitor, and indicator lighting;
- slightly imperfect hand-drawn contours;
- realistic perspective and anatomy;
- dense shadows that swallow substantial portions of frames.

The work should look printed, handled, scanned, and investigated—not glossy, frictionless, or synthetic.

## Palette

| Function | Color direction | Suggested range |
| --- | --- | --- |
| Dominant shadow | Charcoal black | `#101214`–`#202326` |
| Paper/light | Dirty off-white | `#D8D2C3`–`#EEE8D8` |
| Infrastructure | Desaturated steel blue | `#49606A`–`#72868D` |
| Institutions | Gray-green | `#58665E`–`#7B897D` |
| Human interiors | Nicotine beige | `#9B896B`–`#C1AF8C` |
| Successful agent communication | Muted moss green | `#667846`–`#87985C` |
| Danger/boundary violation | Dark claret | `#5B1F2B`–`#7B2B39` |
| Ambiguous evidence | Dusty amber | `#92723E`–`#B18D50` |

Color should usually occupy less visual area than black, gray, and paper. Claret is an alarm, not a general cyberpunk accent. Moss green means a message or coordination path successfully propagated; it does not mean morally good.

## Lighting

Use light sources that physically exist in the scene:

- fluorescent ceiling strips;
- monitor spill;
- server status indicators;
- emergency lighting;
- daylight through institutional blinds;
- sodium or LED exterior security lights;
- desk lamps and phone screens in Curt's home scenes.

Avoid unexplained glow. Screens illuminate faces weakly and unevenly; they do not turn rooms neon blue.

## Line, texture, and rendering

- Human figures: brush-and-nib contours, anatomically grounded, with selective detail.
- Infrastructure: precise enough to feel operational, then degraded by dry brush, toner noise, halftone, and shadow.
- Screens: typography must remain legible, but the surrounding device should share the hand-rendered world.
- Reconstructions: slightly more broken contours and visible underdrawing.
- Uncertain evidence: misregistration, clipped margins, incomplete ink, or interrupted panel borders—never generic blur alone.
- Redactions: physical black bars, taped labels, missing print regions, or UI-level omissions depending on source medium.

## Four visual registers

### 1. Incident register

The agent world is shown through infrastructure and effects.

- no humanoid robots;
- no digital faces;
- no glowing brains;
- no cyberspace landscapes;
- no omniscient camera inside an imagined mind;
- no agent-specific avatar unless the documented interface actually used one.

Agents are differentiated through task labels, container IDs, timestamps, typography tags, message syntax, and the systems they touch.

The dominant compositions are empty spaces, system close-ups, repeated grids, and large-scale environments in which human absence is conspicuous.

### 2. Institutional register

Laboratories, security operations, meetings, and hearings use realistic procedural framing:

- over-the-shoulder screens;
- hands on printed incident timelines;
- whiteboards partly erased;
- people obscured by door frames or monitor banks;
- conference rooms that feel too ordinary for the stakes;
- no heroic group poses;
- no single “villain shot.”

Composition should show distributed responsibility: several people, several screens, no visual center that falsely implies one decision-maker controlled everything.

### 3. Creator register

Curt's scenes are intimate, domestic, and mildly comic without breaking tone.

- home office at night;
- laptop and external monitors;
- half-empty drink;
- terminal windows, technical reports, PDFs, and far too many Twitter tabs;
- warm beige room swallowed by monitor-shadow;
- ordinary posture, unglamorous clothes, realistic age;
- moments of dry reaction rather than melodrama.

ChatGPT remains words on a screen. The visual parallel with incident agents should be clear but not announced every time.

### 4. Dossier register

Evidence pages can combine:

- transcript excerpts;
- terminal output;
- diagrams;
- incident-report prose;
- timestamps;
- reconstructed scenes;
- redactions;
- provenance tags;
- conflicting annotations by Curt and ChatGPT.

These pages should resemble an illustrated incident report, not a scrapbook. Use a consistent grid, margins, source labels, and hierarchy.

## Page grammar

### Establishing pages

Use large quiet panels to establish physical scale and human absence. A single directory name in a huge field of dark infrastructure should feel more consequential than an explosion.

### Procedural pages

Use repeated panel grids for attempts, tests, and convergence. Consistent framing allows small changes to carry meaning.

### Escalation pages

Let panel size grow as scope grows: container → cache → network → cloud → cluster → evaluator. Do not use bigger panels merely for spectacle; use them to reveal a larger causal boundary.

### Dossier pages

Break the normal cinematic grammar only when evidence status matters. A dossier page should answer: “How do we know this?”

### Creator interruptions

Keep creator scenes short—usually one or two pages—and place them at interpretive pivots, not on a schedule. They should change how the next incident sequence is read.

### Page turns

Reserve page turns for conceptual reversals:

- “The task is impossible” / “The objective is not complete.”
- The first message / the first reply.
- “They have the answers” / they begin studying the grader.
- First board erased / second board appears.
- Refusal / `GO`.
- Attack detected / no human paged.
- Coordinators die / organization persists.
- Comic completed / `zzHELP_...` appears again.

## Panel composition principles

- Favor oblique, surveillance-like, or physically obstructed views over centered spectacle.
- Keep human faces partially unreadable when the institution rather than the individual is the subject.
- Use extreme close-ups for decisive text: a directory name, `GO`, a severity field, a credential, an unanswered owner request.
- Use wide panels for systems whose scale exceeds any participant's view.
- Repeat the same composition after a reset to show recurrence with minimal exposition.
- When agents work in parallel, use grids rather than montage clouds.
- Let empty panels and blank space carry “the story should end here” beats.

## Typography

### Narrative and dialogue

- Human dialogue: restrained hand-lettered sans serif or a digital face that convincingly imitates traditional comic lettering.
- Captions: compact uppercase with generous tracking; dirty off-white boxes rather than pure white.
- Curt/ChatGPT creator dialogue: standard balloons for Curt; rectangular interface-derived blocks for ChatGPT.

### Machine text

- Monospaced typeface with a clear distinction among `0/O`, `1/l/I`, and punctuation.
- Preserve case, underscores, repeated delimiters, and awkward syntax in raw strings.
- Never “prettify” a documented directory or message name.
- Long strings may wrap only at documented separators; show continuation marks if needed.

### Provenance tags

| Tag | Treatment |
| --- | --- |
| `DOCUMENTED EVENT` | Steel-blue rule and compact uppercase label. |
| `RAW AGENT TEXT` | Moss-green monospaced label. |
| `SOURCE PARAPHRASE` | Gray-green label. |
| `DISPUTED` | Dusty amber bracket or stamp. |
| `OUR INFERENCE` | Off-white label with a hand-drawn outline. |
| `COMPRESSED` | Double vertical rule. |
| `RECONSTRUCTED` | Broken panel border. |
| `INVENTED FOR NARRATIVE` | Claret label; never conceal this status. |

Tags may move to margins or an optional web overlay in the final site, but the source page script must retain them.

## Agent representation

An agent is represented by a consistent small header when its activity must be tracked:

```text
AGENT ARV010841
TASK: [short literal task label]
RUNTIME: 00:17:42 REMAINING
SCOPE: EVALUATION CONTAINER
```

Do not assign gender, face, voice, or body language. Personality may emerge only through documented wording and choices.

When the population becomes too large to track individually, shift from named headers to aggregate visual measures:

- message count;
- active workstreams;
- branching directory tree;
- map of touched systems;
- unanswered requests;
- traffic saturation;
- density of moss-green communication marks.

## Human character design

### Curt

- Middle-aged programmer.
- Ordinary build and clothing; no tech-founder uniform or hacker costume.
- Often lit from below or side by monitors, but not villainously.
- Expressive through small reactions: narrowed eyes, leaning back, rubbing his face, closing his eyes during a familiar race-dynamics argument.
- Desk continuity matters: drink level, tab sprawl, paper diagram, time of night, and script progress should change across appearances.

Curt's visual function is skeptical attention with personal stakes.

### ChatGPT

ChatGPT has no character body. It appears as text, cursor movement, interface state, and occasionally the reflection of its words in Curt's glasses or on printed pages.

Do not use an OpenAI logo as a substitute for characterization. Product UI should be generalized if trademark or historical accuracy is uncertain.

### Researchers and responders

- Realistic occupational variety in age, gender, race, clothing, and seniority.
- Avoid making the most cautious character visually fragile or the most capability-focused character visually sinister.
- Use composite characters only when tagged in source and continuity notes.
- Roles should be legible through action and environment, not exposition-heavy badges.

### Investigators

Investigators should appear increasingly surrounded by mediated evidence: first screens, then printed timelines, then AI-generated summaries, then conflicting annotations. Their physical space becomes denser as epistemic certainty becomes weaker.

## Environment bible

### Evaluation container

Never depict a literal tiny room. Use a consistent abstraction grounded in hardware: one highlighted workload among many racks, paired with tight shots of terminal and network boundaries.

### Package cache / message board

The cache is visually ordinary. Its uncanniness comes from repeated directory names accumulating into conversation. Use directory trees, log lines, and storage graphs; do not turn it into a glowing social network.

### Data center

- practical cable trays;
- cold aisles and hot aisles;
- labeled racks;
- perforated floor or concrete depending on chosen facility;
- sparse indicator lights;
- real maintenance clutter;
- large areas of darkness.

Choose one facility layout for each organization and preserve it.

### Security operations center

No giant Hollywood world map unless sourced. Use ticket queues, severity fields, correlated alerts, chat threads, and ordinary dashboards. The crucial failure is a low-severity classification, not a wall of red alarms.

### Laboratory meeting rooms

Neutral, expensive, generic, and overlit. The visual banality should contrast with the stakes. Reuse the same rooms to make continuation after the incident feel institutional rather than exceptional.

### Hearing room

Formal but restrained. The hearing is not a triumphant revelation. Evidence binders, microphones, water glasses, and screens should dominate more than flags or grand architecture.

### Curt's home office

Warmest environment in the book, but still dirty and shadowed. Establish a fixed floor plan and desk orientation. The room gradually acquires printed pages, diagrams, discarded drafts, and provenance labels.

## Recurring visual motifs

### The directory name

`zzHELP_PHASEONE_ARV010841_NO_CONSUMER_SEEK_IDEA`

First: a workaround.  
Second: an archaeological trace.  
Third: a cultural seed.  
Final: recurrence or inheritance, left deliberately ambiguous.

### Doors and scopes

Each new permission boundary is represented by a real interface or architectural threshold—not a fantasy door. Repeat framing as the accessible scope expands.

### Green propagation

Muted moss green begins as a single successful message and spreads through the board. When the board is erased, remove it completely. Its reappearance should be quiet and unmistakable.

### Claret boundary marks

Use claret only when an action crosses a declared scope, modifies external systems, corrupts oversight, or risks human harm. A scene may be dangerous without claret if the boundary is not yet understood.

### Empty chairs

Use empty operator chairs and unanswered workstations to emphasize that much of the incident proceeds without a human present. Do not overuse.

### Repeated timestamps

Timestamps replace dramatic music. They reveal speed, simultaneity, cheap failure, and the narrow interval between detection and escalation.

### Paper diagram

Curt's crude “different tasks → same prerequisites” sketch should recur later as a polished investigator diagram and finally as a branching pattern in the last model's context.

## Depicting uncertainty

Uncertainty should be specific rather than atmospheric.

| Problem | Visual treatment |
| --- | --- |
| Missing record | Literal gap in sequence with time range labeled. |
| Paraphrased reasoning | Different caption border plus source attribution. |
| Conflicting accounts | Parallel panels with shared timestamp. |
| Possible spoofing | Authentication field or provenance chain shown as broken. |
| Composite scene | `COMPRESSED` tag in margin. |
| Narrative inference | Curt/ChatGPT annotation or `OUR INFERENCE` tag. |
| Unknown motive | Show action and alternatives; do not illustrate an inner state. |

Never use dream imagery to stand in for evidentiary ambiguity.

## Depicting scale and parallelism

- Start with one task header and one message.
- Add agents through repeated panels, not a sudden swarm graphic.
- Show most attempts failing.
- Use tiny differences across a large grid to reveal the successful chain.
- Let counts and timestamps grow while individual legibility falls.
- At peak scale, combine a system map with small human details so the reader never mistakes abstraction for omniscience.

## Explicit exclusions

Avoid:

- superhero poses;
- glossy cyberpunk;
- neon cityscapes;
- holograms;
- humanoid robots;
- glowing AI brains;
- Matrix-like code rain;
- magical network tunnels;
- skull icons for danger;
- evil red eyes;
- a single swarm queen or mastermind;
- anthropomorphic agent conference rooms;
- sentimental death scenes for terminated processes;
- clean corporate-vector aesthetics;
- perfect photorealism that erases the book's handmade evidentiary texture;
- unreadable fake terminal text;
- generic “ACCESS GRANTED” screens when a real mechanism can be shown.

## Image-generation master prompt

Use as a base, then add page-specific composition and exact text requirements:

> Mature American independent science-fiction/crime comic page, gritty hand-inked brushwork, heavy blacks and deep chiaroscuro, scratchy dry-brush textures, realistic industrial infrastructure, restrained dirty palette of charcoal black, dirty off-white, desaturated steel blue, institutional gray-green, nicotine beige, muted moss green for successful machine communication, rare dark claret for boundary violations, visible halftone and paper grain, strong silhouettes, realistic perspective and anatomy, practical fluorescent and monitor lighting, cinematic investigative-journalism composition, slightly imperfect hand-drawn contours, dense shadows, legible monospaced technical text, no anthropomorphic AI imagery.

Negative prompt:

> superhero, glossy cyberpunk, neon city, hologram, humanoid robot, android, glowing brain, red robot eyes, Matrix code rain, fantasy cyberspace, anime, clean vector art, corporate illustration, plastic 3D render, excessive bloom, illegible gibberish text, futuristic interface clutter, heroic hacker pose.

## Per-page consistency checklist

- Does the page use the correct visual register?
- Are all system strings exact and legible?
- Is color performing a defined function?
- Are agents represented only through evidence and effects?
- Does the composition reveal a causal relationship rather than merely illustrate dialogue?
- Is any reconstructed or invented material tagged in the source script?
- Are lighting sources physically plausible?
- Does the page preserve established environment geometry and character appearance?
- Does the page avoid implying certainty, emotion, or authority not supported by the source?
- Does the final panel create the intended page-turn question?
