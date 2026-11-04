#!/workspace/mpvenv/bin/python
"""P17B proof (rough v4 prep). Plate plates/P17B_dudo_open_bier.png (read-only, md5 891449ef...), 1080x1920, lands on L14.
  depth_v1 (locked engine, read-only), 2 rigid layers: far = arch, sky, town, gate, background mourners, ground;
  near = bier + Hastein + sword + front bearers (Depth Anything band + hand polys forcing face/sword/bier into the near card).
  Camera: slow eased push 1.00 -> 1.06 about Hastein (0.40, 0.30); the far card gets push_gain FAR_G so the far-vs-near relative
  parallax is <= 1.5 output px over the whole shot (measured). Reads as the procession advancing toward camera. No travel.
  Protected (rigidity check, inside one card, no matte edge): Hastein's face, the sword (blade + highlight).
  Optional sky drift through the arch: NOT done (kept static; flagged).
Outputs (refuse overwrite): p17b_proof.mp4 (CRF 18), masks/, p17b_layers.png, p17b_warp_check.json (depth_v1 proof), grabs, p17b_proof_report.json."""
import sys, json, hashlib, subprocess, importlib.util, math, numpy as np, cv2
from pathlib import Path
HERE = Path(__file__).resolve().parent; BJ = HERE.parents[1]; ROOT = BJ.parents[1]; PL = BJ / 'plates/P17B_dudo_open_bier.png'
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
PMD5 = md5(PL); assert PMD5 == '891449efff6d3ca87dfca2bec6a0fe6d'
def _load(n, p): s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DP = _load('depth_v1_ro', ROOT / 'engine-rnd/depth/depth_v1.py'); DP.CACHE = Path('/tmp/bjv4/depthcache'); DP.CACHE.mkdir(parents=True, exist_ok=True)
FPS, OW, OH = 30, 1080, 1920; N = int(sys.argv[sys.argv.index('--frames') + 1]) if '--frames' in sys.argv else 226
W, H = 1080, 1920
def fr(polys): return [[[x / W, y / H] for x, y in p] for p in polys]
def R(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
FACE = R(290, 360, 500, 560)                                                   # Hastein's face/head on the bier
SWORD = [[540, 490], [610, 480], [700, 600], [880, 900], [850, 925], [660, 690], [560, 560]]   # hilt, hands, blade to the tip (highlight)
BIER = [[140, 560], [300, 420], [560, 470], [870, 600], [1080, 760], [1080, 1080], [700, 1100], [520, 1230], [330, 1000], [120, 760]]
ANCHOR = (0.40, 0.30); PUSH = (1.0, 1.06); LIMIT_PX = 1.5
def cfg_for(far_g):
    return dict(name='P17B_proof', plate=str(PL), seconds=N / FPS, formats=['1080x1920'],
                matte=dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6),
                camera=dict(push=list(PUSH), anchor=list(ANCHOR), travel=0.0, dir=[1, 0], pivot=0.5, ease=dict(ramp_in=0.5, ramp_out=0.5, v_end=0.35)),
                layers=[dict(name='far', parallax=0.0, push_gain=far_g),
                        dict(name='near', parallax=1.0, push_gain=1.0, depth_min=0.33, polys=fr([FACE, SWORD, BIER]),
                             protect=[dict(name='hastein_face', poly=fr([FACE])[0]), dict(name='sword', poly=fr([SWORD])[0])])])
def rel_parallax(sh, o, E):
    """max over visible plate points of the change (e0 -> e) in near-vs-far output offset, output px."""
    ys, xs = np.mgrid[0:H:20, 0:W:20]; X = np.stack([xs.ravel(), ys.ravel(), np.ones(xs.size)], 0)
    def off(e): return (sh.layer_affine(1, e, (OW, OH), o).astype(np.float64) @ X) - (sh.layer_affine(0, e, (OW, OH), o).astype(np.float64) @ X)
    d0 = off(E[0]); best = 0.0
    for e in E[::3].tolist() + [E[-1]]:
        Mf = sh.layer_affine(0, e, (OW, OH), o).astype(np.float64) @ X; vis = (Mf[0] >= 0) & (Mf[0] < OW) & (Mf[1] >= 0) & (Mf[1] < OH)
        best = max(best, float(np.hypot(*(off(e) - d0))[vis].max()))
    return best
