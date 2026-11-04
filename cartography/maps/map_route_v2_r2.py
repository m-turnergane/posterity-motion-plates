#!/usr/bin/env python3
"""map_route_v2_r2 -- r2 of map_route_v2 (Vellum review). Copy of map_route_v2.py; v2 is untouched.
r2 changes: nib ~2x + dark ink halo underlay (soft, ~2-3 px, 60%); claimed ink = bright vermilion; longer dashes (per
chain `dash`); rings ~2x (per-stop `ring_r`/`ring_w` overrides where two pins are too close for 2x); arrowheads scale with
the nib; labels 1.5x with a soft parchment halo; region labels for OMIT rows whose MAP-PLACES text allows a label
(Glamorgan, Ireland; no pin); style A realm palette re-valued (lightness separation, same hues); contrast + realm-value
proofs; 360x640 phone crops.  Outputs carry an _r2 suffix.

map_route_v2 -- Map 2a / 2b stills on the v2 basemap modes (Posterity engine R&D).  STILLS ONLY (no animation yet).

    python map_route_v2.py configs/<map>_v2.json --modes realms_worn,campaign_atlas --outdir style/

Builds on v1 (imported read-only): projection, control-point fit, MAP-PLACES-v1 authority check, Wikidata P625 coords,
IM Fell labels, pixel-density guardrail.  New in v2:
  * basemap from map_modes_v2 (mode per shot: `mode`, or `mode_from`/`mode_to`/`xfade_t` crossfade), realms from
    REALMS-1327-v1 (OHM CC0 + hand-coarse, see sources/realms/) -- raster-verified with verify_realms_1327.check_raster;
  * GEOGRAPHIC route splines: least-cost paths (scipy dijkstra, 8-neighbour, plate/4 grid).  Land legs pay for height,
    slope and water (they go round the Alps / Massif Central / Pyrenees and never cross open water); sea legs may
    only use water (+ the endpoint harbour discs) and keep off the coast.  Gaussian-smoothed with endpoints pinned, then
    re-checked; sigma is reduced until every assertion passes (land/sea pixel counts go into the proofs);
  * hand-inked stroke: stamped nib at 4x supersample, width +-25% slow noise, feathered bleed + grain; documented legs
    solid iron-gall, claimed legs (Fieschi) dashed in a vermilion pigment; tapered tip + small arrowhead at arrival;
    lines start/stop EXACTLY on the pin ring's outer edge (dash pattern fitted so both ends are ink);
  * labels auto-placed (8 sides x gaps) so no line, ring or other label touches them; leader fallback.
NOTE: the stroke is a v2 renderer, not the locked house-map-inknib-dashed-v1 MapLight nib (that preset is untouched).
"""
import argparse, hashlib, json, math, os, sys
import numpy as np, cv2
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import map_modes_v2 as MM                                   # noqa: E402
import verify_realms_1327 as VR                             # noqa: E402
V1 = MM.V1; ENG = V1.ENG; guardrails = V1.guardrails

INK = {"documented": dict(col=[34, 28, 30], dash=None), "claimed": dict(col=[252, 102, 46], dash=[30.0, 14.0])}
HALO_COL = [22, 16, 14]; HALO_OPACITY = 0.60; HALO_DILATE_PX = 3; HALO_SIGMA = 0.9
LABEL_HALO_COL = [238, 226, 194]
# style A r2 palette: same hues as the worn house palette, re-valued so neighbours separate in LIGHTNESS
# (Rec.601 luma of the pigment: england 58 dark | france 117 mid | empire 174 light | scotland 136 | castile 76 dark |
#  aragon 158 light | portugal 113 mid | england_light (Gascony) 115 | france_fam 147)
REALM_COL_A_R2 = {"england": [108, 38, 28], "england_light": [170, 96, 70], "scotland": [156, 124, 150],
                  "france": [92, 120, 170], "france_fam": [136, 148, 174], "empire": [188, 182, 112],
                  "castile": [112, 58, 70], "aragon": [198, 154, 76], "portugal": [92, 124, 108]}
MM.REALM_COL_A = REALM_COL_A_R2                              # runtime override for this process only (file untouched)
LABEL_INK = [52, 30, 20]
REALM_WORDS = ["england", "france", "scotland", "empire", "imperial", "flanders", "gascony", "brittany", "burgundy", "navarre",
               "castile", "aragon", "portugal", "majorca", "provence", "dauphin", "savoy", "kingdom", "duchy", "county", "1327"]

def md5(p):
    h = hashlib.md5(); h.update(open(p, "rb").read()); return h.hexdigest()

