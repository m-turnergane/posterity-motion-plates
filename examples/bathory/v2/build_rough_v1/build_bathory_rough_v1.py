#!/workspace/mpvenv/bin/python
"""Bathory ROUGH v1 build (Atelier). Reads plates/engines read-only; writes only into build_rough_v1/ and renders/.
Engines imported read-only via importlib; depth/snow CACHE monkeypatched into build_rough_v1/cache/{depth,snow}.
Own ffmpeg writer with -n (never -y).  Usage:
  build.py still <beat> <t> [out.png]      build.py calib <beat>      build.py clip <beat>
  build.py captions | mix | final | sheet"""
import sys, json, math, re, subprocess, importlib.util, hashlib
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
cv2.setNumThreads(2)
ROOT = Path('/workspace/posterity'); V2 = ROOT / 'standalones/bathory/v2'; BR = V2 / 'build_rough_v1'; PL = V2 / 'plates'
SCR = BR / 'scratch'; SCR.mkdir(exist_ok=True)
FPS = 30; OW, OH = 1080, 1920
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, str(p)); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
FX = _load('fx_v1c_ro', ROOT / 'standalones/edward-ii/edit/fx_v1c.py')
DU = _load('dust_v1_ro', ROOT / 'engine-rnd/dust/dust_v1.py')
SM = _load('smoke_v2_ro', ROOT / 'engine-rnd/smoke/smoke_v2.py')
DP = _load('depth_v1_ro', ROOT / 'engine-rnd/depth/depth_v1.py')
SN = _load('snow_v1b_ro', ROOT / 'engine-rnd/snow/snow_v1b.py')
DP.CACHE = BR / 'cache/depth'; SN.CACHE = BR / 'cache/snow'      # never write into engine dirs
FX.SPECS = {}; FX.PULSE = {}                                       # our own per-beat specs (keys = plate filename prefix)

# ----------------------------------------------------------------------------------------------- timeline (s)
CUTS = [('b01a', 0.0, 3.03), ('b01b', 3.03, 4.99), ('b02', 4.99, 7.60), ('b03', 7.60, 9.45), ('b04', 9.45, 12.08),
        ('b05', 12.08, 14.28), ('b06', 14.28, 18.94), ('b07', 18.94, 23.73), ('b08', 23.73, 29.77), ('b09', 29.77, 31.89),
        ('b10', 31.89, 37.21), ('b11', 37.21, 41.12), ('b12', 41.12, 44.40), ('b13a', 44.40, 1388 / 30), ('b13b', 1388 / 30, 49.0),
        ('b14', 49.0, 50.77), ('b15', 50.77, 56.15), ('b16', 56.15, 61.63), ('b17', 61.63, 66.28), ('b18', 66.28, 68.58),
        ('b19a', 68.58, 70.89), ('b19b', 70.89, 73.43), ('b20', 73.43, 79.60), ('outro', 79.60, 87.0)]
def frames_of(key):
    for k, a, b in CUTS:
        if k == key: return int(round(a * FPS)), int(round(b * FPS))
TOTAL_F = int(round(CUTS[-1][2] * FPS))

# ----------------------------------------------------------------------------------------------- helpers
def load_rgb(p): a = cv2.imread(str(p), cv2.IMREAD_COLOR); assert a is not None, p; return cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
def luma(a): return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def R(x0, y0, x1, y1): return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
def frac(polys, W, H): return [[[x / W, y / H] for x, y in p] for p in polys]
def writer(path):
    cmd = ['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

def heraldry(P, polys, feather=26, desat=0.7, dark=0.6, soften=2.4):
    """Soft painterly knock-back of heraldry: feathered mask, desaturate, darken, soften detail (no hard edges)."""
    H, W = P.shape[:2]; m = np.zeros((H, W), np.float32)
    for p in polys: cv2.fillPoly(m, [np.int32(p)], 1.0)
    m = cv2.GaussianBlur(m, (0, 0), feather)
    Pf = P.astype(np.float32); g = luma(Pf)[..., None]
    d = (Pf * (1 - desat) + g * desat) * dark
    soft = cv2.GaussianBlur(d, (0, 0), soften); bl = cv2.bilateralFilter(d.astype(np.float32), 9, 30, 6)
    d = 0.5 * soft + 0.5 * bl
    return np.clip(Pf * (1 - m[..., None]) + d * m[..., None] + 0.5, 0, 255).astype(np.uint8), m

# ----------------------------------------------------------------------------------------------- per-beat config
WARM = (255, 214, 160); COOL = (214, 222, 236)
GREY_SMOKE = dict(color_dark=[44, 46, 52], color_light=[108, 110, 118], glow=None)
def motes(n, amp, rect=None, color=WARM, sigma=(0.9, 2.8), speed=(3, 11), d=(-0.3, -0.4), jit=60, **k):
    L = dict(type='motes', zone=0, n=n, sigma=list(sigma), speed=list(speed), dir=list(d), dir_jitter_deg=jit, turb_px=6,
             turb_hz=[0.07, 0.3], life_s=[5, 12], amp=amp, near_gain=1.8, depth_power=2.0, pre_roll=40, color=list(color)); L.update(k); return L
def zone(poly, lo=40, hi=180, feather=40, blur=8, gamma=0.8):
    return dict(type='shaft', poly=poly, feather=feather, lum_lo=lo, lum_hi=hi, lum_blur=blur, lum_gamma=gamma)

B = {}
# B01a FLAT (judgment: thin sword + brazier flames cross any layer boundary; 3 s opener). torch on the left brazier + subtle dust
B['b01a'] = dict(plate='b01a_bytca_led_away.png', center=(0.45, 0.45),
    fx=[dict(torch=[(0, 870, 215, 1360)], relight_exclude=[(40, 380, 160, 560), (330, 540, 520, 720), (190, 520, 290, 640),
         (520, 380, 630, 520), (680, 340, 860, 520)], spill_amp=1.6, _kind='torch')],
    dust=dict(zones=[zone([[300, 0], [941, 0], [941, 1100], [700, 1300], [300, 1000]], lo=60, hi=200)],
              protect=[R(330, 520, 560, 760), R(520, 350, 650, 540), R(660, 330, 880, 560), R(0, 380, 180, 580), R(180, 500, 300, 660)],
              layers=[motes(380, 70, color=COOL, d=(0.2, 0.6), speed=(4, 12))]))
# B01b FLAT: candle left 26-36 % height (lock) + candle wisp <=0.4; heraldry: top-right tapestry
B['b01b'] = dict(plate='b01b_never_tried.png', center=(0.4, 0.4), her=[R(770, 0, 941, 480)],
    fx=[dict(manual=[(72, 405, 122, 530)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[97, 420], height=260, lean=-6, seed=1, opacity=0.35)],
               protect=[R(400, 230, 600, 520)]))
B['b02'] = dict(kind='archival', center=(0.5, 0.42))
B['b03'] = dict(kind='map', center=(0.5, 0.45))
# B04 DEPTH: hajdu + torch near, manor far
B['b04'] = dict(plate='b04_riders_at_the_manor.png', kind='depth',
    depth=dict(matte=dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6),
        camera=dict(push=[1.0, 1.06], anchor=[0.7, 0.4], travel=0.03, dir=[-1, 0], pivot=0.5, ease=dict(ramp_in=0.5, ramp_out=0.6, v_end=0.35)),
        near=dict(depth_min=0.55, region=[R(0, 450, 730, 1460)], polys=[R(0, 1400, 941, 1672)], seams=[[[0, 1380], [375, 1380], [375, 1520], [0, 1520]], [[460, 1380], [941, 1380], [941, 1520], [460, 1520]]]),
        far_gain=0.4),
    fx=[dict(torch=[(250, 545, 345, 735)], window=[(430, 580, 478, 632), (560, 570, 606, 622), (720, 548, 768, 598), (560, 710, 606, 760),
         (890, 555, 941, 606), (720, 735, 768, 790)], window_amp=0.7,
         relight_exclude=[(130, 790, 235, 905), (400, 770, 505, 880), (540, 830, 640, 945)], spill_amp=1.6, _kind='torch')],
    smoke=dict(emitters=[dict(name='torch', type='torch', src=[296, 560], height=380, w0=8, w1=100, lean=-18, seed=1, opacity=0.4, **GREY_SMOKE)],
               protect=[R(130, 790, 235, 905), R(400, 770, 505, 880), R(540, 830, 640, 945)]))
