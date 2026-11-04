import json
def U(id_, side, kind, keys, banners=(), **kw):
    return dict(id=id_, side=side, kind=kind, keys=[[round(v, 3) if isinstance(v, float) else v for v in k] for k in keys], banners=[list(b) for b in banners], **kw)
def appear(t, x, y, w, d, ang=0, dy=-8, s=0.35):           # ink-in: fades up while settling into place
    return [[t, x, y + dy, w, d, ang, 0.0], [t + s, x, y, w, d, ang, 1.0]]
units = []
# ---------------- French (south-facing; front = +y) ----------------
units.append(U("fr_rear", "french", "cav", appear(1.00, 535, 760, 330, 74) , [(-110, -37, "fr_pennon"), (110, -37, "fr_pennon")], front=1, companies=2, note="rearguard, mostly mounted"))
units.append(U("fr_main_missile", "french", "missile", appear(1.10, 535, 925, 300, 12), front=1, note="archers/crossbowmen behind the main battle"))
units.append(U("fr_main", "french", "inf",
               appear(1.15, 535, 985, 360, 88) + [[5.3, 535, 985, 360, 88, 0, 1.0], [8.0, 535, 1060, 330, 92, 0, 1.0]],
               [(-120, -44, "fr_lis"), (0, -44, "fr_lis"), (120, -44, "fr_lis")], companies=3, note="main battle, dismounted, a bowshot behind the vanguard"))
units.append(U("fr_van_missile", "french", "missile",
               appear(1.30, 535, 1126, 270, 13) + [[5.3, 535, 1126, 270, 13, 0, 1.0], [7.6, 538, 1224, 200, 14, 0, 1.0], [8.4, 538, 1238, 200, 14, 0, 1.0]], front=1,
               note="archers/crossbowmen behind the vanguard men-at-arms"))
van = appear(1.30, 535, 1210, 330, 120) + [[4.75, 535, 1210, 330, 120, 0, 1.0], [5.05, 533, 1206, 322, 124, -1.2, 1.0], [5.35, 535, 1210, 326, 122, 0.8, 1.0],
       [7.6, 538, 1327, 232, 150, 0, 1.0], [8.4, 538, 1341, 226, 152, 0, 1.0]]
units.append(U("fr_van", "french", "inf", van, [(-110, -60, "fr_lis"), (0, -60, "fr_lis"), (110, -60, "fr_lis")], companies=3, note="vanguard, dismounted, large and deep"))
for nm, x0, x1 in (("fr_wing_w", 335, 403), ("fr_wing_e", 735, 673)):
    units.append(U(nm, "french", "inf", appear(1.45, x0, 1225, 34, 70) + [[5.3, x0, 1225, 34, 70, 0, 1.0], [7.6, x1, 1318, 30, 92, 0, 1.0], [8.4, x1, 1332, 30, 92, 0, 1.0]],
                   note="small dismounted wing beside the vanguard"))
# ---------------- English (north-facing; front = -y) ----------------
eng = [("en_camoys", 454, 452, 66, 74, "left (west): Camoys"), ("en_henry", 538, 545, 72, 82, "centre: Henry"), ("en_york", 622, 638, 66, 74, "right (east): York")]
for nm, x0, x1, w0, w1, note in eng:
    units.append(U(nm, "english", "inf", appear(1.70, x0, 1500, w0, 12, dy=8) + [[2.45, x0, 1500, w0, 12, 0, 1.0], [3.45, x1, 1410, w1, 12, 0, 1.0],
                   [7.95, x1, 1410, w1, 12, 0, 1.0], [8.45, x1 + (x1 - 545) * -0.04, 1424, w1, 13, 0, 1.0]],
                   [(0, -6, "en_george")], mark_dx=4.2, mark_dy=3.0, note=note + ", men-at-arms ~4 deep"))
for nm, x0, x1, xs, ang in (("en_arch_w", 403, 383, 418, 50), ("en_arch_e", 687, 707, 668, -50)):
    units.append(U(nm, "english", "arch", appear(1.85, x0, 1494, 36, 28, dy=8) + [[2.45, x0, 1494, 36, 28, 0, 1.0], [3.45, x1, 1402, 42, 30, 0, 1.0],
                   [8.3, x1, 1402, 42, 30, 0, 1.0], [9.2, xs, 1366, 40, 30, ang, 1.0]], front=-1, ink=[150, 30, 24], note="archers on the flank, behind stakes; swing in at the end"))
