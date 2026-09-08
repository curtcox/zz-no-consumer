"""Offline fixtures for crop detection, exact pixels, filters and write boundaries."""
import struct
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import zlib

import image_crop as crop


def fixture(w, h, channels=3, filtered=False):
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            value = [255]*channels if x < 5 or x >= w-5 or y < 6 or y >= h-6 else [
                (x*17+y*23+c*31) % 256 for c in range(channels)]
            row.extend(value)
        rows.append(row)
    color = {1: 0, 2: 4, 3: 2, 4: 6}[channels]
    header = struct.pack('>IIBBBBB', w, h, 8, color, 0, 0, 0)
    raw = bytearray()
    for y, row in enumerate(rows):
        method = y % 5 if filtered else 0
        raw.append(method)
        previous = rows[y-1] if y else bytes(w*channels)
        for x, value in enumerate(row):
            a = row[x-channels] if x >= channels else 0
            b = previous[x]
            c = previous[x-channels] if x >= channels else 0
            raw.append((value-(0, a, b, (a+b)//2, crop.paeth(a, b, c))[method]) % 256)
    data = (crop.SIGNATURE + crop.chunk(b'IHDR', header)
            + crop.chunk(b'IDAT', zlib.compress(raw)) + crop.chunk(b'IEND', b''))
    return data, rows


def fails(action):
    try:
        action()
    except (ValueError, OSError):
        return
    raise AssertionError('Expected rejection')


def check():
    for channels in (1, 2, 3, 4):
        data, rows = fixture(100, 80, channels, filtered=True)
        decoded = crop.decode(data)
        assert decoded[-1] == rows, 'All PNG filters must decode exactly'
        cropped = crop.decode(crop.encode(decoded, [5, 6, 95, 74]))
        assert cropped[:3] == (90, 68, channels)
        assert cropped[-1] == [row[5*channels:95*channels] for row in rows[6:74]]
    data, _ = fixture(100, 80)
    decoded = crop.decode(data)
    assert crop.borders(decoded) == dict(top=6, bottom=6, left=5, right=5)
    decoded[-1][2][:] = b'\0' * 300
    decoded[-1][-3][:] = b'\0' * 300
    assert crop.borders(decoded) == dict(top=6, bottom=6, left=5, right=5), 'Layered frames'
    for row in decoded[-1]:
        row[:] = b'\xff'*len(row)
    assert not any(crop.borders(decoded).values()), 'Blank images must not be cropped'
    for box in ([0, 0, 0, 1], [-1, 0, 20, 20], [0, 0, 101, 80], [0, 0, 1.5, 2]):
        fails(lambda: crop.encode(decoded, box))
    fails(lambda: crop.decode(data[:-1]))
    broken = bytearray(data); broken[-5] ^= 1
    fails(lambda: crop.decode(bytes(broken)))
    tsv = ('level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
           '5\t1\t1\t1\t1\t1\t20\t70\t20\t5\t96\tCaption\n'
           '5\t1\t1\t1\t1\t2\t42\t70\t20\t5\t90\twords\n'
           '5\t1\t2\t1\t1\t1\t40\t35\t20\t10\t88\tSign\n'
           '5\t1\t3\t1\t1\t1\t20\t1\t20\t5\t12\tNoise\n')
    text = crop.parse_tsv(tsv, 100, 80)
    assert len(text) == 2 and text[0]['edge'] == 'bottom'
    assert text[0]['box'] == [20, 70, 62, 75] and text[1]['edge'] is None
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory)/'source.png'; source.write_bytes(data)
        report = crop.analyze(source, data, crop.decode(data), ocr='off')
        assert report['suggested_box'] == [5, 6, 95, 74]
        report['source'] = '</script><script>alert(1)</script>'
        html = crop.review(data, report)
        assert b'</script><script>' not in html and b'__REPORT__' not in html
        fails(lambda: crop.write_new(source, b'overwrite'))
        assert source.read_bytes() == data
        output = Path(directory)/'crop.png'
        crop.write_new(output, crop.encode(crop.decode(data), report['suggested_box']))
        assert crop.png_size(output.read_bytes()) == [90, 68]
        receipt = Path(directory)/'receipt.json'
        receipt.write_text(json.dumps(dict(box=report['suggested_box'], source_sha256=report['sha256'])))
        final = Path(directory)/'final.png'
        command = [sys.executable, str(Path(crop.__file__)), 'crop', str(source),
                   '--receipt', str(receipt), '--output', str(final)]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert final.read_bytes() == output.read_bytes()
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 1 and final.read_bytes() == output.read_bytes()
        receipt.write_text(json.dumps(dict(box=report['suggested_box'], source_sha256='wrong')))
        command[-1] = str(Path(directory)/'wrong.png')
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 1 and not Path(command[-1]).exists()
    print('Image crop: filters, pixel preservation, border/text detection, invalid inputs and source protection passed.')
