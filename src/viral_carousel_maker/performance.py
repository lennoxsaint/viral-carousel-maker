"""Manual Threads performance ledger for carousel packs."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from typing import Any


LEDGER_DIR = Path.home() / ".viral-carousel-maker" / "performance"
LEDGER_PATH = LEDGER_DIR / "metrics.jsonl"
SECRET_MARKERS = ("sk-", "OPENAI_API_KEY", "api_key", "secret_key", "bearer ")


def add_metrics(
    manifest_path: str | Path,
    metrics: dict[str, Any],
    ledger_path: str | Path | None = None,
) -> dict[str, Any]:
    """Append one performance record and return the stored record."""

    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    safe_metrics = _sanitize_metrics(metrics)
    record = {
        "recorded_at": datetime.now(UTC).isoformat(),
        "manifest_path": str(manifest_file),
        "title": manifest.get("title", ""),
        "handle": manifest.get("handle", ""),
        "template_family": manifest.get("template_family", ""),
        "design_pack": _design_pack_from_manifest(manifest, safe_metrics),
        "visual_modes": (manifest.get("design") or {}).get("visual_modes", []),
        "hook": _hook_from_manifest(manifest),
        "strategy": _safe_strategy(manifest.get("strategy", {})),
        "body_slide_count": _body_slide_count(manifest, safe_metrics),
        "virality_score": (manifest.get("virality") or {}).get("score"),
        **safe_metrics,
    }
    record["diagnosis"] = diagnose_record(record)
    _write_record(record, _resolve_ledger(ledger_path))
    return record


def summarize_metrics(days: int = 30, ledger_path: str | Path | None = None) -> dict[str, Any]:
    ledger = _resolve_ledger(ledger_path)
    records = list(_read_records(ledger))
    cutoff = datetime.now(UTC) - timedelta(days=days)
    recent = [record for record in records if _parse_time(record.get("recorded_at")) >= cutoff]
    totals = {
        "views": sum(int(record.get("views", 0)) for record in recent),
        "likes": sum(int(record.get("likes", 0)) for record in recent),
        "replies": sum(int(record.get("replies", 0)) for record in recent),
        "reposts": sum(int(record.get("reposts", 0)) for record in recent),
        "saves": sum(int(record.get("saves", 0)) for record in recent),
        "clicks": sum(int(record.get("clicks", 0)) for record in recent),
        "conversions": sum(int(record.get("conversions", 0)) for record in recent),
    }
    hook_categories = Counter(
        str((record.get("strategy") or {}).get("hook_archetype") or "unknown") for record in recent
    )
    visual_packs = Counter(str(record.get("design_pack") or "unknown") for record in recent)
    diagnoses = Counter(str(record.get("diagnosis") or "unknown") for record in recent)
    return {
        "days": days,
        "ledger_path": str(ledger),
        "records": len(recent),
        "totals": totals,
        "top_hook_categories": hook_categories.most_common(5),
        "top_visual_packs": visual_packs.most_common(5),
        "learning_summary": build_learning_summary(recent),
        "diagnoses": diagnoses.most_common(),
    }


def build_learning_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "winning_hooks": [],
            "weak_hooks": [],
            "best_visual_packs": [],
            "best_cta_pressure": "unknown",
            "best_body_slide_count": "unknown",
            "topics_that_earned_saves": [],
        }
    ranked = sorted(records, key=lambda record: _save_rate(record), reverse=True)
    weak = sorted(records, key=lambda record: int(record.get("views", 0)), reverse=True)
    weak = [record for record in weak if _save_rate(record) < 0.002]
    cta = Counter(str((record.get("strategy") or {}).get("cta_pressure") or record.get("cta_pressure") or "unknown") for record in ranked[:10])
    body_counts = Counter(str(record.get("body_slide_count") or "unknown") for record in ranked[:10])
    visual_packs = Counter(str(record.get("design_pack") or "unknown") for record in ranked[:10])
    return {
        "winning_hooks": [
            {
                "hook": record.get("hook", ""),
                "category": (record.get("strategy") or {}).get("hook_archetype", "unknown"),
                "save_rate": round(_save_rate(record), 4),
            }
            for record in ranked[:5]
        ],
        "weak_hooks": [
            {
                "hook": record.get("hook", ""),
                "category": (record.get("strategy") or {}).get("hook_archetype", "unknown"),
                "diagnosis": record.get("diagnosis", ""),
            }
            for record in weak[:5]
        ],
        "best_visual_packs": visual_packs.most_common(5),
        "best_cta_pressure": cta.most_common(1)[0][0] if cta else "unknown",
        "best_body_slide_count": body_counts.most_common(1)[0][0] if body_counts else "unknown",
        "topics_that_earned_saves": [
            record.get("title", "") for record in ranked[:5] if int(record.get("saves", 0)) > 0
        ],
    }


def diagnose_record(record: dict[str, Any]) -> str:
    views = max(0, int(record.get("views", 0)))
    saves = max(0, int(record.get("saves", 0)))
    clicks = max(0, int(record.get("clicks", 0)))
    conversions = max(0, int(record.get("conversions", 0)))

    save_rate = saves / views if views else 0
    click_conversion_rate = conversions / clicks if clicks else 0

    if views >= 10_000 and save_rate < 0.002:
        return "high views / low saves: value may be too shallow"
    if 0 < views < 2_000 and saves >= 25:
        return "low views / high saves: hook or first-slide problem"
    if clicks >= 25 and click_conversion_rate < 0.03:
        return "high clicks / low conversions: offer or landing mismatch"
    if views < 1_000 and saves < 10 and clicks < 5:
        return "low everything: reset angle, hook, and value promise"
    return "keep testing: useful signal but no hard diagnosis"


def _sanitize_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "views",
        "likes",
        "replies",
        "reposts",
        "saves",
        "clicks",
        "conversions",
        "published_at",
        "publish_time",
        "hook_category",
        "visual_pack",
        "cta_pressure",
        "body_slide_count",
        "notes",
    }
    sanitized: dict[str, Any] = {}
    for key, value in metrics.items():
        if key not in allowed:
            continue
        if isinstance(value, str):
            _reject_secret(value)
            sanitized[key] = value.strip()
        else:
            sanitized[key] = int(value or 0)
    for key in ("views", "likes", "replies", "reposts", "saves", "clicks", "conversions"):
        sanitized.setdefault(key, 0)
    return sanitized


def _safe_strategy(strategy: Any) -> dict[str, Any]:
    if not isinstance(strategy, dict):
        return {}
    safe: dict[str, Any] = {}
    for key in (
        "goal",
        "hook_archetype",
        "belief_shift",
        "proof_level",
        "cta_pressure",
        "visual_thesis",
        "virality_principles",
        "design_pack",
    ):
        value = strategy.get(key)
        if isinstance(value, str):
            _reject_secret(value)
            safe[key] = value
        elif isinstance(value, list):
            safe[key] = [str(item) for item in value if not _contains_secret(str(item))]
    return safe


def _hook_from_manifest(manifest: dict[str, Any]) -> str:
    for slide in manifest.get("slides", []):
        if slide.get("role") == "hook":
            return str(slide.get("title", ""))
    return str(manifest.get("title", ""))


def _design_pack_from_manifest(manifest: dict[str, Any], metrics: dict[str, Any]) -> str:
    return str(
        metrics.get("visual_pack")
        or manifest.get("design_pack")
        or (manifest.get("design") or {}).get("design_pack")
        or "unknown"
    )


def _body_slide_count(manifest: dict[str, Any], metrics: dict[str, Any]) -> int:
    if metrics.get("body_slide_count") is not None:
        return int(metrics.get("body_slide_count") or 0)
    return sum(1 for slide in manifest.get("slides", []) if slide.get("role") == "body")


def _save_rate(record: dict[str, Any]) -> float:
    views = max(0, int(record.get("views", 0)))
    saves = max(0, int(record.get("saves", 0)))
    return saves / views if views else 0


def _write_record(record: dict[str, Any], ledger_path: Path) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    _reject_secret(json.dumps(record))
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _read_records(ledger_path: Path):
    if not ledger_path.exists():
        return
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def _parse_time(value: Any) -> datetime:
    if not value:
        return datetime.fromtimestamp(0, tz=UTC)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.fromtimestamp(0, tz=UTC)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _resolve_ledger(ledger_path: str | Path | None) -> Path:
    return Path(ledger_path).expanduser() if ledger_path else LEDGER_PATH


def _contains_secret(value: str) -> bool:
    lower = value.lower()
    return any(marker.lower() in lower for marker in SECRET_MARKERS)


def _reject_secret(value: str) -> None:
    if _contains_secret(value):
        raise ValueError("Refusing to store a value that looks like an API key or secret.")
