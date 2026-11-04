#!/workspace/mpvenv/bin/python
"""Bjorn ROUGH v2b mix (AUDIO-ONLY pass) = v2 mix with the un-ducked hit hold shortened 0.5 -> HOLD s and the full duck back before "the coffin";
optional FREE_EQ_DB (option b) = 1-4 kHz cut on the un-ducked share only. Env: TAG (output name), HOLD, DOWN_TO (abs s), FREE_EQ_DB, SCR (scratch audio dir).
Keeps VO-only / bed-only stems in SCR for per-word margins (measure_margins.py).
v2 notes: Bjorn ROUGH v2 mix = v1 mix chain unchanged + v2: segments re-slid to the v2 cuts (seg 3 keeps track 127.0 on the P14 cut / 'leapt'),
duck eased through 'leapt ... struck' (un-ducked bed copy crossfaded in), bed dip under 'the victors.'. Measures hit-vs-VO and the dip on bed-only renders.
v1 notes: Bjorn ROUGH v1 mix. Score = 'Uprising' by Scott Buckley (CC BY 4.0), LOCKED five-section edit of bjorn_score_preview.mp3 (md5 62438a4e),
segment 3 slid so track 127.0 (the 2:07 hit) sits exactly on the P14 hard cut ('leapt'). VO = Oliver, retimed (retime_vo.py).
Chain = Bathory v3c mix_v3c.py (VO chain, bed calibrated VO-12 LU, sidechain duck, bus comp, 4x-oversampled limiter, -14 LUFS / <= -1 dBTP).
Writes only scratch/audio/* and logs/mix_log.json (ffmpeg -n). No mp3 / interim deliverables."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess, hashlib
from pathlib import Path
import numpy as np
BR = Path('/workspace/posterity/standalones/bjorn/rough_v2'); V1 = BR.parent / 'rough_v1'; import os; A = Path(os.environ.get('SCR', str(BR / 'scratch/audio'))); LOGS = BR / 'logs'; TAG = os.environ.get('TAG', 'v2b')
VO = A / 'vo_bjorn_v2.wav'; SRC = V1 / 'score_preview/source/Uprising.mp3'; SR = 48000
assert hashlib.md5(SRC.read_bytes()).hexdigest().startswith('3218446a'), 'score source md5'
CUTS = json.load(open(LOGS / 'cuts_v2.json')); DUR = CUTS[-1]['f1'] / 30
W = json.load(open(LOGS / 'vo_bjorn_v2_words.json'))['words']
P14 = [c for c in CUTS if c['shot'] == 'P14'][0]; HIT_T = P14['start']; LEAPT = [w for w in W if w['word'].lower().startswith('leapt')][0]['start']
HIT_TRACK = 127.0
# preview SEG: (cut_start, track_start, cut_end, fade_in, fade_out, dB)
SEG = [(0.0, 60.0, 45.0, 1.5, 1.2, 0), (43.8, 5.0, 53.8, 1.2, 1.0, -5), (52.8, 121.5, 69.5, 1.0, 1.5, 0), (68.0, 20.0, 89.0, 1.5, 1.2, -3), (87.8, 188.3, 101.5, 1.2, 2.0, 0)]
CS = {c['shot']: c['start'] for c in CUTS}
c3 = HIT_T - (HIT_TRACK - SEG[2][1])               # slide segment 3 (same track window start) so track 127.0 lands on the P14 cut
# v2: every boundary keeps its v1 offset from the cut it was placed against (v1: seg2 end = seg3 start + 0.967; seg3 end = P16 + 1.0;
#     seg4 = P16 - 0.5 .. P20 + 0.8; seg5 = P20 - 0.4 .. end). Section lengths/levels/fades/track windows unchanged except seg 3 ends 1.9 s sooner
#     (the "Only" pause is 1.9 s shorter) and seg 2's tail follows seg 3's new start.
SEG = [SEG[0], (43.8, 5.0, c3 + 0.967, 1.2, 1.0, -5), (c3, 121.5, CS['P16'] + 1.0, 1.0, 1.5, 0), (CS['P16'] - 0.5, 20.0, CS['P20'] + 0.8, 1.5, 1.2, -3),
       (CS['P20'] - 0.4, 188.3, 101.5, 1.2, 2.0, 0)]
def wd(word, after=0.0): return next(w for w in W if w['word'] == word and w['start'] >= after)
STRUCK = wd('struck', HIT_T); VICT = wd('victors.', CS['OUTRO']); THE_V = W[W.index(VICT) - 1]
# hit (Vellum item 2): un-ducked bed share w(t): 0->1 over the 60 ms before the cut, 1 through 'leapt' (+0.5 s), cosine back to 0 by the end of 'struck'
HOLD = float(os.environ.get('HOLD', '0.2')); THE_C = wd('the', HIT_T); DOWN_TO = float(os.environ.get('DOWN_TO', str(THE_C['start'] - 0.025)))
FREE_EQ_DB = float(os.environ.get('FREE_EQ_DB', '0'))
HIT_EASE = dict(up=(HIT_T - 0.06, HIT_T), hold_to=HIT_T + HOLD, down_to=DOWN_TO, free_eq_db_1_4k=FREE_EQ_DB, lift_db=float(__import__('os').environ.get('HIT_LIFT', '0')), lift=(HIT_T, HIT_T + 0.5))
# 'victors.' (item 5): bed dip under 'the victors.', 120 ms raised-cosine ramps
VDIP = dict(db=-2.0, span=(THE_V['start'] - 0.10, VICT['end'] + 0.15), ramp=0.12)
def ramp(t, a, b): u = np.clip((t - a) / (b - a), 0, 1); return 0.5 - 0.5 * np.cos(np.pi * u)
def envelopes(n):
    t = np.arange(n) / SR; h = HIT_EASE
    w = ramp(t, *h['up']) * (1 - ramp(t, h['hold_to'], h['down_to']))
    lift = 1 + (10 ** (h['lift_db'] / 20) - 1) * ramp(t, h['lift'][0] - 0.05, h['lift'][0]) * (1 - ramp(t, h['lift'][1], h['lift'][1] + 0.15))
    a, b = VDIP['span']; r = VDIP['ramp']; dip = 1 + (10 ** (VDIP['db'] / 20) - 1) * ramp(t, a - r, a) * (1 - ramp(t, b, b + r))
    return w.astype(np.float32), (lift * dip).astype(np.float32)
END_FADE = (DUR - 1.0, DUR)
TARGET_I = -13.9     # wav target; the AAC-256k encode of run 1 measured 0.1 LU below the wav (wav -14.1 -> mp4 -14.2), so final mp4 lands at -14.0
def ebur(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r); return I, float(tp[-1])
def build_bed(out):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(SRC), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2); n = int(round(DUR * SR)); bed = np.zeros((n, 2), np.float32)
    for cs, ts, ce, fi, fo, db in SEG:
        ce = min(ce, DUR); a = int(round(cs * SR)); L = int(round((ce - cs) * SR)); t0 = int(round(ts * SR)); seg = x[t0:t0 + L].copy(); L = len(seg)
        g = np.ones(L, np.float32); ni = int(fi * SR); no = int(fo * SR)
        if ni: g[:ni] = np.sin(np.linspace(0, np.pi / 2, ni))
        if no and ce < SEG[-1][2] - 1e-6 or ce >= DUR - 1e-6 and no and SEG[-1][2] <= DUR: g[-no:] *= np.cos(np.linspace(0, np.pi / 2, no))
        bed[a:a + L] += seg * g[:, None] * 10 ** (db / 20)
    f0 = int(END_FADE[0] * SR); bed[f0:] *= np.cos(np.linspace(0, np.pi / 2, n - f0))[:, None]   # bed out by the last frame
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-n', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(out)], input=bed.tobytes(), check=True)
    return bed
def split_bed(bed, duck_p, free_p, use_env=True):
    w, g = envelopes(len(bed)) if use_env else (np.zeros(len(bed), np.float32), np.ones(len(bed), np.float32))
    for arr, p in ((bed * (g * (1 - w))[:, None], duck_p), (bed * (g * w)[:, None], free_p)):
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-n', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(p)], input=np.ascontiguousarray(arr, np.float32).tobytes(), check=True)
VOCH = f"aresample={SR},highpass=f=70,volume=10dB,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3,apad,atrim=0:{DUR}"
def run(fc, out, beds): subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-i', str(beds[0]), '-i', str(beds[1]), '-filter_complex', fc, '-ar', str(SR), str(out)], check=True)
def mix(out, beds, bed_db, master_db, vo_gain=1.0):   # beds = (duckable, un-ducked share); vo_gain=0 -> bed-only render (sidechain still keyed by the VO)
    fc = (f"[0:a]{VOCH},asplit=2[vo0][sc];[vo0]volume={vo_gain}[vo];[1:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB[bed0];"
          f"[2:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB" + (f",equalizer=f=2000:t=o:w=2:g={FREE_EQ_DB}" if FREE_EQ_DB else "") + "[free];"
          "[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bedd];[bedd][free]amix=inputs=2:normalize=0:duration=first[bed];"
          f"[vo][bed]amix=inputs=2:normalize=0:duration=first,acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,volume={master_db}dB,"
          f"aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=0,aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo")
    run(fc, out, beds)
def rms_db(p, a, b, ch_mean=True):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)[int(a * SR):int(b * SR)]; return float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9))
def peak_db(p, a, b):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(p), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)[int(a * SR):int(b * SR)]; return float(20 * np.log10(np.abs(x).max() + 1e-9))
if __name__ == '__main__':
    final = A / f'mix_bjorn_{TAG}.wav'; assert not final.exists()
    log = dict(score="'Uprising' by Scott Buckley (CC BY 4.0)", source_md5=hashlib.md5(SRC.read_bytes()).hexdigest(), segments=[dict(cut=[round(s[0], 3), round(min(s[2], DUR), 3)],
               track=[s[1], round(s[1] + min(s[2], DUR) - s[0], 3)], fade_in=s[3], fade_out=s[4], db=s[5]) for s in SEG], hit_track=HIT_TRACK, target_I_wav=TARGET_I, hit_cut_s=round(HIT_T, 4),
               leapt_onset_s=LEAPT, hit_track_at_cut=round(SEG[2][1] + HIT_T - SEG[2][0], 4), seg3_start=round(c3, 4), hit_ease=HIT_EASE, victors_dip=VDIP, end_fade=END_FADE, dur=DUR, iters=[], master=[])
    bed = A / 'bed_uprising.wav'; bd, bf = A / 'bed_duck.wav', A / 'bed_free.wav'; b0d, b0f = A / 'bed0_duck.wav', A / 'bed0_free.wav'
    arr = build_bed(bed); split_bed(arr, bd, bf, True); split_bed(arr, b0d, b0f, False); del arr
    vo = A / 'vo_stem.wav'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-af', VOCH, '-ar', str(SR), str(vo)], check=True)
    Lvo, _ = ebur(vo); log['vo_I'] = Lvo; bed_db = -2.0
    for it in range(6):                                  # calibrate on the plain bed (no v2 envelopes), as v1
        p = A / f'bedcal_{it}.wav'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(bed), '-af', f'volume={bed_db}dB', str(p)], check=True)
        Lb, _ = ebur(p); d = Lvo - Lb; log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(d, 2)))
        if abs(d - 12.0) <= 0.3: break
        bed_db += d - 12.0
    master = 0.0
    for it in range(8):
        p = A / f'mix_{it}.wav'; mix(p, (bd, bf), bed_db, master); I, tp = ebur(p); log['master'].append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I - TARGET_I) <= 0.05 and tp <= -1.1: break
        master += TARGET_I - I
    log.update(bed_db=round(bed_db, 2), master_db=round(master, 2), I=I, TP=tp); p.rename(final); log['final_wav'] = str(final)
    # measurements: bed-only renders (same chain, VO muted but still keying the duck), with and without the v2 envelopes
    bo, bo0, vs = A / 'm_bedonly.wav', A / 'm_bedonly_noenv.wav', A / 'm_voonly.wav'
    mix(bo, (bd, bf), bed_db, master, 0.0); mix(bo0, (b0d, b0f), bed_db, master, 0.0)
    mix(vs, (bd, bf), -200.0, master)                    # VO-only through the same chain
    H0, H1 = HIT_T, HIT_T + 0.30; L0, L1 = LEAPT, wd('leapt', HIT_T)['end']
    m = dict(hit_window=[round(H0, 3), round(H1, 3)],
             bed_rms_hit_db=round(rms_db(bo, H0, H1), 2), bed_rms_hit_db_no_ease=round(rms_db(bo0, H0, H1), 2),
             bed_peak_hit_db=round(peak_db(bo, H0, H1), 2), bed_peak_hit_db_no_ease=round(peak_db(bo0, H0, H1), 2),
             vo_rms_leapt_db=round(rms_db(vs, L0, L1), 2), vo_rms_leapt_to_struck_db=round(rms_db(vs, L0, STRUCK['end']), 2),
             bed_rms_leapt_to_struck_db=round(rms_db(bo, L0, STRUCK['end']), 2))
    m['hit_under_vo_db'] = round(m['vo_rms_leapt_db'] - m['bed_rms_hit_db'], 2); m['hit_under_vo_db_no_ease'] = round(m['vo_rms_leapt_db'] - m['bed_rms_hit_db_no_ease'], 2)
    m['vo_over_bed_leapt_struck_db'] = round(m['vo_rms_leapt_to_struck_db'] - m['bed_rms_leapt_to_struck_db'], 2)
    a, b = VDIP['span']; m['victors_span'] = [round(a, 3), round(b, 3)]
    m['victors_bed_rms_db'] = round(rms_db(bo, a, b), 2); m['victors_bed_rms_db_no_dip'] = round(rms_db(bo0, a, b), 2); m['victors_dip_measured_db'] = round(m['victors_bed_rms_db'] - m['victors_bed_rms_db_no_dip'], 2)
    log['measure'] = m
    for q in [bo, vs]: q.rename(A / f'stem_{TAG}_{q.stem[2:]}.wav')
    for q in list(A.glob('bedcal_*.wav')) + list(A.glob('mix_[0-9]*.wav')) + [vo, bed, bd, bf, b0d, b0f, bo0]: q.unlink()
    json.dump(log, open((LOGS if TAG.startswith('v2b') else A) / f'mix_{TAG}_log.json', 'x'), indent=1, default=float); print(json.dumps({k: log[k] for k in ('segments', 'hit_cut_s', 'leapt_onset_s', 'hit_track_at_cut', 'bed_db', 'master_db', 'I', 'TP', 'measure')}, indent=1))
