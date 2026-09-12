#!/usr/bin/env python3
"""256t content pointers: name exact bytes by their length and hash, per https://256t.org/.

A 256t content identifier (CID) is 8 to 94 base64url characters, unpadded:

- an 8-character length prefix, the content's length in octets as a 6-octet big-endian
  unsigned integer;
- then, for content of 64 octets or fewer, the content itself; for longer content, its
  SHA-512 digest, which is always 86 characters.

The URI form is `t256:<cid>`. Over HTTP, the CID is the final path segment of a base URL,
`https://256t.org/<cid>`. The three test vectors in `check` are the standard's own.

**Why this project uses it.** When a quotation cannot be written out in a file, point at it
instead. A pointer names three things: the vault copy (`t256:` of the whole file), a byte range
in it, and the excerpt (`t256:` of exactly those bytes). Anyone holding the copy can cut the
range, hash it and confirm the excerpt — which is gate 9's `verbatim` check, done without the
words ever entering the repository. The copy is named by content, so it cannot drift: a changed
transcript is a different CID.

**This tool never prints source text.** It prints CIDs, lengths and offsets only. One
exception is structural and is flagged when it happens: an excerpt of 64 octets or fewer has a
*literal* CID, which is the excerpt itself in base64url. A literal CID is a quotation in
encoding, and is treated as one.

Vault copies are content-addressed but not published: `256t/` is a link-only reference vault,
so a `https://256t.org/` address for a vault copy will normally not resolve, and uploading one
would republish the artifact. The pointer is verifiable offline by anyone with a copy.

    python3 scripts/t256.py check
    python3 scripts/t256.py cid --file PATH
    python3 scripts/t256.py records
    python3 scripts/t256.py pointer --id SOURCE_ID --bytes 1200-1399
    python3 scripts/t256.py pointer --file 256t/transcripts/NAME.md --timecodes 30:47-31:14
    python3 scripts/t256.py locate --file 256t/transcripts/NAME.md --text-file wording.txt
    python3 scripts/t256.py verify
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "256t"
LITERAL_LIMIT = 64
HASH_CHARS = 86
BASE_URL = "https://256t.org/"

URI = re.compile(r"t256:([A-Za-z0-9_-]{8,94})((?:\.[A-Za-z0-9]+)*)")
# A pointer's locator names the copy and the inclusive byte range, HTTP Range style.
LOCATOR_RANGE = re.compile(r"bytes=(\d+)-(\d+)")

# The standard's own test vectors: (content, CID).
VECTORS = (
    (b"", "AAAAAAAA"),
    (b"Hello, World!", "AAAAAAANSGVsbG8sIFdvcmxkIQ"),
    (b"a" * 65, "AAAAAABBuDCGzYSU5VcIrX7Ngt-0vKG9ph7Lt8rwxolnkC5wk0Xl2DBet6wNWIr8bLt1FhqpyMfg6phr2DPa_l4czTc0Wg"),
)


def b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def cid(data: bytes) -> str:
    """The 256t CID of these exact bytes."""
    prefix = b64(len(data).to_bytes(6, "big"))
    payload = data if len(data) <= LITERAL_LIMIT else hashlib.sha512(data).digest()
    return prefix + b64(payload)


def uri(data: bytes) -> str:
    return f"t256:{cid(data)}"


def is_literal(value: str) -> bool:
    return declared_length(value) <= LITERAL_LIMIT


def declared_length(value: str) -> int:
    """The content length a CID or t256 URI declares, from its prefix alone."""
    match = URI.fullmatch(value) if value.startswith("t256:") else None
    text = match.group(1) if match else value
    return int.from_bytes(base64.urlsafe_b64decode(text[:8]), "big")


def uri_problem(value: str) -> str | None:
    """Why `value` is not a well-formed t256 URI, or None if it is."""
    match = URI.fullmatch(value)
    if not match:
        return "is not a t256 URI (t256: followed by 8-94 base64url characters)"
    identifier = match.group(1)
    length = declared_length(identifier)
    payload = identifier[8:]
    if length > LITERAL_LIMIT:
        if len(payload) != HASH_CHARS:
            return f"declares {length} octets, so its payload must be an {HASH_CHARS}-character SHA-512"
    elif len(payload) != len(b64(bytes(length))):
        return f"declares {length} octets but carries a literal payload of the wrong length"
    return None


# --- the vault -------------------------------------------------------------

def vault_files() -> list[Path]:
    """Every copy a pointer may name: accepted bodies, historical blobs, and transcripts."""
    if not VAULT.is_dir():
        return []
    found = list((VAULT / "records").glob("*/content.bin"))
    found += list((VAULT / "records").glob("*/blobs/*"))
    found += [path for path in (VAULT / "transcripts").glob("*") if path.is_file()]
    found += [path for path in (VAULT / "title-source").glob("*") if path.is_file()]
    return sorted(found)


def find_copy(record_uri: str) -> Path | None:
    """The vault file with this CID. The length prefix narrows the search before any hashing."""
    size = declared_length(record_uri)
    for path in vault_files():
        if path.stat().st_size == size and uri(path.read_bytes()) == record_uri:
            return path
    return None


def resolve_source(file: Path | None, source_id: str | None) -> Path:
    if file:
        path = file if file.is_absolute() else ROOT / file
    elif source_id:
        path = VAULT / "records" / source_id / "content.bin"
    else:
        raise SystemExit("name a copy with --file or --id")
    if not path.is_file():
        raise SystemExit(f"no such copy: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return path


# --- ranges ----------------------------------------------------------------

TIMECODE_LINE = re.compile(rb"^(\d{1,2}:\d{2}(?::\d{2})?)\r?\n", re.MULTILINE)


def timecode_range(data: bytes, first: str, last: str) -> tuple[int, int]:
    """Inclusive byte range covering the caption lines stamped `first` through `last`.

    For transcripts that alternate a timestamp line with a caption line. The range runs from
    the first caption's first byte to the last caption's final byte, and includes the
    timestamp lines between — it names the span, not a sentence. Use `locate` or `--bytes` to
    point at exact words.
    """
    stamps = {match.group(1).decode(): match for match in TIMECODE_LINE.finditer(data)}
    if first not in stamps or last not in stamps:
        missing = [code for code in (first, last) if code not in stamps]
        raise SystemExit(f"no caption stamped {', '.join(missing)} in this copy")
    start = stamps[first].end()
    tail = stamps[last].end()
    newline = data.find(b"\n", tail)
    end = (newline if newline != -1 else len(data)) - 1
    if data[end:end + 1] == b"\r":
        end -= 1
    if end < start:
        raise SystemExit("the last timecode precedes the first")
    return start, end


# What `--loose` steps over between words in a caption transcript: punctuation, timestamp
# lines, and the fillers automatic transcription keeps.
LOOSE_GAP = r"(?:[^\w']|\b\d{1,2}:\d{2}(?::\d{2})?\b|\b(?:uh|um)\b)+"


def locate(data: bytes, wording: str, *, loose: bool = False) -> list[tuple[int, int]]:
    """Every inclusive byte range whose text matches `wording`, ignoring case, line wrapping
    and quote style. The wording comes from the caller; nothing is printed from the copy.

    `loose` also ignores punctuation, and steps over timestamp lines and "uh"/"um" between
    words. The bytes it points at are then the transcript's, not the wording supplied — which
    is the point: the pointer names what the record holds, and the lettering is compared
    against that at gate 9.
    """
    text = data.decode("utf-8", errors="replace")
    if loose:
        words = re.findall(r"[\w']+", wording.replace("’", "'"))
        if not words:
            raise SystemExit("the wording to locate is empty")
        pattern = re.compile(
            LOOSE_GAP.join(re.escape(word).replace("'", "['’]") for word in words), re.IGNORECASE
        )
        return [
            (len(text[: m.start()].encode("utf-8")), len(text[: m.end()].encode("utf-8")) - 1)
            for m in pattern.finditer(text)
        ]
    words = wording.split()
    if not words:
        raise SystemExit("the wording to locate is empty")
    quotes = str.maketrans({"'": "['‘’]", "’": "['‘’]", "‘": "['‘’]", '"': '["“”]', "“": '["“”]', "”": '["“”]'})

    def token(word: str) -> str:
        return "".join(ch.translate(quotes) if ch in "'‘’\"“”" else re.escape(ch) for ch in word)

    pattern = re.compile(r"\s+".join(token(word) for word in words), re.IGNORECASE)
    ranges = []
    for match in pattern.finditer(text):
        start = len(text[: match.start()].encode("utf-8"))
        end = start + len(match.group(0).encode("utf-8")) - 1
        ranges.append((start, end))
    return ranges


def describe(path: Path, data: bytes, start: int, end: int) -> str:
    if not 0 <= start <= end < len(data):
        raise SystemExit(f"range bytes={start}-{end} is outside this copy of {len(data)} octets")
    excerpt = data[start:end + 1]
    record = uri(data)
    pointer = uri(excerpt)
    shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    lines = [
        f"copy:     {shown}",
        f"record:   {record}  ({len(data)} octets)",
        f"range:    bytes={start}-{end}  ({len(excerpt)} octets)",
        f"pointer:  {pointer}",
        f"http:     {BASE_URL}{cid(excerpt)}",
        "",
        "exact_strings entry:",
        f"  - pointer: {pointer}",
        "    source: SOURCE-KEY",
        f"    locator: {record} bytes={start}-{end}; HUMAN-READABLE LOCATOR",
        "    verification: unchecked",
        "    rights: unresolved",
    ]
    if len(excerpt) <= LITERAL_LIMIT:
        lines.append("")
        lines.append(
            f"NOTE: {len(excerpt)} octets is within the {LITERAL_LIMIT}-octet literal limit, so this "
            "CID is the excerpt itself in base64url. Treat it as a quotation, not a hash."
        )
    return "\n".join(lines)


# --- checking registrations --------------------------------------------------

def registered_pointers() -> list[tuple[str, dict[str, str]]]:
    import crossref

    files = sorted((ROOT / "content" / "pages").glob("*.md"))
    files += sorted((ROOT / "content" / "novella").glob("*/*.md"))
    found = []
    for path in files:
        metadata = crossref.front_matter(path.read_text(encoding="utf-8")) or ""
        entries, _ = crossref.read_exact_strings(metadata)
        found += [(str(path.relative_to(ROOT)), entry) for entry in entries if entry.get("pointer")]
    return found


def verify() -> int:
    """Check every registered pointer against the vault: cut the range, hash it, compare."""
    pointers = registered_pointers()
    if not pointers:
        print("t256 verify: no registered pointers")
        return 0
    if not VAULT.is_dir():
        print(f"t256 verify: {len(pointers)} registered pointer(s); no local vault, nothing verified")
        return 0
    failures = 0
    for where, entry in pointers:
        locator = entry.get("locator", "")
        record = URI.search(locator)
        span = LOCATOR_RANGE.search(locator)
        if not record or not span:
            print(f"UNLOCATED  {where}: {entry['pointer']} — locator names no record URI and byte range")
            failures += 1
            continue
        copy = find_copy(record.group(0))
        if copy is None:
            print(f"ABSENT     {where}: {entry['pointer']} — no vault copy is {record.group(0)[:24]}…")
            continue
        start, end = int(span.group(1)), int(span.group(2))
        data = copy.read_bytes()
        if end >= len(data) or uri(data[start:end + 1]) != entry["pointer"]:
            print(f"MISMATCH   {where}: {entry['pointer']} — bytes={start}-{end} of {copy.relative_to(ROOT)} hash differently")
            failures += 1
        else:
            print(f"verified   {where}: bytes={start}-{end} of {copy.relative_to(ROOT)}")
    return 1 if failures else 0


def check() -> int:
    findings = []
    for content, expected in VECTORS:
        if cid(content) != expected:
            findings.append(f"test vector of {len(content)} octets: got {cid(content)}")
        if uri_problem(f"t256:{expected}"):
            findings.append(f"test vector {expected[:16]}… rejected: {uri_problem('t256:' + expected)}")
        if declared_length(expected) != len(content):
            findings.append(f"test vector {expected[:16]}… declares the wrong length")
    if uri_problem("t256:AAAAAABBshort") is None:
        findings.append("a hashed CID with a short payload was accepted")
    if uri_problem("t256:AAAAAAANSGVs") is None:
        findings.append("a literal CID of the wrong length was accepted")
    if uri_problem(f"t256:{VECTORS[1][1]}.txt") is not None:
        findings.append("a suffix permitted by the URI grammar was rejected")
    # Round trip a pointer on synthetic data, including a wrapped, curly-quoted match.
    sample = "0:01\nIt’s the first\n0:05\nline of text.\n".encode("utf-8")
    start, end = timecode_range(sample, "0:01", "0:05")
    if sample[start:end + 1] != "It’s the first\n0:05\nline of text.".encode("utf-8"):
        findings.append("timecode range cut the wrong bytes")
    located = locate(sample, "it's THE first")
    if located != [(5, 5 + len("It’s the first".encode("utf-8")) - 1)]:
        findings.append(f"locate returned {located}")
    loose = locate(sample, "first, line", loose=True)
    if len(loose) != 1 or sample[loose[0][0]:loose[0][1] + 1] != b"first\n0:05\nline":
        findings.append(f"loose locate returned {loose}")
    if locate(sample, "first line"):
        findings.append("strict locate stepped over a timestamp line")
    for where, entry in registered_pointers():
        problem = uri_problem(entry["pointer"])
        if problem:
            findings.append(f"{where}: pointer {problem}")
    print(f"t256: {len(findings)} findings")
    for finding in findings:
        print(f"- {finding}")
    return 1 if findings else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "cid", "records", "pointer", "locate", "verify"))
    parser.add_argument("--file", type=Path, help="a copy, by path")
    parser.add_argument("--id", help="a copy, by data/256t-sources.tsv id (its accepted content.bin)")
    parser.add_argument("--bytes", help="inclusive byte range START-END")
    parser.add_argument("--timecodes", help="caption span FIRST-LAST, e.g. 30:47-31:14")
    parser.add_argument("--text-file", type=Path, help="for locate: a file holding the wording to find")
    parser.add_argument("--loose", action="store_true",
                        help="for locate: also ignore punctuation, timestamp lines and uh/um")
    args = parser.parse_args()

    if args.command == "check":
        return check()
    if args.command == "verify":
        return verify()
    if args.command == "records":
        files = vault_files()
        if not files:
            print("no local vault")
        for path in files:
            print(f"{uri(path.read_bytes())}\t{path.relative_to(ROOT)}")
        return 0
    path = resolve_source(args.file, args.id)
    data = path.read_bytes()
    if args.command == "cid":
        print(uri(data))
        return 0
    if args.command == "pointer":
        if bool(args.bytes) == bool(args.timecodes):
            raise SystemExit("pointer needs exactly one of --bytes or --timecodes")
        if args.bytes:
            match = re.fullmatch(r"(\d+)-(\d+)", args.bytes)
            if not match:
                raise SystemExit("--bytes takes START-END")
            start, end = int(match.group(1)), int(match.group(2))
        else:
            first, _, last = args.timecodes.partition("-")
            start, end = timecode_range(data, first, last or first)
        print(describe(path, data, start, end))
        return 0
    if not args.text_file:
        raise SystemExit("locate needs --text-file")
    ranges = locate(data, args.text_file.read_text(encoding="utf-8"), loose=args.loose)
    if not ranges:
        print("no match in this copy")
        return 1
    if len(ranges) > 1:
        print(f"{len(ranges)} matches; showing each\n")
    print("\n\n".join(describe(path, data, start, end) for start, end in ranges))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
