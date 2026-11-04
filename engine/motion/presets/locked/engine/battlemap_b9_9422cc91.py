#!/usr/bin/env python3
"""Posterity battle-map renderer (b9).  Static painted plate (never remapped: land 0 px) + procedural overlays in plate space:
painterly unit blocks with banners, hatched stake lines, inked volley arcs, locked nib movement arrows (MapLight), code-set labels,
an icon stamp (MapInk style "icon") and a keyframed camera (zoom/pan only).  Everything is driven by one JSON config.
usage: battlemap.py CONFIG.json [--frames t1,t2,..] [--stills DIR]"""
import sys, os, json, math, hashlib, subprocess, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animate as A

def sstep(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

def interp_keys(keys, t, n):
    """keys: [[t, v1..vn], ...]  smooth (ease-in-out) per segment; holds outside."""
    if t <= keys[0][0]: return list(keys[0][1:1 + n])
    for a, b in zip(keys[:-1], keys[1:]):
        if t <= b[0]:
            u = sstep((t - a[0]) / max(1e-6, b[0] - a[0]))
            return [a[i] + (b[i] - a[i]) * u for i in range(1, 1 + n)]
    return list(keys[-1][1:1 + n])

def pchip_keys(keys, t, n):
    """monotone cubic (Fritsch-Carlson) through keys: smooth velocity, no overshoot, holds outside."""
    T = np.float64([k[0] for k in keys])
    if t <= T[0]: return list(keys[0][1:1 + n])
    if t >= T[-1]: return list(keys[-1][1:1 + n])
    i = int(np.searchsorted(T, t) - 1); out = []
    for j in range(1, 1 + n):
        V = np.float64([k[j] for k in keys]); h = np.diff(T); dl = np.diff(V) / h
        m = np.zeros_like(V)
        for k in range(1, len(V) - 1):
            if dl[k - 1] * dl[k] > 0: m[k] = 3 * (h[k - 1] + h[k]) / ((2 * h[k] + h[k - 1]) / dl[k - 1] + (h[k] + 2 * h[k - 1]) / dl[k])
        u = (t - T[i]) / h[i]; h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
        out.append(float(h00 * V[i] + h10 * h[i] * m[i] + h01 * V[i + 1] + h11 * h[i] * m[i + 1]))
    return out

def comp_ink(roi, a, col, pigment=0.55):
    """ink over paper: multiply-ish with some opaque pigment."""
    c = np.float32(col) / 255.0; a = a[..., None]
    roi[...] = roi * (1 - a) + (roi * c * (1 - pigment) + c * 255.0 * pigment) * a

class Unit:
    def __init__(s, u, side, rng, ss=3):
        s.u = u; s.side = side; s.kind = u.get("kind", "inf"); s.ss = ss
        k0 = u["keys"][0]; s.w0, s.d0 = float(k0[3]), float(k0[4])
        m = 6; W_, H_ = int((s.w0 + 2 * m) * ss), int((s.d0 + 2 * m) * ss); s.c = (W_ / 2.0, H_ / 2.0); s.m = m
        yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); X = (xx - s.c[0]) / ss; Y = (yy - s.c[1]) / ss   # unit-local px, +Y = rear for "front":-1
        hw, hd = s.w0 / 2, s.d0 / 2
        ang = np.arctan2(Y, X); edge = A.pnoise(rng, 1, 1024, 60, 4)[0]
        jit = u.get("edge_px", 1.8) * A.pnoise(rng, H_, W_, 40 * ss, 7 * ss, 2.4) + 0.5 * A.pnoise(rng, H_, W_, 10 * ss, 3.5 * ss)
        if s.kind == "arch":                                     # wedge: point toward the front
            fr = u.get("front", -1); t_ = (Y * fr + hd) / (2 * hd)          # 0 at rear, 1 at front
            half = hw * (1 - 0.78 * np.clip(t_, 0, 1))
            dist = np.maximum(np.abs(X) - half, np.abs(Y) - hd)
        else:
            rr = min(hw, hd) * (0.45 if s.kind == "cav" else 0.25)
            qx, qy = np.maximum(np.abs(X) - (hw - rr), 0), np.maximum(np.abs(Y) - (hd - rr), 0)
            dist = np.sqrt(qx * qx + qy * qy) - rr + np.minimum(np.maximum(np.abs(X) - (hw - rr), np.abs(Y) - (hd - rr)), 0)
        body = np.clip(0.5 - (dist - jit) * ss / 1.5, 0, 1).astype(np.float32)
        inside = body > 0.5
        st = side
        col = np.float32(u.get("fill", st["fill_arch"] if s.kind in ("arch", "missile") else st["fill_cav"] if s.kind == "cav" else st["fill"]))
        gran = (1 + 0.09 * A.pnoise(rng, H_, W_, 18 * ss, 2 * ss)).astype(np.float32)                    # pigment granulation
        brush = A.pnoise(rng, H_, W_, 40 * ss, 1.5 * ss, 2.0, ax=0.18, ay=1.0).astype(np.float32)          # dry-brush streaks along the line of the block
        dE = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 5) / ss
        pool = 1 - 0.28 * np.exp(-dE / 1.6)                     # pigment pools darker at the wash edge
        lit = 1 + 0.10 * np.clip((-X / max(hw, 1) - Y / max(hd, 1)) * 0.5, -1, 1)                     # light from the upper left
        s.fC = (col[None, None, :] * (gran * pool * lit * (1 + 0.12 * brush))[..., None]).astype(np.float32)
        wash = np.clip(u.get("fill_op", 0.74) * (1 + 0.2 * brush) * (0.85 + 0.15 * np.clip(dE / 3, 0, 1)) + 0.12 * np.exp(-dE / 1.6), 0, 1)
        s.fA = (body * wash).astype(np.float32)
        L = np.zeros((H_, W_), np.float32)
        lw = u.get("outline_px", 1.7) * ss
        ring = np.clip(1 - np.abs(dist - jit) * ss / lw, 0, 1)
        L = np.maximum(L, ring)
        marks = np.zeros((H_, W_), np.uint8)
        rng2 = np.random.default_rng(u.get("seed", 7))
        if s.kind == "inf":                                      # files of men: short engraved ticks
            sx, sy = u.get("mark_dx", 6.0), u.get("mark_dy", 6.5)
            for yi in np.arange(-hd + sy * 0.7, hd - sy * 0.4, sy):
                for xi in np.arange(-hw + sx * 0.7, hw - sx * 0.4, sx):
                    x_, y_ = xi + rng2.uniform(-0.6, 0.6), yi + rng2.uniform(-0.5, 0.5)
                    p0 = (int((s.c[0] + x_ * ss) * 16), int((s.c[1] + (y_ - 1.3) * ss) * 16)); p1 = (int((s.c[0] + x_ * ss) * 16), int((s.c[1] + (y_ + 1.3) * ss) * 16))
                    cv2.line(marks, p0, p1, 255, max(1, int(0.9 * ss)), cv2.LINE_AA, shift=4)
        elif s.kind == "cav":                                    # horse: small chevrons pointing to the front, plus diagonal hatching
            fr = u.get("front", 1); sx, sy = u.get("mark_dx", 8.0), u.get("mark_dy", 7.0)
            for yi in np.arange(-hd + sy * 0.8, hd - sy * 0.3, sy):
                for xi in np.arange(-hw + sx * 0.7, hw - sx * 0.3, sx):
                    x_, y_ = xi + rng2.uniform(-0.8, 0.8), yi + rng2.uniform(-0.6, 0.6)
                    pts = [(x_ - 2.6, y_ - 1.6 * fr), (x_, y_ + 1.6 * fr), (x_ + 2.6, y_ - 1.6 * fr)]
                    cv2.polylines(marks, [np.int32([((s.c[0] + a * ss) * 16, (s.c[1] + b * ss) * 16) for a, b in pts])], False, 255, max(1, int(1.0 * ss)), cv2.LINE_AA, shift=4)
            hp = 5.0 * ss; hat = (np.abs(((xx + yy * fr) / math.sqrt(2)) % hp - hp / 2) < 0.45 * ss).astype(np.float32)
            L = np.maximum(L, hat * body * 0.3)
        elif s.kind in ("arch", "missile"):                      # archers: stipple of dots
            sx = u.get("mark_dx", 5.5)
            for yi in np.arange(-hd + 2, hd - 1, sx * 0.85):
                for xi in np.arange(-hw + 2, hw - 1, sx):
                    x_, y_ = xi + rng2.uniform(-1, 1), yi + rng2.uniform(-1, 1)
                    cv2.circle(marks, (int((s.c[0] + x_ * ss) * 16), int((s.c[1] + y_ * ss) * 16)), int(0.85 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        L = np.maximum(L, marks.astype(np.float32) / 255.0 * body * u.get("mark_op", 0.5))
        nc = int(u.get("companies", 1))                          # bodies of men under separate banners: faint wavering seams
        for ci in range(1, nc):
            xs_ = -hw + 2 * hw * ci / nc; pts = [((s.c[0] + (xs_ + 1.2 * math.sin(yv * 0.21 + ci)) * ss) * 16, (s.c[1] + yv * ss) * 16) for yv in np.linspace(-hd + 2, hd - 2, 24)]
            sm = np.zeros((H_, W_), np.uint8); cv2.polylines(sm, [np.int32(pts)], False, 255, max(1, int(1.3 * ss)), cv2.LINE_AA, shift=4)
            L = np.maximum(L, sm.astype(np.float32) / 255.0 * 0.55 * body)
        if s.kind in ("inf", "cav") and u.get("shade_hatch", True):     # engraved shading: diagonal hatch on the lower-right of the block
            hp = 3.2 * ss; hat2 = (np.abs(((xx - yy) / math.sqrt(2)) % hp - hp / 2) < 0.42 * ss).astype(np.float32)
            side_ = np.clip((X / max(hw, 1) + Y / max(hd, 1)) * 1.6 - 0.35, 0, 1)
            L = np.maximum(L, hat2 * body * side_ * 0.42)
        fib = np.clip(1 - 0.35 * np.clip(A.pnoise(rng, H_, W_, 3 * ss, 0.7 * ss), 0, None), 0.35, 1).astype(np.float32)
        s.lA = (L * fib).astype(np.float32)
        s.sh = cv2.GaussianBlur(body, (0, 0), 2.2 * ss)
        s.ink = np.float32(u.get("ink", st["ink"]))
        s.banners = u.get("banners", [])                         # [[dx, dy, design], ...] in unit-local px (pole foot)
    def state(s, t):
        x, y, w, d, ang, a = interp_keys(s.u["keys"], t, 6)
        return x, y, w, d, ang, a
    def draw(s, img, cov, t, banners_cache):
        x, y, w, d, ang, a = s.state(t)
        if a <= 0.003: return
        sx, sy = w / s.w0 / s.ss, d / s.d0 / s.ss; ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        M = np.float32([[ca * sx, -sa * sy, 0], [sa * sx, ca * sy, 0]]); M[:, 2] = np.float32([x, y]) - M[:, :2] @ np.float32(s.c)
        H_, W_ = s.fA.shape; corners = np.float32([[0, 0, 1], [W_, 0, 1], [0, H_, 1], [W_, H_, 1]]) @ M.T
        x0, y0 = np.floor(corners.min(0)).astype(int) - 8; x1, y1 = np.ceil(corners.max(0)).astype(int) + 8
        Hh, Ww = img.shape[:2]; x0, y0, x1, y1 = max(0, x0), max(0, y0), min(Ww, x1), min(Hh, y1)
        if x1 <= x0 or y1 <= y0: return
        Ml = M.copy(); Ml[:, 2] -= [x0, y0]; sz = (x1 - x0, y1 - y0)
        wf = lambda z: cv2.warpAffine(z, Ml, sz, flags=cv2.INTER_AREA if sx < 1 else cv2.INTER_LINEAR, borderValue=0)
        fA, lA, sh = wf(s.fA) * a, wf(s.lA) * a, wf(s.sh) * a; fC = wf(s.fC)
        roi = img[y0:y1, x0:x1]
        so = s.u.get("shadow_off", [2.5, 3.5]); Ms = np.float32([[1, 0, so[0]], [0, 1, so[1]]])
        shd = cv2.warpAffine(sh, Ms, sz) * s.u.get("shadow", 0.32)
        roi *= (1 - shd[..., None] * np.float32([0.85, 0.9, 1.0]))
        Y_ = 0.299 * roi[..., 0] + 0.587 * roi[..., 1] + 0.114 * roi[..., 2]
        tex = np.clip(0.66 + 0.34 * Y_ / (float(Y_.mean()) + 1e-3), 0.5, 1.3)[..., None]       # furrows/paper tooth show through the wash
        roi[...] = roi * (1 - fA[..., None]) + fC * tex * fA[..., None]
        comp_ink(roi, np.clip(lA, 0, 1), s.ink, 0.5)
        cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], np.maximum(fA, shd))
        for b in s.banners:                                      # banners stay upright (map symbol convention), ride with the unit
            bx = x + ca * b[0] * w / s.w0 - sa * b[1] * d / s.d0; by = y + sa * b[0] * w / s.w0 + ca * b[1] * d / s.d0
            banners_cache.paste(img, cov, b[2], bx, by, a)

