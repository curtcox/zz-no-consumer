#!/usr/bin/env python3
"""Maintain private local snapshots for tracked original-source URLs.

The source manifest is tracked; downloaded bodies and metadata live under the
gitignored 256t/ directory. The script uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "256t-sources.tsv"
VAULT = ROOT / "256t"
RECORDS = VAULT / "records"
MAX_BYTES = 128 * 1024 * 1024
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
USER_AGENT = "zz-no-consumer-source-monitor/1.0 (+local editorial archive)"


@dataclass(frozen=True)
class Source:
    id: str
    url: str
    kind: str
    redistribution: str
    note: str


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_sources() -> list[Source]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"id", "url", "kind", "redistribution", "note"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"Invalid manifest columns in {MANIFEST.relative_to(ROOT)}")
    sources: list[Source] = []
    seen: set[str] = set()
    for row in rows:
        source = Source(**{key: row[key].strip() for key in required})
        if not ID_PATTERN.fullmatch(source.id):
            raise SystemExit(f"Unsafe source id: {source.id!r}")
        if source.id in seen:
            raise SystemExit(f"Duplicate source id: {source.id}")
        if not source.url.startswith(("https://", "http://")):
            raise SystemExit(f"Unsupported URL for {source.id}: {source.url}")
        seen.add(source.id)
        sources.append(source)
    return sources


def select_sources(sources: list[Source], ids: list[str]) -> list[Source]:
    if not ids:
        return sources
    by_id = {source.id: source for source in sources}
    missing = [source_id for source_id in ids if source_id not in by_id]
    if missing:
        raise SystemExit(f"Unknown source ids: {', '.join(missing)}")
    return [by_id[source_id] for source_id in ids]


def read_metadata(source: Source) -> dict:
    path = RECORDS / source.id / "metadata.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(source: Source, metadata: dict) -> tuple[bytes | None, dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if metadata.get("etag"):
        headers["If-None-Match"] = metadata["etag"]
    if metadata.get("last_modified"):
        headers["If-Modified-Since"] = metadata["last_modified"]
    request = urllib.request.Request(source.url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise RuntimeError(f"response exceeds {MAX_BYTES} bytes")
            response_meta = {
                "status": response.status,
                "final_url": response.geturl(),
                "content_type": response.headers.get("Content-Type", ""),
                "etag": response.headers.get("ETag", ""),
                "last_modified": response.headers.get("Last-Modified", ""),
            }
            return body, response_meta
    except urllib.error.HTTPError as error:
        if error.code == 304:
            return None, {"status": 304, "final_url": source.url}
        raise


def write_sync(source: Source, body: bytes | None, response_meta: dict, metadata: dict) -> str:
    record = RECORDS / source.id
    record.mkdir(parents=True, exist_ok=True)
    checked_at = now()
    if body is None:
        metadata.setdefault("checks", []).append({"checked_at": checked_at, "status": 304, "sha256": metadata.get("sha256")})
        metadata["checked_at"] = checked_at
        result = "unchanged (304)"
    else:
        digest = hashlib.sha256(body).hexdigest()
        previous = metadata.get("sha256")
        blob = record / "blobs" / f"{digest}.bin"
        blob.parent.mkdir(exist_ok=True)
        if not blob.exists():
            blob.write_bytes(body)
        shutil.copyfile(blob, record / "content.bin")
        metadata.update(
            {
                "id": source.id,
                "url": source.url,
                "kind": source.kind,
                "redistribution": source.redistribution,
                "note": source.note,
                "checked_at": checked_at,
                "sha256": digest,
                **response_meta,
            }
        )
        metadata.setdefault("checks", []).append(
            {"checked_at": checked_at, "status": response_meta.get("status"), "sha256": digest}
        )
        result = "new" if previous is None else ("changed" if previous != digest else "unchanged")
    (record / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def write_failure(source: Source, metadata: dict, error: Exception) -> None:
    record = RECORDS / source.id
    record.mkdir(parents=True, exist_ok=True)
    metadata.update(
        {
            "id": source.id,
            "url": source.url,
            "kind": source.kind,
            "redistribution": source.redistribution,
            "note": source.note,
            "checked_at": now(),
            "last_error": str(error),
        }
    )
    (record / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sync(sources: list[Source]) -> int:
    failures = 0
    for source in sources:
        metadata = read_metadata(source)
        try:
            body, response_meta = fetch(source, metadata)
            print(f"{source.id}: {write_sync(source, body, response_meta, metadata)}")
        except Exception as error:  # keep independent sources progressing
            failures += 1
            write_failure(source, metadata, error)
            print(f"{source.id}: ERROR {error}", file=sys.stderr)
    return 1 if failures else 0


def check(sources: list[Source]) -> int:
    changed = 0
    failures = 0
    for source in sources:
        metadata = read_metadata(source)
        try:
            body, _ = fetch(source, metadata)
            if body is None:
                state = "unchanged (304)"
            else:
                digest = hashlib.sha256(body).hexdigest()
                state = "unchanged" if digest == metadata.get("sha256") else "CHANGED"
                changed += state == "CHANGED"
            print(f"{source.id}: {state}")
        except Exception as error:
            failures += 1
            print(f"{source.id}: ERROR {error}", file=sys.stderr)
    return 2 if changed else (1 if failures else 0)


def status(sources: list[Source]) -> int:
    for source in sources:
        metadata = read_metadata(source)
        if metadata:
            state = metadata.get("sha256", "ERROR" if metadata.get("last_error") else "-")
            print(f"{source.id}\t{metadata.get('checked_at', '-')}\t{state}\t{source.url}")
        else:
            print(f"{source.id}\tMISSING\t-\t{source.url}")
    return 0


def import_body(source: Source, body: bytes, captured_via: str) -> int:
    if not body:
        raise SystemExit("Refusing to import an empty body")
    if len(body) > MAX_BYTES:
        raise SystemExit(f"Imported body exceeds {MAX_BYTES} bytes")
    metadata = read_metadata(source)
    response_meta = {
        "status": "imported",
        "final_url": source.url,
        "content_type": "text/plain; charset=utf-8",
        "etag": "",
        "last_modified": "",
        "captured_via": captured_via,
    }
    print(f"{source.id}: {write_sync(source, body, response_meta, metadata)} ({captured_via})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check", "status", "import"))
    parser.add_argument("--id", action="append", default=[], help="limit work to one manifest id; repeatable")
    parser.add_argument("--file", type=Path, help="body to import for a browser-only source; omit to read stdin")
    parser.add_argument("--captured-via", default="manual-import", help="provenance label for an imported body")
    args = parser.parse_args()
    sources = select_sources(load_sources(), args.id)
    if args.command == "sync":
        return sync(sources)
    if args.command == "check":
        return check(sources)
    if args.command == "import":
        if len(sources) != 1 or len(args.id) != 1:
            raise SystemExit("import requires exactly one --id")
        body = args.file.read_bytes() if args.file else sys.stdin.buffer.read(MAX_BYTES + 1)
        return import_body(sources[0], body, args.captured_via)
    return status(sources)


if __name__ == "__main__":
    raise SystemExit(main())
