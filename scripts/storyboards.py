#!/usr/bin/env python3
"""Deterministic scene previews. generate appends changed boards; check is offline.

    python3 scripts/storyboards.py generate
    python3 scripts/storyboards.py check
    python3 scripts/storyboards.py gallery --output /tmp/storyboards

Edit data/storyboards.json, then generate. Clean SVGs and source snapshots live
in the existing version store. Layout/lettering guides are review-only layers.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import math
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import panelart
import panels
import crossref
import textimage
import panel_layout
import svg_components

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/storyboards.json'
LIBRARY = ROOT / 'data/storyboard-assets.json'
VERSION = 'storyboard-svg-2'
W, H = textimage.PANEL_SIZE


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def load():
    return json.loads(DATA.read_text()) if DATA.exists() else {'version': 1, 'scenes': {}}


def source_bodies():
    scripts = panels.read_scripts().values()
    # References are a later renderer's citation pool, not visual composition or
    # lettering. Citation-only edits must not require hundreds of identical drawings.
    sources = {f'{page.id}-{section.index:02d}': crossref.without_panel_references(section.body)
               for page in scripts for section in page.sections}
    # A grouped run is one reader image, not nine independently numbered boards.
    # Snapshot the entire grouped script so provenance and page-note drift also
    # require review; use the shared parser's grouped-run identity.
    for page in scripts:
        if page.grouped and not page.sections:
            sources[f'{page.id}-01'] = crossref.without_panel_references(page.text)
    return sources


def relocate(data, resolver, rewrite_source):
    """Called inside the identity tools' plans; never performs a write itself."""
    result = dict(data, scenes={})
    for key, scene in data['scenes'].items():
        page, index = map(int, key.split('-'))
        pair = resolver(page, index)
        if pair is not None:
            updated = dict(scene, source=rewrite_source(scene['source'], page, index))
            result['scenes'][f'{pair[0]:03d}-{pair[1]:02d}'] = updated
    return result


def box(value):
    return (len(value) == 4 and all(isinstance(v, (int, float)) and
            not isinstance(v, bool) and math.isfinite(v) for v in value) and
            value[0] >= 0 and value[1] >= 0 and value[2] > 0 and value[3] > 0 and
            value[0] + value[2] <= 1.000001 and value[1] + value[3] <= 1.000001)


def overlap(a, b):
    return (min(a[0]+a[2], b[0]+b[2]) > max(a[0], b[0]) + .001 and
            min(a[1]+a[3], b[1]+b[3]) > max(a[1], b[1]) + .001)


def place_manual(scene, fields, width, height):
    import letterpress
    placed, remaining = [], []
    specs = scene.get('lettering', [])
    for i, (field, text) in enumerate(fields):
        if i >= len(specs):
            remaining.append((field, text))
            continue
        x, y, w, h = specs[i]['box']
        x, y, w, h = x*width, y*height, w*width, h*height
        spec = specs[i]
        flow = textimage.flow(text, w-32, h-52, min_size=12, max_size=spec.get('max_size', 24))
        role = spec.get('role', 'interface')
        placed.append(letterpress.Placed(role, f'manual-{i}',
                      '' if role == 'plain' else letterpress.speaker_of(field), x, y, w, h, flow.size,
                      flow.leading, flow.lines, flow.truncated))
    return placed, remaining


def lettering(key, scene):
    import letterpress
    page, index = key.split('-')
    W, H = panel_layout.target(key)
    record = letterpress.load_slots()
    fields = textimage.lettering_fields(page).get(int(index), [])
    if scene.get('lettering_mode') == 'manual':
        placed, manual = [], fields
    else:
        placed, manual = letterpress.layout_panel(fields, record, W, H)
    extra, manual = place_manual(scene, manual, W, H)
    return placed + extra, manual, record


