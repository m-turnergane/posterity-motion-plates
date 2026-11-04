#!/usr/bin/env python3
"""chronicle_atlas_p0b -- Chronicle Atlas P0 step 2 FIX-FIRST (new file; chronicle_atlas_p0.py and every p0 still untouched).

Changes vs p0 (everything else is imported from chronicle_atlas_p0 unchanged: Fields, paint, border_alpha, labels, authority):
  1. Route CORES darkened (deep oxblood), NOT resaturated: CIELAB chroma of every route colour is below its p0 value and HSV S
     stays <= p0 documented (0.738).  Claimed stays broken (dashes), thinner and lighter (higher luminance) than documented.
  2. Over SEA the route halo turns from dark ink into a pale paper casing (a dark core can never reach 3:1 against the dark
     sea: sea rel. lum ~0.05 caps any darker colour at ~2.1:1), so on water the line reads core-vs-casing.  Over land: dark halo.
  3. Dash-only phone-scale contrast metric: samples are taken only where the full-resolution leg alpha is > 0.6 at the sample
     and both neighbours (+-2 plate px along the line) -- i.e. inside a dash, never in a gap -- then measured on the frame
     downscaled to phone scale (360x640 crop of the 1920x1080 frame = 0.5926 x output).  At phone scale: core = 25th pct
     luminance inside the stroke band (|d| <= w/2+0.3 px), adjacent = 75th pct of the band w/2+0.8..w/2+2.6 px (halo or
     casing, what touches the line), map = median of the raw map (no ink/halo) just beyond the halo.
  4. Terrain state: residual rust tint removed (pigment_alpha 0 -> no realm pigment at all in terrain-forward; relief only),
     region labels at full alpha with a slightly stronger halo so 2a's Glamorgan / Ireland stay readable.
"""
import copy, json, os, sys, math
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronicle_atlas_p0 as A                                          # noqa: E402
R2, MM, V1, VR = A.R2, A.MM, A.V1, A.VR

ROUTE_P0 = copy.deepcopy(A.ROUTE)
ROUTE_B = {
    "documented": dict(col=[58, 18, 16], pool=[36, 10, 9], strength=0.97, halo_col=[16, 8, 8], halo_opacity=0.85,
                       halo_dilate=4, grain=0.06, sea_casing=[238, 226, 194], sea_casing_opacity=0.92),
    "claimed":    dict(col=[92, 32, 26], pool=[60, 20, 16], strength=0.97, halo_col=[16, 8, 8], halo_opacity=0.78,
                       halo_dilate=3, grain=0.08, sea_casing=[238, 226, 194], sea_casing_opacity=0.90),
}
EMPHASIS_B = copy.deepcopy(A.EMPHASIS)
EMPHASIS_B["terrain"].update(pigment_alpha=0.0, pigment_chroma=0.0, label_region_alpha=1.0, label_halo=0.90)
STATE_FILE = A.STATE_FILE
PHONE_F = 640 / 1080                                                  # phone px per output px (360x640 crop of 1080p)

def use_route_b():
    """p0's composite_route/_build_ink read the module-level ROUTE dict: point it at the p0b values (in-process only)."""
    for st in A.ROUTE: A.ROUTE[st].clear(); A.ROUTE[st].update(copy.deepcopy(ROUTE_B[st]))

class AtlasShotB(A.AtlasShot):
    def __init__(s, cfg_path):
        use_route_b(); super().__init__(cfg_path)
        s.seaw = np.clip(cv2.GaussianBlur((1 - s.T.land).astype(np.float32), (0, 0), 1.5), 0, 1)   # 1 = water

    def halo_rgb(s, st):
        R = ROUTE_B[st]; w = s.seaw[..., None]; h = s.halo[st][..., None]
        col = np.float32(R["halo_col"]) * (1 - w) + np.float32(R["sea_casing"]) * w
        op = h / R["halo_opacity"] * (R["halo_opacity"] * (1 - w) + R["sea_casing_opacity"] * w)
        return col, op

    def render(s, P, layers=None):
        """As p0 render, with the land/sea halo.  layers (optional) = per-leg/pin opacity multipliers are handled by
        the animation renderer; stills use the full ink."""
        T, F = s.T, s.F; H, W = T.lb.shape
        base = A.paint(T, F, P); img = base.copy()
        ba = A.border_alpha(F, P, s.label_mask) * T.land
        img = img * (1 - ba[..., None]) + np.float32(A.BORDER_INK) * ba[..., None]
        mapimg = img.copy(); ink_a = np.zeros((H, W), np.float32)
        for st in ("claimed", "documented"):
            col, op = s.halo_rgb(st); img = img * (1 - op) + col * op
        for st in ("claimed", "documented"):
            img, a = A.composite_route(img, s.alpha[st], st, F); ink_a = np.maximum(ink_a, a)
        inked = img.copy(); s._last = (inked, mapimg)
        s.draw_labels(img, P)
        out = cv2.resize(np.clip(img + 0.5, 0, 255).astype(np.uint8), tuple(s.cfg["out_wh"]), interpolation=cv2.INTER_AREA)
        return out, dict(params=P, ink_a=ink_a, ba=ba)

    def draw_labels(s, img, P, alpha_of=None):
        H, W = img.shape[:2]
        for l in s.labels:
            k = 1.0 if alpha_of is None else alpha_of(l)
            if k <= 0.003: continue
            L = l["L"]; x0, y0, x1, y1 = L.bbox(); cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            roi = img[cy0:cy1, cx0:cx1]; a = L.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            la = (P["label_region_alpha"] if l["tier"] == "region" else P["label_place_alpha"]) * k
            hl = L.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * P["label_halo"] * la
            roi[...] = roi * (1 - hl[..., None]) + np.float32(R2.LABEL_HALO_COL) * hl[..., None]
            roi[...] = roi * (1 - 0.94 * la * a[..., None]) + np.float32(A.TIERS[l["tier"]]["ink"]) * 0.94 * la * a[..., None]

