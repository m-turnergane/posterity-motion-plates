#!/workspace/mpvenv/bin/python
"""Bjorn ROUGH v1 mix. Score = 'Uprising' by Scott Buckley (CC BY 4.0), LOCKED five-section edit of bjorn_score_preview.mp3 (md5 62438a4e),
segment 3 slid so track 127.0 (the 2:07 hit) sits exactly on the P14 hard cut ('leapt'). VO = Oliver, retimed (retime_vo.py).
Chain = Bathory v3c mix_v3c.py (VO chain, bed calibrated VO-12 LU, sidechain duck, bus comp, 4x-oversampled limiter, -14 LUFS / <= -1 dBTP).
Writes only scratch/audio/* and logs/mix_log.json (ffmpeg -n). No mp3 / interim deliverables."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess, hashlib
from pathlib import Path
import numpy as np
BR = Path('/workspace/posterity/standalones/bjorn/rough_v1'); A = BR / 'scratch/audio'; LOGS = BR / 'logs'
VO = A / 'vo_bjorn_v1.wav'; SRC = BR / 'score_preview/source/Uprising.mp3'; SR = 48000
assert hashlib.md5(SRC.read_bytes()).hexdigest().startswith('3218446a'), 'score source md5'
CUTS = json.load(open(LOGS / 'cuts.json')); DUR = CUTS[-1]['f1'] / 30
W = json.load(open(LOGS / 'vo_bjorn_v1_words.json'))['words']
P14 = [c for c in CUTS if c['shot'] == 'P14'][0]; HIT_T = P14['start']; LEAPT = [w for w in W if w['word'].lower().startswith('leapt')][0]['start']
HIT_TRACK = 127.0
# preview SEG: (cut_start, track_start, cut_end, fade_in, fade_out, dB)
SEG = [(0.0, 60.0, 45.0, 1.5, 1.2, 0), (43.8, 5.0, 53.8, 1.2, 1.0, -5), (52.8, 121.5, 69.5, 1.0, 1.5, 0), (68.0, 20.0, 89.0, 1.5, 1.2, -3), (87.8, 188.3, 101.5, 1.2, 2.0, 0)]
c3 = HIT_T - (HIT_TRACK - SEG[2][1]); SEG[2] = (c3, SEG[2][1], SEG[2][2], SEG[2][3], SEG[2][4], SEG[2][5])   # slide segment 3 (same track window start)
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
VOCH = f"aresample={SR},highpass=f=70,volume=10dB,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3,apad,atrim=0:{DUR}"
def run(fc, out, bed): subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-i', str(bed), '-filter_complex', fc, '-ar', str(SR), str(out)], check=True)
def mix(out, bed, bed_db, master_db):
    fc = (f"[0:a]{VOCH},asplit=2[vo][sc];[1:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB[bed0];"
          "[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bed];"
          f"[vo][bed]amix=inputs=2:normalize=0:duration=first,acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,volume={master_db}dB,"
          f"aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=0,aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo")
    run(fc, out, bed)
if __name__ == '__main__':
    final = A / 'mix_bjorn_v1.wav'; assert not final.exists()
    log = dict(score="'Uprising' by Scott Buckley (CC BY 4.0)", source_md5=hashlib.md5(SRC.read_bytes()).hexdigest(), segments=[dict(cut=[round(s[0], 3), round(min(s[2], DUR), 3)],
               track=[s[1], round(s[1] + min(s[2], DUR) - s[0], 3)], fade_in=s[3], fade_out=s[4], db=s[5]) for s in SEG], hit_track=HIT_TRACK, target_I_wav=TARGET_I, hit_cut_s=round(HIT_T, 4),
               leapt_onset_s=LEAPT, seg3_shift_s=round(c3 - 52.8, 4), end_fade=END_FADE, dur=DUR, iters=[], master=[])
    bed = A / 'bed_uprising.wav'
    if not bed.exists(): build_bed(bed)
    vo = A / 'vo_stem.wav'
    if not vo.exists(): subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-af', VOCH, '-ar', str(SR), str(vo)], check=True)
    Lvo, _ = ebur(vo); log['vo_I'] = Lvo; bed_db = -2.0
    for it in range(6):
        p = A / f'bedcal_{it}.wav'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(bed), '-af', f'volume={bed_db}dB', str(p)], check=True)
        Lb, _ = ebur(p); d = Lvo - Lb; log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(d, 2)))
        if abs(d - 12.0) <= 0.3: break
        bed_db += d - 12.0
    master = 0.0
    for it in range(8):
        p = A / f'mix_{it}.wav'; mix(p, bed, bed_db, master); I, tp = ebur(p); log['master'].append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I - TARGET_I) <= 0.05 and tp <= -1.1: break
        master += TARGET_I - I
    log.update(bed_db=round(bed_db, 2), master_db=round(master, 2), I=I, TP=tp); p.rename(final); log['final_wav'] = str(final)
    for q in list(A.glob('bedcal_*.wav')) + list(A.glob('mix_[0-9]*.wav')) + [vo, bed]: q.unlink()
    json.dump(log, open(LOGS / 'mix_log.json', 'x'), indent=1); print(json.dumps(log, indent=1))
