#!/usr/bin/env python3
"""Measure, check, and assemble the novella: the book told again in prose, one file per panel.

The graphic novel's canonical unit is the page script in ``content/pages/NNN.md``. The novella
renders the same story in continuous prose and lives beside it as ``content/novella/NNN/
panel-II.md`` -- one file per *scripted* panel, so a page written as a nine-cell grouped run
has nine files where the viewer exposes one image slot. Each file carries its page, panel,
title, status and provenance statuses in front matter, then a ``# Page NNN — Panel II``
heading, then the prose. The story contract's truth rules bind the prose exactly as they bind
the script: it may not invent an incident fact, quote raw agent text, or supply an agent's
interior state.

    python3 scripts/novella.py report              # word census, per chapter and per panel
    python3 scripts/novella.py check               # exit non-zero while prose and script disagree
    python3 scripts/novella.py assemble            # the whole novella as one Markdown document
    python3 scripts/novella.py assemble --out FILE --continuous

``check`` holds the prose tree to the page scripts: every scripted panel has a file, every
file names a scripted panel, front matter agrees with the script on page, panel and title,
and a file's provenance statuses are drawn from its panel's own ``**Provenance:**`` line. It
does not judge length; ``report`` measures it. The target the novella was commissioned to is
an average of about one manuscript page -- 250 words -- per panel, varying widely by beat.

Renumbering is not this script's job. ``scripts/pagination.py`` and ``scripts/panels.py`` move
the prose files with their pages and panels and rewrite their front matter and headings.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crossref  # noqa: E402
import panels  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content" / "novella"

STATUSES = (
    "documented", "raw-agent-text", "source-paraphrase", "disputed",
    "inferred", "compressed", "reconstructed", "invented",
)
FILE_STATUSES = ("draft", "review", "locked", "published")
MANUSCRIPT_PAGE = 250
HEADING = re.compile(r"^# Page (\d{3}) — Panel (\d{2})\s*$", re.MULTILINE)
PROVENANCE_LINE = re.compile(r"^\*\*Provenance:\*\*(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Prose:
    path: str
    page: int | None
    panel: int | None
    title: str
    status: str
    provenance: tuple[str, ...]
    heading: tuple[int, int] | None
    body: str

    @property
    def words(self) -> int:
        return len(panels.WORD.findall(self.body))


def prose_path(page: int, index: int) -> Path:
    return BASE / f"{page:03d}" / f"panel-{index:02d}.md"


def expected(scripts: dict[int, panels.PageScript]) -> dict[tuple[int, int], Path]:
    return {
        (number, index): prose_path(number, index)
        for number, script in sorted(scripts.items())
        for index in range(1, script.count + 1)
    }


def found() -> dict[tuple[int, int], Path]:
    files: dict[tuple[int, int], Path] = {}
    if not BASE.is_dir():
        return files
    for page_dir in sorted(BASE.iterdir()):
        if not re.fullmatch(r"\d{3}", page_dir.name):
            continue
        for child in sorted(page_dir.glob("panel-[0-9][0-9].md")):
            files[(int(page_dir.name), int(child.stem.split("-")[1]))] = child
    return files


def stray_files() -> list[Path]:
    """Anything under the tree that is not a page directory holding panel files."""
    strays: list[Path] = []
    if not BASE.is_dir():
        return strays
    for child in sorted(BASE.rglob("*")):
        if child.is_dir():
            if child.parent == BASE and not re.fullmatch(r"\d{3}", child.name):
                strays.append(child)
            continue
        if child.parent == BASE or not re.fullmatch(r"panel-\d{2}\.md", child.name):
            if child.name != "README.md":
                strays.append(child)
    return strays


def read_prose(path: Path) -> Prose:
    text = path.read_text(encoding="utf-8")
    metadata = crossref.front_matter(text) or ""

    def value(key: str) -> str:
        match = re.search(rf"^{key}:\s*(.*?)\s*$", metadata, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def integer(key: str) -> int | None:
        raw = value(key)
        return int(raw) if raw.isdigit() else None

    raw_provenance = value("provenance").strip("[]")
    provenance = tuple(item.strip().strip("`'\"") for item in raw_provenance.split(",") if item.strip())
    body = text
    if metadata:
        body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    heading_match = HEADING.search(body)
    heading = (int(heading_match.group(1)), int(heading_match.group(2))) if heading_match else None
    body = HEADING.sub("", body, count=1).strip()
    return Prose(
        path=str(path.relative_to(ROOT)),
        page=integer("page"),
        panel=integer("panel"),
        title=value("title").strip('"'),
        status=value("status"),
        provenance=provenance,
        heading=heading,
        body=body,
    )


def script_provenance(script: panels.PageScript, index: int) -> set[str]:
    """The statuses a panel's own Provenance line names. A grouped run shares one line."""
    if script.sections:
        section = next((item for item in script.sections if item.index == index), None)
        source = section.body if section else ""
    else:
        source = script.text
    statuses: set[str] = set()
    for line in PROVENANCE_LINE.finditer(source):
        for token in re.findall(r"`([^`]+)`", line.group(1)):
            if token in STATUSES:
                statuses.add(token)
    return statuses


