#!/usr/bin/env python3
"""Insert, delete, and move story pages, and audit the parity choreography they depend on.

Page identity in this repository is the ordinal three-digit page number. That number lives
in filenames, page front matter, three manifests, a beat sheet, eight chapter briefs, the
sequence ledger, panel keys, art directories, and several hundred hand-written sentences.
This module owns every one of those sites, so changing the page set is one deterministic
rewrite rather than a reason to fold a page into its neighbour.

Renumbering is the cheap half. The expensive half is parity. Story page 1 is a recto, so
inserting an odd number of pages swaps recto and verso for every page after the insertion
point, and the script asserts its own parity 89 times, directs art by parity on 71 pages,
and choreographs 21 named beats that depend on which side of the gutter a page lands on --
a reveal across the gutter needs an even-to-odd pair, a turn across the leaf an odd-to-even
one, and an odd insertion turns each into the other. Getting the numbers right
does not repair any of that, and neither does this tool. Parity-inverting operations are
refused unless asked for explicitly, and when they are taken the complete list of
invalidated assertions, turns, and compositions is printed. The reasoning is in
``design/page-identity.md``.

    python3 scripts/pagination.py report
    python3 scripts/pagination.py check
    python3 scripts/pagination.py insert --at 045 --chapter 03 --sequence 16 --title "Title"
    python3 scripts/pagination.py delete 079 --apply
    python3 scripts/pagination.py move 029 --to 030 --apply --allow-parity-shift

Operations print a plan and touch nothing without ``--apply``. ``check`` exits non-zero
while the tree disagrees with itself, so a parity shift taken knowingly cannot be forgotten.
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

# Files whose page numbers are a dated record of something that happened, not a pointer to
# a page. Renumbering them would falsify the record, so they are reported and left alone.
HISTORICAL = (
    "data/generation-log.jsonl",
    "design/page-identity.md",
    "design/panel-identity.md",
)

# Hand-written prose lives here. tasks/ holds briefs about the repository rather than parts
# of it; docs/ and 256t/ are generated or out of scope.
PROSE_GLOBS = (
    "README.md",
    "content/**/*.md",
    "design/**/*.md",
    "research/**/*.md",
    "prompts/**/*.md",
)

# Statements about an ordinal position in the abstract. They stay true whatever moves,
# because they describe the first page rather than a page that happens to be first.
RULE_PATTERNS = (
    re.compile(r"\bpage 1 is (?:an? )?(?:[\w-]+ )*recto", re.IGNORECASE),
)

PARITY = ("verso", "recto")


def parity_of(number: int) -> str:
    return PARITY[number % 2]


# ---------------------------------------------------------------------------
# reference sites in prose
# ---------------------------------------------------------------------------

# A story-page reference always names the keyword. Structured page numbers -- beat rows,
# ledger ranges, `**Pages:** 16-29`, the turn table -- never do, which is what keeps the
# prose rewriter away from tables it has no business editing.
PAGE_PHRASE = re.compile(
    r"(?P<printed>\b(?:printed|Printed|PRINTED)\s+)?"
    r"\b(?P<kw>[Pp]ages?)(?P<sep>\s+|-)"
    r"(?P<first>\d{1,3})"
    r"(?P<rest>(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+|\s*[–—-]\s*)\d{1,3})*)"
)

REFERENCE, FOREIGN, RULE, AMBIGUOUS = "reference", "foreign", "rule", "ambiguous"


@dataclass(frozen=True)
class Site:
    path: str
    line: int
    kind: str
    numbers: tuple[int, ...]
    text: str


def classify(match: re.Match[str], line: str) -> str:
    if match.group("printed"):
        return FOREIGN
    if any(pattern.search(line) for pattern in RULE_PATTERNS):
        return RULE
    digits = re.findall(r"\d{1,3}", match.group(0)[len(match.group("printed") or ""):])
    return REFERENCE if all(len(item) == 3 for item in digits) else AMBIGUOUS


def scan_prose(text: str, relative: str) -> list[Site]:
    sites: list[Site] = []
    for number, line in enumerate(text.splitlines(), 1):
        for match in PAGE_PHRASE.finditer(line):
            body = match.group(0)[len(match.group("printed") or ""):]
            sites.append(
                Site(
                    path=relative,
                    line=number,
                    kind=classify(match, line),
                    numbers=tuple(int(item) for item in re.findall(r"\d{1,3}", body)),
                    text=match.group(0).strip(),
                )
            )
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


def rewrite_prose(text: str, mapping: dict[int, int]) -> tuple[str, list[tuple[int, str]]]:
    """Rewrite padded story-page references. Returns the text and any dangling targets."""
    dangling: list[tuple[int, str]] = []
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        def replace(match: re.Match[str]) -> str:
            if classify(match, line) != REFERENCE:
                return match.group(0)
            prefix = match.group("printed") or ""
            body = match.group(0)[len(prefix):]

            def number(hit: re.Match[str]) -> str:
                value = int(hit.group(0))
                if value not in mapping:
                    dangling.append((value, match.group(0).strip()))
                    return hit.group(0)
                return f"{mapping[value]:03d}"

            return prefix + re.sub(r"\d{3}", number, body)

        lines[index] = PAGE_PHRASE.sub(replace, line)
    return "".join(lines), dangling


# ---------------------------------------------------------------------------
# parity assertions and page-turn choreography
# ---------------------------------------------------------------------------

FRAME_PARITY = re.compile(r"^\*\*Frame:\*\*\s*(Recto|Verso)\b", re.IGNORECASE)
SELF_PARITY = re.compile(r"\bpage\s+(\d{1,3})\s+is\s+(recto|verso)\b", re.IGNORECASE)
OTHER_PARITY = re.compile(r"\b(recto|verso)\s+page\s+(\d{1,3})\b", re.IGNORECASE)
SOFT_CHOREOGRAPHY = re.compile(
    r"page[-\s]turn|turn to page|next (?:recto|verso)|prepares? the .{0,60}?page\s+\d{3}",
    re.IGNORECASE,
)
TURN_ROW = re.compile(r"^\|\s*(\d{3})\s*→\s*(\d{3})\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Assertion:
    path: str
    line: int
    kind: str          # frame (art direction) | note (self) | inline (about another page)
    page: int          # the page whose script carries the claim
    target: int        # the page the claim is about
    claimed: str
    text: str

    @property
    def severity(self) -> str:
        return "error" if self.kind == "frame" else "warning"


FACING, LEAF = "facing", "leaf"

# The audit names its two devices in section headings, because they are checked against
# different arithmetic. See content/story-contract.md, "Physical page assumptions".
TURN_SECTIONS = (
    (re.compile(r"^###\s+Reveals across the gutter\s*$", re.MULTILINE), FACING),
    (re.compile(r"^###\s+Turns across the leaf\s*$", re.MULTILINE), LEAF),
)


@dataclass(frozen=True)
class Turn:
    outgoing: int
    landing: int
    function: str
    device: str = FACING

    @property
    def label(self) -> str:
        return "an even-to-odd facing pair" if self.device == FACING else "an odd-to-even turn"

    def holds(self, outgoing: int, landing: int) -> bool:
        """Is this pair still the device the audit files it under?"""
        parity = 0 if self.device == FACING else 1
        return landing == outgoing + 1 and outgoing % 2 == parity


def read_assertions() -> list[Assertion]:
    found: list[Assertion] = []
    for path in sorted((ROOT / "content" / "pages").glob("[0-9][0-9][0-9].md")):
        page = int(path.stem)
        relative = str(path.relative_to(ROOT))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            frame = FRAME_PARITY.match(line)
            if frame:
                found.append(Assertion(relative, number, "frame", page, page,
                                       frame.group(1).lower(), line.strip()))
            for match in SELF_PARITY.finditer(line):
                found.append(Assertion(relative, number, "note", page, int(match.group(1)),
                                       match.group(2).lower(), line.strip()))
            for match in OTHER_PARITY.finditer(line):
                found.append(Assertion(relative, number, "inline", page, int(match.group(2)),
                                       match.group(1).lower(), line.strip()))
    return found


def read_turns() -> list[Turn]:
    """Read the audit section by section, so each row is checked as the device it claims."""
    text = (ROOT / "content" / "production-review.md").read_text(encoding="utf-8")
    starts = sorted(
        (match.start(), device)
        for pattern, device in TURN_SECTIONS
        for match in pattern.finditer(text)
    )

    def device_at(position: int) -> str:
        current = FACING
        for start, device in starts:
            if start < position:
                current = device
        return current

    return [
        Turn(int(match.group(1)), int(match.group(2)), match.group(3), device_at(match.start()))
        for match in TURN_ROW.finditer(text)
    ]


def read_soft_choreography() -> list[tuple[str, int, int, str]]:
    """Sentences whose meaning depends on a turn, but that assert no checkable parity."""
    found: list[tuple[str, int, int, str]] = []
    for path in sorted((ROOT / "content" / "pages").glob("[0-9][0-9][0-9].md")):
        page = int(path.stem)
        relative = str(path.relative_to(ROOT))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if SOFT_CHOREOGRAPHY.search(line):
                found.append((relative, number, page, line.strip()))
    return found


# ---------------------------------------------------------------------------
# the book model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PageRecord:
    number: int
    chapter: str
    sequence: str
    title: str
    status: str

    @property
    def id(self) -> str:
        return f"{self.number:03d}"


@dataclass
class Book:
    pages: list[PageRecord]
    chapter_order: list[str]
    chapter_titles: dict[str, str]

    def numbers(self) -> list[int]:
        return [page.number for page in self.pages]

    def chapter_bounds(self) -> dict[str, tuple[int, int]]:
        bounds: dict[str, tuple[int, int]] = {}
        for page in self.pages:
            low, high = bounds.get(page.chapter, (page.number, page.number))
            bounds[page.chapter] = (min(low, page.number), max(high, page.number))
        return bounds

    def sequence_bounds(self) -> dict[str, tuple[int, int]]:
        bounds: dict[str, tuple[int, int]] = {}
        for page in self.pages:
            low, high = bounds.get(page.sequence, (page.number, page.number))
            bounds[page.sequence] = (min(low, page.number), max(high, page.number))
        return bounds

    def sequence_order(self) -> list[str]:
        return list(dict.fromkeys(page.sequence for page in self.pages))


def read_book() -> Book:
    model = crossref.build()
    return Book(
        pages=[
            PageRecord(page.number, page.chapter, page.sequence, page.title, page.status)
            for page in model.pages
        ],
        chapter_order=[chapter.id for chapter in model.chapters],
        chapter_titles={chapter.id: chapter.title for chapter in model.chapters},
    )


# ---------------------------------------------------------------------------
# operations
# ---------------------------------------------------------------------------

@dataclass
class Operation:
    """One editorial change to the page set, resolved into a complete renumbering."""
    label: str
    pages: list[PageRecord]                        # the book afterwards
    mapping: dict[int, int] = field(default_factory=dict)   # surviving old -> new
    created: list[PageRecord] = field(default_factory=list)
    deleted: list[PageRecord] = field(default_factory=list)

    @property
    def parity_inverting(self) -> bool:
        return any((new - old) % 2 for old, new in self.mapping.items())

    @property
    def shifted(self) -> dict[int, int]:
        return {old: new for old, new in self.mapping.items() if old != new}


def renumber(order: list[PageRecord]) -> list[PageRecord]:
    return [
        PageRecord(index, page.chapter, page.sequence, page.title, page.status)
        for index, page in enumerate(order, 1)
    ]


def build_insert(book: Book, at: int, new_pages: list[PageRecord]) -> Operation:
    order = list(book.pages)
    index = next((position for position, page in enumerate(order) if page.number >= at), len(order))
    order[index:index] = new_pages
    final = renumber(order)
    mapping: dict[int, int] = {}
    created: list[PageRecord] = []
    for position, page in enumerate(order):
        if page in new_pages:
            created.append(final[position])
        else:
            mapping[page.number] = final[position].number
    titles = ", ".join(repr(page.title) for page in new_pages)
    return Operation(
        label=f"insert {len(new_pages)} page(s) at {at:03d} ({titles})",
        pages=final, mapping=mapping, created=created,
    )


def build_delete(book: Book, targets: list[int]) -> Operation:
    doomed = set(targets)
    order = [page for page in book.pages if page.number not in doomed]
    final = renumber(order)
    mapping = {page.number: final[position].number for position, page in enumerate(order)}
    return Operation(
        label="delete page(s) " + ", ".join(f"{number:03d}" for number in sorted(doomed)),
        pages=final, mapping=mapping,
        deleted=[page for page in book.pages if page.number in doomed],
    )


def build_move(
    book: Book, source: int, destination: int, chapter: str, sequence: str
) -> Operation:
    """``destination`` is the number the page carries afterwards.

    Chapter and sequence travel with the page unless the editor renames them. Moving a page
    across a chapter boundary is a membership change, so it has to be stated: nothing here
    infers which chapter a page now belongs to.
    """
    order = list(book.pages)
    moving = next(page for page in order if page.number == source)
    order.remove(moving)
    order.insert(
        destination - 1,
        PageRecord(moving.number, chapter or moving.chapter,
                   sequence or moving.sequence, moving.title, moving.status),
    )
    final = renumber(order)
    mapping = {page.number: final[position].number for position, page in enumerate(order)}
    detail = ""
    if chapter and chapter != moving.chapter:
        detail += f", chapter {moving.chapter} -> {chapter}"
    if sequence and sequence != moving.sequence:
        detail += f", sequence {moving.sequence} -> {sequence}"
    return Operation(
        label=f"move page {source:03d} to {destination:03d}{detail}",
        pages=final, mapping=mapping,
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


def assertion_notes(assertions: list[Assertion], mapping: dict[int, int] | None) -> list[Note]:
    """Check every parity claim against arithmetic, before or after an operation."""
    notes: list[Note] = []
    for item in sorted(assertions, key=lambda a: (a.page, a.line)):
        was_true = item.claimed == parity_of(item.target)
        if mapping is None:
            if not was_true:
                notes.append(Note(
                    item.severity, "parity-assertion-false",
                    f"{item.path}:{item.line}",
                    f"claims page {item.target:03d} is {item.claimed}; "
                    f"{item.target:03d} is {parity_of(item.target)}",
                ))
            continue
        if item.target not in mapping:
            notes.append(Note(
                "error", "parity-assertion-dangling", f"{item.path}:{item.line}",
                f"claims page {item.target:03d} is {item.claimed}, and page "
                f"{item.target:03d} is being deleted",
            ))
            continue
        moved = mapping[item.target]
        now_true = item.claimed == parity_of(moved)
        if was_true and not now_true:
            notes.append(Note(
                item.severity, "parity-assertion-invalidated", f"{item.path}:{item.line}",
                f"page {item.target:03d} becomes {moved:03d}, so “{item.claimed}” "
                f"becomes false: {item.text}",
            ))
        elif not was_true and now_true:
            notes.append(Note(
                "note", "parity-assertion-repaired", f"{item.path}:{item.line}",
                f"was already wrong and becomes true at {moved:03d}: {item.text}",
            ))
        elif not was_true:
            notes.append(Note(
                item.severity, "parity-assertion-false", f"{item.path}:{item.line}",
                f"was already wrong and stays wrong at {moved:03d}: {item.text}",
            ))
    return notes


def turn_notes(turns: list[Turn], mapping: dict[int, int] | None) -> list[Note]:
    notes: list[Note] = []
    for turn in turns:
        if mapping is None:
            if not turn.holds(turn.outgoing, turn.landing):
                notes.append(Note(
                    "error", "turn-wrong-device",
                    f"{turn.outgoing:03d} → {turn.landing:03d}",
                    f"is filed as {turn.label} and is not one; move the row to the other "
                    "table or renumber the beat",
                ))
            continue
        if turn.outgoing not in mapping or turn.landing not in mapping:
            notes.append(Note(
                "error", "turn-endpoint-deleted",
                f"{turn.outgoing:03d} → {turn.landing:03d}",
                f"loses an endpoint to the deletion: {turn.function}",
            ))
            continue
        out, land = mapping[turn.outgoing], mapping[turn.landing]
        if not turn.holds(turn.outgoing, turn.landing):
            notes.append(Note(
                "note", "turn-already-broken",
                f"{turn.outgoing:03d} → {turn.landing:03d}",
                f"was not {turn.label} before this operation and becomes "
                f"{out:03d} → {land:03d}",
            ))
            continue
        if turn.holds(out, land):
            if (out, land) != (turn.outgoing, turn.landing):
                notes.append(Note(
                    "note", "turn-renumbered",
                    f"{turn.outgoing:03d} → {turn.landing:03d}",
                    f"becomes {out:03d} → {land:03d} and stays {turn.label}",
                ))
        else:
            notes.append(Note(
                "error", "turn-broken",
                f"{turn.outgoing:03d} → {turn.landing:03d}",
                f"becomes {out:03d} → {land:03d}, which is no longer {turn.label}: "
                f"{turn.function}",
            ))
    return notes


def soft_notes(mapping: dict[int, int]) -> list[Note]:
    notes: list[Note] = []
    for path, line, page, text in read_soft_choreography():
        if page not in mapping:
            continue
        if (mapping[page] - page) % 2 == 0:
            continue
        notes.append(Note(
            "warning", "choreography-page-parity-changed", f"{path}:{line}",
            f"page {page:03d} becomes {mapping[page]:03d} and changes side: {text}",
        ))
    return notes


def convention_notes(book: Book) -> list[Note]:
    """The repository's two page conventions have to keep closing.

    ``content/story-contract.md`` says story page 1 is a recto, so the physical spreads are
    the lone opening recto, a run of (even, odd) facing pairs, and the lone final verso.
    Under that layout an (even, odd) pair is *visible at once* and an (odd, even) pair is
    the only thing hidden behind a leaf. Those are two different devices, and the audit in
    ``content/production-review.md`` files each row under the one it uses.

    That resolution lives in prose, so it can be undone by an edit. This checks that a
    recto first page still comes with an audit that names both devices; the rows themselves
    are checked against their own section by ``turn_notes``.
    """
    notes: list[Note] = []
    contract = (ROOT / "content" / "story-contract.md").read_text(encoding="utf-8")
    if "Story page 1 is a right-hand recto" not in contract:
        return notes
    review = (ROOT / "content" / "production-review.md").read_text(encoding="utf-8")
    missing = [device for pattern, device in TURN_SECTIONS if not pattern.search(review)]
    if not missing:
        return notes
    total = len(book.pages)
    spreads = 1 + (total - 1) // 2 + (1 if total % 2 == 0 else 0)
    notes.append(Note(
        "warning", "turn-convention-unclosed", "content/production-review.md",
        f"page 1 is a recto and the book has {total} pages, so its {spreads} physical "
        "spreads make an even-to-odd pair a facing reveal and an odd-to-even pair a turn "
        "across the leaf. The audit no longer names both devices ("
        + ", ".join(missing) + " is missing), so every row is being checked as a facing "
        "reveal by default",
    ))
    return notes


def spread_notes(book: Book) -> list[Note]:
    """Declared two-page spreads must pair a verso with the following recto, in one chapter."""
    notes: list[Note] = []
    chapter_of = {page.number: page.chapter for page in book.pages}
    for path in sorted((ROOT / "content" / "pages").glob("[0-9][0-9][0-9].md")):
        metadata = crossref.front_matter(path.read_text(encoding="utf-8"))
        match = re.search(r"^spread:\s*(\d{1,3})\s*$", metadata or "", re.MULTILINE)
        if not match:
            continue
        first = int(match.group(1))
        relative = str(path.relative_to(ROOT))
        if first % 2:
            notes.append(Note("error", "spread-parity", relative,
                              f"declares a spread starting on {first:03d}, which is a recto"))
        if chapter_of.get(first) != chapter_of.get(first + 1):
            notes.append(Note("error", "spread-chapter-boundary", relative,
                              f"declares a spread {first:03d}–{first + 1:03d} that crosses "
                              "a chapter boundary"))
    return notes


def structure_notes(book: Book) -> list[Note]:
    notes: list[Note] = []
    if book.numbers() != list(range(1, len(book.pages) + 1)):
        notes.append(Note("error", "manifest-order", "data/pages.yaml",
                          "does not number its pages 1..N in order"))
    for label, groups in (("chapter", [page.chapter for page in book.pages]),
                          ("sequence", [page.sequence for page in book.pages])):
        seen: set[str] = set()
        previous = None
        for value in groups:
            if value != previous and value in seen:
                notes.append(Note("error", f"{label}-not-contiguous", f"{label} {value}",
                                  "does not occupy one unbroken run of pages"))
            seen.add(value)
            previous = value
    return notes


def reference_notes(sites: list[Site], numbers: set[int]) -> list[Note]:
    notes: list[Note] = []
    for site in sites:
        if site.kind == AMBIGUOUS:
            notes.append(Note("warning", "ambiguous-reference", f"{site.path}:{site.line}",
                              f"“{site.text}” is not padded, so it cannot be told "
                              "apart from a source-document citation and is never rewritten"))
        elif site.kind == REFERENCE:
            missing = sorted(value for value in site.numbers if value not in numbers)
            if missing:
                notes.append(Note("error", "dangling-reference", f"{site.path}:{site.line}",
                                  f"“{site.text}” names "
                                  + ", ".join(f"{value:03d}" for value in missing)
                                  + ", which the manifest does not contain"))
    return notes


# ---------------------------------------------------------------------------
# rewriting
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    writes: dict[str, str] = field(default_factory=dict)      # relative path -> text
    removals: list[str] = field(default_factory=list)
    renames: list[tuple[str, str]] = field(default_factory=list)   # directories
    notes: list[Note] = field(default_factory=list)


def replace_number_column(row: str, value: str) -> str:
    return re.sub(r"^\|\s*[^|]*", f"| {value} ", row, count=1)


def yaml_scalar(value: str, quoted: str | None = None) -> str:
    """Keep the file's own quoting. A bare ``01`` would otherwise read back as ``1``."""
    if quoted or (value.isdigit() and value.startswith("0")):
        return f'"{value}"'
    return value


