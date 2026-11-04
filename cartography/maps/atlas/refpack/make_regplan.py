"""Registration plan data + prototype for the Edward II owner plates (refpack v2).

1. control points per frame (headlands from the engine gazetteer / Wikidata P625, river mouths and confluences from
   the NE 10m centerlines, settlements from MAP-PLACES P625) with lon/lat and px in out (1x) and plate (2x) space.
2. prototype on a SYNTHETIC warp of each frame's reference (stand-in for a generated plate): global ORB+RANSAC affine,
   per-point gradient template matching, thin-plate-spline fit (scipy RBF), leave-one-out residuals, distortion QA,
   QA overlay PNG.  Writes only new files (open(...,'x')); scratch -> REFPACK_OUT.
"""
import sys; sys.dont_write_bytecode = True
import os, json, math, hashlib
import numpy as np, cv2
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import gaussian_filter
from shapely.geometry import LineString, MultiLineString, Polygon, Point
from shapely.ops import unary_union, nearest_points
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from refpack_lib import *                                   # noqa
TAG = os.environ.get("REFPACK_TAG", "v2"); OUTD = os.environ.get("REFPACK_OUT", HERE)
IMG = os.path.join(OUTD, f"img_{TAG}"); os.makedirs(IMG, exist_ok=True)
J = json.load(open(os.path.join(HERE, "framing_refpack_v2.json")))
NE = V1.NE

HEADLANDS = {  # gazetteer name -> extreme direction on the coast (engine fit_control_points convention)
    "Land's End": "W", "Lizard Point, Cornwall": "S", "Mizen Head": "SW", "Pointe du Raz": "W", "Cap Gris-Nez": "NW",
    "Cap de la Hague": "NW", "Dunnet Head": "N", "Grenen": "NE", "Cape Finisterre": "W", "Cap Corse": "N",
    "Portland Bill": "S", "Great Orme": "N", "Spurn": "SE", "Portofino": "S", "Hartland Point": "NW", "Selsey Bill": "S",
    "The Needles": "W", "Brean Down": "W", "Den Helder": "N"}
# approximate positions (my own), SNAPPED to the nearest NE10m coastline point: the stored lon/lat is the NE coast
# vertex, i.e. geodata, not my guess.  'dir' = which way the tip points (for the engine's extreme-pixel locator).
EXTRA_HEADLANDS = {
    "St David's Head": (-5.31, 51.90, "W"), "Strumble Head": (-5.07, 52.03, "NW"), "Braich y Pwll (Lleyn tip)": (-4.77, 52.80, "W"),
    "Holy Head (Anglesey)": (-4.69, 53.31, "W"), "Worms Head (Gower)": (-4.33, 51.56, "W"), "Start Point": (-3.64, 50.22, "S"),
    "North Foreland": (1.45, 51.38, "NE"), "South Foreland": (1.37, 51.14, "SE"), "Dungeness": (0.97, 50.91, "SE"),
    "Beachy Head": (0.24, 50.74, "S"), "Orford Ness": (1.58, 52.08, "E"), "Lowestoft Ness": (1.76, 52.48, "E"),
    "Carnsore Point": (-6.36, 52.17, "SE"), "Wicklow Head": (-5.99, 52.96, "E"), "Howth Head": (-6.05, 53.37, "E"),
    "Hook Head": (-6.93, 52.12, "S"), "St Ann's Head": (-5.17, 51.68, "SW"), "Pointe de Barfleur": (-1.27, 49.70, "NE"),
    "Cap Frehel": (-2.32, 48.68, "N"), "Pointe de Penmarch": (-4.37, 47.80, "SW"), "Cabo Ortegal": (-7.87, 43.77, "N"),
    "Cabo de Penas": (-5.85, 43.66, "N"), "Cap de Creus": (3.32, 42.32, "E"), "Pointe de Grave": (-1.06, 45.57, "N"),
    "Cap Sicie": (5.86, 43.05, "S"), "Flamborough Head": (-0.08, 54.12, "E"), "Mull of Galloway": (-4.86, 54.64, "S"),
    "St Bees Head": (-3.64, 54.51, "W"), "Ile de Re west tip": (-1.56, 46.24, "W"), "Cabo da Roca": (-9.50, 38.78, "W")}
