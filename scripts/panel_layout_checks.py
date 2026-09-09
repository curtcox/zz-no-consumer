"""Offline geometry and artwork boundary regression checks (standard library)."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import struct


def run():
    import panel_layout as p
    import panelart
    def fails(fn):
        try: fn()
        except ValueError: return
        raise AssertionError('Invalid fit accepted')
    for count in range(1,10):
        rects=p.rectangles(count)
        assert len(rects)==count
        for x,y,w,h in rects:
            assert x>=0 and y>=0 and w>0 and h>0
    fails(lambda:p.require_size((1200,800),(1200,1200)))
    fails(lambda:p.require_size((12,8),(1200,800)))
    p.require_size((1536,1024),(1200,800))
    with TemporaryDirectory() as folder:
        root=Path(folder); source=root/'source.svg'
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800"><rect width="1200" height="800"/></svg>')
        original=source.read_bytes()
        with patch.object(p,'ROOT',root):
            svg,receipt=p.crop_svg(source,[200,0,1000,800],(800,800),'Subject and lettering clearance reviewed')
            out=root/'fit.svg';out.write_text(svg)
            p.require(out,(800,800))
            assert receipt['crop']==[200,0,1000,800]
            assert source.read_bytes()==original
            fails(lambda:p.crop_svg(source,[0,0,1200,800],(800,800),'Wrong aspect'))
            fails(lambda:p.crop_svg(source,[-1,0,799,800],(800,800),'Outside'))
            fails(lambda:p.crop_svg(source,[200,0,1000,800],(800,800),''))
        invalid=p.load(); invalid['templates']['2'][1]=invalid['templates']['2'][0]
        config=root/'layouts.json';config.write_text(json.dumps(invalid))
        with patch.object(p,'DATA',config): fails(p.load)
        # Version allocation must include rejected variants and legacy flat files,
        # but must not scan or decode the entire artwork store.
        art=root/'panels'; art.mkdir(); (art/'001-01.webp').write_bytes(b'legacy')
        (art/'001-01').mkdir(); (art/'001-01/v07-storyboard-svg.svg').write_text('<svg/>')
        with patch.object(panelart,'ART_DIR',art),patch.object(panelart,'discover',side_effect=AssertionError('global scan')):
            assert panelart.next_number('001-01')==8
            assert panelart.next_number('002-01')==1
    print('Panel layout: geometry, aspect, resolution, crop preservation and version allocation fixtures passed.')
