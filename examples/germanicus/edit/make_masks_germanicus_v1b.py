# Germanicus "They Found His Name in the Walls" -- candle masks + b3 configs v1b (never overwrites, never deletes).
#   v1b = v1 + teardrop flame polys (v1 box polys grabbed the warm-lit wall around the flame on G1a/G5/G6) + per-plate v_min.
#   locked house-candle-lightspill-v1 via day21 make_masks_atahualpa_v2 (MM, same route as Croatoan ch3) + per-source exp falloff relight.
#   flame_warp (sway) KEPT on candle-sized lamp flames; popped (glow/brightness only) where a flame overlaps a person (G6 c0).
#   person polys -> MM face_hand protect (flame pixels within zone+3 px of a person are dropped) + audit masks (person_*.png).
#   G7b: plate = seq7b with a static directional motion blur baked onto Piso (plates-derived/seq7b_pisoblur_v1.png); tipping lamp: wider flame poly,
#        flicker amps x1.4, sway x1.3, long falloff so the lamp's flicker breathes on the wall shadow.
import json, sys, copy, math
from pathlib import Path
import numpy as np, cv2
G = Path('/workspace/posterity/standalones/germanicus'); PL = G / 'plates-owner'; PD = G / 'plates-derived'
sys.path.insert(0, '/workspace/posterity/day21/atahualpa/edit'); import make_masks_atahualpa_v2 as MM
BASE = G / 'masks/v1b'; CFG = G / 'motion/configs'
for d in (BASE, CFG, PD): d.mkdir(parents=True, exist_ok=True)
def tear(bx, by, w, h, n=24):
    # flame-shaped polygon: base at (bx,by), widest (w) at 30 % height, tip at by-h
    L, Rr = [], []
    for i in range(n + 1):
        u = i / n; f = (u / 0.3) ** 0.6 if u < 0.3 else ((1 - u) / 0.7) ** 0.85
        y = by - u * h; hw = max(1.0, 0.5 * w * f); L.append([round(bx - hw, 1), round(y, 1)]); Rr.append([round(bx + hw, 1), round(y, 1)])
    return [[bx, by + 2]] + Rr + L[::-1]
def src(xy, flame, poly, R, warp=True, dx=0):
    # poly arg kept for the record; v1b uses a teardrop of (flame w+4, h+4) centred dx px off the base
    return dict(xy=list(xy), flame=list(flame), flame_poly=tear(xy[0] + dx, xy[1] + 2, flame[0] + 4, flame[1] + 4), box_poly_v1=poly, R=R, warp=warp)
VER = 'VERIFIED (visual crops 2-3x with 20 px grid, Tue Oct 27 2026; v1b teardrop polys)'
PISO = [[690, 560], [720, 530], [770, 540], [780, 505], [850, 370], [880, 335], [941, 290], [941, 1420], [830, 1420], [790, 1200], [760, 1000], [720, 830], [690, 700]]
BLADE = [[775, 512], [790, 488], [878, 362], [890, 372], [800, 505]]
SPECS = {
 'G1a': dict(plate='seq1a.png', v_min=232, sources=[src([106, 180], [40, 120], [[82, 55], [132, 55], [132, 182], [82, 182]], R=320)], fh=[], persons=[]),
 'G1b': dict(plate='seq1b.png', v_min=215, sources=[src([333, 826], [11, 27], [[324, 796], [343, 796], [343, 829], [324, 829]], R=240),
                                         src([878, 339], [8, 19], [[871, 318], [886, 318], [886, 341], [871, 341]], R=130)],
             fh=[[[0, 520], [240, 520], [285, 680], [297, 808], [300, 825], [328, 836], [330, 860], [300, 900], [280, 1100], [240, 1220], [0, 1230]],
                 [[470, 620], [700, 610], [941, 780], [941, 1420], [700, 1460], [460, 1250], [455, 900]],
                 [[580, 280], [700, 280], [860, 350], [855, 560], [580, 560]]]),
 'G4': dict(plate='seq4.png', v_min=225, sources=[src([20, 773], [15, 52], [[9, 718], [32, 718], [32, 776], [9, 776]], R=340),
                                       src([76, 903], [16, 57], [[64, 843], [88, 843], [88, 906], [64, 906]], R=300)],
            fh=[[[240, 400], [480, 400], [560, 560], [800, 700], [941, 760], [941, 1672], [150, 1672], [130, 1000], [130, 620], [240, 560]]]),
 'G5': dict(plate='seq5.png', v_min=232, sources=[src([129, 402], [18, 73], [[116, 326], [142, 326], [142, 405], [116, 405]], R=300)], fh=[], persons=[]),
 'G6': dict(plate='seq6.png', v_min=225, sources=[src([24, 912], [17, 69], [[13, 841], [37, 841], [37, 915], [13, 915]], R=300, warp=False),
                                       src([103, 1028], [18, 66], [[91, 961], [116, 961], [116, 1031], [91, 1031]], R=280)],
            fh=[[[0, 420], [200, 420], [215, 700], [160, 820], [60, 832], [0, 832]],
                [[180, 560], [420, 560], [560, 800], [700, 1000], [860, 1450], [300, 1500], [250, 1350], [170, 1000], [150, 880]],
                [[340, 250], [941, 220], [941, 1450], [600, 950], [500, 700], [330, 500]]],
            persons=[[[0, 420], [200, 420], [215, 700], [160, 900], [120, 885], [0, 880]],
                     [[180, 560], [420, 560], [560, 800], [700, 1000], [860, 1450], [300, 1500], [250, 1350], [170, 1000], [150, 880]],
                     [[340, 250], [941, 220], [941, 1450], [600, 950], [500, 700], [330, 500]]],
            note='c0 overlaps the woman\'s robe -> no flame_warp on c0 (glow/brightness only); woman fh stops at y 832 so c0 keeps its flame pixels'),
 'G7b': dict(plate='seq7b_pisoblur_v1.png', derived=True, sources=[src([193, 1238], [34, 125], [[168, 1105], [218, 1105], [218, 1242], [168, 1242]], R=620)],
             fh=[PISO], flicker_x=1.4, sway_x=1.3),
}
SEEDS = {k: 1900 + i for i, k in enumerate(SPECS)}
def safe_json(p, d):
    p = Path(p)
    if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    json.dump(d, open(p, 'w'), indent=1)
