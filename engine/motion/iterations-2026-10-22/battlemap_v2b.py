#!/usr/bin/env python3
"""Posterity battle-map renderer v2 (b9).  Standalone (does NOT import battlemap.py; v1 stays frozen).
Static painted plate, never remapped (land 0 px) + procedural overlays in plate space, then a zoom/pan camera.
v2: ragged painterly troop masses (noise-edged SDF washes, upper-left light, drop shadow, stragglers) with per-man helmet dots,
lance ticks and banners riding a non-linear unit warp (width, depth, angle, funnel taper, front bulge, disorder);
double stake rows; inked volley arcs with arrow-fall stipple; locked MapLight nib arrows; write-on period-font labels
(frame-clamped, fade at the viewport edge); MapInk icon stamp; pchip camera.
v2b (2026-10-22): fixes the v2 view-unpack crash; adds low-frequency silhouette lumps (big_px), per-kind emboss/dot opacity,
thinner sepia volley arcs, brighter cavalry horns, greyer missile stipple.
usage: battlemap_v2b.py CONFIG.json [--stills DIR --times a,b] [--out PATH]"""
import sys, os, json, math, hashlib, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animate as A

def sstep(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
NK = 9   # unit key columns after t: x y w d ang alpha funnel bulge disorder

def interp_keys(keys, t, n):
    keys = [list(k) + [0.0] * (n + 1 - len(k)) for k in keys]
    if t <= keys[0][0]: return list(keys[0][1:1 + n])
    for a, b in zip(keys[:-1], keys[1:]):
        if t <= b[0]:
            u = sstep((t - a[0]) / max(1e-6, b[0] - a[0]))
            return [a[i] + (b[i] - a[i]) * u for i in range(1, 1 + n)]
    return list(keys[-1][1:1 + n])

def pchip_keys(keys, t, n):
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
    c = np.float32(col) / 255.0; a = a[..., None]
    roi[...] = roi * (1 - a) + (roi * c * (1 - pigment) + c * 255.0 * pigment) * a

def clip_box(x0, y0, x1, y1, W, H): return max(0, x0), max(0, y0), min(W, x1), min(H, y1)

KINDS = {
    "fr_inf":     dict(fill=[64, 74, 112], op=0.9, edge_px=4.0, big_px=10.0, emboss=1.6, lump=38, fur=6, corner=0.3, dx=5.0, dy=5.4, dot_r=1.3, dot=[18, 20, 34], glint=[176, 182, 198], glint_op=0.55,
                       lance=0.10, lance_len=7.0, lance_mode="up", strag=16, outline=[22, 26, 48], outline_op=0.45, rim=None, shadow=0.40, figure=False),
    "fr_cav":     dict(fill=[208, 168, 76], op=0.94, edge_px=3.0, big_px=4.0, emboss=1.5, dot_op=0.5, lump=26, fur=5, corner=0.8, dx=6.4, dy=6.2, dot_r=1.4, dot=[40, 28, 16], glint=[236, 222, 176], glint_op=0.5,
                       lance=0.5, lance_len=8.0, lance_mode="front", strag=6, outline=[62, 42, 18], outline_op=0.55, rim=None, shadow=0.42, figure=False, horse=True),
    "fr_missile": dict(fill=[178, 184, 200], op=0.72, edge_px=2.4, big_px=3.5, emboss=1.2, lump=22, fur=3, corner=0.6, dx=3.4, dy=3.4, dot_r=0.95, dot=[34, 38, 66], glint=None,
                       lance=0.0, strag=6, outline=[60, 66, 98], outline_op=0.5, rim=None, shadow=0.30, figure=False),
    "en_maa":     dict(fill=[146, 26, 22], op=0.95, edge_px=1.1, big_px=1.2, emboss=1.3, lump=30, fur=5, corner=0.45, dx=4.4, dy=4.2, dot_r=1.15, dot=[46, 8, 6], glint=[226, 196, 182], glint_op=0.45,
                       lance=0.06, lance_len=5.0, lance_mode="front", strag=0, outline=[40, 8, 6], outline_op=0.5, rim=[246, 234, 210], shadow=0.42, figure=False),
    "en_arch":    dict(fill=[230, 208, 172], op=0.86, edge_px=4.0, big_px=4.0, emboss=1.4, lump=26, fur=5, corner=0.55, dx=4.6, dy=4.8, dot_r=1.05, dot=[120, 16, 14], glint=None,
                       lance=0.0, strag=10, outline=[110, 30, 22], outline_op=0.45, rim=None, shadow=0.36, figure=True),
}

class Mass:
    """one body of men: ragged noise-edged SDF wash in unit-local base px (+v = front), warped per frame by a closed-form inverse map."""
    def __init__(s, u, rng, banners):
        s.u = u; s.K = K = {**KINDS[u["kind"]], **u.get("style", {})}; s.ban = banners
        k0 = u["keys"][0]; s.w0, s.d0 = float(k0[3]), float(k0[4]); s.fs = float(u.get("front", 1))
        hw, hd = s.w0 / 2, s.d0 / 2; s.ss = ss = 2; s.m = m = int(K["edge_px"] * 3 + 18)
        W_, H_ = int((s.w0 + 2 * m) * ss), int((s.d0 + 2 * m) * ss)
        yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); X = xx / ss - (hw + m); Y = yy / ss - (hd + m)
        rr = min(hw, hd) * K["corner"]
        qx, qy = np.maximum(np.abs(X) - (hw - rr), 0), np.maximum(np.abs(Y) - (hd - rr), 0)
        sdf = np.sqrt(qx * qx + qy * qy) - rr + np.minimum(np.maximum(np.abs(X) - (hw - rr), np.abs(Y) - (hd - rr)), 0)
        if u.get("shape") == "wedge":                            # archers' wedge pointing to the front
            tf = np.clip((Y + hd) / (2 * hd), 0, 1); half = hw * (1 - 0.55 * tf)
            sdf = np.maximum(np.abs(X) - half, np.abs(Y) - hd) * 0.85 + 0.15 * sdf
        lump, fur = K["lump"] * ss, K["fur"] * ss
        nb = A.pnoise(rng, H_, W_, lump * 2.6, lump / 2, 2.8); n0 = A.pnoise(rng, H_, W_, lump, lump / 4, 2.6); nf = A.pnoise(rng, H_, W_, fur, 1.6 * ss, 2.0)
        E1 = A.pnoise(rng, H_, W_, lump, lump / 4, 2.6); E2 = A.pnoise(rng, H_, W_, lump, lump / 4, 2.6)
        ep = K["edge_px"]
        s.F1 = np.dstack([sdf - K.get("big_px", 0.0) * nb - ep * (0.9 * n0 + 0.35 * nf), E1 * ep, E2 * ep]).astype(np.float32)
        # stragglers: small blobs just outside the ragged edge (more at the front/flanks)
        r2 = np.random.default_rng(u.get("seed", 11)); strag = np.full((H_, W_), 99.0, np.float32); s.str_pts = []
        base = s.F1[..., 0]; tries = 0
        while len(s.str_pts) < K["strag"] and tries < 4000:
            tries += 1
            px, py = r2.uniform(-hw - m + 4, hw + m - 4), r2.uniform(-hd - m + 4, hd + m - 4)
            ix, iy = int((px + hw + m) * ss), int((py + hd + m) * ss); dv = base[iy, ix]
            if not (3.0 < dv < 4.0 + ep * 2.2): continue
            if py < -hd * 0.3 and r2.uniform() < 0.6: continue
            rad = r2.uniform(1.7, 2.8); s.str_pts.append((px, py, rad))
            x0, x1 = max(0, ix - 12 * ss), min(W_, ix + 12 * ss); y0, y1 = max(0, iy - 12 * ss), min(H_, iy + 12 * ss)
            d_ = np.sqrt((X[y0:y1, x0:x1] - px) ** 2 + (Y[y0:y1, x0:x1] - py) ** 2) - rad
            strag[y0:y1, x0:x1] = np.minimum(strag[y0:y1, x0:x1], d_)
        gran = (1 + 0.10 * A.pnoise(rng, H_, W_, 16 * ss, 2 * ss)).astype(np.float32)
        brush = A.pnoise(rng, H_, W_, 50 * ss, 2 * ss, 2.0, ax=0.2, ay=1.0).astype(np.float32)
        s.F2 = np.dstack([strag, gran, brush]).astype(np.float32)
        s.fill = np.float32(K["fill"])
        # men: grid points inside the (static) ragged body + one per straggler
        pts, lance, kind = [], [], []
        dxp, dyp = K["dx"], K["dy"]
        for row, yi in enumerate(np.arange(-hd - ep, hd + ep, dyp)):
            off = (row % 2) * dxp * 0.5
            for xi in np.arange(-hw - ep + off, hw + ep, dxp):
                x_, y_ = xi + r2.uniform(-0.7, 0.7), yi + r2.uniform(-0.6, 0.6)
                ix, iy = int((x_ + hw + m) * ss), int((y_ + hd + m) * ss)
                if not (0 <= ix < W_ and 0 <= iy < H_): continue
                sv = base[iy, ix]
                if sv < -1.6: pts.append((x_, y_, sv)); lance.append(r2.uniform() < K["lance"]); kind.append(0)
        for (px, py, rad) in s.str_pts: pts.append((px, py, -rad)); lance.append(r2.uniform() < K["lance"] * 2); kind.append(1)
        s.P = np.float32([p[:2] for p in pts]).reshape(-1, 2); s.Psdf = np.float32([p[2] for p in pts]); s.lance = np.bool_(lance)
        s.ph = r2.uniform(0, 6.283, (len(pts), 3)).astype(np.float32); s.fq = r2.uniform(0.25, 0.6, (len(pts), 2)).astype(np.float32)
        s.lj = r2.uniform(-0.35, 0.35, len(pts)).astype(np.float32)
        s.banners = u.get("banners", [])                         # [[u, v, design, phase], ...] u,v in [-1,1] local normalized (v + = front)
        s.grow_px = float(u.get("grow_px", 10.0))

    def state(s, t): return interp_keys(s.u["keys"], t, NK)

    def fwd(s, P, st):
        x, y, w, d, ang, a, fun, bul, dis = st
        u = P[:, 0] / (s.w0 / 2); v = P[:, 1] / (s.d0 / 2)
        hw = w / 2 * (1 + fun * np.clip(v, -1.3, 1.3)); lx = u * hw
        ly = v * d / 2 + bul * (1 - np.clip(u, -1, 1) ** 2) * np.clip((v + 1) / 2, 0, 1.2)
        ox, oy = lx, s.fs * ly; c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        return np.stack([x + c * ox - sn * oy, y + sn * ox + c * oy], 1)

    def roi_box(s, st, W, H, pad=24):
        hw, hd = s.w0 / 2 + s.m, s.d0 / 2 + s.m
        C = np.float32([[-hw, -hd], [hw, -hd], [-hw, hd], [hw, hd], [0, hd], [0, -hd]])
        Q = s.fwd(C, st); x0, y0 = np.floor(Q.min(0)).astype(int) - pad; x1, y1 = np.ceil(Q.max(0)).astype(int) + pad
        return clip_box(int(x0), int(y0), int(x1), int(y1), W, H)

    def draw(s, img, cov, t, ban):
        st = s.state(t); x, y, w, d, ang, a, fun, bul, dis = st
        if a <= 0.003: return
        H, W = img.shape[:2]; x0, y0, x1, y1 = s.roi_box(st, W, H)
        if x1 <= x0 or y1 <= y0: return
        K = s.K; m = s.m; ss = s.ss
        Yg, Xg = np.mgrid[y0:y1, x0:x1].astype(np.float32); c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        qx = c * (Xg - x) + sn * (Yg - y); qy = -sn * (Xg - x) + c * (Yg - y); ly = s.fs * qy
        v = ly / (d / 2); u = qx / (w / 2)
        for _ in range(4):
            u = qx / (w / 2 * (1 + fun * np.clip(v, -1.3, 1.3)))
            v = (ly - bul * (1 - np.clip(u, -1, 1) ** 2) * np.clip((v + 1) / 2, 0, 1.2)) / (d / 2)
        mx = ((u * s.w0 / 2) + s.w0 / 2 + m) * ss; my = ((v * s.d0 / 2) + s.d0 / 2 + m) * ss
        F1 = cv2.remap(s.F1, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(99, 0, 0))
        F2 = cv2.remap(s.F2, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(99, 1, 0))
        sc = math.sqrt(max(1e-3, w * d / (s.w0 * s.d0)))
        ph = 2 * math.pi * t / 7.0
        grow = (1 - min(1.0, a)) * s.grow_px
        db = F1[..., 0] - 0.45 * (F1[..., 1] * math.cos(ph) + F1[..., 2] * math.sin(ph)) - dis * 0.5 * F1[..., 1] + grow
        dsg = F2[..., 0] + grow * 1.5
        dd = np.minimum(db, dsg) * sc
        al = np.clip(0.6 - dd / 1.1, 0, 1).astype(np.float32)
        aop = min(1.0, a) ** 0.6
        # light from the upper left: emboss of the softened mass
        g = cv2.GaussianBlur(al, (0, 0), 2.4); gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3) / 8; gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3) / 8
        g2 = cv2.GaussianBlur(al, (0, 0), 7.0); gx2 = cv2.Sobel(g2, cv2.CV_32F, 1, 0, ksize=3) / 8; gy2 = cv2.Sobel(g2, cv2.CV_32F, 0, 1, ksize=3) / 8
        em = K.get("emboss", 1.0); shade = 1 + em * (1.5 * (gx + gy) + 2.2 * (gx2 + gy2))
        pool = 1 - 0.24 * np.exp(-np.maximum(-dd, 0) / 1.8)
        col = s.fill[None, None, :] * (F2[..., 1] * pool * shade * (1 + 0.07 * F2[..., 2]))[..., None]
        roi = img[y0:y1, x0:x1]
        # soft drop shadow (offset to the lower right)
        sh = cv2.GaussianBlur(al, (0, 0), 3.2); sh = cv2.warpAffine(sh, np.float32([[1, 0, 4.5], [0, 1, 5.5]]), (x1 - x0, y1 - y0)) * K["shadow"] * aop
        roi *= (1 - sh[..., None] * np.float32([0.82, 0.86, 1.0]))
        Yl = 0.299 * roi[..., 0] + 0.587 * roi[..., 1] + 0.114 * roi[..., 2]
        tex = np.clip(0.72 + 0.28 * Yl / (float(Yl.mean()) + 1e-3), 0.55, 1.25)[..., None]
        A_ = al * K["op"] * aop
        roi[...] = roi * (1 - A_[..., None]) + col * tex * A_[..., None]
        ring = np.clip(1 - np.abs(dd + 0.6) / 1.0, 0, 1) * aop
        if K.get("rim"): comp_ink(roi, ring * 0.85, K["rim"], 0.9)
        else: comp_ink(roi, ring * K["outline_op"], K["outline"], 0.5)
        cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], np.maximum(A_, sh))
        # men
        vis = (s.Psdf + grow) < -0.6
        if vis.any():
            P = s.P[vis]; phs = s.ph[vis]; fq = s.fq[vis]
            jit = np.stack([np.sin(t * fq[:, 0] * 6.283 + phs[:, 0]), np.sin(t * fq[:, 1] * 6.283 + phs[:, 1])], 1) * (0.25 + 1.8 * dis)
            Q = s.fwd(P, st) + jit.astype(np.float32)
            S3 = 3; hh, ww = (y1 - y0) * S3, (x1 - x0) * S3
            Md = np.zeros((hh, ww), np.uint8); Mg = np.zeros((hh, ww), np.uint8)
            fdir = np.float32([-sn * s.fs, c * s.fs])           # front direction in plate
            r = K["dot_r"]; lam = s.lance[vis]; lj = s.lj[vis]
            for i, (px, py) in enumerate(Q):
                cx, cy = (px - x0) * S3, (py - y0) * S3
                if K.get("horse"):
                    an = math.degrees(math.atan2(fdir[1], fdir[0]))
                    cv2.ellipse(Md, (int(cx * 16), int(cy * 16)), (int(r * 2.1 * S3 * 16), int(r * 1.05 * S3 * 16)), an, 0, 360, 255, -1, cv2.LINE_AA, shift=4)
                elif K.get("figure"):
                    cv2.circle(Md, (int(cx * 16), int((cy - 1.2 * S3) * 16)), int(r * S3 * 16), 255, -1, cv2.LINE_AA, shift=4)
                    cv2.line(Md, (int(cx * 16), int((cy - 0.6 * S3) * 16)), (int((cx + 0.3 * S3) * 16), int((cy + 1.9 * S3) * 16)), 255, max(1, int(0.9 * S3)), cv2.LINE_AA, shift=4)
                else:
                    cv2.circle(Md, (int((cx + 0.35 * S3) * 16), int((cy + 0.35 * S3) * 16)), int(r * S3 * 16), 255, -1, cv2.LINE_AA, shift=4)
                    if K.get("glint"): cv2.circle(Mg, (int((cx - 0.4 * S3) * 16), int((cy - 0.45 * S3) * 16)), int(r * 0.5 * S3 * 16), 255, -1, cv2.LINE_AA, shift=4)
                if lam[i]:
                    L = K["lance_len"] * S3
                    if K["lance_mode"] == "front": vx, vy = fdir[0] + lj[i] * 0.3, fdir[1] + lj[i] * 0.3
                    else: vx, vy = 0.30 + lj[i], -1.0
                    nn = math.hypot(vx, vy); vx, vy = vx / nn, vy / nn
                    cv2.line(Md, (int(cx * 16), int(cy * 16)), (int((cx + vx * L) * 16), int((cy + vy * L) * 16)), 255, max(1, int(0.75 * S3)), cv2.LINE_AA, shift=4)
            ad = cv2.resize(Md, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0 * aop
            comp_ink(roi, ad * K.get("dot_op", 0.85), K["dot"], 0.55)
            if K.get("glint"):
                ag = cv2.resize(Mg, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0 * aop
                comp_ink(roi, ag * K["glint_op"], K["glint"], 0.9)
            cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], ad)
        for b in s.banners:
            uu, vv, des = b[0], b[1], b[2]; ph0 = b[3] if len(b) > 3 else 0.0
            Pb = s.fwd(np.float32([[uu * s.w0 / 2, vv * s.d0 / 2]]), st)[0]
            ban.paste(img, cov, des, float(Pb[0]), float(Pb[1]), aop * sstep((a - 0.5) / 0.5), t, ph0)

