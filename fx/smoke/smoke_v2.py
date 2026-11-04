"""smoke_v2 -- procedural smoke overlay + painted-smoke billow for still painted plates (Posterity engine R&D).

The plate NEVER moves.  Smoke is a semi-transparent layer composited on top:
  * density = multi-octave periodic noise, advected upward and domain-warped by a slowly
    evolving curl (swirl) field, so shapes billow and morph instead of rigidly scrolling;
  * each emitter has its own plume envelope: narrow at the source, widening and thinning as it
    rises, with a wandering centre line;
  * distant columns can be stacked in 2-3 depth layers at different speeds / scales;
  * fire glow lights the smoke from below on a smooth flicker clock;
  * nothing loops: textures are much taller than the distance scrolled in a shot, and the octaves
    scroll at incommensurate speeds;
  * no fade-in: the sim is PRE-ROLLED (`preroll` s, default 8) so smoke is fully established at
    frame 0; an emitter that starts mid-shot (`start`) grows physically from its source upward
    (a rising front), and one that stops (`end`) is cut off at the source and its tail rises away.
v2 adds:
  * Billow: painted smoke already in the plate churns and rises INSIDE a smoke matte built from
    colour + luminance + region polygons (feathered).  Displacements are bounded by the distance to
    the region edge, so no pixel is ever pulled in from outside the region (land, sea, buildings).
  * soft keep-out around `protect` polygons (distance-based fade instead of a hard cut);
  * candle laminar->turbulent wisps, denser painterly columns, depth-varied glow;
  * reduced-resolution rendering for big soft layers (speed);
  * multi-shot reel rendering (--reel);
  * `fires`: automatic fire/ember detection on the plate -> one emitter per fire, sized to the fire;
  * `push_center`: anchor of the 1.00->1.06 push (keeps an edge subject in frame).
Pixels outside the smoke footprint / matte (and always inside `protect`) are bit-exact copies of
the plate; `zero_motion_report()` proves it.  smoke_v1.py is kept unchanged for the PoC.

Dependencies: numpy, opencv-python, ffmpeg (on PATH).  No other project code is imported.

CLI:
  python smoke_v2.py --config CFG.json --out OUT.mp4 [--seconds 8] [--preview 360] [--proof] [--grab G.png]
  python smoke_v2.py --reel REEL.json --out REEL.mp4
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import cv2

# ----------------------------------------------------------------------------------------- noise helpers
def periodic_noise(rng, h, w, lo, hi, beta=2.2, ax=1.0, ay=1.0):
    """Seamless fractal noise (h, w), zero mean / unit std. lo = largest feature px, hi = smallest."""
    fy = np.fft.fftfreq(h)[:, None] * ay
    fx = np.fft.rfftfreq(w)[None, :] * ax
    f = np.sqrt(fx * fx + fy * fy)
    amp = (f * f + (1.0 / lo) ** 2) ** (-beta / 4) * np.exp(-(f * hi) ** 2)
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) * amp
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.mean()
    return n / (n.std() + 1e-8)


def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return x * x * (3 - 2 * x)


def ease(t, t0, t1):
    return float(smoothstep(t0, t1, np.float32(t)))


class Flicker:
    """Smooth, non-repeating fire flicker f(t) ~ 1 +/- amp (sum of cubic-interpolated random walks)."""
    def __init__(self, rng, amp=0.18, rates=(1.3, 3.7, 8.9)):
        self.amp, self.rates = amp, rates
        self.tab = [rng.standard_normal(8192).astype(np.float32) for _ in rates]
        self.w = np.float32([0.55, 0.30, 0.15])

    def __call__(self, t):
        v = 0.0
        for tab, r, w in zip(self.tab, self.rates, self.w):
            i = t * r; j = int(i) % 8190; fr = i - int(i); fr = fr * fr * (3 - 2 * fr)
            v += w * (tab[j] * (1 - fr) + tab[j + 1] * fr)
        return 1.0 + self.amp * v


def poly_mask(shape, polys, feather=0.0):
    m = np.zeros(shape, np.float32)
    for p in polys or []:
        cv2.fillPoly(m, [np.int32(np.round(np.float32(p)))], 1.0)
    if feather > 0 and m.any():
        m = cv2.GaussianBlur(m, (0, 0), feather)
    return m


# ----------------------------------------------------------------------------------------- emitter presets
PRESETS = {
    # snuffed-candle smoke: a thin laminar ribbon that breaks into soft curls higher up
    "candle": dict(height=260, w0=2.0, w1=30.0, lean=0.0, rise=34.0, opacity=0.6, lo=60, hi=4.0,
                   swirl=8.0, laminar=0.3, meander=0.5, thin=1.8, color_dark=[160, 156, 150], color_light=[205, 200, 194],
                   layers=1, detail=0.35, breakup=0.3, edge=(0.04, 0.95), relief=0.12, res=1.0, glow=None),
    # torch smoke: denser, warm and lit near the source, curling as it climbs
    "torch": dict(height=380, w0=10.0, w1=110.0, lean=0.0, rise=48.0, opacity=0.72, lo=80, hi=3.0,
                  swirl=16.0, laminar=0.12, meander=0.35, thin=1.1, color_dark=[46, 40, 38], color_light=[120, 112, 108],
                  layers=1, detail=0.45, breakup=0.42, edge=(0.1, 0.8), relief=0.24, res=0.75,
                  glow=dict(color=[255, 150, 70], strength=0.7, reach=0.3, flicker=0.25, patch=0.35)),
    # big burning-city column: thick dark smoke, cauliflower billows, 2-3 depth layers
    "column": dict(height=700, w0=40.0, w1=260.0, lean=0.0, rise=30.0, opacity=0.92, lo=150, hi=14.0,
                   swirl=8.0, laminar=0.05, meander=0.22, thin=0.7, color_dark=[24, 18, 20], color_light=[70, 58, 64],
                   layers=2, detail=0.15, breakup=0.55, edge=(0.12, 0.62), relief=0.42, res=0.5, puffs=0.8, body=1.15,
                   glow=dict(color=[255, 118, 46], strength=0.6, reach=0.16, flicker=0.25, patch=0.5)),
    # low ground haze: horizontal band drifting sideways
    "haze": dict(rect=None, drift=10.0, opacity=0.35, lo=220, hi=6.0, swirl=18.0, feather=40.0,
                 color_dark=[150, 140, 135], color_light=[190, 180, 172], glow=None, res=0.5),
}

BILLOW_DEFAULTS = dict(
    region=None,          # list of polygons (plate px): where painted smoke may be animated
    exclude=None,         # polygons carved out of the region (buildings, spires, ...)
    luma=(0.0, 0.55),     # smoke = luminance (0-1) inside this window ...
    sat_max=0.55,         # ... and saturation below this
    soft=0.08,            # softness of the colour/luma key
    grow=6,               # px the keyed smoke is grown so its edges can move over the sky
    feather=5.0,          # gaussian feather of the matte
    edge_feather=14.0,    # inward fade at the region boundary (matte is exactly 0 outside the region)
    amp=9.0,              # curl-warp amplitude px
    scale=110.0,          # curl feature size px
    rise=12.0,            # flow-map advection speed px/s (content drifts upward)
    period=2.6,           # flow-map cycle s (two phases, spatially staggered -> no pumping)
    shade=0.07,           # rising light modulation inside the smoke
)


def keepout_fade(protect_bin, feather):
    """0 inside (and 2 px around) the protected shapes, smoothly -> 1 at `feather` px away."""
    if not protect_bin.any():
        return np.ones(protect_bin.shape, np.float32)
    d = cv2.distanceTransform((protect_bin < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    return smoothstep(2.0, max(3.0, feather), d).astype(np.float32)


class Emitter:
    """One smoke source in plate pixel space.  Precomputes its footprint, textures and envelopes.
    Big soft layers render on a coarse grid (`res` < 1) and are upsampled; the keep-out mask is applied
    at full resolution so protected pixels stay exact."""

    TEX_H, TEX_W = 2048, 512   # tall periodic textures: rise*duration << TEX_H so nothing repeats in a shot

    def __init__(self, spec, plate_shape, keep, rng):
        self.kind = spec.get("type", "candle")
        q = {**PRESETS[self.kind], **spec}
        self.q = q
        H, W = plate_shape
        if self.kind == "haze":
            self._init_haze(q, H, W, keep, rng)
        else:
            self._init_plume(q, H, W, keep, rng)
        self.flick = Flicker(rng, (q.get("glow") or {}).get("flicker", 0.2))

    def _grid(self, x0, y0, x1, y1):
        r = float(self.q.get("res", 1.0))
        gh, gw = max(2, int(round((y1 - y0) * r))), max(2, int(round((x1 - x0) * r)))
        ys = np.linspace(y0, y1 - 1, gh, dtype=np.float32); xs = np.linspace(x0, x1 - 1, gw, dtype=np.float32)
        self.gscale = (x1 - x0) / gw
        return np.meshgrid(xs, ys)   # xx, yy

    # ---- plume geometry
    def _init_plume(self, q, H, W, keep, rng):
        sx, sy = map(float, q["src"]); h = float(q["height"])
        pad = q["w1"] * 1.4 + abs(q["lean"]) + q["meander"] * q["w1"] + q["swirl"] * 2
        x0, x1 = int(max(0, sx - pad)), int(min(W, sx + pad + 1))
        y0, y1 = int(max(0, sy - h * 1.05)), int(min(H, sy + q["w0"] * 2 + 6))
        self.bb = (x0, y0, x1, y1)
        xx, yy = self._grid(x0, y0, x1, y1)
        self.s = ((sy - yy) / h).astype(np.float32)                         # 0 at source, 1 at top
        self.xx = xx
        self.sx, self.sy, self.h = sx, sy, h
        s = np.clip(self.s, 0, 1.2)
        self.width = (q["w0"] + (q["w1"] - q["w0"]) * s ** 0.85).astype(np.float32)
        self.venv = (smoothstep(-0.01, 0.06, self.s) * (1 - smoothstep(0.55, 1.0, self.s)) *
                     (1 - 0.55 * s) ** q["thin"]).astype(np.float32)
        self.clip = keep[y0:y1, x0:x1].astype(np.float32)
        th, tw = self.TEX_H, self.TEX_W
        lo, hi = q["lo"], q["hi"]
        self.T1 = periodic_noise(rng, th, tw, lo, hi * 2, ay=1.5)           # big billows
        self.T2 = periodic_noise(rng, th, tw, lo * 0.4, hi, ay=1.2)        # curly detail
        self.T3 = periodic_noise(rng, th, tw, lo * 0.6, lo * 0.08, ay=1.0) # cauliflower puffs (abs)
        self.T3 = np.abs(self.T3); self.T3 = (self.T3 - self.T3.mean()) / (self.T3.std() + 1e-6)
        self.G = periodic_noise(rng, 512, 512, lo * 1.2, lo * 0.2)          # glow patchiness
        psi = periodic_noise(rng, 1024, 512, lo * 0.9, lo * 0.15)          # stream function -> curl flow
        self.cu = cv2.Sobel(psi, cv2.CV_32F, 0, 1, ksize=5)
        self.cv = -cv2.Sobel(psi, cv2.CV_32F, 1, 0, ksize=5)
        sc = 1.0 / (np.abs(self.cu).std() + np.abs(self.cv).std() + 1e-6)
        self.cu *= sc; self.cv *= sc
        self.mtab = rng.standard_normal(4096).astype(np.float32)          # centre-line meander
        self.ph = float(rng.uniform(0, 400))

    def _init_haze(self, q, H, W, keep, rng):
        x0, y0, x1, y1 = q["rect"]
        f = q["feather"]
        X0, Y0, X1, Y1 = int(max(0, x0 - 2 * f)), int(max(0, y0 - 2 * f)), int(min(W, x1 + 2 * f)), int(min(H, y1 + 2 * f))
        self.bb = (X0, Y0, X1, Y1)
        m = np.zeros((Y1 - Y0, X1 - X0), np.float32); m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1
        self.env_full = cv2.GaussianBlur(m, (0, 0), f)
        self.clip = keep[Y0:Y1, X0:X1].astype(np.float32)
        r = float(q.get("res", 1.0))
        self.gsz = (max(2, int(round((X1 - X0) * r))), max(2, int(round((Y1 - Y0) * r))))
        self.env = cv2.resize(self.env_full, self.gsz, interpolation=cv2.INTER_AREA)
        lo, hi = q["lo"] * r, q["hi"]
        bt = float(q.get("beta", 2.2))   # higher = softer, less streaky haze
        self.T1 = periodic_noise(rng, 1024, 2048, lo, hi * 2, beta=bt, ax=0.45)
        self.T2 = periodic_noise(rng, 1024, 2048, lo * 0.45, hi, beta=bt, ax=0.6)
        self.r = r
        self.ph = float(rng.uniform(0, 500))
        self.s = None
        gw, gh = self.gsz; yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
        cxg, cyg = ((x0 + x1) / 2 - X0) * r, ((y0 + y1) / 2 - Y0) * r
        self.hd = np.sqrt((xx - cxg) ** 2 + ((yy - cyg) * 2.5) ** 2)   # haze growth distance (flattened)

    def _meander(self, s, t):
        """smooth wandering offset of the centre line in px, travelling upward with the smoke."""
        q = self.q
        i = (s * 3.0 - t * q["rise"] / self.h * 3.0) * 1.0 + self.ph
        i = np.mod(i, 4090.0); j = i.astype(np.int32); fr = i - j; fr = fr * fr * (3 - 2 * fr)
        n = self.mtab[j] * (1 - fr) + self.mtab[j + 1] * fr
        return q["meander"] * q["w1"] * np.clip(s, 0, None) ** 1.2 * n

    def render(self, t):
        """return (alpha (h,w), colour (h,w,3)) for this emitter's bounding box at time t (seconds),
        at full bbox resolution with the keep-out applied."""
        a, col = self._render_haze(t) if self.kind == "haze" else self._render_plume(t)
        a = a * self._life(t)
        x0, y0, x1, y1 = self.bb
        if a.shape != (y1 - y0, x1 - x0):
            a = cv2.resize(a, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
            col = cv2.resize(col, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
        return a * self.clip, col

    def _life(self, t):
        """start/end without any opacity fade.  Plumes: smoke exists only between a front that rises from
        the source at the plume's speed after `start`, and (after `end`) a tail that leaves the source
        and rises away.  Haze: spreads outward from its rect centre at `spread` px/s after `start`."""
        q = self.q; st, en = q.get("start"), q.get("end")
        if st is None and en is None:
            return 1.0
        if self.kind == "haze":
            if st is None:
                return 1.0
            r = max(0.0, t - st) * q.get("spread", 120.0) * self.r
            return 1.0 - smoothstep(r - 60 * self.r, r + 1e-3, self.hd)
        dist = self.s * self.h
        sp = q["rise"] * q.get("front_speed", 1.6)    # the head of a new plume climbs a bit faster than the drift
        soft = max(6.0, 0.12 * self.h)
        m = 1.0
        if st is not None:
            f = (t - st) * sp
            m = m * (1 - smoothstep(f - soft, f, dist)) if f > 0 else m * 0.0
        if en is not None and t > en:
            m = m * smoothstep((t - en) * sp, (t - en) * sp + soft, dist)
        return m

    # ---- density & colour
    def _render_plume(self, t):
        q = self.q
        s = self.s
        sc = np.clip(s, 0, 1.2)
        cx = self.sx + q["lean"] * sc ** 1.5 + self._meander(s[:, :1], t)      # per row
        across = (self.xx - cx) / self.width                                  # -1..1 inside plume
        u = across * q["w1"] * 0.5 + 256.0
        dist = s * self.h
        rise = q["rise"]
        cu_v = np.mod(dist * 0.5 - rise * 0.225 * t + self.ph, 1024).astype(np.float32)
        cu_u = np.mod(u * 0.5, 512).astype(np.float32)
        wu = cv2.remap(self.cu, cu_u, -cu_v % 1024, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        wv = cv2.remap(self.cv, cu_u, -cu_v % 1024, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        # laminar near the source, turbulence grows with height
        sw = q["swirl"] * smoothstep(0.0, max(q.get("laminar", 0.05), 1e-3), sc) * (0.35 + 0.65 * np.clip(sc, 0, 1))
        uu = np.mod(u + wu * sw, self.TEX_W).astype(np.float32)
        v1 = np.mod(-(dist - rise * t) + wv * sw + self.ph, self.TEX_H).astype(np.float32)
        v2 = np.mod(-(dist * 1.07 - rise * 1.38 * t) + wv * sw * 1.4 + self.ph * 1.7, self.TEX_H).astype(np.float32)
        T1 = cv2.remap(self.T1, uu, v1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        T2 = cv2.remap(self.T2, np.mod(uu * 1.3, self.TEX_W).astype(np.float32), v2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        N = 0.7 * T1 + q["detail"] * T2
        if q.get("puffs"):
            v3 = np.mod(-(dist * 0.93 - rise * 0.81 * t) + wv * sw * 0.8 + self.ph * 0.6, self.TEX_H).astype(np.float32)
            N = N + q["puffs"] * cv2.remap(self.T3, uu, v3, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        core = np.exp(-2.2 * across * across)
        e0, e1 = q.get("edge", (0.1, 0.85))
        D = smoothstep(e0, e1, core * q.get("body", 1.05) + q.get("breakup", 0.4) * N * np.sqrt(core) - 0.2) * self.venv
        D *= smoothstep(0.02, 0.35, core)
        a = np.clip(D * q["opacity"], 0, 0.97)
        mix = np.clip(sc * 1.1, 0, 1)[..., None]
        col = np.float32(q["color_dark"]) * (1 - mix) + np.float32(q["color_light"]) * mix
        Nb = cv2.GaussianBlur(N, (0, 0), max(1.0, q["lo"] * q.get("relief_blur", 0.05) / self.gscale))
        rel = cv2.Sobel(Nb, cv2.CV_32F, 1, 0, ksize=3) * 0.4 + cv2.Sobel(Nb, cv2.CV_32F, 0, 1, ksize=3)
        rel = np.tanh(rel / (np.abs(rel).mean() * 2.5 + 1e-6))
        col = col * (1 + 0.14 * np.clip(N, -2, 2) - q.get("relief", 0.22) * rel)[..., None]
        g = q.get("glow")
        if g:
            f = self.flick(t)
            # patchy glow: some billows catch more firelight than others (patches rise with the smoke)
            gp = cv2.remap(self.G, np.mod(uu, 512).astype(np.float32), np.mod(v1 * 0.8, 512).astype(np.float32),
                           cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            patch = np.clip(1 + g.get("patch", 0.0) * gp, 0.2, 2.0)
            # undersides (density rising above) catch more light than tops
            lit = np.exp(-np.clip(s, 0, None) / g["reach"]) * g["strength"] * f * (0.6 + 0.4 * core) * patch * (1 + 0.5 * np.clip(rel, 0, 1))
            col = col + (np.float32(g["color"]) - col * 0.4) * np.clip(lit, 0, 1)[..., None]
        return a.astype(np.float32), col.astype(np.float32)

    def _render_haze(self, t):
        q = self.q; w, h = self.gsz
        d = q["drift"] * self.r
        M1 = np.float32([[1, 0, self.ph + d * t], [0, 1, 0.0]])
        M2 = np.float32([[1, 0, self.ph * 0.7 + d * 1.6 * t], [0, 1, 3.0 * self.r * t]])
        T1 = cv2.warpAffine(self.T1, M1, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)
        T2 = cv2.warpAffine(self.T2, M2, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)
        N = 0.65 * T1 + 0.45 * T2
        a = np.clip(smoothstep(-0.9, 1.4, N) * self.env * q["opacity"], 0, 0.9)
        col = np.float32(q["color_dark"]) + (np.float32(q["color_light"]) - np.float32(q["color_dark"])) * smoothstep(-1.5, 1.5, N)[..., None]
        return a.astype(np.float32), col.astype(np.float32)


def _expand_layers(spec):
    """distant columns: one spec -> 1..3 depth layers (back layers bigger, slower, fainter, cooler, coarser)."""
    n = int(spec.get("layers", PRESETS[spec.get("type", "candle")].get("layers", 1)))
    if spec.get("type") == "haze" or n <= 1:
        return [spec]
    out = []
    base = {**PRESETS[spec["type"]], **spec}
    for k in range(n):
        f = [1.0, 0.62, 0.42][k]
        L = dict(base)
        L.update(layers=1, rise=base["rise"] * f, opacity=base["opacity"] * [1.0, 0.6, 0.42][k],
                 w1=base["w1"] * [1.0, 1.25, 1.5][k], height=base["height"] * [1.0, 1.08, 1.15][k],
                 lean=base["lean"] * [1.0, 1.3, 1.6][k], lo=base["lo"] * [1.0, 1.35, 1.7][k],
                 res=min(base.get("res", 1.0), [1.0, 0.4, 0.33][k]),
                 color_dark=[c + [0, 14, 26][k] for c in base["color_dark"]],
                 seed=int(spec.get("seed", 0)) * 7 + k)
        if base.get("glow"):
            g = dict(base["glow"]); g["strength"] = g["strength"] * [1.0, 0.55, 0.3][k]
            g["color"] = [c * m for c, m in zip(g["color"], [(1, 1, 1), (1.0, 0.85, 0.8), (0.9, 0.7, 0.65)][k])]
            g["reach"] = g["reach"] * [1.0, 1.4, 1.8][k]
            L["glow"] = g
        out.append(L)
    return out[::-1]   # draw back layers first


# ----------------------------------------------------------------------------------------- painted-smoke billow
def smoke_key(rgb, luma, sat_max, soft, dark_rel=None, rel_sigma=45.0):
    """soft 0..1 key of 'smoke-coloured' pixels: luminance inside `luma` window and low saturation.
    `dark_rel` = (a, b): additionally require the pixel to be darker than its blurred surroundings
    (local sky) by a..b luminance -- separates painted plumes from a sky of similar colour."""
    f = rgb.astype(np.float32) / 255.0
    L = f @ np.float32([0.299, 0.587, 0.114])
    mx, mn = f.max(-1), f.min(-1)
    S = (mx - mn) / (mx + 1e-4)
    kl = smoothstep(luma[0] - soft, luma[0] + soft, L) * (1 - smoothstep(luma[1] - soft, luma[1] + soft, L))
    ks = 1 - smoothstep(sat_max - soft, sat_max + soft, S)
    k = kl * ks
    if dark_rel:
        rel = cv2.GaussianBlur(L, (0, 0), rel_sigma) - L
        k = k * smoothstep(dark_rel[0], dark_rel[1], rel)
    return k.astype(np.float32)


class Billow:
    """Animate smoke that is already painted in the plate, strictly inside a smoke matte.

    matte = colour/luma key (cleaned, grown, feathered) x region polygons (faded inward from their edge),
    minus `exclude` and the scene `protect` polygons.  Outside the matte the plate is untouched.
    Motion = two-phase flow-map advection upward (phases staggered by a static noise field so the
    cross-fade never pulses globally) + an evolving curl warp + a rising light modulation.
    Every displacement is clamped to the distance from the region edge, so no pixel is ever sampled
    from outside the region (land / sea / buildings can't be smeared into the sky)."""

    def __init__(self, spec, plate, protect_bin, rng):
        q = {**BILLOW_DEFAULTS, **spec}; self.q = q
        H, W = plate.shape[:2]
        R = np.zeros((H, W), np.uint8)
        for p in q["region"]:
            cv2.fillPoly(R, [np.int32(np.round(np.float32(p)))], 1)
        for p in q.get("exclude") or []:
            cv2.fillPoly(R, [np.int32(np.round(np.float32(p)))], 0)
        R[protect_bin > 0.5] = 0
        ys, xs = np.nonzero(R)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        self.bb = (int(x0), int(y0), int(x1), int(y1))
        R = R[y0:y1, x0:x1]
        P = plate[y0:y1, x0:x1]
        dist = cv2.distanceTransform(R, cv2.DIST_L2, 5)
        K = smoke_key(P, q["luma"], q["sat_max"], q["soft"], q.get("dark_rel"), q.get("rel_sigma", 45.0))
        K = smoothstep(0.25, 0.75, cv2.GaussianBlur(K, (0, 0), 2.0))           # drop speckle / clean edges
        if q["grow"] > 0:
            g = int(q["grow"]) * 2 + 1
            K = cv2.dilate(K, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (g, g)))
        K = cv2.GaussianBlur(K, (0, 0), q["feather"])
        M = K * smoothstep(0.0, q["edge_feather"], dist)
        M[M < 1.0 / 255] = 0.0
        self.M = M.astype(np.float32)
        maxd = q["rise"] * q["period"] * 0.5 + q["amp"] * 1.6
        self.A = np.clip(dist / (maxd + 1e-6), 0, 1).astype(np.float32)      # displacement clamp
        h, w = R.shape
        self.Y, self.X = np.mgrid[0:h, 0:w].astype(np.float32)
        self.P = P.astype(np.float32)
        sc = q["scale"]
        self.phase = cv2.resize(smoothstep(-2, 2, periodic_noise(rng, 512, 512, 160, 40)).astype(np.float32), (w, h))
        psi = periodic_noise(rng, 1024, 1024, sc, sc * 0.2)
        self.cu = cv2.Sobel(psi, cv2.CV_32F, 0, 1, ksize=5); self.cv = -cv2.Sobel(psi, cv2.CV_32F, 1, 0, ksize=5)
        n = 1.0 / (self.cu.std() + self.cv.std() + 1e-6); self.cu *= n * 2; self.cv *= n * 2
        self.L = periodic_noise(rng, 1024, 1024, sc * 1.3, sc * 0.15)
        self.ph = float(rng.uniform(0, 500))

    def _tex(self, T, xo, yo):
        h, w = self.X.shape
        return cv2.remap(T, np.mod(self.X + xo, T.shape[1]).astype(np.float32), np.mod(self.Y + yo, T.shape[0]).astype(np.float32),
                         cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)

    def render(self, t, k=1.0):
        """return the billowed ROI (float32 RGB) and its matte (alpha, already scaled by ease k)."""
        q = self.q
        rise, per = q["rise"], q["period"]
        phase = self.phase
        # evolving curl: two copies drifting up at different speeds
        wu = 0.6 * self._tex(self.cu, self.ph, rise * 0.7 * t + self.ph) + 0.4 * self._tex(self.cu, -self.ph * 0.5 + 6 * t, rise * 1.3 * t)
        wv = 0.6 * self._tex(self.cv, self.ph, rise * 0.7 * t + self.ph) + 0.4 * self._tex(self.cv, -self.ph * 0.5 + 6 * t, rise * 1.3 * t)
        out = np.zeros_like(self.P)
        for j in (0.0, 0.5):
            p = np.mod(t / per + phase + j, 1.0)
            wgt = 1.0 - np.abs(2 * p - 1)                       # 0 at the wrap -> seamless
            dy = (p - 0.5) * rise * per + q["amp"] * wv
            dx = q["amp"] * wu
            mx = (self.X + dx * self.A).astype(np.float32); my = (self.Y + dy * self.A).astype(np.float32)
            out += cv2.remap(self.P, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) * wgt[..., None]
        lm = self._tex(self.L, self.ph * 0.3, rise * 0.9 * t)
        out *= (1 + q["shade"] * np.clip(lm, -2.5, 2.5))[..., None]
        return out, self.M * k


