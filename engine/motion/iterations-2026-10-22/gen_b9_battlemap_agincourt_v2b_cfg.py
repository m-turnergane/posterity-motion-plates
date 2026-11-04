#!/usr/bin/env python3
"""config generator: Agincourt battle-map v2 (battlemap_v2.py).  Writes configs/<name>.json, refuses to overwrite.
Unit keys: [t, x, y, w, d, angle_deg, alpha, funnel, bulge, disorder] in plate px (1080x1920); +front = 'front' sign (French +1 south, English -1 north)."""
import json, os, sys
NAME = os.environ.get("B9V2_NAME", "b9_battlemap_agincourt_poc_v2b")
OUT = os.environ.get("B9V2_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs", NAME + ".json")
R = lambda k: [round(v, 3) if isinstance(v, float) else v for v in k]
def U(id_, kind, front, keys, banners=(), **kw): return dict(id=id_, kind=kind, front=front, keys=[R(k) for k in keys], banners=[list(b) for b in banners], **kw)
def appear(t, x, y, w, d, ang=0.0, s=0.4): return [[t, x, y, w, d, ang, 0.0], [t + s, x, y, w, d, ang, 1.0]]
def ban(us, vs, des, ph=0.0): return [[u, v, d_, round(ph + 0.37 * i, 3)] for i, (u, v, d_) in enumerate(zip(us, vs, des))]
FRD = ["fr_lis", "fr_pennon", "fr_gules", "fr_lis", "fr_pennon", "fr_lis"]
units = []
# ---------------- French (front = south)
units.append(U("fr_rear", "fr_cav", 1, appear(0.70, 535, 762, 320, 70) + [[9.0, 535, 770, 320, 70, 0, 1.0]],
               ban([-0.6, -0.2, 0.2, 0.6], [-0.2, 0.1, -0.1, 0.15], ["fr_pennon", "fr_lis", "fr_gules", "fr_pennon"]), seed=21, note="rearguard, largely mounted"))
units.append(U("fr_main_missile", "fr_missile", 1, appear(0.78, 535, 928, 300, 18) + [[3.6, 535, 928, 300, 18, 0, 1.0], [7.0, 536, 1040, 290, 18, 0, 1.0]], seed=22))
units.append(U("fr_main", "fr_inf", 1, appear(0.82, 535, 988, 360, 88) + [[3.6, 535, 988, 360, 88, 0, 1], [7.0, 536, 1098, 340, 94, 0, 1, -0.05, 0, 0.3], [8.6, 537, 1118, 330, 98, 0, 1, -0.08, 0, 0.5]],
               ban([-0.75, -0.38, 0.0, 0.38, 0.75], [-0.3, 0.05, -0.2, 0.1, -0.3], FRD), seed=23, note="main battle, dismounted men-at-arms"))
units.append(U("fr_van_missile", "fr_missile", 1, appear(0.90, 535, 1130, 300, 18) + [[3.6, 535, 1130, 300, 18, 0, 1], [5.6, 536, 1210, 280, 18, 0, 0.9], [6.6, 537, 1236, 270, 18, 0, 0.0]], seed=24,
               note="crossbows/archers behind the vanguard, squeezed out"))
units.append(U("fr_van", "fr_inf", 1, appear(0.95, 535, 1212, 330, 120) + [
    [3.6, 535, 1212, 330, 120, 0, 1, 0, 0, 0],
    [4.6, 535, 1250, 316, 124, 0, 1, -0.08, 0, 0.55],      # recoiling horses ride through
    [5.4, 536, 1282, 296, 132, 0, 1, -0.14, 4, 0.45],
    [6.4, 538, 1330, 256, 150, 0, 1, -0.22, 6, 0.6],       # funnelled, contact
    [7.4, 538, 1338, 248, 152, 0, 1, -0.24, 30, 0.9],      # presses into the bent centre: jam
    [8.6, 539, 1342, 236, 156, 0, 1, -0.24, 32, 1.0]],     # flanks crushed in by the archers
    ban([-0.7, -0.42, -0.14, 0.14, 0.42, 0.7], [-0.45, -0.1, -0.5, -0.2, -0.05, -0.45], FRD), seed=25, note="vanguard: dismounted men-at-arms"))