def phone_contrast(S, inked, mapimg, f):
    """Dash-only, phone-scale contrast per leg (see module doc).  Land samples: core vs the raw map just beyond the halo
    (no ink, no halo) = what the eye compares the line with.  Sea samples: core vs casing (adjacent) and core vs sea."""
    H, W = inked.shape[:2]; sz = (int(round(W * f)), int(round(H * f)))
    I = cv2.resize(inked, sz, interpolation=cv2.INTER_AREA); M = cv2.resize(mapimg, sz, interpolation=cv2.INTER_AREA)
    LI, LM = R2.rel_lum(I), R2.rel_lum(M)
    anyink = cv2.resize(np.maximum.reduce([S.halo["documented"], S.halo["claimed"]]), sz, interpolation=cv2.INTER_AREA)
    res = []
    for li, lg in enumerate(S.legs):
        R = ROUTE_B[lg["style"]]; af = S.leg_alpha[li]; Q = R2.resample(lg["Pt"], 2.0)
        m = np.ones(sz[::-1], np.uint8); cv2.polylines(m, [np.int32(np.round(lg["Pt"] * f * 4))], False, 0, 1, cv2.LINE_8, shift=2)
        d = cv2.distanceTransform(m, cv2.DIST_L2, 5); hw = lg["w0"] * f / 2; hh = (lg["w0"] / 2 + R["halo_dilate"] + 2.5) * f
        acc = {"land": ([], [], []), "sea": ([], [], [])}; nskip_gap = 0
        for k, q in enumerate(Q):
            if any(np.hypot(*(q - p["xy"])) < p["r_edge"] + 6 for p in S.pins): continue
            xi, yi = int(round(q[0])), int(round(q[1]))
            if not (0 <= xi < W and 0 <= yi < H): continue
            nb = Q[max(0, k - 1):k + 2]
            if min(af[min(H - 1, int(round(p[1]))), min(W - 1, int(round(p[0])))] for p in nb) < 0.6: nskip_gap += 1; continue
            X, Y = int(round(q[0] * f)), int(round(q[1] * f)); r = int(hh + 5)
            y0, x0 = max(0, Y - r), max(0, X - r); y1, x1 = Y + r + 1, X + r + 1
            dd = d[y0:y1, x0:x1]; ai = anyink[y0:y1, x0:x1]
            core = dd <= max(hw + 0.3, 1.0); ring = (dd >= hh + 1.0) & (dd <= hh + 3.0) & (ai < 0.03); near = (dd >= hw + 0.8) & (dd <= hw + 2.6)
            if core.sum() < 2 or ring.sum() < 3 or near.sum() < 2: continue
            lc = float(np.percentile(LI[y0:y1, x0:x1][core], 25))                 # the ink within the stroke band (robust to ~1 px nib offset)
            kind = "land" if S.seaw[yi, xi] < 0.5 else "sea"
            acc[kind][0].append(R2.wcag(lc, float(np.median(LM[y0:y1, x0:x1][ring]))))
            acc[kind][1].append(R2.wcag(lc, float(np.percentile(LI[y0:y1, x0:x1][near], 75)))); acc[kind][2].append(lc)
        e = dict(leg=f"{lg['a']['row']}->{lg['b']['row']}", style=lg["style"], line_w_phone_px=round(lg["w0"] * f, 2), gap_samples_excluded=nskip_gap)
        for kind, (v, u, c) in acc.items():
            if not v: continue
            v, u = np.array(v), np.array(u)
            e[kind] = dict(n=int(len(v)), core_vs_map_median=round(float(np.median(v)), 2), core_vs_map_p10=round(float(np.percentile(v, 10)), 2),
                           core_vs_adjacent_median=round(float(np.median(u)), 2), core_vs_adjacent_p10=round(float(np.percentile(u, 10)), 2),
                           core_rel_lum_median=round(float(np.median(c)), 4))
        res.append(e)
    return res

