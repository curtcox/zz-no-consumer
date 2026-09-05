#!/usr/bin/env python3
"""Deterministic, dependency-free knowledge-map design studies: generate, check, test."""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/knowledge-map-samples.json"
OUTPUT = ROOT / "assets/knowledge-maps/v1"
RENDERER_VERSION = "knowledge-map-svg-1.0.0"
NS = "http://www.w3.org/2000/svg"
INK = "#101214"
SHADOW = "#202326"
PAPER = "#E7E0D0"
DIRTY = "#CEC5B3"
STEEL = "#5E737B"
AMBER = "#A17D45"
INSTITUTION = "#68766B"
FAMILIES = ("a", "b", "c", "d")
FIXTURES = ("010-hint", "010-no-p6", "016", "039-before", "039-after")
VIEWPOINTS = ("reader", "responders")
PROPOSITIONS = tuple(f"P{i}" for i in range(1, 7))
EVIDENCE_STATES = {"dark", "lit", "hatched"}
REGION_LABELS = {
    "P1": ["P1 / COORDINATION", "deliberate?"],
    "P2": ["P2 / RECURRENCE", "independent?"],
    "P3": ["P3 / RECORD", "equals event?"],
    "P4": ["P4 / REPORTING", "nobody told?"],
    "P5": ["P5 / MEASUREMENT", "independent?"],
}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def load_data():
    return json.loads(DATA.read_text(encoding="utf-8"))


def sample_id(family, fixture, viewpoint):
    if fixture.startswith("010-"):
        return f"{family}-010-{viewpoint}-{fixture[4:]}"
    return f"{family}-{fixture}-{viewpoint}"


def states_for(data, fixture, viewpoint):
    model = data["state_models"][data["fixtures"][fixture]["models"][viewpoint]]
    return dict(model["propositions"], p1_foothold=model["p1_foothold"],
                observations=copy.deepcopy(model["observations"]),
                p6_presence=data["fixtures"][fixture]["p6_presence"])


def semantic_state(states):
    return {key: value for key, value in states.items() if key != "p6_presence"}


def text(x, y, value, size=14, fill=PAPER, anchor="start", mono=False, weight="normal"):
    font = "monospace" if mono else "Arial, Helvetica, sans-serif"
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(value)}</text>')


def path(points):
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points) + " Z"


