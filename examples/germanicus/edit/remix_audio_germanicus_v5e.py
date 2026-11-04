#!/usr/bin/env python3
"""Germanicus v5e AUDIO = stem remix of the v5c build (G/edit/_build_v5c/audio, made by build_audio_germanicus_v5c.py). Vellum-approved notes 2026-10-27:
 1) SCORE stem +GAIN dB from ~112 s to the end (raised-cosine ramp RAMP0->RAMP1), nothing else on the score touched (60.9-108 swell, ducks, taper unchanged).
 2) SFX stem: extra -DUCK dB ONLY under 'His' (62.449-62.612) and 'fought' (63.041-63.308); 20 ms attack/release, 40 ms pad as in the v5c word duck.
VO stem untouched. mix = vo + score' + sfx' (v5c stems sum to v5c mix.flac within 2.4e-7). No limiter needed if TP <= -1 dBTP (asserted).
Writes ONLY new files into --out: mix_aac192.m4a (preview) [+ mix_aac256.m4a with --aac256 for the master] + audio_meta.json. Refuses overwrite.
argv: --gain 3.5 --ramp 112.0:113.5 --duck 2.5 [--aac256] [--measure-only]"""
import argparse, json, subprocess, hashlib
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
E = Path("/workspace/posterity/standalones/germanicus/edit"); SRC = E / "_build_v5c/audio"; SR = 48000
ap = argparse.ArgumentParser(); ap.add_argument("--gain", type=float, default=3.5); ap.add_argument("--ramp", default="112.0:113.5"); ap.add_argument("--duck", type=float, default=2.5)
ap.add_argument("--out", default=str(E / "_build_v5e/audio")); ap.add_argument("--aac256", action="store_true"); ap.add_argument("--measure-only", action="store_true"); A = ap.parse_args()
MD5 = {"stem_vo.flac": "", "stem_score.flac": "", "stem_sfx.flac": ""}
vo, _ = sf.read(SRC / "stem_vo.flac"); sc, _ = sf.read(SRC / "stem_score.flac"); sx, _ = sf.read(SRC / "stem_sfx.flac"); NB = len(vo); t = np.arange(NB) / SR
meta5c = json.load(open(SRC / "audio_meta.json"))
WJ = json.load(open(E.parent / "vo/final-vo-oliver-germanicus-v5_words.json")); words = [dict(word=w["word"], start=w["start"], end=w["end"], line=w["line"]) for w in WJ["words"]]
allw = words + meta5c["outro"]["words"]
def rc(x): x = np.clip(x, 0, 1); return 0.5 - 0.5 * np.cos(np.pi * x)
r0, r1 = map(float, A.ramp.split(":"))
gsc = 10 ** (A.gain * rc((t - r0) / (r1 - r0)) / 20)
DUCKW = {"His": (62.449, 62.612), "fought": (63.041, 63.308)}
for nm, (a, z) in DUCKW.items(): assert any(w["word"] == nm and abs(w["start"] - a) < 1e-3 and abs(w["end"] - z) < 1e-3 for w in allw), nm
gsx = np.ones(NB)
for a, z in DUCKW.values(): gsx = np.minimum(gsx, 1 - (1 - 10 ** (-A.duck / 20)) * rc((t - (a - 0.04 - 0.02)) / 0.02) * rc((z + 0.04 + 0.02 - t) / 0.02))
sc2 = sc * gsc[:, None]; sx2 = sx * gsx[:, None]
mix0 = vo[:, None] + sc + sx; mix1 = vo[:, None] + sc2 + sx2
def ebur(x, extra=""):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0", "-af", (extra + "," if extra else "") + "ebur128=peak=true", "-f", "null", "-"],
                       input=np.ascontiguousarray(x, np.float32).tobytes(), capture_output=True); I = TP = None; s = False
    for ln in p.stderr.decode().splitlines():
        if "Summary:" in ln: s = True
        if s and ln.strip().startswith("I:"): I = float(ln.split("I:")[1].split("LUFS")[0])
        if s and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return I, TP
PHONE = "highpass=f=300:poles=2,highpass=f=300:poles=2,lowpass=f=8000:poles=2"   # small phone speaker: no lows below ~300 Hz
def st(x): return np.repeat(x[:, None], 2, 1) if x.ndim == 1 else x
SOS_BAND = butter(4, [1000, 4000], "bandpass", fs=SR, output="sos")
def peak_margin(i, other):
    w = allw[i]; a, z = int(w["start"] * SR), int(w["end"] * SR); a2, z2 = int((w["start"] - 0.3) * SR), int((w["end"] + 0.3) * SR)
    return round(float(20 * np.log10(np.abs(vo[a:z]).max() + 1e-12) - 20 * np.log10(np.abs(other[a2:z2]).max() + 1e-12)), 2)
