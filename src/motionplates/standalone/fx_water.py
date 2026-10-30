"""fx_water -- LIGHT ON WATER only. The sea never moves. (LOCKED 2026-10-30 4:53pm ET)

Owner rules: the water surface is completely still, with no displacement, warp, ripple,
flow or coastline warp. Only the LIGHT on the water changes:

  * glints: FIXED sites (the plate's own painted specular points, detected once from
    the original plate). Each site brightens and dims IN PLACE on its own smooth clock
    (components <= 2.4 Hz). There's a multiplicative lift on the site's own painted
    pixels plus a static additive stamp (core + short horizontal star + soft halo).
    Its shape never moves; only its brightness scalar changes.

  * breathe: a STATIC reflection-column map (sun/moon path) times one slow scalar per
    frame (<= 0.3 Hz).

  * fire_reflection: a STATIC warm-reflection map, split into per-fire columns. Each
    column is driven by that fire's own flick curve (the same per-frame curve that
    drives the source glow), so the fire and its reflection brighten and dim together.

  * fire: the source fire itself gets the LOCKED torch_v1c treatment. When fire is
    enabled, it requires fx_torch (PR #3) or an external fire renderer.

Mattes: every change is multiplied by a feathered ALLOW map (water matte, plus the fire
zone for fire shots). Every protect polygon (and everything outside the allow area) is
then forced back to the plate, so it is 0 px changed. Nothing is ever resampled before
the optional camera framing (push_frame), so the impulse proof is exact.

Three modes:
  1. Moon path - cool tinted breathe + glints (nm4a_moon_path)
  2. Sun glitter - warm tinted breathe + glints (p05v2_sun_glitter)
  3. Fire reflections - fire_reflection columns synced to torch_v1c + fire-clock glints

Dependencies: numpy, opencv-python. Fire mode requires fx_torch.py (PR #3) or external
fire renderer injection.

See docs/WATER-V1.md for full documentation.
"""
from __future__ import annotations
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import cv2
import numpy as np

from ..effects.smoke_v2 import keepout_fade, load_plate, push_frame, ffmpeg_writer
from .fx_candle import flick, mk_flick

cv2.setNumThreads(4)


def L_of(a: np.ndarray) -> np.ndarray:
    """Compute luminance from RGB array."""
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def poly_mask(shape: Tuple[int, int], polys: Optional[List] = None) -> np.ndarray:
    """Create a binary mask from a list of polygons."""
    m = np.zeros(shape, np.uint8)
    for p in polys or []:
        cv2.fillPoly(m, [np.int32(p)], 1)
    return m > 0


class Twinkle:
    """Per-site brightness clock: a smooth sum of 2 sines.

    f1 in rate_lo, f2 in rate_hi, mapped to [0, 1], then shaped by a soft threshold
    and power so each site rests dim and peaks briefly. A peak lasts about 0.25-0.6 s,
    so the clock stays smooth at 30 fps. Returns per-site values in [0, 1].
    """

    def __init__(
        self,
        rng: np.random.Generator,
        n: int,
        rate_lo: Tuple[float, float] = (0.35, 0.9),
        rate_hi: Tuple[float, float] = (0.9, 2.2),
        thresh: float = 0.45,
        power: float = 1.6
    ):
        self.f1 = rng.uniform(*rate_lo, n)
        self.f2 = rng.uniform(*rate_hi, n)
        self.p1 = rng.uniform(0, 6.283, n)
        self.p2 = rng.uniform(0, 6.283, n)
        self.th = thresh
        self.pw = power

    def __call__(self, t: float) -> np.ndarray:
        c = 0.5 + 0.3 * np.sin(6.2832 * self.f1 * t + self.p1) + 0.2 * np.sin(6.2832 * self.f2 * t + self.p2)
        return np.clip((c - self.th) / (1 - self.th), 0, 1) ** self.pw


