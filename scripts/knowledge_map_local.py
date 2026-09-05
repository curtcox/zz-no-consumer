from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import imagegen
import localgen


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "knowledge-maps" / "local-v1"
MODEL = "flux2-klein-4b"
SEED = 42016
SIZE = (960, 640)
STYLE = (
    "An editorial cartographic illustration for an investigative graphic novel about uncertain knowledge. "
    "Flat overhead diagram, mature hand-inked brush contours, dry-brush abrasion, restrained halftone and dirty paper grain. "
    "Only charcoal black, warm off-white paper and muted steel gray; tiny amber marks for uncertain boundaries. "
    "Three surface treatments: dark unknown territory, pale supported territory, crosshatched contested territory. "
    "The unreachable region stays completely dark. No percentages, meters, scoreboard, glowing brain, neon, logos, "
    "screens, letters, numbers or words. This is a conceptual map, not a geographic world map. "
    "Leave text out entirely; labels will be presented separately. "
)
STUDIES = {
    "a": (
        "Border and beyond",
        "A single irregular island of mapped territory occupies the left two thirds of the image. "
        "Thin contour lines and paths connect five uneven regions, some pale, some hatched, some dark. "
        "At the right a broken survey border abruptly ends all contour lines. Beyond it an enormous "
        "matte-black expanse remains unmapped. The same faint paths remain visible where fog has returned. "
        "One tiny anonymous human observer stands outside the island looking across it; no other figures. "
        "The shape of the unknown is not filled in. The border is the central visual idea.",
    ),
    "b": (
        "Inward-facing silhouettes",
        "Five small anonymous human observer silhouettes face inward around a large irregular black void. "
        "They are diagrammatic observers, not AI bodies or portraits. Each observer has a different wedge-shaped "
        "partial field of view containing faint paths and contour marks. Some wedges contain pale patches, "
        "others crosshatching or dense shadow. Their views overlap but never illuminate the central void. "
        "No wedge sees behind another observer. The composition makes differing perspectives spatially visible; "
        "there is no all-seeing eye and no central illuminated object.",
    ),
    "c": (
        "Overlapping partial maps",
        "Three offset torn survey sheets float almost flat over a charcoal ground, overlapping like a palimpsest. "
        "Each sheet repeats recognizably the same five irregular terrain shapes and branching paths, but "
        "different portions are pale, crosshatched or dark. Registration marks deliberately fail to line up. "
        "The overlap preserves conflicting boundaries rather than blending them into a complete map. "
        "An irregular hole through all three sheets reveals only black underneath. No figures. "
        "Make the misaligned paper layers, not a grid or isolated islands, the dominant visual structure.",
    ),
    "d": (
        "Maps within maps",
        "A large irregular survey map contains a smaller skewed paper inset, and that inset holds one even smaller "
        "incomplete map. Repeat the same branching contour motif at all three scales but omit different paths. "
        "The inset has a broken tentative border and a thin bracket leading from a small anonymous human observer "
        "at the outer edge, showing that it is the observer's conjecture, not a true window into another mind. "
        "Pale, hatched and dark patches disagree between outer map and inner model. "
        "Leave an unmapped black area on every level. No infinite tunnel, no faces, no brain imagery.",
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(directory: Path | None = None, *, complete: bool = True) -> dict:
    directory = directory or OUT
    manifest = json.loads((directory / "manifest.json").read_text())
    provider = imagegen.PROVIDERS_BY_ID[MODEL]
    if (manifest["model"] != MODEL or manifest["route"] != "local-offline"
            or manifest["weights"] != provider.model or manifest["licence"] != provider.licence):
        raise ValueError("Expected the approved offline local model")
    rows = manifest["results"]
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)) or not set(ids) <= STUDIES.keys():
        raise ValueError("Duplicate or unexpected concept IDs")
    if complete and set(ids) != STUDIES.keys():
        raise ValueError("The local comparison requires all four concepts")
    for row in rows:
        if row["path"] != f'{row["id"]}.webp' or row["prompt"] != f'{row["id"]}.txt':
            raise ValueError("Unexpected concept asset path")
        data = (directory / row["path"]).read_bytes()
        prompt = (directory / row["prompt"]).read_bytes()
        if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
            raise ValueError(f'{row["path"]} is not a WebP image')
        if digest(data) != row["sha256"] or digest(prompt) != row["prompt_sha256"]:
            raise ValueError(f'Changed asset for {row["id"]}')
        expected_prompt = STYLE + STUDIES[row["id"]][1]
        if prompt.decode() != expected_prompt:
            raise ValueError("Prompt changed; use a new version rather than overwriting a run")
        if (row["width"], row["height"]) != SIZE or row["seed"] != SEED:
            raise ValueError("Comparison geometry or seed differs")
    return manifest


def generate() -> None:
    provider = imagegen.PROVIDERS_BY_ID[MODEL]
    if not provider.local or provider.build != "command" or not provider.commercial:
        raise ValueError("Only a commercially usable command-backed local model is allowed")
    if not localgen.eligible([provider], memory=localgen.unified_memory_gb(), allow_non_commercial=False):
        raise ValueError("Model exceeds the machine's recorded memory budget")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = check(complete=False) if manifest_path.exists() else {
        "version": 1, "model": MODEL, "weights": provider.model, "licence": provider.licence,
        "route": "local-offline", "machine": localgen.chip(), "command": list(provider.command),
        "note": "Unlettered concept studies, not canonical evidence-state diagrams. No hosted generation.",
        "results": [],
    }
    done = {row["id"] for row in manifest["results"]}
    for key, (label, direction) in STUDIES.items():
        if key in done:
            print(f"Keep existing concept {key}: {label}", flush=True)
            continue
        prompt = STYLE + direction
        if imagegen._token_pieces(prompt) + imagegen.PROMPT_OVERHEAD > provider.prompt_tokens:
            raise ValueError(f"Concept {key} exceeds the conservative prompt budget")
        target = OUT / f"{key}.webp"
        if target.exists():
            raise ValueError(f"Unrecorded image already exists: {target}")
        print(f"Generating {key}: {label} with {MODEL} (offline)", flush=True)
        started = time.monotonic()
        made = imagegen.generate_command(provider, prompt, SEED, SIZE)
        if made.suffix != ".webp" or made.data[8:12] != b"WEBP":
            raise ValueError("Local model did not return a WebP image")
        target.write_bytes(made.data)
        (OUT / f"{key}.txt").write_text(prompt)
        row = {
            "id": key, "label": label, "path": target.name, "prompt": f"{key}.txt",
            "seed": SEED, "width": SIZE[0], "height": SIZE[1],
            "seconds": round(time.monotonic() - started, 2), "sha256": digest(made.data),
            "prompt_sha256": digest(prompt.encode()),
        }
        manifest["results"].append(row)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        imagegen.log_generation({
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "purpose": "knowledge-map-concept", "route": "local", "provider": MODEL,
            "model": provider.model, "sample": key, "seed": SEED, "usd": 0.0,
            "seconds": row["seconds"], "path": str(target.relative_to(ROOT)),
        })
        print(f"Saved {target.relative_to(ROOT)}", flush=True)
    check()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline local-model knowledge-map concept studies")
    parser.add_argument("command", choices=("generate", "check"))
    args = parser.parse_args()
    try:
        if args.command == "generate":
            generate()
        else:
            manifest = check()
            print(f'Validated {len(manifest["results"])} offline local-model concept images')
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        parser.exit(1, f"Knowledge-map local generation: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
