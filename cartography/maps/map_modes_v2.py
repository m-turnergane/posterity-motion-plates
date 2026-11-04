#!/usr/bin/env python3
"""map_modes_v2 -- static painted basemap MODES for the Posterity route maps (engine R&D, v2).

Imported by map_route_v2.py.  Every mode is built from the SAME real geodata at plate resolution:
  * Natural Earth 10m land / lakes / rivers+lake centerlines (public domain, naturalearthdata.com, v5.1.1)
  * ETOPO1 1-arc-minute relief subset (NOAA NCEI, public domain) sources/etopo/etopo1_eu.nc, sampled per plate pixel
    through the inverse of the plate's Lambert azimuthal equal-area projection
  * realm fills sources/realms/realms_1327_v1.geojson, built by build_realms_1327.py from OpenHistoricalMap (CC0)
    relations + hand-coarse areas exactly per longform/edward-ii-feature/REALMS-1327-v1.md; checked by
    verify_realms_1327.py (geometry) and Terrain.realm_weights (raster).  Swappable: cfg["realms_geojson"].

Modes (select per shot with cfg["mode"], or crossfade with cfg["mode_from"], cfg["mode_to"], cfg["xfade_t"]=[t0,t1]):
  realms_worn     (style A, lead) aged house plate after the Persepolis / Ugarit / Tamerlane references: deep teal
                  watercolour sea, worn ochre paper, subtle painted relief, realm cores in chipped, patchy paint coats.
  campaign_atlas  (style B) painted relief is the hero (hypsometric wash + hillshade + snow on the high Alps,
                  procedural forests, river valleys, inked rivers); realms ride over it as soft translucent washes.
  terrain         code only (NOT a deliverable): campaign_atlas without realms.
The basemap is static.  No text is ever drawn here (place names live in map_route_v2), no frame vignette, no letterbox.
Forests are PROCEDURAL (elevation + noise), not land-cover data.
"""
import importlib.util, json, math, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
V1 = _load("map_route_v1_ro", os.path.join(HERE, "map_route_v1.py"))      # read-only reuse of v1 readers/projection
ENG = V1.ENG
ETOPO = os.path.join(HERE, "sources", "etopo", "etopo1_eu.nc")
REALMS = os.path.join(HERE, "sources", "realms", "realms_1327_v1.geojson")
MODES = ("realms_worn", "campaign_atlas", "terrain")

# rivers: owner's list (inked) + faint extras.  NE names arrive mis-decoded (utf-8 read as latin-1); fixed in _nm.
RIVERS_MAJOR = {"Thames", "Severn", "Seine", "Rhine", "Rhein", "Rhin", "Nederrijn", "Waal", "Lek", "IJssel", "Rhône", "Po"}
RIVERS_MINOR = {"Loire", "Garonne", "Meuse", "Maas", "Moselle", "Mosel", "Marne", "Saône", "Dordogne", "Durance", "Danube", "Donau",
                "Shannon", "Trent", "Elbe", "Main", "Ebro", "Wye", "Avon", "Somme", "Scheldt", "Schelde", "Escaut", "Oise", "Yonne", "Allier"}

def _nm(s):
    s = (s or "").strip("\x00").strip()
    try: return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError): return s

# ------------------------------------------------------------------------------------------ geometry helpers
def inverse_laea(proj, x, y):
    """Inverse of V1.LAEA (spherical): km east/north -> lon/lat degrees."""
    R = V1.R_EARTH; rho = np.hypot(x, y); c = 2 * np.arcsin(np.clip(rho / (2 * R), -1, 1))
    sc, cc = np.sin(c), np.cos(c); p0 = proj.p0
    lat = np.arcsin(np.clip(cc * math.sin(p0) + np.where(rho > 0, y * sc * math.cos(p0) / np.maximum(rho, 1e-9), 0), -1, 1))
    lon = proj.l0 + np.arctan2(x * sc, rho * math.cos(p0) * cc - y * math.sin(p0) * sc)
    return np.degrees(lon), np.degrees(lat)

def plate_lonlat(geom):
    """lon/lat of every plate pixel centre (analytic mapping = the one the land raster used)."""
    Y, X = np.mgrid[0:geom.H, 0:geom.W].astype(np.float64) + 0.5
    return inverse_laea(geom.proj, geom.x0 + X / geom.sc, geom.y1 - Y / geom.sc)

