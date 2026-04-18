#!/usr/bin/env python3
"""
Lyra 2.0 — Cinematic Hindi Video Generator
Generates a full 5-minute MP4 video with binaural audio.
"""
import os, sys, math, subprocess
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Lyra2_Cinematic_Hindi.mp4")

# ── Auto-install ──────────────────────────────────────────────
def pip(pkg):
    print(f"  Installing {pkg}...")
    subprocess.call([sys.executable, "-m", "pip", "install", pkg, "-q"])

print("\n[*] Checking dependencies...")
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pip("Pillow"); from PIL import Image, ImageDraw, ImageFont
try:
    import numpy as np
except ImportError:
    pip("numpy"); import numpy as np
try:
    from moviepy.editor import concatenate_videoclips
    from moviepy.audio.AudioClip import AudioArrayClip
    from moviepy.video.VideoClip import VideoClip
except ImportError:
    pip("moviepy==1.0.3")
    from moviepy.editor import concatenate_videoclips
    from moviepy.audio.AudioClip import AudioArrayClip
    from moviepy.video.VideoClip import VideoClip

print("  [OK] All dependencies ready.\n")

# ── Constants ─────────────────────────────────────────────────
W, H, FPS, SR = 1280, 720, 24, 44100
SCENE_DUR = 30  # seconds per scene

# ── Font loading ──────────────────────────────────────────────
def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\NirmalaUI" + ("B" if bold else "") + ".ttf",
        r"C:\Windows\Fonts\NirmalaUI.ttf",
        r"C:\Windows\Fonts\mangal.ttf",
        r"C:\Windows\Fonts\ArialUnicodeMS.ttf",
        r"C:\Windows\Fonts\Arial.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

FONT_XL = load_font(72, bold=True)
FONT_LG = load_font(56, bold=True)
FONT_MD = load_font(38)
FONT_SM = load_font(26)
FONT_XS = load_font(20)

# ── Helpers ───────────────────────────────────────────────────
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def ease(t):
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def text_w(draw, text, font):
    try:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]
    except:
        return len(text) * (font.size // 2 if hasattr(font, 'size') else 12)

def draw_center(draw, y, text, font, color):
    if not text: return
    x = (W - text_w(draw, text, font)) // 2
    # shadow
    for dx, dy in [(-2, 2), (2, 2), (0, 3), (-1, -1)]:
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=color)

def fade_in(t, start, dur=0.8):
    return clamp((t - start) / dur)

def overlay_text(base_img, t, main, sub, main_col=(255, 255, 255)):
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    a1 = fade_in(t, 0.5)
    a2 = fade_in(t, 1.0)
    if a1 > 0:
        c = (*main_col[:3], int(255 * a1))
        draw_center(d, H - 210, main, FONT_LG, c)
    if a2 > 0:
        c = (180, 185, 210, int(210 * a2))
        draw_center(d, H - 135, sub, FONT_SM, c)
    result = Image.alpha_composite(base_img.convert('RGBA'), overlay)
    return result.convert('RGB')

# ── Binaural audio ────────────────────────────────────────────
def gen_audio(beat_hz, base_freq, duration):
    t = np.linspace(0, duration, int(SR * duration), endpoint=False)
    fade = min(SR, int(SR * 1.2))
    L = np.sin(2 * np.pi * base_freq * t) * 0.20
    R = np.sin(2 * np.pi * (base_freq + beat_hz) * t) * 0.20
    drone = np.sin(2 * np.pi * base_freq * 0.5 * t) * 0.06
    L += drone; R += drone
    env = np.ones(len(t))
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    L *= env; R *= env
    return AudioArrayClip(np.stack([L, R], axis=1).astype(np.float32), fps=SR)

# ═══════════════════════════════════════════════════════════════
# SCENE RENDERERS
# ═══════════════════════════════════════════════════════════════

