#!/workspace/mpvenv/bin/python
"""Rough v3b: H04a ink grade, pass 2. Derived copy only (source plate untouched).
Takes the v3 ink-graded copy (page stain already ink) and grades the remaining faint maroon drips / puddle at the
TABLE EDGE below the page to iron-gall ink at the same luma. Mask = crimson hue (<17 deg, i.e. redder than the
orange candle-lit wood at ~22-25 deg) & saturated, inside a feathered table-edge box. Writes a new PNG + log ('x')."""
import sys; sys.dont_write_bytecode = True
import json, hashlib, cv2, numpy as np
from pathlib import Path
BR = Path(__file__).parent
SRC0 = Path('/workspace/posterity/standalones/bathory/v2/plates/h04a_priest_writes_legend.png')
SRC = BR / 'h04a_priest_writes_legend_inkgraded.png'                 # v3 derived copy (page stain)
OUT = BR / 'h04a_priest_writes_legend_inkgraded_v3b.png'
TABLE_BOX = (305, 1360, 520, 1455)                                    # x0, y0, x1, y1 (plate px) - table edge under the page
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
def hue_sat(P):
    r, g, b = P[..., 0], P[..., 1], P[..., 2]; mx = P.max(-1); mn = P.min(-1); d = np.maximum(mx - mn, 1e-3)
    h = np.where(mx == r, 60 * (g - b) / d, np.where(mx == g, 60 * (2 + (b - r) / d), 60 * (4 + (r - g) / d))) % 360
    return h, (mx - mn) / np.maximum(mx, 1e-3)
def crimson(P, hmax=17.0):
    h, s = hue_sat(P); hh = np.where(h > 180, h - 360, h)            # -180..180, red ~0
    return np.clip((hmax - hh) / 5.0, 0, 1) * (hh > -40) * np.clip((s - 0.25) / 0.1, 0, 1) * (P[..., 0] > 18)
if __name__ == '__main__':
    assert not OUT.exists(), OUT
    P = cv2.cvtColor(cv2.imread(str(SRC)), cv2.COLOR_BGR2RGB).astype(np.float32); H, W = P.shape[:2]; x0, y0, x1, y1 = TABLE_BOX
    box = np.zeros((H, W), np.float32); box[y0:y1, x0:x1] = 1; box = cv2.GaussianBlur(box, (0, 0), 6)
    box[:y0 - 20] = 0; box[y1 + 20:] = 0; box[:, :x0 - 20] = 0; box[:, x1 + 20:] = 0
    m = cv2.GaussianBlur(crimson(P), (0, 0), 1.5) * box
    L = (0.299 * P[..., 0] + 0.587 * P[..., 1] + 0.114 * P[..., 2])[..., None]
    tint = np.float32([1.0, 0.86, 0.74]); tint = tint / (0.299 * tint[0] + 0.587 * tint[1] + 0.114 * tint[2])
    out = np.clip(P * (1 - m[..., None]) + L * tint[None, None] * m[..., None] + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(str(OUT), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    ch = np.abs(out.astype(int) - P.astype(int)).max(-1) > 0
    S0 = cv2.cvtColor(cv2.imread(str(SRC0)), cv2.COLOR_BGR2RGB).astype(np.float32)
    after = crimson(out.astype(np.float32)); before = crimson(P); orig = crimson(S0)
    info = dict(src_original=str(SRC0), src_original_md5=md5(SRC0), src_v3_ink=str(SRC), src_v3_ink_md5=md5(SRC), out=str(OUT), out_md5=md5(OUT),
                table_box=TABLE_BOX, changed_px_vs_v3_ink=int(ch.sum()), changed_px_outside_table_box=int((ch & (box == 0)).sum()),
                crimson_px_gt_0_5=dict(original=int((orig > 0.5).sum()), v3_ink=int((before > 0.5).sum()), v3b_ink=int((after > 0.5).sum())),
                crimson_px_in_table_box=dict(v3_ink=int(((before > 0.5) & (box > 0)).sum()), v3b_ink=int(((after > 0.5) & (box > 0)).sum())))
    json.dump(info, open(BR / 'logs_v3b_h04a_inkgrade.json', 'x'), indent=1); print(json.dumps(info, indent=1))
