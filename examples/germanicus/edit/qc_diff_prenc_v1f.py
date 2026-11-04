#!/usr/bin/env python3
"""v1f vs v1e caption burn BEFORE encoding: same concat input (hard-linked v1e clips), ass filter with v1e vs v1f .ass, frames 0-119, decoded rgb24 diff. Also master diff split inside/outside the caption box. New files only."""
import json, subprocess, numpy as np
from pathlib import Path
E = Path("/workspace/posterity/standalones/germanicus/edit"); Q = E / "qc_rough_v1f"; OUT = Q / "caption_diff_preencode_v1f.json"; assert not OUT.exists()
cc = E / "_build_v1f/picture/concat.txt"; N = 120; fsz = 1080 * 1920 * 3
def burn(ass): return subprocess.Popen(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(cc), "-vf", f"ass='{ass}'", "-frames:v", str(N), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
P = [burn(E / "germanicus_rough_v1e.ass"), burn(E / "germanicus_rough_v1f.ass")]; rows = []
for fi in range(N):
    a, b = (np.frombuffer(p.stdout.read(fsz), np.uint8).reshape(1920, 1080, 3).astype(np.int16) for p in P); d = np.abs(a - b).max(2)
    if d.max(): ys, xs = np.where(d > 0); rows.append(dict(f=fi, max=int(d.max()), n_px=int((d > 0).sum()), bbox_xyxy=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]))
fr = [r["f"] for r in rows]; bb = [min(r["bbox_xyxy"][i] for r in rows) for i in (0, 1)] + [max(r["bbox_xyxy"][i] for r in rows) for i in (2, 3)]
R = {"preencode": {"frames_compared": N, "differing_frames": [min(fr), max(fr)], "n": len(rows), "contiguous": fr == list(range(min(fr), max(fr) + 1)), "union_bbox_xyxy": bb}}
M = json.load(open(Q / "qc_master_v1f.json"))["frame_diff_vs_v1e"]["rows"]
# master: diff magnitude inside vs outside the caption box (union bbox padded 8 px), recomputed for frames that differ
R["master_note"] = "master frames differing vs v1e = %d..%d (x264 lookahead/mb-tree/rate-control re-decisions in GOPs f0-29, f30-59, f60-89; every frame from f90 on is pixel-identical)" % (M[0]["f"], M[-1]["f"])
x0, y0, x1, y1 = bb[0] - 8, bb[1] - 8, bb[2] + 8, bb[3] + 8; R["caption_box_padded"] = [x0, y0, x1, y1]
P = [subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"/workspace/posterity/renders/posterity-germanicus-ROUGH-{v}.mp4", "-frames:v", "95", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE) for v in ("v1e", "v1f")]
out = []
for fi in range(95):
    a, b = (np.frombuffer(p.stdout.read(fsz), np.uint8).reshape(1920, 1080, 3).astype(np.int16) for p in P); d = np.abs(a - b).max(2); m = np.zeros_like(d, bool); m[y0:y1, x0:x1] = True
    out.append(dict(f=fi, inside_max=int(d[m].max()), inside_mean=round(float(d[m].mean()), 3), outside_max=int(d[~m].max()), outside_mean=round(float(d[~m].mean()), 4), outside_px_gt8=int((d[~m] > 8).sum())))
R["master_inside_vs_outside"] = out
R["summary"] = {"outside_max_any": max(o["outside_max"] for o in out), "outside_mean_max": max(o["outside_mean"] for o in out), "inside_mean_f36_73_min": min(o["inside_mean"] for o in out if 36 <= o["f"] <= 73),
                "inside_max_f36_73_min": min(o["inside_max"] for o in out if 36 <= o["f"] <= 73), "outside_px_gt8_max": max(o["outside_px_gt8"] for o in out)}
json.dump(R, open(OUT, "x"), indent=1); print(json.dumps({k: v for k, v in R.items() if k != "master_inside_vs_outside"}, indent=1))
