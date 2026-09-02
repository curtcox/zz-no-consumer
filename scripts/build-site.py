#!/usr/bin/env python3
"""Build a dependency-free HTML reading site from the repository's Markdown."""

from __future__ import annotations

import html
import posixpath
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"


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

    print(f"Built {len(markdown_files)} Markdown pages into {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
