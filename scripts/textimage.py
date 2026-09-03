#!/usr/bin/env python3
"""Flow a block of text into an image of exactly the requested dimensions.

The generator adds no image dependencies. Glyph advances come from the
Helvetica metrics that Arial, Liberation Sans, and Nimbus Sans match, so line
breaking and the automatic type-size search run in pure Python and the rendered
SVG breaks its lines exactly where this module measured them.

    python3 scripts/textimage.py render --width 1200 --height 800 --out card.svg --text "..."
    python3 scripts/textimage.py book

`render` is the general tool: any text, any dimensions. `book` writes one
placeholder for every page and every panel image slot in `content/pages/`,
which is what `scripts/build-site.py` embeds in the viewer.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "content" / "pages"
DEFAULT_BOOK_DIR = ROOT / "docs" / "assets" / "placeholders"

PAGE_SIZE = (700, 1000)
PANEL_SIZE = (1200, 800)

FONT_STACK = "Helvetica, Arial, 'Liberation Sans', 'Nimbus Sans', sans-serif"
FALLBACK_ADVANCE = 556
BOLD_RATIO = 1.08
LINE_RATIO = 1.36
GAP_RATIO = 0.62
SIZE_STEP = 0.25


def _advance_table() -> dict[str, int]:
    """Helvetica advance widths, in thousandths of the em."""
    widths = {
        " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
        "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
        ".": 278, "/": 278, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584,
        "?": 556, "@": 1015, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
        "`": 333, "{": 334, "|": 260, "}": 334, "~": 584,
    }
    widths.update({digit: 556 for digit in "0123456789"})
    widths.update(zip(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        (667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
         722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611),
    ))
    widths.update(zip(
        "abcdefghijklmnopqrstuvwxyz",
        (556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
         556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500),
    ))
    widths.update({
        " ": 278, "°": 400, "×": 584, "‘": 222, "’": 222,
        "“": 333, "”": 333, "–": 556, "—": 1000, "…": 1000,
        "•": 350, "→": 1000, "←": 1000, "↑": 1000, "↓": 1000,
    })
    return widths


ADVANCE = _advance_table()


def advance(text: str, size: float, *, bold: bool = False) -> float:
    """Width of `text` set at `size`, in the same units as the image box."""
    total = sum(ADVANCE.get(character, FALLBACK_ADVANCE) for character in text)
    return total * size / 1000 * (BOLD_RATIO if bold else 1.0)


@dataclass(frozen=True)
class Palette:
    paper: str = "#d4d0c5"
    ink: str = "#12140f"
    muted: str = "#6b6d63"
    accent: str = "#a33f22"
    rule: str = "#a4a094"


PAPER = Palette()


@dataclass(frozen=True)
class Flowed:
    """A block of text laid out to fit a box. Empty lines are paragraph gaps."""

    size: float
    leading: float
    lines: tuple[str, ...]
    height: float
    truncated: bool


def _paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    return [re.sub(r"\s+", " ", block).strip() for block in blocks if block.strip()]


def _wrap(paragraph: str, size: float, width: float, bold: bool) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in paragraph.split(" "):
        candidate = f"{current} {word}" if current else word
        if current and advance(candidate, size, bold=bold) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
        while len(current) > 1 and advance(current, size, bold=bold) > width:
            cut = len(current)
            while cut > 1 and advance(current[:cut], size, bold=bold) > width:
                cut -= 1
            lines.append(current[:cut])
            current = current[cut:]
    if current:
        lines.append(current)
    return lines


def _block(paragraphs: list[str], size: float, width: float, bold: bool) -> tuple[list[str], float, float]:
    lines: list[str] = []
    for index, paragraph in enumerate(paragraphs):
        if index:
            lines.append("")
        lines.extend(_wrap(paragraph, size, width, bold))
    leading = size * LINE_RATIO
    height = sum(leading if line else leading * GAP_RATIO for line in lines)
    return lines, leading, height


def ellipsize(text: str, size: float, width: float, *, bold: bool = False, force: bool = False) -> str:
    """Shorten `text` to `width`. `force` marks it even when it already fits,
    which is how a block cut off vertically shows that it continues."""
    if not force and advance(text, size, bold=bold) <= width:
        return text
    trimmed = text.rstrip()
    while trimmed and advance(f"{trimmed}…", size, bold=bold) > width:
        trimmed = trimmed[:-1]
    return f"{trimmed.rstrip()}…"


def flow(
    text: str,
    width: float,
    height: float,
    *,
    bold: bool = False,
    min_size: float = 6.0,
    max_size: float = 72.0,
) -> Flowed:
    """Wrap `text` at the largest type size that fits `width` x `height`.

    Below `min_size` the text is cut to the box and the last kept line ends in
    an ellipsis, so the returned image never spills past its dimensions.
    """
    paragraphs = _paragraphs(text) or [""]
    max_size = max(max_size, min_size)
    steps = max(0, int((max_size - min_size) / SIZE_STEP))
    low, high, best = 0, steps, None
    while low <= high:
        middle = (low + high) // 2
        size = min_size + middle * SIZE_STEP
        lines, leading, block_height = _block(paragraphs, size, width, bold)
        if block_height <= height:
            best = (size, lines, leading, block_height)
            low = middle + 1
        else:
            high = middle - 1
    if best is not None:
        size, lines, leading, block_height = best
        return Flowed(size, leading, tuple(lines), block_height, False)

    lines, leading, _ = _block(paragraphs, min_size, width, bold)
    kept: list[str] = []
    used = 0.0
    truncated = False
    for line in lines:
        step = leading if line else leading * GAP_RATIO
        if used + step > height:
            truncated = True
            break
        kept.append(line)
        used += step
    while kept and not kept[-1]:
        kept.pop()
        used -= leading * GAP_RATIO
    if truncated and kept:
        kept[-1] = ellipsize(kept[-1], min_size, width, bold=bold, force=True)
    return Flowed(min_size, leading, tuple(kept), used, truncated)


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _round(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def text_image(
    text: str,
    width: int,
    height: int,
    *,
    label: str = "",
    footer: str = "",
    title: str = "",
    palette: Palette = PAPER,
    align: str = "left",
    margin: float | None = None,
    frame: bool = True,
    min_size: float | None = None,
    max_size: float | None = None,
) -> str:
    """Return an SVG exactly `width` x `height` with `text` flowed to fit it.

    `label` and `footer` are optional single-line markers on the top and bottom
    edges; both are shortened rather than allowed to widen the image.
    """
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")
    if align not in {"left", "center"}:
        raise ValueError("align must be 'left' or 'center'")

    short = min(width, height)
    edge = float(margin) if margin is not None else round(short * 0.07)
    chrome = min(max(short * 0.028, 8.0), 22.0)
    top_band = chrome * 2.4 if label else 0.0
    bottom_band = chrome * 2.4 if footer else 0.0

    box_x = edge
    box_y = edge + top_band
    box_width = width - 2 * edge
    box_height = height - 2 * edge - top_band - bottom_band
    if box_width <= 0 or box_height <= 0:
        raise ValueError("Margins leave no room for text at these dimensions")

    smallest = min_size if min_size is not None else max(6.0, short / 60)
    largest = max_size if max_size is not None else max(smallest, short / 16)
    laid_out = flow(text, box_width, box_height, min_size=smallest, max_size=largest)

    anchor = "start" if align == "left" else "middle"
    text_x = box_x if align == "left" else box_x + box_width / 2
    # `height` counts full leading under the last line; centre on the ink instead.
    slack = (box_height - laid_out.height + laid_out.leading - laid_out.size) / 2
    baseline = box_y + slack + laid_out.size * 0.78

    heading = title or label or (laid_out.lines[0] if laid_out.lines else "Placeholder image")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
        f"<title id=\"title\">{_esc(heading)}</title>",
        f'<rect width="{width}" height="{height}" fill="{palette.paper}"/>',
    ]
    if frame:
        outer = edge * 0.5
        inner = edge * 0.9
        parts.append(
            f'<rect x="{_round(outer)}" y="{_round(outer)}" width="{_round(width - 2 * outer)}" '
            f'height="{_round(height - 2 * outer)}" fill="none" stroke="{palette.rule}" stroke-width="1"/>'
        )
        parts.append(
            f'<rect x="{_round(inner)}" y="{_round(inner)}" width="{_round(width - 2 * inner)}" '
            f'height="{_round(height - 2 * inner)}" fill="none" stroke="{palette.rule}" '
            f'stroke-width="1" stroke-dasharray="7 7" opacity="0.55"/>'
        )

    parts.append(f'<g font-family="{FONT_STACK}">')
    if label:
        fitted = ellipsize(label, chrome, box_width, bold=True)
        parts.append(
            f'<text x="{_round(box_x)}" y="{_round(edge + chrome)}" font-size="{_round(chrome)}" '
            f'font-weight="700" letter-spacing="{_round(chrome * 0.06)}" fill="{palette.accent}">'
            f"{_esc(fitted)}</text>"
        )
    parts.append(
        f'<text font-size="{_round(laid_out.size)}" fill="{palette.ink}" text-anchor="{anchor}" '
        f'xml:space="preserve">'
    )
    offset = 0.0
    for line in laid_out.lines:
        if not line:
            offset += laid_out.leading * GAP_RATIO
            continue
        parts.append(
            f'<tspan x="{_round(text_x)}" y="{_round(baseline + offset)}">{_esc(line)}</tspan>'
        )
        offset += laid_out.leading
    parts.append("</text>")
    if footer:
        fitted = ellipsize(footer, chrome * 0.86, box_width, bold=False)
        parts.append(
            f'<text x="{_round(box_x)}" y="{_round(height - edge)}" font-size="{_round(chrome * 0.86)}" '
            f'letter-spacing="{_round(chrome * 0.05)}" fill="{palette.muted}">{_esc(fitted)}</text>'
        )
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ------------------------------------------------------------------- the book


FIELD = re.compile(r"^\*\*(?P<name>[^*]+?):?\*\*\s*(?P<rest>.*)$")
PANEL_HEADING = re.compile(r"^## (Panels? [^\n]*?)\s*$", re.MULTILINE)
INDIVIDUAL_PANEL = re.compile(r"^Panel \d+$")
LETTERING = ("Caption", "Dialogue", "Left dialogue", "Right dialogue", "Screen / system text", "Qualification")
DESCRIPTION = ("Frame", "Action")


@dataclass(frozen=True)
class PanelScript:
    index: int
    heading: str
    text: str


@dataclass(frozen=True)
class PageScript:
    id: str
    title: str
    chapter: str
    status: str
    purpose: str
    panels: tuple[PanelScript, ...]


@dataclass(frozen=True)
class Placeholder:
    path: str
    width: int
    height: int
    alt: str


@dataclass(frozen=True)
class BookImages:
    directory: Path
    pages: dict[str, Placeholder]
    panels: dict[tuple[str, int], Placeholder]

    @property
    def count(self) -> int:
        return len(self.pages) + len(self.panels)


def _front_matter(source: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", source, re.MULTILINE)
    return match.group(1).strip('"') if match else ""


def _plain(text: str) -> str:
    """Drop the Markdown markers that carry no meaning once the text is art."""
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


def _fields(section: str) -> list[tuple[str, str]]:
    collected: list[tuple[str, str]] = []
    name: str | None = None
    buffer: list[str] = []
    for raw in section.splitlines():
        line = raw.strip()
        match = FIELD.match(line)
        if match:
            if name:
                collected.append((name, " ".join(buffer).strip()))
            name = match.group("name").strip()
            buffer = [match.group("rest").strip()]
            continue
        if name is None or not line:
            continue
        if line == ">":
            continue
        if line.startswith("> "):
            buffer.append(line[2:].strip())
        elif len(line) > 1 and line.startswith("`") and line.endswith("`"):
            buffer.append(line.strip("`").strip())
        else:
            buffer.append(line)
    if name:
        collected.append((name, " ".join(buffer).strip()))
    return [(name, _plain(value)) for name, value in collected]


def _panel_text(sections: list[tuple[str, str]], *, label_sections: bool) -> str:
    paragraphs: list[str] = []
    for heading, body in sections:
        if label_sections:
            paragraphs.append(heading.upper())
        for name, value in _fields(body):
            if not value:
                continue
            base = name.split("—")[0].strip()
            if base in DESCRIPTION:
                paragraphs.append(f"{name.upper()} — {value}")
            elif base in LETTERING:
                paragraphs.append(f"{name.upper()} — “{value}”")
    return "\n\n".join(paragraphs)


def page_script(page_id: str) -> PageScript:
    """Read one canonical page script into the parts a placeholder needs."""
    source = (PAGE_DIR / f"{page_id}.md").read_text(encoding="utf-8")
    purpose = re.search(r"^## Page purpose\s*\n+((?:(?!^#)[^\n]*\n?)+)", source, re.MULTILINE)
    headings = PANEL_HEADING.findall(source)
    bodies = PANEL_HEADING.split(source)[2::2]
    sections = list(zip(headings, bodies))
    individual = [item for item in sections if INDIVIDUAL_PANEL.match(item[0])]

    panels: list[PanelScript] = []
    if individual:
        for index, (heading, body) in enumerate(individual, 1):
            panels.append(PanelScript(index, heading, _panel_text([(heading, body)], label_sections=False)))
    elif sections:
        # Pages written as one grouped run of panels hold a single image slot.
        panels.append(PanelScript(1, sections[0][0], _panel_text(sections, label_sections=True)))

    return PageScript(
        id=page_id,
        title=_front_matter(source, "title"),
        chapter=_front_matter(source, "chapter"),
        status=_front_matter(source, "status"),
        purpose=_plain(purpose.group(1)) if purpose else "",
        panels=tuple(panels),
    )


def book_scripts() -> list[PageScript]:
    return [page_script(path.stem) for path in sorted(PAGE_DIR.glob("[0-9][0-9][0-9].md"))]


def _summary(text: str, limit: int = 220) -> str:
    condensed = re.sub(r"\s+", " ", text).strip()
    return condensed if len(condensed) <= limit else f"{condensed[:limit].rstrip()}…"


def build_book(
    directory: Path,
    *,
    page_size: tuple[int, int] = PAGE_SIZE,
    panel_size: tuple[int, int] = PANEL_SIZE,
) -> BookImages:
    """Write a placeholder image for every page and every panel image slot."""
    pages: dict[str, Placeholder] = {}
    panels: dict[tuple[str, int], Placeholder] = {}
    (directory / "pages").mkdir(parents=True, exist_ok=True)
    (directory / "panels").mkdir(parents=True, exist_ok=True)

    for script in book_scripts():
        slots = len(script.panels)
        page_body = script.purpose or f"Page {script.id}. {script.title}."
        page_path = f"pages/{script.id}.svg"
        (directory / page_path).write_text(
            text_image(
                page_body,
                *page_size,
                label=f"PAGE {script.id} · {script.title.upper()}",
                footer=f"{script.chapter.upper()} · {script.status.upper()} · "
                       f"{slots} IMAGE SLOT{'S' if slots != 1 else ''} · PLACEHOLDER",
                title=f"Placeholder for page {script.id}, {script.title}",
            ),
            encoding="utf-8",
        )
        pages[script.id] = Placeholder(
            path=page_path,
            width=page_size[0],
            height=page_size[1],
            alt=f"Placeholder for page {script.id}, {script.title}. {_summary(page_body)}",
        )

        for panel in script.panels:
            panel_body = panel.text or f"{panel.heading} of page {script.id}."
            panel_path = f"panels/{script.id}-{panel.index:02d}.svg"
            (directory / panel_path).write_text(
                text_image(
                    panel_body,
                    *panel_size,
                    label=f"PAGE {script.id} · IMAGE {panel.index:02d} OF {slots:02d}",
                    footer=f"{script.title.upper()} · {panel.heading.upper()} · PLACEHOLDER",
                    title=f"Placeholder for page {script.id}, image {panel.index:02d}",
                ),
                encoding="utf-8",
            )
            panels[(script.id, panel.index)] = Placeholder(
                path=panel_path,
                width=panel_size[0],
                height=panel_size[1],
                alt=f"Placeholder for page {script.id}, image {panel.index:02d}. {_summary(panel_body)}",
            )

    return BookImages(directory=directory, pages=pages, panels=panels)


# -------------------------------------------------------------------- the CLI


def _read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.text_file is not None:
        return Path(args.text_file).read_text(encoding="utf-8")
    if sys.stdin.isatty():
        raise SystemExit("Provide text with --text, --text-file, or on standard input.")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    render = commands.add_parser("render", help="flow one block of text into one image")
    render.add_argument("--width", type=int, required=True)
    render.add_argument("--height", type=int, required=True)
    render.add_argument("--out", type=Path, required=True)
    render.add_argument("--text", help="the text to flow; omit to read --text-file or standard input")
    render.add_argument("--text-file")
    render.add_argument("--label", default="", help="small marker along the top edge")
    render.add_argument("--footer", default="", help="small marker along the bottom edge")
    render.add_argument("--title", default="", help="accessible name for the image")
    render.add_argument("--align", default="left", choices=("left", "center"))
    render.add_argument("--margin", type=float, default=None)
    render.add_argument("--min-size", type=float, default=None)
    render.add_argument("--max-size", type=float, default=None)
    render.add_argument("--no-frame", action="store_true")

    book = commands.add_parser("book", help="write placeholders for every page and panel image slot")
    book.add_argument("--out-dir", type=Path, default=DEFAULT_BOOK_DIR)
    book.add_argument("--page-width", type=int, default=PAGE_SIZE[0])
    book.add_argument("--page-height", type=int, default=PAGE_SIZE[1])
    book.add_argument("--panel-width", type=int, default=PANEL_SIZE[0])
    book.add_argument("--panel-height", type=int, default=PANEL_SIZE[1])

    args = parser.parse_args()

    if args.command == "render":
        text = _read_text(args)
        document = text_image(
            text,
            args.width,
            args.height,
            label=args.label,
            footer=args.footer,
            title=args.title,
            align=args.align,
            margin=args.margin,
            frame=not args.no_frame,
            min_size=args.min_size,
            max_size=args.max_size,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(document, encoding="utf-8")
        measured = re.search(r'<text font-size="([0-9.]+)"', document)
        print(f"Wrote {args.width}x{args.height} image to {args.out} at {measured.group(1)}px type.")
        return 0

    directory = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    images = build_book(
        directory,
        page_size=(args.page_width, args.page_height),
        panel_size=(args.panel_width, args.panel_height),
    )
    print(
        f"Wrote {len(images.pages)} page and {len(images.panels)} panel placeholders "
        f"({images.count} images) into {directory}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
