from pathlib import Path

from PIL import Image

from viral_carousel_maker.qa import run_manifest_qa
from viral_carousel_maker.renderer import CarouselRenderer
from viral_carousel_maker.spec import load_spec


ROOT = Path(__file__).resolve().parents[1]


def test_renderer_writes_pack(tmp_path):
    spec = load_spec(ROOT / "examples" / "specs" / "ai-framework.yaml")
    manifest = CarouselRenderer(spec, tmp_path / "out").render()
    assert len(manifest["slides"]) == 8
    assert (tmp_path / "out" / "caption.md").exists()
    assert (tmp_path / "out" / "alt_text.md").exists()
    assert (tmp_path / "out" / "qa_report.md").exists()
    ok, messages = run_manifest_qa(manifest)
    assert ok, messages
    first_slide = Path(manifest["slides"][0]["path"])
    with Image.open(first_slide) as image:
        assert image.size == (1080, 1350)

