"""Bathory B03 reference pack v2 - option (b) (Vellum, 2026-10-31 ~12:06 ET): tight on the Vah corridor, Upper Hungary fills
the frame, Vienna dropped, Pozsony only if it fits (it does not). Native 9:16, spherical LAEA. v1 files are left untouched.
Authority: standalones/bathory/v2/MAP-PLACES-bathory-v1.md (1610 names).  Reuses atlas/refpack/refpack_lib + make_refs read-only.
Scratch inputs (/tmp/bathory_scratch):
  etopo2022_15s_bathory.nc  ETOPO 2022 v1 15-arcsec (NOAA NCEI) via ERDDAP ETOPO_2022_v1_15s, 47.6-49.8N 17.0-19.5E
  osm_rivers_v2.json         OSM (ODbL) way[waterway=river][name] 47.95-49.65N 17.3-19.1E via Overpass (private.coffee mirror)
  osm_vah_rel.json           OSM (ODbL) relation 3509398 (Vah, waterway) out geom, main_stream members = the spine
  ohm_<rel>.json, wd/<Q>.json   as v1
Every output path is asserted to be inside this folder; every write refuses to overwrite.
"""
import sys; sys.dont_write_bytecode = True
import os, json, math, hashlib, datetime
OUTDIR = os.path.dirname(os.path.abspath(__file__)); RP = "/workspace/posterity/engine-rnd/maps/atlas/refpack"
os.environ["REFPACK_OUT"] = OUTDIR; os.environ["REFPACK_TAG"] = "v2"
sys.path.insert(0, RP)
import numpy as np, cv2
from PIL import Image
from scipy.io import netcdf_file
from shapely.geometry import LineString, MultiLineString, Point, box
from shapely.ops import polygonize, unary_union, nearest_points, linemerge
from refpack_lib import *
import make_refs as MR
IMG = os.path.join(OUTDIR, "img_v2"); assert os.path.abspath(MR.IMG) == IMG, MR.IMG
SCR = "/tmp/bathory_scratch"
NAME = "bathory_b03v2_9x16"; W, H = 1080, 1920
CENTER = (18.20, 48.80); WIDTH_KM = 85.0          # chosen by grid scan (see README_v2): max Hungary share, Ottoman 0, Bytca clear of the medallion
FRAMING = os.path.join(OUTDIR, "framing_refpack_bathory_v2.json"); CPJ = os.path.join(OUTDIR, "control_points_refpack_bathory_v2.json")
def inside(p):
    p = os.path.abspath(p); assert p.startswith(OUTDIR + os.sep), f"path escapes pack: {p}"; assert not os.path.exists(p), f"refuse to overwrite {p}"; return p
def save(img, name, quant=False):
    p = inside(os.path.join(IMG, name)); im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if quant and im.mode == "RGB": im = im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)  # disk: overlays only
    im.save(p, optimize=True); return p

