#!/usr/bin/env python3
"""Positive control for doc_reveal_v1.legibility: the same frames with and without a small PAINTED word on the page.
The gate must pass the real frames and catch the painted ones. Writes proofs/legibility_positive_control.json.
(The painted word exists only in memory for this test; it is never rendered to any output.)"""
import json, sys, cv2, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import doc_reveal_v1 as D
out = []
for cfg in sorted((HERE / "configs").glob("dr0[1-4]*.json")):
    s = D.Shot(str(cfg)); inner = cv2.erode(s.doc.bin.astype(np.uint8), np.ones((25, 25), np.uint8))
    ys, xs = np.nonzero(inner); cx, cy = int(xs.mean()), int(ys.mean())
    for t in (0.0, 0.6, 1.0, 1.4):
        pf, rf = s.plate_frame(t, with_ref=True)
        for word, sc in (("ad", 0.35), ("anno domini", 0.5)):
            fk = pf.copy(); (tw, th), _ = cv2.getTextSize(word, cv2.FONT_HERSHEY_SIMPLEX, sc, 1)
            cv2.putText(fk, word, (cx - tw // 2, cy + th // 2), cv2.FONT_HERSHEY_SIMPLEX, sc, (70, 55, 40), 1, cv2.LINE_AA)
            a, b = D.legibility(rf, pf, s.doc.bin), D.legibility(rf, fk, s.doc.bin)
            ga = a["hp_logratio_p99"] <= 0.02 and a["lapvar_log_ratio"] <= 1.05
            gb = b["hp_logratio_p99"] <= 0.02 and b["lapvar_log_ratio"] <= 1.05
            out.append(dict(shot=s.name, t=t, word=word, real=dict(hp=a["hp_logratio_p99"], lapvar=a["lapvar_log_ratio"], new_edges=a["new_edges_px"], gate_pass=bool(ga)),
                            painted=dict(hp=b["hp_logratio_p99"], lapvar=b["lapvar_log_ratio"], new_edges=b["new_edges_px"], gate_pass=bool(gb))))
            print(out[-1], flush=True)
summ = dict(real_frames=len(out), real_pass=sum(o["real"]["gate_pass"] for o in out), painted_caught=sum(not o["painted"]["gate_pass"] for o in out),
            real_hp_max=max(o["real"]["hp"] for o in out), painted_hp_min=min(o["painted"]["hp"] for o in out),
            real_new_edges_max=max(o["real"]["new_edges"] for o in out), painted_new_edges_min=min(o["painted"]["new_edges"] for o in out))
json.dump(dict(summary=summ, cases=out), open(HERE / "proofs" / "legibility_positive_control.json", "w"), indent=1); print(summ)
