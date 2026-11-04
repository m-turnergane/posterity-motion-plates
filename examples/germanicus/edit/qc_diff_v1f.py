#!/usr/bin/env python3
"""v1f vs v1e master: per-frame decoded diff (proves only the caption region f36-f73 changes), ffprobe, md5, ebur128, audio-stream equality, f50 contact frame. New files only."""
import json, subprocess, hashlib, numpy as np, cv2
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); Q = E / "qc_rough_v1f"; R_ = Path("/workspace/posterity/renders")
M0, M1 = R_ / "posterity-germanicus-ROUGH-v1e.mp4", R_ / "posterity-germanicus-ROUGH-v1f.mp4"; OUT = Q / "qc_master_v1f.json"; assert not OUT.exists()
R = {"md5": hashlib.md5(M1.read_bytes()).hexdigest(), "bytes": M1.stat().st_size}
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(M1)], capture_output=True, text=True).stdout)
v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]; a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
R["ffprobe"] = dict(width=v["width"], height=v["height"], v_codec=v["codec_name"], profile=v.get("profile"), pix_fmt=v["pix_fmt"], fps=v["r_frame_rate"], nb_frames=v.get("nb_frames"),
                    a_codec=a["codec_name"], a_rate=a["sample_rate"], a_ch=a["channels"], a_bitrate=a.get("bit_rate"), duration=float(pr["format"]["duration"]), v_dur=float(v["duration"]), a_dur=float(a["duration"]))
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(M1), "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; o = o[o.find("Summary"):]
g = lambda k, u: float(o.split(k)[1].split(u)[0]); R["ebur128"] = dict(I_LUFS=g("I:", "LUFS"), LRA_LU=g("LRA:", "LU"), TP_dBTP=g("Peak:", "dBFS"))
amd5 = [subprocess.run(["ffmpeg", "-v", "error", "-i", str(m), "-map", "0:a", "-c", "copy", "-f", "md5", "-"], capture_output=True, text=True).stdout.strip() for m in (M0, M1)]
R["audio_stream_md5"] = {"v1e": amd5[0], "v1f": amd5[1], "identical": amd5[0] == amd5[1]}
fsz = 1080 * 1920 * 3; P = [subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(m), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE) for m in (M0, M1)]
rows = []; fi = 0; bb = [9999, 9999, -1, -1]
while True:
    b0, b1 = P[0].stdout.read(fsz), P[1].stdout.read(fsz)
    if len(b0) < fsz or len(b1) < fsz: break
    x0 = np.frombuffer(b0, np.uint8).reshape(1920, 1080, 3).astype(np.int16); x1 = np.frombuffer(b1, np.uint8).reshape(1920, 1080, 3)
    d = np.abs(x1.astype(np.int16) - x0).max(2)
    if d.max() > 0:
        ys, xs = np.where(d > 0); r = dict(f=fi, max=int(d.max()), n_px=int((d > 0).sum()), n_px_gt8=int((d > 8).sum()), bbox_xyxy=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
        rows.append(r); bb = [min(bb[0], r["bbox_xyxy"][0]), min(bb[1], r["bbox_xyxy"][1]), max(bb[2], r["bbox_xyxy"][2]), max(bb[3], r["bbox_xyxy"][3])]
    if fi == 50: cv2.imwrite(str(Q / "contact_v1f_f50_hidden.png"), cv2.cvtColor(x1, cv2.COLOR_RGB2BGR)); cv2.imwrite(str(Q / "contact_v1f_f50_hidden_360x640.png"), cv2.resize(cv2.cvtColor(x1, cv2.COLOR_RGB2BGR), (360, 640), interpolation=cv2.INTER_AREA))
    fi += 1
for p in P: p.stdout.close(); p.wait()
fr = [r["f"] for r in rows]
R["frame_diff_vs_v1e"] = {"frames_compared": fi, "n_frames_differing": len(rows), "first": min(fr) if fr else None, "last": max(fr) if fr else None, "union_bbox_xyxy": bb if rows else None,
                          "all_within_f36_f73": all(36 <= f <= 73 for f in fr), "frames_outside_with_px_gt8": [r["f"] for r in rows if not 36 <= r["f"] <= 73 and r["n_px_gt8"]], "rows": rows}
json.dump(R, open(OUT, "x"), indent=1)
print(json.dumps({k: v for k, v in R.items() if k != "frame_diff_vs_v1e"}, indent=1)); print({k: v for k, v in R["frame_diff_vs_v1e"].items() if k != "rows"})
for r in rows[:3] + rows[-3:]: print(r)
