import sys, json, numpy as np
sys.path.insert(0, 'tools'); from hprise import hp_metrics; from specs import load_masks
F = np.load(sys.argv[1]); CX0, CY0 = 368, 672; masks = load_masks(); res = {}
for i, (mk, Hf) in enumerate(zip(masks, (64, 62, 60))):
    reg = mk[CY0:CY0 + F.shape[1], CX0:CX0 + F.shape[2]] > 0.5
    a = hp_metrics(list(F), 30.0, reg, Hf); b = hp_metrics(list(F), 30.0, reg, Hf, top_frac=0.5)
    res[f"c{i}"] = dict(all=a, top=b); print(f"c{i}", a, "top_rise", b['hp_rise_hps'])
if len(sys.argv) > 2: json.dump(res, open(sys.argv[2], 'w'), indent=1)
