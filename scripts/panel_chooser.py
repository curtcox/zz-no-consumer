#!/usr/bin/env python3
"""Choose the best version of one panel, one panel at a time.

    python3 scripts/panel_chooser.py serve
    python3 scripts/panel_chooser.py serve --panel 045-03 --port 8765
    python3 scripts/panel_chooser.py check

`panelart.py list` answers *what versions exist*; this answers *which one wins*,
by putting every image generated for a panel key on one screen and recording the
decision where the book reads it. The panel key is the address: the browser sits
at `/045-03`, so editing the URL is a way to navigate, and Prior/Next walk the
whole book in reading order across page boundaries.

Three stores feed one screen, and they are not equal:

  * `assets/art/panels/NNN-II/` — the tracked variants in `data/panel-art.tsv`.
    These are selectable; Choose and Reject go straight through `panelart`.
  * `256t/panel-candidates/NNN-II/<sha>/` — local candidates, outside the
    repository and in no table. Choosing one has to copy it into the store
    first, so its button says Promote & choose and asks before it writes.
  * the text placeholder and the storyboard render — generated on demand from
    the script and `data/storyboards.json`. They are layout stand-ins, not
    artwork, so they are shown for reference and cannot be chosen.

The chosen version sorts first; everything else sorts newest first, which is the
order a re-roll pass wants to read. Decisions are written by `panelart.set_status`,
so this tool owns no curation rule of its own: one chosen version per panel, a
chosen version must be the panel's size, and the table is rescanned before every
write. Nothing here writes `docs/`; rebuild when you are done deciding.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import socket
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import panel_layout
import panelart
import storyboards
import textimage

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name("panel_chooser_ui")
CANDIDATES = ROOT / "256t" / "panel-candidates"
PANEL_KEY = re.compile(r"^\d{3}-\d{2}$")
SHA = re.compile(r"^[0-9a-f]{8,64}$")
UI_SNAPSHOT = {path.name: path.read_bytes() for path in sorted(UI.iterdir()) if path.is_file()}

TRACKED, LOCAL, GENERATED = "tracked", "candidate", "generated"
EPOCH = datetime.min.replace(tzinfo=timezone.utc)


def shown(path: Path) -> str:
    """A path as it should be named to a person: repository-relative when it is one."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def moment(value: str | None) -> datetime:
    """An ISO timestamp as a comparable instant; anything unreadable sorts oldest."""
    try:
        stamp = datetime.fromisoformat(value or "")
    except (TypeError, ValueError):
        return EPOCH
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class Choice:
    """One image a person could pick for a panel, whatever store it came from."""
    id: str
    kind: str
    url: str
    created: str = ""
    status: str = panelart.CANDIDATE
    stage: str = ""
    provider: str = ""
    seed: str = ""
    note: str = ""
    bytes: int = 0
    width: str = ""
    height: str = ""
    file: str = ""      # the image's own name, which is what the file server needs
    source: str = ""    # where it lives, as it should be named to a person

    def payload(self) -> dict:
        record = dict(vars(self))
        record["selectable"] = self.kind in (TRACKED, LOCAL)
        record["promote"] = self.kind == LOCAL
        return record