MOUTHS = ["Thames", "Severn", "Seine", "Loire", "Garonne", "Rhône", "Po", "Ebro", "Shannon", "Elbe", "Schelde", "Dordogne"]
CONFL = [("Rhine", "Mosel", "Koblenz"), ("Rhine", "Main", "Mainz"), ("Seine", "Marne", "Charenton"), ("Seine", "Yonne", "Montereau"),
         ("Loire", "Vienne", "Candes"), ("Garonne", "Dordogne", "Bec d'Ambès"), ("Po", "Ticino", "Pavia"), ("Severn", "Avon", "Tewkesbury"),
         ("Rhône", "Durance", "Avignon"), ("Rhine", "Maas", "Rhine-Maas delta")]
ALIAS = {"Rhine": {"Rhine", "Rhein", "Rhin"}}

def load_rivers(bbox):
    recs = V1.read_dbf(f"{NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.dbf"); out = {}
    for i, parts in V1.read_shp(f"{NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp", bbox):
        nm = MM._nm(recs[i].get("name", ""))
        for k in set([nm]) | {a for a, s in ALIAS.items() if nm in s}:
            out.setdefault(k, []).extend(LineString(p) for p in parts if len(p) > 1)
    return {k: MultiLineString(v) for k, v in out.items()}

def load_coast(bbox):
    polys = []
    for i, parts in V1.read_shp(f"{NE}/ne_10m_land/ne_10m_land.shp", bbox):
        for p in parts:
            if len(p) > 3: polys.append(Polygon(p).buffer(0))
    return unary_union(polys)

def candidates(F, rivers, land):
    C = []
    for nm, d in HEADLANDS.items():
        g = GAZ[nm]; C.append(dict(type="headland", name=nm, lon=g["lon"], lat=g["lat"], qid=g["qid"], dir=d, source="engine gazetteer (Wikidata P625)"))
    coast = land.boundary
    for nm, (lo, la, d) in EXTRA_HEADLANDS.items():
        q = nearest_points(Point(lo, la), coast)[1]
        if Point(lo, la).distance(q) * 111 > 15: continue
        C.append(dict(type="headland", name=nm, lon=round(q.x, 4), lat=round(q.y, 4), dir=d, source="NE10m coast vertex nearest an approximate position (no Wikidata P625; geodata is the truth)"))
    for r in MOUTHS:
        if r not in rivers: continue
        ends = [Point(c) for ln in rivers[r].geoms for c in (ln.coords[0], ln.coords[-1])]
        e = min(ends, key=lambda p: p.distance(coast)); dd = e.distance(coast)
        if dd > 0.35: continue
        C.append(dict(type="river_mouth", name=f"{r} mouth", lon=round(e.x, 4), lat=round(e.y, 4), source=f"NE10m centerline end nearest coast ({dd * 111:.1f} km)"))
    for a, b, place in CONFL:
        if a not in rivers or b not in rivers: continue
        pa, pb = nearest_points(rivers[a], rivers[b]); dd = pa.distance(pb)
        if dd > 0.03: continue
        C.append(dict(type="confluence", name=f"{a}-{b} ({place})", lon=round(pa.x, 4), lat=round(pa.y, 4), source="NE10m centerlines, nearest approach < 3 km"))
    return C