class Banners:
    def __init__(s, designs, ss=4):
        s.spr = {}
        for name, D in designs.items(): s.spr[name] = s._make(D, ss)
    def _make(s, D, ss):
        pole, fw, fh = D.get("pole", 26), D.get("w", 20), D.get("h", 13)
        W_, H_ = int((fw + 10) * ss), int((pole + 8) * ss); fx, fy = 4 * ss, 4 * ss        # pole foot at (fx, H_-4ss)
        A_ = np.zeros((H_, W_), np.uint8); C = np.zeros((H_, W_, 3), np.float32); L = np.zeros((H_, W_), np.uint8)
        top = 4 * ss; P = lambda x, y: (int(x * 16), int(y * 16))
        tail = D.get("tail", "swallow")
        if tail == "swallow": pts = [(fx, top), (fx + fw * ss, top), (fx + fw * ss * 0.78, top + fh * ss * 0.5), (fx + fw * ss, top + fh * ss), (fx, top + fh * ss)]
        elif tail == "pennon": pts = [(fx, top), (fx + fw * ss, top + fh * ss * 0.5), (fx, top + fh * ss)]
        else: pts = [(fx, top), (fx + fw * ss, top), (fx + fw * ss, top + fh * ss), (fx, top + fh * ss)]
        # gentle cloth wave
        def wave(p): return (p[0], p[1] + 1.2 * ss * math.sin((p[0] - fx) / (fw * ss) * math.pi * 1.4))
        pts = [wave(p) for p in pts]
        flag = np.zeros((H_, W_), np.uint8); cv2.fillPoly(flag, [np.int32([P(*p) for p in pts])], 255, cv2.LINE_AA, shift=4)
        base = np.float32(D["field"]); C[:] = base
        if D.get("cross"):                                       # St George: red cross on white
            cx = fx + fw * ss * 0.38; cy = top + fh * ss * 0.5
            cm = np.zeros((H_, W_), np.uint8)
            cv2.line(cm, P(cx, top - ss), P(cx, top + fh * ss + 2 * ss), 255, int(fh * ss * 0.24), cv2.LINE_AA, shift=4)
            cv2.line(cm, P(fx - ss, cy), P(fx + fw * ss + ss, cy), 255, int(fh * ss * 0.24), cv2.LINE_AA, shift=4)
            m_ = (cm.astype(np.float32) / 255.0)[..., None]; C = C * (1 - m_) + np.float32(D["cross"]) * m_
        if D.get("dots"):                                        # three gold charges (lis)
            for (u, v) in [(0.24, 0.3), (0.56, 0.3), (0.40, 0.72)]:
                dm = np.zeros((H_, W_), np.uint8); px_, py_ = fx + fw * ss * u, top + fh * ss * v; r_ = fh * ss * 0.15
                cv2.fillPoly(dm, [np.int32([P(px_, py_ - r_ * 1.5), P(px_ + r_, py_), P(px_, py_ + r_ * 1.2), P(px_ - r_, py_)])], 255, cv2.LINE_AA, shift=4)
                m_ = (dm.astype(np.float32) / 255.0)[..., None]; C = C * (1 - m_) + np.float32(D["dots"]) * m_
        if D.get("band"):
            bm = np.zeros((H_, W_), np.uint8); cv2.line(bm, P(fx, top + fh * ss * 0.5), P(fx + fw * ss, top + fh * ss * 0.5), 255, int(fh * ss * 0.3), cv2.LINE_AA, shift=4)
            m_ = (bm.astype(np.float32) / 255.0)[..., None]; C = C * (1 - m_) + np.float32(D["band"]) * m_
        A_ = np.maximum(A_, flag)
        k_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2.6 * ss) | 1, int(2.6 * ss) | 1))
        L = np.maximum(L, cv2.subtract(cv2.dilate(flag, k_), cv2.erode(flag, k_)))
        cv2.line(L, P(fx, top - ss), P(fx, H_ - 4 * ss), 255, int(1.8 * ss), cv2.LINE_AA, shift=4)
        cv2.circle(L, P(fx, top - 1.2 * ss), int(1.7 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        ds = lambda z: cv2.resize(z, (W_ // ss, H_ // ss), interpolation=cv2.INTER_AREA)
        Af = ds(A_.astype(np.float32) / 255.0); Cf = ds(C * (A_.astype(np.float32) / 255.0)[..., None]) / np.maximum(Af[..., None], 1e-4)
        Lf = ds(L.astype(np.float32) / 255.0)
        return dict(A=Af, C=Cf, L=Lf, foot=(fx / ss, H_ / ss - 4), ink=np.float32(D.get("ink", [40, 26, 16])), sh=cv2.GaussianBlur(np.maximum(Af, Lf), (0, 0), 1.6))
    def paste(s, img, cov, name, x, y, a):
        S = s.spr[name]; h, w = S["A"].shape; ox, oy = x - S["foot"][0], y - S["foot"][1]
        x0, y0 = int(math.floor(ox)) - 4, int(math.floor(oy)) - 4; x1, y1 = x0 + w + 9, y0 + h + 9
        Hh, Ww = img.shape[:2]
        if x0 < 0 or y0 < 0 or x1 > Ww or y1 > Hh: return
        M = np.float32([[1, 0, ox - x0], [0, 1, oy - y0]]); sz = (x1 - x0, y1 - y0)
        Aw, Lw, Sw = (cv2.warpAffine(S[k], M, sz) * a for k in ("A", "L", "sh")); Cw = cv2.warpAffine(S["C"], M, sz)
        roi = img[y0:y1, x0:x1]
        shd = cv2.warpAffine(Sw, np.float32([[1, 0, 2.0], [0, 1, 2.5]]), sz) * 0.3; roi *= 1 - shd[..., None]
        roi[...] = roi * (1 - Aw[..., None] * 0.95) + Cw * Aw[..., None] * 0.95
        comp_ink(roi, np.clip(Lw, 0, 1) * 0.9, S["ink"], 0.6)
        cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], np.maximum(Aw, Lw))

class Stakes:
    """hatched stake line: short slanted strokes inked one after another along a-b; can be lifted (fade) and re-planted elsewhere."""
    def __init__(s, st, ss=3):
        s.q = {**dict(spacing=6.5, length=11.0, slant_deg=-62, width=1.7, plant_s=0.35, lift_s=0.25, ink=[46, 30, 16], t_off=1e9), **st}
        a, b = np.float32(s.q["a"]), np.float32(s.q["b"]); L = float(np.linalg.norm(b - a)); n = max(2, int(L / s.q["spacing"]))
        rng = np.random.default_rng(s.q.get("seed", 3))
        s.pts = [a + (b - a) * (i / (n - 1)) + rng.uniform(-1.2, 1.2, 2) for i in range(n)]
        s.jl = rng.uniform(0.8, 1.15, n); s.ja = rng.uniform(-8, 8, n); s.n = n
    def draw(s, img, cov, t):
        q = s.q
        if t < q["t_on"]: return
        fade = 1 - sstep((t - q["t_off"]) / q["lift_s"])
        if fade <= 0: return
        pr = (t - q["t_on"]) / q["plant_s"]
        pad = 14; P = np.float32(s.pts); x0, y0 = (P.min(0) - pad).astype(int); x1, y1 = (P.max(0) + pad).astype(int); ss = 3
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        for i, p in enumerate(s.pts):
            v = min(1.0, max(0.0, pr * s.n - i))
            if v <= 0: break
            an = math.radians(q["slant_deg"] + s.ja[i]); L = q["length"] * s.jl[i] * (0.4 + 0.6 * v)
            d = np.float32([math.cos(an), math.sin(an)]) * L / 2; c = (p - [x0, y0]) * ss
            cv2.line(m, tuple(((c - d * ss) * 16).astype(int)), tuple(((c + d * ss) * 16).astype(int)), 255, max(1, int(q["width"] * ss)), cv2.LINE_AA, shift=4)
            cv2.circle(m, tuple(((c - d * ss) * 16).astype(int)), int(q["width"] * 0.9 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)   # sharpened point toward the enemy
        a = cv2.resize(m.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA) * fade
        roi = img[y0:y1, x0:x1]; comp_ink(roi, a * 0.92, q["ink"], 0.55); cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], a)

class Volley:
    """inked arrow-flight arcs: each arc draws on src->dst (head runs ahead, ink trails), then fades as it dries; staggered within the volley."""
    def __init__(s, v, rng):
        s.q = q = {**dict(n=10, dur=0.32, hold=0.25, fade=0.45, spread_src=12.0, spread_dst=26.0, stagger=0.28, bulge=0.22, width=2.2, ink=[40, 22, 12], op=0.85, side=1), **v}
        s.arcs = []
        for i in range(q["n"]):
            s0 = np.float32(q["src"]) + rng.normal(0, q["spread_src"], 2); d0 = np.float32(q["dst"]) + rng.normal(0, q["spread_dst"], 2) * [1.0, 0.45]
            mid = (s0 + d0) / 2; dv = d0 - s0; nrm = np.float32([-dv[1], dv[0]]) / (np.linalg.norm(dv) + 1e-6)
            cpt = mid + nrm * np.linalg.norm(dv) * q["bulge"] * q["side"] * rng.uniform(0.75, 1.25)
            uu = np.linspace(0, 1, 40)[:, None]; pts = (1 - uu) ** 2 * s0 + 2 * (1 - uu) * uu * cpt + uu ** 2 * d0
            s.arcs.append((q["t0"] + rng.uniform(0, q["stagger"]), pts.astype(np.float32)))
        P = np.concatenate([a[1] for a in s.arcs]); s.bb = (P.min(0) - 12).astype(int), (P.max(0) + 12).astype(int)
        s.t_end = max(a[0] for a in s.arcs) + q["dur"] + q["hold"] + q["fade"]
    def draw(s, img, cov, t):
        q = s.q
        if t < q["t0"] or t > s.t_end: return
        (x0, y0), (x1, y1) = s.bb; Hh, Ww = img.shape[:2]; x0, y0, x1, y1 = max(0, x0), max(0, y0), min(Ww, x1), min(Hh, y1); ss = 3
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.float32)
        for ta, pts in s.arcs:
            age = t - ta
            if age <= 0: continue
            hd = min(1.0, age / q["dur"]); tl = max(0.0, (age - q["dur"] * 0.55) / q["dur"]) * 0.0   # whole arc stays inked; dries away
            a = 1 - sstep((age - q["dur"] - q["hold"]) / q["fade"])
            if a <= 0: continue
            k = max(2, int(hd * (len(pts) - 1)) + 1); seg = (pts[:k] - [x0, y0]) * ss
            lay = np.zeros_like(m)
            cv2.polylines(lay, [np.int32(seg * 16)], False, 1.0, max(1, int(q["width"] * ss)), cv2.LINE_AA, shift=4)
            if hd >= 1.0:                                        # tiny arrowhead tick at the fall
                p1, p0 = seg[-1], seg[-4]; dv = (p1 - p0) / (np.linalg.norm(p1 - p0) + 1e-6)
                for sg in (1, -1):
                    rot = np.float32([dv[0] * math.cos(2.6) - sg * dv[1] * math.sin(2.6), sg * dv[0] * math.sin(2.6) + dv[1] * math.cos(2.6)])
                    cv2.line(lay, tuple((p1 * 16).astype(int)), tuple(((p1 + rot * 5.5 * ss) * 16).astype(int)), 1.0, max(1, int(q["width"] * 0.8 * ss)), cv2.LINE_AA, shift=4)
            m = np.maximum(m, lay * a)
        al = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA) * q["op"]
        roi = img[y0:y1, x0:x1]; comp_ink(roi, al, q["ink"], 0.5); cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], al)

