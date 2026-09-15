"""Offline fixtures for production_history.py, personal_records.py and the collaboration audit."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest import mock

import edition_detail
import personal_records
import production_history as history

LINE_A = "Claude wrote this sentence into the page script."
LINE_B = "Codex patched in a second line of authored wording."
LINE_C = "Nobody's transcript contains this committed sentence."


def git(root: Path, *args: str, when: str | None = None):
    env = dict(os.environ, GIT_AUTHOR_NAME="Committer", GIT_AUTHOR_EMAIL="c@example.com",
               GIT_COMMITTER_NAME="Committer", GIT_COMMITTER_EMAIL="c@example.com")
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)


def jsonl(path: Path, records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records))


class AttributionFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo = base / "zz-no-consumer"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        page = self.repo / "content/pages/001.md"
        page.parent.mkdir(parents=True)
        page.write_text("# Page 001\n\n## Panel 1\n\n" + LINE_A + "\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "first", when="2026-09-02T12:00:00Z")
        page.write_text(page.read_text() + LINE_B + "\n" + LINE_C + "\n")
        (self.repo / "data.json").write_text(json.dumps({"lettering": [LINE_B], "digest": "a" * 64}, indent=1) + "\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "second", when="2026-09-02T14:00:00Z")
        cwd = str(self.repo)
        self.claude = base / "claude/session-a.jsonl"
        jsonl(self.claude, [
            dict(type="assistant", timestamp="2026-09-02T11:00:00Z", cwd=cwd, sessionId="claude-a", isSidechain=False,
                 message=dict(model="claude-test", content=[dict(type="tool_use", name="Bash", input=dict(
                     command=f"cat > content/pages/001.md <<'EOF'\n## Panel 1\n\n{LINE_A}\nEOF")) ])),
            # After the commit that contains LINE_A: must not claim it.
            dict(type="assistant", timestamp="2026-09-02T12:30:00Z", cwd=cwd, sessionId="claude-a", isSidechain=False,
                 message=dict(model="claude-test", content=[dict(type="tool_use", name="Edit", input=dict(
                     file_path=cwd + "/content/pages/001.md", old_string=LINE_C, new_string="short")) ])),
        ])
        self.codex = base / "codex/rollout-b.jsonl"
        patch = f"*** Begin Patch\n*** Update File: {cwd}/content/pages/001.md\n@@\n {LINE_A}\n+{LINE_B}\n-{LINE_A}\n*** End Patch"
        jsonl(self.codex, [
            dict(type="session_meta", timestamp="2026-09-02T12:05:00Z", payload=dict(id="codex-b", cwd=cwd)),
            dict(type="turn_context", timestamp="2026-09-02T12:05:01Z", payload=dict(model="gpt-test", cwd=cwd)),
            dict(type="response_item", timestamp="2026-09-02T13:00:00Z", payload=dict(
                type="custom_tool_call", name="exec", input="tools.apply_patch(" + json.dumps(patch) + ")")),
            dict(type="response_item", timestamp="2026-09-02T13:10:00Z", payload=dict(
                type="custom_tool_call", name="exec", input=json.dumps(
                    "python3 - <<'PY'\nimport json\nopen('data.json','w').write(json.dumps({\"lettering\": [\"" + LINE_B + "\"]}))\nPY"))),
        ])
        self.root = mock.patch.object(history, "ROOT", self.repo)
        self.root.start()

    def tearDown(self):
        self.root.stop()
        self.tmp.cleanup()

    def run_attribution(self):
        return history.attribute([f"test-mac:{self.claude.parent}", f"test-mac:{self.codex.parent}"],
                                 ["content", "data.json"], ["zz-no-consumer"])

    def test_lines_go_to_the_session_that_typed_them_inside_the_window(self):
        result = self.run_attribution()
        first, second = result["commits"]
        page = second["files"]["content/pages/001.md"]
        self.assertEqual(first["files"]["content/pages/001.md"]["matched"], {"test-mac:Claude:claude-a": 1})
        self.assertEqual(page["matched"], {"test-mac:Codex:codex-b": 1})
        self.assertEqual(page["unmatched"], 1)                       # LINE_C: only an old_string
        self.assertIn("test-mac:Claude:claude-a", page["edit_sessions"])
        data = second["files"]["data.json"]
        self.assertEqual(data["considered"], 1)                      # the digest is not wording
        self.assertEqual(data["matched"], {"test-mac:Codex:codex-b": 1})
        self.assertEqual(result["sessions"]["test-mac:Codex:codex-b"]["models"], ["gpt-test"])

    def test_earliest_supplier_wins_and_rivals_are_counted(self):
        result = self.run_attribution()
        hits = [h for k, h in result["lines"].items() if k.endswith("data.json:3")]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["time"], "2026-09-02T13:00:00.000Z")
        self.assertEqual(hits[0]["rivals"], 1)

    def test_patch_removals_and_context_are_not_authorship(self):
        found = history.fragments(f"*** Begin Patch\n@@\n {LINE_A}\n-{LINE_C}\n+{LINE_B}\n*** End Patch")
        self.assertEqual(found, {LINE_B})

    def test_blockquote_marker_is_not_wording(self):
        # A script that appends "\n> " + caption supplies the caption without its marker.
        found = history.fragments("additions = {('052', 4): ('inference', '" + LINE_B + "')}")
        self.assertIn(history.committed_value("content/pages/052.md", "> " + LINE_B), found)
        self.assertEqual(history.committed_value("content/pages/052.md", ">"), None)
        # A short caption stays matchable in its quoted form rather than dropping below the threshold.
        short = "> DIFFERENT TARGETS."
        self.assertIn(history.committed_value("content/pages/006.md", short), history.fragments(f"cat > page.md <<'EOF'\n{short}\nEOF"))

    def test_panel_origins_read_the_blame_at_a_commit(self):
        result = self.run_attribution()
        with mock.patch.object(history, "VAULT", Path(self.tmp.name) / "vault"):
            origins = history.panel_origins(result, "001-01", "HEAD")
            actors = history.panel_actors(result, "001-01", "HEAD")
        self.assertEqual(sum(o["unmatched"] for o in origins), 1)
        self.assertEqual(actors, {"Claude": 1, "Codex": 1})

    def test_other_projects_are_ignored(self):
        other = Path(self.tmp.name) / "other/rollout.jsonl"
        jsonl(other, [dict(type="session_meta", timestamp="2026-09-02T12:00:00Z",
                           payload=dict(id="x", cwd="/elsewhere/zz-no-consumer-notes"))])
        self.assertIsNone(history.transcript_events(other, "m", ["zz-no-consumer"]))


class BundleFixture(unittest.TestCase):
    def build(self, tamper=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        transcript = b'{"type": "user"}\n'
        inventory = [dict(path="/Users/curt/.claude/projects/p/s.jsonl", file_sha256=hashlib.sha256(transcript).hexdigest())]
        files = {"other-mac/messages-zz-no-consumer.json": json.dumps(inventory).encode(),
                 "other-mac/sources/.claude/projects/p/s.jsonl": transcript}
        sums = "".join(f"{hashlib.sha256(body).hexdigest()}  {name.removeprefix('other-mac/')}\n" for name, body in files.items())
        files["other-mac/SHA256SUMS"] = sums.encode()
        if tamper:   # bytes change in transit, after the checksums were written
            files["other-mac/sources/.claude/projects/p/s.jsonl"] = transcript + b"x"
        archive = Path(tmp.name) / "bundle.tar"
        with tarfile.open(archive, "w") as tar:
            for name, body in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(body)
                tar.addfile(info, io.BytesIO(body))
        return archive

    def test_verified_bundle_passes(self):
        with mock.patch("sys.stdout", io.StringIO()) as out:
            history.verify_bundle(self.build(), extract=False)
        self.assertIn("verified", out.getvalue())

    def test_changed_bytes_are_caught(self):
        with mock.patch("sys.stdout", io.StringIO()), self.assertRaisesRegex(ValueError, "hash mismatch"):
            history.verify_bundle(self.build(tamper=True), extract=False)


class PersonalRecordsFixture(unittest.TestCase):
    def write(self, name, body):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / name
        path.write_text(body)
        return path

    def test_exports_yield_dated_locators_without_bodies(self):
        start, end = personal_records.from_iso("2026-07-01T00:00:00Z"), personal_records.from_iso("2026-09-02T00:00:00Z")
        watch = self.write("watch-history.json", json.dumps([
            dict(header="YouTube", title="Watched Black Hat talk", titleUrl="https://www.youtube.com/watch?v=87DyyMV0kCY",
                 time="2026-08-06T15:00:00.000Z"),
            dict(header="YouTube", title="Watched a geometry lesson", titleUrl="https://www.youtube.com/watch?v=zzz",
                 time="2026-08-07T15:00:00.000Z")]))
        tweets = self.write("tweets.js", "window.YTD.tweets.part0 = " + json.dumps([dict(tweet=dict(
            id_str="2079658951264920020", created_at="Wed Jul 22 04:20:00 +0000 2026",
            full_text="Private words about Hugging Face"))]))
        chatgpt = self.write("conversations.json", json.dumps([dict(title="t", mapping={"n": dict(message=dict(
            author=dict(role="user"), create_time=1785700000, content=dict(parts=["what did METR find?"]),
            metadata={}))})]))
        result = personal_records.inventory([watch, tweets, chatgpt], start, end, personal_records.TERMS, personal_records.URLS)
        self.assertEqual([r["kind"] for r in result["rows"]], ["x-post", "chatgpt-message", "youtube-watch"])
        self.assertEqual(result["files"][0]["unmatched"], 1)         # "geometry" is not METR
        self.assertNotIn("Private words", json.dumps(result))
        self.assertNotIn("what did METR find", json.dumps(result))

    def test_like_time_is_only_a_lower_bound(self):
        created = personal_records.snowflake_time("2079658951264920020")
        self.assertEqual(created.year, 2026)


class AuditFixture(unittest.TestCase):
    def test_parked_analysis_and_backwards_beats_are_reported(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "manuscript").mkdir()
        sha = "b" * 64
        (root / "production-selections.json").write_text(json.dumps([dict(record_sha256=sha, actor="Codex",
                                                                          utc="2026-09-06T15:02:31.590Z")]))
        beat = lambda i, t: dict(id=f"beat-{i}", time_start=t, time_end=t, old_panels=[],
                                 sources=[dict(key="PROD-" + sha[:12])])
        scene = dict(id="parked", movement="collaboration", owner="Claude",
                     chronology_basis="Narrator examines the draft.", source_limit="",
                     beats=[beat(i, "2026-09-06T15:02:31.590Z") for i in range(4)] + [beat(9, "2026-09-06T15:00:00Z")])
        (root / "manuscript/fixture.json").write_text(json.dumps([scene]))
        findings = edition_detail.audit(root)
        self.assertEqual(len(findings["instant"]), 1)
        self.assertEqual(len(findings["narrator"]), 1)
        self.assertEqual(len(findings["order"]), 1)
        self.assertEqual(len(findings["no-owner-record"]), 5)       # the cited record is Codex's


if __name__ == "__main__":
    unittest.main()
