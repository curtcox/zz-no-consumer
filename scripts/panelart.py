#!/usr/bin/env python3
"""Keep every version of every panel, and defer the choice between them.

A panel is not right or wrong on the first attempt. Different models draw it
differently, a re-roll finds a better composition, and which one belongs in the
book is a judgement that should be made late, over the whole sequence, not at the
moment of generation. So generation never overwrites: each attempt is stored as a
new variant beside the others, and the decision is recorded separately.

    assets/art/panels/001-01/v01-flux2-klein-4b-1001.webp
    assets/art/panels/001-01/v02-qwen-image-1001.webp

`data/panel-art.tsv` lists every variant with where it came from, and carries the
one column that is a human decision rather than a fact: `status`, which is
`candidate`, `chosen`, or `rejected`. Scanning refreshes the facts and preserves
the decisions, so the table can be regenerated without losing curation.

    python3 scripts/panelart.py scan               # discover variants, keep decisions
    python3 scripts/panelart.py list --panel 001-01
    python3 scripts/panelart.py choose 001-01 v02
    python3 scripts/panelart.py reject 001-01 v01 --note "hands"
    python3 scripts/panelart.py clear  001-01 v01   # undo a choice or rejection
    python3 scripts/panelart.py status             # how much of the book is decided
    python3 scripts/panelart.py size               # what the store costs the repository

Until a panel is decided, `resolve()` returns its highest-numbered candidate, so
the site builds and the whole book stays readable end to end while the choosing
happens. `scripts/build-site.py` letters whatever resolve returns and publishes the
other candidates as alternates the reader can open.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "assets" / "art" / "panels"
TABLE = ROOT / "data" / "panel-art.tsv"

SUFFIXES = (".webp", ".png", ".jpg", ".jpeg")
PANEL_ID = re.compile(r"^\d{3}-\d{2}$")
VARIANT_FILE = re.compile(r"^(v\d{2,})(?:-(.+?))?(?:-(\d+))?$")

CANDIDATE, CHOSEN, REJECTED = "candidate", "chosen", "rejected"
STATUSES = (CANDIDATE, CHOSEN, REJECTED)

HEADER = ("panel", "variant", "file", "provider", "seed",
          "width", "height", "bytes", "created", "status", "note")


@dataclass(frozen=True)
class Variant:
    panel: str
    variant: str
    file: str            # repository-relative
    provider: str = ""
    seed: str = ""
    width: str = ""
    height: str = ""
    bytes: str = ""
    created: str = ""
    status: str = CANDIDATE
    note: str = ""

    @property
    def path(self) -> Path:
        return ROOT / self.file

    @property
    def number(self) -> int:
        return int(self.variant.lstrip("v") or 0)


# ------------------------------------------------------------------ the store


def variant_dir(panel: str) -> Path:
    return ART_DIR / panel


def measure(path: Path) -> tuple[str, str]:
    try:
        from PIL import Image
        with Image.open(path) as image:
            return str(image.width), str(image.height)
    except Exception:                       # Pillow absent, or not an image we read
        return "", ""


def discover() -> list[Variant]:
    """Every variant on disk, including legacy flat files as v01."""
    found: list[Variant] = []
    if not ART_DIR.is_dir():
        return found

    for entry in sorted(ART_DIR.iterdir()):
        if entry.is_dir() and PANEL_ID.match(entry.name):
            for file in sorted(entry.iterdir()):
                if file.suffix.lower() not in SUFFIXES:
                    continue
                match = VARIANT_FILE.match(file.stem)
                if not match:
                    continue
                width, height = measure(file)
                found.append(Variant(
                    panel=entry.name, variant=match.group(1),
                    file=str(file.relative_to(ROOT)),
                    provider=match.group(2) or "", seed=match.group(3) or "",
                    width=width, height=height, bytes=str(file.stat().st_size),
                    created=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc)
                            .isoformat(timespec="seconds"),
                ))
        elif entry.is_file() and entry.suffix.lower() in SUFFIXES and PANEL_ID.match(entry.stem):
            # Art written before the store existed: treat it as that panel's v01.
            width, height = measure(entry)
            found.append(Variant(
                panel=entry.stem, variant="v01", file=str(entry.relative_to(ROOT)),
                width=width, height=height, bytes=str(entry.stat().st_size),
                created=datetime.fromtimestamp(entry.stat().st_mtime, timezone.utc)
                        .isoformat(timespec="seconds"),
            ))
    return found


def read_table(path: Path = TABLE) -> list[Variant]:
    if not path.is_file():
        return []
    rows = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        return []
    return [Variant(**dict(zip(rows[0], row))) for row in rows[1:]]


def write_table(variants: list[Variant], path: Path = TABLE) -> None:
    ordered = sorted(variants, key=lambda v: (v.panel, v.number))
    lines = ["\t".join(HEADER)]
    lines += ["\t".join(str(getattr(v, column)) for column in HEADER) for v in ordered]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def scan(path: Path = TABLE) -> tuple[list[Variant], int, int]:
    """Refresh the facts from disk, keep the decisions already recorded."""
    decisions = {(v.panel, v.variant): (v.status, v.note) for v in read_table(path)}
    found = discover()
    merged = []
    for variant in found:
        status, note = decisions.get((variant.panel, variant.variant), (CANDIDATE, ""))
        merged.append(replace(variant, status=status, note=note))
    gone = len(decisions) - sum(1 for v in found if (v.panel, v.variant) in decisions)
    return merged, len(found), max(0, gone)


def by_panel(variants: list[Variant]) -> dict[str, list[Variant]]:
    grouped: dict[str, list[Variant]] = {}
    for variant in variants:
        grouped.setdefault(variant.panel, []).append(variant)
    for items in grouped.values():
        items.sort(key=lambda v: v.number)
    return grouped


# -------------------------------------------------------------- resolution


def pick(variants: list[Variant]) -> Variant | None:
    """The version of this panel the book should show right now.

    A decided panel uses its chosen variant. An undecided one uses its newest
    candidate, so the book reads end to end while the choosing is still open.
    """
    chosen = [v for v in variants if v.status == CHOSEN]
    if chosen:
        return max(chosen, key=lambda v: v.number)
    candidates = [v for v in variants if v.status != REJECTED]
    return max(candidates, key=lambda v: v.number) if candidates else None


_CACHE: dict[str, list[Variant]] | None = None


def load(refresh: bool = False) -> dict[str, list[Variant]]:
    global _CACHE
    if _CACHE is None or refresh:
        table = read_table()
        _CACHE = by_panel(table) if table else by_panel(discover())
    return _CACHE


def resolve(page: str, index: int) -> Path | None:
    """The image file to letter and publish for this panel, or None."""
    variants = load().get(f"{page}-{index:02d}", [])
    winner = pick(variants)
    return winner.path if winner and winner.path.is_file() else None


def alternates(page: str, index: int) -> list[Variant]:
    """Other versions a reader could be shown, newest first."""
    variants = load().get(f"{page}-{index:02d}", [])
    winner = pick(variants)
    return [v for v in sorted(variants, key=lambda v: -v.number)
            if v is not winner and v.status != REJECTED and v.path.is_file()]


def next_number(panel: str) -> int:
    existing = [v.number for v in discover() if v.panel == panel]
    return max(existing, default=0) + 1


def store(panel: str, data: bytes, suffix: str, *, provider: str = "",
          seed: int | str = "") -> Path:
    """Write one more version of a panel. Never replaces an existing one."""
    directory = variant_dir(panel)
    directory.mkdir(parents=True, exist_ok=True)
    parts = [f"v{next_number(panel):02d}"]
    if provider:
        parts.append(provider)
    if seed != "":
        parts.append(str(seed))
    target = directory / ("-".join(parts) + suffix)
    target.write_bytes(data)
    return target


# --------------------------------------------------------------------- CLI


def cmd_scan(args: argparse.Namespace) -> int:
    merged, found, gone = scan()
    write_table(merged)
    print(f"Recorded {found} variant(s) across {len(by_panel(merged))} panel(s) "
          f"in {TABLE.relative_to(ROOT)}")
    if gone:
        print(f"{gone} recorded variant(s) are no longer on disk and were dropped.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    grouped = by_panel(read_table() or discover())
    panels = [args.panel] if args.panel else sorted(grouped)
    for panel in panels:
        variants = grouped.get(panel, [])
        if not variants:
            print(f"{panel}: no variants")
            continue
        winner = pick(variants)
        print(f"\n{panel}")
        for variant in variants:
            mark = "*" if variant is winner else " "
            size = f"{int(variant.bytes)//1024} KB" if variant.bytes.isdigit() else ""
            print(f" {mark} {variant.variant:<5} {variant.status:<10} {variant.provider:<18} "
                  f"{size:>7}  {variant.note}")
    print("\n* = the version the book currently shows")
    return 0


def _set_status(args: argparse.Namespace, status: str) -> int:
    merged, _, _ = scan()
    hit = False
    updated = []
    for variant in merged:
        if variant.panel == args.panel and variant.variant == args.variant:
            hit = True
            updated.append(replace(variant, status=status, note=args.note or variant.note))
        elif variant.panel == args.panel and status == CHOSEN and variant.status == CHOSEN:
            updated.append(replace(variant, status=CANDIDATE))   # only one chosen per panel
        else:
            updated.append(variant)
    if not hit:
        raise SystemExit(f"{args.panel} has no variant {args.variant}. "
                         f"Try `python3 scripts/panelart.py list --panel {args.panel}`.")
    write_table(updated)
    print(f"{args.panel} {args.variant} -> {status}")
    return 0


def cmd_choose(args: argparse.Namespace) -> int:
    return _set_status(args, CHOSEN)


def cmd_reject(args: argparse.Namespace) -> int:
    return _set_status(args, REJECTED)


def cmd_clear(args: argparse.Namespace) -> int:
    """Return a version to the running, undoing a choice or a rejection."""
    return _set_status(args, CANDIDATE)


def cmd_status(args: argparse.Namespace) -> int:
    grouped = by_panel(read_table() or discover())
    import textimage
    total = sum(len(s.panels) for s in textimage.book_scripts())
    decided = sum(1 for v in grouped.values() if any(x.status == CHOSEN for x in v))
    multiple = sum(1 for v in grouped.values() if len([x for x in v if x.status != REJECTED]) > 1)
    print(f"{len(grouped)} of {total} panels have art")
    print(f"{decided} decided, {len(grouped) - decided} showing a provisional newest candidate")
    print(f"{multiple} panel(s) have more than one version to choose between")
    if grouped and len(grouped) - decided:
        pending = [p for p, v in sorted(grouped.items()) if not any(x.status == CHOSEN for x in v)]
        print(f"\nUndecided: {', '.join(pending[:12])}{' …' if len(pending) > 12 else ''}")
    return 0


def cmd_size(args: argparse.Namespace) -> int:
    """What the store costs, and what it would cost at full coverage."""
    variants = read_table() or discover()
    total = sum(int(v.bytes) for v in variants if v.bytes.isdigit())
    panels = by_panel(variants)
    per = total / len(variants) if variants else 0
    print(f"{len(variants)} variant(s), {total/2**20:.1f} MB, "
          f"{per/1024:.0f} KB each on average")
    if per:
        for keep in (1, 2, 3):
            print(f"  541 panels x {keep} version(s): {541*keep*per/2**20:,.0f} MB")
    print("\nOnly the resolved version is published, embedded in its lettered SVG; "
          "alternates are copied once. The store itself is not copied into docs/.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("scan", help="discover variants and refresh the table")
    listing = commands.add_parser("list", help="show a panel's versions")
    listing.add_argument("--panel")
    for name, blurb in (("choose", "mark a version as the one for the book"),
                        ("reject", "set a version aside, keeping it on disk"),
                        ("clear", "return a version to the running")):
        sub = commands.add_parser(name, help=blurb)
        sub.add_argument("panel")
        sub.add_argument("variant")
        sub.add_argument("--note", default="")
    commands.add_parser("status", help="how much of the book is decided")
    commands.add_parser("size", help="what the store costs the repository")

    args = parser.parse_args()
    return {"scan": cmd_scan, "list": cmd_list, "choose": cmd_choose,
            "reject": cmd_reject, "clear": cmd_clear,
            "status": cmd_status, "size": cmd_size}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
