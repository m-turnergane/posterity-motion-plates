#!/workspace/mpvenv/bin/python
"""Per-word VO-over-score margins from VO-only / bed-only stems rendered through the same mix chain (examiner RECHECK-v2 method).
Bands: house = BS.1770 K-weighting; 1-4 kHz = 4th-order Butterworth band-pass 1000-4000 Hz; phone = 4th-order Butterworth band-pass 300-8000 Hz.
Margin = 20log10(RMS_vo / RMS_bed) over each aligned word span (both channels, power-summed). Usage: measure_margins.py TAG [TAG...]"""
import sys, json, subprocess, os
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
SR = 48000; A = Path(os.environ.get('SCR')); BR = Path(__file__).resolve().parent.parent
W = json.load(open(BR / 'logs/vo_bjorn_v2_words.json'))['words']
def load(p):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(p), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, 2).astype(np.float64)
def kweight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return lfilter(b2, a2, lfilter(b1, a1, x, axis=0), axis=0)
BANDS = dict(house=kweight, k1_4=lambda x: sosfilt(butter(4, [1000, 4000], 'bandpass', fs=SR, output='sos'), x, axis=0),
             phone=lambda x: sosfilt(butter(4, [300, 8000], 'bandpass', fs=SR, output='sos'), x, axis=0))
WORDS = [(w['word'], w['start'], w['end']) for w in W if 57.7 < w['start'] < 60.3]
WORDS.append(('the coffin', [w for w in W if w['word'] == 'the' and w['start'] > 58][0]['start'], [w for w in W if w['word'] == 'coffin' and w['start'] > 58][0]['end']))
v = [w for w in W if w['word'] == 'victors.'][0]; WORDS.append(('victors.', v['start'], v['end']))
def margins(tag):
    vo, bed = load(A / f'stem_{tag}_voonly.wav'), load(A / f'stem_{tag}_bedonly.wav'); out = {}
    for name, f in BANDS.items():
        fv, fb = f(vo), f(bed)
        for wname, a, b in WORDS:
            i, j = int(a * SR), int(b * SR); m = 10 * np.log10(np.mean(fv[i:j] ** 2) / np.mean(fb[i:j] ** 2))
            out.setdefault(f'{wname}@{a:.3f}', {})[name] = round(float(m), 1)
    return out
if __name__ == '__main__':
    res = {t: margins(t) for t in sys.argv[1:]}
    print(json.dumps(res, indent=1)); json.dump(res, open(A / 'margins.json', 'w'), indent=1)
