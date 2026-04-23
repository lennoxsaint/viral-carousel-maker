"""QA checks for generated carousel packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from .design import contrast_ratio


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
    critic = manifest.get("critic") if isinstance(manifest.get("critic"), dict) else {}

    if not slides:
        errors.append("Manifest has no slides.")

    if virality and not virality.get("ok", False):
        errors.extend(f"Virality gate: {message}" for message in virality.get("errors", []))
    for message in virality.get("warnings", []):
        if message not in warnings:
            warnings.append(message)

    if critic:
        if critic.get("status") == "needs-revision":
            warnings.append("AI critic gate needs revision; rerun the skill critique before publishing.")
        elif critic.get("status") == "missing":
            warnings.append("AI critic gate missing; skill workflow must run it before final handoff.")

    contact_sheet = design.get("contact_sheet")
    if contact_sheet and not Path(contact_sheet).exists():
        errors.append(f"Missing contact sheet: {contact_sheet}")

    visual_qa = manifest.get("visual_qa")
    if isinstance(visual_qa, dict):
        for blocker in visual_qa.get("blockers", []):
            errors.append(f"Visual QA: {blocker}")
        for warning in visual_qa.get("warnings", []):
            if warning not in warnings:
                warnings.append(f"Visual QA: {warning}")
    else:
        warnings.append("Visual QA metadata missing; run a current renderer before final delivery.")

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
            errors.append(f"{path.name} failed text-fit metadata.")
        if slide.get("role") == "cta" and not slide.get("cta_type"):
            errors.append(f"{path.name} missing CTA type metadata.")
        if not slide.get("visual_mode"):
            warnings.append(f"{path.name} missing visual mode metadata.")

    return not errors, errors + warnings


def build_visual_qa(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build machine-readable visual QA from manifest metadata."""

    slides = manifest.get("slides", [])
    dimensions = tuple(manifest.get("dimensions", []))
    design = manifest.get("design") if isinstance(manifest.get("design"), dict) else {}
    tokens = design.get("tokens") if isinstance(design.get("tokens"), dict) else {}
    palette = design.get("palette") if isinstance(design.get("palette"), dict) else {}
    min_contrast = float(tokens.get("minimum_contrast_ratio", 4.5) or 4.5)
    blockers: list[str] = []
    warnings: list[str] = []
    slide_reports: list[dict[str, Any]] = []

    global_contrast = None
    if palette:
        global_contrast = contrast_ratio(
            str(palette.get("text", "#000000")),
            str(palette.get("paper", palette.get("background", "#ffffff"))),
        )
        if global_contrast < min_contrast:
            blockers.append(
                f"Global text/background contrast is {global_contrast}, below {min_contrast}."
            )

    modes = [str(slide.get("visual_mode", "")) for slide in slides if slide.get("visual_mode")]
    if len(set(modes)) == 1 and len(modes) >= 6:
        warnings.append("All slides use the same visual mode; review pacing for repetition.")

    for slide in slides:
        path = Path(str(slide.get("path", "")))
        report = {
            "index": slide.get("index"),
            "role": slide.get("role"),
            "path": str(path),
            "text_fit": bool(slide.get("text_fit", False)),
            "handle_bottom_left": bool(slide.get("handle_drawn", False))
            and str(slide.get("handle_position", "bottom-left")) == "bottom-left",
            "crop_safe": bool(slide.get("crop_safe", True)),
            "contrast_ratio": float(slide.get("contrast_ratio", global_contrast or min_contrast)),
            "hierarchy_score": float(slide.get("hierarchy_score", 8.0)),
            "visual_mode": slide.get("visual_mode"),
        }
        if not path.exists():
            blockers.append(f"Missing slide file for visual QA: {path}.")
        else:
            try:
                with Image.open(path) as image:
                    report["dimensions"] = list(image.size)
                    if dimensions and image.size != dimensions:
                        blockers.append(
                            f"{path.name} is {image.size}, expected {dimensions}."
                        )
            except Exception as exc:
                blockers.append(f"Could not inspect {path}: {exc}.")

        if not report["text_fit"]:
            blockers.append(f"{path.name} has clipped or overflowing text.")
        if not report["handle_bottom_left"]:
            blockers.append(f"{path.name} is missing required bottom-left handle.")
        if not report["crop_safe"]:
            blockers.append(f"{path.name} has content outside the crop-safe zone.")
        if report["contrast_ratio"] < min_contrast:
            blockers.append(
                f"{path.name} contrast is {report['contrast_ratio']}, below {min_contrast}."
            )
        if report["hierarchy_score"] < 7:
            warnings.append(f"{path.name} hierarchy score is below 7; review first-read clarity.")
        slide_reports.append(report)

    return {
        "status": "pass" if not blockers else "fail",
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            "slides_checked": len(slides),
            "dimensions": list(dimensions),
            "global_contrast_ratio": global_contrast,
            "visual_modes": sorted(set(modes)),
        },
        "slides": slide_reports,
    }


def write_visual_qa_files(manifest: dict[str, Any], out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    visual_qa = manifest.get("visual_qa")
    if not isinstance(visual_qa, dict):
        visual_qa = build_visual_qa(manifest)
        manifest["visual_qa"] = visual_qa
    json_path = out / "visual_qa.json"
    report_path = out / "visual_qa_report.md"
    json_path.write_text(json.dumps(visual_qa, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Visual QA Report",
        "",
        f"- Status: {visual_qa.get('status', 'unknown')}",
        f"- Slides checked: {visual_qa.get('summary', {}).get('slides_checked', 0)}",
        f"- Dimensions: {visual_qa.get('summary', {}).get('dimensions', [])}",
        f"- Global contrast: {visual_qa.get('summary', {}).get('global_contrast_ratio', 'n/a')}",
        "",
        "## Blockers",
        "",
    ]
    blockers = visual_qa.get("blockers", [])
    lines.extend(f"- {item}" for item in blockers) if blockers else lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    warnings = visual_qa.get("warnings", [])
    lines.extend(f"- {item}" for item in warnings) if warnings else lines.append("- None.")
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, report_path


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
