#!/usr/bin/env python3
"""Generate local review candidates for every reader slot without accepted art.

plan is read-only; run saves one candidate per slot under 256t/panel-candidates.
Re-running resumes the same prompt/model/seed; change --seed for a new pass.
Candidates never enter reader selection automatically. No model is used by check.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import signal
import tempfile
import time

import imagegen
import panel_layout
import panelart
import produce

DEFAULT_OUT = produce.ROOT / '256t' / 'panel-candidates'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def accepted(slot, records) -> bool:
    return any(v.status == panelart.CHOSEN and v.stage in ('refined', 'final')
               and v.path.is_file() for v in records.get(slot.id, []))


def request(slot, provider, seed):
    return {
        'panel': slot.id, 'register': slot.register, 'provider': json.loads(json.dumps(asdict(provider))),
        'seed': seed, 'size': list(panel_layout.target(slot.id)),
        'prompt': imagegen.compose_panel(slot.page, slot.panel, slot.register,
                                         budget=provider.prompt_tokens),
    }


def destination(root, spec):
    key = digest(json.dumps(spec, sort_keys=True).encode())
    return root / spec['panel'] / key


def completed(folder, spec) -> bool:
    if not folder.exists():
        return False
    try:
        receipt = json.loads((folder / 'receipt.json').read_text())
        path = folder / receipt['file']
        if path.parent != folder or receipt['request'] != spec:
            raise ValueError('receipt does not match request')
        if digest(path.read_bytes()) != receipt['sha256']:
            raise ValueError('image hash mismatch')
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f'Cannot resume {folder}: {error}; preserve and inspect it first') from error
    return True


def pending(slots, records, provider, seed, root):
    for slot in slots:
        if not accepted(slot, records):
            spec = request(slot, provider, seed)
            if not completed(destination(root, spec), spec):
                yield slot, spec


def generate_one(slot, spec, provider, root):
    folder = destination(root, spec)
    folder.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    result = imagegen.generate(provider, spec['prompt'], spec['seed'], route='local',
                               size=tuple(spec['size']))
    if result.suffix not in ('.png', '.webp', '.jpg', '.jpeg'):
        raise ValueError(f'Unexpected model output suffix: {result.suffix}')
    with tempfile.TemporaryDirectory(prefix='.pending-', dir=folder.parent) as temp:
        stage = Path(temp)
        path = stage / ('candidate' + result.suffix)
        path.write_bytes(result.data)
        panel_layout.require_size(panel_layout.dimensions(path), tuple(spec['size']), slot.id)
        receipt = {
            'request': spec, 'file': path.name, 'sha256': digest(result.data),
            'status': 'candidate', 'at': datetime.now(timezone.utc).isoformat(),
            'seconds': round(time.monotonic() - started, 1),
        }
        (stage / 'prompt.txt').write_text(spec['prompt'], encoding='utf-8')
        (stage / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        stage.rename(folder)
    imagegen.log_generation({
        'at': receipt['at'], 'purpose': 'panel-candidate', 'route': 'local',
        'provider': provider.id, 'model': provider.model or provider.id,
        'page': slot.page, 'panel': slot.panel, 'register': slot.register,
        'seed': spec['seed'], 'size': spec['size'], 'seconds': receipt['seconds'],
        'usd': 0.0, 'path': str(folder / receipt['file']),
    })
    return folder


def execute(args, provider, slots):
    records = panelart.load(refresh=True)
    todo = list(pending(slots, records, provider, args.seed, args.out_dir))
    approved = sum(accepted(s, records) for s in slots)
    print(f'{len(slots)} slots; {approved} accepted; '
          f'{len(slots) - approved - len(todo)} candidates already saved; {len(todo)} pending.')
    if args.limit:
        todo = todo[:args.limit]
    print(f'Model: {provider.id}; seed: {args.seed}; '
          f'this pass: {len(todo)}; estimate: {produce.human(len(todo) * provider.seconds_per_image)}')
    if args.command == 'plan':
        for slot, spec in todo:
            print(f"{slot.id}  {spec['size'][0]}x{spec['size'][1]}")
        return 0
    if not todo:
        return 0
    previous = signal.getsignal(signal.SIGINT)
    stop = produce.Interrupt()
    made = failed = 0
    try:
        for index, (slot, spec) in enumerate(todo, 1):
            if stop.asked:
                break
            # Respect acceptances made after planning, including during a long run.
            if accepted(slot, panelart.load(refresh=True)):
                continue
            print(f'[{index}/{len(todo)}] Generating {slot.id}...', flush=True)
            try:
                folder = generate_one(slot, spec, provider, args.out_dir)
            except (RuntimeError, OSError, ValueError, KeyError, IndexError) as error:
                failed += 1
                print(f'{slot.id} FAILED: {error}', flush=True)
                # A broken runner should not be invoked hundreds more times.
                break
            made += 1
            print(f'Saved {folder}', flush=True)
    finally:
        signal.signal(signal.SIGINT, previous)
    print(f'Saved {made}; failed {failed}. Re-run the same command to resume.')
    return 1 if failed else 130 if stop.asked else 0


def check():
    """Disposable offline checks of eligibility, generation isolation, and resume."""
    from unittest.mock import patch
    import struct
    import zlib
    slot = produce.Slot('001', 1, 'prologue', 'creator')
    provider = imagegen.PROVIDERS_BY_ID['flux2-klein-4b']
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        existing = root / 'existing.png'
        existing.write_bytes(b'existing')
        variant = panelart.Variant(slot.id, 'v01', str(existing))
        for status, stage, expected in [
            ('candidate', 'refined', False), ('rejected', 'final', False),
            ('chosen', 'storyboard', False), ('chosen', 'refined', True),
            ('chosen', 'final', True),
        ]:
            assert accepted(slot, {slot.id: [replace(variant, status=status, stage=stage)]}) == expected
        assert not accepted(slot, {slot.id: [replace(variant, status='chosen', file=str(root / 'missing'))]})
        spec = {'panel': slot.id, 'register': slot.register, 'provider': json.loads(json.dumps(asdict(provider))),
                'seed': 42, 'size': [16, 16], 'prompt': 'fixture'}
        def chunk(kind, data):
            return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
        payload = (b'\x89PNG\r\n\x1a\n'
                   + chunk(b'IHDR', struct.pack('>IIBBBBB', 16, 16, 8, 2, 0, 0, 0))
                   + chunk(b'IDAT', zlib.compress((b'\0' + b'\xff' * 48) * 16))
                   + chunk(b'IEND', b''))
        with patch.object(imagegen, 'generate', return_value=imagegen.Generated(payload, '.png')) as model, \
             patch.object(imagegen, 'log_generation') as log, \
             patch.object(panelart, 'store', side_effect=AssertionError('must not promote')):
            folder = generate_one(slot, spec, provider, root)
            assert model.call_args.kwargs['route'] == 'local'
            assert log.call_count == 1
            assert completed(folder, spec)
            with patch(__name__ + '.request', return_value=spec):
                assert list(pending([slot], {}, provider, 42, root)) == []
            assert not completed(destination(root, dict(spec, seed=43)), dict(spec, seed=43))
            import contextlib
            import io
            args = argparse.Namespace(command='run', seed=42, limit=1, out_dir=root)
            other = replace(slot, panel=2)
            with patch.object(panelart, 'load', return_value={}), \
                 patch(__name__ + '.request', side_effect=lambda s, p, n: dict(spec, panel=s.id)), \
                 contextlib.redirect_stdout(io.StringIO()):
                # Resume skips the completed first slot before applying the limit.
                assert execute(args, provider, [slot, other]) == 0
                assert model.call_count == 2
                assert execute(args, provider, [slot, other]) == 0
                assert model.call_count == 2
                model.side_effect = RuntimeError('offline failure fixture')
                assert execute(args, provider, [replace(slot, panel=3)]) == 1
                assert not destination(root, dict(spec, panel='001-03')).exists()
            (folder / 'candidate.png').write_bytes(b'corrupt')
            try:
                completed(folder, spec)
            except ValueError:
                pass
            else:
                raise AssertionError('corruption was silently skipped')
    print('Panel candidate offline checks passed.')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'check'))
    parser.add_argument('--provider', default='flux2-klein-4b', help='local model from local-models.json')
    parser.add_argument('--seed', type=int, default=produce.DEFAULT_SEED)
    parser.add_argument('--limit', type=int, help='maximum pending panels in this invocation')
    parser.add_argument('--out-dir', type=Path, default=DEFAULT_OUT, help='candidate review directory')
    args = parser.parse_args()
    if args.command == 'check':
        return check()
    if args.limit is not None and args.limit < 1:
        parser.error('--limit must be positive')
    if args.seed < 0:
        parser.error('--seed must be non-negative')
    args.out_dir = args.out_dir.resolve()
    # Candidate output must never be discoverable as published artwork.
    if args.out_dir == produce.ROOT or args.out_dir.is_relative_to(produce.ROOT / 'assets') or \
            args.out_dir.is_relative_to(produce.ROOT / 'docs'):
        parser.error('--out-dir must be a separate review directory outside assets/ and docs/')
    provider = produce.provider_for(args.provider)
    if not provider.commercial:
        parser.error('choose a local model whose output is allowed in the book')
    slots = produce.all_slots()
    try:
        if args.command == 'plan':
            return execute(args, provider, slots)
        # POSIX flock releases on exit/crash; never remove a running process's lock.
        import fcntl
        args.out_dir.mkdir(parents=True, exist_ok=True)
        with (args.out_dir / '.run.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.error('another candidate run is using this output directory')
            return execute(args, provider, slots)
    except (OSError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
