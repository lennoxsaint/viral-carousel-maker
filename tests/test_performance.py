import json

import pytest

from viral_carousel_maker.performance import add_metrics, diagnose_record, summarize_metrics


def write_manifest(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "title": "Threads growth is a lie",
                "handle": "@tester",
                "template_family": "debate",
                "design": {"design_pack": "brutal-proof", "visual_modes": ["shock-stat"]},
                "strategy": {
                    "goal": "reach",
                    "hook_archetype": "lie",
                    "belief_shift": "Old: growth is followers. New: growth is repeated demand.",
                },
                "virality": {"score": 9.1},
                "slides": [{"role": "hook", "title": "Threads growth is a lie"}],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_metrics_add_and_report(tmp_path):
    manifest = write_manifest(tmp_path)
    ledger = tmp_path / "metrics.jsonl"
    record = add_metrics(
        manifest,
        {"views": 12000, "likes": 200, "saves": 10, "clicks": 2},
        ledger_path=ledger,
    )
    assert "high views / low saves" in record["diagnosis"]

    report = summarize_metrics(days=30, ledger_path=ledger)
    assert report["records"] == 1
    assert report["totals"]["views"] == 12000
    assert report["top_hook_categories"][0][0] == "lie"
    assert report["top_visual_packs"][0][0] == "brutal-proof"
    assert report["learning_summary"]["best_visual_packs"][0][0] == "brutal-proof"


def test_metrics_refuses_secret_storage(tmp_path):
    manifest = write_manifest(tmp_path)
    with pytest.raises(ValueError, match="secret"):
        add_metrics(manifest, {"notes": "sk-test123"}, ledger_path=tmp_path / "metrics.jsonl")


def test_diagnosis_rules():
    assert "hook" in diagnose_record({"views": 500, "saves": 30, "clicks": 0})
    assert "landing" in diagnose_record({"views": 5000, "saves": 200, "clicks": 40, "conversions": 0})
    assert "reset" in diagnose_record({"views": 200, "saves": 2, "clicks": 1})
