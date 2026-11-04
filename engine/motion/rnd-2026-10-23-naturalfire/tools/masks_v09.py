"""v09 R&D flame masks (rnd folder only; prod masks_v2b2 is read-only and untouched).
core_ci : painted fire = warm & bright threshold on the plate, inside hand-placed fire ROIs, minus every protected face/hand poly (+margin),
          exclude_polys, and stone/figures (ROIs avoid them; luminance threshold rejects dark stone). Feathered.
ext_ci  : extension zone above each core (frac of its height) where wisps may travel and fade; only over dark / smoky background,
          never over the protected set (faces/hands+margin, exclude_polys, gold/stone/figure guard polys)."""
import sys, json, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks
OUT = "masks_v09"; prm = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
pl = cv2.cvtColor(cv2.imread(str(P.PLATE)), cv2.COLOR_BGR2RGB).astype(np.float32); H, W = pl.shape[:2]
cand = json.load(open(P.MASKS / "P05_candles.json"))
R, G, B = pl[..., 0], pl[..., 1], pl[..., 2]; L = 0.299 * R + 0.587 * G + 0.114 * B
def ss(a, b, x): t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def poly(ps): m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32) for p in ps], 1); return m > 0
MARGIN = prm.get("margin", 5)
fh = poly(cand["face_hand_polys"]); fh_m = cv2.dilate(fh.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * MARGIN + 1,) * 2)) > 0
exc = poly(cand["exclude_polys"])
# guard polys (R&D): stone block faces, smith arms/torsos, gold — hand placed from gridded plate views (masks_rnd/grid_*.png)
GUARD = prm.get("guard", {
    "stone_pillar_front": [[416, 610], [466, 610], [466, 765], [416, 765]],
    "stone_mid_block_face": [[491, 776], [600, 776], [600, 864], [491, 864]],
    "stone_left_low_block": [[330, 858], [500, 858], [500, 1000], [330, 1000]],
    "stone_right_low_block": [[558, 862], [640, 862], [640, 1000], [558, 1000]],
    "left_smith_arm": [[300, 730], [386, 730], [400, 790], [398, 816], [388, 870], [300, 870]],
    "right_smith_body": [[452, 640], [560, 640], [560, 775], [452, 775]],
    "gold_lower_left": [[0, 870], [340, 870], [340, 1200], [0, 1200]]})
guard = poly(list(GUARD.values()))
prot = fh_m | exc | guard
THR = prm.get("thr", {"c0": 130, "c1": 105, "c2": 205})     # min red level; fire = red & saturated ((R-B)/R), or yellow-white hot
SAT = (R - B) / np.maximum(R, 1)
def firescore(k):
    warm = ss(THR[k], THR[k] + 40, R) * ss(0.55, 0.70, SAT) * (R >= G - 4)
    hot = ss(185, 215, L) * (R >= G - 8) * (R - B > 25)
    return np.maximum(warm, hot)
ROIS = prm.get("rois", {
    "c0": [[[398, 566], [424, 566], [424, 612], [416, 612], [416, 762], [386, 762], [386, 612], [398, 612]]],
    "c1": [[[398, 764], [491, 764], [491, 862], [398, 862]]],
    "c2": [[[493, 862], [558, 862], [558, 940], [493, 940]]]})
prodm = dict(zip(('c0', 'c1', 'c2'), load_masks()))
EXT = prm.get("ext_frac", 0.22); res = {}; cores, softs = {}, {}
for k, rois in ROIS.items():
    roi = poly(rois); pm = prodm[k] > 0.5
    fire = firescore(k); c = ((fire > 0.35) & roi & ~prot) | pm          # prod flame mask always included (already prod-verified as flame)
    c = cv2.morphologyEx(c.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)); c = cv2.morphologyEx(c, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(c); keep = np.zeros_like(c)
    for j in range(1, n):
        if st[j, cv2.CC_STAT_AREA] >= prm.get("min_area", 12): keep[lab == j] = 1
    keep = (keep > 0) | pm
    soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 1.2); soft = np.clip(soft * 1.6, 0, 1) * ((~prot & roi) | pm)
    cores[k], softs[k] = keep, np.maximum(soft, prodm[k])
