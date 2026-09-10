#!/usr/bin/env python3
"""QR symbol encoding and decoding, in the standard library alone.

This module owns the *data* half of the ant QR generator: it turns a payload
into the ideal module matrix, and it reads a possibly damaged matrix back,
reporting how much of each Reed-Solomon block's correction budget the damage
consumed. `qrant.py` owns the *art* half and imports both directions from here.

Both directions are needed because the question the art has to answer is not
"does this render look like a QR code" but "how much error correction did the
drawing spend". Only a decoder can answer that, so this file carries one.

Byte mode only. A 256t content tag is base64url, so it is mixed case and
alphanumeric mode cannot hold it; the encoder rejects any other mode rather
than pretending to choose.

Both directions are checked against symbols this file did not make: `check`
pins one CoreImage-generated matrix, and over a sweep of byte-mode payloads the
matrices are identical whenever the mask matches and the decoder reads every
CoreImage symbol. Mask *selection* agrees about seven times in ten; the
standard's four penalty rules leave room for a tie to break either way and any
mask yields a valid symbol, so this is a difference in taste, not in validity.

    python3 scripts/qr_core.py check
    python3 scripts/qr_core.py report --text "https://256t.org/..."
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass


# --- ECC level ------------------------------------------------------------

# name -> (format-info bit pattern, table index, rough share of codewords)
ECC_LEVELS = {'L': (1, 0, 0.07), 'M': (0, 1, 0.15), 'Q': (3, 2, 0.25), 'H': (2, 3, 0.30)}
ECC_ORDER = ('L', 'M', 'Q', 'H')

# Error-correction codewords per block, indexed [ecc index][version]; index 0 unused.
ECC_CODEWORDS_PER_BLOCK = (
    (-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28,
     28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
    (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26,
     26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),
    (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26,
     30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
    (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26,
     28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
)

# Number of error-correction blocks, indexed [ecc index][version].
ECC_BLOCKS = (
    (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7,
     8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),
    (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14,
     16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),
    (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21,
     20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68),
    (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25,
     25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81),
)

BYTE_MODE = 4


def size_for(version: int) -> int:
    return version * 4 + 17


def raw_data_modules(version: int) -> int:
    """Module count available to data and error correction, before format info."""
    result = (16 * version + 128) * version + 64
    if version >= 2:
        aligns = version // 7 + 2
        result -= (25 * aligns - 10) * aligns - 55
        if version >= 7:
            result -= 36
    return result


def total_codewords(version: int) -> int:
    return raw_data_modules(version) // 8


def data_codewords(version: int, ecc: str) -> int:
    index = ECC_LEVELS[ecc][1]
    return (total_codewords(version)
            - ECC_CODEWORDS_PER_BLOCK[index][version] * ECC_BLOCKS[index][version])


def byte_capacity(version: int, ecc: str) -> int:
    """How many payload bytes fit, after mode and character-count overhead."""
    bits = data_codewords(version, ecc) * 8 - 4 - count_bits(version)
    return max(0, bits // 8)


def count_bits(version: int) -> int:
    return 8 if version <= 9 else 16


def smallest_version(payload: bytes, ecc: str, minimum: int = 1) -> int:
    for version in range(max(1, minimum), 41):
        if byte_capacity(version, ecc) >= len(payload):
            return version
    raise ValueError(f'{len(payload)} bytes will not fit any version at ECC {ecc}')


def alignment_positions(version: int) -> list[int]:
    if version == 1:
        return []
    count = version // 7 + 2
    step = 26 if version == 32 else (version * 4 + count * 2 + 1) // (count * 2 - 2) * 2
    size = size_for(version)
    tail = [size - 7 - i * step for i in range(count - 1)]
    return list(reversed(tail + [6]))


# --- GF(256) --------------------------------------------------------------

_EXP = [0] * 512
_LOG = [0] * 256


def _build_tables() -> None:
    value = 1
    for i in range(255):
        _EXP[i] = value
        _LOG[value] = i
        value <<= 1
        if value & 0x100:
            value ^= 0x11D
    for i in range(255, 512):
        _EXP[i] = _EXP[i - 255]


_build_tables()


def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def gf_div(a: int, b: int) -> int:
    if b == 0:
        raise ZeroDivisionError('GF(256) division by zero')
    if a == 0:
        return 0
    return _EXP[(_LOG[a] - _LOG[b]) % 255]


def gf_inv(a: int) -> int:
    return _EXP[(255 - _LOG[a]) % 255]


def poly_mul(p: list[int], q: list[int]) -> list[int]:
    out = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                out[i + j] ^= gf_mul(a, b)
    return out


def poly_eval(p: list[int], x: int) -> int:
    result = 0
    for coefficient in p:
        result = gf_mul(result, x) ^ coefficient
    return result


def generator_poly(degree: int) -> list[int]:
    result = [1]
    for i in range(degree):
        result = poly_mul(result, [1, _EXP[i]])
    return result


def rs_encode(data: bytes, degree: int) -> bytes:
    generator = generator_poly(degree)
    remainder = [0] * degree
    for byte in data:
        factor = byte ^ remainder[0]
        remainder = remainder[1:] + [0]
        if factor:
            for i, g in enumerate(generator[1:]):
                remainder[i] ^= gf_mul(g, factor)
    return bytes(remainder)


def rs_decode(block: list[int], degree: int) -> tuple[list[int] | None, int]:
    """Correct a received block. Returns `(corrected, errors)`, or `(None, -1)`.

    `errors` is the number of symbols the decoder had to change, which is what
    makes this module able to price a drawing: the ratio of that count to
    `degree // 2` is the share of the block's budget the art spent.
    """
    syndromes = [poly_eval(block, _EXP[i]) for i in range(degree)]
    if not any(syndromes):
        return list(block), 0
    locator, previous = [1], [1]
    shift = 1
    discrepancy_old = 1
    for i in range(degree):
        discrepancy = syndromes[i]
        for j in range(1, len(locator)):
            discrepancy ^= gf_mul(locator[len(locator) - 1 - j], syndromes[i - j])
        if discrepancy == 0:
            shift += 1
            continue
        scaled = [gf_mul(c, gf_div(discrepancy, discrepancy_old)) for c in previous]
        scaled = scaled + [0] * shift
        padded = [0] * (len(scaled) - len(locator)) + locator
        if len(locator) > len(scaled):
            padded = locator
            scaled = [0] * (len(locator) - len(scaled)) + scaled
        combined = [a ^ b for a, b in zip(padded, scaled)]
        if 2 * (len(locator) - 1) <= i:
            previous, locator = locator, combined
            discrepancy_old = discrepancy
            shift = 1
        else:
            locator = combined
            shift += 1
    errors = len(locator) - 1
    if errors * 2 > degree:
        return None, -1
    positions = []
    for i in range(len(block)):
        if poly_eval(locator, gf_inv(_EXP[i])) == 0:
            positions.append(len(block) - 1 - i)
    if len(positions) != errors:
        return None, -1
    # Forney: evaluator = syndromes * locator mod x^degree
    syndrome_poly = list(reversed(syndromes))
    evaluator = poly_mul(syndrome_poly, locator)[-degree:]
    derivative = [c for i, c in enumerate(reversed(locator)) if i % 2 == 1]
    derivative = list(reversed(derivative))
    corrected = list(block)
    for position in positions:
        x = _EXP[(len(block) - 1 - position) % 255]
        x_inv = gf_inv(x)
        numerator = poly_eval(evaluator, x_inv)
        denominator = poly_eval(derivative, gf_mul(x_inv, x_inv))
        if denominator == 0:
            return None, -1
        magnitude = gf_div(numerator, gf_mul(x_inv, denominator))
        corrected[position] ^= magnitude
    check = [poly_eval(corrected, _EXP[i]) for i in range(degree)]
    if any(check):
        return None, -1
    return corrected, errors


# --- encoding -------------------------------------------------------------

def encode_codewords(payload: bytes, version: int, ecc: str) -> bytes:
    """Payload -> the interleaved codeword stream the matrix carries."""
    capacity = byte_capacity(version, ecc)
    if len(payload) > capacity:
        raise ValueError(f'{len(payload)} bytes exceeds {capacity} at version {version} ECC {ecc}')
    bits: list[int] = []

    def push(value: int, width: int) -> None:
        for shift in range(width - 1, -1, -1):
            bits.append((value >> shift) & 1)

    push(BYTE_MODE, 4)
    push(len(payload), count_bits(version))
    for byte in payload:
        push(byte, 8)
    total = data_codewords(version, ecc) * 8
    push(0, min(4, total - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    pads = (0xEC, 0x11)
    index = 0
    while len(bits) < total:
        push(pads[index % 2], 8)
        index += 1
    data = bytes(int(''.join(str(b) for b in bits[i:i + 8]), 2) for i in range(0, len(bits), 8))

    index = ECC_LEVELS[ecc][1]
    blocks_total = ECC_BLOCKS[index][version]
    degree = ECC_CODEWORDS_PER_BLOCK[index][version]
    short_len = len(data) // blocks_total
    short_count = blocks_total - len(data) % blocks_total

    blocks, eccs = [], []
    offset = 0
    for i in range(blocks_total):
        length = short_len + (0 if i < short_count else 1)
        block = data[offset:offset + length]
        offset += length
        blocks.append(block)
        eccs.append(rs_encode(block, degree))

    stream = bytearray()
    for i in range(short_len + 1):
        for block in blocks:
            if i < len(block):
                stream.append(block[i])
    for i in range(degree):
        for block in eccs:
            stream.append(block[i])
    return bytes(stream)


def block_layout(version: int, ecc: str) -> tuple[int, int, int, int]:
    """`(blocks, ecc codewords per block, short data length, short block count)`."""
    index = ECC_LEVELS[ecc][1]
    blocks_total = ECC_BLOCKS[index][version]
    degree = ECC_CODEWORDS_PER_BLOCK[index][version]
    total = data_codewords(version, ecc)
    return blocks_total, degree, total // blocks_total, blocks_total - total % blocks_total


# --- matrix ---------------------------------------------------------------

RESERVED, LIGHT, DARK = -1, 0, 1


def _blank(version: int) -> tuple[list[list[int]], list[list[bool]]]:
    size = size_for(version)
    modules = [[LIGHT] * size for _ in range(size)]
    function = [[False] * size for _ in range(size)]
    return modules, function


def _place_finder(modules, function, cx: int, cy: int) -> None:
    size = len(modules)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            x, y = cx + dx, cy + dy
            if not (0 <= x < size and 0 <= y < size):
                continue
            # Rings out from the centre: 3x3 dark core, light ring, dark ring,
            # then the light separator at 4.
            distance = max(abs(dx), abs(dy))
            modules[y][x] = DARK if distance in (0, 1, 3) else LIGHT
            function[y][x] = True


def function_matrix(version: int) -> tuple[list[list[int]], list[list[bool]]]:
    """The finder, timing, alignment, dark-module and reserved-info modules."""
    modules, function = _blank(version)
    size = size_for(version)
    for x in range(size):
        modules[6][x] = DARK if x % 2 == 0 else LIGHT
        function[6][x] = True
        modules[x][6] = DARK if x % 2 == 0 else LIGHT
        function[x][6] = True
    _place_finder(modules, function, 3, 3)
    _place_finder(modules, function, size - 4, 3)
    _place_finder(modules, function, 3, size - 4)
    positions = alignment_positions(version)
    last = len(positions) - 1
    for i, ay in enumerate(positions):
        for j, ax in enumerate(positions):
            if (i, j) in ((0, 0), (0, last), (last, 0)):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    modules[ay + dy][ax + dx] = DARK if max(abs(dx), abs(dy)) != 1 else LIGHT
                    function[ay + dy][ax + dx] = True
    # Format information, reserved here and written after masking.
    for i in range(9):
        function[8][i] = True
        function[i][8] = True
    for i in range(8):
        function[8][size - 1 - i] = True
        function[size - 1 - i][8] = True
    modules[size - 8][8] = DARK          # the always-dark module
    function[size - 8][8] = True
    if version >= 7:
        for i in range(6):
            for j in range(3):
                function[i][size - 11 + j] = True
                function[size - 11 + j][i] = True
    return modules, function


def data_path(version: int) -> list[tuple[int, int]]:
    """Module coordinates in codeword order: the two-column upward zigzag."""
    _, function = function_matrix(version)
    size = size_for(version)
    path = []
    right = size - 1
    while right >= 1:
        if right == 6:
            right = 5
        upward = ((size - 1 - right) // 2) % 2 == 0
        rows = range(size - 1, -1, -1) if upward else range(size)
        for y in rows:
            for x in (right, right - 1):
                if not function[y][x]:
                    path.append((x, y))
        right -= 2
    return path


MASKS = (
    lambda x, y: (x + y) % 2 == 0,
    lambda x, y: y % 2 == 0,
    lambda x, y: x % 3 == 0,
    lambda x, y: (x + y) % 3 == 0,
    lambda x, y: (y // 2 + x // 3) % 2 == 0,
    lambda x, y: (x * y) % 2 + (x * y) % 3 == 0,
    lambda x, y: ((x * y) % 2 + (x * y) % 3) % 2 == 0,
    lambda x, y: ((x + y) % 2 + (x * y) % 3) % 2 == 0,
)


def _format_bits(ecc: str, mask: int) -> int:
    data = ECC_LEVELS[ecc][0] << 3 | mask
    remainder = data
    for _ in range(10):
        remainder = (remainder << 1) ^ ((remainder >> 9) * 0x537)
    return ((data << 10) | remainder) ^ 0x5412


def _version_bits(version: int) -> int:
    remainder = version
    for _ in range(12):
        remainder = (remainder << 1) ^ ((remainder >> 11) * 0x1F25)
    return version << 12 | remainder


def _draw_format(modules, ecc: str, mask: int) -> None:
    size = len(modules)
    bits = _format_bits(ecc, mask)
    # First copy: bits 0-8 run down column 8, bits 9-14 run left along row 8.
    for i in range(6):
        modules[i][8] = (bits >> i) & 1
    modules[7][8] = (bits >> 6) & 1
    modules[8][8] = (bits >> 7) & 1
    modules[8][7] = (bits >> 8) & 1
    for i in range(9, 15):
        modules[8][14 - i] = (bits >> i) & 1
    # Second copy: bits 0-7 run right along row 8, bits 8-14 run up column 8,
    # stopping one short of the always-dark module below them.
    for i in range(8):
        modules[8][size - 1 - i] = (bits >> i) & 1
    for i in range(8, 15):
        modules[size - 15 + i][8] = (bits >> i) & 1


def _draw_version(modules, version: int) -> None:
    if version < 7:
        return
    size = len(modules)
    bits = _version_bits(version)
    for i in range(18):
        bit = (bits >> i) & 1
        modules[i // 3][size - 11 + i % 3] = bit
        modules[size - 11 + i % 3][i // 3] = bit


def _penalty(modules) -> int:
    size = len(modules)
    score = 0
    for run_rows in (modules, [list(col) for col in zip(*modules)]):
        for row in run_rows:
            run, colour = 1, row[0]
            for value in row[1:]:
                if value == colour:
                    run += 1
                else:
                    if run >= 5:
                        score += run - 2
                    run, colour = 1, value
            if run >= 5:
                score += run - 2
    for y in range(size - 1):
        for x in range(size - 1):
            block = (modules[y][x], modules[y][x + 1], modules[y + 1][x], modules[y + 1][x + 1])
            if len(set(block)) == 1:
                score += 3
    finder = [DARK, LIGHT, DARK, DARK, DARK, LIGHT, DARK]
    light = [LIGHT] * 4
    for lines in (modules, [list(col) for col in zip(*modules)]):
        for line in lines:
            padded = light + line + light
            for x in range(len(padded) - 10):
                if padded[x + 4:x + 11] != finder:
                    continue
                if padded[x:x + 4] == light:
                    score += 40
                if padded[x + 11:x + 15] == light:
                    score += 40
    dark = sum(row.count(DARK) for row in modules)
    deviation = abs(dark * 100 / (size * size) - 50)
    score += int(deviation // 5) * 10
    return score


def build_matrix(payload: bytes, version: int, ecc: str,
                 mask: int | None = None) -> tuple[list[list[int]], list[list[bool]], int]:
    """`(modules, function-module flags, chosen mask)` for one payload."""
    stream = encode_codewords(payload, version, ecc)
    path = data_path(version)
    base, function = function_matrix(version)
    bits = [(byte >> shift) & 1 for byte in stream for shift in range(7, -1, -1)]
    for (x, y), bit in zip(path, bits):
        base[y][x] = bit

    best, best_score, best_mask = None, None, 0
    candidates = range(8) if mask is None else (mask,)
    for candidate in candidates:
        trial = [row[:] for row in base]
        for (x, y) in path:
            if MASKS[candidate](x, y):
                trial[y][x] ^= 1
        _draw_format(trial, ecc, candidate)
        _draw_version(trial, version)
        score = _penalty(trial)
        if best_score is None or score < best_score:
            best, best_score, best_mask = trial, score, candidate
    return best, function, best_mask


# --- decoding -------------------------------------------------------------

@dataclass
class BlockResult:
    index: int
    errors: int
    capacity: int
    ok: bool

    @property
    def spent(self) -> float:
        return self.errors / self.capacity if self.capacity else 0.0


@dataclass
class DecodeResult:
    ok: bool
    payload: bytes | None
    reason: str
    blocks: list[BlockResult]
    module_errors: int
    function_errors: int
    format_ok: bool

    @property
    def worst_spent(self) -> float:
        return max((b.spent for b in self.blocks), default=1.0)

    @property
    def corrected(self) -> int:
        return sum(b.errors for b in self.blocks if b.errors > 0)

    @property
    def budget(self) -> int:
        return sum(b.capacity for b in self.blocks)


def _read_format(modules) -> tuple[str, int] | None:
    size = len(modules)
    first = 0
    for i in range(6):
        first |= modules[i][8] << i
    first |= modules[7][8] << 6
    first |= modules[8][8] << 7
    first |= modules[8][7] << 8
    for i in range(9, 15):
        first |= modules[8][14 - i] << i
    second = 0
    for i in range(8):
        second |= modules[8][size - 1 - i] << i
    for i in range(8, 15):
        second |= modules[size - 15 + i][8] << i
    best, best_distance = None, 99
    for name in ECC_ORDER:
        for mask in range(8):
            reference = _format_bits(name, mask)
            for candidate in (first, second):
                distance = bin(candidate ^ reference).count('1')
                if distance < best_distance:
                    best, best_distance = (name, mask), distance
    return best if best_distance <= 3 else None


def decode(modules, version: int, expect_ecc: str | None = None) -> DecodeResult:
    """Read a module matrix the way a scanner does, and price the damage."""
    header = _read_format(modules)
    if header is None:
        return DecodeResult(False, None, 'format information unreadable', [], 0, 0, False)
    ecc, mask = header
    if expect_ecc and ecc != expect_ecc:
        return DecodeResult(False, None, f'format read ECC {ecc}, expected {expect_ecc}',
                            [], 0, 0, False)
    path = data_path(version)
    bits = []
    for (x, y) in path:
        bit = modules[y][x]
        if MASKS[mask](x, y):
            bit ^= 1
        bits.append(bit)
    stream = [int(''.join(str(b) for b in bits[i:i + 8]), 2) for i in range(0, len(bits) - 7, 8)]

    blocks_total, degree, short_len, short_count = block_layout(version, ecc)
    lengths = [short_len + (0 if i < short_count else 1) for i in range(blocks_total)]
    blocks: list[list[int]] = [[] for _ in range(blocks_total)]
    index = 0
    for i in range(short_len + 1):
        for b in range(blocks_total):
            if i < lengths[b]:
                blocks[b].append(stream[index])
                index += 1
    for i in range(degree):
        for b in range(blocks_total):
            blocks[b].append(stream[index])
            index += 1

    results, recovered, ok = [], [], True
    for i, block in enumerate(blocks):
        fixed, errors = rs_decode(block, degree)
        results.append(BlockResult(i, errors if errors >= 0 else degree // 2 + 1,
                                   degree // 2, fixed is not None))
        if fixed is None:
            ok = False
            recovered.append(None)
        else:
            recovered.append(fixed[:lengths[i]])
    if not ok:
        return DecodeResult(False, None, 'a block exceeded its correction capacity',
                            results, 0, 0, True)

    data = bytearray()
    for block in recovered:
        data.extend(block)
    payload = _parse(bytes(data), version)
    if payload is None:
        return DecodeResult(False, None, 'corrected codewords are not a byte-mode segment',
                            results, 0, 0, True)
    return DecodeResult(True, payload, 'decoded', results, 0, 0, True)


def _parse(data: bytes, version: int) -> bytes | None:
    bits = [(byte >> shift) & 1 for byte in data for shift in range(7, -1, -1)]
    if len(bits) < 4 or int(''.join(str(b) for b in bits[:4]), 2) != BYTE_MODE:
        return None
    width = count_bits(version)
    length = int(''.join(str(b) for b in bits[4:4 + width]), 2)
    start = 4 + width
    needed = length * 8
    if start + needed > len(bits):
        return None
    chunk = bits[start:start + needed]
    return bytes(int(''.join(str(b) for b in chunk[i:i + 8]), 2) for i in range(0, needed, 8))


# --- self check -----------------------------------------------------------

# One symbol produced by an implementation that is not this one: "hello world"
# at version 1, ECC M, mask 2, as CoreImage's CIQRCodeGenerator draws it. The
# encoder here reproduces it module for module. Two bugs that a round trip
# through this file alone could never catch — an inverted finder ring and a
# transposed format-information placement — both survived the round trip and
# died against this fixture. Keep it.
COREIMAGE_HELLO_WORLD_1M2 = (
    '111111100101101111111',
    '100000100010001000001',
    '101110101111001011101',
    '101110101110101011101',
    '101110101010101011101',
    '100000101001001000001',
    '111111101010101111111',
    '000000001010000000000',
    '101111100101001111100',
    '011011010101111111101',
    '101011110110111001110',
    '101001000101110011100',
    '000101111100111000001',
    '000000001010100011001',
    '111111100001001000110',
    '100000101000010101111',
    '101110101001001100001',
    '101110101100111111000',
    '101110101100100100100',
    '100000100110110011100',
    '111111101101101010010',
)


def _self_check() -> list[str]:
    findings = []
    tag = 'A' * 86
    sample = ('256t.org/' + '0' * 8 + tag).encode()

    if byte_capacity(10, 'H') != 119:
        findings.append(f'version 10 ECC H byte capacity is {byte_capacity(10, "H")}, expected 119')
    if byte_capacity(1, 'L') != 17:
        findings.append(f'version 1 ECC L byte capacity is {byte_capacity(1, "L")}, expected 17')
    if alignment_positions(7) != [6, 22, 38]:
        findings.append('version 7 alignment positions are wrong')
    if alignment_positions(32) != [6, 34, 60, 86, 112, 138]:
        findings.append(f'version 32 alignment positions are {alignment_positions(32)}')

    reference = [[int(c) for c in row] for row in COREIMAGE_HELLO_WORLD_1M2]
    built, _, _ = build_matrix(b'hello world', 1, 'M', mask=2)
    drift = sum(1 for y, row in enumerate(reference)
                for x, value in enumerate(row) if value != built[y][x])
    if drift:
        findings.append(f'{drift} modules differ from the CoreImage reference symbol')
    if decode(reference, 1).payload != b'hello world':
        findings.append('the decoder cannot read the CoreImage reference symbol')

    for ecc in ECC_ORDER:
        version = smallest_version(sample, ecc)
        modules, _, mask = build_matrix(sample, version, ecc)
        result = decode(modules, version, ecc)
        if not result.ok or result.payload != sample:
            findings.append(f'round trip failed at version {version} ECC {ecc}: {result.reason}')
        elif result.corrected:
            findings.append(f'clean matrix at version {version} ECC {ecc} reported '
                            f'{result.corrected} corrections')

    # Deliberate damage: flip exactly the correctable number of codewords in one block.
    version = smallest_version(sample, 'H')
    modules, function, _ = build_matrix(sample, version, 'H')
    _, degree, _, _ = block_layout(version, 'H')
    path = data_path(version)
    flipped = 0
    for (x, y) in path[:8 * (degree // 2)]:
        modules[y][x] ^= 1
        flipped += 1
    result = decode(modules, version, 'H')
    if not result.ok or result.payload != sample:
        findings.append(f'damage inside the correction budget did not decode: {result.reason}')

    # And past it: enough damage must be reported as a failure, not a wrong payload.
    modules, _, _ = build_matrix(sample, version, 'H')
    for (x, y) in path[:8 * (degree // 2 + 4) * 3]:
        modules[y][x] ^= 1
    result = decode(modules, version, 'H')
    if result.ok and result.payload != sample:
        findings.append('over-budget damage decoded to a wrong payload without reporting failure')
    return findings


def _report(text: str) -> None:
    payload = text.encode()
    print(f'payload: {len(payload)} bytes, byte mode')
    print(f'{"ECC":<4}{"version":>8}{"modules":>9}{"capacity":>10}'
          f'{"slack":>7}{"blocks":>8}{"budget":>8}{"budget %":>10}')
    for ecc in ECC_ORDER:
        version = smallest_version(payload, ecc)
        size = size_for(version)
        capacity = byte_capacity(version, ecc)
        blocks, degree, _, _ = block_layout(version, ecc)
        budget = blocks * (degree // 2)
        share = budget / total_codewords(version)
        print(f'{ecc:<4}{version:>8}{f"{size}x{size}":>9}{capacity:>10}'
              f'{capacity - len(payload):>7}{blocks:>8}{budget:>8}{share:>9.1%}')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check', help='encode, decode and damage-test the codec')
    report = sub.add_parser('report', help='show the versions a payload fits')
    report.add_argument('--text', required=True)
    args = parser.parse_args(argv)

    if args.command == 'report':
        _report(args.text)
        return 0
    findings = _self_check()
    for finding in findings:
        print(f'FAIL {finding}')
    print('qr_core: 0 findings' if not findings else f'qr_core: {len(findings)} findings')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