class Banners:
    """upright map-symbol banners on poles; cloth wave animated by blending pre-drawn phases."""
    NPH = 8
    def __init__(s, designs, ss=4):
        s.spr = {n: [s._make(D, ss, k / s.NPH) for k in range(s.NPH)] for n, D in designs.items()}
    def _make(s, D, ss, phase):
        pole, fw, fh = D.get("pole", 34), D.get("w", 26), D.get("h", 17)
        W_, H_ = int((fw + 12) * ss), int((pole + 10) * ss); fx = 5 * ss; top = 5 * ss
        P = lambda x, y: (int(x * 16), int(y * 16)); tail = D.get("tail", "swallow")
        if tail == "swallow": pts = [(0, 0), (1, 0), (0.76, 0.5), (1, 1), (0, 1)]
        elif tail == "pennon": pts = [(0, 0), (1, 0.45), (1, 0.55), (0, 1)]
        else: pts = [(0, 0), (1, 0), (1, 1), (0, 1)]
        def dense(pts, n=10):
            out = []
            for a, b in zip(pts, pts[1:] + pts[:1]):
                for k in range(n): out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
            return out
        def wave(u, v): return (fx + u * fw * ss, top + v * fh * ss + 1.6 * ss * u * math.sin(u * math.pi * 1.5 - phase * 2 * math.pi))
        poly = np.int32([P(*wave(u, v)) for u, v in dense(pts)])
        flag = np.zeros((H_, W_), np.uint8); cv2.fillPoly(flag, [poly], 255, cv2.LINE_AA, shift=4)
        yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); U = (xx - fx) / (fw * ss)
        V = (yy - top - 1.6 * ss * U * np.sin(U * math.pi * 1.5 - phase * 2 * math.pi)) / (fh * ss)
        C = np.zeros((H_, W_, 3), np.float32); C[:] = np.float32(D["field"])
        def put(mask, col): mm = mask.astype(np.float32)[..., None]; return C * (1 - mm) + np.float32(col) * mm
        if D.get("cross"):
            C = put((np.abs(U - 0.36) < 0.10) | (np.abs(V - 0.5) < 0.14), D["cross"])
        if D.get("quarterly"):                                   # France modern quartered with England
            q1 = ((U < 0.5) == (V < 0.5)); C = put(q1, D["quarterly"][0]); C = put(~q1, D["quarterly"][1])
            for (cu, cv_) in [(0.13, 0.25), (0.37, 0.25), (0.25, 0.42), (0.63, 0.75), (0.87, 0.75), (0.75, 0.92)]:
                C = put(((U - cu) / 0.07) ** 2 + ((V - cv_) / 0.10) ** 2 < 1, D["charge"])
            for (cu, cv_) in [(0.75, 0.15), (0.75, 0.30), (0.25, 0.65), (0.25, 0.80)]:
                C = put((np.abs(U - cu) < 0.15) & (np.abs(V - cv_) < 0.045), D["charge"])
        if D.get("dots"):
            for (cu, cv_) in [(0.22, 0.28), (0.56, 0.28), (0.39, 0.70)]:
                C = put((np.abs(U - cu) / 0.09 + np.abs(V - cv_) / 0.20) < 1, D["dots"])
        if D.get("band"): C = put(np.abs(V - 0.5) < 0.17, D["band"])
        if D.get("pale"): C = put(np.abs(U - 0.5) < 0.17, D["pale"])
        shade = (1 - 0.18 * np.cos(U * math.pi * 1.5 - phase * 2 * math.pi) * np.clip(U, 0, 1)).astype(np.float32)
        C = C * shade[..., None]
        k_ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2.4 * ss) | 1, int(2.4 * ss) | 1))
        L = cv2.subtract(cv2.dilate(flag, k_), cv2.erode(flag, k_))
        cv2.line(L, P(fx, top - 1.5 * ss), P(fx, H_ - 5 * ss), 255, int(2.0 * ss), cv2.LINE_AA, shift=4)
        cv2.circle(L, P(fx, top - 2.0 * ss), int(1.9 * ss * 16), 255, -1, cv2.LINE_AA, shift=4)
        ds = lambda z: cv2.resize(z, (W_ // ss, H_ // ss), interpolation=cv2.INTER_AREA)
        Af = ds(flag.astype(np.float32) / 255.0); Cf = ds(C * (flag.astype(np.float32) / 255.0)[..., None]) / np.maximum(Af[..., None], 1e-4)
        Lf = ds(L.astype(np.float32) / 255.0)
        return dict(A=Af, C=Cf, L=Lf, foot=(fx / ss, H_ / ss - 5), ink=np.float32(D.get("ink", [36, 22, 12])), sh=cv2.GaussianBlur(np.maximum(Af, Lf), (0, 0), 1.8))
    def paste(s, img, cov, name, x, y, a, t=0.0, ph0=0.0):
        if a <= 0.003: return
        f = ((t * 0.9 + ph0) % 1.0) * s.NPH; i0 = int(f) % s.NPH; i1 = (i0 + 1) % s.NPH; wt = f - int(f)
        S0, S1 = s.spr[name][i0], s.spr[name][i1]
        h, w = S0["A"].shape; ox, oy = x - S0["foot"][0], y - S0["foot"][1]
        x0, y0 = int(math.floor(ox)) - 4, int(math.floor(oy)) - 4; x1, y1 = x0 + w + 12, y0 + h + 12
        Hh, Ww = img.shape[:2]
        if x0 < 0 or y0 < 0 or x1 > Ww or y1 > Hh: return
        M = np.float32([[1, 0, ox - x0], [0, 1, oy - y0]]); sz = (x1 - x0, y1 - y0)
        g = lambda k: cv2.warpAffine(S0[k] * (1 - wt) + S1[k] * wt, M, sz)
        Aw, Lw, Sw, Cw = g("A") * a, g("L") * a, g("sh") * a, g("C")
        roi = img[y0:y1, x0:x1]
        shd = cv2.warpAffine(Sw, np.float32([[1, 0, 2.5], [0, 1, 3.0]]), sz) * 0.34; roi *= 1 - shd[..., None]
        roi[...] = roi * (1 - Aw[..., None] * 0.96) + Cw * Aw[..., None] * 0.96
        comp_ink(roi, np.clip(Lw, 0, 1) * 0.92, S0["ink"], 0.65)
        cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], np.maximum(Aw, Lw))