# ---------------- French mounted horns (late, understrength; charge, break on the stakes, recoil through their own vanguard) ----------------
for nm, x0, xh, xr1, xr2 in (("fr_horse_w", 352, 376, 420, 452), ("fr_horse_e", 720, 698, 652, 620)):
    units.append(U(nm, "french", "cav", appear(1.45, x0, 1302, 44, 24) + [[3.95, x0, 1302, 44, 24, 0, 1.0], [4.55, xh, 1366, 40, 22, 0, 1.0],
                   [4.75, xh, 1360, 40, 22, 30 if x0 < 500 else -30, 1.0], [5.05, (xh + xr1) / 2, 1300, 38, 22, 150 if x0 < 500 else -150, 1.0],
                   [5.45, xr1, 1200, 36, 22, 180 if x0 < 500 else -180, 0.9], [5.85, xr2, 1110, 34, 20, 180 if x0 < 500 else -180, 0.0]],
                   [(0, -12, "fr_pennon")], front=1, mark_dx=9.0, mark_dy=8.0, note="mounted horn, slightly forward; thin = understrength"))
stakes = [dict(id="stk_w0", a=[383, 1474], b=[424, 1471], t_on=2.0, t_off=2.35, width=2.2, length=14), dict(id="stk_e0", a=[666, 1471], b=[707, 1474], t_on=2.05, t_off=2.35, width=2.2, length=14),
          dict(id="stk_w1", a=[360, 1381], b=[408, 1378], t_on=3.5, seed=5, width=2.2, length=14), dict(id="stk_e1", a=[682, 1378], b=[730, 1381], t_on=3.55, seed=6, width=2.2, length=14)]
EN = dict(wet_color=[46, 10, 6], dry_color=[150, 44, 30]); FR = dict(wet_color=[10, 16, 50], dry_color=[44, 64, 132])
arrows = []
for x0, x1 in ((454, 452), (538, 545), (622, 638)):
    arrows.append(dict(points=[[x0, 1488], [x1, 1452], [x1, 1428]], t0=2.45, t1=3.0, width=3.4, head_px=13, ink=EN, fade_at=3.9, note="English advance"))
for x0, x1, xm in ((352, 372, 360), (720, 700, 712)):
    arrows.append(dict(points=[[x0, 1318], [xm, 1340], [x1, 1366]], t0=3.95, t1=4.35, width=3.6, head_px=13, ink=FR, fade_at=5.0, note="cavalry charge"))
arrows.append(dict(points=[[388, 1352], [420, 1290], [440, 1200], [452, 1140]], t0=4.7, t1=5.3, width=3.0, head_px=12, ink=FR, dash=[12, 8], fade_at=6.0, note="horses recoil"))
arrows.append(dict(points=[[686, 1352], [652, 1290], [632, 1200], [620, 1140]], t0=4.7, t1=5.3, width=3.0, head_px=12, ink=FR, dash=[12, 8], fade_at=6.0, note="horses recoil"))
arrows.append(dict(points=[[322, 1150], [338, 1240], [384, 1318]], t0=5.35, t1=6.3, width=5.0, head_px=19, ink=FR, fade_at=7.6, note="vanguard advance, funnelled by the woods (west side)"))
arrows.append(dict(points=[[752, 1150], [738, 1240], [690, 1318]], t0=5.4, t1=6.35, width=5.0, head_px=19, ink=FR, fade_at=7.6, note="vanguard advance, funnelled by the woods (east side)"))
for x0, x1, x2 in ((372, 384, 418), (718, 706, 670)):
    arrows.append(dict(points=[[x0, 1440], [x1, 1405], [x2, 1360]], t0=8.3, t1=8.85, width=3.4, head_px=13, ink=EN, note="archers swing in"))
volleys = []
for t0, dw, de, n in ((3.75, [470, 1282], [600, 1282], 9), (4.05, [372, 1330], [700, 1330], 7), (5.7, [480, 1300], [600, 1300], 9),
                      (6.4, [470, 1340], [610, 1340], 9), (7.1, [480, 1375], [600, 1375], 8)):
    volleys.append(dict(src=[383, 1404], dst=dw, t0=t0, n=n, side=1))
    volleys.append(dict(src=[707, 1404], dst=de, t0=t0 + 0.06, n=n, side=-1))
