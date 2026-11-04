#!/usr/bin/env python3
"""Audition samples + full previews under the LOCKED Oliver read (vo_oliver_v3_locked.mp3). Audio only, no video.
Same method as mix_samples.py: Part A = VO start..end of L03, Part B = VO start of L13..end of L15, bed from the SAME offsets inside each window,
bed pre-duck VO-12 LU, sidechain duck (attack 15, ratio 2.5, release 700, knee 4), master: acompressor 3:1, gain to -14 LUFS, 4x-oversampled alimiter.
Fix variant (Anabasis): from the build onward (57.4 s, ramp 1 s) the bed gets -3 dB extra and a -3 dB bell at 2 kHz (Q 1)."""
import subprocess, re, json
VO = 'vo_oliver_v3_locked.mp3'
S = json.load(open('vo_sentences_v3_locked.json'))['sentences']
st = {x['text'][:20]: x for x in S}
A = (0.0, round(next(x for x in S if x['text'].startswith('He sent'))['end'] + 0.2, 2))
B0 = next(x for x in S if x['text'].startswith('Then someone'))['start']; B1 = next(x for x in S if x['text'].startswith('No witness'))['end']
B = (round(B0 - 0.25, 2), round(B1 + 0.2, 2))
FIX_T = round(B0 - 0.75, 2)   # build onward
VOEND = S[-1]['end']
TR = {'anabasis_i': ('anabasis_i.mp3', 256), 'katabasis_i': ('katabasis_i.mp3', 424), 'dark_times': ('dark_times.mp3', 66), 'eyes_in_the_void': ('eyes_in_the_void.mp3', 0)}
def meas(f):
    e = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = e[e.rfind('Summary:'):]; return float(re.search(r'I:\s*(-?[\d.]+) LUFS', s).group(1)), float(re.search(r'True peak:\s*Peak:\s*(-?[\d.]+)', s, re.S).group(1))
def run(c): subprocess.run(c, check=True, capture_output=True)
def dur(f): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
def stems_sample(tag, src, W):
    for inp, off, out, lay in [(VO, 0, f'_v_{tag}.wav', 'mono'), (src, W, f'_b_{tag}.wav', 'stereo')]:
        f = [f"[0:a]atrim={off+a}:{off+b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts={lay}[s{i}]" for i, (a, b) in enumerate([A, B])]
        run(['ffmpeg', '-y', '-v', 'error', '-i', inp, '-filter_complex', ';'.join(f) + ';[s0][s1]acrossfade=d=0.8:c1=tri:c2=tri[o]', '-map', '[o]', out])
    return A[1] - 0.8   # fix starts where Part B begins in the sample (whole of Part B is post-build)
def stems_full(tag, src, W, L):
    run(['ffmpeg', '-y', '-v', 'error', '-i', VO, '-af', f'aformat=sample_rates=48000:channel_layouts=mono,apad=whole_dur={L}', f'_v_{tag}.wav'])
    run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', f'atrim={W}:{W+L},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo', f'_b_{tag}.wav'])
    return FIX_T
def mix(tag, fix_at, out, L, fade_d):
    vI = meas(f'_v_{tag}.wav')[0]; bI = meas(f'_b_{tag}.wav')[0]; g = (vI - 12) - bI
    if fix_at is None:
        bed = f"[1:a]volume={g:.2f}dB[b0]"
    else:  # crossfade dry -> (-3 dB, 2 kHz -3 dB) over 1 s at fix_at
        bed = (f"[1:a]volume={g:.2f}dB,asplit=2[d][w];[d]volume='if(lt(t,{fix_at}),1,if(lt(t,{fix_at+1}),1-(t-{fix_at}),0))':eval=frame[d2];"
               f"[w]equalizer=f=2000:width_type=q:w=1:g=-3,volume=-3dB,volume='if(lt(t,{fix_at}),0,if(lt(t,{fix_at+1}),(t-{fix_at}),1))':eval=frame[w2];[d2][w2]amix=inputs=2:normalize=0[b0]")
    fc = (f"[0:a]pan=stereo|c0=c0|c1=c0,asplit=3[v][sc][sc2];{bed};[b0]asplit=2[b1][b2];"
          f"[b1][sc]sidechaincompress=threshold=0.03:ratio=2.5:attack=15:release=700:knee=4[bd];"
          f"[b2][sc2]sidechaincompress=threshold=0.03:ratio=2.5:attack=15:release=700:knee=4[bdo];"
          f"[v][bd]amix=inputs=2:normalize=0,afade=t=out:st={L-fade_d}:d={fade_d}[m]")
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'_v_{tag}.wav', '-i', f'_b_{tag}.wav', '-filter_complex', fc, '-map', '[m]', '-c:a', 'pcm_s24le', f'_mm_{tag}.wav', '-map', '[bdo]', '-c:a', 'pcm_s24le', f'_bd_{tag}.wav'])
    gg, lim = 13.0, 0.78
    for _ in range(10):
        af = f'acompressor=threshold=0.1:ratio=3:attack=5:release=120:makeup=1,volume={gg:.2f}dB,aresample=192000,alimiter=limit={lim}:attack=1:release=50:level=false,aresample=44100'
        run(['ffmpeg', '-y', '-v', 'error', '-i', f'_mm_{tag}.wav', '-af', af, '-c:a', 'libmp3lame', '-b:a', '128k', '-metadata', f'title={out[:-4]} (audio-only audition, LOCKED VO, not a cut)', out])
        I, TP = meas(out)
        if TP > -1.1: lim *= 0.96; continue
        if abs(I + 14) <= 0.2: break
        gg += -14 - I
    return dict(file=out, dur=round(dur(out), 2), I=I, TP=TP, vo_over_ducked_bed_LU=round(vI - meas(f'_bd_{tag}.wav')[0], 1), bed_gain_dB=round(g, 2), fix_from_s=fix_at)
R = dict(partA=A, partB=B, fix_from_build_s=FIX_T, vo_end=VOEND, out={})
L_s = (A[1] - A[0]) + (B[1] - B[0]) - 0.8
for tag, (src, W) in TR.items():
    stems_sample(tag, src, W); R['out'][f'sample_{tag}_v3c'] = mix(tag, None, f'sample_{tag}_v3c.mp3', L_s, 1.0); print(R['out'][f'sample_{tag}_v3c'], flush=True)
fx = stems_sample('anabasis_i', 'anabasis_i.mp3', 256); R['out']['sample_anabasis_i_v3c_ducked'] = mix('anabasis_i', fx, 'sample_anabasis_i_v3c_ducked.mp3', L_s, 1.0); print(R['out']['sample_anabasis_i_v3c_ducked'], flush=True)
LF = round(VOEND + 3.2, 2)
for tag, W, fix, name in [('anabasis_i', 256, True, 'preview_full_anabasis_v3c.mp3'), ('katabasis_i', 424, False, 'preview_full_katabasis_v3c.mp3')]:
    fx = stems_full(tag, f'{tag}.mp3', W, LF); R['out'][name[:-4]] = mix(tag, fx if fix else None, name, LF, 2.5); R['out'][name[:-4]]['window'] = [W, W + LF]; print(R['out'][name[:-4]], flush=True)
json.dump(R, open('v3c_measurements.json', 'w'), indent=1)