class Stakes:
    """double staggered row of sharpened stakes (thick dark strokes ~3x18 px) driven in one after another; can be lifted (fade)."""
    def __init__(s, st):
        s.q = q = {**dict(spacing=9.0, length=18.0, width=3.0, lean_deg=24, row_gap=7.0, plant_s=0.4, lift_s=0.3, ink=[38, 24, 14], t_off=1e9, order="centre"), **st}
        P = A.catmull([list(p) for p in q["points"]], 30) if len(q["points"]) > 2 else np.float32(q["points"])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(seg)]); L = cum[-1]
        rng = np.random.default_rng(q.get("seed", 3)); s.items = []
        for row in (0, 1):
            n = max(2, int(L / q["spacing"]))
            for i in range(n):
                sv = (i + 0.5 * row + 0.25) / n * L; px, py = np.interp(sv, cum, P[:, 0]), np.interp(sv, cum, P[:, 1])
                k = min(len(P) - 2, int(np.searchsorted(cum, sv))); tg = P[k + 1] - P[k]; tg = tg / (np.linalg.norm(tg) + 1e-6); nrm = np.float32([tg[1], -tg[0]])
                if nrm[1] > 0: nrm = -nrm                         # normal points north (towards the enemy)
                base = np.float32([px, py]) - nrm * q["row_gap"] * row + rng.uniform(-1.0, 1.0, 2)
                s.items.append((base, nrm, rng.uniform(0.85, 1.12), rng.uniform(-9, 9), abs(sv / L - 0.5) if q["order"] == "centre" else sv / L))
        s.items.sort(key=lambda z: z[4]); s.n = len(s.items)
        B = np.float32([it[0] for it in s.items]); s.bb = (B.min(0) - 28).astype(int), (B.max(0) + 28).astype(int)
    def draw(s, img, cov, t):
        q = s.q
        if t < q["t_on"]: return
        fade = 1 - sstep((t - q["t_off"]) / q["lift_s"])
        if fade <= 0: return
        pr = (t - q["t_on"]) / q["plant_s"]
        (x0, y0), (x1, y1) = s.bb; H, W = img.shape[:2]; x0, y0, x1, y1 = clip_box(int(x0), int(y0), int(x1), int(y1), W, H); ss = 3
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8)
        for i, (base, nrm, jl, ja, _) in enumerate(s.items):
            v = min(1.0, max(0.0, pr * s.n * 0.5 - i * 0.5 + 1.0))
            if v <= 0: break
            an = math.radians(ja + q["lean_deg"] * (1 if (i % 2) else -1) * 0.25)
            d = np.float32([nrm[0] * math.cos(an) - nrm[1] * math.sin(an), nrm[0] * math.sin(an) + nrm[1] * math.cos(an)])
            d = np.float32([d[0] * 0.55, d[1]]); d /= np.linalg.norm(d)
            L = q["length"] * jl * (0.3 + 0.7 * sstep(v)); b = (base - [x0, y0]) * ss; tip = b + d * L * ss
            pts = np.int32([(b + np.float32([-d[1], d[0]]) * q["width"] * 0.5 * ss) * 16, (b - np.float32([-d[1], d[0]]) * q["width"] * 0.5 * ss) * 16,
                            (tip - np.float32([-d[1], d[0]]) * q["width"] * 0.3 * ss) * 16, tip * 16 + d * 2.5 * ss * 16, (tip + np.float32([-d[1], d[0]]) * q["width"] * 0.3 * ss) * 16])
            cv2.fillPoly(m, [pts], 255, cv2.LINE_AA, shift=4)
        a = cv2.resize(m.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA) * fade
        roi = img[y0:y1, x0:x1]
        sh = cv2.warpAffine(cv2.GaussianBlur(a, (0, 0), 1.4), np.float32([[1, 0, 2.5], [0, 1, 2.5]]), (x1 - x0, y1 - y0)) * 0.35
        roi *= 1 - sh[..., None]
        comp_ink(roi, a * 0.95, q["ink"], 0.75); cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], a)

