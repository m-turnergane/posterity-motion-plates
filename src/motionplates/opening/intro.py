"""Black ink on parchment, then a plain black ACT I card.

The wordmark is the locked raster master used as a mask. Letters fill by
distance from interior seeds, so the front is ragged and stays inside the
glyph. A finished letter matches that mask. ACT I is a hard cut to black
with centred cream type. Nothing in this module calls an image model.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from motionplates.opening.camera import OUT_H, OUT_W, cover_sample

FONT = Path(__file__).resolve().parents[3] / "assets/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf"
INK = np.array([16, 12, 10], np.float32) / 255.0
CREAM = np.array([236, 226, 208], np.float32)
TITLE = "The Letter for a Buried King"
ACT = "ACT I"
ACT_AT = 5.20
HOLD_END = 7.50


def _ease(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3.0 - 2.0 * u)


def _ease_map(u: np.ndarray) -> np.ndarray:
    u = np.clip(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def _font(size: int) -> ImageFont.FreeTypeFont:
    if not FONT.exists():
        raise FileNotFoundError(f"missing IM Fell DW Pica at {FONT}")
    return ImageFont.truetype(str(FONT), size)


def text_mask(text: str, size: int, tracking: int = 0) -> np.ndarray:
    font = _font(size)
    widths = []
    for ch in text:
        box = font.getbbox(ch)
        widths.append(box[2] - box[0] + tracking)
    width = max(8, sum(widths) + 8)
    height = font.getbbox("Hg")[3] + 16
    img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(img)
    x = 4
    for ch, wch in zip(text, widths):
        draw.text((x, 4), ch, font=font, fill=255)
        x += wch
    return np.asarray(img)


def parchment_from_leaf(leaf: np.ndarray, seed: int = 1611) -> np.ndarray:
    """Interior of the chronicle leaf, without the certificate border.

    The centre of CB1 is the painted vellum. It is cover-fit, then given a
    little fibre and stain so the upscale does not read as a soft blur.
    """
    h, w = leaf.shape[:2]
    patch = leaf[int(h * 0.36):int(h * 0.64), int(w * 0.36):int(w * 0.64)]
    base = cover_sample(patch, 1.0, 0.5, 0.5)
    rng = np.random.default_rng([seed, 11])
    noise = rng.standard_normal((OUT_H, OUT_W)).astype(np.float32)
    fine = cv2.GaussianBlur(noise, (0, 0), 0.7)
    coarse = cv2.GaussianBlur(noise, (0, 0), 14)
    stain = cv2.GaussianBlur(rng.standard_normal((OUT_H // 4, OUT_W // 4)).astype(np.float32), (0, 0), 6)
    stain = cv2.resize(stain, (OUT_W, OUT_H), interpolation=cv2.INTER_LINEAR)
    img = base.astype(np.float32)
    img += fine[..., None] * np.array([5.0, 3.5, 2.0], np.float32)
    img += coarse[..., None] * np.array([8.0, 6.0, 3.0], np.float32)
    img *= 1.0 - np.clip(stain, 0.0, None)[..., None] * 0.07
    yy = np.linspace(0, 1, OUT_H, dtype=np.float32)[:, None]
    for y, gain in ((0.18, 0.03), (0.82, 0.025)):
        line = np.exp(-((yy - y) ** 2) / (2 * 0.0012)) * gain
        img -= line[..., None] * np.array([28, 18, 12], np.float32)
    holes = rng.random((8, 2))
    holes[:, 0] = holes[:, 0] * 0.16 + np.array([0.04, 0.80, 0.06, 0.84, 0.08, 0.78, 0.12, 0.88])
    holes[:, 1] = rng.random(8)
    for x, y in holes:
        cv2.circle(img, (int(x * OUT_W), int(y * OUT_H)), int(rng.integers(2, 5)), (92, 68, 48), -1, lineType=cv2.LINE_AA)
    return np.clip(img, 0, 255).astype(np.uint8)


def _components(mask: np.ndarray) -> list[np.ndarray]:
    n, labels = cv2.connectedComponents((mask > 16).astype(np.uint8), connectivity=8)
    out = []
    for i in range(1, n):
        comp = labels == i
        if int(comp.sum()) > 12:
            out.append(comp)
    out.sort(key=lambda c: float(np.nonzero(c)[1].mean()))
    return out


class InkMark:
    """Organic fill of one exact raster, precomputed."""

    def __init__(self, alpha: np.ndarray, seed: int):
        self.alpha = alpha
        mask = alpha.astype(np.float32) / 255.0
        binary = mask > 0.08
        h, w = mask.shape
        rng = np.random.default_rng(seed)
        noise = cv2.GaussianBlur(rng.random((h, w)).astype(np.float32), (0, 0), 3.5)
        seeds = np.zeros((h, w), np.uint8)
        delay = np.zeros((h, w), np.float32)
        for i, comp in enumerate(_components(alpha)):
            inside = (cv2.distanceTransform(comp.astype(np.uint8), cv2.DIST_L2, 3)).astype(np.float32)
            ys, xs = np.nonzero(inside > 0.5)
            if len(xs) == 0:
                continue
            # A few interior seeds, biased to the stroke's left edge, plus
            # medial points so the fill runs through the letter rather than
            # across it as a bar.
            order = np.argsort(xs + rng.random(len(xs)) * 2.0)
            take = order[: max(1, len(order) // 18)]
            medial = inside >= max(1.5, float(np.percentile(inside[inside > 0], 70)))
            my, mx = np.nonzero(medial)
            if len(mx):
                step = max(1, len(mx) // 6)
                seeds[my[::step], mx[::step]] = 1
            seeds[ys[take], xs[take]] = 1
            delay[comp] = 0.11 * i
        if seeds.max() == 0:
            seeds[binary] = 1
        field = np.where(seeds > 0, 0, 1).astype(np.uint8)
        dist = cv2.distanceTransform(field, cv2.DIST_L2, 5).astype(np.float32)
        speed = 0.55 + 0.9 * noise
        arrival = dist / speed + delay
        inside = arrival[binary]
        hi = float(np.percentile(inside, 98)) if inside.size else 1.0
        hi = max(hi, 1e-3)
        self.arrival = arrival / hi
        self.mask = mask
        self.density = (0.86 + 0.14 * cv2.GaussianBlur(noise, (0, 0), 1.2)).astype(np.float32)
        dil = cv2.dilate(binary.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2)
        self.bleed = cv2.GaussianBlur(dil.astype(np.float32), (0, 0), 1.3)
        self.bleed = np.clip(self.bleed - mask, 0, 1) * (0.35 + 0.4 * noise)

    def at(self, u: float) -> np.ndarray:
        u = min(1.0, max(0.0, u))
        if u >= 0.995:
            return self.mask * self.density
        front = _ease_map((u * 1.08 - self.arrival) / 0.045)
        body = self.mask * front * self.density
        edge = self.bleed * np.clip(front * 1.4, 0, 1) * (1.0 - u * 0.85)
        return np.clip(body + edge, 0, 1)


def _multiply(base: np.ndarray, alpha: np.ndarray, origin: tuple[int, int], ink: np.ndarray = INK) -> np.ndarray:
    ah, aw = alpha.shape
    y, x = origin
    y0, x0 = max(0, y), max(0, x)
    y1, x1 = min(base.shape[0], y + ah), min(base.shape[1], x + aw)
    if y1 <= y0 or x1 <= x0:
        return base
    sub = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    patch = base[y0:y1, x0:x1].astype(np.float32) / 255.0
    painted = patch * (1.0 - sub * (1.0 - ink.reshape(1, 1, 3)))
    base[y0:y1, x0:x1] = np.clip(painted * 255.0, 0, 255).astype(np.uint8)
    return base


def _place(alpha: np.ndarray, y: int) -> tuple[int, int]:
    return y, (OUT_W - alpha.shape[1]) // 2


def act_card(local: float, fade: float = 0.35) -> np.ndarray:
    """Solid black, centred ACT I, cream serif. ``local`` is seconds on the card."""
    frame = np.zeros((OUT_H, OUT_W, 3), np.uint8)
    mask = text_mask(ACT, 92, tracking=10)
    u = 1.0 if fade <= 0 else _ease(min(1.0, max(0.0, local / fade)))
    alpha = (mask.astype(np.float32) / 255.0) * u
    y, x = _place(mask, (OUT_H - mask.shape[0]) // 2)
    ah, aw = alpha.shape
    y1, x1 = min(OUT_H, y + ah), min(OUT_W, x + aw)
    if y1 > y and x1 > x:
        sub = alpha[:y1 - y, :x1 - x][..., None]
        frame[y:y1, x:x1] = np.clip(CREAM.reshape(1, 1, 3) * sub, 0, 255).astype(np.uint8)
    return frame


class Intro:
    def __init__(self, leaf: np.ndarray, wordmark: np.ndarray, act_at: float = ACT_AT):
        self.act_at = act_at
        self.paper = parchment_from_leaf(leaf)
        wm = wordmark[:, :, 3] if wordmark.ndim == 3 else wordmark
        target = 1080
        scale = target / wm.shape[1]
        word = cv2.resize(wm, (target, max(1, int(round(wm.shape[0] * scale)))), interpolation=cv2.INTER_LANCZOS4)
        self.word = InkMark(word, 1611)
        self.title = InkMark(text_mask(TITLE, 52, tracking=1), 1613)
        # Sit the type in the upper field. The leaf's centre fold stays below it.
        self.word_at = _place(word, 250)
        self.title_at = _place(self.title.alpha, 250 + word.shape[0] + 36)

    def frame(self, local: float) -> np.ndarray:
        if local >= self.act_at:
            return act_card(local - self.act_at)
        frame = self.paper.copy()
        word_u = _ease(min(1.0, max(0.0, (local - 0.35) / 2.45)))
        if word_u > 0:
            frame = _multiply(frame, self.word.at(word_u), self.word_at)
        title_u = _ease(min(1.0, max(0.0, (local - 1.85) / 1.70)))
        if title_u > 0:
            frame = _multiply(frame, self.title.at(title_u), self.title_at)
        return frame
