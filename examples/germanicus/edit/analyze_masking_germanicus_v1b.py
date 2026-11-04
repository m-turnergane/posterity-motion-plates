#!/usr/bin/env python3
"""Speech-band (1-4 kHz) masking analysis for Germanicus: VO vs bed per word, plus bed transient/density spikes over speech.
Usage: analyze_masking_germanicus_v1b.py <audio_dir> <out_json> [--lift-scan]
Uses the pre-limiter stems the build writes (vo_staged.wav mono, bed_ridden.wav stereo; both scaled identically by the master gain, VO enters
the mix at -3.01 dB per channel). Never overwrites."""
import sys, json
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
A = Path(sys.argv[1]); OUT = Path(sys.argv[2]); assert not OUT.exists(), OUT
G = Path('/workspace/posterity/standalones/germanicus')
words = json.load(open(G / 'vo/final-vo-oliver-germanicus-v2_words.json'))['words']
vo, sr = sf.read(A / 'vo_staged.wav'); bed, _ = sf.read(A / 'bed_ridden.wav')
sos = butter(4, [1000, 4000], btype='bandpass', fs=sr, output='sos')
vb = sosfiltfilt(sos, vo) * 0.70710678; bb = sosfiltfilt(sos, bed, axis=0)
vp = vb ** 2; bp = (bb ** 2).mean(1)
db = lambda p: 10 * np.log10(p + 1e-20)
def word_rows(lines, bedgain=None):
    rows = []
    bpx = bp if bedgain is None else bp * bedgain ** 2
    for i, w in enumerate(words):
        if w['line'] not in lines: continue
        a, z = int(w['start'] * sr), int(w['end'] * sr)
        r_rms = db(vp[a:z].mean()) - db(bpx[a:z].mean())
        # loudest 50 ms of the word vs the bed over the same 50 ms windows (peak-syllable view) and worst-case 50 ms window
        hop = int(0.05 * sr); seg_v = [vp[k:k + hop].mean() for k in range(a, max(a + 1, z - hop + 1), hop)] or [vp[a:z].mean()]
        seg_b = [bpx[k:k + hop].mean() for k in range(a, max(a + 1, z - hop + 1), hop)] or [bpx[a:z].mean()]
        r_win = [db(x) - db(y) for x, y in zip(seg_v, seg_b)]
        k = int(np.argmax(seg_v))
        rows.append(dict(i=i, line=w['line'], word=w['word'], start=round(w['start'], 3), end=round(w['end'], 3), band_rms_margin_db=round(float(r_rms), 2),
                         peak_syllable_margin_db=round(float(r_win[k]), 2)))
    return rows
# bed density/transient spikes in band over speech: 20 ms frames, spike if > local 1 s median + 6 dB, or bed band level > (VO band level - 8 dB) in that frame
fr = int(0.02 * sr); nF = len(bp) // fr
bf = db(bp[:nF * fr].reshape(nF, fr).mean(1)); vf = db(vp[:nF * fr].reshape(nF, fr).mean(1))
from scipy.ndimage import median_filter
med = median_filter(bf, size=51)
def spikes(lines):
    out = []
    for w in words:
        if w['line'] not in lines: continue
        f0, f1 = int(w['start'] / 0.02), int(w['end'] / 0.02) + 1
        for f in range(f0, min(f1, nF)):
            if bf[f] - med[f] > 6.0: out.append(dict(t=round(f * 0.02, 2), word=w['word'], line=w['line'], jump_over_local_median_db=round(float(bf[f] - med[f]), 1)))
    return out
R = dict(method='1-4 kHz 4th-order Butterworth (zero-phase); VO at -3.01 dB/channel as mixed; bed = mean L/R power; pre-limiter stems; '
         'band_rms_margin = VO band RMS over the word span minus bed band RMS over the same span; peak_syllable = loudest 50 ms of the word vs bed in that window; '
         'spike = 20 ms bed band frame > 1 s running median + 6 dB during a word', audio_dir=str(A))
for name, L in (('L1-L4', (1, 2, 3, 4)), ('L9-L12', (9, 10, 11, 12)), ('L13', (13,))):
    rows = word_rows(L); m = [r['band_rms_margin_db'] for r in rows]
    R[name] = dict(min_band_rms_margin_db=min(m), median_band_rms_margin_db=float(np.median(m)), words_under_8db=[r for r in rows if r['band_rms_margin_db'] < 8.0],
                   bed_spikes_over_speech=spikes(L), rows=rows)
    print(name, 'min', min(m), 'median', round(float(np.median(m)), 2), 'under8', len(R[name]['words_under_8db']), 'spikes', len(R[name]['bed_spikes_over_speech']))
# whole-programme bed band level during speech vs VO
sp = np.zeros(len(vp), bool)
for w in words: sp[int(w['start'] * sr):int(w['end'] * sr)] = True
R['speech_band_overall_db'] = dict(vo=round(float(db(vp[sp].mean())), 2), bed=round(float(db(bp[sp].mean())), 2), margin=round(float(db(vp[sp].mean()) - db(bp[sp].mean())), 2))
if '--lift-scan' in sys.argv:
    t = np.arange(len(bp)) / sr; scan = {}
    for L in np.arange(0, 8.01, 0.5):
        g = np.ones(len(bp)); w = np.clip((t - 62.75) / 0.2, 0, 1); w = 0.5 - 0.5 * np.cos(np.pi * w); g = 10 ** (L * w / 20)
        rows = word_rows((13,), bedgain=g); scan[f'{L:.1f}'] = {r['word']: r['band_rms_margin_db'] for r in rows}
    R['l13_lift_scan_pre_limiter'] = scan; print(json.dumps(scan, indent=0))
json.dump(R, open(OUT, 'x'), indent=1); print('->', OUT)
