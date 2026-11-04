#!/usr/bin/env python3
"""make_p1 -- renders the three p1 palette treatments of map 2b + phone crops, comparison sheet, proofs JSON, README.
Writes only new files under atlas/p1/ (A.save refuses to overwrite).  Usage: python make_p1.py"""
import os, sys, json, datetime, numpy as np, cv2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronicle_atlas_p1 as P
A, B, R2, VR, PA = P.A, P.B, P.R2, P.VR, P.PA
OUT = os.environ.get("P1_OUT", HERE)   # dry runs: P1_OUT=/tmp/...
CFG = f"{HERE}/configs/edward_map2b_atlas_p1.json"; TAG = "p1_map2b"; NAMES = ("heraldic", "illuminated", "campaign")

def J(o): return o.tolist() if hasattr(o, "tolist") else (float(o) if isinstance(o, (np.floating,)) else (int(o) if isinstance(o, np.integer) else str(o)))

def choose_phone(S):
    """608-px window of the 1920 still: no label cut by the edge; most continental pins wholly inside; most continental
    route inside; then centred on the continental route."""
    sx = S.cfg["out_wh"][0] / S.cfg["plate_wh"][0]; W, H = S.cfg["out_wh"]; cw = int(round(H * 9 / 16))
    cont = [lg for lg in S.legs if lg["a"]["row"] >= "2-08"]; Pc = np.concatenate([lg["Pt"] for lg in cont]) * sx
    cx = 0.5 * (Pc[:, 0].min() + Pc[:, 0].max()); pins = [p for p in S.pins if p["row"] >= "2-08"]; best = None
    for x0 in range(0, W - cw + 1):
        cut = [l["text"] for l in S.labels if l["bb"][0] * sx < x0 + cw and l["bb"][2] * sx > x0
               and not (x0 <= l["bb"][0] * sx and l["bb"][2] * sx <= x0 + cw)]
        npin = sum(1 for p in pins if x0 <= (p["xy"][0] - p["r_outer_max"]) * sx and (p["xy"][0] + p["r_outer_max"]) * sx <= x0 + cw)
        ni = int(((Pc[:, 0] >= x0) & (Pc[:, 0] < x0 + cw)).sum())
        marg = min([min((p["xy"][0] - p["r_outer_max"]) * sx - x0, x0 + cw - (p["xy"][0] + p["r_outer_max"]) * sx) for p in pins
                    if x0 <= (p["xy"][0] - p["r_outer_max"]) * sx and (p["xy"][0] + p["r_outer_max"]) * sx <= x0 + cw] or [0])
        key = (-len(cut), npin, ni // 100, min(marg, 24) // 4, -abs(x0 + cw / 2 - cx))
        if best is None or key > best[0]: best = (key, x0)
    x0 = best[1]
    whole = [l["text"] for l in S.labels if x0 <= l["bb"][0] * sx and l["bb"][2] * sx <= x0 + cw]
    cut = [l["text"] for l in S.labels if l["bb"][0] * sx < x0 + cw and l["bb"][2] * sx > x0 and l["text"] not in whole]
    pin_in = [p["row"] for p in S.pins if x0 <= (p["xy"][0] - p["r_outer_max"]) * sx and (p["xy"][0] + p["r_outer_max"]) * sx <= x0 + cw]
    return dict(x0=x0, crop_w=cw, labels_whole=whole, labels_cut=cut, pins_whole=pin_in, continental_centre_x=round(float(cx), 1))

def label_collisions(S, d):
    """Pairwise label box overlaps + route ink / keyline / border ink pixels under glyphs (L.a > 0.3), plate px."""
    H, W = S.T.lb.shape; res = dict(pairs=[], under_glyph=[])
    bbs = [(l["text"], l["L"].bbox()) for l in S.labels]
    for i in range(len(bbs)):
        for j in range(i + 1, len(bbs)):
            a, b = bbs[i][1], bbs[j][1]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]: res["pairs"].append([bbs[i][0], bbs[j][0]])
    key = np.maximum(S.key["documented"], S.key["claimed"])
    for l in S.labels:
        L = l["L"]; x0, y0, x1, y1 = L.bbox(); cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        g = L.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] > 0.3; sl = (slice(cy0, cy1), slice(cx0, cx1))
        res["under_glyph"].append(dict(text=l["text"], glyph_px=int(g.sum()), route_ink_px=int((g & (d["ink_a"][sl] > 0.1)).sum()),
                                       keyline_px=int((g & (key[sl] > 0.1)).sum()), border_ink_px=int((g & (d["ba"][sl] > 0.1)).sum())))
    res["n_collisions"] = len(res["pairs"]) + sum(1 for u in res["under_glyph"] if u["route_ink_px"] or u["keyline_px"] or u["border_ink_px"])
    return res

