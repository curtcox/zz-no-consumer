#!/usr/bin/env python3
"""Build a provisional recto/verso thumbnail wall from canonical page scripts.

The generated geometry is a production-review aid, not locked panel layout. It
preserves panel order, highlights lettering load, and exposes every physical
page turn without adding image-processing dependencies.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import panels  # noqa: E402  the panel and lettering model is defined once, there


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "content" / "pages"
DEFAULT_OUTPUT = ROOT / "256t" / "site" / "production" / "thumbnails" / "index.html"
WORD = panels.WORD
DENSE = panels.DENSE_PAGE_WORDS
DEFAULT_BAND = panels.DEFAULT_BAND


@dataclass(frozen=True)
class Page:
    number: int
    title: str
    chapter: str
    sequence: str
    status: str
    panel_count: int
    word_count: int
    purpose: str
    final_beat: str

    @property
    def side(self) -> str:
        return "recto" if self.number % 2 else "verso"

    @property
    def layout(self) -> str:
        if self.panel_count == 9:
            return "grid-nine"
        if self.panel_count == 6:
            return "grid-six"
        if self.panel_count == 4:
            return "grid-four"
        if self.panel_count == 3:
            return "stack-three"
        if self.panel_count == 2:
            return "split-two"
        if self.panel_count == 1:
            return "splash-one"
        patterns = ("wide-top", "wide-bottom", "tall-left", "tall-right")
        return patterns[self.number % len(patterns)]


def front_matter(source: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", source, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing {key}")
    return match.group(1).strip('"')


panel_count = panels.panel_count
visible_text = panels.visible_text


def page_purpose(source: str) -> str:
    match = re.search(r"^## Page purpose\s*\n\s*([^\n]+)", source, re.MULTILINE)
    return match.group(1).strip() if match else ""


def load_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted(PAGE_DIR.glob("[0-9][0-9][0-9].md")):
        number = int(path.stem)
        source = path.read_text(encoding="utf-8")
        lettering = visible_text(source)
        pages.append(
            Page(
                number=number,
                title=front_matter(source, "title"),
                chapter=front_matter(source, "chapter"),
                sequence=front_matter(source, "sequence"),
                status=front_matter(source, "status"),
                panel_count=panel_count(source),
                word_count=sum(len(WORD.findall(line)) for line in lettering),
                purpose=page_purpose(source),
                final_beat=lettering[-1] if lettering else "[silent final beat]",
            )
        )
    return pages


def panel_grid(page: Page) -> str:
    cells = "".join(
        f'<span class="mini-panel"><i>{index}</i></span>'
        for index in range(1, page.panel_count + 1)
    )
    return f'<div class="mini-page {page.layout}" aria-label="{page.panel_count} provisional panels">{cells}</div>'


def page_card(page: Page | None, *, position: str) -> str:
    if page is None:
        return f'<article class="page-card blank {position}"><span>blank / endmatter</span></article>'
    density = " density-warning" if page.word_count > DENSE else ""
    band = set(range(DEFAULT_BAND[0], DEFAULT_BAND[1] + 1)) | {9}
    unusual = " rhythm-note" if page.panel_count not in band else ""
    return f'''<article class="page-card {position}{density}{unusual}">
      <header><b>{page.number:03d}</b><span>{html.escape(page.side)}</span></header>
      {panel_grid(page)}
      <div class="page-copy"><h3>{html.escape(page.title)}</h3>
        <p>{page.panel_count} panels · {page.word_count} lettered words</p>
        <small>Ch. {html.escape(page.chapter)} · Seq. {html.escape(page.sequence)} · {html.escape(page.status)}</small>
      </div>
    </article>'''


def physical_spreads(pages: list[Page]) -> list[tuple[Page | None, Page | None, str]]:
    """Page 1 is a recto, so it stands alone and every later spread is (even, odd)."""
    by_number = {page.number: page for page in pages}
    last = max(by_number)
    spreads: list[tuple[Page | None, Page | None, str]] = [(None, by_number[1], "Opening recto")]
    for even in range(2, last, 2):
        if even + 1 in by_number:
            spreads.append((by_number[even], by_number[even + 1],
                            f"Facing {even:03d} → {even + 1:03d}"))
    if last % 2 == 0:
        spreads.append((by_number[last], None, "Final verso"))
    return spreads


def spread_rows(pages: list[Page]) -> str:
    spreads = physical_spreads(pages)
    output = []
    for index, (left, right, label) in enumerate(spreads, 1):
        turn = ""
        if left and right:
            turn = f'''<details><summary>Turn text</summary>
              <p><b>Out:</b> {html.escape(left.final_beat)}</p>
              <p><b>Land:</b> {html.escape(right.purpose)}</p>
            </details>'''
        output.append(
            f'''<section class="spread" id="spread-{index:02d}">
              <div class="spread-label"><span>Spread {index:02d}</span><b>{html.escape(label)}</b></div>
              <div class="spread-pages">{page_card(left, position="left")}{page_card(right, position="right")}</div>
              {turn}
            </section>'''
        )
    return "".join(output)


def build_document(pages: list[Page]) -> str:
    total_panels = sum(page.panel_count for page in pages)
    total_words = sum(page.word_count for page in pages)
    densest = max(pages, key=lambda page: page.word_count)
    count_five = sum(page.panel_count == 5 for page in pages)
    spread_count = len(physical_spreads(pages))
    body = spread_rows(pages)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Production thumbnail wall — zz-no-consumer</title>
  <style>
    :root{{--paper:#ded8c8;--ink:#17191b;--muted:#6e6b63;--claret:#773b48;--steel:#4e6673}}
    *{{box-sizing:border-box}} body{{margin:0;background:#111315;color:#ece7d9;font:14px/1.4 system-ui,sans-serif}}
    .mast{{position:sticky;top:0;z-index:3;padding:18px 24px;background:#17191bf2;border-bottom:1px solid #34383b}}
    .mast h1{{margin:0 0 5px;font-size:20px}} .mast p{{margin:0;color:#b8b4a9}}
    .summary{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}} .summary span{{padding:5px 9px;border:1px solid #424649;border-radius:999px}}
    main{{max-width:1500px;margin:auto;padding:26px;display:grid;grid-template-columns:repeat(auto-fit,minmax(410px,1fr));gap:28px}}
    .spread{{break-inside:avoid}} .spread-label{{display:flex;justify-content:space-between;margin-bottom:8px;color:#aaa69b}}
    .spread-pages{{display:grid;grid-template-columns:1fr 1fr;gap:7px;padding:9px;background:#070809;box-shadow:0 6px 22px #0008}}
    .page-card{{min-width:0;aspect-ratio:.72;background:var(--paper);color:var(--ink);padding:8px;display:flex;flex-direction:column;gap:7px}}
    .page-card.left{{border-right:2px solid #27282a}} .page-card.blank{{align-items:center;justify-content:center;color:#777269;background:#c7c1b2}}
    .page-card header{{display:flex;justify-content:space-between;text-transform:uppercase;font-size:10px;letter-spacing:.12em}}
    .mini-page{{flex:1;display:grid;gap:3px;min-height:0}} .mini-panel{{position:relative;background:#3f4748;border:1px solid #242829}}
    .mini-panel:nth-child(3n+2){{background:#59605d}} .mini-panel:nth-child(3n){{background:#293336}}
    .mini-panel i{{position:absolute;left:4px;top:2px;color:#d6d2c6;font:8px ui-monospace,monospace}}
    .grid-nine{{grid-template:repeat(3,1fr)/repeat(3,1fr)}} .grid-six{{grid-template:repeat(3,1fr)/repeat(2,1fr)}}
    .grid-four{{grid-template:repeat(2,1fr)/repeat(2,1fr)}} .stack-three{{grid-template:repeat(3,1fr)/1fr}}
    .split-two{{grid-template:1fr/1fr 1fr}} .splash-one{{grid-template:1fr/1fr}}
    .wide-top,.wide-bottom,.tall-left,.tall-right{{grid-template:repeat(3,1fr)/repeat(2,1fr)}}
    .wide-top .mini-panel:first-child{{grid-column:1/3}} .wide-bottom .mini-panel:last-child{{grid-column:1/3}}
    .tall-left .mini-panel:first-child{{grid-row:1/3}} .tall-right .mini-panel:last-child{{grid-column:2;grid-row:2/4}}
    .page-copy h3{{font-size:12px;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .page-copy p,.page-copy small{{margin:0;font-size:9px}} .page-copy small{{color:var(--muted)}}
    .density-warning{{outline:4px solid var(--claret)}} .rhythm-note{{outline:2px solid var(--steel)}}
    details{{margin-top:7px;color:#bdb9ae;font-size:11px}} details p{{margin:5px 0}} summary{{cursor:pointer}}
    @media print{{.mast{{position:static}} main{{display:block}} .spread{{page-break-inside:avoid;margin-bottom:12mm}} details{{display:block}}}}
  </style>
</head>
<body>
  <header class="mast"><h1>ZZ: NO CONSUMER — provisional thumbnail wall</h1>
    <p>Panel order is canonical; geometry is provisional. Blue outlines mark non-default rhythms. Claret would mark pages over {DENSE} words.</p>
    <div class="summary"><span>{len(pages)} pages</span><span>{total_panels} panels</span><span>{total_words} lettered words</span><span>{count_five} five-panel pages</span><span>Densest: {densest.number:03d} / {densest.word_count} words</span><span>{spread_count} physical spreads</span></div>
  </header>
  <main>{body}</main>
</body>
</html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    pages = load_pages()
    invalid = [page.number for page in pages if page.panel_count == 0]
    if invalid:
        raise SystemExit(f"Pages with no recognized panel structure: {invalid}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_document(pages), encoding="utf-8")
    densest = max(pages, key=lambda page: page.word_count)
    print(
        f"Built {len(physical_spreads(pages))}-spread thumbnail wall for {len(pages)} pages / "
        f"{sum(page.panel_count for page in pages)} panels at {output.relative_to(ROOT)}."
    )
    print(
        f"Lettering: {sum(page.word_count for page in pages)} visible words; "
        f"densest page {densest.number:03d} has {densest.word_count}; "
        f"{sum(page.word_count > DENSE for page in pages)} pages exceed {DENSE}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
