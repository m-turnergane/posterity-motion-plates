#!/usr/bin/env python3
"""Germanicus v5 FINAL VO from take v5t3 (seed 37, one full-script request, never spliced).
Ending level: Oliver's natural read put L22 at +0.3 LU and L23 at -2.1 LU vs body (L01-L21). The owner wants both closing lines gently quieter (2-4 dB, intelligible),
so a static gain is applied ONLY inside silent gaps: ramp 0 -> G22 dB across the gap L21->L22, then G22 -> G23 dB across the L22->L23 pause. No edit, no time change.
Writes final-vo-oliver-germanicus-v5.wav (48k mono PCM_24), _words.json, _alignment.json (copies, timings unchanged), vo_metrics_final-v5.json. Refuses overwrite."""
import json, shutil, subprocess, numpy as np, soundfile as sf
from pathlib import Path
OUT = Path('/workspace/posterity/standalones/germanicus/vo'); TAKE = 'v5t3'; STEM = 'cand-vo-oliver-germanicus-v5t3'; FIN = 'final-vo-oliver-germanicus-v5'
G22, G23 = -3.0, -1.0
for e in ('.wav', '_words.json', '_alignment.json'):
    if (OUT / f'{FIN}{e}').exists(): raise SystemExit('refusing overwrite')
if (OUT / 'vo_metrics_final-v5.json').exists(): raise SystemExit('refusing overwrite')
W = json.load(open(OUT / f'{STEM}_words.json')); words = W['words']
x, sr = sf.read(OUT / f'{STEM}.wav', dtype='float64')
L = lambda n: [w for w in words if w['line'] == n]
a21, a22 = L(21)[-1]['end'], L(22)[0]['start']; b22, b23 = L(22)[-1]['end'], L(23)[0]['start']
# ramps sit inside the gaps, 40 ms clear of each word edge
def env_db(t):
    r1 = np.clip((t - (a21 + 0.04)) / max(0.02, (a22 - 0.04) - (a21 + 0.04)), 0, 1); r2 = np.clip((t - (b22 + 0.04)) / max(0.02, (b23 - 0.04) - (b22 + 0.04)), 0, 1)
    return r1 * G22 + r2 * (G23 - G22)
t = np.arange(len(x)) / sr; y = x * 10 ** (env_db(t) / 20)
sf.write(OUT / f'{FIN}.wav', y.astype(np.float32), sr, subtype='PCM_24')
W2 = dict(W); W2['wav'] = f'{FIN}.wav'; W2['source_take'] = TAKE; W2['ending_gain_db'] = dict(L22=G22, L23=G23, ramp1=[a21 + 0.04, a22 - 0.04], ramp2=[b22 + 0.04, b23 - 0.04])
json.dump(W2, open(OUT / f'{FIN}_words.json', 'w'), indent=1, ensure_ascii=False); shutil.copyfile(OUT / f'{STEM}_alignment.json', OUT / f'{FIN}_alignment.json')
def ebur(ss, dur):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', str(OUT / f'{FIN}.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    I = TP = None; s = False
    for ln in p.stderr.splitlines():
        if 'Summary:' in ln: s = True
        if s and ln.strip().startswith('I:'): I = float(ln.split('I:')[1].split('LUFS')[0])
        if s and ln.strip().startswith('Peak:'): TP = float(ln.split('Peak:')[1].split('dBFS')[0])
    return I, TP
I, TP = ebur(0, len(y) / sr + 1); body, _ = ebur(words[0]['start'], a22 - 0.05 - words[0]['start'])
l22, _ = ebur(a22, max(0.45, b22 - a22 + 0.05)); l23, _ = ebur(b23, max(0.45, L(23)[-1]['end'] - b23 + 0.05)); l2223, _ = ebur(a22, L(23)[-1]['end'] - a22 + 0.05)
M = dict(final=f'{FIN}.wav', source_take=TAKE, duration_s=round(len(y) / sr, 3), speech_end_s=W['speech_end_s'], integrated_LUFS=I, true_peak_dBTP=TP, body_L01_L21_I=body,
         L22_I=l22, L23_I=l23, L22_L23_I=l2223, delta_L22=round(l22 - body, 2), delta_L23=round(l23 - body, 2), delta_L22_L23=round(l2223 - body, 2),
         pause_L22_L23=W['pause_before_L23'], ending_gain_db=W2['ending_gain_db'], wps=round(len(words) / (W['speech_end_s'] - words[0]['start']), 3))
json.dump(M, open(OUT / 'vo_metrics_final-v5.json', 'w'), indent=1); print(json.dumps(M, indent=1))
