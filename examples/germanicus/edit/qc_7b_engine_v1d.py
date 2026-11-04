# v1d 7B engine-level audit (native plate res, pre-camera): still zone (blade/blood/drips/pool/hand/body) must be bit-identical to the plate at every frame.
import json, sys, numpy as np, cv2
sys.path.insert(0, '.'); import make_masks_germanicus_v1b as K
cfgp = '/workspace/posterity/standalones/germanicus/motion/configs/germ_G7d_light_v1d.json'
cfg = json.load(open(cfgp)); b3 = K.MM_engine(); E = b3.Engine(cfg)
st = cv2.imread(cfg['derived_from']['still_zone'], 0) > 0
rel = cv2.imread(cfg['layers'][0]['mask'], 0) / 255.0; Y, X = np.mgrid[0:st.shape[0], 0:st.shape[1]]
lamp = (rel > 0.3) & (np.hypot(X - 167, Y - 232) > 60) & ~st   # relit surfaces (wall/lamp body/table), flame+halo core excluded
fl = cv2.imread(cfg['layers'][0]['params']['plate_flame']['mask'], 0) > 0
rows = []
for fi in range(0, 158):
    t = fi / 30.0; img, dx, dy = E.render(t); img = np.clip(np.rint(img), 0, 255); diff = np.abs(img - E.plate).max(2); d = np.abs(dx) + np.abs(dy)   # img rounded to uint8 as rendered by the build
    rows.append(dict(f=fi, t=round(t, 4), still_absdiff_max=float(diff[st].max()), still_disp_max=float(d[st].max()), outside_allow_max=float(diff[~E.allow].max()) if (~E.allow).any() else 0.0,
                     protect_disp_max=float(d[E.protect].max()), disp_max=float(d.max()), disp_outside_flamezone=float(d[~cv2.dilate(fl.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)].max()),
                     lamp_lum_ratio=float(img[lamp].mean() / E.plate[lamp].mean()), changed_pct=round(100 * float((diff > 0.5).mean()), 2)))
r = np.array([x['lamp_lum_ratio'] for x in rows]); steps = np.abs(np.diff(r))
out = dict(config=cfgp, frames=len(rows), still_absdiff_max=max(x['still_absdiff_max'] for x in rows), still_disp_max=max(x['still_disp_max'] for x in rows),
           protect_disp_max=max(x['protect_disp_max'] for x in rows), disp_outside_flamezone_max=max(x['disp_outside_flamezone'] for x in rows),
           flame_disp_max=max(x['disp_max'] for x in rows), lamp_region_lum_ratio=dict(min=float(r.min()), max=float(r.max()), swing_pct=round(100 * float(r.max() - r.min()), 2),
           max_step_pct_per_frame=round(100 * float(steps.max()), 3)), allow_pct=round(100 * float(E.allow.mean()), 2), rows=rows)
out['ok'] = out['still_absdiff_max'] == 0 and out['still_disp_max'] == 0 and out['protect_disp_max'] == 0
p = 'qc_rough_v1d/qc_7b_engine_audit_v1d.json'
json.dump(out, open(p, 'x'), indent=1)
print({k: v for k, v in out.items() if k != 'rows'})
