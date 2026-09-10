#!/usr/bin/env python3
"""QR codes whose ink is ant bodies, and an honest price list for each one.

The dark half of a QR symbol does not have to be squares. It has to be dark
where a scanner looks. Everything between those two facts is available for
drawing, and this tool spends it on the edition's ant.

Drawing with ants costs error correction. A square module is dark across its
whole cell; an ant is dark along its body and bare between its legs, so some
modules read wrong, the Reed-Solomon blocks spend part of their budget fixing
them, and past some point the symbol stops decoding. **That cost is measured
here, not asserted.** Every style is rasterised, sampled the way a scanner
samples, decoded through `qr_core`, and reported as the share of the
correction budget it consumed — so the choice between data loss and art
quality is made on numbers.

Ink comes from either register:

  * the edition's own vector ant, read from `data/storyboard-assets.json` so
    the QR ant and the page ant are the same animal, and
  * photographs, as PNGs with alpha or a light background, resampled and
    rotated per module.

This is apparatus, not book art. The QR lattice is a countable grid of ants
and so cannot satisfy the non-quantitative ant convention in the visual bible;
a symbol from this tool belongs on a cover, colophon or card, never in the
margins or panels of a page. See `design/qr-ant-codes.md`.

    python3 scripts/qrant.py report --text "$(cat tag.txt)"
    python3 scripts/qrant.py render --text "..." --style swarm --ecc H --out qr.svg
    python3 scripts/qrant.py options --text "..." --out 256t/qr-options
    python3 scripts/qrant.py check
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import antpose
import qr_core
import rasterize
from rasterize import Grid

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'data' / 'storyboard-assets.json'

QUIET = 4                 # quiet zone, in modules; the standard's minimum
DEFAULT_PX = 10           # rendered pixels per module for measurement
POINT_INSET = 0.35        # a scanner reads the middle of a cell, not its edges
THRESHOLD = 0.5           # coverage at or above this reads dark
FENCE_CAP = 0.015         # ink a functional pattern's light cell may take: none
FENCE_MARGIN = 2          # clear modules kept around each finder pattern
DARK_FLOOR = 0.45         # ink a dark module's whole cell must reach

# Why the cap is on the *cell* and not on the sampling point. A drawing whose
# module centres are all correct can still be unreadable: a real scanner
# binarises against a local neighbourhood before it samples anything, so ink
# that sprawls across a light module's cell darkens that neighbourhood even
# when it misses the centre. Measured against the system scanner, an off-
# lattice scatter with every centre correct and a mean light cell of 0.32 was
# not found at all, while a lattice-bound drawing with a mean light cell of
# 0.09 read every time. The cell mean is the quantity that predicts scanning;
# `light_cap` is the dial on it, and it is the whole trade this tool offers.
INK = '#101214'           # the same ink the page ants use
PAPER = '#E7E0D0'


# --- the ant --------------------------------------------------------------

def ant_shapes() -> list[tuple]:
    """The edition's ant, as raster primitives in its own 100-unit box.

    Read from the tracked asset rather than restated here, so the QR ant
    cannot drift away from the ant the pages draw.
    """
    markup = json.loads(LIBRARY.read_text())['assets']['ant']
    width = float(re.search(r'stroke-width="([\d.]+)"', markup).group(1))
    shapes = []
    for cx, cy, rx, ry in re.findall(
            r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)" rx="([-\d.]+)" ry="([-\d.]+)"', markup):
        shapes.append(rasterize.ellipse(float(cx), float(cy), float(rx), float(ry)))
    for path in re.findall(r'<path d="([^"]+)"', markup):
        for run in path.split('M')[1:]:
            points = [tuple(float(v) for v in pair.split())
                      for pair in run.replace('L', ' L ').split(' L ') if pair.strip()]
            for (x0, y0), (x1, y1) in zip(points, points[1:]):
                shapes.append(rasterize.segment(x0, y0, x1, y1, width))
    if not shapes:
        raise ValueError('the ant asset produced no shapes')
    return shapes


def ant_frame(shapes: list[tuple]) -> tuple[float, float, float]:
    """`(centre x, centre y, long axis)` of the ant in its own units."""
    minx, miny, maxx, maxy = rasterize.bounds(shapes)
    return (minx + maxx) / 2, (miny + maxy) / 2, max(maxx - minx, maxy - miny)


# --- placement ------------------------------------------------------------

@dataclass
class Mark:
    """One ant: centre in module coordinates, long axis in modules, degrees.

    A mark with `shapes` is a *posed* ant — one that was jointed to fit the
    ground it covers, carrying its own geometry relative to its centre. A mark
    without them is the library ant at this size and angle, which is cached and
    stamped thousands of times over.
    """
    x: float
    y: float
    size: float
    angle: float
    shapes: tuple = ()
    pose: object = None


@dataclass
class Style:
    """One way of drawing the dark half, and how careful it is told to be.

    `light_cap` is the whole trade: the most ink any light module's cell may
    take. A low cap keeps the ants on the lattice and costs the code nothing;
    a high cap lets them sprawl into an off-lattice drawing and makes the
    Reed-Solomon blocks pay for it.
    """
    name: str
    summary: str
    place: object                     # (matrix, rng) -> list[Mark]
    light_cap: float = 0.30
    repair: bool = True
    on_light: bool = False
    solid: bool = False               # fill every dark module: the plain control
    posed: tuple = ()                 # (largest, smallest) long axis, in modules
    gaster: float = 0.0               # abdomen width in modules; one square, one abdomen
    every: bool = False               # give every dark module its own abdomen
    overlap: bool = False             # may posed ants lie across each other
    body_mask: bool = False           # choose the mask that suits ant bodies


def _dark_modules(matrix) -> list[tuple[int, int]]:
    return [(x, y) for y, row in enumerate(matrix)
            for x, value in enumerate(row) if value == qr_core.DARK]


def _grid_marks(size: float, jitter: float):
    def place(matrix, rng):
        return [Mark(x + 0.5 + rng.uniform(-jitter, jitter),
                     y + 0.5 + rng.uniform(-jitter, jitter),
                     size * rng.uniform(0.92, 1.08), rng.uniform(0, 360))
                for x, y in _dark_modules(matrix)]
    return place


def _swarm_marks(per_module: float, low: float, high: float, on_light: bool = False):
    """Ants scattered over the ground, off the lattice.

    Density is per dark module so a larger symbol carries proportionally more
    ants, and the drawing never has to be retuned per version. Marks are
    emitted largest first: a big ant that fits is worth more to the picture
    than the three small ones that would have blocked it.
    """
    def place(matrix, rng):
        ground = _dark_modules(matrix)
        if on_light:
            ground = [(x, y) for y in range(len(matrix)) for x in range(len(matrix))]
        marks = []
        for _ in range(int(len(ground) * per_module)):
            x, y = ground[rng.randrange(len(ground))]
            marks.append(Mark(x + rng.uniform(0.2, 0.8), y + rng.uniform(0.2, 0.8),
                              rng.uniform(low, high), rng.uniform(0, 360)))
        marks.sort(key=lambda mark: -mark.size)
        return marks
    return place


STYLES: dict[str, Style] = {}


def _register(style: Style) -> Style:
    STYLES[style.name] = style
    return style


_register(Style('plain', 'Plain squares. The control: no ants, no loss.',
                place=lambda matrix, rng: [], repair=False, solid=True, light_cap=0.0))

_register(Style('grid', 'One ant per dark module, kept inside its own cell.',
                place=_grid_marks(1.5, 0.08), light_cap=0.22))

_register(Style('swarm', 'A scatter off the lattice, held to the same clean field.',
                place=_swarm_marks(3.0, 0.9, 2.2), light_cap=0.22))

_register(Style('dense', 'As many ants as a clean light field will take.',
                place=_swarm_marks(7.0, 0.8, 2.6), light_cap=0.22))

_register(Style('bold', 'Larger ants, allowed to smudge the light field a little.',
                place=_swarm_marks(4.0, 1.1, 3.0), light_cap=0.35))

_register(Style('bolder', 'Ants allowed well into the light field.',
                place=_swarm_marks(4.5, 1.3, 3.4), light_cap=0.50))

_register(Style('halftone', 'Ants over the whole field, light modules included.',
                place=_swarm_marks(3.0, 0.7, 2.4, on_light=True),
                on_light=True, light_cap=0.50))

_register(Style('body-mid', 'Jointed ants up to four modules long, kept apart.',
                place=lambda matrix, rng: [], posed=(4.0, 1.8), body_mask=True,
                light_cap=0.22))

_register(Style('body-large', 'The largest ants this anatomy can fit, kept apart.',
                place=lambda matrix, rng: [], posed=(6.0, 2.0), body_mask=True,
                light_cap=0.22))

_register(Style('body-mid-pile', 'Ants up to four modules long, piled rather than kept apart.',
                place=lambda matrix, rng: [], posed=(4.0, 1.8), body_mask=True,
                overlap=True, light_cap=0.22))

_register(Style('body-large-pile', 'The largest ants, piled rather than kept apart.',
                place=lambda matrix, rng: [], posed=(6.0, 2.0), body_mask=True,
                overlap=True, light_cap=0.22))

_register(Style('body-bold', 'The largest ants, buying room with the correction budget.',
                place=lambda matrix, rng: [], posed=(6.0, 2.0), body_mask=True,
                light_cap=0.40))

_register(Style('abdomen', 'One module square, one ant abdomen, pinned on it.',
                place=lambda matrix, rng: [], gaster=1.0, body_mask=True,
                light_cap=0.22))

_register(Style('abdomen-small', 'The same, with the abdomen a module long rather than wide.',
                place=lambda matrix, rng: [], gaster=0.71, body_mask=True,
                light_cap=0.22))

_register(Style('abdomen-full', 'Every dark square gets its own abdomen; ants overlap.',
                place=lambda matrix, rng: [], gaster=1.0, every=True, overlap=True,
                body_mask=True, light_cap=0.22))

_register(Style('abdomen-bold', 'Abdomens a little wider than the square they sit on.',
                place=lambda matrix, rng: [], gaster=1.15, body_mask=True,
                light_cap=0.35))

_register(Style('wild', 'Large ants, no cap and no repair. The far end.',
                place=_swarm_marks(2.5, 1.8, 4.0), light_cap=1.0, repair=False))


# --- rendering ------------------------------------------------------------

@dataclass
class Symbol:
    payload: bytes
    version: int
    ecc: str
    mask: int
    matrix: list
    function: list
    style: Style
    seed: int

    @property
    def size(self) -> int:
        return qr_core.size_for(self.version)

    @property
    def span(self) -> int:
        return self.size + QUIET * 2


@dataclass
class Drawing:
    """What was actually drawn, and what the drawing cost to fit."""
    grid: Grid
    marks: list
    px: int
    offered: int = 0
    rejected: int = 0
    shrunk: int = 0
    repairs: int = 0
    posed: int = 0                    # jointed ants fitted to the ground

    @property
    def biggest(self) -> float:
        return max((mark.size for mark in self.marks), default=0.0)

    @property
    def mean_size(self) -> float:
        return (sum(mark.size for mark in self.marks) / len(self.marks)
                if self.marks else 0.0)

    @property
    def fitted(self) -> float:
        """Share of the offered ants that found room. Repairs are not offers."""
        return (len(self.marks) - self.repairs) / self.offered if self.offered else 1.0


def body_ground(matrix, function) -> float:
    """Share of the dark modules that sit in a two-by-two block or better.

    A large ant covers ground with its body lobes, and a lobe needs a cell it
    can sit in. This is the quantity that says how much of a symbol a few big
    ants could carry, and it varies by about a fifth across the eight masks.
    """
    size = len(matrix)
    dark = {(x, y) for y in range(size) for x in range(size)
            if matrix[y][x] == qr_core.DARK and not function[y][x]}
    if not dark:
        return 0.0
    thick = {(x, y) for x, y in dark
             if any(all((x + ox + i, y + oy + j) in dark for i in range(2) for j in range(2))
                    for ox in (-1, 0) for oy in (-1, 0))}
    return len(thick) / len(dark)


def choose_mask(payload: bytes, version: int, ecc: str) -> int:
    """The mask whose dark regions best suit ant bodies.

    All eight masks give a valid symbol; the standard picks one by a penalty
    score meant to keep a symbol easy to read, and this picks one by how much
    body-sized ground it leaves. Ties in the standard's own terms are broken by
    that penalty, so the choice never drifts far from it for no gain.
    """
    best, best_key = 0, None
    for mask in range(8):
        matrix, function, _ = qr_core.build_matrix(payload, version, ecc, mask=mask)
        key = (round(body_ground(matrix, function), 3), -qr_core._penalty(matrix))
        if best_key is None or key > best_key:
            best, best_key = mask, key
    return best


def build(text: str, ecc: str, style_name: str, version: int | None = None,
          seed: int | None = None) -> Symbol:
    payload = text.encode()
    style = STYLES[style_name]
    version = version or qr_core.smallest_version(payload, ecc)
    chosen = choose_mask(payload, version, ecc) if style.body_mask else None
    matrix, function, mask = qr_core.build_matrix(payload, version, ecc, mask=chosen)
    if seed is None:
        seed = int.from_bytes(payload[:8].ljust(8, b'\0'), 'big')
    return Symbol(payload, version, ecc, mask, matrix, function, style, seed)


_STAMPS: dict[tuple, tuple] = {}


def _ant_geometry():
    """The ant, centred on its own bounding box and scaled to a unit long axis."""
    shapes = ant_shapes()
    cx, cy, long_axis = ant_frame(shapes)
    centred = []
    for shape in shapes:
        if shape[0] == 'ellipse':
            _, sx, sy, rx, ry = shape
            centred.append(rasterize.ellipse(sx - cx, sy - cy, rx, ry))
        else:
            _, x0, y0, x1, y1, half = shape
            centred.append(rasterize.segment(x0 - cx, y0 - cy, x1 - cx, y1 - cy, half * 2))
    return centred, 1.0 / long_axis


def _ant_stamp(shapes, unit_scale: float, size_px: float, angle: float):
    """A cached ant raster. Size and angle are quantised; both are invisible."""
    key = (max(2, round(size_px / 2) * 2), round(angle / 15) % 24)
    cached = _STAMPS.get(key)
    if cached is None:
        cached = rasterize.stamp(shapes, key[0] * unit_scale, key[1] * 15)
        _STAMPS[key] = cached
    return cached


def _photo_stamp(photo: Grid, size_px: float, angle: float):
    side = max(2, int(round(size_px)))
    stamped = rasterize.rotate(rasterize.resample(photo, side, side), angle)
    return stamped, -stamped.width / 2, -stamped.height / 2


def _centre_box(px: int, mx: int, my: int) -> tuple[int, int, int, int]:
    x0, y0 = (QUIET + mx) * px, (QUIET + my) * px
    inset = POINT_INSET * px
    return (int(x0 + inset), int(y0 + inset), int(x0 + px - inset), int(y0 + px - inset))


def _cell_box(px: int, mx: int, my: int) -> tuple[int, int, int, int]:
    x0, y0 = (QUIET + mx) * px, (QUIET + my) * px
    return x0, y0, x0 + px, y0 + px


def _merged_mean(grid: Grid, stamp: Grid, ox: int, oy: int, box) -> float:
    """What a module's sampling point would read if this stamp were laid down."""
    x0, y0, x1, y1 = box
    total = count = 0
    for y in range(max(0, y0), min(grid.height, y1)):
        base = y * grid.width
        sy = y - oy
        srow = sy * stamp.width if 0 <= sy < stamp.height else None
        for x in range(max(0, x0), min(grid.width, x1)):
            value = grid.data[base + x]
            sx = x - ox
            if srow is not None and 0 <= sx < stamp.width:
                other = stamp.data[srow + sx]
                if other > value:
                    value = other
            total += value
            count += 1
    return total / (count * 255) if count else 0.0