def ledger_sequence(value: str) -> str:
    return {"interlude-a": "A", "interlude-b": "B", "interlude-c": "C"}.get(value, value)


def page_range(low: int, high: int, *, pad: bool = False) -> str:
    fmt = "{:03d}" if pad else "{}"
    if low == high:
        return fmt.format(low)
    return f"{fmt.format(low)}–{fmt.format(high)}"


def new_page_script(page: PageRecord, population: str) -> str:
    return (
        "---\n"
        f"page: {page.number}\n"
        f"chapter: {yaml_scalar(page.chapter)}\n"
        f"sequence: {page.sequence}\n"
        f"title: {page.title}\n"
        f"status: {page.status}\n"
        "story_time: unscheduled\n"
        f"population: {population}\n"
        "locations: []\n"
        "provenance:\n"
        "  - status: invented\n"
        "    source: NONE-FICTION\n"
        "exact_strings: []\n"
        "continuity_checks: []\n"
        "---\n"
        "\n"
        f"# Page {page.number:03d}\n"
        "\n"
        "## Page purpose\n"
        "\n"
        "[Causal change on this page. End with the question or consequence carried across "
        "the page turn.]\n"
        "\n"
        "## Panel 1\n"
        "\n"
        "**Frame:** [Shot, angle, environment, actors/system surfaces, visible state.]\n"
        "\n"
        "**Action:** [What changes.]\n"
        "\n"
        "**Provenance:** `invented` — `NONE-FICTION`; placeholder for an unwritten page.\n"
        "\n"
        "## Page notes\n"
        "\n"
        "- Inserted by `scripts/pagination.py`. Nothing here is drafted.\n"
        "- Do not state this page's parity in prose; `scripts/pagination.py check` derives it.\n"
    )


