"""Offline regression checks for local_viewer.py; no publication writes."""
import concurrent.futures
import http.client
import json
import math
import re
import threading
from urllib.parse import urlsplit
from xml.etree import ElementTree
from unittest.mock import patch


def check():
    from local_viewer import MODES, Server, Session, spread
    import viewer_overlays as overlays
    session = Session()
    check_overlay_selection(overlays)
    assert spread(1, session.pages) == (None, 1)
    assert spread(2, session.pages) == spread(3, session.pages) == (2, 3)
    assert spread(4, {1: None, 2: None, 3: None, 4: None}) == (4, None)
    for bad in (True, 0, -1, '3', 1.5, None, 999999):
        try:
            session.select(bad)
            raise AssertionError(f'Accepted invalid page: {bad}')
        except ValueError:
            pass
    assert session.snapshot()['revision'] == 0
    with Server(('127.0.0.1', 0), session) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connections = []
        def request(path, method='GET', body=None, headers=None):
            conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=20)
            conn.request(method, path, body, headers or {})
            response = conn.getresponse()
            result = response.status, response.read()
            conn.close()
            return result
        def stream():
            conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=10)
            conn.request('GET', '/events')
            response = conn.getresponse()
            connections.append((conn, response))
            return response
        def event(response):
            while True:
                line = response.readline()
                if line.startswith(b'data: '):
                    return json.loads(line[6:])
                assert line, 'Event stream closed'
        try:
            assert len(json.loads(request('/api/catalog')[1])['modes']) == 10
            import local_viewer as local
            state = json.loads(request('/api/state')[1])
            assert state['layout_version'] == '2' and not state['restart_required']
            original_css = request('/app.css')[1]
            # A changed checkout cannot hot-load CSS into the old Python process.
            with patch.object(local, 'source_version', return_value='changed-checkout'):
                assert request('/app.css')[1] == original_css
                assert json.loads(request('/api/state')[1])['restart_required']
                assert request('/api/view?mode=right&page=1')[0] == 409
            for number, record in session.pages.items():
                body = session.render_page(number, 'art', overlays.DEFAULTS)
                assert 'data-panel-layout="2"' in body
                assert len(re.findall(r'<img style="left:', body)) == record.panel_count
                # Page-wide figures are extra images inside the page, never panels.
                assert len(re.findall(r'<img ', body)) == record.panel_count + len(re.findall(r'<img class="', body))
            # Independent long-lived readers all receive selection without polling.
            streams = [stream() for _ in range(12)]
            assert all(event(s)['page'] == 1 for s in streams)
            assert request('/api/state', 'POST', '{"page":3}', {'Content-Type': 'application/json'})[0] == 200
            assert all(event(s)['page'] == 3 for s in streams)
            assert event(stream())['page'] == 3  # late join/reconnection
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(session.select, range(4, 12)))
            assert session.snapshot()['revision'] == 9
            for mode in MODES:
                if mode == 'selector':
                    continue
                status, body = request(f'/api/view?mode={mode}&page=3')
                assert status == 200 and body, mode
                for url in re.findall(rb'(?:src|href)="([^"]+)"', body):
                    url = url.decode()
                    if url.startswith('/'):
                        assert request(url)[0] == 200, (mode, url)
            options = request('/api/view?mode=options-right&page=3')[1]
            assert b'rejected' in options and b'candidate' in options and b'chosen' in options
            assert b'Text placeholder' in options and b'storyboard' in options
            ElementTree.fromstring(request('/panel/001-01.svg')[1])
            ElementTree.fromstring(request('/placeholder/001-01.svg')[1])
            text = request('/api/view?mode=novella&page=3')[1]
            assert b'Page 003' in text and b'Page 002' not in text
            for path in ('/.git/config', '/art/%2e%2e/%2e%2e/%2e%2e/.git/config', '/art/', '/app.js/../local_viewer.py'):
                assert request(path)[0] == 404, path
            for path in ('/api/view?mode=wrong', '/api/view?page=-1', '/panel/001-99.svg'):
                assert request(path)[0] == 400, path
            assert request('/api/state', 'POST', '{"page":2}', {'Content-Type':'application/json', 'Origin':'https://other.example'})[0] == 403
            for body in ('[]', '{', '{"page":true}', '{"page":"2"}', '{"page":99999}'):
                assert request('/api/state', 'POST', body, {'Content-Type':'application/json'})[0] == 400
            assert request('/api/state', 'POST', '{"page":2}', {'Content-Type':'text/plain'})[0] == 400
            check_overlays(session, request, stream, event, overlays)
        finally:
            for conn, response in connections:
                response.close()
                conn.close()
            server.shutdown()
            thread.join(timeout=5)
    print('Local viewer checks passed: ten modes, four shared overlays, 12 live clients, reconnect, '
          'concurrent selectors, spread boundaries, all displayed assets, rejected art, separable and '
          'unseparable layers, deterministic fog and its off-panel pictograms, and HTTP '
          'input/path restrictions.')


