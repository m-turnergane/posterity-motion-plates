#!/usr/bin/env python3
"""P05 atlas reference generator (Bjorn Ironside short). No AI imagery: every pixel is drawn from
Natural Earth vectors, OpenHistoricalMap relations (CC0) and hand-traced realm polygons (Shepherd 1911/1923 pl. 56).
Source of truth for points / segments / styles: ../map-reference-data.md (Archivist, 2026-11-03).

    python make_p05_reference.py OUTDIR      # refuses to overwrite any existing output file
"""
import json, math, os, sys
import numpy as np, cv2, shapefile
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union, linemerge, substring
from shapely.prepared import prep
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lcc import LCC

HERE = os.path.dirname(os.path.abspath(__file__))
NE = "/workspace/posterity/engine-rnd/maps/sources/naturalearth"
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
PROJ = LCC(37.0, 46.0, 41.25, 2.25)
SIZES = [(1080, 1920), (2160, 3840)]
FONT = "/usr/share/fonts/truetype/dejavu/"

# --------------------------------------------------------------------------------------------- data (Archivist)
# id: (label, lat, lon, wikidata, show_label, pin)
PTS = {
 "P1": ("Loire", 47.2700, -2.1844, "Q1469", True, True),
 "P2": ("Galicia", 42.8000, -7.9000, "Q3908", True, False),
 "P3": ("Asturias", 43.3614, -5.8478, "Q3934", False, False),
 "P4": ("Beja", 38.0167, -7.8667, "Q321455", False, False),
 "P5": ("Guadalquivir", 36.7913, -6.3567, "Q14309", True, True),
 "P6": ("Seville", 37.3886, -5.9950, "Q8717", True, True),
 "P7": ("Algeciras", 36.1275, -5.4539, "Q484552", True, True),
 "P8": ("Strait of Gibraltar", 35.9739, -5.5161, "Q36124", True, False),
 "P9": ("Nekor", 35.0898, -3.8075, "Q3537816", True, True),
 "P10": ("Orihuela", 38.0848, -0.9440, "Q24008496", True, True),
 "P11": ("Mallorca", 39.6167, 2.9833, "Q8828", True, True),
 "P12": ("Menorca", 39.9667, 4.0833, "Q52636", True, True),
 "P13": ("Formentera", 38.7000, 1.4500, "Q31916364", True, True),
 "P14": ("Camargue", 43.5333, 4.5000, "Q218151", True, True),
 "P15": ("Rhône", 43.3342, 4.8442, "Q602", True, False),
 "P16": ("Valence", 44.9325, 4.8908, "Q8848", True, True),
 "P17": ("Pisa", 43.7167, 10.4000, "Q13375", True, True),
 "P18": ("", 44.0640, 10.0170, "Q579763", False, True),          # Luna: UNLABELLED pin
 "P19": ("Rome", 41.8931, 12.4828, "Q220", True, True),
 "P20": ("Medina Sidonia", 36.4577, -5.9273, "Q642200", False, False),
 "P21": ("Pamplona", 42.8167, -1.6500, "Q10282", True, True),
 "P22": ("Nîmes", 43.8383, 4.3597, "Q42807", False, False),
 "P23": ("Arles", 43.6769, 4.6286, "Q48292", False, False),
}
PT_NOTE = {"P18": "Luna (Roman city site). UNLABELLED pin; must not be marked as the on-screen route end.",
           "P4": "Not pinned (harbour unidentified).", "P22": "Not plotted (D6).", "P23": "Not plotted (D6); used only as a Rhône routing vertex.",
           "P20": "Inland town, not pinned. The 861 battle 'on the coast of Sidona' is the offshore event mark E_SIDONA.",
           "P2": "Region centroid, label only.", "P3": "Region point, realm label only.", "P15": "Entry waypoint; label 'Rhône'.",
           "P8": "Waypoint, optional label."}
EXTRA = {  # derived marks (not Wikidata items) -- documented here and in REFERENCE-NOTES
 "E_SIDONA": ("", 36.36, -6.36, None, "Offshore event mark for the 861 battle 'on the coast of Sidona' (P20 note: offshore, west of P7). Position is a desk choice off Cadiz bay / Sancti Petri."),
 "MAGRA_MOUTH": ("", 44.0455, 9.9891, "Q692549", "Magra mouth (Archivist P18 note). Reference only."),
}
# sea anchors (desk choices, offshore of the named place; used only to steer the sea routing)
ANCH = {"loire": (-2.42, 47.17), "galicia": (-9.45, 43.0), "beja": (-9.0, 37.95), "gq": (-6.47, 36.76),
        "alg": (-5.41, 36.10), "strait": (-5.5161, 35.9739), "nekor": (-3.88, 35.26), "segura": (-0.58, 38.10),
        "form": (1.45, 38.58), "mall": (2.62, 39.42), "men": (4.10, 39.80), "rhone": (4.86, 43.28),
        "magra": (9.95, 44.0), "arno": (10.20, 43.68), "tiber": (12.15, 41.70), "sidona": (-6.36, 36.36)}
BANDS = {"solid": "DOCUMENTED", "dotted": "UNCERTAIN", "broken": "LEGEND", "marker": "UNCERTAIN"}

# --------------------------------------------------------------------------------------------- geometry helpers
def P(lon, lat): x, y = PROJ.fwd(lon, lat); return float(x), float(y)
def Parr(a): a = np.asarray(a, float); x, y = PROJ.fwd(a[:, 0], a[:, 1]); return np.c_[x, y]
def Iarr(a): a = np.asarray(a, float); lo, la = PROJ.inv(a[:, 0], a[:, 1]); return np.c_[lo, la]

def box_xy(W, E, S, N, n=80):
    t = np.linspace(0, 1, n)
    ring = np.r_[np.c_[W + (E - W) * t, np.full(n, S)], np.c_[np.full(n, E), S + (N - S) * t],
                 np.c_[E - (E - W) * t, np.full(n, N)], np.c_[np.full(n, W), N - (N - S) * t]]
    return Parr(ring)

def fit916(W, E, S, N, margin=0.0):
    """smallest 9:16 rectangle (projected metres) containing the lon/lat box, centred on it."""
    xy = box_xy(W, E, S, N); x0, y0 = xy.min(0); x1, y1 = xy.max(0)
    w, h = (x1 - x0) * (1 + margin), (y1 - y0) * (1 + margin)
    w = max(w, h * 9 / 16); h = w * 16 / 9
    return dict(cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, w=w, h=h, box=[W, E, S, N])

