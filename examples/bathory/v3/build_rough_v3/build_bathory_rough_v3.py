#!/workspace/mpvenv/bin/python
"""Bathory ROUGH v3 build. Plates/engines read-only (importlib, no bytecode); writes only into v3/build_rough_v3/ and v3/renders/.
ffmpeg -n everywhere.  Usage: build.py plan | still <beat> <t> | clip <beat> | proofs | captions | final | sheet"""
import sys; sys.dont_write_bytecode = True
import json, math, re, subprocess, importlib.util, hashlib
from pathlib import Path
import numpy as np, cv2
cv2.setNumThreads(2)
ROOT = Path('/workspace/posterity'); BA = ROOT / 'standalones/bathory'; V3 = BA / 'v3'; BR = V3 / 'build_rough_v3'; PL = BA / 'v2/plates'
SCR = BR / 'scratch'; SCR.mkdir(exist_ok=True); LOGS = BR / 'logs'; LOGS.mkdir(exist_ok=True)
FPS = 30; OW, OH = 1080, 1920
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
FX = _load('fx_v1c_ro', ROOT / 'standalones/edward-ii/edit/fx_v1c.py')
DU = _load('dust_v1_ro', ROOT / 'engine-rnd/dust/dust_v1.py')
SM = _load('smoke_v2_ro', ROOT / 'engine-rnd/smoke/smoke_v2.py')
SN = _load('snow_v1b_ro', ROOT / 'engine-rnd/snow/snow_v1b.py')
WG = _load('water_v1_1_ro', ROOT / 'engine-rnd/water/water_v1_1.py'); WA = WG.W; GR = WG.G
SN.CACHE = BR / 'cache/snow'; FX.SPECS = {}; FX.PULSE = {}
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
assert md5(ROOT / 'engine-rnd/water/water_v1.py').startswith('811734e9'), 'water_v1 not the locked file'

# ------------------------------------------------------------------------------------------- timeline from the tight VO
VO = V3 / 'vo/vo_oliver_v3_final_tight.wav'; WORDS = V3 / 'vo/vo_oliver_v3_final_tight_words.json'
WD = json.load(open(WORDS))['words']; VO_END = WD[-1]['end']; HOLD_END = 2.65; DUR = round(round((VO_END + HOLD_END) * FPS) / FPS, 3)
LEAD = 0.10
SEQ = [('h01', 'Elizabeth Báthory was'), ('h02', 'Of forcing others'), ('b06', 'People said young'), ('b07', "He sent Hungary's"),
       ('b04', 'One December night'), ('b05', 'Báthory was eating'), ('h03', 'Thurzó wrote that'), ('b12', 'Báthory was taken'),
       ('b01a_v1', 'Four servants, three'), ('b01a', 'Under torture, they'), ('b01b', 'But Báthory was'),
       ('b17', 'Nothing was ever'), ('b13a', 'The king pressed'), ('b13b', 'Thurzó prevented it'), ('b08', 'Thurzó had fought'),
       ('b14', 'Many historians think'), ('b16', 'rather than risk'), ('b18', 'She died in'), ('h04a', 'Then someone added'),
       ('b15', 'No witness against'), ('h04b', 'No court ever')]
def norm(w): return re.sub(r"[^\w']", '', w.lower().replace('’', "'"))
def find(phrase, after):
    p = [norm(x) for x in phrase.split()]
    for i in range(after, len(WD) - len(p) + 1):
        if [norm(WD[i + k]['word']) for k in range(len(p))] == p: return i
    raise SystemExit(f'phrase not found: {phrase}')
CUTS = []; _i = 0
for j, (k, ph) in enumerate(SEQ):
    _i = find(ph, _i); t = 0.0 if j == 0 else math.floor((WD[_i]['start'] - LEAD) * FPS) / FPS
    CUTS.append([k, t, None, _i])
for j in range(len(CUTS)): CUTS[j][2] = CUTS[j + 1][1] if j + 1 < len(CUTS) else DUR
def frames_of(key):
    for k, a, b, _ in CUTS:
        if k == key: return int(round(a * FPS)), int(round(b * FPS))
T_TAG = WD[find('History remembers the', 0)]['start']; T_L13 = WD[find('She died in', 0)]['start']

