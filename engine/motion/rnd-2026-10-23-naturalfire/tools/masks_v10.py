"""v10 masks (NEW files in v10/masks/). named_protect = v09 R&D guard boxes (no margin) + prod face/hand polys (verbatim, read-only source)
+ new rim/jamb/sill polys. allowed = per-zone polys minus named_protect: the ONLY plate area new material may be drawn over.
Output holdout = camera-mapped complement of allowed (any influence), so protected objects AND all other stone/figures stay bit-exact."""
import sys, json, numpy as np, cv2, os; sys.path.insert(0, 'tools'); import prod as P
pl = cv2.imread(str(P.PLATE)); Hh, Ww = pl.shape[:2]
VER = sys.argv[1] if len(sys.argv) > 1 else ""      # "" = first set, "_b" = right-smith head box trimmed to the head (x>=462) so the fire above the pillar top is usable
TRIM = {"_b": {3: [[462, 578], [522, 578], [522, 668], [462, 668]]}}.get(VER, {})
meta = json.load(open('masks_v09/masks_v09_meta.json')); cand = json.load(open(P.MASKS / 'P05_candles.json'))
NEW = {"c0_rim_c1_lintel": [[355, 750], [500, 750], [500, 798], [355, 798]],
       "c1_left_jamb": [[395, 760], [412, 760], [412, 860], [395, 860]],
       "c2_right_jamb": [[552, 860], [562, 860], [562, 948], [552, 948]],
       "c2_sill": [[488, 946], [565, 946], [565, 1000], [488, 1000]]}
ZONES = {"z0low": [[398, 682], [417, 682], [417, 750], [393, 750], [393, 705]],
         "z0top": [[386, 500], [470, 500], [470, 611], [386, 611]] if VER == "" else [[388, 492], [462, 492], [462, 611], [388, 611]],
         "z1": [[412, 798], [491, 798], [491, 858], [412, 858]],
         "z2": [[500, 862], [553, 862], [553, 946], [500, 946]]}
prot = np.zeros((Hh, Ww), np.uint8); names = {}
for k, p in list(meta["params"]["guard"].items()) + [(f"prod_face_hand_{i}" + ("_trimmed_x462" if i in TRIM else ""), TRIM.get(i, p)) for i, p in enumerate(cand["face_hand_polys"])] + list(NEW.items()):
    cv2.fillPoly(prot, [np.array(p, np.int32)], 255); names[k] = p
allowed = np.zeros((Hh, Ww), np.uint8); zl = {}
for k, p in ZONES.items():
    z = np.zeros_like(allowed); cv2.fillPoly(z, [np.array(p, np.int32)], 255); z[prot > 0] = 0; zl[k] = int((z > 0).sum()); allowed |= z
    cv2.imwrite(f'v10/masks/P05_v10_zone_{k}{VER}.png', z)
for f, a in ((f'v10/masks/P05_v10_named_protect{VER}.png', prot), (f'v10/masks/P05_v10_allowed{VER}.png', allowed)):
    assert not os.path.exists(f) or (cv2.imread(f, 0) == a).all(); cv2.imwrite(f, a)
json.dump(dict(named_protect_polys=names, zones=ZONES, zone_px=zl, allowed_px=int((allowed > 0).sum()), named_protect_px=int((prot > 0).sum()),
               overlap_allowed_protect=int(((allowed > 0) & (prot > 0)).sum())), open(f'v10/masks/masks_v10_meta{VER}.json', 'w'), indent=1)
x0, y0, x1, y1 = 330, 480, 640, 1010; C = pl[y0:y1, x0:x1].copy().astype(np.float32)
C[prot[y0:y1, x0:x1] > 0] = C[prot[y0:y1, x0:x1] > 0] * .55 + np.array([0, 0, 255]) * .45
C[allowed[y0:y1, x0:x1] > 0] = C[allowed[y0:y1, x0:x1] > 0] * .6 + np.array([255, 120, 0]) * .4
cv2.imwrite(f'v10/masks/P05_v10_mask_overlay{VER}.png', cv2.resize(C.astype(np.uint8), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)); print(zl)
