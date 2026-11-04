# Germanicus ROUGH v1c derived plates + 7B candle config (never overwrites, never deletes).
#  (1) 7B route (i): plates-derived/seq7b_lowerleft_v1c.png = owner plate seq7b.png crop x 0-434, y 900-1672 (lamp, spilled oil, toppled
#      table, empty bed, floor; NO wall shadow, NO Piso, no sword in this region of the plate) -> NLM denoise (h 3, de-block) -> bicubic to
#      1080x1920 (x2.488) -> unsharp 0.7 @ sigma 1.8 -> fixed-seed fine grain (sd 3). No new imagery.
#  (2) plates-derived/seq10_softcaps_v1c.png = owner plate seq10.png with Gaussian sigma 1.3 px applied ONLY inside the lettering mask
#      (4 text columns: perspective top/bottom lines, x 60-864, divider bars +-5 px excluded, AND local HF energy > 9, close 7x7), feather 1.5 px.
#      Zero displacement; frame, rivets, dividers, wall untouched (outside mask diff == 0 is asserted).
#  (3) G7c candle config (house-candle-lightspill-v1 via the same MM route as v1b) on the 7B crop: one source, flame coords scaled from v1b G7b,
#      flicker x1.4 / sway x1.3 kept; no persons in frame.
import json, sys, copy, math
from pathlib import Path
import numpy as np, cv2
G = Path('/workspace/posterity/standalones/germanicus'); PL = G / 'plates-owner'; PD = G / 'plates-derived'
sys.path.insert(0, str(G / 'edit')); import make_masks_germanicus_v1b as K
MM = K.MM
BASE = G / 'masks/v1c'; CFG = G / 'motion/configs'
for d in (BASE, CFG, PD): d.mkdir(parents=True, exist_ok=True)
C7 = dict(x0=0, y0=900, w=434, h=772)
S7 = 1080 / C7['w']

