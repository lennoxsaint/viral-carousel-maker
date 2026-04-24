"""Mandatory interview gate for carousel generation.

The skill can ask questions in chat, but the CLI needs a deterministic gate so
the workflow can prove that enough signal exists before drafting or rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import yaml


class InterviewError(ValueError):
    """Raised when interview answers cannot be loaded or parsed."""


@dataclass(frozen=True)
class FieldSpec:
    key: str
    question: str
    aliases: tuple[str, ...]
    min_words: int = 1
    current_required: bool = True
    profile_aliases: tuple[str, ...] = ()
    choices: tuple[str, ...] = ()
    conditional_on: tuple[str, str] | None = None


FIELD_SPECS: tuple[FieldSpec, ...] = (
    FieldSpec(
        "handle",
        "What is your Threads handle?",
        ("handle", "threads_handle", "author_handle", "username", "profile.handle", "user.handle"),
        current_required=False,
    ),
    FieldSpec(
        "niche",
        "What niche are you in?",
        ("niche", "category", "profile.niche"),
        min_words=2,
        current_required=False,
    ),
    FieldSpec(
        "sub_niche",
        "What sub-niche should this carousel signal?",
        ("sub_niche", "sub-niche", "subniche", "profile.sub_niche"),
        min_words=2,
        current_required=False,
    ),
    FieldSpec(
        "target_viewer",
        "Who exactly should feel like this was written for them?",
        ("target_viewer", "viewer", "audience", "target_audience", "profile.audience"),
        min_words=5,
        profile_aliases=("audience", "target_audience"),
    ),
    FieldSpec(
        "viewer_pain",
        "What painful, annoying, expensive, or status-threatening situation are they already experiencing?",
        ("viewer_pain", "pain", "audience_pain", "problem", "profile.audience_pains"),
        min_words=5,
        profile_aliases=("audience_pains",),
    ),
    FieldSpec(
        "viewer_desire",
        "What outcome or desire are they already trying to reach?",
        ("viewer_desire", "desire", "audience_desire", "desired_outcome", "profile.audience_desires"),
        min_words=4,
        profile_aliases=("audience_desires",),
    ),
    FieldSpec(
        "belief_shift",
        "What old belief should the carousel replace, and what new belief should it leave behind?",
        ("belief_shift", "strategy.belief_shift", "old_to_new_belief"),
        min_words=7,
    ),
    FieldSpec(
        "topic",
        "What exact topic and scope should this carousel cover?",
        ("topic", "scope", "carousel_topic", "title"),
        min_words=4,
    ),
    FieldSpec(
        "why_now",
        "Why does this topic matter right now?",
        ("why_now", "timeliness", "why_this_now", "urgency_reason"),
        min_words=4,
    ),
    FieldSpec(
        "proof",
        "What proof, lived experience, example, data, or receipt can we safely use?",
        ("proof", "evidence", "examples", "receipts"),
        min_words=4,
    ),
    FieldSpec(
        "proof_strength",
        "How strong is the proof: none, lived experience, example, data, or receipt?",
        ("proof_strength", "proof_level", "strategy.proof_level"),
        choices=("none", "lived experience", "lived-experience", "example", "data", "receipt"),
    ),
    FieldSpec(
        "carousel_job",
        "What is the carousel's job: reach, saves, authority, conversion, or community?",
        ("carousel_job", "job", "goal", "strategy.goal"),
        choices=("reach", "saves", "authority", "conversion", "community"),
    ),
    FieldSpec(
        "cta_type",
        "What CTA should it earn: follow or offer?",
        ("cta_type", "cta", "cta.type"),
        choices=("follow", "offer"),
    ),
    FieldSpec(
        "cta_pressure",
        "How much CTA pressure is acceptable: none, soft, medium, or hard?",
        ("cta_pressure", "strategy.cta_pressure", "cta.pressure"),
        choices=("none", "soft", "medium", "hard"),
    ),
    FieldSpec(
        "offer_url",
        "If this is an offer CTA, what short URL should appear on the slide?",
        ("offer_url", "url", "cta.url", "offer.url"),
        conditional_on=("cta_type", "offer"),
    ),
    FieldSpec(
        "offer_promise",
        "If this is an offer CTA, what does the offer promise?",
        ("offer_promise", "offer.promise", "cta.description", "offer_description"),
        min_words=4,
        conditional_on=("cta_type", "offer"),
    ),
    FieldSpec(
        "body_slide_count",
        "How many body slides should it use: 3, 5, 7, or 9?",
        ("body_slide_count", "slide_count", "preferred_body_slide_count"),
        current_required=False,
        choices=("3", "5", "7", "9"),
    ),
    FieldSpec(
        "tone",
        "What tone should this use?",
        ("tone", "voice", "profile.tone", "tone.primary"),
        min_words=2,
        current_required=False,
    ),
    FieldSpec(
        "visual_taste",
        "What visual direction should it lean toward?",
        ("visual_taste", "visual_style", "visual_direction", "profile.visual_preferences"),
        min_words=2,
        current_required=False,
        profile_aliases=("visual_preferences",),
    ),
    FieldSpec(
        "visual_avoid",
        "What visual style should it avoid?",
        ("visual_avoid", "visual_anti_taste", "visuals_to_avoid", "style_anti_patterns"),
        min_words=2,
        current_required=False,
        profile_aliases=("style_anti_patterns",),
    ),
    FieldSpec(
        "brand_colors",
        "What colors, fonts, logos, or brand constraints matter?",
        ("brand_colors", "colors", "brand", "profile.brand_colors"),
        current_required=False,
        profile_aliases=("brand_colors",),
    ),
    FieldSpec(
        "risk_appetite",
        "How aggressive should the hook be on a 1-10 scale?",
        ("risk_appetite", "hook_aggression", "risk", "profile.risk_appetite"),
        current_required=False,
    ),
    FieldSpec(
        "enemy_belief",
        "What enemy belief, bad advice, or false assumption should the carousel attack?",
        ("enemy_belief", "enemy", "bad_advice", "false_assumption"),
        min_words=5,
    ),
    FieldSpec(
        "personal_stakes",
        "What raw personal stakes, lived experience, or story can we include without exaggerating?",
        ("personal_stakes", "lived_experience", "story", "stakes"),
        min_words=5,
    ),
    FieldSpec(
        "claims_to_avoid",
        "What claims should we avoid or treat as needing evidence?",
        ("claims_to_avoid", "proof_boundaries", "claims_needing_evidence"),
        min_words=3,
        profile_aliases=("proof_boundaries",),
    ),
    FieldSpec(
        "saveable_reason",
        "What would make the viewer save this?",
        ("saveable_reason", "save_reason", "why_save"),
        min_words=5,
    ),
    FieldSpec(
        "shareable_reason",
        "What would make the viewer share this?",
        ("shareable_reason", "share_reason", "why_share"),
        min_words=5,
    ),
    FieldSpec(
        "distrust_reason",
        "What would make the viewer distrust this?",
        ("distrust_reason", "trust_risk", "why_distrust"),
        min_words=5,
    ),
    FieldSpec(
        "constraints",
        "Any platform, timeline, budget, proof, or technical constraints?",
        ("constraints", "limits", "technical_constraints", "platform_constraints"),
        min_words=3,
    ),
)


VAGUE_TERMS = {
    "viral",
    "valuable",
    "premium",
    "clean",
    "audience",
    "growth",
    "content",
    "creators",
    "businesses",
    "everyone",
    "people",
    "stuff",
    "things",
}


def load_interview_answers(path: str | Path | None) -> dict[str, Any]:
    """Load interview answers from YAML or JSON. Missing path means no answers yet."""

    if not path:
        return {}
    answer_path = Path(path)
    if not answer_path.exists():
        raise InterviewError(f"Interview answers file not found: {answer_path}")
    text = answer_path.read_text(encoding="utf-8")
    try:
        if answer_path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)
    except Exception as exc:  # pragma: no cover - exact parser message varies
        raise InterviewError(f"Could not parse interview answers: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise InterviewError("Interview answers must be a YAML or JSON object.")
    return data


def evaluate_interview(
    answers: dict[str, Any] | None,
    *,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the gate status, normalized answers, and next focused questions."""

    answers = answers or {}
    profile = profile or {}
    answered: dict[str, Any] = {}
    sources: dict[str, str] = {}
    missing: list[dict[str, str]] = []
    weak: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []

    for spec in FIELD_SPECS:
        if spec.conditional_on:
            dependency_key, dependency_value = spec.conditional_on
            dependency = str(answered.get(dependency_key, "")).strip().lower()
            if dependency != dependency_value:
                continue

        value, source = _lookup_value(spec, answers, profile)
        value = _canonical_value(spec, _normalize_value(value))
        if value not in (None, "", [], {}):
            answered[spec.key] = value
            sources[spec.key] = source

        if _is_missing(spec, value, source):
            reason = "Needs a current-carousel answer." if source == "profile" else "Missing answer."
            missing.append(_field_issue(spec, reason))
            continue

        if spec.choices and not _choice_matches(value, spec.choices):
            conflicts.append(_field_issue(spec, f"Must be one of: {', '.join(spec.choices)}."))
            continue

        vague_reason = _vague_reason(value, min_words=spec.min_words)
        if vague_reason:
            weak.append(_field_issue(spec, vague_reason))

    if str(answered.get("cta_type", "")).strip().lower() == "offer":
        if not answered.get("offer_url"):
            missing.append(_field_issue(_spec_for("offer_url"), "Offer CTA requires a visible short URL."))
        if not answered.get("offer_promise"):
            missing.append(_field_issue(_spec_for("offer_promise"), "Offer CTA requires a clear promise."))

    ready = not missing and not weak and not conflicts
    questions = _next_questions(missing, weak, conflicts)
    return {
        "ready_to_draft": ready,
        "status": "ready" if ready else "needs_answers",
        "answered": answered,
        "sources": sources,
        "missing": missing,
        "weak": weak,
        "conflicts": conflicts,
        "questions": questions,
        "ready_summary": _ready_summary(answered) if ready else None,
    }