class Volley:
    """inked arrow-flight arcs drawn src->dst, staggered; arrow-fall stipple at the target; dries and fades."""
    def __init__(s, v, rng):
        s.q = q = {**dict(n=10, dur=0.34, hold=0.25, fade=0.45, spread_src=12.0, spread_dst=24.0, stagger=0.26, bulge=0.24, width=1.5, ink=[60, 28, 14], op=0.82, head=5.0,
                          side=1, hits=26, hit_spread=[34, 16]), **v}
        s.arcs = []
        for i in range(q["n"]):
            s0 = np.float32(q["src"]) + rng.normal(0, q["spread_src"], 2) * [1.0, 0.5]; d0 = np.float32(q["dst"]) + rng.normal(0, q["spread_dst"], 2) * [1.0, 0.45]
            mid = (s0 + d0) / 2; dv = d0 - s0; nrm = np.float32([-dv[1], dv[0]]) / (np.linalg.norm(dv) + 1e-6)
            cpt = mid + nrm * np.linalg.norm(dv) * q["bulge"] * q["side"] * rng.uniform(0.75, 1.25)
            uu = np.linspace(0, 1, 40)[:, None]; pts = (1 - uu) ** 2 * s0 + 2 * (1 - uu) * uu * cpt + uu ** 2 * d0
            s.arcs.append((q["t0"] + rng.uniform(0, q["stagger"]), pts.astype(np.float32)))
        s.hits = [(np.float32(q["dst"]) + rng.normal(0, 1, 2) * q["hit_spread"], rng.uniform(-0.5, 0.5), q["t0"] + q["dur"] + rng.uniform(0, q["stagger"] + 0.1)) for _ in range(q["hits"])]
        P = np.concatenate([a[1] for a in s.arcs] + [np.float32([h[0] for h in s.hits])]); s.bb = (P.min(0) - 14).astype(int), (P.max(0) + 14).astype(int)
        s.t_end = max(a[0] for a in s.arcs) + q["dur"] + q["hold"] + q["fade"] + 0.3
    def draw(s, img, cov, t):
        q = s.q
        if t < q["t0"] or t > s.t_end: return
        (x0, y0), (x1, y1) = s.bb; Hh, Ww = img.shape[:2]; x0, y0, x1, y1 = clip_box(int(x0), int(y0), int(x1), int(y1), Ww, Hh); ss = 3
        m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.float32)
        for ta, pts in s.arcs:
            age = t - ta
            if age <= 0: continue
            hd = min(1.0, age / q["dur"]); a = 1 - sstep((age - q["dur"] - q["hold"]) / q["fade"])
            if a <= 0: continue
            k = max(2, int(hd * (len(pts) - 1)) + 1); k0 = max(0, int(sstep((age - q["dur"] * 0.4) / (q["dur"] * 1.4)) * (len(pts) - 6)))
            seg = (pts[k0:k] - [x0, y0]) * ss
            if len(seg) < 2: continue
            lay = np.zeros_like(m)
            cv2.polylines(lay, [np.int32(seg * 16)], False, 1.0, max(1, int(q["width"] * ss)), cv2.LINE_AA, shift=4)
            p1 = seg[-1]; p0 = seg[max(0, len(seg) - 4)]; dv = (p1 - p0) / (np.linalg.norm(p1 - p0) + 1e-6)
            for sg in (1, -1):
                rot = np.float32([dv[0] * math.cos(2.55) - sg * dv[1] * math.sin(2.55), sg * dv[0] * math.sin(2.55) + dv[1] * math.cos(2.55)])
                cv2.line(lay, tuple((p1 * 16).astype(int)), tuple(((p1 + rot * q["head"] * ss) * 16).astype(int)), 1.0, max(1, int(q["width"] * ss)), cv2.LINE_AA, shift=4)
            m = np.maximum(m, lay * a)
        for (p, lean, th) in s.hits:
            age = t - th
            if age <= 0: continue
            a = sstep(age / 0.08) * (1 - sstep((age - 0.5) / 0.5))
            if a <= 0: continue
            c = (p - [x0, y0]) * ss; dv = np.float32([lean, -1.0]); dv /= np.linalg.norm(dv)
            lay = np.zeros_like(m); cv2.line(lay, tuple((c * 16).astype(int)), tuple(((c + dv * 4.5 * ss) * 16).astype(int)), 1.0, max(1, int(1.3 * ss)), cv2.LINE_AA, shift=4)
            m = np.maximum(m, lay * a)
        al = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA) * q["op"]
        roi = img[y0:y1, x0:x1]; comp_ink(roi, al, q["ink"], 0.55); cov[y0:y1, x0:x1] = np.maximum(cov[y0:y1, x0:x1], al)

