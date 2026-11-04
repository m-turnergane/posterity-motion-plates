#!/usr/bin/env python3
"""map_route_v1 -- self-drawing ink-nib routes on a painted basemap built from real geodata (Posterity engine R&D).

    python map_route_v1.py configs/<map>.json [...]          # one shot per config -> proofs/, poc/, stills
    python map_route_v1.py --reel out.mp4 configs/a.json configs/b.json ...   # hard-cut reel (refuses to overwrite)

Pipeline (one shot):
  1. Basemap  : Natural Earth 10m land / lakes / rivers (public domain) -> explicit Lambert azimuthal equal-area
                projection (spherical, R=6371 km) -> rasterised at the PLATE size (>= output, never upscaled) ->
                painted in the house map palette (teal wash sea, ochre parchment land, ink coastline, paper grain).
                No text, no borders, no labels.  The basemap is STATIC: nothing about land, water or coast moves.
  2. Placement: each stop's lon/lat (from a cited gazetteer, see sources/) is projected, then mapped to pixels by an
                affine fitted by least squares to CONTROL POINTS (headlands with gazetteer coords, located on the
                rendered coastline).  RMS / max error at the control points goes into the proof JSON.
  3. Route    : the LOCKED house-map-inknib-dashed-v1 nib (motion/presets/locked/engine, MapLight, imported
                read-only, never edited) draws the line and the ink stamps.  Stops flagged `claimed` get the
                dashed + fainter nib and open-ring stamps; `documented` get a solid nib and filled stamps.
                Stops that are regions or unverified identifications are never plotted (no guessed points).
  4. Camera   : ONE transform: plate-space frame -> output by a single affine (push z0->z1, smoothstep).
                guardrails.check_pixel_density must pass (refuse mode).
  5. Proofs   : density, protected pixels (land / water / coast outside the ink swath: 0 changed px in plate
                space), control-point error, phone stats at 640x360 (first-second visibility, >5 Hz energy).
"""
import argparse, hashlib, importlib.util, json, math, os, struct, subprocess, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/workspace/posterity"
NE = os.path.join(HERE, "sources", "naturalearth")
GAZ = os.path.join(HERE, "sources", "waypoint_coords_wikidata_2026-10-30.json")
R_EARTH = 6371.0

def _load(name, path):                                  # read-only import of locked code by path
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
ENG = _load("animate_b3_locked", f"{ROOT}/motion/presets/locked/engine/animate_b3_cb9e2b88.py")
sys.path.insert(0, f"{ROOT}/motion"); import guardrails  # noqa: E402
LOCKED_PRESET = json.load(open(f"{ROOT}/motion/presets/locked/house-map-inknib-dashed-v1.json"))
NIB = next(L for L in LOCKED_PRESET["layers"] if L["preset"] == "map-light")["params"]

# ------------------------------------------------------------------------------------------ shapefile (minimal)
def read_dbf(path):
    with open(path, "rb") as f: b = f.read()
    n, hl, rl = struct.unpack("<IHH", b[4:12]); fields = []; o = 32
    while b[o] != 0x0D:
        fields.append((b[o:o + 11].split(b"\0")[0].decode(), b[o + 16])); o += 32
    rows = []
    for i in range(n):
        r = b[hl + i * rl + 1: hl + (i + 1) * rl]; d = {}; p = 0
        for name, ln in fields: d[name] = r[p:p + ln].decode("latin-1").strip(); p += ln
        rows.append(d)
    return rows

def read_shp(path, bbox=None):
    """Yield (record_index, [ring_or_line ndarray Nx2 lon/lat]) for polygon (5) / polyline (3) shapefiles."""
    with open(path, "rb") as f: b = f.read()
    o, i = 100, 0
    while o < len(b):
        _, clen = struct.unpack(">ii", b[o:o + 8]); rec = b[o + 8:o + 8 + clen * 2]; o += 8 + clen * 2
        st = struct.unpack("<i", rec[:4])[0]
        if st in (3, 5):
            x0, y0, x1, y1 = struct.unpack("<4d", rec[4:36])
            if bbox is None or not (x1 < bbox[0] or x0 > bbox[2] or y1 < bbox[1] or y0 > bbox[3]):
                np_, npt = struct.unpack("<ii", rec[36:44])
                parts = list(struct.unpack(f"<{np_}i", rec[44:44 + 4 * np_])) + [npt]
                pts = np.frombuffer(rec[44 + 4 * np_: 44 + 4 * np_ + 16 * npt], "<f8").reshape(-1, 2)
                yield i, [pts[parts[k]:parts[k + 1]] for k in range(np_)]
        i += 1

