"""Asset helpers for texture generation, logo fetching, and optional OpenAI prompts."""

from __future__ import annotations

import base64
import json
import os
import random
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFilter


def paper_texture(
    size: tuple[int, int],
    seed: str = "viral-carousel-maker",
    base_color: str = "#fbfaf6",
) -> Image.Image:
    """Create a reusable paper-like texture without external assets."""

    width, height = size
    rng = random.Random(seed)
    try:
        base_rgb = ImageColor.getrgb(base_color)
    except ValueError:
        base_rgb = ImageColor.getrgb("#fbfaf6")
    base = Image.new("RGB", size, base_rgb)
    noise = Image.new("RGB", size, base_rgb)
    pixels = noise.load()
    for y in range(height):
        for x in range(width):
            jitter = rng.randint(-10, 10)
            pixels[x, y] = tuple(max(0, min(255, channel + jitter)) for channel in base_rgb)
    noise = noise.filter(ImageFilter.GaussianBlur(radius=1.1))
    return Image.blend(base, noise, alpha=0.32)


def draw_logo_badge(
    text: str,
    size: tuple[int, int] = (180, 180),
    fill: str = "#05063f",
    background: str = "#ffffff",
) -> Image.Image:
    badge = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(badge)
    inset = 8
    draw.rounded_rectangle(
        (inset, inset, size[0] - inset, size[1] - inset),
        radius=28,
        fill=background,
        outline=fill,
        width=4,
    )
    initials = "".join(part[0] for part in text.replace(".", " ").split()[:2]).upper() or "?"
    try:
        from .text import load_font

        font = load_font("bold", 72)
    except Exception:
        font = None
    bbox = draw.textbbox((0, 0), initials, font=font)
    draw.text(
        ((size[0] - (bbox[2] - bbox[0])) / 2, (size[1] - (bbox[3] - bbox[1])) / 2 - 8),
        initials,
        fill=fill,
        font=font,
    )
    return badge


def fetch_logo_best_effort(name: str, domain: str | None, cache_dir: Path) -> Path | None:
    """Fetch a public logo best-effort. Failure is expected and safe."""

    if not domain:
        return None
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    target = cache_dir / f"{safe_name or 'logo'}.png"
    if target.exists():
        return target

    url = f"https://logo.clearbit.com/{domain}"
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "viral-carousel-maker/0.1"})
        with urllib.request.urlopen(request, timeout=4) as response:
            data = response.read(1_500_000)
        Image.open(PathBytes(data)).save(target)
        return target
    except Exception:
        return None


class PathBytes:
    """Tiny file-like wrapper for PIL without importing io at module import time."""

    def __init__(self, data: bytes):
        import io

        self._handle = io.BytesIO(data)

    def read(self, *args: Any, **kwargs: Any) -> bytes:
        return self._handle.read(*args, **kwargs)

    def seek(self, *args: Any, **kwargs: Any) -> int:
        return self._handle.seek(*args, **kwargs)


def collect_visual_prompts(spec: dict[str, Any]) -> list[dict[str, Any]]:
    prompts: list[dict[str, Any]] = []
    for index, slide in enumerate(spec.get("slides", []), start=1):
        prompt = str(slide.get("visual_prompt", "")).strip()
        if not prompt:
            continue
        prompts.append(
            {
                "id": slide.get("id", f"slide-{index}"),
                "slide_index": index,
                "role": slide.get("role"),
                "prompt": prompt,
                "recommended_use": "Codex native image generation first; OpenAI API fallback outside Codex.",
            }
        )
    return prompts


def write_prompts_jsonl(spec: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prompts = collect_visual_prompts(spec)
    output_path.write_text(
        "\n".join(json.dumps(item, sort_keys=True) for item in prompts) + ("\n" if prompts else ""),
        encoding="utf-8",
    )
    return output_path


def generate_openai_asset(prompt: str, out_path: Path, model: str = "gpt-image-2") -> Path:
    """Optional API fallback for non-Codex environments."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for OpenAI API asset generation.")
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError("Install the OpenAI SDK with `uv pip install openai`.") from exc

    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024",
        quality="high",
        n=1,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(result.data[0].b64_json))
    return out_path
