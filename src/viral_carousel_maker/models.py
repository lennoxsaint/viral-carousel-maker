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

DESIGN_PACKS = {
    "editorial-paper": {
        "label": "Editorial Paper",
        "palette": {
            "background": "#f7f4ee",
            "paper": "#fbfaf6",
            "text": "#05063f",
            "muted": "#5f6270",
            "accent": "#e84b05",
            "accent_2": "#ff1f83",
            "line": "#dedbd3",
        },
        "tokens": {
            "shadow_strength": "soft",
            "texture": "paper",
            "headline_style": "condensed",
        },
    },
    "brutal-proof": {
        "label": "Brutal Proof",
        "palette": {
            "background": "#090909",
            "paper": "#111111",
            "text": "#ffffff",
            "muted": "#a7a7a7",
            "accent": "#ff3b30",
            "accent_2": "#f9f871",
            "line": "#333333",
        },
        "tokens": {
            "shadow_strength": "hard",
            "texture": "grain",
            "headline_style": "block",
        },
    },
    "quiet-luxury": {
        "label": "Quiet Luxury",
        "palette": {
            "background": "#f8f7f2",
            "paper": "#fcfbf6",
            "text": "#141412",
            "muted": "#666158",
            "accent": "#8a6f35",
            "accent_2": "#1f5a52",
            "line": "#ddd7c8",
        },
        "tokens": {
            "shadow_strength": "soft",
            "texture": "linen",
            "headline_style": "editorial",
        },
    },
    "founder-field-notes": {
        "label": "Founder Field Notes",
        "palette": {
            "background": "#f3f0e7",
            "paper": "#fffdf6",
            "text": "#151515",
            "muted": "#6b665c",
            "accent": "#ff6b4a",
            "accent_2": "#4ecdc4",
            "line": "#d9d1c2",
        },
        "tokens": {
            "shadow_strength": "soft",
            "texture": "notebook",
            "headline_style": "field-note",
        },
    },
    "photo-anchor": {
        "label": "Photo Anchor",
        "palette": {
            "background": "#f4f6f7",
            "paper": "#ffffff",
            "text": "#101820",
            "muted": "#63707a",
            "accent": "#0057ff",
            "accent_2": "#ff7a00",
            "line": "#dae1e7",
        },
        "tokens": {
            "shadow_strength": "image",
            "texture": "clean",
            "headline_style": "modern",
        },
    },
    "data-lab": {
        "label": "Data Lab",
        "palette": {
            "background": "#eef3f2",
            "paper": "#fbfffe",
            "text": "#071b1a",
            "muted": "#516261",
            "accent": "#00a676",
            "accent_2": "#ff4d6d",
            "line": "#c7d8d4",
        },
        "tokens": {
            "shadow_strength": "technical",
            "texture": "grid",
            "headline_style": "precise",
        },
    },
    "myth-truth": {
        "label": "Myth Truth",
        "palette": {
            "background": "#fbfaf6",
            "paper": "#ffffff",
            "text": "#04043f",
            "muted": "#63636f",
            "accent": "#ef4444",
            "accent_2": "#16a34a",
            "line": "#dddce4",
        },
        "tokens": {
            "shadow_strength": "soft",
            "texture": "paper",
            "headline_style": "contrast",
        },
    },
    "template-marketplace": {
        "label": "Template Marketplace",
        "palette": {
            "background": "#f6f7fb",
            "paper": "#ffffff",
            "text": "#16161d",
            "muted": "#696978",
            "accent": "#6c5ce7",
            "accent_2": "#ff6b4a",
            "line": "#dbdeea",
        },
        "tokens": {
            "shadow_strength": "product",
            "texture": "clean",
            "headline_style": "utility",
        },
    },
}

DEFAULT_DESIGN_TOKENS = {
    "headline_max_words": 11,
    "body_max_words": 42,
    "accent_rule_width_ratio": 0.22,
    "handle_position": "bottom-left",
    "progress_position": "top-left",
    "cta_pressure_default": "soft",
    "crop_safe_margin_ratio": 0.085,
    "minimum_contrast_ratio": 4.5,
    "browser_render_scale": 1,
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
