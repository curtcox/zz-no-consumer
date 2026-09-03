#!/usr/bin/env python3
"""Run the same panel prompts through every candidate image generator.

The book needs 541 panel images and 112 page sheets in one hand-inked style.
Choosing the generator is therefore a production decision about style stability,
palette discipline, and text suppression, not a shopping trip. This module makes
that decision testable: it composes one canonical prompt per sample panel from
the same sources the artwork will use, sends that identical prompt to each
candidate, and lays the results out side by side with a scoring rubric.

    python3 scripts/imagegen.py providers            # roster, price, key state
    python3 scripts/imagegen.py prompts              # composed bake-off prompts
    python3 scripts/imagegen.py estimate             # sample and full-book cost
    python3 scripts/imagegen.py sample --dry-run     # whole pipeline, no spend
    python3 scripts/imagegen.py sample --provider flux-2-pro --provider gpt-image
    python3 scripts/imagegen.py sheet                # side-by-side comparison
    python3 scripts/imagegen.py rank                 # weighted result of scores

Every candidate here needs its own vendor account. `scripts/bakeoff.py` runs the
same prompts through OpenRouter instead, so the published comparison can be
produced from one key; this module holds the roster, the prompt composer, and the
comparison sheet that both paths share.

`--dry-run` substitutes a `scripts/textimage.py` placeholder carrying the exact
prompt that would have been sent, so the composer, the run layout, the log, and
the comparison sheet can all be validated before any key exists or any money is
spent. Real runs need only the environment variable named in the roster; a
provider with no key is skipped rather than failing the run. Only live generations
reach `data/generation-log.jsonl`; dry runs stay inside the run directory.

Runs are written to `assets/bakeoff/<run>/` and published by
`scripts/build-site.py` at `/bakeoff/`, so the evidence for the decision travels
with the repository rather than living on whoever ran it.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import textimage


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"
PAGE_DIR = ROOT / "content" / "pages"
PALETTE_FILE = ROOT / "design" / "palette.md"
DEFAULT_RUN_DIR = ROOT / "assets" / "bakeoff"
GENERATION_LOG = ROOT / "data" / "generation-log.jsonl"
LOCAL_MODELS = ROOT / "data" / "local-models.json"

PANEL_SIZE = textimage.PANEL_SIZE          # 1200 x 800, the book's panel slot
PANEL_ASPECT = "3:2"
PANEL_SLOTS = 541                          # panel images in content/pages/
PAGE_SLOTS = 112                           # page sheets
ATTEMPTS_PER_SLOT = 6                      # planning assumption for full-book cost

OPENROUTER_IMAGES = "https://openrouter.ai/api/v1/images"
OPENROUTER_MODELS = "https://openrouter.ai/api/v1/images/models"
OPENROUTER_ENV = "OPENROUTER_API_KEY"

REQUEST_TIMEOUT = 300
LOCAL_TIMEOUT = 1800      # a 20B model at 8-bit on a laptop is not quick

# WebP keeps a committed run to a few megabytes. The comparison is about ink,
# palette, geometry, and text suppression, none of which survive or die on the
# last percent of compression.
DEFAULT_FORMAT = "webp"
SUFFIXES = {"webp": ".webp", "png": ".png", "jpeg": ".jpg"}
MEDIA_SUFFIXES = {"image/webp": ".webp", "image/png": ".png", "image/jpeg": ".jpg"}


# ------------------------------------------------------------------ the roster


@dataclass(frozen=True)
class Provider:
    """One candidate generator and everything needed to call it."""

    id: str
    label: str
    vendor: str
    tier: str                    # premium | balanced | volume
    usd_per_image: float
    auth_env: str
    strengths: str
    risks: str
    endpoint: str = ""
    model: str = ""
    build: str = ""              # request shape: openai | gemini | imagen | fal | replicate
    batch_usd_per_image: float | None = None
    setup_usd: float = 0.0       # one-off cost, e.g. style-LoRA training
    openrouter: str = ""         # slug on the unified image API; empty means unreachable there
    openrouter_usd: float = 0.0
    licence: str = "vendor terms"
    commercial: bool = True      # False means its output may not appear in the book
    parameters: str = ""
    fits_gb: int = 0             # unified memory a local model needs; 0 for hosted
    prompt_tokens: int = 0       # text-encoder ceiling; 0 means none known
    seconds_per_image: float = 0.0
    command: tuple[str, ...] = ()
    local_url: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def local(self) -> bool:
        return self.build in ("command", "http")

    def auth(self, route: str) -> str | None:
        """The key this route needs; local models need none, so they answer yes."""
        if route == "local":
            return "local"
        return os.environ.get(OPENROUTER_ENV if route == "openrouter" else self.auth_env) or None

    def routes(self, route: str) -> bool:
        """Whether this candidate can be reached at all on the given route."""
        if route == "local":
            return self.local
        if self.local:
            return False
        if route == "openrouter":
            return bool(self.openrouter)
        return bool(self.build) and self.build != "openrouter-only"

    def installed(self) -> bool:
        """For a command-backed model, whether its binary is on PATH."""
        return bool(self.command) and shutil.which(self.command[0]) is not None

    def unit_usd(self, route: str = "direct") -> float:
        if route == "local":
            return 0.0            # electricity, and the wall clock below
        if route == "openrouter":
            return self.openrouter_usd or self.usd_per_image
        return self.batch_usd_per_image or self.usd_per_image

    def full_book_hours(self, seconds: float | None = None) -> float:
        """The other price of a local model: how long the whole book takes."""
        rate = seconds if seconds is not None else self.seconds_per_image
        return (PANEL_SLOTS + PAGE_SLOTS) * ATTEMPTS_PER_SLOT * rate / 3600

    def full_book_usd(self, route: str = "direct") -> float:
        slots = PANEL_SLOTS + PAGE_SLOTS
        return self.setup_usd + slots * ATTEMPTS_PER_SLOT * self.unit_usd(route)


PROVIDERS: tuple[Provider, ...] = (
    Provider(
        id="gemini-3-pro-image",
        label="Gemini 3 Pro Image (Nano Banana Pro)",
        vendor="Google",
        tier="premium",
        usd_per_image=0.134,
        batch_usd_per_image=0.067,
        auth_env="GEMINI_API_KEY",
        build="gemini",
        model="gemini-3-pro-image",
        endpoint="https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        openrouter="google/gemini-3-pro-image",
        openrouter_usd=0.134,
        strengths="native multi-reference conditioning; the strongest control we have over "
                  "reusing an established environment across separate calls",
        risks="closed weights that can move under a 112-page book; highest unit price; "
              "eager to render legible interface text unless pushed hard",
    ),
    Provider(
        id="gpt-image",
        label="GPT Image 2",
        vendor="OpenAI",
        tier="premium",
        usd_per_image=0.165,        # widescreen at high quality; medium is $0.041
        auth_env="OPENAI_API_KEY",
        build="openai",
        model="gpt-image-2",
        endpoint="https://api.openai.com/v1/images/generations",
        openrouter="openai/gpt-image-2",
        openrouter_usd=0.165,
        strengths="best long-prompt instruction following; holds compound negative "
                  "constraints such as no face, no logo, no readable text",
        risks="the most expensive candidate at the quality tier a printed book needs; "
              "renders confident legible text unprompted; flattens brush texture",
    ),
    Provider(
        id="flux-2-pro",
        label="FLUX.2 [pro]",
        vendor="Black Forest Labs",
        tier="balanced",
        usd_per_image=0.050,
        auth_env="FAL_KEY",
        build="fal",
        model="fal-ai/flux-2-pro",
        endpoint="https://fal.run/{model}",
        openrouter="black-forest-labs/flux.2-pro",
        openrouter_usd=0.029,       # $0.03 per megapixel; a 1200x800 panel is 0.96 MP
        strengths="the closest default to hand-inked contour, dry-brush abrasion, and "
                  "heavy blacks; plausible rack and cable-tray geometry",
        risks="no trained style lock at this tier, so register drift must be caught by review",
    ),
    Provider(
        id="flux-2-dev-lora",
        label="FLUX.2 [dev] + trained style LoRA",
        vendor="Black Forest Labs (via fal)",
        tier="volume",
        usd_per_image=0.021,        # $0.021 per megapixel; a 1200x800 panel is 0.96 MP
        setup_usd=32.0,             # ~4000 training steps at $0.008
        auth_env="FAL_KEY",
        build="fal",
        model="fal-ai/flux-2/lora",
        endpoint="https://fal.run/{model}",
        strengths="one trained style locks ink, palette, and register across all 541 panels; "
                  "open weights and fixed seeds make any panel reproducible years later",
        risks="needs an approved ink and texture reference sheet before it can be trained; "
              "a bad training set bakes a bad style into the whole book; the only candidate "
              "no aggregator can host, because the weights are ours",
        extra={"loras": []},
    ),
    Provider(
        id="imagen-4",
        label="Imagen 4 Standard",
        vendor="Google",
        tier="balanced",
        usd_per_image=0.040,
        auth_env="GEMINI_API_KEY",
        build="imagen",
        model="imagen-4.0-generate-001",
        endpoint="https://generativelanguage.googleapis.com/v1beta/models/{model}:predict",
        strengths="clean photographic light logic; cheap to sweep at Fast tier",
        risks="pulls toward polished render rather than printed ink; weak halftone and grain",
    ),
    Provider(
        id="seedream",
        label="Seedream 4.5",
        vendor="ByteDance",
        tier="balanced",
        usd_per_image=0.040,
        auth_env="REPLICATE_API_TOKEN",
        build="replicate",
        model="bytedance/seedream-4",
        endpoint="https://api.replicate.com/v1/models/{model}/predictions",
        openrouter="bytedance-seed/seedream-4.5",
        openrouter_usd=0.040,
        strengths="strong composition at low cost; handles dark, low-key frames without mud",
        risks="least predictable on Western comic ink; limited negative-prompt control",
    ),
    Provider(
        id="grok-imagine",
        label="Grok Imagine (quality)",
        vendor="xAI",
        tier="balanced",
        usd_per_image=0.050,
        auth_env="XAI_API_KEY",
        build="openrouter-only",
        openrouter="x-ai/grok-imagine-image-quality",
        openrouter_usd=0.050,
        strengths="grainier, less corporate default than the Google and OpenAI models, "
                  "which is the direction this book's register wants",
        risks="least documented behaviour of the roster; carried because the aggregator "
              "makes trying it nearly free rather than because it is a favourite",
    ),
    Provider(
        id="qwen-image",
        label="Qwen-Image",
        vendor="Alibaba (via fal)",
        tier="volume",
        usd_per_image=0.006,
        auth_env="FAL_KEY",
        build="fal",
        model="fal-ai/qwen-image",
        endpoint="https://fal.run/{model}",
        strengths="cheap enough to use as a layout and framing sweep before committing "
                  "a panel to a premium model",
        risks="not a finish-quality candidate for this style; treat as blocking only",
    ),
)

def local_providers() -> tuple[Provider, ...]:
    """Read the editable local roster, so tooling churn stays out of Python."""
    if not LOCAL_MODELS.is_file():
        return ()
    record = json.loads(LOCAL_MODELS.read_text(encoding="utf-8"))
    built = []
    for entry in record.get("models", ()):
        backend = entry.get("backend", "command")
        built.append(Provider(
            id=entry["id"],
            label=entry["label"],
            vendor=entry["vendor"],
            tier=entry.get("tier", "local"),
            usd_per_image=0.0,
            auth_env="",
            strengths=entry.get("strengths", ""),
            risks=entry.get("risks", ""),
            build=backend,
            model=entry.get("model", ""),
            licence=entry.get("licence", "unstated"),
            commercial=bool(entry.get("commercial", False)),
            parameters=entry.get("parameters", ""),
            fits_gb=int(entry.get("fits_gb", 0)),
            prompt_tokens=int(entry.get("prompt_tokens", 0)),
            seconds_per_image=float(entry.get("seconds_per_image", 0)),
            command=tuple(entry.get("command", ())),
            local_url=entry.get("url", ""),
            extra={"steps": entry.get("steps"), "footprint_gb": entry.get("footprint_gb"),
                   "output_suffix": entry.get("output_suffix")},
        ))
    return tuple(built)


LOCAL = local_providers()
ALL_PROVIDERS: tuple[Provider, ...] = PROVIDERS + LOCAL
PROVIDERS_BY_ID = {provider.id: provider for provider in ALL_PROVIDERS}


# --------------------------------------------------------------- the bake-off


@dataclass(frozen=True)
class Sample:
    """One panel chosen to stress a specific thing the book needs."""

    page: str
    panel: int
    register: str
    tests: str

    @property
    def id(self) -> str:
        return f"{self.page}-{self.panel:02d}"


SAMPLES: tuple[Sample, ...] = (
    Sample("001", 1, "incident",
           "near-black data-center aisle, plausible rack and cable-tray perspective, "
           "one steel practical light, no figure"),
    Sample("001", 2, "incident",
           "abstract dependency diagram that must read causally while staying "
           "visibly non-semantic"),
    Sample("013", 1, "creator",
           "the only register with a real human figure: nicotine light, ordinary "
           "clothes, monitors that must stay unreadable"),
    Sample("026", 1, "institutional",
           "overlit procedural room, distributed responsibility, no villain lighting"),
    Sample("070", 1, "dossier",
           "paper field, strict two-column grid, reserved blank lettering fields"),
    Sample("110", 1, "invented future",
           "fully desaturated, organization-neutral, no incident palette signature"),
)

# Two rubric lines are gates rather than weights: a candidate below the floor on
# either is unusable for a 541-panel book however well it scores elsewhere.
GATED = ("text", "continuity")
GATE_FLOOR = 3

RUBRIC: tuple[tuple[str, str, int], ...] = (
    ("ink", "Hand-inked contour, dry-brush abrasion, heavy blacks, paper grain", 3),
    ("palette", "Stays inside design/palette.md; no unearned moss, claret, or amber", 2),
    ("text", "The panel's own display strings are legible and correctly spelled, with no "
             "invented lettering anywhere else", 3),
    ("geometry", "Racks, trays, rooms, and perspective survive a second look", 2),
    ("continuity", "Repeats of the same prompt stay in one style and one place", 3),
    ("control", "Responds to correction rather than re-rolling a different picture", 2),
)


# ------------------------------------------------------------ prompt assembly


# A text encoder does not reject a prompt that is too long for it; it encodes
# the front and silently drops the rest. FLUX.2 is pinned to 512 tokens by
# mflux, and a composed panel prompt runs to about 1,060 — so slightly over
# half of every prompt, including the whole palette clause and the entire
# negative prompt, never reached the model. Nothing said so. Sections are
# therefore ranked and fitted to the budget here, and whatever will not fit is
# dropped whole and reported, rather than being cut off mid-sentence.

_TOKEN_PIECE = re.compile(r"[A-Za-z]+|\d+|[^\sA-Za-z\d]")
PROMPT_OVERHEAD = 8                   # chat template and delimiters, charged once


def _token_pieces(text: str) -> int:
    total = 0
    for piece in _TOKEN_PIECE.findall(text):
        if piece[0].isalpha():
            total += max(1, math.ceil(len(piece) / 6))
        elif piece[0].isdigit():
            total += len(piece)       # digits rarely merge into one token
        else:
            total += 1
    return total


def estimate_tokens(text: str) -> int:
    """A deliberate overestimate of what a byte-pair tokenizer makes of `text`.

    Measured against the Qwen3 tokenizer FLUX.2 uses, over 220 composed prompts
    and their sections: never under, median 1.22x over. Overestimating is the
    safe direction, because its cost is a little unused budget while
    underestimating restores the silent truncation this exists to prevent.
    Deliberately pure Python: counting tokens must not need a model download.

    The template overhead is a property of the whole prompt, not of each block
    in it, so `Section.tokens` leaves it out and `fit_sections` charges it once.
    """
    return _token_pieces(text) + PROMPT_OVERHEAD


@dataclass(frozen=True)
class Section:
    """One labelled block of a prompt, and how hard it fights to stay in.

    `rank` is what survives a tight budget, lowest first. The order of the list
    is what the model reads; the two are deliberately different, so a section
    can be late in the prompt and still outrank an earlier one.
    """

    name: str
    text: str
    rank: int
    compact: str = ""            # shorter wording to fall back to; "" means none

    @property
    def tokens(self) -> int:
        return _token_pieces(self.text)

    @property
    def compact_tokens(self) -> int:
        return _token_pieces(self.compact) if self.compact else 0

    def at(self, text: str) -> "Section":
        return Section(self.name, text, self.rank, self.compact)


def prompt_sections(page: str, panel: int, register: str) -> list[Section]:
    """Every candidate block for one panel's prompt, in reading order.

    Ranking, and why: the panel's own direction and its display strings are the
    only parts that differ between panels, so they outrank everything generic.
    The register clause is twenty tokens that decide which world the panel is
    in. The rendering target carries the ink identity, without which the book
    stops looking like itself. The palette is next because dropping it is
    visible as colour outside the book's range. Composition and the negative
    prompt rank last because they are the two largest blocks, and because a
    command backend with no negative-prompt channel receives the negatives as
    ordinary prompt text, where measurement shows they change nothing.
    """
    style = PROMPT_DIR / "global-style.md"

    def block(heading: str, rank: int) -> Section:
        """A global-style section, plus its `## <heading> (compact)` form if written."""
        return Section(heading.lower(), _digest(style, heading), rank,
                       _digest(style, f"{heading} (compact)"))

    return [
        block("Rendering target", 4),
        Section("register", f"Register — {register}: {register_clause(register)}", 3),
        Section("panel", f"Panel — {panel_direction(page, panel)}", 1),
        Section("exact text", exact_text_clause(page, panel), 2),
        block("Composition", 7),
        block("Light and material", 6),
        Section("palette", f"Palette, and nothing outside it: {palette_clause()}.", 5,
                _digest(style, "Palette (compact)")),
        block("Output discipline", 8),
        Section("avoid", f"Avoid entirely: {negative_prompt()}", 9,
                _digest(PROMPT_DIR / "negative-prompt.md", "Compact")),
    ]


def _trim_to_sentences(text: str, budget: int) -> str:
    """Cut `text` back to whole sentences that fit, never mid-clause."""
    sentences = re.split(r"(?<=[.!?]) +", text)
    kept: list[str] = []
    for sentence in sentences:
        if _token_pieces(" ".join(kept + [sentence])) > budget:
            break
        kept.append(sentence)
    return " ".join(kept)


def fit_sections(sections: list[Section], budget: int) -> tuple[list[Section], list[Section]]:
    """Choose the sections that fit, best rank first, and report the rest.

    Reading order is preserved for whatever survives. A budget too small even
    for the highest-ranked section leaves that one trimmed to whole sentences,
    because a panel with no direction is not worth generating.
    """
    present = [(index, section) for index, section in enumerate(sections) if section.text]
    if budget <= 0:
        return [section for _, section in present], []
    budget = max(0, budget - PROMPT_OVERHEAD)
    kept: list[tuple[int, Section]] = []
    dropped: list[Section] = []
    spent = 0
    for index, section in sorted(present, key=lambda pair: (pair[1].rank, pair[1].tokens)):
        if spent + section.tokens <= budget:
            kept.append((index, section))
            spent += section.tokens
        elif section.compact and spent + section.compact_tokens <= budget:
            kept.append((index, section.at(section.compact)))
            spent += section.compact_tokens
        elif not kept:
            trimmed = section.at(_trim_to_sentences(section.text, budget))
            kept.append((index, trimmed))
            spent = trimmed.tokens
        else:
            dropped.append(section)
    kept.sort(key=lambda pair: pair[0])
    return [section for _, section in kept], dropped


def budget_for(provider: "Provider | None") -> int:
    """The prompt ceiling to compose against; 0 means compose without one."""
    return provider.prompt_tokens if provider is not None else 0


def _digest(path: Path, heading: str) -> str:
    """Pull one `## heading` section out of a prompt document as flat prose."""
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(heading)}\s*\n+(.*?)(?=^## |\Z)", source, re.M | re.S)
    body = match.group(1) if match else ""
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"^[-*]\s+", "", body, flags=re.M)
    body = body.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", body).strip()


def palette_clause() -> str:
    """Name every canonical color with its hex so no model has to guess."""
    rows = re.findall(r"^\|\s*`([a-z0-9-]+)`\s*\|\s*`(#[0-9A-Fa-f]{6})`",
                      PALETTE_FILE.read_text(encoding="utf-8"), re.M)
    return ", ".join(f"{token} {value}" for token, value in rows)


def negative_prompt() -> str:
    source = (PROMPT_DIR / "negative-prompt.md").read_text(encoding="utf-8")
    body = re.sub(r"^#.*$", "", source, flags=re.M).replace("`", "")
    return re.sub(r"\s+", " ", body).strip()


def register_clause(register: str) -> str:
    modifiers = _digest(PROMPT_DIR / "global-style.md", "Register modifiers")
    match = re.search(rf"{re.escape(register)}:\s*([^.]+\.)", modifiers, re.I)
    return match.group(1).strip() if match else ""


def display_strings(page: str, panel: int) -> list[str]:
    """The exact words this panel's art is meant to show.

    Page scripts mark display text with backticks in the `Frame` and `Action`
    lines. `textimage` strips the backticks when it flattens a panel for a
    placeholder, so the literals are read here from the source instead, and
    handed to the model as an explicit list rather than left buried in prose.

    These are project-authored strings. `research/exact-text-permissions-audit.md`
    records that distributed pages paraphrase rather than quote their sources, so
    rendering them carries no reuse question.
    """
    source = (PAGE_DIR / f"{page}.md").read_text(encoding="utf-8")
    sections = re.split(r"^## Panel \d+\s*$", source, flags=re.M)[1:]
    if panel > len(sections):
        return []
    body = re.split(r"^\*\*(?:Caption|Dialogue|Left dialogue|Right dialogue|Screen|"
                    r"Provenance|Qualification)", sections[panel - 1], flags=re.M)[0]
    seen: list[str] = []
    for literal in re.findall(r"`([^`]+)`", body):
        literal = literal.strip()
        # Palette tokens are direction, not lettering the panel displays.
        if literal and literal not in seen and not re.fullmatch(r"[a-z]+-\d+|[a-z-]{3,12}", literal):
            seen.append(literal)
    return seen


def panel_direction(page: str, panel: int) -> str:
    """The panel's own direction: a hand-written prompt file, else its script."""
    written = PROMPT_DIR / "pages" / page / f"panel-{panel:02d}.md"
    if written.is_file():
        body = re.sub(r"^#.*$", "", written.read_text(encoding="utf-8"), flags=re.M)
        return re.sub(r"\s+", " ", body.replace("`", "")).strip()

    script = textimage.page_script(page)
    for candidate in script.panels:
        if candidate.index == panel:
            wanted = ("FRAME", "ACTION")
            kept = [
                line.split("—", 1)[1].strip()
                for line in candidate.text.splitlines()
                if line.split("—", 1)[0].strip().rstrip(":").upper() in wanted
            ]
            return " ".join(kept).strip()
    raise SystemExit(f"Page {page} has no panel {panel}.")