def safe_img(p, m):
    p = Path(p)
    if p.exists(): raise SystemExit(f'refusing overwrite {p}')
    cv2.imwrite(str(p), np.clip(m, 0, 255).astype(np.uint8) if m.dtype != np.uint8 else m)
def polymask(shape, polys):
    m = np.zeros(shape[:2], np.uint8)
    for pp in polys: cv2.fillPoly(m, [np.int32(pp)], 255)
    return m

def piso_blur():
    out = PD / 'seq7b_pisoblur_v1.png'
    if out.exists(): return out
    im = cv2.imread(str(PL / 'seq7b.png')).astype(np.float32); H, W = im.shape[:2]
    def mblur(img, L, ang):
        k = np.zeros((L * 2 + 1, L * 2 + 1), np.float32); c = L; dx, dy = math.cos(ang), math.sin(ang)
        for s in np.linspace(-L / 2, L / 2, 4 * L): k[int(round(c + s * dy)), int(round(c + s * dx))] = 1
        return cv2.filter2D(img, -1, k / k.sum(), borderType=cv2.BORDER_REFLECT)
    ang = math.atan2(0.8, -0.6)          # the downward-left stroke of the stab
    body = mblur(im, 18, ang); blade = mblur(im, 7, ang)
    mb = cv2.GaussianBlur(polymask(im.shape, [PISO]).astype(np.float32) / 255, (0, 0), 5)[..., None]
    mk = cv2.GaussianBlur(polymask(im.shape, [BLADE]).astype(np.float32) / 255, (0, 0), 3)[..., None]
    o = im * (1 - mb) + body * mb; o = o * (1 - mk) + blade * mk     # blade keeps a lighter blur so the dagger stays legible
    safe_img(out, o.round()); return out

def configs():
    out = {}
    for sid, S in SPECS.items():
        cfgp = CFG / f'germ_{sid}_light_v1b.json'
        if cfgp.exists(): out[sid] = str(cfgp); print(sid, 'exists'); continue
        pl = (PD if S.get('derived') else PL) / S['plate']
        im = cv2.imread(str(pl)); H, W = im.shape[:2]
        spec = dict(status=VER, plate=pl.name, plate_size=[W, H], v_min=S.get('v_min', 200), sources=[{k: v for k, v in q.items() if k in ('xy', 'flame', 'flame_poly')} for q in S['sources']],
                    exclude_polys=[], pool_center=None, face_hand_polys=S['fh'], note=S.get('note', ''))
        sj = BASE / f'{sid}_candles.json'
        if not sj.exists(): safe_json(sj, spec)
        spec, err = MM.load_spec(sid, BASE); assert not err, err
        P = MM.mask_paths(sid, BASE, len(spec['sources']))
        if not P['relight'].exists(): MM.make_masks(sid, str(pl), BASE, spec)
        for k, f in enumerate(P['flames']):
            m = cv2.imread(str(f), 0); print(sid, f'c{k} flame px', int((m > 0).sum()), 'bbox', cv2.boundingRect((m > 0).astype(np.uint8)))
        rel = cv2.imread(str(P['relight']), 0).astype(np.float32) / 255.0; Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
        fall = np.zeros((H, W), np.float32)
        for q in S['sources']: fall = np.maximum(fall, np.exp(-((X - q['xy'][0]) ** 2 + (Y - q['xy'][1]) ** 2) / q['R'] ** 2))
        fall[fall < 0.02] = 0; fall = cv2.GaussianBlur(fall, (0, 0), 3) * rel
        fp = BASE / f'{sid}_relight_falloff_v1b.png'
        if not fp.exists(): safe_img(fp, fall * 255)
        pers = S.get('persons', S['fh'])
        pp = BASE / f'{sid}_persons_v1b.png'
        if not pp.exists(): safe_img(pp, polymask(im.shape, pers))
        mm_cfg = BASE / f'{sid}_mm_config_raw.json'
        cfg = json.load(open(mm_cfg)) if mm_cfg.exists() else MM.make_config(sid, str(pl), BASE, spec, mm_cfg)
        cfg = copy.deepcopy(cfg); popped = []
        for i, (L, q) in enumerate(zip(cfg['layers'], S['sources'])):
            L['mask'] = str(fp.resolve()); p = L['params']
            if 'light_pool' in p: p['light_pool']['mask'] = str(fp.resolve())
            for sp_ in p.get('light_spill', []): sp_['mask'] = str(fp.resolve())
            if not q['warp']: p.pop('flame_warp', None); p['plate_flame']['tongue'] = 0.0; popped.append(i)
            if S.get('flicker_x'):
                for s_ in p['sources']: s_['flicker']['amps'] = [round(a * S['flicker_x'], 4) for a in s_['flicker']['amps']]
            if S.get('sway_x') and 'flame_warp' in p: p['flame_warp']['sway_px'] = round(p['flame_warp']['sway_px'] * S['sway_x'], 3)
        cfg.update(name=f'germanicus_{sid}_light_v1b', seed=SEEDS[sid], out_dir=str(CFG))
        cfg['labels'] = dict(before_note='Plate + slow zoom only', after_note='candle light-spill: pool/spill/halo + plate_flame + flame sway on lamp flames (flame pixels only)')
        cfg['derived_from'].update(germ_mm_raw=str(mm_cfg), relight_falloff=dict(mask=str(fp), R=[q['R'] for q in S['sources']], formula='max_k exp(-d_k^2/R_k^2), <0.02->0, blur 3, x relight'),
                                   flame_warp_popped_layers=popped, persons_mask=str(pp), flicker_x=S.get('flicker_x', 1.0), sway_x=S.get('sway_x', 1.0))
        safe_json(cfgp, cfg); out[sid] = str(cfgp); print(sid, 'config', cfgp)
    return out

