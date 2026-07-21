from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from core.domain import ProductionBrief, ProductionSlide

_DEFAULT_FONTS = [
    "C\\:/Windows/Fonts/arial.ttf",
    "C\\:/Windows/Fonts/calibri.ttf",
    "C\\:/Windows/Fonts/segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

_FONT_CACHE: ImageFont.FreeTypeFont | None = None
_FONT_BOLD_CACHE: ImageFont.FreeTypeFont | None = None

BACKGROUND_PRESETS: dict[str, tuple[int, int, int]] = {
    "bg_light": (248, 248, 248),
    "bg_dark": (32, 32, 40),
    "bg_gradient_dark": (20, 20, 30),
    "bg_gradient_brand": (10, 20, 40),
    "bg_white": (255, 255, 255),
    "bg_black": (0, 0, 0),
    "bg_navy": (10, 20, 50),
    "bg_charcoal": (40, 40, 48),
}


def _find_default_font() -> ImageFont.FreeTypeFont | None:
    global _FONT_CACHE
    if _FONT_CACHE is not None:
        return _FONT_CACHE
    for fp in _DEFAULT_FONTS:
        normalized = fp.replace("\\:", ":")
        if Path(normalized).exists():
            try:
                _FONT_CACHE = ImageFont.truetype(normalized, size=24)
                return _FONT_CACHE
            except OSError:
                continue
    return None


def _find_default_font_bold() -> ImageFont.FreeTypeFont | None:
    global _FONT_BOLD_CACHE
    if _FONT_BOLD_CACHE is not None:
        return _FONT_BOLD_CACHE

    bold_paths = [
        "C\\:/Windows/Fonts/arialbd.ttf",
        "C\\:/Windows/Fonts/calibrib.ttf",
        "C\\:/Windows/Fonts/segoeuib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for fp in bold_paths:
        normalized = fp.replace("\\:", ":")
        if Path(normalized).exists():
            try:
                _FONT_BOLD_CACHE = ImageFont.truetype(normalized, size=24)
                return _FONT_BOLD_CACHE
            except OSError:
                continue
    return None


def _resolve_asset(raw: str, project_root: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    return candidate


def _create_gradient(
    width: int,
    height: int,
    top_color: tuple[int, int, int],
    bottom_color: tuple[int, int, int],
) -> Image.Image:
    im = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(im)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return im


def _get_bg_color(slide: ProductionSlide, brand: object) -> tuple[int, int, int]:
    bg_key = slide.background or "bg_gradient_dark"
    if bg_key in BACKGROUND_PRESETS:
        return BACKGROUND_PRESETS[bg_key]
    return BACKGROUND_PRESETS["bg_gradient_dark"]


def _is_dark_bg(bg_color: tuple[int, int, int]) -> bool:
    r, g, b = bg_color[:3]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < 128


def _build_text_color(bg_color: tuple[int, int, int]) -> tuple[int, int, int]:
    if _is_dark_bg(bg_color):
        return (255, 255, 255)
    return (30, 30, 30)


def _build_accent_color(bg_color: tuple[int, int, int], brand: object) -> tuple[int, int, int]:
    if hasattr(brand, "colors_accent") and brand.colors_accent:
        try:
            hex_str = brand.colors_accent.lstrip("#")
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b)
        except (ValueError, IndexError):
            pass
    if _is_dark_bg(bg_color):
        return (100, 180, 255)
    return (0, 100, 200)


def _wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    if not words:
        return [text]

    lines: list[str] = []
    current_line: list[str] = []
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            bbox = font.getbbox(test_line)
            test_w = bbox[2] - bbox[0]
        except (AttributeError, TypeError):
            test_w = len(test_line) * (font.size // 2)

        if test_w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(" ".join(current_line))
    return lines if lines else [text]


def _text_width(
    text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont
) -> int:
    try:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]
    except (AttributeError, TypeError):
        return len(text) * (font.size // 2)


def _draw_brand_logo(
    draw: ImageDraw.Draw,
    brand: object,
    width: int,
    height: int,
    project_root: Path,
) -> None:
    if not hasattr(brand, "logo_path") or not brand.logo_path:
        return
    logo_path = _resolve_asset(brand.logo_path, project_root)
    if not logo_path.exists():
        return
    try:
        logo_img = Image.open(logo_path).convert("RGBA")
    except Exception:
        return

    target_w = int(width * 0.12)
    logo_w, logo_h = logo_img.size
    ratio = target_w / max(logo_w, 1)
    target_h = int(logo_h * ratio)
    logo_img = logo_img.resize((target_w, target_h), Image.LANCZOS)

    logo_pos = brand.logo_position if hasattr(brand, "logo_position") else "top-right"
    margin = int(height * 0.04)
    if logo_pos == "top-right":
        x = width - target_w - margin
        y = margin
    elif logo_pos == "top-left":
        x = margin
        y = margin
    elif logo_pos == "bottom-right":
        x = width - target_w - margin
        y = height - target_h - margin
    elif logo_pos == "bottom-left":
        x = margin
        y = height - target_h - margin
    else:
        x = width - target_w - margin
        y = margin

    draw._image.paste(logo_img, (x, y), logo_img)


def render_slide_image(
    slide: ProductionSlide,
    width: int,
    height: int,
    brand: object,
    project_root: Path,
) -> Image.Image:
    bg_color = _get_bg_color(slide, brand)

    if slide.background.startswith("bg_gradient"):
        top_color = bg_color
        bottom_color = (
            int(bg_color[0] * 0.3),
            int(bg_color[1] * 0.4),
            int(bg_color[2] * 0.8),
        )
        im = _create_gradient(width, height, top_color, bottom_color)
    else:
        im = Image.new("RGB", (width, height), bg_color)

    draw = ImageDraw.Draw(im)

    text_color = _build_text_color(bg_color)
    accent_color = _build_accent_color(bg_color, brand)
    muted_color = (
        int(text_color[0] * 0.6),
        int(text_color[1] * 0.6),
        int(text_color[2] * 0.6),
    )

    base_font = _find_default_font()
    bold_font = _find_default_font_bold()

    margin_x = int(width * 0.08)
    max_text_w = width - 2 * margin_x

    heading_h = int(height * 0.25)
    subheading_h = int(height * 0.18)
    body_h = int(height * 0.35)
    cta_h = int(height * 0.12)
    margin_bottom = int(height * 0.04)

    current_y = heading_h

    heading_size = int(height * 0.045)
    subheading_size = int(height * 0.032)
    body_size = int(height * 0.028)
    cta_size = int(height * 0.035)

    if base_font is not None:
        try:
            heading_font = base_font.font_variant(size=heading_size)
        except Exception:
            heading_font = ImageFont.load_default()
    else:
        heading_font = ImageFont.load_default()

    if bold_font is not None:
        try:
            bold_heading_font = bold_font.font_variant(size=heading_size)
        except Exception:
            bold_heading_font = heading_font
    else:
        bold_heading_font = heading_font

    if base_font is not None:
        try:
            subheading_font = base_font.font_variant(size=subheading_size)
        except Exception:
            subheading_font = ImageFont.load_default()
    else:
        subheading_font = ImageFont.load_default()

    if base_font is not None:
        try:
            body_font = base_font.font_variant(size=body_size)
        except Exception:
            body_font = ImageFont.load_default()
    else:
        body_font = ImageFont.load_default()

    if base_font is not None:
        try:
            cta_font = base_font.font_variant(size=cta_size)
        except Exception:
            cta_font = ImageFont.load_default()
    else:
        cta_font = ImageFont.load_default()

    if slide.heading.strip():
        lines = _wrap_text(slide.heading.strip(), bold_heading_font, max_text_w)
        for line in lines:
            line_w = _text_width(line, bold_heading_font)
            x = (width - line_w) // 2
            if current_y + heading_size + 8 <= heading_h + subheading_h:
                draw.text((x, current_y), line, fill=text_color, font=bold_heading_font)
                current_y += heading_size + 8

    if slide.subheading.strip():
        current_y += int(height * 0.02)
        lines = _wrap_text(slide.subheading.strip(), subheading_font, max_text_w)
        for line in lines:
            line_w = _text_width(line, subheading_font)
            x = (width - line_w) // 2
            draw.text((x, current_y), line, fill=muted_color, font=subheading_font)
            current_y += subheading_size + 6

    content_start_y = int(height * 0.38)
    current_y = content_start_y

    if slide.body.strip():
        lines = _wrap_text(slide.body.strip(), body_font, max_text_w)
        for line in lines:
            line_w = _text_width(line, body_font)
            x = (width - line_w) // 2
            draw.text((x, current_y), line, fill=text_color, font=body_font)
            current_y += body_size + 8

    if slide.list_items:
        current_y += int(height * 0.02)
        bullet_margin_x = int(width * 0.14)
        bullet_max_w = width - bullet_margin_x - margin_x
        for item in slide.list_items:
            bullet = "\u2022"
            draw.text(
                (margin_x, current_y),
                bullet,
                fill=accent_color,
                font=body_font,
            )
            lines = _wrap_text(item.strip(), body_font, bullet_max_w)
            if lines:
                draw.text((bullet_margin_x, current_y), lines[0], fill=text_color, font=body_font)
                current_y += body_size + 6
                for line in lines[1:]:
                    draw.text((bullet_margin_x, current_y), line, fill=text_color, font=body_font)
                    current_y += body_size + 6

    if slide.cta.strip():
        cta_y = height - cta_h - margin_bottom
        line_w = _text_width(slide.cta.strip(), cta_font)
        x = (width - line_w) // 2

        cta_pad_x = int(width * 0.06)
        cta_pad_y = int(height * 0.015)
        cta_box_x0 = x - cta_pad_x
        cta_box_y0 = cta_y - cta_pad_y
        cta_box_x1 = x + line_w + cta_pad_x
        cta_box_y1 = cta_y + cta_size + cta_pad_y
        draw.rounded_rectangle(
            (cta_box_x0, cta_box_y0, cta_box_x1, cta_box_y1),
            radius=int(height * 0.02),
            fill=accent_color,
        )
        cta_text_color = (255, 255, 255)
        draw.text((x, cta_y), slide.cta.strip(), fill=cta_text_color, font=cta_font)

    _draw_brand_logo(draw, brand, width, height, project_root)

    return im


def render_carousel(
    brief: ProductionBrief,
    output_dir: Path,
    project_root: Path,
) -> dict:
    slides = brief.slides
    if not slides:
        raise ValueError("ProductionBrief must have at least one slide for carousel")

    output_dir.mkdir(parents=True, exist_ok=True)

    W = brief.output.resolution_width or 1080
    H = brief.output.resolution_height or 1080
    if W <= 0 or H <= 0:
        raise ValueError("Carousel output dimensions must be positive")
    brand = brief.brand

    for stale_slide in output_dir.glob("slide_*.png"):
        stale_slide.unlink()

    result: dict[str, list[Path]] = {"slides": []}

    for i, slide in enumerate(slides):
        slide_num = slide.slide_number or (i + 1)
        im = render_slide_image(slide, W, H, brand, project_root)
        slide_path = output_dir / f"slide_{slide_num:02d}.png"
        im.save(slide_path, "PNG")
        result["slides"].append(slide_path)

    return result
