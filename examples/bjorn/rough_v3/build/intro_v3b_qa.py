#!/workspace/mpvenv/bin/python
"""QA for intro proof v2: mask = rigid -28 px shift of the 16 % masks (so the search result applies), identity, captions, stills."""
import sys, json, subprocess, importlib.util, hashlib
from pathlib import Path
import numpy as np, cv2
from PIL import Image
R3 = Path('/workspace/posterity/standalones/bjorn/rough_v3'); TOP = 14.541667; DY = -28
def load(top):
    sys.argv = ['x', 'lib', '--top', str(top)]; s = importlib.util.spec_from_file_location(f'iv{top}', str(R3 / 'build/intro_v3b.py')); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
I16, IV = load(16.0), load(TOP)
M16, M = I16.masks(0, 200), IV.masks(0, 200)
assert sorted(M16) == sorted(M); rigid = all(np.array_equal(np.roll(M16[f], DY, 0), M[f]) for f in M)
A = IV.decode(IV.V2B, 200); B = IV.decode(IV.PROOF, 200); assert len(B) == 200
U = np.zeros(A.shape[1:3], bool)
for m in M.values(): U |= m
Ud = cv2.dilate(U.astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)
d = (A.astype(np.float32) - B.astype(np.float32)) ** 2
ps = lambda m: float('inf') if m == 0 else round(10 * np.log10(255 ** 2 / m), 2)
vis = sorted(M); last = vis[-1]
def cap_box(fr):
    g = fr.astype(int); m = (g.min(2) > 225) & (g.max(2) - g.min(2) < 25); m[:960] = False; ys, xs = np.nonzero(m)
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(ys) > 200 else None
caps = {f: cap_box(A[f]) for f in (20, 55, 90, 120, 160)}
q = dict(top_pct=TOP, dy_vs_16=DY, rigid_shift_verified=rigid, title_visible=[vis[0], last], union_bbox=[int(np.nonzero(U.any(0))[0].min()), int(np.nonzero(U.any(1))[0].min()), int(np.nonzero(U.any(0))[0].max()), int(np.nonzero(U.any(1))[0].max())],
         psnr_outside_overlay_f0_199=ps(float(d[:, ~Ud].mean())), psnr_outside_overlay_P01=ps(float(d[:100][:, ~Ud].mean())), psnr_outside_overlay_P02=ps(float(d[100:][:, ~Ud].mean())),
         psnr_title_free_tail=dict(frames=[last + 1, 199], psnr=ps(float(d[last + 1:].mean())), rmse_max=round(max(float(np.sqrt(d[f].mean())) for f in range(last + 1, 200)), 3)),
         captions=caps, caption_gap_px=min(c[1] for c in caps.values() if c) - int(np.nonzero(U.any(1))[0].max()))
Image.fromarray(B[55]).save(R3 / 'intro_peak_v2.png'); Image.fromarray(B[120]).save(R3 / 'intro_over_P02.png')
q['stills'] = {p: hashlib.md5((R3 / p).read_bytes()).hexdigest() for p in ('intro_peak_v2.png', 'intro_over_P02.png')}
(R3 / 'logs/intro_v3b_qa.json').write_text(json.dumps(q, indent=1)); print(json.dumps(q))
cv2.imwrite('/tmp/bjv3b/chk.jpg', cv2.cvtColor(np.hstack([cv2.resize(B[f][:800], (405, 300)) for f in (100, 142, 155, 165)]), cv2.COLOR_RGB2BGR))
