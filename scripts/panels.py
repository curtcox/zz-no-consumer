#!/usr/bin/env python3
"""Insert, delete, and move panels inside a story page, and price what that costs.

A panel's identity is its ordinal index inside its page, written ``NN`` and joined to the
page as ``NNN-II``. That index lives in the ``## Panel N`` heading, in art keys in
``data/panel-art.tsv``, in ``assets/art/panels/NNN-II/``, in ``prompts/pages/NNN/panel-II.md``,
in the generated classification table and viewer routes, and in the page notes and frame
directions that say things like "Panel 4 is the first time in the book that ChatGPT states
something the next panel contradicts". This module owns every one of those sites, so adding
a beat to a page is one deterministic rewrite rather than a reason to grow an existing
panel's Action line.

Renumbering is the cheap half, exactly as it is for pages. The expensive half is different.
Pages have parity; panels have **rhythm and lettering load**. ``design/page-grammar.md``
bands a page at four to six panels by default, one to three for an establishing or
revelation page, five to nine for a procedural sequence; and ``design/lettering-slots.md``
places a panel's lettering into four anchored corner slots, so a fifth element on one panel
has nowhere to go. Neither is repaired here. An operation prints the page's new rhythm, the
band it lands in, and every panel whose lettering no longer fits, and stops. Which of those
is a real problem is an editorial judgement, the same way a broken page turn is.

    python3 scripts/panels.py report
    python3 scripts/panels.py check
    python3 scripts/panels.py insert --page 039 --at 4
    python3 scripts/panels.py delete 039-04 --apply
    python3 scripts/panels.py move 086-06 --to 3 --apply

Operations print a plan and touch nothing without ``--apply``. ``check`` exits non-zero
while the tree disagrees with itself, so a rhythm taken knowingly cannot be forgotten.

The panel count is a measurement, never an invariant: ``report`` derives it, and nothing in
the repository should hard-code it. The reasoning that settled page identity the same way is
in ``design/page-identity.md``.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crossref  # noqa: E402  the page/chapter/sequence graph is modelled once, there


ROOT = Path(__file__).resolve().parents[1]

# Files whose panel numbers are a dated record of something that happened, not a pointer to
# a panel. Renumbering them would falsify the record, so they are reported and left alone.
HISTORICAL = (
    "data/generation-log.jsonl",
    "design/image-generation-options.md",
    "design/page-identity.md",
    "design/panel-identity.md",
)

# Derived from the page scripts. An operation invalidates them; it does not rewrite them.
GENERATED = (
    "data/panel-types.tsv",
    "docs/viewer",
)

# Hand-written prose that can name a panel. `prompts/pages/NNN/` is page-scoped, so a bare
# reference inside it is local to that page in the same way a page script's is.
PROSE_GLOBS = (
    "README.md",
    "content/**/*.md",
    "design/**/*.md",
    "research/**/*.md",
    "prompts/**/*.md",
)

# The rhythm bands in design/page-grammar.md. The default band is what an operation is
# measured against; the outer band is what the grammar permits at all.
DEFAULT_BAND = (4, 6)
GRAMMAR_BAND = (1, 9)

# design/lettering-slots.md places lettering in four anchored corner slots per panel.
SLOTS_PER_PANEL = 4
# scripts/make-thumbnails.py has always flagged a page over this as dense.
DENSE_PAGE_WORDS = 180


# ---------------------------------------------------------------------------
# the panel model
#
# Two page scripts (006 and 007) write a nine-panel grid as one grouped run,
# `## Panels 1–9`, because the grid is a single composition and the viewer exposes it as one
# image slot. That is an editorial unit, so this module reports such a page and refuses to
# operate inside it rather than inventing nine headings the script never had.
# ---------------------------------------------------------------------------

# `[ \t]*` rather than `\s*`: a trailing `\s*` would swallow the blank line that separates a
# heading from its first field, and the rewriter would close that gap on every pass.
PANEL_HEADING = re.compile(r"^## Panel (\d+)[ \t]*$", re.MULTILINE)
GROUPED_HEADING = re.compile(r"^## Panels (\d+)[–-](\d+)[ \t]*$", re.MULTILINE)
SECTION_HEADING = re.compile(r"^## ", re.MULTILINE)
WORD = re.compile(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)*")

VISIBLE_HEADERS = ("**Caption", "**Dialogue", "**Screen / system text", "**Qualification")


def panel_count(source: str) -> int:
    """The number of panels a page script declares, grouped runs included."""
    individual = len(PANEL_HEADING.findall(source))
    if individual:
        return individual
    grouped = GROUPED_HEADING.search(source)
    if grouped:
        return int(grouped.group(2)) - int(grouped.group(1)) + 1
    return 0


def visible_text(source: str) -> list[str]:
    """Extract intended lettering, excluding script directions and provenance."""
    output: list[str] = []
    active = False
    for line in source.splitlines():
        if line.startswith("## "):
            active = False
        if line.startswith(VISIBLE_HEADERS):
            active = True
            continue
        if line.startswith("**") and not line.startswith(VISIBLE_HEADERS):
            active = False
        if line.startswith("> "):
            output.append(line[2:].strip())
        elif active and line.startswith("`") and line.endswith("`"):
            output.append(line.strip("`").strip())
    return [line for line in output if line]


@dataclass(frozen=True)
class Section:
    """One ``## Panel N`` heading and everything under it, up to the next heading."""

    index: int
    body: str          # the text after the heading line, heading excluded

    @property
    def elements(self) -> int:
        return sum(1 for line in self.body.splitlines() if line.startswith(VISIBLE_HEADERS))

    @property
    def words(self) -> int:
        return sum(len(WORD.findall(line)) for line in visible_text("## Panel 0\n" + self.body))


@dataclass(frozen=True)
class PageScript:
    number: int
    text: str
    preamble: str                      # everything before the first panel heading
    sections: tuple[Section, ...]
    tail: str                          # everything from the heading after the last panel
    grouped: tuple[int, int] | None

    @property
    def id(self) -> str:
        return f"{self.number:03d}"

    @property
    def path(self) -> str:
        return f"content/pages/{self.id}.md"

    @property
    def indices(self) -> tuple[int, ...]:
        return tuple(section.index for section in self.sections)

    @property
    def count(self) -> int:
        return panel_count(self.text)

    @property
    def words(self) -> int:
        return sum(len(WORD.findall(line)) for line in visible_text(self.text))

    def compose(self, order: list[int], created: dict[int, str]) -> str:
        """Rebuild the script with ``order`` naming the old index of each new panel."""
        bodies = {section.index: section.body for section in self.sections}
        parts = [self.preamble]
        for position, old in enumerate(order, 1):
            body = created[old] if old in created else bodies[old]
            parts.append(f"## Panel {position}\n{body}")
        parts.append(self.tail)
        return "".join(parts)


