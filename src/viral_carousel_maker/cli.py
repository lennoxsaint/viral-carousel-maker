"""Command line interface for Viral Carousel Maker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .assets import generate_openai_asset, write_prompts_jsonl
from .profile import init_profile
from .qa import load_manifest, run_manifest_qa, write_qa_report
from .renderer import CarouselRenderer
from .spec import load_spec, validate_spec


def render_command(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    warnings = validate_spec(spec)
    if args.dry_run:
        print(json.dumps({"status": "ok", "warnings": warnings}, indent=2))
        return 0
    manifest = CarouselRenderer(spec, args.out_dir).render()
    print(json.dumps({"manifest": str(Path(args.out_dir) / "manifest.json"), "slides": len(manifest["slides"])}, indent=2))
    return 0


def prompts_command(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    validate_spec(spec)
    path = write_prompts_jsonl(spec, Path(args.out))
    print(path)
    return 0


def qa_command(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    ok, messages = run_manifest_qa(manifest)
    if args.report:
        write_qa_report(manifest, args.report)
    print(json.dumps({"ok": ok, "messages": messages}, indent=2))
    return 0 if ok else 1


def profile_command(args: argparse.Namespace) -> int:
    path = init_profile(args.path)
    print(path)
    return 0


def generate_asset_command(args: argparse.Namespace) -> int:
    path = generate_openai_asset(args.prompt, Path(args.out), model=args.model)
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="viral-carousel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render a carousel spec to PNGs.")
    render.add_argument("spec")
    render.add_argument("--out-dir", required=True)
    render.add_argument("--dry-run", action="store_true")
    render.set_defaults(func=render_command)

    prompts = subparsers.add_parser("prompts", help="Write visual prompts JSONL.")
    prompts.add_argument("spec")
    prompts.add_argument("--out", required=True)
    prompts.set_defaults(func=prompts_command)

    qa = subparsers.add_parser("qa", help="Run QA against a manifest.")
    qa.add_argument("manifest")
    qa.add_argument("--report")
    qa.set_defaults(func=qa_command)

    profile = subparsers.add_parser("profile-init", help="Create a local profile template.")
    profile.add_argument("--path")
    profile.set_defaults(func=profile_command)

    gen_asset = subparsers.add_parser(
        "generate-asset",
        help="Optional OpenAI API fallback for Claude/local environments.",
    )
    gen_asset.add_argument("--prompt", required=True)
    gen_asset.add_argument("--out", required=True)
    gen_asset.add_argument("--model", default="gpt-image-2")
    gen_asset.set_defaults(func=generate_asset_command)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