class Frame:
    def __init__(s, name, rect, W, H):
        s.name, s.W, s.H = name, W, H; s.mpp = rect["w"] / W
        s.x0 = rect["cx"] - rect["w"] / 2; s.y1 = rect["cy"] + rect["h"] / 2; s.rect = rect
    def px(s, xy): xy = np.asarray(xy, float); return np.c_[(xy[:, 0] - s.x0) / s.mpp, (s.y1 - xy[:, 1]) / s.mpp]
    def pll(s, lon, lat): return s.px([P(lon, lat)])[0]
    def rect_px(s, r):
        return [round((r["cx"] - r["w"] / 2 - s.x0) / s.mpp, 1), round((s.y1 - (r["cy"] + r["h"] / 2)) / s.mpp, 1),
                round(r["w"] / s.mpp, 1), round(r["h"] / s.mpp, 1)]
    def bounds_ll(s):
        xs = [s.x0, s.x0 + s.W * s.mpp]; ys = [s.y1 - s.H * s.mpp, s.y1]
        c = Iarr([[xs[0], ys[1]], [xs[1], ys[1]], [xs[1], ys[0]], [xs[0], ys[0]]])
        return {k: [round(float(v[0]), 4), round(float(v[1]), 4)] for k, v in zip(["top_left", "top_right", "bottom_right", "bottom_left"], c)}

# --------------------------------------------------------------------------------------------- Natural Earth
CLIP_LL = box(-32, 14, 45, 74)
def read_polys(path, pred=None):
    r = shapefile.Reader(path); out = []
    fields = [f[0] for f in r.fields[1:]]
    for sr in r.iterShapeRecords():
        d = dict(zip(fields, sr.record))
        if pred and not pred(d): continue
        g = shape(sr.shape.__geo_interface__)
        if not g.is_valid: g = g.buffer(0)
        g = g.intersection(CLIP_LL)
        if not g.is_empty: out.append(g)
    return unary_union(out)

def read_lines(path, names):
    r = shapefile.Reader(path); fields = [f[0] for f in r.fields[1:]]; out = {}
    for sr in r.iterShapeRecords():
        d = dict(zip(fields, sr.record)); n = d.get("name")
        b = sr.shape.bbox
        if n in names and b[0] < 17 and b[2] > -12 and b[1] < 52 and b[3] > 34:
            g = shape(sr.shape.__geo_interface__)
            out.setdefault(n, []).append(g)
    def _m(v):
        u = unary_union(v)
        return linemerge(u) if u.geom_type == "MultiLineString" else u
    return {k: _m(v) for k, v in out.items()}

print("loading Natural Earth ...")
LAND = read_polys(f"{NE}/ne_10m_land/ne_10m_land.shp")
LAKES = read_polys(f"{NE}/ne_10m_lakes/ne_10m_lakes.shp", lambda d: float(d.get("scalerank", 9) or 9) <= 8)
LAND_P = prep(LAND)
RIV_KEY = ["Seine", "Loire", "Rhône", "Tevere", "Guadalquivir"]
RIV_CTX = ["Ebro", "Garonne", "Po", "Duero", "Tajo", "Rhin", "Rhine", "Rhein"]
RIV = read_lines(f"{NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp", RIV_KEY + RIV_CTX)
RIV.update(read_lines(f"{HERE}/sources/ne_10m_rivers_europe/ne_10m_rivers_europe.shp", ["Arno", "Segura"]))

# --------------------------------------------------------------------------------------------- realms c.860
OHM = json.load(open(f"{HERE}/sources/ohm_860_polygons.json"))
def ohm(rid):
    g = shape(OHM[str(rid)]["geom"]); return g if g.is_valid else g.buffer(0)
def parts(g): return list(g.geoms) if hasattr(g, "geoms") else [g]
def keep(g, f): return unary_union([p for p in parts(g) if f(p.representative_point())])

# hand traces after Shepherd pl.56 "Disruption of the Carolingian Empire 843-888" (lon, lat)
PROVENCE = Polygon([(4.37, 43.40), (4.36, 43.55), (4.47, 43.66), (4.61, 43.70), (4.66, 43.90), (4.72, 44.20), (4.69, 44.50),
    (4.76, 44.76), (4.84, 45.00), (4.79, 45.30), (4.78, 45.55), (4.82, 45.76), (4.76, 46.10), (4.88, 46.33), (5.45, 46.30),
    (5.90, 46.15), (6.80, 45.80), (7.10, 45.20), (6.90, 44.50), (7.60, 44.00), (7.62, 43.70), (7.0, 42.6), (4.4, 42.6)])
ITALY = Polygon([(7.62, 43.70), (7.60, 44.00), (6.90, 44.50), (7.10, 45.20), (6.80, 45.80), (7.0, 45.95), (7.9, 46.0), (8.4, 46.45),
    (9.0, 46.5), (10.0, 46.6), (10.5, 46.85), (11.5, 47.0), (12.4, 46.8), (13.7, 46.5), (13.9, 45.6), (13.4, 44.6), (14.25, 42.47),
    (13.9, 42.10), (13.5, 41.75), (12.3, 41.2), (11.2, 41.9), (9.95, 43.30), (9.4, 43.6), (7.9, 43.5)])
EAST_FRANCIA = Polygon([(7.0, 54.0), (8.6, 53.9), (9.0, 54.35), (10.2, 54.35), (10.8, 53.9), (11.3, 53.1), (11.9, 52.0), (11.9, 51.2),
    (12.3, 50.3), (12.4, 49.8), (13.0, 49.1), (13.8, 48.7), (14.8, 48.7), (16.5, 48.3), (16.5, 46.7), (15.0, 46.4), (13.7, 46.5),
    (12.4, 46.8), (10.5, 46.85), (10.0, 46.6), (9.0, 46.5), (8.4, 46.45), (7.9, 46.0), (7.0, 45.95), (6.5, 47.0), (6.5, 51.0)])

