"""flames_v1 -- emissive, vertical-only flame animation for still painted plates (Posterity engine R&D, PoC).

The plate NEVER moves.  Only the light a painted fire EMITS is animated:

  plate = bg + E          bg = soft fill of the surroundings over the (dilated) flame matte, never brighter
                          than the plate;  E = plate - bg >= 0  (the flame's own light)
  frame = plate - E_move + W(E_move) * flicker      (+ light spill, + sparks)

  * Flame matte: hot hue + high value + yellow-white core, limited to hand `region` polygons, plus `add` and
    `protect` polygons.  Every connected flame component is processed on its own: noise scaled to its size,
    its own flicker clock and seed.
  * Tongues: W is a VERTICAL-ONLY remap of E_move (map_x == x exactly, so there is no sway, swivel or
    squiggle by construction).  The displacement D(x, y, t) = amp * L(y) * N(x, y + rise*t) comes from two
    vertically-elongated noise textures scrolling UPWARD at different speeds, so tongues stretch upward, lick
    and fall back; L(y) anchors the base (0) and frees the tips (1).  A second rising noise cuts gaps
    into the tips so tongues break off and shrink as they rise, and a slow rising brightness term gives the
    body an upward internal flow.  The slope dD/dy is clamped so content never folds.
  * Flicker: smooth random-walk clock (rates < 5 Hz, amp ~0.1) per component; channel exponents
    (R 1.0, G 1.35, B 1.9) => brighter = whiter, dimmer = redder; stronger at the tips than the core.
  * Light spill: a multiplicative warm ring on nearby surfaces (distance falloff from the flame, protect
    removed), driven by the SAME clock as its flame.
  * Sparks/embers: deterministic particles born at the flame tips, rising with deceleration and a gentle
    drift, cooling yellow -> red, confined to a spark zone.  Everything is PRE-ROLLED (`preroll` s), so sparks
    are already in the air at frame 0.

Zero motion: pixels outside (flame zone U spill zone U spark zone) and inside every `protect` polygon are
bit-exact copies of the plate; `zero_motion_report()` proves it.  Faces, land and water are never remapped:
the only remapped signal is E_move, which is zero outside the flame matte.

Dependencies: numpy, opencv-python, ffmpeg on PATH.  No other project code is imported (the optional
`--smoke` composite loads smoke_v2.py from a path you give it, read-only).

CLI:
  python flames_v1.py --config CFG.json --out OUT.mp4 [--seconds 7] [--preview 360] [--proof DIR] [--stats]
  python flames_v1.py --config CFG.json --stills DIR --times 1 3        (before/after PNGs, no video)
  python flames_v1.py --reel REEL.json --out REEL.mp4
"""
import argparse, json, math, subprocess, sys
from pathlib import Path
import numpy as np
import cv2


# ----------------------------------------------------------------------------------------- helpers
def periodic_noise(rng, h, w, lo, hi, beta=2.0):
    """Seamless fractal noise (h, w), zero mean / unit std. lo = largest feature px, hi = smallest."""
    fy = np.fft.fftfreq(h)[:, None]; fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    amp = (f * f + (1.0 / lo) ** 2) ** (-beta / 4) * np.exp(-(f * hi) ** 2)
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) * amp
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.mean()
    return n / (n.std() + 1e-8)


def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return x * x * (3 - 2 * x)


