"""flames_v3 -- emissive, vertical-only flame animation for still painted plates (Posterity engine R&D).

v3 (over v2, which is frozen in flames_v2.py; with a v2 config v3 renders bit-identical frames):
  * PHONE-READABLE LIGHT SPILL (opt-in per flame, `spill.amp` set): the spill is light, not motion --
    out = plate * G(x, t), G = 1 + clip(amp * s(t), +-max_gain) * fall_t(x) * tint, a per-pixel gain with NO
    resampling of any pixel.  s(t) is the flame's OWN flicker clock re-weighted toward its faster partials
    (`spill.weights`, still 0.55 / 1.3 / 2.9 Hz -> no strobing).  Strong local falloff fall = exp(-(d/r)^p)
    (`falloff` p, small r); `breath` lets the lit pool's reach breathe with the flicker.
    `through_protect`: spill also lights protected faces (brightness/colour only).  Protects still forbid
    every MOTION signal (tongues, sparks, smoke, billow); `spill_protect` polygons block the light too.
  * PROOFS split light from motion: in protects/guards, (a) the frame with spill OFF equals the plate (0 px:
    no motion), (b) the full frame equals round(plate * G) exactly (residual 0 px: only a per-pixel gain was
    applied, no pixel was moved), (c) phase-correlation shift of each guard vs the plate is reported (~0).
  * Painted-plume BILLOW under the flames (`--billow CFG` / reel "billow"): a smoke_v2 scene with only
    `billows` (smoke matte, locked two-phase flow-map, imported by path, unedited) is applied to the plate
    first; flames and emitter smoke go on top.  Outside the matte the sky/sea/ships/horizon stay 0 px.
  * `--spill-report` / `--billow-report`: measured at 360x640 phone scale.

--- v2 notes (still true) ---

v2 (over v1, which is frozen in flames_v1.py):
  * LICK term: every fire's height breathes/licks -- a per-column vertical STRETCH anchored at the fire's own
    (smoothed) base, D_lick = s(x, t) * h, with s from smooth noise (x wavelength ~ the fire width, time rate
    `lick_rate`).  Its tip excursion is sized to the fire (`lick` * hc) with a PHONE-SCALE FLOOR
    (`lick_min_phone` px at 360x640), so tiny fires visibly lick on a phone.  Still map_x == x (vertical only);
    the column tilt |ds/dx|*h is clamped (`lick_tilt_max`) and the noise is smooth, so no squiggles.  The v1
    travelling turbulence stays on top, its slope budget reduced so content never folds.
  * Small fires flicker a little harder (`flicker.small_ref` / `small_boost`); spill follows the same clock.
  * Sparks scale with the fire (size, glow, speed) and are drawn 2x supersampled, so wall torches and small
    fires get fine sparks.
  * `lick_report()`: measured per-fire tongue motion AT PHONE SCALE (tip excursion in 360x640 px per 1 s window).

--- v1 notes (still true) ---

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
  python flames_v3.py --config CFG.json --out OUT.mp4 [--seconds 7] [--preview 360] [--proof DIR] [--stats]
  python flames_v3.py --config CFG.json --stills DIR --times 1 3        (before/after PNGs, no video)
  python flames_v3.py --reel REEL.json --out REEL.mp4
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

    def mix(self, t, weights):
        """same random walks and phases as __call__, re-weighted partials (unit-rms weights)."""
        w = np.float32(weights) / np.sqrt(np.sum(np.square(weights)))
        v = 0.0
        for tab, r, wi, ph in zip(self.tab, self.rates, w, self.ph):
            i = t * r + ph; j = int(i) % 16380; fr = i - math.floor(i); fr = fr * fr * (3 - 2 * fr)
            v += wi * (tab[j] * (1 - fr) + tab[j + 1] * fr)
        return float(v)

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
    # v2 lick (height-breathing stretch, anchored at the fire base)
    lick=0.18,            # peak tip extension, fraction of hc
    lick_min_phone=2.6,   # floor on the peak tip extension in 360x640 phone px (tiny fires)
    lick_s_max=0.45,      # cap on the stretch factor (tip extension <= s/(1-s) * hc)
    lick_rate=1.3,        # Hz-ish: how fast the fire height licks up / falls back
    lick_scale_x=1.0,     # x wavelength of the lick field, fraction of component width (>= 1: whole tongues)
    lick_lx_min=60.0,
    dim_warm=True,        # darkened core pixels take the plate's own dim-flame chroma (no grey holes)     # px: minimum x wavelength of the lick field (tiny fires breathe as a whole, no tilt)
    lick_bias=0.35,       # >0: licks mostly UP (s in [-(1-b)/(1+b), 1] * s_max)
    lick_tilt_max=1.2,    # clamp of |d(D_lick)/dx| (99th pct) -- column-to-column tilt of the tips
    slope_total=0.85,     # total |dD/dy| budget (stretch + turbulence) -> never folds
    # light
    flicker=dict(amp=0.10, self=0.0, tip=0.8, temp=[1.0, 1.35, 1.9], rates=[0.55, 1.3, 2.9], small_ref=70.0, small_boost=1.8),
    spill=dict(strength=0.55, radius_k=1.4, radius_min=40, radius_max=260, tint=[1.0, 0.82, 0.6], region=None,
               # v3 (active when amp is set): G = 1 + clip(amp*s(t), +-max_gain) * fall_t * tint
               amp=None, max_gain=0.6, falloff=2.0, breath=0.0, weights=[0.55, 0.32, 0.18], through_protect=False,
               lit=0.0, lit_range=[0.05, 0.45], skip_flame=True),
    sparks=dict(rate=5.0, min_h=40, life=[1.2, 2.6], v0=[90, 200], vmin=20, tau=0.7, drift=12.0, wobble=5.0,
                size=[1.0, 2.2], bright=0.9, zone_up=3.0, zone_side=0.9, zone=None,
                size_ref=220.0, size_floor=0.4, ss=2),   # v2: size/glow/speed scale with the fire (hc/size_ref)
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
        self.q = q; self.idx = idx; self.Pfull = plate_f
        ys, xs = np.nonzero(Mz)
        self.top, self.bot = int(ys.min()), int(ys.max())
        self.left, self.right = int(xs.min()), int(xs.max())
        kb = K > 0.5
        kys = np.nonzero(kb)[0] if kb.any() else ys
        ftop, fbot = int(kys.min()), int(kys.max())
        self.hc = hc = max(8.0, float(fbot - ftop + 1)); self.wc = wc = max(6.0, float(xs.max() - xs.min() + 1))
        self.amp = float(min(q["tongue"] * hc, q["tongue_px_max"]))
        # v2 lick: peak tip extension sized to the fire, floored at a phone-visible size
        phone = float(q.get("_phone", 1.0 / 3.0))                          # plate px -> 360x640 px
        ext = max(q["lick"] * hc, q["lick_min_phone"] / phone) if q["lick"] > 0 else 0.0
        self.s_max = float(min(q["lick_s_max"], ext / (hc + ext))) if ext > 0 else 0.0
        self.lick_ext_px = self.s_max * hc / max(1e-6, 1 - self.s_max)
        dl = int(math.ceil(self.lick_ext_px)) + 2 if self.s_max > 0 else 0
        dmax = int(math.ceil(self.amp * 2.2)) + 2 + dl                  # |D| is clipped to this
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
        # dimmed-light chroma curve: where the motion darkens a pixel (a gap opens in a white core) the result
        # must look like the plate's own dimmer flame (orange), not a muddy grey.  LUT over v=(R+G)/2 of the
        # 90th pct G/R and B/G among this fire's keyed pixels, made monotone non-decreasing in v.
        self.dimLUT = None
        if q.get("dim_warm", True) and fz.sum() > 50:
            pz = P[fz].astype(np.float32); v = (pz[:, 0] + pz[:, 1]) * 0.5
            gr = pz[:, 1] / np.maximum(pz[:, 0], 1); bg_ = pz[:, 2] / np.maximum(pz[:, 1], 1)
            edges = np.linspace(0, 255, 18); LG, LB = [], []
            for a0, a1 in zip(edges[:-1], edges[1:]):
                mm = (v >= a0) & (v < a1)
                LG.append(np.percentile(gr[mm], 90) if mm.sum() > 10 else np.nan)
                LB.append(np.percentile(bg_[mm], 90) if mm.sum() > 10 else np.nan)
            LG, LB = np.array(LG), np.array(LB); ok = ~np.isnan(LG)
            if ok.sum() >= 2:
                c = 0.5 * (edges[:-1] + edges[1:])
                LG = np.maximum.accumulate(np.interp(c, c[ok], LG[ok])); LB = np.maximum.accumulate(np.interp(c, c[ok], LB[ok]))
                self.dimLUT = (c.astype(np.float32), np.minimum(LG, 0.98).astype(np.float32), np.minimum(LB, 0.92).astype(np.float32))
        # --- geometry: height fraction (0 at the flame base, 1 at its top), per column
        h, w = mz.shape
        self.Y, self.X = np.mgrid[0:h, 0:w].astype(np.float32)
        ybase = fbot - y0; ytop = ftop - y0
        hf = (ybase - self.Y) / max(1.0, ybase - ytop)
        self.L = smoothstep(q["base"], q["free"], hf).astype(np.float32)
        # per-column fire base (lowest keyed row), smoothed across x so the stretch has no column jumps
        kr = K[y0:y1, x0:x1] > 0.5
        has = kr.any(0); cols = np.arange(w)
        bot = np.where(has, h - 1 - np.argmax(kr[::-1], 0), 0).astype(np.float32)
        bot = np.interp(cols, cols[has], bot[has]).astype(np.float32) if has.any() else np.full(w, ybase, np.float32)
        sig = max(2.0, 0.2 * wc)
        bot = cv2.GaussianBlur(bot[None, :], (0, 0), sig, borderType=cv2.BORDER_REPLICATE)[0]
        self.Hb = np.clip(bot[None, :] - self.Y, 0, None).astype(np.float32)   # height above the local base
        self.keep = keep[y0:y1, x0:x1]
        # self-pulse: small fires also breathe their own painted pixels (the plate's glow, not only E_move),
        # strength flicker.self scaled down for big fires (they read through their tongues)
        fq0 = q["flicker"]; sref = fq0.get("small_ref", 70.0) or 70.0
        self.self_amp = float(fq0.get("self", 0.0)) * float(min(1.0, sref / max(hc, 1.0)))
        self.Kself = (K[y0:y1, x0:x1] * self.keep).astype(np.float32) if self.self_amp > 0 else None
        # --- noise mapping into the shared textures (texture feature ~ 64 px)
        self.tex = tex                                                  # texture wavelength ~TEX_LAMBDA texels
        self.sx = TEX_LAMBDA / max(4.0, q["scale_x"] * wc)
        self.slx = TEX_LAMBDA / max(6.0, q["lick_scale_x"] * wc, q["lick_lx_min"])   # lick field x mapping
        self.sy = TEX_LAMBDA / max(6.0, q["scale_y"] * hc)
        self.rise_px = q["lick_hz"] * q["scale_y"] * hc                 # px/s the tongue field travels upward
        self.off = rng.uniform(0, 4096, 8).astype(np.float32)
        fq = q["flicker"]
        self.flick_amp = fq["amp"] * float(np.clip((fq.get("small_ref", 0) / hc) ** 0.5, 1.0, fq.get("small_boost", 1.0))) \
            if fq.get("small_ref") else fq["amp"]
        self.clock = Clock(rng, tuple(fq["rates"]))
        self.temp = np.float32(fq["temp"])
        self.tongue_hz = q["lick_hz"]
        # lick tilt clamp: 99th pct of |ds/dx| * h over the flame, at a few times
        self.lgain = 1.0
        if self.s_max > 0:
            sup = self.Em.max(-1) > 0
            hmax = float(np.percentile(self.Hb[sup], 99)) if sup.any() else hc
            tl = max(float(np.percentile(np.abs(np.diff(self._S(t))), 99)) for t in (0.0, 0.4, 0.9, 1.7, 2.6, 3.1, 4.4, 5.3)) * hmax
            if tl > q["lick_tilt_max"]:
                self.lgain = q["lick_tilt_max"] / tl
        # turbulence slope clamp: measure max |dD/dy| at a few times, scale down if needed (budget shared with the lick)
        self.slope_lim = max(0.25, min(q["slope_max"], q["slope_total"] - self.s_max * self.lgain))
        self.gain = 1.0
        s = max(self._slope(t) for t in (0.0, 0.7, 1.7, 3.1, 5.3))
        if s > self.slope_lim:
            self.gain = self.slope_lim / s
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

    def _S(self, t):
        """lick stretch factor per column, s(x, t) in [-(1-b)/(1+b), 1] * s_max (smooth in x and t)."""
        if self.s_max <= 0:
            return np.zeros(self.X.shape[1], np.float32)
        T = self.tex[1]; tw, th = T.shape[1], T.shape[0]; o = self.off; b = self.q["lick_bias"]
        u = np.mod((np.arange(self.X.shape[1], dtype=np.float32) + self.bb[0]) * self.slx + o[6], tw)
        v = (t * self.q["lick_rate"] * TEX_LAMBDA + o[7]) % th
        i0 = int(v); fr = v - i0; i1 = (i0 + 1) % th
        ui = u.astype(np.int32); uf = u - ui; uj = (ui + 1) % tw
        row = lambda r: T[r, ui] * (1 - uf) + T[r, uj] * uf
        n = row(i0) * (1 - fr) + row(i1) * fr
        g = (np.tanh(1.3 * n) + b) / (1 + b)
        return (self.s_max * g).astype(np.float32)

    def _Dturb(self, t):
        o = self.off; r = self.rise_px * self.sy
        n = 0.75 * self._sample(self.tex[0], o[0], o[1] + r * t) + 0.45 * self._sample(self.tex[0], o[2], o[3] + 1.61 * r * t, 1.4, 1.3)
        return self.amp * self.gain * self.L * n

    def _D(self, t):
        D = self._Dturb(t)
        if self.s_max > 0:
            D = D + (self.lgain * self._S(t))[None, :] * self.Hb       # D > 0 samples lower -> light moves UP
        return np.clip(D, -self.dmax + 1, self.dmax - 1)

    def _slope(self, t):
        """99.5th pct of the vertical stretch |dD/dy| and of the column shear |dD/dx| (scaled to the y limit)."""
        D = self._Dturb(t); sup = self.Em.max(-1) > 0
        lim = getattr(self, "slope_lim", self.q["slope_max"])
        sy = np.abs(np.diff(D, axis=0))[sup[1:]]
        sx = np.abs(np.diff(D, axis=1))[sup[:, 1:]] * (lim / self.q["shear_max"])
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
        return self.flick_amp * self.clock(t)                    # signed fractional brightness change

    def delta(self, t):
        """ROI delta to add to the frame: (W * flicker) - E_move, faded by the protect keep-out."""
        f = self.flick(t)
        Wm = self.tongues(t)
        tipw = 1.0 - self.q["flicker"]["tip"] * 0.5 + self.q["flicker"]["tip"] * self.L      # stronger at the tips
        F = np.clip(1.0 + f * tipw, 0.2, 3.0)[..., None]
        Wm = Wm * F ** self.temp                                                          # brighter = whiter
        d = (Wm - self.Em) * self.keep[..., None]
        if self.Kself is not None:            # plate pixels of the fire itself pulse with the same clock (warm)
            d = d + (self.P - self.Em) * (self.self_amp / max(self.flick_amp, 1e-6) * f * self.Kself)[..., None] * (self.temp / self.temp.max())
        o = self.P + d
        g = np.minimum(o[..., 1], np.maximum(self.rGR * o[..., 0], self.P[..., 1]))
        bl = np.minimum(o[..., 2], np.maximum(self.rBG * g, self.P[..., 2]))
        if self.dimLUT is not None:          # darkened pixels take the plate's own dim-flame chroma
            c, LG, LB = self.dimLUT
            dk = np.clip((self.P[..., 0] + self.P[..., 1] - o[..., 0] - g) / 40.0, 0, 1)   # 0 = not darkened
            R = np.clip(o[..., 0], 0, 255); gw = np.clip(g, 0, 255)
            for _ in range(3):                   # fixed point: chroma chosen at the darkened pixel's own value
                gw = np.minimum(g, np.interp(0.5 * (R + gw), c, LG) * R)
            vv = 0.5 * (R + gw); g = g + dk * (gw - g)
            bw = np.minimum(bl, np.interp(vv, c, LB) * g); bl = np.minimum(bl, bl + dk * (bw - bl))
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
        v3 = sp.get("amp") is not None
        p = float(sp.get("falloff", 2.0)) if v3 else 2.0
        rm = np.ones_like(d)
        if sp.get("region"):
            rm *= poly_mask((H, W), sp["region"])[y0:y1, x0:x1]
        lk = self.q["_skeep"][y0:y1, x0:x1] if (v3 and sp.get("through_protect")) else keep[y0:y1, x0:x1]
        rm = (rm * lk).astype(np.float32)
        if v3 and sp.get("lit", 0) > 0:      # lit surfaces carry more of the flicker than deep shadow
            Lp = luma(self.Pfull[y0:y1, x0:x1]) / 255.0
            a, b = sp.get("lit_range", [0.05, 0.45])
            rm *= ((1 - sp["lit"]) + sp["lit"] * smoothstep(a, b, cv2.GaussianBlur(Lp, (0, 0), 3))).astype(np.float32)
        if v3 and sp.get("skip_flame", True):  # the flame body is animated by the delta; light only its surroundings
            fz = np.maximum(K[y0:y1, x0:x1], Mz[y0:y1, x0:x1].astype(np.float32))      # key + its flame zone (glow)
            rm *= (1.0 - np.clip(cv2.GaussianBlur(fz, (0, 0), 3.0) * 1.5, 0, 1)).astype(np.float32)
        fall = (np.clip((np.exp(-(d / r) ** p) - 0.01) / 0.99, 0, 1) * rm).astype(np.float32)
        br = float(sp.get("breath", 0.0)) if v3 else 0.0
        zone = fall > 0
        if br > 0:
            zone = (np.clip((np.exp(-(d / (r * (1 + br))) ** p) - 0.01) / 0.99, 0, 1) * rm) > 0
        self.spill = dict(bb=(x0, y0, x1, y1), fall=fall, k=float(sp["strength"]), tint=np.float32(sp["tint"]),
                          v3=v3, dn=(d / r).astype(np.float32), rm=rm, p=p, breath=br, zone=zone,
                          amp=float(sp.get("amp") or 0), gmax=float(sp.get("max_gain", 0.6)),
                          weights=tuple(sp.get("weights", [0.55, 0.32, 0.18])))

    def spill_gain(self, t):
        """per-pixel multiplicative light gain on the spill ROI (h, w, 3); t on the pre-rolled clock."""
        s = self.spill
        if not s["v3"]:
            return 1.0 + s["k"] * self.flick(t) * s["fall"][..., None] * s["tint"]
        c = self.clock.mix(t, s["weights"])
        g = float(np.clip(s["amp"] * c, -s["gmax"], s["gmax"]))
        fall = s["fall"]
        if s["breath"] > 0:
            rr = 1.0 + s["breath"] * float(np.clip(c / 2.0, -1, 1))
            fall = np.clip((np.exp(-(s["dn"] / rr) ** s["p"]) - 0.01) / 0.99, 0, 1) * s["rm"]
        return 1.0 + g * fall[..., None] * s["tint"]

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
        self.spark_k = float(np.clip(self.hc / sp.get("size_ref", 220.0), sp.get("size_floor", 0.4), 1.0))
        self.sparks = dict(bb=(x0, y0, x1, y1), zone=zm, ss=int(sp.get("ss", 2)), vmin=sp["vmin"] * min(1.0, 0.5 + 0.5 * sc), tau=sp["tau"],
                           p=dict(                      # one entry per particle (deterministic, seeded)
            birth=rng.uniform(-10.0, span - 10.0, n).astype(np.float32),
            x0=(tx[j] + rng.uniform(-2, 2, n)).astype(np.float32), y0=(ty[j] + rng.uniform(-1, 1, n)).astype(np.float32),
            life=rng.uniform(lo, hi, n).astype(np.float32),
            v0=(rng.uniform(*sp["v0"], n) * min(1.0, 0.45 + 0.55 * sc)).astype(np.float32),
            drift=rng.normal(0, sp["drift"], n).astype(np.float32), wob=(rng.uniform(0.3, 1.0, n) * sp["wobble"]).astype(np.float32),
            wf=rng.uniform(0.4, 1.2, n).astype(np.float32), wp=rng.uniform(0, 6.28, n).astype(np.float32),
            size=(rng.uniform(*sp["size"], n) * self.spark_k).astype(np.float32), b=(rng.uniform(0.55, 1.0, n) * sp["bright"]).astype(np.float32)))

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
        ss = s.get("ss", 1); k = getattr(self, "spark_k", 1.0)
        canvas = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss, 3), np.uint8)
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
            th = max(1, int(round(ss * p["size"][i] * (1 - 0.4 * u[i]))))
            m = 16 * ss
            cv2.line(canvas, (int((xb[i] - x0) * m), int((yb[i] - y0) * m)), (int((xa[i] - x0) * m), int((ya[i] - y0) * m)),
                     c, th, cv2.LINE_AA, 4)
        f = canvas.astype(np.float32)
        if ss > 1:
            f = cv2.resize(f, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA) * (1.0 + 0.35 * (ss - 1) * (1 - k))
        f = cv2.GaussianBlur(f, (0, 0), 0.5 + 0.1 * k) + 0.5 * cv2.GaussianBlur(f, (0, 0), 1.2 + 1.8 * k)    # core + glow (scaled)
        return f * s["zone"][..., None]


def phone_factor(shape, out_w=1080, out_h=1920, phone_w=360):
    """plate px -> phone (360x640) px for a cover-fit 1080x1920 render (push z=1)."""
    H, W = shape[:2]
    return max(out_w / W, out_h / H) * phone_w / out_w


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
        sprot = poly_mask((H, W), config.get("spill_protect"))          # v3: polygons the LIGHT may not reach
        self.spill_protect_bin = sprot
        skeep = keepout_fade(sprot.astype(np.uint8), float(config.get("protect_feather", 6))) if sprot.any() \
            else np.ones((H, W), np.float32)
        for fi, spec in enumerate(config.get("flames", [])):
            q = _merge(FLAME_DEFAULTS, spec)
            q["_phone"] = phone_factor(plate_rgb.shape); q["_skeep"] = skeep
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
                    x0, y0, x1, y1 = c.spill["bb"]
                    img[y0:y1, x0:x1] *= c.spill_gain(t)
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

    def light_only(self, t, base=None):
        """the frame with ONLY the spill gain applied (same arithmetic order as frame()): the reference for the
        light-vs-motion proof on protected faces."""
        img = (self.Pf if base is None else base.astype(np.float32)).copy()
        t = t + self.preroll
        for c in self.comps:
            if c.spill:
                x0, y0, x1, y1 = c.spill["bb"]
                img[y0:y1, x0:x1] *= c.spill_gain(t)
        return np.clip(np.rint(img), 0, 255).astype(np.uint8)

    # ---- masks for the proofs
    def zone_mask(self, flame=True, spill=True, sparks=True):
        H, W = self.P.shape[:2]; m = np.zeros((H, W), bool)
        for c in self.comps:
            if flame:
                x0, y0, x1, y1 = c.bb; m[y0:y1, x0:x1] |= c.zone
            if spill and c.spill:
                x0, y0, x1, y1 = c.spill["bb"]; m[y0:y1, x0:x1] |= c.spill["zone"]
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


def lick_report(scene, seconds=7.0, fps=30, win=1.0, step=0.5, q_tip=0.12):
    """Measured tongue motion per fire AT PHONE SCALE (flicker-invariant).  For each component the displayed
    flame light (E_move + delta = frame - bg, spill and sparks excluded) is downscaled to 360x640 px.  Per column
    the tip height is where the light, accumulated from the top, reaches `q_tip` of that column's total (a
    brightness-scale-invariant tip, so pure flicker scores 0).  For every 1 s window (stepped 0.5 s): per column
    tip max - min in phone px, light-weighted mean over columns -> `lick_px_*`.  `change_frac_*` = fraction of
    the fire's phone pixels whose luma swings >= 6 levels within the window (this one includes flicker)."""
    n = int(round(seconds * fps)); out = []
    ph = phone_factor(scene.P.shape)
    for c in scene.comps:
        x0, y0, x1, y1 = c.bb; w = max(1, int(round((x1 - x0) * ph))); h = max(1, int(round((y1 - y0) * ph)))
        sm = lambda a: cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
        L0 = sm(luma(c.Em)); cw = L0.sum(0); cols = cw > 0.25 * max(cw.max(), 1e-6)
        tips, lums = [], []
        for i in range(n):
            t = i / fps + scene.preroll
            Lt = sm(luma(np.clip(c.Em + c.delta(t), 0, None)))
            cs = np.cumsum(Lt, 0); tot = cs[-1]
            tip = (cs < q_tip * np.maximum(tot, 1e-6)).sum(0).astype(np.float32)
            # sub-pixel: interpolate inside the crossing row
            j = np.clip(tip.astype(int), 0, h - 1); prev = np.where(j > 0, cs[np.maximum(j - 1, 0), np.arange(w)], 0)
            fr = (q_tip * tot - prev) / np.maximum(Lt[j, np.arange(w)], 1e-6)
            tips.append(tip + np.clip(fr, 0, 1)); lums.append(Lt)
        tips = np.array(tips)[:, cols]; wts = cw[cols] / cw[cols].sum()
        lums = np.array(lums); zone = (sm(c.zone.astype(np.float32)) > 0.2)
        wl, ws = int(round(win * fps)), int(round(step * fps)); lk, cf, lkmax = [], [], []
        for a in range(0, n - wl + 1, ws):
            T = tips[a:a + wl]; p2p = T.max(0) - T.min(0)
            lk.append(float((p2p * wts).sum())); lkmax.append(float(p2p.max()))
            sw = lums[a:a + wl].max(0) - lums[a:a + wl].min(0)
            cf.append(float((sw[zone] >= 6).mean()) if zone.any() else 0.0)
        out.append(dict(name=c.name, hc_px=int(c.hc), hc_phone_px=round(c.hc * ph, 1), bbox=[int(v) for v in c.bb],
                        lick_px_median=round(float(np.median(lk)), 2), lick_px_min=round(float(np.min(lk)), 2),
                        best_column_lick_px_median=round(float(np.median(lkmax)), 2),
                        change_frac_median=round(float(np.median(cf)), 3), change_frac_min=round(float(np.min(cf)), 3),
                        planned_tip_ext_phone_px=round(c.lick_ext_px * c.lgain * ph, 2),
                        flicker_amp=round(c.flick_amp, 3), sparks=bool(c.sparks)))
    return out


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
                tongue_amp_px=[round(c.amp * c.gain, 1) for c in scene.comps[:12]],
                lick_tip_ext_px=[round(c.lick_ext_px * c.lgain, 1) for c in scene.comps[:30]])


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
    """billow (painted plumes, UNDER the flames) -> flames -> emitter smoke (OVER).  smoke_v2 imported by path, unedited."""
    def __init__(self, plate, fcfg, smoke_cfg_path=None, smoke_module=None, billow_cfg_paths=()):
        self.P = plate; self.fl = FlameScene(plate, fcfg); self.protect_bin = self.fl.protect_bin
        self.sm = None; self.bl = []
        if smoke_cfg_path:
            S, scfg = load_smoke(smoke_cfg_path, smoke_module); self.sm = S.SmokeScene(plate, scfg)
        for b in (billow_cfg_paths or []):
            S, bcfg = load_smoke(b, smoke_module)
            assert not bcfg.get("emitters") and not bcfg.get("fires"), "a billow config holds billows only"
            self.bl.append(S.SmokeScene(plate, bcfg))

    def base(self, t):
        img = self.P
        for b in self.bl:
            b.Pf = img.astype(np.float32); img = b.frame(t)
        return img

    def frame(self, t):
        f = self.fl.frame(t, base=self.base(t) if self.bl else None)
        if self.sm is None:
            return f
        self.sm.Pf = f.astype(np.float32)
        return self.sm.frame(t)

    def matte(self):
        H, W = self.P.shape[:2]; m = np.zeros((H, W), np.float32)
        for b in self.bl:
            m = np.maximum(m, b.matte())
        return m

    def allow_mask(self):
        m = self.fl.zone_mask() | (self.matte() > 0)
        return m | self.sm.allow_mask() if self.sm is not None else m


