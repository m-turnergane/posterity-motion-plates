import sys, json, numpy as np, cv2, subprocess
sys.path.insert(0, 'tools'); from firestats import stats, lumf
def read(path, ss, n, crop):
    x0, y0, x1, y1 = crop
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_MSEC, ss * 1000); out = []
    while len(out) < n:
        ok, f = cap.read()
        if not ok: break
        out.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)[y0:y1, x0:x1].copy())
    return out
REFS = {
 "campfire_claytor": dict(path="ref/campfire_claytor.webm", fps=30.0, crop=(470, 70, 790, 440), thr=0.70, warm=0.20, bgbox=None, lic="CC BY 2.0, Virginia State Parks (Wikimedia Commons: 'Campfire at night - Claytor Lake State Park - video')"),
 "fire_bastique": dict(path="ref/fire_bastique.ogv", fps=29.97, crop=(40, 20, 340, 480), thr=0.40, warm=0.20, bgbox=None, lic="Public domain, Cary Bass / User:Bastique (Wikimedia Commons: 'Fire.ogv')"),
 "fireplace_bosnia": dict(path="ref/fireplace_bosnia.webm", fps=29.97, crop=(0, 0, 478, 570), thr=0.62, warm=0.30, bgbox=(320, 40, 470, 190), lic="CC BY-SA 4.0, User:Bosancica_by_MK (Wikimedia Commons: 'Fire burning in a fireplace in Bosnia and Herzegovina (2026)-bs')"),
}
if __name__ == "__main__":
    res = {}
    for k, r in REFS.items():
        dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', r['path']]))
        wins = [s for s in np.arange(0.5, dur - 6.2, 6.0)][:5]
        rs = []
        for s in wins:
            fr = read(r['path'], s, 180, r['crop'])
            if len(fr) < 120: continue
            bg = None
            if r['bgbox']:
                bg = np.zeros(fr[0].shape[:2], bool); a, b, c, d = r['bgbox']; bg[b:d, a:c] = True
            # warm constraint: R channel > B channel by margin
            reg = None
            st = stats(fr, r['fps'], region=reg, thr=r['thr'], bg=bg, warm=r['warm'], label=f"{k}@{s:.1f}s")
            rs.append(st); print(json.dumps(st))
        res[k] = dict(licence=r['lic'], windows=rs)
        cv2.imwrite(f"ref/{k}_crop_mask.png", np.concatenate([cv2.cvtColor(fr[0], cv2.COLOR_RGB2BGR), cv2.cvtColor((((lumf(fr[0]) > r['thr']) & ((fr[0][...,0].astype(float)-fr[0][...,2])/255>r['warm'])) * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)], 1))
    json.dump(res, open('ref/ref_flow_stats_raw.json', 'w'), indent=1)