def build_realms():
    lot = ohm(2806711); papal = ohm(2888203); ben = ohm(2888914); ven = ohm(2839584)
    wf = keep(ohm(2750107), lambda p: p.y > 41.0).difference(PROVENCE)            # drop Balearic part (S39.09 artefact)
    prov = PROVENCE.difference(lot)
    byz = keep(ohm(2860243), lambda p: p.x > 8.0)                                     # drop Balearics (W1.14 artefact)
    ita = ITALY.difference(unary_union([papal, ben, ven, byz, prov, lot]))
    ef = EAST_FRANCIA.difference(unary_union([lot, ita, prov, ven]))
    R = [  # id, key, label, geom, rgb, source
     (1, "west_francia", "West Francia", wf, (176, 96, 70), "OHM 2750107 (843-867), parts south of 41N removed"),
     (2, "brittany", "Brittany", ohm(2805415), (118, 98, 156), "OHM 2805415 (851-867)"),
     (3, "lotharingia", "Lotharingia", lot, (96, 132, 86), "OHM 2806711 (855-870)"),
     (4, "provence", "Provence", prov, (204, 128, 40), "hand trace after Shepherd pl.56; not in OHM"),
     (5, "italy", "Kingdom of Italy", ita, (70, 112, 164), "hand trace after Shepherd pl.56; not in OHM"),
     (6, "east_francia", "East Francia", ef, (128, 128, 92), "hand trace after Shepherd pl.56; not in OHM"),
     (7, "papal", "Papal lands", papal, (158, 62, 96), "OHM 2888203 (800-988)"),
     (8, "benevento", "Benevento", ben, (130, 96, 60), "OHM 2888914 (851-899)"),
     (9, "naples", "Naples", unary_union([ohm(2888433), ohm(2888516)]), (80, 124, 128), "OHM 2888433 + 2888516"),
     (10, "bari", "Emirate of Bari", ohm(2860176), (52, 116, 72), "OHM 2860176 (847-871)"),
     (11, "byzantine", "Byzantine", byz, (124, 72, 142), "OHM 2860243 (847-871), parts west of 8E removed"),
     (12, "aghlabids", "Aghlabids", ohm(2860230), (40, 112, 132), "OHM 2860230 (846-870); Sicily hatched (conquest in progress)"),
     (13, "cordoba", "Emirate of Córdoba", ohm(2697816), (78, 130, 70), "OHM 2697816 (756-902)"),
     (14, "asturias", "Asturias", ohm(2740129), (86, 92, 150), "OHM 2740129 (860-909)"),
     (15, "pamplona", "Pamplona", ohm(2740068), (176, 88, 140), "OHM 2740068 (824-904)"),
     (16, "venice", "Venice", ven, (90, 110, 120), "OHM 2839584 (697-974)"),
    ]
    return [(i, k, l, g.intersection(LAND), c, s) for i, k, l, g, c, s in R]
REALMS = build_realms()
LOOSE_LABELS = [("Nekor", -3.95, 34.78), ("Idrisids", -5.6, 34.15)]  # label only, no fill (Archivist s4)
SICILY = box(12.2, 36.5, 15.8, 38.4)

# --------------------------------------------------------------------------------------------- sea routing
GR = 3000.0   # m per routing cell
gx0, gy0 = P(-14.5, 31.0)[0] - 300e3, P(2.25, 30.0)[1]
gx1, gy1 = P(17.5, 31.0)[0] + 300e3, P(2.25, 50.5)[1]
GW, GH = int((gx1 - gx0) / GR), int((gy1 - gy0) / GR)
def g_ij(x, y): return int(round((gy1 - y) / GR)), int(round((x - gx0) / GR))
def g_xy(i, j): return gx0 + j * GR, gy1 - i * GR

def raster_geom(img, geom, tf, val=255, shift=4):
    f = 1 << shift
    for p in parts(geom):
        if p.is_empty or p.geom_type != "Polygon": continue
        rings = [np.asarray(p.exterior.coords)] + [np.asarray(r.coords) for r in p.interiors]
        pts = [np.round(tf(Parr(r)) * f).astype(np.int32) for r in rings]
        cv2.fillPoly(img, pts, val, cv2.LINE_8, shift)

print("routing grid", GW, GH)
gmask = np.zeros((GH, GW), np.uint8)
raster_geom(gmask, LAND, lambda xy: np.c_[(xy[:, 0] - gx0) / GR, (gy1 - xy[:, 1]) / GR])
gdist = cv2.distanceTransform((gmask == 0).astype(np.uint8), cv2.DIST_L2, 5) * GR / 1000.0   # km to land
ALLOWED = gdist >= 4.0
idx = -np.ones((GH, GW), np.int64); ii, jj = np.nonzero(ALLOWED); idx[ii, jj] = np.arange(len(ii))

def route(a_ll, b_ll, d0=12.0, alpha=0.8, D=80.0):
    cost = 1.0 + alpha * np.minimum(np.abs(gdist - d0), D) / D
    rows, cols, w = [], [], []
    for di, dj in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        A = ALLOWED[max(0, -di):GH - max(0, di), max(0, -dj):GW - max(0, dj)]
        B = ALLOWED[max(0, di):GH - max(0, -di) or None, max(0, dj):GW - max(0, -dj) or None]
        ok = A & B
        ia = idx[max(0, -di):GH - max(0, di), max(0, -dj):GW - max(0, dj)][ok]
        ib = idx[max(0, di):GH - max(0, -di) or None, max(0, dj):GW - max(0, -dj) or None][ok]
        ca = cost[max(0, -di):GH - max(0, di), max(0, -dj):GW - max(0, dj)][ok]
        cb = cost[max(0, di):GH - max(0, -di) or None, max(0, dj):GW - max(0, -dj) or None][ok]
        L = math.hypot(di, dj); rows += [ia, ib]; cols += [ib, ia]; w += [L * (ca + cb) / 2] * 2
    G = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(len(ii), len(ii))).tocsr()
    def snap(ll):
        i, j = g_ij(*P(*ll)); best = None
        for r in range(0, 40):
            sl = ALLOWED[max(0, i - r):i + r + 1, max(0, j - r):j + r + 1]
            if sl.any():
                ci, cj = np.nonzero(sl); ci += max(0, i - r); cj += max(0, j - r)
                k = np.argmin((ci - i) ** 2 + (cj - j) ** 2); return idx[ci[k], cj[k]]
        raise RuntimeError(f"no sea near {ll}")
    s, t = snap(a_ll), snap(b_ll)
    _, pred = dijkstra(G, indices=s, return_predecessors=True)
    path = [t]
    while path[-1] != s:
        path.append(pred[path[-1]]);
        if path[-1] < 0: raise RuntimeError("unreachable")
    path = path[::-1]
    xy = np.array([g_xy(ii[k], jj[k]) for k in path])
    return smooth_safe(np.r_[[P(*a_ll)], xy, [P(*b_ll)]])

def chaikin(a, n):
    for _ in range(n):
        q = 0.75 * a[:-1] + 0.25 * a[1:]; r = 0.25 * a[:-1] + 0.75 * a[1:]
        a = np.r_[a[:1], np.c_[q, r].reshape(-1, 2), a[-1:]]
    return a

def on_land_frac(xy, skip_ends_km=6.0):
    L = LineString(xy); n = max(2, int(L.length / 1000)); bad = 0; pts = []
    for k in range(n + 1):
        d = L.length * k / n
        if d < skip_ends_km * 1e3 or d > L.length - skip_ends_km * 1e3: continue
        p = L.interpolate(d); lo, la = PROJ.inv(p.x, p.y)
        if LAND_P.contains(Point(float(lo), float(la))): bad += 1; pts.append((round(float(lo), 3), round(float(la), 3)))
    return bad, pts