def wd(q):
    e = list(json.load(open(f"{SCR}/wd/{q}.json"))["entities"].values())[0]; v = e["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]
    return dict(qid=q, lat=float(v["latitude"]), lon=float(v["longitude"]), wd_label_en=e["labels"].get("en", {}).get("value"),
                wd_label_hu=e["labels"].get("hu", {}).get("value"), wd_lastrevid=e["lastrevid"])
PLACES = [dict(key="csejte", text="Csejte", qid="Q612364", kind="pin", band="VERIFIED", mp_latlon=(48.7247, 17.7608), note="Csejte fortress (Cachtice Castle). The pin."),
          dict(key="csejte_manor", text=None, qid="Q337440", kind="pin_coarse", band="COARSE", mp_latlon=(48.7122, 17.7872), note="manor = village coordinate stand-in; one 'Csejte' label only; split is for the inset"),
          dict(key="bytca", text="Bytča", qid="Q1968071", kind="pin", band="VERIFIED", mp_latlon=(49.2200, 18.5592), note="Bytca Castle (Thurzo). Town Q27907 49.2228,18.5581"),
          dict(key="pozsony", text="Pozsony", qid="Q1780", kind="anchor", band="anchor", mp_latlon=(48.1517, 17.1093), note="labelled only if it fits naturally (Vellum); never 'Bratislava'"),
          dict(key="vagujhely", text="Vágújhely", qid="Q376987", kind="anchor_optional", band="optional", mp_latlon=(48.7833, 17.8333), note="optional, unlabelled"),
          dict(key="trencsen", text="Trencsén", qid="Q145002", kind="anchor_optional", band="optional", mp_latlon=(48.8942, 18.0406), note="optional, unlabelled"),
          dict(key="zsolna", text="Zsolna", qid="Q25797", kind="anchor_optional", band="optional", mp_latlon=(49.2167, 18.7333), note="optional, unlabelled")]
# Vienna (Q1741) dropped per option (b).

def hav(lat1, lon1, lat2, lon2):
    a, b, c, d = map(math.radians, (lat1, lon1, lat2, lon2))
    return 6371 * 2 * math.asin(math.sqrt(math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2))

def osm_rivers():
    d = json.load(open(f"{SCR}/osm_rivers_v2.json"))["elements"]; out = {}
    for e in d:
        nm = e["tags"].get("name"); g = e.get("geometry")
        if nm and g and len(g) > 1: out.setdefault(nm, []).append(LineString([(p["lon"], p["lat"]) for p in g]))
    out = {k: linemerge(MultiLineString(v)) for k, v in out.items()}
    # Vah spine: OSM waterway relation 3509398 (Q202598) main_stream members - the plain name match leaves a gap at the
    # Slnava reservoir / Piestany reach, so the spine comes from the relation instead.
    rel = [r for r in json.load(open(f"{SCR}/osm_vah_rel.json"))["elements"] if r["id"] == 3509398][0]
    vl = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]]) for m in rel["members"] if m.get("role") == "main_stream" and m.get("geometry")]
    out["Váh"] = linemerge(MultiLineString(vl)); return out

def lines_raster(F, geoms, wpx, ss=4):
    m = np.zeros((H * ss, W * ss), np.uint8); th = max(1, int(round(wpx * ss)))
    for gm in geoms:
        for ln in getattr(gm, "geoms", [gm]):
            c = np.asarray(ln.coords); cv2.polylines(m, [np.int32(np.round(F.px(c[:, 0], c[:, 1]) * ss * 16))], False, 255, th, cv2.LINE_AA, shift=4)
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

def elevation(F):
    f = netcdf_file(f"{SCR}/etopo2022_15s_bathory.nc", "r", mmap=False)
    z = np.array(f.variables["z"].data, np.float32); lat = np.array(f.variables["latitude"].data, np.float64); lon = np.array(f.variables["longitude"].data, np.float64); f.close()
    xs, ys = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5); LO, LA = F.inv(xs.ravel(), ys.ravel()); LO = np.asarray(LO).reshape(H, W); LA = np.asarray(LA).reshape(H, W)
    mx = ((LO - lon[0]) / (lon[1] - lon[0])).astype(np.float32); my = ((LA - lat[0]) / (lat[1] - lat[0])).astype(np.float32)
    assert mx.min() > 2 and my.min() > 2 and mx.max() < len(lon) - 3 and my.max() < len(lat) - 3, "DEM subset too small"
    return cv2.GaussianBlur(cv2.remap(z, mx, my, cv2.INTER_CUBIC), (0, 0), 1.0)

