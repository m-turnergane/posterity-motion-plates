"""fx_torch -- torch_v1c LOCKED treatment for torches, cressets, braziers and larger fires.

LOCKED 2026-10-30 by owner. This is the house torch standard, exactly as shipped in the
Edward II v3b ROUGH v1c master. The v3 flames work "was distorting the things around it";
this treatment is "more like a pulsing effect".

Design principles (torch_v1c rules):
1. Painted flame shape holds: no tongue, no warp, no displacement
2. Soft local glow and spill pulse at v1c strength
3. Surroundings stay visually steady: no moving or warping
4. No strong pulsing waves or moving light gradients on walls/faces
5. Glow zones fixed: the whole room brightens and dims together with one brightness value

Scope: torches, cressets, braziers, and all larger fires (burning buildings, town fires).
Candles keep their own treatment (fx_candle preset plus smoke_v2 wisps).

Reference:
- Master: renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4 (md5 b4f0aa7a68619ed5928738698f6e2eaf)
- Source: standalones/edward-ii/edit/fx_v1c.py (md5 f31394f82a890b94d7670b009e984ce8)

Dependencies: numpy, opencv-python.
"""
from __future__ import annotations
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np


def pnoise(
    rng: np.random.Generator,
    h: int,
    w: int,
    lo: float,
    hi: float,
    beta: float = 2.0,
    ax: float = 1.0,
    ay: float = 1.0,
) -> np.ndarray:
    """Seamless (periodic) fractal noise, zero mean / unit std."""
    fy = np.fft.fftfreq(h)[:, None] * ay
    fx = np.fft.rfftfreq(w)[None, :] * ax
    f = np.sqrt(fx * fx + fy * fy)
    amp = (f * f + (1.0 / lo) ** 2) ** (-beta / 4) * np.exp(-(f * hi) ** 2)
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) * amp
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.mean()
    return n / (n.std() + 1e-8)


def scroll(tex: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """dst(x,y) = tex(x+dx, y+dy) with wrap -> content appears to move by (-dx,-dy)."""
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(
        tex, M, (tex.shape[1], tex.shape[0]),
        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP
    )


def smoothstep(a: float, b: float, x: np.ndarray) -> np.ndarray:
    x = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return x * x * (3 - 2 * x)


def lum(img: np.ndarray) -> np.ndarray:
    return (0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]) / 255.0


def gauss_dot(
    img: np.ndarray,
    x: float, y: float,
    sigma: float,
    col: Tuple[float, ...],
    gain: float,
    allow: Optional[np.ndarray] = None,
) -> None:
    H, W = img.shape[:2]
    R = int(math.ceil(sigma * 3)) + 1
    xi, yi = int(round(x)), int(round(y))
    x0, x1, y0, y1 = max(0, xi - R), min(W, xi + R + 1), max(0, yi - R), min(H, yi + R + 1)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma * sigma)) * gain
    if allow is not None:
        d *= allow[y0:y1, x0:x1]
    img[y0:y1, x0:x1] += d[..., None] * np.float32(col)


# ------------------------------------------------------------------------------------------------
# LOCKED parameters from house-candle-lightspill-v1 (torch_v1c uses same base with torch-specific mults)
# ------------------------------------------------------------------------------------------------

LOCK_FLICKER = dict(
    amps=[0.15, 0.08, 0.035, 0.015],
    freqs=[0.55, 1.3, 2.6, 4.4],
    noise=0.05,
    noise_hz=4.0,
    floor=0.45,
)

LOCK_PLATE_FLAME = dict(
    gain=0.6,
    hot=[255, 238, 190],
)

LOCK_POOL = dict(
    r0=520,
    power=2.2,
    dark=0.22,
    breathe=0.7,
    tint=[1.0, 0.95, 0.9],
)

