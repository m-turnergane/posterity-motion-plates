#!/usr/bin/env python3
"""QC for posterity-germanicus-ROUGH-v1c -> edit/qc_rough_v1c/ (streams frames; never overwrites). Adapted from qc_rough_germanicus_v1b.py (untouched).
Adds: IR tag presence/absence per plate (+1B credit/tag clearance), 7B route-(i) frames vs native plate, plate-10 lettering before/after,
bed constancy over L13/outro, first-6 s bed level, 1-4 kHz frame masking stats, plate in/out table."""
import json, subprocess, hashlib, re, importlib.util
from pathlib import Path
import numpy as np, cv2, soundfile as sf
from scipy.signal import butter, sosfiltfilt
G = Path('/workspace/posterity/standalones/germanicus'); Q = G / 'edit/qc_rough_v1c'; Q.mkdir(exist_ok=True)
M = Path('/workspace/posterity/renders/posterity-germanicus-ROUGH-v1c.mp4'); B = G / 'edit/_build_v1c'
META = json.load(open(B / 'rough_meta.json')); SEGS = META['segments']; FPS = 30
def new(p):
    p = Path(p)
    if p.exists(): raise SystemExit(f'exists: {p}')
    return p
def imw(p, img, *a):
    if Path(p).exists(): return True   # resume after the 7B audit crash: keep the first run's identical frame files
    return cv2.imwrite(str(new(p)), img, *a)
R = {'master': str(M), 'md5': hashlib.md5(M.read_bytes()).hexdigest()}
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(M)], capture_output=True, text=True).stdout)
(Q / 'ffprobe.json').exists() or open(new(Q / 'ffprobe.json'), 'x').write(json.dumps(pr, indent=1))
v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in pr['streams'] if s['codec_type'] == 'audio'][0]
R['video'] = dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], nb_frames=v.get('nb_frames'), pix=v['pix_fmt'], dur=float(v['duration']))
R['audio'] = dict(codec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'], dur=float(a['duration'])); R['format_duration'] = float(pr['format']['duration'])
lo = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(M), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = lo[lo.rfind('Summary:'):]; (Q / 'loudness_ebur128.txt').exists() or open(new(Q / 'loudness_ebur128.txt'), 'x').write(summ)
R['loudness'] = dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', summ).group(1)),
                     TP=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1)))
# plate in/out table
R['plates'] = [dict(id=s['id'], plate=Path(s['plate']).name, f_in=s['f0'], f_out=s['f1'], t_in=round(s['start'], 3), t_out=round(s['end'], 3), dur_s=round(s['duration'], 3),
                    first_word=s.get('first_word'), ir_tag=s['id'] in META['ir_tag'].get('_segs', []) if False else None, push=[s['z_start'], s['z_end']], anchor=s['anchor'],
                    candle=bool(s.get('b3'))) for s in SEGS]
