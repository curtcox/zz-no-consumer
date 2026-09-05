#!/usr/bin/env python3
"""Structure-preserving local finish studies for the knowledge-map comparison.

The controlled SVG samples in `assets/knowledge-maps/v1/` settle *what* each map
says: which propositions are dark, lit, or hatched for which viewpoint. This
pass tests *finish* on top of that structure without letting a model reinvent
the structure. For every one of the 40 samples it:

  1. strips the lettering and chrome from the SVG, leaving only the terrain,
     evidence fills, contours, silhouettes, and P6 regions, and emboldens the
     hatch pattern so the model keeps reading hatched as hatched rather than
     as pale paper (`<id>-init.svg`);
  2. rasterizes that quiet SVG at the sample's own size with rsvg-convert;
  3. runs the approved offline FLUX.2 [klein] 4B weights image-to-image over
     that raster at a fixed strength, so the region outlines and fills survive
     and the model adds ink, hatching grain, and paper texture (`<id>.webp`).

Because the init image carries the evidence states, before/after pairs stay
registered and the two viewpoints differ only where the fixture says they do.
Nothing here is canonical story art, nothing is lettered, and none of it is
adopted. The prompts forbid text; labels remain the SVGs' job.

    python3 scripts/knowledge_map_finish.py generate   # resume or start the 40 images
    python3 scripts/knowledge_map_finish.py check      # verify the committed run

`generate` needs the weights already cached (it forces Hugging Face offline mode)
and `rsvg-convert` on PATH. `check` needs neither and is what CI runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import imagegen
import localgen
from knowledge_map_local import MODEL, SEED, SIZE, STYLE


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "assets" / "knowledge-maps" / "v1"
OUT = ROOT / "assets" / "knowledge-maps" / "local-v2"
STEPS = 4
STRENGTH = 0.6
HATCH_STROKE = "2.4"
HATCH_EXTRA = " M-2,6.5 L6.5,-2 M2.5,11 L11,2.5"
SVG_NS = "http://www.w3.org/2000/svg"
RASTERIZER = ("rsvg-convert", "-w", "{width}", "-h", "{height}", "{svg}", "-o", "{png}")
COMMAND = (
    "mflux-generate-flux2", "--model", "{weights}", "--prompt-file", "{prompt_file}",
    "--width", "{width}", "--height", "{height}", "--steps", "{steps}", "--seed", "{seed}",
    "--low-ram", "--image", "{init}", "{strength}", "--output", "{output}",
)
PRESERVE = (
    "Preserve the reference drawing exactly: the same region outlines, the same pale, crosshatched and dark "
    "fills in the same places, the same faint contour paths, and the same fully black unreachable areas. "
    "Add only surface finish: ink texture, hatching grain, paper tooth and weathered edges. "
    "Do not move, add, remove, brighten or darken any region, and do not add figures or symbols."
)
FAMILIES = {
    "a": ("Border and beyond",
          "The reference shows one continuous mapped territory of five joined regions ending at a broken "
          "survey border on the right; beyond the border a rectangular expanse stays matte black. "
          "Four small survey strips run along the bottom."),
    "b": ("Inward-facing silhouettes",
          "The reference shows five wedge-shaped fields of view arranged in a ring around a central black "
          "void, with a small diagrammatic station glyph outside each wedge. "
          "Four small survey strips run along the bottom."),
    "c": ("Overlapping partial maps",
          "The reference shows three offset dark survey sheets overlapping like a palimpsest, each carrying "
          "part of the same terrain, with small amber registration crosses and a black unmapped column on "
          "the right. Four small survey strips run along the bottom."),
    "d": ("Maps within maps",
          "The reference shows a large dark survey frame holding five terrain regions on its left, a dashed "
          "inset frame on its right containing five much smaller regions, and black unmapped patches at both "
          "scales. Four small survey strips run along the bottom."),
}
FIXTURES = ("010-hint", "010-no-p6", "016", "039-before", "039-after")
VIEWPOINTS = ("reader", "responders")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prompt_for(family: str) -> str:
    return STYLE + FAMILIES[family][1] + " " + PRESERVE


def quiet_svg(source: bytes, sample_id: str) -> bytes:
    """Strip lettering, captions, legend and metadata; keep terrain, fills, contours and figures."""
    ET.register_namespace("", SVG_NS)
    root = ET.fromstring(source)
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ValueError(f"{sample_id}: source is not an SVG document")

    def strip(parent: ET.Element) -> None:
        parent_tag = parent.tag.split("}")[-1]
        for child in list(parent):
            tag = child.tag.split("}")[-1]
            if tag in ("text", "title", "desc", "metadata"):
                parent.remove(child)
                continue
            if (tag == "rect" and parent_tag != "pattern" and "data-attribution" not in child.attrib
                    and not (child.get("x") == "0" and child.get("y") == "0")):
                parent.remove(child)
                continue
            if tag == "path" and parent_tag == "pattern" and child.get("stroke-width"):
                child.set("stroke-width", HATCH_STROKE)
                child.set("d", child.get("d", "") + HATCH_EXTRA)
            strip(child)

    strip(root)
    for attribute in ("aria-labelledby",):
        root.attrib.pop(attribute, None)
    root.set("data-init-for", sample_id)
    title = ET.Element(f"{{{SVG_NS}}}title")
    title.text = f"Unlettered structural init image for {sample_id}"
    root.insert(0, title)
    return ET.tostring(root, encoding="utf-8", xml_declaration=False) + b"\n"


def run(argv: list[str], timeout: int) -> None:
    try:
        finished = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{argv[0]} timed out after {timeout}s") from None
    if finished.returncode != 0:
        tail = (finished.stderr or finished.stdout or "").strip().splitlines()
        raise RuntimeError(f"{argv[0]} exit {finished.returncode}: {tail[-1] if tail else 'no output'}")


def rasterize(svg: Path, png: Path) -> bytes:
    argv = [part.format(width=SIZE[0], height=SIZE[1], svg=svg, png=png) for part in RASTERIZER]
    run(argv, timeout=120)
    data = png.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("rsvg-convert did not write a PNG")
    return data


def rasterizer_version() -> str:
    try:
        finished = subprocess.run([RASTERIZER[0], "--version"], capture_output=True, text=True, timeout=10, check=False)
        first = (finished.stdout or "").strip().splitlines()
        return first[0] if first else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def finish(provider: imagegen.Provider, prompt: str, init_png: Path, output: Path) -> bytes:
    with tempfile.TemporaryDirectory() as workspace:
        prompt_file = Path(workspace) / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        argv = [part.format(weights=provider.model, prompt_file=prompt_file, width=SIZE[0], height=SIZE[1],
                            steps=STEPS, seed=SEED, init=init_png, strength=STRENGTH, output=output)
                for part in COMMAND]
        run(argv, timeout=imagegen.LOCAL_TIMEOUT)
    if not output.is_file():
        raise RuntimeError(f"{COMMAND[0]} exited cleanly but wrote no file to {output}")
    data = output.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise RuntimeError("Local model did not return a WebP image")
    return data


def v1_samples() -> list[dict]:
    manifest = json.loads((V1 / "manifest.json").read_text(encoding="utf-8"))
    samples = manifest["samples"]
    expected = {(f, x, v) for f in FAMILIES for x in FIXTURES for v in VIEWPOINTS}
    if len(samples) != 40 or {(s["family"], s["fixture"], s["viewpoint"]) for s in samples} != expected:
        raise ValueError("The v1 manifest must hold the full 40-sample matrix")
    return samples


def provider_for() -> imagegen.Provider:
    provider = imagegen.PROVIDERS_BY_ID[MODEL]
    if not provider.local or provider.build != "command" or not provider.commercial:
        raise ValueError("Only a commercially usable command-backed local model is allowed")
    if not localgen.eligible([provider], memory=localgen.unified_memory_gb(), allow_non_commercial=False):
        raise ValueError("Model exceeds the machine's recorded memory budget")
    return provider


def new_manifest(provider: imagegen.Provider) -> dict:
    return {
        "version": 2, "model": MODEL, "weights": provider.model, "licence": provider.licence,
        "route": "local-offline", "machine": localgen.chip(), "command": list(COMMAND),
        "rasterizer": list(RASTERIZER), "rasterizer_version": rasterizer_version(),
        "steps": STEPS, "strength": STRENGTH, "seed": SEED, "width": SIZE[0], "height": SIZE[1],
        "source": "assets/knowledge-maps/v1",
        "note": ("Structure-preserving finish studies: image-to-image over the unlettered v1 SVG geometry. "
                 "Evidence states come from the init image, not the model. Unlettered, not canonical, not adopted. "
                 "No hosted generation."),
        "results": [],
    }


def check(directory: Path | None = None, *, complete: bool = True) -> dict:
    directory = directory or OUT
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    provider = imagegen.PROVIDERS_BY_ID[MODEL]
    if (manifest["version"] != 2 or manifest["model"] != MODEL or manifest["route"] != "local-offline"
            or manifest["weights"] != provider.model or manifest["licence"] != provider.licence):
        raise ValueError("Expected the approved offline local model")
    if (manifest["command"] != list(COMMAND) or manifest["rasterizer"] != list(RASTERIZER)
            or manifest["steps"] != STEPS or manifest["strength"] != STRENGTH or manifest["seed"] != SEED
            or (manifest["width"], manifest["height"]) != SIZE):
        raise ValueError("Finish settings differ from the recorded run; use a new version rather than overwriting")
    sources = {sample["id"]: sample for sample in v1_samples()}
    rows = manifest["results"]
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)) or not set(ids) <= sources.keys():
        raise ValueError("Duplicate or unexpected finish sample IDs")
    if complete and set(ids) != sources.keys():
        raise ValueError("The finish comparison requires all 40 samples")
    for row in rows:
        source = sources[row["id"]]
        if (row["family"], row["fixture"], row["viewpoint"]) != (source["family"], source["fixture"], source["viewpoint"]):
            raise ValueError(f'Sample metadata drifted from v1: {row["id"]}')
        if (row["path"], row["init"], row["prompt"]) != (f'{row["id"]}.webp', f'{row["id"]}-init.svg', f'{row["family"]}.txt'):
            raise ValueError(f'Unexpected finish asset path for {row["id"]}')
        if row["source_sha256"] != source["sha256"]:
            raise ValueError(f'{row["id"]} was finished from a different v1 drawing than the one now committed')
        svg = (V1 / source["path"]).read_bytes()
        if digest(svg) != source["sha256"]:
            raise ValueError(f'v1 drawing no longer matches its manifest: {source["path"]}')
        init = (directory / row["init"]).read_bytes()
        if digest(init) != row["init_sha256"] or init != quiet_svg(svg, row["id"]):
            raise ValueError(f'Init drawing is not the unlettered form of the v1 sample: {row["id"]}')
        data = (directory / row["path"]).read_bytes()
        if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            raise ValueError(f'{row["path"]} is not a WebP image')
        if digest(data) != row["sha256"]:
            raise ValueError(f'Changed finish image for {row["id"]}')
        prompt = (directory / row["prompt"]).read_bytes()
        if digest(prompt) != row["prompt_sha256"] or prompt.decode("utf-8") != prompt_for(row["family"]):
            raise ValueError(f'Prompt changed for family {row["family"]}; use a new version rather than overwriting a run')
        if not isinstance(row["init_png_sha256"], str) or len(row["init_png_sha256"]) != 64 or row["seconds"] < 0:
            raise ValueError(f'Incomplete generation record for {row["id"]}')
    return manifest


def generate() -> None:
    provider = provider_for()
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = check(complete=False) if manifest_path.exists() else new_manifest(provider)
    done = {row["id"] for row in manifest["results"]}
    for family, (label, _) in FAMILIES.items():
        prompt = prompt_for(family)
        if imagegen._token_pieces(prompt) + imagegen.PROMPT_OVERHEAD > provider.prompt_tokens:
            raise ValueError(f"Family {family} exceeds the conservative prompt budget")
        prompt_path = OUT / f"{family}.txt"
        if prompt_path.exists() and prompt_path.read_text(encoding="utf-8") != prompt:
            raise ValueError(f"Prompt for family {family} differs from the recorded run")
        prompt_path.write_text(prompt, encoding="utf-8")
    for sample in v1_samples():
        sid = sample["id"]
        if sid in done:
            print(f"Keep existing finish {sid}", flush=True)
            continue
        target = OUT / f"{sid}.webp"
        if target.exists():
            raise ValueError(f"Unrecorded image already exists: {target}")
        source = (V1 / sample["path"]).read_bytes()
        if digest(source) != sample["sha256"]:
            raise ValueError(f"v1 drawing does not match its manifest: {sample['path']}")
        init = quiet_svg(source, sid)
        init_path = OUT / f"{sid}-init.svg"
        init_path.write_bytes(init)
        print(f"Finishing {sid} with {MODEL} (offline, strength {STRENGTH})", flush=True)
        started = time.monotonic()
        with tempfile.TemporaryDirectory() as workspace:
            png = Path(workspace) / "init.png"
            init_png = rasterize(init_path, png)
            data = finish(provider, prompt_for(sample["family"]), png, Path(workspace) / "out.webp")
        target.write_bytes(data)
        row = {
            "id": sid, "family": sample["family"], "fixture": sample["fixture"], "viewpoint": sample["viewpoint"],
            "label": f'{sample["family_label"]} · {sample["fixture"]} · {sample["viewpoint_label"]}',
            "path": target.name, "init": init_path.name, "prompt": f'{sample["family"]}.txt',
            "source_sha256": sample["sha256"], "init_sha256": digest(init), "init_png_sha256": digest(init_png),
            "seconds": round(time.monotonic() - started, 2), "sha256": digest(data),
            "prompt_sha256": digest(prompt_for(sample["family"]).encode("utf-8")),
        }
        manifest["results"].append(row)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        imagegen.log_generation({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "purpose": "knowledge-map-finish", "route": "local", "provider": MODEL,
            "model": provider.model, "sample": sid, "seed": SEED, "strength": STRENGTH, "steps": STEPS,
            "usd": 0.0, "seconds": row["seconds"], "path": str(target.relative_to(ROOT)),
        })
        print(f"Saved {target.relative_to(ROOT)} in {row['seconds']}s", flush=True)
    check()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline structure-preserving knowledge-map finish studies")
    parser.add_argument("command", choices=("generate", "check"))
    args = parser.parse_args()
    try:
        if args.command == "generate":
            generate()
        else:
            manifest = check()
            print(f'Validated {len(manifest["results"])} offline structure-preserving finish images')
    except (OSError, ValueError, KeyError, RuntimeError, ET.ParseError) as error:
        parser.exit(1, f"Knowledge-map finish generation: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
