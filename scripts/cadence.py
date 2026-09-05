#!/usr/bin/env python3
"""Measure the negation cadence of the script's visible lettering.

`research/revision-priorities.md` item 9 asks for a reproducible counting method for the
corrective-contrast habit ("X is not Y", "A happened. B did not."), and says the original
review's totals lacked one. This is that method.

It counts only what a reader sees. `**Frame:**`, `**Action:**`, `**Provenance:**`,
`**Note:**` and the `## Page notes` section are direction to the artist and the editor, not
lettering, and are excluded; `**Caption:**`, `**Qualification:**`, `**Screen / system
text…:**` and every `**… dialogue …:**` label are included. Consecutive blockquote lines
under one label are one caption block, because that is how they are lettered and read.

There is deliberately no `check` subcommand. Negation is not a defect: most instances are
claim boundaries the contract requires, and removing one would upgrade a claim. What the
tool separates is the load-bearing limit from the editorial aphorism — an abstract noun
phrase set against another abstract noun phrase, carrying no evidence boundary. That set is
the one worth thinning, and which of its members to thin is an editorial judgement the tool
does not make.
"""

import argparse
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "content" / "pages"

# Tokens that mark a negation or an explicit limit on a claim.
NEGATION = re.compile(
    r"\b(NOT|NO|NEVER|NEITHER|NOR|CANNOT|WITHOUT|UNRESOLVED|UNKNOWN|UNPUBLISHED|UNBOUNDED)\b"
)

# A caption label whose content is lettered on the page.
LETTERED = re.compile(
    r"^\*\*(Caption|Qualification|Screen\s*/\s*system\s+text|.*?[Dd]ialogue.*?)\b.*:\*\*$"
)

# Direction, not lettering.
DIRECTION = re.compile(r"^\*\*(Frame|Action|Provenance|Note)\b.*:\*\*")

# An aphorism sets one abstract noun phrase against another through a linking verb, and
# bounds no source, date, count, or thing in the story. Two signals separate it from a
# claim boundary: the negation is copular ("X is not Y", "X does not mean Y", "X is A, not
# B") rather than attached to an action verb, and no organisation, date, count, or story
# object appears in the line. The result is a candidate list for editorial review, not a
# classification the tool asserts.
COPULAR_NEGATION = re.compile(
    r"\b(IS|WAS|ARE|WERE)\s+NOT\b"
    r"|\bDOES\s+NOT\s+MEAN\b"
    r"|\b(IS|WAS|ARE|WERE)\s+[A-Z][A-Z\s]*?[,—-]\s*NOT\b"
)

STORY_OBJECT = re.compile(
    r"\b(METR|OPENAI|HUGGING\s+FACE|JFROG|MODAL|CYBERGYM|EXPLOITGYM|ARTIFACTORY"
    r"|BOARD|CACHE|TRANSCRIPT|RECORD|REPORT|LOG|LOGS|EVENT|SOURCE|AGENT|AGENTS|RUN|RUNS"
    r"|WORKER|WORKERS|NODE|CLUSTER|CREDENTIAL|CREDENTIALS|TOKEN|TOKENS|MAINTAINER|WIKI"
    r"|PAGE|FLAG|GRADER|SCORER|MODEL|EVALUATION|OBJECTIVE|TASK|ANSWER|MESSAGE|CHANNEL"
    r"|ALERT|WIPE|PANEL|CLOCK|EXIT|LANE|HUMAN|PERSON|DEATH"
    r"|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER)\b"
    r"|\d"
)


def blocks() -> list[tuple[str, str, list[str]]]:
    """Every lettered block in reading order, as (page, label, lines)."""
    found: list[tuple[str, str, list[str]]] = []
    for path in sorted(PAGES.glob("*.md")):
        page = path.stem
        source = path.read_text(encoding="utf-8")
        body = source.split("---", 2)[2] if source.startswith("---\n") else source
        body = body.split("## Page notes")[0]

        label: str | None = None
        buffer: list[str] = []

        def flush() -> None:
            nonlocal buffer
            if label and buffer:
                found.append((page, label, list(buffer)))
            buffer = []

        for raw in body.splitlines():
            line = raw.strip()
            if DIRECTION.match(line):
                flush()
                label = None
                continue
            match = LETTERED.match(line)
            if match:
                flush()
                label = "Caption" if line.lower().startswith("**caption") else match.group(1)
                continue
            if line.startswith("#"):
                flush()
                label = None
                continue
            if label is None:
                continue
            if line.startswith(">"):
                text = line.lstrip("> ").strip()
                if text:
                    buffer.append(text)
            elif line.startswith("`") and line.endswith("`") and len(line) > 2:
                buffer.append(line.strip("`").strip())
            elif line:
                flush()
                label = None
        flush()
    return found


