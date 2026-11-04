"""B03 v2 overlay-label layout check (Vellum final ruling 12:20 ET). Read-only on inputs; writes only into this folder.
Places the two-line Csejte / Bytca labels and the faint Vah label in 1080x1920 frame px, checks title-safe, pins,
compass (ornament_reserved), medallion, Vah ink, and renders 1080 + 360x640 proofs."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); RP = os.path.dirname(HERE)
FR = json.load(open(f"{RP}/framing_refpack_bathory_v2.json"))["frames"]["bathory_b03v2_9x16"]
W, H = FR["size_px"]; B = FR["projected_bounds_m"]; MPP = FR["m_per_px"]; R = 6371000.0
lat0, lon0 = map(math.radians, (48.8, 18.2))
def px(lon, lat):
    p, l = math.radians(lat), math.radians(lon) - lon0
    k = math.sqrt(2 / (1 + math.sin(lat0) * math.sin(p) + math.cos(lat0) * math.cos(p) * math.cos(l)))
    X = R * k * math.cos(p) * math.sin(l); Y = R * k * (math.cos(lat0) * math.sin(p) - math.sin(lat0) * math.cos(p) * math.cos(l))
    return ((X - B["xmin"]) / MPP, (B["ymax"] - Y) / MPP)
FONT_SC = "/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf"
FONT_IT = "/usr/share/fonts/truetype/sand-box/google/IM Fell French Canon/IMFellFrenchCanon-Italic.ttf"
INK = (52, 30, 20); HALO = (238, 226, 194)
L1, L2, LV, LEAD = 51, 38, 38, 4           # px at 1080 wide (= 17 / 12.7 / 12.7 px at 360)
TS = FR["title_safe_px"]; MED = FR["zones"]["medallion"]["rect_px"]; CMP = FR["zones"]["ornament_reserved"]["rect_px"]
pins = {p["key"]: tuple(p["px"]) for p in FR["safe_area_check"]["places"] if p["key"] in ("csejte", "bytca", "csejte_manor")}
# Vah spine from the same OSM relation the refpack used
SCR = "/tmp/bathory_scratch"; rel = [r for r in json.load(open(f"{SCR}/osm_vah_rel.json"))["elements"] if r["id"] == 3509398][0]
vah = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vah); segs = []
for m in rel["members"]:
    if m.get("type") == "way" and m.get("role") in ("main_stream", "") and "geometry" in m:
        pts = [px(g["lon"], g["lat"]) for g in m["geometry"]]; segs.append(pts); dv.line(pts, fill=255, width=7)
VAH = np.array(vah) > 0
print("check csejte px", [round(v, 1) for v in px(17.76083, 48.72472)], "json", pins["csejte"])
def text_mask(t, f):
    l, tp, r, b = f.getbbox(t); im = Image.new("L", (r - l + 8, b - tp + 8), 0); ImageDraw.Draw(im).text((4 - l, 4 - tp), t, font=f, fill=255); return im
def block(lines, align):
    ms = [text_mask(t, ImageFont.truetype(fp, s)) for t, fp, s in lines]
    bw = max(m.width for m in ms); bh = sum(m.height for m in ms) + LEAD * (len(ms) - 1)
    im = Image.new("L", (bw, bh), 0); y = 0
    for m in ms:
        x = 0 if align == "L" else (bw - m.width if align == "R" else (bw - m.width) // 2); im.paste(m, (x, y)); y += m.height + LEAD
    return im
def tight(a, x0, y0):
    ys, xs = np.nonzero(np.array(a) > 10); return (x0 + xs.min() - 3, y0 + ys.min() - 3, x0 + xs.max() + 4, y0 + ys.max() + 4)
def inter(b, r): return not (b[2] <= r[0] or r[2] <= b[0] or b[3] <= r[1] or r[3] <= b[1])
def dist(b, q): return math.hypot(max(b[0] - q[0], 0, q[0] - b[2]), max(b[1] - q[1], 0, q[1] - b[3]))
def place(key, lines, others):
    P = pins[key]; best = None
    for side, align in [("E", "L"), ("W", "R"), ("N", "L"), ("N", "C"), ("N", "R"), ("S", "L"), ("S", "C"), ("NE", "L"), ("SE", "L"), ("NW", "R"), ("SW", "R")]:
        im = block(lines, align)
        for gap in (14, 20, 28, 40):
            bw, bh = im.size
            x = {"E": P[0] + gap, "NE": P[0] + gap * .7, "SE": P[0] + gap * .7, "W": P[0] - gap - bw, "NW": P[0] - gap * .7 - bw, "SW": P[0] - gap * .7 - bw}.get(side)
            if x is None: x = {"L": P[0] - 18, "C": P[0] - bw / 2, "R": P[0] + 18 - bw}[align]
            y = {"N": P[1] - gap - bh, "NE": P[1] - gap * .7 - bh, "NW": P[1] - gap * .7 - bh, "S": P[1] + gap, "SE": P[1] + gap * .7, "SW": P[1] + gap * .7}.get(side, P[1] - im.size[1] * 0.30)
            x, y = int(round(x)), int(round(y)); bb = tight(im, x, y)
            if not (TS[0] <= bb[0] and bb[2] <= TS[2] and TS[1] <= bb[1] and bb[3] <= min(TS[3], 1280)): continue   # keep out of the caption third
            pad = [bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10]
            if inter(pad, MED) or inter(pad, CMP): continue
            if dist(bb, P) < 10: continue                                    # clear of own pin dot (r 7) + 3 px
            if any(dist(bb, q) < dist(bb, P) + 6 for k, q in pins.items() if k != key and k != "csejte_manor"): continue
            if any(inter(pad, o) for o in others): continue
            vh = int(VAH[max(0, bb[1]):bb[3], max(0, bb[0]):bb[2]].sum())
            score = vh * 10 + dist(bb, P) + (0 if side in ("N", "E", "W") else 5)
            if best is None or score < best[0]: best = (score, im, (x, y), bb, side, align, gap, vh)
    return best
out = {}
cz = place("csejte", [("Csejte", FONT_SC, L1), ("today Čachtice, Slovakia", FONT_IT, L2)], [])
bz = place("bytca", [("Bytča", FONT_SC, L1), ("Slovakia", FONT_IT, L2)], [cz[3]])
# Vah label: italic, along the river between Trencsen and Bytca, clear of everything; rotated to local direction
vmask = Image.new("L", (W, H), 0)
cands = []
for s in segs:
    for i in range(len(s) - 6):
        (xa, ya), (xb, yb) = s[i], s[i + 6]; cx, cy = (xa + xb) / 2, (ya + yb) / 2
        if 420 < cy < 760 and 300 < cx < 900: cands.append((cx, cy, math.degrees(math.atan2(-(yb - ya), xb - xa))))
fv = ImageFont.truetype(FONT_IT, LV); best_v = None
for cx, cy, ang in cands[::3]:
    a = ang if -90 <= ang <= 90 else ang - 180 * np.sign(ang); a = max(-35, min(35, a))
    m = text_mask("Váh", fv).rotate(a, expand=True, resample=Image.BICUBIC)
    for off in (26, -26, 34, -34):                                         # beside the river, not on it
        nx, ny = -math.sin(math.radians(a)), -math.cos(math.radians(a))
        x, y = int(cx + nx * off - m.width / 2), int(cy + ny * off - m.height / 2); bb = tight(m, x, y)
        pad = [bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10]
        if inter(pad, MED) or inter(pad, CMP) or inter(pad, cz[3]) or inter(pad, bz[3]): continue
        if not (TS[0] <= bb[0] and bb[2] <= TS[2]): continue
        vh = int(VAH[bb[1]:bb[3], bb[0]:bb[2]].sum()); sc = vh * 10 + abs(cy - 600) * 0.1
        if best_v is None or sc < best_v[0]: best_v = (sc, m, (x, y), bb, round(a, 1), vh, (round(cx), round(cy)))
base = Image.open(f"{RP}/img_v2/bathory_b03v2_9x16_ref_notext_v2.png").convert("RGB")
def comp(img, m, xy, alpha):
    a = Image.new("L", img.size, 0); a.paste(m, xy)
    halo = a.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2.0)).point(lambda v: int(min(255, v * 1.4) * 0.8 * alpha))
    img.paste(Image.new("RGB", img.size, HALO), (0, 0), halo); img.paste(Image.new("RGB", img.size, INK), (0, 0), a.point(lambda v: int(v * alpha)))
P = base.copy(); d = ImageDraw.Draw(P)
for k in ("csejte", "bytca"):
    q = pins[k]; d.ellipse([q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7], fill=(160, 30, 24), outline=INK, width=2)
comp(P, cz[1], cz[2], 1.0); comp(P, bz[1], bz[2], 1.0); comp(P, best_v[1], best_v[2], 0.60)
P.save(f"{HERE}/b03v2_labels_v2_proof_1080x1920.png")
Z = P.copy(); dz = ImageDraw.Draw(Z)
for r, c in [(TS, (0, 200, 0)), (MED, (220, 0, 220)), (CMP, (230, 0, 0))]: dz.rectangle(r, outline=c, width=3)
for bb in (cz[3], bz[3], best_v[3]): dz.rectangle(bb, outline=(0, 90, 255), width=3); dz.rectangle([bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10], outline=(120, 170, 255), width=1)
Z.save(f"{HERE}/b03v2_labels_v2_zones_1080x1920.png")
S = P.resize((360, 640), Image.LANCZOS); S.save(f"{HERE}/b03v2_labels_v2_phone_360x640.png")
S.crop((0, 300, 360, 420)).resize((1080, 360), Image.NEAREST).save(f"{HERE}/b03v2_phone_crop_csejte_x3.png")
S.crop((180, 80, 360, 160)).resize((720, 320), Image.NEAREST).save(f"{HERE}/b03v2_phone_crop_bytca_x4.png")
def xh(fp, s): f = ImageFont.truetype(fp, s); return f.getbbox("x")[3] - f.getbbox("x")[1], f.getbbox("H")[3] - f.getbbox("H")[1]
rep = dict(csejte=dict(bbox=cz[3], side=cz[4], align=cz[5], gap=cz[6], vah_px=cz[7], origin=cz[2]),
           bytca=dict(bbox=bz[3], side=bz[4], align=bz[5], gap=bz[6], vah_px=bz[7], origin=bz[2]),
           vah=dict(bbox=best_v[3], angle=best_v[4], vah_px=best_v[5], river_pt=best_v[6]),
           sizes_1080=dict(L1=L1, L2=L2, LV=LV), cap_x_heights_at_360={"L1 SC cap": xh(FONT_SC, L1)[1] / 3, "L2 it x": xh(FONT_IT, L2)[0] / 3, "L2 it cap": xh(FONT_IT, L2)[1] / 3, "Vah it x": xh(FONT_IT, LV)[0] / 3},
           dist_to_compass=dict(csejte=dist(cz[3], ((CMP[0]+CMP[2])/2, (CMP[1]+CMP[3])/2)), ), )
rep = json.loads(json.dumps(rep, default=lambda o: [int(v) for v in o] if isinstance(o, (tuple, list)) else float(o)))
json.dump(rep, open(f"{HERE}/label_layout_v2.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(rep, ensure_ascii=False))
