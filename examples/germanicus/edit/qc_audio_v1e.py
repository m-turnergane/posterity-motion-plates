#!/usr/bin/env python3
"""v1e bed audio verification vs v1d (new files only): examiner house measure (1 s RMS, 0.25 s hop) mono / L / R, examiner stereo 1 s K-weighted loudness,
400 ms ST max swing per 1 s window (20.4 s, 61.0 s called out), examiner word margin (VO peak in word vs max |L|,|R| bed in word +-0.3 s), rider slope."""
import json, numpy as np, soundfile as sf, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import lfilter
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); Q = E / "qc_rough_v1e"; JS, PNG = Q / "audio_check_v1e.json", Q / "audio_check_v1e.png"
for p in (JS, PNG): assert not p.exists(), p
SR = 48000
B1, A1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
B2, A2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
def kst(x, win, hop=0.1):
    x = x[:, None] if x.ndim == 1 else x; y = lfilter(B2, A2, lfilter(B1, A1, x, axis=0), axis=0); p = (y ** 2).sum(1)
    c = np.concatenate([[0], np.cumsum(p)]); n = int(win * SR); i = np.arange(0, len(p) - n + 1, int(hop * SR)); return (i + n / 2) / SR, -0.691 + 10 * np.log10((c[i + n] - c[i]) / n + 1e-20)