def next_question_batch(
    answers: dict[str, Any] | None,
    *,
    profile: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return the next 3-5 focused questions for the skill to ask."""

    return evaluate_interview(answers, profile=profile)["questions"]


def require_ready_interview(
    answers: dict[str, Any] | None,
    *,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate the gate and raise when it is not ready."""

    report = evaluate_interview(answers, profile=profile)
    if not report["ready_to_draft"]:
        raise InterviewError("Mandatory interrogation gate is incomplete.")
    return report


def _lookup_value(
    spec: FieldSpec,
    answers: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[Any, str]:
    value = _first_value(answers, spec.aliases)
    if value not in (None, "", [], {}):
        return value, "answers"

    profile_aliases = spec.profile_aliases or spec.aliases
    value = _first_value(profile, profile_aliases)
    if value not in (None, "", [], {}):
        return value, "profile"
    return None, "missing"


def _first_value(data: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = _path_value(data, alias)
        if value not in (None, "", [], {}):
            return value
    for alias in aliases:
        key = alias.split(".")[-1]
        value = _deep_find(data, key)
        if value not in (None, "", [], {}):
            return value
    return None


def _path_value(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _deep_find(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            found = _deep_find(value, key)
            if found not in (None, "", [], {}):
                return found
    if isinstance(data, list):
        for item in data:
            found = _deep_find(item, key)
            if found not in (None, "", [], {}):
                return found
    return None


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.strip().split())
    if isinstance(value, list):
        cleaned = [_normalize_value(item) for item in value]
        return [item for item in cleaned if item not in (None, "", [], {})]
    if isinstance(value, dict):
        return {str(key): _normalize_value(item) for key, item in value.items() if item not in (None, "", [], {})}
    return value


def _is_missing(spec: FieldSpec, value: Any, source: str) -> bool:
    if value in (None, "", [], {}):
        return True
    return spec.current_required and source == "profile"


def _choice_matches(value: Any, choices: tuple[str, ...]) -> bool:
    normalized = str(value).strip().lower().replace("_", " ")
    if normalized in choices:
        return True
    if normalized == "soft offer" or normalized == "hard offer":
        return "offer" in choices
    return False


def _canonical_value(spec: FieldSpec, value: Any) -> Any:
    if value in (None, "", [], {}):
        return value
    if spec.key == "cta_type":
        normalized = str(value).strip().lower().replace("_", " ")
        if "offer" in normalized:
            return "offer"
        if normalized == "follow":
            return "follow"
    if spec.key == "proof_strength":
        return str(value).strip().lower().replace("-", " ")
    if spec.key in {"carousel_job", "cta_pressure"}:
        return str(value).strip().lower().replace("_", " ")
    if spec.key == "body_slide_count":
        try:
            return int(value)
        except (TypeError, ValueError):
            return value
    return value


def _vague_reason(value: Any, *, min_words: int) -> str | None:
    if isinstance(value, (int, float)):
        return None
    if isinstance(value, list):
        text = " ".join(str(item) for item in value)
    elif isinstance(value, dict):
        text = " ".join(str(item) for item in value.values())
    else:
        text = str(value)
    words = [word.strip(".,!?;:()[]{}\"'").lower() for word in text.split() if word.strip()]
    if len(words) < min_words:
        return f"Too thin; needs at least {min_words} specific words."
    vague_hits = sorted({word for word in words if word in VAGUE_TERMS})
    if vague_hits and len(words) <= min_words:
        return f"Too vague: {', '.join(vague_hits)}."
    return None


def _field_issue(spec: FieldSpec, reason: str) -> dict[str, str]:
    return {"field": spec.key, "reason": reason, "question": spec.question}


def _next_questions(
    missing: list[dict[str, str]],
    weak: list[dict[str, str]],
    conflicts: list[dict[str, str]],
) -> list[dict[str, str]]:
    seen: set[str] = set()
    questions: list[dict[str, str]] = []
    for issue in [*conflicts, *missing, *weak]:
        field = issue["field"]
        if field in seen:
            continue
        seen.add(field)
        questions.append(
            {
                "field": field,
                "question": issue["question"],
                "reason": issue["reason"],
            }
        )
        if len(questions) == 5:
            break
    return questions


def _spec_for(key: str) -> FieldSpec:
    return next(spec for spec in FIELD_SPECS if spec.key == key)


def _ready_summary(answered: dict[str, Any]) -> str:
    return (
        "Ready to generate: "
        f"{answered.get('target_viewer')} needs {answered.get('belief_shift')}, "
        f"backed by {answered.get('proof_strength')}, in a {answered.get('tone')} / "
        f"{answered.get('visual_taste')} carousel with {answered.get('body_slide_count')} "
        f"body slides and a {answered.get('cta_type')} CTA."
    )
