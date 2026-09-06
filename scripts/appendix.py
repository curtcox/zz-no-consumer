#!/usr/bin/env python3
"""The appendix of contested assertions and logical fallacies.

`content/appendix/` holds one file per entry. An entry is keyed to story page numbers,
which are the same numbers in the graphic novel and in the novella, so a single appendix
serves both editions and a reader who has one can use it with the other.

Two kinds of entry live here:

* **contested** — an assertion the book makes, or reports, whose truth is genuinely in
  dispute. Each carries the best available evidence *from more than one stance*, with a URL
  wherever a public one exists.
* **fallacy** — a piece of reasoning in the book, or in a dated public statement the book
  cites, that does not license its conclusion. The named fallacy comes from a fixed
  vocabulary so the appendix cannot invent a category to win an argument.

The unit is the entry, the address is the page, and the evidence table is the payload.

    python3 scripts/appendix.py report     # census, page coverage, stance and fallacy spread
    python3 scripts/appendix.py check      # exit non-zero while the appendix disagrees with itself
    python3 scripts/appendix.py json       # the whole model, for other tools
    python3 scripts/appendix.py assemble   # the appendix as one Markdown document

`check` holds three rules above the rest:

1. **Every cited page exists.** An entry that points at a page the book no longer has is a
   broken reference, exactly like a dangling page reference anywhere else in the tree.
2. **A contested entry carries more than one stance.** An appendix of contested assertions
   that quotes one side is not an appendix of contested assertions.
3. **A fallacy attributed to a real, named person or organisation cites the dated public
   statement it characterises.** `content/story-contract.md` allows real critics on the page
   only through attributed paraphrase of dated public writing; this is that rule, enforced.
"""

from __future__ import annotations

import argparse
import json as jsonlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import crossref  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "content" / "appendix"
CONTESTED = BASE / "contested"
FALLACIES = BASE / "fallacies"

ID = re.compile(r"^(CA|LF)-(\d{2})$")
URL = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BARE_URL = re.compile(r"https?://[^\s)\]<>]+")

# A fallacy entry names its fault from this list rather than coining one. The point of the
# vocabulary is that the appendix cannot escape a hard case by inventing a category for it:
# if a piece of reasoning is not one of these, the entry has to argue that it is bad
# reasoning in prose instead of labelling it.
FALLACIES_VOCABULARY = {
    "affirming-the-consequent": "Treating a prediction's success as proof of the hypothesis that made it.",
    "anthropomorphism": "Reading a mental state off behaviour that does not establish one.",
    "appeal-to-authority": "Treating a source's standing, rather than its evidence, as decisive.",
    "appeal-to-procedure": "Treating 'the rules did not require it' as an answer to 'should we'.",
    "argument-from-ignorance": "Treating the absence of evidence for X as evidence for not-X.",
    "argument-from-silence": "Reading a conclusion out of what a record does not mention.",
    "base-rate-neglect": "Reading a proportion as a magnitude, or a magnitude as a proportion.",
    "circular-evidence": "Supporting a claim with a source that derives from the claim.",
    "equivocation": "Letting one word carry two meanings across the steps of an argument.",
    "false-analogy": "Carrying a conclusion across a resemblance that does not support it.",
    "false-dilemma": "Presenting two options as exhaustive when they are neither exhaustive nor exclusive.",
    "false-precision": "Reporting a number to a precision the method cannot support.",
    "fallacy-of-composition": "Attributing to a whole what is true only of its parts, or the reverse.",
    "genetic-fallacy": "Assessing a claim by its origin rather than its content.",
    "hasty-generalization": "Generalising from a sample that cannot carry the generalisation.",
    "modal-slide": "Sliding from 'possible' to 'actual', or from 'could have' to 'did'.",
    "narrative-coherence": "Treating a story's internal coherence as evidence that it is true.",
    "post-hoc": "Treating sequence as cause.",
    "reification": "Treating a category, ranking, or label produced by an instrument as a property of the world.",
    "selection-effect": "Drawing a conclusion from a sample selected by the thing being concluded.",
    "suppressed-evidence": "Presenting a claim with a qualifier too small, late, or quiet to do its work.",
    "survivorship-bias": "Counting what was caught and not what was missed.",
}

