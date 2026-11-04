#!/usr/bin/env python3
"""Germanicus v5c AUDIO (revision of v5b; owner notes via Vellum, 2026-10-27).
- SCORE: new cue (CC BY 4.0), one continuous window from --offset, ONE beat-aligned splice (--splice cut_t:cue_t:xf) into the cue's own
  quiet closing section so the ending (plates 10/2f/outro) is quiet and the cue resolves under the outro line. Light carve.
  Gentle rider (clamp +-RC dB, 3 dB/s cap) toward a designed ARC target, so the cue's lift at 'Piso chose force.' stays.
- MAIN VO: the v5b staged VO (_build_v5final/audio_v5b/vo_staged.wav) used sample-for-sample (untouched), padded.
- OUTRO VO: 'History remembers the victors. We remember the rest.' (Oliver, same settings), same stage/comp chain, integrated level
  matched to the main VO body (L01-L21), placed at --outro-t.
- SFX: louder, layered SeqC-only battle din (2 crowd-shout layers + 10 sword clashes, CC0 StarNinjas), short fades, ducked under key words.
- Level search: score as loud as possible while every key word >= 9 dB (house peak measure), 1-4 kHz frames >= 6 dB on >= 99 %,
  L22/L23 content words >= 12 dB; then SFX as loud as possible (<= --sfx-rel-max vs score) with SeqC key words >= 9 dB and all SeqC words >= 6 dB vs score+SFX.
Lean: no big intermediates; outputs FLAC 24-bit stems + AAC. Refuses overwrite."""
import argparse, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, resample_poly, fftconvolve
from scipy.ndimage import gaussian_filter1d
G = Path("/workspace/posterity/standalones/germanicus"); EDIT = G / "edit"
ap = argparse.ArgumentParser()
ap.add_argument("--music", required=True); ap.add_argument("--music-md5", required=True)
ap.add_argument("--offset", type=float, required=True); ap.add_argument("--splice", required=True)
ap.add_argument("--frames", type=int, default=3757); ap.add_argument("--outro-vo", required=True); ap.add_argument("--outro-t", type=float, default=120.60)
ap.add_argument("--sfx-duck-other-db", type=float, default=0.0); ap.add_argument("--seqc-score-dip-db", type=float, default=0.0); ap.add_argument("--sfx-duck-cap", type=float, default=18.0); ap.add_argument("--kw-duck-max", type=float, default=0.0); ap.add_argument("--frames-min", type=float, default=99.0); ap.add_argument("--speech-dip-db", type=float, default=4.0); ap.add_argument("--rider-clamp", type=float, default=3.0)
ap.add_argument("--arc", default="0:0,50.97:0,60.5:1.5,60.93:4.5,108.0:4.5")
ap.add_argument("--bed-start-db", type=float, default=10.0); ap.add_argument("--bed-step-db", type=float, default=0.5)
ap.add_argument("--sfx-rel-max", type=float, default=8.0); ap.add_argument("--sfx-duck-db", type=float, default=5.0); ap.add_argument("--sfx-carve-db", type=float, default=4.0)
ap.add_argument("--out", default=str(EDIT / "_build_v5c" / "audio")); ap.add_argument("--no-sfx", action="store_true")
A = ap.parse_args()
SR, FPS = 48000, 30; P = A.frames / FPS; NB = int(round(P * SR))
OUT = Path(A.out); OUT.mkdir(parents=True, exist_ok=False)
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def new(p):
    p = Path(p); assert not p.exists(), p; return p