def select(F, C, pins, n_target=26):
    W, H = F.W, F.H; m = 0.05
    def inside(x, y): return m * W <= x <= (1 - m) * W and m * H <= y <= (1 - m) * H
    pool = []
    for c in C + [dict(type="settlement", name=p["name"], lon=p["lon"], lat=p["lat"], qid=p["qid"], source="MAP-PLACES-v1 P625 (pin)") for p in pins]:
        x, y = F.px(c["lon"], c["lat"])
        if inside(x, y): pool.append(dict(c, px=[round(float(x), 1), round(float(y), 1)]))
    # greedy farthest-point, typed: headlands/mouths first (they're what a painter keeps), settlements fill gaps
    pri = {"headland": 0, "river_mouth": 0, "confluence": 1, "settlement": 2}
    pool.sort(key=lambda c: pri[c["type"]]); sel = []
    min_sep = 0.045 * min(W, H)
    for tier in (0, 1):
        for c in [c for c in pool if pri[c["type"]] == tier]:
            if all(math.dist(c["px"], s["px"]) >= min_sep for s in sel): sel.append(c)
    if len(sel) > 28:   # thin by farthest-point
        keep = [sel[0]]
        while len(keep) < 28:
            keep.append(max((c for c in sel if c not in keep), key=lambda c: min(math.dist(c["px"], k["px"]) for k in keep)))
        sel = keep
    sel += [dict(c, role="secondary") for c in pool if c["type"] == "settlement" and c not in sel]
    for i, c in enumerate(sel):
        c.setdefault("role", "secondary" if c["type"] == "settlement" else "primary")
        c["id"] = f"CP{i + 1:02d}"; c["plate_px"] = [round(2 * c["px"][0], 1), round(2 * c["px"][1], 1)]
        c["search_px_out"] = 40 if c["type"] != "settlement" else 60
    return sel

# ------------------------------------------------------------------ prototype
def synth_warp(img, seed, amp_px, bulge):
    H, W = img.shape[:2]; rng = np.random.default_rng(seed)
    th = math.radians(0.9); s = 1.025
    A = np.float64([[s * math.cos(th), -s * math.sin(th), 0], [s * math.sin(th), s * math.cos(th), 0]])
    c = np.float64([W / 2, H / 2]); A[:, 2] = c - A[:, :2] @ c + np.float64([14, -9])
    dx = gaussian_filter(rng.standard_normal((H, W)), 0.15 * min(W, H)); dy = gaussian_filter(rng.standard_normal((H, W)), 0.15 * min(W, H))
    dx *= amp_px / (np.abs(dx).max() + 1e-9); dy *= amp_px / (np.abs(dy).max() + 1e-9)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float64)
    bx, by, br, bd = bulge   # one local 'generation distortion' (e.g. a headland drawn too far out)
    g = np.exp(-((X - bx) ** 2 + (Y - by) ** 2) / (2 * br ** 2)); dx += bd[0] * g; dy += bd[1] * g
    # forward map ref->plate: p = A·(x,y) + d(x,y).  Build the plate by inverse sampling (fixed-point iteration).
    def fwd(x, y):
        dxx = cv2.remap(dx.astype(np.float32), x.astype(np.float32), y.astype(np.float32), cv2.INTER_LINEAR)
        dyy = cv2.remap(dy.astype(np.float32), x.astype(np.float32), y.astype(np.float32), cv2.INTER_LINEAR)
        return A[0, 0] * x + A[0, 1] * y + A[0, 2] + dxx, A[1, 0] * x + A[1, 1] * y + A[1, 2] + dyy
    Ai = cv2.invertAffineTransform(A); sx = Ai[0, 0] * X + Ai[0, 1] * Y + Ai[0, 2]; sy = Ai[1, 0] * X + Ai[1, 1] * Y + Ai[1, 2]
    for _ in range(6):
        fx, fy = fwd(sx, sy); sx -= (Ai[0, 0] * (fx - X) + Ai[0, 1] * (fy - Y)); sy -= (Ai[1, 0] * (fx - X) + Ai[1, 1] * (fy - Y))
    plate = cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return plate, fwd

def grad(im):
    g = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY).astype(np.float32)
    return cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))

