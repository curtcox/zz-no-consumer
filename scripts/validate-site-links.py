#!/usr/bin/env python3
"""Check generated HTML/EPUB links and explicit Markdown download anchors.

Run after build-site.py. External URLs are deliberately not fetched. --out accepts
the internal review build as well as the default public docs tree.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.anchors: set[str] = set()
        self.duplicates: set[str] = set()
        self.references: list[tuple[int, str]] = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        anchor = values.get("id")
        if anchor:
            if anchor in self.anchors:
                self.duplicates.add(anchor)
            self.anchors.add(anchor)
        if tag == "a" and values.get("name"):
            self.anchors.add(values["name"])
        for attr in ("href", "src", "poster", "data"):
            if attr == "data" and tag != "object":
                continue
            if values.get(attr):
                self.references.append((self.getpos()[0], values[attr]))


def audit_documents(out: Path, documents: dict[Path, Document], files: set[Path]) -> list[str]:
    failures = []
    for source, document in documents.items():
        label = source.relative_to(out)
        for anchor in sorted(document.duplicates):
            failures.append(f"{label}: duplicate id {anchor!r}")
        for line, href in document.references:
            address = urlsplit(href)
            if address.scheme or address.netloc:
                continue
            path = unquote(address.path)
            target = ((out / path.lstrip("/")) if path.startswith("/") else
                      (source.parent / path) if path else source).resolve()
            if not target.is_relative_to(out):
                failures.append(f"{label}:{line}: link escapes site: {href}")
                continue
            if target / "index.html" in files:
                target /= "index.html"
            if target not in files:
                failures.append(f"{label}:{line}: missing target: {href}")
                continue
            fragment = unquote(address.fragment)
            # Text fragments are interpreted by the browser, not HTML element IDs.
            fragment = fragment.split(":~:text=", 1)[0]
            if fragment and target in documents and fragment not in documents[target].anchors:
                failures.append(f"{label}:{line}: missing fragment: {href}")
    return failures


def audit(out: Path) -> tuple[int, list[str]]:
    out = out.resolve()
    files = {path.resolve() for path in out.rglob("*") if path.is_file()}
    documents = {path: Document(path.read_text(encoding="utf-8"))
                 for path in sorted(files) if path.suffix == ".html"}
    failures = audit_documents(out, documents, files)
    if not documents:
        failures.append("No HTML documents found; build the site first")
    # Read the EPUB in memory. Its relative links resolve within the archive,
    # independently of files that happen to exist next to the download.
    for path in sorted(files):
        if path.suffix == ".md":
            failures.extend(f"{path.relative_to(out)}: {failure}"
                            for failure in audit_markdown(path.read_text(encoding="utf-8")))
        if path.suffix != ".epub":
            continue
        with zipfile.ZipFile(path) as archive:
            members = {(out / name).resolve(): name for name in archive.namelist()
                       if not name.endswith("/")}
            book = {target: Document(archive.read(name).decode("utf-8"))
                    for target, name in members.items() if name.endswith((".xhtml", ".opf"))}
            failures.extend(f"{path.relative_to(out)}: {failure}"
                            for failure in audit_documents(out, book, set(members)))
    return len(documents), failures


def audit_markdown(text: str) -> list[str]:
    """Downloads use explicit IDs rather than depending on a renderer's slug rules."""
    document = Document(text)
    failures = [f"duplicate id {anchor!r}" for anchor in sorted(document.duplicates)]
    for match in re.finditer(r"\]\(#([^)]+)\)", text):
        if unquote(match.group(1)) not in document.anchors:
            failures.append(f"missing explicit Markdown anchor: #{match.group(1)}")
    return failures


def check_regressions() -> None:
    assert not audit_markdown('<a id="entry"></a>\n\n[Read](#entry)')
    assert audit_markdown('### Entry\n\n[Read](#entry)')
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "chapter").mkdir()
        (root / "chapter" / "index.html").write_text('<h1 id="a b">Chapter</h1>')
        home = root / "index.html"
        home.write_text('<a href="chapter/?view=all#a%20b">Read</a>'
                        '<a href="https://example.invalid/missing">External</a>'
                        '<h1 id="home">Home</h1><a href="#home">Home</a>'
                        '<a href="/chapter/#a%20b">Root</a>')
        assert audit(root) == (2, []), audit(root)
        for markup, expected in (
            ('<a href="chapter/#absent">Read</a>', "missing fragment"),
            ('<a href="#absent">Read</a>', "missing fragment"),
            ('<img src="absent.svg">', "missing target"),
            ('<a href="../outside.html">Read</a>', "escapes site"),
            ('<h1 id="x">One</h1><h2 id="x">Two</h2>', "duplicate id"),
        ):
            home.write_text(markup)
            failures = audit(root)[1]
            assert len(failures) == 1 and expected in failures[0], failures
        home.write_text("<h1>Home</h1>")
        with zipfile.ZipFile(root / "book.epub", "w") as archive:
            archive.writestr("EPUB/nav.xhtml", '<a href="appendix.xhtml#entry">Read</a>')
            archive.writestr("EPUB/appendix.xhtml", '<h1 id="entry">Entry</h1>')
        assert audit(root) == (2, []), audit(root)
        with zipfile.ZipFile(root / "book.epub", "w") as archive:
            archive.writestr("EPUB/nav.xhtml", '<a href="appendix.xhtml#missing">Read</a>')
            archive.writestr("EPUB/appendix.xhtml", '<h1 id="entry">Entry</h1>')
        assert "missing fragment" in audit(root)[1][0], audit(root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "docs")
    args = parser.parse_args()
    check_regressions()
    count, failures = audit(args.out)
    for failure in failures:
        print(f"- {failure}")
    print(f"Site link check: {count} HTML documents, EPUB links and Markdown anchors, {len(failures)} findings.")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