VO_STAGED = EDIT / "_build_v5final/audio_v5b/vo_staged.wav"
assert md5f(A.music) == A.music_md5
WJ = json.load(open(G / "vo/final-vo-oliver-germanicus-v5_words.json")); words = [dict(word=w["word"], start=w["start"], end=w["end"], line=w["line"]) for w in WJ["words"]]
assert len(words) == 289
TL = json.load(open(EDIT / "_build_v5final/timeline.json")); SEG = {s["id"]: s for s in TL["segments"]}
SC0, SC1 = SEG["C"]["start"], SEG["C"]["end"]
# outro words (alignment of the chosen take), absolute times
al = json.load(open(str(A.outro_vo).replace(".wav", "_alignment.json"))); ch = al["characters"]; cs = al["character_start_times_seconds"]; ce = al["character_end_times_seconds"]
txt = "".join(ch); import re
yo, sro = sf.read(A.outro_vo, dtype="float64"); assert sro == SR
h = int(0.01 * SR); rr = np.array([np.sqrt((yo[i:i + h] ** 2).mean()) for i in range(0, len(yo) - h, h)]); dd = 20 * np.log10(rr + 1e-9); on = np.where(dd > dd.max() - 35)[0]
O_ON, O_OFF = on[0] * 0.01, on[-1] * 0.01 + 0.01
owords = []
for m in re.finditer(r"\S+", txt):
    st = cs[m.start()]; en = min(ce[m.end() - 1], O_OFF); st = max(st, O_ON) if not owords else st
    owords.append(dict(word=m.group(), start=A.outro_t + st, end=A.outro_t + en, line=24))
allw = words + owords
t_speech_end = words[-1]["end"]; o_end = owords[-1]["end"]
assert o_end + 0.5 <= P + 1e-6, ("outro line + 0.5 s tail does not fit", o_end, P)
KEY_NAMES = {"germanicus", "piso", "tacitus", "antioch", "armenia", "syria", "rome", "rome's", "senate", "spain", "bronze", "murder", "poisoned", "poisoning", "spells", "lead", "tablets",
             "walls", "sword", "dead", "rebel", "unproved", "killer", "accusers", "condemned", "judgement", "warships", "storm", "history", "victors", "rest"}
KEY = sorted(set([i for i, w in enumerate(allw) if w["word"].endswith((".", "?", "!", ":"))] + [i for i, w in enumerate(allw) if w["word"].strip(".,:;?!").lower() in KEY_NAMES]))
FUNC = {"the", "a", "was", "as", "he", "had", "his", "been"}
L22_23 = [i for i, w in enumerate(words) if w["line"] in (22, 23) and w["word"].strip(".,").lower() not in FUNC]
SEQC = [i for i, w in enumerate(allw) if SC0 <= w["start"] < SC1]
SEQC_KEY = [i for i in SEQC if i in KEY]
def ebur_arr(x):
    x = np.asarray(x, np.float32); x = x[:, None] if x.ndim == 1 else x
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[1]), "-i", "pipe:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=np.ascontiguousarray(x, np.float32).tobytes(), capture_output=True); I = TP = None; s = False
    for ln in p.stderr.decode().splitlines():
        if "Summary:" in ln: s = True
        if s and ln.strip().startswith("I:"): I = float(ln.split("I:")[1].split("LUFS")[0])
        if s and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return I, TP
