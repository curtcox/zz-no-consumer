#!/usr/bin/env python3
"""Make every story-page reference a link, in every edition that can render one.

The three-digit page number is the primary key of the whole project, and prose cites it
constantly -- "the split from page 010", "the escalation from page 011 to page 072". A
reader holding paper can turn to it. A reader holding anything with a hyperlink should be
able to follow it, and until now could not: the number was plain text everywhere.

This module owns that one job. It knows the grammar of a linked reference, it rewrites
prose into that grammar, and it fails when prose or a built artefact has drifted out of it.

    python3 scripts/pagelinks.py report                 # what is linked, and where to
    python3 scripts/pagelinks.py link                   # plan: what would change
    python3 scripts/pagelinks.py link --apply           # write it
    python3 scripts/pagelinks.py check                  # sources: every reference linked
    python3 scripts/pagelinks.py check --built          # docs/: same, after the build

The grammar, and why it is shaped this way
------------------------------------------

A single reference is linked whole::

    the split from [page 010](../00-prologue/010.md)

The keyword stays *inside* the brackets on purpose. `page 010` remains one contiguous
string, so every other regex in the repository that reads a page phrase -- the renumberer
in `pagination.py`, the parity assertions, the panel-reference scanner in `panels.py` --
keeps reading it. Linking the numeral alone would have broken all of them at once.

A range or a list cannot be one link, because it names more than one destination. There
the keyword stays outside and each number carries its own::

    [pages](.) is wrong; pages [039](039.md)-[041](041.md) is right

which is the one form that does break contiguity, so the grammars that care tolerate the
bracket forms too. `NUMBER` below is the shape they all share.

What is *not* linked is as deliberate as what is. `pagination.classify` already sorts a
page phrase into a reference, a foreign citation ("printed page 12" is somebody else's
book), a rule ("page 1 is a recto" is true whatever moves), and an ambiguous unpadded
number. Only a reference becomes a link. Headings are left alone -- a page's own title
line is not a pointer -- as are code fences and inline code, which quote a form rather
than name a page.

Targets are derived, never maintained. `link --apply` recomputes every target from the
current model, so a page that moves chapters is repaired by running the tool rather than
by a careful grep, and `check` is what says the repair is owed.

Standard library only, like everything else in `scripts/`.
"""

from __future__ import annotations

import argparse
import html as html_module
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]

# A resolver: a page number in, a href out, or None for "there is nowhere to point".
Href = Callable[[int], "str | None"]

# ---------------------------------------------------------------------------
# the grammar
# ---------------------------------------------------------------------------

# A page number that may already be wrapped in a Markdown link. Every regex in the
# repository that reads a page phrase is built from this, so that linked prose stays
# readable to the tools that renumber it.
NUMBER = r"(?:\[\s*)?\d{1,3}(?:\s*\]\([^)\s]*\))?"

# A story-page reference always names the keyword. Structured page numbers -- beat rows,
# ledger ranges, `**Pages:** 16-29`, the turn table -- never do, which is what keeps the
# rewriter away from tables it has no business editing.
PAGE_PHRASE = re.compile(
    r"(?P<printed>\b(?:printed|Printed|PRINTED)\s+)?"
    r"(?:\[\s*)?"
    r"\b(?P<kw>[Pp]ages?)(?P<sep>\s+|-)"
    rf"(?P<first>{NUMBER})"
    rf"(?P<rest>(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+|\s+to\s+|\s*[–—-]\s*){NUMBER})*)"
)

# Statements about an ordinal position in the abstract. They stay true whatever moves,
# because they describe the first page rather than a page that happens to be first.
RULE_PATTERNS = (
    re.compile(r"\bpage 1 is (?:an? )?(?:[\w-]+ )*recto", re.IGNORECASE),
)

REFERENCE, FOREIGN, RULE, AMBIGUOUS = "reference", "foreign", "rule", "ambiguous"

LINK = re.compile(r"\[(?P<label>[^\[\]\n]*)\]\((?P<target>[^)\s]*)\)")
LINK_TARGET = re.compile(r"\]\([^)\s]*\)")
PAGE_LABEL = re.compile(r"\A(?:(?P<kw>[Pp]ages?)\s+)?(?P<number>\d{3})\Z")
FENCE = re.compile(r"^\s*```")
CODE_SPAN = re.compile(r"`[^`]*`")