IR_SEGS = ("1B", "2", "3", "4", "6", "7A", "7B", "8", "9B")
for r in R['plates']: r['ir_tag'] = r['id'] in IR_SEGS
R['all_ge_3s'] = all(r['dur_s'] >= 3.0 for r in R['plates'])
# stream decode
need = {45, 60, 75}
for s in SEGS: need |= {s['f0'], (s['f0'] + s['f1']) // 2, s['f1'] - 1, s['f0'] + 30}
cap = cv2.VideoCapture(str(M)); frames = {}; i = 0; bad = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if f.mean() < 6: bad += 1
    if i in need: frames[i] = f
    i += 1
R['decoded_frames'] = i; R['near_black_frames'] = bad
fdir = Q / 'frames'; fdir.mkdir(exist_ok=True); tiles = []
for s in SEGS:
    mid = (s['f0'] + s['f1']) // 2
    for tag, fi in (('in', s['f0']), ('mid', mid), ('out', s['f1'] - 1)): imw(fdir / f"{s['id']}_{tag}_f{fi:04d}.jpg", frames[fi], [cv2.IMWRITE_JPEG_QUALITY, 92])
    t = cv2.resize(frames[mid], (360, 640), interpolation=cv2.INTER_AREA)
    cv2.putText(t, f"{s['id']} {s['start']:.2f}-{s['end']:.2f}{' IR' if s['id'] in IR_SEGS else ''}", (8, 630), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA); tiles.append(t)
while len(tiles) % 7: tiles.append(np.zeros_like(tiles[0]))
imw(Q / 'contact_sheet_360x640.jpg', np.vstack([np.hstack(tiles[k:k + 7]) for k in range(0, len(tiles), 7)]), [cv2.IMWRITE_JPEG_QUALITY, 88])
# IR tag presence: ivory glyph pixels inside the tag band at in+30 frames (tag fully faded in)
def ivory(f, y0, y1):
    im = f[y0:y1, 150:930].astype(int); return int(((im[..., 2] > 215) & (im[..., 1] > 205) & (im[..., 0] > 185)).sum())
plate_ref = {}
tagrows = []
for s in SEGS:
    fi = s['f0'] + 30; y = 384 if s['id'] == '1B' else 296
    tagrows.append(dict(id=s['id'], frame=fi, expected=s['id'] in IR_SEGS, ivory_px_tag_band=ivory(frames[fi], y + 4, y + 36)))
R['ir_tag_check'] = tagrows
tags = [cv2.resize(frames[s['f0'] + 30], (360, 640), interpolation=cv2.INTER_AREA) for s in SEGS]
imw(Q / 'tags_all_plates_360x640.jpg', np.vstack([np.hstack(tags[:7]), np.hstack(tags[7:14])]), [cv2.IMWRITE_JPEG_QUALITY, 88])
f1b = [s for s in SEGS if s['id'] == '1B'][0]['f0'] + 30
imw(Q / '1B_credit_and_tag_1080x1920.png', frames[f1b]); imw(Q / '1B_credit_and_tag_crop.png', frames[f1b][250:480, 100:980])
im = frames[f1b][250:500].astype(int); mk1 = (im[..., 2] > 215) & (im[..., 1] > 205) & (im[..., 0] > 185); rows = np.where(mk1.sum(1) > 2)[0] + 250
runs = np.split(rows, np.where(np.diff(rows) > 4)[0] + 1); bx = []
for r_ in runs:
    xs = np.where(mk1[r_[0] - 250:r_[-1] - 249].any(0))[0]; bx.append(dict(y0=int(r_[0]), y1=int(r_[-1]), x0=int(xs.min()), x1=int(xs.max())))
R['1B_text_runs_measured'] = bx; R['1B_text_clearance_px'] = (bx[1]['y0'] - bx[0]['y1']) if len(bx) >= 2 else None
# 7B route (i)
s7 = [s for s in SEGS if s['id'] == '7B'][0]
for fi in (s7['f0'] + 30, (s7['f0'] + s7['f1']) // 2, s7['f1'] - 1): imw(Q / f'7B_route_i_f{fi:04d}.png', frames[fi])
src = cv2.imread(str(G / 'plates-owner/seq7b.png')); box = src.copy(); cv2.rectangle(box, (0, 900), (434, 1671), (0, 255, 255), 4)
imw(Q / '7B_source_plate_with_crop_box.jpg', cv2.resize(box, (470, 836)), [cv2.IMWRITE_JPEG_QUALITY, 90])
der = cv2.imread(str(G / 'plates-derived/seq7b_lowerleft_v1c.png'))
nat = cv2.resize(src[1080:1300, 100:320], (540, 540), interpolation=cv2.INTER_NEAREST)
up = cv2.resize(der[int((1080 - 900) * 2.4885):int((1080 - 900) * 2.4885) + 540, int(100 * 2.4885):int(100 * 2.4885) + 540], (540, 540))
imw(Q / '7B_lamp_native_nearestx2.5_vs_derived_1to1.png', np.hstack([nat, up]))
# plate 10 before/after (plate level, 1:1) + video frame
p0 = cv2.imread(str(G / 'plates-owner/seq10.png')); p1 = cv2.imread(str(G / 'plates-derived/seq10_softcaps_v1c.png'))
for nm, (y0, x0) in (('topleft', (250, 60)), ('centre', (520, 380)), ('right', (520, 640))):
    imw(Q / f'10_lettering_before_after_{nm}_1to1.png', np.hstack([p0[y0:y0 + 360, x0:x0 + 300], p1[y0:y0 + 360, x0:x0 + 300]]))
mk = cv2.imread(str(G / 'masks/v1c/G10_lettering_mask_v1c.png'), 0)
ovl = p0.copy(); ovl[mk > 0] = (ovl[mk > 0] * 0.5 + np.array([255, 0, 255]) * 0.5).astype(np.uint8)
imw(Q / '10_lettering_mask_overlay.jpg', ovl, [cv2.IMWRITE_JPEG_QUALITY, 90])
R['plate10'] = json.load(open(G / 'masks/v1c/G10_softcaps_v1c.json'))
# person audit (all animated plates, full on-screen duration, every 2nd frame)
sp = importlib.util.spec_from_file_location('mm', str(G / 'edit/make_masks_germanicus_v1b.py')); mm = importlib.util.module_from_spec(sp); sp.loader.exec_module(mm); b3 = mm.MM_engine()
aud = {}
for s in SEGS:
    if not s.get('b3'): continue
    cfg = json.load(open(s['b3'])); E = b3.Engine(cfg); pers = cv2.imread(cfg['derived_from']['persons_mask'], 0) > 0; rows = []
    for k in range(0, s['frames'], 2):
        img, dx, dy = E.render(k / FPS); d = np.abs(dx) + np.abs(dy); diff = np.abs(img - E.plate).max(2)
        rows.append((float(d[pers].max()) if pers.any() else 0.0, float(d[E.protect].max()) if E.protect.any() else 0.0, float(diff[~E.allow].max(initial=0.0)), float(d.max())))
    rr = np.array(rows); aud[s['id']] = dict(config=s['b3'], persons_px=int(pers.sum()), samples=len(rows), person_disp_max=rr[:, 0].max(), protect_disp_max=rr[:, 1].max(),
                                             outside_allow_change_max=rr[:, 2].max(), disp_max=rr[:, 3].max(), ok=bool((rr[:, :3] == 0).all()))
    print(s['id'], aud[s['id']], flush=True)
json.dump(aud, open(new(Q / 'person_mask_audit.json'), 'x'), indent=1, default=float); R['person_audit_ok'] = all(x['ok'] for x in aud.values())
# title 1A
tdir = Q / 'title_1A'; tdir.mkdir(exist_ok=True); tb = {}
for fi in (45, 60, 75):
    f = frames[fi]; imw(tdir / f'1A_title_f{fi:04d}_360x640.png', cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA))
    im = f.astype(int); m = (im[..., 2] > 215) & (im[..., 1] > 205) & (im[..., 0] > 185); m[:, :150] = 0; m[600:] = 0; ys = np.where(m.any(1))[0]
    tb[fi] = dict(text_top_px=int(ys.min()), text_bottom_px=int(ys.max()))
R['title_1A'] = tb
# audio: masking + bed constancy
am = json.load(open(B / 'audio/audio_meta.json')); words = json.load(open(B / 'vo_words.json'))['words']
R['audio_meta'] = {k: am[k] for k in ('music', 'music_md5', 'music_offset_s', 'bed_level_db', 'vo_over_bed_LU', 'mix_I', 'mix_TP', 'v1c_leveler', 'v1c_hold', 'v1c_murder', 'v1c_frames_1_4k',
                                      'frame_metric', 'key_word_min_margin_db_post_limiter', 'l13_word_band_margins_1_4k_post_limiter')}
bL, sr = sf.read(str(B / 'audio/stem_bed_postlim.wav')); bm = (bL ** 2).mean(1)
dB = lambda p: 10 * np.log10(p + 1e-20); h = int(0.25 * sr); n = len(bm) // h; lev = dB(bm[:n * h].reshape(n, h).mean(1)); tt = np.arange(n) * 0.25 + 0.125
seg = lambda a_, b_: lev[(tt >= a_) & (tt < b_)]
mid_med = float(np.median(seg(6, 61)))
R['bed_levels_250ms'] = dict(median_6_61=round(mid_med, 2), first6_max=round(float(seg(0, 6).max()), 2), first6_median=round(float(np.median(seg(2.5, 6))), 2),
                             L13_62_995_64_045_max=round(float(seg(62.995, 64.045).max()), 2), L13_min=round(float(seg(62.995, 64.045).min()), 2),
                             gap_62_18_62_995_max=round(float(seg(62.18, 62.995).max()), 2), after_murder_64_05_66_2_max=round(float(seg(64.05, 66.2).max()), 2),
                             p95_6_61=round(float(np.percentile(seg(6, 61), 95)), 2))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(14, 4)); ax.plot(tt, lev, 'r-', lw=1, label='bed post-limiter (250 ms, dBFS)')
for w in words: ax.axvspan(w['start'], w['end'], color='tab:green' if w['line'] == 13 else 'lightgrey', alpha=.25)
ax.axvline(64.045, color='k', ls=':'); ax.set_ylim(-70, -15); ax.set_xlabel('s'); ax.legend(); ax.set_title('Germanicus ROUGH v1c bed level (green = L13; dotted = end of "murder.")')
fig.tight_layout(); fig.savefig(str(new(Q / 'bed_level_timeline.png')), dpi=100)
json.dump(R, open(new(Q / 'qc_summary.json'), 'x'), indent=1, default=float)
print(json.dumps({k: R[k] for k in ('md5', 'video', 'loudness', 'all_ge_3s', 'ir_tag_check', '1B_text_clearance_px', 'person_audit_ok', 'title_1A', 'bed_levels_250ms', 'near_black_frames')}, indent=1, default=float))