LOCK_SPILL = dict(
    radius=800,
    power=2.0,
    amp=1.35,
    tint=[1.0, 0.8, 0.5],
    offset=[0, -14],
    facing_floor=0.45,
    warm_weight=0.65,
    grad_weight=0.35,
)

# torch_v1c spill is local to each source to avoid whole-frame pumping
LOCAL = 0.32


def _rectmask(
    shape: Tuple[int, int],
    rects: Optional[List] = None,
    feather: float = 0,
    polys: Optional[List] = None,
) -> np.ndarray:
    """Create mask from rectangles and/or polygons."""
    m = np.zeros(shape, np.float32)
    for r in rects or []:
        x0, y0, x1, y1 = r[:4]
        m[max(0, y0):y1, max(0, x0):x1] = 1
    for p in polys or []:
        cv2.fillPoly(m, [np.int32(p)], 1.0)
    if feather:
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


def _L(a: np.ndarray) -> np.ndarray:
    """Compute luminance."""
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def blob(P: np.ndarray, rect: Tuple[int, int, int, int], kind: str) -> Optional[Dict[str, Any]]:
    """Create blob mask for torch/window flames.
    
    Flame key for torch: lo = (L >= max(140, 0.55*Lmax)) & (R >= 170) inside the source rect;
    mask = dilate 3x3 then Gaussian sigma 1.6.
    """
    x0, y0, x1, y1 = rect
    a = P[y0:y1, x0:x1].astype(np.float32)
    L = _L(a)
    Lm = float(L.max())
    if kind == "torch":
        core = L >= 0.85 * Lm
        lo = (L >= max(140.0, 0.55 * Lm)) & (a[..., 0] >= 170)
    else:  # window
        core = L >= 0.85 * Lm
        lo = L >= max(90.0, 0.55 * Lm)
    n, lab = cv2.connectedComponents(lo.astype(np.uint8), connectivity=8)
    keep = np.isin(lab, np.unique(lab[core & (lab > 0)])) if n > 1 else lo
    if kind == "torch":
        keep = lo
    m = cv2.GaussianBlur(
        cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32),
        (0, 0), 1.6 if kind == "torch" else 1.0
    )
    ys, xs = np.nonzero(keep)
    if len(ys) == 0:
        return None
    cyc, cxc = np.nonzero(core)
    cx = x0 + float(cxc.mean()) if len(cxc) else x0 + float(xs.mean())
    return dict(
        bb=(x0, y0, x1, y1),
        mask=m.astype(np.float32),
        x=cx,
        base=float(y0 + ys.max() + 1),
        h=float(ys.max() - ys.min() + 1),
        w=float(xs.max() - xs.min() + 1),
    )


def mk_flick(rng: np.random.Generator, ampx: float = 1.0) -> Dict[str, Any]:
    """Create a flicker state dict with randomized phases.
    
    For torches: ampx = 1.5 (vs 1.35 for candles).
    """
    return dict(
        amps=[a * ampx for a in LOCK_FLICKER["amps"]],
        fq=np.float32(LOCK_FLICKER["freqs"]) * rng.uniform(0.85, 1.15, 4),
        fr=rng.uniform(0, 6.28, 4),
        noise=rng.standard_normal(4096),
        nz=LOCK_FLICKER["noise"] * ampx,
        nhz=LOCK_FLICKER["noise_hz"],
        floor=LOCK_FLICKER["floor"],
    )


def flick(F: Dict[str, Any], t: float) -> float:
    """Evaluate flicker at time t.
    
    f = max(0.45, 1 + Σ(amp*sin(2π*freq*t + phase)) + noise).
    Highest component 4.4 Hz, so nothing strobes.
    """
    a = 0.0
    for amp, f, ph in zip(F["amps"], F["fq"], F["fr"]):
        a += amp * math.sin(2 * math.pi * f * t + ph)
    i = t * F["nhz"]
    j = int(i) % 4095
    fr = i - int(i)
    fr = fr * fr * (3 - 2 * fr)
    return max(F["floor"], 1 + a + F["nz"] * (F["noise"][j] * (1 - fr) + F["noise"][j + 1] * fr))


