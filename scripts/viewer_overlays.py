#!/usr/bin/env python3
"""Preview-only overlay layers for the local viewer: image, lettering, ants, fog.

The local display composes a page from stored panel art and the controlled
lettering layer. These four switches let a reviewer look at a page with any of
those contributions withheld, without touching a stored decision: nothing here
writes artwork, scene records, or `docs/`.

Two of the layers are authored figures rather than book structure, and the
edition convention in `content/visual-bible.md` governs both:

  * **Ants** come from the authored geometry that already exists — the `ant`
    nodes inside a scene, and the marginal route `anthill_study.placements`
    draws for the pages listed in `data/anthill-study.json`. The viewer invents
    no placement of its own, so page 108's deliberate exclusion stays excluded.
  * **Fog of war** is the construction of `knowledge_maps_fog`, on a page
    instead of a map: a seeded heightfield hillshaded from the upper left, many
    pictograms scattered over it and draped so their outlines take the shape of
    the ground beneath them, and a veil computed from the panel rectangles that
    thins in patches, so a form is obscured and revealed by the fog rather than
    sitting on it. Everything below the sampling grid is quoted in that module's
    units and left at its values, so the look is its own rather than a second
    tuning of the same idea. The forms are its vocabulary and carry none of its
    meaning: a page has no propositions and no observation islands, so they are
    drawn from the whole set ungrouped, and every one keeps clear of every
    panel, so no artwork is under them. Two departures a page requires: the
    relief is drawn only outside the panels, since a page's cleared ground is
    the book rather than terrain, and open ground thins to exactly what a panel
    keeps, so the layer never outshines the artwork. It is authored preview
    texture. It is not a map of the wiki, not a measure of what any observer
    knows, and it neither reveals nor resolves anything.

A layer can only be withheld where the geometry is still separable. A panel
whose current art is exactly its scene's render can give up its ants, because
the render can be repeated without those nodes; a raster chosen from a model
cannot, and says so on its face rather than pretending the layer is gone.
"""
from __future__ import annotations

import base64
import html
import math
from array import array
import random
import struct
import zlib

import anthill_study
import knowledge_maps_fog as fogmap
import panel_layout
import storyboards

LAYERS = {
    'image': ('Panel art', 'The chosen picture inside each panel.'),
    'lettering': ('Lettering', 'Controlled captions, dialogue, and slates, drawn last.'),
    'ants': ('Ants', 'Authored ant figures: scene nodes and the marginal route. Nonquantitative, with no run correspondence and no trail between incidents.'),
    'fog': ('Fog of war', 'Authored preview texture: relief and draped pictograms on the margins and gutters, under a veil that thins in patches. Not a map of the wiki and not a measure of what is known.'),
}
DEFAULTS = {name: True for name in LAYERS}
PAGE_LAYERS = ('fog', 'ants')
# Hills are surfaces and the Apache Ant logo is scene content; neither is an ant figure.
ANT_ASSETS = ('ant',)

# The fog is the studies' own construction at page size. Everything below the
# cell size is quoted in their units and left at their values, so the look is
# theirs rather than a second tuning of the same idea; `study_units` converts.
FOG_CELL = 5         # page units per fog sample
RELIEF_CELL = 10     # and per height sample: landforms are broad, the fog is not
FOG_FEATHER = 14     # soft edge either side of a panel boundary
FOG_DRIFT = 30       # how far the noise displaces that edge
CLEARED = 0.16       # veil left over a panel, so the layer stays legible over art
# The studies let contested ground clear further than this, but on a page the
# artwork is the one thing the layer must never outshine, so open ground thins
# to exactly what a panel keeps and no further.
MARGIN_FLOOR = CLEARED
MARGIN_RANGE = 1 - CLEARED  # up to ground that shows nothing at all
# Where that field turns from open to closed. The studies read this band across
# a region already known to be contested; a page has no such region, so the band
# sits low enough that unexplored ground is the rule and a clearing the
# exception. It stays wide, because a veil that is either off or on hides the
# relief it is lying on.
OPEN_EDGE = (-0.28, 0.12)
RELIEF = 42          # height of the broad landforms, and of the detail on them
DETAIL = 9
DRAPE = 9.0          # how far a unit of slope pulls a mark laid across it
DRAPE_LIMIT = 26     # page units, so a pulled mark still cannot reach a panel
INK_LEVEL = 16       # the luminance of the ink token: the floor of the ramp
# Pictograms on the fogged ground. The forms are the study vocabulary; the page
# geometry is this module's, and the fog is the only thing that hides them.
# Measured from the forms themselves rather than assumed: a turned form can put
# its furthest point in any direction, so that reach is what a placement clears.
GLYPH_RADIUS = max(math.hypot(x, y) for polys in fogmap.GLYPHS.values()
                   for poly in polys for x, y in poly)
