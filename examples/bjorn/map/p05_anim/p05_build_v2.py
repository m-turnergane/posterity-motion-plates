#!/usr/bin/env python3
"""v2 (Vellum notes 2026-11-03 07:16 EST: heavier house-oxblood stroke + parchment keyline, 85% settle, 1.5x marks, S4 nudged south).
Björn P05 atlas: register P05_KEEP.png to refpack_p05, distortion/route QA, MapTrace animation.
Atelier, 2026-11-03. Run: /workspace/mpvenv/bin/python p05_build_v2.py [--force] [--stage all|reg|anim]
Writes ONLY inside this folder. Never modifies the source plate (opened read-only; md5 checked before and after)."""
import sys, os, json, math, hashlib, subprocess, time, argparse
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
from scipy import ndimage

HERE = Path(__file__).resolve().parent
BJ = HERE.parent.parent
PLATE = BJ / "plates/P05_KEEP.png"
REFDIR = BJ / "map/refpack_p05"
REF = REFDIR / "img/bjorn_p05_9x16_ref_clean.png"
RJSON = REFDIR / "route_places_p05.json"
sys.path.insert(0, "/workspace/posterity/motion")
import guardrails

W, H, FPS, DUR = 1080, 1920, 30, 6.25
NF = int(math.ceil(DUR * FPS))            # 188 frames (6.267 s); the cut uses 17.50-23.75
Z0, Z1 = 1.00, 1.06
OX = (112, 26, 20); OX_WET = (62, 10, 6); PARCH = (238, 226, 198)
LEG_PALE = (184, 96, 80)                  # v2: same oxblood family, clearly lighter (#B86050)
# v2 stroke spec (ref px; frame px = x zoom). House route colour: motion/PRESETS.md `route.color` [112,26,20] = #701A14
W_INK, W_KEY = 11.0, 16.0                 # v1 5.0 / 8.4  -> 2.2x ink, keyline 2.5 px each side
W_PALE, W_PKEY = 6.5, 10.5                # v1 3.6 / 6.6
A_INK, A_KEY, A_PALE, A_PKEY = 1.0, 0.92, 0.92, 0.80
DASH_ON, DASH_OFF = 20.0, 13.0            # v1 13 / 9
MARK_K = 1.5                              # end-mark + fleet glyph scale vs v1
SPUR = 12.0                               # landfall spur zone (arc px from each landfall end) where the keyline may meet the coast
KEY_PAD = 1.25                            # extra clearance beyond the keyline half-width (AA + raster)

ap = argparse.ArgumentParser(); ap.add_argument("--force", action="store_true"); ap.add_argument("--stage", default="all")
ARGS = ap.parse_args()

def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def out(name):
    p = (HERE / name).resolve(); assert HERE in p.parents or p.parent == HERE, p
    if p.exists() and not ARGS.force: sys.exit(f"refusing to overwrite {p} (use --force)")
    p.parent.mkdir(parents=True, exist_ok=True); return p
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); LOG.append(s)

T0 = time.time()
PLATE_MD5 = md5(PLATE)
plate = np.array(Image.open(PLATE).convert("RGB")); ph, pw = plate.shape[:2]
ref = np.array(Image.open(REF).convert("RGB")).astype(int)
RJ = json.load(open(RJSON))
log(f"plate {PLATE.name} {pw}x{ph} md5 {PLATE_MD5}; ref {REF.name} md5 {md5(REF)}")

# ------------------------------------------------------------------ 1. sea masks + coastline control points
def plate_sea(img):
    b = cv2.GaussianBlur(img, (0, 0), 2.5).astype(int); R_, G_, B_ = b[..., 0], b[..., 1], b[..., 2]
    m = ((B_ > R_ + 8) & (B_ < 118) & (G_ < 115) & (B_ - G_ < 28)).astype(np.uint8)   # slate-teal sea (B-G ~10-16); excludes royal-blue West Francia (B-G ~40)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3))); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5)))
    # keep only sea components of real size (drops blue-pigment speckle inside West Francia)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); keep = np.zeros(n, bool); keep[1:] = st[1:, 4] > 4000
    return keep[lab].astype(np.uint8)
psea = plate_sea(plate)
rsea = (np.abs(ref - np.array([198, 210, 206])).sum(2) < 18).astype(np.uint8)
rsea = cv2.morphologyEx(rsea, cv2.MORPH_CLOSE, np.ones((5, 5))); rsea = cv2.morphologyEx(rsea, cv2.MORPH_OPEN, np.ones((3, 3)))
edge = lambda m: cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3))) > 0
COMP = RJ["zones"]["compass_ornament_reserved"]
s0 = W / pw
py_, px_ = np.nonzero(edge(psea)); P = np.c_[px_, py_].astype(float)
cp = np.array(COMP) / s0
kp = (P[:, 0] > 16) & (P[:, 0] < pw - 16) & (P[:, 1] > 16) & (P[:, 1] < ph - 16) & \
     ~((P[:, 0] > cp[0] - 20) & (P[:, 0] < cp[2] + 20) & (P[:, 1] > cp[1] - 20) & (P[:, 1] < cp[3] + 20))
P = P[kp]
qy, qx = np.nonzero(edge(rsea)); Q = np.c_[qx, qy].astype(float)
kq = (Q[:, 0] > 24) & (Q[:, 0] < W - 24) & (Q[:, 1] > 24) & (Q[:, 1] < H - 24) & \
     ~((Q[:, 0] > COMP[0] - 20) & (Q[:, 0] < COMP[2] + 20) & (Q[:, 1] > COMP[1] - 20) & (Q[:, 1] < COMP[3] + 20))
Q = Q[kq][::3]
log(f"control points: plate coast px {len(P)}, ref coast samples {len(Q)}")

