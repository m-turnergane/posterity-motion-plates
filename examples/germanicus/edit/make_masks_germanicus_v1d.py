# Germanicus ROUGH v1d -- 7B candle config on owner plate seq7b-v2.png (941x1672, native, no crop). Never overwrites, never deletes.
#  flame mask   : lamp flame only (teardrop around wick base (167,266), ~20x68 px) feathered 2 px  -> plate_flame / flame_warp (bbox << 64 px engine limit)
#  STILL zone   : blade + blood on blade + 2 drips + floor pool, Piso's hand/arm/drapery/couch (hand/body) -> relight mask hard 0 there (+8 px), soft ramp beyond
#  relight      : exp(-d^2/R^2) falloff from the flame (lamp, table, wall, left floor) x (1 - still ramp), feather ~30 px
#  protect      : everything except the dilated flame zone (zero displacement outside the flame)
#  halo sigma capped so the unmasked gauss_dot (3 sigma) never reaches the still zone (asserted).
import json, sys, copy, math
from pathlib import Path
import numpy as np, cv2
G = Path('/workspace/posterity/standalones/germanicus'); PLATE = G / 'plates-owner/seq7b-v2.png'
BASE = G / 'masks/v1d'; CFG = G / 'motion/configs'; LOCKED = Path('/workspace/posterity/motion/presets/locked/house-candle-lightspill-v1.json')
W, H = 941, 1672
BX, BY = 167.0, 266.0          # wick / flame base
FW, FH = 20.0, 68.0            # flame size (px)

def safe_img(p, m):
    if Path(p).exists(): raise SystemExit(f'refusing overwrite {p}')
    cv2.imwrite(str(p), np.clip(np.rint(m), 0, 255).astype(np.uint8))

def still_zone():
    m = np.zeros((H, W), np.uint8)
    # blade (pommel 380,775 -> tip 556,1235) incl. guard + blood on blade
    cv2.line(m, (392, 790), (552, 1232), 255, 64)
    cv2.circle(m, (395, 785), 34, 255, -1)
    cv2.line(m, (400, 950), (505, 920), 255, 40)          # guard
    # drips + floor pool
    cv2.ellipse(m, (553, 1250), (12, 22), 0, 0, 360, 255, -1)
    cv2.ellipse(m, (553, 1300), (12, 24), 0, 0, 360, 255, -1)
    cv2.ellipse(m, (543, 1360), (12, 22), 0, 0, 360, 255, -1)
    cv2.ellipse(m, (530, 1393), (92, 28), 0, 0, 360, 255, -1)
    # hand / arm / drapery / couch (Piso): everything right of the couch's left edge, plus the hanging hand
    body = np.array([(395, 300), (430, 180), (520, 110), (700, 40), (941, 0), (941, 1672), (941, 1290), (600, 1260), (560, 1210),
                     (560, 760), (540, 770), (500, 760), (440, 760), (395, 700), (385, 620)], np.int32)
    cv2.fillPoly(m, [body], 255)
    return m > 0

