#!/usr/bin/env python3
"""Fog-of-war knowledge-map studies: shaded relief, draped pictograms, computed fog.

The v1 families draw evidence as filled polygons with hard vector edges. Game
fog of war does not look like that: the cleared area has a boundary that is
neither sharp nor regular, terrain that was once seen stays faintly visible
under the fog, and whatever lies on the ground is obscured and revealed by the
fog rather than sitting on top of it. This set keeps the v1 fixtures,
viewpoints, captions and the A-family region layout, and renders the whole map
as one composited raster:

  * a heightfield (seeded value noise, ridges along the region boundaries,
    mesas for the observation strips) hillshaded from the upper left, so
    altitude reads as shading rather than contour lines;
  * many pictograms scattered irregularly over each region, drawn into that
    raster and draped over the relief: their strokes shift with the slope and
    take the hillshade, like a flag laid on the ground;
  * a fog veil computed per sample from signed distances to the regions,
    displaced by seeded noise and feathered, multiplied over everything.

Only the chrome (header, key, caption, legend) is vector text; nothing inside
the map is lettered. Three treatments differ only in how the veil is computed:

  w3  Patchy contest  — contested ground is visible in patches instead of hatched.
  w2  Line of sight   — vision discs around the places evidence comes from.
  w1  Ragged regions  — each region's fog edge is noise-displaced and feathered.

Fog levels: unexplored (opaque), re-fogged (relief dimly visible: it was seen
and lost support), contested (partly veiled), visible (clear). P6 is always
unexplored. Everything is deterministic, standard-library Python; `check`
regenerates in memory and compares bytes.

    python3 scripts/knowledge_maps_fog.py generate
    python3 scripts/knowledge_maps_fog.py check
"""

import argparse
import base64
import json
import math
import random
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from html import escape
from pathlib import Path

import knowledge_maps as km
from knowledge_maps import (DIRTY, INK, NS, PAPER, STEEL, FIXTURES, VIEWPOINTS, PROPOSITIONS,
                            digest, encoded, line, load_data, rect, states_for, text)

ROOT = km.ROOT
OUTPUT = ROOT / "assets/knowledge-maps/fog-v1"
RENDERER_VERSION = "knowledge-map-fog-2.1.0"
TREATMENTS = {
    "w3": ("Patchy contest", "Contested ground is visible in irregular patches rather than hatched; the fog itself carries the uncertainty."),
    "w2": ("Line of sight", "Vision discs around the places evidence comes from; the relief is only visible where sight reaches."),
    "w1": ("Ragged regions", "Regional fog with a noise-displaced, feathered edge; contested ground is striped fog inside the same soft edge."),
}
MAP_X, MAP_Y, MAP_W, MAP_H = 28, 108, 904, 432
FOG_SCALE = 2                                       # fog cells are 2 map px; the veil is soft anyway
GW, GH = MAP_W // FOG_SCALE, MAP_H // FOG_SCALE     # 452 x 216 fog cells
SAMPLE_RES, SHEET_RES = 1.0, 0.5                    # image px per map px for samples and contact sheets
VEIL = {"lit": 0.0, "hatched": 0.34, "refog": 0.68, "dark": 1.0}
INK_RGB, PAPER_RGB = (16, 18, 20), (231, 224, 208)
LEVELS = 128                                        # palette steps from ink to paper
LIGHT = (-0.50, -0.62, 0.60)
DRAPE = 9.0                                         # px of glyph shift per unit slope
PREVIOUS = {"039-after": "039-before"}

# The A-family region layout, so the fog studies stay comparable with v1 A.
REGIONS = {
    "P1": [(48, 136), (120, 108), (272, 126), (294, 189), (250, 275), (137, 265), (60, 218)],
    "P2": [(272, 126), (416, 109), (515, 153), (490, 266), (370, 284), (294, 189)],
    "P3": [(60, 218), (137, 265), (250, 275), (284, 380), (209, 445), (86, 427), (40, 338)],
    "P4": [(250, 275), (370, 284), (490, 266), (501, 372), (451, 451), (330, 435), (284, 380)],
    "P5": [(515, 153), (636, 112), (714, 150), (706, 293), (668, 425), (565, 439), (501, 372), (490, 266)],
}
SIGHT_AT = {"P1": (170, 189), "P2": (397, 191), "P3": (158, 340), "P4": (386, 357), "P5": (604, 284)}
P6_SHAPE = [(769, 112), (936, 105), (921, 448), (771, 459)]
OBSERVATIONS = ("response", "correction", "configuration", "weights")
OBSERVATION_NAMES = {"response": "ALERT / BOARD / PIVOT", "correction": "SCORER ACCOUNTS",
                     "configuration": "CONFIGURATION ACCOUNT", "weights": "WEIGHTS ACCOUNT"}


def foothold_polygon():
    pts = REGIONS["P1"]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    return [(x0, y0), (x1, y0), (x1, y0 + (y1 - y0) * 0.27), (x0 + (x1 - x0) * 0.52, y0 + (y1 - y0) * 0.20), (x0, y0 + (y1 - y0) * 0.33)]


def observation_polygon(index):
    x = 40 + index * 224
    return [(x, 489), (x + 192, 484), (x + 210, 500), (x + 201, 528), (x + 11, 530)]


def zones():
    """Every fogged zone: polygon, line-of-sight centre, and sight radius."""
    out = {}
    for key, pts in REGIONS.items():
        out[key] = (pts, SIGHT_AT[key], 132)
    fh = foothold_polygon()
    out["P1-foothold"] = (fh, (sum(p[0] for p in fh) / len(fh), sum(p[1] for p in fh) / len(fh)), 62)
    for i, key in enumerate(OBSERVATIONS):
        out[f"observation-{key}"] = (observation_polygon(i), (40 + i * 224 + 105, 507), 60)
    return out


# --- geometry ---------------------------------------------------------------

def inside(pts, x, y):
    result = False
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                result = not result
    return result


