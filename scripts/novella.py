#!/usr/bin/env python3
"""Measure, check, and assemble the novella: the book told again in prose, one file per page.

The graphic novel's canonical unit is the page script in ``content/pages/NNN.md``. The novella
renders the same story in continuous prose and lives beside it as ``content/novella/<chapter>/
NNN.md`` -- one file per story page, in chapter directories named for the chapter briefs in
``content/chapters/``. Each file carries page, chapter, sequence, title and source in front
matter, then an ``# N. Title`` heading, then the prose.

The unit is the page and not the panel, and that is the track's whole design. A page script is
a composition: frames, actions, screen text, and the provenance of each. The prose is the same
events and the same argument told as narrative, so it takes the page's beats and drops the
page's geometry. The vocabulary check below enforces exactly that -- prose that says *panel*
is describing the artwork instead of the story.

    python3 scripts/novella.py report              # word census, per chapter and per page
    python3 scripts/novella.py check               # exit non-zero while prose and script disagree
    python3 scripts/novella.py assemble            # the whole novella as one Markdown document
    python3 scripts/novella.py assemble --out FILE --continuous

``check`` holds the prose tree to the page scripts: every scripted page has exactly one prose
file, every file sits in its chapter's directory, front matter agrees with the script on page,
chapter, sequence and title, the heading numbers the page, the body is prose rather than a
stub, and no file describes panels. It does not judge length; ``report`` measures it. The
novella was commissioned to average about a manuscript page per story page, varying widely by
beat.

The story contract's truth rules bind the prose exactly as they bind the script: it may not
invent an incident fact, quote raw agent text, or supply an agent's interior state. Those are
editorial and are not checkable here.

Renumbering is not this script's job. ``scripts/pagination.py`` moves the prose files with
their pages -- between chapter directories when a page changes chapter -- and rewrites their
front matter and headings. Panel operations do not touch this tree at all; the unit is the
page, so ``scripts/panels.py`` has nothing to move.
"""

from __future__ import annotations

from book_metadata import TITLE

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

MANUSCRIPT_PAGE = 250
HEADING = re.compile(r"^# (\d+)\.\s+(.+?)\s*$", re.MULTILINE)

# The track exists to tell the story without describing the artwork, so the words that name
# the comic's geometry are the ones the prose may not use.
#
# Two words that look like they belong here do not. `page` is deliberately absent: the prose
# cites its own page numbers and the epilogue depends on it. `frame` is absent because the
# book argues in it -- *the interpreter begins inside the actor's frame*, *a frame that says
# whose they are*, *the saga teaches the frame* -- and a check that fires on the load-bearing
# vocabulary of Chapter 5 is a check an editor learns to skim. What is left fires only on
# geometry.
PANEL_VOCABULARY = re.compile(r"\b(?:panels?|gutters?|splash page|inset panel)\b", re.IGNORECASE)

# A stub written by an insert, before anyone has drafted the page.
STUB = re.compile(r"^\[.*\]$", re.DOTALL)


@dataclass(frozen=True)
class Prose:
    path: str
    directory: str
    page: int | None
    chapter: str
    sequence: str
    title: str
    source: str
    heading: tuple[int, str] | None
    body: str
    metadata: str

    @property
    def words(self) -> int:
        return len(panels.WORD.findall(self.body))


def prose_path(directory: str, page: int) -> Path:
    return BASE / directory / f"{page:03d}.md"


def expected(model: crossref.CrossReference) -> dict[int, Path]:
    """Where each story page's prose belongs, keyed by page number."""
    directories = {chapter.id: chapter.directory for chapter in model.chapters}
    return {
        page.number: prose_path(directories.get(page.chapter, page.chapter), page.number)
        for page in model.pages
    }


def found() -> dict[int, list[Path]]:
    """Every prose file on disk, keyed by the page its filename names.

    A list rather than a path, because a page renamed by hand into a second chapter directory
    is the failure this track is most exposed to and silently keeping one copy would hide it.
    """
    files: dict[int, list[Path]] = {}
    if not BASE.is_dir():
        return files
    for child in sorted(BASE.rglob("*.md")):
        if child.parent == BASE or not re.fullmatch(r"\d{3}\.md", child.name):
            continue
        files.setdefault(int(child.stem), []).append(child)
    return files


