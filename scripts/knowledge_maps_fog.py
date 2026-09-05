#!/usr/bin/env python3
"""Fog-of-war knowledge-map studies: soft, irregular fog computed as a raster veil.

The v1 families draw evidence as filled polygons with hard vector edges. Game
fog of war does not look like that: the cleared area has a boundary that is
neither sharp nor regular, and terrain that was once seen stays faintly visible
under the fog. This set keeps the v1 fixtures, viewpoints, captions and the A
family's terrain, and replaces the fills with a computed fog layer:

  * the terrain (coastlines, contours, paths) is drawn once as vectors;
  * a raster veil is computed per sample from signed distances to the regions,
    displaced by seeded value noise and feathered, then embedded as a PNG;
  * labels and chrome sit above the fog.

Three treatments differ only in how the veil is computed:

  w1  Ragged regions  — each region's fog edge is noise-displaced and feathered.
  w2  Line of sight   — vision discs around the places evidence comes from.
  w3  Patchy contest  — contested ground is visible in patches instead of hatched.

Fog levels: unexplored (opaque), re-fogged (terrain dimly visible: it was seen
and lost support), contested (partly veiled), visible (clear). Re-fogged is the
game's "explored but not currently visible" state and is drawing rule 4 made
literal. P6 is always unexplored. Everything is deterministic, standard-library
Python; `check` regenerates in memory and compares bytes.

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
from knowledge_maps import (AMBER, DIRTY, INK, NS, PAPER, SHADOW, STEEL, FIXTURES, VIEWPOINTS,
                            PROPOSITIONS, digest, encoded, label, line, load_data, path, rect,
                            states_for, text)

ROOT = km.ROOT
OUTPUT = ROOT / "assets/knowledge-maps/fog-v1"
RENDERER_VERSION = "knowledge-map-fog-1.0.0"
TREATMENTS = {
    "w1": ("Ragged regions", "Regional fog with a noise-displaced, feathered edge; contested ground is striped fog inside the same soft edge."),
    "w2": ("Line of sight", "Vision discs around the places evidence comes from; the region outlines are only visible where sight reaches."),
    "w3": ("Patchy contest", "Contested ground is visible in irregular patches rather than hatched; the fog itself carries the uncertainty."),
}
MAP_X, MAP_Y, MAP_W, MAP_H = 28, 100, 904, 440
SCALE = 2                                  # raster cells per map pixel
GW, GH = MAP_W // SCALE, MAP_H // SCALE    # 452 x 220 fog cells
VEIL = {"lit": 0.0, "hatched": 0.34, "refog": 0.68, "dark": 1.0}
FOG_RGB = (16, 18, 20)
PREVIOUS = {"039-after": "039-before"}

# The A-family terrain, so the fog studies stay comparable with v1 A.
REGIONS = {
    "P1": [(48, 136), (120, 108), (272, 126), (294, 189), (250, 275), (137, 265), (60, 218)],
    "P2": [(272, 126), (416, 109), (515, 153), (490, 266), (370, 284), (294, 189)],
    "P3": [(60, 218), (137, 265), (250, 275), (284, 380), (209, 445), (86, 427), (40, 338)],
    "P4": [(250, 275), (370, 284), (490, 266), (501, 372), (451, 451), (330, 435), (284, 380)],
    "P5": [(515, 153), (636, 112), (714, 150), (706, 293), (668, 425), (565, 439), (501, 372), (490, 266)],
}
LABEL_AT = {"P1": (170, 189), "P2": (397, 191), "P3": (158, 340), "P4": (386, 357), "P5": (604, 284)}
P6_SHAPE = [(769, 112), (936, 105), (921, 448), (771, 459)]
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
    """Every fogged zone with its polygon and, for line of sight, its vision centre and radius."""
    out = {}
    for key, pts in REGIONS.items():
        out[key] = (pts, LABEL_AT[key], 132)
    fh = foothold_polygon()
    out["P1-foothold"] = (fh, (sum(p[0] for p in fh) / len(fh), sum(p[1] for p in fh) / len(fh)), 62)
    for i, key in enumerate(("response", "correction", "configuration", "weights")):
        pts = observation_polygon(i)
        out[f"observation-{key}"] = (pts, (40 + i * 224 + 105, 507), 60)
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
    """Signed distance (map pixels, negative inside) from every fog cell to the polygon edge."""
    field = []
    n = len(pts)
    edges = [(pts[i], pts[(i + 1) % n]) for i in range(n)]
    for j in range(GH):
        y = MAP_Y + (j + 0.5) * SCALE
        row = []
        for i in range(GW):
            x = MAP_X + (i + 0.5) * SCALE
            d = min(segment_distance(x, y, x1, y1, x2, y2) for (x1, y1), (x2, y2) in edges)
            row.append(-d if inside(pts, x, y) else d)
        field.append(row)
    return field


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


def png_rgba(width, height, alpha_rows):
    raw = bytearray()
    r, g, b = FOG_RGB
    for row in alpha_rows:
        raw.append(0)
        for a in row:
            raw += bytes((r, g, b, a))
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# --- fog -------------------------------------------------------------------

_FIELDS = {}


def distance_fields(zone_table):
    """Signed distance fields are the same for every treatment and sample; compute them once."""
    if not _FIELDS:
        _FIELDS.update({key: signed_distance_field(pts) for key, (pts, _, _) in zone_table.items()})
    return _FIELDS


class Terrain:
    """Per-treatment precomputation shared by all ten samples: distance fields and noise."""

    def __init__(self, treatment):
        self.treatment = treatment
        self.zones = zones()
        self.fields = distance_fields(self.zones)
        self.noise = Noise({"w1": 7301, "w2": 7302, "w3": 7303}[treatment], cell=44.0)
        self.patch = Noise(9901, cell=70.0)


def fog_levels(data, sample):
    states = sample["states"]
    now = {}
    for key in PROPOSITIONS[:5]:
        now[key] = states[key]
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


def veil_rows(terrain, levels):
    """Alpha rows for the fog raster: 255 is opaque unexplored fog."""
    noise, patch = terrain.noise, terrain.patch
    order = sorted(terrain.zones)
    rows = []
    for j in range(GH):
        y = MAP_Y + (j + 0.5) * SCALE
        row = bytearray()
        for i in range(GW):
            x = MAP_X + (i + 0.5) * SCALE
            n = noise.at(x, y)
            veil = 1.0
            for key in order:
                level = levels[key]
                if level == "dark":
                    continue
                target = VEIL[level]
                if terrain.treatment == "w2":
                    _, (cx, cy), radius = terrain.zones[key]
                    radius *= {"lit": 1.0, "hatched": 0.78, "refog": 0.9}[level]
                    d = math.hypot(x - cx, y - cy) - radius
                    member = 1 - smoothstep(-18, 18, d + n * 26)
                    if level == "hatched":
                        target = 0.62 if int((x + y) // 6) % 2 == 0 else 0.14
                else:
                    d = terrain.fields[key][j][i]
                    amp, feather = (16, 10) if terrain.treatment == "w1" else (30, 14)
                    member = 1 - smoothstep(-feather, feather, d + n * amp)
                    if terrain.treatment == "w3" and level == "hatched":
                        target = 0.12 + 0.78 * smoothstep(-0.12, 0.22, patch.at(x, y) + n * 0.35)
                    elif level == "hatched":
                        target = 0.62 if int((x + y) // 6) % 2 == 0 else 0.14
                veil = min(veil, 1 - member * (1 - target))
            row.append(int(round(max(0.0, min(1.0, veil)) * 255)))
        rows.append(row)
    return rows


# --- drawing -----------------------------------------------------------------

def terrain_layer(prefix, treatment, levels):
    """Continuous terrain under the whole map: the fog is the only boundary the reader sees."""
    out = '<g data-layer="terrain">'
    out += rect(MAP_X, MAP_Y, MAP_W, MAP_H, PAPER)
    out += f'<g data-layer="retained-terrain" fill="none" stroke="{STEEL}" stroke-width="0.9">'
    for y in range(106, 540, 19):
        bend = ((y // 19) % 3 - 1) * 11
        out += f'<path d="M{MAP_X - 8},{y} C230,{y - 26 + bend} 470,{y + 30} {MAP_X + MAP_W + 8},{y - 14}"/>'
    for cx, cy in ((190, 210), (430, 230), (150, 372), (400, 385), (600, 300), (840, 250), (300, 505), (740, 505)):
        for k in range(3):
            out += f'<ellipse cx="{cx}" cy="{cy}" rx="{16 + k * 11}" ry="{8 + k * 7}" transform="rotate(-24 {cx} {cy})"/>'
    for sx, sy in ((120, 250), (330, 200), (560, 330), (450, 330), (200, 420), (650, 180), (850, 400)):
        out += f'<path d="M{sx},{sy} l6,-9 l6,9 Z" fill="{INK}" stroke="{DIRTY}"/>'
    out += '</g>'
    out += f'<g data-layer="survey-lines" fill="none" stroke="{SHADOW}" stroke-width="0.9" stroke-dasharray="5 4">'
    for key, pts in list(REGIONS.items()) + [("P1-foothold", foothold_polygon())]:
        out += f'<path data-terrain="{key}" d="{path(pts)}"/>'
    for i, key in enumerate(("response", "correction", "configuration", "weights")):
        out += f'<path data-terrain="observation-{key}" d="{path(observation_polygon(i))}"/>'
    out += f'<path data-terrain="survey-border" d="M747,106 L747,456" stroke="{INK}" stroke-width="2.5" stroke-dasharray="9 6"/>'
    out += '</g>'
    return out + '</g>'


def label_layer(prefix, levels, presence):
    words = {"P1": ["P1 / COORDINATION", "deliberate?"], "P2": ["P2 / RECURRENCE", "independent?"],
             "P3": ["P3 / RECORD", "equals event?"], "P4": ["P4 / REPORTING", "nobody told?"],
             "P5": ["P5 / MEASUREMENT", "independent?"]}
    out = '<g data-layer="labels">'
    for key, at in LABEL_AT.items():
        level = levels[key]
        if level == "dark":
            out += text(at[0], at[1] - 2, key, 13, STEEL, "middle", mono=True, weight="bold")
            out += text(at[0], at[1] + 13, "UNEXPLORED", 10, STEEL, "middle", mono=True)
        elif level == "refog":
            out += text(at[0], at[1] - 2, words[key][0], 12, DIRTY, "middle", weight="bold")
            out += text(at[0], at[1] + 13, "SEEN / SUPPORT LOST", 10, DIRTY, "middle", mono=True)
        else:
            out += label(at[0], at[1], words[key], dark=False)
    for i, key in enumerate(("response", "correction", "configuration", "weights")):
        level = levels[f"observation-{key}"]
        x = 40 + i * 224 + 105
        if level == "dark":
            out += text(x, 512, "UNSURVEYED", 10, STEEL, "middle", mono=True)
        elif level == "refog":
            out += text(x, 512, OBSERVATION_NAMES[key], 10, DIRTY, "middle", mono=True)
        else:
            out += label(x, 508, [OBSERVATION_NAMES[key]], dark=False, size=11)
    if presence != "hidden":
        lines = ["P6", "UNMAPPED"] if presence == "hint" else ["P6 / UNREACHABLE", "NO CAUSAL ACCESS"]
        out += f'<g data-region="P6" data-state="dark" data-presence="{presence}">'
        out += text(850, 268, lines[0], 12, STEEL, "middle", mono=True, weight="bold")
        out += text(850, 284, lines[1], 10, STEEL, "middle", mono=True)
        out += '</g>'
    return out + '</g>'


def state_layer(levels):
    out = '<g data-layer="states" aria-hidden="true">'
    for key, level in sorted(levels.items()):
        state = "dark" if level == "refog" else level
        out += f'<g data-region="{key}" data-state="{state}" data-fog="{level}"/>'
    out += '<g data-region="P6" data-state="dark" data-fog="dark"/>'
    return out + '</g>'


def render(data, sample, terrain):
    prefix = sample["id"]
    fixture = data["fixtures"][sample["fixture"]]
    levels = fog_levels(data, sample)
    presence = sample["states"]["p6_presence"]
    alpha = veil_rows(terrain, levels)
    png = base64.b64encode(png_rgba(GW, GH, alpha)).decode("ascii")
    out = (f'<svg xmlns="{NS}" width="960" height="640" viewBox="0 0 960 640" role="img" '
           f'aria-labelledby="{prefix}-title {prefix}-desc" data-sample-id="{prefix}">')
    out += f'<title id="{prefix}-title">{escape(sample["family_label"] + " — " + fixture["label"] + " — " + sample["viewpoint_label"])}</title>'
    out += f'<desc id="{prefix}-desc">{escape(sample["alt"])}</desc>'
    out += f'<metadata>{escape(json.dumps({"renderer": RENDERER_VERSION, "states": sample["states"], "fog": levels}, sort_keys=True))}</metadata>'
    out += (f'<defs><pattern id="{prefix}-hatch" patternUnits="userSpaceOnUse" width="9" height="9">'
            f'<path d="M-2,2 L2,-2 M0,9 L9,0 M7,11 L11,7" stroke="{INK}" stroke-width="1.1" fill="none"/></pattern></defs>')
    out += rect(0, 0, 960, 640, INK)
    out += text(28, 29, f'{sample["family"].upper()} / {sample["family_label"].upper()}', 21, weight="bold")
    out += text(932, 28, sample["viewpoint_label"].upper(), 17, anchor="end", weight="bold")
    out += text(28, 53, fixture["label"], 15)
    out += text(932, 53, "DESIGN SAMPLE / NOT ADOPTED", 12, anchor="end", mono=True)
    out += line(28, 68, 932, 68, DIRTY)
    out += text(28, 88, "OUR INFERENCE / SCHEMATIC TERRAIN / FOG IS COMPUTED, NOT MEASURED", 11, mono=True)
    out += '<g data-layer="map">' + terrain_layer(prefix, sample["family"], levels)
    out += (f'<image data-layer="fog" x="{MAP_X}" y="{MAP_Y}" width="{MAP_W}" height="{MAP_H}" '
            f'preserveAspectRatio="none" href="data:image/png;base64,{png}"/>')
    out += label_layer(prefix, levels, presence) + state_layer(levels) + '</g>'
    out += rect(28, 542, 904, 34, PAPER)
    out += text(40, 564, fixture["captions"][sample["viewpoint"]], 15, INK, weight="bold")
    out += text(28, 594, fixture["source_label"], 12)
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
    out += text(932, 624, "P1 OUTER BAND = FOOTHOLD", 11, anchor="end")
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
                    + " Fog has a soft irregular edge; unexplored ground is opaque, ground that lost support stays dimly visible.")
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
    out += f'<title id="sheet-title">{escape(label_text)}</title><desc id="sheet-desc">Fog treatments W1–W3 are columns. Each labeled row shares one fixture and viewpoint. Story revelations through page 039.</desc>'
    out += rect(0, 0, width, height, INK)
    out += text(28, 38, label_text.upper(), 26, weight="bold")
    out += text(28, 66, "FOG-OF-WAR STUDIES — NOT ADOPTED / COLUMNS W1–W3 / OPEN AT FULL SIZE / REVELATIONS THROUGH 039", 18)
    for j, (fixture, viewpoint) in enumerate(rows):
        y = 130 + j * 680
        out += text(28, y - 12, f'{fixture.upper()} / {viewpoint.upper()}', 20, weight="bold")
        for i, treatment in enumerate(TREATMENTS):
            content = rendered[sample_id(treatment, fixture, viewpoint)].decode("utf-8")
            out += content.replace('<svg ', f'<svg x="{i * 960}" y="{y}" ', 1).strip()
    return (out + '</svg>\n').encode("utf-8")


def build_outputs(data):
    samples = samples_for(data)
    terrains = {treatment: Terrain(treatment) for treatment in TREATMENTS}
    rendered = {s["id"]: render(data, s, terrains[s["family"]]).encode("utf-8") for s in samples}
    files = {s["path"]: rendered[s["id"]] for s in samples}
    sheets = []
    for viewpoint in VIEWPOINTS:
        for group, fixtures in [("010", ("010-hint", "010-no-p6")), ("016", ("016",)), ("039", ("039-before", "039-after"))]:
            name = f"contact-{group}-{viewpoint}.svg"
            title = f'{group} fog comparison / {data["viewpoints"][viewpoint]["label"]}'
            files[name] = contact_sheet(title, [(f, viewpoint) for f in fixtures], rendered)
            sheets.append({"path": name, "label": title, "rows": [{"fixture": f, "viewpoint": viewpoint} for f in fixtures], "sha256": digest(files[name])})
    inputs = {"data/knowledge-map-samples.json": digest(km.DATA.read_bytes()),
              "scripts/knowledge_maps_fog.py": digest(Path(__file__).read_bytes())}
    for sample in samples:
        sample["sha256"] = digest(files[sample["path"]])
    manifest = {"version": 1, "renderer_version": RENDERER_VERSION, "status": data["status"], "warning": data["warning"],
                "input_hash": digest(encoded(inputs)), "inputs": inputs,
                "treatments": {k: {"label": v[0], "hypothesis": v[1]} for k, v in TREATMENTS.items()},
                "fog_levels": VEIL, "samples": samples, "contact_sheets": sheets,
                "terrain_note": "A-family terrain; fog is a computed raster veil with noise-displaced feathered edges, embedded as PNG.",
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
        km.require(len(image) == 1 and image[0].attrib.get("data-layer") == "fog", f"Exactly one fog raster expected: {sample['id']}")
        terrain = [e.attrib["d"] for e in root.iter() if "data-terrain" in e.attrib]
        km.require(len(terrain) == len(REGIONS) + 1 + 4 + 1, f"Terrain layer changed: {sample['id']}")
    for treatment in TREATMENTS:
        layers = set()
        for sample in manifest["samples"]:
            if sample["family"] != treatment:
                continue
            root = ET.fromstring(expected[sample["path"]])
            layers.add(tuple(e.attrib["d"] for e in root.iter() if "data-terrain" in e.attrib))
        km.require(len(layers) == 1, f"Terrain must be registered across all samples of {treatment}")
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
            for name, content in files.items():
                (OUTPUT / name).write_bytes(content)
        manifest = check_outputs(data)
        print(f'{args.command}: OK — {len(manifest["samples"])} fog samples, {len(manifest["contact_sheets"])} contact sheets; inputs {manifest["input_hash"]}')
        return 0
    except (ValueError, KeyError, OSError, ET.ParseError) as exc:
        print(f"knowledge maps fog: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
