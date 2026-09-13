"""Detailed, page-independent rewrite inventory over the existing panel model.

This does not allocate new pages or claim that extracted fields are fully decomposed
events. Each frame, action and lettering element must receive individual editorial
disposition before a condensed event can be called its complete replacement.
"""
from collections import Counter
import json
import hashlib
from pathlib import Path
import re

import panels
import crossref


def manuscript(root):
    """Load authored sequences, without allocating or parsing page identities."""
    return [scene for path in sorted((root / "manuscript").glob("*.json"))
            for scene in json.loads(path.read_text())]


def beat_digest(beat):
    return hashlib.sha256(json.dumps(beat, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def detail_reviews(root):
    path = root / "detail-review.json"
    return json.loads(path.read_text()) if path.exists() else []


def review_errors(root):
    reviews = detail_reviews(root)
    if not reviews:
        return []
    inventory = {r["old_panel"]: r for r in json.loads((root / "detail-inventory.json").read_text()) if r.get("old_panel")}
    beats = {b["id"]: b for s in manuscript(root) for b in s["beats"]}
    errors, seen = [], set()
    for review in reviews:
        key = review["old_panel"]
        if key in seen or key not in inventory:
            errors.append(f"{key}: duplicate or unknown detail review")
            continue
        seen.add(key)
        original = inventory[key]
        elements = {e["id"]: e for e in original["elements"]}
        ids = [e["id"] for e in review["elements"]]
        if set(ids) != set(elements) or len(ids) != len(set(ids)):
            errors.append(f"{key}: detail review must disposition every source element exactly once")
        if review["old_edition"] != original["old_edition"]:
            errors.append(f"{key}: wrong frozen edition")
        for decision in review["elements"]:
            eid = decision["id"]
            if eid not in elements:
                continue
            checksum = hashlib.sha256(elements[eid]["original"].encode()).hexdigest()
            if checksum != decision["original_sha256"]:
                errors.append(f"{eid}: source wording changed since review")
            disposition = decision["disposition"]
            targets = decision["beats"]
            if not decision["reason"] or disposition not in {"retain", "rewrite", "combine", "split", "omit"}:
                errors.append(f"{eid}: missing editorial disposition or reason")
            if (disposition == "omit") != (not targets):
                errors.append(f"{eid}: omissions have no destinations; retained detail needs a destination")
            if set(decision.get("target_sha256", {})) != set(targets):
                errors.append(f"{eid}: missing reviewed destination hashes")
            for target in targets:
                if target not in beats or key not in beats[target]["old_panels"]:
                    errors.append(f"{eid}: unknown or unassociated destination {target}")
                elif decision.get("target_sha256", {}).get(target) != beat_digest(beats[target]):
                    errors.append(f"{eid}: destination changed since detail review")
    return errors


def manuscript_errors(root):
    from working_edition import ROWS, bound
    sources = json.loads((root / "sources.json").read_text())
    old = {r["panel"]: r for r in json.loads((root / "old-panels.json").read_text())}
    errors, ids = [], set()
    for scene in manuscript(root):
        sid = scene["id"]
        if sid in ids:
            errors.append(f"duplicate manuscript identity: {sid}")
        ids.add(sid)
        if scene["owner"] not in ROWS.get(scene["movement"], []):
            errors.append(f"{sid}: invalid row owner")
        start, end = bound(scene["start"]), bound(scene["end"], True)
        if start > end or not scene["beats"]:
            errors.append(f"{sid}: reversed interval or empty sequence")
        for field in ("chronology_basis", "source_limit", "original_timezone", "precision"):
            if not scene.get(field):
                errors.append(f"{sid}: missing {field}")
        for beat in scene["beats"]:
            bid = beat["id"]
            if bid in ids:
                errors.append(f"duplicate manuscript identity: {bid}")
            ids.add(bid)
            if not start <= bound(beat["time_start"]) <= bound(beat["time_end"], True) <= end:
                errors.append(f"{bid}: beat outside sequence bounds")
            if not beat["frame"] or not beat["sources"] or not beat["evidence_status"]:
                errors.append(f"{bid}: missing script or provenance")
            if set(beat["old_panels"]) - old.keys():
                errors.append(f"{bid}: unknown frozen panel")
            if {d["old_panel"] for d in beat["detail_decisions"]} != set(beat["old_panels"]):
                errors.append(f"{bid}: rewrite decisions do not cover panel associations")
            for source in beat["sources"]:
                key = source["key"]
                if key not in sources or not source["locator"]:
                    errors.append(f"{bid}: unknown source or empty locator")
                elif source["available"] != sources[key]["available"]:
                    errors.append(f"{bid}: source availability differs from admission")
                if scene["movement"] == "collaboration" and bound(source["available"]) > bound(beat["time_end"], True):
                    errors.append(f"{bid}: later evidence used in earlier collaboration")
            # Registrations remain structured, even before canonical pages exist.
            for registration in beat["exact_strings"]:
                required = set(crossref.REQUIRED_FIELDS)
                if not required <= registration.keys() or ("text" in registration) == ("pointer" in registration):
                    errors.append(f"{bid}: incomplete quotation registration")
                if registration.get("verification") not in crossref.ALLOWED_VERIFICATION or registration.get("rights") not in crossref.ALLOWED_RIGHTS:
                    errors.append(f"{bid}: invalid quotation vocabulary")
                if registration.get("source") not in {s["key"] for s in beat["sources"]}:
                    errors.append(f"{bid}: quotation source missing from beat references")
                if registration.get("text") and registration["text"] not in "\n".join(beat["lettering"]):
                    errors.append(f"{bid}: registered wording absent from lettering")
    return errors + review_errors(root)


def manuscript_outputs(root):
    """Readable scene review and conservative coverage; neither is a page matrix."""
    from working_edition import bound, dump
    scenes = sorted(manuscript(root), key=lambda s: (bound(s["start"]), bound(s["end"], True), s["owner"], s["id"]))
    old = json.loads((root / "old-panels.json").read_text())
    reviews = {r["old_panel"]: r for r in detail_reviews(root)}
    associations = {}
    lines = ["# Detailed scene draft", "", "Generated by `working_edition.py manuscript`; edit `manuscript/*.json`.", "",
             "**Incomplete and unallocated.** These are authored scene drafts, not the withdrawn chronology study or a numbered manuscript. "
             "Sorting uncertain intervals does not establish their internal order. Broad intervals still require reconciliation in the three-row matrix. "
             "No page count is inferred from beat count.", "",
             "Frame directions describe authored visualization. Lettering below is narrator text unless a quotation is explicitly registered. "
             "Source availability dates are not actor encounter dates. Panel associations are candidates, not certification that every source element survives.", ""]
    for scene in scenes:
        lines += [f"## {scene['title']} — {scene['id']}", "",
                  f"**Row:** {scene['owner']} · {scene['movement']}", "",
                  f"**UTC bounds:** {scene['start']} → {scene['end']} · {scene['precision']}", "",
                  f"**Time evidence:** {scene['chronology_basis']}", "",
                  f"**Evidence limit:** {scene['source_limit']}", ""]
        for b in scene["beats"]:
            for key in b["old_panels"]:
                associations.setdefault(key, []).append(b["id"])
            lines += [f"### {b['id']}", "", f"**Frame:** {b['frame']}", "", "**Lettering:**", ""]
            lines += b["lettering"] or ["None."]
            lines += ["", "**Sources:** " + "; ".join(f"{r['key']} — {r['locator']} (available {r['available']})" for r in b["sources"]), "",
                      "**Frozen panel associations:** " + (", ".join(b["old_panels"]) or "New material."), ""]
            if b["exact_strings"]:
                lines += ["**Quotation registrations:**", "", "```json", dump(b["exact_strings"]).rstrip(), "```", ""]
    coverage = dict(status="incomplete; associations are not full-detail dispositions", scenes=len(scenes),
                    drafted_beats=sum(len(s["beats"]) for s in scenes), canonical_pages=None,
                    associated_old_panels=len(associations),
                    old_panels=[dict(old_edition=r["edition"], old_panel=r["panel"],
                                    draft_beats=associations.get(r["panel"], []),
                                    detail_review="elements-reviewed" if r["panel"] in reviews else "pending", exact_strings=r["exact_strings"])
                                for r in old])
    coverage["by_row"] = {owner: sum(len(s["beats"]) for s in scenes if s["owner"] == owner)
                          for owner in ("HuggingFace", "GemStuffer", "Collusion Wiki", "Curt", "Codex", "Claude")}
    coverage["reviewed_old_panels"] = len(reviews)
    coverage["reviewed_source_elements"] = sum(len(r["elements"]) for r in reviews.values())
    files = {"manuscript-review.md": "\n".join(lines), "manuscript-coverage.json": dump(coverage)}
    if reviews:
        elements = {e["id"]: e for r in json.loads((root / "detail-inventory.json").read_text()) for e in r["elements"]}
        review_lines = ["# Source-detail disposition review", "", "Generated from `detail-review.json`. "
                        "These are recorded editorial decisions, not automatic certification of semantic equivalence. "
                        "Unlisted panels remain unreviewed. Source and destination hashes make later changes invalidate the review.", ""]
        for key, review in sorted(reviews.items()):
            review_lines += [f"## {review['old_edition']} · {key}", ""]
            for d in review["elements"]:
                e = elements[d["id"]]
                review_lines += [f"### {d['id']} · {e['kind']}", "", "**Frozen wording:**", "", e["original"], "",
                                 f"**Decision:** {d['disposition']} — {d['reason']}", "",
                                 "**Draft destination:** " + (", ".join(d["beats"]) or "Omitted; original remains frozen."), ""]
        files["detail-review.md"] = "\n".join(review_lines)
    return files


def write_manuscript(root):
    errors = manuscript_errors(root)
    if errors:
        raise ValueError("\n".join(errors))
    outputs = manuscript_outputs(root)
    for name, content in outputs.items():
        (root / name).write_text(content)
    coverage = json.loads(outputs["manuscript-coverage.json"])
    print(f"Detailed draft: {coverage['scenes']} sequences, {coverage['drafted_beats']} beats; no canonical pages allocated.")


def check_manuscript(root):
    if not (root / "manuscript").exists():
        return []
    errors = manuscript_errors(root)
    if not errors:
        for name, content in manuscript_outputs(root).items():
            path = root / name
            if not path.is_file() or path.read_text() != content:
                errors.append("stale manuscript review: " + name)
    return errors


def build(old_panels, chronology):
    result = []
    incident_pages = (set(range(1, 13)) | set(range(16, 31)) | set(range(32, 38)) |
                      set(range(41, 53)) | set(range(55, 63)) | set(range(64, 73)) | {107, 108, 109})
    for record in old_panels:
        key = record["panel"]
        page = int(key[:3])
        section = panels.Section(int(key[4:]), record["body"])
        movement = "incident" if page in incident_pages else "collaboration"
        if page >= 115:
            movement = "retired-coda"
        fields = [("frame", section.field("Frame")), ("action", section.field("Action"))]
        fields += [("lettering", s) for s in panels.visible_text(section.body)]
        elements = [dict(id=f"legacy-{key}-detail-{n:02}", kind=kind, original=text,
                         decomposition="required", event_ids=[], disposition="pending", reason="")
                    for n, (kind, text) in enumerate(fields, 1) if text]
        result.append(dict(id="legacy-" + key, old_edition=record["edition"], old_panel=key,
                           proposed_movement=movement,
                           proposed_owner=("Collusion Wiki" if page in {107, 108, 109} else "HuggingFace") if movement == "incident" else None,
                           owner_status="editorial triage; not an actor or event-time attribution",
                           source_path=record["source_path"], source_sha256=record["source_sha256"],
                           exact_strings=record["exact_strings"], shared_composition=record["grouped"],
                           source_provenance=section.field("Provenance"), source_references=section.field("References"),
                           elements=elements, review_status="unreviewed"))
    # Newly researched material has no old source panel. Preserve its high-level
    # seed and require decomposition as well, rather than treating one row as done.
    for event in chronology:
        if not event["old_panels"]:
            result.append(dict(id="new-" + event["id"], old_edition=None, old_panel=None,
                               proposed_movement=event["movement"], proposed_owner=event["owner"],
                               source_event=event["id"], sources=event["sources"],
                               original_summary=event["caption"], review_status="needs-source-decomposition",
                               elements=[dict(id=event["id"] + "-detail-01", kind="research-seed",
                                              original=event["caption"], decomposition="required",
                                              event_ids=[], disposition="pending", reason="")]))
    return result


def write(root):
    old = json.loads((root / "old-panels.json").read_text())
    chronology = json.loads((root / "ledger.json").read_text())
    records = build(old, chronology)
    path = root / "detail-inventory.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(f"Detailed inventory: {len(old)} old panels, "
          f"{sum(len(r['elements']) for r in records)} source elements; no page allocation.")


def errors(root):
    records = json.loads((root / "detail-inventory.json").read_text())
    expected = build(json.loads((root / "old-panels.json").read_text()),
                     json.loads((root / "ledger.json").read_text()))
    if records != expected:
        return ["stale detail inventory; regenerate from frozen panels and research seeds"]
    return []


NARRATOR = re.compile(r"narrator|no specific read time|no additional reading act", re.IGNORECASE)


def audit(root, attribution=None, baseline=None):
    """Advisory findings for the collaboration rule; none of them blocks a draft check.

    A collaboration beat belongs to the actor performing its central act at that act's time.
    These findings mark beats that do not yet show such an act: analysis parked on an
    unrelated record's clock, no cited record by the row's actor, beats that run backwards
    within a scene, and old wording whose transcript author differs from the row.
    """
    from working_edition import bound
    selections = {"PROD-" + r["record_sha256"][:12]: r
                  for r in json.loads((root / "production-selections.json").read_text())}
    findings = {"order": [], "instant": [], "narrator": [], "no-owner-record": [], "draft-author": []}
    instants = {}
    for scene in manuscript(root):
        times = [bound(b["time_start"]) for b in scene["beats"]]
        for previous, (beat, current) in zip(times, list(zip(scene["beats"], times))[1:]):
            if current < previous:
                findings["order"].append(f"{beat['id']}: starts {beat['time_start']}, before the previous beat in {scene['id']}")
        if scene["movement"] != "collaboration":
            continue
        if NARRATOR.search(scene["chronology_basis"] + " " + scene["source_limit"]):
            findings["narrator"].append(f"{scene['id']} ({scene['owner']}, {len(scene['beats'])} beats): "
                                        "describes narrator analysis rather than the row actor's act")
        for beat in scene["beats"]:
            instants.setdefault((scene["owner"], beat["time_start"], beat["time_end"]), []).append(beat["id"])
            records = [selections[s["key"]] for s in beat["sources"] if s["key"] in selections]
            own = [r for r in records if r["actor"] == scene["owner"]
                   and bound(beat["time_start"]) <= bound(r["utc"]) <= bound(beat["time_end"], True)]
            if not own:
                cited = ", ".join(sorted({f"{r['actor']} {r['utc']}" for r in records})) or "no production record"
                findings["no-owner-record"].append(f"{beat['id']} ({scene['owner']} row): cites {cited}")
            if attribution and beat["old_panels"]:
                import production_history
                actors = Counter()
                for key in beat["old_panels"]:
                    actors += production_history.panel_actors(attribution, key, baseline)
                if actors and scene["owner"] not in actors:
                    findings["draft-author"].append(
                        f"{beat['id']} ({scene['owner']} row): old wording in {', '.join(beat['old_panels'])} was typed by "
                        + ", ".join(f"{actor} ({count} lines)" for actor, count in actors.most_common()))
    for (owner, start, end), beats in sorted(instants.items()):
        if len(beats) > 3:
            findings["instant"].append(f"{owner} {start}: {len(beats)} beats share one instant "
                                       f"({beats[0]} … {beats[-1]})")
    return findings
