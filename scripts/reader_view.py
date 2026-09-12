#!/usr/bin/env python3
"""Reader-facing views of the book: what a reader is given, and nothing a reader is not.

The synthetic reader protocol (``design/synthetic-reader-protocol.md``) hands a stateless model
the book and asks it what the book says. The protocol is only interpretable if the model sees
what a reader sees -- page and chapter titles, the picture, the lettering -- and none of the
apparatus: front matter, page purposes, provenance lines, references, production notes, page
notes, the beat sheet. This module is that boundary, built as views over the parsers that
already own each edition rather than as a second parser.

- **The script** is read through ``panels.py``: its section regexes find the panels, and its
  ``visible_text`` supplies every lettered line, so the extractor and the lettered-word counter
  cannot disagree about what is lettered. ``check`` holds them to the same total.
- **The novella and the appendix** are the plain-text download ``build-site.py`` publishes,
  produced by the builder's own functions. That file is the thing a reader downloads.

The script has no pictures, so a panel's ``Frame`` stands in for its art. That is a
substitution with a known bias -- frames are written for an artist and sometimes say what a
drawing would only show -- and ``--view`` exists so an arm can record which substitution it
used:

    lettering   titles and lettering only
    frames      plus each panel's Frame, as the picture
    full        plus each panel's Action line (the protocol's reading, and the default)

    python3 scripts/reader_view.py script --pages 001-015 [--view full]
    python3 scripts/reader_view.py novella
    python3 scripts/reader_view.py appendix
    python3 scripts/reader_view.py arms --out 256t/synthetic-readers/arms   # A0-A5 + manifest
    python3 scripts/reader_view.py check
    python3 scripts/reader_view.py report

Standard library only. This tool writes nothing tracked; ``arms`` writes under the ignored
``256t/`` vault, beside the transcripts the protocol keeps there. It is not in the CI sequence,
because the protocol it serves is optional external tooling -- but ``check`` needs no network
and no key, so run it before building arms.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crossref  # noqa: E402
import panels  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "design" / "synthetic-reader-protocol.md"
VIEWS = ("lettering", "frames", "full")

FIELD = re.compile(r"^\*\*(?P<name>[^*]+?):\*\*[ \t]*(?P<rest>.*)$")
READER_SECTIONS = (panels.BANNER_HEADING,)
APPARATUS_SECTIONS = ("## Page purpose", "## Page notes")
# Fields a reader never sees. Anything neither here nor lettered nor Frame/Action is reported,
# because a new field is a new decision about the boundary, not something to guess.
APPARATUS_FIELDS = ("Provenance", "References", "Note")

# Strings that mean apparatus reached the reader's text. Registered source keys with a hyphen
# are added at run time; the rest (METR, PUBLIC, JFROG) are ordinary words to a reader. The
# words "provenance" and "continuity" are not markers: Curt's provenance tags are in the story.
APPARATUS_MARKERS = re.compile(
    r"page purpose|page notes|\.md\b|\]\(|NONE-FICTION|PROJECT-INFERENCE",
    re.IGNORECASE,
)

# Arms A0-A5 of the protocol. A6-A8 are built by hand from these, with the damage recorded.
ARMS = {
    "A0": "nothing; the questions only",
    "A1": "stripped script, pages 001-015",
    "A2": "stripped script, pages 001-056",
    "A3": "stripped script, all pages",
    "A4": "the novella, all pages",
    "A5": "stripped script, all pages, plus the appendix",
}


def _builder():
    spec = importlib.util.spec_from_file_location("reader_view_builder", ROOT / "scripts/build-site.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def flatten(text: str) -> str:
    """Markdown to the words it renders as. Link targets are addresses, not reading."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"\1", text)
    return " ".join(text.split())


def lettered_label(name: str) -> str | None:
    """The reader-facing label for a lettered field, or None if the field is not lettered."""
    if not ("**" + name).startswith(panels.VISIBLE_HEADERS):
        return None
    base, _, qualifier = (part.strip() for part in name.partition("—"))
    base = re.sub(r"\s*\(.*\)$", "", base)
    # "across panels 1–3" places a caption on the page; it is lettering direction, not text.
    if re.match(r"(across )?panels? \d", qualifier):
        qualifier = ""
    if base in ("Dialogue", "Left dialogue", "Right dialogue"):
        side = {"Left dialogue": " (left)", "Right dialogue": " (right)"}.get(base, "")
        return (qualifier or "Speaker") + side
    if base == "Screen / system text":
        return f"Screen ({qualifier})" if qualifier else "Screen"
    if base == "Dossier tag":
        return "Tag"
    return base if not qualifier else f"{base} ({qualifier})"


@dataclass
class PageView:
    number: int
    text: str
    lettered_words: int
    problems: list[str] = field(default_factory=list)


def fields_of(body: str) -> list[tuple[str, str]]:
    """(name, block) pairs; a block runs from its field line to the next field line."""
    out: list[tuple[str, list[str]]] = []
    for line in body.splitlines():
        match = FIELD.match(line)
        if match:
            out.append((match.group("name").strip(), [line]))
        elif out:
            out[-1][1].append(line)
    return [(name, "\n".join(lines)) for name, lines in out]


