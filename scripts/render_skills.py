#!/usr/bin/env python3
"""Render canonical skill source into Claude and Codex target folders."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "source" / "viral-carousel-maker"
DIST = ROOT / "skills" / "dist"
TARGETS = {
    "claude": {
        "label": "Claude Code",
        "skill_root": "~/.claude/skills",
        "path": DIST / "claude" / "viral-carousel-maker",
        "install": Path.home() / ".claude" / "skills" / "viral-carousel-maker",
    },
    "codex": {
        "label": "Codex",
        "skill_root": "~/.codex/skills",
        "path": DIST / "codex" / "viral-carousel-maker",
        "install": Path.home() / ".codex" / "skills" / "viral-carousel-maker",
    },
}


def hash_tree(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file_path.relative_to(path).as_posix()
        result[rel] = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return result


def strip_existing_adapter(text: str) -> str:
    return re.sub(
        r"<!-- BEGIN GENERATED: platform-adapter -->.*?<!-- END GENERATED: platform-adapter -->\n*",
        "",
        text,
        flags=re.DOTALL,
    )


def adapter_block(target: str) -> str:
    info = TARGETS[target]
    if target == "claude":
        platform_notes = (
            "- In Claude Desktop or Claude Code, require `OPENAI_API_KEY` before the intended OpenAI image-generation workflow.\n"
            "- If the key is missing, pause and show the API-key onboarding message from `SKILL.md`.\n"
            "- If the user declines a key, offer procedural draft rendering and clearly label it as the fallback path.\n"
            "- Readiness check: `viral-carousel doctor --platform claude-code`.\n"
            "- API key setup guide: `references/claude-openai-api-key-setup.md`.\n"
        )
    else:
        platform_notes = (
            "- In Codex, prefer native image generation and do not require `OPENAI_API_KEY`.\n"
            "- If native image generation is unavailable, continue with procedural renderer assets rather than blocking.\n"
            "- Readiness check: `viral-carousel doctor --platform codex`.\n"
        )
    return (
        "<!-- BEGIN GENERATED: platform-adapter -->\n"
        "## Platform Adapter\n\n"
        f"- Rendered for: {info['label']}.\n"
        f"- Skill root: `{info['skill_root']}`.\n"
        "- Canonical source: `skills/source/viral-carousel-maker`.\n"
        f"{platform_notes}"
        "<!-- END GENERATED: platform-adapter -->\n\n"
    )


def render_skill_md(source: Path, dest: Path, target: str) -> None:
    text = strip_existing_adapter(source.read_text(encoding="utf-8"))
    parts = text.split("---\n", 2)
    if len(parts) == 3 and parts[0] == "":
        rendered = f"---\n{parts[1]}---\n\n{adapter_block(target)}{parts[2].lstrip()}"
    else:
        rendered = f"{adapter_block(target)}{text}"
    dest.write_text(rendered, encoding="utf-8")


def copy_tree(source: Path, dest: Path, target: str) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        out = dest / rel
        if path.is_dir():
            out.mkdir(parents=True, exist_ok=True)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        if path.name == "SKILL.md":
            render_skill_md(path, out, target)
        else:
            shutil.copy2(path, out)


def render_all(check: bool = False) -> int:
    with tempfile.TemporaryDirectory(prefix="viral-carousel-skill-render-") as tmp:
        tmp_root = Path(tmp)
        changed = False
        for target, info in TARGETS.items():
            rendered = tmp_root / target
            copy_tree(SOURCE, rendered, target)
            before = hash_tree(info["path"])
            after = hash_tree(rendered)
            target_changed = before != after
            changed = changed or target_changed
            status = "changed" if target_changed else "unchanged"
            print(f"{target}: {status}")
            if not check:
                copy_tree(SOURCE, info["path"], target)
    return 1 if check and changed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not SOURCE.exists():
        print(f"Missing source skill: {SOURCE}", file=sys.stderr)
        return 1
    return render_all(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
