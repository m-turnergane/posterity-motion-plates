"""depth_v1 tests: ONE camera transform per layer per frame (push folded in), uniform scale+translate only, and
composition with a LOCKED effect (dust_v1) as plate_fx without a double camera.
  python tests/test_depth_v1.py proofs/test_depth_v1.json      (refuses to overwrite)"""
import sys, os, json, importlib.util
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
import depth_v1 as D

def load_dust():
    p = HERE.parent / "dust" / "dust_v1.py"; s = importlib.util.spec_from_file_location("dust_v1", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def main(out):
    if os.path.exists(out): sys.exit(f"refusing to overwrite {out}")
    R = {}; ok = True
    sh = D.DepthShot(D._cfg(HERE / "configs/b01_gloucester_kent_drift_v1.json")); size = (540, 960); o = sh.overscan(size); E = D.smooth_progress(180)
    dust = load_dust(); ds = dust.DustShot(json.load(open(HERE / "configs/compose_b01_dust_test.json")))
    # the locked effect's camera must never run inside a depth shot: trap it
    calls = {"push_frame": 0}; real = dust.F3.push_frame
    def trap(*a, **k): calls["push_frame"] += 1; return real(*a, **k)
    dust.F3.push_frame = trap
    plate_fx = lambda t: ds.frame(t).astype(np.float32) / 255.0
    tint = np.zeros((sh.H, sh.W, 4), np.float32); tint[100:140, 100:140] = (0.2, 0.1, 0.0, 0.2)
    layer_fx = {"near": lambda t: tint}
    screen_fx = lambda img, t: img * 0.98 + 0.01
    # 1) WARP_LOG: exactly one warp per layer per frame with all three effect hooks active
    D.WARP_LOG.clear(); ids = [0, 45, 90, 135, 179]
    for i in ids: sh.frame(E[i], size, o, fid=i, plate_fx=plate_fx, layer_fx=layer_fx, screen_fx=screen_fx, t=i / 30)
    cnt = {}
    for t in D.WARP_LOG: cnt[t] = cnt.get(t, 0) + 1
    t1 = dict(warps=len(D.WARP_LOG), expected=len(ids) * len(sh.cards), max_per_layer_frame=max(cnt.values()),
              locked_effect_camera_calls=calls["push_frame"])
    t1["pass_"] = t1["warps"] == t1["expected"] and t1["max_per_layer_frame"] == 1 and calls["push_frame"] == 0; R["one_warp_per_layer_frame_with_fx"] = t1
    # 2) identity plate_fx (returns the plate) changes nothing
    a = sh.frame(E[90], size, o); b = sh.frame(E[90], size, o, plate_fx=lambda t: sh.Pf)
    R["identity_plate_fx"] = dict(max_abs_diff=float(np.abs(a - b).max()), pass_=float(np.abs(a - b).max()) < 1e-5)
    # 3) the dust delta rides the layer's single matrix: warp the delta alone with M_far and compare with (with_fx - without_fx)
    d = plate_fx(2.0) - sh.Pf; fx = sh.frame(E[90], size, o, plate_fx=plate_fx, t=2.0)
    M = sh.layer_affine(0, E[90], size, o); import cv2
    pred = cv2.warpAffine(d, M, size, flags=cv2.INTER_LANCZOS4); vis = (sh.frame(E[90], size, o) * 0 + 1)
    zone = cv2.warpAffine((np.abs(d).max(-1) > 0.02).astype(np.float32), M, size) > 0.5
    near_cover = cv2.warpAffine(sh.cards[1]["a"], sh.layer_affine(1, E[90], size, o), size) < 0.01
    m = zone & near_cover
    err = np.abs((fx - a) - pred)[m].mean() if m.any() else 0.0
    R["fx_delta_rides_layer_matrix"] = dict(px=int(m.sum()), mean_abs_err=round(float(err), 5),
                                           pass_=bool(m.sum() > 50 and err < 0.01))
    # what a second (dust-side) push would have done to the same delta: displacement of an off-centre mote
    R["fx_delta_rides_layer_matrix"]["note"] = "dust_v1 normally applies F3.push_frame itself; here it was trapped and called 0 times"
    # 4) dot test + matrix form on every frame
    R["dot_test"] = D.dot_test(sh, size, o, E[-1])
    Ms = [sh.layer_affine(k, E[i], size, o) for k in range(len(sh.cards)) for i in range(180)]
    R["uniform_scale_translate_only_all_180_frames"] = bool(all(abs(M[0, 1]) < 1e-9 and abs(M[1, 0]) < 1e-9 and abs(M[0, 0] - M[1, 1]) < 1e-6 for M in Ms))
    # 5) push folded in: layer zoom at e=0/1 vs house push 1.00 -> 1.06 (near layer gain 1.0 hits 1.06 exactly)
    R["push_folded"] = {sh.layers[k]["name"]: [round(sh.layer_params(k, 0.0)[0], 5), round(sh.layer_params(k, 1.0)[0], 5)] for k in range(len(sh.cards))}
    ok = t1["pass_"] and R["identity_plate_fx"]["pass_"] and R["fx_delta_rides_layer_matrix"]["pass_"] and R["dot_test"]["pass_"] and R["uniform_scale_translate_only_all_180_frames"]
    R["pass"] = bool(ok); json.dump(R, open(out, "x"), indent=1, default=float); print(json.dumps(R, indent=1, default=float)); return ok

if __name__ == "__main__": sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else "proofs/test_depth_v1.json") else 1)
