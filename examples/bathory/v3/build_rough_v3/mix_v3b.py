#!/workspace/mpvenv/bin/python
"""Rough v3b mix: Oliver v3b VO (raw-gap retime) + Anabasis I refit (window from track 256 s; 2.5 s qsin crossfade at cut 38.5 s,
A 293.25-295.75 vs B 279.65-282.15, both inside the flat 275-300 stretch; repeat 13.6 s so the priest line lands at track ~321.2 as in v3).
Writes only scratch_v3b/audio/*, logs_v3b/mix_log.json, v3/vo/mix_v3b_final.mp3 (ffmpeg -n)."""
import sys; sys.dont_write_bytecode = True
import json, re, subprocess
from pathlib import Path
V3 = Path('/workspace/posterity/standalones/bathory/v3'); BR = V3 / 'build_rough_v3'; A = BR / 'scratch_v3b/audio'; A.mkdir(parents=True, exist_ok=True)
VO = V3 / 'vo/vo_oliver_v3b.wav'; BED = V3 / 'score_audition/anabasis_i.mp3'
W = json.load(open(V3 / 'vo/vo_oliver_v3b_words.json'))['words']
def wstart(i): return W[i]['start']
DUR = 101.5; SR = 48000
T0A = 256.0; OFFB = 242.4; TX = 38.5; XF = 2.5                      # cut t -> track t+256 until the crossfade, then t+242.4
A_END = TX + XF / 2; B_START = OFFB + TX - XF / 2
T_L13 = [w for w in W if w['line'] == 13][0]['start']; R0, R1 = T_L13 - 0.6, T_L13 + 0.4     # 1 s ramp into the post-L13 fix
T_PRIEST = [w for w in W if w['line'] == 15][0]['start']; T_COURT_END = [w for w in W if w['line'] == 17][-1]['end']
T_BC = [w for w in W if w['word'].startswith('Blood')][0]['start']
E0, E1 = T_COURT_END, T_BC - 0.15                                    # ease the swell (-3 dB) between "heard her." and "Blood Countess"
F0 = DUR - 2.5
FIX_DB, EASE_DB = -3.5, -3.0
def ebur(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); tp = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', r); return I, float(tp[-1])
def ramp(a, b): return f"clip((t-{a})/{b - a},0,1)"
VOCH = f"aresample={SR},highpass=f=70,volume=10dB,acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2dB,acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3,apad,atrim=0:{DUR}"
def bed_chain(bed_db, auto=True):
    s = (f"[1:a]aresample={SR},atrim={T0A}:{T0A + A_END},asetpts=N/SR/TB[ba];[2:a]aresample={SR},atrim={B_START}:{OFFB + DUR},asetpts=N/SR/TB[bb];"
         f"[ba][bb]acrossfade=d={XF}:c1=qsin:c2=qsin,atrim=0:{DUR},afade=t=in:st=0:d=0.02,volume={bed_db}dB")
    if not auto: return s + f",afade=t=out:st={F0}:d=2.5[bed0];"
    fx = 10 ** (FIX_DB / 20); ez = 10 ** (EASE_DB / 20)
    return (s + f",asplit=2[dry][wet];[wet]equalizer=f=2000:width_type=q:w=1:g=-3,volume='{fx}*{ramp(R0, R1)}':eval=frame[w2];"
            f"[dry]volume='1-{ramp(R0, R1)}':eval=frame[d2];[d2][w2]amix=inputs=2:normalize=0,"
            f"volume='1-(1-{ez})*{ramp(E0, E1)}':eval=frame,afade=t=out:st={F0}:d=2.5[bed0];")
def inputs(): return ['-i', str(VO), '-i', str(BED), '-i', str(BED)]
def run(fc, out): subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', *inputs(), '-filter_complex', fc, '-ar', str(SR), str(out)], check=True)
def mix(out, bed_db, master_db):
    fc = (f"[0:a]{VOCH},asplit=2[vo][sc];" + bed_chain(bed_db) + "[bed0][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bed];"
          f"[vo][bed]amix=inputs=2:normalize=0:duration=first,acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,volume={master_db}dB,"
          f"aresample=192000,alimiter=limit=0.85:attack=1:release=60:level=0,aresample={SR},aformat=sample_fmts=s16:channel_layouts=stereo")
    run(fc, out)
if __name__ == '__main__':
    log = dict(window=dict(track_start=T0A, segA=[T0A, T0A + A_END], segB=[B_START, OFFB + DUR], crossfade_cut_s=[TX - XF / 2, TX + XF / 2],
               crossfade_track_A=[T0A + TX - XF / 2, T0A + A_END], crossfade_track_B=[B_START, OFFB + TX + XF / 2], repeat_s=T0A - OFFB,
               map='cut t -> track t+256 (t<38.5), t+242.4 after'), fix=dict(ramp=[R0, R1], extra_duck_db=FIX_DB, eq='2 kHz bell -3 dB Q1 (bed only)'),
               ease=dict(ramp=[E0, E1], db=EASE_DB), priest_line_cut=T_PRIEST, priest_line_track=T_PRIEST + OFFB, blood_countess_cut=T_BC,
               blood_countess_track=T_BC + OFFB, fade=[F0, DUR], iters=[], master=[])
    vo = A / 'vo_stem.wav'
    if not vo.exists(): run(f"[0:a]{VOCH}", vo)
    Lvo, _ = ebur(vo); log['vo_I'] = Lvo; bed_db = -2.0
    for it in range(5):
        p = A / f'bedcal_{it}.wav'; fc = bed_chain(bed_db, auto=False) + "[bed0]anull"; run(fc, p); Lb, _ = ebur(p); d = Lvo - Lb
        log['iters'].append(dict(bed_db=round(bed_db, 2), bed_I=Lb, vo_over_bed_LU=round(d, 2)))
        if abs(d - 12.0) <= 0.3: break
        bed_db += d - 12.0
    master = 0.0
    for it in range(8):
        p = A / f'mix_{it}.wav'; mix(p, bed_db, master); I, tp = ebur(p); log['master'].append(dict(master_db=round(master, 2), I=I, TP=tp))
        if abs(I + 14.0) <= 0.1 and tp <= -1.1: break
        master += -14.0 - I
    log.update(final_wav=str(p), bed_db=round(bed_db, 2), master_db=round(master, 2), I=I, TP=tp)
    final = A / 'mix_v3b_final.wav'; p.rename(final); log['final_wav'] = str(final)
    mp3 = V3 / 'vo/mix_v3b_final.mp3'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n', '-i', str(final), '-c:a', 'libmp3lame', '-b:a', '320k', str(mp3)], check=True)
    log['mp3'] = str(mp3); log['mp3_ebur'] = ebur(mp3)
    for q in A.glob('bedcal_*.wav'): q.unlink()
    for q in A.glob('mix_[0-9]*.wav'): q.unlink()
    json.dump(log, open(BR / 'logs_v3b/mix_log.json', 'x'), indent=1); print(json.dumps(log, indent=1))