def stray_files() -> list[Path]:
    """Anything under the tree that is not a chapter directory holding page files."""
    strays: list[Path] = []
    if not BASE.is_dir():
        return strays
    known = {chapter.directory for chapter in crossref.read_chapters()}
    for child in sorted(BASE.rglob("*")):
        if child.is_dir():
            if child.parent == BASE and child.name not in known:
                strays.append(child)
            continue
        if child.parent == BASE:
            if child.name != "README.md":
                strays.append(child)
        elif not re.fullmatch(r"\d{3}\.md", child.name):
            strays.append(child)
    return strays


def read_prose(path: Path) -> Prose:
    text = path.read_text(encoding="utf-8")
    metadata = crossref.front_matter(text) or ""

    def value(key: str) -> str:
        match = re.search(rf"^{key}:\s*(.*?)\s*$", metadata, re.MULTILINE)
        return match.group(1).strip().strip('"') if match else ""

    raw_page = value("page")
    body = text
    if metadata:
        body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    heading_match = HEADING.search(body)
    heading = (int(heading_match.group(1)), heading_match.group(2)) if heading_match else None
    body = HEADING.sub("", body, count=1).strip()
    return Prose(
        path=str(path.relative_to(ROOT)),
        directory=path.parent.name,
        page=int(raw_page) if raw_page.isdigit() else None,
        chapter=value("chapter"),
        sequence=value("sequence"),
        title=value("title"),
        source=value("source"),
        heading=heading,
        body=body,
        metadata=metadata,
    )


@dataclass(frozen=True)
class Note:
    severity: str
    kind: str
    subject: str
    message: str


def audit(model: crossref.CrossReference) -> list[Note]:
    notes: list[Note] = []
    wanted = expected(model)
    present = found()
    pages = {page.number: page for page in model.pages}
    directories = {chapter.id: chapter.directory for chapter in model.chapters}

    for number, path in sorted(wanted.items()):
        if number not in present:
            notes.append(Note("error", "prose-missing", str(path.relative_to(ROOT)),
                              f"page {number:03d} is scripted and has no prose"))
    for number, paths in sorted(present.items()):
        if number not in wanted:
            for path in paths:
                notes.append(Note("error", "prose-orphaned", str(path.relative_to(ROOT)),
                                  "names a page no manifest declares"))
        elif len(paths) > 1:
            notes.append(Note("error", "prose-duplicated", f"page {number:03d}",
                              "has prose in " + ", ".join(
                                  str(path.relative_to(ROOT)) for path in paths)))
    for stray in stray_files():
        notes.append(Note("warning", "prose-stray", str(stray.relative_to(ROOT)),
                          "is not a chapter directory or a page file"))

    for number, paths in sorted(present.items()):
        if number not in wanted:
            continue
        page = pages[number]
        prose = read_prose(paths[0])

        if prose.page != number:
            notes.append(Note("error", "front-matter-disagrees", prose.path,
                              f"says page {prose.page}; the path says {number:03d}"))
        for name, mine, theirs in (("chapter", prose.chapter, page.chapter),
                                   ("sequence", prose.sequence, page.sequence),
                                   ("title", prose.title, page.title)):
            if mine != theirs:
                severity = "warning" if name == "title" else "error"
                notes.append(Note(severity, f"{name}-disagrees", prose.path,
                                  f"says {name} {mine!r}; the script says {theirs!r}"))
        wanted_directory = directories.get(page.chapter, page.chapter)
        if prose.directory != wanted_directory:
            notes.append(Note("error", "chapter-directory-wrong", prose.path,
                              f"sits in {prose.directory!r}; page {number:03d} belongs to "
                              f"chapter {page.chapter!r}, whose directory is "
                              f"{wanted_directory!r}"))
        expected_source = f"content/pages/{number:03d}.md"
        if prose.source != expected_source:
            notes.append(Note("error", "source-wrong", prose.path,
                              f"points at {prose.source!r}; its script is {expected_source!r}"))

        if prose.heading is None:
            notes.append(Note("error", "heading-missing", prose.path,
                              "has no `# N. Title` heading"))
        else:
            if prose.heading[0] != number:
                notes.append(Note("error", "heading-disagrees", prose.path,
                                  f"is headed {prose.heading[0]}; the path says {number}"))
            if prose.heading[1] != page.title:
                notes.append(Note("warning", "heading-title-disagrees", prose.path,
                                  f"is headed {prose.heading[1]!r}; the script titles the page "
                                  f"{page.title!r}"))

        # The prose edition ships as its own target and shares the page key, so a quotation
        # here is held to the same rule as one in the script. crossref owns the model; this
        # only supplies the file and whether its page has locked.
        locked = page.status == "locked"
        string_errors, string_warnings = crossref.audit_exact_strings(
            prose.metadata, prose.path, locked=locked
        )
        def without_path(message: str, where: str = prose.path) -> str:
            # crossref prefixes the file it was given; Note prints the path itself.
            return message.removeprefix(where).lstrip(": ").strip() or message

        for message in string_errors:
            notes.append(Note("error", "exact-string-registration",
                              prose.path, without_path(message)))
        for message in string_warnings:
            notes.append(Note("warning", "exact-string-undispositioned",
                              prose.path, without_path(message)))

        if prose.words == 0:
            notes.append(Note("error", "prose-empty", prose.path, "has no prose after its heading"))
        elif STUB.match(prose.body):
            notes.append(Note("warning", "prose-stub", prose.path,
                              "is a placeholder left by an insert and has not been written"))
        for match in PANEL_VOCABULARY.finditer(prose.body):
            notes.append(Note("warning", "describes-panels", prose.path,
                              f"says “{match.group(0)}”; the prose tells the story and the "
                              "script describes the artwork"))
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
    model = crossref.build()
    notes = audit(model)
    counts = print_notes(notes)
    blocking = counts["error"] + (counts["warning"] if strict else 0)
    if blocking:
        print(f"\nNovella check failed: {blocking} blocking findings.")
        return 1
    written = sum(1 for paths in found().values() if paths)
    print(f"\nNovella check passed: {written} prose files for {len(model.pages)} story pages "
          f"in {len(model.chapters)} chapter directories.")
    return 0


