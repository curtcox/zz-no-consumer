#!/usr/bin/env python3
"""Attribute committed text to the agent sessions whose tool calls supplied it.

Commit author, committer and trailers do not identify the authoring agent: Curt switches
among agents and the committing agent is often not the one that wrote the change. This
tool compares each line a commit added with text agents passed to tool calls in local
Codex and Claude session transcripts. A candidate must fall inside the window where the
line had to be written: after the previous commit touching the file, and no later than
the commit. The earliest such tool call is the attributed act; the number of competing
sessions is kept so ambiguity stays visible.

A match is evidence that a session typed the words, not that it originated the idea, and
an unmatched line is not evidence of human authorship: text produced by a script, copied
by a tool, written on an uninventoried machine, or shorter than the threshold cannot match.

Output contains locators, hashes, times and counts, never message bodies. Results live in
the ignored vault, beside the transcript inventories they are derived from.

    python3 scripts/production_history.py attribute
    python3 scripts/production_history.py panel 073-02 073-03
    python3 scripts/production_history.py commit cda29ea35
    python3 scripts/production_history.py summary
    python3 scripts/production_history.py verify-bundle 256t/editions/other-mac-bundle-….tar
"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile

import panels

ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "256t/editions"
RESULT = VAULT / "attribution.json"
BASELINE = ROOT / "editions/three-stream/baseline.json"
HOME = Path.home()
DEFAULT_SOURCES = [f"current-mac:{HOME}/.codex/sessions", f"current-mac:{HOME}/.codex/archived_sessions",
                   f"current-mac:{HOME}/.claude/projects"]
BUNDLE_SOURCES = VAULT / "other-mac/sources"
# Authored text lives here; generated trees (docs, derived JSON, artwork) would only add noise.
DEFAULT_PATHS = ["content", "research", "design", "prompts", "tasks", "site", "scripts",
                 "editions/three-stream/manuscript", "editions/three-stream/detail-review.json",
                 "editions/three-stream/sources.json", "editions/three-stream/README.md",
                 "editions/three-stream/research-handoff.md", "data/pages.yaml", "data/chapters.yaml",
                 "data/storyboards.json", "AGENTS.md", "CLAUDE.md", "README.md"]
# Identifiers, hashes and markup fragments are not authored wording; require a short phrase.
MIN_CHARS = 16
MIN_WORDS = 3
READ_ONLY_TOOLS = {"Read", "Glob", "Grep", "WebSearch", "WebFetch", "ToolSearch", "TaskOutput",
                   "AskUserQuestion", "SendUserFile", "view_image", "wait"}
QUOTED = re.compile(r'"((?:[^"\\\n]|\\.){%d,})"|\'((?:[^\'\\\n]|\\.){%d,})\'' % (MIN_CHARS, MIN_CHARS))
ESCAPE = re.compile(r"\\(u[0-9a-fA-F]{4}|.)")
PATH_TOKEN = re.compile(r"[\w.@+-]*(?:/[\w.@+-]+)*\.(?:md|json|jsonl|py|ya?ml|tsv|html|css|js|txt|svg)\b")
PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
SPACE = re.compile(r"\s+")


def utc(stamp: str) -> float:
    dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"unqualified timestamp: {stamp}")
    return dt.timestamp()


def iso(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def norm(line: str) -> str:
    return SPACE.sub(" ", line).strip()


def attributable(value: str) -> bool:
    return len(value) >= MIN_CHARS and value.count(" ") >= MIN_WORDS - 1


def unescape(body: str) -> str:
    def one(match):
        code = match.group(1)
        if code[0] == "u" and len(code) == 5:
            return chr(int(code[1:], 16))
        return {"n": "\n", "t": "\t", "r": ""}.get(code, code)
    return ESCAPE.sub(one, body)


def fragments(text: str, *, patch_only: bool = False) -> set[str]:
    """Candidate authored lines, unwrapping up to three layers of string literals.

    Agents write through heredocs, Python and JavaScript string literals and patches, so a
    line of a JSON file can sit inside a Python literal inside a shell command inside a
    JavaScript call. Patch removal and context lines are not authored text and are dropped.
    """
    found, layer, seen = set(), [text], set()
    for _ in range(4):
        following = []
        for piece in layer:
            if piece in seen:
                continue
            seen.add(piece)
            patch = patch_only or "*** Begin Patch" in piece or piece.startswith("@@ ")
            for line in piece.split("\n"):
                if patch:
                    if not line.startswith("+") or line.startswith("+++"):
                        continue
                    line = line[1:]
                value = norm(line)
                if attributable(value):
                    found.add(value)
            following += [unescape(m.group(1) or m.group(2)) for m in QUOTED.finditer(piece)]
        layer = following
        if not layer:
            break
    return found


def committed_value(path: str, line: str) -> str | None:
    """The authored text of one added line: the longest string value for JSON, else the line."""
    if path.endswith((".json", ".jsonl")):
        values = [unescape(m.group(1)) for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', line)]
        value = norm(max(values, key=len)) if values else ""
    else:
        value = norm(line)
    return value if attributable(value) else None


def relative(path: str, projects: list[str]) -> str | None:
    """Repository-relative form of a path inside a named checkout or one of its Claude worktrees."""
    parts = PurePosixPath(path.removeprefix("file://")).parts
    if not any(name in parts for name in projects):
        return None
    if ".claude" in parts and "worktrees" in parts:
        at = parts.index("worktrees")
        return str(PurePosixPath(*parts[at + 2:])) if len(parts) > at + 2 else None
    for index in range(len(parts) - 1, -1, -1):
        if parts[index] in projects:
            return str(PurePosixPath(*parts[index + 1:])) if len(parts) > index + 1 else None
    return None


def leaves(value, skip=("old_string",)):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in skip:
                yield from leaves(item, skip)
    elif isinstance(value, list):
        for item in value:
            yield from leaves(item, skip)


def transcript_events(path: Path, machine: str, projects: list[str]):
    """Tool-call events of one Codex or Claude transcript, or None if not this project's."""
    raw = path.read_bytes()
    if not any(name.encode() in raw for name in projects):
        return None
    events, belongs, model, session = [], False, None, path.stem
    for number, line in enumerate(raw.splitlines(), 1):
        try:
            item = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(item, dict):
            continue
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        cwd = item.get("cwd") or payload.get("cwd")
        if isinstance(cwd, str) and (PurePosixPath(cwd).name in projects or relative(cwd, projects) is not None):
            belongs = True
        stamp = item.get("timestamp")
        base = dict(machine=machine, transcript=str(path), line=number)
        if item.get("type") == "session_meta":
            session = payload.get("id") or session
        elif item.get("type") == "turn_context":
            model = payload.get("model") or model
        elif item.get("type") == "assistant" and isinstance(item.get("message"), dict) and stamp:
            content = item["message"].get("content")
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("name") in READ_ONLY_TOOLS:
                    continue
                tool_input = block.get("input") or {}
                edit = block.get("name") in {"Edit", "Write", "MultiEdit", "NotebookEdit"}
                targets = [tool_input.get(k) for k in ("file_path", "notebook_path") if isinstance(tool_input.get(k), str)]
                texts = list(leaves(tool_input))
                events.append(dict(base, time=utc(stamp), actor="Claude", model=item["message"].get("model"),
                                   session=item.get("sessionId") or path.stem, subagent=bool(item.get("isSidechain")),
                                   tool=block.get("name"), kind="edit" if edit else "command", targets=targets,
                                   mentions={t for text in texts for t in PATH_TOKEN.findall(text)},
                                   fragments=set().union(*(fragments(s) for s in texts))))
        elif item.get("type") == "response_item" and payload.get("type") in {"custom_tool_call", "function_call"} and stamp:
            if payload.get("name") in READ_ONLY_TOOLS:
                continue
            text = payload.get("input") or payload.get("arguments") or ""
            if not isinstance(text, str):
                continue
            edit = "apply_patch" in text or payload.get("name") == "apply_patch"
            events.append(dict(base, time=utc(stamp), actor="Codex", model=model, session=session, subagent=False,
                               tool=payload.get("name"), kind="edit" if edit else "command",
                               targets=[unescape(t).strip() for t in PATCH_FILE.findall(unescape(text))],
                               mentions=set(PATH_TOKEN.findall(unescape(text))), fragments=fragments(text)))
        elif item.get("type") == "event_msg" and payload.get("type") == "item_completed" and stamp:
            change = payload.get("item")
            if not isinstance(change, dict) or change.get("type") != "FileChange" or change.get("status") != "completed":
                continue
            found = set()
            for target, detail in (change.get("changes") or {}).items():
                if isinstance(detail, dict):
                    if isinstance(detail.get("content"), str):
                        found |= fragments(detail["content"])
                    if isinstance(detail.get("unified_diff"), str):
                        found |= fragments(detail["unified_diff"], patch_only=True)
            events.append(dict(base, time=utc(stamp), actor="Codex", model=model, session=session, subagent=False,
                               tool="FileChange", kind="edit", targets=list(change.get("changes") or {}), mentions=set(),
                               fragments=found))
    return events if belongs else None