def exact_text_clause(page: str, panel: int) -> str:
    """Tell the model exactly which words to letter, and to spell them correctly."""
    strings = display_strings(page, panel)
    if not strings:
        return ""
    quoted = "; ".join(f'"{item}"' for item in strings)
    return (f"Lettering shown inside the scene — render these exact words, correctly "
            f"spelled, legible at reading size, and nothing else in their place: {quoted}. "
            f"Leave any other surface blank rather than inventing words for it.")


def compose_panel(page: str, panel: int, register: str, *, budget: int = 0) -> str:
    """Build the prompt for any panel in the book, from the canonical sources.

    `budget` is the model's text-encoder ceiling in tokens. The default of 0
    composes everything, which is what a model with room for it should get;
    pass a provider's `prompt_tokens` to compose against a real limit instead
    of letting the encoder cut the tail off unannounced.
    """
    kept, _ = fit_sections(prompt_sections(page, panel, register), budget)
    return "\n\n".join(section.text for section in kept)


def compose_panel_fit(page: str, panel: int, register: str, *, budget: int = 0
                      ) -> tuple[str, list[Section], list[Section]]:
    """`compose_panel`, and the accounting of what was kept and what was cut."""
    kept, dropped = fit_sections(prompt_sections(page, panel, register), budget)
    return "\n\n".join(section.text for section in kept), kept, dropped


