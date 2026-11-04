# finisher: the first QC run crashed on its last step (L13 margin lookup); this assembles qc_summary.json from the files it already wrote
import json, re, hashlib, subprocess
from pathlib import Path
import numpy as np, soundfile as sf, cv2
G = Path('/workspace/posterity/standalones/germanicus'); Q = G / 'edit/qc_rough_v1'; B = G / 'edit/_build_v1'
M = Path('/workspace/posterity/renders/posterity-germanicus-ROUGH-v1.mp4')
pr = json.load(open(Q / 'ffprobe.json')); v = [s for s in pr['streams'] if s['codec_type'] == 'video'][0]; a = [s for s in pr['streams'] if s['codec_type'] == 'audio'][0]
summ = open(Q / 'loudness_ebur128.txt').read()
R = dict(master=str(M), md5=hashlib.md5(M.read_bytes()).hexdigest(),
         video=dict(codec=v['codec_name'], w=v['width'], h=v['height'], fps=v['r_frame_rate'], nb_frames=v.get('nb_frames'), pix=v['pix_fmt'], dur=float(v['duration'])),
         audio=dict(codec=a['codec_name'], sr=a['sample_rate'], ch=a['channels'], br=a.get('bit_rate'), dur=float(a['duration'])), format_duration=float(pr['format']['duration']),
         loudness=dict(I=float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)), LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU', summ).group(1)), TP=float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1))))
R['edge'] = json.load(open(Q / 'edge_check.json'))['summary']
R['person_audit'] = {k: {kk: vv for kk, vv in d.items() if kk != 'config'} for k, d in json.load(open(Q / 'person_mask_audit.json')).items()}
x, sr = sf.read(str(B / 'audio/bed_ridden.wav')); x = x.mean(1) if x.ndim > 1 else x
db = lambda a, b: 20 * np.log10(np.sqrt((x[int(a * sr):int(b * sr)] ** 2).mean()) + 1e-9)
e = [db(t, t + .02) for t in np.arange(62.6, 63.4, .02)]; i = int(np.argmax(np.diff(e)))
words = json.load(open(B / 'vo_words.json'))['words']; but = [w for w in words if w['line'] == 13][0]
R['hit'] = dict(bed_rise_at_s=round(62.6 + .02 * (i + 1), 3), rise_db=round(float(np.diff(e)[i]), 1), but_onset_s=but['start'], bed_pre_db=round(db(62.0, 62.9), 1), bed_post_db=round(db(63.0, 63.9), 1))
am = json.load(open(B / 'audio/audio_meta.json')); R['L13_key_margins'] = [m for m in am['key_word_margins_post_limiter'] if m[2] >= 62.9]
R['vo_over_bed_LU'] = am['vo_over_bed_LU']; R['key_word_min_margin_db'] = am['key_word_min_margin_db_post_limiter']
p = Q / 'qc_summary.json'; assert not p.exists(); json.dump(R, open(p, 'x'), indent=1); print(json.dumps({k: R[k] for k in ('md5','video','audio','format_duration','loudness','edge','hit','L13_key_margins')}, indent=1))
