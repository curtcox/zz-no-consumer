#!/usr/bin/env python3
"""Generate the book's panel art locally, one panel, a range, or all 541.

This is the production run, not the bake-off. `scripts/imagegen.py` decides which
generator to use; this uses the chosen one to make the artwork, writing each panel
to `assets/art/panels/NNN-II.webp`, where `scripts/build-site.py` picks it up and
letters it through the approved slot convention.

    python3 scripts/produce.py status                  # how much of the book has art
    python3 scripts/produce.py plan                    # what a run would do, and for how long
    python3 scripts/produce.py run                     # everything still missing
    python3 scripts/produce.py run --slot 013-02       # one image
    python3 scripts/produce.py run --page 013          # one page
    python3 scripts/produce.py run --from 001 --to 020 # a range of pages
    python3 scripts/produce.py run --chapter prologue  # a chapter
    python3 scripts/produce.py registers               # audit the register derivation

A full pass is 541 renders. At the measured 66 seconds each that is about ten
hours, so the run is built to be interrupted: panels that already have art are
skipped, progress and a running estimate are printed, and Ctrl-C stops after the
current panel rather than losing it. Re-running continues where it stopped.
`--force` regenerates panels that already exist, and says how many it will
overwrite before it starts.

Page sheets are not generated. A page is composed from its panels by layout, the
way a comic page is actually made, so the page grammar governs it and it costs no
generation time.
"""

from __future__ import annotations

import argparse
import re
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import imagegen
import letterpress
import localgen
import textimage


ROOT = imagegen.ROOT
ART_DIR = ROOT / "assets" / "art" / "panels"
PAGES_FILE = ROOT / "data" / "pages.yaml"
DEFAULT_SEED = 1001

# Register is derived from a page's first location, matched in this order. The
# first pattern that appears in the location name wins, and anything unmatched is
# an incident-register panel, which is the book's default voice. `registers`
# prints the result for every page so a wrong call is visible rather than silent.
REGISTER_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("creator", ("curt-home",)),
    ("invented future", ("unnamed-future", "continuation-montage")),
    ("dossier", ("evidence", "dossier", "transcript-archive", "report-comparison",
                 "public-record", "announcement-ledger")),
    ("institutional", ("review-workspace", "security-operations", "accountability-forum",
                       "lab-room", "regulatory", "institutional", "board-composite",
                       "security-stack", "security-workspace", "incident-response",
                       "training-program")),
)
DEFAULT_REGISTER = "incident"


@dataclass(frozen=True)
class Slot:
    """One required image: a page, a panel index, and how to letter its prompt."""

    page: str
    panel: int
    chapter: str
    register: str

    @property
    def id(self) -> str:
        return f"{self.page}-{self.panel:02d}"

    def art(self) -> Path | None:
        return letterpress.find_art(self.page, self.panel)


def page_locations(page_id: str) -> list[str]:
    source = (ROOT / "content" / "pages" / f"{page_id}.md").read_text(encoding="utf-8")
    match = re.search(r"^locations:\s*\n((?:\s*-\s*.+\n)+)", source, re.M)
    return [item.strip() for item in re.findall(r"-\s*(.+)", match.group(1))] if match else []


def register_for(page_id: str) -> str:
    """Which register modifier this page's panels are drawn in."""
    locations = page_locations(page_id)
    primary = locations[0] if locations else ""
    for register, patterns in REGISTER_RULES:
        if any(pattern in primary for pattern in patterns):
            return register
    return DEFAULT_REGISTER


def all_slots() -> list[Slot]:
    """Every panel image the book requires, in reading order."""
    slots = []
    for script in textimage.book_scripts():
        register = register_for(script.id)
        for panel in script.panels:
            slots.append(Slot(script.id, panel.index, script.chapter, register))
    return slots


# ------------------------------------------------------------------ selection


def select(slots: list[Slot], args: argparse.Namespace) -> list[Slot]:
    """Narrow the full set to what was asked for. No filters means all of it."""
    chosen = slots
    if args.slot:
        wanted = set(args.slot)
        unknown = wanted - {s.id for s in slots}
        if unknown:
            raise SystemExit(f"No such panel: {', '.join(sorted(unknown))}")
        chosen = [s for s in chosen if s.id in wanted]
    if args.page:
        wanted = set(args.page)
        unknown = wanted - {s.page for s in slots}
        if unknown:
            raise SystemExit(f"No such page: {', '.join(sorted(unknown))}")
        chosen = [s for s in chosen if s.page in wanted]
    if args.chapter:
        wanted = set(args.chapter)
        known = {s.chapter for s in slots}
        unknown = wanted - known
        if unknown:
            raise SystemExit(f"No such chapter: {', '.join(sorted(unknown))}. "
                             f"Known: {', '.join(sorted(known))}")
        chosen = [s for s in chosen if s.chapter in wanted]
    if args.start or args.end:
        low = args.start or min(s.page for s in slots)
        high = args.end or max(s.page for s in slots)
        if low > high:
            raise SystemExit(f"--from {low} is after --to {high}")
        chosen = [s for s in chosen if low <= s.page <= high]
    if args.register:
        chosen = [s for s in chosen if s.register in set(args.register)]
    if args.limit:
        chosen = chosen[:args.limit]
    return chosen


