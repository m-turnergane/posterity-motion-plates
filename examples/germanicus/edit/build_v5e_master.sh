#!/usr/bin/env bash
# Germanicus v5e ROUGH master (NOT YET RUN; written Tue Oct 27 2026 ~7:10 PM EDT). Supersedes build_v5d_master.sh (kept, unchanged).
# Picture = v5d (v5c master, outro re-encoded from the caption-free v5b master, no burnt-in caption).
# Audio   = v5e remix of the v5c stems (score +3.5 dB from 112 s, 1.5 s ramp; extra 2.5 dB SFX duck under "His"/"fought"), AAC 256k (v5c master convention).
# Frames 0-3599 (0-120.0 s): stream copy from the v5c master (keyframe at 3600 = 120.0 s; GOP30).
# Frames 3600-3756: re-encoded from v5b master frames 3600-3718 + 38 cloned last frames, same encoder settings as v5b/v5c masters.
# Needs >= 340 MB free (240 master + 80 reserve + scratch/audio). Deletes nothing pre-existing; scratch = $TMP only.
set -euo pipefail
R=/workspace/posterity/renders
E5=/workspace/posterity/standalones/germanicus/edit
SRC_C=$R/posterity-germanicus-v5c-ROUGH.mp4     # md5 979a8be1258b47b94457481a4ce4f1e8
SRC_B=$R/posterity-germanicus-v5b-ROUGH.mp4     # md5 9e696b000fdf183607613e38f6e22573 (caption-free outro plate)
OUT=$R/posterity-germanicus-v5e-ROUGH.mp4
AUD_DIR=$E5/_build_v5e/audio_master            # new dir; the remix script refuses to overwrite
AUD=$AUD_DIR/mix_aac256.m4a
TMP=/workspace/tmp/v5e_master
test ! -e "$OUT" || { echo "exists: $OUT"; exit 1; }
FREE=$(df -Pm / | awk 'NR==2{print $4}'); [ "$FREE" -ge 340 ] || { echo "only ${FREE} MB free; need >=340"; exit 1; }
mkdir -p "$TMP"
# 0) master audio: the same deterministic stem remix as the v5e preview (needs G/edit/_build_v5c/audio stems)
[ -s "$AUD" ] || ( cd "$E5" && python3 remix_audio_germanicus_v5e.py --gain 3.5 --ramp 112.0:113.5 --duck 2.5 --aac256 --out "$AUD_DIR" )
test -s "$AUD"
ENC=(-c:v libx264 -pix_fmt yuv420p -crf 16 -preset medium -profile:v high -g 30 -keyint_min 30 -x264-params keyint=30:min-keyint=30:scenecut=0)
# 1) outro tail, timestamps kept absolute (120.0 s) for the join
ffmpeg -v error -n -ss 120 -copyts -i "$SRC_B" -map 0:v -vf "tpad=stop_mode=clone:stop=38" -frames:v 157 "${ENC[@]}" -r 30 -f mpegts "$TMP/tail_raw.ts"
# 2) align tail pts with the stream-copied head in mpegts (head first pts 1.4667; tail 121.4) -> +2 frames
ffmpeg -v error -n -copyts -i "$TMP/tail_raw.ts" -c copy -muxdelay 0 -muxpreload 0 -output_ts_offset 0.0666667 -f mpegts "$TMP/tail.ts"
python3 - "$TMP/tail.ts" <<'PY'
import subprocess,sys
p=subprocess.run(["ffprobe","-v","error","-show_entries","packet=pts_time","-of","csv=p=0",sys.argv[1]],capture_output=True,text=True).stdout.split()
assert abs(min(float(x.strip(",")) for x in p if x.strip(","))-121.466667)<1e-3, p[:3]
PY
# 3) head (stream copy) + tail -> mux with the v5e audio (stream copy)
cat <(ffmpeg -v error -i "$SRC_C" -map 0:v -c copy -frames:v 3600 -f mpegts -) "$TMP/tail.ts" \
 | ffmpeg -v error -n -f mpegts -i - -i "$AUD" -map 0:v -map 1:a -c copy -movflags +faststart "$OUT"
rm -rf "$TMP"
# 4) QC
ffprobe -v error -show_entries format=duration,size:stream=codec_name,nb_frames,duration,start_time -of compact "$OUT"   # expect 3757 frames, 125.233 s
md5sum "$OUT"
ffmpeg -v error -i "$OUT" -f null - && echo "full decode OK"
ffprobe -v error -select_streams v -show_entries packet=pts_time -of csv=p=0 "$OUT" | sort -g | awk 'NR>1{d=$1-p; if(d<0.0333||d>0.0334) print "PTS GAP",p,$1} {p=$1} END{print NR" video packets"}'
for f in "$SRC_C" "$OUT"; do ffmpeg -v error -i "$f" -map 0:v -frames:v 3600 -f framemd5 - | grep -v '^#' | awk -F, '{print $NF}' | md5sum; done   # must match
ffmpeg -hide_banner -nostats -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' | grep -E "I:|Peak:"   # expect ~-14.1 LUFS, peak <= -1
mkdir -p "$E5/qc_rough_v5e"
ffmpeg -v error -n -i "$OUT" -vf "select='eq(n\,3605)+eq(n\,3620)+eq(n\,3640)+eq(n\,3680)+eq(n\,3690)+eq(n\,3720)+eq(n\,3740)+eq(n\,3756)',scale=270:480,tile=4x2" -frames:v 1 -fps_mode passthrough "$E5/qc_rough_v5e/outro_contact_sheet_v5e_master.png"   # expect no caption
df -m /