def load_etopo():
    from scipy.io import netcdf_file
    f = netcdf_file(ETOPO, "r", mmap=False)
    z = np.array(f.variables["altitude"].data, np.float32); lat = np.array(f.variables["latitude"].data, np.float64)
    lon = np.array(f.variables["longitude"].data, np.float64); f.close(); return z, lon, lat

def elevation(geom):
    z, lon, lat = load_etopo(); LO, LA = plate_lonlat(geom)
    mx = ((LO - lon[0]) / (lon[1] - lon[0])).astype(np.float32); my = ((LA - lat[0]) / (lat[1] - lat[0])).astype(np.float32)
    e = cv2.remap(z, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=-3000.0)
    return cv2.GaussianBlur(e, (0, 0), 1.2), (LO, LA)

def hillshade(elev, km_per_px, az=315.0, alt=40.0, zf=1.0):
    gy, gx = np.gradient(elev.astype(np.float64), km_per_px * 1000.0)
    slope = np.arctan(zf * np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    a, z = math.radians(az), math.radians(90 - alt)
    hs = np.cos(z) * np.cos(slope) + np.sin(z) * np.sin(slope) * np.cos(a - aspect - math.pi / 2)
    flat = math.cos(z)
    return (hs - flat).astype(np.float32)          # 0 on flat ground, + lit, - shadow

def smoothstep(a, b, x): return ENG.smoothstep(a, b, x)
def pn(rng, H, W, lo, hi, beta=2.0, ax=1.0, ay=1.0): return ENG.pnoise(rng, H, W, lo, hi, beta, ax, ay)

# ------------------------------------------------------------------------------------------ realms
def load_realms(path=REALMS):
    d = json.load(open(path)); return d, [f for f in d["features"]]

def realm_masks(geom, feats, ss=2):
    out = {}
    for f in feats:
        g = f["geometry"]
        if g["type"] not in ("Polygon", "MultiPolygon"): continue
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        m = np.zeros((geom.H * ss, geom.W * ss), np.uint8)
        for poly in polys:
            for k, ring in enumerate(poly):
                r = np.float64(ring); p = np.int32(np.round(geom.analytic(r[:, 0], r[:, 1]) * ss * 16))
                cv2.fillPoly(m, [p], 255 if k == 0 else 0, cv2.LINE_8, shift=4)
        out[f["properties"]["id"]] = cv2.resize(m, (geom.W, geom.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    return out

# REALMS-1327 family palettes (families, not polities: one Imperial hue, one France family, England+Wales one hue)
REALM_COL_A = {"england": [150, 62, 46], "england_light": [164, 88, 68], "scotland": [118, 80, 108],
               "france": [80, 100, 148], "france_fam": [120, 134, 162], "empire": [112, 122, 64],
               "castile": [140, 92, 86], "aragon": [184, 132, 60], "portugal": [104, 128, 116]}
REALM_COL_B = {"england": [170, 52, 40], "england_light": [192, 90, 70], "scotland": [122, 72, 142],
               "france": [60, 92, 168], "france_fam": [112, 138, 192], "empire": [196, 168, 60],
               "castile": [150, 70, 110], "aragon": [214, 140, 40], "portugal": [70, 140, 112]}
FLANDERS_LON = (3.0, 4.3)     # R08/R09: France -> Empire gradient across the Scheldt (lon of the blend ramp)

# ------------------------------------------------------------------------------------------ shared terrain
class Terrain:
    """Everything both modes share, computed once per shot at plate size."""
    def __init__(s, geom, cfg):
        s.geom, s.cfg = geom, cfg; b = cfg.get("basemap", {}); bbox = geom.lonlat_bbox(); H, W = geom.H, geom.W
        s.kmpp = geom.km_per_px
        land = V1.raster_polys(geom, f"{V1.NE}/ne_10m_land/ne_10m_land.shp", bbox)
        lakes = V1.raster_polys(geom, f"{V1.NE}/ne_10m_lakes/ne_10m_lakes.shp", bbox, filt=lambda r: V1._rank(r) <= b.get("lake_rank", 6))
        s.land = np.clip(land - lakes, 0, 1); s.lb = (s.land > 0.5).astype(np.uint8)
        s.d_sea = cv2.distanceTransform(1 - s.lb, cv2.DIST_L2, 5); s.d_land = cv2.distanceTransform(s.lb, cv2.DIST_L2, 5)
        rw = b.get("river_px", 1.0 if s.kmpp > 0.8 else 1.4)
        riv = f"{V1.NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp"
        isriv = lambda r: r.get("featurecla", "").startswith("River") or r.get("featurecla", "").startswith("Lake Centerline")
        names = lambda r: {_nm(r.get("name")), _nm(r.get("name_en")), _nm(r.get("name_alt"))}
        s.riv_major = V1.raster_lines(geom, riv, bbox, lambda r: isriv(r) and bool(names(r) & RIVERS_MAJOR), lambda r: rw * 1.6) * s.land
        s.riv_minor = V1.raster_lines(geom, riv, bbox, lambda r: isriv(r) and bool(names(r) & RIVERS_MINOR) and not (names(r) & RIVERS_MAJOR),
                                      lambda r: rw * 1.0) * s.land
        s.elev, (s.lon, s.lat) = elevation(geom)
        s.elev_land = np.where(s.lb > 0, np.maximum(s.elev, 0), 0).astype(np.float32)
        hs = hillshade(s.elev_land, s.kmpp, 315, 40, b.get("relief_zf", 2.2 if s.kmpp > 0.8 else 1.6))
        hs2 = hillshade(s.elev_land, s.kmpp, 250, 50, 1.6)
        raw = (0.7 * hs + 0.3 * hs2) * s.land
        s.hs_scale = max(float(np.percentile(np.abs(raw[s.lb > 0]), 98)), 0.05)       # normalise per framing
        s.hs = np.tanh(raw / s.hs_scale).astype(np.float32)
        s.local_relief = (s.elev_land - cv2.GaussianBlur(s.elev_land, (0, 0), 6.0)).astype(np.float32)
        s.realm_fc, feats = load_realms(cfg.get("realms_geojson", REALMS))
        s.realms = realm_masks(geom, feats); s.realm_meta = {f["properties"]["id"]: f["properties"] for f in feats}
        s.realm_pts = {f["properties"]["id"]: f["geometry"]["coordinates"] for f in feats if f["geometry"]["type"] == "Point"}
        s.edge = np.clip(cv2.GaussianBlur(s.land, (0, 0), 0.8) * 4 * (1 - cv2.GaussianBlur(s.land, (0, 0), 0.8)), 0, 1)

    def realm_weights(s, warp_km=4.0):
        """REALMS-1327 soft fill field.  Every fill feature is rasterised, given a small hand wobble, then blurred with
        its own feather (sigma = feather_km/2) and normalised by blurred land, so neighbouring realms meet in a soft
        colour gradient (no line anywhere) and fade to bare paper at neutral edges.  Returns {family: weight} where
        weight = coverage share x feature alpha (sum <= 1).  'flanders' is returned as its own key; the painters colour
        it with the France->Empire ramp.  Deterministic (fixed seed) so the raster verifier sees the painted field."""
        if hasattr(s, "_rw"): return s._rw
        H, W = s.lb.shape; rng = np.random.default_rng(1327)
        Y, X = np.mgrid[0:H, 0:W].astype(np.float32); amp = warp_km / s.kmpp
        att = np.ones((H, W), np.float32)                          # wobble is pinned (-> 0) within ~8 km of every
        try:                                                        # REALMS-1327 checkpoint, so the hand wobble can
            import verify_realms_1327 as _VR                        # never push a border across a verified place
            for _n, lo, la, _r, _a in _VR.POINTS:
                x0, y0 = s.geom.analytic(np.float64([lo]), np.float64([la]))[0]
                att = np.minimum(att, 1 - np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) * s.kmpp ** 2 / (2 * 8.0 ** 2)))
        except Exception:
            pass
        wx = (X + amp * att * pn(rng, H, W, 220, 20, 2.4)).astype(np.float32); wy = (Y + amp * att * pn(rng, H, W, 220, 20, 2.4)).astype(np.float32)
        landf = s.land.astype(np.float32); out = {}
        for rid, m in s.realms.items():
            pr = s.realm_meta[rid]
            mw = cv2.remap(m, wx, wy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) * landf
            if mw.max() < 0.5: continue
            sg = max(pr["feather_km"] * 0.5 / s.kmpp, 1.0)
            w = cv2.GaussianBlur(mw, (0, 0), sg) / np.maximum(cv2.GaussianBlur(landf, (0, 0), sg), 0.05)
            w = np.clip(w, 0, 1) * landf * pr["alpha"]
            # core weighting: a realm's own interior keeps dominance over neighbours' feathered bleed (small units like
            # Montpellier or the County of Burgundy edge must not read as the bigger neighbour at small scales)
            core = cv2.GaussianBlur(mw, (0, 0), max(1.5 / s.kmpp, 0.7))
            s._core = getattr(s, "_core", {}); s._core[rid] = core
            key = "flanders" if pr["family"] == "flanders" else pr["family"]
            out[key] = out.get(key, 0) + w
        if getattr(s, "_core", None):                              # outside-of-own-core bleed is damped to 35 %
            fam_core = {}
            for rid, core in s._core.items():
                pr = s.realm_meta[rid]; key = "flanders" if pr["family"] == "flanders" else pr["family"]
                fam_core[key] = np.maximum(fam_core.get(key, 0), core)
            anycore = np.clip(sum(fam_core.values()), 0, 1)
            for key in out:
                own = fam_core.get(key, 0)
                out[key] = out[key] * (1 - 0.65 * anycore * (1 - np.clip(own, 0, 1)))
        for rid, pr in s.realm_meta.items():                        # gaussian fringes (Milan, R20): no polygon at all
            if pr.get("render") != "gaussian": continue
            lon0, lat0 = s.realm_pts[rid]
            x0, y0 = s.geom.analytic(np.float64([lon0]), np.float64([lat0]))[0]
            d2 = ((X - x0) ** 2 + (Y - y0) ** 2) * s.kmpp ** 2
            out[pr["family"]] = out.get(pr["family"], 0) + pr["alpha"] * np.exp(-d2 / (2 * pr["sigma_km"] ** 2)) * landf
        tot = sum(out.values()); k = np.where(tot > 1, 1 / np.maximum(tot, 1e-6), 1.0)
        s._rw = {f: (w * k).astype(np.float32) for f, w in out.items()}
        return s._rw

    def realm_colour(s, pal):
        """(H,W,3) colour of the realm field + (H,W) coverage, with Flanders on the France->Empire ramp."""
        rw = s.realm_weights(); H, W = s.lb.shape
        col = np.zeros((H, W, 3), np.float32); cov = np.zeros((H, W), np.float32)
        t = smoothstep(FLANDERS_LON[0], FLANDERS_LON[1], s.lon)[..., None].astype(np.float32)
        for f, w in rw.items():
            if f == "flanders":
                c = (1 - t) * (0.8 * np.float32(pal["france"]) + 0.2 * np.float32([160, 150, 130])) + t * np.float32(pal["empire"])
            else:
                c = np.float32(pal[f])
            col += c * w[..., None]; cov += w
        col = col / np.maximum(cov, 1e-6)[..., None]
        return col, np.clip(cov, 0, 1)


# ------------------------------------------------------------------------------------------ paper
def paper(rng, H, W, base, grain_std, fibre=True, stains=0.07):
    p = np.ones((H, W, 3), np.float32) * np.float32(base)
    blot = pn(rng, H, W, 600, 40, 2.6); p *= (1 + stains * blot)[..., None]
    if fibre:
        f1 = pn(rng, H, W, 40, 1.0, 1.6, ax=0.25, ay=1.0); f2 = pn(rng, H, W, 40, 1.0, 1.6, ax=1.0, ay=0.3)
        p *= (1 + 0.5 * grain_std / 128.0 * (f1 + f2) * 0.7)[..., None]
    g = pn(rng, H, W, 4, 0.7, 1.2); p *= (1 + 0.6 * grain_std / 128.0 * g)[..., None]
    return p

def foxing(rng, H, W, n, kmin=2, kmax=9):
    m = np.zeros((H, W), np.float32)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H); r = rng.uniform(kmin, kmax)
        cv2.circle(m, (int(x), int(y)), int(r), float(rng.uniform(0.3, 1.0)), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 2.0)

