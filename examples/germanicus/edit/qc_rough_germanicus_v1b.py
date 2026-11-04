#!/usr/bin/env python3
"""QC for posterity-germanicus-ROUGH-v1b -> edit/qc_rough_v1b/ (never overwrites; new names only). Adapted from qc_rough_germanicus_v1.py (untouched);
adds the 1A title frame check, the L13 VO-vs-bed plot/margins and fixes the v1 L13-margin lookup crash."""
import json, subprocess, hashlib, re, sys, importlib.util
from pathlib import Path
import numpy as np, cv2
G = Path('/workspace/posterity/standalones/germanicus'); Q = G / 'edit/qc_rough_v1b'; Q.mkdir(exist_ok=True)
M = Path('/workspace/posterity/renders/posterity-germanicus-ROUGH-v1b.mp4'); B = G / 'edit/_build_v1b'
TL = json.load(open(B / 'timeline.json')); FPS = 30
def new(p):
    p = Path(p)
    if p.exists(): raise SystemExit(f'exists: {p}')
    return p
def wjson(name, d):
    if (Q / name).exists() and name in RESUME_OK: return
    json.dump(d, open(new(Q / name), 'x'), indent=1, default=float)
RESUME_OK = {'edge_check.json', 'person_mask_audit.json'}
def imw(p, img, *a):
    p = Path(p)
    if p.exists() and (p.parent == Q / 'frames' or p.name in ('contact_sheet_360x640.jpg', 'overlays_360x640.jpg', 'edge_corners_watermark_check.jpg')): return True
    return cv2.imwrite(str(new(p)), img, *a)
def txtw(p, t):
    p = Path(p)
    if p.exists() and p.name in ('ffprobe.json', 'loudness_ebur128.txt'): return
    open(new(p), 'x').write(t)
R = {}
# --- ffprobe / md5 / loudness
R['md5'] = hashlib.md5(M.read_bytes()).hexdigest()
pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(M)], capture_output=True, text=True).stdout)
txtw(Q / 'ffprobe.json', json.dumps(pr, indent=1))
v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in pr['streams'] if s['codec_type'] == 'audio'][0]
R['video'] = dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], nb_frames=v.get('nb_frames'), pix=v['pix_fmt'], dur=float(v['duration']))
R['audio'] = dict(codec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'], br=a.get('bit_rate'), dur=float(a['duration']))
R['format_duration'] = float(pr['format']['duration'])
lo = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(M), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = lo[lo.rfind('Summary:'):]
txtw(Q / 'loudness_ebur128.txt', summ)
R['loudness'] = dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', summ).group(1)),
                     TP=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1)))