# B05 FLAT: 3 candles lock + offscreen torch at the door edge (faces excluded, torch only) + candle wisp; heraldry tapestry
B['b05'] = dict(plate='b05_supper_manor.png', center=(0.72, 0.3), her=[R(0, 0, 345, 470)],
    fx=[dict(auto=[(40, 560, 270, 720)], spill_amp=1.6, _kind='candle'),
        dict(offscreen=[dict(xy=(860, 400), h=60, radius=420, kind='torch')], relight_exclude=[(360, 380, 580, 620)], spill_amp=1.4, _kind='torch')],
    smoke=dict(emitters=[dict(name='wick_mid', type='candle', src=[152, 600], height=240, lean=8, seed=1, opacity=0.3)], protect=[R(360, 380, 580, 620)]))
# B06 FLAT: dust in the low-sun band (air only)
B['b06'] = dict(plate='b06_rumours_village.png', center=(0.65, 0.45),
    dust=dict(zones=[zone([[120, 180], [941, 180], [941, 820], [700, 900], [600, 640], [120, 470]], lo=80, hi=220, feather=50)],
              protect=[R(0, 450, 640, 1350), R(540, 400, 941, 760)],
              layers=[motes(520, 110, color=(255, 222, 170), d=(0.5, -0.2), speed=(3, 10))]))
B['b07'] = dict(plate='b07_thurzo_ordered.png', center=(0.5, 0.3),
    fx=[dict(manual=[(78, 285, 122, 375)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[99, 292], height=260, lean=10, seed=2, opacity=0.35)], protect=[R(400, 290, 570, 520)]))
B['b08'] = dict(plate='b08_husbands_letter.png', center=(0.4, 0.45),
    fx=[dict(manual=[(272, 105, 325, 275)], spill_amp=1.6, _kind='candle')],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[298, 112], height=240, lean=-8, seed=3, opacity=0.35)], protect=[]))
# B09 DEPTH: her + candles + table near; doorway men + torches far
B['b09'] = dict(plate='b09_arrest.png', kind='depth',
    depth=dict(matte=dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6),
        camera=dict(push=[1.0, 1.06], anchor=[0.72, 0.28], travel=0.03, dir=[1, 0], pivot=0.5, ease=dict(ramp_in=0.5, ramp_out=0.5, v_end=0.35)),
        near=dict(depth_min=0.28, exclude=[R(790, 960, 941, 1360)]), far_gain=0.4),
    fx=[dict(auto=[(0, 640, 140, 840)], spill_amp=1.6, _kind='candle'),
        dict(torch=[(645, 330, 715, 445), (860, 285, 925, 400)], relight_exclude=[(150, 250, 400, 560), (630, 380, 720, 480), (740, 380, 830, 470), (840, 380, 930, 470)], spill_amp=1.5, _kind='torch')])
# B10 FLAT (owner redo): candle lock + dust in the window shaft
B['b10'] = dict(plate='b10_bytca_transfer.png', center=(0.55, 0.5),
    fx=[dict(manual=[(540, 1075, 592, 1180)], spill_amp=1.6, _kind='candle')],
    dust=dict(zones=[zone([[800, 90], [941, 90], [941, 420], [700, 900], [560, 900], [620, 500]], lo=50, hi=190, feather=50)],
              protect=[R(300, 400, 420, 590), R(690, 530, 820, 700), R(450, 240, 560, 370), R(50, 870, 200, 1060)],
              layers=[motes(260, 90, color=COOL, d=(-0.4, 0.5), speed=(3, 9))]))
# B11 DEPTH: carriers + bier near, arcade far; brazier torch; snow b11 (helper, near-layer matrix)
B['b11'] = dict(plate='b11_bytca_door_shut.png', kind='depth', snow='b11',
    depth=dict(matte=dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6),
        camera=dict(push=[1.0, 1.06], anchor=[0.55, 0.5], travel=0.025, dir=[1, 0], pivot=0.5, ease=dict(ramp_in=0.5, ramp_out=0.5, v_end=0.35)),
        near='FIG', far_gain=0.4),
    fx=[dict(torch=[(85, 985, 295, 1262)], relight_exclude='FACES', spill_amp=1.6, _kind='torch')])
B['b12'] = dict(plate='b12_taken_up_to_fortress.png', center=(0.5, 0.38), snow='b12',
    fx=[dict(torch='AUTO_B12', window=[(365, 225, 395, 270)], window_amp=0.7, radius_mult=0.5, spill_amp=1.4, _kind='torch')],
    smoke=dict(emitters='AUTO_B12', protect=[]))
