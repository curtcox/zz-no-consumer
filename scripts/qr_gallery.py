#!/usr/bin/env python3
"""The published gallery of QR codes drawn in ants, and its tracked assets.

Rendering one of these symbols takes seconds to minutes, so the images are not
built by the site builder. They are generated once by `generate`, committed
under `assets/qr-ant/` with a manifest recording what each one measured, and
the builder only lays them out. `check` is what keeps that arrangement honest:
it re-derives every claim the manifest makes about the *code* from `qr_core`,
and verifies every file it names is present and unchanged.

The symbols encode a placeholder that says so in its own text. They are the
length of a real 256t content tag - 103 bytes, the shape the tool was built
for - but they resolve to nothing, and a reader who scans one is told that by
the payload itself rather than by a caption they may not read.

    python3 scripts/qr_gallery.py generate     # slow; rewrites the assets
    python3 scripts/qr_gallery.py check
    python3 scripts/qr_gallery.py check --built
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

import qr_core
import qrant

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'qr-ant'
MANIFEST = ASSETS / 'manifest.json'
SCANS = ROOT / 'research' / 'qr-ant-2026-09-10' / 'scan-styles.tsv'
BUILT = ROOT / 'docs' / 'qr-ant' / 'index.html'
ROUTE = 'qr-ant'
TITLE = 'QR codes drawn in ants'
RENDER_PX = 12
VECTOR = ('abdomen-small', 'L')       # the one option also published as vector


def placeholder() -> str:
    """A payload the length of a 256t tag that admits what it is.

    A real tag is an eight-character length prefix and an eighty-six character
    base64url hash. This keeps that shape so the symbols are the size the tool
    was built for, and spends the hash on a sentence instead.
    """
    body = 'PLACEHOLDER-this-is-not-a-real-256t-content-tag-and-resolves-to-nothing'
    tag = '00000000' + body + '-' * (86 - len(body))
    payload = '256t.org/' + tag
    if len(tag) != 94 or len(payload.encode()) != 103:
        raise ValueError(f'placeholder is {len(payload.encode())} bytes, expected 103')
    return payload


# Which options the gallery shows, in the order it shows them, and why each is
# there. The roles drive the layout: the page is an argument, not a contact
# sheet, and every image has to be carrying a point.
SELECTION = (
    ('plain', 'L', 'control', 'Plain squares. What every other option is measured against.'),
    ('grid', 'L', 'scattered', 'One library ant per dark module, sized to fit inside it. '
     'Its abdomen ends up 0.67 by 0.47 of a square — half the width of the thing it '
     'stands on.'),
    ('swarm', 'L', 'scattered', 'Small ants scattered off the lattice. The picture is the '
     'mass, not the animal.'),
    ('dense', 'L', 'scattered', 'As many scattered ants as a clean light field will take.'),
    ('body-large-pile', 'L', 'posed', 'Jointed ants sized against the whole symbol, as '
     'large as the ground anywhere will take, piled rather than kept apart. The longest '
     'ants anything here reaches.'),
    ('abdomen-small', 'L', 'recommended', 'Sized against one module instead: the gaster is '
     'a module long and pinned at the module’s centre, so a square <em>is</em> an abdomen. The '
     'cleanest light field of any option, and the recommendation.'),
    ('abdomen', 'L', 'abdomen', 'The gaster a module <em>wide</em> rather than long, which '
     'makes the whole ant half again as big.'),
    ('abdomen-bold', 'L', 'abdomen', 'Abdomens slightly wider than their square. The fewest '
     'ants of any option that reads.'),
    ('abdomen-full', 'L', 'abdomen', 'An abdomen forced onto <em>every</em> dark module '
     'rather than only where one is still needed. The abdomens run together into strings '
     'and the individual animals are lost.'),
    ('halftone', 'L', 'failure', 'Ants over the whole field, light modules included. This '
     'tool’s decoder reads it; a real scanner does not find it at all.'),
    ('wild', 'L', 'failure', 'Large ants drawn with no budget and no repair at all: the '
     'only option here that overruns the correction budget rather than merely losing the '
     'scanner.'),
    ('swarm', 'H', 'scattered', 'The scattered family on the largest symbol.'),
    ('abdomen-small', 'H', 'recommended', 'The recommendation on the largest symbol, where '
     'the whole 112-codeword correction budget is left intact for real-world damage.'),
)

ROLE_LABEL = {
    'control': 'Control',
    'scattered': 'Scattered',
    'posed': 'Posed',
    'abdomen': 'One square, one abdomen',
    'recommended': 'Recommended',
    'failure': 'Past the edge',
}


def stem(style: str, ecc: str) -> str:
    return f'{style}-{ecc}'


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate() -> dict:
    """Render every option in the selection and write the tracked assets."""
    import rasterize
    text = placeholder()
    ASSETS.mkdir(parents=True, exist_ok=True)
    entries = []
    for style, ecc, role, note in SELECTION:
        symbol = qrant.build(text, ecc, style)
        drawing = qrant.compose(symbol, RENDER_PX)
        run = qrant.measure(symbol, drawing)
        name = stem(style, ecc)
        png = ASSETS / f'{name}.png'
        rasterize.write_png(png, drawing.grid)
        # The manifest records *measurements* only. Role and caption live in
        # SELECTION, so rewriting the prose never means re-rendering the images.
        entry = {
            'style': style, 'ecc': ecc,
            'png': png.name, 'png_sha256': _digest(png),
            'version': symbol.version, 'mask': symbol.mask, 'modules': symbol.size,
            'ants': len(drawing.marks), 'posed': drawing.posed,
            'fitted': round(drawing.fitted, 4),
            'mean_size': round(drawing.mean_size, 2),
            'biggest': round(drawing.biggest, 2),
            'module_errors': run.module_errors,
            'binary_errors': run.binary_errors,
            'finders': run.finders,
            'spent': round(run.spent, 4),
            'worst_block': round(run.worst_block, 4),
            'light_cell': round(run.light_cell, 4),
            'worst_light': round(run.worst_light, 4),
            'ink': round(run.ink, 4),
            'reads': run.decoded,
            'reads_blurred': qrant.measure(symbol, drawing, max(1, RENDER_PX // 6)).decoded,
        }
        if (style, ecc) == VECTOR:
            svg = ASSETS / f'{name}.svg'
            svg.write_text(qrant.to_svg(symbol, drawing, 8.0), encoding='utf-8')
            entry['svg'] = svg.name
            entry['svg_sha256'] = _digest(svg)
        entries.append(entry)
        print(f'{name}: {entry["ants"]} ants, {entry["spent"]:.0%} of the budget, '
              f'{"reads" if entry["reads"] else "DOES NOT READ"}')
    manifest = {
        'version': 1,
        'about': 'QR symbols drawn in ants. Generated by scripts/qr_gallery.py generate; '
                 'laid out by scripts/build-site.py. The payload is a placeholder that '
                 'says so in its own text and resolves to nothing.',
        'payload': text,
        'payload_bytes': len(text.encode()),
        'render_px': RENDER_PX,
        'entries': entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding='utf-8'))


def scanner_verdicts() -> dict:
    """What the system scanner made of each option, from the tracked evidence."""
    if not SCANS.exists():
        return {}
    out = {}
    for line in SCANS.read_text(encoding='utf-8').splitlines()[1:]:
        if '\t' not in line:
            continue
        name, verdict = line.split('\t', 1)
        out[name.removesuffix('.png')] = verdict.strip()
    return out


# --- the page -------------------------------------------------------------

def described() -> dict:
    """`(style, ecc)` -> `(role, caption)`, from the selection rather than the manifest."""
    return {(style, ecc): (role, note) for style, ecc, role, note in SELECTION}


def _figure(entry: dict, role: str, note: str, verdict: str, prefix: str) -> str:
    name = stem(entry['style'], entry['ecc'])
    src = f'{prefix}{entry["png"]}'
    label = ROLE_LABEL.get(role, role)
    alt = (f'QR symbol {entry["version"]}-{entry["ecc"]}, {entry["modules"]} modules square, '
           f'drawn with {entry["ants"]} ants in the {entry["style"]} style. It encodes a '
           f'placeholder that resolves to nothing.')
    reads = 'reads' if entry['reads'] else 'does not read'
    stats = [
        ('ants', f'{entry["ants"]:,}'),
        ('longest ant', f'{entry["biggest"]:.1f} modules' if entry['biggest'] else '—'),
        ('budget spent', f'{entry["spent"]:.0%}'),
        ('light-cell ink', f'{entry["light_cell"]:.2f}'),
        ('this tool', reads),
    ]
    if verdict:
        stats.append(('system scanner', verdict))
    rows = ''.join(f'<div><dt>{html.escape(key)}</dt><dd>{html.escape(value)}</dd></div>'
                   for key, value in stats)
    # `note` is authored in SELECTION above and carries its own emphasis markup,
    # so it is the one field here that is not escaped.
    vector = ''
    if entry.get('svg'):
        vector = (f' <a class="qr-vector" href="{prefix}{entry["svg"]}">'
                  'Open the vector version</a>')
    return (f'<figure class="qr-card qr-{html.escape(role)}" id="{html.escape(name)}">'
            f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" '
            f'width="{(entry["modules"] + 8) * RENDER_PX}" '
            f'height="{(entry["modules"] + 8) * RENDER_PX}">'
            f'<figcaption><p class="qr-role">{html.escape(label)}</p>'
            f'<h3><code>{html.escape(entry["style"])}</code> · '
            f'{entry["version"]}-{html.escape(entry["ecc"])} · '
            f'{entry["modules"]}&nbsp;×&nbsp;{entry["modules"]}</h3>'
            f'<p>{note}</p><dl class="qr-stats">{rows}</dl>{vector}'
            '</figcaption></figure>')


def body(prefix: str = '../assets/qr-ant/') -> str:
    """The gallery page, as HTML for the site builder to wrap in its template."""
    manifest = load()
    verdicts = scanner_verdicts()
    entries = manifest['entries']
    captions = described()
    by_key = {(e['style'], e['ecc']): e for e in entries}
    recommended = by_key.get(('abdomen-small', 'H')) or entries[0]

    def figures(role: str) -> str:
        out = []
        for entry in entries:
            key = (entry['style'], entry['ecc'])
            entry_role, note = captions[key]
            if entry_role != role:
                continue
            out.append(_figure(entry, entry_role, note, verdicts.get(stem(*key), ''), prefix))
        return ''.join(out)

    free = [e for e in entries if e['spent'] == 0 and e['reads']]
    others = [e['light_cell'] for e in entries
              if e['style'] not in ('plain', 'abdomen-small') and e['reads']]
    cleanest = recommended['light_cell']
    ratio = (min(others) / cleanest) if cleanest and others else 0
    grid = next((e['light_cell'] for e in entries if e['style'] == 'grid'), 0)
    table_rows = ''.join(
        f'<tr><th scope="row"><code>{html.escape(e["style"])}</code></th>'
        f'<td>{html.escape(e["ecc"])}</td><td>{e["ants"]:,}</td>'
        f'<td>{e["fitted"]:.0%}</td><td>{e["biggest"]:.1f}</td>'
        f'<td>{e["spent"]:.0%}</td><td>{e["light_cell"]:.2f}</td>'
        f'<td>{"yes" if e["reads"] else "no"}</td>'
        f'<td>{html.escape(verdicts.get(stem(e["style"], e["ecc"]), "—"))}</td></tr>'
        for e in entries)

    return f'''
<p class="qr-lede">A QR symbol has to be dark where a scanner looks. Everything between
those two facts is available for drawing, and this is what happens when it is spent on the
edition’s ant. Every symbol below is real and scannable; each one is measured rather than
asserted, and the measurements are what the page is for.</p>

<div class="qr-warning"><p><strong>These encode a placeholder, not an address.</strong>
They are the length of a real 256t content tag — 103 bytes — so that they are the size the
tool was built for, but the tag is the sentence
<code>{html.escape(manifest['payload'])}</code>. Scanning one tells you so. Nothing here
resolves anywhere.</p></div>

<h2>What the drawing costs</h2>
<p>Nothing is lost from the payload: every option here either carries all 103 bytes or does
not scan. What art spends is <em>margin</em> — the damage the symbol could have absorbed
from a scuff, a fold, a bad angle or cheap printing, and now cannot, because the drawing
already spent it. A symbol has to clear three separate hurdles, and a drawing can pass one
and fail another:</p>
<ol class="qr-hurdles">
<li><strong>Locating.</strong> A scanner has to find the symbol before it decodes anything,
by scanning for the finder patterns’ 1:1:3:1:1 run of dark and light. Ink pressed against a
finder breaks that run even when every module inside it is correct.</li>
<li><strong>Binarising.</strong> A camera turns the frame into black and white against a
<em>local</em> average. Ink that misses every module’s centre but fills the space around it
still moves the threshold that centre will be judged against.</li>
<li><strong>Sampling.</strong> Only then is each module read, at its centre. A leg straight
through a light module’s middle loses it, however empty the rest of that cell is.</li>
</ol>
<p>The tool measures all three. <em>Budget spent</em> below is the share of the Reed–Solomon
correction budget the drawing consumed; <em>light-cell ink</em> is the mean ink in a light
module’s whole cell, which is the quantity that decides hurdle 2 and, in practice, whether a
real scanner finds the symbol at all.</p>

<h2>The control</h2>
{figures('control')}

<h2>Ants as marks: the scattered family</h2>
<p>These build the dark half out of the <em>positions</em> of many small copies of the
library ant. The ant is a mark; the picture is where the marks are.</p>
<div class="qr-grid">{figures('scattered')}</div>

<h2>Ants as shapes: the posed family</h2>
<p>These build it out of the ant’s own silhouette. Each ant is jointed — gaster and head
pivoting about the thorax, six legs and two antennae solved joint by joint — to fit the
ground it covers. Poses <strong>articulate and never stretch</strong>: every bone keeps the
length the tracked asset gives it, so each one is the same animal in a different attitude.</p>
<p>Two things follow from that restriction, and they set what this family can do. A large
ant has a large <em>gaster</em>, and a gaster has to sit in dark ground — but only about a
third of a QR symbol’s dark modules lie in a two-by-two block, so <strong>nothing fits above
about six modules at any tolerance</strong>. And a large ant has proportionally thin legs, a
quarter of a module wide, so bodies do the covering and legs are filigree.</p>
<div class="qr-grid">{figures('posed')}</div>

<h2>One square, one abdomen</h2>
<p>The posed styles above size an ant against the <em>symbol</em>. Sizing it against a single
<em>module</em> instead — gaster as wide as the square, pinned at the square’s centre — is
better on every measurement taken, and the margin is not small. Its light field carries
{cleanest:.2f} mean ink against {grid:.2f} for the lattice-bound <code>grid</code> and
{min(others):.2f} for the next cleanest thing that reads — {ratio:.1f} times cleaner than
anything else here. It wastes almost none of the ants it offers, and it costs no correction
budget.</p>
<p>The reason appears to be that pinning the gaster puts the ant’s one thick part exactly
where the ink is wanted, so the thin parts — which are what stray onto light ground — have
much less to cover. Sizing against the symbol leaves the thick part wherever it lands and
asks the legs to make up the difference.</p>
<div class="qr-grid">{figures('recommended')}</div>
<p>The same sizing at three other settings — a wider abdomen, a slightly oversized one, and
one forced onto every dark module whether or not it was still needed:</p>
<div class="qr-grid">{figures('abdomen')}</div>

<h2>Past the edge</h2>
<p>Kept so that the far end of the trade is visible rather than asserted.</p>
<div class="qr-grid">{figures('failure')}</div>

<h2>Every option, measured</h2>
<div class="qr-table-scroll"><table class="qr-table">
<caption>Rendered at {manifest['render_px']} pixels per module. <em>fit</em> is the share of
the ants a style offered that found room; <em>longest</em> is in modules. The last column is
the verdict of the macOS Vision framework on the same file.</caption>
<thead><tr><th scope="col">style</th><th scope="col">ecc</th><th scope="col">ants</th>
<th scope="col">fit</th><th scope="col">longest</th><th scope="col">budget</th>
<th scope="col">light cell</th><th scope="col">this tool</th>
<th scope="col">system scanner</th></tr></thead>
<tbody>{table_rows}</tbody></table></div>
<p>{len(free)} of the {len(entries)} options shown spend nothing of the correction budget and
still read. What separates them is the picture, and how much margin is left for the world.</p>

<h2>The measurements are calibrated, not assumed</h2>
<p>A decoder written alongside an encoder will agree with it and prove nothing. Two bugs in
this project’s codec — an inverted finder ring, and a transposed format-information
placement — survived every round trip through it, because the decoder made the same mistake
as the encoder. Both died immediately against a symbol generated by an implementation that
was not this one, and one such symbol is now pinned as a fixture and checked on every run.</p>
<p>The same discipline found the drawing bugs. An early version reported a clean read on
symbols the system scanner could not find at all, because it constrained ink at each
module’s centre and nothing else. A later one reported the opposite, because it constrained
the whole cell and nothing else. Both constraints have to hold together; the tables above
are what the tool reports once they do.</p>

<h2>This is apparatus, not page art</h2>
<p>A QR symbol is a lattice of marks in a fixed count, arranged to be read as data. The ant
convention this edition follows requires the opposite of all three: no count, no
correspondence between a mark and anything, no reading off the page. A symbol from this tool
belongs on a cover, a colophon or a card, and never in a margin, a gutter or a panel, where
a reader could take the two registers for one.</p>
<p>Nothing here is adopted. No symbol is used anywhere in the book, no build step depends on
one, and no ant photographs are in the repository — every ant above is the edition’s own
vector ant, jointed or scattered.</p>
'''.strip()


# --- checks ---------------------------------------------------------------

def _check_manifest() -> list[str]:
    findings = []
    if not MANIFEST.exists():
        return [f'{MANIFEST.relative_to(ROOT)} is missing; run qr_gallery.py generate']
    manifest = load()
    text = placeholder()
    if manifest.get('payload') != text:
        findings.append('the manifest payload is not the documented placeholder')
    if manifest.get('payload_bytes') != len(text.encode()):
        findings.append('the manifest payload length disagrees with the payload')

    entries = manifest.get('entries', [])
    wanted = [(style, ecc) for style, ecc, _, _ in SELECTION]
    if [(e['style'], e['ecc']) for e in entries] != wanted:
        findings.append('the manifest entries do not match the selection, in order')
    roles = {role for _, _, role, _ in SELECTION}
    if 'recommended' not in roles:
        findings.append('no option is marked as the recommendation')
    unknown = roles - set(ROLE_LABEL)
    if unknown:
        findings.append(f'the selection carries roles the page cannot lay out: {sorted(unknown)}')

    for entry in entries:
        name = stem(entry['style'], entry['ecc'])
        if entry['style'] not in qrant.STYLES:
            findings.append(f'{name}: no such style')
            continue
        for key, suffix in (('png', '.png'), ('svg', '.svg')):
            if key not in entry:
                continue
            path = ASSETS / entry[key]
            if not path.is_file() or path.suffix != suffix:
                findings.append(f'{name}: {key} asset {entry[key]} is missing')
            elif _digest(path) != entry[f'{key}_sha256']:
                findings.append(f'{name}: {key} asset has changed since it was recorded')

        # Everything the manifest claims about the code, re-derived here.
        version = qr_core.smallest_version(text.encode(), entry['ecc'])
        if entry['version'] != version:
            findings.append(f'{name}: manifest says version {entry["version"]}, '
                            f'the payload needs {version}')
        if entry['modules'] != qr_core.size_for(version):
            findings.append(f'{name}: module count disagrees with its version')
        matrix, _, _ = qr_core.build_matrix(text.encode(), version, entry['ecc'],
                                            mask=entry['mask'])
        result = qr_core.decode(matrix, version)
        if not result.ok or result.payload != text.encode():
            findings.append(f'{name}: the recorded version, level and mask do not '
                            'reproduce the payload')
        if entry['finders'] != 3:
            findings.append(f'{name}: only {entry["finders"]} of 3 finders were locatable, '
                            'which no published option may be')
        role = described()[(entry['style'], entry['ecc'])][0]
        if role == 'recommended' and not (entry['reads'] and entry['spent'] == 0):
            findings.append(f'{name}: recommended, but it spends budget or does not read')
        if role == 'failure' and entry['reads']:
            findings.append(f'{name}: shown as past the edge, but it reads')

    for stray in sorted(ASSETS.glob('*')):
        if stray.name == 'manifest.json':
            continue
        named = {entry.get('png') for entry in entries} | {entry.get('svg') for entry in entries}
        if stray.name not in named:
            findings.append(f'{stray.name} is in the asset directory but not in the manifest')
    return findings


def _check_built() -> list[str]:
    findings = []
    if not BUILT.exists():
        return [f'{BUILT.relative_to(ROOT)} is missing; run scripts/build-site.py']
    page = BUILT.read_text(encoding='utf-8')
    manifest = load()
    for entry in manifest['entries']:
        for key in ('png', 'svg'):
            if key in entry and entry[key] not in page:
                findings.append(f'the built gallery does not reference {entry[key]}')
        published = ROOT / 'docs' / 'assets' / 'qr-ant' / entry['png']
        if not published.is_file():
            findings.append(f'{entry["png"]} was not published under docs/assets/qr-ant/')
    if manifest['payload'] not in page:
        findings.append('the built gallery does not print the placeholder payload it encodes')
    if 'apparatus' not in page:
        findings.append('the built gallery does not carry the apparatus statement')
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('generate', help='render every option and write the tracked assets')
    checker = sub.add_parser('check', help='verify the manifest, the assets and their claims')
    checker.add_argument('--built', action='store_true',
                         help='also check the published gallery under docs/')
    sub.add_parser('report', help='list what the gallery shows')
    args = parser.parse_args(argv)

    if args.command == 'generate':
        manifest = generate()
        print(f'wrote {len(manifest["entries"])} options to {ASSETS.relative_to(ROOT)}')
        return 0
    if args.command == 'report':
        manifest = load()
        verdicts = scanner_verdicts()
        print(f'{manifest["payload_bytes"]} byte placeholder, '
              f'{len(manifest["entries"])} options')
        for entry in manifest['entries']:
            name = stem(entry['style'], entry['ecc'])
            role = described()[(entry['style'], entry['ecc'])][0]
            print(f'  {name:<22}{ROLE_LABEL[role]:<26}{entry["ants"]:>6} ants  '
                  f'{entry["spent"]:>4.0%} budget  {verdicts.get(name, "—")}')
        return 0

    findings = _check_manifest()
    if args.built and not findings:
        findings += _check_built()
    for finding in findings:
        print(f'FAIL {finding}')
    print('qr_gallery: 0 findings' if not findings
          else f'qr_gallery: {len(findings)} findings')
    return 1 if findings else 0


if __name__ == '__main__':
    sys.exit(main())