# ------------------------------------------------------------------------------------------- helpers
def load_rgb(p): a = cv2.imread(str(p), cv2.IMREAD_COLOR); assert a is not None, p; return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def R(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
def sstep(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def writer(path):
    cmd = ['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
def warp_out(img, A): return cv2.warpAffine(img, A, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
def heraldry(P, polys, feather=26, desat=0.7, dark=0.6, soften=2.4):
    H, W = P.shape[:2]; m = np.zeros((H, W), np.float32)
    for p in polys: cv2.fillPoly(m, [np.int32(p)], 1.0)
    m = cv2.GaussianBlur(m, (0, 0), feather); Pf = P.astype(np.float32); g = luma(Pf)[..., None]
    d = (Pf * (1 - desat) + g * desat) * dark; soft = cv2.GaussianBlur(d, (0, 0), soften); bl = cv2.bilateralFilter(d.astype(np.float32), 9, 30, 6)
    d = 0.5 * soft + 0.5 * bl
    return np.clip(Pf * (1 - m[..., None]) + d * m[..., None] + 0.5, 0, 255).astype(np.uint8), m
WARM = (255, 214, 160); COOL = (214, 222, 236)
GREY_SMOKE = dict(color_dark=[44, 46, 52], color_light=[108, 110, 118], glow=None)
def motes(n, amp, color=WARM, sigma=(0.9, 2.8), speed=(3, 11), d=(-0.3, -0.4), jit=60, **k):
    L = dict(type='motes', zone=0, n=n, sigma=list(sigma), speed=list(speed), dir=list(d), dir_jitter_deg=jit, turb_px=6,
             turb_hz=[0.07, 0.3], life_s=[5, 12], amp=amp, near_gain=1.8, depth_power=2.0, pre_roll=40, color=list(color)); L.update(k); return L
def zone(poly, lo=40, hi=180, feather=40, blur=8, gamma=0.8):
    return dict(type='shaft', poly=poly, feather=feather, lum_lo=lo, lum_hi=hi, lum_blur=blur, lum_gamma=gamma)

# ------------------------------------------------------------------------------------------- H04a ink-graded derived copy
H04A_SRC = PL / 'h04a_priest_writes_legend.png'; H04A_INK = BR / 'h04a_priest_writes_legend_inkgraded.png'
INK_BOX = (300, 1240, 540, 1410)
def make_h04a_ink():
    if H04A_INK.exists(): return json.load(open(LOGS / 'h04a_inkgrade.json'))
    P = load_rgb(H04A_SRC).astype(np.float32); H, W = P.shape[:2]; x0, y0, x1, y1 = INK_BOX
    r, g, b = P[..., 0], P[..., 1], P[..., 2]; red = np.clip((0.48 - g / np.maximum(r, 1)) / 0.12, 0, 1) * (r > 25)   # blood G/R~0.3; parchment ~0.7, wood ~0.45+
    box = np.zeros((H, W), np.float32); box[y0:y1, x0:x1] = 1; box = cv2.GaussianBlur(box, (0, 0), 6); box[:y0 - 20] = 0; box[y1 + 20:] = 0; box[:, :x0 - 20] = 0; box[:, x1 + 20:] = 0
    m = cv2.GaussianBlur(red.astype(np.float32), (0, 0), 1.2) * box
    L = luma(P)[..., None]; tint = np.float32([1.0, 0.86, 0.74]); tint = tint / (0.299 * tint[0] + 0.587 * tint[1] + 0.114 * tint[2])
    ink = L * tint[None, None]                                   # iron-gall brown-black at the SAME luma (texture kept)
    out = np.clip(P * (1 - m[..., None]) + ink * m[..., None] + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(str(H04A_INK), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    info = dict(src=str(H04A_SRC), src_md5=md5(H04A_SRC), out=str(H04A_INK), out_md5=md5(H04A_INK), box=INK_BOX,
                changed_px=int((np.abs(out.astype(int) - P.astype(int)).max(-1) > 0).sum()), mask_px_gt_0_5=int((m > 0.5).sum()),
                outside_box_changed_px=int(((np.abs(out.astype(int) - P.astype(int)).max(-1) > 0) & (box == 0)).sum()))
    json.dump(info, open(LOGS / 'h04a_inkgrade.json', 'x'), indent=1); return info

# ------------------------------------------------------------------------------------------- per-beat config
B = {}
B['h01'] = dict(plate='h01_heated_iron_threat.png', kind='h01', box0=(0, 120, 720), box1=(0, 250, 800), tilt=(0.6, 3.4),
    fx=[dict(auto=[(400, 190, 580, 345)], spill_amp=1.6, relight_exclude=[(150, 250, 430, 580), (700, 600, 830, 820)], _kind='candle'),
        dict(torch=[(0, 1170, 330, 1560)], relight_exclude=[(150, 250, 430, 580), (700, 600, 830, 820)], spill_amp=1.6, _kind='torch')])
B['h02'] = dict(plate='h02_freezing_water.png', kind='h02', center=(0.5, 0.42))
H02_FACES = [R(330, 460, 575, 720), R(200, 200, 370, 370), R(680, 235, 830, 400)]
H02_WATER = dict(name='h02_freezing_water_streams_v3', plate=str(PL / 'h02_freezing_water.png'), seed=202, push=[1.0, 1.06], push_center=[0.5, 0.42],
    water=[[[165, 505], [245, 495], [300, 540], [312, 620], [315, 700], [310, 760], [230, 770], [195, 720], [170, 620]],
           [[630, 630], [810, 620], [780, 670], [710, 710], [690, 780], [680, 900], [670, 960], [590, 960], [570, 860], [560, 740], [590, 680]]],
    protect=H02_FACES, protect_feather=5,
    layers=[dict(type='glints', hp_sigma=4.0, thresh=10, min_dist=7, n_max=140, edge_px=4, sigma=1.8, star=0.35, star_len=6, halo=0.10, halo_sigma=5.0,
                 own_r=4, lift=0.6, dim=0.2, add=0.55, color=[225, 235, 250], rate_lo=[0.4, 1.0], rate_hi=[1.0, 2.4], thresh_t=0.45, power=1.6)])
H02_STEAM = dict(seed=22, protect=H02_FACES, protect_feather=36, flame_keepout=0.0, preroll=8.0, billows=[], fires=[],
    emitters=[dict(name='steam_a', type='haze', rect=[360, 300, 520, 400], drift=6.0, opacity=0.3, lo=220, hi=6.0, swirl=14.0, feather=34.0,
                   color_dark=[150, 152, 158], color_light=[200, 202, 208], glow=None, res=0.5),
              dict(name='steam_b', type='haze', rect=[560, 360, 670, 470], drift=-5.0, opacity=0.28, lo=220, hi=6.0, swirl=14.0, feather=30.0,
                   color_dark=[150, 152, 158], color_light=[200, 202, 208], glow=None, res=0.5)])
B['b06'] = dict(plate='b06_rumours_village.png', center=(0.65, 0.45),
    dust=dict(zones=[zone([[120, 180], [941, 180], [941, 820], [700, 900], [600, 640], [120, 470]], lo=80, hi=220, feather=50)],
              protect=[R(0, 450, 640, 1350), R(540, 400, 941, 760)], layers=[motes(520, 110, color=(255, 222, 170), d=(0.5, -0.2), speed=(3, 10))]))
B['b07'] = dict(plate='b07_thurzo_ordered.png', center=(0.5, 0.3), fx=[dict(manual=[(78, 285, 122, 375)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[99, 292], height=260, lean=10, seed=2, opacity=0.35)], protect=[R(400, 290, 570, 520)]))
B['b04'] = dict(plate='b04_riders_at_the_manor.png', center=(0.5, 0.45),
    fx=[dict(torch=[(250, 545, 345, 735)], window=[(430, 580, 478, 632), (560, 570, 606, 622), (720, 548, 768, 598), (560, 710, 606, 760),
         (890, 555, 941, 606), (720, 735, 768, 790)], window_amp=0.7, relight_exclude=[(130, 790, 235, 905), (400, 770, 505, 880), (540, 830, 640, 945)], spill_amp=1.6, _kind='torch')],
    smoke=dict(emitters=[dict(name='torch', type='torch', src=[296, 560], height=380, w0=8, w1=100, lean=-18, seed=1, opacity=0.4, **GREY_SMOKE)],
               protect=[R(130, 790, 235, 905), R(400, 770, 505, 880), R(540, 830, 640, 945)]))
B['b05'] = dict(plate='b05_supper_manor.png', center=(0.72, 0.3), her=[R(0, 0, 345, 470)],
    fx=[dict(auto=[(40, 560, 270, 720)], spill_amp=1.6, _kind='candle'),
        dict(offscreen=[dict(xy=(860, 400), h=60, radius=420, kind='torch')], relight_exclude=[(360, 380, 580, 620)], spill_amp=1.4, _kind='torch')],
    smoke=dict(emitters=[dict(name='wick_mid', type='candle', src=[152, 600], height=240, lean=8, seed=1, opacity=0.3)], protect=[R(360, 380, 580, 620)]))
B['h03'] = dict(plate='h03_thurzo_claimed_finding.png', center=(0.55, 0.5),
    fx=[dict(torch=[(395, 50, 520, 320)], relight_exclude=[(330, 200, 640, 560), (100, 120, 330, 420)], spill_amp=1.5, _kind='torch')])
B['b12'] = dict(plate='b12_taken_up_to_fortress.png', center=(0.5, 0.38), snow='b12',
    fx=[dict(torch='AUTO_B12', window=[(365, 225, 395, 270)], window_amp=0.7, radius_mult=0.5, spill_amp=1.4, _kind='torch')], smoke=dict(emitters='AUTO_B12', protect=[]))
B['b01a_v1'] = dict(plate='b01a_bytca_led_away_v1.png', center=(0.5, 0.5), snow=str(BR / 'snow_b01a_v1.json'))
B['b01a'] = dict(plate='b01a_bytca_led_away.png', center=(0.45, 0.45), snow=str(BR / 'snow_b01a.json'),
    fx=[dict(torch=[(0, 870, 215, 1360)], relight_exclude=[(40, 380, 160, 560), (330, 540, 520, 720), (190, 520, 290, 640),
         (520, 380, 630, 520), (680, 340, 860, 520)], spill_amp=1.6, _kind='torch')])
B['b01b'] = dict(plate='b01b_never_tried.png', center=(0.4, 0.4), her=[R(770, 0, 941, 480)], fx=[dict(manual=[(72, 405, 122, 530)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[97, 420], height=260, lean=-6, seed=1, opacity=0.35)], protect=[R(400, 230, 600, 520)]))
B['b17'] = dict(plate='b17_secondhand_witnesses.png', center=(0.4, 0.4), snow='b17', her=[R(95, 60, 335, 285), R(85, 430, 170, 570)],
    fx=[dict(torch=[(50, 840, 235, 1120)], relight_exclude=[(430, 520, 941, 1080), (60, 560, 260, 720)], spill_amp=1.5, _kind='torch')],
    smoke=dict(emitters=[dict(name='brazier', type='torch', src=[135, 860], height=420, w0=18, w1=140, lean=12, seed=5, opacity=0.4, **GREY_SMOKE)],
               protect=[R(430, 520, 941, 1080), R(60, 560, 260, 720)]))
B['b13a'] = dict(plate='b13a_doors_open.png', center=(0.65, 0.42), push=(1.0, 1.035),
    fx=[dict(auto=[(630, 520, 740, 660)], spill_amp=1.6, relight_poly=[[(484, 145), (753, 145), (753, 1300), (484, 1300)]], _kind='candle')])
B['b13b'] = dict(plate='b13b_doors_shut.png', kind='b13b')
B['b08'] = dict(plate='b08_husbands_letter.png', center=(0.4, 0.45), fx=[dict(manual=[(272, 105, 325, 275)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[298, 112], height=240, lean=-8, seed=3, opacity=0.35)], protect=[]))
B['b14'] = dict(plate='b14_why_window.png', center=(0.78, 0.3),
    dust=dict(zones=[zone([[560, 130], [714, 130], [714, 840], [690, 1250], [560, 1250]], lo=40, hi=170, feather=40)],
              protect=[R(330, 280, 490, 570)], layers=[motes(300, 120, color=COOL, d=(-0.3, 0.4), speed=(3, 9))]))
B['b16'] = dict(plate='b16_family_silence.png', center=(0.5, 0.3),
    fx=[dict(torch=[(340, 330, 690, 620)], relight_exclude=[(50, 420, 230, 580), (465, 505, 610, 670), (725, 390, 915, 580)], spill_amp=1.6, _kind='torch')],
    smoke=dict(emitters=[dict(name='hearth', type='torch', src=[515, 420], height=170, w0=30, w1=160, lean=0, seed=4, opacity=0.35, **GREY_SMOKE)],
               protect=[R(0, 0, 941, 300), R(0, 0, 330, 1672), R(700, 0, 941, 1672), R(0, 630, 941, 1672), R(50, 420, 230, 580), R(465, 505, 610, 670), R(725, 390, 915, 580)]))
B['b18'] = dict(plate='b18_empty_room.png', center=(0.72, 0.4), her=[R(25, 130, 205, 690)],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[692, 738], height=230, lean=-6, seed=6, opacity=0.35)], protect=[]),
    dust=dict(zones=[zone([[680, 200], [860, 200], [860, 800], [600, 1350], [380, 1350], [520, 700]], lo=50, hi=200, feather=50)],
              protect=[], layers=[motes(320, 110, color=COOL, d=(-0.3, 0.4), speed=(3, 9))]))
B['h04a'] = dict(plate=str(H04A_INK), center=(0.42, 0.70),
    fx=[dict(auto=[(760, 470, 940, 740)], spill_amp=1.6, relight_exclude=[(180, 150, 600, 720)], _kind='candle')])
B['b15'] = dict(plate='b15_thurzo_depositions.png', center=(0.45, 0.55), her=[R(0, 0, 300, 590)], fx=[dict(manual=[(38, 690, 102, 845)], spill_amp=1.6, _kind='candle')])
B['h04b'] = dict(plate='h04b_final_stare.png', kind='h04b', center=(0.44, 0.336),
    fx=[dict(auto=[(10, 640, 130, 860)], spill_amp=1.6, relight_exclude=[(240, 320, 620, 860)], _kind='candle')])
SNOW_CUSTOM = {
    'snow_b01a_v1.json': dict(base='b12', name='b01a_v1_snow_v3', plate=str(PL / 'b01a_bytca_led_away_v1.png'), plate_md5=None, seed=1101, color_gain=1.0,
        push=[1.0, 1.06], push_center=[0.5, 0.5], wind=-3.0, tiers=dict(far=dict(n=200, depth=0.3), mid=dict(n=110, depth=0.55), near=dict(n=36)),
        faces=[], subjects=[], keepout=[], interior=[], land=[[[0, 1180], [941, 1120], [941, 1672], [0, 1672]]], land_gain=0.0, land_feather=70),
    'snow_b01a.json': dict(base='b12', name='b01a_snow_v3', plate=str(PL / 'b01a_bytca_led_away.png'), plate_md5=None, seed=1102, color_gain=1.0,
        push=[1.0, 1.06], push_center=[0.45, 0.45], wind=4.0, tiers=dict(far=dict(n=180, depth=0.3), mid=dict(n=96, depth=0.55), near=dict(n=30)),
        faces=[[40, 380, 160, 560], [330, 540, 520, 720], [190, 520, 290, 640], [520, 380, 630, 520], [680, 340, 860, 520]], subjects=[],
        keepout=[R(0, 850, 235, 1380)], interior=[], land=[[[0, 1300], [941, 1260], [941, 1672], [0, 1672]]], land_gain=0.0, land_feather=70)}
def ensure_snow_cfgs():
    for n, c in SNOW_CUSTOM.items():
        p = BR / n
        if not p.exists():
            c = dict(c); c['plate_md5'] = md5(c['plate']); json.dump(c, open(p, 'x'), indent=1)

# ------------------------------------------------------------------------------------------- calibration
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
    pp = lambda v: float((v.max() - v.min()) / max(v.mean(), 1e-3) * 100); st = lambda v: float(np.abs(np.diff(v)).max() / max(v.mean(), 1e-3) * 100)
    return dict(whole=pp(wl), local=pp(ll), step=max(st(wl), st(ll)))
def calibrate(inst, P, kind, scale=1.0):
    FX.PULSE[inst.key] = 1.0; m1 = fx_metrics(inst, P)
    T = TARGET[kind]; pul = min(T['local'] / max(m1['local'], 1e-3), T['whole'] / max(m1['whole'], 1e-3), T['step'] / max(m1['step'], 1e-3))
    for _ in range(6):
        FX.PULSE[inst.key] = pul; m = fx_metrics(inst, P); L = LIMIT[kind]
        over = max(m['whole'] / L['whole'], m['step'] / L['step'], m['local'] / L['local']); under = m['local'] / T['local']
        if over > 1.0: pul *= 0.95 / over
        elif under < 0.85 and kind == 'candle': pul *= min(1.0 / under, 0.95 / max(over, 1e-3))
        else: break
    pul *= scale; FX.PULSE[inst.key] = pul; m = fx_metrics(inst, P); return pul, m1, m

# ------------------------------------------------------------------------------------------- snow overlay (v2)
def snow_overlay(sh, base_u8, A, t):
    w, h = sh.out_wh; out = base_u8.astype(np.float32)
    col = sh.warp(sh.col, A); prot = sh.warp(sh.protect.astype(np.uint8), A, cv2.INTER_NEAREST) > 0; info = {}
    for L in sh.tiers:
        Ms = sh.warp(L['M'], A); x, y, env = sh.positions(L, t)
        xi = np.clip(np.round(x).astype(int), 0, w - 1); yi = np.clip(np.round(y).astype(int), 0, h - 1)
        ins = (x > -L['mg']) & (x < w + L['mg']) & (y > -L['mg']) & (y < h + L['mg']); peak = L['op'] * env * ins
        cover = np.clip(np.minimum.reduce([x, w - 1 - x, y, h - 1 - y]) / (3 * L['sig']) + 0.5, 0, 1)
        info[L['name']] = int((peak * Ms[yi, xi] * cover > 0.08).sum()); aer = L['T']['aerial']
        for k in np.nonzero(peak > 0.01)[0]:
            s = L['sig'][k]; sy = s * 1.12; r = int(math.ceil(3.2 * sy)) + 1; cx, cy = x[k], y[k]
            x0, y0 = max(int(cx) - r, 0), max(int(cy) - r, 0); x1, y1 = min(int(cx) + r + 2, w), min(int(cy) + r + 2, h)
            if x1 <= x0 or y1 <= y0: continue
            gx = np.exp(-0.5 * ((np.arange(x0, x1) - cx) / s) ** 2); gy = np.exp(-0.5 * ((np.arange(y0, y1) - cy) / sy) ** 2)
            a = (peak[k] * gy[:, None] * gx[None, :]).astype(np.float32) * Ms[y0:y1, x0:x1]
            if a.max() < 1e-3: continue
            cc = col[yi[k], xi[k]]
            if aer > 0: cc = cc * (1 - aer) + np.maximum(cc * 0.92, out[yi[k], xi[k]] * 1.08) * aer
            sub = out[y0:y1, x0:x1]; sub += (cc[None, None] - sub) * a[..., None]
    o = np.clip(out + 0.5, 0, 255).astype(np.uint8); o[prot] = base_u8[prot]; return o, info
def snow_shot(key):
    ensure_snow_cfgs(); return SN.SnowShot(dict(SN.get_cfg(key)), '1080x1920', FPS)

# ------------------------------------------------------------------------------------------- beat
MOD = BR / 'cache/plates_mod'; MOD.mkdir(exist_ok=True, parents=True)
def box_matrix(x0, y0, w):
    s = OW / w; return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])
class Beat:
    def __init__(self, key, calib=True):
        self.key = key; c = B[key]; self.c = c; self.kind = c.get('kind', 'flat'); f0, f1 = frames_of(key); self.f0, self.n = f0, f1 - f0
        self.log = dict(beat=key, kind=self.kind, frames=[f0, f1], t=[round(f0 / FPS, 3), round(f1 / FPS, 3)], seconds=round(self.n / FPS, 3))
        self.fx = []; self.dust = None; self.smoke = None; self.snow = None; self.water = None
        if key == 'h04a': self.log['inkgrade'] = make_h04a_ink()
        path = Path(c['plate']) if c['plate'].startswith('/') else PL / c['plate']; P = load_rgb(path); pk = path.name.split('_')[0]
        H, W = P.shape[:2]; self.W, self.H = W, H; self.log.update(plate=str(path), plate_md5=md5(path), plate_wh=[W, H])
        if c.get('her'):
            P, m = heraldry(P, c['her']); path = MOD / f'{pk}_her_{key}.png'
            if not path.exists(): cv2.imwrite(str(path), cv2.cvtColor(P, cv2.COLOR_RGB2BGR))
            self.log['heraldry_polys'] = c['her']
        self.path = path; self.P = P; self.Pf = P.astype(np.float32)
        if c.get('snow'): self.snow = snow_shot(c['snow']); self.log['snow_cfg'] = c['snow']; self.log['snow_face_boxes'] = self.snow.face_boxes
        for j, spec in enumerate(c.get('fx', [])):
            spec = dict(spec); kind = spec.pop('_kind')
            if spec.get('torch') == 'AUTO_B12': spec['torch'] = self.b12_torches()
            FX.SPECS[pk] = spec; inst = FX.PlateFX(str(path), seed=j); inst.key = f'{key}#{j}'
            self.log.setdefault('fx', []).append(dict(kind=kind, info=inst.info(), spec={k: v for k, v in spec.items()}))
            if spec.get('torch') and spec['torch'] != 'AUTO_B12':
                fz = self.zoom_max()
                try: self.log['fx'][-1]['fire_sharpness'] = GR.check_fire_sharpness(load_rgb(self.path), spec['torch'], zoom=fz, mode='warn')
                except Exception as e: self.log['fx'][-1]['fire_sharpness'] = f'ERR {e}'
            if calib:
                pul, m1, m = calibrate(inst, P, kind); self.log['fx'][-1].update(pulse=round(pul, 4), metrics_at_pulse1=m1, metrics=m)
            self.fx.append(inst)
        if c.get('dust'):
            d = c['dust']; seed = int(hashlib.md5(key.encode()).hexdigest()[:8], 16) % 1000
            cfg = dict(plate=str(path), seed=seed, protect_feather=12, zones=d['zones'], protect=d.get('protect', []), layers=d['layers'])
            self.dust = DU.DustShot(cfg); self.log['dust'] = dict(seed=seed, n=[L['n'] for L in d['layers']], amp=[L['amp'] for L in d['layers']])
        if c.get('smoke'):
            s = c['smoke']; em = self.b12_smoke() if s['emitters'] == 'AUTO_B12' else s['emitters']
            cfg = dict(seed=7, protect=s.get('protect', []), protect_feather=36, flame_keepout=0.0, preroll=8.0, emitters=em, billows=[], fires=[])
            self.smoke = SM.SmokeScene(SM.load_plate(str(path)), cfg); self.log['smoke'] = [dict(name=e['name'], type=e['type'], opacity=e['opacity']) for e in em]
            assert all(e['opacity'] <= 0.4 for e in em)
        if self.kind == 'h02':
            self.water = WA.WaterShot(H02_WATER); self.steam = SM.SmokeScene(self.P, H02_STEAM)
            self.log['water'] = self.water.info(); self.log['steam'] = [dict(name=e['name'], opacity=e['opacity']) for e in H02_STEAM['emitters']]
            self.log['water_guard'] = WG.guard(H02_WATER, 'refuse')
        if self.kind == 'b13b': self._b13b()
        self.log['density_max'] = round(self.density_max(), 4)
        try: self.log['guard_density'] = GR.check_pixel_density((W, H), (OW, OH), (1.0, 1.0), mode='measure', crop_zoom=self.zoom_max(), name=key)
        except Exception as e: self.log['guard_density'] = f'ERR {e}'
    def zoom_max(self):
        s0 = max(OW / self.W, OH / self.H); return self.density_max() / s0
    def density_max(self):
        return max(float(self.cam(i)[0, 0]) for i in (0, self.n // 4, self.n // 2, 3 * self.n // 4, self.n - 1))
    def b12_torches(self):
        P = self.P.astype(np.float32); x0, y0, x1, y1 = 330, 560, 640, 770
        sc = luma(P[y0:y1, x0:x1]) + 0.8 * np.clip(P[y0:y1, x0:x1, 0] - P[y0:y1, x0:x1, 2], 0, 255); sc = cv2.GaussianBlur(sc, (0, 0), 3); pts = []
        for _ in range(4):
            yy, xx = np.unravel_index(np.argmax(sc), sc.shape); pts.append((x0 + xx, y0 + yy)); sc[max(0, yy - 30):yy + 30, max(0, xx - 30):xx + 30] = -1e9
        self.b12_pts = sorted(pts); self.log['b12_torch_pts'] = [list(map(int, p)) for p in self.b12_pts]
        return [(int(x - 22), int(y - 30), int(x + 22), int(y + 22)) for x, y in self.b12_pts]
    def b12_smoke(self):
        return [dict(name=f't{i}', type='torch', src=[int(x), int(y - 18)], height=150, w0=4, w1=45, lean=-10, seed=10 + i, opacity=0.35, **GREY_SMOKE)
                for i, (x, y) in enumerate(self.b12_pts)]
    def _b13b(self):
        a = B['b13a']; P = load_rgb(PL / a['plate']); Wa, Ha = P.shape[1], P.shape[0]; self.zA = a['push'][1]
        M = SN.cam_matrix((Wa, Ha), (OW, OH), 1.0, 1.0, self.zA, a['center']); ax, ay = a['center'][0] * Wa, a['center'][1] * Ha
        self.MA = M; self.SA = float(M[0, 0]); self.aout = (M[0, 0] * ax + M[0, 2], M[1, 1] * ay + M[1, 2]); self.anc = (ax, ay)
        reg = json.load(open(BA / 'v2/build_rough_v1/b13/b13_registration.json'))['ecc_b_to_a']['translation']['warp']; self.d = (reg[0][2], reg[1][2])
        fa = warp_out(P, M).astype(np.float32); best = None; m = np.ones((OH, OW), bool)
        pts = np.float32([[440, 120], [800, 120], [800, 1100], [440, 1100]]) @ M[:, :2].T + M[:, 2]
        x0, y0 = pts.min(0).astype(int); x1, y1 = pts.max(0).astype(int); m[max(0, y0):y1, max(0, x0):x1] = False
        for sg in (1, -1, 0):
            self.sg = sg; fb = warp_out(self.P, self.cam(0)).astype(np.float32)
            err = float(np.abs(luma(fa) - luma(fb))[m].mean()); best = (err, sg) if best is None or err < best[0] else best
            self.log.setdefault('b13_cut_diff', {})[str(sg)] = round(err, 3)
        self.sg = best[1]; self.log['b13_reg_sign'] = self.sg; self.log['b13_reg_shift_plate_px'] = [round(v * self.sg, 3) for v in self.d]
    def cam(self, i):
        t = i / FPS; u = i / max(self.n - 1, 1); c = self.c
        if self.kind == 'h01':
            e = sstep((t - c['tilt'][0]) / (c['tilt'][1] - c['tilt'][0])); b0, b1 = c['box0'], c['box1']
            x0 = b0[0] + (b1[0] - b0[0]) * e; y0 = b0[1] + (b1[1] - b0[1]) * e; w = 1.0 / (1 / b0[2] + (1 / b1[2] - 1 / b0[2]) * e)
            return box_matrix(x0, y0, w)
        if self.kind == 'h04b':
            tp = T_TAG - self.f0 / FPS; return SN.cam_matrix((self.W, self.H), (OW, OH), min(1.0, t / tp), 1.0, 1.06, c['center'])
        if self.kind == 'b13b':
            z = self.zA + (1.06 - self.zA) * (1 - (1 - u) ** 2); S = self.SA * z / self.zA; ax, ay = self.aout; ancx, ancy = self.anc
            dx, dy = self.d[0] * self.sg, self.d[1] * self.sg
            return np.float32([[S, 0, ax - S * ancx + S * dx], [0, S, ay - S * ancy + S * dy]])
        z0, z1 = c.get('push', (1.0, 1.06)); return SN.cam_matrix((self.W, self.H), (OW, OH), u, z0, z1, c['center'])
    def plate_comp(self, t):
        if not (self.fx or self.dust or self.smoke or self.water): return self.P
        acc = self.Pf.copy()
        for inst in self.fx: acc += inst.render(t).astype(np.float32) - self.Pf
        if self.dust: acc += self.dust.frame(t).astype(np.float32) - self.Pf
        if self.smoke: acc += np.asarray(self.smoke.frame(t)).astype(np.float32) - self.Pf
        if self.water is not None:
            acc += self.water.frame(t).astype(np.float32) - self.Pf; acc += self.steam.frame(t).astype(np.float32) - self.Pf
        return np.clip(acc + 0.5, 0, 255).astype(np.uint8)
    def render_frame(self, i, info=None):
        t = i / FPS; A = self.cam(i); fr = warp_out(self.plate_comp(t), A)
        if self.snow is not None:
            fr, inf = snow_overlay(self.snow, fr, A, t)
            if info is not None: info.append(inf)
        return fr

def cmd_plan():
    for k, a, b, wi in CUTS: print(f'{k:8s} {a:7.3f} {b:7.3f} {b - a:6.3f}  "{WD[wi]["word"]}" @ {WD[wi]["start"]:.3f}')
    print('DUR', DUR, 'VO_END', VO_END, 'T_TAG', T_TAG, 'T_L13', T_L13)
def cmd_still(key, t, out=None):
    b = Beat(key, calib=False); i = min(int(round(float(t) * FPS)), b.n - 1); inf = []
    fr = b.render_frame(i, inf); out = out or str(SCR / f'still_{key}_{i:03d}.jpg')
    cv2.imwrite(out, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR)); print(json.dumps(b.log, default=str)[:2500]); print(out)
def cmd_clip(key):
    cl = SCR / 'clips'; cl.mkdir(exist_ok=True); out = cl / f'{key}.mp4'; lg = LOGS / f'beat_{key}.json'
    if out.exists(): print('exists', out); return
    b = Beat(key); p = writer(out); vis = []
    for i in range(b.n):
        inf = []; fr = b.render_frame(i, inf); p.stdin.write(fr.tobytes())
        if inf: vis.append(inf[0])
    p.stdin.close(); assert p.wait() == 0
    if vis:
        tot = [sum(v for k, v in d.items() if not k.startswith('_')) for d in vis]
        b.log['snow_visible_flakes_per_frame'] = dict(min=int(min(tot)), mean=round(float(np.mean(tot)), 1), max=int(max(tot)))
    json.dump(b.log, open(lg, 'w'), indent=1, default=str); print('done', key, b.n)
def cmd_proofs():
    """H02: water_v1 impulse/protect proof + steam/face proof + combined 'nothing else moves' proof."""
    out = LOGS / 'h02_water_proof.json'
    if not out.exists(): WA.proof(dict(H02_WATER), str(out))
    b = Beat('h02', calib=False); P = b.P.astype(int); H, W = P.shape[:2]
    face = np.zeros((H, W), np.uint8)
    for p in H02_FACES: cv2.fillPoly(face, [np.int32(p)], 1)
    face = face > 0; wallow = ~b.water.protect; sallow = b.steam.allow_mask(); r = dict(times=[], face_changed_px=[], outside_allow_changed_px=[], water_changed_px=[], steam_changed_px=[])
    for t in [0.0, 0.7, 1.4, 2.1]:
        f = b.plate_comp(t).astype(int); ch = np.abs(f - P).max(-1) > 0
        r['times'].append(t); r['face_changed_px'].append(int((ch & face).sum())); r['outside_allow_changed_px'].append(int((ch & ~(wallow | sallow)).sum()))
        r['water_changed_px'].append(int((ch & wallow).sum())); r['steam_changed_px'].append(int((ch & sallow & ~wallow).sum()))
    r['pass'] = max(r['face_changed_px']) == 0 and max(r['outside_allow_changed_px']) == 0
    json.dump(r, open(LOGS / 'h02_combined_proof.json', 'w'), indent=1); print(json.dumps(r))

# ------------------------------------------------------------------------------------------- captions
ASS = BR / 'bathory_rough_v3_captions.ass'
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
def ts(t): t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; cs = int(round(s * 100)); return f'{h}:{m:02d}:{cs // 100:02d}.{cs % 100:02d}'
def two_lines(ws):
    txt = ' '.join(ws)
    if len(txt) <= 24: return txt, True
    best = None
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:]); sc = max(len(a), len(b))
        if best is None or sc < best[0]: best = (sc, a + r'\N' + b)
    return best[1], best[0] <= 24