B['b13a'] = dict(plate='b13a_doors_open.png', kind='depth',
    depth=dict(matte=dict(mode='poly', inpaint_radius=6),
        camera=dict(push=[1.0, 1.035], anchor=[0.65, 0.42], travel=0.03, dir=[1, 0], pivot=1.0, ease=dict(ramp_in=0.5, ramp_out=0.01, v_end=0.35)),
        near=dict(polys=[R(0, 0, 941, 1671)], exclude=[[[484, 145], [753, 145], [753, 1000], [484, 1000]]], seams=[R(484, 960, 753, 1010)], feather_px=2.0),
        far_gain=1.0),
    fx=[dict(auto=[(630, 520, 740, 660)], spill_amp=1.6, relight_poly=[[(484, 145), (753, 145), (753, 1300), (484, 1300)]], _kind='candle')])
B['b13b'] = dict(plate='b13b_doors_shut.png', kind='b13b')
B['b14'] = dict(plate='b14_why_window.png', center=(0.78, 0.3),
    dust=dict(zones=[zone([[560, 130], [714, 130], [714, 840], [690, 1250], [560, 1250]], lo=40, hi=170, feather=40)],
              protect=[R(330, 280, 490, 570)], layers=[motes(300, 120, color=COOL, d=(-0.3, 0.4), speed=(3, 9))]))
B['b15'] = dict(plate='b15_thurzo_depositions.png', center=(0.45, 0.55), her=[R(0, 0, 300, 590)],
    fx=[dict(manual=[(38, 690, 102, 845)], spill_amp=1.6, _kind='candle')])
B['b16'] = dict(plate='b16_family_silence.png', center=(0.5, 0.3),
    fx=[dict(torch=[(340, 330, 690, 620)], relight_exclude=[(50, 420, 230, 580), (465, 505, 610, 670), (725, 390, 915, 580)], spill_amp=1.6, _kind='torch')],
    smoke=dict(emitters=[dict(name='hearth', type='torch', src=[515, 420], height=170, w0=30, w1=160, lean=0, seed=4, opacity=0.35, **GREY_SMOKE)],
               protect=[R(0, 0, 941, 300), R(0, 0, 330, 1672), R(700, 0, 941, 1672), R(0, 630, 941, 1672), R(50, 420, 230, 580), R(465, 505, 610, 670), R(725, 390, 915, 580)]))
B['b17'] = dict(plate='b17_secondhand_witnesses.png', center=(0.4, 0.4), snow='b17', her=[R(95, 60, 335, 285), R(85, 430, 170, 570)],
    fx=[dict(torch=[(50, 840, 235, 1120)], relight_exclude=[(430, 520, 941, 1080), (60, 560, 260, 720)], spill_amp=1.5, _kind='torch')],
    smoke=dict(emitters=[dict(name='brazier', type='torch', src=[135, 860], height=420, w0=18, w1=140, lean=12, seed=5, opacity=0.4, **GREY_SMOKE)],
               protect=[R(430, 520, 941, 1080), R(60, 560, 260, 720)]))
B['b18'] = dict(plate='b18_empty_room.png', center=(0.72, 0.4), her=[R(25, 130, 205, 690)],
    smoke=dict(emitters=[dict(name='wick', type='candle', src=[692, 738], height=230, lean=-6, seed=6, opacity=0.35)], protect=[]),
    dust=dict(zones=[zone([[680, 200], [860, 200], [860, 800], [600, 1350], [380, 1350], [520, 700]], lo=50, hi=200, feather=50)],
              protect=[], layers=[motes(320, 110, color=COOL, d=(-0.3, 0.4), speed=(3, 9))]))
B['b19a'] = dict(plate='b11_bytca_door_shut.png', center=(0.4, 0.62), snow='b19a',
    fx=[dict(torch=[(85, 985, 295, 1262)], relight_exclude='FACES', spill_amp=1.6, _kind='torch')])
B['b19b'] = dict(kind='archival', center=(0.5, 0.36))
B['b20'] = dict(plate='b20_closing_eyes.png', kind='depth', half_pulse=True,
    depth=dict(matte=dict(mode='hybrid', guided_r=4, guided_eps=2e-3, inpaint_radius=6),
        camera=dict(push=[1.0, 1.06], anchor=[0.5, 0.35], travel=0.012, dir=[1, 0], pivot=0.5, ease=dict(ramp_in=0.5, ramp_out=1.2, v_end=0.2)),
        near=dict(depth_min=0.38), far_gain=0.4),
    fx=[dict(manual=[(45, 755, 118, 905)], spill_amp=1.6, _kind='candle')])
B['outro'] = dict(plate='outro_bathory_csejte_first_light_OWNER.png', center=(0.5, 0.55),
    dust=dict(zones=[zone([[0, 470], [941, 470], [941, 570], [400, 600], [150, 760], [0, 800]], lo=60, hi=230, feather=40)],
              protect=[R(163, 579, 908, 910), R(560, 560, 680, 680), R(0, 120, 941, 470)], layers=[motes(260, 80, color=(255, 236, 205), d=(0.4, -0.2), speed=(2, 7))]))
ORDER = [k for k, _, _ in CUTS]

# ----------------------------------------------------------------------------------------------- calibration (fx_candle / torch_v1c)
TARGET = dict(candle=dict(local=32.0, whole=15.0, step=6.0), torch=dict(local=30.0, whole=12.0, step=2.95))
LIMIT = dict(candle=dict(local=36.0, whole=15.0, step=6.0), torch=dict(local=45.0, whole=14.0, step=3.1))
def fx_metrics(inst, P, seconds=3.0):
    """p-p % of mean luma: whole frame, and local (annulus around each source, flames excluded); max per-frame step %."""
    H, W = P.shape[:2]; flame = np.zeros((H, W), np.uint8); loc = np.zeros((H, W), bool)
    for s in inst.srcs:
        if s.get('bb') is not None:
            x0, y0, x1, y1 = s['bb']; flame[max(0, y0 - 8):y1 + 8, max(0, x0 - 8):x1 + 8] = 1
    Y, X = np.ogrid[:H, :W]
    for s in inst.srcs:
        if s['kind'] == 'window': continue
        r = float(s['radius']); cy = s['base'] - s['h'] * 0.5
        d = np.sqrt((X - s['x']) ** 2 + (Y - cy) ** 2); loc |= (d < max(r * 0.6, 25)) & (d > s['h'] * 0.6)
    loc &= flame == 0; whole = flame == 0
    wl, ll = [], []
    for i in range(int(seconds * FPS)):
        f = luma(inst.render(i / FPS).astype(np.float32)); wl.append(f[whole].mean()); ll.append(f[loc].mean() if loc.any() else 0)
    wl, ll = np.array(wl), np.array(ll)
    pp = lambda v: float((v.max() - v.min()) / max(v.mean(), 1e-3) * 100)
    st = lambda v: float(np.abs(np.diff(v)).max() / max(v.mean(), 1e-3) * 100)
    return dict(whole=pp(wl), local=pp(ll), step=max(st(wl), st(ll)))
