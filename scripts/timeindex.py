#!/usr/bin/env python3
"""Time-based index over every dated thing the repository holds.

The index answers, for any span of story time: what happened, which sources
contain information about the span ranked by primacy, what those sources say
exactly (registered ``exact_strings`` text or 256t pointers), and what the book
depicts at that time. It is built for programs and agents: ``query`` prints
JSON, ``build`` writes ``data/time-index.json``, and ``report`` prints Markdown.

Inputs, all derived except the first:

* ``data/time-spans.tsv`` — the hand-maintained registry. One row per dated
  fact about a source: ``kind`` is ``covers`` (the source contains information
  about a span), ``published`` (the source itself appeared at an instant), or
  ``event`` (the source attests an occurrence). ``tier`` ranks primacy:
  ``primary``, ``reporting``, ``analysis``, ``internal``.
* ``research/timeline.md`` — the story-world event tables; every ``When`` cell
  is parsed, and ``check`` fails on one it cannot read.
* ``research/collusion/*.jsonl`` — the wiki edit corpus, aggregated to per-day
  counts. Rows themselves are never copied into the index; ``query --rows``
  streams them on demand, including revision ``body`` text, which is the exact
  wording.
* ``content/**/*.md`` — front-matter ``story_time`` (what a page depicts) and
  ``exact_strings`` registrations (what a source says exactly), plus
  ``provenance`` source keys (which pages cite a source).
* ``data/256t-sources.tsv`` — the external source registry (id, url, kind,
  note).
* ``editions/three-stream/manuscript/*.json`` — production-time beats.
* ``research/scene-provenance.md`` and ``research/chapter-source-packets/*.md``
  — the citation-key registries an id may resolve against.

Times are UTC throughout. Everything here is standard library only.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import crossref

ROOT = Path(__file__).resolve().parents[1]
SPANS_TSV = ROOT / "data" / "time-spans.tsv"
INDEX_JSON = ROOT / "data" / "time-index.json"
TIMELINE_MD = ROOT / "research" / "timeline.md"
SOURCES_TSV = ROOT / "data" / "256t-sources.tsv"
COLLUSION = ROOT / "research" / "collusion"
MANUSCRIPTS = ROOT / "editions" / "three-stream" / "manuscript"
CONTENT = ROOT / "content"

SCHEMA = "time-index/1"
TIERS = ("primary", "reporting", "analysis", "internal")
SPAN_KINDS = ("covers", "published", "event")
SPANS_HEADER = ("id", "tier", "kind", "start", "end", "basis")

MONTHS = {
    name: number
    for number, name in enumerate(
        ("January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"), start=1)
}
MONTHS.update({name[:3]: number for name, number in list(MONTHS.items())})

# Part-of-day windows used when a source says "morning", "late", and the like.
# They are conventional, not measured: the event keeps its original wording.
DAY_PARTS = {
    "night": (0, 6), "morning": (6, 12), "afternoon": (12, 18),
    "evening": (18, 24), "late": (18, 24), "early": (0, 6),
}


# --------------------------------------------------------------------- time


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_moment(text: str) -> tuple[datetime, str] | None:
    """Parse a partial ISO moment. Returns (start, precision)."""
    text = text.strip().replace(" ", "T").rstrip("Z")
    match = re.fullmatch(
        r"(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?)?)?)?",
        text)
    if not match:
        return None
    year, month, day, hour, minute, second = match.groups()
    if month is None:
        return datetime(int(year), 1, 1), "year"
    if day is None:
        return datetime(int(year), int(month), 1), "month"
    if hour is None:
        return datetime(int(year), int(month), int(day)), "day"
    precision = "second" if second is not None else "minute"
    return (datetime(int(year), int(month), int(day),
                     int(hour), int(minute), int(second or 0)), precision)


def moment_extent(start: datetime, precision: str) -> datetime:
    """The exclusive end of the span a partially specified moment covers."""
    if precision == "year":
        return start.replace(year=start.year + 1)
    if precision == "month":
        year, month = (start.year + 1, 1) if start.month == 12 else (start.year, start.month + 1)
        return start.replace(year=year, month=month)
    if precision == "day":
        return start + timedelta(days=1)
    if precision == "minute":
        return start + timedelta(minutes=1)
    return start + timedelta(seconds=1)


def parse_span(spec: str) -> tuple[datetime, datetime]:
    """Parse a query span into [start, end).

    Accepts a single moment at any precision (``2026``, ``2026-05``,
    ``2026-05-11``, ``2026-05-11T08:30Z``) or two moments joined by ``..`` or
    ``/``, where the end keeps its own precision: ``2026-05-11..2026-05-13``
    runs through the end of 13 May.
    """
    for separator in ("..", "/"):
        if separator in spec:
            left, right = spec.split(separator, 1)
            first, second = parse_moment(left), parse_moment(right)
            if first and second:
                return first[0], moment_extent(*second)
            break
    parsed = parse_moment(spec)
    if not parsed:
        raise ValueError(
            f"cannot read {spec!r} as a time span; use YYYY[-MM[-DD]] or A..B")
    return parsed[0], moment_extent(*parsed)


def overlaps(start: datetime, end: datetime, other_start: datetime, other_end: datetime) -> bool:
    return start < other_end and other_start < end


# ------------------------------------------------------------- timeline.md
#
# The ``When`` column is prose on purpose. Every observed form is handled;
# anything new fails ``check`` rather than being silently dropped.
#
#   20 Apr 07:59        instant        12–13 May / 28–30 Aug   day range
#   9 Jul 08:30–20:16   clock range    11 Jul ~05–15           approximate hour range
#   9 Jul morning       day part       9 Jul +1h               relative to the row above
#   Late 4 Jul          qualifier      12 Jul ~01:30           approximate instant


@dataclass(frozen=True)
class When:
    start: datetime
    end: datetime
    precision: str          # minute | hour | part-of-day | day | days
    approximate: bool


def parse_when(text: str, *, year: int = 2026) -> When | None:
    original = text
    approximate = False
    qualifier = re.match(r"^(Late|Early)\s+", text, re.IGNORECASE)
    part = None
    if qualifier:
        part = qualifier.group(1).lower()
        text = text[qualifier.end():]
        approximate = True
    if text.startswith("~"):
        approximate = True
        text = text[1:].strip()

    match = re.fullmatch(
        r"(\d{1,2})\s*[–—-]\s*(\d{1,2})\s+([A-Za-z]{3,9})(?:\s+(\d{4}))?\s*(.*)",
        text)
    if match:
        first_day, last_day, month_name, year_text, rest = match.groups()
        last_month = month = MONTHS.get(month_name.capitalize())
    else:
        match = re.fullmatch(
            r"(\d{1,2})\s+([A-Za-z]{3,9})"
            r"(?:\s*[–—-]\s*(\d{1,2})\s+([A-Za-z]{3,9}))?"
            r"(?:\s+(\d{4}))?\s*(.*)", text)
        if not match:
            return None
        first_day, month_name, last_day, last_month_name, year_text, rest = match.groups()
        month = MONTHS.get(month_name.capitalize())
        last_month = MONTHS.get(last_month_name.capitalize()) if last_month_name else month
    if month is None or last_month is None:
        return None
    year = int(year_text) if year_text else year
    rest = rest.strip()

    def moment(day: int, mon: int) -> datetime | None:
        try:
            return datetime(year, mon, int(day))
        except ValueError:
            return None

    start = moment(first_day, month)
    end = moment(last_day, last_month) + timedelta(days=1) if last_day else (
        start + timedelta(days=1) if start else None)
    if start is None or end is None:
        return None
    precision = "day" if not last_day else "days"

    relative = re.fullmatch(r"\+(\d+)h", rest)
    clock_range = re.fullmatch(r"~?(\d{1,2})(?::(\d{2}))?\s*[–—-]\s*(\d{1,2})(?::(\d{2}))?", rest)
    clock = re.fullmatch(r"~?(\d{1,2}):(\d{2})", rest)
    if rest.startswith("~"):
        approximate = True
    if part or rest.lower() in DAY_PARTS:
        low, high = DAY_PARTS[part or rest.lower()]
        start, end = start + timedelta(hours=low), start + timedelta(hours=high)
        precision, approximate = "part-of-day", True
    elif relative:
        end = start + timedelta(hours=int(relative.group(1)))
        precision, approximate = "part-of-day", True
    elif clock_range:
        h1, m1, h2, m2 = clock_range.groups()
        start = start.replace(hour=int(h1), minute=int(m1 or 0))
        end = (end - timedelta(days=1)).replace(hour=int(h2), minute=int(m2 or 0))
        precision = "hour" if m1 is None and m2 is None else "minute"
        if "~" in rest:
            approximate = True
    elif clock:
        start = start.replace(hour=int(clock.group(1)), minute=int(clock.group(2)))
        end = start + timedelta(minutes=1)
        precision = "minute"
    elif rest:
        return None
    return When(start, end, precision, approximate)


def read_timeline() -> tuple[list[dict], list[str]]:
    """Story events from research/timeline.md's tables, plus unparsed rows."""
    events: list[dict] = []
    problems: list[str] = []
    section = ""
    row_number = 0
    for line in TIMELINE_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line.lstrip("#").strip()
            continue
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4 or cells[0] in {"When", "---"} or set(cells[0]) <= {"-", ":"}:
            continue
        row_number += 1
        when_text, track, title, source_note = cells
        when = parse_when(when_text)
        if when is None:
            problems.append(f"timeline row {row_number}: cannot parse When {when_text!r}")
            continue
        events.append({
            "id": f"timeline:{row_number}",
            "kind": "story-event",
            "start": iso(when.start),
            "end": iso(when.end),
            "precision": when.precision,
            "approximate": when.approximate,
            "when": when_text,
            "title": title,
            "track": track,
            "section": section,
            "sources": re.findall(r"`([A-Z][A-Z0-9-]*)`", source_note),
            "source_note": source_note,
        })
    return events, problems


