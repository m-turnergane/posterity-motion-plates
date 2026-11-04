"""Tighten Oliver final read: shorten inter-sentence silences only (words untouched), cut in the quietest part of each gap, 8 ms crossfades.
Writes vo_oliver_v3_final_tight.wav/.mp3 + _words.json + tighten_log.json. Refuses overwrite."""
import json, subprocess, sys, numpy as np, wave
from pathlib import Path
D = Path(__file__).parent; SR = 48000
CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.45
W = json.load(open(D / 'vo_oliver_v3_final_words.json'))['words']
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(D / 'vo_oliver_v3_final.mp3'), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, '<i2').astype(np.float32) / 32768
# special gaps (target seconds): keep the hinge pause, the priest-line build, the tagline break
SPECIAL = {('tried.', 'Nothing'): 0.62, ('infamous.', 'A'): 0.70, ('Countess.', 'History'): 0.80, ('victors.', 'We'): 0.70, ('monster:', 'the'): 0.48}
cuts = []; log = []
for a, b in zip(W, W[1:]):
    g = b['start'] - a['end']; tgt = SPECIAL.get((a['word'], b['word']))
    if tgt is None:
        if a['word'][-1] not in '.:?!' or g <= CAP: continue
        tgt = CAP
    rm = g - tgt
    if rm < 0.02: continue
    # quietest window of length rm inside the gap, keeping 0.08 s guard at each side
    s0, s1 = int((a['end'] + 0.08) * SR), int((b['start'] - 0.08) * SR); L = int(rm * SR)
    if s1 - s0 < L: L = max(0, s1 - s0); rm = L / SR
    if L <= 0: continue
    e = np.convolve(x[s0:s1] ** 2, np.ones(L), 'valid'); k = s0 + int(np.argmin(e))
    cuts.append((k, k + L)); log.append(dict(after=a['word'], before=b['word'], at=round(a['end'], 3), gap=round(g, 3), new_gap=round(g - rm, 3), removed=round(rm, 3),
                                             rms_dBFS=round(float(10 * np.log10(np.mean(x[k:k + L] ** 2) + 1e-12)), 1)))
XF = int(0.008 * SR); out = []; pos = 0; fade = np.linspace(0, 1, XF, dtype=np.float32)
for k0, k1 in cuts:
    seg = x[pos:k0].copy(); out.append(seg); pos = k1
out.append(x[pos:].copy())
y = out[0]
for seg in out[1:]:
    if len(y) >= XF and len(seg) >= XF:
        y = np.concatenate([y[:-XF], y[-XF:] * (1 - fade) + seg[:XF] * fade, seg[XF:]])
    else: y = np.concatenate([y, seg])
# retime words
def shift(t):
    s = 0.0
    for k0, k1 in cuts:
        if t * SR >= k1: s += (k1 - k0 + XF) / SR   # each splice overlap also removes XF samples
    return t - s
W2 = [dict(w, start=round(shift(w['start']), 4), end=round(shift(w['end']), 4)) for w in W]
wav = D / 'vo_oliver_v3_final_tight.wav'; mp3 = D / 'vo_oliver_v3_final_tight.mp3'
for p in (wav, mp3): assert not p.exists(), p
with wave.open(str(wav), 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-n', '-v', 'error', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)], check=True)
json.dump(dict(words=W2), open(D / 'vo_oliver_v3_final_tight_words.json', 'x'), indent=0)
R = dict(cap=CAP, special=[list(k) + [v] for k, v in SPECIAL.items()], raw_s=round(len(x) / SR, 3), tight_s=round(len(y) / SR, 3),
         removed_s=round((len(x) - len(y)) / SR, 3), n_cuts=len(cuts), cuts=log)
json.dump(R, open(D / 'tighten_log.json', 'x'), indent=1); print(R['raw_s'], R['tight_s'], R['n_cuts'], max(c['rms_dBFS'] for c in log))