def split_page(number: int, text: str) -> PageScript:
    heads = list(PANEL_HEADING.finditer(text))
    grouped_match = GROUPED_HEADING.search(text)
    grouped = (
        (int(grouped_match.group(1)), int(grouped_match.group(2))) if grouped_match else None
    )
    if not heads:
        return PageScript(number, text, text, (), "", grouped)

    sections: list[Section] = []
    for position, head in enumerate(heads):
        start = head.end() + 1 if text[head.end():head.end() + 1] == "\n" else head.end()
        following = SECTION_HEADING.search(text, head.end())
        while following and PANEL_HEADING.match(text, following.start()):
            following = SECTION_HEADING.search(text, following.end())
        end = heads[position + 1].start() if position + 1 < len(heads) else (
            following.start() if following else len(text)
        )
        sections.append(Section(int(head.group(1)), text[start:end]))
    last = heads[-1]
    following = SECTION_HEADING.search(text, last.end())
    tail = text[following.start():] if following else ""
    return PageScript(number, text, text[: heads[0].start()], tuple(sections), tail, grouped)


def read_scripts() -> dict[int, PageScript]:
    pages: dict[int, PageScript] = {}
    for path in sorted((ROOT / "content" / "pages").glob("[0-9][0-9][0-9].md")):
        pages[int(path.stem)] = split_page(int(path.stem), path.read_text(encoding="utf-8"))
    return pages


# ---------------------------------------------------------------------------
# reference sites in prose
#
# A panel reference is local unless it names a page. `Panel 4 is the first time...` in a page
# script means that page's panel 4; `Repeat page 003 panel 2` means another page's. Outside a
# page script or a `prompts/pages/NNN/` file there is no page to be local to, so a bare
# reference is reported and never guessed -- the same posture pagination.py takes toward a
# bare `page 6` that might be a source-document citation. Anything inside a code fence or
# inline backticks quotes a form rather than pointing at a panel, so it is an example.
# ---------------------------------------------------------------------------

PANEL_PHRASE = re.compile(
    r"(?P<page>\b[Pp]ages?\s+(?P<pagenum>\d{1,3})\s*(?:[—–-]\s*)?)?"
    r"\b(?P<kw>[Pp]anels?)(?P<sep>\s+)"
    r"(?P<first>\d{1,2})"
    r"(?P<rest>(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+|\s*[–—-]\s*)\d{1,2})*)"
)
PANEL_KEY = re.compile(r"\b(?P<page>\d{3})-(?P<panel>\d{2})\b")
FENCE = re.compile(r"^\s*```")
CODE_SPAN = re.compile(r"`[^`]+`")


def code_ranges(line: str) -> list[tuple[int, int]]:
    """Inline code quotes a form rather than pointing at a panel, like a fenced block."""
    return [(match.start(), match.end()) for match in CODE_SPAN.finditer(line)]


def in_code(position: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= position < end for start, end in ranges)

LOCAL, CROSS, KEY, EXAMPLE, AMBIGUOUS = "local", "cross", "key", "example", "ambiguous"


@dataclass(frozen=True)
class Site:
    path: str
    line: int
    kind: str
    page: int | None       # the page whose panels the reference names
    panels: tuple[int, ...]
    text: str


def page_scope(relative: str) -> int | None:
    """The page a bare panel reference in this file belongs to, if any."""
    match = re.match(r"^content/pages/(\d{3})\.md$", relative)
    if match:
        return int(match.group(1))
    match = re.match(r"^prompts/pages/(\d{3})/", relative)
    return int(match.group(1)) if match else None


def scan_prose(text: str, relative: str) -> list[Site]:
    """Classify every panel reference in one file. Headings are structured, so skipped."""
    scope = page_scope(relative)
    sites: list[Site] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if line.startswith("## "):
            continue
        quoted = code_ranges(line)
        for match in PANEL_KEY.finditer(line):
            example = fenced or in_code(match.start(), quoted)
            sites.append(Site(relative, number, EXAMPLE if example else KEY,
                              int(match.group("page")), (int(match.group("panel")),),
                              match.group(0)))
        for match in PANEL_PHRASE.finditer(line):
            panels = tuple(int(item) for item in re.findall(r"\d{1,2}", match.group(0)[
                len(match.group("page") or ""):]))
            if fenced or in_code(match.start(), quoted):
                kind, page = EXAMPLE, None
            elif match.group("page"):
                raw = match.group("pagenum")
                kind = CROSS if len(raw) == 3 else AMBIGUOUS
                page = int(raw)
            elif scope is not None:
                kind, page = LOCAL, scope
            else:
                kind, page = AMBIGUOUS, None
            sites.append(Site(relative, number, kind, page, panels, match.group(0).strip()))
    return sites


def prose_files() -> list[Path]:
    paths: list[Path] = []
    for pattern in PROSE_GLOBS:
        paths.extend(ROOT.glob(pattern))
    return sorted(
        path
        for path in dict.fromkeys(paths)
        if path.is_file() and str(path.relative_to(ROOT)) not in HISTORICAL
    )


def read_sites() -> list[Site]:
    return [
        site
        for path in prose_files()
        for site in scan_prose(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)))
    ]


class Relocation:
    """Where every (page, panel) pair an operation touches ends up.

    One table answers every rewriting question, including the cross-page ones: a panel that
    changes index, a panel that changes page, and a panel that leaves the book all look the
    same to a caller. A pair on a page the operation does not touch resolves to itself.
    """

    def __init__(self, operation: Operation) -> None:
        self.pages = {change.page for change in operation.changes}
        self.moves: dict[tuple[int, int], tuple[int, int] | None] = {}
        for change in operation.changes:
            for old, new in change.mapping.items():
                self.moves[(change.page, old)] = (change.page, new)
            for old in change.deleted:
                self.moves[(change.page, old)] = None
        transfer = operation.transfer
        if transfer is not None:
            landing = operation.change(transfer.target)
            assert landing is not None and landing.arrived is not None
            self.moves[(transfer.source, transfer.index)] = (transfer.target, landing.arrived)

    def resolve(self, page: int, index: int) -> tuple[int, int] | None:
        """The pair afterwards, or ``None`` if that panel no longer exists."""
        if (page, index) in self.moves:
            return self.moves[(page, index)]
        if page in self.pages:
            return None
        return (page, index)