# ------------------------------------------------------------ collusion cut


def corpus_days() -> dict[str, dict]:
    """Per-day activity counts over the wiki edit corpus. No bodies."""
    days: dict[str, dict] = {}

    def day(row_time: str) -> dict:
        return days.setdefault(row_time[:10], {
            "events": 0, "saves": 0, "deletes": 0, "reverts": 0, "probes": 0,
            "revisions": 0, "pages_created": 0, "pages_last_active": 0,
            "pages_touched": 0, "labels": 0,
        })

    touched: dict[str, set] = {}
    labels_seen: dict[str, set] = {}
    events_path = COLLUSION / "events.jsonl"
    if events_path.exists():
        for line in events_path.open(encoding="utf-8"):
            row = json.loads(line)
            bucket = day(row["time"])
            bucket["events"] += 1
            kind = row.get("event_type", "")
            if kind in ("save", "delete", "revert", "probe"):
                bucket[kind + "s"] += 1
            ref = row.get("page_key") or (row.get("revision_ref") or "").split("@")[0]
            if ref:
                touched.setdefault(row["time"][:10], set()).add(ref)
            if row.get("actor_label"):
                labels_seen.setdefault(row["time"][:10], set()).add(row["actor_label"])
    revisions_path = COLLUSION / "revisions.jsonl"
    if revisions_path.exists():
        for line in revisions_path.open(encoding="utf-8"):
            row = json.loads(line)
            stamp = row.get("pref_ts") or row.get("time", "")
            if not stamp:
                continue
            bucket = day(stamp)
            bucket["revisions"] += 1
            touched.setdefault(stamp[:10], set()).add(row.get("page_key", ""))
            labels_seen.setdefault(stamp[:10], set()).add(row.get("label") or "")
    pages_path = COLLUSION / "pages.jsonl"
    if pages_path.exists():
        for line in pages_path.open(encoding="utf-8"):
            row = json.loads(line)
            if row.get("first_write"):
                day(row["first_write"])["pages_created"] += 1
            if row.get("last_write"):
                day(row["last_write"])["pages_last_active"] += 1
    for name, pages in touched.items():
        days[name]["pages_touched"] = len(pages - {""})
    for name, handles in labels_seen.items():
        days[name]["labels"] = len(handles - {""})
    return days