def build():
    for d in (BASE, CFG): d.mkdir(parents=True, exist_ok=True)
    im = cv2.imread(str(PLATE)); assert im.shape[:2] == (H, W), im.shape
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    # flame: teardrop polygon x bright pixels (L>150), closed, feathered 2 px
    L = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    u = (BY + 2 - Y) / (FH + 6)                           # 0 at base -> 1 at tip
    half = (FW / 2 + 3) * np.clip(np.sqrt(np.clip(u, 0, 1)) * (1 - u) * 2.6, 0, 1.15)
    tear = (u >= -0.04) & (u <= 1.0) & (np.abs(X - BX) <= np.maximum(half, 3))
    fl = tear & (L > 150)
    fl = cv2.morphologyEx(fl.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)) > 0
    fm = cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 1.0) * 255; fm[~(cv2.dilate(fl.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0)] = 0
    x, y, w, h = cv2.boundingRect((fm > 0).astype(np.uint8)); assert w + 5 <= 64 and h <= 250, (x, y, w, h)
    st = still_zone()
    hard = cv2.dilate(st.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0               # +8 px hard zero
    soft = np.clip(cv2.GaussianBlur(cv2.dilate(st.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(np.float32), (0, 0), 14), 0, 1)
    R = 430.0; d2 = (X - BX) ** 2 + (Y - (BY - 30)) ** 2
    fall = np.exp(-d2 / R ** 2); fall[fall < 0.02] = 0; fall = cv2.GaussianBlur(fall, (0, 0), 6)
    rel = fall * (1 - soft); rel[hard] = 0; rel[st] = 0
    flz = cv2.dilate((fm > 0).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    prot = ~flz
    assert not (flz & hard).any()
    # still-zone distance to flame centre -> halo cap
    dist = cv2.distanceTransform((~hard).astype(np.uint8), cv2.DIST_L2, 5)
    hcx, hcy = BX, BY - FH * 0.5
    dmin = float(np.sqrt(((np.argwhere(hard)[:, 1] - hcx) ** 2 + (np.argwhere(hard)[:, 0] - hcy) ** 2).min()))
    P = dict(flame=BASE / 'G7d_flame_c0.png', relight=BASE / 'G7d_relight_falloff_v1d.png', protect=BASE / 'G7d_protect.png', still=BASE / 'G7d_still_zone_v1d.png')
    safe_img(P['flame'], fm); safe_img(P['relight'], rel * 255); safe_img(P['protect'], prot * 255.0); safe_img(P['still'], st * 255.0)
    ov = im.astype(np.float32).copy(); ov[st] = ov[st] * 0.5 + np.float32([255, 0, 255]) * 0.5
    ov = ov * (1 - 0.6 * rel[..., None]) + np.float32([0, 200, 255]) * 0.6 * rel[..., None]; ov[fm > 0] = [0, 255, 0]
    safe_img(BASE / 'G7d_mask_overlay.png', ov)
    cfg = json.load(open(LOCKED)); cfg = copy.deepcopy(cfg); Lr = cfg['layers'][0]; p = Lr['params']; s = p['sources'][0]
    sig = min(1.3 * FH, (dmin - 2) / 3.0 - 1)            # gauss_dot reach = 3*sigma+1 must stay outside the still zone
    s.update(xy=[BX, BY], flame=[FW, FH]); s['halo']['sigma'] = round(sig, 2)
    p['flame_warp'].update(mask=str(P['flame']), base=[BX, BY], height=round(1.4 * FH, 1), sway_px=2.5, zone_px=6)
    p['plate_flame'].update(mask=str(P['flame']))
    p['light_pool'].update(mask=str(P['relight']), center=[200.0, 420.0], r0=420.0)
    p['light_spill'][0].update(mask=str(P['relight']), radius=round(1.2 * 520, 1), amp=1.2, offset=[0.0, round(-0.5 * FH, 1)])
    Lr['mask'] = str(P['relight'])
    cfg.update(name='germanicus_G7d_light_v1d', plate=str(PLATE), out_dir=str(CFG), seed=1907, protect=[str(P['protect'])],
               labels=dict(before_note='Plate + slow push-in only', after_note='house-candle-lightspill-v1 on the lamp flame only; blade/blood/drips/pool and hand/body masked out (static)'))
    cfg['derived_from'] = dict(preset='house-candle-lightspill-v1', locked_json=str(LOCKED), locked_md5='0591d4c770c5363f1ca6135a5d961d17',
                               still_zone=str(P['still']), relight_falloff=dict(R=R, centre=[BX, BY - 30], hard_px=8, soft_px=30),
                               flame_bbox=[x, y, w, h], halo_sigma_cap=dict(still_dmin=dmin, sigma=sig), persons_mask=str(P['still']))
    cp = CFG / 'germ_G7d_light_v1d.json'
    if cp.exists(): raise SystemExit(f'refusing overwrite {cp}')
    json.dump(cfg, open(cp, 'x'), indent=1); print(cp, 'flame bbox', (x, y, w, h), 'dmin', round(dmin, 1), 'halo sigma', round(sig, 2), 'relight px', int((rel > 0).sum()))

if __name__ == '__main__':
    if '--preview' in sys.argv:
        im = cv2.imread(str(PLATE)).astype(np.float32); st = still_zone(); im[st] = im[st] * 0.5 + np.float32([255, 0, 255]) * 0.5
        cv2.imwrite(sys.argv[-1], cv2.resize(im, (470, 836)).astype(np.uint8))
    else: build()
