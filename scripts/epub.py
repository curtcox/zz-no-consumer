#!/usr/bin/env python3
"""Write a reflowable EPUB 3 book from already-rendered XHTML chapter bodies.

Standard library only, on purpose. The repository's whole publishing chain is
dependency-free, and an EPUB is a zip of XML: adding a packaging library would buy
nothing but a version to pin.

The caller owns the prose. This module owns the container — mimetype ordering,
`container.xml`, the package document, the navigation document, and the spine — and
one thing the caller cannot easily do for itself: a real EPUB 3 **page list**. The
novella's prose cites its own page numbers, and the epilogue depends on a reader
being able to find them, so every story page emits a `pagebreak` marker and every
marker is listed in `nav.xhtml`. A conforming reading system turns that into a
go-to-page control.

    import epub
    epub.write(
        Path("book.epub"),
        epub.Metadata(title="…", author="…", identifier="…", language="en", rights="…"),
        [epub.Chapter(id="ch00", title="Prologue", body="<section>…</section>")],
        stylesheet="body{…}",
        page_list=[epub.PageRef(label="001", href="ch00.xhtml#p001")],
    )

Output is deterministic for a given input: every zip member is stamped with the same
timestamp, taken from `SOURCE_DATE_EPOCH` when it is set and from today's UTC date
otherwise, so a rebuild on the same day of unchanged prose produces an identical file.
"""

from __future__ import annotations

import html
import os
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Metadata:
    title: str
    author: str
    identifier: str
    language: str = "en"
    rights: str = ""
    description: str = ""
    publisher: str = ""


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    body: str


@dataclass(frozen=True)
class PageRef:
    label: str
    href: str


@dataclass(frozen=True)
class Item:
    """A non-spine manifest entry — a cover image, say."""

    id: str
    href: str
    media_type: str
    data: bytes
    properties: str = ""


CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def _timestamp() -> datetime:
    stamp = os.environ.get("SOURCE_DATE_EPOCH")
    if stamp and stamp.strip().isdigit():
        return datetime.fromtimestamp(int(stamp.strip()), tz=timezone.utc)
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def _document(title: str, body: str, *, stylesheet: bool = True) -> str:
    link = '\n  <link rel="stylesheet" type="text/css" href="style.css"/>' if stylesheet else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        'lang="en" xml:lang="en">\n<head>\n'
        f'  <meta charset="utf-8"/>\n  <title>{html.escape(title)}</title>{link}\n'
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


def _package(metadata: Metadata, chapters: list[Chapter], items: list[Item], modified: datetime) -> str:
    def element(tag: str, value: str, attributes: str = "") -> str:
        return f"    <{tag}{attributes}>{html.escape(value)}</{tag}>\n" if value else ""

    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n',
        '    <item id="style" href="style.css" media-type="text/css"/>\n',
    ]
    for chapter in chapters:
        manifest.append(
            f'    <item id="{chapter.id}" href="{chapter.id}.xhtml" '
            'media-type="application/xhtml+xml"/>\n'
        )
    for item in items:
        properties = f' properties="{item.properties}"' if item.properties else ""
        manifest.append(
            f'    <item id="{item.id}" href="{item.href}" '
            f'media-type="{item.media_type}"{properties}/>\n'
        )
    spine = "".join(f'    <itemref idref="{chapter.id}"/>\n' for chapter in chapters)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="book-id" xml:lang="en">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'    <dc:identifier id="book-id">{html.escape(metadata.identifier)}</dc:identifier>\n'
        f"{element('dc:title', metadata.title)}"
        f"{element('dc:language', metadata.language)}"
        f"{element('dc:creator', metadata.author)}"
        f"{element('dc:publisher', metadata.publisher)}"
        f"{element('dc:description', metadata.description)}"
        f"{element('dc:rights', metadata.rights)}"
        f'    <meta property="dcterms:modified">{modified.strftime("%Y-%m-%dT%H:%M:%SZ")}</meta>\n'
        "  </metadata>\n"
        f"  <manifest>\n{''.join(manifest)}  </manifest>\n"
        f"  <spine>\n{spine}  </spine>\n"
        "</package>\n"
    )


def _navigation(metadata: Metadata, chapters: list[Chapter], page_list: list[PageRef]) -> str:
    toc = "".join(
        f'      <li><a href="{chapter.id}.xhtml">{html.escape(chapter.title)}</a></li>\n'
        for chapter in chapters
    )
    body = (
        '<nav epub:type="toc" id="toc" role="doc-toc">\n'
        f"  <h1>{html.escape(metadata.title)}</h1>\n"
        f"  <ol>\n{toc}  </ol>\n</nav>\n"
    )
    if page_list:
        pages = "".join(
            f'      <li><a href="{page.href}">{html.escape(page.label)}</a></li>\n'
            for page in page_list
        )
        body += (
            '<nav epub:type="page-list" id="page-list" hidden="hidden">\n'
            "  <h1>Pages</h1>\n"
            f"  <ol>\n{pages}  </ol>\n</nav>\n"
        )
    return _document("Contents", body)


def write(
    destination: Path,
    metadata: Metadata,
    chapters: list[Chapter],
    *,
    stylesheet: str = "",
    page_list: list[PageRef] | None = None,
    items: list[Item] | None = None,
) -> Path:
    """Write the EPUB and return its path."""
    if not chapters:
        raise ValueError("An EPUB needs at least one chapter")
    identifiers = [chapter.id for chapter in chapters]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Chapter ids must be unique")

    items = list(items or [])
    page_list = list(page_list or [])
    modified = _timestamp()
    stamp = (modified.year, modified.month, modified.day, 0, 0, 0)
    destination.parent.mkdir(parents=True, exist_ok=True)

    def entry(name: str, compress: bool) -> zipfile.ZipInfo:
        info = zipfile.ZipInfo(name, date_time=stamp)
        info.compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
        info.external_attr = 0o644 << 16
        return info

    with zipfile.ZipFile(destination, "w") as archive:
        # The mimetype has to be the first entry and stored uncompressed.
        archive.writestr(entry("mimetype", False), "application/epub+zip")
        archive.writestr(entry("META-INF/container.xml", True), CONTAINER)
        archive.writestr(
            entry("EPUB/package.opf", True), _package(metadata, chapters, items, modified)
        )
        archive.writestr(
            entry("EPUB/nav.xhtml", True), _navigation(metadata, chapters, page_list)
        )
        archive.writestr(entry("EPUB/style.css", True), stylesheet)
        for chapter in chapters:
            archive.writestr(
                entry(f"EPUB/{chapter.id}.xhtml", True),
                _document(chapter.title, chapter.body),
            )
        for item in items:
            archive.writestr(entry(f"EPUB/{item.href}", True), item.data)
    return destination