GLYPH_SCALE = (1.7, 2.9)
GLYPH_CLEAR = 14      # page units a form keeps away from every panel and the page edge
GLYPH_SPACING = (25, 37, 56, 81, 105, 136)  # how far apart two forms may fall
GLYPH_DETAIL = 5      # page units below which a form's own outline is not resampled
FOG_CACHED_PAGES = 12  # rendered grounds kept, so a spread and its neighbours stay warm
GLYPH_GROUND = 24000  # square page units of fogged ground per form
GLYPH_STROKE = 2.0    # stroke in glyph units, so weight scales with the form


# ------------------------------------------------------------- the selection


def normalize(value, base=None):
    """A complete, validated switch set. A partial object updates `base`."""
    base = DEFAULTS if base is None else base
    if not isinstance(value, dict):
        raise ValueError('Overlay selection must be an object of layer flags')
    unknown = sorted(set(value) - set(LAYERS))
    if unknown:
        raise ValueError(f'Unknown overlay layer: {", ".join(unknown)}')
    if any(type(flag) is not bool for flag in value.values()):
        raise ValueError('Overlay flags are true or false')
    return {name: value.get(name, base[name]) for name in LAYERS}


def signature(overlays):
    """A stable URL token, so a display refetches when the selection changes."""
    return ','.join(name for name in LAYERS if overlays[name]) or 'none'


def parse(token, base=None):
    """Read a signature back. An absent token means the caller's own selection."""
    base = DEFAULTS if base is None else base
    if token is None:
        return dict(base)
    names = [] if token == 'none' else token.split(',')
    return normalize({name: True for name in LAYERS if name in names} |
                     {name: False for name in LAYERS if name not in names})


# --------------------------------------------------------------- panel layer


def scene_ants(key, data):
    """The authored ant nodes in this panel's scene, if it has any."""
    scene = data.get('scenes', {}).get(key)
    if not scene:
        return None, []
    return scene, [node for node in scene['nodes'] if node['asset'] in ANT_ASSETS]


def art_without_ants(key, art, size, data=None):
    """`(href, note)` for a panel asked to drop its ants.

    `href` replaces the stored art; `note` marks a panel that could not give the
    layer up. Both are empty when the panel has no authored ants to remove.
    """
    data = storyboards.load() if data is None else data
    scene, ants = scene_ants(key, data)
    if not ants:
        return None, None
    if art is None or art.suffix.lower() != '.svg':
        return None, 'ANTS NOT SEPARABLE · STORED IMAGE'
    try:
        stored = art.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None, 'ANTS NOT SEPARABLE · STORED IMAGE'
    if stored != storyboards.render(scene, data, size=size):
        return None, 'ANTS NOT SEPARABLE · STORED IMAGE'
    kept = [node for node in scene['nodes'] if node['asset'] not in ANT_ASSETS]
    return storyboards.svg_uri(storyboards.render(dict(scene, nodes=kept), data, size=size)), None


def note_mark(text, width, height):
    """A legible tag on a panel whose stored art keeps a layer it was asked to drop."""
    pad = round(width * 0.018)
    size = max(16, round(height * 0.030))
    bar = round(size * 1.7)
    box = round(len(text) * size * 0.62) + 2 * pad
    return (f'<g aria-hidden="true" style="pointer-events:none">'
            f'<rect x="{pad}" y="{pad}" width="{min(box, width - 2 * pad)}" height="{bar}" '
            f'fill="#101214" fill-opacity="0.85"/>'
            f'<text x="{pad * 2}" y="{pad + round(bar * 0.68)}" fill="#E7E0D0" '
            f'font-family="monospace" font-size="{size}">{html.escape(text)}</text></g>')


