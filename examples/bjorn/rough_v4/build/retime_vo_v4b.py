#!/workspace/mpvenv/bin/python
"""Björn Rough v4b VO retime (Examiner FIX-1: P07 too short). Input: rough_v4/scratch/vo_bjorn_v4.wav (the v4 retime, unchanged).
Only change: +0.500 s (24000 samples = 15 frames) of local-noise-floor room tone inserted in the gap "barred.|So" (31.927 -> 32.31),
at the quietest 50 ms window inside that gap, 8 ms fades, rng 1611 (same recipe as retime_vo_v4.py). No re-voicing, no stretching.
Every word after "barred." and every cut from P08 on (plus P07's end) moves +0.5 s / +15 frames; END_F +15.
Writes rough_v4/scratch/vo_bjorn_v4b.wav, logs/vo_bjorn_v4b_words.json, logs/cuts_v4b.json, logs/retime_vo_v4b_log.json (refuses overwrite)."""
import json, hashlib, wave, numpy as np
from pathlib import Path
RO = Path(__file__).resolve().parent.parent; BJ = RO.parent; SR = 48000; FPS = 30; XF = int(0.008 * SR); INS_F = 15; INS = INS_F * SR // FPS
assert hashlib.md5((BJ / 'raw/script-vo-v4-LOCKED.txt').read_bytes()).hexdigest() == 'ff97caaa20d2238fddc30c7bdb4a0c8a'
SRC = RO / 'scratch/vo_bjorn_v4.wav'
with wave.open(str(SRC)) as f: assert f.getframerate() == SR and f.getnchannels() == 1; x = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float32) / 32768
W = json.load(open(RO / 'logs/vo_bjorn_v4_words.json'))['words']; C = json.load(open(RO / 'logs/cuts_v4.json'))
iB = next(i for i in range(len(W) - 1) if W[i]['word'] == 'barred.' and W[i + 1]['word'] == 'So')
a, b = W[iB]['end'], W[iB + 1]['start']; s0, s1 = int((a + 0.05) * SR), int((b - 0.05) * SR)
e = np.convolve(x[s0:s1] ** 2, np.ones(2400), 'valid'); k = s0 + int(np.argmin(e)) + 1200
fl = float(np.sqrt(np.mean(x[k - 1200:k + 1200] ** 2)) + 1e-7)
rng = np.random.default_rng(1611); ins = (rng.standard_normal(INS) * fl).astype(np.float32)
fq = np.linspace(0, 1, XF, dtype=np.float32); ins[:XF] *= fq; ins[-XF:] *= fq[::-1]
y = np.concatenate([x[:k], ins, x[k:]])
D = INS / SR
nw = [dict(w, start=round(w['start'] + (D if i > iB else 0), 4), end=round(w['end'] + (D if i > iB else 0), 4)) for i, w in enumerate(W)]
i7 = next(n for n, c in enumerate(C) if c['shot'] == 'P07'); cuts = []
for n, c in enumerate(C):
    c = dict(c)
    if n > i7: c['f0'] += INS_F; c['word_start'] = round(c['word_start'] + D, 4)
    if n >= i7: c['f1'] += INS_F
    c['start'], c['end'], c['dur'] = round(c['f0'] / FPS, 3), round(c['f1'] / FPS, 3), round((c['f1'] - c['f0']) / FPS, 3); c['lead'] = round(c['word_start'] - c['start'], 4)
    cuts.append(c)
END_F = cuts[-1]['f1']; assert len(y) == END_F * SR // FPS, (len(y), END_F)
# verify: samples before k identical; samples after the insert are the v4 samples shifted exactly INS (cross-correlation on "So", "leapt", last word)
assert np.array_equal(y[:k], x[:k]) and np.array_equal(y[k + INS:], x[k:])
chk = []
for wd in ('So', 'leapt', W[-1]['word']):
    i = next(j for j in range(iB + 1, len(W)) if W[j]['word'] == wd); s, t = int(W[i]['start'] * SR), int(W[i]['end'] * SR); seg = x[s:t]
    best = max(range(INS - 480, INS + 481, 4), key=lambda o: float(np.dot(y[s + o:s + o + len(seg)], seg))); chk.append([wd, round(best / SR, 4)])
outs = [RO / 'scratch/vo_bjorn_v4b.wav', RO / 'logs/vo_bjorn_v4b_words.json', RO / 'logs/cuts_v4b.json', RO / 'logs/retime_vo_v4b_log.json']
for p in outs: assert not p.exists(), p
with wave.open(str(outs[0]), 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
json.dump(dict(words=nw), open(outs[1], 'x'), indent=0); json.dump(cuts, open(outs[2], 'x'), indent=1)
json.dump(dict(src=str(SRC), src_md5=hashlib.md5(SRC.read_bytes()).hexdigest(), insert_after='barred.', gap_v4=[a, b], insert_at_s=round(k / SR, 4), insert_s=D, insert_frames=INS_F,
               noise_floor_rms=fl, out_s=round(len(y) / SR, 3), end_f=END_F, xcorr_shift_s=chk), open(outs[3], 'x'), indent=1)
for c in cuts: print(f"{c['shot']:6s} f{c['f0']:5d} {c['start']:7.3f}-{c['end']:7.3f} {c['dur']:5.3f} {c['word']} @{c['word_start']:.3f}")
print('insert at', round(k / SR, 4), 'floor', fl, 'end', END_F, END_F / FPS, 'xcorr', chk)
