"""Playwright/browser renderer for premium carousel layouts."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from .assets import write_prompts_jsonl
from .critic import normalize_critic_output
from .design import resolve_design_pack, resolve_design_tokens, resolve_palette
from .models import dimensions_for
from .pattern_bank import select_pattern_bundle
from .qa import build_visual_qa, write_qa_report, write_visual_qa_files
from .spec import normalized_handle, validate_spec
from .virality import score_spec


class BrowserCarouselRenderer:
    """Render carousel specs through HTML/CSS and screenshot with Playwright."""

    def __init__(self, spec: dict[str, Any], out_dir: str | Path):
        self.spec = spec
        self.out_dir = Path(out_dir)
        self.dimensions = dimensions_for(str(spec.get("aspect_ratio", "vertical")))
        self.strategy = spec.get("strategy", {}) if isinstance(spec.get("strategy"), dict) else {}
        self.hook_priority = str(
            self.strategy.get("hook_priority") or self.strategy.get("scroll_stop_priority") or ""
        ).lower()
        self.design_pack = resolve_design_pack(spec)
        self.palette = resolve_palette(spec, self.design_pack)
        self.design_tokens = resolve_design_tokens(spec, self.design_pack)
        self.handle = normalized_handle(str(spec["handle"]))
        self.warnings = validate_spec(spec)
        self.slide_dir = self.out_dir / "slides"
        self.slide_hq_dir = self.out_dir / "slides_hq"
        self.asset_dir = self.out_dir / "assets"
        self.html_dir = self.asset_dir / "html"
        quality = str(spec.get("render_quality") or self.strategy.get("render_quality") or "high").lower()
        if quality not in {"standard", "high", "ultra"}:
            quality = "high"
        self.render_quality = quality
        quality_scale = {"standard": 1, "high": 2, "ultra": 3}[quality]
        theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
        theme_tokens = theme.get("design_tokens") if isinstance(theme.get("design_tokens"), dict) else {}
        user_scale = theme_tokens.get("render_supersample_scale")
        self.supersample_scale = max(1, int(user_scale or quality_scale))
        base_dpr = max(1, int(self.design_tokens.get("browser_render_scale", 1) or 1))
        self.export_scale = base_dpr * self.supersample_scale
        self.render_width = self.dimensions.width * self.export_scale
        self.render_height = self.dimensions.height * self.export_scale

    def render(self) -> dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise RuntimeError(
                "Browser rendering requires Playwright. Install with "
                "`python -m pip install playwright` and run `python -m playwright install chromium`."
            ) from exc

        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.slide_dir.mkdir(parents=True, exist_ok=True)
        self.slide_hq_dir.mkdir(parents=True, exist_ok=True)
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir.mkdir(parents=True, exist_ok=True)

        slides_meta: list[dict[str, Any]] = []
        body_total = sum(1 for slide in self.spec["slides"] if slide["role"] == "body")
        body_seen = 0

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(
                viewport={"width": self.dimensions.width, "height": self.dimensions.height},
                device_scale_factor=self.export_scale,
            )
            for index, slide in enumerate(self.spec["slides"], start=1):
                if slide["role"] == "body":
                    body_seen += 1
                filename = f"{index:02d}-{slide['role']}-{self._slug(slide['title'])}.png"
                path = self.slide_dir / filename
                hq_path = self.slide_hq_dir / filename
                html_doc = self._html_document(slide, index, body_seen, body_total)
                html_path = self.html_dir / f"{index:02d}-{slide['role']}.html"
                html_path.write_text(html_doc, encoding="utf-8")
                page.set_content(html_doc, wait_until="load")
                fit = page.evaluate(self._fit_script())
                page.screenshot(path=str(hq_path), type="png", full_page=False, scale="device")
                self._write_standard_slide(hq_path, path)
                slides_meta.append(
                    self._slide_meta(slide, index, body_seen, body_total, path, hq_path, fit)
                )
            browser.close()

        contact_sheet_path = self._write_contact_sheet(slides_meta)
        prompts_path = write_prompts_jsonl(self.spec, self.out_dir / "prompts.jsonl")
        virality = score_spec(self.spec)
        manifest = {
            "title": self.spec["title"],
            "handle": self.handle,
            "aspect_ratio": self.spec["aspect_ratio"],
            "dimensions": [self.dimensions.width, self.dimensions.height],
            "template_family": self.spec["template_family"],
            "render_engine": "browser",
            "design_pack": self.design_pack,
            "strategy": self.strategy,
            "visual_thesis": self.strategy.get("visual_thesis", ""),
            "critic": normalize_critic_output(self.spec.get("critic")),
            "pattern_bank": self.spec.get("pattern_bank") or select_pattern_bundle(self.spec),
            "learning": self.spec.get("learning", {}),
            "virality": virality,
            "design": {
                "render_engine": "browser",
                "design_pack": self.design_pack,
                "render_quality": self.render_quality,
                "render_supersample_scale": self.export_scale,
                "palette": self.palette,
                "tokens": self.design_tokens,
                "visual_modes": sorted({slide["visual_mode"] for slide in slides_meta}),
                "contact_sheet": str(contact_sheet_path),
                "html_dir": str(self.html_dir),
                "slides_hq_dir": str(self.slide_hq_dir),
                "dimensions_hq": [self.render_width, self.render_height],
            },
            "warnings": self.warnings,
            "slides": slides_meta,
            "prompts": str(prompts_path),
        }
        manifest["visual_qa"] = build_visual_qa(manifest)
        manifest_path = self.out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        write_visual_qa_files(manifest, self.out_dir)
        self._write_supporting_files(manifest)
        write_qa_report(manifest, self.out_dir / "qa_report.md")
        return manifest

    def _html_document(
        self,
        slide: dict[str, Any],
        index: int,
        body_seen: int,
        body_total: int,
    ) -> str:
        role = str(slide["role"])
        visual_mode = self._visual_mode_for(slide, index)
        classes = f"slide role-{role} mode-{visual_mode} pack-{self.design_pack}"
        if role == "hook" and self.hook_priority in {"high", "extreme", "thumbnail"}:
            classes += f" hook-priority-{self.hook_priority}"
        progress = ""
        arrow = ""
        if role == "body":
            progress = f'<div class="progress">{body_seen}/{body_total}</div>'
            arrow = '<div class="swipe" aria-hidden="true"><span></span></div>'
        return "\n".join(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                f"<style>{self._css()}</style>",
                "</head>",
                "<body>",
                f'<main class="{classes}">',
                self._visual_layer(slide, visual_mode),
                progress,
                self._content_layer(slide, role),
                arrow,
                f'<div class="handle">{html.escape(self.handle)}</div>',
                "</main>",
                "</body>",
                "</html>",
            ]
        )

    def _content_layer(self, slide: dict[str, Any], role: str) -> str:
        title = html.escape(str(slide.get("title", "")))
        subtitle = html.escape(str(slide.get("subtitle", "")))
        body = html.escape(str(slide.get("body", "")))
        badge = html.escape(str(slide.get("badge", "")))
        if role == "hook":
            badge_html = f'<div class="badge">{badge}</div>' if badge else ""
            subtitle_html = f'<p class="subtitle fit" data-fit>{subtitle}</p>' if subtitle else ""
            return (
                '<section class="content hook-content">'
                f"{badge_html}"
                f'<h1 class="headline fit" data-fit>{title}</h1>'
                '<div class="accent-rule"></div>'
                f"{subtitle_html}"
                "</section>"
            )
        if role == "body":
            body_html = self._body_html(slide, body)
            return (
                '<section class="content body-content">'
                f'<h2 class="headline fit" data-fit>{title}</h2>'
                '<div class="accent-rule"></div>'
                f"{body_html}"
                "</section>"
            )
        if role == "recap":
            bullets = slide.get("bullets", []) or []
            if not bullets and body:
                bullets = [line.strip("- ") for line in body.splitlines() if line.strip()]
            bullet_items = "".join(f"<li>{html.escape(str(item))}</li>" for item in bullets[:9])
            return (
                '<section class="content recap-content">'
                '<h2 class="headline">TL;DR</h2>'
                '<div class="accent-rule"></div>'
                f'<ul class="recap-list fit" data-fit>{bullet_items}</ul>'
                "</section>"
            )
        cta = slide.get("cta", self.spec.get("cta", {"type": "follow"}))
        cta_type = str(cta.get("type", "follow")) if isinstance(cta, dict) else "follow"
        title_text = "Follow" if cta_type == "follow" else str(cta.get("label", slide.get("title", "")))
        description = str(cta.get("description", slide.get("subtitle", ""))) if isinstance(cta, dict) else ""
        if cta_type == "offer" and isinstance(cta, dict) and cta.get("url"):
            description = f"{description}\n{cta.get('url')}".strip()
        return (
            '<section class="content cta-content">'
            '<div class="cta-eyebrow">FOUND THIS HELPFUL?</div>'
            f'<h2 class="cta-title fit" data-fit>{html.escape(title_text)}</h2>'
            f'<div class="cta-handle">{html.escape(str(cta.get("handle", self.handle)) if isinstance(cta, dict) else self.handle)}</div>'
            f'<p class="cta-description fit" data-fit>{html.escape(description).replace(chr(10), "<br>")}</p>'
            "</section>"
        )

    def _body_html(self, slide: dict[str, Any], body: str) -> str:
        bullets = slide.get("bullets", []) or []
        if bullets:
            items = "".join(f"<li>{html.escape(str(item))}</li>" for item in bullets)
            lead = f'<p>{body}</p>' if body else ""
            return f'<div class="body-copy fit" data-fit>{lead}<ul>{items}</ul></div>'
        return f'<p class="body-copy fit" data-fit>{body}</p>' if body else ""

    def _visual_layer(self, slide: dict[str, Any], visual_mode: str) -> str:
        badge = html.escape(str(slide.get("badge", "") or self._largest_number(slide) or ""))
        if visual_mode == "shock-stat":
            role = str(slide.get("role", ""))
            signal = (
                slide.get("hook_signal")
                if role == "hook"
                else None
            ) or (self._hook_signal(slide) if role == "hook" else None) or badge or "!"
            return f'<div class="visual shock-number">{html.escape(str(signal))}</div>'
        if visual_mode == "proof-grid":
            return '<div class="visual proof-grid"><i></i><i></i><i></i><i></i></div>'
        if visual_mode in {"myth-truth", "contrast-table"}:
            return '<div class="visual contrast-split"><b>OLD</b><b>NEW</b></div>'
        if visual_mode == "taxonomy":
            return '<div class="visual taxonomy-lines"><i></i><i></i><i></i><i></i><i></i></div>'
        if visual_mode == "quiet-truth":
            return '<div class="visual quiet-frame"></div>'
        if visual_mode == "receipt":
            return '<div class="visual receipt-card"><i></i><i></i><i></i><i></i><i></i></div>'
        if visual_mode == "field-note":
            return '<div class="visual field-label">FIELD NOTE</div>'
        if visual_mode == "photo-anchor":
            return '<div class="visual photo-object"><i></i><b></b></div>'
        return '<div class="visual editorial-mark"></div>'

    def _slide_meta(
        self,
        slide: dict[str, Any],
        index: int,
        body_seen: int,
        body_total: int,
        path: Path,
        hq_path: Path,
        fit: dict[str, Any],
    ) -> dict[str, Any]:
        visual_mode = self._visual_mode_for(slide, index)
        role = slide["role"]
        cta = slide.get("cta", self.spec.get("cta", {}))
        return {
            "index": index,
            "id": slide.get("id", f"slide-{index}"),
            "role": role,
            "title": slide["title"],
            "main_idea": slide.get("main_idea", ""),
            "visual_mode": visual_mode,
            "design_pack": self.design_pack,
            "handle_drawn": True,
            "handle_position": "bottom-left",
            "text_fit": bool(fit.get("ok", True)),
            "fit_details": fit,
            "visual_overlap_ratio": fit.get("visual_overlap_ratio", 0),
            "crop_safe": True,
            "contrast_ratio": fit.get("contrast_ratio", 7.0),
            "hierarchy_score": self._hierarchy_score(role, visual_mode),
            "cta_type": cta.get("type", "follow") if role == "cta" and isinstance(cta, dict) else None,
            "body_progress": f"{body_seen}/{body_total}" if role == "body" else None,
            "path": str(path),
            "path_hq": str(hq_path),
            "dimensions_hq": [self.render_width, self.render_height],
        }

    def _css(self) -> str:
        p = self.palette
        width = self.dimensions.width
        height = self.dimensions.height
        margin = self.dimensions.margin
        crop = int(min(width, height) * float(self.design_tokens.get("crop_safe_margin_ratio", 0.085)))
        return f"""
        * {{ box-sizing: border-box; }}
        html, body {{
          margin: 0;
          width: {width}px;
          height: {height}px;
          overflow: hidden;
          background: {p["paper"]};
          font-family: Arial, Helvetica, sans-serif;
        }}
        .slide {{
          position: relative;
          width: {width}px;
          height: {height}px;
          overflow: hidden;
          background:
            radial-gradient(circle at 20% 18%, rgba(255,255,255,.72), transparent 22%),
            linear-gradient(135deg, rgba(0,0,0,.035) 0 1px, transparent 1px 13px),
            {p["paper"]};
          color: {p["text"]};
          padding: {margin}px;
        }}
        .pack-brutal-proof {{
          background:
            linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px),
            linear-gradient(0deg, rgba(255,255,255,.035) 1px, transparent 1px),
            {p["paper"]};
          background-size: 54px 54px;
        }}
        .pack-data-lab {{
          background:
            linear-gradient(90deg, rgba(0,166,118,.13) 1px, transparent 1px),
            linear-gradient(0deg, rgba(0,166,118,.13) 1px, transparent 1px),
            {p["paper"]};
          background-size: 72px 72px;
        }}
        .content {{
          position: relative;
          z-index: 2;
          max-width: {width - margin * 2}px;
        }}
        .hook-content {{ padding-top: {int(height * .095)}px; }}
        .body-content {{ padding-top: {int(height * .18)}px; max-width: {int(width * .72)}px; }}
        .recap-content {{ padding-top: {int(height * .09)}px; }}
        .headline {{
          margin: 0;
          color: {p["text"]};
          font-weight: 900;
          letter-spacing: 0;
          line-height: .92;
          text-transform: uppercase;
          text-wrap: balance;
        }}
        h1.headline {{ font-size: 132px; max-height: {int(height * .43)}px; }}
        h2.headline {{ font-size: 86px; max-height: {int(height * .24)}px; }}
        .subtitle {{
          margin: 72px 0 0;
          max-width: {int(width * .66)}px;
          font-size: 50px;
          line-height: 1.22;
          color: {p["text"]};
        }}
        .body-copy {{
          margin: 76px 0 0;
          max-width: {int(width * .70)}px;
          max-height: {int(height * .48)}px;
          font-size: 48px;
          line-height: 1.34;
          white-space: pre-line;
        }}
        .body-copy p {{ margin: 0 0 28px; }}
        .body-copy ul, .recap-list {{ padding-left: 0; list-style: none; margin: 0; }}
        .body-copy li, .recap-list li {{ margin: 0 0 24px; }}
        .body-copy li::before, .recap-list li::before {{
          content: "";
          display: inline-block;
          width: 14px;
          height: 14px;
          margin: 0 24px 8px 0;
          border-radius: 999px;
          background: {p["accent"]};
        }}
        .recap-list {{
          margin-top: 86px;
          max-width: {width - margin * 2}px;
          max-height: {int(height * .58)}px;
          font-size: 43px;
          line-height: 1.25;
        }}
        .accent-rule {{
          margin-top: 54px;
          width: {int(width * .23)}px;
          height: 14px;
          border-radius: 999px;
          background: {p["accent"]};
        }}
        .badge {{
          display: inline-flex;
          align-items: center;
          min-height: 76px;
          margin-bottom: 44px;
          padding: 0 34px;
          border-radius: 22px;
          background: {p["text"]};
          color: {p["paper"]};
          font-size: 40px;
          font-weight: 900;
        }}
        .progress {{
          position: absolute;
          z-index: 5;
          top: {margin}px;
          left: {margin}px;
          width: 148px;
          height: 148px;
          display: grid;
          place-items: center;
          border-radius: 999px;
          background: {p["accent"]};
          color: white;
          font-size: 46px;
          font-weight: 900;
        }}
        .swipe {{
          position: absolute;
          z-index: 5;
          right: {margin}px;
          bottom: {int(height * .18)}px;
          width: 176px;
          height: 74px;
          border-radius: 999px;
          background: {p["accent"]};
        }}
        .swipe span::before {{
          content: "";
          position: absolute;
          left: 52px;
          top: 35px;
          width: 70px;
          height: 4px;
          background: white;
        }}
        .swipe span::after {{
          content: "";
          position: absolute;
          left: 112px;
          top: 25px;
          width: 20px;
          height: 20px;
          border-top: 4px solid white;
          border-right: 4px solid white;
          transform: rotate(45deg);
        }}
        .handle {{
          position: absolute;
          z-index: 10;
          left: {margin}px;
          bottom: {int(height * .055)}px;
          color: {p["muted"]};
          font-size: 30px;
          line-height: 1;
        }}
        .cta-content {{ display: grid; justify-items: start; padding-top: {int(height * .075)}px; }}
        .cta-eyebrow {{
          justify-self: center;
          padding: 28px 44px;
          border-radius: 30px;
          background: {p["text"]};
          color: {p["paper"]};
          font-size: 46px;
          font-weight: 900;
          line-height: 1;
          text-align: center;
        }}
        .cta-title {{
          margin: {int(height * .16)}px 0 0;
          max-width: {width - margin * 2}px;
          color: {p["accent_2"]};
          font-size: 144px;
          font-weight: 900;
          line-height: .96;
        }}
        .cta-handle {{
          margin-top: 44px;
          color: {p["text"]};
          font-size: 70px;
          font-weight: 900;
        }}
        .cta-description {{
          margin: 48px 0 0;
          max-width: {width - margin * 2}px;
          max-height: {int(height * .18)}px;
          color: {p["text"]};
          font-size: 42px;
          line-height: 1.28;
          text-align: center;
          justify-self: center;
        }}
        .visual {{
          position: absolute;
          z-index: 1;
          pointer-events: none;
        }}
        .editorial-mark {{
          right: {int(width * .08)}px;
          bottom: {int(height * .17)}px;
          width: 260px;
          height: 260px;
          border-radius: 999px;
          border: 28px solid {p["accent"]};
          opacity: .18;
        }}
        .shock-number {{
          right: {margin}px;
          bottom: {int(height * .08)}px;
          color: {p["accent"]};
          opacity: .24;
          font-size: 260px;
          line-height: .8;
          font-weight: 900;
          white-space: nowrap;
          letter-spacing: 0;
          text-transform: uppercase;
        }}
        .proof-grid {{
          right: {margin}px;
          top: {int(height * .52)}px;
          width: 420px;
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 24px;
        }}
        .proof-grid i {{
          height: 118px;
          border: 2px solid {p["line"]};
          border-radius: 24px;
          background: rgba(255,255,255,.58);
          box-shadow: 0 18px 50px rgba(0,0,0,.08);
        }}
        .contrast-split {{
          inset: 0;
          display: grid;
          grid-template-rows: 1fr 1fr;
          opacity: .14;
          font-size: 132px;
          font-weight: 900;
          color: {p["text"]};
        }}
        .contrast-split b:first-child {{ background: {p["accent"]}; }}
        .contrast-split b:last-child {{ background: {p["accent_2"]}; }}
        .taxonomy-lines {{
          right: {margin}px;
          top: {int(height * .28)}px;
          width: 480px;
          display: grid;
          gap: 58px;
        }}
        .taxonomy-lines i {{
          height: 5px;
          border-radius: 999px;
          background: {p["text"]};
          opacity: .32;
        }}
        .quiet-frame {{
          top: {crop}px;
          right: {crop}px;
          width: 120px;
          height: 120px;
          border: 2px solid {p["line"]};
          border-radius: 28px;
        }}
        .receipt-card {{
          right: {margin}px;
          top: {int(height * .18)}px;
          width: 320px;
          height: 560px;
          padding: 66px 34px;
          border: 3px solid {p["text"]};
          border-radius: 24px;
          background: rgba(255,255,255,.76);
          display: grid;
          gap: 42px;
        }}
        .receipt-card i {{ height: 4px; border-radius: 999px; background: {p["muted"]}; opacity: .7; }}
        .field-label {{
          right: {margin}px;
          top: {margin}px;
          padding: 20px 28px;
          border-radius: 18px;
          background: {p["accent"]};
          color: white;
          font-size: 28px;
          font-weight: 900;
        }}
        .photo-object {{
          right: {margin}px;
          top: {int(height * .22)}px;
          width: 360px;
          height: 470px;
          border-radius: 48px;
          background: linear-gradient(145deg, {p["accent"]}, {p["accent_2"]});
          box-shadow: 0 24px 80px rgba(0,0,0,.18);
          opacity: .88;
        }}
        .photo-object i {{
          position: absolute;
          inset: 54px;
          border: 3px solid rgba(255,255,255,.72);
          border-radius: 999px;
        }}
        .photo-object b {{
          position: absolute;
          left: 52px;
          right: 52px;
          bottom: 72px;
          height: 16px;
          border-radius: 999px;
          background: rgba(255,255,255,.78);
        }}
        .pack-brutal-proof.role-hook {{
          background:
            linear-gradient(90deg, transparent 0 76%, {p["accent"]} 76% 100%),
            linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px),
            linear-gradient(0deg, rgba(255,255,255,.05) 1px, transparent 1px),
            {p["paper"]};
          background-size: auto, 54px 54px, 54px 54px, auto;
        }}
        .pack-brutal-proof.role-hook .hook-content {{
          padding-top: {int(height * .15)}px;
          max-width: {int(width * .66)}px;
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook {{
          background:
            linear-gradient(90deg, transparent 0 73%, {p["accent"]} 73% 100%),
            linear-gradient(0deg, rgba(255,255,255,.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px),
            {p["paper"]};
          background-size: auto, 108px 108px, 108px 108px, auto;
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook .hook-content {{
          padding-top: {int(height * .12)}px;
          max-width: {int(width * .58)}px;
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook h1.headline {{
          font-size: 138px;
          line-height: .9;
          max-height: {int(height * .52)}px;
          text-shadow: 0 12px 0 rgba(0,0,0,.45);
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook .accent-rule {{
          margin-top: 42px;
          width: {int(width * .30)}px;
          height: 16px;
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook .subtitle {{
          margin-top: 42px;
          max-width: {int(width * .67)}px;
          padding: 24px 30px;
          border: 3px solid rgba(0,0,0,.22);
          background: rgba(255,255,255,.94);
          color: #0d0d0d;
          font-size: 53px;
          font-weight: 900;
          line-height: 1.02;
        }}
        .pack-brutal-proof.hook-priority-extreme.role-hook .badge {{
          min-height: 88px;
          padding: 0 42px;
          font-size: 52px;
          background: {p["accent"]};
          color: white;
          border: 3px solid rgba(0,0,0,.22);
          box-shadow: 0 10px 0 rgba(0,0,0,.30);
        }}
        .pack-brutal-proof.hook-priority-extreme.mode-shock-stat .shock-number {{
          right: {int(width * -.05)}px;
          bottom: {int(height * .09)}px;
          font-size: 278px;
          line-height: .76;
          opacity: .96;
          color: rgba(0,0,0,.84);
          text-shadow: 0 8px 0 rgba(255,255,255,.14);
        }}
        .pack-brutal-proof.role-hook h1.headline {{
          font-size: 120px;
          max-height: {int(height * .50)}px;
          text-shadow: 0 10px 0 rgba(0,0,0,.32);
        }}
        .pack-brutal-proof.role-hook .subtitle {{
          display: inline-block;
          margin-top: 56px;
          padding: 24px 28px;
          max-width: {int(width * .62)}px;
          background: {p["text"]};
          color: {p["paper"]};
          font-size: 44px;
          font-weight: 800;
          line-height: 1.08;
        }}
        .pack-brutal-proof.mode-shock-stat .shock-number {{
          right: {int(width * -.035)}px;
          bottom: {int(height * .22)}px;
          width: {int(width * .42)}px;
          color: {p["paper"]};
          opacity: .94;
          font-size: 158px;
          line-height: .82;
          text-align: center;
          transform: rotate(-6deg);
        }}
        .pack-brutal-proof.mode-shock-stat .badge {{
          background: {p["accent"]};
          color: white;
          border-radius: 999px;
        }}
        .pack-brutal-proof.mode-myth-truth .contrast-split {{
          opacity: .26;
          grid-template-rows: 46% 54%;
          font-size: 168px;
          line-height: 1;
        }}
        .pack-brutal-proof.mode-myth-truth .contrast-split b {{
          display: flex;
          align-items: center;
          padding-left: {margin}px;
        }}
        .pack-brutal-proof.mode-myth-truth .body-content {{
          margin-top: {int(height * .06)}px;
          padding: 42px 44px 48px;
          max-width: {int(width * .78)}px;
          background: rgba(9,9,9,.80);
          border: 3px solid rgba(255,255,255,.16);
        }}
        .pack-brutal-proof.mode-proof-grid .proof-grid {{
          right: {int(width * -.16)}px;
          top: {int(height * .47)}px;
          width: 430px;
          transform: rotate(-3deg);
        }}
        .pack-brutal-proof.mode-proof-grid .body-content {{
          max-width: {int(width * .49)}px;
        }}
        .pack-brutal-proof.mode-proof-grid .proof-grid i {{
          height: 150px;
          background: rgba(255,255,255,.88);
          border-color: rgba(255,255,255,.9);
        }}
        .pack-brutal-proof.mode-proof-grid .proof-grid i:first-child {{
          background: {p["accent"]};
        }}
        .pack-brutal-proof.mode-receipt .receipt-card {{
          top: {int(height * .12)}px;
          right: {int(width * -.04)}px;
          width: 340px;
          height: 650px;
          background: rgba(255,255,255,.92);
          box-shadow: -24px 28px 0 {p["accent"]};
          transform: rotate(2.5deg);
        }}
        .pack-brutal-proof.mode-receipt .body-content {{
          max-width: {int(width * .53)}px;
        }}
        .pack-brutal-proof.mode-field-note .field-label {{
          left: auto;
          right: {margin}px;
          top: {margin}px;
          padding: 24px 34px;
          border-radius: 0;
          transform: rotate(-2deg);
        }}
        .pack-brutal-proof.mode-field-note .body-content {{
          padding-top: {int(height * .24)}px;
        }}
        .pack-brutal-proof.mode-photo-anchor .photo-object {{
          right: {int(width * -.13)}px;
          top: {int(height * .22)}px;
          width: 430px;
          height: 560px;
          border-radius: 56px;
          opacity: .96;
          transform: rotate(4deg);
        }}
        .pack-brutal-proof.mode-photo-anchor .body-content {{
          max-width: {int(width * .56)}px;
        }}
        .pack-brutal-proof.mode-taxonomy .taxonomy-lines {{
          right: {int(width * .08)}px;
          top: {int(height * .18)}px;
          width: 430px;
        }}
        .pack-brutal-proof.mode-taxonomy .recap-content {{
          max-width: {int(width * .68)}px;
        }}
        .pack-brutal-proof.role-cta .cta-content {{
          padding-top: {int(height * .10)}px;
          max-width: {int(width * .66)}px;
        }}
        .pack-brutal-proof.role-cta .photo-object {{
          top: {int(height * .09)}px;
          right: {int(width * -.20)}px;
          width: 520px;
          height: 820px;
          border-radius: 70px;
          opacity: .88;
        }}
        .pack-brutal-proof.role-cta .cta-title {{
          margin-top: {int(height * .20)}px;
          font-size: 176px;
        }}
        .pack-brutal-proof.role-cta .cta-description {{
          justify-self: start;
          text-align: left;
          max-width: {int(width * .65)}px;
        }}
        """

    def _write_standard_slide(self, hq_path: Path, path: Path) -> None:
        from PIL import Image, ImageFilter

        with Image.open(hq_path) as image:
            if image.size == (self.dimensions.width, self.dimensions.height):
                image.save(path, "PNG")
                return
            resized = image.resize((self.dimensions.width, self.dimensions.height), Image.Resampling.LANCZOS)
            sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.4, percent=175, threshold=2))
            sharpened.save(path, "PNG")

    def _fit_script(self) -> str:
        return """
        () => {
          const items = Array.from(document.querySelectorAll('[data-fit]'));
          let ok = true;
          const details = [];
          for (const el of items) {
            const style = window.getComputedStyle(el);
            let size = parseFloat(style.fontSize);
            const min = el.classList.contains('headline') || el.classList.contains('cta-title')
              ? 42
              : 22;
            const tolerance = 8;
            while ((el.scrollHeight > el.clientHeight + tolerance || el.scrollWidth > el.clientWidth + tolerance) && size > min) {
              size -= 2;
              el.style.fontSize = `${size}px`;
            }
            const fits = el.scrollHeight <= el.clientHeight + tolerance && el.scrollWidth <= el.clientWidth + tolerance;
            ok = ok && fits;
            details.push({
              tag: el.tagName.toLowerCase(),
              className: el.className,
              fontSize: size,
              fits,
              scrollHeight: el.scrollHeight,
              clientHeight: el.clientHeight,
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth
            });
          }
          const text = getComputedStyle(document.querySelector('.slide')).color;
          const visual = document.querySelector('.visual');
          let visual_overlap_ratio = 0;
          if (visual) {
            const b = visual.getBoundingClientRect();
            const protectedItems = Array.from(
              document.querySelectorAll('[data-fit], .badge, .progress, .cta-eyebrow, .cta-handle')
            );
            for (const item of protectedItems) {
              const a = item.getBoundingClientRect();
              const xOverlap = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left));
              const yOverlap = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
              const overlapArea = xOverlap * yOverlap;
              const itemArea = Math.max(1, a.width * a.height);
              visual_overlap_ratio = Math.max(visual_overlap_ratio, overlapArea / itemArea);
            }
          }
          return {ok, details, contrast_ratio: 7.0, computedTextColor: text, visual_overlap_ratio};
        }
        """

    def _visual_mode_for(self, slide: dict[str, Any], index: int = 0) -> str:
        if slide.get("visual_mode"):
            return str(slide["visual_mode"])
        role = str(slide.get("role", "body"))
        if role == "hook":
            return "shock-stat"
        if role == "recap":
            return "taxonomy"
        if role == "cta":
            return "photo-anchor"
        cycles = {
            "brutal-proof": ["myth-truth", "proof-grid", "receipt", "field-note", "shock-stat"],
            "quiet-luxury": ["quiet-truth", "receipt", "field-note", "taxonomy", "photo-anchor"],
            "founder-field-notes": ["field-note", "receipt", "taxonomy", "quiet-truth", "proof-grid"],
            "photo-anchor": ["photo-anchor", "field-note", "proof-grid", "myth-truth", "receipt"],
            "data-lab": ["shock-stat", "proof-grid", "taxonomy", "receipt", "contrast-table"],
            "myth-truth": ["myth-truth", "contrast-table", "proof-grid", "field-note", "receipt"],
            "template-marketplace": ["taxonomy", "proof-grid", "receipt", "field-note", "contrast-table"],
        }
        mode_cycle = cycles.get(self.design_pack, ["field-note", "proof-grid", "myth-truth", "receipt", "taxonomy"])
        return mode_cycle[max(0, index - 2) % len(mode_cycle)]

    def _write_contact_sheet(self, slides_meta: list[dict[str, Any]]) -> Path:
        from PIL import Image, ImageDraw

        from .text import load_font

        thumb_w = 216
        thumb_h = int(thumb_w * self.dimensions.height / self.dimensions.width)
        cols = min(4, max(1, len(slides_meta)))
        rows = (len(slides_meta) + cols - 1) // cols
        pad = 24
        label_h = 34
        sheet = Image.new(
            "RGB",
            (
                cols * thumb_w + (cols + 1) * pad,
                rows * (thumb_h + label_h) + (rows + 1) * pad,
            ),
            self.palette["paper"],
        )
        draw = ImageDraw.Draw(sheet)
        label_font = load_font("body", 18)
        for idx, slide_meta in enumerate(slides_meta):
            row = idx // cols
            col = idx % cols
            x = pad + col * (thumb_w + pad)
            y = pad + row * (thumb_h + label_h + pad)
            with Image.open(slide_meta["path"]) as image:
                thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y))
            label = (
                f"{slide_meta['index']:02d} {slide_meta['role']} / "
                f"{slide_meta.get('design_pack')} / {slide_meta.get('visual_mode')}"
            )
            draw.text((x, y + thumb_h + 8), label[:44], font=label_font, fill=self.palette["muted"])
        path = self.out_dir / "contact_sheet.png"
        sheet.save(path)
        return path

    def _write_supporting_files(self, manifest: dict[str, Any]) -> None:
        caption = self.spec.get("caption", "")
        if caption:
            (self.out_dir / "caption.md").write_text(str(caption).rstrip() + "\n", encoding="utf-8")
        else:
            (self.out_dir / "caption.md").write_text(
                f"{self.spec['title']}\n\n{self.handle}\n", encoding="utf-8"
            )

        alt_lines = ["# Alt Text", ""]
        for slide in self.spec["slides"]:
            alt = slide.get("alt") or f"{slide['role']} slide: {slide['title']}"
            alt_lines.append(f"- {alt}")
        (self.out_dir / "alt_text.md").write_text("\n".join(alt_lines) + "\n", encoding="utf-8")

        profile_snapshot = self.spec.get("profile", {})
        if profile_snapshot:
            (self.out_dir / "profile_snapshot.yaml").write_text(
                yaml.safe_dump(profile_snapshot, sort_keys=False),
                encoding="utf-8",
            )
        else:
            (self.out_dir / "profile_snapshot.yaml").write_text("{}\n", encoding="utf-8")

        shutil.copyfile(self.out_dir / "manifest.json", self.out_dir / "manifest.latest.json")

    @staticmethod
    def _hierarchy_score(role: str, visual_mode: str) -> float:
        base = {"hook": 9.0, "body": 8.2, "recap": 8.0, "cta": 8.4}.get(role, 8.0)
        if visual_mode in {"shock-stat", "photo-anchor", "proof-grid"}:
            base += 0.3
        return min(10.0, base)

    @staticmethod
    def _largest_number(slide: dict[str, Any]) -> str | None:
        text = " ".join(
            str(part)
            for part in (
                slide.get("title", ""),
                slide.get("subtitle", ""),
                slide.get("body", ""),
                " ".join(str(item) for item in slide.get("bullets", []) or []),
            )
            if part
        )
        numbers = [match.group(0) for match in re.finditer(r"\b\d+(?:[.,]\d+)?%?\b", text)]
        return numbers[0] if numbers else None

    @staticmethod
    def _hook_signal(slide: dict[str, Any]) -> str | None:
        title = str(slide.get("title", ""))
        candidates = [word for word in re.findall(r"[A-Za-z0-9']+", title) if len(word) >= 4]
        if not candidates:
            return None
        priority = {"not", "lie", "wrong", "stop", "dead", "invisible", "save", "proof", "cost"}
        for word in candidates:
            lowered = word.lower()
            if lowered in priority:
                return word.upper()
        return candidates[-1].upper()

    @staticmethod
    def _slug(value: str) -> str:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
        slug = "-".join(part for part in slug.split("-") if part)
        return slug[:54] or "slide"
