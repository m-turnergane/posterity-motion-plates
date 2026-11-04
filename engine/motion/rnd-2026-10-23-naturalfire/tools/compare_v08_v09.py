"""Like-for-like v08 vs v09 on the DECODED FINAL mp4s (what the owner sees), vs the v2c static twin.
Regions (output space, camera-mapped at frame 90): prod v2b2 flame masks (v08's area) and v09 cores, v09 ext.
Metrics: hp_energy (hprise), output dF%, and phone legibility = mean |L(t+10)-L(t)| (0.33 s) at 360x640 inside the region (8-bit L)."""
import sys, json, subprocess, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks; from flame_v09 import load_masks_v09; from hprise import hp_metrics
def dec(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, P.H, P.W, 3)
prodm = load_masks(); cores, exts = load_masks_v09(); box = P.plate_box(); seg = dict(P.SEG_POC); seg["frames"] = 180
U = np.asarray(P.frame_out(np.repeat((np.maximum.reduce(prodm + cores + exts) * 255).astype(np.float32)[..., None], 3, 2), box, seg, 90))[..., 0] > 0
_ys, _xs = np.nonzero(U); CY0, CX0 = (_ys.min() - 30) // 3 * 3, (_xs.min() - 30) // 3 * 3; CY1, CX1 = CY0 + ((_ys.max() + 30 - CY0) // 3 + 1) * 3, CX0 + ((_xs.max() + 30 - CX0) // 3 + 1) * 3
V = {k: dec(p)[:, CY0:CY1, CX0:CX1].copy() for k, p in (("v08", "P05_naturalfire_poc_final_v08.mp4"), ("v09", "P05_naturalfire_poc_final_v09.mp4"), ("static", "work/final_v09_v2cstatic_lossless.mp4"))}
om = lambda m: (np.asarray(P.frame_out(np.repeat((m * 255).astype(np.float32)[..., None], 3, 2), box, seg, 90))[..., 0] > 127)[CY0:CY1, CX0:CX1]
R = {}
for i in range(3):
    for nm, m in (("prod", prodm[i]), ("v09core", cores[i]), ("v09ext", exts[i])):
        reg = om(m) if nm != "v09ext" else (np.asarray(P.frame_out(np.repeat((m * 255).astype(np.float32)[..., None], 3, 2), box, seg, 90))[..., 0] > 76)[CY0:CY1, CX0:CX1]
        ys = np.nonzero(reg.any(1))[0]; Hf = float(ys.max() - ys.min() + 1); regp = cv2.resize(reg.astype(np.float32), (reg.shape[1] // 3, reg.shape[0] // 3), interpolation=cv2.INTER_AREA) > 0.5
        row = {}
        for k, X in V.items():
            L = X.astype(np.float32).mean(3); d = np.abs(np.diff(L, axis=0))[:, reg].mean(1) / L[1:, reg].mean(1)
            Lp = np.stack([cv2.resize(l, (l.shape[1] // 3, l.shape[0] // 3), interpolation=cv2.INTER_AREA) for l in L])
            e = dict(dF_mean=round(100 * float(d.mean()), 2), dF_max=round(100 * float(d.max()), 2), phone_dL_0p33s=round(float(np.abs(Lp[10:] - Lp[:-10])[:, regp].mean()), 2) if regp.any() else None)
            if nm != "v09ext": h = hp_metrics(list(X[::1]), 30.0, reg, Hf); e.update(hp_energy=h["hp_energy"], hp_rise=h["hp_rise_hps"], corr=h["corr_0p5to3s_max"])
            row[k] = e
        R[f"c{i}_{nm}"] = row; print(f"c{i}_{nm}", row, flush=True)
json.dump(R, open("qc/final_v09_vs_v08_like_for_like.json", "x"), indent=1)