def band_margin(i, other):
    w = allw[i]; a, z = int(w["start"] * SR) - SR, int(w["end"] * SR) + SR   # filter a padded slice
    v = sosfiltfilt(SOS_BAND, vo[a:z]) ** 2; o = (sosfiltfilt(SOS_BAND, other[a:z], axis=0) ** 2).mean(1); k0, k1 = SR, len(v) - SR
    return round(float(10 * np.log10(v[k0:k1].mean() + 1e-20) - 10 * np.log10(o[k0:k1].mean() + 1e-20)), 2)
WIN = {"L21 tail 108.0-112.45": (108.0, 112.45), "L22 112.9-116.15": (112.9, 116.15), "L23 116.6-119.5": (116.6, 119.5), "outro 120.6-124.75": (120.6, 124.75), "108-125.23": (108.0, NB / SR)}
def windows(s_, x_):
    out = {}
    for k, (a, z) in WIN.items():
        a_, z_ = int(a * SR), int(z * SR); r = {}
        for band, fl in (("full", ""), ("phone", PHONE)):
            vI, _ = ebur(st(vo)[a_:z_], fl); sI, _ = ebur(s_[a_:z_], fl); mI, _ = ebur(x_[a_:z_], fl)
            r[band] = dict(vo_LUFS=vI, score_LUFS=sI, score_minus_vo_LU=round(sI - vI, 1), mix_LUFS=mI)
        out[k] = r
    return out
KEYN = {"germanicus", "piso", "rome", "murder", "rebel", "unproved", "killer", "condemned", "history", "victors", "rest", "force", "troops", "lost"}
LATE = [i for i, w in enumerate(allw) if w["start"] >= 112.9]
SEQ = [i for i, w in enumerate(allw) if w["word"].strip(".").lower() in ("his", "fought", "force") and 60.9 <= w["start"] < 65.6]
R = dict(params=vars(A), src=str(SRC))
for tag, s_, x_, mx in (("v5c", sc, sx, mix0), ("v5e", sc2, sx2, mix1)):
    I, TP = ebur(mx); r = dict(I=I, TP=TP, sample_peak_dBFS=round(float(20 * np.log10(np.abs(mx).max())), 2))
    r["late_words_peak_vs_score"] = [(allw[i]["word"], allw[i]["start"], peak_margin(i, s_), allw[i]["word"].strip(".,").lower() in KEYN or allw[i]["word"].endswith(".")) for i in LATE]
    r["l21_murder_peak_vs_score"] = [(w["word"], w["start"], peak_margin(i, s_)) for i, w in enumerate(allw) if 110.6 <= w["start"] < 112.9]
    r["seqc_his_fought_force"] = {allw[i]["word"]: dict(band_vs_score_sfx=band_margin(i, s_ + x_), band_vs_sfx=band_margin(i, x_), peak_vs_score_sfx=peak_margin(i, s_ + x_)) for i in SEQ}
    r["seqc_all_band_vs_score_sfx"] = {allw[i]["word"]: band_margin(i, s_ + x_) for i, w in enumerate(allw) if 60.9 <= w["start"] < 65.6}
    r["windows"] = windows(s_, mx); R[tag] = r
    print(tag, I, TP, flush=True)
vI_body, _ = ebur(st(vo)[:int(112.45 * SR)]); vI_l2223, _ = ebur(st(vo)[int(112.9 * SR):int(119.5 * SR)]); R["vo_body_I"] = vI_body; R["vo_L22_23_I"] = vI_l2223
R["diff_outside"] = dict(score_max_abs_before_ramp=float(np.abs(sc2 - sc)[: int(r0 * SR)].max()), sfx_changed_span_s=[float(t[np.where(gsx < 1)[0][0]]), float(t[np.where(gsx < 1)[0][-1]])])
assert R["v5e"]["TP"] <= -1.0, R["v5e"]["TP"]
print(json.dumps({k: R[k] for k in ("vo_body_I", "vo_L22_23_I", "diff_outside")}))
if A.measure_only: print(json.dumps(R, indent=0, default=float)); raise SystemExit
OUT = Path(A.out); OUT.mkdir(parents=True, exist_ok=False)
pcm = np.ascontiguousarray(mix1, np.float32).tobytes()
for br in (["192k"] + (["256k"] if A.aac256 else [])):
    o = OUT / f"mix_aac{br[:-1]}.m4a"; assert not o.exists()
    subprocess.run(["ffmpeg", "-n", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0", "-c:a", "aac", "-b:a", br, "-ar", "48000", "-ac", "2", str(o)], input=pcm, check=True)
    R[f"aac{br}_md5"] = hashlib.md5(o.read_bytes()).hexdigest()
R["mix_pcm_f32_md5"] = hashlib.md5(pcm).hexdigest()
json.dump(R, open(OUT / "audio_meta.json", "x"), indent=1, default=float); print("DONE", R["mix_pcm_f32_md5"])