def main():
    for sd in ("stills", "phone", "sheets", "proofs"): os.makedirs(f"{OUT}/{sd}", exist_ok=True)
    S = P.AtlasShotP1(CFG); f = B.PHONE_F * S.cfg["out_wh"][0] / S.cfg["plate_wh"][0]
    ph = choose_phone(S); x0, cw = ph["x0"], ph["crop_w"]; sxp = S.cfg["plate_wh"][0] / S.cfg["out_wh"][0]
    xr = (int(x0 * sxp), int((x0 + cw) * sxp))   # plate px (phone_contrast_p1 filters on plate x)
    texts = [l["text"] for l in S.labels]; allowed = [s.get("label") for c in S.cfg["chains"] for s in c["stops"] if s.get("label")]
    geo = VR.check_geometry()
    rw = S.T.realm_weights(); l2p = lambda lo, la: S.geom.analytic(np.float64([lo]), np.float64([la]))[0]
    proofs = dict(generated_et=datetime.datetime.now().strftime("%Y-%m-%d %H:%M ET"), config=CFG, shot=S.name,
                  realm_verifier_geometry=dict(n=len(geo), n_ok=sum(1 for g in geo if g["ok"]), fails=[g for g in geo if not g["ok"]]),
                  realm_raster_soft=VR.check_raster(rw, l2p, S.T.lb.shape, texts, R2.REALM_WORDS),
                  realm_raster_painted=VR.check_raster(S.Pa.onehot(5), l2p, S.T.lb.shape, texts, R2.REALM_WORDS),
                  authority_refusal=PA.refusal(CFG),
                  text_on_screen=dict(labels=texts, allowed_place_labels=allowed + ["Ireland"],
                                      realm_words_found=[t for t in texts if any(r in t.lower() for r in R2.REALM_WORDS)],
                                      other_text="none (no legend, title, date, realm name, watermark, vignette, letterbox drawn)"),
                  pins=[p["row"] for p in S.pins], phone=ph, route_ink=P.ROUTE_P1, treatments={})
    outs = {}
    for n in NAMES:
        Pt = P.TREAT[n]; r = dict(concept=Pt["concept"], palette_rgb=Pt["pal"], sea_rgb=Pt["sea"], paper_rgb=Pt["paper"], ink_rgb=Pt["ink"],
                                  flanders_rgb=[int(round(v)) for v in P.pigment_rgb(Pt, S.Pa, "flanders", None)], files={})
        o0, d0 = S.render(n, routes=False); o1, d1 = S.render(n, routes=True)
        phone = cv2.resize(o1[:, x0:x0 + cw], (360, 640), interpolation=cv2.INTER_AREA)
        small = cv2.resize(o1, (640, 360), interpolation=cv2.INTER_AREA)
        for k, p, im in (("noroute", f"stills/{TAG}_{n}_noroute_1920x1080.png", o0), ("route", f"stills/{TAG}_{n}_route_1920x1080.png", o1),
                         ("phone", f"phone/{TAG}_{n}_route_phone360x640.png", phone), ("full640", f"phone/{TAG}_{n}_route_640x360.png", small)):
            r["files"][k] = dict(path=f"atlas/p1/{p}", md5=A.save(f"{OUT}/{p}", im)); print(p, r["files"][k]["md5"], flush=True)
        outs[n] = (o0, o1, phone)
        r["phone_contrast_full_frame"] = P.phone_contrast_p1(S, d1["inked"], d1["mapimg"], f)
        r["phone_contrast_in_phone_crop"] = P.phone_contrast_p1(S, d1["inked"], d1["mapimg"], f, x_range=xr)
        r["deltaE00_neighbours"] = P.realm_separability(S, d1["mapimg"], d1["ba"])
        r["within_realm_spread"] = P.within_realm_spread(S, d1["mapimg"])
        r["label_collisions"] = label_collisions(S, d1)
        r["label_readability"] = B.label_readability(S, d1["plate"])
        proofs["treatments"][n] = r
    # comparison sheet: rows = treatments, cols = no-route, route, phone. No text.
    g = 12; cwid = 960; ch = 540; pw = int(round(360 * ch / 640))
    sheet = np.full((g + 3 * (ch + g), g + cwid + g + cwid + g + pw + g, 3), 20, np.uint8)
    for i, n in enumerate(NAMES):
        o0, o1, phn = outs[n]; y = g + i * (ch + g)
        sheet[y:y + ch, g:g + cwid] = cv2.resize(o0, (cwid, ch), interpolation=cv2.INTER_AREA)
        sheet[y:y + ch, 2 * g + cwid:2 * g + 2 * cwid] = cv2.resize(o1, (cwid, ch), interpolation=cv2.INTER_AREA)
        sheet[y:y + ch, 3 * g + 2 * cwid:3 * g + 2 * cwid + pw] = cv2.resize(phn, (pw, ch), interpolation=cv2.INTER_AREA)
    sp = f"sheets/{TAG}_compare.png"; proofs["sheet"] = dict(path=f"atlas/p1/{sp}", md5=A.save(f"{OUT}/{sp}", sheet),
                                                            layout="rows heraldic/illuminated/campaign; cols no-route 960x540, route 960x540, phone 304x540")
    print(sp, proofs["sheet"]["md5"])
    pj = f"{OUT}/proofs/{TAG}_proofs.json"; assert not os.path.exists(pj)
    json.dump(proofs, open(pj, "w"), indent=1, default=J); print(pj)

if __name__ == "__main__":
    main()
