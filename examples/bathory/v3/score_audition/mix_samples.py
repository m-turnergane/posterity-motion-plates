#!/usr/bin/env python3
"""TEMP score-audition samples (audio only, NOT a cut mix). VO = TEMP Oliver read of Scriptor DRAFT VO.
Each sample = [VO 0.0-15.4s 'opening'] + 0.8s crossfade + [VO 57.9-72.5s 'build/payoff, Movement 4 turn'],
bed taken from the SAME offsets inside the recommended 90s window, so the VO/bed relationship is what the cut would have.
Bed pre-duck at VO-12 LU, sidechain duck like v2 rough (attack 15ms, ratio 2.5, release 700ms, knee 4), master two-pass loudnorm -14 LUFS / -1.5 dBTP."""
import subprocess, re, json, sys
VO = 'TEMP_vo_oliver_v3_scriptorDRAFT.mp3'
SEGS = [(0.0, 15.4), (57.9, 72.5)]
TRACKS = {'anabasis_i': ('anabasis_i.mp3', 256), 'katabasis_i': ('katabasis_i.mp3', 424), 'dark_times': ('dark_times.mp3', 66), 'eyes_in_the_void': ('eyes_in_the_void.mp3', 0)}
def lufs(f, extra=[]):
    e = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', *extra, '-i', f, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = e[e.rfind('Summary:'):]; return float(re.search(r'I:\s*(-?[\d.]+) LUFS', s).group(1)), float(re.search(r'Peak:\s*(-?[\d.]+) dBFS', s).group(1))
def run(cmd): subprocess.run(cmd, check=True, capture_output=True)
vo_I = lufs(VO)[0]; res = {}
for tag, (src, W) in TRACKS.items():
    # build VO and bed stems (48k stereo wav scratch)
    def stem(inp, off, out, mono):
        f = []; 
        for i, (a, b) in enumerate(SEGS):
            f.append(f"[0:a]atrim={off+a}:{off+b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts={'mono' if mono else 'stereo'}[s{i}]")
        f.append('[s0][s1]acrossfade=d=0.8:c1=tri:c2=tri[o]')
        run(['ffmpeg', '-y', '-v', 'error', '-i', inp, '-filter_complex', ';'.join(f), '-map', '[o]', out])
    stem(VO, 0, f'_vo_{tag}.wav', True); stem(src, W, f'_bed_{tag}.wav', False)
    bI = lufs(f'_bed_{tag}.wav')[0]; vI = lufs(f'_vo_{tag}.wav')[0]
    g = (vI - 12) - bI
    fc = (f"[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][sc];[1:a]volume={g:.2f}dB,afade=t=in:d=0.02[b0];"
          f"[b0][sc]sidechaincompress=threshold=0.03:ratio=2.5:attack=15:release=700:knee=4[bd];[v][bd]amix=inputs=2:normalize=0,afade=t=out:st=28.2:d=1.0[m]")
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'_vo_{tag}.wav', '-i', f'_bed_{tag}.wav', '-filter_complex', fc, '-map', '[m]', f'_mix_{tag}.wav'])
    # ducked bed alone, for the VO-over-bed figure
    fc2 = fc.replace('[v][bd]amix=inputs=2:normalize=0,afade=t=out:st=28.2:d=1.0[m]', '[bd]anull[m]').replace('[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][sc]', '[0:a]pan=stereo|c0=c0|c1=c0[sc]')
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'_vo_{tag}.wav', '-i', f'_bed_{tag}.wav', '-filter_complex', fc2, '-map', '[m]', f'_bedduck_{tag}.wav'])
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', f'_mix_{tag}.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rfind('{'):m.rfind('}')+1])
    ln = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    out = f'sample_{tag}.mp3'
    run(['ffmpeg', '-y', '-v', 'error', '-i', f'_mix_{tag}.wav', '-af', ln + ',aresample=44100', '-c:a', 'libmp3lame', '-b:a', '128k', out])
    I, P = lufs(out); TP = lufs(out, [])[1]
    tp = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    tpv = float(re.search(r'True peak:\s*Peak:\s*(-?[\d.]+)', tp[tp.rfind('Summary:'):], re.S).group(1))
    dI = lufs(f'_bedduck_{tag}.wav')[0]
    res[tag] = dict(file=out, window_start_s=W, bed_gain_dB=round(g, 2), vo_stem_I=vI, bed_ducked_I=dI, vo_over_ducked_bed_LU=round(vI - dI, 1), sample_I=I, sample_TP=tpv,
                    dur=float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout))
    print(tag, res[tag], flush=True)
json.dump(res, open('samples_TEMP_measurements.json', 'w'), indent=1)
