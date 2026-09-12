#!/usr/bin/env python3
"""Build the page/source/provenance cross reference from canonical repository files.

The model joins four records that are maintained separately:

* ``data/pages.yaml`` and ``data/chapters.yaml`` — the page and chapter manifest.
* ``content/pages/NNN.md`` — front-matter provenance pairs and per-panel
  ``**Provenance:**`` lines.
* ``research/scene-provenance.md`` — the citation-key table and sequence ledger.
* ``research/chapter-source-packets/*.md`` — the per-chapter citation-key registry
  that carries each key's title and original URL.

Used as a library by ``build-site.py`` and as a command line tool:

    python3 scripts/crossref.py report
    python3 scripts/crossref.py check
    python3 scripts/crossref.py json --out data/crossref.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Kept in step with ALLOWED_PROVENANCE in validate-continuity.py.
PROVENANCE_STATUSES = (
    "documented",
    "raw-agent-text",
    "quotation",
    "source-paraphrase",
    "disputed",
    "inferred",
    "compressed",
    "reconstructed",
    "invented",
)

STATUS_NOTES = {
    "documented": "Asserted by a cited source and narrowed, never widened, on the page.",
    "raw-agent-text": "Agent output in the words the source record preserves, registered on the page with its locator.",
    "quotation": "A person's or institution's own words, registered on the page with source, locator, and how the record was made.",
    "source-paraphrase": "An attributed summary standing in for source language that is not reproduced.",
    "disputed": "Sources disagree; the page keeps both accounts visible.",
    "inferred": "A conclusion this project draws from cited events, stated as project analysis.",
    "compressed": "Several documented events shown as one panel or figure.",
    "reconstructed": "Invented staging for a sourced event: rooms, interfaces, and dialogue.",
    "invented": "Material with no claim of direct observation, disclosed as such.",
}

# Sequence keys in data/pages.yaml are spelled out; the ledger uses single letters.
SEQUENCE_ALIASES = {"interlude-a": "A", "interlude-b": "B", "interlude-c": "C"}


def sequence_key(value: str) -> str:
    return SEQUENCE_ALIASES.get(value.strip(), value.strip())


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def split_key(value: str) -> list[str]:
    """``HF-TL/OAI-TR`` records one claim resting on two sources."""
    return [part.strip() for part in value.split("/") if part.strip()]


@dataclass(frozen=True)
class Source:
    key: str
    title: str = ""
    url: str = ""
    ledger_note: str = ""
    packet_notes: tuple[tuple[str, str], ...] = ()

    @property
    def registered(self) -> bool:
        return bool(self.ledger_note or self.packet_notes)

    @property
    def label(self) -> str:
        return self.title or self.ledger_note or self.key


@dataclass(frozen=True)
class Panel:
    number: int
    statuses: tuple[str, ...]
    sources: tuple[str, ...]
    note: str
    invalid_statuses: tuple[str, ...] = ()


@dataclass(frozen=True)
class Page:
    id: str
    number: int
    chapter: str
    sequence: str
    title: str
    status: str
    scripted: bool
    declared: tuple[tuple[str, tuple[str, ...]], ...] = ()
    panels: tuple[Panel, ...] = ()
    locations: tuple[str, ...] = ()
    continuity_checks: tuple[str, ...] = ()

    @property
    def declared_statuses(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(status for status, _ in self.declared))

    @property
    def declared_sources(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(key for _, keys in self.declared for key in keys))

    @property
    def panel_statuses(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(status for panel in self.panels for status in panel.statuses))

    @property
    def panel_sources(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(key for panel in self.panels for key in panel.sources))

    @property
    def statuses(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.declared_statuses + self.panel_statuses))

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.declared_sources + self.panel_sources))


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    first_page: int
    last_page: int
    # The stem of the chapter's brief in `content/chapters/`. It is also the name of the
    # chapter's directory in the novella tree, which is why it is modelled here rather than
    # rebuilt from the title: a chapter id is `01`, and `01` is not a directory name.
    directory: str = ""


@dataclass(frozen=True)
class Sequence:
    key: str
    first_page: int
    last_page: int
    event: str
    statuses: tuple[str, ...]
    rule: str
    sources: tuple[str, ...]

    @property
    def label(self) -> str:
        return f"Interlude {self.key}" if self.key.isalpha() else f"Sequence {self.key}"


# error: the record does not join up. warning: page front matter and panel
# lines disagree. note: something registered is going unused.
SEVERITIES = ("error", "warning", "note")


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    subject: str
    message: str


@dataclass
class CrossReference:
    chapters: list[Chapter]
    pages: list[Page]
    sources: dict[str, Source]
    sequences: dict[str, Sequence]
    findings: list[Finding] = field(default_factory=list)

    def chapter(self, chapter_id: str) -> Chapter:
        return next(item for item in self.chapters if item.id == chapter_id)

    def page(self, page_id: str) -> Page:
        return next(item for item in self.pages if item.id == page_id)

    def pages_for_source(self, key: str) -> list[Page]:
        return [page for page in self.pages if key in page.sources]

    def pages_for_status(self, status: str) -> list[Page]:
        return [page for page in self.pages if status in page.statuses]

    def pages_for_sequence(self, key: str) -> list[Page]:
        return [page for page in self.pages if sequence_key(page.sequence) == key]

    def sources_for_status(self, status: str) -> list[str]:
        keys: list[str] = []
        for page in self.pages:
            for declared_status, declared_keys in page.declared:
                if declared_status == status:
                    keys.extend(declared_keys)
            for panel in page.panels:
                if status in panel.statuses:
                    keys.extend(panel.sources)
        return sorted(dict.fromkeys(keys))

    def statuses_for_source(self, key: str) -> list[str]:
        statuses: list[str] = []
        for page in self.pages:
            for status, keys in page.declared:
                if key in keys:
                    statuses.append(status)
            for panel in page.panels:
                if key in panel.sources:
                    statuses.extend(panel.statuses)
        return sorted(dict.fromkeys(statuses), key=PROVENANCE_STATUSES.index)

    def used_statuses(self) -> list[str]:
        used = {status for page in self.pages for status in page.statuses}
        return [status for status in PROVENANCE_STATUSES if status in used]

    def used_sources(self) -> list[str]:
        used = {key for page in self.pages for key in page.sources}
        return sorted(used)


def front_matter(source: str) -> str:
    if not source.startswith("---\n"):
        return ""
    end = source.find("\n---\n", 4)
    return "" if end < 0 else source[4:end]


def yaml_list(metadata: str, field_name: str) -> tuple[str, ...]:
    match = re.search(rf"^{field_name}:\s*$((?:\n[ \t]+-.*)*)", metadata, re.MULTILINE)
    if not match:
        return ()
    return tuple(
        item.strip().strip('"')
        for item in re.findall(r"^\s+-\s*(.+?)\s*$", match.group(1), re.MULTILINE)
    )


EXACT_STRING_FIELDS = ("text", "source", "locator", "verification", "rights")
# `pointer` may stand in for `text`: a 256t URI of the exact excerpt, when the words cannot be
# written into the file. Its locator must name the copy (`t256:` of the whole file) and the
# inclusive byte range, so the pointer is checkable by anyone holding that copy. See
# scripts/t256.py.
POINTER_FIELD = "pointer"
REQUIRED_FIELDS = ("source", "locator", "verification", "rights")

ALLOWED_VERIFICATION = {
    "unchecked",          # registered, nothing checked yet
    "exists",             # the source resolves; says nothing about content
    "locator",            # the passage is findable; says nothing about content
    "quoted",             # the claim was checked against the passage, by someone, on a date
    "verbatim",           # character-exact against a NAMED copy, and the row says which copy
    "derived",            # computed rather than read; the method is recorded
    "project-authored",   # this book wrote it; there is no third party to verify against
}

ALLOWED_RIGHTS = {
    "unresolved",         # no decision yet
    "cleared",            # may print as it stands
    "paraphrase",         # gate 9 decided to summarise; apply it and drop the registration
    "redact",             # gate 9 decided to remove; apply it and drop the registration
}

# What a locked file may carry. A `quoted` match is not enough to print a quotation: the
# wording has to be exact against a named copy. `paraphrase` and `redact` are decisions to
# transform, so a locked file carrying one means the decision was recorded and never applied.
LOCKABLE_VERIFICATION = {"verbatim", "project-authored"}
LOCKABLE_RIGHTS = {"cleared"}


def read_exact_strings(metadata: str) -> tuple[list[dict[str, str]], list[str]]:
    """Parse an exact_strings block into entries, and report malformed ones.

    Hand-parsed for the same reason everything else here is: the standard library has no
    YAML. The block is either `exact_strings: []` or a list of mappings whose keys are
    EXACT_STRING_FIELDS. A bare list item is malformed, because a string with no source,
    locator, verification or rights decision is exactly what the check exists to catch.
    """
    match = re.search(r"^exact_strings:[ \t]*(.*)$", metadata, re.MULTILINE)
    if not match:
        return [], ["missing exact_strings"]
    if match.group(1).strip() == "[]":
        return [], []
    body = metadata[match.end():]
    stop = re.search(r"^[A-Za-z_]", body, re.MULTILINE)
    if stop:
        body = body[: stop.start()]
    if not body.strip():
        return [], ["exact_strings is present but empty; write `exact_strings: []`"]
    entries: list[dict[str, str]] = []
    problems: list[str] = []
    for chunk in re.split(r"(?=^\s*-\s)", body, flags=re.MULTILINE):
        if not chunk.strip():
            continue
        entry: dict[str, str] = {}
        for line in chunk.splitlines():
            field_match = re.match(r"^\s*(?:-\s*)?([a-z_]+):\s*(.*?)\s*$", line)
            if field_match and field_match.group(1) in (*EXACT_STRING_FIELDS, POINTER_FIELD):
                entry[field_match.group(1)] = field_match.group(2).strip().strip('"')
        if not entry:
            problems.append(
                f"unregistered exact string {chunk.strip().lstrip('- ')[:48]!r}: "
                f"needs {', '.join(EXACT_STRING_FIELDS)}"
            )
            continue
        entries.append(entry)
    return entries, problems


def pointer_problems(entry: dict[str, str], label: str) -> list[str]:
    """What is wrong with a registration's 256t pointer, checkable without the vault.

    The URI must be well formed, and the locator must name the copy and a byte range whose
    length is the length the pointer declares — a range and a pointer that disagree about
    how many octets were quoted cannot both be right. Whether the bytes hash to the pointer
    needs the copy: `t256.py verify`.
    """
    import t256

    problems: list[str] = []
    pointer = entry[POINTER_FIELD]
    problem = t256.uri_problem(pointer)
    if problem:
        return [f"pointer {label!r} {problem}"]
    record = t256.URI.search(entry.get("locator", ""))
    span = t256.LOCATOR_RANGE.search(entry.get("locator", ""))
    if not record or t256.uri_problem(record.group(0)):
        problems.append(f"pointer {label!r} has no t256 URI for its copy in the locator")
    if not span:
        problems.append(f"pointer {label!r} has no bytes=START-END range in the locator")
    elif int(span.group(2)) - int(span.group(1)) + 1 != t256.declared_length(pointer):
        problems.append(
            f"pointer {label!r} declares {t256.declared_length(pointer)} octets but its locator "
            f"range is {int(span.group(2)) - int(span.group(1)) + 1}"
        )
    elif record and int(span.group(2)) >= t256.declared_length(record.group(0)):
        problems.append(f"pointer {label!r} range runs past the end of its copy")
    return problems


def audit_exact_strings(metadata: str, where: str, *, locked: bool) -> tuple[list[str], list[str]]:
    """Hold one file's exact_strings registration to the rule. Returns (errors, warnings).

    Both editions share this, because both ship and both share the page key. A quotation
    registered on a script and not on its prose page, or the reverse, is two different books.
    """
    errors: list[str] = []
    warnings: list[str] = []
    registered, malformed = read_exact_strings(metadata)
    for problem in malformed:
        errors.append(f"{where}: {problem}")
    for entry in registered:
        label = (entry.get("text") or entry.get(POINTER_FIELD) or "?")[:48]
        missing = [name for name in REQUIRED_FIELDS if not entry.get(name)]
        if not entry.get("text") and not entry.get(POINTER_FIELD):
            missing.insert(0, "text (or pointer)")
        if missing:
            errors.append(f"{where}: exact string {label!r} is missing {', '.join(missing)}")
            continue
        if entry.get(POINTER_FIELD):
            errors.extend(f"{where}: {problem}" for problem in pointer_problems(entry, label))
        if entry["verification"] not in ALLOWED_VERIFICATION:
            errors.append(
                f"{where}: exact string {label!r} has unknown verification "
                f"{entry['verification']!r}"
            )
        if entry["rights"] not in ALLOWED_RIGHTS:
            errors.append(f"{where}: exact string {label!r} has unknown rights {entry['rights']!r}")
        if locked:
            if not entry.get("text"):
                errors.append(
                    f"{where} is locked but exact string {label!r} is only a pointer; a pointer "
                    "says where the words are, and a locked page has to print them"
                )
            if entry["verification"] not in LOCKABLE_VERIFICATION:
                errors.append(
                    f"{where} is locked but exact string {label!r} is only "
                    f"{entry['verification']!r}; gate 9 requires verbatim"
                )
            if entry["rights"] not in LOCKABLE_RIGHTS:
                errors.append(
                    f"{where} is locked but exact string {label!r} has rights "
                    f"{entry['rights']!r}; apply the decision and drop the registration"
                )
        elif entry["verification"] == "unchecked" or entry["rights"] == "unresolved":
            warnings.append(
                f"{where}: exact string {label!r} is not yet dispositioned "
                f"(verification {entry['verification']}, rights {entry['rights']}) — gate 9"
            )
    return errors, warnings


# A paraphrase lettered in a verbatim shape is the one hazard the registration above cannot
# see: nothing is registered precisely because nothing was quoted, so `exact_strings: []` is
# truthful and the page still shows the reader words in a source's mouth. Lettered
# `Screen / system text` reads as verbatim. See
# research/quotation-and-paraphrase-2026-09-12.md, which found the first instance by hand and
# predicted the pattern would recur.
PARAPHRASE_DECLARED = re.compile(r"source-paraphrase|paraphras", re.IGNORECASE)
VERBATIM_SHAPED = re.compile(r"^\*\*Screen / system text", re.MULTILINE)
# Words that tell the *reader* the wording is the project's. Attribution is deliberately not
# among them: attributing a quotation to a named person is the failure, not the disclosure.
SUMMARY_DISCLOSED = re.compile(
    r"summar|paraphras|editorial|abstract|redact|restat|report|describ|treats|belief|states that",
    re.IGNORECASE,
)
# The two statuses that say the lettering is the source's own words.
QUOTING_STATUSES = ("quotation", "raw-agent-text")
# A lettering label that presents its text as a third party's words.
ATTRIBUTION_LABEL = re.compile(r"CITED|CITING|PUBLISHED|ATTRIBUTED|QUOTED|QUOTATION|VERBATIM")
LETTERING_LABEL = re.compile(r"^\*\*Screen / system text(?:\s*—\s*([^*]*?))?:\*\*\s*$", re.MULTILINE)


def panel_chunks(source: str) -> list[tuple[str, str, str]]:
    """Each panel as (number, provenance text, reader-visible text).

    The whole Provenance paragraph is production text, including its continuation lines, so
    all of it is removed from the reader's view — a disclosure word that only appears on the
    second line of a provenance note is still invisible to the reader.
    """
    panels: list[tuple[str, str, str]] = []
    for chunk in re.split(r"^## Panels? ", source, flags=re.MULTILINE)[1:]:
        number = chunk.split("\n", 1)[0].strip()
        chunk = re.split(r"^## ", chunk, flags=re.MULTILINE)[0]
        provenance = re.search(r"^\*\*Provenance:\*\*(.*?)(?:\n\s*\n|\Z)", chunk, re.MULTILINE | re.DOTALL)
        provenance_text = provenance.group(1) if provenance else ""
        reader_visible = chunk.replace(provenance.group(0), "\n") if provenance else chunk
        panels.append((number, provenance_text, reader_visible))
    return panels


def normalise_wording(text: str) -> str:
    """Compare wording, not typography: case, quote style, backticks, and line wrapping."""
    text = text.replace("`", "").translate(str.maketrans("‘’“”", "''\"\""))
    return re.sub(r"\s+", " ", text).strip().casefold()


def lettered_under_label(reader_visible: str) -> list[tuple[str, list[str]]]:
    """Each `Screen / system text` block as (label, the backticked strings it letters)."""
    blocks: list[tuple[str, list[str]]] = []
    for match in LETTERING_LABEL.finditer(reader_visible):
        rest = reader_visible[match.end():]
        stop = re.search(r"^\*\*", rest, re.MULTILINE)
        body = rest[: stop.start()] if stop else rest
        strings = [item for item in re.findall(r"`([^`]+)`", body) if item.strip()]
        blocks.append(((match.group(1) or "").strip(), strings))
    return blocks


def is_registered(string: str, registered: list[dict[str, str]]) -> bool:
    """A lettered string is registered when its wording is a registered entry, or a run of it.

    One direction only: a lettered line may be part of a registered quotation split across
    lines, but a line that adds words to a registration is carrying unregistered words. A
    fragment must be at least four words on word boundaries, so a one-word label such as
    `OFFENSE` is not mistaken for part of a quotation that happens to contain it.
    """
    if any(entry.get(POINTER_FIELD) and string.strip() == entry[POINTER_FIELD] for entry in registered):
        return True
    wording = normalise_wording(string)
    if not wording:
        return False
    for entry in registered:
        text = normalise_wording(entry.get("text", ""))
        if not text:
            continue
        if wording == text:
            return True
        if len(wording.split()) >= 4 and re.search(rf"(?<!\w){re.escape(wording)}(?!\w)", text):
            return True
    return False


def audit_paraphrase_shape(source: str, where: str) -> list[str]:
    """Warn where a declared paraphrase is lettered in a shape that reads as a quotation.

    The provenance line is the trigger, not the evidence: it is production text the reader
    never sees, so a panel that discloses only there has disclosed nothing. The disclosure
    has to sit in the frame direction, the action line, the caption, or the lettering itself.
    Warning, not error: which panels are repaired, and whether by quoting the source or by
    relettering the summary, is an editorial decision for gate 9.
    """
    warnings: list[str] = []
    for number, provenance, reader_visible in panel_chunks(source):
        if not PARAPHRASE_DECLARED.search(provenance):
            continue
        if not VERBATIM_SHAPED.search(reader_visible):
            continue
        if SUMMARY_DISCLOSED.search(reader_visible):
            continue
        warnings.append(
            f"{where} panel {number}: provenance declares a paraphrase, the panel letters it as "
            "`Screen / system text`, and nothing in the reader's view says the wording is the "
            "project's — quote the source or reletter the summary at gate 9"
        )
    return warnings


def audit_quotation_shape(source: str, metadata: str, where: str) -> tuple[list[str], list[str]]:
    """Hold lettering that claims to be a source's words to the registration. (errors, warnings)

    Two failures, both invisible to `audit_exact_strings`, which reads front matter only:

    - A panel declaring `quotation` or `raw-agent-text` whose page registers none of the words
      it letters. The status says "these are the source's words"; with nothing registered there
      is no source, locator, or verification to check them against. Error, for the same reason a
      bare string in `exact_strings` is an error.
    - A lettering label that presents its text as a third party's — `CITED`, `PUBLISHED`,
      `ATTRIBUTED` — over strings that are neither registered nor marked `PARAPHRASED` in the
      label. Whether they are the source's words or the project's, the reader cannot tell and
      the record does not say. Warning: the repair, register or reletter, is gate 9's. Panels
      that `audit_paraphrase_shape` already flags are not flagged twice.
    """
    errors: list[str] = []
    warnings: list[str] = []
    registered, _ = read_exact_strings(metadata)
    for number, provenance, reader_visible in panel_chunks(source):
        head = provenance.partition("—")[0]
        quoting = [status for status in QUOTING_STATUSES if f"`{status}`" in head]
        blocks = lettered_under_label(reader_visible)
        if quoting:
            visible = normalise_wording(re.sub(r"^>\s?", "", reader_visible, flags=re.MULTILINE))
            if not any(
                (entry.get("text") and normalise_wording(entry["text"]) in visible)
                or (entry.get(POINTER_FIELD) and entry[POINTER_FIELD] in reader_visible)
                for entry in registered
            ):
                errors.append(
                    f"{where} panel {number}: provenance declares `{quoting[0]}` but no string or "
                    "pointer registered in exact_strings appears in the panel — register the words, "
                    "or a 256t pointer to them, with source, locator, verification and rights"
                )
            continue
        if PARAPHRASE_DECLARED.search(provenance) and VERBATIM_SHAPED.search(reader_visible) \
                and not SUMMARY_DISCLOSED.search(reader_visible):
            continue  # already reported by audit_paraphrase_shape
        for label, strings in blocks:
            if not ATTRIBUTION_LABEL.search(label) or re.search(r"PARAPHRAS", label):
                continue
            unregistered = [string for string in strings if not is_registered(string, registered)]
            if unregistered:
                warnings.append(
                    f"{where} panel {number}: lettering labelled `{label}` presents "
                    f"{len(unregistered)} string(s) as a third party's words that are neither "
                    "registered in exact_strings nor marked PARAPHRASED — register the quotation "
                    "or reletter the summary at gate 9"
                )
    return errors, warnings


def read_chapters() -> list[Chapter]:
    source = (ROOT / "data" / "chapters.yaml").read_text(encoding="utf-8")
    chapters: list[Chapter] = []
    for chunk in re.split(r"(?=^\s*- id: )", source, flags=re.MULTILINE)[1:]:
        def value(key: str) -> str:
            prefix = r"\s+-\s+" if key == "id" else r"\s+"
            match = re.search(rf"^{prefix}{key}:\s+(.+?)\s*$", chunk, flags=re.MULTILINE)
            if not match:
                raise ValueError(f"Missing {key} in data/chapters.yaml")
            return match.group(1).strip('"')

        chapters.append(
            Chapter(
                id=value("id"),
                title=value("title"),
                first_page=int(value("first_page")),
                last_page=int(value("last_page")),
                directory=value("file").removesuffix(".md"),
            )
        )
    return chapters


def read_panels(body: str, known_keys: set[str]) -> tuple[Panel, ...]:
    """Read provenance within each panel section, including shared grouped runs."""
    panels: list[Panel] = []
    chunks = re.split(r"^## ([^\n]+)\n?", body, flags=re.MULTILINE)[1:]
    for heading, chunk in zip(chunks[0::2], chunks[1::2]):
        identity = re.fullmatch(r"Panel (\d+)|Panels (\d+)[–-](\d+)", heading.strip())
        if not identity:
            continue
        first, start, end = identity.groups()
        number = int(first or start)
        numbers = range(number, int(end or number) + 1)
        match = re.search(r"^\*\*Provenance:\*\*\s*(.+?)\s*$", chunk, flags=re.MULTILINE)
        if not match:
            panels.extend(Panel(number=n, statuses=(), sources=(), note="") for n in numbers)
            continue
        line = match.group(1)
        head, _, tail = line.partition("—")
        statuses = tuple(
            dict.fromkeys(
                token
                for token in re.findall(r"`([^`]+)`", head or line)
                if token in PROVENANCE_STATUSES
            )
        )
        sources = tuple(
            dict.fromkeys(
                key
                for token in re.findall(r"`([^`]+)`", line)
                for key in split_key(token)
                if key in known_keys
            )
        )
        panel = Panel(number=number, statuses=statuses, sources=sources, note=tail.strip() or line.strip(),
                  invalid_statuses=tuple(token for token in re.findall(r"`([^`]+)`", head)
                                         if token not in PROVENANCE_STATUSES))
        panels.extend(replace(panel, number=n) for n in numbers)
    return tuple(panels)


def read_pages(known_keys: set[str]) -> list[Page]:
    manifest = (ROOT / "data" / "pages.yaml").read_text(encoding="utf-8")
    rows = re.findall(
        r'^\s*- \{id: "(\d{3})", chapter: "([^"]+)", sequence: "([^"]+)", '
        r'title: "([^"]+)", status: ([a-z-]+)\}$',
        manifest,
        re.MULTILINE,
    )
    pages: list[Page] = []
    for page_id, chapter, sequence, title, status in rows:
        path = ROOT / "content" / "pages" / f"{page_id}.md"
        if not path.exists():
            pages.append(
                Page(
                    id=page_id, number=int(page_id), chapter=chapter, sequence=sequence,
                    title=title, status=status, scripted=False,
                )
            )
            continue
        text = path.read_text(encoding="utf-8")
        metadata = front_matter(text)
        declared = tuple(
            (match.group(1), tuple(split_key(match.group(2))))
            for match in re.finditer(
                r"^\s+-\s*status:\s*([a-z-]+)\s*\n\s+source:\s*(\S+)\s*$", metadata, re.MULTILINE
            )
        )
        pages.append(
            Page(
                id=page_id, number=int(page_id), chapter=chapter, sequence=sequence,
                title=title, status=status, scripted=True, declared=declared,
                panels=read_panels(text[len(metadata) + 8:] if metadata else text, known_keys),
                locations=yaml_list(metadata, "locations"),
                continuity_checks=yaml_list(metadata, "continuity_checks"),
            )
        )
    return pages


def read_ledger_keys() -> dict[str, str]:
    text = (ROOT / "research" / "scene-provenance.md").read_text(encoding="utf-8")
    table = re.search(r"## Citation keys\s*\n(.*?)(?=\n## )", text, re.DOTALL)
    if not table:
        return {}
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", table.group(1), re.MULTILINE)
    }


def read_packet_registry() -> dict[str, tuple[str, str, list[tuple[str, str]]]]:
    """Return ``key -> (title, url, [(chapter id, note)])`` from the chapter packets."""
    chapters = read_chapters()
    registry: dict[str, tuple[str, str, list[tuple[str, str]]]] = {}
    packets = sorted((ROOT / "research" / "chapter-source-packets").glob("*.md"))
    for path in packets:
        index = int(path.stem[:2])
        chapter_id = chapters[index].id if index < len(chapters) else path.stem
        for match in re.finditer(r"^- `([A-Z][A-Z0-9-]*)` — (.+?)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE):
            key, body = match.group(1), match.group(2)
            link = re.search(r"\[([^\]]+)\]\(([^)]+)\)", body)
            title = re.sub(r"[*_]", "", link.group(1)).strip() if link else ""
            url = link.group(2) if link else ""
            existing_title, existing_url, notes = registry.get(key, ("", "", []))
            notes.append((chapter_id, body))
            registry[key] = (existing_title or title, existing_url or url, notes)
    return registry


def read_sequences(pages: list[Page], known_keys: set[str]) -> dict[str, Sequence]:
    text = (ROOT / "research" / "scene-provenance.md").read_text(encoding="utf-8")
    table = re.search(r"## Sequence ledger\s*\n(.*?)(?=\n## )", text, re.DOTALL)
    sequences: dict[str, Sequence] = {}
    if not table:
        return sequences
    row_pattern = re.compile(
        r"^\|\s*(?P<key>\w+)\s*\|\s*(?P<pages>[\d–\-—]+)\s*\|\s*(?P<event>.+?)\s*\|"
        r"\s*(?P<status>.+?)\s*\|\s*(?P<rule>.+?)\s*\|\s*$",
        re.MULTILINE,
    )
    for match in row_pattern.finditer(table.group(1)):
        key = match.group("key")
        if key in {"Seq.", "Target"} or set(key) <= {"-", ":"}:
            continue
        bounds = [int(part) for part in re.findall(r"\d+", match.group("pages"))]
        if not bounds:
            continue
        rule = match.group("rule")
        statuses = tuple(
            dict.fromkeys(
                token for token in re.findall(r"`([^`]+)`", match.group("status"))
                if token in PROVENANCE_STATUSES
            )
        )
        sources = tuple(
            dict.fromkeys(
                item
                for token in re.findall(r"`([^`]+)`", rule)
                for item in split_key(token)
                if item in known_keys
            )
        )
        sequences[key] = Sequence(
            key=key, first_page=bounds[0], last_page=bounds[-1],
            event=match.group("event"), statuses=statuses, rule=rule, sources=sources,
        )
    return sequences


def audit(model: CrossReference) -> list[Finding]:
    findings: list[Finding] = []
    for page in model.pages:
        for key in page.sources:
            if not model.sources[key].registered:
                findings.append(Finding(
                    "unregistered-source", "error", f"page {page.id}",
                    f"cites `{key}`, which no citation-key table or chapter source packet registers",
                ))
        for panel in page.panels:
            if not panel.statuses or panel.invalid_statuses:
                findings.append(Finding(
                    "panel-provenance-invalid", "error", f"page {page.id} panel {panel.number}",
                    "must name canonical provenance statuses; "
                    + (f"unrecognized: {', '.join(panel.invalid_statuses)}"
                       if panel.invalid_statuses else "none found"),
                ))
            for key in panel.sources:
                if key not in page.declared_sources:
                    findings.append(Finding(
                        "panel-source-undeclared", "warning", f"page {page.id} panel {panel.number}",
                        f"cites `{key}`, which the page front matter does not declare",
                    ))
            for status in panel.statuses:
                if status not in page.declared_statuses:
                    findings.append(Finding(
                        "panel-status-undeclared", "warning", f"page {page.id} panel {panel.number}",
                        f"uses provenance status `{status}`, which the page front matter does not declare",
                    ))
        sequence = model.sequences.get(sequence_key(page.sequence))
        if sequence is None:
            findings.append(Finding(
                "sequence-missing", "error", f"page {page.id}",
                f"is assigned to sequence {page.sequence}, which the scene ledger does not list",
            ))
        elif not sequence.first_page <= page.number <= sequence.last_page:
            findings.append(Finding(
                "sequence-range", "error", f"page {page.id}",
                f"is assigned to {sequence.label}, whose ledger range is "
                f"{sequence.first_page}–{sequence.last_page}",
            ))
    used = set(model.used_sources())
    for key, source in sorted(model.sources.items()):
        if source.registered and key not in used:
            findings.append(Finding(
                "unused-source", "note", f"source {key}",
                "is registered in the research record but cited by no page",
            ))
    for key, sequence in sorted(model.sequences.items()):
        if not model.pages_for_sequence(key):
            findings.append(Finding(
                "sequence-unused", "note", f"sequence {key}",
                "appears in the scene ledger but no manifest page is assigned to it",
            ))
    return findings


def by_severity(model: CrossReference, severity: str) -> list[Finding]:
    return [item for item in model.findings if item.severity == severity]


def build() -> CrossReference:
    chapters = read_chapters()
    ledger_keys = read_ledger_keys()
    packets = read_packet_registry()
    known_keys = set(ledger_keys) | set(packets)

    # Page front matter is read twice: once to discover keys the research record
    # never registered, then again so panel lines can resolve those keys too.
    declared_keys = {
        key
        for page in read_pages(known_keys)
        for key in page.declared_sources
    }
    known_keys |= declared_keys
    pages = read_pages(known_keys)

    sources = {
        key: Source(
            key=key,
            title=packets.get(key, ("", "", []))[0],
            url=packets.get(key, ("", "", []))[1],
            ledger_note=ledger_keys.get(key, ""),
            packet_notes=tuple(packets.get(key, ("", "", []))[2]),
        )
        for key in sorted(known_keys)
    }
    model = CrossReference(
        chapters=chapters,
        pages=pages,
        sources=sources,
        sequences=read_sequences(pages, known_keys),
    )
    model.findings = audit(model)
    return model


def to_json(model: CrossReference) -> dict[str, object]:
    return {
        "chapters": [
            {"id": item.id, "title": item.title, "first_page": item.first_page, "last_page": item.last_page}
            for item in model.chapters
        ],
        "pages": [
            {
                "id": page.id, "chapter": page.chapter, "sequence": page.sequence,
                "title": page.title, "status": page.status, "scripted": page.scripted,
                "provenance_statuses": list(page.statuses),
                "sources": list(page.sources),
                "declared": [{"status": status, "sources": list(keys)} for status, keys in page.declared],
                "panels": [
                    {
                        "number": panel.number, "statuses": list(panel.statuses),
                        "sources": list(panel.sources), "note": panel.note,
                    }
                    for panel in page.panels
                ],
                "locations": list(page.locations),
                "continuity_checks": list(page.continuity_checks),
            }
            for page in model.pages
        ],
        "sources": [
            {
                "key": source.key, "title": source.title, "url": source.url,
                "registered": source.registered, "ledger_note": source.ledger_note,
                "packets": [{"chapter": chapter, "note": note} for chapter, note in source.packet_notes],
                "pages": [page.id for page in model.pages_for_source(source.key)],
                "provenance_statuses": model.statuses_for_source(source.key),
            }
            for source in model.sources.values()
        ],
        "provenance": [
            {
                "status": status, "note": STATUS_NOTES.get(status, ""),
                "pages": [page.id for page in model.pages_for_status(status)],
                "sources": model.sources_for_status(status),
            }
            for status in PROVENANCE_STATUSES
        ],
        "sequences": [
            {
                "key": sequence.key, "label": sequence.label,
                "first_page": sequence.first_page, "last_page": sequence.last_page,
                "event": sequence.event, "provenance_statuses": list(sequence.statuses),
                "rule": sequence.rule, "sources": list(sequence.sources),
                "pages": [page.id for page in model.pages_for_sequence(sequence.key)],
            }
            for sequence in model.sequences.values()
        ],
        "findings": [
            {"kind": item.kind, "severity": item.severity, "subject": item.subject, "message": item.message}
            for item in model.findings
        ],
    }


def print_report(model: CrossReference) -> None:
    scripted = [page for page in model.pages if page.scripted]
    panels = sum(len(page.panels) for page in scripted)
    print(
        f"{len(model.pages)} manifest pages ({len(scripted)} scripted, {panels} panels), "
        f"{len(model.sources)} citation keys, {len(model.sequences)} ledger sequences."
    )
    print("\nSources by page count")
    for key in sorted(model.used_sources(), key=lambda item: (-len(model.pages_for_source(item)), item)):
        source = model.sources[key]
        mark = "" if source.registered else "  [unregistered]"
        print(f"  {key:<18} {len(model.pages_for_source(key)):>3} pages  {source.label[:60]}{mark}")
    unused = [key for key, source in model.sources.items() if source.registered and key not in set(model.used_sources())]
    if unused:
        print(f"  (registered but uncited: {', '.join(unused)})")

    print("\nProvenance statuses by page count")
    for status in PROVENANCE_STATUSES:
        pages = model.pages_for_status(status)
        print(f"  {status:<18} {len(pages):>3} pages  {len(model.sources_for_status(status)):>2} sources")

    print("\nSequences")
    for sequence in model.sequences.values():
        pages = model.pages_for_sequence(sequence.key)
        print(
            f"  {sequence.label:<14} pages {sequence.first_page:>3}–{sequence.last_page:<3} "
            f"{len(pages):>2} assigned  {'+'.join(sequence.statuses) or '—'}"
        )

    counts = {level: len(by_severity(model, level)) for level in SEVERITIES}
    print("\nFindings: " + ", ".join(f"{counts[level]} {level}s" for level in SEVERITIES))
    for level in SEVERITIES:
        for item in by_severity(model, level):
            print(f"  [{item.severity}] {item.subject}: {item.message}")


def check_provenance_regressions() -> None:
    """Unknown or absent panel tags must never disappear from the audit."""
    for label, valid in [("`documented` — a public claim", True),
                         ("`documented claim` — a public claim", False),
                         ("`inferred` + `inventd` — a synthesis", False),
                         ("no tag", False)]:
        panels = read_panels("## Panel 1\n**Provenance:** " + label, set())
        page = Page("001", 1, "prologue", "1", "Fixture", "review", True,
                    declared=(("documented", ()), ("inferred", ())), panels=panels)
        model = CrossReference([], [page], {}, {})
        invalid = any(f.kind == "panel-provenance-invalid" for f in audit(model))
        assert invalid != valid, label
    assert not read_panels("## Panel 1\nNo provenance line", set())[0].statuses
    grouped = read_panels("## Panels 1–9\n**Provenance:** `compressed` — `METR`", {"METR"})
    assert [panel.number for panel in grouped] == list(range(1, 10))
    assert all(panel.statuses == ("compressed",) and panel.sources == ("METR",) for panel in grouped)
    # A provenance line in page notes cannot substitute for an absent panel field.
    missing = read_panels("## Panel 1\nNo provenance\n## Page notes\n"
                          "**Provenance:** `documented` — `METR`", {"METR"})
    assert not missing[0].statuses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "command", nargs="?", default="report", choices=("report", "check", "json"),
        help="report prints the cross reference, check exits non-zero on errors, json emits the model",
    )
    parser.add_argument("--out", type=Path, help="write JSON output to this path instead of stdout")
    parser.add_argument(
        "--strict", action="store_true",
        help="make check fail on warnings as well as errors",
    )
    args = parser.parse_args(argv)

    model = build()
    if args.command == "json":
        payload = json.dumps(to_json(model), indent=2, ensure_ascii=False) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload, encoding="utf-8")
            print(f"Wrote {args.out}")
        else:
            sys.stdout.write(payload)
        return 0

    if args.command == "check":
        check_provenance_regressions()
        blocking = by_severity(model, "error")
        if args.strict:
            blocking += by_severity(model, "warning")
        for level in SEVERITIES:
            items = by_severity(model, level)
            if items:
                print(f"{level.title()}s:")
                for item in items:
                    print(f"- {item.subject}: {item.message}")
        if blocking:
            print(f"Cross-reference check failed: {len(blocking)} blocking findings.")
            return 1
        print(
            f"Cross-reference check passed: {len(model.pages)} pages, {len(model.used_sources())} cited "
            f"sources, {len(model.sequences)} sequences resolve."
        )
        return 0

    print_report(model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
