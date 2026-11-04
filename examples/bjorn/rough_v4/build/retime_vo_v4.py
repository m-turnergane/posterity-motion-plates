#!/workspace/mpvenv/bin/python
"""Björn Rough v4 VO retime. Input: rough_v4/vo/vo_oliver_bjorn_v4.mp3 (full Oliver read of LOCKED v4, md5 ff97caaa…).
Words are never changed: only silence between words is shortened (quietest window, 8 ms crossfade) or opened (local noise floor, 8 ms fades).
Rules: comma pauses <= 0.22 s, in-line sentence pauses <= 0.40 s, line breaks <= 0.45 s; designated: +0.354 s after "Mediterranean," (ALT-A2),
1.20 s hold after "This wasn't Rome." (storyboard P16), P05 slot exactly 10.5 s (line starts 0.37 s after the P05 cut), tagline break kept.
Writes rough_v4/scratch/vo_bjorn_v4.wav, logs/vo_bjorn_v4_words.json, logs/cuts_v4.json, logs/retime_vo_v4_log.json (refuses overwrite)."""
import json, re, subprocess, hashlib, wave, numpy as np
from pathlib import Path
RO = Path(__file__).resolve().parent.parent; BJ = RO.parent; SR = 48000; FPS = 30; XF = int(0.008 * SR)
assert hashlib.md5((BJ / 'raw/script-vo-v4-LOCKED.txt').read_bytes()).hexdigest() == 'ff97caaa20d2238fddc30c7bdb4a0c8a'
MP3 = RO / 'vo/vo_oliver_bjorn_v4.mp3'; W = json.load(open(RO / 'vo/vo_oliver_bjorn_v4_words_raw.json'))['words']
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(MP3), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout, '<i2').astype(np.float32) / 32768
LEAD, HL, T0, P05_OFF, P05_SLOT = 0.10, 1 / FPS, 0.15, 0.37, 10.5
# (shot, first words, hard)
A = [('P01', 'A coffin', 0), ('P02', 'Inside, the', 1), ('P03', 'Legend says', 0), ('P04', 'His tutor', 0), ('P05', 'A Viking', 0), ('P06', 'At a walled', 0),
     ('P07', 'But the gates', 1), ('P08', 'So Hastein', 0), ('P09', 'The bishop and', 0), ('P10', 'They chose', 1), ('P11', 'Then, on', 0), ('P12', 'They said', 0),
     ('P13', 'The bishop let', 0), ('P14', 'leapt from', 1), ('P15', 'Only after', 0), ('P16', "This wasn't", 1), ('P17A', 'But the strangest', 0),
     ('P17B', 'The oldest surviving', 0), ('P18', 'Decades later,', 0), ('P20', 'They conquered', 0), ('OUTRO', 'History remembers', 0)]
def norm(w): return re.sub(r"[^\w']", '', w.lower())
idx = []; j = 0
for k, ph, h in A:
    p = [norm(s) for s in ph.split()]
    j = next(i for i in range(j, len(W)) if [norm(W[i + q]['word']) for q in range(len(p))] == p); idx.append(j)
gap0 = [W[i + 1]['start'] - W[i]['end'] for i in range(len(W) - 1)]
g = list(gap0); why = {}
for i in range(len(W) - 1):
    w = W[i]['word']; lb = W[i + 1]['line'] != W[i]['line']
    if w == 'Mediterranean,': g[i] = gap0[i] + 0.354; why[i] = 'ALT-A2 +0.354'
    elif lb and W[i + 1]['line'] == 17: why[i] = 'tagline break kept'
    elif w == 'victors.': why[i] = 'tagline beat kept'
    elif lb: g[i] = min(gap0[i], 0.45)
    elif w[-1] in '.!?': g[i] = min(gap0[i], 0.40)
    elif w[-1] in ',;:': g[i] = min(gap0[i], 0.22)
iR = next(i for i in range(len(W) - 1) if W[i]['word'] == 'Rome.' and W[i - 1]['word'] == "wasn't"); g[iR] = 1.20; why[iR] = 'P16 hold 1.2 s'
def times(g):
    nw = [dict(W[0], start=T0, end=T0 + W[0]['end'] - W[0]['start'])]
    for i in range(1, len(W)):
        t = nw[-1]['end'] + g[i - 1]; nw.append(dict(W[i], start=t, end=t + W[i]['end'] - W[i]['start']))
    return nw
# P05 slot: gap "Italy.|At" so that P06 cut = P05 cut + 10.5
iI = idx[5] - 1; nw = times(g); c05 = nw[idx[4]]['start'] - P05_OFF; need = c05 + P05_SLOT + LEAD - nw[idx[5]]['start']
g[iI] += need; why[iI] = f'P05 slot 10.5 s ({need:+.3f})'; assert g[iI] >= 0.30, g[iI]
nw = times(g)
# frames
cuts = []
for n, (k, ph, h) in enumerate(A):
    if n == 0: f0 = 0
    elif k == 'P05': f0 = int(round((nw[idx[n]]['start'] - P05_OFF) * FPS))
    elif k == 'P06': f0 = cuts[4]['f0'] + int(round(P05_SLOT * FPS))
    else: f0 = int(round((nw[idx[n]]['start'] - (HL if h else LEAD)) * FPS))
    cuts.append(dict(shot=k, f0=f0, hard=bool(h), word=W[idx[n]]['word'], word_start=round(nw[idx[n]]['start'], 4), line=W[idx[n]]['line']))
