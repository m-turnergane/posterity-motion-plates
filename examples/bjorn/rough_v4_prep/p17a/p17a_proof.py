#!/workspace/mpvenv/bin/python
"""P17A proof (rough v4 prep). Plate plates/P17A_unnamed_captain.png (read-only, md5 fa286390...), lands on L12+L13.
  glints : LOCKED water_v1 glints (same layer params as rough_v2 P06), masked to the sunlit water (masks/p17a_mask_water.png); guards = captain, oars, hull.
  motion : NEW MOTION AWAITING APPROVAL (proof only): hull swell = rigid camera bob (camera rides the hull: <=1.0 px vertical, <=0.05 deg roll, no warp);
           sail ripple = smooth displacement <=0.6 px inside the sail mask only; distant fleet drift = +1.6 px forward over the shot inside the fleet box.
           Displacement is hard-zeroed (feathered 12 px outside) on captain, oars, steering oar, mast, ropes, prow, hull.
  camera : flat push 1.00 -> 1.04 (sstep) centred (0.55, 0.45).
Outputs (refuse overwrite): p17a_proof.mp4, p17a_glints_only.mp4, grabs, p17a_proof_report.json."""
import sys, json, hashlib, subprocess, importlib.util, math, numpy as np, cv2
from pathlib import Path
HERE = Path(__file__).resolve().parent; BJ = HERE.parents[1]; ROOT = BJ.parents[1]; PL = BJ / 'plates/P17A_unnamed_captain.png'
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
PMD5 = md5(PL); assert PMD5 == 'fa2863906d7648c30406adc27d738670'
assert md5(ROOT / 'engine-rnd/water/water_v1.py').startswith('811734e9')
def _load(n, p): s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
WG = _load('water_v1_1_ro', ROOT / 'engine-rnd/water/water_v1_1.py'); WA, GR = WG.W, WG.G
FPS, OW, OH = 30, 1080, 1920; SECS = float(sys.argv[sys.argv.index('--secs') + 1]) if '--secs' in sys.argv else 7.5; N = int(round(SECS * FPS))
P = cv2.cvtColor(cv2.imread(str(PL)), cv2.COLOR_BGR2RGB); H, W = P.shape[:2]; Pf = P.astype(np.float32); s0 = max(OW / W, OH / H) * (1 + 10.0 / OW)   # run-1 fix: +10 px cover slack (bob/roll clamp revealed a 2.4 px reflected strip on the right edge)
MK = json.load(open(HERE / 'masks/p17a_masks.json')); m = lambda n: cv2.imread(str(HERE / f'masks/p17a_mask_{n}.png'), 0) > 127
WATER, GUARD, SAIL, FLEET, NOWARP = m('water'), m('guard'), m('sail'), m('fleet'), m('nowarp')
WCFG = dict(name='P17A_glints', plate=str(PL), seed=617, push=[1.0, 1.04], push_center=[0.55, 0.45], water=MK['water'], protect=MK['protect'], protect_feather=5,
            layers=[dict(type='glints', hp_sigma=3.0, thresh=9, min_dist=6, n_max=60, edge_px=1, sigma=1.5, star=0.25, star_len=4, halo=0.08, halo_sigma=4.0,
                         own_r=3, lift=0.6, dim=0.2, add=0.55, color=[255, 225, 180], rate_lo=[0.5, 1.2], rate_hi=[1.2, 2.6], thresh_t=0.45, power=1.6)])
