"""One geometric resample from a plate to the delivery frame.

Crop edges stay in floating point. A slow move does not snap to whole
source pixels before the resize. A shot may ease ``z`` by a few percent.
The window stays on the plate, so the resample does not reveal an edge
by reflecting it.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

OUT_W = 1920
OUT_H = 1080


@dataclass(frozen=True)
class Cover:
    z: float
    cx: float
    cy: float
    x0: float
    y0: float
    cw: float
    ch: float
    src_w: int
    src_h: int
    out_w: int = OUT_W
    out_h: int = OUT_H

    @property
    def source_wh(self) -> tuple[float, float]:
        return (self.cw, self.ch)

    @property
    def upscales(self) -> bool:
        return self.cw + 1e-3 < self.out_w or self.ch + 1e-3 < self.out_h

    def to_frame(self, px: float, py: float) -> tuple[float, float]:
        return (
            (px - self.x0) * self.out_w / self.cw,
            (py - self.y0) * self.out_h / self.ch,
        )

    def matrix(self) -> np.ndarray:
        """Output pixel -> source pixel, with pixel-center alignment."""
        sx = self.cw / self.out_w
        sy = self.ch / self.out_h
        return np.float32([
            [sx, 0.0, self.x0 + 0.5 * sx - 0.5],
            [0.0, sy, self.y0 + 0.5 * sy - 0.5],
        ])


def smoothstep(u: float) -> float:
    """Ease used by a scale-only push. Flat at both ends, so it does not tick."""
    u = min(1.0, max(0.0, float(u)))
    return u * u * (3.0 - 2.0 * u)


def cover_window(
    src_w: int,
    src_h: int,
    z: float,
    cx: float,
    cy: float,
    out_w: int = OUT_W,
    out_h: int = OUT_H,
) -> Cover:
    """Cover-fit, then zoom by ``z`` around ``(cx, cy)`` in 0..1 plate units.

    ``z`` of 1 fills the frame and crops only the aspect-ratio difference.
    Larger ``z`` enlarges. The window is clamped so it stays on the plate.
    """
    if z <= 0:
        raise ValueError(f"zoom must be positive, got {z}")
    base = max(out_w / src_w, out_h / src_h)
    scale = base * z
    cw = out_w / scale
    ch = out_h / scale
    if cw > src_w + 1.0 or ch > src_h + 1.0:
        raise ValueError(f"zoom {z} is wider than the plate")
    cw = min(cw, float(src_w))
    ch = min(ch, float(src_h))
    x0 = min(max(cx * src_w - cw / 2.0, 0.0), src_w - cw)
    y0 = min(max(cy * src_h - ch / 2.0, 0.0), src_h - ch)
    return Cover(z, cx, cy, x0, y0, cw, ch, src_w, src_h, out_w, out_h)


def warp(plate: np.ndarray, cam: Cover) -> np.ndarray:
    return cv2.warpAffine(
        plate,
        cam.matrix(),
        (cam.out_w, cam.out_h),
        flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
        borderMode=cv2.BORDER_REFLECT101,
    )


def cover_sample(
    plate: np.ndarray,
    z: float,
    cx: float,
    cy: float,
    out_w: int = OUT_W,
    out_h: int = OUT_H,
) -> np.ndarray:
    h, w = plate.shape[:2]
    return warp(plate, cover_window(w, h, z, cx, cy, out_w, out_h))


def legacy_window_sample(
    plate: np.ndarray,
    z: float,
    cx: float,
    cy: float,
    out_w: int = OUT_W,
    out_h: int = OUT_H,
) -> np.ndarray:
    """Float resample of the first cut's window (plate aspect, then fit).

    The first cut took ``int`` bounds of ``(w/z, h/z)`` and resized. This
    keeps that window and drops the integer snap.
    """
    h, w = plate.shape[:2]
    cw, ch = w / z, h / z
    x0 = min(max(cx * w - cw / 2.0, 0.0), w - cw)
    y0 = min(max(cy * h - ch / 2.0, 0.0), h - ch)
    cam = Cover(z, cx, cy, x0, y0, cw, ch, w, h, out_w, out_h)
    return warp(plate, cam)