# ------------------------------------------------------------------------------------------ projection
class LAEA:
    """Lambert azimuthal equal-area, spherical, centred on (lon0, lat0). Returns km east / north."""
    def __init__(s, lon0, lat0): s.l0, s.p0 = math.radians(lon0), math.radians(lat0)
    def __call__(s, lon, lat):
        l, p = np.radians(lon) - s.l0, np.radians(lat)
        k = np.sqrt(2.0 / (1 + math.sin(s.p0) * np.sin(p) + math.cos(s.p0) * np.cos(p) * np.cos(l)))
        return (R_EARTH * k * np.cos(p) * np.sin(l),
                R_EARTH * k * (math.cos(s.p0) * np.sin(p) - math.sin(s.p0) * np.cos(p) * np.cos(l)))

class MapGeom:
    """projection + analytic km->plate px (north up). `fit` (2x3 affine on analytic px) is set by control points."""
    def __init__(s, cfg, W, H):
        m = cfg["map"]; s.proj = LAEA(*m["center_lonlat"]); s.W, s.H = W, H
        cx, cy = s.proj(*m["center_lonlat"]); s.kmw = float(m["width_km"]); s.sc = W / s.kmw   # px per km
        s.x0, s.y1 = cx - s.kmw / 2, cy + (H / s.sc) / 2; s.fit = np.float64([[1, 0, 0], [0, 1, 0]])
        corners = [(s.x0, s.y1 - H / s.sc), (s.x0 + s.kmw, s.y1)]
        s.km_per_px = 1 / s.sc
    def analytic(s, lon, lat):
        x, y = s.proj(np.asarray(lon, float), np.asarray(lat, float))
        return np.stack([(x - s.x0) * s.sc, (s.y1 - y) * s.sc], -1)
    def px(s, lon, lat):
        a = s.analytic(lon, lat); return a @ s.fit[:, :2].T + s.fit[:, 2]
    def lonlat_bbox(s, pad_deg=3.0):
        # coarse geographic window for reading shapefiles: invert by sampling the plate border
        lo, la = np.meshgrid(np.linspace(-40, 50, 361), np.linspace(25, 72, 189))
        p = s.analytic(lo, la); ok = (p[..., 0] > -50) & (p[..., 0] < s.W + 50) & (p[..., 1] > -50) & (p[..., 1] < s.H + 50)
        return (lo[ok].min() - pad_deg, la[ok].min() - pad_deg, lo[ok].max() + pad_deg, la[ok].max() + pad_deg)

# ------------------------------------------------------------------------------------------ basemap
def _ring_area(r): return 0.5 * float(np.sum(r[:-1, 0] * r[1:, 1] - r[1:, 0] * r[:-1, 1]))