def spoken(text: str) -> str:
    """The text a reader hears: link targets removed, brackets left where they were.

    `[page 039](../039.md)` is the words *page 039*. Digit-counting and classification
    have to work on this rather than on the raw string, or a chapter directory named
    `00-prologue` becomes a two-digit page number.
    """
    return LINK_TARGET.sub("]", text)


def spoken_sub(pattern: str, repl, text: str) -> str:
    """Substitute in the spoken text only, leaving every link target untouched."""
    parts: list[str] = []
    position = 0
    for match in LINK_TARGET.finditer(text):
        parts.append(re.sub(pattern, repl, text[position:match.start()]))
        parts.append(match.group(0))
        position = match.end()
    parts.append(re.sub(pattern, repl, text[position:]))
    return "".join(parts)


def phrase_body(match: re.Match[str]) -> str:
    """The matched phrase without any `printed` prefix."""
    return match.group(0)[len(match.group("printed") or ""):]


def phrase_numbers(match: re.Match[str]) -> tuple[str, ...]:
    return tuple(re.findall(r"\d{1,3}", spoken(phrase_body(match))))


def is_pointer(match: re.Match[str], text: str) -> bool:
    """Does this phrase point at a page, or merely contain one?

    `same-event-as-page-003` is a continuity-check identifier. It names page 003 and moves
    with it -- `pagination.py` renumbers it like any other reference -- but it is a key in a
    record, not a sentence a reader can follow, so it is never linked.
    """
    start = match.start()
    return not (start and (text[start - 1] == "-" or text[start - 1].isalnum()))


def classify(match: re.Match[str], line: str) -> str:
    if match.group("printed"):
        return FOREIGN
    if any(pattern.search(line) for pattern in RULE_PATTERNS):
        return RULE
    digits = phrase_numbers(match)
    return REFERENCE if all(len(item) == 3 for item in digits) else AMBIGUOUS


# ---------------------------------------------------------------------------
# rewriting prose into the grammar
# ---------------------------------------------------------------------------
#
# One pass does three things at once, because doing them separately would fight itself:
# an existing page link is re-pointed at the target the model says it should have, a
# reference that is still plain text becomes a link, and every other link on the line is
# held aside so nothing ends up nested inside anything else.
#
# The result is idempotent: normalising already-normalised prose returns it unchanged,
# which is what lets `check` be a plain comparison rather than a second implementation.
# ---------------------------------------------------------------------------

HOLE_BASE = 0xE000
HOLE = re.compile("\x00(.)\x00")


def _split_code(line: str) -> list[tuple[bool, str]]:
    parts: list[tuple[bool, str]] = []
    position = 0
    for match in CODE_SPAN.finditer(line):
        parts.append((False, line[position:match.start()]))
        parts.append((True, match.group(0)))
        position = match.end()
    parts.append((False, line[position:]))
    return parts


def _normalize_chunk(chunk: str, line: str, href: Href) -> str:
    holes: list[str] = []

    def hole(text: str) -> str:
        holes.append(text)
        return f"\x00{chr(HOLE_BASE + len(holes) - 1)}\x00"

    def existing(match: re.Match[str]) -> str:
        """Re-point a page link; hold every other link aside untouched."""
        label = match.group("label")
        hit = PAGE_LABEL.match(label.strip())
        if not hit:
            return hole(match.group(0))
        target = href(int(hit.group("number")))
        if target is None:
            return label
        return hole(f"[{label}]({target})")

    chunk = LINK.sub(existing, chunk)

    def phrase(match: re.Match[str]) -> str:
        if classify(match, line) != REFERENCE or not is_pointer(match, chunk):
            return match.group(0)
        prefix = match.group("printed") or ""
        body = phrase_body(match)
        numbers = [int(item) for item in re.findall(r"\d{3}", spoken(body))]
        targets = [href(number) for number in numbers]
        if not targets or any(target is None for target in targets):
            return match.group(0)
        # Only a singular keyword can be swallowed by the link: `pages 038 to 040` names
        # two destinations, and `Pages 038` alone is still a plural that may be continued
        # by a phrase this grammar does not read.
        if len(numbers) == 1 and match.group("kw").lower() == "page":
            return prefix + hole(f"[{body}]({targets[0]})")
        remaining = iter(targets)
        return prefix + re.sub(
            r"\d{3}", lambda hit: hole(f"[{hit.group(0)}]({next(remaining)})"), body
        )

    chunk = PAGE_PHRASE.sub(phrase, chunk)
    return HOLE.sub(lambda match: holes[ord(match.group(1)) - HOLE_BASE], chunk)


