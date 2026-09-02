#!/usr/bin/env python3
"""Reserved thumbnail hook.

The project can add an image-processing dependency here later. Keeping this
entry point makes the workflow predictable without requiring one today.
"""


def main() -> int:
    print("No thumbnail generation configured yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
