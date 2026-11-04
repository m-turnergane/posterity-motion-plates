#!/usr/bin/env python3
"""v5 VO per-line ASR (faster-whisper medium.en, no prompt): each script line clipped from the take by its alignment words (+-0.25 s), transcribed alone,
normalised, compared word-for-word. Complements the full-file pass (asr_vo_germanicus_v5.py). Writes vo/asr_lines_<take>.json (refuses overwrite)."""
import json, re, sys, subprocess, numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path('/workspace/posterity/standalones/germanicus'); take, stem = sys.argv[1], sys.argv[2]; out = ROOT / 'vo' / f'asr_lines_{take}.json'
if out.exists(): raise SystemExit(f'refusing overwrite {out}')
SPELL = {'judgment': 'judgement'}
norm = lambda s: [SPELL.get(w, w) for w in re.sub(r"[^a-z' ]", ' ', (s + ' ').lower().replace('-', ' ').replace("'s ", " s ")).split()]
W = json.load(open(ROOT / 'vo' / f'{stem}_words.json')); words, lines = W['words'], W['lines']
pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / 'vo' / f'{stem}.wav'), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-']); x = np.frombuffer(pcm, np.float32)
m = WhisperModel('medium.en', device='cpu', compute_type='int8'); res = []
for li, L in enumerate(lines):
    lw = [w for w in words if w['line'] == li + 1]; a = max(0, lw[0]['start'] - 0.25); b = lw[-1]['end'] + 0.25
    segs, _ = m.transcribe(x[int(a * 16000):int(b * 16000)], language='en', beam_size=5, condition_on_previous_text=False)
    hyp = ' '.join(s.text for s in segs).strip(); ok = norm(hyp) == norm(L)
    res.append(dict(line=li + 1, ok=ok, ref=L, hyp=hyp)); print(take, li + 1, 'OK' if ok else 'DIFF', '' if ok else hyp, flush=True)
json.dump({'take': take, 'model': 'medium.en', 'lines_ok': sum(r['ok'] for r in res), 'n_lines': len(res), 'lines': res}, open(out, 'w'), indent=1)
print(take, 'lines ok', sum(r['ok'] for r in res), '/', len(res))