def sources(specs: list[str]) -> list[tuple[str, Path]]:
    found = []
    for spec in specs:
        machine, _, location = spec.partition(":")
        root = Path(location).expanduser()
        if not machine or not location:
            raise ValueError(f"source must be MACHINE:PATH, got {spec!r}")
        if root.is_file():
            found.append((machine, root))
        elif root.is_dir():
            found += [(machine, p) for p in sorted(root.rglob("*.jsonl"))]
    return found


def git(*args: str) -> str:
    return subprocess.run(["git", "--no-optional-locks", "-c", "diff.autoRefreshIndex=false", *args],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout


def commit_lines(paths: list[str]):
    """Every added line under ``paths``, with the window in which it had to be written."""
    log = git("log", "--reverse", "--no-merges", "-M", "--unified=0", "--no-color", "--no-ext-diff",
              "--format=%x00%H%x00%cI%x00%aI%x00%an%x00%cn%x00%s", "-p", "--", *paths)
    commits, lines, last_touch = [], [], {}
    current, path, new_line, renamed_from, header = None, None, 0, None, False
    for row in log.split("\n"):
        if row.startswith("\x00"):
            _, sha, committed, authored, author, committer, subject = row.split("\x00", 6)
            current = dict(sha=sha, committed=committed, authored=authored, author=author,
                           committer=committer, subject=subject, time=utc(committed), files={})
            commits.append(current)
            path = renamed_from = None
        elif current is None:
            continue
        elif row.startswith("diff --git "):
            # File headers are only read here: an added line may itself begin with "+++".
            header, path, renamed_from = True, None, None
        elif header and row.startswith("rename from "):
            renamed_from = row[len("rename from "):]
        elif header and row.startswith("+++ "):
            path = None if row == "+++ /dev/null" else row[len("+++ b/"):]
            if path is not None:
                previous = last_touch.get(renamed_from or path, 0.0)
                current["files"][path] = dict(since=previous, added=0, considered=0)
                last_touch[path] = current["time"]
        elif header and not row.startswith("@@ "):
            continue
        elif row.startswith("@@ ") and path:
            header = False
            match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", row)
            new_line = int(match.group(1)) if match else 0
        elif row.startswith("+") and path:
            record = current["files"][path]
            record["added"] += 1
            value = committed_value(path, row[1:])
            if value:
                record["considered"] += 1
                lines.append((value, current["sha"], path, new_line, record["since"], current["time"]))
            new_line += 1
    for commit in commits:
        for path in list(commit["files"]):
            if not commit["files"][path]["added"]:
                del commit["files"][path]
    return commits, lines


def attribute(specs: list[str], paths: list[str], projects: list[str]) -> dict:
    commits, lines = commit_lines(paths)
    wanted = defaultdict(list)
    for index, (value, *_rest) in enumerate(lines):
        wanted[value].append(index)
    best, rivals = {}, defaultdict(set)
    sessions, edits_by_path, mentions_by_path, transcripts = {}, defaultdict(list), defaultdict(list), []
    by_basename = defaultdict(set)
    for commit in commits:
        for name in commit["files"]:
            by_basename[PurePosixPath(name).name].add(name)
    for machine, path in sources(specs):
        events = transcript_events(path, machine, projects)
        if events is None:
            continue
        transcripts.append(dict(machine=machine, path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                events=len(events)))
        for event in events:
            key = f"{event['machine']}:{event['actor']}:{event['session']}"
            info = sessions.setdefault(key, dict(machine=event["machine"], actor=event["actor"], session=event["session"],
                                                 transcripts=set(), models=set(), first=event["time"], last=event["time"],
                                                 subagent_events=0))
            info["transcripts"].add(event["transcript"])
            if event["model"]:
                info["models"].add(event["model"])
            info["first"], info["last"] = min(info["first"], event["time"]), max(info["last"], event["time"])
            info["subagent_events"] += event["subagent"]
            if event["kind"] == "edit":
                for target in event["targets"]:
                    rel = relative(target, projects) if target.startswith("/") else target
                    if rel:
                        edits_by_path[rel].append((event["time"], key))
            for token in event["mentions"]:
                token = (relative(token, projects) or token) if token.startswith("/") else token.removeprefix("./")
                for name in by_basename.get(PurePosixPath(token).name, ()):
                    if name == token or name.endswith("/" + token):
                        mentions_by_path[name].append((event["time"], key))
            for value in event["fragments"]:
                for index in wanted.get(value, ()):
                    _, _, _, _, since, until = lines[index]
                    if not since < event["time"] <= until:
                        continue
                    rivals[index].add(key)
                    # Earliest wins: later appearances are usually searches, moves or replacements of it.
                    rank = (event["time"], event["transcript"], event["line"])
                    if index not in best or rank < best[index][0]:
                        best[index] = (rank, dict(session=key, time=iso(event["time"]), kind=event["kind"],
                                                  tool=event["tool"], transcript=event["transcript"], line=event["line"]))
    for entries in [*edits_by_path.values(), *mentions_by_path.values()]:
        entries.sort()
    by_commit = defaultdict(lambda: defaultdict(Counter))
    attributed = {}
    for index, (value, sha, path, number, _since, _until) in enumerate(lines):
        if index in best:
            choice = dict(best[index][1], rivals=len(rivals[index]))
            attributed[f"{sha}:{path}:{number}"] = choice
            by_commit[sha][path][choice["session"]] += 1
    for commit in commits:
        for path, record in commit["files"].items():
            record["matched"] = dict(by_commit[commit["sha"]][path])
            record["unmatched"] = record["considered"] - sum(record["matched"].values())
            for field, index in (("edit_sessions", edits_by_path), ("mention_sessions", mentions_by_path)):
                entries = index.get(path, [])
                start = bisect_right(entries, (record["since"], "\uffff"))
                end = bisect_right(entries, (commit["time"], "\uffff"))
                record[field] = sorted({key for _, key in entries[start:end]})
            record["since"] = iso(record["since"]) if record["since"] else None
        del commit["time"]
    for info in sessions.values():
        info.update(transcripts=sorted(info["transcripts"]), models=sorted(info["models"]),
                    first=iso(info["first"]), last=iso(info["last"]))
    return dict(generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                head=git("rev-parse", "HEAD").strip(), min_chars=MIN_CHARS, min_words=MIN_WORDS,
                paths=paths, projects=projects,
                claim_limit=("A match shows a session supplied the words in a tool call inside the commit window. "
                             "It does not show origination, review or acceptance. Unmatched is not human authorship."),
                transcripts=transcripts, sessions=sessions, commits=commits, lines=attributed)


def load() -> dict:
    if not RESULT.is_file():
        raise ValueError(f"{RESULT.relative_to(ROOT)} is missing; run `production_history.py attribute` first")
    return json.loads(RESULT.read_text())


def label(result: dict, key: str) -> str:
    info = result["sessions"].get(key, {})
    models = ",".join(info.get("models", [])) or "model unrecorded"
    return f"{info.get('actor', '?')} [{models}] {info.get('machine', '?')} session {info.get('session', key)}"


def report_file(result: dict, sha: str, path: str, record: dict, indent: str = "  "):
    print(f"{indent}{path}: {record['added']} added, {record['considered']} attributable "
          f"(≥{result['min_chars']} chars, ≥{result['min_words']} words), "
          f"{record['unmatched']} unmatched; window {record['since'] or 'file start'} → commit")
    for key, count in sorted(record["matched"].items(), key=lambda kv: -kv[1]):
        print(f"{indent}  {count:5d} lines  {label(result, key)}")
    others = [k for k in record["edit_sessions"] if k not in record["matched"]]
    if others:
        print(f"{indent}  edited this file in the window without a text match: " + "; ".join(label(result, k) for k in others))
    named = [k for k in record["mention_sessions"] if k not in record["matched"] and k not in others]
    if named:
        print(f"{indent}  named this file in a command in the window (weak): " + "; ".join(label(result, k) for k in named))


def find_commit(result: dict, prefix: str) -> dict:
    found = [c for c in result["commits"] if c["sha"].startswith(prefix)]
    if len(found) != 1:
        raise ValueError(f"{prefix}: {'no' if not found else 'ambiguous'} commit in the attribution result "
                         "(only commits touching the scanned paths are indexed)")
    return found[0]


def show_commit(result: dict, prefix: str):
    commit = find_commit(result, prefix)
    print(f"{commit['sha'][:12]} committed {commit['committed']} by {commit['committer']} "
          f"(author {commit['author']}, {commit['authored']}) — {commit['subject']}")
    for path, record in commit["files"].items():
        report_file(result, commit["sha"], path, record)


def panel_lines(page_text: str, number: int, panel: int) -> tuple[int, int]:
    script = panels.split_page(number, page_text)
    if script.grouped and script.grouped[0] <= panel <= script.grouped[1]:
        return 1, page_text.count("\n") + 1
    heads = {int(m.group(1)): m for m in panels.PANEL_HEADING.finditer(page_text)}
    for section in script.sections:
        if section.index == panel and panel in heads:
            first = page_text.count("\n", 0, heads[panel].start()) + 1
            return first, first + section.body.count("\n")
    raise ValueError(f"panel {panel} not found on page {number:03d}")


def blame(commit: str, path: str) -> list[tuple[int, str, str, int, str]]:
    """(final line, origin commit, origin path, origin line, text) at ``commit``."""
    rows, header, meta = [], None, {}
    for row in git("blame", "-M", "-C", "--line-porcelain", commit, "--", path).split("\n"):
        if row.startswith("\t"):
            sha, origin_line, final_line = header
            rows.append((final_line, sha, meta.get("filename", path), origin_line, row[1:]))
            header = None
        elif header is None and re.match(r"^[0-9a-f]{40} \d+ \d+", row):
            parts = row.split()
            header = (parts[0], int(parts[1]), int(parts[2]))
        elif header is not None and " " in row:
            key, _, value = row.partition(" ")
            meta[key] = value
    return rows


_BLAMES: dict = {}   # (commit, path) -> (text, blame rows); panels of one page share a blame


def cached_blame(commit: str, path: str):
    """Text and blame of a file at a commit. A commit never changes, so the vault cache never expires."""
    commit = git("rev-parse", commit).strip()
    if (commit, path) in _BLAMES:
        return _BLAMES[(commit, path)]
    store = VAULT / "blame" / f"{commit}.json"
    if not _BLAMES.get(store):
        _BLAMES[store] = json.loads(store.read_text()) if store.is_file() else {}
    saved = _BLAMES[store]
    if path not in saved:
        saved[path] = [git("show", f"{commit}:{path}"), blame(commit, path)]
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text(json.dumps(saved, ensure_ascii=False))
    _BLAMES[(commit, path)] = saved[path]
    return saved[path]


def panel_origins(result: dict, key: str, baseline: str) -> list[dict]:
    """Where a frozen panel's wording came from: one entry per origin commit and file."""
    match = re.fullmatch(r"(\d{3})-(\d{2})", key)
    if not match:
        raise ValueError(f"{key}: expected a panel key like 073-02")
    number, panel = int(match.group(1)), int(match.group(2))
    path = f"content/pages/{number:03d}.md"
    text, blamed = cached_blame(baseline, path)
    first, last = panel_lines(text, number, panel)
    commits = {c["sha"]: c for c in result["commits"]}
    by_origin = defaultdict(list)
    for final_line, sha, origin_path, origin_line, content in blamed:
        if first <= final_line <= last:
            by_origin[(sha, origin_path)].append((origin_line, content))
    origins = []
    for (sha, origin_path), items in by_origin.items():
        commit = commits.get(sha)
        entry = dict(key=key, path=path, first=first, last=last, sha=sha, origin_path=origin_path, lines=len(items),
                     committed=commit["committed"] if commit else None, subject=commit["subject"] if commit else "",
                     file=commit["files"].get(origin_path, {}) if commit else {},
                     sessions=Counter(), short=0, unmatched=0, ambiguous=0)
        for origin_line, content in items:
            if not committed_value(origin_path, content):
                entry["short"] += 1
                continue
            hit = result["lines"].get(f"{sha}:{origin_path}:{origin_line}")
            if hit:
                entry["sessions"][hit["session"]] += 1
                entry["ambiguous"] += hit["rivals"] > 1
            else:
                entry["unmatched"] += 1
        origins.append(entry)
    return sorted(origins, key=lambda e: e["committed"] or "")


def panel_actors(result: dict, key: str, baseline: str) -> Counter:
    """Matched lines of a frozen panel, by actor."""
    actors = Counter()
    for entry in panel_origins(result, key, baseline):
        for session, count in entry["sessions"].items():
            actors[result["sessions"][session]["actor"]] += count
    return actors


def show_panels(result: dict, keys: list[str], baseline: str):
    for key in keys:
        origins = panel_origins(result, key, baseline)
        if origins:
            print(f"{key} at {baseline[:12]} ({origins[0]['path']} lines {origins[0]['first']}–{origins[0]['last']})")
        for entry in origins:
            print(f"  {entry['sha'][:12]} {entry['committed'] or 'not indexed'} {entry['origin_path']} — "
                  f"{entry['lines']} lines: {entry['subject']}")
            for session, count in entry["sessions"].most_common():
                print(f"      {count:3d} lines  {label(result, session)}")
            if entry["ambiguous"]:
                print(f"      ({entry['ambiguous']} of the matched lines also appear in another session's tool calls in the window)")
            record = entry["file"]
            if entry["unmatched"] or entry["short"]:
                print(f"      {entry['unmatched']:3d} lines  no transcript text match; "
                      f"{entry['short']} too short, blank or identifier-only")
                if record.get("matched"):
                    print("           same commit and file, matched elsewhere: " +
                          "; ".join(f"{label(result, k)} ({n})" for k, n in sorted(record["matched"].items(), key=lambda kv: -kv[1])))
                for field, text in (("edit_sessions", "edited the file in the window"),
                                    ("mention_sessions", "named the file in a command in the window (weak)")):
                    keys_ = [k for k in record.get(field, []) if k not in record.get("matched", {})]
                    if keys_:
                        print(f"           {text}: " + "; ".join(label(result, k) for k in keys_))


def summary(result: dict):
    totals, daily, silent = Counter(), defaultdict(Counter), []
    for key, hit in result["lines"].items():
        actor = result["sessions"][hit["session"]]["actor"]
        totals[actor] += 1
        daily[hit["time"][:10]][actor] += 1
    for commit in result["commits"]:
        considered = sum(f["considered"] for f in commit["files"].values())
        matched = sum(sum(f["matched"].values()) for f in commit["files"].values())
        if considered >= 20 and matched / considered < 0.1:
            silent.append((commit, considered, matched))
    print(f"Attribution from {len(result['transcripts'])} transcripts, {len(result['sessions'])} sessions, "
          f"{len(result['commits'])} commits (head {result['head'][:12]}, generated {result['generated_at']})")
    considered = sum(f["considered"] for c in result["commits"] for f in c["files"].values())
    print(f"Attributable added lines: {considered}; matched: {sum(totals.values())} " + dict(totals).__repr__())
    print("Matched lines by UTC day of the tool call:")
    for day in sorted(daily):
        print(f"  {day}  " + "  ".join(f"{actor} {count}" for actor, count in sorted(daily[day].items())))
    print(f"Commits with ≥20 attributable lines and <10% matched ({len(silent)}): written elsewhere, generated, "
          "moved by a tool, or authored on an uninventoried machine")
    for commit, total, matched in silent:
        print(f"  {commit['sha'][:12]} {commit['committed']} {matched}/{total} — {commit['subject']}")
    print(result["claim_limit"])


def verify_bundle(archive: Path, extract: bool):
    """Check an other-Mac bundle before use; optionally extract it into the vault."""
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"{archive.name}: sha256 {digest}")
    errors = []
    with tarfile.open(archive) as tar:
        members = {m.name: m for m in tar.getmembers()}
        for name, member in members.items():
            if member.issym() or member.islnk() or name.startswith("/") or ".." in PurePosixPath(name).parts:
                errors.append(f"unsafe member: {name}")
            elif not name.startswith("other-mac"):
                errors.append(f"member outside other-mac/: {name}")
        sums = members.get("other-mac/SHA256SUMS")
        if sums is None:
            errors.append("missing other-mac/SHA256SUMS")
        else:
            for row in tar.extractfile(sums).read().decode().splitlines():
                if not row.strip():
                    continue
                expected, _, name = row.partition("  ")
                name = name.strip().removeprefix("./")
                member = members.get(name) or members.get("other-mac/" + name)
                if member is None:
                    errors.append(f"listed but absent: {name}")
                elif hashlib.sha256(tar.extractfile(member).read()).hexdigest() != expected:
                    errors.append(f"hash mismatch: {name}")
        inventories = [n for n in members if re.fullmatch(r"other-mac/messages-[^/]+\.json", n)]
        if not inventories:
            errors.append("no other-mac/messages-*.json inventory")
        stale = 0
        for name in inventories:
            rows = json.loads(tar.extractfile(members[name]).read())
            for path, expected in {r["path"]: r["file_sha256"] for r in rows}.items():
                relative_path = str(Path(path).relative_to(Path(path).anchor))
                home_relative = re.sub(r"^(Users|home)/[^/]+/", "", relative_path)
                member = members.get("other-mac/sources/" + home_relative)
                if member is None:
                    errors.append(f"{name}: transcript not bundled: {path}")
                elif hashlib.sha256(tar.extractfile(member).read()).hexdigest() != expected:
                    stale += 1
        if stale:
            print(f"warning: {stale} bundled transcripts differ from their inventory hash (e.g. a live session); "
                  "rerun the inventory from the bundled copies before selecting records")
        if errors:
            raise ValueError("\n".join(errors))
        print(f"verified {len(members)} members, {len(inventories)} inventories")
        if extract:
            if (VAULT / "other-mac").exists():
                raise ValueError(f"{VAULT / 'other-mac'} already exists; move it aside before extracting")
            tar.extractall(VAULT, filter="data")
            print(f"extracted into {VAULT / 'other-mac'}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("attribute", help="index commits and transcripts; write the vault result")
    run.add_argument("--source", action="append", metavar="MACHINE:PATH",
                     help="transcript file or directory (repeatable); defaults to this Mac's Codex and Claude "
                          "histories plus an extracted other-Mac bundle")
    run.add_argument("--path", action="append", help="repository path to index (repeatable)")
    run.add_argument("--project", action="append", help="checkout directory name (repeatable)")
    show = sub.add_parser("panel", help="who supplied the frozen wording of panels")
    show.add_argument("keys", nargs="+")
    show.add_argument("--at", help="commit to read panels at; defaults to the frozen baseline")
    one = sub.add_parser("commit", help="attribution for one commit")
    one.add_argument("sha")
    sub.add_parser("summary", help="matched lines by actor and day; commits without transcript support")
    bundle = sub.add_parser("verify-bundle", help="verify an other-Mac bundle tar")
    bundle.add_argument("archive", type=Path)
    bundle.add_argument("--extract", action="store_true", help="extract into 256t/editions/ after verification")
    args = parser.parse_args(argv)
    try:
        if args.command == "attribute":
            specs = args.source or DEFAULT_SOURCES + ([f"other-mac:{BUNDLE_SOURCES}"] if BUNDLE_SOURCES.is_dir() else [])
            result = attribute(specs, args.path or DEFAULT_PATHS, args.project or ["zz-no-consumer"])
            VAULT.mkdir(parents=True, exist_ok=True)
            RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
            summary(result)
            print(f"wrote {RESULT.relative_to(ROOT)}")
        elif args.command == "panel":
            baseline = args.at or json.loads(BASELINE.read_text())["commit"]
            show_panels(load(), args.keys, baseline)
        elif args.command == "commit":
            show_commit(load(), args.sha)
        elif args.command == "summary":
            summary(load())
        else:
            verify_bundle(args.archive, args.extract)
    except (ValueError, OSError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(getattr(error, "stderr", None) or error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