def _draw_posed(symbol: Symbol, style: Style, rng: random.Random,
                grid: Grid, px: int, lay_down) -> tuple[int, int]:
    """Fit jointed ants to the dark ground, largest first, all the way down.

    Every mark in a posed style is a fitted ant, not just the big ones. The
    ladder walks down from the largest size the ground will take to about two
    modules, and each ant is posed against what is still uncovered, so the
    drawing is a sequence of decisions: the first ant takes the best piece of
    ground on the symbol and the last takes what is left.

    The fitter and the raster share one account of the page. Every ant that is
    laid down is measured back off the grid it was drawn on before the next one
    is fitted, because a fitter working from its own estimate will happily
    spend the light budget on ink the raster never delivers — which is exactly
    what an earlier version of this did, at a cost of a third of the correction
    budget for nothing.

    The size the ladder starts at is not a free choice. Articulating the ant
    without stretching it means a large ant has a large *gaster*, and a gaster
    has to sit in dark ground: at six modules long it is about two modules
    across, and only about a third of a QR symbol's dark modules lie in a
    two-by-two block. Past six modules nothing fits anywhere at any tolerance,
    which is a fact about the pattern rather than a limit of the search.
    """
    anatomy = antpose.load()
    largest, smallest = style.posed
    ground = antpose.Field(symbol.matrix, _protected(symbol),
                           light_cap=style.light_cap, dark_target=DARK_FLOOR)
    for y in range(symbol.size):
        for x in range(symbol.size):
            ground.covered[(x, y)] = grid.mean(*_cell_box(px, x, y))

    placed = refused = 0

    def settle(pose) -> bool:
        nonlocal placed, refused
        local = antpose.Pose(0.0, 0.0, pose.size, pose.angle,
                             pose.gaster, pose.head, pose.joints)
        mark = Mark(pose.x, pose.y, pose.size, pose.angle,
                    tuple(antpose.module_shapes(anatomy, local)), pose)
        touched = antpose._weights(antpose.module_shapes(anatomy, pose))
        if not lay_down(mark):
            refused += 1
            # The raster refused it, so nothing about the page changed; mark the
            # ground taken anyway or the same ant is fitted here again forever.
            for key in touched:
                if ground.dark(*key):
                    ground.occupied.add(key)
            return False
        placed += 1
        for key in touched:
            if ground.inside(*key):
                ground.covered[key] = grid.mean(*_cell_box(px, *key))
        return True

    steps = 6
    for step in range(steps):
        size = largest * (smallest / largest) ** (step / (steps - 1))
        if size >= antpose.LIMB_SOLVE_FLOOR:
            # Big ants: search, because ground one can sit on is scarce.
            misses = 0
            while misses < 30:
                found = antpose.fit(ground, anatomy, size, rng, attempts=16,
                                    forbid_overlap=not style.overlap)
                if found is None:
                    break
                pose, value = found
                if value <= 0.12 * size:
                    misses += 1
                    continue
                misses = 0
                settle(pose)
        else:
            # Small ants: sweep, because nearly every module left wants one.
            for x, y in sorted(antpose._uncovered(ground, not style.overlap)):
                if ground.covered.get((x, y), 0.0) >= DARK_FLOOR:
                    continue
                # The starting angle is jittered per module. Without it every
                # tie goes to the same heading and the sweep lays out combs of
                # identical ants down a filament, which is the one thing that
                # makes a drawn swarm look machine-made.
                start = rng.uniform(0, 360)
                best, best_score = None, 0.0
                for turn in range(8):
                    pose, value = antpose.pose_at(
                        ground, anatomy, x + 0.5 + rng.uniform(-0.12, 0.12),
                        y + 0.5 + rng.uniform(-0.12, 0.12), size, start + turn * 45,
                        not style.overlap, solve_limbs=size >= antpose.LIMB_SOLVE_FLOOR)
                    if value > best_score:
                        best, best_score = pose, value
                if best is not None:
                    settle(best)
    return placed, refused


