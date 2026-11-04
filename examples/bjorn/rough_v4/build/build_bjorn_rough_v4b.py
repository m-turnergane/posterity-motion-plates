#!/workspace/mpvenv/bin/python
"""Bjorn Ironside ROUGH v4b build = build_bjorn_rough_v4.py (md5 d112a9fe...) with v4b inputs only: cuts/words/VO/mix _v4b (+0.5 s after "barred.",
  P07 2.267 s), P05 clip from scratch/p05_rough_v4b (phone-legible labels), clips -> scratch/clips_v4b, outputs *_v4b. No other change.
-- v4 header: Bjorn Ironside ROUGH v4 build = rough_v2 build (copied, md5 logged) + v4 changes (owner directive 2026-11-03):
  P05 = rough_v4 word-locked atlas clip; P06 FLAT + water-only masked glints (no depth); P11 4.2 s; P13 FLAT wide -> word-locked
  HARD CUT 1 frame before 'armour' to HEM z1.30 top345 (no zoom/vertical move); P17A = p17a glints-only clip; P17B = p17b proof clip;
  P19 dropped; house title over P03 (after the coffin hook), 15 % lower; voiced v4 VO + continuous-score mix. -- v2 notes: P13 eased tilt/push resolving on 'armour' (cam='hem'),
  P07/P13 caption position overrides, rough_v2 paths/timeline (logs/cuts_v2.json). v1 notes: Template: Bathory v2/v3c builds. Plates/engines read-only (importlib);
writes only into rough_v2/{scratch,logs,renders} + rough_v2 deliverables. ffmpeg -n (never -y).
  build.py faces | still <P> <t> | clip <P> | proofs | captions | final | sheet"""
