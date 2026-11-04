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
            roi = img[y0:y1, x0:x1]
            if q.get("cool"):                                                                  # b6 opt-in: cool/desaturate what shows through the plume base
                cq = {**dict(amt=0.6, tint=[0.92, 0.98, 1.12], env_pow=0.6, base=[0.0, 0.45]), **q["cool"]}
                bw = 1 - smoothstep(cq["base"][0], cq["base"][1], sn)
                ca = np.clip(env ** cq["env_pow"] * bw * cq["amt"] * s.k, 0, 1) * P["mclip"]
                Y = (0.299 * roi[..., 0] + 0.587 * roi[..., 1] + 0.114 * roi[..., 2])[..., None]
                roi[...] = roi + (Y * np.float32(cq["tint"]) - roi) * ca[..., None]
            roi[...] = roi * (1 - a[..., None]) + col * a[..., None]
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
            if ft.get("opaque"):                                                               # b6 opt-in: solid flames (opaque cores, clean alpha)
                oq = {**dict(lo=0.03, hi=0.2, gamma=0.75, alpha=1.0, rim=0.35, rim_px=1.6, tip_alpha=0.7,
                             lut=[[0.0, [140, 26, 6]], [0.15, [200, 52, 10]], [0.35, [242, 104, 18]], [0.55, [255, 160, 42]],
                                  [0.75, [255, 212, 112]], [0.9, [255, 238, 182]], [1.0, [255, 249, 224]]]), **ft["opaque"]}
                xo_ = np.float32([c[0] for c in oq["lut"]]); co_ = np.float32([c[1] for c in oq["lut"]])
                s.olut = np.stack([np.interp(np.linspace(0, 1, 256), xo_, co_[:, k]) for k in range(3)], 1).astype(np.float32); s.oq = oq
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
                Rd = R * q["dark_radius_mult"]
                if q.get("dark_exact"):                                                        # b5 opt-in: full-frame falloff (no bbox-truncation edges in the dark map)
                    lmF = np.zeros((H, W), np.uint8); cv2.polylines(lmF, [np.int32(np.round(pts))], False, 1, max(int(b["thickness"]), 3))
                    dF = cv2.distanceTransform((1 - lmF).astype(np.uint8), cv2.DIST_L2, 5); tot = np.maximum(tot, 1.0 / (1 + (dF / Rd) ** q["power"]))
                else: tot[ya:yb, xa:xb] = np.maximum(tot[ya:yb, xa:xb], 1.0 / (1 + (d / Rd) ** q["power"]))
            s.bspill = dict(q=q, L=L_, dark=(q["dark"] * (1 - np.clip(tot, 0, 1)) * M).astype(np.float32) if q["dark"] > 0 else None)
        # ---- seat (batch 5, opt-in per bed): seat a clump onto its fuel -- a charred dark band at/below the base line and a hot
        #      contact glow hugging the base (driven by the clump's flicker).  Light/colour only, 0 px, inside the layer mask.
        s.seats = []
        for B in (s.beds if ft else []):
            b = B["b"]
            if not b.get("seat"): continue
            q = {**dict(dark=0.45, dark_w=7.0, dark_up=0.35, glow=0.55, glow_w=3.5, glow_up=0.5, color=[255, 170, 80], pad=0.2, tex=0.5), **b["seat"]}
            pts = np.float32(b["points"]); xa_, xb_ = B["xr"]; th = float(b["thickness"]); padx = (xb_ - xa_) * q["pad"] + 4
            xa, xb = int(max(0, xa_ - padx)), int(min(W, xb_ + padx + 1)); ya, yb = int(max(0, pts[:, 1].min() - th - 12)), int(min(H, pts[:, 1].max() + th + q["dark_w"] * 3 + 4))
            X_ = np.arange(xa, xb, dtype=np.float32); yb_ = np.interp(X_, pts[:, 0], pts[:, 1]).astype(np.float32)
            dy = np.arange(ya, yb, dtype=np.float32)[:, None] - (yb_[None, :] + th * 0.5)        # >0 below the fuel line
            hw = max((xb_ - xa_) * 0.5 * (1 + q["pad"]), 3.0); ex = np.clip(1 - ((X_ - 0.5 * (xa_ + xb_)) / hw) ** 2, 0, 1) ** 0.6
            tx = np.clip(1 + q["tex"] * np.tanh(1.5 * s.wtex[int(B["ph"]) % 512, (X_.astype(np.int32) * 3) % 512]), 0, 2)[None, :]
            dk = q["dark"] * np.where(dy > 0, np.exp(-(dy / q["dark_w"]) ** 2), np.exp(-(dy / (th * q["dark_up"] + 1e-3)) ** 2)) * ex[None, :]
            gl = q["glow"] * np.exp(-((dy + th * q["glow_up"]) / q["glow_w"]) ** 2) * ex[None, :] * tx
            Mc = s.m[ya:yb, xa:xb]
            s.seats.append(dict(B=B, bb=(xa, ya, xb, yb), dark=(dk * Mc).astype(np.float32), glow=(gl * Mc).astype(np.float32), col=np.float32(q["color"]) / 255.0))
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
        for S_ in getattr(s, "seats", []):                                                     # b5: seat clumps onto fuel (before flames)
            xa, ya, xb, yb = S_["bb"]; f = s._flick(S_["B"]["fs"], t); roi = img[ya:yb, xa:xb]
            roi *= 1 - (S_["dark"] * s.k)[..., None]
            roi[...] = 255 - (255 - roi) * (1 - np.clip(S_["glow"] * f * s.k, 0, 1)[..., None] * S_["col"])
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
        if ft.get("opaque"):                                                                   # b6: solid body, hot core -> orange/red tips
            oq = s.oq; Ig = np.clip(I, 0, 1) ** oq["gamma"]; col = s.olut[np.clip(Ig * 255, 0, 255).astype(np.int32)]
            ao = smoothstep(oq["lo"], oq["hi"], I) * (oq["tip_alpha"] + (1 - oq["tip_alpha"]) * smoothstep(oq["hi"], oq["hi"] * 2.5, I)) * oq["alpha"]
            roi[...] = roi * (1 - ao[..., None]) + col * ao[..., None]
            if oq["rim"] > 0:                                                                  # thin luminous fringe just outside the body
                rg = np.clip(cv2.GaussianBlur(ao, (0, 0), oq["rim_px"]) - ao, 0, 1) * oq["rim"]
                roi[...] = 255 - (255 - roi) * (1 - np.clip(rg[..., None] * np.float32(ft["light_color"]) / 255.0, 0, 1))
        else:
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
        for S_ in getattr(s, "seats", []):
            xa, ya, xb, yb = S_["bb"]; a[ya:yb, xa:xb] |= (S_["dark"] > 1e-5) | (S_["glow"] > 1e-5)
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
        if p.get("streak"):                                                                    # b8 opt-in: break the path into distinct streaks with dark gaps
            S = {**dict(k=7000.0, e2=130.0, duty=0.3, soft=0.18, jitter=0.35, jit_lo=90, dash=0.55, dash_lo=[70, 3], speed=0.45, floor=0.0,
                        fade_px=[3.0, 6.0], path=True), **p["streak"]}; s.S = S
            s.sphi = (S["k"] / (d - p["eps"] + S["e2"])).astype(np.float32)                    # row phase: rows widen toward the viewer
            sp = (d - p["eps"] + S["e2"]) ** 2 / S["k"]                                        # local row spacing (px)
            s.sfade = smoothstep(S["fade_px"][0], S["fade_px"][1], sp).astype(np.float32)      # near the horizon rows merge -> no comb aliasing
            s.SJ = pnoise(r, 512, 512, S["jit_lo"], 6); s.SD = pnoise(r, 512, 512, S["dash_lo"][0], S["dash_lo"][1], ax=0.25)
    def _streak(s, t):
        S = s.S; ws, cs = s.p["wave_speed"] * 512, s.p["cross_speed"] * 512
        J = s._samp(s.SJ, cs * t, -ws * 0.5 * t, 1.0, 0.4)
        c = np.cos(2 * math.pi * (s.sphi + S["speed"] * t + S["jitter"] * J))
        thr = math.cos(math.pi * S["duty"])
        row = smoothstep(thr - S["soft"], thr + S["soft"], c)
        Dn = s._samp(s.SD, -cs * 2 * t + 31, -ws * 0.8 * t + 77, 1.0, 1.0)
        dash = np.clip(0.5 + 0.5 * np.tanh(2.0 * (Dn + S["dash"])), 0, 1)
        st = row * dash
        st = st * s.sfade + (1 - s.sfade) * (0.35 + 0.65 * dash)
        return (S["floor"] + (1 - S["floor"]) * st).astype(np.float32)
    def _samp(s, T, du, dv, su=1.0, sv=1.0):
        return cv2.remap(T, ((s.u * su * 512 + du) % 512).astype(np.float32), ((s.v * sv * 512 + dv) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    def shade(s, img, t):
        p = s.p; x0, y0, x1, y1 = s.bb; roi = img[y0:y1, x0:x1]
        ws, cs = p["wave_speed"] * 512, p["cross_speed"] * 512
        # broken path: horizontal light bands drifting toward the viewer (luminance only)
        Bn = s._samp(s.B1, cs * t, -ws * 0.6 * t, 1.0, 0.5)
        band = np.clip(0.5 + 0.5 * np.tanh(1.4 * Bn), 0, 1)
        path = s.env * ((1 - p["broken"]) + p["broken"] * band) * p["path_gain"] * s.k * s.mb * s.lf
        st = s._streak(t) if p.get("streak") else None
        if st is not None and s.S["path"]: path = path * st
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
        if st is not None: g = g * st
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

class MapInk(Preset):
    """b5 R&D (opt-in preset "map-ink"): ink EVENTS on a map, built on the locked ink-nib look (same wet/dry ink, pigment, bloom).
    stamps: a seal impression drops in (converging soft shadow + defocused falling ghost, accelerating, no bounce), presses
            (ink splat spray, paper press-darkening + deboss shading), then dries wet->dry and its bloom settles.
    washes: a territory wash bleeds outward from a seed along a masked region (geodesic arrival-time front over a fingered
            speed field), with a darker wet front, granulation, watercolour edge pooling and an inked land border.
    Colour/light only: 0 px displacement."""
    SD = dict(t_on=0.5, radius=40.0, ring_w=5.0, inner=0.8, inner_w=1.8, emblem="star8", emblem_r=0.54, dots=12, rot_deg=0.0,
              drop_s=0.32, ghost=0.3, ghost_scale=1.25, ghost_blur=10.0, shadow=0.42, shadow_off=[18.0, 24.0], shadow_sigma=[18.0, 3.0],
              splat=14, splat_r=[1.08, 1.6], splat_px=[1.0, 3.2], streaks=3, splat_spread=1.2, press=0.16, press_settle=0.06, press_s=0.35,
              emboss=0.12, emboss_px=2.2, cover=0.3, pressure=0.25, bloom=0.45, bloom_px=1.8, bloom_s=0.3, bloom_settle=0.4, spread_s=0.07,
              opacity=1.0)
    WD = dict(mask=None, seed=[0, 0], t0=0.15, t1=3.2, power=2.0, color=None, wet_color=None, opacity=0.4, wet_opacity=0.62, pigment=0.12,
              front_s=0.14, edge=0.35, edge_s=0.3, rim=0.32, rim_px=4.0, finger=0.65, finger_lo=90, gran=0.22, step=3,
              land=None, border_w=2.4, border=0.85, border_s=0.25)
    def __init__(s, *a):
        super().__init__(*a); p = s.p; r = s.rng; H, W = s.H, s.W
        s.ink = {**dict(wet_color=[62, 10, 6], dry_color=[142, 46, 26], wet_opacity=0.97, dry_opacity=0.88, dry_time=0.9, pigment=0.55), **p.get("ink", {})}
        s.stamps = []
        for q in p.get("stamps", []):
            q = {**s.SD, **(s.WX if q.get("style") == "wax" else {}), **(s.IX if q.get("style") == "icon" else {}), **q}; s.stamps.append(s._stamp_init(q, r))
        s.washes = []
        for q in p.get("washes", []):
            q = {**s.WD, **(s.SW if q.get("reach_frac") else {}), **q}; s.washes.append(s._wash_init(q, r))
    # ---------------------------------------------------------------- stamps
    def _stamp_init(s, q, r):
        if q.get("style") == "wax": return s._wax_init(q, r)
        if q.get("style") == "icon": return s._icon_init(q, r)
        H, W = s.H, s.W; x, y = q["xy"]; R = q["radius"]; ext = int(R * max(q["splat_r"][1], q["ghost_scale"]) + q["ghost_blur"] * 3 + max(q["shadow_off"]) + q["shadow_sigma"][0] * 3 + 6)
        xa, xb, ya, yb = max(0, int(x) - ext), min(W, int(x) + ext + 1), max(0, int(y) - ext), min(H, int(y) + ext + 1)
        h, w = yb - ya, xb - xa; ss = 4; c = ((x - xa) * ss, (y - ya) * ss)
        def P(px, py): return (int(round(px * 16)), int(round(py * 16)))
        can = np.zeros((h * ss, w * ss), np.uint8)
        cv2.circle(can, P(*c), int(R * ss * 16), 255, max(1, int(q["ring_w"] * ss)), cv2.LINE_AA, shift=4)
        cv2.circle(can, P(*c), int(R * q["inner"] * ss * 16), 255, max(1, int(q["inner_w"] * ss)), cv2.LINE_AA, shift=4)
        rot = math.radians(q["rot_deg"])
        if q["dots"]:
            rd = R * (1 + q["inner"]) * 0.5
            for i in range(q["dots"]):
                th = rot + 2 * math.pi * i / q["dots"]
                cv2.circle(can, P(c[0] + math.cos(th) * rd * ss, c[1] + math.sin(th) * rd * ss), int(q["ring_w"] * 0.32 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        if q["emblem"] == "star8":
            re = R * q["emblem_r"]; pts = []
            for i in range(16):
                th = rot - math.pi / 2 + math.pi * i / 8; rr = re if i % 2 == 0 else re * (0.36 if i % 4 == 1 or i % 4 == 3 else 0.36)
                if i % 4 == 2: rr = re * 0.62
                pts.append(P(c[0] + math.cos(th) * rr * ss, c[1] + math.sin(th) * rr * ss))
            cv2.fillPoly(can, [np.int32(pts)], 255, cv2.LINE_AA, shift=4)
            cv2.circle(can, P(*c), int(re * 0.16 * ss * 16), 0, -1, cv2.LINE_AA, shift=4)
        A = cv2.resize(can, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2); ang = np.arctan2(yy - y, xx - x)
        phi = float(r.uniform(0, 2 * math.pi))
        tex = pnoise(r, h, w, max(6.0, R * 0.25), 1.0); tex2 = pnoise(r, h, w, 3.0, 0.7)
        cover = np.clip(1 - q["cover"] * np.clip(0.5 + 0.5 * tex, 0, 1) ** 2 - 0.12 * np.clip(tex2, 0, None), 0.35, 1)      # rubber-stamp ink take
        press = 1 - q["pressure"] * (0.5 - 0.5 * np.cos(ang - phi)) * smoothstep(R * 0.5, R * 1.05, d)                 # uneven hand pressure
        A = A * cover * press
        # splat spray (on the heavy-pressure side), drawn once
        sc_ = np.zeros((h * ss, w * ss), np.uint8)
        for i in range(q["splat"]):
            th = phi + r.normal(0, q["splat_spread"]); u_ = r.uniform(0, 1); dd = R * (q["splat_r"][0] + (q["splat_r"][1] - q["splat_r"][0]) * u_ ** 1.6); sz = (q["splat_px"][0] + (q["splat_px"][1] - q["splat_px"][0]) * r.uniform(0, 1) ** 2.5) * (1.25 - 0.5 * u_)
            cv2.circle(sc_, P(c[0] + math.cos(th) * dd * ss, c[1] + math.sin(th) * dd * ss), int(max(sz, 0.6) * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        for i in range(q["streaks"]):
            th = phi + r.normal(0, q["splat_spread"] * 0.6); d0, d1 = R * 1.0, R * r.uniform(1.12, 1.32)
            cv2.line(sc_, P(c[0] + math.cos(th) * d0 * ss, c[1] + math.sin(th) * d0 * ss), P(c[0] + math.cos(th) * d1 * ss, c[1] + math.sin(th) * d1 * ss),
                     255, max(1, int(r.uniform(1.0, 2.0) * ss)), cv2.LINE_AA, shift=4)
        Sp = cv2.resize(sc_, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        disc = (d <= R * 1.06).astype(np.float32); discb = cv2.GaussianBlur(disc, (0, 0), q["emboss_px"])
        gx = cv2.Sobel(discb, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(discb, cv2.CV_32F, 0, 1, ksize=3); gn = max(float(np.abs(gx).max()), 1e-6)
        emb = (-(gx + gy) * 0.7071 / gn).astype(np.float32)                                          # deboss: light from top-left
        Ab = cv2.GaussianBlur(A, (0, 0), q["bloom_px"]); Ab = np.clip(Ab / (Ab.max() + 1e-6) * 1.5, 0, 1) * (1 - A) * (0.6 + 0.4 * np.clip(0.5 + 0.5 * tex2, 0, 1))
        Asum = cv2.GaussianBlur(np.clip(A + disc * 0.25, 0, 1), (0, 0), 1.0)                         # silhouette for shadow / ghost
        return dict(q=q, bb=(xa, ya, xb, yb), A=A.astype(np.float32), Sp=Sp, Ab=Ab.astype(np.float32), disc=cv2.GaussianBlur(disc, (0, 0), 1.2), emb=emb,
                    sil=Asum.astype(np.float32), c=(x - xa, y - ya), lm=s.m[ya:yb, xa:xb])
    def _warp(s, z, c, sc, dx=0.0, dy=0.0):
        M = np.float32([[sc, 0, c[0] * (1 - sc) + dx], [0, sc, c[1] * (1 - sc) + dy]])
        return cv2.warpAffine(z, M, (z.shape[1], z.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    def _comp(s, roi, a, wet, wetc=None, dryc=None, k=None):
        I = s.ink; wc = np.float32(wetc or I["wet_color"]); dc = np.float32(dryc or I["dry_color"]); k = I["pigment"] if k is None else k
        cc = (dc * (1 - wet[..., None]) + wc * wet[..., None]) / 255.0
        roi[...] = roi * (1 - a[..., None]) + (roi * cc * (1 - k) + cc * 255.0 * k) * a[..., None]
    def _stamp(s, img, S, t):
        if S.get("wax"): return s._wax(img, S, t)
        if S.get("icon"): return s._icon(img, S, t)
        q = S["q"]; I = s.ink; xa, ya, xb, yb = S["bb"]; roi = img[ya:yb, xa:xb]; lm = S["lm"]; age = t - q["t_on"]
        if age < -q["drop_s"]: return
        if age < 0:                                                                                   # falling: accelerating, so height = 1 - u^2
            u = 1 + age / q["drop_s"]; hgt = 1 - u * u
            ox, oy = q["shadow_off"]; sg = q["shadow_sigma"][1] + (q["shadow_sigma"][0] - q["shadow_sigma"][1]) * hgt
            sh = cv2.GaussianBlur(s._warp(S["sil"], S["c"], 1 + 0.15 * hgt, ox * hgt, oy * hgt), (0, 0), sg)
            sh = np.clip(sh / (sh.max() + 1e-6), 0, 1) * q["shadow"] * (0.25 + 0.75 * u) * lm * s.k
            roi *= 1 - sh[..., None] * np.float32([0.85, 0.9, 1.0])
            g = s._warp(S["A"], S["c"], 1 + (q["ghost_scale"] - 1) * hgt); bl = q["ghost_blur"] * hgt
            if bl > 0.3: g = cv2.GaussianBlur(g, (0, 0), bl)
            s._comp(roi, (g * q["ghost"] * u * lm * s.k).astype(np.float32), np.ones(g.shape, np.float32))
            return
        sp = min(1.0, age / q["spread_s"]); sc = 0.965 + 0.035 * (1 - (1 - sp) ** 2)                 # ink squashes outward to rest, monotonic
        wet = math.exp(-age / I["dry_time"]); op = (I["dry_opacity"] + (I["wet_opacity"] - I["dry_opacity"]) * wet) * q["opacity"]
        pr = q["press_settle"] + (q["press"] - q["press_settle"]) * math.exp(-age / q["press_s"])    # paper press: dark at impact, settles
        roi *= 1 - (S["disc"] * pr * lm * s.k)[..., None]
        roi *= 1 + (S["emb"] * q["emboss"] * min(1.0, age / 0.05) * lm * s.k)[..., None]
        A = S["A"] if sp >= 1 else s._warp(S["A"], S["c"], sc)
        ab = age / q["bloom_s"]; gb = min(1.0, ab * math.exp(1 - ab)) * (1 - q["bloom_settle"]) + q["bloom_settle"] * min(1.0, ab)
        spl = S["Sp"] if age >= q["spread_s"] * 1.5 else s._warp(S["Sp"], S["c"], 0.85 + 0.15 * min(1.0, age / (q["spread_s"] * 1.5)))
        a = np.maximum(A * op, S["Ab"] * q["bloom"] * gb * op); a = np.maximum(a, spl * op * 0.95)
        s._comp(roi, (np.clip(a, 0, 1) * lm * s.k).astype(np.float32), np.full(a.shape, wet, np.float32))
    # ---------------------------------------------------------------- washes
    def _wash_init(s, q, r):
        if q.get("reach_frac"): return s._swash_init(q, r)
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import dijkstra
        H, W = s.H, s.W; M = load_mask(q["mask"], (H, W)) * s.m; st = int(q["step"])
        h, w = (H + st - 1) // st, (W + st - 1) // st
        Ms = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA) > 0.35
        nz = pnoise(r, h, w, q["finger_lo"] / st, 1.5); spd = np.exp(q["finger"] * nz).astype(np.float64)
        idx = -np.ones((h, w), np.int64); ys, xs = np.nonzero(Ms); idx[ys, xs] = np.arange(len(ys))
        rows, cols, vals = [], [], []
        for dy_, dx_, ln in ((0, 1, 1.0), (1, 0, 1.0), (1, 1, 1.4142), (1, -1, 1.4142)):
            y2, x2 = ys + dy_, xs + dx_; ok = (y2 < h) & (x2 >= 0) & (x2 < w); ok[ok] = Ms[y2[ok], x2[ok]]
            a_, b_ = idx[ys[ok], xs[ok]], idx[y2[ok], x2[ok]]; cst = ln * st * 0.5 * (1 / spd[ys[ok], xs[ok]] + 1 / spd[y2[ok], x2[ok]])
            rows += [a_, b_]; cols += [b_, a_]; vals += [cst, cst]
        G = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(ys),) * 2).tocsr()
        sx, sy = q["seed"]; sx_, sy_ = int(sx // st), int(sy // st)
        if not Ms[sy_, sx_]: d2 = (ys - sy_) ** 2 + (xs - sx_) ** 2; k0 = int(np.argmin(d2))
        else: k0 = int(idx[sy_, sx_])
        dist = dijkstra(G, indices=k0); dist[~np.isfinite(dist)] = np.nan
        D = np.full((h, w), np.nan, np.float32); D[ys, xs] = dist
        dmax = float(np.nanpercentile(dist, 99.7)); D = np.nan_to_num(D, nan=dmax * 1.5)
        D = cv2.GaussianBlur(D, (0, 0), 0.8); D = cv2.resize(D, (W, H), interpolation=cv2.INTER_LINEAR)
        frac = np.clip(D / dmax, 0, 1.5)
        tA = (q["t0"] + (q["t1"] - q["t0"]) * (1 - np.clip(1 - frac, 0, 1) ** (1.0 / q["power"]))).astype(np.float32)   # front eases out: fast, then slows
        tA[frac > 1.0] = 1e3
        ys_, xs_ = np.nonzero(M > 1e-3); bb = (int(xs_.min()), int(ys_.min()), int(xs_.max()) + 1, int(ys_.max()) + 1); x0, y0, x1, y1 = bb
        Mb = M[y0:y1, x0:x1]; inside = (Mb > 0.5).astype(np.uint8)
        de = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
        gran = np.clip(1 - q["gran"] * (0.5 + 0.5 * pnoise(r, y1 - y0, x1 - x0, 5.0, 0.8)), 0, 1).astype(np.float32)
        rim = (np.exp(-(de / q["rim_px"]) ** 2) * inside).astype(np.float32)
        brd = None
        if q["land"]:
            L = load_mask(q["land"], (H, W))[y0:y1, x0:x1] > 0.5
            outland = (L & (Mb <= 0.5)).astype(np.uint8); near = cv2.dilate(outland, np.ones((int(q["border_w"] * 2) * 2 + 3,) * 2, np.uint8)) > 0
            brd = (np.clip(1 - np.abs(de - q["border_w"] * 0.5) / q["border_w"], 0, 1) * near * inside).astype(np.float32)
            fib = pnoise(r, y1 - y0, x1 - x0, 7, 0.8); brd = brd * np.clip(0.8 + 0.3 * fib, 0.5, 1.1)
        return dict(q=q, bb=bb, tA=tA[y0:y1, x0:x1], M=Mb.astype(np.float32), gran=gran, rim=rim, brd=brd)
    def _wash(s, img, Wd, t):
        if Wd.get("soft"): return s._swash(img, Wd, t)
        q = Wd["q"]; I = s.ink
        if t < q["t0"]: return
        x0, y0, x1, y1 = Wd["bb"]; roi = img[y0:y1, x0:x1]; dt = t - Wd["tA"]
        fill = smoothstep(0.0, q["front_s"], dt)
        wet = np.exp(-np.maximum(dt, 0) / I["dry_time"]) * (dt > 0)
        edge = smoothstep(0.0, 0.04, dt) * (1 - smoothstep(0.04, q["edge_s"], dt)) * q["edge"]          # darker wet bleeding front
        op = q["opacity"] + (q["wet_opacity"] - q["opacity"]) * wet
        a = (fill * op * Wd["gran"] + edge + Wd["rim"] * q["rim"] * fill) * Wd["M"]
        wc, dc = q["wet_color"] or I["wet_color"], q["color"] or I["dry_color"]
        s._comp(roi, (np.clip(a, 0, 1) * s.k).astype(np.float32), np.clip(wet + edge, 0, 1).astype(np.float32), wc, dc, q["pigment"])
        if Wd["brd"] is not None:
            bt = smoothstep(0.0, q["border_s"], dt); bw = np.exp(-np.maximum(dt, 0) / I["dry_time"])
            s._comp(roi, (Wd["brd"] * bt * q["border"] * I["dry_opacity"] * s.k).astype(np.float32), bw.astype(np.float32))
    # ---------------------------------------------------------------- b6: wax seal (stamps[].style = "wax", opt-in)
    WX = dict(blob=1.28, blob_var=0.045, bulge=0.08, lip=0.28, lip_w=0.07, depth=0.42, edge_round=0.2, beads=30, bead_r=0.89, bead_px=2.1,
              ring2=0.8, ring2_w=1.6, design="tudor_rose", design_r=0.66, relief=3.0, light=[-0.55, -0.65, 0.55], amb=0.38, spec=0.75, spec_pow=22,
              gloss_wet=1.0, gloss_dry=0.35, gloss_s=0.7, wax=[152, 34, 24], tex=0.07, contact=0.42, contact_px=3.5, contact_off=[3.0, 4.5],
              flash_s=0.24, relief_flash=0.7, spec_flash=1.2, ring_press=0.34, ring_settle=0.07, ring_s=0.42, press_w=0.42,
              shock=0.22, shock_v=260.0, shock_w=7.0, shock_s=0.2, drops=7, drop_r=[1.04, 1.42], drop_px=[2.6, 6.5], drip_len=[1.5, 3.0],
              drop_spread=0.5, spatter=7, spatter_r=[1.55, 2.35], spatter_px=[0.9, 2.3], spatter_spread=0.9, fly_v=1500.0, fall_fade=0.35)
    def _wax_init(s, q, r):
        H, W = s.H, s.W; x, y = q["xy"]; R = q["radius"]; Rb = R * q["blob"]
        ext = int(max(R * q["spatter_r"][1] * 1.06 + q["spatter_px"][1] * 3, Rb * q["ghost_scale"] * 1.12 + q["ghost_blur"] * 3) + max(q["shadow_off"]) + q["shadow_sigma"][0] * 3 + 10)
        xa, xb, ya, yb = max(0, int(x) - ext), min(W, int(x) + ext + 1), max(0, int(y) - ext), min(H, int(y) + ext + 1)
        h, w = yb - ya, xb - xa; ss = 4; c = ((x - xa) * ss, (y - ya) * ss); rot = math.radians(q["rot_deg"])
        def P(px, py): return (int(round(px * 16)), int(round(py * 16)))
        def C(px, py): return P(c[0] + px * ss, c[1] + py * ss)
        def down(cn): return cv2.resize(cn, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        phi = float(r.uniform(0, 2 * math.pi))
        # irregular wax blob, bulging on the heavy-pressure side
        hp = [(k, float(r.uniform(0, 2 * math.pi)), float(r.normal(0, 1))) for k in (2, 3, 5, 7)]
        pts = []
        for i in range(160):
            th = 2 * math.pi * i / 160; n = sum(a / k * math.cos(k * th + p_) for k, p_, a in hp) / 1.2
            rr = Rb * (1 + q["blob_var"] * n + q["bulge"] * max(0.0, math.cos(th - phi)) ** 2); pts.append(C(math.cos(th) * rr, math.sin(th) * rr))
        cb = np.zeros((h * ss, w * ss), np.uint8); cv2.fillPoly(cb, [np.int32(pts)], 255, cv2.LINE_AA, shift=4)
        Bm = down(cb)
        de = cv2.distanceTransform((cb > 127).astype(np.uint8), cv2.DIST_L2, 5)
        de = cv2.resize(de, (w, h), interpolation=cv2.INTER_AREA) / ss
        hb = 1 - (1 - np.clip(de / (R * q["edge_round"]), 0, 1)) ** 2
        yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
        fld = 1 - smoothstep(R * 0.97, R * 1.03, d)
        Hh = hb + q["lip"] * np.exp(-((d - R * 1.06) / (R * q["lip_w"])) ** 2) * hb - q["depth"] * fld
        # matrix design (intaglio matrix -> raised on the wax): beaded border, inner fillet, Tudor double rose
        def layer(): return np.zeros((h * ss, w * ss), np.uint8)
        L1 = layer()
        for i in range(q["beads"]):
            th = rot + 2 * math.pi * i / q["beads"]; cv2.circle(L1, C(math.cos(th) * R * q["bead_r"], math.sin(th) * R * q["bead_r"]), int(q["bead_px"] * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        cv2.circle(L1, C(0, 0), int(R * q["ring2"] * ss * 16), 255, max(1, int(q["ring2_w"] * ss)), cv2.LINE_AA, shift=4)
        Rr = R * q["design_r"]; Lo, Li, Lc = layer(), layer(), layer()
        for i in range(5):                                                                # sepals / barbs between the outer petals
            th = rot - math.pi / 2 + 2 * math.pi * (i + 0.5) / 5; tip = Rr * 1.06; bs = Rr * 0.6; wd = 0.2
            tri = [C(math.cos(th) * tip, math.sin(th) * tip), C(math.cos(th - wd) * bs, math.sin(th - wd) * bs), C(math.cos(th + wd) * bs, math.sin(th + wd) * bs)]
            cv2.fillPoly(Lo, [np.int32(tri)], 255, cv2.LINE_AA, shift=4)
        for i in range(5):
            th = rot - math.pi / 2 + 2 * math.pi * i / 5; cv2.circle(Lo, C(math.cos(th) * Rr * 0.5, math.sin(th) * Rr * 0.5), int(Rr * 0.42 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        for i in range(5):
            th = rot - math.pi / 2 + 2 * math.pi * (i + 0.5) / 5; ctr = C(math.cos(th) * Rr * 0.26, math.sin(th) * Rr * 0.26)
            cv2.circle(Li, ctr, int(Rr * 0.25 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
            cv2.circle(Lo, ctr, int(Rr * 0.25 * ss * 16), 0, max(1, int(1.6 * ss)), cv2.LINE_AA, shift=4)   # groove separating the petal rows
        cv2.circle(Lc, C(0, 0), int(Rr * 0.15 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        cv2.circle(Li, C(0, 0), int(Rr * 0.15 * ss * 16), 0, max(1, int(1.4 * ss)), cv2.LINE_AA, shift=4)
        for i in range(8):
            th = rot + 2 * math.pi * i / 8; cv2.circle(Lc, C(math.cos(th) * Rr * 0.22, math.sin(th) * Rr * 0.22), int(1.3 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        def dome(m, sg): return cv2.GaussianBlur(m, (0, 0), sg) * m
        m1, mo, mi, mc = down(L1), down(Lo), down(Li), down(Lc)
        Hd = 0.42 * dome(m1, 0.9) + 0.36 * dome(mo, 2.2) + 0.32 * dome(mi, 1.8) + 0.3 * dome(mc, 1.0)
        Hh = cv2.GaussianBlur(Hh + Hd * fld * 1.1, (0, 0), 0.7)
        Lv = np.float32(q["light"]); Lv /= np.linalg.norm(Lv); Hv = Lv + np.float32([0, 0, 1]); Hv /= np.linalg.norm(Hv)
        def shade(Hm, k):
            gx = cv2.Sobel(Hm, cv2.CV_32F, 1, 0, ksize=3) / 8 * k; gy = cv2.Sobel(Hm, cv2.CV_32F, 0, 1, ksize=3) / 8 * k
            nn = np.sqrt(gx * gx + gy * gy + 1); nx, ny, nz = -gx / nn, -gy / nn, 1 / nn
            dif = np.clip(nx * Lv[0] + ny * Lv[1] + nz * Lv[2], 0, 1); sd = q["amb"] + (1 - q["amb"]) * dif / Lv[2]
            sp = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** q["spec_pow"]; sp0 = Hv[2] ** q["spec_pow"]
            return (sd - 1).astype(np.float32), np.clip(sp - sp0, 0, 1).astype(np.float32)
        Sd, Sp = shade(Hh * R * 0.12, q["relief"])
        tex = pnoise(r, h, w, max(5.0, R * 0.2), 1.0); tex = (1 + q["tex"] * tex).astype(np.float32)
        # splat: wet wax drops (teardrops pointing outward) on the pressure side + far spatter that lands slightly later
        bins = [layer() for _ in range(3)]; tbins = [0.0, 0.0, 0.0]
        for i in range(q["drops"] + q["spatter"]):
            sp_ = i >= q["drops"]
            th = phi + r.normal(0, q["spatter_spread"] if sp_ else q["drop_spread"]); u_ = r.uniform(0, 1)
            lo_, hi_ = q["spatter_r"] if sp_ else q["drop_r"]; dd = Rb * (lo_ + (hi_ - lo_) * u_ ** 1.4)
            pl, ph_ = q["spatter_px"] if sp_ else q["drop_px"]; sz = pl + (ph_ - pl) * r.uniform(0, 1) ** 1.8
            el = 1.0 if sp_ else float(r.uniform(*q["drip_len"])); dly = max(0.0, dd - Rb) / q["fly_v"]
            bi = 0 if dly < 0.03 else (1 if dly < 0.07 else 2); tbins[bi] = max(tbins[bi], dly)
            cx_, cy_ = math.cos(th) * dd, math.sin(th) * dd
            cv2.ellipse(bins[bi], C(cx_, cy_), (int(sz * el * ss * 16), int(sz * ss * 16)), math.degrees(th), 0, 360, 255, -1, cv2.LINE_AA, shift=4)
            if not sp_ and el > 2.0:                                                      # a thin neck back toward the blob
                cv2.line(bins[bi], C(math.cos(th) * (dd - sz * el), math.sin(th) * (dd - sz * el)), C(math.cos(th) * Rb * 0.98, math.sin(th) * Rb * 0.98), 255, max(1, int(sz * 0.55 * ss)), cv2.LINE_AA, shift=4)
        Db = [down(b_) * (1 - Bm) for b_ in bins]; Dall = np.clip(sum(Db), 0, 1)
        Sdd, Spd = shade(dome(Dall, 1.6) * 6.0, 1.4)
        dout = cv2.distanceTransform((cb <= 127).astype(np.uint8), cv2.DIST_L2, 5); dout = cv2.resize(dout, (w, h), interpolation=cv2.INTER_AREA) / ss
        ring = (np.exp(-(dout / (R * q["press_w"])) ** 1.5) * (1 - Bm)).astype(np.float32)
        sil = cv2.GaussianBlur(Bm, (0, 0), 1.0)
        return dict(wax=True, q=q, bb=(xa, ya, xb, yb), c=(x - xa, y - ya), Bm=Bm, Sd=Sd, Sp=Sp, tex=tex, Db=Db, tb=tbins, Sdd=Sdd, Spd=Spd,
                    ring=ring, dout=dout.astype(np.float32), sil=sil, lm=s.m[ya:yb, xa:xb])
    def _wax(s, img, S, t):
        q = S["q"]; xa, ya, xb, yb = S["bb"]; roi = img[ya:yb, xa:xb]; lm = S["lm"]; age = t - q["t_on"]; k_ = s.k
        if age < -q["drop_s"]: return
        wax = np.float32(q["wax"]); spc = np.float32([255, 236, 220])
        def rgb(Sd, Sp, kr, gl): return np.clip(wax * (1 + Sd * kr)[..., None] * S["tex"][..., None] + spc * (Sp * gl)[..., None], 0, 255)
        if age < 0:                                                                       # descent: seal scales down from larger toward its spot, shadow converges
            u = 1 + age / q["drop_s"]; hgt = 1 - u * u
            ox, oy = q["shadow_off"]; sg = q["shadow_sigma"][1] + (q["shadow_sigma"][0] - q["shadow_sigma"][1]) * hgt
            sh = cv2.GaussianBlur(s._warp(S["sil"], S["c"], 1 + 0.12 * hgt, ox * hgt, oy * hgt), (0, 0), sg)
            sh = np.clip(sh / (sh.max() + 1e-6), 0, 1) * q["shadow"] * (0.3 + 0.7 * u) * lm * k_
            roi *= 1 - sh[..., None] * np.float32([0.85, 0.9, 1.0])
            sc = 1 + (q["ghost_scale"] - 1) * hgt; bl = q["ghost_blur"] * hgt
            A = s._warp(S["Bm"], S["c"], sc); col = rgb(s._warp(S["Sd"], S["c"], sc), s._warp(S["Sp"], S["c"], sc), 1.0, q["spec"])
            if bl > 0.3: A = cv2.GaussianBlur(A, (0, 0), bl); col = cv2.GaussianBlur(col, (0, 0), bl)
            a = (A * min(1.0, u / q["fall_fade"]) * q["opacity"] * lm * k_)[..., None]
            roi[...] = roi * (1 - a) + col * a; return
        fl = math.exp(-age / q["flash_s"]); wet = math.exp(-age / s.ink["dry_time"])
        pr = q["ring_settle"] + (q["ring_press"] - q["ring_settle"]) * math.exp(-age / q["ring_s"])
        shk = q["shock"] * math.exp(-age / q["shock_s"]) * np.exp(-((S["dout"] - q["shock_v"] * age) / q["shock_w"]) ** 2) * (1 - S["Bm"])
        cs = cv2.GaussianBlur(s._warp(S["Bm"], S["c"], 1.0, *q["contact_off"]), (0, 0), q["contact_px"]) * (1 - S["Bm"]) * q["contact"]
        dk = np.clip(S["ring"] * pr + shk + cs, 0, 0.9) * lm * k_
        roi *= 1 - dk[..., None] * np.float32([0.9, 0.94, 1.0])
        gl = (q["gloss_dry"] + (q["gloss_wet"] - q["gloss_dry"]) * math.exp(-age / q["gloss_s"])) * q["spec"] * (1 + q["spec_flash"] * fl)
        for Dm, tb in zip(S["Db"], S["tb"]):
            v = min(1.0, max(0.0, (age - tb) / 0.035))
            if v <= 0: continue
            a = (Dm * v * q["opacity"] * lm * k_)[..., None]; col = rgb(S["Sdd"], S["Spd"], 1.0, gl * (0.6 + 0.6 * wet))
            roi[...] = roi * (1 - a) + col * a
        a = (S["Bm"] * q["opacity"] * lm * k_)[..., None]; col = rgb(S["Sd"], S["Sp"], 1 + q["relief_flash"] * fl, gl)
        roi[...] = roi * (1 - a) + col * a
    # ---------------------------------------------------------------- b8: story-specific icon stamp (stamps[].style = "icon", opt-in)
    # Same landing motion as the b6 wax stamp (falling ghost from ghost_scale, blur, converging shadow, press ring + shock, no bounce);
    # the impression is a procedural engraved + hand-tinted map icon: sword | crossed_swords | anchor | crown | skull.
    IX = dict(icon="sword", radius=70.0, rot_deg=0.0, drop_s=0.42, ghost_scale=1.3, ghost_blur=5.0, shadow=0.5, shadow_off=[26.0, 34.0], shadow_sigma=[20.0, 3.5],
              fall_fade=0.35, opacity=1.0, contact=0.32, contact_px=3.5, contact_off=[3.0, 4.5], ring_press=0.34, ring_settle=0.07, ring_s=0.42, press_w=0.42,
              shock=0.22, shock_v=260.0, shock_w=7.0, shock_s=0.2, line=[38, 24, 12], line_wet=[14, 8, 4], line_w=2.4, inner_w=1.5, hatch_px=3.4, hatch_w=1.1,
              hatch_frac=0.8, line_op=0.92, pigment=0.6, dry_break=0.25, fill_op=0.9, wet_dark=0.12, dry_time=0.9, palette={},
              spatter=6, spatter_r=[1.05, 1.5], spatter_px=[0.8, 2.0], spatter_spread=0.9, fly_v=1500.0)
    PAL = dict(steel=[214, 208, 190], gold=[198, 154, 62], hilt=[132, 44, 30], iron=[112, 102, 88], wood=[128, 88, 52], bone=[232, 218, 184], red=[152, 36, 30],
               pearl=[240, 232, 212], blue=[52, 72, 132])
    @staticmethod
    def _icon_parts(kind):
        def sword(T=lambda x, y: (x, y)):
            def tp(pts): return [T(*p_) for p_ in pts]
            P = []
            P.append(dict(col="steel", fill=[("poly", tp([(0, 1.0), (0.11, 0.80), (0.115, -0.30), (-0.115, -0.30), (-0.11, 0.80)]))],
                          lines=[(tp([(0, -0.27), (0, 0.66)]), 1.0)]))
            P.append(dict(col="gold", fill=[("poly", tp([(-0.44, -0.29), (0.44, -0.29), (0.47, -0.38), (-0.47, -0.38)])),
                                            ("circle", T(-0.49, -0.335), 0.065), ("circle", T(0.49, -0.335), 0.065)], lines=[]))
            P.append(dict(col="hilt", fill=[("poly", tp([(-0.062, -0.38), (0.062, -0.38), (0.056, -0.71), (-0.056, -0.71)]))],
                          lines=[(tp([(-0.056, y_), (0.056, y_ - 0.045)]), 0.8) for y_ in np.arange(-0.42, -0.69, -0.055)]))
            P.append(dict(col="gold", fill=[("circle", T(0, -0.79), 0.09)], lines=[]))
            return P
        def rot(a, s_=1.0, dy=0.0):
            c_, s2 = math.cos(a), math.sin(a)
            return lambda x, y: ((x * c_ - (y + dy) * s2) * s_, (x * s2 + (y + dy) * c_) * s_)
        if kind == "sword": return sword()
        if kind == "crossed_swords": return sword(rot(math.radians(140), 0.95, -0.12)) + sword(rot(math.radians(-140), 0.95, -0.12))   # hilts low, blades crossing above
        if kind == "anchor":
            arc = [(0.6 * math.cos(th), 0.24 + 0.6 * math.sin(th)) for th in np.linspace(0.13 * math.pi, 0.87 * math.pi, 40)]
            fl = []
            for sg in (1, -1):
                th = 0.13 * math.pi if sg == 1 else 0.87 * math.pi; ex, ey = 0.6 * math.cos(th), 0.24 + 0.6 * math.sin(th)
                tg = (math.sin(th), -math.cos(th)) if sg == 1 else (-math.sin(th), math.cos(th)); nr = (math.cos(th), math.sin(th))
                fl.append(("poly", [(ex + tg[0] * 0.27, ey + tg[1] * 0.27), (ex + nr[0] * 0.16 - tg[0] * 0.05, ey + nr[1] * 0.16 - tg[1] * 0.05),
                                    (ex - nr[0] * 0.12 - tg[0] * 0.05, ey - nr[1] * 0.12 - tg[1] * 0.05)]))
            return [dict(col="iron", fill=[("ring", (0, -0.80), 0.14, 0.06)], lines=[]),
                    dict(col="iron", fill=[("poly", [(-0.062, -0.68), (0.062, -0.68), (0.078, 0.80), (-0.078, 0.80)])], lines=[]),
                    dict(col="iron", fill=[("stroke", arc, 0.115)] + fl + [("circle", (0, 0.86), 0.075)], lines=[]),
                    dict(col="wood", fill=[("poly", [(-0.44, -0.62), (0.44, -0.62), (0.44, -0.52), (-0.44, -0.52)]), ("circle", (-0.46, -0.57), 0.065), ("circle", (0.46, -0.57), 0.065)],
                         lines=[([(-0.38, -0.57), (0.38, -0.57)], 0.6)])]
        if kind == "crown":
            xs = [-0.72, -0.36, 0.0, 0.36, 0.72]; ty = [-0.36, -0.52, -0.72, -0.52, -0.36]; vx = [-0.54, -0.18, 0.18, 0.54]; vy = [-0.02, -0.12, -0.12, -0.02]
            top = []
            for i in range(5):
                top.append((xs[i], ty[i]))
                if i < 4: top.append((vx[i], vy[i]))
            body = [(-0.62, 0.30)] + top + [(0.62, 0.30)]
            band = [(-0.66 + 1.32 * u, 0.22 + 0.06 * (2 * u - 1) ** 2) for u in np.linspace(0, 1, 20)] + [(0.66 - 1.32 * u, 0.52 + 0.06 * (1 - 2 * u) ** 2) for u in np.linspace(0, 1, 20)]
            return [dict(col="gold", fill=[("poly", body)], lines=[([(0, -0.62), (0, 0.18)], 0.6)]),
                    dict(col="red", fill=[("ellipse", (0, -0.24), (0.075, 0.11), 0)], lines=[]),
                    dict(col="pearl", fill=[("circle", (x_, y_ - 0.06), 0.075) for x_, y_ in zip(xs, ty)], lines=[]),
                    dict(col="gold", fill=[("poly", band)], lines=[]),
                    dict(col="red", fill=[("circle", (x_, 0.37 + 0.06 * x_ * x_), 0.07) for x_ in (-0.4, 0.4)] + [("poly", [(0, 0.27), (0.08, 0.37), (0, 0.47), (-0.08, 0.37)])], lines=[])]
        if kind == "skull":
            face = [(-0.46, 0.08), (-0.38, 0.46), (-0.26, 0.60), (0.26, 0.60), (0.38, 0.46), (0.46, 0.08)]
            return [dict(col="bone", fill=[("ellipse", (0, -0.20), (0.62, 0.60), 0), ("poly", face)],
                         lines=[([(-0.06, -0.78), (0.01, -0.64), (-0.05, -0.52)], 0.7)],
                         dark=[("ellipse", (-0.25, 0.04), (0.17, 0.145), 12), ("ellipse", (0.25, 0.04), (0.17, 0.145), -12), ("poly", [(0, 0.22), (-0.075, 0.38), (0.075, 0.38)])]),
                    dict(col="bone", fill=[("poly", [(-0.30, 0.54), (0.30, 0.54), (0.27, 0.80), (0.16, 0.88), (-0.16, 0.88), (-0.27, 0.80)])],
                         lines=[([(-0.27, 0.66), (0.27, 0.66)], 0.8)] + [([(x_, 0.56), (x_, 0.76)], 0.7) for x_ in (-0.18, -0.09, 0.0, 0.09, 0.18)])]
        raise ValueError(f"unknown icon {kind}")
    def _icon_init(s, q, r):
        H, W = s.H, s.W; x, y = q["xy"]; R = q["radius"]
        ext = int(R * q["ghost_scale"] * 1.15 + q["ghost_blur"] * 3 + max(q["shadow_off"]) + q["shadow_sigma"][0] * 3 + R * q["spatter_r"][1] * 0.3 + 10)
        xa, xb, ya, yb = max(0, int(x) - ext), min(W, int(x) + ext + 1), max(0, int(y) - ext), min(H, int(y) + ext + 1)
        h, w = yb - ya, xb - xa; ss = 4; c = ((x - xa) * ss, (y - ya) * ss); rot = math.radians(q["rot_deg"]); cr, sr = math.cos(rot), math.sin(rot)
        pal = {**s.PAL, **q["palette"]}
        def U(px, py): return (c[0] + (px * cr - py * sr) * R * ss, c[1] + (px * sr + py * cr) * R * ss)
        def P(pt): return (int(round(pt[0] * 16)), int(round(pt[1] * 16)))
        def draw(m, op, val=255):
            k = op[0]
            if k == "poly": cv2.fillPoly(m, [np.int32([P(U(*p_)) for p_ in op[1]])], val, cv2.LINE_AA, shift=4)
            elif k == "circle": cv2.circle(m, P(U(*op[1])), int(op[2] * R * ss * 16), val, -1, cv2.LINE_AA, shift=4)
            elif k == "ring": cv2.circle(m, P(U(*op[1])), int(op[2] * R * ss * 16), val, max(1, int(op[3] * R * ss)), cv2.LINE_AA, shift=4)
            elif k == "ellipse":
                cv2.ellipse(m, P(U(*op[1])), (int(op[2][0] * R * ss * 16), int(op[2][1] * R * ss * 16)), q["rot_deg"] + op[3], 0, 360, val, -1, cv2.LINE_AA, shift=4)
            elif k == "stroke": cv2.polylines(m, [np.int32([P(U(*p_)) for p_ in op[1]])], False, val, max(1, int(op[2] * R * ss)), cv2.LINE_AA, shift=4)
        HS, WS = h * ss, w * ss
        fA = np.zeros((HS, WS), np.float32); fC = np.zeros((HS, WS, 3), np.float32); lA = np.zeros((HS, WS), np.float32)
        yy, xx = np.mgrid[0:HS, 0:WS].astype(np.float32)
        hp = q["hatch_px"] * ss; hat = (np.abs(((xx - yy) / math.sqrt(2)) % hp - hp / 2) < q["hatch_w"] * ss / 2).astype(np.float32)
        lw = max(1, int(q["line_w"] * ss)); ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * lw + 1, 2 * lw + 1))
        Lv = (-0.7071, -0.7071)                                                                   # light from the upper left; engraved hatching on the lower-right side
        for part in s._icon_parts(q["icon"]):
            pm = np.zeros((HS, WS), np.uint8)
            for op in part["fill"]: draw(pm, op)
            pb = (pm > 127).astype(np.uint8)
            if not pb.any(): continue
            de = cv2.distanceTransform(pb, cv2.DIST_L2, 5); dl = max(2.0, float(de.max()) * 2 * q["hatch_frac"])
            M = np.float32([[1, 0, Lv[0] * dl], [0, 1, Lv[1] * dl]])
            band = pb * (1 - cv2.warpAffine(pb, M, (WS, HS)))                                   # inside, but not inside when shifted from the light
            band = band.astype(np.float32) * np.clip(de / (dl * 0.25 + 1e-6), 0, 1)
            pmf = pm.astype(np.float32) / 255.0
            outl = np.clip(pmf - cv2.erode(pmf, ker), 0, 1)
            inner = np.zeros((HS, WS), np.uint8)
            for pts, wf in part.get("lines", []): cv2.polylines(inner, [np.int32([P(U(*p_)) for p_ in pts])], False, 255, max(1, int(q["inner_w"] * wf * ss)), cv2.LINE_AA, shift=4)
            dk = np.zeros((HS, WS), np.uint8)
            for op in part.get("dark", []): draw(dk, op)
            lp = np.clip(outl + inner.astype(np.float32) / 255.0 * pmf + hat * band * 0.85 + dk.astype(np.float32) / 255.0, 0, 1)
            col = np.float32(pal[part["col"]])
            fC = fC * (1 - pmf[..., None]) + col * pmf[..., None]; fA = np.maximum(fA, pmf)
            lA = lA * (1 - pmf) + lp
        def down(z): return cv2.resize(z, (w, h), interpolation=cv2.INTER_AREA)
        fA, fC, lA = down(fA), down(fC), np.clip(down(lA), 0, 1)
        fC = fC / np.maximum(fA[..., None], 1e-4)
        brk = np.clip(1 - q["dry_break"] * np.clip(pnoise(r, h, w, 2.2, 0.7), 0, None) * 1.6, 0.3, 1).astype(np.float32)   # dry-brush skips in the lines
        gran = np.clip(1 - 0.12 * (0.5 + 0.5 * pnoise(r, h, w, 4.0, 0.8)), 0, 1).astype(np.float32)                         # wash granulation
        Bm = np.clip(fA, 0, 1).astype(np.float32)
        dout = cv2.distanceTransform((Bm < 0.5).astype(np.uint8), cv2.DIST_L2, 5).astype(np.float32)
        ring = (np.exp(-(dout / (R * q["press_w"])) ** 1.5) * (1 - Bm)).astype(np.float32)
        phi = float(r.uniform(0, 2 * math.pi)); sp_ = np.zeros((h * ss, w * ss), np.uint8); dl_ = []
        for i in range(q["spatter"]):
            th = phi + r.normal(0, q["spatter_spread"]); u_ = r.uniform(0, 1); dd = R * (q["spatter_r"][0] + (q["spatter_r"][1] - q["spatter_r"][0]) * u_)
            sz = q["spatter_px"][0] + (q["spatter_px"][1] - q["spatter_px"][0]) * r.uniform(0, 1) ** 1.8
            cv2.circle(sp_, P((c[0] + math.cos(th) * dd * ss, c[1] + math.sin(th) * dd * ss)), int(sz * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        Sp = (down(sp_.astype(np.float32) / 255.0) * (1 - Bm)).astype(np.float32)
        sil = cv2.GaussianBlur(np.maximum(Bm, lA), (0, 0), 1.0)
        return dict(icon=True, q=q, bb=(xa, ya, xb, yb), c=(x - xa, y - ya), Bm=Bm, fC=fC.astype(np.float32), lA=(lA * brk).astype(np.float32), gran=gran, Sp=Sp,
                    ring=ring, dout=dout, sil=sil.astype(np.float32), lm=s.m[ya:yb, xa:xb], tsp=R * (q["spatter_r"][0] - 1 + 0.2) / q["fly_v"])
    def _icon_paint(s, roi, q, Bm, fC, lA, gran, wet, a_mul):
        Y = 0.299 * roi[..., 0] + 0.587 * roi[..., 1] + 0.114 * roi[..., 2]; Ym = float(Y.mean()) + 1e-3
        tex = np.clip(0.8 + 0.2 * Y / Ym, 0.6, 1.2)[..., None]                                     # paper tooth shows through the wash
        fa = (Bm * q["fill_op"] * gran * a_mul)[..., None]
        roi[...] = roi * (1 - fa) + fC * tex * (1 - q["wet_dark"] * wet) * fa
        lc = (np.float32(q["line"]) * (1 - wet) + np.float32(q["line_wet"]) * wet) / 255.0; k = q["pigment"]
        la = (lA * q["line_op"] * a_mul)[..., None]
        roi[...] = roi * (1 - la) + (roi * lc * (1 - k) + lc * 255.0 * k) * la
    def _icon(s, img, S, t):
        q = S["q"]; xa, ya, xb, yb = S["bb"]; roi = img[ya:yb, xa:xb]; lm = S["lm"]; age = t - q["t_on"]; k_ = s.k
        if age < -q["drop_s"]: return
        if age < 0:                                                                       # descent: identical to the b6 wax stamp
            u = 1 + age / q["drop_s"]; hgt = 1 - u * u
            ox, oy = q["shadow_off"]; sg = q["shadow_sigma"][1] + (q["shadow_sigma"][0] - q["shadow_sigma"][1]) * hgt
            sh = cv2.GaussianBlur(s._warp(S["sil"], S["c"], 1 + 0.12 * hgt, ox * hgt, oy * hgt), (0, 0), sg)
            sh = np.clip(sh / (sh.max() + 1e-6), 0, 1) * q["shadow"] * (0.3 + 0.7 * u) * lm * k_
            roi *= 1 - sh[..., None] * np.float32([0.85, 0.9, 1.0])
            sc = 1 + (q["ghost_scale"] - 1) * hgt; bl = q["ghost_blur"] * hgt
            Bm, lA, fC, gr = (s._warp(S[k], S["c"], sc) for k in ("Bm", "lA", "fC", "gran"))
            if bl > 0.3:
                fP = cv2.GaussianBlur(fC * Bm[..., None], (0, 0), bl); Bm, lA = cv2.GaussianBlur(Bm, (0, 0), bl), cv2.GaussianBlur(lA, (0, 0), bl)
                fC = fP / np.maximum(Bm[..., None], 1e-4)
            s._icon_paint(roi, q, Bm, fC, lA, gr, 1.0, min(1.0, u / q["fall_fade"]) * q["opacity"] * lm * k_); return
        wet = math.exp(-age / q["dry_time"])
        pr = q["ring_settle"] + (q["ring_press"] - q["ring_settle"]) * math.exp(-age / q["ring_s"])
        shk = q["shock"] * math.exp(-age / q["shock_s"]) * np.exp(-((S["dout"] - q["shock_v"] * age) / q["shock_w"]) ** 2) * (1 - S["Bm"])
        cs = cv2.GaussianBlur(s._warp(S["Bm"], S["c"], 1.0, *q["contact_off"]), (0, 0), q["contact_px"]) * (1 - S["Bm"]) * q["contact"]
        dk = np.clip(S["ring"] * pr + shk + cs, 0, 0.9) * lm * k_
        roi *= 1 - dk[..., None] * np.float32([0.9, 0.94, 1.0])
        if age >= S["tsp"]:
            v = min(1.0, (age - S["tsp"]) / 0.035); lc = np.float32(q["line_wet"]) / 255.0
            a = (S["Sp"] * v * q["line_op"] * lm * k_)[..., None]; roi[...] = roi * (1 - a) + roi * lc * a
        s._icon_paint(roi, q, S["Bm"], S["fC"], S["lA"], S["gran"], wet, q["opacity"] * lm * k_)
    # ---------------------------------------------------------------- b6: soft area-of-influence wash (washes[].reach_frac, opt-in; no border line)
    SW = dict(reach_at=None, reach_frac=1.1, feather_frac=0.35, aniso=[0.0, 0.0], cov=[[0.3, 0.0], [1.0, 0.5], [2.0, 0.76], [3.0, 0.92], [3.6, 1.0]],
              cov_weight_sat=0.5, color=[176, 52, 104], wet_color=[110, 20, 62], opacity=0.5, wet_opacity=0.3, edge=0.55, edge_px=6.0, front_s=0.35,
              gran=0.3, gran_px=2.5, gran2=0.15, gran2_px=9.0, yref=150.0, ygamma=1.0, wet_time=0.7)
    def _swash_init(s, q, r):
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import dijkstra
        H, W = s.H, s.W; M = load_mask(q["mask"], (H, W)) * s.m; st = int(q["step"])
        h, w = (H + st - 1) // st, (W + st - 1) // st
        Ms = cv2.resize(M, (w, h), interpolation=cv2.INTER_AREA) > float(q.get("geo_thresh", 0.35))
        nz = pnoise(r, h, w, q["finger_lo"] / st, 1.5); spd = np.exp(q["finger"] * nz).astype(np.float64)
        sx, sy = q["seed"]; gy_, gx_ = np.mgrid[0:h, 0:w].astype(np.float64)
        th0, ka = math.radians(q["aniso"][0]), q["aniso"][1]
        ang = np.arctan2(gy_ * st - sy, gx_ * st - sx); kb = q["aniso"][2] if len(q["aniso"]) > 2 else 0.0
        spd = spd * (1 + ka * np.clip(np.cos(ang - th0), 0, 1) ** 2) / (1 + kb * np.clip(-np.cos(ang - th0), 0, 1) ** 2)
        idx = -np.ones((h, w), np.int64); ys, xs = np.nonzero(Ms); idx[ys, xs] = np.arange(len(ys))
        rows, cols, vals = [], [], []
        for dy_, dx_, ln in ((0, 1, 1.0), (1, 0, 1.0), (1, 1, 1.4142), (1, -1, 1.4142)):
            y2, x2 = ys + dy_, xs + dx_; ok = (y2 < h) & (x2 >= 0) & (x2 < w); ok[ok] = Ms[y2[ok], x2[ok]]
            a_, b_ = idx[ys[ok], xs[ok]], idx[y2[ok], x2[ok]]; cst = ln * st * 0.5 * (1 / spd[ys[ok], xs[ok]] + 1 / spd[y2[ok], x2[ok]])
            rows += [a_, b_]; cols += [b_, a_]; vals += [cst, cst]
        G = coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(len(ys),) * 2).tocsr()
        sx_, sy_ = int(sx // st), int(sy // st)
        k0 = int(idx[sy_, sx_]) if Ms[sy_, sx_] else int(np.argmin((ys - sy_) ** 2 + (xs - sx_) ** 2))
        dist = dijkstra(G, indices=k0)
        ax_, ay_ = q["reach_at"] or q["seed"]; ka_ = int(np.argmin((ys - ay_ // st) ** 2 + (xs - ax_ // st) ** 2)); dref = float(dist[ka_])
        reach = dref * q["reach_frac"]; fe = reach * q["feather_frac"]
        fin = np.isfinite(dist); dist = np.where(fin, dist, reach * 9)
        Sa_n = 1 - smoothstep(reach - fe, reach + fe, dist)
        wgt = np.clip(Sa_n / q["cov_weight_sat"], 0, 1) * (Sa_n > 0.01)
        order = np.argsort(dist, kind="stable"); cw = np.cumsum(wgt[order]); cw /= max(cw[-1], 1e-9)
        Qn = np.empty_like(cw); Qn[order] = cw
        ct = np.float64([c_[0] for c_ in q["cov"]]); cc = np.float64([c_[1] for c_ in q["cov"]])
        tn = np.interp(Qn, cc, ct); tn[Sa_n <= 0.01] = 1e3
        def up(v, fill):
            g = np.full((h, w), fill, np.float32); g[ys, xs] = v; g = cv2.GaussianBlur(g, (0, 0), 0.8)
            return cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
        tA = up(np.minimum(tn, ct[-1] + 0.6), ct[-1] + 0.6); Sa = np.clip(up(Sa_n, 0.0), 0, 1) * M
        tA[Sa <= 0.005] = 1e3
        ys_, xs_ = np.nonzero(Sa > 0.005); x0, y0, x1, y1 = int(xs_.min()), int(ys_.min()), int(xs_.max()) + 1, int(ys_.max()) + 1
        tb = tA[y0:y1, x0:x1]; tcl = np.where(tb < 100, tb, ct[-1] + 0.6).astype(np.float32)
        gx = cv2.Sobel(tcl, cv2.CV_32F, 1, 0, ksize=3) / 8; gy = cv2.Sobel(tcl, cv2.CV_32F, 0, 1, ksize=3) / 8
        dtE = np.clip(np.sqrt(gx * gx + gy * gy) * q["edge_px"], 0.025, 0.6).astype(np.float32)
        hh, ww = y1 - y0, x1 - x0
        gran = (1 - q["gran"] * np.clip(0.5 + 0.5 * pnoise(r, hh, ww, q["gran_px"], 0.7), 0, 1) - q["gran2"] * np.clip(0.5 + 0.5 * pnoise(r, hh, ww, q["gran2_px"], 2.0), 0, 1)).astype(np.float32)
        return dict(soft=True, q=q, bb=(x0, y0, x1, y1), tA=tb.astype(np.float32), dtE=dtE, Sa=Sa[y0:y1, x0:x1].astype(np.float32), M=Sa[y0:y1, x0:x1].astype(np.float32), gran=gran,
                    dref=dref, reach=reach)
    def _swash(s, img, Wd, t):
        q = Wd["q"]
        if t < q["cov"][0][0]: return
        x0, y0, x1, y1 = Wd["bb"]; roi = img[y0:y1, x0:x1]; dt = t - Wd["tA"]
        xe = dt / Wd["dtE"]
        front = smoothstep(-0.15, 0.1, xe) * (1 - smoothstep(0.1, 1.0, xe)) * q["edge"]                    # thin dark pooled crest at the front
        fill = smoothstep(0.0, q["front_s"], dt); wet = np.exp(-np.maximum(dt, 0) / q["wet_time"]) * (dt > 0)
        op = q["opacity"] + (q["wet_opacity"] - q["opacity"]) * wet                                          # lighter while wet, settles darker as it dries
        g = Wd["gran"]; gs = 1 + (g - 1) * (0.4 + 0.6 * (1 - wet))                                             # granulation develops as it dries
        a_i = fill * op * gs; a = np.clip((a_i + front) * Wd["Sa"] * s.k, 0, 1)
        wmix = np.clip(front / (a_i + front + 1e-4), 0, 1)[..., None]
        col = np.float32(q["color"]) * (1 - wmix) + np.float32(q["wet_color"]) * wmix
        Y = (0.299 * roi[..., 0] + 0.587 * roi[..., 1] + 0.114 * roi[..., 2])[..., None]
        tint = col * (Y / q["yref"]) ** q["ygamma"]                                                           # colour-of-wash x local relief luminance (relief stays visible)
        roi[...] = roi * (1 - a[..., None]) + tint * a[..., None]
    def overlay(s, img, t):
        for Wd in s.washes: s._wash(img, Wd, t)
        for S in s.stamps: s._stamp(img, S, t)
    def allow(s):
        a = np.zeros((s.H, s.W), bool)
        for S in s.stamps: xa, ya, xb, yb = S["bb"]; a[ya:yb, xa:xb] |= S["lm"] > 1e-4
        for Wd in s.washes: x0, y0, x1, y1 = Wd["bb"]; a[y0:y1, x0:x1] |= Wd["M"] > 1e-4
        return a

PRESETS = {"water-glint": WaterGlint, "water": Water, "map-light": MapLight, "sky": Sky, "atmos": Atmos, "smoke": Smoke, "fire-torchlight": FireTorch, "foliage": Foliage, "light-shift": LightShift, "map-ink": MapInk}

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