ATTRIBUTIONS = ("in-story", "book", "named-source")
LAYERS = ("incident", "thesis")
STATUSES = ("unresolved", "disputed", "bounded", "open")
KINDS = ("contested", "fallacy")


@dataclass(frozen=True)
class Reference:
    stance: str
    label: str
    url: str
    detail: str


@dataclass(frozen=True)
class Entry:
    id: str
    kind: str
    title: str
    path: Path
    pages: tuple[int, ...]
    body: str
    front: dict[str, str]
    references: tuple[Reference, ...] = ()
    sections: tuple[str, ...] = ()

    @property
    def relative(self) -> str:
        return str(self.path.relative_to(ROOT))

    @property
    def stances(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(reference.stance for reference in self.references))


@dataclass
class Note:
    severity: str
    code: str
    where: str
    message: str


@dataclass
class Appendix:
    entries: list[Entry] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)

    @property
    def contested(self) -> list[Entry]:
        return [entry for entry in self.entries if entry.kind == "contested"]

    @property
    def fallacies(self) -> list[Entry]:
        return [entry for entry in self.entries if entry.kind == "fallacy"]

    def by_page(self) -> dict[int, list[Entry]]:
        index: dict[int, list[Entry]] = {}
        for entry in self.entries:
            for page in entry.pages:
                index.setdefault(page, []).append(entry)
        return {page: index[page] for page in sorted(index)}


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Front matter is flat `key: value`, plus one list form for `pages:`.

    Deliberately not YAML. The repository parses its own front matter everywhere else for
    the same reason: one dependency-free reader, one shape, and a parse error that names the
    file rather than a line number inside a library.
    """
    if not text.startswith("---\n"):
        return {}, text
    _, block, body = text.split("---\n", 2)
    front: dict[str, str] = {}
    key = ""
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) and key:
            front[key] = (front[key] + " " + line.strip()).strip()
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # A folded-scalar marker introduces the value on the following lines rather than
        # being part of it, so it is read and discarded rather than stored.
        front[key] = "" if value in (">-", ">", "|", "|-") else value
    return front, body


def parse_pages(value: str) -> tuple[int, ...]:
    return tuple(int(number) for number in re.findall(r"\d{1,3}", value or ""))


def parse_references(body: str) -> tuple[tuple[Reference, ...], list[str]]:
    """Read the evidence table.

    One table, four columns, one row per reference: stance, source, date, and what the
    source actually supports. A row whose source cell carries no link is kept — some of the
    best evidence here is a PDF behind a paywall or a document with no stable address — and
    reported separately so the gap is visible rather than silently tolerated.
    """
    references: list[Reference] = []
    problems: list[str] = []
    rows = re.findall(r"^\|(?!\s*[-: ]+\|).*\|\s*$", body, flags=re.MULTILINE)
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if cells[0].lower() in ("stance", "position"):
            continue
        stance, source, date, detail = cells[0], cells[1], cells[2], cells[3]
        link = URL.search(source)
        if link:
            references.append(Reference(stance, link.group(1), link.group(2), f"{date} — {detail}"))
            continue
        bare = BARE_URL.search(source)
        if bare:
            references.append(Reference(stance, source, bare.group(0), f"{date} — {detail}"))
            continue
        references.append(Reference(stance, re.sub(r"[*`]", "", source), "", f"{date} — {detail}"))
        problems.append(source)
    return tuple(references), problems


def read_entry(path: Path) -> Entry:
    text = path.read_text(encoding="utf-8")
    front, body = split_front_matter(text)
    references, _ = parse_references(body)
    return Entry(
        id=front.get("id", ""),
        kind=front.get("kind", ""),
        title=front.get("title", ""),
        path=path,
        pages=parse_pages(front.get("pages", "")),
        body=body,
        front=front,
        references=references,
        sections=tuple(match.strip() for match in re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)),
    )


def entry_files() -> list[Path]:
    paths: list[Path] = []
    for directory in (CONTESTED, FALLACIES):
        if directory.is_dir():
            paths.extend(sorted(directory.glob("*.md")))
    return paths


def build() -> Appendix:
    appendix = Appendix()
    for path in entry_files():
        appendix.entries.append(read_entry(path))
    appendix.entries.sort(key=lambda entry: entry.id)
    return appendix


def audit(appendix: Appendix) -> list[Note]:
    notes: list[Note] = []
    model = crossref.build()
    known = {page.number for page in model.pages}
    seen: dict[str, str] = {}

    required_contested = ("What the book asserts", "Why it is contested", "The evidence")
    required_fallacy = ("Where it appears", "Why the reasoning does not carry", "The evidence")

    for entry in appendix.entries:
        where = entry.relative

        if not ID.match(entry.id):
            notes.append(Note("error", "bad-id", where, f"id {entry.id!r} is not CA-NN or LF-NN"))
        elif entry.id in seen:
            notes.append(Note("error", "duplicate-id", where, f"id {entry.id} is also {seen[entry.id]}"))
        else:
            seen[entry.id] = where

        if entry.kind not in KINDS:
            notes.append(Note("error", "bad-kind", where, f"kind {entry.kind!r} is not one of {KINDS}"))
        expected_directory = CONTESTED if entry.kind == "contested" else FALLACIES
        if entry.kind in KINDS and entry.path.parent != expected_directory:
            notes.append(Note("error", "misfiled", where,
                              f"a {entry.kind} entry belongs in {expected_directory.relative_to(ROOT)}/"))
        if entry.kind == "contested" and not entry.id.startswith("CA-"):
            notes.append(Note("error", "id-kind-mismatch", where, "a contested entry takes a CA- id"))
        if entry.kind == "fallacy" and not entry.id.startswith("LF-"):
            notes.append(Note("error", "id-kind-mismatch", where, "a fallacy entry takes an LF- id"))

        if not entry.title:
            notes.append(Note("error", "no-title", where, "has no title"))

        # Rule 1. An entry that points at a page the book no longer has is a broken
        # reference, and the appendix is addressed by page number in two editions at once.
        if not entry.pages:
            notes.append(Note("error", "no-pages", where, "cites no story page"))
        for page in entry.pages:
            if page not in known:
                notes.append(Note("error", "dangling-page", where,
                                  f"cites page {page:03d}, which is not in the page manifest"))

        for heading in (required_contested if entry.kind == "contested" else required_fallacy):
            if heading not in entry.sections:
                notes.append(Note("error", "missing-section", where, f"has no '## {heading}' section"))

        if entry.kind == "contested":
            layer = entry.front.get("layer", "")
            if layer not in LAYERS:
                notes.append(Note("error", "bad-layer", where, f"layer {layer!r} is not one of {LAYERS}"))
            status = entry.front.get("status", "")
            if status not in STATUSES:
                notes.append(Note("error", "bad-status", where, f"status {status!r} is not one of {STATUSES}"))
            if not entry.front.get("claim"):
                notes.append(Note("error", "no-claim", where, "does not state the assertion in a claim: line"))

            # Rule 2. One stance is not a contested assertion, it is a citation.
            if len(entry.stances) < 2:
                notes.append(Note("error", "single-stance", where,
                                  f"carries {len(entry.stances)} stance(s); a contested assertion needs at least two"))
            if len(entry.references) < 4:
                notes.append(Note("warning", "thin-evidence", where,
                                  f"carries {len(entry.references)} references"))

        if entry.kind == "fallacy":
            name = entry.front.get("fallacy", "")
            if name not in FALLACIES_VOCABULARY:
                notes.append(Note("error", "unknown-fallacy", where,
                                  f"names {name!r}, which is not in the vocabulary"))
            attribution = entry.front.get("attributed_to", "")
            if attribution not in ATTRIBUTIONS:
                notes.append(Note("error", "bad-attribution", where,
                                  f"attributed_to {attribution!r} is not one of {ATTRIBUTIONS}"))
            # Rule 3. The story contract lets a real critic onto the page only as attributed
            # paraphrase of dated public writing. A fallacy entry that names one without
            # citing the statement it characterises is an accusation, not a citation.
            if attribution == "named-source":
                if not entry.front.get("source_url", "").startswith("http"):
                    notes.append(Note("error", "uncited-attribution", where,
                                      "attributes reasoning to a named source without a source_url"))
                if not entry.front.get("said"):
                    notes.append(Note("error", "uncited-attribution", where,
                                      "attributes reasoning to a named source without a said: date"))
            if not entry.references:
                notes.append(Note("error", "no-evidence", where, "carries no evidence table rows"))

        for reference in entry.references:
            if not reference.url:
                notes.append(Note("note", "no-url", where,
                                  f"'{reference.label}' has no public URL"))

    # Entries cross-reference each other by anchor, and the assembled document is where those
    # anchors resolve. An anchor that does not match an entry is a link that lands nowhere in
    # the EPUB, the self-contained HTML, and the reader alike, so it fails rather than warns.
    anchors = {anchor(entry): entry.id for entry in appendix.entries}
    for entry in appendix.entries:
        for target in re.findall(r"\]\(#((?:ca|lf)-[a-z0-9-]+)\)", entry.body, flags=re.IGNORECASE):
            if target.lower() not in anchors:
                notes.append(Note("error", "dangling-anchor", entry.relative,
                                  f"links to #{target}, which is not an entry anchor"))

    # A page carrying an entry that no other entry or index knows about is fine; a page the
    # appendix claims twice under the same id is not.
    for page, entries in appendix.by_page().items():
        ids = [entry.id for entry in entries]
        if len(ids) != len(set(ids)):
            notes.append(Note("error", "duplicate-page-entry", f"page {page:03d}",
                              "is cited twice by the same entry"))
    return notes


def print_notes(notes: list[Note]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "note": 0}
    for note in sorted(notes, key=lambda item: (item.severity, item.where, item.code)):
        counts[note.severity] = counts.get(note.severity, 0) + 1
        print(f"{note.severity:>7}  {note.code:<22} {note.where}: {note.message}")
    return counts


def cmd_check(strict: bool) -> int:
    appendix = build()
    if not appendix.entries:
        print("No appendix entries found under content/appendix/.")
        return 1
    notes = audit(appendix)
    counts = print_notes(notes)
    print(
        f"\n{len(appendix.entries)} entries "
        f"({len(appendix.contested)} contested, {len(appendix.fallacies)} fallacies), "
        f"{sum(len(entry.references) for entry in appendix.entries)} references, "
        f"{len(appendix.by_page())} pages cited."
    )
    print(f"{counts['error']} error(s), {counts['warning']} warning(s), {counts['note']} note(s).")
    if counts["error"]:
        return 1
    return 1 if strict and counts["warning"] else 0


def cmd_report() -> int:
    appendix = build()
    model = crossref.build()
    titles = {page.number: page.title for page in model.pages}

    print("Entries")
    print("-------")
    for entry in appendix.entries:
        pages = ", ".join(f"{page:03d}" for page in entry.pages)
        detail = entry.front.get("layer") or entry.front.get("fallacy") or ""
        print(f"  {entry.id}  {entry.title}")
        print(f"          {detail:<24} pages {pages}")
        print(f"          {len(entry.references)} references, {len(entry.stances)} stances")

    print("\nStances")
    print("-------")
    stances: dict[str, int] = {}
    for entry in appendix.entries:
        for reference in entry.references:
            stances[reference.stance] = stances.get(reference.stance, 0) + 1
    for stance, count in sorted(stances.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {count:>4}  {stance}")

    print("\nFallacies named")
    print("---------------")
    named: dict[str, int] = {}
    for entry in appendix.fallacies:
        name = entry.front.get("fallacy", "?")
        named[name] = named.get(name, 0) + 1
    for name, count in sorted(named.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {count:>4}  {name}")
    unused = sorted(set(FALLACIES_VOCABULARY) - set(named))
    if unused:
        print(f"  ({len(unused)} vocabulary entries unused: {', '.join(unused)})")

    print("\nPage coverage")
    print("-------------")
    index = appendix.by_page()
    for page, entries in index.items():
        ids = " ".join(entry.id for entry in entries)
        print(f"  {page:03d}  {titles.get(page, '?')[:40]:<42} {ids}")
    print(f"\n{len(index)} of {len(model.pages)} story pages carry at least one entry.")

    hosts: dict[str, int] = {}
    for entry in appendix.entries:
        for reference in entry.references:
            if reference.url:
                host = reference.url.split("/")[2]
                hosts[host] = hosts.get(host, 0) + 1
    print(f"\n{sum(hosts.values())} linked references across {len(hosts)} hosts.")
    return 0


def cmd_json(out: str | None) -> int:
    appendix = build()
    payload = {
        "entries": [
            {
                "id": entry.id,
                "kind": entry.kind,
                "title": entry.title,
                "pages": list(entry.pages),
                "source": entry.relative,
                **{key: value for key, value in entry.front.items()
                   if key not in ("id", "kind", "title", "pages")},
                "references": [
                    {"stance": reference.stance, "label": reference.label,
                     "url": reference.url, "detail": reference.detail}
                    for reference in entry.references
                ],
            }
            for entry in appendix.entries
        ]
    }
    text = jsonlib.dumps(payload, indent=2) + "\n"
    if out:
        Path(out).write_text(text, encoding="utf-8")
        print(f"Wrote {out}")
    else:
        sys.stdout.write(text)
    return 0


def assemble() -> str:
    """The whole appendix as one Markdown document, for the book's back matter.

    Links stay as Markdown links, which is what makes them clickable in every edition that
    can render one: the site, the self-contained HTML, and the EPUB all run this through the
    same converter, and the plain-text build flattens them to the bare URL rather than
    dropping the address.
    """
    appendix = build()
    intro = (BASE / "README.md").read_text(encoding="utf-8") if (BASE / "README.md").exists() else ""
    intro = re.sub(r"^#\s+.*\n", "", intro, count=1).strip()
    # Only the reader-facing half of the README belongs in the book.
    intro = intro.split("<!-- editorial -->")[0].strip()

    parts = [
        "# Appendix — Contested Assertions and Logical Fallacies",
        "",
        intro,
        "",
        "## Index by story page",
        "",
        "| Page | Entries |",
        "| ---: | --- |",
    ]
    for page, entries in appendix.by_page().items():
        ids = ", ".join(f"[{entry.id}](#{anchor(entry)})" for entry in entries)
        parts.append(f"| {page:03d} | {ids} |")
    parts += ["", "## Contested assertions", ""]
    for entry in appendix.contested:
        parts += [render(entry), ""]
    parts += ["## Logical fallacies", ""]
    for entry in appendix.fallacies:
        parts += [render(entry), ""]
    return "\n".join(parts).rstrip() + "\n"


def anchor(entry: Entry) -> str:
    return f"{entry.id.lower()}-" + re.sub(r"[^a-z0-9]+", "-", entry.title.lower()).strip("-")


def render(entry: Entry) -> str:
    pages = ", ".join(f"{page:03d}" for page in entry.pages)
    lines = [f"### {entry.id} — {entry.title}", ""]
    meta = [f"**Pages** {pages}"]
    if entry.kind == "contested":
        meta.append(f"**Layer** {entry.front.get('layer', '')}")
        meta.append(f"**Status** {entry.front.get('status', '')}")
    else:
        meta.append(f"**Fallacy** {entry.front.get('fallacy', '')}")
        meta.append(f"**Attributed to** {entry.front.get('attributed_to', '')}")
        if entry.front.get("speaker"):
            meta.append(f"**Speaker** {entry.front['speaker']}")
    lines += [" · ".join(meta), ""]
    if entry.front.get("claim"):
        lines += [f"> {entry.front['claim']}", ""]
    lines += [entry.body.strip(), ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("report", help="census, page coverage, stance and fallacy spread")
    check = commands.add_parser("check", help="exit non-zero while the appendix disagrees with itself")
    check.add_argument("--strict", action="store_true", help="also fail on warnings")
    dump = commands.add_parser("json", help="the whole model, for other tools")
    dump.add_argument("--out", metavar="FILE", help="write here instead of standard output")
    build_command = commands.add_parser("assemble", help="the appendix as one Markdown document")
    build_command.add_argument("--out", metavar="FILE", help="write here instead of standard output")
    args = parser.parse_args(argv)

    if args.command == "report":
        return cmd_report()
    if args.command == "check":
        return cmd_check(args.strict)
    if args.command == "json":
        return cmd_json(args.out)
    text = assemble()
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
