"""Render the 6 s POC (animated flame plate through the locked b3 engine + prod camera) and the v2c static twin with the same push.
Writes lossless intermediates in work/ and per-frame QC in qc/. Never overwrites: refuses if outputs exist."""
import sys, os, json, subprocess, time, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from flame import FlameSet; from specs import load_masks
tag = sys.argv[1]; spec = json.load(open(sys.argv[2])); N = int(sys.argv[3]) if len(sys.argv) > 3 else 180
seg = dict(P.SEG_POC); seg["frames"] = 180
pocp, stp = f"work/{tag}_poc_lossless.mp4", f"work/{tag}_v2cstatic_lossless.mp4"
for f in (pocp, stp, f"qc/{tag}_render_qc.json"): assert not os.path.exists(f), f
M = P.load_engine(); E = M.Engine(P.load_cfg()); box = P.plate_box(); masks = load_masks(); FS = FlameSet(E, masks, spec["flames"])
plate0 = FS.plate0; union = FS.union; Hh, Ww = union.shape
cand = json.load(open(P.MASKS / "P05_candles.json")); fh = np.zeros((Hh, Ww), np.uint8); cv2.fillPoly(fh, [np.array(p, np.int32) for p in cand["face_hand_polys"]], 1)
protect = cv2.imread(str(P.MASKS / "P05_protect.png"), 0) > 0
prot_all = protect | (fh > 0)
# glow zone exactly as prod p05static QC (engine space): layer-0 relight mask > .02 minus dilated flame zones and sprite boxes
cfg = P.load_cfg(); rel = M.load_mask(cfg["layers"][0]["mask"], plate0.shape[:2])
flz = cv2.dilate(union.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
for L in cfg["layers"]:
    for q in L["params"]["sources"]:
        x, y = q["xy"]; fw, fh_ = q["flame"]; flz[max(0, int(y - fh_ * 1.4)) - 2:int(y + fh_ * 0.4) + 3, max(0, int(x - fw * 2)) - 2:int(x + fw * 2) + 3] = True
glowz = (rel > 0.02) & ~flz
# output-space flame support: push the union mask (as an image) through the same camera, dilate 4 px for resampling support
def ff(cmd, p): return subprocess.Popen(["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{P.W}x{P.H}", "-r", "30", "-i", "pipe:0", "-an", *cmd, "-r", "30", p], stdin=subprocess.PIPE)
pp, ps = ff(P.ENC_INTER, pocp), ff(P.ENC_INTER, stp)
q = dict(plate_outside_union_maxabs=0.0, plate_protected_maxabs=0.0, engine_outside_union_maxabs=0.0, out_outside_support_maxabs=0, out_outside_support_px_changed=0)
glow_p, glow_s, flame_p, flame_s, act = [], [], [], [], []; t0 = time.time()
mimg = np.repeat((union.astype(np.float32) * 255)[..., None], 3, 2)
for fi in range(N):
    t = fi / 30.0
    pl = FS.plate_at(t)
    q["plate_outside_union_maxabs"] = max(q["plate_outside_union_maxabs"], float(np.abs(pl - plate0)[~union].max()))
    q["plate_protected_maxabs"] = max(q["plate_protected_maxabs"], float(np.abs(pl - plate0)[prot_all].max()))
    E.plate = pl; ip, _, _ = E.render(t); E.plate = plate0; is_, _, _ = E.render(t)
    q["engine_outside_union_maxabs"] = max(q["engine_outside_union_maxabs"], float(np.abs(ip - is_)[~union].max()))
    glow_p.append(float(ip.mean(2)[glowz].mean())); glow_s.append(float(is_.mean(2)[glowz].mean()))
    flame_p.append([float(ip.mean(2)[m > 0.5].mean()) for m in masks]); flame_s.append([float(is_.mean(2)[m > 0.5].mean()) for m in masks])
    act.append([round(f.last["A"], 4) for f in FS.fl] + [round(f.flare, 4) for f in FS.fl])
    op = np.asarray(P.frame_out(ip, box, seg, fi)); os_ = np.asarray(P.frame_out(is_, box, seg, fi))
    sup = np.asarray(P.frame_out(mimg, box, seg, fi))[..., 0] > 0; sup = cv2.dilate(sup.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    d = np.abs(op.astype(int) - os_)[~sup]; q["out_outside_support_maxabs"] = max(q["out_outside_support_maxabs"], int(d.max())); q["out_outside_support_px_changed"] += int((d.max(1) > 0).sum())
    pp.stdin.write(op.tobytes()); ps.stdin.write(os_.tobytes())
    if fi % 30 == 0: print(fi, round(time.time() - t0, 1), q, flush=True)
pp.stdin.close(); ps.stdin.close(); pp.wait(); ps.wait()
gp, gs = np.array(glow_p), np.array(glow_s)
q.update(frames=N, glow_engine=dict(poc_amp=round(float(gp.max() - gp.min()), 4), static_amp=round(float(gs.max() - gs.min()), 4), corr=round(float(np.corrcoef(gp, gs)[0, 1]), 6), max_abs_diff=round(float(np.abs(gp - gs).max()), 6)),
         flame_mean_series_poc=flame_p, flame_mean_series_static=flame_s, glow_series_poc=glow_p, glow_series_static=glow_s, activity_flare=act, spec=spec, sec_per_frame=round((time.time() - t0) / N, 3))
json.dump(q, open(f"qc/{tag}_render_qc.json", "w"))
print("DONE", {k: v for k, v in q.items() if not isinstance(v, list) and k != "spec"})
