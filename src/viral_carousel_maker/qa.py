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
    expected_hq_size = tuple((manifest.get("design") or {}).get("dimensions_hq", []))
    virality = manifest.get("virality") or {}
    design = manifest.get("design") or {}
    render_engine = str(design.get("render_engine") or manifest.get("render_engine") or "")
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
        hq_path_value = slide.get("path_hq")
        if hq_path_value:
            hq_path = Path(str(hq_path_value))
            if not hq_path.exists():
                errors.append(f"Missing HQ slide image: {hq_path}")
            elif expected_hq_size:
                with Image.open(hq_path) as hq_image:
                    if hq_image.size != expected_hq_size:
                        errors.append(f"{hq_path.name} is {hq_image.size}, expected {expected_hq_size}.")
        if not slide.get("handle_drawn"):
            errors.append(f"{path.name} is missing bottom-left handle metadata.")
        if slide.get("text_fit") is False:
            errors.append(f"{path.name} failed text-fit metadata.")
        if slide.get("role") == "cta" and not slide.get("cta_type"):
            errors.append(f"{path.name} missing CTA type metadata.")
        if not slide.get("visual_mode"):
            warnings.append(f"{path.name} missing visual mode metadata.")
        if render_engine == "browser":
            if not slide.get("visual_component_present"):
                errors.append(f"{path.name} is missing required visual component metadata.")
            if float(slide.get("visual_area_ratio", 0) or 0) <= 0:
                errors.append(f"{path.name} has zero visual area ratio; add a visual icon/object.")

    return not errors, errors + warnings