def relocated(relocation: Relocation):
    """A ``PANEL_KEY`` substitution that moves every key it finds, and drops nothing."""
    def replace(hit: re.Match[str]) -> str:
        landing = relocation.resolve(int(hit.group("page")), int(hit.group("panel")))
        if landing is None:
            return hit.group(0)
        return f"{landing[0]:03d}-{landing[1]:02d}"
    return replace


@dataclass
class Rewrite:
    text: str
    dangling: list[tuple[int, str]] = field(default_factory=list)
    split: list[str] = field(default_factory=list)
    circular: list[str] = field(default_factory=list)


def rewrite_prose(text: str, relative: str, relocation: Relocation, *,
                  origin: int | None = None, lands_on: int | None = None) -> Rewrite:
    """Apply a relocation to every panel reference in one file.

    ``origin`` is the page a bare reference in this text was written against, and
    ``lands_on`` the page the text will belong to afterwards. They differ only when the text
    itself is moving between pages -- a transferred panel's script, or its prompt file --
    and that is exactly when a bare reference has to become an explicit one, because the
    page it was implicitly naming is no longer the page it sits on.
    """
    scope = page_scope(relative) if origin is None else origin
    settles = scope if lands_on is None else lands_on
    result = Rewrite("")
    lines = text.splitlines(keepends=True)
    fenced = False
    for position, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or line.startswith("## "):
            continue
        quoted = code_ranges(line)

        def key(match: re.Match[str]) -> str:
            if in_code(match.start(), quoted):
                return match.group(0)
            pair = relocation.resolve(int(match.group("page")), int(match.group("panel")))
            if pair is None:
                result.dangling.append((int(match.group("panel")), match.group(0)))
                return match.group(0)
            return f"{pair[0]:03d}-{pair[1]:02d}"

        def phrase(match: re.Match[str]) -> str:
            if in_code(match.start(), quoted):
                return match.group(0)
            raw = match.group("pagenum")
            if raw is not None and len(raw) != 3:
                return match.group(0)
            named = int(raw) if raw is not None else scope
            if named is None:
                return match.group(0)
            prefix = match.group("page") or ""
            body = match.group(0)[len(prefix):]
            numbers = [int(item) for item in re.findall(r"\d{1,2}", body)]
            pairs = [relocation.resolve(named, value) for value in numbers]
            for value, pair in zip(numbers, pairs):
                if pair is None:
                    result.dangling.append((value, match.group(0).strip()))
                    return match.group(0)
            landed = {pair[0] for pair in pairs if pair is not None}
            # `panels 3–6` names four panels and writes two, so the endpoints are not the
            # whole reference. A transfer that takes one from inside the span breaks the
            # range just as surely as one that takes an end of it.
            if len(numbers) == 2 and re.search(r"\d\s*[–—-]\s*\d", body):
                for value in range(min(numbers), max(numbers) + 1):
                    inside = relocation.resolve(named, value)
                    if inside is not None:
                        landed.add(inside[0])
            if len(landed) > 1:
                # `panels 3–6` where the move takes some of them elsewhere. A range that no
                # longer names one page is not a renumbering; it is a sentence to rewrite.
                result.split.append(match.group(0).strip())
                return match.group(0)
            page = landed.pop()
            remaining = iter(pair[1] for pair in pairs if pair is not None)

            def number(hit: re.Match[str]) -> str:
                # `Panel 02` is padded and `panel 2` is not; keep whichever this site used.
                return f"{next(remaining):0{len(hit.group(0))}d}"

            renumbered = re.sub(r"\d{1,2}", number, body)
            if raw is not None:
                if page == named:
                    return prefix + renumbered
                if page == settles:
                    # `Repeat page 003 panel 4` on a page that has just been given that
                    # panel. Still true, and still worth a human's eye: an instruction to
                    # repeat a composition now points at the page it sits on.
                    result.circular.append(match.group(0).strip())
                return re.sub(r"\d{1,3}", f"{page:03d}", prefix, count=1) + renumbered
            if page == settles:
                return renumbered
            # The panel this bare reference names is no longer on the page the sentence
            # sits on, so the sentence has to say which page it means.
            lead = "Page" if renumbered[:1].isupper() else "page"
            return f"{lead} {page:03d} " + renumbered[:1].lower() + renumbered[1:]

        lines[position] = PANEL_PHRASE.sub(phrase, PANEL_KEY.sub(key, line))
    result.text = "".join(lines)
    return result


# ---------------------------------------------------------------------------
# operations
# ---------------------------------------------------------------------------

# A panel arriving from another page occupies a slot in the target's order before it has an
# index there. Negative sentinels distinguish the two kinds of arrival: a panel written fresh
# by `insert`, and a panel carried in by a cross-page `move`.
ARRIVAL = -100


@dataclass(frozen=True)
class PageChange:
    """What one page looks like afterwards. An operation changes one page, or two."""

    page: int
    order: list[int]                 # old index of each panel, in the new order
    created: tuple[int, ...]         # sentinels for panels written fresh
    deleted: tuple[int, ...]         # indices removed from the book
    departed: tuple[int, ...]        # indices that left for another page

    @property
    def id(self) -> str:
        return f"{self.page:03d}"

    @property
    def mapping(self) -> dict[int, int]:
        return {old: position for position, old in enumerate(self.order, 1) if old > 0}

    @property
    def shifted(self) -> dict[int, int]:
        return {old: new for old, new in self.mapping.items() if old != new}

    @property
    def arrived(self) -> int | None:
        return next((position for position, old in enumerate(self.order, 1)
                     if old == ARRIVAL), None)

    @property
    def gone(self) -> tuple[int, ...]:
        """Indices this page no longer has, whichever way they left."""
        return tuple(sorted(self.deleted + self.departed))


@dataclass(frozen=True)
class Transfer:
    """One panel carried from one page to another, keeping its script and its art."""

    source: int
    index: int
    target: int
    position: int

    @property
    def from_key(self) -> str:
        return f"{self.source:03d}-{self.index:02d}"

    @property
    def to_key(self) -> str:
        return f"{self.target:03d}-{self.position:02d}"