def beat_row(page: PageRecord) -> str:
    return (
        f"| {page.number} | {ledger_sequence(page.sequence)} | [Causal job for this page.] | "
        "[End beat.] | `invented` |"
    )


def plan_rewrite(book: Book, operation: Operation, population: str) -> Plan:
    plan = Plan()
    mapping = operation.mapping
    after = {page.number: page for page in operation.pages}
    created = {page.number for page in operation.created}
    def read(relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    # --- page scripts -------------------------------------------------------
    for old, new in sorted(mapping.items()):
        relative = f"content/pages/{old:03d}.md"
        text = read(relative)
        text = re.sub(r"^page:\s*\d+\s*$", f"page: {new}", text, count=1, flags=re.MULTILINE)
        record = after[new]
        for name, value in (("chapter", record.chapter), ("sequence", record.sequence)):
            text = re.sub(
                rf'^{name}:\s*(")?([^"\n]+?)"?\s*$',
                lambda match, value=value, name=name: (
                    match.group(0) if match.group(2) == value
                    else f"{name}: {yaml_scalar(value, match.group(1))}"
                ),
                text, count=1, flags=re.MULTILINE,
            )
        text, dangling = rewrite_prose(text, mapping)
        for value, snippet in dangling:
            plan.notes.append(Note("error", "dangling-reference", relative,
                                   f"“{snippet}” names page {value:03d}, "
                                   "which is being deleted"))
        plan.writes[f"content/pages/{new:03d}.md"] = text
        if old != new:
            plan.removals.append(relative)
    for page in operation.deleted:
        plan.removals.append(f"content/pages/{page.id}.md")
    for page in operation.created:
        plan.writes[f"content/pages/{page.id}.md"] = new_page_script(page, population)

    # --- other prose --------------------------------------------------------
    for path in prose_files():
        relative = str(path.relative_to(ROOT))
        if relative.startswith("content/pages/"):
            continue
        text = read(relative)
        rewritten, dangling = rewrite_prose(text, mapping)
        for value, snippet in dangling:
            plan.notes.append(Note("error", "dangling-reference", relative,
                                   f"“{snippet}” names page {value:03d}, "
                                   "which is being deleted"))
        if rewritten != text:
            plan.writes[relative] = rewritten

    # --- data/pages.yaml ----------------------------------------------------
    manifest = read("data/pages.yaml")
    rows = "\n".join(
        f'  - {{id: "{page.id}", chapter: "{page.chapter}", sequence: "{page.sequence}", '
        f'title: "{page.title}", status: {page.status}}}'
        for page in operation.pages
    )
    manifest = re.sub(r"^  story_pages: \d+$", f"  story_pages: {len(operation.pages)}",
                      manifest, count=1, flags=re.MULTILINE)
    manifest = re.sub(r"(?<=^pages:\n)(?:  - \{id: .*\n)+", rows + "\n", manifest,
                      count=1, flags=re.MULTILINE)
    plan.writes["data/pages.yaml"] = manifest

    # --- data/chapters.yaml -------------------------------------------------
    chapters_text = read("data/chapters.yaml")
    bounds = Book(operation.pages, book.chapter_order, book.chapter_titles).chapter_bounds()
    chunks = re.split(r"(?=^  - id: )", chapters_text, flags=re.MULTILINE)
    for index, chunk in enumerate(chunks):
        identifier = re.search(r"^  - id: \"?([\w-]+)\"?", chunk, re.MULTILINE)
        if not identifier or identifier.group(1) not in bounds:
            continue
        low, high = bounds[identifier.group(1)]
        chunk = re.sub(r"^    first_page: \d+$", f"    first_page: {low}", chunk,
                       count=1, flags=re.MULTILINE)
        chunks[index] = re.sub(r"^    last_page: \d+$", f"    last_page: {high}", chunk,
                               count=1, flags=re.MULTILINE)
    plan.writes["data/chapters.yaml"] = "".join(chunks)

    # --- content/page-plan.md ----------------------------------------------
    plan.writes["content/page-plan.md"] = rewrite_beat_sheet(
        plan.writes.get("content/page-plan.md", read("content/page-plan.md")),
        book, operation,
    )

    # --- content/story-contract.md canonical map ---------------------------
    contract = plan.writes.get("content/story-contract.md", read("content/story-contract.md"))
    order = [chapter for chapter in book.chapter_order if chapter in bounds]
    index = 0

    def contract_row(match: re.Match[str]) -> str:
        nonlocal index
        if index >= len(order):
            return match.group(0)
        low, high = bounds[order[index]]
        index += 1
        return replace_number_column(match.group(0), page_range(low, high))

    contract = re.sub(r"^\|\s*\d{1,3}(?:–\d{1,3})?\s*\|\s*(?:Prologue|Chapter|Epilogue).*$",
                      contract_row, contract, flags=re.MULTILINE)
    plan.writes["content/story-contract.md"] = contract

    # --- content/chapters/*.md briefs --------------------------------------
    for chapter_id, (low, high) in bounds.items():
        matches = [path for path in sorted((ROOT / "content" / "chapters").glob("*.md"))
                   if chapter_file_id(path, book) == chapter_id]
        for path in matches:
            relative = str(path.relative_to(ROOT))
            text = plan.writes.get(relative, read(relative))
            plan.writes[relative] = re.sub(
                r"^(- \*\*Pages:\*\* )\d{1,3}[–-]\d{1,3}$",
                lambda match: match.group(1) + page_range(low, high),
                text, count=1, flags=re.MULTILINE,
            )

    # --- research/scene-provenance.md ledger ranges ------------------------
    plan.writes["research/scene-provenance.md"] = rewrite_ledger(
        plan.writes.get("research/scene-provenance.md", read("research/scene-provenance.md")),
        Book(operation.pages, book.chapter_order, book.chapter_titles),
    )

    # --- content/production-review.md tables --------------------------------
    review = plan.writes.get("content/production-review.md", read("content/production-review.md"))
    review = rewrite_padded_tables(review, mapping)
    plan.writes["content/production-review.md"] = review

    # --- panel art ----------------------------------------------------------
    art = read("data/panel-art.tsv")
    plan.writes["data/panel-art.tsv"] = rewrite_panel_keys(art, mapping)
    plan.writes["data/assets.yaml"] = rewrite_panel_keys(read("data/assets.yaml"), mapping)
    for directory in ("assets/art/panels", "prompts/pages"):
        base = ROOT / directory
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            match = re.match(r"^(\d{3})(-\d{2})?$", child.name)
            if not match:
                continue
            old = int(match.group(1))
            if old not in mapping:
                plan.notes.append(Note("error", "orphaned-art", f"{directory}/{child.name}",
                                       "belongs to a page that is being deleted"))
                continue
            if mapping[old] != old:
                plan.renames.append((
                    f"{directory}/{child.name}",
                    f"{directory}/{mapping[old]:03d}{match.group(2) or ''}",
                ))

    # A rewritten file that lives inside a renamed directory belongs at its destination, not
    # at the name the directory is about to vacate. `prompts/pages/NNN/` is the case that
    # bites: its files name their own page, so they are rewritten and moved at once.
    # Remapped in one pass, because a shift is a permutation and popping keys one at a time
    # would let one page's prompts land on another's.
    def destination(relative: str) -> str:
        for source, target in plan.renames:
            if relative.startswith(source + "/"):
                return target + relative[len(source):]
        return relative

    plan.writes = {destination(relative): text for relative, text in plan.writes.items()}

    # --- historical records -------------------------------------------------
    for relative in HISTORICAL:
        path = ROOT / relative
        if not path.exists():
            continue
        touched = {
            value
            for value in re.findall(r"\d{3}", path.read_text(encoding="utf-8"))
            if int(value) in operation.shifted
        }
        if touched:
            plan.notes.append(Note("note", "historical-record", relative,
                                   f"names {len(touched)} page numbers that move; it is a dated "
                                   "record and is not rewritten"))

    del created
    return plan


def chapter_file_id(path: Path, book: Book) -> str:
    stem = path.stem[:2]
    if stem == "00":
        return book.chapter_order[0]
    if path.stem.startswith("07"):
        return book.chapter_order[-1]
    return stem


def rewrite_beat_sheet(text: str, book: Book, operation: Operation) -> str:
    """Re-emit the beat rows in the new order, keeping each row's editorial body."""
    bodies: dict[int, str] = {}
    lines = text.splitlines()
    row_indexes = [
        index for index, line in enumerate(lines)
        if re.match(r"^\|\s*\d{1,3}\s*\|", line)
    ]
    numbers = iter(book.numbers())
    for index in row_indexes:
        bodies[next(numbers)] = lines[index]
    after = {page.number: page for page in operation.pages}
    rows_by_new: dict[int, str] = {}
    for old, new in operation.mapping.items():
        row = replace_number_column(bodies[old], str(new))
        rows_by_new[new] = re.sub(
            r"^(\|[^|]*\|)\s*[^|]*", rf"\1 {ledger_sequence(after[new].sequence)} ",
            row, count=1,
        )
    for page in operation.created:
        rows_by_new[page.number] = beat_row(page)

    sections: list[list[int]] = []
    for page in operation.pages:
        chapter_index = book.chapter_order.index(page.chapter)
        while len(sections) <= chapter_index:
            sections.append([])
        sections[chapter_index].append(page.number)

    output: list[str] = []
    section = -1
    emitted: set[int] = set()
    for index, line in enumerate(lines):
        if re.match(r"^## (?:Prologue|Chapter|Epilogue)", line):
            section += 1
            output.append(line)
            continue
        if index in row_indexes:
            if section >= 0 and section < len(sections):
                for number in sections[section]:
                    if number not in emitted:
                        output.append(rows_by_new[number])
                        emitted.add(number)
            continue
        output.append(line)
    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def rewrite_ledger(text: str, book: Book) -> str:
    """The ledger's Target pages column is derived from sequence membership."""
    bounds = book.sequence_bounds()
    aliases = {"A": "interlude-a", "B": "interlude-b", "C": "interlude-c"}

    def row(match: re.Match[str]) -> str:
        key = aliases.get(match.group(1), match.group(1))
        if key not in bounds:
            return match.group(0)
        low, high = bounds[key]
        return f"| {match.group(1)} | {page_range(low, high)} |"

    section = re.search(r"(## Sequence ledger\s*\n)(.*?)(?=\n## )", text, re.DOTALL)
    if not section:
        return text
    body = re.sub(r"^\|\s*(\w+)\s*\|\s*[\d–—-]+\s*\|", row, section.group(2),
                  flags=re.MULTILINE)
    return text[:section.start(2)] + body + text[section.end(2):]


def rewrite_padded_tables(text: str, mapping: dict[int, int]) -> str:
    """Turn-audit and revision rows carry bare padded page numbers in table cells."""
    def number(match: re.Match[str]) -> str:
        value = int(match.group(0))
        return f"{mapping[value]:03d}" if value in mapping else match.group(0)

    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if TURN_ROW.match(line) or re.match(r"^\|\s*\d{3}\s*\|", line):
            lines[index] = re.sub(r"\b\d{3}\b", number, line)
    return "".join(lines)


def rewrite_panel_keys(text: str, mapping: dict[int, int]) -> str:
    def key(match: re.Match[str]) -> str:
        value = int(match.group(1))
        if value not in mapping:
            return match.group(0)
        return f"{mapping[value]:03d}{match.group(2)}"

    text = re.sub(r"\b(\d{3})(-\d{2})\b", key, text)
    return re.sub(
        r"\b(?<=pages/)(\d{3})()\b",
        lambda match: f"{mapping[int(match.group(1))]:03d}"
        if int(match.group(1)) in mapping else match.group(0),
        text,
    )


def drop_unchanged(plan: Plan) -> Plan:
    plan.writes = {
        relative: text
        for relative, text in plan.writes.items()
        if not (ROOT / relative).exists() or (ROOT / relative).read_text(encoding="utf-8") != text
    }
    return plan


def commit(plan: Plan) -> None:
    staging = ROOT / ".pagination-staging"
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
        # Renames land before writes, never after: a rewritten file inside a renamed
        # directory is written under its destination, and unstaging afterwards would put
        # the original content back on top of it.
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


def cmd_report(book: Book, sites: list[Site]) -> int:
    assertions = read_assertions()
    turns = read_turns()
    census: dict[str, int] = {}
    for site in sites:
        census[site.kind] = census.get(site.kind, 0) + 1
    print(
        f"{len(book.pages)} story pages in {len(book.chapter_order)} chapters and "
        f"{len(book.sequence_order())} sequences."
    )
    print("\nChapters")
    for chapter, (low, high) in Book(
        book.pages, book.chapter_order, book.chapter_titles
    ).chapter_bounds().items():
        print(f"  {chapter:<9} {page_range(low, high, pad=True):>9}  "
              f"{high - low + 1:>3} pages  opens on a {parity_of(low)}  "
              f"{book.chapter_titles.get(chapter, '')}")
    print("\nParity assertions")
    for kind, label in (("frame", "art direction"), ("note", "page notes"),
                        ("inline", "about another page")):
        items = [item for item in assertions if item.kind == kind]
        wrong = [item for item in items if item.claimed != parity_of(item.target)]
        print(f"  {label:<20} {len(items):>3} claims on "
              f"{len({item.page for item in items}):>3} pages, {len(wrong)} disagree with arithmetic")
    print(f"\nPage-turn audit: {len(turns)} named beats")
    for device, label in ((FACING, "reveals across the gutter"), (LEAF, "turns across the leaf")):
        rows = [turn for turn in turns if turn.device == device]
        holding = sum(1 for turn in rows if turn.holds(turn.outgoing, turn.landing))
        print(f"  {label:<26} {len(rows):>3} named, {len(rows) - holding} filed as the "
              "wrong device")
    print("\nReference sites in prose")
    for kind in (REFERENCE, FOREIGN, RULE, AMBIGUOUS):
        print(f"  {kind:<12} {census.get(kind, 0):>4}")
    print(f"\nHistorical records not rewritten: {', '.join(HISTORICAL)}")
    return 0


def audit(book: Book, sites: list[Site]) -> list[Note]:
    return (
        structure_notes(book)
        + assertion_notes(read_assertions(), None)
        + turn_notes(read_turns(), None)
        + spread_notes(book)
        + convention_notes(book)
        + reference_notes(sites, set(book.numbers()))
    )


def cmd_check(book: Book, sites: list[Site], strict: bool) -> int:
    notes = audit(book, sites)
    counts = print_notes(notes)
    blocking = counts["error"] + (counts["warning"] if strict else 0)
    if blocking:
        print(f"\nPagination check failed: {blocking} blocking findings.")
        return 1
    print(f"\nPagination check passed: {len(book.pages)} pages, "
          f"{len(read_assertions())} parity assertions, {len(read_turns())} named turns.")
    return 0


def impact(book: Book, operation: Operation) -> list[Note]:
    return (
        assertion_notes(read_assertions(), operation.mapping)
        + turn_notes(read_turns(), operation.mapping)
        + soft_notes(operation.mapping)
        + structure_notes(Book(operation.pages, book.chapter_order, book.chapter_titles))
    )


def run_operation(book: Book, operation: Operation, args: argparse.Namespace) -> int:
    print(f"Operation: {operation.label}")
    inverting = operation.parity_inverting
    print(f"Parity: {'INVERTING' if inverting else 'preserving'} "
          f"({len(operation.shifted)} pages renumbered, "
          f"{len(operation.created)} created, {len(operation.deleted)} deleted)")

    if operation.shifted:
        print("\nPage map")
        for old, new in sorted(operation.shifted.items()):
            print(f"  {old:03d} -> {new:03d}")
    for page in operation.created:
        print(f"  new  {page.id}  {page.chapter}/{page.sequence}  {page.title!r}")
    for page in operation.deleted:
        print(f"  gone {page.id}  {page.chapter}/{page.sequence}  {page.title!r}")

    notes = impact(book, operation)
    plan = drop_unchanged(
        plan_rewrite(book, operation, getattr(args, "population", ""))
    )
    notes += plan.notes
    counts = print_notes(notes)

    print(f"\nFiles: {len(plan.writes)} written, {len(plan.removals)} removed, "
          f"{len(plan.renames)} directories renamed")

    if inverting and not args.allow_parity_shift:
        print("\nRefused: this operation inverts recto/verso for "
              f"{sum(1 for old, new in operation.mapping.items() if (new - old) % 2)} pages. "
              "The findings above are the work list. Re-run with --allow-parity-shift to take "
              "it deliberately.")
        return 1
    art_loss = [note for note in plan.notes if note.kind == "orphaned-art"]
    if art_loss and not args.allow_art_loss:
        print("\nRefused: deleting these pages discards existing art. Re-run with "
              "--allow-art-loss to take it deliberately.")
        return 1
    if not args.apply:
        print("\nPlan only. Re-run with --apply to write it.")
        return 0

    commit(plan)
    print("\nApplied. Regenerate the derived artifacts, then re-check:")
    print("  python3 scripts/paneltypes.py write")
    print("  python3 scripts/build-site.py")
    print("  python3 scripts/pagination.py check")
    if counts["error"]:
        print(f"\n{counts['error']} findings remain open. They are editorial, not mechanical.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="page map, parity map, turn audit, reference census")
    check = commands.add_parser("check", help="exit non-zero while the tree disagrees with itself")
    check.add_argument("--strict", action="store_true", help="also fail on warnings")

    for name, help_text in (
        ("insert", "add pages before a position"),
        ("delete", "remove pages"),
        ("move", "move one page to another position"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--apply", action="store_true", help="write the plan")
        command.add_argument("--allow-parity-shift", action="store_true",
                             help="permit an operation that inverts recto/verso")
        command.add_argument("--allow-art-loss", action="store_true",
                             help="permit discarding art belonging to a deleted page")
        if name == "insert":
            command.add_argument("--at", required=True, type=int, metavar="NNN")
            command.add_argument("--title", required=True, action="append")
            command.add_argument("--chapter", required=True)
            command.add_argument("--sequence", required=True)
            command.add_argument("--population", default="",
                                 help="defaults to the population of the displaced page")
            command.add_argument("--status", default="planned")
        elif name == "delete":
            command.add_argument("pages", nargs="+", type=int, metavar="NNN")
        else:
            command.add_argument("page", type=int, metavar="NNN")
            command.add_argument("--to", type=int, metavar="NNN",
                                 help="the number the page carries afterwards (default: "
                                      "unchanged, for a pure chapter reassignment)")
            command.add_argument("--chapter", default="")
            command.add_argument("--sequence", default="")

    args = parser.parse_args(argv)
    book = read_book()
    sites = [
        site
        for path in prose_files()
        for site in scan_prose(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)))
    ]

    if args.command == "report":
        return cmd_report(book, sites)
    if args.command == "check":
        return cmd_check(book, sites, args.strict)

    numbers = set(book.numbers())
    if args.command == "insert":
        if not 1 <= args.at <= len(book.pages) + 1:
            print(f"insert --at {args.at:03d} is outside 001–{len(book.pages) + 1:03d}")
            return 2
        if not args.population:
            displaced = next((page for page in book.pages if page.number == args.at), None)
            args.population = read_population(displaced.number) if displaced else "second"
        new_pages = [
            PageRecord(0, args.chapter, args.sequence, title, args.status)
            for title in args.title
        ]
        operation = build_insert(book, args.at, new_pages)
    elif args.command == "delete":
        missing = sorted(set(args.pages) - numbers)
        if missing:
            print("no such page: " + ", ".join(f"{value:03d}" for value in missing))
            return 2
        operation = build_delete(book, args.pages)
    else:
        destination = args.to if args.to is not None else args.page
        if args.page not in numbers or not 1 <= destination <= len(book.pages):
            print("move endpoints must be existing page numbers")
            return 2
        operation = build_move(book, args.page, destination, args.chapter, args.sequence)
    return run_operation(book, operation, args)


def read_population(number: int) -> str:
    path = ROOT / "content" / "pages" / f"{number:03d}.md"
    metadata = crossref.front_matter(path.read_text(encoding="utf-8")) if path.exists() else ""
    match = re.search(r"^population:\s*(\S+)\s*$", metadata, re.MULTILINE)
    return match.group(1) if match else "second"


if __name__ == "__main__":
    raise SystemExit(main())