def calibrate(inst, P, kind, scale=1.0):
    FX.PULSE[inst.key] = 1.0; m1 = fx_metrics(inst, P)
    T = TARGET[kind]; r = min(T['local'] / max(m1['local'], 1e-3), T['whole'] / max(m1['whole'], 1e-3), T['step'] / max(m1['step'], 1e-3))
    pul = r
    for _ in range(6):      # halo term is not linear in pulse below 0.6: re-measure and correct
        FX.PULSE[inst.key] = pul; m = fx_metrics(inst, P); L = LIMIT[kind]
        over = max(m['whole'] / L['whole'], m['step'] / L['step'], m['local'] / L['local'])
        under = m['local'] / T['local']
        if over > 1.0: pul *= 0.95 / over
        elif under < 0.85 and kind == 'candle': pul *= min(1.0 / under, 0.95 / max(over, 1e-3))
        else: break
    pul *= scale; FX.PULSE[inst.key] = pul; m = fx_metrics(inst, P)
    return pul, m1, m

# ----------------------------------------------------------------------------------------------- snow overlay on OUR composite
def snow_overlay(sh, base_u8, A, t):
    w, h = sh.out_wh; out = base_u8.astype(np.float32)
    col = sh.warp(sh.col, A); prot = sh.warp(sh.protect.astype(np.uint8), A, cv2.INTER_NEAREST) > 0; info = {}
    for L in sh.tiers:
        Ms = sh.warp(L['M'], A); x, y, env = sh.positions(L, t)
        xi = np.clip(np.round(x).astype(int), 0, w - 1); yi = np.clip(np.round(y).astype(int), 0, h - 1)
        ins = (x > -L['mg']) & (x < w + L['mg']) & (y > -L['mg']) & (y < h + L['mg'])
        peak = L['op'] * env * ins
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
    o = np.clip(out + 0.5, 0, 255).astype(np.uint8); o[prot] = base_u8[prot]
    return o, info

def snow_shot(key):
    if key == 'b19a':
        cfg = SN.get_cfg('b11'); cfg = dict(cfg); cfg['seed'] = 1912; cfg['name'] = 'b19a_snow_from_b11'
    else: cfg = dict(SN.get_cfg(key))
    return SnowShot_safe(cfg)
def SnowShot_safe(cfg): return SN.SnowShot(cfg, '1080x1920', FPS)

# ----------------------------------------------------------------------------------------------- B03 map
FONT_SC = '/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf'
FONT_IT = '/usr/share/fonts/truetype/sand-box/google/IM Fell French Canon/IMFellFrenchCanon-Italic.ttf'
LINK = (52, 30, 20); LHALO = (238, 226, 194)
def text_mask(t, f):
    l, tp, r, b = f.getbbox(t); im = Image.new('L', (r - l + 8, b - tp + 8), 0); ImageDraw.Draw(im).text((4 - l, 4 - tp), t, font=f, fill=255); return im
def comp_label(img, m, xy, alpha):
    a = Image.new('L', img.size, 0); a.paste(m, xy)
    halo = a.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(2.0)).point(lambda v: int(min(255, v * 1.4) * 0.8 * alpha))
    img.paste(Image.new('RGB', img.size, LHALO), (0, 0), halo); img.paste(Image.new('RGB', img.size, LINK), (0, 0), a.point(lambda v: int(v * alpha)))
def slow_noise(rng, n, period):
    k = max(2, int(n / period) + 3); ctrl = rng.normal(0, 1, k); x = np.linspace(0, k - 1, n)
    v = np.interp(x, np.arange(k), ctrl); v = np.convolve(v, np.ones(9) / 9, mode='same'); return v / (np.abs(v).max() + 1e-6)
