"""Bathory B03 (Upper Hungary / Vah valley) reference pack, one native 9:16 frame.
Adapted from atlas/refpack (make_framing / make_refs / make_regplan / refpack_lib), reused read-only by import.
Authority: standalones/bathory/v2/MAP-PLACES-bathory-v1.md (pins, anchors, rivers, realms).
Writes only NEW files in this folder (save()/open(...,'x') refuse to overwrite).  Scratch inputs in /tmp/bathory_scratch:
  etopo1_bathory.nc      ETOPO1 (NOAA, via ERDDAP etopo180) 45-52N 13-23E; the engine subset etopo1_eu.nc stops at 20E
  ne_10m_rivers_europe/  Natural Earth 10m rivers, Europe supplement (Vah, Hron, Nitra, Dyje...; NE10m core has no Vah)
  ohm_<rel>.json         OpenHistoricalMap (CC0) relations, 'out geom'
  wd/<Q>.json            Wikidata entity JSON (P625)
"""
import sys; sys.dont_write_bytecode = True
import os, json, math, hashlib, datetime
OUTDIR = os.path.dirname(os.path.abspath(__file__)); RP = "/workspace/posterity/engine-rnd/maps/atlas/refpack"
os.environ["REFPACK_OUT"] = OUTDIR; os.environ["REFPACK_TAG"] = "v1"
sys.path.insert(0, RP)
import numpy as np, cv2
from shapely.geometry import LineString, MultiLineString, Point, box, mapping, shape
from shapely.ops import polygonize, unary_union, nearest_points
from refpack_lib import *            # Frame, V1, MM, R2, proj_string
import make_refs as MR               # relief, compose, draw_text, text_width, save (-> OUTDIR/img_v1)
assert os.path.abspath(MR.IMG) == os.path.join(OUTDIR, "img_v1"), MR.IMG
SCR = "/tmp/bathory_scratch"
MM.ETOPO = f"{SCR}/etopo1_bathory.nc"
NE_EU = f"{SCR}/ne_10m_rivers_europe/ne_10m_rivers_europe"
NE_CORE = f"{V1.NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines"
NAME = "bathory_b03_9x16"; W, H = 1080, 1920
CENTER = (17.55, 49.5); WIDTH_KM = 200.0
FRAMING = os.path.join(OUTDIR, "framing_refpack_bathory_v1.json"); CPJ = os.path.join(OUTDIR, "control_points_refpack_bathory_v1.json")