def build_visual_qa(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build machine-readable visual QA from manifest metadata."""

    slides = manifest.get("slides", [])
    dimensions = tuple(manifest.get("dimensions", []))
    design = manifest.get("design") if isinstance(manifest.get("design"), dict) else {}
    render_engine = str(design.get("render_engine") or manifest.get("render_engine") or "")
    strategy = manifest.get("strategy") if isinstance(manifest.get("strategy"), dict) else {}
    tokens = design.get("tokens") if isinstance(design.get("tokens"), dict) else {}
    palette = design.get("palette") if isinstance(design.get("palette"), dict) else {}
    visual_priority = str(
        strategy.get("visual_priority")
        or design.get("visual_priority")
        or "high"
    ).lower()
    if visual_priority not in {"standard", "high", "extreme", "thumbnail"}:
        visual_priority = "high"
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
    if (
        len(set(modes)) == 1
        and len(modes) >= 6
        and str(design.get("render_engine") or manifest.get("render_engine") or "") == "browser"
    ):
        blockers.append("All slides use the same visual mode; this fails pacing and upgrade quality.")

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
            "visual_overlap_ratio": float(slide.get("visual_overlap_ratio") or 0),
            "visual_area_ratio": float(slide.get("visual_area_ratio") or 0),
            "visual_component_present": bool(slide.get("visual_component_present", False)),
            "visual_component_count": int(slide.get("visual_component_count", 0) or 0),
            "copy_word_count": int(slide.get("copy_word_count", 0) or 0),
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
        if render_engine == "browser":
            if not report["visual_component_present"] or report["visual_component_count"] < 1:
                blockers.append(f"{path.name} is missing a required icon/object visual component.")
            visual_area_min = _visual_area_threshold(str(report.get("role") or ""), visual_priority)
            if report["visual_area_ratio"] < visual_area_min:
                blockers.append(
                    f"{path.name} visual area ratio is {report['visual_area_ratio']:.3f}; "
                    f"{visual_priority} priority requires at least {visual_area_min:.3f}."
                )
        if str(report.get("role") or "") == "body":
            copy_words = int(report.get("copy_word_count") or 0)
            if visual_priority in {"extreme", "thumbnail"} and copy_words > 34:
                blockers.append(
                    f"{path.name} has {copy_words} words; extreme visual priority limits body copy to 34."
                )
            elif visual_priority == "high" and copy_words > 40:
                warnings.append(
                    f"{path.name} has {copy_words} words; visual-first runs work better under 40."
                )
        visual_mode = str(slide.get("visual_mode") or "")
        overlap_ratio = float(slide.get("visual_overlap_ratio") or 0)
        if visual_mode in {"receipt", "photo-anchor", "proof-grid"} and overlap_ratio > 0.08:
            blockers.append(
                f"{path.name} visual object overlaps readable content "
                f"({overlap_ratio:.2f}); move the object or narrow the copy block."
            )
        slide_reports.append(report)

    makeover = _makeover_scale(manifest, modes)
    hook_stop = _hook_visual_stop_score(manifest, slide_reports)
    hook_priority = str(strategy.get("hook_priority") or strategy.get("scroll_stop_priority") or "").lower()
    if hook_priority in {"high", "extreme", "thumbnail"} and hook_stop["score"] < 8.5:
        blockers.append(
            f"Hook visual stop score is {hook_stop['score']}/10; {hook_priority} priority requires 8.5+."
        )
    elif hook_stop["score"] < 7.5:
        warnings.append(
            f"Hook visual stop score is {hook_stop['score']}/10; strengthen first-slide hierarchy and tension."
        )
    if makeover["intensity"] in {"high", "large", "extreme"} and makeover["score"] < 8.5:
        blockers.append(
            f"Makeover scale is {makeover['score']}/10; high-intensity upgrades must clear 8.5."
        )
    elif makeover["score"] < 7.0:
        warnings.append(f"Makeover scale is only {makeover['score']}/10; output may feel too incremental.")

    return {
        "status": "pass" if not blockers else "fail",
        "blockers": blockers,
        "warnings": warnings,
        "summary": {
            "slides_checked": len(slides),
            "dimensions": list(dimensions),
            "global_contrast_ratio": global_contrast,
            "visual_modes": sorted(set(modes)),
            "design_pack": design.get("design_pack"),
            "visual_priority": visual_priority,
            "hook_visual_stop_score": hook_stop["score"],
            "average_visual_area_ratio": round(
                sum(item["visual_area_ratio"] for item in slide_reports) / max(1, len(slide_reports)),
                3,
            ),
        },
        "hook_stop": hook_stop,
        "makeover_scale": makeover,
        "slides": slide_reports,
    }


def _makeover_scale(manifest: dict[str, Any], modes: list[str]) -> dict[str, Any]:
    design = manifest.get("design") if isinstance(manifest.get("design"), dict) else {}
    strategy = manifest.get("strategy") if isinstance(manifest.get("strategy"), dict) else {}
    slides = manifest.get("slides", [])
    design_pack = str(design.get("design_pack") or manifest.get("design_pack") or "editorial-paper")
    render_engine = str(design.get("render_engine") or manifest.get("render_engine") or "unknown")
    unique_modes = len(set(modes))
    mode_target = min(5, max(3, len(slides) // 2)) if len(slides) >= 6 else 2
    score = 3.0
    reasons: list[str] = []
    if render_engine == "browser":
        score += 1.2
        reasons.append("browser-rendered")
    if design_pack != "editorial-paper":
        score += 1.5
        reasons.append(f"non-default design pack: {design_pack}")
    if unique_modes >= mode_target:
        score += 2.2
        reasons.append(f"{unique_modes} visual modes")
    elif unique_modes >= 3:
        score += 1.2
        reasons.append(f"{unique_modes} visual modes")
    if str(manifest.get("visual_thesis") or strategy.get("visual_thesis") or "").strip():
        score += 0.8
        reasons.append("visual thesis present")
    avg_hierarchy = 0.0
    if slides:
        avg_hierarchy = sum(float(slide.get("hierarchy_score", 0) or 0) for slide in slides) / len(slides)
        if avg_hierarchy >= 8.5:
            score += 1.0
            reasons.append("strong hierarchy")
        elif avg_hierarchy >= 7.5:
            score += 0.5
            reasons.append("acceptable hierarchy")
    intensity = str(
        strategy.get("makeover_intensity")
        or strategy.get("visual_upgrade_target")
        or "standard"
    ).lower()
    return {
        "score": round(min(10.0, score), 2),
        "intensity": intensity,
        "design_pack": design_pack,
        "render_engine": render_engine,
        "unique_visual_modes": unique_modes,
        "visual_mode_target": mode_target,
        "average_hierarchy_score": round(avg_hierarchy, 2),
        "reasons": reasons,
    }


def _hook_visual_stop_score(manifest: dict[str, Any], slide_reports: list[dict[str, Any]]) -> dict[str, Any]:
    design = manifest.get("design") if isinstance(manifest.get("design"), dict) else {}
    hook_slide = next((slide for slide in manifest.get("slides", []) if slide.get("role") == "hook"), {})
    hook_report = next((item for item in slide_reports if item.get("role") == "hook"), {})
    title = str(hook_slide.get("title", ""))
    title_words = len(title.split())
    score = 4.8
    reasons: list[str] = []

    if str(design.get("design_pack") or manifest.get("design_pack") or "") != "editorial-paper":
        score += 1.2
        reasons.append("non-default pack")
    if hook_report.get("text_fit"):
        score += 0.8
        reasons.append("text fits")
    hierarchy = float(hook_report.get("hierarchy_score") or 0)
    if hierarchy >= 8.8:
        score += 1.0
        reasons.append("strong hierarchy")
    elif hierarchy >= 8.0:
        score += 0.6
        reasons.append("clear hierarchy")
    if title_words <= 8:
        score += 0.9
        reasons.append("tight headline")
    elif title_words <= 11:
        score += 0.5
    overlap = float(hook_report.get("visual_overlap_ratio") or 0)
    if overlap <= 0.08:
        score += 0.6
        reasons.append("clean visual separation")
    visual_area = float(hook_report.get("visual_area_ratio") or 0)
    if visual_area >= 0.14:
        score += 0.8
        reasons.append("high visual dominance")
    elif visual_area >= 0.10:
        score += 0.4
        reasons.append("visible visual dominance")
    elif visual_area < 0.07:
        score -= 0.9
        reasons.append("visual dominance too low")
    mode = str(hook_slide.get("visual_mode") or hook_report.get("visual_mode") or "")
    if mode in {"shock-stat", "myth-truth", "proof-grid", "photo-anchor"}:
        score += 0.8
        reasons.append(f"high-impact mode: {mode}")
    contrast = float(hook_report.get("contrast_ratio") or 0)
    if contrast >= 7.0:
        score += 0.5
        reasons.append("high contrast")

    return {
        "score": round(min(10.0, score), 2),
        "title_words": title_words,
        "hierarchy_score": round(hierarchy, 2),
        "visual_mode": mode,
        "overlap_ratio": round(overlap, 3),
        "visual_area_ratio": round(visual_area, 3),
        "reasons": reasons,
    }


def _visual_area_threshold(role: str, visual_priority: str) -> float:
    if visual_priority in {"extreme", "thumbnail"}:
        thresholds = {"hook": 0.14, "body": 0.085, "recap": 0.085, "cta": 0.12}
    elif visual_priority == "high":
        thresholds = {"hook": 0.08, "body": 0.06, "recap": 0.06, "cta": 0.09}
    else:
        thresholds = {"hook": 0.09, "body": 0.05, "recap": 0.05, "cta": 0.08}
    return thresholds.get(role, 0.06)


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