anycore = np.maximum.reduce([v for v in softs.values()]) > 0
allc = np.zeros((H, W), np.float32); alle = np.zeros((H, W), np.float32)
for k in ROIS:
    keep, soft = cores[k], softs[k]
    ys, xs = np.nonzero(keep); y0, y1 = ys.min(), ys.max(); Hf = y1 - y0 + 1
    eh = int(round(EXT * Hf)); ext = np.zeros((H, W), np.float32)
    for d in range(1, eh + 1): ext[:-d][keep[d:]] = 1.0                       # directional (upward) dilation of the core by eh px
    okbg = (L < prm.get("ext_Lmax", {"c0": 200, "c1": 200, "c2": 90})[k]) & ~prot & ~anycore
    ext = cv2.GaussianBlur((ext * okbg).astype(np.float32), (0, 0), 1.5) * okbg
    ext = np.clip(ext * 1.4, 0, 1)
    cv2.imwrite(f"{OUT}/P05_fire_{k}.png", np.rint(soft * 255).astype(np.uint8)); cv2.imwrite(f"{OUT}/P05_fire_{k}_ext.png", np.rint(ext * 255).astype(np.uint8))
    res[k] = dict(core_px=int((soft > 0.5).sum()), ext_px=int((ext > 0.5).sum()), Hf=int(Hf), ybot=int(y1), ytop=int(y0), ext_h=eh)
    allc = np.maximum(allc, soft); alle = np.maximum(alle, ext)
prot_save = prot & ~anycore   # R&D protected set used for the v09 QC: face/hand polys (+margin), exclude_polys, guard polys (stone/figures/gold), minus the flame cores
cv2.imwrite(f"{OUT}/P05_rnd_protect.png", (prot_save * 255).astype(np.uint8))
res["rnd_protect_px"] = int(prot_save.sum()); res["prod_protect_px_overlapped_by_new_core_or_ext"] = int((((allc + alle) > 0) & (cv2.imread(str(P.MASKS / "P05_protect.png"), 0) > 0)).sum())
prod = np.maximum.reduce(list(prodm.values()))
res["prod_union_px"] = int((prod > 0.5).sum()); res["new_core_union_px"] = int((allc > 0.5).sum()); res["prod_covered_by_new"] = round(float(((allc > 0.3) & (prod > 0.5)).sum() / max(1, (prod > 0.5).sum())), 3)
res["overlap_core_with_protect_px"] = int(((allc > 0) & prot).sum()); res["overlap_ext_with_protect_px"] = int(((alle > 0) & prot).sum())
res["overlap_with_face_hand_polys_px"] = int((((allc + alle) > 0) & fh).sum())
json.dump(dict(stats=res, params=dict(margin=MARGIN, guard=GUARD, rois=ROIS, ext_frac=EXT, prm=prm)), open(f"{OUT}/masks_v09_meta.json", "w"), indent=1)
# overlay: red = new core, cyan = extension, green contour = prod v2b2 masks, magenta = face/hand polys, blue tint = R&D protect
X0, Y0, X1, Y1, S = 300, 540, 640, 1000, 3
im = pl.copy(); im[prot] = im[prot] * 0.6 + np.array([40, 60, 200]) * 0.4
im = im * (1 - 0.55 * allc[..., None]) + np.array([255, 30, 30]) * 0.55 * allc[..., None]
im = im * (1 - 0.6 * alle[..., None]) + np.array([0, 255, 255]) * 0.6 * alle[..., None]
im = np.clip(im, 0, 255).astype(np.uint8)
big = cv2.resize(im[Y0:Y1, X0:X1], None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
raw = cv2.resize(pl[Y0:Y1, X0:X1].astype(np.uint8), None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
def cont(img, m, col, thr=0.5):
    cs, _ = cv2.findContours((m > thr).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, [((c.astype(np.float32) - [X0, Y0] + 0.5) * S).astype(np.int32) for c in cs], -1, col, 1)
cont(big, prod, (0, 255, 0)); cont(big, fh.astype(np.float32), (255, 0, 255)); cont(raw, allc, (255, 255, 255), 0.5); cont(raw, alle, (0, 255, 255), 0.5)
ov = np.hstack([raw, big]); cv2.imwrite(f"{OUT}/P05_fire_v09_mask_overlay.png", cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))
print(json.dumps(res, indent=1))
for nm, (a, b, c_, d) in {"upper": (360, 550, 470, 780), "lower": (390, 760, 570, 950)}.items():
    z = cv2.resize(im[b:d, a:c_], None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST); r = cv2.resize(pl[b:d, a:c_].astype(np.uint8), None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(f"{OUT}/zoom_{nm}.png", cv2.cvtColor(np.hstack([r, z]), cv2.COLOR_RGB2BGR))