class Arrow:
    """movement arrow: the locked MapLight nib route + inked arrowhead that opens when the nib arrives."""
    def __init__(s, ar, ctx, rng):
        s.q = q = {**dict(width=5.0, head_px=20.0, head_s=0.14, fade_at=None, fade_s=0.4), **ar}
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
            m = np.zeros(((y1 - y0) * ss, (x1 - x0) * ss), np.uint8); c = (s.tip - [x0, y0]) * ss; dv = s.dirv; pts = []
            for sg in (1, -1):
                an = sg * 0.48; r_ = np.float32([dv[0] * math.cos(an) - dv[1] * math.sin(an), dv[0] * math.sin(an) + dv[1] * math.cos(an)]); pts.append(c - r_ * L * hv * ss)
            tri = np.int32([c * 16, pts[0] * 16, (c - dv * L * 0.62 * hv * ss) * 16, pts[1] * 16]); cv2.fillPoly(m, [tri], 255, cv2.LINE_AA, shift=4)
            a = cv2.resize(m.astype(np.float32) / 255.0, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
            wet = math.exp(-max(0.0, t - q["t1"]) / 0.7); col = np.float32(s.ink["wet_color"]) * wet + np.float32(s.ink["dry_color"]) * (1 - wet)
            roi = img[y0:y1, x0:x1]; comp_ink(roi, a * 0.92, col, 0.6)
        if before is not None: img[...] = before + (img - before) * fa

class Labels:
    """code-set period-font labels: left-to-right write-on (wet ink drying), strong parchment halo, clamped inside the plate,
    and faded as they approach the camera viewport edge."""
    def __init__(s, labels, size, fonts, margin=22):
        H, W = size; s.items = []; s.report = []
        for L in labels:
            q = {**dict(size=57, rot=0, t_on=0.0, t_in=0.55, tracking=0.08, color=[34, 20, 10], wet=[12, 6, 2], halo=[240, 228, 196], halo_op=0.82, font="sc", op=0.95), **L}
            S = 3; f = ImageFont.truetype(fonts[q["font"]], int(q["size"] * S))
            txt = q["text"]; tr = q["tracking"] * q["size"] * S
            widths = [f.getlength(ch) for ch in txt]; tw = int(sum(widths) + tr * (len(txt) - 1)) + 60; th = int(q["size"] * S * 1.5) + 40
            im = Image.new("L", (tw, th), 0); d = ImageDraw.Draw(im); x = 30
            for ch, wd in zip(txt, widths): d.text((x, 20), ch, font=f, fill=255); x += wd + tr
            a = np.asarray(im).astype(np.float32) / 255.0
            ys, xs = np.where(a > 0.02); a = a[max(0, ys.min() - 30):ys.max() + 30, max(0, xs.min() - 30):xs.max() + 30]
            reveal = np.tile(np.linspace(0, 1, a.shape[1], dtype=np.float32)[None, :], (a.shape[0], 1))
            if q["rot"]:
                rot = lambda z: np.asarray(Image.fromarray(z).rotate(q["rot"], resample=Image.BICUBIC, expand=True)).astype(np.float32)
                a = rot((a * 255).astype(np.uint8)) / 255.0; reveal = rot(reveal.astype(np.float32))
            a = cv2.resize(a, (a.shape[1] // S, a.shape[0] // S), interpolation=cv2.INTER_AREA); reveal = cv2.resize(reveal, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
            pd = int(q["size"] * 0.95); a = cv2.copyMakeBorder(a, pd, pd, pd, pd, cv2.BORDER_CONSTANT, value=0)   # v2b: room for the wide halo (v2 clipped it to a hard box)
            reveal = cv2.copyMakeBorder(reveal, pd, pd, pd, pd, cv2.BORDER_REPLICATE)
            h, w = a.shape
            halo = np.clip(cv2.GaussianBlur(cv2.dilate(a, np.ones((5, 5), np.uint8)), (0, 0), q["size"] * 0.10) * 2.6, 0, 1)
            halo = np.maximum(halo, np.clip(cv2.GaussianBlur(a, (0, 0), q["size"] * 0.28) * 2.0, 0, 1) * 0.6)
            ys, xs = np.where(np.maximum(a, halo) > 0.05); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max(), ys.max()
            x0, y0 = int(round(q["xy"][0] - w / 2)), int(round(q["xy"][1] - h / 2))
            x0 = min(max(x0, margin - bx0), W - margin - bx1); y0 = min(max(y0, margin - by0), H - margin - by1)   # keep inside the frame
            s.items.append(dict(q=q, a=a, halo=halo, rev=reveal, x0=x0, y0=y0, bb=(x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)))
            s.report.append((txt, (x0 + bx0, y0 + by0, x0 + bx1, y0 + by1)))
    def draw(s, img, cov, t, view):
        H, W = img.shape[:2]
        for it in s.items:
            q = it["q"]; p = (t - q["t_on"]) / q["t_in"]
            if p <= 0: continue
            vx0, vy0, vx1, vy1 = view[:4]; bx0, by0, bx1, by1 = it["bb"]
            marg = min(bx0 - vx0, vx1 - bx1, by0 - vy0, vy1 - by1)
            ef = sstep((marg + 6) / 26.0) if (vx1 - vx0) < W - 2 else 1.0
            if q.get("hide_zoom") and view[4] > q["hide_zoom"][0]: ef *= 1 - sstep((view[4] - q["hide_zoom"][0]) / (q["hide_zoom"][1] - q["hide_zoom"][0]))
            if ef <= 0: continue
            fe = 0.18; rv = np.clip((p * (1 + fe) - it["rev"]) / fe, 0, 1)
            h, w = it["a"].shape; y0, x0 = it["y0"], it["x0"]
            sy0, sx0 = max(0, -y0), max(0, -x0); sy1, sx1 = min(h, H - y0), min(w, W - x0)
            roi = img[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]; sl = (slice(sy0, sy1), slice(sx0, sx1))
            hv = np.clip(rv * 1.4, 0, 1)[sl] * it["halo"][sl] * q["halo_op"] * ef; a = it["a"][sl] * rv[sl] * q["op"] * ef
            roi[...] = roi * (1 - hv[..., None]) + np.float32(q["halo"]) * hv[..., None]
            wet = math.exp(-max(0.0, t - q["t_on"] - q["t_in"] * 0.5) / 0.5)
            col = np.float32(q["wet"]) * wet + np.float32(q["color"]) * (1 - wet)
            comp_ink(roi, a, col, 0.8)
            cov[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1] = np.maximum(cov[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1], np.maximum(hv, a))

class Camera:
    def __init__(s, keys, plate_wh, out_wh, ss=2):
        s.keys = keys; s.PW, s.PH = plate_wh; s.OW, s.OH = out_wh; s.ss = ss; s.s0 = s.OW / s.PW
    def M(s, t):
        cx, cy, z = pchip_keys(s.keys, t, 3); sc = s.s0 * max(1.0, z)
        hw, hh = s.OW / sc / 2, s.OH / sc / 2
        cx = min(max(cx, hw), s.PW - hw); cy = min(max(cy, hh), s.PH - hh); k = sc * s.ss
        return np.float32([[k, 0, s.OW * s.ss / 2 - k * cx], [0, k, s.OH * s.ss / 2 - k * cy]]), (cx, cy, z, (cx - hw, cy - hh, cx + hw, cy + hh, z))
    def apply(s, img, t):
        M, st = s.M(t)
        big = cv2.warpAffine(img, M, (s.OW * s.ss, s.OH * s.ss), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        return cv2.resize(big, (s.OW, s.OH), interpolation=cv2.INTER_AREA), st

def build(cfg, root):
    pl = cv2.cvtColor(cv2.imread(os.path.join(root, cfg["plate"])), cv2.COLOR_BGR2RGB).astype(np.float32); H, W = pl.shape[:2]
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32); ctx = dict(H=H, W=W, X=X, Y=Y, plate=pl, half=4.0)
    seed = cfg.get("seed", 1415)
    ban = Banners(cfg["banners"])
    units = [Mass(u, np.random.default_rng([seed, 10, i]), ban) for i, u in enumerate(cfg["units"])]
    stakes = [Stakes(s_) for s_ in cfg.get("stakes", [])]
    vol = [Volley(v, np.random.default_rng([seed, 20, i])) for i, v in enumerate(cfg.get("volleys", []))]
    arrows = [Arrow(a, ctx, np.random.default_rng([seed, 30, i])) for i, a in enumerate(cfg.get("arrows", []))]
    labels = Labels(cfg.get("labels", []), (H, W), cfg["fonts"])
    mk = cfg.get("marker"); ink = None
    if mk: ink = A.MapInk(ctx, np.ones((H, W), np.float32), 1.0, dict(stamps=[{**dict(style="icon"), **mk}]), np.random.default_rng([seed, 40]))
    bk = None
    if mk and mk.get("backing") is not None:                                  # v2b: parchment roundel under the icon so steel reads on indigo (lands with the stamp)
        q = {**dict(col=[232, 214, 172], op=0.8, r=1.1, ring=[44, 26, 12], ring_op=0.8, ring_w=2.0, land=mk.get("drop_s", 0.42)), **mk["backing"]}
        R0 = mk["radius"] * q["r"]; cx, cy = mk["xy"]; e = int(R0 + 12); bx0, by0, bx1, by1 = clip_box(int(cx) - e, int(cy) - e, int(cx) + e + 1, int(cy) + e + 1, W, H)
        yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float32); dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - R0
        dd = dd - 1.6 * A.pnoise(np.random.default_rng([seed, 41]), by1 - by0, bx1 - bx0, 18, 3, 2.4)
        disc = np.clip(0.5 - dd / 1.2, 0, 1).astype(np.float32); rg = np.clip(1 - np.abs(dd + 2.2) / (q["ring_w"] * 0.6), 0, 1).astype(np.float32)
        bk = (q, (bx0, by0, bx1, by1), disc, rg)
    def backing(img, cov, t):
        q, (bx0, by0, bx1, by1), disc, rg = bk; age = t - mk["t_on"] - q["land"]
        if age < -0.03: return
        a = sstep((age + 0.03) / 0.06); roi = img[by0:by1, bx0:bx1]
        sh = cv2.warpAffine(cv2.GaussianBlur(disc, (0, 0), 3.0), np.float32([[1, 0, 3], [0, 1, 4]]), (bx1 - bx0, by1 - by0)) * 0.35 * a
        roi *= 1 - sh[..., None]
        A_ = disc * q["op"] * a; roi[...] = roi * (1 - A_[..., None]) + np.float32(q["col"]) * A_[..., None]
        comp_ink(roi, rg * q["ring_op"] * a, q["ring"], 0.6); cov[by0:by1, bx0:bx1] = np.maximum(cov[by0:by1, bx0:bx1], A_)
    cam = Camera(cfg["camera"], (W, H), tuple(cfg["size"]), cfg.get("cam_ss", 2))
    layers = cfg.get("order", ["labels", "stakes", "units", "arrows", "volleys", "marker"])
    byid = {u.u["id"]: u for u in units}
    def frame(t):
        img = pl.copy(); cov = np.zeros((H, W), np.float32); view = cam.M(t)[1][3]
        for L in layers:
            if L == "labels": labels.draw(img, cov, t, view)
            elif L == "stakes": [s_.draw(img, cov, t) for s_ in stakes]
            elif L == "units": [u.draw(img, cov, t, ban) for u in units]
            elif L.startswith("units:"): [byid[i].draw(img, cov, t, ban) for i in L[6:].split(",")]
            elif L == "arrows": [a.draw(img, cov, t) for a in arrows]
            elif L == "volleys": [v.draw(img, cov, t) for v in vol]
            elif L == "marker" and ink is not None:
                if bk is not None: backing(img, cov, t)
                ink.overlay(img, t)
        out, st = cam.apply(np.clip(img, 0, 255), t)
        return img, out, st, cov
    return pl, frame, labels

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--stills", default=None); ap.add_argument("--times", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--labels-report", action="store_true")
    a = ap.parse_args(); root = os.path.dirname(os.path.abspath(__file__))
    cfg = json.load(open(a.config)); pl, frame, labels = build(cfg, root)
    if a.labels_report:
        for txt, bb in labels.report: print("label", txt, bb)
    fps, dur = cfg["fps"], cfg["duration"]; OW, OH = cfg["size"]
    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
        for t in [float(x) for x in a.times.split(",")]:
            _, out, st, _ = frame(t); cv2.imwrite(os.path.join(a.stills, f"t{t:05.2f}.png"), cv2.cvtColor(np.clip(np.round(out), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
        return
    outp = a.out or os.path.join(root, cfg["out_dir"], cfg["name"] + ".mp4")
    if os.path.exists(outp): raise SystemExit(f"refusing to overwrite {outp}")
    wr = A.ffmpeg_writer(outp, OW, OH, fps); fh = hashlib.sha256()
    for i in range(int(round(fps * dur))):
        t = i / fps; img, out, st, cov = frame(t)
        o8 = np.clip(np.round(out), 0, 255).astype(np.uint8); fh.update(o8.tobytes()); wr.stdin.write(o8.tobytes())
        if i % 30 == 0: print(f"f{i} t={t:.2f} cam=({st[0]:.0f},{st[1]:.0f},{st[2]:.2f})", flush=True)
    wr.stdin.close(); rc = wr.wait(); print("frames_sha256", fh.hexdigest())
    if rc: raise SystemExit(f"ffmpeg rc={rc}")

if __name__ == "__main__": main()