SS = 4
class Canvas:
    def __init__(s, H, W): s.H, s.W = H, W; s.m = np.zeros((H * SS, W * SS), np.uint8)
    def stamp(s, pts, widths):
        for (x, y), w in zip(pts, widths):
            r = max(0.5, w * 0.5 * SS); cv2.circle(s.m, (int(round(x * SS * 16)), int(round(y * SS * 16))), int(round(r * 16)), 255, -1, cv2.LINE_8, shift=4)
    def alpha(s): return cv2.resize(s.m, (s.W, s.H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
def ring(cv, c, rc, wr, rng, step=0.25):
    n = int(2 * math.pi * rc / step) + 2; th = np.linspace(0, 2 * math.pi, n) - 1.7 + rng.uniform(-0.3, 0.3)
    rr = rc * (1 + 0.025 * slow_noise(rng, n, n / 3)); P = np.stack([c[0] + rr * np.cos(th), c[1] + rr * np.sin(th)], -1)
    w = wr * (1 + 0.2 * slow_noise(rng, n, n / 4)); w = np.clip(w, 0.8 * wr, 1.2 * wr); cv.stamp(P, w)
class MapB03:
    PINS = dict(csejte=(130.7, 1065.2), bytca=(871.4, 365.8)); T_ON = dict(csejte=0.15, bytca=0.55); STAMP_DUR = 0.45
    def __init__(self):
        base = load_rgb(BR / 'b03/b03_registered_1080x1920.png'); assert base.shape[:2] == (1920, 1080)
        lay = json.load(open(ROOT / 'engine-rnd/maps/atlas/refpack_bathory/label_plan_v2b/label_layout_v2b.json'))
        # Vah thinning under the Csejte label zone: river pixels (blue-ish) blended 60% toward an inpaint
        x0, y0, x1, y1 = 105, 1076, 842, 1163; B = base.astype(np.int16)
        riv = np.zeros(base.shape[:2], np.uint8); sub = B[y0:y1, x0:x1]
        riv[y0:y1, x0:x1] = ((sub[..., 2] - sub[..., 0]) > 8).astype(np.uint8)
        riv = cv2.dilate(riv, np.ones((3, 3), np.uint8)); self.river_px = int(riv.sum())
        inp = cv2.inpaint(base, riv * 255, 5, cv2.INPAINT_TELEA)
        m = cv2.GaussianBlur(riv.astype(np.float32), (0, 0), 1.0)[..., None] * 0.6
        base = np.clip(base * (1 - m) + inp * m + 0.5, 0, 255).astype(np.uint8)
        img = Image.fromarray(base); fs = ImageFont.truetype(FONT_SC, lay['sizes_1080']['csejte']); fv = ImageFont.truetype(FONT_IT, lay['sizes_1080']['vah'])
        comp_label(img, text_mask('Csejte, today Čachtice, Slovakia', fs), tuple(lay['csejte']['origin']), 1.0)
        comp_label(img, text_mask('Bytča', ImageFont.truetype(FONT_SC, lay['sizes_1080']['bytca'])), tuple(lay['bytca']['origin']), 1.0)
        mv = text_mask('Váh', fv).rotate(lay['vah']['angle'], expand=True, resample=Image.BICUBIC)
        a = np.array(mv) > 10; ys, xs = np.nonzero(a); bb = lay['vah']['bbox']
        comp_label(img, mv, (int(bb[0] - (xs.min() - 3)), int(bb[1] - (ys.min() - 3))), 0.60)
        self.labeled = np.asarray(img).astype(np.float32)
        # stamp alphas (final), each scaled/faded in
        self.st = {}
        for i, (k, c) in enumerate(self.PINS.items()):
            cv = Canvas(1920, 1080); ring(cv, c, 18, 4.4, np.random.default_rng([3, 300 + i])); cv.stamp([c], [18 * 0.9])
            al = cv.alpha(); core = cv2.GaussianBlur(al, (0, 0), 0.7); bleed = cv2.GaussianBlur(al, (0, 0), 2.0) * 0.15
            g = cv2.GaussianBlur(np.random.default_rng(40 + i).standard_normal(al.shape).astype(np.float32), (0, 0), 1.2); g = 1 + 0.14 * g / (g.std() + 1e-6)
            ink = np.clip(core ** 0.9 * 0.96 * g + bleed, 0, 0.97)
            kh = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)); halo = cv2.GaussianBlur(cv2.dilate(al, kh), (0, 0), 0.9) * 0.60
            self.st[k] = (c, ink.astype(np.float32), halo.astype(np.float32))
    def plate_at(self, t):
        img = self.labeled.copy()
        for k, (c, ink, halo) in self.st.items():
            u = np.clip((t - self.T_ON[k]) / self.STAMP_DUR, 0, 1)
            if u <= 0: continue
            e = 1 - (1 - u) ** 3; sc = 1.35 - 0.35 * e; op = min(1.0, u * 1.6)
            M = np.float32([[sc, 0, c[0] * (1 - sc)], [0, sc, c[1] * (1 - sc)]])
            ik = cv2.warpAffine(ink, M, (1080, 1920)) * op; hl = cv2.warpAffine(halo, M, (1080, 1920)) * op
            img = img * (1 - hl[..., None]) + np.float32([22, 16, 14]) * hl[..., None]
            img = img * (1 - ik[..., None]) + np.float32([34, 28, 30]) * ik[..., None] * (0.92 + 0.08 * img / 200.0)
        return np.clip(img + 0.5, 0, 255).astype(np.uint8)

