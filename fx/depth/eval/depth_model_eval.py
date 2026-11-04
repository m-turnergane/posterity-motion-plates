"""DEPTH_MODEL_EVAL: hand polygons vs Depth Anything V2 Small (+hand region, guided edge) on ONE plate (b10 Corfe).
Same shot, same camera, same fill, same compositor; only the near-card matte differs.
  python eval/depth_model_eval.py eval/depth_model_eval.json eval/depth_model_eval_still.png"""
import sys, os, json, time, math, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import depth_v1 as D

HAND = "configs/b10_corfe_letter_drift_HANDPOLY_eval.json"; HYB = "configs/b10_corfe_letter_drift_v1.json"

def edge_metrics(sh):
    """Model-independent: does the matte contour sit on real image edges? Sobel |grad| of plate luma sampled on the
    alpha=0.5 contour, normalised by the image's median |grad|; plus share of contour px on a strong edge (> p80)."""
    g = D.luma(sh.Pf); gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3); G = np.hypot(gx, gy)
    G = cv2.dilate(G, np.ones((3, 3), np.uint8))          # +-1 px tolerance
    a = sh.cards[1]["a"]; m = (a >= 0.5).astype(np.uint8)
    cs, _ = cv2.findContours(m, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE); pts = np.concatenate([c[:, 0] for c in cs])
    H, W = a.shape; ok = (pts[:, 0] > 2) & (pts[:, 0] < W - 3) & (pts[:, 1] > 2) & (pts[:, 1] < H - 3)
    sm = poly = D.poly_mask((H, W), sh.layers[1].get("seams", []), W, H) if sh.layers[1].get("seams") else np.zeros((H, W), bool)
    pts = pts[ok]; pts = pts[~sm[pts[:, 1], pts[:, 0]]]       # ignore frame border and the deliberate soft floor seam
    v = G[pts[:, 1], pts[:, 0]]; med = float(np.median(G)); p80 = float(np.percentile(G, 80))
    return dict(contour_px=int(len(v)), grad_on_contour_rel_median=round(float(v.mean() / med), 2), share_on_strong_edge=round(float((v > p80).mean()), 3))

def wrong_band(sh):
    """Width of the 'transition' band (0.02<a<0.98) as a share of contour length = matte softness (halo carrier)."""
    a = sh.cards[1]["a"]; band = (a > 0.02) & (a < 0.98)
    cs, _ = cv2.findContours((a >= 0.5).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE); per = sum(cv2.arcLength(c, True) for c in cs)
    return round(float(band.sum() / max(per, 1)), 2)

def main(out_json, out_png):
    for p in (out_json, out_png):
        if os.path.exists(p): sys.exit(f"refusing to overwrite {p}")
    R = {}
    # runtime: model inference uncached (fresh session) on the plate
    import onnxruntime as ort
    P = D.load_rgb(json.load(open(HYB))["plate"]); t0 = time.time()
    sess = ort.InferenceSession(str(D.MODEL), providers=["CPUExecutionProvider"]); t_load = time.time() - t0
    h, w = P.shape[:2]; s = 518 / min(h, w); W, H = int(round(w * s / 14)) * 14, int(round(h * s / 14)) * 14
    x = cv2.resize(P, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    ts = []
    for _ in range(3): t0 = time.time(); sess.run(None, {sess.get_inputs()[0].name: x}); ts.append(time.time() - t0)
    R["model"] = dict(name="Depth Anything V2 Small (onnx-community, fp32 ONNX, Apache-2.0)", runtime="onnxruntime CPU (already in venv; no pip install)",
                      weights_mb=round(os.path.getsize(D.MODEL) / 1e6, 1), session_load_s=round(t_load, 2), infer_s_min=round(min(ts), 2), net_in=[W, H],
                      cache_kb_per_plate=round(sum(os.path.getsize(D.CACHE / f) for f in os.listdir(D.CACHE)) / 1e3 / max(len(os.listdir(D.CACHE)), 1), 1))
    sh = {}
    for k, p in (("hand_poly", HAND), ("da2_hybrid", HYB)):
        cfg = json.load(open(p)); t0 = time.time(); s_ = D.DepthShot(cfg); bt = time.time() - t0; sh[k] = s_
        pr = json.load(open(f"proofs/proof_{cfg['name']}.json"))["formats"]["1080x1920"]
        R[k] = dict(config=p, build_s=round(bt, 2), edges=edge_metrics(s_), soft_band_px=wrong_band(s_),
                    disocclusion=pr["disocclusion"], rigidity_pass=all(r["pass_"] for r in pr["rigidity"]),
                    near_own_frac=round(float(s_.hard[1].mean()), 4))
    R["hand_poly"]["authoring"] = "2 traced polygons, 44 vertices, ~15 min incl. checking; still misses hair curls, horse ears, cloak fur, spear tips"
    R["da2_hybrid"]["authoring"] = "1 threshold (depth_min 0.32) + 1 floor-seam box, ~3 min; model run once per plate (cached)"
    a, b = sh["hand_poly"].cards[1]["a"] >= 0.5, sh["da2_hybrid"].cards[1]["a"] >= 0.5
    R["label_disagreement_frac"] = round(float((a ^ b).mean()), 4)
    # still: three boundary crops (hair, horse ears/head, hand+letter) at max offset e=1, 9:16, hand | hybrid, plus matte overlays
    size = (1080, 1920); rows = []
    crops = [(0.24, 0.29, 0.46, 0.43), (0.0, 0.31, 0.22, 0.45), (0.45, 0.49, 0.75, 0.62)]
    for k in ("hand_poly", "da2_hybrid"):
        s_ = sh[k]; o = s_.overscan(size); img = s_.frame(1.0, size, o)
        M = s_.layer_affine(1, 1.0, size, o); A = cv2.warpAffine(s_.cards[1]["a"], M, size, flags=cv2.INTER_LINEAR)
        ov = img * 0.55 + np.dstack([0 * A, A, 0 * A]) * 0.45
        tiles = []
        for (x0, y0, x1, y1) in crops:
            p0 = M @ [x0 * s_.W, y0 * s_.H, 1]; p1 = M @ [x1 * s_.W, y1 * s_.H, 1]
            X0, Y0, X1, Y1 = [int(round(v)) for v in (p0[0], p0[1], p1[0], p1[1])]
            X0, Y0 = max(X0, 0), max(Y0, 0)
            for im in (img, ov):
                t = np.clip(im[Y0:Y1, X0:X1], 0, 1); t = cv2.resize(t, (360, int(360 * t.shape[0] / t.shape[1])), interpolation=cv2.INTER_AREA)
                tiles.append(t)
        hmax = max(t.shape[0] for t in tiles); tiles = [np.pad(t, ((0, hmax - t.shape[0]), (0, 4), (0, 0))) for t in tiles]
        row = np.hstack(tiles); lab = np.zeros((34, row.shape[1], 3), np.float32)
        lab = (lab * 255).astype(np.uint8); cv2.putText(lab, {"hand_poly": "HAND POLYGONS (no model)", "da2_hybrid": "DEPTH ANYTHING V2 SMALL + hand region + guided edge"}[k] + "   | frame at max offset, 9:16 | crop / matte overlay", (8, 24), 0, 0.7, (255, 255, 255), 2); lab = lab.astype(np.float32) / 255
        rows += [lab, row]
    out = (np.vstack(rows) * 255).astype(np.uint8); cv2.imwrite(out_png, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    json.dump(R, open(out_json, "w"), indent=1); print(json.dumps(R, indent=1))

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
