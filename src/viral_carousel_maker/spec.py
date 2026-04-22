"""Spec loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .models import ASPECT_RATIOS, SLIDE_ROLES, TEMPLATE_FAMILIES


class SpecError(ValueError):
    """Raised when a carousel spec is invalid."""


def load_spec(path: str | Path) -> dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise SpecError(f"Spec file not found: {spec_path}")
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SpecError("Spec must be a YAML object.")
    return data


def validate_with_jsonschema(spec: dict[str, Any], schema_path: str | Path | None = None) -> list[str]:
    """Validate with jsonschema when installed; return warnings if unavailable."""

    if schema_path is None:
        schema_path = Path(__file__).resolve().parents[2] / "schemas" / "carousel.schema.json"
    schema_file = Path(schema_path)
    if not schema_file.exists():
        return [f"Schema file missing: {schema_file}"]

    try:
        import jsonschema
    except Exception:
        return ["jsonschema is not installed; used built-in validation only."]

    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    jsonschema.validate(instance=spec, schema=schema)
    return []


def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Validate required fields and return non-fatal warnings."""

    warnings: list[str] = []
    required = ["title", "handle", "template_family", "aspect_ratio", "slides"]
    for key in required:
        if key not in spec:
            raise SpecError(f"Missing required field: {key}")

    aspect_ratio = str(spec["aspect_ratio"])
    if aspect_ratio not in ASPECT_RATIOS:
        raise SpecError(f"Unsupported aspect_ratio '{aspect_ratio}'.")

    template_family = str(spec["template_family"])
    if template_family not in TEMPLATE_FAMILIES:
        raise SpecError(f"Unsupported template_family '{template_family}'.")

    handle = str(spec["handle"]).strip()
    if not handle:
        raise SpecError("handle cannot be empty.")
    if not handle.startswith("@"):
        warnings.append("handle does not start with @; renderer will normalize it.")

    slides = spec["slides"]
    if not isinstance(slides, list) or not slides:
        raise SpecError("slides must be a non-empty list.")

    roles = [str(slide.get("role", "")) for slide in slides if isinstance(slide, dict)]
    if roles.count("hook") != 1:
        raise SpecError("Carousel must include exactly one hook slide.")
    if roles.count("recap") != 1:
        raise SpecError("Carousel must include exactly one recap slide.")
    if roles.count("cta") != 1:
        raise SpecError("Carousel must include exactly one cta slide.")
    body_count = roles.count("body")
    if body_count not in {3, 5, 7, 9}:
        raise SpecError("Carousel must include 3, 5, 7, or 9 body slides.")

    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            raise SpecError(f"Slide {index} must be an object.")
        role = str(slide.get("role", ""))
        if role not in SLIDE_ROLES:
            raise SpecError(f"Slide {index} has unsupported role '{role}'.")
        if not str(slide.get("title", "")).strip():
            raise SpecError(f"Slide {index} is missing title.")
        if role == "cta":
            cta = slide.get("cta", spec.get("cta", {}))
            if not isinstance(cta, dict):
                raise SpecError("CTA slide must include a cta object.")
            cta_type = str(cta.get("type", "follow"))
            if cta_type not in {"follow", "offer"}:
                raise SpecError("CTA type must be follow or offer.")
            if cta_type == "offer" and not str(cta.get("url", "")).strip():
                raise SpecError("Offer CTA must include a url.")

    warnings.extend(validate_with_jsonschema(spec))
    return warnings


def normalized_handle(value: str) -> str:
    value = value.strip()
    return value if value.startswith("@") else f"@{value}"

