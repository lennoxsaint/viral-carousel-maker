#!/usr/bin/env python3
"""Project validation used by CI and local development."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    print("+", " ".join(command))
    env = {"PYTHONPATH": str(ROOT / "src")}
    return subprocess.call(command, cwd=ROOT, env={**os.environ, **env})


def main() -> int:
    commands = [
        [sys.executable, "scripts/render_skills.py", "--check"],
        [sys.executable, "-m", "viral_carousel_maker.cli", "render", "examples/specs/ai-framework.yaml", "--out-dir", "output/check", "--dry-run"],
    ]
    for command in commands:
        code = run(command)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
