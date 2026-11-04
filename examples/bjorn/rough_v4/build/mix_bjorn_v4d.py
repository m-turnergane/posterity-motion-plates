#!/workspace/mpvenv/bin/python
"""Bjorn ROUGH v4d mix.  OWNER OVERRIDE 2026-11-03 ("just let the score play, forget timing"):
  * 'Uprising' (Scott Buckley, CC BY 4.0, source md5 3218446a...) plays as ONE continuous run from a single track offset (OFFSET) from timeline 0 to the end
    of the outro: no segment edits / splices / crossfades, no seg1/seg2/seg3, no seg2 dip, no hit retime/preserve.
  * NO level automation (no -6 dB plateau, no hit ease, no victors dip, no tail lift). Shaping = the v4c sidechain duck under the VO + a 1.0 s end fade,
    plus the v4c score start (timeline 0, 1.5 s sine fade-in, as v4c seg1).
  * Chain = v4b/v4c chain unchanged (VO chain, bed calibrated VO-12 LU, sidechaincompress threshold 0.035 ratio 2.5 attack 15 release 700 knee 4,
    bus comp, 4x-oversampled limiter), WAV target -13.9 LUFS (final -14 +/-0.5, <= -1 dBTP).
  * OFFSET = 60.0 s = the v4c seg1 offset: score identical in content to v4c up to P11-0.1 s; track 104.4 -> 120.8 (the track's rising build) lies under P11-P13.
Writes rough_v4/scratch/audio/{mix_bjorn_v4d.wav, stem_v4d_bedonly.wav, stem_v4d_voonly.wav, stem_v4d_bednoduck.wav} and logs/{mix_v4d_log.json, margins_v4d.json} (refuses overwrite)."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess, hashlib, os
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
BR = Path('/workspace/posterity/standalones/bjorn/rough_v4'); A = BR / 'scratch/audio'; LOGS = BR / 'logs'
VO = BR / 'scratch/vo_bjorn_v4b.wav'; SRC = BR.parent / 'rough_v1/score_preview/source/Uprising.mp3'; SR = 48000
assert hashlib.md5(SRC.read_bytes()).hexdigest().startswith('3218446a'), 'score source md5'
CUTS = json.load(open(LOGS / 'cuts_v4b.json')); DUR = CUTS[-1]['f1'] / 30; CS = {c['shot']: c['start'] for c in CUTS}; CE = {c['shot']: c['end'] for c in CUTS}
W = json.load(open(LOGS / 'vo_bjorn_v4b_words.json'))['words']
OFFSET = float(os.environ.get('V4D_OFFSET', '60.0')); FADE_IN = 1.5; END_FADE = (DUR - 1.0, DUR); TARGET_I = -13.9
def ebur(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r); return I, float(tp[-1])
def wr(arr, p): subprocess.run(['ffmpeg', '-loglevel', 'error', '-n', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(p)], input=np.ascontiguousarray(arr, np.float32).tobytes(), check=True)
def build_bed():
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(SRC), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2); n = int(round(DUR * SR)); t0 = int(round(OFFSET * SR))
    bed = x[t0:t0 + n].copy(); assert len(bed) == n, 'track too short for this offset'
    ni = int(FADE_IN * SR); bed[:ni] *= np.sin(np.linspace(0, np.pi / 2, ni))[:, None]          # = v4c seg1 fade-in
    f0 = int(END_FADE[0] * SR); bed[f0:] *= np.cos(np.linspace(0, np.pi / 2, n - f0))[:, None]   # = v4c end fade
    return bed
VOCH = f"aresample={SR},highpass=f=70,volume=10dB,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3,apad,atrim=0:{DUR}"
def mix(out, bedp, bed_db, master_db, vo_gain=1.0, vo=VO):
    # identical to the v4b/v4c chain with the bed_free branch removed (it carried only the hit ease, which the override drops)
    fc = (f"[0:a]{VOCH},asplit=2[vo0][sc];[vo0]volume={vo_gain}[vo];[1:a]aresample={SR},atrim=0:{DUR},volume={bed_db}dB[bed0];"
          "[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bed];"
          f"[vo][bed]amix=inputs=2:normalize=0:duration=first,acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,volume={master_db}dB,"
          f"aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=0,aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo")
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(vo), '-i', str(bedp), '-filter_complex', fc, '-ar', str(SR), str(out)], check=True)
def load(p, ch=2):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(p), '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, ch).astype(np.float64)
def rms(x, a, b): s = x[int(a * SR):int(b * SR)]; return float(20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-12))
def kweight(x):
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    return lfilter([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621], lfilter(b1, a1, x, axis=0), axis=0)
BANDS = dict(house=kweight, k1_4=lambda x: sosfilt(butter(4, [1000, 4000], 'bandpass', fs=SR, output='sos'), x, axis=0),
             phone=lambda x: sosfilt(butter(4, [300, 8000], 'bandpass', fs=SR, output='sos'), x, axis=0))
if __name__ == '__main__':
    final = A / 'mix_bjorn_v4d.wav'; assert not final.exists()
    log = dict(score="'Uprising' by Scott Buckley (CC BY 4.0)", source_md5=hashlib.md5(SRC.read_bytes()).hexdigest(), offset_s=OFFSET,
               run=dict(timeline=[0.0, round(DUR, 3)], track=[OFFSET, round(OFFSET + DUR, 3)]), fade_in=FADE_IN, end_fade=END_FADE, edits=0, automation=None,
               hit_cut_s=CS['P14'], track_at_P14_cut=round(OFFSET + CS['P14'], 3), dur=DUR, target_I_wav=TARGET_I, iters=[], master=[])
    arr = build_bed(); n = len(arr); bed = A / 'bed_v4d.wav'; wr(arr, bed); raw_bed = arr.astype(np.float64).mean(1); del arr
    vo = A / 'vo_stem_v4d.wav'; subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(VO), '-af', VOCH, '-ar', str(SR), str(vo)], check=True)
    Lvo, _ = ebur(vo); log['vo_I'] = Lvo; bed_db = -2.0
    for it in range(6):
        p = A / f'bedcal_v4d_{it}.wav'; subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(bed), '-af', f'volume={bed_db}dB', str(p)], check=True)
        Lb, _ = ebur(p); d = Lvo - Lb; log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(d, 2)))
        if abs(d - 12.0) <= 0.3: break
        bed_db += d - 12.0
    master = 0.0
    for it in range(8):
        p = A / f'mix_v4d_{it}.wav'; mix(p, bed, bed_db, master); I, tp = ebur(p); log['master'].append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I - TARGET_I) <= 0.05 and tp <= -1.1: break
        master += TARGET_I - I
    log.update(bed_db=round(bed_db, 2), master_db=round(master, 2), I=I, TP=tp); p.rename(final); log['final_wav'] = str(final)
    # stems through the same chain: bed-only (ducked by the VO sidechain), VO-only, and bed-only with a silent VO (= score stem before VO, at mix level)
    sil = A / 'vo_silent_v4d.wav'; subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-f', 'lavfi', '-i', f'anullsrc=r={SR}:cl=mono', '-t', f'{DUR}', str(sil)], check=True)
    bo, vs, bn = A / 'stem_v4d_bedonly.wav', A / 'stem_v4d_voonly.wav', A / 'stem_v4d_bednoduck.wav'
    mix(bo, bed, bed_db, master, 0.0); mix(vs, bed, -200.0, master); mix(bn, bed, bed_db, master, 0.0, vo=sil)
    vs2, bo2 = load(vs), load(bo); mg = {}
    for name, f in BANDS.items():
        fv, fb = f(vs2), f(bo2)
        for w in W:
            i, j = int(w['start'] * SR), int(w['end'] * SR); mg.setdefault(f"{w['word']}@{w['start']:.3f}", {})[name] = round(float(10 * np.log10(np.mean(fv[i:j] ** 2) / (np.mean(fb[i:j] ** 2) + 1e-20))), 1)
    json.dump(mg, open(LOGS / 'margins_v4d.json', 'x'), indent=1)
    log['margins_worst'] = {b: sorted(mg.items(), key=lambda kv: kv[1][b])[:6] for b in BANDS}
    log['raw_bed_rms_per_shot_db'] = {k: round(rms(raw_bed, CS[k], CE[k]), 2) for k in CS}
    for q in list(A.glob('bedcal_v4d_*.wav')) + list(A.glob('mix_v4d_[0-9]*.wav')) + [vo, bed, sil]: q.unlink()
    json.dump(log, open(LOGS / 'mix_v4d_log.json', 'x'), indent=1, default=float)
    print(json.dumps({k: log[k] for k in ('offset_s', 'track_at_P14_cut', 'bed_db', 'master_db', 'I', 'TP', 'margins_worst')}, indent=1))
