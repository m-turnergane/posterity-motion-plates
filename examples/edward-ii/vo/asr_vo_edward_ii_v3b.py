#!/usr/bin/env python3
"""ASR word-match check: faster-whisper medium.en, no prompt, vs raw/script-vo-v3-DRAFT.txt. Writes vo/asr_<take>.json."""
import json, re, sys, difflib, subprocess, numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path('/workspace/posterity/standalones/edward-ii')
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace("\u2019", "'")).split()
ref = norm((ROOT / 'raw/script-vo-v3-DRAFT.txt').read_text())
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
for take in sys.argv[1:]:
    out = ROOT / 'vo' / f'asr_{take}.json'
    pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(ROOT / 'vo' / f'cand-vo-oliver-edward-ii-{take}.wav'), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language='en', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False, temperature=0.0)
    segs = list(segs); hyp = norm(' '.join(s.text for s in segs))
    ops = [(t, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for t, a, b, c, d in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes() if t != 'equal']
    match = sum(b - a for t, a, b, c, d in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes() if t == 'equal')
    json.dump({'model': 'medium.en', 'ref_words': len(ref), 'hyp_words': len(hyp), 'matched': match, 'diffs': ops, 'hyp': ' '.join(hyp)}, open(out, 'w'), indent=1)
    print(take, 'ref', len(ref), 'hyp', len(hyp), 'matched', match, 'diffs', ops, flush=True)
