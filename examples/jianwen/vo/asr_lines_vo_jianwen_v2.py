#!/usr/bin/env python3
"""Per-line ASR check (faster-whisper medium.en) for Jianwen v2 takes: each script line cut from the wav using the alignment's line window (+-0.2 s),
transcribed alone and diffed against that line. Avoids whole-file Whisper window skipping. Writes vo/asr_lines_v2_<take>.json."""
import json, re, sys, difflib, subprocess, numpy as np
from pathlib import Path
from faster_whisper import WhisperModel
ROOT = Path('/workspace/posterity/standalones/jianwen'); VO = ROOT / 'vo'
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace("\u2019", "'")).split()
LINES = [l.strip() for l in (ROOT / 'raw/script-vo-tts.txt').read_text().strip().splitlines() if l.strip()]
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
for take in sys.argv[1:]:
    words = json.load(open(VO / f'cand-vo-oliver-jianwen-v2-{take}_words.json'))['words']
    pcm = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(VO / f'cand-vo-oliver-jianwen-v2-{take}.wav'), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-']), np.float32)
    res = []; tm = tr = 0
    for li, line in enumerate(LINES, 1):
        ws = [w for w in words if w['line'] == li]; a = max(0, ws[0]['start'] - 0.2); b = ws[-1]['end'] + 0.2
        segs, _ = m.transcribe(pcm[int(a * 16000):int(b * 16000)], language='en', beam_size=5, condition_on_previous_text=False, vad_filter=False, temperature=0.0)
        hyp_t = ' '.join(s.text for s in segs); ref = norm(line); hyp = norm(hyp_t)
        sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
        match = sum(b2 - a2 for t, a2, b2, c, d in sm.get_opcodes() if t == 'equal'); tm += match; tr += len(ref)
        diffs = [(t, ' '.join(ref[a2:b2]), ' '.join(hyp[c:d])) for t, a2, b2, c, d in sm.get_opcodes() if t != 'equal']
        res.append(dict(line=li, start=round(a, 2), end=round(b, 2), ref_words=len(ref), matched=match, hyp=hyp_t.strip(), diffs=diffs))
        print(take, f'L{li:02d}', f'{match}/{len(ref)}', diffs if diffs else '', flush=True)
    json.dump({'model': 'medium.en', 'take': take, 'matched': tm, 'ref_words': tr, 'lines': res}, open(VO / f'asr_lines_v2_{take}.json', 'w'), indent=1)
    print(take, 'TOTAL', tm, '/', tr, flush=True)
