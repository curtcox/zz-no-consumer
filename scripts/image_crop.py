#!/usr/bin/env python3
"""Inspect borders and OCR text, review crops, and save lossless PNG derivatives.

Standard library only. Optional local Tesseract supplies text boxes; no model calls.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

from art_jobs import png_size

SIGNATURE = b'\x89PNG\r\n\x1a\n'


def chunk(kind, payload):
    return (struct.pack('>I', len(payload)) + kind + payload
            + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))


def paeth(a, b, c):
    p = a + b - c
    distances = (abs(p-a), abs(p-b), abs(p-c))
    return (a, b, c)[distances.index(min(distances))]


def decode(data):
    """Use the queue's bounded validation before reversing all five PNG filters."""
    w, h = png_size(data)
    pos, compressed, metadata = 8, [], []
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        kind, payload = data[pos+4:pos+8], data[pos+8:pos+8+length]
        if kind == b'IHDR':
            header = payload
        elif kind == b'IDAT':
            compressed.append(payload)
        elif kind in (b'cHRM', b'gAMA', b'iCCP', b'sRGB', b'tRNS', b'pHYs', b'sBIT'):
            metadata.append((kind, payload))
        pos += length + 12
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[header[9]]
    raw = zlib.decompress(b''.join(compressed))
    stride, rows = w * channels, []
    previous = bytearray(stride)
    for y in range(h):
        start = y * (stride + 1)
        method = raw[start]
        row = bytearray(raw[start+1:start+1+stride])
        if method:
            for x in range(stride):
                a = row[x-channels] if x >= channels else 0
                b = previous[x]
                c = previous[x-channels] if x >= channels else 0
                predictor = (0, a, b, (a+b)//2, paeth(a, b, c))[method]
                row[x] = (row[x] + predictor) & 255
        rows.append(row)
        previous = row
    return w, h, channels, header, metadata, rows


def encode(decoded, box):
    w, h, channels, header, metadata, rows = decoded
    left, top, right, bottom = validate_box(box, w, h)
    cropped = b''.join(b'\0' + row[left*channels:right*channels] for row in rows[top:bottom])
    return (SIGNATURE + chunk(b'IHDR', struct.pack('>II', right-left, bottom-top) + header[8:])
            + b''.join(chunk(k, v) for k, v in metadata)
            + chunk(b'IDAT', zlib.compress(cropped)) + chunk(b'IEND', b''))


def validate_box(box, w, h):
    if len(box) != 4 or any(type(v) is not int for v in box):
        raise ValueError('Crop requires four integer pixel coordinates')
    l, t, r, b = box
    if not (0 <= l < r <= w and 0 <= t < b <= h):
        raise ValueError(f'Crop must be nonempty and inside {w} × {h}')
    return list(box)


def borders(decoded, tolerance=12, max_fraction=.2):
    """Conservative flat edge runs, allowing color changes between border layers.

    Each entire row/column must be nearly uniform. A limit hit is ambiguous and
    yields no removal on that edge (e.g. blank sky or a monochrome image).
    """
    w, h, channels, _, _, rows = decoded
    def pixel(x, y):
        value = rows[y][x*channels:(x+1)*channels]
        # Ignore RGB noise under fully transparent pixels.
        return bytes(channels) if channels in (2, 4) and value[-1] == 0 else value
    def uniform(points):
        low, high = None, None
        for x, y in points:
            value = pixel(x, y)
            if low is None:
                low, high = list(value), list(value)
            else:
                for c in range(channels):
                    low[c], high[c] = min(low[c], value[c]), max(high[c], value[c])
                    if high[c] - low[c] > tolerance:
                        return False
        return True
    found = {}
    # Peel full-width rows first; restrict columns to the remaining vertical span.
    for side in ('top', 'bottom', 'left', 'right'):
        vertical = side in ('top', 'bottom')
        length = h if vertical else w
        limit = max(1, int(length * max_fraction))
        count = 0
        for offset in range(limit):
            at = offset if side in ('top', 'left') else length-1-offset
            points = ((x, at) for x in range(w)) if vertical else (
                (at, y) for y in range(found['top'], h-found['bottom']))
            if not uniform(points):
                break
            count += 1
        found[side] = count if count < limit else 0
    return found


def parse_tsv(tsv, w, h):
    lines = {}
    for row in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
        if row['level'] != '5' or not row['text'].strip() or float(row['conf']) < 40:
            continue
        x, y, width, height = (int(row[k]) for k in ('left', 'top', 'width', 'height'))
        box = [max(0, x), max(0, y), min(w, x+width), min(h, y+height)]
        if box[0] >= box[2] or box[1] >= box[3]:
            continue
        key = tuple(row[k] for k in ('page_num', 'block_num', 'par_num', 'line_num'))
        lines.setdefault(key, []).append((box, row['text'], float(row['conf'])))
    results = []
    for words in lines.values():
        box = [min(a[0][0] for a in words), min(a[0][1] for a in words),
               max(a[0][2] for a in words), max(a[0][3] for a in words)]
        distances = dict(left=box[2]/w, top=box[3]/h, right=(w-box[0])/w, bottom=(h-box[1])/h)
        edge = min(distances, key=distances.get)
        results.append(dict(box=box, text=' '.join(a[1] for a in words),
                            confidence=round(sum(a[2] for a in words)/len(words), 1),
                            edge=edge if distances[edge] <= .25 else None))
    return results


def analyze(path, data, decoded, ocr='auto', tolerance=12):
    w, h = decoded[:2]
    margins = borders(decoded, tolerance)
    report = dict(source=str(path.resolve()), sha256=hashlib.sha256(data).hexdigest(),
                  width=w, height=h, borders=margins,
                  suggested_box=[margins['left'], margins['top'], w-margins['right'], h-margins['bottom']],
                  text=[], ocr='disabled', warnings=[
                      'Flat edges may be intentional artwork. Review before cropping.',
                      'OCR identifies text, not its purpose. Captions require visual review.',
                      'A rectangular crop cannot remove interior text without losing surrounding artwork.'])
    executable = shutil.which('tesseract') if ocr != 'off' else None
    if ocr == 'required' and not executable:
        raise ValueError('Tesseract is required but not installed or on PATH')
    if executable:
        # OCR the exact validated bytes, avoiding changes to the source during analysis.
        with tempfile.TemporaryDirectory(prefix='image-crop-') as directory:
            snapshot = Path(directory) / 'source.png'
            snapshot.write_bytes(data)
            result = subprocess.run([executable, str(snapshot), 'stdout', '--psm', '11', 'tsv'],
                                    capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise ValueError('Tesseract failed: ' + result.stderr.strip())
        report['text'] = parse_tsv(result.stdout, w, h)
        report['ocr'] = 'tesseract; sparse text; confidence >= 40'
    elif ocr != 'off':
        report['ocr'] = 'unavailable: install local Tesseract for caption candidates'
    return report


def write_new(path, payload):
    """Exclusive creation protects sources and all earlier derivatives."""
    with Path(path).open('xb') as stream:
        stream.write(payload)


def review(data, report):
    template = Path(__file__).with_name('image_crop_review.html').read_text()
    return template.replace('__REPORT__', json.dumps(report).replace('<', '\\u003c')).replace(
        '__IMAGE__', base64.b64encode(data).decode()).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect', help='Report borders/text and optionally write an interactive review')
    inspect.add_argument('image', type=Path)
    inspect.add_argument('--ocr', choices=('auto', 'off', 'required'), default='auto')
    inspect.add_argument('--tolerance', type=int, choices=range(0, 65), metavar='0..64', default=12)
    inspect.add_argument('--review', type=Path, help='New self-contained HTML file')
    crop = commands.add_parser('crop', help='Write a new lossless PNG with explicit reviewed coordinates')
    crop.add_argument('image', type=Path)
    selection = crop.add_mutually_exclusive_group(required=True)
    selection.add_argument('--box', nargs=4, type=int, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    selection.add_argument('--receipt', type=Path, help='Reviewed browser receipt; verifies source SHA-256')
    crop.add_argument('--output', type=Path, required=True)
    crop.add_argument('--source-sha256', help='Refuse a source that changed since inspection')
    commands.add_parser('check', help='Run disposable offline regression fixtures')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            from image_crop_checks import check
            check()
            return
        data = args.image.read_bytes()
        decoded = decode(data)
        if args.command == 'inspect':
            report = analyze(args.image, data, decoded, args.ocr, args.tolerance)
            if args.review:
                write_new(args.review, review(data, report))
            print(json.dumps(report, indent=2))
        else:
            digest = hashlib.sha256(data).hexdigest()
            if args.receipt:
                receipt = json.loads(args.receipt.read_text())
                if not isinstance(receipt, dict) or not isinstance(receipt.get('box'), list) or not receipt.get('source_sha256'):
                    raise ValueError('Receipt requires box and source_sha256')
                if receipt['source_sha256'] != digest:
                    raise ValueError('Receipt belongs to a different source image')
                args.box = receipt['box']
            if args.source_sha256 and args.source_sha256 != digest:
                raise ValueError('Source changed since inspection')
            output = encode(decoded, args.box)
            write_new(args.output, output)
            print(json.dumps(dict(source_sha256=digest, output=str(args.output),
                                  output_sha256=hashlib.sha256(output).hexdigest(), box=args.box), indent=2))
    except (ValueError, OSError, zlib.error, subprocess.TimeoutExpired) as error:
        print(f'Image crop: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
