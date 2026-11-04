"""House candle spill and smoke on a locked delivery frame.

Effects run after the single plate resample. Flame warp stays inside the
flame rect. Torches keep their painted shape and only flicker, spill, and
smoke. An offscreen candle spills light and does not move the paper.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from motionplates.effects.smoke_v2 import SmokeScene
from motionplates.opening.camera import Cover
from motionplates.standalone.fx_candle import PlateFX


def _clip_rect(rect: tuple[int, int, int, int], w: int, h: int) -> tuple[int, int, int, int] | None:
    x0, y0, x1, y1 = rect
    x0, x1 = max(0, min(w - 1, x0)), max(0, min(w, x1))
    y0, y1 = max(0, min(h - 1, y0)), max(0, min(h, y1))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return None
    return x0, y0, x1, y1


def _map_rect(cam: Cover, rect: tuple[float, float, float, float], w: int, h: int):
    x0, y0, x1, y1 = rect
    ax, ay = cam.to_frame(x0, y0)
    bx, by = cam.to_frame(x1, y1)
    return _clip_rect(
        (int(round(min(ax, bx))), int(round(min(ay, by))), int(round(max(ax, bx))), int(round(max(ay, by)))),
        w,
        h,
    )


def _map_point(cam: Cover, xy: tuple[float, float]) -> tuple[float, float]:
    return cam.to_frame(xy[0], xy[1])


class HouseLight:
    """One shot's candle/torch spill and smoke, seeded and plate-locked."""

    def __init__(self, frame: np.ndarray, spec: dict, seed: int, work: Path, key: str):
        self.base = np.ascontiguousarray(frame)
        self.fx = None
        self.smoke = None
        h, w = frame.shape[:2]
        cam: Cover = spec["cam"]
        candles = []
        torches = []
        for rect in spec.get("candles", []):
            mapped = _map_rect(cam, rect, w, h)
            if mapped:
                candles.append(mapped)
        for rect in spec.get("torches", []):
            mapped = _map_rect(cam, rect, w, h)
            if mapped:
                torches.append(mapped)
        offscreen = []
        for src in spec.get("offscreen", []):
            x, y = _map_point(cam, tuple(src["xy"]))
            offscreen.append({
                "xy": [float(x), float(y)],
                "h": float(src.get("h", 70)),
                "radius": float(src.get("radius", 900)),
                "kind": "torch",
            })
        plate_spec = {
            "manual": candles,
            "torch": torches,
            "offscreen": offscreen,
            "spill_amp": float(spec.get("spill_amp", 0.55)),
            "radius_mult": float(spec.get("radius_mult", 0.55)),
            "groups": int(spec.get("groups", 4)),
            "pulse": float(spec.get("pulse", 0.85)),
        }
        if spec.get("relight_exclude"):
            plate_spec["relight_exclude"] = spec["relight_exclude"]
        if candles or torches or offscreen:
            work.mkdir(parents=True, exist_ok=True)
            path = work / f"{key}.png"
            cv2.imwrite(str(path), cv2.cvtColor(self.base, cv2.COLOR_RGB2BGR))
            self.fx = PlateFX(str(path), plate_spec, seed=seed)
        emitters = []
        for i, src in enumerate(spec.get("smoke", [])):
            x, y = _map_point(cam, tuple(src["src"]))
            if x < -40 or y < -40 or x > w + 40 or y > h + 40:
                continue
            item = {
                "type": src.get("type", "candle"),
                "src": [float(x), float(y)],
                "seed": seed + 17 * (i + 1),
            }
            for name in ("height", "w0", "w1", "opacity", "lean", "meander", "rise", "swirl"):
                if name in src:
                    item[name] = src[name]
            emitters.append(item)
        protect = []
        for poly in spec.get("protect", []):
            protect.append([_map_point(cam, tuple(p)) for p in poly])
        if emitters:
            self.smoke = SmokeScene(self.base, {
                "seed": seed,
                "preroll": 8.0,
                "protect": protect,
                "protect_feather": float(spec.get("protect_feather", 22)),
                "emitters": emitters,
            })

    @property
    def active(self) -> bool:
        return self.fx is not None or self.smoke is not None

    def render(self, t: float) -> np.ndarray:
        img = self.fx.render(t) if self.fx is not None else self.base
        if self.smoke is not None:
            self.smoke.Pf = np.ascontiguousarray(img, dtype=np.float32)
            img = self.smoke.frame(t)
        return img
