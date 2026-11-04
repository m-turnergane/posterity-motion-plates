#!/workspace/mpvenv/bin/python
"""Bjorn ROUGH v4 mix. Chain = rough_v2b mix chain unchanged (VO chain, bed VO-12 LU, sidechain duck, bus comp, 4x-oversampled limiter, -14 LUFS / <= -1 dBTP).
Score = 'Uprising' by Scott Buckley (CC BY 4.0), source md5 3218446a...  Owner directive (SCORE-PLAN-v4.md):
  * keep the v2b build-up (seg1 track 60.0 from 0 s; seg2 track 5.0 at -5 dB from P11-0.1 s) and the 'leapt' hit: track 127.0 exactly on the P14 hard cut,
    un-ducked share held 0.2 s then fully ducked again before 'the coffin' (v2b HOLD 0.2);
  * then ONE continuous Uprising run (track 121.5 -> ~168.7) to the end, no further edits/restarts: volume automation + ducking only
    (-6 dB plateau P16-0.5 .. P20-0.4 with 1.5 s / 1.2 s raised-cosine ramps = the level of the old v2 seg4; -3 dB for P20 + outro);
  * duck pick xd6: bed dip under 'the victors.' = -2 dB (v2b) - 6 dB = -8 dB nominal, held through 'We remember the rest.'
Writes rough_v4/scratch/audio/* and rough_v4/logs/mix_v4_log.json + margins_v4.json (refuses overwrite)."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess, hashlib, os
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
BR = Path('/workspace/posterity/standalones/bjorn/rough_v4'); A = BR / 'scratch/audio'; A.mkdir(parents=True, exist_ok=True); LOGS = BR / 'logs'
VO = BR / 'scratch/vo_bjorn_v4.wav'; SRC = BR.parent / 'rough_v1/score_preview/source/Uprising.mp3'; SR = 48000
assert hashlib.md5(SRC.read_bytes()).hexdigest().startswith('3218446a'), 'score source md5'
CUTS = json.load(open(LOGS / 'cuts_v4.json')); DUR = CUTS[-1]['f1'] / 30; CS = {c['shot']: c['start'] for c in CUTS}
W = json.load(open(LOGS / 'vo_bjorn_v4_words.json'))['words']
HIT_T = CS['P14']; HIT_TRACK = 127.0; LEAPT = next(w for w in W if w['word'].lower().startswith('leapt'))['start']
c3 = HIT_T - (HIT_TRACK - 121.5)
# (cut_start, track_start, cut_end, fade_in, fade_out, dB)   v2b offsets kept: seg2 start = P11 - 0.1 (v2: 43.8 vs P11 43.9), seg1 end = P11 + 1.1, seg2 end = seg3 start + 0.967
SEG = [(0.0, 60.0, CS['P11'] + 1.1, 1.5, 1.2, 0), (CS['P11'] - 0.1, 5.0, c3 + 0.967, 1.2, 1.0, -5), (c3, 121.5, DUR, 1.0, 0.0, 0)]
def wd(word, after=0.0): return next(w for w in W if w['word'] == word and w['start'] >= after)
STRUCK = wd('struck', HIT_T); VICT = wd('victors.', CS['OUTRO']); THE_V = W[W.index(VICT) - 1]; THE_C = wd('the', HIT_T)
HOLD = 0.2; HIT_EASE = dict(up=(HIT_T - 0.06, HIT_T), hold_to=HIT_T + HOLD, down_to=THE_C['start'] - 0.025)
XD = 6.0; VDIP = dict(db=-2.0 - XD, span=(THE_V['start'] - 0.10, W[-1]['end'] + 0.15), ramp=0.12)   # xd6 dip held through 'We remember the rest.' (run-1 'We' margin 1.4 dB)
AUTO = dict(db=-6.0, down=(CS['P16'] - 0.5, CS['P16'] + 1.0), up=(CS['P20'] - 0.4, CS['P20'] + 0.8), tail_db=-3.0)   # run-1 QA: P20/outro at 0 dB left 'Rome.' 4.6 / 'We' 1.4 dB (1-4 kHz) -> tail -3 dB
END_FADE = (DUR - 1.0, DUR); TARGET_I = -13.9
def ramp(t, a, b): u = np.clip((t - a) / (b - a), 0, 1); return 0.5 - 0.5 * np.cos(np.pi * u)
def envelopes(n, use_env=True):
    t = np.arange(n) / SR; h = HIT_EASE
    lo, tl = 10 ** (AUTO['db'] / 20), 10 ** (AUTO['tail_db'] / 20); r1, r2 = ramp(t, *AUTO['down']), ramp(t, *AUTO['up'])
    auto = 1 + (lo - 1) * r1 * (1 - r2) + (tl - 1) * r1 * r2
    if not use_env: return np.zeros(n, np.float32), auto.astype(np.float32)
    w = ramp(t, *h['up']) * (1 - ramp(t, h['hold_to'], h['down_to']))
    a, b = VDIP['span']; r = VDIP['ramp']; dip = 1 + (10 ** (VDIP['db'] / 20) - 1) * ramp(t, a - r, a) * (1 - ramp(t, b, b + r))
    return w.astype(np.float32), (auto * dip).astype(np.float32)
def ebur(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r); return I, float(tp[-1])
def wr(arr, p): subprocess.run(['ffmpeg', '-loglevel', 'error', '-n', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(p)], input=np.ascontiguousarray(arr, np.float32).tobytes(), check=True)
def build_bed():
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(SRC), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2); n = int(round(DUR * SR)); bed = np.zeros((n, 2), np.float32)
    for k, (cs, ts, ce, fi, fo, db) in enumerate(SEG):
        a = int(round(cs * SR)); L = int(round((ce - cs) * SR)); t0 = int(round(ts * SR)); seg = x[t0:t0 + L].copy(); L = len(seg); assert L == int(round((ce - cs) * SR)), 'track too short'
        g = np.ones(L, np.float32); ni = int(fi * SR); no = int(fo * SR)
        if ni: g[:ni] = np.sin(np.linspace(0, np.pi / 2, ni))
        if no: g[-no:] *= np.cos(np.linspace(0, np.pi / 2, no))
        bed[a:a + L] += seg * g[:, None] * 10 ** (db / 20)
    f0 = int(END_FADE[0] * SR); bed[f0:] *= np.cos(np.linspace(0, np.pi / 2, n - f0))[:, None]
    return bed
VOCH = f"aresample={SR},highpass=f=70,volume=10dB,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3,apad,atrim=0:{DUR}"
def mix(out, beds, bed_db, master_db, vo_gain=1.0):
    fc = (f"[0:a]{VOCH},asplit=2[vo0][sc];[vo0]volume={vo_gain}[vo];[1:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB[bed0];"
          f"[2:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB[free];"
          "[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bedd];[bedd][free]amix=inputs=2:normalize=0:duration=first[bed];"
          f"[vo][bed]amix=inputs=2:normalize=0:duration=first,acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,volume={master_db}dB,"
          f"aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=0,aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo")
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-i', str(beds[0]), '-i', str(beds[1]), '-filter_complex', fc, '-ar', str(SR), str(out)], check=True)
def load(p, ch=2):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(p), '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, ch).astype(np.float64)
def rms(x, a, b): s = x[int(a * SR):int(b * SR)]; return float(20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-12))
def pk(x, a, b): return float(20 * np.log10(np.abs(x[int(a * SR):int(b * SR)]).max() + 1e-12))
def kweight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    return lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], lfilter(b1, a1, x, axis=0), axis=0)
BANDS = dict(house=kweight, k1_4=lambda x: sosfilt(butter(4, [1000, 4000], 'bandpass', fs=SR, output='sos'), x, axis=0),
             phone=lambda x: sosfilt(butter(4, [300, 8000], 'bandpass', fs=SR, output='sos'), x, axis=0))
if __name__ == '__main__':
    final = A / 'mix_bjorn_v4.wav'; assert not final.exists()
    log = dict(score="'Uprising' by Scott Buckley (CC BY 4.0)", source_md5=hashlib.md5(SRC.read_bytes()).hexdigest(),
               segments=[dict(cut=[round(s[0], 3), round(s[2], 3)], track=[s[1], round(s[1] + s[2] - s[0], 3)], fade_in=s[3], fade_out=s[4], db=s[5]) for s in SEG],
               hit_track=HIT_TRACK, hit_cut_s=round(HIT_T, 4), leapt_onset_s=LEAPT, hit_track_at_cut=round(SEG[2][1] + HIT_T - SEG[2][0], 4), hit_ease=HIT_EASE,
               duck_pick='xd6', victors_dip=VDIP, automation=AUTO, end_fade=END_FADE, dur=DUR, target_I_wav=TARGET_I, iters=[], master=[])
    arr = build_bed(); n = len(arr); bd, bf, b0d, b0f, bed = A / 'bed_duck.wav', A / 'bed_free.wav', A / 'bed0_duck.wav', A / 'bed0_free.wav', A / 'bed_uprising.wav'
    w, g = envelopes(n, True); wr(arr * (g * (1 - w))[:, None], bd); wr(arr * (g * w)[:, None], bf)
    w0, g0 = envelopes(n, False); wr(arr * g0[:, None], b0d); wr(arr * 0, b0f); wr(arr * g0[:, None], bed)   # bed0 = automation only (no hit ease, no dip)
    raw_bed = arr.astype(np.float64); del arr
    vo = A / 'vo_stem.wav'; subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-af', VOCH, '-ar', str(SR), str(vo)], check=True)
    Lvo, _ = ebur(vo); log['vo_I'] = Lvo; bed_db = -2.0
    for it in range(6):
        p = A / f'bedcal_{it}.wav'; subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(bed), '-af', f'volume={bed_db}dB', str(p)], check=True)
        Lb, _ = ebur(p); d = Lvo - Lb; log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(d, 2)))
        if abs(d - 12.0) <= 0.3: break
        bed_db += d - 12.0
    master = 0.0
    for it in range(8):
        p = A / f'mix_{it}.wav'; mix(p, (bd, bf), bed_db, master); I, tp = ebur(p); log['master'].append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I - TARGET_I) <= 0.05 and tp <= -1.1: break
        master += TARGET_I - I
    log.update(bed_db=round(bed_db, 2), master_db=round(master, 2), I=I, TP=tp); p.rename(final); log['final_wav'] = str(final)
    bo, bo0, vs = A / 'stem_v4_bedonly.wav', A / 'm_bedonly_noenv.wav', A / 'stem_v4_voonly.wav'
    mix(bo, (bd, bf), bed_db, master, 0.0); mix(bo0, (b0d, b0f), bed_db, master, 0.0); mix(vs, (bd, bf), -200.0, master)
    B, B0, V = load(bo, 1)[:, 0], load(bo0, 1)[:, 0], load(vs, 1)[:, 0]
    H0, H1 = HIT_T, HIT_T + 0.30; L1 = wd('leapt', HIT_T)['end']
    m = dict(hit_window=[round(H0, 3), round(H1, 3)], bed_rms_hit_db=round(rms(B, H0, H1), 2), bed_rms_hit_db_no_ease=round(rms(B0, H0, H1), 2),
             bed_peak_hit_db=round(pk(B, H0, H1), 2), vo_rms_leapt_db=round(rms(V, LEAPT, L1), 2), vo_rms_leapt_to_struck_db=round(rms(V, LEAPT, STRUCK['end']), 2),
             bed_rms_leapt_to_struck_db=round(rms(B, LEAPT, STRUCK['end']), 2))
    m['hit_under_vo_db'] = round(m['vo_rms_leapt_db'] - m['bed_rms_hit_db'], 2); m['vo_over_bed_leapt_struck_db'] = round(m['vo_rms_leapt_to_struck_db'] - m['bed_rms_leapt_to_struck_db'], 2)
    a, b = VDIP['span'][0], VICT['end'] + 0.15; m.update(victors_span=[round(a, 3), round(b, 3)], victors_bed_rms_db=round(rms(B, a, b), 2), victors_bed_rms_db_no_dip=round(rms(B0, a, b), 2))
    m['victors_dip_measured_db'] = round(m['victors_bed_rms_db'] - m['victors_bed_rms_db_no_dip'], 2)
    # restart audit: raw bed (pre-duck, pre-automation) RMS in 0.5 s windows either side of every segment join; joins after the hit must be none
    joins = [(SEG[k + 1][0], SEG[k][2]) for k in range(len(SEG) - 1)]
    m['restart_audit'] = dict(joins=[dict(xfade=[round(s, 3), round(e, 3)], rms_pre_db=round(rms(raw_bed.mean(1), s - 0.5, s), 2), rms_mid_db=round(rms(raw_bed.mean(1), s, e), 2),
                                          rms_post_db=round(rms(raw_bed.mean(1), e, e + 0.5), 2)) for s, e in joins],
                              joins_after_hit=[j for j in joins if j[0] > HIT_T], continuous_run_track=[121.5, round(121.5 + DUR - c3, 3)],
                              raw_bed_rms_per_shot_db={k: round(rms(raw_bed.mean(1), CS[k], ([c['end'] for c in CUTS if c['shot'] == k][0])), 2) for k in CS},
                              mixed_bed_rms_per_shot_db={k: round(rms(B, CS[k], ([c['end'] for c in CUTS if c['shot'] == k][0])), 2) for k in CS})
    log['measure'] = m
    # per-word margins (examiner method) on all 244 words; flag weakest
    vs2, bo2 = load(vs), load(bo); mg = {}
    for name, f in BANDS.items():
        fv, fb = f(vs2), f(bo2)
        for w in W:
            i, j = int(w['start'] * SR), int(w['end'] * SR); mg.setdefault(f"{w['word']}@{w['start']:.3f}", {})[name] = round(float(10 * np.log10(np.mean(fv[i:j] ** 2) / (np.mean(fb[i:j] ** 2) + 1e-20))), 1)
    json.dump(mg, open(LOGS / 'margins_v4.json', 'x'), indent=1)
    worst = sorted(mg.items(), key=lambda kv: kv[1]['k1_4'])[:10]; log['margins_worst_k1_4'] = worst
    for q in list(A.glob('bedcal_*.wav')) + list(A.glob('mix_[0-9]*.wav')) + [vo, bed, bd, bf, b0d, b0f, bo0]: q.unlink()
    json.dump(log, open(LOGS / 'mix_v4_log.json', 'x'), indent=1, default=float)
    print(json.dumps({k: log[k] for k in ('segments', 'hit_cut_s', 'leapt_onset_s', 'hit_track_at_cut', 'bed_db', 'master_db', 'I', 'TP', 'measure', 'margins_worst_k1_4')}, indent=1))