for sg, nm in ((-1, "w"), (1, "e")):
    units.append(U(f"fr_wing_{nm}", "fr_inf", 1, appear(1.05, 535 + sg * 178, 1228, 36, 72) + [[3.6, 535 + sg * 178, 1228, 36, 72, 0, 1], [5.4, 535 + sg * 150, 1290, 34, 70, -sg * 8, 1, 0, 0, 0.4],
                   [6.6, 535 + sg * 132, 1322, 30, 66, -sg * 12, 1, 0, 0, 0.8], [7.6, 535 + sg * 128, 1318, 28, 60, -sg * 14, 0.0, 0, 0, 1.0]],
                   [[0.0, -0.3, "fr_pennon" if nm == "w" else "fr_gules", 0.2 * sg]], seed=26 + (sg > 0), note="vanguard wing (crowded into the van)"))
    x0 = 535 + sg * 165
    units.append(U(f"fr_horse_{nm}", "fr_cav", 1, appear(1.12, x0, 1300, 66, 32) + [
        [3.0, x0, 1300, 66, 32, 0, 1], [3.85, 540 + sg * 150, 1366, 56, 32, -sg * 6, 1, 0, 0, 0.3],   # charge late and thin
        [4.2, 540 + sg * 152, 1360, 50, 34, sg * 18, 0.95, 0, 0, 1.0],                                # fail on the stakes
        [5.0, 540 + sg * 118, 1200, 46, 30, sg * 160, 0.85, 0, 0, 0.9],                               # recoil through their own vanguard
        [5.6, 540 + sg * 108, 1120, 40, 26, sg * 175, 0.0, 0, 0, 0.8]],
        [[0.0, -0.2, "fr_pennon", 0.5]], seed=28 + (sg > 0), note="mounted horn"))
# ---------------- English (front = north)
LY0, LY1 = 1500, 1425
divs = [("en_camoys", 455, 12), ("en_henry", 540, 0), ("en_york", 625, -12)]
for id_, x, ang in divs:
    w = 84 if id_ == "en_henry" else 76
    if id_ == "en_henry":
        k = appear(1.32, x, LY0, w, 18) + [[1.75, x, LY0, w, 18, 0, 1], [2.4, x, LY1, w, 18, 0, 1], [6.6, x, LY1, w, 18, 0, 1, 0, 0, 0.15], [7.4, x, LY1 + 30, w, 18, 0, 1, 0, -5, 0.5], [9.0, x, LY1 + 32, w, 18, 0, 1, 0, -5, 0.3]]
        b = [[-0.86, 0.0, "en_royal", 0.1], [0.62, 0.0, "en_george", 0.6]]
    else:
        dx = 3 if x < 540 else -3
        k = appear(1.28 if x < 540 else 1.36, x, LY0, w, 18) + [[1.75, x, LY0, w, 18, 0, 1], [2.4, x, LY1, w, 18, 0, 1], [6.6, x, LY1, w, 18, 0, 1], [7.4, x + dx, LY1 + 12, w, 18, ang, 1, 0, 0, 0.3], [9.0, x + dx, LY1 + 12, w, 18, ang, 1, 0, 0, 0.2]]
        b = [[0.0, 0.0, "en_george", 0.3 if x < 540 else 0.8]]
    units.append(U(id_, "en_maa", -1, k, b, seed=40 + len(units)))