def edge_age(rng, H, W, px, amount):
    """Paper ageing at the sheet edge, baked into the paper (irregular, uneven); NOT an overlay vignette.
    amount=0 disables it."""
    if amount <= 0: return np.zeros((H, W), np.float32)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32); d = np.minimum(np.minimum(X, W - 1 - X), np.minimum(Y, H - 1 - Y))
    d = d + pn(rng, H, W, 220, 6, 2.0) * px * 0.45
    return (amount * (1 - smoothstep(0, px, d))).astype(np.float32)

# ------------------------------------------------------------------------------------------ style A: realms_worn
def mode_realms_worn(T, seed):
    """Aged house plate (refs: Persepolis seq2-map, Ugarit p03, Tamerlane seq2m_map; sampled stats in README)."""
    H, W = T.geom.H, T.geom.W; rng = np.random.default_rng([seed, 11]); b = T.cfg.get("style_A", {})
    # --- sea: deep teal watercolour, mottled; light shallow rim; darker offshore (ref sea median ~(33..60,67..90,78..101))
    deep = np.float32([30, 62, 76]); mid = np.float32([52, 86, 98]); shallow = np.float32([92, 126, 124])
    off = smoothstep(0, 140, T.d_sea)[..., None]
    sea = mid * (1 - off) + deep * off
    mott = pn(rng, H, W, 380, 14, 2.6)[..., None]; cloud = pn(rng, H, W, 120, 6, 2.2)[..., None]
    sea = sea * (1 + 0.09 * mott + 0.05 * cloud)
    sh = np.exp(-T.d_sea / 9.0)[..., None]; sea = sea * (1 - 0.75 * sh) + shallow * 0.75 * sh
    sea = sea * (1 + 0.055 * pn(rng, H, W, 5, 0.7, 1.3)[..., None])                         # fine sea grain (~std 7)
    # --- land: worn ochre paper + painted relief (brown ridges, olive valleys)
    ldp = paper(rng, H, W, [192, 150, 104], 15, stains=0.09)
    e = T.elev_land
    low = smoothstep(220, 0, e) * smoothstep(0.0, 8.0, T.d_land)
    olive = np.float32([150, 138, 84]); brown = np.float32([128, 88, 54]); pale = np.float32([214, 190, 150])
    ldp = ldp * (1 - 0.30 * low[..., None]) + olive * (0.30 * low)[..., None] * (ldp / 180.0)
    hi = smoothstep(500, 2200, e)[..., None]; ldp = ldp * (1 - 0.35 * hi) + brown * 0.35 * hi
    top = smoothstep(2600, 3600, e)[..., None]; ldp = ldp * (1 - 0.35 * top) + pale * 0.35 * top
    hsA = T.hs * b.get("relief", 1.0)
    ridge = np.clip(T.local_relief / 250.0, -1, 1)
    ldp = ldp * (1 - 0.22 * np.clip(ridge, 0, 1)[..., None]) + brown * (0.22 * np.clip(ridge, 0, 1))[..., None]
    # --- realm coats: worn, aged paint (patchy pigment, chipped/faded edges, brush streaks, pooled edges)
    rc, cov = T.realm_colour(REALM_COL_A)
    if cov.max() > 0:
        e_r = cov
        patch = 0.78 + 0.22 * np.clip(pn(rng, H, W, 260, 18, 2.4), -2, 2) / 2
        brush = 1 + 0.10 * pn(rng, H, W, 90, 2, 1.8, ax=0.15, ay=1.0) * pn(rng, H, W, 400, 60, 2.0)
        chip_n = pn(rng, H, W, 70, 2.0, 1.9)
        wear = np.clip((chip_n * 0.55 + 2.0 * e_r - 0.55) * 2.5, 0, 1)                     # chips concentrate at fading edges
        scuff = np.clip((pn(rng, H, W, 30, 1.0, 1.7) - 1.6) * 2.0, 0, 1) * 0.6               # small rubbed-off spots inside
        a = np.clip(e_r ** 0.7 * wear * patch * brush * (1 - scuff), 0, 1) * b.get("paint", 0.62)
        a = a * smoothstep(0.5, 3.0, T.d_land)                                             # hair of bare paper at shore
        pool = np.clip(cv2.GaussianBlur(np.abs(cv2.Laplacian(a, cv2.CV_32F, ksize=3)), (0, 0), 1.0) * 5.0, 0, 0.25)
        coat = (0.6 * rc + 0.4 * ldp * rc / 200.0) * (1 - pool)[..., None]
        ldp = ldp * (1 - a[..., None]) + coat * a[..., None]
    # relief shows THROUGH the paint (applied after the coats)
    ldp = ldp * (1 + 0.24 * np.clip(hsA, -1, 1))[..., None]
    rim = np.exp(-T.d_land / 3.0)[..., None]; ldp = ldp * (1 - 0.35 * rim) + np.float32([214, 188, 140]) * 0.35 * rim
    a = T.land[..., None]; img = sea * (1 - a) + ldp * a
    # rivers: faded blue-grey pen (majors a touch stronger)
    for m, k in ((T.riv_major, 0.70), (T.riv_minor, 0.35)):
        img = img * (1 - k * m[..., None]) + np.float32([66, 96, 108]) * k * m[..., None]
    # thin dark coast edge, width-varied
    ew = T.edge * np.clip(0.75 + 0.3 * pn(rng, H, W, 80, 4), 0.35, 1.0)
    img = img * (1 - 0.8 * ew[..., None]) + np.float32([40, 34, 26]) * 0.8 * ew[..., None]
    # aged sheet: foxing + stains + irregular edge browning baked into the paper
    fox = foxing(rng, H, W, b.get("foxing", 40)); img *= (1 - 0.10 * fox)[..., None]
    ea = edge_age(rng, H, W, b.get("edge_age_px", 70), b.get("edge_age", 0.0)); img *= (1 - ea)[..., None]
    img *= (1 + 0.045 * pn(rng, H, W, 3, 0.6, 1.0))[..., None]
    return np.clip(img, 0, 255)

