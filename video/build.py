"""Fabrique une vidéo TikTok (1080x1920) à partir d'une histoire.

Usage : python3 build.py stories/banane.py [numéro_de_partie ...]
"""
import asyncio
import hashlib
import importlib.util
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cairo
import numpy as np

import engine as e

FPS = 24
SR = 24000
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
OUT = os.path.join(HERE, "..", "videos")

VOICES = {
    "narr": ("fr-FR-RemyMultilingualNeural", "-10%", "-6Hz"),
    "bana": ("fr-FR-DeniseNeural", "-4%", "+4Hz"),
    "kiwi": ("fr-FR-HenriNeural", "+4%", "+0Hz"),
    "fraise": ("fr-BE-CharlineNeural", "+6%", "+10Hz"),
    "mangue": ("fr-CH-FabriceNeural", "-10%", "-14Hz"),
}


# ---------------------------------------------------------------- audio
def tts_all(items):
    """items: liste (speaker, text) -> dict clé -> chemin wav"""
    import certifi
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):  # proxy de l'environnement cloud
        certifi.where = lambda: ca
    import edge_tts

    os.makedirs(CACHE, exist_ok=True)
    todo, paths = [], {}
    for spk, text in items:
        voice, rate, pitch = VOICES[spk]
        key = hashlib.md5(f"{voice}|{rate}|{pitch}|{text}".encode()).hexdigest()
        mp3 = os.path.join(CACHE, key + ".mp3")
        wav = os.path.join(CACHE, key + ".wav")
        paths[(spk, text)] = wav
        if not os.path.exists(wav):
            todo.append((voice, rate, pitch, text, mp3, wav))

    async def one(v, r, p, text, mp3, wav):
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, v, rate=r, pitch=p).save(mp3)
                break
            except Exception:
                if attempt == 3:
                    raise
                await asyncio.sleep(2 ** attempt)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)

    async def run():
        sem = asyncio.Semaphore(6)

        async def guarded(*a):
            async with sem:
                await one(*a)
        await asyncio.gather(*(guarded(*x) for x in todo))

    if todo:
        asyncio.run(run())
    return paths


def load_wav(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    # retirer le silence de début/fin
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz):
        a = a[max(0, nz[0] - 600): nz[-1] + 1200]
    return a


def envelope(a):
    hop = SR // FPS
    n = len(a) // hop + 1
    env = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(n)])
    peak = np.percentile(env, 95) + 1e-6
    env = np.clip(env / peak, 0, 1)
    env[env < 0.12] = 0
    return env.tolist()


def tone(f, dur, amp=1.0, decay=None, harm=(1, 0.3, 0.1)):
    t = np.arange(int(dur * SR)) / SR
    s = sum(h * np.sin(2 * np.pi * f * (i + 1) * t) for i, h in enumerate(harm))
    env = np.exp(-t * decay) if decay else np.minimum(1, np.minimum(t / 0.4, (dur - t) / 0.6).clip(0))
    return (s * env * amp).astype(np.float32)


NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)


def add(out, p, st):
    if st >= len(out):
        return
    m = min(len(p), len(out) - st)
    out[st:st + m] += p[:m]


