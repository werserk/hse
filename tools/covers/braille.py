"""Braille dot-matrix rendering in the style of the Devault ASCII "Braille" preset (Glacier palette, Dark bg).

Each braille character is a 2x4 cell of dot positions. A dot is lit by ordered (Bayer) dithering of the
sub-cell luminance; the dot colour follows the cell's mean luminance along the Glacier ramp; a soft bloom
is added on top. Input: a float luminance field in [0, 1]. Output: an RGB PIL image.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BG = (13, 13, 18)
RAMP = [(0.00, (29, 79, 214)), (0.30, (47, 143, 240)), (0.50, (69, 192, 245)),
        (0.70, (168, 238, 248)), (0.85, (230, 253, 255)), (1.00, (255, 255, 255))]
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32


# "paper" variant for the light hse.werserk.dev theme: ink dots on the card's white, no glow
PAPER_BG = (255, 255, 255)
PAPER_RAMP = [(0.00, (185, 180, 170)), (0.45, (110, 106, 98)), (0.80, (45, 43, 40)), (1.00, (28, 27, 25))]


def ramp(v, stops=RAMP):
    xs = np.array([r[0] for r in stops]); cs = np.array([r[1] for r in stops], float)
    return np.stack([np.interp(v, xs, cs[:, k]) for k in range(3)], -1)


def levels(lum, shadows=0.06, gamma=1.0):
    lo, hi = np.percentile(lum, 1), np.percentile(lum, 99.7)
    v = np.clip((lum - lo) / max(hi - lo, 1e-6), 0, 1) ** gamma
    return np.where(v < shadows, 0, v)


def render(lum, size=(1600, 900), pitch=8, radius=0.31, bloom=0.15, scale=2, shadows=0.06, gamma=1.0, paper=False, paper_ramp=None):
    """lum: 2-D array, any resolution with the target aspect. pitch: dot spacing in output px."""
    W, H = size
    nx, ny = W // pitch, H // pitch
    nx -= nx % 2; ny -= ny % 4                       # whole braille cells
    small = np.asarray(Image.fromarray((np.clip(lum, 0, 1) * 65535).astype(np.uint16)).resize((nx, ny), Image.BOX),
                       float) / 65535
    v = levels(small, shadows, gamma)
    on = v > np.tile(BAYER, (ny // 4 + 1, nx // 4 + 1))[:ny, :nx]
    cell = v.reshape(ny // 4, 4, nx // 2, 2).mean((1, 3))
    tone = np.repeat(np.repeat(cell, 4, 0), 2, 1) * 0.6 + v * 0.4
    col = ramp(tone ** 0.8, paper_ramp or PAPER_RAMP) if paper else ramp(tone ** 1.7)
    S = scale
    if paper:
        img = Image.new("RGB", (W * S, H * S), PAPER_BG); d = ImageDraw.Draw(img)
        ox, oy = (W - nx * pitch) / 2 + pitch / 2, (H - ny * pitch) / 2 + pitch / 2
        r = radius * pitch * S
        for j, i in zip(*np.nonzero(on)):
            cx, cy = (ox + i * pitch) * S, (oy + j * pitch) * S
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c) for c in col[j, i]))
        return img.resize((W, H), Image.LANCZOS)
    img = Image.new("RGB", (W * S, H * S), BG)
    dots = Image.new("RGB", (W * S, H * S), (0, 0, 0))
    d = ImageDraw.Draw(dots)
    ox, oy = (W - nx * pitch) / 2 + pitch / 2, (H - ny * pitch) / 2 + pitch / 2
    r = radius * pitch * S
    for j, i in zip(*np.nonzero(on)):
        cx, cy = (ox + i * pitch) * S, (oy + j * pitch) * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(c) for c in col[j, i]))
    glow = np.asarray(dots.filter(ImageFilter.GaussianBlur(pitch * S * 1.2)), float) * bloom * 2.2
    out = np.asarray(img, float) + np.asarray(dots, float) + glow
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