def smooth_safe(xy):
    xy = np.asarray(LineString(xy).simplify(2500).coords)
    for n in (4, 3, 2, 1, 0):
        s = chaikin(xy, n)
        if on_land_frac(s)[0] == 0: return s
    return xy

def river_sub(name, a_ll, b_ll):
    g = RIV[name]
    if g.geom_type == "MultiLineString": g = max(g.geoms, key=lambda q: q.distance(Point(*a_ll)) * -1 if False else -q.length)
    da, db = g.project(Point(*a_ll)), g.project(Point(*b_ll))
    sub = substring(g, min(da, db), max(da, db)); c = np.asarray(sub.coords)
    if da > db: c = c[::-1]
    return Parr(c)

def rhone_sub(a_ll, b_ll):
    g = RIV["Rhône"]; gs = parts(g)
    g = min(gs, key=lambda q: q.distance(Point(4.89, 44.93)))
    da, db = g.project(Point(*a_ll)), g.project(Point(*b_ll))
    c = np.asarray(substring(g, min(da, db), max(da, db)).coords)
    return Parr(c[::-1] if da > db else c)

def cat(*xs):
    out = [np.asarray(xs[0], float)]
    for x in xs[1:]:
        x = np.asarray(x, float)
        if np.hypot(*(out[-1][-1] - x[0])) < 1: x = x[1:]
        out.append(x)
    return np.concatenate(out)
def ll(k): v = PTS[k]; return (v[2], v[1])
def pxy(k): return np.array([P(*ll(k))])
A = ANCH

print("routing segments ...")
SEG = []
def seg(sid, title, years, style, xy, cite, band=None, land_legs=None, extra=None):
    d = dict(id=sid, title=title, years=years, style=style, band=band or BANDS[style], cite=cite, xy=np.asarray(xy, float), land_legs=land_legs or [])
    if extra: d.update(extra)
    SEG.append(d)

seg("S1", "Loire (P1) to Galicia coast (P2)", "859", "dotted", cat(pxy("P1"), route(A["loire"], A["galicia"], d0=14)),
    "AB 859 names no base; Loire base is a modern inference (WP-Nekor line 5); indirect support AB 862 (AB 3645-3647).")
seg("S2", "Galicia coast (P2) south to Beja coast and Guadalquivir mouth (P5)", "859", "solid",
    cat(route(A["galicia"], A["beja"], d0=12), route(A["beja"], A["gq"], d0=12), pxy("P5")),
    "Sebastian SB 25643-25644; Ibn Idhari SB 25570, 25576-25577.")
gq = RIV["Guadalquivir"]; gq_line = max(parts(gq), key=lambda q: q.length)
seg("S2a", "Guadalquivir mouth (P5) to Seville (P6)", "859", "dotted",
    cat(pxy("P5"), river_sub("Guadalquivir", (-6.19, 36.93), ll("P6")), pxy("P6")),
    "Ibn Idhari has them only at the mouth (SB 25577, 25580); Nowairi SB 25606-25607. D2.", land_legs=["whole segment is up-river (NE10m Guadalquivir; mouth-to-(-6.19,36.93) straight, NE line ends there)"])
seg("S3", "Guadalquivir mouth (P5) to Algeciras (P7)", "859", "solid", cat(pxy("P5"), route(A["gq"], A["alg"], d0=10), pxy("P7")),
    "Ibn Idhari SB 25580-25582; eswp-Sitio_de_Algeciras_859.")
seg("S4", "Algeciras (P7) through the Strait (P8) to Nekor (P9)", "859 (or 858, D1)", "solid",
    cat(pxy("P7"), route(A["alg"], A["strait"], d0=4, alpha=0.3), route(A["strait"], A["nekor"], d0=10), pxy("P9")),
    "SB 25582, 25633-25639, 25623, 25646, 25657; AB 3292-3293.", land_legs=["last ~18 km anchor->P9 straight (Nekor is inland)"])
seg("S5", "Nekor (P9) to Orihuela (P10)", "859", "solid",
    cat(pxy("P9"), route(A["nekor"], A["segura"], d0=12), river_sub("Segura", (-0.65, 38.10), ll("P10")), pxy("P10")),
    "Ibn Idhari SB 25583-25585; Nowairi SB 25609-25610.", land_legs=["first leg P9->sea straight", "last leg up the Segura (NE rivers_europe) to Orihuela"])
seg("S6", "Orihuela (P10) to Balearics (P13, P11, P12)", "859", "dotted",
    cat(route(A["segura"], A["form"], d0=15), route(A["form"], A["mall"], d0=10), route(A["mall"], A["men"], d0=10)),
    "Sebastian only, SB 25658-25659. Order unknown (D4); drawn Formentera -> Mallorca -> Menorca.")
seg("S7", "Balearics (or Orihuela) to Rhône mouth (P15) and Camargue (P14)", "859", "solid",
    cat(route(A["men"], A["rhone"], d0=20), pxy("P15"), pxy("P14")),
    "AB 859 (AB 3293-3295) 'Rodanum ingrediuntur ... in insula quae Camarias dicitur sedes ponunt'; Ibn Idhari SB 25585-25586.",
    land_legs=["P15 -> P14 straight into the Camargue island (winter camp)"],
    extra=dict(alt_start="If Atelier prefers to keep the solid chain unbroken, start S7 at the Segura anchor instead (Archivist: 'Balearics (or Orihuela)'). See S7_alt."))
seg("S7_alt", "ALT: Orihuela coast (P10) to Rhône mouth (P15), unused by default", "859", "solid",
    cat(route(A["segura"], A["rhone"], d0=14), pxy("P15"), pxy("P14")), "as S7", land_legs=["P15 -> P14 straight"],
    extra=dict(default_hidden=True))
arles = ll("P23")
seg("S8", "Camargue (P14) up the Rhône to Valence (P16) and back", "860", "solid",
    cat(pxy("P14"), rhone_sub(arles, ll("P16")), pxy("P16")),
    "AB 860 (AB 3441-3444) 'usque ad Valentiam civitatem vastando perveniunt ... ad insulam ... redeunt'.",
    land_legs=["whole segment is up-river: Camargue -> Arles straight, then NE10m Rhône centreline to Valence"],
    extra=dict(out_and_back=True, animate="trace up to Valence, then retract back down the same line to P14"))