# ------------------------------------------------------------------------------------------ style B: campaign_atlas
HYPSO = [(-1, [118, 138, 80]), (80, [126, 144, 84]), (300, [150, 152, 96]), (700, [170, 152, 108]),
         (1400, [150, 128, 100]), (2200, [148, 138, 128]), (2900, [196, 194, 188]), (3600, [238, 238, 232])]

def hypso(e):
    xs = np.float32([h for h, _ in HYPSO]); cs = np.float32([c for _, c in HYPSO])
    return np.stack([np.interp(e, xs, cs[:, k]) for k in range(3)], -1).astype(np.float32)

def forests(T, rng):
    """PROCEDURAL forest placement (no land-cover data): clustered on low hills/upland (100-1700 m), more in the
    north-east and in the Ardennes / Vosges / Black Forest / Massif Central band, thinned in the lowland plains."""
    H, W = T.geom.H, T.geom.W; e = T.elev_land
    n = pn(rng, H, W, 60.0 / T.kmpp, 3.0 / max(T.kmpp, 0.5), 2.6)
    pref = smoothstep(80, 400, e) * (1 - smoothstep(1400, 1900, e))
    score = n + 1.6 * pref
    land = (T.lb > 0) & (e < 1900)
    q = float(np.percentile(score[land], 100 - T.cfg.get("style_B", {}).get("forest_cover_pct", 22)))
    m = smoothstep(q - 0.08, q + 0.25, score) * smoothstep(1.5, 5.0, T.d_land) * (T.riv_major < 0.2)
    trees = np.clip((pn(rng, H, W, 5, 1.0, 1.2) + 0.3) * 2.0, 0, 1)            # canopy stipple
    return m.astype(np.float32), trees.astype(np.float32)