def validate(data):
    assets = json.loads(LIBRARY.read_text())['assets']
    sources = source_bodies()
    errors = svg_components.Library().errors()
    if data.get('version') != 1:
        errors.append('unsupported scene schema')
    for key, scene in data['scenes'].items():
        if scene.get('lettering_mode', 'slots') not in ('slots', 'manual'):
            errors.append(f'{key}: unknown lettering mode')
        if key not in sources:
            errors.append(f'{key}: nonexistent panel')
            continue
        W, H = panel_layout.target(key)
        if scene.get('source') != sources[key]:
            errors.append(f'{key}: script changed; review composition and refresh its source snapshot')
        for node in scene['nodes']:
            if node['asset'] not in assets or not box(node['box']):
                errors.append(f'{key}: invalid asset/box: {node}')
            if node['color'] not in data['palette']:
                errors.append(f'{key}: unknown palette color')
        for item in scene.get('lettering', []):
            if not box(item['box']):
                errors.append(f'{key}: invalid lettering box')
            if item.get('role', 'interface') not in ('interface', 'plain'):
                errors.append(f'{key}: invalid manual lettering role')
        placed, manual, _ = lettering(key, scene)
        if manual or any(p.truncated for p in placed):
            errors.append(f'{key}: missing or truncated lettering')
        zones = [(p.x/W, p.y/H, p.w/W, p.h/H) for p in placed]
        for i, a in enumerate(zones):
            if any(overlap(a, b) for b in zones[i+1:]):
                errors.append(f'{key}: lettering boxes overlap')
        for node in scene['nodes']:
            if node.get('focus') and any(overlap(node['box'], z) for z in zones):
                errors.append(f'{key}: focal subject overlaps lettering: {node["asset"]}')
            if 'label_box' in node:
                if not box(node['label_box']):
                    errors.append(f'{key}: invalid label box')
                else:
                    lx, ly, lw, lh = node['label_box']
                    flow = textimage.flow(node.get('label', ''), lw*W, lh*H, min_size=12, max_size=node.get('label_size', 20))
                    if flow.truncated or any(overlap(node['label_box'], z) for z in zones):
                        errors.append(f'{key}: label does not fit clear of lettering: {node.get("label")}')
    return errors


def render(scene, data, *, layout=False, size=None, component_library=None):
    W, H = size or textimage.PANEL_SIZE
    library = json.loads(LIBRARY.read_text())
    palette = data['palette']
    def asset_key(node):
        return node['asset'] + ('@' + node['asset_version'] if node.get('asset_version') else '')
    used_assets = {}
    for node in scene['nodes']:
        if node.get('asset_version'):
            component_library = component_library or svg_components.Library()
            fragment = component_library.resolve(node['asset'], node['asset_version'])
        else:
            fragment = library['assets'][node['asset']]
        used_assets[asset_key(node)] = fragment
    snapshot = {'renderer': VERSION, 'scene': scene, 'assets': used_assets, 'palette': palette}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             '<title>' + html.escape(scene['title']) + '</title>',
             '<desc>' + html.escape(scene['intent']) + '</desc>',
             '<metadata>' + html.escape(encoded(snapshot)) + '</metadata>',
             f'<rect width="{W}" height="{H}" fill="{palette[scene["background"]]}"/>']
    for node_index, node in enumerate(scene['nodes']):
        x,y,w,h = node['box']; x,y,w,h = x*W,y*H,w*W,h*H
        color = palette[node['color']]
        if layout:
            parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="none" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<text x="{x+8:g}" y="{y+24:g}" fill="{color}" font-family="sans-serif" font-size="20">{html.escape(node["asset"])}</text>')
        else:
            transform = 'translate(100 0) scale(-1 1)' if node.get('flip') else ''
            parts.append(f'<g transform="translate({x:g} {y:g}) scale({w/100:g} {h/100:g})" color="{color}"><g transform="{transform}">' + svg_components.scope_ids(used_assets[asset_key(node)], f'node-{node_index}-') + '</g></g>')
        if node.get('label'):
            if 'label_box' in node:
                lx, ly, lw, lh = node['label_box']
                flow = textimage.flow(node['label'], lw*W, lh*H, min_size=12, max_size=node.get('label_size', 20))
                for i, line in enumerate(flow.lines):
                    parts.append(f'<text x="{(lx+lw/2)*W:g}" y="{ly*H+flow.size+i*flow.leading:g}" text-anchor="middle" fill="{palette["paper"]}" font-size="{flow.size:g}" font-family="sans-serif">{html.escape(line)}</text>')
            else:
                parts.append(f'<text x="{x+w/2:g}" y="{y+h+24:g}" text-anchor="middle" fill="{palette["paper"]}" font-size="20" font-family="monospace">{html.escape(node["label"])}</text>')
    border = ' stroke-dasharray="18 10"' if scene.get('reconstructed') else ''
    if scene.get('border', 'default') != 'none':
        parts.append(f'<rect x="3" y="3" width="{W-6}" height="{H-6}" fill="none" stroke="{palette["steel"]}" stroke-width="4"{border}/>')
    parts.append('</svg>')
    return ''.join(parts)


def svg_uri(svg):
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()


def preview(key, scene, data, mode='lettered'):
    import letterpress
    W, H = panel_layout.target(key)
    drawing = render(scene, data, layout=mode == 'layout', size=(W,H))
    if mode == 'clean' or mode == 'layout':
        return drawing
    placed, _, record = lettering(key, scene)
    return letterpress.svg_panel(placed, record, W, H, art_href=svg_uri(drawing))


