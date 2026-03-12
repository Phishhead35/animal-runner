#!/usr/bin/env python3
"""
Animal Runner - Screenshot Generator
Generates promotional screenshots (960x540 PNG) for distribution platforms.
Requires: pip install Pillow
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import random


OUTPUT_DIR = Path(__file__).parent / "screenshots"
W, H = 960, 540

# ── Biome color palettes ──────────────────────────────────────────────────────
BIOMES = {
    "grasslands": {
        "sky_top": (170, 225, 255),
        "sky_bot": (140, 200, 240),
        "ground":  (115, 214, 120),
        "ground_dark": (80, 185, 90),
        "label": "Grasslands Biome",
    },
    "desert": {
        "sky_top": (255, 200, 100),
        "sky_bot": (240, 160, 60),
        "ground":  (212, 168, 90),
        "ground_dark": (184, 136, 58),
        "label": "Desert Biome",
    },
    "night_desert": {
        "sky_top": (20, 10, 55),
        "sky_bot": (40, 20, 80),
        "ground":  (138, 106, 58),
        "ground_dark": (90, 64, 32),
        "label": "Night Desert Biome",
    },
    "storm": {
        "sky_top": (25, 25, 35),
        "sky_bot": (15, 15, 25),
        "ground":  (58, 58, 74),
        "ground_dark": (34, 34, 46),
        "label": "Storm Biome",
    },
    "arctic": {
        "sky_top": (200, 230, 255),
        "sky_bot": (170, 210, 245),
        "ground":  (221, 238, 255),
        "ground_dark": (168, 204, 238),
        "label": "Arctic Biome",
    },
    "underwater": {
        "sky_top": (10, 60, 120),
        "sky_bot": (5, 40, 90),
        "ground":  (26, 74, 106),
        "ground_dark": (13, 42, 64),
        "label": "Underwater Biome",
    },
}

GROUND_Y = 420
INK = (35, 35, 35)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_sky_gradient(img, sky_top, sky_bot):
    """Draw a vertical sky gradient."""
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = lerp_color(sky_top, sky_bot, t)
        draw.line([(0, y), (W, y)], fill=color)


def draw_ground(draw, ground, ground_dark):
    """Draw ground strip."""
    draw.rectangle([0, GROUND_Y, W, H], fill=ground)
    draw.rectangle([0, GROUND_Y, W, GROUND_Y + 8], fill=ground_dark)


def draw_clouds(draw, sky_top, count=5):
    """Draw simple cloud shapes."""
    cloud_color = tuple(min(255, c + 80) for c in sky_top) + (200,)
    random.seed(42)
    for i in range(count):
        cx = random.randint(80, W - 80)
        cy = random.randint(40, 180)
        s = 0.8 + random.random() * 0.7
        for ox, oy, rx, ry in [(60, 55, 60, 30), (120, 40, 70, 35), (180, 58, 55, 28)]:
            x, y = cx + ox * s - 150, cy + oy * s - 60
            draw.ellipse([x - rx * s, y - ry * s, x + rx * s, y + ry * s],
                         fill=cloud_color[:3])


def draw_frog(draw, px, py, pw, ph, body=(80, 210, 110), belly=(210, 255, 217)):
    """Draw simplified frog character."""
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=16,
                           fill=body, outline=INK, width=3)
    bx, by = px + pw // 2, py + int(ph * 0.70)
    draw.ellipse([bx - pw // 3, by - ph // 5, bx + pw // 3, by + ph // 5],
                 fill=belly, outline=INK, width=2)
    for ex in [-1, 1]:
        ox, oy = px + pw // 2 + ex * pw // 5, py - ph // 14
        draw.ellipse([ox - 10, oy - 10, ox + 10, oy + 10],
                     fill=(120, 235, 145), outline=INK, width=2)
        draw.ellipse([ox - 5, oy - 5, ox + 5, oy + 5], fill="white")
        draw.ellipse([ox - 2, oy - 2, ox + 2, oy + 2], fill=INK)


def draw_title_card(img, title, subtitle=None, badge=None):
    """Draw a semi-transparent info card over the image."""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Card background
    card_w, card_h = 560, 110 if subtitle else 80
    cx, cy = W // 2, H - 80
    d.rounded_rectangle(
        [cx - card_w // 2, cy - card_h // 2, cx + card_w // 2, cy + card_h // 2],
        radius=14,
        fill=(255, 255, 255, 210),
        outline=INK + (230,),
        width=3,
    )

    # Try to use a system font, fall back to default
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
        font_sub   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except Exception:
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
            font_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except Exception:
            font_title = ImageFont.load_default()
            font_sub   = font_title

    # Title text
    bbox = d.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    d.text((cx - tw // 2, cy - card_h // 2 + 14), title, font=font_title, fill=INK)

    if subtitle:
        sbbox = d.textbbox((0, 0), subtitle, font=font_sub)
        sw = sbbox[2] - sbbox[0]
        d.text((cx - sw // 2, cy - card_h // 2 + 52), subtitle,
               font=font_sub, fill=(80, 80, 80))

    if badge:
        bd = d.textbbox((0, 0), badge, font=font_sub)
        bw = bd[2] - bd[0] + 24
        bx1 = W - bw - 20
        d.rounded_rectangle([bx1, 12, W - 12, 44], radius=8,
                             fill=(35, 35, 35, 200))
        d.text((bx1 + 12, 16), badge, font=font_sub, fill="white")

    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))


def screenshot_title():
    """Title/start screen screenshot."""
    biome = BIOMES["grasslands"]
    img = Image.new("RGB", (W, H))
    draw_sky_gradient(img, biome["sky_top"], biome["sky_bot"])
    draw = ImageDraw.Draw(img)
    draw_clouds(draw, biome["sky_top"])
    draw_ground(draw, biome["ground"], biome["ground_dark"])

    # Big title card
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([160, 130, 800, 380], radius=24, fill=(255, 255, 255, 220),
                        outline=INK + (230,), width=4)

    try:
        font_big  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 58)
        font_med  = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        font_sm   = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 17)
    except Exception:
        try:
            font_big  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
            font_med  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
            font_sm   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
        except Exception:
            font_big = font_med = font_sm = ImageFont.load_default()

    title = "Cartoon Animal Runner"
    tb = d.textbbox((0, 0), title, font=font_big)
    d.text(((W - (tb[2]-tb[0])) // 2, 160), title, font=font_big, fill=INK)

    for y_off, text in [(252, "12 Characters  •  48 Skins  •  6 Biomes"),
                         (284, "Endless Runner  •  Play in any browser"),
                         (320, "Hold Space to jump  •  Duck under birds  •  Collect coins")]:
        bb = d.textbbox((0, 0), text, font=font_med if y_off < 300 else font_sm)
        d.text(((W - (bb[2]-bb[0])) // 2, y_off), text, font=font_med if y_off < 300 else font_sm,
               fill=(80, 80, 80))

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Player frog
    draw_frog(draw, 440, GROUND_Y - 78, 56, 72)

    return img


def screenshot_biome(biome_key):
    """Generate a screenshot for a specific biome."""
    biome = BIOMES[biome_key]
    img = Image.new("RGB", (W, H))
    draw_sky_gradient(img, biome["sky_top"], biome["sky_bot"])
    draw = ImageDraw.Draw(img)
    draw_clouds(draw, biome["sky_top"])

    # Biome-specific extras
    if biome_key == "night_desert":
        # Moon
        draw.ellipse([786, 34, 858, 106], fill=(255, 250, 204))
        draw.ellipse([802, 28, 868, 94], fill=biome["sky_top"])

    if biome_key == "arctic":
        # Aurora strips
        for i, col in enumerate([(128, 255, 204, 55), (96, 221, 255, 45), (170, 136, 255, 40)]):
            y = 50 + i * 28
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rectangle([0, y, W, y + 50], fill=col)
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
            draw = ImageDraw.Draw(img)

    if biome_key == "storm":
        # Storm clouds
        for cx2, cy2, cw in [(160, 40, 220), (400, 20, 280), (680, 50, 200)]:
            for ox, oy, rx, ry in [(0, 0, cw*0.5, 38), (cw*0.22, -18, cw*0.35, 30)]:
                draw.ellipse([cx2+ox-rx, cy2+oy-ry, cx2+ox+rx, cy2+oy+ry],
                             fill=(40, 40, 55))

    if biome_key == "underwater":
        # Seaweed
        for sx in range(0, W, 60):
            draw.arc([sx - 10, GROUND_Y - 40, sx + 22, GROUND_Y + 4], -90, 90,
                     fill=(40, 180, 120), width=3)

    draw_ground(draw, biome["ground"], biome["ground_dark"])

    # Simple obstacles
    if biome_key in ("grasslands", "desert"):
        # Cactus
        cx3, cy3 = 700, GROUND_Y - 65
        draw.rounded_rectangle([cx3, cy3, cx3 + 38, GROUND_Y], radius=6,
                               fill=(58, 138, 58), outline=INK, width=2)
        draw.rounded_rectangle([cx3 - 22, cy3 + 22, cx3 + 6, cy3 + 40], radius=5,
                               fill=(58, 138, 58), outline=INK, width=2)

    # Player frog
    draw_frog(draw, 160, GROUND_Y - 78, 56, 72)

    # Score HUD pill
    pill_text = f"Score: 1,240  •  {biome['label']}"
    overlay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(overlay2)
    try:
        fpill = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except Exception:
        try:
            fpill = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        except Exception:
            fpill = ImageFont.load_default()
    pb = d2.textbbox((0, 0), pill_text, font=fpill)
    pw2 = pb[2] - pb[0] + 20
    d2.rounded_rectangle([8, 8, 8 + pw2, 34], radius=999, fill=(255, 255, 255, 200),
                          outline=INK + (180,), width=1)
    d2.text((18, 12), pill_text, font=fpill, fill=INK)
    img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")

    return img


def screenshot_shop():
    """Shop screen screenshot."""
    biome = BIOMES["grasslands"]
    img = Image.new("RGB", (W, H))
    draw_sky_gradient(img, biome["sky_top"], biome["sky_bot"])
    draw = ImageDraw.Draw(img)
    draw_clouds(draw, biome["sky_top"])

    # Panel
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([36, 44, W - 36, H - 44], radius=20,
                        fill=(255, 255, 255, 238), outline=INK + (230,), width=3)

    try:
        font_h = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
        font_r = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 19)
        font_s = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    except Exception:
        try:
            font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
            font_r = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
            font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        except Exception:
            font_h = font_r = font_s = ImageFont.load_default()

    d.text((80, 60), "SHOP", font=font_h, fill=INK)
    d.text((80, 116), "💰 350 coins   🏆 Best: 4,280", font=font_r, fill=(80, 80, 80))

    chars = [
        ("Frog 🐸",      "free",     True,  (80, 210, 110)),
        ("Dog 🐶",       "30 coins", False, (212, 145, 90)),
        ("Cat 🐱",       "30 coins", False, (240, 131, 74)),
        ("Monkey 🐒",    "30 coins", False, (139, 94, 60)),
        ("Capybara 🐾",  "50 coins", False, (181, 133, 74)),
    ]

    start_y = 170
    for i, (name, cost, equipped, color) in enumerate(chars):
        y = start_y + i * 54
        bg = (50, 210, 90, 33) if equipped else (35, 35, 35, 18) if i == 0 else (0, 0, 0, 8)
        d.rounded_rectangle([80, y - 6, W - 80, y + 46], radius=12, fill=bg,
                            outline=((48, 176, 96) + (255,) if equipped else INK + (80,)),
                            width=2)

        # Color swatch
        d.ellipse([100, y + 8, 136, y + 40], fill=color, outline=INK, width=2)

        badge = " ✓ PLAYING" if equipped else f"  — {cost}"
        d.text((148, y + 8), ("▶ " if i == 0 else "   ") + name + badge,
               font=font_r, fill=INK)
        d.text((152, y + 30), "Skin: Green (default)" if equipped else "", font=font_s,
               fill=(120, 120, 120))

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def screenshot_powerups():
    """In-game power-ups screenshot."""
    biome = BIOMES["grasslands"]
    img = Image.new("RGB", (W, H))
    draw_sky_gradient(img, biome["sky_top"], biome["sky_bot"])
    draw = ImageDraw.Draw(img)
    draw_clouds(draw, biome["sky_top"])
    draw_ground(draw, biome["ground"], biome["ground_dark"])

    # Player with shield bubble
    draw_frog(draw, 160, GROUND_Y - 78, 56, 72)
    cx_p, cy_p = 160 + 28, GROUND_Y - 42
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse([cx_p - 46, cy_p - 46, cx_p + 46, cy_p + 46],
              fill=(120, 190, 255, 90), outline=(60, 120, 220, 200), width=3)

    # Orbs on screen
    orbs = [
        (340, 320, (120, 190, 255), "Shield", "10 coins"),
        (480, 290, (255, 90, 90),   "Magnet", "12 coins"),
        (620, 310, (175, 120, 255), "Double", "12 coins"),
    ]
    for ox, oy, col, label, cost in orbs:
        glow = col + (80,)
        d.ellipse([ox - 28, oy - 28, ox + 28, oy + 28], fill=glow)
        d.ellipse([ox - 14, oy - 14, ox + 14, oy + 14], fill=col + (255,),
                  outline=INK + (220,), width=2)

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Labels
    try:
        font_lbl = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except Exception:
        try:
            font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except Exception:
            font_lbl = ImageFont.load_default()

    for ox, oy, col, label, cost in orbs:
        bb = draw.textbbox((0, 0), label, font=font_lbl)
        tw = bb[2] - bb[0]
        draw.text((ox - tw // 2, oy + 20), label, font=font_lbl, fill=INK)

    draw_title_card(img, "Collect Power-Up Orbs",
                   "Shield • Magnet • Score Doubler",
                   badge="v2.0")
    return img


SCREENSHOTS = [
    ("01_title.png",      screenshot_title,                    None),
    ("02_grasslands.png", screenshot_biome,                    "grasslands"),
    ("03_night.png",      screenshot_biome,                    "night_desert"),
    ("04_storm.png",      screenshot_biome,                    "storm"),
    ("05_arctic.png",     screenshot_biome,                    "arctic"),
    ("06_underwater.png", screenshot_biome,                    "underwater"),
    ("07_shop.png",       screenshot_shop,                     None),
    ("08_powerups.png",   screenshot_powerups,                 None),
]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"🐸 Animal Runner Screenshot Generator")
    print(f"Output: {OUTPUT_DIR.resolve()}\n")

    for fname, fn, arg in SCREENSHOTS:
        out_path = OUTPUT_DIR / fname
        print(f"  Generating {fname}...", end=" ", flush=True)
        img = fn(arg) if arg else fn()
        img.save(out_path)
        print(f"✓  ({img.size[0]}×{img.size[1]})")

    print(f"\n✅ {len(SCREENSHOTS)} screenshots saved to '{OUTPUT_DIR.name}/'")


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("ERROR: Pillow is required.")
        print("Install it with:  pip install Pillow")
