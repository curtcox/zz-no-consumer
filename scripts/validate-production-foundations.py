#!/usr/bin/env python3
"""Validate palette, visual-continuity, prompt, and asset foundations."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "design/palette.md",
    "design/visual-continuity.md",
    "prompts/global-style.md",
    "prompts/characters.md",
    "prompts/environments.md",
    "prompts/negative-prompt.md",
    "prompts/pages/001/page.md",
    "data/assets.yaml",
]

PALETTE_TOKENS = {
    "ink-100",
    "ink-85",
    "paper",
    "paper-dirty",
    "steel",
    "institution",
    "nicotine",
    "moss",
    "claret",
    "amber",
}


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.exists():
            errors.append(f"Missing production foundation: {relative}")
            continue
        if "Placeholder" in path.read_text(encoding="utf-8"):
            errors.append(f"Unresolved placeholder: {relative}")

    palette_path = ROOT / "design/palette.md"
    if palette_path.exists():
        palette = palette_path.read_text(encoding="utf-8")
        for token in sorted(PALETTE_TOKENS):
            if f"`{token}`" not in palette:
                errors.append(f"Palette token missing: {token}")

    page_script = (ROOT / "content/pages/001.md").read_text(encoding="utf-8")
    panel_count = len(re.findall(r"^## Panel \d+$", page_script, re.MULTILINE))
    panel_prompts = sorted((ROOT / "prompts/pages/001").glob("panel-[0-9][0-9].md"))
    if len(panel_prompts) != panel_count:
        errors.append(
            f"Page 001 prompt count mismatch: {len(panel_prompts)} prompt files for {panel_count} panels"
        )

    assets_path = ROOT / "data/assets.yaml"
    if assets_path.exists():
        assets = assets_path.read_text(encoding="utf-8")
        sources = re.findall(r"^\s+source:\s+(.+)$", assets, re.MULTILINE)
        for source in sources:
            if not (ROOT / source.strip()).exists():
                errors.append(f"Asset source does not exist: {source.strip()}")

    if errors:
        print("Production-foundation validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(
        "Production foundations validated: "
        f"{len(PALETTE_TOKENS)} palette tokens, {panel_count} page-001 panel prompts, asset sources resolved."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
