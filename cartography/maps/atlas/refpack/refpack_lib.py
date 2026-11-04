"""Refpack shared helpers (read-only reuse of the engine).

Reuses, unchanged: map_route_v1 (LAEA projection, MapGeom, NE shapefile readers, MAP-PLACES-v1 parser, Wikidata P625,
authority check), map_modes_v2 (ETOPO1 sampling, hillshade, realm masks, NE name fix), map_route_v2_r2 (label placer),
verify_realms_1327 (40-check realm verifier).  Nothing here writes outside atlas/refpack/.
"""
import sys; sys.dont_write_bytecode = True
import os, json, math, importlib.util, copy
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.abspath(os.path.join(HERE, "..", ".."))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m

V1 = _load("rp_map_route_v1", f"{MAPS}/map_route_v1.py")
MM = _load("rp_map_modes_v2", f"{MAPS}/map_modes_v2.py")
R2 = _load("rp_map_route_v2_r2", f"{MAPS}/map_route_v2_r2.py")
VR = _load("rp_verify_realms", f"{MAPS}/verify_realms_1327.py")
NE = V1.NE
GAZ = json.load(open(V1.GAZ))["places"]
R_KM = V1.R_EARTH

def proj_string(c):
    return f"+proj=laea +lat_0={c[1]} +lon_0={c[0]} +x_0=0 +y_0=0 +R={int(R_KM*1000)} +units=m +no_defs"

class Frame:
    """A frame = engine MapGeom (spherical LAEA centred on the frame centre, north up) at a given pixel size."""
    def __init__(s, name, center, width_km, W, H):
        s.name, s.center, s.width_km, s.W, s.H = name, list(center), float(width_km), W, H
        s.geom = V1.MapGeom({"map": {"center_lonlat": s.center, "width_km": s.width_km}}, W, H)
        s.height_km = H * s.geom.km_per_px
    def px(s, lon, lat): return s.geom.px(lon, lat)
    def inv(s, x, y):
        g = s.geom; return MM.inverse_laea(g.proj, g.x0 + np.asarray(x, float) / g.sc, g.y1 - np.asarray(y, float) / g.sc)
    def proj_bounds_m(s):
        hw, hh = s.width_km / 2, s.height_km / 2
        return dict(xmin=-hw * 1000, xmax=hw * 1000, ymin=-hh * 1000, ymax=hh * 1000)
    def lonlat_bounds(s):
        t = np.linspace(0, 1, 401); W, H = s.W, s.H
        xs = np.concatenate([t * W, t * W, np.zeros_like(t), np.full_like(t, W)])
        ys = np.concatenate([np.zeros_like(t), np.full_like(t, H), t * H, t * H])
        lo, la = s.inv(xs, ys)
        corners = {k: [round(float(v), 4) for v in s.inv(*xy)] for k, xy in
                   dict(top_left=(0, 0), top_right=(W, 0), bottom_left=(0, H), bottom_right=(W, H)).items()}
        return dict(lon_min=round(float(lo.min()), 4), lon_max=round(float(lo.max()), 4),
                    lat_min=round(float(la.min()), 4), lat_max=round(float(la.max()), 4), corners=corners,
                    note="envelope of the frame edge; the frame is a rectangle in LAEA metres, so meridians/parallels are curved inside it")

# ------------------------------------------------------------------------------------------ authority-driven stops
ROWS = V1.read_places_md()
LABEL_TEXT = {r: (v["onscreen"].split(":", 1)[1].split(",")[0].strip() if ":" in v["onscreen"] else None) for r, v in ROWS.items()}
# Region (OMIT) rows: label-only.  label_lonlat chosen INSIDE the region on land (not a pin, never drawn as a dot).
REGION_LABEL_LL = {"1-02": (-3.55, 51.62), "2-02": (-3.55, 51.62), "2-06": (-7.6, 53.15), "2-13": (4.75, 50.75)}

