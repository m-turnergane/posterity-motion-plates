#!/usr/bin/env python3
"""v5b FIX-1 ASR spot-check of a window (default 28-40 s) of a master; faster-whisper medium.en int8, condition_on_previous_text False; compared to the vo_words in that window. New files only.
argv: master out_json [t0 t1]"""
import json, re, sys, subprocess, difflib, numpy as np
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); M, OUT = sys.argv[1], Path(sys.argv[2]); assert not OUT.exists(), OUT
T0, T1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (28.0, 40.0)
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{T0}", "-t", f"{T1 - T0}", "-i", M, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).copy()
W0 = json.load(open(E / "_build_v5final/vo_words.json"))["words"]; ref_w = [w for w in W0 if w["start"] >= T0 - 0.05 and w["end"] <= T1 + 0.05]
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8"); seg, _ = m.transcribe(x, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
W = [(w.word.strip(), round(float(w.start) + T0, 3), round(float(w.end) + T0, 3), round(float(w.probability), 3)) for s in seg for w in s.words]
norm = lambda s: re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("\u2019", "'")).split()
ref, hyp = norm(" ".join(w["word"] for w in ref_w)), norm(" ".join(w[0] for w in W)); sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
ops = [(t, " ".join(ref[i1:i2]), " ".join(hyp[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
R = {"master": M, "window_s": [T0, T1], "model": "faster-whisper medium.en int8", "ref": " ".join(ref), "hyp": " ".join(hyp), "ref_words": len(ref), "hyp_words": len(hyp), "diffs": ops, "words": W}
json.dump(R, open(OUT, "x"), indent=1); print({k: v for k, v in R.items() if k != "words"})