def check(data):
    errors = validate(data)
    variants = panelart.load(refresh=True)
    for key, scene in data['scenes'].items():
        W, H = panel_layout.target(key)
        svg = render(scene, data, size=(W,H)).encode()
        ET.fromstring(svg)
        if svg != render(scene, data, size=(W,H)).encode():
            errors.append(f'{key}: nondeterministic renderer')
        if not any(v.path.is_file() and v.provider == 'storyboard-svg' and
                   v.path.read_bytes() == svg for v in variants.get(key, [])):
            errors.append(f'{key}: current board missing; run generate')
    # Exercise policy boundaries without reading or changing artwork.
    from dataclasses import replace
    a = panelart.Variant('001-01', 'v01', '', stage='refined')
    b = panelart.Variant('001-01', 'v02', '', stage='storyboard')
    assert panelart.pick([a, b]) == a
    assert panelart.pick([a, replace(b, status='chosen')]) == a
    assert panelart.pick([replace(a, status='chosen'), replace(a, variant='v03')]).variant == 'v01'
    assert panelart.pick([a, replace(a, variant='v03')]).variant == 'v03'
    assert panelart.pick([a, replace(b, stage='final')]) == replace(b, stage='final')
    assert panelart.pick([replace(a, status='rejected'), b]) == b
    assert panelart.pick([replace(b, status='rejected')]) is None
    for pair in ((3, 2), None):
        moved = relocate({'scenes': {'001-01': {'source': 'source'}}},
                         lambda p, i: pair, lambda s, p, i: s)
        assert list(moved['scenes']) == (['003-02'] if pair else [])
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    import produce
    import letterpress
    # Reader and workshop must agree when every field is manually placed, rather
    # than silently duplicating the fields the old slot convention already placed.
    sample = {'lettering_mode': 'manual', 'lettering': [
        {'box': [.05, .05, .9, .2]},
        {'box': [.05, .7, .9, .2], 'role': 'plain', 'max_size': 40}]}
    with patch.object(textimage, 'lettering_fields', return_value={1: [
            ('Screen / system text', 'First'), ('Dialogue — CURT', 'Second')]}), \
         patch('storyboards.load', return_value={'scenes': {'001-01': sample}}):
        workshop, remaining, record = lettering('001-01', sample)
        reader, reader_remaining = letterpress.panel_layout('001', 1, record)
        assert not remaining and not reader_remaining and workshop == reader
        assert [tuple(p.lines) for p in reader] == [('First',), ('Second',)]
        assert reader[1].role == 'plain' and not reader[1].header
        assert 'Second' in letterpress.svg_panel(reader, record, W, H)
        from contextlib import redirect_stdout
        from io import StringIO
        from types import SimpleNamespace
        one_slot = [SimpleNamespace(id='001', panels=[SimpleNamespace(index=1)])]
        with patch.object(textimage, 'book_scripts', return_value=one_slot):
            output = StringIO()
            with redirect_stdout(output):
                assert letterpress.cmd_audit(None) == 0
            assert '100.0% of 2' in output.getvalue()
            for layout in [(reader[:1], [('Dialogue — CURT', 'Second')]),
                           ([replace(reader[0], truncated=True)], [])]:
                with patch.object(letterpress, 'panel_layout', return_value=layout), \
                     redirect_stdout(StringIO()):
                    assert letterpress.cmd_audit(None) == 1
    with TemporaryDirectory() as directory:
        art = Path(directory) / 'board.svg'
        art.write_text('<svg/>')
        board = panelart.Variant('001-01', 'v99', str(art), stage='storyboard', status='chosen')
        with patch.object(panelart, '_CACHE', {'001-01': [board]}):
            assert panelart.resolve('001', 1) == art
            assert produce.Slot('001', 1, 'prologue', 'incident').art() is None
        finished = replace(board, variant='v01', stage='final', status='candidate')
        with patch.object(panelart, '_CACHE', {'001-01': [board, finished]}):
            assert produce.Slot('001', 1, 'prologue', 'incident').art() == art
        table = Path(directory) / 'art.tsv'
        panelart.write_table([board, finished], table)
        assert panelart.read_table(table) == [finished, board]
        with patch.object(panelart, 'discover', return_value=[replace(board, status='candidate', stage='refined')]):
            refreshed, _, _ = panelart.scan(table)
            assert refreshed[0].status == 'chosen' and refreshed[0].stage == 'storyboard'
        with patch.object(panelart, '_CACHE', {'001-01': [replace(board, file=str(art)+'-missing')]}):
            assert panelart.resolve('001', 1) is None
            assert panelart.selected('001', 1) is None
        missing = replace(finished, file=str(art)+'-missing')
        with patch.object(panelart, '_CACHE', {'001-01': [board, missing]}):
            assert panelart.selected('001', 1) == board
            assert panelart.alternates('001', 1) == []
        table.write_text('panel\tvariant\tfile\tstatus\n001-01\tv01\tmissing.webp\tcandidate\n')
        assert panelart.read_table(table)[0].stage == 'refined'
    return errors