def _shift(a, b):
    """phase-correlation shift (px) between two luma patches (structure displacement; ~0 = nothing moved)."""
    a = np.float32(a); b = np.float32(b)
    if min(a.shape) < 8:
        return 0.0
    win = cv2.createHanningWindow(a.shape[::-1], cv2.CV_32F)
    (dx, dy), _ = cv2.phaseCorrelate(a, b, win)
    return round(float(math.hypot(dx, dy)), 3)


def proof_v3(plate, cfg, scene, times, billow_guards_ok=()):
    """zero-motion proof that separates LIGHT from MOTION.
       outside allowed (flame U spill U spark zones U smoke footprints U billow matte)       -> 0 px changed
       flames only (spill, sparks off): outside the flame zone                               -> 0 px changed
       protects + guards, MOTION: frame with the spill gain OFF (everything else on) == plate  -> 0 px
       protects + guards, LIGHT : full frame == round(plate * G_spill) exactly (no resampling) -> residual 0 px
       guards: phase-correlation shift vs plate (reported), matte overlap (0 unless billow_guards_ok)."""
    comp = isinstance(scene, Composite); fl = scene.fl if comp else scene
    H, W = plate.shape[:2]; P16 = plate.astype(np.int16)
    mat = (scene.matte() > 0) if comp else np.zeros((H, W), bool)
    allow = scene.allow_mask() if comp else fl.zone_mask()
    prot = (fl.protect_bin > 0) & ~mat
    only = FlameScene(plate, fl.cfg, sparks=False, spill=False); fz = only.zone_mask(spill=False, sparks=False)
    gm = {n: poly_mask((H, W), [p]) > 0 for n, p in (cfg.get("guards") or {}).items()}
    gmo = {n: (m & ~mat) if n in billow_guards_ok else m for n, m in gm.items()}
    r = dict(frames=len(times), changed_px_outside_allowed=0, flames_only_changed_px_outside_flame_zone=0,
             protect_px=int(prot.sum()), protect_motion_max_diff=0, protect_light_residual_max=0,
             protect_light_change_max=0, protect_lit_px_max=0,
             guards_motion_max_diff={n: 0 for n in gm}, guards_light_residual_max={n: 0 for n in gm},
             guards_light_change_max={n: 0 for n in gm}, guards_shift_px_max={n: 0.0 for n in gm},
             guards_matte_overlap_px={n: int((m & mat).sum()) for n, m in gm.items()},
             allowed_fraction=round(float(allow.mean()), 4), components=len(fl.comps))
    if comp and scene.bl:
        r.update(matte_px=int(mat.sum()), matte_protect_overlap_px=int(((fl.protect_bin > 0) & mat).sum()),
                 billow_only_changed_px_outside_matte=0)
    gl = lambda im: luma(im)
    for t in times:
        f = scene.frame(t); d = np.abs(f.astype(np.int16) - P16).max(-1)
        r["changed_px_outside_allowed"] += int((d[~allow] > 0).sum())
        fl.use_spill = False
        fm = scene.frame(t); fl.use_spill = True
        dm = np.abs(fm.astype(np.int16) - P16).max(-1)
        lo = fl.light_only(t); dr = np.abs(f.astype(np.int16) - lo.astype(np.int16)).max(-1)
        r["protect_motion_max_diff"] = max(r["protect_motion_max_diff"], int(dm[prot].max(initial=0)))
        r["protect_light_residual_max"] = max(r["protect_light_residual_max"], int(dr[prot].max(initial=0)))
        r["protect_light_change_max"] = max(r["protect_light_change_max"], int(d[prot].max(initial=0)))
        r["protect_lit_px_max"] = max(r["protect_lit_px_max"], int((d[prot] > 0).sum()))
        for n, m in gmo.items():
            r["guards_motion_max_diff"][n] = max(r["guards_motion_max_diff"][n], int(dm[m].max(initial=0)))
            r["guards_light_residual_max"][n] = max(r["guards_light_residual_max"][n], int(dr[m].max(initial=0)))
            r["guards_light_change_max"][n] = max(r["guards_light_change_max"][n], int(d[m].max(initial=0)))
            ys, xs = np.nonzero(gm[n])
            if len(xs):
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                r["guards_shift_px_max"][n] = max(r["guards_shift_px_max"][n], _shift(gl(plate[y0:y1, x0:x1]), gl(f[y0:y1, x0:x1])))
        d2 = np.abs(only.frame(t).astype(np.int16) - P16).max(-1)
        r["flames_only_changed_px_outside_flame_zone"] += int((d2[~fz] > 0).sum())
        if comp and scene.bl:
            db = np.abs(scene.base(t).astype(np.int16) - P16).max(-1)
            r["billow_only_changed_px_outside_matte"] += int((db[~mat] > 0).sum())
    ok_ov = all(v == 0 for n, v in r["guards_matte_overlap_px"].items() if n not in billow_guards_ok)
    r["pass"] = bool(r["changed_px_outside_allowed"] == 0 and r["flames_only_changed_px_outside_flame_zone"] == 0
                     and r["protect_motion_max_diff"] == 0 and r["protect_light_residual_max"] == 0
                     and all(v == 0 for v in r["guards_motion_max_diff"].values())
                     and all(v == 0 for v in r["guards_light_residual_max"].values()) and ok_ov
                     and r.get("billow_only_changed_px_outside_matte", 0) == 0)
    return r