@dataclass(frozen=True)
class Operation:
    label: str
    changes: tuple[PageChange, ...]
    transfer: Transfer | None = None

    @property
    def pages(self) -> tuple[int, ...]:
        return tuple(change.page for change in self.changes)

    def change(self, page: int) -> PageChange | None:
        return next((item for item in self.changes if item.page == page), None)


def build_insert(script: PageScript, at: int, count: int) -> Operation:
    order = list(script.indices)
    created = tuple(-(n + 1) for n in range(count))
    order[at - 1:at - 1] = list(created)
    return Operation(f"insert {count} panel(s) at {script.id}-{at:02d}",
                     (PageChange(script.number, order, created, (), ()),))


def build_delete(script: PageScript, indices: list[int]) -> Operation:
    order = [index for index in script.indices if index not in indices]
    return Operation(
        "delete " + ", ".join(f"{script.id}-{index:02d}" for index in sorted(indices)),
        (PageChange(script.number, order, (), tuple(sorted(indices)), ()),),
    )


def build_move(script: PageScript, index: int, destination: int) -> Operation:
    order = [value for value in script.indices if value != index]
    order.insert(destination - 1, index)
    return Operation(f"move {script.id}-{index:02d} to position {destination:02d}",
                     (PageChange(script.number, order, (), (), ()),))


def build_transfer(source: PageScript, index: int,
                   target: PageScript, position: int) -> Operation:
    """Move a panel to another page: one page loses a beat, another gains it."""
    leaving = [value for value in source.indices if value != index]
    arriving = list(target.indices)
    arriving[position - 1:position - 1] = [ARRIVAL]
    transfer = Transfer(source.number, index, target.number, position)
    return Operation(
        f"move {transfer.from_key} to {target.id} as panel {position:02d}",
        (
            PageChange(source.number, leaving, (), (), (index,)),
            PageChange(target.number, arriving, (), (), ()),
        ),
        transfer,
    )


# ---------------------------------------------------------------------------
# impact
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Note:
    severity: str
    kind: str
    subject: str
    message: str


SEVERITIES = ("error", "warning", "note")


def band_of(count: int) -> str:
    if count == 9:
        return "nine-panel grid, reserved for convergence, scale, or repeated attempts"
    if DEFAULT_BAND[0] <= count <= DEFAULT_BAND[1]:
        return "default"
    if count < DEFAULT_BAND[0]:
        return "establishing or revelation"
    return "procedural sequence"


def rhythm_notes(script: PageScript, change: PageChange) -> list[Note]:
    """The page's new rhythm, measured against design/page-grammar.md. Never repaired."""
    notes: list[Note] = []
    count = len(change.order)
    if not GRAMMAR_BAND[0] <= count <= GRAMMAR_BAND[1]:
        notes.append(Note("error", "rhythm-out-of-grammar", script.path,
                          f"would carry {count} panels, and the page grammar bands a page "
                          f"at {GRAMMAR_BAND[0]}–{GRAMMAR_BAND[1]}"))
        return notes
    if not DEFAULT_BAND[0] <= count <= DEFAULT_BAND[1]:
        notes.append(Note("warning", "rhythm-off-default", script.path,
                          f"moves from {script.count} to {count} panels, which reads as a "
                          f"{band_of(count)} page rather than the {DEFAULT_BAND[0]}–"
                          f"{DEFAULT_BAND[1]} default"))
    return notes


def lettering_notes(script: PageScript, change: PageChange,
                    incoming: Section | None) -> list[Note]:
    """Lettering does not move with a panel index, so say what changed shape."""
    notes: list[Note] = []
    bodies = {section.index: section for section in script.sections}
    for old in change.deleted:
        section = bodies[old]
        if section.elements:
            notes.append(Note("warning", "lettering-deleted",
                              f"{change.id}-{old:02d}",
                              f"carries {section.elements} lettered element(s) and "
                              f"{section.words} words, which the deletion removes from the book"))
    for old, new in sorted(change.mapping.items()):
        section = bodies[old]
        if section.elements > SLOTS_PER_PANEL:
            notes.append(Note("warning", "lettering-overflow",
                              f"{change.id}-{new:02d}",
                              f"carries {section.elements} lettered elements and the slot "
                              f"convention anchors {SLOTS_PER_PANEL}"))
    remaining = sum(bodies[old].words for old in change.mapping)
    if incoming is not None:
        remaining += incoming.words
        if incoming.elements > SLOTS_PER_PANEL:
            notes.append(Note("warning", "lettering-overflow",
                              f"{change.id}-{change.arrived:02d}",
                              f"arrives carrying {incoming.elements} lettered elements and "
                              f"the slot convention anchors {SLOTS_PER_PANEL}"))
    if remaining > DENSE_PAGE_WORDS:
        notes.append(Note("warning", "lettering-dense", script.path,
                          f"keeps {remaining} lettered words, over the {DENSE_PAGE_WORDS} "
                          "density line the thumbnail wall flags"))
    return notes


def art_notes(script: PageScript, change: PageChange) -> list[Note]:
    notes: list[Note] = []
    for old in change.deleted:
        if art_directory(change.page, old).is_dir() or art_rows(change.page, old):
            notes.append(Note("error", "orphaned-art", f"{change.id}-{old:02d}",
                              "has generated art, which the deletion discards"))
    for old, new in sorted(change.shifted.items()):
        if art_directory(change.page, old).is_dir():
            notes.append(Note("note", "art-renamed", f"{change.id}-{old:02d}",
                              f"art moves to {change.id}-{new:02d}; the image was drawn for "
                              "the old beat and should be re-reviewed against the new one"))
    return notes