# ----------------------------------------------------------------------------------------- fire detection
FIRE_DEFAULTS = dict(
    ymin=0, ymax=None,     # only look for fires between these rows (e.g. skip a sunset sky)
    exclude=None,          # polygons where bright orange is NOT fire (sun glitter, lit windows, ...)
    r_min=200, rb_min=130, # flame colour thresholds (see fire_mask)
    min_area=100,          # px (after a 9x9 dilation that merges flame tongues)
    split=90,              # px: a wide fire front gets one plume per `split` px of width
    skip_radius=70,        # px: no auto plume this close to a hand-placed emitter's source
    wind=0.08,             # lean per px of plume height (+ = right)
    big=1500, mid=400,     # fire-area thresholds (px) for the column / torch / ember classes
    column={}, torch={}, ember={},   # per-class overrides merged into the generated specs
    drop=None,             # list of [x, y] points: auto plumes whose source is within 25 px are dropped
)


def fire_mask(rgb, r_min=200, rb_min=130):
    """bright saturated orange/yellow = flame.  (uint8 0/1).  Lower r_min / rb_min for distant, dimmer fires."""
    P = rgb.astype(np.int16); R, G, B = P[..., 0], P[..., 1], P[..., 2]
    m = (R > r_min) & (G > 70) & (G < 215) & (B < 120) & ((R - B) > rb_min)
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))


