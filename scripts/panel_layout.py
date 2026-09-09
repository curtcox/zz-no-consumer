#!/usr/bin/env python3
"""Shared page geometry and strict, non-destructive panel fitting.

check validates selected sources; check --built also validates published canvases.
fit PANEL SOURCE --box L T R B --note TEXT stores a reviewed SVG crop as a
new candidate, with immutable source hash and crop receipt. Coordinates use the
source's native pixels. Choose it with panelart.py after visual review.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/panel-layouts.json'


def load():
    data = json.loads(DATA.read_text())
    if data['version'] != 1:
        raise ValueError('Unsupported panel layout version')
    pw, ph = data['page']
    if pw <= 0 or ph <= 0:
        raise ValueError('Invalid page dimensions')
    for count, rects in data['templates'].items():
        if len(rects) != int(count):
            raise ValueError(f'Layout {count}: wrong rectangle count')
        for i, (x,y,w,h) in enumerate(rects):
            if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (x,y,w,h)) or any(int(v)!=v for v in (x,y,w,h)) or not (x>=0 and y>=0 and w>0 and h>0 and x+w<=pw and y+h<=ph):
                raise ValueError(f'Layout {count}: invalid rectangle {i+1}')
            for X,Y,W,H in rects[:i]:
                if min(x+w,X+W)>max(x,X) and min(y+h,Y+H)>max(y,Y):
                    raise ValueError(f'Layout {count}: overlapping rectangles')
    return data


def rectangles(count):
    try:
        return load()['templates'][str(count)]
    except KeyError:
        raise ValueError(f'No page layout for {count} reader slots') from None


def size(page, index):
    import textimage
    rects = rectangles(len(textimage.page_script(str(page).zfill(3)).panels))
    if not 1 <= int(index) <= len(rects):
        raise ValueError(f'{page}-{index}: no such reader slot')
    rect = rects[int(index)-1]
    w,h = int(rect[2]),int(rect[3])
    divisor = math.gcd(w,h)
    rw,rh = w//divisor,h//divisor
    scale = math.ceil(1200/rw)
    return rw*scale,rh*scale


def target(key):
    return size(*key.split('-'))


def style(count, index):
    x,y,w,h = rectangles(count)[index-1]
    pw,ph = load()['page']
    return f'left:{100*x/pw:.10g}%;top:{100*y/ph:.10g}%;width:{100*w/pw:.10g}%;height:{100*h/ph:.10g}%'


def dimensions(path):
    """Read supported image headers without optional imaging dependencies."""
    raw = Path(path).read_bytes()
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return struct.unpack('>II',raw[16:24])
    if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        pos=12
        while pos+8 <= len(raw):
            kind=raw[pos:pos+4]; n=int.from_bytes(raw[pos+4:pos+8],'little'); b=raw[pos+8:pos+8+n]
            if kind==b'VP8X': return 1+int.from_bytes(b[4:7],'little'),1+int.from_bytes(b[7:10],'little')
            if kind==b'VP8 ': return struct.unpack('<HH',b[6:10])[0]&16383,struct.unpack('<HH',b[6:10])[1]&16383
            if kind==b'VP8L':
                bits=int.from_bytes(b[1:5],'little'); return (bits&16383)+1,((bits>>14)&16383)+1
            pos+=8+n+(n%2)
    if raw[:2] == b'\xff\xd8':
        pos=2
        while pos < len(raw):
            if raw[pos]!=255: break
            while raw[pos]==255: pos+=1
            marker=raw[pos]; pos+=1
            n=int.from_bytes(raw[pos:pos+2],'big')
            if marker in (192,193,194): return int.from_bytes(raw[pos+5:pos+7],'big'),int.from_bytes(raw[pos+3:pos+5],'big')
            pos+=n
    if Path(path).suffix.lower()=='.svg':
        node=ET.fromstring(raw)
        return float(node.attrib['width']),float(node.attrib['height'])
    raise ValueError(f'Cannot read image dimensions: {path}')


def require_size(actual, expected, label='Panel'):
    w,h=actual; W,H=expected
    if min(w,h)<=0 or not math.isclose(w*H,h*W,rel_tol=1e-9):
        raise ValueError(f'{label}: {w:g}x{h:g} does not match target {W}x{H}; review a crop or regenerate')
    if w<W/2 or h<H/2:
        raise ValueError(f'{label}: {w:g}x{h:g} is below minimum resolution {W/2:g}x{H/2:g}')


def require(path, expected):
    require_size(dimensions(path), expected, str(path))


def crop_svg(source, box, expected, note):
    sw,sh=dimensions(source); l,t,r,b=box; W,H=expected
    if not note.strip() or not all(math.isfinite(v) for v in box) or not (0<=l<r<=sw and 0<=t<b<=sh):
        raise ValueError('A reviewed crop inside the source and a review note are required')
    # Vector inputs have no minimum pixel resolution; raster derivatives must not upscale.
    require_size((r-l,b-t), (W,H) if source.suffix!='.svg' else (W/min(W,H),H/min(W,H)), str(source))
    raw=source.read_bytes()
    receipt={'source':str(source.relative_to(ROOT)), 'source_sha256':hashlib.sha256(raw).hexdigest(),
             'crop':box,'target':list(expected),'review_note':note}
    kind={'svg':'svg+xml','png':'png','webp':'webp','jpg':'jpeg','jpeg':'jpeg'}[source.suffix[1:]]
    uri=f'data:image/{kind};base64,'+base64.b64encode(raw).decode()
    metadata=__import__('html').escape(json.dumps(receipt,sort_keys=True))
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
         f'<metadata>{metadata}</metadata><svg width="{W}" height="{H}" viewBox="{l} {t} {r-l} {b-t}" overflow="hidden">'
         f'<image width="{sw}" height="{sh}" href="{uri}"/></svg></svg>')
    return svg,receipt


def check_html():
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit
    errors=[]
    class Panels(HTMLParser):
        def __init__(self,path):
            super().__init__(); self.path=path; self.count=0; self.index=0; self.depth=0
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='div' and self.depth:
                self.depth += 1
            if tag=='div' and 'page-art' in attrs.get('class','').split():
                self.depth = 1
                if attrs.get('data-panel-layout') != '2':
                    errors.append(f'{self.path}: missing layout version')
                self.count=int(attrs['data-panels']); self.index=0
                pw,ph=load()['page']
                if attrs.get('style')!=f'aspect-ratio:{pw}/{ph}':
                    errors.append(f'{self.path}: page ratio differs from layout')
            if tag=='img' and 'page-art__panel' in attrs.get('class','').split():
                self.index+=1
                if self.index > self.count:
                    errors.append(f'{self.path}: excess panel image')
                    return
                if attrs.get('style')!=style(self.count,self.index):
                    errors.append(f'{self.path}: panel rectangle differs from layout')
                source=(self.path.parent/unquote(urlsplit(attrs['src']).path)).resolve()
                w,h=dimensions(source)
                _,_,W,H=rectangles(self.count)[self.index-1]
                if not math.isclose(w*H,h*W,rel_tol=1e-9):
                    errors.append(f'{self.path}: panel image does not fill its rectangle')
        def handle_endtag(self,tag):
            if tag=='div' and self.depth:
                self.depth -= 1
                if self.depth==0 and self.index!=self.count:
                    errors.append(f'{self.path}: expected {self.count} panels, found {self.index}')
    for path in (ROOT/'docs').rglob('*.html'):
        document=path.read_text()
        if 'class="page-art' in document: Panels(path).feed(document)
    return errors


def check(built=False):
    import textimage, panelart
    import panel_layout_checks
    panel_layout_checks.run()
    errors=[]
    load()
    for page in textimage.book_scripts():
        for panel in page.panels:
            key=f'{page.id}-{panel.index:02d}'; expected=target(key)
            art=panelart.resolve(page.id,panel.index)
            try:
                if art: require(art,expected)
                if built:
                    path=ROOT/'docs/assets'/('lettered' if art else 'placeholders/panels')/f'{key}.svg'
                    require(path,expected)
            except (ValueError,OSError) as exc: errors.append(str(exc))
    if built:
        errors.extend(check_html())
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    c=commands.add_parser('check'); c.add_argument('--built',action='store_true')
    f=commands.add_parser('fit'); f.add_argument('panel'); f.add_argument('source',type=Path)
    f.add_argument('--box',nargs=4,type=float,required=True); f.add_argument('--note',required=True)
    args=parser.parse_args()
    if args.command=='check':
        errors=check(args.built)
        if errors: raise SystemExit('\n'.join(errors))
        print('Panel geometry and selected image fit checked.')
    else:
        import panelart
        svg,receipt=crop_svg(args.source.resolve(),args.box,target(args.panel),args.note)
        out=panelart.store(args.panel,svg.encode(),'.svg',provider='panel-fit')
        out.with_suffix('.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(out)

if __name__=='__main__': main()
