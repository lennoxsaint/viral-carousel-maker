"""Local profile helpers."""

from __future__ import annotations

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
}


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

