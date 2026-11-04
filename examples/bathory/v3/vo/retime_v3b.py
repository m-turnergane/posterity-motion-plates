"""Rough v3b VO: start from Oliver's RAW final read (vo_oliver_v3_final.mp3, natural gaps), then set selected inter-sentence gaps
(open some so no plate is < ~2.5 s and 'tried.' holds ~1 s; re-tighten a few long ones). Words untouched; splices in the quietest
part of each gap with 8 ms crossfades. Writes vo_oliver_v3b.wav/.mp3 + _words.json + retime_v3b_log.json. Refuses overwrite."""
import json, subprocess, numpy as np, wave
from pathlib import Path
D = Path(__file__).parent; SR = 48000; XF = int(0.008 * SR)
W = json.load(open(D / 'vo_oliver_v3_final_words.json'))['words']
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(D / 'vo_oliver_v3_final.mp3'), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, '<i2').astype(np.float32) / 32768
TARGET = {('supper.', 'Thurzó'): (0.93, 'open: B05 >= 2.5 s'), ('tried.', 'Nothing'): (1.12, 'open: ~1.0 s held beat on B01b after "never tried."'),
          ('trial.', 'Thurzó'): (0.90, 'open: B13a >= 2.5 s'), ('it.', 'Thurzó'): (1.12, 'open: B13b >= 2.5 s'),
          ('confinement.', 'Then'): (0.97, 'open: B18 >= 2.5 s'),
          ('investigate.', 'One'): (0.55, 'tighten'), ('dying.', 'Báthory'): (0.55, 'tighten'), ('court.', 'The'): (0.55, 'tighten'),
          ('hearsay.', 'The'): (0.60, 'tighten'), ('infamous.', 'A'): (0.85, 'tighten (keeps a build before the priest line)'),
          ('victors.', 'We'): (0.80, 'tighten')}
used = set(); ops = []
for i in range(len(W) - 1):
    a, b = W[i], W[i + 1]; key = (a['word'], b['word'])
    if key not in TARGET: continue
    assert key not in used, key; used.add(key); tgt, why = TARGET[key]; g = b['start'] - a['end']; d = tgt - g
    s0, s1 = int((a['end'] + 0.08) * SR), int((b['start'] - 0.08) * SR)
    if d < 0:
        L = int(-d * SR); assert s1 - s0 >= L, key
        e = np.convolve(x[s0:s1] ** 2, np.ones(L), 'valid'); k = s0 + int(np.argmin(e)); ops.append((k, k + L, 0, i, key, g, why))
    else:
        L = int(d * SR); win = int(0.05 * SR); e = np.convolve(x[s0:s1] ** 2, np.ones(win), 'valid'); k = s0 + int(np.argmin(e)) + win // 2
        ops.append((k, k, L, i, key, g, why))
assert used == set(TARGET), set(TARGET) - used
ops.sort(); segs = []; pos = 0; rng = np.random.default_rng(7); log = []; shifts = []
for k0, k1, ins, i, key, g, why in ops:
    segs.append(x[pos:k0].copy()); pos = k1
    if ins:
        floor = float(np.sqrt(np.mean(x[k0 - 2400:k0 + 2400] ** 2)) + 1e-7)
        segs.append((rng.standard_normal(ins + XF) * floor).astype(np.float32)); delta = ins
    else: delta = -(k1 - k0)
    shifts.append((k1, delta)); log.append(dict(after=key[0], before=key[1], raw_gap=round(g, 3), new_gap=TARGET[key][0], change_s=round(delta / SR, 3), why=why,
                                                 at_raw_s=round(k0 / SR, 3), local_floor_dBFS=round(float(20 * np.log10(np.sqrt(np.mean(x[k0 - 2400:k0 + 2400] ** 2)) + 1e-9)), 1)))
segs.append(x[pos:].copy())
y = segs[0]; fade = np.linspace(0, 1, XF, dtype=np.float32); xfs = 0
for s in segs[1:]:
    y = np.concatenate([y[:-XF], y[-XF:] * (1 - fade) + s[:XF] * fade, s[XF:]]); xfs += 1
# each op adds 2 splices (removal: 1 splice, insertion: 2) -> retime exactly by sample bookkeeping
def shift(t):
    s = t * SR; o = 0
    for (k0, k1, ins, *_ ) in ops:
        if s >= k1:
            o += (ins + XF - XF * 2) if ins else (-(k1 - k0) - XF)
    return (s + o) / SR
W2 = [dict(w, start=round(shift(w['start']), 4), end=round(shift(w['end']), 4)) for w in W]
assert abs(shift(len(x) / SR) - len(y) / SR) < 0.002, (shift(len(x) / SR), len(y) / SR)
wav = D / 'vo_oliver_v3b.wav'; mp3 = D / 'vo_oliver_v3b.mp3'
for p in (wav, mp3, D / 'vo_oliver_v3b_words.json', D / 'retime_v3b_log.json'): assert not p.exists(), p
with wave.open(str(wav), 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-n', '-v', 'error', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)], check=True)
json.dump(dict(words=W2), open(D / 'vo_oliver_v3b_words.json', 'x'), indent=0)
R = dict(source='vo_oliver_v3_final.mp3 (raw read)', raw_s=round(len(x) / SR, 3), v3b_s=round(len(y) / SR, 3), net_change_s=round((len(y) - len(x)) / SR, 3), ops=log)
json.dump(R, open(D / 'retime_v3b_log.json', 'x'), indent=1, ensure_ascii=False); print(R['raw_s'], R['v3b_s'], R['net_change_s'])