def corpus_rows(start: datetime, end: datetime, limit: int,
                body_bytes: int) -> tuple[list[dict], bool]:
    """Corpus rows inside a span, streamed on demand. Revision ``body`` is the
    exact wording the wiki stored; it is truncated at ``body_bytes``."""
    rows: list[dict] = []
    truncated = False

    def inside(stamp: str) -> bool:
        parsed = parse_moment(stamp)
        return bool(parsed) and start <= parsed[0] < end

    for name, emit in (
        ("event", lambda row: {
            "id": row.get("event_id"), "kind": "event",
            "type": row.get("event_type"), "time": row.get("time"),
            "label": row.get("actor_label") or row.get("label"),
            "page": row.get("page_key"),
            "refs": row.get("source_refs"),
        }),
        ("revision", lambda row: {
            "id": row.get("rev_id"), "kind": "revision",
            "time": row.get("pref_ts") or row.get("time"),
            "label": row.get("label"), "page": row.get("page_key"),
            "seq": row.get("seq"),
            "body": (row.get("body") or "")[:body_bytes] or None,
            "body_truncated": len(row.get("body") or "") > body_bytes,
        }),
    ):
        path = COLLUSION / f"{name}s.jsonl"
        if not path.exists():
            continue
        emitted = 0
        for line in path.open(encoding="utf-8"):
            row = json.loads(line)
            stamp = row.get("time") or row.get("pref_ts") or ""
            if not inside(stamp):
                continue
            if emitted >= limit:
                truncated = True
                break
            rows.append(emit(row))
            emitted += 1
    rows.sort(key=lambda row: row.get("time") or "")
    return rows[:limit], truncated


# ------------------------------------------------------------------ content


def parse_story_time(text: str) -> tuple[datetime | None, datetime | None]:
    """The ``story_time`` vocabulary is richer than ISO: ``A/B`` ranges,
    ``creator-relative-2026-09-04`` embeddings, ``through-2026-08-30`` bounds,
    ``2026-08-early`` parts of a month, and labels like ``invented-composite``
    that name no date at all. Returns (start, end); either may be None."""
    start: datetime | None = None
    end: datetime | None = None
    for part in text.split("/"):
        part = part.strip()
        if not part:
            continue
        direct = parse_moment(part)
        if direct:
            moment, precision = direct
            start = moment if start is None else min(start, moment)
            end = moment_extent(moment, precision) if end is None else max(end, moment_extent(moment, precision))
            continue
        through = re.fullmatch(r"through-(\d{4}-\d{2}(?:-\d{2})?)", part)
        embedded = re.search(r"(\d{4}-\d{2}(?:-\d{2})?)(?:-(early|mid|late))?$", part)
        if through:
            bound = parse_moment(through.group(1))
            if bound:
                bound_end = moment_extent(*bound)
                end = bound_end if end is None else max(end, bound_end)
        elif embedded:
            bound = parse_moment(embedded.group(1))
            if bound:
                moment, precision = bound
                qualifier = embedded.group(2)
                if qualifier and precision == "month":
                    third = timedelta(days=10)
                    lo = {"early": moment, "mid": moment + third,
                          "late": moment + 2 * third}[qualifier]
                    hi = {"early": moment + third, "mid": moment + 2 * third,
                          "late": moment_extent(moment, precision)}[qualifier]
                    start = lo if start is None else min(start, lo)
                    end = hi if end is None else max(end, hi)
                else:
                    start = moment if start is None else min(start, moment)
                    extent = moment_extent(moment, precision)
                    end = extent if end is None else max(end, extent)
    return start, end


