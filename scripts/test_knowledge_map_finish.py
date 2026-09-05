import contextlib
import io
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import knowledge_map_finish as finish


PNG = b"\x89PNG\r\n\x1a\n" + b"test-init-raster"
WEBP = b"RIFF\x10\x00\x00\x00WEBPtest-finish-image"


class FinishStudyTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.out = self.root / "local-v2"
        for target, value in (("ROOT", self.root), ("OUT", self.out)):
            scoped = patch.object(finish, target, value)
            scoped.start()
            self.addCleanup(scoped.stop)
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)

    def fake_rasterize(self, svg, png):
        Path(png).write_bytes(PNG)
        return PNG

    def fake_finish(self, provider, prompt, init_png, output):
        self.assertTrue(Path(init_png).is_file())
        self.assertIn("Do not move, add, remove", prompt)
        Path(output).write_bytes(WEBP)
        return WEBP

    def generate(self):
        with patch.object(finish.localgen, "unified_memory_gb", return_value=16), \
                patch.object(finish.localgen, "chip", return_value="test"), \
                patch.object(finish, "rasterizer_version", return_value="test-rasterizer"), \
                patch.object(finish, "rasterize", side_effect=self.fake_rasterize) as raster, \
                patch.object(finish, "finish", side_effect=self.fake_finish) as command, \
                patch.object(finish.imagegen, "log_generation") as log, \
                contextlib.redirect_stdout(io.StringIO()):
            finish.generate()
            return raster, command, log

    def test_generates_all_forty_from_v1_and_resumes_without_calls(self):
        raster, command, log = self.generate()
        self.assertEqual(command.call_count, 40)
        self.assertEqual(raster.call_count, 40)
        self.assertEqual(log.call_count, 40)
        self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
        manifest = finish.check(self.out)
        self.assertEqual(len(manifest["results"]), 40)
        self.assertEqual({row["id"] for row in manifest["results"]}, {s["id"] for s in finish.v1_samples()})
        self.assertEqual(sorted(p.name for p in self.out.glob("*.txt")), ["a.txt", "b.txt", "c.txt", "d.txt"])
        self.assertEqual(len(list(self.out.glob("*-init.svg"))), 40)
        raster, command, log = self.generate()
        command.assert_not_called()
        log.assert_not_called()

    def test_init_is_unlettered_and_keeps_terrain(self):
        self.generate()
        init = (self.out / "a-039-after-reader-init.svg").read_bytes()
        self.assertNotIn(b"<text", init)
        self.assertNotIn(b"<metadata", init)
        self.assertIn(b'data-terrain="P2"', init)
        self.assertIn(b'data-state="dark"', init)
        self.assertIn(b"<pattern", init)
        self.assertIn(b'stroke-width="2.4"', init)
        self.assertIn(b"M2.5,11 L11,2.5", init)
        self.assertIn(b'data-init-for="a-039-after-reader"', init)

    def test_detects_changed_image_and_changed_init(self):
        self.generate()
        (self.out / "b-016-reader.webp").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "not a WebP"):
            finish.check(self.out)
        (self.out / "b-016-reader.webp").write_bytes(WEBP)
        (self.out / "b-016-reader-init.svg").write_bytes(b"<svg/>")
        with self.assertRaisesRegex(ValueError, "unlettered form"):
            finish.check(self.out)

    def test_detects_stale_v1_source(self):
        self.generate()
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["results"][3]["source_sha256"] = "0" * 64
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "different v1 drawing"):
            finish.check(self.out)

    def test_rejects_incomplete_manifest_and_changed_settings(self):
        self.generate()
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["results"].pop()
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "all 40"):
            finish.check(self.out)
        self.assertEqual(len(finish.check(self.out, complete=False)["results"]), 39)
        manifest["strength"] = 0.99
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "settings differ"):
            finish.check(self.out, complete=False)

    def test_rejects_path_escape(self):
        self.generate()
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["results"][0]["path"] = "../a-010-reader-hint.webp"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unexpected finish asset path"):
            finish.check(self.out)

    def test_never_calls_a_hosted_provider(self):
        hosted = replace(finish.imagegen.PROVIDERS_BY_ID[finish.MODEL], build="openai")
        with patch.dict(finish.imagegen.PROVIDERS_BY_ID, {finish.MODEL: hosted}), \
                patch.object(finish, "finish") as command:
            with self.assertRaisesRegex(ValueError, "local model"):
                finish.generate()
            command.assert_not_called()

    def test_rejects_noncommercial_model(self):
        restricted = replace(finish.imagegen.PROVIDERS_BY_ID[finish.MODEL], commercial=False)
        with patch.dict(finish.imagegen.PROVIDERS_BY_ID, {finish.MODEL: restricted}):
            with self.assertRaisesRegex(ValueError, "commercially usable"):
                finish.generate()

    def test_prompts_fit_the_model_budget(self):
        budget = finish.imagegen.PROVIDERS_BY_ID[finish.MODEL].prompt_tokens
        for family in finish.FAMILIES:
            tokens = finish.imagegen._token_pieces(finish.prompt_for(family)) + finish.imagegen.PROMPT_OVERHEAD
            self.assertLessEqual(tokens, budget, family)
            self.assertIn("words", finish.prompt_for(family))


if __name__ == "__main__":
    unittest.main()
