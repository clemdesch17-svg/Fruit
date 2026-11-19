"""Dessin des personnages fruits, décors, overlays et textes (pycairo).

Repère : image 1080x1920. Un personnage est dessiné dans un repère local
dont l'origine est entre ses pieds, y vers le haut négatif, hauteur ~420
unités à l'échelle 1.
"""
import math
import random
import cairo

W, H = 1080, 1920
FONT = "DejaVu Sans"


# ---------------------------------------------------------------- utilitaires
def hexc(h, a=1.0):
    h = h.lstrip("#")
    if len(h) == 8:
        a = a * int(h[6:8], 16) / 255
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def setc(ctx, c, a=None):
    r, g, b, aa = hexc(c) if isinstance(c, str) else (*c[:3], c[3] if len(c) > 3 else 1)
    ctx.set_source_rgba(r, g, b, aa if a is None else a)


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def radial(cx, cy, r, c0, c1, fx=None, fy=None):
    g = cairo.RadialGradient(fx if fx is not None else cx, fy if fy is not None else cy, 0, cx, cy, r)
    g.add_color_stop_rgba(0, *hexc(c0))
    g.add_color_stop_rgba(1, *hexc(c1))
    return g


def linear(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for off, c in stops:
        g.add_color_stop_rgba(off, *(hexc(c) if isinstance(c, str) else c))
    return g


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def heart(ctx, x, y, s):
    ctx.move_to(x, y + s * 0.35)
    ctx.curve_to(x - s * 1.1, y - s * 0.4, x - s * 0.45, y - s * 1.1, x, y - s * 0.45)
    ctx.curve_to(x + s * 0.45, y - s * 1.1, x + s * 1.1, y - s * 0.4, x, y + s * 0.35)
    ctx.close_path()


# ---------------------------------------------------------------- texte
def wrap(ctx, text, size, maxw, bold=True):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    lines, cur = [], ""
    text = text.replace(" ?", "\u00a0?").replace(" !", "\u00a0!").replace(" :", "\u00a0:")
    for word in text.split(" "):
        test = (cur + " " + word).strip()
        if ctx.text_extents(test).x_advance > maxw and cur:
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def outlined_text(ctx, text, cx, y, size, fill="#FFFFFF", stroke="#000000", sw=10, maxw=920):
    lines = wrap(ctx, text, size, maxw)
    lh = size * 1.18
    for i, ln in enumerate(lines):
        ext = ctx.text_extents(ln)
        x = cx - ext.x_advance / 2
        yy = y + i * lh
        ctx.move_to(x, yy)
        ctx.text_path(ln)
        setc(ctx, stroke)
        ctx.set_line_width(sw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
        setc(ctx, fill)
        ctx.fill()
    return len(lines) * lh


def boxed_text(ctx, text, cx, y, size, bg="#FFFFFF", fg="#000000", maxw=860, alpha=1.0):
    lines = wrap(ctx, text, size, maxw)
    lh = size * 1.25
    widths = [ctx.text_extents(l).x_advance for l in lines]
    bw = max(widths) + 56
    bh = len(lines) * lh + 30
    rrect(ctx, cx - bw / 2, y - size - 12, bw, bh, 22)
    setc(ctx, bg, alpha)
    ctx.fill()
    for i, ln in enumerate(lines):
        ctx.move_to(cx - widths[i] / 2, y + i * lh)
        setc(ctx, fg, alpha)
        ctx.show_text(ln)
    return bh


# ---------------------------------------------------------------- visage
EXPR_BROWS = {  # (décalage intérieur, extérieur) ; négatif = vers le haut
    "neutral": (0, 0), "happy": (-6, -4), "sad": (-14, 6), "angry": (12, -8),
    "shocked": (-16, -12), "cold": (6, -2), "scared": (-14, 2), "smug": (4, -6),
}


def draw_face(ctx, fx, fy, fs, st, expr, mouth, blink, t, look=(0, 0)):
    ctx.save()
    ctx.translate(fx, fy)
    ctx.scale(fs, fs)
    big = 1.18 if expr in ("shocked", "scared") else 1.0
    lx, ly = look
    # joues
    for sx in (-1, 1):
        ellipse(ctx, sx * 62, 34, 20, 11)
        setc(ctx, "#FF6F91", 0.35 if expr != "angry" else 0.5)
        ctx.fill()
    for sx in (-1, 1):
        ex = sx * 40
        rx, ry = 24 * big, 29 * big
        if blink:
            ctx.move_to(ex - rx, 0)
            ctx.curve_to(ex - rx / 2, 9, ex + rx / 2, 9, ex + rx, 0)
            setc(ctx, "#2B1B12")
            ctx.set_line_width(4.5)
            ctx.stroke()
        else:
            ellipse(ctx, ex, 0, rx, ry)
            setc(ctx, "#FFFFFF")
            ctx.fill_preserve()
            setc(ctx, "#2B1B12")
            ctx.set_line_width(3)
            ctx.stroke()
            ir = 16 if expr not in ("shocked", "scared") else 12
            ix, iy = ex + lx * 7, 3 + ly * 7
            ctx.arc(ix, iy, ir, 0, 2 * math.pi)
            setc(ctx, st.get("iris", "#5D3A1A"))
            ctx.fill()
            ctx.arc(ix, iy, ir * 0.5, 0, 2 * math.pi)
            setc(ctx, "#0E0805")
            ctx.fill()
            ctx.arc(ix - 5, iy - 6, 4.5, 0, 2 * math.pi)
            ctx.arc(ix + 5, iy + 5, 2, 0, 2 * math.pi)
            setc(ctx, "#FFFFFF")
            ctx.fill()
            # paupières (froid / colère)
            lid = {"cold": 0.55, "angry": 0.35, "smug": 0.45}.get(expr, 0)
            if lid:
                ctx.save()
                ellipse(ctx, ex, 0, rx + 1, ry + 1)
                ctx.clip()
                tilt = 10 * sx if expr == "angry" else 0
                ctx.move_to(ex - rx - 2, -ry - 2)
                ctx.line_to(ex + rx + 2, -ry - 2)
                ctx.line_to(ex + rx + 2, -ry + 2 * ry * lid - tilt)
                ctx.line_to(ex - rx - 2, -ry + 2 * ry * lid + tilt)
                ctx.close_path()
                setc(ctx, st["skin"])
                ctx.fill()
                ctx.restore()
            if st.get("lashes"):
                setc(ctx, "#1A0F08")
                ctx.set_line_width(3.5)
                for k in (-1, 0, 1):
                    ax = ex + sx * (rx * 0.55) + k * 8 * sx
                    ctx.move_to(ax, -ry + 4 + abs(k) * 2)
                    ctx.line_to(ax + sx * 8, -ry - 8)
                    ctx.stroke()
        # sourcils
        bi, bo = EXPR_BROWS.get(expr, (0, 0))
        inner, outer = ex - sx * 18, ex + sx * 22
        ctx.move_to(inner, -46 + bi)
        ctx.line_to(outer, -46 + bo)
        setc(ctx, st.get("brow", "#3A2414"))
        ctx.set_line_width(7)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    # larmes
    if expr == "sad":
        for sx in (-1, 1):
            ph = (t * 0.9 + (0.5 if sx > 0 else 0)) % 1.0
            ty = 28 + ph * 70
            ctx.move_to(sx * 46, ty - 10)
            ctx.curve_to(sx * 46 - 7, ty + 2, sx * 46 - 6, ty + 10, sx * 46, ty + 10)
            ctx.curve_to(sx * 46 + 6, ty + 10, sx * 46 + 7, ty + 2, sx * 46, ty - 10)
            setc(ctx, "#6EC6FF", 0.85 * (1 - ph * 0.6))
            ctx.fill()
    if expr == "scared":
        ctx.move_to(78, -40)
        ctx.curve_to(70, -22, 72, -10, 80, -10)
        ctx.curve_to(88, -10, 90, -22, 78, -40)
        setc(ctx, "#8FD3FF", 0.9)
        ctx.fill()
    # bouche
    my = 55
    lip = st.get("lips", "#3A1010")
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mouth > 0.05:
        h = 6 + 30 * mouth
        ellipse(ctx, 0, my + h / 3, 20 + 6 * mouth, h / 2 + 3)
        setc(ctx, "#4A0F14")
        ctx.fill_preserve()
        setc(ctx, lip)
        ctx.set_line_width(4)
        ctx.stroke()
        ellipse(ctx, 0, my + h / 2 + 2, 11, 5 * mouth + 1)
        setc(ctx, "#FF7B8A")
        ctx.fill()
    elif expr in ("shocked", "scared"):
        ellipse(ctx, 0, my + 6, 15, 20)
        setc(ctx, "#4A0F14")
        ctx.fill_preserve()
        setc(ctx, lip)
        ctx.set_line_width(4)
        ctx.stroke()
    else:
        setc(ctx, lip)
        ctx.set_line_width(6)
        if expr == "happy":
            ctx.move_to(-28, my - 4)
            ctx.curve_to(-14, my + 22, 14, my + 22, 28, my - 4)
        elif expr == "sad":
            ctx.move_to(-22, my + 12)
            ctx.curve_to(-10, my - 2, 10, my - 2, 22, my + 12)
        elif expr == "angry":
            ctx.move_to(-24, my + 6)
            ctx.curve_to(-10, my, 10, my, 24, my + 6)
        elif expr in ("cold", "smug"):
            ctx.move_to(-22, my + 4)
            ctx.curve_to(-6, my + 8, 12, my + 4, 26, my - 8)
        else:
            ctx.move_to(-18, my)
            ctx.curve_to(-8, my + 9, 8, my + 9, 18, my)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- membres
def limbs(ctx, c, arm_l, arm_r, leg_l, leg_r, pose, t, walk, prop=None, part="legs"):
    col = c.get("limb", "#3B2A1A")
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    sw = math.sin(t * 2 * math.pi * 1.6) if walk else 0
    for (hx, hy), side in (((leg_l, -1), (leg_r, 1)) if part == "legs" else ()):
        fx = hx + side * 10 + sw * 26 * side
        ctx.move_to(hx, hy)
        ctx.line_to(fx, -14)
        setc(ctx, col)
        ctx.set_line_width(13)
        ctx.stroke()
        ellipse(ctx, fx + side * 8, -8, 24, 12)
        setc(ctx, c.get("shoe", "#2A2A2A"))
        ctx.fill()
    if part == "legs":
        return
    sway = math.sin(t * 2 * math.pi * 0.5) * 5
    hands = []
    for (sx, sy), side in ((arm_l, -1), (arm_r, 1)):
        if pose == "up":
            hx, hy, ex, ey = sx + side * 70, sy - 120, sx + side * 55, sy - 40
        elif pose == "cover" and side == 1:
            hx, hy, ex, ey = c["face"][0] + 10, c["face"][1] + 55, sx + 45, sy + 30
        elif pose == "phone" and side == 1:
            hx, hy, ex, ey = sx + 30, sy - 70, sx + 55, sy + 20
        elif pose == "point" and side == 1:
            hx, hy, ex, ey = sx + 120, sy - 30, sx + 60, sy - 10
        elif pose == "hug":
            hx, hy, ex, ey = sx + side * 85, sy + 10, sx + side * 60, sy + 15
        else:
            sws = -sw * 20 * side if walk else 0
            hx, hy, ex, ey = sx + side * 40 + sws, sy + 95 + sway * side, sx + side * 30, sy + 50
        ctx.move_to(sx, sy)
        ctx.curve_to(ex, ey, ex, ey, hx, hy)
        setc(ctx, col)
        ctx.set_line_width(11)
        ctx.stroke()
        ctx.arc(hx, hy, 14, 0, 2 * math.pi)
        setc(ctx, "#FFFFFF")
        ctx.fill_preserve()
        setc(ctx, col)
        ctx.set_line_width(3)
        ctx.stroke()
        hands.append((hx, hy))
    if prop == "phone":
        hx, hy = hands[1]
        ctx.save()
        ctx.translate(hx, hy - 20)
        ctx.rotate(-0.25)
        rrect(ctx, -26, -48, 52, 96, 10)
        setc(ctx, "#111111")
        ctx.fill()
        rrect(ctx, -21, -42, 42, 84, 6)
        setc(ctx, "#9FD8FF")
        ctx.fill()
        ctx.restore()
    if prop == "badge":
        hx, hy = hands[1]
        ctx.save()
        ctx.translate(hx + 10, hy - 30)
        rrect(ctx, -30, -40, 60, 75, 10)
        setc(ctx, "#1C2A4A")
        ctx.fill()
        ctx.move_to(0, -28)
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 22 if i % 2 == 0 else 10
            ctx.line_to(math.cos(a) * r, math.sin(a) * r - 4)
        ctx.close_path()
        setc(ctx, "#FFD54F")
        ctx.fill()
        ctx.restore()


# ---------------------------------------------------------------- personnages
def body_banana(ctx, c):
    pts_l, pts_r = [], []
    for i in range(41):
        u = i / 40
        cx = 62 * math.sin(math.pi * u)
        y = -60 - 360 * u
        w = 80 * max(math.sin(math.pi * u), 0) ** 0.55 + 4
        pts_l.append((cx - w, y))
        pts_r.append((cx + w, y))
    ctx.move_to(*pts_l[0])
    for p in pts_l[1:]:
        ctx.line_to(*p)
    for p in reversed(pts_r):
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source(linear(-80, 0, 150, 0, [(0, "#F6C514"), (0.45, "#FFE45C"), (1, "#E0A800")]))
    ctx.fill_preserve()
    setc(ctx, "#B07A00")
    ctx.set_line_width(4)
    ctx.stroke()
    # arête
    ctx.move_to(pts_l[6][0] + 40, pts_l[6][1])
    for i in range(6, 36, 3):
        ctx.line_to(pts_l[i][0] + 40 + 6 * math.sin(math.pi * i / 40), pts_l[i][1])
    setc(ctx, "#D9A400", 0.6)
    ctx.set_line_width(4)
    ctx.stroke()
    # tige + bout
    rrect(ctx, -4, -455, 16, 42, 5)
    setc(ctx, "#6B4A1E")
    ctx.fill()
    ellipse(ctx, 0, -60, 9, 7)
    setc(ctx, "#4A3010")
    ctx.fill()
    # boucles d'oreilles
    for sx in (-1, 1):
        ctx.arc(62 + sx * 82, -230, 13, 0, 2 * math.pi)
        setc(ctx, "#FFC72C")
        ctx.set_line_width(5)
        ctx.stroke()


def body_kiwi(ctx, c):
    ellipse(ctx, 0, -215, 152, 165)
    ctx.set_source(radial(-40, -260, 200, "#9A7246", "#5C3D1E"))
    ctx.fill()
    rnd = random.Random(7)
    setc(ctx, "#7A5530", 0.8)
    ctx.set_line_width(2.5)
    for _ in range(140):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(0.93, 1.02)
        x, y = math.cos(a) * 152 * r, -215 + math.sin(a) * 165 * r
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(a) * 9, y + math.sin(a) * 9)
        ctx.stroke()
    ellipse(ctx, 0, -210, 124, 134)
    ctx.set_source(radial(0, -210, 134, "#D7EFA0", "#6FAE2E"))
    ctx.fill()
    ellipse(ctx, 0, -210, 12, 20)
    setc(ctx, "#F4F7DD", 0.8)
    ctx.fill()
    for i in range(26):
        a = i / 26 * 2 * math.pi
        ellipse(ctx, math.cos(a) * 104, -210 + math.sin(a) * 112, 3.5, 6)
        setc(ctx, "#1A1A10")
        ctx.fill()
    # casquette à l'envers
    ctx.save()
    ctx.move_to(-118, -322)
    ctx.curve_to(-110, -420, 110, -420, 118, -322)
    ctx.close_path()
    setc(ctx, "#151515")
    ctx.fill()
    ellipse(ctx, -150, -330, 62, 15)
    setc(ctx, "#222222")
    ctx.fill()
    ctx.arc(0, -393, 9, 0, 2 * math.pi)
    setc(ctx, "#333333")
    ctx.fill()
    ctx.restore()


def body_strawberry(ctx, c):
    ctx.move_to(0, -50)
    ctx.curve_to(-110, -80, -178, -260, -152, -352)
    ctx.curve_to(-132, -412, -40, -418, 0, -398)
    ctx.curve_to(40, -418, 132, -412, 152, -352)
    ctx.curve_to(178, -260, 110, -80, 0, -50)
    ctx.close_path()
    ctx.set_source(radial(-50, -300, 300, "#FF5A6A", "#B5081E", -60, -330))
    ctx.fill_preserve()
    setc(ctx, "#8A0414")
    ctx.set_line_width(4)
    ctx.stroke()
    rnd = random.Random(3)
    for gy in range(-370, -70, 34):
        for gx in range(-160, 170, 36):
            x = gx + (17 if (gy // 34) % 2 else 0) + rnd.uniform(-4, 4)
            y = gy + rnd.uniform(-4, 4)
            if ((x) / 105) ** 2 + ((y + 268) / 100) ** 2 < 1:
                continue
            ctx.save()
            ctx.new_path()
            ctx.move_to(0, -50)
            ctx.curve_to(-100, -85, -166, -260, -142, -350)
            ctx.curve_to(-124, -400, 124, -400, 142, -350)
            ctx.curve_to(166, -260, 100, -85, 0, -50)
            ctx.clip()
            ellipse(ctx, x, y, 4, 6.5)
            setc(ctx, "#FFE08A")
            ctx.fill()
            ctx.restore()
    # feuilles = cheveux
    for i in range(7):
        a = math.pi + (i / 6) * math.pi
        ctx.save()
        ctx.translate(0, -398)
        ctx.rotate(a + math.pi / 2)
        ctx.move_to(0, 0)
        ctx.curve_to(-26, -40, -10, -88, 0, -100)
        ctx.curve_to(10, -88, 26, -40, 0, 0)
        setc(ctx, "#2E9E44" if i % 2 else "#3CBF55")
        ctx.fill()
        ctx.restore()
    rrect(ctx, -6, -460, 12, 40, 5)
    setc(ctx, "#2A7A33")
    ctx.fill()


def body_mango(ctx, c):
    ctx.save()
    ellipse(ctx, 0, -255, 138, 205)
    ctx.clip_preserve()
    ctx.set_source(linear(120, -440, -120, -60, [(0, "#E53935"), (0.45, "#FF7A1A"), (1, "#FFC233")]))
    ctx.fill()
    ellipse(ctx, 70, -400, 60, 40)
    setc(ctx, "#7CB342", 0.35)
    ctx.fill()
    # costume
    ctx.rectangle(-160, -195, 320, 200)
    setc(ctx, "#5A5F66")
    ctx.fill()
    ctx.move_to(-40, -195)
    ctx.line_to(40, -195)
    ctx.line_to(0, -105)
    ctx.close_path()
    setc(ctx, "#FFFFFF")
    ctx.fill()
    ctx.move_to(-8, -190)
    ctx.line_to(8, -190)
    ctx.line_to(12, -130)
    ctx.line_to(0, -112)
    ctx.line_to(-12, -130)
    ctx.close_path()
    setc(ctx, "#7A1020")
    ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx * 40, -195)
        ctx.line_to(sx * 8, -100)
        setc(ctx, "#3E4247")
        ctx.set_line_width(6)
        ctx.stroke()
    ctx.restore()
    ellipse(ctx, 0, -255, 138, 205)
    setc(ctx, "#9A2A10")
    ctx.set_line_width(4)
    ctx.stroke()
    rrect(ctx, -5, -480, 10, 30, 4)
    setc(ctx, "#5D4020")
    ctx.fill()


CHARS = {
    "bana": dict(body=body_banana, face=(64, -262), fs=1.0, skin="#FFE45C", iris="#6B3E1A",
                 lashes=True, lips="#C2185B", arms=((5, -205), (122, -205)),
                 legs=((10, -64), (40, -64)), limb="#5A3A12", name="Bana", color="#FFD93D"),
    "kiwi": dict(body=body_kiwi, face=(0, -222), fs=1.0, skin="#8FCB4F", iris="#3B2A16",
                 lashes=False, lips="#2D4A12", arms=((-145, -200), (145, -200)),
                 legs=((-40, -55), (40, -55)), limb="#4A3418", name="Kiwi", color="#9BE15D"),
    "fraise": dict(body=body_strawberry, face=(0, -270), fs=1.0, skin="#E8243A", iris="#1E6B2A",
                   lashes=True, lips="#FF8FC8", brow="#5A0A14", arms=((-150, -260), (150, -260)),
                   legs=((-30, -58), (30, -58)), limb="#7A0A18", name="Fraise", color="#FF5C7A"),
    "mangue": dict(body=body_mango, face=(0, -310), fs=1.0, skin="#FF8A2A", iris="#2A1A0A",
                   lashes=False, lips="#5A1A0A", arms=((-132, -180), (132, -180)),
                   legs=((-40, -55), (40, -55)), limb="#3E4247", name="Mangue", color="#FFA040"),
}


def draw_char(ctx, ch, t):
    """ch: dict k, x, y, s, expr, mouth, blink, look, pose, walk, flip, prop, alpha"""
    c = CHARS[ch["k"]]
    ctx.save()
    bob = math.sin(t * 2 * math.pi * 0.6 + ch["x"]) * 4 + ch.get("mouth", 0) * 5
    if ch.get("walk"):
        bob += abs(math.sin(t * 2 * math.pi * 1.6)) * -10
    ctx.translate(ch["x"], ch["y"] + bob)
    ctx.scale(ch["s"] * (-1 if ch.get("flip") else 1), ch["s"])
    # ombre
    ellipse(ctx, c["face"][0] * 0.4, 0, 140, 22)
    setc(ctx, "#000000", 0.28)
    ctx.fill()
    args = (ctx, c, c["arms"][0], c["arms"][1], c["legs"][0], c["legs"][1],
            ch.get("pose", "idle"), t, ch.get("walk", False), ch.get("prop"))
    limbs(*args, part="legs")
    c["body"](ctx, c)
    limbs(*args, part="arms")
    if ch.get("flip"):
        # garder le visage non inversé
        fx, fy = c["face"]
        ctx.save()
        ctx.translate(fx, fy)
        ctx.scale(-1, 1)
        ctx.translate(-fx, -fy)
    draw_face(ctx, c["face"][0], c["face"][1], c["fs"], c, ch.get("expr", "neutral"),
              ch.get("mouth", 0), ch.get("blink", False) or ch.get("sleep", False), t, ch.get("look", (0, 0)))
    if ch.get("flip"):
        ctx.restore()
    if ch.get("glasses"):
        fx, fy = c["face"]
        for sx in (-1, 1):
            rrect(ctx, fx + sx * 40 - 34, fy - 22, 68, 40, 12)
            setc(ctx, "#0A0A0A", 0.92)
            ctx.fill()
        ctx.move_to(fx - 8, fy - 8)
        ctx.line_to(fx + 8, fy - 8)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- décors
def floor(ctx, y, c0, c1):
    ctx.rectangle(0, y, W, H - y)
    ctx.set_source(linear(0, y, 0, H, [(0, c0), (1, c1)]))
    ctx.fill()


def window(ctx, x, y, w, h, sky, moon=False, sun=False):
    rrect(ctx, x - 14, y - 14, w + 28, h + 28, 10)
    setc(ctx, "#E8E1D0")
    ctx.fill()
    ctx.rectangle(x, y, w, h)
    ctx.set_source(linear(0, y, 0, y + h, sky))
    ctx.fill()
    if moon:
        ctx.arc(x + w * 0.7, y + h * 0.3, 42, 0, 2 * math.pi)
        setc(ctx, "#FFF6D5")
        ctx.fill()
        rnd = random.Random(1)
        for _ in range(25):
            ctx.arc(x + rnd.uniform(0, w), y + rnd.uniform(0, h * 0.8), rnd.uniform(1, 2.5), 0, 6.3)
            setc(ctx, "#FFFFFF", 0.8)
            ctx.fill()
    if sun:
        ctx.arc(x + w * 0.3, y + h * 0.35, 55, 0, 2 * math.pi)
        setc(ctx, "#FFF3B0")
        ctx.fill()
    setc(ctx, "#E8E1D0")
    ctx.rectangle(x + w / 2 - 7, y, 14, h)
    ctx.rectangle(x, y + h / 2 - 7, w, 14)
    ctx.fill()


def kitchen(ctx, t, night):
    wall = [(0, "#1B2347"), (1, "#0D1128")] if night else [(0, "#FFF1D6"), (1, "#F6D9A8")]
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, wall))
    ctx.fill()
    window(ctx, 300, 260, 480, 420,
           [(0, "#0A0F2E"), (1, "#26306A")] if night else [(0, "#7EC8FF"), (1, "#CDEBFF")],
           moon=night, sun=not night)
    # placards
    for i in range(3):
        rrect(ctx, 40 + i * 340, 760, 320, 300, 14)
        setc(ctx, "#2A3360" if night else "#C98B4E")
        ctx.fill()
        ctx.arc(40 + i * 340 + 290, 910, 9, 0, 6.3)
        setc(ctx, "#C9A24A")
        ctx.fill()
    # plan de travail
    ctx.rectangle(0, 1240, W, 40)
    setc(ctx, "#3B3F5A" if night else "#EDEDED")
    ctx.fill()
    floor(ctx, 1280, "#1E2240" if night else "#B9763A", "#0B0D1C" if night else "#8C5422")
    if not night:
        # plante + coupe de fruits
        rrect(ctx, 860, 1150, 90, 95, 14)
        setc(ctx, "#E86A3C")
        ctx.fill()
        for a in range(-3, 4):
            ctx.save()
            ctx.translate(905, 1150)
            ctx.rotate(a * 0.35)
            ellipse(ctx, 0, -60, 18, 60)
            setc(ctx, "#3AA655")
            ctx.fill()
            ctx.restore()
    else:
        # lampe chaude
        ctx.arc(540, 120, 520, 0, 6.3)
        ctx.set_source(radial(540, 120, 520, "#FFB86B30", "#FFB86B00"))
        ctx.fill()


