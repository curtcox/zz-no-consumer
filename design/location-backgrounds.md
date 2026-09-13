# Location backgrounds

The palette includes 50 independent background components: all 48 IDs in panel
`Location` fields and the two additional page-level montage IDs. Component IDs are
`location-background-` followed by the exact location ID. They appear in the component
workshop's **Locations** category; search for “Background”.

Each SVG has its own silhouette and margin motif: domestic windows, receding rooms,
cache indentation, transcript gutters, dataset layers, cluster cells, separate
report margins, wiki navigation, public document leaves, terminal rails or the
future's clipped corners. Related names receive related but distinguishable views;
alternative IDs do not establish separate physical sites. Logical backgrounds are
authored diagrams, never source evidence or architectural reconstructions.

The components use quiet translucent centers, shaded edges and material-specific colors.
Backgrounds carry no lettering, people, activity indicators, credential values or
institutional logos. Foreground objects and captions remain independently editable.
The regulatory setting uses a docket surface, not an invented room for public authors.

## Application

```sh
python3 scripts/location_backgrounds.py plan
python3 scripts/location_backgrounds.py apply
python3 scripts/location_backgrounds.py refine
python3 scripts/location_backgrounds.py check
python3 scripts/storyboards.py generate
python3 scripts/storyboards.py check --complete
python3 scripts/build-site.py
python3 scripts/svg_components.py check --built
python3 scripts/storyboards.py check --complete --built
```

`plan` writes nothing. `apply` creates missing components through the versioned
component library and prepends background nodes only to eligible storyboards.
`apply` does not replace existing defaults or saved versions. `refine` saves the
authored material treatment as a new immutable version and selects it as the default;
running it again with identical designs adds nothing. It also updates existing
location-background region layouts, preserving their other node properties.
Further refinements can be saved as additional versions in the component workshop.

A scene with an existing location-category component keeps that setting. A scene
with no nodes, a `blank` shot, or a deliberately absent border keeps its authored
empty background. The ordinary `background` palette color is an undercoat, not
setting artwork. This distinguishes an unillustrated setting from an intentional
black interval or ending.

Multiple locations occupy separate regions in the field's reading order, with
empty gutters and no connecting geometry. The nine-cell grids receive evaluation
backgrounds inside their existing cell boxes; the shared-cache field stays separate
on the convergence grid. Background nodes precede all existing nodes and are not
focal subjects. Existing objects, source snapshots, frame borders, labeling and
lettering placements remain unchanged.

The initial pass filled 511 scenes and preserved 79 existing or intentionally empty
backgrounds. `check` derives current coverage from scripts and scene records, checks
palette integrity and distinct geometry, and reports background/location drift.
It does not claim that every location should be drawn as a physical room.

## Visual review

The initial palette was reviewed as a 50-item contact sheet and in 15 lettered
panels covering single settings, grouped grids, split scenes, three-way comparisons,
physical rooms, logical surfaces, evidence records and the future register.
Background lines remain subordinate to the existing objects and lettering. The
final black fields and existing location compositions remain unchanged.

## Material and combination refinement

All 50 backgrounds now have distinct material color pairs, shaded planes, beveled
motif lines and one of 13 texture families. Wood grain distinguishes the domestic
office; paper fibers and binding lines distinguish evidence surfaces; brushed metal,
mesh, ribs, glazed tiles and stippling separate the infrastructure settings. Public
web and production tooling use different cool scan-line surfaces, and the unidentified
future stays neutral. The colors identify authored settings, not incident states.
The center remains quieter than the perimeter so foreground text and objects dominate.

The 157 multi-location scenes reuse the exact same components as single-location
scenes. A combined field therefore retains each location's motif, material, color
and shading; it does not get an unrelated generic texture. Component paint IDs are
scoped per instance, preventing one region's gradients or patterns from overwriting
another's. Two through four locations occupy equal-height columns with empty gutters.
Six four-location scenes were adjusted from three upper regions and one lower region
to four columns so every location remains prominent. The grouped nine-cell exception
keeps its separate cache field.

Review covered the full palette and 12 lettered examples, including two-, three-
and four-location compositions. Foregrounds, source snapshots and lettering are
unchanged. The earlier flat versions remain available in the palette workshop.
