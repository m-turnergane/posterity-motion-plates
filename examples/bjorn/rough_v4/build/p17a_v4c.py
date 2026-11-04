#!/workspace/mpvenv/bin/python
"""P17A v4c (ruling e): full proof treatment of rough_v4_prep/p17a/p17a_proof.py (glints + hull swell + sail ripple + fleet drift,
same params, same camera) with the hooded figure (hood, cloak, arm, steering hand) and ALL oars (incl. steering oar) matted OUT of
every displacement: hard zero inside the matte grown 6 px, feathered to full strength 12 px beyond that.
Plate read-only (fa286390...). Proof masks read-only. Outputs (refuse overwrite) in rough_v4/scratch/p17a_v4c/:
  p17a_v4c.mp4, p17a_v4c_report.json, matte png.  --checks: measurements only."""
import sys, json, hashlib, subprocess, importlib.util, math, numpy as np, cv2
from pathlib import Path
BJ = Path(__file__).resolve().parents[2]; ROOT = BJ.parents[1]; PREP = BJ / 'rough_v4_prep/p17a'; PL = BJ / 'plates/P17A_unnamed_captain.png'
OUTD = BJ / 'rough_v4/scratch/p17a_v4c'; OUTD.mkdir(exist_ok=True)
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
PMD5 = md5(PL); assert PMD5 == 'fa2863906d7648c30406adc27d738670'
assert md5(ROOT / 'engine-rnd/water/water_v1.py').startswith('811734e9')
def _load(n, p): s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
WG = _load('water_v1_1_ro', ROOT / 'engine-rnd/water/water_v1_1.py'); WA, GR = WG.W, WG.G
FPS, OW, OH = 30, 1080, 1920; SECS = 7.5; N = int(round(SECS * FPS))
P = cv2.cvtColor(cv2.imread(str(PL)), cv2.COLOR_BGR2RGB); H, W = P.shape[:2]; SLACK = 1 + 10.0 / OW; s0 = max(OW / W, OH / H) * SLACK
MK = json.load(open(PREP / 'masks/p17a_masks.json')); m = lambda n: cv2.imread(str(PREP / f'masks/p17a_mask_{n}.png'), 0) > 127
WATER, GUARD, SAIL, FLEET, NOWARP, CAPT, OARS0 = m('water'), m('guard'), m('sail'), m('fleet'), m('nowarp'), m('captain'), m('oars')
def poly(pts): k = np.zeros((H, W), np.uint8); cv2.fillPoly(k, [np.int32(pts)], 1); return k > 0
def grow(k, r): return cv2.dilate(k.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))) > 0
# v4c figure matte = proof captain box + the arm/steering hand that pokes out right of it (x 480-545, y 535-620), grown 8 px
HAND = poly([[470, 530], [520, 540], [548, 575], [548, 615], [520, 625], [470, 615]])
FIG = grow(CAPT | HAND, 8)
OARS = grow(OARS0, 8)                      # proof oar lines (24 px) + steering oar, grown 8 px to take in blade edges / tips
ZERO = grow(FIG | OARS | NOWARP, 6)        # hard zero
WCFG = dict(name='P17A_glints', plate=str(PL), seed=617, push=[1.0, 1.04], push_center=[0.55, 0.45], water=MK['water'], protect=MK['protect'], protect_feather=5,
            layers=[dict(type='glints', hp_sigma=3.0, thresh=9, min_dist=6, n_max=60, edge_px=1, sigma=1.5, star=0.25, star_len=4, halo=0.08, halo_sigma=4.0,
                         own_r=3, lift=0.6, dim=0.2, add=0.55, color=[255, 225, 180], rate_lo=[0.5, 1.2], rate_hi=[1.2, 2.6], thresh_t=0.45, power=1.6)])
