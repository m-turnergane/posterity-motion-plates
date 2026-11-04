"""Refpack v1: framing JSON (deliverable 1) + clean reference images (deliverable 2) + realm masks.
python make_refs.py   (refuses to overwrite anything; scratch goes to /tmp/refdbg)"""
import sys; sys.dont_write_bytecode = True
import os, json, math, hashlib, datetime, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from refpack_lib import *
import make_framing as MF

TAG = os.environ.get("REFPACK_TAG", "v2")                       # v1 = first pass (superseded, kept: never overwrite)
OUTD = os.environ.get("REFPACK_OUT", HERE); IMG = os.path.join(OUTD, f"img_{TAG}"); os.makedirs(IMG, exist_ok=True)
FRAMING = os.path.join(OUTD, f"framing_refpack_{TAG}.json")
# final frames: solver minimum x ~1.02 comfort, rounded (solver output recorded in the JSON)
FINAL = {"euro_16x9": ((0.5, 48.5), 3040), "britain_16x9": ((-2.55, 51.95), 705),
         "euro_9x16": ((1.5, 48.0), 1550), "britain_9x16": ((-2.6, 51.95), 700)}   # solver result rounded up ~1-3 %
SEA, LAND, COAST, RIVER, BORDER = (213, 225, 233), (243, 240, 231), (78, 96, 112), (96, 140, 176), (64, 52, 52)
RIV_MAJOR = {"Thames", "Severn", "Seine", "Loire", "Rhine", "Rhein", "Rhin", "Rhône", "Po", "Garonne", "Shannon", "Danube", "Donau", "Elbe", "Ebro"}
RIV_MINOR = {"Trent", "Avon", "Mosel", "Maas", "Schelde", "Marne", "Yonne", "Main", "Weser", "Dordogne", "Durance", "Tarn", "Vienne", "Ticino"}
MOUNTAINS = [("ALPS", (8.6, 46.35)), ("PYRENEES", (0.6, 42.75)), ("MASSIF CENTRAL", (2.9, 45.3)), ("WELSH UPLANDS", (-3.75, 52.35)),
             ("APENNINES", (10.3, 44.25)), ("JURA", (6.2, 46.85)), ("VOSGES", (7.05, 48.2)), ("PENNINES", (-2.15, 54.15))]
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def save(img, name):
    p = os.path.join(IMG, name); assert not os.path.exists(p), f"refuse to overwrite {p}"
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(p, optimize=True); return p

def base_layers(F):
    g = F.geom; bbox = g.lonlat_bbox(); kmpp = g.km_per_px
    land = V1.raster_polys(g, f"{NE}/ne_10m_land/ne_10m_land.shp", bbox)
    lakes = V1.raster_polys(g, f"{NE}/ne_10m_lakes/ne_10m_lakes.shp", bbox, filt=lambda r: V1._rank(r) <= 6)
    land = np.clip(land - lakes, 0, 1)
    s = 1.25 if kmpp < 0.8 else 1.0
    def rv(names, wpx): return V1.raster_lines(g, f"{NE}/ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp", bbox,
                                               lambda r: MM._nm(r.get("name", "")) in names and r.get("featurecla", "").startswith("River"), lambda r: wpx)
    rivers = np.maximum(rv(RIV_MAJOR, 2.3 * s), 0.75 * rv(RIV_MINOR, 1.4 * s)) * np.clip(land * 1.5, 0, 1)
    elev, _ = MM.elevation(g)
    return land, rivers, elev

def relief(elev, land, kmpp):
    """grey relief: elevation tone from 250 m up + hillshade (exaggerated for the scale) + 1000/2000 m form lines"""
    zf = float(np.clip(2.2 * kmpp, 1.2, 4.0))
    hs = MM.hillshade(elev, kmpp, zf=zf)
    mt = MM.smoothstep(250.0, 2400.0, elev) * land
    dark = np.clip(0.30 * mt ** 0.8 - 0.55 * hs * MM.smoothstep(150.0, 700.0, elev), 0, 0.55) * land
    form = np.zeros_like(elev)
    for z, a in ((1000.0, 0.45), (2000.0, 0.6)):
        m = (elev > z).astype(np.uint8); e = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((2, 2), np.uint8)).astype(np.float32)
        form = np.maximum(form, cv2.GaussianBlur(e, (0, 0), 0.6) * a)
    return dark, form * land