def raster_polys(geom, shp, bbox, ss=4, filt=None):
    W, H = geom.W * ss, geom.H * ss; m = np.zeros((H, W), np.uint8); outer, holes = [], []
    rows = read_dbf(shp[:-4] + ".dbf") if filt else None
    for i, rings in read_shp(shp, bbox):
        if filt and not filt(rows[i]): continue
        for r in rings:
            p = np.int32(np.round(geom.px(r[:, 0], r[:, 1]) * ss * 16))
            (holes if _ring_area(r) > 0 else outer).append(p)     # shapefile: outer rings clockwise (negative area)
    if outer: cv2.fillPoly(m, outer, 255, cv2.LINE_8, shift=4)
    if holes: cv2.fillPoly(m, holes, 0, cv2.LINE_8, shift=4)
    return cv2.resize(m, (geom.W, geom.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

def raster_lines(geom, shp, bbox, filt, width_fn, ss=4):
    W, H = geom.W * ss, geom.H * ss; m = np.zeros((H, W), np.uint8); rows = read_dbf(shp[:-4] + ".dbf")
    for i, lines in read_shp(shp, bbox):
        if not filt(rows[i]): continue
        th = max(1, int(round(width_fn(rows[i]) * ss)))
        for l in lines:
            cv2.polylines(m, [np.int32(np.round(geom.px(l[:, 0], l[:, 1]) * ss * 16))], False, 255, th, cv2.LINE_AA, shift=4)
    return cv2.resize(m, (geom.W, geom.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

def _rank(row):
    try: return int(float(row.get("scalerank", "99") or 99))
    except ValueError: return 99

def build_basemap(geom, cfg, seed):
    """Painted static basemap at plate size. Returns RGB uint8 + dict of masks (land, water, coast) as bool."""
    b = cfg.get("basemap", {}); W, H = geom.W, geom.H; bbox = geom.lonlat_bbox(); rng = np.random.default_rng(seed)
    land = raster_polys(geom, f"{NE}/ne_10m_land/ne_10m_land.shp", bbox)
    lakes = raster_polys(geom, f"{NE}/ne_10m_lakes/ne_10m_lakes.shp", bbox, filt=lambda r: _rank(r) <= b.get("lake_rank", 6))
    land = np.clip(land - lakes, 0, 1)
    rivers = raster_lines(geom, f"{NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp", bbox,
                          lambda r: _rank(r) <= b.get("river_rank", 5) and r.get("featurecla", "").startswith("River"),
                          lambda r: b.get("river_px", 1.6) * (1.25 if _rank(r) <= 3 else 0.85)) * land
    pn = ENG.pnoise
    # --- distances from the shore (px) for coastal washes
    lb = (land > 0.5).astype(np.uint8)
    d_sea = cv2.distanceTransform(1 - lb, cv2.DIST_L2, 5); d_land = cv2.distanceTransform(lb, cv2.DIST_L2, 5)
    # --- sea: teal watercolour wash, lighter shallows at the shore, darker and cooler offshore, slow pigment mottling
    deep, shallow = np.float32(b.get("sea_deep", [46, 96, 118])), np.float32(b.get("sea_shallow", [112, 160, 160]))
    sh = np.exp(-d_sea / b.get("shallow_px", 38.0))[..., None]
    mott = pn(rng, H, W, 420, 18, 2.6)[..., None]; fine = pn(rng, H, W, 60, 2, 2.0)[..., None]
    sea = deep * (1 - sh) + shallow * sh; sea = sea * (1 + 0.07 * mott + 0.025 * fine)
    # --- land: ochre parchment, sandy rim at the shore, olive mottling inland
    ochre, rim, olive = np.float32(b.get("land", [208, 182, 118])), np.float32(b.get("land_rim", [228, 210, 160])), np.float32(b.get("land_inland", [168, 160, 96]))
    rimw = np.exp(-d_land / b.get("rim_px", 5.0))[..., None]
    inl = np.clip(ENG.smoothstep(0.1, 1.4, pn(rng, H, W, 300, 30, 2.8)), 0, 1)[..., None] * (1 - np.exp(-d_land / 60.0))[..., None]
    lnd = ochre * (1 - inl * 0.55) + olive * inl * 0.55
    lnd = lnd * (1 + 0.06 * pn(rng, H, W, 140, 6, 2.4)[..., None] + 0.03 * fine)
    lnd = lnd * (1 - rimw) + rim * rimw
    lnd = lnd * (1 - 0.10 * np.exp(-d_land / 16.0)[..., None] * (1 - rimw))   # watercolour pooling just inside the rim
    a = land[..., None]; img = sea * (1 - a) + lnd * a
    # --- rivers: thin faded blue-grey pen
    img = img * (1 - 0.55 * rivers[..., None]) + np.float32([92, 120, 128]) * 0.55 * rivers[..., None]
    # --- coastline ink: AA edge of the land alpha, width-varied
    edge = np.clip(cv2.GaussianBlur(land, (0, 0), 0.8) * 4 * (1 - cv2.GaussianBlur(land, (0, 0), 0.8)), 0, 1)
    ew = cv2.dilate(edge, np.ones((2, 2), np.uint8)) * np.clip(0.8 + 0.25 * pn(rng, H, W, 80, 4), 0.4, 1.0)
    ink = np.float32(b.get("coast_ink", [58, 44, 30]))
    img = img * (1 - 0.85 * ew[..., None]) + ink * 0.85 * ew[..., None]
    # --- paper grain over everything (static, plate-native size)
    grain = pn(rng, H, W, 6, 0.8, 1.5)[..., None]; img *= 1 + b.get("grain", 0.035) * grain
    rgb = np.clip(img, 0, 255).astype(np.uint8)
    coast = dilate_b(ew > 0.08, 1)
    masks = dict(land=(land > 0.5) & ~coast, water=(land <= 0.5) & ~coast, coast=coast)
    return rgb, masks

def dilate_b(b, px): return cv2.dilate(b.astype(np.uint8), np.ones((2 * px + 1,) * 2, np.uint8)) > 0

# ------------------------------------------------------------------------------------------ control points
def fit_control_points(geom, land, cps, gaz):
    """Locate each control point on the rendered coastline (extreme land pixel in direction `dir` within a search
    window around its projected position), then least-squares fit an affine analytic px -> measured px."""
    D = dict(W=(-1, 0), E=(1, 0), N=(0, -1), S=(0, 1), NW=(-1, -1), NE=(1, -1), SW=(-1, 1), SE=(1, 1))
    lb = land > 0.5; out = []
    for cp in cps:
        g = gaz[cp["ref"]]; a = geom.analytic(g["lon"], g["lat"]); r = int(cp.get("search_px", 30))
        x0, y0 = int(a[0]) - r, int(a[1]) - r
        if x0 < 0 or y0 < 0 or x0 + 2 * r >= geom.W or y0 + 2 * r >= geom.H: continue
        win = lb[y0:y0 + 2 * r + 1, x0:x0 + 2 * r + 1]; yy, xx = np.nonzero(win)
        if len(xx) == 0: continue
        dx, dy = D[cp["dir"]]; score = (xx * dx + yy * dy) / math.hypot(dx, dy)
        sel = score >= score.max() - 0.5; mx, my = xx[sel].mean() + x0, yy[sel].mean() + y0
        out.append(dict(name=cp["ref"], qid=g["qid"], lonlat=[g["lon"], g["lat"]], dir=cp["dir"],
                        analytic_px=[round(float(a[0]), 2), round(float(a[1]), 2)], measured_px=[round(float(mx), 2), round(float(my), 2)]))
    if len(out) < 3: raise RuntimeError(f"need >=3 control points on the map, found {len(out)}")
    A = np.float64([[*o["analytic_px"], 1] for o in out]); B = np.float64([o["measured_px"] for o in out])
    M, *_ = np.linalg.lstsq(A, B, rcond=None); geom.fit = M.T
    pre = np.linalg.norm(A[:, :2] - B, axis=1); post = np.linalg.norm(A @ M - B, axis=1)
    for o, e0, e1 in zip(out, pre, post): o["err_px_unfitted"], o["err_px_fitted"] = round(float(e0), 2), round(float(e1), 2)
    kmpp = geom.km_per_px
    return dict(method="extreme coastline pixel in `dir` within search window; LSQ affine (6 dof) analytic->measured",
                n=len(out), rms_px=round(float(np.sqrt((post ** 2).mean())), 2), max_px=round(float(post.max()), 2),
                rms_km=round(float(np.sqrt((post ** 2).mean()) * kmpp), 2), max_km=round(float(post.max() * kmpp), 2),
                rms_px_unfitted=round(float(np.sqrt((pre ** 2).mean())), 2), km_per_plate_px=round(kmpp, 4),
                affine=np.round(geom.fit, 6).tolist(), points=out)


# ------------------------------------------------------------------------------------------ authority: MAP-PLACES-v1
EDW = f"{ROOT}/longform/edward-ii-feature"
PLACES_MD = f"{EDW}/MAP-PLACES-v1.md"
WD_RAW = f"{EDW}/raw/wikidata"

def wikidata_p625(qid):
    """Coordinates come ONLY from the Archivist's saved Wikidata entity JSON (P625), as MAP-PLACES-v1 requires."""
    d = json.load(open(f"{WD_RAW}/{qid}.json")); e = d["entities"][qid]
    v = e["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]
    return dict(qid=qid, lon=float(v["longitude"]), lat=float(v["latitude"]), label=e.get("labels", {}).get("en", {}).get("value"))

def read_places_md():
    """Parse the MAP 1 / MAP 2 tables: row id -> {qid, status, onscreen}."""
    import re
    rows = {}
    for line in open(PLACES_MD, encoding="utf-8"):
        if not re.match(r"^\| [12]-\d\d ", line): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        qid = next((c for c in cells if re.fullmatch(r"Q\d+", c)), None)
        status = next((c for c in cells if re.match(r"^(VERIFIED|OMIT|UNCERTAIN)", c)), "")
        onscreen = next((c for c in cells if re.match(r"^(yes:|label only:|tint or label only|no$|n/a$)", c)), "")
        rows[cells[0]] = dict(qid=qid, status=status, onscreen=onscreen, site=cells[4] if cells[0][0] == "1" else cells[3])
    return rows

def check_against_authority(cfg, rows):
    """Refuse to render anything MAP-PLACES-v1 does not allow: pins must be VERIFIED rows, vias must be OMIT (region)
    rows, Q-IDs must match, label text must be the row's allowed on-screen text, rows in a chain must keep the list order."""
    log = []
    def chk(st, kind):
        r = rows.get(st["row"]); assert r, f"row {st['row']} not in MAP-PLACES-v1"
        assert r["qid"] == st["qid"], f"{st['row']}: config {st['qid']} != list {r['qid']}"
        if kind == "pin": assert r["status"].startswith("VERIFIED"), f"{st['row']} is {r['status']}, cannot pin"
        if kind == "via": assert r["status"].startswith("OMIT"), f"{st['row']} via must be a region (OMIT) row"
        lab = st.get("label")
        if lab: assert lab in r["onscreen"] and not r["onscreen"].startswith("no"), f"{st['row']}: label {lab!r} not allowed ({r['onscreen']})"
        log.append(dict(row=st["row"], qid=st["qid"], kind=kind, status=r["status"].split(" ")[0], label=lab, site=r["site"]))
    for ch in cfg.get("chains", []):
        ids = [st["row"] for st in ch["stops"]]
        assert ids == sorted(ids), f"chain order {ids} differs from MAP-PLACES-v1 row order"
        for st in ch["stops"]: chk(st, "pin" if st.get("pin", True) else "via")
    for g in cfg.get("pins", []):
        for st in g["items"]: chk(st, "pin")
    for tn in cfg.get("tints", []): chk(dict(row=tn["row"], qid=tn["qid"]), "via")
    return log

# ------------------------------------------------------------------------------------------ region tints (static)
def paint_tints(rgb, land, geom, tints):
    """Soft, unlabelled watercolour wash over a region (land only), gaussian around the region's P625 point.
    Painted INTO the static basemap: it never moves, fades or pumps."""
    img = rgb.astype(np.float32); H, W = land.shape; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    for tn in tints:
        g = wikidata_p625(tn["qid"]); x, y = geom.px(g["lon"], g["lat"]); r = tn["radius_km"] / geom.km_per_px
        ax = tn.get("aspect", 1.0)
        d2 = ((X - x) / (r * ax)) ** 2 + ((Y - y) / r) ** 2
        a = np.exp(-d2) * tn.get("strength", 0.2) * land
        col = np.float32(tn.get("color", [172, 124, 108])) / 255.0
        img = img * (1 - a[..., None]) + img * col * a[..., None]
    return np.clip(img, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------------------------------ route geometry
def leg_points(p0, p1, bow, step=6.0):
    """Straight leg with an optional gentle hand-drawn bow (fraction of leg length, + = left of travel). Dense points so
    the locked Catmull-Rom spline passes through them without overshooting at sharp turns."""
    d = p1 - p0; L = float(np.hypot(*d)); n = max(2, int(L / step)); s = np.linspace(0, 1, n)
    nrm = np.float64([-d[1], d[0]]) / (L + 1e-9)
    return p0[None] + s[:, None] * d[None] + (4 * s * (1 - s) * bow * L)[:, None] * nrm[None]

def chain_path(pts, kinds, bows, rounds):
    """Polyline through pins; at region vias the corner is rounded (quadratic Bezier) so the line sweeps THROUGH the
    region's tint without making a sharp turn that would read as a located spot."""
    pts = [np.float64(p) for p in pts]; n = len(pts)
    entry, exit_ = list(pts), list(pts)
    for k in range(1, n - 1):
        if kinds[k] != "via": continue
        a, b = pts[k - 1] - pts[k], pts[k + 1] - pts[k]; la, lb = np.hypot(*a), np.hypot(*b); r = rounds[k] * min(la, lb)
        entry[k], exit_[k] = pts[k] + a / la * r, pts[k] + b / lb * r
    P = [pts[0][None]]
    for k in range(1, n):
        P.append(leg_points(exit_[k - 1], entry[k], bows[k])[1:])
        if kinds[k] == "via" and k < n - 1:
            s = np.linspace(0, 1, 14)[1:, None]
            P.append((1 - s) ** 2 * entry[k] + 2 * s * (1 - s) * pts[k] + s ** 2 * exit_[k])
    return np.concatenate(P)

STYLE = {  # documented (Map 1) vs claimed (Map 2): the difference is nib dash + strength + stamp, never text
    "documented": dict(dash=None,     strength=1.00, stamp_dot=None, stamp_bloom=None),
    "claimed":    dict(dash=[14, 12], strength=0.80, stamp_dot=0.0,  stamp_bloom=0.0),
}
INKS = {
    "house": {},                                                                 # locked red-brown nib ink
    "slate": dict(wet_color=[24, 34, 52], dry_color=[58, 74, 96]),               # 1330 places on Map 1: separate colour
}
LABEL_COL = {"house": [64, 34, 22], "slate": [36, 50, 70]}

# ------------------------------------------------------------------------------------------ labels
FONT_SC = "/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf"
FONT_IT = "/usr/share/fonts/truetype/sand-box/google/IM Fell French Canon/IMFellFrenchCanon-Italic.ttf"

class Label:
    """Small period-serif place name, rendered once at plate resolution; fades in (0.4 s) when its stamp lands and is
    static afterwards. Thin parchment halo under the letters keeps it legible on sea or ink."""
    def __init__(s, text, xy, side, t_on, ink, px, region=False, gap=20.0):
        from PIL import Image, ImageDraw, ImageFont
        f = ImageFont.truetype(FONT_IT if region else FONT_SC, int(px * (1.05 if region else 1.0)))
        if region: text = " ".join(text)                                           # letter-spaced region name
        l, t_, r, b = f.getbbox(text); w, h = r - l, b - t_; pad = 8
        im = Image.new("L", (w + 2 * pad, h + 2 * pad), 0); ImageDraw.Draw(im).text((pad - l, pad - t_), text, font=f, fill=255)
        a = np.asarray(im, np.float32) / 255.0; x, y = xy
        ox = {"E": gap, "W": -gap - w, "N": -w / 2, "S": -w / 2, "NE": gap * 0.7, "SE": gap * 0.7, "NW": -gap * 0.7 - w, "SW": -gap * 0.7 - w, "C": -w / 2}[side]
        oy = {"E": -h / 2, "W": -h / 2, "N": -gap - h, "S": gap, "NE": -gap * 0.7 - h, "NW": -gap * 0.7 - h, "SE": gap * 0.7, "SW": gap * 0.7, "C": -h / 2}[side]
        s.x0, s.y0 = int(round(x + ox - pad)), int(round(y + oy - pad)); s.a = a
        s.halo = np.clip(cv2.GaussianBlur(cv2.dilate(a, np.ones((5, 5), np.uint8)), (0, 0), 2.0) * 1.4, 0, 1)
        s.t_on, s.ink, s.text = t_on, np.float32(ink), text
    def bbox(s): return s.x0, s.y0, s.x0 + s.a.shape[1], s.y0 + s.a.shape[0]
    def draw(s, img, t):
        k = float(ENG.smoothstep(s.t_on + 0.05, s.t_on + 0.45, np.float32(t)))
        if k <= 0: return
        x0, y0, x1, y1 = s.bbox(); H, W = img.shape[:2]
        cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        roi = img[cy0:cy1, cx0:cx1]; a = s.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * k; hl = s.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * k * 0.5
        roi[...] = roi * (1 - hl[..., None]) + np.float32([236, 224, 190]) * hl[..., None]
        roi[...] = roi * (1 - 0.92 * a[..., None]) + s.ink * 0.92 * a[..., None]

# ------------------------------------------------------------------------------------------ route + pins layer
def _marker(base, xy, t_on, scale, st):
    m = {**dict(color=[0, 0, 0], pulse_hz=0, gain=1, ring=False, style="ink"), **base, "xy": [float(v) for v in xy], "t_on": t_on,
         "radius": base["radius"] * scale, "width": base["width"] * scale, "dot": base["dot"] * scale, "start_deg": -100}
    if st["stamp_dot"] is not None: m["dot"] = st["stamp_dot"]
    if st["stamp_bloom"] is not None: m["bloom"] = st["stamp_bloom"]
    return m

class Layers:
    """Chains: one locked MapLight nib each (explicit t0/t1 per chain; a negative window = already drawn and dry).
    Pin groups: MapLight with markers only (no route). Labels fade in as each stamp lands."""
    def __init__(s, cfg, geom, plate):
        H, W = geom.H, geom.W; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        ctx = dict(H=H, W=W, Y=Y, X=X, plate=plate, half=cfg["duration"]); zero = np.zeros((H, W), np.float32)
        s.layers, s.labels, s.meta = [], [], []; s.allow = np.zeros((H, W), bool); mk_base = NIB["markers"]; lpx = cfg.get("label_px", 30)
        for ci, ch in enumerate(cfg.get("chains", [])):
            st = STYLE[ch["style"]]; sc = ch.get("scale", 1.0); ink = {**NIB["ink"], **INKS[ch.get("ink", "house")], **ch.get("ink_override", {})}
            stops = ch["stops"]; ll = [wikidata_p625(x["qid"]) for x in stops]; pts = [geom.px(g["lon"], g["lat"]) for g in ll]
            kinds = ["pin" if x.get("pin", True) else "via" for x in stops]
            P = chain_path(pts, kinds, [x.get("bow", ch.get("bow", 0.04)) for x in stops], [x.get("round", 0.3) for x in stops])
            p = {"ink": ink, "markers": [], "route": {**NIB["route"], "points": P.tolist(), "t0": ch["t0"], "t1": ch["t1"],
                 "width": NIB["route"]["width"] * sc, "dash": (st["dash"] and [v * sc for v in st["dash"]]) or None}}
            lay = ENG.MapLight(ctx, zero, st["strength"], p, np.random.default_rng([cfg["seed"], ci]))
            N = lay.nb; cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(N["D"], axis=0).T))])
            first_pin = True
            for x, g, q, kd in zip(stops, ll, pts, kinds):
                i = int(np.argmin(np.hypot(*(N["D"] - np.float64(q)).T))); ta = float(np.interp(cum[i], N["Ls"], N["ts"]))
                if kd == "pin" and not x.get("no_stamp"):
                    lay.markers.append(_marker(mk_base[0] if first_pin and not x.get("arrival") else mk_base[1], q, ta, sc * x.get("stamp_scale", 1.0), st))
                    first_pin = False
                if x.get("label"):
                    lt = ta if not x.get("label_t") else x["label_t"]
                    s.labels.append(Label(x["label"], q if kd == "pin" else geom.px(*x.get("label_lonlat", (g["lon"], g["lat"]))), x.get("side", "E"), lt,
                                          LABEL_COL[ch.get("ink", "house")], lpx, region=(kd == "via"), gap=x.get("gap", 20 * sc)))
                s.meta.append(dict(row=x["row"], qid=x["qid"], kind=kd, label=x.get("label"), style=ch["style"], ink=ch.get("ink", "house"),
                                   lonlat=[g["lon"], g["lat"]], xy=[round(float(v), 1) for v in q], t=round(ta, 3)))
            s.layers.append(lay); s.allow |= lay.allow()
        for gi, gp in enumerate(cfg.get("pins", [])):
            st = STYLE[gp.get("style", "documented")]; ink = {**NIB["ink"], **INKS[gp.get("ink", "house")]}; sc = gp.get("scale", 1.0)
            lay = ENG.MapLight(ctx, zero, st["strength"], {"ink": ink, "markers": []}, np.random.default_rng([cfg["seed"], 100 + gi]))
            for k, x in enumerate(gp["items"]):
                g = wikidata_p625(x["qid"]); q = geom.px(g["lon"], g["lat"]); ta = gp["t0"] + k * gp["step"]
                lay.markers.append(_marker(mk_base[0], q, ta, sc, st))
                if x.get("label"): s.labels.append(Label(x["label"], q, x.get("side", "E"), ta, LABEL_COL[gp.get("ink", "house")], lpx, gap=x.get("gap", 18 * sc)))
                s.meta.append(dict(row=x["row"], qid=x["qid"], kind="pin (no route)", label=x.get("label"), ink=gp.get("ink", "house"),
                                   lonlat=[g["lon"], g["lat"]], xy=[round(float(v), 1) for v in q], t=round(ta, 3)))
            s.layers.append(lay); s.allow |= lay.allow()
        for L in s.labels:
            x0, y0, x1, y1 = L.bbox(); s.allow[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
            if x0 < 0 or y0 < 0 or x1 > W or y1 > H: raise RuntimeError(f"label {L.text!r} runs off the plate")
    def draw(s, img, t):
        for lay in s.layers: lay.overlay(img, t)
        for L in s.labels: L.draw(img, t)

# ------------------------------------------------------------------------------------------ camera (single transform)
def cam_matrix(cfg, geom, t, center):
    W, H = cfg["out_wh"]; z0, z1 = cfg.get("push", [1.0, 1.06]); u = ENG.ease(t, 0.0, cfg["duration"]); z = z0 + (z1 - z0) * u
    s = max(W / geom.W, H / geom.H) * z; vw, vh = W / s, H / s
    cx = min(max(center[0], vw / 2), geom.W - vw / 2); cy = min(max(center[1], vh / 2), geom.H - vh / 2)
    cx = geom.W / 2 + (cx - geom.W / 2) * u; cy = geom.H / 2 + (cy - geom.H / 2) * u     # start full frame, drift with the push
    return np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]]), z