@dataclass(frozen=True)
class Note:
    severity: str
    kind: str
    subject: str
    message: str


def audit(scripts: dict[int, panels.PageScript]) -> list[Note]:
    notes: list[Note] = []
    wanted = expected(scripts)
    present = found()
    for key, path in sorted(wanted.items()):
        if key not in present:
            notes.append(Note("error", "prose-missing", str(path.relative_to(ROOT)),
                              f"panel {key[0]:03d}-{key[1]:02d} is scripted and has no prose"))
    for key, path in sorted(present.items()):
        if key not in wanted:
            notes.append(Note("error", "prose-orphaned", str(path.relative_to(ROOT)),
                              "names a panel no page script declares"))
    for stray in stray_files():
        notes.append(Note("warning", "prose-stray", str(stray.relative_to(ROOT)),
                          "is not a page directory or a panel file"))

    for (page, index), path in sorted(present.items()):
        if (page, index) not in wanted:
            continue
        prose = read_prose(path)
        script = scripts[page]
        if prose.page is None or prose.panel is None:
            notes.append(Note("error", "front-matter-missing", prose.path,
                              "carries no page and panel in front matter"))
        else:
            if prose.page != page or prose.panel != index:
                notes.append(Note("error", "front-matter-disagrees", prose.path,
                                  f"says page {prose.page} panel {prose.panel}; the path says "
                                  f"{page:03d}-{index:02d}"))
        if prose.heading is None:
            notes.append(Note("error", "heading-missing", prose.path,
                              "has no `# Page NNN — Panel II` heading"))
        elif prose.heading != (page, index):
            notes.append(Note("error", "heading-disagrees", prose.path,
                              f"is headed Page {prose.heading[0]:03d} — Panel "
                              f"{prose.heading[1]:02d}"))
        title = panels.front_matter_value(script, "title")
        if prose.title != title:
            notes.append(Note("warning", "title-disagrees", prose.path,
                              f"titles the page {prose.title!r}; the script says {title!r}"))
        if prose.status not in FILE_STATUSES:
            notes.append(Note("error", "status-invalid", prose.path,
                              f"status {prose.status!r} is not one of {', '.join(FILE_STATUSES)}"))
        if not prose.provenance:
            notes.append(Note("error", "provenance-missing", prose.path,
                              "declares no provenance statuses"))
        else:
            allowed = script_provenance(script, index)
            unknown = [item for item in prose.provenance if item not in STATUSES]
            foreign = [item for item in prose.provenance if item in STATUSES and item not in allowed]
            if unknown:
                notes.append(Note("error", "provenance-unknown", prose.path,
                                  "uses statuses the continuity bible does not define: "
                                  + ", ".join(unknown)))
            if foreign and allowed:
                notes.append(Note("warning", "provenance-upgraded", prose.path,
                                  "claims " + ", ".join(foreign) + " and the panel's own "
                                  "Provenance line names only " + ", ".join(sorted(allowed))))
        if prose.words == 0:
            notes.append(Note("error", "prose-empty", prose.path, "has no prose after its heading"))
        elif prose.body.startswith("[") and prose.body.endswith("]"):
            notes.append(Note("warning", "prose-stub", prose.path,
                              "is a placeholder left by an insert and has not been written"))
    return notes


def print_notes(notes: list[Note]) -> dict[str, int]:
    counts = {level: 0 for level in ("error", "warning", "note")}
    for level in counts:
        items = [note for note in notes if note.severity == level]
        counts[level] = len(items)
        if not items:
            continue
        print(f"\n{level.title()}s:")
        for note in items:
            print(f"- [{note.kind}] {note.subject}: {note.message}")
    return counts


