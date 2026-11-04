#!/usr/bin/env python3
"""v1f master ASR check (faster-whisper medium.en, CPU int8, word timestamps) vs the owner script; also the timing of "hidden" vs the burnt cue. New files only."""
import json, re, subprocess, difflib, numpy as np
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); OUT = E / "qc_rough_v1f/asr_v1f.json"; assert not OUT.exists()
M = "/workspace/posterity/renders/posterity-germanicus-ROUGH-v1f.mp4"; SCRIPT = Path("/workspace/posterity/standalones/germanicus/raw/script-vo-OWNER-v3.txt").read_text()
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", M, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).copy()
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8"); seg, _ = m.transcribe(x, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
W = [(w.word.strip(), round(float(w.start), 3), round(float(w.end), 3), round(float(w.probability), 3)) for s in seg for w in s.words]
norm = lambda s: re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("\u2019", "'")).split()
ref, hyp = norm(SCRIPT), norm(" ".join(w[0] for w in W)); sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
ops = [(t, " ".join(ref[i1:i2]), " ".join(hyp[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
errs = sum(max(i2 - i1, j2 - j1) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal")
hid = [w for w in W if w[0].strip(",.").lower() == "hidden"]
R = {"model": "faster-whisper medium.en int8", "ref_words": len(ref), "hyp_words": len(hyp), "wer_approx": round(errs / len(ref), 4), "diffs": ops, "hidden_asr": hid,
     "hidden_cue_s": [1.207, 2.421], "hidden_inside_cue": bool(hid) and 1.0 <= hid[0][1] <= 1.6, "words": W}
json.dump(R, open(OUT, "x"), indent=1); print({k: v for k, v in R.items() if k != "words"}); print(W[:10])
