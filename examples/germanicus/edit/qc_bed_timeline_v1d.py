#!/usr/bin/env python3
"""v1d bed constancy QC: examiner method (1 s RMS of the post-limiter bed stem, L/R mean, 0.25 s hop), v1c overlaid. Writes new files only."""
import json, subprocess, numpy as np, soundfile as sf, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); Q = E / "qc_rough_v1d"; Q.mkdir(exist_ok=True)
PNG, JS = Q / "bed_level_timeline_v1d.png", Q / "bed_level_v1d_stats.json"
for p in (PNG, JS): assert not p.exists(), p
SR = 48000; FADE = 64.5; FIN = 2.5
def env(p):
    x, sr = sf.read(p); assert sr == SR; m = x.mean(1) if x.ndim > 1 else x; c = np.concatenate([[0], np.cumsum(m ** 2)]); idx = np.arange(0, len(m) - SR + 1, SR // 4)
    return idx / SR, 10 * np.log10((c[idx + SR] - c[idx]) / SR + 1e-20)
def stats(T, L, t0, t1, label):
    mk = (T >= t0) & (T + 1 <= t1 + 1e-9); Ts, Ls = T[mk], L[mk]; med = float(np.median(Ls)); r1 = Ls[4:] - Ls[:-4]; hop = np.diff(Ls) * 4
    return dict(label=label, windows=int(mk.sum()), median_db=round(med, 2), max_dev_db=round(float(np.abs(Ls - med).max()), 2), max_dev_at_s=float(Ts[np.argmax(np.abs(Ls - med))]),
                min_db=round(float(Ls.min()), 2), max_db=round(float(Ls.max()), 2), max_rise_over_1s_db=round(float(r1.max()), 2), at_s=float(Ts[np.argmax(r1)]),
                max_rise_rate_0p25s_hop_db_per_s=round(float(hop.max()), 2), hop_at_s=float(Ts[np.argmax(hop)]))
T, L = env(E / "_build_v1d/audio/stem_bed_postlim.wav"); Tc, Lc = env(E / "_build_v1c/audio/stem_bed_postlim.wav")
Tm, Lm = env(E / "_build_v1d/audio/mix.wav")
S = {"method": "1 s RMS (window [t, t+1]) of stem_bed_postlim.wav, mean of L/R, 0.25 s hop, dBFS; constancy span = windows wholly inside [2.5 s, fade start 64.5 s]",
     "v1d": stats(T, L, FIN, FADE, "v1d 2.5-64.5"), "v1d_centred_label": stats(T + 0.5, L, FIN, FADE + 0.5, "v1d, centred label, centres 3.0-64.0 approx"),
     "v1c_same_span_for_reference": stats(Tc, Lc, FIN, FADE, "v1c 2.5-64.5")}
def ebur(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; o = o[o.find("Summary"):]
    g = lambda k, u: float(o.split(k)[1].split(u)[0])
    return {"I_LUFS": g("I:", "LUFS"), "LRA_LU": g("LRA:", "LU"), "TP_dBTP": g("Peak:", "dBFS")}
S["mix_wav_ebur128"] = ebur(E / "_build_v1d/audio/mix.wav"); S["mix_aac_ebur128"] = ebur(E / "_build_v1d/audio/mix_aac256.m4a")
fig, ax = plt.subplots(figsize=(15, 5.5), dpi=110)
ax.plot(Tc + 0.5, Lc, color="#b0b0b0", lw=1, label="v1c bed (post-limiter)")
ax.plot(T + 0.5, L, color="#c0392b", lw=1.6, label="v1d bed (post-limiter)")
ax.plot(Tm + 0.5, Lm, color="#2c3e50", lw=0.6, alpha=0.45, label="v1d full mix")
med = S["v1d"]["median_db"]; ax.axhspan(med - 1, med + 1, color="#c0392b", alpha=0.10, label=f"v1d median {med} dB +-1 dB")
ax.axhline(med, color="#c0392b", lw=0.6, ls="--")
for x, lab in ((FIN, "fade-in end 2.5 s"), (FADE, "bed fade 64.5 s"), (62.5, "cut 10 f1875"), (65.5, "outro f1965")): ax.axvline(x, color="k", lw=0.7, ls=":"); ax.text(x + 0.2, med + 7.3, lab, fontsize=7, rotation=90, va="top")
ax.set_xlim(0, 69); ax.set_ylim(med - 14, med + 8); ax.set_xlabel("time (s), plotted at window centre"); ax.set_ylabel("1 s RMS (dBFS)")
v = S["v1d"]; ax.set_title(f"Germanicus ROUGH v1d bed level (examiner 1 s RMS, 0.25 s hop): max dev {v['max_dev_db']} dB, max rise {v['max_rise_over_1s_db']} dB/1 s, "
                           f"max 0.25 s-hop rate {v['max_rise_rate_0p25s_hop_db_per_s']} dB/s (2.5-64.5 s)", fontsize=9)
ax.legend(loc="lower left", fontsize=8); ax.grid(alpha=0.25); fig.tight_layout(); fig.savefig(PNG)
json.dump(S, open(JS, "x"), indent=1); print(json.dumps(S, indent=1))
