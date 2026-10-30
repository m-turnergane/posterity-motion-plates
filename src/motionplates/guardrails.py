"""Shared motion guardrails (2026-10-30, after the water_v1 K11 shot-2 failure).

Provides crop-zoom and fire-sharpness checks for motion presets.
See docs/GUARDRAILS.md and docs/K11-FIRE-DIAGNOSIS.md for background.

Functions:
    check_crop_zoom(zoom, max_zoom=1.5)
        zoom = push/crop factor RELATIVE TO NATIVE COVER-FIT (1.0 = plate fills the frame).

    check_fire_sharpness(plate, rects, zoom)
        torch_v1c / water fire reflections only on sharp, native-resolution fire.

    check_shot(cfg, plate=None, mode="refuse")
        Convenience: push/crop zoom + fire rects from a shot config.

mode="refuse" raises GuardrailError; mode="warn" prints a WARNING to stderr
and returns the report. Pure numpy/cv2, no side effects.
"""
from __future__ import annotations
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

MAX_ZOOM = 1.5
FIRE_MIN_LAPVAR = 100.0
FIRE_MAX_ZOOM = 1.5


class GuardrailError(RuntimeError):
    """Raised when a guardrail check fails in refuse mode."""
    pass


LOCKED_WAIVERS = {
    "p05v2_sun_glitter_v1d": dict(
        zoom=1.6,
        reason="water_v1 reel shot 3 (sun glitter), LOCKED by owner 2026-10-30 4:53pm ET at a 1.6x static crop"
    ),
}


def _emit(
    ok: bool,
    msg: str,
    mode: str,
    rep: Dict[str, Any]
) -> Dict[str, Any]:
    rep["ok"] = bool(ok)
    rep["msg"] = "ok" if ok else msg
    if not ok:
        if mode == "refuse":
            raise GuardrailError(msg)
        print("WARNING guardrail: " + msg, file=sys.stderr)
    return rep


def output_px_per_plate_px(
    plate_wh: Tuple[int, int],
    out_wh: Tuple[int, int],
    zoom: float
) -> float:
    """Compute output pixels per plate pixel at a given zoom."""
    (W, H), (w, h) = plate_wh, out_wh
    return max(w / W, h / H) * zoom


def check_crop_zoom(
    zoom: Union[float, List[float], Tuple[float, ...]],
    max_zoom: float = MAX_ZOOM,
    mode: str = "refuse",
    plate_wh: Optional[Tuple[int, int]] = None,
    out_wh: Tuple[int, int] = (1080, 1920)
) -> Dict[str, Any]:
    """Check that zoom does not exceed max_zoom.

    Args:
        zoom: Scalar or [z0, z1] push endpoints; max is checked.
        max_zoom: Maximum allowed zoom (default 1.5x).
        mode: "refuse" raises GuardrailError, "warn" prints and continues.
        plate_wh: Optional (W, H) of the plate, to report output_px_per_plate_px.
        out_wh: Output size, default 1080x1920.

    Returns:
        Report dict with keys: check, zoom, max_zoom, ok, msg, and optionally
        output_px_per_plate_px.
    """
    z = float(max(zoom) if isinstance(zoom, (list, tuple)) else zoom)
    rep: Dict[str, Any] = dict(check="crop_zoom", zoom=z, max_zoom=max_zoom)
    if plate_wh:
        rep["output_px_per_plate_px"] = round(output_px_per_plate_px(plate_wh, out_wh, z), 3)
    return _emit(
        z <= max_zoom + 1e-9,
        f"zoom {z:.3f}x of native fill exceeds {max_zoom}x (plate is upscaled and goes soft)",
        mode,
        rep
    )


def lapvar(img: np.ndarray, rect: Tuple[int, int, int, int]) -> float:
    """Compute Laplacian variance of a region (sharpness metric)."""
    x0, y0, x1, y1 = [int(v) for v in rect[:4]]
    g = img[y0:y1, x0:x1]
    if g.ndim == 3:
        g = cv2.cvtColor(g, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(g.astype(np.float64), cv2.CV_64F).var()) if g.size else 0.0