def plate7b():
    out = PD / 'seq7b_lowerleft_v1c.png'
    if out.exists(): return out
    im = cv2.imread(str(PL / 'seq7b.png'))
    c = im[C7['y0']:C7['y0'] + C7['h'], C7['x0']:C7['x0'] + C7['w']].copy()
    d = cv2.fastNlMeansDenoisingColored(c, None, 3, 3, 5, 15)
    up = cv2.resize(d, (1080, 1920), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    us = up + 0.7 * (up - cv2.GaussianBlur(up, (0, 0), 1.8))
    rng = np.random.default_rng(7); gr = cv2.GaussianBlur(rng.normal(0, 1, (1920, 1080)).astype(np.float32), (0, 0), 0.7); gr *= 3.0 / gr.std()
    K.safe_img(out, np.clip(np.rint(us + gr[..., None]), 0, 255).astype(np.uint8)); return out

def plate10():
    out = PD / 'seq10_softcaps_v1c.png'
    if out.exists(): return out
    im = cv2.imread(str(PL / 'seq10.png')).astype(np.float32); H, W = im.shape[:2]
    g = cv2.cvtColor(im.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = cv2.GaussianBlur(np.abs(g - cv2.GaussianBlur(g, (0, 0), 1.2)), (0, 0), 4)
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    poly = (X >= 60) & (X <= 864) & (Y >= 268 + (X - 300) * 0.255) & (Y <= 984 + (X - 620) * 0.075)
    for dx in (297, 502, 697): poly &= np.abs(X - dx) > 5
    m = cv2.morphologyEx((poly & (e > 9)).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    m = (m > 0) & poly
    mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)
    K.safe_img(BASE / 'G10_lettering_mask_v1c.png', mf * 255)
    o = im * (1 - mf[..., None]) + cv2.GaussianBlur(im, (0, 0), 1.3) * mf[..., None]
    o = np.clip(np.rint(o), 0, 255).astype(np.uint8)
    diff = np.abs(o.astype(int) - im.astype(int)).max(2)
    assert diff[mf <= 0].max() == 0, 'pixels outside the lettering mask changed'
    K.safe_img(out, o)
    json.dump(dict(plate=str(out), src=str(PL / 'seq10.png'), sigma=1.3, feather=1.5, mask_px=int(m.sum()), changed_px=int((diff > 0).sum()),
                   outside_mask_changed_px=int((diff[mf <= 0] > 0).sum())), open(BASE / 'G10_softcaps_v1c.json', 'x'), indent=1)
    return out

def config7c(pl):
    cfgp = CFG / 'germ_G7c_light_v1c.json'
    if cfgp.exists(): return cfgp
    sid = 'G7c'; im = cv2.imread(str(pl)); H, W = im.shape[:2]
    bx, by = 193 * S7, (1238 - C7['y0']) * S7; fw, fh_ = 34 * S7, 125 * S7
    sources = [dict(xy=[round(bx, 1), round(by, 1)], flame=[round(fw, 1), round(fh_, 1)], flame_poly=K.tear(round(bx, 1), round(by + 5, 1), round(fw + 10, 1), round(fh_ + 10, 1)))]
    spec = dict(status=K.VER.replace('v1b', 'v1c') + ' -- G7c = v1b G7b source scaled x%.4f onto the 7B lower-left crop' % S7, plate=pl.name, plate_size=[W, H], v_min=200,
                sources=sources, exclude_polys=[], pool_center=None, face_hand_polys=[], note='no person in frame (route i crop excludes Piso and the wall shadow)')
    sj = BASE / f'{sid}_candles.json'
    if not sj.exists(): K.safe_json(sj, spec)
    spec, err = MM.load_spec(sid, BASE); assert not err, err
    P = MM.mask_paths(sid, BASE, 1)
    if not P['relight'].exists(): MM.make_masks(sid, str(pl), BASE, spec)
    m = cv2.imread(str(P['flames'][0]), 0); print(sid, 'flame px', int((m > 0).sum()), 'bbox', cv2.boundingRect((m > 0).astype(np.uint8)))
    rel = cv2.imread(str(P['relight']), 0).astype(np.float32) / 255.0; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    R = 620 * S7; fall = np.exp(-((X - bx) ** 2 + (Y - by) ** 2) / R ** 2); fall[fall < 0.02] = 0; fall = cv2.GaussianBlur(fall, (0, 0), 3 * S7) * rel
    fp = BASE / f'{sid}_relight_falloff_v1c.png'
    if not fp.exists(): K.safe_img(fp, fall * 255)
    pp = BASE / f'{sid}_persons_v1c.png'
    if not pp.exists(): K.safe_img(pp, np.zeros((H, W), np.uint8))
    mm_cfg = BASE / f'{sid}_mm_config_raw.json'
    cfg = json.load(open(mm_cfg)) if mm_cfg.exists() else MM.make_config(sid, str(pl), BASE, spec, mm_cfg)
    cfg = copy.deepcopy(cfg)
    for L in cfg['layers']:
        L['mask'] = str(fp.resolve()); p = L['params']
        if 'light_pool' in p: p['light_pool']['mask'] = str(fp.resolve())
        for sp_ in p.get('light_spill', []): sp_['mask'] = str(fp.resolve())
        for s_ in p['sources']: s_['flicker']['amps'] = [round(a * 1.4, 4) for a in s_['flicker']['amps']]
        if 'flame_warp' in p: p['flame_warp']['sway_px'] = round(p['flame_warp']['sway_px'] * 1.3, 3)
    cfg.update(name='germanicus_G7c_light_v1c', seed=1906, out_dir=str(CFG))
    cfg['labels'] = dict(before_note='Plate + slow zoom only', after_note='candle light-spill: pool/spill/halo + plate_flame + flame sway on the lamp flame (flame pixels only)')
    cfg['derived_from'].update(germ_mm_raw=str(mm_cfg), relight_falloff=dict(mask=str(fp), R=[R], formula='exp(-d^2/R^2), <0.02->0, blur 3*s, x relight'),
                               flame_warp_popped_layers=[], persons_mask=str(pp), flicker_x=1.4, sway_x=1.3, crop_from_seq7b=C7, scale=S7)
    K.safe_json(cfgp, cfg); return cfgp

def qc(cfgp):
    b3 = K.MM_engine(); cfg = json.load(open(cfgp)); E = b3.Engine(cfg); r = []
    pers = cv2.imread(cfg['derived_from']['persons_mask'], 0) > 0
    for t in np.arange(0, 6.0, 0.5):
        img, dx, dy = E.render(float(t)); diff = np.abs(img - E.plate).max(2); d = np.abs(dx) + np.abs(dy)
        r.append(dict(t=float(t), outside_max=float(diff[~E.allow].max()) if (~E.allow).any() else 0.0, disp_max=float(d.max()),
                      protect_disp_max=float(d[E.protect].max()) if E.protect.any() else 0.0, person_disp_max=float(d[pers].max()) if pers.any() else 0.0,
                      changed_pct=round(100 * float((diff > 0.5).mean()), 2)))
    ok = all(x['outside_max'] == 0 and x['protect_disp_max'] == 0 and x['person_disp_max'] == 0 for x in r)
    return dict(G7c=dict(times=r, allow_pct=round(100 * float(E.allow.mean()), 2), ok=ok))

if __name__ == '__main__':
    p7 = plate7b(); p10 = plate10(); c = config7c(p7); print(p7, p10, c)
    if '--qc' in sys.argv:
        R = qc(c); qp = G / 'edit/qc_masks_germanicus_v1c.json'
        if not qp.exists(): json.dump(R, open(qp, 'x'), indent=1)
        print('QC', 'OK' if R['G7c']['ok'] else 'FAIL', max(x['disp_max'] for x in R['G7c']['times']))
