#!/usr/bin/env python3
"""Validate the published knowledge-map gallery without rebuilding any assets."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ("010-hint", "010-no-p6", "016", "039-before", "039-after")
VIEWPOINTS = ("reader", "responders")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class GalleryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.references: list[str] = []
        self.images: list[dict[str, str]] = []
        self.figures: list[tuple[dict[str, str], set[str]]] = []
        self.stack: list[tuple[str, str]] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        identity = values.get("id", "")
        if identity:
            if identity in self.ids:
                self.duplicate_ids.add(identity)
            self.ids.add(identity)
        if tag == "figure":
            self.figures.append((values, {identity for _, identity in self.stack if identity}))
        if tag == "img":
            self.images.append(values)
        for key in ("href", "src"):
            if key in values:
                self.references.append(values[key])
        if tag not in VOID_TAGS:
            self.stack.append((tag, identity))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def local_target(site: Path, document: Path, reference: str) -> tuple[Path, str] | None:
    url = urlsplit(reference)
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    target = ((site / path.lstrip("/")) if path.startswith("/") else (document.parent / path)).resolve() if path else document.resolve()
    if not target.is_relative_to(site):
        raise ValueError(f"Reference escapes site root: {reference}")
    if target.is_dir() or path.endswith("/"):
        target /= "index.html"
    return target, unquote(url.fragment)


def validate(site: Path) -> list[str]:
    site = site.resolve()
    failures: list[str] = []
    parsed: dict[Path, GalleryParser] = {}

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    def parse(path: Path) -> GalleryParser:
        path = path.resolve()
        if path not in parsed:
            parser = GalleryParser()
            if path.is_file():
                parser.feed(path.read_text(encoding="utf-8"))
                require(not parser.duplicate_ids, f"{path}: duplicate anchors {sorted(parser.duplicate_ids)}")
            else:
                failures.append(f"Missing gallery route or linked document: {path}")
            parsed[path] = parser
        return parsed[path]

    def asset(folder: str, filename: str, suffix: str) -> Path:
        if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", filename) or not filename.endswith(suffix):
            raise ValueError(f"Invalid asset basename: {filename!r}")
        path = site / "assets" / "knowledge-maps" / folder / filename
        require(path.resolve().is_relative_to(site), f"Asset escapes site root: {path}")
        require(path.is_file() and path.stat().st_size > 0, f"Missing or empty asset: {path}")
        source = ROOT / "assets" / "knowledge-maps" / folder / filename
        if source.is_file() and path.is_file():
            require(source.read_bytes() == path.read_bytes(), f"Published asset differs from source: {path}")
        return path

    home = site / "index.html"
    overview = site / "knowledge-maps" / "index.html"
    version = site / "knowledge-maps" / "v1" / "index.html"
    homepage, index, gallery = (parse(path) for path in (home, overview, version))
    require(any(local_target(site, home, ref) == (overview, "") for ref in homepage.references), "Homepage must link to knowledge-maps/")
    require(any(local_target(site, overview, ref) == (version, "") for ref in index.references), "Gallery index must link to v1/")
    documents = sorted(set((overview, version)) | set((site / "knowledge-maps").rglob("*.html")))
    for document in documents:
        parser = parse(document)
        for reference in parser.references:
            target = local_target(site, document, reference)
            if target is None:
                continue
            path, fragment = target
            require(path.is_file(), f"{document}: broken local link or image {reference}")
            if fragment and path.is_file() and path.suffix == ".html":
                require(fragment in parse(path).ids, f"{document}: missing target anchor {reference}")
        for image in parser.images:
            require(bool(image.get("src", "").strip()), f"{document}: image missing src")
            require(bool(image.get("alt", "").strip()), f"{document}: image missing meaningful alt text")

    manifest_path = asset("v1", "manifest.json", ".json")
    if not manifest_path.is_file():
        return failures
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest["version"] == 1, "Unsupported semantic gallery version")
    require(bool(manifest["renderer_version"]), "Missing renderer version")
    samples = manifest["samples"]
    expected = {(family, fixture, viewpoint) for family in "abcd" for fixture in FIXTURES for viewpoint in VIEWPOINTS}
    require(len(samples) == 40, f"Expected 40 semantic samples, found {len(samples)}")
    require({(item["family"], item["fixture"], item["viewpoint"]) for item in samples} == expected, "Manifest does not cover all four families, five fixtures, and two viewpoints")
    require(len({item["id"] for item in samples}) == 40, "Sample ids are not unique")
    require(len({item["path"] for item in samples}) == 40, "Sample SVG paths are not unique")
    primary = [values for values, _ in gallery.figures if "data-km-sample" in values]
    require(len(primary) == 40, f"Expected 40 primary gallery samples, found {len(primary)}")
    require({values["data-km-sample"] for values in primary} == {item["id"] for item in samples}, "Gallery sample ids do not match the manifest")
    image_targets = {local_target(site, version, image.get("src", ""))[0]: image.get("alt", "") for image in gallery.images if local_target(site, version, image.get("src", "")) is not None}
    for sample in samples:
        path = asset("v1", sample["path"], ".svg")
        require(bool(sample["alt"].strip()) and isinstance(sample["states"], dict), f"Sample lacks alt or states: {sample['id']}")
        require(image_targets.get(path) == sample["alt"], f"Sample not displayed with manifest alt text: {sample['id']}")
        if path.is_file():
            svg = ET.fromstring(path.read_bytes())
            require(svg.tag == "{http://www.w3.org/2000/svg}svg" and bool(svg.get("viewBox")), f"Sample needs an SVG viewBox: {path}")

    required_anchors = {"controlled-comparison", "039-before-after", "010-hint-nohint", "reader-responders", "placements", "contact-sheets"}
    for fixture in FIXTURES:
        for viewpoint in VIEWPOINTS:
            anchor = f"compare-{fixture}-{viewpoint}"
            required_anchors.add(anchor)
            row = [values for values, ancestors in gallery.figures if anchor in ancestors]
            require(len(row) == 4 and {values.get("data-family") for values in row} == set("abcd") and all(values.get("data-fixture") == fixture and values.get("data-viewpoint") == viewpoint for values in row), f"Comparison row must hold fixture/viewpoint fixed across all families: {anchor}")
    for anchor, fixtures in (("039-before-after", ("039-before", "039-after")), ("010-hint-nohint", ("010-hint", "010-no-p6")), ("reader-responders", FIXTURES)):
        figures = [values for values, ancestors in gallery.figures if anchor in ancestors]
        keys = {(item.get("data-family"), item.get("data-fixture"), item.get("data-viewpoint")) for item in figures}
        pairs = {(family, fixture, viewpoint) for family in "abcd" for fixture in fixtures for viewpoint in VIEWPOINTS}
        require(len(figures) == len(pairs) and keys == pairs, f"Missing paired comparison coverage: {anchor}")
    for placement in ("margin", "gutter", "chapter-opening"):
        required_anchors.add(f"placement-{placement}")
        figures = [values for values, _ in gallery.figures if values.get("data-placement") == placement]
        require(len(figures) == 4 and {values.get("data-family") for values in figures} == set("abcd"), f"Placement needs all four alternatives: {placement}")
        required_anchors.update(f"placement-{placement}-{family}" for family in "abcd")
    require(required_anchors <= gallery.ids, f"Missing gallery anchors: {sorted(required_anchors - gallery.ids)}")
    require(bool(manifest["contact_sheets"]), "Manifest has no contact sheets")
    sheets = [values.get("data-contact-sheet") for values, _ in gallery.figures if "data-contact-sheet" in values]
    require(sorted(sheets) == sorted(sheet["path"] for sheet in manifest["contact_sheets"]), "Displayed contact sheets differ from manifest")
    for sheet in manifest["contact_sheets"]:
        path = asset("v1", sheet["path"], ".svg")
        require(bool(sheet["label"].strip()) and image_targets.get(path) == sheet["label"], f"Missing contact-sheet image or alt: {path}")
        if path.is_file():
            require(ET.fromstring(path.read_bytes()).tag == "{http://www.w3.org/2000/svg}svg", f"Contact sheet is not SVG: {path}")

    local_source = ROOT / "assets" / "knowledge-maps" / "local-v1" / "manifest.json"
    local_path = site / "assets" / "knowledge-maps" / "local-v1" / "manifest.json"
    if local_source.exists() or local_path.exists():
        local_path = asset("local-v1", "manifest.json", ".json")
        if local_path.is_file():
            local = json.loads(local_path.read_text(encoding="utf-8"))
            require(bool(local["model"].strip()) and bool(local["licence"].strip()), "Local studies need model and licence labels")
            require(len(local["results"]) == 4 and {item["id"] for item in local["results"]} == set("abcd"), "Expected four actual local model studies")
            for document, parser in ((overview, index), (version, gallery)):
                studies = [values["data-local-study"] for values, _ in parser.figures if "data-local-study" in values]
                require(sorted(studies) == list("abcd"), f"{document}: missing local model studies")
                text = " ".join(parser.text).lower()
                require("local model concept studies" in text and "exploratory" in text and "not exact evidence states" in text, f"{document}: missing exploratory model disclosure")
                references = {local_target(site, document, image.get("src", "")) for image in parser.images}
                for result in local["results"]:
                    image = asset("local-v1", result["path"], ".webp")
                    asset("local-v1", result["prompt"], ".txt")
                    require((image, "") in references, f"{document}: local image not displayed: {image}")
                    require(isinstance(result["seed"], int) and result["width"] > 0 and result["height"] > 0 and result["seconds"] >= 0, f"Invalid local generation metadata: {result['id']}")
                    if image.is_file():
                        signature = image.read_bytes()[:12]
                        require(signature[:4] == b"RIFF" and signature[8:12] == b"WEBP", f"Local study is not a WebP raster: {image}")
    else:
        require(not any("data-local-study" in values for parser in (index, gallery) for values, _ in parser.figures), "Gallery claims local model outputs without a manifest")

    finish_source = ROOT / "assets" / "knowledge-maps" / "local-v2" / "manifest.json"
    finish_path = site / "assets" / "knowledge-maps" / "local-v2" / "manifest.json"
    if finish_source.exists() or finish_path.exists():
        finish_path = asset("local-v2", "manifest.json", ".json")
        if finish_path.is_file():
            finish = json.loads(finish_path.read_text(encoding="utf-8"))
            require(finish["version"] == 2 and bool(finish["model"].strip()) and bool(finish["licence"].strip()), "Finish studies need version 2, model and licence labels")
            require(0 < float(finish["strength"]) < 1 and int(finish["steps"]) > 0 and isinstance(finish["seed"], int), "Finish studies need image-to-image settings")
            results = {row["id"]: row for row in finish["results"]}
            require(len(finish["results"]) == 40 and set(results) == {item["id"] for item in samples}, "Expected one finish study per semantic sample")
            by_id = {item["id"]: item for item in samples}
            for document, parser, expected_count in ((overview, index, 4), (version, gallery, 40)):
                figures = [values for values, _ in parser.figures if "data-local-finish" in values]
                shown = {values["data-local-finish"] for values in figures}
                require(len(figures) == expected_count and len(shown) == expected_count and shown <= set(results), f"{document}: expected {expected_count} finish studies")
                if expected_count == 4:
                    require({values.get("data-family") for values in figures} == set("abcd"), f"{document}: finish overview needs one study per family")
                text = " ".join(parser.text).lower()
                require("local model finish studies" in text and "structure-preserving" in text and "not exact evidence states" in text and "not adopted" in text, f"{document}: missing finish-study disclosure")
                references = {local_target(site, document, image.get("src", "")) for image in parser.images}
                links = {local_target(site, document, reference) for reference in parser.references}
                for values in figures:
                    row = results[values["data-local-finish"]]
                    sample = by_id[row["id"]]
                    require((values.get("data-family"), values.get("data-fixture"), values.get("data-viewpoint")) == (sample["family"], sample["fixture"], sample["viewpoint"]) == (row["family"], row["fixture"], row["viewpoint"]), f"{document}: finish study metadata drifted: {row['id']}")
                    image = asset("local-v2", row["path"], ".webp")
                    require((image, "") in references, f"{document}: finish image not displayed: {image}")
                    require((asset("local-v2", row["init"], ".svg"), "") in links and (asset("local-v2", row["prompt"], ".txt"), "") in links, f"{document}: finish study must link its init drawing and prompt: {row['id']}")
                    require(row["source_sha256"] == sample["sha256"], f"Finish study was made from a different v1 drawing: {row['id']}")
                    if image.is_file():
                        signature = image.read_bytes()[:12]
                        require(signature[:4] == b"RIFF" and signature[8:12] == b"WEBP", f"Finish study is not a WebP raster: {image}")
            for document, parser in ((overview, index), (version, gallery)):
                for image in parser.images:
                    target = local_target(site, document, image.get("src", ""))
                    if target and target[0].parent.name == "local-v2":
                        require("unlettered" in image.get("alt", "").lower(), f"{document}: finish image alt must say it is unlettered")
            require("local-model-finish-studies" in gallery.ids and "local-model-finish-studies" in index.ids, "Finish studies need a stable anchor on both gallery pages")
            for fixture in FIXTURES:
                for viewpoint in VIEWPOINTS:
                    anchor = f"finish-{fixture}-{viewpoint}"
                    row = [values for values, ancestors in gallery.figures if anchor in ancestors]
                    require(anchor in gallery.ids and len(row) == 4 and {values.get("data-family") for values in row} == set("abcd") and all(values.get("data-fixture") == fixture and values.get("data-viewpoint") == viewpoint for values in row), f"Finish row must hold fixture/viewpoint fixed across all families: {anchor}")
    else:
        require(not any("data-local-finish" in values for parser in (index, gallery) for values, _ in parser.figures), "Gallery claims finish studies without a manifest")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=ROOT / "docs", help="generated site root (default: docs)")
    args = parser.parse_args()
    try:
        failures = validate(args.site)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        failures = [f"Invalid or unreadable gallery: {error}"]
    if failures:
        print("Knowledge-map gallery validation failed:")
        for failure in failures[:50]:
            print(f"- {failure}")
        if len(failures) > 50:
            print(f"- …and {len(failures) - 50} more")
        return 1
    print("Validated knowledge-map gallery routes, local links, 40 samples, contact sheets, paired comparisons, placements, homepage discovery, and available local model studies.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