def frame_mark(width, height):
    """Where the picture is withheld, the panel rectangle still has to read."""
    return (f'<g aria-hidden="true" style="pointer-events:none">'
            f'<rect x="2" y="2" width="{width - 4}" height="{height - 4}" fill="none" '
            f'stroke="#6E7A66" stroke-width="4" stroke-dasharray="24 16"/></g>')


def annotate(svg, marks):
    """Append preview marks inside the panel, after everything the book draws."""
    if not marks:
        return svg
    head, _, tail = svg.rpartition('</svg>')
    return head + ''.join(marks) + '</svg>' + tail


# ---------------------------------------------------------------- page layer


def ant_pages():
    """Pages with an authored marginal route. The viewer adds none of its own."""
    return {int(page): enabled for page, enabled in anthill_study.cases()}


def has_page_ants(page):
    return bool(ant_pages().get(int(page)))


def page_ants_svg(page, panel_count):
    w, h = panel_layout.load()['page']
    poses = anthill_study.placements(panel_layout.rectangles(panel_count),
                                     has_page_ants(page))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>Page {int(page):03d} — authored marginal ants</title>'
            '<desc>Flat authored marks in the page margin. Their number and spacing measure '
            'nothing, no route joins the two incidents, and they reveal no fog and resolve '
            'no question.</desc>'
            '<g aria-hidden="true" style="pointer-events:none">'
            + ''.join(anthill_study.ant(*pose) for pose in poses) + '</g></svg>')


def rect_distance(x, y, rect):
    """Signed distance from a point to a rectangle; negative inside it."""
    rx, ry, rw, rh = rect
    dx = max(rx - x, 0.0, x - (rx + rw))
    dy = max(ry - y, 0.0, y - (ry + rh))
    if dx or dy:
        return math.hypot(dx, dy)
    return -min(x - rx, rx + rw - x, y - ry, ry + rh - y)


def study_units():
    """Page units per unit of the knowledge-map studies.

    Their terrain, drape and fog constants are tuned against a 904-unit map.
    Reading a 2800-unit page in the same units carries that tuning over intact,
    instead of re-deriving every number for a different-sized surface.
    """
    return panel_layout.load()['page'][0] / fogmap.MAP_W