# far push gain: largest Δzoom with relative parallax <= LIMIT_PX (bisection on far_g)
E = DP.smooth_progress(N, fps=FPS, ramp_in=0.5, ramp_out=0.5, v_end=0.35)
sh = DP.DepthShot(cfg_for(1.0)); lo, hi = 0.0, 1.0
for _ in range(14):
    mid = (lo + hi) / 2; sh.cfg = cfg_for(mid); sh.layers = sh.cfg['layers']
    o = sh.overscan((OW, OH), N); (lo, hi) = (lo, mid) if rel_parallax(sh, o, E) <= LIMIT_PX else (mid, hi)
FAR_G = round(hi + 0.0005, 4)
cfg = cfg_for(FAR_G); sh = DP.DepthShot(cfg); o = sh.overscan((OW, OH), N); rp = rel_parallax(sh, o, E)
print('far push_gain', FAR_G, 'overscan', o, 'rel parallax px', rp, flush=True); assert rp <= LIMIT_PX + 1e-3
json.dump(cfg, open(HERE / 'p17b_depth_cfg.json', 'x'), indent=1)
for k, n in enumerate(['far', 'near']): cv2.imwrite(str(HERE / f'masks/p17b_mask_{n}_hard.png'), sh.hard[k].astype(np.uint8) * 255)
for n, p in dict(face=FACE, sword=SWORD, bier_force=BIER).items():
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.int32(p)], 255); cv2.imwrite(str(HERE / f'masks/p17b_mask_{n}.png'), m)
ov = sh.P.copy().astype(np.float32); nm = sh.hard[1]; ov[nm] = ov[nm] * 0.55 + np.float32([60, 200, 255]) * 0.45
ov = ov.astype(np.uint8); cv2.polylines(ov, [np.int32(FACE), np.int32(SWORD)], True, (255, 40, 40), 4)
cv2.imwrite(str(HERE / 'p17b_mask_overlay.png'), cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))
# face/sword wholly inside the near card?
inside = {n: round(float(sh.hard[1][np.asarray(cv2.fillPoly(np.zeros((H, W), np.uint8), [np.int32(p)], 1), bool)].mean()), 4) for n, p in dict(face=FACE, sword=SWORD).items()}
print('in near card', inside, flush=True)
DP.layers_sheet(cfg, str(HERE / 'p17b_layers.png')) if not (HERE / 'p17b_layers.png').exists() else None
pr = DP.proof(cfg, str(HERE / 'p17b_warp_check.json'))
mp4 = HERE / 'p17b_proof.mp4'; assert not mp4.exists()
p = subprocess.Popen(['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(mp4)], stdin=subprocess.PIPE)
for i in range(N):
    f = DP.to8(sh.frame(E[i], (OW, OH), o, fid=i)); p.stdin.write(np.ascontiguousarray(f).tobytes())
    if i in (0, N // 2, N - 1): cv2.imwrite(str(HERE / f'p17b_proof_f{i:03d}.jpg'), cv2.cvtColor(f, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 90])
p.stdin.close(); assert p.wait() == 0
f0 = pr['formats']['1080x1920']
REP = dict(plate=str(PL), plate_md5_before=PMD5, plate_md5_after=md5(PL), frames=N, seconds=round(N / FPS, 3), push=list(PUSH), anchor=list(ANCHOR), far_push_gain=FAR_G,
           overscan=round(o, 5), rel_parallax_max_px=round(rp, 3), limit_px=LIMIT_PX, protect_in_near_card=inside, layers=sh.info()['layers'],
           warp_check=dict(pass_=pr['pass'], recon_psnr_db=pr['recon_native']['psnr_db'], single_transform=f0['single_transform']['pass_'], dot_test=f0['single_transform']['dot_test']['pass_'],
                           uniform_scale=f0['single_transform']['uniform_scale_no_shear_no_rot'], holes=[d['holes_px'] for d in f0['disocclusion']],
                           rigidity=[dict(name=x['name'], layer=x['layer'], in_layer=x['in_layer_frac'], pass_=x['pass_']) for x in f0['rigidity']], guardrail=f0['guardrail']),
           sky_drift='not done (optional; static sky)', output=dict(path=str(mp4), md5=md5(mp4)))
assert REP['plate_md5_after'] == PMD5
json.dump(REP, open(HERE / 'p17b_proof_report.json', 'x'), indent=1, default=float); print(json.dumps(REP, default=float)[:3000])
