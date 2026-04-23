"""QA checks for generated carousel packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


def load_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def run_manifest_qa(manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    warnings = list(manifest.get("warnings", []))
    slides = manifest.get("slides", [])
    expected_size = tuple(manifest.get("dimensions", []))
    virality = manifest.get("virality") or {}
    design = manifest.get("design") or {}

    if not slides:
        errors.append("Manifest has no slides.")

    if virality and not virality.get("ok", False):
        errors.extend(f"Virality gate: {message}" for message in virality.get("errors", []))
    for message in virality.get("warnings", []):
        if message not in warnings:
            warnings.append(message)

    contact_sheet = design.get("contact_sheet")
    if contact_sheet and not Path(contact_sheet).exists():
        errors.append(f"Missing contact sheet: {contact_sheet}")

    roles = [slide.get("role") for slide in slides]
    for role in ("hook", "recap", "cta"):
        if roles.count(role) != 1:
            errors.append(f"Expected exactly one {role} slide.")
    body_count = roles.count("body")
    if body_count not in {3, 5, 7, 9}:
        errors.append("Expected 3, 5, 7, or 9 body slides.")

    for slide in slides:
        path = Path(slide.get("path", ""))
        if not path.exists():
            errors.append(f"Missing slide image: {path}")
            continue
        with Image.open(path) as image:
            if expected_size and image.size != expected_size:
                errors.append(f"{path.name} is {image.size}, expected {expected_size}.")
        if not slide.get("handle_drawn"):
            errors.append(f"{path.name} is missing bottom-left handle metadata.")
        if slide.get("text_fit") is False:
            warnings.append(f"{path.name} required minimum text sizing; review manually.")
        if slide.get("role") == "cta" and not slide.get("cta_type"):
            errors.append(f"{path.name} missing CTA type metadata.")
        if not slide.get("visual_mode"):
            warnings.append(f"{path.name} missing visual mode metadata.")

    return not errors, errors + warnings


def write_qa_report(manifest: dict[str, Any], output_path: str | Path) -> Path:
    ok, messages = run_manifest_qa(manifest)
    lines = [
        "# QA Report",
        "",
        f"- Status: {'pass' if ok else 'fail'}",
        f"- Slides checked: {len(manifest.get('slides', []))}",
        f"- Dimensions: {manifest.get('dimensions')}",
        "",
        "## Findings",
        "",
    ]
    if not messages:
        lines.append("- No blocking issues found.")
    else:
        lines.extend(f"- {message}" for message in messages)
    path = Path(output_path)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path
