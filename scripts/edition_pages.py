#!/usr/bin/env python3
"""Incident-movement pages and storyboards for the three-stream working edition.

    python3 scripts/edition_pages.py allocate            # print the page plan
    python3 scripts/edition_pages.py allocate --apply    # write incident/windows.json
    python3 scripts/edition_pages.py check               # windows + storyboards
    python3 scripts/edition_pages.py preview             # 256t/editions/incident-preview/
                                                         #   pages/, panels/, reader.html,
                                                         #   huggingface.html, gemstuffer.html, wiki.html
    python3 scripts/edition_pages.py status              # storyboard coverage by scene file
    python3 scripts/edition_pages.py sheet STEM [--from N --count N]   # lettered boards for review

Beats come from the unallocated manuscript (``edition_detail.manuscript``); this module
does not parse scripts. Windows name beats, never page numbers: a page number exists only
in the generated preview, derived from window order. Storyboards are keyed by beat ID, so
reallocation never invalidates a composition. A storyboard's ``source`` snapshot of the
beat's frame and lettering makes a script change require another review.

Owner rule, 15 September 2026: a beat known only to a day or a longer range goes on an
*interval page* whose clocks show that whole interval, placed right after the last timed
page inside it, and labelled that order within the interval is not recorded. Interval
pages are the only pages allowed to overlap the page before them.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import timedelta
import html
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import edition_detail
import font_key
import letterpress
import storyboards
from working_edition import DEFAULT, ROWS, bound, dump

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name("edition_reader_ui")
MOVEMENT = "incident"
OWNERS = ROWS[MOVEMENT]
LABELS = {"HuggingFace": "HUGGING FACE", "GemStuffer": "GEMSTUFFER", "Collusion Wiki": "COLLUSION WIKI"}
STREAMS = {"HuggingFace": ("huggingface.html", "Hugging Face"),
           "GemStuffer": ("gemstuffer.html", "GemStuffer"),
           "Collusion Wiki": ("wiki.html", "Collusion Wiki")}
SLOTS = 2                      # ordinary form: two positions per row
BROAD = timedelta(hours=12)    # a beat this long or longer is an interval beat from the start

# Page geometry, in the same 2800 x 4000 page space as data/panel-layout.json.
PAGE_W, PAGE_H = 2800, 4000
MARGIN = 140
LABEL_W = 110
ROW_TOP, ROW_H, ROW_GAP = 330, 1070, 60
PANEL_X, PANEL_GAP = MARGIN + LABEL_W + 30, 40
PANEL_W = (PAGE_W - MARGIN - PANEL_X - PANEL_GAP * (SLOTS - 1)) // SLOTS
PANEL_H = ROW_H
PANEL = (PANEL_W, PANEL_H)
LETTER_MIN, LETTER_MAX = 26, 44
CAPTION_BOX = [0.035, 0.705, 0.93, 0.265]

CHAPTERS = [("2026-05-31T23:59:59Z", "april-may", "April–May"),
            ("2026-06-30T23:59:59Z", "june", "June"),
            ("2026-07-07T23:59:59Z", "early-july", "1–7 July"),
            ("2026-07-13T23:59:59Z", "july-8-13", "8–13 July"),
            ("9999-12-31T23:59:59Z", "mid-late-july", "Mid–late July")]


def paths(edition):
    base = edition / MOVEMENT
    return base / "windows.json", base / "storyboards"


def beats(edition):
    """Incident beats in manuscript order: scenes by bounds, beats in scene order."""
    scenes = [s for s in edition_detail.manuscript(edition) if s["movement"] == MOVEMENT]
    scenes.sort(key=lambda s: (bound(s["start"]), bound(s["end"], True), s["owner"], s["id"]))
    result = {}
    for scene in scenes:
        for beat in scene["beats"]:
            result[beat["id"]] = dict(beat, owner=scene["owner"], scene=scene["id"], seq=len(result),
                                      a=bound(beat["time_start"]), z=bound(beat["time_end"], True))
    return result


def source_of(beat):
    """The reviewed part of a beat: what a composition must agree with."""
    return {"frame": beat["frame"], "lettering": beat["lettering"]}


# ------------------------------------------------------------------ allocation

def _pack(items, broad):
    timed = sorted((b for b in items if b["id"] not in broad), key=lambda b: (b["a"], b["seq"]))
    groups = {}
    for b in sorted((b for b in items if b["id"] in broad), key=lambda b: b["seq"]):
        groups.setdefault((b["a"], b["z"]), []).append(b)
    stream = [(b["a"], 0, b["a"], b["seq"], "beat", b) for b in timed]
    stream += [(z, 1, a, g[0]["seq"], "group", g) for (a, z), g in groups.items()]
    stream.sort(key=lambda e: e[:4])
    pages = []

    def room(page, members):
        need = Counter(b["owner"] for b in members)
        return all(len(page["rows"][o]) + n <= SLOTS for o, n in need.items())

    def add(page, b):
        page["rows"][b["owner"]].append(b)
        page["a"], page["z"] = min(page["a"], b["a"]), max(page["z"], b["z"])

    def new(kind, a, z):
        page = {"kind": kind, "rows": {o: [] for o in OWNERS}, "a": a, "z": z}
        pages.append(page)
        return page

    def longest(page, after=None):
        return max((x for r in page["rows"].values() for x in r
                    if x["id"] not in broad and (after is None or x["z"] > after)),
                   key=lambda x: (x["z"] - x["a"], x["z"], x["seq"]), default=None)

    for *_, kind, entry in stream:
        current = pages[-1] if pages else None
        if kind == "beat":
            b = entry
            if current and current["kind"] == "timed" and room(current, [b]):
                add(current, b)
                continue
            if current and not shares_boundary(current, b["a"]):
                return None, longest(current, b["a"])
            add(new("timed", b["a"], b["z"]), b)
            continue
        members = entry
        a, z = members[0]["a"], members[0]["z"]
        if current and current["z"] > z:
            # A timed beat began inside this interval and ends after it: it is the long one.
            culprit = longest(current, z)
            if culprit is not None:
                return None, culprit
        before = pages[-2]["z"] if len(pages) > 1 else None
        if current and room(current, members) and (
                current["kind"] == "interval" or before is None or min(current["a"], a) >= before):
            for b in members:
                add(current, b)
            continue
        queue = list(members)
        while queue:
            kind = "interval" if pages and a < pages[-1]["z"] else "timed"
            page = new(kind, a, z)
            rest = []
            for b in queue:
                if len(page["rows"][b["owner"]]) < SLOTS:
                    page["rows"][b["owner"]].append(b)
                else:
                    rest.append(b)
            queue = rest
    return pages, None


TOLERANCE = timedelta(minutes=1)


def shares_boundary(previous, start):
    """A page may begin inside the previous page's final minute when no beat there starts later.

    Same-minute or same-second beats that fill more than one page share the boundary clock;
    the shared instant is shown on both pages, never duplicated as an event.
    """
    latest = max(x["a"] for r in previous["rows"].values() for x in r)
    return start >= previous["z"] or (start >= latest and previous["z"] - start < TOLERANCE)


def allocate(edition):
    items = list(beats(edition).values())
    broad = {b["id"] for b in items if b["z"] - b["a"] >= BROAD}
    promoted = []
    while True:
        pages, culprit = _pack(items, broad)
        if pages is not None:
            break
        broad.add(culprit["id"])
        promoted.append(culprit["id"])
    windows = []
    for page in pages:
        members = [b for r in page["rows"].values() for b in r]
        first = min(members, key=lambda b: (b["a"], b["seq"]))
        start = min(members, key=lambda b: b["a"])["time_start"]
        end = max(members, key=lambda b: b["z"])["time_end"]
        wid = "incident-" + first["id"]
        count = sum(1 for w in windows if w["id"].startswith(wid))
        chapter = next(c for limit, c, _ in CHAPTERS if bound(end, True) <= bound(limit, True))
        windows.append({
            "id": wid + (f"-{count + 1}" if count else ""),
            "movement": MOVEMENT, "chapter": chapter,
            "kind": page["kind"],
            "start": start, "end": end,
            "rows": [{"owner": o, "slots": [b["id"] for b in page["rows"][o]] +
                      [None] * (SLOTS - len(page["rows"][o]))} for o in OWNERS]})
    return windows, promoted


def load_windows(edition):
    path, _ = paths(edition)
    return json.loads(path.read_text()) if path.is_file() else []


def window_errors(windows, table):
    errors, seen = [], []
    last = {o: None for o in OWNERS}
    previous = None
    for w in windows:
        wid = w["id"]
        if [r["owner"] for r in w["rows"]] != OWNERS:
            errors.append(f"{wid}: rows must be {', '.join(OWNERS)}")
            continue
        start, end = bound(w["start"]), bound(w["end"], True)
        if start > end:
            errors.append(f"{wid}: reversed clock")
        members = {"rows": {r["owner"]: [table[k] for k in r["slots"] if k in table] for r in w["rows"]}}
        if previous:
            if end < previous["z"]:
                errors.append(f"{wid}: page ends before the page it follows")
            if w.get("kind") != "interval" and not shares_boundary(previous, start):
                errors.append(f"{wid}: overlaps the previous page without being an interval page")
            if w.get("kind") == "interval" and start >= previous["z"]:
                errors.append(f"{wid}: marked interval but overlaps nothing")
        elif w.get("kind") == "interval":
            errors.append(f"{wid}: marked interval but overlaps nothing")
        if any(members["rows"].values()):
            previous = dict(members, z=end)
        filled = 0
        for row in w["rows"]:
            if not 1 <= len(row["slots"]) <= 3:
                errors.append(f"{wid}: each row needs one to three positions")
            for key in row["slots"]:
                if key is None:
                    continue
                filled += 1
                seen.append(key)
                b = table.get(key)
                if b is None:
                    errors.append(f"{wid}: unknown beat {key}")
                    continue
                if b["owner"] != row["owner"]:
                    errors.append(f"{key}: wrong row")
                if not start <= b["a"] <= b["z"] <= end:
                    errors.append(f"{key}: outside page clock {w['start']} – {w['end']}")
                p = last[row["owner"]]
                if p is not None and b["z"] < p["a"]:
                    errors.append(f"{key}: ends before {p['id']} begins, but follows it in the row")
                last[row["owner"]] = b
        if not filled:
            errors.append(f"{wid}: entirely empty page")
    counts = Counter(seen)
    errors += [f"{k}: placed {n} times" for k, n in counts.items() if n > 1]
    errors += [f"{k}: not placed" for k in table if k not in counts]
    return errors


# ------------------------------------------------------------------ storyboards

def load_boards(edition):
    _, directory = paths(edition)
    boards, errors = {}, []
    for path in sorted(directory.glob("*.json")) if directory.is_dir() else []:
        for key, scene in json.loads(path.read_text()).items():
            if key in boards:
                errors.append(f"{key}: storyboard defined twice")
            boards[key] = dict(scene, _file=path.name)
    return boards, errors


def palette():
    return {"palette": storyboards.load()["palette"]}


def caption_layout(beat, scene):
    record = letterpress.load_slots()
    specs = scene.get("lettering") or [{"box": CAPTION_BOX}]
    placed, missing = [], []
    for i, text in enumerate(beat["lettering"]):
        if i >= len(specs):
            missing.append(text)
            continue
        x, y, w, h = specs[i]["box"]
        x, y, w, h = x * PANEL_W, y * PANEL_H, w * PANEL_W, h * PANEL_H
        flow = font_key.flow(text, w - 40, h - 36, key="editorial", min_size=LETTER_MIN,
                             max_size=specs[i].get("max_size", LETTER_MAX))
        placed.append(letterpress.Placed("caption", f"caption-{i}", "", x, y, w, h, flow.size,
                                         flow.leading, tuple(flow.lines), flow.truncated, "editorial"))
    return placed, missing, record


def board_errors(boards, table):
    assets = json.loads(storyboards.LIBRARY.read_text())["assets"]
    colors = palette()["palette"]
    errors = []
    for key, scene in boards.items():
        if key not in table:
            errors.append(f"{key}: storyboard for unknown beat")
            continue
        beat = table[key]
        if scene.get("source") != source_of(beat):
            errors.append(f"{key}: beat changed; review composition and refresh its source snapshot")
        for field in ("title", "intent", "shot", "background", "nodes"):
            if not scene.get(field):
                errors.append(f"{key}: missing {field}")
        if scene.get("background") not in colors:
            errors.append(f"{key}: unknown background")
        placed, missing, _ = caption_layout(beat, scene)
        if missing or any(p.truncated for p in placed):
            errors.append(f"{key}: lettering does not fit at {LETTER_MIN}px or larger")
        zones = [(p.x / PANEL_W, p.y / PANEL_H, p.w / PANEL_W, p.h / PANEL_H) for p in placed]
        inked = []
        for node in scene.get("nodes", []):
            if node.get("asset") not in assets or not storyboards.box(node.get("box", [])):
                errors.append(f"{key}: invalid asset or box: {node.get('asset')}")
                continue
            if node.get("color") not in colors:
                errors.append(f"{key}: unknown color {node.get('color')}")
            if node.get("focus") and any(storyboards.overlap(node["box"], z) for z in zones):
                errors.append(f"{key}: focal {node['asset']} overlaps lettering")
            if node.get("label"):
                if node.get("font") not in font_key.load():
                    errors.append(f"{key}: label needs a font")
                lb = node.get("label_box")
                if lb:
                    if not storyboards.box(lb):
                        errors.append(f"{key}: invalid label box")
                        continue
                    flow = font_key.flow(node["label"], lb[2] * PANEL_W, lb[3] * PANEL_H, key=node["font"],
                                         min_size=18, max_size=node.get("label_size", 30))
                    if flow.truncated:
                        errors.append(f"{key}: label does not fit: {node['label']}")
                    if any(storyboards.overlap(lb, z) for z in zones):
                        errors.append(f"{key}: label overlaps lettering: {node['label']}")
                    # The drawn extent is the centred text, not the whole label box.
                    width = max((font_key.advance(line, flow.size, node["font"]) for line in flow.lines), default=0) / PANEL_W
                    inked.append((node["label"], [lb[0] + lb[2] / 2 - width / 2 - 0.005, lb[1], width + 0.01,
                                                  len(flow.lines) * flow.leading / PANEL_H]))
        for i, (name, a) in enumerate(inked):
            for other, b in inked[i + 1:]:
                if storyboards.overlap(a, b):
                    errors.append(f"{key}: labels collide: {name} / {other}")
    return errors


def clean_scene(scene):
    return {k: v for k, v in scene.items() if not k.startswith("_")}


def panel_svg(beat, scene):
    if scene is None:
        return placeholder_svg(beat)
    drawing = storyboards.render(clean_scene(scene), palette(), size=PANEL)
    placed, _, record = caption_layout(beat, scene)
    href = "data:image/svg+xml;base64," + base64.b64encode(drawing.encode()).decode()
    return letterpress.svg_panel(placed, record, PANEL_W, PANEL_H, art_href=href)


def placeholder_svg(beat):
    import textimage
    frame = textimage.flow("NO STORYBOARD YET — " + beat["frame"], PANEL_W - 80, PANEL_H * 0.5, min_size=22, max_size=34)
    caption = textimage.flow(" ".join(beat["lettering"]), PANEL_W - 80, PANEL_H * 0.3, min_size=18, max_size=34)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PANEL_W} {PANEL_H}" width="{PANEL_W}" height="{PANEL_H}">',
           f'<rect width="{PANEL_W}" height="{PANEL_H}" fill="#E7E0D0" stroke="#A17D45" stroke-width="6" stroke-dasharray="24 14"/>']
    y = 60
    for line in frame.lines:
        y += frame.leading
        out.append(f'<text x="40" y="{y:.0f}" font-family="Georgia, serif" font-style="italic" font-size="{frame.size}" fill="#6B2634">{html.escape(line)}</text>')
    y = PANEL_H * 0.66
    for line in caption.lines:
        y += caption.leading
        out.append(f'<text x="40" y="{y:.0f}" font-family="Georgia, serif" font-size="{caption.size}" fill="#101214">{html.escape(line)}</text>')
    return "".join(out) + "</svg>"


# ------------------------------------------------------------------ pages

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def clock(value):
    date = f"{int(value[8:10])} {MONTHS[int(value[5:7]) - 1]} {value[:4]}"
    if len(value) == 10:
        return date
    return date + " · " + value[11:-1] + " UTC"


def page_svg(number, window, table, panels, chapter_title):
    esc = html.escape
    serif = "Georgia, 'Times New Roman', serif"
    mono = "'IBM Plex Mono', Menlo, monospace"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_W} {PAGE_H}" width="{PAGE_W}" height="{PAGE_H}">',
           f'<title>Page {number:03} · {esc(clock(window["start"]))} to {esc(clock(window["end"]))}</title>',
           f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="#F4EFE4"/>',
           f'<text x="{MARGIN}" y="250" font-family="{mono}" font-weight="700" font-size="64" fill="#101214">{esc(clock(window["start"]))}</text>',
           f'<text x="{PAGE_W - MARGIN}" y="220" text-anchor="end" font-family="{serif}" font-size="40" fill="#5E737B">{esc(chapter_title)} · {number:03}</text>',
           f'<text x="{PAGE_W - MARGIN}" y="{PAGE_H - 120}" text-anchor="end" font-family="{mono}" font-weight="700" font-size="64" fill="#101214">{esc(clock(window["end"]))}</text>']
    if window.get("kind") == "interval":
        out.append(f'<text x="{MARGIN}" y="{PAGE_H - 130}" font-family="{serif}" font-style="italic" font-size="42" fill="#6B2634">'
                   f'Interval page: these beats are dated only to this span, and their times within it are not recorded.</text>')
    for r, row in enumerate(window["rows"]):
        y = ROW_TOP + r * (ROW_H + ROW_GAP)
        cx, cy = MARGIN + LABEL_W / 2, y + ROW_H / 2
        out.append(f'<rect x="{MARGIN}" y="{y}" width="{LABEL_W}" height="{ROW_H}" fill="#202326"/>'
                   f'<text x="{cx}" y="{cy}" transform="rotate(-90 {cx} {cy})" text-anchor="middle" dominant-baseline="central" '
                   f'font-family="{mono}" font-weight="700" font-size="50" letter-spacing="6" fill="#E7E0D0">{LABELS[row["owner"]]}</text>')
        width = (PAGE_W - MARGIN - PANEL_X - PANEL_GAP * (len(row["slots"]) - 1)) / len(row["slots"])
        for c, key in enumerate(row["slots"]):
            x = PANEL_X + c * (width + PANEL_GAP)
            if key is None:
                out.append(f'<rect x="{x:.0f}" y="{y}" width="{width:.0f}" height="{ROW_H}" fill="none" stroke="#CEC5B3" stroke-width="4"/>')
                continue
            svg = panels[key]
            href = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
            out.append(f'<image x="{x:.0f}" y="{y}" width="{width:.0f}" height="{ROW_H}" preserveAspectRatio="xMidYMid meet" href="{href}"/>')
            out.append(f'<rect x="{x:.0f}" y="{y - 4}" width="{min(width, 12 + len(stamp(table[key])) * 21):.0f}" height="0" />')
            out.append(f'<text x="{x + 4:.0f}" y="{y - 12}" font-family="{mono}" font-size="34" fill="#5E737B">{esc(stamp(table[key]))}</text>')
    out.append("</svg>")
    return "".join(out)


def stamp(beat):
    a, z = beat["time_start"], beat["time_end"]
    return clock(a) if a == z else clock(a) + " – " + clock(z)


def reader_manifest(windows, table):
    titles = {c: t for _, c, t in CHAPTERS}
    pages = []
    for number, w in enumerate(windows, 1):
        rows = [{"owner": LABELS[r["owner"]],
                 "slots": [{"key": k, "stamp": stamp(table[k])} if k else None
                           for k in r["slots"]]}
                for r in w["rows"]]
        pages.append({"n": number, "chapter": titles[w["chapter"]],
                      "kind": w.get("kind", "timed"),
                      "start": clock(w["start"]), "end": clock(w["end"]),
                      "rows": rows})
    return {"pages": pages}


def stream_document(owner, windows, table):
    """One stream as a text-only reading: each panel's clock, then its caption."""
    esc = html.escape
    titles = {c: t for _, c, t in CHAPTERS}
    title = STREAMS[owner][1]
    entries, current = [], None
    for number, w in enumerate(windows, 1):
        row = next(r for r in w["rows"] if r["owner"] == owner)
        keys = [k for k in row["slots"] if k]
        if not keys:
            continue
        if w["chapter"] != current:
            current = w["chapter"]
            entries.append(f'<h2>{esc(titles[current])}</h2>')
        for key in keys:
            beat = table[key]
            interval = ('<p class="interval">Interval page: this beat is dated only to its span; '
                        'its time within the span is not recorded.</p>'
                        if w.get("kind") == "interval" else "")
            captions = "".join(f"<p>{esc(text)}</p>" for text in beat["lettering"])
            entries.append(f'<article><header><time>{esc(stamp(beat))}</time>'
                           f'<span><a href="index.html#p{number:03}">p{number:03}</a> · '
                           f'<a href="panels/{key}.svg">{esc(key)}</a></span></header>'
                           f'{captions}{interval}</article>')
    count = len([e for e in entries if e.startswith("<article")])
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)} — incident stream, text only</title><style>'
            'body{margin:0;background:#101214;color:#E7E0D0;font:16px/1.5 Georgia,serif}main{max-width:80ch;margin:auto;padding:24px}'
            'h2{margin-top:2em}article{margin:1.8em 0}article p{margin:.5em 0}'
            'header{display:flex;justify-content:space-between;gap:1em;font:13px monospace;color:#8fa4ad}'
            'header span{white-space:nowrap}a{color:#bdd4df}.interval{font-style:italic;color:#c98790;font-size:14px}'
            '</style><main>'
            f'<h1>{esc(title)} — text only</h1>'
            '<p><strong>Draft preview of the working edition.</strong> Every panel in this stream, in page order: '
            'its clock, then the caption a reader sees on the panel. The same panels appear with the other two streams on '
            '<a href="index.html">the three-stream pages</a> and in the <a href="reader.html">keyboard reader</a>.</p>'
            f'<p>{count} panels.</p>' + "".join(entries) + '</main></html>\n')