def breathe(t: float, hz: Tuple[float, float] = (0.12, 0.27), ph: Tuple[float, float] = (0.0, 1.3)) -> float:
    """Slow breathing scalar, range [-1, 1], components <= 0.3 Hz."""
    return 0.6 * math.sin(6.2832 * hz[0] * t + ph[0]) + 0.4 * math.sin(6.2832 * hz[1] * t + ph[1])


class WaterShot:
    """Light-on-water shot renderer.

    Args:
        cfg: Shot configuration dict with keys:
            - plate: Path to the plate image
            - water: List of polygon vertices defining water area
            - protect: List of polygon vertices to protect (0 change)
            - protect_feather: Feather distance for protect mask (default 6)
            - layers: List of layer configs (breathe, glints, fire_reflection)
            - fire: Optional fire config for torch_v1c integration
            - seed: Random seed (default 0)
        fire_fx_factory: Optional callable (plate_path, seed) -> fire renderer with
            .render(t, u) and .srcs attributes. Required for fire mode.
    """

    def __init__(
        self,
        cfg: Dict[str, Any],
        fire_fx_factory: Optional[Callable[[str, int], Any]] = None
    ):
        self.cfg = cfg
        self.P = load_plate(cfg["plate"])
        P = self.P
        H, W = P.shape[:2]
        self.H, self.W = H, W
        self.Pf = P.astype(np.float32)
        self.L0 = L_of(self.Pf)
        rng = np.random.default_rng(int(cfg.get("seed", 0)))

        self.water = poly_mask((H, W), cfg["water"]) & ~poly_mask((H, W), cfg.get("protect", []))

        self.fx = None
        self.fire_curve = None
        if cfg.get("fire"):
            self._prep_fire(cfg["fire"], fire_fx_factory)

        fz = poly_mask((H, W), cfg.get("fire_zone", []))
        zm = (cfg.get("fire") or {}).get("zone_from_masks")
        if zm and self.fx is not None:
            fm = np.zeros((H, W), np.uint8)
            for s_ in self.fx.srcs:
                if s_.get("mask") is None:
                    continue
                x0, y0, x1, y1 = s_["bb"]
                fm[y0:y1, x0:x1] |= (s_["mask"] > float(zm.get("thresh", 0.05))).astype(np.uint8)
            r_ = int(zm.get("dilate", 3))
            if r_ > 0:
                fm = cv2.dilate(fm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r_ + 1, 2 * r_ + 1)))
            fz = (fm > 0) & (fz if cfg.get("fire_zone") else True)
        self.fire_zone = fz

        allow = self.water | fz
        self.protect = ~allow
        self.keep = keepout_fade(self.protect.astype(np.uint8), float(cfg.get("protect_feather", 6)))
        self.water_keep = keepout_fade((~self.water).astype(np.uint8), float(cfg.get("protect_feather", 6)))

        self.layers: List[Dict[str, Any]] = []
        for Ly in cfg.get("layers", []):
            k = Ly["type"]
            if k == "glints":
                self.layers.append(self._prep_glints(Ly, rng))
            elif k == "breathe":
                self.layers.append(self._prep_breathe(Ly, rng))
            elif k == "fire_reflection":
                self.layers.append(self._prep_fire_refl(Ly))
            else:
                raise ValueError(f"Unknown layer type: {k}")

    def _path_w(self, pth: Dict[str, Any]) -> np.ndarray:
        """Compute path weight map (sun/moon column) in plate coords."""
        H, W = self.H, self.W
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        y0, y1 = pth["y"]
        w0, w1 = pth["w"]
        u = np.clip((Y - y0) / max(1, y1 - y0), 0, 1)
        w = w0 + (w1 - w0) * u
        cx = pth["x"] + (pth.get("x_bot", pth["x"]) - pth["x"]) * u
        return (np.exp(-((X - cx) / w) ** 2) * (Y >= y0 - 2)).astype(np.float32)

    def _prep_glints(self, g: Dict[str, Any], rng: np.random.Generator) -> Dict[str, Any]:
        H, W = self.H, self.W
        L = self.L0
        hp = L - cv2.GaussianBlur(L, (0, 0), g.get("hp_sigma", 5.0))
        reg = cv2.erode(self.water.astype(np.uint8), np.ones((2 * g.get("edge_px", 6) + 1,) * 2, np.uint8)) > 0
        if g.get("region"):
            reg &= poly_mask((H, W), g["region"])
        pw = self._path_w(g["path"]) if g.get("path") else np.ones((H, W), np.float32)
        md = int(g.get("min_dist", 9))
        mx = cv2.dilate(hp, np.ones((2 * md + 1, 2 * md + 1), np.uint8))
        cand = (hp >= mx) & (hp > g.get("thresh", 12.0)) & reg & (pw > g.get("path_min", 0.08)) & (L > g.get("lum_min", 0))
        ys, xs = np.nonzero(cand)
        sc = hp[ys, xs] * (pw[ys, xs] ** g.get("path_bias", 1.0))
        o = np.argsort(-sc)[: int(g.get("n_max", 120))]
        ys, xs = ys[o], xs[o]

        sg = float(g.get("sigma", 2.2))
        star = float(g.get("star_len", 10))
        halo = float(g.get("halo_sigma", 6.0))
        R = int(max(3 * sg, star, 3 * halo)) + 2
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
        stamp = (
            np.exp(-(xx ** 2 + yy ** 2) / (2 * sg * sg)) +
            g.get("star", 0.5) * np.exp(-(xx / max(star, 1)) ** 2 * 2.5 - (yy / 1.1) ** 2) +
            g.get("halo", 0.15) * np.exp(-(xx ** 2 + yy ** 2) / (2 * halo * halo))
        ).astype(np.float32)

        sites = []
        for y, x in zip(ys, xs):
            y0, y1, x0, x1 = max(0, y - R), min(H, y + R + 1), max(0, x - R), min(W, x + R + 1)
            st = stamp[y0 - y + R: y1 - y + R, x0 - x + R: x1 - x + R] * self.water_keep[y0:y1, x0:x1]
            own = np.clip(hp[y0:y1, x0:x1] / max(hp[y, x], 1e-3), 0, 1) * (
                np.hypot(*np.mgrid[y0 - y:y1 - y, x0 - x:x1 - x]) <= g.get("own_r", 4)
            )
            own = (own * self.water_keep[y0:y1, x0:x1]).astype(np.float32)
            sites.append(dict(y=int(y), x=int(x), bb=(y0, y1, x0, x1), st=st, own=own, w=float(pw[y, x])))

        tw = Twinkle(
            rng, len(sites),
            tuple(g.get("rate_lo", (0.35, 0.9))),
            tuple(g.get("rate_hi", (0.9, 2.2))),
            g.get("thresh_t", 0.45),
            g.get("power", 1.6)
        )
        clock = g.get("clock", "twinkle")
        return dict(
            type="glints", g=g, sites=sites, tw=tw, clock=clock,
            col=np.float32(g.get("color", (255, 236, 200)))
        )

    def _prep_breathe(self, b: Dict[str, Any], rng: np.random.Generator) -> Dict[str, Any]:
        H, W = self.H, self.W
        pw = self._path_w(b["path"])
        L = self.L0
        lit = np.clip(
            (cv2.GaussianBlur(L, (0, 0), 2.0) - b.get("lum_lo", 60)) /
            max(1, b.get("lum_hi", 200) - b.get("lum_lo", 60)),
            0, 1
        )
        M = (pw * lit * self.water_keep).astype(np.float32)
        M /= max(float(M.max()), 1e-6)
        return dict(
            type="breathe", b=b, M=M[..., None],
            ph=tuple(rng.uniform(0, 6.283, 2)),
            col=np.float32(b.get("tint", (1, 1, 1)))
        )

    def _prep_fire(self, f: Dict[str, Any], fire_fx_factory: Optional[Callable]) -> None:
        """Prepare fire rendering via torch_v1c.

        This requires fx_torch (PR #3) or an external fire renderer factory.
        """
        if fire_fx_factory is None:
            try:
                from .fx_torch import PlateFX as TorchPlateFX
                from .fx_torch import SPECS as TORCH_SPECS
                from .fx_torch import PULSE as TORCH_PULSE

                def default_factory(plate_path: str, seed: int) -> Any:
                    key = Path(plate_path).stem.split("_")[0]
                    TORCH_SPECS[key] = dict(
                        torch=[tuple(r) for r in f["torch"]],
                        relight_poly=f.get("relight_exclude", []),
                        spill_amp=f.get("spill_amp", 1.8)
                    )
                    TORCH_PULSE[key] = float(f.get("pulse", 0.3))
                    return TorchPlateFX(plate_path, seed=seed)

                fire_fx_factory = default_factory
            except ImportError:
                raise ImportError(
                    "Fire mode requires fx_torch.py (torch_v1c). Either:\n"
                    "  1. Install PR #3 (cursor/torch-v1c-locked-preset-4fa6), or\n"
                    "  2. Provide a fire_fx_factory callable to WaterShot"
                )

        p = fire_fx_factory(self.cfg["plate"], int(f.get("seed", 0)))
        for s in p.srcs:
            s.pop("warp", None)
            if s["kind"] == "candle":
                s["kind"] = "torch"
        p.par = None
        p.smoke = []
        p.layers = []
        p.motes = []
        if not f.get("embers", False):
            p.embers = []
        assert np.array_equal(p.P, self.P), "fx plate != water plate"
        self.fx = p

    def _prep_fire_refl(self, r: Dict[str, Any]) -> Dict[str, Any]:
        assert self.fx is not None, "fire_reflection needs a fire block"
        H, W = self.H, self.W
        a = self.Pf
        L = self.L0
        reg = self.water & (poly_mask((H, W), r["region"]) if r.get("region") else True)
        warm = np.clip(
            (a[..., 0] - a[..., 2] - r.get("warm_lo", 30)) /
            max(1, r.get("warm_hi", 90) - r.get("warm_lo", 30)),
            0, 1
        )
        lit = np.clip(
            (L - r.get("lum_lo", 70)) /
            max(1, r.get("lum_hi", 170) - r.get("lum_lo", 70)),
            0, 1
        )
        M = cv2.GaussianBlur((warm * lit * reg).astype(np.float32), (0, 0), r.get("soften", 1.0)) * self.water_keep
        X = np.arange(W, dtype=np.float32)[None, :]
        srcs = self.fx.srcs
        cols = []
        for s in srcs:
            wd = max(float(s["w"]) * r.get("col_w", 0.6), r.get("col_min_px", 8.0))
            cols.append(np.exp(-((X - float(s["x"])) / wd) ** 2))
        C = np.stack([np.broadcast_to(c, (H, W)) for c in cols]) if cols else np.zeros((0, H, W), np.float32)
        den = np.maximum(C.sum(0), 1e-6)
        Wn = C / den
        reach = np.clip(C.max(0) / 0.2, 0, 1)
        self.refl_reach = (M * reach).astype(np.float32)
        return dict(type="fire_reflection", r=r, M=(M * reach).astype(np.float32), Wn=Wn.astype(np.float32))

    def fire_flicks(self, t: float) -> np.ndarray:
        """Get per-source flicker values at time t."""
        return np.float32([flick(s["F"], self.t_fire(t)) for s in self.fx.srcs])

    def t_fire(self, t: float) -> float:
        """Map water time to fire time (with t0 offset)."""
        return float(self.cfg.get("fire", {}).get("t0", 6.0)) + t

    def frame(self, t: float) -> np.ndarray:
        """Render a single frame at time t."""
        img = self.Pf.copy()
        flicks = None

        if self.fx is not None:
            img = self.fx.render(self.t_fire(t), 0.0).astype(np.float32)
            flicks = self.fire_flicks(t)

        for Ly in self.layers:
            k = Ly["type"]
            if k == "breathe":
                b = Ly["b"]
                v = breathe(t, tuple(b.get("hz", (0.12, 0.27))), Ly["ph"]) * b.get("amp", 0.08)
                img *= 1 + Ly["M"] * v * Ly["col"]
            elif k == "fire_reflection":
                r = Ly["r"]
                d = (flicks - 1.0) * self.fx.pulse * r.get("gain", 1.0)
                s = np.tensordot(d, Ly["Wn"], axes=1) * Ly["M"]
                img *= 1 + s[..., None] * np.float32(r.get("tint", (1.0, 0.92, 0.8)))
                if r.get("add", 0):
                    img += (np.clip(s, 0, None) * r["add"])[..., None] * np.float32(r.get("add_color", (255, 170, 90)))
            elif k == "glints":
                g = Ly["g"]
                if Ly["clock"] == "fire":
                    v = np.clip(
                        (np.mean(flicks) - 1.0) * self.fx.pulse * g.get("fire_k", 3.0) + 0.5,
                        0, 1
                    ) * Ly["tw"](t) ** 0.5
                else:
                    v = Ly["tw"](t)
                lift = g.get("lift", 0.6)
                dim = g.get("dim", 0.25)
                add = g.get("add", 0.5)
                col = Ly["col"]
                for s, a in zip(Ly["sites"], v):
                    y0, y1, x0, x1 = s["bb"]
                    roi = img[y0:y1, x0:x1]
                    ww = s["w"] ** g.get("w_power", 0.5)
                    m = (lift * a - dim * (1 - a)) * ww
                    roi *= 1 + (s["own"] * m)[..., None]
                    if a > 0:
                        roi += (s["st"] * (add * a * ww))[..., None] * col

        np.clip(img, 0, 255, out=img)
        o = self.P.astype(np.float32) + (img - self.P) * self.keep[..., None]
        out = np.clip(o + 0.5, 0, 255).astype(np.uint8)
        out[self.protect] = self.P[self.protect]
        return out

    def set_plate_for_proof(self, Pf: np.ndarray) -> None:
        """Swap the plate for impulse proofs."""
        self.Pf = Pf
        if self.fx is not None:
            self.fx.Pf = Pf

    def info(self) -> Dict[str, Any]:
        """Return shot info dict."""
        d = dict(
            plate=self.cfg["plate"],
            water_px=int(self.water.sum()),
            allow_px=int((~self.protect).sum()),
            protect_px=int(self.protect.sum())
        )
        for Ly in self.layers:
            if Ly["type"] == "glints":
                d.setdefault("glint_sites", []).append(len(Ly["sites"]))
        if self.fx is not None:
            d["fire"] = self.fx.info()
            d["fire_pulse"] = self.fx.pulse if hasattr(self.fx, "pulse") else None
        return d


