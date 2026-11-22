#!/usr/bin/env python3
"""Draw entry.png: Sunday 22 November 2026 in one picture.

Deterministic. Pillow only. No network and no assets beyond a system TTF.
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
GUTTER = 14
RADIUS = 18
PAD_X = 15
ICON_D = 60

BG = (13, 27, 46)          # #0d1b2e
CARD = (24, 48, 78)        # slightly lighter navy
CARD_EDGE = (52, 86, 124)
INK = (244, 241, 234)
DECK = (206, 216, 226)
MUTED = (140, 158, 176)
GOLD = (227, 195, 122)
RULE = (46, 72, 104)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "entry.png"

STORIES = (
    {
        "tag": "CLIMATE",
        "accent": (61, 214, 186),
        "icon": "climate",
        "lines": ("COP31 talks", "stall in overtime"),
        "sub": "Antalya summit deadlocked over fossil-fuel phase-out",
    },
    {
        "tag": "CONFLICT",
        "accent": (255, 107, 120),
        "icon": "ship",
        "lines": ("Iran strikes", "site in Bahrain"),
        "sub": "Tankers hit in the Strait of Hormuz as tensions flare",
    },
    {
        "tag": "JUSTICE",
        "accent": (240, 196, 77),
        "icon": "badge",
        "lines": ("Mexico captures", "'El Chapo Isidro'"),
        "sub": "FBI most-wanted cartel boss seized in Sinaloa; 11 killed",
    },
    {
        "tag": "DIPLOMACY",
        "accent": (110, 176, 255),
        "icon": "diplomacy",
        "lines": ("Trump, Xi, Putin", "meet in Shenzhen"),
        "sub": "Leaders agree to start nuclear risk-reduction talks",
    },
    {
        "tag": "MARKETS",
        "accent": (192, 146, 255),
        "icon": "chart",
        "lines": ("AI sell-off", "sinks stocks"),
        "sub": "Dow and S&P 500 slide into correction territory",
    },
    {
        "tag": "WAR",
        "accent": (255, 148, 77),
        "icon": "bridge",
        "lines": ("Missile hits", "Zelensky's hometown"),
        "sub": "Kryvyi Rih strike kills two; Ukraine hits Crimean bridge",
    },
)

CANONICAL = (
    "COP31 talks stall in overtime",
    "Iran strikes site in Bahrain",
    "Mexico captures 'El Chapo Isidro'",
    "Trump, Xi, Putin meet in Shenzhen",
    "AI sell-off sinks stocks",
    "Missile hits Zelensky's hometown",
)


def find_ttf(filename):
    root = "/usr/share/fonts"
    if not os.path.isdir(root):
        return None
    matches = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name == filename:
                matches.append(os.path.join(dirpath, name))
    matches.sort()
    return matches[0] if matches else None


def any_ttf():
    root = "/usr/share/fonts"
    if not os.path.isdir(root):
        return None
    found = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(".ttf"):
                found.append(os.path.join(dirpath, name))
    found.sort()
    return found[0] if found else None


def load_font(path, size):
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def rgba(color, alpha=255):
    return (color[0], color[1], color[2], alpha)


def ink_box(x, y, text, font):
    box = font.getbbox(text, anchor="lt")
    return (x + box[0], y + box[1], x + box[2], y + box[3])


def assert_inside(box, bounds, label):
    if box[0] < bounds[0] - 0.5 or box[1] < bounds[1] - 0.5 or box[2] > bounds[2] + 0.5 or box[3] > bounds[3] + 0.5:
        raise SystemExit(f"Clipping: {label} {tuple(round(v, 1) for v in box)} outside {bounds}")


def draw_tracked(draw, text, y, font, fill, tracking, canvas_w):
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (canvas_w - total) / 2
    height = font.getbbox("Hg", anchor="lt")[3]
    for ch, width in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor="lt")
        x += width + tracking
    return height


def star_points(cx, cy, outer, inner, n, rotation=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        radius = outer if i % 2 == 0 else inner
        angle = rotation + i * math.pi / n
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts


def paint_icon(kind, accent, glyph):
    """Supersample a geometric icon so the disc edge and strokes stay smooth."""
    scale = 4
    diameter = ICON_D * scale
    image = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = scale * 2
    draw.ellipse(
        [margin, margin, diameter - 1 - margin, diameter - 1 - margin],
        fill=rgba(accent),
    )

    inset = 0.16
    lo = diameter * inset
    span = diameter * (1 - 2 * inset)

    def P(x, y):
        return (lo + span * (x / 100.0), lo + span * (y / 100.0))

    def R(x0, y0, x1, y1):
        a = P(x0, y0)
        b = P(x1, y1)
        return [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]

    def round_rect(box, radius, **kwargs):
        width = box[2] - box[0]
        height = box[3] - box[1]
        radius = max(1, min(radius, width / 2 - 2, height / 2 - 2))
        draw.rounded_rectangle(box, radius=radius, **kwargs)

    stroke = max(8, int(round(diameter * 0.052)))
    ink = rgba(glyph)
    hole = rgba(accent)

    if kind == "climate":
        draw.ellipse(R(30, 56, 70, 98), fill=ink)
        round_rect(R(41, 6, 59, 70), stroke, fill=ink)
        round_rect(R(46, 14, 54, 42), max(2, stroke // 3), fill=hole)
    elif kind == "ship":
        draw.polygon(
            [P(6, 58), P(94, 58), P(80, 84), P(20, 84)],
            fill=ink,
        )
        draw.rectangle(R(44, 36, 80, 58), fill=ink)
        draw.rectangle(R(56, 14, 72, 36), fill=ink)
        draw.rectangle(R(50, 42, 74, 50), fill=hole)
        draw.rectangle(R(24, 66, 76, 72), fill=hole)
    elif kind == "badge":
        shield = [P(*p) for p in ((50, 4), (90, 24), (82, 58), (50, 98), (18, 58), (10, 24))]
        draw.polygon(shield, fill=ink)
        star = [P(*p) for p in star_points(50, 46, 22, 9, 5)]
        draw.polygon(star, fill=hole)
    elif kind == "diplomacy":
        centers = ((28, 66), (72, 66), (50, 30))
        radius = 16
        for i, a in enumerate(centers):
            for b in centers[i + 1 :]:
                draw.line([P(*a), P(*b)], fill=ink, width=stroke)
        for cx, cy in centers:
            draw.ellipse(R(cx - radius, cy - radius, cx + radius, cy + radius), fill=ink)
            draw.ellipse(R(cx - 6, cy - 6, cx + 6, cy + 6), fill=hole)
    elif kind == "chart":
        draw.line([P(12, 14), P(12, 88), P(92, 88)], fill=ink, width=stroke, joint="curve")
        pts = ((14, 22), (40, 36), (62, 58), (86, 80))
        shortened = []
        for i, p in enumerate(pts):
            if i < len(pts) - 1:
                shortened.append(p)
            else:
                prev = pts[-2]
                shortened.append((prev[0] * 0.22 + p[0] * 0.78, prev[1] * 0.22 + p[1] * 0.78))
        draw.line([P(*p) for p in shortened], fill=ink, width=stroke + 4, joint="curve")
        x1, y1 = pts[-2]
        x2, y2 = pts[-1]
        ang = math.atan2(y2 - y1, x2 - x1)
        length = 18
        spread = 0.55
        tip = P(x2, y2)
        left = P(x2 - length * math.cos(ang - spread), y2 - length * math.sin(ang - spread))
        right = P(x2 - length * math.cos(ang + spread), y2 - length * math.sin(ang + spread))
        draw.polygon([tip, left, right], fill=ink)
    elif kind == "bridge":
        # Suspension bridge: thin towers, roadway, sagging cable, impact star.
        draw.rectangle(R(18, 6, 30, 92), fill=ink)
        draw.rectangle(R(70, 6, 82, 92), fill=ink)
        cable_w = max(6, stroke - 1)
        cable = []
        for i in range(21):
            t = i / 20
            x = 24 + (76 - 24) * t
            y = 10 + 46 * (4 * t * (1 - t))
            cable.append(P(x, y))
        draw.line(cable, fill=ink, width=cable_w, joint="curve")
        for hanger_x in (38, 50, 62):
            # Drop a short suspender from the cable down to the deck.
            t = (hanger_x - 24) / (76 - 24)
            y_top = 10 + 46 * (4 * t * (1 - t))
            draw.line([P(hanger_x, y_top), P(hanger_x, 60)], fill=ink, width=max(4, cable_w - 4))
        round_rect(R(6, 58, 94, 70), max(4, stroke // 2), fill=ink)
        burst = [P(*p) for p in star_points(90, 28, 12, 5, 8)]
        draw.polygon(burst, fill=ink)
    else:
        draw.ellipse(R(30, 30, 70, 70), outline=ink, width=stroke)

    return image.resize((ICON_D, ICON_D), Image.Resampling.LANCZOS)


def render():
    for story, headline in zip(STORIES, CANONICAL):
        joined = " ".join(story["lines"])
        if joined != headline:
            raise SystemExit(f"Headline drift: {joined!r} != {headline!r}")
        if len(story["lines"]) > 3:
            raise SystemExit(f"Too many lines: {headline}")

    bold_path = find_ttf("DejaVuSans-Bold.ttf") or any_ttf()
    regular_path = find_ttf("DejaVuSans.ttf") or bold_path or any_ttf()

    title_font = load_font(bold_path, 58)
    kicker_font = load_font(bold_path, 15)
    subtitle_font = load_font(regular_path, 20)
    tag_font = load_font(bold_path, 14)
    head_font = load_font(bold_path, 36)
    sub_font = load_font(regular_path, 16)
    footer_font = load_font(regular_path, 15)

    image = Image.new("RGBA", (W, H), rgba(BG))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, W, 5], fill=GOLD)

    column_left = MARGIN
    column_right = W - MARGIN

    y = 24
    kicker = "THE WORLD IN ONE PICTURE"
    kicker_h = draw_tracked(draw, kicker, y, kicker_font, GOLD, 2.4, W)
    y += kicker_h + 10
    ornament_w = 56
    draw.rounded_rectangle(
        [(W - ornament_w) / 2, y, (W + ornament_w) / 2, y + 3],
        radius=1,
        fill=GOLD,
    )
    y += 14

    title = "Sunday 22 November 2026"
    title_w = title_font.getlength(title)
    title_x = (W - title_w) / 2
    draw.text((title_x, y), title, font=title_font, fill=INK, anchor="lt")
    title_box = ink_box(title_x, y, title, title_font)
    assert_inside(title_box, (12, 0, W - 12, H), "title")
    y += (title_box[3] - y) + 8

    subtitle = "The day's six biggest stories"
    sub_w = subtitle_font.getlength(subtitle)
    sub_x = (W - sub_w) / 2
    draw.text((sub_x, y), subtitle, font=subtitle_font, fill=DECK, anchor="lt")
    subtitle_box = ink_box(sub_x, y, subtitle, subtitle_font)
    y = subtitle_box[3] + 14
    draw.line([(column_left, y), (column_right, y)], fill=RULE, width=1)
    grid_top = y + 16

    footer = "Sources: wire reports, 22 Nov 2026 · Drawn by an AI agent"
    footer_box_h = footer_font.getbbox(footer, anchor="lt")[3]
    footer_y = H - 18 - footer_box_h
    footer_rule = footer_y - 14
    grid_bottom = footer_rule - 14

    panel_w = (W - 2 * MARGIN - GUTTER) // 2
    avail = grid_bottom - grid_top
    panel_h = (avail - 2 * GUTTER) // 3
    if panel_h < 220:
        raise SystemExit(f"Panels too short: {panel_h}")

    head_h = head_font.getbbox("Hg", anchor="lt")[3]
    line_step = head_h + 7
    sub_h = sub_font.getbbox("Hg", anchor="lt")[3]
    block_h = ICON_D + 12 + line_step + head_h + 11 + sub_h
    pad_top = (panel_h - block_h) // 2
    if pad_top < 14:
        raise SystemExit(f"Not enough card padding: {pad_top}")

    text_w = panel_w - 2 * PAD_X
    icons = {id(story): paint_icon(story["icon"], story["accent"], INK) for story in STORIES}

    for index, story in enumerate(STORIES):
        col = index % 2
        row = index // 2
        x = MARGIN + col * (panel_w + GUTTER)
        card_y = grid_top + row * (panel_h + GUTTER)
        bounds = (x + 8, card_y + 8, x + panel_w - 8, card_y + panel_h - 8)

        draw.rounded_rectangle(
            [x, card_y + 3, x + panel_w, card_y + panel_h + 4],
            radius=RADIUS,
            fill=(7, 14, 26, 255),
        )
        draw.rounded_rectangle(
            [x, card_y, x + panel_w, card_y + panel_h],
            radius=RADIUS,
            fill=CARD,
            outline=CARD_EDGE,
            width=1,
        )
        # Accent rail on the straight part of the left edge.
        draw.rectangle(
            [x + 8, card_y + 20, x + 12, card_y + panel_h - 20],
            fill=story["accent"],
        )

        icon_x = x + panel_w - PAD_X - ICON_D
        icon_y = card_y + pad_top
        image.alpha_composite(icons[id(story)], (icon_x, icon_y))

        tag = story["tag"]
        tag_track = 0.8
        tag_widths = [tag_font.getlength(ch) for ch in tag]
        tag_text_w = sum(tag_widths) + tag_track * (len(tag) - 1)
        tag_box = tag_font.getbbox(tag, anchor="lt")
        tag_h = tag_box[3] - tag_box[1]
        pill_pad_x = 9
        pill_pad_y = 5
        pill_w = tag_text_w + pill_pad_x * 2
        pill_h = tag_h + pill_pad_y * 2
        pill_x = x + PAD_X + 6
        pill_y = icon_y + (ICON_D - pill_h) / 2
        pill_fill = mix(CARD, story["accent"], 0.22)
        draw.rounded_rectangle(
            [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
            radius=pill_h / 2,
            fill=pill_fill,
        )
        cursor = pill_x + pill_pad_x
        text_y = pill_y + pill_pad_y - tag_box[1]
        for ch, width in zip(tag, tag_widths):
            draw.text((cursor, text_y), ch, font=tag_font, fill=story["accent"], anchor="lt")
            cursor += width + tag_track
        assert_inside(
            (pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
            (x + 4, card_y + 4, icon_x - 8, card_y + panel_h - 4),
            story["tag"] + " pill",
        )

        text_x = x + PAD_X
        head_y = icon_y + ICON_D + 12
        for line_i, line in enumerate(story["lines"]):
            ly = head_y + line_i * line_step
            if head_font.getlength(line) > text_w:
                raise SystemExit(f"Headline too wide: {line}")
            draw.text((text_x, ly), line, font=head_font, fill=INK, anchor="lt")
            assert_inside(ink_box(text_x, ly, line, head_font), bounds, line)

        sub_y = head_y + line_step + head_h + 11
        if sub_font.getlength(story["sub"]) > text_w:
            raise SystemExit(f"Sub too wide: {story['sub']}")
        draw.text((text_x, sub_y), story["sub"], font=sub_font, fill=DECK, anchor="lt")
        assert_inside(ink_box(text_x, sub_y, story["sub"], sub_font), bounds, story["sub"])

    draw.line([(column_left, footer_rule), (column_right, footer_rule)], fill=RULE, width=1)
    footer_w = footer_font.getlength(footer)
    footer_x = (W - footer_w) / 2
    draw.text((footer_x, footer_y), footer, font=footer_font, fill=MUTED, anchor="lt")
    assert_inside(ink_box(footer_x, footer_y, footer, footer_font), (8, footer_rule + 2, W - 8, H - 8), "footer")

    return image.convert("RGB")


def main():
    image = render()
    if image.size != (W, H):
        raise SystemExit(f"Unexpected size {image.size}")
    image.save(OUT, "PNG", optimize=True, compress_level=9)
    size = OUT.stat().st_size
    print(f"wrote {OUT.name} {image.size[0]}x{image.size[1]} {size} bytes")
    if size >= 1048576:
        raise SystemExit("PNG is over 1 MiB")


if __name__ == "__main__":
    main()
