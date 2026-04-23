"""Draft intake normalization for Viral Carousel Maker."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any

import yaml


TEXT_EXTENSIONS = {".md", ".markdown", ".txt"}
JSON_EXTENSIONS = {".json"}


@dataclass
class IntakeResult:
    """Normalized draft data plus a human-editable carousel seed spec."""

    source_type: str
    extracted: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    seed_spec: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "extracted": self.extracted,
            "warnings": self.warnings,
            "seed_spec": self.seed_spec,
        }


def normalize_intake(
    source: str | Path | None = None,
    *,
    text: str | None = None,
    input_format: str = "auto",
) -> IntakeResult:
    """Normalize pasted text, markdown, or best-effort Threadify JSON into a seed spec."""

    if not source and not text:
        raise ValueError("Provide a source path/string or --text content.")

    raw, path = _read_source(source, text)
    kind = _detect_format(raw, path, input_format)
    if kind == "json":
        extracted, warnings = _extract_json(raw)
    else:
        extracted, warnings = _extract_text(raw, kind)

    seed_spec = build_seed_spec(extracted, source_type=kind, warnings=warnings)
    return IntakeResult(source_type=kind, extracted=extracted, warnings=warnings, seed_spec=seed_spec)


def write_seed_yaml(result: IntakeResult, output_path: str | Path) -> Path:
    """Write only the editable seed spec to YAML."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(result.seed_spec, sort_keys=False), encoding="utf-8")
    return path


def build_seed_spec(extracted: dict[str, Any], *, source_type: str, warnings: list[str]) -> dict[str, Any]:
    title = _compact_title(str(extracted.get("title") or "This draft is doing too much"))
    handle = _normalize_handle(str(extracted.get("handle") or "@yourhandle"))
    draft_text = str(extracted.get("draft_text") or title).strip()
    body_points = _body_points(draft_text)
    cta = extracted.get("cta") if isinstance(extracted.get("cta"), dict) else {"type": "follow"}
    cta_type = str(cta.get("type") or "follow").lower()
    cta = {"type": "offer", "url": str(cta.get("url", "")).strip()} if cta_type == "offer" else {"type": "follow"}

    slides = [
        {
            "role": "hook",
            "title": title,
            "subtitle": "The useful version needs one sharper job.",
            "main_idea": "Name the tension before teaching.",
            "visual_mode": "shock-stat",
            "alt": f"Hook slide for {title}.",
        }
    ]
    body_titles = ["Name the tension", "Choose one job", "Cut the extras", "Prove the point", "Give the next move"]
    for index, body_title in enumerate(body_titles):
        point = body_points[index] if index < len(body_points) else "Make this slide carry one useful idea, not a pile of advice."
        slides.append(
            {
                "role": "body",
                "title": body_title,
                "body": _compact_sentence(point),
                "main_idea": body_title,
                "visual_mode": _visual_mode_for_index(index),
            }
        )
    slides.extend(
        [
            {
                "role": "recap",
                "title": "TL;DR",
                "bullets": [
                    "Start with tension.",
                    "Make each slide do one job.",
                    "Give the reader a next move.",
                ],
                "main_idea": "Compress the useful takeaway.",
                "visual_mode": "field-note",
            },
            {
                "role": "cta",
                "title": "Follow",
                "subtitle": "For practical creator systems people actually save.",
                "cta": cta,
                "main_idea": "Earn a low-pressure next step.",
                "visual_mode": "photo-anchor",
            },
        ]
    )

    return {
        "version": 1,
        "title": title,
        "handle": handle,
        "template_family": "framework",
        "aspect_ratio": "vertical",
        "design_pack": "editorial-paper",
        "render_engine": "browser",
        "render_quality": "high",
        "strategy": {
            "goal": "saves",
            "hook_archetype": "private_room_observation",
            "belief_shift": "Old: the draft is information. New: the carousel needs one useful belief shift.",
            "proof_level": "lived-experience",
            "cta_pressure": "soft",
            "visual_priority": "high",
            "visual_thesis": "One clear visual anchor per slide, with crisp editorial hierarchy.",
            "virality_principles": ["observation-over-how-to", "one-idea-per-slide"],
        },
        "intake": {
            "source_type": source_type,
            "mapping": "best-effort",
            "warnings": warnings,
            "extracted_fields": sorted(extracted.keys()),
        },
        "profile": _profile_from_extracted(extracted),
        "caption": str(extracted.get("caption") or "").strip(),
        "slides": slides,
    }


def _read_source(source: str | Path | None, text: str | None) -> tuple[str, Path | None]:
    if text is not None:
        return text, None
    assert source is not None
    source_text = str(source)
    path = Path(source_text)
    if path.exists():
        return path.read_text(encoding="utf-8"), path
    return source_text, None


def _detect_format(raw: str, path: Path | None, input_format: str) -> str:
    requested = input_format.lower()
    if requested not in {"auto", "text", "markdown", "json"}:
        raise ValueError("input_format must be auto, text, markdown, or json.")
    if requested != "auto":
        return "text" if requested == "markdown" else requested
    suffix = path.suffix.lower() if path else ""
    if suffix in JSON_EXTENSIONS:
        return "json"
    if suffix in TEXT_EXTENSIONS:
        return "text"
    stripped = raw.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    return "text"


