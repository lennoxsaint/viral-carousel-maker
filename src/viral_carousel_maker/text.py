"""Text layout helpers for Pillow rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import ImageDraw, ImageFont

from .models import FONT_CANDIDATES


def load_font(kind: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for raw_path in FONT_CANDIDATES.get(kind, []) + FONT_CANDIDATES["body"]:
        path = Path(raw_path)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines():
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if text_size(draw, candidate, font)[0] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    kind: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int = 24,
    line_spacing: float = 1.16,
) -> tuple[ImageFont.ImageFont, list[str], bool]:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        line_height = int(size * line_spacing)
        height = max(line_height, len(lines) * line_height)
        widest = max((text_size(draw, line, font)[0] for line in lines), default=0)
        if widest <= max_width and height <= max_height:
            return font, lines, True
    font = load_font(kind, min_size)
    return font, wrap_text(draw, text, font, max_width), False


def draw_multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: Iterable[str],
    font: ImageFont.ImageFont,
    fill: str,
    line_height: int,
    anchor: str = "la",
) -> tuple[int, int, int, int]:
    x, y = xy
    top = y
    max_right = x
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill, anchor=anchor)
        width, _ = text_size(draw, line, font)
        max_right = max(max_right, x + width)
        y += line_height
    return x, top, max_right, y

