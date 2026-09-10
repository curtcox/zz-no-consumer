#!/usr/bin/env python3
"""The edition's ant, jointed, and fitted to a shape it has to cover.

`qrant.py`'s scattered styles draw the dark half of a QR symbol out of the
*positions* of many small ants. This module is for the other approach: a few
large ants whose own silhouettes are the shape, posed one at a time to lie
along the dark ground they are covering.

The anatomy is read from `assets.ant` in `data/storyboard-assets.json` and is
never invented here: three body lobes on a chain, six two-jointed legs and two
antennae, with every segment length and stroke width exactly as the pages draw
them. A pose bends joints and nothing else, so every ant this module produces
is the same animal in a different attitude rather than a different animal.

Two consequences follow from that restriction and are worth stating before the
pictures are looked at:

  * **A large ant has proportionally thin legs.** At six modules long its legs
    are about a quarter of a module wide, so they cannot fill a module. The
    body lobes are the only parts thick enough to darken ground, which is why
    the fitting below scores bodies and merely keeps legs out of trouble.
  * **The body is a three-link chain.** The gaster and head pivot about the
    thorax, so the covering part of the ant can follow a bend in the ground it
    is covering. Without that pivot a large ant fits almost nothing, because
    only about a third of a QR symbol's dark modules lie in a two-by-two block.

    python3 scripts/antpose.py check
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

import rasterize

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'data' / 'storyboard-assets.json'

# Joint travel, in degrees either side of the pose the asset is drawn in.
GASTER_SWING = 38.0
HEAD_SWING = 32.0
COXA_SWING = 62.0
KNEE_SWING = 75.0
ANTENNA_SWING = 55.0


@dataclass(frozen=True)
class Limb:
    """One leg or antenna: where it joins the body, and how long its bones are."""
    attach: tuple
    lengths: tuple
    rest: tuple                       # absolute segment angles, radians
    on_head: bool


@dataclass(frozen=True)
class Anatomy:
    """The ant as measured from the tracked asset, in its own 100-unit box."""
    lobes: tuple                      # (cx, cy, rx, ry) gaster, thorax, head
    limbs: tuple
    stroke: float
    pivot_gaster: tuple               # where the gaster turns about the thorax
    pivot_head: tuple

    @property
    def long_axis(self) -> float:
        xs = [c[0] - c[2] for c in self.lobes] + [c[0] + c[2] for c in self.lobes]
        ys = [c[1] - c[3] for c in self.lobes] + [c[1] + c[3] for c in self.lobes]
        for limb in self.limbs:
            x, y = limb.attach
            for length, angle in zip(limb.lengths, limb.rest):
                x, y = x + length * math.cos(angle), y + length * math.sin(angle)
                xs.append(x)
                ys.append(y)
        return max(max(xs) - min(xs), max(ys) - min(ys))

    @property
    def centre(self) -> tuple:
        return self.lobes[1][0], self.lobes[1][1]


def load(path: Path | None = None) -> Anatomy:
    """Read the anatomy out of the tracked asset."""
    markup = json.loads((path or LIBRARY).read_text())['assets']['ant']
    stroke = float(re.search(r'stroke-width="([\d.]+)"', markup).group(1))
    lobes = tuple(tuple(float(v) for v in group) for group in re.findall(
        r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)" rx="([-\d.]+)" ry="([-\d.]+)"', markup))
    if len(lobes) != 3:
        raise ValueError(f'expected three body lobes, found {len(lobes)}')
    gaster, thorax, head = lobes

    limbs = []
    for path_data in re.findall(r'<path d="([^"]+)"', markup):
        for run in path_data.split('M')[1:]:
            points = [tuple(float(v) for v in pair.split())
                      for pair in run.replace('L', ' L ').split(' L ') if pair.strip()]
            lengths, rest = [], []
            for (x0, y0), (x1, y1) in zip(points, points[1:]):
                lengths.append(math.hypot(x1 - x0, y1 - y0))
                rest.append(math.atan2(y1 - y0, x1 - x0))
            limbs.append(Limb(points[0], tuple(lengths), tuple(rest),
                              on_head=points[0][0] > head[0] - head[2]))
    if not limbs:
        raise ValueError('the ant asset has no limbs')
    return Anatomy(lobes, tuple(limbs), stroke,
                   ((gaster[0] + thorax[0]) / 2, (gaster[1] + thorax[1]) / 2),
                   ((head[0] + thorax[0]) / 2, (head[1] + thorax[1]) / 2))


@dataclass
class Pose:
    """A placed, jointed ant. Position and size are in module units."""
    x: float
    y: float
    size: float                       # long axis, in modules
    angle: float                      # degrees
    gaster: float = 0.0               # joint travel from rest, degrees
    head: float = 0.0
    joints: tuple = ()                # per limb, one angle offset per segment


def _turn(point: tuple, about: tuple, radians_: float) -> tuple:
    cos, sin = math.cos(radians_), math.sin(radians_)
    dx, dy = point[0] - about[0], point[1] - about[1]
    return about[0] + dx * cos - dy * sin, about[1] + dx * sin + dy * cos


def local_shapes(anatomy: Anatomy, pose: Pose) -> list[tuple]:
    """The posed ant as raster primitives, still in anatomy units."""
    gaster, thorax, head = anatomy.lobes
    shapes = []
    turned_gaster = _turn((gaster[0], gaster[1]), anatomy.pivot_gaster,
                          math.radians(pose.gaster))
    turned_head = _turn((head[0], head[1]), anatomy.pivot_head, math.radians(pose.head))
    shapes.append(rasterize.ellipse(turned_gaster[0], turned_gaster[1], gaster[2], gaster[3]))
    shapes.append(rasterize.ellipse(thorax[0], thorax[1], thorax[2], thorax[3]))
    shapes.append(rasterize.ellipse(turned_head[0], turned_head[1], head[2], head[3]))
    for index, limb in enumerate(anatomy.limbs):
        offsets = pose.joints[index] if index < len(pose.joints) else (0.0,) * len(limb.lengths)
        attach = limb.attach
        if limb.on_head:
            attach = _turn(attach, anatomy.pivot_head, math.radians(pose.head))
        x, y = attach
        carried = math.radians(pose.head) if limb.on_head else 0.0
        for length, rest, offset in zip(limb.lengths, limb.rest, offsets):
            angle = rest + carried + math.radians(offset)
            nx, ny = x + length * math.cos(angle), y + length * math.sin(angle)
            shapes.append(rasterize.segment(x, y, nx, ny, anatomy.stroke))
            x, y = nx, ny
            carried = angle - rest        # the next bone hangs off this one
    return shapes


def module_shapes(anatomy: Anatomy, pose: Pose) -> list[tuple]:
    """The posed ant in module coordinates, ready to rasterise or measure."""
    scale = pose.size / anatomy.long_axis
    cx, cy = anatomy.centre
    turn = math.radians(pose.angle)
    cos, sin = math.cos(turn), math.sin(turn)

    def place(px: float, py: float) -> tuple:
        lx, ly = (px - cx) * scale, (py - cy) * scale
        return pose.x + lx * cos - ly * sin, pose.y + lx * sin + ly * cos

    out = []
    for shape in local_shapes(anatomy, pose):
        if shape[0] == 'ellipse':
            _, ex, ey, rx, ry = shape
            # Lobes are near-circular; the mean radius keeps them cheap to test
            # and the difference is under a tenth of a module at these sizes.
            mx, my = place(ex, ey)
            out.append(rasterize.ellipse(mx, my, rx * scale, ry * scale))
        else:
            _, x0, y0, x1, y1, half = shape
            ax, ay = place(x0, y0)
            bx, by = place(x1, y1)
            out.append(rasterize.segment(ax, ay, bx, by, half * 2 * scale))
    return out


# --- fitting --------------------------------------------------------------

def _weights(shapes: list[tuple], samples: int = 3) -> dict:
    """Roughly how much of each module cell these primitives ink.

    Point sampling rather than rasterising: the fitter evaluates thousands of
    candidate poses and only needs to rank them, while the drawing that is
    finally kept is rasterised properly by `rasterize.stamp`.
    """
    out: dict = {}
    for shape in shapes:
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            area = math.pi * rx * ry
            steps = max(3, int(math.ceil(max(rx, ry) * samples * 2)))
            points = []
            for i in range(steps):
                for j in range(steps):
                    u = (i + 0.5) / steps * 2 - 1
                    v = (j + 0.5) / steps * 2 - 1
                    if u * u + v * v <= 1.0:
                        points.append((cx + u * rx, cy + v * ry))
            if not points:
                continue
            share = area / len(points)
        else:
            _, x0, y0, x1, y1, half = shape
            length = math.hypot(x1 - x0, y1 - y0)
            steps = max(2, int(math.ceil(length * samples)))
            points = [(x0 + (x1 - x0) * (i + 0.5) / steps,
                       y0 + (y1 - y0) * (i + 0.5) / steps) for i in range(steps)]
            share = length * half * 2 / len(points)
        for px, py in points:
            key = (int(math.floor(px)), int(math.floor(py)))
            out[key] = out.get(key, 0.0) + share
    return out


@dataclass
class Field:
    """The ground a pose is fitted to, and what has already been drawn on it."""
    matrix: list
    protected: set
    light_cap: float
    dark_target: float = 0.75
    covered: dict = field(default_factory=dict)
    occupied: set = field(default_factory=set)

    def dark(self, x: int, y: int) -> bool:
        return (0 <= x < len(self.matrix) and 0 <= y < len(self.matrix)
                and self.matrix[y][x] == 1)

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < len(self.matrix) and 0 <= y < len(self.matrix)


def score(field_: Field, weights: dict, forbid_overlap: bool) -> float:
    """Rank a candidate pose. `-inf` means it may not be drawn at all."""
    gain = cost = 0.0
    for (x, y), weight in weights.items():
        if not field_.inside(x, y):
            return float('-inf')                      # never over the quiet zone
        already = field_.covered.get((x, y), 0.0)
        if (x, y) in field_.protected:
            if not field_.dark(x, y):
                return float('-inf')                  # the patterns stay untouched
            continue                                  # a dark one is solid already
        if field_.dark(x, y):
            if forbid_overlap and (x, y) in field_.occupied:
                return float('-inf')
            gain += min(weight, max(0.0, field_.dark_target - already))
        else:
            if already + weight > field_.light_cap:
                return float('-inf')
            cost += weight
    return gain - 3.0 * cost


def commit(field_: Field, weights: dict, claim: bool = True) -> None:
    for key, weight in weights.items():
        field_.covered[key] = field_.covered.get(key, 0.0) + weight
        if claim and field_.dark(*key):
            field_.occupied.add(key)


def _limb_shapes(anatomy: Anatomy, pose: Pose, index: int) -> list[tuple]:
    """Just one limb of a posed ant, in module coordinates."""
    everything = module_shapes(anatomy, pose)
    start = 3
    for i, limb in enumerate(anatomy.limbs):
        if i == index:
            return everything[start:start + len(limb.lengths)]
        start += len(limb.lengths)
    raise IndexError(index)


def pose_at(field_: Field, anatomy: Anatomy, x: float, y: float, size: float,
            angle: float, forbid_overlap: bool, steps: int = 5,
            solve_limbs: bool = True) -> tuple:
    """Fit every joint for a body placed here. Returns `(pose, score)`.

    Joints are solved one after another, and each is scored on the ink *it*
    moves rather than on the whole animal. The lobes hang off the thorax and
    the limbs hang off the lobes, so a later joint cannot undo an earlier one's
    coverage; solving them together would cost thousands of times more for a
    pose no reader could tell apart. The one thing this misses is a limb being
    credited for ground its own body already covers, which flatters a tucked
    leg slightly and never changes which ant gets placed.
    """
    def spread(swing: float) -> list:
        return [-swing + 2 * swing * i / (steps - 1) for i in range(steps)]

    rest = tuple((0.0,) * len(limb.lengths) for limb in anatomy.limbs)
    pose = Pose(x, y, size, angle, joints=rest)

    best, best_score = 0.0, float('-inf')
    for value in spread(GASTER_SWING):
        trial = Pose(x, y, size, angle, value, 0.0, rest)
        value_score = score(field_, _weights([module_shapes(anatomy, trial)[0]]),
                            forbid_overlap)
        if value_score > best_score:
            best, best_score = value, value_score
    pose.gaster = best

    best, best_score = 0.0, float('-inf')
    for value in spread(HEAD_SWING):
        trial = Pose(x, y, size, angle, pose.gaster, value, rest)
        value_score = score(field_, _weights([module_shapes(anatomy, trial)[2]]),
                            forbid_overlap)
        if value_score > best_score:
            best, best_score = value, value_score
    pose.head = best

    joints = list(rest)
    # Below about three modules a leg is a fraction of a pixel wide at any
    # sensible print size. Solving its joints costs most of the fitting time
    # and moves no ink a reader or a scanner could see, so small ants keep the
    # attitude the asset is drawn in.
    for index, limb in enumerate(anatomy.limbs if solve_limbs else ()):
        swing = ANTENNA_SWING if len(limb.lengths) == 1 else COXA_SWING
        best, best_score = joints[index], float('-inf')
        seconds = spread(KNEE_SWING) if len(limb.lengths) == 2 else (0.0,)
        for first in spread(swing):
            for second in seconds:
                setting = (first,) if len(limb.lengths) == 1 else (first, second)
                trial = list(joints)
                trial[index] = setting
                candidate = Pose(x, y, size, angle, pose.gaster, pose.head, tuple(trial))
                value = score(field_, _weights(_limb_shapes(anatomy, candidate, index)),
                              forbid_overlap)
                if value > best_score:
                    best, best_score = setting, value
        joints[index] = best
    pose.joints = tuple(joints)
    final = _weights(module_shapes(anatomy, pose))
    return pose, score(field_, final, forbid_overlap)


LIMB_SOLVE_FLOOR = 3.0


def _uncovered(field_: Field, forbid_overlap: bool) -> list:
    """Dark modules still wanting ink, and still free to take it."""
    return [(x, y) for y, row in enumerate(field_.matrix)
            for x, value in enumerate(row)
            if value == 1 and (x, y) not in field_.protected
            and field_.covered.get((x, y), 0.0) < field_.dark_target
            and not (forbid_overlap and (x, y) in field_.occupied)]


def fit(field_: Field, anatomy: Anatomy, size: float, rng: random.Random,
        attempts: int = 24, forbid_overlap: bool = True,
        directions: int = 12) -> tuple | None:
    """Search for the best-placed ant of this size on the ground that is left."""
    wanted = _uncovered(field_, forbid_overlap)
    if not wanted:
        return None
    best, best_score = None, 0.0
    for _ in range(attempts):
        cx, cy = wanted[rng.randrange(len(wanted))]
        angle = rng.randrange(directions) * 360 / directions
        pose, value = pose_at(field_, anatomy,
                              cx + 0.5 + rng.uniform(-0.3, 0.3),
                              cy + 0.5 + rng.uniform(-0.3, 0.3),
                              size, angle, forbid_overlap,
                              solve_limbs=size >= LIMB_SOLVE_FLOOR)
        if value > best_score:
            best, best_score = pose, value
    return (best, best_score) if best else None


def sweep(field_: Field, anatomy: Anatomy, size: float, rng: random.Random,
          forbid_overlap: bool = True, directions: int = 8):
    """Fit one ant per still-uncovered dark module, in a fixed order.

    Random search is right while ants are large and good ground is scarce; it
    is wrong once they are small, because then almost every remaining module
    wants an ant and sampling for one wastes the search on ground already
    taken. This walks what is left in order and puts an ant on each, which is
    what actually finishes a symbol.
    """
    placed = []
    for x, y in sorted(_uncovered(field_, forbid_overlap)):
        if field_.covered.get((x, y), 0.0) >= field_.dark_target:
            continue
        best, best_score = None, 0.0
        for step in range(directions):
            pose, value = pose_at(field_, anatomy, x + 0.5, y + 0.5, size,
                                  step * 360 / directions, forbid_overlap,
                                  solve_limbs=size >= LIMB_SOLVE_FLOOR)
            if value > best_score:
                best, best_score = pose, value
        if best is None:
            continue
        commit(field_, _weights(module_shapes(anatomy, best)), claim=not forbid_overlap)
        placed.append(best)
    return placed


def svg_group(anatomy: Anatomy, pose: Pose, module: float, offset: float) -> str:
    """One posed ant as SVG, in the same coordinates the raster uses."""
    parts = []
    for shape in module_shapes(anatomy, pose):
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            parts.append(f'<ellipse cx="{offset + cx * module:.2f}" '
                         f'cy="{offset + cy * module:.2f}" '
                         f'rx="{rx * module:.2f}" ry="{ry * module:.2f}"/>')
        else:
            _, x0, y0, x1, y1, half = shape
            parts.append(f'<line x1="{offset + x0 * module:.2f}" '
                         f'y1="{offset + y0 * module:.2f}" '
                         f'x2="{offset + x1 * module:.2f}" '
                         f'y2="{offset + y1 * module:.2f}" '
                         f'stroke-width="{half * 2 * module:.2f}"/>')
    return ('<g stroke="currentColor" stroke-linecap="round" fill="currentColor">'
            + ''.join(parts) + '</g>')


# --- self check -----------------------------------------------------------

def _self_check() -> list[str]:
    findings = []
    anatomy = load()
    if len(anatomy.limbs) != 8:
        findings.append(f'parsed {len(anatomy.limbs)} limbs, expected six legs and two antennae')
    if sum(1 for limb in anatomy.limbs if len(limb.lengths) == 2) != 6:
        findings.append('expected exactly six two-jointed legs')
    if sum(1 for limb in anatomy.limbs if limb.on_head) != 2:
        findings.append('expected exactly two limbs attached to the head')
    if not 60 < anatomy.long_axis < 100:
        findings.append(f'long axis is {anatomy.long_axis:.1f}, outside the 100-unit box')

    # Articulation may bend joints and must never change a bone.
    rest = Pose(0, 0, 10, 0)
    bent = Pose(0, 0, 10, 0, gaster=GASTER_SWING, head=-HEAD_SWING,
                joints=tuple((COXA_SWING, -KNEE_SWING)[:len(limb.lengths)]
                             for limb in anatomy.limbs))
    for name, pose in (('rest', rest), ('bent', bent)):
        shapes = module_shapes(anatomy, pose)
        if len(shapes) != 3 + sum(len(limb.lengths) for limb in anatomy.limbs):
            findings.append(f'the {name} pose produced {len(shapes)} primitives')
    rest_bones = [round(math.hypot(s[3] - s[1], s[4] - s[2]), 6)
                  for s in module_shapes(anatomy, rest) if s[0] == 'segment']
    bent_bones = [round(math.hypot(s[3] - s[1], s[4] - s[2]), 6)
                  for s in module_shapes(anatomy, bent) if s[0] == 'segment']
    if rest_bones != bent_bones:
        findings.append('bending a joint changed a bone length')
    rest_lobes = [(round(s[3], 6), round(s[4], 6))
                  for s in module_shapes(anatomy, rest) if s[0] == 'ellipse']
    bent_lobes = [(round(s[3], 6), round(s[4], 6))
                  for s in module_shapes(anatomy, bent) if s[0] == 'ellipse']
    if rest_lobes != bent_lobes:
        findings.append('bending a joint changed a body lobe')

    # Scaling is the only thing that changes size, and it changes it linearly.
    small = module_shapes(anatomy, Pose(0, 0, 5, 0))
    large = module_shapes(anatomy, Pose(0, 0, 10, 0))
    ratios = {round(b[5] / s[5], 4) for s, b in zip(small, large) if s[0] == 'segment'}
    if ratios != {2.0}:
        findings.append(f'doubling the size scaled strokes by {ratios}')

    # Rotating the whole ant must not change how much ground it covers.
    flat = sum(_weights(module_shapes(anatomy, Pose(20, 20, 8, 0))).values())
    tilted = sum(_weights(module_shapes(anatomy, Pose(20, 20, 8, 37))).values())
    if abs(flat - tilted) / flat > 0.05:
        findings.append(f'rotation changed the inked area from {flat:.2f} to {tilted:.2f}')

    # The fitter must prefer dark ground and must refuse to break a pattern.
    size = 25
    matrix = [[1 if 8 <= x <= 16 and 8 <= y <= 16 else 0 for x in range(size)]
              for y in range(size)]
    ground = Field(matrix, protected=set(), light_cap=0.25)
    found = fit(ground, anatomy, 6.0, random.Random(3), attempts=12)
    if found is None:
        findings.append('the fitter found no pose on a nine-by-nine dark square')
    else:
        pose, value = found
        if value <= 0:
            findings.append(f'the best pose on open dark ground scored {value:.2f}')
        weights = _weights(module_shapes(anatomy, pose))
        stray = sum(w for (x, y), w in weights.items() if not ground.dark(x, y))
        wanted = sum(w for (x, y), w in weights.items() if ground.dark(x, y))
        if stray > wanted:
            findings.append('the fitted ant put more ink on light ground than on dark')

    fenced = Field(matrix, protected={(x, y) for x in range(8, 17) for y in range(8, 17)
                                      if matrix[y][x] == 0}, light_cap=0.25)
    fenced.protected.add((12, 12))
    for _ in range(6):
        found = fit(fenced, anatomy, 6.0, random.Random(11), attempts=8)
        if found is None:
            break
        pose, _ = found
        weights = _weights(module_shapes(anatomy, pose))
        if any((x, y) in fenced.protected and not fenced.dark(x, y) for x, y in weights):
            findings.append('a fitted ant inked a protected light module')
            break
        commit(fenced, weights)

    # Determinism: the same ground and seed give the same ant.
    one = fit(Field(matrix, set(), 0.25), anatomy, 6.0, random.Random(5), attempts=8)
    two = fit(Field(matrix, set(), 0.25), anatomy, 6.0, random.Random(5), attempts=8)
    if (one is None) != (two is None) or (one and one[0] != two[0]):
        findings.append('fitting is not deterministic for a fixed seed')
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check', help='verify the anatomy, the joints and the fitter')
    sub.add_parser('report', help='describe the parsed anatomy')
    args = parser.parse_args(argv)

    if args.command == 'report':
        anatomy = load()
        print(f'long axis {anatomy.long_axis:.1f} units, stroke {anatomy.stroke:g}')
        for name, lobe in zip(('gaster', 'thorax', 'head'), anatomy.lobes):
            print(f'  {name:<8} centre ({lobe[0]:g}, {lobe[1]:g}) '
                  f'radii {lobe[2]:g} x {lobe[3]:g}')
        for index, limb in enumerate(anatomy.limbs):
            kind = 'antenna' if len(limb.lengths) == 1 else 'leg'
            bones = ', '.join(f'{length:.1f}' for length in limb.lengths)
            print(f'  {kind:<8} {index} at ({limb.attach[0]:g}, {limb.attach[1]:g}) '
                  f'bones {bones}' + ('  (on head)' if limb.on_head else ''))
        return 0

    findings = _self_check()
    for finding in findings:
        print(f'FAIL {finding}')
    print('antpose: 0 findings' if not findings else f'antpose: {len(findings)} findings')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