# ----------------------------------------------------------------------------------------------- beat renderer
MOD = SCR / 'plates_mod'; MOD.mkdir(exist_ok=True)
def warp_out(img, A): return cv2.warpAffine(img, A, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
def to_frac_layer(d, W, H):
    o = {}
    for k, v in d.items():
        o[k] = frac(v, W, H) if k in ('region', 'polys', 'exclude', 'seams') else v
    return o

class Beat:
    def __init__(self, key, calib=True):
        self.key = key; c = B[key]; self.c = c; self.kind = c.get('kind', 'flat'); f0, f1 = frames_of(key); self.f0, self.n = f0, f1 - f0
        self.log = dict(beat=key, kind=self.kind, frames=[f0, f1], seconds=round(self.n / FPS, 3)); self.fx = []; self.dust = None; self.smoke = None; self.snow = None
        if self.kind == 'archival':
            self.P = load_rgb(BR / 'assets/b02_bathory_erzsebet_2_commons.jpg'); H, W = self.P.shape[:2]
            self.log['density_max'] = round(max(OW / W, OH / H) * 1.06, 3); return
        if self.kind == 'map':
            self.map = MapB03(); self.log['vah_thinned_px'] = self.map.river_px; self.log['density_max'] = round(1080 / 941 * 1.06, 3); return
        path = PL / c['plate']; P = load_rgb(path); pk = c['plate'].split('_')[0]; H, W = P.shape[:2]; self.W, self.H = W, H
        if c.get('her'):
            P, m = heraldry(P, c['her']); path = MOD / f'{pk}_her_{key}.png'
            if not path.exists(): cv2.imwrite(str(path), cv2.cvtColor(P, cv2.COLOR_RGB2BGR))
            self.log['heraldry_polys'] = c['her']; self.log['heraldry_mean_mask'] = round(float(m.mean()), 4)
        self.path = path; self.P = P; self.Pf = P.astype(np.float32)
        if c.get('snow'): self.snow = snow_shot(c['snow']); self.log['snow_cfg'] = c['snow']
        for j, spec in enumerate(c.get('fx', [])):
            spec = dict(spec); kind = spec.pop('_kind')
            if spec.get('relight_exclude') == 'FACES':
                fb = self.snow.face_boxes if self.snow else []; spec['relight_exclude'] = [tuple(b) for b in fb]; self.log['faces_from_snow_detector'] = fb
            if spec.get('torch') == 'AUTO_B12': spec['torch'] = self.b12_torches()
            FX.SPECS[pk] = spec; inst = FX.PlateFX(str(path), seed=j); inst.key = f'{key}#{j}'
            self.log.setdefault('fx', []).append(dict(kind=kind, info=inst.info(), spec={k: v for k, v in spec.items()}))
            if calib:
                pul, m1, m = calibrate(inst, P, kind, 0.5 if c.get('half_pulse') else 1.0)
                self.log['fx'][-1].update(pulse=round(pul, 4), metrics_at_pulse1=m1, metrics=m)
            self.fx.append(inst)
        if c.get('dust'):
            d = c['dust']; cfg = dict(plate=str(path), seed=hash(key) % 1000, protect_feather=12, zones=d['zones'], protect=d.get('protect', []), layers=d['layers'])
            self.dust = DU.DustShot(cfg); self.log['dust'] = dict(n=[L['n'] for L in d['layers']], amp=[L['amp'] for L in d['layers']])
        if c.get('smoke'):
            s = c['smoke']; em = self.b12_smoke() if s['emitters'] == 'AUTO_B12' else s['emitters']
            cfg = dict(seed=7, protect=s.get('protect', []), protect_feather=36, flame_keepout=0.0, preroll=8.0, emitters=em, billows=[], fires=[])
            self.smoke = SM.SmokeScene(SM.load_plate(str(path)), cfg); self.log['smoke'] = [dict(name=e['name'], type=e['type'], opacity=e['opacity']) for e in em]
        if self.kind == 'depth': self._depth()
        if self.kind == 'b13b': self._b13b()
        if self.kind == 'flat': self.log['density_max'] = round(max(OW / W, OH / H) * 1.06, 3)

    # B12: find the 4 torch flames as local maxima of warm brightness in the switchback band
    def b12_torches(self):
        P = self.P.astype(np.float32); x0, y0, x1, y1 = 330, 560, 640, 770
        sc = luma(P[y0:y1, x0:x1]) + 0.8 * np.clip(P[y0:y1, x0:x1, 0] - P[y0:y1, x0:x1, 2], 0, 255)
        sc = cv2.GaussianBlur(sc, (0, 0), 3); pts = []
        for _ in range(4):
            yy, xx = np.unravel_index(np.argmax(sc), sc.shape); pts.append((x0 + xx, y0 + yy)); sc[max(0, yy - 30):yy + 30, max(0, xx - 30):xx + 30] = -1e9
        self.b12_pts = sorted(pts); self.log['b12_torch_pts'] = [list(map(int, p)) for p in self.b12_pts]
        return [(int(x - 22), int(y - 30), int(x + 22), int(y + 22)) for x, y in self.b12_pts]
    def b12_smoke(self):
        return [dict(name=f't{i}', type='torch', src=[int(x), int(y - 18)], height=150, w0=4, w1=45, lean=-10, seed=10 + i, opacity=0.35, **GREY_SMOKE)
                for i, (x, y) in enumerate(self.b12_pts)]

    def _depth_cfg(self):
        c = self.c['depth']; W, H = self.W, self.H; near = c['near']
        if near == 'FIG': near = self.b11_near()
        layers = [dict(name='far', parallax=0.0, push_gain=c['far_gain']), dict(name='near', parallax=1.0, push_gain=1.0, **to_frac_layer(near, W, H))]
        return dict(name=f'{self.key}_rough_v1', plate=str(self.path), matte=c['matte'], camera=c['camera'], layers=layers)
    def b11_near(self):
        return dict(depth_min=0.18, region=[[[60, 520], [880, 520], [880, 1300], [60, 1300]]], polys=[R(0, 1230, 941, 1672)],
                    seams=[R(0, 1180, 941, 1262)], seam_feather_px=22)
    def _depth(self):
        cfg = self._depth_cfg(); self.dcfg = cfg; self.ds = DP.DepthShot(cfg); size = (OW, OH)
        self.o = self.ds.overscan(size, self.n); self.E = DP.smooth_progress(self.n, fps=FPS, **cfg['camera'].get('ease', {}))
        g = self.ds.guard(size, n=self.n); s, _, cz = self.ds.out_frame(size)
        zmax = max(self.ds.layer_params(k, e)[0] for k in range(2) for e in (0.0, 1.0)) * self.o
        self.log.update(depth_info=self.ds.info(), overscan=round(self.o, 4), guard=g, density_max=round(s * zmax, 3))
    def _b13b(self):
        A = Beat('b13a', calib=False); M = A.ds.layer_affine(1, A.E[-1], (OW, OH), A.o); ax, ay = A.ds.anchor()
        self.MA = M; self.aout = (M[0, 0] * ax + M[0, 2], M[1, 1] * ay + M[1, 2]); self.SA = float(M[0, 0]); self.zA = A.dcfg['camera']['push'][1]
        reg = json.load(open(BR / 'b13/b13_registration.json'))['ecc_b_to_a']['translation']['warp']; self.d = (reg[0][2], reg[1][2])
        # verify the sign of the registration shift numerically on the cut frames (outside the door leaves)
        fa = A.render_frame(A.n - 1).astype(np.float32); best = None
        for sg in (1, -1, 0):
            self.sg = sg; fb = self.render_frame(0).astype(np.float32); m = np.ones((OH, OW), bool)
            Mi = M; pts = np.float32([[440, 120], [800, 120], [800, 1100], [440, 1100]]) @ Mi[:, :2].T + Mi[:, 2]
            x0, y0 = pts.min(0).astype(int); x1, y1 = pts.max(0).astype(int); m[max(0, y0):y1, max(0, x0):x1] = False
            err = float(np.abs(luma(fa) - luma(fb))[m].mean()); best = (err, sg) if best is None or err < best[0] else best
            self.log.setdefault('b13_cut_diff', {})[str(sg)] = round(err, 3)
        self.sg = best[1]; self.log['b13_reg_sign'] = self.sg; self.log['b13_reg_shift_plate_px'] = [round(v * self.sg, 3) for v in self.d]
        self.log['b13_reg_shift_output_px'] = [round(v * self.sg * self.SA, 3) for v in self.d]; self.log['density_max'] = round(self.SA / self.zA * 1.06, 3)

    def plate_comp(self, t):
        if not (self.fx or self.dust or self.smoke): return self.P
        acc = self.Pf.copy()
        for inst in self.fx: acc += inst.render(t).astype(np.float32) - self.Pf
        if self.dust: acc += self.dust.frame(t).astype(np.float32) - self.Pf
        if self.smoke: acc += np.asarray(self.smoke.frame(t)).astype(np.float32) - self.Pf
        return np.clip(acc + 0.5, 0, 255).astype(np.uint8)

    def cam_flat(self, i):
        u = i / max(self.n - 1, 1)
        if self.kind == 'archival': H, W = self.P.shape[:2]
        elif self.kind == 'map': W, H = 1080, 1920
        else: W, H = self.W, self.H
        return SN.cam_matrix((W, H), (OW, OH), u, 1.0, 1.06, tuple(self.c['center']))

    def render_frame(self, i, info=None):
        t = i / FPS
        if self.kind == 'archival': return warp_out(self.P, self.cam_flat(i))
        if self.kind == 'map': return warp_out(self.map.plate_at(t), self.cam_flat(i))
        if self.kind == 'depth':
            if hasattr(DP, 'WARP_LOG'): DP.WARP_LOG.clear()
            out, lay = self.ds.frame(self.E[i], (OW, OH), self.o, fid=i, plate_fx=lambda tt: self.plate_comp(tt).astype(np.float32) / 255.0, t=t, return_layers=True)
            fr = (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8); A = lay[1][0]
        elif self.kind == 'b13b':
            u = i / max(self.n - 1, 1); z = self.zA + (1.06 - self.zA) * (1 - (1 - u) ** 2); S = self.SA * z / self.zA
            ax, ay = self.aout; ancx, ancy = (ax - self.MA[0, 2]) / self.SA, (ay - self.MA[1, 2]) / self.SA
            dx, dy = self.d[0] * self.sg, self.d[1] * self.sg
            A = np.float32([[S, 0, ax - S * ancx + S * dx], [0, S, ay - S * ancy + S * dy]])
            fr = warp_out(self.plate_comp(t), A)
        else:
            A = self.cam_flat(i); fr = warp_out(self.plate_comp(t), A)
        if self.snow is not None:
            fr, inf = snow_overlay(self.snow, fr, A, t)
            if info is not None: info.append(inf)
        return fr

def cmd_still(key, t, out=None):
    b = Beat(key, calib='--nocal' not in sys.argv); i = min(int(round(float(t) * FPS)), b.n - 1); inf = []
    fr = b.render_frame(i, inf); out = out or str(SCR / f'still_{key}_{i:03d}.png')
    cv2.imwrite(out, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR)); print(json.dumps(dict(b.log, snow_vis=inf), default=str)[:3000]); print(out)

