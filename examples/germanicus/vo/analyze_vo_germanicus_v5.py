#!/usr/bin/env python3
"""Germanicus v5 VO analysis (copy of analyze_vo_germanicus_v2.py, adapted to the LOCKED 23-line v5 script + SSML break before L23).
Same post chain: clamp stretched last-char end with RMS > -45 dBFS, trim at true decay (< -50 dBFS), 15 ms fade, +0.25 s silence, 48k mono PCM_24. No loudnorm.
Break-tag characters are dropped from word timings. PAUSE = silence between L12 'war.' and L13 'But' measured two ways: alignment (word end->start)
and RMS (last frame > -45 dBFS of 'war.' -> first frame > -45 dBFS before 'But'). END CHECK: LUFS(L13), LUFS(L12+L13) vs body L01-L11 (flag < -3 LU).
Usage: analyze_vo_germanicus_v2.py TAKE OUTSTEM   -> OUTSTEM.wav, OUTSTEM_alignment.json, OUTSTEM_words.json, vo_metrics_<TAKE>.json. Refuses overwrite."""
import json, re, subprocess, sys, numpy as np, soundfile as sf
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/germanicus'); OUT = ROOT / 'vo'
LINES = [l.strip() for l in (ROOT / 'raw' / 'script-vo-v5-DRAFT.txt').read_text().strip().splitlines() if l.strip()]
NW = sum(len(l.split()) for l in LINES); assert len(LINES) == 23
def ebur(path, ss, dur):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{ss:.3f}', '-t', f'{dur:.3f}', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    I = TP = None; s = False
    for ln in p.stderr.splitlines():
        if 'Summary:' in ln: s = True
        if s and ln.strip().startswith('I:'): I = float(ln.split('I:')[1].split('LUFS')[0])
        if s and ln.strip().startswith('Peak:'): TP = float(ln.split('Peak:')[1].split('dBFS')[0])
    return I, TP
name, stem = sys.argv[1], sys.argv[2]
fin = OUT / f'{stem}.wav'; fal = OUT / f'{stem}_alignment.json'; fw = OUT / f'{stem}_words.json'; fm = OUT / f'vo_metrics_{name}.json'
for p in (fin, fal, fw, fm):
    if p.exists(): raise SystemExit(f'refusing overwrite {p}')
al = json.load(open(OUT / f'vo_germanicus_oliver_{name}_alignment.json')); ch = list(al['characters'])
st, en = list(al['character_start_times_seconds']), list(al['character_end_times_seconds'])
txt = ''.join(ch); m = re.search(r'<break[^>]*/>', txt); assert m
brk = dict(chars=m.group(0), start=st[m.start()], end=en[m.end() - 1])
keep = [i for i in range(len(ch)) if not (m.start() <= i < m.end())]
ch2 = [ch[i] for i in keep]; st2 = [st[i] for i in keep]; en2 = [en[i] for i in keep]
assert ' '.join(''.join(ch2).split()) == ' '.join(LINES)
ws = []; i = 0
while i < len(ch2):
    if ch2[i].isspace(): i += 1; continue
    j = i
    while j < len(ch2) and not ch2[j].isspace(): j += 1
    ws.append({'word': ''.join(ch2[i:j]), 'start': st2[i], 'end': en2[j - 1]}); i = j
assert len(ws) == NW
x, sr = sf.read(OUT / f'vo_germanicus_oliver_{name}.wav', dtype='float64'); raw_dur = len(x) / sr
wlen = int(0.02 * sr); hop = wlen // 2
def rms_db(a, b): seg = x[int(a * sr):int(b * sr)]; return 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12) if len(seg) else -200
lvl = [(k / sr, rms_db(k / sr, k / sr + 0.02)) for k in range(int(ws[-1]['start'] * sr), len(x) - wlen, hop)]
last_sound = max(tt for tt, l in lvl if l > -45) + 0.02; al_end_raw = ws[-1]['end']
last_end = min(ws[-1]['end'], last_sound + 0.03); ws[-1]['end'] = last_end
t = last_end - 0.05; cut = None
while t < raw_dur:
    if rms_db(t, t + 0.02) < -50: cut = t + 0.02; break
    t += 0.005
cut = min(cut or raw_dur, raw_dur); y = x[:int(cut * sr)].copy(); f = int(0.015 * sr); y[-f:] *= np.linspace(1, 0, f)
y = np.concatenate([y, np.zeros(int(0.25 * sr))]); sf.write(fin, y.astype(np.float32), sr, subtype='PCM_24')
json.dump({'characters': ch2, 'character_start_times_seconds': st2, 'character_end_times_seconds': en2, 'break_tag': brk, 'trim_s': cut,
           'source': f'vo_germanicus_oliver_{name}_alignment.json', 'last_char_end_raw_s': al_end_raw, 'seed': al['seed'], 'voice': al['voice'], 'model': al['model'],
           'voice_settings': al['voice_settings'], 'next_text': al['next_text'], 'text_sent': al['text_sent']}, open(fal, 'w'), indent=1)