labels = [dict(text="AZINCOURT", xy=[150, 610], size=40, hide_zoom=[1.15, 1.3]), dict(text="TRAMECOURT", xy=[910, 1000], size=36, hide_zoom=[1.15, 1.3]),
          dict(text="MAISONCELLE", xy=[540, 1882], size=40, t_on=0.45),
          dict(text="Azincourt Wood", xy=[118, 1150], size=36, rot=90, font="it", tracking=0.08, hide_zoom=[1.2, 1.35]),
          dict(text="Tramecourt Wood", xy=[930, 1420], size=36, rot=90, font="it", tracking=0.08, hide_zoom=[1.2, 1.35]),
          dict(text="towards Ruisseauville", xy=[540, 128], size=28, font="it", tracking=0.06, op=0.75, hide_zoom=[1.15, 1.3])]
import numpy as _np
TW = [(0, 0), (1.0, 0.3), (2.45, 1.6), (8.3, 7.7), (10, 10)]          # time warp applied to the beat sheet (compress the deploy)
def tw(t): return round(float(_np.interp(t, [a for a, _ in TW], [b_ for _, b_ in TW])), 3)
for u in units:
    u["keys"] = [[tw(k[0])] + k[1:] for k in u["keys"]]
for s_ in stakes:
    s_["t_on"] = tw(s_["t_on"]); s_["t_off"] = tw(s_["t_off"]) if "t_off" in s_ else 1e9
for a_ in arrows:
    for k in ("t0", "t1", "fade_at"):
        if a_.get(k) is not None: a_[k] = tw(a_[k])
for v in volleys: v["t0"] = tw(v["t0"])
for i, L in enumerate(labels): L["t_on"] = round(0.0 + 0.08 * i, 3); L["t_in"] = 0.5
cfg = dict(name="b9_battlemap_agincourt_poc_v1", plate="batch9/plates/agincourt_map_plate_v1.png", out_dir="batch9", fps=30, duration=10.0, size=[720, 1280], seed=1415, cam_ss=2,
           notes="Agincourt 25 Oct 1415, traditional site, schematic (not an exact-spot claim). Units: keys [t, x, y, w, d, angle_deg, alpha] in plate px (1080x1920), eased per segment. "
                 "Camera keys [t, cx, cy, zoom], zoom 1 = whole plate; monotone-cubic through keys. Archivist corrections: edit units/arrows/volleys here.",
           fonts=dict(sc="/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf",
                      it="/usr/share/fonts/truetype/sand-box/google/EB Garamond/EBGaramond-Italic-VariableFont_wght.ttf"),
           sides=dict(english=dict(fill=[178, 46, 36], fill_arch=[236, 226, 208], fill_cav=[180, 40, 32], ink=[48, 16, 10]),
                      french=dict(fill=[56, 80, 150], fill_arch=[200, 206, 222], fill_cav=[208, 168, 74], ink=[16, 20, 46])),
           banners=dict(en_george=dict(field=[242, 236, 222], cross=[186, 32, 26], tail="swallow", w=19, h=12, pole=24, ink=[40, 18, 12]),
                        fr_lis=dict(field=[44, 68, 150], dots=[226, 186, 70], tail="square", w=17, h=13, pole=24, ink=[18, 20, 40]),
                        fr_pennon=dict(field=[222, 182, 68], band=[44, 68, 150], tail="pennon", w=22, h=11, pole=22, ink=[30, 24, 30])),
           units=units, stakes=stakes, arrows=arrows, volleys=volleys, labels=labels,
           marker=dict(icon="crossed_swords", xy=[540, 1388], t_on=tw(7.95), radius=60),
           camera=[[0.0, 540, 960, 1.06], [0.9, 540, 1000, 1.0], [tw(2.2), 540, 1150, 1.12], [tw(3.3), 540, 1320, 1.4], [tw(4.45), 540, 1340, 1.9], [tw(5.4), 540, 1270, 1.4],
                   [tw(7.0), 540, 1320, 1.6], [tw(8.1), 540, 1310, 2.3], [tw(8.9), 540, 1310, 2.3], [10.0, 540, 1290, 1.6]],
           order=["labels", "stakes", "units", "arrows", "volleys", "marker"])
p = "/workspace/posterity/motion/iterations-2026-10-22/configs/b9_battlemap_agincourt_poc_v1.json"
import os
if os.path.exists(p) and not os.environ.get("B9_SCRATCH"): raise SystemExit("exists")
json.dump(cfg, open(os.environ.get("B9_OUT", p), "w"), indent=1)