def transfer_notes(scripts: dict[int, PageScript], operation: Operation) -> list[Note]:
    """A panel that changes page changes more than its number."""
    transfer = operation.transfer
    if transfer is None:
        return []
    notes: list[Note] = []
    source, target = scripts[transfer.source], scripts[transfer.target]
    if art_directory(transfer.source, transfer.index).is_dir():
        notes.append(Note("note", "art-transferred", transfer.from_key,
                          f"art moves to {transfer.to_key}, onto a page it was not composed "
                          "for; re-review it against the new neighbours"))
    section = next(item for item in source.sections if item.index == transfer.index)
    provenance = re.findall(r"^\*\*Provenance:\*\*.*$", section.body, re.MULTILINE)
    if provenance:
        notes.append(Note("note", "provenance-transferred", transfer.to_key,
                          "carries its own provenance line onto a page whose front matter "
                          "may not declare those sources; crossref will say so"))
    source_chapter = front_matter_value(source, "chapter")
    target_chapter = front_matter_value(target, "chapter")
    if source_chapter != target_chapter:
        notes.append(Note("warning", "transfer-crosses-chapter", transfer.from_key,
                          f"leaves chapter {source_chapter} for chapter {target_chapter}; "
                          "the beat changes which chapter's argument it serves"))
    return notes


def front_matter_value(script: PageScript, field_name: str) -> str:
    metadata = crossref.front_matter(script.text) or ""
    match = re.search(rf'^{field_name}:\s*"?([^"\n]+)"?\s*$', metadata, re.MULTILINE)
    return match.group(1).strip() if match else ""


def art_directory(page: int, index: int) -> Path:
    return ROOT / "assets" / "art" / "panels" / f"{page:03d}-{index:02d}"


def art_rows(page: int, index: int) -> list[str]:
    path = ROOT / "data" / "panel-art.tsv"
    if not path.exists():
        return []
    prefix = f"{page:03d}-{index:02d}\t"
    return [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith(prefix)]


def structure_notes(scripts: dict[int, PageScript]) -> list[Note]:
    notes: list[Note] = []
    for number, script in sorted(scripts.items()):
        if script.grouped and script.sections:
            notes.append(Note("error", "panel-headings-mixed", script.path,
                              "declares both a grouped run and individual panel headings"))
        if not script.sections and not script.grouped:
            notes.append(Note("error", "panel-headings-missing", script.path,
                              "declares no panels"))
        if script.sections and list(script.indices) != list(range(1, len(script.sections) + 1)):
            notes.append(Note("error", "panel-headings-unordered", script.path,
                              "does not number its panels 1..N in order: "
                              + ", ".join(str(index) for index in script.indices)))
    return notes


def slot_keys(scripts: dict[int, PageScript]) -> list[str]:
    """The image slots the viewer and the classifier expose: one per panel, one per group."""
    keys: list[str] = []
    for number, script in sorted(scripts.items()):
        if script.sections:
            keys.extend(f"{number:03d}-{index:02d}" for index in script.indices)
        elif script.grouped:
            keys.append(f"{number:03d}-01")
    return keys


def joined_notes(scripts: dict[int, PageScript]) -> list[Note]:
    """Every structured panel key must name a panel some page script actually declares."""
    notes: list[Note] = []
    known = set(slot_keys(scripts))
    for relative, keys in structured_keys().items():
        for key in sorted(keys):
            if key not in known:
                notes.append(Note("error", "panel-key-dangling", f"{relative}: {key}",
                                  "names a panel no page script declares"))
    generated = ROOT / "data" / "panel-types.tsv"
    if generated.exists():
        rows = generated.read_text(encoding="utf-8").splitlines()[1:]
        table = [row.split("\t")[0] for row in rows if row.strip()]
        if table != slot_keys(scripts):
            notes.append(Note("error", "panel-types-stale", "data/panel-types.tsv",
                              f"lists {len(table)} slots and the page scripts declare "
                              f"{len(known)}; re-run scripts/paneltypes.py write"))
    return notes


def structured_keys() -> dict[str, set[str]]:
    """Panel keys held outside prose: the art table, the art tree, the prompt tree."""
    found: dict[str, set[str]] = {}
    art = ROOT / "data" / "panel-art.tsv"
    if art.exists():
        found["data/panel-art.tsv"] = {
            row.split("\t")[0]
            for row in art.read_text(encoding="utf-8").splitlines()[1:]
            if row.strip()
        }
    directory = ROOT / "assets" / "art" / "panels"
    if directory.is_dir():
        found["assets/art/panels"] = {
            child.name for child in directory.iterdir()
            if re.fullmatch(r"\d{3}-\d{2}", child.name)
        }
    prompts: set[str] = set()
    base = ROOT / "prompts" / "pages"
    if base.is_dir():
        for page_dir in base.iterdir():
            if not re.fullmatch(r"\d{3}", page_dir.name):
                continue
            for child in page_dir.glob("panel-[0-9][0-9].md"):
                prompts.add(f"{page_dir.name}-{child.stem.split('-')[1]}")
    if prompts:
        found["prompts/pages"] = prompts
    return found


def reference_notes(sites: list[Site], scripts: dict[int, PageScript]) -> list[Note]:
    notes: list[Note] = []
    for site in sites:
        if site.kind == AMBIGUOUS:
            notes.append(Note("warning", "ambiguous-panel-reference", f"{site.path}:{site.line}",
                              f"“{site.text}” names no page, and the file is not scoped to "
                              "one, so it is never rewritten"))
            continue
        if site.kind not in (LOCAL, CROSS, KEY):
            continue
        script = scripts.get(site.page or 0)
        if script is None:
            notes.append(Note("error", "dangling-panel-reference", f"{site.path}:{site.line}",
                              f"“{site.text}” names page {site.page:03d}, which does not exist"))
            continue
        missing = sorted(value for value in site.panels if not 1 <= value <= script.count)
        if missing:
            notes.append(Note("error", "dangling-panel-reference", f"{site.path}:{site.line}",
                              f"“{site.text}” names panel "
                              + ", ".join(str(value) for value in missing)
                              + f", and page {script.id} has {script.count}"))
    return notes


# ---------------------------------------------------------------------------
# rewriting
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    writes: dict[str, str] = field(default_factory=dict)
    removals: list[str] = field(default_factory=list)      # files
    discards: list[str] = field(default_factory=list)      # directories
    renames: list[tuple[str, str]] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)


NEW_PANEL_BODY = (
    "\n"
    "**Frame:** [Shot, angle, environment, actors or system surfaces, visible state.]\n"
    "\n"
    "**Action:** [Only what changes during the panel.]\n"
    "\n"
    "**Provenance:** `invented` — `NONE-FICTION`; placeholder for an unwritten panel.\n"
    "\n"
)


