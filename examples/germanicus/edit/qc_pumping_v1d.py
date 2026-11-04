#!/usr/bin/env python3
"""v1d music-bed pumping check (new files only). Short-term loudness = BS.1770 K-weighted, 400 ms window, 100 ms hop (momentary-style),
on: music_seg (raw source, pre-rider), bed_ridden (post rider/duck, pre-limiter), stem_bed_postlim (as heard). Gain rider = g1+g2 (100 Hz) + duck/fade curve.
Limiter gain reduction on the bed = postlim/ridden level difference (minus constant master gain)."""
import json, numpy as np, soundfile as sf, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import lfilter, welch, detrend
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); A = E / "_build_v1d/audio"; Q = E / "qc_rough_v1d"
PNG, JS = Q / "pumping_check_v1d.png", Q / "pumping_check_v1d.json"
for p in (PNG, JS): assert not p.exists(), p
SR = 48000; LIVE = (2.5, 64.5); HOP = 0.1; WIN = 0.4
# K-weighting @48k (BS.1770-4)
B1, A1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
B2, A2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
def st_loud(x):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    y = lfilter(B2, A2, lfilter(B1, A1, x, axis=0), axis=0); p = (y ** 2).sum(1)
    c = np.concatenate([[0], np.cumsum(p)]); n = int(WIN * SR); idx = np.arange(0, len(p) - n + 1, int(HOP * SR))
    return (idx + n / 2) / SR, -0.691 + 10 * np.log10((c[idx + n] - c[idx]) / n + 1e-20)
