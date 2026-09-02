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
    "raw-agent-text",
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
        ROOT / "design" / "page-grammar.md",
        ROOT / "design" / "page-script-template.md",
        ROOT / "research" / "scene-provenance.md",
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
    if "`STRICT_CAUSAL?`" in outline:
        errors.append("Non-canonical exact term remains in story outline: STRICT_CAUSAL?")
    if "Cold open, 8–9 July 2026" not in outline:
        errors.append("Story outline does not identify the post-wipe cold open")

    ledger = (ROOT / "research" / "scene-provenance.md").read_text(encoding="utf-8")
    for sequence in range(1, 37):
        if not re.search(rf"^\| {sequence} \|", ledger, re.MULTILINE):
            errors.append(f"Scene ledger missing sequence {sequence}")
    for interlude in ("A", "B", "C"):
        if not re.search(rf"^\| {interlude} \|", ledger, re.MULTILINE):
            errors.append(f"Scene ledger missing interlude {interlude}")

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
        statuses = re.findall(r"^\s*- status:\s*([a-z-]+)\s*$", metadata, re.MULTILINE)
        invalid = sorted(set(statuses) - ALLOWED_PROVENANCE)
        if invalid:
            errors.append(f"Invalid provenance status in {path.relative_to(ROOT)}: {', '.join(invalid)}")
        if "source: TODO" in metadata:
            warnings.append(f"Unresolved source TODO in {path.relative_to(ROOT)}")

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
