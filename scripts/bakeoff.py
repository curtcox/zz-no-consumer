#!/usr/bin/env python3
"""Produce the whole published bake-off from one API key, through OpenRouter.

`scripts/imagegen.py` calls each vendor directly, which means a Google key, an
OpenAI key, a fal key, and a Replicate key before the first comparison exists.
That is four accounts of friction in front of a decision that should take an
afternoon. OpenRouter's unified image API fronts most of the roster behind a
single key and reports the exact cost of every call, so this script can generate
every candidate the aggregator can reach, price the run honestly, and write the
published comparison in one command:

    export OPENROUTER_API_KEY=...
    python3 scripts/bakeoff.py models     # what the aggregator can actually route
    python3 scripts/bakeoff.py estimate   # what a full run would cost
    python3 scripts/bakeoff.py run        # generate, price, and write the sheet

The output lands in `assets/bakeoff/<run>/` and is published at `/bakeoff/` by
`scripts/build-site.py`, so the images behind the decision are committed evidence
rather than something only the person who ran it ever saw.

One candidate can never appear here. `flux-2-dev-lora` is FLUX.2 [dev] with a
style LoRA trained on our own ink and texture references; no aggregator can host
weights that do not exist yet. Judge it against the FLUX.2 [pro] column, which
shares the same base model without the trained style lock, and remember that the
gap between them is the entire reason to train one.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

import imagegen


ROOT = imagegen.ROOT


def key_or_exit() -> str:
    key = os.environ.get(imagegen.OPENROUTER_ENV)
    if not key:
        raise SystemExit(
            f"{imagegen.OPENROUTER_ENV} is not set. Create a key at "
            f"https://openrouter.ai/keys, export it, and run this again. "
            f"To see the pipeline without a key or any spend, run "
            f"`python3 scripts/bakeoff.py run --dry-run`."
        )
    return key


def routable() -> list[imagegen.Provider]:
    return [provider for provider in imagegen.PROVIDERS if provider.openrouter]


def unroutable() -> list[imagegen.Provider]:
    return [provider for provider in imagegen.PROVIDERS if not provider.openrouter]


def cmd_models(args: argparse.Namespace) -> int:
    """Ask the aggregator what it can route, rather than trusting the roster."""
    available = imagegen.openrouter_models(key_or_exit())
    print(f"OpenRouter offers {len(available)} image model(s).\n")
    print(f"{'ID':<20} {'SLUG':<34} {'$/IMAGE':>8}  STATE")
    missing = 0
    for provider in routable():
        live = provider.openrouter in available
        missing += not live
        print(f"{provider.id:<20} {provider.openrouter:<34} "
              f"{provider.unit_usd('openrouter'):>8.3f}  "
              f"{'available' if live else 'NOT OFFERED — update the roster'}")
    for provider in unroutable():
        print(f"{provider.id:<20} {'—':<34} {'':>8}  vendor API only ({provider.auth_env})")

    if missing:
        print(f"\n{missing} roster slug(s) are no longer offered. The full catalogue:")
        for identifier in sorted(available):
            print(f"  {identifier}")
    return 1 if missing else 0


def cmd_estimate(args: argparse.Namespace) -> int:
    providers = routable()
    samples = imagegen.chosen_samples(args.sample)
    images = len(samples) * args.repeat
    print(f"{len(providers)} candidate(s) × {len(samples)} panel(s) × {args.repeat} take(s) "
          f"= {len(providers) * images} images through one key\n")
    print(f"{'ID':<20} {'$/IMAGE':>8} {'RUN':>8} {'FULL BOOK':>10}")
    total = 0.0
    for provider in providers:
        cost = images * provider.unit_usd("openrouter")
        total += cost
        print(f"{provider.id:<20} {provider.unit_usd('openrouter'):>8.3f} {cost:>8.2f} "
              f"{provider.full_book_usd('openrouter'):>10,.0f}")
    print(f"\nWhole run: about ${total:,.2f}. OpenRouter meters each call, so the "
          f"figure recorded in the manifest is what was actually charged.")
    skipped = ", ".join(provider.id for provider in unroutable())
    print(f"Not reachable through the aggregator: {skipped}.")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.dry_run:
        key = key_or_exit()
        if not args.skip_check:
            available = imagegen.openrouter_models(key)
            gone = [provider.openrouter for provider in routable()
                    if provider.openrouter not in available]
            if gone:
                raise SystemExit(
                    f"OpenRouter no longer offers {', '.join(gone)}. "
                    f"Run `python3 scripts/bakeoff.py models` for the current catalogue "
                    f"and update the roster in scripts/imagegen.py, or pass --skip-check."
                )

    base = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    stamp = args.run or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    directory = base / stamp
    samples = imagegen.chosen_samples(args.sample)

    print(f"Run {stamp} → {directory.relative_to(ROOT)}")
    manifest = imagegen.run_samples(
        directory,
        routable(),
        samples,
        repeat=args.repeat,
        dry_run=args.dry_run,
        route="openrouter",
        image_format=args.format,
    )
    imagegen.report_run(directory, manifest)

    skipped = ", ".join(provider.id for provider in unroutable())
    print(f"\nNot in this run, vendor API only: {skipped}.")
    print("Those need `python3 scripts/imagegen.py sample --provider <id>` and their own key.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("models", help="what OpenRouter can route, against the roster")

    estimate = commands.add_parser("estimate", help="what a full single-key run would cost")
    estimate.add_argument("--sample", action="append")
    estimate.add_argument("--repeat", type=int, default=2)

    run = commands.add_parser("run", help="generate every routable candidate and write the sheet")
    run.add_argument("--out-dir", type=Path, default=imagegen.DEFAULT_RUN_DIR)
    run.add_argument("--run", help="run directory name; defaults to a UTC timestamp")
    run.add_argument("--sample", action="append", help="panel id such as 001-01; repeatable")
    run.add_argument("--repeat", type=int, default=2,
                     help="takes per panel; more than one exposes style drift")
    run.add_argument("--format", default=imagegen.DEFAULT_FORMAT, choices=tuple(imagegen.SUFFIXES),
                     help="image format to request; WebP keeps a committed run small")
    run.add_argument("--dry-run", action="store_true",
                     help="write prompt placeholders instead of calling the API")
    run.add_argument("--skip-check", action="store_true",
                     help="do not verify the roster against the live catalogue first")

    args = parser.parse_args()
    return {"models": cmd_models, "estimate": cmd_estimate, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