def cmd_captions():
    W = WD; cuts = [c[1] for c in CUTS[1:]]; segs, cur = [], []
    for w in W:
        if cur and (w['line'] != cur[-1]['line'] or any(cur[-1]['start'] < c - 0.05 and w['start'] >= c - 0.05 for c in cuts)): segs.append(cur); cur = []
        cur.append(w)
        if w['word'][-1] in '.?!;:': segs.append(cur); cur = []
    if cur: segs.append(cur)
    def fits(ch): return len(ch) <= 7 and two_lines([x['word'] for x in ch])[1]
    def split(ch):
        if fits(ch): return [ch]
        best = None
        for k in range(2 if len(ch) > 3 else 1, len(ch) - (1 if len(ch) <= 3 else 1)):
            A, B2 = ch[:k], ch[k:]; la = len(' '.join(x['word'] for x in A)); lb = len(' '.join(x['word'] for x in B2))
            sc = abs(la - lb) - (12 if A[-1]['word'][-1] == ',' else 0) + (30 if min(len(A), len(B2)) < 2 else 0)
            if best is None or sc < best[0]: best = (sc, k)
        k = best[1]; return split(ch[:k]) + split(ch[k:])
    chunks = [c for sg in segs for c in split(sg)]; lines = []; over = []
    for j, ch in enumerate(chunks):
        st = ch[0]['start']; en = ch[-1]['end'] + 0.25
        if j + 1 < len(chunks): en = min(max(en, ch[-1]['end'] + 0.05), chunks[j + 1][0]['start'])
        txt, ok = two_lines([x['word'] for x in ch])
        if not ok or len(ch) > 7: over.append(txt)
        lines.append((st, en, txt))
    joined = ' '.join(t.replace(r'\N', ' ') for _, _, t in lines); script = ' '.join(x['word'] for x in W); assert joined == script, 'caption text != VO words'
    with open(ASS, 'x') as f: f.write(ASS_HEAD + ''.join(f'Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{t}\n' for a, b, t in lines))
    json.dump(dict(n=len(lines), overlong=over, lines=lines), open(LOGS / 'captions.json', 'w'), indent=1, ensure_ascii=False); print(len(lines), 'chunks; overlong:', over)