# --- decode master
need = {30, 45, 60, 75, 180 + 60, 1280 + 60, 1755 + 50}
for s_ in TL['segments']: need |= {s_['f0'], (s_['f0'] + s_['f1']) // 2, s_['f1'] - 1}
cap = cv2.VideoCapture(str(M)); frames = {}; edge = []; bad = []; i = 0
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
    e = dict(f=i, top=float(g[:6].mean()), bot=float(g[-6:].mean()), left=float(g[:, :6].mean()), right=float(g[:, -6:].mean()), mean=float(g.mean()))
    if i % 15 == 0: edge.append(e)
    if min(e['top'], e['bot'], e['left'], e['right']) < 4.0 or e['mean'] < 6.0: bad.append(e)
    if i == 0: first_mean = e['mean']
    last_mean = e['mean']
    if i in need: frames[i] = f
    i += 1
N = i; R['decoded_frames'] = N
# --- frames per plate (in / mid / out) + 360x640 contact sheet
fdir = Q / 'frames'; fdir.mkdir(exist_ok=True); tiles = []
for s in TL['segments']:
    for tag, fi in (('in', s['f0']), ('mid', (s['f0'] + s['f1']) // 2), ('out', s['f1'] - 1)):
        imw(fdir / f"{s['id']}_{tag}_f{fi:04d}.jpg", frames[fi], [cv2.IMWRITE_JPEG_QUALITY, 92])
    t = cv2.resize(frames[(s['f0'] + s['f1']) // 2], (360, 640), interpolation=cv2.INTER_AREA)
    cv2.putText(t, f"{s['id']} {s['start']:.2f}-{s['end']:.2f}", (8, 630), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA); tiles.append(t)
while len(tiles) % 7: tiles.append(np.zeros_like(tiles[0]))
sheet = np.vstack([np.hstack(tiles[i:i + 7]) for i in range(0, len(tiles), 7)])
imw(Q / 'contact_sheet_360x640.jpg', sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])
# overlays at 360x640 (title, credit, IR)
ov = [frames[f] for f in (45, 75, 180 + 60, 1280 + 60, 1755 + 50)]
imw(Q / 'overlays_360x640.jpg', np.hstack([cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA) for f in ov]), [cv2.IMWRITE_JPEG_QUALITY, 90])
# --- edge / blank check
R['edge'] = dict(min_edge_luma=min(min(x['top'], x['bot'], x['left'], x['right']) for x in edge), first_frame_mean=first_mean,
                 last_frame_mean=last_mean, frames_flagged=len(bad), flagged=bad[:20])
wjson('edge_check.json', dict(summary=R['edge'], samples=edge))
cor = []
for s in TL['segments']:
    f = frames[(s['f0'] + s['f1']) // 2]; c = 220
    cor.append(np.hstack([f[:c, :c], f[:c, -c:], f[-c:, :c], f[-c:, -c:]]))
imw(Q / 'edge_corners_watermark_check.jpg', np.vstack(cor), [cv2.IMWRITE_JPEG_QUALITY, 88])
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
# --- 1A title frames: 1080 + 360x640, measured text block (ivory pixels, x>=150, y<600)
tdir = Q / 'title_1A'; tdir.mkdir(exist_ok=True); tb = {}
for fi in (30, 45, 60, 75):
    f = frames[fi]; imw(tdir / f'1A_title_f{fi:04d}_1080x1920.png', f)
    imw(tdir / f'1A_title_f{fi:04d}_360x640.png', cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA))
    im = f.astype(int); m = (im[..., 2] > 215) & (im[..., 1] > 205) & (im[..., 0] > 185); m[:, :150] = 0; m[600:] = 0
    ys = np.where(m.any(1))[0]; xs = np.where(m.any(0))[0]
    tb[fi] = dict(text_top_px=int(ys.min()), text_bottom_px=int(ys.max()), text_left_px=int(xs.min()), text_right_px=int(xs.max()))
g = cv2.resize(frames[60], (360, 640), interpolation=cv2.INTER_AREA).copy()
for y in (270, tb[60]['text_top_px'], tb[60]['text_bottom_px']): cv2.line(g, (0, round(y / 3)), (359, round(y / 3)), (0, 255, 255) if y == 270 else (0, 255, 0), 1)
cv2.putText(g, '270px', (300, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
imw(tdir / '1A_title_f0060_360x640_guides.png', g)
R['title_1A'] = dict(measured=tb, text_top_ok_ge_270=all(v['text_top_px'] >= 270 for v in tb.values()), v1_measured=dict(text_top_px=288, text_bottom_px=434))
# --- L13: margins from audio_meta (post-limiter stems) + plot VO vs bed
import soundfile as sf
am = json.load(open(B / 'audio/audio_meta.json')); words = json.load(open(B / 'vo_words.json'))['words']
R['L13_lift'] = {k: am['v1b_l13_lift'][k] for k in ('lift_db', 'up_ramp', 'hold_to', 'down_ramp_to', 'depth_db_during_hold', 'word_band_margins_1_4k_post_limiter')}
R['speech_dip'] = am['v1b_speech_dip']; R['key_word_min_margin_db_ex_L13'] = am['key_word_min_margin_db_post_limiter']; R['vo_over_bed_LU'] = am['vo_over_bed_LU']
from scipy.signal import butter, sosfiltfilt
vL, sr = sf.read(str(B / 'audio/stem_vo_postlim.wav')); bL, _ = sf.read(str(B / 'audio/stem_bed_postlim.wav'))
sos = butter(4, [1000, 4000], 'bandpass', fs=sr, output='sos'); vb = sosfiltfilt(sos, vL); bbp = (sosfiltfilt(sos, bL, axis=0) ** 2).mean(1)
sos2 = butter(4, [300, 1000], 'bandpass', fs=sr, output='sos'); vb2 = sosfiltfilt(sos2, vL); bbp2 = (sosfiltfilt(sos2, bL, axis=0) ** 2).mean(1)
dB = lambda p: 10 * np.log10(p + 1e-20)
war = [w for w in words if w['word'] == 'war.'][0]; a_, z_ = int(war['start'] * sr), int(war['end'] * sr)
R['war_low_band_note'] = dict(word='war.', margin_300_1000Hz_db=round(float(dB((vb2[a_:z_] ** 2).mean()) - dB(bbp2[a_:z_].mean())), 2),
                              margin_1_4kHz_db=round(float(dB((vb[a_:z_] ** 2).mean()) - dB(bbp[a_:z_].mean())), 2))
bfull = bL.mean(1); hop = int(0.02 * sr); n = len(vL) // hop
fr = lambda x: dB((x[:n * hop] ** 2).reshape(n, hop).mean(1)); tt = np.arange(n) * 0.02
bed_full_db = fr(bfull); bed_band_db = dB(bbp[:n * hop].reshape(n, hop).mean(1)); vo_band_db = fr(vb)
e = bed_full_db[(tt >= 62.6) & (tt < 63.4)]; d = np.diff(e); i = int(np.argmax(d))
but = [w for w in words if w['line'] == 13][0]
seg = lambda a, b: float(dB((bfull[int(a * sr):int(b * sr)] ** 2).mean()))
R['hit'] = dict(bed_rise_at_s=round(62.6 + 0.02 * (i + 1), 3), rise_db_20ms=round(float(d[i]), 1), but_onset_s=but['start'], bed_rms_62_0_62_7_db=round(seg(62.0, 62.7), 1),
                bed_rms_63_0_63_9_db=round(seg(63.0, 63.9), 1), bed_rms_64_1_65_0_hold_db=round(seg(64.1, 65.0), 1))
gc = np.load(B / 'audio/bed_gain_curve_db.npy'); gv1 = np.load(B / 'audio/bed_gain_curve_v1_db.npy')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(3, 1, figsize=(14, 10), sharex=True); w0, w1 = 60.5, 68.6; mk = (tt >= w0) & (tt <= w1)
ta = np.arange(len(vL)) / sr; ms = (ta >= w0) & (ta <= w1)
ax[0].plot(ta[ms][::8], vL[ms][::8], lw=.4, color='tab:blue', label='VO (post-limiter stem)'); ax[0].plot(ta[ms][::8], bfull[ms][::8], lw=.4, color='tab:red', alpha=.7, label='bed (post-limiter stem, L/R mean)')
ax[0].set_ylabel('amplitude'); ax[0].legend(loc='upper right'); ax[0].set_title('Germanicus ROUGH v1b: L13 "But not for murder." VO vs bed')
ax[1].plot(tt[mk], vo_band_db[mk], color='tab:blue', label='VO 1-4 kHz (20 ms)'); ax[1].plot(tt[mk], bed_band_db[mk], color='tab:red', label='bed 1-4 kHz (20 ms)'); ax[1].plot(tt[mk], bed_full_db[mk], color='tab:orange', lw=.8, label='bed full-band (20 ms)')
ax[1].set_ylim(-90, -5); ax[1].set_ylabel('dBFS'); ax[1].legend(loc='lower left')
taa = np.arange(len(gc)) / sr; mg = (taa >= w0) & (taa <= w1)
ax[2].plot(taa[mg][::48], gv1[mg][::48], color='grey', ls='--', label='v1 bed gain (duck+fade)'); ax[2].plot(taa[mg][::48], gc[mg][::48], color='k', label='v1b bed gain (duck+lift+fade)')
ax[2].set_ylim(-35, 3); ax[2].set_ylabel('dB'); ax[2].set_xlabel('s'); ax[2].legend(loc='lower left')
for w in words:
    if w['line'] >= 12 and w['start'] >= w0:
        for a in ax: a.axvspan(w['start'], w['end'], color='tab:green' if w['line'] == 13 else 'lightgrey', alpha=.12)
        ax[1].text((w['start'] + w['end']) / 2, -12, w['word'], ha='center', fontsize=8)
for r in R['L13_lift']['word_band_margins_1_4k_post_limiter']:
    ax[1].text(r[2], -20, f'{r[3]:+.1f} dB', fontsize=8, color='darkgreen')
for a in ax: a.axvline(63.0, color='purple', lw=.8, ls=':')
fig.tight_layout(); fig.savefig(str(new(Q / 'L13_vo_vs_bed_levels.png')), dpi=110)
wjson('qc_summary.json', R); print(json.dumps({k: R[k] for k in ('md5', 'video', 'audio', 'loudness', 'edge', 'hit', 'title_1A', 'L13_lift', 'war_low_band_note')}, indent=1, default=float))