def detect_fire_emitters(plate, spec, manual=(), protect=None):
    """One emitter spec per detected fire, sized to the fire.  Wide fire fronts are split into several
    sources.  Small embers -> thin 'ember' wisps, medium fires -> torch plumes, big fires -> columns."""
    q = {**FIRE_DEFAULTS, **spec}
    H, W = plate.shape[:2]
    m = fire_mask(plate, q["r_min"], q["rb_min"])
    m[:int(q["ymin"])] = 0
    if q["ymax"]:
        m[int(q["ymax"]):] = 0
    if q["exclude"]:
        m[poly_mask((H, W), q["exclude"]) > 0.5] = 0
    if protect:
        m[poly_mask((H, W), protect) > 0.5] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(m, np.ones((9, 9), np.uint8)))
    srcs = [tuple(e["src"]) for e in manual if e.get("src")]
    drops = q["drop"] or []
    out = []
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < q["min_area"]:
            continue
        k = max(1, int(round(w / q["split"])))
        for c in range(k):
            cx0, cx1 = x + w * c // k, x + w * (c + 1) // k
            sub = (lab[y:y + h, cx0:cx1] == i) & (m[y:y + h, cx0:cx1] > 0)
            ys, xs = np.nonzero(sub)
            if len(xs) < 12:
                continue
            area = float(sub.sum()); wc = float(xs.max() - xs.min() + 1)
            sx = float(cx0 + xs.mean()); sy = float(y + np.percentile(ys, 6))    # at the flame tips
            if any(math.hypot(sx - u, sy - v) < q["skip_radius"] for u, v in srcs):
                continue
            if any(math.hypot(sx - u, sy - v) < 25 for u, v in drops):
                continue
            r = math.sqrt(area)
            if area >= q["big"]:
                e = dict(type="column", w0=max(14.0, 0.45 * wc), w1=float(np.clip(2.6 * wc, 120, 300)),
                         height=float(np.clip(11 * r, 320, 820)), rise=26.0 + 0.1 * r, layers=2); e.update(q["column"])
            elif area >= q["mid"]:
                e = dict(type="torch", w0=max(6.0, 0.4 * wc), w1=float(np.clip(1.8 * wc + 30, 50, 130)),
                         height=float(np.clip(10 * r, 170, 420))); e.update(q["torch"])
            else:
                e = dict(type="torch", w0=3.0, w1=float(np.clip(1.5 * wc + 24, 28, 70)),
                         height=float(np.clip(9 * r, 90, 190)), opacity=0.5, swirl=8.0); e.update(q["ember"])
            e.setdefault("lean", q["wind"] * e["height"])
            e.update(src=[round(sx, 1), round(sy, 1)], name=f"fire{i}_{c}", fire_area=int(area),
                     seed=int(i * 10 + c))
            out.append(e)
    return out


