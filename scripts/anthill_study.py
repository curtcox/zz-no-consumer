#!/usr/bin/env python3
"""Build/check a static anthill composition study, independent of reader selection.

Uses canonical storyboard scenes, panel geometry and immutable fog studies. Selection by
page title avoids a second page-key registry; identities and rectangles resolve at build.
The cover borrows fog imagery as authored texture, never as a wiki evidence-state model.
"""
from __future__ import annotations
import argparse
import base64
import json
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET
import book_metadata
import panel_layout
import storyboards
import textimage

ROOT = Path(__file__).resolve().parents[1]
FOG = ROOT / 'assets/knowledge-maps/fog-v1'
# Titles identify existing scenes. No independently maintained page or panel numbers.
CASES = [('Published', True), ('Another Agent', True),
         ('The End of the Alphabet', False)]
MAPS = ['w3-010-reader-hint.svg', 'w3-010-responders-hint.svg',
        'w3-039-before-reader.svg', 'w3-039-after-reader.svg']
NS = '{http://www.w3.org/2000/svg}'


def uri(content, mime='image/svg+xml'):
    if isinstance(content, str):
        content = content.encode()
    return f'data:{mime};base64,' + base64.b64encode(content).decode()


def pages():
    source = textimage.book_scripts()
    for title, _ in CASES:
        if sum(p.title == title for p in source) != 1:
            raise ValueError(f'Study selector must resolve exactly once: {title}')
    return {p.title: p for p in source}


def ant(x, y, angle=0, size=34):
    shape = json.loads(storyboards.LIBRARY.read_text())['assets']['ant']
    return (f'<g transform="translate({x} {y}) rotate({angle}) scale({size/100}) '
            f'translate(-50 -50)" color="#101214">{shape}</g>')


def placements(rects, enabled):
    """A short marginal route, anchored to the first panel; no panel crossings."""
    if not enabled:
        return []
    x, y, _, h = rects[0]
    poses = [(x / 2, y + h * t, -75 + 5*i, 34) for i, t in enumerate((.20,.27,.34,.41,.48))]
    # First horizontal gutter, anchored to the top panel. The five-panel cases have
    # sixty page units here; check() rejects any collision if that geometry changes.
    pw = rects[0][2]
    poses.extend((x + pw*t, y+h+30, 5, 30) for t in (.28,.32,.36))
    return poses


def page_svg(page, data, enabled):
    w, h = panel_layout.load()['page']
    rects = panel_layout.rectangles(len(page.panels))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
             f'<title>{escape(page.title)} — authored ant placement study</title>',
             '<rect width="100%" height="100%" fill="#E7E0D0"/>']
    for index, (x,y,pw,ph) in enumerate(rects, 1):
        key = f'{page.id}-{index:02d}'
        art = storyboards.preview(key, data['scenes'][key], data)
        parts.append(f'<image x="{x}" y="{y}" width="{pw}" height="{ph}" href="{uri(art)}"/>')
    parts.append('<g aria-hidden="true" style="pointer-events:none">')
    parts.extend(ant(*pose) for pose in placements(rects, enabled))
    parts.append('</g></svg>')
    return ''.join(parts)