def normalize(text: str, href: Href) -> str:
    """Return `text` with every story-page reference linked by `href`.

    `href` returning None for a page means "leave it as words" -- which is how the
    plain-text edition, and any surface with nowhere to point, gets the same prose with
    the links taken back out.
    """
    lines = text.splitlines(keepends=True)
    fenced = False
    in_front_matter = text.startswith("---\n")
    for index, line in enumerate(lines):
        if in_front_matter:
            # Front matter is a record, not prose: `page: 39` and `pages: [12, 45]` are
            # fields other tools parse.
            if index and line.rstrip("\n") == "---":
                in_front_matter = False
            continue
        if FENCE.match(line):
            fenced = not fenced
            continue
        # A heading names the page it sits on rather than pointing at another one.
        if fenced or line.lstrip().startswith("#"):
            continue
        lines[index] = "".join(
            chunk if is_code else _normalize_chunk(chunk, line, href)
            for is_code, chunk in _split_code(line)
        )
    return "".join(lines)


def scan(text: str) -> Iterable[tuple[int, str, re.Match[str]]]:
    """Every page phrase in prose this module would rewrite, with its line.

    The skips are `normalize`'s skips, which is the point: `report` and the artefact checks
    must not ask for a link where the rewriter would refuse to write one. Front matter is
    the interesting exclusion -- an appendix entry's `claim:` block is prose, and it is
    published, but it is published by `appendix.render`, which hands it to a renderer that
    links it there.
    """
    lines = text.splitlines()
    fenced = False
    in_front_matter = text.startswith("---")
    for index, line in enumerate(lines, 1):
        if in_front_matter:
            if index > 1 and line.rstrip() == "---":
                in_front_matter = False
            continue
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or line.lstrip().startswith("#"):
            continue
        for is_code, chunk in _split_code(line):
            if is_code:
                continue
            for match in PAGE_PHRASE.finditer(chunk):
                if is_pointer(match, chunk):
                    yield index, line, match


def unlink(text: str) -> str:
    """The same prose with page links flattened back to words, for editions without them."""
    return normalize(text, lambda page: None)


# ---------------------------------------------------------------------------
# where a page lives
# ---------------------------------------------------------------------------

# Which edition a file's page references point into. A reader inside the novella stays in
# the novella; a reader inside a page script stays in the script; the appendix serves both
# editions and names one, because it lists the other explicitly under every entry.
NOVELLA_TREE = "content/novella/"
SCRIPT_TREE = "content/pages/"
APPENDIX_TREE = "content/appendix/"