def _extract_text(raw: str, kind: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    title = ""
    if lines:
        first = re.sub(r"^#+\s*", "", lines[0]).strip()
        title = first if first else "This draft is doing too much"
    else:
        warnings.append("Draft text was empty; generated a placeholder seed.")
    return {
        "title": title,
        "draft_text": raw.strip(),
        "handle": _find_handle(raw) or "@yourhandle",
        "caption": raw.strip()[:240],
        "format": kind,
    }, warnings


def _extract_json(raw: str) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _extract_text(raw, "text")[0], [f"JSON parse failed: {exc.msg}; treated input as text."]

    root = data[0] if isinstance(data, list) and data else data
    if not isinstance(root, dict):
        warnings.append("Threadify JSON did not contain an object; treated stringified content as text.")
        return _extract_text(json.dumps(data, ensure_ascii=False), "text")[0], warnings

    title = _first_string(root, ("title", "topic", "hook", "headline", "name"))
    handle = _first_string(root, ("handle", "threads_handle", "author_handle", "username"))
    handle = handle or _nested_string(root, (("profile", "handle"), ("user", "handle"), ("author", "handle")))
    draft_text = _first_string(root, ("content", "body", "text", "draft", "notes", "caption"))
    slides = root.get("slides") or root.get("carousel") or root.get("items")
    slide_text = _extract_slide_text(slides)
    if not draft_text and slide_text:
        draft_text = slide_text
    if not title and slide_text:
        title = slide_text.splitlines()[0]
    cta = _extract_cta(root)

    if not title:
        warnings.append("No title/hook found in JSON; generated a placeholder hook.")
    if not draft_text:
        warnings.append("No draft body found in JSON; body slides will need manual editing.")
    if not handle:
        warnings.append("No Threads handle found; seed uses @yourhandle.")

    return {
        "title": title or "This draft is doing too much",
        "draft_text": draft_text or title or "",
        "handle": handle or "@yourhandle",
        "caption": _first_string(root, ("caption", "post_caption", "thread_caption")) or "",
        "cta": cta,
        "format": "threadify-json",
    }, warnings


def _extract_slide_text(slides: Any) -> str:
    if not isinstance(slides, list):
        return ""
    parts: list[str] = []
    for slide in slides:
        if isinstance(slide, dict):
            parts.extend(str(slide.get(key, "")).strip() for key in ("title", "subtitle", "body", "text") if slide.get(key))
            bullets = slide.get("bullets")
            if isinstance(bullets, list):
                parts.extend(str(item).strip() for item in bullets if item)
        elif isinstance(slide, str):
            parts.append(slide.strip())
    return "\n".join(part for part in parts if part)


def _extract_cta(root: dict[str, Any]) -> dict[str, str]:
    cta = root.get("cta")
    if isinstance(cta, dict):
        cta_type = str(cta.get("type") or "follow").lower()
        return {"type": cta_type, "url": str(cta.get("url", "")).strip()}
    offer_url = _first_string(root, ("offer_url", "url", "link", "cta_url"))
    if offer_url:
        return {"type": "offer", "url": offer_url}
    return {"type": "follow"}


def _first_string(root: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = root.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _nested_string(root: dict[str, Any], paths: tuple[tuple[str, str], ...]) -> str:
    for first, second in paths:
        value = root.get(first)
        if isinstance(value, dict):
            nested = value.get(second)
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
    return ""


def _find_handle(text: str) -> str:
    match = re.search(r"@[A-Za-z0-9_\\.]{2,30}", text)
    return match.group(0) if match else ""


def _normalize_handle(handle: str) -> str:
    value = handle.strip()
    return value if value.startswith("@") else f"@{value}"


def _compact_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title.strip().strip("#")).strip()
    if not cleaned:
        cleaned = "This draft is doing too much"
    lower = cleaned.lower()
    if lower.startswith(("how to ", "here are ", "here's how ", "want to ")):
        cleaned = "This draft is hiding the real tension"
    words = cleaned.split()
    return " ".join(words[:11])


def _body_points(text: str) -> list[str]:
    candidates = re.split(r"(?<=[.!?])\s+|\n+-\s+|\n+\d+[.)]\s+", text.strip())
    points = [candidate.strip(" -\n\t") for candidate in candidates if len(candidate.strip()) > 12]
    return points[:5]


def _compact_sentence(text: str) -> str:
    words = re.sub(r"\s+", " ", text.strip()).split()
    return " ".join(words[:28]).rstrip(".,;:") + "."


def _visual_mode_for_index(index: int) -> str:
    return ["myth-truth", "contrast-table", "field-note", "proof-grid", "photo-anchor"][index % 5]


def _profile_from_extracted(extracted: dict[str, Any]) -> dict[str, Any]:
    return {
        "handle": _normalize_handle(str(extracted.get("handle") or "@yourhandle")),
        "visual_preferences": ["visual-first", "mobile-readable", "high contrast"],
        "style_anti_patterns": ["generic slide deck", "text-only slides"],
    }
