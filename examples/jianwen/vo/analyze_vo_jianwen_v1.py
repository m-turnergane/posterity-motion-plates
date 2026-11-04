#!/usr/bin/env python3
"""Words json (display tokens of the script, with line idx) from char alignment + pacing/loudness/speech-end metrics per take (Jianwen v1)."""
import json, sys, re, subprocess, numpy as np, soundfile as sf
from pathlib import Path
ROOT = Path('/workspace/posterity/standalones/jianwen'); VO = ROOT / 'vo'
LINES = [l.strip() for l in (ROOT / 'raw/script-vo-tts.txt').read_text().strip().splitlines() if l.strip()]
DISP = [(w, li + 1) for li, l in enumerate(LINES) for w in l.split()]; NL = len(LINES); NBODY = sum(len(l.split()) for l in LINES[:-1])
def ebur(p, ss=None, t=None):
    c = ['ffmpeg', '-hide_banner', '-nostats'] + (['-ss', str(ss)] if ss is not None else []) + ['-i', str(p)] + (['-t', str(t)] if t else []) + ['-af', 'ebur128=peak=true', '-f', 'null', '-']
    e = subprocess.run(c, capture_output=True, text=True).stderr; s = e[e.rfind('Summary'):]
    return float(re.search(r'I:\s+(-?[\d.]+)', s).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))
def speech_end(p):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'silencedetect=n=-45dB:d=0.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', e)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', e)]
    return (st[-1] if len(st) > len(en) else None), list(zip(st, en))
for take in sys.argv[1:]:
    al = json.load(open(VO / f'cand-vo-oliver-jianwen-{take}_alignment.json'))
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
    wav = VO / f'cand-vo-oliver-jianwen-{take}.wav'; x, sr = sf.read(wav); dur = len(x) / sr
    gaps = sorted([(round(b['start'] - a['end'], 3), a['word'], b['word']) for a, b in zip(words, words[1:])], reverse=True)[:6]
    ls = {li: (min(w['start'] for w in words if w['line'] == li), max(w['end'] for w in words if w['line'] == li)) for li in range(1, NL + 1)}
    I, TP = ebur(wav); body_end = ls[NL - 1][1]; se, sil = speech_end(wav)
    long_words = sorted([(round(w['end'] - w['start'], 3), w['word']) for w in words], reverse=True)[:6]
    m = dict(take=take, seed=al['seed'], duration=round(dur, 3), align_end=words[-1]['end'], speech_end_silencedetect=se, body_end=body_end, wps_body=round(NBODY / body_end, 3),
             I=I, TP=TP, top_gaps=gaps, longest_words=long_words, line_starts={k: round(v[0], 2) for k, v in ls.items()},
             line_durs={k: round(v[1] - v[0], 2) for k, v in ls.items()}, silences=[(round(a, 2), round(b, 2)) for a, b in sil])
    json.dump({'words': words, 'source': f'cand-vo-oliver-jianwen-{take}_alignment.json'}, open(VO / f'cand-vo-oliver-jianwen-{take}_words.json', 'w'), indent=1)
    json.dump(m, open(VO / f'vo_metrics_{take}.json', 'w'), indent=1)
    print(take, json.dumps({k: m[k] for k in ('seed','duration','align_end','speech_end_silencedetect','body_end','wps_body','I','TP','top_gaps','longest_words')}))
    print('  line_starts', m['line_starts'])
