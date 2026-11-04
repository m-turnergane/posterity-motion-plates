#!/usr/bin/env python3
"""ASR word-match check of the TEMP VO (same method as standalones/edward-ii/vo/asr_vo_edward_ii_v3b.py: faster-whisper medium.en)."""
import json, re, difflib, subprocess, numpy as np, os
from faster_whisper import WhisperModel
HERE = os.path.dirname(os.path.abspath(__file__))
al = json.load(open(f"{HERE}/audio/edward_atlas_TEMPVO_v1_oliver_alignment.json"))
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace("\u2019", "'")).split()
ref = norm(' '.join(al["lines"].values() if isinstance(al["lines"], dict) else [l if isinstance(l, str) else l["text"] for l in al["lines"]]))
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
out = f"{HERE}/audio/edward_atlas_TEMPVO_v1_oliver_asr.json"; assert not os.path.exists(out)
pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f"{HERE}/audio/edward_atlas_TEMPVO_v1_oliver_edit.wav", '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language='en', beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=False, temperature=0.0)
segs = list(segs); hyp = norm(' '.join(s.text for s in segs))
sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
ops = [(t, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for t, a, b, c, d in sm.get_opcodes() if t != 'equal']
match = sum(b - a for t, a, b, c, d in sm.get_opcodes() if t == 'equal')
words = [dict(w=w.word, s=round(w.start, 3), e=round(w.end, 3)) for s in segs for w in s.words]
json.dump({'temp_vo': True, 'model': 'medium.en', 'ref_words': len(ref), 'hyp_words': len(hyp), 'matched': match, 'diffs': ops, 'hyp': ' '.join(hyp), 'words': words}, open(out, 'w'), indent=1)
print('ref', len(ref), 'hyp', len(hyp), 'matched', match, 'diffs', ops)