def read_content() -> tuple[list[dict], dict[str, list[dict]], dict[str, list[str]]]:
    """Depictions (``story_time``), registered exact strings, and page->sources."""
    depictions: list[dict] = []
    strings: dict[str, list[dict]] = {}
    pages_by_source: dict[str, list[str]] = {}
    for path in sorted(CONTENT.rglob("*.md")):
        relative = path.relative_to(ROOT).as_posix()
        metadata = crossref.front_matter(path.read_text(encoding="utf-8"))
        if not metadata:
            continue
        story_time = re.search(r"^story_time:[ \t]*(\S+)", metadata, re.MULTILINE)
        title = re.search(r'^title:[ \t]*"?([^"\n]+)"?', metadata, re.MULTILINE)
        page_match = re.fullmatch(r"content/pages/(\d{3})\.md", relative)
        page_id = page_match.group(1) if page_match else None
        provenance = re.search(r"^provenance:\s*$((?:\n[ \t]+.+)*)", metadata, re.MULTILINE)
        sources = []
        if provenance:
            sources = re.findall(r"source:[ \t]*([A-Za-z0-9-]+)", provenance.group(1))
        if story_time:
            start, end = parse_story_time(story_time.group(1))
            depictions.append({
                "id": f"page:{page_id}" if page_id else f"file:{relative}",
                "kind": "story-page" if page_id else "content",
                "start": iso(start) if start else None,
                "end": iso(end) if end else None,
                "when": story_time.group(1),
                "title": title.group(1).strip() if title else relative,
                "path": relative,
                "sources": sources,
            })
        for key in sources:
            if page_id:
                pages_by_source.setdefault(key, []).append(page_id)
        registered, _ = crossref.read_exact_strings(metadata)
        for entry in registered:
            record = {name: entry[name] for name in ("source", "locator", "verification", "rights") if entry.get(name)}
            if entry.get("text"):
                record["text"] = entry["text"]
            if entry.get(crossref.POINTER_FIELD):
                record["pointer"] = entry[crossref.POINTER_FIELD]
            record["registered_on"] = page_id or relative
            strings.setdefault(entry.get("source", ""), []).append(record)
    return depictions, strings, pages_by_source


# The isolated edition cites shared sources under its own keys. Aliasing is
# mechanical resolution, not interpretation: the key names the same document.
EDITION_ALIASES = {
    "GS-REPORT": "gemstuffer-report",
    "GS-STATUS": "gemstuffer-status",
    "GS-SOCKET": "gemstuffer-socket",
    "GS-EMAIL": "gemstuffer-email-fix",
    "GS-CACHE": "gemstuffer-cache-advisory",
    "AL-SUB": "alabama-subpoena",
    "AL-PR": "alabama-press-release",
}


def read_editions() -> tuple[list[dict], dict[str, dict]]:
    """Production-time beats, plus the edition-local source keys they carry.

    Edition keys are self-describing — every one bears a locator and an
    ``available`` date — so each becomes an internal source record dated by
    first availability, unless an alias lands it on a canonical source.
    """
    events: list[dict] = []
    edition_sources: dict[str, dict] = {}
    if not MANUSCRIPTS.exists():
        return events, edition_sources
    for path in sorted(MANUSCRIPTS.glob("*.json")):
        try:
            scenes = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for scene in scenes if isinstance(scenes, list) else []:
            for beat in scene.get("beats", []):
                start_text = beat.get("time_start")
                if not start_text:
                    continue
                parsed = parse_moment(str(start_text))
                if not parsed:
                    continue
                end = parse_moment(str(beat.get("time_end") or start_text))
                locators = {
                    source.get("key"): source.get("locator")
                    for source in beat.get("sources", []) if source.get("key")
                }
                for source in beat.get("sources", []):
                    key = source.get("key")
                    if not key:
                        continue
                    record = edition_sources.setdefault(
                        key, {"available": None, "locators": set(),
                              "registered_in": "editions/three-stream"})
                    available = parse_moment(str(source.get("available", "")))
                    if available:
                        stamp = iso(available[0])
                        if record["available"] is None or stamp < record["available"]:
                            record["available"] = stamp
                    if source.get("locator"):
                        record["locators"].add(source["locator"])
                events.append({
                    "id": f"beat:{scene.get('id')}/{beat.get('id')}",
                    "kind": "edition-beat",
                    "start": iso(parsed[0]),
                    "end": iso(moment_extent(*end)) if end else iso(moment_extent(*parsed)),
                    "title": beat.get("frame") or beat.get("id") or "",
                    "sources": sorted(locators),
                    "resolved_sources": sorted(
                        {EDITION_ALIASES.get(key, key) for key in locators}),
                    "detail": {"manuscript": path.name, "locators": locators,
                               "evidence_status": beat.get("evidence_status")},
                })
    for record in edition_sources.values():
        record["locators"] = sorted(record["locators"])
    return events, edition_sources


# ----------------------------------------------------------------- registry


def read_span_rows() -> tuple[list[dict], list[str]]:
    """The hand-maintained coverage registry, plus malformed rows."""
    rows: list[dict] = []
    problems: list[str] = []
    if not SPANS_TSV.exists():
        return rows, [f"missing {SPANS_TSV.relative_to(ROOT)}"]
    with SPANS_TSV.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, [])
        if tuple(header) != SPANS_HEADER:
            problems.append(
                f"{SPANS_TSV.relative_to(ROOT)} header must be {'/'.join(SPANS_HEADER)}")
            return rows, problems
        for number, fields in enumerate(reader, start=2):
            if not fields or fields[0].startswith("#"):
                continue
            if len(fields) != len(SPANS_HEADER):
                problems.append(f"{SPANS_TSV.name}:{number}: expected {len(SPANS_HEADER)} columns")
                continue
            row = dict(zip(SPANS_HEADER, fields))
            label = f"{SPANS_TSV.name}:{number} ({row['id']})"
            if row["tier"] not in TIERS:
                problems.append(f"{label}: tier must be one of {'/'.join(TIERS)}")
            if row["kind"] not in SPAN_KINDS:
                problems.append(f"{label}: kind must be one of {'/'.join(SPAN_KINDS)}")
            start = parse_moment(row["start"])
            if not start:
                problems.append(f"{label}: cannot parse start {row['start']!r}")
                continue
            end = parse_moment(row["end"]) if row["end"] else None
            if row["end"] and not end:
                problems.append(f"{label}: cannot parse end {row['end']!r}")
                continue
            row["_start"], row["_precision"] = start
            if end:
                row["_end"] = end[0]
            elif row["kind"] == "covers":
                row["_end"] = moment_extent(*start)
            else:
                row["_end"] = moment_extent(*start)
            if row["_end"] < row["_start"]:
                problems.append(f"{label}: end precedes start")
            rows.append(row)
    return rows, problems


