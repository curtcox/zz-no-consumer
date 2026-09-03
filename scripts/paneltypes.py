#!/usr/bin/env python3
"""Classify every panel by what its description demands of an image generator.

No single model is best at all of this. One panel is a dark room with no text and
wants whatever is cheapest; the next carries a thirty-character header and wants a
model that can spell; a third shows a named person and cannot be drawn at all until
an approved reference sheet exists. Routing them all to one generator means either
overpaying for the easy ones or failing the hard ones.

This module reads each panel's own description — the `Frame` and `Action` lines of
the page script, its display strings, and its page front matter — and assigns:

  * a TYPE, describing what the image is, and
  * a ROUTE, describing the capability a model needs to draw it.

Types are many-to-one onto routes, because several different-looking panels make
the same demand. `design/panel-image-types.md` is the key; `data/panel-types.tsv`
is the classification of all 539 panels, written by this script.

    python3 scripts/paneltypes.py write     # refresh data/panel-types.tsv
    python3 scripts/paneltypes.py summary   # counts by type and route
    python3 scripts/paneltypes.py show --type text-heavy

Classification is derived, not authored, so it stays correct when the script
changes. Anything it gets wrong should be fixed by sharpening a rule here rather
than by hand-editing the table, which is regenerated.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import imagegen
import textimage


ROOT = imagegen.ROOT
TABLE = ROOT / "data" / "panel-types.tsv"

# A string longer than this is where FLUX.2 klein 4B stopped spelling reliably.
LONG_STRING = 15
HEAVY_TOTAL = 24

PEOPLE = re.compile(
    r"\b(curt|responder|engineer|chair|counsel|investigator|analyst|operator|reviewer"
    r"|lead|figure|hands?|shoulder|face|team|staff|person|people|worker|colleague"
    r"|attendee|panelist)\b", re.I)
CURT = re.compile(r"\bcurt(?:'s)?\b", re.I)
# Deliberately narrow: a `UI-TASK-CARD` inset into a dark aisle is a scene with a
# card in it, not a dossier page. Only structure that dominates the panel counts.
DOSSIER = re.compile(
    r"\b(column|columns|dossier|page field|grid|ledger|archive|docket|filing"
    r"|top strip|persistent strip|verso)\b", re.I)
DIAGRAM = re.compile(
    r"\b(diagram|boundary map|arrow|graph|chart|topology|schematic|map|node|branch"
    r"|tree)\b", re.I)

# Type -> the capability a generator must have. Several types share a route.
ROUTES: dict[str, str] = {
    "portrait": "reference",
    "text-heavy": "text-fidelity",
    "figure": "figures",
    "dossier": "structure",
    "diagram": "structure",
    "text-light": "local",
    "scene": "local",
}


@dataclass(frozen=True)
class Panel:
    page: str
    index: int
    chapter: str
    register: str
    type: str
    strings: int
    longest: int
    text_chars: int

    @property
    def id(self) -> str:
        return f"{self.page}-{self.index:02d}"

    @property
    def route(self) -> str:
        return ROUTES[self.type]


def description(page: str, index: int) -> str:
    """The panel's own direction: everything before its lettering fields."""
    source = (imagegen.PAGE_DIR / f"{page}.md").read_text(encoding="utf-8")
    sections = re.split(r"^## Panel \d+\s*$", source, flags=re.M)[1:]
    if index > len(sections):
        return ""
    return re.split(
        r"^\*\*(?:Caption|Dialogue|Left dialogue|Right dialogue|Screen|Provenance|Qualification)",
        sections[index - 1], flags=re.M)[0]


NEGATION = re.compile(r"\b(no|not|never|without|absent|nobody|none)\b", re.I)


def mentions(pattern: re.Pattern[str], body: str) -> bool:
    """Whether the description really contains this, rather than ruling it out.

    Page scripts routinely say "No face, avatar, or speech balloon", and the
    style guide's whole point is what a panel must not show. Matching the bare
    word would classify those panels as the very thing they exclude, so a match
    inside a negated clause does not count.
    """
    for match in pattern.finditer(body):
        clause_start = max(body.rfind(".", 0, match.start()),
                           body.rfind(";", 0, match.start()),
                           body.rfind(":", 0, match.start())) + 1
        if not NEGATION.search(body[clause_start:match.start()]):
            return True
    return False


