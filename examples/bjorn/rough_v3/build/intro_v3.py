#!/workspace/mpvenv/bin/python
"""Bjorn ROUGH v3 -- house title intro (Chronicle Reveal v3.2b) over P01, INTRO-ONLY PROOF.
Matched source: standalones/jianwen/edit/build_final_jianwen_v2.py (Jianwen v2 FINAL candidate, the newest 1080x1920 Short carrying the
house intro; its Chronicle Reveal block is 'Germanicus v5b, verbatim except text/position/timing'). The Jianwen code span (strike + title
maths, lines CODE_SPAN) is exec'd VERBATIM from that file (read-only; md5 logged) -- nothing re-typed.
Bathory v3c has NO title intro (checked: build has no title code; frames 0-4 s show plate + captions only), so it is NOT the source.
Input: rough_v2/renders/bjorn_rough_v2b.mp4 frames 0..99 (P01, 0-3.333 s; f100 = P02 cut = IDR keyframe in v2b). Output written with -n.
Usage: intro_v3.py proof | stills"""
import sys, json, hashlib, subprocess, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = Path('/workspace/posterity'); BJ = ROOT / 'standalones/bjorn'; R3 = BJ / 'rough_v3'
V2B = BJ / 'rough_v2/renders/bjorn_rough_v2b.mp4'; JW = ROOT / 'standalones/jianwen/edit/build_final_jianwen_v2.py'
JW_FINAL = ROOT / 'standalones/jianwen/renders/posterity-jianwen-v2-FINAL-candidate-v1.mp4'
BA_V3C = ROOT / 'standalones/bathory/v3/renders/bathory_rough_v3c.mp4'
PROOF = R3 / 'renders/bjorn_v3_intro_proof_P01.mp4'; LOG = R3 / 'logs/intro_v3_log.json'
W, H, FPS = 1080, 1920, 30; P01_F = 100            # P01 = frames 0..99; P02 cut at f100
ANCHOR = P01_F                                       # house anchor rule (Edward v3 / Jianwen grid): title clean 2 f before the next plate
TITLE = "THE KING WHO SACKED\nTHE WRONG ROME"        # house casing: all caps, two balanced lines (as Jianwen / Germanicus / Edward)
TOP_PCT = 16.0                                       # house portrait default (motion/templates build_template_v1: top 16 %); Jianwen's 7.5 is plate-specific and would sit on P01's mosaic face
FONT_PX = 78                                         # Jianwen v2 value
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
# ---- verbatim Jianwen Chronicle Reveal maths
src = JW.read_text().split('\n'); CODE_SPAN = [(197, 214), (225, 329)]   # 1-based inclusive: easing maths | strike + title. Skipped 215-224 = Jianwen's _S04/asserts/CR (replaced below)
code = '\n'.join('\n'.join(src[a - 1:b]) for a, b in CODE_SPAN)
assert src[196] == 'TITLE_LINE_H = 0.84' and src[213].startswith('    return v0') and src[224].startswith('def hexrgb') and src[328].strip() == 'return layer if any_on else None', 'span moved'
F_SEMI = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/SourceSerifPro-Semibold.ttf"
NS = dict(np=np, Image=Image, ImageDraw=ImageDraw, ImageFilter=ImageFilter, ImageFont=ImageFont, math=math, W=W, H=H, F_SEMI=F_SEMI)
_S04 = ANCHOR
NS['CR'] = dict(title=TITLE, fontSize=FONT_PX, color=(243, 237, 224), topPercent=TOP_PCT, offsetX=-16,   # = Jianwen CR dict, verbatim apart from text/top/anchor
          strokeEnterStart=8, strokeEnterEnd=26, strokeClearStart=_S04 - 23, strokeClearEnd=_S04 - 2,
          manifestStart=14, manifestEnd=42, exitStart=_S04 - 32, exitEnd=_S04 - 12, bandHeightPercent=14,
          widthPercent=94, peakOpacity=0.92, fill="#5A1A18", edge="#3A0E0C", mid="#6E2A1C",
          scaleFrom=0.92, scaleTo=1.0, exitScaleTo=0.94, settleYPx=4, afterEdgeLagFrames=2,
          letterSettleFrames=12, trackingEm=0.02, nudgeY=-4)
