#!/usr/bin/env python3
"""Durable, offline artwork handoff queue. No model calls, keys or Git writes.

prepare -> claim -> receive -> review accept|reject; retry explicitly after rejection.
Pending PNGs live in SQLite, outside the reader's artwork store. export produces
self-contained review HTML and exact tool handoffs. check runs offline fixtures.
"""
from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import html
import json
import math
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import zlib

import imagegen
import letterpress
import panelart
import produce
import storyboards
import textimage

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / '256t/art-jobs/queue.sqlite3'
SLUG = re.compile(r'[a-z][a-z0-9-]{0,59}\Z')
VERSION = 1


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def png_size(data):
    """Validate PNG chunks, CRCs and the complete noninterlaced scanline stream.

    Bound decompression to the declared dimensions; no third-party decoder needed.
    Only 8-bit gray/RGB/gray-alpha/RGBA PNGs are accepted for this first workflow.
    """
    if len(data) > 100_000_000 or data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected a PNG under 100 MB')
    pos, kinds, compressed, size = 8, [], [], None
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError('Truncated PNG chunk')
        length = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        end = pos + 12 + length
        if end > len(data):
            raise ValueError('Truncated PNG data')
        payload = data[pos+8:end-4]
        if zlib.crc32(kind + payload) & 0xffffffff != struct.unpack('>I', data[end-4:end])[0]:
            raise ValueError('PNG CRC mismatch')
        if not kinds and kind != b'IHDR':
            raise ValueError('PNG must start with IHDR')
        if kind == b'IHDR':
            if kinds or length != 13:
                raise ValueError('Invalid PNG header')
            w, h, depth, color, comp, filt, interlace = struct.unpack('>IIBBBBB', payload)
            if not (0 < w <= 8192 and 0 < h <= 8192 and w*h <= 20_000_000):
                raise ValueError('PNG dimensions exceed workflow limits')
            if depth != 8 or color not in (0, 2, 4, 6) or comp or filt or interlace:
                raise ValueError('Use a noninterlaced 8-bit gray/RGB/RGBA PNG')
            size = (w, h)
            stride = w * {0: 1, 2: 3, 4: 2, 6: 4}[color] + 1
        elif kind == b'IDAT':
            if b'IDAT' in kinds and kinds[-1] != b'IDAT':
                raise ValueError('Noncontiguous PNG image data')
            compressed.append(payload)
        elif kind == b'IEND':
            if length or end != len(data):
                raise ValueError('Invalid PNG end')
        elif kind == b'acTL':
            raise ValueError('Animated PNG is not supported')
        elif kind not in (b'PLTE',) and not kind[0] & 32:
            raise ValueError('Unknown critical PNG chunk')
        kinds.append(kind)
        pos = end
    if not size or not kinds or kinds[-1] != b'IEND' or not compressed:
        raise ValueError('Incomplete PNG')
    expected = stride * size[1]
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(b''.join(compressed), expected + 1)
    if len(pixels) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError('Invalid PNG pixel stream')
    if any(pixels[i] > 4 for i in range(0, expected, stride)):
        raise ValueError('Invalid PNG scanline filter')
    return list(size)


@contextmanager
def database(path, *, create=False):
    path = Path(path).resolve()
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() and not create:
        raise ValueError(f'No queue at {path}; prepare a job first')
    connection = sqlite3.connect(str(path), timeout=2)
    try:
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, record TEXT NOT NULL)')
        connection.execute('CREATE TABLE IF NOT EXISTS blobs (sha TEXT PRIMARY KEY, data BLOB NOT NULL)')
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        if version not in (0, VERSION):
            raise ValueError(f'Unsupported queue schema {version}')
        connection.execute(f'PRAGMA user_version={VERSION}')
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def jobs(db):
    return [json.loads(row[0]) for row in db.execute('SELECT record FROM jobs ORDER BY id')]


