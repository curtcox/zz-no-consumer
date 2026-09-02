#!/usr/bin/env python3
"""Build a dependency-free HTML reading site from the repository's Markdown."""

from __future__ import annotations

import html
import posixpath
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"


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
            "in": "+", "out": "−", "home": "⌂",
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

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="description" content="Validation viewer for {html.escape(title)} in zz-no-consumer.">
  <title>{html.escape(title)} — Viewer — zz-no-consumer</title>
  <link rel="stylesheet" href="{html.escape(css_href)}">
</head>
<body data-entity-id="{html.escape(entity_id)}" data-entity-kind="{html.escape(entity_kind)}"
      data-nav-up="{html.escape(nav_links['up'])}" data-nav-down="{html.escape(nav_links['down'])}"
      data-nav-left="{html.escape(nav_links['left'])}" data-nav-right="{html.escape(nav_links['right'])}"
      data-nav-in="{html.escape(nav_links['in'])}" data-nav-out="{html.escape(nav_links['out'])}"
      data-nav-home="{html.escape(nav_links['home'])}">
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
      <a class="utility" href="{html.escape(project_home)}">Project site</a>
    </div>
  </header>
  <main id="content">
    <div class="view-heading">
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
    </div>
  </nav>
  <dialog class="shortcut-dialog" data-shortcut-dialog>
    <button class="shortcut-dialog__close" type="button" data-close-dialog aria-label="Close">×</button>
    <p class="eyebrow">Keyboard map</p>
    <h2>Move without losing your place.</h2>
    <dl><div><dt>← → ↑ ↓</dt><dd>Move left, right, up, or down</dd></div>
    <div><dt>Enter</dt><dd>Move in</dd></div><div><dt>Esc</dt><dd>Move out</dd></div>
    <div><dt>H</dt><dd>Viewer home</dd></div><div><dt>?</dt><dd>Show this map</dd></div></dl>
  </dialog>
  <div class="toast" role="status" aria-live="polite" data-toast></div>
  <script src="{html.escape(js_href)}" defer></script>