def cmd_clip(key):
    cl = SCR / 'clips'; cl.mkdir(exist_ok=True); out = cl / f'{key}.mp4'; lg = cl / f'{key}.json'
    if out.exists(): print('exists', out); return
    b = Beat(key); p = writer(out); vis = []
    for i in range(b.n):
        inf = []; fr = b.render_frame(i, inf); p.stdin.write(fr.tobytes())
        if inf: vis.append(inf[0])
        if i in (0, b.n // 2, b.n - 1): cv2.imwrite(str(cl / f'{key}_f{i:03d}.png'), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
    p.stdin.close(); assert p.wait() == 0
    if vis:
        tot = [sum(v for k, v in d.items() if not k.startswith('_')) for d in vis]
        b.log['snow_visible_flakes_per_frame'] = dict(min=int(min(tot)), mean=round(float(np.mean(tot)), 1), max=int(max(tot)),
                                                       per_tier_mean={k: round(float(np.mean([d[k] for d in vis])), 1) for k in vis[0] if not k.startswith('_')})
    json.dump(b.log, open(lg, 'w'), indent=1, default=str); print('done', key, b.n)


# ----------------------------------------------------------------------------------------------- captions
VO = BR / 'vo/final-vo-oliver-bathory-rough-v1.wav'; WORDS = BR / 'vo/final-vo-oliver-bathory-rough-v1_words.json'
ASS = BR / 'bathory_rough_v1_captions.ass'
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
    W = json.load(open(WORDS))['words']; cuts = [c[1] for c in CUTS[1:]]
    # 1) segments: sentence punctuation, VO line changes and picture cuts are hard breaks
    segs, cur = [], []
    for w in W:
        if cur and (w['line'] != cur[-1]['line'] or any(cur[-1]['start'] < c - 0.1 and w['start'] >= c - 0.1 for c in cuts)):
            segs.append(cur); cur = []
        cur.append(w)
        if w['word'][-1] in '.?!;:': segs.append(cur); cur = []
    if cur: segs.append(cur)
    # 2) balanced recursive split until each chunk is <=7 words and fits two lines of <=24 chars
    def fits(ch): return len(ch) <= 7 and two_lines([x['word'] for x in ch])[1]
    def split(ch):
        if fits(ch): return [ch]
        best = None
        for k in range(2 if len(ch) > 3 else 1, len(ch) - (1 if len(ch) <= 3 else 1)):
            A, B2 = ch[:k], ch[k:]; la = len(' '.join(x['word'] for x in A)); lb = len(' '.join(x['word'] for x in B2))
            sc = abs(la - lb) - (12 if A[-1]['word'][-1] == ',' else 0) + (30 if min(len(A), len(B2)) < 2 else 0)
            if best is None or sc < best[0]: best = (sc, k)
        k = best[1]; return split(ch[:k]) + split(ch[k:])
    chunks = [c for sg in segs for c in split(sg)]
    # never leave a single-word orphan when it can join the previous chunk
    lines = []; over = []
    for j, ch in enumerate(chunks):
        st = ch[0]['start']; en = ch[-1]['end'] + 0.25
        if j + 1 < len(chunks): en = min(max(en, ch[-1]['end'] + 0.05), chunks[j + 1][0]['start'])
        txt, ok = two_lines([x['word'] for x in ch])
        if not ok: over.append(txt)
        lines.append((st, en, txt))
    joined = ' '.join(t.replace(r'\N', ' ') for _, _, t in lines)
    script = ' '.join(x['word'] for x in W); assert joined == script, 'caption text != VO words'
    with open(ASS, 'x') as f:
        f.write(ASS_HEAD + ''.join(f'Dialogue: 0,{ts(a)},{ts(b)},Default,,0,0,0,,{t}\n' for a, b, t in lines))
    print(len(lines), 'chunks; overlong:', over); return lines

# ----------------------------------------------------------------------------------------------- F7 door impact (synth) + mix
SR = 48000; T_IMPACT = CUTS[[c[0] for c in CUTS].index('b13b')][1]; BED_SS = 31.0; DUR = CUTS[-1][2]
def synth_f7(path):
    rng = np.random.default_rng(77); pre = 0.42; n = int((pre + 2.6) * SR); t = np.arange(n) / SR; y = np.zeros(n)
    # pre-swing: low airy whoosh + faint hinge groan rising into the impact
    sw = rng.standard_normal(n); sw = np.convolve(sw, np.ones(60) / 60, 'same'); env = np.clip(t / pre, 0, 1) ** 2.2 * (t < pre)
    y += sw * env * 0.25
    tg = t[t < pre]; y[:len(tg)] += 0.05 * np.sin(2 * np.pi * (90 + 60 * tg / pre) * tg) * (tg / pre) ** 3
    ti = t - pre; m = ti >= 0; tt = ti[m]
    body = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 9) + 0.6 * np.sin(2 * np.pi * 78 * tt + 0.4) * np.exp(-tt * 13) + 0.35 * np.sin(2 * np.pi * 131 * tt) * np.exp(-tt * 22)
    knock = rng.standard_normal(m.sum()); knock = np.convolve(knock, np.ones(10) / 10, 'same') * np.exp(-tt * 60) * 0.9
    latch = rng.standard_normal(m.sum()) * np.exp(-np.maximum(tt - 0.11, 0) * 90) * (tt > 0.11) * 0.18
    y[m] += body + knock + latch
    att = np.clip(tt / 0.002, 0, 1); y[m] *= np.where(tt < 0.002, att, 1)
    # stone-room tail: sparse decaying echoes, lowpassed
    tail = np.zeros(n)
    for d, g in [(0.043, 0.35), (0.071, 0.3), (0.113, 0.24), (0.167, 0.18), (0.229, 0.13), (0.31, 0.09), (0.42, 0.06), (0.56, 0.04)]:
        k = int(d * SR); tail[k:] += y[:n - k] * g
    tail = np.convolve(tail, np.ones(24) / 24, 'same'); y = y + tail
    y = y / np.abs(y).max() * 0.89
    import wave
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
    return pre
