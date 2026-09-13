"""Offline regression fixtures for the isolated edition boundary; no live writes."""
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import tempfile

import collaboration_records
import edition_detail
import working_edition as edition


def fixture():
    events = []
    windows = []
    for i, (movement, owner) in enumerate((("incident", "HuggingFace"), ("collaboration", "Curt"))):
        clock = f"2026-07-21T00:00:0{i}Z"
        end = "2026-07-21T00:00:01Z"
        events.append(dict(id=f"event-{i}", movement=movement, owner=owner, subject=owner,
                           start=clock, end=end, precision="second", original_timezone="UTC",
                           uncertainty="Fixture record with a known interval.", purpose="Fixture action",
                           frame="A source record.", caption="Reconstructed fixture scene.",
                           evidence_status="reconstructed" if i else "documented",
                           sources=[dict(key="SOURCE", available="2026-07-20", locator="fixture")],
                           old_panels=["001-01"] if i == 0 else [], exact_strings=[]))
        windows.append(dict(id=f"window-{i}", title="Fixture", chapter=movement, movement=movement,
                            start=clock, end=end, purpose="A fixture", rows=[
                                dict(owner=row, slots=[f"event-{i}" if row == owner else None, None])
                                for row in edition.ROWS[movement]]))
    return {"ledger": events, "windows": windows, "sources": {"SOURCE": {}},
            "baseline": {"frozen_files": {}}, "old-panels": [
                {"panel": "001-01", "edition": "legacy-fixture", "exact_strings": []}],
            "dispositions": {"001-01": dict(disposition="retain", events=["event-0"], reason="Retained action")},
            "readiness": {"pending": []}}


def run():
    good = fixture()
    assert not edition.validate(good), edition.validate(good)
    mutations = [
        (lambda m: m["windows"][1]["rows"].reverse(), "row order"),
        (lambda m: m["windows"][0]["rows"][0]["slots"].append("event-0"), "exactly once"),
        (lambda m: m["ledger"][0].update(end="2026-07-22"), "outside page clock"),
        (lambda m: m["ledger"][1]["sources"][0].update(available="2026-07-22"), "later knowledge"),
        (lambda m: m["ledger"][1].update(caption="A scene without its disclosure."), "invisible reconstruction"),
        (lambda m: m["dispositions"]["001-01"].update(events=[]), "reciprocal"),
        (lambda m: m["readiness"].update(pending=["Missing source Mac"]), "incomplete"),
        (lambda m: m["windows"].append(copy.deepcopy(m["windows"][0])), "transition"),
        (lambda m: m["old-panels"][0].update(exact_strings=[{"text": "Original wording"}]), "registration lost"),
    ]
    for change, expected in mutations:
        model = copy.deepcopy(good)
        change(model)
        assert any(expected in error for error in edition.validate(model)), expected
    generated = edition.outputs(good)
    assert generated == edition.outputs(good), "nondeterministic output"
    manifest = json.loads(generated["manifest.json"])
    assert sum(s["empty"] for p in manifest for s in p["slots"]) == 10
    assert all(s["panel"] is None and s["art_status"] == "not-applicable"
               for p in manifest for s in p["slots"] if s["empty"])
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for name, data in good.items():
            (root / (name + ".json")).write_text(edition.dump(data))
        before = {p.name: p.read_bytes() for p in root.iterdir()}
        with redirect_stdout(io.StringIO()):
            edition.migrate(root)
        assert before == {p.name: p.read_bytes() for p in root.iterdir()}, "dry run wrote files"
        with redirect_stdout(io.StringIO()):
            edition.migrate(root, True)
            edition.check(root, fixtures=False)
        path = root / "generated/content/pages/001.md"
        path.write_text(path.read_text() + "stale")
        try:
            edition.check(root, fixtures=False)
        except ValueError as error:
            assert "stale" in str(error)
        else:
            raise AssertionError("stale script accepted")
        frozen = root / "frozen.txt"
        frozen.write_text("original")
        model = copy.deepcopy(good)
        model["baseline"]["frozen_files"] = {str(frozen): edition.digest(frozen)}
        frozen.write_text("changed")
        assert edition.frozen_errors(model)
        transcript = root / "transcript.jsonl"
        rows = [dict(type="session_meta", payload={"cwd": "/fixture/book"}),
                dict(type="response_item", timestamp="2026-09-01T12:00:00Z",
                     payload={"type": "message", "role": "assistant", "content": [{"text": "PRIVATE BODY"}]}),
                dict(type="response_item", timestamp="2026-09-01T12:00:01Z",
                     payload={"type": "function_call", "name": "untrusted command"})]
        transcript.write_text("".join(json.dumps(r) + "\n" for r in rows))
        records = collaboration_records.inventory([transcript], "fixture-mac", "book")
        assert len(records) == 1 and records[0]["actor"] == "Codex"
        assert "PRIVATE BODY" not in json.dumps(records)
        assert not collaboration_records.inventory([transcript], "fixture-mac", "other")
    # Scene drafts cannot silently lose their identity, source clock or quotation.
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "manuscript").mkdir()
        (root / "sources.json").write_text(edition.dump({"SOURCE": {"available": "2026-07-20"}}))
        (root / "old-panels.json").write_text(edition.dump(good["old-panels"]))
        beat = dict(id="beat", frame="A recorded message.", lettering=["Original wording"],
                    time_start="2026-07-21", time_end="2026-07-21", old_panels=["001-01"],
                    detail_decisions=[dict(old_panel="001-01", disposition="rewrite", reason="Retain the action")],
                    sources=[dict(key="SOURCE", available="2026-07-20", locator="record")],
                    evidence_status="documented", exact_strings=[dict(text="Original wording", source="SOURCE",
                    locator="record", verification="verbatim", rights="unresolved")])
        scene = dict(id="scene", owner="Curt", movement="collaboration", start="2026-07-21", end="2026-07-21",
                     precision="day", original_timezone="UTC", chronology_basis="Recorded date",
                     source_limit="No delivery time", title="Fixture", beats=[beat])
        path = root / "manuscript/fixture.json"
        path.write_text(edition.dump([scene]))
        assert not edition_detail.manuscript_errors(root)
        with redirect_stdout(io.StringIO()):
            edition_detail.write_manuscript(root)
        assert not edition_detail.check_manuscript(root)
        for change, expected in [
            (lambda s: s["beats"].append(copy.deepcopy(s["beats"][0])), "duplicate"),
            (lambda s: s["beats"][0].update(time_end="2026-07-22"), "outside"),
            (lambda s: s["beats"][0].update(lettering=["Changed words"]), "wording absent"),
            (lambda s: s["beats"][0]["sources"][0].update(available="2026-07-22"), "later evidence"),
            (lambda s: s["beats"][0]["sources"][0].update(key="UNKNOWN"), "unknown source"),
            (lambda s: s["beats"][0].update(old_panels=["999-99"]), "unknown frozen"),
        ]:
            changed = copy.deepcopy(scene)
            change(changed)
            path.write_text(edition.dump([changed]))
            assert any(expected in e for e in edition_detail.manuscript_errors(root)), expected
        path.write_text(edition.dump([scene]))
        (root / "manuscript-review.md").write_text("stale")
        assert any("stale" in e for e in edition_detail.check_manuscript(root))
    print("Working edition regression fixtures passed.")