def relief(elev, land, kmpp):
    """v1 relief_local retuned for 0.079 km/px and a 100-1700 m range: tone from 150 m, form lines 400/700/1000/1300 m."""
    hs = MM.hillshade(elev, kmpp, zf=2.2)
    mt = MM.smoothstep(150.0, 1500.0, elev) * land
    dark = np.clip(0.30 * mt ** 0.8 - 0.75 * hs * MM.smoothstep(120.0, 450.0, elev), 0, 0.6) * land
    form = np.zeros_like(elev)
    for zz, a in ((400.0, 0.16), (700.0, 0.26), (1000.0, 0.36), (1300.0, 0.46)):
        m = (elev > zz).astype(np.uint8); e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(np.float32)
        form = np.maximum(form, cv2.GaussianBlur(e, (0, 0), 0.6) * a)
    return dark, form * land

def poly_from_ohm(rel):
    d = json.load(open(f"{SCR}/ohm_{rel}.json"))["elements"][0]
    ls = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]]) for m in d["members"] if m["type"] == "way" and m.get("geometry")]
    return unary_union(list(polygonize(unary_union(ls)))), d["tags"]

def fill(F, geom, ss=2):
    m = np.zeros((H * ss, W * ss), np.uint8)
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty or g.geom_type != "Polygon": continue
        for ring, val in [(g.exterior, 1)] + [(r, 0) for r in g.interiors]:
            xy = np.asarray(ring.coords); p = F.px(xy[:, 0], xy[:, 1])
            cv2.fillPoly(m, [np.int32(np.round(p * ss * 16))], val, cv2.LINE_8, shift=4)
    return cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_AREA)