def stop_set(kind):
    """kind: 'britain' (Map 1 + Map 2a) or 'euro' (whole route: Map 2 + the Map 1 long-form stations)."""
    m1 = ["1-01", "1-02", "1-03", "1-04", "1-05", "1-06", "1-07", "1-08", "1-09", "1-10", "1-11", "1-12"]
    m2a = ["2-01", "2-02", "2-03", "2-04", "2-05", "2-06", "2-07"]
    m2b = ["2-08", "2-09", "2-10", "2-11", "2-12", "2-13", "2-14", "2-15"]
    return dict(map1=m1, map2=m2a + (m2b if kind == "euro" else []))

def authority_cfg(kind):
    """Build an engine-schema cfg (chains of {row,qid,label,pin}) from MAP-PLACES-v1 itself and run the engine check."""
    chains = []
    for cid, rows in stop_set(kind).items():
        stops = []
        for r in rows:
            v = ROWS[r]; pin = v["status"].startswith("VERIFIED"); lab = LABEL_TEXT.get(r)
            st = dict(row=r, qid=v["qid"], pin=pin)
            if lab: st["label"] = lab
            stops.append(st)
        chains.append(dict(id=cid, stops=stops))
    return dict(chains=chains)

def refusal_tests(cfg):
    """Same probes as atlas/proof_atlas_p0.refusal (UNCERTAIN 2-16 and an unlisted row must be refused), in memory,
    plus: a label on a region row that allows no text (2-09 Normandy) must be refused."""
    out = []
    for row, qid, why in (("2-16", None, "UNCERTAIN hermitage pinned"), ("9-99", "Q90", "unlisted row"), ("2-09", "Q15878", "text on a no-text region")):
        c2 = copy.deepcopy(cfg); q = qid or ROWS[row]["qid"]; ch = c2["chains"][-1]["stops"]
        hit = [s for s in ch if s["row"] == row]
        if hit: hit[0]["label"] = "Normandy"
        else: ch.append({"row": row, "qid": q, "label": "X"}); ch.sort(key=lambda s: s["row"])
        try: V1.check_against_authority(c2, ROWS); out.append(dict(test=why, refused=False))
        except Exception as e: out.append(dict(test=why, row=row, refused=True, error=str(e)[:160]))
    return out

def stops_for(kind):
    """pins (VERIFIED rows, dot + name) and regions (OMIT rows with allowed text, name only) with lon/lat."""
    cfg = authority_cfg(kind); log = V1.check_against_authority(cfg, ROWS)
    pins, regions, seen = [], [], set()
    for ch in cfg["chains"]:
        for st in ch["stops"]:
            key = (st["qid"], st.get("label"))
            if key in seen: continue
            seen.add(key)
            if st["pin"]:
                g = V1.wikidata_p625(st["qid"])
                pins.append(dict(row=st["row"], qid=st["qid"], name=st["label"], lon=g["lon"], lat=g["lat"], chain=ch["id"]))
            elif st.get("label"):
                lo, la = REGION_LABEL_LL[st["row"]]
                regions.append(dict(row=st["row"], qid=st["qid"], name=st["label"], lon=lo, lat=la, chain=ch["id"],
                                    note="label-only region (MAP-PLACES OMIT): no dot; label_lonlat is a layout point, not a location"))
    return pins, regions, log

# ------------------------------------------------------------------------------------------ realms (display groups)
REALM_GROUPS = [  # display group -> geojson ids; label text (reference image only; never on the final plate)
    ("england", ["england"], "KINGDOM OF ENGLAND"),
    ("gascony", ["gascony"], "GASCONY (ENGLISH)"),
    ("ireland_eng", ["ireland_eng"], "LORDSHIP OF IRELAND"),
    ("scotland", ["scotland"], "KINGDOM OF SCOTLAND"),
    ("france", ["france", "france_lyon"], "KINGDOM OF FRANCE"),
    ("brittany", ["brittany"], "DUCHY OF BRITTANY"),
    ("burgundy_duchy", ["burgundy_duchy"], "DUCHY OF BURGUNDY"),
    ("flanders", ["flanders"], "FLANDERS"),
    ("navarre", ["navarre"], "NAVARRE"),
    ("empire", ["empire_low", "empire_arles", "empire_provence"], "HOLY ROMAN EMPIRE"),
    ("castile", ["castile"], "CASTILE"),
    ("aragon", ["aragon"], "ARAGON"),
    ("portugal", ["portugal"], "PORTUGAL"),
]
# flat reference tints (variant 'tinted' only): the plate's intended pigment families, light
REALM_TINT = {"england": (214, 150, 150), "gascony": (226, 176, 172), "ireland_eng": (232, 196, 192), "scotland": (196, 178, 214),
              "france": (158, 178, 222), "brittany": (186, 200, 228), "burgundy_duchy": (178, 196, 232), "flanders": (180, 196, 200),
              "navarre": (196, 200, 226), "empire": (226, 206, 140), "castile": (214, 182, 176), "aragon": (232, 204, 156), "portugal": (182, 210, 192)}