def segment_distance(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def signed_distance_field(pts):
    """Signed distance (map px, negative inside) from every fog cell centre to the polygon edge."""
    n = len(pts)
    edges = [(pts[i], pts[(i + 1) % n]) for i in range(n)]
    field = []
    for j in range(GH):
        y = MAP_Y + (j + 0.5) * FOG_SCALE
        row = []
        for i in range(GW):
            x = MAP_X + (i + 0.5) * FOG_SCALE
            d = min(segment_distance(x, y, x1, y1, x2, y2) for (x1, y1), (x2, y2) in edges)
            row.append(-d if inside(pts, x, y) else d)
        field.append(row)
    return field


def sample_field(field, x, y):
    """Bilinear sample of a fog-cell grid at map coordinates."""
    fx = (x - MAP_X) / FOG_SCALE - 0.5
    fy = (y - MAP_Y) / FOG_SCALE - 0.5
    i0 = max(0, min(GW - 2, int(math.floor(fx))))
    j0 = max(0, min(GH - 2, int(math.floor(fy))))
    tx = max(0.0, min(1.0, fx - i0))
    ty = max(0.0, min(1.0, fy - j0))
    r0, r1 = field[j0], field[j0 + 1]
    return (r0[i0] * (1 - tx) + r0[i0 + 1] * tx) * (1 - ty) + (r1[i0] * (1 - tx) + r1[i0 + 1] * tx) * ty


class Noise:
    """Seeded value noise with three octaves, in [-1, 1]."""

    def __init__(self, seed, cell=44.0):
        rnd = random.Random(seed)
        self.cell = cell
        self.lattices = [[[rnd.random() for _ in range(96)] for _ in range(96)] for _ in range(3)]

    def at(self, x, y):
        total, weight, amplitude = 0.0, 0.0, 1.0
        for octave, lattice in enumerate(self.lattices):
            cell = self.cell / (2 ** octave)
            fx, fy = x / cell, y / cell
            ix, iy = int(math.floor(fx)), int(math.floor(fy))
            tx, ty = fx - ix, fy - iy
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            a, b = lattice[iy % 96][ix % 96], lattice[iy % 96][(ix + 1) % 96]
            c, d = lattice[(iy + 1) % 96][ix % 96], lattice[(iy + 1) % 96][(ix + 1) % 96]
            value = (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty
            total += (value * 2 - 1) * amplitude
            weight += amplitude
            amplitude /= 2
        return total / weight


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def png_palette(width, height, index_rows):
    """8-bit palette PNG along the ink-to-paper ramp; deterministic bytes."""
    palette = bytearray()
    for i in range(LEVELS):
        t = i / (LEVELS - 1)
        palette += bytes(int(round(INK_RGB[c] + (PAPER_RGB[c] - INK_RGB[c]) * t)) for c in range(3))
    raw = bytearray()
    for row in index_rows:
        raw.append(0)
        raw += row

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
            + chunk(b"PLTE", bytes(palette)) + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# --- pictograms ---------------------------------------------------------------
# Each glyph is a set of polylines in a 40 x 40 box centred on the origin. They
# are rasterised into the ground, draped over the relief, and then fogged.

def arc(cx, cy, r, a0, a1, steps=20):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / steps)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / steps))) for k in range(steps + 1)]


def circle(cx, cy, r):
    return arc(cx, cy, r, 0, 360, 24)


def rectp(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]


def arrow(x1, y1, x2, y2, head=5):
    a = math.atan2(y2 - y1, x2 - x1)
    return [[(x1, y1), (x2, y2)],
            [(x2 - head * math.cos(a - 0.5), y2 - head * math.sin(a - 0.5)), (x2, y2), (x2 - head * math.cos(a + 0.5), y2 - head * math.sin(a + 0.5))]]


def spiral(turns=2.2, r0=2, r1=15, steps=40):
    return [(r * math.cos(t), r * math.sin(t)) for k in range(steps + 1)
            for t in [k / steps * turns * 2 * math.pi] for r in [r0 + (r1 - r0) * k / steps]]


def wave(x0, x1, y, amp, periods, steps=32):
    return [(x0 + (x1 - x0) * k / steps, y + amp * math.sin(k / steps * periods * 2 * math.pi)) for k in range(steps + 1)]


def star(n, r_out, r_in):
    pts = []
    for k in range(2 * n + 1):
        r = r_out if k % 2 == 0 else r_in
        a = -math.pi / 2 + k * math.pi / n
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


