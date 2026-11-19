#!/usr/bin/env python3
"""Braille-dot cover for a case: one command from a title/topic.

  python3 tools/covers/cover.py content/<course>/<case>            # title from entry.json, writes cover.webp
  python3 tools/covers/cover.py content/<course>/<case> --topic "coalescent tree" --scene tree
  python3 tools/covers/cover.py --all-missing                        # every case without "cover" in entry.json

The scene is abstract and loosely tied to the topic: a motif is picked from keywords in the title/topic (or --scene),
and the title seeds its random details, so a case always gets the same picture. Style: braille.py (ink dots on white,
brand burgundy on the brightest tones), same as genomics/loter and runtime. Needs numpy and pillow.
Sets "cover": "cover.webp" in entry.json (only that key is touched).
"""
import argparse, hashlib, json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from braille import render

W, H = 1600, 900
ROOT = Path(__file__).resolve().parents[2]
ACCENT = [(0, (185, 180, 170)), (0.45, (110, 106, 98)), (0.72, (40, 38, 35)), (0.80, (140, 47, 43)), (1, (140, 47, 43))]


def ball(buf, cx, cy, r, gain=1.0):
    n = int(np.ceil(r)) * 2 + 1
    y, x = (np.mgrid[0:n, 0:n] - n // 2) / r
    rr = x * x + y * y; z = np.sqrt(np.clip(1 - rr, 0, 1))
    lam = np.clip(-0.45 * x - 0.55 * y + 0.7 * z, 0, 1)
    lum = 0.18 + 0.7 * lam + 0.6 * lam ** 24; a = np.clip((1 - rr) * r, 0, 1)
    x0, y0 = int(round(cx)) - n // 2, int(round(cy)) - n // 2
    xs, ys = slice(max(x0, 0), min(x0 + n, W)), slice(max(y0, 0), min(y0 + n, H))
    if xs.start >= xs.stop or ys.start >= ys.stop: return
    sl = (slice(ys.start - y0, ys.stop - y0), slice(xs.start - x0, xs.stop - x0))
    buf[ys, xs] = buf[ys, xs] * (1 - a[sl]) + lum[sl] * gain * a[sl]


def strands(rng):
    """Tubes sweeping diagonally, each a mosaic of bright/dim pieces (genes, populations, inheritance)."""
    buf = np.zeros((H, W)); yy, xx = np.mgrid[0:H, 0:W].astype(float)
    a = np.deg2rad(rng.uniform(10, 26)); c, s = np.cos(a), np.sin(a)
    u, v = c * (xx - W / 2) - s * (yy - H / 2), s * (xx - W / 2) + c * (yy - H / 2)
    for k in sorted(range(5), key=lambda k: -abs(k - 2)):
        depth = 1 - abs(k - 2) * 0.16; R = 46 * depth
        d = (v - ((k - 2) * 135 + 38 * np.sin(u / 260 + k * 1.3) + 14 * np.sin(u / 90 + k))) / R
        shade = np.sqrt(np.clip(1 - d * d, 0, 1)); spec = np.exp(-((d + 0.45) / 0.18) ** 2)
        edges = np.sort(rng.uniform(-1100, 1100, 9)); seg = np.searchsorted(edges, u)
        lv = np.where((seg + k) % 2 == 0, 1.0, 0.42) * rng.uniform(0.85, 1, 10)[seg]
        gap = np.min(np.abs(u[..., None] - edges[None, None, :]), -1) < 7
        val = (0.12 + 0.75 * shade * lv + 0.55 * spec * lv) * depth
        buf = np.where(np.abs(d) < 1, np.where(gap, val * 0.15, val), buf)
    return buf


def tree(rng):
    """Branching tree of beads: lineages merging into a root (coalescent, ancestry, hierarchy)."""
    n = 14
    nodes = [(W * (0.1 + 0.8 * (i + rng.uniform(-.25, .25)) / (n - 1)), H * 0.92, 0.0) for i in range(n)]
    pil = Image.new("F", (W, H), 0); d = ImageDraw.Draw(pil); top = H * 0.1
    while len(nodes) > 1:
        i = int(rng.integers(len(nodes) - 1)); j = i + 1
        (x1, y1, _), (x2, y2, _) = nodes[i], nodes[j]
        y = min(y1, y2) - rng.uniform(55, 120) * (1 + 0.15 * (n - len(nodes)) * 0.1); y = max(y, top)
        x = (x1 + x2) / 2
        for (px, py, _) in (nodes[i], nodes[j]):
            d.line([(px, py), (px, y), (x, y)], fill=0.7, width=7)
        nodes[i:j + 1] = [(x, y, 1.0)]
    img = np.asarray(pil, float)
    for x in [(W * (0.1 + 0.8 * i / (n - 1))) for i in range(n)]:
        ball(img, x, H * 0.92, 16, 0.9)
    ball(img, nodes[0][0], nodes[0][1], 26, 1.0)
    return img


def flow(rng):
    """Streamlines of a smooth field drawn as chains of beads (dynamics, differential equations)."""
    img = np.zeros((H, W))
    ph = rng.uniform(0, 6.28, 4); k = rng.uniform(0.8, 1.6, 2)
    def f(x, y):
        X, Y = (x - W / 2) / 420, (y - H / 2) / 420
        return np.array([np.sin(k[0] * Y + ph[0]) + 0.6 * np.cos(X + ph[1]), np.cos(k[1] * X + ph[2]) - 0.6 * np.sin(Y + ph[3]) - 0.35])
    for sx in np.linspace(-100, W + 100, 14):
        for sy in np.linspace(40, H - 40, 6):
            p = np.array([sx + rng.uniform(-30, 30), sy]); steps = 70
            for t in range(steps):
                v = f(*p); p = p + 11 * v / (np.linalg.norm(v) + 1e-6)
                if not (0 <= p[0] < W and 0 <= p[1] < H): break
                ball(img, p[0], p[1], 3.2 + 6.5 * t / steps, 0.35 + 0.65 * t / steps)
    return img


def walks(rng):
    """Random walks fanning out from one point, with the endpoints as bright beads (Monte Carlo, Markov chains, noise)."""
    img = np.zeros((H, W)); ox, oy = W * 0.18, H / 2
    for _ in range(26):
        p = np.array([ox, oy]); ang = rng.normal(0, 0.35); g = rng.uniform(0.35, 0.8)
        for t in range(180):
            ang += rng.normal(0, 0.28); p = p + 9 * np.array([np.cos(ang), np.sin(ang)]) + [3.2, 0]
            if not (0 <= p[0] < W and 0 <= p[1] < H): break
            ball(img, p[0], p[1], 3.5 + 2.5 * t / 180, g * (0.45 + 0.55 * t / 180))
        ball(img, p[0], p[1], 15, 1.0)
    ball(img, ox, oy, 30, 1.0)
    return img


def lattice(rng):
    """Surface of beads in perspective (a cost, a distribution, a parameter space)."""
    buf = np.zeros((H, W)); pts = []; a, b2 = rng.uniform(0.6, 1.6, 2)
    for a_ in np.linspace(0, 1, 52):
        for b in np.linspace(0, 1, 30):
            X, Y = (a_ - 0.5) * 3.2, 1.2 + 2.0 * b
            Z = 1.2 * np.exp(-((a_ - 0.5) * 3 * a) ** 2 - ((b - 0.5) * 3 * b2) ** 2) + 0.15 * np.sin(6 * a_ + 5 * b)
            pts.append((Y, W / 2 + X * 560 / Y, H * 0.45 + (0.9 - Z) * 560 / Y, 14 / Y, 0.4 + 0.6 * np.clip(Z, 0, 1.4) / 1.4))
    for Y, px, py, r, g in sorted(pts, key=lambda p: -p[0]): ball(buf, px, py, max(r, 2.2), g)
    return buf


SCENES = {"strands": strands, "tree": tree, "flow": flow, "walks": walks, "lattice": lattice}
KEYWORDS = [("flow", ("дифференц", "уравнен", "differential", "ode")), ("walks", ("монте", "стохаст", "марков", "monte", "markov", "random")),
            ("tree", ("коалесц", "филоген", "дерев", "skygrid", "coalescent", "tree")), ("strands", ("геном", "lai", "днк", "genom", "формул")),
            ("lattice", ())]


def pick_scene(text, seed):
    t = text.lower()
    for name, keys in KEYWORDS:
        if any(k in t for k in keys): return name
    return list(SCENES)[seed % len(SCENES)]


def make(text, out, scene=None):
    seed = int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)
    name = scene or pick_scene(text, seed)
    lum = np.clip(SCENES[name](np.random.default_rng(seed)), 0, 1)
    lum = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), float) / 255
    render(lum, pitch=7, radius=0.36, gamma=0.85, paper=True, paper_ramp=ACCENT).save(out, quality=82)
    return name


def do_case(d, topic=None, scene=None):
    p = d / "entry.json"; e = json.loads(p.read_text(encoding="utf-8"))
    out = d / "cover.webp"; name = make(" ".join([e.get("title", ""), topic or ""]), out, scene)
    if e.get("cover") != "cover.webp":
        t = p.read_text(encoding="utf-8").rstrip()  # add the key in place, keep the rest of the file as written
        p.write_text(t[:-1].rstrip() + ', "cover": "cover.webp"}\n', encoding="utf-8")
    print(d.relative_to(ROOT) if d.is_absolute() and ROOT in d.parents else d, name, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case", nargs="?", help="content/<course>/<case>"); ap.add_argument("--topic"); ap.add_argument("--scene", choices=SCENES)
    ap.add_argument("--all-missing", action="store_true")
    a = ap.parse_args()
    if a.all_missing:
        for p in sorted((ROOT / "content").glob("*/*/entry.json")):
            e = json.loads(p.read_text(encoding="utf-8"))
            if not e.get("cover") and e.get("type") not in ("link",): do_case(p.parent)
    elif a.case: do_case(Path(a.case).resolve(), a.topic, a.scene)
    else: ap.error("give a case folder or --all-missing")