def source_directory() -> dict[str, dict]:
    """Everything an id can resolve to: vault ids, citation keys, paths."""
    directory: dict[str, dict] = {}
    if SOURCES_TSV.exists():
        with SOURCES_TSV.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                directory[row["id"]] = {
                    "registered_in": "data/256t-sources.tsv",
                    "url": row.get("url", ""), "kind": row.get("kind", ""),
                    "title": row.get("note", "").split(";")[0].strip(),
                    "note": row.get("note", ""),
                }
    for key, description in crossref.read_ledger_keys().items():
        directory.setdefault(key, {
            "registered_in": "research/scene-provenance.md", "title": description})
    for key, (title, url, _notes) in crossref.read_packet_registry().items():
        entry = directory.setdefault(key, {"registered_in": "research/chapter-source-packets"})
        entry.setdefault("title", title)
        if url:
            entry.setdefault("url", url)
    return directory


def build_sources(rows: list[dict], directory: dict[str, dict],
                  strings: dict[str, list[dict]],
                  pages_by_source: dict[str, list[str]]) -> tuple[dict[str, dict], list[dict], list[str]]:
    """Source records from registry rows; unattributed registry events out."""
    sources: dict[str, dict] = {}
    events: list[dict] = []
    problems: list[str] = []
    tier_by_id: dict[str, str] = {}
    for row in rows:
        key = row["id"]
        if key.startswith("path:"):
            target = ROOT / key[5:]
            if not target.exists():
                problems.append(f"time-spans.tsv: {key} does not exist")
        elif key not in directory:
            problems.append(
                f"time-spans.tsv: id {key!r} is not in 256t-sources.tsv, "
                "scene-provenance.md, or the chapter packets")
        if key in tier_by_id and tier_by_id[key] != row["tier"]:
            problems.append(
                f"time-spans.tsv: {key} carries both tier {tier_by_id[key]} and {row['tier']}")
        tier_by_id.setdefault(key, row["tier"])
        record = sources.setdefault(key, {
            "id": key, "tier": row["tier"],
            "covers": [], "published": [], "exact_strings": [], "pages": [],
        })
        span = {
            "start": iso(row["_start"]), "end": iso(row["_end"]),
            "when": row["start"] + (f"–{row['end']}" if row["end"] else ""),
            "basis": row["basis"],
        }
        if row["kind"] == "event":
            events.append({
                "id": f"span-event:{key}:{iso(row['_start'])}",
                "kind": "story-event",
                "start": span["start"], "end": span["end"],
                "precision": row["_precision"], "approximate": False,
                "title": row["basis"], "sources": [key],
                "source_note": f"attested by {key}",
            })
        else:
            record[row["kind"]].append(span)
    for key, record in sources.items():
        meta = directory.get(key, {})
        record.update({name: meta[name] for name in ("url", "title", "note", "registered_in") if meta.get(name)})
        record["exact_strings"] = sorted(strings.get(key, []), key=lambda item: item.get("registered_on", ""))
        record["pages"] = sorted(pages_by_source.get(key, []))
        record["covers"].sort(key=lambda span: span["start"])
        record["published"].sort(key=lambda span: span["start"])
    return sources, events, problems


# -------------------------------------------------------------------- index


def build() -> dict:
    timeline_events, timeline_problems = read_timeline()
    depictions, strings, pages_by_source = read_content()
    rows, span_problems = read_span_rows()
    edition_events, edition_sources = read_editions()
    directory = source_directory()
    for key, record in edition_sources.items():
        directory.setdefault(key, {
            "registered_in": record["registered_in"],
            "title": (record["locators"][0] if record["locators"] else key)})
    # A source's `available` stamp is a publication-style instant from the
    # edition's point of view; it lands on the canonical id when aliased.
    declared_tiers = {row["id"]: row["tier"] for row in rows}
    for key, record in edition_sources.items():
        if not record["available"]:
            continue
        canonical = EDITION_ALIASES.get(key, key)
        moment = parse_moment(record["available"])
        if not moment:
            continue
        rows.append({
            "id": canonical,
            "tier": declared_tiers.get(canonical, "internal"),
            "kind": "published",
            "start": record["available"], "end": "",
            "basis": f"available to edition beats as {key}",
            "_start": moment[0], "_precision": moment[1],
            "_end": moment_extent(*moment),
        })
    sources, registry_events, source_problems = build_sources(
        rows, directory, strings, pages_by_source)
    problems = timeline_problems + span_problems + source_problems
    days = corpus_days()
    events = timeline_events + registry_events + edition_events
    events.sort(key=lambda event: (event["start"], event["id"]))
    depictions.sort(key=lambda event: (event["start"] or "9999", event["id"]))
    stamps = ([event["start"] for event in events]
              + [event["start"] for event in depictions if event["start"]]
              + list(days))
    ends = ([event["end"] for event in events]
            + [event["end"] for event in depictions if event["end"]]
            + list(days))
    index = {
        "schema": SCHEMA,
        "range": {
            "start": min(stamps) if stamps else None,
            "end": max(ends) if ends else None,
        },
        "sources": dict(sorted(sources.items())),
        "events": events,
        "depictions": depictions,
        "corpus_days": dict(sorted(days.items())),
    }
    if problems:
        index["problems"] = problems
    return index


