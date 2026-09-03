#!/usr/bin/env python3
"""Compose the controlled lettering layer over panel art.

Generated art cannot be trusted to leave text alone, and it cannot be trusted to
letter it correctly when it tries. The answer is not to fight the model for the
last glyph but to keep every word the book actually says in a separate layer that
the build owns: the art supplies a quiet field, this supplies the words.

Placement is convention, not per-panel authorship. `data/lettering-slots.json`
defines a small set of anchored slots as fractions of the panel, and a strict
raster order for filling them, so 435 of the book's roughly 500 lettering
elements — every caption and every interface block — are placed from the page
script with nothing to author. The residue is dialogue: a balloon needs a speaker
position, which no convention can derive, so those panels stay a manual pass and
are reported rather than guessed at.

    python3 scripts/letterpress.py slots                 # render the slot map
    python3 scripts/letterpress.py panel --page 001 --image 1 --art PATH
    python3 scripts/letterpress.py audit                 # what fits, what needs a hand
    python3 scripts/letterpress.py page --page 001 --out-dir DIR

Two emitters share one layout pass. SVG keeps the web viewer dependency-free;
`--flatten` rasterises with Pillow for print, imported lazily so the repository
still runs without it.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import textimage


ROOT = Path(__file__).resolve().parents[1]
SLOTS_FILE = ROOT / "data" / "lettering-slots.json"
ART_DIR = ROOT / "assets" / "art" / "panels"
PANEL_SIZE = textimage.PANEL_SIZE


def load_slots(path: Path = SLOTS_FILE) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    check_disjoint(record)
    return record


def check_disjoint(record: dict) -> None:
    """`top` and `bottom` replace the corner slots; everything else must not collide."""
    slots = record["slots"]
    names = [n for n in slots if n not in ("top", "bottom")]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            A, B = slots[a], slots[b]
            ox = max(0.0, min(A["x"]+A["w"], B["x"]+B["w"]) - max(A["x"], B["x"]))
            oy = max(0.0, min(A["y"]+A["h"], B["y"]+B["h"]) - max(A["y"], B["y"]))
            if ox * oy > 1e-9:
                raise SystemExit(f"lettering slots {a} and {b} overlap by {ox*oy:.3f} of the panel")


# ------------------------------------------------------------------- layout


@dataclass(frozen=True)
class Placed:
    """One lettering element, measured and positioned on the panel."""

    role: str
    slot: str
    header: str
    x: float
    y: float
    w: float
    h: float
    size: float
    leading: float
    lines: tuple[str, ...]
    truncated: bool


def role_for(field: str, roles: dict) -> str | None:
    """Which role letters this script field. Dialogue deliberately has none."""
    # An exact field match wins over the base name, so
    # "Screen / system text — CHATGPT" letters as an interface voice in mixed
    # case rather than falling through to the monospaced machine role.
    for name, spec in roles.items():
        if field in spec["fields"]:
            return name
    base = field.split("—")[0].strip()
    for name, spec in roles.items():
        if base in spec["fields"]:
            return name
    return None


def speaker_of(field: str) -> str:
    parts = [p.strip() for p in field.split("—")]
    return parts[1] if len(parts) > 1 else ""


def layout_panel(fields: list[tuple[str, str]], record: dict,
                 width: int, height: int) -> tuple[list[Placed], list[tuple[str, str]]]:
    """Place what convention can place; hand back what it cannot."""
    roles, slots, order = record["roles"], record["slots"], record["order"]
    pad = record["padding"] * width
    used: dict[str, int] = {}
    placed: list[Placed] = []
    manual: list[tuple[str, str]] = []

    for field, text in fields:
        role = role_for(field, roles)
        if role is None:
            manual.append((field, text))
            continue
        sequence = order.get(role, [])
        index = used.get(role, 0)
        if index >= len(sequence):
            manual.append((field, text))
            continue
        used[role] = index + 1
        spec = roles[role]
        slot = slots[sequence[index]]

        box_w = slot["w"] * width
        box_h = slot["h"] * height
        header = speaker_of(field) if spec.get("header") else ""
        head_h = (spec["min_size"] + 6) if header else 0
        inner_w = box_w - 2 * pad
        inner_h = box_h - 2 * pad - head_h

        body = text.upper() if spec["uppercase"] else text
        flowed = textimage.flow(body, inner_w, inner_h,
                                min_size=spec["min_size"], max_size=spec["max_size"])
        # Shrink the box to the measured content, keeping the slot's anchor fixed.
        longest = max((textimage.advance(line, flowed.size) for line in flowed.lines), default=0.0)
        tracking = spec["tracking"] * flowed.size
        longest += tracking * max((len(line) - 1 for line in flowed.lines), default=0)
        if header:
            longest = max(longest, textimage.advance(header, spec["min_size"]))
        fit_w = min(box_w, longest + 2 * pad)
        fit_h = min(box_h, flowed.height + 2 * pad + head_h)

        anchor = slot["anchor"]
        x = slot["x"] * width if "left" in anchor else (slot["x"] + slot["w"]) * width - fit_w
        y = slot["y"] * height if "top" in anchor else (slot["y"] + slot["h"]) * height - fit_h
        placed.append(Placed(role, sequence[index], header, x, y, fit_w, fit_h,
                             flowed.size, flowed.leading, flowed.lines, flowed.truncated))
    return placed, manual


def panel_layout(page_id: str, index: int, record: dict,
                 width: int = PANEL_SIZE[0], height: int = PANEL_SIZE[1]):
    fields = textimage.lettering_fields(page_id).get(index, [])
    return layout_panel(fields, record, width, height)


# ------------------------------------------------------------- SVG emitter


def _stack(fonts: list[str]) -> str:
    return ", ".join(f"'{f}'" if " " in f else f for f in fonts)


def svg_layer(placed: list[Placed], record: dict, width: int, height: int) -> str:
    roles, fonts = record["roles"], record["fonts"]
    pad = record["padding"] * width
    out = []
    for item in placed:
        spec = roles[item.role]
        family = _stack(fonts[spec["font"]])
        out.append(
            f'<g><rect x="{item.x:.1f}" y="{item.y:.1f}" width="{item.w:.1f}" '
            f'height="{item.h:.1f}" fill="{spec["box"]}" stroke="{spec["border"]}" '
            f'stroke-width="{spec["border_width"]}"/>'
        )
        top = item.y + pad
        if item.header:
            bar = spec["min_size"] + 4
            out.append(
                f'<rect x="{item.x:.1f}" y="{item.y:.1f}" width="{item.w:.1f}" '
                f'height="{bar + 2:.1f}" fill="{spec["border"]}"/>'
                f'<text x="{item.x + pad:.1f}" y="{item.y + bar - 1:.1f}" '
                f'font-family="{family}" font-size="{spec["min_size"] - 1:.1f}" '
                f'fill="{spec["box"]}" letter-spacing="0.4">{html.escape(item.header)}</text>'
            )
            top += bar
        baseline = top + item.size
        spans = []
        for line in item.lines:
            if line:
                spans.append(
                    f'<tspan x="{item.x + pad:.1f}" y="{baseline:.1f}">{html.escape(line)}</tspan>')
                baseline += item.leading
            else:
                baseline += item.leading * 0.62
        out.append(
            f'<text font-family="{family}" font-size="{item.size:.1f}" fill="{spec["ink"]}" '
            f'letter-spacing="{spec["tracking"] * item.size:.2f}">{"".join(spans)}</text></g>'
        )
    return "".join(out)


def svg_panel(placed: list[Placed], record: dict, width: int, height: int,
              art: Path | None = None, art_href: str | None = None) -> str:
    image = ""
    if art_href:
        image = f'<image href="{html.escape(art_href)}" x="0" y="0" width="{width}" height="{height}"/>'
    elif art:
        import base64
        kind = {"png": "png", "webp": "webp", "jpg": "jpeg", "jpeg": "jpeg"}[art.suffix.lstrip(".").lower()]
        data = base64.b64encode(art.read_bytes()).decode()
        image = (f'<image href="data:image/{kind};base64,{data}" x="0" y="0" '
                 f'width="{width}" height="{height}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{image}'
            f'{svg_layer(placed, record, width, height)}</svg>')


# ---------------------------------------------------------- raster emitter


def raster_panel(placed: list[Placed], record: dict, width: int, height: int,
                 art: Path | None, scale: float = 1.0):
    """Flatten to a raster for print. Pillow only, imported here so the rest runs without it."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise SystemExit(
            "--flatten needs Pillow (pip install pillow). The SVG path needs nothing.") from None

    W, H = int(width * scale), int(height * scale)
    if art and art.is_file():
        base = Image.open(art).convert("RGB").resize((W, H), Image.LANCZOS)
    else:
        base = Image.new("RGB", (W, H), "#202326")
    draw = ImageDraw.Draw(base)
    roles, fonts = record["roles"], record["fonts"]
    pad = record["padding"] * width * scale

    def font_for(spec, size):
        path = fonts.get("raster_mono" if spec["font"] == "mono" else "raster_sans")
        try:
            return ImageFont.truetype(path, max(1, int(size * scale)))
        except (OSError, TypeError):
            return ImageFont.load_default()

    for item in placed:
        spec = roles[item.role]
        box = [item.x*scale, item.y*scale, (item.x+item.w)*scale, (item.y+item.h)*scale]
        draw.rectangle(box, fill=spec["box"], outline=spec["border"],
                       width=max(1, int(spec["border_width"] * scale)))
        top = item.y*scale + pad
        if item.header:
            bar = (spec["min_size"] + 4) * scale
            draw.rectangle([box[0], box[1], box[2], box[1] + bar + 2], fill=spec["border"])
            draw.text((box[0] + pad, box[1] + 2), item.header,
                      font=font_for(spec, spec["min_size"] - 1), fill=spec["box"])
            top += bar
        face = font_for(spec, item.size)
        y = top
        for line in item.lines:
            if line:
                draw.text((box[0] + pad, y), line, font=face, fill=spec["ink"])
                y += item.leading * scale
            else:
                y += item.leading * 0.62 * scale
    return base