words = []; wi = 0
for li, L in enumerate(LINES):
    for tok in L.split():
        w = ws[wi]; assert w['word'] == tok, (w['word'], tok)
        words.append({'i': wi, 'line': li + 1, 'word': tok, 'start': round(w['start'], 3), 'end': round(w['end'], 3)}); wi += 1
# pause before L13 (alignment + RMS)
w12 = [w for w in words if w['line'] == 22][-1]; w13 = [w for w in words if w['line'] == 23][0]
fr = [(k / sr, rms_db(k / sr, k / sr + 0.02)) for k in range(int((w12['start']) * sr), int((w13['start'] + 0.4) * sr), int(0.005 * sr))]
war_off = max(tt for tt, l in fr if l > -45 and tt < (w12['end'] + w13['start']) / 2) + 0.02
but_on = min(tt for tt, l in fr if l > -45 and tt > war_off + 0.1)
pause = dict(align_war_end=w12['end'], align_but_start=w13['start'], align_gap=round(w13['start'] - w12['end'], 3),
             rms_war_offset=round(war_off, 3), rms_but_onset=round(but_on, 3), rms_gap=round(but_on - war_off, 3), break_tag_align=brk)
json.dump({'words': words, 'word_count': len(words), 'lines': LINES, 'wav': fin.name, 'timing_source': 'ElevenLabs /with-timestamps character alignment (word = first char start .. last char end); break-tag chars removed',
           'speech_end_s': round(last_end, 3), 'duration_s': round(len(y) / sr, 3), 'pause_before_L23': pause}, open(fw, 'w'), indent=1, ensure_ascii=False)
lines = []
for li in range(23):
    lw = [w for w in words if w['line'] == li + 1]; I, _ = ebur(fin, lw[0]['start'], max(0.45, lw[-1]['end'] - lw[0]['start'] + 0.05))
    lines.append(dict(line=f'L{li+1:02d}', start=lw[0]['start'], end=lw[-1]['end'], I=I, peak=round(20*np.log10(np.max(np.abs(y[int(lw[0]['start']*sr):int(lw[-1]['end']*sr)]))+1e-12), 2), text=LINES[li][:44]))
b0 = words[0]['start']; s12 = [w for w in words if w['line'] == 22][0]['start']
body, _ = ebur(fin, b0, s12 - 0.05 - b0)
# end block excludes the silent pause: measure L12 and L13 separately; L12+L13 energy via concatenation
l12 = [l for l in lines if l['line'] == 'L22'][0]; l13 = lines[-1]
I, TP = ebur(fin, 0, len(y) / sr + 1)
# short-term RMS of voiced frames per line (dBFS, frames > -40)
def voiced(a, b):
    v = [rms_db(k / sr, k / sr + 0.05) for k in range(int(a * sr), int(b * sr) - int(0.05 * sr), int(0.025 * sr))]; v = [q for q in v if q > -40]
    return round(float(np.median(v)), 2) if v else None
vr = {l['line']: voiced(l['start'], l['end']) for l in lines}
gaps = [dict(after=words[k]['word'], before=words[k+1]['word'], gap=round(words[k+1]['start'] - words[k]['end'], 3), at=words[k]['end']) for k in range(len(words) - 1)]
M = dict(take=name, out=fin.name, raw_duration_s=round(raw_dur, 3), duration_s=round(len(y) / sr, 3), speech_start_s=round(b0, 3), speech_end_s=round(last_end, 3),
         last_char_end_raw_s=round(al_end_raw, 3), trim_s=round(cut, 3), integrated_LUFS=I, true_peak_dBTP=TP,
         body_L01_L21_I=body, L22_I=l12['I'], L23_I=l13['I'], delta_L22_vs_body=round(l12['I'] - body, 2), delta_L23_vs_body=round(l13['I'] - body, 2), L22_L23_I=ebur(fin, l12['start'], l13['end'] - l12['start'] + 0.05)[0],
         voiced_median_rms_dBFS=vr, end_drop_flag=(l12['I'] - body) < -3.0 or (l13['I'] - body) < -3.0, pause_before_L23=pause,
         wps=round(len(words) / (last_end - b0), 3), gaps_over_0p6=[g for g in gaps if g['gap'] > 0.6], word_count=len(words), lines=lines, seed=al['seed'])
json.dump(M, open(fm, 'w'), indent=1); print(json.dumps({k: v for k, v in M.items() if k != 'lines'}, indent=1)); [print(l) for l in lines]
