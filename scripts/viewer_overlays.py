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
  * **Fog of war** is drawn the way `knowledge_maps_fog` draws it: pictograms
    lying on the ground, and a veil computed per page from the panel rectangles
    that thins in patches, so a form reads anywhere from plain to invisible. The
    forms come from that module's vocabulary but carry none of its meaning: a
    page has no propositions and no observation islands, so they are drawn from
    the whole set ungrouped, and every one of them keeps clear of every panel.
    It is authored preview texture. It is not a map of the wiki, not a measure
    of what any observer knows, and it neither reveals nor resolves anything.

A layer can only be withheld where the geometry is still separable. A panel
whose current art is exactly its scene's render can give up its ants, because
the render can be repeated without those nodes; a raster chosen from a model
cannot, and says so on its face rather than pretending the layer is gone.
"""
from __future__ import annotations

import base64
import html
import math
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
    'fog': ('Fog of war', 'Authored preview texture: pictograms on the margins and gutters under a veil that thins in patches. Not a map of the wiki and not a measure of what is known.'),
}
DEFAULTS = {name: True for name in LAYERS}
PAGE_LAYERS = ('fog', 'ants')
# Hills are surfaces and the Apache Ant logo is scene content; neither is an ant figure.
ANT_ASSETS = ('ant',)

FOG_CELL = 16      # page units per veil sample
FOG_FEATHER = 48   # page units of soft edge either side of a panel boundary
FOG_DRIFT = 80     # page units the noise displaces that edge by
CLEARED = 0.16     # veil left over a panel, so the layer stays legible over art
MARGIN = 0.86      # deep veil over margins and gutters, before noise
CLEARING = 0.55    # how far a thin patch lifts that veil, so the ground shows through
INK_LEVEL = 16     # the luminance of the ink token: what the veil is made of
# Pictograms on the fogged ground. The forms are the study vocabulary; the page
# geometry is this module's, and the fog is the only thing that hides them.
# Measured from the forms themselves rather than assumed: a turned form can put
# its furthest point in any direction, so that reach is what a placement clears.
GLYPH_RADIUS = max(math.hypot(x, y) for polys in fogmap.GLYPHS.values()
                   for poly in polys for x, y in poly)
GLYPH_SCALE = (1.7, 2.9)
GLYPH_CLEAR = 14      # page units a form keeps away from every panel and the page edge
GLYPH_GROUND = 52000  # square page units of fogged ground per form
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


def veil_rows(page, panel_count):
    """The veil sampled on a coarse grid: deep in the margins, thin over panels.

    Seeded from the page number, so a page fogs the same way every time it is
    looked at. The panel rectangles are the only input: no proposition, evidence
    state, or observer viewpoint reaches this computation.

    Each row holds what the page still shows through the veil. The margin does
    not fog evenly: a patch field lifts it by up to `CLEARING`, which is what
    lets a pictogram beneath read at all, and the lifted margin still stays
    deeper than `CLEARED`, so a panel always reads more clearly than the ground
    around it.
    """
    w, h = panel_layout.load()['page']
    rects = panel_layout.rectangles(panel_count)
    edge = fogmap.Noise(7300 + int(page), cell=300.0)
    drift = fogmap.Noise(9900 + int(page), cell=700.0)
    patch = fogmap.Noise(8600 + int(page), cell=520.0)
    gw, gh = w // FOG_CELL, h // FOG_CELL
    rows = []
    for j in range(gh):
        y = (j + 0.5) * FOG_CELL
        row = bytearray()
        for i in range(gw):
            x = (i + 0.5) * FOG_CELL
            base = (MARGIN + 0.10 * drift.at(x, y)
                    - CLEARING * fogmap.smoothstep(0.0, 0.45, patch.at(x, y)))
            displaced = edge.at(x, y) * FOG_DRIFT
            veil = base
            for rect in rects:
                member = 1 - fogmap.smoothstep(-FOG_FEATHER, FOG_FEATHER,
                                               rect_distance(x, y, rect) + displaced)
                veil = min(veil, base - member * (base - CLEARED))
            veil = max(0.0, min(1.0, veil))
            row.append(int(round(255 - veil * (255 - INK_LEVEL))))
        rows.append(row)
    return gw, gh, rows


def fog_png(width, height, rows):
    """The veil as ink with an alpha channel; deterministic bytes.

    `rows` carry what the page shows through, so the alpha is the part the fog
    withholds. Ink with an alpha, rather than a flat grey, is what lets the
    pictograms underneath be swallowed by their own fog instead of sitting on it.
    """
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for shown in row:
            raw += bytes((INK_LEVEL, round((255 - shown) * 255 / (255 - INK_LEVEL))))

    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 4, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))


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
    so the layer lies in the margins and gutters and crosses no artwork,
    lettering, evidence field or provenance slate. Their number and spacing
    measure nothing.
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
        reach = GLYPH_RADIUS * scale + GLYPH_CLEAR
        if not (reach <= x <= w - reach and reach <= y <= h - reach):
            continue
        if any(rect_distance(x, y, rect) < reach for rect in rects):
            continue
        spacing = reach + rnd.choice((10, 40, 90, 170))
        if any(math.hypot(x - qx, y - qy) < spacing for _, qx, qy, *_ in placed):
            continue
        near = {kind for kind, qx, qy, *_ in placed if math.hypot(x - qx, y - qy) < 420}
        choices = [kind for kind in forms if kind not in near]
        if not choices:
            continue
        placed.append((rnd.choice(choices), x, y, scale, rnd.uniform(-35, 35)))
    return placed


def glyph_mark(kind, x, y, scale, angle):
    """One pictogram in the ink token, turned on the spot."""
    return (f'<g transform="rotate({angle:.1f} {x:.1f} {y:.1f})">'
            + fogmap.glyph_svg(kind, x, y, scale, fogmap.INK, GLYPH_STROKE) + '</g>')


def page_fog_svg(page, panel_count):
    w, h = panel_layout.load()['page']
    gw, gh, rows = veil_rows(page, panel_count)
    data = base64.b64encode(fog_png(gw, gh, rows)).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>Page {int(page):03d} — fog-of-war preview texture</title>'
            '<desc>Authored texture computed from the panel rectangles alone: pictograms lying '
            'on the margins and gutters, and a veil over them that thins in patches, so a form '
            'reads anywhere from plain to invisible. It is not a map of the wiki, not a measure '
            'of what any observer knows, and it neither reveals nor resolves anything. The forms '
            'stand for no proposition and carry no count; nothing in the book is under them.</desc>'
            '<g aria-hidden="true" style="pointer-events:none">'
            + '<g data-layer="ground">'
            + ''.join(glyph_mark(*pose) for pose in ground_glyphs(page, panel_count)) + '</g>'
            + f'<image x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="none" '
              f'href="data:image/png;base64,{data}"/></g></svg>')


def page_layer_svg(layer, page, panel_count):
    if layer == 'fog':
        return page_fog_svg(page, panel_count)
    if layer == 'ants':
        return page_ants_svg(page, panel_count)
    raise ValueError(f'No page overlay named {layer}')