def living_night(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#24173D"), (1, "#0F0A1E")]))
    ctx.fill()
    window(ctx, 640, 260, 320, 420, [(0, "#090C26"), (1, "#202A5E")], moon=True)
    # lampe
    ctx.rectangle(150, 520, 14, 620)
    setc(ctx, "#2B2B2B")
    ctx.fill()
    ctx.move_to(90, 520)
    ctx.line_to(224, 520)
    ctx.line_to(190, 420)
    ctx.line_to(124, 420)
    ctx.close_path()
    setc(ctx, "#F2C27A")
    ctx.fill()
    ctx.arc(157, 520, 420, 0, 6.3)
    ctx.set_source(radial(157, 520, 420, "#FFC07A40", "#FFC07A00"))
    ctx.fill()
    floor(ctx, 1300, "#2A1D3F", "#120C20")
    # canapé
    rrect(ctx, 60, 1000, 960, 260, 50)
    setc(ctx, "#5B3B8C")
    ctx.fill()
    rrect(ctx, 30, 1120, 1020, 240, 50)
    setc(ctx, "#6E4AA6")
    ctx.fill()


def street_day(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#7FC8FF"), (1, "#FFE3B3")]))
    ctx.fill()
    rnd = random.Random(5)
    x = -40
    while x < W:
        w = rnd.randint(180, 300)
        h = rnd.randint(500, 900)
        ctx.rectangle(x, 1200 - h, w, h)
        setc(ctx, rnd.choice(["#F2A65A", "#E76F51", "#F4D35E", "#8AB17D", "#E9C46A"]))
        ctx.fill()
        for wy in range(1200 - h + 50, 1150, 110):
            for wx in range(x + 30, x + w - 50, 80):
                ctx.rectangle(wx, wy, 44, 60)
                setc(ctx, "#FFFFFF", 0.7)
                ctx.fill()
        x += w + 10
    floor(ctx, 1200, "#BDBDBD", "#8E8E8E")
    ctx.rectangle(0, 1380, W, 18)
    setc(ctx, "#FFFFFF", 0.5)
    ctx.fill()


def cafe(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#F7E1C8"), (1, "#E0B98F")]))
    ctx.fill()
    for i in range(4):
        ctx.arc(140 + i * 270, 240, 30, 0, 6.3)
        setc(ctx, "#FFE8A3")
        ctx.fill()
        ctx.arc(140 + i * 270, 240, 160, 0, 6.3)
        ctx.set_source(radial(140 + i * 270, 240, 160, "#FFE8A360", "#FFE8A300"))
        ctx.fill()
        ctx.move_to(140 + i * 270, 0)
        ctx.line_to(140 + i * 270, 210)
        setc(ctx, "#3A2A1A")
        ctx.set_line_width(4)
        ctx.stroke()
    rrect(ctx, 80, 420, 920, 500, 20)
    setc(ctx, "#6D4C2F")
    ctx.fill()
    ctx.rectangle(110, 450, 860, 440)
    ctx.set_source(linear(0, 450, 0, 890, [(0, "#9FD3FF"), (1, "#DFF1FF")]))
    ctx.fill()
    floor(ctx, 1300, "#7A5234", "#4E3320")


def table_front(ctx):
    ctx.move_to(40, 1420)
    ctx.line_to(1040, 1420)
    ctx.line_to(1080, 1520)
    ctx.line_to(0, 1520)
    ctx.close_path()
    setc(ctx, "#F4EDE3")
    ctx.fill()
    ctx.rectangle(0, 1520, W, 30)
    setc(ctx, "#C9B9A3")
    ctx.fill()


def night_out(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#050816"), (1, "#141B3A")]))
    ctx.fill()
    ctx.arc(820, 260, 60, 0, 6.3)
    setc(ctx, "#FFF6D5")
    ctx.fill()
    # maison
    ctx.rectangle(260, 700, 560, 520)
    setc(ctx, "#2C2F45")
    ctx.fill()
    ctx.move_to(220, 720)
    ctx.line_to(540, 470)
    ctx.line_to(860, 720)
    ctx.close_path()
    setc(ctx, "#1C1E2E")
    ctx.fill()
    for wx in (330, 630):
        ctx.rectangle(wx, 800, 120, 120)
        setc(ctx, "#FFD27A")
        ctx.fill()
    ctx.rectangle(490, 1000, 100, 220)
    setc(ctx, "#5A3A22")
    ctx.fill()
    floor(ctx, 1220, "#0F2A1A", "#06140C")


def bushes_front(ctx):
    for i in range(9):
        ctx.arc(i * 135, 1640 + (i % 2) * 40, 150, 0, 6.3)
        setc(ctx, "#123D22" if i % 2 else "#185030")
        ctx.fill()


def warehouse(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#1A1A1E"), (1, "#0A0A0C")]))
    ctx.fill()
    for i in range(6):
        ctx.rectangle(i * 190 - 20, 0, 24, 1300)
        setc(ctx, "#26262C")
        ctx.fill()
    ctx.move_to(540, 0)
    ctx.line_to(300, 1400)
    ctx.line_to(780, 1400)
    ctx.close_path()
    ctx.set_source(linear(0, 0, 0, 1400, [(0, (1, 1, 0.85, 0.22)), (1, (1, 1, 0.85, 0.0))]))
    ctx.fill()
    floor(ctx, 1300, "#2A2A2E", "#111114")
    # caisses
    for (x, y) in ((40, 1080), (40, 880), (230, 1080), (860, 1080), (860, 880)):
        ctx.rectangle(x, y, 180, 200)
        setc(ctx, "#7A5A34")
        ctx.fill()
        ctx.move_to(x, y)
        ctx.line_to(x + 180, y + 200)
        ctx.move_to(x + 180, y)
        ctx.line_to(x, y + 200)
        setc(ctx, "#5A3F22")
        ctx.set_line_width(8)
        ctx.stroke()


def juicer(ctx, x, y, s, t, on=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -170, -620, 340, 520, 30)
    ctx.set_source(linear(-170, 0, 170, 0, [(0, "#6E7781"), (0.5, "#C9D1D9"), (1, "#5A626B")]))
    ctx.fill()
    ctx.move_to(-230, -760)
    ctx.line_to(230, -760)
    ctx.line_to(120, -620)
    ctx.line_to(-120, -620)
    ctx.close_path()
    setc(ctx, "#8B949E")
    ctx.fill()
    ctx.arc(0, -380, 80, 0, 6.3)
    setc(ctx, "#222222")
    ctx.fill()
    for i in range(6):
        a = t * (8 if on else 1) + i * math.pi / 3
        ctx.move_to(0, -380)
        ctx.line_to(math.cos(a) * 75, -380 + math.sin(a) * 75)
        setc(ctx, "#B0B8C0")
        ctx.set_line_width(10)
        ctx.stroke()
    ctx.arc(120, -560, 16, 0, 6.3)
    setc(ctx, "#FF3030" if int(t * 3) % 2 else "#661010")
    ctx.fill()
    rrect(ctx, -60, -110, 120, 60, 10)
    setc(ctx, "#40474E")
    ctx.fill()
    ctx.restore()


def sunrise(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, "#3B2C6B"), (0.45, "#FF7E5F"), (0.7, "#FEB47B"), (1, "#FFD8A8")]))
    ctx.fill()
    ctx.arc(540, 1160, 190, 0, 6.3)
    setc(ctx, "#FFF1C1")
    ctx.fill()
    ctx.arc(540, 1160, 520, 0, 6.3)
    ctx.set_source(radial(540, 1160, 520, "#FFF1C170", "#FFF1C100"))
    ctx.fill()
    floor(ctx, 1240, "#5B3A5E", "#2A1830")


def dark(ctx, t):
    ctx.rectangle(0, 0, W, H)
    setc(ctx, "#08080C")
    ctx.fill()


BGS = {
    "kitchen_night": lambda c, t: kitchen(c, t, True),
    "kitchen_day": lambda c, t: kitchen(c, t, False),
    "living_night": living_night,
    "street_day": street_day,
    "cafe": cafe,
    "night_out": night_out,
    "warehouse": warehouse,
    "sunrise": sunrise,
    "dark": dark,
}


# ---------------------------------------------------------------- overlays
def phone_overlay(ctx, t, sender, msg, appear=0.0, love=None):
    k = smooth((t - appear) / 0.35)
    ctx.save()
    ctx.translate(540, 1170 + (1 - k) * 900)
    ctx.scale(0.8, 0.8)
    rrect(ctx, -300, -600, 600, 1200, 70)
    setc(ctx, "#0E0E10")
    ctx.fill()
    rrect(ctx, -275, -575, 550, 1150, 55)
    ctx.set_source(linear(0, -575, 0, 575, [(0, "#2B3A67"), (1, "#0F1630")]))
    ctx.fill()
    rrect(ctx, -70, -560, 140, 34, 17)
    setc(ctx, "#000000")
    ctx.fill()
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(110)
    setc(ctx, "#FFFFFF")
    e = ctx.text_extents("23:47")
    ctx.move_to(-e.x_advance / 2, -330)
    ctx.show_text("23:47")
    nk = smooth((t - appear - 0.5) / 0.3)
    if nk > 0:
        ctx.translate(0, (1 - nk) * -60)
        lines = wrap(ctx, msg, 40, 440, bold=False)
        bh = 120 + 52 * len(lines)
        rrect(ctx, -250, -220, 500, bh, 36)
        setc(ctx, "#F2F2F7", 0.96 * nk)
        ctx.fill()
        rrect(ctx, -225, -195, 70, 70, 16)
        setc(ctx, "#34C759", nk)
        ctx.fill()
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(42)
        setc(ctx, "#111111", nk)
        ctx.move_to(-135, -150)
        ctx.show_text(sender)
        if (love if love is not None else sender == "Fraise"):
            sx = -135 + ctx.text_extents(sender).x_advance + 32
            heart(ctx, sx, -162, 20)
            setc(ctx, "#FF2D55", nk)
            ctx.fill()
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(40)
        for i, ln in enumerate(lines):
            ctx.move_to(-225, -80 + i * 52)
            setc(ctx, "#222222", nk)
            ctx.show_text(ln)
    ctx.restore()


def photo_overlay(ctx, t, flip_at=None, dur=1.0):
    """Cadre photo de Bana & Fraise ; se retourne face cachée à flip_at."""
    sc = 1.0
    if flip_at is not None:
        p = smooth((t - flip_at) / 0.6)
        sc = math.cos(p * math.pi)
    ctx.save()
    ctx.translate(540, 1080)
    ctx.scale(1, abs(sc) if sc != 0 else 0.01)
    rrect(ctx, -330, -280, 660, 520, 18)
    setc(ctx, "#7A4E2A")
    ctx.fill()
    if sc >= 0:
        rrect(ctx, -290, -240, 580, 440, 6)
        ctx.set_source(linear(0, -240, 0, 200, [(0, "#FFE7B8"), (1, "#FFB8C8")]))
        ctx.fill()
        ctx.save()
        rrect(ctx, -290, -240, 580, 440, 6)
        ctx.clip()
        ctx.translate(-540, -1080)
        draw_char(ctx, dict(k="bana", x=420, y=1290, s=0.85, expr="happy", blink=False), 0)
        draw_char(ctx, dict(k="fraise", x=660, y=1290, s=0.8, expr="happy", blink=False), 0)
        ctx.restore()
        heart(ctx, 0, -190, 30)
        setc(ctx, "#FF2D55")
        ctx.fill()
    else:
        rrect(ctx, -290, -240, 580, 440, 6)
        setc(ctx, "#5A3A1E")
        ctx.fill()
    ctx.restore()
    # étagère
    ctx.rectangle(120, 1340, 840, 40)
    setc(ctx, "#4A2E18")
    ctx.fill()


def screen_text_overlay(ctx, t, title, msg):
    ctx.rectangle(0, 0, W, H)
    setc(ctx, "#000000", 0.55)
    ctx.fill()
    phone_overlay(ctx, t, title, msg, appear=0)


# ---------------------------------------------------------------- effets
def vignette(ctx, strength=0.55):
    g = cairo.RadialGradient(540, 960, 500, 540, 960, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, strength)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def flashback(ctx):
    ctx.rectangle(0, 0, W, H)
    setc(ctx, "#FFB65C", 0.22)
    ctx.fill()
    g = cairo.RadialGradient(540, 960, 400, 540, 960, 1200)
    g.add_color_stop_rgba(0, 1, 1, 1, 0)
    g.add_color_stop_rgba(1, 1, 0.95, 0.85, 0.75)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def police_lights(ctx, t):
    on = int(t * 4) % 2
    ctx.rectangle(0, 0, W, H)
    setc(ctx, "#FF1E3C" if on else "#1E5BFF", 0.22)
    ctx.fill()


def flicker(ctx, t):
    v = 0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13)
    if v > 0.75:
        ctx.rectangle(0, 0, W, H)
        setc(ctx, "#000000", 0.55)
        ctx.fill()


def wind_lines(ctx, t):
    rnd = random.Random(int(t * 12))
    setc(ctx, "#FFFFFF", 0.5)
    ctx.set_line_width(4)
    for _ in range(10):
        x = rnd.uniform(0, W)
        y = rnd.uniform(200, 1600)
        ctx.move_to(x, y)
        ctx.line_to(x - 160, y + 10)
        ctx.stroke()


def juice_splash(ctx, t, start):
    p = t - start
    if p < 0 or p > 1.6:
        return
    rnd = random.Random(11)
    for _ in range(40):
        a = rnd.uniform(-math.pi, 0)
        v = rnd.uniform(400, 1100)
        x = 540 + math.cos(a) * v * p * 0.6
        y = 1380 + math.sin(a) * v * p * 0.6 + 900 * p * p * 0.5
        ctx.arc(x, y, rnd.uniform(8, 20) * (1 - p / 1.8), 0, 6.3)
        setc(ctx, "#FF9F1C", 0.9)
        ctx.fill()


def glass(ctx, x, y, s, broken=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if not broken:
        ctx.move_to(-40, -140)
        ctx.line_to(40, -140)
        ctx.line_to(30, 0)
        ctx.line_to(-30, 0)
        ctx.close_path()
        setc(ctx, "#FFFFFF", 0.35)
        ctx.fill_preserve()
        setc(ctx, "#FFFFFF", 0.8)
        ctx.set_line_width(3)
        ctx.stroke()
        ctx.move_to(-36, -90)
        ctx.line_to(36, -90)
        ctx.line_to(30, 0)
        ctx.line_to(-30, 0)
        ctx.close_path()
        setc(ctx, "#FF9F1C", 0.9)
        ctx.fill()
        ctx.move_to(20, -140)
        ctx.line_to(45, -200)
        setc(ctx, "#FF4FA0")
        ctx.set_line_width(7)
        ctx.stroke()
    ctx.restore()


def ropes(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for i, yy in enumerate((-150, -195, -240)):
        ctx.move_to(-130, yy + 12)
        ctx.curve_to(-40, yy - 14, 120, yy - 14, 220, yy + 12)
        setc(ctx, "#8D6E43")
        ctx.set_line_width(16)
        ctx.stroke()
        ctx.move_to(-130, yy + 12)
        ctx.curve_to(-40, yy - 14, 120, yy - 14, 220, yy + 12)
        setc(ctx, "#B8955F")
        ctx.set_line_width(6)
        ctx.set_dash([14, 10])
        ctx.stroke()
        ctx.set_dash([])
    ctx.restore()


def chair(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    rrect(ctx, -150, -470, 300, 330, 20)
    setc(ctx, "#4A3424")
    ctx.fill()
    rrect(ctx, -170, -150, 340, 40, 10)
    ctx.fill()
    for lx in (-150, 130):
        ctx.rectangle(lx, -110, 20, 110)
        ctx.fill()
    ctx.restore()