def check_overlay_selection(overlays):
    """The switch set itself: complete, validated, and survivable through a URL."""
    assert set(overlays.LAYERS) == set(overlays.DEFAULTS) and all(overlays.DEFAULTS.values())
    assert set(overlays.PAGE_LAYERS) <= set(overlays.LAYERS)
    for chosen in ([], ['fog'], ['image', 'lettering'], list(overlays.LAYERS)):
        selection = {name: name in chosen for name in overlays.LAYERS}
        assert overlays.parse(overlays.signature(selection)) == selection, chosen
    assert overlays.parse(None, overlays.DEFAULTS) == overlays.DEFAULTS
    assert overlays.normalize({'fog': False}, overlays.DEFAULTS)['image'] is True
    for bad in ({'nope': True}, {'fog': 'no'}, {'fog': 1}, [], 'fog', None):
        try:
            overlays.normalize(bad)
            raise AssertionError(f'Accepted invalid overlay selection: {bad!r}')
        except ValueError:
            pass


def check_overlays(session, request, stream, event, overlays):
    """Withholding a layer, on every display, without touching a stored decision."""
    from pathlib import Path
    import letterpress
    import panel_layout
    page = session.page
    record = session.pages[page]
    all_on = dict(overlays.DEFAULTS)
    off = lambda name: dict(all_on, **{name: False})

    # A switch is shared state: it bumps the revision and reaches live displays.
    listener = stream()
    assert event(listener)['overlays'] == all_on
    before = session.snapshot()['revision']
    status, body = request('/api/state', 'POST', '{"overlays":{"fog":false}}',
                           {'Content-Type': 'application/json'})
    assert status == 200 and not json.loads(body)['overlays']['fog']
    assert json.loads(body)['revision'] == before + 1 and json.loads(body)['page'] == page
    assert event(listener)['overlay_signature'] == 'image,lettering,ants'
    assert request('/api/state', 'POST', '{"overlays":{"fog":true}}',
                   {'Content-Type': 'application/json'})[0] == 200
    assert session.snapshot()['overlays'] == all_on
    for bad in ('{"overlays":{"nope":true}}', '{"overlays":{"fog":"no"}}',
                '{"overlays":[]}', '{"colour":true}'):
        assert request('/api/state', 'POST', bad, {'Content-Type': 'application/json'})[0] == 400, bad
    assert json.loads(request('/api/catalog')[1])['overlays'].keys() == overlays.LAYERS.keys()

    # Every switch renders, and the requested set is what comes back.
    for name in overlays.LAYERS:
        status, body = request(f'/api/view?mode=right&page={page}&o={overlays.signature(off(name))}')
        assert status == 200, name
        assert f'o={overlays.signature(off(name))}'.encode() in body, name
        for url in re.findall(rb'(?:src|href)="([^"]+)"', body):
            if url.startswith(b'/'):
                assert request(url.decode())[0] == 200, (name, url)
    lit = session.panel(page, 1, all_on)
    assert '<image' in lit
    dark = session.panel(page, 1, off('image'))
    assert '<image' not in dark and 'stroke-dasharray="24 16"' in dark
    assert '<text' not in session.panel(page, 1, dict(off('image'), lettering=False))
    assert session.panel(page, 1, off('lettering')) != lit

    # Ants: authored geometry only, separated where the panel can give it up.
    anted = [number for number in session.pages if overlays.has_page_ants(number)]
    assert anted and all(overlays.ant_pages()[number] for number in anted)
    assert 108 not in anted, 'Page 108 keeps its deliberate exclusion'
    for number in anted:
        art = session.render_page(number, 'art', all_on)
        assert 'src="/overlay/ants/' in art and 'src="/overlay/fog/' in art
        assert 'src="/overlay/ants/' not in session.render_page(number, 'art', off('ants'))
    plain = next(number for number in session.pages if not overlays.has_page_ants(number))
    assert 'src="/overlay/ants/' not in session.render_page(plain, 'art', all_on)
    scenes = __import__('storyboards').load()
    separable = [(number, index) for number in session.pages
                 for index in range(1, session.pages[number].panel_count + 1)
                 if overlays.scene_ants(f'{number:03d}-{index:02d}', scenes)[1]]
    assert separable, 'No authored in-picture ants to separate'
    for number, index in separable:
        key, size = f'{number:03d}-{index:02d}', panel_layout.size(number, index)
        href, note = overlays.art_without_ants(key, letterpress.find_art(f'{number:03d}', index), size)
        assert href and not note, key
        assert session.panel(number, index, off('ants')) != session.panel(number, index, all_on)
        # A stored image that is not this scene's render keeps its ants and says so.
        raster, warning = overlays.art_without_ants(key, Path('chosen.webp'), size)
        assert raster is None and 'NOT SEPARABLE' in warning
        assert 'NOT SEPARABLE' in overlays.note_mark(warning, *size)

    # The fog is authored texture: deterministic, panel-derived, and disclaimed.
    rects = panel_layout.rectangles(record.panel_count)
    fog = request(f'/overlay/fog/{page:03d}.svg')[1]
    assert fog == request(f'/overlay/fog/{page:03d}.svg')[1]
    assert b'not a map of the wiki' in fog and b'data:image/png;base64,' in fog
    ElementTree.fromstring(fog)
    ElementTree.fromstring(request(f'/overlay/ants/{page:03d}.svg')[1])
    width, height, rows = overlays.veil_rows(page, record.panel_count)
    assert (width, height) == tuple(v // overlays.FOG_CELL for v in panel_layout.load()['page'])
    x, y, w, h = rects[0]
    inside = rows[(y + h // 2) // overlays.FOG_CELL][(x + w // 2) // overlays.FOG_CELL]
    ground = [rows[j][i] for j in range(height) for i in range(width)
              if all(overlays.rect_distance((i + 0.5) * overlays.FOG_CELL, (j + 0.5) * overlays.FOG_CELL, rect)
                     > overlays.FOG_FEATHER + overlays.FOG_DRIFT for rect in rects)]
    assert inside > max(ground), 'A panel must read more clearly than any fogged ground'
    assert max(ground) - min(ground) > 40, 'Fog that never thins can reveal nothing lying under it'

    # Pictograms lie on that ground and nowhere else, in borrowed forms that
    # carry none of the knowledge map's meaning onto a page.
    import knowledge_maps_fog
    assert overlays.glyph_forms() == sorted(knowledge_maps_fog.GLYPHS)
    forms = overlays.ground_glyphs(page, record.panel_count)
    assert forms == overlays.ground_glyphs(page, record.panel_count)
    assert fog.count(b'data-glyph="') == len(forms)
    # Every layout in the book, so no page shape can put a form over artwork.
    page_w, page_h = panel_layout.load()['page']
    for count, number in sorted({r.panel_count: n for n, r in session.pages.items()}.items()):
        shapes = panel_layout.rectangles(count)
        placed = overlays.ground_glyphs(number, count)
        assert len(placed) >= 12 and len({kind for kind, *_ in placed}) >= 12, count
        assert {kind for kind, *_ in placed} <= set(overlays.glyph_forms()), count
        for kind, gx, gy, scale, _ in placed:
            held = overlays.GLYPH_RADIUS * scale
            assert held < gx < page_w - held and held < gy < page_h - held, (count, kind)
            assert all(overlays.rect_distance(gx, gy, rect) >= held for rect in shapes), (count, kind)
        for index, (kind, gx, gy, *_) in enumerate(placed):
            assert all(kind != other or math.hypot(gx - ox, gy - oy) >= 420
                       for other, ox, oy, *_ in placed[index + 1:]), (count, kind)
    for path in ('/overlay/hills/001.svg', '/overlay/fog/999.svg'):
        assert request(path)[0] == 400, path