def plan_rewrite(scripts: dict[int, PageScript], operation: Operation) -> Plan:
    plan = Plan()
    relocation = Relocation(operation)
    transfer = operation.transfer

    def report(rewrite: Rewrite, relative: str) -> None:
        for value, snippet in rewrite.dangling:
            plan.notes.append(Note("error", "dangling-panel-reference", relative,
                                   f"“{snippet}” names panel {value}, which is being deleted"))
        for snippet in rewrite.split:
            plan.notes.append(Note("error", "reference-split-by-move", relative,
                                   f"“{snippet}” names panels that no longer share a page; "
                                   "a range is not a renumbering, so it is left for a human"))
        for snippet in rewrite.circular:
            plan.notes.append(Note("warning", "reference-now-self", relative,
                                   f"“{snippet}” now names a panel on the page it sits on; "
                                   "the reference is true but probably wants rewriting"))

    # --- what a departing or deleted panel takes with it ----------------------
    # A vacated index must not leave its art directory behind: the panel after it is about to
    # be renamed onto that name. A deletion discards it, a transfer carries it to the other
    # page, and either way it is in the plan rather than left to chance.
    doomed: set[str] = set()
    for change in operation.changes:
        for old in change.deleted:
            relative = f"prompts/pages/{change.id}/panel-{old:02d}.md"
            if (ROOT / relative).exists():
                plan.removals.append(relative)
                doomed.add(relative)
            if art_directory(change.page, old).is_dir():
                plan.discards.append(f"assets/art/panels/{change.id}-{old:02d}")

    # --- the page scripts ----------------------------------------------------
    carried = ""
    if transfer is not None:
        section = next(item for item in scripts[transfer.source].sections
                       if item.index == transfer.index)
        # The body is leaving the page its bare references were written against, so those
        # references are qualified with the page they came from before they travel.
        carried = rewrite_prose(section.body, scripts[transfer.source].path, relocation,
                                origin=transfer.source, lands_on=transfer.target).text

    for change in operation.changes:
        script = scripts[change.page]
        bodies = {old: NEW_PANEL_BODY for old in change.created}
        if change.arrived is not None:
            bodies[ARRIVAL] = carried
        text = script.compose(change.order, bodies)
        rewrite = rewrite_prose(text, script.path, relocation)
        report(rewrite, script.path)
        plan.writes[script.path] = rewrite.text

    # --- every other file that can name a panel on either page ----------------
    written = {scripts[change.page].path for change in operation.changes}
    for path in prose_files():
        relative = str(path.relative_to(ROOT))
        if relative in written or relative in doomed:
            continue
        body = path.read_text(encoding="utf-8")
        # A prompt file belonging to the transferred panel travels with it, so its bare
        # references are qualified for the same reason the panel body's are.
        travelling = (
            transfer is not None
            and relative == f"prompts/pages/{transfer.source:03d}/panel-{transfer.index:02d}.md"
        )
        rewrite = rewrite_prose(
            body, relative, relocation,
            origin=transfer.source if travelling else None,
            lands_on=transfer.target if travelling else None,
        )
        report(rewrite, relative)
        if rewrite.text != body:
            plan.writes[relative] = rewrite.text

    # --- the art table -------------------------------------------------------
    art = ROOT / "data" / "panel-art.tsv"
    if art.exists():
        kept: list[str] = []
        for row in art.read_text(encoding="utf-8").splitlines(keepends=True):
            match = re.match(r"^(\d{3})-(\d{2})\t", row)
            if not match:
                kept.append(row)
                continue
            pair = relocation.resolve(int(match.group(1)), int(match.group(2)))
            if pair is None:
                continue
            # Every key in the row, not just the one in the first column: the `file` column
            # holds `assets/art/panels/NNN-II/...`, and a key that agrees with a path that
            # does not is worse than either being wrong, because the art silently stops
            # resolving and the build simply letters fewer panels.
            kept.append(PANEL_KEY.sub(relocated(relocation), row))
        plan.writes["data/panel-art.tsv"] = "".join(kept)

    # --- the art tree and the prompt tree ------------------------------------
    art_base = ROOT / "assets" / "art" / "panels"
    if art_base.is_dir():
        for child in sorted(art_base.iterdir()):
            match = re.fullmatch(r"(\d{3})-(\d{2})", child.name)
            if not match:
                continue
            page, index = int(match.group(1)), int(match.group(2))
            pair = relocation.resolve(page, index)
            if pair is None:
                plan.notes.append(Note("note", "discarded", f"assets/art/panels/{child.name}",
                                       "belongs to a deleted panel and is removed, because "
                                       "the panel after it is renamed onto this name"))
                continue
            if pair != (page, index):
                plan.renames.append((f"assets/art/panels/{child.name}",
                                     f"assets/art/panels/{pair[0]:03d}-{pair[1]:02d}"))

    prompt_base = ROOT / "prompts" / "pages"
    if prompt_base.is_dir():
        for page_dir in sorted(prompt_base.iterdir()):
            if not re.fullmatch(r"\d{3}", page_dir.name):
                continue
            page = int(page_dir.name)
            for child in sorted(page_dir.glob("panel-[0-9][0-9].md")):
                index = int(child.stem.split("-")[1])
                pair = relocation.resolve(page, index)
                if pair is None or pair == (page, index):
                    continue
                plan.renames.append((
                    f"prompts/pages/{page:03d}/{child.name}",
                    f"prompts/pages/{pair[0]:03d}/panel-{pair[1]:02d}.md",
                ))

    # A renamed file's rewritten content belongs at its destination, not at the name it is
    # about to vacate. Remapped in one pass, because a move is usually a permutation and
    # popping keys one at a time would let one file's content land on another's.
    moves = dict(plan.renames)
    plan.writes = {moves.get(relative, relative): text
                   for relative, text in plan.writes.items()}

    # `prompts/pages/NNN/panel-II.md` names its own panel in a `# Page NNN — Panel II`
    # heading. That is an ordinary cross-page reference and the prose pass above already
    # rewrote it, padding included; only the filename needed a rename.

    # --- historical records --------------------------------------------------
    for relative in HISTORICAL:
        path = ROOT / relative
        if not path.exists():
            continue
        touched = {
            match.group(0)
            for match in PANEL_KEY.finditer(path.read_text(encoding="utf-8"))
            if relocation.resolve(int(match.group("page")), int(match.group("panel")))
            not in (None, (int(match.group("page")), int(match.group("panel"))))
        }
        if touched:
            plan.notes.append(Note("note", "historical-record", relative,
                                   "names " + ", ".join(sorted(touched))
                                   + " and is a dated record, so it is not rewritten"))
    return plan