def rms1(x):
    c = np.concatenate([[0], np.cumsum(x ** 2)]); i = np.arange(0, len(x) - SR, SR // 4); return i / SR, 10 * np.log10((c[i + SR] - c[i]) / SR + 1e-20)
def sp(t, l, t0, t1):
    m = (t >= t0) & (t + 1 <= t1 + 1e-9); v = l[m]; med = np.median(v)
    return dict(spread_maxmin_db=round(float(v.max() - v.min()), 2), p95_p5_db=round(float(np.percentile(v, 95) - np.percentile(v, 5)), 2), sd_db=round(float(v.std()), 2),
                max_dev_db=round(float(np.abs(v - med).max()), 2), max_dev_at_s=float(t[m][np.argmax(np.abs(v - med))]), pct_within_0p75_db=round(100 * float((np.abs(v - med) <= 0.75).mean()), 1))
def swing_at(T, L, t0, t1):   # max over 1 s windows starting in [t0,t1] of (max-min) 400 ms ST
    best = (0, 0)
    for s in np.arange(t0, t1 + 1e-9, 0.1):
        m = (T >= s) & (T < s + 1.0); v = L[m].max() - L[m].min()
        if v > best[0]: best = (float(v), float(s))
    return dict(max_swing_db=round(best[0], 2), window_start_s=round(best[1], 1))
W = json.load(open(E / "_build_v1e/vo_words.json"))["words"]
OUT = {"method": {"house_1s": "1 s RMS [t,t+1], 0.25 s hop, dBFS, post-limiter bed stem; span = windows wholly in [3, 64] s (and [30, 64] s)",
                  "examiner_K1s": "BS.1770 K-weighted stereo (L+R power) 1 s window, 0.1 s hop (reproduces the examiner's -25.2 LUFS at 61.0 s on v1d)",
                  "st400": "BS.1770 K-weighted stereo 400 ms, 0.1 s hop; max-min within 1 s windows",
                  "word_margin": "VO-stem peak inside the word minus max(|L|,|R|) bed-stem peak in the word +-0.3 s, post-limiter (reproduces examiner 8.4 / 8.5 dB on v1d)"}}
fig, ax = plt.subplots(4, 1, figsize=(15, 12), dpi=100, sharex=True)
for v, col in (("v1d", "#999"), ("v1e", "#c0392b")):
    A = E / f"_build_{v}/audio"; b, _ = sf.read(A / "stem_bed_postlim.wav"); vo, _ = sf.read(A / "stem_vo_postlim.wav"); raw, _ = sf.read(A / "music_seg.wav"); raw = raw[:len(b)]
    R = {}
    for nm, x in (("mono", b.mean(1)), ("L", b[:, 0]), ("R", b[:, 1])):
        t, l = rms1(x); R[nm] = {"3-64": sp(t, l, 3, 64), "30-64": sp(t, l, 30, 64)}
        if nm != "mono": ax[1 if nm == "L" else 2].plot(t + 0.5, l, color=col, lw=0.9, label=f"{v} {nm} 1 s RMS")
        else: ax[0].plot(t + 0.5, l, color=col, lw=0.9, label=f"{v} mono 1 s RMS")
    T1, K1 = kst(b, 1.0); T4, K4 = kst(b, 0.4); _, K4raw = kst(raw, 0.4)
    win = lambda t0, t1, T=T1, K=K1: (lambda m: dict(swing_db=round(float(K[m].max() - K[m].min()), 2), max_lufs=round(float(K[m].max()), 2), max_at_s=round(float(T[m][np.argmax(K[m])]), 2)))((T >= t0) & (T <= t1))
    R["examiner_K1s"] = {"59-62.5": win(59, 62.5), "19.8-21.6": win(19.8, 21.6), "3-64": win(3, 64), "at_61.0_lufs": round(float(K1[np.argmin(np.abs(T1 - 61.0))]), 2)}
    R["st400_max_swing_per_1s"] = {"20.4_window (19.9-20.9 start)": swing_at(T4, K4, 19.9, 20.9), "source_20.4": swing_at(T4, K4raw, 19.9, 20.9),
                                   "61.0_window (60.0-61.0 start)": swing_at(T4, K4, 60.0, 61.0), "source_61.0": swing_at(T4, K4raw, 60.0, 61.0), "whole 3-63": swing_at(T4, K4, 3, 63), "source whole 3-63": swing_at(T4, K4raw, 3, 63)}
    ax[3].plot(T4, K4, color=col, lw=0.8, label=f"{v} 400 ms ST stereo")
    rows = {}
    for i, w in enumerate(W):
        a, z = int(w["start"] * SR), int(w["end"] * SR); a2, z2 = max(0, int((w["start"] - .3) * SR)), int((w["end"] + .3) * SR)
        rows[i] = (w["word"], round(w["start"], 2), round(float(20 * np.log10(np.abs(vo[a:z]).max()) - 20 * np.log10(np.abs(b[a2:z2]).max())), 2))
    R["word_margin"] = {"and_60.31": rows[140][2], "to_60.78": rows[142][2], "words_59_62": [rows[i] for i in rows if 59 <= rows[i][1] <= 62.5],
                        "min_all_words": min(rows.values(), key=lambda r: r[2]), "n_words_under_12": sum(r[2] < 12 for r in rows.values())}
    tk, g1, g2 = np.load(A / "bed_rider_db_100hz.npy"); gl = (tk >= 2.5) & (tk <= 64.5); sl = np.abs(np.diff(g1 + g2)) * 100
    R["rider"] = {"max_slope_db_per_s": round(float(sl[gl[1:]].max()), 3), "range_db": [round(float((g1 + g2)[gl].min()), 2), round(float((g1 + g2)[gl].max()), 2)]}
    corr = np.corrcoef(b[3 * SR:64 * SR, 0], b[3 * SR:64 * SR, 1])[0, 1]; R["LR_correlation_3_64"] = round(float(corr), 3)
    OUT[v] = R
for a in ax: a.grid(alpha=.25); a.legend(fontsize=8, loc="lower left"); [a.axvspan(x0, x1, color="#3498db", alpha=.08) for x0, x1 in ((19.9, 21.9), (59, 62.5))]
ax[0].set_title("v1e vs v1d bed (post-limiter): house 1 s RMS mono / L / R, and 400 ms ST stereo; blue = 20.4 s and 61.0 s windows"); ax[3].set_xlabel("s"); ax[3].set_xlim(0, 69)
fig.tight_layout(); fig.savefig(PNG); json.dump(OUT, open(JS, "x"), indent=1)
for v in ("v1d", "v1e"):
    R = OUT[v]; print(v, {k: R[k]["3-64"]["spread_maxmin_db"] for k in ("mono", "L", "R")}, "p95-p5", {k: R[k]["3-64"]["p95_p5_db"] for k in ("mono", "L", "R")}, "sd", {k: R[k]["3-64"]["sd_db"] for k in ("mono", "L", "R")})
    print("   30-64", {k: R[k]["30-64"]["spread_maxmin_db"] for k in ("mono", "L", "R")}); print("   K1s", R["examiner_K1s"]); print("   st400", R["st400_max_swing_per_1s"]); print("   words", R["word_margin"]["and_60.31"], R["word_margin"]["to_60.78"], R["word_margin"]["min_all_words"], R["word_margin"]["n_words_under_12"]); print("   rider", R["rider"])