def rd(p): x, sr = sf.read(p, dtype="float64"); assert sr == SR; return x
raw, rid, post, vo = rd(A / "music_seg.wav"), rd(A / "bed_ridden.wav"), rd(A / "stem_bed_postlim.wav"), rd(A / "stem_vo_postlim.wav")
post = post[:, None] if post.ndim == 1 else post
T, Lraw = st_loud(raw[:len(post)]); _, Lrid = st_loud(rid[:len(post)]); _, Lpost = st_loud(post)
n = min(len(T), len(Lrid), len(Lpost)); T, Lraw, Lrid, Lpost = T[:n], Lraw[:n], Lrid[:n], Lpost[:n]
live = (T >= LIVE[0] + 0.2) & (T <= LIVE[1] - 0.2)
# gain rider (100 Hz) + duck/fade curve resampled to 100 Hz
tk, g1, g2 = np.load(A / "bed_rider_db_100hz.npy"); gc = np.load(A / "bed_gain_curve_db.npy")[:: SR // 100][: len(tk)]
grider = g1 + g2; gtot = grider + gc; gtot_T = np.interp(T, tk, gtot); grider_T = np.interp(T, tk, grider)
slope = np.gradient(gtot, tk); live_k = (tk >= LIVE[0]) & (tk <= LIVE[1])
# limiter GR on the bed (post - ridden, constant master gain removed by median)
gr = Lpost - Lrid; gr = gr - np.median(gr[live])
# VO onsets / offsets from the VO stem (50 ms RMS gate, -45 dBFS, merge gaps < 150 ms)
v = vo if vo.ndim == 1 else vo.mean(1); h = int(0.05 * SR); e = 10 * np.log10(np.convolve(v ** 2, np.ones(h) / h, "same")[::h // 2] + 1e-20); te = np.arange(len(e)) * (h // 2) / SR
on = e > -45; d = np.diff(on.astype(int)); ons, offs = te[1:][d == 1], te[1:][d == -1]
segs = []
for a in ons:
    z = offs[offs > a]; z = z[0] if len(z) else te[-1]
    if segs and a - segs[-1][1] < 0.15: segs[-1][1] = z
    else: segs.append([a, z])
segs = [s for s in segs if s[1] - s[0] >= 0.12 and LIVE[0] <= s[0] <= LIVE[1]]
ons = np.array([s[0] for s in segs]); offs = np.array([s[1] for s in segs if s[1] <= LIVE[1]])
def eta(L, ev, pre=0.6, post_=0.6):
    rows = []
    for x in ev:
        a, b = (T >= x - pre) & (T < x - 0.1), (T > x + 0.1) & (T <= x + post_)
        if a.any() and b.any(): rows.append(L[b].mean() - L[a].mean())
    r = np.array(rows); return dict(n=len(r), mean_db=round(float(r.mean()), 3), sd_db=round(float(r.std()), 3), max_abs_db=round(float(np.abs(r).max()), 3))
# swing per second: max-min of ST loudness in each 1 s window (0.1 s hop)
def swing(L):
    out = []
    for i in range(len(T)):
        mk = (T >= T[i]) & (T < T[i] + 1.0)
        if T[i] >= LIVE[0] and T[i] + 1 <= LIVE[1]: out.append((T[i], L[mk].max() - L[mk].min()))
    return np.array(out)
Sw_post, Sw_raw = swing(Lpost), swing(Lraw)
excess = Sw_post[:, 1] - Sw_raw[:, 1]     # swing ADDED by processing vs the source music
# modulation spectrum 1-4 Hz of the (detrended) ST loudness envelope, live span; ratio post/raw
def modband(L):
    f, P = welch(detrend(L[live]), fs=1 / HOP, nperseg=128); b = (f >= 1) & (f <= 4)
    return float(np.sqrt(P[b].sum() * (f[1] - f[0])))
# gain-rider modulation 1-4 Hz (dB rms)
fG, PG = welch(detrend(gtot[live_k]), fs=100, nperseg=1024); bG = (fG >= 1) & (fG <= 4)
corr_rider_vo = float(np.corrcoef(np.interp(tk[live_k], te, on.astype(float)), grider[live_k])[0, 1])
# worst 3: largest post-limiter 1 s swing (>=1.5 s apart), with context
order = np.argsort(-Sw_post[:, 1]); worst = []
for i in order:
    t0 = Sw_post[i, 0]
    if all(abs(t0 - w["t_s"]) >= 1.5 for w in worst):
        mk = (tk >= t0) & (tk <= t0 + 1); mT = (T >= t0) & (T <= t0 + 1)
        worst.append(dict(t_s=round(float(t0), 1), window=f"{t0:.1f}-{t0 + 1:.1f} s", post_swing_db=round(float(Sw_post[i, 1]), 2), source_swing_db=round(float(Sw_raw[i, 1]), 2),
                          rider_slope_max_db_per_s=round(float(np.abs(slope[mk]).max()), 2), limiter_gr_max_db=round(float(-gr[mT].min()), 2),
                          vo_event_within=bool(np.any(np.abs(np.concatenate([ons, offs]) - (t0 + 0.5)) <= 0.6))))
    if len(worst) == 3: break
S = dict(method="BS.1770 K-weighted ST loudness, 400 ms window, 100 ms hop; live span 2.5-64.5 s; VO events from stem_vo_postlim (50 ms RMS > -45 dBFS)",
         vo_onsets=len(ons), vo_offsets=len(offs),
         max_short_term_swing_per_1s_db=dict(postlim_bed=round(float(Sw_post[:, 1].max()), 2), at_s=round(float(Sw_post[np.argmax(Sw_post[:, 1]), 0]), 1),
                                             source_music=round(float(Sw_raw[:, 1].max()), 2), median_postlim=round(float(np.median(Sw_post[:, 1])), 2), median_source=round(float(np.median(Sw_raw[:, 1])), 2),
                                             max_excess_over_source_db=round(float(excess.max()), 2), excess_at_s=round(float(Sw_post[np.argmax(excess), 0]), 1)),
         gain_rider=dict(range_db=[round(float(grider[live_k].min()), 2), round(float(grider[live_k].max()), 2)], max_slope_db_per_s=round(float(np.abs(slope[live_k]).max()), 2),
                         max_slope_at_s=round(float(tk[live_k][np.argmax(np.abs(slope[live_k]))]), 2), pct_time_slope_gt_2dB_s=round(100 * float((np.abs(slope[live_k]) > 2).mean()), 2),
                         mod_1_4Hz_rms_db=round(float(np.sqrt(PG[bG].sum() * (fG[1] - fG[0]))), 3), corr_with_vo_gate=round(corr_rider_vo, 3)),
         limiter_gr_on_bed_db=dict(max=round(float(-gr[live].min()), 2), p99=round(float(-np.percentile(gr[live], 1)), 2)),
         vo_triggered_bed_change_db=dict(postlim_at_onsets=eta(Lpost, ons), postlim_at_offsets=eta(Lpost, offs), source_at_onsets=eta(Lraw, ons), source_at_offsets=eta(Lraw, offs),
                                         note="mean ST-loudness change (0.1-0.6 s after minus 0.6-0.1 s before each event); pumping would show a consistent negative onset / positive offset mean vs source"),
         envelope_mod_1_4Hz_rms_db=dict(postlim=round(modband(Lpost), 3), source=round(modband(Lraw), 3), ridden_prelim=round(modband(Lrid), 3)),
         worst3=worst)
on_m, off_m = S["vo_triggered_bed_change_db"]["postlim_at_onsets"]["mean_db"], S["vo_triggered_bed_change_db"]["postlim_at_offsets"]["mean_db"]
# the v1d rider is a deliberately fast bed-keyed leveler (slope >2 dB/s most of the time, uncorrelated with VO), so slope alone is not a pumping
# signature; a window is suspect when processing ADDS >2 dB of 1 s swing over the source, or the limiter takes >1.5 dB off the bed.
susp = [w for w in worst if w["post_swing_db"] - w["source_swing_db"] > 2.0 or w["limiter_gr_max_db"] > 1.5]
pump = (on_m < -1.0 and off_m > 1.0) or abs(S["gain_rider"]["corr_with_vo_gate"]) > 0.3 or S["envelope_mod_1_4Hz_rms_db"]["postlim"] > 1.5 * S["envelope_mod_1_4Hz_rms_db"]["source"]
S["verdict_basis"] = dict(vo_keyed_pumping=bool(pump), windows_with_added_swing=[w["window"] for w in susp])
S["verdict"] = ("suspect at " + ", ".join(f"{w['t_s']}s" for w in susp)) if (pump or susp) else "likely clean"
fig, ax = plt.subplots(3, 1, figsize=(15, 9), dpi=100, sharex=True)
ax[0].plot(T, Lraw, color="#999", lw=0.8, label="source music (pre-rider)"); ax[0].plot(T, Lpost, color="#c0392b", lw=1, label="bed as heard (post-limiter)")
for s in segs: ax[0].axvspan(s[0], s[1], color="#3498db", alpha=0.08)
for w in worst: ax[0].axvline(w["t_s"] + 0.5, color="k", ls=":", lw=0.8)
ax[0].set_ylabel("ST loudness LUFS (0.4 s)"); ax[0].legend(fontsize=8, loc="lower left"); ax[0].set_title(f"v1d bed pumping check -- verdict: {S['verdict']} (blue = VO active)", fontsize=10)
ax[1].plot(tk, grider, color="#27ae60", label="rider g1+g2 (dB)"); ax[1].plot(tk, gc, color="#8e44ad", lw=0.8, label="duck/fade curve (dB)"); ax[1].plot(T, -gr, color="#e67e22", lw=0.8, label="limiter GR on bed (dB, +=reduction)")
ax[1].legend(fontsize=8); ax[1].set_ylabel("dB"); ax[1].set_ylim(-12, 12)
ax[2].plot(Sw_post[:, 0] + 0.5, Sw_post[:, 1], color="#c0392b", label="post-limiter 1 s swing"); ax[2].plot(Sw_raw[:, 0] + 0.5, Sw_raw[:, 1], color="#999", label="source 1 s swing")
ax[2].set_ylabel("max-min in 1 s (dB)"); ax[2].set_xlabel("s"); ax[2].legend(fontsize=8)
for a in ax: a.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(PNG); json.dump(S, open(JS, "x"), indent=1); print(json.dumps(S, indent=1))