import sys, json, math, subprocess, importlib.util, hashlib
from pathlib import Path
import numpy as np, cv2
cv2.setNumThreads(4)
ROOT = Path('/workspace/posterity'); BJ = ROOT / 'standalones/bjorn'; BR = BJ / 'rough_v4'; PL = BJ / 'plates'
SCR = BR / 'scratch'; SCR.mkdir(exist_ok=True); LOGS = BR / 'logs'; REN = BR / 'renders'
FPS = 30; OW, OH = 1080, 1920
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
FX = _load('fx_v1c_ro', ROOT / 'standalones/edward-ii/edit/fx_v1c.py')
SM = _load('smoke_v2_ro', ROOT / 'engine-rnd/smoke/smoke_v2.py')
DP = _load('depth_v1_ro', ROOT / 'engine-rnd/depth/depth_v1.py')
SN = _load('snow_v1b_ro', ROOT / 'engine-rnd/snow/snow_v1b.py')          # only for detect_faces (YuNet)
WG = _load('water_v1_1_ro', ROOT / 'engine-rnd/water/water_v1_1.py'); WA = WG.W; GR = WG.G
DP.CACHE = SCR / 'cache/depth'; SN.CACHE = SCR / 'cache/snow'; FX.SPECS = {}; FX.PULSE = {}
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
assert md5(ROOT / 'engine-rnd/water/water_v1.py').startswith('811734e9'), 'water_v1 not the locked file'
def load_rgb(p): a = cv2.imread(str(p), cv2.IMREAD_COLOR); assert a is not None, p; return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def R(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
def frac(polys, W, H): return [[[x / W, y / H] for x, y in p] for p in polys]
def writer(path):
    cmd = ['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

# ------------------------------------------------------------------ timeline (from retime_vo.py -> logs/cuts.json)
CUTS = json.load(open(LOGS / 'cuts_v4b.json')); ORDER = [c['shot'] for c in CUTS]
def frames_of(k): c = CUTS[ORDER.index(k)]; return c['f0'], c['f1']
TOTAL_F = CUTS[-1]['f1']; DUR = TOTAL_F / FPS
VO = SCR / 'vo_bjorn_v4b.wav'; WORDS = LOGS / 'vo_bjorn_v4b_words.json'
MIXWAV = SCR / 'audio/mix_bjorn_v4b.wav'; ASS = BR / 'bjorn_rough_v4b_captions.ass'; FINAL = REN / 'bjorn_rough_v4b.mp4'
PREP = BJ / 'rough_v4_prep'
CLIPS_SRC = dict(P05=BR / 'scratch/p05_rough_v4b/p05_test_v4b_silent.mp4', P17A=PREP / 'p17a/p17a_glints_only.mp4', P17B=PREP / 'p17b/p17b_proof.mp4')
P05_CLIP = CLIPS_SRC['P05']

# ------------------------------------------------------------------ per-shot config (plate px)
M_HY = dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6)
def CAM(anchor, push=(1.0, 1.06), travel=0.02, d=(1, 0), ro=0.5): return dict(push=list(push), anchor=list(anchor), travel=travel, dir=list(d), pivot=0.5,
                                                                          ease=dict(ramp_in=0.5, ramp_out=ro, v_end=0.35))
B = {}
B['P01'] = dict(kind='depth', fx=[dict(manual=[(64, 1203, 114, 1286), (855, 1202, 905, 1286)], spill_amp=1.4, _kind='candle')],
                depth=dict(matte=M_HY, camera=CAM((0.5, 0.5)), far_gain=0.4, near=dict(depth_min=0.46, region=[R(0, 1000, 941, 1672), R(300, 838, 600, 1000)])))
B['P02'] = dict(kind='flat', center=(0.5, 0.42), push=(1.0, 1.05),   # storyboard: push 1.00-1.05 into the hand; candle light through the lid gap
               fx=[dict(offscreen=[dict(xy=(780, 335), h=30, radius=420, kind='torch')], spill_amp=1.0, _kind='candle')])
B['P03'] = dict(kind='depth', fx=[dict(torch=[(650, 715, 715, 795), (815, 728, 858, 768)], spill_amp=1.2, _kind='torch')],
                depth=dict(matte=M_HY, camera=CAM((0.35, 0.3)), far_gain=0.4, near=dict(depth_min=0.55, exclude=[R(620, 1330, 941, 1672)])))
B['P04'] = dict(kind='flat', center=(0.45, 0.5), fx=[dict(torch=[(400, 640, 660, 862)], spill_amp=1.3, _kind='torch')],
                faces_manual=[(160, 570, 345, 735), (690, 275, 805, 390)])
B['P05'] = dict(kind='clip')
# v4 P06 (directive 12): FLAT (no depth parallax = landscape/Hastein never move apart), slow push 1.00->1.04; glints ONLY inside the
# hand-traced sea + sunlit lagoon polygons (plate px, traced on a 1.5x grid crop); Hastein (hood, braid, fur, cloak), shore, reeds, rail protected.
P06_SEA = [[365, 838], [600, 828], [941, 836], [941, 1385], [560, 1350], [552, 1240], [540, 1120], [480, 1030], [420, 960], [365, 905]]
P06_LAGOON = [[600, 748], [941, 744], [941, 758], [600, 763]]
P06_HASTEIN = [[0, 480], [330, 480], [345, 860], [400, 925], [470, 1000], [530, 1100], [548, 1230], [556, 1340], [560, 1672], [0, 1672]]
P06_RAIL = [[500, 1330], [941, 1375], [941, 1672], [500, 1672]]
B['P06'] = dict(kind='flat', center=(0.65, 0.5), push=(1.0, 1.04), water=dict(polys=[P06_SEA, P06_LAGOON], protect=[P06_HASTEIN, P06_RAIL]))
B['P07'] = dict(kind='flat', center=(0.55, 0.45))
B['P17A'] = dict(kind='clip'); B['P17B'] = dict(kind='clip')
B['P08'] = dict(kind='flat', center=(0.35, 0.5), fx=[dict(torch=[(125, 1282, 200, 1400)], spill_amp=1.2, _kind='torch')],
                faces_manual=[(140, 275, 460, 640), (690, 140, 941, 640)])
B['P09'] = dict(kind='flat', push=(1.0, 1.04), center=(0.5, 0.45), fx=[dict(torch=[(955, 800, 1075, 990)], spill_amp=1.2, _kind='torch')],
                faces_manual=[(263, 566, 395, 790), (671, 605, 816, 816)])
B['P10'] = dict(kind='flat', center=(0.45, 0.5), fx=[dict(auto=[(0, 890, 215, 1200)], spill_amp=1.4, _kind='candle')],
                faces_manual=[(160, 138, 300, 390), (528, 184, 666, 367), (436, 757, 690, 1056)])
B['P11'] = dict(kind='flat', center=(0.4, 0.5), fx=[dict(torch=[(230, 340, 320, 480), (825, 365, 915, 485)], spill_amp=1.2, _kind='torch')])
B['P12'] = dict(kind='flat', center=(0.3, 0.4), fx=[dict(manual=[(328, 558, 359, 629)], spill_amp=1.4, _kind='candle')],
                faces_manual=[(250, 320, 370, 495), (436, 345, 550, 495)])
B['P13'] = dict(kind='flat', center=(0.5, 0.45), cam='hemcut', push=(1.0, 1.02), fx=[dict(manual=[(516, 531, 530, 556), (567, 546, 581, 573), (812, 546, 826, 570)], spill_amp=1.3, _kind='candle')],
                faces_manual=[(190, 120, 315, 310)])   # v2: striding mourner's profile face (YuNet misses it at 0.6; v1 left it under candle-spill flicker)
# P13: depth tried (0.65) -> the ground strip under the striding man fell in the near layer across the full width (shear at the ground line) -> FLAT
B['P14'] = dict(kind='flat', center=(0.5, 0.35), cam='snap', fx=[dict(manual=[(578, 415, 600, 506), (626, 479, 662, 540)], spill_amp=1.3, _kind='candle')],
                faces_manual=[(820, 400, 941, 560)])
B['P15'] = dict(kind='flat', center=(0.6, 0.3), smoke=dict(protect=[R(100, 160, 790, 1672)], emitters=[
    dict(name='band_hi', type='haze', rect=[700, 140, 941, 470], drift=6.0, opacity=0.22, lo=220, hi=6.0, swirl=12.0, feather=36.0,
         color_dark=[70, 66, 66], color_light=[150, 144, 140], glow=None, res=0.5),
    dict(name='band_lo', type='haze', rect=[790, 520, 941, 860], drift=5.0, opacity=0.18, lo=220, hi=6.0, swirl=10.0, feather=36.0,
         color_dark=[70, 66, 66], color_light=[150, 144, 140], glow=None, res=0.5)]))
B['P16'] = dict(kind='depth', depth=dict(matte=M_HY, camera=CAM((0.4, 0.45), push=(1.06, 1.0)), far_gain=0.4, near=dict(depth_min=0.45)))
B['P17'] = dict(kind='flat', center=(0.4, 0.55), cam='tilt', fx=[dict(manual=[(736, 1074, 791, 1166)], spill_amp=1.4, _kind='candle')],
                faces_manual=[(160, 850, 436, 1055)])
B['P18'] = dict(kind='flat', center=(0.4, 0.35), fx=[dict(manual=[(440, 1120, 491, 1310)], spill_amp=1.4, _kind='candle')],
                faces_manual=[(344, 115, 690, 600)])
B['P19'] = dict(kind='flat', push=(1.0, 1.04), center=(0.45, 0.6), fx=[dict(manual=[(744, 1013, 768, 1087)], spill_amp=1.4, _kind='candle')],
                faces_manual=[(252, 850, 460, 1055)])
B['P20'] = dict(kind='depth', depth=dict(matte=M_HY, camera=CAM((0.3, 0.2)), far_gain=0.4,
                near=dict(depth_min=0.36, region=[R(0, 0, 700, 1672)])))
B['OUTRO'] = dict(kind='flat', center=(0.5, 0.3), push=(1.0, 1.03))
OUTRO_TEXT = (40, 60, 900, 420)

TARGET = dict(candle=dict(local=32.0, whole=15.0, step=6.0), torch=dict(local=30.0, whole=12.0, step=2.95))
LIMIT = dict(candle=dict(local=36.0, whole=15.0, step=6.0), torch=dict(local=45.0, whole=14.0, step=3.1))
def fx_metrics(inst, P, seconds=3.0):
    H, W = P.shape[:2]; flame = np.zeros((H, W), np.uint8); loc = np.zeros((H, W), bool)
    for s in inst.srcs:
        if s.get('bb') is not None:
            x0, y0, x1, y1 = s['bb']; flame[max(0, y0 - 8):y1 + 8, max(0, x0 - 8):x1 + 8] = 1
    Y, X = np.ogrid[:H, :W]
    for s in inst.srcs:
        if s['kind'] == 'window': continue
        r = float(s['radius']); cy = s['base'] - s['h'] * 0.5
        d = np.sqrt((X - s['x']) ** 2 + (Y - cy) ** 2); loc |= (d < max(r * 0.6, 25)) & (d > s['h'] * 0.6)
    loc &= flame == 0; whole = flame == 0; wl, ll = [], []
    for i in range(int(seconds * FPS)):
        f = luma(inst.render(i / FPS).astype(np.float32)); wl.append(f[whole].mean()); ll.append(f[loc].mean() if loc.any() else 0)
    wl, ll = np.array(wl), np.array(ll)
    pp = lambda v: float((v.max() - v.min()) / max(v.mean(), 1e-3) * 100)
    st = lambda v: float(np.abs(np.diff(v)).max() / max(v.mean(), 1e-3) * 100)
    return dict(whole=pp(wl), local=pp(ll), step=max(st(wl), st(ll)))
def calibrate(inst, P, kind):
    FX.PULSE[inst.key] = 1.0; m1 = fx_metrics(inst, P)
    T = TARGET[kind]; pul = min(T['local'] / max(m1['local'], 1e-3), T['whole'] / max(m1['whole'], 1e-3), T['step'] / max(m1['step'], 1e-3)); m = m1
    for _ in range(6):
        FX.PULSE[inst.key] = pul; m = fx_metrics(inst, P); L = LIMIT[kind]
        over = max(m['whole'] / L['whole'], m['step'] / L['step'], m['local'] / L['local']); under = m['local'] / T['local'] if m['local'] > 0 else 1.0   # window-only sources (P02): no local ring, calibrate on whole/step
        if over > 1.0: pul *= 0.95 / over
        elif under < 0.85 and kind == 'candle': pul *= min(1.0 / under, 0.95 / max(over, 1e-3))
        else: break
    FX.PULSE[inst.key] = pul; return pul, {k: round(v, 2) for k, v in m1.items()}, {k: round(v, 2) for k, v in m.items()}

# ------------------------------------------------------------------ faces: YuNet + manual boxes, padded; FX delta hard-zeroed inside
FACE_PAD = 6; FACE_FEATHER = 18
def face_boxes(key, P):
    H, W = P.shape[:2]; out = []
    for f in SN.detect_faces(P, 0.6):
        x, y, w, h = [float(v) for v in f[:4]]
        if w < 12 or h < 12: continue                                   # tiny false positives (e.g. P03 [711,747,6,8])
        out.append([int(x - 0.25 * w), int(y - 0.35 * h), int(x + 1.25 * w), int(y + 1.2 * h)])
    out += [list(b) for b in B[key].get('faces_manual', [])]
    return [[max(0, x0 - FACE_PAD), max(0, y0 - FACE_PAD), min(W, x1 + FACE_PAD), min(H, y1 + FACE_PAD)] for x0, y0, x1, y1 in out]
def face_zero(shape, boxes):
    H, W = shape; hard = np.zeros((H, W), np.uint8)
    for x0, y0, x1, y1 in boxes: hard[y0:y1, x0:x1] = 1
    if not hard.any(): return hard.astype(bool), np.zeros((H, W), np.float32)
    d = cv2.distanceTransform(1 - hard, cv2.DIST_L2, 5); z = np.clip(1 - d / FACE_FEATHER, 0, 1).astype(np.float32); z[hard > 0] = 1.0
    return hard > 0, z

def warp_out(img, A): return cv2.warpAffine(img, A, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
def to_frac_layer(d, W, H): return {k: (frac(v, W, H) if k in ('region', 'polys', 'exclude', 'seams') else v) for k, v in d.items()}
def ssmooth(u): u = min(max(u, 0.0), 1.0); return u * u * u * (u * (6 * u - 15) + 10)     # smootherstep (zero vel+acc at both ends)
# v2 P13 (Vellum item 3): FLAT build. Opens framed ABOVE the mail hem (bishop, coffin, procession; hem low in the bottom UI band),
# eased tilt-down + push (smootherstep) that ARRIVES on the hem at the onset of "armour", then a very slow eased creep (no frozen hold).
HEM = dict(z=(1.26, 1.29, 1.30), top=(0.0, 330.0, 345.0), left=(0.0, 0.0, 0.0), word='armour')   # left edge of view in plate px (0 = keeps the striding mourner's head in frame)
def hem_t(b):
    w = next(x for x in json.load(open(WORDS))['words'] if x['word'] == HEM['word'] and b.f0 / FPS <= x['start'] < (b.f0 + b.n) / FPS)
    return w['start'] - b.f0 / FPS
def hem_cam(b, i):
    if not hasattr(b, '_hem_T'): b._hem_T = hem_t(b)
    t = i / FPS; T = b._hem_T; (z0, z1, z2), (y0, y1, y2), (x0, x1, x2) = HEM['z'], HEM['top'], HEM['left']
    if t <= T: u = ssmooth(t / T); z = z0 + (z1 - z0) * u; y = y0 + (y1 - y0) * u; xs = min(x0, b.W - OW / (b.s0 * z0)); x = xs + (x1 - xs) * u
    else: u = sstep((t - T) / max((b.n - 1) / FPS - T, 1e-6)); z = z1 + (z2 - z1) * u; y = y1 + (y2 - y1) * u; x = x1 + (x2 - x1) * u
    s = b.s0 * z; y = min(max(y, 0.0), b.H - OH / s); x = min(max(x, 0.0), b.W - OW / s)
    return z, x, y
def sstep(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
# v4 P13 (directive 11): no zoom/tilt between framings. Wide procession view (whole plate, very slow eased push 1.00->1.02 on (0.5,0.45)),
# then a word-locked HARD CUT one frame before the onset frame of 'armour' to the HEM framing (z 1.30, view top 345 px, left 0) with an
# imperceptible creep 1.30->1.31 / top 345->350 (no frozen hold).
HEMCUT = dict(z=(1.30, 1.305), top=(345.0, 347.5), left=0.0, word='armour', frames_before=1)
# v4 QA: z_end 1.31 -> 1.305 so pixel density stays <= 1.5 (1.1483 cover x 1.31 = 1.5052 failed the guardrail).
def hemcut_i(b):
    if not hasattr(b, '_hc_i'): b._hc_i = int(math.floor((b.f0 / FPS + hem_t(b)) * FPS + 1e-6)) - HEMCUT['frames_before'] - b.f0
    return b._hc_i
def hemcut_cam(b, i):
    k = hemcut_i(b); u = sstep((i - k) / max(b.n - 1 - k, 1)); z = HEMCUT['z'][0] + (HEMCUT['z'][1] - HEMCUT['z'][0]) * u
    y = HEMCUT['top'][0] + (HEMCUT['top'][1] - HEMCUT['top'][0]) * u; s = b.s0 * z
    return z, min(max(HEMCUT['left'], 0.0), b.W - OW / s), min(max(y, 0.0), b.H - OH / s)

class Beat:
    def __init__(self, key, calib=True):
        self.key = key; c = B[key]; self.c = c; self.kind = c['kind']; f0, f1 = frames_of(key); self.f0, self.n = f0, f1 - f0
        self.log = dict(shot=key, kind=self.kind, frames=[f0, f1], seconds=round(self.n / FPS, 3)); self.fx = []; self.smoke = None; self.water = None
        if self.kind == 'clip':
            self.src = CLIPS_SRC[key]; self.log.update(source=str(self.src), source_md5=md5(self.src), density_max=1.0, note='source clip frames 0..%d' % (self.n - 1)); return
        pk = key; path = PL / f'{key}_KEEP.png'; P = load_rgb(path); H, W = P.shape[:2]; self.W, self.H = W, H
        self.path = path; self.P = P; self.Pf = P.astype(np.float32); self.s0 = max(OW / W, OH / H)
        self.faces = face_boxes(key, P); self.face_hard, self.face_z = face_zero((H, W), self.faces); self.log['faces_protected'] = self.faces
        for j, spec in enumerate(c.get('fx', [])):
            spec = dict(spec); kind = spec.pop('_kind'); spec['relight_exclude'] = [tuple(b) for b in self.faces]
            FX.SPECS[pk] = spec; inst = FX.PlateFX(str(path), seed=j); inst.key = f'{key}#{j}'
            self.log.setdefault('fx', []).append(dict(engine='fx_v1c ' + kind, info=inst.info(), spec={k: v for k, v in spec.items() if k != 'relight_exclude'}))
            if calib:
                pul, m1, m = calibrate(inst, P, kind); self.log['fx'][-1].update(pulse=round(pul, 4), metrics_at_pulse1=m1, metrics=m)
            self.fx.append(inst)
        if c.get('smoke'):
            s = c['smoke']; cfg = dict(seed=7, protect=s['protect'] + [R(*b) for b in self.faces], protect_feather=36, flame_keepout=0.0, preroll=8.0,
                                       emitters=s['emitters'], billows=[], fires=[])
            self.smoke = SM.SmokeScene(SM.load_plate(str(path)), cfg); self.log['smoke'] = [dict(engine='smoke_v2', name=e['name'], type=e['type'], opacity=e['opacity']) for e in s['emitters']]
        if c.get('water'):
            w = c['water']; self.wcfg = dict(name=f'{key}_glints', plate=str(path), seed=606, push=list(c.get('push', (1.0, 1.06))), push_center=list(c.get('center', (0.65, 0.3))), water=w['polys'],
                protect=w['protect'] + [R(*b) for b in self.faces], protect_feather=5,
                layers=[dict(type='glints', hp_sigma=3.0, thresh=9, min_dist=6, n_max=60, edge_px=1, sigma=1.5, star=0.25, star_len=4, halo=0.08, halo_sigma=4.0,
                             own_r=3, lift=0.6, dim=0.2, add=0.55, color=[255, 225, 180], rate_lo=[0.5, 1.2], rate_hi=[1.2, 2.6], thresh_t=0.45, power=1.6)])
            self.water = WA.WaterShot(self.wcfg); self.log['water'] = dict(engine='water_v1 glints', info=self.water.info())
        if self.kind == 'depth': self._depth()
        else:
            self.log['density_max'] = round(self.density_flat(), 4)
            self.log['guard_density'] = GR.check_pixel_density((W, H), (OW, OH), (1.0, 1.0), mode='measure', crop_zoom=self.density_flat() / self.s0, name=key)

    def _depth_cfg(self, protect=None):
        c = self.c['depth']; W, H = self.W, self.H; near = dict(c['near'])
        layers = [dict(name='far', parallax=0.0, push_gain=c['far_gain']), dict(name='near', parallax=1.0, push_gain=1.0, **to_frac_layer(near, W, H))]
        if protect:
            for k, lst in protect.items():
                if lst: layers[k]['protect'] = lst
        return dict(name=f'{self.key}_bjorn_rough_v4', plate=str(self.path), matte=c['matte'], camera=c['camera'], layers=layers, seconds=self.n / FPS)
    def _depth(self):
        cfg = self._depth_cfg(); ds = DP.DepthShot(cfg); W, H = self.W, self.H; prot = {0: [], 1: []}; fl = []
        for j, (X0, Y0, X1, Y1) in enumerate(self.faces):
            dx, dy = (X1 - X0) * 0.2, (Y1 - Y0) * 0.2; x0, y0, x1, y1 = int(X0 + dx), int(Y0 + dy), int(X1 - dx), int(Y1 - dy)   # face core (inner 60%)
            fr_near = float(ds.hard[1][y0:y1, x0:x1].mean()); k = 1 if fr_near >= 0.5 else 0
            prot[k].append(dict(name=f'face{j}', poly=frac([R(x0, y0, x1, y1)], W, H)[0])); fl.append(dict(box=[x0, y0, x1, y1], near_frac=round(fr_near, 4), layer=['far', 'near'][k]))
        cfg = self._depth_cfg(prot); self.dcfg = cfg; self.ds = DP.DepthShot(cfg); size = (OW, OH)
        self.o = self.ds.overscan(size, self.n); self.E = DP.smooth_progress(self.n, fps=FPS, **cfg['camera'].get('ease', {}))
        g = self.ds.guard(size, mode='warn', n=self.n); s, _, cz = self.ds.out_frame(size)
        zmax = max(self.ds.layer_params(k, e)[0] for k in range(2) for e in (0.0, 1.0)) * self.o
        self.log.update(depth_info=self.ds.info(), overscan=round(self.o, 4), guard=g, density_max=round(s * zmax, 4), face_layers=fl)

    def zoom(self, i):
        u = i / max(self.n - 1, 1); z0, z1 = self.c.get('push', (1.0, 1.06))
        if self.c.get('cam') == 'hem': return hem_cam(self, i)[0]
        if self.c.get('cam') == 'hemcut':
            k = hemcut_i(self)
            return hemcut_cam(self, i)[0] if i >= k else z0 + (z1 - z0) * sstep(i / max(k - 1, 1))
        if self.c.get('cam') == 'snap':                                     # P14: sharp 0.8 s scale-in, then hold
            a = min((i / FPS) / 0.8, 1.0); return z0 + (z1 - z0) * (1 - (1 - a) ** 3)
        return z0 + (z1 - z0) * sstep(u)
    def density_flat(self): return max(self.s0 * self.zoom(i) for i in range(self.n))
    def cam_flat(self, i):
        W, H = self.W, self.H; s0 = self.s0; s = s0 * self.zoom(i); cx, cy = self.c['center']
        qx = s0 * cx * W + (OW - W * s0) / 2; qy = s0 * cy * H + (OH - H * s0) / 2
        ox = qx - s * cx * W; oy = qy - s * cy * H
        if self.c.get('cam') == 'hem':                                      # v2 P13: view rect (top-left anchored) from hem_cam
            z, x_left, y_top = hem_cam(self, i); ox = -s * x_left; oy = -s * y_top
        if self.c.get('cam') == 'hemcut' and i >= hemcut_i(self):
            z, x_left, y_top = hemcut_cam(self, i); ox = -s * x_left; oy = -s * y_top
        if self.c.get('cam') == 'tilt':                                     # P17: slow tilt-up = view centre rises 0.55H -> 0.43H, clamped to cover
            u = sstep(i / max(self.n - 1, 1)); yc = H * (0.55 - 0.12 * u); oy = OH / 2 - s * yc
        ox = min(0.0, max(OW - s * W, ox)); oy = min(0.0, max(OH - s * H, oy))
        return np.float32([[s, 0, ox], [0, s, oy]])

    def plate_comp(self, t):
        if not (self.fx or self.smoke or self.water): return self.P
        acc = self.Pf.copy()
        for inst in self.fx: acc += inst.render(t).astype(np.float32) - self.Pf
        if self.smoke is not None: acc += np.asarray(self.smoke.frame(t)).astype(np.float32) - self.Pf
        if self.water is not None: acc += self.water.frame(t).astype(np.float32) - self.Pf
        acc = self.Pf + (acc - self.Pf) * (1 - self.face_z)[..., None]    # faces: FX delta hard 0 (feathered 18 px outside)
        out = np.clip(acc + 0.5, 0, 255).astype(np.uint8); out[self.face_hard] = self.P[self.face_hard]; return out

    def clip_frames(self):
        cmd = ['ffmpeg', '-loglevel', 'error', '-i', str(self.src), '-frames:v', str(self.n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE); k = 0
        while k < self.n:
            b = p.stdout.read(OW * OH * 3)
            if len(b) < OW * OH * 3: break
            yield np.frombuffer(b, np.uint8).reshape(OH, OW, 3); k += 1
        p.stdout.close(); p.wait(); assert k == self.n, (k, self.n)

    def render_frame(self, i):
        t = i / FPS
        if self.kind == 'depth':
            out, lay = self.ds.frame(self.E[i], (OW, OH), self.o, fid=i, plate_fx=lambda tt: self.plate_comp(tt).astype(np.float32) / 255.0, t=t, return_layers=True)
            return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)
        return warp_out(self.plate_comp(t), self.cam_flat(i))

def cmd_still(key, t, out=None):
    b = Beat(key, calib='--nocal' not in sys.argv); i = min(int(round(float(t) * FPS)), b.n - 1)
    fr = b.render_frame(i); out = out or str(SCR / f'still_{key}_{i:03d}.png')
    cv2.imwrite(out, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR)); print(json.dumps(b.log, default=str)[:4000]); print(out)

def cmd_clip(key):
    cl = SCR / 'clips_v4b'; cl.mkdir(exist_ok=True); out = cl / f'{key}.mp4'; lg = cl / f'{key}.json'
    if out.exists(): print('exists', out); return
    b = Beat(key); p = writer(out)
    it = b.clip_frames() if b.kind == 'clip' else (b.render_frame(i) for i in range(b.n))
    if key == INTRO_SHOT: IN = intro_mod(); it = (intro_comp(IN, fr, i) for i, fr in enumerate(it)); b.log['intro'] = dict(source=str(INTRO_SRC), source_md5=md5(INTRO_SRC), top_pct=INTRO_TOP, title=IN.TITLE, anchor=IN.ANCHOR)
    for i, fr in enumerate(it):
        p.stdin.write(np.ascontiguousarray(fr).tobytes())
        if i in (0, b.n // 2, b.n - 1): cv2.imwrite(str(cl / f'{key}_f{i:03d}.jpg'), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
    p.stdin.close(); assert p.wait() == 0
    json.dump(b.log, open(lg, 'w'), indent=1, default=str); print('done', key, b.n)

# v4 house title (directive 13 + owner 10:35 'move title down 15%'): rough_v3 intro_v3b Chronicle Reveal (Jianwen code span exec'd
# verbatim, read-only), placed over P03 = first shot AFTER the coffin hook (P01-P02), gf 0 = P03 cut; topPercent 16 -> 31 (+15 % of frame height).
INTRO_SRC = BJ / 'rough_v3/build/intro_v3b.py'; INTRO_SHOT = 'P03'; INTRO_TOP = 31.0
def intro_mod():
    m = _load('intro_v3b_ro', INTRO_SRC); m.CR['topPercent'] = INTRO_TOP; m.TOP_PCT = INTRO_TOP; return m
def intro_comp(m, fr, gf): return m.comp(np.ascontiguousarray(fr), gf)[0]

def cmd_faces():
    r = {}
    for k in ORDER:
        if B[k]['kind'] == 'clip': continue
        P = load_rgb(PL / f'{k}_KEEP.png'); r[k] = face_boxes(k, P)
    print(json.dumps(r))

# ------------------------------------------------------------------ proofs: face leak (plate+output space), outro text leak, depth proof
def cmd_proofs(keys=None):
    res = {}
    for k in (keys or ORDER):
        if B[k]['kind'] == 'clip': continue
        b = Beat(k, calib=False); r = dict(faces=len(b.faces), plate_face_changed_px=[], output_face_changed_px=[], fx_changed_px_outside_faces=[])
        if not (b.fx or b.smoke or b.water): r['note'] = 'no FX on this shot (plate_comp == plate)'
        for i in sorted(set([0, b.n // 3, 2 * b.n // 3, b.n - 1])):
            t = i / FPS; f = b.plate_comp(t); ch = np.abs(f.astype(int) - b.P.astype(int)).max(-1) > 0
            r['plate_face_changed_px'].append(int((ch & b.face_hard).sum())); r['fx_changed_px_outside_faces'].append(int((ch & ~b.face_hard).sum()))
            if b.kind == 'flat' and b.face_hard.any():
                A = b.cam_flat(i); fr = warp_out(f, A); ref = warp_out(b.P, A)
                mo = cv2.warpAffine(b.face_hard.astype(np.uint8) * 255, A, (OW, OH), flags=cv2.INTER_NEAREST) > 0
                dif = np.abs(fr.astype(int) - ref.astype(int)).max(-1) > 0
                m9 = cv2.erode(mo.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0                  # 4 px in (older check)
                m11 = cv2.erode(mo.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0                # 5 px in = LANCZOS4 footprint (4 plate px x 1.22)
                r.setdefault('output_face_changed_px_erode4', []).append(int((dif & m9).sum()))
                r['output_face_changed_px'].append(int((dif & m11).sum()))
        if k == 'OUTRO':
            x0, y0, x1, y1 = OUTRO_TEXT; r['outro_text_rect_plate'] = [x0, y0, x1, y1]; r['outro_plate_text_changed_px'] = []; r['outro_output_text_changed_px'] = []
            for i in sorted(set([0, b.n // 4, b.n // 2, 3 * b.n // 4, b.n - 1])):
                f = b.plate_comp(i / FPS); r['outro_plate_text_changed_px'].append(int((np.abs(f[y0:y1, x0:x1].astype(int) - b.P[y0:y1, x0:x1].astype(int)).max(-1) > 0).sum()))
                A = b.cam_flat(i); m = np.zeros(b.P.shape[:2], np.uint8); m[y0:y1, x0:x1] = 255
                mo = cv2.erode((cv2.warpAffine(m, A, (OW, OH), flags=cv2.INTER_NEAREST) > 0).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
                fr = b.render_frame(i); ref = warp_out(b.P, A); r['outro_output_text_changed_px'].append(int(((np.abs(fr.astype(int) - ref.astype(int)).max(-1) > 0) & mo).sum()))
            r['outro_zoom_end'] = round(b.zoom(b.n - 1), 4)
        if b.kind == 'depth':
            pj = LOGS / f'depth_proof_{k}.json'
            if not pj.exists(): DP.proof(b.dcfg, str(pj))
            d = json.load(open(pj)); r['depth_proof'] = str(pj.relative_to(BR)); r['face_layers'] = b.log['face_layers']
            f0 = d['formats'][list(d['formats'])[0]] if d.get('formats') else {}
            r['depth_rigidity'] = [dict(name=x['name'], layer=x['layer'], in_layer=x['in_layer_frac'], alpha_min=x['alpha_min_native'], pass_=x['pass_']) for x in f0.get('rigidity', [])]
            r['depth_single_transform'] = f0.get('single_transform', {}).get('pass_'); r['depth_dot_test'] = f0.get('single_transform', {}).get('dot_test', {}).get('pass_')
            r['depth_disocclusion'] = [dict(revealed_frac=x['revealed_frac'], holes=x['holes_px'], hf_ratio=x['hf_ratio']) for x in f0.get('disocclusion', [])]
            r['depth_guard'] = f0.get('guardrail')
        r['density_max'] = b.log.get('density_max'); res[k] = r; print(k, json.dumps(r, default=str)[:1500], flush=True)
    out = LOGS / ('proofs_' + '_'.join(keys) + '.json' if keys else 'proofs_all.json')
    json.dump(res, open(out, 'w'), indent=1, default=str); print(out)

# ------------------------------------------------------------------ captions (Bathory v3 style; tagline not captioned)
ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
CAP_POS = {'P07': 615, 'P13': 860}   # P13 860 over both the wide and the HEM framing (hem output y ~1125-1425 after the cut)
def ts(t): t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; cs = int(round(s * 100)); return f'{h}:{m:02d}:{cs // 100:02d}.{cs % 100:02d}'
def two_lines(ws):
    txt = ' '.join(ws)
    if len(txt) <= 24: return txt, True
    best = None
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:]); sc = max(len(a), len(b))
        if best is None or sc < best[0]: best = (sc, a + r'\N' + b)
    return best[1], best[0] <= 24
def tagline_index(W):
    for i in range(len(W) - 1):
        if W[i]['word'] == 'History' and W[i + 1]['word'].startswith('remember') and W[i]['start'] >= CUTS[-1]['start'] - 0.5: return i
    raise SystemExit('tagline not found')
def cmd_captions():
    WA_ = json.load(open(WORDS))['words']; it = tagline_index(WA_); W = WA_[:it]; cuts = [c['start'] for c in CUTS[1:]]
    segs, cur = [], []
    for w in W:
        if cur and (w['line'] != cur[-1]['line'] or any(cur[-1]['start'] < c - 0.1 and w['start'] >= c - 0.1 for c in cuts)):
            segs.append(cur); cur = []
        cur.append(w)
        if w['word'][-1] in '.?!;:': segs.append(cur); cur = []
    if cur: segs.append(cur)
    def fits(ch): return len(ch) <= 7 and two_lines([x['word'] for x in ch])[1]
    def split(ch):
        if fits(ch): return [ch]
        best = None
        for k in range(2 if len(ch) > 3 else 1, len(ch) - 1 if len(ch) > 3 else len(ch)):
            A, B2 = ch[:k], ch[k:]; la = len(' '.join(x['word'] for x in A)); lb = len(' '.join(x['word'] for x in B2))
            sc = abs(la - lb) - (12 if A[-1]['word'][-1] == ',' else 0) + (30 if min(len(A), len(B2)) < 2 else 0)
            if best is None or sc < best[0]: best = (sc, k)
        k = best[1]; return split(ch[:k]) + split(ch[k:])
    chunks = [c for sg in segs for c in split(sg)]; lines = []; over = []
    for j, ch in enumerate(chunks):
        st = ch[0]['start']; en = ch[-1]['end'] + 0.25
        if j + 1 < len(chunks): en = min(max(en, ch[-1]['end'] + 0.05), chunks[j + 1][0]['start'])
        else: en = min(en, CUTS[-1]['start'])                                  # nothing on screen over the OUTRO
        txt, ok = two_lines([x['word'] for x in ch])
        if not ok: over.append(txt)
        lines.append((st, en, txt))
    joined = ' '.join(t.replace(r'\N', ' ') for _, _, t in lines); script = ' '.join(x['word'] for x in W); assert joined == script, 'caption text != VO words'
    assert lines[-1][1] <= CUTS[-1]['start'] + 1e-6
    # v2: per-shot caption position (event MarginV; style default 400). P07 raised above the barring beam; P13 raised above the
    # whole path of the mail hem (hem output y 1098-1810 across the move) -> mid-frame over the procession. Events keep their words/timing,
    # except an overridden event is ended at its shot's cut so the raised caption never spills into the next shot.
    def shot_at(t): return next(c for c in CUTS if c['start'] - 1e-6 <= t < c['end'] - 1e-6)
    ev = []
    for a, b, t in lines:
        c = shot_at(a); mv = CAP_POS.get(c['shot'], 0)
        if mv and b > c['end']: b = c['end']
        ev.append((a, b, t, mv, c['shot']))
    with open(ASS, 'x') as f:
        f.write(ASS_HEAD + ''.join(f'Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,{mv},,{t}\n' for a, b, t, mv, _ in ev))
    json.dump([dict(shot=k, start=round(a, 3), end=round(b, 3), marginV=mv or 400, text=t) for a, b, t, mv, k in ev if mv], open(LOGS / 'caption_overrides_v4b.json', 'w'), indent=1)
    tag = ' '.join(x['word'] for x in WA_[it:])
    print(len(lines), 'chunks; overlong:', over, '| uncaptioned tagline:', tag)

def cmd_final():
    cl = SCR / 'clips_v4b'; lst = SCR / 'concat_v4b.txt'; lst.write_text(''.join(f"file '{cl / (k + '.mp4')}'\n" for k in ORDER)); REN.mkdir(exist_ok=True)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(MIXWAV),
           '-vf', f"subtitles={ASS}", '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30',
           '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{DUR:.3f}', str(FINAL)]
    subprocess.run(cmd, check=True); print(FINAL, md5(FINAL))
def cmd_sheet():
    out = BR / 'bjorn_rough_v4b_contact_sheet.jpg'; tiles = []
    for c in CUTS:
        k = c['shot']; t = (c['start'] + c['end']) / 2; p = SCR / f'sheet_{k}.png'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-ss', f'{t:.3f}', '-i', str(FINAL), '-frames:v', '1', str(p)], check=True)
        im = cv2.resize(cv2.imread(str(p)), (270, 480), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (270, 30), (0, 0, 0), -1); cv2.putText(im, f'{k}  {t:.1f}s', (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(im); p.unlink()
    cols = 7; rows = [np.hstack(tiles[r * cols:(r + 1) * cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r * cols:(r + 1) * cols]))) for r in range((len(tiles) + cols - 1) // cols)]
    assert not out.exists(); cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88]); print(out)

if __name__ == '__main__' and len(sys.argv) > 1:
    a = sys.argv
    if a[1] == 'still': cmd_still(a[2], a[3], a[4] if len(a) > 4 and not a[4].startswith('--') else None)
    elif a[1] == 'clip': cmd_clip(a[2])
    elif a[1] == 'proofs': cmd_proofs(a[2:] or None)
    else: dict(faces=cmd_faces, captions=cmd_captions, final=cmd_final, sheet=cmd_sheet)[a[1]]()