def drop_unchanged(plan: Plan) -> Plan:
    plan.writes = {
        relative: text
        for relative, text in plan.writes.items()
        if not (ROOT / relative).exists() or (ROOT / relative).read_text(encoding="utf-8") != text
    }
    return plan


def commit(plan: Plan) -> None:
    """Stage renames outside the tree first, so a swap never collides with itself.

    Renames land before writes, never after: a renamed prose file is written under its
    destination name, and unstaging it afterwards would put the original content back.
    """
    staging = ROOT / ".panels-staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    try:
        for index, (source, _) in enumerate(plan.renames):
            shutil.move(str(ROOT / source), str(staging / str(index)))
        for relative in plan.removals:
            path = ROOT / relative
            if path.exists():
                path.unlink()
        for relative in plan.discards:
            shutil.rmtree(ROOT / relative, ignore_errors=True)
        for index, (_, destination) in enumerate(plan.renames):
            target = ROOT / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(staging / str(index)), str(target))
        for relative, text in sorted(plan.writes.items()):
            path = ROOT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def print_notes(notes: list[Note]) -> dict[str, int]:
    counts = {level: 0 for level in SEVERITIES}
    for level in SEVERITIES:
        items = [note for note in notes if note.severity == level]
        counts[level] = len(items)
        if not items:
            continue
        print(f"\n{level.title()}s:")
        for note in items:
            print(f"- [{note.kind}] {note.subject}: {note.message}")
    return counts


def audit(scripts: dict[int, PageScript], sites: list[Site]) -> list[Note]:
    return (
        structure_notes(scripts)
        + joined_notes(scripts)
        + reference_notes(sites, scripts)
    )


def cmd_report(scripts: dict[int, PageScript], sites: list[Site]) -> int:
    slots = slot_keys(scripts)
    scripted = sum(script.count for script in scripts.values())
    histogram: dict[int, int] = {}
    for script in scripts.values():
        histogram[script.count] = histogram.get(script.count, 0) + 1
    print(f"{scripted} scripted panels across {len(scripts)} pages, exposed as "
          f"{len(slots)} image slots.")

    print("\nRhythm")
    for count in sorted(histogram):
        pages = histogram[count]
        print(f"  {count:>2} panels  {pages:>3} pages  {band_of(count)}")
    grouped = sorted(script.id for script in scripts.values() if script.grouped)
    if grouped:
        print(f"  grouped runs, not operated on: {', '.join(grouped)}")

    print("\nLettering load")
    individual = sum(section.elements
                     for script in scripts.values() for section in script.sections)
    # A grouped run carries captions that span its panels, which the slot convention treats
    # as ordinary captions on the first panel of the run. They are counted, not slotted.
    spanning = sum(
        1
        for script in scripts.values() if not script.sections
        for line in script.text.splitlines() if line.startswith(VISIBLE_HEADERS)
    )
    overflow = [
        f"{script.id}-{section.index:02d}"
        for script in scripts.values() for section in script.sections
        if section.elements > SLOTS_PER_PANEL
    ]
    dense = sorted(script.id for script in scripts.values() if script.words > DENSE_PAGE_WORDS)
    print(f"  {individual + spanning} lettered elements ({individual} on individually "
          f"scripted panels, {spanning} spanning a grouped run)")
    print(f"  {SLOTS_PER_PANEL} anchored slots per panel, {len(overflow)} panels over")
    print(f"  {sum(script.words for script in scripts.values())} lettered words, "
          f"{len(dense)} pages over the {DENSE_PAGE_WORDS}-word density line")

    print("\nStructured panel keys")
    for relative, keys in sorted(structured_keys().items()):
        print(f"  {relative:<22} {len(keys):>4}")

    print("\nPanel references in prose")
    census: dict[str, int] = {}
    for site in sites:
        census[site.kind] = census.get(site.kind, 0) + 1
    for kind in (LOCAL, CROSS, KEY, EXAMPLE, AMBIGUOUS):
        print(f"  {kind:<10} {census.get(kind, 0):>4}")

    print(f"\nDerived, not rewritten: {', '.join(GENERATED)}")
    print(f"Historical records not rewritten: {', '.join(HISTORICAL)}")
    return 0


def cmd_check(scripts: dict[int, PageScript], sites: list[Site], strict: bool) -> int:
    notes = audit(scripts, sites)
    counts = print_notes(notes)
    blocking = counts["error"] + (counts["warning"] if strict else 0)
    if blocking:
        print(f"\nPanel check failed: {blocking} blocking findings.")
        return 1
    print(f"\nPanel check passed: {sum(script.count for script in scripts.values())} panels "
          f"on {len(scripts)} pages, {len(slot_keys(scripts))} image slots.")
    return 0