# ------------------------------------------------------------- the slot map


def slot_map_svg(record: dict, width: int, height: int) -> str:
    slots, order = record["slots"], record["order"]
    tint = {"caption": "#74864F", "machine": "#5E737B", "interface": "#AA9571", "slate": "#A17D45"}
    where = {}
    for role, names in order.items():
        for position, name in enumerate(names, 1):
            where[name] = (role, position)
    out = [f'<rect width="{width}" height="{height}" fill="#101214"/>']
    margin = record["margin"]
    out.append(f'<rect x="{margin*width:.0f}" y="{margin*height:.0f}" '
               f'width="{(1-2*margin)*width:.0f}" height="{(1-2*margin)*height:.0f}" '
               f'fill="none" stroke="#3E3931" stroke-dasharray="6 6"/>')
    for name, slot in slots.items():
        role, position = where.get(name, ("unused", 0))
        colour = tint.get(role, "#6B2634")
        x, y = slot["x"]*width, slot["y"]*height
        w, h = slot["w"]*width, slot["h"]*height
        out.append(
            f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{colour}" '
            f'fill-opacity="0.18" stroke="{colour}" stroke-width="2"/>'
            f'<text x="{x+8:.0f}" y="{y+22:.0f}" font-family="Helvetica, Arial" font-size="17" '
            f'font-weight="700" fill="{colour}">{html.escape(name)}</text>'
            f'<text x="{x+8:.0f}" y="{y+40:.0f}" font-family="Helvetica, Arial" font-size="13" '
            f'fill="{colour}">{html.escape(role)}{f" #{position}" if position else ""}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(out)}</svg>')


