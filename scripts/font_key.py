"""Semantic lettering fonts shared by scripts, illustrations and the reader."""
from pathlib import Path
import json
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def load():
    return json.loads((ROOT / 'data/font-key.json').read_text())['fonts']

class Text(str):
    """A string carrying source font metadata without changing tuple consumers."""
    def __new__(cls, value, font):
        if font not in load():
            raise ValueError(f'Unknown or missing font key: {font!r}')
        obj = super().__new__(cls, value)
        obj.font = font
        return obj

def family(key):
    return ', '.join("'" + name + "'" if ' ' in name else name for name in load()[key]['family'])

def advance(text, size, key):
    import textimage
    if key in ('machine', 'chronology'):
        return len(text) * size * .61
    return textimage.advance(text, size) * load()[key]['width_scale']

def flow(text, width, height, *, key, min_size=12, max_size=24):
    import textimage
    # Use the same wrapper with font-specific metrics, including fixed-width glyphs.
    return textimage.flow(text, width, height, min_size=min_size, max_size=max_size,
                          measure=lambda value, size, **kw: advance(value, size, key))

def check():
    import textimage
    errors=[]
    count=0
    for path in sorted((ROOT/'content/pages').glob('[0-9][0-9][0-9].md')):
        source=path.read_text()
        for declaration in ('font_key: data/font-key.json', 'font: editorial', 'illustration_font: editorial'):
            if declaration not in source:
                errors.append(f'{path.name}: missing {declaration}')
        pending=None
        for line in source.splitlines():
            if line.startswith('**Font:**'):
                pending=line.split('`')[1] if '`' in line else None
                if pending not in load(): errors.append(f'{path.name}: invalid font {pending}')
            elif line.startswith(('**Caption', '**Dialogue', '**Left dialogue', '**Right dialogue', '**Screen / system text', '**Qualification', '**Dossier tag', '## Persistent banner')):
                count+=1
                if pending not in load(): errors.append(f'{path.name}: missing font for {line}')
                pending=None
            elif line.startswith(('**','## ')):
                pending=None
        # Exercise the real renderer extraction too.
        textimage.lettering_fields(path.stem)
    print(f'Font key: {count} source lettering fields and banners checked.')
    return errors


def regression_checks():
    """Protect source-to-overlay semantics, including manual compositions."""
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    import textimage
    import letterpress
    import storyboards
    errors=[]
    with TemporaryDirectory() as directory:
        path=Path(directory)/'001.md'
        path.write_text('## Panel 1\n\n**Font:** `human`\n\n**Dialogue — CURT:**\n> Keep the distinction.\n\n**Font:** `machine`\n\n**Screen / system text:**\n`iii WWW`\n')
        with patch.object(textimage, 'PAGE_DIR', Path(directory)):
            fields=textimage.lettering_fields('001')[1]
            assert [value.font for _, value in fields] == ['human', 'machine']
            assert [str(value) for _,value in fields] == ['Keep the distinction.', 'iii WWW']
            record=letterpress.load_slots()
            automatic, manual=letterpress.layout_panel(fields, record, 1200, 800)
            assert automatic[0].font == 'machine' and len(manual)==1
            placed, remaining=storyboards.place_manual({'lettering':[{'box':[.05,.7,.9,.2]}]}, manual,1200,800)
            assert placed[0].font=='human' and not remaining
            svg=letterpress.svg_layer(automatic+placed,record,1200,800)
            assert 'data-font-key="machine"' in svg and 'data-font-key="human"' in svg
            path.write_text('## Panel 1\n\n**Caption:**\n> Missing font.\n')
            try: textimage.lettering_fields('001')
            except ValueError: pass
            else: errors.append('Missing source font was accepted')
    assert advance('iii',12,'machine') == advance('WWW',12,'machine')
    for key in load():
        fitted=flow('A longer explanation of the boundary. '*10,350,160,key=key,min_size=12,max_size=24)
        if not fitted.truncated:
            assert all(advance(line,fitted.size,key)<=350.01 for line in fitted.lines)
    return errors
