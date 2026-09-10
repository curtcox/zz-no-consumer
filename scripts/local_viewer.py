#!/usr/bin/env python3
"""Serve synchronized repository displays: python3 scripts/local_viewer.py serve."""
from __future__ import annotations

import argparse
import html
import hashlib
import importlib.util
import json
import mimetypes
from pathlib import Path
import re
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

import letterpress
import panel_layout
import novella
import panelart
import textimage
import viewer_overlays

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name("local_viewer_ui")
# Share the publication renderer without running its build or writing docs/.
_spec = importlib.util.spec_from_file_location("local_viewer_builder", ROOT / "scripts/build-site.py")
builder = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = builder
_spec.loader.exec_module(builder)
MODES = {
    "selector": "Page selector", "spread": "Graphic novel spread",
    "left": "Left graphic novel page", "right": "Right graphic novel page",
    "description": "Spread description", "description-left": "Left page description",
    "description-right": "Right page description", "novella": "Novella page text",
    "options-left": "Left page image options", "options-right": "Right page image options",
}


LAYOUT_VERSION = "2"
WATCHED = tuple(sorted((ROOT / 'scripts').glob('*.py'))) + tuple(sorted(UI.glob('*'))) + (ROOT / 'data/panel-layouts.json',)

def source_version():
    digest = hashlib.sha256()
    for path in WATCHED:
        digest.update(str(path.relative_to(ROOT)).encode())
        try:
            digest.update(path.read_bytes())
        except OSError:
            digest.update(b"missing")
    return digest.hexdigest()[:16]

# Snapshot code-compatible assets when this module loads, not on each HTTP request.
START_VERSION = source_version()
UI_SNAPSHOT = {path.name: path.read_bytes() for path in UI.iterdir() if path.is_file()}
UI_SNAPSHOT['app.js'] = UI_SNAPSHOT['panel-audit.js'] + b'\n' + UI_SNAPSHOT['app.js']


def spread(page: int, pages: dict) -> tuple[int | None, int | None]:
    left = page if page % 2 == 0 else page - 1
    return (left if left in pages else None, left + 1 if left + 1 in pages else None)