def script_page(number: int, source: str, view: str) -> PageView:
    body = source.split("\n---\n", 1)[1] if source.startswith("---\n") else source
    heads = list(panels.SECTION_HEADING.finditer(body))
    lines: list[str] = []
    problems: list[str] = []
    words = 0
    for position, head in enumerate(heads):
        end = heads[position + 1].start() if position + 1 < len(heads) else len(body)
        section = body[head.start():end]
        heading = section.splitlines()[0].strip()
        if heading.startswith(APPARATUS_SECTIONS):
            continue
        if heading.startswith(READER_SECTIONS):
            for text in panels.visible_text(section):
                words += len(panels.WORD.findall(text))
                lines.append(f"Banner, on every panel: {text}")
            continue
        panel = panels.PANEL_HEADING.match(heading) or panels.GROUPED_HEADING.match(heading)
        if not panel:
            problems.append(f"unknown section {heading!r}")
            continue
        lines += ["", heading.lstrip("# ")]
        for name, block in fields_of(section.split("\n", 1)[1] if "\n" in section else ""):
            label = lettered_label(name)
            if label:
                raw = panels.visible_text(block)
                # Counted as panels.py counts, so the totals agree; shown as a reader reads it.
                words += sum(len(panels.WORD.findall(text)) for text in raw)
                texts = [flatten(text) for text in raw]
                if len(texts) == 1:
                    lines.append(f"{label}: {texts[0]}")
                else:
                    lines.append(f"{label}:")
                    lines += [f"  {text}" for text in texts]
            elif name == "Frame":
                if view in ("frames", "full"):
                    lines.append(f"Picture: {flatten(block.split(':**', 1)[1])}")
            elif name == "Action":
                if view == "full":
                    lines.append(f"Action: {flatten(block.split(':**', 1)[1])}")
            elif name.split(" ")[0] not in APPARATUS_FIELDS:
                problems.append(f"unknown field {name!r}")
    return PageView(number, "\n".join(lines).strip(), words, problems)


def page_range(spec: str | None, available: list[int]) -> list[int]:
    if not spec:
        return available
    first, _, last = spec.partition("-")
    low, high = int(first), int(last or first)
    return [number for number in available if low <= number <= high]


def script_text(pages_spec: str | None = None, view: str = "full") -> tuple[str, list[PageView]]:
    model = crossref.build()
    chapters = {chapter.id: chapter for chapter in model.chapters}
    scripts = {page.number: page for page in model.pages}
    numbers = page_range(pages_spec, sorted(scripts))
    parts: list[str] = []
    views: list[PageView] = []
    chapter_id = None
    for number in numbers:
        page = scripts[number]
        if page.chapter != chapter_id:
            chapter_id = page.chapter
            label = "Prologue" if chapter_id == "prologue" else (
                "Epilogue" if chapter_id == "epilogue" else f"Chapter {int(chapter_id)}")
            banner = f"{label} — {chapters[chapter_id].title}"
            parts += ["", banner.upper(), "=" * len(banner), ""]
        source = (ROOT / "content" / "pages" / f"{number:03d}.md").read_text(encoding="utf-8")
        page_view = script_page(number, source, view)
        views.append(page_view)
        parts += [f"PAGE {number:03d} — {page.title}", "", page_view.text, "", ""]
    return "\n".join(parts).strip() + "\n", views


def novella_text() -> str:
    builder = _builder()
    return builder.novella_plain_text(builder.novella_chapters())


def appendix_text() -> str:
    builder = _builder()
    model = builder.appendix_module.build()
    return builder.appendix_plain_text(builder.pagelinks.unlink(builder.appendix_markdown(model)))


def _protocol_terms(heading: str) -> list[str]:
    text = PROTOCOL.read_text(encoding="utf-8")
    match = re.search(r"\*\*" + re.escape(heading) + r".*?\n\n(.+?)\n\n", text, flags=re.DOTALL)
    if not match:
        raise SystemExit(f"{PROTOCOL.relative_to(ROOT)}: {heading!r} term list not found")
    return [term.strip() for term in " ".join(match.group(1).split()).split("·") if term.strip()]


def leakage_terms() -> list[str]:
    """The protocol's leakage list, read from the protocol so there is one copy of it."""
    return _protocol_terms("Leakage flag")


def text_supplied_terms() -> list[str]:
    """The leakage terms the protocol records as present in the story's own reader text."""
    return _protocol_terms("Text-supplied terms")


def term_hits(text: str, terms: list[str]) -> dict[str, int]:
    hits = {}
    for term in terms:
        count = len(re.findall(r"\b" + re.escape(term).replace(r"\ ", r"[\s-]+") + r"\b", text, re.IGNORECASE))
        if count:
            hits[term] = count
    return hits


def words(text: str) -> int:
    return len(panels.WORD.findall(text))


def estimated_tokens(text: str) -> int:
    # An estimate for budgeting, not a tokenizer: about four characters per token in English.
    return round(len(text) / 4)