seg("S9", "Camargue (P14) to Pisa (P17)", "860", "solid",
    cat(pxy("P14"), pxy("P15"), route(A["rhone"], A["magra"], d0=12), route(A["magra"], A["arno"], d0=8),
        river_sub("Arno", (10.28, 43.68), ll("P17")), pxy("P17")),
    "AB 860 (AB 3455-3456) 'Dani qui in Rodano fuerant Italiam petunt et Pisas civitatem aliasque capiunt'; Ibn al-Kutia SB 25628-25629.",
    land_legs=["P14 -> P15 back out of the Camargue", "Arno mouth -> Pisa up the Arno (NE rivers_europe)"],
    extra=dict(on_screen_end="P17 is the END of the solid line. On screen it is an UNLABELLED coastal mark (storyboard P05); 1.0 s hold here."))
seg("S10", "Coastal arc to Luna (P18, unlabelled)", "860 (as legend)", "broken",
    cat(np.array([P(*A["magra"])]), np.array([P(9.9891, 44.0455)]), pxy("P18")),
    "GND ch. IX (GND 953-954) 'fut jeté par une tempête auprès de Luna, ville d'Italie'. No annal names Luna for 860.",
    land_legs=["Magra mouth -> Luna site, ~2.5 km over the coastal plain"])
s11 = cat(pxy("P18"), np.array([P(9.9891, 44.0455)]), route(A["magra"], A["tiber"], d0=10))
rome = np.array(P(*ll("P19"))); dd = np.hypot(*(s11 - rome).T)
cut = np.argmax(dd < 45e3) if (dd < 45e3).any() else len(s11)
s11 = s11[:max(cut, 2)]
seg("S11", "Luna (P18) toward Rome (P19), never reached", "legend", "broken", s11,
    "GND 952-953 'se rendant par mer à Rome'; GND 964-965; ch. XI 'non esse Romam' (Latin transcription line 1196).",
    extra=dict(stop_short_km=round(float(np.hypot(*(s11[-1] - rome)) / 1000), 1), fade="alpha 1.0 -> 0.0 over the last 40% of length; never touches Rome",
               rome_mark="P19 drawn as a small PALE glyph, not connected"))
seg("S12", "Italy back west to the Strait, Sidona coast (P20)", "861", "dotted",
    cat(route(A["arno"], A["strait"], d0=45, alpha=0.6), route(A["strait"], A["sidona"], d0=8)),
    "Ibn Idhari SB 25589-25600; Nowairi SB 25612-25614. Path not recorded.")
seg("S13", "Strait (P8) north to the Loire / Brittany coast (P1)", "861-862", "dotted",
    cat(route(A["sidona"], A["galicia"], d0=50, alpha=0.6), route(A["galicia"], A["loire"], d0=55, alpha=0.6), pxy("P1")),
    "AB 862 'quibus et illi iunguntur qui in Hispania fuerant' (AB 3646-3647). Path not recorded.")
seg("S14", "Pamplona (P21), García's ransom", "859-861 (disputed)", "marker", pxy("P21"),
    "Nowairi SB 25617-25619; Christys via WP-VI line 49. D5. Marker only, NO connecting line.")

# verification
VER = {}
for s in SEG:
    if s["style"] == "marker": continue
    if s["land_legs"]: VER[s["id"]] = "river/land legs by design: " + "; ".join(s["land_legs"]); continue
    bad, pts = on_land_frac(s["xy"], 3.0); VER[s["id"]] = f"sea check: {bad} sample points on land (1 km sampling, ends ±3 km excluded)" + (f" {pts[:5]}" if bad else "")
for k in ("S9", "S11", "S12", "S13", "S7", "S5", "S4"):
    s = next(q for q in SEG if q["id"] == k)
    bad, pts = on_land_frac(s["xy"], 30.0); VER[k + "_sea_part"] = f"{bad} pts on land excluding 30 km at each end {pts[:4]}"
print(json.dumps(VER, indent=1, ensure_ascii=False))

# --------------------------------------------------------------------------------------------- frames
WIDE = fit916(-11.0, 15.5, 34.5, 48.0, margin=0.03)
CAM = {"iberia": fit916(-10.5, 5.5, 34.5, 48.0), "rhone_italy": fit916(3.5, 13.5, 40.5, 46.0),
       "luna_rome_inset": fit916(8.8, 13.2, 41.3, 44.6)}
DETAIL = dict(CAM["rhone_italy"])

# --------------------------------------------------------------------------------------------- painting
SEA_DEEP, SEA_SH, LAND_C, COAST = np.array([46, 96, 118]), np.array([112, 160, 160]), np.array([208, 182, 118]), (58, 44, 30)
RIVER_C = (64, 112, 132)
def paint_base(F):
    s = F.W / 1080.0; tf = lambda xy: F.px(xy)
    land = np.zeros((F.H, F.W), np.uint8); raster_geom(land, LAND, tf)
    lakes = np.zeros_like(land); raster_geom(lakes, LAKES, tf)
    sea = land == 0
    dist = cv2.distanceTransform(sea.astype(np.uint8), cv2.DIST_L2, 5) * F.mpp / 1000.0
    t = np.clip(dist / 180.0, 0, 1)[..., None] ** 0.7
    img = (SEA_SH * (1 - t) + SEA_DEEP * t)
    rng = np.random.default_rng(860)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (F.H, F.W)).astype(np.float32), (0, 0), 1.2 * s)[..., None]
    landc = LAND_C + grain * 5
    img = np.where(land[..., None] > 0, landc, img + grain * 3)
    img = np.where(lakes[..., None] > 0, SEA_SH, img)
    # interior land shading: slightly darker inland
    ld = cv2.distanceTransform((land > 0).astype(np.uint8), cv2.DIST_L2, 5) * F.mpp / 1000.0
    img = np.where(land[..., None] > 0, img * (1 - 0.06 * np.clip(ld / 300, 0, 1)[..., None]), img)
    return img, land, lakes