def _abdomen_marks(symbol: Symbol, style: Style, rng: random.Random,
                   grid: Grid, px: int, lay_down) -> tuple[int, int]:
    """Draw the symbol at the scale where one module square *is* one abdomen.

    The other styles size an ant against the whole symbol and let whatever part
    of it lands on a module do the darkening. This one sizes it against a
    single module: the gaster is set to the module's width and pinned at the
    module's centre, so every mark reads as an abdomen sitting on a square,
    with the thorax, head and legs swinging off it onto the ground next door.

    An ant whose gaster is one module across is about three modules long, so
    two thirds of it hangs outside the square it is drawn for. Where that
    overhang lands is the whole problem, and it is what the orientation search
    below spends its time on.
    """
    anatomy = antpose.load()
    size = antpose.size_for_gaster(anatomy, style.gaster)
    ground = antpose.Field(symbol.matrix, _protected(symbol),
                           light_cap=style.light_cap, dark_target=DARK_FLOOR)
    for y in range(symbol.size):
        for x in range(symbol.size):
            ground.covered[(x, y)] = grid.mean(*_cell_box(px, x, y))

    placed = refused = 0
    wanted = [(x, y) for x, y in _dark_modules(symbol.matrix)
              if (x, y) not in ground.protected]
    for x, y in wanted:
        if not style.every and ground.covered.get((x, y), 0.0) >= DARK_FLOOR:
            continue
        start = rng.uniform(0, 360)
        best, best_score = None, 0.0 if not style.every else float('-inf')
        for turn in range(12):
            pose, value = antpose.pose_at(
                ground, anatomy, x + 0.5, y + 0.5, size, start + turn * 30,
                not style.overlap, solve_limbs=True, anchor='gaster')
            if value > best_score:
                best, best_score = pose, value
        if best is None:
            continue
        local = antpose.Pose(0.0, 0.0, best.size, best.angle,
                             best.gaster, best.head, best.joints, 'gaster')
        mark = Mark(best.x, best.y, best.size, best.angle,
                    tuple(antpose.module_shapes(anatomy, local)), best)
        touched = antpose._weights(antpose.module_shapes(anatomy, best))
        if not lay_down(mark):
            refused += 1
            for key in touched:
                if ground.dark(*key):
                    ground.occupied.add(key)
            continue
        placed += 1
        for key in touched:
            if ground.inside(*key):
                ground.covered[key] = grid.mean(*_cell_box(px, *key))
    return placed, refused


