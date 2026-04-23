"""Design-pack helpers shared by renderers and QA."""

from __future__ import annotations

from typing import Any

from .models import DEFAULT_DESIGN_TOKENS, DESIGN_PACKS, deep_merge_palette


DEFAULT_DESIGN_PACK = "editorial-paper"


def normalize_design_pack(value: Any) -> str:
    pack = str(value or DEFAULT_DESIGN_PACK).strip().lower()
    return pack if pack in DESIGN_PACKS else DEFAULT_DESIGN_PACK


def resolve_design_pack(spec: dict[str, Any]) -> str:
    strategy = spec.get("strategy") if isinstance(spec.get("strategy"), dict) else {}
    theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    return normalize_design_pack(
        spec.get("design_pack")
        or theme.get("design_pack")
        or strategy.get("design_pack")
        or DEFAULT_DESIGN_PACK
    )


def resolve_palette(spec: dict[str, Any], design_pack: str | None = None) -> dict[str, str]:
    pack = DESIGN_PACKS[normalize_design_pack(design_pack or resolve_design_pack(spec))]
    palette = deep_merge_palette(pack.get("palette", {}))
    theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    user_palette = theme.get("palette") if isinstance(theme.get("palette"), dict) else {}
    for key, value in user_palette.items():
        if value:
            palette[str(key)] = str(value)
    return palette


def resolve_design_tokens(spec: dict[str, Any], design_pack: str | None = None) -> dict[str, Any]:
    pack = DESIGN_PACKS[normalize_design_pack(design_pack or resolve_design_pack(spec))]
    theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    user_tokens = theme.get("design_tokens") if isinstance(theme.get("design_tokens"), dict) else {}
    return {
        **DEFAULT_DESIGN_TOKENS,
        **pack.get("tokens", {}),
        **user_tokens,
    }


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """Return WCAG-style contrast ratio for two hex colors."""

    def channel(value: int) -> float:
        normalized = value / 255
        return normalized / 12.92 if normalized <= 0.03928 else ((normalized + 0.055) / 1.055) ** 2.4

    def luminance(hex_value: str) -> float:
        value = hex_value.lstrip("#")
        if len(value) != 6:
            value = "000000"
        red, green, blue = (int(value[i : i + 2], 16) for i in (0, 2, 4))
        return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)

    l1 = luminance(hex_a)
    l2 = luminance(hex_b)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)