for sg, nm in ((-1, "w"), (1, "e")):
    x = 540 + sg * 148
    units.append(U(f"en_arch_{nm}", "en_arch", -1, appear(1.2, x, LY0 - 12, 58, 54) + [[1.75, x, LY0 - 12, 58, 54, 0, 1], [2.4, x, LY1 - 20, 58, 54, 0, 1],
                   [7.4, x, LY1 - 20, 58, 54, 0, 1], [8.0, 540 + sg * 160, 1384, 56, 50, -sg * 30, 1], [8.6, 540 + sg * 158, 1360, 54, 48, -sg * 42, 1]],
                   shape="wedge", seed=50 + (sg > 0), note="archers on the flank behind the stakes; wrap the French flank"))
stakes = []
for sg, nm in ((-1, "w"), (1, "e")):
    xa, xb = 540 + sg * 186, 540 + sg * 112
    stakes.append(dict(id=f"stk_{nm}0", points=[[xa, 1458], [xb, 1456]], t_on=1.45, t_off=1.78, seed=5 + (sg > 0)))
    stakes.append(dict(id=f"stk_{nm}1", points=[[xa - sg * 2, 1382], [(xa + xb) / 2, 1379], [xb, 1384]], t_on=2.32, seed=7 + (sg > 0)))
EN = dict(wet_color=[50, 8, 4], dry_color=[140, 34, 24]); FR = dict(wet_color=[10, 14, 44], dry_color=[40, 52, 110])
arrows = []
for x in (455, 540, 625): arrows.append(dict(points=[[x, 1492], [x, 1462], [x, 1440]], t0=1.75, t1=2.2, width=4.6, head_px=16, ink=EN, fade_at=3.0, note="English advance"))
for sg in (-1, 1):
    arrows.append(dict(points=[[540 + sg * 166, 1288], [540 + sg * 160, 1322], [540 + sg * 150, 1352]], t0=3.0, t1=3.5, width=3.4, head_px=14, ink=FR, fade_at=4.3, note="horns charge"))
    arrows.append(dict(points=[[540 + sg * 150, 1352], [540 + sg * 134, 1290], [540 + sg * 118, 1220], [540 + sg * 108, 1150]], t0=4.25, t1=4.95, width=3.8, head_px=15, ink=FR, dash=[13, 8], fade_at=5.9, note="horses recoil through the vanguard"))
    arrows.append(dict(points=[[540 + sg * 214, 1150], [540 + sg * 200, 1236], [540 + sg * 150, 1310]], t0=4.9, t1=5.8, width=5.6, head_px=20, ink=FR, fade_at=6.7, note="vanguard funnelled by the woods"))
    arrows.append(dict(points=[[540 + sg * 150, 1418], [540 + sg * 170, 1396], [540 + sg * 166, 1360]], t0=7.45, t1=7.95, width=4.6, head_px=16, ink=EN, fade_at=9.2, note="archers wrap the flank"))
volleys = []
def vol(t0, sg, dst, **kw): volleys.append(dict(t0=t0, src=[540 + sg * 148, 1392], dst=dst, side=-1 if sg < 0 else 1, **kw))
for sg in (-1, 1):
    vol(2.75, sg, [540 + sg * 60, 1215]); vol(3.2, sg, [540 + sg * 160, 1302], n=5, bulge=0.45, spread_dst=12, hit_spread=[16, 8], hits=10)
    vol(3.65, sg, [540 + sg * 30, 1236]); vol(4.3, sg, [540 + sg * 75, 1258]); vol(5.0, sg, [540 + sg * 40, 1285]); vol(5.6, sg, [540 + sg * 80, 1300]); vol(6.2, sg, [540 + sg * 30, 1320])
    for t0 in (7.7, 8.1, 8.5):
        volleys.append(dict(t0=t0, src=[540 + sg * 160, 1372], dst=[540 + sg * 92, 1318], side=-1 if sg < 0 else 1, n=8, bulge=0.4, spread_src=8, spread_dst=14, hit_spread=[14, 22], hits=16))