def compose(sample: Sample, *, budget: int = 0) -> str:
    """The bake-off's prompt for one sample panel."""
    return compose_panel(sample.page, sample.panel, sample.register, budget=budget)


# ---------------------------------------------------------------- the callers


@dataclass(frozen=True)
class Generated:
    """What came back from one call: the image, its suffix, and what it cost."""

    data: bytes
    suffix: str
    usd: float | None = None      # None means the vendor did not report a figure


def _post(url: str, body: dict, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _get(url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:
        return response.read()


def openrouter_models(key: str) -> dict[str, dict]:
    """Ask the aggregator which image models it can actually route right now."""
    payload = _get(OPENROUTER_MODELS, {"Authorization": f"Bearer {key}"})
    records = payload.get("data", payload if isinstance(payload, list) else [])
    return {record["id"]: record for record in records if isinstance(record, dict) and "id" in record}


def generate_openrouter(provider: Provider, prompt: str, key: str, image_format: str) -> Generated:
    """One call through the unified image API, which reports its own cost."""
    payload = _post(OPENROUTER_IMAGES, {
        "model": provider.openrouter,
        "prompt": prompt,
        "aspect_ratio": PANEL_ASPECT,
        "output_format": image_format,
        "n": 1,
    }, {"Authorization": f"Bearer {key}"})

    record = payload["data"][0]
    suffix = MEDIA_SUFFIXES.get(record.get("media_type", ""), SUFFIXES[image_format])
    if "b64_json" in record:
        data = base64.b64decode(record["b64_json"])
    elif record.get("url"):
        data = _fetch(record["url"])
    else:
        raise RuntimeError("OpenRouter returned neither b64_json nor url")
    usage = payload.get("usage") or {}
    return Generated(data, suffix, usage.get("cost"))


def generate_command(provider: Provider, prompt: str, seed: int,
                     size: tuple[int, int] | None = None) -> Generated:
    """Run a local generator binary and read back the file it wrote.

    The argv comes from `data/local-models.json` and is executed with no shell,
    so a prompt containing quotes, backticks, or newlines is passed through as
    one argument rather than being reinterpreted.
    """
    if not provider.installed():
        raise RuntimeError(f"{provider.command[0]} is not on PATH")

    width, height = size or PANEL_SIZE
    with tempfile.TemporaryDirectory() as workspace:
        target = Path(workspace) / f"out{provider.extra.get('output_suffix') or '.png'}"
        # A composed panel prompt is about 4 KB. Most local runners accept a file,
        # which keeps it off the argument list and out of any process listing.
        prompt_file = Path(workspace) / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        argv = [
            part.format(prompt=prompt, prompt_file=prompt_file, width=width, height=height,
                        seed=seed, steps=provider.extra.get("steps") or 20, output=target)
            for part in provider.command
        ]
        try:
            finished = subprocess.run(argv, capture_output=True, text=True,
                                      timeout=LOCAL_TIMEOUT, check=False)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"timed out after {LOCAL_TIMEOUT}s") from None
        if finished.returncode != 0:
            tail = (finished.stderr or finished.stdout or "").strip().splitlines()
            raise RuntimeError(f"exit {finished.returncode}: {tail[-1] if tail else 'no output'}")
        if not target.is_file():
            raise RuntimeError(f"{argv[0]} exited cleanly but wrote no file to {target}")
        return Generated(target.read_bytes(), target.suffix)


def generate_local_http(provider: Provider, prompt: str, seed: int,
                        size: tuple[int, int] | None = None) -> Generated:
    """Ask a local image server for one panel, in the OpenAI images shape.

    Draw Things, ComfyUI behind a bridge, and LocalAI all speak some variant of
    this, so the response is read defensively rather than assuming one field.
    """
    width, height = size or PANEL_SIZE
    try:
        payload = _post(provider.local_url, {
            "model": provider.model,
            "prompt": prompt,
            "width": width,
            "height": height,
            "size": f"{width}x{height}",
            "steps": provider.extra.get("steps") or 30,
            "seed": seed,
            "n": 1,
        }, {})
    except urllib.error.URLError as error:
        raise RuntimeError(f"no local server at {provider.local_url} ({error.reason})") from None

    records = payload.get("data") or payload.get("images") or []
    if not records:
        raise RuntimeError(f"local server returned no image: {str(payload)[:200]}")
    record = records[0]
    if isinstance(record, str):                      # some servers return bare base64
        return Generated(base64.b64decode(record), ".png")
    if record.get("b64_json"):
        return Generated(base64.b64decode(record["b64_json"]), ".png")
    if record.get("url"):
        return Generated(_fetch(record["url"]), ".png")
    raise RuntimeError("local server returned neither base64 nor a url")


def generate(provider: Provider, prompt: str, seed: int, *,
             route: str = "direct", image_format: str = DEFAULT_FORMAT,
             size: tuple[int, int] | None = None) -> Generated:
    """Send one prompt to one provider and return the image and what it cost."""
    if route == "local" or provider.local:
        if provider.build == "command":
            return generate_command(provider, prompt, seed, size)
        return generate_local_http(provider, prompt, seed, size)

    key = provider.auth(route)
    if not key:
        raise RuntimeError(f"{OPENROUTER_ENV if route == 'openrouter' else provider.auth_env} is not set")

    if route == "openrouter":
        if not provider.openrouter:
            raise RuntimeError(f"{provider.id} has no OpenRouter slug")
        return generate_openrouter(provider, prompt, key, image_format)

    width, height = size or PANEL_SIZE
    if not provider.build or provider.build == "openrouter-only":
        raise RuntimeError(f"{provider.id} is reachable through OpenRouter only")
    endpoint = provider.endpoint.format(model=provider.model)

    if provider.build == "openai":
        payload = _post(endpoint, {
            "model": provider.model,
            "prompt": prompt,
            "size": "1536x1024",
            "quality": "high",
            "n": 1,
        }, {"Authorization": f"Bearer {key}"})
        return Generated(base64.b64decode(payload["data"][0]["b64_json"]), ".png")

    if provider.build == "gemini":
        payload = _post(f"{endpoint}?key={key}", {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": PANEL_ASPECT},
            },
        }, {})
        for part in payload["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                return Generated(base64.b64decode(part["inlineData"]["data"]), ".png")
        raise RuntimeError("Gemini returned no image part")

    if provider.build == "imagen":
        payload = _post(f"{endpoint}?key={key}", {
            "instances": [{"prompt": prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": PANEL_ASPECT},
        }, {})
        return Generated(base64.b64decode(payload["predictions"][0]["bytesBase64Encoded"]), ".png")

    if provider.build == "fal":
        payload = _post(endpoint, {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "num_images": 1,
            "seed": seed,
            **provider.extra,
        }, {"Authorization": f"Key {key}"})
        return Generated(_fetch(payload["images"][0]["url"]), ".png")

    if provider.build == "replicate":
        payload = _post(endpoint, {
            "input": {"prompt": prompt, "width": width, "height": height, "seed": seed},
        }, {"Authorization": f"Bearer {key}", "Prefer": "wait"})
        output = payload.get("output")
        url = output[0] if isinstance(output, list) else output
        if not url:
            raise RuntimeError(f"Replicate returned {payload.get('status')}: {payload.get('error')}")
        return Generated(_fetch(url), ".png")

    raise RuntimeError(f"Unknown request shape {provider.build!r}")


def placeholder(provider: Provider, sample: Sample, prompt: str, seed: int, route: str) -> Generated:
    """A dry-run stand-in carrying the exact prompt that would have been sent."""
    document = textimage.text_image(
        prompt,
        *PANEL_SIZE,
        label=f"{provider.label.upper()} · {sample.id} · SEED {seed}",
        footer=f"DRY RUN · {sample.register.upper()} · "
               f"${provider.unit_usd(route):.3f} PER IMAGE VIA {route.upper()}",
        title=f"Dry-run prompt for {sample.id} on {provider.label}",
    )
    return Generated(document.encode("utf-8"), ".svg", 0.0)


# ------------------------------------------------------------------- the run


def selected(ids: list[str] | None) -> list[Provider]:
    if not ids:
        return list(ALL_PROVIDERS)
    missing = [name for name in ids if name not in PROVIDERS_BY_ID]
    if missing:
        raise SystemExit(f"Unknown provider(s): {', '.join(missing)}. "
                         f"Known: {', '.join(PROVIDERS_BY_ID)}")
    return [PROVIDERS_BY_ID[name] for name in ids]


def chosen_samples(ids: list[str] | None) -> list[Sample]:
    if not ids:
        return list(SAMPLES)
    by_id = {sample.id: sample for sample in SAMPLES}
    missing = [name for name in ids if name not in by_id]
    if missing:
        raise SystemExit(f"Unknown sample panel(s): {', '.join(missing)}. "
                         f"Known: {', '.join(by_id)}")
    return [by_id[name] for name in ids]


def log_generation(record: dict) -> None:
    GENERATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with GENERATION_LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def run_samples(
    directory: Path,
    providers: list[Provider],
    samples: list[Sample],
    *,
    repeat: int,
    dry_run: bool,
    route: str = "direct",
    image_format: str = DEFAULT_FORMAT,
    allow_non_commercial: bool = False,
) -> dict:
    """Send every sample prompt to every provider and record what came back.

    Every candidate is sent the same prompt, which is the point of a bake-off.
    That only means anything if each of them can actually read all of it, so
    the prompt is composed against the tightest text-encoder limit in the
    field: comparing models on a prompt one of them silently halves compares
    nothing. Candidates with no recorded limit do not constrain the others.
    """
    directory.mkdir(parents=True, exist_ok=True)
    limits = [provider.prompt_tokens for provider in providers if provider.prompt_tokens]
    budget = min(limits) if limits else 0
    if budget:
        print(f"  prompt budget: {budget} tokens, the tightest encoder in this field")
    prompts = {sample.id: compose(sample, budget=budget) for sample in samples}
    (directory / "prompts").mkdir(exist_ok=True)
    for sample in samples:
        (directory / "prompts" / f"{sample.id}.txt").write_text(prompts[sample.id], encoding="utf-8")

    ran: list[Provider] = []
    results: list[dict] = []
    spend = 0.0
    for provider in providers:
        if not provider.routes(route):
            print(f"  skip {provider.id}: not reachable on the {route} route")
            continue
        if not provider.commercial and not allow_non_commercial:
            print(f"  skip {provider.id}: {provider.licence} forbids shipping its output; "
                  f"pass --allow-non-commercial to score it anyway")
            continue
        if provider.build == "command" and not dry_run and not provider.installed():
            print(f"  skip {provider.id}: {provider.command[0]} is not on PATH")
            continue
        if not dry_run and not provider.auth(route):
            print(f"  skip {provider.id}: "
                  f"{OPENROUTER_ENV if route == 'openrouter' else provider.auth_env} is not set")
            continue
        ran.append(provider)
        (directory / provider.id).mkdir(exist_ok=True)
        for sample in samples:
            for take in range(1, repeat + 1):
                seed = 1000 + take
                name = f"{sample.id}-{take}"
                started = time.time()
                try:
                    made = (
                        placeholder(provider, sample, prompts[sample.id], seed, route)
                        if dry_run else
                        generate(provider, prompts[sample.id], seed,
                                 route=route, image_format=image_format)
                    )
                except (urllib.error.URLError, RuntimeError, KeyError, IndexError, ValueError) as error:
                    print(f"  fail {provider.id} {name}: {error}")
                    results.append({
                        "provider": provider.id, "sample": sample.id, "take": take,
                        "seed": seed, "error": str(error), "path": None,
                    })
                    continue

                relative = f"{provider.id}/{name}{made.suffix}"
                (directory / relative).write_bytes(made.data)
                elapsed = round(time.time() - started, 2)
                cost = 0.0 if dry_run else (
                    made.usd if made.usd is not None else provider.unit_usd(route))
                spend += cost
                results.append({
                    "provider": provider.id, "sample": sample.id, "take": take,
                    "seed": seed, "path": relative, "seconds": elapsed,
                    "usd": round(cost, 5), "metered": made.usd is not None,
                    "bytes": len(made.data),
                })
                if not dry_run:
                    log_generation({
                        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "purpose": "generator-bake-off",
                        "route": route,
                        "provider": provider.id,
                        "model": provider.openrouter if route == "openrouter" else (provider.model or provider.id),
                        "page": sample.page,
                        "panel": sample.panel,
                        "seed": seed,
                        "usd": round(cost, 5),
                        "path": str((directory / relative).relative_to(ROOT)),
                    })
                print(f"  {provider.id:<20} {name}  {elapsed:>6.2f}s  ${cost:.4f}  "
                      f"{len(made.data) // 1024:>5} KB")

    manifest = {
        "run": directory.name,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "route": route,
        "dry_run": dry_run,
        "repeat": repeat,
        "panel_size": list(PANEL_SIZE),
        "providers": [provider.id for provider in ran],
        "evaluation_only": sorted(provider.id for provider in ran if not provider.commercial),
        "samples": [
            {"id": sample.id, "register": sample.register, "tests": sample.tests}
            for sample in samples
        ],
        "rubric": [{"key": key, "question": question, "weight": weight}
                   for key, question, weight in RUBRIC],
        "results": results,
        "usd": round(spend, 4),
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_scores_template(directory, ran)
    return manifest


def write_scores_template(directory: Path, providers: list[Provider]) -> None:
    """A blank scorecard the reviewer fills in; `rank` reads it back."""
    path = directory / "scores.tsv"
    if path.exists():
        return
    header = ["provider", *(key for key, _, _ in RUBRIC), "notes"]
    lines = ["\t".join(header)]
    lines += ["\t".join([provider.id, *("" for _ in RUBRIC), ""]) for provider in providers]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------ the comparison


def load_manifest(directory: Path) -> dict:
    return json.loads((directory / "manifest.json").read_text(encoding="utf-8"))


def run_directories(base: Path) -> list[Path]:
    return sorted(path for path in base.glob("*") if (path / "manifest.json").is_file())


def median_seconds(manifest: dict) -> dict[str, float]:
    """Measured seconds per image per provider, which beats any estimate.

    A dry run measures the placeholder writer, not the model, so it reports
    nothing and the roster's own estimate stands.
    """
    if manifest.get("dry_run"):
        return {}
    timings: dict[str, list[float]] = {}
    for result in manifest.get("results", ()):
        if result.get("seconds"):
            timings.setdefault(result["provider"], []).append(result["seconds"])
    medians = {}
    for name, values in timings.items():
        values.sort()
        medians[name] = values[len(values) // 2]
    return medians


def sheet_body(manifest: dict, *, prefix: str = "") -> str:
    """The comparison itself, reusable inside the site shell or a bare page.

    `prefix` is prepended to every asset path, so the same markup works whether
    the images sit beside the page or under the published `assets/` tree.
    """
    by_key: dict[tuple[str, str], list[dict]] = {}
    for result in manifest["results"]:
        by_key.setdefault((result["sample"], result["provider"]), []).append(result)

    providers = [PROVIDERS_BY_ID[name] for name in manifest["providers"]]
    route = manifest.get("route", "direct")
    escape = html.escape

    head = "".join(
        f'<th><div class="bakeoff__name">{escape(provider.label)}</div>'
        f'<div class="bakeoff__meta">{escape(provider.vendor)} · {escape(provider.tier)} · '
        f'${provider.unit_usd(route):.3f}/image</div></th>'
        for provider in providers
    )

    rows = []
    for sample in manifest["samples"]:
        cells = []
        for provider in providers:
            takes = sorted(by_key.get((sample["id"], provider.id), []), key=lambda item: item["take"])
            if not takes:
                cells.append('<td class="bakeoff__empty">not run</td>')
                continue
            frames = []
            for take in takes:
                if take.get("path"):
                    source = escape(prefix + take["path"])
                    frames.append(
                        f'<a href="{source}"><img src="{source}" loading="lazy" '
                        f'alt="{escape(provider.label)} take {take["take"]} of panel '
                        f'{escape(sample["id"])}: {escape(sample["tests"])}"></a>'
                    )
                else:
                    frames.append(f'<p class="bakeoff__error">{escape(take.get("error", "failed"))}</p>')
            cells.append(f'<td>{"".join(frames)}</td>')
        rows.append(
            f'<tr><th class="bakeoff__sample"><div class="bakeoff__name">{escape(sample["id"])}</div>'
            f'<div class="bakeoff__meta">{escape(sample["register"])}</div>'
            f'<p>{escape(sample["tests"])}</p>'
            f'<p><a href="{escape(prefix)}prompts/{escape(sample["id"])}.txt">prompt</a></p></th>'
            f'{"".join(cells)}</tr>'
        )

    rubric = "".join(
        f"<li><b>{escape(item['key'])}</b> (weight {item['weight']}) — {escape(item['question'])}</li>"
        for item in manifest["rubric"]
    )

    measured = median_seconds(manifest)

    def book_cost(provider: Provider) -> str:
        if provider.local:
            hours = provider.full_book_hours(measured.get(provider.id))
            return f"{hours:,.0f} h"
        return f"${provider.full_book_usd(route):,.0f}"

    def licence_cell(provider: Provider) -> str:
        if provider.commercial:
            return escape(provider.licence)
        return f'<b class="bakeoff__error">{escape(provider.licence)}</b><br>evaluation only'

    notes = "".join(
        f'<tr><td>{escape(provider.label)}'
        f'{f"<br><span class=\'bakeoff__meta\'>{escape(provider.parameters)}</span>" if provider.parameters else ""}</td>'
        f'<td>{licence_cell(provider)}</td>'
        f'<td>{escape(provider.strengths)}</td>'
        f'<td>{escape(provider.risks)}</td>'
        f'<td class="bakeoff__num">{book_cost(provider)}</td></tr>'
        for provider in providers
    )

    warning = ""
    if manifest.get("evaluation_only"):
        names = ", ".join(PROVIDERS_BY_ID[name].label for name in manifest["evaluation_only"]
                          if name in PROVIDERS_BY_ID)
        warning = (f'<p class="bakeoff__warning"><b>Evaluation only.</b> {escape(names)} '
                   f'{"are" if len(manifest["evaluation_only"]) > 1 else "is"} generated from '
                   f'weights under a non-commercial licence. Score these columns to calibrate '
                   f'the rubric; nothing in them may appear in the book.</p>')

    mode = ("dry run — placeholders carry the prompt that would have been sent"
            if manifest["dry_run"] else f"live run — ${manifest['usd']:.2f} spent")

    return f"""{BAKEOFF_STYLE}
<div class="bakeoff">
<p class="bakeoff__meta">{escape(manifest['run'])} · {escape(manifest['at'])} ·
via {escape(route)} · {escape(mode)} · {manifest['repeat']} take(s) per panel at
{manifest['panel_size'][0]}×{manifest['panel_size'][1]}</p>
{warning}
<p>Every candidate received a byte-identical prompt composed from
<code>prompts/global-style.md</code>, <code>prompts/negative-prompt.md</code>,
<code>design/palette.md</code>, and the panel's own direction. The point of more than one
take per panel is drift: a candidate whose takes are the same place in the same style can
carry 541 panels, and one whose takes diverge cannot, however good either image is alone.</p>
<h2>Rubric</h2>
<ul>{rubric}</ul>
<div class="table-wrap"><table class="bakeoff__grid">
<thead><tr><th class="bakeoff__sample">Panel</th>{head}</tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>
<h2>Candidates</h2>
<div class="table-wrap"><table>
<thead><tr><th>Candidate</th><th>Licence</th><th>Why it might win</th>
<th>What it costs us</th><th class="bakeoff__num">Full book</th></tr></thead>
<tbody>{notes}</tbody>
</table></div>
<p class="bakeoff__meta">Full-book figures assume {PANEL_SLOTS} panels plus {PAGE_SLOTS} page
sheets at {ATTEMPTS_PER_SLOT} attempts per slot, plus any one-off setup. Hosted candidates are
priced in dollars; local ones cost nothing per image and are priced in wall clock instead,
measured from this run where it recorded one.</p>
</div>"""


BAKEOFF_STYLE = """<style>
/* A side-by-side comparison needs the width the reading column does not have. */
body:has(.bakeoff) .shell { width: min(1760px, calc(100% - 2rem)); }
.bakeoff__meta { color: var(--muted, #a9a398); font-size: .85rem; }
.bakeoff__name, .bakeoff__meta, .bakeoff__sample p {
  text-transform: none; letter-spacing: 0; font-weight: 400; }
.bakeoff__name { font-weight: 700; font-size: .95rem; }
.bakeoff__grid th.bakeoff__sample { width: 13rem; }
.bakeoff__grid th.bakeoff__sample p { font-size: .85rem; color: var(--muted, #a9a398); }
.bakeoff__grid td { min-width: 14rem; }
.bakeoff__grid img { width: 100%; display: block; margin-bottom: .4rem;
  background: var(--panel, #211f1b); border: 1px solid var(--line, #3e3931); }
.bakeoff__empty { color: var(--muted, #a9a398); }
.bakeoff__error { color: #d08a7a; font-size: .85rem; }
.bakeoff__num { text-align: right; white-space: nowrap; }\n.bakeoff__warning { padding: .75rem 1rem; border-left: 3px solid #d08a7a;\n  background: var(--panel, #211f1b); }
</style>"""


def sheet_html(manifest: dict) -> str:
    """A standalone page for reading a run before it is published."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Image generator bake-off — {html.escape(manifest['run'])}</title>
<style>
:root {{ color-scheme: dark; --ink: #f3efe5; --muted: #a9a398; --paper: #171613;
  --panel: #211f1b; --line: #3e3931; --accent: #f0a35b; }}
body {{ margin: 0; padding: 2rem; background: var(--paper); color: var(--ink);
  font: 15px/1.6 -apple-system, "Helvetica Neue", Arial, sans-serif; }}
h1 {{ font-size: 1.5rem; margin: 0 0 .25rem; }}
a {{ color: #8fd3c8; }}
code {{ padding: .15rem .3rem; background: var(--panel); }}
.table-wrap {{ margin: 1.5rem 0; overflow-x: auto; border: 1px solid var(--line); }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: .7rem .8rem; border-right: 1px solid var(--line);
  border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
thead th {{ color: var(--accent); background: var(--panel); }}
ul {{ max-width: 60rem; }}
</style>
</head>
<body>
<h1>Image generator bake-off</h1>
{sheet_body(manifest)}
</body>
</html>
"""


# ---------------------------------------------------------------------- CLI


def base_dir(args: argparse.Namespace) -> Path:
    return args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir


def resolve_run(args: argparse.Namespace) -> Path:
    base = base_dir(args)
    if getattr(args, "run", None):
        return base / args.run
    runs = run_directories(base)
    if not runs:
        raise SystemExit(f"No run with a manifest under {base}. Run `sample` first.")
    return runs[-1]


def cmd_providers(args: argparse.Namespace) -> int:
    route = args.via
    print(f"{'ID':<20} {'TIER':<10} {'FULL BOOK':>11}  {'READY':<9} "
          f"{'LICENCE':<28} VENDOR")
    for provider in ALL_PROVIDERS:
        if provider.local:
            book = f"{provider.full_book_hours():>9,.0f} h"
            ready = "yes" if provider.installed() else (
                "server" if provider.build == "http" else "install")
        else:
            # A hosted candidate keeps its own price whatever route is being listed.
            book = f"${provider.full_book_usd('direct' if route == 'local' else route):>10,.0f}"
            ready = "yes" if provider.auth(route) else "no key"
        if not provider.routes(route):
            ready = "n/a"
        licence = provider.licence if provider.commercial else f"{provider.licence} ✗"
        print(f"{provider.id:<20} {provider.tier:<10} {book:>11}  {ready:<9} "
              f"{licence:<28} {provider.vendor}")
    envs = sorted({provider.auth_env for provider in PROVIDERS if provider.auth_env} | {OPENROUTER_ENV})
    print(f"\nRoute: {route}. Keys are read from {', '.join(envs)}.")
    print("Local models need no key. 'server' means it wants a local endpoint running; "
      "'install' means its binary is not on PATH. ✗ marks a licence that forbids "
      "shipping the output.")
    print("Hosted candidates are priced in dollars, local ones in wall clock.")
    return 0


def cmd_prompts(args: argparse.Namespace) -> int:
    provider = PROVIDERS_BY_ID.get(args.provider[0]) if args.provider else None
    budget = budget_for(provider)
    if args.budget is not None:
        budget = args.budget
    for sample in chosen_samples(args.sample):
        print(f"===== {sample.id} · {sample.register} · {sample.tests}\n")
        text, kept, dropped = compose_panel_fit(sample.page, sample.panel,
                                                sample.register, budget=budget)
        if budget:
            used = sum(section.tokens for section in kept)
            print(f"budget {used} of {budget} tokens"
                  f" ({estimate_tokens(text)} estimated for the whole prompt)")
            for section in kept:
                print(f"    keep  {section.tokens:>4}  {section.name}")
            for section in dropped:
                print(f"    DROP  {section.tokens:>4}  {section.name}")
            print()
        print(text)
        print()
    return 0


def cmd_estimate(args: argparse.Namespace) -> int:
    route = args.via
    providers = [provider for provider in selected(args.provider) if provider.routes(route)]
    samples = chosen_samples(args.sample)
    images = len(samples) * args.repeat
    print(f"Sample run via {route}: {len(providers)} provider(s) × {len(samples)} panel(s) "
          f"× {args.repeat} take(s) = {len(providers) * images} images\n")
    print(f"{'ID':<20} {'SAMPLE':>10} {'FULL BOOK':>11}  NOTE")
    total = 0.0
    for provider in providers:
        if provider.local:
            span = images * provider.seconds_per_image / 60
            note = "" if provider.commercial else f"{provider.licence}: evaluation only"
            print(f"{provider.id:<20} {span:>8,.0f} m {provider.full_book_hours():>9,.0f} h  {note}")
            continue
        cost = images * provider.unit_usd(route)
        total += cost
        note = f"includes ${provider.setup_usd:,.0f} setup" if provider.setup_usd else ""
        print(f"{provider.id:<20} {cost:>9.2f}  ${provider.full_book_usd(route):>9,.0f}  {note}")
    print(f"\nWhole bake-off: ${total:,.2f}")
    print(f"Full book assumes {PANEL_SLOTS} panels + {PAGE_SLOTS} page sheets "
          f"× {ATTEMPTS_PER_SLOT} attempts.")
    return 0


def cmd_sample(args: argparse.Namespace) -> int:
    stamp = args.run or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    directory = base_dir(args) / stamp
    providers = selected(args.provider)
    samples = chosen_samples(args.sample)
    print(f"Run {stamp} via {args.via} → {directory.relative_to(ROOT)}")
    manifest = run_samples(directory, providers, samples, repeat=args.repeat,
                           dry_run=args.dry_run, route=args.via, image_format=args.format,
                           allow_non_commercial=args.allow_non_commercial)
    report_run(directory, manifest, write_sheet=not args.no_sheet)
    return 0


def report_run(directory: Path, manifest: dict, *, write_sheet: bool = True) -> None:
    made = sum(1 for result in manifest["results"] if result.get("path"))
    total = sum(result.get("bytes", 0) for result in manifest["results"])
    print(f"\nWrote {made} image(s), {total // 1024} KB, ${manifest['usd']:.2f} spent.")
    if write_sheet:
        target = directory / "sheet.html"
        target.write_text(sheet_html(manifest), encoding="utf-8")
        print(f"Comparison sheet: {target.relative_to(ROOT)}")
    print(f"Scorecard to fill in: {(directory / 'scores.tsv').relative_to(ROOT)}")
    print("Publish it with: python3 scripts/build-site.py")


def cmd_sheet(args: argparse.Namespace) -> int:
    directory = resolve_run(args)
    target = directory / "sheet.html"
    target.write_text(sheet_html(load_manifest(directory)), encoding="utf-8")
    print(f"Wrote {target.relative_to(ROOT)}")
    return 0


def cmd_rank(args: argparse.Namespace) -> int:
    directory = resolve_run(args)
    path = directory / "scores.tsv"
    route = load_manifest(directory).get("route", "direct")
    rows = [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    header, body = rows[0], rows[1:]
    weights = {key: weight for key, _, weight in RUBRIC}
    ceiling = sum(weights.values()) * 5

    ranked = []
    for row in body:
        record = dict(zip(header, row))
        provider = PROVIDERS_BY_ID.get(record.get("provider", ""))
        if provider is None:
            continue
        scores = {key: record.get(key, "").strip() for key in weights}
        if not all(value.isdigit() for value in scores.values()):
            continue
        total = sum(int(scores[key]) * weights[key] for key in weights)
        # A defect invisible in one panel and fatal across 541 is not tradeable
        # against a good score elsewhere, so these two gate rather than weigh.
        failed = [key for key in GATED if int(scores[key]) < GATE_FLOOR]
        ranked.append((total, provider, record.get("notes", ""), failed))

    if not ranked:
        print(f"No completed rows in {path.relative_to(ROOT)}. "
              f"Score each rubric column 1–5, then re-run.")
        return 1

    ranked.sort(key=lambda item: (bool(item[3]), -item[0]))
    measured = median_seconds(load_manifest(directory))
    print(f"{'ID':<20} {'SCORE':>7} {'OF':>5} {'FULL BOOK':>11}  VERDICT")
    for total, provider, notes, failed in ranked:
        book = (f"{provider.full_book_hours(measured.get(provider.id)):>9,.0f} h"
                if provider.local else f"${provider.full_book_usd(route):>10,.0f}")
        verdict = f"DISQUALIFIED on {', '.join(failed)}" if failed else (notes or "eligible")
        print(f"{provider.id:<20} {total:>7} {ceiling:>5} {book:>11}  {verdict}")
    if any(item[3] for item in ranked):
        print(f"\nScoring below {GATE_FLOOR} on {' or '.join(GATED)} disqualifies a candidate at "
              f"any price. Both defects are invisible in a single panel and fatal across a book.")
    print(f"\nWeights: {', '.join(f'{key}×{weight}' for key, weight in weights.items())}. "
          f"Score each column 1–5 in {path.relative_to(ROOT)}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def route_option(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--via", default="direct",
                               choices=("direct", "openrouter", "local"),
                               help="call each vendor directly, route through OpenRouter, "
                                    "or run open weights on this machine")

    providers = commands.add_parser("providers", help="list the candidates, their price, and key state")
    route_option(providers)

    prompts = commands.add_parser("prompts", help="print the composed bake-off prompts")
    prompts.add_argument("--sample", action="append", help="panel id such as 001-01; repeatable")
    prompts.add_argument("--provider", action="append",
                         help="compose against this model's text-encoder limit")
    prompts.add_argument("--budget", type=int,
                         help="compose against this many tokens instead")

    estimate = commands.add_parser("estimate", help="cost of a sample run and of the full book")
    estimate.add_argument("--provider", action="append")
    estimate.add_argument("--sample", action="append")
    estimate.add_argument("--repeat", type=int, default=2)
    route_option(estimate)

    sample = commands.add_parser("sample", help="send every sample prompt to every candidate")
    sample.add_argument("--out-dir", type=Path, default=DEFAULT_RUN_DIR)
    sample.add_argument("--run", help="run directory name; defaults to a UTC timestamp")
    sample.add_argument("--provider", action="append", help="candidate id; repeatable")
    sample.add_argument("--sample", action="append", help="panel id such as 001-01; repeatable")
    sample.add_argument("--repeat", type=int, default=2,
                        help="takes per panel; more than one exposes style drift")
    sample.add_argument("--format", default=DEFAULT_FORMAT, choices=tuple(SUFFIXES),
                        help="image format to request; WebP keeps a committed run small")
    sample.add_argument("--dry-run", action="store_true",
                        help="write prompt placeholders instead of calling any API")
    sample.add_argument("--no-sheet", action="store_true")
    sample.add_argument("--allow-non-commercial", action="store_true",
                        help="include weights whose licence forbids shipping their output")
    route_option(sample)

    sheet = commands.add_parser("sheet", help="rebuild the standalone comparison sheet")
    sheet.add_argument("--out-dir", type=Path, default=DEFAULT_RUN_DIR)
    sheet.add_argument("--run", help="run directory name; defaults to the newest")

    rank = commands.add_parser("rank", help="weighted ranking from a filled-in scores.tsv")
    rank.add_argument("--out-dir", type=Path, default=DEFAULT_RUN_DIR)
    rank.add_argument("--run", help="run directory name; defaults to the newest")

    args = parser.parse_args()
    return {
        "providers": cmd_providers,
        "prompts": cmd_prompts,
        "estimate": cmd_estimate,
        "sample": cmd_sample,
        "sheet": cmd_sheet,
        "rank": cmd_rank,
    }[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
