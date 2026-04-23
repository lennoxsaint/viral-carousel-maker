"""Shared constants and small helpers for carousel specs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "vertical": (1080, 1350),
    "square": (1080, 1080),
    "wide": (1920, 1080),
}

SLIDE_ROLES = {"hook", "body", "recap", "cta"}

TEMPLATE_FAMILIES = {
    "story",
    "list",
    "framework",
    "timeline",
    "debate",
    "examples",
    "data",
    "quote",
    "map",
    "mistakes",
    "recap",
    "cta",
}

VISUAL_MODES = {
    "editorial-paper",
    "shock-stat",
    "proof-grid",
    "myth-truth",
    "taxonomy",
    "quiet-truth",
    "receipt",
    "contrast-table",
    "field-note",
    "photo-anchor",
}

DEFAULT_DESIGN_TOKENS = {
    "headline_max_words": 11,
    "body_max_words": 42,
    "accent_rule_width_ratio": 0.22,
    "handle_position": "bottom-left",
    "progress_position": "top-left",
    "cta_pressure_default": "soft",
}

DEFAULT_PALETTE = {
    "background": "#f7f4ee",
    "paper": "#fbfaf6",
    "text": "#05063f",
    "muted": "#5f6270",
    "accent": "#e84b05",
    "accent_2": "#ff1f83",
    "success": "#10a640",
    "danger": "#ff2a2a",
    "line": "#dedbd3",
}

FONT_CANDIDATES = {
    "heading": [
        "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "body": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
    ],
    "bold": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
}


@dataclass(frozen=True)
class RenderDimensions:
    width: int
    height: int

    @property
    def margin(self) -> int:
        return max(64, int(min(self.width, self.height) * 0.11))

    @property
    def gutter(self) -> int:
        return max(28, int(min(self.width, self.height) * 0.035))


def dimensions_for(aspect_ratio: str) -> RenderDimensions:
    if aspect_ratio not in ASPECT_RATIOS:
        allowed = ", ".join(sorted(ASPECT_RATIOS))
        raise ValueError(f"Unsupported aspect_ratio '{aspect_ratio}'. Use one of: {allowed}.")
    width, height = ASPECT_RATIOS[aspect_ratio]
    return RenderDimensions(width=width, height=height)


def deep_merge_palette(user_palette: dict[str, Any] | None) -> dict[str, str]:
    palette = dict(DEFAULT_PALETTE)
    for key, value in (user_palette or {}).items():
        if value:
            palette[str(key)] = str(value)
    return palette


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]