def apply_realms(F, img, land):
    s = F.W / 1080.0; ids = np.zeros((F.H, F.W), np.uint8)
    rgba = np.zeros((F.H, F.W, 4), np.float32)
    for rid, key, lab, g, col, src in REALMS:
        m = np.zeros((F.H, F.W), np.uint8); raster_geom(m, g, F.px)
        m = (m > 0) & (land > 0); ids[m] = rid
    out = img.copy()
    for rid, key, lab, g, col, src in REALMS:
        m = (ids == rid).astype(np.float32)
        if not m.any(): continue
        a = cv2.GaussianBlur(m, (0, 0), 2.0 * s) * m * 0.30
        edge = cv2.morphologyEx((ids == rid).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)
        edge = cv2.GaussianBlur(edge, (0, 0), 0.8 * s) * 0.22
        if key == "aghlabids":   # hatch Sicily (conquest in progress)
            sm = np.zeros((F.H, F.W), np.uint8); raster_geom(sm, SICILY, F.px); yy, xx = np.mgrid[0:F.H, 0:F.W]
            hatch = (((xx + yy) // max(1, int(4 * s))) % 2 == 0).astype(np.float32)
            a = np.where(sm > 0, a * (0.35 + 0.65 * hatch), a)
        aa = np.clip(a + edge, 0, 0.5)[..., None]
        out = out * (1 - aa) + np.array(col) * aa
        rgba[..., :3] = np.where(aa > 0, np.array(col, np.float32), rgba[..., :3]); rgba[..., 3] = np.maximum(rgba[..., 3], aa[..., 0])
    return out, ids, rgba

def draw_lines(F, img, land, lakes):
    s = F.W / 1080.0; im = np.ascontiguousarray(np.clip(img, 0, 255).astype(np.uint8)); sh = 4; f = 1 << sh
    # rivers
    for name, g in RIV.items():
        key = name in RIV_KEY + ["Arno", "Segura"]
        th = max(1, int(round((1.6 if key else 1.0) * s)))
        col = RIVER_C if key else (98, 132, 140)
        for L in parts(g):
            pts = np.round(F.px(Parr(np.asarray(L.coords))) * f).astype(np.int32)
            cv2.polylines(im, [pts], False, col, th, cv2.LINE_AA, sh)
    # coast ink
    edge = cv2.morphologyEx(((land > 0) & (lakes == 0)).astype(np.uint8) * 255, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    for p in parts(LAND):
        for r in [p.exterior] + list(p.interiors):
            pts = np.round(F.px(Parr(np.asarray(r.coords))) * f).astype(np.int32)
            cv2.polylines(im, [pts], True, COAST, max(1, int(round(1.3 * s))), cv2.LINE_AA, sh)
    return im

# --------------------------------------------------------------------------------------------- routes / labels
INK, PALE = (52, 38, 26), (128, 108, 88)
def resample(xy, step):
    L = LineString(xy); n = max(2, int(L.length / step)); return np.array([L.interpolate(L.length * k / n).coords[0] for k in range(n + 1)])

def draw_routes(F, im):
    s = F.W / 1080.0; base = Image.fromarray(im).convert("RGBA"); lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    order = ["S13", "S12", "S1", "S2a", "S6", "S2", "S3", "S4", "S5", "S7", "S8", "S9", "S10", "S11"]
    for sid in order:
        sg = next(q for q in SEG if q["id"] == sid); xy = F.px(sg["xy"])
        if sg["style"] == "solid":
            d.line([tuple(p) for p in xy], fill=INK + (255,), width=max(2, int(3.2 * s)), joint="curve")
        elif sg["style"] == "dotted":
            pts = resample(xy, 8.5 * s); r = 1.7 * s
            for x, y in pts: d.ellipse([x - r, y - r, x + r, y + r], fill=INK + (235,))
        elif sg["style"] == "broken":
            pts = resample(xy, 1.0); n = len(pts); dash, gap = 14 * s, 8 * s; L = 0.0; on = True; seglen = 0
            for k in range(n - 1):
                fr = k / (n - 1); al = 1.0 if (sid != "S11" or fr < 0.6) else max(0.0, 1 - (fr - 0.6) / 0.4)
                if on: d.line([tuple(pts[k]), tuple(pts[k + 1])], fill=PALE + (int(230 * al),), width=max(2, int(2.6 * s)))
                seglen += 1
                if seglen >= (dash if on else gap): on = not on; seglen = 0
    return Image.alpha_composite(base, lay)

def font(sz, bold=False, italic=False, serif=True):
    fam = "DejaVuSerif" if serif else "DejaVuSans"
    suf = "-BoldItalic" if bold and italic else "-Bold" if bold else "-Italic" if italic else ""
    if serif and italic and not bold: suf = "-Italic"
    try: return ImageFont.truetype(f"{FONT}{fam}{suf}.ttf", int(sz))
    except OSError: return ImageFont.truetype(f"{FONT}{fam}.ttf", int(sz))

def annotate(F, img, kind):
    s = F.W / 1080.0; d = ImageDraw.Draw(img); boxes = []
    def free(b): return all(b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3] for o in boxes) and b[0] > 4 and b[1] > 4 and b[2] < F.W - 4 and b[3] < F.H - 4
    def place(x, y, text, f, fill, r=6 * s, prefer=None):
        tw, th = d.textbbox((0, 0), text, font=f)[2:]
        cands = [(r + 2, -th / 2), (-tw - r - 2, -th / 2), (-tw / 2, -th - r), (-tw / 2, r), (r, -th - r * 0.6), (r, r * 0.6), (-tw - r, -th - r * 0.6), (-tw - r, r * 0.6)]
        if prefer is not None: cands = [cands[prefer]] + cands
        for dx, dy in cands:
            b = (x + dx - 2, y + dy - 2, x + dx + tw + 2, y + dy + th + 2)
            if free(b):
                d.text((x + dx + 1, y + dy + 1), text, font=f, fill=(250, 240, 220, 200)); d.text((x + dx, y + dy), text, font=f, fill=fill)
                boxes.append(b); return True
        return False
    # realm labels
    for rid, key, lab, g, col, src in REALMS:
        frame_ll = Polygon([tuple(v) for v in F.bounds_ll().values()])
        gi = g.intersection(frame_ll.buffer(-0.3))
        if gi.is_empty or gi.area < 0.25: continue
        big = max(parts(gi), key=lambda q: q.area); rp = big.representative_point()
        x, y = F.pll(rp.x, rp.y); t = f"{lab.upper()} (approx.)"
        f = font(11 * s, italic=True); tw, th = d.textbbox((0, 0), t, font=f)[2:]
        b = (x - tw / 2, y - th / 2, x + tw / 2, y + th / 2)
        if free(b): d.text((b[0], b[1]), t, font=f, fill=tuple(int(c * 0.55) for c in col) + (255,)); boxes.append(b)
    for lab, lo, la in LOOSE_LABELS:
        x, y = F.pll(lo, la); t = f"{lab.upper()} (loose, no border)"; f = font(11 * s, italic=True); tw, th = d.textbbox((0, 0), t, font=f)[2:]
        if 0 < x < F.W and 0 < y < F.H: d.text((x - tw / 2, y - th / 2), t, font=f, fill=(70, 60, 40, 255)); boxes.append((x - tw / 2, y - th / 2, x + tw / 2, y + th / 2))
    # pins
    for k, (lab, la, lo, wd, show, pin) in PTS.items():
        x, y = F.pll(lo, la)
        if not (0 <= x < F.W and 0 <= y < F.H): continue
        r = 4.2 * s
        if k == "P18":
            d.ellipse([x - r, y - r, x + r, y + r], outline=(90, 90, 90, 255), width=max(1, int(1.6 * s))); boxes.append((x - r, y - r, x + r, y + r)); continue
        if k == "P19":
            d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 226, 206, 255), outline=PALE + (255,), width=max(1, int(1.2 * s)))
        elif k == "P21":
            d.ellipse([x - r, y - r, x + r, y + r], fill=None, outline=INK + (255,), width=max(1, int(1.6 * s)))
            for a in range(0, 360, 45):
                xa, ya = x + 1.9 * r * math.cos(math.radians(a)), y + 1.9 * r * math.sin(math.radians(a)); d.ellipse([xa - s, ya - s, xa + s, ya + s], fill=INK + (255,))
        elif pin:
            d.ellipse([x - r, y - r, x + r, y + r], fill=INK + (255,), outline=(250, 240, 220, 255), width=max(1, int(1.2 * s)))
        boxes.append((x - r, y - r, x + r, y + r))
    x, y = F.pll(EXTRA["E_SIDONA"][2], EXTRA["E_SIDONA"][1]); r = 5 * s
    d.line([x - r, y - r, x + r, y + r], fill=INK + (255,), width=max(1, int(2 * s))); d.line([x - r, y + r, x + r, y - r], fill=INK + (255,), width=max(1, int(2 * s)))
    for k, (lab, la, lo, wd, show, pin) in PTS.items():
        if not show: continue
        x, y = F.pll(lo, la)
        if not (0 <= x < F.W and 0 <= y < F.H): continue
        opt = k in ("P6", "P8", "P21")
        place(x, y, lab, font((13 if not opt else 11.5) * s, bold=not opt, italic=opt), (40, 30, 20, 255))
    # segment ids (desk only)
    for sg in SEG:
        if sg["style"] == "marker" or sg.get("default_hidden"): continue
        xy = F.px(sg["xy"]); L = LineString(xy); m = L.interpolate(0.5, normalized=True)
        if 0 < m.x < F.W and 0 < m.y < F.H and L.length > 40 * s: place(m.x, m.y, sg["id"], font(9.5 * s, serif=False), (120, 30, 30, 255), r=3 * s)
    return img