class TorchFX:
    """torch_v1c treatment for torches, cressets, braziers and larger fires.
    
    LOCKED 2026-10-30. The painted flame shape holds; glow and spill pulse together
    so the whole room brightens and dims coherently without moving gradients.
    
    Args:
        plate_path: Path to the plate image.
        spec: Per-plate specification dict with keys:
            - torch: List of (x0, y0, x1, y1) rects for torch flames
            - window: List of rects for window flames (optional)
            - offscreen: List of {xy, h, radius, kind} for off-screen sources (optional)
            - relight_exclude: List of rects to exclude from relight (optional)
            - relight_poly: List of polygon point lists to exclude (optional)
            - spill_amp: Spill amplitude multiplier (default 1.8)
            - groups: Max number of spill groups (default 8)
            - pool: Whether to apply light pool breathing (optional)
            - window_amp: Window amplitude multiplier (optional, default 1.0)
            - radius_mult: Radius multiplier (optional, default 1.0)
            - embers: List of {spawn, n} ember specifications (optional)
            - haze/mist/motes: Atmosphere specs (optional)
        pulse: Per-plate pulse calibration (default 1.0).
        seed: RNG seed (default 0).
    """

    def __init__(
        self,
        plate_path: Union[str, Path],
        spec: Dict[str, Any],
        pulse: float = 1.0,
        seed: int = 0,
    ):
        self.key = Path(plate_path).stem.split("_")[0]
        self.sp = spec
        self.P = np.asarray(cv2.cvtColor(cv2.imread(str(plate_path)), cv2.COLOR_BGR2RGB))
        H, W = self.P.shape[:2]
        self.H, self.W = H, W
        self.Pf = self.P.astype(np.float32)
        rng = np.random.default_rng(1326 + seed + sum(map(ord, self.key)))
        
        self.srcs: List[Dict[str, Any]] = []
        
        # Torches: the primary scope of torch_v1c
        for r in spec.get("torch", []):
            s = blob(self.P, tuple(r), "torch")
            if s:
                s["kind"] = "torch"
                self.srcs.append(s)
        
        # Windows (ambient light sources)
        for r in spec.get("window", []):
            s = blob(self.P, tuple(r), "window")
            if s:
                s["kind"] = "window"
                self.srcs.append(s)
        
        # Offscreen sources
        for o in spec.get("offscreen", []):
            self.srcs.append(dict(
                kind="offscreen", x=o["xy"][0], base=o["xy"][1],
                h=o["h"], w=o["h"] / 2, bb=None, mask=None,
                radius=o["radius"] * 0.6
            ))
        
        wa = spec.get("window_amp", 1.0)
        rm = spec.get("radius_mult", 1.0)
        
        for s in self.srcs:
            k = s["kind"]
            # Torch amplitude = 1.5 (vs 1.35 for candles, 0.8 for windows)
            s["F"] = mk_flick(rng, {"torch": 1.5, "offscreen": 1.5, "window": 0.8 * wa}[k])
            s["ftex"] = pnoise(rng, 256, 64, 18, 2, ay=1.8)
            hn = s["h"] / 26.0
            if "radius" not in s:
                if k == "torch":
                    # torch_v1c reach: 800 × 1.3 × LOCAL × clip(h/26, 0.5, 3)^0.5
                    s["radius"] = LOCK_SPILL["radius"] * 1.3 * LOCAL * float(np.clip(hn, 0.5, 3.0)) ** 0.5 * rm
                else:  # window
                    s["radius"] = 40.0 * float(np.clip(hn, 0.5, 2)) / max(rm, 1e-3) * rm
            s["weight"] = float(np.clip(hn, 0.25, 2.5)) ** 0.5 if k != "window" else 0.5
        
        self._prep_spill(rng)
        self._prep_atmos(rng)
        self._prep_embers(rng)
        self.pulse = pulse

    def _prep_spill(self, rng: np.random.Generator) -> None:
        """Prepare grouped light-spill maps (locked falloff × facing × relight mask)."""
        sp = self.sp
        H, W = self.H, self.W
        S = [s for s in self.srcs]
        self.groups: List[Dict[str, Any]] = []
        self.lm = np.zeros((H, W), np.float32)
        self.pool: Optional[Dict[str, Any]] = None
        if not S:
            return
        
        G = min(sp.get("groups", 8), len(S))
        pts = np.float32([[s["x"], s["base"]] for s in S])
        
        # K-means clustering for spill groups
        cen = [pts[0]]
        for _ in range(1, G):
            d = np.min([((pts - c) ** 2).sum(1) for c in cen], 0)
            cen.append(pts[int(d.argmax())])
        cen = np.float32(cen)
        for _ in range(12):
            lab = np.argmin(((pts[:, None] - cen[None]) ** 2).sum(-1), 1)
            cen = np.float32([pts[lab == g].mean(0) if (lab == g).any() else cen[g] for g in range(G)])
        
        # Relight mask
        rel = 1 - _rectmask((H, W), sp.get("relight_exclude"), 0, sp.get("relight_poly"))
        rel = np.clip(cv2.GaussianBlur(rel, (0, 0), 14), 0, 1) * rel
        rel = cv2.GaussianBlur(rel, (0, 0), 6)
        
        # Facing heuristic
        Lp = lum(self.Pf)
        warm = np.clip((self.Pf[..., 0] - self.Pf[..., 2]) / 255.0 * 2, 0, 1)
        lit = smoothstep(0.02, 0.35, Lp) * (0.5 + 0.5 * warm)
        Lb = cv2.GaussianBlur(Lp, (0, 0), 6.0)
        gx = cv2.Sobel(Lb, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(Lb, cv2.CV_32F, 0, 1, ksize=3)
        gm = np.sqrt(gx * gx + gy * gy)
        gw = np.clip(gm / (np.percentile(gm, 95) + 1e-6), 0, 1)
        
        q4 = 4
        Hq, Wq = (H + q4 - 1) // q4, (W + q4 - 1) // q4
        Yq, Xq = np.mgrid[0:Hq, 0:Wq].astype(np.float32) * q4
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        amp = sp.get("spill_amp", 1.8)  # torch default is 1.8
        off = np.float32(LOCK_SPILL["offset"])
        
        for g in range(G):
            mem = [S[i] for i in range(len(S)) if lab[i] == g]
            if not mem:
                continue
            keep = np.ones((Hq, Wq), np.float32)
            for s in mem:
                d = np.sqrt((Xq - s["x"] - off[0]) ** 2 + (Yq - (s["base"] - s["h"] * 0.5) - off[1]) ** 2)
                keep *= 1 - np.clip(s["weight"], 0, 1) / (1 + (d / s["radius"]) ** LOCK_SPILL["power"])
            fall = cv2.resize(1 - keep, (W, H), interpolation=cv2.INTER_LINEAR)
            wsum = sum(s["weight"] for s in mem)
            lx = sum(s["x"] * s["weight"] for s in mem) / wsum
            ly = sum((s["base"] - s["h"] * 0.5) * s["weight"] for s in mem) / wsum
            d = np.sqrt((X - lx) ** 2 + (Y - ly) ** 2) + 1e-3
            gd = (gx * (lx - X) / d + gy * (ly - Y) / d) / (gm + 1e-4)
            gterm = 0.5 + 0.5 * gd * gw
            facing = LOCK_SPILL["facing_floor"] + (1 - LOCK_SPILL["facing_floor"]) * np.clip(
                LOCK_SPILL["warm_weight"] * lit + LOCK_SPILL["grad_weight"] * gterm, 0, 1
            )
            self.groups.append(dict(mem=mem, map=(amp * fall * facing * rel).astype(np.float32), k=min(math.sqrt(len(mem)), 2.5)))
            self.lm = np.maximum(self.lm, fall)
        
        self.lm = (self.lm / max(self.lm.max(), 1e-6)).astype(np.float32)
        
        if sp.get("pool"):
            main = max(S, key=lambda s: s["h"] if s["kind"] == "torch" else 0)
            self.pool = dict(
                src=main,
                d=np.sqrt((X - main["x"]) ** 2 + (Y - main["base"]) ** 2).astype(np.float32),
                rel=rel
            )

    def _prep_atmos(self, rng: np.random.Generator) -> None:
        """Prepare haze/mist layers (screen-blend light, no displacement)."""
        sp = self.sp
        H, W = self.H, self.W
        self.layers: List[Dict[str, Any]] = []
        mex = 1 - _rectmask((H, W), sp.get("mist_exclude"), 10)
        
        for kind in ("haze", "mist"):
            for L in sp.get(kind, []):
                feather = L.get("feather", 60 if kind == "haze" else 30)
                m = _rectmask((H, W), [L["rect"]], feather) * (mex if kind == "mist" else 1)
                if kind == "mist" and L.get("color") is None:
                    x0, y0, x1, y1 = L["rect"]
                    c = self.Pf[y0:y1, x0:x1].reshape(-1, 3)
                    c = np.percentile(c, 80, 0)
                    col = np.clip(c * 1.25 + 18, 0, 255)
                else:
                    col = np.float32(L["color"])
                lo = L.get("lo", 150) / 4.0
                Hq = 1 << int(math.ceil(math.log2((H // 4 + 1))))
                Wq = 1 << int(math.ceil(math.log2((W // 4 + 1))))
                T1 = pnoise(rng, Hq, Wq, lo, lo * 0.18, beta=2.6, ax=0.55)
                T2 = pnoise(rng, Hq, Wq, lo * 0.6, lo * 0.12, beta=2.6, ax=0.7)
                self.layers.append(dict(
                    kind=kind, m=m.astype(np.float32), col=np.float32(col),
                    op=L["opacity"], v=L["v"], T1=T1, T2=T2, lit=L.get("lit", False)
                ))
        
        self.motes: List[Dict[str, Any]] = []
        for M in sp.get("motes", []):
            n = M["n"]
            x0, y0, x1, y1 = M["rect"]
            if M.get("light") == "shaft":
                sx0, sy0, sx1, sy1, fe = M["shaft"]
                lmap = np.zeros((H, W), np.float32)
                lmap[sy0:sy1, sx0:sx1] = 1
                lmap = cv2.GaussianBlur(lmap, (0, 0), fe / 2)
                lmap /= max(lmap.max(), 1e-6)
                lmap = np.clip(lmap * 1.3, 0, 1)
            else:
                lmap = None
            self.motes.append(dict(
                q=M,
                x=rng.uniform(x0, x1, n), y=rng.uniform(y0, y1, n),
                vx=rng.uniform(-4, 4, n), vy=rng.uniform(-6, 2, n),
                ax=rng.uniform(2, 9, n), ay=rng.uniform(2, 7, n),
                wx=rng.uniform(0.05, 0.25, n), wy=rng.uniform(0.04, 0.2, n),
                ph=rng.uniform(0, 6.28, (n, 3)), tw=rng.uniform(0.3, 1.2, n),
                sz=rng.uniform(*M["size"], n), br=rng.uniform(0.35, 1.0, n), lmap=lmap
            ))

    def _prep_embers(self, rng: np.random.Generator) -> None:
        """Prepare torch embers (rise with sway and flicker)."""
        self.embers: List[Dict[str, Any]] = []
        for Em in self.sp.get("embers", []):
            n = Em["n"]
            spn = np.float32(Em["spawn"])
            k = rng.integers(0, len(spn), n)
            ang = rng.uniform(0, 6.28, n)
            rad = np.sqrt(rng.uniform(0, 1, n))
            ep = dict(
                x=spn[k, 0] + np.cos(ang) * rad * spn[k, 2],
                y=spn[k, 1] + np.sin(ang) * rad * spn[k, 3],
                v=rng.uniform(25, 70, n), life=rng.uniform(1.2, 2.6, n),
                sw=rng.uniform(0.3, 1.0, n) * 8, sf=rng.uniform(0.4, 1.4, n),
                ph=rng.uniform(0, 6.28, n), sz=rng.uniform(0.9, 1.7, n),
                br=rng.uniform(0.5, 1, n), fl=rng.uniform(5, 13, n)
            )
            ep["t0"] = rng.uniform(0, 1, n) * ep["life"]
            self.embers.append(ep)

    def info(self) -> Dict[str, Any]:
        """Return summary of the plate's sources and effects."""
        from collections import Counter
        c = Counter(s["kind"] for s in self.srcs)
        return dict(
            plate=self.key,
            sources=dict(c),
            spill_groups=len(self.groups),
            haze=sum(1 for L in self.layers if L["kind"] == "haze"),
            mist=sum(1 for L in self.layers if L["kind"] == "mist"),
            motes=sum(len(m["x"]) for m in self.motes),
            embers=sum(len(e["x"]) for e in self.embers),
            pool=bool(self.pool),
            pulse=self.pulse,
        )

    def active(self) -> bool:
        return bool(self.srcs or self.layers or self.motes or self.embers)

    def render(self, t: float, want_disp: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, Dict[str, Any]]]:
        """Render a single frame at time t.
        
        torch_v1c has 0 px displacement everywhere: painted flame shape holds,
        glow zones fixed. Returns RGB uint8 array (H, W, 3).
        
        If want_disp=True, also returns a dict with warp_max_px (always 0 for torch_v1c).
        """
        img = self.Pf.copy()
        fs = [flick(s["F"], t) for s in self.srcs]

        # Light pool breathing (optional)
        if self.pool:
            P = self.pool
            f = flick(P["src"]["F"], t)
            R = LOCK_POOL["r0"] * 1.3 * (1 + LOCK_POOL["breathe"] * 0.35 * (f - 1))
            litp = 1.0 / (1 + (P["d"] / R) ** LOCK_POOL["power"])
            dk = LOCK_POOL["dark"] * (1 - litp) * P["rel"]
            img *= (1 - dk[..., None] * np.float32(LOCK_POOL["tint"]))

        # Grouped spill: one scalar pulse per group (no moving gradients)
        sig = []
        for G in self.groups:
            dl = sum(flick(s["F"], t) - 1.0 for s in G["mem"]) / len(G["mem"]) * G["k"] * self.pulse
            sig.append(dl)
            img *= 1 + (G["map"] * dl)[..., None] * np.float32(LOCK_SPILL["tint"])
        smean = float(np.mean(sig)) if sig else 0.0

        # Painted flame gain (shape holds: no tongue, no remap)
        hot = np.float32(LOCK_PLATE_FLAME["hot"])
        for s, f in zip(self.srcs, fs):
            if s["mask"] is None:
                continue
            x0, y0, x1, y1 = s["bb"]
            fm = s["mask"][..., None]
            roi = img[y0:y1, x0:x1]
            gain = LOCK_PLATE_FLAME["gain"] if s["kind"] == "torch" else 0.5
            g = np.clip(gain * (f - 1), -0.5, 0.6)
            mod = np.where(g > 0, roi + (hot - roi) * np.clip(g, 0, 1) * 0.6 + roi * g * 0.2, roi * (1 + g))
            roi[...] = roi * (1 - fm) + mod * fm

        # Glow (halo) for each source
        col = np.float32([255, 165, 80])
        for s, f in zip(self.srcs, fs):
            k = s["kind"]
            if k == "offscreen":
                continue
            if k == "torch":
                # Torch glow: sigma = clip(0.9*h, 20, 120), gain 0.18
                sg = float(np.clip(0.9 * s["h"], 20, 120))
                gn = 0.18
            else:  # window
                sg = float(np.clip(1.6 * s["h"], 8, 40))
                gn = 0.12 * self.sp.get("window_amp", 1.0)
            gauss_dot(img, s["x"], s["base"] - s["h"] * 0.5, sg, col,
                      gn * 2.0 * min(1.0, max(self.pulse, 0.6)) * (f - 1.0))

        np.clip(img, 0, 255, out=img)

        # Atmosphere (screen blends; no displacement)
        for L in self.layers:
            v = L["v"]
            T = 0.62 * scroll(L["T1"], v[0] * t / 4, v[1] * t / 4) + 0.38 * scroll(L["T2"], v[0] * 1.7 * t / 4, v[1] * 1.4 * t / 4 + 0.6 * t)
            T = cv2.resize(T[:self.H // 4 + 1, :self.W // 4 + 1], (self.W, self.H), interpolation=cv2.INTER_LINEAR)
            a = L["op"] * np.clip(0.45 + 0.45 * T, 0, 1.2) * L["m"]
            if L["lit"]:
                a = a * (0.35 + 0.65 * self.lm) * (1 + 0.9 * smean)
            img[...] = 255 - (255 - img) * (1 - a[..., None] * L["col"] / 255.0)

        # Motes
        for M in self.motes:
            q = M["q"]
            x0, y0, x1, y1 = q["rect"]
            w, h = x1 - x0, y1 - y0
            px = x0 + (M["x"] - x0 + M["vx"] * t + M["ax"] * np.sin(2 * math.pi * M["wx"] * t + M["ph"][:, 0])) % w
            py = y0 + (M["y"] - y0 + M["vy"] * t + M["ay"] * np.sin(2 * math.pi * M["wy"] * t + M["ph"][:, 1])) % h
            edge = np.clip(np.minimum.reduce([px - x0, x1 - px, py - y0, y1 - py]) / 30.0, 0, 1)
            lm = M["lmap"] if M["lmap"] is not None else self.lm
            li = lm[np.clip(py.astype(int), 0, self.H - 1), np.clip(px.astype(int), 0, self.W - 1)]
            br = q["gain"] * M["br"] * li * edge * (0.55 + 0.45 * np.sin(2 * math.pi * M["tw"] * t + M["ph"][:, 2])) * (1 + 0.8 * smean if q.get("light") == "lm" else 1)
            for x, y, b, sz in zip(px, py, br, M["sz"]):
                if b > 2:
                    gauss_dot(img, x, y, sz * 0.8, np.float32(q["color"]) / 255.0, b)

        # Embers
        for ep in self.embers:
            age = (t + ep["t0"]) % ep["life"]
            k = age / ep["life"]
            px = ep["x"] + 6 * age + ep["sw"] * np.sin(ep["ph"] + age * ep["sf"] * 2 * math.pi) * k
            py = ep["y"] - ep["v"] * age
            br = ep["br"] * np.sin(math.pi * k) ** 0.6 * (0.7 + 0.3 * np.sin(ep["fl"] * t * 2 * math.pi + ep["ph"]))
            for x, y, b, sz in zip(px, py, br, ep["sz"]):
                gauss_dot(img, x, y, sz * 0.7, (255, 170, 80), b * 0.9)
                gauss_dot(img, x, y + sz * 1.2, sz * 0.6, (255, 170, 80), b * 0.35)

        np.clip(img, 0, 255, out=img)
        out = np.clip(img + 0.5, 0, 255).astype(np.uint8)

        if want_disp:
            return out, dict(warp_max_px=0.0)  # torch_v1c: 0 px displacement everywhere
        return out
