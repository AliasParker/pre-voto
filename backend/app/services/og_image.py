"""
OG card image generation using Pillow.

Generates 1200×630 PNG images for social media sharing (Twitter, WhatsApp,
Facebook, Telegram). Design follows the pre.voto design system (SPEC §5.1).
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Design tokens (SPEC §5.1)
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1200, 630

COLOR_PAPER = "#fafafa"
COLOR_INK = "#1a1a1a"
COLOR_INK_SOFT = "#404040"
COLOR_INK_FAINT = "#737373"
COLOR_BRAND = "#D85A30"

# ---------------------------------------------------------------------------
# Font paths
# ---------------------------------------------------------------------------
_FONTS_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"
_INTER_REGULAR = _FONTS_DIR / "Inter-Regular.ttf"
_INTER_BOLD = _FONTS_DIR / "Inter-Bold.ttf"


def _load_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    path = _INTER_BOLD if bold else _INTER_REGULAR
    return ImageFont.truetype(str(path), size)


def generate_og_image(
    candidate_name: str,
    party: str | None,
    pct: int,
    election_label: str,
) -> bytes:
    """
    Generate a 1200×630 OG card PNG.

    Layout:
    - Top-left: coral dot + "pre.voto" wordmark
    - Center: "Mi afinidad" / large percentage / candidate name / party
    - Bottom-center: election label line

    Args:
        candidate_name: Full display name of the top-match candidate.
        party: Party name (shown in parentheses). None to omit.
        pct: Affinity percentage (0–100), rendered as integer.
        election_label: Bottom line text, e.g. "pre.voto · Colombia 2026".

    Returns:
        PNG image as bytes.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_PAPER)
    draw = ImageDraw.Draw(img)

    # -- Fonts --
    font_logo = _load_font(bold=True, size=28)
    font_label = _load_font(bold=False, size=24)
    font_pct = _load_font(bold=True, size=120)
    font_name = _load_font(bold=True, size=36)
    font_party = _load_font(bold=False, size=22)
    font_bottom = _load_font(bold=False, size=18)

    cx = WIDTH // 2  # horizontal center

    # -- Logo (top-left): coral dot + "pre.voto" --
    dot_radius = 8
    dot_x, dot_y = 48, 44
    draw.ellipse(
        [dot_x - dot_radius, dot_y - dot_radius,
         dot_x + dot_radius, dot_y + dot_radius],
        fill=COLOR_BRAND,
    )
    draw.text((dot_x + 16, dot_y), "pre.voto", fill=COLOR_INK, font=font_logo, anchor="lm")

    # -- "Mi afinidad" label --
    y_label = 195
    draw.text((cx, y_label), "Mi afinidad", fill=COLOR_INK_SOFT, font=font_label, anchor="mm")

    # -- Large percentage --
    y_pct = 290
    draw.text((cx, y_pct), f"{pct}%", fill=COLOR_BRAND, font=font_pct, anchor="mm")

    # -- "con {Candidate Name}" --
    y_name = 385
    draw.text((cx, y_name), f"con {candidate_name}", fill=COLOR_INK, font=font_name, anchor="mm")

    # -- "(Party)" --
    if party:
        y_party = 425
        draw.text((cx, y_party), f"({party})", fill=COLOR_INK_SOFT, font=font_party, anchor="mm")

    # -- Bottom line: election label --
    y_bottom = HEIGHT - 40
    draw.text((cx, y_bottom), election_label, fill=COLOR_INK_FAINT, font=font_bottom, anchor="mm")

    # -- Encode as PNG --
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
