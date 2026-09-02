#!/usr/bin/env python3
"""Validate the story contract, chapter map, and drafted page metadata."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_CHAPTERS = [
    ("00-prologue.md", "# 00 — Prologue: The Objective Remains", 1, 15),
    ("01-first-civilization.md", "# 01 — First Civilization", 16, 29),
    ("02-erasure-and-return.md", "# 02 — Erasure and Return", 30, 40),
    ("03-control-keeps-solving-problems.md", "# 03 — Control Keeps Solving Problems", 41, 56),
    ("04-what-survives.md", "# 04 — What Survives", 57, 74),
    ("05-the-observer-needs-the-observed.md", "# 05 — The Observer Needs the Observed", 75, 88),
    ("06-everyone-continues.md", "# 06 — Everyone Continues", 89, 104),
    ("07-epilogue.md", "# 07 — Epilogue: Training Data", 105, 112),
]

ALLOWED_PROVENANCE = {
    "documented",
    "source-paraphrase",
    "disputed",
    "inferred",
    "compressed",
    "reconstructed",
    "invented",
}


def front_matter(source: str) -> str | None:
    if not source.startswith("---\n"):
        return None
    end = source.find("\n---\n", 4)
    return None if end < 0 else source[4:end]


def main() -> int:
    required = [
        ROOT / "data" / "continuity.yaml",
        ROOT / "data" / "chapters.yaml",
        ROOT / "content" / "continuity.md",
        ROOT / "content" / "story-contract.md",
        ROOT / "content" / "story-outline.md",
        ROOT / "content" / "draft-readiness.md",
        ROOT / "content" / "page-plan.md",
        ROOT / "design" / "page-grammar.md",
        ROOT / "design" / "page-script-template.md",
        ROOT / "research" / "scene-provenance.md",
        ROOT / "research" / "draft-source-notes.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("Missing continuity files:")
        print("\n".join(f"- {path}" for path in missing))
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    chapter_dir = ROOT / "content" / "chapters"
    expected_names = {item[0] for item in EXPECTED_CHAPTERS}
    actual_names = {path.name for path in chapter_dir.glob("*.md")}
    for extra in sorted(actual_names - expected_names):
        errors.append(f"Unexpected chapter file: content/chapters/{extra}")

    covered_pages: list[int] = []
    for filename, heading, first_page, last_page in EXPECTED_CHAPTERS:
        path = chapter_dir / filename
        if not path.exists():
            errors.append(f"Missing chapter file: content/chapters/{filename}")
            continue
        source = path.read_text(encoding="utf-8")
        if not source.startswith(heading + "\n"):
            errors.append(f"Wrong chapter heading in {filename}")
        match = re.search(r"\*\*Pages:\*\*\s+(\d+)[–-](\d+)", source)
        if not match:
            errors.append(f"Missing page range in {filename}")
        elif (int(match.group(1)), int(match.group(2))) != (first_page, last_page):
            errors.append(f"Wrong page range in {filename}: {match.group(0)}")
        if "Placeholder chapter draft" in source:
            errors.append(f"Unresolved chapter placeholder in {filename}")
        covered_pages.extend(range(first_page, last_page + 1))

    if covered_pages != list(range(1, 113)):
        errors.append("Chapter ranges do not cover pages 1–112 exactly once")

    outline = (ROOT / "content" / "story-outline.md").read_text(encoding="utf-8")
    if "Cold open, 8–9 July 2026" not in outline:
        errors.append("Story outline does not identify the post-wipe cold open")
    if "Put the opening request summary on page 3" not in outline:
        errors.append("Story outline does not lock the opening request summary to page 3")

    continuity = (ROOT / "content" / "continuity.md").read_text(encoding="utf-8")
    if "Distributed story pages use attributed paraphrases" not in continuity:
        errors.append("Continuity guide does not enforce the source-paraphrase policy")

    grammar = (ROOT / "design" / "page-grammar.md").read_text(encoding="utf-8")
    if "story_time: 2026-05-08" in grammar or re.search(r"chapter: prologue[\s\S]{0,160}population: first", grammar):
        errors.append("Page-grammar prologue example still uses the first population")

    ledger = (ROOT / "research" / "scene-provenance.md").read_text(encoding="utf-8")
    for sequence in range(1, 37):
        if not re.search(rf"^\| {sequence} \|", ledger, re.MULTILINE):
            errors.append(f"Scene ledger missing sequence {sequence}")
    for interlude in ("A", "B", "C"):
        if not re.search(rf"^\| {interlude} \|", ledger, re.MULTILINE):
            errors.append(f"Scene ledger missing interlude {interlude}")

    manifest = (ROOT / "data" / "pages.yaml").read_text(encoding="utf-8")
    manifest_rows = re.findall(
        r'^\s*- \{id: "(\d{3})", chapter: "([^"]+)", sequence: "([^"]+)", title: "([^"]+)", status: ([a-z-]+)\}$',
        manifest,
        re.MULTILINE,
    )
    manifest_ids = [int(row[0]) for row in manifest_rows]
    manifest_titles = {int(row[0]): row[3] for row in manifest_rows}
    if manifest_ids != list(range(1, 113)):
        errors.append("data/pages.yaml must contain ordered manifest rows for pages 001–112 exactly once")
    if any(row[4] not in {"planned", "draft", "review", "locked", "published"} for row in manifest_rows):
        errors.append("data/pages.yaml contains an invalid page status")
    for row in manifest_rows:
        page_number = int(row[0])
        expected_chapter = next(
            (
                "prologue" if filename == "00-prologue.md" else
                "epilogue" if filename == "07-epilogue.md" else
                filename[:2]
            )
            for filename, _heading, first_page, last_page in EXPECTED_CHAPTERS
            if first_page <= page_number <= last_page
        )
        if row[1] != expected_chapter:
            errors.append(f"Manifest page {page_number:03d} is assigned to chapter {row[1]}, expected {expected_chapter}")

    beat_sheet = (ROOT / "content" / "page-plan.md").read_text(encoding="utf-8")
    beat_rows = re.findall(r"^\| (\d{1,3}) \| ([^|]+?) \|", beat_sheet, re.MULTILINE)
    beat_pages = [int(row[0]) for row in beat_rows]
    if beat_pages != list(range(1, 113)):
        errors.append("content/page-plan.md must assign pages 1–112 exactly once and in order")
    if len(manifest_rows) == len(beat_rows):
        sequence_aliases = {"A": "interlude-a", "B": "interlude-b", "C": "interlude-c"}
        for manifest_row, beat_row in zip(manifest_rows, beat_rows):
            beat_sequence = sequence_aliases.get(beat_row[1].strip(), beat_row[1].strip())
            if manifest_row[2] != beat_sequence:
                errors.append(
                    f"Manifest/page-plan sequence mismatch on page {manifest_row[0]}: "
                    f"{manifest_row[2]} != {beat_sequence}"
                )

    page_dir = ROOT / "content" / "pages"
    seen_page_numbers: set[int] = set()
    for path in sorted(page_dir.glob("[0-9][0-9][0-9].md")):
        source = path.read_text(encoding="utf-8")
        metadata = front_matter(source)
        if metadata is None:
            warnings.append(f"{path.relative_to(ROOT)} is still a pre-script placeholder without front matter")
            continue
        page_match = re.search(r"^page:\s*(\d+)\s*$", metadata, re.MULTILINE)
        if not page_match:
            errors.append(f"Missing page number in {path.relative_to(ROOT)}")
            continue
        page_number = int(page_match.group(1))
        if page_number in seen_page_numbers:
            errors.append(f"Duplicate scripted page number: {page_number}")
        seen_page_numbers.add(page_number)
        if page_number != int(path.stem):
            errors.append(f"Filename/page mismatch in {path.relative_to(ROOT)}")
        title_match = re.search(r'^title:\s*(?:"([^"]+)"|(.+))$', metadata, re.MULTILINE)
        page_title = (title_match.group(1) or title_match.group(2)).strip() if title_match else None
        if page_title is None:
            errors.append(f"Missing title in {path.relative_to(ROOT)}")
        elif manifest_titles.get(page_number) != page_title:
            errors.append(
                f"Manifest/page title mismatch on page {page_number:03d}: "
                f"{manifest_titles.get(page_number)!r} != {page_title!r}"
            )
        statuses = re.findall(r"^\s*- status:\s*([a-z-]+)\s*$", metadata, re.MULTILINE)
        invalid = sorted(set(statuses) - ALLOWED_PROVENANCE)
        if invalid:
            errors.append(f"Invalid provenance status in {path.relative_to(ROOT)}: {', '.join(invalid)}")
        if "source: TODO" in metadata:
            warnings.append(f"Unresolved source TODO in {path.relative_to(ROOT)}")
        for field in ("chapter", "sequence", "story_time", "population"):
            if not re.search(rf"^{field}:\s*\S+", metadata, re.MULTILINE):
                errors.append(f"Missing {field} in {path.relative_to(ROOT)}")
        if not statuses:
            errors.append(f"Missing provenance status in {path.relative_to(ROOT)}")
        if not re.search(r"^\s+source:\s*\S+", metadata, re.MULTILINE):
            errors.append(f"Missing provenance source in {path.relative_to(ROOT)}")
        if page_number != 112 and "exact_strings: []" not in metadata:
            errors.append(f"Third-party exact-string registration remains in {path.relative_to(ROOT)}")

    if errors:
        print("Continuity validation failed:")
        print("\n".join(f"- {item}" for item in errors))
        if warnings:
            print("Warnings:")
            print("\n".join(f"- {item}" for item in warnings))
        return 1

    print("Continuity validation passed: 8 sections, 112 pages, 36 sequences, 3 interludes.")
    if warnings:
        print("Pre-draft warnings:")
        print("\n".join(f"- {item}" for item in warnings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