def classify(page: str, index: int, register: str, has_dialogue: bool) -> str:
    """Pick the one type that decides where this panel is generated.

    Ordered by how binding the demand is, not by how the panel looks: a dossier
    page carrying a long header is routed on the header, because that is the part
    a model will fail.
    """
    body = description(page, index)
    strings = imagegen.display_strings(page, index)
    longest = max((len(s) for s in strings), default=0)
    total = sum(len(s) for s in strings)

    if mentions(CURT, body) or (register == "creator" and (has_dialogue or mentions(PEOPLE, body))):
        return "portrait"
    if longest > LONG_STRING or total > HEAVY_TOTAL:
        return "text-heavy"
    if has_dialogue or mentions(PEOPLE, body):
        return "figure"
    if mentions(DOSSIER, body):
        return "dossier"
    if mentions(DIAGRAM, body):
        return "diagram"
    if strings:
        return "text-light"
    return "scene"


def book_panels() -> list[Panel]:
    import produce                      # register derivation lives with the runner

    panels: list[Panel] = []
    for script in textimage.book_scripts():
        register = produce.register_for(script.id)
        fields = textimage.lettering_fields(script.id)
        for panel in script.panels:
            named = fields.get(panel.index, [])
            has_dialogue = any(name.split("—")[0].strip() in
                               ("Dialogue", "Left dialogue", "Right dialogue")
                               for name, _ in named)
            strings = imagegen.display_strings(script.id, panel.index)
            panels.append(Panel(
                page=script.id, index=panel.index, chapter=script.chapter,
                register=register,
                type=classify(script.id, panel.index, register, has_dialogue),
                strings=len(strings),
                longest=max((len(s) for s in strings), default=0),
                text_chars=sum(len(s) for s in strings),
            ))
    return panels


HEADER = ("panel", "page", "chapter", "register", "type", "route",
          "strings", "longest", "text_chars")


def write_table(panels: list[Panel], path: Path = TABLE) -> None:
    lines = ["\t".join(HEADER)]
    lines += ["\t".join((p.id, p.page, p.chapter, p.register, p.type, p.route,
                         str(p.strings), str(p.longest), str(p.text_chars)))
              for p in panels]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_table(path: Path = TABLE) -> list[dict]:
    rows = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [dict(zip(rows[0], row)) for row in rows[1:]]


def cmd_write(args: argparse.Namespace) -> int:
    panels = book_panels()
    write_table(panels)
    print(f"Wrote {len(panels)} panels to {TABLE.relative_to(ROOT)}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    panels = book_panels()
    by_type: dict[str, int] = {}
    by_route: dict[str, int] = {}
    for panel in panels:
        by_type[panel.type] = by_type.get(panel.type, 0) + 1
        by_route[panel.route] = by_route.get(panel.route, 0) + 1

    print(f"{len(panels)} panels\n")
    print(f"{'TYPE':<12} {'PANELS':>7} {'SHARE':>7}  ROUTE")
    for name in ROUTES:
        count = by_type.get(name, 0)
        print(f"{name:<12} {count:>7} {100*count/len(panels):>6.1f}%  {ROUTES[name]}")
    print(f"\n{'ROUTE':<15} {'PANELS':>7} {'SHARE':>7}")
    for route, count in sorted(by_route.items(), key=lambda kv: -kv[1]):
        print(f"{route:<15} {count:>7} {100*count/len(panels):>6.1f}%")

    heavy = [p for p in panels if p.type == "text-heavy"]
    if heavy:
        print(f"\nLongest display string: {max(p.longest for p in heavy)} characters")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    panels = book_panels()
    chosen = [p for p in panels
              if (not args.type or p.type in args.type)
              and (not args.route or p.route in args.route)]
    print(f"{'PANEL':<9} {'TYPE':<12} {'ROUTE':<14} {'REGISTER':<16} {'STR':>4} {'LONGEST':>8}")
    for panel in chosen[:args.limit]:
        print(f"{panel.id:<9} {panel.type:<12} {panel.route:<14} {panel.register:<16} "
              f"{panel.strings:>4} {panel.longest:>8}")
    print(f"\n{len(chosen)} panel(s)"
          + (f", showing {args.limit}" if len(chosen) > args.limit else ""))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("write", help="refresh data/panel-types.tsv")
    commands.add_parser("summary", help="counts by type and route")
    show = commands.add_parser("show", help="list panels of a type or route")
    show.add_argument("--type", action="append")
    show.add_argument("--route", action="append")
    show.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    return {"write": cmd_write, "summary": cmd_summary, "show": cmd_show}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
