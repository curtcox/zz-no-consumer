"""Offline regression checks for panel_chooser.py; no publication writes.

Every decision this tool can record rewrites `data/panel-art.tsv` and can copy a
file into `assets/art/panels/`, so the checks never touch either. They redirect
`panelart` at a temporary store built here, exercise the real server against it,
and assert on the fixture's own table. The book's panel list is read from
`content/`, which the checks only read.
"""
import http.client
import json
import os
import shutil
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800">'
       '<rect width="100%" height="100%" fill="#{fill}"/></svg>')
WRONG = ('<svg xmlns="http://www.w3.org/2000/svg" width="640" height="200">'
         '<rect width="100%" height="100%" fill="#333333"/></svg>')


def fixture(root: Path):
    """A two-panel art store and a local candidate tree, with nothing tracked yet."""
    art = root / "assets/art/panels"
    for panel, fills in (("001-01", "224466 448822 886644"), ("001-02", "112233 445566")):
        (art / panel).mkdir(parents=True)
        for number, fill in enumerate(fills.split(), 1):
            (art / panel / f"v{number:02d}-fixture-{1000 + number}.svg").write_text(
                SVG.format(fill=fill), encoding="utf-8")
    # Ordering is only testable if the versions do not share a modification time.
    for number, when in enumerate((1_700_000_000, 1_800_000_000, 1_750_000_000), 1):
        target = art / "001-01" / f"v{number:02d}-fixture-{1000 + number}.svg"
        os.utime(target, (when, when))

    candidates = root / "256t/panel-candidates"
    for name, body in (("a" * 64, SVG.format(fill="ff0000")), ("b" * 64, WRONG)):
        directory = candidates / "001-01" / name
        directory.mkdir(parents=True)
        (directory / "candidate.svg").write_text(body, encoding="utf-8")
        (directory / "receipt.json").write_text(json.dumps({
            "file": "candidate.svg", "status": "candidate", "at": "2026-09-09T12:00:00+00:00",
            "request": {"panel": "001-01", "seed": 2002,
                        "provider": {"id": "fixture-model"}},
        }), encoding="utf-8")
    # A directory with no receipt is not a candidate, and must not be served.
    (candidates / "001-01" / ("c" * 64)).mkdir(parents=True)
    return art, root / "data/panel-art.tsv", candidates


def check():
    import panel_chooser as chooser
    import panelart

    root = Path(tempfile.mkdtemp(prefix="panel-chooser-check-"))
    try:
        art, table, candidates = fixture(root)
        table.parent.mkdir(parents=True, exist_ok=True)
        with patch.object(panelart, "ROOT", root), patch.object(panelart, "ART_DIR", art), \
             patch.object(panelart, "TABLE", table), \
             patch.object(chooser, "CANDIDATES", candidates), \
             patch.object(panelart, "_CACHE", None):
            run(chooser, panelart, art, table, candidates)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("panel_chooser: checks passed")


def run(chooser, panelart, art, table, candidates):
    session = chooser.Session()
    keys = session.keys
    assert len(keys) > 100 and keys[0] == "001-01", keys[:3]
    assert all(chooser.PANEL_KEY.match(key) for key in keys)
    # Reading order is continuous across pages, which is what Prior/Next walks.
    assert session.view("001-05")["next"] == "002-01"
    assert session.view("001-01")["prior"] is None
    assert session.view(keys[-1])["next"] is None
    assert session.view("001-01")["position"] == 1

    for bad in ("", "1-1", "001-1", "999-01", "001-99", "../secret"):
        try:
            session.view(bad)
            raise AssertionError(f"Accepted an invalid panel: {bad!r}")
        except ValueError:
            pass

    # Nothing is chosen yet, so the pass starts at the very first panel.
    assert session.start == "001-01" and session.view("001-01")["chosen"] is None

    view = session.view("001-01")
    assert [c["id"] for c in view["choices"] if c["kind"] == "tracked"] == ["v02", "v03", "v01"], \
        "Untouched versions sort newest first"
    local = [c for c in view["choices"] if c["kind"] == "candidate"]
    assert len(local) == 2 and all(c["promote"] and c["selectable"] for c in local)
    assert {c["id"] for c in view["reference"]} == {"placeholder", "storyboard"}
    assert not any(c["selectable"] for c in view["reference"])
    assert view["target"] == {"width": 1200, "height": 800}

    # Choosing moves one version to the front and leaves the rest by recency.
    after = session.decide("001-01", "v01", "choose")
    assert [c["id"] for c in after["choices"] if c["kind"] == "tracked"] == ["v01", "v02", "v03"]
    assert after["chosen"] == "v01" and after["decided"] == 1
    assert "\tv01\t" in table.read_text() and "chosen" in table.read_text()

    # One chosen version per panel: panelart owns that rule, and it still holds.
    after = session.decide("001-01", "v03", "choose")
    assert after["chosen"] == "v03"
    assert [c["status"] for c in after["choices"] if c["id"] == "v01"] == ["candidate"]

    rejected = session.decide("001-01", "v02", "reject")
    assert [c["status"] for c in rejected["choices"] if c["id"] == "v02"] == ["rejected"]
    cleared = session.decide("001-01", "v02", "clear")
    assert [c["status"] for c in cleared["choices"] if c["id"] == "v02"] == ["candidate"]
    assert cleared["choices"][0]["id"] == "v03", "The chosen version stays first"

    for panel, variant in (("001-01", "v99"), ("003-01", "v01")):
        try:
            session.decide(panel, variant, "choose")
            raise AssertionError(f"Accepted an unknown version: {panel} {variant}")
        except ValueError:
            pass

    # A candidate that is not the panel's shape is refused before anything is copied.
    before = sorted(p.name for p in (art / "001-01").iterdir())
    try:
        session.promote("001-01", "b" * 64)
        raise AssertionError("Promoted a candidate of the wrong size")
    except ValueError as error:
        assert "does not match target" in str(error), error
    assert sorted(p.name for p in (art / "001-01").iterdir()) == before, "A refusal wrote a file"

    promoted = session.promote("001-01", "a" * 64)
    assert promoted["chosen"] == "v04" and (art / "001-01" / "v04-fixture-model-2002.svg").is_file()
    assert "Promoted from local candidate" in promoted["choices"][0]["note"]
    assert len([p for p in (art / "001-01").iterdir()]) == len(before) + 1
    try:
        session.promote("001-01", "c" * 64)
        raise AssertionError("Promoted a directory with no receipt")
    except ValueError:
        pass

    serve(chooser, session, art, candidates)


