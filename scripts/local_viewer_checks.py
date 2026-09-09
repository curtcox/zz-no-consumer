"""Offline regression checks for local_viewer.py; no publication writes."""
import concurrent.futures
import http.client
import json
import re
import threading
from urllib.parse import urlsplit
from xml.etree import ElementTree
from unittest.mock import patch


def check():
    from local_viewer import MODES, Server, Session, spread
    session = Session()
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
                body = session.render_page(number, 'art')
                assert 'data-panel-layout="2"' in body
                assert len(re.findall(r'<img ', body)) == record.panel_count
                assert len(re.findall(r'<img style="left:', body)) == record.panel_count
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
        finally:
            for conn, response in connections:
                response.close()
                conn.close()
            server.shutdown()
            thread.join(timeout=5)
    print('Local viewer checks passed: ten modes, 12 live clients, reconnect, concurrent selectors, spread boundaries, all displayed assets, rejected art, and HTTP input/path restrictions.')