def ffpipe(inargs, af, ch, x=None):
    cmd = ["ffmpeg", "-v", "error"] + inargs + (["-af", af] if af else []) + ["-ar", str(SR), "-ac", str(ch), "-f", "f32le", "pipe:1"]
    p = subprocess.run(cmd, input=None if x is None else np.ascontiguousarray(x, np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).reshape(-1, ch).astype(np.float64)
def rc(x): x = np.clip(x, 0, 1); return 0.5 - 0.5 * np.cos(np.pi * x)
t = np.arange(NB) / SR
# ---------------- VO: main (untouched samples) + outro line
vo = np.zeros(NB); vs, s_ = sf.read(VO_STAGED, dtype="float64"); assert s_ == SR; vo[:len(vs)] = vs[:NB]
assert np.abs(vs[int((t_speech_end + 0.2) * SR):]).max() < 1e-3, "main VO not silent after speech end"
BODY_B = [w for w in words if w["line"] == 21][-1]["end"] + 0.05
bodyI, _ = ebur_arr(vs[:int(BODY_B * SR)])
oI, _ = ebur_arr(yo)
oc = ffpipe(["-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "pipe:0"], f"volume={-16.0 - oI:.3f}dB,acompressor=threshold=0.2:ratio=2.5:attack=10:release=150:knee=2.8:makeup=1", 1, yo)[:, 0]
ocI, _ = ebur_arr(oc); oc = oc * 10 ** ((bodyI - ocI) / 20); ocI2, ocTP = ebur_arr(oc)
i0 = int(round(A.outro_t * SR)); assert not np.any(np.abs(vo[i0:]) > 1e-3); vo[i0:i0 + len(oc)] += oc[:NB - i0]
print(f"VO body I {bodyI:.2f}; outro raw {oI:.2f} -> staged/comp/matched {ocI2:.2f} LUFS (TP {ocTP})", flush=True)
# ---------------- SCORE
s_cut, s_cue, s_xf = map(float, A.splice.split(":"))
mdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", A.music], capture_output=True, text=True).stdout)
m1 = ffpipe(["-ss", f"{A.offset}", "-t", f"{P + 1}", "-i", A.music], None, 2)
m2 = ffpipe(["-ss", f"{s_cue - s_xf}", "-i", A.music], None, 2)   # cue from (s_cue - xf) placed at package (s_cut - xf)
def fit(x, a0):
    y = np.zeros((NB, 2)); n = min(len(x), NB - a0); y[a0:a0 + n] = x[:n]; return y
M1 = fit(m1, 0); M2 = fit(m2, int(round((s_cut - s_xf) * SR)))
w = np.clip((t - (s_cut - s_xf / 2)) / s_xf, 0, 1)
mus = M1 * np.cos(np.pi / 2 * w)[:, None] + M2 * np.sin(np.pi / 2 * w)[:, None]
cue_end_in_cut = s_cut + (mdur - s_cue)
b = ffpipe(["-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0"],
           "highpass=f=70,highpass=f=70,equalizer=f=320:t=q:w=1.2:g=-2.5,equalizer=f=1800:t=q:w=1.0:g=-2.0,afade=t=in:st=0:d=2.5:curve=cub", 2, mus)[:NB]
# light speech carve 900-4500 Hz across main VO + outro line
sp0, sp1 = words[0]["start"], o_end
env = np.where(t < sp0, rc((t - (sp0 - 0.25)) / 0.25), np.where(t > sp1, rc((sp1 + 0.25 - t) / 0.25), 1.0))
b = b - (1 - 10 ** (-A.speech_dip_db / 20)) * sosfiltfilt(butter(2, [900, 4500], "bandpass", fs=SR, output="sos"), b, axis=0) * env[:, None]
# gentle rider toward the ARC target (live 2.5 s .. splice-0.5); held outside
D = SR // 100; tk = np.arange(0, NB, D) / SR; LIVE0, LIVE1 = 2.5, s_cut - 0.5; live = (tk >= LIVE0) & (tk <= LIVE1)
il0, il1 = int(np.argmax(live)), int(np.where(live)[0][-1])
arc = np.array([[float(v) for v in p.split(":")] for p in A.arc.split(",")]); arc_k = np.interp(tk, arc[:, 0], arc[:, 1])
def cenv(x):
    m = x.mean(1); c = np.concatenate([[0], np.cumsum(m ** 2)]); k = np.arange(0, NB, D); hh = SR // 2; a_ = np.clip(k - hh, 0, NB); z_ = np.clip(k + hh, 0, NB)
    return 10 * np.log10((c[z_] - c[a_]) / np.maximum(z_ - a_, 1) + 1e-12)
def apply(x, gk): return x * (10 ** (np.interp(t, tk, gk) / 20))[:, None]
SL = 3.0 / 100
def ratelim(gk):
    y = gk.copy()
    for i in range(1, len(y)): y[i] = min(max(y[i], y[i - 1] - SL), y[i - 1] + SL)
    for i in range(len(y) - 2, -1, -1): y[i] = min(max(y[i], y[i + 1] - SL), y[i + 1] + SL)
    return y
e0 = cenv(b); base = float(np.median((e0 - arc_k)[live])); g2 = np.zeros(len(tk))
for _ in range(40):
    e = cenv(apply(b, g2)); err = (base + arc_k) - e; err[~live] = 0
    g2 = gaussian_filter1d(g2 + 0.7 * err, 20, mode="nearest"); g2[:il0] = g2[il0]; g2[il1 + 1:] = g2[il1]; g2 = ratelim(np.clip(g2, -A.rider_clamp, A.rider_clamp))
b = apply(b, g2)
bI, _ = ebur_arr(b[int(2.5 * SR):int(LIVE1 * SR)]); b = b * 10 ** ((-28.0 - bI) / 20)
# constant duck 3.5 dB, tail dip 3 dB (L21 end-1 -> L22 start+0.5) as v5b, short end taper (cue resolves itself)
T0d, T1d = TL["taildip"][0], TL["taildip"][1]
g = 10 ** (-3.5 / 20) * 10 ** (-3.0 * rc((t - T0d) / (T1d - T0d)) / 20)
FE = P - 0.03; FS = FE - 0.6; g = g * np.where(t < FS, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - FS) / (FE - FS), 0, 1))); g[t >= FE] = 0
b = b * g[:, None]
# ---------------- SFX (SeqC only)
SFX = G / "sfx"
assert md5f(SFX / "oga_starninjas_crowd_shouting_CC0.ogg") == "8ed53bd014f92a59eb4a93467df3a059" and md5f(SFX / "oga_starninjas_sword_clash_CC0.zip") == "3b82c7072f96dcec53d24072bf74a7b9"
def rd(f):
    y, sr = sf.read(str(f), dtype="float64", always_2d=True); y = y[:, :2] if y.shape[1] >= 2 else np.repeat(y, 2, 1)
    q = math.gcd(SR, sr); return y if sr == SR else resample_poly(y, SR // q, sr // q, axis=0)
L = int((SC1 - SC0) * SR); sx = np.zeros((L + SR, 2)); rng = np.random.default_rng(57)
sh = rd(SFX / "oga_starninjas_crowd_shouting_CC0.ogg"); shl = len(sh) / SR
for (st, gdb, swap) in ((3.0, 0.0, False), (min(14.0, shl - (L / SR) - 1.5), -2.0, True)):
    a_ = int(st * SR); seg = sh[a_:a_ + L + SR]; seg = seg / np.sqrt((seg ** 2).mean()); seg = seg[:, ::-1] if swap else seg; sx[:len(seg)] += seg * 10 ** (gdb / 20)
HITS = [(0.48, 4), (0.88, 6), (1.44, 1), (1.76, 7), (2.08, 3), (2.44, 9), (3.36, 5), (3.66, 2), (4.30, 8), (4.52, 10)]   # rel. to SeqC start; mostly in word gaps / weak words
for (dt, k) in HITS:
    c = rd(SFX / "sword_clash" / f"sword_clash.{k}.ogg"); c = c / np.abs(c).max(); gg = 10 ** (rng.uniform(-3, 0) / 20) * 2.2; pan = rng.uniform(-0.6, 0.6)
    j0 = int(dt * SR); n = min(len(c), len(sx) - j0); sx[j0:j0 + n, 0] += c[:n, 0] * gg * (1 - pan); sx[j0:j0 + n, 1] += c[:n, 1] * gg * (1 + pan)
sx = sosfiltfilt(butter(2, 180, "highpass", fs=SR, output="sos"), sx, axis=0); sx = sosfiltfilt(butter(4, 9000, "lowpass", fs=SR, output="sos"), sx, axis=0)
ir = rng.standard_normal((int(0.6 * SR), 2)) * np.exp(-np.arange(int(0.6 * SR)) / (0.15 * SR))[:, None]; ir /= np.sqrt((ir ** 2).sum(0))
wet = np.stack([fftconvolve(sx[:, c_], ir[:, c_])[:len(sx)] for c_ in range(2)], 1); sx = 0.8 * sx + 0.35 * wet
sx = sx - (1 - 10 ** (-A.sfx_carve_db / 20)) * sosfiltfilt(butter(2, [1000, 4000], "bandpass", fs=SR, output="sos"), sx, axis=0)
sx = sx[:L]; tt = np.arange(L) / SR; FADE = 0.15
sx = sx * rc(np.minimum(tt / FADE, (L / SR - tt) / FADE))[:, None]
SX_ND = sx.copy(); DUCKW = {i: (A.sfx_duck_db if i in SEQC_KEY else A.sfx_duck_other_db) for i in SEQC}
def build_sfxf(dw):   # word-locked duck: deeper under key words, lighter under the rest; full level in the gaps
    duck = np.ones(L)
    for i, dd_ in dw.items():
        a_, z_ = allw[i]["start"] - SC0, allw[i]["end"] - SC0
        duck = np.minimum(duck, 1 - (1 - 10 ** (-dd_ / 20)) * rc((tt - (a_ - 0.04)) / 0.04) * rc((z_ + 0.04 - tt) / 0.04))
    o = np.zeros((NB, 2)); o[j0:j0 + L] = SX_ND * duck[:, None]; return o
j0 = int(round(SC0 * SR)); SFXF = build_sfxf(DUCKW)
wa, wz = int((SC0 + 0.15) * SR), int((SC1 - 0.15) * SR)
def rms_db(x): return 10 * np.log10((np.asarray(x) ** 2).mean() + 1e-20)
SFX_UNIT = 10 ** ((rms_db(b[wa:wz]) - rms_db(SFXF[wa:wz])) / 20); SFXF = SFXF * SFX_UNIT   # unit = score rms in the window (base duck)
if A.no_sfx: SFXF[:] = 0
assert not np.any(SFXF[:int(SC0 * SR) - 1]) and not np.any(SFXF[int(SC1 * SR) + 1:])
# ---------------- mix / limiter / measures
SOS_BAND = butter(4, [1000, 4000], "bandpass", fs=SR, output="sos")
SDIP = np.zeros(NB); _t = np.arange(NB) / SR   # score dip inside SeqC so the battle din leads the bed (0.3 s raised-cosine ramps)
SDIP -= A.seqc_score_dip_db * rc((_t - (SC0 - 0.3)) / 0.3) * rc((SC1 + 0.3 - _t) / 0.3)
KWG = np.zeros(NB)   # score key-word duck (dB, <=0), built in loop 1
def kw_gain(req):
    g = np.zeros(NB)
    for i, r in req.items():
        a_, z_ = allw[i]["start"] - 0.3, allw[i]["end"] + 0.3
        g = np.minimum(g, -r * rc((t - (a_ - 0.12)) / 0.12) * rc((z_ + 0.12 - t) / 0.12))
    return g
def run(bed_db, sfx_db, mg):
    bed = b * 10 ** ((bed_db + KWG[:, None] + SDIP[:, None]) / 20); s2 = SFXF * 10 ** ((bed_db + sfx_db) / 20)
    pre = 0.70710678 * vo[:, None].repeat(2, 1) + bed + s2
    seven = np.concatenate([pre, 0.70710678 * vo[:, None] * 1e-3, bed * 1e-3, s2 * 1e-3], 1).astype(np.float32)
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "7", "-i", "pipe:0", "-af",
                        f"volume={mg:.3f}dB,aresample=192000,alimiter=limit={10 ** (-4.0 / 20):.4f}:attack=3:release=60:level=disabled:asc=1,aresample={SR}",
                        "-f", "f32le", "-ac", "7", "pipe:1"], input=seven.tobytes(), capture_output=True, check=True)
    o = np.frombuffer(p.stdout, np.float32).reshape(-1, 7).astype(np.float64)[:NB]
    return o[:, :2], o[:, 2] * 1e3, o[:, 3:5] * 1e3, o[:, 5:7] * 1e3
