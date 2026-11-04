#!/usr/bin/env python3
"""Posterity element-motion engine (R&D 2026-10-22).  One CLI:  animate.py --config configs/<plate>.json [--repeat-check]

Renders a BEFORE|AFTER review clip: BEFORE = plate + standard StablePush (scale-only centre zoom z0->z1),
AFTER = same zoom + preset layers.  Presets: water, map-light, sky, atmos, smoke, fire-torchlight, foliage, light-shift.
Everything is seeded (numpy Generator seeded from config seed + layer index) -> identical input gives identical frames;
x264 is run with fixed threads + bitexact flags so the MP4 is byte-identical too (--repeat-check proves it).
Stability QC runs on every render: plate-space and output-space |AFTER-BEFORE| outside the union of layer masks,
displacement magnitude (overall / outside masks / inside protect masks).  Writes <name>.mp4, <name>.qc.json, QC stills.
Never overwrites an existing file unless it was produced by this engine for the same name in the same out dir
(the engine only ever writes into the config's out_dir under this iterations folder)."""
import argparse, hashlib, json, math, os, subprocess, sys, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspace/posterity"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
cv2.setNumThreads(4)

# ----------------------------------------------------------------------------------------------- utilities
def resolve(p):
    if os.path.isabs(p): return p
    for base in (ENGINE_DIR, ROOT):
        q = os.path.join(base, p)
        if os.path.exists(q): return q
    raise FileNotFoundError(p)

def load_mask(p, shape):
    m = cv2.imread(resolve(p), cv2.IMREAD_GRAYSCALE)
    if m is None: raise FileNotFoundError(p)
    if m.shape != shape: m = cv2.resize(m, (shape[1], shape[0]), interpolation=cv2.INTER_LINEAR)
    return m.astype(np.float32) / 255.0