def s1_sparks(t):
    """ACT I Scene 1 — Spark Fall"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(42)
    xs    = rng.randint(20, W-20, 22)
    speeds= rng.uniform(70, 210, 22)
    lens  = rng.randint(40, 140, 22)
    offs  = rng.uniform(0, 9, 22)
    widths= rng.randint(1, 4, 22)
    for i in range(22):
        period = (H + lens[i]) / speeds[i]
        local_t = (t + offs[i]) % period
        sy = int(local_t * speeds[i]) - lens[i]
        ey = sy + int(lens[i])
        if ey < 0 or sy > H: continue
        brightness = int(200 + 55 * (local_t / period))
        c = (brightness, int(brightness * 0.85), int(brightness * 0.35))
        draw.line([(xs[i], max(0, sy)), (xs[i], min(H, ey))], fill=c, width=int(widths[i]))
    return overlay_text(img, t, "कल्पना करो...", "Ek andheri jagah mein, pehli roshan ki iskra", (240, 192, 96))

def s2_grid(t):
    """ACT I Scene 2 — Perspective Grid"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    reveal = clamp(ease((t - 0.2) / 2.2))
    horizon = int(H * 0.36)
    gc = (0, 160, 220)
    n_h = int(20 * reveal)
    for i in range(n_h):
        p = (i + 1) / 20
        y = horizon + int((H - horizon) * (p ** 0.65))
        bright = clamp(1 - p * 0.55)
        c = tuple(int(x * bright * 0.75) for x in gc)
        draw.line([(0, y), (W, y)], fill=c, width=1)
    n_v = int(14 * reveal)
    for i in range(-n_v, n_v + 1):
        xb = W // 2 + i * 72
        c = tuple(int(x * 0.4) for x in gc)
        draw.line([(xb, H), (W // 2, horizon)], fill=c, width=1)
    # horizon glow
    for dy in range(6, 0, -1):
        a = int(30 * (1 - dy / 6) * reveal)
        draw.line([(0, horizon + dy), (W, horizon + dy)], fill=(0, a * 3, a * 5), width=1)
    return overlay_text(img, t, "दुनिया सिर्फ 2D थी", "Flat pixels. Frozen images. Koi depth nahi.", (0, 212, 255))

def s3_eye(t):
    """ACT I Scene 3 — Pulsing Eye"""
    img = Image.new('RGB', (W, H), (8, 0, 18))
    draw = ImageDraw.Draw(img)
    # radial bg
    cx, cy = W // 2, H // 2
    for r in range(350, 0, -14):
        a = (1 - r / 350) * 0.12
        c = (int(50 * a), 0, int(100 * a))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c)
    pulse = 1 + 0.09 * math.sin(t * 2 * math.pi / 2.2)
    ew, eh = int(300 * pulse), int(150 * pulse)
    ex, ey = cx - ew // 2, cy - eh // 2
    # outer glow
    for g in range(5, 0, -1):
        ge = g * 7
        gc = int(40 * (1 - g / 5))
        draw.ellipse([ex - ge, ey - ge // 2, ex + ew + ge, ey + eh + ge // 2],
                     outline=(gc, 0, gc * 2), width=1)
    draw.ellipse([ex, ey, ex + ew, ey + eh], outline=(168, 85, 247), width=2)
    ir = int(eh * 0.42 * pulse)
    draw.ellipse([cx - ir, cy - ir, cx + ir, cy + ir], fill=(90, 40, 180))
    pr = int(ir * 0.42)
    draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(0, 0, 0))
    for r in [ir + 3, ir + 7, ir + 14]:
        a = max(0, int(100 * (1 - (r - ir) / 15)))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(168, 85, 247, a), width=1)
    return overlay_text(img, t, "AI ne dekhna seekha", "Depth map · Point cloud · Spatial understanding", (168, 85, 247))

def s4_cloud(t):
    """ACT I Scene 4 — Point Cloud"""
    img = Image.new('RGB', (W, H), (0, 0, 14))
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(123)
    n = 550
    xs = rng.uniform(W * 0.12, W * 0.88, n)
    ys = rng.uniform(H * 0.15, H * 0.82, n)
    zs = rng.uniform(0, 1, n)
    hs = rng.uniform(175, 240, n)
    ph = rng.uniform(0, 2 * math.pi, n)
    reveal = clamp(ease(t / 7))
    for i in range(int(n * reveal)):
        x = xs[i] + math.sin(t * 0.32 + ph[i]) * 9
        y = ys[i] + math.cos(t * 0.26 + ph[i]) * 7
        sz = max(1, int(1.5 + zs[i] * 3.5))
        h = hs[i]
        a = (math.sin(t * 0.45 + ph[i]) * 0.25 + 0.75)
        r = int(min(255, 40 + 80 * abs(math.sin(math.radians(h)))) * a)
        g = int(min(255, 180 + 60 * abs(math.sin(math.radians(h + 90)))) * a)
        b = int(min(255, 210 + 45 * abs(math.cos(math.radians(h)))) * a)
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=(r, g, b))
    return overlay_text(img, t, "एक photo से 3D दुनिया", "Input image → Depth → Point Cloud → 3D Space", (34, 211, 238))