def margins(vL, other):
    pk = np.abs(other).max(1); rows = []
    for i, w in enumerate(allw):
        a_, z_ = int(w["start"] * SR), int(w["end"] * SR); a2, z2 = max(0, int((w["start"] - 0.3) * SR)), int((w["end"] + 0.3) * SR)
        rows.append((i, w["word"], round(w["start"], 3), round(float(20 * np.log10(np.abs(vL[a_:z_]).max() + 1e-12) - 20 * np.log10(pk[a2:z2].max() + 1e-12)), 2)))
    return rows
def band_margins(vL, other):   # v5b SFX convention: in-word 1-4 kHz band RMS, VO vs (score+SFX)
    vb_ = sosfiltfilt(SOS_BAND, vL) ** 2; ob_ = (sosfiltfilt(SOS_BAND, other, axis=0) ** 2).mean(1); out = {}
    for i in SEQC:
        a_, z_ = int(allw[i]["start"] * SR), int(allw[i]["end"] * SR)
        out[i] = round(float(10 * np.log10(vb_[a_:z_].mean() + 1e-20) - 10 * np.log10(ob_[a_:z_].mean() + 1e-20)), 2)
    return out
def frame_stats(vL, bL):
    vb = sosfiltfilt(SOS_BAND, vL); bbp = (sosfiltfilt(SOS_BAND, bL, axis=0) ** 2).mean(1); vbp = vb ** 2; hop = int(0.05 * SR); fr = []
    for w in allw:
        for k in range(int(w["start"] * SR), int(w["end"] * SR) - hop + 1, hop): fr.append((vbp[k:k + hop].mean(), bbp[k:k + hop].mean()))
    fr = np.array(fr); vdb = 10 * np.log10(fr[:, 0] + 1e-20); bdb = 10 * np.log10(fr[:, 1] + 1e-20); vo_ = vdb >= np.percentile(vdb, 99) - 35; m = (vdb - bdb)[vo_]
    return dict(n=int(vo_.sum()), pct_ge_6db=round(100 * float((m >= 6).mean()), 2), pct_lt_0db=round(100 * float((m < 0).mean()), 2), median=round(float(np.median(m)), 2), p5=round(float(np.percentile(m, 5)), 2))