NEUTRAL_LABELS = [("GAELIC IRELAND", (-8.6, 53.9)), ("LOMBARDY", (9.6, 45.2))]   # neutral (R05 / R20-R21), reference only

def realm_index(F, land, coast_snap_km=10.0):
    """Exclusive realm raster from the geodata in the frame's projection.  Priority = the geojson's own 'priority' list
    (first wins).  Land pixels within coast_snap_km of a realm but outside every polygon (NE coast vs simplified
    polygon mismatch) take the nearest realm; anything further stays neutral (Gaelic Ireland, Italy, etc.)."""
    d, feats = MM.load_realms(); masks = MM.realm_masks(F.geom, feats, ss=2)
    gid = {fid: gi + 1 for gi, (g, ids, _) in enumerate(REALM_GROUPS) for fid in ids}
    idx = np.zeros((F.H, F.W), np.int32)
    for fid in reversed(d["priority"]):
        if fid in masks and fid in gid: idx[masks[fid] > 0.5] = gid[fid]
    lb = land > 0.5; idx[~lb] = 0
    from scipy.ndimage import distance_transform_edt
    dist, (iy, ix) = distance_transform_edt(idx == 0, return_indices=True)
    fill = lb & (idx == 0) & (dist * F.geom.km_per_px <= coast_snap_km)
    idx[fill] = idx[iy[fill], ix[fill]]
    return idx

# neutral land a realm edge may be drawn against (REALMS-1327 NEUTRAL rows that are real 1327 edges):
# Gaelic Ireland (R05) and north Italy below the Alps (R20/R21).  Any other realm->neutral edge is the END OF THE DATA
# (e.g. the 'Imperial rim' stops east of the Rhine-Alps band): no line is drawn there and tints fade out.
def neutral_edge_ok(lon, lat):
    ire = (lon > -11) & (lon < -5.3) & (lat > 51.3) & (lat < 55.5)
    ita = (lon > 6.6) & (lon < 13.5) & (lat < 46.25) & (lat > 43.5)
    return ire | ita

def borders_from_index(idx, land, F=None):
    """Realm boundary pixels on land: realm vs realm everywhere; realm vs neutral only where neutral_edge_ok.
    Returns (border_bool, dict(fade_ok=bool map of realm pixels that touch a data-extent edge))."""
    b = np.zeros(idx.shape, bool); lb = land > 0.5; H, W = idx.shape
    okmap = np.ones(idx.shape, bool)
    if F is not None:
        Y, X = np.mgrid[0:H, 0:W]; lo, la = F.inv(X + 0.5, Y + 0.5); okmap = neutral_edge_ok(lo, la)
    dedge = np.zeros(idx.shape, bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = idx[: H - dy, : W - dx]; c = idx[dy:, dx:]
        l2 = lb[: H - dy, : W - dx] & lb[dy:, dx:]
        e = (a != c) & l2
        neu = (a == 0) | (c == 0); ok = okmap[: H - dy, : W - dx]
        draw = e & (~neu | ok); data_end = e & neu & ~ok
        b[: H - dy, : W - dx] |= draw; b[dy:, dx:] |= draw
        dedge[: H - dy, : W - dx] |= data_end; dedge[dy:, dx:] |= data_end
    fade = cv2.dilate(dedge.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    return b, dict(fade_ok=fade & (idx > 0), data_edge_px=int(dedge.sum()))