def _phone(img):
    return cv2.resize(img, (360, 640), interpolation=cv2.INTER_AREA)


def spill_report(scene, surfaces, seconds=7.0, fps=30, win=1.0, step=0.5):
    """local light swing on named surfaces AT PHONE SCALE (360x640, no push).  Per surface and per 1 s window:
       mean-luma peak-to-peak in % of the mean (`swing_pct`), the median pixel's luma p2p in 8-bit levels
       (`px_p2p_levels`) and the share of its pixels swinging >= 4 levels (`frac_px_ge4`).  Plus whole-frame swing.
       Phone pixels touched by a flame zone are removed from every surface and sparks are switched off while measuring,
       so this measures light only (the whole-frame numbers here are therefore without sparks)."""
    n = int(round(seconds * fps)); H, W = scene.P.shape[:2]
    fl = scene.fl if isinstance(scene, Composite) else scene      # surfaces exclude the flame/spark zones (pure light)
    mot = _phone((fl.zone_mask(spill=False, sparks=False) > 0).astype(np.float32)) > 0
    sp0 = fl.use_sparks; fl.use_sparks = False                      # sparks off while measuring light
    ms = {k: (_phone((poly_mask((H, W), [p]) > 0).astype(np.float32)) > 0.5) & ~mot for k, p in surfaces.items()}
    Ls = []
    for i in range(n):
        Ls.append(luma(_phone(scene.frame(i / fps))))
    fl.use_sparks = sp0
    Ls = np.array(Ls); wl, ws = int(round(win * fps)), int(round(step * fps)); out = {}
    for k, m in ms.items():
        mm = Ls[:, m].mean(1); sw, pp, fr = [], [], []
        for a in range(0, n - wl + 1, ws):
            seg = mm[a:a + wl]; sw.append((seg.max() - seg.min()) / seg.mean() * 100)
            px = Ls[a:a + wl][:, m]; p2 = px.max(0) - px.min(0); pp.append(np.median(p2)); fr.append((p2 >= 4).mean())
        out[k] = dict(mean_luma=round(float(mm.mean()), 1), swing_pct_median=round(float(np.median(sw)), 2),
                      swing_pct_min=round(float(np.min(sw)), 2), px_p2p_levels_median=round(float(np.median(pp)), 2),
                      frac_px_ge4_median=round(float(np.median(fr)), 3), phone_px=int(m.sum()))
    g = Ls.mean((1, 2)); x = g - g.mean(); P = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(n, 1 / fps)
    out["_whole_frame"] = dict(swing_pct=round(float((g.max() - g.min()) / g.mean() * 100), 3),
                               max_step_pct=round(float(np.abs(np.diff(g)).max() / g.mean() * 100), 3),
                               energy_above_5hz=round(float(P[f > 5].sum() / max(P[1:].sum(), 1e-12)), 4))
    return out