def settle(bed_db, sfx_db, mg):
    for _ in range(16):
        mix, vL, bL, sL = run(bed_db, sfx_db, mg); I, TP = ebur_arr(mix)
        if abs(I + 14.0) <= 0.15: break
        mg += -14.0 - I
    return mix, vL, bL, sL, I, TP, mg
log = []; bed_db = A.bed_start_db; mg = 0.0
while True:   # 1) score level (SFX off in the search; SeqC handled in step 2)
    mix, vL, bL, sL, I, TP, mg = settle(bed_db, -60.0, mg)
    rows = margins(vL, bL); kmin = min(rows[i][3] for i in KEY)
    if A.kw_duck_max > 0:
        req = {}
        for _p in range(4):
            need = {i: 9.4 - rows[i][3] for i in KEY if rows[i][3] < 9.4}
            if not need: break
            for i, r in need.items(): req[i] = min(A.kw_duck_max, req.get(i, 0.0) + r)
            KWG[:] = kw_gain(req); mix, vL, bL, sL, I, TP, mg = settle(bed_db, -60.0, mg); rows = margins(vL, bL)
        kmin = min(rows[i][3] for i in KEY)
    fs_ = frame_stats(vL, bL); wc = min(rows[i][3] for i in L22_23)
    log.append(dict(step="score", bed_db=bed_db, kw_ducked=int((KWG < -0.05).sum() > 0) and len([1 for i in KEY if KWG[int(allw[i]['start'] * SR)] < -0.05]), kw_duck_min_db=round(float(KWG.min()), 2), I=I, TP=TP, key_min=kmin, frames=fs_, l22_23_min=wc)); print(log[-1], flush=True)
    if kmin >= 9.0 and fs_["pct_ge_6db"] >= A.frames_min and fs_["pct_lt_0db"] <= 5.0 and wc >= 12.0: break
    bed_db = round(bed_db - A.bed_step_db, 2); assert bed_db > -20; KWG[:] = 0
