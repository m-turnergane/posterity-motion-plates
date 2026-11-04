#!/usr/bin/env python3
"""P05 for ROUGH v4 (copy of rough_v4_prep/p05/build_p05_v4.py): word-locked to the VOICED v4 VO (rough_v4/scratch/vo_bjorn_v4.wav, ALT-A2 pause already in the retime -> --pause 0);
realm labels IM Fell English SC (Uncial E->C legibility flag). Variant b only. Run: --variants b --offset 0.376667 --pause 0. Writes rough_v4/scratch/p05_rough/.
Parameterised solver: --slot, --offset, --pause-after, --pause, --onsets (json of word timings) -> beats.
Run: /workspace/mpvenv/bin/python build_p05_v4.py [--variants b,a] [--force]
Writes ONLY into ./test_v4/. Reads plates/P05_KEEP.png read-only (md5 before/after)."""
import sys, os, json, math, hashlib, subprocess, time, argparse
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent; BJ = HERE.parents[1]; OUT = BJ / "rough_v4/scratch/p05_rough_v4b"
PLATE = BJ / "plates/P05_KEEP.png"; TJ = BJ / "map/p05_anim/p05_transform_v2.json"; RJ = BJ / "map/refpack_p05/route_places_p05.json"
SCRIPT = BJ / "raw/script-vo-v4-LOCKED.txt"; SCRIPT_MD5 = "ff97caaa20d2238fddc30c7bdb4a0c8a"
WORDS = BJ / "rough_v4/scratch/p05_L04_words_v4vo.json"; VO = BJ / "rough_v4/scratch/vo_bjorn_v4.wav"
FONTS = BJ / "rough_v4_prep/p05/fonts"
sys.path.insert(0, "/workspace/posterity/motion"); import guardrails
ap = argparse.ArgumentParser()
ap.add_argument("--slot", type=float, default=10.5); ap.add_argument("--offset", type=float, default=0.37)
ap.add_argument("--pause-after", default="Mediterranean,"); ap.add_argument("--pause", type=float, default=0.354)
ap.add_argument("--variants", default="b,a"); ap.add_argument("--force", action="store_true"); ap.add_argument("--frames", default="")
A = ap.parse_args()
def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def outp(n):
    p = OUT / n
    if p.exists() and not A.force: sys.exit(f"refusing to overwrite {p}")
    p.parent.mkdir(parents=True, exist_ok=True); return p
LOG = []
def log(*a): s = " ".join(map(str, a)); print(s, flush=True); LOG.append(s)

W, H, FPS = 1080, 1920, 30; SLOT = A.slot; NF = int(round(SLOT * FPS)); Z0, Z1 = 1.0, 1.06
assert md5(SCRIPT) == SCRIPT_MD5, "script md5 mismatch"
PMD5 = md5(PLATE); assert PMD5.startswith("4ef7ca5f")
plate = np.array(Image.open(PLATE).convert("RGB")); T = json.load(open(TJ)); R = json.load(open(RJ))
MS = np.array(T["matrix_plate_to_ref"]); PL = {p["code"]: p for p in R["places"]}; LEGS = {l["id"]: l for l in R["legs"]}

# ---------------------------------------------------------------- 1. word-locked solver
wd = json.load(open(WORDS)); wl = wd["words"] if isinstance(wd, dict) and "words" in wd else wd
def wstart(w): return float(w.get("start", w.get("start_s")))
def wend(w): return float(w.get("end", w.get("end_s")))
def wtext(w): return w.get("w", w.get("word", w.get("text")))
cut = None
for i, w in enumerate(wl):
    if wtext(w) == A.pause_after: cut = (wend(w) + wstart(wl[i + 1])) / 2
def p05t(t_raw): return A.offset + t_raw + (A.pause if (cut is not None and t_raw > cut) else 0.0)
ON = {}
for w in wl:
    k = wtext(w).strip(",.")
    if k in ("Spain", "Mediterranean", "France", "Italy", "Rhône") and k not in ON: ON[k] = round(p05t(wstart(w)), 3)
line_end = p05t(wend(wl[-1]))
HOLD = 0.5
B = dict(strait=ON["Spain"], camargue=ON["France"], depart=ON["France"] + HOLD, pisa=ON["Italy"], pisa_hold_end=ON["Italy"] + HOLD,
         tail=(ON["Italy"] + HOLD, ON["Italy"] + HOLD + 0.8), med_label=ON["Mediterranean"], line_end=round(line_end, 3), slot=SLOT)
log("onsets (P05 time)", ON, "pause cut at raw", round(cut, 3), "beats", B)
assert B["tail"][1] <= SLOT - 0.3 and line_end <= SLOT

# ---------------------------------------------------------------- 2. geometry (ref px)
reg = cv2.warpAffine(plate, MS, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
def plate_sea(img):
    b = cv2.GaussianBlur(img, (0, 0), 2.5).astype(int); r, g, bb = b[..., 0], b[..., 1], b[..., 2]
    m = ((bb > r + 8) & (bb < 118) & (g < 115) & (bb - g < 28)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3))); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); keep = np.zeros(n, bool); keep[1:] = st[1:, 4] > 4000; return keep[lab].astype(np.uint8)
sea = plate_sea(reg); D = cv2.distanceTransform(sea, cv2.DIST_L2, 5); Ds = cv2.GaussianBlur(D, (0, 0), 1.5); gyD, gxD = np.gradient(Ds)
def dens(p, step=1.0):
    p = np.asarray(p, float); c = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]; s = np.r_[np.arange(0, c[-1], step), c[-1]]
    return np.c_[np.interp(s, c, p[:, 0]), np.interp(s, c, p[:, 1])]
