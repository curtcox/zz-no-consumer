#!/usr/bin/env python3
"""Validate the generated novella reader, its page anchors, and its four downloads.

The viewer validator cannot cover this tree: it asserts eight-direction controls and
image/text modes that a prose reader deliberately does not have. What matters here is
different, and it is mostly one thing — **an address that stops working is a broken
bookmark**. So every story page must have exactly one anchor, in exactly one chapter,
reachable from the contents; a page that lost its anchor, or gained a second one in
another chapter, fails the build rather than quietly sending readers to the wrong
chapter months later.

The downloads are checked as artifacts, not as links: an EPUB is opened and its page
list counted against the manifest, and the single-file HTML is checked for the outside
references that would make it stop working the moment it is off the network.

    python3 scripts/validate-novella.py
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ElementTree
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
NOVELLA = ROOT / "docs" / "novella"
SLUG = "zz-no-consumer-novella"
DOWNLOADS = (f"{SLUG}.epub", f"{SLUG}.html", f"{SLUG}.md", f"{SLUG}.txt")
NAV_KEYS = {"home", "next", "previous"}
SETTING_OPTIONS = {"theme=dark", "theme=light", "full=off", "full=on"}


class ReaderParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body_attributes: dict[str, str] = {}
        self.links: list[str] = []
        self.downloads: set[str] = set()
        self.anchors: list[str] = []
        self.settings: set[str] = set()
        self.has_settings_panel = False
        self.scripts: list[str] = []
        self.stylesheets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "body":
            self.body_attributes = values
        if "data-settings-panel" in values:
            self.has_settings_panel = True
        if values.get("data-setting"):
            self.settings.add(f"{values['data-setting']}={values.get('data-value', '')}")
        if tag == "section" and values.get("id", "").startswith("p"):
            self.anchors.append(values["id"])
        if tag == "script" and values.get("src"):
            self.scripts.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet":
            self.stylesheets.append(values.get("href", ""))
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
            if "download" in values:
                self.downloads.add(values["href"])


def local_target(source: Path, href: str) -> Path | None:
    split = urlsplit(href)
    if split.scheme or split.netloc or not split.path:
        return None
    target = (source.parent / unquote(split.path)).resolve()
    if split.path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def prose_census() -> tuple[int, list[str]]:
    """What the prose tree actually holds: its word count, and every page title.

    Read straight from `content/novella/`, so a download is measured against the source
    rather than against another generated file that could be wrong in the same way.
    """
    words = 0
    titles: list[str] = []
    for path in sorted((ROOT / "content" / "novella").rglob("*.md")):
        if not re.fullmatch(r"\d{3}\.md", path.name):
            continue
        text = path.read_text(encoding="utf-8")
        body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
        body = re.sub(r"^#\s+.*$", "", body, count=1, flags=re.MULTILINE)
        words += len(re.findall(r"[A-Za-z0-9']+", body))
        title = re.search(r"^title:\s*(.+?)\s*$", text, flags=re.MULTILINE)
        if title:
            titles.append(title.group(1).strip().strip('"'))
    return words, titles


def story_pages() -> list[int]:
    manifest = (ROOT / "data" / "pages.yaml").read_text(encoding="utf-8")
    return [int(value) for value in re.findall(r'^\s*- \{id: "(\d{3})",', manifest, re.MULTILINE)]


def check_epub(path: Path, pages: list[int], failures: list[str]) -> None:
    if not zipfile.is_zipfile(path):
        failures.append(f"{path.name} is not a zip archive")
        return
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if not entries or entries[0].filename != "mimetype":
            failures.append(f"{path.name}: mimetype is not the first entry")
        elif entries[0].compress_type != zipfile.ZIP_STORED:
            failures.append(f"{path.name}: mimetype is compressed")
        elif archive.read("mimetype") != b"application/epub+zip":
            failures.append(f"{path.name}: mimetype holds the wrong value")

        names = {entry.filename for entry in entries}
        for required in ("META-INF/container.xml", "EPUB/package.opf", "EPUB/nav.xhtml"):
            if required not in names:
                failures.append(f"{path.name}: missing {required}")
        if failures:
            return

        for name in sorted(names):
            if name.endswith((".xhtml", ".opf", ".xml")):
                try:
                    ElementTree.fromstring(archive.read(name))
                except ElementTree.ParseError as error:
                    failures.append(f"{path.name}: {name} is not well-formed XML ({error})")

        package = archive.read("EPUB/package.opf").decode("utf-8")
        spine = re.findall(r'<itemref idref="([^"]+)"', package)
        manifest_ids = set(re.findall(r'<item id="([^"]+)"', package))
        for reference in spine:
            if reference not in manifest_ids:
                failures.append(f"{path.name}: spine names {reference}, which the manifest does not")
        if "dcterms:modified" not in package:
            failures.append(f"{path.name}: the package declares no dcterms:modified")

        nav = archive.read("EPUB/nav.xhtml").decode("utf-8")
        if 'epub:type="page-list"' not in nav:
            failures.append(f"{path.name}: no page list, so the cited page numbers are unreachable")
        else:
            listed = re.search(
                r'epub:type="page-list".*?<ol>(.*?)</ol>', nav, flags=re.DOTALL
            )
            labels = re.findall(r">(\d{3})</a>", listed.group(1)) if listed else []
            if [int(value) for value in labels] != pages:
                failures.append(
                    f"{path.name}: the page list holds {len(labels)} pages, "
                    f"not the manifest's {len(pages)}"
                )
        breaks = sum(
            archive.read(name).decode("utf-8").count('epub:type="pagebreak"')
            for name in names
            if name.endswith(".xhtml") and name != "EPUB/nav.xhtml"
        )
        if breaks != len(pages):
            failures.append(f"{path.name}: {breaks} page breaks for {len(pages)} story pages")


def check_standalone(path: Path, pages: list[int], failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    parser = ReaderParser()
    parser.feed(text)
    # The point of this file is that it keeps working with nothing else present.
    for href in parser.stylesheets:
        failures.append(f"{path.name}: links an external stylesheet ({href})")
    for src in parser.scripts:
        failures.append(f"{path.name}: loads an external script ({src})")
    if "<style>" not in text:
        failures.append(f"{path.name}: carries no inline stylesheet")
    found = sorted(int(anchor[1:]) for anchor in parser.anchors)
    if found != pages:
        failures.append(f"{path.name}: holds {len(found)} pages, not the manifest's {len(pages)}")


def main() -> int:
    failures: list[str] = []
    pages = story_pages()
    if not pages:
        failures.append("The page manifest lists no story pages")

    home = NOVELLA / "index.html"
    if not home.exists():
        print("Novella validation failed:\n- The novella was not generated; run scripts/build-site.py")
        return 1

    for asset in ("reader.css", "reader.js"):
        if not (NOVELLA / asset).exists():
            failures.append(f"Missing {asset}")

    documents = sorted(NOVELLA.rglob("index.html"))
    parsed: dict[Path, ReaderParser] = {}
    anchor_home: dict[int, list[Path]] = {}
    for document in documents:
        parser = ReaderParser()
        parser.feed(document.read_text(encoding="utf-8"))
        parsed[document.resolve()] = parser
        where = document.relative_to(ROOT)

        missing_nav = {f"data-nav-{key}" for key in NAV_KEYS} - parser.body_attributes.keys()
        if missing_nav:
            failures.append(f"{where}: missing navigation {sorted(missing_nav)}")
        if not parser.has_settings_panel:
            failures.append(f"{where}: missing the view settings panel")
        missing_settings = SETTING_OPTIONS - parser.settings
        if missing_settings:
            failures.append(f"{where}: missing settings {sorted(missing_settings)}")

        for href in parser.links:
            target = local_target(document, href)
            if target is not None and not target.exists():
                failures.append(f"{where}: broken link {href}")

        for anchor in parser.anchors:
            if not re.fullmatch(r"p\d{3}", anchor):
                failures.append(f"{where}: malformed page anchor {anchor}")
                continue
            anchor_home.setdefault(int(anchor[1:]), []).append(document)

    # One anchor, one chapter, one address. A page with two homes is a broken bookmark.
    for number in pages:
        homes = anchor_home.get(number, [])
        if not homes:
            failures.append(f"Page {number:03d} has no anchor in any chapter")
        elif len(homes) > 1:
            names = sorted(str(path.relative_to(ROOT)) for path in homes)
            failures.append(f"Page {number:03d} is anchored in more than one place: {names}")
    for number in sorted(set(anchor_home) - set(pages)):
        failures.append(f"Page {number:03d} is anchored but is not in the page manifest")

    # Every page must be reachable from the contents, or the index is decoration.
    contents = parsed.get(home.resolve())
    if contents:
        listed = {
            int(match.group(1))
            for href in contents.links
            if (match := re.search(r"#p(\d{3})$", href))
        }
        for number in sorted(set(pages) - listed):
            failures.append(f"Page {number:03d} is not linked from the novella contents")

        for name in DOWNLOADS:
            if name not in contents.downloads:
                failures.append(f"The contents page does not offer {name} as a download")

    # The spacebar chain: home, every chapter once, back to home.
    if contents:
        visited: set[Path] = set()
        current = home.resolve()
        while current in parsed and current not in visited:
            visited.add(current)
            following = local_target(current, parsed[current].body_attributes.get("data-nav-next", ""))
            if following is None:
                failures.append(f"{current.relative_to(ROOT)}: data-nav-next does not resolve")
                break
            current = following.resolve()
        else:
            if current != home.resolve():
                failures.append(
                    f"The reading chain rejoins at {current.relative_to(ROOT)} instead of the contents"
                )
        unreached = set(parsed) - visited
        if unreached:
            names = sorted(str(path.relative_to(ROOT)) for path in unreached)
            failures.append(f"{len(unreached)} novella routes are unreachable: {names}")

    for name in DOWNLOADS:
        path = NOVELLA / name
        if not path.exists():
            failures.append(f"Missing download {name}")
        elif path.stat().st_size == 0:
            failures.append(f"Download {name} is empty")

    if (NOVELLA / f"{SLUG}.epub").exists():
        check_epub(NOVELLA / f"{SLUG}.epub", pages, failures)
    if (NOVELLA / f"{SLUG}.html").exists():
        check_standalone(NOVELLA / f"{SLUG}.html", pages, failures)

    # The plain downloads carry no markup to inspect, so check them by content: every
    # page's title has to be there, and the whole thing has to weigh what the prose
    # tree weighs. A silently truncated download is the failure worth catching.
    source_words, titles = prose_census()
    for name in (f"{SLUG}.md", f"{SLUG}.txt", f"{SLUG}.html"):
        path = NOVELLA / name
        if not path.exists():
            continue
        # The HTML download escapes apostrophes; compare against what a reader sees.
        text = html.unescape(path.read_text(encoding="utf-8"))
        absent = [title for title in titles if title not in text]
        if absent:
            failures.append(
                f"{name}: {len(absent)} page titles are missing, starting with {absent[0]!r}"
            )
        words = len(re.findall(r"[A-Za-z0-9']+", text))
        if words < source_words:
            failures.append(
                f"{name}: {words:,} words against the prose tree's {source_words:,}"
            )

    if failures:
        print("Novella validation failed:")
        for failure in failures[:50]:
            print(f"- {failure}")
        if len(failures) > 50:
            print(f"- …and {len(failures) - 50} more")
        return 1

    print(
        f"Validated {len(documents)} novella routes, {len(pages)} page anchors, "
        f"{len(DOWNLOADS)} downloads, the EPUB page list, and the reading chain; "
        "every page has exactly one address and the contents reaches all of them."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
