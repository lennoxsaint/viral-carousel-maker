"""Local profile helpers."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


PROFILE_DIR = Path.home() / ".viral-carousel-maker"
PROFILE_PATH = PROFILE_DIR / "profile.yaml"


DEFAULT_PROFILE = {
    "handle": "@yourhandle",
    "niche": "creator education",
    "audience": "people who want practical, saveable ideas",
    "tone": "strategic but friendly",
    "cta_default": "follow",
    "visual_preferences": ["clean", "high contrast", "mobile-first"],
    "winning_hook_categories": [],
    "weak_hook_categories": [],
    "visual_anchors": [],
    "best_visual_packs": [],
    "style_anti_patterns": [],
    "performance_summary": {
        "top_hooks": [],
        "weak_hooks": [],
        "best_cta_pressure": "soft",
        "best_body_slide_count": 5,
        "topics_that_earned_saves": [],
        "last_reviewed_at": None,
    },
}

PROFILE_ALLOWED_KEYS = {
    "handle",
    "niche",
    "sub_niche",
    "audience",
    "tone",
    "voice",
    "cta_default",
    "offer",
    "visual_preferences",
    "brand_colors",
    "proof_boundaries",
    "risk_appetite",
    "preferred_body_slide_count",
    "style_anti_patterns",
    "winning_hook_categories",
    "weak_hook_categories",
    "visual_anchors",
    "best_visual_packs",
    "performance_summary",
}

SECRET_KEY_PARTS = (
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "authorization",
    "credential",
)


def load_profile(path: str | Path | None = None) -> dict[str, Any]:
    profile_path = Path(path) if path else PROFILE_PATH
    if not profile_path.exists():
        return {}
    data = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def write_profile(profile: dict[str, Any], path: str | Path | None = None) -> Path:
    profile_path = Path(path) if path else PROFILE_PATH
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    return profile_path


def init_profile(path: str | Path | None = None) -> Path:
    return write_profile(DEFAULT_PROFILE, path)


def merge_profile(
    existing: dict[str, Any] | None,
    incoming: dict[str, Any] | None,
    *,
    source: str = "manual",
    now: str | None = None,
) -> dict[str, Any]:
    """Merge stable, allowlisted creator preferences while stripping secrets."""

    merged = _strip_secrets(deepcopy(existing or {}))
    clean_incoming = _strip_secrets(incoming or {})
    for key in PROFILE_ALLOWED_KEYS:
        if key not in clean_incoming:
            continue
        value = clean_incoming[key]
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            merged[key] = _merge_list(merged.get(key), value)
        elif isinstance(value, dict):
            current = merged.get(key) if isinstance(merged.get(key), dict) else {}
            merged[key] = {**current, **value}
        else:
            merged[key] = value

    provenance = merged.get("provenance") if isinstance(merged.get("provenance"), dict) else {}
    sources = provenance.get("sources") if isinstance(provenance.get("sources"), list) else []
    if source and source not in sources:
        sources.append(source)
    provenance["sources"] = sources
    provenance["last_updated_at"] = now or datetime.now(timezone.utc).isoformat()
    merged["provenance"] = provenance
    return merged


def profile_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Extract stable profile hints from a rendered manifest/spec snapshot."""

    profile = manifest.get("profile_snapshot")
    if not isinstance(profile, dict):
        profile = manifest.get("profile")
    if not isinstance(profile, dict):
        profile = {}

    strategy = manifest.get("strategy") if isinstance(manifest.get("strategy"), dict) else {}
    design = manifest.get("design") if isinstance(manifest.get("design"), dict) else {}
    slides = manifest.get("slides") if isinstance(manifest.get("slides"), list) else []
    body_count = sum(1 for slide in slides if isinstance(slide, dict) and slide.get("role") == "body")

    incoming = dict(profile)
    if manifest.get("handle"):
        incoming["handle"] = manifest.get("handle")
    cta_slide = next(
        (slide for slide in slides if isinstance(slide, dict) and slide.get("role") == "cta"),
        {},
    )
    cta = cta_slide.get("cta") if isinstance(cta_slide.get("cta"), dict) else manifest.get("cta")
    if isinstance(cta, dict) and cta.get("type"):
        incoming["cta_default"] = cta.get("type")
    if body_count:
        incoming["preferred_body_slide_count"] = body_count
    if design.get("design_pack") or manifest.get("design_pack"):
        incoming["best_visual_packs"] = [design.get("design_pack") or manifest.get("design_pack")]
    if strategy.get("hook_archetype"):
        incoming["winning_hook_categories"] = [strategy.get("hook_archetype")]
    if strategy.get("visual_thesis"):
        incoming["visual_anchors"] = [strategy.get("visual_thesis")]
    return incoming


def update_profile_from_manifest(
    manifest: dict[str, Any],
    *,
    path: str | Path | None = None,
    source: str = "successful-render",
) -> Path:
    """Merge a successful render's stable preferences into the local profile."""

    profile_path = Path(path) if path else PROFILE_PATH
    existing = load_profile(profile_path)
    incoming = profile_from_manifest(manifest)
    merged = merge_profile(existing, incoming, source=source)
    return write_profile(merged, profile_path)


def _merge_list(existing: Any, incoming: list[Any]) -> list[Any]:
    result: list[Any] = []
    for item in existing if isinstance(existing, list) else []:
        if item not in result:
            result.append(item)
    for item in incoming:
        if item not in result:
            result.append(item)
    return result


def _strip_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in SECRET_KEY_PARTS):
                continue
            clean[key] = _strip_secrets(item)
        return clean
    if isinstance(value, list):
        return [_strip_secrets(item) for item in value]
    return value