def arc(p): return np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
def Dbl(P_):
    P_ = np.asarray(P_, np.float32).reshape(-1, 1, 2); return cv2.remap(D, P_[..., 0], P_[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).ravel()
def push(p, m=5.0, fix_ends=True):
    p = dens(p, 1.0)
    for it in range(150):
        xi = np.clip(p[:, 0].round().astype(int), 0, W - 1); yi = np.clip(p[:, 1].round().astype(int), 0, H - 1)
        lack = m - Dbl(p); mv = lack > 0
        if fix_ends: mv[0] = mv[-1] = False
        if not mv.any(): break
        g = np.c_[gxD[yi, xi], gyD[yi, xi]]; g /= np.linalg.norm(g, axis=1, keepdims=True) + 1e-6
        p[mv] += 0.7 * g[mv] * np.minimum(lack[mv, None], 2.0)
        if it % 10 == 9: p[1:-1] = (p[:-2] + 2 * p[1:-1] + p[2:]) / 4
    return p
RP = {k: np.array(v, float) for k, v in T["route_px"].items()}
s2 = dens(LEGS["S2"]["polyline_out_px"]); a2 = arc(s2); TAIL_IN = 100.0; tail0 = s2[a2 >= a2[-1] - TAIL_IN]   # ship enters through the left edge fade (was 56 px in-frame)
s3 = push(LEGS["S3"]["polyline_out_px"], 4.0)
main = dens(np.r_[push(tail0, 3.0, False)[:-1], s3[:-1], dens(RP["S4"]), dens(RP["S5"])[1:], dens(RP["S7"])[1:]], 1.0)
s9 = dens(RP["S9"], 1.0)
am = arc(main)
STRAIT_PT = np.array(T["s4_exit"]["exit_point_px"]) if "exit_point_px" in T.get("s4_exit", {}) else np.array([196.7, 1199.3])
i_str = int(np.argmin(np.linalg.norm(main - STRAIT_PT, axis=1))); L0 = am[i_str]
SHORT = 36.0; L1 = am[-1] - SHORT
path2 = dens(np.r_[main[am >= am[-1] - SHORT], s9[1:]], 1.0); a_p2 = arc(path2); L2 = a_p2[-1] - SHORT   # Camargue stop -> Pisa stop
ORI = np.array([388.0, 1105.0]); L_ori = am[int(np.argmin(np.linalg.norm(main - ORI, axis=1)))]
log(f"main path {am[-1]:.1f} px: seg0 to Strait {L0:.1f}, seg1 {L1-L0:.1f}, seg2 (S9) {L2:.1f}")
PISA_END = RP["S9"][-1]; CAM_J = RP["S7"][-1]; VAL = np.array(PL["P16"]["out_px"]); CAM_D = np.array(PL["P14"]["out_px"])
PISA_D = np.array(PL["P17"]["out_px"]); LUNA = np.array(PL["P18"]["out_px"])

# ---------------------------------------------------------------- 3. ship kinematics (arc length vs time)
def sramp(u): return 0.5 - 0.5 * math.cos(math.pi * min(max(u, 0), 1))
def prof_A(ta, r_dn, T1):   # 0..T1: cosine ramp-up over ta, cruise, cosine ramp-down over r_dn*T1; returns unit-vmax s(t)
    td = r_dn * T1; ts = np.linspace(0, T1, 4001); v = np.array([sramp(t / ta) * (1 - sramp((t - (T1 - td)) / td)) for t in ts])
    s = np.r_[0, np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(ts))]; return ts, s
T0 = B["strait"]; T1b = B["camargue"] - B["strait"]; RDN = 0.30; V0 = 18.0
V1 = (L1 - L0) / (T1b - 0.5 * RDN * T1b)                       # seg1: enters at V1, cruises, cosine ramp-down to rest at the France onset
NPOW = (V1 - V0) * T0 / (L0 - V0 * T0) - 1                       # seg0: v = V0 + (V1-V0)(t/T0)^n  -> continuous speed at the Strait
assert NPOW >= 1.0, NPOW
tsA = np.linspace(0, B["camargue"], 6001)
def vA(t):
    if t <= T0: return V0 + (V1 - V0) * (t / T0) ** NPOW
    u = t - T0; td = RDN * T1b; return V1 * (1 - sramp((u - (T1b - td)) / td))
vv = np.array([vA(t) for t in tsA]); sA = np.r_[0, np.cumsum((vv[1:] + vv[:-1]) / 2 * np.diff(tsA))]; sA *= L1 / sA[-1]
TA, VMAX_A = NPOW, V1
T2 = B["pisa"] - B["depart"]; tsB = np.linspace(0, T2, 4001); vb = np.array([sramp(t / (0.3 * T2)) * (1 - sramp((t - 0.7 * T2) / (0.3 * T2))) for t in tsB])
sB = np.r_[0, np.cumsum((vb[1:] + vb[:-1]) / 2 * np.diff(tsB))]; VMAX_B = L2 / sB[-1]; sB = sB * VMAX_B
log(f"solver: seg0 v=V0+(V1-V0)(t/T0)^{NPOW:.2f}, V0 {V0}, V1 {V1:.1f} ref px/s; s(Strait)={np.interp(T0, tsA, sA):.1f} vs L0 {L0:.1f}; seg2 vmax {VMAX_B:.1f}")
def ship_state(t):
    """returns (which path, arc) ; path 'main' or 's9'"""
    if t < B["camargue"]: return "main", float(np.interp(t, tsA, sA))
    if t < B["depart"]: return "main", L1
    if t < B["pisa"]: return "s9", float(np.interp(t - B["depart"], tsB, sB))
    return "s9", L2