class PageGround:
    """The fogged ground of one page: shaded relief with the veil lying on it.

    This is the studies' own construction, on a page instead of a map: a seeded
    heightfield hillshaded from the upper left, so altitude reads as shading
    rather than contour lines, and a veil computed from the panel rectangles,
    displaced by noise and feathered, multiplied over it. The veil is the only
    boundary; the ground is continuous underneath.

    Seeded from the page number, so a page fogs the same way every time it is
    looked at. The panel rectangles are the only input from the book: no
    proposition, evidence state, or observer viewpoint reaches this computation.

    Two grids come out of the one pass. `base` is what the page is multiplied
    by — relief under fog outside the panels, and the fog alone over them, so
    no invented terrain is laid across artwork. `clear` is how much of the
    ground the fog leaves showing, which is what a pictogram is seen through.
    """

    def __init__(self, page, panel_count):
        self.page = int(page)
        self.unit = study_units()
        self.width, self.height = panel_layout.load()['page']
        self.rects = [[v / self.unit for v in rect] for rect in panel_layout.rectangles(panel_count)]
        self.relief()
        self.fog()

    # --- the coarse grid: landforms, their light, and the reach of the panels

    def padded(self, rows):
        """A grid with one sample of its own edge repeated all the way round.

        The fog reads this grid between its samples, several hundred thousand
        times; carrying the border in the data is what keeps a bounds test out
        of that loop.
        """
        rows = [array('f', [row[0]]) + row + array('f', [row[-1]]) for row in rows]
        return [rows[0]] + rows + [rows[-1]]

    def clearance(self):
        """Study units from every coarse sample to the nearest panel edge.

        Negative inside a panel. The distance to a rectangle separates into an
        x part and a y part, so the columns are computed once and the rows walk
        across them: the per-sample form of this was most of the cost of the
        whole layer.
        """
        columns = []
        for rx, _, rw, _ in self.rects:
            gap, inside = array('f'), array('f')
            for i in range(self.rw):
                x = (i + 0.5) * RELIEF_CELL / self.unit
                gap.append(max(rx - x, 0.0, x - (rx + rw)))
                inside.append(min(x - rx, rx + rw - x))
            columns.append((gap, inside))
        rows = []
        for j in range(self.rh):
            y = (j + 0.5) * RELIEF_CELL / self.unit
            row = array('f', [1e9]) * self.rw
            for (gap, inside), (_, ry, _, rh) in zip(columns, self.rects):
                gap_y = max(ry - y, 0.0, y - (ry + rh))
                inside_y = min(y - ry, ry + rh - y)
                for i in range(self.rw):
                    gap_x = gap[i]
                    d = math.hypot(gap_x, gap_y) if gap_x or gap_y else -min(inside[i], inside_y)
                    if d < row[i]:
                        row[i] = d
            rows.append(row)
        return rows

    def relief(self):
        """The heightfield and its hillshade, on a grid of their own.

        Landforms are broad and the fog is not, so the ground is sampled half as
        often in each direction and read back between samples: a quarter of the
        noise for a surface whose finest octave is still resolved.
        """
        self.rw, self.rh = self.width // RELIEF_CELL, self.height // RELIEF_CELL
        near = self.clearance()
        # Deep inside a panel the ground is hidden, so it is never computed.
        # Panels are most of a page, so that is most of the work.
        buried = FOG_FEATHER + FOG_DRIFT + 2 * RELIEF_CELL / self.unit
        relief = fogmap.Noise(5100 + self.page, cell=150.0)
        detail = fogmap.Noise(5200 + self.page, cell=40.0)
        altitude = []
        for j in range(self.rh):
            y = (j + 0.5) * RELIEF_CELL / self.unit
            row, reach = array('f'), near[j]
            for i in range(self.rw):
                x = (i + 0.5) * RELIEF_CELL / self.unit
                row.append(0.0 if reach[i] < -buried
                           else relief.at(x, y) * RELIEF + detail.at(x, y) * DETAIL)
            altitude.append(row)
        self.altitude = self.padded(altitude)
        lx, ly, lz = fogmap.LIGHT
        norm = math.sqrt(lx * lx + ly * ly + lz * lz)
        lx, ly, lz = lx / norm, ly / norm, lz / norm
        lit = []
        for j in range(self.rh):
            row = array('f')
            for i in range(self.rw):
                gx, gy = self.slope(i, j)
                face = math.sqrt(gx * gx + gy * gy + 1.0)
                shade = ((-gx * lx - gy * ly + lz) / face) / lz
                row.append(max(0.0, min(1.0, 0.42 + 0.46 * shade
                                        + 0.12 * ((altitude[j][i] + 50) / 100 - 0.5))))
            lit.append(row)
        self.lit, self.near = self.padded(lit), self.padded(near)

    def slope(self, i, j):
        """The relief gradient at one coarse sample, in study units."""
        step = 2 * RELIEF_CELL / self.unit
        i, j = max(0, min(self.rw - 1, i)) + 1, max(0, min(self.rh - 1, j)) + 1
        return ((self.altitude[j][i + 1] - self.altitude[j][i - 1]) / step,
                (self.altitude[j + 1][i] - self.altitude[j - 1][i]) / step)

    def between(self, grid, x, y):
        """Read a coarse grid at a page point, between its samples."""
        fx, fy = x / RELIEF_CELL - 0.5, y / RELIEF_CELL - 0.5
        i, j = math.floor(fx), math.floor(fy)
        tx, ty = fx - i, fy - j
        top, low = grid[j + 1], grid[j + 2]
        return ((top[i + 1] * (1 - tx) + top[i + 2] * tx) * (1 - ty)
                + (low[i + 1] * (1 - tx) + low[i + 2] * tx) * ty)

    # --- the fine grid: the veil, and what the page is multiplied by

    def fog(self):
        """The veil over that ground, sampled where the fog needs the detail.

        Two grids come out of this pass, and the pictograms are drawn between
        them. `ground` is the lit relief, and is left at full strength over the
        panels so no invented terrain is laid across artwork. `veil` is the fog
        itself, ink with an alpha, which is what swallows a form rather than
        letting it sit on top of the weather.
        """
        edge = fogmap.Noise(7300 + self.page, cell=44.0)
        patch = fogmap.Noise(9900 + self.page, cell=70.0)
        buried = FOG_FEATHER + FOG_DRIFT
        floor = INK_LEVEL / 255
        span = 1 - floor
        self.gw, self.gh = self.width // FOG_CELL, self.height // FOG_CELL
        self.ground, self.veil = [], []
        open0, open1 = OPEN_EDGE
        for j in range(self.gh):
            py = (j + 0.5) * FOG_CELL
            y = py / self.unit
            ground_row, veil_row = bytearray(), bytearray()
            for i in range(self.gw):
                px = (i + 0.5) * FOG_CELL
                near = self.between(self.near, px, py)
                if near < -buried:
                    ground_row.append(255)
                    veil_row.append(round(CLEARED * 255))
                    continue
                x = px / self.unit
                noise = edge.at(x, y)
                # The patchy-contest treatment: the fog itself carries the
                # unevenness, so ground is revealed in irregular patches rather
                # than behind a boundary of its own.
                open_ground = MARGIN_FLOOR + MARGIN_RANGE * fogmap.smoothstep(
                    open0, open1, patch.at(x, y) + noise * 0.35)
                member = 1 - fogmap.smoothstep(-FOG_FEATHER, FOG_FEATHER, near + noise * FOG_DRIFT)
                veil = max(0.0, min(1.0, min(open_ground, 1 - member * (1 - CLEARED))))
                lit = 1 - (1 - member) * (1 - self.between(self.lit, px, py))
                ground_row.append(round((floor + span * lit) * 255))
                veil_row.append(round(veil * 255))
            self.ground.append(ground_row)
            self.veil.append(veil_row)

    def drape(self, x, y):
        """How far the relief under a page point pulls a mark laid across it.

        The studies displace each sampled pixel of a pictogram by the slope
        beneath it, so the form takes the shape of the ground. A vector page
        does the same to each vertex, which is that displacement evaluated where
        it can be afforded at this size.
        """
        gx, gy = self.slope(int(x / RELIEF_CELL), int(y / RELIEF_CELL))
        dx, dy = DRAPE * gx * self.unit, DRAPE * gy * self.unit
        reach = math.hypot(dx, dy)
        if reach > DRAPE_LIMIT:
            dx, dy = dx * DRAPE_LIMIT / reach, dy * DRAPE_LIMIT / reach
        return dx, dy

    def png(self, rows, ink=False):
        """One byte a pixel; deterministic bytes.

        Grey by default. `ink` reads the same bytes as the fog's own opacity:
        every palette entry is the ink token and the transparency table is the
        identity, which carries an alpha channel at a grey channel's cost.
        """
        raw = bytearray()
        for row in rows:
            raw.append(0)
            raw += row

        def chunk(kind, body):
            return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)
        out = (b'\x89PNG\r\n\x1a\n'
               + chunk(b'IHDR', struct.pack('>IIBBBBB', self.gw, self.gh, 8, 3 if ink else 0, 0, 0, 0)))
        if ink:
            tone = bytes(int(fogmap.INK[i:i + 2], 16) for i in (1, 3, 5))
            out += chunk(b'PLTE', tone * 256) + chunk(b'tRNS', bytes(range(256)))
        return out + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')