def provider_for(name: str | None) -> imagegen.Provider:
    """The local model to draw with: the named one, or the best ready default."""
    if name:
        provider = imagegen.PROVIDERS_BY_ID.get(name)
        if provider is None:
            raise SystemExit(f"Unknown provider {name!r}. "
                             f"See `python3 scripts/localgen.py doctor`.")
        if not provider.local:
            raise SystemExit(f"{name} is a hosted candidate; this script generates locally.")
        return provider
    ready = [p for p in imagegen.LOCAL
             if p.commercial and (p.installed() or p.build == "http")]
    if not ready:
        raise SystemExit(
            "No local model is installed under a licence whose output can ship. "
            "Run `python3 scripts/localgen.py doctor` to see what is missing.")

    # Having the command on PATH is not having the weights: mflux installs every
    # model's entry point at once. Prefer a model that has actually produced an
    # image on this machine, so a ten-hour run does not stall on a first download.
    proven = localgen.measured_seconds()
    tried = [p for p in ready if p.id in proven]
    if tried:
        return min(tried, key=lambda p: proven[p.id])
    choice = min(ready, key=lambda p: p.seconds_per_image)
    print(f"note: {choice.label} has not run on this machine yet. Its first panel will "
          f"download weights, and its {choice.seconds_per_image:.0f}s estimate is unverified.\n"
          f"      `python3 scripts/localgen.py doctor` lists what has been measured.")
    return choice


# ----------------------------------------------------------------- reporting


def human(seconds: float) -> str:
    if seconds < 90:
        return f"{seconds:.0f}s"
    if seconds < 5400:
        return f"{seconds/60:.0f}m"
    return f"{seconds/3600:.1f}h"


def summarise(chosen: list[Slot], provider: imagegen.Provider, *, force: bool) -> tuple[list[Slot], list[Slot]]:
    missing = [s for s in chosen if s.art() is None]
    existing = [s for s in chosen if s.art() is not None]
    todo = chosen if force else missing
    rate = provider.seconds_per_image or 60
    print(f"Model:     {provider.label} ({provider.licence})")
    print(f"Selected:  {len(chosen)} panel(s) of {len(all_slots())} in the book")
    print(f"Have art:  {len(existing)}")
    print(f"To draw:   {len(todo)}" + ("  (--force will overwrite existing art)" if force and existing else ""))
    if todo:
        print(f"Estimate:  {human(len(todo) * rate)} at {rate:.0f}s per panel")
    return todo, existing


def cmd_status(args: argparse.Namespace) -> int:
    slots = all_slots()
    done = [s for s in slots if s.art() is not None]
    print(f"{len(done)} of {len(slots)} panels have art ({100*len(done)/len(slots):.1f}%)\n")
    by_chapter: dict[str, list[int]] = {}
    for slot in slots:
        row = by_chapter.setdefault(slot.chapter, [0, 0])
        row[1] += 1
        row[0] += slot.art() is not None
    print(f"{'CHAPTER':<14} {'DONE':>6} {'OF':>5}  PROGRESS")
    for chapter, (have, total) in by_chapter.items():
        bar = "#" * round(20 * have / total) + "." * (20 - round(20 * have / total))
        print(f"{chapter:<14} {have:>6} {total:>5}  {bar}")
    return 0


def cmd_registers(args: argparse.Namespace) -> int:
    """Show how every page was classified, so a wrong call is visible."""
    counts: dict[str, int] = {}
    rows = []
    for script in textimage.book_scripts():
        register = register_for(script.id)
        counts[register] = counts.get(register, 0) + 1
        rows.append((script.id, register, (page_locations(script.id) or ["—"])[0], script.title))
    if args.verbose:
        print(f"{'PAGE':<6} {'REGISTER':<16} {'PRIMARY LOCATION':<34} TITLE")
        for page, register, location, title in rows:
            print(f"{page:<6} {register:<16} {location:<34} {title}")
        print()
    print(f"{'REGISTER':<16} {'PAGES':>6}")
    for register, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{register:<16} {count:>6}")
    print(f"\nDerived from each page's first location. Edit REGISTER_RULES in this "
          f"script if a page is classified wrongly.")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    provider = provider_for(args.provider)
    chosen = select(all_slots(), args)
    if not chosen:
        print("Nothing selected.")
        return 1
    todo, _ = summarise(chosen, provider, force=args.force)
    if todo:
        shown = ", ".join(s.id for s in todo[:14])
        print(f"\nWould draw: {shown}{' …' if len(todo) > 14 else ''}")
        print(f"Size:      {args.width}x{args.height}"
              f"{'  (above the 1200x800 the model was measured at)' if args.width > 1200 else ''}")
    return 0


# --------------------------------------------------------------------- the run