def poly_mask(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys or []:
        cv2.fillPoly(m, [np.int32(np.round(np.float32(p)))], 1)
    return m


def keepout_fade(protect_bin, feather):
    """0 inside (and 1 px around) protected shapes, smoothly -> 1 at `feather` px away."""
    if not protect_bin.any():
        return np.ones(protect_bin.shape, np.float32)
    d = cv2.distanceTransform((protect_bin == 0).astype(np.uint8), cv2.DIST_L2, 5)
    return smoothstep(1.5, max(2.5, feather), d).astype(np.float32)


class Clock:
    """Smooth non-repeating flicker clock c(t) ~ N(0,1)-ish: sum of smoothstep-interpolated random walks.
    Every rate is < 5 Hz (default 0.55 / 1.3 / 2.9 Hz), so there is no strobing."""
    def __init__(self, rng, rates=(0.55, 1.3, 2.9), weights=(0.55, 0.32, 0.18)):
        self.rates = rates; self.w = np.float32(weights) / np.sqrt(np.sum(np.square(weights)))
        self.tab = [rng.standard_normal(16384).astype(np.float32) for _ in rates]
        self.ph = [float(rng.uniform(0, 4000)) for _ in rates]

    def __call__(self, t):
        v = 0.0
        for tab, r, w, ph in zip(self.tab, self.rates, self.w, self.ph):
            i = t * r + ph; j = int(i) % 16380; fr = i - math.floor(i); fr = fr * fr * (3 - 2 * fr)
            v += w * (tab[j] * (1 - fr) + tab[j + 1] * fr)
        return float(v)


# ----------------------------------------------------------------------------------------- defaults
TEX_LAMBDA = 45.0         # measured mean wavelength (texels) of the shared noise textures
FLAME_DEFAULTS = dict(
    name="flame",
    region=None,          # polygons (plate px) where flames may be keyed
    add=None,             # polygons forced INTO the matte (missed flame pixels)
    protect=None,         # polygons forced OUT of the matte (and out of every effect) -- per flame
    key=dict(v_min=0.70, v_soft=0.10, rb_min=70, rb_soft=40, core_v=0.92),  # flame colour key
    min_area=60,          # px: smaller keyed blobs are ignored
    min_h=12,             # px: flatter blobs (glints, lit rims) are ignored
    grow=7,               # px: matte dilation = the bg-fill zone (also merges nearby tongues into one component)
    # tongues (all lengths relative to the component's height hc unless _px)
    tongue=0.12,          # displacement amplitude, fraction of hc
    tongue_px_max=38.0,   # hard cap on amplitude in px
    scale_x=0.60,         # horizontal wavelength of the tongue field, fraction of component width (finger size)
    scale_y=2.5,          # vertical wavelength, fraction of hc: long, so whole tongues stretch/retract (no folding)
    lick_hz=1.8,          # how often a tongue licks up and falls back (the field travels UPWARD at lick_hz*scale_y*hc px/s)
    base=0.10, free=0.75, # height fractions: below `base` nothing moves, above `free` full motion
    slope_max=0.7,        # |dD/dy| clamp (no folding)
    shear_max=0.6,        # |dD/dx| clamp: column-to-column shear is what reads as squiggles
    soften=0.0,           # gaussian sigma on the moved light (match a defocused plate flame)
    breakup=0.45,         # strength of the rising gaps cut into the tips
    flow=0.10,            # rising brightness turbulence inside the body
    fringe=1.0,           # how far tongues may extend above the matte, in units of the amplitude
    # light
    flicker=dict(amp=0.10, tip=0.8, temp=[1.0, 1.35, 1.9], rates=[0.55, 1.3, 2.9]),
    spill=dict(strength=0.55, radius_k=1.4, radius_min=40, radius_max=260, tint=[1.0, 0.82, 0.6], region=None),
    sparks=dict(rate=5.0, min_h=40, life=[1.2, 2.6], v0=[90, 200], vmin=20, tau=0.7, drift=12.0, wobble=5.0,
                size=[1.0, 2.2], bright=0.9, zone_up=3.0, zone_side=0.9, zone=None),
    seed=0,
)


def _merge(a, b):
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = _merge(a[k], v) if isinstance(v, dict) and isinstance(a.get(k), dict) else v
    return out


def flame_key(rgb, v_min, v_soft, rb_min, rb_soft, core_v):
    """soft 0..1 key: bright (V) AND hot (R-B large), OR a near-white core."""
    f = rgb.astype(np.float32)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    V = f.max(-1) / 255.0
    hot = smoothstep(v_min - v_soft, v_min + v_soft, V) * smoothstep(rb_min - rb_soft, rb_min + rb_soft, R - B) \
        * smoothstep(0.0, 40.0, R - G + 30)          # not green/blue-ish
    core = smoothstep(core_v - 0.04, core_v + 0.04, (R + G) / 510.0) * smoothstep(0, 30, R - B)
    return np.maximum(hot, core).astype(np.float32)


# ----------------------------------------------------------------------------------------- one flame component
class FlameComponent:
    """One connected flame: own ROI, bg fill, emission, noise mapping, clock, spill and sparks."""

    def __init__(self, plate_f, K, Mz, q, keep, tex, rng, idx):
        H, W = plate_f.shape[:2]
        self.q = q; self.idx = idx
        ys, xs = np.nonzero(Mz)
        self.top, self.bot = int(ys.min()), int(ys.max())
        self.left, self.right = int(xs.min()), int(xs.max())
        kb = K > 0.5
        kys = np.nonzero(kb)[0] if kb.any() else ys
        ftop, fbot = int(kys.min()), int(kys.max())
        self.hc = hc = max(8.0, float(fbot - ftop + 1)); self.wc = wc = max(6.0, float(xs.max() - xs.min() + 1))
        self.amp = float(min(q["tongue"] * hc, q["tongue_px_max"]))
        dmax = int(math.ceil(self.amp * 2.2)) + 2                       # |D| is clipped to this
        fr = int(math.ceil(self.amp * q["fringe"]))
        x0, x1 = max(0, self.left - 2), min(W, self.right + 3)
        y0, y1 = max(0, self.top - dmax - fr), min(H, self.bot + 3)
        self.bb = (x0, y0, x1, y1); self.dmax = dmax
        P = plate_f[y0:y1, x0:x1]
        mz = Mz[y0:y1, x0:x1].astype(np.uint8)
        # --- background fill (emissive model): bg <= plate, == plate outside the zone
        p8 = np.clip(P, 0, 255).astype(np.uint8)
        fill = cv2.inpaint(p8, mz, max(3, q["grow"]), cv2.INPAINT_TELEA).astype(np.float32)
        fill = cv2.GaussianBlur(fill, (0, 0), 1.5)
        bg = np.where(mz[..., None] > 0, np.minimum(P, fill), P)
        E = P - bg                                                      # >= 0, == 0 outside the zone
        dist = cv2.distanceTransform(mz, cv2.DIST_L2, 3)
        k = K[y0:y1, x0:x1] * smoothstep(0.5, 3.5, dist) * keep[y0:y1, x0:x1]
        self.Em = (E * k[..., None]).astype(np.float32)                 # the light that moves
        # warm-order caps: moved light must not push a pixel bluer than the plate's own flame ever is
        # (E carries plate-minus-fill colour, so shifting it across a varying fill can tint cores blue-grey)
        self.P = P.astype(np.float32)
        fz = (k > 0.05) & (P[..., 0] > 40)
        if fz.sum() > 20:
            self.rGR = min(0.98, float(np.percentile(P[..., 1][fz] / np.maximum(P[..., 0][fz], 1), 97)))
            self.rBG = min(0.92, float(np.percentile(P[..., 2][fz] / np.maximum(P[..., 1][fz], 1), 97)))
        else:
            self.rGR = self.rBG = 1.0
        # --- geometry: height fraction (0 at the flame base, 1 at its top), per column
        h, w = mz.shape
        self.Y, self.X = np.mgrid[0:h, 0:w].astype(np.float32)
        ybase = fbot - y0; ytop = ftop - y0
        hf = (ybase - self.Y) / max(1.0, ybase - ytop)
        self.L = smoothstep(q["base"], q["free"], hf).astype(np.float32)
        self.keep = keep[y0:y1, x0:x1]
        # --- noise mapping into the shared textures (texture feature ~ 64 px)
        self.tex = tex                                                  # texture wavelength ~TEX_LAMBDA texels
        self.sx = TEX_LAMBDA / max(4.0, q["scale_x"] * wc)
        self.sy = TEX_LAMBDA / max(6.0, q["scale_y"] * hc)
        self.rise_px = q["lick_hz"] * q["scale_y"] * hc                 # px/s the tongue field travels upward
        self.off = rng.uniform(0, 4096, 6).astype(np.float32)
        fq = q["flicker"]
        self.clock = Clock(rng, tuple(fq["rates"]))
        self.temp = np.float32(fq["temp"])
        self.tongue_hz = q["lick_hz"]
        # slope clamp: measure max |dD/dy| at a few times, scale down if needed
        self.gain = 1.0
        s = max(self._slope(t) for t in (0.0, 0.7, 1.7, 3.1, 5.3))
        if s > q["slope_max"]:
            self.gain = q["slope_max"] / s
        # exact footprint of the tongue change: E_move support dilated vertically by dmax, clipped to ROI
        sup = (self.Em.max(-1) > 0).astype(np.uint8)
        self.zone = cv2.dilate(sup, np.ones((2 * dmax + 1, 1), np.uint8)) > 0
        self.zone &= self.keep > 0
        self._init_spill(K, Mz, keep, H, W)
        self._init_sparks(K, Mz, keep, H, W, rng)

    # ---- tongue field
    def _sample(self, T, xo, yo, sxf=1.0, syf=1.0):
        tw, th = T.shape[1], T.shape[0]
        u = np.mod((self.X + self.bb[0]) * self.sx * sxf + xo, tw).astype(np.float32)
        v = np.mod((self.Y + self.bb[1]) * self.sy * syf + yo, th).astype(np.float32)
        return cv2.remap(T, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)

    def _D(self, t):
        o = self.off; r = self.rise_px * self.sy
        n = 0.75 * self._sample(self.tex[0], o[0], o[1] + r * t) + 0.45 * self._sample(self.tex[0], o[2], o[3] + 1.61 * r * t, 1.4, 1.3)
        return np.clip(self.amp * self.gain * self.L * n, -self.dmax + 1, self.dmax - 1)

    def _slope(self, t):
        """99.5th pct of the vertical stretch |dD/dy| and of the column shear |dD/dx| (scaled to the y limit)."""
        D = self._D(t); sup = self.Em.max(-1) > 0
        sy = np.abs(np.diff(D, axis=0))[sup[1:]]
        sx = np.abs(np.diff(D, axis=1))[sup[:, 1:]] * (self.q["slope_max"] / self.q["shear_max"])
        return float(max(np.percentile(sy, 99.5), np.percentile(sx, 99.5))) if sy.size and sx.size else 0.0

    def tongues(self, t):
        """W(E_move): vertical-only remap (map_x is exactly the pixel column) + rising tip gaps + body flow."""
        q = self.q; o = self.off; r = self.rise_px * self.sy
        D = self._D(t)
        Wm = cv2.remap(self.Em, self.X, self.Y + D, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        g = self._sample(self.tex[2], o[4], o[5] + 0.9 * r * t, 1.3, 4.0)       # rising gaps (shorter wavelength)
        cut = 1.0 - q["breakup"] * self.L * smoothstep(0.2, 1.8, g)
        fl = self._sample(self.tex[1], o[5], o[4] + 0.6 * r * t, 0.9, 3.0)        # rising body turbulence
        m = np.clip(cut * (1.0 + q["flow"] * np.clip(fl, -2, 2)), 0.0, 2.0)[..., None]
        Wm = Wm * m ** self.temp              # thinner/dimmer flame light is redder, not grey
        if q["soften"] > 0:                   # match the plate's own focus (defocused foreground fire)
            Wm = cv2.GaussianBlur(Wm, (0, 0), q["soften"])
        return Wm

    def flick(self, t):
        return self.q["flicker"]["amp"] * self.clock(t)          # signed fractional brightness change

    def delta(self, t):
        """ROI delta to add to the frame: (W * flicker) - E_move, faded by the protect keep-out."""
        f = self.flick(t)
        Wm = self.tongues(t)
        tipw = 1.0 - self.q["flicker"]["tip"] * 0.5 + self.q["flicker"]["tip"] * self.L      # stronger at the tips
        F = np.clip(1.0 + f * tipw, 0.2, 3.0)[..., None]
        Wm = Wm * F ** self.temp                                                          # brighter = whiter
        d = (Wm - self.Em) * self.keep[..., None]
        o = self.P + d
        g = np.minimum(o[..., 1], np.maximum(self.rGR * o[..., 0], self.P[..., 1]))
        bl = np.minimum(o[..., 2], np.maximum(self.rBG * g, self.P[..., 2]))
        d[..., 1] = g - self.P[..., 1]; d[..., 2] = bl - self.P[..., 2]
        d[~self.zone] = 0.0
        return d

    # ---- light spill
    def _init_spill(self, K, Mz, keep, H, W):
        sp = self.q.get("spill")
        self.spill = None
        if not sp or sp.get("strength", 0) <= 0:
            return
        r = float(np.clip(sp["radius_k"] * self.hc, sp["radius_min"], sp["radius_max"]))
        R = int(math.ceil(r * 2.2))
        x0, x1 = max(0, self.left - R), min(W, self.right + R + 1)
        y0, y1 = max(0, self.top - R), min(H, self.bot + R + 1)
        src = (K[y0:y1, x0:x1] > 0.5) & (Mz[y0:y1, x0:x1] > 0)
        d = cv2.distanceTransform((~src).astype(np.uint8), cv2.DIST_L2, 5)
        fall = np.clip((np.exp(-(d / r) ** 2) - 0.01) / 0.99, 0, 1)
        if sp.get("region"):
            fall *= poly_mask((H, W), sp["region"])[y0:y1, x0:x1]
        fall = (fall * keep[y0:y1, x0:x1]).astype(np.float32)
        self.spill = dict(bb=(x0, y0, x1, y1), fall=fall, k=float(sp["strength"]), tint=np.float32(sp["tint"]))

    # ---- sparks
    def _init_sparks(self, K, Mz, keep, H, W, rng):
        sp = self.q.get("sparks"); self.sparks = None
        if not sp or sp.get("rate", 0) <= 0 or self.hc < sp["min_h"]:
            return
        ys, xs = np.nonzero((K > 0.5) & (Mz > 0))
        # birth points: the top of every keyed column that reaches the upper half of the flame, so sparks
        # leave from all tongues across the fire (one global tip makes a dotted single-file line)
        top = {}
        for x, y in zip(xs.tolist(), ys.tolist()):
            if y < top.get(x, 1 << 30):
                top[x] = y
        tx = np.float32(list(top.keys())); ty = np.float32(list(top.values()))
        hf = (ys.max() - ty) / max(1.0, ys.max() - ys.min())
        ok = hf > 0.5
        tx, ty = tx[ok], ty[ok]
        up = sp["zone_up"] * self.hc; side = sp["zone_side"] * self.hc
        x0, x1 = int(max(0, self.left - side)), int(min(W, self.right + side + 1))
        y0, y1 = int(max(0, self.top - up)), int(min(H, self.bot + 1))
        zm = np.zeros((y1 - y0, x1 - x0), np.float32)
        # zone: a rounded column above the flame, soft at the top and sides
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        cx = 0.5 * (self.left + self.right)
        hw = 0.5 * (self.right - self.left) + side * (0.3 + 0.7 * smoothstep(self.top, self.top - up, yy))
        zm = (1 - smoothstep(0.7, 1.0, np.abs(xx - cx) / hw)) * (1 - smoothstep(0.75, 1.0, (self.bot - yy) / (self.bot - y0 + 1)))
        if sp.get("zone"):
            zm *= poly_mask((H, W), sp["zone"])[y0:y1, x0:x1]
        zm = (zm * keep[y0:y1, x0:x1]).astype(np.float32)
        span = 200.0                                    # seconds of births (covers preroll + any shot)
        rate = sp["rate"] * self.hc / 100.0
        n = int(rng.poisson(rate * span)) + 1
        j = rng.integers(0, len(tx), n)
        lo, hi = sp["life"]
        sc = self.hc / 100.0
        self.sparks = dict(bb=(x0, y0, x1, y1), zone=zm, vmin=sp["vmin"] * min(1.0, 0.5 + 0.5 * sc), tau=sp["tau"],
                           p=dict(                      # one entry per particle (deterministic, seeded)
            birth=rng.uniform(-10.0, span - 10.0, n).astype(np.float32),
            x0=(tx[j] + rng.uniform(-2, 2, n)).astype(np.float32), y0=(ty[j] + rng.uniform(-1, 1, n)).astype(np.float32),
            life=rng.uniform(lo, hi, n).astype(np.float32),
            v0=(rng.uniform(*sp["v0"], n) * min(1.0, 0.45 + 0.55 * sc)).astype(np.float32),
            drift=rng.normal(0, sp["drift"], n).astype(np.float32), wob=(rng.uniform(0.3, 1.0, n) * sp["wobble"]).astype(np.float32),
            wf=rng.uniform(0.4, 1.2, n).astype(np.float32), wp=rng.uniform(0, 6.28, n).astype(np.float32),
            size=rng.uniform(*sp["size"], n).astype(np.float32), b=(rng.uniform(0.55, 1.0, n) * sp["bright"]).astype(np.float32)))

    def spark_pos(self, p, a):
        """closed-form position at age a: decelerating rise (v0 -> vmin, time constant tau) + slow drift/wobble."""
        s = self.sparks; vmin, tau = s["vmin"], s["tau"]
        rise = vmin * a + (p["v0"] - vmin) * tau * (1 - np.exp(-a / tau))
        x = p["x0"] + p["drift"] * a + p["wob"] * np.sin(6.283 * p["wf"] * a + p["wp"]) * np.minimum(a, 1.0)
        return x, p["y0"] - rise

    def render_sparks(self, t, fps=30.0):
        s = self.sparks; P = s["p"]
        x0, y0, x1, y1 = s["bb"]
        a = t - P["birth"]
        alive = np.nonzero((a > 0) & (a < P["life"]))[0]
        if len(alive) == 0:
            return None
        canvas = np.zeros((y1 - y0, x1 - x0, 3), np.uint8)
        p = {k: v[alive] for k, v in P.items()}
        aa = a[alive]
        xa, ya = self.spark_pos(p, aa)
        xb, yb = self.spark_pos(p, np.maximum(aa - 1.6 / fps, 0))       # motion-blur streak
        u = aa / p["life"]
        fade = smoothstep(0.0, 0.08, u) * (1 - smoothstep(0.55, 1.0, u))
        cool = smoothstep(0.0, 0.9, u)[:, None]
        col = np.float32([255, 205, 120]) * (1 - cool) + np.float32([255, 95, 30]) * cool
        col = col * (p["b"] * fade)[:, None]
        for i in range(len(alive)):
            c = tuple(int(v) for v in col[i])
            th = max(1, int(round(p["size"][i] * (1 - 0.4 * u[i]))))
            cv2.line(canvas, (int((xb[i] - x0) * 16), int((yb[i] - y0) * 16)), (int((xa[i] - x0) * 16), int((ya[i] - y0) * 16)),
                     c, th, cv2.LINE_AA, 4)
        f = canvas.astype(np.float32)
        f = cv2.GaussianBlur(f, (0, 0), 0.6) + 0.5 * cv2.GaussianBlur(f, (0, 0), 3.0)    # core + soft glow
        return f * s["zone"][..., None]


# ----------------------------------------------------------------------------------------- scene
class FlameScene:
    """All flames of one plate.  `frame(t)` returns the plate with animated flames (uint8 RGB, plate size)."""

    def __init__(self, plate_rgb, config, sparks=True, spill=True):
        self.P = plate_rgb; self.Pf = plate_rgb.astype(np.float32)
        H, W = plate_rgb.shape[:2]
        self.cfg = config; self.fps = float(config.get("fps", 30))
        self.preroll = float(config.get("preroll", 6.0))
        self.use_sparks, self.use_spill = sparks, spill
        seed = int(config.get("seed", 0))
        prot = poly_mask((H, W), config.get("protect"))
        self.protect_bin = prot
        self.comps = []
        rng0 = np.random.default_rng(seed)
        # shared periodic textures (smooth: lo 64 / hi 16 texels, measured wavelength ~TEX_LAMBDA texels)
        # all three textures are deliberately smooth (no detail below ~0.7 of a feature): fine detail in a
        # vertical-only field turns into column-to-column shear, which reads as squiggles
        tex = [periodic_noise(rng0, 1024, 1024, 64, 34), periodic_noise(rng0, 1024, 1024, 64, 26),
               periodic_noise(rng0, 1024, 1024, 64, 26)]
        self.tex = [(T - T.mean()) / (T.std() + 1e-6) for T in tex]
        for fi, spec in enumerate(config.get("flames", [])):
            q = _merge(FLAME_DEFAULTS, spec)
            fprot = (prot | poly_mask((H, W), q.get("protect"))).astype(np.uint8)
            self.protect_bin = self.protect_bin | fprot
            keep = keepout_fade(fprot, float(config.get("protect_feather", 6)))
            K = flame_key(plate_rgb, **q["key"])
            R = poly_mask((H, W), q["region"]) if q["region"] else np.ones((H, W), np.uint8)
            K *= R
            A = poly_mask((H, W), q.get("add"))
            K = np.maximum(K, A.astype(np.float32) * R)
            K[fprot > 0] = 0
            K = cv2.GaussianBlur(K, (0, 0), 0.8)
            kb = (K > 0.5).astype(np.uint8)
            kb = cv2.morphologyEx(kb, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            g = int(q["grow"]); zone = cv2.dilate(kb, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * g + 1, 2 * g + 1)))
            zone[fprot > 0] = 0
            n, lab, st, _ = cv2.connectedComponentsWithStats(zone)
            for i in range(1, n):
                Mz = lab == i
                kys = np.nonzero(kb * Mz)[0]
                if int(len(kys)) < q["min_area"] or kys.max() - kys.min() < q["min_h"]:
                    continue
                Kc = K * Mz
                rng = np.random.default_rng(seed * 7919 + fi * 101 + i * 13 + int(q.get("seed", 0)))
                c = FlameComponent(self.Pf, Kc, Mz, q, keep, self.tex, rng, (fi, i))
                c.name = f"{q['name']}#{len(self.comps)}"
                self.comps.append(c)

    def frame(self, t, base=None):
        img = (self.Pf if base is None else base.astype(np.float32)).copy()
        t = t + self.preroll
        if self.use_spill:                                   # light on surroundings first (multiplicative)
            for c in self.comps:
                if c.spill:
                    s = c.spill; x0, y0, x1, y1 = s["bb"]
                    m = 1.0 + s["k"] * c.flick(t) * s["fall"][..., None] * s["tint"]
                    img[y0:y1, x0:x1] *= m
        for c in self.comps:                                 # flame light: remove E_move, add tongues
            x0, y0, x1, y1 = c.bb
            img[y0:y1, x0:x1] += c.delta(t)
        if self.use_sparks:
            for c in self.comps:
                if c.sparks:
                    f = c.render_sparks(t, self.fps)
                    if f is not None:
                        x0, y0, x1, y1 = c.sparks["bb"]
                        img[y0:y1, x0:x1] += f
        return np.clip(np.rint(img), 0, 255).astype(np.uint8)

    # ---- masks for the proofs
    def zone_mask(self, flame=True, spill=True, sparks=True):
        H, W = self.P.shape[:2]; m = np.zeros((H, W), bool)
        for c in self.comps:
            if flame:
                x0, y0, x1, y1 = c.bb; m[y0:y1, x0:x1] |= c.zone
            if spill and c.spill:
                x0, y0, x1, y1 = c.spill["bb"]; m[y0:y1, x0:x1] |= c.spill["fall"] > 0
            if sparks and c.sparks:
                x0, y0, x1, y1 = c.sparks["bb"]; m[y0:y1, x0:x1] |= c.sparks["zone"] > 0
        return m


# ----------------------------------------------------------------------------------------- proofs + measurements
def zero_motion_report(plate_rgb, cfg, times, guards=None):
    """Diff frames against the still plate:
       full effect  : changed px outside (flame zone U spill zone U spark zone)  -> must be 0
       flames only  : (sparks + spill off) changed px outside the flame zone     -> must be 0
       protect/guard: max diff inside every protect polygon and named guard      -> must be 0"""
    H, W = plate_rgb.shape[:2]
    full = FlameScene(plate_rgb, cfg); only = FlameScene(plate_rgb, cfg, sparks=False, spill=False)
    allow = full.zone_mask(); fz = only.zone_mask(spill=False, sparks=False)
    prot = full.protect_bin > 0
    gm = {n: poly_mask((H, W), [p]) > 0 for n, p in (guards or {}).items()}
    r = dict(frames=len(times), changed_px_outside_allowed=0, max_diff_outside_allowed=0,
             flames_only_changed_px_outside_flame_zone=0, max_diff_in_protect=0, protect_px=int(prot.sum()),
             guards_max_diff={n: 0 for n in gm}, allowed_fraction=round(float(allow.mean()), 4),
             flame_zone_fraction=round(float(fz.mean()), 4), components=len(full.comps), changed_px_inside_allowed_max=0)
    P16 = plate_rgb.astype(np.int16)
    for t in times:
        d = np.abs(full.frame(t).astype(np.int16) - P16).max(-1)
        r["changed_px_outside_allowed"] += int((d[~allow] > 0).sum())
        r["max_diff_outside_allowed"] = max(r["max_diff_outside_allowed"], int(d[~allow].max(initial=0)))
        r["max_diff_in_protect"] = max(r["max_diff_in_protect"], int(d[prot].max(initial=0)))
        r["changed_px_inside_allowed_max"] = max(r["changed_px_inside_allowed_max"], int((d[allow] > 0).sum()))
        for n, m in gm.items():
            r["guards_max_diff"][n] = max(r["guards_max_diff"][n], int(d[m].max(initial=0)))
        d2 = np.abs(only.frame(t).astype(np.int16) - P16).max(-1)
        r["flames_only_changed_px_outside_flame_zone"] += int((d2[~fz] > 0).sum())
    r["pass"] = (r["changed_px_outside_allowed"] == 0 and r["flames_only_changed_px_outside_flame_zone"] == 0
                 and r["max_diff_in_protect"] == 0 and all(v == 0 for v in r["guards_max_diff"].values()))
    return r


def luma(img):
    return img.astype(np.float32) @ np.float32([0.299, 0.587, 0.114])


def measure(scene, seconds, fps=30):
    """plate-level brightness swing, local flame-zone swing, flicker spectrum, frame-to-frame steps."""
    n = int(round(seconds * fps)); allow = scene.zone_mask(); fz = scene.zone_mask(spill=False, sparks=False)
    plate_mean, zone_mean, flame_mean, clocks = [], [], [], []
    for i in range(n):
        t = i / fps; L = luma(scene.frame(t))
        plate_mean.append(L.mean()); zone_mean.append(L[allow].mean()); flame_mean.append(L[fz].mean())
        clocks.append([c.flick(t + scene.preroll) for c in scene.comps[:12]])
    def swing(a):
        a = np.float64(a); return round(float((a.max() - a.min()) / a.mean() * 100), 3)
    def spectrum(a):
        a = np.float64(a) - np.mean(a); p = np.abs(np.fft.rfft(a * np.hanning(len(a)))) ** 2; f = np.fft.rfftfreq(len(a), 1 / fps)
        c = np.cumsum(p[1:]) / max(p[1:].sum(), 1e-12)
        return dict(peak_hz=round(float(f[1:][np.argmax(p[1:])]), 2), f95_hz=round(float(f[1:][np.searchsorted(c, 0.95)]), 2),
                    energy_above_5hz=round(float(p[f >= 5].sum() / max(p[1:].sum(), 1e-12)), 4))
    step = lambda a: round(float(np.abs(np.diff(np.float64(a))).max() / np.mean(a) * 100), 3)
    cl = np.array(clocks)
    return dict(seconds=seconds, fps=fps,
                plate_swing_pct=swing(plate_mean), plate_max_step_pct=step(plate_mean),
                effect_zone_swing_pct=swing(zone_mean), flame_zone_swing_pct=swing(flame_mean),
                flame_zone_max_frame_step_pct=step(flame_mean), flame_zone_spectrum=spectrum(flame_mean),
                flicker_amp_rms=round(float(cl.std()), 4) if cl.size else 0,
                clock_spectrum=spectrum(cl[:, 0]) if cl.size else None,
                tongue_feature_hz=sorted({round(c.tongue_hz, 2) for c in scene.comps}),
                tongue_amp_px=[round(c.amp * c.gain, 1) for c in scene.comps[:12]])


# ----------------------------------------------------------------------------------------- camera + IO
def push_frame(img, u, out_w, out_h, z0=1.0, z1=1.06, center=(0.5, 0.5)):
    """StablePush (same maths as smoke_v2): zoom z0->z1 (smoothstep over u), cover-fit, fixed point `center`."""
    H, W = img.shape[:2]
    e = u * u * (3 - 2 * u); z = z0 + (z1 - z0) * e
    s0 = max(out_w / W, out_h / H); s = s0 * z; cx, cy = center
    ox, oy = out_w / 2 + (cx - 0.5) * W * s0, out_h / 2 + (cy - 0.5) * H * s0
    M = np.float32([[s, 0, ox - s * cx * W], [0, s, oy - s * cy * H]])
    return cv2.warpAffine(img, M, (out_w, out_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def ffmpeg_writer(path, w, h, fps, crf=21):
    cmd = ["ffmpeg", "-n", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def load_plate(path):
    a = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if a is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)


def save_rgb(path, rgb):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    cv2.imwrite(str(path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))


def load_smoke(cfg, module_path):
    """optional: smoke_v2 scene on the same plate (smoke_v2.py is only imported, never modified)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("smoke_v2", module_path)
    S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
    scfg = json.load(open(cfg))
    return S, scfg


class Composite:
    """flames under smoke: flames modify the plate, smoke_v2 composites on top of that frame."""
    def __init__(self, plate, fcfg, smoke_cfg_path, smoke_module):
        S, scfg = load_smoke(smoke_cfg_path, smoke_module)
        self.fl = FlameScene(plate, fcfg); self.sm = S.SmokeScene(plate, scfg); self.P = plate
        self.protect_bin = self.fl.protect_bin

    def frame(self, t):
        self.sm.Pf = self.fl.frame(t).astype(np.float32)
        return self.sm.frame(t)


def render(scene, cfg, out_path, seconds, fps=30, size=(1080, 1920), push=(1.0, 1.06), writer=None, hold=None):
    n = int(round(seconds * fps)); w, h = size
    p = writer or ffmpeg_writer(out_path, w, h, fps)
    c = tuple(cfg.get("push_center", (0.5, 0.5)))
    for i in range(n):
        f = scene.frame(hold if hold is not None else i / fps)
        p.stdin.write(push_frame(f, i / max(n - 1, 1), w, h, *push, center=c).tobytes())
    if writer is None:
        p.stdin.close(); p.wait()


def render_reel(reel, out_path, base_dir, fps=30, size=(1080, 1920)):
    """reel = {"shots":[{"config":..., "seconds":s, "hold": t (optional: a still frame), "smoke": cfg (optional)}]}"""
    w, h = size; p = ffmpeg_writer(out_path, w, h, fps, crf=int(reel.get("crf", 22)))
    for shot in reel["shots"]:
        cfg = json.load(open(Path(base_dir) / shot["config"])); plate = load_plate(cfg["plate"])
        sc = Composite(plate, cfg, Path(base_dir) / shot["smoke"], Path(base_dir) / reel["smoke_module"]) if shot.get("smoke") else FlameScene(plate, cfg)
        print("shot", shot["config"], shot["seconds"], "s", file=sys.stderr, flush=True)
        render(sc, cfg, None, shot["seconds"], fps, size, tuple(shot.get("push", cfg.get("push", (1.0, 1.06)))), writer=p, hold=shot.get("hold"))
    p.stdin.close(); p.wait()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Animate painted flames on a still plate (vertical-only tongues; plate never moves).")
    ap.add_argument("--config"); ap.add_argument("--plate", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--reel", default=None, help="reel JSON -> one mp4 with hard cuts")
    ap.add_argument("--seconds", type=float, default=7.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", type=int, default=0, help="output width for a quick low-res preview (e.g. 360)")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--smoke", default=None, help="also composite this smoke_v2 config on top")
    ap.add_argument("--smoke-module", default=str(Path(__file__).resolve().parent.parent / "smoke" / "smoke_v2.py"))
    ap.add_argument("--proof", default=None, help="write DIR/proof_<name>.json + diff_<name>.png")
    ap.add_argument("--stats", action="store_true", help="print swing / flicker measurements")
    ap.add_argument("--stills", default=None, help="write before/after 360x640 + full-res PNGs to DIR at --times")
    ap.add_argument("--times", type=float, nargs="*", default=[1.0, 3.0])
    a = ap.parse_args(argv)
    if a.reel:
        render_reel(json.load(open(a.reel)), a.out, Path(a.reel).resolve().parent.parent, a.fps)
        return
    cfg = json.load(open(a.config)); name = Path(a.config).stem
    plate = load_plate(a.plate or cfg["plate"])
    scene = Composite(plate, cfg, a.smoke, a.smoke_module) if a.smoke else FlameScene(plate, cfg)
    push = (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06)))
    if a.out:
        w = a.preview or 1080
        render(scene, cfg, a.out, a.seconds, a.fps, (w, int(round(w * 16 / 9))), push)
    if a.stills:
        d = Path(a.stills); d.mkdir(parents=True, exist_ok=True); c = tuple(cfg.get("push_center", (0.5, 0.5)))
        small = lambda im: cv2.resize(push_frame(im, 0.0, 1080, 1920, 1.0, 1.0, c), (360, 640), interpolation=cv2.INTER_AREA)
        save_rgb(d / f"{name}_before_360x640.png", small(plate))
        for t in a.times:
            f = scene.frame(t)
            save_rgb(d / f"{name}_after_t{t:g}_360x640.png", small(f))
            save_rgb(d / f"{name}_after_t{t:g}_full.png", f)
    if a.proof:
        d = Path(a.proof); d.mkdir(parents=True, exist_ok=True)
        times = list(np.arange(0, a.seconds + 1e-6, 0.5))
        if a.smoke:
            r = dict(note="flames+smoke composite: diff vs plate; allowed = flames zones U smoke allow_mask")
            fl, sm = scene.fl, scene.sm
            allow = fl.zone_mask() | sm.allow_mask(); prot = fl.protect_bin > 0
            H, W = plate.shape[:2]; gm = {n: poly_mask((H, W), [p]) > 0 for n, p in (cfg.get("guards") or {}).items()}
            ch = 0; pw = 0; gw = {n: 0 for n in gm}
            for t in times:
                dd = np.abs(scene.frame(t).astype(np.int16) - plate.astype(np.int16)).max(-1)
                ch += int((dd[~allow] > 0).sum()); pw = max(pw, int(dd[prot].max(initial=0)))
                for n, m in gm.items(): gw[n] = max(gw[n], int(dd[m].max(initial=0)))
            r.update(frames=len(times), changed_px_outside_allowed=ch, max_diff_in_protect=pw, guards_max_diff=gw,
                     **{"pass": ch == 0 and pw == 0 and all(v == 0 for v in gw.values())})
            name = name + "_with_smoke"
        else:
            r = zero_motion_report(plate, cfg, times, cfg.get("guards"))
        r.update(config=str(a.config), plate=str(a.plate or cfg["plate"]), seconds=a.seconds, times_step=0.5)
        print(json.dumps(r, indent=1))
        pj = d / f"proof_{name}.json"
        if pj.exists():
            raise FileExistsError(pj)
        json.dump(r, open(pj, "w"), indent=1)
        f = scene.frame(a.seconds / 2)
        dd = np.abs(f.astype(np.int16) - plate.astype(np.int16)).max(-1)
        heat = cv2.cvtColor(np.clip(dd * 6, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        allow = scene.fl.zone_mask() if a.smoke else scene.zone_mask()
        cnt, _ = cv2.findContours(allow.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(heat, cnt, -1, (60, 200, 60), 1)
        for p in cfg.get("protect", []): cv2.polylines(heat, [np.int32(p)], True, (60, 120, 255), 2)
        for p in (cfg.get("guards") or {}).values(): cv2.polylines(heat, [np.int32(p)], True, (255, 40, 40), 2)
        im = np.hstack([plate, f, heat]); s = 900 / plate.shape[0]
        save_rgb(d / f"diff_{name}.png", cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    if a.stats:
        print(json.dumps(measure(scene.fl if a.smoke else scene, min(a.seconds, 8.0), a.fps), indent=1))


if __name__ == "__main__":
    main()
