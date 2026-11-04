#!/usr/bin/env python3
"""faster-whisper sanity check of a VO take vs script (word diff) + ASR word timestamps. Copy of asr_vo_germanicus_v1.py (ref = raw/script-vo-OWNER-v3.txt). Writes vo/asr_<take>.json (refuses overwrite)."""
import json, re, sys, difflib, subprocess, numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path('/workspace/posterity/standalones/germanicus'); take, wavname = sys.argv[1], sys.argv[2]; out = ROOT / 'vo' / f'asr_{take}.json'
if out.exists(): raise SystemExit(f'refusing overwrite {out}')
norm = lambda s: re.sub(r"[^a-z' ]", ' ', s.lower().replace('-', ' ')).split()
ref = norm((ROOT / 'raw' / 'script-vo-OWNER-v3.txt').read_text())
m = WhisperModel('small.en', device='cpu', compute_type='int8')
pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / 'vo' / wavname), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), beam_size=5, word_timestamps=True, initial_prompt='Germanicus, Tiberius, Piso, Syria, Tacitus, Senate.')
segs = list(segs); ww = [dict(w=w.word.strip(), s=round(w.start, 2), e=round(w.end, 2)) for s in segs for w in s.words]
hyp = norm(' '.join(s.text for s in segs))
ops = [(t, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for t, a, b, c, d in difflib.SequenceMatcher(None, ref, hyp).get_opcodes() if t != 'equal']
json.dump({'ref_words': len(ref), 'hyp_words': len(hyp), 'diffs': ops, 'hyp': ' '.join(hyp), 'asr_words': ww}, open(out, 'w'), indent=1); print(len(ref), len(hyp), ops); print(ww[-8:])