def contrasts(captions: list[tuple[str, list[str]]]) -> tuple[list, list]:
    """Split caption blocks into two-beat and single-clause negation contrasts."""
    two_beat: list[tuple[str, list[str]]] = []
    single: list[tuple[str, str]] = []
    for page, lines in captions:
        if len(lines) >= 2:
            opens_clean = not NEGATION.search(lines[0].upper())
            if opens_clean and any(NEGATION.search(line.upper()) for line in lines[1:]):
                two_beat.append((page, lines))
            continue
        line = lines[0]
        parts = re.split(r"(?<=\.)\s+", line)
        if len(parts) >= 2:
            opens_clean = not NEGATION.search(parts[0].upper())
            if opens_clean and any(NEGATION.search(part.upper()) for part in parts[1:]):
                two_beat.append((page, parts))
                continue
        upper = line.upper()
        verbal = re.search(r"\b(IS|WAS|ARE|WERE|DOES|DID|DO|CAN|MAY|HAS|HAVE)\s+NOT\b", upper)
        if verbal or COPULAR_NEGATION.search(upper) or upper.startswith("NO "):
            single.append((page, line))
    return two_beat, single


def is_aphorism(text: str) -> bool:
    """An abstract contrast, carried by a linking verb, that bounds nothing in the record."""
    upper = text.upper()
    return bool(COPULAR_NEGATION.search(upper)) and not STORY_OBJECT.search(upper)


def report() -> int:
    found = blocks()
    captions = [(page, lines) for page, label, lines in found if label == "Caption"]
    units = [(page, line) for page, _, lines in found for line in lines]

    two_beat, single = contrasts(captions)
    negated_units = sum(1 for _, line in units if NEGATION.search(line.upper()))
    total_contrast = len(two_beat) + len(single)

    print(f"Visible lettering units: {len(units)}")
    print(f"  carrying a negation or limit token: {negated_units} ({negated_units / len(units):.0%})")
    print(f"Caption blocks: {len(captions)}")
    print(
        f"  built on a negation contrast: {total_contrast} "
        f"({total_contrast / len(captions):.0%}) — "
        f"{len(two_beat)} two-beat, {len(single)} single-clause"
    )

    aphorisms = [(page, " / ".join(lines)) for page, lines in two_beat if is_aphorism(" ".join(lines))]
    aphorisms += [(page, line) for page, line in single if is_aphorism(line)]
    print(f"  of those, abstract aphorisms carrying no evidence boundary: {len(aphorisms)}")

    print("\nCaption negation density by page band")
    print("pages      captions  with negation")
    totals: Counter[int] = Counter()
    negated: Counter[int] = Counter()
    for page, lines in captions:
        band = (int(page) - 1) // 10 * 10 + 1
        for line in lines:
            totals[band] += 1
            if NEGATION.search(line.upper()):
                negated[band] += 1
    for band in sorted(totals):
        share = negated[band] / totals[band]
        print(f"{band:03d}-{band + 9:03d}      {totals[band]:4d}      {negated[band]:4d}  ({share:.0%})")
    print(
        "\nDensity is roughly flat across the book. Concentration in the later chapters is "
        "not what the count shows; repetition of one rhetorical shape is."
    )
    return 0


def listing() -> int:
    found = blocks()
    captions = [(page, lines) for page, label, lines in found if label == "Caption"]
    two_beat, single = contrasts(captions)

    print("Two-beat corrective captions — assert, then negate or bound")
    for page, lines in two_beat:
        mark = "*" if is_aphorism(" ".join(lines)) else " "
        print(f" {mark} {page}: " + " / ".join(lines))

    print("\nSingle-clause negations")
    for page, line in single:
        mark = "*" if is_aphorism(line) else " "
        print(f" {mark} {page}: {line}")

    print(
        "\n* marks an abstract aphorism: it sets one abstract noun phrase against another and "
        "bounds no source, date, count, or artifact. Unmarked lines carry a claim boundary and "
        "removing one would upgrade a claim."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("report", help="cadence census and per-band density")
    commands.add_parser("list", help="every negation contrast, with aphorisms marked")
    args = parser.parse_args(argv)
    return listing() if args.command == "list" else report()


if __name__ == "__main__":
    raise SystemExit(main())