def app(M, X): return X @ M[:, :2].T + M[:, 2]
def icp(kind):
    M = np.array([[s0, 0, 0], [0, H / ph, 0]], float)
    for it in range(30):
        dd, ii = cKDTree(app(M, P)).query(Q); m = dd < max(4.0, 12.0 * 0.85 ** it)
        f = cv2.estimateAffinePartial2D if kind == "similarity" else cv2.estimateAffine2D
        M, _ = f(P[ii[m]].astype(np.float32), Q[m].astype(np.float32), method=cv2.LMEDS)
    dd, ii = cKDTree(app(M, P)).query(Q); return M, dd, app(M, P)[ii] - Q
fits = {}
for kind in ("similarity", "affine"):
    M, dd, V = icp(kind); inl = dd < 8
    fits[kind] = dict(M=M, dd=dd, V=V, stats=dict(
        inlier_frac_4px=round(float((dd < 4).mean()), 3), inlier_frac_8px=round(float(inl.mean()), 3),
        mean_px=round(float(dd[inl].mean()), 2), median_px=round(float(np.median(dd[inl])), 2),
        p95_px=round(float(np.percentile(dd[inl], 95)), 2), max_px=round(float(dd[inl].max()), 2),
        all_points_median_px=round(float(np.median(dd)), 2), all_points_p90_px=round(float(np.percentile(dd, 90)), 2)))
    log(kind, np.round(M, 6).tolist(), fits[kind]["stats"])
MS = fits["similarity"]["M"]
sc = float(math.hypot(MS[0, 0], MS[1, 0])); rot = math.degrees(math.atan2(MS[1, 0], MS[0, 0]))
log(f"chosen: similarity, scale {sc:.5f} (cover-fit {max(W/pw, H/ph):.5f}), rotation {rot:.4f} deg, shift ({MS[0,2]:.2f},{MS[1,2]:.2f}) px")

# landmark regions (where the route lives) residuals
PL = {p["code"]: p for p in RJ["places"]}
dd, V = fits["similarity"]["dd"], fits["similarity"]["V"]
LM = {}
for c in ["P7", "P8", "P9", "P10", "P11", "P14", "P15", "P17", "P19", "P2", "P1"]:
    x, y = PL[c]["out_px"]; n = (np.hypot(Q[:, 0] - x, Q[:, 1] - y) < 45) & (dd < 16)
    if n.sum():
        LM[c] = dict(name=PL[c]["name"], n=int(n.sum()), mean_px=round(float(dd[n].mean()), 2), max_px=round(float(dd[n].max()), 2),
                     mean_vec_px=np.round(V[n].mean(0), 2).tolist())
log("landmark residuals", json.dumps(LM, ensure_ascii=False))

# ------------------------------------------------------------------ 2. registered plate + distortion QA
reg = cv2.warpAffine(plate, MS, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
psea_ref = cv2.warpAffine(psea, MS, (W, H), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
# Jacobian of the chosen map, evaluated on a grid (constant for a similarity; reported numerically anyway)
gx, gy = np.meshgrid(np.linspace(0, pw, 40), np.linspace(0, ph, 70)); G = np.c_[gx.ravel(), gy.ravel()]
e = 0.5; Jx = (app(MS, G + [e, 0]) - app(MS, G - [e, 0])) / (2 * e); Jy = (app(MS, G + [0, e]) - app(MS, G - [0, e])) / (2 * e)
sv = np.array([np.linalg.svd(np.c_[a, b], compute_uv=False) for a, b in zip(Jx, Jy)])
shear = np.degrees(np.abs(np.arcsin(np.clip((Jx * Jy).sum(1) / (np.linalg.norm(Jx, axis=1) * np.linalg.norm(Jy, axis=1)), -1, 1))))
DIST = dict(local_scale_min=round(float(sv.min()), 6), local_scale_max=round(float(sv.max()), 6),
            max_scale_deviation_pct=round(float((sv.max() / sv.min() - 1) * 100), 4), max_shear_deg=round(float(shear.max()), 5),
            max_anisotropy=round(float((sv[:, 0] / sv[:, 1]).max()), 6))
log("distortion", DIST)

# ------------------------------------------------------------------ 3. route on the plate (ref space == registered space)
D = cv2.distanceTransform(psea_ref, cv2.DIST_L2, 5)          # px to nearest painted land, in sea
Ds = cv2.GaussianBlur(D, (0, 0), 1.5); gyD, gxD = np.gradient(Ds)
def Dat(p):
    x, y = int(round(p[0])), int(round(p[1])); return float(D[min(max(y, 0), H - 1), min(max(x, 0), W - 1)])
def Dbl(P_):                                                                     # bilinear D (v2: sub-px accurate clearance)
    P_ = np.asarray(P_, np.float32).reshape(-1, 1, 2)
    return cv2.remap(D, P_[..., 0], P_[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).ravel()
def coast_pt(xy, min_d=2.0, r=40):
    x, y = xy; ys, xs = np.mgrid[int(y) - r:int(y) + r + 1, int(x) - r:int(x) + r + 1]
    ok = (D[np.clip(ys, 0, H - 1), np.clip(xs, 0, W - 1)] >= min_d); d2 = (xs - x) ** 2 + (ys - y) ** 2; d2[~ok] = 1e9
    i = np.unravel_index(np.argmin(d2), d2.shape); return [float(xs[i]), float(ys[i])], float(math.sqrt(d2[i]))
def dens(pts, step=1.0):
    pts = np.asarray(pts, float); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); cum = np.r_[0, np.cumsum(seg)]
    s = np.arange(0, cum[-1], step); s = np.r_[s, cum[-1]]
    return np.c_[np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1])]
def chaikin(p, k=2):
    for _ in range(k):
        q = np.empty((2 * len(p) - 2, 2)); q[0::2] = .75 * p[:-1] + .25 * p[1:]; q[1::2] = .25 * p[:-1] + .75 * p[1:]
        p = np.r_[p[:1], q, p[-1:]]
    return p
