"""Jianwen v2b -- REAL fx settings for the landed plates (K01-K05, 941x1672 / K05 941x1671) + smoke_v2 layer + per-plate grade + framing.
Layered ON TOP of fx_jianwen_v2.py (md5-locked, NOT edited): this module builds a new SPECS dict ({templates..., real k01-k05}) and rebinds
fx_jianwen_v2.SPECS in memory, so PlateFX (which reads its module global) uses it. K06-K11 real since owner 12:13; K12-K19 + outro real since owner 12:58 (Rough v1). LEGEND removed (owner 12:59).
smoke_v2 (/workspace/posterity/engine-rnd/smoke/smoke_v2.py, locked) is imported BY PATH and md5-checked; nothing under engine-rnd/ is edited or copied.
All coordinates are PLATE PIXELS (x0, y0, x1, y1) unless given as dict(frac=[x0, y0, x1, y1]) (fractions of the plate).
"""
import hashlib, importlib.util
from pathlib import Path
import numpy as np
import fx_jianwen_v2 as V2

def _md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
V2_MD5 = "6c4160305cd8e6ef9f2b09c11b5780a6"; assert _md5(V2.__file__) == V2_MD5, "fx_jianwen_v2.py changed"
SMOKE_V2 = "/workspace/posterity/engine-rnd/smoke/smoke_v2.py"; SMOKE_V2_MD5 = "80bb28695757f7568b005e8ba8327bde"
assert _md5(SMOKE_V2) == SMOKE_V2_MD5, "locked smoke_v2.py changed"
_sp = importlib.util.spec_from_file_location("smoke_v2_locked", SMOKE_V2); SM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SM)

