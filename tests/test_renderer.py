from pathlib import Path

from PIL import Image, ImageDraw

from viral_carousel_maker.qa import run_manifest_qa
from viral_carousel_maker.renderer import CarouselRenderer
from viral_carousel_maker.spec import load_spec
from viral_carousel_maker.text import text_size


ROOT = Path(__file__).resolve().parents[1]


def test_renderer_writes_pack(tmp_path):
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    manifest = CarouselRenderer(spec, tmp_path / "out").render()
    assert len(manifest["slides"]) == 8
    assert (tmp_path / "out" / "caption.md").exists()
    assert (tmp_path / "out" / "alt_text.md").exists()
    assert (tmp_path / "out" / "qa_report.md").exists()
    assert (tmp_path / "out" / "contact_sheet.png").exists()
    assert "virality" in manifest
    assert manifest["design"]["contact_sheet"].endswith("contact_sheet.png")
    ok, messages = run_manifest_qa(manifest)
    assert ok, messages
    first_slide = Path(manifest["slides"][0]["path"])
    with Image.open(first_slide) as image:
        assert image.size == (1080, 1350)


def test_renderer_honors_custom_paper_palette(tmp_path):
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["theme"] = {
        "palette": {
            "paper": "#0d0d0d",
            "text": "#ffffff",
            "muted": "#a0a0a0",
        }
    }

    manifest = CarouselRenderer(spec, tmp_path / "out").render()
    first_slide = Path(manifest["slides"][0]["path"])
    with Image.open(first_slide) as image:
        red, green, blue = image.getpixel((12, 12))[:3]
        assert max(red, green, blue) < 40


def test_cta_eyebrow_fits_inside_badge():
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    renderer = CarouselRenderer(spec, "unused")
    image = Image.new("RGB", (renderer.dimensions.width, renderer.dimensions.height), "#0d0d0d")
    draw = ImageDraw.Draw(image)
    badge_padding_x = 44
    max_width = renderer.dimensions.width - renderer.dimensions.margin * 2 - badge_padding_x * 2

    font, fit = renderer._fit_single_line_font(
        draw,
        "FOUND THIS HELPFUL?",
        "bold",
        max_width=max_width,
        start_size=int(renderer.dimensions.width * 0.05),
        min_size=34,
    )

    assert fit
    assert text_size(draw, "FOUND THIS HELPFUL?", font)[0] <= max_width


def test_renderer_records_visual_mode_metadata(tmp_path):
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    spec["strategy"] = {"visual_mode": "shock-stat"}
    spec["slides"][0]["visual_mode"] = "shock-stat"
    manifest = CarouselRenderer(spec, tmp_path / "out").render()
    assert manifest["slides"][0]["visual_mode"] == "shock-stat"
    assert "shock-stat" in manifest["design"]["visual_modes"]