VO_END = nw[-1]['end']; END_F = int(round((VO_END + 0.50) * FPS))
for n, c in enumerate(cuts):
    c['f1'] = cuts[n + 1]['f0'] if n + 1 < len(cuts) else END_F
    c['start'], c['end'], c['dur'] = round(c['f0'] / FPS, 3), round(c['f1'] / FPS, 3), round((c['f1'] - c['f0']) / FPS, 3)
    c['lead'] = round(c['word_start'] - c['start'], 4)
# audio splice
def quiet(a, b):
    s0, s1 = int((a + 0.05) * SR), int((b - 0.05) * SR)
    if s1 - s0 < 2400: return int((a + b) / 2 * SR)
    e = np.convolve(x[s0:s1] ** 2, np.ones(2400), 'valid'); return s0 + int(np.argmin(e)) + 1200
rng = np.random.default_rng(1611); fade = np.linspace(0, 1, XF, dtype=np.float32)
y = [np.zeros(int(round(T0 * SR)) - int(round(W[0]['start'] * SR)), np.float32)]; cur = 0; ops = []
for i in range(len(W) - 1):
    d = g[i] - gap0[i]
    if abs(d) < 0.5 / SR: continue
    k = quiet(W[i]['end'], W[i + 1]['start'])
    if d > 0:
        L = int(round(d * SR)); fl = float(np.sqrt(np.mean(x[max(0, k - 1200):k + 1200] ** 2)) + 1e-7)
        ins = (rng.standard_normal(L) * fl).astype(np.float32); q = min(XF, L // 2); fq = np.linspace(0, 1, q, dtype=np.float32); ins[:q] *= fq; ins[L - q:] *= fq[::-1]
        y += [x[cur:k], ins]; cur = k; ops.append(dict(after=W[i]['word'], op='open', s=round(d, 3)))
    else:
        L = int(round(-d * SR)); s0 = max(int((W[i]['end'] + 0.04) * SR), k - L // 2); s0 = min(s0, int((W[i + 1]['start'] - 0.04) * SR) - L)
        assert s0 >= int(W[i]['end'] * SR) - 1, (W[i]['word'], d)
        a_ = x[cur:s0 + XF].copy(); b_ = x[s0 + L:s0 + L + XF]; a_[-XF:] = a_[-XF:] * (1 - fade) + b_ * fade; y.append(a_); cur = s0 + L + XF
        ops.append(dict(after=W[i]['word'], op='cut', s=round(-d, 3)))
y.append(x[cur:]); y = np.concatenate(y); endN = int(round(END_F / FPS * SR)); y = np.concatenate([y, np.zeros(max(0, endN - len(y)), np.float32)])[:endN]
chk = []
for i in (0, idx[13], len(W) - 1):
    s, e = int(W[i]['start'] * SR), int(W[i]['end'] * SR); s2 = int(nw[i]['start'] * SR); seg_ = x[s:e]
    best = min(range(-240, 241, 4), key=lambda o: float(np.abs(y[s2 + o:s2 + o + len(seg_)] - seg_).mean())); chk.append([W[i]['word'], best / SR])
outs = [RO / 'scratch/vo_bjorn_v4.wav', RO / 'logs/vo_bjorn_v4_words.json', RO / 'logs/cuts_v4.json', RO / 'logs/retime_vo_v4_log.json']
for p in outs: assert not p.exists(), p
(RO / 'scratch').mkdir(exist_ok=True); (RO / 'logs').mkdir(exist_ok=True)
with wave.open(str(outs[0]), 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
json.dump(dict(words=[dict(w, start=round(w['start'], 4), end=round(w['end'], 4)) for w in nw]), open(outs[1], 'x'), indent=0)
json.dump(cuts, open(outs[2], 'x'), indent=1)
json.dump(dict(src=str(MP3), src_md5=hashlib.md5(MP3.read_bytes()).hexdigest(), raw_s=round(len(x) / SR, 3), out_s=round(len(y) / SR, 3), vo_end=round(VO_END, 3), end_f=END_F,
               designated={f"{W[i]['word']}|{W[i+1]['word']}": [round(gap0[i], 3), round(g[i], 3), r] for i, r in why.items()}, ops=ops, word_position_check_s=chk), open(outs[3], 'x'), indent=1)
for c in cuts: print(f"{c['shot']:6s} f{c['f0']:5d} {c['start']:7.3f}-{c['end']:7.3f} {c['dur']:5.2f} {'HARD ' if c['hard'] else ''}L{c['line']} {c['word']} @{c['word_start']:.3f}")
print('vo_end', round(VO_END, 3), 'end', END_F / FPS, 'chk', chk)
