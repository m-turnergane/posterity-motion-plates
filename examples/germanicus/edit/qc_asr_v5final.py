#!/usr/bin/env python3
"""v5 final master ASR (faster-whisper medium.en int8, language en, condition_on_previous_text False) vs script-vo-v5-DRAFT.txt; proper nouns; new files only."""
import json, re, subprocess, difflib, numpy as np
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); OUT = E / "qc_rough_v5final/asr_master_v5final.json"; assert not OUT.exists()
M = "/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4"; SCRIPT = Path("/workspace/posterity/standalones/germanicus/raw/script-vo-v5-DRAFT.txt").read_text()
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", M, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).copy()
from faster_whisper import WhisperModel
m = WhisperModel("medium.en", device="cpu", compute_type="int8"); seg, _ = m.transcribe(x, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
W = [(w.word.strip(), round(float(w.start), 3), round(float(w.end), 3), round(float(w.probability), 3)) for s in seg for w in s.words]
norm = lambda s: re.sub(r"[^a-z0-9' ]", " ", s.lower().replace("\u2019", "'")).split()
ref, hyp = norm(SCRIPT), norm(" ".join(w[0] for w in W)); sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
ops = [(t, " ".join(ref[i1:i2]), " ".join(hyp[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal"]
errs = sum(max(i2 - i1, j2 - j1) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != "equal")
PN = {n: (sum(1 for r in ref if r.startswith(n)), sum(1 for h in hyp if h.startswith(n))) for n in ("germanicus", "piso", "tacitus", "antioch", "armenia", "syria", "senate", "celenderis")}
R = {"model": "faster-whisper medium.en int8", "ref_words": len(ref), "hyp_words": len(hyp), "wer_approx": round(errs / len(ref), 4), "diffs": ops, "proper_nouns_ref_hyp": PN, "words": W}
json.dump(R, open(OUT, "x"), indent=1); print({k: v for k, v in R.items() if k != "words"})
