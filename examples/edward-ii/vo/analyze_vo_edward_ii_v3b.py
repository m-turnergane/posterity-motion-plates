#!/usr/bin/env python3
"""Words json (display tokens of the script, with line idx) from char alignment + pacing/loudness metrics per take."""
import json, sys, re, subprocess, numpy as np, soundfile as sf
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/edward-ii'); VO = ROOT / 'vo'
LINES = [l.strip() for l in (ROOT / 'raw/script-vo-v3-DRAFT.txt').read_text().strip().splitlines() if l.strip()]
DISP = [(w, li + 1) for li, l in enumerate(LINES) for w in l.split()]
def ebur(p, ss=None, t=None):
    c = ['ffmpeg', '-hide_banner', '-nostats'] + (['-ss', str(ss)] if ss is not None else []) + ['-i', str(p)] + (['-t', str(t)] if t else []) + ['-af', 'ebur128=peak=true', '-f', 'null', '-']
    e = subprocess.run(c, capture_output=True, text=True).stderr; s = e[e.rfind('Summary'):]
    return float(re.search(r'I:\s+(-?[\d.]+)', s).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))
for take in sys.argv[1:]:
    al = json.load(open(VO / f'cand-vo-oliver-edward-ii-{take}_alignment.json'))
    ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
    text = ''.join(ch); b0 = text.find('<break'); b1 = text.find('/>', b0) + 2
    toks = []; cur = None
    for i, c in enumerate(ch):
        if b0 <= i < b1: 
            if cur: toks.append(cur); cur = None
            continue
        if c.isspace():
            if cur: toks.append(cur); cur = None
        else:
            if cur is None: cur = dict(word='', start=st[i], end=en[i])
            cur['word'] += c; cur['end'] = en[i]
    if cur: toks.append(cur)
    assert [t['word'] for t in toks] == [w for w, _ in DISP], 'token mismatch'
    words = [dict(word=w, start=round(t['start'], 3), end=round(t['end'], 3), line=li) for t, (w, li) in zip(toks, DISP)]
    wav = VO / f'cand-vo-oliver-edward-ii-{take}.wav'; x, sr = sf.read(wav); dur = len(x) / sr
    gaps = sorted([(round(b['start'] - a['end'], 3), a['word'], b['word']) for a, b in zip(words, words[1:])], reverse=True)[:5]
    ls = {li: (min(w['start'] for w in words if w['line'] == li), max(w['end'] for w in words if w['line'] == li)) for li in range(1, 18)}
    I, TP = ebur(wav); body_end = ls[16][1]
    Ib, _ = ebur(wav, 0, ls[15][1]); I16, _ = ebur(wav, ls[16][0], ls[16][1] - ls[16][0]); I17, _ = ebur(wav, ls[17][0], ls[17][1] - ls[17][0] + 0.2)
    m = dict(take=take, seed=al['seed'], duration=round(dur, 3), speech_end=words[-1]['end'], body_end=body_end, wps_body=round(214 / body_end, 3),
             I=I, TP=TP, I_body_L01_15=Ib, I_L16=I16, I_L17=I17, top_gaps=gaps, line_starts={k: round(v[0], 2) for k, v in ls.items()},
             line_durs={k: round(v[1] - v[0], 2) for k, v in ls.items()})
    json.dump({'words': words, 'source': f'cand-vo-oliver-edward-ii-{take}_alignment.json'}, open(VO / f'cand-vo-oliver-edward-ii-{take}_words.json', 'w'), indent=1)
    json.dump(m, open(VO / f'vo_metrics_{take}.json', 'w'), indent=1); print(json.dumps(m))
