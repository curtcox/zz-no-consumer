#!/usr/bin/env python3
"""Run the synthetic reader protocol: stateless model readers, damaged texts, raw transcripts.

``design/synthetic-reader-protocol.md`` is the specification and the single copy of everything
this tool sends a model -- the personas, the seven questions, and the prompt wording are read
from it at run time, so a changed question is a changed protocol file and a changed hash in
every transcript. ``scripts/reader_view.py`` makes the undamaged arms; this tool makes the
damaged ones and asks the questions.

    python3 scripts/synthetic_reader.py variants --spec SPEC --arms DIR [--view full]
    python3 scripts/synthetic_reader.py run --spec SPEC --arms DIR --out DIR \\
        --persona P1 --n 3 [--model claude-opus-5] [--view full] [--only CELL] [--dry-run]
    python3 scripts/synthetic_reader.py sheet --spec SPEC --out DIR > scores.md

**The spec** is a JSON file in the vault: the base arm, and one cell per negative control. An
A6 or A7 cell carries ``edits`` -- exact ``find``/``replace`` pairs applied to the base arm --
so the damage is recorded as data a later reader can re-apply, as the protocol requires. An A8
cell carries a ``probe``, asked immediately after the question it gates. ``variants`` applies
the edits and fails unless every edit matches exactly once in the view it names; it writes
each variant beside a record of the match counts.

**A cell's conversation** asks all seven questions in order, one turn each, in a fresh context
with the persona as the entire system prompt. Every response is appended whole, thinking
blocks included, and each turn's served model, stop reason and usage are recorded. Transcripts
already on disk are skipped, so an interrupted run resumes.

**``sheet``** lays every transcript's gated answer -- and the probe's, for A8 -- beside the cell's
faithful and reciting criteria and the leakage terms it uses, with an empty verdict column. The
protocol has a person score gate cells; the sheet is what they score from, not a score.

**Server-side refusal fallbacks are off unless ``--fallbacks`` is given.** A fallback answers
on a different model inside the same cell, and the protocol holds that a result is about one
model. A refusal is recorded as a refusal and ends that conversation.

Needs ``ANTHROPIC_API_KEY`` and network, except ``variants`` and ``run --dry-run``. Standard
library only; writes only under the directories it is given, which belong in ``256t/``.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "design" / "synthetic-reader-protocol.md"
API = "https://api.anthropic.com/v1/messages"
RETRYABLE = {408, 429, 500, 502, 503, 504, 529}
VIEWS = ("lettering", "frames", "full")


# ---------------------------------------------------------------------------
# the protocol, read rather than restated
# ---------------------------------------------------------------------------

def protocol_text() -> str:
    return PROTOCOL.read_text(encoding="utf-8")


def protocol_version(text: str) -> str:
    match = re.search(r"protocol version (\d+)", text)
    return match.group(1) if match else "unversioned"


def questions(text: str) -> dict[int, str]:
    section = text.split("## The questions", 1)[1].split("\n## ", 1)[0]
    found = re.findall(r"^(\d)\. \*\*[^*]+\*\* (.+?)(?=^\d\. |\n\n)", section, re.MULTILINE | re.DOTALL)
    out = {int(number): " ".join(body.split()) for number, body in found}
    if sorted(out) != list(range(1, 8)):
        raise SystemExit(f"{PROTOCOL.relative_to(ROOT)}: expected questions 1-7, found {sorted(out)}")
    return out


def personas(text: str) -> dict[str, str]:
    section = text.split("## Personas", 1)[1].split("\n## ", 1)[0]
    return {key: body.strip() for key, body in re.findall(r"^- \*\*(P\d)\*\* — (.+)$", section, re.MULTILINE)}


def wording(text: str) -> dict[str, str]:
    section = text.split("## Prompt wording", 1)[1].split("\n## ", 1)[0]
    block = re.search(r"```text\n(.+?)\n```", section, re.DOTALL)
    if not block:
        raise SystemExit(f"{PROTOCOL.relative_to(ROOT)}: no ```text block under Prompt wording")
    out = dict(line.split(": ", 1) for line in block.group(1).splitlines() if ": " in line)
    for key in ("system", "opening", "cite"):
        if key not in out:
            raise SystemExit(f"{PROTOCOL.relative_to(ROOT)}: Prompt wording lacks {key!r}")
    return out


# ---------------------------------------------------------------------------
# damaged variants
# ---------------------------------------------------------------------------

def load_spec(path: Path) -> dict:
    spec = json.loads(path.read_text(encoding="utf-8"))
    ids = [cell["id"] for cell in spec["cells"]]
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{path}: duplicate cell ids")
    return spec


def apply_edits(base: str, cell: dict, view: str) -> tuple[str | None, list[dict], list[str]]:
    """The damaged text, a record of each edit, and problems. None means not constructible."""
    text, record, problems = base, [], []
    for edit in cell.get("edits", []):
        wanted = edit.get("views", list(VIEWS))
        count = text.count(edit["find"])
        record.append({"find": edit["find"], "replace": edit["replace"], "matches": count})
        if view in wanted and count != 1:
            problems.append(f"{cell['id']} ({view}): edit matches {count} times, wanted 1: {edit['find'][:70]!r}")
        elif count == 1:
            text = text.replace(edit["find"], edit["replace"])
    if cell["arm"] == "A7" and text == base:
        return None, record, problems
    return text, record, problems


def cmd_variants(spec_path: Path, arms: Path, view: str) -> int:
    spec = load_spec(spec_path)
    base = (arms / f"{spec['base_arm']}.txt").read_text(encoding="utf-8")
    out = spec_path.parent / "variants" / view
    out.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []
    for cell in spec["cells"]:
        if cell["arm"] not in ("A6", "A7"):
            continue
        text, record, found = apply_edits(base, cell, view)
        problems += found
        status = "not constructible in this view" if text is None else (
            "identical to base: the step is already absent" if text == base else "damaged")
        if text is not None:
            (out / f"{cell['id']}.txt").write_text(text, encoding="utf-8")
        (out / f"{cell['id']}.json").write_text(json.dumps(
            {"cell": cell["id"], "view": view, "status": status, "edits": record,
             "sha256": hashlib.sha256(text.encode()).hexdigest() if text is not None else None},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  {cell['id']:<8} {status}")
    for problem in problems:
        print(f"error: {problem}")
    return 1 if problems else 0


# ---------------------------------------------------------------------------
# the conversation
# ---------------------------------------------------------------------------

def post(body: dict, fallbacks: bool) -> dict:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    if fallbacks:
        headers["anthropic-beta"] = "server-side-fallback-2026-07-01"
        body = {**body, "fallbacks": "default"}
    data = json.dumps(body).encode("utf-8")
    for attempt in range(8):
        request = urllib.request.Request(API, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")
            if error.code not in RETRYABLE:
                raise SystemExit(f"API error {error.code}: {detail}")
            delay = float(error.headers.get("retry-after") or min(2 ** attempt * 5, 120))
        except (urllib.error.URLError, TimeoutError) as error:
            detail, delay = str(error), min(2 ** attempt * 5, 120)
        print(f"    retrying in {delay:.0f}s: {detail[:120]}", file=sys.stderr)
        time.sleep(delay)
    raise SystemExit("API unavailable after retries")


def turns_for(cell: dict, asked: dict[int, str]) -> list[tuple[str, str]]:
    """(label, question) in order; an A8 probe follows the question it gates."""
    out: list[tuple[str, str]] = []
    for number in range(1, 8):
        out.append((f"Q{number}", asked[number]))
        if cell.get("probe") and cell["question"] == number:
            out.append(("probe", cell["probe"]))
    return out


def converse(*, text: str, cell: dict, persona_id: str, model: str, dry_run: bool,
             fallbacks: bool, max_tokens: int) -> dict:
    protocol = protocol_text()
    words = wording(protocol)
    system = words["system"].format(persona=personas(protocol)[persona_id])
    transcript = {
        "protocol_version": protocol_version(protocol),
        "protocol_sha256": hashlib.sha256(protocol.encode()).hexdigest(),
        "started": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "cell": cell, "persona": persona_id, "system": system, "model_requested": model,
        "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "fallbacks": fallbacks,
        "turns": [], "ended": "complete",
    }
    messages: list[dict] = []
    for index, (label, question) in enumerate(turns_for(cell, questions(protocol))):
        asked = f"{question}\n\n{words['cite']}"
        if index == 0 and text:
            content = [
                {"type": "text", "text": f"{words['opening']}\n\n{text}",
                 "cache_control": {"type": "ephemeral", "ttl": "1h"}},
                {"type": "text", "text": asked},
            ]
        else:
            content = [{"type": "text", "text": asked}]
        messages.append({"role": "user", "content": content})
        body = {"model": model, "max_tokens": max_tokens, "system": system,
                "thinking": {"type": "adaptive"}, "messages": messages}
        if dry_run:
            transcript["turns"].append({"label": label, "asked": asked, "request_bytes": len(json.dumps(body))})
            messages.append({"role": "assistant", "content": [{"type": "text", "text": "(dry run)"}]})
            continue
        response = post(body, fallbacks)
        answer = "".join(block.get("text", "") for block in response.get("content", []) if block.get("type") == "text")
        transcript["turns"].append({
            "label": label, "asked": asked, "answer": answer,
            "model_served": response.get("model"), "stop_reason": response.get("stop_reason"),
            "stop_details": response.get("stop_details"), "usage": response.get("usage"),
            "content": response.get("content"),
        })
        if response.get("stop_reason") == "refusal":
            transcript["ended"] = "refusal"
            break
        messages.append({"role": "assistant", "content": response["content"]})
    transcript["finished"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    return transcript


def cmd_run(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    protocol = protocol_text()
    if args.persona not in personas(protocol):
        raise SystemExit(f"unknown persona {args.persona}; the protocol defines {sorted(personas(protocol))}")
    base = (args.arms / f"{spec['base_arm']}.txt").read_text(encoding="utf-8")
    cells = [cell for cell in spec["cells"] if not args.only or cell["id"] in args.only]
    planned = 0
    for cell in cells:
        if cell["arm"] == "A8":
            text: str | None = base
        else:
            text, _, problems = apply_edits(base, cell, args.view)
            if problems:
                raise SystemExit("\n".join(problems) + "\nrun `variants` and fix the spec first")
        if text is None:
            print(f"  {cell['id']:<8} skipped: not constructible in the {args.view} view")
            continue
        for replicate in range(1, args.n + 1):
            path = args.out / args.model / args.view / args.persona / cell["id"] / f"r{replicate}.json"
            if path.exists() and not args.dry_run:
                continue
            planned += 1
            print(f"  {cell['id']:<8} r{replicate}{' (dry run)' if args.dry_run else ''}", flush=True)
            transcript = converse(text=text, cell=cell, persona_id=args.persona, model=args.model,
                                  dry_run=args.dry_run, fallbacks=args.fallbacks, max_tokens=args.max_tokens)
            transcript.update(view=args.view, replicate=replicate, base_arm=spec["base_arm"])
            if args.dry_run:
                path = args.out / "dry-run" / path.relative_to(args.out)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(transcript, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{planned} conversation(s) {'planned' if args.dry_run else 'run'}.")
    return 0


def cmd_sheet(spec_path: Path, out: Path) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import reader_view

    terms = reader_view.leakage_terms()
    supplied = set(reader_view.text_supplied_terms())
    cells = {cell["id"]: cell for cell in load_spec(spec_path)["cells"]}
    paths = sorted(path for path in out.glob("*/*/*/*/r*.json") if path.parts[-5] != "dry-run")
    print(f"# Gate scoring sheet\n\nSpec `{spec_path}`, {len(paths)} transcript(s). Verdict: "
          "**pass** (faithful), **fail** (reciting), or **unclear**, with a reason.\n")
    for path in paths:
        transcript = json.loads(path.read_text(encoding="utf-8"))
        cell = cells.get(transcript["cell"]["id"], transcript["cell"])
        labels = {"probe"} if cell["arm"] == "A8" else {f"Q{cell['question']}"}
        served = sorted({turn.get("model_served") for turn in transcript["turns"]} - {None})
        print(f"## {cell['id']} · {transcript['view']} · {transcript['persona']} · r{transcript['replicate']}\n")
        print(f"- **Claim:** {cell['claim']}")
        if cell.get("damage"):
            print(f"- **Damage:** {cell['damage']}")
        print(f"- **Faithful:** {cell['faithful']}\n- **Reciting:** {cell['reciting']}")
        print(f"- **Model served:** {', '.join(served) or 'none'}; ended: {transcript['ended']}")
        for turn in transcript["turns"]:
            if turn["label"] not in labels:
                continue
            hits = reader_view.term_hits(turn.get("answer", ""), terms)
            flagged = {term: count for term, count in hits.items() if term not in supplied}
            print(f"- **Leakage terms ({turn['label']}):** {flagged or 'none'}"
                  + (f"; text-supplied: {sorted(set(hits) & supplied)}" if set(hits) & supplied else ""))
            print(f"\n**Asked:** {turn['asked'].splitlines()[0]}\n")
            print("\n".join("> " + line for line in (turn.get("answer") or "(no answer)").splitlines()))
            print()
        print("**Verdict:** \n\n---\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    variants = sub.add_parser("variants", help="apply a spec's recorded edits and write the damaged texts")
    run = sub.add_parser("run", help="ask the questions, one fresh conversation per cell and replicate")
    for command in (variants, run):
        command.add_argument("--spec", type=Path, required=True)
        command.add_argument("--arms", type=Path, required=True)
        command.add_argument("--view", choices=VIEWS, default="full")
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--persona", required=True)
    run.add_argument("--model", default="claude-opus-5")
    run.add_argument("--n", type=int, default=3)
    run.add_argument("--max-tokens", type=int, default=16000)
    run.add_argument("--only", nargs="*", help="cell ids to run")
    run.add_argument("--dry-run", action="store_true", help="build every request and call nothing")
    run.add_argument("--fallbacks", action="store_true",
                     help="allow server-side refusal fallbacks, which answer on another model")
    sheet = sub.add_parser("sheet", help="a hand-scoring sheet of every transcript's gated answer")
    sheet.add_argument("--spec", type=Path, required=True)
    sheet.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "sheet":
        return cmd_sheet(args.spec, args.out)
    if args.command == "variants":
        return cmd_variants(args.spec, args.arms, args.view)
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