def pt_at(path, s):
    p = main if path == "main" else path2; a = am if path == "main" else a_p2
    return np.array([np.interp(s, a, p[:, 0]), np.interp(s, a, p[:, 1])])

# ---------------------------------------------------------------- 4. camera
ease = sramp
KU = [(0.0, -0.5), (2.2, -0.5), (7.7, 0.9), (SLOT, 0.9)]; KV = [(0.0, 0.5), (2.2, 0.5), (7.7, -0.15), (SLOT, -0.15)]
def kf(K, t):
    for (ta, va), (tb, vb) in zip(K, K[1:]):
        if t <= tb: return va + (vb - va) * ease((t - ta) / (tb - ta))
    return K[-1][1]
def C(t):
    z = Z0 + (Z1 - Z0) * ease(t / SLOT); cx = 540 + 540 * (1 - 1 / z) * kf(KU, t); cy = 960 + 960 * (1 - 1 / z) * kf(KV, t)
    return np.array([[z, 0, 540 - z * cx], [0, z, 960 - z * cy]])
def c3(M): return np.r_[M, [[0, 0, 1]]]
G1 = guardrails.check_pixel_density(str(PLATE), (W, H), (Z0, Z1), mode="refuse", name="P05_KEEP")
G2 = guardrails.check_crop_zoom(Z1, mode="refuse", plate_wh=plate.shape[1::-1], out_wh=(W, H)); log("guardrails", G1, G2)

# ---------------------------------------------------------------- 5. pigments sampled from the plate
lum = cv2.cvtColor(reg, cv2.COLOR_RGB2GRAY).astype(float)
land = (sea == 0) & (lum > 20); lv = lum[land]
INK = np.median(reg[land & (lum < np.percentile(lv, 0.7))], 0)            # darkest painted line work = iron-gall/sepia
BONE = np.median(reg[land & (lum > np.percentile(lv, 99.0))], 0)          # brightest parchment highlights
OX = np.array([112, 26, 20], float)                                        # house route colour (PRESETS route.color)
log("pigments: ink", INK.round(), "bone", BONE.round(), "ox", OX)

# ---------------------------------------------------------------- 6. 2x ROI canvas + ink helpers
X0, Y0, X1, Y1 = 30, 540, 1050, 1290; S = 2; RW, RH = (X1 - X0) * S, (Y1 - Y0) * S
def r2(p): return ((np.asarray(p, float) - [X0, Y0]) * S)
rng = np.random.default_rng(1611)
NZ_L = cv2.GaussianBlur(rng.standard_normal((RH, RW)).astype(np.float32), (0, 0), 6); NZ_L /= NZ_L.std()
NZ_H = cv2.GaussianBlur(rng.standard_normal((RH, RW)).astype(np.float32), (0, 0), 1.3); NZ_H /= NZ_H.std()
DX = cv2.GaussianBlur(rng.standard_normal((RH, RW)).astype(np.float32), (0, 0), 3); DX *= 1.3 / DX.std()
DY = cv2.GaussianBlur(rng.standard_normal((RH, RW)).astype(np.float32), (0, 0), 3); DY *= 1.3 / DY.std()
GX, GY = np.meshgrid(np.arange(RW, dtype=np.float32), np.arange(RH, dtype=np.float32))
def inkify(m, pool=True, rough=1.0, tn=0.10):
    """m: 0..1 coverage at 2x. -> density 0..1 with irregular edge, weight modulation and edge pooling"""
    m = cv2.remap(m.astype(np.float32), GX + DX * rough, GY + DY * rough, cv2.INTER_LINEAR)
    mb = cv2.GaussianBlur(m, (0, 0), 0.9); thr = 0.42 + tn * NZ_H
    a = np.clip((mb - thr + 0.18) / 0.36, 0, 1); a = a * a * (3 - 2 * a)
    d = a * (0.80 + 0.10 * np.clip(NZ_L, -2, 2) * 1.0)
    if pool:
        inner = np.clip(mb - cv2.GaussianBlur(mb, (0, 0), 2.5), 0, 1); d = d + 0.9 * inner * a
    return np.clip(d, 0, 1).astype(np.float32)