# --------------------------------------------------------------------- CLI


def find_art(page_id: str, index: int) -> Path | None:
    for suffix in (".webp", ".png", ".jpg", ".jpeg"):
        candidate = ART_DIR / f"{page_id}-{index:02d}{suffix}"
        if candidate.is_file():
            return candidate
    return None


def cmd_slots(args: argparse.Namespace) -> int:
    record = load_slots()
    out = args.out or (ROOT / "assets" / "bakeoff" / "lettering-slot-map.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(slot_map_svg(record, *PANEL_SIZE), encoding="utf-8")
    print(f"status: {record['status']}")
    print(f"{'SLOT':<10} {'ROLE':<11} {'ORDER':>5}  BOX (fractions)")
    where = {n: (r, i) for r, names in record["order"].items() for i, n in enumerate(names, 1)}
    for name, slot in record["slots"].items():
        role, position = where.get(name, ("—", 0))
        print(f"{name:<10} {role:<11} {position or '-':>5}  "
              f"x{slot['x']:.2f} y{slot['y']:.2f} w{slot['w']:.2f} h{slot['h']:.2f} {slot['anchor']}")
    print(f"\nSlot map: {out.relative_to(ROOT)}")
    return 0


def cmd_panel(args: argparse.Namespace) -> int:
    record = load_slots()
    placed, manual = panel_layout(args.page, args.image, record)
    art = Path(args.art) if args.art else find_art(args.page, args.image)
    out = args.out or ROOT / f"letterpress-{args.page}-{args.image:02d}." \
                             f"{'png' if args.flatten else 'svg'}"
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.flatten:
        raster_panel(placed, record, *PANEL_SIZE, art, args.scale).save(out)
    else:
        out.write_text(svg_panel(placed, record, *PANEL_SIZE, art=art), encoding="utf-8")

    for item in placed:
        mark = " TRUNCATED" if item.truncated else ""
        print(f"  {item.role:<10} -> {item.slot:<9} {item.w:>5.0f}x{item.h:<5.0f} "
              f"{item.size:>5.1f}px  {len(item.lines)} line(s){mark}")
    for field, text in manual:
        print(f"  MANUAL     {field}: {text[:52]}")
    print(f"Wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}"
          f"{'' if art else '  (no art found; lettering layer only)'}")
    return 0


def cmd_page(args: argparse.Namespace) -> int:
    record = load_slots()
    out_dir = args.out_dir or ROOT / "assets" / "bakeoff" / "letterpress"
    out_dir.mkdir(parents=True, exist_ok=True)
    script = textimage.page_script(args.page)
    for panel in script.panels:
        placed, manual = panel_layout(args.page, panel.index, record)
        art = find_art(args.page, panel.index)
        target = out_dir / f"{args.page}-{panel.index:02d}.svg"
        target.write_text(svg_panel(placed, record, *PANEL_SIZE, art=art), encoding="utf-8")
        print(f"  {target.name}  {len(placed)} placed, {len(manual)} manual")
    print(f"Wrote {len(script.panels)} panel(s) into {out_dir.relative_to(ROOT)}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    """How much of the book's lettering the convention actually places."""
    record = load_slots()
    placed_n = manual_n = truncated_n = 0
    by_role: dict[str, int] = {}
    needs_hand: list[str] = []
    for script in textimage.book_scripts():
        fields = textimage.lettering_fields(script.id)
        for panel in script.panels:
            placed, manual = layout_panel(fields.get(panel.index, []), record, *PANEL_SIZE)
            placed_n += len(placed)
            manual_n += len(manual)
            for item in placed:
                by_role[item.role] = by_role.get(item.role, 0) + 1
                truncated_n += item.truncated
            if manual:
                needs_hand.append(f"{script.id}-{panel.index:02d}")
    total = placed_n + manual_n
    print(f"{'ROLE':<12} {'PLACED':>7}")
    for role, count in sorted(by_role.items(), key=lambda kv: -kv[1]):
        print(f"{role:<12} {count:>7}")
    print(f"{'':<12} {'-'*7}\n{'automatic':<12} {placed_n:>7}  ({100*placed_n/total:.1f}% of {total})")
    print(f"{'manual':<12} {manual_n:>7}  ({100*manual_n/total:.1f}%) across {len(needs_hand)} panels")
    if truncated_n:
        print(f"\n{truncated_n} element(s) did not fit their slot at minimum type size.")
    print(f"\nPanels needing a hand-placed balloon: {len(needs_hand)}")
    print("  " + ", ".join(needs_hand[:12]) + (" …" if len(needs_hand) > 12 else ""))
    return 1 if truncated_n else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    slots = commands.add_parser("slots", help="print the convention and render a slot map")
    slots.add_argument("--out", type=Path)

    panel = commands.add_parser("panel", help="letter one panel")
    panel.add_argument("--page", required=True)
    panel.add_argument("--image", type=int, default=1)
    panel.add_argument("--art", help="panel art; defaults to assets/art/panels/NNN-II.*")
    panel.add_argument("--out", type=Path)
    panel.add_argument("--flatten", action="store_true", help="rasterise with Pillow for print")
    panel.add_argument("--scale", type=float, default=1.0, help="raster scale, e.g. 3 for 300dpi")

    page = commands.add_parser("page", help="letter every panel of one page")
    page.add_argument("--page", required=True)
    page.add_argument("--out-dir", type=Path)

    commands.add_parser("audit", help="how much of the book the convention places")

    args = parser.parse_args()
    return {"slots": cmd_slots, "panel": cmd_panel, "page": cmd_page,
            "audit": cmd_audit}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