class Interrupt:
    """Ctrl-C finishes the panel in flight instead of losing it."""

    def __init__(self) -> None:
        self.asked = False
        signal.signal(signal.SIGINT, self._handle)

    def _handle(self, *_: object) -> None:
        if self.asked:
            raise KeyboardInterrupt
        self.asked = True
        print("\n  interrupt received; finishing this panel then stopping "
              "(press Ctrl-C again to stop now)")


def cmd_run(args: argparse.Namespace) -> int:
    provider = provider_for(args.provider)
    chosen = select(all_slots(), args)
    if not chosen:
        print("Nothing selected.")
        return 1
    todo, _ = summarise(chosen, provider, force=args.force)
    if not todo:
        print("\nNothing to draw. Use --force to regenerate.")
        return 0
    if args.dry_run:
        print("\nDry run; nothing generated.")
        return 0

    ART_DIR.mkdir(parents=True, exist_ok=True)
    size = (args.width, args.height)
    stop = Interrupt()
    started = time.time()
    made = failed = 0
    times: list[float] = []

    for position, slot in enumerate(todo, 1):
        if stop.asked:
            break
        prompt = imagegen.compose_panel(slot.page, slot.panel, slot.register)
        for take in range(args.takes):
            seed = args.seed + take
            began = time.time()
            try:
                result = imagegen.generate(provider, prompt, seed, route="local",
                                           image_format=args.format, size=size)
            except (RuntimeError, OSError, KeyError, IndexError, ValueError) as error:
                failed += 1
                print(f"  [{position}/{len(todo)}] {slot.id}  FAILED: {error}")
                continue
            suffix = f"-{take + 1}" if args.takes > 1 else ""
            target = ART_DIR / f"{slot.id}{suffix}{result.suffix}"
            target.write_bytes(result.data)
            elapsed = time.time() - began
            times.append(elapsed)
            made += 1
            remaining = (len(todo) - position) * (sum(times) / len(times))
            print(f"  [{position}/{len(todo)}] {slot.id}  {slot.register:<16} "
                  f"{elapsed:>5.0f}s  {len(result.data)//1024:>4} KB  "
                  f"eta {human(remaining)}")
            imagegen.log_generation({
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "purpose": "panel-art",
                "route": "local",
                "provider": provider.id,
                "model": provider.model or provider.id,
                "page": slot.page,
                "panel": slot.panel,
                "register": slot.register,
                "seed": seed,
                "size": [args.width, args.height],
                "seconds": round(elapsed, 1),
                "usd": 0.0,
                "path": str(target.relative_to(ROOT)),
            })

    total = time.time() - started
    print(f"\nDrew {made} panel(s) in {human(total)}"
          f"{f', {failed} failed' if failed else ''}.")
    if stop.asked:
        left = len(todo) - made - failed
        print(f"Stopped early; {left} panel(s) still to draw. Re-run to continue.")
    remaining_book = [s for s in all_slots() if s.art() is None]
    print(f"{len(all_slots()) - len(remaining_book)} of {len(all_slots())} panels now have art.")
    if made:
        print("Letter and publish them with: python3 scripts/build-site.py")
    return 1 if failed and not made else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def selection(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--slot", action="append", metavar="NNN-II",
                         help="one panel image, such as 013-02; repeatable")
        sub.add_argument("--page", action="append", metavar="NNN",
                         help="every panel of one page; repeatable")
        sub.add_argument("--chapter", action="append", help="every panel of one chapter")
        sub.add_argument("--from", dest="start", metavar="NNN", help="first page of a range")
        sub.add_argument("--to", dest="end", metavar="NNN", help="last page of a range")
        sub.add_argument("--register", action="append",
                         help="only panels in this register, e.g. creator")
        sub.add_argument("--limit", type=int, help="stop after this many panels")
        sub.add_argument("--provider", help="local model id; defaults to the fastest ready one")
        sub.add_argument("--force", action="store_true",
                         help="regenerate panels that already have art")
        sub.add_argument("--width", type=int, default=imagegen.PANEL_SIZE[0])
        sub.add_argument("--height", type=int, default=imagegen.PANEL_SIZE[1])

    status = commands.add_parser("status", help="how much of the book has art")

    registers = commands.add_parser("registers", help="audit the register derivation")
    registers.add_argument("--verbose", "-v", action="store_true", help="list every page")

    plan = commands.add_parser("plan", help="what a run would do, without doing it")
    selection(plan)

    run = commands.add_parser("run", help="generate the selected panels")
    selection(run)
    run.add_argument("--takes", type=int, default=1,
                     help="images per panel; more than one appends -1, -2 to the name")
    run.add_argument("--seed", type=int, default=DEFAULT_SEED)
    run.add_argument("--format", default=imagegen.DEFAULT_FORMAT, choices=tuple(imagegen.SUFFIXES))
    run.add_argument("--dry-run", action="store_true", help="print the plan and stop")

    args = parser.parse_args()
    return {"status": cmd_status, "registers": cmd_registers,
            "plan": cmd_plan, "run": cmd_run}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