def register(ref, plate, cps, kmpp):
    H, W = ref.shape[:2]
    orb = cv2.ORB_create(6000); g1 = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY); g2 = cv2.cvtColor(plate, cv2.COLOR_RGB2GRAY)
    k1, d1 = orb.detectAndCompute(g1, None); k2, d2 = orb.detectAndCompute(g2, None)
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2)
    P1 = np.float32([k1[x.queryIdx].pt for x in m]); P2 = np.float32([k2[x.trainIdx].pt for x in m])
    A, inl = cv2.estimateAffine2D(P1, P2, method=cv2.RANSAC, ransacReprojThreshold=6.0, maxIters=5000)
    G1, G2 = grad(ref), grad(plate); meas = []
    # flat (zero-variance) sea windows make TM_CCOEFF_NORMED return a spurious 1.0 -> add a tiny fixed dither
    rng = np.random.default_rng(7); G1 = G1 + rng.random(G1.shape, dtype=np.float32) * 0.5; G2 = G2 + rng.random(G2.shape, dtype=np.float32) * 0.5
    for c in cps:
        if c["role"] != "primary": meas.append(None); continue
        x, y = c["px"]; r = 28; s = c["search_px_out"]
        px, py = A @ np.float64([x, y, 1])
        x0, y0 = int(x) - r, int(y) - r
        if x0 < 0 or y0 < 0 or x0 + 2 * r >= W or y0 + 2 * r >= H: meas.append(None); continue
        T = G1[y0:y0 + 2 * r, x0:x0 + 2 * r]
        sx0, sy0 = int(px) - r - s, int(py) - r - s
        sx0c, sy0c = max(0, sx0), max(0, sy0); S = G2[sy0c:min(H, int(py) + r + s), sx0c:min(W, int(px) + r + s)]
        if S.shape[0] <= T.shape[0] or S.shape[1] <= T.shape[1] or T.std() < 1e-3: meas.append(None); continue
        R = cv2.matchTemplate(S, T, cv2.TM_CCOEFF_NORMED); _, mv, _, ml = cv2.minMaxLoc(R)
        # sub-pixel peak
        ix, iy = ml; ox = oy = 0.0
        if 0 < ix < R.shape[1] - 1: a_, b_, c_ = R[iy, ix - 1], R[iy, ix], R[iy, ix + 1]; ox = 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_ + 1e-9)
        if 0 < iy < R.shape[0] - 1: a_, b_, c_ = R[iy - 1, ix], R[iy, ix], R[iy + 1, ix]; oy = 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_ + 1e-9)
        meas.append(dict(xy=[sx0c + ix + ox + r + (x - int(x)), sy0c + iy + oy + r + (y - int(y))], ncc=float(mv)))
    ok = [i for i, q in enumerate(meas) if q and q["ncc"] >= 0.6]
    # robust loop: a point whose leave-one-out residual is > REJECT_PX and the worst is dropped from the FIT
    # (kept in the report as 'rejected' -> it is exactly the place that needs a local correction or a regen)
    rejected = []
    def loo_of(idx):
        sr = np.float64([cps[i]["px"] for i in idx]); ds = np.float64([meas[i]["xy"] for i in idx]); out = []
        for j in range(len(idx)):
            msk = np.arange(len(idx)) != j
            f = RBFInterpolator(sr[msk], ds[msk], kernel="thin_plate_spline", smoothing=SMOOTH)
            out.append(float(np.linalg.norm(f(sr[j:j + 1])[0] - ds[j])))
        return np.float64(out)
    while True:
        loo = loo_of(ok); j = int(np.argmax(loo))
        if loo[j] <= REJECT_PX or len(ok) <= 12: break
        rejected.append(ok.pop(j))
    src = np.float64([cps[i]["px"] for i in ok]); dst = np.float64([meas[i]["xy"] for i in ok])
    tps = RBFInterpolator(src, dst, kernel="thin_plate_spline", smoothing=SMOOTH)
    aff_res = np.linalg.norm(np.c_[src, np.ones(len(src))] @ A.T - dst, axis=1)
    return dict(rejected=rejected, A=A, n_orb=len(m), n_inl=int(inl.sum()), meas=meas, ok=ok, tps=tps, src=src, dst=dst, loo=np.float64(loo), aff_res=aff_res)

