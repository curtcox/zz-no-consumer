#!/usr/bin/env python3
"""Build a dependency-free HTML reading site from the repository's Markdown."""

from __future__ import annotations

import argparse
import html
import posixpath
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import crossref
import textimage


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

# Viewer settings live in the page fragment. This runs before first paint so a
# restored view never flashes the default theme, chrome, or content mode.
SETTINGS_BOOT = """(function(){
var root=document.documentElement;
var allowed={theme:['dark','light'],nav:['on','off'],full:['off','on'],mode:['both','image','text']};
var chosen={theme:'dark',nav:'on',full:'off',mode:'both'};
(location.hash||'').replace(/^#/,'').split('&').forEach(function(pair){
var parts=pair.split('=');
var key=decodeURIComponent(parts[0]||'');
var value=decodeURIComponent(parts[1]||'');
if(allowed[key]&&allowed[key].indexOf(value)>-1){chosen[key]=value;}
});
Object.keys(chosen).forEach(function(key){root.setAttribute('data-'+key,chosen[key]);});
})();"""

SETTING_GROUPS = (
    ("Screen", "full", (("off", "Windowed"), ("on", "Full screen"))),
    ("Navigation icons", "nav", (("on", "Show"), ("off", "Hide"))),
    ("Appearance", "theme", (("dark", "Dark"), ("light", "Light"))),
    ("Content", "mode", (("both", "Image + text"), ("image", "Image only"), ("text", "Text only"))),
)


def settings_panel() -> str:
    groups = []
    for legend, setting, options in SETTING_GROUPS:
        buttons = "".join(
            f'<button class="settings__option" type="button" data-setting="{setting}" '
            f'data-value="{value}" aria-pressed="false">{html.escape(label)}</button>'
            for value, label in options
        )
        groups.append(
            f'<fieldset class="settings__group"><legend>{html.escape(legend)}</legend>'
            f'<div class="settings__options" role="group" aria-label="{html.escape(legend)}">{buttons}</div></fieldset>'
        )
    return (
        '<button class="settings-fab" type="button" data-settings-toggle aria-expanded="false"'
        ' aria-controls="view-settings" aria-label="View settings">\u2699</button>\n'
        '  <section class="settings" id="view-settings" data-settings-panel hidden aria-label="View settings">\n'
        '    <div class="settings__head"><p class="eyebrow">View settings</p>'
        '<button class="settings__close" type="button" data-settings-close aria-label="Close view settings">\u00d7</button></div>\n'
        f'    {"".join(groups)}\n'
        '    <p class="settings__note">These settings ride along in the page address, so a copied '
        'link reopens the same view. Press <kbd>S</kbd> to reopen this panel.</p>\n'
        '  </section>'
    )


def markdown_sources(internal: bool) -> list[Path]:
    if internal:
        return sorted(
            path
            for folder in ("content", "prompts", "research", "design")
            for path in (ROOT / folder).rglob("*.md")
        )
    public_files = [ROOT / "content" / "premise.md", ROOT / "content" / "source-links.md"]
    public_files.extend((ROOT / "content" / "chapters").rglob("*.md"))
    public_files.extend((ROOT / "content" / "pages").rglob("*.md"))
    return sorted(path for path in public_files if path.exists())


@dataclass(frozen=True)
class ViewerPage:
    id: str
    chapter: str
    sequence: str
    title: str
    status: str
    panel_count: int