def preview(edition, output):
    table = beats(edition)
    windows = load_windows(edition)
    boards, _ = load_boards(edition)
    if output.exists():
        marker = output / ".edition-pages"
        if not marker.exists():
            raise ValueError(f"refusing to replace unowned directory {output}")
        shutil.rmtree(output)
    (output / "pages").mkdir(parents=True)
    (output / "panels").mkdir()
    (output / ".edition-pages").write_text("generated by edition_pages.py preview\n")
    (output / "empty.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PANEL_W} {PANEL_H}" '
        f'width="{PANEL_W}" height="{PANEL_H}"><rect width="{PANEL_W}" height="{PANEL_H}" '
        f'fill="#F4EFE4" stroke="#CEC5B3" stroke-width="8"/></svg>')
    rendered = {}
    for w in windows:
        for r in w["rows"]:
            for key in r["slots"]:
                if key and key not in rendered:
                    svg = panel_svg(table[key], boards.get(key))
                    ET.fromstring(svg)
                    (output / "panels" / f"{key}.svg").write_text(svg)
                    rendered[key] = svg
    titles = {c: t for _, c, t in CHAPTERS}
    cards, current = [], None
    for number, window in enumerate(windows, 1):
        svg = page_svg(number, window, table, rendered, titles[window["chapter"]])
        ET.fromstring(svg)
        (output / "pages" / f"{number:03}.svg").write_text(svg)
        if window["chapter"] != current:
            current = window["chapter"]
            cards.append(f'<h2 id="{current}">{html.escape(titles[current])}</h2>')
        drawn = sum(1 for r in window["rows"] for k in r["slots"] if k and k in boards)
        total = sum(1 for r in window["rows"] for k in r["slots"] if k)
        cards.append(f'<figure id="p{number:03}"><a href="pages/{number:03}.svg"><img loading="lazy" src="pages/{number:03}.svg" '
                     f'alt="Page {number:03}"></a><figcaption>{number:03} · {html.escape(clock(window["start"]))} → '
                     f'{html.escape(clock(window["end"]))}{" · interval" if window.get("kind") == "interval" else ""} · {drawn}/{total} boarded</figcaption></figure>')
    drawn = sum(1 for k in table if k in boards)
    document = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Three streams — incident pages</title><style>'
                'body{margin:0;background:#101214;color:#E7E0D0;font:16px/1.5 Georgia,serif}main{max-width:1500px;margin:auto;padding:24px}'
                'p{max-width:80ch}h2{margin-top:2em}section{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:24px}'
                'figure{margin:0}img{width:100%;display:block;background:#F4EFE4}figcaption{font:13px monospace;margin-top:6px}a{color:#bdd4df}'
                '</style><main><h1>Three streams — incident movement (working draft)</h1>'
                '<p><strong>Draft preview of the working edition.</strong> Not the published book. Page numbers here are derived from window order and are not canonical identities.</p>'
                '<p><strong>How to read a page.</strong> Pages run forward in UTC. The clock at upper left is where the page begins; the clock at lower right is where it ends; everything on the page falls between them. '
                'The three rows are always Hugging Face, GemStuffer and the Collusion Wiki, top to bottom. Read each row left to right. Rows share the page interval, not an instant: '
                'a panel in one row is not simultaneous with the panel above or below it. Each panel carries its own time above it. '
                'An empty frame means no event is depicted from the available record, not that nothing happened. '
                'An interval page holds beats known only to a day or a longer span; it follows the timed pages inside that span, and the order of its beats within the span is not recorded.</p>'
                f'<p>{len(windows)} pages · {len(table)} beats · {drawn} storyboarded.</p>'
                '<p><a href="reader.html">Keyboard reader</a>: space toggles two-page spread and single-panel views; '
                '← → turn a spread or a panel; ↑ ↓ move between rows in panel view.</p>'
                '<p>One stream at a time, text only: <a href="huggingface.html">Hugging Face</a> · '
                '<a href="gemstuffer.html">GemStuffer</a> · <a href="wiki.html">Collusion Wiki</a>.</p><section>' +
                "".join(c if c.startswith("<figure") else "</section>" + c + "<section>" for c in cards) + '</section></main></html>\n')
    (output / "index.html").write_text(document)
    for asset in UI.iterdir():
        if asset.is_file():
            shutil.copy(asset, output / asset.name)
    (output / "reader-data.js").write_text(
        "const READER_DATA = " + json.dumps(reader_manifest(windows, table)) + ";\n")
    for owner in OWNERS:
        (output / STREAMS[owner][0]).write_text(stream_document(owner, windows, table))
    rel = output.relative_to(ROOT) if output.is_relative_to(ROOT) else output
    print(f"{len(windows)} pages; {len(rendered)} panels; {drawn}/{len(table)} beats storyboarded; "
          f"wrote {rel}/index.html, {rel}/reader.html and "
          + ", ".join(STREAMS[o][0] for o in OWNERS))


