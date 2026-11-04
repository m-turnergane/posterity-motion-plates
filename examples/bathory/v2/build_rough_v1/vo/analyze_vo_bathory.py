#!/usr/bin/env python3
"""Words json from char alignment + ASR (faster-whisper medium.en) diff + metrics per take."""
import json, sys, re, subprocess, difflib, numpy as np
from pathlib import Path
V2 = Path('/workspace/posterity/standalones/bathory/v2'); VO = V2 / 'build_rough_v1' / 'vo'
LINES = [l.strip() for l in (V2 / 'raw/script-vo-v2-DRAFT.txt').read_text().strip().splitlines() if l.strip()]
DISP = [(w, li + 1) for li, l in enumerate(LINES) for w in l.split()]
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace("\u2019", "'")).split()
def ebur(p):
    e = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr; s = e[e.rfind('Summary'):]
    return float(re.search(r'I:\s+(-?[\d.]+)', s).group(1)), float(re.search(r'Peak:\s+(-?[\d.]+)', s).group(1))
from faster_whisper import WhisperModel
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
ref = norm(' '.join(LINES))
for take in sys.argv[1:]:
    al = json.load(open(VO / f'cand-vo-oliver-bathory-{take}_alignment.json'))
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
    wav = VO / f'cand-vo-oliver-bathory-{take}.wav'
    pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(wav), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language='en', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False, temperature=0.0)
    segs = list(segs); hyp = norm(' '.join(s.text for s in segs))
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    ops = [(t, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for t, a, b, c, d in sm.get_opcodes() if t != 'equal']
    I, TP = ebur(wav)
    gaps = sorted([(round(b['start'] - a['end'], 3), a['word'], b['word']) for a, b in zip(words, words[1:])], reverse=True)[:6]
    ls = {li: round(min(w['start'] for w in words if w['line'] == li), 2) for li in range(1, 20)}
    body_end = max(w['end'] for w in words if w['line'] == 18)
    met = dict(take=take, seed=al['seed'], speech_end=words[-1]['end'], body_end=body_end, wps_body=round(sum(1 for w in words if w['line'] <= 18) / body_end, 3), I=I, TP=TP,
               top_gaps=gaps, line_starts=ls, asr_diffs=ops, asr_hyp=' '.join(hyp))
    json.dump({'words': words, 'source': f'cand-vo-oliver-bathory-{take}_alignment.json'}, open(VO / f'cand-vo-oliver-bathory-{take}_words.json', 'w'), indent=1)
    json.dump(met, open(VO / f'vo_metrics_{take}.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in met.items() if k != 'asr_hyp'}), flush=True)
