#!/workspace/mpvenv/bin/python
"""P06 v4 proof (directive 12): FLAT push 1.00->1.04 + water_v1 glints ONLY inside the hand-traced sea/lagoon mask.
Uses the rough_v4 builder's Beat('P06') (same code path as the rough). Writes mask PNGs, overlay, leak check, proof mp4 (CRF 18), grabs."""
import sys, json, hashlib, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
OUT = Path(__file__).resolve().parent; BJ = OUT.parents[1]
s = importlib.util.spec_from_file_location('bv4', str(BJ / 'rough_v4/build/build_bjorn_rough_v4.py')); BV = importlib.util.module_from_spec(s); s.loader.exec_module(BV)
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
PLATE = BJ / 'plates/P06_KEEP.png'; pm0 = md5(PLATE)
b = BV.Beat('P06'); ws = b.water; H, W = b.H, b.W
water = ws.water; allow = ~ws.protect
hast = BV.WA.poly((H, W), [BV.P06_HASTEIN]) if hasattr(BV.WA, 'poly') else None
from PIL import Image, ImageDraw
def pmask(polys):
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    for p in polys: d.polygon([tuple(map(float, q)) for q in p], fill=255)
    return np.asarray(im) > 0
hast = pmask([BV.P06_HASTEIN]); rail = pmask([BV.P06_RAIL]); faces = b.face_hard
(OUT / 'masks').mkdir(exist_ok=True)
for n, m in dict(water=water, allow=allow, hastein=hast, rail=rail).items(): cv2.imwrite(str(OUT / f'masks/p06_mask_{n}.png'), m.astype(np.uint8) * 255)
o = b.P.copy().astype(np.float32); o[water] = o[water] * 0.5 + np.float32([60, 200, 255]) * 0.5; o[hast] = o[hast] * 0.55 + np.float32([255, 60, 60]) * 0.45; o[rail] = o[rail] * 0.55 + np.float32([255, 200, 0]) * 0.45
cv2.imwrite(str(OUT / 'p06_mask_overlay.png'), cv2.cvtColor(o.astype(np.uint8), cv2.COLOR_RGB2BGR))
# leak check over every 5th frame (plate space) + output-space check inside the warped Hastein mask
rep = dict(plate=str(PLATE), plate_md5=pm0, frames=b.n, seconds=round(b.n / BV.FPS, 3), push=list(b.c['push']), water_px=int(water.sum()), water_info=b.log.get('water'),
           density_max=b.log.get('density_max'), guard=b.log.get('guard_density'), faces=b.faces,
           changed_px_outside_water=[], changed_px_in_hastein=[], changed_px_in_rail=[], changed_px_in_water=[], out_changed_px_in_hastein_eroded5=[])
peak = (0, -1)
for i in range(0, b.n, 5):
    f = b.plate_comp(i / BV.FPS); ch = np.abs(f.astype(int) - b.P.astype(int)).max(-1) > 0
    rep['changed_px_outside_water'].append(int((ch & ~water).sum())); rep['changed_px_in_hastein'].append(int((ch & hast).sum()))
    rep['changed_px_in_rail'].append(int((ch & rail).sum())); rep['changed_px_in_water'].append(int((ch & water).sum()))
    if (ch & water).sum() > peak[0]: peak = (int((ch & water).sum()), i)
    A = b.cam_flat(i); fr = BV.warp_out(f, A); ref = BV.warp_out(b.P, A)
    mo = cv2.warpAffine(hast.astype(np.uint8) * 255, A, (BV.OW, BV.OH), flags=cv2.INTER_NEAREST) > 0; mo = cv2.erode(mo.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
    rep['out_changed_px_in_hastein_eroded5'].append(int(((np.abs(fr.astype(int) - ref.astype(int)).max(-1) > 0) & mo).sum()))
rep['pass'] = max(rep['changed_px_outside_water']) == 0 and max(rep['changed_px_in_hastein']) == 0 and max(rep['out_changed_px_in_hastein_eroded5']) == 0
rep['peak_glint_frame'] = peak[1]
mp4 = OUT / 'p06_proof.mp4'; assert not mp4.exists()
p = subprocess.Popen(['ffmpeg', '-n', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{BV.OW}x{BV.OH}', '-r', '30', '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', str(mp4)], stdin=subprocess.PIPE)
for i in range(b.n):
    fr = b.render_frame(i); p.stdin.write(np.ascontiguousarray(fr).tobytes())
    if i in (0, peak[1], b.n - 1): cv2.imwrite(str(OUT / f'p06_proof_f{i:03d}.png'), cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
p.stdin.close(); assert p.wait() == 0
assert md5(PLATE) == pm0; rep['proof'] = dict(path=str(mp4), md5=md5(mp4))
json.dump(rep, open(OUT / 'p06_proof_report.json', 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in rep.items() if not isinstance(v, list) or len(v) < 8}, default=str)[:2500])
print('max outside', max(rep['changed_px_outside_water']), 'hastein', max(rep['changed_px_in_hastein']), 'rail', max(rep['changed_px_in_rail']), 'out', max(rep['out_changed_px_in_hastein_eroded5']))
