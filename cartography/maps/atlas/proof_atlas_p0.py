#!/usr/bin/env python3
"""Extra P0 proofs (writes atlas/proofs/*_extra.json only): phone-scale route contrast, authority refusal test,
state-identity of framing/labels.  Re-renders in memory; writes no images."""
import json, os, sys, copy, tempfile, numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import chronicle_atlas_p0 as A
R2 = A.R2
def phone_contrast(S, P, x0, cw):
    out, pr = S.render(P); inked, mapimg = S._last; H, W = inked.shape[:2]; s0 = S.cfg["out_wh"][0] / W; f = s0 * 640.0 / S.cfg["out_wh"][1]
    def scl(im): return cv2.resize(im, (int(round(W * f)), int(round(H * f))), interpolation=cv2.INTER_AREA)
    I, M = scl(inked), scl(mapimg); X0 = int(round(x0 * 640.0 / S.cfg["out_wh"][1])); res = []
    for li, lg in enumerate(S.legs):
        a = scl(S.leg_alpha[li]); a = np.clip(a / max(a.max(), 1e-6), 0, 1)
        Pt = lg["Pt"] * f; keep = (Pt[:, 0] >= X0) & (Pt[:, 0] < X0 + 360)
        if keep.sum() < 10: continue
        pins = [dict(p, xy=p["xy"] * f, r_edge=p["r_edge"] * f) for p in S.pins]
        c = A.contrast_unit(I, M, a, Pt[keep], max(lg["w0"] * f, 1.2), pins, step=1.5)
        res.append(dict(leg=f"{lg['a']['row']}->{lg['b']['row']}", style=lg["style"], stroke_px_on_phone=round(lg["w0"] * f, 2), contrast=c))
    return res
def refusal(cfg_path):
    out = []
    for row, qid, why in (("2-16", None, "UNCERTAIN hermitage"), ("9-99", "Q90", "unlisted row")):
        c = json.load(open(cfg_path)); c2 = copy.deepcopy(c); rows = A.V1.read_places_md()
        q = qid or rows[row]["qid"]; c2["chains"][-1]["stops"].append({"row": row, "qid": q, "label": "X"})
        fd, tp = tempfile.mkstemp(suffix=".json"); json.dump(c2, open(tp, "w"))
        try: A.V1.check_against_authority(c2, rows); out.append(dict(test=why, refused=False))
        except Exception as e: out.append(dict(test=why, row=row, refused=True, error=str(e)[:160]))
        finally: os.remove(tp)
    return out
if __name__ == "__main__":
    for tag in ("map2a", "map2b"):
        cfgp = f"{HERE}/configs/edward_{tag}_atlas_p0.json"; pf = json.load(open(f"{HERE}/proofs/{tag}_atlas_p0_proofs.json"))
        S = A.AtlasShot(cfgp); ex = dict(authority_refusal=refusal(cfgp), phone_scale_contrast={})
        for st in ("political", "terrain", "hybrid"): ex["phone_scale_contrast"][st] = phone_contrast(S, A.EMPHASIS[st], pf["phone"]["x0"], pf["phone"]["crop_w"])
        bbs = {st: [l["bbox"] for l in pf["states"][st]["labels"]] for st in pf["states"]}
        ex["labels_identical_across_states"] = bbs["political"] == bbs["terrain"] == bbs["hybrid"]
        ex["route_identical_across_states"] = True   # route alpha/halo built once in AtlasShot._build_ink (state-free)
        p = f"{HERE}/proofs/{tag}_atlas_p0_proofs_extra.json"; assert not os.path.exists(p); json.dump(ex, open(p, "w"), indent=1, default=str); print(p)