def cmd_report() -> int:
    model = crossref.build()
    chapter_title = {chapter.id: chapter.title for chapter in model.chapters}
    chapter_of = {page.number: page.chapter for page in model.pages}
    title_of = {page.number: page.title for page in model.pages}
    wanted = expected(model)
    present = found()
    counts: list[tuple[int, int]] = []
    per_chapter: dict[str, list[int]] = {}
    for number in sorted(wanted):
        paths = present.get(number)
        if not paths:
            continue
        words = read_prose(paths[0]).words
        counts.append((words, number))
        per_chapter.setdefault(chapter_of.get(number, "?"), []).append(words)
    total_words = sum(item[0] for item in counts)
    print(f"{len(counts)} of {len(wanted)} story pages have prose; "
          f"{total_words:,} words in all, about {total_words / MANUSCRIPT_PAGE:,.0f} "
          f"manuscript pages at {MANUSCRIPT_PAGE} words.")
    if counts:
        values = [item[0] for item in counts]
        print(f"\nPer page: mean {statistics.mean(values):.0f}, median "
              f"{statistics.median(values):.0f}, shortest {min(values)}, longest {max(values)}.")
        print("\nBy chapter")
        for chapter in model.chapters:
            words = per_chapter.get(chapter.id, [])
            if not words:
                continue
            scripted = sum(1 for number in wanted if chapter_of.get(number) == chapter.id)
            print(f"  {chapter.directory:<36} {len(words):>3}/{scripted:<3} pages  "
                  f"{sum(words):>7,} words  {statistics.mean(words):>5.0f} per page")
        ordered = sorted(counts)
        print("\nShortest")
        for words, number in ordered[:5]:
            print(f"  {number:03d}  {words:>4} words  {title_of.get(number, '')}")
        print("\nLongest")
        for words, number in ordered[-5:][::-1]:
            print(f"  {number:03d}  {words:>4} words  {title_of.get(number, '')}")
    missing = [number for number in wanted if number not in present]
    if missing:
        print(f"\nUnwritten: {len(missing)} pages, first {missing[0]:03d}")
    return 0


def assemble(continuous: bool) -> str:
    model = crossref.build()
    present = found()
    parts: list[str] = [f"# {TITLE}", "", "*The novella.*", ""]
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
            paths = present.get(page.number)
            if not paths:
                parts += [f"*[Page {page.number:03d} has no prose yet.]*", ""]
                continue
            if not continuous:
                parts += [f"### {page.number}. {page.title}", ""]
            body = read_prose(paths[0]).body
            if body:
                parts += [body, ""]
    return "\n".join(parts).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="word census by chapter and page")
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