WS = WA.WaterShot(WCFG)
def sstep(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def feather(mask, r):
    d = cv2.distanceTransform((~mask).astype(np.uint8), cv2.DIST_L2, 5); return np.clip(1 - d / r, 0, 1).astype(np.float32)
nowarp_w = 1 - feather(NOWARP, 12)                                         # 0 on guards, ramps to 1 at 12 px
sail_w = cv2.GaussianBlur(SAIL.astype(np.float32), (0, 0), 10) * nowarp_w; sail_w[NOWARP] = 0
fleet_w = cv2.GaussianBlur(FLEET.astype(np.float32), (0, 0), 8) * nowarp_w; fleet_w[NOWARP] = 0
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
SAIL_A, FLEET_D, BOB_A, ROLL_A = 0.6, 1.6, 1.0, 0.05
def disp(t):
    ph = 2 * math.pi * (XX / 260.0 - t / 3.1) + YY / 180.0
    dx = 0.35 * SAIL_A * np.sin(ph * 0.7 + 1.3) * sail_w + FLEET_D * sstep(t / SECS) * fleet_w
    dy = SAIL_A * np.sin(ph) * sail_w
    return dx, dy
def cam(i, motion):
    t = i / FPS; z = 1.0 + 0.04 * sstep(i / max(N - 1, 1)); s = s0 * z; cx, cy = 0.55, 0.45
    qx = s0 * cx * W + (OW - W * s0) / 2; qy = s0 * cy * H + (OH - H * s0) / 2; ox = qx - s * cx * W; oy = qy - s * cy * H
    A = np.float64([[s, 0, ox], [0, s, oy]])
    if motion:                                                            # rigid bob + roll about frame centre (camera on the hull)
        ang = math.radians(ROLL_A * math.sin(2 * math.pi * t / 5.3 + 0.4)); by = BOB_A * math.sin(2 * math.pi * t / 4.2)
        R = cv2.getRotationMatrix2D((OW / 2, OH / 2), math.degrees(ang), 1.0); A = R @ np.vstack([A, [0, 0, 1]]); A[1, 2] += by
    marg = 3.0                                                           # keep cover: clamp so no edge reveal (bob/roll need a few px slack)
    A[0, 2] = min(-marg, max(OW - s * W + marg, A[0, 2])); A[1, 2] = min(-marg, max(OH - s * H + marg, A[1, 2]))
    return A.astype(np.float32)
def plate_frame(t, motion):
    f = WS.frame(t)
    if motion:
        dx, dy = disp(t); f = cv2.remap(f, XX + dx, YY + dy, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    return f
def writer(path):
    return subprocess.Popen(['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(path)], stdin=subprocess.PIPE)
REP = dict(plate=str(PL), plate_md5_before=PMD5, seconds=SECS, frames=N, water_info=WS.info(), new_motion='AWAITING APPROVAL (proof only)',
           params=dict(sail_amp_px=SAIL_A, fleet_drift_px=FLEET_D, bob_px=BOB_A, roll_deg=ROLL_A, push=[1.0, 1.04]))
# ---- checks: displacement in guards, glint leak, peak displacement
peak = dict(sail=0.0, fleet=0.0); guard_disp = 0.0; leak_out, leak_guard = [], []
for i in range(0, N, 15):
    t = i / FPS; dx, dy = disp(t); mag = np.hypot(dx, dy); guard_disp = max(guard_disp, float(mag[NOWARP].max()))
    peak['sail'] = max(peak['sail'], float(mag[SAIL].max())); peak['fleet'] = max(peak['fleet'], float(mag[FLEET].max()))
    g = WS.frame(t); ch = np.abs(g.astype(int) - P.astype(int)).max(-1) > 0
    leak_out.append(int((ch & ~WATER).sum())); leak_guard.append(int((ch & GUARD).sum()))
REP['checks'] = dict(guard_displacement_max_px=round(guard_disp, 6), sail_disp_peak_px=round(peak['sail'], 3), fleet_disp_peak_px=round(peak['fleet'], 3),
                     glint_changed_px_outside_water=leak_out, glint_changed_px_in_guards=leak_guard,
                     pass_=bool(guard_disp == 0.0 and max(leak_out) == 0 and max(leak_guard) == 0))
den = GR.check_pixel_density((W, H), (OW, OH), (1.0, 1.0), mode='measure', crop_zoom=1.04, name='P17A'); REP['guard_density'] = den
print(json.dumps(REP['checks']), flush=True)
if '--checks' in sys.argv: sys.exit(0)
outs = dict(proof=HERE / 'p17a_proof.mp4', glints=HERE / 'p17a_glints_only.mp4')
for p in outs.values(): assert not p.exists(), p
pa, pb = writer(outs['proof']), writer(outs['glints']); peak_glint = (-1, 0)
for i in range(N):
    t = i / FPS
    g = WS.frame(t); nz = int((np.abs(g.astype(int) - P.astype(int)).max(-1) > 6).sum())
    if nz > peak_glint[1]: peak_glint = (i, nz)
    fb = cv2.warpAffine(g, cam(i, False), (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT); pb.stdin.write(fb.tobytes())
    dx, dy = disp(t); gm = cv2.remap(g, XX + dx, YY + dy, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    fa = cv2.warpAffine(gm, cam(i, True), (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT); pa.stdin.write(fa.tobytes())
    if i in (0, N // 2, N - 1): cv2.imwrite(str(HERE / f'p17a_proof_f{i:03d}.jpg'), cv2.cvtColor(fa, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
    if i % 45 == 0: print('f', i, flush=True)
pa.stdin.close(); pb.stdin.close(); assert pa.wait() == 0 and pb.wait() == 0
i = peak_glint[0]; g = WS.frame(i / FPS); fa = cv2.warpAffine(g, cam(i, False), (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
cv2.imwrite(str(HERE / f'p17a_peak_glint_f{i:03d}.png'), cv2.cvtColor(fa, cv2.COLOR_RGB2BGR))
REP.update(peak_glint_frame=i, peak_glint_px=peak_glint[1], outputs={k: dict(path=str(p), md5=md5(p)) for k, p in outs.items()}, plate_md5_after=md5(PL))
assert REP['plate_md5_after'] == PMD5
json.dump(REP, open(HERE / 'p17a_proof_report.json', 'x'), indent=1, default=str); print('done', REP['outputs'])
