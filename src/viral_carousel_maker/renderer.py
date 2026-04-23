"""Pillow renderer for viral carousel specs."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, ImageDraw

from .assets import paper_texture, write_prompts_jsonl
from .critic import normalize_critic_output
from .design import resolve_design_pack, resolve_design_tokens, resolve_palette
from .models import dimensions_for
from .pattern_bank import select_pattern_bundle
from .qa import build_visual_qa, write_qa_report, write_visual_qa_files
from .spec import normalized_handle, validate_spec
from .text import draw_multiline, fit_font, load_font, text_size, wrap_text
from .virality import score_spec


class CarouselRenderer:
    def __init__(self, spec: dict[str, Any], out_dir: str | Path):
        self.spec = spec
        self.out_dir = Path(out_dir)
        self.dimensions = dimensions_for(str(spec.get("aspect_ratio", "vertical")))
        self.strategy = spec.get("strategy", {}) if isinstance(spec.get("strategy"), dict) else {}
        self.design_pack = resolve_design_pack(spec)
        self.palette = resolve_palette(spec, self.design_pack)
        self.design_tokens = resolve_design_tokens(spec, self.design_pack)
        self.handle = normalized_handle(str(spec["handle"]))
        self.warnings = validate_spec(spec)
        self.slide_dir = self.out_dir / "slides"
        self.asset_dir = self.out_dir / "assets"

    def render(self) -> dict[str, Any]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.slide_dir.mkdir(parents=True, exist_ok=True)
        self.asset_dir.mkdir(parents=True, exist_ok=True)

        slides_meta = []
        body_total = sum(1 for slide in self.spec["slides"] if slide["role"] == "body")
        body_seen = 0
        for index, slide in enumerate(self.spec["slides"], start=1):
            if slide["role"] == "body":
                body_seen += 1
            image, meta = self._render_slide(slide, index, body_seen, body_total)
            filename = f"{index:02d}-{slide['role']}-{self._slug(slide['title'])}.png"
            path = self.slide_dir / filename
            image.save(path)
            meta["path"] = str(path)
            slides_meta.append(meta)

        contact_sheet_path = self._write_contact_sheet(slides_meta)
        prompts_path = write_prompts_jsonl(self.spec, self.out_dir / "prompts.jsonl")
        virality = score_spec(self.spec)
        manifest = {
            "title": self.spec["title"],
            "handle": self.handle,
            "aspect_ratio": self.spec["aspect_ratio"],
            "dimensions": [self.dimensions.width, self.dimensions.height],
            "template_family": self.spec["template_family"],
            "strategy": self.strategy,
            "visual_thesis": self.strategy.get("visual_thesis", ""),
            "critic": normalize_critic_output(self.spec.get("critic")),
            "pattern_bank": self.spec.get("pattern_bank") or select_pattern_bundle(self.spec),
            "learning": self.spec.get("learning", {}),
            "virality": virality,
            "design": {
                "render_engine": "pillow",
                "design_pack": self.design_pack,
                "palette": self.palette,
                "tokens": self.design_tokens,
                "visual_modes": sorted(
                    {
                        slide_meta.get("visual_mode", "editorial-paper")
                        for slide_meta in slides_meta
                    }
                ),
                "contact_sheet": str(contact_sheet_path),
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

    def _base(self, slide: dict[str, Any]) -> Image.Image:
        texture_seed = f"{self.spec['title']}:{slide.get('id', slide.get('title'))}"
        image = paper_texture(
            (self.dimensions.width, self.dimensions.height),
            seed=texture_seed,
            base_color=self.palette["paper"],
        )
        draw = ImageDraw.Draw(image, "RGBA")
        if self.spec["template_family"] in {"data", "cta"}:
            self._draw_soft_band(draw)
        return image

    def _render_slide(
        self,
        slide: dict[str, Any],
        index: int,
        body_seen: int,
        body_total: int,
    ) -> tuple[Image.Image, dict[str, Any]]:
        image = self._base(slide)
        draw = ImageDraw.Draw(image, "RGBA")
        role = slide["role"]
        visual_mode = self._visual_mode_for(slide)
        meta = {
            "index": index,
            "id": slide.get("id", f"slide-{index}"),
            "role": role,
            "title": slide["title"],
            "main_idea": slide.get("main_idea", ""),
            "visual_mode": visual_mode,
            "handle_drawn": True,
            "text_fit": True,
            "cta_type": None,
        }

        self._draw_visual_mode(draw, slide, visual_mode)
        if role == "hook":
            meta["text_fit"] = self._draw_hook(draw, slide)
        elif role == "body":
            self._draw_progress(draw, body_seen, body_total)
            meta["text_fit"] = self._draw_body(draw, slide)
            self._draw_swipe_arrow(draw)
        elif role == "recap":
            meta["text_fit"] = self._draw_recap(draw, slide)
        elif role == "cta":
            cta = slide.get("cta", self.spec.get("cta", {"type": "follow"}))
            meta["cta_type"] = cta.get("type", "follow")
            meta["text_fit"] = self._draw_cta(draw, slide, cta)

        self._draw_handle(draw)
        return image, meta

    def _draw_hook(self, draw: ImageDraw.ImageDraw, slide: dict[str, Any]) -> bool:
        d = self.dimensions
        margin = d.margin
        title = str(slide["title"]).upper()
        subtitle = str(slide.get("subtitle", ""))
        title_font, title_lines, title_fit = fit_font(
            draw,
            title,
            "heading",
            max_width=d.width - margin * 2,
            max_height=int(d.height * 0.42),
            start_size=int(d.width * 0.145),
            min_size=58,
            line_spacing=0.95,
        )
        title_height = int(title_font.size * 0.95) * len(title_lines)
        y = int(d.height * 0.18)
        draw_multiline(
            draw,
            (margin, y),
            title_lines,
            title_font,
            self.palette["text"],
            int(title_font.size * 0.95),
        )
        self._draw_accent_rule(draw, margin, y + title_height + 44)

        body_fit = True
        if subtitle:
            body_font, body_lines, body_fit = fit_font(
                draw,
                subtitle,
                "body",
                max_width=int(d.width * 0.66),
                max_height=int(d.height * 0.24),
                start_size=int(d.width * 0.045),
                min_size=28,
            )
            draw_multiline(
                draw,
                (margin, y + title_height + 120),
                body_lines,
                body_font,
                self.palette["text"],
                int(body_font.size * 1.35),
            )

        if slide.get("badge"):
            self._draw_badge(draw, str(slide["badge"]), d.width - margin - 270, margin)
        return title_fit and body_fit

    def _draw_body(self, draw: ImageDraw.ImageDraw, slide: dict[str, Any]) -> bool:
        d = self.dimensions
        margin = d.margin
        top = int(d.height * 0.23)
        title_font, title_lines, title_fit = fit_font(
            draw,
            str(slide["title"]).upper(),
            "heading",
            max_width=d.width - margin * 2,
            max_height=int(d.height * 0.22),
            start_size=int(d.width * 0.085),
            min_size=42,
            line_spacing=0.95,
        )
        draw_multiline(
            draw,
            (margin, top),
            title_lines,
            title_font,
            self.palette["text"],
            int(title_font.size * 0.95),
        )
        self._draw_accent_rule(draw, margin, top + int(title_font.size * 1.08) * len(title_lines) + 36)

        text_blocks = []
        if slide.get("body"):
            text_blocks.append(str(slide["body"]))
        for bullet in slide.get("bullets", []) or []:
            text_blocks.append(f"- {bullet}")
        body_text = "\n\n".join(text_blocks)
        body_font, body_lines, body_fit = fit_font(
            draw,
            body_text,
            "body",
            max_width=int(d.width * 0.70),
            max_height=int(d.height * 0.45),
            start_size=int(d.width * 0.043),
            min_size=24,
        )
        draw_multiline(
            draw,
            (margin, int(d.height * 0.45)),
            body_lines,
            body_font,
            self.palette["text"],
            int(body_font.size * 1.36),
        )
        self._draw_optional_logo(draw, slide)
        return title_fit and body_fit

    def _visual_mode_for(self, slide: dict[str, Any]) -> str:
        return str(
            slide.get("visual_mode")
            or self.strategy.get("visual_mode")
            or "editorial-paper"
        )

    def _draw_visual_mode(
        self,
        draw: ImageDraw.ImageDraw,
        slide: dict[str, Any],
        visual_mode: str,
    ) -> None:
        d = self.dimensions
        accent = self.palette["accent"]
        text = self.palette["text"]
        muted = self.palette["muted"]
        if visual_mode in {"editorial-paper", "quiet-truth"}:
            if visual_mode == "quiet-truth":
                draw.rounded_rectangle(
                    (
                        d.width - d.margin - int(d.width * 0.11),
                        d.margin,
                        d.width - d.margin,
                        d.margin + int(d.width * 0.11),
                    ),
                    radius=18,
                    outline=self._hex_to_rgba(muted, 70),
                    width=2,
                )
            return

        if visual_mode == "shock-stat":
            badge = str(slide.get("badge", "") or self._largest_number(slide) or "!")
            font = load_font("bold", int(d.width * 0.24))
            draw.text(
                (d.width - d.margin, int(d.height * 0.78)),
                badge,
                font=font,
                fill=self._hex_to_rgba(accent, 32),
                anchor="rd",
            )
            return

        if visual_mode == "proof-grid":
            left = d.margin
            top = int(d.height * 0.58)
            cell_w = int((d.width - d.margin * 2 - 24) / 2)
            cell_h = int(d.height * 0.09)
            for row in range(2):
                for col in range(2):
                    x = left + col * (cell_w + 24)
                    y = top + row * (cell_h + 22)
                    draw.rounded_rectangle(
                        (x, y, x + cell_w, y + cell_h),
                        radius=18,
                        outline=self._hex_to_rgba(text, 44),
                        fill=self._hex_to_rgba("#ffffff", 88),
                        width=2,
                    )
            return

        if visual_mode in {"myth-truth", "contrast-table"}:
            split_y = int(d.height * 0.55)
            draw.rectangle(
                (0, split_y, d.width, d.height),
                fill=self._hex_to_rgba(accent, 24),
            )
            draw.line((d.margin, split_y, d.width - d.margin, split_y), fill=self._hex_to_rgba(text, 62), width=2)
            return

        if visual_mode == "taxonomy":
            left = int(d.width * 0.51)
            for i in range(5):
                y = int(d.height * (0.28 + i * 0.105))
                draw.line((left, y, d.width - d.margin, y), fill=self._hex_to_rgba(text, 58), width=3)
                draw.ellipse((left - 8, y - 8, left + 8, y + 8), fill=accent)
            return

        if visual_mode == "receipt":
            x = int(d.width * 0.58)
            y = int(d.height * 0.18)
            w = int(d.width * 0.28)
            h = int(d.height * 0.46)
            draw.rounded_rectangle(
                (x, y, x + w, y + h),
                radius=18,
                fill="#ffffff",
                outline=self._hex_to_rgba(text, 84),
                width=3,
            )
            for i in range(6):
                line_y = y + 58 + i * 52
                draw.line((x + 28, line_y, x + w - 28, line_y), fill=self._hex_to_rgba(muted, 80), width=2)
            return

        if visual_mode == "field-note":
            font = load_font("bold", int(d.width * 0.028))
            label = "FIELD NOTE"
            x = d.width - d.margin - int(d.width * 0.23)
            y = d.margin + 14
            draw.rounded_rectangle(
                (x - 24, y - 14, d.width - d.margin, y + 42),
                radius=14,
                fill=self._hex_to_rgba(accent, 220),
            )
            draw.text((x, y), label, font=font, fill="#ffffff")
            return

        if visual_mode == "photo-anchor":
            x = int(d.width * 0.56)
            y = int(d.height * 0.25)
            w = int(d.width * 0.30)
            h = int(d.height * 0.36)
            draw.rounded_rectangle(
                (x, y, x + w, y + h),
                radius=34,
                fill=self._hex_to_rgba(accent, 42),
                outline=self._hex_to_rgba(text, 64),
                width=3,
            )
            draw.ellipse(
                (
                    x + int(w * 0.22),
                    y + int(h * 0.18),
                    x + int(w * 0.78),
                    y + int(h * 0.74),
                ),
                outline=self._hex_to_rgba(text, 55),
                width=3,
            )


    def _draw_recap(self, draw: ImageDraw.ImageDraw, slide: dict[str, Any]) -> bool:
        d = self.dimensions
        margin = d.margin
        title_font = load_font("heading", int(d.width * 0.082))
        draw.text((margin, int(d.height * 0.15)), "TL;DR", font=title_font, fill=self.palette["text"])
        self._draw_accent_rule(draw, margin, int(d.height * 0.15) + int(d.width * 0.1))

        bullets = slide.get("bullets", []) or []
        if not bullets and slide.get("body"):
            bullets = [line.strip("- ") for line in str(slide["body"]).splitlines() if line.strip()]
        bullet_font, _, fit = fit_font(
            draw,
            "\n".join(str(bullet) for bullet in bullets),
            "body",
            max_width=d.width - margin * 2,
            max_height=int(d.height * 0.58),
            start_size=int(d.width * 0.041),
            min_size=24,
        )
        y = int(d.height * 0.31)
        for bullet in bullets[:9]:
            circle_x = margin + 8
            circle_y = y + int(bullet_font.size * 0.45)
            draw.ellipse(
                (circle_x, circle_y, circle_x + 14, circle_y + 14),
                fill=self.palette["accent"],
            )
            lines = wrap_text(draw, str(bullet), bullet_font, d.width - margin * 2 - 50)
            draw_multiline(
                draw,
                (margin + 42, y),
                lines,
                bullet_font,
                self.palette["text"],
                int(bullet_font.size * 1.3),
            )
            y += max(int(bullet_font.size * 1.55), len(lines) * int(bullet_font.size * 1.3) + 24)
        return fit

    def _draw_cta(self, draw: ImageDraw.ImageDraw, slide: dict[str, Any], cta: dict[str, Any]) -> bool:
        d = self.dimensions
        margin = d.margin
        cta_type = str(cta.get("type", "follow"))
        eyebrow = "FOUND THIS HELPFUL?"
        badge_padding_x = 44
        badge_max_width = d.width - margin * 2
        eyebrow_font, eyebrow_fit = self._fit_single_line_font(
            draw,
            eyebrow,
            "bold",
            max_width=badge_max_width - badge_padding_x * 2,
            start_size=int(d.width * 0.05),
            min_size=34,
        )
        eyebrow_width, eyebrow_height = text_size(draw, eyebrow, eyebrow_font)
        badge_width = min(
            badge_max_width,
            max(int(d.width * 0.52), eyebrow_width + badge_padding_x * 2),
        )
        badge_height = max(int(d.height * 0.07), eyebrow_height + 34)
        badge_x = int((d.width - badge_width) / 2)
        badge_y = int(d.height * 0.12)
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_width, badge_y + badge_height),
            radius=badge_height // 2,
            fill=self.palette["text"],
        )
        draw.text(
            (badge_x + badge_width / 2, badge_y + badge_height / 2),
            eyebrow,
            font=eyebrow_font,
            fill=self.palette["paper"],
            anchor="mm",
        )

        title = "Follow" if cta_type == "follow" else str(cta.get("label", slide["title"]))
        title_font, title_lines, title_fit = fit_font(
            draw,
            title,
            "bold",
            max_width=d.width - margin * 2,
            max_height=int(d.height * 0.22),
            start_size=int(d.width * 0.135),
            min_size=58,
            line_spacing=1.0,
        )
        y = int(d.height * 0.42)
        draw_multiline(
            draw,
            (margin, y),
            title_lines,
            title_font,
            self.palette["accent_2"],
            int(title_font.size * 1.02),
        )

        handle_font = load_font("bold", int(d.width * 0.063))
        main_handle = str(cta.get("handle", self.handle))
        draw.text((margin, int(d.height * 0.64)), main_handle, font=handle_font, fill=self.palette["text"])

        desc = str(cta.get("description", slide.get("subtitle", "")))
        if cta_type == "offer":
            desc = f"{desc}\n{cta.get('url', '')}".strip()
        desc_font, desc_lines, desc_fit = fit_font(
            draw,
            desc,
            "body",
            max_width=d.width - margin * 2,
            max_height=int(d.height * 0.18),
            start_size=int(d.width * 0.039),
            min_size=22,
        )
        draw_multiline(
            draw,
            (margin, int(d.height * 0.75)),
            desc_lines,
            desc_font,
            self.palette["text"],
            int(desc_font.size * 1.35),
        )
        return eyebrow_fit and title_fit and desc_fit

    @staticmethod
    def _fit_single_line_font(
        draw: ImageDraw.ImageDraw,
        text: str,
        kind: str,
        max_width: int,
        start_size: int,
        min_size: int,
    ):
        for size in range(start_size, min_size - 1, -2):
            font = load_font(kind, size)
            width, _ = text_size(draw, text, font)
            if width <= max_width:
                return font, True
        return load_font(kind, min_size), False

    def _draw_handle(self, draw: ImageDraw.ImageDraw) -> None:
        d = self.dimensions
        font = load_font("body", int(d.width * 0.025))
        draw.text(
            (d.margin, d.height - int(d.height * 0.075)),
            self.handle,
            font=font,
            fill=self.palette["muted"],
        )

    def _draw_progress(self, draw: ImageDraw.ImageDraw, current: int, total: int) -> None:
        d = self.dimensions
        radius = int(d.width * 0.071)
        x = d.margin
        y = d.margin
        draw.ellipse((x, y, x + radius * 2, y + radius * 2), fill=self.palette["accent"])
        font = load_font("bold", int(radius * 0.62))
        draw.text(
            (x + radius, y + radius),
            f"{current}/{total}",
            font=font,
            fill="#ffffff",
            anchor="mm",
        )

    def _draw_swipe_arrow(self, draw: ImageDraw.ImageDraw) -> None:
        d = self.dimensions
        w = int(d.width * 0.16)
        h = int(d.height * 0.055)
        x = d.width - d.margin - w
        y = d.height - int(d.height * 0.19)
        draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=self.palette["accent"])
        line_y = y + h // 2
        draw.line((x + w * 0.32, line_y, x + w * 0.68, line_y), fill="#ffffff", width=4)
        draw.polygon(
            [
                (x + w * 0.68, line_y - 12),
                (x + w * 0.82, line_y),
                (x + w * 0.68, line_y + 12),
            ],
            fill="#ffffff",
        )

    def _draw_accent_rule(self, draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
        width = int(self.dimensions.width * 0.22)
        draw.rounded_rectangle((x, y, x + width, y + 14), radius=7, fill=self.palette["accent"])

    def _draw_badge(self, draw: ImageDraw.ImageDraw, text: str, x: int, y: int) -> None:
        font = load_font("bold", 42)
        text_w, text_h = text_size(draw, text, font)
        pad_x = 32
        pad_y = 20
        draw.rounded_rectangle(
            (x, y, x + text_w + pad_x * 2, y + text_h + pad_y * 2),
            radius=26,
            fill=self.palette["text"],
        )
        draw.text((x + pad_x, y + pad_y), text, font=font, fill="#ffffff")

    def _draw_soft_band(self, draw: ImageDraw.ImageDraw) -> None:
        d = self.dimensions
        draw.rounded_rectangle(
            (
                d.margin,
                int(d.height * 0.54),
                d.width - d.margin,
                int(d.height * 0.76),
            ),
            radius=34,
            fill=self._hex_to_rgba(self.palette["accent"], 34),
        )

    def _draw_optional_logo(self, draw: ImageDraw.ImageDraw, slide: dict[str, Any]) -> None:
        logo = slide.get("logo")
        if not isinstance(logo, dict):
            return
        d = self.dimensions
        label = str(logo.get("name", "Logo"))
        initials = "".join(part[0] for part in label.replace(".", " ").split()[:2]).upper() or "?"
        size = int(d.width * 0.14)
        x = d.width - d.margin - size
        y = int(d.height * 0.52)
        draw.rounded_rectangle(
            (x, y, x + size, y + size),
            radius=24,
            fill="#ffffff",
            outline=self.palette["text"],
            width=4,
        )
        font = load_font("bold", int(size * 0.42))
        draw.text(
            (x + size / 2, y + size / 2),
            initials,
            font=font,
            fill=self.palette["text"],
            anchor="mm",
        )

    def _write_contact_sheet(self, slides_meta: list[dict[str, Any]]) -> Path:
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
            label = f"{slide_meta['index']:02d} {slide_meta['role']} / {slide_meta.get('visual_mode', 'editorial-paper')}"
            draw.text((x, y + thumb_h + 8), label, font=label_font, fill=self.palette["muted"])
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
    def _hex_to_rgba(hex_value: str, alpha: int) -> tuple[int, int, int, int]:
        value = hex_value.lstrip("#")
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)

    @staticmethod
    def _slug(value: str) -> str:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
        slug = "-".join(part for part in slug.split("-") if part)
        return slug[:54] or "slide"