def arc(p): return np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
LEGS = {l["id"]: l for l in RJ["legs"]}
J = {}; JQ = {}
for c in ["P7", "P9", "P10", "P14", "P17"]:
    J[c], JQ[c] = coast_pt(PL[c]["out_px"], 2.0)
# Pisa end-mark: nearest painted-sea point to Pisa that is clearly nearer Pisa than Luna (>= 8 px), so it cannot read as Luna
_x, _y = PL["P17"]["out_px"]; _lx, _ly = PL["P18"]["out_px"]; ys, xs = np.mgrid[int(_y) - 40:int(_y) + 41, int(_x) - 40:int(_x) + 41]
dp = np.hypot(xs - _x, ys - _y); dl = np.hypot(xs - _lx, ys - _ly); ok = (D[ys, xs] >= 2) & (dl >= dp + 8); dp[~ok] = 1e9
_i = np.unravel_index(np.argmin(dp), dp.shape); J["P17"], JQ["P17"] = [float(xs[_i]), float(ys[_i])], float(dp[_i])
log("junction (coast) points", {c: (np.round(J[c], 1).tolist(), round(JQ[c], 1)) for c in J})
LEG_ENDS = {"S4": ("P7", "P9"), "S5": ("P9", "P10"), "S7": ("P10", "P14"), "S9": ("P14", "P17"), "P05-LEG": ("P17", None)}
ROUTE = {}; RQA = {}; SPURS = {}; S4_EXIT = {}
for lid, (a_, b_) in LEG_ENDS.items():
    src = dens(LEGS[lid]["polyline_out_px"]); d_src = np.array([Dat(p) for p in src])
    sea = np.nonzero(d_src >= 1)[0]; i0, i1 = sea[0], sea[-1]                     # trim inland spurs at both ends
    core = src[i0:i1 + 1].copy()
    A = np.array(J[a_]); Bp = np.array(J[b_]) if b_ else None
    if lid == "P05-LEG":                                                         # must stop at sea, short of Rome
        end = core[-1]
        if Dat(end) < W_PKEY / 2 + 0.75: end, _ = coast_pt(end, W_PKEY / 2 + 0.75)
        Bp = np.array(end)
    pts = np.r_[[A], core[3:-3] if len(core) > 8 else core, [Bp]]
    pts = dens(pts, 1.0); orig = pts.copy(); n = len(pts)
    s_arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; L = s_arc[-1]
    half = (W_PKEY if lid == "P05-LEG" else W_KEY) / 2 + KEY_PAD                # v2: whole keyline footprint offshore outside the spurs
    sp0 = SPUR
    if lid == "S4":
        # v2 (Vellum): S4 leaves the Algeciras landfall in the painted channel and drops SOUTH-EAST into open water at once, so the
        # keyline clears the Spanish tip. E = nearest point east of the landfall where the whole keyline fits (D >= half).
        # E: nearest point where the whole keyline fits, reached on a SE heading (25-50 deg below east) by a straight run that stays on sea
        ys, xs = np.nonzero(D >= half); ang = np.degrees(np.arctan2(ys - A[1], xs - A[0])); dE_ = np.hypot(xs - A[0], ys - A[1])
        cand = np.nonzero((ang >= 25) & (ang <= 50) & (dE_ < 40))[0]; cand = cand[np.argsort(dE_[cand])]
        for ci in cand:
            E_ = np.array([xs[ci], ys[ci]], float); seg_ = dens(np.r_[[A], [E_]], 0.5)
            if Dbl(seg_[2:]).min() >= 1.5: break
        u_ = (E_ - A) / np.linalg.norm(E_ - A); E2 = E_ + 3.0 * u_                    # 3 px further on, inside the clear water
        tail = orig[(orig[:, 0] > E2[0] + 6)]
        dy0 = E2[1] - np.interp(E2[0], orig[:, 0], orig[:, 1])                       # how far south of the v1/refpack line the exit sits
        st_ = arc(tail); fd = np.clip(st_ / 45.0, 0, 1); tail = tail + np.c_[np.zeros(len(tail)), dy0 * (1 - fd * fd * (3 - 2 * fd))]
        pts = dens(np.r_[[A], [E2], tail], 1.0); s_arc = arc(pts); L = s_arc[-1]
        sp0 = float(np.linalg.norm(E2 - A))                                        # the Algeciras spur = the run out of the channel
        S4_EXIT = dict(exit_point_px=np.round(E2, 1).tolist(), exit_heading_deg=round(float(np.degrees(np.arctan2(u_[1], u_[0]))), 1), channel_spur_px=round(sp0, 1), south_offset_at_exit_px=round(float(dy0), 1))
    def margin_for(sa, La, half=half, lid=lid, sp0=sp0):
        u0 = np.clip(sa / sp0, 0, 1); u1 = np.clip((La - sa) / SPUR, 0, 1) if lid != "P05-LEG" else np.ones_like(sa)
        u = np.minimum(u0, u1); return 1.0 + (half - 1.0) * u * u * (3 - 2 * u)
    SPURS[lid] = (sp0, SPUR if lid != "P05-LEG" else 0.0)
    margin = margin_for(s_arc, L)
    for it in range(160):                                                        # push points seaward up the distance field
        xi = np.clip(pts[:, 0].round().astype(int), 0, W - 1); yi = np.clip(pts[:, 1].round().astype(int), 0, H - 1)
        lack = margin_for(arc(pts), arc(pts)[-1]) - Dbl(pts); mv = lack > 0
        mv[0] = mv[-1] = False
        if not mv.any(): break
        g = np.c_[gxD[yi, xi], gyD[yi, xi]]; gn = np.linalg.norm(g, axis=1, keepdims=True) + 1e-6
        pts[mv] += 0.7 * (g[mv] / gn[mv]) * np.minimum(lack[mv, None], 2.0)
        if it % 10 == 9: pts[1:-1] = (pts[:-2] + 2 * pts[1:-1] + pts[2:]) / 4
    pts = dens(chaikin(pts[::4] if n > 12 else pts, 2), 1.0)
    pts[0], pts[-1] = A, Bp
    for it in range(120):                                                        # final no-smoothing pass: keyline footprint off painted land
        sa = arc(pts); mg = margin_for(sa, sa[-1])
        xi = np.clip(pts[:, 0].round().astype(int), 0, W - 1); yi = np.clip(pts[:, 1].round().astype(int), 0, H - 1)
        lack = mg - Dbl(pts); mv = lack > 0; mv[0] = mv[-1] = False
        if not mv.any(): break
        g = np.c_[gxD[yi, xi], gyD[yi, xi]]; gn = np.linalg.norm(g, axis=1, keepdims=True) + 1e-6
        pts[mv] += 0.5 * (g[mv] / gn[mv])
    dq = Dbl(pts); shift = cKDTree(orig).query(pts)[0]
    ROUTE[lid] = pts
    sa = arc(pts); La = sa[-1]; hk = (W_PKEY if lid == "P05-LEG" else W_KEY) / 2
    inner = (sa >= SPURS[lid][0]) & (sa <= La - SPURS[lid][1])
    def foot(sel, width):
        m = np.zeros((H * 4, W * 4), np.uint8); seg = pts[sel]
        if len(seg) >= 2: cv2.polylines(m, [(seg * 4).round().astype(np.int32)], False, 1, int(round(width * 4)), cv2.LINE_8)
        return int(((m > 0) & (cv2.resize(1 - psea_ref, (W * 4, H * 4), interpolation=cv2.INTER_NEAREST) > 0)).sum()) / 16.0
    fp_in = foot(inner, 2 * hk); fp_ink = foot(np.ones(len(pts), bool), (W_PALE if lid == "P05-LEG" else W_INK)); fp_all = foot(np.ones(len(pts), bool), 2 * hk)
    RQA[lid] = dict(from_=a_, to=b_ or "sea short of Rome", length_px=round(float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()), 1),
                    land_samples=int((dq < 1).sum()), min_dist_to_land_px=round(float(dq[1:-1].min()), 2),
                    max_shift_from_refpack_px=round(float(shift.max()), 2), trimmed_spur_samples=int(i0 + (len(src) - 1 - i1)),
                    keyline_halfwidth_px=hk, keyline_land_px_outside_spurs=fp_in, keyline_land_px_total_incl_spurs=fp_all, ink_land_px_total=fp_ink,
                    min_keyline_clearance_outside_spurs_px=round(float((dq[inner] - hk).min()), 2) if inner.any() else None,
                    spur_px=list(SPURS[lid]), min_centre_dist_to_land_in_spurs_px=round(float(dq[~inner][1:-1].min()), 2) if (~inner).sum() > 2 else None)
    log(lid, RQA[lid])