def sstep(a, b, x): u = np.clip((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- 7. route rasters: coverage + arc maps
def stroke_arcmap(pts, width, dash=None):
    """returns (coverage 0..1 at 2x, arcmap) — arcmap = arc length (ref px) of the stroke pixel"""
    P = r2(pts); a = arc(pts); cov = np.zeros((RH, RW), np.float32); am_ = np.full((RH, RW), 1e9, np.float32)
    for i in range(len(P) - 1):
        if dash is not None:
            on, off, kind = dash; ph = a[i] % (on + off)
            if ph > on: continue
        p, q = tuple(np.round(P[i] * 4).astype(int)), tuple(np.round(P[i + 1] * 4).astype(int))
        if dash is not None and dash[2] == "dot":
            if (a[i] % (on + off)) < 1.0: cv2.circle(cov, tuple(np.round(P[i] * 4).astype(int)), int(width * S / 2 * 4), 1.0, -1, cv2.LINE_AA, 2)
            else: continue
        else:
            cv2.line(cov, p, q, 1.0, max(1, int(round(width * S))), cv2.LINE_AA, 2)
        tmp = np.zeros((RH, RW), np.uint8)
    # arcmap via nearest path sample
    yy, xx = np.nonzero(cov > 0.01)
    from scipy.spatial import cKDTree
    _, ii = cKDTree(P).query(np.c_[xx, yy]); am_[yy, xx] = a[ii]
    return cov, am_
def legdef(pts, style, w_ink=5.5, w_key=8.5):
    pts = dens(pts, 1.0)
    if style == "solid": dash = None
    elif style == "dot": dash = (1.0, 10.0, "dot")
    else: dash = (10.0, 6.5, "dash")
    if style == "dot":
        ci, am_ = stroke_arcmap(pts, 5.4, (1.0, 10.0, "dot")); ck, _ = stroke_arcmap(pts, 9.0, (1.0, 8.0, "dot"))
    else:
        ci, am_ = stroke_arcmap(pts, w_ink, dash); ck, _ = stroke_arcmap(pts, w_key, dash)
    return dict(pts=pts, L=arc(pts)[-1], ink=inkify(ci), key=np.clip(cv2.GaussianBlur(ck, (0, 0), 0.8), 0, 1), am=am_)
log("rasterising legs ...")
LG = {}
LG["main"] = legdef(main, "solid", 7.5, 11.5)          # v2 W_INK 11 / W_KEY 16 at 1x were heavy; hand-inked v4 = 5.5 ink / 8.5 bone key (ref px)
LG["S9"] = legdef(s9, "solid", 7.5, 11.5)
LG["S8"] = legdef(np.r_[[CAM_J], LEGS["S8"]["polyline_out_px"][3:]], "solid", 5.5, 9.0)
LG["S1"] = legdef(LEGS["S1"]["polyline_out_px"], "dot"); LG["S2"] = legdef(s2[a2 <= a2[-1] - TAIL_IN + 1], "solid", 6.0, 9.5)
LG["S2a"] = legdef(LEGS["S2a"]["polyline_out_px"], "dot"); LG["S6"] = legdef(LEGS["S6"]["polyline_out_px"], "dot")
LG["S12"] = legdef(LEGS["S12"]["polyline_out_px"], "dot"); LG["S13"] = legdef(LEGS["S13"]["polyline_out_px"], "dot")
LG["TAIL"] = legdef(RP["P05-LEG"], "dash", 5.0, 8.5)
t_ori = float(np.interp(L_ori, sA, tsA))
CTX = {"S1": (0.0, 0.0, 0.55), "S2": (0.0, 0.0, 0.70), "S2a": (2.0, 2.6, 0.60), "S6": (t_ori + 0.15, t_ori + 0.75, 0.60),
       "S12": (B["tail"][0] + 0.05, B["tail"][1], 0.50), "S13": (B["tail"][0] + 0.20, B["tail"][1] + 0.1, 0.50)}
log("Orihuela pass", round(t_ori, 2), "context timing", CTX)

# ---------------------------------------------------------------- 8. sprites: sword + ship (drawn at 8x then area-down to 2x)
def sprite(draw_fn, size, k=4):
    big = np.zeros((size * k, size * k, 3), np.float32); draw_fn(big, k); sm = cv2.resize(big, (size, size), interpolation=cv2.INTER_AREA)
    sil = np.clip(sm.sum(2), 0, 1); halo = np.clip(cv2.GaussianBlur(cv2.dilate(sil, np.ones((5, 5), np.uint8)), (0, 0), 1.2) * 1.5, 0, 1)
    sm[..., 1] = np.maximum(sm[..., 1], halo * 0.9)          # parchment keyline under the ink, as on the route
    return sm
def sword_draw(img, k):
    c = img.shape[0] / 2; s = img.shape[0] / 72
    def P(x, y): return (int(c + x * s), int(c + y * s))
    blade = np.array([P(-2.6, -6), P(2.6, -6), P(2.0, 22), P(0, 30), P(-2.0, 22)])
    cv2.fillPoly(img, [blade], (0, 1, 0), cv2.LINE_AA, 0)                               # ch1 = bone fill
    cv2.polylines(img, [blade], True, (1, 0, 0), int(1.6 * s), cv2.LINE_AA)              # ch0 = ink
    cv2.line(img, P(0, -4), P(0, 20), (1, 0, 0), int(0.9 * s), cv2.LINE_AA)             # fuller
    guard = np.array([P(-11, -9), P(-6, -7), P(6, -7), P(11, -9), P(11, -6.5), P(6, -4.6), P(-6, -4.6), P(-11, -6.5)])
    cv2.fillPoly(img, [guard], (1, 0, 0), cv2.LINE_AA)
    cv2.line(img, P(0, -7), P(0, -17), (1, 0, 0), int(3.2 * s), cv2.LINE_AA)
    for y in (-9.5, -12, -14.5): cv2.line(img, P(-1.8, y), P(1.8, y - 1), (0, 1, 0), int(0.6 * s), cv2.LINE_AA)
    cv2.circle(img, P(0, -20), int(3.6 * s), (1, 0, 0), -1, cv2.LINE_AA); cv2.circle(img, P(0, -20), int(1.4 * s), (0, 1, 0), -1, cv2.LINE_AA)
def ship_draw(img, k):
    c = img.shape[0] / 2; s = img.shape[0] / 72
    def P(x, y): return (int(c + x * s), int(c + y * s))
    hull = np.array([P(-21, 2), P(-12, 7.5), P(0, 9), P(12, 7.5), P(21, 2), P(15, 3.2), P(0, 4.2), P(-15, 3.2)])
    cv2.fillPoly(img, [hull], (1, 0, 0), cv2.LINE_AA)
    for x in range(-12, 14, 4): cv2.line(img, P(x, 4.6), P(x - 1.5, 8), (0, 1, 0), int(0.55 * s), cv2.LINE_AA)   # strake hatching
    pr = [P(21, 2), P(24, -3), P(25.5, -8), P(24, -11), P(21.5, -10.5), P(21.8, -8.2), P(23.3, -8.6)]
    cv2.polylines(img, [np.array(pr)], False, (1, 0, 0), int(1.8 * s), cv2.LINE_AA)
    st = [P(-21, 2), P(-23.5, -3), P(-24, -7), P(-22, -9), P(-20.4, -7.6)]
    cv2.polylines(img, [np.array(st)], False, (1, 0, 0), int(1.8 * s), cv2.LINE_AA)
    for x in range(-14, 16, 4): cv2.circle(img, P(x, 2.6), int(1.5 * s), (1, 0, 0), int(0.6 * s), cv2.LINE_AA)       # shields
    cv2.line(img, P(0, 3), P(0, -25), (1, 0, 0), int(1.5 * s), cv2.LINE_AA)
    sail = np.array([P(-11.5, -22), P(11.5, -22), P(12.5, -12), P(11.5, -4), P(-11.5, -4), P(-12.5, -12)])
    cv2.fillPoly(img, [sail], (0, 1, 0), cv2.LINE_AA)
    for i, x in enumerate(range(-11, 12, 4)):
        if i % 2 == 0: cv2.fillPoly(img, [np.array([P(x, -22), P(x + 4, -22), P(x + 4.4, -12), P(x + 4, -4), P(x, -4), P(x + 0.3, -12)])], (0, 0, 1), cv2.LINE_AA)
    cv2.polylines(img, [sail], True, (1, 0, 0), int(1.3 * s), cv2.LINE_AA)
    cv2.line(img, P(-12, -22.5), P(12, -22.5), (1, 0, 0), int(1.5 * s), cv2.LINE_AA)
SW = sprite(sword_draw, 72); SH = sprite(ship_draw, 96)
def inkspr(spr):
    out = spr.copy(); pad = lambda a: a
    return out
# ---------------------------------------------------------------- 9. labels
F_REALM = "/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf"; F_WATER = str(FONTS / "imfelldwpica/IMFePIit28P.ttf")
F_PISA = str(FONTS / "imfelldwpica/IMFePIrm28P.ttf")
# v4b (phone legibility, Examiner RECHECK-v4 FIX-2): story labels (Pisa, Provence, Rhône, Strait) raised to cap >= 22.7 px at 1080 on appearance;
# realms lifted to stay the largest tier; FRANCIA moved inland off the Atlantic coast; Strait of Gibraltar moved onto the Andalusian shore
# directly above the strait (the end-frame camera crops the Atlantic and the Alboran pocket is filled by the route); Pisa set snug to its dot.
# Positions found by an obstacle/clearance search (route legs, dots, swords, compass, other labels, frame edges at every t) then eye-checked.
LABELS = [  # name, lines, font, px(1x cap-ish size), tracking em, centre (ref px), rotate deg, t_in, status, source
    ("WEST FRANCIA", ["WEST", "FRANCIA"], F_REALM, 38, 0.08, (490, 646), 0, (0.10, 0.75), "CONFIRMED", "ARCHIVIST-v4-CHECK.md l.141; map-reference-data.md (Loire to Aquitaine; NOT over the Rhône)"),
    ("PROVENCE", ["PROVENCE"], F_REALM, 33, 0.00, (728, 762), 22, (0.25, 0.85), "CONFIRMED (boundary = interpretation)", "ARCHIVIST-v4-CHECK.md l.142, l.150 FLAG"),
    ("EMIRATE OF CÓRDOBA", ["EMIRATE OF", "CÓRDOBA"], F_REALM, 38, 0.02, (272, 1030), 0, (0.15, 0.80), "CONFIRMED", "ARCHIVIST-v4-CHECK.md l.143"),
    ("KINGDOM OF ITALY", ["KINGDOM", "OF ITALY"], F_REALM, 36, 0.08, (828, 652), 0, (0.35, 0.95), "CONFIRMED", "ARCHIVIST-v4-CHECK.md l.144"),
    ("Strait of Gibraltar", ["Strait of", "Gibraltar"], F_WATER, 33, 0.04, (232, 1132), 0, (2.30, 2.95), "CONFIRMED (modern English per Archivist)", "ARCHIVIST-v4-CHECK.md l.145"),
    ("Mediterranean Sea", ["Mediterranean  Sea"], F_WATER, 35, 0.10, (704, 1100), 0, (B["med_label"], B["med_label"] + 0.75), "CONFIRMED (modern name)", "ARCHIVIST-v4-CHECK.md l.148"),
    ("Rhône", ["Rhône"], F_WATER, 33, 0.06, (560, 766), 82, (5.80, 6.30), "CONFIRMED", "ARCHIVIST-v4-CHECK.md l.146"),
    ("Pisa", ["Pisa"], F_PISA, 33, 0.06, (864, 800), 0, (B["pisa"], B["pisa"] + 0.35), "CONFIRMED", "ARCHIVIST-v4-CHECK.md l.147; AB 860 ll.3455-3456"),
]
HALO = {"KINGDOM OF ITALY": (0.70, 0.30), "Rhône": (0.42, 0.45)}
def render_label(lines, font, px, track, rot):
    f = ImageFont.truetype(font, int(px * S * 1.0)); lh = int(px * S * 1.0 * 1.05)
    ws = []
    for ln in lines:
        w = sum(f.getlength(ch) for ch in ln) + track * px * S * 1.0 * (len(ln) - 1); ws.append(w)
    Wd, Hd = int(max(ws) + 20), int(lh * len(lines) + 20); im = Image.new("L", (Wd, Hd), 0); d = ImageDraw.Draw(im)
    for li, ln in enumerate(lines):
        x = 10 + (max(ws) - ws[li]) / 2
        for ch in ln:
            d.text((x, 10 + li * lh), ch, font=f, fill=255); x += f.getlength(ch) + track * px * S * 1.0
    m = np.array(im, np.float32) / 255; u = np.tile(np.arange(Wd, dtype=np.float32), (Hd, 1)) / Wd
    if rot:
        Mr = cv2.getRotationMatrix2D((Wd / 2, Hd / 2), rot, 1.0); cs, sn = abs(Mr[0, 0]), abs(Mr[0, 1])
        nW, nH = int(Hd * sn + Wd * cs), int(Hd * cs + Wd * sn); Mr[0, 2] += nW / 2 - Wd / 2; Mr[1, 2] += nH / 2 - Hd / 2
        m = cv2.warpAffine(m, Mr, (nW, nH)); u = cv2.warpAffine(u, Mr, (nW, nH), borderValue=0)
    return m, u
LB = []
for (name, lines, font, px, track, cen, rot, tin, status, src) in LABELS:
    m, u = render_label(lines, font, px, track, rot); hh, ww = m.shape; c2 = r2(cen); x0, y0 = int(c2[0] - ww / 2), int(c2[1] - hh / 2)
    full = np.zeros((RH, RW), np.float32); uf = np.zeros((RH, RW), np.float32); full[y0:y0 + hh, x0:x0 + ww] = m; uf[y0:y0 + hh, x0:x0 + ww] = u
    yy, xx = np.nonzero(m > 0.1); bb = [(x0 + xx.min()) / S + X0, (y0 + yy.min()) / S + Y0, (x0 + xx.max()) / S + X0, (y0 + yy.max()) / S + Y0]
    bbi = [int(v) for v in bb]; Lm = lum[bbi[1]:bbi[3], bbi[0]:bbi[2]].mean()
    light = Lm < 112
    dens_ = inkify(cv2.GaussianBlur(full, (0, 0), 0.5), pool=True, rough=0.35, tn=0.04)
    halo = np.clip(cv2.GaussianBlur(cv2.dilate(dens_, np.ones((5, 5), np.uint8)), (0, 0), 2.2) * 1.4, 0, 1)
    LB.append(dict(name=name, d=dens_, halo=halo, u=uf, tin=tin, light=bool(light), bbox_ref=[round(v, 1) for v in bb], ground_lum=round(float(Lm), 1),
                   font=Path(font).name, px=px, status=status, src=src, lines=lines, rot=rot))
    log(f"label {name}: bbox {np.round(bb,1).tolist()} ground L {Lm:.0f} -> {'bone body colour' if light else 'iron-gall multiply'}")
# collision checks among labels, legs, compass, Luna
COMP = R["zones"]["compass_ornament_reserved"]
def ov(a, b): return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
for i in range(len(LB)):
    assert not ov(LB[i]["bbox_ref"], COMP), LB[i]["name"] + " hits compass"
    for j in range(i + 1, len(LB)): assert not ov(LB[i]["bbox_ref"], LB[j]["bbox_ref"]), (LB[i]["name"], LB[j]["name"])
ROUTE_ALL = np.r_[main, s9]
LBQA = {}
for l in LB:
    b = l["bbox_ref"]; inb = (ROUTE_ALL[:, 0] > b[0] - 4) & (ROUTE_ALL[:, 0] < b[2] + 4) & (ROUTE_ALL[:, 1] > b[1] - 4) & (ROUTE_ALL[:, 1] < b[3] + 4)
    LBQA[l["name"]] = dict(route_pts_inside_bbox_pad4=int(inb.sum()), dist_to_luna_px=round(float(math.hypot(max(b[0] - LUNA[0], 0, LUNA[0] - b[2]), max(b[1] - LUNA[1], 0, LUNA[1] - b[3]))), 1))
# v4b clearance: label ink (rotation-aware) vs every leg polyline and the three approved dots
for l in LB:
    yy, xx = np.nonzero(l["d"] > 0.3); P_ = np.c_[xx / S + X0, yy / S + Y0][::7]
    dleg = min(float(np.min(np.linalg.norm(P_[:, None, :] - np.asarray(g["pts"], float)[None, ::2, :], axis=2))) for k, g in LG.items() if k != "TAIL")
    ddot = min(float(np.min(np.linalg.norm(P_ - p, axis=1))) for p in (CAM_D, VAL, PISA_D))
    LBQA[l["name"]].update(ink_to_nearest_leg_px=round(dleg, 1), ink_to_nearest_dot_px=round(ddot, 1))
    assert dleg >= 5 and ddot >= 8, (l["name"], dleg, ddot)
log("label QA", LBQA)

# city dots (ink): Camargue, Valence, Pisa, Seville(dotted ring), Algeciras, Nekor, Orihuela — NOTHING at Luna
DOTS = dict(Camargue=CAM_D, Valence=VAL, Pisa=PISA_D)
dotcov = np.zeros((RH, RW), np.float32)
for n, p in DOTS.items(): q = r2(p); cv2.circle(dotcov, tuple(np.round(q * 4).astype(int)), int(3.2 * S * 4), 1.0, -1, cv2.LINE_AA, 2)
DOTD = inkify(dotcov, rough=0.5)
SWORDS = [("Camargue", CAM_D, B["camargue"], 22), ("Valence", VAL, None, -22), ("Pisa", PISA_D, B["pisa"], 24)]
assert min(np.linalg.norm(p - LUNA) for p in [CAM_D, VAL, PISA_D, PISA_END]) > 12

# ---------------------------------------------------------------- 10. per-frame overlay (2x ROI) -> frame
def paste(dst_list, spr, centre2x, scale, rot, alpha=1.0):
    """spr HxWx3 (ink, bone, ox) ; place centre at centre2x with scale/rot into 3 layers"""
    h, w = spr.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale); M[0, 2] += centre2x[0] - w / 2; M[1, 2] += centre2x[1] - h / 2
    wsp = cv2.warpAffine(spr, M, (RW, RH), flags=cv2.INTER_LINEAR)
    for c in range(3): dst_list[c] += wsp[..., c] * alpha
SWS = SW * 0.55; SHS = SH * 1.0      # sword ~ 72*0.55/2 = 20 ref px tall... scaled at paste
VALT = None
def overlay(t, variant):
    Lr = [np.zeros((RH, RW), np.float32) for _ in range(3)]   # route group: ink, bone, ox  (edge-faded)
    Lm = [np.zeros((RH, RW), np.float32) for _ in range(3)]   # mark/label group
    def leg(key, s_rev, alpha=1.0, wet=True, grp=Lr, pale=False):
        g = LG[key]; rev = sstep(s_rev + 0.5, s_rev - 2.0, g["am"]) * alpha
        grp[1] += g["key"] * rev * (0.80 if not pale else 0.55); grp[2] += g["ink"] * rev * (0.62 if pale else 1.0)
        if wet: grp[0] += g["ink"] * rev * 0.35 * sstep(s_rev - 30, s_rev - 2, g["am"])
    for k, (ta, tb, al) in CTX.items():
        if variant == "b" and k in ():
            continue
        if tb == ta: f = 1.0
        else: f = sstep(ta, tb, t)
        if f > 0: leg(k, f * LG[k]["L"] if tb > ta else LG[k]["L"], al, wet=False)
    path, s = ship_state(t)
    if path == "main":
        s_line = s if t < B["camargue"] else min(am[-1], L1 + (am[-1] - L1) * sstep(0, 0.15, t - B["camargue"]))
        leg("main", s_line)
    else:
        leg("main", am[-1], wet=False); s_line = max(0.0, s - SHORT) if t < B["pisa"] else (L2 - SHORT) + SHORT * sstep(0, 0.15, t - B["pisa"])
        leg("S9", s_line)
    # S8 Valence out-and-back trace during the Camargue hold
    if t >= B["camargue"]:
        u = sstep(B["camargue"] + 0.02, B["camargue"] + 0.25, t); leg("S8", u * LG["S8"]["L"], 0.9, wet=False)
    if variant == "a" and t >= B["tail"][0]:
        u = sstep(B["tail"][0], B["tail"][1], t); leg("TAIL", u * LG["TAIL"]["L"], 0.70, wet=False, pale=True)
    # ship
    pos = pt_at(path, s); bob = 0.9 * math.sin(2 * math.pi * t / 1.6); roll = 2.2 * math.sin(2 * math.pi * t / 2.3 + 0.7)
    paste(Lr, SH, r2(pos + [0, -12 + bob]), 1.32, roll)
    # dots + swords
    for c in (0,): Lm[0] += DOTD
    for (n, p, ts, rot) in SWORDS:
        if n == "Valence": ts = B["camargue"] + 0.25
        if t < ts: continue
        u = min((t - ts) / 0.2, 1.0); e = 1 - (1 - u) ** 3; sc = 1.25 * (1.25 - 0.25 * e); drop = -8 * (1 - e)
        tip = r2(p); ang = math.radians(rot); off = np.array([math.sin(ang), -math.cos(ang)]) * 30 * sc  # sprite centre above tip (tip at +30 sprite px)
        paste(Lm, SW, tip + off * 1.0 + [0, drop * S], sc, -rot, alpha=min(1.0, u * 2))
    # labels
    global SHD
    SHD = [np.zeros((RH, RW), np.float32)]
    for l in LB:
        ta, tb = l["tin"]
        if t < ta: continue
        p = min((t - ta) / (tb - ta), 1.0); F = 0.06; wipe = np.clip((p * (1 + F) - l["u"]) / F, 0, 1) * (l["u"] > 0)
        wh = cv2.GaussianBlur(wipe, (0, 0), 2.0) if p < 1 else (l["u"] > 0).astype(np.float32)
        if l["light"]: SHD[0] += l["halo"] * wh * HALO.get(l["name"], (0.42, 0.30))[1]; Lm[1] += l["d"] * wipe * 0.95      # bone body colour + soft iron-gall shadow
        else: Lm[1] += l["halo"] * wh * HALO.get(l["name"], (0.42, 0.30))[0]; Lm[0] += l["d"] * wipe * 1.0              # iron-gall ink + parchment knock-out halo
    return [np.clip(x, 0, 1) for x in Lr], [np.clip(x, 0, 1) for x in Lm], pos, np.clip(SHD[0], 0, 1)
EDGE = None
def compose_frame(t, variant):
    Ct = C(t); Mf = c3(Ct) @ c3(MS); frame = cv2.warpAffine(plate, Mf[:2], (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    Lr, Lm, pos, shd = overlay(t, variant)
    A_ = c3(Ct) @ np.array([[1, 0, X0], [0, 1, Y0], [0, 0, 1]], float)       # ROI@1x -> frame
    lum_f = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    hp = lum_f - cv2.GaussianBlur(lum_f, (0, 0), 2.0); g = np.clip(hp / 18.0, -1, 1)
    xs = np.arange(W, dtype=np.float32); edge = sstep(64, 128, xs)[None, :] * sstep(1015, 960, xs)[None, :]; edgeL = sstep(64, 86, xs)[None, :] * sstep(1015, 993, xs)[None, :]
    out = frame
    a_s = np.clip(cv2.warpAffine(cv2.resize(shd, (RW // S, RH // S), interpolation=cv2.INTER_AREA), A_[:2], (W, H), flags=cv2.INTER_LINEAR) * edgeL, 0, 1)[..., None]
    out = out * (1 - a_s + a_s * INK / 255.0)
    def warp(l): return cv2.warpAffine(cv2.resize(l, (RW // S, RH // S), interpolation=cv2.INTER_AREA), A_[:2], (W, H), flags=cv2.INTER_LINEAR)
    for grp, ef in ((Lr, edge), (Lm, edgeL)):
        ink, bone, ox = [warp(x) for x in grp]
        ink, bone, ox = ink * ef, bone * ef, ox * ef
        ab = np.clip(bone * (0.85 + 0.30 * (g * 0.5 + 0.5)), 0, 1)[..., None]
        out = out * (1 - ab) + BONE[None, None, :] * ab
        ao = np.clip(ox * (0.85 + 0.30 * (0.5 - g * 0.5)), 0, 1)[..., None]
        out = out * (1 - ao + ao * OX / 255.0)
        ai = np.clip(ink * (0.85 + 0.30 * (0.5 - g * 0.5)), 0, 1)[..., None]
        out = out * (1 - ai + ai * INK / 255.0)
    ovm = np.zeros((H, W), bool)
    for grp, ef in ((Lr, edge), (Lm, edgeL)):
        for l in grp: ovm |= (warp(l) * ef) > 0.03
    shipf = (Ct @ np.r_[pos, 1])
    return np.clip(out, 0, 255).astype(np.uint8), ovm, shipf

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    if A.frames:
        for spec in A.frames.split(","):
            v, t = spec.split("@"); im, _, _ = compose_frame(float(t), v); Image.fromarray(im).save(f"/tmp/bjv4b/p05v4b_{v}_{t}.png")
        sys.exit()
    REP = dict(script=str(SCRIPT), script_md5=SCRIPT_MD5, vo_temp=str(VO), vo_md5=md5(VO), onsets_p05=ON, pause_cut_raw_s=round(cut, 3),
               pause_s=A.pause, line_offset_s=A.offset, beats=B, guardrails=[G1, G2], pigments=dict(ink=INK.round().tolist(), bone=BONE.round().tolist(), ox=OX.tolist()),
               solver=dict(seg0_power=round(TA, 3), vmax_ref_px_s_seg01=round(VMAX_A, 1), vmax_ref_px_s_seg2=round(VMAX_B, 1), L0=round(L0, 1), L1=round(L1, 1), L2=round(L2, 1)),
               labels=[{k: l[k] for k in ("name", "lines", "font", "px", "rot", "tin", "bbox_ref", "ground_lum", "light", "status", "src")} for l in LB], label_qa=LBQA, context_legs=CTX)
    for v in A.variants.split(","):
        sil = outp(f"p05_test_v4{v}_silent.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(sil)], stdin=subprocess.PIPE)
        ext = [9999, 9999, 0, 0]; shp = []; grabs = {}
        GT = dict(strait=B["strait"], camargue_valence=B["camargue"] + 0.30, peak_speed=None, pisa=B["pisa"] + 0.30, final=(NF - 1) / FPS)
        for f in range(NF):
            t = f / FPS; im, ovm, sp = compose_frame(t, v); ff.stdin.write(im.tobytes()); shp.append(sp.tolist())
            ys, xs = np.nonzero(ovm)
            if len(xs): ext = [min(ext[0], xs.min()), min(ext[1], ys.min()), max(ext[2], xs.max()), max(ext[3], ys.max())]
            for k, tg in GT.items():
                if tg is not None and abs(t - tg) < 0.5 / FPS: Image.fromarray(im).save(outp(f"grab_v4{v}_{k}_f{f:03d}.png"))
            if f % 30 == 0: print(v, f, flush=True)
        ff.stdin.close(); ff.wait()
        shp = np.array(shp); spd = np.linalg.norm(np.diff(shp, axis=0), axis=1) * FPS; fpk = int(np.argmax(spd))
        # peak-speed grab
        im, _, _ = compose_frame(fpk / FPS, v); Image.fromarray(im).save(outp(f"grab_v4{v}_peakspeed_f{fpk:03d}.png"))
        REP[f"variant_{v}"] = dict(silent=str(sil), overlay_extent_frame_px=[int(x) for x in ext],
                                   safe_ok=bool(ext[0] >= 64 and ext[2] <= 1015 and ext[3] < 1280 and ext[1] >= 96),
                                   ship_peak_frame_px_s=round(float(spd.max()), 1), ship_peak_frame=fpk, ship_peak_screen_frac_per_s=round(float(spd.max() / W), 3),
                                   ship_speed_p95=round(float(np.percentile(spd, 95)), 1), frames=NF)
        log(f"variant {v}", REP[f"variant_{v}"])
    json.dump(REP, open(outp("p05_test_v4_report.json"), "w"), indent=1, ensure_ascii=False, default=float)
    assert md5(PLATE) == PMD5
    open(outp("build_log.txt"), "w").write("\n".join(LOG))