def label_readability(S, img_plate):
    """Region/place label legibility in a rendered plate: WCAG of glyph core (L.a > 0.6) vs the label's surround
    (halo zone, glyph alpha < 0.05) -- median luminance of each."""
    H, W = img_plate.shape[:2]; Lm = R2.rel_lum(img_plate); out = []
    for l in S.labels:
        L = l["L"]; x0, y0, x1, y1 = L.bbox(); cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        a = L.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]; hz = L.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        roi = Lm[cy0:cy1, cx0:cx1]; g = roi[a > 0.6]; sur = roi[(a < 0.05) & (hz > 0.05)]
        if len(g) < 5 or len(sur) < 5: continue
        out.append(dict(text=l["text"], tier=l["tier"], glyph_vs_surround=round(R2.wcag(float(np.median(g)), float(np.median(sur))), 2)))
    return out

def rust_metric(S, P):
    """Mean CIELAB a* (red-green; + = red) and chroma of English land in the painted map (no ink), plate px."""
    img = np.clip(A.paint(S.T, S.F, P), 0, 255).astype(np.uint8); lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
    rw = S.T.realm_weights(); m = (rw.get("england", np.zeros_like(S.T.lb, np.float32)) > 0.8) & (S.T.lb > 0)
    a, b = lab[..., 1][m] - 128, lab[..., 2][m] - 128
    return dict(n_px=int(m.sum()), england_land_mean_a=round(float(a.mean()), 2), england_land_mean_b=round(float(b.mean()), 2),
                england_land_mean_chroma=round(float(np.hypot(a, b).mean()), 2))

def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--tag", required=True); a = ap.parse_args()
    S = AtlasShotB(a.config); od = HERE
    f = S.cfg["out_wh"][0] / S.cfg["plate_wh"][0] * PHONE_F
    allp = dict(shot=S.name, config=a.config, density=S.density, authority=S.authority, approx_areas=S.approx,
                route_ink_p0b={k: dict(v, col_stats=A.colour_stats(v["col"]), pool_stats=A.colour_stats(v["pool"])) for k, v in ROUTE_B.items()},
                route_ink_p0={k: dict(col_stats=A.colour_stats(v["col"]), pool_stats=A.colour_stats(v["pool"])) for k, v in ROUTE_P0.items()},
                emphasis_p0b=dict(hybrid=EMPHASIS_B["hybrid"], terrain=EMPHASIS_B["terrain"]), states={})
    outs = {}
    for st in ("hybrid", "terrain"):
        out, pr = S.render(EMPHASIS_B[st]); inked, mapimg = S._last; outs[st] = out
        p = f"{od}/stills/{a.tag}_atlas_p0b_{STATE_FILE[st]}_16x9.png"
        allp["states"][st] = dict(png=p, md5=A.save(p, out), phone_contrast_dash_only=phone_contrast(S, inked, mapimg, f))
        img_l = inked.copy(); S.draw_labels(img_l, EMPHASIS_B[st]); allp["states"][st]["label_readability"] = label_readability(S, img_l)
        print(p, allp["states"][st]["md5"], flush=True)
    allp["rust"] = dict(terrain_p0=rust_metric(S, A.EMPHASIS["terrain"]), terrain_p0b=rust_metric(S, EMPHASIS_B["terrain"]), hybrid=rust_metric(S, EMPHASIS_B["hybrid"]))
    labs = [dict(text=l["text"], tier=l["tier"], bbox=[int(v) for v in l["bb"]]) for l in S.labels]; H, W = outs["hybrid"].shape[:2]
    x0, cw, whole, cut = A.phone_x0(W, H, S.legs, labs, S.cfg["plate_wh"][0]); allp["phone"] = dict(x0=x0, crop_w=cw, labels_whole=whole, labels_cut=cut, files={})
    for st in ("hybrid", "terrain"):
        ph = cv2.resize(outs[st][:, x0:x0 + cw], (360, 640), interpolation=cv2.INTER_AREA)
        p = f"{od}/phone/{a.tag}_atlas_p0b_{STATE_FILE[st]}_phone360x640.png"; allp["phone"]["files"][st] = dict(path=p, md5=A.save(p, ph))
    rw = S.T.realm_weights()
    allp["realms_raster"] = VR.check_raster(rw, lambda lo, la: S.geom.analytic(np.float64([lo]), np.float64([la]))[0], S.T.lb.shape,
                                            [l["text"] for l in S.labels], R2.REALM_WORDS)
    pj = f"{od}/proofs/{a.tag}_atlas_p0b_proofs.json"; assert not os.path.exists(pj)
    json.dump(allp, open(pj, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)); print(pj)

if __name__ == "__main__":
    main()
