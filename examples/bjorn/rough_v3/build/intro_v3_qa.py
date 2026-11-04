#!/workspace/mpvenv/bin/python
"""QA for the intro-only proof: face/caption/glint collision vs the overlay union mask, identity of non-overlay pixels, stills."""
import json, subprocess, importlib.util, hashlib
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
ROOT = Path('/workspace/posterity'); BJ = ROOT / 'standalones/bjorn'; R3 = BJ / 'rough_v3'
s = importlib.util.spec_from_file_location('sn', str(ROOT / 'engine-rnd/snow/snow_v1b.py')); SN = importlib.util.module_from_spec(s); s.loader.exec_module(SN)
V2B = BJ / 'rough_v2/renders/bjorn_rough_v2b.mp4'; PROOF = R3 / 'renders/bjorn_v3_intro_proof_P01.mp4'
BA = ROOT / 'standalones/bathory/v3/renders/bathory_rough_v3c.mp4'; JWF = ROOT / 'standalones/jianwen/renders/posterity-jianwen-v2-FINAL-candidate-v1.mp4'
W, H = 1080, 1920; L = json.load(open(R3 / 'logs/intro_v3_log.json'))
def dec(p, n0, n1, w=W, h=H):
    b = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-vf', f'select=between(n\\,{n0}\\,{n1})', '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, h, w, 3)
A = dec(V2B, 0, 99); B = dec(PROOF, 0, 99); assert len(A) == len(B) == 100
U = np.load('/tmp/bjv3/union.npy'); Ud = cv2.dilate(U.astype(np.uint8), np.ones((17, 17), np.uint8)).astype(bool)   # +8 px guard
faces = {}
for f in (0, 30, 55, 80, 99):
    fs = SN.detect_faces(A[f], 0.6); faces[f] = [[int(x), int(y), int(x + w), int(y + h), round(float(sc), 2)] for x, y, w, h, sc in fs]
hit = []
for f, fl in faces.items():
    for x0, y0, x1, y1, sc in fl:
        hb = U[max(y0, 0):y1, max(x0, 0):x1]
        hit.append(dict(frame=f, face=[x0, y0, x1, y1], score=sc, overlay_px_on_face=int(hb.sum()), gap_px=int(min(abs(y1 - 236), abs(y0 - 382))) if not hb.any() else 0))
# caption zone: pixels that differ between A and a caption-free estimate are unknown -> locate burned caption by bright-white text rows (ivory/white, low sat) in the lower half
def cap_box(fr):
    g = fr.astype(int); m = (g.min(2) > 225) & (g.max(2) - g.min(2) < 25); m[:H // 2] = False
    ys, xs = np.nonzero(m); return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(ys) > 200 else None
caps = {f: cap_box(A[f]) for f in (20, 55, 90)}
# glint: brightest warm blob inside the coffin region (y 450-900)
def glint(fr):
    l = fr.astype(np.float32) @ np.array([.299, .587, .114], np.float32); l[:620] = 0; l[900:] = 0; l = cv2.GaussianBlur(l, (0, 0), 6)
    y, x = np.unravel_index(np.argmax(l), l.shape); m = l > l[y, x] * 0.85; ys, xs = np.nonzero(m); return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
gl = {f: glint(A[f]) for f in (0, 55, 99)}
# identity outside the overlay (guard-dilated): PSNR of proof vs v2b over frames 0..99
d = (A.astype(np.float32) - B.astype(np.float32)) ** 2
out_mse = float(d[:, ~Ud].mean()); in_mse = float(d[:, U].mean())
psnr = lambda m: float('inf') if m == 0 else 10 * np.log10(255 ** 2 / m)
f97 = [float(np.sqrt(d[f].mean())) for f in (97, 98, 99)]
q = dict(faces_yunet=faces, face_vs_overlay=hit, caption_boxes=caps, glint_boxes=gl, overlay_union_bbox=L['overlay_union_bbox_px'],
         psnr_outside_overlay_dB=round(psnr(out_mse), 2), psnr_inside_overlay_union_dB=round(psnr(in_mse), 2), rmse_f97_99=f97)
# stills
PK = 55
Image.fromarray(B[PK]).save(R3 / 'intro_peak.png')
ba = dec(BA, PK, PK)[0]; jw = dec(JWF, PK, PK)[0]
sc = 0.5; tiles = [(Image.fromarray(B[PK]), f'BJORN v3 proof f{PK}'), (Image.fromarray(ba), f'BATHORY v3c f{PK}: no intro'),
                   (Image.fromarray(jw), f'JIANWEN v2 FINAL f{PK}: source')]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
cv = Image.new('RGB', (int(W * sc) * 3 + 40, int(H * sc) + 50), (20, 20, 20)); dr = ImageDraw.Draw(cv)
for i, (im, t) in enumerate(tiles):
    x = 10 + i * (int(W * sc) + 10); cv.paste(im.resize((int(W * sc), int(H * sc)), Image.LANCZOS), (x, 45)); dr.text((x, 12), t, fill=(240, 240, 240), font=font)
cv.save(R3 / 'intro_ref_bathory_v3c.png')
q['stills'] = {p: hashlib.md5((R3 / p).read_bytes()).hexdigest() for p in ('intro_peak.png', 'intro_ref_bathory_v3c.png')}
(R3 / 'logs/intro_v3_qa.json').write_text(json.dumps(q, indent=1)); print(json.dumps(q))
# collision crop for my own review
cv2.imwrite('/tmp/bjv3/peak_top.jpg', cv2.cvtColor(cv2.resize(B[PK][:900], (540, 450)), cv2.COLOR_RGB2BGR))
for f in (20, 30, 75, 90): cv2.imwrite(f'/tmp/bjv3/pf{f}.jpg', cv2.cvtColor(cv2.resize(B[f][:900], (360, 300)), cv2.COLOR_RGB2BGR))
