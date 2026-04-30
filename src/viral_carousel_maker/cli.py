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
from .interview import evaluate_interview, load_interview_answers
from .intake import normalize_intake, write_seed_yaml
from .performance import add_metrics, summarize_metrics
from .profile import (
    init_profile,
    load_profile,
    merge_profile,
    profile_from_interview_answers,
    update_profile_from_manifest,
)
from .qa import load_manifest, run_manifest_qa, write_qa_report
from .renderer import CarouselRenderer
from .spec import load_spec, validate_spec
from .virality import score_spec


def render_command(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    profile = load_profile(args.profile_path) if (args.use_profile or args.update_profile or args.profile_path) else {}
    if args.use_profile or args.update_profile:
        if profile and not isinstance(spec.get("profile"), dict):
            spec["profile"] = profile
    interview_report = _apply_interview_to_spec(spec, args, profile=profile)
    if interview_report is not None and args.require_interview and not interview_report["ready_to_draft"]:
        print(json.dumps(interview_report, indent=2, sort_keys=True))
        return 1
    warnings = validate_spec(spec)
    if args.dry_run:
        print(json.dumps({"status": "ok", "renderer": args.renderer, "warnings": warnings}, indent=2))
        return 0
    if args.renderer == "imagegen":
        prompts_path = write_prompts_jsonl(spec, Path(args.out_dir) / "prompts.jsonl")
        print(
            json.dumps(
                {
                    "status": "host_imagegen_required",
                    "prompts": str(prompts_path),
                    "message": (
                        "ImageGen production rendering is host-driven. Use Codex native ImageGen, "
                        "or Claude's configured image provider/API fallback, then QA accepted PNGs."
                    ),
                },
                indent=2,
            )
        )
        return 2
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


def _apply_interview_to_spec(
    spec: dict[str, object],
    args: argparse.Namespace,
    *,
    profile: dict[str, object],
) -> dict[str, object] | None:
    if not args.require_interview and not args.interview_answers:
        return None
    answers = load_interview_answers(args.interview_answers)
    report = evaluate_interview(answers, profile=profile)
    if not report["ready_to_draft"]:
        return report

    strategy = spec.setdefault("strategy", {})
    if isinstance(strategy, dict):
        strategy["interview_answers"] = report["answered"]
    incoming_profile = profile_from_interview_answers(report["answered"])
    current_profile = spec.get("profile") if isinstance(spec.get("profile"), dict) else {}
    spec["profile"] = merge_profile(current_profile, incoming_profile, source="interview")
    return report


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


def interview_next_command(args: argparse.Namespace) -> int:
    answers = load_interview_answers(args.answers)
    profile = load_profile(args.profile_path) if args.use_profile or args.profile_path else {}
    report = evaluate_interview(answers, profile=profile)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def interview_validate_command(args: argparse.Namespace) -> int:
    answers = load_interview_answers(args.answers)
    profile = load_profile(args.profile_path) if args.use_profile or args.profile_path else {}
    report = evaluate_interview(answers, profile=profile)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_ready and not report["ready_to_draft"]:
        return 1
    return 0


def doctor_command(args: argparse.Namespace) -> int:
    platform = args.platform
    openai_key_set = bool(os.environ.get("OPENAI_API_KEY"))
    google_key_set = bool(
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_GENERATIVE_AI_API_KEY")
    )
    claude_provider = os.environ.get("VIRAL_CAROUSEL_IMAGEGEN_PROVIDER") or os.environ.get(
        "CLAUDE_IMAGEGEN_PROVIDER"
    )
    if platform == "codex":
        status = {
            "platform": "codex",
            "ok": True,
            "api_key_required": False,
            "production_renderer": "codex-native-imagegen",
            "native_imagegen": "host_tool",
            "openai_api_key_set": openai_key_set,
            "google_image_api_key_set": google_key_set,
            "message": "Codex native ImageGen / ChatGPT ImageGen 2 is the production path. OPENAI_API_KEY is not required.",
        }
    else:
        has_connected_provider = bool(claude_provider)
        provider_order = [
            "connected Claude image-generation provider",
            "OpenAI Images API via OPENAI_API_KEY",
            "Google image API via GOOGLE_API_KEY/GEMINI_API_KEY",
        ]
        status = {
            "platform": platform,
            "ok": has_connected_provider or openai_key_set or google_key_set,
            "api_key_required": not has_connected_provider,
            "production_renderer": "provider-imagegen",
            "connected_imagegen_provider": claude_provider or None,
            "openai_api_key_set": openai_key_set,
            "google_image_api_key_set": google_key_set,
            "provider_order": provider_order,
            "message": (
                f"Claude image-generation workflow can run through connected provider: {claude_provider}."
                if has_connected_provider
                else (
                    "OPENAI_API_KEY is set. Claude OpenAI Images API production path can run."
                    if openai_key_set
                    else (
                        "Google image API key is set. Claude Google image fallback can run."
                        if google_key_set
                        else "No Claude-connected image provider, OPENAI_API_KEY, or Google image API key was detected. Pause before production image generation."
                    )
                )
            ),
            "next_action": (
                "Run the carousel workflow."
                if has_connected_provider or openai_key_set or google_key_set
                else "Connect an image-generation provider to Claude, expose OPENAI_API_KEY, or expose GOOGLE_API_KEY/GEMINI_API_KEY."
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
        choices=["browser", "pillow", "imagegen"],
        default="browser",
        help="Renderer engine. ImageGen is the production host path; browser/Pillow are draft and QA fallbacks.",
    )
    render.add_argument("--dry-run", action="store_true")
    render.add_argument("--use-profile", action="store_true", help="Load local profile into the spec when the spec has no profile block.")
    render.add_argument("--update-profile", action="store_true", help="After successful QA, merge stable render metadata into the local profile.")
    render.add_argument("--profile-path", help="Override the local profile path.")
    render.add_argument("--require-interview", action="store_true", help="Fail unless interview answers satisfy the mandatory gate.")
    render.add_argument("--interview-answers", help="YAML or JSON answers captured from the mandatory interview.")
    render.set_defaults(func=render_command)

    interview = subparsers.add_parser("interview", help="Run the mandatory interrogation gate.")
    interview_sub = interview.add_subparsers(dest="interview_command", required=True)
    interview_next = interview_sub.add_parser("next", help="Return the next focused question batch.")
    interview_next.add_argument("--answers", help="YAML or JSON answers collected so far.")
    interview_next.add_argument("--use-profile", action="store_true", help="Use the saved local creator profile as stable context.")
    interview_next.add_argument("--profile-path", help="Override the local profile path.")
    interview_next.set_defaults(func=interview_next_command)

    interview_validate = interview_sub.add_parser("validate", help="Validate interview answers.")
    interview_validate.add_argument("--answers", help="YAML or JSON answers collected so far.")
    interview_validate.add_argument("--require-ready", action="store_true", help="Exit non-zero until ready_to_draft is true.")
    interview_validate.add_argument("--use-profile", action="store_true", help="Use the saved local creator profile as stable context.")
    interview_validate.add_argument("--profile-path", help="Override the local profile path.")
    interview_validate.set_defaults(func=interview_validate_command)

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
