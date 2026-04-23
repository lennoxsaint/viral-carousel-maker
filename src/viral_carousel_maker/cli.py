"""Command line interface for Viral Carousel Maker."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .assets import generate_openai_asset, write_prompts_jsonl
from .browser_renderer import BrowserCarouselRenderer
from .corpus import import_private_corpus
from .critic import load_critic, validate_critic_output
from .intake import normalize_intake, write_seed_yaml
from .performance import add_metrics, summarize_metrics
from .profile import init_profile, load_profile, update_profile_from_manifest
from .qa import load_manifest, run_manifest_qa, write_qa_report
from .renderer import CarouselRenderer
from .spec import load_spec, validate_spec
from .virality import score_spec


def render_command(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    if args.use_profile or args.update_profile:
        profile = load_profile(args.profile_path)
        if profile and not isinstance(spec.get("profile"), dict):
            spec["profile"] = profile
    warnings = validate_spec(spec)
    if args.dry_run:
        print(json.dumps({"status": "ok", "renderer": args.renderer, "warnings": warnings}, indent=2))
        return 0
    renderer = (
        CarouselRenderer(spec, args.out_dir)
        if args.renderer == "pillow"
        else BrowserCarouselRenderer(spec, args.out_dir)
    )
    manifest = renderer.render()
    profile_path = None
    if args.update_profile:
        qa_ok, _messages = run_manifest_qa(manifest)
        if qa_ok:
            profile_path = update_profile_from_manifest(manifest, path=args.profile_path)
    print(
        json.dumps(
            {
                "manifest": str(Path(args.out_dir) / "manifest.json"),
                "slides": len(manifest["slides"]),
                "profile_updated": str(profile_path) if profile_path else None,
            },
            indent=2,
        )
    )
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


def critic_validate_command(args: argparse.Namespace) -> int:
    critic = load_critic(args.critic_json)
    ok, errors = validate_critic_output(critic)
    print(json.dumps({"ok": ok, "errors": errors}, indent=2, sort_keys=True))
    return 0 if ok else 1


def corpus_import_command(args: argparse.Namespace) -> int:
    summary = import_private_corpus(args.source, local_only=args.local_only)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def intake_command(args: argparse.Namespace) -> int:
    result = normalize_intake(args.source, text=args.text, input_format=args.format)
    if args.out:
        path = write_seed_yaml(result, args.out)
        print(json.dumps({"seed_spec": str(path), "warnings": result.warnings}, indent=2))
    else:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


def doctor_command(args: argparse.Namespace) -> int:
    platform = args.platform
    key_set = bool(os.environ.get("OPENAI_API_KEY"))
    if platform == "codex":
        status = {
            "platform": "codex",
            "ok": True,
            "api_key_required": False,
            "message": "Codex preferred path is ready. OPENAI_API_KEY is not required.",
        }
    else:
        status = {
            "platform": platform,
            "ok": key_set,
            "api_key_required": True,
            "openai_api_key_set": key_set,
            "message": (
                "OPENAI_API_KEY is set. Claude image-generation workflow can run."
                if key_set
                else "OPENAI_API_KEY is missing. Claude can still make procedural drafts, but the intended image workflow needs a key."
            ),
            "next_action": (
                "Run the carousel workflow."
                if key_set
                else "Create a key at https://platform.openai.com/api-keys and expose it as OPENAI_API_KEY."
            ),
        }
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="viral-carousel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render = subparsers.add_parser("render", help="Render a carousel spec to PNGs.")
    render.add_argument("spec")
    render.add_argument("--out-dir", required=True)
    render.add_argument(
        "--renderer",
        choices=["browser", "pillow"],
        default="browser",
        help="Renderer engine. Browser is the default production path; Pillow is the fallback.",
    )
    render.add_argument("--dry-run", action="store_true")
    render.add_argument("--use-profile", action="store_true", help="Load local profile into the spec when the spec has no profile block.")
    render.add_argument("--update-profile", action="store_true", help="After successful QA, merge stable render metadata into the local profile.")
    render.add_argument("--profile-path", help="Override the local profile path.")
    render.set_defaults(func=render_command)

    intake = subparsers.add_parser("intake", help="Normalize pasted text, markdown, or Threadify JSON into a seed spec.")
    intake.add_argument("source", nargs="?", help="Local path or raw source string.")
    intake.add_argument("--text", help="Pasted draft text. Use this instead of a source path.")
    intake.add_argument("--format", choices=["auto", "text", "markdown", "json"], default="auto")
    intake.add_argument("--out", help="Write the normalized seed spec YAML to this path.")
    intake.set_defaults(func=intake_command)

    doctor = subparsers.add_parser("doctor", help="Check platform readiness and API-key behavior.")
    doctor.add_argument("--platform", choices=["codex", "claude", "claude-code", "claude-desktop"], default="codex")
    doctor.set_defaults(func=doctor_command)

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

    critic = subparsers.add_parser("critic", help="Validate structured AI critic output.")
    critic_sub = critic.add_subparsers(dest="critic_command", required=True)
    critic_validate = critic_sub.add_parser("validate", help="Validate an AI critic JSON file.")
    critic_validate.add_argument("critic_json")
    critic_validate.set_defaults(func=critic_validate_command)

    corpus = subparsers.add_parser("corpus", help="Manage local-only private corpus summaries.")
    corpus_sub = corpus.add_subparsers(dest="corpus_command", required=True)
    corpus_import = corpus_sub.add_parser("import", help="Import a private corpus as a local summary.")
    corpus_import.add_argument("source")
    corpus_import.add_argument("--local-only", action="store_true", required=True)
    corpus_import.set_defaults(func=corpus_import_command)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
