from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from core.domain import (
    ContentFormat,
    ProductionBrief,
    ProductionBrand,
    ProductionOutput,
    ProductionSlide,
)


def _make_brief(slides):
    return ProductionBrief(
        workspace_id="test",
        project_id="test",
        production_brief_id="brief_test",
        scenario_id="scenario_test",
        content_format=ContentFormat.INSTAGRAM_CAROUSEL,
        slides=slides,
        output=ProductionOutput(resolution_width=1080, resolution_height=1080, slide_count=len(slides)),
        brand=ProductionBrand(),
    )


class RenderSlideImageTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_single_slide_renders_png(self):
        from core.tools.carousel.renderer import render_slide_image

        slide = ProductionSlide(
            slide_number=1,
            heading="Test Heading",
            subheading="This is a test subheading",
            body="Body text for the slide.",
            cta="Learn More",
            background="bg_gradient_dark",
        )
        im = render_slide_image(slide, 1080, 1080, ProductionBrand(), Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1080))

        output_path = Path(self.temp_dir.name) / "test_slide.png"
        im.save(output_path, "PNG")
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 100)

    def test_slide_with_list_items(self):
        from core.tools.carousel.renderer import render_slide_image

        slide = ProductionSlide(
            slide_number=1,
            heading="Benefits",
            list_items=["Faster results", "Better quality", "Less effort"],
            background="bg_light",
        )
        im = render_slide_image(slide, 1080, 1080, ProductionBrand(), Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1080))

    def test_slide_without_heading(self):
        from core.tools.carousel.renderer import render_slide_image

        slide = ProductionSlide(
            slide_number=1,
            body="Only body text, no heading.",
            background="bg_dark",
        )
        im = render_slide_image(slide, 1080, 1080, ProductionBrand(), Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1080))

    def test_slide_empty_content(self):
        from core.tools.carousel.renderer import render_slide_image

        slide = ProductionSlide(slide_number=1, background="bg_gradient_dark")
        im = render_slide_image(slide, 1080, 1080, ProductionBrand(), Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1080))

    def test_slide_non_standard_resolution(self):
        from core.tools.carousel.renderer import render_slide_image

        slide = ProductionSlide(
            slide_number=1,
            heading="Wide slide",
            background="bg_navy",
        )
        im = render_slide_image(slide, 1080, 1350, ProductionBrand(), Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1350))

    def test_brand_accent_color(self):
        from core.tools.carousel.renderer import render_slide_image

        brand = ProductionBrand(colors_accent="#FF5733")
        slide = ProductionSlide(
            slide_number=1,
            heading="With brand accent",
            cta="Get Started",
            background="bg_gradient_dark",
        )
        im = render_slide_image(slide, 1080, 1080, brand, Path(self.temp_dir.name))
        self.assertEqual(im.size, (1080, 1080))


class RenderCarouselTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_render_multiple_slides(self):
        from core.tools.carousel.renderer import render_carousel

        slides = [
            ProductionSlide(slide_number=1, heading="Hook", background="bg_gradient_dark"),
            ProductionSlide(slide_number=2, heading="Key Point 1", body="Details about point 1.", background="bg_dark"),
            ProductionSlide(slide_number=3, heading="Key Point 2", body="Details about point 2.", background="bg_dark"),
            ProductionSlide(slide_number=4, heading="CTA", cta="Follow Us", background="bg_gradient_dark"),
        ]
        brief = _make_brief(slides)
        output_dir = Path(self.temp_dir.name) / "carousel"
        result = render_carousel(brief, output_dir, Path(self.temp_dir.name))
        self.assertIn("slides", result)
        self.assertEqual(len(result["slides"]), 4)
        for i, p in enumerate(result["slides"]):
            self.assertTrue(p.exists(), f"Slide {i+1} not found: {p}")
            self.assertGreater(p.stat().st_size, 100)

    def test_render_single_slide(self):
        from core.tools.carousel.renderer import render_carousel

        slides = [ProductionSlide(slide_number=1, heading="Solo slide", background="bg_light")]
        brief = _make_brief(slides)
        output_dir = Path(self.temp_dir.name) / "carousel_solo"
        result = render_carousel(brief, output_dir, Path(self.temp_dir.name))
        self.assertEqual(len(result["slides"]), 1)
        self.assertTrue(result["slides"][0].exists())

    def test_empty_slides_raises(self):
        from core.tools.carousel.renderer import render_carousel

        brief = _make_brief([])
        output_dir = Path(self.temp_dir.name) / "carousel_empty"
        with self.assertRaises(ValueError):
            render_carousel(brief, output_dir, Path(self.temp_dir.name))


class BackgroundPresetTests(unittest.TestCase):
    def test_all_presets_are_valid_colors(self):
        from core.tools.carousel.renderer import BACKGROUND_PRESETS

        for name, color in BACKGROUND_PRESETS.items():
            self.assertEqual(len(color), 3, f"Preset {name} is not RGB triplet")
            for channel in color:
                self.assertGreaterEqual(channel, 0)
                self.assertLessEqual(channel, 255)

    def test_bg_light_is_bright(self):
        from core.tools.carousel.renderer import BACKGROUND_PRESETS

        color = BACKGROUND_PRESETS["bg_light"]
        luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        self.assertGreater(luminance, 200)

    def test_bg_dark_is_dark(self):
        from core.tools.carousel.renderer import BACKGROUND_PRESETS

        color = BACKGROUND_PRESETS["bg_dark"]
        luminance = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        self.assertLess(luminance, 80)