def glyph_forms():
    """The pictogram vocabulary of the studies, in a fixed order and ungrouped.

    There, each proposition and observation has a family of its own. A page has
    neither, so a page draws from the whole set without regard to family: no
    part of a page corresponds to P1-P6, to an observation island, or to any
    other thing the map names.
    """
    return sorted(fogmap.GLYPHS)


def ground_glyphs(page, panel_count):
    """`(kind, x, y, scale, angle)` for the forms lying on one page's ground.

    Seeded from the page number, clustered and irregularly spaced the way the
    studies scatter them, with no two near neighbours sharing a form. Every form
    keeps its whole reach clear of every panel rectangle and of the page edge,
    with room for the drape to pull it, so the layer lies in the margins and
    gutters and crosses no artwork, lettering, evidence field or provenance
    slate. Their number and spacing measure nothing.
    """
    w, h = panel_layout.load()['page']
    rects = panel_layout.rectangles(panel_count)
    ground = w * h - sum(rw * rh for _, _, rw, rh in rects)
    forms = glyph_forms()
    rnd = random.Random(4200 + int(page))
    placed, attempts = [], 0
    while len(placed) < max(12, ground // GLYPH_GROUND) and attempts < 8000:
        attempts += 1
        if placed and rnd.random() < 0.35:
            _, px, py, *_ = rnd.choice(placed)
            bearing, step = rnd.uniform(0, 2 * math.pi), rnd.uniform(90, 260)
            x, y = px + step * math.cos(bearing), py + step * math.sin(bearing)
        else:
            x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        scale = rnd.uniform(*GLYPH_SCALE)
        reach = GLYPH_RADIUS * scale + DRAPE_LIMIT + GLYPH_CLEAR
        if not (reach <= x <= w - reach and reach <= y <= h - reach):
            continue
        if any(rect_distance(x, y, rect) < reach for rect in rects):
            continue
        # Separation is the studies' own, in their units: forms sit apart, crowd,
        # and sometimes overlap. Only the panels get the full keep-out.
        spacing = rnd.choice(GLYPH_SPACING)
        if any(math.hypot(x - qx, y - qy) < spacing for _, qx, qy, *_ in placed):
            continue
        near = {kind for kind, qx, qy, *_ in placed if math.hypot(x - qx, y - qy) < 420}
        choices = [kind for kind in forms if kind not in near]
        if not choices:
            continue
        placed.append((rnd.choice(choices), x, y, scale, rnd.uniform(-35, 35)))
    return placed


def glyph_mark(ground, kind, x, y, scale, angle):
    """One pictogram, turned on the spot and draped over the relief beneath it.

    The forms are drawn for a map a third of this page's size, so their arcs
    carry more vertices than a page can resolve; points closer together than
    `GLYPH_DETAIL` are dropped rather than draped and written out.
    """
    cos_a, sin_a = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    parts = []
    for poly in fogmap.GLYPHS[kind]:
        points, last = [], None
        for index, (u, v) in enumerate(poly):
            px = x + scale * (u * cos_a - v * sin_a)
            py = y + scale * (u * sin_a + v * cos_a)
            if last and index < len(poly) - 1 and math.hypot(px - last[0], py - last[1]) < GLYPH_DETAIL:
                continue
            last = (px, py)
            dx, dy = ground.drape(px, py)
            points.append(f'{px - dx:.0f},{py - dy:.0f}')
        parts.append('M' + ' L'.join(points))
    return (f'<path data-glyph="{kind}" stroke-width="{fogmap.GLYPH_STROKE * scale:.2f}" '
            f'd="{" ".join(parts)}"/>')


def page_fog_svg(page, panel_count):
    ground = PageGround(page, panel_count)
    w, h = ground.width, ground.height
    marks = ''.join(glyph_mark(ground, *pose) for pose in ground_glyphs(page, panel_count))

    def layer(rows, ink=False):
        data = base64.b64encode(ground.png(rows, ink)).decode()
        return (f'<image x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="none" '
                f'href="data:image/png;base64,{data}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>Page {int(page):03d} — fog-of-war preview texture</title>'
            '<desc>Authored texture computed from the panel rectangles alone: shaded relief with '
            'pictograms draped over it on the margins and gutters, under a veil that thins in '
            'patches, so a form is obscured and revealed by the fog rather than sitting on it. It '
            'is not a map of the wiki, not a measure of what any observer knows, and it neither '
            'reveals nor resolves anything. The forms stand for no proposition and carry no count; '
            'no artwork is under them.</desc>'
            '<g aria-hidden="true" style="pointer-events:none">'
            + layer(ground.ground)
            + f'<g fill="none" stroke="{fogmap.INK}" stroke-linecap="round" stroke-linejoin="round">'
            + marks + '</g>' + layer(ground.veil, ink=True) + '</g></svg>')


FOG_CACHE = {}


def page_layer_svg(layer, page, panel_count):
    if layer == 'fog':
        # The ground is a raster, and a page is looked at from several displays
        # at once. It is deterministic, so it is drawn once and kept.
        key = (int(page), panel_count)
        if key not in FOG_CACHE:
            if len(FOG_CACHE) >= FOG_CACHED_PAGES:
                del FOG_CACHE[next(iter(FOG_CACHE))]
            FOG_CACHE[key] = page_fog_svg(page, panel_count)
        return FOG_CACHE[key]
    if layer == 'ants':
        return page_ants_svg(page, panel_count)
    raise ValueError(f'No page overlay named {layer}')
