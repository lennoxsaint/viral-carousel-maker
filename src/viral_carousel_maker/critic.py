"""Structured AI critic gate helpers.

The actual critique is produced by the host AI during the skill workflow. This
module validates and normalizes that critique so manifests keep a stable shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCORE_FIELDS = (
    "hook_strength",
    "belief_shift",
    "specificity",
    "proof_integrity",
    "cta_fit",
    "visual_thesis",
    "slide_density",
    "saveability",
    "shareability",
)


def load_critic(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Critic output must be a JSON object.")
    return data


def validate_critic_output(critic: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    scores = critic.get("scores")
    if not isinstance(scores, dict):
        errors.append("critic.scores must be an object.")
        scores = {}
    for field in SCORE_FIELDS:
        value = scores.get(field)
        if not isinstance(value, (int, float)):
            errors.append(f"critic.scores.{field} must be a number.")
        elif value < 1 or value > 10:
            errors.append(f"critic.scores.{field} must be between 1 and 10.")
    verdict = str(critic.get("verdict", "")).lower()
    if verdict not in {"pass", "revise", "fail"}:
        errors.append("critic.verdict must be pass, revise, or fail.")
    blockers = critic.get("blockers", [])
    if not isinstance(blockers, list):
        errors.append("critic.blockers must be a list.")
    if verdict == "pass" and any(float(scores.get(field, 0) or 0) < 8 for field in SCORE_FIELDS):
        errors.append("critic cannot pass while any score is below 8.")
    return not errors, errors


def normalize_critic_output(critic: dict[str, Any] | None) -> dict[str, Any]:
    if not critic:
        return {
            "status": "missing",
            "verdict": "not-run",
            "scores": {},
            "blockers": ["AI critic gate has not been attached to this spec."],
            "revision_notes": [],
        }
    ok, errors = validate_critic_output(critic)
    normalized = dict(critic)
    normalized["status"] = "pass" if ok and str(critic.get("verdict", "")).lower() == "pass" else "needs-revision"
    if errors:
        normalized["validation_errors"] = errors
    normalized.setdefault("revision_notes", [])
    normalized.setdefault("blockers", [])
    return normalized
