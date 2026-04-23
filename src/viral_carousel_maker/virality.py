"""Static virality checks for carousel specs.

These checks are deliberately conservative. They do not promise virality; they
catch the predictable mistakes that make Threads carousels feel generic,
overstuffed, or like thin sales pages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any


WEAK_HOOK_OPENERS = (
    "how to ",
    "here are ",
    "here's how ",
    "want to ",
    "save this",
    "follow for",
    "comment below",
    "drop a ",
    "like this",
    "the ultimate guide",
    "a complete guide",
)

FAKE_URGENCY_PATTERNS = (
    "before it's too late",
    "right now or",
    "now or never",
    "you need to see this",
    "don't miss",
    "last chance",
)

TRIGGER_WORDS = {
    "hack",
    "hacks",
    "secret",
    "secrets",
    "skyrocket",
    "explode",
    "crush",
    "guaranteed",
    "instantly",
    "overnight",
    "growth journey",
    "game changer",
}

CTA_PRESSURE_WORDS = {
    "buy",
    "book",
    "dm me",
    "comment",
    "link in bio",
    "save this",
    "follow",
    "subscribe",
    "download",
}

HOOK_ARCHETYPE_TERMS = {
    "shock_stat": ("%", "x", "every", "nobody", "most"),
    "lie": ("lie", "myth", "wrong", "not"),
    "confession": ("i was wrong", "i got this wrong", "i used to"),
    "enemy_belief": ("stop", "bad", "enemy", "mistake", "trap"),
    "identity_mirror": ("you are", "you may", "your ", "creators", "founders"),
    "proof_receipt": ("after", "before", "receipt", "proof", "client"),
}


@dataclass
class ViralityAudit:
    score: float
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 2),
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def score_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Return a serializable virality audit for a carousel spec."""

    return audit_spec(spec).to_dict()


