# installer/build_power_banner.py
"""
Composites the existing koda.ico K-mark onto the AI-generated Atlas Navy
background and writes installer/power_banner.bmp for the Inno Setup
Power Mode wizard page.

Usage:
    venv/Scripts/python installer/build_power_banner.py

Re-run after replacing power_banner_bg.png. Output (power_banner.bmp) is
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

from PIL import Image

INSTALLER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(INSTALLER_DIR)

BG_PATH = os.path.join(INSTALLER_DIR, "power_banner_bg.png")
ICO_PATH = os.path.join(PROJECT_ROOT, "koda.ico")
OUTPUT_PATH = os.path.join(INSTALLER_DIR, "power_banner.bmp")

TARGET_WIDTH = 600
TARGET_HEIGHT = 300
KMARK_SIZE = 96


def main() -> int:
    if not os.path.exists(BG_PATH):
        print(
            f"ERROR: {BG_PATH} missing. Generate via the AI prompt in this "
            f"file's docstring and save to that path.",
            file=sys.stderr,
        )
        return 1
    if not os.path.exists(ICO_PATH):
        print(f"ERROR: {ICO_PATH} missing.", file=sys.stderr)
        return 1

    bg = Image.open(BG_PATH).convert("RGBA")
    bg = bg.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    ico = Image.open(ICO_PATH).convert("RGBA")
    ico = ico.resize((KMARK_SIZE, KMARK_SIZE), Image.LANCZOS)

    x = (TARGET_WIDTH - ico.size[0]) // 2
    y = (TARGET_HEIGHT - ico.size[1]) // 2

    composite = bg.copy()
    composite.paste(ico, (x, y), ico)
    composite.convert("RGB").save(OUTPUT_PATH, format="BMP")

    print(f"Wrote {OUTPUT_PATH} ({TARGET_WIDTH}x{TARGET_HEIGHT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