def query(index: dict, spec: str, *, rows: int = 0, body_bytes: int = 4000) -> dict:
    start, end = parse_span(spec)

    def inside(entry: dict) -> bool:
        if not entry.get("start") or not entry.get("end"):
            return False
        entry_start = datetime.strptime(entry["start"], "%Y-%m-%dT%H:%M:%SZ")
        entry_end = datetime.strptime(entry["end"], "%Y-%m-%dT%H:%M:%SZ")
        return overlaps(start, end, entry_start, entry_end)

    corpus_overlap = {
        day: counts for day, counts in index["corpus_days"].items()
        if start.strftime("%Y-%m-%d") <= day <= (end - timedelta(microseconds=1)).strftime("%Y-%m-%d")
    }
    totals = {
        key: sum(counts.get(key, 0) for counts in corpus_overlap.values())
        for key in ("events", "saves", "deletes", "reverts", "probes",
                    "revisions", "pages_created", "pages_touched", "labels")
    }
    sources = []
    for key, record in index["sources"].items():
        covering = [span for span in record["covers"]
                    if overlaps(start, end,
                                datetime.strptime(span["start"], "%Y-%m-%dT%H:%M:%SZ"),
                                datetime.strptime(span["end"], "%Y-%m-%dT%H:%M:%SZ"))]
        published = [span for span in record["published"]
                     if start <= datetime.strptime(span["start"], "%Y-%m-%dT%H:%M:%SZ") < end]
        if not covering and not published:
            continue
        sources.append({
            "id": key, "tier": record["tier"], "title": record.get("title", ""),
            "url": record.get("url", ""), "registered_in": record.get("registered_in", ""),
            "covers": covering, "published_in_span": published,
            "exact_strings": record["exact_strings"], "pages": record["pages"],
        })
    sources.sort(key=lambda record: (TIERS.index(record["tier"]), record["id"]))
    result = {
        "span": {"input": spec, "start": iso(start), "end": iso(end)},
        "events": [event for event in index["events"] if inside(event)],
        "depictions": [event for event in index["depictions"] if inside(event)],
        "corpus": {"totals": totals, "days": corpus_overlap},
        "sources": sources,
    }
    if rows:
        sample, truncated = corpus_rows(start, end, rows, body_bytes)
        result["corpus"]["rows"] = sample
        result["corpus"]["rows_truncated"] = truncated
    return result


# ------------------------------------------------------------------ report


def report(index: dict) -> str:
    lines = [
        "# Time index", "",
        "Generated by `python3 scripts/timeindex.py report`. Do not edit; "
        "the inputs are `data/time-spans.tsv`, `research/timeline.md`, the "
        "collusion corpus, content front matter, and the edition manuscripts.",
        "",
        f"Coverage: {index['range']['start']} to {index['range']['end']}.",
        f"{len(index['events'])} events, {len(index['depictions'])} depictions, "
        f"{len(index['sources'])} sources, {len(index['corpus_days'])} corpus days.",
        "",
        "## Sources by tier", "",
    ]
    for tier in TIERS:
        members = [record for record in index["sources"].values() if record["tier"] == tier]
        if not members:
            continue
        lines.append(f"### {tier.capitalize()}")
        lines.append("")
        for record in members:
            spans = [span["when"] for span in record["covers"]]
            published = sorted({span["start"][:10] for span in record["published"]})
            detail = []
            if spans:
                detail.append("covers " + ", ".join(spans))
            if published:
                detail.append("published " + ", ".join(published))
            title = record.get("title") or record.get("note", "")[:80]
            lines.append(f"- `{record['id']}` — {title}; " + "; ".join(detail))
        lines.append("")
    lines += ["## Days with recorded activity", "",
              "| Day | Story events | Depictions | Corpus events | Corpus revisions | Covering sources |",
              "| --- | --- | --- | ---: | ---: | --- |"]
    all_days = sorted(
        set(index["corpus_days"])
        | {event["start"][:10] for event in index["events"]}
        | {event["start"][:10] for event in index["depictions"] if event["start"]})
    for day in all_days:
        start, end = parse_span(day)
        result = query(index, day)
        events = [event["title"] for event in result["events"] if event["kind"] == "story-event"]
        depictions = [f"{event['id']} {event['title']}" for event in result["depictions"]]
        covering = [f"`{record['id']}`" for record in result["sources"]
                    if record["tier"] == "primary"]
        corpus = result["corpus"]["totals"]
        lines.append(
            f"| {day} | {'; '.join(events) or '—'} | {'; '.join(depictions) or '—'} "
            f"| {corpus['events']} | {corpus['revisions']} | {', '.join(covering) or '—'} |")
    undated = [event for event in index["depictions"] if not event["start"]]
    if undated:
        lines += ["", "## Depictions with no absolute date", ""]
        for event in undated:
            lines.append(f"- `{event['id']}` {event['title']} — `{event['when']}`")
    lines.append("")
    return "\n".join(lines)


# -------------------------------------------------------------------- site
#
# build-site.py emits these as docs/time/** on internal builds only: the index
# is research-derived, and the public build excludes research/ entirely.


def _rel(depth: int, target: str) -> str:
    return "../" * depth + target