# ----------------------------------------------------------------------------------------- scene
class SmokeScene:
    """All emitters + billows of one plate.  `frame(t)` returns the plate with smoke (uint8 RGB, plate size)."""

    def __init__(self, plate_rgb, config):
        self.P = plate_rgb
        self.Pf = plate_rgb.astype(np.float32)
        H, W = plate_rgb.shape[:2]
        self.cfg = config
        self.protect_bin = (poly_mask((H, W), config.get("protect"), 0) > 0.5).astype(np.float32)
        self.keep = keepout_fade(self.protect_bin, float(config.get("protect_feather", 36)))
        fk = float(config.get("flame_keepout", 0.0))   # flames stay readable: smoke thins over flame pixels
        if fk > 0:
            fm = cv2.GaussianBlur(cv2.dilate(fire_mask(plate_rgb).astype(np.float32), np.ones((3, 3), np.uint8)), (0, 0), 2.5)
            self.keep = (self.keep * (1 - fk * np.clip(fm * 1.6, 0, 1))).astype(np.float32)
        self.ease_in = float(config.get("ease_in", 0.0))   # legacy global fade; v2 configs leave it 0
        self.preroll = float(config.get("preroll", 8.0))    # sim time already elapsed at frame 0
        seed = int(config.get("seed", 0))
        self.billows = []
        for i, spec in enumerate(config.get("billows", [])):
            rng = np.random.default_rng(seed * 991 + i * 13 + int(spec.get("seed", 0)))
            self.billows.append(Billow(spec, plate_rgb, self.protect_bin, rng))
        self.emitters = []
        specs = list(config.get("emitters", []))
        if config.get("fires"):
            self.fire_specs = detect_fire_emitters(plate_rgb, config["fires"], specs, config.get("protect"))
            specs += self.fire_specs
        for i, spec in enumerate(specs):
            spec = dict(spec)
            for key in ("start", "end"):                   # given in shot time; emitters run on the pre-rolled clock
                if spec.get(key) is not None:
                    spec[key] = float(spec[key]) + self.preroll
            for L in _expand_layers(spec):
                rng = np.random.default_rng(seed * 1000 + i * 37 + int(L.get("seed", 0)))
                self.emitters.append(Emitter(L, (H, W), self.keep, rng))

    def frame(self, t):
        img = self.Pf.copy()
        k = ease(t, 0.0, self.ease_in) if self.ease_in > 0 else 1.0
        t = t + self.preroll                         # pre-rolled sim clock: established at frame 0
        for b in self.billows:                       # painted smoke first, overlay smoke on top
            x0, y0, x1, y1 = b.bb
            out, m = b.render(t, k)
            nz = m > 0
            roi = img[y0:y1, x0:x1]
            m3 = m[..., None]
            roi[nz] = (roi * (1 - m3) + out * m3)[nz]
        for e in self.emitters:
            x0, y0, x1, y1 = e.bb
            roi = img[y0:y1, x0:x1]
            a, col = e.render(t)
            a = (a * k)[..., None]
            roi[...] = roi * (1 - a) + col * a
        return np.clip(np.rint(img), 0, 255).astype(np.uint8)

    def matte(self):
        """float matte (plate size) of where billow may change pixels."""
        H, W = self.P.shape[:2]; m = np.zeros((H, W), np.float32)
        for b in self.billows:
            x0, y0, x1, y1 = b.bb; m[y0:y1, x0:x1] = np.maximum(m[y0:y1, x0:x1], b.M)
        return m

    def allow_mask(self):
        """True where smoke may touch pixels: emitter footprints (where keep-out > 0) + billow matte > 0."""
        H, W = self.P.shape[:2]; m = np.zeros((H, W), bool)
        for e in self.emitters:
            x0, y0, x1, y1 = e.bb; m[y0:y1, x0:x1] |= e.clip > 0
        return m | (self.matte() > 0)