@dataclass(frozen=True)
class ViewerChapter:
    id: str
    title: str
    first_page: int
    last_page: int


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', text)

    def link(match: re.Match[str]) -> str:
        label, target = match.groups()
        if not re.match(r"^[a-z][a-z0-9+.-]*://", target, flags=re.IGNORECASE) and not target.startswith("#"):
            target = re.sub(r"\.md(?=([?#]|$))", ".html", target)
        return f'<a href="{target}">{label}</a>'

    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def markdown_to_html(source: str) -> str:
    lines = source.replace("\r\n", "\n").split("\n")
    result: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = "ul"
    quote_lines: list[str] = []
    code_lines: list[str] = []
    code_language = ""
    in_code = False

    def flush_paragraph() -> None:
        if paragraph:
            result.append(f"<p>{inline(' '.join(part.strip() for part in paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            result.append(f"<{list_tag}>" + "".join(f"<li>{item}</li>" for item in list_items) + f"</{list_tag}>")
            list_items.clear()

    def flush_quote() -> None:
        if quote_lines:
            result.append(f"<blockquote><p>{inline(' '.join(quote_lines))}</p></blockquote>")
            quote_lines.clear()

    def flush_blocks() -> None:
        flush_paragraph(); flush_list(); flush_quote()

    def table_cells(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def is_table_separator(line: str) -> bool:
        cells = table_cells(line)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.strip()

        if line.startswith("```"):
            if in_code:
                language_attr = f' class="language-{html.escape(code_language)}"' if code_language else ""
                result.append(f"<pre><code{language_attr}>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines.clear()
                code_language = ""
                in_code = False
            else:
                flush_blocks()
                code_language = line[3:].strip()
                in_code = True
            index += 1
            continue

        if in_code:
            code_lines.append(raw)
            index += 1
            continue

        if (
            line.startswith("|")
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1].strip())
        ):
            flush_blocks()
            headers = table_cells(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(table_cells(lines[index].strip()))
                index += 1
            head = "".join(f"<th>{inline(cell)}</th>" for cell in headers)
            body_rows = []
            for row in rows:
                padded = row + [""] * max(0, len(headers) - len(row))
                body_rows.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in padded[:len(headers)]) + "</tr>")
            result.append(f"<div class=\"table-wrap\"><table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>")
            continue

        if line.startswith("#"):
            flush_blocks()
            level = min(len(line) - len(line.lstrip("#")), 6)
            result.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
        elif line.startswith(">"):
            flush_paragraph(); flush_list()
            quote_lines.append(line[1:].strip())
        elif re.match(r"^[-*] ", line):
            flush_paragraph(); flush_quote()
            if list_items and list_tag != "ul":
                flush_list()
            list_tag = "ul"
            list_items.append(inline(line[2:]))
        elif re.match(r"^\d+\. ", line):
            flush_paragraph(); flush_quote()
            if list_items and list_tag != "ol":
                flush_list()
            list_tag = "ol"
            list_items.append(inline(re.sub(r"^\d+\. ", "", line)))
        elif not line:
            flush_blocks()
        else:
            flush_list(); flush_quote()
            paragraph.append(line)
        index += 1

    if in_code:
        language_attr = f' class="language-{html.escape(code_language)}"' if code_language else ""
        result.append(f"<pre><code{language_attr}>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_blocks()
    return "\n".join(result)


def title_for(path: Path) -> str:
    first_heading = next(
        (line[1:].strip() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("#")),
        path.stem.replace("-", " ").title(),
    )
    return first_heading


def slug_for(path: Path) -> Path:
    relative = path.relative_to(ROOT)
    return Path("pages") / relative.with_suffix(".html")


def relative_url(from_directory: Path, target: Path) -> str:
    return posixpath.relpath(target.as_posix(), start=from_directory.as_posix())


def route_url(from_directory: Path, target: Path) -> str:
    """Return a relative, directory-style URL for a generated index page."""
    destination = target.parent if target.name == "index.html" else target
    value = relative_url(from_directory, destination)
    return "./" if value == "." else f"{value}/"


def viewer_pages() -> list[ViewerPage]:
    pattern = re.compile(
        r'^\s*- \{id: "(?P<id>\d+)", chapter: "(?P<chapter>[^"]+)", '
        r'sequence: "(?P<sequence>[^"]+)", title: "(?P<title>[^"]+)", status: (?P<status>\w+)\}'
    )
    records: list[ViewerPage] = []
    for line in (ROOT / "data" / "pages.yaml").read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        values = match.groupdict()
        source = ROOT / "content" / "pages" / f"{values['id']}.md"
        panel_count = 1
        if source.exists():
            panel_count = max(
                1,
                len(re.findall(r"^## Panel \d+\s*$", source.read_text(encoding="utf-8"), flags=re.MULTILINE)),
            )
        records.append(ViewerPage(panel_count=panel_count, **values))
    return records


def viewer_chapters() -> list[ViewerChapter]:
    source = (ROOT / "data" / "chapters.yaml").read_text(encoding="utf-8")
    chunks = re.split(r"(?=^\s*- id: )", source, flags=re.MULTILINE)[1:]
    records: list[ViewerChapter] = []
    for chunk in chunks:
        def value(key: str) -> str:
            prefix = r"\s+-\s+" if key == "id" else r"\s+"
            match = re.search(rf"^{prefix}{key}:\s+(.+?)\s*$", chunk, flags=re.MULTILINE)
            if not match:
                raise ValueError(f"Missing {key} in chapter record")
            return match.group(1).strip('"')

        records.append(
            ViewerChapter(
                id=value("id"),
                title=value("title"),
                first_page=int(value("first_page")),
                last_page=int(value("last_page")),
            )
        )
    return records


def viewer_destination(*parts: str) -> Path:
    return Path("viewer", *parts, "index.html")


def viewer_link(from_directory: Path, *parts: str) -> str:
    return route_url(from_directory, viewer_destination(*parts))


def viewer_document(
    *,
    title: str,
    eyebrow: str,
    body: str,
    destination: Path,
    nav: dict[str, tuple[str, Path]],
    entity_id: str,
    entity_kind: str,
) -> str:
    current_directory = destination.parent
    css_href = relative_url(current_directory, Path("viewer/viewer.css"))
    js_href = relative_url(current_directory, Path("viewer/viewer.js"))
    project_home = route_url(current_directory, Path("index.html"))
    nav_links = {
        key: route_url(current_directory, target)
        for key, (_, target) in nav.items()
    }

    def nav_item(direction: str, key: str, shortcut: str) -> str:
        label, _ = nav[key]
        glyphs = {
            "up": "↑", "down": "↓", "left": "←", "right": "→",
            "in": "+", "out": "−", "home": "⌂", "next": "▶",
        }
        return (
            f'<a class="wayfinder__item wayfinder__item--{direction}" '
            f'href="{html.escape(nav_links[key])}" data-direction="{key}" '
            f'aria-label="{html.escape(direction.title())}: {html.escape(label)}">'
            f'<span class="wayfinder__glyph" aria-hidden="true">{glyphs[direction]}</span>'
            f'<span class="wayfinder__text"><b>{html.escape(direction.title())}</b>'
            f'<small>{html.escape(label)}</small></span>'
            f'<kbd>{html.escape(shortcut)}</kbd></a>'
        )

    nav_attributes = "\n      ".join(
        f'data-nav-{key}="{html.escape(value)}"' for key, value in nav_links.items()
    )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <meta name="description" content="Validation viewer for {html.escape(title)} in zz-no-consumer.">
  <title>{html.escape(title)} — Viewer — zz-no-consumer</title>
  <link rel="stylesheet" href="{html.escape(css_href)}">
  <script>{SETTINGS_BOOT}</script>
</head>
<body data-entity-id="{html.escape(entity_id)}" data-entity-kind="{html.escape(entity_kind)}"
      {nav_attributes}>
  <a class="skip-link" href="#content">Skip to content</a>
  <header class="masthead">
    <a class="brand" href="{html.escape(viewer_link(current_directory))}" aria-label="Viewer home">
      <span class="brand__mark" aria-hidden="true">ZZ</span>
      <span><b>NO CONSUMER</b><small>Reader validation build</small></span>
    </a>
    <div class="masthead__actions">
      <button class="utility" type="button" data-bookmark aria-pressed="false">☆ <span>Bookmark</span></button>
      <button class="utility" type="button" data-copy-link>↗ <span>Copy link</span></button>
      <button class="utility utility--keys" type="button" data-shortcuts>⌨ <span>Keys</span></button>
      <button class="utility" type="button" data-settings-toggle aria-expanded="false"
              aria-controls="view-settings">⚙ <span>Settings</span></button>
      <a class="utility" href="{html.escape(project_home)}">Project site</a>
    </div>
  </header>
  <main id="content">
    <div class="view-heading" data-content="text">
      <p class="eyebrow">{html.escape(eyebrow)}</p>
      <h1>{html.escape(title)}</h1>
    </div>
    {body}
  </main>
  <nav class="wayfinder" aria-label="Spatial navigation">
    <p class="wayfinder__label">Move through the book</p>
    <div class="wayfinder__grid">
      {nav_item("up", "up", "↑")}
      {nav_item("left", "left", "←")}
      {nav_item("in", "in", "Enter")}
      {nav_item("right", "right", "→")}
      {nav_item("out", "out", "Esc")}
      {nav_item("down", "down", "↓")}
      {nav_item("home", "home", "H")}
      {nav_item("next", "next", "Space")}
    </div>
  </nav>
  {settings_panel()}
  <dialog class="shortcut-dialog" data-shortcut-dialog>
    <button class="shortcut-dialog__close" type="button" data-close-dialog aria-label="Close">×</button>
    <p class="eyebrow">Keyboard map</p>
    <h2>Move without losing your place.</h2>
    <dl><div><dt>← → ↑ ↓</dt><dd>Move left, right, up, or down</dd></div>
    <div><dt>Enter</dt><dd>Move in</dd></div><div><dt>Esc</dt><dd>Move out</dd></div>
    <div><dt>H</dt><dd>Viewer home</dd></div>
    <div><dt>Space</dt><dd>Read on: scroll this view, then the next node</dd></div>
    <div><dt>Shift + Space</dt><dd>Back up: scroll this view, then the previous node</dd></div>
    <div><dt>S</dt><dd>Open view settings</dd></div>
    <div><dt>F</dt><dd>Full screen on or off</dd></div>
    <div><dt>N</dt><dd>Navigation icons on or off</dd></div>
    <div><dt>D</dt><dd>Dark or light appearance</dd></div>
    <div><dt>M</dt><dd>Image + text, image only, or text only</dd></div>
    <div><dt>?</dt><dd>Show this map</dd></div></dl>
  </dialog>
  <div class="toast" role="status" aria-live="polite" data-toast></div>
  <script src="{html.escape(js_href)}" defer></script>
</body>
</html>
'''


PLACEHOLDER_DIR = Path("assets/placeholders")


def placeholder_url(from_directory: Path, image: textimage.Placeholder) -> str:
    return relative_url(from_directory, PLACEHOLDER_DIR / image.path)


def placeholder_img(
    from_directory: Path, image: textimage.Placeholder, css_class: str
) -> str:
    return (
        f'<img class="{css_class}" src="{html.escape(placeholder_url(from_directory, image))}" '
        f'alt="{html.escape(image.alt)}" width="{image.width}" height="{image.height}" '
        f'loading="lazy" decoding="async">'
    )


def page_art(
    page: ViewerPage, image: textimage.Placeholder, from_directory: Path, *, compact: bool = False
) -> str:
    compact_class = " page-art--compact" if compact else ""
    return (
        f'<div class="page-art page-art--sheet{compact_class}" data-content="image" '
        f'data-panels="{page.panel_count}">'
        f'{placeholder_img(from_directory, image, "page-art__sheet")}</div>'
    )


# One chain through every generated route, so the spacebar alone reaches all of
# the content and comes back to where it started.
READING_ORDER: list[tuple[Path, str]] = []
READING_INDEX: dict[Path, int] = {}


def linear_nav(current: Path) -> dict[str, tuple[str, Path]]:
    position = READING_INDEX[current]
    steps = {}
    for key, offset in (("next", 1), ("previous", -1)):
        destination, label = READING_ORDER[(position + offset) % len(READING_ORDER)]
        steps[key] = (label, destination)
    return steps


def write_viewer_page(destination: Path, *, nav: dict[str, tuple[str, Path]], **kwargs: object) -> None:
    full_destination = OUT / destination
    full_destination.parent.mkdir(parents=True, exist_ok=True)
    full_destination.write_text(
        viewer_document(destination=destination, nav={**nav, **linear_nav(destination)}, **kwargs),
        encoding="utf-8",
    )


def build_viewer() -> None:
    pages = viewer_pages()
    chapters = viewer_chapters()
    book = textimage.build_book(OUT / PLACEHOLDER_DIR)
    missing = [
        f"{page.id}-{index:02d}"
        for page in pages
        for index in range(1, page.panel_count + 1)
        if (page.id, index) not in book.panels
    ] + [page.id for page in pages if page.id not in book.pages]
    if missing:
        raise ValueError(f"No placeholder image was generated for: {missing}")
    page_by_number = {int(page.id): page for page in pages}
    chapter_by_id = {chapter.id: chapter for chapter in chapters}
    viewer_home = viewer_destination()

    def chapter_dest(chapter_id: str, info: bool = False) -> Path:
        return viewer_destination("chapters", chapter_id, *(('info',) if info else ()))

    def page_dest(page_id: str, info: bool = False) -> Path:
        return viewer_destination("pages", page_id, *(('info',) if info else ()))

    def image_dest(page_id: str, image_id: int, info: bool = False) -> Path:
        return viewer_destination("pages", page_id, "images", f"{image_id:02d}", *(('info',) if info else ()))

    def wrapped(items: list[object], index: int, offset: int) -> object:
        return items[(index + offset) % len(items)]

    READING_ORDER.clear()
    READING_ORDER.append((viewer_home, "Viewer home"))
    for chapter in chapters:
        READING_ORDER.append((chapter_dest(chapter.id), chapter.title))
        READING_ORDER.append((chapter_dest(chapter.id, True), f"About {chapter.title}"))
        for page in pages:
            if not chapter.first_page <= int(page.id) <= chapter.last_page:
                continue
            READING_ORDER.append((page_dest(page.id), f"Page {page.id}"))
            READING_ORDER.append((page_dest(page.id, True), f"About page {page.id}"))
            for image_index in range(1, page.panel_count + 1):
                READING_ORDER.append((image_dest(page.id, image_index), f"{page.id} · image {image_index:02d}"))
                READING_ORDER.append(
                    (image_dest(page.id, image_index, True), f"About {page.id}-{image_index:02d}")
                )
    READING_INDEX.clear()
    READING_INDEX.update({destination: index for index, (destination, _) in enumerate(READING_ORDER)})
    if len(READING_INDEX) != len(READING_ORDER):
        raise ValueError("The reading order visits a route more than once")

    chapter_cards = []
    for chapter in chapters:
        chapter_cards.append(
            f'''<a class="chapter-card" href="{html.escape(viewer_link(Path("viewer"), "chapters", chapter.id))}">
              <span class="chapter-card__index">{html.escape(chapter.id.upper())}</span>
              <span class="chapter-card__title">{html.escape(chapter.title)}</span>
              <span class="chapter-card__meta">Pages {chapter.first_page:03d}–{chapter.last_page:03d}</span>
            </a>'''
        )
    home_body = f'''
    <section class="intro-grid">
      <div class="intro-copy" data-content="text"><p class="kicker">A spatial reading prototype</p>
        <p>This build validates durable routes, page and panel hierarchy, eight-direction navigation, and shareable view settings. Every page and image slot already carries a generated placeholder: the script text for that page or panel, flowed to fit the frame the final art will occupy.</p>
        <a class="primary-action" href="{html.escape(viewer_link(Path("viewer"), "pages", pages[0].id))}">Begin on page 001 <span>→</span></a>
      </div>
      <div class="map-card" data-content="image" aria-label="Content map"><span>HOME</span><i></i><span>CHAPTER</span><i></i><span>PAGE</span><i></i><span>IMAGE</span></div>
    </section>
    <section class="section-block"><div class="section-heading"><div><p class="eyebrow">The complete route map</p><h2>Eight chapters. 112 permanent page addresses.</h2></div><span class="count">112 pages</span></div>
      <div class="chapter-grid">{''.join(chapter_cards)}</div>
    </section>
    <section class="bookmark-shelf" data-bookmark-shelf hidden><div class="section-heading"><div><p class="eyebrow">Saved on this device</p><h2>Your bookmarks</h2></div></div><div data-bookmark-list></div></section>
    '''
    write_viewer_page(
        viewer_home,
        title="Viewer field test",
        eyebrow="Prototype / no final artwork",
        body=home_body,
        entity_id="viewer-home",
        entity_kind="viewer",
        nav={
            "up": ("Project site", Path("index.html")),
            "down": (chapters[0].title, chapter_dest(chapters[0].id)),
            "left": (chapters[-1].title, chapter_dest(chapters[-1].id)),
            "right": (chapters[0].title, chapter_dest(chapters[0].id)),
            "in": ("Page 001", page_dest(pages[0].id)),
            "out": ("Project site", Path("index.html")),
            "home": ("Viewer home", viewer_home),
        },
    )

    for chapter_index, chapter in enumerate(chapters):
        chapter_pages = [
            page for page in pages
            if chapter.first_page <= int(page.id) <= chapter.last_page
        ]
        current_dir = chapter_dest(chapter.id).parent
        cards = []
        for page in chapter_pages:
            cards.append(
                f'''<a class="page-card" href="{html.escape(route_url(current_dir, page_dest(page.id)))}">
                  {page_art(page, book.pages[page.id], current_dir, compact=True)}
                  <span class="page-card__copy" data-content="text"><b>{html.escape(page.id)} · {html.escape(page.title)}</b><small>Sequence {html.escape(page.sequence)} · {html.escape(page.status)}</small></span>
                </a>'''
            )
        chapter_body = f'''
        <section class="chapter-intro"><div><p class="kicker">Chapter {html.escape(chapter.id.upper())}</p><p>{len(chapter_pages)} pages · {sum(page.panel_count for page in chapter_pages)} image slots · placeholder art</p></div>
          <a class="text-action" href="{html.escape(route_url(current_dir, chapter_dest(chapter.id, True)))}">Read chapter information <span>↓</span></a></section>
        <section class="page-grid" aria-label="Pages in {html.escape(chapter.title)}">{''.join(cards)}</section>
        '''
        previous_chapter = wrapped(chapters, chapter_index, -1)
        next_chapter = wrapped(chapters, chapter_index, 1)
        chapter_nav = {
            "up": ("Viewer home", viewer_home),
            "down": ("Chapter information", chapter_dest(chapter.id, True)),
            "left": (previous_chapter.title, chapter_dest(previous_chapter.id)),
            "right": (next_chapter.title, chapter_dest(next_chapter.id)),
            "in": ("First page", page_dest(chapter_pages[0].id)),
            "out": ("Viewer home", viewer_home),
            "home": ("Viewer home", viewer_home),
        }
        write_viewer_page(
            chapter_dest(chapter.id), title=chapter.title,
            eyebrow=f"Chapter {chapter.id.upper()} / pages {chapter.first_page:03d}–{chapter.last_page:03d}",
            body=chapter_body, nav=chapter_nav,
            entity_id=f"chapter-{chapter.id}", entity_kind="chapter",
        )
        info_dir = chapter_dest(chapter.id, True).parent
        info_body = f'''
        <section class="info-layout"><div class="info-lede"><p>Chapter record</p><p>The overview, this record, every page, and every image have independent URLs designed to survive the transition from placeholders to final art.</p></div>
        <dl class="metadata"><div><dt>Identifier</dt><dd>{html.escape(chapter.id)}</dd></div><div><dt>Page range</dt><dd>{chapter.first_page:03d}–{chapter.last_page:03d}</dd></div>
        <div><dt>Pages</dt><dd>{len(chapter_pages)}</dd></div><div><dt>Image slots</dt><dd>{sum(page.panel_count for page in chapter_pages)}</dd></div><div><dt>Artwork</dt><dd><span class="status-dot"></span> Placeholder</dd></div></dl></section>
        <a class="primary-action" href="{html.escape(route_url(info_dir, chapter_dest(chapter.id)))}">Return to chapter <span>↑</span></a>
        '''
        write_viewer_page(
            chapter_dest(chapter.id, True), title=f"About {chapter.title}", eyebrow=f"Chapter {chapter.id.upper()} / information",
            body=info_body, entity_id=f"chapter-{chapter.id}-info", entity_kind="chapter-info",
            nav={
                "up": ("Chapter overview", chapter_dest(chapter.id)),
                "down": ("First page information", page_dest(chapter_pages[0].id, True)),
                "left": (f"About {previous_chapter.title}", chapter_dest(previous_chapter.id, True)),
                "right": (f"About {next_chapter.title}", chapter_dest(next_chapter.id, True)),
                "in": ("Chapter overview", chapter_dest(chapter.id)),
                "out": ("Viewer home", viewer_home),
                "home": ("Viewer home", viewer_home),
            },
        )

    for page_index, page in enumerate(pages):
        current_dir = page_dest(page.id).parent
        chapter = chapter_by_id[page.chapter]
        previous_page = wrapped(pages, page_index, -1)
        next_page = wrapped(pages, page_index, 1)
        image_links = "".join(
            f'<a href="{html.escape(route_url(current_dir, image_dest(page.id, image_index)))}">Image {image_index:02d}</a>'
            for image_index in range(1, page.panel_count + 1)
        )
        page_body = f'''
        <section class="reader-layout">
          <div class="reader-stage" data-content="image"><div class="reader-stage__top"><span>Page {html.escape(page.id)} / 112</span><span class="art-state"><i></i> Placeholder artwork</span></div>
            <a class="page-art-link" href="{html.escape(route_url(current_dir, image_dest(page.id, 1)))}" aria-label="Open first image on page {html.escape(page.id)}">{page_art(page, book.pages[page.id], current_dir)}</a>
          </div>
          <aside class="reader-notes" data-content="text"><p class="eyebrow">Page record</p><h2>{html.escape(page.title)}</h2><dl><div><dt>Chapter</dt><dd>{html.escape(chapter.title)}</dd></div><div><dt>Sequence</dt><dd>{html.escape(page.sequence)}</dd></div><div><dt>Status</dt><dd>{html.escape(page.status)}</dd></div></dl>
            <div class="image-links"><span>Image slots</span>{image_links}</div>
            <a class="text-action" href="{html.escape(route_url(current_dir, page_dest(page.id, True)))}">Page information <span>↓</span></a>
          </aside>
        </section>
        '''
        page_nav = {
            "up": (chapter.title, chapter_dest(chapter.id)),
            "down": ("Page information", page_dest(page.id, True)),
            "left": (f"Page {previous_page.id}", page_dest(previous_page.id)),
            "right": (f"Page {next_page.id}", page_dest(next_page.id)),
            "in": ("First image", image_dest(page.id, 1)),
            "out": (chapter.title, chapter_dest(chapter.id)),
            "home": ("Viewer home", viewer_home),
        }
        write_viewer_page(
            page_dest(page.id), title=page.title,
            eyebrow=f"{chapter.title} / page {page.id}", body=page_body,
            nav=page_nav, entity_id=f"page-{page.id}", entity_kind="page",
        )
        info_dir = page_dest(page.id, True).parent
        source_file = ROOT / "content" / "pages" / f"{page.id}.md"
        source_label = f"content/pages/{page.id}.md" if source_file.exists() else "Planned; script not drafted"
        page_info_body = f'''
        <section class="info-layout"><div class="info-lede"><p>Page record</p><p>Production metadata is separated from the reading surface while remaining one directional move away.</p></div>
        <dl class="metadata"><div><dt>Page</dt><dd>{html.escape(page.id)} of 112</dd></div><div><dt>Title</dt><dd>{html.escape(page.title)}</dd></div><div><dt>Chapter</dt><dd>{html.escape(chapter.title)}</dd></div><div><dt>Sequence</dt><dd>{html.escape(page.sequence)}</dd></div><div><dt>Status</dt><dd>{html.escape(page.status)}</dd></div><div><dt>Image slots</dt><dd>{page.panel_count}</dd></div><div><dt>Artwork</dt><dd><span class="status-dot"></span> Placeholder</dd></div><div class="metadata__wide"><dt>Source</dt><dd>{html.escape(source_label)}</dd></div><div class="metadata__wide"><dt>Placeholder image</dt><dd><a href="{html.escape(placeholder_url(info_dir, book.pages[page.id]))}">assets/placeholders/{html.escape(book.pages[page.id].path)}</a> · {book.pages[page.id].width}×{book.pages[page.id].height}</dd></div><div class="metadata__wide"><dt>Cross reference</dt><dd><a href="{html.escape(crossref_link(info_dir, "pages", page.id))}">Sources and provenance cited by page {html.escape(page.id)}</a></dd></div></dl></section>
        <a class="primary-action" href="{html.escape(route_url(info_dir, page_dest(page.id)))}">Return to page <span>↑</span></a>
        '''
        write_viewer_page(
            page_dest(page.id, True), title=f"About page {page.id}", eyebrow=f"{page.title} / information",
            body=page_info_body, entity_id=f"page-{page.id}-info", entity_kind="page-info",
            nav={
                "up": ("Page view", page_dest(page.id)),
                "down": ("First image information", image_dest(page.id, 1, True)),
                "left": (f"About page {previous_page.id}", page_dest(previous_page.id, True)),
                "right": (f"About page {next_page.id}", page_dest(next_page.id, True)),
                "in": ("Page view", page_dest(page.id)),
                "out": ("Chapter information", chapter_dest(chapter.id, True)),
                "home": ("Viewer home", viewer_home),
            },
        )

        for image_index in range(1, page.panel_count + 1):
            image_current = image_dest(page.id, image_index)
            image_dir = image_current.parent
            previous_image = ((image_index - 2) % page.panel_count) + 1
            next_image = (image_index % page.panel_count) + 1
            image_body = f'''
            <section class="image-viewer"><div class="image-frame" id="image" data-content="image">{placeholder_img(image_dir, book.panels[(page.id, image_index)], "image-sheet")}</div>
            <div class="image-caption" data-content="text"><p><span>{html.escape(chapter.title)}</span> / Page {html.escape(page.id)}</p><h2>Image {image_index:02d} of {page.panel_count:02d}</h2><a class="text-action" href="{html.escape(route_url(image_dir, image_dest(page.id, image_index, True)))}">Image information <span>↓</span></a></div></section>
            '''
            write_viewer_page(
                image_current, title=f"{page.title} — image {image_index:02d}", eyebrow=f"Page {page.id} / individual image",
                body=image_body, entity_id=f"page-{page.id}-image-{image_index:02d}", entity_kind="image",
                nav={
                    "up": ("Page view", page_dest(page.id)),
                    "down": ("Image information", image_dest(page.id, image_index, True)),
                    "left": (f"Image {previous_image:02d}", image_dest(page.id, previous_image)),
                    "right": (f"Image {next_image:02d}", image_dest(page.id, next_image)),
                    "in": ("Image detail", image_current),
                    "out": ("Page view", page_dest(page.id)),
                    "home": ("Viewer home", viewer_home),
                },
            )
            image_info_dir = image_dest(page.id, image_index, True).parent
            image_info_body = f'''
            <section class="info-layout"><div class="info-lede"><p>Image record</p><p>This address already resolves to a placeholder carrying the panel's own script text, and is ready for the final media, credits, provenance, and generation metadata that will replace it.</p></div>
            <dl class="metadata"><div><dt>Identifier</dt><dd>{html.escape(page.id)}-{image_index:02d}</dd></div><div><dt>Parent page</dt><dd>{html.escape(page.id)} · {html.escape(page.title)}</dd></div><div><dt>Position</dt><dd>{image_index} of {page.panel_count}</dd></div><div><dt>Artwork</dt><dd><span class="status-dot"></span> Placeholder</dd></div><div class="metadata__wide"><dt>Placeholder image</dt><dd><a href="{html.escape(placeholder_url(image_info_dir, book.panels[(page.id, image_index)]))}">assets/placeholders/{html.escape(book.panels[(page.id, image_index)].path)}</a> · {book.panels[(page.id, image_index)].width}×{book.panels[(page.id, image_index)].height}</dd></div><div class="metadata__wide"><dt>Final asset</dt><dd>assets/art/panels/{html.escape(page.id)}-{image_index:02d}.*</dd></div><div class="metadata__wide"><dt>Cross reference</dt><dd><a href="{html.escape(crossref_link(image_info_dir, "pages", page.id))}">Panel {image_index:02d} provenance on the page {html.escape(page.id)} record</a></dd></div></dl></section>
            <a class="primary-action" href="{html.escape(route_url(image_info_dir, image_current))}">Return to image <span>↑</span></a>
            '''
            write_viewer_page(
                image_dest(page.id, image_index, True), title=f"About image {page.id}-{image_index:02d}", eyebrow=f"Page {page.id} / image information",
                body=image_info_body, entity_id=f"page-{page.id}-image-{image_index:02d}-info", entity_kind="image-info",
                nav={
                    "up": ("Image view", image_current),
                    "down": ("Page information", page_dest(page.id, True)),
                    "left": (f"About image {previous_image:02d}", image_dest(page.id, previous_image, True)),
                    "right": (f"About image {next_image:02d}", image_dest(page.id, next_image, True)),
                    "in": ("Image view", image_current),
                    "out": ("Page information", page_dest(page.id, True)),
                    "home": ("Viewer home", viewer_home),
                },
            )

    viewer_source = ROOT / "site" / "viewer"
    shutil.copy2(viewer_source / "viewer.css", OUT / "viewer" / "viewer.css")
    shutil.copy2(viewer_source / "viewer.js", OUT / "viewer" / "viewer.js")


# ---------------------------------------------------------------- cross reference


def crossref_destination(*parts: str) -> Path:
    return Path("crossref", *parts, "index.html")


def crossref_link(from_directory: Path, *parts: str) -> str:
    return route_url(from_directory, crossref_destination(*parts))


def chips(from_directory: Path, section: str, values: list[str], labels: dict[str, str] | None = None) -> str:
    if not values:
        return '<span class="xref-empty">none</span>'
    labels = labels or {}
    return '<span class="xref-chips">' + "".join(
        f'<a class="xref-chip" href="{html.escape(crossref_link(from_directory, section, crossref.slug(value)))}">'
        f'{html.escape(labels.get(value, value))}</a>'
        for value in values
    ) + "</span>"


def crossref_navigation(from_directory: Path) -> str:
    items = [
        ("Cross-reference overview", crossref_link(from_directory)),
        ("Pages", crossref_link(from_directory, "pages")),
        ("Sources", crossref_link(from_directory, "sources")),
        ("Provenance statuses", crossref_link(from_directory, "provenance")),
        ("Sequences", crossref_link(from_directory, "sequences")),
        ("Viewer validation build", route_url(from_directory, viewer_destination())),
        ("Project site", route_url(from_directory, Path("index.html"))),
    ]
    return "<ul>" + "".join(
        f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>' for label, href in items
    ) + "</ul>"


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(item)}</th>" for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def page_link(from_directory: Path, page: crossref.Page) -> str:
    return (
        f'<a href="{html.escape(crossref_link(from_directory, "pages", page.id))}">'
        f'{html.escape(page.id)} · {html.escape(page.title)}</a>'
    )


def write_crossref_page(destination: Path, title: str, body: str) -> None:
    directory = destination.parent
    full_destination = OUT / destination
    full_destination.parent.mkdir(parents=True, exist_ok=True)
    full_destination.write_text(
        page_document(
            title,
            body,
            crossref_navigation(directory),
            relative_url(directory, Path("css/site.css")),
        ),
        encoding="utf-8",
    )


def build_crossref(model: crossref.CrossReference, *, internal: bool) -> int:
    """Write the page/source/provenance cross-reference section of the site."""
    chapter_titles = {chapter.id: chapter.title for chapter in model.chapters}
    status_labels = {status: status for status in crossref.PROVENANCE_STATUSES}
    used_statuses = model.used_statuses()
    used_sources = model.used_sources()
    scope_note = (
        '<p class="xref-note">Internal build: the scene ledger’s narrative summaries and drafting '
        'rules are included below. The public build carries only the relational index.</p>'
        if internal else
        '<p class="xref-note">Public build: this index publishes which sources and provenance statuses '
        'each page rests on. The scene ledger’s narrative summaries and drafting rules stay in the '
        'unpublished research record.</p>'
    )

    def page_table(from_directory: Path, pages: list[crossref.Page]) -> str:
        rows = [
            [
                page_link(from_directory, page),
                html.escape(chapter_titles.get(page.chapter, page.chapter)),
                f'<a href="{html.escape(crossref_link(from_directory, "sequences", crossref.slug(crossref.sequence_key(page.sequence))))}">'
                f'{html.escape(page.sequence)}</a>',
                chips(from_directory, "provenance", list(page.statuses), status_labels),
                chips(from_directory, "sources", list(page.sources)),
            ]
            for page in pages
        ]
        return table(["Page", "Chapter", "Sequence", "Provenance", "Sources"], rows)

    # Overview -----------------------------------------------------------------
    home = crossref_destination()
    home_dir = home.parent
    cards = "".join(
        f'<a class="card" href="{html.escape(crossref_link(home_dir, section))}">'
        f"<h3>{html.escape(title)}</h3><p>{html.escape(blurb)}</p></a>"
        for section, title, blurb in (
            ("pages", "By page", f"{len(model.pages)} manifest pages, panel by panel."),
            ("sources", "By source", f"{len(used_sources)} cited citation keys and their originals."),
            ("provenance", "By provenance", f"{len(used_statuses)} evidentiary statuses in use."),
            ("sequences", "By sequence", f"{len(model.sequences)} scene-ledger sequences."),
        )
    )
    status_rows = [
        [
            f'<a href="{html.escape(crossref_link(home_dir, "provenance", status))}">{html.escape(status)}</a>',
            html.escape(crossref.STATUS_NOTES.get(status, "")),
            str(len(model.pages_for_status(status))),
            str(len(model.sources_for_status(status))),
        ]
        for status in crossref.PROVENANCE_STATUSES
    ]
    source_rows = []
    for key in sorted(used_sources, key=lambda item: (-len(model.pages_for_source(item)), item)):
        source = model.sources[key]
        label = html.escape(source.label)
        source_rows.append([
            f'<a href="{html.escape(crossref_link(home_dir, "sources", crossref.slug(key)))}"><code>{html.escape(key)}</code></a>',
            f'<a href="{html.escape(source.url)}">{label}</a>' if source.url else label,
            str(len(model.pages_for_source(key))),
            chips(home_dir, "provenance", model.statuses_for_source(key), status_labels),
        ])
    findings_block = ""
    if internal and model.findings:
        findings_block = (
            "<h2>Build findings</h2>"
            "<p>Reported by <code>python3 scripts/crossref.py check</code>. Warnings mark pages whose panel "
            "provenance lines cite a status or source their front matter does not declare.</p>"
            + table(
                ["Severity", "Subject", "Finding"],
                [
                    [html.escape(item.severity), html.escape(item.subject), html.escape(item.message)]
                    for item in sorted(model.findings, key=lambda item: crossref.SEVERITIES.index(item.severity))
                ],
            )
        )
    write_crossref_page(
        home,
        "Cross reference",
        f'''<p>Every page script declares its evidentiary footing twice: once in front matter, as
        status-and-source pairs, and again on each panel. This section joins those declarations to the
        citation keys in the research record and to the scene ledger, so a page can be reached from the
        source it rests on, and a source from every page that uses it.</p>
        {scope_note}
        <div class="cards">{cards}</div>
        <h2>Provenance statuses</h2>
        {table(["Status", "What it means", "Pages", "Sources"], status_rows)}
        <h2>Cited sources</h2>
        {table(["Key", "Source", "Pages", "Statuses"], source_rows)}
        {findings_block}''',
    )

    # Pages --------------------------------------------------------------------
    pages_index = crossref_destination("pages")
    pages_dir = pages_index.parent
    index_rows = [
        [
            page_link(pages_dir, page),
            html.escape(chapter_titles.get(page.chapter, page.chapter)),
            f'<a href="{html.escape(crossref_link(pages_dir, "sequences", crossref.slug(crossref.sequence_key(page.sequence))))}">'
            f'{html.escape(page.sequence)}</a>',
            str(len(page.panels)),
            chips(pages_dir, "provenance", list(page.statuses), status_labels),
            chips(pages_dir, "sources", list(page.sources)),
        ]
        for page in model.pages
    ]
    write_crossref_page(
        pages_index,
        "Pages by source and provenance",
        f'''<p>All {len(model.pages)} manifest pages with the citation keys and provenance statuses they
        declare. Panel-level detail is on each page record.</p>
        {table(["Page", "Chapter", "Sequence", "Panels", "Provenance", "Sources"], index_rows)}''',
    )

    for page in model.pages:
        destination = crossref_destination("pages", page.id)
        directory = destination.parent
        sequence = model.sequences.get(crossref.sequence_key(page.sequence))
        declared_rows = [
            [html.escape(status), chips(directory, "sources", list(keys))]
            for status, keys in page.declared
        ]
        panel_rows = [
            [
                str(panel.number),
                chips(directory, "provenance", list(panel.statuses), status_labels),
                chips(directory, "sources", list(panel.sources)),
                inline(panel.note),
            ]
            for panel in page.panels
        ]
        script_href = relative_url(directory, slug_for(ROOT / "content" / "pages" / f"{page.id}.md"))
        outbound = [
            (f"Read the page {page.id} script", script_href),
            (f"Open page {page.id} in the viewer", route_url(directory, viewer_destination("pages", page.id))),
            (f"Page {page.id} viewer information", route_url(directory, viewer_destination("pages", page.id, "info"))),
        ]
        if sequence:
            outbound.append((
                f"{sequence.label} ledger record",
                crossref_link(directory, "sequences", crossref.slug(sequence.key)),
            ))
        links = '<ul class="xref-links">' + "".join(
            f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>' for label, href in outbound
        ) + "</ul>"
        extras = ""
        if page.locations or page.continuity_checks:
            extras = "<h2>Page metadata</h2>" + table(
                ["Field", "Values"],
                [
                    row for row in (
                        ["Locations", ", ".join(html.escape(item) for item in page.locations)] if page.locations else [],
                        ["Continuity checks", ", ".join(f"<code>{html.escape(item)}</code>" for item in page.continuity_checks)] if page.continuity_checks else [],
                    ) if row
                ],
            )
        write_crossref_page(
            destination,
            f"Page {page.id} — {page.title}",
            f'''<p><strong>{html.escape(chapter_titles.get(page.chapter, page.chapter))}</strong> ·
            sequence {html.escape(page.sequence)} · draft status {html.escape(page.status)} ·
            {len(page.panels)} panels.</p>
            <h2>Declared provenance</h2>
            {table(["Status", "Sources"], declared_rows) if declared_rows else "<p>This page has no front-matter provenance declaration.</p>"}
            <h2>Panel provenance</h2>
            {table(["Panel", "Statuses", "Sources", "Boundary note"], panel_rows) if panel_rows else "<p>No panel provenance lines were found in this script.</p>"}
            {extras}
            <h2>Elsewhere</h2>
            {links}''',
        )

    # Sources ------------------------------------------------------------------
    sources_index = crossref_destination("sources")
    sources_dir = sources_index.parent
    rows = []
    for key, source in model.sources.items():
        pages = model.pages_for_source(key)
        label = html.escape(source.label)
        rows.append([
            f'<a href="{html.escape(crossref_link(sources_dir, "sources", crossref.slug(key)))}"><code>{html.escape(key)}</code></a>',
            f'<a href="{html.escape(source.url)}">{label}</a>' if source.url else label,
            str(len(pages)),
            chips(sources_dir, "provenance", model.statuses_for_source(key), status_labels),
        ])
    write_crossref_page(
        sources_index,
        "Sources by page",
        f'''<p>Citation keys registered in the research record or used by a page script. Links point at the
        original publication; this project links rather than republishing report pages or extended
        fragments.</p>
        {table(["Key", "Source", "Pages", "Statuses"], rows)}''',
    )

    for key, source in model.sources.items():
        destination = crossref_destination("sources", crossref.slug(key))
        directory = destination.parent
        pages = model.pages_for_source(key)
        original = (
            f'<p><a class="viewer-callout" href="{html.escape(source.url)}">Open the original →</a></p>'
            if source.url else
            '<p class="xref-note">This key stands for project-authored material and has no external original.</p>'
        )
        ledger = f"<p>{inline(source.ledger_note)}</p>" if source.ledger_note else ""
        packet_block = ""
        if internal and source.packet_notes:
            packet_block = (
                "<h2>Chapter source packets</h2>"
                + table(
                    ["Chapter", "Registered use"],
                    [
                        [html.escape(chapter_titles.get(chapter, chapter)), inline(note)]
                        for chapter, note in source.packet_notes
                    ],
                )
            )
        unregistered = (
            '<p class="xref-note">No citation-key table or chapter source packet registers this key.</p>'
            if not source.registered else ""
        )
        heading = ""
        if source.title:
            named = html.escape(source.title)
            if source.url:
                named = f'<a href="{html.escape(source.url)}">{named}</a>'
            heading = f'<p class="lede">{named}</p>'

        write_crossref_page(
            destination,
            key,
            f'''{heading}{original}{ledger}{unregistered}
            <p>Cited on {len(pages)} of {len(model.pages)} pages, at these provenance statuses:
            {chips(directory, "provenance", model.statuses_for_source(key), status_labels)}</p>
            {packet_block}
            <h2>Pages resting on this source</h2>
            {page_table(directory, pages) if pages else "<p>No page cites this key.</p>"}''',
        )

    # Provenance statuses ------------------------------------------------------
    provenance_index = crossref_destination("provenance")
    provenance_dir = provenance_index.parent
    write_crossref_page(
        provenance_index,
        "Provenance statuses",
        f'''<p>The seven evidentiary statuses a panel may carry. A page script may narrow the claim its
        sources support; it may not silently upgrade it.</p>
        {table(
            ["Status", "What it means", "Pages", "Sources"],
            [
                [
                    f'<a href="{html.escape(crossref_link(provenance_dir, "provenance", status))}">{html.escape(status)}</a>',
                    html.escape(crossref.STATUS_NOTES.get(status, "")),
                    str(len(model.pages_for_status(status))),
                    chips(provenance_dir, "sources", model.sources_for_status(status)),
                ]
                for status in crossref.PROVENANCE_STATUSES
            ],
        )}''',
    )

    for status in crossref.PROVENANCE_STATUSES:
        destination = crossref_destination("provenance", status)
        directory = destination.parent
        pages = model.pages_for_status(status)
        panels = sum(
            1 for page in model.pages for panel in page.panels if status in panel.statuses
        )
        write_crossref_page(
            destination,
            f"Provenance: {status}",
            f'''<p>{html.escape(crossref.STATUS_NOTES.get(status, ""))}</p>
            <p>Carried by {len(pages)} pages and {panels} panels, resting on these sources:
            {chips(directory, "sources", model.sources_for_status(status))}</p>
            <h2>Pages</h2>
            {page_table(directory, pages) if pages else "<p>No page carries this status.</p>"}''',
        )

    # Sequences ----------------------------------------------------------------
    sequences_index = crossref_destination("sequences")
    sequences_dir = sequences_index.parent
    headers = ["Sequence", "Ledger pages", "Assigned", "Provenance", "Sources"]
    rows = []
    for key, sequence in model.sequences.items():
        row = [
            f'<a href="{html.escape(crossref_link(sequences_dir, "sequences", crossref.slug(key)))}">{html.escape(sequence.label)}</a>',
            f"{sequence.first_page:03d}–{sequence.last_page:03d}",
            str(len(model.pages_for_sequence(key))),
            chips(sequences_dir, "provenance", list(sequence.statuses), status_labels),
            chips(sequences_dir, "sources", list(sequence.sources)),
        ]
        if internal:
            row.append(inline(sequence.event))
        rows.append(row)
    write_crossref_page(
        sequences_index,
        "Sequences",
        f'''<p>The scene ledger groups the 112 pages into {len(model.sequences)} sequences and fixes the
        evidentiary treatment of each. These records connect a sequence to the pages assigned to it.</p>
        {scope_note}
        {table(headers + (["Narrative event"] if internal else []), rows)}''',
    )

    for key, sequence in model.sequences.items():
        destination = crossref_destination("sequences", crossref.slug(key))
        directory = destination.parent
        pages = model.pages_for_sequence(key)
        ledger_block = ""
        if internal:
            ledger_block = (
                f"<h2>Ledger record</h2><p>{inline(sequence.event)}</p>"
                f"<blockquote><p>{inline(sequence.rule)}</p></blockquote>"
            )
        write_crossref_page(
            destination,
            sequence.label,
            f'''<p>Ledger pages {sequence.first_page:03d}–{sequence.last_page:03d} ·
            {len(pages)} pages assigned in the manifest.</p>
            <p>Ledger provenance: {chips(directory, "provenance", list(sequence.statuses), status_labels)}<br>
            Ledger sources: {chips(directory, "sources", list(sequence.sources))}</p>
            {ledger_block}
            <h2>Pages</h2>
            {page_table(directory, pages) if pages else "<p>No manifest page is assigned to this sequence.</p>"}''',
        )

    return len(list((OUT / "crossref").rglob("index.html")))


def page_document(title: str, body: str, nav: str, css_href: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} — zz-no-consumer</title>
  <link rel="stylesheet" href="{html.escape(css_href)}">
</head>
<body>
  <header><div class="shell"><div class="eyebrow">zz-no-consumer</div><h1>{html.escape(title)}</h1><p class="lede">A graphic novel about emergent AI agent coordination.</p></div></header>
  <main class="shell"><article>{body}</article><aside><h2>Explore</h2>{nav}</aside></main>
  <footer><div class="shell">Generated from canonical Markdown on the main branch.</div></footer>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--internal",
        action="store_true",
        help="build all research, production, prompt, and design pages into the ignored 256t/site directory",
    )
    args = parser.parse_args()

    global OUT
    OUT = ROOT / "256t" / "site" if args.internal else ROOT / "docs"
    OUT.mkdir(parents=True, exist_ok=True)
    for child in OUT.iterdir():
        if child.name != ".gitkeep":
            shutil.rmtree(child) if child.is_dir() else child.unlink()

    markdown_files = markdown_sources(args.internal)
    pages: list[tuple[str, Path]] = [(title_for(path), slug_for(path)) for path in markdown_files]
    def navigation(from_directory: Path) -> str:
        links = "".join(
            f'<li><a href="{html.escape(relative_url(from_directory, Path(slug)))}">{html.escape(title)}</a></li>'
            for title, slug in pages
        )
        return f"<ul>{links}</ul>"

    for source in markdown_files:
        destination = OUT / slug_for(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            page_document(
                title_for(source),
                markdown_to_html(source.read_text(encoding="utf-8")),
                navigation(destination.parent.relative_to(OUT)),
                relative_url(destination.parent.relative_to(OUT), Path("css/site.css")),
            ),
            encoding="utf-8",
        )

    story = textimage.book_scripts()
    placeholder_link = (
        '<p><a class="viewer-callout" href="viewer/pages/001/">'
        f'Read all {len(story)} pages and {sum(len(item.panels) for item in story)} panels '
        'as placeholder images →</a></p>'
    )

    index_cards = "".join(
        f'<a class="card" href="{html.escape(str(slug))}"><h3>{html.escape(title)}</h3><p>{html.escape(str(source.relative_to(ROOT)))}</p></a>'
        for (title, slug), source in zip(pages, markdown_files)
    )
    if args.internal:
        index_body = (
            '<p>Private local review build: canonical story material, visual direction, research, and production notes.</p>'
            '<p><a class="viewer-callout" href="viewer/">Open the graphic novel viewer validation build →</a></p>'
            f'{placeholder_link}'
            '<p><a class="viewer-callout" href="crossref/">Open the page, source, and provenance cross reference →</a></p>'
            '<p><a class="viewer-callout" href="production/thumbnails/">Open the provisional 57-spread thumbnail wall →</a></p>'
            f'<h2>Browse the internal project</h2><div class="cards">{index_cards}</div>'
        )
    else:
        index_body = (
            '<p>Story-first public build. Research snapshots, source packets, prompts, and production notes remain local.</p>'
            '<p><a class="viewer-callout" href="viewer/">Open the graphic novel viewer validation build →</a></p>'
            f'{placeholder_link}'
            '<p><a class="viewer-callout" href="crossref/">Open the page, source, and provenance cross reference →</a></p>'
            f'<h2>Browse the story</h2><div class="cards">{index_cards}</div>'
        )
    (OUT / "index.html").write_text(
        page_document("The Project", index_body, navigation(Path(".")), "css/site.css"),
        encoding="utf-8",
    )

    for folder in ("assets",):
        source = ROOT / folder
        destination = OUT / folder
        if source.exists():
            shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".gitkeep"))
    css = ROOT / "site" / "css" / "site.css"
    if css.exists():
        (OUT / "css").mkdir(exist_ok=True)
        shutil.copy2(css, OUT / "css" / "site.css")

    model = crossref.build()
    crossref_routes = build_crossref(model, internal=args.internal)
    build_viewer()

    print(
        f"Built {len(markdown_files)} Markdown pages, {crossref_routes} cross-reference routes, "
        f"and the viewer validation section into {OUT.relative_to(ROOT)}/"
    )
    warnings = [item for item in model.findings if item.severity != "note"]
    if warnings:
        print(f"Cross-reference findings: {len(warnings)}; run scripts/crossref.py check for detail.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