def music(mood, dur):
    n = int(dur * SR) + SR
    out = np.zeros(n, np.float32)
    if mood in ("sad", "happy", "love"):
        prog = {"sad": [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)],
                "happy": [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)],
                "love": [(53, 57, 60, 64), (55, 59, 62), (57, 60, 64), (52, 55, 59)]}[mood]
        bar = 2.6
        i = 0
        while i * bar < dur + bar:
            ch = prog[i % len(prog)]
            st = int(i * bar * SR)
            for nn in ch:
                p = tone(NOTE(nn - 12), bar + 0.6, 0.05)
                add(out, p, st)
            for j, nn in enumerate(ch + (ch[0] + 12,)):
                ps = st + int(j * bar / 4 * SR)
                p = tone(NOTE(nn + (12 if mood != "sad" else 0)), 1.6, 0.06, decay=3.2, harm=(1, 0.5, 0.25, 0.1))
                add(out, p, ps)
            i += 1
    elif mood == "tense":
        t = np.arange(n) / SR
        out += (0.07 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t))).astype(np.float32)
        out += (0.03 * np.sin(2 * np.pi * 58.3 * t)).astype(np.float32)
        k = 0.0
        while k < dur:
            for off in (0, 0.22):
                p = tone(48, 0.25, 0.35, decay=18, harm=(1,))
                st = int((k + off) * SR)
                add(out, p, st)
            k += 0.95
    elif mood == "action":
        t = np.arange(n) / SR
        beat = 0.42
        k = 0.0
        while k < dur:
            p = tone(60, 0.2, 0.4, decay=20, harm=(1,))
            st = int(k * SR)
            add(out, p, st)
            k += beat
        out += (0.03 * np.sign(np.sin(2 * np.pi * 110 * t)) * (np.sin(2 * np.pi * t / beat) > 0)).astype(np.float32)
    return out


def sfx(name):
    rnd = np.random.default_rng(1)
    if name == "notif":
        return np.concatenate([tone(988, 0.12, 0.3, decay=12), tone(1319, 0.25, 0.3, decay=10)])
    if name == "boom":
        t = np.arange(int(1.4 * SR)) / SR
        return (0.6 * np.sin(2 * np.pi * (70 - 30 * t) * t) * np.exp(-t * 3)).astype(np.float32)
    if name == "sting":
        chord = sum(tone(NOTE(nn), 2.0, 0.12, decay=1.6) for nn in (45, 57, 60, 64, 69))
        b = sfx("boom")
        return chord + np.pad(b, (0, len(chord) - len(b)))
    if name == "whoosh":
        t = np.arange(int(0.7 * SR)) / SR
        nz = rnd.standard_normal(len(t)).astype(np.float32)
        nz = np.convolve(nz, np.ones(30) / 30, mode="same")
        return (nz * np.sin(np.pi * t / 0.7) * 0.5).astype(np.float32)
    if name == "glass":
        t = np.arange(int(0.9 * SR)) / SR
        nz = rnd.standard_normal(len(t)).astype(np.float32) * np.exp(-t * 7)
        ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((3200, 5), (4700, 7), (2600, 4)))
        return ((nz * 0.3 + ring * 0.12)).astype(np.float32)
    if name == "door":
        b = sfx("boom")
        return b * 0.9 + np.pad(sfx("glass")[:2000] * 0.3, (0, len(b) - 2000))
    if name == "siren":
        t = np.arange(int(2.5 * SR)) / SR
        f = 700 + 250 * np.sign(np.sin(2 * np.pi * 1.5 * t))
        return (0.12 * np.sin(2 * np.pi * np.cumsum(f) / SR)).astype(np.float32)
    if name == "machine":
        t = np.arange(int(3.0 * SR)) / SR
        return (0.12 * np.sin(2 * np.pi * 90 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 12 * t)))).astype(np.float32)
    if name == "heart":
        return np.concatenate([tone(50, 0.18, 0.6, decay=20, harm=(1,)), np.zeros(int(0.06 * SR), np.float32),
                               tone(45, 0.25, 0.5, decay=16, harm=(1,))])
    raise KeyError(name)


