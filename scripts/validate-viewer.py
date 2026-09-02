#!/usr/bin/env python3
"""Validate the generated viewer's permanent routes and directional controls."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "viewer"
DIRECTIONS = {"up", "down", "left", "right", "in", "out", "home"}


class ViewerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body_attributes: dict[str, str] = {}
        self.links: list[str] = []
        self.directions: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "body":
            self.body_attributes = values
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
            if values.get("data-direction"):
                self.directions.add(values["data-direction"])


def local_target(source: Path, href: str) -> Path | None:
    split = urlsplit(href)
    if split.scheme or split.netloc or not split.path:
        return None
    target = (source.parent / unquote(split.path)).resolve()
    if split.path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def main() -> int:
    failures: list[str] = []
    documents = sorted(VIEWER.rglob("index.html"))
    if not documents:
        failures.append("No viewer pages were generated")

    for document in documents:
        parser = ViewerParser()
        parser.feed(document.read_text(encoding="utf-8"))
        missing_controls = DIRECTIONS - parser.directions
        if missing_controls:
            failures.append(f"{document.relative_to(ROOT)}: missing controls {sorted(missing_controls)}")
        missing_data = {f"data-nav-{direction}" for direction in DIRECTIONS} - parser.body_attributes.keys()
        if missing_data:
            failures.append(f"{document.relative_to(ROOT)}: missing keyboard routes {sorted(missing_data)}")

        for href in parser.links:
            target = local_target(document, href)
            if target is not None and not target.exists():
                failures.append(f"{document.relative_to(ROOT)}: broken link {href}")

    expected = [
        VIEWER / "index.html",
        VIEWER / "chapters" / "prologue" / "index.html",
        VIEWER / "chapters" / "prologue" / "info" / "index.html",
        VIEWER / "pages" / "001" / "index.html",
        VIEWER / "pages" / "001" / "info" / "index.html",
        VIEWER / "pages" / "001" / "images" / "01" / "index.html",
        VIEWER / "pages" / "001" / "images" / "01" / "info" / "index.html",
        VIEWER / "pages" / "112" / "index.html",
    ]
    for path in expected:
        if not path.exists():
            failures.append(f"Missing representative route: {path.relative_to(ROOT)}")

    if failures:
        print("Viewer validation failed:")
        for failure in failures[:50]:
            print(f"- {failure}")
        if len(failures) > 50:
            print(f"- …and {len(failures) - 50} more")
        return 1

    print(f"Validated {len(documents)} viewer routes; all local links and seven-direction controls resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