labels = [dict(text="AZINCOURT", xy=[235, 585], size=58, t_on=0.0),
          dict(text="TRAMECOURT", xy=[860, 690], size=56, t_on=0.06),
          dict(text="MAISONCELLE", xy=[540, 1872], size=58, t_on=0.12),
          dict(text="Azincourt Wood", xy=[252, 1185], size=56, font="it", rot=90, t_on=0.18, tracking=0.03),
          dict(text="Tramecourt Wood", xy=[852, 1215], size=56, font="it", rot=-90, t_on=0.22, tracking=0.03),
          dict(text="towards Ruisseauville", xy=[540, 152], size=54, font="it", t_on=0.26, tracking=0.02)]
for L in labels: L["t_in"] = 0.42
cfg = dict(name=NAME, plate="batch9/plates/agincourt_map_plate_v1.png", out_dir="batch9", fps=30, duration=10.0, size=[720, 1280], seed=1415, cam_ss=2,
           engine="battlemap_v2b.py",
           notes="Agincourt 25 Oct 1415, traditional site, schematic (not an exact-spot claim). v2 beat sheet: 0-0.7 labels ink on empty map; 0.7-1.7 deploy; 1.75-2.4 English advance & re-plant stakes; "
                 "2.75-6.2 volleys; 3.0-4.2 horns charge, fail on stakes; 4.2-5.6 recoil through own vanguard; 4.6-6.4 vanguard funnels; 6.45 marker; 6.6-7.4 centre bends back ~30 px, wings +-12 deg; "
                 "7.4-8.6 archers wrap the flanks with flank volleys; 8.6-10 pull back.",
           fonts=dict(sc="/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf",
                      it="/usr/share/fonts/truetype/sand-box/google/EB Garamond/EBGaramond-Italic-VariableFont_wght.ttf"),
           banners=dict(en_george=dict(field=[244, 238, 224], cross=[184, 30, 24], tail="swallow", w=30, h=20, pole=40, ink=[40, 16, 10]),
                        en_royal=dict(field=[44, 62, 146], quarterly=[[44, 62, 146], [176, 32, 26]], charge=[230, 190, 74], tail="square", w=28, h=20, pole=42, ink=[30, 14, 10]),
                        fr_lis=dict(field=[52, 78, 168], dots=[232, 192, 72], tail="square", w=26, h=17, pole=34, ink=[16, 18, 36]),
                        fr_pennon=dict(field=[228, 188, 70], band=[52, 78, 168], tail="pennon", w=32, h=14, pole=34, ink=[30, 24, 30]),
                        fr_gules=dict(field=[176, 40, 32], pale=[232, 192, 72], tail="swallow", w=26, h=17, pole=34, ink=[30, 14, 12])),
           units=units, stakes=stakes, arrows=arrows, volleys=volleys, labels=labels,
           marker=dict(icon="crossed_swords", xy=[540, 1340], t_on=6.45, radius=52, backing=dict()),
           camera=[[0.0, 540, 960, 1.0], [0.7, 540, 960, 1.0], [1.7, 540, 1110, 1.14], [2.6, 540, 1350, 1.55], [3.9, 540, 1340, 1.8], [5.0, 540, 1255, 1.42],
                   [6.4, 540, 1330, 1.62], [7.3, 540, 1378, 2.12], [8.5, 540, 1352, 1.86], [10.0, 540, 1262, 1.42]],
           order=["labels", "stakes", "units:fr_rear,fr_main_missile,fr_main,fr_van_missile,fr_van,fr_wing_w,fr_wing_e,en_arch_w,en_arch_e,en_camoys,en_york,en_henry,fr_horse_w,fr_horse_e",
                  "arrows", "volleys", "marker"])
if os.path.exists(OUT): sys.exit(f"refusing to overwrite {OUT}")
json.dump(cfg, open(OUT, "x"), indent=1); print("wrote", OUT)