ROME = np.array(PL["P19"]["out_px"]); LEG_END = ROUTE["P05-LEG"][-1]
ROMEQA = dict(rome_glyph_px=ROME.tolist(), rome_on_plate_land=bool(Dat(ROME) < 1), leg_end_px=np.round(LEG_END, 1).tolist(),
              leg_end_dist_to_land_px=round(Dat(LEG_END), 2), leg_end_to_rome_px=round(float(np.linalg.norm(LEG_END - ROME)), 1),
              leg_end_to_rome_km=round(float(np.linalg.norm(LEG_END - ROME)) * RJ["frame"]["km_per_out_px"], 1))
ENDMARK = np.array(J["P17"])
EMQA = dict(endmark_px=ENDMARK.tolist(), pisa_data_px=PL["P17"]["out_px"], offset_from_pisa_px=round(JQ["P17"], 1),
            offset_km=round(JQ["P17"] * RJ["frame"]["km_per_out_px"], 1), dist_to_land_px=round(Dat(ENDMARK), 2),
            dist_to_luna_px=round(float(np.hypot(*(ENDMARK - PL["P18"]["out_px"]))), 1))
log("rome", ROMEQA); log("endmark", EMQA)
assert all(q["land_samples"] == 0 and q["keyline_land_px_outside_spurs"] == 0 for q in RQA.values()), "route/keyline on painted land"
assert ROMEQA["leg_end_dist_to_land_px"] >= 1 and ROMEQA["leg_end_to_rome_px"] > 8

# ------------------------------------------------------------------ 4. timing + camera + guardrail
ease = lambda u: 0.5 - 0.5 * math.cos(math.pi * min(max(u, 0.0), 1.0))
BEATS = [("S4", 0.25, 1.30), ("S5", 1.30, 2.35), ("S7", 2.35, 3.45), ("S9", 3.45, 4.55)]
T_ENDMARK = 4.55; HOLD = (4.55, 4.85); T_LEG = (4.85, 5.90); T_ROME = (5.55, 5.90)
FADE_TO, FADE_S = 0.85, 0.6
def zoom(t): return Z0 + (Z1 - Z0) * ease(t / DUR)
KU = [(0.0, -0.5), (1.3, -0.5), (4.6, 0.9), (DUR, 0.9)]          # horizontal drift (fraction of available slack)
KV = [(0.0, 0.5), (1.3, 0.5), (4.6, -0.15), (DUR, -0.15)]         # vertical drift (+ = window south)
def kf(K, t):
    for (ta, va), (tb, vb) in zip(K, K[1:]):
        if t <= tb: return va + (vb - va) * ease((t - ta) / (tb - ta))
    return K[-1][1]
def cam(t):
    z = zoom(t); cx = 540 + 540 * (1 - 1 / z) * kf(KU, t); cy = 960 + 960 * (1 - 1 / z) * kf(KV, t)
    return z, cx, cy
