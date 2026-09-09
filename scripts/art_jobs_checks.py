"""Offline fixture checks for art_jobs.py; invoked by its check subcommand."""
from argparse import Namespace
from contextlib import ExitStack
import json
from pathlib import Path
import sqlite3
import struct
import tempfile
from unittest.mock import patch
import zlib


def png(w=1536, h=1024):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\x00' + b'\x10\x12\x14'*w)*h)) + chunk(b'IEND', b''))


def fails(callback, message):
    try:
        callback()
    except (ValueError, sqlite3.Error):
        return
    raise AssertionError(message)


def run():
    import art_jobs as a
    import panelart as p
    # Changing a governing visual rule must invalidate a prepared snapshot.
    baseline = a.snapshot('001-01')
    job = {'id': 'visual-rule-fixture', 'panel': '001-01', 'snapshot': baseline,
           'snapshot_sha': a.digest(a.encoded(baseline).encode())}
    original_bytes = Path.read_bytes
    for relative in ('content/visual-bible.md', 'design/visual-continuity.md',
                     'content/continuity.md', 'design/knowledge-map.md'):
        target = a.ROOT / relative
        def changed(path):
            return original_bytes(path) + (b'\nChanged visual rule\n' if path == target else b'')
        with patch.object(Path, 'read_bytes', changed):
            fails(lambda: a.fresh(job), f'Changed visual rule accepted: {relative}')
    raw = png()
    assert a.png_size(raw) == [1536, 1024]
    for damaged in (b'not a png', raw[:-1], raw+b'extra', raw[:50]+bytes([raw[50]^1])+raw[51:]):
        fails(lambda: a.png_size(damaged), 'Corrupt PNG accepted')
    snap = {'target_size': [1536, 1024], 'panel': '001-01', 'source': 'fixture', 'board': '<svg/>',
            'scene': {'border': 'default', 'reconstructed': True}, 'palette': {'steel': '#5E737B'},
            'placed': [], 'lettering': {}, 'sources': {}}
    assert 'stroke-dasharray' in a.compose({'snapshot': snap}, raw)
    plain = dict(snap, scene={'border': 'none', 'reconstructed': True})
    assert '<rect' not in a.compose({'snapshot': plain}, raw)
    with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
        root = Path(folder); table = root/'data/panel-art.tsv'; table.parent.mkdir()
        original_read, original_scan = p.read_table, p.scan
        stack.enter_context(patch.object(a, 'ROOT', root))
        stack.enter_context(patch.object(p, 'ROOT', root))
        stack.enter_context(patch.object(p, 'ART_DIR', root/'assets/art/panels'))
        stack.enter_context(patch.object(p, 'TABLE', table))
        stack.enter_context(patch.object(p, 'read_table', lambda path=None: original_read(path or table)))
        stack.enter_context(patch.object(p, 'scan', lambda path=None: original_scan(path or table)))
        stack.enter_context(patch.object(a, 'snapshot', lambda panel: snap))
        stack.enter_context(patch.object(a, 'rasterize', lambda svg: raw))
        stack.enter_context(patch.object(a.imagegen, 'compose_panel', lambda *args, **kw: 'fixture prompt'))
        stack.enter_context(patch.object(a.produce, 'register_for', lambda panel: 'fixture'))
        prompt_file = root/'edit.txt'; prompt_file.write_text('Keep geometry. Remove invented text.')
        path = root/'queue.sqlite3'
        args = Namespace(job='first', panel='001-01', depends=[], reference=[], prompt_file=prompt_file,
                         priority=0, max_attempts=2)
        with a.database(path, create=True) as db:
            first = a.prepare(db, args)
            fails(lambda: a.prepare(db, args), 'Duplicate job permitted')
            args.job='second'; args.depends=['first']; args.priority=10
            a.prepare(db, args)
            job = a.claim(db)
            assert job['id'] == 'first', 'Dependent job ran too early'
            fails(lambda: a.claim(db, 'first'), 'Job claimed twice')
            fails(lambda: a.receive(db, job, png(20, 20), 1), 'Wrong dimensions accepted')
            a.receive(db, job, raw, 1)
            a.receive(db, a.get(db, 'first'), raw, 1)
            assert len(a.get(db, 'first')['attempts']) == 1
            assert not p.discover(), 'Pending output leaked into reader store'
            fails(lambda: a.review(db, job, 'accept', ''), 'Review note omitted')
            with patch.object(a, 'snapshot', lambda panel: dict(snap, source='changed')):
                fails(lambda: a.review(db, job, 'accept', 'reviewed'), 'Stale source accepted')
            a.review(db, job, 'reject', 'text: invented glyphs')
            a.retry(db, job, prompt_file.read_text())
            job = a.claim(db, 'first')
            assert job['attempts'][-1]['references'][0]['role'] == 'edit-source'
            a.receive(db, job, raw, 2)
            assert len(job['attempts']) == 2
        # Simulate a crash after immutable store write but before table/queue commit.
        with a.database(path) as db:
            job = a.get(db, 'first')
            provider = 'art-job-first-a02'
            saved = p.store('001-01', a.compose(job, raw).encode(), '.svg', provider=provider)
        with a.database(path) as db:
            job = a.get(db, 'first')
            a.review(db, job, 'accept', 'Composition and lettered sequence reviewed')
            assert job['promotion']['file'] == str(saved.relative_to(root))
            assert len(p.discover()) == 1, 'Crash recovery created a duplicate variant'
            a.review(db, a.get(db, 'first'), 'accept', 'repeat delivery')
            assert len(p.discover()) == 1
            chosen = p.pick(p.read_table())
            assert chosen.status == p.CHOSEN and chosen.stage == 'refined'
            second = a.claim(db)
            assert second['id'] == 'second'
            assert second['attempts'][-1]['references'][-1]['role'] == 'accepted-dependency'
            a.receive(db, second, raw, 1)
            a.review(db, second, 'reject', 'continuity')
            a.retry(db, second, 'correction')
            second = a.claim(db, 'second'); a.receive(db, second, raw, 1)
            a.review(db, second, 'reject', 'still wrong')
            fails(lambda: a.retry(db, second, 'again'), 'Retry limit bypassed')
            with patch.object(p, 'resolve', lambda *args: None), patch.object(a.letterpress, 'svg_layer', lambda *args: ''):
                out = root/'review'
                a.export(db, out)
                handoff = json.loads((out/'first/handoff.json').read_text())
                assert handoff['arguments']['prompt'] == prompt_file.read_text()
                assert (out/'first/attempt-02.png').read_bytes() == raw
                assert 'getBBox' in (out/'index.html').read_text()
        # A stale blocked job remains inspectable but cannot re-enter generation.
        with a.database(path) as db:
            args.job = 'stale'; args.depends = []
            stale = a.prepare(db, args)
            with patch.object(a, 'snapshot', lambda panel: dict(snap, source='changed')):
                fails(lambda: a.check_job(db, stale), 'Runnable stale job passed check')
                a.transition(stale, 'blocked', 'Source changed; preserve the old inputs')
                a.save(db, stale)
                a.check_job(db, stale)
                fails(lambda: a.claim(db, 'stale'), 'Blocked stale job was claimed')
                fails(lambda: a.retry(db, stale, 'new prompt'), 'Stale snapshot silently refreshed')
        # SQLite must reject a second writer and roll back interrupted state changes.
        with a.database(path) as db:
            with sqlite3.connect(path, timeout=0) as other:
                fails(lambda: other.execute('BEGIN IMMEDIATE'), 'Concurrent writer admitted')
        try:
            with a.database(path) as db:
                db.execute("DELETE FROM jobs WHERE id='first'")
                raise RuntimeError('simulated interruption')
        except RuntimeError:
            pass
        with a.database(path) as db:
            assert a.get(db, 'first')['state'] == 'accepted'