class Session:
    def __init__(self, initial: int = 1):
        self.pages = {int(p.id): p for p in builder.viewer_pages()}
        if initial not in self.pages:
            raise ValueError("Initial page is not in the book")
        self.page, self.revision = initial, 0
        self.overlays = dict(viewer_overlays.DEFAULTS)
        self.condition = threading.Condition()
        self.prose = novella.found()

    def snapshot(self):
        with self.condition:
            left, right = spread(self.page, self.pages)
            return dict(page=self.page, revision=self.revision, left=left, right=right,
                        overlays=dict(self.overlays), overlay_signature=viewer_overlays.signature(self.overlays),
                        layout_version=LAYOUT_VERSION, build=START_VERSION, restart_required=source_version() != START_VERSION)

    def update(self, request):
        """One shared selection: the page, the overlay switches, or both."""
        if not isinstance(request, dict):
            raise ValueError("Expected an object")
        unknown = sorted(set(request) - {'page', 'overlays'})
        if unknown:
            raise ValueError(f'Unknown selection field: {", ".join(unknown)}')
        page = request.get('page', self.page)
        if type(page) is not int or page not in self.pages:
            raise ValueError("Choose an existing integer page number")
        overlays = viewer_overlays.normalize(request['overlays'], self.overlays) if 'overlays' in request else dict(self.overlays)
        with self.condition:
            self.page, self.overlays = page, overlays
            self.revision += 1
            self.condition.notify_all()
            return self.snapshot()

    def select(self, page):
        return self.update({'page': page})

    def placeholder(self, page, index):
        script = textimage.page_script(f"{page:03d}")
        panel = next(p for p in script.panels if p.index == index)
        return textimage.text_image(panel.text, *panel_layout.size(page, index),
                                    label=f"PAGE {page:03d} · PANEL {index:02d} · PLACEHOLDER")

    def panel(self, page, index, overlays=None):
        overlays = viewer_overlays.DEFAULTS if overlays is None else overlays
        page_id, key = f"{page:03d}", f"{page:03d}-{index:02d}"
        width, height = panel_layout.size(page, index)
        # The text placeholder is this panel's picture, not a layer over one:
        # withholding the art withholds it too, and it carries no separate lettering.
        if not overlays['image']:
            record = letterpress.load_slots()
            placed = letterpress.panel_layout(page_id, index, record)[0] if overlays['lettering'] else []
            return viewer_overlays.annotate(letterpress.svg_panel(placed, record, width, height),
                                            [viewer_overlays.frame_mark(width, height)])
        art = letterpress.find_art(page_id, index)
        if not art:
            return self.placeholder(page, index)
        panel_layout.require(art, (width, height))
        marks, art_href = [], None
        if not overlays['ants']:
            art_href, note = viewer_overlays.art_without_ants(key, art, (width, height))
            if art_href:
                art = None
            if note:
                marks.append(viewer_overlays.note_mark(note, width, height))
        record = letterpress.load_slots()
        placed = letterpress.panel_layout(page_id, index, record)[0] if overlays['lettering'] else []
        return viewer_overlays.annotate(
            letterpress.svg_panel(placed, record, width, height, art=art, art_href=art_href), marks)

    def page_overlay(self, layer, page):
        return viewer_overlays.page_layer_svg(layer, page, self.pages[page].panel_count)

    def render_page(self, page, kind, overlays=None):
        overlays = viewer_overlays.DEFAULTS if overlays is None else overlays
        if page is None:
            return '<section class="blank" aria-label="Blank facing page">Blank facing page</section>'
        if source_version() != START_VERSION:
            raise ValueError("Viewer code changed; restart the local server")
        record = self.pages[page]
        heading = f'<h2>Page {page:03d} · {html.escape(record.title)}</h2>'
        if kind == "art":
            token = viewer_overlays.signature(overlays)
            images = ''.join(f'<img style="{panel_layout.style(record.panel_count, i)}" src="/panel/{page:03d}-{i:02d}.svg?o={token}" alt="Panel {page:03d}-{i:02d}">'
                             for i in range(1, record.panel_count + 1))
            # Page-wide figures sit above every panel, decorative and unable to
            # intercept a control, so the panel-fit audit still sees the panels.
            layers = ''.join(f'<img class="{layer}" src="/overlay/{layer}/{page:03d}.svg" alt="">'
                             for layer in viewer_overlays.PAGE_LAYERS
                             if overlays[layer] and (layer != 'ants' or viewer_overlays.has_page_ants(page)))
            overlay = f'<div class="page-overlay" aria-hidden="true">{layers}</div>' if layers else ''
            return f'<section>{heading}<div class="page-art" data-panel-layout="2" style="aspect-ratio:{panel_layout.load()["page"][0]}/{panel_layout.load()["page"][1]}" data-panels="{record.panel_count}">{images}{overlay}</div></section>'
        if kind == "options":
            # scan merges on-disk discoveries with decisions, but never writes the table.
            variants, _, _ = panelart.scan()
            groups = panelart.by_panel(variants)
            body = []
            for i in range(1, record.panel_count + 1):
                key = f"{page:03d}-{i:02d}"
                cells = [f'<figure><a href="/placeholder/{key}.svg" target="_blank"><img loading="lazy" src="/placeholder/{key}.svg" alt="Text placeholder {key}"></a><figcaption>Text placeholder · layout</figcaption></figure>']
                for v in groups.get(key, []):
                    url = '/art/' + v.path.relative_to(panelart.ART_DIR).as_posix()
                    label = f'{v.variant} · {v.status} · {v.stage} · {v.provider}'
                    cells.append(f'<figure><a href="{html.escape(url)}" target="_blank"><img loading="lazy" src="{html.escape(url)}" alt="{html.escape(key + " " + label)}"></a><figcaption>{html.escape(label)}<p>{html.escape(v.note)}</p></figcaption></figure>')
                body.append(f'<h3>Panel {key}</h3><div class="options">{"".join(cells)}</div>')
            return f'<section>{heading}{"".join(body)}</section>'
        if kind == "novella":
            paths = self.prose.get(page, [])
            source = novella.read_prose(paths[0]).body if paths else "No novella text for this page."
        else:
            source = (ROOT / 'content/pages' / f'{page:03d}.md').read_text(encoding='utf-8')
            source = re.sub(r'\A---\n.*?\n---\n', '', source, count=1, flags=re.S)
        # References open a static local reading, never change the shared selection.
        rendered = builder.markdown_to_html(source, lambda n: f'/reading/{kind}/{n:03d}')
        return f'<article class="prose">{heading}{rendered}</article>'

    def render(self, mode, page, overlays=None):
        overlays = self.overlays if overlays is None else overlays
        left, right = spread(page, self.pages)
        if mode == 'novella':
            return self.render_page(page, 'novella', overlays)
        kind = 'options' if mode.startswith('options-') else 'description' if mode.startswith('description') else 'art'
        if mode.endswith('left') or mode == 'left':
            return self.render_page(left, kind, overlays)
        if mode.endswith('right') or mode == 'right':
            return self.render_page(right, kind, overlays)
        return '<div class="spread">' + self.render_page(left, kind, overlays) + self.render_page(right, kind, overlays) + '</div>'


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128

    def __init__(self, address, session):
        self.session = session
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, body, kind='application/json', status=200):
        if isinstance(body, dict):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', kind + ('; charset=utf-8' if kind.startswith('text/') or kind == 'application/json' else ''))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Viewer-Build', START_VERSION)
        self.send_header('X-Panel-Layout', LAYOUT_VERSION)
        self.end_headers()
        self.wfile.write(body)

    def file(self, root, name):
        path = (root / unquote(name)).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            self.reply({'error': 'Not found'}, status=404)
            return
        if root == panelart.ART_DIR and path.suffix.lower() not in panelart.SUFFIXES:
            self.reply({'error': 'Not an image'}, status=404)
            return
        self.reply(path.read_bytes(), mimetypes.guess_type(path.name)[0] or 'application/octet-stream')

    def do_GET(self):
        session = self.server.session
        url = urlsplit(self.path)
        path = url.path
        try:
            if path == '/events':
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                self.connection.settimeout(20)
                revision = None
                while True:
                    with session.condition:
                        session.condition.wait_for(lambda: revision is None or session.revision != revision[0], timeout=10)
                        state = session.snapshot()
                    if (state['revision'], state['restart_required']) != revision:
                        self.wfile.write(('data: ' + json.dumps(state) + '\n\n').encode())
                        revision = (state['revision'], state['restart_required'])
                    else:
                        self.wfile.write(b': heartbeat\n\n')
                    self.wfile.flush()
            elif path == '/api/catalog':
                self.reply(dict(layout_version=LAYOUT_VERSION, build=START_VERSION, modes=MODES,
                                overlays={name: dict(label=label, note=note) for name, (label, note) in viewer_overlays.LAYERS.items()},
                                pages=[dict(number=n, title=p.title) for n, p in session.pages.items()]))
            elif path == '/api/state':
                self.reply(session.snapshot())
            elif path == '/api/view':
                if source_version() != START_VERSION:
                    self.reply({'error': 'Viewer code changed; restart the local server'}, status=409)
                    return
                query = parse_qs(url.query)
                mode = query.get('mode', ['spread'])[0]
                page = int(query.get('page', [str(session.page)])[0])
                if mode not in MODES or mode == 'selector' or page not in session.pages:
                    raise ValueError('Invalid display mode or page')
                # A display renders the overlay set it asked for, so a page it is
                # still fetching stays self-consistent with the images inside it.
                overlays = viewer_overlays.parse(query.get('o', [None])[0], session.overlays)
                self.reply(session.render(mode, page, overlays), 'text/html')
            elif match := re.fullmatch(r'/(panel|placeholder)/(\d{3})-(\d{2})\.svg', path):
                if source_version() != START_VERSION:
                    self.reply({'error': 'Viewer code changed; restart the local server'}, status=409)
                    return
                kind, page, index = match.groups()
                page, index = int(page), int(index)
                if page not in session.pages or not 1 <= index <= session.pages[page].panel_count:
                    raise ValueError('Unknown panel')
                overlays = viewer_overlays.parse(parse_qs(url.query).get('o', [None])[0], session.overlays)
                svg = session.panel(page, index, overlays) if kind == 'panel' else session.placeholder(page, index)
                self.reply(svg, 'image/svg+xml')
            elif match := re.fullmatch(r'/overlay/([a-z]+)/(\d{3})\.svg', path):
                if source_version() != START_VERSION:
                    self.reply({'error': 'Viewer code changed; restart the local server'}, status=409)
                    return
                layer, page = match.group(1), int(match.group(2))
                if layer not in viewer_overlays.PAGE_LAYERS or page not in session.pages:
                    raise ValueError('Unknown page overlay')
                self.reply(session.page_overlay(layer, page), 'image/svg+xml')
            elif match := re.fullmatch(r'/reading/(description|novella)/(\d{3})', path):
                kind, page = match.groups()
                if int(page) not in session.pages:
                    raise ValueError('Unknown page')
                body = session.render_page(int(page), kind)
                self.reply('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Local reading</title><link rel="stylesheet" href="/app.css"><main>' + body + '</main></html>', 'text/html')
            elif path.startswith('/art/'):
                self.file(panelart.ART_DIR, path[len('/art/'):])
            elif path in ('/', '/app.js', '/app.css', '/sync.js'):
                name = 'index.html' if path == '/' else path[1:]
                self.reply(UI_SNAPSHOT[name], mimetypes.guess_type(name)[0] or 'application/octet-stream')
            else:
                self.reply({'error': 'Not found'}, status=404)
        except (ValueError, StopIteration):
            self.reply({'error': 'Invalid page or mode'}, status=400)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass

    def do_POST(self):
        if self.path != '/api/state':
            self.reply({'error': 'Not found'}, status=404)
            return
        # No cross-origin browser can steer this LAN session.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            self.reply({'error': 'Cross-origin selection refused'}, status=403)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 1024 or self.headers.get_content_type() != 'application/json':
                raise ValueError('Expected a small JSON request')
            self.connection.settimeout(5)
            self.reply(self.server.session.update(json.loads(self.rfile.read(length))))
        except (ValueError, TimeoutError):
            self.reply({'error': 'Expected an existing integer page number, or overlay flags, in JSON'}, status=400)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['serve', 'check'])
    parser.add_argument('--host', default='0.0.0.0', help='bind address (default: all IPv4 interfaces)')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--page', type=int, default=1)
    args = parser.parse_args()
    if args.command == 'check':
        from local_viewer_checks import check
        check()
        return
    with Server((args.host, args.port), Session(args.page)) as server:
        port = server.server_port
        print(f'Local viewer: http://localhost:{port}/', flush=True)
        print(f'LAN: http://{socket.gethostname()}:{port}/ (or use this computer’s LAN IP)', flush=True)
        print(f'Listening on {args.host}:{port}. Ctrl-C stops the session.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