def pnoise(rng, h, w, lo, hi, beta=2.0, ax=1.0, ay=1.0):
    """Seamless (periodic) fractal noise, zero mean / unit std.  lo = largest feature (px), hi = smallest; ax/ay stretch."""
    fy = np.fft.fftfreq(h)[:, None] * ay; fx = np.fft.rfftfreq(w)[None, :] * ax
    f = np.sqrt(fx * fx + fy * fy)
    amp = (f * f + (1.0 / lo) ** 2) ** (-beta / 4) * np.exp(-(f * hi) ** 2)
    spec = (rng.standard_normal((h, w // 2 + 1)) + 1j * rng.standard_normal((h, w // 2 + 1))) * amp
    n = np.fft.irfft2(spec, s=(h, w)).astype(np.float32)
    n -= n.mean(); return n / (n.std() + 1e-8)

def scroll(tex, dx, dy):
    """dst(x,y) = tex(x+dx, y+dy) with wrap -> content appears to move by (-dx,-dy)."""
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(tex, M, (tex.shape[1], tex.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_WRAP)

def smoothstep(a, b, x):
    x = np.clip((x - a) / (b - a + 1e-9), 0, 1); return x * x * (3 - 2 * x)

def ease(t, t0, t1):
    return float(smoothstep(t0, t1, np.float32(t)))

def lum(img):
    return (0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]) / 255.0

def gauss_dot(img, x, y, sigma, col, gain, allow=None):
    H, W = img.shape[:2]; R = int(math.ceil(sigma * 3)) + 1; xi, yi = int(round(x)), int(round(y))
    x0, x1, y0, y1 = max(0, xi - R), min(W, xi + R + 1), max(0, yi - R), min(H, yi + R + 1)
    if x0 >= x1 or y0 >= y1: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sigma * sigma)) * gain
    if allow is not None: d *= allow[y0:y1, x0:x1]
    img[y0:y1, x0:x1] += d[..., None] * np.float32(col)

def dilate(b, px):
    if px <= 0: return b
    k = 2 * int(px) + 1
    return cv2.dilate(b.astype(np.uint8), np.ones((k, k), np.uint8)) > 0

def taper(mask, erode_px, blur_px):
    m = (mask > 0.5).astype(np.uint8)
    if erode_px > 0: m = cv2.erode(m, np.ones((2 * erode_px + 1,) * 2, np.uint8))
    m = m.astype(np.float32)
    if blur_px > 0: m = cv2.GaussianBlur(m, (0, 0), blur_px) * (m > 0)   # zero exactly at/after the eroded edge
    return m * mask

def catmull(points, n=24):
    P = np.float32(points); P = np.vstack([P[:1], P, P[-1:]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            s2, s3 = s * s, s * s * s
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3))
    out.append(P[-2]); return np.float32(out)

# ----------------------------------------------------------------------------------------------- presets
class Preset:
    """Base: stage hooks.  disp(t)->(dx,dy)|None ; shade/overlay/grade/emit(img,t) mutate img in place ; allow()->bool HxW."""
    def __init__(self, ctx, mask, strength, p, rng):
        self.ctx, self.m, self.k, self.p, self.rng = ctx, mask, float(strength), p, rng
        self.H, self.W = ctx["H"], ctx["W"]
        self.Y, self.X = ctx["Y"], ctx["X"]
    def disp(self, t): return None
    def shade(self, img, t): pass
    def overlay(self, img, t): pass
    def grade(self, img, t): pass
    def emit(self, img, t): pass
    def allow(self): return self.m > 1e-4

class Water(Preset):
    """Painted-water motion: travelling ripple displacement (tapered to 0 at the shore) + luminance shimmer + optional sun glints."""
    D = dict(amp_px=1.2, dir_deg=0.0, speed=14.0, lo=140, hi=6, stretch=3.0, shimmer=0.07, glint=0.0, glint_thresh=2.4,
             glint_color=[255, 246, 220], glint_lum_power=2.0, coast_margin_px=3, coast_blur_px=4)
    def __init__(s, *a):
        super().__init__(*a); p = {**s.D, **s.p}; s.p = p; r = s.rng; H, W = s.H, s.W
        s.dm = taper(s.m, int(p["coast_margin_px"] + math.ceil(p["amp_px"])), p["coast_blur_px"])
        st = p["stretch"]
        s.A = pnoise(r, H, W, p["lo"], p["hi"] * 2, ax=st); s.B = pnoise(r, H, W, p["lo"] * 0.6, p["hi"] * 2, ax=st)
        s.S1 = pnoise(r, H, W, p["lo"] * 0.4, p["hi"], 2.2, ax=st); s.S2 = pnoise(r, H, W, p["lo"] * 0.3, p["hi"], 2.2, ax=st)
        a = math.radians(p["dir_deg"]); s.u = (math.cos(a), math.sin(a))
        L = lum(s.ctx["plate"]); mm = s.m > 0.5
        s.gm = s.m * np.clip(L / (np.percentile(L[mm], 99) + 1e-6), 0, 1) ** p["glint_lum_power"] if mm.any() else s.m
    def _sc(s, tex, v, t, sign=1.0, ang=0.0):
        ux, uy = s.u; c, si = math.cos(ang), math.sin(ang); ux, uy = ux * c - uy * si, ux * si + uy * c
        return scroll(tex, -sign * ux * v * t, -sign * uy * v * t)
    def disp(s, t):
        p = s.p; v = p["speed"]
        f = np.tanh(0.6 * s._sc(s.A, v, t) + 0.45 * s._sc(s.B, 0.65 * v, t, -1.0, 0.5))
        a = p["amp_px"] * s.k * s.dm
        return a * f, 0.45 * a * np.tanh(0.7 * s._sc(s.B, 0.8 * v, t, 1.0, -0.4))
    def shade(s, img, t):
        p = s.p; v = p["speed"] * 1.3
        r1, r2 = s._sc(s.S1, v, t), s._sc(s.S2, 0.7 * v, t, -1.0, 0.35)
        g = 1 + p["shimmer"] * s.k * np.tanh(0.8 * (r1 + r2)) * s.m
        img *= g[..., None]
        if p["glint"] > 0:
            G = np.clip(r1 + r2 - p["glint_thresh"], 0, None) ** 2 * s.gm
            img += (p["glint"] * s.k * 60.0 * G)[..., None] * (np.float32(p["glint_color"]) / 255.0)
    def allow(s): return dilate(s.m > 1e-4, math.ceil(s.p["amp_px"]) + 1)

class MapLight(Preset):
    """Map lighting kit: parchment light sweep, drifting cloud shadows, ink route draw-on, glowing place markers."""
    def __init__(s, *a):
        super().__init__(*a); p = s.p; r = s.rng; H, W = s.H, s.W
        s.parch = {**dict(strength=0.06, angle_deg=30, width_frac=0.45, x_from=-0.4, x_to=0.9, warm=[1.0, 0.88, 0.66]), **p.get("parchment", {})} if "parchment" in p else None
        s.cloud = {**dict(strength=0.16, lo=420, hi=110, beta=3.0, coverage=0.35, softness=1.2, velocity=[20.0, 6.0], tint=[1.0, 0.93, 0.80]), **p.get("cloud_shadows", {})} if "cloud_shadows" in p else None
        if s.cloud:
            c = s.cloud; s.C1 = pnoise(r, H, W, c["lo"], c["hi"], c["beta"]); s.C2 = pnoise(r, H, W, c["lo"] * 0.5, c["hi"], c["beta"])
            s.c0 = float(np.quantile(0.8 * s.C1 + 0.45 * s.C2, 1 - c["coverage"]))
        s.route = {**dict(t0=0.3, t1=3.0, width=3.2, color=[112, 26, 20], opacity=0.88, dash=[16, 8], head_glow=1.0,
                          head_color=[255, 190, 110], head_sigma=5.0, supersample=4, halo=0.35, halo_sigma=3.0, halo_color=[255, 200, 140]), **p["route"]} if "route" in p else None
        if s.route:
            R = s.route; s.path = catmull(R["points"]); seg = np.linalg.norm(np.diff(s.path, axis=0), axis=1)
            s.cum = np.concatenate([[0], np.cumsum(seg)]); s.Lr = float(s.cum[-1])
            pad = int(R["width"] * 3 + R["head_sigma"] * 4)
            x0, y0 = np.floor(s.path.min(0)).astype(int) - pad; x1, y1 = np.ceil(s.path.max(0)).astype(int) + pad
            s.rbb = (max(0, x0), max(0, y0), min(W, x1), min(H, y1))
            s.paper = np.clip(0.82 + 0.18 * pnoise(r, H, W, 12, 1.5), 0.55, 1.0)       # ink takes unevenly on paper
        s.markers = [{**dict(t_on=0.0, radius=9.0, color=[255, 176, 90], pulse_hz=0.55, gain=1.0, ring=True, style="glow", width=2.2,
                              dot=2.2, draw_s=0.25, start_deg=-100), **mk} for mk in p.get("markers", [])]
        s.ink = {**dict(wet_color=[52, 12, 12], dry_color=[118, 48, 34], wet_opacity=0.97, dry_opacity=0.86, dry_time=0.7, wick_time=1.2,
                        width_var=0.22, width_var_len=70, feather=0.45, feather_px=1.4, fibre_lo=7, tip_px=26, bead=0.75, dash_jitter=0.25, pigment=0.0,
                        density=0.14, bloom=0.0, bloom_px=3.0, bloom_s=0.25, bloom_settle=0.35, sheen=0.0, sheen_px=1.0,
                        wobble_px=0.0, wobble_hz=6.0, tip_always=False, speed_var=0.0), **p.get("ink", {})}
        s.nib = bool(s.route) and s.route.get("style") == "nib"
        if s.nib: s._nib_init()
    # ---------------- hand-inked nib route (v2): wet dark tip, drying tone shift behind it, fibre feathering, width variation
    def _nib_init(s):
        R, I, r = s.route, s.ink, s.rng; H, W = s.H, s.W
        P = s.path; seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)])
        n = int(cum[-1]) + 1; sv = np.linspace(0, cum[-1], n)
        D = np.stack([np.interp(sv, cum, P[:, 0]), np.interp(sv, cum, P[:, 1])], 1).astype(np.float32); s.Lr = float(cum[-1])
        wn = pnoise(r, 1, 4096, I["width_var_len"], 6)[0]
        wid = R["width"] * (1 + I["width_var"] * np.tanh(wn[:n])) * np.clip(0.55 + sv / 18.0, 0, 1)     # pressure: nib lands, then opens
        on = np.ones(n, bool)
        if R.get("dash"):
            a_, b_ = R["dash"]; pos = 0.0; flag = True
            while pos < n:
                L_ = (a_ if flag else b_) * (1 + I["dash_jitter"] * r.uniform(-1, 1)); i0, i1 = int(pos), int(min(n, pos + L_))
                on[i0:i1] = flag; pos += L_; flag = not flag
        pad = int(R["width"] * 3 + 12); x0, y0 = np.floor(D.min(0)).astype(int) - pad; x1, y1 = np.ceil(D.max(0)).astype(int) + pad
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1); h, w = y1 - y0, x1 - x0; ss = R["supersample"]
        A = np.zeros((h * ss, w * ss), np.uint8); S = np.full((h * ss, w * ss), -1.0, np.float32)
        for i in range(n - 1):
            if not on[i]: continue
            q0 = tuple(np.int32(np.round((D[i] - [x0, y0]) * ss * 16))); q1 = tuple(np.int32(np.round((D[i + 1] - [x0, y0]) * ss * 16)))
            th = max(1, int(round(wid[i] * ss)))
            cv2.line(A, q0, q1, 255, th, cv2.LINE_AA, shift=4); cv2.line(S, q0, q1, float(sv[i]), th + 2, cv2.LINE_8, shift=4)
        A = cv2.resize(A, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        S = S.reshape(h, ss, w, ss).max((1, 3))
        fib = 0.5 * pnoise(r, h, w, I["fibre_lo"], 0.8, ax=3.0) + 0.5 * pnoise(r, h, w, I["fibre_lo"], 0.8, ay=3.0)
        fe = np.clip(cv2.GaussianBlur(A, (0, 0), I["feather_px"]) * (0.55 + 0.6 * fib) - 0.10, 0, 1) * (1 - A)
        kf = int(I["feather_px"] * 3) * 2 + 1; Sf = cv2.dilate(S, np.ones((kf, kf), np.uint8))
        dens = np.clip(1 - I["density"] + I["density"] * pnoise(r, h, w, 5, 1.0), 0.6, 1.1)       # ink density varies with paper tooth
        ts = np.linspace(R["t0"], R["t1"], 2048); Ls = np.float32([ease(t_, R["t0"], R["t1"]) for t_ in ts]) * s.Lr
        if I["speed_var"] > 0:                                                                 # v3: hand speed varies (pauses, pushes)
            v = np.gradient(Ls); ph = r.uniform(0, 6.28, 2); u = np.linspace(0, 1, len(ts))
            v = v * np.clip(1 + I["speed_var"] * (0.65 * np.sin(2 * math.pi * 2.3 * u + ph[0]) + 0.35 * np.sin(2 * math.pi * 5.1 * u + ph[1])), 0.15, None)
            Ls = (np.cumsum(v) - v[0]); Ls = (Ls / Ls[-1] * s.Lr).astype(np.float32)
        Sb = None
        if I["bloom"] > 0:                                                                     # v3: ink bloom footprint around each dash
            kb = int(I["bloom_px"] * 2.5) * 2 + 1; Sb = cv2.dilate(S, np.ones((kb, kb), np.uint8))
            Ab = cv2.GaussianBlur(A, (0, 0), I["bloom_px"]); Ab = np.clip(Ab / (Ab.max() + 1e-6) * 1.6, 0, 1) * (1 - A)
            Ab = Ab * (0.6 + 0.5 * fib)
        core = None
        if I["sheen"] > 0:                                                                     # v3: wet-sheen highlight: thin core, offset up-left
            core = np.clip((A - 0.75) / 0.25, 0, 1); core = cv2.erode(core, np.ones((3, 3), np.uint8)) if R["width"] > 4 else core
            M_ = np.float32([[1, 0, -I["sheen_px"]], [0, 1, -I["sheen_px"]]]); core = cv2.warpAffine(core, M_, (w, h)) * A
        s.nb = dict(bb=(x0, y0, x1, y1), A=A * dens, S=S, fe=fe, Sf=Sf, D=D, wid=wid, sv=sv, ts=ts, Ls=Ls, on=on, Sb=Sb,
                    Ab=(Ab if Sb is not None else None), core=core, wph=r.uniform(0, 6.28, 2))
    def _ink_comp(s, roi, a, wet):
        I = s.ink; c = (np.float32(I["dry_color"]) * (1 - wet[..., None]) + np.float32(I["wet_color"]) * wet[..., None]) / 255.0
        k = I["pigment"]                                                                       # 0 = pure multiply (transparent ink), 1 = opaque pigment
        roi[...] = roi * (1 - a[..., None]) + (roi * c * (1 - k) + c * 255.0 * k) * a[..., None]
    def _nib_overlay(s, img, t):
        R, I, N = s.route, s.ink, s.nb; pr = s._prog(t)
        if pr <= 0: return
        L = pr * s.Lr; x0, y0, x1, y1 = N["bb"]; roi = img[y0:y1, x0:x1]
        tS = np.interp(N["S"], N["Ls"], N["ts"]); age = np.maximum(t - tS, 0); wet = np.exp(-age / I["dry_time"])
        op = I["dry_opacity"] + (I["wet_opacity"] - I["dry_opacity"]) * wet
        drawn = (N["S"] >= 0) & (N["S"] <= L)
        tSf = np.interp(N["Sf"], N["Ls"], N["ts"]); agef = np.maximum(t - tSf, 0)
        fe = N["fe"] * I["feather"] * smoothstep(0.0, I["wick_time"], agef) * ((N["Sf"] >= 0) & (N["Sf"] <= L))
        a = np.clip(N["A"] * op * drawn + fe * I["dry_opacity"], 0, 1)
        if N["Sb"] is not None:                                                                # bloom: spreads out right after deposit, then settles
            tSb = np.interp(N["Sb"], N["Ls"], N["ts"]); ab = np.maximum(t - tSb, 0) / I["bloom_s"]
            g = np.clip(ab * np.exp(1 - ab), 0, 1) * (1 - I["bloom_settle"]) + I["bloom_settle"] * np.clip(ab, 0, 1)
            a = np.maximum(a, N["Ab"] * I["bloom"] * g * ((N["Sb"] >= 0) & (N["Sb"] <= L)))
        a = np.clip(a, 0, 1) * s.k
        wetm = np.where(drawn, wet, 0.0).astype(np.float32)
        s._ink_comp(roi, a.astype(np.float32), wetm)
        if N["core"] is not None:                                                              # wet sheen: fades as the ink dries
            sh = N["core"] * wetm * I["sheen"] * s.k; roi += sh[..., None] * (np.float32([235, 205, 185]) - roi) * 0.9
        if pr < 1:                                                                             # ink bead pooling at the nib (dark, never a glow)
            i = min(int(L), len(N["D"]) - 1)
            if N["on"][i] or I["tip_always"]:
                hx, hy = N["D"][i]; rr = N["wid"][i] * I["bead"] * (1.0 if N["on"][i] else 0.7)
                if I["wobble_px"] > 0:
                    j = min(i + 3, len(N["D"]) - 1); tx, ty = N["D"][j] - N["D"][max(i - 3, 0)]; nn = math.hypot(tx, ty) + 1e-6
                    wb = I["wobble_px"] * (0.7 * math.sin(2 * math.pi * I["wobble_hz"] * t + N["wph"][0]) + 0.3 * math.sin(2 * math.pi * 2.7 * I["wobble_hz"] * t + N["wph"][1]))
                    hx, hy = hx - ty / nn * wb, hy + tx / nn * wb; rr *= 1 + 0.15 * math.sin(2 * math.pi * 1.7 * t + N["wph"][1])
                R_ = int(rr * 2 + 3)
                xa, xb, ya, yb = max(x0, int(hx) - R_), min(x1, int(hx) + R_ + 1), max(y0, int(hy) - R_), min(y1, int(hy) + R_ + 1)
                yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
                b = np.clip(rr + 0.5 - d, 0, 1) * I["wet_opacity"] * s.k
                s._ink_comp(img[ya:yb, xa:xb], b.astype(np.float32), np.ones_like(b, np.float32))
    def _ink_markers(s, img, t):
        I = s.ink; H, W = s.H, s.W
        for mk in s.markers:
            if mk["style"] != "ink" or t < mk["t_on"]: continue
            age = t - mk["t_on"]; fr = min(1.0, age / mk["draw_s"]); x, y = mk["xy"]; rr = mk["radius"]
            R_ = int(rr + mk["width"] * 2 + 4); xa, xb, ya, yb = max(0, int(x) - R_), min(W, int(x) + R_ + 1), max(0, int(y) - R_), min(H, int(y) + R_ + 1)
            ss = 4; can = np.zeros(((yb - ya) * ss, (xb - xa) * ss), np.uint8); c = (int(round((x - xa) * ss * 16)), int(round((y - ya) * ss * 16)))
            st = mk["start_deg"]; cv2.ellipse(can, c, (int(rr * ss * 16), int(rr * ss * 16)), 0, st, st + 360 * fr, 255, max(1, int(mk["width"] * ss)), cv2.LINE_AA, shift=4)
            if fr >= 1: cv2.circle(can, c, int(mk["dot"] * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
            a = cv2.resize(can, (xb - xa, yb - ya), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
            wet = math.exp(-max(age - mk["draw_s"] * 0.5, 0) / I["dry_time"])
            op = I["dry_opacity"] + (I["wet_opacity"] - I["dry_opacity"]) * wet
            if mk.get("bloom", 0) > 0:                                                          # v3 stamp: ink blooms outward on arrival, then settles
                ab = age / mk.get("bloom_s", 0.3); g = min(1.0, ab * math.exp(1 - ab)) * (1 - mk.get("bloom_settle", 0.45)) + mk.get("bloom_settle", 0.45) * min(1.0, ab)
                yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
                if "fib" not in mk: mk["fib"] = pnoise(np.random.default_rng([int(x), int(y)]), 64, 64, 6, 1.0)
                fb = cv2.resize(mk["fib"], (xb - xa, yb - ya))
                rb = rr * mk.get("bloom_r", 1.4) * min(1.0, 0.35 + 0.65 * min(1.0, ab))
                blot = np.clip((rb - d) / 2.5 + 0.35 * fb, 0, 1) * mk["bloom"] * g
                a = np.maximum(a, blot)
            s._ink_comp(img[ya:yb, xa:xb], (a * op * s.k).astype(np.float32), np.full(a.shape, wet, np.float32))
    def _prog(s, t): return ease(t, s.route["t0"], s.route["t1"])
    def shade(s, img, t):
        if s.parch:
            c = s.parch; a = math.radians(c["angle_deg"]); proj = (s.X * math.cos(a) + s.Y * math.sin(a)) / (s.W * abs(math.cos(a)) + s.H * abs(math.sin(a)))
            pos = c["x_from"] + (c["x_to"] - c["x_from"]) * (t / s.ctx["half"])
            band = np.exp(-((proj - pos) / c["width_frac"]) ** 2) * s.m * s.k * c["strength"]
            img *= 1 + band[..., None] * np.float32(c["warm"])
        if s.cloud:
            c = s.cloud; vx, vy = c["velocity"]
            F = 0.8 * scroll(s.C1, -vx * t, -vy * t) + 0.45 * scroll(s.C2, -1.35 * vx * t, -0.6 * vy * t)
            sh = smoothstep(s.c0, s.c0 + c["softness"], F) * s.m * (c["strength"] * s.k)
            img *= 1 - sh[..., None] * np.float32(c["tint"])
    def overlay(s, img, t):
        _ = s._ink_markers(img, t) if any(mk["style"] == "ink" for mk in s.markers) else None
        if not s.route: return
        if s.nib: return s._nib_overlay(img, t)
        R = s.route; pr = s._prog(t)
        if pr <= 0: return
        L = pr * s.Lr; x0, y0, x1, y1 = s.rbb; ss = R["supersample"]
        can = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        on, off = R["dash"]; period = on + off
        # walk the path, draw dash pieces up to length L
        for i in range(len(s.path) - 1):
            a0, a1 = s.cum[i], s.cum[i + 1]
            if a0 >= L: break
            p0, p1 = s.path[i], s.path[i + 1]
            e = min(a1, L); seglen = a1 - a0
            # split into dash on-pieces
            d = a0
            while d < e:
                ph = d % period; nd = min(e, d + (on - ph) if ph < on else d + (period - ph))
                if ph < on:
                    q0 = p0 + (p1 - p0) * ((d - a0) / seglen); q1 = p0 + (p1 - p0) * ((nd - a0) / seglen)
                    cv2.line(can, tuple(np.int32(np.round((q0 - [x0, y0]) * ss * 16))), tuple(np.int32(np.round((q1 - [x0, y0]) * ss * 16))),
                             255, int(round(R["width"] * ss)), cv2.LINE_AA, shift=4)
                d = nd + 1e-4
        al = cv2.resize(can, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        al *= R["opacity"] * s.k * s.paper[y0:y1, x0:x1]
        roi = img[y0:y1, x0:x1]
        if R["halo"] > 0:   # faint warm light under the ink so the line reads on a phone
            hal = cv2.GaussianBlur(al, (0, 0), R["halo_sigma"]) * R["halo"]; roi += hal[..., None] * np.float32(R["halo_color"]) * 0.6
        roi[...] = roi * (1 - al[..., None]) + np.float32(R["color"]) * al[..., None]
    def emit(s, img, t):
        if s.route and not s.nib:
            R = s.route; pr = s._prog(t)
            if 0 < pr < 1 or (pr >= 1 and t < R["t1"] + 0.4):
                i = int(np.searchsorted(s.cum, pr * s.Lr)); i = min(max(i, 1), len(s.path) - 1)
                hx, hy = s.path[i]; fade = 1.0 if pr < 1 else 1 - (t - R["t1"]) / 0.4
                fl = 0.85 + 0.15 * math.sin(t * 2 * math.pi * 3.1)
                gauss_dot(img, hx, hy, R["head_sigma"], R["head_color"], R["head_glow"] * fade * fl * s.k * 0.9)
                gauss_dot(img, hx, hy, R["head_sigma"] * 0.35, [255, 245, 220], R["head_glow"] * fade * s.k * 0.9)
        for mk in s.markers:
            if t < mk["t_on"] or mk["style"] != "glow": continue
            age = t - mk["t_on"]; on = smoothstep(0, 0.35, np.float32(age))
            pulse = 0.75 + 0.25 * math.sin(2 * math.pi * mk["pulse_hz"] * age)
            flash = 1.0 + 1.2 * math.exp(-age / 0.25) * (mk["t_on"] > 0)
            x, y = mk["xy"]; g = mk["gain"] * s.k * float(on) * pulse * flash
            gauss_dot(img, x, y, mk["radius"], mk["color"], 0.55 * g)
            gauss_dot(img, x, y, mk["radius"] * 0.3, [255, 240, 205], 0.9 * g)
            if mk["ring"]:
                ph = (age * 0.6) % 1.0; rr = mk["radius"] * (0.8 + 2.6 * ph); H, W = s.H, s.W
                R_ = int(rr + 4); x0, x1, y0, y1 = max(0, int(x) - R_), min(W, int(x) + R_ + 1), max(0, int(y) - R_), min(H, int(y) + R_ + 1)
                yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
                ring = np.exp(-((d - rr) / 1.3) ** 2) * (1 - ph) ** 1.5 * g * 0.5
                img[y0:y1, x0:x1] += ring[..., None] * np.float32(mk["color"])
    def allow(s):
        a = s.m > 1e-4
        if s.route:
            sw = np.zeros((s.H, s.W), np.uint8)
            cv2.polylines(sw, [np.int32(np.round(s.path))], False, 1, int(s.route["width"] * 2 + s.route["head_sigma"] * 8 + 4))
            a = a | (sw > 0)
        for mk in s.markers:
            d = np.zeros((s.H, s.W), np.uint8); cv2.circle(d, tuple(int(v) for v in mk["xy"]), int(mk["radius"] * 4.5 + 6), 1, -1); a = a | (d > 0)
        return a

class Sky(Preset):
    """Cloud drift: the painted sky slides (parallax by height, faster near the top) with a slow billow; tapered to 0 at the skyline."""
    D = dict(velocity=[7.0, 0.0], parallax=0.8, billow_px=0.8, billow_lo=120, edge_erode_px=2, edge_blur_px=10)
    def __init__(s, *a):
        super().__init__(*a); p = {**s.D, **s.p}; s.p = p
        s.dm = taper(s.m, p["edge_erode_px"], p["edge_blur_px"])
        ys = np.nonzero((s.m > 0.5).any(1))[0]; s.ymax = float(ys.max()) if len(ys) else s.H
        s.par = (1 + p["parallax"] * (1 - np.clip(s.Y / max(s.ymax, 1), 0, 1))) / (1 + p["parallax"] * 0.5)
        s.N1 = pnoise(s.rng, s.H, s.W, p["billow_lo"], 8); s.N2 = pnoise(s.rng, s.H, s.W, p["billow_lo"], 8)
    def disp(s, t):
        p = s.p; vx, vy = p["velocity"]; w = s.dm * s.k
        bx = p["billow_px"] * scroll(s.N1, -vx * t * 0.5, 0); by = p["billow_px"] * scroll(s.N2, -vx * t * 0.5, 0)
        return (-vx * t * s.par + bx) * w, (-vy * t * s.par + by) * w
    def allow(s): return s.m > 1e-4

class Atmos(Preset):
    """Haze / mist sheets drifting through a height band + optional crepuscular light rays from a source point."""
    def __init__(s, *a):
        super().__init__(*a); p = s.p; r = s.rng; H, W = s.H, s.W
        s.haze = {**dict(color=[205, 196, 190], opacity=0.22, lo=260, hi=30, velocity=[12.0, -1.0], band=None, band_soft=120, contrast=1.3), **p["haze"]} if "haze" in p else None
        if s.haze:
            h = s.haze; s.H1 = pnoise(r, H, W, h["lo"], h["hi"], ax=2.5); s.H2 = pnoise(r, H, W, h["lo"] * 0.5, h["hi"], ax=2.5)
            s.band = np.ones((H, W), np.float32) if not h["band"] else smoothstep(h["band"][0] - h["band_soft"], h["band"][0], s.Y) * (1 - smoothstep(h["band"][1], h["band"][1] + h["band_soft"], s.Y))
        s.rays = {**dict(origin=[700, 200], strength=0.16, color=[255, 214, 170], n_scale=40, speed=0.002, falloff=900, luma_gate=0.35, near_fade=[40, 260]), **p["rays"]} if "rays" in p else None
        if s.rays:
            R = s.rays; ox, oy = R["origin"]; s.th = np.arctan2(s.Y - oy, s.X - ox); s.dist = np.sqrt((s.X - ox) ** 2 + (s.Y - oy) ** 2)
            n = 4096; spec = (r.standard_normal(n // 2 + 1) + 1j * r.standard_normal(n // 2 + 1)) * np.exp(-(np.fft.rfftfreq(n) * R["n_scale"]) ** 2)
            s.ang1 = np.fft.irfft(spec, n); s.ang1 = (s.ang1 - s.ang1.mean()) / s.ang1.std()
            spec2 = (r.standard_normal(n // 2 + 1) + 1j * r.standard_normal(n // 2 + 1)) * np.exp(-(np.fft.rfftfreq(n) * R["n_scale"] * 0.6) ** 2)
            s.ang2 = np.fft.irfft(spec2, n); s.ang2 = (s.ang2 - s.ang2.mean()) / s.ang2.std(); s.na = n
            s.fall = (1.0 / (1 + (s.dist / R["falloff"]) ** 2) * smoothstep(R["near_fade"][0], R["near_fade"][1], s.dist)).astype(np.float32)
            Lp = lum(s.ctx["plate"]); s.gate = (R["luma_gate"] + (1 - R["luma_gate"]) * Lp).astype(np.float32)
    def overlay(s, img, t):
        if s.haze:
            h = s.haze; vx, vy = h["velocity"]
            N = 0.7 * scroll(s.H1, -vx * t, -vy * t) + 0.5 * scroll(s.H2, -1.6 * vx * t, 0.5 * vy * t)
            a = np.clip(0.5 + 0.5 * h["contrast"] * np.tanh(N * 0.8), 0, 1) * h["opacity"] * s.k * s.m * s.band
            img[...] = img * (1 - a[..., None]) + np.float32(h["color"]) * a[..., None]
    def emit(s, img, t):
        if s.rays:
            R = s.rays; n = s.na
            i1 = ((s.th / (2 * math.pi)) * n + R["speed"] * n * t) % n; i2 = ((s.th / (2 * math.pi)) * n - 0.6 * R["speed"] * n * t) % n
            A = np.interp(i1.ravel(), np.arange(n), s.ang1).reshape(s.H, s.W); B = np.interp(i2.ravel(), np.arange(n), s.ang2).reshape(s.H, s.W)
            I = np.clip(0.55 * A + 0.45 * B, 0, None) ** 1.6 * s.fall * s.gate * s.m * R["strength"] * s.k
            I *= 0.85 + 0.15 * math.sin(2 * math.pi * t / 3.7)
            col = np.float32(R["color"]) / 255.0
            img[...] = 255 - (255 - img) * (1 - np.clip(I, 0, 1)[..., None] * col)

class Smoke(Preset):
    """Volumetric-looking smoke plumes: widening advected noise columns with travelling meander, clipped by the mask;
    optional falling ash particles (ash_mask, may sit in front of everything)."""
    PD = dict(w0=10.0, w1=90.0, opacity=0.55, rise=22.0, color_dark=[58, 52, 54], color_light=[150, 140, 140], meander=0.18, meander_len=180, lo=60, hi=4)
    def __init__(s, *a):
        super().__init__(*a); p = s.p; r = s.rng; H, W = s.H, s.W; s.plumes = []
        for q in p.get("plumes", []):
            q = {**s.PD, **q}; src, top = np.float32(q["src"]), np.float32(q["top"]); ax = top - src; L = float(np.linalg.norm(ax)); u = ax / L; nrm = np.float32([-u[1], u[0]])
            pad = q["w1"] * 1.6; pts = np.float32([src + nrm * q["w0"] * 2, src - nrm * q["w0"] * 2, top + nrm * pad + u * pad * 0.6, top - nrm * pad + u * pad * 0.6])
            x0, y0 = np.floor(pts.min(0)).astype(int); x1, y1 = np.ceil(pts.max(0)).astype(int)
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); along = (xx - src[0]) * u[0] + (yy - src[1]) * u[1]; across = (xx - src[0]) * nrm[0] + (yy - src[1]) * nrm[1]
            tex1 = pnoise(r, 1024, 512, q["lo"], q["hi"] * 2, ay=1.6); tex2 = pnoise(r, 1024, 512, q["lo"] * 0.45, q["hi"], ay=1.4)
            s.plumes.append(dict(q=q, bb=(x0, y0, x1, y1), along=along, across=across, L=L, t1=tex1, t2=tex2, ph=float(r.uniform(0, 6.28)), mclip=s.m[y0:y1, x0:x1]))
        s.ash = {**dict(count=0, size=[0.6, 1.8], big_frac=0.08, big_size=[2.5, 4.5], fall=[8, 26], wind=[10, 2], sway=6, color=[200, 194, 188], opacity=0.55, mask=None), **p["ash"]} if "ash" in p else None
        if s.ash and s.ash["count"]:
            A = s.ash; n = A["count"]; s.am = load_mask(A["mask"], (H, W)) if A["mask"] else np.ones((H, W), np.float32)
            big = r.random(n) < A["big_frac"]
            s.ap = dict(x=r.uniform(0, W, n), y=r.uniform(0, H, n), vy=r.uniform(*A["fall"], n), vx=A["wind"][0] * r.uniform(0.6, 1.4, n),
                        sz=np.where(big, r.uniform(*A["big_size"], n), r.uniform(*A["size"], n)), ph=r.uniform(0, 6.28, n), f=r.uniform(0.3, 1.2, n),
                        br=r.uniform(0.5, 1.0, n) * np.where(big, 0.6, 1.0))
    def overlay(s, img, t):
        for P in s.plumes:
            q = P["q"]; x0, y0, x1, y1 = P["bb"]; L = P["L"]; al, ac = P["along"], P["across"]
            sn = al / L; w = q["w0"] + (q["w1"] - q["w0"]) * np.clip(sn, 0, 1.3) ** 0.8
            mea = q["meander"] * q["w1"] * np.clip(sn, 0, None) * np.sin(2 * math.pi * al / q["meander_len"] - 1.6 * t + P["ph"])
            ac2 = ac - mea
            env = np.exp(-1.15 * (ac2 / w) ** 2) * smoothstep(-0.04, 0.10, sn) * (1 - smoothstep(0.75, 1.25, sn))
            u = (ac2 * (q["w1"] * 0.6 / w) + 256).astype(np.float32)
            v1 = (al - q["rise"] * t) * 0.9; v2 = (al * 1.1 - q["rise"] * 1.7 * t)
            T1 = cv2.remap(P["t1"], u, (-v1 % 1024).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            T2 = cv2.remap(P["t2"], u, (-v2 % 1024).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            D = np.clip(0.42 + 0.5 * (0.65 * T1 + 0.45 * T2), 0, 1) ** 1.5 * env
            a = np.clip(D * q["opacity"] * s.k, 0, 0.95) * P["mclip"]
            mix = np.clip(sn, 0, 1)[..., None]; col = np.float32(q["color_dark"]) * (1 - mix) + np.float32(q["color_light"]) * mix
            roi = img[y0:y1, x0:x1]; roi[...] = roi * (1 - a[..., None]) + col * a[..., None]
        if s.ash and s.ash["count"]:
            A, ap = s.ash, s.ap; H, W = s.H, s.W
            x = (ap["x"] + ap["vx"] * t + A["sway"] * np.sin(ap["ph"] + t * ap["f"] * 2 * math.pi)) % W
            y = (ap["y"] + ap["vy"] * t) % H
            br = ap["br"] * (0.6 + 0.4 * np.sin(ap["ph"] * 3 + t * ap["f"] * 9)) * A["opacity"] * s.k
            col = np.float32(A["color"])
            for xi, yi, sz, b in zip(x, y, ap["sz"], br):
                R = int(sz * 3) + 1; xa, xb, ya, yb = max(0, int(xi) - R), min(W, int(xi) + R + 1), max(0, int(yi) - R), min(H, int(yi) + R + 1)
                if xa >= xb or ya >= yb: continue
                yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
                d = np.exp(-((xx - xi) ** 2 + (yy - yi) ** 2) / (2 * (sz * 0.6) ** 2)) * b * s.am[ya:yb, xa:xb]
                roi = img[ya:yb, xa:xb]; roi[...] = roi * (1 - d[..., None]) + col * d[..., None]
    def allow(s):
        a = np.zeros((s.H, s.W), bool)
        for P in s.plumes:
            x0, y0, x1, y1 = P["bb"]; a[y0:y1, x0:x1] |= P["mclip"] > 1e-4
        if s.ash and s.ash["count"]: a |= s.am > 1e-4
        return a

class FireTorch(Preset):
    """Fire / torchlight: per-source flicker (deterministic multi-band), small procedural flames, light thrown onto
    surfaces (multiplies surface albedo, limited to the layer mask), smoulder hotspots on a char mask, rising embers."""
    SD = dict(flame=[6, 16], light_radius=120, intensity=0.5, color=[255, 150, 70], flame_gain=1.0, cast_light=True, halo=None,
              flicker=dict(amps=[0.30, 0.20, 0.12, 0.07], freqs=[1.7, 3.9, 7.3, 12.1], noise=0.12, noise_hz=24.0, floor=0.15, smooth=False))
    def __init__(s, *a):
        super().__init__(*a); p = s.p; r = s.rng; H, W = s.H, s.W
        s.src = []
        for q in p.get("sources", []):
            q = {**s.SD, **q}; q["flicker"] = {**s.SD["flicker"], **q["flicker"]}; x, y = q["xy"]; d = np.sqrt((s.X - x) ** 2 + (s.Y - y) ** 2)
            fall = 1.0 / (1 + (d / q["light_radius"]) ** 2) * np.exp(-d / (q["light_radius"] * 3))
            fr = r.uniform(0, 6.28, 4); fq = np.float32(q["flicker"]["freqs"]) * r.uniform(0.85, 1.15, 4)
            fw, fh = q["flame"]; ftex = pnoise(r, 256, 64, 18, 2, ay=1.8)
            s.src.append(dict(q=q, fall=fall.astype(np.float32), fr=fr, fq=fq, ftex=ftex, noise=r.standard_normal(4096)))
        s.hot = {**dict(mask=None, coverage=0.18, lo=70, hi=6, gain=0.9, color=[255, 96, 28], breathe=0.35, bloom=6, light=0.25, light_radius=40), **p["hotspots"]} if "hotspots" in p else None
        if s.hot:
            h = s.hot; cm = load_mask(h["mask"], (H, W)); N = pnoise(r, H, W, h["lo"], h["hi"]); thr = np.quantile(N[cm > 0.5], 1 - h["coverage"]) if (cm > 0.5).any() else 9
            s.hm = (smoothstep(thr, thr + 0.8, N) * cm).astype(np.float32); s.hm = cv2.GaussianBlur(s.hm, (0, 0), 1.0)
            s.hb1 = pnoise(r, H, W, 90, 10); s.hb2 = pnoise(r, H, W, 50, 8)
            s.hlight = cv2.GaussianBlur(s.hm, (0, 0), h["light_radius"]); s.hlight /= max(s.hlight.max(), 1e-6)
        s.emb = {**dict(count=0, spawn=[], rise=[25, 70], life=[1.2, 2.6], drift=[6, 0], sway=8, size=[0.6, 1.4], color=[255, 170, 80], gain=1.0, mask=None), **p["embers"]} if "embers" in p else None
        if s.emb and s.emb["count"]:
            e = s.emb; n = e["count"]; sp = np.float32(e["spawn"])                 # list of [x, y, rx, ry] spawn ellipses
            k = r.integers(0, len(sp), n); ang = r.uniform(0, 6.28, n); rad = np.sqrt(r.uniform(0, 1, n))
            s.ep = dict(x=sp[k, 0] + np.cos(ang) * rad * sp[k, 2], y=sp[k, 1] + np.sin(ang) * rad * sp[k, 3], v=r.uniform(*e["rise"], n), life=r.uniform(*e["life"], n),
                        sw=r.uniform(0.3, 1.0, n) * e["sway"], sf=r.uniform(0.4, 1.4, n), ph=r.uniform(0, 6.28, n), sz=r.uniform(*e["size"], n), br=r.uniform(0.5, 1, n), fl=r.uniform(5, 13, n))
            s.ep["t0"] = r.uniform(0, 1, n) * s.ep["life"]
            s.em = load_mask(e["mask"], (H, W)) if e["mask"] else np.ones((H, W), np.float32)
        # ---- light-spill (v2): relight surfaces around a source, driven by THAT source's flicker curve (flame and spill in sync)
        s.spill = []
        for sp_ in p.get("light_spill", []):
            q = {**dict(source=0, mask=None, radius=300.0, power=2.0, amp=0.5, tint=[1.0, 0.85, 0.6], facing_floor=0.25, warm_weight=0.6,
                        grad_weight=0.4, grad_sigma=6.0, lum_lo=0.02, lum_hi=0.35, offset=[0, 0]), **sp_}
            S0 = s.src[q["source"]]; lx, ly = np.float32(S0["q"]["xy"]) + np.float32(q["offset"])
            d = np.sqrt((s.X - lx) ** 2 + (s.Y - ly) ** 2)
            fall = 1.0 / (1 + (d / q["radius"]) ** q["power"])                       # inverse-square-ish with a soft core
            P = s.ctx["plate"]; Lp = lum(P); warm = np.clip((P[..., 0] - P[..., 2]) / 255.0 * 2, 0, 1)
            lit = smoothstep(q["lum_lo"], q["lum_hi"], Lp) * (0.5 + 0.5 * warm)      # surfaces the painted candle already lights
            Lb = cv2.GaussianBlur(Lp, (0, 0), q["grad_sigma"]); gx = cv2.Sobel(Lb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Lb, cv2.CV_32F, 0, 1, ksize=3)
            ux, uy = (lx - s.X) / (d + 1e-3), (ly - s.Y) / (d + 1e-3); gm = np.sqrt(gx * gx + gy * gy)
            gd = (gx * ux + gy * uy) / (gm + 1e-4); gw = np.clip(gm / (np.percentile(gm, 95) + 1e-6), 0, 1)
            gterm = 0.5 + 0.5 * gd * gw                                            # brightness rising toward the flame -> faces it
            facing = q["facing_floor"] + (1 - q["facing_floor"]) * np.clip(q["warm_weight"] * lit + q["grad_weight"] * gterm, 0, 1)
            mk = load_mask(q["mask"], (H, W)) if q["mask"] else np.ones((H, W), np.float32)
            s.spill.append(dict(q=q, src=S0, map=(q["amp"] * fall * facing * mk).astype(np.float32), facing=facing.astype(np.float32), mask=mk))
        # ---- plate flame flicker (v2): the painted flame's own pixels breathe with the source curve + rising tongue texture
        s.pflame = None
        if "plate_flame" in p:
            q = {**dict(source=0, mask=None, gain=0.35, tongue=0.18, rise=60.0, hot=[255, 238, 190]), **p["plate_flame"]}
            fm = load_mask(q["mask"], (H, W)); ys, xs = np.nonzero(fm > 1e-3)
            bb = (max(0, xs.min() - 2), max(0, ys.min() - 2), min(W, xs.max() + 3), min(H, ys.max() + 3))
            s.pflame = dict(q=q, src=s.src[q["source"]], fm=fm, bb=bb)
        # ---- flame_warp (batch 3): the painted flame itself sways at the tip and stretches with the flicker curve.
        #      Displacement exists ONLY inside a small zone around the flame mask (protect everything else).
        s.fwarp = None
        if "flame_warp" in p:
            q = {**dict(source=0, mask=None, base=[0, 0], height=40.0, sway_px=3.0, sway_hz=[0.9, 2.3], stretch=0.35, zone_px=5, lean_px=0.0), **p["flame_warp"]}
            fm = load_mask(q["mask"], (H, W)); zone = cv2.dilate((fm > 1e-3).astype(np.uint8), np.ones((2 * q["zone_px"] + 1,) * 2, np.uint8)).astype(np.float32)
            zone = cv2.GaussianBlur(zone, (0, 0), max(q["zone_px"] / 3, 0.8)) * zone
            bx, by = q["base"]; hgt = np.clip((by - s.Y) / q["height"], 0, 1.3)
            s.fwarp = dict(q=q, src=s.src[q["source"]], zone=zone.astype(np.float32), h=(hgt * zone).astype(np.float32), fr=r.uniform(0, 6.28, 2), nz=r.standard_normal(4096))
        # ---- light pool (batch 3): soft darkening toward the room edges whose radius breathes with the flicker curve
        s.pool = None
        if "light_pool" in p:
            q = {**dict(source=0, mask=None, center=None, r0=500.0, power=2.0, dark=0.35, breathe=0.6, tint=[1.0, 0.93, 0.85]), **p["light_pool"]}
            S0 = s.src[q["source"]]; cx, cy = q["center"] or S0["q"]["xy"]
            s.pool = dict(q=q, src=S0, d=np.sqrt((s.X - cx) ** 2 + (s.Y - cy) ** 2).astype(np.float32),
                          mask=load_mask(q["mask"], (H, W)) if q["mask"] else np.ones((H, W), np.float32))
        # ---- flame_tongues (v2): procedural licking flames rising from hand-placed fire beds (base polylines).
        #      Pure emissive overlay: the flame FIELD is noise-displaced, plate pixels never are.
        s.beds = []; ft = p.get("flame_tongues")
        if ft:
            ft = {**dict(rise=95.0, sway_px=5.0, tongue_lo=20, tongue_hi=6, tongue_sharp=1.5, body=0.8, clump_gain=0.8, cover=0.55, bloom_sigma=7.0, bloom=0.45, light_radius=120.0, light=0.55,
                         light_color=[255, 140, 60], lut=[[0.0, [40, 5, 0]], [0.2, [140, 30, 5]], [0.4, [220, 75, 10]], [0.6, [255, 130, 30]],
                                                           [0.8, [255, 190, 80]], [1.0, [255, 232, 165]]],
                         flicker=dict(amps=[0.16, 0.10, 0.06, 0.03], freqs=[1.3, 2.9, 5.3, 9.7], noise=0.1, noise_hz=10.0, floor=0.45, smooth=True),
                         body_mix=0.0, body_scale=0.35, despeckle=0.0, pad_mult=2.6, soot=None, clip_to_mask=False), **ft}
            s.ft = ft; xs_ = np.float32([c[0] for c in ft["lut"]]); cs_ = np.float32([c[1] for c in ft["lut"]])
            s.lut = np.stack([np.interp(np.linspace(0, 1, 256), xs_, cs_[:, k]) for k in range(3)], 1).astype(np.float32)
            s.ftex1 = pnoise(r, 512, 512, ft["tongue_lo"], ft["tongue_hi"], ay=4.0); s.ftex2 = pnoise(r, 512, 512, ft["tongue_lo"] * 0.6, 4, ay=2.0)
            s.wtex = pnoise(r, 512, 512, 40, 6); s.bed_light = np.zeros((H, W), np.float32)
            P0 = s.ctx["plate"]; Lp = lum(P0)
            for b in ft["beds"]:
                b = {**dict(thickness=6, height=50, intensity=1.0, clump=0.55, light_scale=1.0), **b}
                pts = np.float32(b["points"]); Hh = b["height"]; pad = int(Hh * ft["pad_mult"]) + 8
                x0, x1 = int(max(0, pts[:, 0].min() - Hh * 0.6 - 8)), int(min(W, pts[:, 0].max() + Hh * 0.6 + 8))
                y0, y1 = int(max(0, pts[:, 1].min() - pad)), int(min(H, pts[:, 1].max() + b["thickness"] + 4))
                bm = np.zeros((y1 - y0, x1 - x0), np.uint8)
                cv2.polylines(bm, [np.int32(np.round(pts - [x0, y0]))], False, 1, int(b["thickness"]), cv2.LINE_8)
                D = np.full(bm.shape, 1e4, np.float32); run = np.full(bm.shape[1], 1e4, np.float32)
                for yy in range(bm.shape[0] - 1, -1, -1):                     # vertical distance above the nearest base pixel below
                    run = np.where(bm[yy] > 0, 0.0, run + 1.0); D[yy] = run
                cx = rng_cl = pnoise(r, 1, 1024, 60, 8)[0]                     # 1-D clump noise along x
                bfl = {**ft["flicker"], **b["flicker"]} if b.get("flicker") else ft["flicker"]          # b4: per-clump flicker curve
                fq = np.float32(bfl["freqs"]) * r.uniform(0.85, 1.15, 4); fr = r.uniform(0, 6.28, 4)
                if b.get("rate", 1.0) != 1.0: fq = fq * b["rate"]                                     # b4: per-clump flicker rate
                fs = dict(q=dict(flicker=bfl), fq=fq, fr=fr, noise=r.standard_normal(4096))
                # firelight thrown on nearby surfaces (light-spill reuse: distance falloff x painted-lit 'facing' heuristic)
                lm = np.zeros((H, W), np.uint8); cv2.polylines(lm, [np.int32(np.round(pts))], False, 1, int(b["thickness"]) + 2)
                dist = cv2.distanceTransform((1 - lm).astype(np.uint8), cv2.DIST_L2, 5)
                fall = 1.0 / (1 + (dist / (ft["light_radius"] * b["light_scale"])) ** 2)
                facing = 0.35 + 0.65 * smoothstep(0.04, 0.45, Lp)
                s.beds.append(dict(b=b, bb=(x0, y0, x1, y1), D=D, has=(D < 1e3), cl=cx, fs=fs, ph=float(r.uniform(0, 512)), xr=(float(pts[:, 0].min()), float(pts[:, 0].max())),
                                   light=(fall * facing * b["intensity"] * b["light_scale"]).astype(np.float32)))
        # ---- bed_spill (batch 4): the candle light-spill model per fire clump.  Light-only relight of walls/ground near each clump:
        #      distance falloff from the clump's flame body x 'facing' heuristic (painted-lit + gradient toward the fire),
        #      driven by THAT clump's flicker curve (steady warm base + flicker swing); optional dark falloff away from all fires.
        s.bspill = None
        if ft and ft.get("bed_spill"):
            q = {**dict(radius_mult=1.6, radius_add=40.0, power=2.0, base=0.3, amp=0.9, tint=[1.0, 0.62, 0.32], lift=0.4, facing_floor=0.35,
                        warm_weight=0.6, grad_weight=0.4, grad_sigma=6.0, lum_lo=0.04, lum_hi=0.45, exclude=[], dark=0.0, dark_tint=[1.0, 0.95, 0.9],
                        dark_radius_mult=1.0, cut=0.03), **ft["bed_spill"]}
            P0 = s.ctx["plate"]; Lp = lum(P0); warm = np.clip((P0[..., 0] - P0[..., 2]) / 255.0 * 2, 0, 1)
            lit = smoothstep(q["lum_lo"], q["lum_hi"], Lp) * (0.5 + 0.5 * warm)
            Lb = cv2.GaussianBlur(Lp, (0, 0), q["grad_sigma"]); gx = cv2.Sobel(Lb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(Lb, cv2.CV_32F, 0, 1, ksize=3)
            gm = np.sqrt(gx * gx + gy * gy); gw = np.clip(gm / (np.percentile(gm, 95) + 1e-6), 0, 1)
            M = s.m.copy()
            for e in q["exclude"]: M *= 1 - load_mask(e, (H, W))
            tot = np.zeros((H, W), np.float32); L_ = []
            for B in s.beds:
                b = B["b"]
                if b.get("spill_gain", 1.0) <= 0: continue
                pts = np.float32(b["points"]) - [0, q["lift"] * b["height"]]
                R = b.get("spill_radius", q["radius_mult"] * b["height"] + q["radius_add"])
                ext = R * ((1.0 / q["cut"]) - 1) ** (1.0 / q["power"])
                xa, xb = int(max(0, pts[:, 0].min() - ext)), int(min(W, pts[:, 0].max() + ext + 1)); ya, yb = int(max(0, pts[:, 1].min() - ext)), int(min(H, pts[:, 1].max() + ext + 1))
                lm = np.zeros((yb - ya, xb - xa), np.uint8); cv2.polylines(lm, [np.int32(np.round(pts - [xa, ya]))], False, 1, max(int(b["thickness"]), 3))
                d = cv2.distanceTransform((1 - lm).astype(np.uint8), cv2.DIST_L2, 5)
                fall = 1.0 / (1 + (d / R) ** q["power"])
                X_, Y_ = s.X[ya:yb, xa:xb], s.Y[ya:yb, xa:xb]; cxp, cyp = float(pts[:, 0].mean()), float(pts[:, 1].mean())
                dd = np.sqrt((X_ - cxp) ** 2 + (Y_ - cyp) ** 2) + 1e-3; ux, uy = (cxp - X_) / dd, (cyp - Y_) / dd
                gd = (gx[ya:yb, xa:xb] * ux + gy[ya:yb, xa:xb] * uy) / (gm[ya:yb, xa:xb] + 1e-4); gterm = 0.5 + 0.5 * gd * gw[ya:yb, xa:xb]
                facing = q["facing_floor"] + (1 - q["facing_floor"]) * np.clip(q["warm_weight"] * lit[ya:yb, xa:xb] + q["grad_weight"] * gterm, 0, 1)
                L_.append(dict(B=B, bb=(xa, ya, xb, yb), map=(fall * facing * M[ya:yb, xa:xb] * b.get("spill_gain", 1.0) * b["intensity"]).astype(np.float32)))
                Rd = R * q["dark_radius_mult"]; tot[ya:yb, xa:xb] = np.maximum(tot[ya:yb, xa:xb], 1.0 / (1 + (d / Rd) ** q["power"]))
            s.bspill = dict(q=q, L=L_, dark=(q["dark"] * (1 - np.clip(tot, 0, 1)) * M).astype(np.float32) if q["dark"] > 0 else None)
        s.shim = None
        if ft and "shimmer" in p:
            q = {**dict(amp_px=1.2, lo=10, rise=70.0, band=[0.45, 2.4], sky_mask=None, sky_erode_px=3), **p["shimmer"]}
            A = np.zeros((H, W), np.float32)
            for B in s.beds:
                x0, y0, x1, y1 = B["bb"]; Hh = B["b"]["height"]; D = B["D"]; lo_, hi_ = q["band"]
                a = smoothstep(lo_ * Hh * 0.6, lo_ * Hh, D) * (1 - smoothstep(hi_ * Hh * 0.7, hi_ * Hh, D)) * B["has"]
                A[y0:y1, x0:x1] = np.maximum(A[y0:y1, x0:x1], a)
            if q.get("spread_px", 0) > 0:                                                      # v3: wider shimmer column (still sky-only via plateA)
                sp = int(q["spread_px"]); A = cv2.GaussianBlur(cv2.dilate(A, np.ones((1, 2 * sp + 1), np.uint8)), (0, 0), sp / 3.0)
            sky = load_mask(q["sky_mask"], (H, W)) if q["sky_mask"] else np.zeros((H, W), np.float32)
            safe = taper(sky, int(q["sky_erode_px"] + math.ceil(q["amp_px"])), 2.0)    # never samples stone: eroded sky only
            s.shim = dict(q=q, A=A, plateA=(A * safe).astype(np.float32), N1=pnoise(r, H, W, q["lo"], 2, ay=0.6), N2=pnoise(r, H, W, q["lo"], 2, ay=0.6))
        s.sparks = None
        if ft and p.get("sparks", {}).get("count"):
            q = {**dict(count=200, rise=[90, 230], life=[0.35, 1.0], spread=35, gravity=60.0, turb=25.0, size=[0.5, 1.0], gain=1.2,
                        hot=[255, 225, 150], cool=[255, 110, 30], streak=0.8, mask=None), **p["sparks"]}
            n = q["count"]; w = np.float32([B["b"]["height"] * len(B["b"]["points"]) for B in s.beds]); w /= w.sum()
            k = r.choice(len(s.beds), n, p=w); sx = np.zeros(n, np.float32); sy = np.zeros(n, np.float32); sc = np.zeros(n, np.float32)
            for i in range(n):
                pts = np.float32(s.beds[k[i]]["b"]["points"]); j = r.integers(0, len(pts) - 1) if len(pts) > 1 else 0; u = r.uniform()
                a_ = pts[j]; b_ = pts[min(j + 1, len(pts) - 1)]; sx[i], sy[i] = a_ + (b_ - a_) * u; sc[i] = s.beds[k[i]]["b"]["height"] / 60.0
            s.sparks = dict(q=q, x=sx, y=sy - 3, sc=sc, v=r.uniform(*q["rise"], n), vx=r.uniform(-1, 1, n) * q["spread"], life=r.uniform(*q["life"], n),
                            t0=r.uniform(0, 1, n), ph=r.uniform(0, 6.28, n), sz=r.uniform(*q["size"], n), fl=r.uniform(8, 20, n),
                            m=load_mask(q["mask"], (H, W)) if q["mask"] else np.ones((H, W), np.float32))
            s.sparks["t0"] *= s.sparks["life"]
    def disp(s, t):
        fw = s._fwarp(t) if s.fwarp else None
        if not s.shim or not s.shim["plateA"].any(): return fw
        q = s.shim["q"]; A = s.shim["plateA"] * s.k
        dx = q["amp_px"] * A * np.tanh(scroll(s.shim["N1"], 0, q["rise"] * t)); dy = 0.6 * q["amp_px"] * A * np.tanh(scroll(s.shim["N2"], 0, q["rise"] * 1.3 * t))
        if fw is not None: dx = dx + fw[0]; dy = dy + fw[1]
        return dx, dy
    def _fwarp(s, t):
        F = s.fwarp; q = F["q"]; f = s._flick(F["src"], t); h = F["h"]
        i = t * 3.0; j = int(i) % 4095; fr = i - int(i); fr = fr * fr * (3 - 2 * fr); nz = F["nz"][j] * (1 - fr) + F["nz"][j + 1] * fr
        sw = 0.6 * math.sin(2 * math.pi * q["sway_hz"][0] * t + F["fr"][0]) + 0.3 * math.sin(2 * math.pi * q["sway_hz"][1] * t + F["fr"][1]) + 0.25 * nz
        dx = -(q["sway_px"] * sw + q["lean_px"]) * h ** 1.6 * s.k            # tip moves most, base anchored
        dy = q["stretch"] * (f - 1.0) * q["height"] * h * (1.3 - h) * F["zone"] * s.k   # brighter -> taller (samples from below)
        return dx.astype(np.float32), dy.astype(np.float32)
    def _flick(s, S, t):
        """THE flicker curve of a source (deterministic).  Flame, halo, plate-flame and light-spill all read this one value."""
        F = S["q"]["flicker"]; a = 0.0
        for amp, f, ph in zip(F["amps"], S["fq"], S["fr"]): a += amp * math.sin(2 * math.pi * f * t + ph)
        i = t * F["noise_hz"]; j = int(i) % 4095; fr = i - int(i)
        if F["smooth"]: fr = fr * fr * (3 - 2 * fr)            # smoothstep interpolation (no kinks -> no flash pulsing)
        nz = S["noise"][j] * (1 - fr) + S["noise"][j + 1] * fr
        return max(F["floor"], 1 + a + F["noise"] * nz)
    def emit(s, img, t):
        H, W = s.H, s.W; ramp = 1.0
        light = np.zeros((H, W, 3), np.float32)
        if s.pool:
            P = s.pool; q = P["q"]; f = s._flick(P["src"], t); R = q["r0"] * (1 + q["breathe"] * (f - 1))
            lit = 1.0 / (1 + (P["d"] / R) ** q["power"]); dk = q["dark"] * (1 - lit) * P["mask"] * s.k
            img *= (1 - dk[..., None] * np.float32(q["tint"]))
        for sp_ in s.spill:                                    # relight: zero-mean breathing around the painted lighting
            dlt = s._flick(sp_["src"], t) - 1.0
            img *= 1 + (sp_["map"] * (dlt * s.k))[..., None] * np.float32(sp_["q"]["tint"])
        if s.pflame:
            P = s.pflame; q = P["q"]; x0, y0, x1, y1 = P["bb"]; f = s._flick(P["src"], t); fm = P["fm"][y0:y1, x0:x1, None]
            T = scroll(P["src"]["ftex"], 0, q["rise"] * t)[: y1 - y0, : x1 - x0][..., None] if P["src"]["ftex"].shape[0] >= y1 - y0 else 0
            g = np.clip(q["gain"] * (f - 1) + q["tongue"] * T * 0.5, -0.5, 0.6)
            roi = img[y0:y1, x0:x1]; hot = np.float32(q["hot"])
            mod = np.where(g > 0, roi + (hot - roi) * np.clip(g, 0, 1) * 0.6 + roi * g * 0.2, roi * (1 + g))
            roi[...] = roi * (1 - fm * s.k) + mod * fm * s.k
        for S in s.src:
            q = S["q"]; f = s._flick(S, t)
            if q["cast_light"]: light += (S["fall"] * (q["intensity"] * f * s.k))[..., None] * (np.float32(q["color"]) / 255.0)
            if q["halo"]:
                gauss_dot(img, q["xy"][0], q["xy"][1] - q["flame"][1] * 0.5, q["halo"]["sigma"], q["color"], q["halo"]["gain"] * f * s.k)
            # small flame: teardrop + rising tongues
            fw, fh = q["flame"]; x, y = q["xy"]
            if fh > 0:
                R = int(fh * 1.6) + 2; xa, xb, ya, yb = max(0, int(x - fw * 2)), min(W, int(x + fw * 2) + 1), max(0, int(y - fh * 1.4)), min(H, int(y + fh * 0.4) + 1)
                yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); vy = (y - yy) / fh; vx = (xx - x) / fw
                width = np.clip(1 - vy, 0, 1) ** 0.7 * (0.6 + 0.4 * np.clip(vy * 4, 0, 1))
                tongue = cv2.remap(S["ftex"], ((vx * 14 + 32) % 64).astype(np.float32), ((vy * 70 - 60 * t) % 256).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
                shape = np.clip(1 - (vx / (width + 1e-3)) ** 2, 0, 1) * (vy > -0.3) * np.clip(1 + vy * 3, 0, 1)
                fl = np.clip(shape * (0.75 + 0.45 * tongue) * (0.75 + 0.25 * f) - 0.25 * np.clip(vy, 0, 1), 0, 1) ** 1.3 * q["flame_gain"] * s.k
                core = np.float32([255, 236, 180]); outer = np.float32(q["color"])
                c = outer * (1 - fl[..., None]) + core * fl[..., None]
                img[ya:yb, xa:xb] += fl[..., None] * c * 0.9
        if s.hot:
            h = s.hot
            B = np.clip(1 + h["breathe"] * (0.6 * scroll(s.hb1, 3 * t, -9 * t) + 0.4 * scroll(s.hb2, -5 * t, -14 * t)), 0, 2)
            G = s.hm * B * h["gain"] * s.k
            light += (s.hlight * h["light"] * s.k * (0.85 + 0.15 * math.sin(t * 2.3)))[..., None] * (np.float32(h["color"]) / 255.0)
            glow = G[..., None] * np.float32(h["color"]) * 0.8
            if h["bloom"]: glow += cv2.GaussianBlur(G, (0, 0), h["bloom"])[..., None] * np.float32(h["color"]) * 0.6
            if getattr(s, "ft", None) and s.ft["clip_to_mask"]: glow *= s.m[..., None]                           # v3: hotspot glow kept inside the layer mask
            img += glow
        for B in s.beds:
            light += (B["light"] * (s.ft["light"] * s._flick(B["fs"], t) * s.k))[..., None] * (np.float32(s.ft["light_color"]) / 255.0)
        img += img * light * s.m[..., None]
        if s.bspill:                                                                           # b4: per-clump light spill (light only, 0 px)
            q = s.bspill["q"]; acc = np.zeros((H, W), np.float32)
            for L_ in s.bspill["L"]:
                xa, ya, xb, yb = L_["bb"]; f = s._flick(L_["B"]["fs"], t)
                acc[ya:yb, xa:xb] += L_["map"] * (q["base"] + q["amp"] * (f - 1.0))
            if s.bspill["dark"] is not None: img *= 1 - (s.bspill["dark"] * s.k)[..., None] * np.float32(q["dark_tint"])
            img *= 1 + (np.maximum(acc, -0.6) * s.k)[..., None] * np.float32(q["tint"])
        for B in s.beds:
            if s.ft["clip_to_mask"]:                                                           # v3: flames/soot/bloom never leave the layer mask (depth: foreground stays in front)
                x0, y0, x1, y1 = B["bb"]; before = img[y0:y1, x0:x1].copy(); s._flames(img, B, t)
                img[y0:y1, x0:x1] = before + (img[y0:y1, x0:x1] - before) * s.m[y0:y1, x0:x1, None]
            else: s._flames(img, B, t)
        if s.sparks: s._sparks(img, t)
        if s.emb and s.emb["count"]:
            e, ep = s.emb, s.ep; age = (t + ep["t0"]) % ep["life"]; k = age / ep["life"]
            px = ep["x"] + e["drift"][0] * age + ep["sw"] * np.sin(ep["ph"] + age * ep["sf"] * 2 * math.pi) * k
            py = ep["y"] - ep["v"] * age + e["drift"][1] * age
            br = ep["br"] * np.sin(math.pi * k) ** 0.6 * (0.7 + 0.3 * np.sin(ep["fl"] * t * 2 * math.pi + ep["ph"])) * e["gain"] * s.k
            for x, y, b, sz in zip(px, py, br, ep["sz"]):
                gauss_dot(img, x, y, sz * 0.7, e["color"], b * 0.9, s.em); gauss_dot(img, x, y + sz * 1.2, sz * 0.6, e["color"], b * 0.35, s.em)
    def _flames(s, img, B, t):
        ft, b = s.ft, B["b"]; x0, y0, x1, y1 = B["bb"]; h, w = y1 - y0, x1 - x0; Hh = b["height"]; f = s._flick(B["fs"], t)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); D = B["D"]
        rise = ft["rise"] * (Hh / 60.0) ** 0.5; ph = B["ph"]
        up = np.clip(D / Hh, 0, 1.5)
        wx = ft["sway_px"] * (Hh / 60.0) * cv2.remap(s.wtex, ((xx + x0) % 512).astype(np.float32), ((yy + ph + rise * 0.6 * t) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP) * up
        if s.shim: wx += s.shim["q"]["amp_px"] * 1.5 * s.shim["A"][y0:y1, x0:x1] * np.tanh(scroll(s.shim["N1"], 0, s.shim["q"]["rise"] * t)[y0:y1, x0:x1])
        Dw = cv2.remap(D, xx + wx, yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        sc = 60.0 / Hh                                                      # tongue spacing scales with flame size
        ux = (((xx + x0 + wx) * sc) % 512).astype(np.float32)
        T1 = cv2.remap(s.ftex1, ux, ((yy * sc + ph + rise * sc * t) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        T2 = cv2.remap(s.ftex2, ux, ((yy * sc + ph * 0.7 + rise * sc * 1.7 * t) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
        cl = np.interp(((xx[0] + x0 + 40 * math.sin(0.4 * t + ph)) % 1024), np.arange(1024), B["cl"]).astype(np.float32)[None, :]
        tong = (0.5 + 0.5 * np.tanh(1.6 * T1)) ** ft["tongue_sharp"]          # distinct tongues: per-column height peaks rising and reshaping
        shp = 0.2 + 1.0 * tong
        if ft["body_mix"] > 0:                                                                 # v3: broad flame bodies (low-freq) instead of thin tongues
            sb = sc * ft["body_scale"]; ub = (((xx + x0 + wx) * sb + 97) % 512).astype(np.float32)
            Tb = cv2.remap(s.ftex2, ub, ((yy * sb + ph * 0.3 + rise * sb * 1.2 * t) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            shp = (1 - ft["body_mix"]) * shp + ft["body_mix"] * (0.8 + 0.4 * np.tanh(0.9 * Tb) + 0.25 * tong)
        Hc = Hh * f * np.clip(0.5 + ft["clump_gain"] * b["clump"] * cl, 0.0, 1.4) * shp
        if b.get("taper"):                                                                     # b4: clump mound profile (tallest mid-clump)
            tq = {**dict(floor=0.25, power=0.8, pad=0.15), **b["taper"]}; xa_, xb_ = B["xr"]; hw = max((xb_ - xa_) * 0.5 * (1 + tq["pad"]), 4.0)
            env = np.clip(1 - ((xx[0] + x0 - 0.5 * (xa_ + xb_)) / hw) ** 2, 0, 1) ** tq["power"]
            Hc = Hc * (tq["floor"] + (1 - tq["floor"]) * env)[None, :]
        if ft["despeckle"] > 0:                                                                # v3: no wisps: tongue heights smoothed across x
            Hc = cv2.GaussianBlur(Hc, (0, 0), sigmaX=ft["despeckle"] * Hh, sigmaY=0.5)
        if ft["soot"]:                                                                         # v3: soot darkening above the flame tips, feeding the smoke
            q = {**dict(gain=0.45, lo=0.85, hi=1.9, ramp=0.25, smooth=0.0, fade=[0.75, 1.0], color=[30, 24, 22]), **ft["soot"]}
            Hs = cv2.GaussianBlur(Hc, (0, 0), sigmaX=q["smooth"] * Hh + 1e-3, sigmaY=q["smooth"] * Hh * 0.5 + 1e-3) if q["smooth"] > 0 else Hc
            rel = Dw / (Hs + 1e-3); Ts = cv2.remap(s.wtex, ((xx + x0 + wx) * 0.5 % 512).astype(np.float32), ((yy * 0.5 + ph + rise * 0.35 * t) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
            sa = smoothstep(q["lo"], q["lo"] + q["ramp"], rel) * (1 - smoothstep(q["lo"] + q["ramp"] + 0.15, q["hi"], rel)) * np.clip(0.6 + 0.4 * np.tanh(Ts), 0, 1)
            top = y1 - y0 - b["thickness"]
            sa = sa * (Dw < 1e3) * (1 - smoothstep(q["fade"][0] * top, q["fade"][1] * top, D)) * q["gain"] * f ** 0.5 * s.k
            roi0 = img[y0:y1, x0:x1]; roi0[...] = roi0 * (1 - sa[..., None]) + np.float32(q["color"]) * sa[..., None]
        I = np.clip(1 - Dw / (Hc + 1e-3), 0, 1) ** ft["body"] * np.clip(0.85 + 0.3 * T2, 0, 1.2) * (Dw < 1e3)
        I = np.clip(I, 0, 1) * b["intensity"] * s.k
        idx = np.clip(I * 255, 0, 255).astype(np.int32); col = s.lut[idx]
        a = smoothstep(0.03, 0.35, I)[..., None]
        roi = img[y0:y1, x0:x1]
        roi[...] = roi * (1 - a * ft["cover"]) + col * a * ft["cover"]                        # opaque-ish core over the timber
        roi[...] = 255 - (255 - roi) * (1 - np.clip(col / 255.0 * a * (1 - ft["cover"]), 0, 1))  # screen the rest (luminous edges)
        if ft["bloom"] > 0:
            g = cv2.GaussianBlur(I, (0, 0), ft["bloom_sigma"] * (Hh / 60.0) ** 0.5)
            roi += g[..., None] * np.float32(ft["light_color"]) * ft["bloom"] * 0.6
    def _sparks(s, img, t):
        S = s.sparks; q = S["q"]; age = (t + S["t0"]) % S["life"]; k = age / S["life"]
        vy = S["v"] * S["sc"] ** 0.5; turb = q["turb"] * np.sin(S["ph"] + age * 7.0) * k
        px = S["x"] + S["vx"] * age + turb; py = S["y"] - vy * age + 0.5 * q["gravity"] * age * age
        svx = S["vx"] + q["turb"] * 7.0 * np.cos(S["ph"] + age * 7.0) * k; svy = -vy + q["gravity"] * age
        br = (1 - k) ** 1.2 * (0.7 + 0.3 * np.sin(S["fl"] * t * 6.28 + S["ph"])) * q["gain"] * s.k
        hot, cool = np.float32(q["hot"]), np.float32(q["cool"])
        for i in range(len(px)):
            c = hot * (1 - k[i]) + cool * k[i]; sz = S["sz"][i] * max(S["sc"][i], 0.4) ** 0.4
            for j, wgt in ((0, 1.0), (1, 0.6), (2, 0.3)):
                dt = j * q["streak"] / 30.0 / 2
                gauss_dot(img, px[i] - svx[i] * dt, py[i] - svy[i] * dt, sz * 0.6, c, br[i] * wgt * 0.9, S["m"])
    def allow(s):
        a = s.m > 1e-4
        if s.fwarp: a |= s.fwarp["zone"] > 0
        for B in s.beds:
            x0, y0, x1, y1 = B["bb"]
            if s.ft["clip_to_mask"]: a[y0:y1, x0:x1] |= s.m[y0:y1, x0:x1] > 1e-4
            else: a[y0:y1, x0:x1] = True
            a |= B["light"] * s.m > 1e-5
        if s.bspill:
            for L_ in s.bspill["L"]:
                xa, ya, xb, yb = L_["bb"]; a[ya:yb, xa:xb] |= L_["map"] > 1e-5
            if s.bspill["dark"] is not None: a |= s.bspill["dark"] > 1e-5
        if s.shim: a |= dilate(s.shim["plateA"] > 1e-4, math.ceil(s.shim["q"]["amp_px"]) + 1)
        if s.sparks: a |= s.sparks["m"] > 1e-4
        for S in s.src:
            q = S["q"]; x, y = q["xy"]; fw, fh = q["flame"]; b = np.zeros((s.H, s.W), np.uint8)
            cv2.rectangle(b, (int(x - fw * 2) - 1, int(y - fh * 1.4) - 1), (int(x + fw * 2) + 2, int(y + fh * 0.4) + 2), 1, -1); a = a | (b > 0)
        if s.hot: a = a | (s.hm > 1e-4) | dilate(s.hm > 1e-4, s.hot["bloom"] * 4)
        if s.emb and s.emb["count"]: a = a | (s.em > 1e-4)
        for sp_ in s.spill: a = a | (sp_["map"] > 1e-5)
        if s.pflame: a = a | (s.pflame["fm"] > 1e-3)
        for S in s.src:
            if S["q"]["halo"]:
                q = S["q"]; b = np.zeros((s.H, s.W), np.uint8); r_ = int(q["halo"]["sigma"] * 3) + 3
                cv2.circle(b, (int(q["xy"][0]), int(q["xy"][1] - q["flame"][1] * 0.5)), r_, 1, -1); a = a | (b > 0)
        return a

class Foliage(Preset):
    """Grass/foliage sway: travelling gust fronts modulate a coherent sway + fine leaf flutter (displacement, tapered at
    the foliage edge), plus leaf-light dapple (luminance)."""
    D = dict(amp_px=1.1, dir_deg=0.0, gust_speed=90.0, gust_len=420.0, sway_hz=0.7, flutter=0.35, flutter_lo=14, dapple=0.05, edge_erode_px=0, edge_blur_px=1.5, vertical=0.3)
    def __init__(s, *a):
        super().__init__(*a); p = {**s.D, **s.p}; s.p = p; r = s.rng; H, W = s.H, s.W
        s.dm = taper(s.m, p["edge_erode_px"], p["edge_blur_px"])
        s.ph = pnoise(r, H, W, 160, 30) * 1.2; s.F1 = pnoise(r, H, W, p["flutter_lo"], 2); s.F2 = pnoise(r, H, W, p["flutter_lo"], 2)
        a = math.radians(p["dir_deg"]); s.proj = s.X * math.cos(a) + s.Y * math.sin(a); s.ca, s.sa = math.cos(a), math.sin(a)
    def _g(s, t):
        p = s.p; G = 0.5 + 0.5 * np.sin(2 * math.pi * (s.proj - p["gust_speed"] * t) / p["gust_len"] + s.ph)
        return G * G
    def disp(s, t):
        p = s.p; G = s._g(t)
        sway = G * (0.55 + 0.45 * np.sin(2 * math.pi * p["sway_hz"] * t + s.ph * 2))
        fl = p["flutter"] * (scroll(s.F1, -30 * t, 4 * t) * (0.4 + G))
        a = p["amp_px"] * s.k * s.dm
        tot = 1.25 * np.tanh((sway + fl) / 1.25)            # bounded: |sway+flutter| <= 1.25 x amp (stability)
        dx = -a * tot * s.ca; dy = -a * tot * s.sa + a * p["vertical"] * (sway - 0.3) * 0.5
        return dx, dy
    def shade(s, img, t):
        p = s.p; G = s._g(t)
        d = 1 + p["dapple"] * s.k * s.m * (0.6 * G - 0.25 + 0.4 * scroll(s.F2, -40 * t, 0) * G)
        img *= d[..., None]
    def allow(s): return dilate(s.m > 1e-4, math.ceil(s.p["amp_px"] * 2) + 1)

class LightShift(Preset):
    """Day -> dusk (or any) grade over time: colour gains, exposure, shadow tint, low sun glow; eased between t0..t1."""
    D = dict(t0=0.3, t1=3.7, gain=[1.06, 0.84, 0.66], ev=-0.45, shadow_color=[40, 30, 70], shadow_amt=0.22, sky_mask=None, sky_gain=[1.15, 0.78, 0.62],
             sun=None, sun_radius=260, sun_color=[255, 140, 70], sun_strength=0.35)
    def __init__(s, *a):
        super().__init__(*a); p = {**s.D, **s.p}; s.p = p
        s.sky = load_mask(p["sky_mask"], (s.H, s.W)) if p["sky_mask"] else None
        if p["sun"]:
            x, y = p["sun"]; d = np.sqrt((s.X - x) ** 2 + (s.Y - y) ** 2); s.sunf = np.exp(-(d / p["sun_radius"]) ** 2).astype(np.float32)
    def grade(s, img, t):
        p = s.p; k = ease(t, p["t0"], p["t1"]) * s.k
        if k <= 0: return
        L = lum(np.clip(img, 0, 255))[..., None]
        g = img * np.float32(p["gain"]) * (2.0 ** p["ev"])
        g = g * (1 - p["shadow_amt"] * (1 - L) ** 2) + np.float32(p["shadow_color"]) * p["shadow_amt"] * (1 - L) ** 2
        if s.sky is not None: g = g * (1 - s.sky[..., None]) + g * np.float32(p["sky_gain"]) * s.sky[..., None]
        if p["sun"]: g = 255 - (255 - g) * (1 - s.sunf[..., None] * p["sun_strength"] * np.float32(p["sun_color"]) / 255.0)
        m = (s.m * k)[..., None]; img[...] = img * (1 - m) + g * m

class WaterGlint(Preset):
    """Sun / moon path on water by LIGHT ONLY (0 px displacement): a broken column of light toward the source, widening toward
    the viewer, with perspective-correct specular glints that twinkle organically, concentrated along the path.
    Glint field = two periodic noise textures sampled in a perspective (u = x-offset/depth, v = 1/depth) frame, scrolled
    toward the viewer at different speeds; a glint lights where their sum crosses a threshold that is LOWER inside the path."""
    D = dict(light_x=470, horizon_y=200, path_w0=20, path_w1=220, path_power=0.9, along=[1.0, 0.55], path_gain=0.18, broken=0.7,
             su=0.9, sv=40.0, eps=10.0, wave_speed=0.035, cross_speed=0.004, thresh_in=1.6, thresh_out=3.0, glint_gain=1.3,
             glint_gamma=1.6, twinkle=0.6, outside=0.15, twinkle_lo=40, color=[255, 225, 170], bloom=0.35, bloom_sigma=1.6, lum_follow=0.5, glint_lo=[18, 12], glint_hi=[1.2, 1.0])
    def __init__(s, *a):
        super().__init__(*a); p = {**s.D, **s.p}; s.p = p; r = s.rng; H, W = s.H, s.W
        ys, xs = np.nonzero(s.m > 1e-3); s.bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        x0, y0, x1, y1 = s.bb; yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d = np.maximum(yy - p["horizon_y"] + p["eps"], 1.0); s.d = d
        k = np.clip((yy - p["horizon_y"]) / (H - p["horizon_y"]), 0, 1)
        w = p["path_w0"] + (p["path_w1"] - p["path_w0"]) * k ** p["path_power"]
        s.env = (np.exp(-((xx - p["light_x"]) / w) ** 2) * (p["along"][0] + (p["along"][1] - p["along"][0]) * k)).astype(np.float32)
        s.u = ((xx - p["light_x"]) / d * p["su"]).astype(np.float32); s.v = (p["sv"] / d).astype(np.float32)
        s.T1 = pnoise(r, 512, 512, p["glint_lo"][0], p["glint_hi"][0]); s.T2 = pnoise(r, 512, 512, p["glint_lo"][1], p["glint_hi"][1]); s.TW = pnoise(r, 512, 512, p["twinkle_lo"], 4)
        s.B1 = pnoise(r, 512, 512, 60, 3, ax=4.0)
        L = lum(s.ctx["plate"][y0:y1, x0:x1]); s.lf = (1 - p["lum_follow"]) + p["lum_follow"] * np.clip(L / (np.percentile(L, 98) + 1e-6), 0, 1.2)
        s.mb = s.m[y0:y1, x0:x1]
    def _samp(s, T, du, dv, su=1.0, sv=1.0):
        return cv2.remap(T, ((s.u * su * 512 + du) % 512).astype(np.float32), ((s.v * sv * 512 + dv) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    def shade(s, img, t):
        p = s.p; x0, y0, x1, y1 = s.bb; roi = img[y0:y1, x0:x1]
        ws, cs = p["wave_speed"] * 512, p["cross_speed"] * 512
        # broken path: horizontal light bands drifting toward the viewer (luminance only)
        Bn = s._samp(s.B1, cs * t, -ws * 0.6 * t, 1.0, 0.5)
        band = np.clip(0.5 + 0.5 * np.tanh(1.4 * Bn), 0, 1)
        path = s.env * ((1 - p["broken"]) + p["broken"] * band) * p["path_gain"] * s.k * s.mb * s.lf
        col = np.float32(p["color"]) / 255.0
        roi[...] = 255 - (255 - roi) * (1 - path[..., None] * col)
        # glints: crossing threshold of two counter-scrolling facet fields, lower threshold inside the path
        G1 = s._samp(s.T1, cs * t, -ws * t); G2 = s._samp(s.T2, -cs * 1.3 * t + 97, -ws * 1.45 * t + 211, 1.3, 1.3)
        tw = np.clip(0.5 + 0.5 * np.tanh(1.5 * s._samp(s.TW, 0, -ws * 0.3 * t + 50 * math.sin(0.2 * t), 0.4, 0.4)), 0, 1)
        en = np.clip(s.env / max(p["along"][0], 1e-6), 0, 1)
        thr = p["thresh_out"] + (p["thresh_in"] - p["thresh_out"]) * en
        # crossing of two wave-facet sets (product) -> sparse, spiky sparkles; weighted toward the path
        g = (np.clip(G1 - thr, 0, None) * np.clip(G2 - thr, 0, None)) ** p["glint_gamma"] * ((1 - p["twinkle"]) + p["twinkle"] * tw)
        g = g * (p["outside"] + (1 - p["outside"]) * en)
        g = g * s.mb * s.lf * p["glint_gain"] * s.k
        if p.get("grow_px", 0) > 0:                                                            # b4: bigger sparkle clusters (opt-in)
            kg = int(p["grow_px"]); g = np.maximum(g, cv2.dilate(g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * kg + 1, 2 * kg + 1))) * p.get("grow_gain", 0.7))
        if p.get("star", 0) > 0:                                                               # b4: horizontal specular streak (opt-in)
            ln = int(p.get("star_len", 15)) | 1; kx = np.float32(np.exp(-np.abs(np.arange(ln) - ln // 2) / (ln / 5.0)))[None, :]; kx /= kx.sum()
            g = g + cv2.filter2D(g, -1, kx * ln * 0.25, borderType=cv2.BORDER_REPLICATE) * p["star"]
        if p.get("halo", 0) > 0: g = g + cv2.GaussianBlur(np.clip(g, 0, 1.5), (0, 0), p.get("halo_sigma", 8.0)) * p["halo"]   # b4: soft wide bloom (opt-in)
        if p["bloom"] > 0: g = (g + cv2.GaussianBlur(g, (0, 0), p["bloom_sigma"]) * p["bloom"]) * s.mb     # bloom re-masked: strictly water
        elif p.get("grow_px", 0) > 0 or p.get("star", 0) > 0 or p.get("halo", 0) > 0: g = g * s.mb
        roi[...] = 255 - (255 - roi) * (1 - np.clip(g, 0, 1)[..., None] * col)
    def allow(s): return s.m > 1e-3

PRESETS = {"water-glint": WaterGlint, "water": Water, "map-light": MapLight, "sky": Sky, "atmos": Atmos, "smoke": Smoke, "fire-torchlight": FireTorch, "foliage": Foliage, "light-shift": LightShift}

# ----------------------------------------------------------------------------------------------- engine
class Engine:
    def __init__(s, cfg):
        s.cfg = cfg; im = cv2.imread(resolve(cfg["plate"]), cv2.IMREAD_COLOR)
        if im is None: raise FileNotFoundError(cfg["plate"])
        s.plate = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32); s.H, s.W = s.plate.shape[:2]
        Y, X = np.mgrid[0:s.H, 0:s.W].astype(np.float32)
        ctx = dict(H=s.H, W=s.W, X=X, Y=Y, plate=s.plate, half=cfg.get("half_seconds", 4.0)); s.X, s.Y = X, Y
        s.layers = []
        for i, L in enumerate(cfg["layers"]):
            rng = np.random.default_rng([int(cfg.get("seed", 1)), i])
            mask = load_mask(L["mask"], (s.H, s.W)) if L.get("mask") else np.ones((s.H, s.W), np.float32)
            s.layers.append((L, PRESETS[L["preset"]](ctx, mask, L.get("strength", 1.0), L.get("params", {}), rng)))
        s.allow = np.zeros((s.H, s.W), bool)
        for L, P in s.layers: s.allow |= P.allow()
        s.protect = np.zeros((s.H, s.W), bool)
        for p in cfg.get("protect", []): s.protect |= load_mask(p, (s.H, s.W)) > 0.5

    def render(s, t):
        dx = np.zeros((s.H, s.W), np.float32); dy = np.zeros_like(dx); used = False
        for L, P in s.layers:
            d = P.disp(t)
            if d is not None: dx += d[0]; dy += d[1]; used = True
        img = s.plate.copy()
        if used:
            nz = (np.abs(dx) + np.abs(dy)) > 1e-6
            w = cv2.remap(s.plate, s.X + dx, s.Y + dy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            img[nz] = w[nz]                      # pixels with zero displacement are exact plate copies
        for stage in ("shade", "overlay", "grade", "emit"):
            for L, P in s.layers: getattr(P, stage)(img, t)
        return np.clip(img, 0, 255), dx, dy

def zoom(img_f, z, W, H, outW, outH):
    s = (outH / H) * z
    M = np.float32([[s, 0, outW / 2 - s * W / 2], [0, s, outH / 2 - s * H / 2]])
    return cv2.warpAffine(img_f, M, (outW, outH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), M

def fit_font(text, path, size, maxw):
    while size > 10:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= maxw: return f
        size -= 1
    return ImageFont.truetype(path, size)

def label(frame_u8, tag, note):
    im = Image.fromarray(frame_u8); d = ImageDraw.Draw(im, "RGBA"); W, H = im.size
    f = ImageFont.truetype(FONT_B, 26); tw = f.getlength(tag)
    d.rounded_rectangle([22, 22, 22 + tw + 24, 22 + 40], 6, fill=(0, 0, 0, 150)); d.text((34, 27), tag, font=f, fill=(255, 255, 255, 255))
    if note:
        fn = fit_font(note, FONT_R, 19, W - 64); nw = fn.getlength(note)
        y = H - 74; d.rounded_rectangle([W / 2 - nw / 2 - 12, y - 6, W / 2 + nw / 2 + 12, y + 28], 6, fill=(0, 0, 0, 150))
        d.text((W / 2 - nw / 2, y), note, font=fn, fill=(255, 255, 255, 240))
    return np.asarray(im)

def ffmpeg_writer(path, W, H, fps):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-threads", "4", "-x264-params", "threads=4:lookahead-threads=1",
           "-movflags", "+faststart", "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:v", "+bitexact", path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def run(cfg, out_mp4, qc_dir, stills=True):
    t_start = time.time(); E = Engine(cfg); fps = cfg.get("fps", 30); outW, outH = cfg.get("size", [720, 1280]); half = cfg.get("half_seconds", 4.0)
    N = int(round(half * fps)); z0, z1 = cfg.get("camera", {}).get("z0", 1.0), cfg.get("camera", {}).get("z1", 1.04)
    notes = cfg.get("labels", {}); name = cfg["name"]
    if os.path.exists(out_mp4): raise SystemExit(f"refusing to overwrite existing {out_mp4}")
    wr = ffmpeg_writer(out_mp4, outW, outH, fps); fh = hashlib.sha256()
    allow_f = E.allow.astype(np.float32); outside = ~E.allow
    qc = dict(plate_outside_max=0.0, plate_outside_where=None, plate_outside_u8_max=0, out_outside_max=0, out_outside_where=None,
              disp_max=0.0, disp_where=None, disp_outside_mask_max=0.0, disp_protect_max=0.0, disp_protect_where=None,
              changed_pct_max=0.0, changed_pct_mean=0.0, mean_abs_diff_mean=0.0)
    mid = None
    for half_i, tag in ((0, "BEFORE"), (1, "AFTER")):
        for i in range(N):
            z = z0 + (z1 - z0) * (i / max(N - 1, 1)); t = i / fps
            before, M = zoom(E.plate, z, E.W, E.H, outW, outH); bu8 = np.round(np.clip(before, 0, 255)).astype(np.uint8)
            if half_i == 0:
                fr = bu8
            else:
                img, dx, dy = E.render(t)
                d = np.abs(img - E.plate).max(2)
                om = d[outside].max() if outside.any() else 0.0
                if om > qc["plate_outside_max"]:
                    yy, xx = np.unravel_index(np.argmax(np.where(outside, d, -1)), d.shape); qc["plate_outside_max"] = float(om); qc["plate_outside_where"] = dict(frame=N + i, x=int(xx), y=int(yy))
                du8 = np.abs(np.round(img).astype(np.int16) - np.round(E.plate).astype(np.int16)).max(2)
                qc["plate_outside_u8_max"] = max(qc["plate_outside_u8_max"], int(du8[outside].max()) if outside.any() else 0)
                ch = float((du8 > 2).mean() * 100); qc["changed_pct_max"] = max(qc["changed_pct_max"], ch); qc["changed_pct_mean"] += ch / N
                qc["mean_abs_diff_mean"] += float(d.mean()) / N
                mag = np.sqrt(dx * dx + dy * dy); mm = float(mag.max())
                if mm > qc["disp_max"]:
                    yy, xx = np.unravel_index(np.argmax(mag), mag.shape); qc["disp_max"] = mm; qc["disp_where"] = dict(frame=N + i, x=int(xx), y=int(yy))
                if outside.any(): qc["disp_outside_mask_max"] = max(qc["disp_outside_mask_max"], float(mag[outside].max()))
                if E.protect.any():
                    pm = float(mag[E.protect].max())
                    if pm > qc["disp_protect_max"]:
                        yy, xx = np.unravel_index(np.argmax(np.where(E.protect, mag, -1)), mag.shape); qc["disp_protect_max"] = pm; qc["disp_protect_where"] = dict(frame=N + i, x=int(xx), y=int(yy))
                after, _ = zoom(img, z, E.W, E.H, outW, outH); fr = np.round(np.clip(after, 0, 255)).astype(np.uint8)
                aw = cv2.warpAffine(allow_f, M, (outW, outH), flags=cv2.INTER_LINEAR) > 0; ow = ~dilate(aw, 2)
                od = np.abs(fr.astype(np.int16) - bu8.astype(np.int16)).max(2)
                if ow.any() and od[ow].max() > qc["out_outside_max"]:
                    yy, xx = np.unravel_index(np.argmax(np.where(ow, od, -1)), od.shape); qc["out_outside_max"] = int(od[ow].max()); qc["out_outside_where"] = dict(frame=N + i, x=int(xx), y=int(yy))
                if i == N // 2: mid = (img.copy(), fr.copy(), d.copy())
            note = notes.get("before_note" if half_i == 0 else "after_note", "")
            lf = label(fr, tag, note); fh.update(lf.tobytes()); wr.stdin.write(lf.tobytes())
    wr.stdin.close(); rc = wr.wait()
    if rc: raise SystemExit(f"ffmpeg failed rc={rc}")
    qc.update(name=name, mp4=out_mp4, md5=md5(out_mp4), frames_sha256=fh.hexdigest(), frames=2 * N, fps=fps, size=[outW, outH],
              duration_s=2 * N / fps, mask_coverage_pct=float(E.allow.mean() * 100), seconds_to_render=round(time.time() - t_start, 1),
              plate=cfg["plate"], seed=cfg.get("seed", 1), camera=dict(z0=z0, z1=z1, per_half=True),
              stability_pass_outside_mask=(qc["plate_outside_max"] == 0 and qc["out_outside_max"] == 0))
    if stills and mid is not None:
        os.makedirs(qc_dir, exist_ok=True)
        img, fr, d = mid
        cv2.imwrite(os.path.join(qc_dir, f"{name}_after_mid.png"), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(qc_dir, f"{name}_after_mid_platefull.png"), cv2.cvtColor(np.round(img).astype(np.uint8), cv2.COLOR_RGB2BGR))
        ov = E.plate.copy(); cols = [(255, 60, 60), (60, 120, 255), (60, 230, 90), (255, 0, 255), (255, 200, 0), (0, 230, 230), (255, 140, 0), (180, 120, 255)]
        for j, (L, P) in enumerate(E.layers):
            a = (P.allow().astype(np.float32) * 0.45)[..., None]; ov = ov * (1 - a) + np.float32(cols[j % len(cols)]) * a
        ov = np.round(ov).astype(np.uint8)
        if E.protect.any():
            hatch = ((E.X + E.Y) % 14 < 2) & E.protect; ov[hatch] = (255, 255, 255)
        y = 30
        for j, (L, P) in enumerate(E.layers):
            cv2.rectangle(ov, (20, y - 18), (40, y + 2), cols[j % len(cols)][::-1][::-1], -1)
            cv2.putText(ov, L["preset"], (48, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA); y += 30
        if E.protect.any(): cv2.putText(ov, "white hatch = protect (no displacement)", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(qc_dir, f"{name}_mask_overlay.png"), cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))
        hm = cv2.applyColorMap(np.clip(d * 4, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO); hm[~E.allow] = (hm[~E.allow] * 0 + np.uint8([90, 0, 0]))
        cv2.imwrite(os.path.join(qc_dir, f"{name}_diff_heat_mid.png"), hm)
    return qc

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--config", required=True); ap.add_argument("--repeat-check", action="store_true")
    ap.add_argument("--suffix", default=""); ap.add_argument("--out-dir", default=None, help="override (e.g. /tmp preview dir)")
    a = ap.parse_args(); cfg = json.load(open(a.config))
    out_dir = a.out_dir or os.path.join(ENGINE_DIR, cfg.get("out_dir", "batch1")); os.makedirs(out_dir, exist_ok=True)
    qc_dir = os.path.join(out_dir, "qc"); name = cfg["name"] + a.suffix; cfg["name"] = name
    out = os.path.join(out_dir, name + ".mp4")
    qc = run(cfg, out, qc_dir)
    if a.repeat_check:
        rdir = os.path.join(out_dir, "determinism"); os.makedirs(rdir, exist_ok=True)
        q2 = run({**cfg}, os.path.join(rdir, name + "_rerun.mp4"), qc_dir, stills=False)
        qc["determinism"] = dict(rerun_mp4=q2["mp4"], rerun_md5=q2["md5"], md5_identical=q2["md5"] == qc["md5"], frames_sha256_identical=q2["frames_sha256"] == qc["frames_sha256"])
    qp = os.path.join(qc_dir, name + ".qc.json"); json.dump(qc, open(qp, "w"), indent=1)
    print(json.dumps(qc, indent=1))

if __name__ == "__main__":
    main()