# ----------------------------------------------------------------------------------------- camera + IO
def push_frame(img, u, out_w, out_h, z0=1.0, z1=1.06, center=(0.5, 0.5)):
    """StablePush: scale from z0 to z1 over u in [0,1] (smoothstep), cover-fit to out_w x out_h.
    `center` (fractions of the plate) is the fixed point of the zoom: (0.5,0.5) = centre push;
    moving it toward an edge keeps a subject at that edge in frame."""
    H, W = img.shape[:2]
    e = u * u * (3 - 2 * u)
    z = z0 + (z1 - z0) * e
    s0 = max(out_w / W, out_h / H); s = s0 * z
    cx, cy = center
    # fixed point: plate point (cx*W, cy*H) maps to the same output position at every zoom
    ox, oy = out_w / 2 + (cx - 0.5) * W * s0, out_h / 2 + (cy - 0.5) * H * s0
    M = np.float32([[s, 0, ox - s * cx * W], [0, s, oy - s * cy * H]])
    return cv2.warpAffine(img, M, (out_w, out_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def ffmpeg_writer(path, w, h, fps, crf=17):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def load_plate(path):
    a = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if a is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)


def zero_motion_report(scene, times, guards=None):
    """Diff rendered frames against the still plate.
    * outside the allowed footprint (emitter boxes minus keep-out, plus billow matte) -> must be 0;
    * inside `protect` polygons (coast, buildings, horizon, faces ...)                -> must be 0;
    * billow-only check: frames rendered with emitters off may change pixels ONLY where matte > 0;
    * optional `guards`: extra named polygons checked the same way."""
    H, W = scene.P.shape[:2]
    allow = scene.allow_mask(); prot = scene.protect_bin > 0.5; mat = scene.matte() > 0
    gm = {n: poly_mask((H, W), [p], 0) > 0.5 for n, p in (guards or {}).items()}
    worst = changed = pw = bw = 0; gw = {n: 0 for n in gm}
    em = scene.emitters
    for t in times:
        f = scene.frame(t)
        d = np.abs(f.astype(np.int16) - scene.P.astype(np.int16)).max(-1)
        worst = max(worst, int(d[~allow].max(initial=0))); changed += int((d[~allow] > 0).sum())
        pw = max(pw, int(d[prot].max(initial=0)))
        for n, m in gm.items():
            gw[n] = max(gw[n], int(d[m].max(initial=0)))
        if scene.billows:
            scene.emitters = []
            try:
                db = np.abs(scene.frame(t).astype(np.int16) - scene.P.astype(np.int16)).max(-1)
            finally:
                scene.emitters = em
            bw = max(bw, int(db[~mat].max(initial=0)))
    r = dict(frames=len(times), max_diff_outside=worst, changed_px_outside=changed,
             max_diff_in_protect=pw, protect_px=int(prot.sum()), allow_fraction=round(float(allow.mean()), 4))
    if scene.billows:
        r.update(billow_max_diff_outside_matte=bw, matte_px=int(mat.sum()))
    if gm:
        r["guards_max_diff"] = gw
    return r


def render(plate_path, config, out_path, seconds=8.0, fps=30, size=(1080, 1920), push=(1.0, 1.06), writer=None):
    """render one shot; if `writer` (an open ffmpeg pipe) is given, frames are appended to it."""
    scene = SmokeScene(load_plate(plate_path), config)
    n = int(round(seconds * fps)); w, h = size
    p = writer or ffmpeg_writer(out_path, w, h, fps)
    for i in range(n):
        t = i / fps
        p.stdin.write(push_frame(scene.frame(t), i / max(n - 1, 1), w, h, *push, center=tuple(config.get("push_center", (0.5, 0.5)))).tobytes())
    if writer is None:
        p.stdin.close(); p.wait()
    return scene


def _render_shot_job(args):
    cfg_path, seconds, fps, size, out = args
    cfg = json.load(open(cfg_path))
    render(cfg["plate"], cfg, out, seconds, fps, size, tuple(cfg.get("push", (1.0, 1.06))))
    return out


def render_reel(reel, out_path, size=(1080, 1920), fps=30, base_dir=".", jobs=1):
    """reel = {"shots": [{"config": path, "seconds": s}, ...]} -> one mp4 with hard cuts.
    jobs > 1: shots render in parallel processes to temporary segments (same encoder settings),
    then are joined losslessly with ffmpeg's concat demuxer (stream copy) -- a cheap ~N-x speed-up."""
    w, h = size
    shots = reel["shots"]
    if jobs <= 1:
        p = ffmpeg_writer(out_path, w, h, fps)
        for shot in shots:
            cfg = json.load(open(Path(base_dir) / shot["config"]))
            print("shot", shot["config"], shot["seconds"], "s", file=sys.stderr, flush=True)
            render(cfg["plate"], cfg, None, shot["seconds"], fps, size, tuple(cfg.get("push", (1.0, 1.06))), writer=p)
        p.stdin.close(); p.wait()
        return
    import multiprocessing as mp, tempfile, os
    tmp = Path(tempfile.mkdtemp(prefix=".reel_", dir=str(Path(out_path).resolve().parent)))
    segs = [str(tmp / f"shot{i:02d}.mp4") for i in range(len(shots))]
    work = [(str(Path(base_dir) / s["config"]), s["seconds"], fps, size, segs[i]) for i, s in enumerate(shots)]
    with mp.get_context("spawn").Pool(min(jobs, len(work))) as pool:
        for o in pool.imap_unordered(_render_shot_job, work):
            print("done", o, file=sys.stderr, flush=True)
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{x}'\n" for x in segs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(out_path)], check=True)
    for x in segs + [str(lst)]:          # our own temporary segments only
        os.remove(x)
    tmp.rmdir()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Composite procedural smoke over a still plate (plate never moves).")
    ap.add_argument("--plate", default=None, help="plate image (defaults to the config's \"plate\" field)"); ap.add_argument("--config", default=None)
    ap.add_argument("--reel", default=None, help="reel JSON: render several shots into one mp4"); ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=8.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", type=int, default=0, help="output width for a quick low-res preview (e.g. 360)")
    ap.add_argument("--no-push", action="store_true"); ap.add_argument("--proof", action="store_true",
                    help="also print the zero-motion report (frame diff vs still outside the smoke footprint)")
    ap.add_argument("--grab", default=None, help="also save a 360x640 PNG frame grab at --grab-t seconds")
    ap.add_argument("--grab-t", type=float, default=3.0)
    ap.add_argument("--jobs", type=int, default=1, help="reel only: render shots in N parallel processes")
    a = ap.parse_args(argv)
    if a.reel:
        w = a.preview or 1080
        render_reel(json.load(open(a.reel)), a.out, (w, int(round(w * 16 / 9))), a.fps, Path(a.reel).parent.parent, a.jobs)
        return
    cfg = json.load(open(a.config))
    a.plate = a.plate or cfg["plate"]
    w = a.preview or 1080; h = int(round(w * 16 / 9))
    scene = render(a.plate, cfg, a.out, a.seconds, a.fps, (w, h), (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06))))
    if a.grab:
        u = min(a.grab_t / max(a.seconds, 1e-6), 1.0)
        z = (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06)))
        g = push_frame(scene.frame(a.grab_t), u, 1080, 1920, *z, center=tuple(cfg.get("push_center", (0.5, 0.5))))
        g = cv2.resize(g, (360, 640), interpolation=cv2.INTER_AREA)
        cv2.imwrite(a.grab, cv2.cvtColor(g, cv2.COLOR_RGB2BGR))
    if a.proof:
        print(json.dumps(zero_motion_report(scene, np.arange(0, a.seconds, 0.5), cfg.get("guards")), indent=1))


if __name__ == "__main__":
    main()