def s5_curve(t):
    """ACT I Scene 5 — Exponential Curve"""
    img = Image.new('RGB', (W, H), (0, 14, 6))
    draw = ImageDraw.Draw(img)
    ox, oy = 170, H - 165
    aw, ah = W - 270, H - 260
    draw.line([(ox, oy - ah - 25), (ox, oy)], fill=(70, 70, 70), width=2)
    draw.line([(ox, oy), (ox + aw + 25, oy)], fill=(70, 70, 70), width=2)
    # arrow heads
    draw.polygon([(ox - 5, oy - ah - 25), (ox + 5, oy - ah - 25), (ox, oy - ah - 38)], fill=(70, 70, 70))
    draw.polygon([(ox + aw + 25, oy - 5), (ox + aw + 25, oy + 5), (ox + aw + 40, oy)], fill=(70, 70, 70))
    prog = clamp(ease((t - 0.4) / 4.5))
    pts = []
    steps = 220
    for i in range(int(steps * prog) + 1):
        px = i / steps
        x = ox + int(aw * px)
        ey = (math.exp(px * 4.2) - 1) / (math.exp(4.2) - 1)
        y = oy - int(ah * min(1.0, ey))
        pts.append((x, y))
    if len(pts) > 1:
        for i in range(len(pts) - 1):
            p = i / max(1, len(pts))
            r = int(lerp(0, 60, p))
            g = int(lerp(190, 255, p))
            b = int(lerp(80, 130, p))
            draw.line([pts[i], pts[i + 1]], fill=(r, g, b), width=3)
        tip = pts[-1]
        for r in [9, 6, 3]:
            draw.ellipse([tip[0] - r, tip[1] - r, tip[0] + r, tip[1] + r], fill=(0, 255, 136))
    # year labels
    for yr, px in [("2022", 0.05), ("2024", 0.38), ("2026", 0.72)]:
        x = ox + int(aw * px)
        if x < ox + aw * prog:
            draw.line([(x, oy), (x, oy + 8)], fill=(60, 60, 60), width=1)
            draw_center(draw, oy + 12, yr, FONT_XS, (80, 80, 80))
    return overlay_text(img, t, "Exponential growth शुरू हुआ", "Generative AI: 2022 → 2024 → 2026 → ∞", (0, 255, 136))

def s6_cold(t):
    """ACT II Scene 6 — Cold Doubt"""
    img = Image.new('RGB', (W, H), (5, 13, 40))
    draw = ImageDraw.Draw(img)
    # vignette
    cx, cy = W // 2, H // 2
    for r in range(500, 10, -18):
        a = (1 - r / 500) * 0.07
        c = (int(5 * a * 12), int(13 * a * 8), int(40 * a * 6))
        draw.ellipse([cx - r, cy - int(r * 0.75), cx + r, cy + int(r * 0.75)], outline=c)
    words = ["REAL?", "SACH?", "भ्रम?", "TRUE?", "FAKE?", "वास्तविक?"]
    word = words[int(t / 1.15) % len(words)]
    gx = int(math.sin(t * 39) * 5)
    gy = int(math.cos(t * 53) * 3)
    tw = text_w(draw, word, FONT_XL)
    x = (W - tw) // 2
    y = H // 2 - 90
    draw.text((x + gx + 5, y + gy), word, font=FONT_XL, fill=(220, 0, 70))
    draw.text((x + gx - 5, y + gy), word, font=FONT_XL, fill=(0, 180, 255))
    draw.text((x + gx, y + gy), word, font=FONT_XL, fill=(55, 110, 255))
    # scan lines
    rng2 = np.random.RandomState(int(t * FPS) % 1000)
    for sy in range(0, H, 5):
        if rng2.random() < 0.06:
            draw.line([(0, sy), (W, sy)], fill=(0, 20, 55), width=1)
    return overlay_text(img, t, "लेकिन... क्या यह सच है?", "Ya sirf believable hallucination hai?", (100, 140, 255))