def wd(q):
    e = list(json.load(open(f"{SCR}/wd/{q}.json"))["entities"].values())[0]; v = e["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]
    return dict(qid=q, lat=float(v["latitude"]), lon=float(v["longitude"]), wd_label_en=e["labels"].get("en", {}).get("value"),
                wd_label_hu=e["labels"].get("hu", {}).get("value"), wd_lastrevid=e["lastrevid"])
# MAP-PLACES-bathory-v1: text = its on-screen names; kind pin (story) / anchor (frame, label only if owner wants)
PLACES = [dict(key="csejte", text="Csejte", qid="Q612364", kind="pin", band="VERIFIED", mp_latlon=(48.7247, 17.7608), note="Csejte fortress (Cachtice Castle). The pin."),
          dict(key="csejte_manor", text=None, qid="Q337440", kind="pin_coarse", band="COARSE", mp_latlon=(48.7122, 17.7872), note="manor = village coordinate stand-in (no own Wikidata point); one 'Csejte' label only; castle/manor split is for the inset"),
          dict(key="bytca", text="Bytča", qid="Q1968071", kind="pin", band="VERIFIED", mp_latlon=(49.2200, 18.5592), note="Bytca Castle, Thurzo's seat (trial Jan 1611). Town Q27907 49.2228,18.5581"),
          dict(key="vienna", text="Vienna", qid="Q1741", kind="anchor", band="anchor", mp_latlon=(48.2083, 16.3725), note="west edge anchor; label only if owner wants"),
          dict(key="pozsony", text="Pozsony", qid="Q1780", kind="anchor", band="anchor", mp_latlon=(48.1517, 17.1093), note="never 'Bratislava'; label only if owner wants"),
          dict(key="vagujhely", text="Vágújhely", qid="Q376987", kind="anchor_optional", band="optional", mp_latlon=(48.7833, 17.8333), note="optional, unlabelled here"),
          dict(key="trencsen", text="Trencsén", qid="Q145002", kind="anchor_optional", band="optional", mp_latlon=(48.8942, 18.0406), note="optional, unlabelled here"),
          dict(key="zsolna", text="Zsolna", qid="Q25797", kind="anchor_optional", band="optional", mp_latlon=(49.2167, 18.7333), note="optional, unlabelled here")]
REF_LABEL_KEYS = ["csejte", "bytca", "pozsony", "vienna"]     # the brief's places; MAP-PLACES names; nothing else gets text

def load_rivers(bbox):
    out = {}
    for shp in (NE_CORE, NE_EU):
        recs = V1.read_dbf(shp + ".dbf")
        for i, parts in V1.read_shp(shp + ".shp", bbox):
            nm = MM._nm(recs[i].get("name", "")); nm = {"Donau": "Danube"}.get(nm, nm)
            if not nm: continue
            out.setdefault(nm, []).extend(LineString(p) for p in parts if len(p) > 1)
    return {k: MultiLineString(v) for k, v in out.items()}

def poly_from_ohm(rel):
    d = json.load(open(f"{SCR}/ohm_{rel}.json"))["elements"][0]
    ls = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]]) for m in d["members"] if m["type"] == "way" and m.get("geometry")]
    return unary_union(list(polygonize(unary_union(ls)))), d["tags"]

def fill(F, geom, ss=2):
    m = np.zeros((H * ss, W * ss), np.uint8)
    gs = getattr(geom, "geoms", [geom])
    for g in gs:
        for ring, val in [(g.exterior, 1)] + [(r, 0) for r in g.interiors]:
            xy = np.asarray(ring.coords); p = F.px(xy[:, 0], xy[:, 1])
            cv2.fillPoly(m, [np.int32(np.round(np.asarray(p, np.float64) * ss * 16))], val, cv2.LINE_8, shift=4)
    return cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)

def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()

def relief_local(elev, land, kmpp):
    """make_refs.relief tuned for 0.19 km/px and a 100-2600 m range (Western Carpathians, Tatras edge): stronger hillshade
    exaggeration, tone from 150 m, form lines at 500/1000/1500 m."""
    hs = MM.hillshade(elev, kmpp, zf=4.0)
    mt = MM.smoothstep(150.0, 1900.0, elev) * land
    dark = np.clip(0.34 * mt ** 0.8 - 0.75 * hs * MM.smoothstep(120.0, 500.0, elev), 0, 0.6) * land
    form = np.zeros_like(elev)
    for z, a in ((500.0, 0.22), (1000.0, 0.38), (1500.0, 0.5)):
        m = (elev > z).astype(np.uint8); e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(np.float32)
        form = np.maximum(form, cv2.GaussianBlur(e, (0, 0), 0.6) * a)
    return dark, form * land