def check_fire_sharpness(
    plate: np.ndarray,
    rects: List[Tuple[int, int, int, int]],
    zoom: Union[float, List[float], Tuple[float, ...]] = 1.0,
    min_lapvar: float = FIRE_MIN_LAPVAR,
    max_zoom: float = FIRE_MAX_ZOOM,
    mode: str = "refuse"
) -> Dict[str, Any]:
    """Check fire/torch rects for sharpness at native resolution.

    torch_v1c / water fire reflections run only on sharp, native-resolution fire.

    Args:
        plate: RGB uint8 at NATIVE res (never a resampled frame).
        rects: List of (x0, y0, x1, y1) fire/torch rectangles.
        zoom: Scalar or [z0, z1] push endpoints.
        min_lapvar: Minimum Laplacian variance (default 100).
        max_zoom: Maximum allowed zoom for fire effects (default 1.5x).
        mode: "refuse" raises GuardrailError, "warn" prints and continues.

    Returns:
        Report dict with keys: check, zoom, lapvar, min_lapvar, soft_rects,
        max_zoom, ok, msg.
    """
    z = float(max(zoom) if isinstance(zoom, (list, tuple)) else zoom)
    lv = [round(lapvar(plate, r), 1) for r in rects]
    soft = [i for i, v in enumerate(lv) if v < min_lapvar]
    rep = dict(
        check="fire_sharpness",
        zoom=z,
        lapvar=lv,
        min_lapvar=min_lapvar,
        soft_rects=soft,
        max_zoom=max_zoom
    )
    msgs = []
    if z > max_zoom + 1e-9:
        msgs.append(
            f"fire at {z:.3f}x zoom (> {max_zoom}x): "
            "torch_v1c / fire reflections run only on native-resolution fire"
        )
    if soft:
        msgs.append(f"soft fire rects {soft} (Laplacian var {[lv[i] for i in soft]} < {min_lapvar})")
    return _emit(not msgs, "; ".join(msgs) or "ok", mode, rep)


def check_shot(
    cfg: Dict[str, Any],
    plate: Optional[np.ndarray] = None,
    mode: str = "refuse",
    out_wh: Tuple[int, int] = (1080, 1920)
) -> List[Dict[str, Any]]:
    """Check a shot config for crop-zoom and fire-sharpness guardrails.

    Args:
        cfg: Shot config dict with keys: push [z0, z1], crop_zoom (optional),
             fire.torch (optional list of rects), name (optional).
        plate: RGB uint8 plate image at native resolution.
        mode: "refuse" raises GuardrailError, "warn" prints and continues.
        out_wh: Output size, default (1080, 1920).

    Returns:
        List of report dicts from check_crop_zoom and optionally check_fire_sharpness.
    """
    z = max(float(v) for v in cfg.get("push", (1.0, 1.0))) * float(cfg.get("crop_zoom", 1.0))
    wh = (plate.shape[1], plate.shape[0]) if plate is not None else None

    wv = LOCKED_WAIVERS.get(cfg.get("name"))
    if wv and abs(z - wv["zoom"]) < 1e-6:
        print(
            f"WARNING guardrail: {cfg.get('name')} zoom {z}x > {MAX_ZOOM}x WAIVED ({wv['reason']})",
            file=sys.stderr
        )
        mode = "warn"

    reps = [check_crop_zoom(z, mode=mode, plate_wh=wh, out_wh=out_wh)]

    if wv and abs(z - wv["zoom"]) < 1e-6:
        reps[0]["waived"] = wv["reason"]

    if cfg.get("fire") and plate is not None:
        reps.append(check_fire_sharpness(
            plate,
            cfg["fire"].get("torch", []),
            z,
            mode=mode
        ))

    return reps