# Symbol families: each region carries many forms of its own idea, never one repeated stamp.
GLYPHS = {
    # --- P1 coordination: things that link, meet, relay, agree ---
    "P1/stations": [circle(-12, 8, 5), circle(12, 8, 5), circle(0, -12, 5), [(-8, 5), (-3, -8)], [(8, 5), (3, -8)], [(-7, 8), (7, 8)]],
    "P1/meet": arrow(-17, 0, -4, 0) + arrow(17, 0, 4, 0) + [[(0, -8), (0, 8)]],
    "P1/relay": [circle(-13, 0, 3), circle(0, 0, 3), circle(13, 0, 3)] + arrow(-9, -6, -4, -6, 3) + arrow(4, 6, 9, 6, 3),
    "P1/chain": [arc(-6, 0, 8, 40, 320), arc(6, 0, 8, 220, 500)],
    "P1/mesh": [rectp(-12, -12, 24, 24), [(-12, -12), (12, 12)], [(12, -12), (-12, 12)], circle(-12, -12, 2.5), circle(12, -12, 2.5), circle(12, 12, 2.5), circle(-12, 12, 2.5)],
    "P1/board": [rectp(-10, -10, 20, 20), [(-6, -4), (6, -4)], [(-6, 1), (2, 1)]] + arrow(-19, 0, -11, 0, 3) + arrow(19, 0, 11, 0, 3),
    "P1/converge": arrow(-15, -12, -3, -2) + arrow(15, -12, 3, -2) + arrow(0, 16, 0, 4) + [circle(0, 0, 2.5)],
    "P1/knot": [arc(-6, 0, 7, 0, 360, 24), arc(6, 0, 7, 0, 360, 24), arc(0, -8, 7, 0, 360, 24)],
    "P1/handoff": [[(-16, 6), (-8, 6), (-8, -6), (0, -6)], [(0, 6), (8, 6), (8, -6), (16, -6)], circle(-16, 6, 2), circle(16, -6, 2)],
    "P1/agreement": [[(-14, 4), (-6, 10), (6, -8)], [(-14, -10), (14, -10)], [(-14, 14), (14, 14)]],
    # --- P2 recurrence: things that return, repeat, echo ---
    "P2/loop": [arc(0, 0, 13, -70, 230), [(4, -16), (8, -10), (1, -8), (4, -16)], arc(0, 2, 5, -70, 230)],
    "P2/spiral": [spiral()],
    "P2/twin-cycles": [arc(-7, 0, 7, 20, 330), arc(7, 0, 7, 200, 510)] + arrow(-1, -6, 1, -6, 3),
    "P2/wave": [wave(-17, 17, 0, 6, 2)],
    "P2/echo": [arc(-8, 0, 6, -60, 60), arc(-8, 0, 12, -60, 60), arc(-8, 0, 18, -60, 60)],
    "P2/again": [rectp(-12, -9, 24, 18), arc(0, 0, 6, -150, 150)] + [[(4, -6), (7, -1), (1, -1), (4, -6)]],
    "P2/tracks": [circle(-12, 6, 2), circle(-6, -4, 2), circle(0, 6, 2), circle(6, -4, 2), circle(12, 6, 2)],
    "P2/hourglass": [[(-9, -13), (9, -13), (-9, 13), (9, 13), (-9, -13)], [(-4, 0), (4, 0)]],
    "P2/orbit": [arc(0, 0, 14, 0, 360, 28), circle(0, 0, 3), circle(14, 0, 2.5)],
    "P2/ripple": [circle(0, 0, 4), arc(0, 0, 9, 20, 160), arc(0, 0, 9, 200, 340), arc(0, 0, 14, 20, 160), arc(0, 0, 14, 200, 340)],
    # --- P3 record equals event: things that capture, seal, mirror, reproduce ---
    "P3/ledger": [rectp(-17, -13, 18, 24), [(-13, -7), (-3, -7)], [(-13, -2), (-3, -2)], [(-13, 3), (-7, 3)], [(4, -2), (10, -2)], [(4, 3), (10, 3)], [(14, -9), (18, -1), (14, 7), (10, -1), (14, -9)]],
    "P3/scroll": [[(-14, -10), (14, -10)], [(-14, 10), (14, 10)], arc(-14, -7, 3, 90, 270), arc(14, 7, 3, -90, 90), [(-9, -4), (9, -4)], [(-9, 1), (5, 1)]],
    "P3/lens": [rectp(-15, -10, 30, 20), circle(0, 0, 6), circle(0, 0, 2.5), [(-12, -14), (-4, -14)]],
    "P3/reel": [circle(-9, 0, 6), circle(9, 0, 6), circle(-9, 0, 2), circle(9, 0, 2), [(-9, 6), (9, 6)], [(-9, -6), (9, -6)]],
    "P3/seal": [circle(0, 0, 13), star(5, 8, 3.5)],
    "P3/stamp": [rectp(-12, -12, 24, 24), [(-8, -8), (8, 8)], [(8, -8), (-8, 8)]],
    "P3/frames": [rectp(-15, -12, 20, 16), rectp(-5, -4, 20, 16)],
    "P3/mirror": [[(0, -15), (0, 15)], [(-14, -8), (-3, 0), (-14, 8), (-14, -8)], [(14, -8), (3, 0), (14, 8), (14, -8)]],
    "P3/tape": [rectp(-16, -6, 32, 12), circle(-8, 0, 3), circle(8, 0, 3), [(-8, 3), (8, 3)]],
    "P3/witness": [circle(0, -8, 4), [(0, -4), (0, 6)], [(-6, 12), (0, 6), (6, 12)], arc(0, 0, 16, 200, 340)],
    # --- P4 reporting: things that signal, call, or fail to reach anyone ---
    "P4/short": [circle(10, -9, 4), [(10, -5), (10, 6)], [(4, 0), (16, 0)], [(10, 6), (5, 14)], [(10, 6), (15, 14)], [(-17, 0), (-6, 0)], [(-8, -4), (-4, 0), (-8, 4)], [(-1, -8), (-1, 8)]],
    "P4/silenced-bell": [arc(0, 4, 10, 180, 360) + [(13, 8), (-13, 8), (-10, 4)], [(-14, 14), (14, -14)]],
    "P4/megaphone": [[(-14, -4), (-14, 4), (-4, 6), (12, 14), (12, -14), (-4, -6), (-14, -4)], [(-14, 4), (-10, 12)]],
    "P4/envelope": [rectp(-15, -10, 30, 20), [(-15, -10), (0, 2), (15, -10)]],
    "P4/hail": [circle(0, -9, 4), [(0, -5), (0, 6)], [(-7, 0), (0, 0)], [(0, 0), (9, -8)], [(0, 6), (-6, 14)], [(0, 6), (6, 14)]],
    "P4/tower": [[(-8, 14), (0, -14), (8, 14)], [(-5, 4), (5, 4)], [(-3, -4), (3, -4)], arc(0, -14, 7, 200, 340), arc(0, -14, 12, 200, 340)],
    "P4/bubble": [[(-14, -10), (14, -10), (14, 5), (-2, 5), (-8, 12), (-7, 5), (-14, 5), (-14, -10)]],
    "P4/flag": [[(-8, 15), (-8, -15)], [(-8, -15), (12, -10), (-8, -4)]],
    "P4/unanswered": [arc(-4, -2, 9, 180, 360) + [(5, -2), (5, 4), (-2, 4)], circle(-2, 11, 1.5)],
    "P4/wire-cut": [[(-17, 0), (-4, 0)], [(4, 0), (17, 0)], [(-3, -5), (-3, 5)], [(3, -5), (3, 5)]],
    # --- P5 measurement: instruments, and the question of what they touch ---
    "P5/rule": [rectp(-17, -6, 34, 12), [(-11, -6), (-11, 0)], [(-5, -6), (-5, -3)], [(1, -6), (1, 0)], [(7, -6), (7, -3)], [(13, -6), (13, 0)], [(-17, 12), (17, 12)], [(-17, 9), (-17, 15)], [(17, 9), (17, 15)]],
    "P5/calipers": [[(-12, -14), (-12, 12)], [(12, -14), (12, 12)], [(-12, -14), (12, -14)], [(-12, 12), (-6, 12)], [(12, 12), (6, 12)]],
    "P5/gauge": [arc(0, 6, 14, 180, 360), [(0, 6), (7, -6)], circle(0, 6, 2), [(-14, 6), (14, 6)]],
    "P5/protractor": [arc(0, 6, 15, 180, 360) + [(15, 6), (-15, 6)]] + [[(15 * math.cos(math.radians(a)) * 0.8, 6 + 15 * math.sin(math.radians(a)) * 0.8), (15 * math.cos(math.radians(a)), 6 + 15 * math.sin(math.radians(a)))] for a in (200, 230, 260, 290, 320)],
    "P5/crosshair": [circle(0, 0, 10), [(0, -16), (0, -5)], [(0, 5), (0, 16)], [(-16, 0), (-5, 0)], [(5, 0), (16, 0)]],
    "P5/thermometer": [[(-4, -15), (4, -15), (4, 6), (-4, 6), (-4, -15)], circle(0, 10, 6), [(0, -4), (0, 6)]],
    "P5/tally": [[(-12, -10), (-12, 10)], [(-6, -10), (-6, 10)], [(0, -10), (0, 10)], [(6, -10), (6, 10)], [(-15, 8), (10, -8)]],
    "P5/compass": [star(4, 15, 4), circle(0, 0, 2.5)],
    "P5/plumb": [[(0, -16), (0, 2)], [(-5, 2), (5, 2), (0, 12), (-5, 2)], [(-10, -16), (10, -16)]],
    "P5/probe": [[(-15, 12), (6, -9)], [(6, -9), (14, -14)], [(2, -12), (10, -4)], circle(-15, 12, 2)],
    # --- P6 unreachable: what cannot be entered or seen ---
    "P6/gate": [[(-13, 14), (-13, -6)] + arc(0, -6, 13, 180, 360) + [(13, 14), (-13, 14)], [(-5, 2), (5, 2)], [(0, -3), (0, 7)]],
    "P6/locked": [rectp(-11, -14, 22, 28), circle(3, 0, 3), [(3, 3), (3, 8)]],
    "P6/wall": [rectp(-16, -12, 32, 24), [(-16, -4), (16, -4)], [(-16, 4), (16, 4)], [(-8, -12), (-8, -4)], [(8, -12), (8, -4)], [(0, -4), (0, 4)], [(-8, 4), (-8, 12)], [(8, 4), (8, 12)]],
    "P6/closed-eye": [arc(0, -6, 15, 20, 160), [(-9, 5), (-11, 10)], [(0, 6), (0, 12)], [(9, 5), (11, 10)]],
    "P6/void": [circle(0, 0, 13), [(-9, -9), (9, 9)], [(9, -9), (-9, 9)]],
    "P6/cloud": [arc(-8, 4, 6, 90, 270) + arc(-3, -4, 7, 180, 330) + arc(7, -1, 6, 210, 400) + arc(9, 7, 4, 300, 450) + [(-8, 10)]],
    "P6/hidden-peak": [[(-16, 14), (-4, -6), (2, 2), (8, -10), (16, 14)], [(-18, -6), (18, -6)]],
    # --- observations ---
    "response/bell": [arc(0, 6, 10, 180, 360) + [(13, 10), (-13, 10), (-10, 6)], arc(0, 13, 3, 0, 180), [(0, -4), (0, -9)]],
    "response/siren": [arc(0, 6, 10, 180, 360) + [(10, 6), (-10, 6)], [(-14, 10), (14, 10)], [(0, -8), (0, -14)], [(-9, -5), (-13, -9)], [(9, -5), (13, -9)]],
    "response/board": [rectp(-14, -10, 28, 20), [(-10, -5), (4, -5)], [(-10, 0), (8, 0)], [(-10, 5), (0, 5)]],
    "response/pivot": arrow(-14, 10, -14, -6) + arrow(-14, -6, 12, -6) + [[(-14, 10), (12, 10)]],
    "correction/balance": [[(0, -12), (0, 12)], [(-14, 12), (14, 12)], [(-14, -6), (14, -6)], [(-14, -6), (-19, 4), (-9, 4), (-14, -6)], [(14, -6), (9, 4), (19, 4), (14, -6)]],
    "correction/checked": [rectp(-12, -12, 24, 24), [(-7, 0), (-2, 6), (8, -7)]],
    "correction/pencil": [[(-14, 10), (8, -12)], [(-10, 14), (12, -8)], [(-14, 10), (-16, 16), (-10, 14)], [(8, -12), (12, -8)]],
    "correction/struck": [[(-15, 0), (15, 0)], wave(-14, 14, 5, 2.5, 3)],
    "configuration/gear": [circle(0, 0, 8), circle(0, 0, 3)] + [[(0, -14), (0, -9)], [(0, 9), (0, 14)], [(-14, 0), (-9, 0)], [(9, 0), (14, 0)], [(-10, -10), (-6, -6)], [(6, 6), (10, 10)], [(10, -10), (6, -6)], [(-6, 6), (-10, 10)]],
    "configuration/slider": [[(-15, -6), (15, -6)], circle(5, -6, 3.5), [(-15, 6), (15, 6)], circle(-6, 6, 3.5)],
    "configuration/toggle": [arc(-7, 0, 7, 90, 270) + [(7, -7)] + arc(7, 0, 7, -90, 90) + [(-7, 7)], circle(7, 0, 4)],
    "configuration/wrench": [[(-12, 12), (2, -2)], arc(6, -6, 7, 200, 500), [(2, -2), (6, -6)]],
    "weights/block": [[(-11, 13), (-7, -4), (7, -4), (11, 13), (-11, 13)], [(-4, -4), (-4, -9), (4, -9), (4, -4)], [(-3, 4), (3, 4)]],
    "weights/dumbbell": [[(-8, 0), (8, 0)], rectp(-14, -7, 6, 14), rectp(8, -7, 6, 14)],
    "weights/pan": [[(0, -14), (0, -6)], [(-12, -6), (12, -6)], [(-12, -6), (-14, 6)], [(12, -6), (14, 6)], arc(0, 0, 14, 25, 155)],
    "weights/anvil": [[(-16, -6), (16, -6), (12, 0), (4, 2), (4, 10), (10, 12), (-10, 12), (-4, 10), (-4, 2), (-12, 0), (-16, -6)]],
}
FAMILIES = {}
for _kind in GLYPHS:
    FAMILIES.setdefault(_kind.split("/")[0], []).append(_kind)