def C(t):  # ref(out@1.0) -> frame
    z, cx, cy = cam(t); return np.array([[z, 0, 540 - z * cx], [0, z, 960 - z * cy]])
def compose(A, B): return np.r_[A, [[0, 0, 1]]] @ np.r_[B, [[0, 0, 1]]]
G1 = guardrails.check_pixel_density(str(PLATE), (W, H), (Z0, Z1), mode="refuse", name="P05_KEEP")
G2 = guardrails.check_crop_zoom(Z1, mode="refuse", plate_wh=(pw, ph), out_wh=(W, H))
actual_density = sc * Z1
log("guardrail check_pixel_density", G1); log("guardrail check_crop_zoom", G2); log(f"actual plate->frame scale at peak {actual_density:.4f}")
# frame-safety: every overlay point stays inside pin_safe and above y 1280 all through the move
allpts = np.vstack([ROUTE[k] for k in ROUTE] + [ENDMARK[None], ROME[None]])
worst = dict(min_x=1e9, max_x=-1e9, min_y=1e9, max_y=-1e9)
for f in range(NF):
    Mt = C(f / FPS); q = app(Mt, allpts)
    worst["min_x"] = min(worst["min_x"], q[:, 0].min()); worst["max_x"] = max(worst["max_x"], q[:, 0].max())
    worst["min_y"] = min(worst["min_y"], q[:, 1].min()); worst["max_y"] = max(worst["max_y"], q[:, 1].max())
    z, cx, cy = cam(f / FPS); hw, hh = 540 / z, 960 / z
    assert cx - hw >= -1e-6 and cx + hw <= W + 1e-6 and cy - hh >= -1e-6 and cy + hh <= H + 1e-6, "window leaves plate"
worst = {k: round(float(v), 1) for k, v in worst.items()}; log("overlay extent over the shot", worst)
assert worst["max_y"] < 1280 - 8 and worst["min_x"] > 64 and worst["max_x"] < 1015, worst   # geometry centres; rendered-alpha bbox checked in the render

transform = dict(
    plate=str(PLATE), plate_md5=PLATE_MD5, plate_wh=[pw, ph], ref=str(REF), ref_md5=md5(REF), ref_space="refpack_p05 output px (1080x1920, LAEA lat0 40.7 lon0 3.0)",
    model="similarity (uniform scale + rotation + shift); no TPS", matrix_plate_to_ref=np.round(MS, 8).tolist(),
    scale=round(sc, 6), rotation_deg=round(rot, 5), shift_px=[round(float(MS[0, 2]), 3), round(float(MS[1, 2]), 3)],
    control_points=dict(method="automatic coastline ICP: ref coast = boundary of the refpack clean sea colour (every 3rd px); plate coast = boundary of "
                        "colour-segmented painted sea (slate-teal: B>R+8, B<118, G<115, B-G<28 to exclude royal-blue West Francia; blur 2.5; open/close; components >4000 px). Excluded: 16 px plate border, "
                        "24 px ref border, compass zone +20 px. Trimmed nearest-neighbour ICP, LMedS fit, trim radius annealed 12 -> 4 px over 30 iterations.",
                        n_plate=int(len(P)), n_ref=int(len(Q))),
    residuals_out_px={k: v["stats"] for k, v in fits.items()}, affine_matrix_for_comparison=np.round(fits["affine"]["M"], 8).tolist(),
    landmark_residuals_out_px=LM, distortion=DIST, camera=dict(zoom=[Z0, Z1], drift_keys_u=KU, drift_keys_v=KV, note="frame = C(t) o M; one Lanczos resample per frame from the original plate"),
    guardrail=dict(check_pixel_density=G1, check_crop_zoom=G2, actual_peak_out_px_per_source_px=round(actual_density, 4)),
    s4_exit=S4_EXIT, route_px={k: np.round(v[::3], 2).tolist() + [np.round(v[-1], 2).tolist()] for k, v in ROUTE.items()}, route_qa=RQA,
    endmark=EMQA, rome=ROMEQA, junctions={c: dict(px=J[c], offset_from_data_px=round(JQ[c], 1)) for c in J},
    beats=dict(legs=BEATS, endmark=T_ENDMARK, hold=HOLD, legend_leg=T_LEG, rome_glyph=T_ROME, fade_to=FADE_TO, fade_s=FADE_S),
    overlay_extent_frame_px=worst)
