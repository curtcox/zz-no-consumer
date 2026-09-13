#!/usr/bin/env python3
"""Inventory Curt's personal data exports for dated evidence of the entrance, without bodies.

Supported exports, detected by shape:

- Google Takeout YouTube ``watch-history.json`` — watch times.
- X archive ``tweets.js`` / ``tweet.js`` — Curt's own posts, replies and quotes.
- X archive ``like.js`` — likes carry no like time; a liked post's ID yields its creation
  time, which is only the earliest moment the like could have happened.
- ChatGPT export ``conversations.json`` — message times, roles and model slugs.
- claude.ai export ``conversations.json`` — message times and roles.
- Podcast OPML with per-episode ``userUpdatedDate`` (Overcast's "all data" export).

Only rows inside the window that match a term or a listed URL are written, as locators:
the export file and position, UTC time, what that time means, role or product, public URL
where the row is a public post or video, and which terms matched. Titles, message bodies
and post text are never written. Row counts outside the match are reported, not listed.

What someone watched, liked or wrote is not what they noticed or understood; an export
shows actions the service recorded, and each row says which action.

    python3 scripts/personal_records.py inventory ~/Downloads/Takeout/…/watch-history.json
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ElementTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "256t/editions/personal"
# Whole words, case-insensitive; a trailing * allows any word ending.
TERMS = ["Hugging Face", "HuggingFace", "Artifactory", "METR", "GemStuffer", "Collusion Wiki",
         "Greenblatt", "Black Hat", "misalign*", "This Week in Tech", "Intelligent Machines"]
URLS = ["-RXD4bTuFTo", "87DyyMV0kCY", "twit.tv/shows/intelligent-machines/episodes/880",
        "twit.tv/shows/this-week-in-tech/episodes/1094", "hugging-face-model-evaluation-security-incident",
        "hugging-face-incident-and-misalignment", "dwarkesh.com/p/ryan-greenblatt"]
TWITTER_EPOCH_MS = 1288834974657


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def from_epoch(seconds) -> datetime | None:
    return datetime.fromtimestamp(float(seconds), timezone.utc) if seconds not in (None, "") else None


def from_iso(value) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"unqualified timestamp: {value}")
    return dt


def snowflake_time(post_id) -> datetime | None:
    try:
        return datetime.fromtimestamp(((int(post_id) >> 22) + TWITTER_EPOCH_MS) / 1000, timezone.utc)
    except (TypeError, ValueError):
        return None


def text_of(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(text_of(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_of(v) for v in value)
    return ""


def load_js(path: Path):
    """X archive files are JavaScript assignments around a JSON array."""
    body = path.read_text(encoding="utf-8")
    return json.loads(body[body.index("=") + 1:].strip().rstrip(";"))


def rows(path: Path):
    """(kind, position, time, time meaning, role/product, public url, searchable text)."""
    name = path.name.lower()
    if name.endswith(".opml") or name.endswith(".xml"):
        for index, node in enumerate(ElementTree.parse(path).iter("outline")):
            if node.get("type") != "podcast-episode":
                continue
            yield ("podcast", f"outline {index}", from_iso(node.get("userUpdatedDate")),
                   "last change to this episode's state in the app (played/progress), not a listening time",
                   "played" if node.get("played") == "1" else "not marked played",
                   node.get("enclosureUrl") or node.get("url"), " ".join(filter(None, (node.get("title"), node.get("url")))))
        return
    if name.endswith(".js"):
        data = load_js(path)
        for index, entry in enumerate(data):
            if "tweet" in entry:
                post = entry["tweet"]
                created = datetime.strptime(post["created_at"], "%a %b %d %H:%M:%S %z %Y")
                role = "reply" if post.get("in_reply_to_status_id_str") else ("quote" if post.get("is_quote_status") else "post")
                yield ("x-post", f"[{index}]", created, "post creation time", role,
                       f"https://x.com/i/status/{post.get('id_str')}", text_of(post))
            elif "like" in entry:
                like = entry["like"]
                yield ("x-like", f"[{index}]", snowflake_time(like.get("tweetId")),
                       "creation time of the liked post; the like happened at or after it, time unrecorded", "like",
                       like.get("expandedUrl"), text_of(like))
            else:
                raise ValueError(f"{path}: unrecognised X archive entry keys {sorted(entry)}")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("header") in {"YouTube", "YouTube Music"}:
        for index, entry in enumerate(data):
            yield ("youtube-watch", f"[{index}]", from_iso(entry.get("time")),
                   "time YouTube recorded the watch; not duration or attention", entry.get("header"),
                   entry.get("titleUrl"), text_of({k: entry.get(k) for k in ("title", "titleUrl", "subtitles")}))
    elif isinstance(data, list) and data and isinstance(data[0], dict) and "mapping" in data[0]:
        for index, conversation in enumerate(data):
            for node_id, node in (conversation.get("mapping") or {}).items():
                message = (node or {}).get("message")
                if not message or not message.get("create_time"):
                    continue
                role = (message.get("author") or {}).get("role")
                model = (message.get("metadata") or {}).get("model_slug")
                yield ("chatgpt-message", f"[{index}] mapping {node_id}", from_epoch(message["create_time"]),
                       "stored message creation time", f"ChatGPT {role}" + (f" ({model})" if model else ""), None,
                       text_of(message.get("content")) + " " + str(conversation.get("title") or ""))
    elif isinstance(data, list) and data and isinstance(data[0], dict) and "chat_messages" in data[0]:
        for index, conversation in enumerate(data):
            for position, message in enumerate(conversation.get("chat_messages") or []):
                yield ("claude-ai-message", f"[{index}] chat_messages[{position}]", from_iso(message.get("created_at")),
                       "stored message creation time", f"claude.ai {message.get('sender')}", None,
                       text_of(message.get("text")) + " " + text_of(message.get("content")) + " " + str(conversation.get("name") or ""))
    else:
        raise ValueError(f"{path}: not a recognised export shape")


def inventory(paths: list[Path], start: datetime, end: datetime, terms: list[str], urls: list[str]) -> dict:
    patterns = [(term, re.compile(r"(?<!\w)" + (re.escape(term[:-1]) + r"\w*" if term.endswith("*") else re.escape(term))
                                  + r"(?!\w)", re.IGNORECASE)) for term in terms]
    result = dict(generated_at=iso(datetime.now(timezone.utc)), window=[iso(start), iso(end)],
                  terms=terms, urls=urls, files=[], rows=[],
                  claim_limit="Recorded service actions only; not what was noticed, read in full, or understood.")
    for path in paths:
        counts = dict(total=0, undated=0, outside_window=0, unmatched=0, matched=0)
        for kind, position, time, meaning, role, url, text in rows(path):
            counts["total"] += 1
            if time is None:
                counts["undated"] += 1
                continue
            if not start <= time <= end:
                counts["outside_window"] += 1
                continue
            matched = [term for term, pattern in patterns if pattern.search(text)]
            matched += [u for u in urls if u in text or (url and u in url)]
            if not matched:
                counts["unmatched"] += 1
                continue
            counts["matched"] += 1
            result["rows"].append(dict(kind=kind, file=str(path), position=position, utc=iso(time), time_meaning=meaning,
                                       role=role, url=url if kind in {"youtube-watch", "x-post", "x-like", "podcast"} else None,
                                       matched=sorted(set(matched))))
        result["files"].append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **counts))
    result["rows"].sort(key=lambda r: (r["utc"], r["file"], r["position"]))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("inventory")
    run.add_argument("paths", nargs="+", type=Path)
    run.add_argument("--from", dest="start", default="2026-07-01T00:00:00Z")
    run.add_argument("--to", dest="end", default="2026-09-02T00:00:00Z")
    run.add_argument("--term", action="append", help="replace the default term list (repeatable)")
    run.add_argument("--url", action="append", help="replace the default URL list (repeatable)")
    run.add_argument("--out", type=Path, default=OUT / "inventory.json")
    args = parser.parse_args(argv)
    try:
        result = inventory(args.paths, from_iso(args.start), from_iso(args.end), args.term or TERMS, args.url or URLS)
    except (ValueError, KeyError, OSError, ElementTree.ParseError) as error:
        print(error, file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for record in result["files"]:
        print(f"{record['path']}: {record['matched']} matched of {record['total']} "
              f"({record['outside_window']} outside window, {record['undated']} undated)")
    for row in result["rows"]:
        print(f"  {row['utc']}  {row['kind']:18} {row['role']}  {row['url'] or ''}  [{', '.join(row['matched'])}]")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