def out_size(cfg: Dict[str, Any], size: Optional[str] = None) -> Tuple[int, int]:
    """Parse output size from config or argument."""
    s = size or cfg.get("size", "1080x1920")
    w, h = map(int, s.split("x"))
    return w, h


def render(
    cfg: Dict[str, Any],
    out: str,
    seconds: Optional[float] = None,
    size: Optional[str] = None,
    crf: Optional[int] = None,
    writer: Optional[subprocess.Popen] = None,
    fps: int = 30,
    fire_fx_factory: Optional[Callable] = None
) -> None:
    """Render a water shot to video.

    Args:
        cfg: Shot config dict.
        out: Output video path.
        seconds: Duration in seconds (default from config).
        size: Output size as "WxH" (default from config).
        crf: Video quality (default from config).
        writer: Optional existing ffmpeg subprocess.
        fps: Frame rate (default 30).
        fire_fx_factory: Optional fire renderer factory.
    """
    sh = WaterShot(cfg, fire_fx_factory=fire_fx_factory)
    w, h = out_size(cfg, size)
    n = int(round((seconds or cfg.get("seconds", 5.0)) * fps))
    z0, z1 = cfg.get("push", (1.0, 1.0))
    c = tuple(cfg.get("push_center", (0.5, 0.5)))
    p = writer or ffmpeg_writer(out, w, h, fps, crf=int(crf or cfg.get("crf", 24)))
    print("shot", cfg.get("name"), json.dumps(sh.info(), default=str), file=sys.stderr, flush=True)
    for i in range(n):
        p.stdin.write(push_frame(sh.frame(i / fps), i / max(n - 1, 1), w, h, z0, z1, center=c).tobytes())
    if writer is None:
        p.stdin.close()
        assert p.wait() == 0