def main():
    for p in (FRAMING, CPJ): assert not os.path.exists(p), f"refuse to overwrite {p}"
    F = Frame(NAME, CENTER, WIDTH_KM, W, H); g = F.geom; kmpp = g.km_per_px; bbox = g.lonlat_bbox()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET")
    # ---------------- places (Wikidata P625 live, cross-checked with MAP-PLACES)
    P = []
    for p in PLACES:
        w = wd(p["qid"]); x, y = F.px(w["lon"], w["lat"])
        d_km = V1.haversine(w["lon"], w["lat"], p["mp_latlon"][1], p["mp_latlon"][0]) if hasattr(V1, "haversine") else \
            6371 * math.acos(min(1, math.sin(math.radians(w["lat"])) * math.sin(math.radians(p["mp_latlon"][0])) + math.cos(math.radians(w["lat"])) * math.cos(math.radians(p["mp_latlon"][0])) * math.cos(math.radians(w["lon"] - p["mp_latlon"][1]))))
        P.append(dict(p, lon=w["lon"], lat=w["lat"], wikidata=w, map_places_delta_km=round(d_km, 3), xy=[float(x), float(y)]))
    PK = {p["key"]: p for p in P}
    # ---------------- layers
    land = V1.raster_polys(g, f"{V1.NE}/ne_10m_land/ne_10m_land.shp", bbox)
    lakes = V1.raster_polys(g, f"{V1.NE}/ne_10m_lakes/ne_10m_lakes.shp", bbox, filt=lambda r: V1._rank(r) <= 7)
    land = np.clip(land - lakes, 0, 1)
    rivers = load_rivers(bbox); MAJOR = {"Danube", "Váh"}
    def rv(names, wpx, shp):
        return V1.raster_lines(g, shp + ".shp", bbox, lambda r: {"Donau": "Danube"}.get(MM._nm(r.get("name", "")), MM._nm(r.get("name", ""))) in names
                               and r.get("featurecla", "").startswith("River"), lambda r: wpx)
    minor = sorted(set(rivers) - MAJOR)
    riv = np.maximum.reduce([rv(MAJOR, 3.0, NE_CORE), rv(MAJOR, 3.0, NE_EU), 0.75 * rv(set(minor), 1.6, NE_CORE), 0.75 * rv(set(minor), 1.6, NE_EU)])
    elev, _ = MM.elevation(g); dark, form = relief_local(elev, land, kmpp)
    # relief: at 0.19 km/px the engine's 2x exaggeration clip is fine; form lines at 1000/2000 m (Tatras edge, Fatra)
    L = dict(land=land, rivers=riv, elev=elev, dark=dark, form=form)
    base = MR.compose(F, L, None, None)
    # ---------------- realms (OHM, coarse) -> realm id mask only (never on the guide)
    REALMS = [("hungary", "Kingdom of Hungary (Royal Hungary) - union of OHM county relations", [2830015, 2830018, 2829775, 2829772, 2829771, 2829458, 2829427, 2829455, 2829043, 2829044], (37, 91, 157)),
              ("austria", "Archduchy of Austria - OHM 'Austrian Circle' 1565-1618 (Reichskreis, contains the archduchy)", [2830626], (180, 40, 40)),
              ("moravia", "Margraviate of Moravia (Bohemian Crown) - OHM Moravia 1182-1742", [2830504], (60, 160, 70)),
              ("bohemian_crown_other", "Lands of the Bohemian Crown minus Moravia (Silesian duchies) - OHM 1557-1635", [2830430], (200, 160, 40)),
              ("poland", "Crown of Poland, Krakow Voivodeship - OHM 1400-1773", [2696433], (140, 70, 170))]
    _lb = F.lonlat_bounds(); frame_box = box(_lb["lon_min"] - 0.05, _lb["lat_min"] - 0.05, _lb["lon_max"] + 0.05, _lb["lat_max"] + 0.05); polys = {}; tags = {}
    for key, desc, rels, col in REALMS:
        gs = []
        for r in rels:
            pg, t = poly_from_ohm(r); gs.append(pg); tags[r] = dict(name=t.get("name:en") or t.get("name"), start=t.get("start_date"), end=t.get("end_date"))
        polys[key] = unary_union(gs).intersection(frame_box)
    polys["bohemian_crown_other"] = polys["bohemian_crown_other"].difference(polys["moravia"])
    idx = np.zeros((H, W), np.uint8)
    for i, (key, *_r) in reversed(list(enumerate(REALMS))):    # first listed wins
        idx[fill(F, polys[key]) > 0.5] = i + 1
    otto, ot = poly_from_ohm(2860343); otto_in = otto.intersection(frame_box)
    otto_m = fill(F, otto_in) > 0.5 if not otto_in.is_empty else np.zeros((H, W), bool)
    idimg = np.full((H, W, 3), 128, np.uint8)
    legend = {"128,128,128": "unassigned land (no OHM polygon for 1610 here; do not tint)"}
    for i, (key, desc, rels, col) in enumerate(REALMS):
        idimg[idx == i + 1] = col; legend[",".join(map(str, col))] = f"{key}: {desc} [COARSE]"
    realm_stats = {key: dict(px=int((idx == i + 1).sum()), frac=round(float((idx == i + 1).mean()), 4)) for i, (key, *_r) in enumerate(REALMS)}
    realm_stats["unassigned"] = dict(px=int((idx == 0).sum()), frac=round(float((idx == 0).mean()), 4))
    pin_realm = {p["key"]: (REALMS[idx[int(p["xy"][1]), int(p["xy"][0])] - 1][0] if 0 <= p["xy"][0] < W and 0 <= p["xy"][1] < H and idx[int(p["xy"][1]), int(p["xy"][0])] else None) for p in P}
    # ---------------- labels (engine placer), only the four brief places
    tsafe = (int(0.05 * W), int(0.05 * H), int(0.95 * W), int(0.95 * H)); dot_r = 6.0; lpx = 34
    block = np.zeros((H, W), np.uint8)
    for p in P:
        if p["kind"].startswith("pin") or p["key"] in REF_LABEL_KEYS:
            cv2.circle(block, (int(round(p["xy"][0])), int(round(p["xy"][1]))), int(dot_r + 4), 1, -1)
    block |= (cv2.dilate((riv > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)) & (rv(MAJOR, 3.0, NE_EU) + rv(MAJOR, 3.0, NE_CORE) > 0.3).astype(np.uint8))
    LP = [PK[k] for k in REF_LABEL_KEYS]; labels = []
    for p in LP:
        best = R2.place_label(p["text"], p["xy"], dot_r, block, tsafe, lpx, ["E"] if p["key"] == "vienna" else [], H, W,
                              other_pins=[q["xy"] for q in LP if q is not p])
        if best is None or best[5] != 0:
            labels.append(dict(key=p["key"], text=p["text"], placed=False)); continue
        _, Lb, bb, sd, gap, hit = best; block[max(0, bb[1] - 4):bb[3] + 4, max(0, bb[0] - 4):bb[2] + 4] = 1
        labels.append(dict(key=p["key"], text=p["text"], placed=True, side=sd, bbox=[int(v) for v in bb], px=lpx, _L=Lb))
    def dots(img):
        im = img.copy()
        for p in LP + [PK["csejte_manor"]]:
            x, y = p["xy"]; r = dot_r if p["kind"] == "pin" else (4.0 if p["kind"] == "anchor" else 3.0)
            cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int((r + 2) * 16), (255, 255, 255), -1, cv2.LINE_AA, shift=4)
            cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int(r * 16), (40, 26, 22) if p["kind"] != "pin_coarse" else (120, 100, 90), -1, cv2.LINE_AA, shift=4)
        return im
    def texts(img):
        im = img.copy()
        for l in labels:
            if l["placed"]: l["_L"].draw(im)
        return im
    # ---------------- zones: medallion + ornament, calm = low relief, off the major rivers, clear of labels/pins
    occ = np.zeros((H, W), np.uint8)
    for l in labels:
        if l["placed"]: b = l["bbox"]; occ[max(0, b[1] - 20):b[3] + 20, max(0, b[0] - 20):b[2] + 20] = 1
    for p in P: cv2.circle(occ, (int(p["xy"][0]), int(p["xy"][1])), 40, 1, -1)
    majr = (rv(MAJOR, 3.0, NE_EU) + rv(MAJOR, 3.0, NE_CORE)) > 0.3
    m = int(0.05 * W); sm = int(0.22 * W); so = int(0.18 * W)
    def cands(s):
        xs = [m, (W - s) // 2, W - m - s]; ys = [m, int(H * 0.2), (H - s) // 2, int(H * 0.68), H - m - s]
        return [(x, y, x + s, y + s) for x in xs for y in ys]
    def score(r):
        x0, y0, x1, y1 = r
        if occ[y0:y1, x0:x1].any() or majr[y0:y1, x0:x1].any(): return None
        return round(1.0 - float(dark[y0:y1, x0:x1].mean()) * 3 - float((riv[y0:y1, x0:x1] > 0.3).mean()) * 20 - 0.15 * (y0 / H), 4)
    sc = sorted([(score(r), r) for r in cands(sm) if score(r) is not None], key=lambda t: -t[0]); med = sc[0][1]
    occ[med[1] - 10:med[3] + 10, med[0] - 10:med[2] + 10] = 1
    so_c = sorted([(score(r), r) for r in cands(so) if score(r) is not None], key=lambda t: -t[0]); orn = so_c[0][1]
    def ll(r):
        lo, la = F.inv([r[0], r[2], r[2], r[0]], [r[1], r[1], r[3], r[3]]); return [[round(float(a), 3), round(float(b), 3)] for a, b in zip(lo, la)]
    def where(r):
        cx, cy = (r[0] + r[2]) / 2 / W, (r[1] + r[3]) / 2 / H
        return ("upper" if cy < 0.34 else "lower" if cy > 0.66 else "middle") + "-" + ("left" if cx < 0.34 else "right" if cx > 0.66 else "centre")
    Z = dict(medallion=dict(rect_px=list(map(int, med)), lonlat_corners=ll(med), calm_score=sc[0][0], position=where(med),
                            use="parking/hold position for the portrait medallion at wide zoom; the marker must never cover a label zone"),
             ornament_reserved=dict(rect_px=list(map(int, orn)), lonlat_corners=ll(orn), calm_score=so_c[0][0], position=where(orn),
                                    use="the ONLY place a small static compass rose may be painted"))
    # ---------------- images
    out = {}
    out["ref_notext"] = MR.save(base, f"{NAME}_ref_notext.png")              # THE plate guide: relief + rivers + lakes, no dots/text/borders
    full = texts(dots(base)); out["ref_labels"] = MR.save(full, f"{NAME}_ref_labels.png")
    gr = np.zeros((H, W), np.float32); gitems = []
    for lo in np.arange(15.0, 20.01, 0.5):
        la = np.linspace(46, 52, 400); p = F.px(np.full_like(la, lo), la)
        cv2.polylines(gr, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        k = np.argmin(np.abs(p[:, 1] - 30))
        if 20 < p[k, 0] < W - 60: gitems.append((f"{lo:g}°E", (float(p[k, 0]) + 2, 30.0), 17, "grat"))
    for la in np.arange(47.5, 51.51, 0.5):
        lo = np.linspace(14, 21, 400); p = F.px(lo, np.full_like(lo, la))
        cv2.polylines(gr, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        k = np.argmin(np.abs(p[:, 0] - 50))
        if 40 < p[k, 1] < H - 10: gitems.append((f"{la:g}°N", (50.0, float(p[k, 1]) - 12), 17, "grat"))
    gimg = full * (1 - 0.55 * gr[..., None]) + np.float32([60, 110, 170]) * 0.55 * gr[..., None]
    out["ref_graticule"] = MR.save(MR.draw_text(gimg, gitems), f"{NAME}_ref_graticule.png")
    zimg = full.copy()
    def rect(im, r, col, t=3): cv2.rectangle(im, (int(r[0]), int(r[1])), (int(r[2]), int(r[3])), col, t)
    rect(zimg, tsafe, (30, 140, 60), 2)
    pin_inset = (0.06, 0.05); ps = (int(pin_inset[0] * W), int(pin_inset[1] * H), int((1 - pin_inset[0]) * W), int((1 - pin_inset[1]) * H)); rect(zimg, ps, (200, 120, 0), 2)
    for l in labels:
        if l["placed"]: b = l["bbox"]; rect(zimg, [b[0] - 10, b[1] - 10, b[2] + 10, b[3] + 10], (60, 90, 200), 2)
    rect(zimg, med, (170, 30, 160), 4); rect(zimg, orn, (200, 60, 40), 4)
    out["zones_overlay"] = MR.save(zimg, f"{NAME}_zones_overlay.png")
    p_ = os.path.join(MR.IMG, f"{NAME}_realm_ids.png"); assert not os.path.exists(p_)
    from PIL import Image
    Image.fromarray(idimg).quantize(colors=8, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(p_, optimize=True); out["realm_ids"] = p_
    # ---------------- control points
    C = []
    def add(**k):
        x, y = F.px(k["lon"], k["lat"])
        if 0.05 * W <= x <= 0.95 * W and 0.05 * H <= y <= 0.95 * H: C.append(dict(k, px=[round(float(x), 1), round(float(y), 1)]))
    names = sorted(rivers); seen = set()
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pa, pb = nearest_points(rivers[a], rivers[b])
            if pa.distance(pb) < 0.03 and frame_box.contains(pa):
                add(type="confluence", name=f"{a}-{b}", lon=round(pa.x, 4), lat=round(pa.y, 4), source="NE10m (core + Europe supplement) centerlines, nearest approach < 3 km")
    vah = unary_union(rivers["Váh"]); vl = list(vah.geoms) if hasattr(vah, "geoms") else [vah]
    for ln in vl:                                            # Vah bends: turning > 45 deg on a 2.5 km-simplified line
        s = ln.simplify(0.025); c = np.asarray(s.coords)
        for j in range(1, len(c) - 1):
            v1, v2 = c[j] - c[j - 1], c[j + 1] - c[j]
            v1 = v1 * [math.cos(math.radians(c[j][1])), 1]; v2 = v2 * [math.cos(math.radians(c[j][1])), 1]
            ang = math.degrees(math.acos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12), -1, 1)))
            if ang > 35 and min(np.linalg.norm(v1), np.linalg.norm(v2)) * 111 > 3:
                add(type="river_bend", name=f"Váh bend {ang:.0f} deg", lon=round(float(c[j][0]), 4), lat=round(float(c[j][1]), 4), turn_deg=round(ang, 1),
                    source="NE10m Europe-supplement Vah centerline vertex (2.5 km simplification), turning angle > 35 deg")
    dan = unary_union(rivers["Danube"]); dl = list(dan.geoms) if hasattr(dan, "geoms") else [dan]
    for ln in dl:
        s = ln.simplify(0.02); c = np.asarray(s.coords)
        for j in range(1, len(c) - 1):
            v1, v2 = (c[j] - c[j - 1]) * [0.66, 1], (c[j + 1] - c[j]) * [0.66, 1]
            ang = math.degrees(math.acos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12), -1, 1)))
            if ang > 35: add(type="river_bend", name=f"Danube bend {ang:.0f} deg", lon=round(float(c[j][0]), 4), lat=round(float(c[j][1]), 4), turn_deg=round(ang, 1),
                             source="NE10m Danube centerline vertex (2 km simplification), turning angle > 35 deg")
    for rn in ("Morava", "Nitra", "Hron", "Oder", "Dyje"):
        if rn not in rivers: continue
        gg = unary_union(rivers[rn]); gl = list(gg.geoms) if hasattr(gg, "geoms") else [gg]
        for ln in gl:
            c = np.asarray(ln.simplify(0.025).coords)
            for j in range(1, len(c) - 1):
                v1, v2 = (c[j] - c[j - 1]) * [0.66, 1], (c[j + 1] - c[j]) * [0.66, 1]
                if min(np.linalg.norm(v1), np.linalg.norm(v2)) * 111 < 3: continue
                ang = math.degrees(math.acos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12), -1, 1)))
                if ang > 50: add(type="river_bend", name=f"{rn} bend {ang:.0f} deg", lon=round(float(c[j][0]), 4), lat=round(float(c[j][1]), 4), turn_deg=round(ang, 1),
                                 source=f"NE10m {rn} centerline vertex (2.5 km simplification), turning angle > 50 deg", weight="low (minor river)")
    pri = {"confluence": 0, "river_bend": 1}
    C.sort(key=lambda c: (pri[c["type"]], 0 if c["name"].startswith(("Váh", "Danube")) else 1, -c.get("turn_deg", 0))); 
    sel = []; min_sep = 0.045 * W
    for c in C:
        if all(math.dist(c["px"], s["px"]) >= min_sep for s in sel): sel.append(dict(c, role="primary"))
    for p in P:
        x, y = p["xy"]
        if 0 <= x < W and 0 <= y < H:
            sel.append(dict(type="settlement", name=p["text"] or "Csejte manor (village)", key=p["key"], qid=p["qid"], lon=p["lon"], lat=p["lat"],
                            px=[round(x, 1), round(y, 1)], role="secondary", band=p["band"], source="Wikidata P625 (live) = MAP-PLACES-bathory-v1"))
    for i, c in enumerate(sel):
        c["id"] = f"CP{i + 1:02d}"; c["plate_px"] = [round(2 * c["px"][0], 1), round(2 * c["px"][1], 1)]; c["search_px_out"] = 40 if c["type"] != "settlement" else 60
    # ---------------- JSON
    TH = dict(pass_px=4, flag_px=8, pass_km=round(4 * kmpp, 2), flag_km=round(8 * kmpp, 2))
    checks = []
    for p in P:
        x, y = p["xy"]; lab = next((l for l in labels if l["key"] == p["key"]), None)
        checks.append(dict(key=p["key"], text=p["text"], qid=p["qid"], kind=p["kind"], band=p["band"], lonlat=[round(p["lon"], 5), round(p["lat"], 5)],
                           map_places_latlon=list(p["mp_latlon"]), map_places_delta_km=p["map_places_delta_km"], px=[round(x, 1), round(y, 1)],
                           in_frame=bool(0 <= x < W and 0 <= y < H), in_pin_safe=bool(ps[0] <= x <= ps[2] and ps[1] <= y <= ps[3]),
                           in_title_safe=bool(tsafe[0] <= x <= tsafe[2] and tsafe[1] <= y <= tsafe[3]), realm=pin_realm[p["key"]],
                           ref_label=(dict(text=lab["text"], bbox=lab.get("bbox"), side=lab.get("side")) if lab and lab["placed"] else None), note=p["note"]))
    pb = F.proj_bounds_m()
    J = dict(name="framing_refpack_bathory_v1", created=now, authority="standalones/bathory/v2/MAP-PLACES-bathory-v1.md (Archivist 2026-10-31 ~11:55 ET)",
             projection=dict(name="Lambert azimuthal equal-area, spherical (engine map_route_v1.LAEA), centred on the frame centre, north up", sphere_radius_m=int(R_KM * 1000),
                             note="engine LAEA (forward map_route_v1.LAEA, inverse map_modes_v2.inverse_laea); proj4 is the exact equivalent (+R sphere). x_px = (X_m - xmin)/m_per_px, y_px = (ymax - Y_m)/m_per_px."),
             frames={NAME: dict(aspect="9:16", size_px=[W, H], use="B03 Upper Hungary / Vah valley map beat",
                 justification="Width set by the MAP-PLACES suggested span (16.3-19.0E): Vienna near the west edge, Bytca/Zsolna inside the east pin-safe band. "
                               "The south edge is held just north of the Danube's Komarom-Esztergom reach (about 47.85-47.9N) so the Ottoman-held Esztergom/Parkany "
                               "bend stays out of frame (MAP-PLACES: frontier out of frame). Native 9:16 then needs ~356 km of height, which goes NORTH (White Carpathians, "
                               "Javorniky, Beskids, Moravian gate, upper Oder): calm ground for the medallion and label margins.",
                 center_lonlat=list(CENTER), width_km=WIDTH_KM, height_km=round(F.height_km, 2), m_per_px=round(kmpp * 1000, 3), km_per_px=round(kmpp, 5),
                 proj4=proj_string(CENTER), projected_bounds_m={k: round(v, 1) for k, v in pb.items()}, lonlat_bounds=F.lonlat_bounds(),
                 pin_inset=list(pin_inset), pin_safe_px=list(ps), title_safe_px=list(tsafe),
                 safe_area_check=dict(all_story_pins_in_pin_safe=all(c["in_pin_safe"] for c in checks if c["kind"].startswith("pin")), places=checks),
                 label_zones=[dict(key=l["key"], text=l["text"], rect_px=l["bbox"], pad_px=10) for l in labels if l["placed"]],
                 labels_not_placed=[l["text"] for l in labels if not l["placed"]],
                 label_zone_rule="keep these rects (+10 px) low-detail on the plate: no settlement vignette, no dense forest/hatching under a label",
                 label_text_rule="MAP-PLACES names only (Csejte, Bytca, Pozsony, Vienna). Vienna/Pozsony are frame anchors: on-screen only if the owner wants. No river, range, realm, date or status text.",
                 zones=Z,
                 realms=dict(status="COARSE - reference masks for engine pigment only, never painted from the reference; never shown as borders on the guide",
                             source="OpenHistoricalMap (CC0), relations fetched 2026-10-31 via overpass-api.openhistoricalmap.org; 'Kingdom of Hungary' rel 2750054 has no geometry, so Hungary = union of its county relations (dated 1050/1350-1850, i.e. not 1610-specific)",
                             ohm_relations={str(k): v for k, v in tags.items()}, coverage=realm_stats, legend=legend,
                             ottoman_conflict=dict(ohm_relation=2860343, ohm_dates=f"{ot.get('start_date')}..{ot.get('end_date')}",
                                                   px_in_frame=int(otto_m.sum()), bounds_in_frame=[round(v, 3) for v in otto_in.bounds] if not otto_in.is_empty else None,
                                                   note="OHM's single 1540-1669 Ottoman polygon reaches into this frame (SE). It is a whole-period envelope, not 1610; MAP-PLACES puts the 1610 frontier out of frame, so it is NOT masked or tinted. Flagged to the Archivist.")),
                 renderer=dict(map=dict(center_lonlat=list(CENTER), width_km=WIDTH_KM), out_wh=[W, H], plate_wh=[2 * W, 2 * H], px_scale_out_to_plate=2.0),
                 sources=dict(land="Natural Earth 10m land + lakes (engine sources/naturalearth)", rivers="NE10m rivers_lake_centerlines (Danube, Morava, Oder, Vistula) + NE10m rivers_europe supplement (Vah, Hron, Nitra, Dyje...) - downloaded to scratch, naciscdn.org",
                              relief="ETOPO1 1-arc-min (NOAA NCEI) via coastwatch.pfeg.noaa.gov ERDDAP etopo180, 45-52N 13-23E (engine subset etopo1_eu.nc ends at 20E)",
                              places="Wikidata P625 live 2026-10-31 (entity JSON), equal to MAP-PLACES-bathory-v1"),
                 files={k: os.path.relpath(v, OUTDIR) for k, v in out.items()})})
    json.dump(J, open(FRAMING, "x"), indent=1, ensure_ascii=False, default=lambda o: None)
    CP = dict(name="control_points_refpack_bathory_v1", px_space="out px of the frame (plate px = 2x, also given)", frame=NAME,
              thresholds=dict(pass_px=TH["pass_px"], flag_px=TH["flag_px"], pass_km=TH["pass_km"], flag_km=TH["flag_km"],
                              scaled_from="Edward refpack v2 britain row (<=4/8 px, 1.6/3.0 km at 0.37-0.65 km/px): same px gates, km = px x this frame's km/px"),
              warp_limit_frac_of_min_side=0.025, control_points=sel)
    json.dump(CP, open(CPJ, "x"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(kmpp=kmpp, H_km=F.height_km, bounds=F.lonlat_bounds(), labels=[(l["text"], l["placed"], l.get("side")) for l in labels],
                          zones={k: (v["rect_px"], v["position"]) for k, v in Z.items()}, n_cp=len(sel), n_primary=sum(c["role"] == "primary" for c in sel),
                          realm=realm_stats, pin_realm=pin_realm, otto_px=int(otto_m.sum()), checks=[(c["key"], c["px"], c["in_pin_safe"], c["map_places_delta_km"]) for c in checks]), ensure_ascii=False, indent=0))

if __name__ == "__main__":
    main()