def book_panels() -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Every panel key in reading order, with its page title and script text."""
    keys, titles, text = [], {}, {}
    for script in textimage.book_scripts():
        for panel in script.panels:
            key = f"{script.id}-{panel.index:02d}"
            keys.append(key)
            titles[key] = script.title
            text[key] = panel.text
    return keys, titles, text


def local_candidates(panel: str) -> list[Choice]:
    """The untracked local candidates for a panel, read from their receipts."""
    directory = CANDIDATES / panel
    if not directory.is_dir():
        return []
    found = []
    for entry in sorted(directory.iterdir()):
        receipt = entry / "receipt.json"
        if not entry.is_dir() or not receipt.is_file():
            continue
        try:
            record = json.loads(receipt.read_text(encoding="utf-8"))
            image = entry / record["file"]
            request = record.get("request", {})
        except (OSError, ValueError, KeyError):
            continue
        if not image.is_file() or image.suffix.lower() not in panelart.SUFFIXES:
            continue
        width, height = panelart.measure(image)
        found.append(Choice(
            id=entry.name, kind=LOCAL, url=f"/candidate/{panel}/{entry.name}",
            created=record.get("at", ""), status=record.get("status", panelart.CANDIDATE),
            stage="refined", provider=(request.get("provider") or {}).get("id", ""),
            seed=str(request.get("seed", "")), bytes=image.stat().st_size,
            width=width, height=height, file=image.name, source=shown(image),
            note="Local candidate, not in the tracked store.",
        ))
    return found


class Session:
    """The book's panels, and the art store cached between decisions."""

    def __init__(self, start: str | None = None):
        self.keys, self.titles, self.text = book_panels()
        if not self.keys:
            raise ValueError("The book has no panels")
        self.place = {key: index for index, key in enumerate(self.keys)}
        self.lock = threading.Lock()
        self.variants: dict[str, list[panelart.Variant]] = {}
        self.refresh()
        self.start = start or self.first_undecided()
        if self.start not in self.place:
            raise ValueError(f"{self.start} is not a panel in this book")

    def refresh(self) -> None:
        """Re-read the store, keeping the decisions already recorded."""
        merged, _, _ = panelart.scan(panelart.TABLE)
        self.variants = panelart.by_panel(merged)

    def first_undecided(self) -> str:
        """Where a review pass wants to start: the first panel nobody has decided."""
        return next((key for key in self.keys
                     if not any(v.status == panelart.CHOSEN for v in self.variants.get(key, []))),
                    self.keys[0])

    def tracked(self, panel: str) -> list[Choice]:
        return [Choice(
            id=v.variant, kind=TRACKED,
            url="/art/" + v.path.relative_to(panelart.ART_DIR).as_posix(),
            created=v.created, status=v.status, stage=v.stage, provider=v.provider,
            seed=v.seed, note=v.note, width=v.width, height=v.height,
            bytes=int(v.bytes) if v.bytes.isdigit() else 0,
            file=v.path.name, source=v.file,
        ) for v in self.variants.get(panel, []) if v.path.is_file()]

    def generated(self, panel: str) -> list[Choice]:
        """Layout stand-ins rendered on demand; reference only, never selectable."""
        width, height = panel_layout.target(panel)
        made = [Choice(id="placeholder", kind=GENERATED, url=f"/placeholder/{panel}.svg",
                       provider="text placeholder", stage="layout",
                       width=f"{width:g}", height=f"{height:g}",
                       note="Rendered from the panel script.")]
        if panel in storyboards.load()["scenes"]:
            made.append(Choice(id="storyboard", kind=GENERATED, url=f"/storyboard/{panel}.svg",
                               provider="storyboard render", stage="storyboard",
                               width=f"{width:g}", height=f"{height:g}",
                               note="Rendered from data/storyboards.json, lettered."))
        return made

    def choices(self, panel: str) -> list[Choice]:
        """The chosen version first, then every other image newest first."""
        found = self.tracked(panel) + local_candidates(panel)
        found.sort(key=lambda choice: moment(choice.created), reverse=True)
        found.sort(key=lambda choice: choice.status != panelart.CHOSEN)   # stable
        return found

    def view(self, panel: str) -> dict:
        if panel not in self.place:
            raise ValueError(f"{panel} is not a panel in this book")
        at = self.place[panel]
        found = self.choices(panel)
        width, height = panel_layout.target(panel)
        decided = sum(1 for key in self.keys
                      if any(v.status == panelart.CHOSEN for v in self.variants.get(key, [])))
        return dict(
            panel=panel, page=panel[:3], title=self.titles[panel], script=self.text[panel],
            target=dict(width=width, height=height),
            prior=self.keys[at - 1] if at else None,
            next=self.keys[at + 1] if at + 1 < len(self.keys) else None,
            position=at + 1, total=len(self.keys), decided=decided,
            chosen=next((c.id for c in found if c.status == panelart.CHOSEN), None),
            choices=[c.payload() for c in found],
            reference=[c.payload() for c in self.generated(panel)],
        )

    # ----------------------------------------------------------- decisions

    def decide(self, panel: str, variant: str, action: str) -> dict:
        """Record a decision about a tracked version, then re-read the store."""
        status = {"choose": panelart.CHOSEN, "reject": panelart.REJECTED,
                  "clear": panelart.CANDIDATE}[action]
        with self.lock:
            panelart.set_status(panel, variant, status)
            self.refresh()
            return self.view(panel)

    def promote(self, panel: str, candidate: str) -> dict:
        """Copy a local candidate into the tracked store, then choose it.

        The size check runs before the copy, so a candidate that is not the
        panel's shape is refused without leaving an unusable variant behind.
        """
        match = next((c for c in local_candidates(panel) if c.id == candidate), None)
        if match is None:
            raise ValueError(f"{panel} has no local candidate {candidate}")
        source = CANDIDATES / panel / match.id / match.file
        with self.lock:
            panel_layout.require_size(panel_layout.dimensions(source),
                                      panel_layout.target(panel), f"{panel} {candidate[:12]}")
            stored = panelart.store(panel, source.read_bytes(), source.suffix,
                                    provider=match.provider, seed=match.seed)
            variant = panelart.VARIANT_FILE.match(stored.stem).group(1)
            panelart.set_status(panel, variant, panelart.CHOSEN,
                                note=f"Promoted from local candidate {candidate[:12]}.")
            self.refresh()
            return self.view(panel)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, session):
        self.session = session
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, body, kind="application/json", status=200):
        if isinstance(body, dict):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode("utf-8")
        textual = kind.startswith("text/") or kind in ("application/json", "image/svg+xml")
        self.send_response(status)
        self.send_header("Content-Type", kind + ("; charset=utf-8" if textual else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def file(self, root: Path, name: str):
        """Serve one image from a directory, never from outside it."""
        path = (root / unquote(name)).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            self.reply({"error": "Not found"}, status=404)
            return
        if path.suffix.lower() not in panelart.SUFFIXES:
            self.reply({"error": "Not an image"}, status=404)
            return
        self.reply(path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")

    def do_GET(self):
        session = self.server.session
        path = urlsplit(self.path).path
        try:
            if path == "/":
                self.redirect("/" + session.start)
            elif PANEL_KEY.match(path[1:]):
                # A mistyped key is still a panel address: answer with the app, which
                # says what is wrong and leaves the address bar there to correct.
                self.reply(UI_SNAPSHOT["index.html"], "text/html",
                           status=200 if path[1:] in session.place else 404)
            elif path in ("/app.js", "/app.css"):
                self.reply(UI_SNAPSHOT[path[1:]],
                           mimetypes.guess_type(path)[0] or "application/octet-stream")
            elif match := re.fullmatch(r"/api/panel/(\d{3}-\d{2})", path):
                self.reply(session.view(match.group(1)))
            elif path == "/api/panels":
                self.reply(dict(start=session.start, panels=session.keys))
            elif match := re.fullmatch(r"/candidate/(\d{3}-\d{2})/([0-9a-f]{8,64})", path):
                panel, name = match.groups()
                # Resolve through the receipt rather than guessing a filename, so
                # only a candidate this tool actually listed can be read.
                found = next((c for c in local_candidates(panel) if c.id == name), None)
                if found is None:
                    self.reply({"error": "Not found"}, status=404)
                else:
                    self.file(CANDIDATES, f"{panel}/{name}/{found.file}")
            elif match := re.fullmatch(r"/placeholder/(\d{3}-\d{2})\.svg", path):
                self.reply(session_placeholder(session, match.group(1)), "image/svg+xml")
            elif match := re.fullmatch(r"/storyboard/(\d{3}-\d{2})\.svg", path):
                self.reply(session_storyboard(match.group(1)), "image/svg+xml")
            elif path.startswith("/art/"):
                self.file(panelart.ART_DIR, path[len("/art/"):])
            else:
                self.reply({"error": "Not found"}, status=404)
        except (KeyError, ValueError, StopIteration) as error:
            self.reply({"error": str(error) or "Invalid request"}, status=400)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass

    def do_POST(self):
        session = self.server.session
        path = urlsplit(self.path).path
        if path not in ("/api/decide", "/api/promote"):
            self.reply({"error": "Not found"}, status=404)
            return
        # No cross-origin browser can record a decision in this checkout.
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host", ""):
            self.reply({"error": "Cross-origin decision refused"}, status=403)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 2048 or self.headers.get_content_type() != "application/json":
                raise ValueError("Expected a small JSON request")
            self.connection.settimeout(10)
            request = json.loads(self.rfile.read(length))
            panel, target = str(request.get("panel", "")), str(request.get("id", ""))
            if not PANEL_KEY.match(panel):
                raise ValueError("Expected a panel key like 045-03")
            if path == "/api/promote":
                if not SHA.match(target):
                    raise ValueError("Expected a local candidate identifier")
                self.reply(session.promote(panel, target))
            else:
                if not re.fullmatch(r"v\d{2,}", target):
                    raise ValueError("Expected a tracked variant like v03")
                self.reply(session.decide(panel, target, str(request.get("action", ""))))
        except KeyError:
            self.reply({"error": "Expected action choose, reject, or clear"}, status=400)
        except (ValueError, TimeoutError) as error:
            self.reply({"error": str(error) or "Invalid decision"}, status=400)


def session_placeholder(session: Session, panel: str) -> str:
    page, index = panel.split("-")
    return textimage.text_image(session.text[panel], *panel_layout.target(panel),
                                label=f"PAGE {page} · PANEL {index} · PLACEHOLDER")


def session_storyboard(panel: str) -> str:
    data = storyboards.load()
    if panel not in data["scenes"]:
        raise ValueError(f"{panel} has no storyboard scene")
    return storyboards.preview(panel, data["scenes"][panel], data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["serve", "check"])
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: loopback)")
    parser.add_argument("--port", type=int, default=8010)
    parser.add_argument("--panel", help="panel to open first (default: the first undecided one)")
    args = parser.parse_args()
    if args.command == "check":
        from panel_chooser_checks import check
        check()
        return 0
    session = Session(args.panel)
    with Server((args.host, args.port), session) as server:
        port = server.server_port
        print(f"Panel chooser: http://localhost:{port}/{session.start}", flush=True)
        print(f"{session.view(session.start)['decided']} of {len(session.keys)} panels decided. "
              f"Edit the URL to jump to a panel. Ctrl-C stops the session.", flush=True)
        if args.host not in ("127.0.0.1", "localhost"):
            print(f"LAN: http://{socket.gethostname()}:{port}/ — decisions write this checkout.",
                  flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
