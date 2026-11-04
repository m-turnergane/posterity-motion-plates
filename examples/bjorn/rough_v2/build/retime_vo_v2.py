#!/workspace/mpvenv/bin/python
"""Björn Rough v2 VO retime = the v1 retime (identical gap solver, reproduces v1 VO bit-exactly with REPRO=1) + v2 gap/cut overrides:
  "down.|Only" 3.196 -> 1.30 s; P13 inner pauses tightened so P13 <= 7.0 s; P07 in-cut 15 frames earlier (no VO moves).
Inputs read-only from ../rough_v1 (vo_prep, logs/vo_prep_words.json). v1 docstring follows.
Björn Rough v1 VO retime. Oliver prep read (vo_prep/vo_oliver_bjorn_v3_prep.mp3, md5 d9da6b85…) -> gaps tightened/opened so each
storyboard-v3 plate starts on its first word (cut = word start - LEAD; HARD CUT words: cut = word start - 1 frame).
Words untouched: only silence between words is removed (quietest window, 8 ms crossfade) or filled (local noise floor, 8 ms fades).
Writes scratch/audio/vo_bjorn_v1.wav (scratch, not a deliverable), logs/vo_bjorn_v1_words.json, logs/retime_vo_log.json, logs/cuts.json."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess, hashlib, numpy as np, wave
from pathlib import Path
RO = Path(__file__).resolve().parent.parent; RV = RO.parent / 'rough_v1'; import os; REPRO = os.environ.get('REPRO') == '1'; SR = 48000; XF = int(0.008 * SR); FPS = 30
LOCK = RV.parent / 'raw/script-vo-v3-LOCKED.txt'; MP3 = RV / 'vo_prep/vo_oliver_bjorn_v3_prep.mp3'
assert hashlib.md5(LOCK.read_bytes()).hexdigest() == 'c4683d2b846a026498a830c57e3853dc'; assert len(LOCK.read_text().split()) == 225
assert hashlib.md5(MP3.read_bytes()).hexdigest() == 'd9da6b850ae0082e10e2daa6256a7dfb'
al = json.load(open(RV / 'vo_prep/vo_oliver_bjorn_v3_prep_alignment.json'))
assert re.sub(r'\s*<break[^>]*/>\s*', ' ', al['text_sent']).split() == LOCK.read_text().split(), 'sent text != LOCKED'
W = json.load(open(RV / 'logs/vo_prep_words.json'))['words']; assert [w['word'] for w in W] == LOCK.read_text().split()
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(MP3), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout, '<i2').astype(np.float32) / 32768
LEAD, HLEAD, T0 = 0.10, 1 / FPS, 0.15
# (key, first words, storyboard start s, hard cut, designated hold gap {after-word: seconds})
A = [('P01', 'A coffin', 0.0, 0), ('P02', 'Inside, the', 3.33, 1), ('P03', 'Legend says', 6.67, 0), ('P04', 'His tutor', 12.92, 0), ('P05', 'Annals of', 17.50, 0),
     ('P06', 'At a walled', 23.75, 0), ('P07', 'But the gates', 29.17, 1), ('P08', 'So Hastein sent', 31.25, 0), ('P09', 'The bishop and', 37.08, 0),
     ('P10', 'They chose', 41.25, 1), ('P11', 'Then', 44.17, 0), ('P12', 'Their leader', 46.25, 0), ('P13', 'The bishop let', 51.67, 0),
     ('P14', 'leapt from', 58.33, 1), ('P15', 'Only after', 63.92, 0), ('P16', 'This was not', 68.50, 1), ('P17', 'The first known', 74.28, 0),
     ('P18', 'Björn first joins', 80.53, 1), ('P19', 'in a chronicle', 83.45, 0), ('P20', 'So the city', 88.20, 0), ('OUTRO', 'History remembers', 94.12, 0)]
END = 97.95; TAIL = 0.50
HOLD = {'Rome.#P16': 1.20}                         # storyboard: 1.2 s hold after "This was not Rome."
def norm(w): return re.sub(r"[^\w']", '', w.lower())
idx = []; j = 0
for k, ph, t, h in A:
    p = [norm(s) for s in ph.split()]
    j = next(i for i in range(j, len(W)) if [norm(W[i + q]['word']) for q in range(len(p))] == p); idx.append(j)
gap0 = [W[i + 1]['start'] - W[i]['end'] for i in range(len(W) - 1)]
def gmin(i, final):
    g = gap0[i]; w = W[i]['word']
    m = 0.30 if final else (0.65 if w == 'victors.' else (0.40 if w[-1] in '.!?' else (0.22 if w[-1] in ',;:' else g)))   # tagline beat kept ≥ 0.65 s
    return min(g, m)
seg = [(idx[n], idx[n + 1] if n + 1 < len(idx) else len(W)) for n in range(len(A))]
lead = [HLEAD if a[3] else LEAD for a in A]
tgt = [a[2] for a in A]; tgt[0] = T0 - LEAD
def need(n, tight):           # time from this word-start to next anchor word-start (or END-TAIL) for the segment
    i0, i1 = seg[n]; sp = W[i1 - 1]['end'] - W[i0]['start'] - sum(gap0[i0:i1 - 1])
    gi = list(range(i0, i1 - 1)); fin = [i1 - 1] if i1 < len(W) else []
    return sp + sum(gmin(i, False) if tight else gap0[i] for i in gi) + sum(gmin(i, True) if tight else gap0[i] for i in fin)
# word start times of anchors, with feasibility: if a segment can't fit even tightened, borrow time by starting it earlier
ws = [tgt[n] + lead[n] for n in range(len(A))]; ws.append(END - TAIL)
moves = []
for n in range(len(A) - 1, -1, -1):
    over = need(n, True) - (ws[n + 1] - ws[n])
    if over > 0:
        ws[n] -= over + 0.02; moves.append(dict(shot=A[n][0], earlier_by=round(over + 0.02, 3)))
for n in range(1, len(A)):
    assert ws[n] - ws[n - 1] >= need(n - 1, True) - 1e-6, A[n][0]
# per-segment gap assignment
newgap = list(gap0); seglog = []
for n, (i0, i1) in enumerate(seg):
    avail = ws[n + 1] - ws[n]; gi = list(range(i0, i1 - 1)); fin = i1 - 1 if i1 < len(W) else None
    sp = W[i1 - 1]['end'] - W[i0]['start'] - sum(gap0[i0:i1 - 1])
    cur = {i: gap0[i] for i in gi}
    if fin is not None: cur[fin] = gap0[fin]
    tail = None
    d = avail - sp - sum(cur.values())
    if fin is None and d >= 0: tail = d                              # last segment: the remaining time is VO end -> END-TAIL
    else:
        if d < 0:                                                    # tighten largest gaps first, down to their minimums
            while d < -1e-9:
                cand = [(cur[i] - gmin(i, i == fin), i) for i in cur if cur[i] - gmin(i, i == fin) > 1e-9]
                cand.sort(reverse=True); s, i = cand[0]; take = min(s, -d, 0.05); cur[i] -= take; d += take
        else:
            for i in gi:
                h = HOLD.get(f"{W[i]['word']}#{A[n][0]}")
                if h and cur[i] < h: add = min(d, h - cur[i]); cur[i] += add; d -= add
            inner = [i for i in gi if W[i]['word'][-1] in '.!?,;:' and f"{W[i]['word']}#{A[n][0]}" not in HOLD]
            share = 0.4 * d if inner else 0.0                        # 40 % spread on sentence/comma pauses (≤ +0.35 s each), rest ends the shot
            if inner:
                wts = np.array([2.0 if W[i]['word'][-1] in '.!?' else 1.0 for i in inner]); add = share * wts / wts.sum()
                add = np.minimum(add, 0.35); share = float(add.sum())
                for i, a in zip(inner, add): cur[i] += float(a)
            cur[fin] += d - share
        if fin is None: tail = avail - sp - sum(cur.values())
    if A[n][0] == 'OUTRO':                                           # tagline: tighten "victors. | We" only if needed (done above)
        pass
    for i, g in cur.items(): newgap[i] = g
    seglog.append(dict(shot=A[n][0], slot=round(avail, 3), speech=round(sp, 3), gaps={f"{W[i]['word']}|{W[i + 1]['word']}": [round(gap0[i], 3), round(g, 3)] for i, g in cur.items()},
                       tail_after_vo=None if tail is None else round(tail, 3)))
# OUTRO: tagline must end by END - TAIL; tighten its inner gaps if needed
i0, _ = seg[-1]; over = (ws[-2] + W[-1]['end'] - W[i0]['start'] - sum(gap0[i0:len(W) - 1]) + sum(newgap[i0:len(W) - 1])) - (END - TAIL)
assert over <= 1e-6, ('tagline overruns', over)
# ---- v2 overrides (skipped with REPRO=1) ----
def gi_(a, b): return next(i for i in range(len(W) - 1) if W[i]['word'] == a and W[i + 1]['word'] == b)
# exact-frame shaves so every later cut keeps v1's sub-frame phase (P15..OUTRO durations identical to v1):
#   P13 inner pauses shave 18 frames (P13 228 -> 210 f = 7.000 s, P12/P13 cut unchanged at f1522);  "down.|Only" shaves 57 frames (1.900 s).
P13_SHAVE, ONLY_SHAVE, COMMA = 18 / FPS, 57 / FPS, 0.10
V2_F0 = {'P07': 860}                         # P07 2.6 s: in-cut 15 f earlier, in the silence after "Rome." (no VO moves)
gap_v1 = list(newgap); v2log = []
if not REPRO:
    i_in, i_tun, i_com, i_down = gi_('in.', 'Behind'), gi_('tunics.', 'Mid-funeral,'), gi_('coffin,', 'the'), gi_('down.', 'Only')
    pp = (gap_v1[i_in] + gap_v1[i_tun] + gap_v1[i_com] - COMMA - P13_SHAVE) / 2
    V2_GAPS = {i_in: pp, i_tun: pp, i_com: COMMA, i_down: gap_v1[i_down] - ONLY_SHAVE}
    for i, g in V2_GAPS.items():
        assert g < gap0[i] or i == i_down; assert i == i_down or gap0[i] >= 0.08 + (gap0[i] - g) - 1e-9, W[i]['word']
        v2log.append(dict(gap=f"{W[i]['word']}|{W[i + 1]['word']}", prep=round(gap0[i], 4), v1=round(gap_v1[i], 4), v2=round(g, 4))); newgap[i] = g
# build audio: new word times
nw = []; t = T0; nw.append(dict(W[0], start=round(t, 4), end=round(t + W[0]['end'] - W[0]['start'], 4)))
for i in range(1, len(W)):
    t = nw[-1]['end'] + newgap[i - 1]; nw.append(dict(W[i], start=round(t, 4), end=round(t + W[i]['end'] - W[i]['start'], 4)))
for n in range(len(A)): assert REPRO or True or abs(nw[idx[n]]['start'] - ws[n]) < 2e-3
for n in range(len(A)): assert (not REPRO) or abs(nw[idx[n]]['start'] - ws[n]) < 2e-3, (A[n][0], nw[idx[n]]['start'], ws[n])
# audio: pieces = word spans with gap splices; split each gap at its quietest 50 ms point
def quiet(a, b):
    s0, s1 = int((a + 0.05) * SR), int((b - 0.05) * SR)
    if s1 - s0 < 2400: return int((a + b) / 2 * SR)
    e = np.convolve(x[s0:s1] ** 2, np.ones(2400), 'valid'); return s0 + int(np.argmin(e)) + 1200
rng = np.random.default_rng(1611); fade = np.linspace(0, 1, XF, dtype=np.float32)
out = []; pos = 0; tot = 0.0; oplog = []
lead_in = np.zeros(int(round(T0 * SR)) - int(round(W[0]['start'] * SR)), np.float32)   # first word starts at T0
y = [lead_in, x[:0]]
cursor = 0
for i in range(len(W) - 1):
    d = newgap[i] - gap0[i]
    if abs(d) < 0.5 / SR: continue
    k = quiet(W[i]['end'], W[i + 1]['start'])
    if d > 0:
        L = int(round(d * SR)); fl = float(np.sqrt(np.mean(x[max(0, k - 1200):k + 1200] ** 2)) + 1e-7)
        ins = (rng.standard_normal(L) * fl).astype(np.float32); q = min(XF, L // 2); fq = np.linspace(0, 1, q, dtype=np.float32); ins[:q] *= fq; ins[L - q:] *= fq[::-1]
        y.append(x[cursor:k]); y.append(ins); cursor = k; oplog.append(dict(after=W[i]['word'], op='open', s=round(d, 3)))
    else:
        L = int(round(-d * SR)); s0 = max(int((W[i]['end'] + 0.04) * SR), k - L // 2); s0 = min(s0, int((W[i + 1]['start'] - 0.04) * SR) - L)
        assert s0 >= int(W[i]['end'] * SR) - 1, (W[i]['word'], d)
        a_ = x[cursor:s0 + XF].copy(); b_ = x[s0 + L:s0 + L + XF]
        a_[-XF:] = a_[-XF:] * (1 - fade) + b_ * fade; y.append(a_); cursor = s0 + L + XF; oplog.append(dict(after=W[i]['word'], op='cut', s=round(-d, 3)))
y.append(x[cursor:]); y = np.concatenate(y)
DSH = sum(newgap) - sum(gap_v1); END2 = END + DSH; endN = int(round(END2 * SR)); y = np.concatenate([y, np.zeros(max(0, endN - len(y)), np.float32)])[:endN]
# verify: words in the new file sit where nw says (cross-correlate 3 words)
chk = []
for i in (0, idx[13], len(W) - 1):
    s, e = int(W[i]['start'] * SR), int(W[i]['end'] * SR); s2 = int(nw[i]['start'] * SR)
    seg_ = x[s:e]; best = min(range(-240, 241, 4), key=lambda o: float(np.abs(y[s2 + o:s2 + o + len(seg_)] - seg_).mean())); chk.append([W[i]['word'], best / SR])
SCR = RO / 'scratch/audio'; SCR.mkdir(parents=True, exist_ok=True); wavp = SCR / ('vo_bjorn_v1_repro.wav' if REPRO else 'vo_bjorn_v2.wav')
OUTS = [wavp] if REPRO else [wavp, RO / 'logs/vo_bjorn_v2_words.json', RO / 'logs/retime_vo_v2_log.json', RO / 'logs/cuts_v2.json']
for p in OUTS: assert not p.exists(), p
with wave.open(str(wavp), 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
if REPRO: print('REPRO wrote', wavp); sys.exit(0)
json.dump(dict(words=nw), open(RO / 'logs/vo_bjorn_v2_words.json', 'x'), indent=0)
C1 = json.load(open(RV / 'logs/cuts.json'))
SHIFT = {k: (0 if REPRO else (-18 if k == 'P14' else -75)) for k in [a[0] for a in A][14:] + ['P14']}   # word times after P13 moved by exactly these frames
cuts = []
for n, a in enumerate(A):
    c = nw[idx[n]]['start'] - lead[n] if n else 0.0; f0 = V2_F0.get(a[0], int(round(c * FPS)) if a[0] not in SHIFT else C1[n]['f0'] + SHIFT[a[0]]) if n else 0
    if a[0] in SHIFT: assert abs((c - (C1[n]['word_start'] - lead[n]) - SHIFT[a[0]] / FPS)) < 1e-3, a[0]
    cuts.append(dict(shot=a[0], f0=f0, lead=round(nw[idx[n]]['start'] - f0 / FPS, 4) if n else None, start=round(f0 / FPS, 3), storyboard=a[2], hard=bool(a[3]), word=W[idx[n]]['word'], word_start=nw[idx[n]]['start']))
for n in range(len(cuts)): cuts[n]['f1'] = cuts[n + 1]['f0'] if n + 1 < len(cuts) else 2938 + (cuts[-1]['f0'] - 2791); cuts[n]['end'] = round(cuts[n]['f1'] / FPS, 3); cuts[n]['dur'] = round((cuts[n]['f1'] - cuts[n]['f0']) / FPS, 3)
D1 = {c['shot']: c['f1'] - c['f0'] for c in C1}
for c, c1 in zip(cuts, C1):
    if c['shot'] not in ('P06', 'P07', 'P13', 'P14'): assert c['f1'] - c['f0'] == D1[c['shot']], (c['shot'], 'duration changed')
    if c['shot'] in ('P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P08', 'P09', 'P10', 'P11', 'P12', 'P13'): assert c['f0'] == c1['f0'], c['shot']
assert cuts[12]['f1'] - cuts[12]['f0'] <= 210
json.dump(cuts, open(RO / 'logs/cuts_v2.json', 'x'), indent=1)
json.dump(dict(v2_overrides=v2log, v2_f0_overrides=V2_F0, shave_s=round(DSH, 4), src=str(MP3), raw_s=round(len(x) / SR, 3), out_s=round(len(y) / SR, 3), T0=T0, lead=LEAD, hard_lead=HLEAD, moved_earlier=moves, ops=oplog, segments=seglog,
               word_position_check_s=chk, leapt=nw[idx[13]]['start'], vo_end=nw[-1]['end']), open(RO / 'logs/retime_vo_v2_log.json', 'x'), indent=1)
for c in cuts: print(f"{c['shot']:6s} {c['start']:7.3f}-{c['end']:7.3f} {c['dur']:5.2f}  sb {c['storyboard']:6.2f}  {'HARD ' if c['hard'] else ''}{c['word']} @{c['word_start']:.3f}")
print('moves', moves, 'chk', chk, 'leapt', nw[idx[13]]['start'], 'vo_end', nw[-1]['end'])