class Arrow:
    """movement arrow: the locked MapLight nib route (hand-inked) + an inked arrowhead that opens when the nib arrives."""
    def __init__(s, ar, ctx, rng):
        s.q = q = {**dict(width=4.2, head_px=17.0, head_s=0.14, fade_at=None, fade_s=0.4), **ar}
        ink = {**dict(wet_color=[30, 14, 10], dry_color=[110, 40, 30], pigment=0.5), **q.get("ink", {})}
        H, W = ctx["H"], ctx["W"]
        s.ml = A.MapLight(ctx, np.ones((H, W), np.float32), 1.0, dict(route=dict(points=q["points"], t0=q["t0"], t1=q["t1"], width=q["width"], style="nib", supersample=3, dash=q.get("dash")), ink=ink), rng)
        P = A.catmull(q["points"]); s.tip = P[-1]; s.dirv = (P[-1] - P[-4]) / (np.linalg.norm(P[-1] - P[-4]) + 1e-6); s.ink = ink
    def draw(s, img, cov, t):
        q = s.q
        if t < q["t0"]: return
        fa = 1.0 if q["fade_at"] is None else 1 - sstep((t - q["fade_at"]) / q["fade_s"])
        if fa <= 0: return
        before = img.copy() if fa < 1 else None
        s.ml.overlay(img, t)
        hv = sstep((t - q["t1"] + 0.04) / q["head_s"])
        if hv > 0:
            ss = 3; L = q["head_px"]; x0, y0 = (s.tip - L * 1.6).astype(int); x1, y1 = (s.tip + L * 1.6).astype(int)
            m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8); c = (s.tip - [x0, y0]) * ss; dv = s.dirv
            pts = []
            for sg in (1, -1):
                an = sg * 0.48; r_ = np.float32([dv[0] * math.cos(an) - dv[1] * math.sin(an), dv[0] * math.sin(an) + dv[1] * math.cos(an)])
                pts.append(c - r_ * L * hv * ss)
            tri = np.int32([c * 16, pts[0] * 16, (c - dv * L * 0.62 * hv * ss) * 16, pts[1] * 16])
            cv2.fillPoly(m, [tri], 255, cv2.LINE_AA, shift=4)
            a = cv2.resize(m.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
            wet = math.exp(-max(0.0, t - q["t1"]) / 0.7); col = np.float32(s.ink["wet_color"]) * wet + np.float32(s.ink["dry_color"]) * (1 - wet)
            roi = img[y0:y1, x0:x1]; comp_ink(roi, a * 0.92, col, 0.6)
        if before is not None: img[...] = before + (img - before) * fa
        d = np.abs(img - (before if before is not None else img)).max(-1) if False else None

class Labels:
    def __init__(s, labels, size, fonts):
        H, W = size; s.items = []
        for L in labels:
            q = {**dict(size=40, rot=0, t_on=0.3, t_in=0.6, tracking=0.12, color=[50, 32, 18], halo=[238, 224, 190], halo_op=0.55, font="sc", op=0.9), **L}
            f = ImageFont.truetype(fonts[q["font"]], int(q["size"] * 3))
            txt = q["text"]; tr = q["tracking"] * q["size"] * 3
            widths = [f.getlength(ch) for ch in txt]; tw = int(sum(widths) + tr * (len(txt) - 1)) + 40; th = int(q["size"] * 3 * 1.6) + 20
            im = Image.new("L", (tw, th), 0); d = ImageDraw.Draw(im); x = 20
            for ch, wd in zip(txt, widths): d.text((x, 10), ch, font=f, fill=255); x += wd + tr
            a = np.asarray(im).astype(np.float32) / 255.0
            if q["rot"]:
                im2 = Image.fromarray((a * 255).astype(np.uint8)).rotate(q["rot"], resample=Image.BICUBIC, expand=True); a = np.asarray(im2).astype(np.float32) / 255.0
            a = cv2.resize(a, (a.shape[1] // 3, a.shape[0] // 3), interpolation=cv2.INTER_AREA)
            h, w = a.shape; x0, y0 = int(q["xy"][0] - w / 2), int(q["xy"][1] - h / 2)
            halo = np.clip(cv2.GaussianBlur(cv2.dilate(a, np.ones((3, 3), np.uint8)), (0, 0), q["size"] * 0.12) * 2.2, 0, 1)
            s.items.append(dict(q=q, a=a, halo=halo, x0=x0, y0=y0))
    def draw(s, img, cov, t, zoom=1.0):
        for it in s.items:
            q = it["q"]; v = sstep((t - q["t_on"]) / q["t_in"])
            if q.get("hide_zoom"): v *= 1 - sstep((zoom - q["hide_zoom"][0]) / (q["hide_zoom"][1] - q["hide_zoom"][0]))
            if v <= 0: continue
            h, w = it["a"].shape; roi = img[it["y0"]:it["y0"] + h, it["x0"]:it["x0"] + w]
            ha = it["halo"][:roi.shape[0], :roi.shape[1]] * q["halo_op"] * v; a = it["a"][:roi.shape[0], :roi.shape[1]] * q["op"] * v
            roi[...] = roi * (1 - ha[..., None]) + np.float32(q["halo"]) * ha[..., None]
            comp_ink(roi, a, q["color"], 0.7)
            cov[it["y0"]:it["y0"] + h, it["x0"]:it["x0"] + w] = np.maximum(cov[it["y0"]:it["y0"] + h, it["x0"]:it["x0"] + w], np.maximum(ha, a))

class Camera:
    def __init__(s, keys, plate_wh, out_wh, ss=2):
        s.keys = keys; s.PW, s.PH = plate_wh; s.OW, s.OH = out_wh; s.ss = ss; s.s0 = s.OW / s.PW
    def M(s, t):
        cx, cy, z = pchip_keys(s.keys, t, 3); sc = s.s0 * max(1.0, z)
        hw, hh = s.OW / sc / 2, s.OH / sc / 2
        cx = min(max(cx, hw), s.PW - hw); cy = min(max(cy, hh), s.PH - hh)
        k = sc * s.ss
        return np.float32([[k, 0, s.OW * s.ss / 2 - k * cx], [0, k, s.OH * s.ss / 2 - k * cy]]), (cx, cy, z)
    def apply(s, img, t):
        M, st = s.M(t)
        big = cv2.warpAffine(img, M, (s.OW * s.ss, s.OH * s.ss), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        return cv2.resize(big, (s.OW, s.OH), interpolation=cv2.INTER_AREA), st

def build(cfg, root):
    pl = cv2.cvtColor(cv2.imread(os.path.join(root, cfg["plate"])), cv2.COLOR_BGR2RGB).astype(np.float32); H, W = pl.shape[:2]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32); ctx = dict(H=H, W=W, X=X, Y=Y, plate=pl, half=4.0)
    seed = cfg.get("seed", 1415)
    sides = cfg["sides"]
    units = [Unit(u, sides[u["side"]], np.random.default_rng([seed, 10, i])) for i, u in enumerate(cfg["units"])]
    ban = Banners(cfg["banners"])
    stakes = [Stakes(s_) for s_ in cfg.get("stakes", [])]
    vol = [Volley(v, np.random.default_rng([seed, 20, i])) for i, v in enumerate(cfg.get("volleys", []))]
    arrows = [Arrow(a, ctx, np.random.default_rng([seed, 30, i])) for i, a in enumerate(cfg.get("arrows", []))]
    labels = Labels(cfg.get("labels", []), (H, W), cfg["fonts"])
    mk = cfg.get("marker"); ink = None
    if mk:
        st = {**dict(style="icon"), **mk}
        ink = A.MapInk(ctx, np.ones((H, W), np.float32), 1.0, dict(stamps=[st]), np.random.default_rng([seed, 40]))
    cam = Camera(cfg["camera"], (W, H), tuple(cfg["size"]), cfg.get("cam_ss", 2))
    layers = cfg.get("order", ["labels", "stakes", "units", "arrows", "volleys", "marker"])
    def frame(t):
        img = pl.copy(); cov = np.zeros((H, W), np.float32)
        for L in layers:
            if L == "labels": labels.draw(img, cov, t, cam.M(t)[1][2])
            elif L == "stakes": [s_.draw(img, cov, t) for s_ in stakes]
            elif L == "units": [u.draw(img, cov, t, ban) for u in units]
            elif L.startswith("units:"):
                ids = L[6:].split(","); [u.draw(img, cov, t, ban) for u in units if u.u["id"] in ids]
            elif L == "units-rest":
                pass
            elif L == "arrows": [a.draw(img, cov, t) for a in arrows]
            elif L == "volleys": [v.draw(img, cov, t) for v in vol]
            elif L == "marker" and ink is not None: ink.overlay(img, t)
        g = cfg.get("grade")
        out, st = cam.apply(np.clip(img, 0, 255), t)
        return img, out, st
    return pl, frame

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--stills", default=None); ap.add_argument("--times", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args(); root = os.path.dirname(os.path.abspath(__file__))
    cfg = json.load(open(a.config)); pl, frame = build(cfg, root)
    fps, dur = cfg["fps"], cfg["duration"]; OW, OH = cfg["size"]
    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
        for t in [float(x) for x in a.times.split(",")]:
            _, out, st = frame(t); cv2.imwrite(os.path.join(a.stills, f"t{t:05.2f}.png"), cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        return
    outp = a.out or os.path.join(root, cfg["out_dir"], cfg["name"] + ".mp4")
    wr = A.ffmpeg_writer(outp, OW, OH, fps); fh = hashlib.sha256(); land_bad = 0
    for i in range(int(round(fps * dur))):
        t = i / fps; img, out, st = frame(t)
        o8 = np.clip(np.round(out), 0, 255).astype(np.uint8); fh.update(o8.tobytes()); wr.stdin.write(o8.tobytes())
        if i % 30 == 0: print(f"f{i} t={t:.2f} cam=({st[0]:.0f},{st[1]:.0f},{st[2]:.2f})", flush=True)
    wr.stdin.close(); rc = wr.wait(); print("frames_sha256", fh.hexdigest())
    if rc: raise SystemExit(f"ffmpeg rc={rc}")

if __name__ == "__main__": main()
