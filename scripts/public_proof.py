#!/usr/bin/env python3
"""Validate or regenerate public showcase proof artifacts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GALLERY_DIR = ROOT / "docs" / "assets" / "gallery"
SPECS_DIR = ROOT / "examples" / "specs"
GENERATED_DIR = ROOT / "examples" / "generated"


def gallery_names() -> list[str]:
    return sorted(path.name for path in GALLERY_DIR.iterdir() if path.is_dir())


def check_gallery() -> int:
    errors: list[str] = []
    for name in gallery_names():
        gallery = GALLERY_DIR / name
        spec = SPECS_DIR / f"{name}.yaml"
        generated = GENERATED_DIR / name
        required = [
            gallery / "hook.png",
            gallery / "contact_sheet.png",
            gallery / "summary.json",
            spec,
            generated / "manifest.json",
            generated / "qa_report.md",
        ]
        for path in required:
            if not path.exists():
                errors.append(f"Missing public proof artifact: {path.relative_to(ROOT)}")
        summary_path = gallery / "summary.json"
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if summary.get("visual_qa") != "pass":
                errors.append(f"Gallery summary is not pass: {summary_path.relative_to(ROOT)}")
            if not summary.get("slides"):
                errors.append(f"Gallery summary missing slide count: {summary_path.relative_to(ROOT)}")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"ok": True, "packs": gallery_names()}, indent=2))
    return 0


def run_showcase(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, object]] = []
    if _run([sys.executable, "-m", "viral_carousel_maker.cli", "critic", "validate", "examples/critic-pass.json"]):
        return 1
    for name in gallery_names():
        spec = SPECS_DIR / f"{name}.yaml"
        pack_dir = out_dir / name
        if pack_dir.exists():
            shutil.rmtree(pack_dir)
        if _run([sys.executable, "-m", "viral_carousel_maker.cli", "score", str(spec.relative_to(ROOT))]):
            return 1
        if _run(
            [
                sys.executable,
                "-m",
                "viral_carousel_maker.cli",
                "render",
                str(spec.relative_to(ROOT)),
                "--out-dir",
                str(pack_dir.relative_to(ROOT)),
            ]
        ):
            return 1
        if _run([sys.executable, "-m", "viral_carousel_maker.cli", "qa", str((pack_dir / "manifest.json").relative_to(ROOT))]):
            return 1
        manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
        visual_qa = manifest.get("visual_qa") if isinstance(manifest.get("visual_qa"), dict) else {}
        summary.append(
            {
                "name": name,
                "title": manifest.get("title", ""),
                "slides": len(manifest.get("slides", [])),
                "visual_qa": visual_qa.get("status", "unknown"),
                "manifest": str((pack_dir / "manifest.json").relative_to(ROOT)),
                "contact_sheet": str((pack_dir / "contact_sheet.png").relative_to(ROOT)),
            }
        )
    (out_dir / "showcase-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "summary": str((out_dir / "showcase-summary.json").relative_to(ROOT))}, indent=2))
    return 0


def _run(command: list[str]) -> int:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    print("+", " ".join(command))
    return subprocess.call(command, cwd=ROOT, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-gallery", action="store_true")
    parser.add_argument("--run-showcase", action="store_true")
    parser.add_argument("--out-dir", default="output/public-proof")
    args = parser.parse_args()
    if args.run_showcase:
        return run_showcase(ROOT / args.out_dir)
    return check_gallery()


if __name__ == "__main__":
    raise SystemExit(main())