def _cfg(path: str) -> Dict[str, Any]:
    """Load config from JSON file."""
    c = json.load(open(path))
    c.setdefault("name", Path(path).stem)
    return c


def proof(
    cfg: Dict[str, Any],
    out_json: str,
    times: Optional[List[float]] = None,
    fire_fx_factory: Optional[Callable] = None
) -> Dict[str, Any]:
    """Run impulse and protect proofs.

    (1) impulse proof: +-24 impulses on an isolated 9-px grid added to the plate the
    renderer reads. Render the same t with and without them. Any resampling would spread
    an impulse, so it PASSES only if the difference is non-zero solely on impulse pixels.

    (2) protect proof: changed px vs the plate inside protect (land, sky, ships, people,
    coast, everything outside water + fire zone) = 0.

    (3) water-only proof for the light layers: changes outside water + fire zone = 0.
    """
    sh = WaterShot(cfg, fire_fx_factory=fire_fx_factory)
    P = sh.P
    H, W = P.shape[:2]
    times = times or [0.0, 0.5, 1.0, 1.7, 2.4, 3.1, 4.0]

    G = np.zeros((H, W), bool)
    G[4::9, 4::9] = True
    sgn = np.where(P[G].mean(-1) > 128, -24, 24).astype(np.float32)
    Pf0 = sh.Pf.copy()
    Pf1 = Pf0.copy()
    Pf1[G] += sgn[:, None]

    r: Dict[str, Any] = dict(
        name=cfg["name"], plate=cfg["plate"], times=times,
        impulses=int(G.sum()), leaked_px_total=0,
        impulse_live_changed_min_frac=1.0,
        protect_px=int(sh.protect.sum()),
        protect_changed_px=[], allow_changed_px=[],
        changed_frac_of_frame=[], max_abs_diff_in_allow=[]
    )
    live = G & ~sh.protect

    for t in times:
        sh.set_plate_for_proof(Pf0)
        a = sh.frame(t).astype(int)
        sh.set_plate_for_proof(Pf1)
        b = sh.frame(t).astype(int)
        d = np.abs(a - b).max(-1) > 0
        r["leaked_px_total"] += int((d & ~G).sum())
        r["impulse_live_changed_min_frac"] = min(
            r["impulse_live_changed_min_frac"],
            round(float(d[live].mean()), 4) if live.any() else 1.0
        )
        ch = np.abs(a - P.astype(int)).max(-1)
        r["protect_changed_px"].append(int((ch[sh.protect] > 0).sum()))
        r["allow_changed_px"].append(int((ch[~sh.protect] > 0).sum()))
        r["changed_frac_of_frame"].append(round(float((ch > 0).mean()), 5))
        r["max_abs_diff_in_allow"].append(int(ch[~sh.protect].max()))

    sh.set_plate_for_proof(Pf0)
    r["pass_impulse_0px"] = r["leaked_px_total"] == 0
    r["pass_protect_0px"] = max(r["protect_changed_px"]) == 0
    r["pass"] = r["pass_impulse_0px"] and r["pass_protect_0px"]

    with open(out_json, "x") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r))
    return r