def audit_spec(spec: dict[str, Any]) -> ViralityAudit:
    slides = [slide for slide in spec.get("slides", []) if isinstance(slide, dict)]
    hook = next((slide for slide in slides if slide.get("role") == "hook"), {})
    body_slides = [slide for slide in slides if slide.get("role") == "body"]
    cta_slide = next((slide for slide in slides if slide.get("role") == "cta"), {})
    strategy = spec.get("strategy") if isinstance(spec.get("strategy"), dict) else {}

    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {
        "body_slide_count": len(body_slides),
        "hook_archetype_guess": guess_hook_archetype(hook),
        "hook_word_count": count_words(_slide_text(hook, include_body=False)),
        "max_body_words": 0,
        "slides_with_multiple_ideas": [],
    }

    hook_title = str(hook.get("title", "")).strip()
    hook_subtitle = str(hook.get("subtitle", "")).strip()
    hook_text = _slide_text(hook, include_body=False)
    hook_lower = _normalize(hook_title)

    weak_opener = detect_weak_hook_opener(hook_title)
    if weak_opener:
        errors.append(f"Hook uses banned weak opener '{weak_opener}'. Rewrite as an observation, contradiction, or identity mirror.")

    if "?" in hook_title and not looks_like_identity_mirror_question(hook_title):
        errors.append("Hook is a homework-style question. Rewrite it as a confident statement.")

    if count_words(hook_title) > 16:
        errors.append("Hook headline is too long for feed speed; compress it under 16 words.")
    elif count_words(hook_title) > 11:
        warnings.append("Hook headline is usable but long; consider compressing it under 11 words.")

    if contains_fake_urgency(hook_text):
        errors.append("Hook uses fake urgency. Replace urgency with tension, proof, or a sharper belief shift.")

    trigger_hits = find_trigger_words(hook_text)
    if trigger_hits:
        warnings.append(f"Hook contains generic trigger words: {', '.join(trigger_hits)}.")

    belief_shift = str(strategy.get("belief_shift", "")).strip()
    strategy_has_virality_claim = any(
        key in strategy
        for key in ("goal", "hook_archetype", "proof_level", "cta_pressure", "virality_principles")
    )
    if strategy_has_virality_claim and not belief_shift:
        errors.append("Strategy is missing belief_shift; name the old belief and the new belief before rendering.")

    goal = str(strategy.get("goal", "")).strip().lower()
    if goal == "reach" and len(body_slides) > 3:
        warnings.append("Reach mode usually performs better with 3 body slides; 5+ should be justified by proof or story.")
    if len(body_slides) in {7, 9} and not _has_any(strategy, "proof_level", "raw_stakes", "lived_stakes"):
        warnings.append("Long carousels need proof, raw stakes, or story. Information alone usually fades.")

    for index, slide in enumerate(body_slides, start=1):
        words = count_words(_slide_text(slide))
        metrics["max_body_words"] = max(metrics["max_body_words"], words)
        if words > 55:
            errors.append(f"Body slide {index} is too dense at {words} words; cut to one main idea.")
        elif words > 42:
            warnings.append(f"Body slide {index} is dense at {words} words; consider cutting it.")
        if has_multiple_ideas(slide):
            metrics["slides_with_multiple_ideas"].append(slide.get("id") or slide.get("title") or index)
            warnings.append(f"Body slide {index} may contain multiple ideas; split or compress it.")

    cta = cta_slide.get("cta", spec.get("cta", {}))
    if isinstance(cta, dict):
        cta_pressure = score_cta_pressure(cta, cta_slide)
        metrics["cta_pressure_score"] = cta_pressure
        desired_pressure = str(strategy.get("cta_pressure", "")).lower()
        if cta_pressure >= 6 and desired_pressure == "soft":
            errors.append("CTA is marked soft but reads high-pressure. Reduce the ask or earn it with clearer value.")
        elif cta_pressure >= 7:
            warnings.append("CTA is high-pressure; make sure the carousel earns it.")

    hook_score = score_hook(hook_title, hook_text, belief_shift)
    hook_stop_score = score_hook_stop(hook_title, hook_subtitle, belief_shift)
    density_score = max(0.0, 10.0 - max(0, metrics["max_body_words"] - 32) * 0.12)
    cta_score = max(0.0, 10.0 - metrics.get("cta_pressure_score", 0) * 0.6)
    score = round((hook_score * 0.46) + (density_score * 0.34) + (cta_score * 0.20), 2)
    metrics["hook_stop_score"] = round(hook_stop_score, 2)

    hook_priority = str(strategy.get("hook_priority") or strategy.get("scroll_stop_priority") or "").lower()
    if hook_priority in {"high", "extreme", "thumbnail"} and hook_stop_score < 8.5:
        errors.append(
            f"Hook scroll-stop score is {hook_stop_score:.2f}/10; {hook_priority} priority requires 8.5+."
        )
    elif hook_stop_score < 7.8:
        warnings.append(
            f"Hook scroll-stop score is {hook_stop_score:.2f}/10; compress and polarize the opener further."
        )

    if hook_lower.startswith("the ") and not any(term in hook_lower for term in ("lie", "wrong", "trap", "cost")):
        warnings.append("Hook starts broad. Strong Threads hooks usually start with tension, not a neutral label.")
    if score < 8.5:
        warnings.append(f"Virality score is {score}/10; revise until it clears 8.5 before final production.")

    metrics["hook_score"] = round(hook_score, 2)
    metrics["density_score"] = round(density_score, 2)
    metrics["cta_score"] = round(cta_score, 2)
    return ViralityAudit(score=score, ok=not errors, errors=errors, warnings=warnings, metrics=metrics)


def detect_weak_hook_opener(text: str) -> str | None:
    normalized = _normalize(text)
    for opener in WEAK_HOOK_OPENERS:
        if normalized.startswith(opener):
            return opener.strip()
    if re.match(r"^\d+\s+(tips|ways|steps|ideas)\b", normalized):
        return "numbered how-to opener"
    return None


def looks_like_identity_mirror_question(text: str) -> bool:
    normalized = _normalize(text)
    return normalized.startswith(("are you ", "is your ", "do you still ")) and any(
        token in normalized for token in ("still", "actually", "really")
    )


def contains_fake_urgency(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern in normalized for pattern in FAKE_URGENCY_PATTERNS)