# ---------------------------------------------------------------- timeline
def plan_part(part):
    items = [(s, txt) for sh in part["shots"] for (s, txt) in sh.get("lines", []) if s in VOICES]
    paths = tts_all(items)
    audio = {k: load_wav(p) for k, p in paths.items()}
    plans, t0 = [], 0.0
    for sh in part["shots"]:
        cur = sh.get("lead", 0.5)
        lines = []
        for spk, txt in sh.get("lines", []):
            if spk in VOICES:
                a = audio[(spk, txt)]
                d = len(a) / SR
                lines.append(dict(spk=spk, text=txt, start=cur, end=cur + d, env=envelope(a), key=(spk, txt)))
                cur += d + 0.45
            else:  # texte écran sans voix
                lines.append(dict(spk=spk, text=txt, start=0, end=1e9, env=[], key=None))
        dur = max(sh.get("min", 2.5), cur + sh.get("tail", 0.6))
        plans.append(dict(shot=sh, lines=lines, dur=dur, t0=t0))
        t0 += dur
    return plans, audio, t0


def mix_audio(part, plans, audio, total, path):
    n = int((total + 1) * SR)
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    for p in plans:
        for ln in p["lines"]:
            if ln["key"]:
                a = audio[ln["key"]]
                st = int((p["t0"] + ln["start"]) * SR)
                voice[st:st + len(a)] += a[: n - st]
        for name, at in p["shot"].get("sfx", []):
            s = sfx(name)
            st = int((p["t0"] + at) * SR)
            fx[st:st + len(s)] += s[: max(0, n - st)]
    # musique par plan avec fondu
    mus = np.zeros(n, np.float32)
    tracks = {}
    gains = {}
    default = part.get("music", "sad")
    for p in plans:
        m = p["shot"].get("music", default)
        if m and m not in tracks:
            tracks[m] = music(m, total)[:n]
            tracks[m] = np.pad(tracks[m], (0, n - len(tracks[m])))
            gains[m] = np.zeros(n, np.float32)
        if m:
            a, b = int(p["t0"] * SR), int((p["t0"] + p["dur"]) * SR)
            gains[m][a:b] = 1
    k = np.ones(int(0.3 * SR), np.float32) / int(0.3 * SR)
    for m in tracks:
        g = np.convolve(gains[m], k, mode="same")
        mus += tracks[m] * g
    # ducking sous les voix
    venv = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    duck = 1 - 0.55 * np.clip(venv * 12, 0, 1)
    mixed = voice * 1.0 + fx * 0.9 + mus * duck * 1.1
    mixed = mixed[: int(total * SR)]
    peak = np.max(np.abs(mixed)) + 1e-9
    mixed = mixed / max(peak, 1.0) * 0.95
    pcm = (mixed * 32767).astype(np.int16).tobytes()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", path],
                   input=pcm, check=True)


# ---------------------------------------------------------------- rendu
def expr_at(ch, frac):
    ex = ch.get("expr", "neutral")
    if isinstance(ex, str):
        return ex
    cur = ex[0][1]
    for f, x in ex:
        if frac >= f:
            cur = x
    return cur


def char_state(ch, t, dur, lines, local_t):
    frac = t / dur
    st = dict(ch)
    st["expr"] = expr_at(ch, frac)
    if "move" in ch:
        x1, y1 = ch["move"][:2]
        a, b = (ch["move"][2], ch["move"][3]) if len(ch["move"]) > 2 else (0, 1)
        k = e.smooth((frac - a) / max(b - a, 1e-3))
        st["x"] = ch["x"] + (x1 - ch["x"]) * k
        st["y"] = ch["y"] + (y1 - ch["y"]) * k
        st["walk"] = ch.get("walk", False) and 0 < k < 1
    if "pose_at" in ch:
        for f, pz in ch["pose_at"]:
            if frac >= f:
                st["pose"] = pz
    if "show" in ch:
        a, b = ch["show"]
        if not (a <= frac < b):
            return None
    mouth = 0.0
    for ln in lines:
        if ln["spk"] == ch["k"] and ln["start"] <= t < ln["end"] and ln["env"]:
            i = int((t - ln["start"]) * FPS)
            mouth = ln["env"][min(i, len(ln["env"]) - 1)]
    st["mouth"] = mouth
    seed = sum(map(ord, ch["k"])) * 0.37
    st["blink"] = ((t + seed) % 3.3) < 0.12 and mouth < 0.05
    return st


