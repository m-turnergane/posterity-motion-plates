"""B13a/B13b registration check (Báthory rough v1). Read-only on plates. Writes b13_registration.json here."""
import cv2, numpy as np, json
from pathlib import Path
PL = Path("/workspace/posterity/standalones/bathory/v2/plates")
A = cv2.imread(str(PL / "b13a_doors_open.png")); B = cv2.imread(str(PL / "b13b_doors_shut.png"))
H = min(A.shape[0], B.shape[0]); W = A.shape[1]
ga = cv2.cvtColor(A[:H], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255; gb = cv2.cvtColor(B[:H], cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
mask = np.ones((H, W), np.uint8); mask[90:1420, 270:941] = 0            # exclude doors + gap + lit floor (plate px; the intended change)
res = {"plate_a": [A.shape[1], A.shape[0]], "plate_b": [B.shape[1], B.shape[0]]}
out = {}
for mode, name in ((cv2.MOTION_TRANSLATION, "translation"), (cv2.MOTION_AFFINE, "affine")):
    w = np.eye(2, 3, dtype=np.float32)
    cc, w = cv2.findTransformECC(cv2.GaussianBlur(ga, (0, 0), 1.5), cv2.GaussianBlur(gb, (0, 0), 1.5), w, mode,
                                 (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7), mask, 5)
    out[name] = dict(cc=float(cc), warp=w.tolist())
res["ecc_b_to_a"] = out
# per-region phase correlation on static regions
regs = {"silhouette": (200, 1500, 0, 270), "silhouette_upper": (250, 700, 120, 300), "floor_bottom": (1430, H, 0, 941), "top_lintel": (0, 90, 0, 941)}
pc = {}
for k, (y0, y1, x0, x1) in regs.items():
    (dx, dy), r = cv2.phaseCorrelate(ga[y0:y1, x0:x1].copy(), gb[y0:y1, x0:x1].copy(), cv2.createHanningWindow((x1 - x0, y1 - y0), cv2.CV_32F))
    pc[k] = dict(dx=round(dx, 3), dy=round(dy, 3), resp=round(r, 3))
res["phase_corr_b_vs_a_plate_px"] = pc
wA = np.array(out["affine"]["warp"]); s = 1080 / 941 * 1.0
# max displacement over the frame implied by the affine, in output px at 1080x1920 cover (x1.1477)
pts = np.array([[0, 0, 1], [W, 0, 1], [0, H, 1], [W, H, 1], [W / 2, H / 2, 1]], float)
disp = np.abs(pts @ wA.T - pts[:, :2]).max()
res["affine_max_disp_plate_px"] = round(float(disp), 3); res["affine_max_disp_out_px"] = round(float(disp) * max(1080 / W, 1920 / H) * 1.06, 3)
tr = out["translation"]["warp"]; res["translation_out_px"] = [round(tr[0][2] * 1920 / H * 1.06, 3), round(tr[1][2] * 1920 / H * 1.06, 3)]
res["verdict"] = "PASS (<=2 px at 1080x1920, no alignment needed)" if max(res["affine_max_disp_out_px"], max(map(abs, res["translation_out_px"]))) <= 2 else "ALIGN B13b to B13a"
json.dump(res, open(Path(__file__).with_name("b13_registration.json"), "w"), indent=1); print(json.dumps(res, indent=1))