def phone(img: np.ndarray) -> np.ndarray:
    """Resize to phone resolution (360x640)."""
    return cv2.resize(img, (360, 640), interpolation=cv2.INTER_AREA)


def luma(img: np.ndarray) -> np.ndarray:
    """Compute luminance."""
    return 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


def series_stats(v: np.ndarray, fps: int = 30, win: float = 1.0, step: float = 0.5) -> Dict[str, Any]:
    """Compute statistics for a time series."""
    v = np.asarray(v, np.float64)
    n = int(win * fps)
    sw = []
    for i in range(0, len(v) - n + 1, int(step * fps)):
        w = v[i:i + n]
        sw.append((w.max() - w.min()) / max(w.mean(), 1e-6))
    st = np.abs(np.diff(v)) / max(v.mean(), 1e-6)
    x = v - v.mean()
    P = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / fps)
    return dict(
        swing_1s_median_pct=round(100 * float(np.median(sw)), 2),
        swing_1s_max_pct=round(100 * float(np.max(sw)), 2),
        max_step_pct=round(100 * float(st.max()), 3),
        energy_above_5hz=round(float(P[f > 5].sum() / max(P[1:].sum(), 1e-12)), 4)
    )


def stats(
    cfg: Dict[str, Any],
    out_json: str,
    seconds: float = 4.0,
    fps: int = 30,
    fire_fx_factory: Optional[Callable] = None
) -> Dict[str, Any]:
    """Compute phone-size (360x640) measurements in the framed output.

    Reported: whole frame; water (phone-mapped matte); the brightest 'active'
    water px (top 2% of temporal std); a readability score; and per-site glint
    swing (median over sites).
    """
    sh = WaterShot(cfg, fire_fx_factory=fire_fx_factory)
    w, h = out_size(cfg)
    n = int(seconds * fps)
    z0, z1 = cfg.get("push", (1.0, 1.0))
    c = tuple(cfg.get("push_center", (0.5, 0.5)))

    def fr(im: np.ndarray, i: int) -> np.ndarray:
        return phone(push_frame(im, i / max(n - 1, 1), w, h, z0, z1, center=c))

    wm = fr(np.repeat(sh.water[..., None].astype(np.uint8) * 255, 3, -1), 0)[..., 0] > 127
    seq = np.stack([luma(fr(sh.frame(i / fps), i)) for i in range(n)]).astype(np.float32)
    base = luma(fr(sh.P, 0)).astype(np.float32)
    sd = seq.std(0)
    act = wm & (sd >= np.quantile(sd[wm], 0.98)) if wm.any() else wm

    r: Dict[str, Any] = dict(
        name=cfg["name"], seconds=seconds, phone="360x640",
        whole_frame=series_stats(seq.mean((1, 2)), fps),
        water=series_stats(seq[:, wm].mean(1), fps) if wm.any() else None,
        active_water_top2pct=series_stats(seq[:, act].mean(1), fps) if act.any() else None,
        phone_px_changed_ge8_levels_any_frame=int(((np.abs(seq - base[None]) >= 8).any(0)).sum()),
        phone_px_changed_ge8_levels_within_1s=int(((seq[:30].max(0) - seq[:30].min(0)) >= 8).sum()),
        phone_px_outside_water_changed_ge2=int((
            ((np.abs(seq - base[None]) >= 2).any(0)) &
            ~cv2.dilate(wm.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        ).sum())
    )

    if sh.fx is not None:
        fl = [float(np.mean(sh.fire_flicks(i / fps))) for i in range(n)]
        refl = [l for l in sh.layers if l["type"] == "fire_reflection"]
        if refl:
            rm = fr(np.repeat((refl[0]["M"] > 0.2)[..., None].astype(np.uint8) * 255, 3, -1), 0)[..., 0] > 127
            fz = fr(
                np.repeat(poly_mask(sh.P.shape[:2], cfg.get("fire_zone", []))[..., None].astype(np.uint8) * 255, 3, -1),
                0
            )[..., 0] > 127
            rs = seq[:, rm].mean(1) if rm.any() else None
            fs = seq[:, fz].mean(1) if fz.any() else None
            r["fire_reflection_px_phone"] = int(rm.sum())
            r["fire_reflection"] = series_stats(rs, fps) if rs is not None else None
            r["fire_source_zone"] = series_stats(fs, fps) if fs is not None else None
            if rs is not None and fs is not None:
                r["corr_reflection_vs_source_luma"] = round(float(np.corrcoef(rs, fs)[0, 1]), 3)
                r["corr_reflection_vs_flick_curve"] = round(float(np.corrcoef(rs, fl)[0, 1]), 3)

    with open(out_json, "x") as f:
        json.dump(r, f, indent=1)
    print(json.dumps(r))
    return r


def overlay(cfg: Dict[str, Any], out_png: str, fire_fx_factory: Optional[Callable] = None) -> None:
    """Generate overlay visualization of mattes, sites and columns."""
    sh = WaterShot(cfg, fire_fx_factory=fire_fx_factory)
    im = cv2.cvtColor(sh.P, cv2.COLOR_RGB2BGR).copy()
    o = im.copy()
    o[sh.protect] = (o[sh.protect] * 0.45 + np.float32([255, 60, 60]) * 0.55).astype(np.uint8)
    o[sh.water] = (o[sh.water] * 0.75 + np.float32([60, 255, 60]) * 0.25).astype(np.uint8)

    for Ly in sh.layers:
        if Ly["type"] == "glints":
            for s in Ly["sites"]:
                cv2.circle(o, (s["x"], s["y"]), 4, (0, 255, 255), 1)
        if Ly["type"] in ("breathe", "fire_reflection"):
            M = Ly["M"][..., 0] if Ly["M"].ndim == 3 else Ly["M"]
            o[M > 0.25] = (o[M > 0.25] * 0.5 + np.float32([0, 140, 255]) * 0.5).astype(np.uint8)

    if sh.fx is not None:
        for s in sh.fx.srcs:
            if s.get("bb"):
                x0, y0, x1, y1 = s["bb"]
                cv2.rectangle(o, (x0, y0), (x1, y1), (0, 0, 255), 1)

    cv2.imwrite(out_png, np.hstack([im, o]))
    w, h = out_size(cfg)
    z0, _ = cfg.get("push", (1.0, 1.0))
    c = tuple(cfg.get("push_center", (0.5, 0.5)))
    ph = [phone(push_frame(cv2.cvtColor(x, cv2.COLOR_BGR2RGB), 0.0, w, h, z0, z0, center=c)) for x in (im, o)]
    cv2.imwrite(out_png.replace(".png", "_phone.png"), cv2.cvtColor(np.hstack(ph), cv2.COLOR_RGB2BGR))


def reel(
    reel_json: str,
    out: str,
    fps: int = 30,
    fire_fx_factory: Optional[Callable] = None
) -> None:
    """Render a reel of multiple shots."""
    with open(reel_json) as f:
        R = json.load(f)
    w, h = map(int, R.get("size", "1080x1920").split("x"))
    p = ffmpeg_writer(out, w, h, fps, crf=int(R.get("crf", 24)))
    cfg_dir = Path(reel_json).parent
    for s in R["shots"]:
        cfg = _cfg(str(cfg_dir / s["config"]))
        cfg.update({k: v for k, v in s.items() if k != "config"})
        render(cfg, out, seconds=s["seconds"], size=f"{w}x{h}", writer=p, fire_fx_factory=fire_fx_factory)
    p.stdin.close()
    assert p.wait() == 0
