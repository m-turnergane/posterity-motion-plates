#!/usr/bin/env python3
"""v5 final audio QC (from qc_audio_v1f.py + qc_pumping_v1f.py; new files only).
Bed constancy (house 1 s RMS, 0.25 s hop) mono/L/R; 400 ms / 3 s ST stereo; word margins; rider slope; pumping (VO-keyed bed change, 1-4 Hz envelope modulation,
1 s swing added over the source); last-two-lines loudness vs the rest (master, VO stem, bed stem)."""
import json, subprocess, numpy as np, soundfile as sf, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import lfilter, welch, detrend
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); B = E / "_build_v5final"; A = B / "audio"; Q = E / "qc_rough_v5final"
M = "/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4"
JS, PNG = Q / "audio_check_v5final.json", Q / "audio_check_v5final.png"
for p in (JS, PNG): assert not p.exists(), p
SR = 48000; AM = json.load(open(A / "audio_meta.json")); TL = json.load(open(B / "timeline.json")); W = json.load(open(B / "vo_words.json"))["words"]
TD0, TD1, _ = TL["taildip"]; FS, FE = TL["fade"]; LIVE = (2.5, TD0)
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
def ebur(x):
    x = np.asarray(x, np.float32); x = x[:, None] if x.ndim == 1 else x
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[1]), "-i", "pipe:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=np.ascontiguousarray(x).tobytes(), capture_output=True).stderr.decode(); o = o[o.find("Summary"):]
    return float(o.split("I:")[1].split("LUFS")[0]), float(o.split("Peak:")[1].split("dBFS")[0])
b, _ = sf.read(A / "stem_bed_postlim.wav"); vo, _ = sf.read(A / "stem_vo_postlim.wav"); raw, _ = sf.read(A / "music_seg.wav"); raw = raw[:len(b)]
mx = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", M, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).reshape(-1, 2).astype(np.float64)
OUT = {"method": "house 1 s RMS (0.25 s hop) on the post-limiter bed stem, live span [3, tail-dip start]; BS.1770 400 ms / 3 s ST; word margin = VO peak in word - max(|L|,|R|) bed peak in word +-0.3 s",
       "bed_window": AM["music_window_s"], "bed_loop": AM["bed_loop"], "live_span_s": [3, TD0], "tail_dip": AM["tail_dip"], "fade": [FS, FE]}
R = {}
fig, ax = plt.subplots(4, 1, figsize=(16, 13), dpi=90, sharex=True)
for nm, x in (("mono", b.mean(1)), ("L", b[:, 0]), ("R", b[:, 1])):
    t, l = rms1(x); R[nm] = {"live": sp(t, l, 3, TD0), "3-30": sp(t, l, 3, 30), "30-TD0": sp(t, l, 30, TD0)}
    ax[0].plot(t + 0.5, l, lw=0.9, label=f"bed {nm} 1 s RMS")
tr, lr_ = rms1(raw.mean(1)); ax[0].plot(tr + 0.5, lr_ - np.median(lr_) + np.median(rms1(b.mean(1))[1]), color="#999", lw=0.7, label="source music (offset to bed median)")
T4, K4 = kst(b, 0.4); _, K4raw = kst(raw, 0.4); T3, K3 = kst(b, 3.0); _, K3raw = kst(raw, 3.0)
m3 = (T3 - 1.5 >= 3) & (T3 + 1.5 <= TD0); R["st3s"] = {"range_db": round(float(np.ptp(K3[m3])), 2), "p95_p5_db": round(float(np.percentile(K3[m3], 95) - np.percentile(K3[m3], 5)), 2),
                                                    "source_range_db": round(float(np.ptp(K3raw[m3])), 2), "median_lufs": round(float(np.median(K3[m3])), 2)}
def swing(T, L, t0, t1):
    out = []
    for s in np.arange(t0, t1 - 1 + 1e-9, 0.1):
        m = (T >= s) & (T < s + 1.0); out.append((float(s), float(L[m].max() - L[m].min())))
    return np.array(out)
Sw, SwR = swing(T4, K4, 3, TD0), swing(T4, K4raw, 3, TD0); exc = Sw[:, 1] - SwR[:, 1]
R["st400_1s_swing"] = {"max_db": round(float(Sw[:, 1].max()), 2), "at_s": round(float(Sw[np.argmax(Sw[:, 1]), 0]), 1), "source_max_db": round(float(SwR[:, 1].max()), 2),
                       "median_db": round(float(np.median(Sw[:, 1])), 2), "max_added_over_source_db": round(float(exc.max()), 2), "added_at_s": round(float(Sw[np.argmax(exc), 0]), 1)}