def find_trigger_words(text: str) -> list[str]:
    normalized = _normalize(text)
    hits = [word for word in TRIGGER_WORDS if re.search(rf"\b{re.escape(word)}\b", normalized)]
    return sorted(hits)


def has_multiple_ideas(slide: dict[str, Any]) -> bool:
    main_idea = str(slide.get("main_idea", "")).strip()
    if main_idea:
        return False
    text = _slide_text(slide)
    separators = text.count(";") + text.count(" and ") + text.count(" also ") + text.count(" plus ")
    bullets = slide.get("bullets", []) or []
    return len(bullets) > 3 or separators >= 3


def score_cta_pressure(cta: dict[str, Any], slide: dict[str, Any] | None = None) -> int:
    text = " ".join(
        str(part)
        for part in (
            cta.get("type", ""),
            cta.get("label", ""),
            cta.get("description", ""),
            cta.get("url", ""),
            (slide or {}).get("title", ""),
            (slide or {}).get("subtitle", ""),
        )
        if part
    )
    normalized = _normalize(text)
    score = 0
    for phrase in CTA_PRESSURE_WORDS:
        if phrase in normalized:
            score += 2 if phrase in {"buy", "book", "dm me", "link in bio"} else 1
    if str(cta.get("type", "")).lower() == "offer":
        score += 2
    if cta.get("url"):
        score += 1
    return score


def score_hook(title: str, full_text: str, belief_shift: str = "") -> float:
    normalized = _normalize(f"{title} {full_text}")
    score = 6.0
    if any(term in normalized for term in ("not ", "lie", "wrong", "trap", "vs", "cost")):
        score += 1.1
    if any(char.isdigit() for char in title):
        score += 0.7
    if any(term in normalized for term in ("you ", "your ", "creators", "founders", "clients")):
        score += 0.7
    if belief_shift:
        score += 0.8
    if count_words(title) <= 8:
        score += 0.5
    if detect_weak_hook_opener(title):
        score -= 2.0
    if contains_fake_urgency(full_text):
        score -= 1.5
    return min(10.0, max(0.0, score))


def score_hook_stop(title: str, subtitle: str = "", belief_shift: str = "") -> float:
    """Score copy-only hook stop power for opening slides."""

    normalized_title = _normalize(title)
    normalized_subtitle = _normalize(subtitle)
    score = 5.0
    title_words = count_words(title)
    subtitle_words = count_words(subtitle)

    if title_words <= 8:
        score += 1.5
    elif title_words <= 11:
        score += 0.8
    elif title_words > 14:
        score -= 0.8

    if subtitle:
        if subtitle_words <= 12:
            score += 0.7
        elif subtitle_words > 18:
            score -= 0.4

    if any(token in normalized_title for token in ("not ", "lie", "wrong", "dead", "invisible", "never", "stop")):
        score += 1.2
    if any(token in normalized_title for token in ("you ", "your ", "creators", "founders")):
        score += 0.6
    if belief_shift:
        score += 0.8
    if detect_weak_hook_opener(title):
        score -= 2.2
    if "?" in title and not looks_like_identity_mirror_question(title):
        score -= 1.4
    if subtitle and normalized_title == normalized_subtitle:
        score -= 0.8

    return max(0.0, min(10.0, round(score, 2)))


def guess_hook_archetype(hook: dict[str, Any]) -> str:
    text = _normalize(_slide_text(hook, include_body=False))
    for archetype, terms in HOOK_ARCHETYPE_TERMS.items():
        if any(term in text for term in terms):
            return archetype
    return "private_room_observation"


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text))


def _slide_text(slide: dict[str, Any], include_body: bool = True) -> str:
    parts = [str(slide.get("title", "")), str(slide.get("subtitle", ""))]
    if include_body:
        parts.append(str(slide.get("body", "")))
        parts.extend(str(item) for item in slide.get("bullets", []) or [])
    return " ".join(part for part in parts if part)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _has_any(mapping: dict[str, Any], *keys: str) -> bool:
    return any(str(mapping.get(key, "")).strip() for key in keys)
