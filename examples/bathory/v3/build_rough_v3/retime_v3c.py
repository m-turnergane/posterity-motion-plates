#!/workspace/mpvenv/bin/python
"""Rough v3c VO: v3b VO (vo_oliver_v3b.wav, locked read) with ONE change: the gap before the tagline ('Countess.' -> 'History')
opens from 0.859 s to GAP s so the tagline plays over the restored outro. Words untouched; noise-floor fill at the quietest
50 ms of the gap with 8 ms crossfades (same method as retime_v3b). Writes scratch_v3c/audio/vo_oliver_v3c.wav (scratch only,
not an owner deliverable), logs_v3c/vo_oliver_v3c_words.json + retime_v3c_log.json. Refuses overwrite."""
import json, subprocess, numpy as np, wave
from pathlib import Path
BR = Path(__file__).parent; V3 = BR.parent; SR = 48000; XF = int(0.008 * SR); GAP = 2.20
W = json.load(open(V3 / 'vo/vo_oliver_v3b_words.json'))['words']
with wave.open(str(V3 / 'vo/vo_oliver_v3b.wav')) as f: assert f.getframerate() == SR and f.getnchannels() == 1; x = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(np.float32) / 32768
i = [j for j in range(len(W) - 1) if W[j]['word'] == 'Countess.' and W[j + 1]['word'] == 'History'][0]; assert i == len(W) - 9
a, b = W[i], W[i + 1]; g = b['start'] - a['end']; L = int(round((GAP - g) * SR)); s0, s1 = int((a['end'] + 0.08) * SR), int((b['start'] - 0.08) * SR)
win = int(0.05 * SR); e = np.convolve(x[s0:s1] ** 2, np.ones(win), 'valid'); k = s0 + int(np.argmin(e)) + win // 2
floor = float(np.sqrt(np.mean(x[k - 2400:k + 2400] ** 2)) + 1e-7)
ins = (np.random.default_rng(7).standard_normal(L + XF) * floor).astype(np.float32); fade = np.linspace(0, 1, XF, dtype=np.float32)
A0, B0 = x[:k], x[k:]
y = np.concatenate([A0[:-XF], A0[-XF:] * (1 - fade) + ins[:XF] * fade, ins[XF:]]); y = np.concatenate([y[:-XF], y[-XF:] * (1 - fade) + B0[:XF] * fade, B0[XF:]])
assert len(y) == len(x) + L - XF
dt = (L - XF) / SR
W2 = [dict(w, start=round(w['start'] + (dt if j > i else 0), 4), end=round(w['end'] + (dt if j > i else 0), 4)) for j, w in enumerate(W)]
assert np.array_equal(y[:k - XF], x[:k - XF]) and np.array_equal(y[k + L - XF + XF:], x[k + XF:])     # untouched outside the splice
out = BR / 'scratch_v3c/audio/vo_oliver_v3c.wav'
for p in (out, BR / 'logs_v3c/vo_oliver_v3c_words.json', BR / 'logs_v3c/retime_v3c_log.json'): assert not p.exists(), p
with wave.open(str(out), 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
json.dump(dict(words=W2), open(BR / 'logs_v3c/vo_oliver_v3c_words.json', 'x'), indent=0)
R = dict(source='v3/vo/vo_oliver_v3b.wav', v3b_s=round(len(x) / SR, 3), v3c_s=round(len(y) / SR, 3), op=dict(after='Countess.', before='History', old_gap=round(g, 3),
         new_gap=round(b['start'] + dt - a['end'], 3), change_s=round(dt, 4), at_s=round(k / SR, 3), local_floor_dBFS=round(20 * np.log10(floor), 1),
         why='tagline (L18) moved onto the restored outro; H04b ends captionless on her eyes'), tagline_v3b=[b['start'], W[-1]['end']], tagline_v3c=[W2[i + 1]['start'], W2[-1]['end']])
json.dump(R, open(BR / 'logs_v3c/retime_v3c_log.json', 'x'), indent=1); print(json.dumps(R))
