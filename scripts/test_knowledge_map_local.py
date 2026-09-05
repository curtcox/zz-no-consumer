import contextlib
import io
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import knowledge_map_local as maps


class LocalConceptTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.out = self.root / "concepts"
        for target, value in (("ROOT", self.root), ("OUT", self.out)):
            scoped = patch.object(maps, target, value)
            scoped.start()
            self.addCleanup(scoped.stop)
        env = patch.dict(os.environ)
        env.start()
        self.addCleanup(env.stop)
        self.mock_image = maps.imagegen.Generated(b"RIFF\x10\x00\x00\x00WEBPtest-local-image", ".webp")

    def generate(self):
        with patch.object(maps.localgen, "unified_memory_gb", return_value=16), \
                patch.object(maps.localgen, "chip", return_value="test"), \
                patch.object(maps.imagegen, "generate_command", return_value=self.mock_image) as command, \
                patch.object(maps.imagegen, "log_generation") as log, \
                contextlib.redirect_stdout(io.StringIO()):
            maps.generate()
            return command, log

    def test_generates_four_local_images_and_resumes_without_calls(self):
        command, log = self.generate()
        self.assertEqual(command.call_count, 4)
        self.assertEqual(log.call_count, 4)
        self.assertEqual(os.environ["HF_HUB_OFFLINE"], "1")
        self.assertEqual(os.environ["TRANSFORMERS_OFFLINE"], "1")
        self.assertEqual(len(maps.check()["results"]), 4)
        command, log = self.generate()
        command.assert_not_called()
        log.assert_not_called()

    def test_detects_changed_image(self):
        self.generate()
        (self.out / "a.webp").write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "not a WebP"):
            maps.check()

    def test_rejects_incomplete_manifest(self):
        self.generate()
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["results"].pop()
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "all four"):
            maps.check()
        self.assertEqual(len(maps.check(complete=False)["results"]), 3)

    def test_rejects_path_escape(self):
        self.generate()
        path = self.out / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["results"][0]["path"] = "../a.webp"
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "Unexpected concept asset path"):
            maps.check()

    def test_never_calls_a_hosted_provider(self):
        hosted = replace(maps.imagegen.PROVIDERS_BY_ID[maps.MODEL], build="openai")
        with patch.dict(maps.imagegen.PROVIDERS_BY_ID, {maps.MODEL: hosted}), \
                patch.object(maps.imagegen, "generate_command") as command:
            with self.assertRaisesRegex(ValueError, "local model"):
                maps.generate()
            command.assert_not_called()

    def test_rejects_noncommercial_model(self):
        restricted = replace(maps.imagegen.PROVIDERS_BY_ID[maps.MODEL], commercial=False)
        with patch.dict(maps.imagegen.PROVIDERS_BY_ID, {maps.MODEL: restricted}):
            with self.assertRaisesRegex(ValueError, "commercially usable"):
                maps.generate()

    def test_rejects_oversized_model(self):
        with patch.object(maps.localgen, "unified_memory_gb", return_value=8):
            with self.assertRaisesRegex(ValueError, "memory budget"):
                maps.generate()


if __name__ == "__main__":
    unittest.main()
