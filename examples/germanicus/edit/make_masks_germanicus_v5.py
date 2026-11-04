# Germanicus v5 -- candle mask + b3 config for the new owner plate Seq7B (seq7b_piso_room_daybreak_sword_floor_v5_OWNER.png). Never overwrites, never deletes.
#   Same route as make_masks_germanicus_v1b.py (locked house-candle-lightspill-v1 via MM + per-source exp falloff relight), one source = the small oil lamp
#   on the side table (flame base (886, 650), ~10 x 52 px, candle-sized -> flame sway kept on flame pixels only). Sword + bed + door protected (static).
#   New plates checked for flames (warm-bright blob scan + visual): SeqR / SeqW / SeqC / SeqG have none -> plate + slow zoom only.
import json, sys, copy
from pathlib import Path
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).parent)); import make_masks_germanicus_v1b as K
MM = K.MM; G = K.G; PL = K.PL; CFG = K.CFG; BASE = G / 'masks/v5'; BASE.mkdir(parents=True, exist_ok=True)
VER = 'VERIFIED (visual crops 6x with 10 px grid, Tue Oct 27 2026 ~17:00 EDT; v1b teardrop polys)'
SWORD = [[300, 1062], [395, 1030], [680, 990], [700, 1000], [690, 1012], [455, 1072], [400, 1090], [320, 1105], [295, 1090]]
BED = [[0, 840], [500, 860], [530, 980], [470, 1040], [0, 1060]]
SPECS = {'G7b5': dict(plate='seq7b_piso_room_daybreak_sword_floor_v5_OWNER.png', v_min=225, sources=[K.src([886, 650], [10, 52], None, R=240)],
                      fh=[SWORD], persons=[SWORD], note='single small oil lamp; sword polygon protected (static) -- empty room, no persons')}
SEEDS = {'G7b5': 1950}
def configs():
    out = {}
    for sid, S in SPECS.items():
        cfgp = CFG / f'germ_{sid}_light_v5.json'
        if cfgp.exists(): out[sid] = str(cfgp); print(sid, 'exists'); continue
        pl = PL / S['plate']; im = cv2.imread(str(pl)); H, W = im.shape[:2]
        spec = dict(status=VER, plate=pl.name, plate_size=[W, H], v_min=S['v_min'], sources=[{k: v for k, v in q.items() if k in ('xy', 'flame', 'flame_poly')} for q in S['sources']],
                    exclude_polys=[], pool_center=None, face_hand_polys=S['fh'], note=S.get('note', ''))
        sj = BASE / f'{sid}_candles.json'
        if not sj.exists(): K.safe_json(sj, spec)
        spec, err = MM.load_spec(sid, BASE); assert not err, err
        P = MM.mask_paths(sid, BASE, len(spec['sources']))
        if not P['relight'].exists(): MM.make_masks(sid, str(pl), BASE, spec)
        for k, f in enumerate(P['flames']):
            m = cv2.imread(str(f), 0); print(sid, f'c{k} flame px', int((m > 0).sum()), 'bbox', cv2.boundingRect((m > 0).astype(np.uint8)))
        rel = cv2.imread(str(P['relight']), 0).astype(np.float32) / 255.0; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        fall = np.zeros((H, W), np.float32)
        for q in S['sources']: fall = np.maximum(fall, np.exp(-((X - q['xy'][0]) ** 2 + (Y - q['xy'][1]) ** 2) / q['R'] ** 2))
        fall[fall < 0.02] = 0; fall = cv2.GaussianBlur(fall, (0, 0), 3) * rel
        fall[K.polymask(im.shape, [SWORD]) > 0] = 0
        fp = BASE / f'{sid}_relight_falloff_v5.png'
        if not fp.exists(): K.safe_img(fp, fall * 255)
        pp = BASE / f'{sid}_persons_v5.png'
        if not pp.exists(): K.safe_img(pp, K.polymask(im.shape, S['persons']))
        mm_cfg = BASE / f'{sid}_mm_config_raw.json'
        cfg = json.load(open(mm_cfg)) if mm_cfg.exists() else MM.make_config(sid, str(pl), BASE, spec, mm_cfg)
        cfg = copy.deepcopy(cfg)
        for L in cfg['layers']:
            L['mask'] = str(fp.resolve()); p = L['params']
            if 'light_pool' in p: p['light_pool']['mask'] = str(fp.resolve())
            for sp_ in p.get('light_spill', []): sp_['mask'] = str(fp.resolve())
        cfg.update(name=f'germanicus_{sid}_light_v5', seed=SEEDS[sid], out_dir=str(CFG))
        cfg['labels'] = dict(before_note='Plate + slow zoom only', after_note='candle light-spill on the single oil lamp (flame pixels sway only); sword static')
        cfg['derived_from'].update(germ_mm_raw=str(mm_cfg), relight_falloff=dict(mask=str(fp), R=[q['R'] for q in S['sources']], formula='max_k exp(-d_k^2/R_k^2), <0.02->0, blur 3, x relight, sword zeroed'),
                                   flame_warp_popped_layers=[], persons_mask=str(pp), flicker_x=1.0, sway_x=1.0)
        K.safe_json(cfgp, cfg); out[sid] = str(cfgp); print(sid, 'config', cfgp)
    return out
def overlay():
    S = SPECS['G7b5']; im = cv2.imread(str(PL / S['plate'])); q = S['sources'][0]; m = cv2.imread(str(BASE / 'G7b5_flame_c0.png'), 0); fall = cv2.imread(str(BASE / 'G7b5_relight_falloff_v5.png'), 0)
    o = im.copy(); mm = m > 0; o[mm] = (o[mm] * 0.3 + np.array([255, 0, 255]) * 0.7).astype(np.uint8)
    heat = cv2.applyColorMap(fall, cv2.COLORMAP_JET); o2 = cv2.addWeighted(im, 0.6, heat, 0.4, 0); cv2.polylines(o2, [np.int32(SWORD)], True, (0, 255, 0), 2)
    p = G / 'edit/qc_flame_mask_v5_G7b5.jpg'
    if not p.exists(): cv2.imwrite(str(p), np.hstack([cv2.resize(o[560:720, 820:941], None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)[:, :, :] if False else cv2.resize(o, (470, 836)), cv2.resize(o2, (470, 836))]))
if __name__ == '__main__':
    c = configs(); overlay()
    K.CFG = CFG
    R = K.qc(c); qp = G / 'edit/qc_masks_germanicus_v5.json'
    if not qp.exists(): json.dump(R, open(qp, 'w'), indent=1)
    print('QC ->', qp, 'ALL OK' if all(v['ok'] for v in R.values()) else 'FAIL')