def compose(F, L, tint_idx=None, borders=None, dedge=None):
    land, rivers, elev, dark, form = L["land"], L["rivers"], L["elev"], L["dark"], L["form"]
    img = np.empty((F.H, F.W, 3), np.float32); img[:] = SEA
    lc = np.empty_like(img); lc[:] = LAND
    if tint_idx is not None:
        for gi, (gname, _, _) in enumerate(REALM_GROUPS):
            lc[tint_idx == gi + 1] = REALM_TINT[gname]
        if dedge is not None:   # data-extent edge (e.g. east end of the 'Imperial rim' polygon): fade the tint out, draw no line
            from scipy.ndimage import distance_transform_edt
            dist, (iy, ix) = distance_transform_edt(tint_idx == 0, return_indices=True)
            near = (tint_idx == 0) & dedge["fade_ok"][iy, ix] & (land > 0.5)
            a_ = np.exp(-dist * F.geom.km_per_px / 70.0)[..., None] * near[..., None]
            src = np.float32([REALM_TINT[REALM_GROUPS[k - 1][0]] if k else LAND for k in range(len(REALM_GROUPS) + 1)])[tint_idx[iy, ix]]
            lc = lc * (1 - a_) + src * a_
    a = land[..., None]; img = img * (1 - a) + lc * a
    img = img * (1 - dark[..., None]) + np.float32([88, 84, 80]) * dark[..., None]
    img = img * (1 - form[..., None]) + np.float32([110, 100, 92]) * form[..., None]
    rv = rivers[..., None] * 0.95; img = img * (1 - rv) + np.float32(RIVER) * rv
    if borders is not None:
        bw = 2 if F.geom.km_per_px < 1.0 else 1
        b = cv2.dilate(borders.astype(np.uint8), np.ones((bw, bw), np.uint8)).astype(np.float32)
        b = np.clip(cv2.GaussianBlur(b, (0, 0), 0.6) * 1.3, 0, 1)[..., None] * 0.92
        img = img * (1 - b) + np.float32(BORDER) * b
    lb = cv2.GaussianBlur(land, (0, 0), 0.7); edge = np.clip(lb * (1 - lb) * 4.2, 0, 1)[..., None]
    img = img * (1 - edge) + np.float32(COAST) * edge
    return img

def draw_text(img, items):
    """items: (text, (x,y) centre, px, kind) kind in realm|mountain|grat"""
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for text, (x, y), px, kind in items:
        if kind == "realm":
            f = ImageFont.truetype(V1.FONT_SC, int(px)); col = (120, 56, 52); sp = px * 0.18
        elif kind == "mountain":
            f = ImageFont.truetype(V1.FONT_IT, int(px)); col = (96, 90, 84); sp = px * 0.12
        else:
            f = ImageFont.truetype(FONT_SANS, int(px)); col = (70, 96, 120); sp = 0
        ws = [f.getlength(ch) for ch in text]; tw = sum(ws) + sp * (len(text) - 1)
        cx = x - tw / 2
        for ch, w in zip(text, ws):
            d.text((cx, y), ch, font=f, fill=col, anchor="lm"); cx += w + sp
    return np.asarray(im, np.float32)

def text_width(text, px, kind):
    f = ImageFont.truetype(V1.FONT_SC if kind == "realm" else V1.FONT_IT, int(px)); sp = px * (0.18 if kind == "realm" else 0.12)
    return sum(f.getlength(c) for c in text) + sp * (len(text) - 1)