# ------------------------------------------------------------------------------------------ routing
class Router:
    G = 4                                                       # plate px per grid cell
    def __init__(s, T, geom):
        s.T, s.geom = T, geom; H, W = T.lb.shape; g = s.G; s.h, s.w = H // g, W // g
        lf = cv2.resize(T.land, (s.w, s.h), interpolation=cv2.INTER_AREA)
        s.water = lf < 0.98                                     # land legs: any water in the cell counts as water
        s.water_strict = lf < 0.02                              # sea legs: only all-water cells are sea
        e = cv2.resize(T.elev_land, (s.w, s.h), interpolation=cv2.INTER_AREA)
        gy, gx = np.gradient(e, T.kmpp * g); slope = np.hypot(gx, gy)            # m per km
        s.c_land = (1 + 5.0 * (np.maximum(e, 0) / 1000.0) ** 1.6 + 0.012 * np.minimum(slope, 300)).astype(np.float64)
        s.d_coast_km = cv2.distanceTransform(s.water_strict.astype(np.uint8), cv2.DIST_L2, 5) * T.kmpp * g   # sea cell -> land
        Y, X = np.mgrid[0:s.h, 0:s.w]; s.Y, s.X = Y, X
        s.border = np.minimum(np.minimum(X, s.w - 1 - X), np.minimum(Y, s.h - 1 - Y))
        s.drawn = []                                            # previous legs (plate px polylines)

    def nearest_sea_cell(s, xy):
        ys, xs = np.nonzero(s.water_strict); d = np.hypot((xs + 0.5) * s.G - xy[0], (ys + 0.5) * s.G - xy[1]); i = int(d.argmin())
        return ys[i], xs[i], float(d[i])

    def snap_sea(s, xy, clear_cells=4):
        """nearest open-water cell centre with >= clear_cells of sea round it (for a sea-leg via anchor)."""
        deep = cv2.distanceTransform(s.water_strict.astype(np.uint8), cv2.DIST_L2, 5) >= clear_cells + 0.5
        ys, xs = np.nonzero(deep); d = np.hypot((xs + 0.5) * s.G - xy[0], (ys + 0.5) * s.G - xy[1]); i = int(d.argmin())
        return np.float64([(xs[i] + 0.5) * s.G, (ys[i] + 0.5) * s.G]), float(d[i])

    def _graph(s, cost):
        h, w = s.h, s.w; idx = np.arange(h * w).reshape(h, w); rows, cols, vals = [], [], []
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            ys, ye = 0, h - dy; xs, xe = max(0, -dx), w - max(0, dx)
            a = idx[ys:ye, xs:xe]; b = idx[ys + dy:ye + dy, xs + dx:xe + dx]
            ca = cost[ys:ye, xs:xe]; cb = cost[ys + dy:ye + dy, xs + dx:xe + dx]
            v = 0.5 * (ca + cb) * math.hypot(dx, dy); ok = np.isfinite(v)
            rows += [a[ok], b[ok]]; cols += [b[ok], a[ok]]; vals += [v[ok], v[ok]]
        r, c, v = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
        return coo_matrix((v, (r, c)), shape=(h * w, h * w)).tocsr()

    def _prox(s, pts_px, rad_px):
        """distance (grid cells) from each cell to a set of plate-px points (via a raster)."""
        m = np.ones((s.h, s.w), np.uint8)
        for p in pts_px:
            cv2.circle(m, (int(round(p[0] / s.G)), int(round(p[1] / s.G))), max(0, int(rad_px / s.G)), 0, -1)
        return cv2.distanceTransform(m, cv2.DIST_L2, 5)

    def cost(s, kind, a, b, others, harbour, extra=(), pin_ends=(True, True)):
        """kind land|sea; a,b endpoints (plate px); others: [(xy, r_edge)] pins to keep clear; harbour: {i: r_px}."""
        c = s.c_land.copy() if kind == "land" else np.ones((s.h, s.w))
        if kind == "land":
            c[s.water] = 80.0
        else:
            c = 1.0 + 4.0 * np.exp(-s.d_coast_km / 6.0)               # keep off the coast (~10-20 km sea room)
            c[~s.water_strict] = np.inf
            for xy, r in harbour:                                     # embark / land inside the endpoint harbour disc
                d = np.hypot(s.X - xy[0] / s.G, s.Y - xy[1] / s.G); c[(d * s.G <= r - 2.83) & ~s.water_strict] = 3.0
                wy, wx, _ = s.nearest_sea_cell(xy); m = np.zeros((s.h, s.w), np.uint8)     # guaranteed corridor to open water
                cv2.line(m, (int(xy[0] / s.G), int(xy[1] / s.G)), (int(wx), int(wy)), 1, 1); c[(m > 0) & ~s.water_strict] = 3.0
        c = c + np.where(s.border < 3, 60.0, 0.0)
        for xy, r in others:
            d = np.hypot(s.X - xy[0] / s.G, s.Y - xy[1] / s.G) * s.G - r       # plate px from the ring edge
            c = c + np.where(d < 5, 400.0, 6.0 * np.exp(-np.maximum(d, 0) / 10.0))
        drawn = list(s.drawn) + list(extra)
        if drawn:
            m = np.ones((s.h, s.w), np.uint8)
            for P in drawn:
                cv2.polylines(m, [np.int32(np.round(P / s.G))], False, 0, 1)
            d = cv2.distanceTransform(m, cv2.DIST_L2, 5) * s.G
            near_end = np.zeros((s.h, s.w), bool)
            for p, isp in zip((a, b), pin_ends):
                near_end |= np.hypot(s.X - p[0] / s.G, s.Y - p[1] / s.G) * s.G < (26 if isp else 6)
            c = c + np.where(near_end, 0.0, 10.0 * np.exp(-d / 16.0))
        return c

    def pull(s, cells, c, tol):
        """Cost-aware string pulling (any-angle): greedily replace runs of the 8-neighbour path by a straight segment
        when the segment stays on finite-cost cells and its line-integral cost is within `tol` of the path's own cost
        over that run.  Removes the 0/45/90-degree staircase without leaving the geography the cost encodes."""
        ys, xs = cells[:, 0], cells[:, 1]; cv = c[ys, xs]
        step = np.r_[0, np.hypot(np.diff(xs), np.diff(ys))]; cum = np.cumsum(0.5 * (cv + np.r_[cv[0], cv[:-1]]) * step)
        def seg_cost(i, j):
            n = int(max(abs(xs[j] - xs[i]), abs(ys[j] - ys[i])) * 2) + 2
            t = np.linspace(0, 1, n); X = np.round(xs[i] + (xs[j] - xs[i]) * t).astype(int); Y = np.round(ys[i] + (ys[j] - ys[i]) * t).astype(int)
            v = c[Y, X]
            if not np.all(np.isfinite(v)): return np.inf
            return float(v.mean() * math.hypot(xs[j] - xs[i], ys[j] - ys[i]))
        out = [0]; i = 0; n = len(cells)
        while i < n - 1:
            best = i + 1; fails = 0
            for j in range(i + 2, n):
                if seg_cost(i, j) <= (cum[j] - cum[i]) * (1 + tol) + 1e-9: best = j; fails = 0
                else:
                    fails += 1
                    if fails > 12: break
            out.append(best); i = best
        return out

    def path(s, kind, a, b, others, harbour, extra=(), pin_ends=(True, True)):
        c = s.cost(kind, a, b, others, harbour, extra, pin_ends); Gm = s._graph(c)
        ia = int(round(a[1] / s.G)) * s.w + int(round(a[0] / s.G)); ib = int(round(b[1] / s.G)) * s.w + int(round(b[0] / s.G))
        dist, pred = dijkstra(Gm, indices=ia, return_predecessors=True)
        if not np.isfinite(dist[ib]): raise RuntimeError(f"no {kind} path between {a} and {b}")
        out = [ib]
        while out[-1] != ia: out.append(pred[out[-1]])
        out = np.array(out[::-1]); cells = np.stack([out // s.w, out % s.w], -1)
        keep = s.pull(cells, c, 0.04 if kind == "sea" else 0.02)
        P = np.float64([[(cells[k, 1] + 0.5) * s.G, (cells[k, 0] + 0.5) * s.G] for k in keep])
        P[0], P[-1] = a, b
        return P

def resample(P, step=1.0):
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]; n = max(2, int(d[-1] / step) + 1)
    t = np.linspace(0, d[-1], n); return np.stack([np.interp(t, d, P[:, 0]), np.interp(t, d, P[:, 1])], -1)

def smooth_fixed(P, sigma):
    """Gaussian smooth with the endpoints pinned (subtract the chord, odd-reflect pad, smooth, add back)."""
    if sigma < 0.5 or len(P) < 5: return P.copy()
    n = len(P); u = np.linspace(0, 1, n)[:, None]; base = P[0] * (1 - u) + P[-1] * u; r = P - base
    pad = int(3 * sigma) + 1; rp = np.concatenate([-r[1:pad + 1][::-1], r, -r[-pad - 1:-1][::-1]])
    k = np.exp(-0.5 * (np.arange(-pad, pad + 1) / sigma) ** 2); k /= k.sum()
    rs = np.stack([np.convolve(rp[:, j], k, mode="same") for j in (0, 1)], -1)[pad:pad + n]
    out = base + rs; out[0], out[-1] = P[0], P[-1]; return out

def max_turn_deg(P, step=6):
    Q = resample(P, step); v = np.diff(Q, axis=0); a = np.arctan2(v[:, 1], v[:, 0])
    if len(a) < 2: return 0.0
    da = np.degrees(np.abs((np.diff(a) + np.pi) % (2 * np.pi) - np.pi)); return float(da.max())

def teardrop(P, iv, D=70.0, k=1.0, kv=0.9):
    """Where a route touches a via and reverses (there-and-back sea leg), replace the hairpin with a rounded
    teardrop: two cubic Hermite arcs A->V->B (V = the via point, held exactly), tangent at V across the bulb.
    Returns (new P resampled at 1 px, new index of V)."""
    d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    ia = int(np.searchsorted(d, d[iv] - D)); ib = int(np.searchsorted(d, d[iv] + D))
    ia = max(ia, 2); ib = min(ib, len(P) - 3)
    A, B, V = P[ia], P[ib], P[iv]
    ta = P[ia + 2] - P[ia - 2]; ta /= np.linalg.norm(ta) + 1e-9
    tb = P[ib + 2] - P[ib - 2]; tb /= np.linalg.norm(tb) + 1e-9
    M = (A + B) / 2; u = V - M; u /= np.linalg.norm(u) + 1e-9
    w = (B - A) - np.dot(B - A, u) * u
    if np.linalg.norm(w) < 1e-3: w = np.array([-u[1], u[0]]) * np.sign(np.cross(ta, tb) or 1.0)
    tv = w / np.linalg.norm(w)
    def herm(p0, m0, p1, m1, n=200):
        t = np.linspace(0, 1, n)[:, None]; h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t; h01 = -2*t**3 + 3*t**2; h11 = t**3 - t**2
        return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1
    L1 = np.linalg.norm(V - A) * k; L2 = np.linalg.norm(B - V) * k
    c1 = herm(A, ta * L1, V, tv * L1 * kv); c2 = herm(V, tv * L2 * kv, B, tb * L2)
    head = resample(np.concatenate([P[:ia], c1]), 1.0); tail = resample(np.concatenate([c2, P[ib + 1:]]), 1.0)
    return np.concatenate([head, tail[1:]]), len(head) - 1

def trim_to_ring(P, c, r, at_start):
    """Cut the polyline exactly where it crosses the circle (c, r): returns P from/to the crossing point."""
    Q = P if at_start else P[::-1]
    d = np.hypot(*(Q - c).T); i = int(np.argmax(d >= r))
    if d[i] < r: raise RuntimeError("leg never leaves the pin ring")
    p0, p1 = Q[i - 1], Q[i]; f = p1 - p0; g = p0 - c                      # solve |p0 + t f - c| = r
    A, B, C = f @ f, 2 * f @ g, g @ g - r * r; t = (-B + math.sqrt(max(B * B - 4 * A * C, 0))) / (2 * A)
    out = np.vstack([p0 + t * f, Q[i:]]); return out if at_start else out[::-1]

# ------------------------------------------------------------------------------------------ hand-inked stroke
SS = 4
def slow_noise(rng, n, period):
    k = max(2, int(n / period) + 3); ctrl = rng.normal(0, 1, k); x = np.linspace(0, k - 1, n)
    v = np.interp(x, np.arange(k), ctrl); v = np.convolve(v, np.ones(9) / 9, mode="same"); return v / (np.abs(v).max() + 1e-6)

class Canvas:
    """Supersampled coverage canvas for one ink layer (whole plate)."""
    def __init__(s, H, W): s.H, s.W = H, W; s.m = np.zeros((H * SS, W * SS), np.uint8)
    def stamp(s, pts, widths):
        for (x, y), w in zip(pts, widths):
            r = max(0.5, w * 0.5 * SS)
            cv2.circle(s.m, (int(round(x * SS * 16)), int(round(y * SS * 16))), int(round(r * 16)), 255, -1, cv2.LINE_8, shift=4)
    def alpha(s):
        return cv2.resize(s.m, (s.W, s.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

def nib_widths(rng, n, w0, step, taper_start=True, taper_end=True):
    w = w0 * (1 + 0.25 * slow_noise(rng, n, 90 / step)); w = np.clip(w, 0.72 * w0, 1.3 * w0)
    s = np.arange(n) * step; L = s[-1] if n > 1 else 1
    if taper_start: w = w * (0.6 + 0.4 * np.clip(s / 9.0, 0, 1))
    if taper_end: w = w * (0.22 + 0.78 * np.clip((L - s) / 16.0, 0, 1))
    return w

def dash_spans(L, dash, gap, rng):
    """Dashes fitted to the leg so the first and last pieces are ink (no gap at either pin)."""
    if dash is None or L < dash * 1.5: return [(0.0, L)]
    n = max(1, int(round((L + gap) / (dash + gap)))); jit = 1 + 0.12 * rng.uniform(-1, 1, n)
    d = dash * jit; g = gap * (1 + 0.12 * rng.uniform(-1, 1, max(n - 1, 1)))[:n - 1]
    sc = L / (d.sum() + g.sum()); d *= sc; g *= sc; out, x = [], 0.0
    for i in range(n):
        out.append((x, x + d[i])); x += d[i] + (g[i] if i < n - 1 else 0)
    return out

def ink_leg(cv, P, w0, style, rng, arrow=True, step=0.25, dash=None):
    """Stamp one pin-to-pin leg (P already trimmed to the ring edges) into canvas `cv`."""
    Q = resample(P, step); n = len(Q); s = np.arange(n) * step; L = s[-1]
    w = nib_widths(rng, n, w0, step, taper_start=True, taper_end=True)
    dash = dash if dash is not None else INK[style]["dash"]
    for a, b in dash_spans(L, *(dash or [None, None]), rng):
        i0, i1 = int(a / step), min(n - 1, int(round(b / step)))
        if i1 <= i0: continue
        seg_w = w[i0:i1 + 1].copy(); m = len(seg_w); ss = np.arange(m) * step
        if dash:                                                  # each dash: nib lands and lifts (soft taper)
            seg_w *= (0.6 + 0.4 * np.clip(ss / 4.0, 0, 1)) * (0.6 + 0.4 * np.clip((ss[-1] - ss) / 4.0, 0, 1))
            if i0 == 0: seg_w[:] = np.maximum(seg_w, w[i0:i1 + 1] * 0.6)
        cv.stamp(Q[i0:i1 + 1], seg_w)
    if arrow:                                                     # small arrowhead: tip ON the ring edge
        tip = Q[-1]; k = max(1, int(10 / step)); d = Q[-1] - Q[-1 - k]; d /= np.hypot(*d) + 1e-9
        La = 2.9 * w0 + 4.0
        for sgn in (1, -1):
            ang = math.radians(26) * sgn; R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
            back = tip - (R @ d) * La; m = max(3, int(La / step)); u = np.linspace(0, 1, m)[:, None]
            seg = back * (1 - u) + tip * u
            ww = w0 * 0.85 * (0.35 + 0.65 * np.sin(np.pi * np.clip(u[:, 0] * 0.95 + 0.05, 0, 1)) ** 0.6)
            ww[-1] = min(ww[-1], w[-1])
            cv.stamp(seg, ww)
    return Q

def ring(cv, c, rc, wr, rng, step=0.25):
    n = int(2 * math.pi * rc / step) + 2; th = np.linspace(0, 2 * math.pi, n) - 1.7 + rng.uniform(-0.3, 0.3)
    rr = rc * (1 + 0.025 * slow_noise(rng, n, n / 3)); P = np.stack([c[0] + rr * np.cos(th), c[1] + rr * np.sin(th)], -1)
    w = wr * (1 + 0.2 * slow_noise(rng, n, n / 4)); w = np.clip(w, 0.8 * wr, 1.2 * wr)
    cv.stamp(P, w); return float((rr + w / 2).max()), float((rr + w / 2).mean())

def composite_ink(img, alpha, col, rng, strength=0.92):
    H, W = alpha.shape
    core = cv2.GaussianBlur(alpha, (0, 0), 0.7)
    bleed = cv2.GaussianBlur(alpha, (0, 0), 2.0) * 0.15
    grain = 1 + 0.14 * MM.pn(rng, H, W, 3, 0.6, 1.2)
    a = np.clip((core ** 0.9) * strength * grain + bleed, 0, 0.97)[..., None]
    wet = np.float32(col); return img * (1 - a) + wet * a * (0.92 + 0.08 * img / 200.0), a[..., 0]

# ------------------------------------------------------------------------------------------ labels
class LabelR2:
    """IM Fell place name (SC for places, French Canon italic for regions) with a soft parchment halo."""
    def __init__(s, text, xy, side, t_on, ink, px, region=False, gap=20.0):
        from PIL import Image, ImageDraw, ImageFont
        f = ImageFont.truetype(V1.FONT_IT if region else V1.FONT_SC, int(px))
        l, t_, r, b = f.getbbox(text); w, h = r - l, b - t_; pad = 20
        im = Image.new("L", (w + 2 * pad, h + 2 * pad), 0); ImageDraw.Draw(im).text((pad - l, pad - t_), text, font=f, fill=255)
        a = np.asarray(im, np.float32) / 255.0; x, y = xy
        ox = {"E": gap, "W": -gap - w, "N": -w / 2, "S": -w / 2, "NE": gap * 0.7, "SE": gap * 0.7, "NW": -gap * 0.7 - w, "SW": -gap * 0.7 - w, "C": -w / 2}[side]
        oy = {"E": -h / 2, "W": -h / 2, "N": -gap - h, "S": gap, "NE": -gap * 0.7 - h, "NW": -gap * 0.7 - h, "SE": gap * 0.7, "SW": gap * 0.7, "C": -h / 2}[side]
        s.x0, s.y0 = int(round(x + ox - pad)), int(round(y + oy - pad)); s.a = a
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        s.halo = np.clip(cv2.GaussianBlur(cv2.dilate(a, k), (0, 0), 3.0) * 1.5, 0, 1)
        s.ink, s.text, s.region = np.float32(ink), text, region
    def bbox(s): return s.x0, s.y0, s.x0 + s.a.shape[1], s.y0 + s.a.shape[0]
    def draw(s, img, t=10.0):
        x0, y0, x1, y1 = s.bbox(); H, W = img.shape[:2]
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        roi = img[cy0:cy1, cx0:cx1]; a = s.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; hl = s.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * 0.78
        roi[...] = roi * (1 - hl[..., None]) + np.float32(LABEL_HALO_COL) * hl[..., None]
        roi[...] = roi * (1 - 0.94 * a[..., None]) + s.ink * 0.94 * a[..., None]

def place_label(text, xy, r_edge, block, frame_ok, lpx, prefer, H, W, other_pins=(), region=False, soft=None):
    """Try 8 sides x gaps; reject any overlap with `block` (route ink, rings, other labels) or the frame margin."""
    sides = list(dict.fromkeys(prefer + ["E", "W", "N", "S", "NE", "SE", "NW", "SW"]))
    best = None
    if region: sides = ["C"] + sides
    for gap in (r_edge + 6, r_edge + 12, r_edge + 20, r_edge + 32, r_edge + 46, r_edge + 64):
        for si, sd in enumerate(sides):
            L = LabelR2(text, xy, sd, 0.0, LABEL_INK, lpx, region=region, gap=gap)
            ys, xs = np.nonzero(L.a > 0.04); x0, y0 = L.x0 + xs.min() - 3, L.y0 + ys.min() - 3; x1, y1 = L.x0 + xs.max() + 4, L.y0 + ys.max() + 4
            if not (frame_ok[0] <= x0 and x1 <= frame_ok[2] and frame_ok[1] <= y0 and y1 <= frame_ok[3]): continue
            hit = int(block[max(0, y0):y1, max(0, x0):x1].sum())
            halo_hit = int(soft[max(0, y0 - 9):y1 + 9, max(0, x0 - 9):x1 + 9].sum()) if soft is not None else 0
            def boxd(q):
                return math.hypot(max(x0 - q[0], 0, q[0] - x1), max(y0 - q[1], 0, q[1] - y1))
            own = boxd(xy)
            if any(boxd(q) < own + 6 for q in other_pins): hit += 500      # a label must read as its OWN pin's
            score = hit * 1000 + halo_hit * 0.5 + si * 2 + gap * 0.05
            if best is None or score < best[0]: best = (score, L, (x0, y0, x1, y1), sd, gap, hit)
        if best and best[5] == 0: break
    return best

# ------------------------------------------------------------------------------------------ shot
class StillShot:
    def __init__(s, cfg_path):
        cfg = json.load(open(cfg_path)); s.cfg = cfg; s.name = cfg["name"]
        s.authority = V1.check_against_authority(cfg, V1.read_places_md())
        PW, PH = cfg["plate_wh"]
        s.density = guardrails.check_pixel_density((PW, PH), cfg["out_wh"], cfg.get("push", [1.0, 1.06]), mode="refuse", name=s.name)
        s.geom = MM.V1.MapGeom(cfg, PW, PH); s.T = MM.Terrain(s.geom, cfg)
        gaz = json.load(open(V1.GAZ))["places"]
        s.cp = V1.fit_control_points(s.geom, s.T.land > 0.5, cfg["control_points"], gaz)
        s.route()

    def stop_xy(s, st):
        if st["row"] in getattr(s, "via_snap", {}): return s.via_snap[st["row"]][0]
        if "anchor_lonlat" in st: return s.geom.px(*st["anchor_lonlat"])
        g = V1.wikidata_p625(st["qid"]); return s.geom.px(g["lon"], g["lat"])

    def route(s):
        cfg, T = s.cfg, s.T; H, W = T.lb.shape; R = Router(T, s.geom); s.legs, s.pins = [], []
        chains = cfg["chains"]
        for ch in chains:                                             # all pins (for clearance), with ring sizes
            for st in ch["stops"]:
                if st.get("pin", True) and not st.get("no_stamp"):
                    rc = st.get("ring_r", ch["ring_r"]); wr = st.get("ring_w", ch["ring_w"])
                    s.pins.append(dict(row=st["row"], qid=st["qid"], label=st.get("label"), xy=s.stop_xy(st), rc=rc, wr=wr,
                                       r_edge=rc + wr / 2, style=ch["style"], side=st.get("side"), chain=ch["id"]))
        redge = {p["row"]: p["r_edge"] for p in s.pins}
        s.regions = []                                                # OMIT rows with an allowed label: region label, no pin
        for ch in chains:
            for st in ch["stops"]:
                if not st.get("pin", True) and st.get("label"):
                    ll = st.get("label_lonlat")
                    if ll: xy = s.geom.px(*ll); src = "label_lonlat"
                    else: g = V1.wikidata_p625(st["qid"]); xy = s.geom.px(g["lon"], g["lat"]); src = f"P625 {st['qid']}"
                    s.regions.append(dict(row=st["row"], qid=st["qid"], label=st["label"], xy=np.float64(xy), src=src, side=st.get("side")))
        s.via_snap = {}
        for ch in chains:                                             # sea vias: snap the illustrative anchor onto open water
            for k, st in enumerate(ch["stops"]):
                nxt = ch["stops"][k + 1] if k + 1 < len(ch["stops"]) else {}
                if not st.get("pin", True) and (st.get("leg") == "sea" or nxt.get("leg") == "sea"):
                    q, dd = R.snap_sea(s.stop_xy(st)); s.via_snap[st["row"]] = (q, dd)
        for ch in chains:
            stops = ch["stops"]; pin_idx = [i for i, st in enumerate(stops) if st.get("pin", True)]
            for a_i, b_i in zip(pin_idx[:-1], pin_idx[1:]):
                parts, kinds = [], []
                for k in range(a_i, b_i):
                    A, B = stops[k], stops[k + 1]; kind = B.get("leg", "land")
                    pa, pb = s.stop_xy(A), s.stop_xy(B)
                    others = [(p["xy"], p["r_edge"]) for p in s.pins if p["row"] not in (stops[a_i]["row"], stops[b_i]["row"])]
                    harbour = []
                    for st, p in ((A, pa), (B, pb)):
                        if st.get("pin", True) and kind == "sea":     # harbour = pin to the nearest open-water cell, +3 px
                            harbour.append((p, max(redge[st["row"]], R.nearest_sea_cell(p)[2] + 3.0)))
                        elif st.get("pin", True):
                            dcoast = float(T.d_land[int(round(p[1])), int(round(p[0]))])
                            harbour.append((p, max(redge[st["row"]], dcoast + 3.0)))
                    P = R.path(kind, pa, pb, others, harbour, extra=parts, pin_ends=(A.get("pin", True), B.get("pin", True))); parts.append(resample(P, 1.0)); kinds.append((kind, A["row"], B["row"], harbour))
                s.legs.append(dict(chain=ch["id"], style=ch["style"], w0=ch["width"], dash=ch.get("dash"), a=stops[a_i], b=stops[b_i], parts=parts, kinds=kinds,
                                   others=[(p["xy"], p["r_edge"]) for p in s.pins if p["row"] not in (stops[a_i]["row"], stops[b_i]["row"])]))
                R.drawn.append(np.concatenate(parts))
        # smooth each pin-to-pin leg (vias are not fixed points: the curve sweeps through the region), then re-check
        s.leg_proofs = []
        for lg in s.legs:
            lg["sigma"], lg["P"], lg["check"], lg["fit"] = s.fit_leg(lg)
            ra, rb = redge[lg["a"]["row"]], redge[lg["b"]["row"]]
            ca, cb = lg["P"][0], lg["P"][-1]
            lg["Pt"] = trim_to_ring(trim_to_ring(lg["P"], ca, ra, True), cb, rb, False)
            lg["r_a"], lg["r_b"] = ra, rb

    def check_leg(s, lg, P, bounds, want_mask=False):
        """Assertions per sub-leg on the centreline: land legs -> 0 samples on water (outside the endpoint harbour discs);
        sea legs -> 0 samples on land outside the endpoint harbour discs, and >= 2.5 px clear of the coast (except on
        the final 8 px approach into a harbour disc).  Also: no zigzag (max turn per 6 px < 40 deg), clear of other pins."""
        T = s.T; H, W = T.lb.shape; info = []; ok = True; badm = np.zeros(len(P), bool)
        for k, (kind, ra, rb, harbour) in enumerate(lg["kinds"]):
            i0, i1 = bounds[k], bounds[k + 1] + 1; Q = P[i0:i1]
            xi = np.clip(np.round(Q[:, 0]).astype(int), 0, W - 1); yi = np.clip(np.round(Q[:, 1]).astype(int), 0, H - 1)
            land = T.lb[yi, xi] > 0; excl = np.zeros(len(Q), bool); appr = np.zeros(len(Q), bool)
            for p, r in harbour:
                dd = np.hypot(*(Q - p).T); excl |= dd <= r; appr |= dd <= r + 8
            if kind == "land":
                b = ~land & ~excl; info.append(dict(sub=f"{ra}->{rb}", kind=kind, water_samples=int(b.sum()), n=len(Q)))
            else:
                clr = T.d_sea[yi, xi]; b = (land & ~excl) | ((clr < 2.5) & ~appr)
                info.append(dict(sub=f"{ra}->{rb}", kind=kind, land_samples_outside_harbour=int((land & ~excl).sum()),
                                 min_coast_clear_px=round(float(clr[~appr].min()) if (~appr).any() else 99.0, 2), n=len(Q),
                                 harbour_r_px=[round(float(r), 2) for _, r in harbour]))
            badm[i0:i1] |= b
        ok &= not badm.any()
        tooth = max_turn_deg(P); ok &= tooth < 40
        clear_other = min([float(np.hypot(*(P - xy).T).min()) - r for xy, r in lg["others"]] or [99.0])
        ok &= clear_other >= 3
        info.append(dict(max_turn_deg_per_6px=round(tooth, 2), min_clear_of_other_pins_px=round(clear_other, 2)))
        return (ok, info, badm) if want_mask else (ok, info)

    def fit_leg(s, lg):
        """Smooth (endpoints pinned); round any there-and-back via into a teardrop; where the curve breaks a
        land/sea rule, blend back toward the lightly-smoothed least-cost path over a soft window, then re-check.
        Sigma steps down until everything passes."""
        raw = np.concatenate([p if i == 0 else p[1:] for i, p in enumerate(lg["parts"])])
        bounds0 = np.cumsum([0] + [len(p) - (0 if i == 0 else 1) for i, p in enumerate(lg["parts"])])
        def drops(P, bounds):
            bounds = list(bounds)
            for j in range(1, len(bounds) - 1):
                if lg["kinds"][j - 1][0] == lg["kinds"][j][0]:
                    iv = bounds[j]; a = P[iv] - P[max(iv - 25, 0)]; b = P[min(iv + 25, len(P) - 1)] - P[iv]
                    cosang = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
                    if cosang < -0.3:
                        Dmax = 0.6 * min(bounds[j] - bounds[j - 1], bounds[j + 1] - bounds[j]); done = False
                        for D in sorted({min(D, Dmax) for D in (90.0, 75.0, 60.0, 48.0, 36.0, 26.0)}, reverse=True):
                            for kv in (0.9, 1.3, 1.8):
                                Q, nv = teardrop(P, iv, D, kv=kv)
                                nb = [bb if bb <= iv else bb + (len(Q) - len(P)) for bb in bounds]; nb[j] = nv
                                if s.check_leg(lg, Q, nb)[0]: P, bounds, done = Q, nb, True; break
                            if done: break
                        if not done:
                            Q, nv = teardrop(P, iv, max(min(48.0, Dmax), 12.0), kv=1.3)
                            bounds = [bb if bb <= iv else bb + (len(Q) - len(P)) for bb in bounds]; bounds[j] = nv; P = Q
            return P, np.array(bounds)
        info = None
        for sig in (24.0, 18.0, 14.0, 11.0, 8.0, 6.0):
            Sm, bounds = drops(smooth_fixed(raw, sig), bounds0); ok, info, bad = s.check_leg(lg, Sm, bounds, True)
            if ok: lg["bounds"] = bounds; return sig, Sm, info, "smooth"
            # adaptive sigma: per sample, the largest sigma whose curve is clean within +-2 sigma there
            levels = [sig] + [x for x in (18.0, 14.0, 11.0, 8.0, 6.0, 4.0, 3.0, 2.0) if x < sig]
            curves, oks = [], []
            for lv in levels:
                C = smooth_fixed(raw, lv); _, _, bd = s.check_leg(lg, C, bounds0, True)
                curves.append(C); oks.append(np.convolve(bd.astype(float), np.ones(int(4 * lv) | 1), mode="same") == 0)
            choice = np.full(len(raw), len(levels) - 1)
            for k in range(len(levels) - 1, -1, -1): choice[oks[k]] = k
            onehot = np.stack([(choice == k).astype(float) for k in range(len(levels))], -1)
            ker = np.exp(-0.5 * (np.arange(-30, 31) / 10.0) ** 2); ker /= ker.sum()
            wts = np.stack([np.convolve(np.pad(onehot[:, k], 30, mode="edge"), ker, mode="same")[30:-30] for k in range(len(levels))], -1)
            wts /= wts.sum(1, keepdims=True)
            P2 = sum(wts[:, k:k + 1] * curves[k] for k in range(len(levels)))
            P2, bounds = drops(P2, bounds0); ok, info = s.check_leg(lg, P2, bounds)
            if ok: lg["bounds"] = bounds; return sig, P2, info, f"adaptive sigma {levels[0]:g}..{levels[int(choice.max())]:g}"
        raise RuntimeError(f"leg {lg['a']['row']}->{lg['b']['row']} fails land/sea assertions at every sigma: {info}")

    # ---------------------------------------------------------------------------- render
    def render(s, mode, seed_extra=0):
        cfg, T = s.cfg, s.T; H, W = T.lb.shape; rng = np.random.default_rng([cfg["seed"], 7])
        base = MM.render_mode(T, mode, cfg["seed"]).astype(np.float32)
        img = base.copy(); proofs = dict(legs=[], pins=[], labels=[])
        leg_alpha = {}
        for li, lg in enumerate(s.legs):
            cv = Canvas(H, W); r2 = np.random.default_rng([cfg["seed"], 100 + li])
            ink_leg(cv, lg["Pt"], lg["w0"], lg["style"], r2, arrow=True, dash=lg.get("dash"))
            leg_alpha[li] = cv.alpha()
        ring_alpha = {}
        for pi, p in enumerate(s.pins):
            cv = Canvas(H, W); r_max, r_mean = ring(cv, p["xy"], p["rc"], p["wr"], np.random.default_rng([cfg["seed"], 300 + pi]))
            if p["style"] == "documented": cv.stamp([p["xy"]], [p["rc"] * 0.9])
            ring_alpha[pi] = cv.alpha(); p["r_outer_max"] = r_max
        allink = {}
        for li, lg in enumerate(s.legs): allink.setdefault(lg["style"], []).append(leg_alpha[li])
        for pi, p in enumerate(s.pins): allink.setdefault(p["style"], []).append(ring_alpha[pi])
        # dark ink halo UNDER all route ink (lines + rings + arrowheads): dilate ~2 px, soften, 60 %
        alla = np.clip(sum(sum(l) for l in allink.values()), 0, 1).astype(np.float32)
        kh = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * HALO_DILATE_PX + 1, 2 * HALO_DILATE_PX + 1))
        halo = np.clip(cv2.GaussianBlur(cv2.dilate(alla, kh), (0, 0), HALO_SIGMA) * 1.15, 0, 1) * HALO_OPACITY
        img = img * (1 - halo[..., None]) + np.float32(HALO_COL) * halo[..., None]
        ink_a = np.zeros((H, W), np.float32)
        for st, lst in allink.items():
            a = np.clip(sum(lst), 0, 1); img, aa = composite_ink(img, a, INK[st]["col"], rng, strength=0.96); ink_a = np.maximum(ink_a, aa)
        inked = img.copy()
        # labels (pins first, then OMIT-row region labels)
        frame = (70, 50, W - 70, H - 50)                                    # inside the 1.06-push crop too
        anyink = np.maximum(ink_a, halo)
        block = (cv2.dilate((anyink > 0.04).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0).astype(np.uint8)
        for p in s.pins:                                                    # keep labels off every ring disc
            cv2.circle(block, (int(round(p["xy"][0])), int(round(p["xy"][1]))), int(p["r_edge"] + 4), 1, -1)
        soft = (anyink > 0.02).astype(np.uint8)
        labs = []; lpx = cfg.get("label_px", 45)
        items = [(p, False) for p in s.pins if p.get("label")] + [(r, True) for r in s.regions]
        for p, isreg in items:
            best = place_label(p["label"], p["xy"], (6.0 if isreg else p["r_edge"]), block, frame, (cfg.get("region_label_px", lpx) if isreg else lpx),
                               [p["side"]] if p.get("side") else [], H, W,
                               other_pins=[q["xy"] for q in s.pins if q is not p], region=isreg, soft=soft)
            if best is None: raise RuntimeError(f"no in-frame spot for {p['label']}")
            sc, L, bb, sd, gap, hit = best; labs.append((L, bb))
            x0, y0, x1, y1 = bb; block[max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = 1
            proofs["labels"].append(dict(text=p["label"], row=p["row"], kind=("region (no pin)" if isreg else "pin"), side=sd, gap_px=round(gap, 1),
                                         bbox=[int(v) for v in bb], ink_px_in_bbox=hit, px=(cfg.get("region_label_px", lpx) if isreg else lpx),
                                         anchor=(p.get("src") if isreg else "pin"),
                                         in_frame=bool(frame[0] <= x0 and x1 <= frame[2] and frame[1] <= y0 and y1 <= frame[3])))
        for L, bb in labs: L.draw(img)
        for (L, bb), pr in zip(labs, proofs["labels"]):
            x0, y0, x1, y1 = bb
            pr["final_ink_px_gt0.02_in_bbox"] = int((ink_a[max(0, y0):y1, max(0, x0):x1] > 0.02).sum())
            pr["final_halo_px_gt0.02_in_bbox"] = int((halo[max(0, y0):y1, max(0, x0):x1] > 0.02).sum())
        # pin-edge proofs (each leg's own alpha): ink radial extent near each endpoint
        for li, lg in enumerate(s.legs):
            a = leg_alpha[li]; ent = dict(leg=f"{lg['a']['row']}->{lg['b']['row']}", chain=lg["chain"], style=lg["style"], w0=lg["w0"], dash=lg.get("dash"),
                                         sigma_px=round(lg["sigma"], 2), fit=lg["fit"], checks=lg["check"])
            for end, c, r in (("start", lg["P"][0], lg["r_a"]), ("end", lg["P"][-1], lg["r_b"])):
                q = lg["Pt"][0] if end == "start" else lg["Pt"][-1]
                cl_gap = abs(float(np.hypot(*(q - c))) - r)
                x0, y0 = int(c[0]) - int(r) - 12, int(c[1]) - int(r) - 12; sz = 2 * int(r) + 25
                crop = a[max(0, y0):y0 + sz, max(0, x0):x0 + sz]; up = cv2.resize(crop, None, fx=8, fy=8, interpolation=cv2.INTER_LINEAR)
                ys, xs = np.nonzero(up > 0.5); dd = np.hypot((xs + 0.5) / 8 + max(0, x0) - c[0], (ys + 0.5) / 8 + max(0, y0) - c[1])
                dmin = float(dd.min()) if len(dd) else None
                ent[end] = dict(r_edge_px=round(r, 3), centreline_gap_px=round(cl_gap, 4),
                                ink_min_dist_from_centre_px=round(dmin, 3) if dmin is not None else None,
                                ink_vs_edge_px=round(dmin - r, 3) if dmin is not None else None)
            foot = a > 0.25; Y, X = np.nonzero(foot)
            kinds = set(k[0] for k in lg["kinds"])
            hb = np.zeros(len(X), bool); ring_ex = np.zeros(len(X), bool)
            for kd in lg["kinds"]:
                for p, r in kd[3]: hb |= np.hypot(X - p[0], Y - p[1]) <= r
            for c, r in ((lg["P"][0], lg["r_a"]), (lg["P"][-1], lg["r_b"])): ring_ex |= np.hypot(X - c[0], Y - c[1]) <= r + 0.5
            on_land = T.lb[Y, X] > 0
            if kinds == {"sea"}:
                ent["ink_land_px_outside_pin_ring"] = int((on_land & ~ring_ex).sum())
                ent["ink_land_px_outside_harbour_disc"] = int((on_land & ~hb).sum())
            elif kinds == {"land"}:
                ent["ink_sea_px_outside_pin_ring"] = int((~on_land & ~ring_ex).sum())
            else:
                ent["mixed"] = True
            ent["contrast"] = contrast_along(inked, base, a, lg["Pt"], lg["w0"], s.pins)
            proofs["legs"].append(ent)
        for p in s.pins:
            proofs["pins"].append(dict(row=p["row"], qid=p["qid"], label=p["label"], xy=[round(float(v), 2) for v in p["xy"]], ring_r=p["rc"], ring_w=p["wr"],
                                       r_edge=p["r_edge"]))
        proofs["regions"] = [dict(row=r["row"], qid=r["qid"], label=r["label"], anchor=r["src"], xy=[round(float(v), 2) for v in r["xy"]], pin=False) for r in s.regions]
        out = cv2.resize(np.clip(img + 0.5, 0, 255).astype(np.uint8), tuple(cfg["out_wh"]), interpolation=cv2.INTER_AREA)
        rw = T.realm_weights()
        rv = VR.check_raster(rw, lambda lo, la: s.geom.analytic(np.float64([lo]), np.float64([la]))[0], T.lb.shape,
                             [l["text"] for l in proofs["labels"]], REALM_WORDS)
        proofs["realms_raster"] = rv
        proofs["realm_values_luma601"] = realm_values(base, rw, T)
        return out, img, proofs, ink_a

# ------------------------------------------------------------------------------------------ r2 proofs
def rel_lum(rgb):
    c = np.asarray(rgb, np.float64) / 255.0; c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c[..., 0] * 0.2126 + c[..., 1] * 0.7152 + c[..., 2] * 0.0722

def wcag(a, b):
    hi, lo = max(a, b), min(a, b); return (hi + 0.05) / (lo + 0.05)

def contrast_along(img, base, alpha, Pt, w0, pins, step=3.0):
    """WCAG luminance contrast of the inked stroke along the path (plate px), sampled every `step` px on the dashes:
       core   = median rel. luminance of stroke pixels (leg alpha > 0.75, <= 0.4 w0 from the centreline) in the RENDER;
       under  = median rel. luminance of the RAW basemap under those same core pixels (local background, no ink/halo);
       edge   = median rel. luminance of the render just outside the stroke (w0/2+0.5 .. w0/2+3.5 px; leg alpha < 0.2)
                -- i.e. what the eye actually sees beside the stroke (halo over the basemap).
       Ring discs (r_edge + 4) are excluded.  Returns min / 5th pct / median for core-vs-under and core-vs-edge."""
    H, W = alpha.shape; m = np.ones((H, W), np.uint8); cv2.polylines(m, [np.int32(np.round(Pt * 4))], False, 0, 1, cv2.LINE_8, shift=2)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    Lr, Lb = rel_lum(img), rel_lum(base)
    Q = resample(Pt, step); R = int(w0 / 2 + 6); cu, ce, where = [], [], []
    for q in Q:
        if any(np.hypot(*(q - p["xy"])) < p["r_edge"] + 4 for p in pins): continue
        x, y = int(round(q[0])), int(round(q[1])); x0, y0, x1, y1 = max(0, x - R), max(0, y - R), min(W, x + R + 1), min(H, y + R + 1)
        a = alpha[y0:y1, x0:x1]; d = dist[y0:y1, x0:x1]
        core = (a > 0.75) & (d <= max(0.4 * w0, 0.8))
        if core.sum() < 2: continue                                       # gap between dashes
        edge = (d >= w0 / 2 + 0.5) & (d <= w0 / 2 + 3.5) & (a < 0.2)
        if edge.sum() < 3: continue
        lc = float(np.median(Lr[y0:y1, x0:x1][core])); lu = float(np.median(Lb[y0:y1, x0:x1][core])); le = float(np.median(Lr[y0:y1, x0:x1][edge]))
        cu.append(wcag(lc, lu)); ce.append(wcag(lc, le)); where.append([round(float(q[0]), 1), round(float(q[1]), 1)])
    cu, ce = np.array(cu), np.array(ce)
    if not len(cu): return dict(n=0)
    return dict(n=int(len(cu)), core_vs_raw_under=dict(min=round(float(cu.min()), 2), p5=round(float(np.percentile(cu, 5)), 2), median=round(float(np.median(cu)), 2),
                                                       min_at_plate_px=where[int(cu.argmin())]),
                core_vs_edge_rendered=dict(min=round(float(ce.min()), 2), p5=round(float(np.percentile(ce, 5)), 2), median=round(float(np.median(ce)), 2),
                                           min_at_plate_px=where[int(ce.argmin())]))

def realm_values(base, rw, T):
    """Median Rec.601 luma (0-255) of the painted basemap where one realm family dominates (weight > 0.8, on land)."""
    luma = base[..., 0] * 0.299 + base[..., 1] * 0.587 + base[..., 2] * 0.114; out = {}
    for f, w in rw.items():
        m = (w > 0.8) & (T.land > 0.5) & (T.d_land > 4)
        if m.sum() > 200: out[f] = dict(luma_median=round(float(np.median(luma[m])), 1), px=int(m.sum()))
    return out

def phone_crop(out, legs, plate_wh, path, labels=()):
    """9:16 window (full height), scaled to 360x640 -- a phone preview, not a deliverable.  x chosen to keep the most
    labels whole (ties -> most route ink, then nearest the route centre)."""
    H, W = out.shape[:2]; sx = W / plate_wh[0]
    P = np.concatenate([lg["Pt"] for lg in legs]) * sx; cx = 0.5 * (P[:, 0].min() + P[:, 0].max())
    cw = int(round(H * 9 / 16)); best = None
    for x0 in range(0, W - cw + 1, 4):
        nl = sum(1 for l in labels if x0 <= l["bbox"][0] * sx and l["bbox"][2] * sx <= x0 + cw)
        ni = int(((P[:, 0] >= x0) & (P[:, 0] <= x0 + cw)).sum())
        key = (nl, ni // 200, -abs(x0 + cw / 2 - cx))
        if best is None or key > best[0]: best = (key, x0)
    x0 = best[1]
    ph = cv2.resize(out[:, x0:x0 + cw], (360, 640), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, cv2.cvtColor(ph, cv2.COLOR_RGB2BGR))
    whole = [l["text"] for l in labels if x0 <= l["bbox"][0] * sx and l["bbox"][2] * sx <= x0 + cw]
    return dict(path=path, x0=x0, crop_w=cw, scale=round(640 / H, 4), labels_whole=whole, md5=md5(path))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--modes", default="realms_worn,campaign_atlas")
    ap.add_argument("--outdir", default=os.path.join(HERE, "style")); ap.add_argument("--tag", required=True)
    ap.add_argument("--suffix", default="_r2")
    ap.add_argument("--proofs", default=os.path.join(HERE, "proofs")); a = ap.parse_args()
    S = StillShot(a.config); allp = dict(shot=S.name, density=S.density, authority=S.authority, control_points={k: v for k, v in S.cp.items() if k != "points"},
                                         modes={})
    os.makedirs(os.path.join(a.outdir, "phone"), exist_ok=True)
    for mode in a.modes.split(","):
        letter = {"realms_worn": "A_worn_house", "campaign_atlas": "B_campaign_atlas"}[mode]
        out, plate, pr, ink = S.render(mode)
        path = os.path.join(a.outdir, f"{a.tag}_style_{letter}_16x9{a.suffix}.png")
        assert not os.path.exists(path) or a.suffix, "refusing to overwrite an r1 still"
        cv2.imwrite(path, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        pr["png"] = path; pr["md5"] = md5(path)
        pr["phone"] = phone_crop(out, S.legs, S.cfg["plate_wh"], labels=pr["labels"], path=os.path.join(a.outdir, "phone", f"{a.tag}_style_{letter}{a.suffix}_phone360x640.png"))
        allp["modes"][mode] = pr; print(path, pr["md5"], flush=True)
    json.dump(allp, open(os.path.join(a.proofs, f"{S.name}_stills{a.suffix}.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))

if __name__ == "__main__":
    main()