exec(compile(code, str(JW) + f':{CODE_SPAN}', 'exec'), NS)
CR = NS['CR']
def overlay_for(gf):   # Jianwen overlay_for minus the LEGEND layer (owner 12:59 removed LEGEND; no labels here)
    ls = [l for l in (NS['strike_layer'](gf), NS['title_layer'](gf)) if l is not None]
    if not ls: return None
    out = ls[0].copy()
    for x in ls[1:]: out.alpha_composite(x)
    return out
def decode(path, n, start=0):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vf', f'select=between(n\\,{start}\\,{start + n - 1})', '-vsync', '0',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(p, np.uint8).reshape(-1, H, W, 3)
def comp(fr, gf):
    ov = overlay_for(gf)
    if ov is None: return fr, None
    im = Image.fromarray(fr).convert('RGBA'); im.alpha_composite(ov); return np.asarray(im.convert('RGB')), np.asarray(ov)[..., 3]
def geometry():
    fs = CR['fontSize']; font = ImageFont.truetype(F_SEMI, fs); tr = CR['trackingEm'] * fs
    lw = [sum(font.getlength(c) for c in l) + tr * (len(l) - 1) for l in TITLE.split('\n')]
    bw = int(round(W * 0.94)); bh = int(round(H * 0.14)); x0 = int(round((W - bw) / 2 + CR['offsetX'])); y0 = int(round(H * TOP_PCT / 100 - bh / 2))
    return dict(line_w_px=[round(v, 1) for v in lw], line_limit_px=W * 0.92, band_px=[x0, y0, x0 + bw, y0 + bh])
def proof():
    assert not PROOF.exists(), f'{PROOF} exists (-n)'
    v2b_md5 = md5f(V2B); fr = decode(V2B, P01_F); assert fr.shape[0] == P01_F, fr.shape
    union = np.zeros((H, W), bool); per = []
    enc = subprocess.Popen(['ffmpeg', '-n', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-ss', '0', '-t', f'{P01_F / FPS:.6f}', '-i', str(V2B), '-map', '0:v', '-map', '1:a', '-c:a', 'copy',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), str(PROOF)], stdin=subprocess.PIPE)
    for gf in range(P01_F):
        out, a = comp(fr[gf], gf); enc.stdin.write(np.ascontiguousarray(out).tobytes())
        if a is not None and (a > 0).any():
            m = a > 0; union |= m; ys, xs = np.nonzero(m); per.append([gf, int(m.sum()), [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]])
        else: per.append([gf, 0, None])
    enc.stdin.close(); assert enc.wait() == 0
    ys, xs = np.nonzero(union); on = [p[0] for p in per if p[1]]
    log = dict(source=str(JW), source_md5=md5f(JW), code_span_lines=CODE_SPAN, code_span_md5=hashlib.md5(code.encode()).hexdigest(), CR=CR, title=TITLE,
               input=str(V2B), input_md5=v2b_md5, frames=P01_F, overlay_first_last_frame=[on[0], on[-1]], overlay_union_bbox_px=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
               overlay_union_mask_md5=hashlib.md5(np.packbits(union).tobytes()).hexdigest(), geometry=geometry(), per_frame=per, proof=str(PROOF), proof_md5=md5f(PROOF))
    np.save('/tmp/bjv3/union.npy', union); LOG.write_text(json.dumps(log, indent=1, default=str)); print(json.dumps({k: v for k, v in log.items() if k != 'per_frame'}, default=str))
if __name__ == '__main__':
    {'proof': proof}[sys.argv[1]]()
