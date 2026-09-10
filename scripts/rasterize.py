#!/usr/bin/env python3
"""Grayscale coverage grids, and PNG in and out, in the standard library alone.

`qrant.py` measures its own artwork rather than trusting it, and a measurement
has to happen on pixels: a scanner samples light, not geometry. This module is
the pixel layer. It rasterises the shape primitives the ant is made of into an
8-bit coverage grid, writes that grid as a PNG, and reads a PNG back so a
photographed ant can be used as ink the same way a drawn one is.

Coverage is anti-aliased by supersampling inside each pixel, because a hard
edge would make the module-fidelity metrics depend on where the grid happened
to fall rather than on the drawing.

    python3 scripts/rasterize.py check
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import zlib


class Grid:
    """An 8-bit coverage grid. 0 is bare paper, 255 is full ink."""

    __slots__ = ('width', 'height', 'data')

    def __init__(self, width: int, height: int, fill: int = 0):
        self.width = width
        self.height = height
        self.data = bytearray([fill]) * (width * height)

    def get(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y * self.width + x]
        return 0

    def max_into(self, other: 'Grid', ox: int, oy: int) -> None:
        """Stamp `other` at `(ox, oy)`, keeping the darker value. Ink is opaque.

        Clipped once per row and merged with `map(max, ...)`: this runs for
        every ant on every symbol, so a per-pixel Python loop here is the
        difference between a report that is worth running and one that is not.
        """
        x0 = max(0, -ox)
        x1 = min(other.width, self.width - ox)
        if x1 <= x0:
            return
        y0 = max(0, -oy)
        y1 = min(other.height, self.height - oy)
        data, source = self.data, other.data
        for y in range(y0, y1):
            start = (oy + y) * self.width + ox + x0
            stop = start + (x1 - x0)
            chunk = source[y * other.width + x0:y * other.width + x1]
            data[start:stop] = bytes(map(max, chunk, data[start:stop]))

    def fill_rect(self, x0: int, y0: int, x1: int, y1: int, value: int = 255) -> None:
        for y in range(max(0, y0), min(self.height, y1)):
            row = y * self.width
            for x in range(max(0, x0), min(self.width, x1)):
                self.data[row + x] = value

    def mean(self, x0: int, y0: int, x1: int, y1: int) -> float:
        """Mean coverage over a box, as a 0..1 fraction. Empty boxes read light."""
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        if x1 <= x0 or y1 <= y0:
            return 0.0
        total = 0
        for y in range(y0, y1):
            row = y * self.width
            total += sum(self.data[row + x0:row + x1])
        return total / ((x1 - x0) * (y1 - y0) * 255)

    def binarize(self, block: int = 8) -> 'Grid':
        """Binarise against a local average, the way a real scanner does.

        A decoder never sees coverage; it sees a camera frame it has to turn
        into black and white first, and it does that against the neighbourhood
        rather than against a fixed level. That is why ink which misses every
        module centre but fills the space around it still breaks a symbol: the
        neighbourhood it darkens is the one the threshold is drawn from.

        Block averages over `block` by `block` pixels, thresholded against the
        mean of the surrounding five-by-five block window, after ZXing's hybrid
        binariser. Returns a grid of 0 and 255.
        """
        bw = max(1, self.width // block)
        bh = max(1, self.height // block)
        averages = []
        for by in range(bh):
            row = []
            for bx in range(bw):
                x0, y0 = bx * block, by * block
                total = 0
                for y in range(y0, min(y0 + block, self.height)):
                    base = y * self.width
                    total += sum(self.data[base + x0:base + min(x0 + block, self.width)])
                row.append(total / (block * block * 255))
            averages.append(row)
        out = Grid(self.width, self.height)
        for by in range(bh):
            for bx in range(bw):
                window = [averages[y][x]
                          for y in range(max(0, by - 2), min(bh, by + 3))
                          for x in range(max(0, bx - 2), min(bw, bx + 3))]
                level = sum(window) / len(window)
                if max(window) - min(window) < 0.10:
                    # A uniform neighbourhood carries no edge to threshold
                    # against, so fall back to the midpoint. Deriving a level
                    # from the neighbourhood itself here erodes the inside of
                    # any area larger than the window - including a finder's
                    # three-module core, which is the one area that must
                    # survive intact.
                    level = 0.5
                cut = int(level * 255)
                x1 = min(bx * block + block, self.width)
                y1 = min(by * block + block, self.height)
                for y in range(by * block, y1):
                    base = y * self.width
                    for x in range(bx * block, x1):
                        out.data[base + x] = 255 if self.data[base + x] > cut else 0
        return out

    def blur(self, radius: int) -> 'Grid':
        """A separable box blur, standing in for an out-of-focus camera."""
        if radius < 1:
            return self
        span = radius * 2 + 1
        pass_one = Grid(self.width, self.height)
        for y in range(self.height):
            row = y * self.width
            line = self.data[row:row + self.width]
            running = sum(line[:radius + 1]) + line[0] * radius
            for x in range(self.width):
                pass_one.data[row + x] = running // span
                leaving = line[max(0, x - radius)]
                entering = line[min(self.width - 1, x + radius + 1)]
                running += entering - leaving
        out = Grid(self.width, self.height)
        for x in range(self.width):
            column = [pass_one.data[y * self.width + x] for y in range(self.height)]
            running = sum(column[:radius + 1]) + column[0] * radius
            for y in range(self.height):
                out.data[y * self.width + x] = running // span
                leaving = column[max(0, y - radius)]
                entering = column[min(self.height - 1, y + radius + 1)]
                running += entering - leaving
        return out


# --- shape primitives -----------------------------------------------------

def ellipse(cx: float, cy: float, rx: float, ry: float) -> tuple:
    return ('ellipse', cx, cy, rx, ry)


def segment(x0: float, y0: float, x1: float, y1: float, width: float) -> tuple:
    return ('segment', x0, y0, x1, y1, width / 2)


def _inside(shape: tuple, x: float, y: float) -> bool:
    kind = shape[0]
    if kind == 'ellipse':
        _, cx, cy, rx, ry = shape
        if rx <= 0 or ry <= 0:
            return False
        dx, dy = (x - cx) / rx, (y - cy) / ry
        return dx * dx + dy * dy <= 1.0
    _, x0, y0, x1, y1, half = shape
    vx, vy = x1 - x0, y1 - y0
    wx, wy = x - x0, y - y0
    length = vx * vx + vy * vy
    t = 0.0 if length == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / length))
    dx, dy = wx - t * vx, wy - t * vy
    return dx * dx + dy * dy <= half * half


def bounds(shapes: list[tuple]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for shape in shapes:
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            xs += [cx - rx, cx + rx]
            ys += [cy - ry, cy + ry]
        else:
            _, x0, y0, x1, y1, half = shape
            xs += [x0 - half, x1 + half]
            ys += [y0 - half, y1 + half]
    return min(xs), min(ys), max(xs), max(ys)


def stamp(shapes: list[tuple], scale: float, angle_degrees: float,
          samples: int = 3) -> tuple[Grid, float, float]:
    """Rasterise shapes rotated and scaled into their own tight grid.

    Each shape is drawn only inside its own rotated bounding box, and each
    pixel keeps a bitmask of which subsamples are already inked, so overlapping
    shapes neither double-count coverage nor re-test a settled subsample. An
    ant is eleven small shapes in a large box; testing every shape against
    every pixel is what made this the whole cost of a report.

    Returns `(grid, ox, oy)`: the offsets place the shapes' origin at the
    caller's anchor, so a caller stamps at `(round(x + ox), round(y + oy))`.
    """
    angle = math.radians(angle_degrees)
    cos, sin = math.cos(angle), math.sin(angle)
    local = []
    for shape in shapes:
        if shape[0] == 'ellipse':
            _, cx, cy, rx, ry = shape
            local.append(('ellipse', cx * scale, cy * scale, rx * scale, ry * scale))
        else:
            _, x0, y0, x1, y1, half = shape
            local.append(('segment', x0 * scale, y0 * scale,
                          x1 * scale, y1 * scale, half * scale))

    def rotated_box(box):
        minx, miny, maxx, maxy = box
        points = [(x * cos - y * sin, x * sin + y * cos)
                  for x, y in ((minx, miny), (maxx, miny), (minx, maxy), (maxx, maxy))]
        return (min(p[0] for p in points), min(p[1] for p in points),
                max(p[0] for p in points), max(p[1] for p in points))

    wx0, wy0, wx1, wy1 = rotated_box(bounds(local))
    rx0, ry0 = math.floor(wx0) - 1, math.floor(wy0) - 1
    width = int(math.ceil(wx1) + 1 - rx0)
    height = int(math.ceil(wy1) + 1 - ry0)
    grid = Grid(width, height)

    step = 1.0 / samples
    offsets = [(i + 0.5) * step for i in range(samples)]
    total = samples * samples
    masks = [0] * (width * height)
    for shape in local:
        sx0, sy0, sx1, sy1 = rotated_box(bounds([shape]))
        px0 = max(0, int(math.floor(sx0)) - rx0 - 1)
        px1 = min(width, int(math.ceil(sx1)) - rx0 + 1)
        py0 = max(0, int(math.floor(sy0)) - ry0 - 1)
        py1 = min(height, int(math.ceil(sy1)) - ry0 + 1)
        for py in range(py0, py1):
            row = py * width
            for px in range(px0, px1):
                index = row + px
                mask = masks[index]
                if mask == (1 << total) - 1:
                    continue
                bit = 1
                for dy in offsets:
                    wy = ry0 + py + dy
                    for dx in offsets:
                        if not mask & bit:
                            wxs = rx0 + px + dx
                            if _inside(shape, wxs * cos + wy * sin, -wxs * sin + wy * cos):
                                mask |= bit
                        bit <<= 1
                masks[index] = mask
    for index, mask in enumerate(masks):
        if mask:
            grid.data[index] = mask.bit_count() * 255 // total
    return grid, rx0, ry0


# --- PNG ------------------------------------------------------------------

def write_png(path, grid: Grid, invert: bool = True) -> None:
    """Write coverage as 8-bit grayscale. Inverted, ink is black on white."""
    raw = bytearray()
    for y in range(grid.height):
        raw.append(0)
        row = grid.data[y * grid.width:(y + 1) * grid.width]
        raw.extend(bytes(255 - v for v in row) if invert else row)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack('>I', len(payload)) + tag + payload
                + struct.pack('>I', zlib.crc32(tag + payload) & 0xFFFFFFFF))

    header = struct.pack('>IIBBBBB', grid.width, grid.height, 8, 0, 0, 0, 0)
    blob = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
    with open(path, 'wb') as handle:
        handle.write(blob)


def read_png(path) -> Grid:
    """Read a PNG as an ink-coverage grid: alpha if present, else darkness.

    Supports 8- and 16-bit grayscale, RGB, RGBA, gray+alpha and 8-bit palette,
    non-interlaced. Anything else raises rather than guessing, because a wrong
    guess would show up as art rather than as an error.
    """
    with open(path, 'rb') as handle:
        blob = handle.read()
    if blob[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'{path} is not a PNG')
    offset, idat, palette, transparency = 8, bytearray(), None, None
    width = height = depth = colour = interlace = 0
    while offset < len(blob):
        length = struct.unpack('>I', blob[offset:offset + 4])[0]
        tag = blob[offset + 4:offset + 8]
        payload = blob[offset + 8:offset + 8 + length]
        offset += 12 + length
        if tag == b'IHDR':
            width, height, depth, colour, _, _, interlace = struct.unpack('>IIBBBBB', payload)
        elif tag == b'PLTE':
            palette = payload
        elif tag == b'tRNS':
            transparency = payload
        elif tag == b'IDAT':
            idat.extend(payload)
        elif tag == b'IEND':
            break
    if interlace:
        raise ValueError(f'{path} is interlaced; save it without Adam7')
    if depth not in (8, 16):
        raise ValueError(f'{path} has bit depth {depth}; 8 or 16 expected')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colour)
    if channels is None:
        raise ValueError(f'{path} has colour type {colour}')
    if colour == 3 and palette is None:
        raise ValueError(f'{path} is palette colour with no palette')
    step = channels * (depth // 8)
    stride = width * step
    raw = zlib.decompress(bytes(idat))
    lines: list[bytearray] = []
    previous = bytearray(stride)
    position = 0
    for _ in range(height):
        filter_type = raw[position]
        position += 1
        line = bytearray(raw[position:position + stride])
        position += stride
        for i in range(stride):
            left = line[i - step] if i >= step else 0
            up = previous[i]
            upleft = previous[i - step] if i >= step else 0
            if filter_type == 1:
                line[i] = (line[i] + left) & 0xFF
            elif filter_type == 2:
                line[i] = (line[i] + up) & 0xFF
            elif filter_type == 3:
                line[i] = (line[i] + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                p = left + up - upleft
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - upleft)
                nearest = left if (pa <= pb and pa <= pc) else (up if pb <= pc else upleft)
                line[i] = (line[i] + nearest) & 0xFF
            elif filter_type != 0:
                raise ValueError(f'{path} uses filter type {filter_type}')
        lines.append(line)
        previous = line

    grid = Grid(width, height)
    high = depth == 16
    for y, line in enumerate(lines):
        row = y * width
        for x in range(width):
            base = x * step
            values = [line[base + i * (2 if high else 1)] for i in range(channels)]
            if colour == 3:
                index = values[0]
                r, g, b = palette[index * 3:index * 3 + 3]
                alpha = transparency[index] if transparency and index < len(transparency) else 255
                luma = (r * 299 + g * 587 + b * 114) // 1000
            elif colour == 0:
                luma, alpha = values[0], 255
            elif colour == 4:
                luma, alpha = values
            elif colour == 2:
                r, g, b = values
                luma, alpha = (r * 299 + g * 587 + b * 114) // 1000, 255
            else:
                r, g, b, alpha = values
                luma = (r * 299 + g * 587 + b * 114) // 1000
            ink = (255 - luma) * alpha // 255
            grid.data[row + x] = ink
    return grid


def resample(grid: Grid, width: int, height: int) -> Grid:
    """Box-average `grid` to a new size. Used to fit a photograph to a module."""
    out = Grid(width, height)
    for y in range(height):
        sy0 = y * grid.height // height
        sy1 = max(sy0 + 1, (y + 1) * grid.height // height)
        for x in range(width):
            sx0 = x * grid.width // width
            sx1 = max(sx0 + 1, (x + 1) * grid.width // width)
            total = count = 0
            for sy in range(sy0, min(sy1, grid.height)):
                row = sy * grid.width
                for sx in range(sx0, min(sx1, grid.width)):
                    total += grid.data[row + sx]
                    count += 1
            out.data[y * width + x] = total // count if count else 0
    return out


def rotate(grid: Grid, angle_degrees: float) -> Grid:
    """Rotate a coverage grid about its centre, sampling the source nearest."""
    angle = math.radians(angle_degrees)
    cos, sin = math.cos(angle), math.sin(angle)
    w, h = grid.width, grid.height
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (-w / 2, h / 2), (w / 2, h / 2)]
    turned = [(x * cos - y * sin, x * sin + y * cos) for x, y in corners]
    nw = int(math.ceil(max(p[0] for p in turned) - min(p[0] for p in turned)))
    nh = int(math.ceil(max(p[1] for p in turned) - min(p[1] for p in turned)))
    out = Grid(nw, nh)
    for y in range(nh):
        wy = y - nh / 2 + 0.5
        row = y * nw
        for x in range(nw):
            wx = x - nw / 2 + 0.5
            sx = int(wx * cos + wy * sin + w / 2)
            sy = int(-wx * sin + wy * cos + h / 2)
            if 0 <= sx < w and 0 <= sy < h:
                out.data[row + x] = grid.data[sy * w + sx]
    return out


def _self_check() -> list[str]:
    import os
    import tempfile
    findings = []

    disc = [ellipse(10, 10, 8, 8)]
    grid, ox, oy = stamp(disc, 1.0, 0.0, samples=4)
    coverage = sum(grid.data) / 255
    expected = math.pi * 64
    if abs(coverage - expected) / expected > 0.03:
        findings.append(f'disc area rasterised to {coverage:.1f}, expected about {expected:.1f}')
    turned, _, _ = stamp(disc, 1.0, 37.0, samples=4)
    if abs(sum(turned.data) - sum(grid.data)) / sum(grid.data) > 0.03:
        findings.append('rotating a disc changed its rasterised area')

    bar = [segment(0, 0, 20, 0, 4)]
    grid, _, _ = stamp(bar, 1.0, 0.0, samples=4)
    area = sum(grid.data) / 255
    expected = 20 * 4 + math.pi * 4
    if abs(area - expected) / expected > 0.05:
        findings.append(f'round-capped bar rasterised to {area:.1f}, expected {expected:.1f}')

    source = Grid(9, 5)
    for i, value in enumerate((0, 40, 80, 120, 160, 200, 240, 255, 12)):
        for y in range(5):
            source.data[y * 9 + i] = value
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, 'probe.png')
        write_png(path, source)
        back = read_png(path)
        if back.width != 9 or back.height != 5:
            findings.append('PNG round trip changed the image size')
        elif bytes(back.data) != bytes(source.data):
            findings.append('PNG round trip changed pixel values')

    # A checkerboard of blocks must binarise back to itself.
    board = Grid(64, 64)
    for y in range(64):
        for x in range(64):
            board.data[y * 64 + x] = 230 if (x // 8 + y // 8) % 2 == 0 else 20
    binary = board.binarize(8)
    wrong = sum(1 for i in range(64 * 64)
                if (binary.data[i] > 127) != (board.data[i] > 127))
    if wrong > 64 * 64 * 0.02:
        findings.append(f'local binarisation changed {wrong} pixels of a clean checkerboard')

    solid = Grid(8, 8, 255)
    if abs(solid.mean(0, 0, 8, 8) - 1.0) > 1e-9:
        findings.append('mean of a solid grid is not 1.0')
    if abs(resample(solid, 4, 4).mean(0, 0, 4, 4) - 1.0) > 1e-9:
        findings.append('resampling a solid grid did not stay solid')
    if solid.blur(2).mean(2, 2, 6, 6) < 0.9:
        findings.append('blurring a solid grid emptied its middle')
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check', help='verify rasterised areas and PNG round trips')
    parser.parse_args(argv)
    findings = _self_check()
    for finding in findings:
        print(f'FAIL {finding}')
    print('rasterize: 0 findings' if not findings else f'rasterize: {len(findings)} findings')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