def s7_mirror(t):
    """ACT II Scene 7 — Mirror Illusion"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    pulse = 0.88 + 0.12 * math.sin(t * 2 * math.pi / 3.0)
    mw, mh = int(310 * pulse), int(470 * pulse)
    mx, my = (W - mw) // 2, (H - mh) // 2 - 30
    for g in range(5, 0, -1):
        ge = g * 10
        draw.rectangle([mx - ge, my - ge, mx + mw + ge, my + mh + ge],
                       outline=(int(30 * (1 - g / 5)), int(60 * (1 - g / 5)), int(180 * (1 - g / 5))))
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(10, 16, 55))
    draw.rectangle([mx, my, mx + mw, my + mh], outline=(70, 110, 240), width=1)
    ma = int(90 + 75 * math.sin(t * 2 * math.pi / 3.0))
    fc = (ma, int(ma * 1.15), 255)
    draw_center(draw, my + mh // 2 - 35, "वही दृश्य", FONT_MD, fc)
    draw_center(draw, my + mh // 2 + 18, "दूसरा कोण", FONT_SM, tuple(int(x * 0.5) for x in fc))
    return overlay_text(img, t, "अलग angle, वही भ्रम", "Old methods: no memory, no consistency, no truth", (100, 140, 255))

def s8_breakthrough(t):
    """ACT III Scene 8 — Breakthrough"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2
    for delay, base_col in [(0, (255, 255, 255)), (0.8, (255, 215, 0)), (1.6, (255, 140, 0))]:
        rt = (t - delay) % 2.4
        if rt < 0: continue
        prog = ease(rt / 2.4)
        r = int(prog * min(W, H) * 0.72)
        a = clamp(1 - prog)
        if r <= 0: continue
        c = tuple(int(x * a) for x in base_col)
        for th in range(4, 0, -1):
            if r - th > 0:
                draw.ellipse([cx - r + th, cy - r + th, cx + r - th, cy + r - th],
                             outline=tuple(int(x * (th / 4)) for x in c), width=2)
    # center flash
    cf = clamp(1 - t * 2.5)
    if cf > 0:
        fv = int(255 * cf)
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(fv, fv, fv))
    # text
    if t > 0.9:
        ta = clamp((t - 0.9) / 1.2)
        c = (int(255 * ta), int(215 * ta), 0)
        draw_center(draw, H // 2 - 55, "Lyra 2.0 का जवाब", FONT_LG, c)
    return overlay_text(img, t, "Spatial Memory · 3D Consistency", "Real Exploration · Global Consistency · No Hallucination", (255, 215, 0))

def s9_galaxy(t):
    """ACT III Scene 9 — Galaxy Zoom"""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(77)
    cx, cy = W // 2, H // 2
    n = 420
    angles = rng.uniform(0, 2 * math.pi, n)
    radii  = rng.uniform(0, min(W, H) * 0.65, n)
    sizes  = rng.uniform(0.4, 2.2, n)
    smult = 1 + t * 0.18
    for i in range(n):
        r = radii[i] * smult
        x = cx + r * math.cos(angles[i])
        y = cy + r * math.sin(angles[i]) * 0.58
        if x < -5 or x > W + 5 or y < -5 or y > H + 5: continue
        dist_frac = r / (min(W, H) * 0.65 * smult)
        a = clamp(dist_frac * 1.3)
        sz = max(1, int(sizes[i] * (1 + dist_frac * 1.5)))
        bv = int(190 + 65 * a)
        c = (bv, int(bv * 0.88), int(bv * 0.72))
        draw.ellipse([x - sz, y - sz, x + sz, y + sz], fill=c)
    return overlay_text(img, t, "Infinite दुनिया। एक image से।", "DiT + Spatial Memory = Globally Consistent 3D World", (240, 192, 96))

def s10_triumph(t):
    """ACT III Scene 10 — Triumph"""
    img = Image.new('RGB', (W, H), (18, 6, 0))
    draw = ImageDraw.Draw(img)
    rng = np.random.RandomState(55)
    n = 85
    pxb   = rng.uniform(W / 2 - 260, W / 2 + 260, n)
    spds  = rng.uniform(55, 195, n)
    szs   = rng.uniform(2.0, 6.5, n)
    hues  = rng.uniform(22, 60, n)
    ofts  = rng.uniform(0, 4.5, n)
    for i in range(n):
        period = H * 0.86 / spds[i]
        lt = (t + ofts[i]) % period
        py = H * 0.84 - lt * spds[i]
        if py < -10 or py > H: continue
        life = clamp(1 - py / (H * 0.84))
        h = hues[i]
        rc = min(255, int(lerp(240, 255, h / 60) * life))
        gc = min(255, int(lerp(120, 200, h / 60) * life))
        draw.ellipse([pxb[i] - szs[i], py - szs[i], pxb[i] + szs[i], py + szs[i]],
                     fill=(rc, gc, 0))
    # main text
    ta = clamp((t - 0.4) / 1.6)
    if ta > 0:
        glow_a = abs(math.sin(t * math.pi / 2.2))
        lines = ["अब तुम", "explore", "कर सकते हो"]
        ys = [H // 2 - 165, H // 2 - 35, H // 2 + 95]
        for line, ly in zip(lines, ys):
            gv = min(255, int(192 + 50 * glow_a))
            for dx, dy in [(-3, 0), (3, 0), (0, -2), (0, 2)]:
                c_glow = (int(200 * ta), int(100 * ta), 0)
                draw.text(((W - text_w(draw, line, FONT_XL)) // 2 + dx, ly + dy),
                          line, font=FONT_XL, fill=c_glow)
            draw_center(draw, ly, line, FONT_XL, (int(240 * ta), int(gv * ta), int(80 * ta)))
    if t > 22:
        a2 = clamp((t - 22) / 2.5)
        draw_center(draw, H - 68, "Lyra 2.0  ·  arXiv:2604.13036  ·  NVIDIA Research  ·  2026",
                    FONT_XS, (int(140 * a2), int(110 * a2), int(65 * a2)))
    return np.array(img)

# ═══════════════════════════════════════════════════════════════
# SCENE CONFIGS
# ═══════════════════════════════════════════════════════════════
SCENES = [
    {"fn": s1_sparks,       "beat": 8.0,  "base": 200, "label": "ACT I   · Awakening"},
    {"fn": s2_grid,         "beat": 8.0,  "base": 210, "label": "ACT I   · 2D World"},
    {"fn": s3_eye,          "beat": 8.0,  "base": 200, "label": "ACT I   · AI Vision"},
    {"fn": s4_cloud,        "beat": 7.83, "base": 194, "label": "ACT I   · Point Cloud (Schumann)"},
    {"fn": s5_curve,        "beat": 8.0,  "base": 200, "label": "ACT I   · Exponential"},
    {"fn": s6_cold,         "beat": 4.0,  "base": 180, "label": "ACT II  · Doubt"},
    {"fn": s7_mirror,       "beat": 3.5,  "base": 175, "label": "ACT II  · Illusion"},
    {"fn": s8_breakthrough, "beat": 10.0, "base": 210, "label": "ACT III · Breakthrough"},
    {"fn": s9_galaxy,       "beat": 10.0, "base": 220, "label": "ACT III · Galaxy"},
    {"fn": s10_triumph,     "beat": 10.0, "base": 220, "label": "ACT III · Triumph"},
]

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 56)
    print("  LYRA 2.0 -- CINEMATIC HINDI VIDEO GENERATOR")
    print("=" * 56)
    print(f"  Resolution : {W}x{H}  @  {FPS} fps")
    print(f"  Duration   : {len(SCENES) * SCENE_DUR // 60} min {len(SCENES) * SCENE_DUR % 60} sec")
    print(f"  Scenes     : {len(SCENES)}")
    print(f"  Output     : {OUTPUT_FILE}")
    print()

    clips = []
    for i, sc in enumerate(SCENES):
        print(f"  [{i+1:02d}/10]  Rendering  {sc['label']} ...", end=" ", flush=True)

        fn = sc["fn"]
        def make_frame(t, _fn=fn):
            frame = _fn(t)
            if isinstance(frame, Image.Image):
                return np.array(frame.convert('RGB'))
            return frame

        video = VideoClip(make_frame, duration=SCENE_DUR)
        audio = gen_audio(sc["beat"], sc["base"], SCENE_DUR)
        clips.append(video.set_audio(audio))
        print("OK")

    print()
    print("  Concatenating all scenes ...")
    final = concatenate_videoclips(clips, method="compose")

    print("  Encoding MP4 (this takes ~5–15 min depending on your CPU) ...")
    print()
    final.write_videofile(
        OUTPUT_FILE,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        audio_fps=SR,
        preset="faster",
        ffmpeg_params=["-crf", "20"],
        verbose=False,
        logger="bar",
    )

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print()
    print("=" * 56)
    print("  VIDEO READY!")
    print("=" * 56)
    print(f"  File : Lyra2_Cinematic_Hindi.mp4")
    print(f"  Size : {size_mb:.1f} MB")
    print(f"  Path : {OUTPUT_FILE}")
    print("=" * 56)
    print()
    # Open folder
    try:
        os.startfile(OUTPUT_DIR)
    except:
        pass

if __name__ == "__main__":
    main()