# source dip ~125-135 s of the cue = master 5-15 s: did the rider level it?
R["source_dip_5_15s"] = {"source_1s_rms_range_db": round(float(np.ptp(lr_[(tr >= 3) & (tr <= 16)])), 2), "bed_1s_rms": sp(*rms1(b.mean(1)), 3, 17)}
rows = []
for i, w in enumerate(W):
    a, z = int(w["start"] * SR), int(w["end"] * SR); a2, z2 = max(0, int((w["start"] - .3) * SR)), int((w["end"] + .3) * SR)
    rows.append((i, w["word"], round(w["start"], 2), round(float(20 * np.log10(np.abs(vo[a:z]).max() + 1e-12) - 20 * np.log10(np.abs(b[a2:z2]).max() + 1e-12)), 2)))
R["word_margin"] = {"min": min(rows, key=lambda r: r[3]), "n_under_12": sum(r[3] < 12 for r in rows), "n_under_9": sum(r[3] < 9 for r in rows), "lowest5": sorted(rows, key=lambda r: r[3])[:5],
                    "L22_L23": [r for r in rows if W[r[0]]["line"] >= 22]}
tk, g1, g2 = np.load(A / "bed_rider_db_100hz.npy"); gc = np.load(A / "bed_gain_curve_db.npy")[:: SR // 100][: len(tk)]; gl = (tk >= 2.5) & (tk <= FS)
rid = g1 + g2; sl = np.abs(np.diff(rid)) * 100; slt = np.abs(np.diff(rid + gc)) * 100
R["rider"] = {"max_slope_db_per_s": round(float(sl[gl[1:]].max()), 3), "range_db": [round(float(rid[gl].min()), 2), round(float(rid[gl].max()), 2)],
              "max_total_gain_slope_incl_taildip_db_per_s": round(float(slt[(tk[1:] >= 2.5) & (tk[1:] <= FS)].max()), 3)}
R["LR_correlation_live"] = round(float(np.corrcoef(b[3 * SR:int(TD0 * SR), 0], b[3 * SR:int(TD0 * SR), 1])[0, 1]), 3)
# ---- pumping
v = vo if vo.ndim == 1 else vo.mean(1); h = int(0.05 * SR); e = 10 * np.log10(np.convolve(v ** 2, np.ones(h) / h, "same")[::h // 2] + 1e-20); te = np.arange(len(e)) * (h // 2) / SR
on = e > -45; d = np.diff(on.astype(int)); ons_, offs_ = te[1:][d == 1], te[1:][d == -1]; vs = []
for a in ons_:
    z = offs_[offs_ > a]; z = z[0] if len(z) else te[-1]
    if vs and a - vs[-1][1] < 0.15: vs[-1][1] = z
    else: vs.append([a, z])
vs = [s for s in vs if s[1] - s[0] >= 0.12 and LIVE[0] <= s[0] <= LIVE[1]]; ons = np.array([s[0] for s in vs]); offs = np.array([s[1] for s in vs if s[1] <= LIVE[1]])
def eta(L, ev):
    r = []
    for x in ev:
        a, bb = (T4 >= x - .6) & (T4 < x - .1), (T4 > x + .1) & (T4 <= x + .6)
        if a.any() and bb.any(): r.append(L[bb].mean() - L[a].mean())
    r = np.array(r); return dict(n=len(r), mean_db=round(float(r.mean()), 3), sd_db=round(float(r.std()), 3))
live4 = (T4 >= LIVE[0] + .2) & (T4 <= LIVE[1] - .2)
def modband(L):
    f, P = welch(detrend(L[live4]), fs=10, nperseg=128); bb = (f >= 1) & (f <= 4); return float(np.sqrt(P[bb].sum() * (f[1] - f[0])))
corr = float(np.corrcoef(np.interp(tk[gl], te, on.astype(float)), rid[gl])[0, 1])
PM = dict(vo_onsets=len(ons), bed_change_at_vo_onsets=eta(K4, ons), bed_change_at_vo_offsets=eta(K4, offs), source_at_onsets=eta(K4raw, ons), source_at_offsets=eta(K4raw, offs),
          env_mod_1_4Hz_rms_db=dict(postlim=round(modband(K4), 3), source=round(modband(K4raw), 3)), rider_corr_with_vo_gate=round(corr, 3))
pump = (PM["bed_change_at_vo_onsets"]["mean_db"] < -1 and PM["bed_change_at_vo_offsets"]["mean_db"] > 1) or abs(corr) > 0.3 or PM["env_mod_1_4Hz_rms_db"]["postlim"] > 1.5 * PM["env_mod_1_4Hz_rms_db"]["source"]
PM["verdict"] = ("suspect (VO-keyed)" if pump else "likely clean") + (f"; processing adds >2 dB 1 s swing at {R['st400_1s_swing']['added_at_s']} s" if R["st400_1s_swing"]["max_added_over_source_db"] > 2 else "")
R["pumping"] = PM
# ---- last two lines vs the rest
L22 = [w for w in W if w["line"] == 22]; L21 = [w for w in W if w["line"] == 21]; se = W[-1]["end"]
body = (0, L21[-1]["end"] + 0.05); end = (L22[0]["start"] - 0.05, se + 0.05); cut = lambda x, r: x[int(r[0] * SR):int(r[1] * SR)]
LL = {}
for nm, x in (("master", mx), ("vo_stem", vo), ("bed_stem", b)):
    bI, _ = ebur(cut(x, body)); eI, _ = ebur(cut(x, end)); LL[nm] = dict(body_I=round(bI, 2), last2_I=round(eI, 2), delta_db=round(eI - bI, 2))
LL["vo_source_and_staged"] = AM["vo_ending_delta"]; LL["ranges_s"] = dict(body=body, last2=end)
LL["verdict"] = "drop survives" if LL["master"]["delta_db"] <= -2.0 else "drop weakened"
R["last_two_lines"] = LL
mI, mTP = ebur(mx); R["master"] = dict(I=round(mI, 2), TP=round(mTP, 2))
sx, _ = sf.read(A / "stem_sfx_postlim.wav"); segC = [x for x in TL["segments"] if x["id"] == "C"][0]; c0, c1 = segC["start"], segC["end"]
nz = np.where(np.abs(sx).max(1) > 1e-6)[0]; rr = lambda x, a_, z_: 10 * np.log10((np.asarray(x)[int(a_ * SR):int(z_ * SR)] ** 2).mean() + 1e-20)
R["sfx_seqC"] = dict(segC_s=[c0, c1], nonzero_span_s=[round(nz[0] / SR, 3), round(nz[-1] / SR, 3)] if len(nz) else None, inside_segC=bool(len(nz) == 0 or (nz[0] / SR >= c0 - 0.001 and nz[-1] / SR <= c1 + 0.001)),
                     sfx_rms_db=round(rr(sx, c0 + 0.3, c1 - 0.3), 2), bed_rms_db=round(rr(b, c0 + 0.3, c1 - 0.3), 2), vo_rms_db=round(rr(vo, c0 + 0.3, c1 - 0.3), 2),
                     master_I_segC=round(ebur(cut(mx, (c0, c1)))[0], 2), master_I_prev_5s=round(ebur(cut(mx, (c0 - 5, c0)))[0], 2), master_I_next_5s=round(ebur(cut(mx, (c1, c1 + 5)))[0], 2), sources=AM.get("sfx_seqC", {}).get("sources"))
OUT.update(R)
ax[0].axvspan(TD0, TD1, color="#e67e22", alpha=.15); ax[0].set_ylabel("dBFS"); ax[0].set_title("v5 final bed (post-limiter) 1 s RMS; orange = tail dip")
ax[1].plot(T4, K4, color="#c0392b", lw=.8, label="bed 400 ms ST"); ax[1].plot(T4, K4raw - np.median(K4raw) + np.median(K4), color="#999", lw=.6, label="source (offset)")
for s in vs: ax[1].axvspan(s[0], s[1], color="#3498db", alpha=.06)
ax[2].plot(tk, rid, color="#27ae60", label="rider dB"); ax[2].plot(tk, gc, color="#8e44ad", lw=.8, label="duck/tail-dip/fade dB"); ax[2].set_ylim(-40, 8)
tm, km = kst(mx, 3.0); ax[3].plot(tm, km, color="k", lw=.8, label="master 3 s ST"); tv, kv = kst(vo, 3.0); ax[3].plot(tv, kv, color="#3498db", lw=.8, label="VO stem 3 s ST"); ax[3].axvline(end[0], color="r", ls=":")
for a in ax: a.grid(alpha=.25); a.legend(fontsize=8, loc="lower left")
ax[3].set_xlabel("s"); fig.tight_layout(); fig.savefig(PNG); json.dump(OUT, open(JS, "x"), indent=1, default=float)
print(json.dumps({k: v_ for k, v_ in OUT.items() if k != "word_margin"}, indent=1, default=float)); print(json.dumps(R["word_margin"]["lowest5"]), R["word_margin"]["n_under_12"])