def get(db, name):
    row = db.execute('SELECT record FROM jobs WHERE id=?', (name,)).fetchone()
    if row is None:
        raise ValueError(f'Unknown job: {name}')
    return json.loads(row[0])


def save(db, job):
    db.execute('INSERT OR REPLACE INTO jobs VALUES (?, ?)', (job['id'], encoded(job)))


def put_blob(db, data):
    sha = digest(data)
    db.execute('INSERT OR IGNORE INTO blobs VALUES (?, ?)', (sha, data))
    return sha


def blob(db, sha):
    row = db.execute('SELECT data FROM blobs WHERE sha=?', (sha,)).fetchone()
    if row is None or digest(row[0]) != sha:
        raise ValueError(f'Missing or corrupt saved artifact: {sha}')
    return row[0]


def transition(job, state, note):
    job['state'] = state
    job['events'].append({'at': now(), 'state': state, 'note': note})


def snapshot(panel):
    import panel_layout
    size = panel_layout.target(panel)
    data = storyboards.load()
    if panel not in {s.id for s in produce.all_slots()}:
        raise ValueError(f'{panel} is not a current reader slot')
    scene = data['scenes'][panel]
    source = storyboards.source_bodies()[panel]
    if scene['source'] != source:
        raise ValueError(f'{panel}: stale storyboard; review its source first')
    placed, remaining, lettering = storyboards.lettering(panel, scene)
    if remaining or any(p.truncated for p in placed):
        raise ValueError(f'{panel}: incomplete lettering')
    board = storyboards.render(scene, data, size=size)
    # Include the complete page and adjacent pages so changed continuity invalidates work.
    page = int(panel[:3])
    sources = {}
    for n in (page-1, page, page+1):
        path = ROOT / f'content/pages/{n:03d}.md'
        if path.exists():
            sources[str(path.relative_to(ROOT))] = digest(path.read_bytes())
    for name in ('content/story-contract.md', 'prompts/global-style.md',
                 'prompts/negative-prompt.md', 'prompts/characters.md', 'prompts/environments.md'):
        path = ROOT / name
        sources[name] = digest(path.read_bytes())
    return {'panel': panel, 'target_size': list(size), 'source': source, 'board': board, 'scene': scene,
            'palette': data['palette'], 'placed': [asdict(p) for p in placed],
            'lettering': lettering, 'sources': sources}


def fresh(job):
    current = snapshot(job['panel'])
    # Pre-layout jobs are compatible only with their original 1200x800 canvas.
    if 'target_size' not in job['snapshot'] and current.get('target_size') == [1200,800]:
        current.pop('target_size')
    if digest(encoded(current).encode()) != job['snapshot_sha']:
        raise ValueError(f"{job['id']}: source/composition changed; prepare a new job after review")