def legend(F, img, title, lines_extra):
    s = F.W / 1080.0; d = ImageDraw.Draw(img); x0, y0 = 22 * s, F.H - 330 * s; w = F.W - 44 * s
    d.rounded_rectangle([x0, y0, x0 + w, F.H - 20 * s], radius=10 * s, fill=(246, 238, 220, 236), outline=COAST + (255,), width=max(1, int(1.5 * s)))
    f1, f2, f3 = font(17 * s, bold=True), font(12.5 * s, serif=False), font(10.5 * s, serif=False)
    d.text((x0 + 16 * s, y0 + 12 * s), title, font=f1, fill=(40, 30, 20, 255))
    y = y0 + 44 * s; X = x0 + 18 * s
    def key(kind, text):
        nonlocal y
        if kind == "solid": d.line([X, y + 8 * s, X + 50 * s, y + 8 * s], fill=INK + (255,), width=max(2, int(3.2 * s)))
        elif kind == "dotted":
            for k in range(7): xx = X + k * 8.5 * s; d.ellipse([xx - 1.7 * s, y + 8 * s - 1.7 * s, xx + 1.7 * s, y + 8 * s + 1.7 * s], fill=INK + (255,))
        elif kind == "broken":
            for k in range(3): d.line([X + k * 22 * s, y + 8 * s, X + k * 22 * s + 14 * s, y + 8 * s], fill=PALE + (255,), width=max(2, int(2.6 * s)))
        elif kind == "pin": d.ellipse([X + 21 * s, y + 4 * s, X + 29 * s, y + 12 * s], fill=INK + (255,))
        elif kind == "luna": d.ellipse([X + 21 * s, y + 4 * s, X + 29 * s, y + 12 * s], outline=(90, 90, 90, 255), width=max(1, int(1.6 * s)))
        elif kind == "rome": d.ellipse([X + 21 * s, y + 4 * s, X + 29 * s, y + 12 * s], fill=(236, 226, 206, 255), outline=PALE + (255,))
        elif kind == "x": d.line([X + 20 * s, y + 3 * s, X + 30 * s, y + 13 * s], fill=INK + (255,), width=2); d.line([X + 20 * s, y + 13 * s, X + 30 * s, y + 3 * s], fill=INK + (255,), width=2)
        elif kind == "ring": d.ellipse([X + 21 * s, y + 4 * s, X + 29 * s, y + 12 * s], outline=INK + (255,), width=2)
        d.text((X + 62 * s, y), text, font=f2, fill=(40, 30, 20, 255)); y += 21 * s
    key("solid", "DOCUMENTED route (859-860): Galicia > Guadalquivir > Algeciras > Strait > Nekor > Orihuela; Rhône/Camargue; Valence; Pisa")
    key("dotted", "UNCERTAIN: Loire departure, Seville, Balearics, 861 return (Italy > Strait/Sidona > Loire)")
    key("broken", "LEGEND (Dudo / William): Luna > toward Rome, fades out, never reaches Rome")
    key("pin", "Place pin (Wikidata P625)"); key("luna", "Luna site 44.0640, 10.0170 — UNLABELLED pin")
    key("rome", "Rome — pale mark, never connected"); key("ring", "Pamplona / García ransom — marker only, no line (D5)")
    key("x", "Sidona coast battle 861 — offshore event mark (desk placement)")
    y += 4 * s
    for t in lines_extra: d.text((X, y), t, font=f3, fill=(60, 48, 34, 255)); y += 15 * s
    return img

# --------------------------------------------------------------------------------------------- main
def r1(a): return [[round(float(x), 1), round(float(y), 1)] for x, y in a]
def simplify_px(xy, tol=0.35): return np.asarray(LineString(xy).simplify(tol).coords)