def mode_campaign_atlas(T, seed, realms=True):
    H, W = T.geom.H, T.geom.W; rng = np.random.default_rng([seed, 22]); b = T.cfg.get("style_B", {})
    # sea: deep painted blue with lighter shallows and faint coastal ripple lines
    deep = np.float32([34, 70, 98]); shallow = np.float32([82, 128, 140])
    off = smoothstep(0, 90, T.d_sea)[..., None]; sea = shallow * (1 - off) + deep * off
    sea *= (1 + 0.07 * pn(rng, H, W, 300, 10, 2.4) + 0.03 * pn(rng, H, W, 40, 3, 2.0))[..., None]
    for d0 in (7.0, 15.0, 25.0):
        r = np.exp(-((T.d_sea - d0 - 1.5 * pn(rng, H, W, 120, 10, 2.0)) / 0.9) ** 2) * (T.lb == 0) * (0.22 - d0 * 0.005)
        sea = sea * (1 - r[..., None]) + np.float32([170, 196, 196]) * r[..., None]
    # land: hypsometric wash with brush noise
    e = T.elev_land; e_j = e + 25 * pn(rng, H, W, 200, 8, 2.2)
    ldp = hypso(e_j) * (1 + 0.05 * pn(rng, H, W, 90, 3, 2.0))[..., None]
    # river valleys: greener, lighter floodplains along named rivers
    val = np.clip(cv2.GaussianBlur(T.riv_major + 0.6 * T.riv_minor, (0, 0), 6.0 / max(T.kmpp, 0.4)) * 6, 0, 1) * smoothstep(400, 50, e)
    ldp = ldp * (1 - 0.35 * val[..., None]) + np.float32([134, 158, 86]) * 0.35 * val[..., None]
    # forests (procedural): dark green clumps with canopy stipple
    fm, tr = forests(T, rng)
    fcol = np.float32([64, 92, 50]); a_f = (fm * (0.50 + 0.18 * tr))[..., None] * b.get("forest", 1.0)
    ldp = ldp * (1 - a_f) + fcol * a_f
    # realms: soft translucent washes OVER the terrain (no edge lines)
    if realms:
        rc, cov = T.realm_colour(REALM_COL_B)
        a = (cov * b.get("realm_alpha", 0.40) * (0.9 + 0.1 * pn(rng, H, W, 200, 20, 2.2)))[..., None]
        tint = 0.55 * (ldp * rc / 150.0) + 0.45 * rc * (0.55 + 0.45 * ldp.mean(-1, keepdims=True) / 150.0)   # glaze keeps hue
        ldp = ldp * (1 - a) + tint * a
    # relief: strong hillshade is the hero (multiply + a little highlight)
    hs = T.hs * b.get("relief", 1.0)
    ldp = ldp * (1 + 0.40 * hs)[..., None]
    ldp *= (1 + 0.04 * pn(rng, H, W, 4, 0.7, 1.2))[..., None]
    a = T.land[..., None]; img = sea * (1 - a) + ldp * a
    # inked rivers: majors dark blue ink with variable width, minors faint
    for m, k, col in ((T.riv_major, 0.92, [40, 72, 104]), (T.riv_minor, 0.55, [70, 104, 128])):
        img = img * (1 - k * m[..., None]) + np.float32(col) * k * m[..., None]
    ew = T.edge * np.clip(0.8 + 0.3 * pn(rng, H, W, 80, 4), 0.4, 1.0)
    img = img * (1 - 0.85 * ew[..., None]) + np.float32([36, 40, 38]) * 0.85 * ew[..., None]
    img *= (1 + 0.03 * pn(rng, H, W, 3, 0.6, 1.0))[..., None]          # canvas tooth
    return np.clip(img, 0, 255)

def render_mode(T, mode, seed):
    if mode == "realms_worn": return mode_realms_worn(T, seed)
    if mode == "campaign_atlas": return mode_campaign_atlas(T, seed, realms=True)
    if mode == "terrain": return mode_campaign_atlas(T, seed, realms=False)
    raise ValueError(f"unknown mode {mode!r}; one of {MODES}")

class Basemap:
    """Per-shot static basemap.  cfg["mode"] OR cfg["mode_from"]+cfg["mode_to"]+cfg["xfade_t"]=[t0,t1] (smoothstep blend
    between two static plates; outside the window it is exactly one plate)."""
    def __init__(s, T, cfg):
        s.cfg = cfg; seed = cfg["seed"]
        if "mode_from" in cfg:
            s.a = render_mode(T, cfg["mode_from"], seed); s.b = render_mode(T, cfg["mode_to"], seed); s.win = cfg["xfade_t"]
        else:
            s.a = render_mode(T, cfg.get("mode", "realms_worn"), seed); s.b = None
    def at(s, t):
        if s.b is None: return s.a
        k = float(ENG.smoothstep(s.win[0], s.win[1], np.float32(t)))
        return s.a if k <= 0 else (s.b if k >= 1 else s.a * (1 - k) + s.b * k)
