"""Detailed, page-independent rewrite inventory over the existing panel model.

This does not allocate new pages or claim that extracted fields are fully decomposed
events. Each frame, action and lettering element must receive individual editorial
disposition before a condensed event can be called its complete replacement.
"""
import json
from pathlib import Path

import panels


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