def site_pages(used_source_keys: set[str] | None = None) -> list[tuple[str, str, str]]:
    """(relative path, title, body) for the generated time section."""
    used = used_source_keys or set()
    index = build()
    pages: list[tuple[str, str, str]] = []

    def source_cell(key: str, depth: int) -> str:
        label = f"<code>{html.escape(key)}</code>"
        if key in used:
            slug = crossref.slug(key)
            return f'<a href="{html.escape(_rel(depth, "crossref/sources/" + slug + "/"))}">{label}</a>'
        return label

    def day_body(day: str, depth: int) -> str:
        result = query(index, day)
        body = [f'<h2>{day}</h2>']
        events = result["events"]
        story = [event for event in events if event["kind"] != "edition-beat"]
        beats = [event for event in events if event["kind"] == "edition-beat"]
        if story:
            rows = "".join(
                f"<tr><td>{html.escape(event['when'] if event.get('when') else event['start'][:16].replace('T', ' ') + ' UTC')}</td>"
                f"<td>{html.escape(event.get('track', ''))}</td>"
                f"<td>{html.escape(event['title'])}</td>"
                f"<td>{html.escape(event.get('source_note', ''))}</td></tr>"
                for event in story)
            body.append('<h3>Events</h3><div class="table-wrap"><table><thead>'
                        "<tr><th>When</th><th>Track</th><th>Event</th><th>Source</th></tr>"
                        f"</thead><tbody>{rows}</tbody></table></div>")
        if beats:
            items = "".join(
                f"<li>{html.escape(beat['title'])}"
                f" <code>{html.escape(beat['id'])}</code></li>"
                for beat in beats)
            body.append(
                f"<h3>Draft edition beats</h3><details><summary>{len(beats)} "
                f"manuscript scene(s) placed at this time</summary><ul>{items}</ul></details>")
        corpus = result["corpus"]["totals"]
        if corpus["events"] or corpus["revisions"]:
            body.append(
                f"<h3>Wiki edit corpus (<code>CW-EXPORT</code>)</h3><p>"
                f"{corpus['events']} events — {corpus['saves']} saves, "
                f"{corpus['deletes']} deletes, {corpus['reverts']} reverts, "
                f"{corpus['probes']} probes — across {corpus['pages_touched']} pages and "
                f"{corpus['labels']} handles; {corpus['revisions']} stored revisions, "
                f"{corpus['pages_created']} pages created. Row-level detail: "
                f"<code>python3 scripts/timeindex.py query {day} --rows 50</code>.</p>")
        if result["depictions"]:
            items = "".join(
                f'<li><a href="{html.escape(_rel(depth, "viewer/pages/" + event["id"].split(":")[1] + "/"))}">'
                f'Page {html.escape(event["id"].split(":")[1])}</a> · {html.escape(event["title"])}</li>'
                if event["kind"] == "story-page"
                else f'<li>{html.escape(event["title"])} <code>{html.escape(event.get("path", ""))}</code></li>'
                for event in result["depictions"])
            if items:
                body.append(f"<h3>Depicted on</h3><ul>{items}</ul>")
        if result["sources"]:
            rows = "".join(
                f"<tr><td>{source_cell(record['id'], depth)}</td>"
                f"<td>{html.escape(record['tier'])}</td>"
                f"<td>{html.escape(record.get('title', ''))}</td>"
                f"<td>{html.escape('; '.join(span['basis'] for span in record['covers']))}</td></tr>"
                for record in result["sources"])
            body.append('<h3>Sources covering this day</h3><div class="table-wrap"><table><thead>'
                        "<tr><th>Source</th><th>Tier</th><th>What it is</th><th>Coverage basis</th></tr>"
                        f"</thead><tbody>{rows}</tbody></table></div>")
            for record in result["sources"]:
                if not record["exact_strings"]:
                    continue
                items = "".join(
                    f"<li><code>{html.escape(string.get('text') or string.get('pointer', ''))}</code>"
                    f" — {html.escape(string.get('locator', ''))} "
                    f"({html.escape(string.get('verification', ''))}, "
                    f"{html.escape(string.get('rights', ''))})</li>"
                    for string in record["exact_strings"])
                body.append(f"<h3>Exact wording — {source_cell(record['id'], depth)}</h3><ul>{items}</ul>")
        return "".join(body)

    all_days = sorted(
        set(index["corpus_days"])
        | {event["start"][:10] for event in index["events"]}
        | {event["start"][:10] for event in index["depictions"] if event["start"]})
    rows = []
    for day in all_days:
        result = query(index, day)
        corpus = result["corpus"]["totals"]
        count = len(result["events"]) + len(result["depictions"]) + corpus["events"] + corpus["revisions"]
        rows.append(
            f'<tr><td><a href="{day}/">{day}</a></td><td>{len(result["events"])}</td>'
            f"<td>{len(result['depictions'])}</td><td>{corpus['events'] + corpus['revisions']}</td>"
            f"<td>{len(result['sources'])}</td></tr>")
    overview = (
        "<p>Everything dated in the repository, by day: story events from "
        "<code>research/timeline.md</code>, the wiki edit corpus "
        "(<code>CW-EXPORT</code>), source coverage and publication from "
        "<code>data/time-spans.tsv</code>, page depictions from "
        "<code>story_time</code> front matter, and edition beats. The same "
        "data is queryable as JSON: <code>python3 scripts/timeindex.py query "
        "2026-05-11</code>.</p>"
        f"<p>{len(index['events'])} events · {len(index['depictions'])} depictions · "
        f"{len(index['sources'])} sources · {len(all_days)} days</p>"
        '<div class="table-wrap"><table><thead><tr><th>Day</th><th>Events</th>'
        "<th>Depictions</th><th>Corpus rows</th><th>Sources</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>")
    pages.append(("time", "Time index", overview))
    for position, day in enumerate(all_days):
        neighbours = ""
        if position:
            neighbours += f'<p><a href="../{all_days[position - 1]}/">← {all_days[position - 1]}</a> '
        if position + 1 < len(all_days):
            neighbours += f'<a href="../{all_days[position + 1]}/">{all_days[position + 1]} →</a>'
        if neighbours:
            neighbours += "</p>"
        pages.append((f"time/{day}", f"Time index — {day}", neighbours + day_body(day, 2) + neighbours))
    return pages