def render_frame(ctx, part, plan, t):
    sh, dur = plan["shot"], plan["dur"]
    frac = t / dur
    z0, z1, fx, fy = sh.get("cam", (1.0, 1.06, 540, 1100))
    z = z0 + (z1 - z0) * e.smooth(frac)
    ctx.save()
    if "shake" in sh.get("fx", []) or ("shake_at" in sh and t > sh["shake_at"] and t < sh["shake_at"] + 0.6):
        ctx.translate(math.sin(t * 90) * 10, math.cos(t * 77) * 10)
    ctx.translate(fx, fy)
    ctx.scale(z, z)
    ctx.translate(-fx, -fy)
    e.BGS[sh["bg"]](ctx, t)
    for pr in sh.get("props_back", []):
        draw_prop(ctx, pr, t, frac)
    chars = []
    for ch in sh.get("chars", []):
        s = char_state(ch, t, dur, plan["lines"], t)
        if s:
            chars.append(s)
    for s in sorted(chars, key=lambda c: c["y"]):
        e.draw_char(ctx, s, t)
    for pr in sh.get("props", []):
        draw_prop(ctx, pr, t, frac)
    front = sh.get("front")
    if front == "table":
        e.table_front(ctx)
    elif front == "bushes":
        e.bushes_front(ctx)
    for pr in sh.get("props_front", []):
        draw_prop(ctx, pr, t, frac)
    ctx.restore()

    for f in sh.get("fx", []):
        if f == "flashback":
            e.flashback(ctx)
        elif f == "police":
            e.police_lights(ctx, t)
        elif f == "flicker" and frac > 0.4:
            e.flicker(ctx, t)
        elif f == "wind":
            e.wind_lines(ctx, t)
    if "splash" in sh:
        e.juice_splash(ctx, t, sh["splash"])
    ov = sh.get("overlay")
    if ov and ov[0] == "phone":
        a = ov[3] if len(ov) > 3 else 0.2
        if t >= a:
            ctx.rectangle(0, 0, e.W, e.H)
            e.setc(ctx, "#000000", 0.5 * e.smooth((t - a) / 0.3))
            ctx.fill()
            e.phone_overlay(ctx, t, ov[1], ov[2], appear=a)
    elif ov and ov[0] == "photo":
        e.photo_overlay(ctx, t, flip_at=ov[1])
    e.vignette(ctx, 0.5)

    # textes
    top_y = 430
    for ln in plan["lines"]:
        if ln["spk"] in ("narr", "txt") and ln["start"] - 0.1 <= t:
            top_y += e.boxed_text(ctx, ln["text"], 540, top_y, 50) + 24
        elif ln["spk"] in e.CHARS and ln["start"] <= t < ln["end"] + 0.15:
            c = e.CHARS[ln["spk"]]
            e.outlined_text(ctx, c["name"].upper(), 540, 1490, 44, fill=c["color"], sw=9)
            e.outlined_text(ctx, ln["text"], 540, 1570, 62, sw=11)
    # badge
    ctx.select_font_face(e.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34)
    label = f"{part['title']}  ·  PARTIE {part['n']}/{part['of']}"
    w = ctx.text_extents(label).x_advance
    e.rrect(ctx, 540 - w / 2 - 24, 222, w + 48, 58, 29)
    e.setc(ctx, "#000000", 0.55)
    ctx.fill()
    ctx.move_to(540 - w / 2, 263)
    e.setc(ctx, "#FFFFFF")
    ctx.show_text(label)
    # carte de fin
    end = sh.get("end")
    if end:
        k = e.smooth((t - (dur - 2.0)) / 0.4)
        if k > 0:
            ctx.rectangle(0, 0, e.W, e.H)
            e.setc(ctx, "#000000", 0.6 * k)
            ctx.fill()
            pulse = 1 + 0.05 * math.sin(t * 8)
            ctx.save()
            ctx.translate(540, 900)
            ctx.scale(pulse * k, pulse * k)
            y = -60
            for i, txt in enumerate(end):
                y += e.outlined_text(ctx, txt, 0, y, 96 if i == 0 else 54, fill="#FFD93D" if i == 0 else "#FFFFFF",
                                     sw=14, maxw=900) + 20
            ctx.restore()
    # fondu d'entrée de la vidéo
    if plan["t0"] == 0 and t < 0.25:
        ctx.rectangle(0, 0, e.W, e.H)
        e.setc(ctx, "#000000", 1 - t / 0.25)
        ctx.fill()


