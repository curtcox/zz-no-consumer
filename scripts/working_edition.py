#!/usr/bin/env python3
"""Isolated graphic editions. Identity allocation is invoked by pagination.py.

Authored input is a page-independent event ledger and a window matrix. This module
does not parse a second Markdown dialect: panels and crossref own script parsing.
No command changes the published edition, its dependents, or artwork selections.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import crossref
import panels

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "editions/three-stream"
ROWS = {"incident": ["HuggingFace", "GemStuffer", "Collusion Wiki"],
        "collaboration": ["Curt", "Codex", "Claude"]}


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def git(*args):
    return subprocess.check_output(["git", "--no-optional-locks", "-c", "diff.autoRefreshIndex=false", *args], cwd=ROOT)


def bound(value, upper=False):
    """Inclusive UTC bounds. A date is a day, never an invented midnight event."""
    if len(value) == 10:
        result = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
        return result + timedelta(days=1, microseconds=-1) if upper else result
    if not value.endswith("Z"):
        raise ValueError(f"UTC Z required: {value}")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if upper and len(value) == 17:
        result += timedelta(minutes=1, microseconds=-1)
    return result


def snapshot(edition):
    """Capture once, refusing dirty published inputs. Archive uses Git objects only."""
    target = edition / "baseline.json"
    if target.exists():
        raise ValueError("baseline already exists; it is immutable")
    commit = git("rev-parse", "HEAD").decode().strip()
    tracked = git("ls-tree", "-r", "--name-only", commit).decode().splitlines()
    protected = [p for p in tracked if not p.startswith(("scripts/", "tasks/", ".github/", "editions/"))]
    dirty = git("diff", "--name-only", commit, "--", *protected).decode().strip()
    if dirty:
        raise ValueError("published inputs must be clean before snapshot: " + dirty)
    archive = ROOT / "256t/editions" / (commit + ".tar")
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        subprocess.run(["git", "--no-optional-locks", "archive", "--format=tar",
                        "--output=" + str(archive), commit], cwd=ROOT, check=True)
    record = {"edition": "legacy-" + commit[:12], "commit": commit,
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": digest(archive),
              "frozen_files": {p: digest(ROOT / p) for p in protected}}
    edition.mkdir(parents=True, exist_ok=True)
    target.write_text(dump(record))
    inventory = []
    for path in sorted((ROOT / "content/pages").glob("*.md")):
        source = path.read_text()
        script = panels.split_page(int(path.stem), source)
        exact, errors = crossref.read_exact_strings(crossref.front_matter(source))
        if errors:
            raise ValueError(str(errors))
        chunks = {s.index: s.body for s in script.sections}
        if script.grouped:
            # Each declared panel has an identity, but shares one composition record.
            chunks = {n: source for n in range(script.grouped[0], script.grouped[1] + 1)}
        for number, body in chunks.items():
            inventory.append({"edition": record["edition"], "panel": f"{path.stem}-{number:02}",
                              "source_path": str(path.relative_to(ROOT)),
                              "source_sha256": digest(path), "grouped": bool(script.grouped),
                              "body": body, "exact_strings": exact})
    (edition / "old-panels.json").write_text(dump(inventory))
    print(f"Frozen {len(inventory)} panels at {commit}; archive {record['archive']}")


def load(edition):
    return {name: json.loads((edition / (name + ".json")).read_text())
            for name in ("baseline", "old-panels", "ledger", "windows", "sources", "dispositions", "readiness")}


def validate(model, draft=False):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
    ledger, windows = model["ledger"], model["windows"]
    ids = [e["id"] for e in ledger]
    require(len(ids) == len(set(ids)), "duplicate event identifier")
    events = {e["id"]: e for e in ledger}
    require(len({w["id"] for w in windows}) == len(windows), "duplicate window identifier")
    seen, movements, chapters = [], [], []
    previous = None
    row_times = {}
    for w in windows:
        if not chapters or chapters[-1] != w["chapter"]:
            require(w["chapter"] not in chapters, w["id"] + ": chapter is not consecutive")
            chapters.append(w["chapter"])
        movement = w["movement"]
        require(movement in ROWS, w["id"] + ": unknown movement")
        if movement not in ROWS:
            continue
        if not movements or movements[-1] != movement:
            movements.append(movement)
        require([r["owner"] for r in w["rows"]] == ROWS[movement], w["id"] + ": row order")
        start, end = bound(w["start"]), bound(w["end"], True)
        require(start <= end, w["id"] + ": reversed interval")
        if previous:
            pstart, pend, pmovement = previous
            equal = start == pstart and end == pend and bool(w.get("unordered_with_previous"))
            require(start >= pend or equal, w["id"] + ": overlapping windows without explicit unresolved ordering")
            if pmovement != movement:
                require(start == pend, "movements must share an exact boundary")
        previous = start, end, movement
        for row in w["rows"]:
            slots = row["slots"]
            require(1 <= len(slots) <= 3, w["id"] + ": each row needs one to three slots")
            for event_id in slots:
                if event_id is None:
                    continue
                seen.append(event_id)
                if event_id not in events:
                    errors.append("missing event: " + event_id)
                    continue
                event = events[event_id]
                require(event["movement"] == movement and event["owner"] == row["owner"], event_id + ": wrong row")
                a, b = bound(event["start"]), bound(event["end"], True)
                require(start <= a <= b <= end, event_id + ": outside page clock")
                key = (movement, row["owner"])
                if key in row_times:
                    pa, pb = row_times[key]
                    require(a >= pb or (a >= pa and event.get("order_uncertain") and w.get("evidence_questions")), event_id + ": row order")
                row_times[key] = (a, b)
        require(any(s for r in w["rows"] for s in r["slots"]), w["id"] + ": entirely empty page")
    require(movements == ["incident", "collaboration"] or (draft and movements == ["incident"]),
            "exactly one incident-to-collaboration transition required")
    if not draft:
        require(model["readiness"].get("kind") != "withdrawn-chronology-study",
                "withdrawn chronology study cannot become the manuscript")
        require(not model["readiness"]["pending"], "edition incomplete: " + "; ".join(model["readiness"]["pending"]))
        require(not any("Unresolved overlap:" in w.get("evidence_questions", "") for w in windows),
                "unresolved chronological allocation requires editorial decision")
    require(Counter(seen) == Counter(ids), "every ledger event must appear exactly once")
    old = {p["panel"] for p in model["old-panels"]}
    decisions = model["dispositions"]
    require(set(decisions) == old, "old-panel disposition coverage differs from frozen inventory")
    for key, decision in decisions.items():
        require(bool(decision.get("reason")), key + ": missing disposition reason")
        allowed = {"retain", "split", "combine", "rewrite", "omit"} | ({"defer"} if draft else set())
        require(decision.get("disposition") in allowed, key + ": invalid or unfinished disposition")
        require(all(e in events for e in decision["events"]), key + ": unknown successor")
        require(bool(decision["events"]) != (decision["disposition"] in {"omit", "defer"}), key + ": omitted/successor mismatch")
    reverse = {key: set() for key in old}
    for event in ledger:
        key = event["id"]
        for field in ("subject", "precision", "uncertainty", "original_timezone", "purpose", "frame", "caption", "evidence_status"):
            require(bool(event.get(field)), key + ": missing " + field)
        require(event["precision"] in {"day", "minute", "second", "range"}, key + ": precision vocabulary")
        require(len(panels.WORD.findall(event["caption"])) <= panels.MAX_PANEL_WORDS, key + ": lettering overflow")
        require(bool(event["sources"]), key + ": no source")
        for ref in event["sources"]:
            require(ref["key"] in model["sources"], key + ": unregistered source")
            require(bool(ref.get("locator")), key + ": missing locator")
            if event["movement"] == "collaboration":
                require(bound(ref["available"], True) <= bound(event["end"], True), key + ": later knowledge acted upon early")
        if event["movement"] == "collaboration":
            require(event["evidence_status"] in {"reconstructed", "production-record"}, key + ": actor evidence status")
            if event["evidence_status"] == "reconstructed":
                require("reconstruct" in event["caption"].lower(), key + ": invisible reconstruction")
        for predecessor in event["old_panels"]:
            require(predecessor in old, key + ": unknown old identity")
            if predecessor in reverse:
                reverse[predecessor].add(key)
    for key, successors in reverse.items():
        require(successors == set(decisions[key]["events"]), key + ": mapping is not reciprocal")
    for old_panel in model["old-panels"]:
        successors = decisions[old_panel["panel"]]["events"]
        if successors:
            for registration in old_panel["exact_strings"]:
                require(any(registration in events[e].get("exact_strings", []) for e in successors if e in events),
                        old_panel["panel"] + ": source quotation registration lost in migration")
    return errors


def script(number, window, events):
    used = [events[s] for r in window["rows"] for s in r["slots"] if s]
    registrations = [x for event in used for x in event.get("exact_strings", [])]
    exact = "exact_strings: []\n" if not registrations else "exact_strings:\n" + "".join(
        "  - " + "\n    ".join(k + ": " + json.dumps(v, ensure_ascii=False) for k, v in x.items()) + "\n" for x in registrations)
    source = (f"---\npage: {number}\nedition: three-stream\nstatus: draft\n"
              f"title: {window['title']}\nchapter: {window['chapter']}\n"
              f"movement: {window['movement']}\nclock_start: {window['start']}\nclock_end: {window['end']}\n"
              + exact + "---\n\n" + f"# Page {number:03}\n\n## Page purpose\n\n{window['purpose']}\n\n")
    index = 0
    for row in window["rows"]:
        for position, event_id in enumerate(row["slots"], 1):
            if event_id is None:
                continue
            index += 1
            event = events[event_id]
            source += (f"## Panel {index}\n\n**Row:** {row['owner']}; position {position}\n\n"
                       f"**Event:** {event_id}\n\n**Time:** {event['start']} / {event['end']} UTC; {event['precision']}\n\n"
                       f"**Frame:** {event['frame']}\n\n**Action:** {event['purpose']}\n\n"
                       f"**Caption:**\n> {event['caption']}\n\n"
                       f"**Provenance:** `{event['evidence_status']}` — {event['uncertainty']}\n\n**References:**\n")
            for ref in event["sources"]:
                source += f"- `{ref['key']}` `{ref['locator']}` — 0.90 — available {ref['available']}.\n"
            source += "\n"
    source += "## Page notes\n\nEmpty slots are intentional, with no art or lettering. See manifest.json for geometry.\n"
    return source


def render_page(number, window, events, sources):
    esc = html.escape
    rows = []
    for row in window["rows"]:
        cells = []
        for key in row["slots"]:
            if key is None:
                cells.append('<div class="blank" aria-label="Intentional blank"></div>')
                continue
            e = events[key]
            refs = ""
            for r in e["sources"]:
                url = sources[r["key"]].get("url", "")
                label = f'<a href="{esc(url, quote=True)}">{esc(r["key"])}</a>' if url.startswith("https://") else esc(r["key"])
                refs += f"<li>{label}: {esc(r['locator'])}; available {esc(r['available'])}</li>"
            cells.append(f'<section class="panel"><small>{esc(e["start"])} · {esc(e["precision"])}</small>'
                         f'<p class="direction">{esc(e["frame"])}</p><p class="caption">{esc(e["caption"])}</p>'
                         f'<details><summary>Evidence · {esc(key)}</summary><p>{esc(e["uncertainty"])}</p><ul>{refs}</ul></details></section>')
        rows.append(f'<div class="row"><b class="owner">{esc(row["owner"])}</b><div class="cells" style="--slots:{len(cells)}">{"".join(cells)}</div></div>')
    note = " · Unresolved overlap — allocation under review" if "Unresolved overlap:" in window.get("evidence_questions", "") else ""
    return (f'<article class="page" id="p{number:03}"><header><time>{esc(window["start"])} UTC</time>'
            f'<span>{number:03} · {esc(window["title"])}</span></header>' + "".join(rows) +
            f'<footer><span>{esc(window["movement"])}{note}</span><time>{esc(window["end"])} UTC</time></footer></article>')


CSS = """
*{box-sizing:border-box}body{background:#dedbd3;color:#161616;font:16px Georgia,serif;margin:0}main{max-width:1200px;margin:auto}
.intro{padding:2rem;max-width:850px;margin:auto}.page{background:#fffdf7;padding:22px;margin:28px auto;width:100%;break-after:page}
header,footer{display:flex;justify-content:space-between;gap:16px;font:14px monospace;padding:12px 0}header time,footer time{font-weight:bold;white-space:nowrap}
.row{display:grid;grid-template-columns:100px 1fr;height:290px;margin:12px 0;gap:12px}.owner{font:700 15px sans-serif;align-self:center}
.cells{display:grid;grid-template-columns:repeat(var(--slots),minmax(0,1fr));gap:12px}.panel,.blank{border:1.5px solid #333;overflow:auto;padding:12px}
.blank{border-color:#aaa}.panel p{margin:8px 0;line-height:1.28}.direction{font:italic 14px/1.3 Georgia,serif;color:#555}.caption{font-size:17px}
small,details{font:12px/1.35 sans-serif}details{margin-top:10px}footer time{margin-left:auto}a{color:#244f6c}
@media(max-width:700px){main{min-width:650px}.page{padding:12px}.row{grid-template-columns:75px 1fr;height:350px}.caption{font-size:15px}}
@media print{@page{size:A3 portrait;margin:12mm}body{background:white}.intro{break-after:page}.page{margin:0;padding:0}.row{height:105mm}details{display:none}.caption{font-size:14pt}.direction{font-size:11pt}header,footer{font-size:11pt}}
"""


def outputs(model):
    events = {e["id"]: e for e in model["ledger"]}
    manifest, destinations, files = [], {}, {}
    chapter_map = {}
    for number, w in enumerate(model["windows"], 1):
        if number > 999:
            raise ValueError("three-digit page identity exhausted")
        content = script(number, w, events)
        if model["readiness"].get("kind") == "withdrawn-chronology-study":
            content = content.replace("edition: three-stream\n", "edition: three-stream-chronology-study\n")
            content = content.replace("## Page purpose", "Withdrawn chronology study — not a manuscript page.\n\n## Page purpose", 1)
        parsed = panels.split_page(number, content)
        if parsed.words > panels.MAX_PAGE_WORDS:
            raise ValueError(f"page {number}: lettering exceeds page budget")
        errors, _ = crossref.audit_exact_strings(crossref.front_matter(content), str(number), locked=False)
        if errors:
            raise ValueError(str(errors))
        files[f"content/pages/{number:03}.md"] = content
        index, slots = 0, []
        for rowno, row in enumerate(w["rows"]):
            for col, key in enumerate(row["slots"]):
                index += bool(key)
                slot = {"row": rowno, "column": col, "owner": row["owner"], "event": key,
                        "empty": key is None, "panel": f"{number:03}-{index:02}" if key else None,
                        "rect": [col / len(row["slots"]), rowno / 3, 1 / len(row["slots"]), 1 / 3],
                        "art": None, "art_status": "unassigned" if key else "not-applicable"}
                slots.append(slot)
                if key:
                    destinations[key] = slot["panel"]
        manifest.append({"page": f"{number:03}", "window": w["id"], "chapter": w["chapter"],
                         "movement": w["movement"], "start": w["start"], "end": w["end"], "slots": slots})
        chapter_map.setdefault(w["chapter"], []).append(number)
    mappings = []
    for old in model["old-panels"]:
        d = model["dispositions"][old["panel"]]
        mappings.append({"old_edition": old["edition"], "old_panel": old["panel"], **d,
                         "new_edition": "three-stream-chronology-study" if model["readiness"].get("kind") == "withdrawn-chronology-study" else "three-stream",
                         "new_panels": [destinations[e] for e in d["events"]],
                         "source_registrations": old["exact_strings"],
                         "artwork": "preserved in old edition; no reuse approved"})
    files["manifest.json"] = dump(manifest)
    files["mapping.json"] = dump(mappings)
    files["chapters.json"] = dump({k: {"first_page": min(v), "last_page": max(v)} for k, v in chapter_map.items()})
    files["data/pages.yaml"] = "book:\n  format: graphic-novel-script\n  story_pages: " + str(len(manifest)) + "\npages:\n" + "".join(
        "  - " + json.dumps({"id": p["page"], "chapter": p["chapter"], "status": "draft"}) + "\n" for p in manifest)
    files["preview/index.html"] = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Three streams — working graphic script</title><style>' + CSS + '</style><main><div class="intro">'
        '<h1>Three streams — chronology study</h1><p><strong>Withdrawn as a manuscript candidate.</strong> '
        'These summary panels are a chronology sketch, not the requested full-detail graphic novel. '
        'Their page count is not a target, estimate or capacity plan. Rewriting now begins from the detailed source-panel inventory.</p>'
        '<p><strong>Incomplete working cut.</strong> ' + html.escape("; ".join(model["readiness"]["pending"])) + '</p>'
        '<p>Read pages forward in UTC. Read each row left to right. Rows share a page interval, not necessarily an instant. '
        'A blank means no selected event from the available record, not proof of inactivity. Equal intervals explicitly retain unresolved order.</p>'
        '<p>The planned second movement changes subjects once to Curt, Codex and Claude. Positions imply no identity between subjects. '
        'Its entrance and activity require source research; it is not present in this cut. Source publication is distinct from encounter time.</p>'
        '<p>This preview is separate from the frozen edition. The novella, appendix, downloads and artwork remain attached to their old identities.</p></div>' +
        "".join(render_page(n, w, events, model["sources"]) for n, w in enumerate(model["windows"], 1)) + '</main></html>\n')
    return files


def frozen_errors(model):
    return ["frozen file changed: " + name for name, sha in model["baseline"]["frozen_files"].items()
            if not (ROOT / name).is_file() or digest(ROOT / name) != sha]


def migrate(edition, apply=False, draft=False):
    model = load(edition)
    errors = validate(model, draft) + frozen_errors(model)
    if (edition / "detail-inventory.json").exists():
        import edition_detail
        errors += edition_detail.errors(edition)
    if errors:
        raise ValueError("\n".join(errors))
    generated = outputs(model)
    for item in json.loads(generated["mapping.json"]):
        print(f"{item['old_edition']}:{item['old_panel']} -> " +
              (", ".join(e + "=" + p for e, p in zip(item["events"], item["new_panels"])) or item["disposition"].upper()) + " · " + item["reason"])
    print(f"{len(model['windows'])} pages; {len(model['ledger'])} beats; {len(generated)} generated files")
    if not apply:
        print("Dry run; nothing written. Pass --apply after reviewing this mapping.")
        return
    target = edition / "generated"
    if target.exists() and not (target / ".working-edition").exists():
        raise ValueError("refusing to replace unowned output")
    # Validate and render everything before replacing the disposable generated tree.
    staging = Path(tempfile.mkdtemp(prefix=".edition-", dir=edition))
    try:
        for name, content in generated.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        (staging / ".working-edition").write_text("generated by pagination.py edition\n")
        if target.exists():
            shutil.rmtree(target)
        staging.rename(target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def check(edition, draft=False, *, fixtures=True):
    if fixtures:
        import working_edition_checks
        working_edition_checks.run()
    model = load(edition)
    errors = validate(model, draft) + frozen_errors(model)
    if (edition / "detail-inventory.json").exists():
        import edition_detail
        errors += edition_detail.errors(edition)
    if not errors:
        expected = outputs(model)
        for name, content in expected.items():
            path = edition / "generated" / name
            if not path.is_file() or path.read_text() != content:
                errors.append("stale generated file: " + name)
        actual = {str(p.relative_to(edition / "generated")) for p in (edition / "generated").rglob("*") if p.is_file()}
        if actual != set(expected) | {".working-edition"}:
            errors.append("unexpected/missing generated output")
    if errors:
        raise ValueError("\n".join(errors))
    print(f"Working {'draft ' if draft else ''}edition check passed: {len(model['windows'])} pages, {len(model['ledger'])} beats, "
          f"{len(model['old-panels'])} old panels inventoried; frozen edition unchanged.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("snapshot", "inventory", "check"))
    parser.add_argument("--edition", type=Path, default=DEFAULT)
    parser.add_argument("--draft", action="store_true", help="validate incomplete cut without claiming completion")
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            snapshot(args.edition)
        elif args.command == "inventory":
            import edition_detail
            edition_detail.write(args.edition)
        else:
            check(args.edition, args.draft)
    except (ValueError, KeyError, OSError) as error:
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