WS = WA.WaterShot(WCFG)
def sstep(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def feather(mask, r):
    d = cv2.distanceTransform((~mask).astype(np.uint8), cv2.DIST_L2, 5); return np.clip(1 - d / r, 0, 1).astype(np.float32)
nowarp_w = 1 - feather(ZERO, 12)
sail_w = cv2.GaussianBlur(SAIL.astype(np.float32), (0, 0), 10) * nowarp_w; sail_w[ZERO] = 0
fleet_w = cv2.GaussianBlur(FLEET.astype(np.float32), (0, 0), 8) * nowarp_w; fleet_w[ZERO] = 0
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
SAIL_A, FLEET_D, BOB_A, ROLL_A = 0.6, 1.6, 1.0, 0.05
def disp(t):
    ph = 2 * math.pi * (XX / 260.0 - t / 3.1) + YY / 180.0
    dx = 0.35 * SAIL_A * np.sin(ph * 0.7 + 1.3) * sail_w + FLEET_D * sstep(t / SECS) * fleet_w
    dy = SAIL_A * np.sin(ph) * sail_w
    dx[ZERO] = 0; dy[ZERO] = 0
    return dx, dy
def cam(i, motion):
    t = i / FPS; z = 1.0 + 0.04 * sstep(i / max(N - 1, 1)); s = s0 * z; cx, cy = 0.55, 0.45
    qx = s0 * cx * W + (OW - W * s0) / 2; qy = s0 * cy * H + (OH - H * s0) / 2; ox = qx - s * cx * W; oy = qy - s * cy * H
    A = np.float64([[s, 0, ox], [0, s, oy]])
    if motion:
        ang = math.radians(ROLL_A * math.sin(2 * math.pi * t / 5.3 + 0.4)); by = BOB_A * math.sin(2 * math.pi * t / 4.2)
        R = cv2.getRotationMatrix2D((OW / 2, OH / 2), math.degrees(ang), 1.0); A = R @ np.vstack([A, [0, 0, 1]]); A[1, 2] += by
    marg = 3.0
    A[0, 2] = min(-marg, max(OW - s * W + marg, A[0, 2])); A[1, 2] = min(-marg, max(OH - s * H + marg, A[1, 2]))
    return A.astype(np.float32)
def wa(img, A, interp=cv2.INTER_LANCZOS4): return cv2.warpAffine(img, A, (OW, OH), flags=interp, borderMode=cv2.BORDER_REFLECT)
def frame(i):
    t = i / FPS; g = WS.frame(t); dx, dy = disp(t); gm = cv2.remap(g, XX + dx, YY + dy, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    return g, gm, wa(gm, cam(i, True))
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST); DIS.setFinestScale(0)
def flow_mag(a, b, msk):
    f = DIS.calc(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), cv2.cvtColor(b, cv2.COLOR_RGB2GRAY), None); mg = np.hypot(f[..., 0], f[..., 1])
    return float(mg[msk].max()), float(np.percentile(mg[msk], 99))
