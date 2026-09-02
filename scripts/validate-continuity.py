#!/usr/bin/env python3
"""Perform lightweight checks on the continuity data files."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        ROOT / "data" / "continuity.yaml",
        ROOT / "content" / "continuity.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("Missing continuity files:")
        print("\n".join(f"- {path}" for path in missing))
        return 1
    print("Continuity files present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
