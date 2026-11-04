#!/usr/bin/env python3
"""QC for posterity-germanicus-ROUGH-v1 -> edit/qc_rough_v1/ (never overwrites; new names only)."""
import json, subprocess, hashlib, re, sys, importlib.util
from pathlib import Path
import numpy as np, cv2
G = Path('/workspace/posterity/standalones/germanicus'); Q = G / 'edit/qc_rough_v1'; Q.mkdir(exist_ok=True)
M = Path('/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4'); B = G / 'edit/_build_v1'
TL = json.load(open(B / 'timeline.json')); FPS = 30
def new(p):
    p = Path(p)
    if p.exists(): raise SystemExit(f'exists: {p}')
    return p
def wjson(name, d): json.dump(d, open(new(Q / name), 'x'), indent=1, default=float)
R = {}
# --- ffprobe / md5 / loudness
R['md5'] = hashlib.md5(M.read_bytes()).hexdigest()
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(M)], capture_output=True, text=True).stdout)
open(new(Q / 'ffprobe.json'), 'x').write(json.dumps(pr, indent=1))
v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in pr['streams'] if s['codec_type'] == 'audio'][0]
R['video'] = dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], nb_frames=v.get('nb_frames'), pix=v['pix_fmt'], dur=float(v['duration']))
R['audio'] = dict(codec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'], br=a.get('bit_rate'), dur=float(a['duration']))
R['format_duration'] = float(pr['format']['duration'])
lo = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(M), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = lo[lo.rfind('Summary:'):]
open(new(Q / 'loudness_ebur128.txt'), 'x').write(summ)
R['loudness'] = dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', summ).group(1)),
                     TP=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1)))