# ------------------------------------------------------------------------------------------- final + sheet
FINAL = V3 / 'renders/bathory_rough_v3.mp4'; MIXWAV = SCR / 'audio/mix_v3_final.wav'
def cmd_final():
    cl = SCR / 'clips'; lst = SCR / 'concat.txt'; lst.write_text(''.join(f"file '{cl / (k + '.mp4')}'\n" for k, _, _, _ in CUTS))
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', str(MIXWAV),
           '-vf', f"subtitles={ASS}", '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30',
           '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{DUR:.3f}', str(FINAL)]
    subprocess.run(cmd, check=True); print(FINAL, md5(FINAL))
def cmd_sheet():
    out = BR / 'bathory_rough_v3_contact_sheet.jpg'; tiles = []
    for k, a, b, _ in CUTS:
        t = (a + b) / 2; p = SCR / f'sheet_{k}.png'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-ss', f'{t:.3f}', '-i', str(FINAL), '-frames:v', '1', str(p)], check=True)
        im = cv2.resize(cv2.imread(str(p)), (270, 480), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (270, 30), (0, 0, 0), -1); cv2.putText(im, f'{k}  {t:.1f}s', (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(im); p.unlink()
    cols = 8; rows = [np.hstack(tiles[r * cols:(r + 1) * cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r * cols:(r + 1) * cols]))) for r in range((len(tiles) + cols - 1) // cols)]
    assert not out.exists(); cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88]); print(out)

if __name__ == '__main__' and len(sys.argv) > 1:
    a = sys.argv
    if a[1] == 'still': cmd_still(a[2], a[3], a[4] if len(a) > 4 else None)
    elif a[1] == 'clip': cmd_clip(a[2])
    else: dict(plan=cmd_plan, proofs=cmd_proofs, captions=cmd_captions, final=cmd_final, sheet=cmd_sheet)[a[1]]()
