#!/usr/bin/env python3
"""Inventory explicitly supplied Codex/Claude histories without exporting message bodies.

Run on each source Mac. Output is a locator catalog, not evidence of conversation
content or a narrative ledger. Original files stay local. A row-level byte digest
allows a later reviewer to verify a selected message before registering its words.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def inventory(paths, machine, project):
    records = []
    for path in sorted(set(p for root in paths for p in ([root] if root.is_file() else root.rglob("*.jsonl")))):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        lines = raw.splitlines(keepends=True)
        parsed = []
        belongs = False
        for line in lines:
            try:
                item = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                parsed.append(None)
                continue
            parsed.append(item)
            payload = item.get("payload", {})
            cwd = item.get("cwd") or (payload.get("cwd") if isinstance(payload, dict) else None)
            if cwd and Path(cwd).name == project:
                belongs = True
        if not belongs:
            continue
        file_hash = hashlib.sha256(raw).hexdigest()
        offset = 0
        for line_number, (line, item) in enumerate(zip(lines, parsed), 1):
            begin = offset
            offset += len(line)
            if item is None:
                continue
            role, actor, identity = None, None, None
            if item.get("type") in {"user", "assistant"} and isinstance(item.get("message"), dict):
                role = item["type"]
                actor = "Curt" if role == "user" else "Claude"
                identity = item["message"].get("model")
            elif item.get("type") == "response_item":
                payload = item.get("payload", {})
                if payload.get("type") == "message" and payload.get("role") in {"user", "assistant"}:
                    role = payload["role"]
                    actor = "Curt" if role == "user" else "Codex"
            if role is None:
                continue
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                raise ValueError(f"unqualified timestamp: {path}:{line_number}")
            records.append({"id": machine + ":" + path.stem + ":" + str(line_number),
                            "machine": machine, "actor": actor, "role": role,
                            "model": identity, "timestamp_original": timestamp,
                            "utc": dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                            "clock_meaning": "stored message record; delivery/read time not established",
                            "path": str(path), "line": line_number,
                            "bytes": [begin, offset - 1], "record_sha256": hashlib.sha256(line).hexdigest(),
                            "file_sha256": file_hash, "selection": "unreviewed",
                            "caveat": "user role may include injected context or tool results; inspect before assigning Curt"})
    return sorted(records, key=lambda row: (row["utc"], row["id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", type=Path, nargs="+")
    parser.add_argument("--machine", required=True)
    parser.add_argument("--project", default="zz-no-consumer")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = inventory(args.paths, args.machine, args.project)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(result)} candidate message locators; content and actor attribution still require review")


if __name__ == "__main__":
    main()