def main():
    for p in (FRAMING, CPJ): inside(p)
    F = Frame(NAME, CENTER, WIDTH_KM, W, H); g = F.geom; kmpp = g.km_per_px; LB = F.lonlat_bounds()
    frame_box = box(LB["lon_min"] - 0.03, LB["lat_min"] - 0.03, LB["lon_max"] + 0.03, LB["lat_max"] + 0.03)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET")
    P = []
    for p in PLACES:
        w = wd(p["qid"]); x, y = F.px(w["lon"], w["lat"])
        P.append(dict(p, lon=w["lon"], lat=w["lat"], wikidata=w, map_places_delta_km=round(hav(w["lat"], w["lon"], *p["mp_latlon"]), 3), xy=[float(x), float(y)]))
    PK = {p["key"]: p for p in P}
    inf = lambda p: 0 <= p["xy"][0] < W and 0 <= p["xy"][1] < H
    # layers
    bbox = (LB["lon_min"] - 0.3, LB["lat_min"] - 0.3, LB["lon_max"] + 0.3, LB["lat_max"] + 0.3)
    land = V1.raster_polys(g, f"{V1.NE}/ne_10m_land/ne_10m_land.shp", bbox)
    R = {k: v.intersection(frame_box.buffer(0.1)) for k, v in osm_rivers().items()}
    R = {k: v for k, v in R.items() if not v.is_empty}
    rlen = {k: v.length * 111 * 0.8 for k, v in R.items()}
    MAJOR = ["Váh"]; minor = [k for k in R if k not in MAJOR and rlen[k] >= 12]
    vah_r = lines_raster(F, [R["Váh"]], 3.2); minr = lines_raster(F, [R[k] for k in minor], 1.5)
    riv = np.maximum(vah_r, 0.75 * minr)
    elev = elevation(F); dark, form = relief(elev, land, kmpp)
    base = MR.compose(F, dict(land=land, rivers=riv, elev=elev, dark=dark, form=form), None, None)
    # Vah continuity: which frame edges it crosses
    vah_in = R["Váh"].intersection(F_poly := box(*[float(v) for v in (LB["lon_min"], LB["lat_min"], LB["lon_max"], LB["lat_max"])]))
    vpx = np.concatenate([F.px(*np.asarray(l.coords).T) for l in getattr(R["Váh"], "geoms", [R["Váh"]])])
    vin = vpx[(vpx[:, 0] >= 0) & (vpx[:, 0] < W) & (vpx[:, 1] >= 0) & (vpx[:, 1] < H)]
    vah_stats = dict(px_inside=int((vah_r > 0.3).sum()), x_range=[round(float(vin[:, 0].min())), round(float(vin[:, 0].max()))], y_range=[round(float(vin[:, 1].min())), round(float(vin[:, 1].max()))])
    # realms (coarse OHM)
    REALMS = [("hungary", "Kingdom of Hungary (Royal Hungary) - union of OHM county relations", [2830015, 2830018, 2829775, 2829772, 2829771, 2829458, 2829427, 2829455, 2829043, 2829044], (37, 91, 157)),
              ("austria", "Archduchy of Austria - OHM Austrian Circle 1565-1618", [2830626], (180, 40, 40)),
              ("moravia", "Margraviate of Moravia - OHM 1182-1742", [2830504], (60, 160, 70)),
              ("bohemian_crown_other", "Lands of the Bohemian Crown minus Moravia (Silesia) - OHM 1557-1635", [2830430], (200, 160, 40)),
              ("poland", "Crown of Poland, Krakow Voivodeship - OHM 1400-1773", [2696433], (140, 70, 170))]
    polys = {}; tags = {}
    for key, desc, rels, col in REALMS:
        gs = []
        for r in rels:
            pg, t = poly_from_ohm(r); gs.append(pg); tags[r] = dict(name=t.get("name:en") or t.get("name"), start=t.get("start_date"), end=t.get("end_date"))
        polys[key] = unary_union(gs).intersection(frame_box)
    polys["bohemian_crown_other"] = polys["bohemian_crown_other"].difference(polys["moravia"])
    idx = np.zeros((H, W), np.uint8)
    for i, (key, *_r) in reversed(list(enumerate(REALMS))): idx[fill(F, polys[key]) > 0.5] = i + 1
    otto, ot = poly_from_ohm(2860343); otto_in = otto.intersection(frame_box)
    otto_px = int((fill(F, otto_in) > 0.5).sum()) if not otto_in.is_empty else 0
    idimg = np.full((H, W, 3), 128, np.uint8); legend = {"128,128,128": "unassigned (no OHM polygon; do not tint)"}
    for i, (key, desc, rels, col) in enumerate(REALMS): idimg[idx == i + 1] = col; legend[",".join(map(str, col))] = f"{key}: {desc} [COARSE]"
    shares = {key: round(100 * float((idx == i + 1).mean()), 2) for i, (key, *_r) in enumerate(REALMS)}; shares["unassigned"] = round(100 * float((idx == 0).mean()), 2)
    shares["ottoman_ohm_envelope_overlap"] = round(100 * otto_px / (W * H), 2)
    # moravia wedge extent along the edges
    mor = idx == 3; mor_edge = dict(top_px=int(mor[0].sum()), left_px=int(mor[:, 0].sum()), max_depth_from_left_px=int(max((np.argmax(~r) if r[0] else 0) for r in mor)))
    def realm_at(p):
        if not inf(p): return None
        v = idx[int(p["xy"][1]), int(p["xy"][0])]; return REALMS[v - 1][0] if v else None
    # labels: Csejte, Bytca; Pozsony only if inside the title-safe frame
    tsafe = (int(0.05 * W), int(0.05 * H), int(0.95 * W), int(0.95 * H)); dot_r = 7.0; lpx = 40
    pin_inset = (0.06, 0.05); ps = (int(pin_inset[0] * W), int(pin_inset[1] * H), int((1 - pin_inset[0]) * W), int((1 - pin_inset[1]) * H))
    m = int(0.05 * W); sm = int(0.22 * W); so = int(0.18 * W)
    med = (W - m - sm, m, W - m, m + sm)                              # medallion fixed upper-right (Vellum)
    LP = [PK["csejte"], PK["bytca"]] + ([PK["pozsony"]] if (tsafe[0] + 40 <= PK["pozsony"]["xy"][0] <= tsafe[2] - 40 and tsafe[1] <= PK["pozsony"]["xy"][1] <= tsafe[3]) else [])
    block = np.zeros((H, W), np.uint8)
    for p in P:
        if inf(p): cv2.circle(block, (int(round(p["xy"][0])), int(round(p["xy"][1]))), int(dot_r + 4), 1, -1)
    block |= cv2.dilate((vah_r > 0.3).astype(np.uint8), np.ones((7, 7), np.uint8))
    block[med[1] - 12:med[3] + 12, med[0] - 12:med[2] + 12] = 1
    labels = []
    for p in LP:
        best = R2.place_label(p["text"], p["xy"], dot_r, block, tsafe, lpx, ["W"] if p["key"] == "csejte" else [], H, W, other_pins=[q["xy"] for q in LP if q is not p])
        if best is None or best[5] != 0: labels.append(dict(key=p["key"], text=p["text"], placed=False)); continue
        _, Lb, bb, sd, gap, hit = best; block[max(0, bb[1] - 4):bb[3] + 4, max(0, bb[0] - 4):bb[2] + 4] = 1
        labels.append(dict(key=p["key"], text=p["text"], placed=True, side=sd, bbox=[int(v) for v in bb], px=lpx, _L=Lb))
    # compass zone: calm candidate, clear of medallion, labels, pins and the Vah
    occ = np.zeros((H, W), np.uint8)
    for l in labels:
        if l["placed"]: b = l["bbox"]; occ[max(0, b[1] - 20):b[3] + 20, max(0, b[0] - 20):b[2] + 20] = 1
    for p in P:
        if inf(p): cv2.circle(occ, (int(p["xy"][0]), int(p["xy"][1])), 40, 1, -1)
    occ[med[1] - 20:med[3] + 20, med[0] - 20:med[2] + 20] = 1; vb = vah_r > 0.3
    cands = [(x, y, x + so, y + so) for x in (m, (W - so) // 2, W - m - so) for y in (m, int(H * 0.2), (H - so) // 2, int(H * 0.68), H - m - so)]
    def score(r):
        x0, y0, x1, y1 = r
        if occ[y0:y1, x0:x1].any() or vb[y0:y1, x0:x1].any(): return None
        return round(1.0 - float(dark[y0:y1, x0:x1].mean()) * 3 - float((riv[y0:y1, x0:x1] > 0.3).mean()) * 20 - 0.1 * (y0 / H), 4)
    sc = sorted([(score(r), r) for r in cands if score(r) is not None], key=lambda t: -t[0]); orn = sc[0][1]
    def ll(r):
        lo, la = F.inv([r[0], r[2], r[2], r[0]], [r[1], r[1], r[3], r[3]]); return [[round(float(a), 3), round(float(b), 3)] for a, b in zip(lo, la)]
    def where(r):
        cx, cy = (r[0] + r[2]) / 2 / W, (r[1] + r[3]) / 2 / H
        return ("upper" if cy < 0.34 else "lower" if cy > 0.66 else "middle") + "-" + ("left" if cx < 0.34 else "right" if cx > 0.66 else "centre")
    Z = dict(medallion=dict(rect_px=list(map(int, med)), lonlat_corners=ll(med), position="upper-right", use="portrait medallion; never over a label zone"),
             ornament_reserved=dict(rect_px=list(map(int, orn)), lonlat_corners=ll(orn), calm_score=sc[0][0], position=where(orn), use="the ONLY place a small compass rose may be painted"))
    # images
    def dots(img):
        im = img.copy()
        for p in [PK["csejte"], PK["csejte_manor"], PK["bytca"]] + [q for q in LP if q["kind"] == "anchor"]:
            x, y = p["xy"]; r = dot_r if p["kind"] == "pin" else (5.0 if p["kind"] == "anchor" else 3.5)
            cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int((r + 2) * 16), (255, 255, 255), -1, cv2.LINE_AA, shift=4)
            cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int(r * 16), (40, 26, 22) if p["kind"] != "pin_coarse" else (120, 100, 90), -1, cv2.LINE_AA, shift=4)
        return im
    def texts(img):
        im = img.copy()
        for l in labels:
            if l["placed"]: l["_L"].draw(im)
        return im
    out = {}
    out["ref_notext"] = save(base, f"{NAME}_ref_notext_v2.png")
    full = texts(dots(base)); out["ref_labels"] = save(full, f"{NAME}_ref_labels_v2.png", quant=True)
    gr = np.zeros((H, W), np.float32); gitems = []
    for lo in np.arange(17.0, 19.51, 0.25):
        la = np.linspace(47.5, 50, 300); p = F.px(np.full_like(la, lo), la)
        cv2.polylines(gr, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        k = np.argmin(np.abs(p[:, 1] - 30))
        if 20 < p[k, 0] < W - 80: gitems.append((f"{lo:g}°E", (float(p[k, 0]) + 3, 30.0), 17, "grat"))
    for la in np.arange(47.75, 49.76, 0.25):
        lo = np.linspace(16.5, 20, 300); p = F.px(lo, np.full_like(lo, la))
        cv2.polylines(gr, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        k = np.argmin(np.abs(p[:, 0] - 50))
        if 40 < p[k, 1] < H - 10: gitems.append((f"{la:g}°N", (50.0, float(p[k, 1]) - 12), 17, "grat"))
    gimg = full * (1 - 0.55 * gr[..., None]) + np.float32([60, 110, 170]) * 0.55 * gr[..., None]
    out["ref_graticule"] = save(MR.draw_text(gimg, gitems), f"{NAME}_ref_graticule_v2.png", quant=True)
    zimg = full.copy()
    def rect(im, r, col, t=3): cv2.rectangle(im, (int(r[0]), int(r[1])), (int(r[2]), int(r[3])), col, t)
    rect(zimg, tsafe, (30, 140, 60), 2); rect(zimg, ps, (200, 120, 0), 2)
    for l in labels:
        if l["placed"]: b = l["bbox"]; rect(zimg, [b[0] - 10, b[1] - 10, b[2] + 10, b[3] + 10], (60, 90, 200), 2)
    rect(zimg, med, (170, 30, 160), 4); rect(zimg, orn, (200, 60, 40), 4)
    out["zones_overlay"] = save(zimg, f"{NAME}_zones_overlay_v2.png", quant=True)
    pr_ = inside(os.path.join(IMG, f"{NAME}_realm_ids_v2.png"))
    Image.fromarray(idimg).quantize(colors=8, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(pr_, optimize=True); out["realm_ids"] = pr_
    # control points (OSM rivers)
    C = []
    def add(**k):
        x, y = F.px(k["lon"], k["lat"])
        if 0.05 * W <= x <= 0.95 * W and 0.05 * H <= y <= 0.95 * H: C.append(dict(k, px=[round(float(x), 1), round(float(y), 1)]))
    big = [k for k in R if rlen[k] >= 12]
    for a in big:                                    # confluence = an end of river a lying on river b
        ends = []
        for ln in getattr(R[a], "geoms", [R[a]]): ends += [Point(ln.coords[0]), Point(ln.coords[-1])]
        for b in big:
            if b == a: continue
            for e in ends:
                if e.distance(R[b]) < 0.004 and frame_box.contains(e):
                    q = nearest_points(R[b], e)[0]
                    add(type="confluence", name=f"{a} into {b}", lon=round(q.x, 4), lat=round(q.y, 4), source="OSM waterway=river centerlines (ODbL): end of the tributary within 400 m of the main river")
    def bends(rn, tol, thr, minleg_km, tag):
        for ln in getattr(R[rn], "geoms", [R[rn]]):
            c = np.asarray(ln.simplify(tol).coords)
            for j in range(1, len(c) - 1):
                v1, v2 = (c[j] - c[j - 1]) * [0.66, 1], (c[j + 1] - c[j]) * [0.66, 1]
                if min(np.linalg.norm(v1), np.linalg.norm(v2)) * 111 < minleg_km: continue
                ang = math.degrees(math.acos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-12), -1, 1)))
                if ang > thr: add(type="river_bend", name=f"{rn} bend {ang:.0f} deg", lon=round(float(c[j][0]), 4), lat=round(float(c[j][1]), 4), turn_deg=round(ang, 1),
                                  source=f"OSM {rn} centerline vertex ({tol * 111:.1f} km simplification), turn > {thr} deg", weight=tag)
    bends("Váh", 0.012, 35, 2.0, "high (spine)")
    for rn in big:
        if rn != "Váh": bends(rn, 0.012, 55, 2.0, "low (minor river)")
    # dedupe confluences of split ways
    pri = {"confluence": 0, "river_bend": 1}
    C.sort(key=lambda c: (pri[c["type"]], 0 if "Váh" in c["name"] else 1, -c.get("turn_deg", 0)))
    sel = []; min_sep = 0.045 * W
    for c in C:
        if all(math.dist(c["px"], s["px"]) >= min_sep for s in sel): sel.append(dict(c, role="primary"))
    for p in P:
        if inf(p): sel.append(dict(type="settlement", name=p["text"] or "Csejte manor (village)", key=p["key"], qid=p["qid"], lon=p["lon"], lat=p["lat"],
                                   px=[round(p["xy"][0], 1), round(p["xy"][1], 1)], role="secondary", band=p["band"], source="Wikidata P625 (live) = MAP-PLACES-bathory-v1"))
    for i, c in enumerate(sel):
        c["id"] = f"CP{i + 1:02d}"; c["plate_px"] = [round(2 * c["px"][0], 1), round(2 * c["px"][1], 1)]; c["search_px_out"] = 40 if c["type"] != "settlement" else 60
    nprim = sum(c["role"] == "primary" for c in sel); nvah = sum(c["role"] == "primary" and "Váh" in c["name"] for c in sel)
    TH = dict(pass_px=4, flag_px=8, pass_km=round(4 * kmpp, 3), flag_km=round(8 * kmpp, 3))
    checks = []
    for p in P:
        x, y = p["xy"]; lab = next((l for l in labels if l["key"] == p["key"]), None)
        checks.append(dict(key=p["key"], text=p["text"], qid=p["qid"], kind=p["kind"], band=p["band"], lonlat=[round(p["lon"], 5), round(p["lat"], 5)],
                           map_places_latlon=list(p["mp_latlon"]), map_places_delta_km=p["map_places_delta_km"], px=[round(x, 1), round(y, 1)], in_frame=inf(p),
                           in_pin_safe=bool(ps[0] <= x <= ps[2] and ps[1] <= y <= ps[3]), realm=realm_at(p),
                           ref_label=(dict(text=lab["text"], bbox=lab["bbox"], side=lab["side"]) if lab and lab["placed"] else None), note=p["note"]))
    cs, by = PK["csejte"]["xy"], PK["bytca"]["xy"]
    sep = dict(px=round(math.dist(cs, by), 1), km=round(hav(PK["csejte"]["lat"], PK["csejte"]["lon"], PK["bytca"]["lat"], PK["bytca"]["lon"]), 1),
               phone_note="at a 6.1in phone (1080x1920 shown ~65 mm wide) the pins are ~%.0f mm apart" % (math.dist(cs, by) / W * 65))
    pb = F.proj_bounds_m()
    J = dict(name="framing_refpack_bathory_v2", created=now, supersedes="framing_refpack_bathory_v1.json (kept)", decision="Vellum option (b): crop tight on the Vah valley, Upper Hungary fills the frame, Vienna dropped",
             authority="standalones/bathory/v2/MAP-PLACES-bathory-v1.md",
             projection=dict(name="Lambert azimuthal equal-area, spherical, centred on the frame centre, north up", sphere_radius_m=6371000, note="x_px = (X_m - xmin)/m_per_px, y_px = (ymax - Y_m)/m_per_px"),
             frames={NAME: dict(aspect="9:16", size_px=[W, H], center_lonlat=list(CENTER), width_km=WIDTH_KM, height_km=round(F.height_km, 2),
                 m_per_px=round(kmpp * 1000, 3), km_per_px=round(kmpp, 5), proj4=proj_string(CENTER), projected_bounds_m={k: round(v, 1) for k, v in pb.items()}, lonlat_bounds=LB,
                 pin_inset=list(pin_inset), pin_safe_px=list(ps), title_safe_px=list(tsafe), csejte_bytca_separation=sep,
                 safe_area_check=dict(story_pins_in_pin_safe=all(c["in_pin_safe"] for c in checks if c["kind"] == "pin"), places=checks),
                 label_zones=[dict(key=l["key"], text=l["text"], rect_px=l["bbox"], pad_px=10) for l in labels if l["placed"]],
                 labels_not_placed=[l["text"] for l in labels if not l["placed"]], pozsony="out of frame (x=%.0f px) - dropped, as allowed" % PK["pozsony"]["xy"][0] if not inf(PK["pozsony"]) else "in frame",
                 label_text_rule="MAP-PLACES 1610 names only. No river, range, realm, date or status text.",
                 zones=Z, vah=vah_stats, danube="out of frame (frame bottom %.3fN; the Danube runs ~47.75-48.15N west/south of the frame)" % LB["lat_min"],
                 realms=dict(status="COARSE engine-pigment masks; never painted from the reference", source="OpenHistoricalMap (CC0) relations, as v1", ohm_relations={str(k): v for k, v in tags.items()},
                             share_pct=shares, moravia_wedge=mor_edge, legend=legend,
                             ottoman=dict(ohm_relation=2860343, overlap_px=otto_px, note="OHM 1540-1669 envelope; not masked/tinted (MAP-PLACES: frontier out of frame)")),
                 renderer=dict(map=dict(center_lonlat=list(CENTER), width_km=WIDTH_KM), out_wh=[W, H], plate_wh=[2 * W, 2 * H], px_scale_out_to_plate=2.0),
                 sources=dict(land="Natural Earth 10m land", rivers="OpenStreetMap waterway=river named ways (ODbL, (c) OSM contributors) via Overpass 2026-10-31; drawn: Vah heavy + rivers >= 12 km in frame: " + ", ".join(sorted(minor)),
                              relief="ETOPO 2022 v1 15-arcsec (NOAA NCEI, doi:10.25921/fd45-gt74) via coastwatch ERDDAP ETOPO_2022_v1_15s",
                              places="Wikidata P625 live 2026-10-31 = MAP-PLACES-bathory-v1"),
                 files={k: os.path.relpath(v, OUTDIR) for k, v in out.items()})})
    with open(FRAMING, "x") as f: json.dump(J, f, indent=1, ensure_ascii=False)
    CP = dict(name="control_points_refpack_bathory_v2", px_space="out px (plate px = 2x, also given)", frame=NAME,
              thresholds=dict(TH, scaled_from="Edward v2 px gates (4/8 px); km = px x %.5f km/px" % kmpp), warp_limit_frac_of_min_side=0.025,
              counts=dict(primary=nprim, primary_vah=nvah, secondary=len(sel) - nprim), control_points=sel)
    with open(CPJ, "x") as f: json.dump(CP, f, indent=1, ensure_ascii=False)
    print(json.dumps(dict(kmpp=kmpp, H_km=F.height_km, LB=LB, labels=[(l["text"], l["placed"], l.get("side"), l.get("bbox")) for l in labels], zones={k: (v["rect_px"], v["position"]) for k, v in Z.items()},
                          nprim=nprim, nvah=nvah, shares=shares, mor=mor_edge, vah=vah_stats, sep=sep, minor=sorted(minor),
                          checks=[(c["key"], c["px"], c["in_frame"], c["in_pin_safe"], c["realm"]) for c in checks]), ensure_ascii=False))

if __name__ == "__main__":
    main()
