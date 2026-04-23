"""Command line interface for Viral Carousel Maker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .assets import generate_openai_asset, write_prompts_jsonl
from .performance import add_metrics, summarize_metrics
from .profile import init_profile
from .qa import load_manifest, run_manifest_qa, write_qa_report
from .renderer import CarouselRenderer
from .spec import load_spec, validate_spec
from .virality import score_spec


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


def score_command(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    validate_spec(spec)
    print(json.dumps(score_spec(spec), indent=2))
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


def metrics_add_command(args: argparse.Namespace) -> int:
    metrics = {
        "views": args.views,
        "likes": args.likes,
        "replies": args.replies,
        "reposts": args.reposts,
        "saves": args.saves,
        "clicks": args.clicks,
        "conversions": args.conversions,
    }
    if args.published_at:
        metrics["published_at"] = args.published_at
    if args.notes:
        metrics["notes"] = args.notes
    record = add_metrics(args.manifest, metrics, ledger_path=args.ledger)
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


def metrics_report_command(args: argparse.Namespace) -> int:
    report = summarize_metrics(days=args.days, ledger_path=args.ledger)
    print(json.dumps(report, indent=2, sort_keys=True))
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

    score = subparsers.add_parser("score", help="Score a carousel spec for virality blockers.")
    score.add_argument("spec")
    score.set_defaults(func=score_command)

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

    metrics = subparsers.add_parser("metrics", help="Record or report manual Threads metrics.")
    metrics_sub = metrics.add_subparsers(dest="metrics_command", required=True)

    metrics_add = metrics_sub.add_parser("add", help="Add performance metrics for a manifest.")
    metrics_add.add_argument("manifest")
    metrics_add.add_argument("--views", type=int, default=0)
    metrics_add.add_argument("--likes", type=int, default=0)
    metrics_add.add_argument("--replies", type=int, default=0)
    metrics_add.add_argument("--reposts", type=int, default=0)
    metrics_add.add_argument("--saves", type=int, default=0)
    metrics_add.add_argument("--clicks", type=int, default=0)
    metrics_add.add_argument("--conversions", type=int, default=0)
    metrics_add.add_argument("--published-at")
    metrics_add.add_argument("--notes")
    metrics_add.add_argument("--ledger")
    metrics_add.set_defaults(func=metrics_add_command)

    metrics_report = metrics_sub.add_parser("report", help="Summarize recent performance metrics.")
    metrics_report.add_argument("--days", type=int, default=30)
    metrics_report.add_argument("--ledger")
    metrics_report.set_defaults(func=metrics_report_command)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
