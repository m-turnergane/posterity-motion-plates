#!/usr/bin/env python3
"""v5 VO ASR check: faster-whisper medium.en, NO initial prompt (strict proper-noun test), word diff vs raw/script-vo-v5-DRAFT.txt.
Copy of asr_vo_germanicus_v2.py. Writes vo/asr_<take>.json (refuses overwrite)."""
import json, re, sys, difflib, subprocess, numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path('/workspace/posterity/standalones/germanicus'); take, wavname = sys.argv[1], sys.argv[2]; out = ROOT / 'vo' / f'asr_{take}.json'
if out.exists(): raise SystemExit(f'refusing overwrite {out}')
norm = lambda s: re.sub(r"[^a-z' ]", ' ', s.lower().replace('-', ' ').replace("'s ", " s ").replace("\u2019", "'")).split()
SPELL = {'judgment': 'judgement'}
ref = norm((ROOT / 'raw' / 'script-vo-v5-DRAFT.txt').read_text())
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / 'vo' / wavname), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language='en', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False, temperature=0.0)
segs = list(segs); ww = [dict(w=w.word.strip(), s=round(w.start, 2), e=round(w.end, 2)) for s in segs for w in s.words]
hyp = [SPELL.get(w, w) for w in norm(' '.join(s.text for s in segs) + ' ')]
ops = [(t, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for t, a, b, c, d in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes() if t != 'equal']
names = {n: (sum(1 for w in ref if w.startswith(n)), sum(1 for w in hyp if w.startswith(n))) for n in ['germanicus', 'piso', 'tacitus', 'antioch', 'armenia', 'syria']}
json.dump({'model': 'medium.en', 'prompt': None, 'decode': 'beam5, condition_on_previous_text=False, temperature 0 (long-file repetition loop seen with conditioning on)', 'ref_words': len(ref), 'hyp_words': len(hyp), 'diffs': ops, 'proper_nouns_ref_hyp': names, 'hyp': ' '.join(hyp), 'asr_words': ww}, open(out, 'w'), indent=1)
print(take, len(ref), len(hyp), 'diffs:', ops, 'names:', names)