def chapter_directories() -> dict[int, str]:
    """Page number to the novella chapter directory holding its prose."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import crossref  # noqa: E402  the page/chapter graph is modelled once, there

    model = crossref.build()
    directories = {chapter.id: (chapter.directory or chapter.id) for chapter in model.chapters}
    return {page.number: directories.get(page.chapter, page.chapter) for page in model.pages}


def source_target(relative: str, page: int, directories: dict[int, str]) -> str | None:
    """The repository path a reference in `relative` should point at."""
    if page not in directories:
        return None
    if relative.startswith(SCRIPT_TREE):
        return f"{SCRIPT_TREE}{page:03d}.md"
    if relative.startswith(NOVELLA_TREE) or relative.startswith(APPENDIX_TREE):
        return f"{NOVELLA_TREE}{directories[page]}/{page:03d}.md"
    return f"{SCRIPT_TREE}{page:03d}.md"


def source_href(relative: str, directories: dict[int, str]) -> Href:
    """A resolver for one source file: relative paths, so GitHub and any editor follow them."""
    directory = posixpath.dirname(relative) or "."

    def href(page: int) -> str | None:
        target = source_target(relative, page, directories)
        return None if target is None else posixpath.relpath(target, directory)

    return href


def governed_files() -> list[Path]:
    """The hand-written prose whose page references this tool maintains."""
    return sorted(path for path in (ROOT / "content").rglob("*.md") if path.is_file())


# ---------------------------------------------------------------------------
# reading a built artefact back
# ---------------------------------------------------------------------------
#
# The source check is a comparison against what this module would write. A built artefact
# has been through a renderer, so the question there is weaker and more useful: is every
# spoken page reference inside something a reader can follow? Text already inside an
# anchor passes however it got there, headings and non-rendered metadata are exempt for
# the same reason they are exempt in source, and the plain-text download is exempt
# entirely -- it has no links to be missing.
# ---------------------------------------------------------------------------

ANCHOR = re.compile(r"<a\b[^>]*>.*?</a>", re.IGNORECASE | re.DOTALL)
# Code quotes a form rather than naming a page -- `page-064-ranking-is-disclosed-as-…` is a
# continuity-check key -- which is the same reason `normalize` skips inline code and fences.
DROPPED = re.compile(
    r"<(script|style|title|desc|code|pre|kbd|samp|h[1-6])\b[^>]*>.*?</\1>|<!--.*?-->",
    re.IGNORECASE | re.DOTALL,
)
TAG = re.compile(r"<[^>]+>")


OWN_PAGE = re.compile(r"(?:^|/)pages/(\d{3})(?:/|\.)")
CHAPTER_ROUTE = re.compile(r"(?:^|/)(?:novella|viewer/chapters)/([\w-]+)/")

_CHAPTER_BOUNDS: dict[str, set[int]] = {}


def chapter_bounds() -> dict[str, set[int]]:
    """The first and last page of each chapter, by directory and by id."""
    if not _CHAPTER_BOUNDS:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import crossref  # noqa: E402

        for chapter in crossref.build().chapters:
            pair = {chapter.first_page, chapter.last_page}
            _CHAPTER_BOUNDS[chapter.id] = pair
            if chapter.directory:
                _CHAPTER_BOUNDS[chapter.directory] = pair
    return _CHAPTER_BOUNDS


def route_identity(relative: str) -> set[int]:
    """The page numbers a built route names as its own subject rather than as destinations.

    A page's route says which page it is; a chapter's route says which pages it covers.
    Neither is a pointer -- there is nowhere for `Page 042` on page 042 to go -- and both
    are the same exemption a heading gets in the sources.
    """
    page = OWN_PAGE.search(relative)
    if page:
        return {int(page.group(1))}
    chapter = CHAPTER_ROUTE.search(relative)
    if chapter:
        # The bounds pair only: a reference to a page *inside* the chapter is still a
        # reference, and the whole point of this check is to notice one that is not a link.
        return chapter_bounds().get(chapter.group(1), set())
    return set()


def unlinked_html(markup: str, identity: set[int] | None = None) -> list[str]:
    """Every page reference in rendered markup that a reader cannot follow."""
    text = DROPPED.sub(" ", markup)
    text = ANCHOR.sub(" ", text)
    # A newline rather than a space: a tag is a boundary, and `<dt>Page</dt><dd>001 of 118`
    # is a field label beside a number rather than a reference to page 001.
    text = html_module.unescape(TAG.sub("\n", text))
    return unlinked_text(text, identity)


def unlinked_text(text: str, identity: set[int] | None = None) -> list[str]:
    findings: list[str] = []
    for line in text.splitlines():
        for match in PAGE_PHRASE.finditer(line):
            if classify(match, line) != REFERENCE or not is_pointer(match, line):
                continue
            if LINK_TARGET.search(phrase_body(match)):
                continue
            numbers = {int(item) for item in phrase_numbers(match)}
            # A route names its own subject: `Page 042` on page 042, `Pages 016-029` on
            # chapter 01. That is a label, the identity a heading carries, not a pointer.
            if identity and numbers == identity:
                continue
            findings.append(match.group(0).strip())
    return findings


def unlinked_markdown(text: str) -> list[str]:
    """A Markdown artefact: a reference passes when its numbers carry their own targets."""
    findings: list[str] = []
    for _, line, match in scan(text):
        if classify(match, line) != REFERENCE:
            continue
        body = phrase_body(match)
        if len(LINK_TARGET.findall(body)) < len(re.findall(r"\d{3}", spoken(body))):
            findings.append(match.group(0).strip())
    return findings


def built_artefacts(out: Path) -> Iterable[tuple[str, list[str]]]:
    """Every built file that can carry a link, with the references it failed to link."""
    for path in sorted(out.rglob("*.html")):
        relative = str(path.relative_to(ROOT))
        yield relative, unlinked_html(path.read_text(encoding="utf-8"), route_identity(relative))
    for path in sorted(out.rglob("*.md")):
        yield str(path.relative_to(ROOT)), unlinked_markdown(path.read_text(encoding="utf-8"))
    for path in sorted(out.rglob("*.epub")):
        findings: list[str] = []
        with zipfile.ZipFile(path) as archive:
            for name in sorted(archive.namelist()):
                if name.endswith((".xhtml", ".html")):
                    findings += unlinked_html(archive.read(name).decode("utf-8"))
        yield str(path.relative_to(ROOT)), findings


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


def planned() -> list[tuple[Path, str, str]]:
    """Every governed file whose prose is not in the grammar, with the text it should hold."""
    directories = chapter_directories()
    changes: list[tuple[Path, str, str]] = []
    for path in governed_files():
        relative = str(path.relative_to(ROOT))
        text = path.read_text(encoding="utf-8")
        wanted = normalize(text, source_href(relative, directories))
        if wanted != text:
            changes.append((path, text, wanted))
    return changes


def changed_lines(before: str, after: str) -> list[tuple[int, str]]:
    return [
        (number, new.strip())
        for number, (old, new) in enumerate(zip(before.splitlines(), after.splitlines()), 1)
        if old != new
    ]


def cmd_link(apply: bool) -> int:
    changes = planned()
    if not changes:
        print("Every story-page reference in content/ is already a link.")
        return 0
    sites = 0
    for path, before, after in changes:
        lines = changed_lines(before, after)
        sites += len(lines)
        print(f"\n{path.relative_to(ROOT)}  ({len(lines)} lines)")
        for number, text in lines[:4]:
            print(f"  {number:>5}  {text[:110]}")
        if len(lines) > 4:
            print(f"        … {len(lines) - 4} more")
        if apply:
            path.write_text(after, encoding="utf-8")
    verb = "Linked" if apply else "Would link"
    print(f"\n{verb} {sites} lines in {len(changes)} files.")
    if not apply:
        print("Nothing was written. Re-run with --apply.")
    return 0


def cmd_check(built: bool, out: Path) -> int:
    if not built:
        changes = planned()
        if not changes:
            print(f"Page links: every reference in {len(governed_files())} content files is a link.")
            return 0
        print("Page references that are not links, or that point at the wrong page:\n")
        for path, before, after in changes:
            for number, text in changed_lines(before, after):
                print(f"  {path.relative_to(ROOT)}:{number}  {text[:100]}")
        print("\nRun: python3 scripts/pagelinks.py link --apply")
        return 1
    if not out.is_dir():
        print(f"{out.relative_to(ROOT)} does not exist; run scripts/build-site.py first.")
        return 1
    failures = [(name, findings) for name, findings in built_artefacts(out) if findings]
    if not failures:
        print(f"Page links: every reference in {out.relative_to(ROOT)} is a link.")
        return 0
    print("Built artefacts printing a page reference a reader cannot follow:\n")
    for name, findings in failures:
        shown = ", ".join(sorted(set(findings))[:6])
        print(f"  {name}  ({len(findings)}) {shown}")
    return 1


def cmd_report() -> int:
    directories = chapter_directories()
    counts: dict[str, int] = {}
    linked = 0
    total = 0
    for path in governed_files():
        for _, line, match in scan(path.read_text(encoding="utf-8")):
            kind = classify(match, line)
            counts[kind] = counts.get(kind, 0) + 1
            if kind != REFERENCE:
                continue
            total += 1
            if LINK_TARGET.search(phrase_body(match)):
                linked += 1
    print(f"{sum(counts.values())} page phrases in {len(governed_files())} content files")
    for kind in (REFERENCE, RULE, FOREIGN, AMBIGUOUS):
        print(f"  {kind:<10} {counts.get(kind, 0):>4}")
    print(f"\n{linked} of {total} references are links "
          f"({0 if not total else round(100 * linked / total)}%).")
    print(f"{len(directories)} pages can be pointed at.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="how many references there are, and how many are links")
    link = commands.add_parser("link", help="rewrite content prose into the linked grammar")
    link.add_argument("--apply", action="store_true", help="write the plan instead of printing it")
    check = commands.add_parser("check", help="exit non-zero while a reference is not a link")
    check.add_argument("--built", action="store_true",
                       help="check the built site and downloads rather than the sources")
    check.add_argument("--out", metavar="DIR", default="docs",
                       help="the build to check with --built (default: docs)")
    args = parser.parse_args(argv)

    if args.command == "report":
        return cmd_report()
    if args.command == "link":
        return cmd_link(args.apply)
    return cmd_check(args.built, ROOT / args.out)


if __name__ == "__main__":
    raise SystemExit(main())