def overlay():
    rows = []
    for sid, S in SPECS.items():
        pl = (PD if S.get('derived') else PL) / S['plate']; im = cv2.imread(str(pl))
        for k, q in enumerate(S['sources']):
            m = cv2.imread(str(BASE / f'{sid}_flame_c{k}.png'), 0); x, y = q['xy']; w, h = q['flame']
            x0, y0, x1, y1 = max(0, x - w - 20), max(0, y - h - 20), min(im.shape[1], x + w + 20), min(im.shape[0], y + 15)
            c = im[y0:y1, x0:x1].copy(); o = c.copy(); mm = m[y0:y1, x0:x1] > 0; o[mm] = (o[mm] * 0.3 + np.array([255, 0, 255]) * 0.7).astype(np.uint8)
            t = np.hstack([c, o]); sc = 300 / t.shape[0]; rows.append(cv2.resize(t, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST))
    p = G / 'edit/qc_flame_masks_v1b.jpg'
    if not p.exists(): cv2.imwrite(str(p), np.hstack(rows))

def MM_engine():
    import importlib.util
    sp = importlib.util.spec_from_file_location('animate_b3_locked', str(MM.ENGINE)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def qc(cfgs):
    b3 = MM_engine(); rows = {}
    for sid, cp in cfgs.items():
        cfg = json.load(open(cp)); E = b3.Engine(cfg); r = []
        pers = cv2.imread(cfg['derived_from']['persons_mask'], 0) > 0
        for t in np.arange(0, 6.0, 0.5):
            img, dx, dy = E.render(float(t)); diff = np.abs(img - E.plate).max(2); d = np.abs(dx) + np.abs(dy)
            r.append(dict(t=float(t), outside_max=float(diff[~E.allow].max()) if (~E.allow).any() else 0.0, disp_max=float(d.max()),
                          protect_disp_max=float(d[E.protect].max()) if E.protect.any() else 0.0, person_disp_max=float(d[pers].max()) if pers.any() else 0.0,
                          changed_pct=round(100 * float((diff > 0.5).mean()), 2)))
        rows[sid] = dict(times=r, allow_pct=round(100 * float(E.allow.mean()), 2),
                         ok=all(x['outside_max'] == 0 and x['protect_disp_max'] == 0 and x['person_disp_max'] == 0 for x in r))
        print(sid, 'ok' if rows[sid]['ok'] else 'FAIL', 'disp_max', max(x['disp_max'] for x in r), 'person_disp_max', max(x['person_disp_max'] for x in r), 'changed%', r[3]['changed_pct'])
    return rows

if __name__ == '__main__':
    piso_blur(); c = configs(); overlay()
    if '--qc' in sys.argv:
        R = qc(c); qp = G / 'edit/qc_masks_germanicus_v1b.json'; k = 2
        while qp.exists(): qp = G / f'edit/qc_masks_germanicus_v1b_{k}.json'; k += 1
        json.dump(R, open(qp, 'w'), indent=1); print('QC ->', qp, 'ALL OK' if all(v['ok'] for v in R.values()) else 'FAIL')