SHORT = {"KINGDOM OF ENGLAND": "ENGLAND", "KINGDOM OF FRANCE": "FRANCE", "KINGDOM OF SCOTLAND": "SCOTLAND", "DUCHY OF BRITTANY": "BRITTANY",
         "DUCHY OF BURGUNDY": "BURGUNDY", "LORDSHIP OF IRELAND": "IRELAND (ENG.)", "GASCONY (ENGLISH)": "GASCONY", "HOLY ROMAN EMPIRE": "EMPIRE"}
def realm_label_spots(F, idx, block, base_px, skip_gaelic=False):
    """one label per realm group on its largest visible part, at the interior point farthest from its edge and
    from anything already placed; font shrinks to fit, skipped below 13 px."""
    out = []; bl = block.copy()
    order = sorted(range(len(REALM_GROUPS)), key=lambda gi: -(idx == gi + 1).sum())
    for gi in order:
        gname, _, text = REALM_GROUPS[gi]; m = (idx == gi + 1).astype(np.uint8)
        if m.sum() < 400: continue
        n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8); k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        comp = ((lab == k) & (bl == 0)).astype(np.uint8)
        dist = cv2.distanceTransform(np.pad(comp, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
        ii = np.pad(comp.astype(np.int32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)   # integral image: box fully inside the realm
        hit = None
        for text, lo_px in ((text, max(18, base_px - 12)), (SHORT.get(text, text), 12)):
          for px in range(base_px, lo_px - 1, -1):
            tw = int(text_width(text, px, "realm")) + 12; th = int(px * 1.2) + 8
            if tw >= F.W or th >= F.H: continue
            inside = ii[th:, tw:] - ii[:-th, tw:] - ii[th:, :-tw] + ii[:-th, :-tw]      # [y0, x0] = box sum
            ok = inside == tw * th
            if ok.any():
                cy, cx = np.nonzero(ok); sc = dist[cy + th // 2, cx + tw // 2]
                j = int(np.argmax(sc)); y, x = int(cy[j] + th // 2), int(cx[j] + tw // 2); hit = px; break
          if hit: break
        if hit is None: out.append(dict(group=gname, text=text, placed=False, why="no room inside the realm for the name at >=12 px")); continue
        px = hit
        tw = text_width(text, px, "realm"); bb = (int(x - tw / 2) - 6, int(y - px * 0.6) - 4, int(x + tw / 2) + 6, int(y + px * 0.6) + 4)
        bl[max(0, bb[1]):bb[3], max(0, bb[0]):bb[2]] = 1
        out.append(dict(group=gname, text=text, placed=True, xy=[int(x), int(y)], px=int(px), bbox=list(bb)))
    for text, ll in NEUTRAL_LABELS:
        if text == "GAELIC IRELAND" and skip_gaelic: continue
        x, y = F.px(*ll); px = max(14, int(base_px * 0.75))
        tw = text_width(text, px, "realm"); bb = (int(x - tw / 2) - 6, int(y - px * 0.6) - 4, int(x + tw / 2) + 6, int(y + px * 0.6) + 4)
        if bb[0] < 10 or bb[1] < 10 or bb[2] > F.W - 10 or bb[3] > F.H - 10 or bl[max(0, bb[1]):bb[3], max(0, bb[0]):bb[2]].any(): continue
        bl[bb[1]:bb[3], bb[0]:bb[2]] = 1
        out.append(dict(group="neutral", text=text, placed=True, xy=[int(x), int(y)], px=px, bbox=list(bb), note="neutral (unfilled) land, REALMS R05/R20-21"))
    return out, bl

def graticule(F, step):
    g = np.zeros((F.H, F.W), np.float32); items = []
    for lo in np.arange(-30, 40.01, step):
        la = np.linspace(30, 64, 600); p = F.px(np.full_like(la, lo), la)
        cv2.polylines(g, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        for yy in (14,):
            k = np.argmin(np.abs(p[:, 1] - 22));
            if 0 < p[k, 0] < F.W - 30: items.append((f"{abs(lo):g}°{'W' if lo < 0 else 'E'}", (float(p[k, 0]) + 2, 22.0), 15, "grat"))
    for la in np.arange(30, 64.01, step):
        lo = np.linspace(-30, 40, 800); p = F.px(lo, np.full_like(lo, la))
        cv2.polylines(g, [np.int32(np.round(p * 16))], False, 1.0, 1, cv2.LINE_AA, shift=4)
        k = np.argmin(np.abs(p[:, 0] - 40))
        if 30 < p[k, 1] < F.H - 10: items.append((f"{la:g}°N", (40.0, float(p[k, 1]) - 10), 15, "grat"))
    return g, items

def zones(F, land, label_boxes, pins_xy, ornament_ok=True):
    """medallion parking zone + ornament (compass) zone: corner/edge squares inside action-safe, clear of every label
    zone and pin (20 px pad), preferring open sea.  Returned as px rects + lon/lat corners."""
    W, H = F.W, F.H; m = int(0.05 * min(W, H)); sm = int(0.22 * min(W, H)); so = int(0.18 * min(W, H))
    occ = np.zeros((H, W), np.uint8)
    for bb in label_boxes: occ[max(0, bb[1] - 20):bb[3] + 20, max(0, bb[0] - 20):bb[2] + 20] = 1
    for x, y in pins_xy: cv2.circle(occ, (int(x), int(y)), 40, 1, -1)
    def cands(s):
        xs = [m, (W - s) // 2, W - m - s] + ([int(W * 0.25 - s / 2), int(W * 0.75 - s / 2)] if W > H else [])
        ys = [m, (H - s) // 2, H - m - s] + ([int(H * 0.2), int(H * 0.68)] if H > W else [])
        return [(x, y, x + s, y + s) for x in xs for y in ys]
    def score(r):
        x0, y0, x1, y1 = r
        if occ[y0:y1, x0:x1].any(): return None
        return float((land[y0:y1, x0:x1] < 0.5).mean())
    sc = sorted([(score(r), r) for r in cands(sm) if score(r) is not None], key=lambda t: -t[0])
    med = sc[0][1]; occ[med[1] - 10:med[3] + 10, med[0] - 10:med[2] + 10] = 1
    so_c = sorted([(score(r), r) for r in cands(so) if score(r) is not None], key=lambda t: -t[0])
    orn = so_c[0][1] if so_c else None
    def ll(r):
        x0, y0, x1, y1 = r; lo, la = F.inv([x0, x1, x1, x0], [y0, y0, y1, y1])
        return [[round(float(a), 3), round(float(b), 3)] for a, b in zip(lo, la)]
    def where(r):
        cx, cy = (r[0] + r[2]) / 2 / W, (r[1] + r[3]) / 2 / H
        return ("upper" if cy < 0.34 else "lower" if cy > 0.66 else "middle") + "-" + ("left" if cx < 0.34 else "right" if cx > 0.66 else "centre")
    out = dict(medallion=dict(rect_px=list(map(int, med)), lonlat_corners=ll(med), sea_fraction=round(sc[0][0], 3), position=where(med),
                              use="parking/hold position for the portrait medallion at wide zoom; the travelling marker itself follows the route and must never cover a label zone"))
    if orn: out["ornament_reserved"] = dict(rect_px=list(map(int, orn)), lonlat_corners=ll(orn), sea_fraction=round(so_c[0][0], 3), position=where(orn),
                                           use="the ONLY place a static compass rose may be painted; nothing else ornamental anywhere on the plate")
    return out

def crop_test(F, pins, regions, out_W=1080, out_H=1920):
    """Can the 9:16 deliverable be a crop of this 16:9 plate?  Slide a full-height 9:16 window; count stops inside the
    window's pin-safe area (10% x inset) and report the needed upscale."""
    cw = int(round(F.H * out_W / out_H)); pts = [F.px(s["lon"], s["lat"]) for s in pins + regions]; best = (-1, 0)
    for x0 in range(0, F.W - cw + 1, 4):
        n = sum(1 for x, y in pts if x0 + 0.1 * cw <= x <= x0 + 0.9 * cw and 0.08 * F.H <= y <= 0.92 * F.H)
        if n > best[0]: best = (n, x0)
    return dict(crop_w_px=cw, crop_h_px=F.H, best_x0=best[1], stops_in_safe=best[0], stops_total=len(pts),
                upscale_to_1080x1920=round(out_H / F.H, 3), passes=bool(best[0] == len(pts) and out_H / F.H <= 1.06))

def main():
    assert not os.path.exists(FRAMING), f"refuse to overwrite {FRAMING}"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET")
    geo_ok = VR.check_geometry(); n_ok = sum(r["ok"] for r in geo_ok)
    J = dict(name=f"framing_refpack_{TAG}", created=now, projection=dict(
        name="Lambert azimuthal equal-area, spherical (engine map_route_v1.LAEA), centred on each frame centre, north up",
        sphere_radius_m=int(R_KM * 1000), note="pyproj not installed; the engine's own LAEA formulas are used (forward map_route_v1.LAEA, inverse map_modes_v2.inverse_laea). "
        "The proj strings are exact equivalents (+R sphere, not WGS84 ellipsoid). Pixel mapping: x_px = (X_m - xmin) / m_per_px, y_px = (ymax - Y_m) / m_per_px."),
        verifier=dict(script="verify_realms_1327.check_geometry", passed=n_ok, total=len(geo_ok)),
        safe_area_definitions=dict(title_safe="5% inset each side (labels must stay inside)",
                                   pin_safe="per frame pin_inset (fraction of W, H): every pinned stop and region label point must be inside"),
        frames={})
    assert n_ok == len(geo_ok) == 40, f"realm verifier {n_ok}/{len(geo_ok)}"
    for name, (c, wkm) in FINAL.items():
        sp = MF.SPECS[name]; W, H = sp["WH"]; F = Frame(name, c, wkm, W, H); kind = sp["kind"]
        (w_min, c_min), _ = MF.solve(sp)
        pins, regions, auth = stops_for(kind); cfg = authority_cfg(kind); refusals = refusal_tests(cfg)
        assert all(r["refused"] for r in refusals), refusals
        print(name, "layers..."); land, rivers, elev = base_layers(F); dark, form = relief(elev, land, F.geom.km_per_px)
        L = dict(land=land, rivers=rivers, elev=elev, dark=dark, form=form)
        idx = realm_index(F, land); bord, dedge = borders_from_index(idx, land, F)
        # raster check (family dominance at the 30 verifier points) on our exclusive index
        fam_of = {gname: gname for gname, _, _ in REALM_GROUPS}
        _, feats = MM.load_realms(); id2fam = {f["properties"]["id"]: f["properties"]["family"] for f in feats}
        gfam = {gi + 1: id2fam[ids[0]] for gi, (g, ids, _) in enumerate(REALM_GROUPS)}
        weights = {}
        for gi, fam in gfam.items(): weights[fam] = np.maximum(weights.get(fam, 0), (idx == gi).astype(np.float32))
        ras = VR.check_raster(weights, lambda lo, la: tuple(F.px(lo, la)), (H, W), [], [])
        ras = [r for r in ras if r["check"].startswith("raster ") and "no realm names" not in r["check"]]
        # ---- dots + place labels (engine label placer)
        kmpp = F.geom.km_per_px; lpx = 30 if kmpp < 0.8 else 26; rpx = lpx - 2; dot_r = 6.0 if kmpp < 0.8 else 5.0
        tsafe = (int(0.05 * W), int(0.05 * H), int(0.95 * W), int(0.95 * H))
        block = np.zeros((H, W), np.uint8); P = []
        for p in pins:
            x, y = F.px(p["lon"], p["lat"]); P.append(dict(p, xy=[float(x), float(y)]))
            cv2.circle(block, (int(round(x)), int(round(y))), int(dot_r + 4), 1, -1)
        KEY = ["Berkeley", "Corfe", "Sandwich", "Sluis", "Paris", "Avignon", "Cologne", "Milan", "Chepstow", "Kenilworth", "Westminster"]
        order = sorted(P, key=lambda p: (KEY.index(p["name"]) if p["name"] in KEY else 99, p["row"]))
        labels = []
        for p in order:
            best = R2.place_label(p["name"], p["xy"], dot_r, block, tsafe, lpx, [], H, W,
                                  other_pins=[q["xy"] for q in P if q is not p and math.dist(q["xy"], p["xy"]) > 0.5])
            used = lpx
            if (best is None or best[5] != 0) and p["name"] in KEY:      # crowded: one size smaller, ignore dots <= 9 px away
                for used, near in ((lpx - 4, 9), (lpx - 6, 22)):
                    b2 = block.copy()
                    for q in P:                                    # let the text pass close to (not over) a neighbour's dot
                        if q is not p and math.dist(q["xy"], p["xy"]) <= near:
                            qx, qy = int(round(q["xy"][0])), int(round(q["xy"][1])); cv2.circle(b2, (qx, qy), int(dot_r + 4), 0, -1); cv2.circle(b2, (qx, qy), int(dot_r + 1), 1, -1)
                    best = R2.place_label(p["name"], p["xy"], dot_r, b2, tsafe, used, [], H, W,
                                          other_pins=[q["xy"] for q in P if q is not p and math.dist(q["xy"], p["xy"]) > near])
                    if best is not None and best[5] == 0: break
            if best is None or best[5] != 0:
                labels.append(dict(row=p["row"], text=p["name"], placed=False, why="no collision-free spot at this scale (see Britain frame)")); continue
            sc_, Lb, bb, sd, gap, hit = best; block[max(0, bb[1] - 4):bb[3] + 4, max(0, bb[0] - 4):bb[2] + 4] = 1
            labels.append(dict(row=p["row"], text=p["name"], placed=True, side=sd, bbox=[int(v) for v in bb], px=used, _L=Lb))
        for r in regions:
            x, y = F.px(r["lon"], r["lat"])
            if r["row"] == "2-06" and kind == "britain": x, y = F.px(-6.55, 52.75)
            r["xy"] = [float(x), float(y)]
            best = R2.place_label(r["name"], r["xy"], 6.0, block, tsafe, rpx, [], H, W, other_pins=[q["xy"] for q in P], region=True)
            if best is None or best[5] != 0:
                labels.append(dict(row=r["row"], text=r["name"], placed=False, region=True, why="no collision-free spot")); continue
            sc_, Lb, bb, sd, gap, hit = best; block[max(0, bb[1] - 4):bb[3] + 4, max(0, bb[0] - 4):bb[2] + 4] = 1
            labels.append(dict(row=r["row"], text=r["name"], placed=True, region=True, side=sd, bbox=[int(v) for v in bb], px=rpx, _L=Lb))
        # ---- realm + mountain names (reference only)
        base_px = 34 if W > H else 30
        mblock = block | (cv2.dilate((elev > 900).astype(np.uint8), np.ones((9, 9), np.uint8)) & (land > 0.5))   # keep realm names off the ranges
        rl, bl2 = realm_label_spots(F, idx, mblock, base_px, skip_gaelic=any(r["row"] == "2-06" for r in regions))
        mitems = []
        for text, ll in MOUNTAINS:
            x, y = F.px(*ll); mpx = 19; tw = text_width(text, mpx, "mountain")
            bb = (int(x - tw / 2) - 4, int(y - 12), int(x + tw / 2) + 4, int(y + 12))
            if bb[0] < tsafe[0] or bb[2] > tsafe[2] or bb[1] < tsafe[1] or bb[3] > tsafe[3] or bl2[bb[1]:bb[3], bb[0]:bb[2]].any(): continue
            bl2[bb[1]:bb[3], bb[0]:bb[2]] = 1; mitems.append((text, (float(x), float(y)), mpx, "mountain"))
        # ---- images
        def dots(img):
            im = img.copy()
            for p in P:
                x, y = p["xy"]
                cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int((dot_r + 2) * 16), (255, 255, 255), -1, cv2.LINE_AA, shift=4)
                cv2.circle(im, (int(round(x * 16)), int(round(y * 16))), int(dot_r * 16), (40, 26, 22), -1, cv2.LINE_AA, shift=4)
            return im
        def texts(img):
            im = draw_text(img, [(r["text"], tuple(r["xy"]), r["px"], "realm") for r in rl if r["placed"]] + mitems)
            for l in labels:
                if l.get("placed"): l["_L"].draw(im)
            return im
        bare = compose(F, L, None, bord); tinted = compose(F, L, idx, bord, dedge=dedge)
        out = {}
        out["bare"] = save(bare, f"{name}_ref_bare.png")                       # geography + realm borders only
        out["notext"] = save(dots(bare), f"{name}_ref_notext.png")             # + stop dots, no text
        full = texts(dots(bare)); out["labels"] = save(full, f"{name}_ref_labels.png")
        gstep = 2 if kind == "euro" else 1; gr, gitems = graticule(F, gstep)
        gimg = full * (1 - 0.55 * gr[..., None]) + np.float32([60, 110, 170]) * 0.55 * gr[..., None]
        out["graticule"] = save(draw_text(gimg, gitems), f"{name}_ref_graticule.png")
        out["tinted_notext"] = save(tinted, f"{name}_ref_tinted_notext.png")  # recommended attachment for the image model
        out["tinted_labels"] = save(texts(dots(tinted)), f"{name}_ref_tinted_labels.png")
        # realm id mask (engine side; borders/pulses come from this, never from the painting)
        pal = {0: (0, 0, 0)}; idimg = np.zeros((H, W, 3), np.uint8); idimg[land > 0.5] = (128, 128, 128)
        legend = {"0": "sea", "128,128,128": "neutral land"}
        for gi, (gname, ids, text) in enumerate(REALM_GROUPS):
            col = tuple(int(v) for v in np.array(REALM_TINT[gname]) * 0.0 + np.array([(37 * (gi + 1)) % 256, (91 * (gi + 1)) % 256, (157 * (gi + 1)) % 256]))
            idimg[idx == gi + 1] = col; legend[",".join(map(str, col))] = f"{gname} ({'+'.join(ids)})"
        out["realm_ids"] = save(idimg, f"{name}_realm_ids.png")
        # ---- zones + safe checks
        lbox = [l["bbox"] for l in labels if l.get("placed")]
        Z = zones(F, land, lbox, [p["xy"] for p in P])
        zimg = full.copy()
        def rect(im, r, col, t=3): cv2.rectangle(im, (r[0], r[1]), (r[2], r[3]), col, t)
        rect(zimg, tsafe, (30, 140, 60), 2)
        ix, iy = sp["pin_inset"]; ps = (int(ix * W), int(iy * H), int((1 - ix) * W), int((1 - iy) * H)); rect(zimg, ps, (200, 120, 0), 2)
        for b in lbox: rect(zimg, [b[0] - 10, b[1] - 10, b[2] + 10, b[3] + 10], (60, 90, 200), 2)
        rect(zimg, Z["medallion"]["rect_px"], (170, 30, 160), 4)
        if "ornament_reserved" in Z: rect(zimg, Z["ornament_reserved"]["rect_px"], (200, 60, 40), 4)
        out["zones_overlay"] = save(zimg, f"{name}_zones_overlay.png")
        checks = []
        for p in P + regions:
            x, y = p["xy"]; lab = next((l for l in labels if l["row"] == p["row"]), None)
            checks.append(dict(row=p["row"], name=p["name"], qid=p["qid"], kind="pin" if p in P else "region_label_only",
                               lonlat=[round(p["lon"], 5), round(p["lat"], 5)], px=[round(x, 1), round(y, 1)],
                               in_frame=bool(0 <= x < W and 0 <= y < H), in_pin_safe=bool(ps[0] <= x <= ps[2] and ps[1] <= y <= ps[3]),
                               in_title_safe=bool(tsafe[0] <= x <= tsafe[2] and tsafe[1] <= y <= tsafe[3]),
                               label_placed=bool(lab and lab.get("placed")), label_bbox=(lab or {}).get("bbox"), label_side=(lab or {}).get("side"),
                               label_note=None if (lab and lab.get("placed")) else (lab or {}).get("why")))
        pb = F.proj_bounds_m(); asp = "16:9" if W > H else "9:16"
        J["frames"][name] = dict(
            aspect=asp, size_px=[W, H], use=("Map 2 whole route (2a+2b) + Map 1 stations for context" if kind == "euro" else "Map 1 + Map 2a (Britain)"),
            justification=sp["why"], center_lonlat=list(c), width_km=wkm, height_km=round(F.height_km, 2),
            m_per_px=round(F.geom.km_per_px * 1000, 3), km_per_px=round(F.geom.km_per_px, 5),
            proj4=proj_string(c), projected_bounds_m={k: round(v, 1) for k, v in pb.items()}, lonlat_bounds=F.lonlat_bounds(),
            solver=dict(min_width_km=round(w_min, 1), note="minimum width satisfying every pin-safe/geography inset; final = rounded up for comfort, centre = content-centred"),
            pin_inset=list(sp["pin_inset"]), pin_safe_px=list(ps), title_safe_px=list(tsafe),
            safe_area_check=dict(all_stops_in_pin_safe=all(c_["in_pin_safe"] for c_ in checks),
                                 labels_dropped=[c_["name"] for c_ in checks if not c_["label_placed"]], stops=checks),
            label_zones=[dict(row=l["row"], text=l["text"], rect_px=l["bbox"], pad_px=10) for l in labels if l.get("placed")],
            label_zone_rule="keep these rects (+10 px) low-detail on the plate: no settlement vignette, no dense forest/hatching under a label",
            zones=Z, realm_labels_reference_only=[{k: v for k, v in r.items()} for r in rl],
            renderer=dict(note="drop-in for the engine/accept configs: replace their 'map', 'out_wh', 'plate_wh' (plate = 2x out) and 'control_points'",
                          map=dict(center_lonlat=list(c), width_km=wkm), out_wh=[W, H], plate_wh=[2 * W, 2 * H],
                          px_scale_out_to_plate=2.0, register_plate_to="this frame at out_wh (homography/TPS output in out px, scale x2 for plate px)"),
            authority=dict(engine_check="map_route_v1.check_against_authority", rows=auth, refusal_tests=refusals),
            realm_raster_check=dict(passed=sum(r["ok"] for r in ras), total=len(ras), failed=[r for r in ras if not r["ok"]]),
            realm_id_legend=legend,
            crop_from_16x9=None,
            files={k: os.path.relpath(v, OUTD) for k, v in out.items()})
        if asp == "16:9": J["frames"][name]["crop_to_9x16_test"] = crop_test(F, P, regions)
        print(name, "done", J["frames"][name]["safe_area_check"]["all_stops_in_pin_safe"], J["frames"][name]["safe_area_check"]["labels_dropped"], Z["medallion"]["position"], Z.get("ornament_reserved", {}).get("position"))
    J["nine_sixteen_decision"] = dict(own_plate=True, why=[f"{k}: best full-height 9:16 crop holds {v['crop_to_9x16_test']['stops_in_safe']}/{v['crop_to_9x16_test']['stops_total']} stops in its safe area and needs a {v['crop_to_9x16_test']['upscale_to_1080x1920']}x upscale" for k, v in J["frames"].items() if "crop_to_9x16_test" in v])
    json.dump(J, open(FRAMING, "x"), indent=1, default=lambda o: None)
    print(FRAMING)

if __name__ == "__main__":
    main()