def render(tag, rect, W, H, outputs, frames_json):
    F = Frame(tag, rect, W, H); print("render", tag, W, H, "km/px", round(F.mpp / 1000, 3))
    img, land, lakes = paint_base(F)
    img, ids, rgba = apply_realms(F, img, land)
    base = draw_lines(F, img, land, lakes)
    sfx = "" if W == 1080 else f"_{W}x{H}"
    stem = "p05_reference" if tag == "wide" else "p05_detail_rhone_italy"
    clean = Image.fromarray(base)
    outputs[f"{stem}_clean{sfx}.png"] = clean
    routed = draw_routes(F, base)
    ann = annotate(F, routed, tag)
    extra = ["REALM ZONES APPROXIMATE c.860. OHM (CC0) relations where they exist; Provence, Kingdom of Italy, East Francia hand-traced after",
             "Shepherd, Historical Atlas pl.56 (1911/1923, PD). Nekor & Idrisids: loose labels only. Balearics left unshaded (OHM artefacts removed).",
             f"Projection: {PROJ.proj4()}  |  {F.mpp/1000:.3f} km/px  |  basemap Natural Earth 10m (PD)",
             "Desk reference only. On-screen plate: place names only, no routes / dates / captions. Data: p05_routes.json, map-reference-data.md."]
    if tag == "wide":
        d = ImageDraw.Draw(ann)
        for name, r in CAM.items():
            x, y, w, h = F.rect_px(r); d.rectangle([x, y, x + w, y + h], outline=(150, 20, 20, 255), width=max(1, int(1.6 * W / 1080)))
            d.text((x + 6 * W / 1080, y + 4 * W / 1080), f"CAM {name}", font=font(11 * W / 1080, serif=False), fill=(150, 20, 20, 255))
    else:
        d = ImageDraw.Draw(ann); x, y, w, h = F.rect_px(CAM["luna_rome_inset"])
        d.rectangle([x, y, x + w, y + h], outline=(150, 20, 20, 255), width=max(1, int(1.6 * W / 1080)))
        d.text((x + 6 * W / 1080, y + 4 * W / 1080), "CAM luna_rome_inset", font=font(11 * W / 1080, serif=False), fill=(150, 20, 20, 255))
    ann = legend(F, ann, "P05 REFERENCE — annotated (" + ("wide plate" if tag == "wide" else "detail: Rhône–Italy frame") + ")", extra)
    outputs[f"{stem}_annotated{sfx}.png"] = ann.convert("RGB")
    lay = Image.fromarray(np.clip(rgba * np.array([1, 1, 1, 255]), 0, 255).astype(np.uint8), "RGBA")
    outputs[f"{stem}_realms_layer{sfx}.png"] = lay
    outputs[f"{stem}_realm_ids{sfx}.png"] = Image.fromarray(ids, "L")
    # json part
    fj = frames_json.setdefault(tag, {"plate_stem": stem, "sizes": {}})
    fj["proj_rect_m"] = {"xmin": F.x0, "ymax": F.y1, "width": rect["w"], "height": rect["h"]}
    sz = fj["sizes"][f"{W}x{H}"] = {"m_per_px": round(F.mpp, 3), "corners_lonlat": F.bounds_ll(), "points_px": {}, "segments_px": {}, "cameras_px_xywh": {}}
    for k, (lab, la, lo, wd, show, pin) in PTS.items(): sz["points_px"][k] = r1([F.pll(lo, la)])[0]
    for k, v in EXTRA.items(): sz["points_px"][k] = r1([F.pll(v[2], v[1])])[0]
    for sg in SEG: sz["segments_px"][sg["id"]] = r1(simplify_px(F.px(sg["xy"])) if len(sg["xy"]) > 1 else F.px(sg["xy"]))
    for name, r in CAM.items():
        x, y, w, h = F.rect_px(r); sz["cameras_px_xywh"][name] = {"xywh": [x, y, w, h], "zoom_vs_full_frame": round(W / w, 3),
                                                                  "source_px_per_1080_output_px": round(w / 1080, 3), "upscale_needed": w < 1080}
    return F

def main():
    os.makedirs(OUT, exist_ok=True)
    outputs, frames = {}, {}
    names = [f"{st}_{k}{sfx}.png" for st in ("p05_reference", "p05_detail_rhone_italy") for k in ("clean", "annotated", "realms_layer", "realm_ids") for sfx in ("", "_2160x3840")] + ["p05_routes.json"]
    clash = [n for n in names if os.path.exists(os.path.join(OUT, n))]
    if clash: sys.exit(f"REFUSING to overwrite existing outputs in {OUT}: {clash}")
    for tag, rect in (("wide", WIDE), ("detail", DETAIL)):
        for W, H in SIZES: render(tag, rect, W, H, outputs, frames)
    for n, im in outputs.items(): im.save(os.path.join(OUT, n), optimize=True); print("wrote", n)
    J = {
      "schema": "posterity.p05_routes.v1", "generated": "2026-11-03", "source_of_truth": "standalones/bjorn/map-reference-data.md (Archivist 2026-11-03)",
      "projection": {"name": "Lambert Conformal Conic (spherical, 2SP)", "proj4": PROJ.proj4(), "lat_1": PROJ.lat1, "lat_2": PROJ.lat2, "lat_0": PROJ.lat0, "lon_0": PROJ.lon0, "R_m": 6371000,
                     "px_from_proj": "px = (x - xmin)/m_per_px ; py = (ymax - y)/m_per_px  (per frame, per size)"},
      "plate_box_lonlat": {"W": -11.0, "E": 15.5, "S": 34.5, "N": 48.0},
      "frames": frames,
      "camera_boxes_lonlat": {k: v["box"] for k, v in CAM.items()},
      "points": {k: {"label_on_screen": (v[0] if v[4] else None), "lat": v[1], "lon": v[2], "wikidata": v[3], "pinned": v[5], "note": PT_NOTE.get(k, "")} for k, v in PTS.items()},
      "derived_marks": {k: {"lat": v[1], "lon": v[2], "wikidata": v[3], "note": v[4]} for k, v in EXTRA.items()},
      "sea_anchors_lonlat": {k: list(v) for k, v in ANCH.items()},
      "segments": [{k: (v if k != "xy" else None) for k, v in sg.items() if k != "xy"} | {"lonlat": [[round(float(a), 4), round(float(b), 4)] for a, b in Iarr(np.asarray(LineString(sg["xy"]).simplify(500).coords) if len(sg["xy"]) > 1 else sg["xy"])]} for sg in SEG],
      "draw_order_on_screen": ["S2", "S3", "S4", "S5", "S7", "S8", "S9", "(1.0 s hold at P17 empty end)", "S11 (broken, fading; Rome pale mark)"],
      "styles": {"solid": "DOCUMENTED", "dotted": "UNCERTAIN", "broken": "LEGEND (long dash)", "marker": "marker only, no line"},
      "realms": [{"id": i, "key": k, "label": l, "rgb": list(c), "source": s, "approximate": True} for i, k, l, g, c, s in REALMS] + [{"key": "nekor", "label": "Nekor", "fill": None, "label_lonlat": [-3.95, 34.78]}, {"key": "idrisids", "label": "Idrisids", "fill": None, "label_lonlat": [-5.6, 34.15]}],
      "verification": VER,
      "not_plotted": ["Narbonne (Q6555)", "Roussillon", "Nîmes (D6)", "Arles (D6, routing vertex only)", "Beja harbour (unidentified)", "Greece / Alexandria (excluded by Archivist)"],
    }
    json.dump(J, open(os.path.join(OUT, "p05_routes.json"), "w"), indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else (o.tolist() if hasattr(o, "tolist") else str(o))); print("wrote p05_routes.json")

if __name__ == "__main__": main()