def billow_report(scene, seconds=7.0, fps=30):
    """billow visibility AT PHONE SCALE (billow stage only, no push): per 1 s window the share of matte pixels whose
       luma swings >= 6 levels, and the Farneback optical-flow displacement (phone px) between t and t+1 s inside the
       matte (median / 90th pct).  Outside the matte the flow image is not used (it is 0 px by the proof)."""
    m = _phone(scene.matte()) > 0.3; n = int(round(seconds * fps))
    G = [luma(_phone(scene.base(i / fps))) for i in range(n)]
    G = np.array(G); cf, fm, f9 = [], [], []
    for a in range(0, n - fps + 1, fps // 2):
        sw = G[a:a + fps].max(0) - G[a:a + fps].min(0); cf.append(float((sw[m] >= 6).mean()))
        fl = cv2.calcOpticalFlowFarneback(np.uint8(np.clip(G[a], 0, 255)), np.uint8(np.clip(G[a + fps - 1], 0, 255)),
                                          None, 0.5, 3, 15, 3, 5, 1.1, 0)
        mag = np.hypot(fl[..., 0], fl[..., 1])[m]; fm.append(float(np.median(mag))); f9.append(float(np.percentile(mag, 90)))
    return dict(matte_phone_px=int(m.sum()), matte_frac_of_frame=round(float(m.mean()), 4),
                frac_matte_px_ge6_per_1s_median=round(float(np.median(cf)), 3), frac_min=round(float(np.min(cf)), 3),
                flow_1s_median_px=round(float(np.median(fm)), 2), flow_1s_p90_px=round(float(np.median(f9)), 2))


def composite_swing(scene, seconds=7.0, fps=30):
    n = int(round(seconds * fps)); g = np.array([luma(scene.frame(i / fps)).mean() for i in range(n)])
    x = g - g.mean(); P = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(n, 1 / fps)
    return dict(plate_swing_pct=round(float((g.max() - g.min()) / g.mean() * 100), 3),
                plate_max_step_pct=round(float(np.abs(np.diff(g)).max() / g.mean() * 100), 3),
                energy_above_5hz=round(float(P[f > 5].sum() / max(P[1:].sum(), 1e-12)), 4))


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
    """reel = {"shots":[{"config":..., "seconds":s, "hold": t, "smoke": cfg, "billow": [cfgs]}]}"""
    w, h = size; p = ffmpeg_writer(out_path, w, h, fps, crf=int(reel.get("crf", 22)))
    for shot in reel["shots"]:
        cfg = json.load(open(Path(base_dir) / shot["config"])); plate = load_plate(cfg["plate"])
        sm = Path(base_dir) / shot["smoke"] if shot.get("smoke") else None
        bl = [Path(base_dir) / b for b in shot.get("billow", [])]
        sc = Composite(plate, cfg, sm, Path(base_dir) / reel["smoke_module"], bl) if (sm or bl) else FlameScene(plate, cfg)
        print("shot", shot["config"], shot["seconds"], "s", file=sys.stderr, flush=True)
        render(sc, cfg, None, shot["seconds"], fps, size, tuple(shot.get("push", cfg.get("push", (1.0, 1.06)))), writer=p, hold=shot.get("hold"))
    p.stdin.close(); p.wait()


def _new(path):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Animate painted flames on a still plate (vertical-only tongues; plate never moves).")
    ap.add_argument("--config"); ap.add_argument("--plate", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--reel", default=None, help="reel JSON -> one mp4 with hard cuts")
    ap.add_argument("--seconds", type=float, default=7.0); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", type=int, default=0, help="output width for a quick low-res preview (e.g. 360)")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--smoke", default=None, help="also composite this smoke_v2 config on top")
    ap.add_argument("--billow", nargs="*", default=[], help="smoke_v2 billow-only configs applied UNDER the flames")
    ap.add_argument("--smoke-module", default=str(Path(__file__).resolve().parent.parent / "smoke" / "smoke_v2.py"))
    ap.add_argument("--proof", default=None, help="write DIR/proof_<name>.json + diff_<name>.png")
    ap.add_argument("--stats", default=None, help="write swing / flicker measurements (JSON) to this path")
    ap.add_argument("--stills", default=None, help="write before/after 360x640 + full-res PNGs to DIR at --times")
    ap.add_argument("--times", type=float, nargs="*", default=[1.0, 3.0])
    ap.add_argument("--phone-report", default=None, help="per-fire phone-scale lick measurements (JSON)")
    ap.add_argument("--spill-report", default=None, help="phone-scale light swing on named surfaces (JSON)")
    ap.add_argument("--surfaces", default=None, help="JSON with {name: polygon}; default: config 'spill_surfaces'")
    ap.add_argument("--billow-report", default=None, help="phone-scale billow visibility (JSON)")
    ap.add_argument("--tag", default="", help="suffix for proof/diff names")
    a = ap.parse_args(argv)
    if a.reel:
        render_reel(json.load(open(a.reel)), _new(a.out), Path(a.reel).resolve().parent.parent, a.fps)
        return
    cfg = json.load(open(a.config)); name = Path(a.config).stem + a.tag
    plate = load_plate(a.plate or cfg["plate"])
    comp = bool(a.smoke or a.billow)
    scene = Composite(plate, cfg, a.smoke, a.smoke_module, a.billow) if comp else FlameScene(plate, cfg)
    fl = scene.fl if comp else scene
    push = (1.0, 1.0) if a.no_push else tuple(cfg.get("push", (1.0, 1.06)))
    if a.out:
        w = a.preview or 1080
        render(scene, cfg, _new(a.out), a.seconds, a.fps, (w, int(round(w * 16 / 9))), push)
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
        if a.smoke: name += "_with_smoke"
        if a.billow: name += "_billow"
        pj = _new(d / f"proof_{name}.json")
        times = list(np.arange(0, a.seconds + 1e-6, 0.5))
        r = proof_v3(plate, cfg, scene, times, tuple(cfg.get("billow_guards_ok", [])))
        r.update(config=str(a.config), smoke=a.smoke, billow=a.billow, plate=str(a.plate or cfg["plate"]),
                 seconds=a.seconds, times_step=0.5)
        print(json.dumps(r, indent=1))
        json.dump(r, open(pj, "w"), indent=1)
        f = scene.frame(a.seconds / 2)
        dd = np.abs(f.astype(np.int16) - plate.astype(np.int16)).max(-1)
        heat = cv2.cvtColor(np.clip(dd * 6, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        allow = fl.zone_mask()
        cnt, _ = cv2.findContours(allow.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(heat, cnt, -1, (60, 200, 60), 1)
        if comp and scene.bl:
            cnt, _ = cv2.findContours((scene.matte() > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(heat, cnt, -1, (220, 220, 60), 1)
        for p in cfg.get("protect", []): cv2.polylines(heat, [np.int32(p)], True, (60, 120, 255), 2)
        for p in (cfg.get("guards") or {}).values(): cv2.polylines(heat, [np.int32(p)], True, (255, 40, 40), 2)
        im = np.hstack([plate, f, heat]); s = 900 / plate.shape[0]
        save_rgb(d / f"diff_{name}.png", cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA))
    if a.stats:
        o = _new(a.stats); r = measure(fl, min(a.seconds, 8.0), a.fps)
        if comp:
            r["composite"] = composite_swing(scene, min(a.seconds, 8.0), a.fps)
        json.dump(r, open(o, "w"), indent=1); print(json.dumps({k: v for k, v in r.items() if not isinstance(v, list)}, indent=1))
    if a.spill_report:
        o = _new(a.spill_report)
        surf = json.load(open(a.surfaces)) if a.surfaces else cfg["spill_surfaces"]
        r = spill_report(scene, surf, min(a.seconds, 8.0), a.fps); r["_config"] = str(a.config)
        json.dump(r, open(o, "w"), indent=1)
        for k, v in r.items():
            print(k, v)
    if a.billow_report:
        o = _new(a.billow_report); r = billow_report(scene, min(a.seconds, 8.0), a.fps); r["_config"] = a.billow
        json.dump(r, open(o, "w"), indent=1); print(r)
    if a.phone_report:
        pr = _new(a.phone_report)
        r = lick_report(fl, min(a.seconds, 8.0), a.fps)
        json.dump(r, open(pr, "w"), indent=1)
        for e in r:
            print(f"{e['name']:16s} hc {e['hc_phone_px']:5.1f}ph  lick med {e['lick_px_median']:5.2f} min {e['lick_px_min']:5.2f} "
                  f"bestcol {e['best_column_lick_px_median']:5.2f}  change med {e['change_frac_median']:.2f} min {e['change_frac_min']:.2f}  sparks {e['sparks']}")


if __name__ == "__main__":
    main()