</body>
</html>
'''


def page_art(page: ViewerPage, *, compact: bool = False) -> str:
    count = min(page.panel_count, 6)
    panels = "".join(
        f'<span class="placeholder-panel placeholder-panel--{index}" aria-hidden="true"></span>'
        for index in range(1, count + 1)
    )
    compact_class = " page-art--compact" if compact else ""
    return (
        f'<div class="page-art{compact_class}" data-panels="{count}">'
        f'<span class="page-art__number">{html.escape(page.id)}</span>{panels}'
        f'<span class="page-art__status">{html.escape(page.status)}</span></div>'
    )


def write_viewer_page(destination: Path, **kwargs: object) -> None:
    full_destination = OUT / destination
    full_destination.parent.mkdir(parents=True, exist_ok=True)
    full_destination.write_text(
        viewer_document(destination=destination, **kwargs),
        encoding="utf-8",
    )


def build_viewer() -> None:
    pages = viewer_pages()
    chapters = viewer_chapters()
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
      <div class="intro-copy"><p class="kicker">A spatial reading prototype</p>
        <p>This isolated build validates durable routes, page and panel hierarchy, and seven-direction navigation before final artwork exists.</p>
        <a class="primary-action" href="{html.escape(viewer_link(Path("viewer"), "pages", pages[0].id))}">Begin on page 001 <span>→</span></a>
      </div>
      <div class="map-card" aria-label="Content map"><span>HOME</span><i></i><span>CHAPTER</span><i></i><span>PAGE</span><i></i><span>IMAGE</span></div>
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
                  {page_art(page, compact=True)}
                  <span class="page-card__copy"><b>{html.escape(page.id)} · {html.escape(page.title)}</b><small>Sequence {html.escape(page.sequence)} · {html.escape(page.status)}</small></span>
                </a>'''
            )
        chapter_body = f'''
        <section class="chapter-intro"><div><p class="kicker">Chapter {html.escape(chapter.id.upper())}</p><p>{len(chapter_pages)} pages · {sum(page.panel_count for page in chapter_pages)} image slots · artwork pending</p></div>
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
        <div><dt>Pages</dt><dd>{len(chapter_pages)}</dd></div><div><dt>Image slots</dt><dd>{sum(page.panel_count for page in chapter_pages)}</dd></div><div><dt>Artwork</dt><dd><span class="status-dot"></span> Not generated</dd></div></dl></section>
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
          <div class="reader-stage"><div class="reader-stage__top"><span>Page {html.escape(page.id)} / 112</span><span class="art-state"><i></i> Placeholder artwork</span></div>
            <a class="page-art-link" href="{html.escape(route_url(current_dir, image_dest(page.id, 1)))}" aria-label="Open first image on page {html.escape(page.id)}">{page_art(page)}</a>
          </div>
          <aside class="reader-notes"><p class="eyebrow">Page record</p><h2>{html.escape(page.title)}</h2><dl><div><dt>Chapter</dt><dd>{html.escape(chapter.title)}</dd></div><div><dt>Sequence</dt><dd>{html.escape(page.sequence)}</dd></div><div><dt>Status</dt><dd>{html.escape(page.status)}</dd></div></dl>
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
        <dl class="metadata"><div><dt>Page</dt><dd>{html.escape(page.id)} of 112</dd></div><div><dt>Title</dt><dd>{html.escape(page.title)}</dd></div><div><dt>Chapter</dt><dd>{html.escape(chapter.title)}</dd></div><div><dt>Sequence</dt><dd>{html.escape(page.sequence)}</dd></div><div><dt>Status</dt><dd>{html.escape(page.status)}</dd></div><div><dt>Image slots</dt><dd>{page.panel_count}</dd></div><div class="metadata__wide"><dt>Source</dt><dd>{html.escape(source_label)}</dd></div></dl></section>
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
            <section class="image-viewer"><div class="image-frame" id="image"><div class="image-placeholder"><span class="image-placeholder__cross"></span><span class="image-placeholder__label">PAGE {html.escape(page.id)} / IMAGE {image_index:02d}</span><b>ARTWORK<br>NOT GENERATED</b><small>Aspect ratio and route are ready for validation.</small></div></div>
            <div class="image-caption"><p><span>{html.escape(chapter.title)}</span> / Page {html.escape(page.id)}</p><h2>Image {image_index:02d} of {page.panel_count:02d}</h2><a class="text-action" href="{html.escape(route_url(image_dir, image_dest(page.id, image_index, True)))}">Image information <span>↓</span></a></div></section>
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
            <section class="info-layout"><div class="info-lede"><p>Image record</p><p>This stable address is ready for final media, alt text, credits, provenance, and generation metadata.</p></div>
            <dl class="metadata"><div><dt>Identifier</dt><dd>{html.escape(page.id)}-{image_index:02d}</dd></div><div><dt>Parent page</dt><dd>{html.escape(page.id)} · {html.escape(page.title)}</dd></div><div><dt>Position</dt><dd>{image_index} of {page.panel_count}</dd></div><div><dt>Artwork</dt><dd><span class="status-dot"></span> Not generated</dd></div><div class="metadata__wide"><dt>Future asset</dt><dd>assets/art/panels/{html.escape(page.id)}-{image_index:02d}.*</dd></div></dl></section>
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
    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        if child.name != ".gitkeep":
            shutil.rmtree(child) if child.is_dir() else child.unlink()

    markdown_files = sorted(
        path for folder in ("content", "prompts", "research", "design")
        for path in (ROOT / folder).rglob("*.md")
    )
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

    index_cards = "".join(
        f'<a class="card" href="{html.escape(str(slug))}"><h3>{html.escape(title)}</h3><p>{html.escape(str(source.relative_to(ROOT)))}</p></a>'
        for (title, slug), source in zip(pages, markdown_files)
    )
    index_body = (
        '<p>Canonical story material, visual direction, research, and production notes.</p>'
        '<p><a class="viewer-callout" href="viewer/">Open the graphic novel viewer validation build →</a></p>'
        f'<h2>Browse the project</h2><div class="cards">{index_cards}</div>'
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

    build_viewer()

    print(f"Built {len(markdown_files)} Markdown pages and the viewer validation section into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