REG = dict(figure=FIG, oars=OARS)
def measure(step=5):
    gl = cv2.VideoCapture(str(PREP / 'p17a_glints_only.mp4')); v4b = []
    while True:
        ok, fr = gl.read()
        if not ok: break
        v4b.append(fr)
    rep = {k: dict(analytic_disp_max_plate_px=0.0, plate_remap_changed_px=0, out_absdiff_max_vs_rigid=0, out_flow_max_vs_rigid_px=0.0,
                   out_flow_p99_vs_rigid_px=0.0, rigid_swell_vs_v4b_flow_max_px=0.0) for k in REG}
    for i in range(0, N, step):
        t = i / FPS; dx, dy = disp(t); mg = np.hypot(dx, dy); g, gm, fa = frame(i); fr = wa(g, cam(i, True))   # same glints + same camera, NO displacement
        b4 = cv2.cvtColor(v4b[i], cv2.COLOR_BGR2RGB)
        for k, R in REG.items():
            r = rep[k]; r['analytic_disp_max_plate_px'] = max(r['analytic_disp_max_plate_px'], float(mg[R].max()))
            r['plate_remap_changed_px'] = max(r['plate_remap_changed_px'], int((np.abs(gm[R].astype(int) - g[R].astype(int)).max(-1) > 0).sum()))
            mo = cv2.warpAffine(R.astype(np.uint8) * 255, cam(i, True), (OW, OH), flags=cv2.INTER_NEAREST) > 0
            mo5 = cv2.erode(mo.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
            r['out_absdiff_max_vs_rigid'] = max(r['out_absdiff_max_vs_rigid'], int(np.abs(fa[mo5].astype(int) - fr[mo5].astype(int)).max()))
            a, p = flow_mag(fr, fa, mo5); r['out_flow_max_vs_rigid_px'] = max(r['out_flow_max_vs_rigid_px'], a); r['out_flow_p99_vs_rigid_px'] = max(r['out_flow_p99_vs_rigid_px'], p)
            a, p = flow_mag(b4, fa, mo5); r['rigid_swell_vs_v4b_flow_max_px'] = max(r['rigid_swell_vs_v4b_flow_max_px'], a)
        print('m', i, flush=True)
    for r in rep.values():
        for kk in list(r): r[kk] = round(r[kk], 4) if isinstance(r[kk], float) else r[kk]
    return rep
REP = dict(plate=str(PL), plate_md5_before=PMD5, seconds=SECS, frames=N, base='rough_v4_prep/p17a/p17a_proof.py (proof md5 cb67cc82) params unchanged',
           params=dict(sail_amp_px=SAIL_A, fleet_drift_px=FLEET_D, bob_px=BOB_A, roll_deg=ROLL_A, push=[1.0, 1.04], cover_slack=SLACK),
           matte=dict(figure_px=int(FIG.sum()), oars_px=int(OARS.sum()), zero_px=int(ZERO.sum()), feather_px=12))
REP['guard_density'] = GR.check_pixel_density((W, H), (OW, OH), (1.0, 1.04), mode='measure', crop_zoom=SLACK, name='P17A_v4c')
pk = dict(sail=0.0, fleet=0.0)
for i in range(0, N, 15):
    dx, dy = disp(i / FPS); mg = np.hypot(dx, dy); pk['sail'] = max(pk['sail'], float(mg[SAIL].max())); pk['fleet'] = max(pk['fleet'], float(mg[FLEET].max()))
REP['peaks_plate_px'] = {k: round(v, 3) for k, v in pk.items()}
ov = P.astype(np.float32)
for k, c in ((ZERO, (255, 60, 60)), (SAIL & ~ZERO, (60, 255, 90)), (FLEET & ~ZERO, (255, 230, 0))): ov[k] = ov[k] * 0.55 + np.float32(c) * 0.45
cv2.imwrite(str(OUTD / 'p17a_v4c_matte_overlay.jpg'), cv2.cvtColor(ov.astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
if '--checks' in sys.argv:
    REP['warp'] = measure(int(sys.argv[sys.argv.index('--checks') + 1]) if len(sys.argv) > sys.argv.index('--checks') + 1 else 15); print(json.dumps(REP, indent=1, default=str)); sys.exit(0)
out = OUTD / 'p17a_v4c.mp4'; assert not out.exists(), out
pa = subprocess.Popen(['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(out)], stdin=subprocess.PIPE)
for i in range(N):
    _, _, fa = frame(i); pa.stdin.write(fa.tobytes())
    if i % 45 == 0: print('f', i, flush=True)
pa.stdin.close(); assert pa.wait() == 0
REP['warp'] = measure(5)
REP.update(output=dict(path=str(out), md5=md5(out)), plate_md5_after=md5(PL)); assert REP['plate_md5_after'] == PMD5
json.dump(REP, open(OUTD / 'p17a_v4c_report.json', 'x'), indent=1, default=str); print(json.dumps(REP, default=str))