def rect(x, y, w, h, fill, stroke="none", extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" {extra}/>'


def line(x1, y1, x2, y2, stroke=STEEL, width=1, extra=""):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def paint(state, prefix):
    return {"dark": SHADOW, "lit": PAPER, "hatched": f"url(#{prefix}-hatch)"}[state]


def label(x, y, lines, dark=False, size=13):
    width = max(len(s) for s in lines) * size * 0.57 + 16
    height = len(lines) * (size + 3) + 6
    result = rect(round(x - width / 2, 2), round(y - 14, 2), round(width, 2), height,
                  INK if dark else PAPER)
    for i, value in enumerate(lines):
        result += text(round(x, 2), round(y + i * (size + 3), 2), value, size,
                       PAPER if dark else INK, "middle", weight="bold" if i == 0 else "normal")
    return result


def region(prefix, key, points, state, label_at, lines, foothold=None):
    d = path(points)
    clip_id = f"{prefix}-{key}-clip"
    x0 = min(p[0] for p in points)
    x1 = max(p[0] for p in points)
    y0 = min(p[1] for p in points)
    y1 = max(p[1] for p in points)
    out = f'<g data-region="{key}" data-state="{state}">'
    out += f'<defs><clipPath id="{clip_id}"><path d="{d}"/></clipPath></defs>'
    out += f'<path data-terrain="{key}" d="{d}" fill="{paint(state, prefix)}" stroke="{DIRTY}" stroke-width="1.7"/>'
    out += f'<g clip-path="url(#{clip_id})">'
    if foothold is not None:
        band = path([(x0, y0), (x1, y0), (x1, y0 + (y1-y0)*0.27),
                     (x0 + (x1-x0)*0.52, y0 + (y1-y0)*0.20), (x0, y0 + (y1-y0)*0.33)])
        out += (f'<path data-region="P1-foothold" data-state="{foothold}" data-terrain="P1-foothold" '
                f'd="{band}" fill="{paint(foothold, prefix)}" stroke="{DIRTY}" stroke-width="1.3"/>')
    out += '<g data-layer="retained-terrain" fill="none" stroke="' + STEEL + '" stroke-width="0.85">'
    for i in range(8):
        yy = y0 + 9 + i * (y1-y0) / 7
        bend = ((i % 3) - 1) * 9
        out += (f'<path d="M{x0-15:.2f},{yy:.2f} C{x0+(x1-x0)*0.28:.2f},{yy-25+bend:.2f} '
                f'{x0+(x1-x0)*0.48:.2f},{yy+28:.2f} {x1+20:.2f},{yy-12:.2f}"/>')
    cx = x0 + (x1-x0)*0.72
    cy = y0 + (y1-y0)*0.67
    for i in range(3):
        out += f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{14+i*9}" ry="{7+i*6}" transform="rotate(-24 {cx:.2f} {cy:.2f})"/>'
    out += '</g>'
    out += (f'<path data-layer="retained-terrain" d="M{x0+15:.2f},{y1-16:.2f} '
            f'Q{x0+(x1-x0)*0.5:.2f},{y0+12:.2f} {x1-15:.2f},{y0+(y1-y0)*0.6:.2f}" '
            f'fill="none" stroke="{STEEL}" stroke-width="2.8"/>')
    for i in range(3):
        sx = x0 + (x1-x0)*(0.18+i*0.25)
        sy = y0 + (y1-y0)*(0.72-(i % 2)*0.3)
        out += f'<path data-layer="retained-terrain" d="M{sx:.2f},{sy:.2f} l6,-9 l6,9 Z" fill="{INK}" stroke="{DIRTY}"/>'
    out += '</g>'
    out += label(*label_at, lines, dark=state == "dark")
    return out + '</g>'


def p6(prefix, presence, shape, x, y, viewpoint, compact=False):
    if presence == "hidden":
        return ""
    words = ["P6", "UNMAPPED"] if presence == "hint" else ["P6 / UNREACHABLE", "NO CAUSAL ACCESS"]
    if compact:
        words = ["P6", "UNREACHABLE" if presence != "hint" else "UNMAPPED"]
    result = (f'<g data-region="P6" data-state="dark" data-presence="{presence}">'
              f'<path data-terrain="P6" d="{shape}" fill="{INK}" stroke="{DIRTY}" stroke-width="2.5"/>')
    result += label(x, y, words, dark=True, size=12 if compact else 13)
    result += '</g>'
    return result


def silhouette(x, y, angle, kind, active=False):
    stroke = PAPER if active else STEEL
    out = f'<g transform="translate({x:.2f} {y:.2f}) rotate({angle:.2f})" fill="{INK}" stroke="{stroke}" stroke-width="1.8">'
    if kind == 0:
        out += '<path d="M-20,10 L-20,-9 L20,-9 L20,10 M-13,-9 L-13,-18 L13,-18 L13,-9 M-7,10 L-7,17 M7,10 L7,17"/>'
    elif kind == 1:
        out += '<path d="M-24,9 L24,9 M-20,9 L-20,19 M20,9 L20,19 M-15,5 L-15,-16 L15,-16 L15,5 Z M0,5 L0,9"/>'
    elif kind == 2:
        out += '<path d="M-23,12 L23,12 L23,-12 L-23,-12 Z M-15,-12 L-15,12 M15,-12 L15,12 M-23,0 L23,0"/>'
    elif kind == 3:
        out += '<path d="M-23,13 L23,13 M-16,13 L-16,-13 L4,-13 L4,8 L-16,8 M-8,-7 L-1,-7 M9,-3 L20,-3 L20,9 L9,9 Z"/>'
    else:
        out += '<path d="M-23,14 L23,14 M-18,14 L-18,-13 L-5,-22 L8,-13 L8,14 M-12,-10 L2,-10 L2,1 L-12,1 Z M13,5 L21,5 L21,14"/>'
    return out + '<path d="M-4,25 L0,31 L4,25"/>' + '</g>'


def border_map(prefix, states):
    shapes = [
        ("P1", [(48,136),(120,108),(272,126),(294,189),(250,275),(137,265),(60,218)], (170,189), ["P1 / COORDINATION", "deliberate?"]),
        ("P2", [(272,126),(416,109),(515,153),(490,266),(370,284),(294,189)], (397,191), ["P2 / RECURRENCE", "independent?"]),
        ("P3", [(60,218),(137,265),(250,275),(284,380),(209,445),(86,427),(40,338)], (158,340), ["P3 / RECORD", "equals event?"]),
        ("P4", [(250,275),(370,284),(490,266),(501,372),(451,451),(330,435),(284,380)], (386,357), ["P4 / REPORTING", "nobody told?"]),
        ("P5", [(515,153),(636,112),(714,150),(706,293),(668,425),(565,439),(501,372),(490,266)], (604,284), ["P5 / MEASUREMENT", "independent?"])
    ]
    out = line(747,106,747,456,DIRTY,3)
    for key, pts, at, words in shapes:
        out += region(prefix,key,pts,states[key],at,words,states["p1_foothold"] if key == "P1" else None)
    for y in range(117,448,22):
        out += line(738,y,747,y,DIRTY,1.5)
    out += text(44,466,"SCHEMATIC CLAIM TERRAIN / BORDER OF AVAILABLE SUPPORT",12,mono=True)
    out += p6(prefix,states["p6_presence"],path([(769,112),(936,105),(921,448),(771,459)]),850,265,"",True)
    return out


def ellipse_point(cx, cy, rx, ry, angle):
    a = math.radians(angle)
    return (cx + rx * math.cos(a), cy + ry * math.sin(a))


def silhouette_map(prefix, states):
    out = ''
    cx, cy = 470, 285
    names = ["EVALUATION", "RESPONSE", "PLATFORM", "INVESTIGATOR", "HOME OFFICE"]
    words = [["P1 / COORDINATION"],["P2 / RECURRENCE"],["P3 / RECORD"],["P4 / REPORTING"],["P5 / MEASUREMENT"]]
    for i, a in enumerate((-126,-54,18,90,162)):
        angles = [a-31+j*62/8 for j in range(9)]
        pts = [ellipse_point(cx,cy,330,130,b) for b in angles]
        pts += [ellipse_point(cx,cy,140,70,b) for b in reversed(angles)]
        key = f"P{i+1}"
        at = ellipse_point(cx,cy,245,105,a)
        out += region(prefix,key,pts,states[key],at,words[i],states["p1_foothold"] if i == 0 else None)
        sx, sy = ellipse_point(cx,cy,402,167,a)
        out += silhouette(sx,sy,a-90,i,active=i == 1)
        tx, ty = ellipse_point(cx,cy,402,197,a)
        out += text(round(tx,2),round(ty,2),names[i],11,anchor="middle",mono=True)
    center = path([ellipse_point(cx,cy,112,56,a) for a in range(0,360,12)])
    out += p6(prefix,states["p6_presence"],center,cx,279,"",True)
    out += text(40,468,"FIVE INWARD VIEWS / SILHOUETTES DENOTE ACCESS BOUNDARIES, NOT KNOWN INTERIORS",12,mono=True)
    return out


def partial_map(prefix, states):
    sheets = [([(35,111),(470,106),(444,371),(60,390)],"PUBLIC ACCOUNT FRAGMENT"),
              ([(286,146),(725,129),(743,424),(266,446)],"INFERENCE FRAGMENT"),
              ([(505,187),(895,165),(919,448),(510,471)],"UNRESOLVED FRAGMENT")]
    out = ''
    for i,(pts,name) in enumerate(sheets):
        out += f'<path data-terrain="sheet-{i}" d="{path(pts)}" fill="{SHADOW}" stroke="{DIRTY}" stroke-width="2"/>'
        x,y = pts[0]
        out += text(x+12,y+21,name,11,mono=True)
    shapes = [
        ("P1",[(63,152),(232,146),(300,183),(255,281),(93,290)],(170,206),["P1 / COORDINATION"]),
        ("P2",[(318,191),(482,175),(573,204),(529,309),(336,331)],(438,251),["P2 / RECURRENCE"]),
        ("P3",[(75,310),(254,299),(284,358),(233,378),(90,367)],(172,336),["P3 / RECORD"]),
        ("P4",[(332,349),(509,322),(560,394),(490,422),(313,416)],(431,376),["P4 / REPORTING"]),
        ("P5",[(580,218),(732,207),(771,271),(746,390),(607,425),(568,345)],(668,305),["P5 / MEASUREMENT"])
    ]
    for key,pts,at,words in shapes:
        out += region(prefix,key,pts,states[key],at,words,states["p1_foothold"] if key == "P1" else None)
    for x,y in [(269,284),(535,309),(478,176)]:
        out += line(x-8,y,x+8,y,AMBER,2) + line(x,y-8,x,y+8,AMBER,2)
    out += p6(prefix,states["p6_presence"],path([(799,216),(897,210),(904,422),(786,435)]),846,318,"",True)
    out += text(40,468,"OFFSET SOURCE FRAGMENTS / OVERLAP IS NOT CORROBORATION",12,mono=True)
    return out


def nested_map(prefix, states, data, viewpoint):
    out = f'<path data-terrain="outer-frame" d="{path([(35,108),(939,108),(934,454),(43,466)])}" fill="{SHADOW}" stroke="{DIRTY}" stroke-width="2"/>'
    shapes = [
        ("P1",[(57,133),(222,125),(265,171),(236,252),(72,260)],(158,191),["P1 / COORDINATION"]),
        ("P2",[(281,132),(444,125),(476,182),(453,249),(277,264)],(369,192),["P2 / RECURRENCE"]),
        ("P3",[(60,286),(201,275),(223,337),(190,398),(72,404)],(143,329),["P3 / RECORD"]),
        ("P4",[(237,283),(375,272),(390,357),(355,415),(230,400)],(309,332),["P4 / REPORTING"]),
        ("P5",[(414,284),(550,258),(570,369),(540,433),(416,418),(389,357)],(481,343),["P5 / MEASUREMENT"])
    ]
    for key,pts,at,words in shapes:
        out += region(prefix,key,pts,states[key],at,words,states["p1_foothold"] if key == "P1" else None)
    attribution = data["attributions"][viewpoint]
    out += rect(620,126,309,252,INK,INSTITUTION,'stroke-width="2" stroke-dasharray="9 5" data-attribution="tentative"')
    out += text(635,149,"ATTRIBUTED INNER MAP",14,weight="bold")
    out += text(635,169,attribution["label"],13)
    out += text(635,190,"TENTATIVE / NOT DIRECT ACCESS",12,mono=True)
    out += line(565,199,620,199,INSTITUTION,2,'stroke-dasharray="6 4"')
    model = data["state_models"].get(attribution["model"])
    for i in range(5):
        x = 646 + (i % 3)*84
        y = 210 + (i // 3)*73
        pts = [(x,y+9),(x+44,y),(x+70,y+15),(x+61,y+56),(x+7,y+61)]
        key = f"P{i+1}"
        state = model["propositions"][key] if model else "dark"
        out += region(prefix,f"attributed-{key}",pts,state,(x+35,y+34),[key])
    out += p6(prefix,states["p6_presence"],path([(808,290),(902,288),(909,353),(811,355)]),858,311,"",True)
    out += text(635,399,"DASHED FRAME = ATTRIBUTION",12,mono=True)
    out += text(635,419,"Not a fourth evidence state.",13)
    out += text(635,439,"Unknown interiors stay dark.",13)
    out += p6(prefix,states["p6_presence"],path([(487,119),(572,120),(583,246),(487,250)]),534,169,"",True)
    out += text(40,470,"OUTER VIEWPOINT HOLDS A MODEL / THE MODEL DOES NOT BECOME ANOTHER PERSON'S INTERIOR",11,mono=True)
    return out


def observations(prefix, states):
    names = {"response": "ALERT / BOARD / PIVOT", "correction": "SCORER ACCOUNTS",
             "configuration": "CONFIGURATION ACCOUNT", "weights": "WEIGHTS ACCOUNT"}
    out = ''
    for i,(key,state) in enumerate(states["observations"].items()):
        x = 40+i*224
        pts = [(x,489),(x+192,484),(x+210,500),(x+201,528),(x+11,530)]
        name = names[key] if state != "dark" else "UNSURVEYED"
        out += f'<g data-observation="{key}" data-state="{state}">'
        out += f'<path data-terrain="observation-{key}" d="{path(pts)}" fill="{paint(state,prefix)}" stroke="{DIRTY}"/>'
        out += label(x+105,508,[name],dark=state == "dark",size=11)
        out += '</g>'
    return out


def render(data, sample):
    prefix = sample["id"]
    states = sample["states"]
    fixture = data["fixtures"][sample["fixture"]]
    out = (f'<svg xmlns="{NS}" width="960" height="640" viewBox="0 0 960 640" '
           f'role="img" aria-labelledby="{prefix}-title {prefix}-desc" data-sample-id="{prefix}">')
    out += f'<title id="{prefix}-title">{escape(sample["family_label"] + " — " + fixture["label"] + " — " + sample["viewpoint_label"])}</title>'
    out += f'<desc id="{prefix}-desc">{escape(sample["alt"])}</desc>'
    out += f'<metadata>{escape(json.dumps({"renderer": RENDERER_VERSION, "states": states},sort_keys=True))}</metadata>'
    out += (f'<defs><pattern id="{prefix}-hatch" patternUnits="userSpaceOnUse" width="9" height="9">'
            f'<rect width="9" height="9" fill="{DIRTY}"/><path d="M-2,2 L2,-2 M0,9 L9,0 M7,11 L11,7" '
            f'stroke="{INK}" stroke-width="1.1"/></pattern></defs>')
    out += rect(0,0,960,640,INK)
    out += text(28,29,f'{sample["family"].upper()} / {sample["family_label"].upper()}',21,weight="bold")
    out += text(932,28,sample["viewpoint_label"].upper(),17,anchor="end",weight="bold")
    out += text(28,53,fixture["label"],15)
    out += text(932,53,"DESIGN SAMPLE / NOT ADOPTED",12,anchor="end",mono=True)
    out += line(28,68,932,68,DIRTY)
    out += text(28,88,"OUR INFERENCE / SCHEMATIC TERRAIN / NO MEASURED BELIEFS",11,mono=True)
    out += '<g data-layer="map">'
    if sample["family"] == "a":
        out += border_map(prefix,states)
    elif sample["family"] == "b":
        out += silhouette_map(prefix,states)
    elif sample["family"] == "c":
        out += partial_map(prefix,states)
    else:
        out += nested_map(prefix,states,data,sample["viewpoint"])
    out += '</g>' + observations(prefix,states)
    out += rect(28,542,904,34,PAPER)
    out += text(40,564,fixture["captions"][sample["viewpoint"]],15,INK,weight="bold")
    out += text(28,594,fixture["source_label"],12)
    for x,state,word in [(28,"dark","DARK / NO SUPPORT"),(228,"lit","LIT / EVIDENCE"),(401,"hatched","HATCHED / SINGLE-SOURCE OR CONTESTED")]:
        out += rect(x,611,17,17,paint(state,prefix),DIRTY)
        out += text(x+24,624,word,11)
    out += text(932,624,"P1 OUTER BAND = FOOTHOLD",11,anchor="end")
    return out + '</svg>\n'


def samples_for(data):
    samples = []
    for family in FAMILIES:
        for fixture in FIXTURES:
            for viewpoint in VIEWPOINTS:
                states = states_for(data,fixture,viewpoint)
                sid = sample_id(family,fixture,viewpoint)
                summary = "; ".join(f"{p} {states[p]}" for p in PROPOSITIONS[:5]) + "."
                summary += f' P1 outer foothold {states["p1_foothold"]}.'
                summary += " Observation islands: " + ", ".join(f"{k} {v}" for k,v in states["observations"].items()) + "."
                if family == "d":
                    summary += " " + data["attributions"][viewpoint]["label"] + "; " + data["attributions"][viewpoint]["qualifier"] + "."
                family_label = data["families"][family]["label"]
                viewpoint_label = data["viewpoints"][viewpoint]["label"]
                presence = {"hint":"is only an unnamed dark hint", "hidden":"has no visual presence in this control; its underlying state is still dark", "acknowledged":"remains dark and unreachable"}[states["p6_presence"]]
                alt = data["alt_template"].format(family=family_label,fixture=data["fixtures"][fixture]["label"],viewpoint=viewpoint_label,summary=summary,presence=presence)
                model = data["state_models"][data["fixtures"][fixture]["models"][viewpoint]]
                samples.append({"id":sid,"family":family,"family_label":family_label,"fixture":fixture,
                                "viewpoint":viewpoint,"viewpoint_label":viewpoint_label,"path":sid+".svg",
                                "alt":alt,"states":states,"source_references":model["sources"],
                                "rationale":model["rationale"],"caption":data["fixtures"][fixture]["captions"][viewpoint],
                                "attribution":data["attributions"][viewpoint] if family == "d" else None})
    return samples


def contact_sheet(label_text, rows, samples, rendered):
    width = 3840
    height = 130+len(rows)*680
    out = f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="sheet-title sheet-desc">'
    out += f'<title id="sheet-title">{escape(label_text)}</title><desc id="sheet-desc">Families A–D are columns. Each labeled row shares one fixture and viewpoint. Full SVG drawings are embedded; no linked images. Story revelations through page 039.</desc>'
    out += rect(0,0,width,height,INK)
    out += text(28,38,label_text.upper(),26,weight="bold")
    out += text(28,66,"DESIGN SAMPLES — NOT ADOPTED / COLUMNS A–D / OPEN AT FULL SIZE FOR LABELS / REVELATIONS THROUGH 039",18)
    for j,(fixture,viewpoint) in enumerate(rows):
        y = 130+j*680
        out += text(28,y-12,f'{fixture.upper()} / {viewpoint.upper()}',20,weight="bold")
        for i,family in enumerate(FAMILIES):
            sid = sample_id(family,fixture,viewpoint)
            content = rendered[sid].decode("utf-8")
            content = content.replace('<svg ',f'<svg x="{i*960}" y="{y}" ',1)
            out += content.strip()
    return (out+'</svg>\n').encode("utf-8")


def build_outputs(data):
    samples = samples_for(data)
    rendered = {s["id"]:render(data,s).encode("utf-8") for s in samples}
    files = {s["path"]:rendered[s["id"]] for s in samples}
    sheets = []
    for viewpoint in VIEWPOINTS:
        for group,fixtures in [("010",("010-hint","010-no-p6")),("016",("016",)),("039",("039-before","039-after"))]:
            name = f'contact-{group}-{viewpoint}.svg'
            title = f'{group} comparison / {data["viewpoints"][viewpoint]["label"]}'
            files[name] = contact_sheet(title,[(f,viewpoint) for f in fixtures],samples,rendered)
            sheets.append({"path":name,"label":title,"rows":[{"fixture":f,"viewpoint":viewpoint} for f in fixtures],"sha256":digest(files[name])})
    sources = {p:digest((ROOT/p).read_bytes()) for p in data["source_paths"]}
    inputs = {"data/knowledge-map-samples.json":digest(DATA.read_bytes()),"scripts/knowledge_maps.py":digest(Path(__file__).read_bytes()),**sources}
    for sample in samples:
        sample["sha256"] = digest(files[sample["path"]])
    manifest = {"version":1,"renderer_version":RENDERER_VERSION,"status":data["status"],"warning":data["warning"],
                "input_hash":digest(encoded(inputs)),"inputs":inputs,"samples":samples,"contact_sheets":sheets,
                "terrain_note":"Registered topology per family. P1 core and foothold are separate; contour paths persist beneath every evidence state.",
                "model_note":data["model_note"]}
    files["manifest.json"] = encoded(manifest)
    return files,manifest


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_data(data):
    require(data["version"] == 1,"Fixture version must be 1")
    require(set(data["families"]) == set(FAMILIES),"Exactly families a–d required")
    require(set(data["fixtures"]) == set(FIXTURES),"Exactly five fixtures required")
    require(set(data["viewpoints"]) == set(VIEWPOINTS),"Exactly two viewpoints required")
    expected = {sample_id(a,b,c) for a in FAMILIES for b in FIXTURES for c in VIEWPOINTS}
    require(len(data["sample_ids"]) == 40 and set(data["sample_ids"]) == expected,"Explicit sample IDs must cover the unique 40-sample matrix")
    require(set(data["propositions"]) == set(PROPOSITIONS),"All six proposition definitions required")
    for p in data["source_paths"]:
        require(not Path(p).is_absolute() and ".." not in Path(p).parts and (ROOT/p).is_file(),f"Missing or unsafe source: {p}")
    for key,model in data["state_models"].items():
        require(set(model["propositions"]) == set(PROPOSITIONS),f"Missing propositions: {key}")
        values = list(model["propositions"].values())+[model["p1_foothold"]]+list(model["observations"].values())
        require(all(s in EVIDENCE_STATES for s in values),f"Invalid evidence state: {key}")
        require(model["propositions"]["P6"] == "dark",f"P6 must never clear: {key}")
        require(set(model["observations"]) == {"response","correction","configuration","weights"},f"Wrong observations: {key}")
        require(model["sources"] and model["rationale"],f"Source references and rationale required: {key}")
        for ref in model["sources"]:
            require(ref.split("#")[0] in data["source_paths"],f"Unhashed source: {ref}")
    for fixture in FIXTURES:
        for viewpoint in VIEWPOINTS:
            state = states_for(data,fixture,viewpoint)
            require(state["p6_presence"] in {"hint","hidden","acknowledged"},"Invalid P6 presence")
            require(state["P3"] == state["P4"] == "dark","Later universal claims must remain unsupported")
            require(state["P1"] == "hatched","P1 core remains contested in all fixtures")
            expected_p2 = "hatched" if viewpoint == "reader" and fixture == "039-before" else "dark"
            require(state["P2"] == expected_p2,f"Unsupported P2 state: {fixture}/{viewpoint}")
            require(state["P5"] == ("hatched" if viewpoint == "reader" else "dark"),"Measurement access leaked between viewpoints")
            require(state["p1_foothold"] == ("dark" if viewpoint == "reader" and fixture == "039-after" else "hatched"),"P1 must lose only its outer foothold at 039")
            obs = state["observations"]
            expected_obs = {"response":"lit","correction":"dark","configuration":"dark","weights":"dark"} if viewpoint == "responders" else {
                "response":"hatched" if fixture.startswith("039") else "dark",
                "correction":"hatched", "configuration":"dark" if fixture.startswith("010") else "hatched",
                "weights":"hatched" if fixture == "039-after" else "dark"}
            require(obs == expected_obs,f"Unsupported observation states: {fixture}/{viewpoint}")
    for viewpoint in VIEWPOINTS:
        hint = states_for(data,"010-hint",viewpoint)
        control = states_for(data,"010-no-p6",viewpoint)
        require(semantic_state(hint) == semantic_state(control),"010 control changes evidence")
        require(hint["p6_presence"] == "hint" and control["p6_presence"] == "hidden","010 hint/control presence mismatch")
    fixed = semantic_state(states_for(data,"010-hint","responders"))
    require(all(semantic_state(states_for(data,f,"responders")) == fixed for f in FIXTURES),"Reader revelations leaked into responders")
    require(data["attributions"]["responders"]["model"] is None,"Do not invent a responder model of another interior")


def parse_svg(content, name):
    root = ET.fromstring(content)
    require(root.tag == f'{{{NS}}}svg',f"Not SVG: {name}")
    require(root.find(f'{{{NS}}}title') is not None and root.find(f'{{{NS}}}desc') is not None,f"Accessible labels missing: {name}")
    ids = [e.attrib["id"] for e in root.iter() if "id" in e.attrib]
    require(len(ids) == len(set(ids)),f"Duplicate SVG IDs: {name}")
    for node in root.iter():
        require(node.tag not in {f'{{{NS}}}image',f'{{{NS}}}script',f'{{{NS}}}foreignObject'},f"Non-standalone or unsafe SVG element: {name}")
        for attr,value in node.attrib.items():
            require(not attr.lower().startswith("on"),f"Event attribute: {name}")
            if attr.endswith("href"):
                require(value.startswith("#") and value[1:] in ids,f"External/broken SVG reference: {name}")
            if value.startswith("url(#"):
                require(value[5:-1] in ids,f"Broken SVG paint/clip reference: {name}")
    return root


def terrain(root):
    return [(e.attrib.get("data-terrain"),e.attrib.get("d")) for e in root.iter() if "data-terrain" in e.attrib]


def check_outputs(data, folder=OUTPUT):
    validate_data(data)
    expected,manifest = build_outputs(data)
    require(folder.is_dir(),f"Missing output directory: {folder}; run generate")
    actual_names = {p.name for p in folder.iterdir() if p.is_file()}
    require(actual_names == set(expected),f"Output inventory mismatch: missing={set(expected)-actual_names}, extra={actual_names-set(expected)}")
    for name,content in expected.items():
        require((folder/name).read_bytes() == content,f"Stale or non-reproducible output: {name}; run generate")
    actual_manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    require(actual_manifest == manifest,"Manifest differs from reproducible inputs")
    roots = {}
    for sample in manifest["samples"]:
        name = sample["path"]
        require(Path(name).name == name and name == sample["id"]+".svg","Unsafe or mismatched sample path")
        root = parse_svg(expected[name],name)
        roots[sample["id"]] = root
        require(root.attrib["viewBox"] == "0 0 960 640",f"Wrong viewBox: {name}")
        visible = " ".join(e.text or "" for e in root.iter(f'{{{NS}}}text'))
        require(sample["viewpoint_label"].upper() in visible and "NOT ADOPTED" in visible,f"Viewpoint/status label missing: {name}")
        require(sample["alt"] == root.find(f'{{{NS}}}desc').text,f"Alt text mismatch: {name}")
        for p in PROPOSITIONS[:5]:
            nodes = [e for e in root.iter() if e.attrib.get("data-region") == p]
            require(len(nodes) == 1 and nodes[0].attrib["data-state"] == sample["states"][p],f"Region state mismatch {p}: {name}")
        footholds = [e for e in root.iter() if e.attrib.get("data-region") == "P1-foothold"]
        require(len(footholds) == 1 and footholds[0].attrib["data-state"] == sample["states"]["p1_foothold"],f"P1 foothold mismatch: {name}")
        p6_nodes = [e for e in root.iter() if e.attrib.get("data-region") == "P6"]
        if sample["fixture"] == "010-no-p6":
            require(not p6_nodes and "P6" not in visible,f"P6 visible in no-P6 control: {name}")
        else:
            require(len(p6_nodes) == (2 if sample["family"] == "d" else 1),f"Missing P6 shape: {name}")
            for node in p6_nodes:
                require(node.attrib["data-state"] == "dark",f"P6 cleared: {name}")
                require(all(e.attrib.get("fill",INK) == INK or e.tag == f'{{{NS}}}text' for e in node.iter()),f"P6 lit or hatched: {name}")
        if sample["fixture"].startswith("010"):
            require("CONFIGURATION" not in visible and "WEIGHTS" not in visible,f"Early hint explains later revelation: {name}")
        if sample["viewpoint"] == "responders":
            require("WEIGHTS ACCOUNT" not in visible and "CONFIGURATION ACCOUNT" not in visible and "SCORER ACCOUNTS" not in visible,f"Responders learned reader-only facts: {name}")
        for key,value in sample["states"]["observations"].items():
            nodes = [e for e in root.iter() if e.attrib.get("data-observation") == key]
            require(len(nodes) == 1 and nodes[0].attrib["data-state"] == value,f"Observation state mismatch {key}: {name}")
        if sample["family"] == "d":
            require("TENTATIVE" in visible and "NOT DIRECT ACCESS" in visible,"Missing nested attribution qualification")
    for family in FAMILIES:
        for viewpoint in VIEWPOINTS:
            before = roots[sample_id(family,"039-before",viewpoint)]
            after = roots[sample_id(family,"039-after",viewpoint)]
            require(terrain(before) == terrain(after),f"Terrain shifted at re-fog: {family}/{viewpoint}")
            for fixture in ("010-hint","016"):
                require(terrain(roots[sample_id(family,fixture,viewpoint)]) == terrain(before),f"Terrain changed across fixtures: {family}/{fixture}")
        for fixture in FIXTURES:
            require(all(s["states"] == states_for(data,fixture,s["viewpoint"]) for s in manifest["samples"] if s["fixture"] == fixture),"Family changed shared fixture semantics")
    for sheet in manifest["contact_sheets"]:
        root = parse_svg(expected[sheet["path"]],sheet["path"])
        embedded = [e for e in root.iter() if "data-sample-id" in e.attrib]
        wanted = [sample_id(f,row["fixture"],row["viewpoint"]) for row in sheet["rows"] for f in FAMILIES]
        require([e.attrib["data-sample-id"] for e in embedded] == wanted,f"Contact-sheet coverage/order mismatch: {sheet['path']}")
    return manifest


class KnowledgeMapTests(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_fixture_contract(self):
        validate_data(self.data)
        self.assertEqual(len(samples_for(self.data)),40)

    def test_reject_p6_evidence(self):
        for state in ("lit","hatched"):
            broken = copy.deepcopy(self.data)
            broken["state_models"]["reader-after"]["propositions"]["P6"] = state
            with self.assertRaises(ValueError):
                validate_data(broken)

    def test_reject_omniscient_responders(self):
        self.data["state_models"]["responders-fixed"]["observations"]["weights"] = "hatched"
        with self.assertRaises(ValueError):
            validate_data(self.data)

    def test_reject_false_pre_reveal_certainty(self):
        self.data["state_models"]["reader-before"]["propositions"]["P2"] = "lit"
        with self.assertRaises(ValueError):
            validate_data(self.data)

    def test_reject_missing_control(self):
        self.data["sample_ids"].pop()
        with self.assertRaises(ValueError):
            validate_data(self.data)

    def test_repeatability(self):
        first,_ = build_outputs(self.data)
        second,_ = build_outputs(self.data)
        self.assertEqual(first,second)

    def test_generated_files(self):
        check_outputs(self.data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("generate","check","test"))
    args = parser.parse_args(argv)
    try:
        if args.command == "test":
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(KnowledgeMapTests))
            return 0 if result.wasSuccessful() else 1
        data = load_data()
        validate_data(data)
        if args.command == "generate":
            files,_ = build_outputs(data)
            OUTPUT.mkdir(parents=True,exist_ok=True)
            for name,content in files.items():
                (OUTPUT/name).write_bytes(content)
        manifest = check_outputs(data)
        print(f'{args.command}: OK — {len(manifest["samples"])} samples, {len(manifest["contact_sheets"])} standalone contact sheets; inputs {manifest["input_hash"]}')
        return 0
    except (ValueError,KeyError,OSError,ET.ParseError) as exc:
        print(f'knowledge maps: {exc}',file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