overlay, plate_key = V2.overlay, V2.plate_key
class PlateFX(V2.PlateFX):
    """owner 11:55: 'glow pulse (flame shapes static)' -> the locked candle flame_warp is dropped (every flame keeps its painted shape;
    flicker/glow/spill unchanged). A spec may opt back in with warp_candles=True."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        sp = V2.SPECS.get(self.key, {})
        if not sp.get("warp_candles", False):
            for s in self.srcs: s.pop("warp", None)
        fm = sp.get("flick_mult", 1.0)   # owner 12:58: K18's guttering stub flickers harder (amplitude only; same frequencies -> no strobe)
        if fm != 1.0:
            for s in self.srcs:
                if s["kind"] == "candle": s["F"]["amps"] = [a * fm for a in s["F"]["amps"]]; s["F"]["nz"] = s["F"]["nz"] * fm
        # FREEZE rects (owner 12:58: K19's blank page, the outro's baked lettering): after all fx the region is put back to the PLATE pixels
        # exactly (mask = 1 inside the rect, feathered OUTSIDE it only) -> zero pixel change there before the global grade + push.
        self.freeze = None
        if sp.get("freeze"):
            fe = int(sp.get("freeze_feather", 24)); hard = V2._rectmask((self.H, self.W), sp["freeze"], 0)
            k = np.ones((2 * fe + 1, 2 * fe + 1), np.uint8); import cv2 as _cv
            soft = _cv.GaussianBlur(_cv.dilate(hard, k), (0, 0), fe / 2.0); self.freeze = np.maximum(hard, np.clip(soft, 0, 1)).astype(np.float32)[..., None]
            self.freeze_hard = hard > 0.5
    def render(self, t, u=0.0, want_disp=False):
        r = super().render(t, u, want_disp)
        if self.freeze is None: return r
        out, d = (r if want_disp else (r, None))
        out = np.clip(np.rint(out.astype(np.float32) * (1 - self.freeze) + self.Pf * self.freeze), 0, 255).astype(np.uint8)
        out[self.freeze_hard] = self.P[self.freeze_hard]
        return (out, d) if want_disp else out
WARM_HAZE, COOL_MIST = V2.WARM_HAZE, V2.COOL_MIST
def _pad(r, p=3): return (max(0, r[0] - p), max(0, r[1] - p), r[2] + p, r[3] + p)

# ---------------------------------------------------------------------------------------------- title (owner 11:55: check against faces)
# K02's face sits at 20-40 % of frame height (eyebrows ~23 %), right in the old 25-40 % band, so the title moves UP into the dark sky (K01) /
# dark wall + hat crown (K02). Strike band = 14 % H centred on TITLE_TOP_PCT.
TITLE_TOP_PCT = 10.0   # owner 12:58 (Vellum 1): title to 10 %; verified clear of the K02 hat ornament for the whole push (qc/v2-rough-v1/)
def _title_band(scale=1.0): return dict(frac=[0.0, max(0.0, (TITLE_TOP_PCT - 7.5) / 100 * scale), 1.0, (TITLE_TOP_PCT + 7.5) / 100])

# ---------------------------------------------------------------------------------------------- framing (overrides the grid placeholders)
# anchor = StablePush target (frame fractions of the slot's source frame); crop = frac/centre of the plate (9:16 kept)
FRAMING = {
 "S01":  dict(anchor=(0.62, 0.58)),                                   # push to the yellow-draped coffin
 "S02A": dict(anchor=(0.47, 0.30)),                                   # toward Zhu Di's face (K02)
 "S02B": dict(anchor=(0.56, 0.37), crop=dict(frac=0.81, center=[0.405, 0.405])),   # crop (0,0)-(762,1354): candle at left edge + face; guard cut; 762 px >= 756
 "S03":  dict(anchor=(0.62, 0.32)),                                   # drift founder -> grandson
 "S04":  dict(anchor=(0.63, 0.29)),                                   # push up to Zhu Di's face
 "S05":  dict(anchor=(0.53, 0.30)),                                   # push from the edict up to Zhu Di
 "S09":  dict(anchor=(0.45, 0.50), crop=dict(frac=0.82, center=[0.469, 0.50])),    # crop (55,151)-(827,1522): Zhu Di at the grave head + coffin; 772 px wide
 "S06":  dict(anchor=(0.695, 0.38)),                                 # owner 12:13: push centred on the GATE (arch ~(655,640) plate px), away from the siege frames
 "S07":  dict(anchor=(0.50, 0.45)),                                  # commander + the opening gate leaves
 "S08":  dict(anchor=(0.55, 0.52)),                                  # the bearers + coffin under the burning roof
 "S10":  dict(anchor=(0.60, 0.40)),                                  # candle + window fire over the empty bed
 "S11":  dict(anchor=(0.50, 0.50)),                                  # carver / brazier, Yongle in the hall
 "S12":  dict(anchor=(0.40, 0.58)),                                  # the monk on the path
 # owner 12:58 (Rough v1): K12-K19 + outro
 "S13":  dict(anchor=(0.45, 0.40)),                                  # Yongle hands Hu Ying the sealed orders under the candle stand
 "S14":  dict(anchor=(0.40, 0.32)),                                  # Hu Ying under the eave lanterns
 "S15":  dict(anchor=(0.40, 0.45)),                                  # Hu Ying reading by the single candle
 "S16":  dict(anchor=(0.45, 0.38)),                                  # Hu Ying at the gate, torches
 "S17":  dict(anchor=(0.55, 0.40)),                                  # Yongle + the eunuch's oil lamp
 "S18":  dict(anchor=(0.55, 0.42)),                                  # the low candle between the two faces
 "S19":  dict(anchor=(0.45, 0.40)),                                  # Yongle by the guttering stub
 "S20":  dict(anchor=(0.55, 0.50)),                                  # the blank page + desk candle (page frozen; only the global push moves it)
 "OUTRO": dict(anchor=(0.50, 0.50), z_start=1.0, z_end=1.0),         # STATIC hold: the baked POSTERITY + tagline never move
}
# owner 12:59: the LEGEND label is REMOVED from the cut entirely (no LEGEND / DOCUMENTED / similar tag anywhere). The build's legend_layer
# returns None whenever enabled is False -> no sprite is ever built or composited (not a transparent layer: no text pixels at all).
LEGEND = dict(enabled=False)


# ---------------------------------------------------------------------------------------------- PlateFX specs (real for k01-k05)
K04_TORCH = [(281, 337, 289, 348), (443, 343, 460, 359), (91, 496, 98, 507), (205, 551, 221, 569), (6, 612, 26, 629), (96, 616, 102, 629), (32, 621, 47, 642),
             (165, 626, 176, 640), (184, 626, 192, 643), (58, 634, 65, 651), (214, 640, 221, 656), (204, 650, 217, 679), (218, 652, 240, 684), (188, 654, 197, 666),
             (106, 656, 114, 680), (260, 664, 285, 718), (237, 675, 247, 691), (363, 686, 372, 702), (286, 687, 298, 705), (159, 691, 169, 711), (255, 693, 260, 708),
             (407, 694, 417, 707), (319, 696, 332, 719), (301, 698, 316, 723), (392, 704, 405, 729), (188, 705, 199, 728), (403, 710, 411, 728), (429, 720, 457, 749),
             (240, 731, 257, 755), (459, 735, 468, 752), (255, 745, 286, 779), (317, 773, 332, 797), (307, 779, 315, 797), (243, 796, 252, 807), (376, 810, 418, 848),
             (36, 824, 46, 848), (53, 829, 60, 844), (264, 874, 273, 902), (247, 875, 261, 896), (155, 896, 172, 935), (146, 906, 160, 915), (145, 929, 160, 940),
             (15, 949, 27, 960), (343, 951, 383, 1001), (0, 952, 16, 976), (21, 964, 34, 983), (0, 978, 9, 988), (311, 1024, 318, 1031), (19, 1049, 29, 1058),
             (143, 1087, 153, 1109), (131, 1101, 145, 1137), (57, 1179, 65, 1194), (441, 1189, 451, 1198)]   # fire components (A >= 40) of the torch sea, Zhu Di excluded
K01_TORCH = [(16, 330, 87, 433), (79, 453, 119, 515), (11, 510, 40, 560), (900, 550, 941, 603), (849, 605, 877, 646)]
K05_TORCH = [(9, 464, 75, 577), (292, 571, 338, 654), (873, 418, 941, 520), (832, 558, 880, 660)]
K05_FIRE = [(0, 895, 95, 1015)]
# ---- K06-K11 (owner 12:13): fire_mask components (A >= 40) filtered BY REGION (reflections / gilt / bedding false positives dropped)
K06_TORCH = [(171, 636, 178, 649), (197, 643, 205, 655), (50, 671, 57, 681), (330, 680, 356, 705), (580, 689, 615, 751), (623, 694, 638, 748), (355, 695, 363, 704),
             (716, 699, 732, 706), (508, 707, 550, 750), (702, 708, 732, 753), (439, 713, 450, 724), (91, 735, 101, 755), (780, 735, 825, 777), (636, 737, 645, 749),
             (663, 739, 703, 774), (650, 745, 662, 753), (773, 760, 779, 776), (650, 762, 667, 771), (638, 767, 658, 779), (613, 775, 634, 789), (581, 781, 593, 788),
             (686, 787, 708, 803), (518, 791, 536, 803), (493, 801, 510, 820), (452, 802, 485, 828), (437, 807, 449, 826), (484, 813, 493, 826), (381, 821, 398, 836),
             (656, 835, 678, 852), (679, 836, 692, 860), (694, 843, 723, 864), (715, 886, 727, 904), (317, 887, 325, 898), (356, 887, 365, 896), (730, 888, 738, 900),
             (337, 889, 351, 897), (193, 891, 202, 919), (203, 893, 215, 913), (588, 898, 602, 915), (169, 899, 188, 913), (475, 913, 484, 925), (870, 917, 887, 941),
             (83, 919, 101, 950), (118, 919, 124, 934), (513, 921, 523, 941), (372, 922, 387, 941), (652, 925, 667, 954), (121, 935, 127, 948), (677, 935, 698, 973),
             (628, 948, 641, 963), (599, 950, 612, 963), (555, 953, 566, 975), (689, 953, 714, 983), (740, 969, 771, 1010), (727, 970, 733, 984), (771, 970, 798, 1038),
             (15, 972, 21, 985), (517, 975, 530, 1001), (672, 986, 680, 1004), (799, 986, 825, 1024), (568, 989, 578, 1000), (416, 997, 436, 1031), (480, 1004, 490, 1023),
             (853, 1011, 869, 1027), (885, 1013, 907, 1047), (836, 1016, 843, 1030), (450, 1019, 467, 1050), (913, 1026, 941, 1101), (360, 1041, 376, 1064), (471, 1050, 482, 1063),
             (413, 1051, 420, 1077), (403, 1052, 411, 1068), (311, 1066, 337, 1126), (428, 1069, 434, 1092), (364, 1072, 374, 1103), (351, 1073, 363, 1099), (191, 1077, 205, 1100),
             (200, 1085, 207, 1101), (301, 1087, 307, 1096), (590, 1102, 611, 1134), (626, 1132, 650, 1170), (250, 1145, 258, 1157), (668, 1172, 687, 1201), (904, 1185, 913, 1199),
             (920, 1193, 929, 1202), (846, 1195, 858, 1208), (896, 1200, 906, 1210), (838, 1211, 852, 1223), (525, 1224, 552, 1268), (293, 1235, 320, 1271), (171, 1243, 174, 1261),
             (330, 1248, 370, 1312), (876, 1255, 885, 1267), (55, 1261, 84, 1301), (135, 1274, 189, 1362), (705, 1306, 718, 1330), (466, 1323, 508, 1397), (153, 1340, 163, 1355),
             (153, 1362, 168, 1371), (160, 1372, 167, 1384), (484, 1381, 491, 1391), (67, 1392, 78, 1404), (693, 1405, 730, 1484), (373, 1430, 419, 1494), (897, 1440, 941, 1555),
             (740, 1443, 746, 1465), (707, 1462, 731, 1500), (135, 1473, 148, 1481), (710, 1474, 719, 1489), (289, 1478, 297, 1491), (383, 1488, 396, 1506), (692, 1556, 702, 1565),
             (333, 1558, 351, 1571), (856, 1600, 863, 1608), (935, 1620, 941, 1628), (651, 1646, 658, 1656)]   # torch sea + foreground torches (gate-arch lamps excluded: the push target stays still)
K06_FG = [(135, 1274, 189, 1362), (330, 1248, 370, 1312), (466, 1323, 508, 1397), (373, 1430, 419, 1494), (693, 1405, 730, 1484), (897, 1440, 941, 1555)]   # nearest torches (smoke)
K07_TORCH = [(459, 625, 473, 643), (720, 652, 736, 675), (459, 655, 476, 742), (444, 686, 459, 737), (849, 715, 855, 731), (542, 723, 554, 728), (457, 735, 491, 829),
             (814, 748, 852, 823), (444, 752, 458, 791), (674, 761, 757, 877), (549, 783, 589, 889), (590, 786, 632, 888), (759, 791, 767, 806), (512, 801, 537, 844),
             (759, 805, 813, 896), (629, 808, 689, 892), (468, 829, 475, 842), (811, 837, 825, 852), (539, 839, 553, 861), (837, 839, 852, 864), (594, 853, 611, 879),
             (753, 853, 768, 900), (524, 854, 538, 873), (814, 859, 835, 889), (736, 860, 753, 893), (851, 877, 856, 893), (802, 878, 810, 890), (810, 887, 817, 896)]   # torches through the gate (wet-paving reflections y>1100 excluded)
K08_FIRE = [(858, 157, 941, 251), (585, 170, 811, 287), (401, 281, 624, 403), (689, 334, 763, 379), (289, 441, 368, 498), (464, 491, 601, 516),
            (125, 532, 243, 615), (742, 638, 839, 762), (481, 647, 545, 735), (535, 677, 621, 782)]   # roof + hall-door fires: bigfire = STATIC shape
K08_TORCH = [(89, 666, 109, 680), (67, 682, 113, 757), (55, 703, 67, 721), (17, 736, 32, 760), (115, 736, 128, 755), (132, 736, 158, 807), (80, 744, 89, 754),
             (128, 773, 139, 802)]   # soldiers' torches (left)
K09_CANDLE = [(586, 458, 625, 508)]   # the one lit candle (flame only; wax below y 510)
K09_CITY = [(845, 305, 915, 425)]     # palace fire seen through the window (distant, static glow)
K10_FIRE = [(700, 878, 940, 1000)]     # brazier coals under the block being burned: bigfire = STATIC
K10_CANDLE = [(487, 314, 502, 359), (424, 340, 442, 369), (582, 358, 594, 371), (779, 358, 794, 380), (536, 359, 549, 376), (424, 367, 452, 402), (818, 368, 842, 392),
             (508, 371, 523, 392), (637, 382, 660, 416), (778, 384, 784, 396), (835, 389, 858, 424), (561, 400, 575, 415), (788, 408, 797, 422), (757, 411, 766, 425),
             (530, 412, 542, 428), (592, 413, 601, 426), (486, 415, 489, 434), (852, 428, 858, 448), (852, 448, 858, 471)]   # hall candles behind (static, small glow)
K11_LANTERN = [(205, 1005, 272, 1075)] # monk's lantern: torch kind (static: NO lantern sway -- shapes static)
K11_CITY = [(555, 630, 880, 702)]      # distant burning city (static glow pulse)
# ---- K12-K19 + outro (owner 12:58): candles/lamps manual or auto, torches static, lanterns sway (K13)
K13_LANTERNS = [dict(rect=(158, 38, 288, 208), pivot=(222, 30), amp_deg=0.8), dict(rect=(482, 256, 574, 384), pivot=(528, 250), amp_deg=0.8),
                dict(rect=(552, 412, 625, 510), pivot=(588, 405), amp_deg=0.7)]   # the three big eave lanterns: gentle pendulum sway about the cord
K13_SMALL = [(679, 799, 712, 848), (634, 865, 677, 932), (798, 1073, 828, 1164)]   # distant small lanterns + a carried lamp: static glow
K15_TORCH = [(680, 440, 791, 608), (658, 978, 724, 1078), (798, 1034, 829, 1081), (763, 100, 787, 138), (727, 123, 751, 149), (829, 46, 851, 75),
             (608, 188, 623, 208), (482, 246, 496, 267), (233, 406, 242, 422)]   # held torch, gate torches, wall-top torches (STATIC shapes)
OUTRO_TORCH = [(226, 1208, 264, 1238), (331, 1046, 351, 1072), (166, 1193, 181, 1222), (132, 1187, 148, 1209), (834, 1154, 851, 1175), (131, 1025, 144, 1041),
               (35, 1015, 45, 1026), (401, 1013, 407, 1020), (907, 997, 912, 1003), (161, 1193, 167, 1206)]   # wall torches (STATIC shapes: glow + spill only)
OUTRO_WINDOW = [(578, 1060, 620, 1106)]   # the one lit window
OUTRO_LETTERING = (0, 450, 941, 990)       # baked POSTERITY + rule + tagline sit at plate y 500-697 (30-42 %); frozen 27-59 % (all lights are below 60 %)
K19_PAGE = (0, 700, 941, 1215)              # the open book (both blank pages) + its edges
FACES = {
 "k01": [(185, 375, 285, 525), (0, 550, 45, 650), (40, 570, 105, 690), (870, 630, 941, 735), (790, 670, 840, 735), (320, 690, 880, 752),
         (410, 730, 480, 812), (490, 750, 552, 812), (670, 760, 715, 812), (730, 750, 800, 822), (800, 750, 870, 832)],
 "k02": [(285, 330, 570, 670), (780, 470, 910, 860)],                  # Zhu Di face + beard, background guard
 "k03": [(225, 245, 335, 425), (640, 450, 745, 590)],                  # founder, grandson
 "k04": [(480, 240, 700, 790)],                                        # Zhu Di face/helmet/beard
 "k05": [(425, 150, 585, 355), (40, 600, 132, 745), (140, 630, 218, 752), (258, 628, 342, 742), (628, 640, 708, 752), (775, 600, 872, 745), (885, 615, 941, 765)],
 "k06": [(585, 925, 645, 1000)],                                     # mounted commander (ranks are backs of helmets)
 "k07": [(150, 400, 290, 570), (370, 745, 445, 825), (470, 810, 530, 890), (665, 810, 725, 885)],   # commander, gate pushers, horseman
 "k08": [(290, 780, 390, 900), (680, 775, 790, 890), (400, 750, 480, 840), (770, 760, 850, 850), (0, 770, 160, 970)],   # bearers + soldiers
 "k09": [],
 "k10": [(110, 225, 225, 365), (185, 635, 315, 775), (815, 475, 925, 605), (640, 340, 720, 440)],   # official, carver, brazier man, Yongle
 "k11": [(190, 680, 480, 1230)],                                    # the monk (hood/face/staff)
 "k12": [(225, 270, 385, 475), (670, 610, 765, 765)],                  # Yongle, kneeling Hu Ying
 "k13": [(205, 415, 275, 565), (325, 430, 445, 575), (470, 540, 560, 650), (880, 690, 941, 800)],   # old man, Hu Ying, official, walker
 "k14": [(375, 545, 500, 695)],                                        # Hu Ying
 "k15": [(360, 530, 465, 700), (865, 360, 941, 510), (600, 940, 650, 1000)],   # Hu Ying, near guard, gate guard
 "k16": [(280, 360, 430, 560), (775, 590, 900, 700)],                  # Yongle, eunuch
 "k17": [(270, 405, 395, 625), (635, 520, 720, 720)],                  # Yongle, Hu Ying
 "k18": [(290, 450, 410, 650)],                                        # Yongle
 "k19": [],
 "outro": [],
}
LAND = {
 "k06": [(590, 520, 720, 745), (325, 630, 425, 790), (830, 660, 941, 840), (0, 0, 941, 520)],   # gate arch, siege frames, wall/tower/sky above
 "k10": [(0, 1050, 560, 1420)],                                       # carved printing blocks + chips
 "k11": [(0, 140, 385, 520)],                                         # upper-left tree
 "k15": [(165, 150, 235, 220)],                                       # the moon
 "outro": [(680, 120, 780, 250)],                                     # the moon
}

SPECS = dict(V2.SPECS)
SPECS.update({
 "k01": dict(torch=[_pad(r, 4) for r in K01_TORCH],
             mist=[dict(rect=(300, 430, 870, 685), opacity=0.07, v=(6, 0), color=COOL_MIST, feather=50, lo=220)],   # cool night haze over the far city / moat
             mist_exclude=FACES["k01"],
             embers=[dict(spawn=[(99, 458, 10, 6), (922, 556, 12, 6), (863, 610, 8, 5)], n=9)],   # NOT off the tall left torch: its sparks would rise into the title band
             note="pole torches: static shapes, glow pulse + spill on robe/coffin/mourners | cool haze far city/moat | 9 embers | smoke_v2 off the torch heads"),
 "k02": dict(manual=[(36, 655, 92, 798)],
             haze=[dict(rect=(0, 150, 215, 1100), opacity=0.05, v=(2, -6), color=WARM_HAZE, feather=60)],
             motes=[dict(rect=(0, 420, 240, 1000), n=12, size=(1.6, 2.6), gain=0.55, color=(255, 214, 160), light="lm")],
             note="single tall candle: flame-shape motion + spill on face/robe/map | warm haze + lit motes at the left wall only (off the face) | lit candle -> no smoke"),
 "k03": dict(auto=[(0, 250, 110, 820), (520, 360, 640, 520), (780, 330, 941, 820)], exclude=FACES["k03"],
             mist=[dict(rect=(0, 200, 941, 900), opacity=0.045, v=(3, -5), color=WARM_HAZE, feather=60, lo=200)], mist_exclude=FACES["k03"],
             motes=[dict(rect=(0, 260, 200, 800), n=9, size=(1.6, 2.6), gain=0.5, color=(255, 214, 160), light="lm"),
                    dict(rect=(780, 300, 941, 800), n=8, size=(1.6, 2.6), gain=0.5, color=(255, 214, 160), light="lm")],
             note="13 candles on stands (auto): shape motion + grouped spill | warm haze (faces excluded) + lit motes at the edges | lit candles -> no smoke"),
 "k04": dict(torch=[_pad(r, 3) for r in K04_TORCH],
             mist=[dict(rect=(0, 380, 470, 1150), opacity=0.07, v=(5, -3), color=(190, 170, 150), feather=60, lo=220)], mist_exclude=FACES["k04"],
             embers=[dict(spawn=[(397, 815, 15, 5), (363, 956, 15, 5), (140, 1092, 6, 4), (222, 648, 8, 4)], n=10)],
             note="53 torches (static shapes, glow pulse + spill on armour) | warm smoke haze over the army, Zhu Di excluded | 10 embers | smoke_v2 off the big torches"),
 "k05": dict(bigfire=K05_FIRE, torch=[_pad(r, 4) for r in K05_TORCH],
             embers=[dict(spawn=[(45, 925, 35, 15)], n=12)],
             note="brazier = bigfire (static shape, pulse + spill on the edict/Zhu Di) + 12 embers | 4 wall torches (static) | smoke_v2 off the brazier + torches"),
 "k06": dict(torch=[_pad(r, 3) for r in K06_TORCH],
             mist=[dict(rect=(0, 430, 941, 900), opacity=0.06, v=(6, -2), color=(185, 168, 152), feather=60, lo=220)], mist_exclude=LAND["k06"][:3] + FACES["k06"],
             embers=[dict(spawn=[(162, 1276, 14, 6), (487, 1325, 12, 6), (711, 1407, 10, 6), (919, 1442, 12, 6)], n=10)],
             note="torch sea (static shapes, glow pulse + spill on helmets) | smoke haze over the ranks (gate + siege frames excluded) | 10 embers | smoke_v2 off the 6 nearest torches"),
 "k07": dict(torch=[_pad(r, 3) for r in K07_TORCH],
             mist=[dict(rect=(420, 600, 941, 960), opacity=0.05, v=(4, -3), color=(185, 168, 152), feather=60, lo=220)], mist_exclude=FACES["k07"],
             embers=[dict(spawn=[(715, 763, 18, 6), (611, 788, 10, 5), (833, 750, 10, 5)], n=8)],
             note="torches through the gate (static, pulse + spill on the gate leaves/armour) | haze in the gateway | 8 embers | smoke_v2 off the gate torches"),
 "k08": dict(bigfire=K08_FIRE, torch=[_pad(r, 3) for r in K08_TORCH], relight_exclude=[(0, 1280, 941, 1672)], mist_exclude=[(0, 1280, 941, 1672)] + FACES["k08"],
             embers=[dict(spawn=[(700, 230, 100, 40), (512, 340, 100, 45), (900, 200, 40, 40), (300, 470, 60, 25), (790, 700, 40, 40)], n=26)],
             note="roof fire = bigfire: STATIC painted shapes, brightness/colour/glow pulse + spill on the bearers/coffin/steps (no sway, no displacement) | 26 embers | soldiers' torches | wet paving relight-excluded | smoke_v2 plumes above the roofline"),
 "k09": dict(manual=K09_CANDLE, bigfire=K09_CITY,
             haze=[dict(rect=(420, 250, 941, 900), opacity=0.04, v=(2, -5), color=WARM_HAZE, feather=60)],
             motes=[dict(rect=(450, 330, 760, 720), n=10, size=(1.5, 2.4), gain=0.5, color=(255, 214, 160), light="lm")],
             note="lit candle (static shape, flicker + spill on the table/bed) + distant palace fire through the window (static glow) | warm haze + lit motes near the candle | lit candle -> no smoke"),
 "k10": dict(bigfire=K10_FIRE, torch=[_pad(r, 2) for r in K10_CANDLE],
             embers=[dict(spawn=[(820, 940, 90, 25)], n=16)],
             mist=[dict(rect=(380, 280, 900, 640), opacity=0.04, v=(3, -2), color=WARM_HAZE, feather=60, lo=200)], mist_exclude=FACES["k10"],
             note="brazier = bigfire: STATIC shape, glow pulse + spill on the brazier man/block | 16 embers | hall candles static glow | smoke_v2 off the brazier"),
 "k11": dict(torch=K11_LANTERN, bigfire=K11_CITY, spill_amp=0.55, radius_mult=0.7,
             relight_exclude=[(0, 0, 941, 600), (500, 600, 941, 1672), (0, 1250, 941, 1672)],   # warm light only in the lantern pool + the city strip
             mist=[dict(rect=(380, 700, 941, 1120), opacity=0.07, v=(6, 0), color=COOL_MIST, feather=70, lo=220),
                   dict(rect=(0, 1100, 941, 1500), opacity=0.05, v=(4, 0), color=COOL_MIST, feather=70, lo=220)], mist_exclude=FACES["k11"] + LAND["k11"],
             note="COOL moon-blue grade | lantern (static, small warm pool) | distant city fire (static glow pulse) | moonlit valley mist | smoke_v2 slow faint plumes off the city"),
 # ---- owner 12:58 (Rough v1): only candles + lanterns get flame-shape motion (warp_candles / sway); torch + big fire shapes static
 "k12": dict(auto=[(430, 340, 650, 560)], exclude=FACES["k12"], warp_candles=True,
             mist=[dict(rect=(380, 250, 941, 900), opacity=0.045, v=(2, -5), color=WARM_HAZE, feather=60, lo=200)], mist_exclude=FACES["k12"],
             note="4 candles on the lamp-stand (auto): flame-shape motion + flicker + grouped spill on the robes/orders | thin warm haze behind (faces excluded) | lit candles -> no smoke"),
 "k13": dict(lantern=K13_LANTERNS, torch=[_pad(r, 2) for r in K13_SMALL],
             mist=[dict(rect=(560, 120, 941, 1000), opacity=0.04, v=(3, -3), color=WARM_HAZE, feather=60, lo=200)], mist_exclude=FACES["k13"],
             note="WARM amber grade | 3 eave lanterns: gentle sway (<= 0.8 deg) + amber flicker + spill | far lanterns static glow | warm haze (faces excluded) | smoke_v2 thin slow incense curl from the burner"),
 "k14": dict(manual=[(92, 765, 120, 832)], warp_candles=True, torch=[(806, 541, 850, 597)],
             note="single candle: flame-shape motion + flicker + spill on Hu Ying/the letter | far lantern through the window: static glow | no smoke"),
 "k15": dict(torch=[_pad(r, 3) for r in K15_TORCH], relight_exclude=[(0, 1300, 941, 1672)],
             mist=[dict(rect=(480, 820, 941, 1300), opacity=0.04, v=(5, -2), color=(185, 168, 152), feather=60, lo=220)], mist_exclude=FACES["k15"] + LAND["k15"],
             embers=[dict(spawn=[(735, 455, 30, 12)], n=6)],
             note="held + gate + wall-top torches: STATIC shapes, glow pulse + spill on Hu Ying/the guards | dust haze at the gate (faces excluded) | 6 embers | wet ground relight-excluded | smoke_v2 plumes off 3 torches"),
 "k16": dict(manual=[(738, 728, 766, 780)], warp_candles=True, window=[(705, 665, 792, 800)], window_amp=0.8,
             note="eunuch's oil lamp: flame-shape motion + flicker, glass glow flicker (window kind) + spill on Yongle/the bed | no smoke"),
 "k17": dict(manual=[(486, 805, 514, 862)], warp_candles=True,
             note="single low candle: flame-shape motion + flicker + spill on both faces | no smoke"),
 "k18": dict(manual=[(698, 812, 732, 864)], warp_candles=True, flick_mult=1.5,
             note="guttering stub: flame-shape motion + HARDER flicker (amplitude x1.5, same frequencies) + spill on Yongle | no smoke"),
 "k19": dict(manual=[(758, 250, 810, 368)], warp_candles=True, freeze=[K19_PAGE], freeze_feather=24,
             note="desk candle: flame-shape motion + flicker + spill (shelves/stand) ONLY | the blank page FROZEN to the plate pixels (no spill/haze/motes/smoke/grain) | no smoke"),
 "outro": dict(torch=[_pad(r, 3) for r in OUTRO_TORCH], window=OUTRO_WINDOW, window_amp=1.0, spill_amp=0.6,
               relight_exclude=[(0, 0, 941, 990)], freeze=[OUTRO_LETTERING], freeze_feather=24,
               mist=[dict(rect=(0, 1260, 941, 1672), opacity=0.06, v=(5, 0), color=COOL_MIST, feather=50, lo=220)], mist_exclude=[OUTRO_LETTERING],
               note="baked POSTERITY + tagline used AS-IS (no overlay), lettering band FROZEN | lit window: flicker + glow + small spill | wall torches: static shapes, glow + spill only | cool mist low in the foreground (below 75 %) | static hold z 1.0 | no smoke"),
})
V2.SPECS = SPECS            # rebind the module global PlateFX reads (file untouched)
PULSE = V2.PULSE            # per-plate pulse calibration (scales the grouped SPILL only; halo + painted-flame brightness flicker are unaffected)
# measured 12:20 on the real plates (90 f, atmos/embers off), linear fit swing = a + b*pulse; target whole-frame swing <= ~6 % p-p
# (house limit 15 % / 6 %/f). k03/k07 have a 6.3-6.6 % floor from the candle/torch halos alone -> lowest sensible pulse.
PULSE.update(dict(k01=0.11, k02=0.25, k03=0.03, k04=0.045, k05=0.075, k06=0.035, k07=0.02, k08=0.03, k09=0.12, k10=0.03, k11=0.35))
PULSE.update(dict(k12=0.05, k13=0.05, k14=0.10, k15=0.03, k16=0.12, k17=0.08, k18=0.15, k19=0.25, outro=0.25))   # calib (owner 12:58): whole-frame swing 6.5/6.4/5.2/6.8/5.2/5.9/6.1/4.7/2.8 %, max step <= 1.25 %/f
def spec_todo(path): return V2.spec_todo(path)

# ---------------------------------------------------------------------------------------------- grade (static, per pixel; after fx + smoke, before crop)
GRADE = {   # lift (added, 0-1), gamma, gain (per channel), sat
 "k01": dict(lift=(0.0, 0.004, 0.012), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.97),    # cool night shadows
 "k02": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 0.995, 0.98), sat=0.95),           # calm the saturated yellow robe
 "k03": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),
 "k04": dict(lift=(0.0, 0.003, 0.010), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.97),    # cool snow night under the warm torches
 "k05": dict(lift=(0, 0, 0), gamma=1.02, gain=(1.0, 1.0, 1.0), sat=0.95),             # tame the red/orange hall a touch
 "k06": dict(lift=(0.0, 0.004, 0.012), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),    # cool night sky over the torch river
 "k07": dict(lift=(0.0, 0.002, 0.008), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),
 "k08": dict(lift=(0, 0, 0), gamma=1.02, gain=(1.0, 1.0, 1.0), sat=0.94),             # keep the roof fire from clipping orange
 "k09": dict(lift=(0.0, 0.002, 0.008), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),
 "k10": dict(lift=(0, 0, 0), gamma=1.01, gain=(1.0, 1.0, 1.0), sat=0.95),
 "k11": dict(lift=(0.0, 0.010, 0.030), gamma=1.0, gain=(0.95, 0.99, 1.05), sat=0.90),  # COOL moon-blue throughout
 "k12": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 0.995, 0.98), sat=0.95),           # calm the yellow robe
 "k13": dict(lift=(0.010, 0.004, 0.0), gamma=1.0, gain=(1.04, 1.0, 0.90), sat=1.0),   # WARM amber (distinct from K11's cool blue)
 "k14": dict(lift=(0.0, 0.002, 0.008), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),
 "k15": dict(lift=(0.0, 0.003, 0.010), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),    # cool night over the torches
 "k16": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 0.995, 0.98), sat=0.95),
 "k17": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.96),
 "k18": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 0.995, 0.98), sat=0.95),
 "k19": dict(lift=(0, 0, 0), gamma=1.0, gain=(1.0, 1.0, 1.0), sat=0.97),
 # outro: NO grade (the baked lettering is used as-is)
}
_LUT = {}
def grade(img, key):
    g = GRADE.get(key)
    if not g: return img
    if key not in _LUT:
        x = np.arange(256, dtype=np.float32) / 255.0; luts = []
        for c in range(3):
            y = np.clip(x * g["gain"][c] + g["lift"][c] * (1 - x), 0, 1) ** g["gamma"]; luts.append(np.clip(np.rint(y * 255), 0, 255).astype(np.uint8))
        _LUT[key] = luts
    out = np.stack([_LUT[key][c][img[..., c]] for c in range(3)], -1)
    s = g["sat"]
    if abs(s - 1) > 1e-6:
        f = out.astype(np.float32); L = (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2])[..., None]
        out = np.clip(np.rint(L + (f - L) * s), 0, 255).astype(np.uint8)
    return out

# ---------------------------------------------------------------------------------------------- smoke_v2 per plate
GLOW = dict(color=[255, 150, 80], strength=0.22, reach=0.1, flicker=0.3, patch=0.4)
def torch_em(name, src, h, w1, lean, seed, op=0.55, dark=(30, 30, 34), light=(100, 98, 104), **kw):
    return dict(dict(name=name, type="torch", src=list(src), height=h, w0=max(4.0, w1 / 10), w1=w1, lean=lean, seed=seed, opacity=op,
                     color_dark=list(dark), color_light=list(light), glow=dict(GLOW), detail=0.2, relief=0.12, breakup=0.3, hi=6.0, lo=90, edge=[0.06, 0.75]), **kw)
# protect groups: faces / flames / water / land / lettering / title_band / legend_corner -> protect polygons (0 px) + named guards in the per-slot proof
SMOKE = {
 "k01": dict(todo=False, on=True, seed=101, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k01"], flames=[_pad(r, 3) for r in K01_TORCH], water=[(380, 598, 870, 700)], land=[(0, 840, 941, 1672)], title_band=[_title_band()]),
             emitters=[torch_em("torch_L1", (52, 338), 260, 90, -15, 1, 0.55), torch_em("torch_L2", (99, 456), 220, 70, -12, 2, 0.5),
                       torch_em("torch_L3", (25, 512), 170, 50, -10, 3, 0.45), torch_em("torch_R1", (922, 553), 240, 80, -20, 4, 0.55),
                       torch_em("torch_R2", (863, 607), 200, 60, -15, 5, 0.5)]),
 "k02": dict(todo=False, on=False, why="lit candle, not snuffed: no visible smoke (owner may switch on a faint candle wisp)", groups={}, emitters=[]),
 "k03": dict(todo=False, on=False, why="lit candles only: no smoke", groups={}, emitters=[]),
 "k04": dict(todo=False, on=True, seed=104, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k04"], flames=[_pad(r, 3) for r in K04_TORCH], land=[(0, 0, 941, 240), (150, 225, 310, 335)]),   # mountains + the gate tower
             emitters=[torch_em("t810", (397, 812), 240, 80, -18, 1, 0.45), torch_em("t951", (363, 953), 260, 90, -20, 2, 0.45),
                       torch_em("t720", (443, 722), 200, 60, -16, 3, 0.4), torch_em("t745", (270, 747), 200, 60, -16, 4, 0.4),
                       torch_em("t664", (272, 666), 190, 60, -14, 5, 0.4), torch_em("t645", (222, 645), 180, 55, -14, 6, 0.38),
                       torch_em("t898", (163, 898), 200, 60, -16, 7, 0.4), torch_em("t1090", (140, 1090), 220, 70, -18, 8, 0.42),
                       torch_em("t614", (26, 614), 180, 55, -14, 9, 0.38), torch_em("t952", (17, 952), 200, 60, -16, 10, 0.4),
                       torch_em("wall344", (451, 344), 110, 36, -8, 11, 0.32)]),
 "k05": dict(todo=False, on=True, seed=105, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k05"], flames=[_pad(r, 3) for r in K05_TORCH + K05_FIRE], water=[(0, 1040, 941, 1671)]),   # wet floor + the edict (lettering)
             emitters=[torch_em("brazier", (45, 905), 230, 150, -55, 1, 0.55, dark=(40, 34, 32), light=(120, 110, 104), w0=28.0, rise=40),
                       torch_em("torch_L", (40, 467), 260, 85, -15, 2, 0.55), torch_em("torch_M", (315, 574), 230, 72, -12, 3, 0.5),
                       torch_em("torch_R1", (905, 421), 260, 80, -20, 4, 0.55), torch_em("torch_R2", (856, 561), 220, 70, -15, 5, 0.5)]),
 "k06": dict(todo=False, on=True, seed=106, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k06"], flames=[_pad(r, 3) for r in K06_FG], land=LAND["k06"], water=[(0, 440, 250, 770)]),   # gate, siege frames, wall/sky, river
             emitters=[torch_em(f"fg{i}", ((r[0] + r[2]) // 2, r[1] + 2), h, w, -14, i + 1, op) for i, (r, h, w, op) in enumerate(zip(K06_FG, (220, 200, 220, 230, 240, 260), (70, 60, 70, 75, 80, 90), (0.42, 0.4, 0.42, 0.45, 0.45, 0.48)))]),
 "k07": dict(todo=False, on=True, seed=107, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k07"], water=[(280, 1100, 941, 1672)]),
             emitters=[torch_em("g715", (715, 761), 230, 80, -10, 1, 0.42), torch_em("g659", (659, 808), 190, 60, -8, 2, 0.36),
                       torch_em("g786", (786, 805), 190, 60, -12, 3, 0.36), torch_em("g569", (569, 783), 180, 55, -8, 4, 0.34),
                       torch_em("g833", (833, 748), 200, 60, -12, 5, 0.38), torch_em("g474", (474, 735), 170, 50, -6, 6, 0.32)]),
 "k08": dict(todo=False, on=True, seed=108, preroll=10.0, protect_feather=20,
             groups=dict(faces=FACES["k08"], water=[(0, 1280, 941, 1672)], flames=[_pad(r, 3) for r in K08_TORCH]),
             emitters=[dict(name='roof_main', type="column", src=[700, 178], height=460, w0=60, w1=260, lean=-20, layers=2, seed=1, rise=30, opacity=0.62, color_dark=[26, 18, 20], color_light=[80, 62, 60]),
                       dict(name='roof_left', type="column", src=[512, 285], height=320, w0=45, w1=190, lean=-25, layers=1, seed=2, rise=28, opacity=0.5, color_dark=[26, 18, 20], color_light=[80, 62, 60]),
                       dict(name='roof_right', type="column", src=[900, 160], height=300, w0=30, w1=150, lean=-15, layers=1, seed=3, rise=28, opacity=0.5, color_dark=[26, 18, 20], color_light=[80, 62, 60]),
                       torch_em("sold1", (90, 684), 200, 60, -10, 4, 0.42), torch_em("sold2", (145, 738), 180, 55, -10, 5, 0.38)]),
 "k09": dict(todo=False, on=False, why="lit candle, not snuffed; the window fire is far and already painted with smoke", groups={}, emitters=[]),
 "k10": dict(todo=False, on=True, seed=110, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k10"], land=LAND["k10"]),
             emitters=[torch_em("brazier", (845, 905), 300, 160, 28, 1, 0.5, dark=(40, 34, 32), light=(120, 110, 104), w0=30.0, rise=38),
                       torch_em("brazier_b", (760, 935), 220, 110, 20, 2, 0.4, dark=(40, 34, 32), light=(120, 110, 104), w0=22.0, rise=34)]),
 "k11": dict(todo=False, on=True, seed=111, preroll=12.0, protect_feather=24,
             groups=dict(faces=FACES["k11"], land=LAND["k11"], moon=[(770, 80, 870, 180)], water=[(560, 705, 941, 840)]),
             emitters=[dict(name='city_a', type="column", src=[760, 640], height=360, w0=26, w1=150, lean=28, layers=1, seed=1, rise=18, opacity=0.42, color_dark=[30, 32, 40], color_light=[78, 82, 96]),
                       dict(name='city_b', type="column", src=[845, 652], height=300, w0=22, w1=130, lean=32, layers=1, seed=2, rise=16, opacity=0.38, color_dark=[30, 32, 40], color_light=[78, 82, 96])]),
}
# owner 12:58 (Rough v1): K12-K19 + outro real (no templates left). Lit candles/lamps -> no smoke (Vellum 2: no wisps on lit candles).
_OFF = lambda why: dict(todo=False, on=False, why=why, groups={}, emitters=[])
SMOKE.update({
 "k12": _OFF("lit candles: no smoke"),
 "k13": dict(todo=False, on=True, seed=113, preroll=12.0, protect_feather=20,
             groups=dict(faces=FACES["k13"], lanterns=[_pad(L["rect"], 14) for L in K13_LANTERNS]),
             emitters=[dict(name="incense", type="candle", src=[45, 656], height=380, w0=1.5, w1=26.0, lean=12.0, rise=16.0, opacity=0.30, seed=1,
                            swirl=6.0, meander=0.4, color_dark=[150, 132, 112], color_light=[205, 188, 165])]),   # thin + slow, warm-lit
 "k14": _OFF("lit candle: no smoke"),
 "k15": dict(todo=False, on=True, seed=115, preroll=8.0, protect_feather=20,
             groups=dict(faces=FACES["k15"], moon=LAND["k15"], water=[(0, 1300, 941, 1672)]),
             emitters=[torch_em("held", (737, 446), 300, 100, -12, 1, 0.48), torch_em("gate", (690, 984), 200, 60, -8, 2, 0.40),
                       torch_em("gate2", (813, 1038), 170, 50, -8, 3, 0.36)]),
 "k16": _OFF("lit oil lamp: no smoke"), "k17": _OFF("lit candle: no smoke"),
 "k18": _OFF("guttering stub is still lit: no wick smoke (grid's thin curl kept OFF per Vellum 2 -- owner option)"),
 "k19": _OFF("desk candle lit; the page must stay still: no smoke"),
 "outro": dict(todo=False, on=False, why="outro: torches glow only; lettering untouched", groups=dict(lettering=[dict(frac=[0, 0.30, 1, 0.70])]), emitters=[]),
})
SLOT_SMOKE = {   # per-slot on/off (None = the plate default); drop = protect groups not needed in that slot
 "S01": dict(on=None), "S02A": dict(on=None), "S02B": dict(on=None), "S03": dict(on=None), "S04": dict(on=None), "S05": dict(on=None),
 "S09": dict(on=None, drop=["title_band"]),   # reprise: no title on screen -> the tall left torch may smoke into the sky
 "S06": dict(on=None), "S07": dict(on=None), "S08": dict(on=None), "S10": dict(on=None), "S11": dict(on=None),
 "S12": dict(on=None),   # owner 12:59: LEGEND removed -> legend_top protect dropped (moon + tree + monk + valley stay protected)
 "S13": dict(on=None), "S14": dict(on=None), "S15": dict(on=None), "S16": dict(on=None), "S17": dict(on=None), "S18": dict(on=None),
 "S19": dict(on=None), "S20": dict(on=None), "OUTRO": dict(on=None),
}

def _poly(r, W, H):
    if isinstance(r, dict):
        x0, y0, x1, y1 = r["frac"]; r = (x0 * W, y0 * H, x1 * W, y1 * H)
    x0, y0, x1, y1 = [float(v) for v in r]; return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
def smoke_state(key, slot):
    """('on'|'off'|'todo', reason) for a plate key + slot."""
    s = SMOKE.get(key)
    if s is None: return "off", "no smoke entry"
    if s["todo"]: return "todo", s.get("plan", "")
    o = SLOT_SMOKE.get(slot, {}).get("on"); on = s["on"] if o is None else o
    return ("on", "") if on else ("off", s.get("why", f"slot {slot} off"))
def smoke_config(key, slot, W, H):
    s = SMOKE[key]; sl = SLOT_SMOKE.get(slot, {})
    groups = {g: v for g, v in s["groups"].items() if g not in sl.get("drop", [])}; groups.update(sl.get("add", {}))
    protect, guards = [], {}
    for g, rs in groups.items():
        for i, r in enumerate(rs): p = _poly(r, W, H); protect.append(p); guards[f"{g}_{i}"] = p
    return dict(seed=s["seed"], preroll=s["preroll"], protect=protect, protect_feather=s["protect_feather"], flame_keepout=0.0, emitters=s["emitters"], guards=guards)