def rasterize(svg):
    runner = shutil.which('rsvg-convert')
    if not runner:
        raise ValueError('Preparing a PNG board requires rsvg-convert on PATH; no package is installed automatically')
    result = subprocess.run([runner], input=svg.encode(),
                            capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError('Board rasterization failed: ' + result.stderr.decode(errors='replace')[-500:])
    png_size(result.stdout)
    return result.stdout


def prepare(db, args):
    if not SLUG.fullmatch(args.job):
        raise ValueError('Job name must start with a letter and use lowercase letters, digits or hyphens (max 60)')
    if any(j['id'] == args.job for j in jobs(db)):
        raise ValueError('Job already exists; export/resume it, or use a new name')
    if not 1 <= args.max_attempts <= 10:
        raise ValueError('max-attempts must be 1–10')
    snap = snapshot(args.panel)
    for dep in args.depends:
        get(db, dep)  # Only existing jobs may be dependencies: prevents cycles.
    refs = [{'role': 'composition', 'sha': put_blob(db, rasterize(snap['board']))}]
    for path in args.reference:
        data = path.read_bytes()
        png_size(data)
        refs.append({'role': 'continuity', 'sha': put_blob(db, data), 'origin': str(path.resolve())})
    page, index = args.panel.split('-')
    prompt = (args.prompt_file.read_text() if args.prompt_file else
              imagegen.compose_panel(page, int(index), produce.register_for(page), budget=0))
    if not prompt.strip():
        raise ValueError('Empty prompt')
    width, height = snap['target_size']
    zones = [[round(p[k]/(width if k in ('x', 'w') else height), 4)
              for k in ('x', 'y', 'w', 'h')] for p in snap['placed']]
    prompt += (f'\n\nProduction constraints: one full-bleed image for a {width}x{height} panel. '
               'Generate at this aspect ratio and resolution when supported. Otherwise preserve '
               'the composition inside an explicit crop area; deliver a reviewed crop at the target ratio. '
               'No letterboxing, padding, stretching, or baked-in edge bands. '
               'Use the first reference for composition and later references for continuity. '
               'Do not draw captions, speech balloons, or an outer frame; production adds these. '
               'Keep meaningful subjects and labels out of these normalized [x,y,w,h] lettering boxes: '
               + json.dumps(zones) + '. Do not invent source prose or pseudo-writing.\n')
    job = {'schema': VERSION, 'id': args.job, 'panel': args.panel, 'priority': args.priority,
           'max_attempts': args.max_attempts, 'depends': list(dict.fromkeys(args.depends)),
           'snapshot': snap, 'snapshot_sha': digest(encoded(snap).encode()), 'references': refs,
           'prompt': prompt, 'attempts': [], 'events': []}
    transition(job, 'prepared', 'Prompt and composition saved; visual inspection required before generation')
    save(db, job)
    return job


def claim(db, name=None):
    candidates = [get(db, name)] if name else sorted(jobs(db), key=lambda j: (-j['priority'], j['id']))
    for job in candidates:
        if job['state'] != 'prepared':
            continue
        if any(get(db, dep)['state'] != 'accepted' for dep in job['depends']):
            continue
        fresh(job)
        if len(job['attempts']) >= job['max_attempts']:
            raise ValueError('Attempt limit reached')
        refs = list(job['references'])
        for dep in job['depends']:
            parent = get(db, dep)
            refs.append({'role': 'accepted-dependency', 'sha': parent['attempts'][-1]['output_sha']})
        attempt = {'number': len(job['attempts'])+1, 'prompt': job['prompt'], 'references': refs,
                   'started': now(), 'tool': 'image_gen.imagegen', 'model_revision': None,
                   'seed': None, 'controls': 'Model revision, seed, sampler, strength and billing unavailable.'}
        job['attempts'].append(attempt)
        transition(job, 'generating', 'Claimed once; recover output before retrying an interrupted call')
        save(db, job)
        return job
    raise ValueError('No prepared job with accepted dependencies; inspect status for pending work')


def receive(db, job, data, seconds):
    attempt = job['attempts'][-1] if job['attempts'] else {}
    sha = digest(data)
    if attempt.get('output_sha') == sha:
        return job  # Repeat delivery never allocates another attempt or version.
    if job['state'] != 'generating':
        raise ValueError('Receive requires a generating job; a different output cannot replace a saved attempt')
    if seconds is not None and (not math.isfinite(seconds) or seconds < 0 or seconds > 86400):
        raise ValueError('Elapsed seconds must be between 0 and 86400')
    size = png_size(data)
    import panel_layout
    panel_layout.require_size(size, job['snapshot'].get('target_size', [1200,800]), job['id'])
    attempt.update(output_sha=put_blob(db, data), dimensions=size, elapsed_seconds=seconds, received=now())
    transition(job, 'awaiting-review', 'Exact PNG saved outside the published artwork store')
    save(db, job)
    return job


def compose(job, raw):
    """Immutable controlled border, preserving original PNG bytes inside the SVG."""
    w, h = png_size(raw)
    scene, palette = job['snapshot']['scene'], job['snapshot']['palette']
    image = base64.b64encode(raw).decode()
    frame = ''
    if scene.get('border', 'default') != 'none':
        scale = w / storyboards.W
        dash = f' stroke-dasharray="{18*scale:g} {10*scale:g}"' if scene.get('reconstructed') else ''
        frame = (f'<rect x="{3*scale:g}" y="{3*scale:g}" width="{w-6*scale:g}" '
                 f'height="{h-6*scale:g}" fill="none" stroke="{html.escape(palette["steel"])}" '
                 f'stroke-width="{4*scale:g}"{dash}/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<image width="{w}" height="{h}" href="data:image/png;base64,{image}"/>{frame}</svg>')


def publish(db, job, note):
    """Recover an interrupted promotion by its unique job/attempt provider and bytes.

    SQLite serializes this tool's writers. Other artwork writers must be coordinated
    by the operator, as for the repository's existing store and curation commands.
    """
    fresh(job)
    attempt = job['attempts'][-1]
    raw = blob(db, attempt['output_sha'])
    import panel_layout
    panel_layout.require_size(png_size(raw), job['snapshot'].get('target_size', [1200,800]), job['id'])
    composed = compose(job, raw).encode()
    # Accepted provenance survives removal of the local queue. Files are addressed
    # by content, shared across jobs, and never overwritten.
    evidence = ROOT / 'assets/art/job-references'
    evidence.mkdir(parents=True, exist_ok=True)
    references = []
    for sha in dict.fromkeys([attempt['output_sha'], *[r['sha'] for r in attempt['references']]]):
        data = blob(db, sha)
        archive = evidence / f'{sha}.png'
        if archive.exists():
            if archive.read_bytes() != data:
                raise ValueError('Conflicting archived image hash')
        else:
            with archive.open('xb') as stream:
                stream.write(data)
        references.append(str(archive.relative_to(ROOT)))
    provider = f"art-job-{job['id']}-a{attempt['number']:02d}"
    matches = [v for v in panelart.discover() if v.panel == job['panel'] and v.provider == provider]
    if len(matches) > 1 or (matches and matches[0].path.read_bytes() != composed):
        raise ValueError('Conflicting promotion artifact; inspect before recovery')
    target = matches[0].path if matches else panelart.store(job['panel'], composed, '.svg', provider=provider)
    variant = target.name.split('-')[0]
    receipt = {'schema': VERSION, 'job': job['id'], 'panel': job['panel'], 'variant': variant,
               'source_sha': job['snapshot_sha'], 'attempt': attempt, 'review_note': note,
               'composed_sha': digest(composed), 'snapshot': job['snapshot'],
               'archived_images': references,
               'original_png': 'Losslessly embedded in SVG image data URI; also archived by SHA-256'}
    sidecar = target.with_suffix('.json')
    if sidecar.exists() and json.loads(sidecar.read_text()) != receipt:
        raise ValueError('Promotion receipt differs; recover with the original review note')
    if not sidecar.exists():
        with sidecar.open('x') as out:
            out.write(encoded(receipt))
    rows, _, _ = panelart.scan()
    updated = []
    for row in rows:
        if row.panel == job['panel'] and row.variant == variant:
            row = replace(row, status=panelart.CHOSEN, stage='refined', note=' '.join(note.split()))
        elif row.panel == job['panel'] and row.status == panelart.CHOSEN:
            row = replace(row, status=panelart.CANDIDATE)
        updated.append(row)
    # Atomic table replacement, using the existing table serializer.
    with tempfile.TemporaryDirectory(dir=panelart.TABLE.parent) as folder:
        temp = Path(folder) / 'panel-art.tsv'
        panelart.write_table(updated, temp)
        temp.replace(panelart.TABLE)
    panelart._CACHE = None
    job['promotion'] = {'file': str(target.relative_to(ROOT)), 'variant': variant, 'sha': digest(composed)}
    transition(job, 'accepted', note)
    save(db, job)


def review(db, job, decision, note):
    if not note.strip():
        raise ValueError('Record the visual decision or defect in --note')
    if job['state'] == 'accepted' and decision == 'accept':
        return job
    if job['state'] != 'awaiting-review':
        raise ValueError('Review requires a saved output awaiting review')
    if decision == 'accept':
        publish(db, job, note)
    else:
        job['attempts'][-1]['defect'] = note
        transition(job, 'rejected', note)
        save(db, job)
    return job


def retry(db, job, prompt):
    if job['state'] not in ('rejected', 'blocked'):
        raise ValueError('Retry only a rejected or explicitly blocked job')
    fresh(job)
    if len(job['attempts']) >= job['max_attempts']:
        raise ValueError('Attempt limit reached; keep the current reader image and review the approach')
    if not prompt.strip():
        raise ValueError('A correction/retry prompt is required')
    if job['attempts'] and job['attempts'][-1].get('output_sha'):
        job['references'] = [{'role': 'edit-source', 'sha': job['attempts'][-1]['output_sha']}]
    job['prompt'] = prompt
    transition(job, 'prepared', 'Explicit bounded retry; all prior attempts retained')
    save(db, job)
    return job


BROWSER_CHECK = r'''
<script>
async function audit() {
 await document.fonts.ready;
 const errors=[]; let measuredText=0;
 document.querySelectorAll('.lettered svg').forEach(svg=>{
  const page=svg.viewBox.baseVal;
  svg.querySelectorAll('text').forEach(text=>{
   measuredText++;
   const b=text.getBBox();
   const group=text.closest('g');
   const rect=group && group.querySelector('rect');
   const limit=rect ? rect.getBBox() : {x:0,y:0,width:page.width,height:page.height};
   if(b.x<limit.x-1 || b.y<limit.y-1 || b.x+b.width>limit.x+limit.width+1 || b.y+b.height>limit.y+limit.height+1)
    errors.push({panel:svg.closest('section').dataset.job,text:text.textContent,problem:'text overflow'});
  });
 });
 document.querySelectorAll('img').forEach(img=>{
  if(!img.complete || !img.naturalWidth) errors.push({problem:'image missing',alt:img.alt});
 });
 const report={at:new Date().toISOString(),userAgent:navigator.userAgent,
  measuredText,images:document.querySelectorAll('img').length,errors};
 document.getElementById('bounds').textContent=JSON.stringify(report,null,2);
 window.artReviewReport=report;
}
window.addEventListener('load',audit);
</script>'''


def export(db, directory):
    directory.mkdir(parents=True, exist_ok=True)
    sections = []
    for job in jobs(db):
        folder = directory / job['id']
        folder.mkdir(exist_ok=True)
        attempt = job['attempts'][-1] if job['attempts'] else {'prompt': job['prompt'], 'references': job['references']}
        refs = []
        for i, ref in enumerate(attempt['references']):
            path = folder / f'reference-{i+1}-{ref["sha"][:12]}.png'
            path.write_bytes(blob(db, ref['sha']))
            refs.append(str(path.resolve()))
        (folder / 'prompt.txt').write_text(attempt['prompt'])
        (folder / 'job.json').write_text(encoded(job))
        (folder / 'board.svg').write_text(job['snapshot']['board'])
        (folder / 'handoff.json').write_text(encoded({'job': job['id'], 'state': job['state'],
            'tool': 'image_gen.imagegen', 'arguments': {'prompt': attempt['prompt'], 'referenced_image_paths': refs},
            'instruction': 'Inspect references before invoking the tool. Only a generating job has been claimed.'}))
        views = [f'<figure><img alt="Saved storyboard" src="{storyboards.svg_uri(job["snapshot"]["board"])}"><figcaption>Saved composition</figcaption></figure>']
        page, index = job['panel'].split('-')
        current = panelart.resolve(page, int(index))
        if current:
            kind = {'svg': 'svg+xml', 'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'webp': 'webp'}[current.suffix[1:]]
            uri = f'data:image/{kind};base64,' + base64.b64encode(current.read_bytes()).decode()
            views.append(f'<figure><img alt="Current reader art" src="{uri}"><figcaption>Current reader art</figcaption></figure>')
        for item in job['attempts']:
            if not item.get('output_sha'):
                continue
            raw = blob(db, item['output_sha'])
            (folder / f'attempt-{item["number"]:02d}.png').write_bytes(raw)
            drawing = compose(job, raw)
            placed = [letterpress.Placed(**p) for p in job['snapshot']['placed']]
            lettered = letterpress.svg_panel(placed, job['snapshot']['lettering'], *job['snapshot'].get('target_size', [1200,800]), art_href=storyboards.svg_uri(drawing))
            (folder / f'attempt-{item["number"]:02d}-lettered.svg').write_text(lettered)
            label = html.escape(item.get('defect', 'Visual review required; mechanical checks do not approve the scene'))
            views.append(f'<figure class="lettered">{lettered}<figcaption>Attempt {item["number"]}: {label}</figcaption></figure>')
        sections.append(f'<section data-job="{job["id"]}"><h2>{job["id"]} · {job["panel"]} · {job["state"]}</h2>'
                        f'<div class="views">{"".join(views)}</div><details><summary>Exact prompt</summary><pre>{html.escape(attempt["prompt"])}</pre></details></section>')
    document = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>Artwork queue review</title>'
                '<style>body{background:#101214;color:#e7e0d0;font:16px system-ui;margin:2rem} '
                '.views{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1rem}'
                'figure{margin:0}img,svg{width:100%;height:auto}pre{white-space:pre-wrap}section{margin-bottom:3rem}</style>'
                '<h1>Artwork queue review</h1><p>Compare action, lettering, continuity and source boundaries. '
                'Inspect neighboring reader pages before accepting. No selection changes happen in this page.</p>'
                '<details open><summary>Browser text bounds and image loading</summary><pre id="bounds">Waiting for browser…</pre></details>'
                + ''.join(sections) + BROWSER_CHECK + '</html>')
    (directory / 'index.html').write_text(document)
    summary = [{'id': j['id'], 'panel': j['panel'], 'state': j['state'],
        'attempts': len(j['attempts']), 'limit': j['max_attempts']} for j in jobs(db)]
    (directory / 'status.json').write_text(encoded(summary))
    (directory / 'STATUS.md').write_text('# Artwork queue\n\nGenerated by art_jobs.py; do not edit.\n\n'
        '| Job | Panel | State | Attempts / limit |\n| --- | --- | --- | --- |\n'
        + ''.join(f"| {j['id']} | {j['panel']} | {j['state']} | {j['attempts']} / {j['limit']} |\n" for j in summary))
    return str((directory / 'index.html').resolve())


def verify(db_path):
    """Run the artwork publication boundary once; save every command's result."""
    with database(db_path) as db:
        for job in jobs(db):
            if job['state'] != 'accepted':
                fresh(job)
    commands = [['storyboards.py', 'check', '--complete'], ['letterpress.py', 'audit'],
                ['image_generation_status.py', 'write'], ['build-site.py'],
                ['storyboards.py', 'check', '--complete', '--built'], ['validate-viewer.py'],
                ['validate-site-links.py'], ['pagelinks.py', 'check', '--built'],
                ['image_generation_status.py', 'check']]
    results = []
    for command in commands:
        try:
            result = subprocess.run([sys.executable, str(ROOT/'scripts'/command[0]), *command[1:]],
                                    cwd=ROOT, capture_output=True, text=True, timeout=300)
            record = {'command': command, 'exit_code': result.returncode, 'output': result.stdout+result.stderr}
        except subprocess.TimeoutExpired:
            record = {'command': command, 'exit_code': 124, 'output': 'Timed out after 300 seconds'}
        results.append(record)
        print(f'{command[0]}: {"passed" if record["exit_code"] == 0 else "FAILED"}', flush=True)
        if record['exit_code']:
            break
    with database(db_path) as db:
        put_blob(db, encoded({'at': now(), 'checks': results}).encode())
    path = Path(db_path).parent / 'verification.json'
    path.write_text(encoded({'at': now(), 'checks': results}))
    return int(any(r['exit_code'] for r in results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    subs = parser.add_subparsers(dest='command', required=True)
    p = subs.add_parser('prepare')
    p.add_argument('job'); p.add_argument('panel')
    p.add_argument('--reference', type=Path, action='append', default=[])
    p.add_argument('--prompt-file', type=Path)
    p.add_argument('--depends', action='append', default=[])
    p.add_argument('--priority', type=int, default=0)
    p.add_argument('--max-attempts', type=int, default=3)
    p = subs.add_parser('claim'); p.add_argument('--job')
    p = subs.add_parser('receive'); p.add_argument('job'); p.add_argument('image', type=Path)
    p.add_argument('--seconds', type=float)
    p = subs.add_parser('review'); p.add_argument('job'); p.add_argument('decision', choices=['accept', 'reject'])
    p.add_argument('--note', required=True)
    p = subs.add_parser('retry'); p.add_argument('job'); p.add_argument('--prompt-file', type=Path, required=True)
    p = subs.add_parser('block'); p.add_argument('job'); p.add_argument('--note', required=True)
    p = subs.add_parser('export'); p.add_argument('--output', type=Path)
    subs.add_parser('status'); subs.add_parser('verify'); subs.add_parser('check')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            return check(args.db)
        if args.command == 'verify':
            return verify(args.db)
        with database(args.db, create=args.command == 'prepare') as db:
            if args.command == 'prepare':
                result = prepare(db, args)
            elif args.command == 'claim':
                result = claim(db, args.job)
            elif args.command == 'receive':
                result = receive(db, get(db, args.job), args.image.read_bytes(), args.seconds)
            elif args.command == 'review':
                result = review(db, get(db, args.job), args.decision, args.note)
            elif args.command == 'retry':
                result = retry(db, get(db, args.job), args.prompt_file.read_text())
            elif args.command == 'block':
                result = get(db, args.job)
                if result['state'] not in ('generating', 'prepared') or not args.note.strip():
                    raise ValueError('Block only prepared/generating jobs, with a reason')
                transition(result, 'blocked', args.note); save(db, result)
            elif args.command == 'export':
                print(export(db, args.output or args.db.parent/'review')); return 0
            else:
                print(encoded([{'id': j['id'], 'panel': j['panel'], 'state': j['state'],
                                'attempts': len(j['attempts']), 'limit': j['max_attempts']} for j in jobs(db)])); return 0
            summary = {'id': result['id'], 'panel': result['panel'], 'state': result['state'],
                       'attempts': len(result['attempts'])}
        # Queue progress is already committed if an interrupted export needs rerunning.
        with database(args.db) as db:
            summary['review'] = export(db, args.db.parent/'review')
            if args.command == 'claim':
                summary['handoff'] = json.loads((args.db.parent/'review'/result['id']/'handoff.json').read_text())
        print(encoded(summary))
        return 0
    except (ValueError, OSError, sqlite3.Error, subprocess.TimeoutExpired, zlib.error) as error:
        print(f'art_jobs: {error}', file=sys.stderr)
        return 1


# check() is below the CLI to keep the production path together.
def check_job(db, job):
    # Explicitly blocked inputs are retained history, not runnable work. Freshness is
    # still mandatory in retry/claim/publish; never rewrite a stale saved snapshot.
    if job['state'] not in ('accepted', 'blocked'):
        fresh(job)
    for ref in job['references']:
        png_size(blob(db, ref['sha']))
    for attempt in job['attempts']:
        for ref in attempt['references']:
            png_size(blob(db, ref['sha']))
        if attempt.get('output_sha'):
            png_size(blob(db, attempt['output_sha']))


def check(path):
    import art_jobs_checks
    art_jobs_checks.run()
    if path.exists():
        with database(path) as db:
            for job in jobs(db):
                check_job(db, job)
    print('Artwork queue: offline recovery, review isolation, PNG and state checks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