sfx_db = A.sfx_rel_max
while not A.no_sfx:   # 2) SFX level; per-word duck deepened as needed (cap) before stepping the level down
    mix, vL, bL, sL, I, TP, mg = settle(bed_db, sfx_db, mg)
    for _p in range(4):
        bm_ = band_margins(vL, sL); need = {i: (9.4 if i in SEQC_KEY else 6.4) - bm_[i] for i in SEQC}
        need = {i: r for i, r in need.items() if r > 0 and DUCKW[i] < A.sfx_duck_cap}
        if not need: break
        for i, r in need.items(): DUCKW[i] = min(A.sfx_duck_cap, DUCKW[i] + r)
        SFXF[:] = build_sfxf(DUCKW) * SFX_UNIT; mix, vL, bL, sL, I, TP, mg = settle(bed_db, sfx_db, mg)
    rc_ = band_margins(vL, sL); rows_b = margins(vL, bL); ck = min(rc_[i] for i in SEQC_KEY); ca = min(rc_[i] for i in SEQC)   # v5b convention: VO vs SFX stem, in-word 1-4 kHz RMS
    cb_ = band_margins(vL, bL + sL); comb_band = min(cb_[i] for i in SEQC)
    pk_ = margins(vL, bL + sL); log_pk = min(pk_[i][3] for i in SEQC)
    kmin = min(rows_b[i][3] for i in KEY)
    log.append(dict(step="sfx", sfx_db=sfx_db, word_duck_db={allw[i]['word']: round(DUCKW[i], 1) for i in SEQC}, I=I, TP=TP, seqc_key_min_band_vs_sfx=ck, seqc_all_min_band_vs_sfx=ca, seqc_all_min_band_vs_score_plus_sfx=comb_band, seqc_all_min_peak_vs_score_sfx=log_pk, key_min_vs_score=kmin)); print(log[-1], flush=True)
    if ck >= 9.0 and ca >= 6.0 and kmin >= 9.0: break
    sfx_db = round(sfx_db - 1.0, 2); assert sfx_db > -20