def to_output(cfg, plate_frame, M):
    W, H = cfg["out_wh"]; assert M[0, 0] <= 1.0 + 1e-6, "would upscale"
    return cv2.warpAffine(plate_frame, M, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)

# ------------------------------------------------------------------------------------------ shot
class Shot:
    def __init__(s, cfg_path):
        cfg = json.load(open(cfg_path)); s.cfg = cfg; s.name = cfg["name"]
        s.authority = check_against_authority(cfg, read_places_md())
        gaz = json.load(open(GAZ))["places"]                       # control-point headlands only
        PW, PH = cfg["plate_wh"]
        s.density = guardrails.check_pixel_density((PW, PH), cfg["out_wh"], cfg.get("push", [1.0, 1.06]), mode="refuse", name=s.name)
        s.geom = MapGeom(cfg, PW, PH)
        rgb, masks = build_basemap(s.geom, cfg, cfg["seed"])
        s.cp = fit_control_points(s.geom, masks["land"] | masks["coast"], cfg["control_points"], gaz)
        land = (masks["land"] | masks["coast"]).astype(np.float32)
        rgb = paint_tints(rgb, cv2.GaussianBlur(land, (0, 0), 1.0), s.geom, cfg.get("tints", []))
        s.plate, s.masks = rgb, masks
        cv2.imwrite(os.path.join(HERE, "cache", f"{s.name}_basemap.png"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        s.platef = rgb.astype(np.float32)
        s.lay = Layers(cfg, s.geom, s.platef)
        pins = np.float64([m["xy"] for m in s.lay.meta if m["kind"] != "via"])
        s.center = cfg.get("push_center_px") or (pins.mean(0) if len(pins) else (PW / 2, PH / 2))
    def plate_frame(s, t):
        img = s.platef.copy(); s.lay.draw(img, t); return np.clip(img + 0.5, 0, 255).astype(np.uint8)
    def frame(s, t):
        M, z = cam_matrix(s.cfg, s.geom, t, s.center); return to_output(s.cfg, s.plate_frame(t), M), M
    def proofs(s, fps):
        cfg = s.cfg; n = int(round(cfg["duration"] * fps)); P = s.plate.astype(np.int16)
        prot = {k: 0 for k in s.masks}; outside_allow = 0; lum_full, lum_sw, vis1 = [], [], None; sw_small = None
        for i in range(n):
            t = i / fps; pf = s.plate_frame(t); d = np.abs(pf.astype(np.int16) - P).max(-1) > 0
            outside_allow += int((d & ~s.lay.allow).sum())
            for k, m in s.masks.items(): prot[k] += int((d & m & ~s.lay.allow).sum())
            M, _ = cam_matrix(cfg, s.geom, t, s.center); o = to_output(cfg, pf, M); b = to_output(cfg, s.plate, M)
            os_ = cv2.resize(o, (640, 360), interpolation=cv2.INTER_AREA).astype(np.float32); bs = cv2.resize(b, (640, 360), interpolation=cv2.INTER_AREA).astype(np.float32)
            Lo, Lb = ENG.lum(os_), ENG.lum(bs); dl = Lo - Lb
            if sw_small is None or i % 15 == 0:
                sw_small = cv2.resize(to_output(cfg, s.lay.allow.astype(np.uint8) * 255, M), (640, 360), interpolation=cv2.INTER_AREA) > 0
            lum_full.append(float(Lo.mean())); lum_sw.append(float(dl[sw_small].mean()) if sw_small.any() else 0.0)
            if abs(t - 1.0) < 0.5 / fps: vis1 = int((np.abs(dl) * 255 > 12).sum())
        def hf(sig):
            x = np.float64(sig) - np.mean(sig); F = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / fps)
            return round(float(F[f > 5].sum() / (F[1:].sum() + 1e-12)), 5)
        swing = max((max(lum_full[j:j + fps]) - min(lum_full[j:j + fps])) / (np.mean(lum_full[j:j + fps]) + 1e-9) for j in range(0, n - fps + 1, max(1, fps // 2)))
        hff, hfs = hf(lum_full), hf(lum_sw)
        return dict(
            shot=s.name, pixel_density=s.density,
            basemap=dict(plate_wh=cfg["plate_wh"], native=True, upscaled=False, camera="single affine, INTER_AREA, scale<=1 asserted",
                         source="Natural Earth 10m land/lakes/rivers v5.1.1 (public domain)", tints=cfg.get("tints", [])),
            authority=dict(file=PLACES_MD, coords=f"{WD_RAW}/<QID>.json (Wikidata P625, CC0)", rows=s.authority),
            protected_pixels=dict(note="plate space, every frame; changed px OUTSIDE the ink/stamp/label allow-mask, split by class",
                                  changed_outside_allow=outside_allow, by_class=prot, allow_mask_frac=round(float(s.lay.allow.mean()), 4), pass_=outside_allow == 0),
            control_points=s.cp, places=s.lay.meta,
            phone_640x360=dict(first_second_visible_px_gt12=vis1, first_second_pass=bool(vis1 and vis1 >= 150),
                               hf_energy_frac_gt5hz_full=hff, hf_energy_frac_gt5hz_ink=hfs, max_1s_full_frame_swing=round(float(swing), 4),
                               pass_=bool(hff < 0.05 and hfs < 0.05 and swing < 0.08)))

def ffmpeg_writer(path, W, H, fps, crf=20):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", path],
                            stdin=subprocess.PIPE)

def md5(p):
    h = hashlib.md5(); f = open(p, "rb")
    for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("configs", nargs="+"); ap.add_argument("--reel"); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--no-proofs", action="store_true"); ap.add_argument("--no-poc", action="store_true"); ap.add_argument("--still-only", action="store_true"); a = ap.parse_args()
    if a.reel and os.path.exists(a.reel): sys.exit(f"refusing to overwrite {a.reel}")
    shots = [Shot(c) for c in a.configs]; W, H = shots[0].cfg["out_wh"]
    for s in shots:
        fin = s.plate_frame(s.cfg["duration"]); st = cv2.resize(fin, (W, H), interpolation=cv2.INTER_AREA)   # full map, 2048->1920 downscale only
        cv2.imwrite(os.path.join(HERE, "final", f"{s.name}_final_16x9.png"), cv2.cvtColor(st, cv2.COLOR_RGB2BGR))
        if a.still_only: continue
        if not a.no_proofs:
            pr = s.proofs(a.fps); json.dump(pr, open(os.path.join(HERE, "proofs", f"{s.name}.json"), "w"), indent=1)
            print(s.name, "density", pr["pixel_density"], "protected", pr["protected_pixels"]["changed_outside_allow"],
                  "cp_rms_km", pr["control_points"]["rms_km"], "phone", pr["phone_640x360"], flush=True)
        if not a.no_poc:
            poc = os.path.join(HERE, "poc", f"{s.name}_540p.mp4"); w = ffmpeg_writer(poc, 960, 540, a.fps, 23)
            for i in range(int(round(s.cfg["duration"] * a.fps))):
                f, _ = s.frame(i / a.fps); w.stdin.write(cv2.resize(f, (960, 540), interpolation=cv2.INTER_AREA).tobytes())
            w.stdin.close(); w.wait()
    if a.reel:
        w = ffmpeg_writer(a.reel, W, H, a.fps, 20)
        for s in shots:
            for i in range(int(round(s.cfg["duration"] * a.fps))): w.stdin.write(s.frame(i / a.fps)[0].tobytes())
        w.stdin.close(); w.wait(); print("reel", a.reel, md5(a.reel))

if __name__ == "__main__":
    main()