# -------------------------------------------------------------------- check


def check(built: bool) -> list[str]:
    problems: list[str] = []
    index = build()
    problems.extend(index.get("problems", []))
    directory = source_directory()
    _, edition_sources = read_editions()
    known = set(index["sources"]) | set(directory) | set(edition_sources)
    for event in index["events"]:
        for key in event.get("sources", []):
            if key not in known:
                problems.append(
                    f"{event['id']}: source key {key!r} is not registered")
    for record in index["sources"].values():
        for string in record["exact_strings"]:
            if not string.get("text") and not string.get("pointer"):
                problems.append(
                    f"{record['id']}: exact_strings entry on "
                    f"{string.get('registered_on', '?')} has neither text nor pointer")
    if built:
        expected = json.dumps(index, indent=2, sort_keys=True) + "\n"
        if not INDEX_JSON.exists():
            problems.append(f"{INDEX_JSON.relative_to(ROOT)} missing; run timeindex.py build")
        elif INDEX_JSON.read_text(encoding="utf-8") != expected:
            problems.append(
                f"{INDEX_JSON.relative_to(ROOT)} is stale; run timeindex.py build")
    try:
        import timeindex_checks
        timeindex_checks.run()
    except AssertionError as error:
        problems.append(f"offline fixture failed: {error}")
    return problems


# ---------------------------------------------------------------------- cli


def render_query_markdown(result: dict) -> str:
    span = result["span"]
    lines = [f"## {span['input']} — {span['start']} to {span['end']}", ""]
    if result["events"]:
        lines.append("### Events")
        for event in result["events"]:
            when = event.get("when") or event["start"]
            kind = "" if event["kind"] == "story-event" else f"[{event['kind']}] "
            note = f" — {event['source_note']}" if event.get("source_note") else ""
            lines.append(f"- {when}: {kind}{event['title']}{note}")
        lines.append("")
    if result["depictions"]:
        lines.append("### Depicted on")
        for event in result["depictions"]:
            lines.append(f"- {event['id']} — {event['title']} (`{event.get('path', '')}`)")
        lines.append("")
    corpus = result["corpus"]
    if corpus["totals"]["events"] or corpus["totals"]["revisions"]:
        totals = corpus["totals"]
        lines.append(
            f"### Corpus: {totals['events']} events "
            f"({totals['saves']} saves, {totals['deletes']} deletes, "
            f"{totals['reverts']} reverts, {totals['probes']} probes), "
            f"{totals['revisions']} revisions, {totals['pages_created']} pages created")
        for row in corpus.get("rows", []):
            body = f" — {row['body']!r}" if row.get("body") else ""
            lines.append(f"- {row['time']} {row['kind']} `{row['id']}`{body}")
        lines.append("")
    if result["sources"]:
        lines.append("### Sources")
        for record in result["sources"]:
            lines.append(f"- `{record['id']}` ({record['tier']}) — {record.get('title', '')}")
            for span_row in record["covers"]:
                lines.append(f"  - covers {span_row['start']}–{span_row['end']}: {span_row['basis']}")
            for string in record["exact_strings"]:
                words = string.get("text") or string.get("pointer", "")
                lines.append(f"  - says: {words!r} ({string.get('locator', '')})")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("build", help="write data/time-index.json")

    query_parser = commands.add_parser("query", help="answer a timespan as JSON or Markdown")
    query_parser.add_argument("span", help="YYYY[-MM[-DD[THH:MM[:SS]]]] or A..B / A/B")
    query_parser.add_argument("--md", action="store_true", help="Markdown instead of JSON")
    query_parser.add_argument("--rows", type=int, default=0, metavar="N",
                              help="include up to N corpus rows (revision bodies included)")
    query_parser.add_argument("--body-bytes", type=int, default=4000,
                              help="cap on revision body text per row")

    report_parser = commands.add_parser("report", help="print the Markdown report")
    report_parser.add_argument("--out", metavar="PATH", help="write instead of printing")

    check_parser = commands.add_parser("check", help="validate inputs and fixtures")
    check_parser.add_argument("--built", action="store_true",
                              help="also require data/time-index.json to be fresh")

    commands.add_parser("days", help="list days that carry anything, as JSON")

    args = parser.parse_args(argv)
    if args.command == "build":
        index = build()
        INDEX_JSON.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
        problems = index.get("problems", [])
        print(f"Wrote {INDEX_JSON.relative_to(ROOT)}: {len(index['events'])} events, "
              f"{len(index['depictions'])} depictions, {len(index['sources'])} sources, "
              f"{len(index['corpus_days'])} corpus days"
              + (f"; {len(problems)} problem(s)" if problems else ""))
        for problem in problems:
            print(f"  warning: {problem}")
        return 0
    if args.command == "query":
        index = build()
        try:
            result = query(index, args.span, rows=args.rows, body_bytes=args.body_bytes)
        except ValueError as error:
            print(f"timeindex: {error}", file=sys.stderr)
            return 2
        if args.md:
            print(render_query_markdown(result))
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "report":
        text = report(build())
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(f"Wrote {args.out}")
        else:
            print(text)
        return 0
    if args.command == "days":
        index = build()
        days = sorted(
            set(index["corpus_days"])
            | {event["start"][:10] for event in index["events"]}
            | {event["start"][:10] for event in index["depictions"] if event["start"]})
        print(json.dumps(days, indent=2))
        return 0
    if args.command == "check":
        problems = check(args.built)
        for problem in problems:
            print(problem)
        print(f"timeindex: {len(problems)} problem(s)" if problems else "timeindex: ok")
        return 1 if problems else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
