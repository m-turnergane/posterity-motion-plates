"""ASR spot-check (faster-whisper medium.en) of the tight read vs the locked script; prints diffs + name-word timings."""
import json, re, difflib
from faster_whisper import WhisperModel
from pathlib import Path
D = Path(__file__).parent
norm = lambda s: re.sub(r"[^a-z0-9' ]", ' ', s.lower().replace('-', ' ').replace('\u2019', "'")).split()
ref = norm((D.parent / 'raw/script-vo-v3.txt').read_text())
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
import subprocess, numpy as np
a = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',str(D / 'vo_oliver_v3_final_tight.wav'),'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout,'<i2').astype(np.float32) / 32768
seg, _ = m.transcribe(a, beam_size=5, word_timestamps=True, initial_prompt='Elizabeth Báthory, György Thurzó, Ferenc Nádasdy, Csejte, Bytča, Túróczi')
hw = [w for s in seg for w in s.words]; hyp = norm(' '.join(w.word for w in hw))
sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False); diffs = [(op, ' '.join(ref[a:b]), ' '.join(hyp[c:d])) for op, a, b, c, d in sm.get_opcodes() if op != 'equal']
out = dict(ratio=round(sm.ratio(), 4), n_ref=len(ref), n_hyp=len(hyp), diffs=diffs)
json.dump(out, open(D / 'asr_check_v3_tight.json', 'x'), indent=1); print(json.dumps(out, indent=1, ensure_ascii=False))