def draw_prop(ctx, pr, t, frac):
    kind = pr[0]
    if kind == "juicer":
        e.juicer(ctx, pr[1], pr[2], pr[3], t, on=len(pr) > 4 and pr[4])
    elif kind == "glass":
        broken_at = pr[4] if len(pr) > 4 else 99
        if t < broken_at:
            e.glass(ctx, pr[1], pr[2], pr[3])
    elif kind == "ropes":
        e.ropes(ctx, pr[1], pr[2], pr[3])
    elif kind == "chair":
        e.chair(ctx, pr[1], pr[2], pr[3])
    elif kind == "heart":
        k = e.smooth(frac * 2)
        e.heart(ctx, pr[1], pr[2] - 40 * math.sin(t * 2), pr[3] * k)
        e.setc(ctx, "#FF2D55", 0.9)
        ctx.fill()
    elif kind == "car":
        x0, x1, y = pr[1], pr[2], pr[3]
        x = x0 + (x1 - x0) * e.smooth(frac)
        e.rrect(ctx, x - 200, y - 150, 400, 120, 40)
        e.setc(ctx, "#1C1C22")
        ctx.fill()
        e.rrect(ctx, x - 120, y - 230, 240, 100, 40)
        ctx.fill()
        for wx in (-120, 120):
            ctx.arc(x + wx, y - 30, 45, 0, 6.3)
            e.setc(ctx, "#0A0A0A")
            ctx.fill()
        ctx.arc(x + 190, y - 100, 18, 0, 6.3)
        e.setc(ctx, "#FFF2A8")
        ctx.fill()


def render_shot(args):
    part, plan, path = args
    n = max(1, int(round(plan["dur"] * FPS)))
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                             "-s", f"{e.W}x{e.H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, e.W, e.H)
    for i in range(n):
        ctx = cairo.Context(surf)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        render_frame(ctx, part, plan, i / FPS)
        surf.flush()
        proc.stdin.write(bytes(surf.get_data()))
    proc.stdin.close()
    proc.wait()
    return n


def load_story(path):
    spec = importlib.util.spec_from_file_location("story", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_part(story, part, slug):
    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(CACHE, f"{slug}_p{part['n']}")
    os.makedirs(work, exist_ok=True)
    plans, audio, total = plan_part(part)
    print(f"Partie {part['n']} : {len(plans)} plans, {total:.1f} s")
    jobs = [(part, p, os.path.join(work, f"shot{i:02d}.mp4")) for i, p in enumerate(plans)]
    with Pool(min(4, os.cpu_count() or 1)) as pool:
        pool.map(render_shot, jobs)
    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as f:
        for _, _, p in jobs:
            f.write(f"file '{p}'\n")
    wav = os.path.join(work, "audio.wav")
    mix_audio(part, plans, audio, total, wav)
    out = os.path.join(OUT, f"{slug}_partie{part['n']}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out],
                   check=True)
    print("→", os.path.relpath(out))
    return out


if __name__ == "__main__":
    story = load_story(sys.argv[1])
    slug = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    wanted = [int(x) for x in sys.argv[2:]] or [p["n"] for p in story.PARTS]
    for p in story.PARTS:
        if p["n"] in wanted:
            build_part(story, p, slug)