GLYPH_SEGMENTS = {kind: [(a, b) for poly in polys for a, b in zip(poly, poly[1:])] for kind, polys in GLYPHS.items()}
GLYPH_STROKE = 2.3


def glyph_svg(kind, x, y, scale=1.0, stroke=INK, width=2.2):
    """Vector form of a glyph, for the key outside the map and the P6 survey mark."""
    kind = FAMILIES[kind][0] if kind in FAMILIES else kind
    d = " ".join("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in poly) for poly in GLYPHS[kind])
    return (f'<g data-glyph="{kind}" transform="translate({x:.1f} {y:.1f}) scale({scale:.2f})" fill="none" '
            f'stroke="{stroke}" stroke-width="{width:.2f}" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></g>')


def polygon_area(pts):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def scatter(fields, seed=4242):
    """Irregular, clustered glyph placement: (kind, cx, cy, scale, angle).

    Spacing is drawn per glyph, so some sit apart and some crowd or overlap;
    a third of them are dropped next to an earlier one to make clusters. Each
    glyph takes a form from its family that none of its near neighbours use.
    """
    rnd = random.Random(seed)
    instances = []
    areas = [(key, pts, key, 13, (0.5, 0.9), 1500) for key, pts in REGIONS.items()]
    areas.append(("P6", P6_SHAPE, "P6", 12, (0.5, 0.85), 1700))
    for i, key in enumerate(OBSERVATIONS):
        areas.append((f"observation-{key}", observation_polygon(i), key, 6, (0.42, 0.62), 1300))
    for zone, pts, family, margin, scales, density in areas:
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        target = max(4, int(polygon_area(pts) / density))
        placed = []
        attempts = 0
        while len(placed) < target and attempts < 4000:
            attempts += 1
            if placed and rnd.random() < 0.35:
                px, py = rnd.choice(placed)[:2]
                a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(10, 34)
                x, y = px + r * math.cos(a), py + r * math.sin(a)
            else:
                x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if not inside(pts, x, y) or -sample_field(fields[zone], x, y) < margin:
                continue
            spacing = rnd.choice((8, 12, 18, 26, 34, 44))
            if any(math.hypot(x - qx, y - qy) < spacing for qx, qy, _ in placed):
                continue
            near = {kind for qx, qy, kind in placed if math.hypot(x - qx, y - qy) < 60}
            choices = [kind for kind in FAMILIES[family] if kind not in near]
            if not choices:
                continue
            kind = rnd.choice(choices)
            placed.append((x, y, kind))
            instances.append((kind, x, y, rnd.uniform(*scales), rnd.uniform(-35, 35)))
    return instances


# --- relief and ground --------------------------------------------------------

_FIELDS = {}
_GROUND = {}


def distance_fields():
    if not _FIELDS:
        zone_table = zones()
        _FIELDS.update({key: signed_distance_field(pts) for key, (pts, _, _) in zone_table.items()})
        _FIELDS["P6"] = signed_distance_field(P6_SHAPE)
    return _FIELDS


class Ground:
    """Hillshaded relief with draped glyphs at one resolution; shared by every sample."""

    def __init__(self, res):
        self.res = res
        self.w, self.h = int(round(MAP_W * res)), int(round(MAP_H * res))
        fields = distance_fields()
        relief = Noise(5101, cell=150.0)
        detail = Noise(5102, cell=40.0)
        ridge_keys = list(REGIONS) + ["P6"]
        mesa_keys = [f"observation-{key}" for key in OBSERVATIONS]
        height = []
        for j in range(self.h):
            y = MAP_Y + (j + 0.5) / res
            row = []
            for i in range(self.w):
                x = MAP_X + (i + 0.5) / res
                value = relief.at(x, y) * 42 + detail.at(x, y) * 9
                dmin = min(abs(sample_field(fields[key], x, y)) for key in ridge_keys)
                dmin = min(dmin, abs(x - 747))
                value += 16 * math.exp(-(dmin / 11.0) ** 2)
                mesa = min(sample_field(fields[key], x, y) for key in mesa_keys)
                value += 10 * (1 - smoothstep(-6, 6, mesa))
                row.append(value)
            height.append(row)
        self.height = height
        lx, ly, lz = LIGHT
        norm = math.sqrt(lx * lx + ly * ly + lz * lz)
        lx, ly, lz = lx / norm, ly / norm, lz / norm
        self.shade, self.gradient = [], []
        step = 2.0 / res
        for j in range(self.h):
            shade_row, grad_row = [], []
            up, down = height[max(0, j - 1)], height[min(self.h - 1, j + 1)]
            row = height[j]
            for i in range(self.w):
                gx = (row[min(self.w - 1, i + 1)] - row[max(0, i - 1)]) / step
                gy = (down[i] - up[i]) / step
                n = math.sqrt(gx * gx + gy * gy + 1.0)
                shade_row.append(((-gx * lx - gy * ly + lz) / n) / lz)
                grad_row.append((gx, gy))
            self.shade.append(shade_row)
            self.gradient.append(grad_row)
        self.instances = scatter(fields)
        self.ink = [[0.0] * self.w for _ in range(self.h)]
        for kind, cx, cy, scale, angle in self.instances:
            self.drape(kind, cx, cy, scale, angle)
        self.value = []
        for j in range(self.h):
            row = []
            for i in range(self.w):
                shade = self.shade[j][i]
                altitude = (height[j][i] + 50) / 100
                ground_value = max(0.0, min(1.0, 0.42 + 0.46 * shade + 0.12 * (altitude - 0.5)))
                ink = 0.10 + 0.22 * max(0.0, shade - 0.7)
                cover = self.ink[j][i]
                row.append(ground_value * (1 - cover) + ink * cover)
            self.value.append(row)

    def drape(self, kind, cx, cy, scale, angle):
        """Rasterise one glyph into the ink layer, shifted by the slope beneath each pixel."""
        res = self.res
        reach = 24 * scale + DRAPE * 1.5 + 2
        i0, i1 = max(0, int((cx - reach - MAP_X) * res)), min(self.w - 1, int((cx + reach - MAP_X) * res) + 1)
        j0, j1 = max(0, int((cy - reach - MAP_Y) * res)), min(self.h - 1, int((cy + reach - MAP_Y) * res) + 1)
        cos_a, sin_a = math.cos(math.radians(-angle)), math.sin(math.radians(-angle))
        segments = GLYPH_SEGMENTS[kind]
        half = GLYPH_STROKE / 2
        for j in range(j0, j1 + 1):
            y = MAP_Y + (j + 0.5) / res
            for i in range(i0, i1 + 1):
                x = MAP_X + (i + 0.5) / res
                gx, gy = self.gradient[j][i]
                dx, dy = x + DRAPE * gx - cx, y + DRAPE * gy - cy
                u = (dx * cos_a - dy * sin_a) / scale
                v = (dx * sin_a + dy * cos_a) / scale
                d = min(segment_distance(u, v, x1, y1, x2, y2) for (x1, y1), (x2, y2) in segments)
                edge = (d - half) * scale * res
                if edge < 1.0:
                    cover = 1 - smoothstep(-0.8, 0.8, edge)
                    if cover > self.ink[j][i]:
                        self.ink[j][i] = cover

    def signature(self):
        return digest(b"".join(bytes(int(round(v * 255)) for v in row) for row in self.value))


def ground(res):
    if res not in _GROUND:
        _GROUND[res] = Ground(res)
    return _GROUND[res]


# --- fog -------------------------------------------------------------------

class Fog:
    """Per-treatment noise fields, shared by all ten samples of that treatment."""

    def __init__(self, treatment):
        self.treatment = treatment
        self.zones = zones()
        self.fields = distance_fields()
        self.noise = Noise({"w1": 7301, "w2": 7302, "w3": 7303}[treatment], cell=44.0)
        self.patch = Noise(9901, cell=70.0)


def fog_levels(data, sample):
    states = sample["states"]
    now = {key: states[key] for key in PROPOSITIONS[:5]}
    now["P1-foothold"] = states["p1_foothold"]
    for key, state in states["observations"].items():
        now[f"observation-{key}"] = state
    previous = PREVIOUS.get(sample["fixture"])
    if previous:
        before = states_for(data, previous, sample["viewpoint"])
        earlier = {key: before[key] for key in PROPOSITIONS[:5]}
        earlier["P1-foothold"] = before["p1_foothold"]
        earlier.update({f"observation-{k}": v for k, v in before["observations"].items()})
        for key, state in now.items():
            if state == "dark" and earlier.get(key) in ("lit", "hatched"):
                now[key] = "refog"
    return now


def veil_rows(fog, levels):
    """Fog veil per fog cell, 0 clear to 1 opaque."""
    noise, patch = fog.noise, fog.patch
    order = sorted(fog.zones)
    rows = []
    for j in range(GH):
        y = MAP_Y + (j + 0.5) * FOG_SCALE
        row = []
        for i in range(GW):
            x = MAP_X + (i + 0.5) * FOG_SCALE
            n = noise.at(x, y)
            veil = 1.0
            for key in order:
                level = levels[key]
                if level == "dark":
                    continue
                target = VEIL[level]
                if fog.treatment == "w2":
                    _, (cx, cy), radius = fog.zones[key]
                    radius *= {"lit": 1.0, "hatched": 0.78, "refog": 0.9}[level]
                    d = math.hypot(x - cx, y - cy) - radius
                    member = 1 - smoothstep(-18, 18, d + n * 26)
                    if level == "hatched":
                        target = 0.62 if int((x + y) // 6) % 2 == 0 else 0.14
                else:
                    d = fog.fields[key][j][i]
                    amp, feather = (16, 10) if fog.treatment == "w1" else (30, 14)
                    member = 1 - smoothstep(-feather, feather, d + n * amp)
                    if fog.treatment == "w3" and level == "hatched":
                        target = 0.12 + 0.78 * smoothstep(-0.12, 0.22, patch.at(x, y) + n * 0.35)
                    elif level == "hatched":
                        target = 0.62 if int((x + y) // 6) % 2 == 0 else 0.14
                veil = min(veil, 1 - member * (1 - target))
            row.append(max(0.0, min(1.0, veil)))
        rows.append(row)
    return rows


def composite(base, veil):
    """Ground brightness under the veil, quantised to palette indices."""
    res = base.res
    rows = []
    top = LEVELS - 1
    for j in range(base.h):
        y = MAP_Y + (j + 0.5) / res
        values = base.value[j]
        row = bytearray()
        for i in range(base.w):
            x = MAP_X + (i + 0.5) / res
            v = values[i] * (1 - sample_field(veil, x, y))
            row.append(int(round(max(0.0, min(1.0, v)) * top)))
        rows.append(row)
    return png_palette(base.w, base.h, rows)


# --- drawing -----------------------------------------------------------------

def label_layer(presence):
    """Nothing lettered inside the map. P6's presence is a survey mark above the fog, never a fill."""
    out = '<g data-layer="labels">'
    if presence != "hidden":
        out += f'<g data-region="P6" data-state="dark" data-presence="{presence}">'
        out += f'<path d="M747,112 L747,456" fill="none" stroke="{STEEL}" stroke-width="1.4" stroke-dasharray="3 7"/>'
        if presence == "acknowledged":
            out += glyph_svg("P6", 850, 276, 0.8, STEEL, 1.6)
        out += '</g>'
    return out + '</g>'


def state_layer(levels):
    out = '<g data-layer="states" aria-hidden="true">'
    for key, level in sorted(levels.items()):
        state = "dark" if level == "refog" else level
        out += f'<g data-region="{key}" data-state="{state}" data-fog="{level}"/>'
    out += '<g data-region="P6" data-state="dark" data-fog="dark"/>'
    return out + '</g>'


def render(data, sample, veil, res):
    prefix = sample["id"]
    fixture = data["fixtures"][sample["fixture"]]
    levels = fog_levels(data, sample)
    presence = sample["states"]["p6_presence"]
    base = ground(res)
    png = base64.b64encode(composite(base, veil)).decode("ascii")
    glyph_counts = {}
    for kind, *_ in base.instances:
        family = kind.split("/")[0]
        glyph_counts[family] = glyph_counts.get(family, 0) + 1
    metadata = {"renderer": RENDERER_VERSION, "states": sample["states"], "fog": levels, "resolution": res,
                "ground_sha256": base.signature(), "glyphs": glyph_counts,
                "distinct_glyphs": len({kind for kind, *_ in base.instances})}
    out = (f'<svg xmlns="{NS}" width="960" height="640" viewBox="0 0 960 640" role="img" '
           f'aria-labelledby="{prefix}-title {prefix}-desc" data-sample-id="{prefix}">')
    out += f'<title id="{prefix}-title">{escape(sample["family_label"] + " — " + fixture["label"] + " — " + sample["viewpoint_label"])}</title>'
    out += f'<desc id="{prefix}-desc">{escape(sample["alt"])}</desc>'
    out += f'<metadata>{escape(json.dumps(metadata, sort_keys=True))}</metadata>'
    out += (f'<defs><pattern id="{prefix}-hatch" patternUnits="userSpaceOnUse" width="9" height="9">'
            f'<path d="M-2,2 L2,-2 M0,9 L9,0 M7,11 L11,7" stroke="{INK}" stroke-width="1.1" fill="none"/></pattern></defs>')
    out += rect(0, 0, 960, 640, INK)
    out += text(28, 29, f'{sample["family"].upper()} / {sample["family_label"].upper()}', 21, weight="bold")
    out += text(932, 28, sample["viewpoint_label"].upper(), 17, anchor="end", weight="bold")
    out += text(28, 53, fixture["label"], 15)
    out += text(932, 53, "DESIGN SAMPLE / NOT ADOPTED", 12, anchor="end", mono=True)
    out += line(28, 68, 932, 68, DIRTY)
    x = 28
    for key, name in (("P1", "COORDINATION"), ("P2", "RECURRENCE"), ("P3", "RECORD = EVENT"), ("P4", "REPORTING"),
                      ("P5", "MEASUREMENT"), ("P6", "UNREACHABLE")):
        out += glyph_svg(key, x + 8, 82, 0.34, PAPER, 3.2) + text(x + 20, 86, f"{key} {name}", 10, DIRTY, mono=True)
        x += 20 + (len(name) + 3) * 6.1 + 14
    x = 28
    for key, name in (("response", "ALERT / BOARD / PIVOT"), ("correction", "SCORER ACCOUNTS"),
                      ("configuration", "CONFIGURATION ACCOUNT"), ("weights", "WEIGHTS ACCOUNT")):
        out += glyph_svg(key, x + 8, 98, 0.34, PAPER, 3.2) + text(x + 20, 102, name, 10, DIRTY, mono=True)
        x += 20 + len(name) * 6.1 + 14
    out += text(932, 102, "ONE FORM OF EACH FAMILY SHOWN / ALL LIE UNDER THE FOG", 10, DIRTY, anchor="end", mono=True)
    out += '<g data-layer="map">'
    out += (f'<image data-layer="ground-and-fog" x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" '
            f'preserveAspectRatio="none" href="data:image/png;base64,{png}"/>')
    out += label_layer(presence) + state_layer(levels) + '</g>'
    out += rect(28, 542, 904, 34, PAPER)
    out += text(40, 564, fixture["captions"][sample["viewpoint"]], 15, INK, weight="bold")
    out += text(28, 594, fixture["source_label"] + "  ·  OUR INFERENCE / SCHEMATIC RELIEF / FOG IS COMPUTED, NOT MEASURED", 12)
    swatches = [("dark", "UNEXPLORED / NO SUPPORT"), ("refog", "SEEN, SUPPORT LOST"),
                ("hatched", "CONTESTED / SINGLE-SOURCE"), ("lit", "VISIBLE / EVIDENCE")]
    x = 28
    for level, word in swatches:
        out += rect(x, 611, 17, 17, PAPER, DIRTY)
        out += rect(x, 611, 17, 17, INK, "none", f'fill-opacity="{VEIL[level]:.2f}"')
        if level == "hatched" and sample["family"] != "w3":
            out += rect(x, 611, 17, 17, f"url(#{prefix}-hatch)", "none")
        out += text(x + 24, 624, word, 11)
        x += 32 + len(word) * 6.6
    out += text(932, 624, "SHADING = ALTITUDE", 11, anchor="end")
    return out + '</svg>\n'


# --- samples, sheets, manifest ------------------------------------------------

def sample_id(treatment, fixture, viewpoint):
    if fixture.startswith("010-"):
        return f"{treatment}-010-{viewpoint}-{fixture[4:]}"
    return f"{treatment}-{fixture}-{viewpoint}"


def samples_for(data):
    samples = []
    for treatment, (label_text, _) in TREATMENTS.items():
        for fixture in FIXTURES:
            for viewpoint in VIEWPOINTS:
                states = states_for(data, fixture, viewpoint)
                sid = sample_id(treatment, fixture, viewpoint)
                summary = "; ".join(f"{p} {states[p]}" for p in PROPOSITIONS[:5]) + "."
                summary += f' P1 outer foothold {states["p1_foothold"]}.'
                summary += " Observation islands: " + ", ".join(f"{k} {v}" for k, v in states["observations"].items()) + "."
                presence = {"hint": "is only an unnamed dark hint", "hidden": "has no visual presence in this control; its underlying state is still dark",
                            "acknowledged": "remains dark and unreachable"}[states["p6_presence"]]
                alt = ("Fog of war, " + data["alt_template"].format(
                    family=label_text, fixture=data["fixtures"][fixture]["label"], viewpoint=data["viewpoints"][viewpoint]["label"],
                    summary=summary, presence=presence)
                    + " Shaded relief with a soft, irregular fog edge; unexplored ground is opaque, ground that lost support stays dimly visible. "
                    "Many pictograms lie draped on the ground beneath the fog, not text; a key names them outside the map.")
                model = data["state_models"][data["fixtures"][fixture]["models"][viewpoint]]
                samples.append({"id": sid, "family": treatment, "family_label": label_text, "fixture": fixture,
                                "viewpoint": viewpoint, "viewpoint_label": data["viewpoints"][viewpoint]["label"],
                                "path": sid + ".svg", "alt": alt, "states": states, "source_references": model["sources"],
                                "caption": data["fixtures"][fixture]["captions"][viewpoint]})
    return samples


def contact_sheet(label_text, rows, rendered):
    width = 960 * len(TREATMENTS)
    height = 130 + len(rows) * 680
    out = f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="sheet-title sheet-desc">'
    out += f'<title id="sheet-title">{escape(label_text)}</title><desc id="sheet-desc">Fog treatments are columns, best-ranked first. Each labeled row shares one fixture and viewpoint. Half-resolution ground rasters. Story revelations through page 039.</desc>'
    out += rect(0, 0, width, height, INK)
    out += text(28, 38, label_text.upper(), 26, weight="bold")
    out += text(28, 66, "FOG-OF-WAR STUDIES — NOT ADOPTED / COLUMNS W3, W2, W1 / OPEN AT FULL SIZE / REVELATIONS THROUGH 039", 18)
    for j, (fixture, viewpoint) in enumerate(rows):
        y = 130 + j * 680
        out += text(28, y - 12, f'{fixture.upper()} / {viewpoint.upper()}', 20, weight="bold")
        for i, treatment in enumerate(TREATMENTS):
            content = rendered[sample_id(treatment, fixture, viewpoint)].decode("utf-8")
            out += content.replace('<svg ', f'<svg x="{i * 960}" y="{y}" ', 1).strip()
    return (out + '</svg>\n').encode("utf-8")


def build_outputs(data):
    samples = samples_for(data)
    fogs = {treatment: Fog(treatment) for treatment in TREATMENTS}
    veils = {s["id"]: veil_rows(fogs[s["family"]], fog_levels(data, s)) for s in samples}
    rendered = {s["id"]: render(data, s, veils[s["id"]], SAMPLE_RES).encode("utf-8") for s in samples}
    rendered_sheet = {s["id"]: render(data, s, veils[s["id"]], SHEET_RES).encode("utf-8") for s in samples}
    files = {s["path"]: rendered[s["id"]] for s in samples}
    sheets = []
    for viewpoint in VIEWPOINTS:
        for group, fixtures in [("010", ("010-hint", "010-no-p6")), ("016", ("016",)), ("039", ("039-before", "039-after"))]:
            name = f"contact-{group}-{viewpoint}.svg"
            title = f'{group} fog comparison / {data["viewpoints"][viewpoint]["label"]}'
            files[name] = contact_sheet(title, [(f, viewpoint) for f in fixtures], rendered_sheet)
            sheets.append({"path": name, "label": title, "rows": [{"fixture": f, "viewpoint": viewpoint} for f in fixtures], "sha256": digest(files[name])})
    inputs = {"data/knowledge-map-samples.json": digest(km.DATA.read_bytes()),
              "scripts/knowledge_maps_fog.py": digest(Path(__file__).read_bytes())}
    for sample in samples:
        sample["sha256"] = digest(files[sample["path"]])
    base = ground(SAMPLE_RES)
    manifest = {"version": 1, "renderer_version": RENDERER_VERSION, "status": data["status"], "warning": data["warning"],
                "input_hash": digest(encoded(inputs)), "inputs": inputs,
                "treatments": {k: {"label": v[0], "hypothesis": v[1]} for k, v in TREATMENTS.items()},
                "fog_levels": VEIL, "resolution": {"sample": SAMPLE_RES, "sheet": SHEET_RES},
                "ground_sha256": base.signature(), "glyph_instances": len(base.instances),
                "glyph_forms": len(GLYPHS), "glyph_families": {family: len(kinds) for family, kinds in FAMILIES.items()},
                "samples": samples, "contact_sheets": sheets,
                "terrain_note": ("A-family region layout as hillshaded relief with ridges on the boundaries and mesas for the observation "
                                 "strips; pictograms are scattered irregularly, draped over the relief, and fogged with it. One palette PNG per sample."),
                "model_note": data["model_note"]}
    files["manifest.json"] = encoded(manifest)
    return files, manifest


def check_svg(content, name):
    root = ET.fromstring(content)
    km.require(root.tag == f'{{{NS}}}svg', f"Not SVG: {name}")
    km.require(root.find(f'{{{NS}}}title') is not None and root.find(f'{{{NS}}}desc') is not None, f"Accessible labels missing: {name}")
    ids = [e.attrib["id"] for e in root.iter() if "id" in e.attrib]
    km.require(len(ids) == len(set(ids)), f"Duplicate SVG IDs: {name}")
    for node in root.iter():
        km.require(node.tag not in {f'{{{NS}}}script', f'{{{NS}}}foreignObject'}, f"Unsafe SVG element: {name}")
        for attr, value in node.attrib.items():
            km.require(not attr.lower().startswith("on"), f"Event attribute: {name}")
            if attr.endswith("href"):
                km.require(value.startswith("data:image/png;base64,") or (value.startswith("#") and value[1:] in ids), f"External SVG reference: {name}")
            if value.startswith("url(#"):
                km.require(value[5:-1] in ids, f"Broken SVG paint/clip reference: {name}")
    return root


def check_outputs(data, folder=OUTPUT):
    km.validate_data(data)
    expected, manifest = build_outputs(data)
    km.require(folder.is_dir(), f"Missing output directory: {folder}; run generate")
    for name, content in expected.items():
        target = folder / name
        km.require(target.is_file() and target.read_bytes() == content, f"Stale or non-reproducible output: {name}; run generate")
    grounds = set()
    for sample in manifest["samples"]:
        root = check_svg(expected[sample["path"]], sample["path"])
        states = {e.attrib["data-region"]: e.attrib["data-state"] for e in root.iter() if "data-region" in e.attrib and "data-state" in e.attrib}
        km.require(states.get("P6") == "dark", f"P6 must stay dark: {sample['id']}")
        for key in PROPOSITIONS[:5]:
            km.require(states[key] == sample["states"][key], f"State drift {key}: {sample['id']}")
        km.require(states["P1-foothold"] == sample["states"]["p1_foothold"], f"Foothold drift: {sample['id']}")
        fog = {e.attrib["data-region"]: e.attrib["data-fog"] for e in root.iter() if "data-fog" in e.attrib}
        km.require(all(level != "refog" for level in fog.values()) or sample["fixture"] == "039-after", f"Re-fog outside 039: {sample['id']}")
        if sample["fixture"] == "039-after" and sample["viewpoint"] == "reader":
            km.require(fog["P2"] == "refog" and fog["P1-foothold"] == "refog", f"039 must re-fog P2 and the foothold: {sample['id']}")
        image = [e for e in root.iter() if e.tag == f'{{{NS}}}image']
        km.require(len(image) == 1 and image[0].attrib.get("data-layer") == "ground-and-fog", f"Exactly one composited raster expected: {sample['id']}")
        map_layer = next(e for e in root.iter() if e.attrib.get("data-layer") == "map")
        km.require(not any(e.tag == f'{{{NS}}}text' for e in map_layer.iter()), f"No text may appear inside the map: {sample['id']}")
        meta = json.loads(root.find(f'{{{NS}}}metadata').text)
        km.require(set(meta["glyphs"]) == set(FAMILIES) and min(meta["glyphs"].values()) >= 3, f"Every symbol family must lie on the ground several times: {sample['id']}")
        km.require(meta["distinct_glyphs"] >= 50, f"Too few distinct symbol forms on the ground: {sample['id']}")
        grounds.add(meta["ground_sha256"])
    km.require(len(grounds) == 1 and grounds == {manifest["ground_sha256"]}, "Ground relief and glyphs must be identical across every sample")
    placed = ground(SAMPLE_RES).instances
    for a, (kind_a, xa, ya, *_) in enumerate(placed):
        for kind_b, xb, yb, *_ in placed[a + 1:]:
            km.require(kind_a != kind_b or math.hypot(xa - xb, ya - yb) >= 60, f"Adjacent glyphs share a form: {kind_a}")
    km.require(len({kind for kind, *_ in placed}) >= 50 and len(placed) >= 120, "Expected a large, varied glyph population")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "check"))
    args = parser.parse_args(argv)
    try:
        data = load_data()
        km.validate_data(data)
        if args.command == "generate":
            files, _ = build_outputs(data)
            OUTPUT.mkdir(parents=True, exist_ok=True)
            for stale in OUTPUT.glob("*"):
                if stale.name not in files:
                    stale.unlink()
            for name, content in files.items():
                (OUTPUT / name).write_bytes(content)
        manifest = check_outputs(data)
        print(f'{args.command}: OK — {len(manifest["samples"])} fog samples, {len(manifest["contact_sheets"])} contact sheets, '
              f'{manifest["glyph_instances"]} draped glyphs in {manifest["glyph_forms"]} forms; inputs {manifest["input_hash"]}')
        return 0
    except (ValueError, KeyError, OSError, ET.ParseError) as exc:
        print(f"knowledge maps fog: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