# --- decode master
cap = cv2.VideoCapture(str(M)); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
N = len(frames); R['decoded_frames'] = N
# --- frames per plate (in / mid / out) + 360x640 contact sheet
fdir = Q / 'frames'; fdir.mkdir(exist_ok=True); tiles = []
for s in TL['segments']:
    for tag, fi in (('in', s['f0']), ('mid', (s['f0'] + s['f1']) // 2), ('out', s['f1'] - 1)):
        cv2.imwrite(str(new(fdir / f"{s['id']}_{tag}_f{fi:04d}.jpg")), frames[fi], [cv2.IMWRITE_JPEG_QUALITY, 92])
    t = cv2.resize(frames[(s['f0'] + s['f1']) // 2], (360, 640), interpolation=cv2.INTER_AREA)
    cv2.putText(t, f"{s['id']} {s['start']:.2f}-{s['end']:.2f}", (8, 630), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA); tiles.append(t)
while len(tiles) % 7: tiles.append(np.zeros_like(tiles[0]))
sheet = np.vstack([np.hstack(tiles[i:i + 7]) for i in range(0, len(tiles), 7)])
cv2.imwrite(str(new(Q / 'contact_sheet_360x640.jpg')), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
# overlays at 360x640 (title, credit, IR)
ov = [frames[f] for f in (45, 75, 180 + 60, 1280 + 60, 1755 + 50)]
cv2.imwrite(str(new(Q / 'overlays_360x640.jpg')), np.hstack([cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA) for f in ov]), [cv2.IMWRITE_JPEG_QUALITY, 90])
# --- edge / blank check
edge = []; bad = []
for i in range(0, N):
    g = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = dict(f=i, top=float(g[:6].mean()), bot=float(g[-6:].mean()), left=float(g[:, :6].mean()), right=float(g[:, -6:].mean()), mean=float(g.mean()))
    if i % 15 == 0: edge.append(e)
    if min(e['top'], e['bot'], e['left'], e['right']) < 4.0 or e['mean'] < 6.0: bad.append(e)
R['edge'] = dict(min_edge_luma=min(min(x['top'], x['bot'], x['left'], x['right']) for x in edge), first_frame_mean=float(cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY).mean()),
                 last_frame_mean=float(cv2.cvtColor(frames[-1], cv2.COLOR_BGR2GRAY).mean()), frames_flagged=len(bad), flagged=bad[:20])
wjson('edge_check.json', dict(summary=R['edge'], samples=edge))
cor = []
for s in TL['segments']:
    f = frames[(s['f0'] + s['f1']) // 2]; c = 220
    cor.append(np.hstack([f[:c, :c], f[:c, -c:], f[-c:, :c], f[-c:, -c:]]))
cv2.imwrite(str(new(Q / 'edge_corners_watermark_check.jpg')), np.vstack(cor), [cv2.IMWRITE_JPEG_QUALITY, 88])
# --- person-mask zero-displacement audit + candle luma swing at 360x640, every animated plate over its full on-screen duration
sp = importlib.util.spec_from_file_location('mm', str(G / 'edit/make_masks_germanicus_v1b.py')); mm = importlib.util.module_from_spec(sp); sp.loader.exec_module(mm); b3 = mm.MM_engine()
aud = {}
for s in TL['segments']:
    if not s.get('b3'): continue
    cfg = json.load(open(s['b3'])); E = b3.Engine(cfg); pers = cv2.imread(cfg['derived_from']['persons_mask'], 0) > 0
    sc = 640.0 / E.plate.shape[0]; small = lambda im: cv2.resize(im.astype(np.float32), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    allow_s = small(E.allow.astype(np.float32)) > 0.05; lum = []; rows = []
    for k in range(0, s['frames'], 2):
        t = k / FPS; img, dx, dy = E.render(float(t)); d = np.abs(dx) + np.abs(dy); diff = np.abs(img - E.plate).max(2)
        rows.append(dict(t=round(t, 3), person_disp_max=float(d[pers].max()) if pers.any() else 0.0, protect_disp_max=float(d[E.protect].max()) if E.protect.any() else 0.0,
                         outside_allow_change_max=float(diff[~E.allow].max()), disp_max=float(d.max())))
        y = small(img).mean(2); lum.append(y[allow_s])
    L = np.array(lum); sw = L.max(0) - L.min(0)
    aud[s['id']] = dict(config=s['b3'], persons_px=int(pers.sum()), samples=len(rows), seconds=s['duration'],
                        person_disp_max=max(r['person_disp_max'] for r in rows), protect_disp_max=max(r['protect_disp_max'] for r in rows),
                        outside_allow_change_max=max(r['outside_allow_change_max'] for r in rows), disp_max=max(r['disp_max'] for r in rows),
                        luma_swing_360x640_p95=float(np.percentile(sw, 95)), luma_swing_360x640_max=float(sw.max()),
                        ok=all(r['person_disp_max'] == 0 and r['protect_disp_max'] == 0 and r['outside_allow_change_max'] == 0 for r in rows))
    print(s['id'], aud[s['id']])
R['person_audit'] = {k: {kk: vv for kk, vv in v.items() if kk != 'config'} for k, v in aud.items()}
wjson('person_mask_audit.json', aud)
# --- hit timing (bed stem) + L13 margin
import soundfile as sf
x, sr = sf.read(str(B / 'audio/bed_ridden.wav')); x = x.mean(1) if x.ndim > 1 else x
db = lambda a, b: 20 * np.log10(np.sqrt((x[int(a * sr):int(b * sr)] ** 2).mean()) + 1e-9)
e = [db(t, t + .02) for t in np.arange(62.6, 63.4, .02)]; i = int(np.argmax(np.diff(e)))
words = json.load(open(B / 'vo_words.json'))['words']; but = [w for w in words if w['line'] == 13][0]
R['hit'] = dict(bed_rise_at_s=round(62.6 + .02 * (i + 1), 3), rise_db=round(float(np.diff(e)[i]), 1), but_onset_s=but['start'],
                bed_pre_db=round(db(62.0, 62.9), 1), bed_post_db=round(db(63.0, 63.9), 1))
am = json.load(open(B / 'audio/audio_meta.json'))
R['L13_key_margins'] = [m for m in am['key_word_margins_post_limiter'] if m[2] >= 62.9]
wjson('qc_summary.json', R); print(json.dumps({k: R[k] for k in ('md5', 'video', 'audio', 'loudness', 'edge', 'hit', 'L13_key_margins')}, indent=1, default=float))