def status(edition):
    table = beats(edition)
    boards, _ = load_boards(edition)
    by_scene_file = Counter()
    done = Counter()
    for scene_path in sorted((edition / "manuscript").glob("*.json")):
        for scene in json.loads(scene_path.read_text()):
            if scene["movement"] != MOVEMENT:
                continue
            for b in scene["beats"]:
                by_scene_file[scene_path.stem] += 1
                done[scene_path.stem] += b["id"] in boards
    for stem, n in sorted(by_scene_file.items()):
        print(f"{done[stem]:4}/{n:<4} {stem}")
    print(f"{sum(done.values())}/{len(table)} incident beats storyboarded")


def sheet(edition, stem, output, first=0, count=12):
    """Lettered boards of one manuscript file beside their frame directions, for visual review."""
    table = beats(edition)
    boards, _ = load_boards(edition)
    keys = [b["id"] for scene in json.loads((edition / "manuscript" / (stem + ".json")).read_text())
            if scene["movement"] == MOVEMENT for b in scene["beats"]][first:first + count]
    cells = []
    for key in keys:
        svg = panel_svg(table[key], boards.get(key))
        href = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
        cells.append(f'<figure><img src="{href}"><figcaption><b>{html.escape(key)}</b> · '
                     f'{html.escape(stamp(table[key]))}<br>{html.escape(table[key]["frame"])}</figcaption></figure>')
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"{stem}-{first:03}.html"
    target.write_text('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#333;display:grid;'
                      'grid-template-columns:repeat(4,1fr);gap:8px;padding:8px}figure{margin:0}img{width:100%;display:block}'
                      'figcaption{font:11px/1.3 sans-serif;color:#ddd;height:5.4em;overflow:hidden}</style>' + "".join(cells))
    print(target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("allocate", "check", "preview", "status", "sheet"))
    parser.add_argument("stem", nargs="?", help="sheet: manuscript file stem")
    parser.add_argument("--from", dest="first", type=int, default=0)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--edition", type=Path, default=DEFAULT)
    parser.add_argument("--apply", action="store_true", help="allocate: write incident/windows.json")
    parser.add_argument("--output", type=Path, default=ROOT / "256t/editions/incident-preview")
    args = parser.parse_args(argv)
    try:
        table = beats(args.edition)
        if args.command == "allocate":
            windows, promoted = allocate(args.edition)
            errors = window_errors(windows, table)
            if errors:
                raise ValueError("\n".join(errors))
            kinds = Counter(w["kind"] for w in windows)
            chapters = Counter(w["chapter"] for w in windows)
            print(f"{len(windows)} pages ({kinds['timed']} timed, {kinds['interval']} interval) for {len(table)} beats")
            print("by chapter: " + ", ".join(f"{c} {n}" for c, n in chapters.items()))
            print(f"promoted to interval beats after overlapping a later timed beat: {len(promoted)}")
            displaced = 0
            last = {}
            for w in windows:
                for row in w["rows"]:
                    for key in row["slots"]:
                        if key:
                            if row["owner"] in last and table[key]["seq"] < last[row["owner"]]:
                                displaced += 1
                            last[row["owner"]] = max(last.get(row["owner"], -1), table[key]["seq"])
            print(f"beats shown before an earlier-drafted beat of their row: {displaced}")
            if args.apply:
                path, _ = paths(args.edition)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(dump(windows))
                print(f"wrote {path.relative_to(ROOT)}")
            else:
                print("Dry run; pass --apply to write.")
        elif args.command == "check":
            boards, errors = load_boards(args.edition)
            errors += window_errors(load_windows(args.edition), table)
            errors += board_errors(boards, table)
            if errors:
                raise ValueError("\n".join(errors))
            print(f"Incident pages check passed: {len(load_windows(args.edition))} pages, "
                  f"{len(boards)}/{len(table)} beats storyboarded. Draft; not an editorial approval.")
        elif args.command == "preview":
            preview(args.edition, args.output)
        elif args.command == "sheet":
            sheet(args.edition, args.stem, ROOT / "256t/editions/incident-boards", args.first, args.count)
        else:
            status(args.edition)
    except (ValueError, KeyError, OSError) as error:
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
