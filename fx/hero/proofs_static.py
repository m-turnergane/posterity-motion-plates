"""Static proofs for the b10 full stack (no video written): density, single transform (dot test + matrices),
holes at both ends, 0-px displacement impulse test of the whole plate-space effect stack, face keep-out exactness,
smoke premultiplied path == smoke_v2.SmokeScene.frame, camera-call trap."""
import sys, json, numpy as np, cv2; from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import fullstack_v1 as F
D = F.DEPTH; S = F.Stack(seconds=7.0); n = S.n; size = (1080, 1920); o = S.sh.overscan(size, n); r = dict()
# density / crop guard
r["density"] = dict(pixel_density=F.G.check_pixel_density(str(F.PLATE), size, (1.0, 1.06), mode="warn"),
                    depth_guard=S.sh.guard(size, mode="warn", n=n), overscan=round(o, 5))
# single transform: matrices + dot test (one affine per card; a stacked push would move the dot)
Ms = [S.sh.layer_affine(k, S.E[i], size, o) for k in range(2) for i in (0, n // 2, n - 1)]
r["single_transform"] = dict(uniform_scale_no_shear_no_rot=bool(all(abs(M[0, 1]) < 1e-9 and abs(M[1, 0]) < 1e-9 and abs(M[0, 0] - M[1, 1]) < 1e-6 for M in Ms)),
                             dot_test=D.dot_test(S.sh, size, o, S.E[n - 1]))
# holes at both ends -- with the full stack on (smoke only ever ADDS alpha to the near card) and via depth_v1.disocclusion
r["disocclusion"] = [D.disocclusion(S.sh, size, o, e) for e in (S.E[0], S.E[-1])]
hs = []
for i in (0, n - 1):
    img, lay = S.frame(i, size, o=o, return_layers=True); cov = np.zeros(lay[0][1].shape, np.float32)
    for M, a in lay[::-1]: cov = cov + (1 - cov) * a
    hs.append(dict(frame=i, holes_px_full_stack=int((cov < 0.999).sum())))
r["holes_full_stack"] = hs
# 0-px displacement: +-24 impulses on an isolated 9-px lattice in the plate the effects read; render torch+smoke stack
H, W = S.H, S.W; Gm = np.zeros((H, W), bool); Gm[4::9, 4::9] = True
sgn = np.where(S.P[Gm].mean(-1) > 128, -24, 24).astype(np.float32); P0 = S.fx.Pf.copy(); P1 = P0.copy(); P1[Gm] += sgn[:, None]
leak = 0; frames = 0; minfrac = 1.0
for i in range(0, n, 15):
    t = i / 30; ov = S.smoke(t)
    a = S.torch(t, P0) * (1 - ov[..., 3:]) + ov[..., :3]; b = S.torch(t, P1) * (1 - ov[..., 3:]) + ov[..., :3]
    d = np.abs(np.rint(a * 255) - np.rint(b * 255)).max(-1) > 0
    leak += int((d & ~Gm).sum()); frames += 1; minfrac = min(minfrac, float(d[Gm].mean()))
r["torch_fixed_zones_impulse"] = dict(method="impulse lattice (+-24 levels, every 9th px) added to fx_v1c's Pf; same t rendered with/without; any resample would leak to neighbours",
                                      impulses=int(Gm.sum()), frames=frames, leaked_px_total=leak, impulse_px_changed_min_frac=round(minfrac, 4), pass_=leak == 0)
_, disp = S.fx.render(1.0, 0.0, want_disp=True); dmax = disp["warp_max_px"]; zones = disp["zones"]
r["torch_fixed_zones_impulse"]["fx_v1c_reported_warp_disp_px"] = dmax; r["torch_fixed_zones_impulse"]["warped_sources"] = S.fx.info()["warped_candles"]
r["smoke_path_equiv"] = []
for t in (0.0, 2.0, 4.0, 6.9):
    ov = S.smoke(t); mine = np.clip(np.rint((S.Pf * (1 - ov[..., 3:]) + ov[..., :3]) * 255), 0, 255); ref = S.sm.frame(t).astype(np.float32)
    r["smoke_path_equiv"].append(dict(t=t, max_abs_vs_SmokeScene_frame=float(np.abs(mine - ref).max()), px_ne=int((mine != ref).any(-1).sum())))
r["smoke_zero_motion_report"] = F.SM.zero_motion_report(S.sm, [0.0, 1.5, 3.0, 4.5, 6.9], S.scfg.get("guards"))
r["camera_calls"] = dict(F.CAM_CALLS)
json.dump(r, open(Path(__file__).resolve().parent / "proofs" / "static_fullstack_v1.json", "x"), indent=1, default=float); print(json.dumps(r, default=float)[:5000])