def qa_level(e_px, e_km, th):
    if e_px <= th["pass_px"] and e_km <= th["pass_km"]: return "pass"
    if e_px <= th["flag_px"] and e_km <= th["flag_km"]: return "flag"
    return "fail"

THRESH = {"euro": dict(pass_px=4, flag_px=8, pass_km=7, flag_km=13), "britain": dict(pass_px=4, flag_px=8, pass_km=1.6, flag_km=3.0)}
SMOOTH = 5.0; REJECT_PX = 12.0
WARP_LIMIT_FRAC = 0.025   # non-affine TPS displacement above 2.5 % of min(W,H) at any control point = painting geometry problem

def main():
    out_cp = dict(name=f"control_points_refpack_{TAG}", px_space="out px of the frame (plate px = 2x, also given)",
                  thresholds=THRESH, warp_limit_frac_of_min_side=WARP_LIMIT_FRAC, frames={})
    for name, fr in J["frames"].items():
        c, wkm = fr["center_lonlat"], fr["width_km"]; W, H = fr["size_px"]; F = Frame(name, tuple(c), wkm, W, H)
        kind = "euro" if name.startswith("euro") else "britain"
        bbox = F.geom.lonlat_bbox(); rivers = load_rivers(bbox); land = load_coast(bbox)
        pins, regions, _ = stops_for(kind)
        cps = select(F, candidates(F, rivers, land), pins)
        # ---- prototype
        ref = cv2.cvtColor(cv2.imread(os.path.join(HERE, fr["files"]["tinted_notext"])), cv2.COLOR_BGR2RGB)
        bul = max(cps, key=lambda q: q["type"] == "headland" and 0.2 * W < q["px"][0] < 0.8 * W)   # distort one headland region
        bd = (0.022 * min(W, H), 0.012 * min(W, H))
        plate, fwd = synth_warp(ref, 1327, 0.012 * min(W, H), (bul["px"][0], bul["px"][1], 0.035 * min(W, H), bd))
        R = register(ref, plate, cps, F.geom.km_per_px); kmpp = F.geom.km_per_px; th = THRESH[kind]
        truth = {i: np.float64([float(np.ravel(v)[0]) for v in fwd(np.float64([[cps[i]["px"][0]]]), np.float64([[cps[i]["px"][1]]]))]) for i in range(len(cps))}
        affd = np.c_[R["src"], np.ones(len(R["src"]))] @ R["A"].T
        nonaff = np.linalg.norm(R["dst"] - affd, axis=1)
        rows = []
        for k, i in enumerate(R["ok"]):
            e = float(R["loo"][k]); merr = float(np.linalg.norm(np.float64(R["meas"][i]["xy"]) - truth[i]))
            lvl = qa_level(e, e * kmpp, th); warp_flag = nonaff[k] > WARP_LIMIT_FRAC * min(W, H)
            rows.append(dict(id=cps[i]["id"], name=cps[i]["name"], ncc=round(R["meas"][i]["ncc"], 3), match_err_vs_truth_px=round(merr, 2),
                             loo_residual_px=round(e, 2), loo_residual_km=round(e * kmpp, 2), nonaffine_px=round(float(nonaff[k]), 2),
                             affine_only_residual_px=round(float(R["aff_res"][k]), 2), qa=lvl, warp_limit_exceeded=bool(warp_flag)))
        rej_rows = []
        for i in R["rejected"]:
            mxy = np.float64(R["meas"][i]["xy"]); e = float(np.linalg.norm(R["tps"](np.float64([cps[i]["px"]]))[0] - mxy))
            na_ = float(np.linalg.norm(mxy - R["A"] @ np.float64([cps[i]["px"][0], cps[i]["px"][1], 1])))
            rej_rows.append(dict(id=cps[i]["id"], name=cps[i]["name"], ncc=round(R["meas"][i]["ncc"], 3),
                                 match_err_vs_truth_px=round(float(np.linalg.norm(mxy - truth[i])), 2),
                                 residual_vs_final_fit_px=round(e, 2), residual_vs_final_fit_km=round(e * kmpp, 2), nonaffine_px=round(na_, 2),
                                 qa=qa_level(e, e * kmpp, th), warp_limit_exceeded=bool(na_ > WARP_LIMIT_FRAC * min(W, H)),
                                 action="local correction: the plate disagrees with the geodata here (or the match is wrong) - inspect overlay"))
        unmatched = [cps[i]["id"] for i in range(len(cps)) if i not in R["ok"] and i not in R["rejected"] and cps[i]["role"] == "primary"]
        lm0 = V1.raster_polys(F.geom, f"{NE}/ne_10m_land/ne_10m_land.shp", bbox) > 0.5
        ce = cv2.morphologyEx(lm0.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
        cy, cx = np.nonzero(ce); sel_ = (cx > 0.04 * W) & (cx < 0.96 * W) & (cy > 0.04 * H) & (cy < 0.96 * H); cy, cx = cy[sel_][::7], cx[sel_][::7]
        tx, ty = fwd(cx.astype(np.float64)[None], cy.astype(np.float64)[None]); tr = np.c_[np.ravel(tx), np.ravel(ty)]
        pt = np.c_[cx, cy].astype(np.float64)
        dense_tps = np.linalg.norm(R["tps"](pt) - tr, axis=1); dense_aff = np.linalg.norm(np.c_[pt, np.ones(len(pt))] @ R["A"].T - tr, axis=1)
        # ---- QA overlay: plate resampled into reference space with the TPS (ref px -> plate px), NE coastline on top
        Y, X = np.mgrid[0:H, 0:W]; g = np.c_[X.ravel(), Y.ravel()].astype(np.float64)
        step = 8; ys, xs = np.mgrid[0:H:step, 0:W:step]; gs = np.c_[xs.ravel(), ys.ravel()].astype(np.float64)
        m = R["tps"](gs).reshape(ys.shape + (2,)).astype(np.float32)
        mx = cv2.resize(m[..., 0], (W, H), interpolation=cv2.INTER_LINEAR); my = cv2.resize(m[..., 1], (W, H), interpolation=cv2.INTER_LINEAR)
        reg = cv2.remap(plate, mx, my, cv2.INTER_LINEAR)
        lm = V1.raster_polys(F.geom, f"{NE}/ne_10m_land/ne_10m_land.shp", bbox) > 0.5
        edge = cv2.morphologyEx(lm.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
        qa = (0.75 * reg + 0.25 * 255).astype(np.uint8); qa[edge] = (200, 30, 30)
        col = {"pass": (30, 150, 60), "flag": (230, 150, 0), "fail": (210, 20, 20)}
        for c_ in cps:
            if c_["role"] == "secondary": cv2.drawMarker(qa, (int(c_["px"][0]), int(c_["px"][1])), (90, 90, 90), cv2.MARKER_TILTED_CROSS, 10, 1)
        for r_, k in zip(rows, R["ok"]):
            x, y = cps[k]["px"]; e = R["dst"][R["ok"].index(k)] if False else None
            j = R["ok"].index(k); pred = R["tps"](R["src"][j:j + 1])[0]
            cv2.circle(qa, (int(x), int(y)), 9, col[r_["qa"]], 2, cv2.LINE_AA)
            cv2.putText(qa, f'{r_["id"]} {r_["loo_residual_px"]:.1f}', (int(x) + 11, int(y) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col[r_["qa"]], 1, cv2.LINE_AA)
            na = R["dst"][j] - affd[j]; cv2.arrowedLine(qa, (int(x), int(y)), (int(x + 4 * na[0]), int(y + 4 * na[1])), (40, 40, 160), 2, cv2.LINE_AA, tipLength=0.25)
        for r_ in rej_rows:
            c_ = next(q for q in cps if q["id"] == r_["id"]); x, y = c_["px"]
            cv2.drawMarker(qa, (int(x), int(y)), (200, 0, 200), cv2.MARKER_TILTED_CROSS, 18, 2)
            cv2.putText(qa, f'{r_["id"]} REJ {r_["residual_vs_final_fit_px"]:.0f}', (int(x) + 11, int(y) + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 0, 200), 1, cv2.LINE_AA)
        cv2.putText(qa, f"{name} synthetic-warp prototype: red = NE10m coast, circles = control points (LOO residual px), blue arrows = non-affine warp x4, magenta X = rejected from fit",
                    (20, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2, cv2.LINE_AA)
        p_plate = os.path.join(IMG, f"{name}_regproto_synthetic_plate.png"); p_qa = os.path.join(IMG, f"{name}_regproto_qa_overlay.png")
        for p_, im in ((p_plate, plate), (p_qa, qa)):
            assert not os.path.exists(p_), p_
            cv2.imwrite(p_, cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        lo = R["loo"]
        out_cp["frames"][name] = dict(control_points=cps, prototype=dict(
            synthetic_warp="affine (scale 1.025, rot 0.9 deg, shift 14,-9 px) + smooth random field (max %.0f px) + one local bulge at %s (%.0f,%.0f px)" % (0.012 * min(W, H), bul["name"], bd[0], bd[1]),
            orb_matches=R["n_orb"], orb_inliers=R["n_inl"], matched=len(R["ok"]), unmatched=unmatched,
            loo_rms_px=round(float(np.sqrt((lo ** 2).mean())), 2), loo_max_px=round(float(lo.max()), 2),
            loo_rms_km=round(float(np.sqrt((lo ** 2).mean()) * kmpp), 2), loo_max_km=round(float(lo.max() * kmpp), 2),
            affine_only_rms_px=round(float(np.sqrt((R["aff_res"] ** 2).mean())), 2),
            match_err_vs_truth_rms_px=round(float(np.sqrt(np.mean([r_["match_err_vs_truth_px"] ** 2 for r_ in rows]))), 2),
            coast_true_error_px=dict(tps_median=round(float(np.median(dense_tps)), 2), tps_p95=round(float(np.percentile(dense_tps, 95)), 2), tps_max=round(float(dense_tps.max()), 2),
                                     affine_median=round(float(np.median(dense_aff)), 2), affine_p95=round(float(np.percentile(dense_aff, 95)), 2), n=int(len(pt)),
                                     note="synthetic truth known: |registered - true| at every 7th NE coastline pixel inside the frame"),
            counts={q: sum(r_["qa"] == q for r_ in rows) for q in ("pass", "flag", "fail")},
            rejected_from_fit=rej_rows, robust=dict(smoothing=SMOOTH, reject_loo_px=REJECT_PX, min_points=12),
            warp_limit_exceeded=[r_["id"] for r_ in rows + rej_rows if r_["warp_limit_exceeded"]], points=rows,
            files=dict(synthetic_plate=os.path.relpath(p_plate, OUTD), qa_overlay=os.path.relpath(p_qa, OUTD))))
        pr = out_cp["frames"][name]["prototype"]
        print(name, len(cps), {t: sum(c_["type"] == t for c_ in cps) for t in ("headland", "river_mouth", "confluence", "settlement")},
              "matched", pr["matched"], "loo rms/max", pr["loo_rms_px"], pr["loo_max_px"], "aff", pr["affine_only_rms_px"], "truth", pr["match_err_vs_truth_rms_px"], pr["coast_true_error_px"], pr["counts"], pr["warp_limit_exceeded"], [(r["name"], r["match_err_vs_truth_px"], r["residual_vs_final_fit_px"]) for r in pr["rejected_from_fit"]])
    p = os.path.join(OUTD, f"control_points_refpack_{TAG}.json")
    json.dump(out_cp, open(p, "x"), indent=1, default=lambda o: None); print(p)

if __name__ == "__main__":
    main()