def serve(chooser, session, art, candidates):
    with chooser.Server(("127.0.0.1", 0), session) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(path, method="GET", body=None, headers=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=20)
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            result = (response.status, response.getheader("Location"), response.read())
            connection.close()
            return result

        def send(path, payload, headers=None):
            return request(path, "POST", json.dumps(payload),
                           {"Content-Type": "application/json", **(headers or {})})

        try:
            # The address bar is the navigation surface: a panel key is a real page.
            assert request("/")[:2] == (302, "/" + session.start)
            status, _, body = request("/001-01")
            assert status == 200 and b'src="/app.js"' in body
            # A well-formed key that is not in the book still gets the app, so the
            # person who mistyped it can see why and fix the address.
            missing = request("/999-01")
            assert missing[0] == 404 and b'src="/app.js"' in missing[2]
            assert json.loads(request("/nonsense")[2])["error"] == "Not found"
            assert request("/app.css")[0] == request("/app.js")[0] == 200

            view = json.loads(request("/api/panel/001-01")[2])
            assert view["chosen"] == "v04" and view["panel"] == "001-01"
            assert request("/api/panel/999-01")[0] == 400
            assert json.loads(request("/api/panels")[2])["panels"][0] == "001-01"

            # Images come back from all three stores, and from nowhere else.
            assert request("/art/001-01/v01-fixture-1001.svg")[:1] == (200,)
            assert request("/candidate/001-01/" + "a" * 64)[0] == 200
            assert request("/candidate/001-01/" + "c" * 64)[0] == 404
            assert request("/placeholder/001-01.svg")[0] == 200
            assert request("/storyboard/001-01.svg")[0] == 200
            for escape in ("/art/../../../etc/passwd", "/art/%2e%2e/%2e%2e/AGENTS.md",
                           "/candidate/001-01/" + "a" * 63 + "/"):
                assert request(escape)[0] == 404, escape
            (art / "001-01" / "notes.txt").write_text("not an image", encoding="utf-8")
            assert request("/art/001-01/notes.txt")[0] == 404

            # Writes are refused unless they come from this server's own page.
            assert send("/api/decide", {"panel": "001-01", "id": "v01", "action": "choose"},
                        {"Origin": "http://evil.example"})[0] == 403
            assert request("/api/decide", "POST")[0] == 400
            assert send("/api/decide", {"panel": "bad", "id": "v01", "action": "choose"})[0] == 400
            assert send("/api/decide", {"panel": "001-01", "id": "../x", "action": "choose"})[0] == 400
            assert send("/api/decide", {"panel": "001-01", "id": "v01", "action": "delete"})[0] == 400
            assert send("/api/promote", {"panel": "001-01", "id": "nothex"})[0] == 400
            assert send("/api/nothing", {})[0] == 404

            decided = json.loads(send("/api/decide",
                                      {"panel": "001-01", "id": "v01", "action": "choose"})[2])
            assert decided["chosen"] == "v01" and decided["choices"][0]["id"] == "v01"
        finally:
            server.shutdown()