def cmd_check(strict: bool) -> int:
    scripts = panels.read_scripts()
    notes = audit(scripts)
    counts = print_notes(notes)
    blocking = counts["error"] + (counts["warning"] if strict else 0)
    total = sum(script.count for script in scripts.values())
    if blocking:
        print(f"\nNovella check failed: {blocking} blocking findings.")
        return 1
    print(f"\nNovella check passed: {len(found())} prose files for {total} scripted panels.")
    return 0


def cmd_report() -> int:
    scripts = panels.read_scripts()
    model = crossref.build()
    chapter_title = {chapter.id: chapter.title for chapter in model.chapters}
    chapter_of = {page.number: page.chapter for page in model.pages}
    present = found()
    wanted = expected(scripts)
    counts: list[tuple[int, int, int]] = []
    per_chapter: dict[str, list[int]] = {}
    for key, path in sorted(present.items()):
        if key not in wanted:
            continue
        words = read_prose(path).words
        counts.append((words, *key))
        per_chapter.setdefault(chapter_of.get(key[0], "?"), []).append(words)
    total_panels = len(wanted)
    written = len(counts)
    total_words = sum(item[0] for item in counts)
    print(f"{written} of {total_panels} scripted panels have prose; "
          f"{total_words:,} words in all, about {total_words / MANUSCRIPT_PAGE:,.0f} "
          f"manuscript pages at {MANUSCRIPT_PAGE} words.")
    if counts:
        values = [item[0] for item in counts]
        print(f"\nPer panel: mean {statistics.mean(values):.0f}, median "
              f"{statistics.median(values):.0f}, shortest {min(values)}, longest {max(values)}.")
        print("\nBy chapter")
        for chapter in model.chapters:
            words = per_chapter.get(chapter.id, [])
            if not words:
                continue
            scripted = sum(script.count for number, script in scripts.items()
                           if chapter_of.get(number) == chapter.id)
            print(f"  {chapter.id:<9} {chapter_title.get(chapter.id, ''):<36} "
                  f"{len(words):>3}/{scripted:<3} panels  {sum(words):>7,} words  "
                  f"{statistics.mean(words):>5.0f} per panel")
        ordered = sorted(counts)
        print("\nShortest")
        for words, page, index in ordered[:5]:
            print(f"  {page:03d}-{index:02d}  {words:>4} words")
        print("\nLongest")
        for words, page, index in ordered[-5:][::-1]:
            print(f"  {page:03d}-{index:02d}  {words:>4} words")
    missing = [key for key in wanted if key not in present]
    if missing:
        print(f"\nUnwritten: {len(missing)} panels, first {missing[0][0]:03d}-{missing[0][1]:02d}")
    return 0


def assemble(continuous: bool) -> str:
    scripts = panels.read_scripts()
    model = crossref.build()
    present = found()
    parts: list[str] = ["# ZZ: NO CONSUMER", "", "*The novella.*", ""]
    pages_by_chapter: dict[str, list] = {}
    for page in model.pages:
        pages_by_chapter.setdefault(page.chapter, []).append(page)
    for chapter in model.chapters:
        pages = pages_by_chapter.get(chapter.id, [])
        if not pages:
            continue
        label = "Prologue" if chapter.id == "prologue" else (
            "Epilogue" if chapter.id == "epilogue" else f"Chapter {int(chapter.id)}")
        parts += [f"## {label} — {chapter.title}", ""]
        for page in pages:
            script = scripts.get(page.number)
            if script is None:
                continue
            if not continuous:
                parts += [f"### {page.number:03d} — {page.title}", ""]
            for index in range(1, script.count + 1):
                path = present.get((page.number, index))
                if path is None:
                    parts += [f"*[Panel {page.number:03d}-{index:02d} has no prose yet.]*", ""]
                    continue
                body = read_prose(path).body
                if body:
                    parts += [body, ""]
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="word census by chapter and panel")
    check = commands.add_parser("check", help="exit non-zero while prose and script disagree")
    check.add_argument("--strict", action="store_true", help="also fail on warnings")
    build = commands.add_parser("assemble", help="print the whole novella as one document")
    build.add_argument("--out", metavar="FILE", help="write here instead of standard output")
    build.add_argument("--continuous", action="store_true",
                       help="omit the per-page headings; chapters only")
    args = parser.parse_args(argv)
    if args.command == "report":
        return cmd_report()
    if args.command == "check":
        return cmd_check(args.strict)
    text = assemble(args.continuous)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {len(panels.WORD.findall(text)):,} words to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
