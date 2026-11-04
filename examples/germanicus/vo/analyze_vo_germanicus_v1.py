#!/usr/bin/env python3
"""Germanicus v1 VO analysis (adapted from serials/croatoan/ch3/vo/analyze_vo_croatoan_ch3_v4.py; same clamp/trim/fade/pad + ebur128 method).
Clamps stretched last-char end with RMS > -45 dBFS, trims at true decay (< -50 dBFS), 15 ms fade, +0.25 s silence, 48k mono PCM_24.
END CHECK: LUFS(L11 final line) and LUFS(L10+L11) vs body L01-L09; flag if < -3 LU. Pauses = inter-word gaps (alignment) > 1.2 s, cross-checked by RMS silence.
Usage: analyze_vo_germanicus_v1.py TAKE OUTSTEM [METRICSNAME]   -> OUTSTEM.wav, OUTSTEM_alignment.json, OUTSTEM_words.json, vo_metrics_<TAKE>.json. Refuses overwrite."""
import json, subprocess, sys, numpy as np, soundfile as sf
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/germanicus'); OUT = ROOT / 'vo'
TTS = (ROOT / 'raw' / 'script-vo-tts.txt').read_text().strip()
LINES = [l.strip() for l in (ROOT / 'raw' / 'script-vo.txt').read_text().strip().splitlines() if l.strip()]
SPK = {}  # no respellings used
SCRIPT = ' '.join(TTS.split()); assert len(SCRIPT.split()) == 146 and len(LINES) == 11
def ebur(path, ss, dur):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    I = TP = None; s = False
    for ln in p.stderr.splitlines():
        if 'Summary:' in ln: s = True
        if s and ln.strip().startswith('I:'): I = float(ln.split('I:')[1].split('LUFS')[0])
        if s and ln.strip().startswith('Peak:'): TP = float(ln.split('Peak:')[1].split('dBFS')[0])
    return I, TP
def words_of(ch, st, en):
    out = []; i = 0
    while i < len(ch):
        if ch[i].isspace(): i += 1; continue
        j = i
        while j < len(ch) and not ch[j].isspace(): j += 1
        out.append({'word': ''.join(ch[i:j]), 'start': st[i], 'end': en[j - 1]}); i = j
    return out
name, stem = sys.argv[1], sys.argv[2]
fin = OUT / f'{stem}.wav'; fal = OUT / f'{stem}_alignment.json'; fw = OUT / f'{stem}_words.json'; fm = OUT / f'vo_metrics_{sys.argv[3] if len(sys.argv) > 3 else name}.json'
for p in (fin, fal, fw, fm):
    if p.exists(): raise SystemExit(f'refusing overwrite {p}')
al = json.load(open(OUT / f'vo_germanicus_oliver_{name}_alignment.json')); ch = al['characters']
assert ' '.join(''.join(ch).split()) == SCRIPT
st, en = list(al['character_start_times_seconds']), list(al['character_end_times_seconds'])
ws = words_of(ch, st, en); assert len(ws) == 146
x, sr = sf.read(OUT / f'vo_germanicus_oliver_{name}.wav', dtype='float64'); raw_dur = len(x) / sr
wlen = int(0.02 * sr); hop = wlen // 2
lvl = [(i / sr, 20 * np.log10(np.sqrt(np.mean(x[i:i + wlen] ** 2)) + 1e-12)) for i in range(int(ws[-1]['start'] * sr), len(x) - wlen, hop)]
last_sound = max(tt for tt, l in lvl if l > -45) + 0.02; al_end_raw = ws[-1]['end']
last_end = min(ws[-1]['end'], last_sound + 0.03); ws[-1]['end'] = last_end
k = max(i for i, c in enumerate(ch) if not c.isspace()); en[k] = min(en[k], last_end)
t = last_end - 0.05; cut = None
while t < raw_dur:
    seg = x[int(t * sr):int((t + 0.02) * sr)]
    if len(seg) and 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12) < -50: cut = t + 0.02; break
    t += 0.005