def run_operation(scripts: dict[int, PageScript], operation: Operation,
                  args: argparse.Namespace) -> int:
    transfer = operation.transfer
    print(f"Operation: {operation.label}")
    for change in operation.changes:
        script = scripts[change.page]
        count = len(change.order)
        print(f"Rhythm: page {change.id} {script.count} -> {count} panels ({band_of(count)})")

    if transfer is not None:
        print(f"\nTransfer\n  {transfer.from_key} -> {transfer.to_key}")
    for change in operation.changes:
        if change.shifted or change.created or change.gone:
            print(f"\nPanel map, page {change.id}")
        for old, new in sorted(change.shifted.items()):
            print(f"  {change.id}-{old:02d} -> {change.id}-{new:02d}")
        for position, old in enumerate(change.order, 1):
            if old in change.created:
                print(f"  new  {change.id}-{position:02d}")
        for old in change.deleted:
            print(f"  gone {change.id}-{old:02d}")
        for old in change.departed:
            print(f"  left {change.id}-{old:02d}")

    notes: list[Note] = []
    for change in operation.changes:
        script = scripts[change.page]
        incoming = None
        if transfer is not None and change.page == transfer.target:
            incoming = next(item for item in scripts[transfer.source].sections
                            if item.index == transfer.index)
        notes += (rhythm_notes(script, change)
                  + lettering_notes(script, change, incoming)
                  + art_notes(script, change))
    notes += transfer_notes(scripts, operation)
    plan = drop_unchanged(plan_rewrite(scripts, operation))
    notes += plan.notes
    counts = print_notes(notes)

    print(f"\nFiles: {len(plan.writes)} written, "
          f"{len(plan.removals) + len(plan.discards)} removed, {len(plan.renames)} renamed")

    # Rhythm is to a panel what parity is to a page: legal to break, expensive, and never
    # broken by accident. The price is the printed work list, not a refusal.
    rhythm_break = [note for note in notes
                    if note.kind in ("rhythm-off-default", "rhythm-out-of-grammar")]
    if rhythm_break and not args.allow_rhythm_shift:
        pages = ", ".join(sorted({note.subject.split("/")[-1][:3] for note in rhythm_break}))
        print(f"\nRefused: this operation leaves page {pages} outside the "
              f"{DEFAULT_BAND[0]}–{DEFAULT_BAND[1]} default in design/page-grammar.md. "
              "Re-run with --allow-rhythm-shift to take it deliberately.")
        return 1
    split = [note for note in notes if note.kind == "reference-split-by-move"]
    if split:
        print("\nRefused: a sentence names a range of panels the move would break apart. "
              "Rewrite it first; the tool will not guess at a range.")
        return 1
    art_loss = [note for note in notes if note.kind == "orphaned-art"]
    if art_loss and not args.allow_art_loss:
        print("\nRefused: this operation discards generated art. The findings above are the "
              "work list. Re-run with --allow-art-loss to take it deliberately.")
        return 1
    if not args.apply:
        print("\nPlan only. Re-run with --apply to write it.")
        return 0

    commit(plan)
    print("\nApplied. Regenerate the derived artifacts, then re-check:")
    print("  python3 scripts/paneltypes.py write")
    print("  python3 scripts/build-site.py")
    print("  python3 scripts/panels.py check")
    open_findings = counts["error"] + counts["warning"]
    if open_findings:
        noun = "finding remains" if open_findings == 1 else "findings remain"
        print(f"\n{open_findings} {noun} open. Rhythm, lettering, and a prompt that "
              "still names a deleted panel are editorial, not mechanical.")
    return 0


def parse_key(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d{3})-(\d{2})", value)
    if not match:
        raise argparse.ArgumentTypeError(f"{value!r} is not a NNN-II panel key")
    return int(match.group(1)), int(match.group(2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="panel census, rhythm map, lettering load, references")
    check = commands.add_parser("check", help="exit non-zero while the tree disagrees with itself")
    check.add_argument("--strict", action="store_true", help="also fail on warnings")

    for name, help_text in (
        ("insert", "add panels before a position on one page"),
        ("delete", "remove panels from one page"),
        ("move", "move one panel to another position, on its page or another"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--apply", action="store_true", help="write the plan")
        command.add_argument("--allow-art-loss", action="store_true",
                             help="permit discarding art belonging to a deleted panel")
        command.add_argument("--allow-rhythm-shift", action="store_true",
                             help="permit an operation that leaves the default panel band")
        if name == "insert":
            command.add_argument("--page", required=True, type=int, metavar="NNN")
            command.add_argument("--at", required=True, type=int, metavar="II")
            command.add_argument("--count", type=int, default=1)
        elif name == "delete":
            command.add_argument("panels", nargs="+", type=parse_key, metavar="NNN-II")
        else:
            command.add_argument("panel", type=parse_key, metavar="NNN-II")
            command.add_argument("--to", required=True, type=int, metavar="II",
                                 help="the index the panel carries afterwards")
            command.add_argument("--to-page", type=int, default=0, metavar="NNN",
                                 help="move it to another page (default: stay on its own)")

    args = parser.parse_args(argv)
    scripts = read_scripts()
    sites = read_sites()

    if args.command == "report":
        return cmd_report(scripts, sites)
    if args.command == "check":
        return cmd_check(scripts, sites, args.strict)

    target: PageScript | None = None
    if args.command == "insert":
        page, positions = args.page, [args.at]
    elif args.command == "delete":
        pages = {number for number, _ in args.panels}
        if len(pages) != 1:
            print("delete takes panels from one page at a time")
            return 2
        page, positions = pages.pop(), [index for _, index in args.panels]
    else:
        page, index = args.panel
        positions = [index] if args.to_page and args.to_page != page else [index, args.to]

    script = scripts.get(page)
    if script is None:
        print(f"no such page: {page:03d}")
        return 2

    if args.command == "move" and args.to_page and args.to_page != page:
        target = scripts.get(args.to_page)
        if target is None:
            print(f"no such page: {args.to_page:03d}")
            return 2
        if script.count <= 1:
            print(f"page {script.id} has one panel; moving it away would leave the page with "
                  "none. Delete the page with scripts/pagination.py instead.")
            return 2
        if not 1 <= args.to <= target.count + 1:
            print(f"--to {args.to:02d} is outside 01–{target.count + 1:02d} on page "
                  f"{target.id}")
            return 2

    for candidate in (script, target):
        if candidate is not None and candidate.grouped:
            print(f"page {candidate.id} writes its panels as one grouped run, `## Panels "
                  f"{candidate.grouped[0]}–{candidate.grouped[1]}`. That is a single "
                  "composition and a single image slot; splitting it is an editorial "
                  "decision, not a renumbering.")
            return 2

    limit = script.count + (1 if args.command == "insert" else 0)
    outside = sorted(value for value in positions if not 1 <= value <= limit)
    if outside:
        print("outside 01–{:02d}: ".format(limit)
              + ", ".join(f"{value:02d}" for value in outside))
        return 2

    if args.command == "insert":
        if args.count < 1:
            print("--count must be at least 1")
            return 2
        operation = build_insert(script, args.at, args.count)
    elif args.command == "delete":
        missing = sorted(set(positions) - set(script.indices))
        if missing:
            print("no such panel: " + ", ".join(f"{page:03d}-{value:02d}" for value in missing))
            return 2
        if len(positions) >= script.count:
            print(f"deleting {len(positions)} of {script.count} panels would leave page "
                  f"{script.id} with none")
            return 2
        operation = build_delete(script, positions)
    elif target is not None:
        if positions[0] not in script.indices:
            print(f"no such panel: {page:03d}-{positions[0]:02d}")
            return 2
        operation = build_transfer(script, positions[0], target, args.to)
    else:
        operation = build_move(script, positions[0], positions[1])

    return run_operation(scripts, operation, args)


if __name__ == "__main__":
    raise SystemExit(main())