def generate(data):
    problems = validate(data)
    if problems:
        raise SystemExit('\n'.join(problems))
    started = time.perf_counter()
    variants = panelart.load(refresh=True)
    added = 0
    for key, scene in data['scenes'].items():
        W, H = panel_layout.target(key)
        svg = render(scene, data, size=(W,H)).encode()
        if any(v.path.is_file() and v.provider == 'storyboard-svg' and
               v.path.read_bytes() == svg for v in variants.get(key, [])):
            continue
        panelart.store(key, svg, '.svg', provider='storyboard-svg')
        added += 1
    rows, _, _ = panelart.scan()
    panelart.write_table(rows)
    panelart.load(refresh=True)
    print(f'{len(data["scenes"])} boards; {added} new versions; {time.perf_counter()-started:.3f}s')


def gallery(output, *, components_url=None):
    data = load()
    output.mkdir(parents=True, exist_ok=True)
    scenes = data['scenes']
    cards = []
    for key, scene in scenes.items():
        W, H = panel_layout.target(key)
        modes = []
        for mode in ('layout', 'clean', 'lettered', 'current'):
            name = f'{key}-{mode}.svg'
            svg = preview(key, scene, data, mode)
            if mode == 'current':
                import letterpress
                page, index = key.split('-')
                art = panelart.resolve(page, int(index))
                if art:
                    placed, _, record = lettering(key, scene)
                    svg = letterpress.svg_panel(placed, record, W, H, art=art)
            (output/name).write_text(svg)
            modes.append(f'<img class="{mode}" src="{name}" alt="{html.escape(scene["title"])} — {mode}">')
        (output/f'{key}.json').write_text(encoded(scene))
        placed, _, _ = lettering(key, scene)
        zones = ''.join(f'<rect x="{p.x}" y="{p.y}" width="{p.w}" height="{p.h}"/>' for p in placed)
        zones += ''.join(f'<ellipse cx="{(n["box"][0]+n["box"][2]/2)*W}" cy="{(n["box"][1]+n["box"][3]/2)*H}" rx="30" ry="30"/>' for n in scene['nodes'] if n.get('focus'))
        guides = f'<svg class="guides" viewBox="0 0 {W} {H}" fill="none" stroke="#ffb844" stroke-width="4" stroke-dasharray="10 8">{zones}</svg>'
        cards.append(f'<article id="p{key}"><h2>{key} · {html.escape(scene["title"])}</h2><div class="image">' + ''.join(modes) + guides + f'</div><p>{html.escape(scene["intent"])}</p><p><a href="{key}-clean.svg">Clean reference</a> · <a href="{key}.json">Scene record</a></p></article>')
    # Entire neighboring pages, paired by physical parity, with text fallback.
    spreads = []
    script_map = {s.id:s for s in textimage.book_scripts()}
    starts = sorted({int(k[:3]) // 2 * 2 for k in scenes})
    for start in starts:
        pages_html = []
        for page in (start, start+1):
            pid = f'{page:03d}'
            if pid not in script_map:
                pages_html.append('<div class="sheet"><p>Unnumbered facing page</p></div>')
                continue
            cells = []
            for panel in script_map[pid].panels:
                key = f'{pid}-{panel.index:02d}'
                if key in scenes:
                    svg = preview(key, scenes[key], data)
                else:
                    svg = textimage.text_image(panel.text, W, H, label=key, footer='TEXT FALLBACK')
                cells.append(f'<figure style="{panel_layout.style(len(script_map[pid].panels), panel.index)}"><img src="{svg_uri(svg)}" alt="Panel {key}"><figcaption>{key}</figcaption></figure>')
            pages_html.append(f'<div class="sheet"><h3>{pid} · {"Recto" if page%2 else "Verso"}</h3><div class="pagepanels" style="aspect-ratio:{panel_layout.load()["page"][0]}/{panel_layout.load()["page"][1]}">' + ''.join(cells) + '</div></div>')
        spreads.append('<div class="spread">'+''.join(pages_html)+'</div>')
    document = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Storyboard workshop</title><style>
    *{box-sizing:border-box}body{margin:0;background:#101214;color:#E7E0D0;font:16px/1.5 system-ui}header,main{max-width:1500px;margin:auto;padding:24px}h1{font-size:38px;margin:0}h2{font-size:18px;scroll-margin-top:100px}p{max-width:85ch}a{color:#bdd4df}nav{display:flex;gap:20px;flex-wrap:wrap;position:sticky;top:0;background:#202326;padding:18px 24px;z-index:2}button,select{font:inherit;padding:6px}section.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}article{background:#202326;padding:18px;border:1px solid #5E737B;border-radius:8px}.image{position:relative}.image img{width:100%;display:none}body[data-mode=lettered] .lettered,body[data-mode=clean] .clean,body[data-mode=layout] .layout,body[data-mode=current] .current{display:block}.guides{display:none;position:absolute;inset:0;width:100%;height:100%;pointer-events:none}body.show-guides .guides{display:block}.spread{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:24px 0}.sheet{background:#E7E0D0;color:#101214;padding:18px}.pagepanels{position:relative}.pagepanels figure{position:absolute}.pagepanels figure img{height:100%;object-fit:contain}.pagepanels figcaption{position:absolute;bottom:0;background:#e7e0d0;padding:0 3px}figure{margin:0}figure img{width:100%;display:block}figcaption{font-size:11px}@media(max-width:750px){section.cards{grid-template-columns:1fr}.spread{gap:8px}.sheet{padding:8px}}
    </style><body data-mode="lettered"><header><h1>Storyboard workshop</h1><p>Composition before rendering. Reconstructed scenes use broken borders. These are provisional compositions, not documentary images or likeness studies.</p></header><nav><label>View <select id="mode"><option value="lettered">With lettering</option><option value="clean">Clean storyboard</option><option value="layout">Layout boxes</option><option value="current">Current book selection</option></select></label><label><input id="guides" type="checkbox"> Lettering zones & focal points</label><a href="#spreads">Page spreads</a>COMPONENT_NAV</nav><main><section class="cards">'''
    document += ''.join(cards) + '</section><h2 id="spreads">Page spreads</h2><p>Shared reader geometry, with the complete panel sequence and physical recto/verso pairing.</p>' + ''.join(spreads)
    document += '''</main><script>document.getElementById('mode').onchange=e=>document.body.dataset.mode=e.target.value;document.getElementById('guides').onchange=e=>document.body.classList.toggle('show-guides',e.target.checked);</script></body></html>'''
    document = document.replace('COMPONENT_NAV', f'<a href="{html.escape(components_url, quote=True)}">Component palette</a>' if components_url else '')
    (output/'index.html').write_text(document)


def check_built(output):
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit
    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for name, value in attrs:
                if name not in ('src', 'href') or not value:
                    continue
                url = urlsplit(value)
                if url.scheme or not url.path:
                    continue
                target = output / unquote(url.path)
                if target.is_dir():
                    target = target / 'index.html'
                assert target.is_file(), value
    Links().feed((output / 'index.html').read_text())
    for key, scene in load()['scenes'].items():
        W, H = panel_layout.target(key)
        assert json.loads((output / f'{key}.json').read_text()) == scene
        for mode in ('layout', 'clean', 'lettered', 'current'):
            root = ET.parse(output / f'{key}-{mode}.svg').getroot()
            assert root.get('viewBox') == f'0 0 {W} {H}'
    print('Built storyboard links, scene exports, and four preview modes checked.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['generate', 'check', 'gallery'])
    parser.add_argument('--built', action='store_true', help='also check the published workshop')
    parser.add_argument('--complete', action='store_true', help='require a scene for every reader image slot')
    parser.add_argument('--output', type=Path, default=ROOT/'256t/storyboards')
    args = parser.parse_args()
    data = load()
    if args.command == 'generate':
        generate(data)
    elif args.command == 'gallery':
        gallery(args.output)
        print(args.output/'index.html')
    else:
        errors = check(data)
        if args.complete:
            slots = {f'{p.id}-{s.index:02d}' for p in textimage.book_scripts() for s in p.panels}
            errors.extend(f'{key}: missing reader-slot storyboard' for key in sorted(slots - data['scenes'].keys()))
        if errors:
            raise SystemExit('\n'.join(errors))
        if args.built:
            check_built(ROOT / 'docs/storyboards')
        print(f'Storyboards checked: {len(data["scenes"])} current boards; geometry, lettering, version policy and relocation passed.')


if __name__ == '__main__':
    main()
