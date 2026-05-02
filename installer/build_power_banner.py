# installer/build_power_banner.py
"""
Builds installer/power_banner.bmp — the hero bitmap for the Power Mode
celebration wizard page.

Composition (600×300):
- AI-generated Atlas Navy background (installer/power_banner_bg.png)
- 170px K-mark from koda.ico, vertically centred on the LEFT
- Three-pass bloom around the K-mark (outer haze + mid + hot core)
- Horizontal light beam emanating from the K-mark across the banner
- Kicker label "UNLOCKED" tracked-out small caps in NAVY_BRIGHT
- Headline "POWER MODE" in WHITE, auto-fit to fill the right column
- Status row: green operational dot + "Hardware acceleration active" in DIM

Usage:
    venv/Scripts/python installer/build_power_banner.py

Re-run when power_banner_bg.png or this composition changes. Output is
committed so ISCC builds don't need PIL on the build host.

Canonical AI prompt for power_banner_bg.png (regenerate via ChatGPT /
Gemini / DALL-E / Midjourney if the background needs to change):

    Premium dark navy background banner image for a Windows installer
    page celebrating GPU hardware detection. Color palette: deep
    midnight charcoal-blue background (#0e1419 to #161d24 vertical
    gradient) with a single hero accent in IBM/Maersk premium navy
    (#1c5fb8) appearing as a subtle abstract glow or atmospheric
    element on one side. Mood: aerospace-corporate-premium, like Maersk
    shipping or Pan Am branding — NOT Tailwind blue (#3b82f6), NOT
    bright/saturated, NOT video-game-coded. Composition: 600x300
    pixels, generous empty space in the center for a logo and text
    overlay. NO text in the image. NO logos in the image. Style:
    minimalist, restrained, single accent on a dark base. NOT
    earth-tone, NOT pink/rose, NOT carmine/red. Should feel like
    premium American tooling.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(INSTALLER_DIR)

BG_PATH = os.path.join(INSTALLER_DIR, "power_banner_bg.png")
ICO_PATH = os.path.join(PROJECT_ROOT, "koda.ico")
OUTPUT_PATH = os.path.join(INSTALLER_DIR, "power_banner.bmp")

W, H = 600, 300
KMARK_SIZE = 170
KMARK_X = 28

# Atlas Navy palette (hex shown alongside RGB for spec traceability)
NAVY_DEEP = (28, 95, 184)        # #1c5fb8 — locked Atlas Navy hero accent
NAVY_BRIGHT = (96, 178, 255)     # brighter navy for kicker label
NAVY_GLOW = (110, 195, 255)      # outer bloom + light beam tint
WHITE = (245, 248, 252)          # headline foreground
DIM = (175, 192, 215)            # subtitle, secondary text
GREEN = (46, 204, 113)           # #2ecc71 — operational dot, matches K-mark ready state


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Segoe UI (Win 11 system font) at the requested size and weight."""
    path = "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    if not os.path.exists(path):
        return ImageFont.load_default()
    return ImageFont.truetype(path, size)


def _build_bloom_layer(canvas_size: tuple[int, int]) -> Image.Image:
    """Three-pass bloom: outer atmospheric haze, mid bloom, hot core.
    Massive gaussian blur fuses them into one continuous glow."""
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    kmark_y = (H - KMARK_SIZE) // 2
    # Outer atmospheric haze
    draw.ellipse(
        [KMARK_X - 110, kmark_y - 110,
         KMARK_X + KMARK_SIZE + 110, kmark_y + KMARK_SIZE + 110],
        fill=(74, 158, 245, 70),
    )
    # Mid bloom
    draw.ellipse(
        [KMARK_X - 50, kmark_y - 50,
         KMARK_X + KMARK_SIZE + 50, kmark_y + KMARK_SIZE + 50],
        fill=(96, 178, 255, 130),
    )
    # Hot core (tightest, brightest)
    draw.ellipse(
        [KMARK_X - 12, kmark_y - 12,
         KMARK_X + KMARK_SIZE + 12, kmark_y + KMARK_SIZE + 12],
        fill=(140, 205, 255, 170),
    )
    return layer.filter(ImageFilter.GaussianBlur(48))


def _build_beam_layer(canvas_size: tuple[int, int]) -> Image.Image:
    """Horizontal energy beam from the K-mark out across the banner."""
    layer = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    beam_y = H // 2
    draw.rectangle(
        [KMARK_X + KMARK_SIZE // 2, beam_y - 18, W, beam_y + 18],
        fill=(*NAVY_GLOW, 70),
    )
    return layer.filter(ImageFilter.GaussianBlur(28))


def _autofit_headline(draw: ImageDraw.ImageDraw, text: str, max_width: int,
                      max_size: int = 80, min_size: int = 24) -> tuple[ImageFont.ImageFont, int, int]:
    """Largest font size where `text` fits within `max_width`. Returns (font, width, height)."""
    for size in range(max_size, min_size - 1, -2):
        font = _load_font(size, bold=True)
        bbox = draw.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            return font, bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Fallback — return min size even if it overflows (caller should never hit this in practice)
    font = _load_font(min_size, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    return font, bbox[2] - bbox[0], bbox[3] - bbox[1]


def main() -> int:
    if not os.path.exists(BG_PATH):
        print(f"ERROR: {BG_PATH} missing. Generate via the AI prompt in this "
              f"file's docstring and save to that path.", file=sys.stderr)
        return 1
    if not os.path.exists(ICO_PATH):
        print(f"ERROR: {ICO_PATH} missing.", file=sys.stderr)
        return 1

    # Background
    bg = Image.open(BG_PATH).convert("RGBA").resize((W, H), Image.LANCZOS)

    # Bloom (under K-mark) + horizontal energy beam (under K-mark)
    bg = Image.alpha_composite(bg, _build_bloom_layer((W, H)))
    bg = Image.alpha_composite(bg, _build_beam_layer((W, H)))

    # K-mark on top of the energy effects
    ico = Image.open(ICO_PATH).convert("RGBA").resize((KMARK_SIZE, KMARK_SIZE), Image.LANCZOS)
    kmark_y = (H - KMARK_SIZE) // 2
    bg.paste(ico, (KMARK_X, kmark_y), ico)

    draw = ImageDraw.Draw(bg)

    # Right-column layout
    text_x = KMARK_X + KMARK_SIZE + 36
    right_margin = 28
    avail_width = W - text_x - right_margin

    # Kicker — tracked-out 'UNLOCKED' (PIL has no kerning/tracking API,
    # so we fake the tracking by interleaving spaces between the chars)
    kicker_text = "U N L O C K E D"
    kicker_y = 76
    draw.text((text_x, kicker_y), kicker_text,
              fill=NAVY_BRIGHT, font=_load_font(15, bold=True))

    # Headline — auto-fit POWER MODE to the right-column width
    headline = "POWER MODE"
    headline_font, headline_w, headline_h = _autofit_headline(
        draw, headline, max_width=avail_width
    )
    headline_y = kicker_y + 28
    draw.text((text_x, headline_y), headline, fill=WHITE, font=headline_font)

    # Status row — green operational dot + subtitle
    sub_y = headline_y + headline_h + 24
    dot_size = 11
    draw.ellipse(
        [text_x, sub_y + 7, text_x + dot_size, sub_y + 7 + dot_size],
        fill=GREEN,
    )
    draw.text((text_x + dot_size + 12, sub_y),
              "Hardware acceleration active",
              fill=DIM, font=_load_font(18))

    bg.convert("RGB").save(OUTPUT_PATH, format="BMP")
    print(f"Wrote {OUTPUT_PATH} ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
