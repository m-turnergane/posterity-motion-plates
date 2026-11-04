import sys, json, numpy as np
sys.path.insert(0, 'tools'); from ref_analysis import REFS, read; from firestats import flame_masks, height_of; from hprise import hp_metrics
out = {}
for k, r in REFS.items():
    rs = []
    for s in (0.5, 6.5, 12.5):
        fr = read(r['path'], s, 180, r['crop'])
        if len(fr) < 120: continue
        L, M = flame_masks(fr, None, r['thr'], r['warm']); Hf = height_of(M); reg = np.mean(M, 0) > 0.05
        a = hp_metrics(fr, r['fps'], reg, Hf); b = hp_metrics(fr, r['fps'], reg, Hf, top_frac=0.5)
        rs.append(dict(win=s, Hf=Hf, all=a, top=b)); print(k, s, Hf, a, b['hp_rise_hps'])
    out[k] = rs
json.dump(out, open('ref/ref_hp_stats.json', 'w'), indent=1)