def build_arms(view: str) -> dict[str, str]:
    a1, _ = script_text("001-015", view)
    a2, _ = script_text("001-056", view)
    a3, _ = script_text(None, view)
    return {
        "A0": "",
        "A1": a1,
        "A2": a2,
        "A3": a3,
        "A4": novella_text(),
        "A5": a3 + "\n\n" + appendix_text(),
    }


def git(*args: str) -> str:
    result = subprocess.run(["git", "--no-optional-locks", *args], cwd=ROOT,
                            capture_output=True, text=True)
    return result.stdout.strip()


def cmd_arms(out: Path, view: str) -> int:
    out.mkdir(parents=True, exist_ok=True)
    terms = leakage_terms()
    manifest = {
        "made": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "tree_dirty_paths": git("status", "--short", "--", "content", "scripts", "design").splitlines(),
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "view": view,
        "arms": {},
    }
    for arm, text in build_arms(view).items():
        path = out / f"{arm}.txt"
        path.write_text(text, encoding="utf-8")
        manifest["arms"][arm] = {
            "given": ARMS[arm],
            "file": path.name,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "words": words(text),
            "estimated_tokens": estimated_tokens(text),
            "leakage_terms": term_hits(text, terms),
        }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    for arm, row in manifest["arms"].items():
        print(f"  {arm}  {row['words']:>7,} words  ~{row['estimated_tokens']:>7,} tokens  {row['given']}")
    print(f"Wrote {len(manifest['arms'])} arms and manifest.json to {out}")
    return 0


def cmd_check(view: str) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    text, views = script_text(None, view)
    counted = {number: script.words for number, script in panels.read_scripts().items()}
    for page_view in views:
        errors += [f"page {page_view.number:03d}: {problem}" for problem in page_view.problems]
        if page_view.lettered_words != counted.get(page_view.number):
            errors.append(f"page {page_view.number:03d}: extractor letters {page_view.lettered_words} "
                          f"words, panels.py counts {counted.get(page_view.number)}")
    total = sum(page_view.lettered_words for page_view in views)
    if total != sum(counted.values()):
        errors.append(f"lettered words: extractor {total}, panels.py {sum(counted.values())}")

    keys = [key for key in crossref.build().sources if "-" in key]
    markers = re.compile(APPARATUS_MARKERS.pattern + "|" + "|".join(rf"\b{re.escape(k)}\b" for k in keys),
                         re.IGNORECASE)
    for number, line in ((v.number, line) for v in views for line in v.text.splitlines()):
        hit = markers.search(line)
        if hit:
            errors.append(f"page {number:03d}: apparatus {hit.group(0)!r} in reader text: {line[:90]}")

    # The protocol's text-supplied list must be exactly the leakage terms the story carries.
    terms, supplied = leakage_terms(), set(text_supplied_terms())
    for label, edition in (("script", text), ("novella", novella_text())):
        found = set(term_hits(edition, terms))
        if found - supplied:
            warnings.append(f"{label}: leakage terms in the reader text but not recorded as "
                            f"text-supplied in the protocol: {sorted(found - supplied)}")
        if supplied - found:
            warnings.append(f"{label}: recorded as text-supplied but absent from the reader text: "
                            f"{sorted(supplied - found)}")

    for message in errors:
        print(f"error: {message}")
    for message in warnings:
        print(f"warning: {message}")
    print(f"Reader view check ({view}): {len(views)} pages, {total} lettered words, "
          f"{len(errors)} errors, {len(warnings)} warnings.")
    return 1 if errors else 0


def cmd_report(view: str) -> int:
    terms = leakage_terms()
    print(f"Reader views, measured {datetime.date.today().isoformat()}, view {view!r}. "
          "Tokens are estimates at four characters per token.\n")
    for arm, text in build_arms(view).items():
        hits = term_hits(text, terms)
        print(f"  {arm}  {words(text):>7,} words  ~{estimated_tokens(text):>7,} tokens  "
              f"{len(hits):>2} leakage terms  {ARMS[arm]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    script = sub.add_parser("script", help="the stripped script")
    script.add_argument("--pages", help="an inclusive range such as 001-015")
    for command in (script, sub.add_parser("arms", help="write arms A0-A5 and a manifest"),
                    sub.add_parser("check", help="hold the extractor to panels.py and scan for apparatus"),
                    sub.add_parser("report", help="words and estimated tokens per arm")):
        command.add_argument("--view", choices=VIEWS, default="full")
    sub.add_parser("novella", help="the novella's plain-text edition")
    sub.add_parser("appendix", help="the appendix's plain-text edition")
    sub.choices["arms"].add_argument("--out", type=Path, default=ROOT / "256t" / "synthetic-readers" / "arms")
    args = parser.parse_args(argv)

    if args.command == "script":
        sys.stdout.write(script_text(args.pages, args.view)[0])
        return 0
    if args.command == "novella":
        sys.stdout.write(novella_text())
        return 0
    if args.command == "appendix":
        sys.stdout.write(appendix_text())
        return 0
    if args.command == "arms":
        return cmd_arms(args.out, args.view)
    if args.command == "check":
        return cmd_check(args.view)
    return cmd_report(args.view)


if __name__ == "__main__":
    raise SystemExit(main())