cut = min(cut or raw_dur, raw_dur); y = x[:int(cut * sr)].copy(); f = int(0.015 * sr); y[-f:] *= np.linspace(1, 0, f)
y = np.concatenate([y, np.zeros(int(0.25 * sr))]); sf.write(fin, y.astype(np.float32), sr, subtype='PCM_24')
json.dump({'characters': ch, 'character_start_times_seconds': st, 'character_end_times_seconds': en, 'trim_s': cut,
           'source': f'vo_germanicus_oliver_{name}_alignment.json', 'last_char_end_raw_s': al_end_raw, 'seed': al['seed'], 'voice': al['voice'], 'model': al['model'],
           'voice_settings': al['voice_settings'], 'next_text': al['next_text']}, open(fal, 'w'), indent=1)
words = []; wi = 0
for li, L in enumerate(LINES):
    for tok in L.split():
        w = ws[wi]; assert SPK.get(w['word'], w['word']) == tok, (w['word'], tok)
        words.append({'i': wi, 'line': li + 1, 'word': tok, 'start': round(w['start'], 3), 'end': round(w['end'], 3)}); wi += 1
assert wi == 146
json.dump({'words': words, 'word_count': len(words), 'lines': LINES, 'wav': fin.name, 'timing_source': 'ElevenLabs /with-timestamps character alignment (word = first char start .. last char end)',
           'speech_end_s': round(last_end, 3), 'duration_s': round(len(y) / sr, 3)}, open(fw, 'w'), indent=1, ensure_ascii=False)
lines = []
for li in range(11):
    lw = [w for w in words if w['line'] == li + 1]; I, _ = ebur(fin, lw[0]['start'], lw[-1]['end'] - lw[0]['start'] + 0.05)
    lines.append(dict(line=f'L{li+1:02d}', start=lw[0]['start'], end=lw[-1]['end'], I=I, text=LINES[li][:44]))
b0 = words[0]['start']; s10 = [w for w in words if w['line'] == 10][0]['start']; s11 = [w for w in words if w['line'] == 11][0]['start']
body, _ = ebur(fin, b0, s10 - 0.05 - b0); endI, _ = ebur(fin, s10, last_end + 0.05 - s10); lastI, _ = ebur(fin, s11, last_end + 0.05 - s11)
I, TP = ebur(fin, 0, len(y) / sr + 1)
gaps = [dict(after=words[i]['word'], before=words[i+1]['word'], gap=round(words[i+1]['start'] - words[i]['end'], 3), at=words[i]['end']) for i in range(145)]
long_gaps = [g for g in gaps if g['gap'] > 1.2]
# RMS-silence cross-check (< -45 dBFS runs > 1.2 s inside speech)
fr = [(i / sr, 20 * np.log10(np.sqrt(np.mean(y[i:i + wlen] ** 2)) + 1e-12)) for i in range(0, int(last_end * sr), hop)]
sil = []; s0 = None
for tt, l in fr:
    if l < -45: s0 = tt if s0 is None else s0
    else:
        if s0 is not None and tt - s0 > 1.2: sil.append([round(s0, 3), round(tt, 3)])
        s0 = None
peak_lin = float(np.max(np.abs(y))); last_peak = 20*np.log10(np.max(np.abs(y[int(s11*sr):int(last_end*sr)])) + 1e-12)
M = dict(take=name, out=fin.name, raw_duration_s=round(raw_dur, 3), duration_s=round(len(y) / sr, 3), speech_start_s=round(b0, 3), speech_end_s=round(last_end, 3),
         last_char_end_raw_s=round(al_end_raw, 3), trim_s=round(cut, 3), integrated_LUFS=I, true_peak_dBTP=TP, sample_peak_dBFS=round(20*np.log10(peak_lin), 2),
         body_L01_L09_I=body, end_L10_L11_I=endI, delta_end_vs_body_LU=round(endI - body, 2), final_line_L11_I=lastI, delta_L11_vs_body_LU=round(lastI - body, 2),
         L11_sample_peak_dBFS=round(last_peak, 2), end_drop_flag=(endI - body) < -3.0 or (lastI - body) < -3.0, wps=round(146 / (last_end - b0), 3),
         max_gap=max(gaps, key=lambda g: g['gap']), long_gaps_over_1p2=long_gaps, rms_silences_over_1p2=sil, word_count=len(words), lines=lines, seed=al['seed'])
json.dump(M, open(fm, 'w'), indent=1); print(json.dumps({k: v for k, v in M.items() if k != 'lines'}, indent=1)); [print(l) for l in lines]