def ebur(path, extra=''):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true' + extra, '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r); return I, float(tp[-1]) if tp else None
BED = ROOT / 'standalones/bathory/v2/score/candidates/macleod_ignosi.mp3'
FADE_T0, FADE_RATE = 83.2, 16.0   # constant dB/s outro fade: -60 dB at 86.95s
def render_mix(out, bed_db, f7_db, master_db, pre, f7):
    fc = (f"[0:a]aresample={SR},highpass=f=70,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,apad,atrim=0:{DUR},asplit=2[vo][sc];"
          f"[1:a]aresample={SR},atrim=0:{DUR},asetpts=N/SR/TB,afade=t=in:st=0:d=0.02,volume={bed_db}dB,"
          f"volume='if(lt(t,{FADE_T0}),1,pow(10,-{FADE_RATE}*(t-{FADE_T0})/20))':eval=frame[bed0];"
          f"[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bed];"
          f"[2:a]aresample={SR},volume={f7_db}dB,adelay={int(round((T_IMPACT - pre) * 1000))}:all=1,apad,atrim=0:{DUR}[fx];"
          f"[vo][bed][fx]amix=inputs=3:normalize=0:duration=first,volume={master_db}dB,alimiter=limit=0.74:attack=2:release=60:level=0,"
          f"aformat=sample_fmts=s16:channel_layouts=stereo")
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-ss', str(BED_SS), '-i', str(BED), '-i', str(f7), '-filter_complex', fc, '-ar', str(SR), str(out)]
    subprocess.run(cmd, check=True)
def stem(out, which, bed_db, pre, f7):
    if which == 'vo':
        fc = f"[0:a]aresample={SR},highpass=f=70,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,apad,atrim=0:{DUR}"
        cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-filter_complex', fc, str(out)]
    else:
        fc = (f"[0:a]aresample={SR},highpass=f=70,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,apad,atrim=0:{DUR}[sc];"
              f"[1:a]aresample={SR},atrim=0:{DUR},asetpts=N/SR/TB,afade=t=in:st=0:d=0.02,volume={bed_db}dB,"
              f"volume='if(lt(t,{FADE_T0}),1,pow(10,-{FADE_RATE}*(t-{FADE_T0})/20))':eval=frame[b0];[b0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4")
        cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-ss', str(BED_SS), '-i', str(BED), '-filter_complex', fc, str(out)]
    subprocess.run(cmd, check=True)
def cmd_mix():
    A = SCR / 'audio'; A.mkdir(exist_ok=True); f7 = A / 'f7_door_impact_synth.wav'; pre = synth_f7(f7) if not f7.exists() else 0.42
    Lvo, _ = ebur(stem(A / 'vo.wav', 'vo', 0, pre, f7) or A / 'vo.wav'); bed_db = -8.0; log = dict(vo_I=Lvo, iters=[])
    for it in range(4):
        p = A / f'bed_{it}.wav'; stem(p, 'bed', bed_db, pre, f7); Lb, _ = ebur(p); diff = Lvo - Lb; log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(diff, 2)))
        if 12.4 <= diff <= 13.6: break
        bed_db += diff - 13.0
    master = 0.0
    for it in range(5):
        p = A / f'mix_{it}.wav'; render_mix(p, bed_db, -4.0, master, pre, f7); I, tp = ebur(p); log.setdefault('master', []).append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I + 14.0) <= 0.3 and tp <= -1.0: break
        master += -14.0 - I
    log.update(final_mix=str(p), bed_db=bed_db, f7_impact_timeline_s=round(T_IMPACT, 3), f7_impact_track_s=round(T_IMPACT + BED_SS, 3), fade=dict(start=FADE_T0, dB_per_s=FADE_RATE))
    json.dump(log, open(A / 'mix_log.json', 'w'), indent=1); print(json.dumps(log, indent=1))

# ----------------------------------------------------------------------------------------------- final + contact sheet
FINAL = BR.parent / 'renders/bathory_rough_v1.mp4'
def cmd_final():
    cl = SCR / 'clips'; lst = SCR / 'concat.txt'
    lst.write_text(''.join(f"file '{cl / (k + '.mp4')}'\n" for k, _, _ in CUTS))
    mix = json.load(open(SCR / 'audio/mix_log.json'))['final_mix']; FINAL.parent.mkdir(exist_ok=True)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(lst), '-i', mix,
           '-vf', f"subtitles={ASS}", '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30',
           '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', '-t', f'{DUR:.3f}', str(FINAL)]
    subprocess.run(cmd, check=True); print(FINAL, md5(FINAL))
def cmd_sheet():
    out = BR / 'bathory_rough_v1_contact_sheet.jpg'; tiles = []
    for k, a, b in CUTS:
        t = (a + b) / 2; p = SCR / f'sheet_{k}.png'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-ss', f'{t:.3f}', '-i', str(FINAL), '-frames:v', '1', str(p)], check=True)
        im = cv2.resize(cv2.imread(str(p)), (270, 480), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (270, 30), (0, 0, 0), -1); cv2.putText(im, f'{k}  {t:.1f}s', (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA); tiles.append(im); p.unlink()
    cols = 8; rows = [np.hstack(tiles[r * cols:(r + 1) * cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r * cols:(r + 1) * cols]))) for r in range((len(tiles) + cols - 1) // cols)]
    assert not out.exists(); cv2.imwrite(str(out), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88]); print(out)

if __name__ == '__main__' and len(sys.argv) > 1:
    a = sys.argv
    if a[1] == 'still': cmd_still(a[2], a[3], a[4] if len(a) > 4 and not a[4].startswith('--') else None)
    elif a[1] == 'clip': cmd_clip(a[2])
    else: dict(captions=cmd_captions, mix=cmd_mix, final=cmd_final, sheet=cmd_sheet)[a[1]]()