def _protected(symbol: Symbol) -> set:
    """Module cells no ant may reach: the patterns that carry no correction.

    Finders, separators, timing, alignment and the format and version words are
    read before any error correction exists to protect them. One of them read
    wrong can cost the whole symbol, so they are drawn as squares and fenced
    off in every style. The trade this tool offers is inside the data region;
    it was never available here.
    """
    fenced = {(x, y) for y, row in enumerate(symbol.function)
              for x, flag in enumerate(row) if flag}
    # And a clear margin around each finder on top of that. A scanner has to
    # *find* the symbol before it decodes anything, and it does that by scanning
    # for the finder's 1:1:3:1:1 run of dark and light. Ink pressed up against
    # the separator breaks that run even when every module inside it is right:
    # measured against the system scanner, off-lattice drawings that decoded
    # perfectly were simply not found until this margin was given to them.
    size = symbol.size
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4 - FENCE_MARGIN, 5 + FENCE_MARGIN):
            for dx in range(-4 - FENCE_MARGIN, 5 + FENCE_MARGIN):
                if 0 <= cx + dx < size and 0 <= cy + dy < size:
                    fenced.add((cx + dx, cy + dy))
    return fenced


def compose(symbol: Symbol, px: int = DEFAULT_PX,
            photos: list[Grid] | None = None) -> Drawing:
    """Draw the symbol, fitting each ant against the raster as it goes."""
    shapes, unit = _ant_geometry()
    style = symbol.style
    grid = Grid(symbol.span * px, symbol.span * px)
    offset = QUIET * px
    protected = _protected(symbol)
    rng = random.Random(symbol.seed)

    solid = _dark_modules(symbol.matrix) if style.solid else \
        [(x, y) for x, y in sorted(protected) if symbol.matrix[y][x] == qr_core.DARK]
    for x, y in solid:
        grid.fill_rect(offset + x * px, offset + y * px,
                       offset + (x + 1) * px, offset + (y + 1) * px)

    def stamp_for(mark: Mark):
        if mark.shapes:
            return rasterize.stamp(list(mark.shapes), px, 0.0)
        if photos:
            return _photo_stamp(photos[rng.randrange(len(photos))], mark.size * px, mark.angle)
        return _ant_stamp(shapes, unit, mark.size * px, mark.angle)

    def try_place(mark: Mark, drawing: Drawing, allow_shrink: bool = True) -> bool:
        """Lay an ant down unless it would move a module that must not move."""
        for scale in (1.0, 0.75, 0.55) if allow_shrink else (1.0,):
            if mark.shapes and scale != 1.0:
                continue          # a fitted ant is not rescaled; it was fitted at this size
            candidate = Mark(mark.x, mark.y, mark.size * scale, mark.angle,
                             mark.shapes, mark.pose)
            stamped, sx, sy = stamp_for(candidate)
            ox = int(round(offset + candidate.x * px + sx))
            oy = int(round(offset + candidate.y * px + sy))
            mx0 = max(0, (ox - offset) // px - 1)
            my0 = max(0, (oy - offset) // px - 1)
            mx1 = min(symbol.size, (ox + stamped.width - offset) // px + 2)
            my1 = min(symbol.size, (oy + stamped.height - offset) // px + 2)
            blocked = False
            for my in range(my0, my1):
                for mx in range(mx0, mx1):
                    if symbol.matrix[my][mx] == qr_core.DARK:
                        continue          # ink can only help a module that is dark
                    cap = FENCE_CAP if (mx, my) in protected else style.light_cap
                    box = _cell_box(px, mx, my)
                    if grid.mean(*box) <= cap \
                            and _merged_mean(grid, stamped, ox, oy, box) > cap:
                        blocked = True    # the binariser reads the whole cell
                        break
                    # And the sampler reads its middle. A cell can hold a leg
                    # straight through its centre and still average under the
                    # cap, which is exactly how a fitted ant loses a module
                    # while appearing to respect its budget.
                    middle = _centre_box(px, mx, my)
                    if grid.mean(*middle) < THRESHOLD \
                            and _merged_mean(grid, stamped, ox, oy, middle) >= THRESHOLD:
                        blocked = True
                        break
                if blocked:
                    break
            if blocked:
                continue
            grid.max_into(stamped, ox, oy)
            drawing.marks.append(candidate)
            if scale != 1.0:
                drawing.shrunk += 1
            return True
        return False

    drawing = Drawing(grid, [], px)
    if style.gaster:
        placed, refused = _abdomen_marks(
            symbol, style, rng, grid, px,
            lambda mark: try_place(mark, drawing, allow_shrink=False))
        drawing.posed = placed
        drawing.offered = placed + refused
        drawing.rejected = refused
    elif style.posed:
        placed, refused = _draw_posed(
            symbol, style, rng, grid, px,
            lambda mark: try_place(mark, drawing, allow_shrink=False))
        drawing.posed = placed
        drawing.offered = placed + refused
        drawing.rejected = refused
    else:
        offered = style.place(symbol.matrix, rng)
        drawing.offered = len(offered)
        for mark in offered:
            if not try_place(mark, drawing):
                drawing.rejected += 1

    if style.repair:
        # A dark module the drawing left too pale is a module it lost. Put an
        # ant on it, centred and small enough to stay inside its own cell, and
        # come back for it: the way to darken a cell without spreading into the
        # light field is another ant across the first, not a wider one.
        for _ in range(6):
            missing = [(x, y) for x, y in _dark_modules(symbol.matrix)
                       if (x, y) not in protected
                       and (grid.mean(*_centre_box(px, x, y)) < THRESHOLD
                            or grid.mean(*_cell_box(px, x, y)) < DARK_FLOOR)]
            if not missing:
                break
            turn = rng.uniform(0, 360)
            for x, y in missing:
                # Angles are tried rather than guessed. A repair ant has one
                # module to darken and very little light budget around it, so
                # which way it lies decides whether it fits at all; taking the
                # first random angle throws away most of the chances.
                done = False
                for size in (1.5, 1.25, 1.05, 0.85):
                    for step in range(6):
                        patch = Mark(x + 0.5, y + 0.5, size, turn + step * 60)
                        if try_place(patch, drawing, allow_shrink=False):
                            drawing.repairs += 1
                            done = True
                            break
                    if done:
                        break
    return drawing


def rasterise(symbol: Symbol, px: int = DEFAULT_PX,
              photos: list[Grid] | None = None) -> Grid:
    return compose(symbol, px, photos).grid


def to_svg(symbol: Symbol, drawing: Drawing, module: float = 8.0) -> str:
    """The same drawing as vector art. One `<use>` per ant, per the density note."""
    shapes = ant_shapes()
    cx, cy, long_axis = ant_frame(shapes)
    side = symbol.span * module
    body = json.loads(LIBRARY.read_text())['assets']['ant']
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:g} {side:g}" '
             f'width="{side:g}" height="{side:g}" role="img">',
             f'<title>QR code, version {symbol.version}-{symbol.ecc}, drawn in ants</title>',
             f'<desc>Style {symbol.style.name}. {symbol.style.summary} '
             f'Apparatus, not page art: this lattice is not the non-quantitative '
             f'marginal ant layer and carries no count.</desc>',
             f'<rect width="100%" height="100%" fill="{PAPER}"/>',
             f'<defs><g id="ant" transform="translate({-cx:g} {-cy:g})">{body}</g></defs>',
             f'<g color="{INK}" fill="{INK}">']
    offset = QUIET * module
    protected = _protected(symbol)
    solid = _dark_modules(symbol.matrix) if symbol.style.solid else \
        [(x, y) for x, y in sorted(protected) if symbol.matrix[y][x] == qr_core.DARK]
    for x, y in solid:
        parts.append(f'<rect x="{offset + x * module:g}" y="{offset + y * module:g}" '
                     f'width="{module:g}" height="{module:g}"/>')
    anatomy = antpose.load() if any(mark.pose for mark in drawing.marks) else None
    for mark in drawing.marks:
        if mark.pose is not None:
            parts.append(antpose.svg_group(anatomy, mark.pose, module, offset))
            continue
        scale = mark.size * module / long_axis
        parts.append(f'<use href="#ant" transform="translate('
                     f'{offset + mark.x * module:g} {offset + mark.y * module:g}) '
                     f'rotate({mark.angle:.1f}) scale({scale:.4f})"/>')
    parts.append('</g></svg>')
    return ''.join(parts)


# --- measurement ----------------------------------------------------------

@dataclass
class Measurement:
    px: int
    blur: int
    module_errors: int
    function_errors: int
    dark_errors: int
    light_errors: int
    dark_cell: float
    light_cell: float
    worst_light: float
    faint_dark: int
    ink: float
    finders: int
    binary_errors: int
    decoded: bool
    reason: str
    corrected: int
    budget: int
    worst_block: float

    @property
    def spent(self) -> float:
        return self.corrected / self.budget if self.budget else 0.0

    @property
    def contrast(self) -> float:
        return self.dark_cell - self.light_cell


def _ratio_ok(run: list[int]) -> bool:
    """Is this a 1:1:3:1:1 run of dark, light, dark, light, dark?"""
    if len(run) != 5 or min(run) <= 0:
        return False
    unit = sum(run) / 7
    wanted = (1, 1, 3, 1, 1)
    return all(abs(length - want * unit) <= unit * 0.6
               for length, want in zip(run, wanted))


def _runs_through(binary: Grid, px: int, y: int, x0: int, x1: int,
                  vertical: bool = False) -> list[tuple[int, int]]:
    """Run-lengths of dark and light along one scan line, as (dark, length)."""
    runs: list[tuple[int, int]] = []
    current, length = None, 0
    for i in range(x0, x1):
        pixel = binary.get(y, i) if vertical else binary.get(i, y)
        dark = pixel >= 128        # these grids carry ink, not light
        if dark == current:
            length += 1
        else:
            if current is not None:
                runs.append((current, length))
            current, length = dark, 1
    if current is not None:
        runs.append((current, length))
    # Absorb specks. A run a fraction of a module long is sensor noise or a
    # stray leg, and a real locator's run counter is not derailed by one; a
    # model that is would report a symbol lost over a single pixel.
    speck = max(1, px // 4)
    merged: list[tuple[int, int]] = []
    for dark, length in runs:
        if merged and length < speck and merged[-1][0] != dark:
            merged[-1] = (merged[-1][0], merged[-1][1] + length)
        elif merged and merged[-1][0] == dark:
            merged[-1] = (dark, merged[-1][1] + length)
        else:
            merged.append((dark, length))
    return merged


def locatable(symbol: Symbol, binary: Grid, px: int) -> int:
    """How many of the three finders a locator could still pick out.

    This is the step that fails first and the one a decoder that already knows
    where the symbol is will never notice. Each finder is scanned across and
    down through its centre; it counts only if the 1:1:3:1:1 run survives in
    both directions.
    """
    found = 0
    for cx, cy in ((3, 3), (symbol.size - 4, 3), (3, symbol.size - 4)):
        both = True
        for vertical in (False, True):
            centre = int((QUIET + (cy if not vertical else cx) + 0.5) * px)
            along = int((QUIET + (cx if not vertical else cy) + 0.5) * px)
            span = 6 * px
            runs = _runs_through(binary, px, centre,
                                 max(0, along - span), along + span, vertical)
            windows = [runs[i:i + 5] for i in range(len(runs) - 4)]
            if not any(window[0][0] and _ratio_ok([length for _, length in window])
                       for window in windows):
                both = False
                break
        found += both
    return found


@dataclass
class Reading:
    """What a scanner would take off the page, at cell and at point."""
    modules: list
    dark_cell: float
    light_cell: float
    worst_light: float
    faint_dark: int
    ink: float


def sample(symbol: Symbol, grid: Grid, px: int) -> Reading:
    """Read the grid twice over: the sampling point, and the whole cell.

    The point decides what the module says. The cell decides whether a real
    scanner's local binariser will agree, so both are carried out of here.
    """
    modules, darks, lights = [], [], []
    faint = 0
    for y in range(symbol.size):
        row = []
        for x in range(symbol.size):
            point = grid.mean(*_centre_box(px, x, y))
            cell = grid.mean(*_cell_box(px, x, y))
            row.append(qr_core.DARK if point >= THRESHOLD else qr_core.LIGHT)
            if symbol.matrix[y][x] == qr_core.DARK:
                darks.append(cell)
                faint += cell < DARK_FLOOR
            else:
                lights.append(cell)
        modules.append(row)
    return Reading(modules,
                   sum(darks) / max(1, len(darks)),
                   sum(lights) / max(1, len(lights)),
                   max(lights, default=0.0), faint,
                   grid.mean(0, 0, grid.width, grid.height))


def measure(symbol: Symbol, drawing: Drawing, blur: int = 0) -> Measurement:
    """Price one drawing three ways over.

    Against the ideal coverage, to count the modules the drawing moved; through
    a local binariser, to count the ones a real camera would move; and through
    the finder scan, to say whether a scanner could have located the symbol at
    all. A drawing can pass the first and fail the third, and that failure is
    the one that matters on a cover.
    """
    px = drawing.px
    grid = drawing.grid.blur(blur) if blur else drawing.grid
    reading = sample(symbol, grid, px)
    # The block window spans five blocks, so a block of one module gives the
    # binariser five modules of context - enough to always contain both inks.
    binary = grid.binarize(max(4, px))
    binary_reading = sample(symbol, binary, px)
    finders = locatable(symbol, binary, px)
    binary_errors = sum(1 for y in range(symbol.size) for x in range(symbol.size)
                        if binary_reading.modules[y][x] != symbol.matrix[y][x])
    read = reading.modules
    errors = function_errors = dark_errors = light_errors = 0
    for y in range(symbol.size):
        for x in range(symbol.size):
            if read[y][x] == symbol.matrix[y][x]:
                continue
            errors += 1
            if symbol.function[y][x]:
                function_errors += 1
            if symbol.matrix[y][x] == qr_core.DARK:
                dark_errors += 1
            else:
                light_errors += 1
    result = qr_core.decode(read, symbol.version)
    binary_result = qr_core.decode(binary_reading.modules, symbol.version)
    ok = result.ok and result.payload == symbol.payload
    reason = 'decoded'
    if not result.ok:
        reason = result.reason
    elif not ok:
        reason = 'decoded to the wrong payload'
    # Everything above assumed the symbol had already been found. These two do
    # not, and a drawing has to survive all of them to be worth printing.
    if ok and finders < 3:
        ok, reason = False, f'only {finders} of 3 finders are still locatable'
    elif ok and function_errors:
        ok = False
        reason = f'{function_errors} functional modules misread'
    elif ok and not (binary_result.ok and binary_result.payload == symbol.payload):
        ok, reason = False, f'fails through a local binariser: {binary_result.reason}'
    return Measurement(px, blur, errors, function_errors, dark_errors, light_errors,
                       reading.dark_cell, reading.light_cell, reading.worst_light,
                       reading.faint_dark, reading.ink, finders, binary_errors,
                       ok, reason, result.corrected, result.budget, result.worst_spent)


@dataclass
class Option:
    style: str
    ecc: str
    version: int
    modules: int
    drawing: Drawing
    crisp: Measurement
    blurred: Measurement
    files: tuple = ()


def evaluate(text: str, styles: list[str], eccs: list[str], px: int,
             photos: list[Grid] | None = None) -> list[Option]:
    payload = text.encode()
    options = []
    for ecc in eccs:
        version = qr_core.smallest_version(payload, ecc)
        for name in styles:
            symbol = build(text, ecc, name, version)
            drawing = compose(symbol, px, photos)
            options.append(Option(name, ecc, version, symbol.size, drawing,
                                  measure(symbol, drawing),
                                  measure(symbol, drawing, max(1, px // 6))))
    return options


# --- reporting ------------------------------------------------------------

def print_report(text: str, options: list[Option]) -> None:
    payload = text.encode()
    print(f'payload {len(payload)} bytes, byte mode\n')
    header = (f'{"style":<9}{"ecc":>4}{"ver":>4}{"size":>8}{"ants":>7}{"fit":>5}'
              f'{"mean":>6}{"max":>5}'
              f'{"bad":>5}{"cam":>5}{"find":>6}{"spent":>7}{"worst":>6}'
              f'{"light":>7}{"peak":>6}{"ink":>6}'
              f'{"reads":>7}{"blur":>6}')
    print(header)
    print('-' * len(header))
    for option in options:
        crisp, drawing = option.crisp, option.drawing
        print(f'{option.style:<9}{option.ecc:>4}{option.version:>4}'
              f'{f"{option.modules}sq":>8}{len(drawing.marks):>7}'
              f'{drawing.fitted:>4.0%}'
              f'{drawing.mean_size:>6.1f}{drawing.biggest:>5.1f}'
              f'{crisp.module_errors:>5}{crisp.binary_errors:>5}'
              f'{f"{crisp.finders}/3":>6}'
              f'{crisp.spent:>6.0%}{crisp.worst_block:>6.0%}'
              f'{crisp.light_cell:>7.2f}{crisp.worst_light:>6.2f}'
              f'{crisp.ink:>5.0%}'
              f'{("yes" if crisp.decoded else "NO"):>7}'
              f'{("yes" if option.blurred.decoded else "NO"):>6}')
    print('\nants: ants drawn.  fit: share offered that found room.  '
          'mean / max: ant length, in modules.')
    print('bad: modules read wrong off the ideal coverage.  cam: the same through a '
          'local binariser.')
    print('find: finder patterns a locator could still pick out; under 3 and nothing '
          'else matters.')
    print('spent: share of the correction budget used; worst: the worst single block.')
    print('dark / light: mean ink in a dark and in a light module\'s whole cell.  '
          'peak: the inkiest light cell.')
    print('reads: passes locating, binarising and decoding.  blur: still does out of '
          'focus.')


def load_photos(folder: Path) -> list[Grid]:
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() == '.png')
    if not files:
        raise ValueError(f'no PNGs in {folder}')
    return [rasterize.read_png(path) for path in files]


def write_options(text: str, out: Path, styles: list[str], eccs: list[str],
                  px: int, module: float, photos: list[Grid] | None = None) -> list[Option]:
    out.mkdir(parents=True, exist_ok=True)
    payload = text.encode()
    options = []
    for ecc in eccs:
        version = qr_core.smallest_version(payload, ecc)
        for name in styles:
            symbol = build(text, ecc, name, version)
            drawing = compose(symbol, px, photos)
            stem = f'{name}-{ecc}'
            (out / f'{stem}.svg').write_text(to_svg(symbol, drawing, module))
            rasterize.write_png(out / f'{stem}.png', drawing.grid)
            options.append(Option(name, ecc, version, symbol.size, drawing,
                                  measure(symbol, drawing),
                                  measure(symbol, drawing, max(1, px // 6)),
                                  (f'{stem}.svg', f'{stem}.png')))
    (out / 'metrics.tsv').write_text(_tsv(options))
    return options


def _tsv(options: list[Option]) -> str:
    columns = ('style', 'ecc', 'version', 'modules', 'ants', 'offered', 'rejected',
               'shrunk', 'repairs', 'posed', 'mean_size', 'biggest',
               'module_errors', 'function_errors',
               'dark_errors', 'light_errors', 'budget', 'corrected', 'spent',
               'worst_block', 'binary_errors', 'finders', 'dark_cell', 'light_cell',
               'worst_light', 'faint_dark', 'ink', 'contrast', 'reads',
               'reads_blurred', 'reason')
    lines = ['\t'.join(columns)]
    for option in options:
        crisp, drawing = option.crisp, option.drawing
        lines.append('\t'.join(str(v) for v in (
            option.style, option.ecc, option.version, option.modules,
            len(drawing.marks), drawing.offered, drawing.rejected, drawing.shrunk,
            drawing.repairs, drawing.posed, f'{drawing.mean_size:.2f}',
            f'{drawing.biggest:.2f}', crisp.module_errors,
            crisp.function_errors, crisp.dark_errors, crisp.light_errors,
            crisp.budget, crisp.corrected, f'{crisp.spent:.4f}',
            f'{crisp.worst_block:.4f}', crisp.binary_errors, crisp.finders,
            f'{crisp.dark_cell:.4f}',
            f'{crisp.light_cell:.4f}', f'{crisp.worst_light:.4f}', crisp.faint_dark,
            f'{crisp.ink:.4f}', f'{crisp.contrast:.4f}',
            'yes' if crisp.decoded else 'no',
            'yes' if option.blurred.decoded else 'no', crisp.reason)))
    return '\n'.join(lines) + '\n'


# --- self check -----------------------------------------------------------

def _self_check() -> list[str]:
    findings = []
    text = '256t.org/00000056' + 'Qw3' * 28 + 'Zx'
    payload = text.encode()
    if len(payload) != 103:
        findings.append(f'the check fixture is {len(payload)} bytes, expected 103')

    shapes = ant_shapes()
    if len(shapes) < 10:
        findings.append(f'the ant asset parsed to {len(shapes)} shapes, expected three '
                        'body ellipses and eight limbs')
    _, _, long_axis = ant_frame(shapes)
    if not 60 < long_axis < 100:
        findings.append(f'the ant long axis is {long_axis:.1f} units, outside its 100-unit box')

    symbol = build(text, 'H', 'plain')
    if symbol.version != 10:
        findings.append(f'103 bytes at ECC H chose version {symbol.version}, expected 10')
    control = measure(symbol, compose(symbol, 8))
    if control.module_errors:
        findings.append(f'plain squares misread {control.module_errors} modules')
    if not control.decoded:
        findings.append(f'plain squares did not decode: {control.reason}')
    if control.corrected:
        findings.append(f'plain squares spent {control.corrected} correction codewords')

    # Fitting a jointed ant is thousands of times the work of stamping a
    # library one, and a style that pins an abdomen on every module fits one
    # per module, so the styles that do either are checked on a fourteen-byte
    # payload in a version 1 symbol rather than on the 103-byte tag. Every
    # invariant below is a property of the drawing rather than of the payload,
    # and a check nobody will wait for is a check that gets removed.
    brief = '256t.org/Qw3Zx'
    cache: dict = {}

    def trial(name: str) -> tuple:
        if name not in cache:
            style = STYLES[name]
            fitted = style.posed or style.gaster
            load, ecc, px = (brief, 'L', 8) if fitted else (text, 'H', 8)
            run_symbol = build(load, ecc, name)
            drawing = compose(run_symbol, px)
            cache[name] = (run_symbol, drawing, measure(run_symbol, drawing))
        return cache[name]

    # Every style fences off the patterns that carry no error correction.
    for name in STYLES:
        _, _, run = trial(name)
        if run.function_errors:
            findings.append(f'{name} damaged {run.function_errors} functional modules, '
                            'which no style may touch')

    # A style offered no budget must cost the code nothing at all, and a style
    # offered a budget must stay inside the one it was given.
    for name, style in STYLES.items():
        run_symbol, drawing, run = trial(name)
        if style.gaster:
            long_axis, short = antpose.gaster_size(
                antpose.load(), antpose.size_for_gaster(antpose.load(), style.gaster))
            if abs(short - style.gaster) > 1e-6:
                findings.append(f'{name} asked for a {style.gaster:.2f} module abdomen '
                                f'and sized one {short:.2f} across')
            if not any(mark.pose is not None and mark.pose.anchor == 'gaster'
                       for mark in drawing.marks):
                findings.append(f'{name} drew no ant pinned by its abdomen')
        if style.posed:
            sizes = {round(mark.size, 3) for mark in drawing.marks}
            if len(sizes) < 2:
                findings.append(f'{name} drew every ant at one size, so it is not a ladder')
            if drawing.biggest > style.posed[0] + 1e-6:
                findings.append(f'{name} drew an ant {drawing.biggest:.2f} modules long, '
                                f'over its {style.posed[0]:.2f} limit')
            if not any(mark.pose is not None for mark in drawing.marks):
                findings.append(f'{name} is a posed style but drew no jointed ant')
        if not drawing.marks and name != 'plain':
            findings.append(f'style {name} drew no ants at all')
        if run.contrast <= 0:
            findings.append(f'{name} did not make dark modules darker than light ones')
        if run.finders < 3 and name != 'wild':
            findings.append(f'{name} left only {run.finders} of 3 finders locatable')
        if style.posed or style.gaster:
            # A fitted ant covers ground its own body has to reach, so a posed
            # style is not required to cost nothing - what it costs is the
            # measurement the tool exists to report. It is required to read.
            if not run.decoded:
                findings.append(f'posed style {name} did not decode: {run.reason}')
        elif style.light_cap <= 0.25:
            if run.module_errors:
                findings.append(f'free style {name} misread {run.module_errors} modules')
            if not run.decoded:
                findings.append(f'free style {name} did not decode: {run.reason}')
        if style.light_cap < 1.0 and run.worst_light > style.light_cap + 0.02:
            findings.append(f'{name} let a light cell reach {run.worst_light:.2f} ink, '
                            f'over its {style.light_cap:.2f} cap')

    # Determinism: the same payload, style and resolution give the same drawing.
    first = compose(build(text, 'Q', 'swarm'), 8)
    second = compose(build(text, 'Q', 'swarm'), 8)
    if [(m.x, m.y, m.size, m.angle) for m in first.marks] != \
       [(m.x, m.y, m.size, m.angle) for m in second.marks]:
        findings.append('ant placement is not deterministic for a fixed payload')

    # The SVG and the raster must agree about what was drawn.
    svg_symbol = build(text, 'Q', 'swarm')
    svg = to_svg(svg_symbol, first, 6)
    if svg.count('<use ') != len(first.marks):
        findings.append('the SVG emitted a different number of ants than were drawn')
    if not svg.startswith('<svg') or not svg.endswith('</svg>'):
        findings.append('the SVG is malformed')

    # The loose end of the range must be reported as costing something.
    loose_symbol = build(text, 'H', 'wild')
    loose = measure(loose_symbol, compose(loose_symbol, 8))
    if loose.module_errors == 0:
        findings.append('the wild style cost nothing, so the range spans no trade at all')

    # The photographic path must run on a real PNG and darken what it draws.
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        stamped, _, _ = rasterize.stamp(ant_shapes(), 0.6, 0.0)
        rasterize.write_png(Path(folder) / 'ant.png', stamped)
        try:
            photos = load_photos(Path(folder))
            photo_symbol = build(text, 'H', 'grid')
            run = measure(photo_symbol, compose(photo_symbol, 8, photos))
        except Exception as error:                     # noqa: BLE001 - reported, not raised
            findings.append(f'the photographic path failed: {error!r}')
        else:
            if run.contrast <= 0:
                findings.append('photographic ink did not make dark modules darker')
            if run.function_errors:
                findings.append('photographic ink damaged a functional pattern')
    return findings


# --- CLI ------------------------------------------------------------------

def _selection(given: str, allowed, what: str) -> list[str]:
    """Resolve a comma-separated choice, or 'all', against what exists."""
    if given == 'all':
        return list(allowed)
    chosen = [part.strip() for part in given.split(',') if part.strip()]
    unknown = [part for part in chosen if part not in allowed]
    if unknown or not chosen:
        raise SystemExit(f'unknown {what}: {", ".join(unknown) or "(none given)"}; '
                         f'choose from {", ".join(allowed)}, or all')
    return chosen


def _payload_from(args) -> str:
    if args.text is not None:
        return args.text
    return Path(args.text_file).read_text().strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)

    def payload_args(p):
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument('--text', help='the payload')
        group.add_argument('--text-file', help='a file holding the payload')
        p.add_argument('--ecc', default='H',
                       help="one or more of L, M, Q, H separated by commas, or 'all'")
        p.add_argument('--style', default='swarm',
                       help="one or more style names separated by commas, or 'all'; "
                            "`styles` lists them")
        p.add_argument('--px', type=int, default=DEFAULT_PX,
                       help='rendered pixels per module for measurement')
        p.add_argument('--photos', help='a directory of PNG ants to use as ink')

    styles = sub.add_parser('styles', help='list the drawing styles')

    rep = sub.add_parser('report', help='measure the data loss of each option')
    payload_args(rep)

    render = sub.add_parser('render', help='write one symbol')
    payload_args(render)
    render.add_argument('--out', required=True, help='.svg or .png')
    render.add_argument('--module', type=float, default=8.0, help='SVG units per module')

    options = sub.add_parser('options', help='write every option, with a metrics table')
    payload_args(options)
    options.add_argument('--out', required=True, help='output directory')
    options.add_argument('--module', type=float, default=8.0)

    sub.add_parser('check', help='verify the codec, the styles and the ant asset')
    args = parser.parse_args(argv)

    if args.command == 'styles':
        for name, style in STYLES.items():
            print(f'{name:<12} {style.summary}')
        return 0
    if args.command == 'check':
        findings = _self_check()
        for finding in findings:
            print(f'FAIL {finding}')
        print('qrant: 0 findings' if not findings else f'qrant: {len(findings)} findings')
        return 1 if findings else 0

    text = _payload_from(args)
    names = _selection(args.style, STYLES, 'style')
    eccs = _selection(args.ecc, qr_core.ECC_ORDER, 'error-correction level')
    photos = load_photos(Path(args.photos)) if args.photos else None

    if args.command == 'report':
        print_report(text, evaluate(text, names, eccs, args.px, photos))
        return 0
    if args.command == 'render':
        symbol = build(text, eccs[0], names[0])
        drawing = compose(symbol, args.px, photos)
        out = Path(args.out)
        if out.suffix == '.svg':
            out.write_text(to_svg(symbol, drawing, args.module))
        else:
            rasterize.write_png(out, drawing.grid)
        run = measure(symbol, drawing)
        print(f'{out}: version {symbol.version}-{symbol.ecc}, '
              f'{symbol.size}x{symbol.size}, {len(drawing.marks)} ants '
              f'({drawing.fitted:.0%} of those offered), {run.module_errors} modules misread, '
              f'{run.spent:.0%} of the correction budget spent, '
              f'{"decodes" if run.decoded else "DOES NOT DECODE: " + run.reason}')
        return 0

    options = write_options(text, Path(args.out), names, eccs, args.px, args.module, photos)
    print_report(text, options)
    print(f'\nwrote {len(options) * 2} files and metrics.tsv to {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