if A.no_sfx: mix, vL, bL, sL, I, TP, mg = settle(bed_db, -60.0, mg)
rows_b = margins(vL, bL); rows_c = margins(vL, bL + sL); band_c = band_margins(vL, bL + sL); band_s = band_margins(vL, sL)
for nm, x in (("mix", mix), ("stem_vo", vL), ("stem_score", bL), ("stem_sfx", sL)):
    sf.write(new(OUT / f"{nm}.flac"), np.clip(x, -1, 1).astype(np.float32), SR, subtype="PCM_24")
subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(OUT / "mix.flac"), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", str(new(OUT / "mix_aac256.m4a"))])
meta = dict(kw_duck=dict(max_db=A.kw_duck_max, min_db=float(KWG.min()), n_key_words_ducked=len([1 for i in KEY if KWG[int(allw[i]['start'] * SR)] < -0.05])), frames_min_pct=A.frames_min, package_s=P, frames=A.frames, music=A.music, music_md5=A.music_md5, music_duration_s=mdur, offset_s=A.offset, splice=dict(cut_t=s_cut, cue_t=s_cue, xf_s=s_xf, cue_natural_end_in_cut_s=cue_end_in_cut),
            window=f"cut 0..{s_cut} = cue {A.offset}..{A.offset + s_cut}; cut {s_cut}..{P:.3f} = cue {s_cue}..{s_cue + P - s_cut:.3f}",
            speech_dip_db=A.speech_dip_db, rider=dict(clamp_db=A.rider_clamp, slope_db_s=3.0, live=[LIVE0, LIVE1], arc=A.arc, gain_range=[float(g2.min()), float(g2.max())]),
            duck_db=3.5, tail_dip=TL["taildip"], end_taper=[FS, FE], bed_db=bed_db, sfx_db_rel_score_rms=sfx_db, master_gain_db=mg, I=I, TP=TP,
            outro=dict(t=A.outro_t, file=A.outro_vo, md5=md5f(A.outro_vo), on=O_ON, off=O_OFF, words=owords, body_I=bodyI, outro_I=ocI2),
            sfx=dict(window=[SC0, SC1], fade_s=FADE, hits=HITS, duck_key_db=A.sfx_duck_db, duck_other_db=A.sfx_duck_other_db, duck_ramp_s=0.04, word_duck_db={allw[i]['word']: round(DUCKW[i], 2) for i in SEQC}, duck_cap_db=A.sfx_duck_cap, seqc_score_dip_db=A.seqc_score_dip_db, carve_1_4k_db=A.sfx_carve_db, seqc_key=[allw[i]["word"] for i in SEQC_KEY]),
            key_words=len(KEY), key_min_vs_score=min(rows_b[i][3] for i in KEY), key_under_9=[rows_b[i] for i in KEY if rows_b[i][3] < 9],
            seqc_words_vs_score_sfx_peak=[rows_c[i] for i in SEQC], seqc_words_vs_score_sfx_band_1_4k=[(i, allw[i]['word'], band_c[i]) for i in SEQC], seqc_words_vs_sfx_band_1_4k=[(i, allw[i]['word'], band_s[i]) for i in SEQC], outro_words_vs_score=[rows_b[i] for i in range(len(words), len(allw))],
            l22_23_vs_score={rows_b[i][1]: rows_b[i][3] for i in L22_23}, frames_1_4k=frame_stats(vL, bL), lowest10=sorted(rows_b, key=lambda r: r[3])[:10], log=log, main_vo_source=str(VO_STAGED), main_vo_md5=md5f(VO_STAGED))
json.dump(meta, open(new(OUT / "audio_meta.json"), "x"), indent=1, default=float)
print("DONE", I, TP, "bed_db", bed_db, "sfx_db", sfx_db, flush=True)