if ARGS.stage in ("all", "reg"):
    # v2: registration is unchanged; verify the regenerated warp equals the saved v1 registered PNG instead of rewriting it
    REG_SAME = bool(np.array_equal(np.array(Image.open(HERE / "P05_KEEP_registered_1080x1920.png").convert("RGB")), reg)); log("registered PNG identical to v1:", REG_SAME)
    assert REG_SAME; transform["registered_png_identical_to_v1"] = REG_SAME
    json.dump(transform, open(out("p05_transform_v2.json"), "w"), indent=1, ensure_ascii=False)
    # ---- QA crops: before (original plate, nearest-upsampled 2x) | after (registered, same region, 2x) with ref coast (magenta) over the after
    rcoast = edge(rsea); qa_regions = {"strait": (90, 1080, 330, 1280), "rhone": (520, 720, 720, 880), "tuscany_rome": (740, 720, 960, 920)}
    tiles = []
    for nm, (x0, y0, x1, y1) in qa_regions.items():
        ia = MS[:, :2]; inv = np.linalg.inv(ia); c0 = inv @ (np.array([x0, y0]) - MS[:, 2]); c1 = inv @ (np.array([x1, y1]) - MS[:, 2])
        bef = plate[int(c0[1]):int(c1[1]), int(c0[0]):int(c1[0])]
        bef = cv2.resize(bef, ((x1 - x0) * 2, (y1 - y0) * 2), interpolation=cv2.INTER_NEAREST)
        aft = cv2.resize(reg[y0:y1, x0:x1], ((x1 - x0) * 2, (y1 - y0) * 2), interpolation=cv2.INTER_NEAREST)
        ov = aft.copy(); m2 = cv2.resize(rcoast[y0:y1, x0:x1].astype(np.uint8), ((x1 - x0) * 2, (y1 - y0) * 2), interpolation=cv2.INTER_NEAREST) > 0
        ov[m2] = (255, 0, 255)
        for lid, pts in ROUTE.items():
            q = ((pts - [x0, y0]) * 2).astype(np.int32)
            cv2.polylines(ov, [q], False, (40, 220, 40) if lid != "P05-LEG" else (40, 220, 220), 2, cv2.LINE_AA)
        for pnt in (ENDMARK, ROME):
            cv2.circle(ov, tuple(((pnt - [x0, y0]) * 2).astype(int)), 6, (255, 255, 0), 2, cv2.LINE_AA)
        tiles.append(np.hstack([bef, np.full((bef.shape[0], 6, 3), 255, np.uint8), aft, np.full((bef.shape[0], 6, 3), 255, np.uint8), ov]))
    wmax = max(t.shape[1] for t in tiles)
    sheet = np.vstack([np.pad(t, ((0, 8), (0, wmax - t.shape[1]), (0, 0)), constant_values=255) for t in tiles])
    sheet = cv2.resize(sheet, (sheet.shape[1] * 3 // 5, sheet.shape[0] * 3 // 5), interpolation=cv2.INTER_AREA)
    Image.fromarray(sheet).quantize(256).save(out("qa/p05_registration_crops_v2.png"), optimize=True)
    # texture check: Laplacian variance of the registered plate vs the original (same regions), expect ~ 1/scale^2 x original for an honest resample
    lv = {}
    for nm, (x0, y0, x1, y1) in qa_regions.items():
        inv = np.linalg.inv(MS[:, :2]); c0 = inv @ (np.array([x0, y0]) - MS[:, 2]); c1 = inv @ (np.array([x1, y1]) - MS[:, 2])
        g0 = cv2.cvtColor(plate[int(c0[1]):int(c1[1]), int(c0[0]):int(c1[0])], cv2.COLOR_RGB2GRAY).astype(float)
        g1 = cv2.cvtColor(reg[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(float)
        lv[nm] = dict(lapvar_original=round(float(cv2.Laplacian(g0, cv2.CV_64F).var()), 1), lapvar_registered=round(float(cv2.Laplacian(g1, cv2.CV_64F).var()), 1))
    transform["texture_lapvar"] = lv; log("texture", lv)
    json.dump(transform, open(HERE / "p05_transform_v2.json", "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ 5. animation
ARC = {k: arc(v) for k, v in ROUTE.items()}
def prefix(lid, u):
    p, s = ROUTE[lid], ARC[lid]; L = s[-1] * u
    if u <= 0: return p[:1], 0.0
    k = np.searchsorted(s, L); k = min(max(k, 1), len(p) - 1)
    a_ = (L - s[k - 1]) / max(s[k] - s[k - 1], 1e-9); head = p[k - 1] + a_ * (p[k] - p[k - 1])
    return np.r_[p[:k], [head]], L
def point_at(lid, L):
    p, s = ROUTE[lid], ARC[lid]; L = min(max(L, 0), s[-1]); return np.array([np.interp(L, s, p[:, 0]), np.interp(L, s, p[:, 1])])
SS = 3
def ship_poly(cx, cy, k):
    hull = [(-15, 2), (15, 2), (11, 8), (-11, 8)]
    sail = [(-9, -18), (9, -18), (10, -1), (-10, -1)]
    tf = lambda pts: np.array([[(cx + x * k) * SS, (cy + y * k) * SS] for x, y in pts], np.int32)
    return tf(hull), tf(sail), np.array([[(cx) * SS, (cy - 21 * k) * SS], [(cx) * SS, (cy + 2 * k) * SS]], np.int32), \
        [tf([(-3.5, -18), (-3.5, -1)]), tf([(3.5, -18), (3.5, -1)])]
dash_rng = np.random.default_rng(860)
def render_overlay(t, Mt):
    """returns (rgb float HxWx3 premult-free colour layer, alpha HxW) in frame px for time t"""
    q_all = app(Mt, allpts); x0 = int(max(0, q_all[:, 0].min() - 60)); x1 = int(min(W, q_all[:, 0].max() + 60))
    y0 = int(max(0, q_all[:, 1].min() - 70)); y1 = int(min(H, q_all[:, 1].max() + 60)); w, h = x1 - x0, y1 - y0
    off = np.array([x0, y0])
    toS = lambda pts: ((app(Mt, pts) - off) * SS).astype(np.int32)
    z = cam(t)[0]
    key = np.zeros((h * SS, w * SS), np.float32); ink = np.zeros_like(key); wet = np.zeros_like(key)
    pale = np.zeros_like(key); pkey = np.zeros_like(key); mk_ink = np.zeros_like(key); mk_key = np.zeros_like(key)
    sail_f = np.zeros_like(key); shad = np.zeros_like(key); rome_a = np.zeros_like(key); rome_k = np.zeros_like(key)
    wI = int(round(W_INK * z * SS)); wK = int(round(W_KEY * z * SS))
    fleet = None
    for lid, ta, tb in BEATS:
        if t < ta: continue
        u = ease((t - ta) / (tb - ta)); pre, Ld = prefix(lid, u)
        a = 1.0 if t <= tb else 1.0 - (1.0 - FADE_TO) * ease((t - tb) / FADE_S)
        if len(pre) >= 2:
            S_ = toS(pre); tmpk = np.zeros_like(key); tmpi = np.zeros_like(key)
            cv2.polylines(tmpk, [S_], False, 1.0, wK, cv2.LINE_AA); cv2.polylines(tmpi, [S_], False, 1.0, wI, cv2.LINE_AA)
            key = np.maximum(key, tmpk * a); ink = np.maximum(ink, tmpi * a)
            if t < tb + 0.5:                                            # wet tip: darker over the last ~26 px, dries in 0.5 s after the beat
                tip, _ = prefix(lid, u); s_ = arc(tip); k0 = np.searchsorted(s_, s_[-1] - 26)
                tmpw = np.zeros_like(key); cv2.polylines(tmpw, [toS(tip[k0:])], False, 1.0, wI, cv2.LINE_AA)
                wet = np.maximum(wet, tmpw * (1 - ease((t - tb) / 0.5)) if t > tb else tmpw)
        fleet = point_at(lid, min(Ld, ARC[lid][-1] - (64 if lid == "S9" else 0)))
    if fleet is None: fleet = ROUTE["S4"][0]
    # legendary leg: broken, paler
    if t >= T_LEG[0]:
        u = ease((t - T_LEG[0]) / (T_LEG[1] - T_LEG[0])); pre, Ld = prefix("P05-LEG", u)
        s_ = arc(pre); on = ((s_ % (DASH_ON + DASH_OFF)) < DASH_ON)
        segs = []; cur = []
        for pp, o in zip(pre, on):
            if o: cur.append(pp)
            elif cur: segs.append(cur); cur = []
        if cur: segs.append(cur)
        for sg in segs:
            if len(sg) >= 2:
                S_ = toS(np.array(sg)); cv2.polylines(pkey, [S_], False, 1.0, int(round(W_PKEY * z * SS)), cv2.LINE_AA)
                cv2.polylines(pale, [S_], False, 1.0, int(round(W_PALE * z * SS)), cv2.LINE_AA)
    # end-mark (unlabelled): ink ring + centre dot, stamped at T_ENDMARK
    if t >= T_ENDMARK:
        u = ease((t - T_ENDMARK) / 0.22); r = (8.5 * MARK_K * (1.35 - 0.35 * u)) * z; c = tuple(toS(ENDMARK[None])[0]); K_ = MARK_K * z * SS
        cv2.circle(mk_key, c, int(r * SS), u, int(5.6 * K_), cv2.LINE_AA); cv2.circle(mk_ink, c, int(r * SS), u, int(2.8 * K_), cv2.LINE_AA)
        cv2.circle(mk_key, c, int(3.6 * K_), u, -1, cv2.LINE_AA); cv2.circle(mk_ink, c, int(2.4 * K_), u, -1, cv2.LINE_AA)
    # small pale Rome glyph (no text), on land; the leg stops short of it at sea
    if t >= T_ROME[0]:
        u = ease((t - T_ROME[0]) / (T_ROME[1] - T_ROME[0])) * 0.8; c = tuple(toS(ROME[None])[0])
        cv2.circle(rome_k, c, int(6 * z * SS), u, int(4.0 * z * SS), cv2.LINE_AA); cv2.circle(rome_a, c, int(6 * z * SS), u, int(2.0 * z * SS), cv2.LINE_AA)
    # nameless fleet marker: one square-sailed ship, no text/portrait
    fa = ease(t / 0.25); fq = app(Mt, fleet[None])[0] - off; k = 1.05 * MARK_K * z
    hull, sail, mast, stripes = ship_poly(fq[0], fq[1] - 6 * k, k)
    tmp = np.zeros_like(key); cv2.fillPoly(tmp, [hull, sail], 1.0, cv2.LINE_AA); cv2.polylines(tmp, [mast], False, 1.0, int(3 * MARK_K * SS), cv2.LINE_AA)
    shad = cv2.GaussianBlur(tmp, (0, 0), 2.2 * MARK_K * SS) * 0.45 * fa
    kk = cv2.dilate(tmp, np.ones((int(3.2 * MARK_K * SS), int(3.2 * MARK_K * SS)), np.uint8)) * fa
    cv2.fillPoly(mk_ink, [hull], fa, cv2.LINE_AA); cv2.polylines(mk_ink, [mast], False, fa, int(2.0 * MARK_K * SS), cv2.LINE_AA)
    cv2.polylines(mk_ink, [sail], True, fa, int(1.8 * MARK_K * SS), cv2.LINE_AA)
    for st_ in stripes: cv2.polylines(mk_ink, [st_], False, fa * 0.85, int(1.6 * MARK_K * SS), cv2.LINE_AA)
    cv2.fillPoly(sail_f, [sail], fa, cv2.LINE_AA)
    mk_key = np.maximum(mk_key, kk)
    ds = lambda m: cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA)
    L = {n_: ds(v) for n_, v in dict(key=key, ink=ink, wet=wet, pale=pale, pkey=pkey, mk_ink=mk_ink, mk_key=mk_key, sail=sail_f,
                                      shad=shad, rome_a=rome_a, rome_k=rome_k).items()}
    return (x0, y0, x1, y1), L
def comp(base, col, a):
    return base * (1 - a[..., None]) + np.array(col, np.float32) * a[..., None]
BB = []
def frame(t):
    Mt = C(t); F = compose(Mt, MS)[:2]
    img = cv2.warpAffine(plate, F, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    (x0, y0, x1, y1), L = render_overlay(t, Mt); roi = img[y0:y1, x0:x1]
    roi = comp(roi, PARCH, np.clip(L["key"] * A_KEY, 0, 1))
    roi = comp(roi, PARCH, np.clip(L["pkey"] * A_PKEY, 0, 1)); roi = comp(roi, LEG_PALE, np.clip(L["pale"] * A_PALE, 0, 1))
    roi = comp(roi, OX, np.clip(L["ink"] * A_INK, 0, 1)); roi = comp(roi, OX_WET, np.clip(L["wet"] * 0.9, 0, 1))
    roi = comp(roi, PARCH, np.clip(L["rome_k"] * 0.45, 0, 1)); roi = comp(roi, (226, 204, 176), np.clip(L["rome_a"], 0, 1))
    roi = comp(roi, (20, 12, 10), np.clip(L["shad"], 0, 1)); roi = comp(roi, PARCH, np.clip(L["mk_key"] * 0.7, 0, 1))
    roi = comp(roi, (244, 234, 212), np.clip(L["sail"], 0, 1)); roi = comp(roi, OX, np.clip(L["mk_ink"] * 0.95, 0, 1))
    img[y0:y1, x0:x1] = roi
    al = np.maximum.reduce([L[k_] for k_ in L]); ys_, xs_ = np.nonzero(al > 0.02)
    if len(xs_): BB.append((x0 + xs_.min(), y0 + ys_.min(), x0 + xs_.max(), y0 + ys_.max()))
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)

if ARGS.stage in ("all", "anim"):
    mp4 = out("p05_test_v2.mp4"); tr0 = time.time()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
                           "-bitexact", "-fflags", "+bitexact", str(mp4)], stdin=subprocess.PIPE)
    CS = [0, 30, 52, 85, 118, 140, 160, 187]; csf = {}
    for f in range(NF):
        im = frame(f / FPS); ff.stdin.write(im.tobytes())
        if f in CS: csf[f] = im
    ff.stdin.close(); assert ff.wait() == 0
    log(f"render {NF} frames in {time.time() - tr0:.1f} s")
    th = [cv2.resize(csf[f], (270, 480), interpolation=cv2.INTER_AREA) for f in CS]
    for f, im in zip(CS, th):
        cv2.putText(im, f"f{f} {f / FPS:.2f}s", (6, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    sheet = np.vstack([np.hstack(th[:4]), np.hstack(th[4:])])
    Image.fromarray(sheet).quantize(256, dither=Image.Dither.NONE).save(out("p05_contact_sheet_v2.png"), optimize=True)
    for f in (140, 187):
        Image.fromarray(csf[f][700:1320, 100:1000]).quantize(256).save(out(f"qa/p05_v2_frame{f:03d}_routecrop.png"), optimize=True)
    bb = np.array(BB); ext = dict(min_x=int(bb[:, 0].min()), min_y=int(bb[:, 1].min()), max_x=int(bb[:, 2].max()), max_y=int(bb[:, 3].max()))
    log("rendered overlay alpha bbox over the shot (frame px)", ext); transform["rendered_overlay_bbox_frame_px"] = ext
    assert ext["min_x"] >= 64 and ext["max_x"] <= 1015 and ext["min_y"] >= 96 and ext["max_y"] < 1280, ext
    # legibility: last frame at phone-thumb size, and v1 vs v2 side by side
    th2 = cv2.resize(csf[CS[-1]], (360, 640), interpolation=cv2.INTER_AREA); Image.fromarray(th2).save(out("qa/p05_v2_last_360x640.png"), optimize=True)
    v1 = HERE / "p05_test_v1.mp4"
    if v1.exists():
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-sseof", "-0.05", "-i", str(v1), "-frames:v", "1", "-vf", "scale=360:640:flags=area",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == 360 * 640 * 3:
            th1 = np.frombuffer(raw, np.uint8).reshape(640, 360, 3)
            Image.fromarray(np.hstack([th1, np.full((640, 8, 3), 255, np.uint8), th2])).save(out("qa/p05_v1_vs_v2_last_360x640.png"), optimize=True)
    # contrast of the route at thumb size: ink core vs the sea just outside the keyline (CIELAB dE, last frame)
    Mt = C(CS[-1] / FPS); core = np.zeros((H, W), np.uint8); halo = np.zeros((H, W), np.uint8)
    for lid_ in ("S5", "S7", "S9"):
        q_ = app(Mt, ROUTE[lid_][int(SPUR):-int(SPUR)]).round().astype(np.int32)
        cv2.polylines(core, [q_], False, 1, max(1, int(W_INK * 0.6)), cv2.LINE_8); cv2.polylines(halo, [q_], False, 1, int(W_KEY * 2.6), cv2.LINE_8)
    ring = (halo > 0) & (cv2.dilate(core, np.ones((int(W_KEY * 1.4), int(W_KEY * 1.4)), np.uint8)) == 0)
    lab = cv2.cvtColor(th2, cv2.COLOR_RGB2LAB).astype(float); lab[..., 0] *= 100 / 255; lab[..., 1:] -= 128
    c_ = cv2.resize(core, (360, 640), interpolation=cv2.INTER_AREA) > 0; r_ = cv2.resize(ring.astype(np.uint8), (360, 640), interpolation=cv2.INTER_NEAREST) > 0
    r_ &= ~c_
    dE = float(np.linalg.norm(lab[c_].mean(0) - lab[r_].mean(0)))
    LEGIB = dict(thumb="qa/p05_v2_last_360x640.png", ink_core_lab=np.round(lab[c_].mean(0), 1).tolist(), sea_ring_lab=np.round(lab[r_].mean(0), 1).tolist(),
                 dE_core_vs_sea=round(dE, 1), ink_width_thumb_px=round(W_INK * Z1 / 3, 2), keyline_width_thumb_px=round(W_KEY * Z1 / 3, 2))
    log("legibility", LEGIB); transform["legibility"] = LEGIB
    transform["render"] = dict(frames=NF, fps=FPS, seconds=round(NF / FPS, 4), contact_frames=CS)
    json.dump(transform, open(HERE / "p05_transform_v2.json", "w"), indent=1, ensure_ascii=False)
assert md5(PLATE) == PLATE_MD5, "source plate changed!"
json.dump(LOG, open(HERE / "qa/build_log_v2.json", "w"), indent=0, ensure_ascii=False)
log(f"total {time.time() - T0:.1f} s; plate md5 unchanged {PLATE_MD5}")