def cover():
    # Extract the raster, not the proposition/legend layer. This is labelled cover texture,
    # not an alternate map. Unmodified, fully labelled maps are displayed below the cover.
    node = ET.fromstring((FOG / MAPS[0]).read_bytes()).find(f'.//{NS}image')
    texture = node.attrib['href']
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1100">
<title>{escape(book_metadata.TITLE)} — cover study</title>
<desc>Two separate surfaces borrow existing fog-study texture. This is authored cover art, not a map of the wiki or a measure of record completeness. No route connects the surfaces.</desc>
<defs><clipPath id="hills"><path d="M70 800Q140 750 175 565Q235 470 300 570Q342 745 400 800Z M505 800Q560 746 609 621Q675 503 721 628Q765 750 835 800Z"/></clipPath></defs>
<rect width="900" height="1100" fill="#101214"/>
<text x="65" y="100" fill="#CEC5B3" font-family="monospace" font-size="16" letter-spacing="3">A DOCUMENTARY GRAPHIC NOVEL</text>
<g fill="#E7E0D0" font-family="Georgia,serif" font-size="94"><text x="60" y="240">The Two</text><text x="60" y="342">Anthill</text><text x="60" y="444">Problem</text></g>
<g clip-path="url(#hills)"><image x="60" y="480" width="790" height="350" preserveAspectRatio="none" href="{texture}"/></g>
<path d="M70 800Q140 750 175 565Q235 470 300 570Q342 745 400 800 M505 800Q560 746 609 621Q675 503 721 628Q765 750 835 800" fill="none" stroke="#CEC5B3" stroke-opacity=".6" stroke-width="2"/>
<path d="M207 800Q229 746 251 800M650 800Q669 763 688 800" fill="#101214"/>
<text x="65" y="930" fill="#E7E0D0" font-family="Georgia,serif" font-size="30">Curt Cox</text>
<text x="65" y="1000" fill="#CEC5B3" font-family="monospace" font-size="15">TWO INCIDENTS. AN INCOMPLETE VIEW.</text>
</svg>'''


def build(output):
    data = storyboards.load()
    lookup = pages()
    output.mkdir(parents=True, exist_ok=True)
    cards=[]
    for title, enabled in CASES:
        page=lookup[title]
        label=f'{page.id} · {title}'
        svg=page_svg(page,data,enabled)
        cards.append(f'<article><h3>{escape(label)}</h3><p>{"Short routes occupy the outer margin and first horizontal gutter; they do not enter another panel." if enabled else "Excluded: no gutter ants, connecting trail, or barrier. The naming echo remains."}</p><img class="page" src="{uri(svg)}" alt="{escape(label)} — storyboard composition study"/></article>')
    maps=''.join(f'<img src="{uri((FOG/name).read_bytes())}" alt="{escape(ET.fromstring((FOG/name).read_bytes()).find(NS+"title").text)}"/>' for name in MAPS)
    content=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Anthill study — {escape(book_metadata.TITLE)}</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#eee8d8;color:#101214;font:17px/1.6 Georgia,serif}}main{{max-width:1120px;margin:auto;padding:36px 24px}}h1,h2,h3{{line-height:1.15}}h1{{font-size:clamp(36px,6vw,70px);max-width:15ch;margin:.3em 0}}h2{{margin-top:2em}}p{{max-width:72ch}}.eyebrow{{font:12px monospace;letter-spacing:.16em}}.cover{{width:min(100%,540px);display:block}}img{{max-width:100%;display:block}}.maps{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.pages article{{margin:36px 0}}.page{{width:900px;max-width:100%;border:1px solid #a79c84}}label{{display:inline-block;padding:8px 12px;border:1px solid;margin:4px;cursor:pointer}}input{{margin-right:4px}}#narrow:checked~.pages .page{{width:360px}}#hide:checked~.pages{{display:none}}a{{color:inherit}}@media(max-width:680px){{.maps{{grid-template-columns:1fr}}}}@media(prefers-color-scheme:dark){{body{{background:#101214;color:#e7e0d0}}}}
</style><main><p class="eyebrow">9 SEPTEMBER 2026 · COMPOSITION STUDY</p><h1>{escape(book_metadata.TITLE)}</h1>
<p>The two hills name the incidents examined here. Their visibility does not tell us how many incidents went unseen.</p>
<p><a href="../">Return to the book</a></p>
<h2>Cover and surface treatment</h2><img class="cover" src="{uri(cover())}" alt="Cover study: the new title above two separate fog-textured hills"/>
<p>The cover borrows raster terrain from the existing fog study as authored texture. It is not a wiki evidence map. Both hills remain surfaces; the gap asserts neither contact nor isolation. A wiki-specific proposition model remains to be designed before map adoption.</p>
<h2>The records have different limits</h2><p><b>Artifactory:</b> this project has published investigations, not the underlying board dump. <b>Wiki:</b> the stored export contains revisions and events within a declared cut. Neither is a complete view of the event. Brightness and ant density do not encode that difference.</p>
<h2>Viewpoints and re-fog stay intact</h2><p>The original labelled W3 studies are reproduced unchanged: reader and responder at the same reading point, followed by reader states before and after the correction. These are Artifactory studies; neither is relabelled as the wiki.</p><div class="maps">{maps}</div>
<h2>Page composition</h2><p>The creator’s desk carries two small in-picture ants. The flat marginal marks below are a separate study layer. All lettering comes from canonical scripts. No animation or JavaScript is required.</p>
<input type="checkbox" id="narrow"><label for="narrow">360 px page</label><input type="checkbox" id="hide"><label for="hide">Hide image studies</label>
<div class="pages">{''.join(cards)}</div>
<p>At 360 px, gutter-width ants are tiny marks. Enlargement must not obscure lettering or turn density into a measurement. This study does not change ordinary reader overlays or raster selections.</p></main></html>'''
    (output/'index.html').write_text(content)
    (output/'cover.svg').write_text(cover())
    for title, enabled in CASES:
        page=lookup[title]
        (output/f'{page.id}.svg').write_text(page_svg(page,data,enabled))


def check():
    data=storyboards.load(); lookup=pages(); w,h=panel_layout.load()['page']
    for title, enabled in CASES:
        page=lookup[title];rects=panel_layout.rectangles(len(page.panels))
        for x,y,angle,size in placements(rects,enabled):
            r=size/2
            assert r<=x<=w-r and r<=y<=h-r
            assert all(x+r<=X or x-r>=X+W or y+r<=Y or y-r>=Y+H for X,Y,W,H in rects), 'Ant touches protected panel'
        if not enabled:assert not placements(rects,enabled)
        a=page_svg(page,data,enabled);assert a==page_svg(page,data,enabled)
        ET.fromstring(a)
    for name in MAPS:
        root=ET.fromstring((FOG/name).read_bytes())
        meta=json.loads(root.find(NS+'metadata').text)
        assert 'P6' not in meta['fog'] or meta['fog']['P6']=='dark'
        assert root.find(NS+'desc').text
    assert 'refog' in json.loads(ET.fromstring((FOG/MAPS[-1]).read_bytes()).find(NS+'metadata').text)['fog'].values()
    ET.fromstring(cover())
    assert cover()==cover()
    print('Anthill study checked: resolved identities, panel exclusions, deterministic SVG, retained map states and re-fog.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['build','check'])
    parser.add_argument('--out',type=Path,default=ROOT/'256t/anthill-study')
    args=parser.parse_args()
    if args.command=='check':check()
    else:check();build(args.out)
