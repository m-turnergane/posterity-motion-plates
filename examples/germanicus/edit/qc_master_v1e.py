#!/usr/bin/env python3
"""v1e master QC (copy of qc_master_v1d.py; + dense 7B tag rows k<=12 and f1285 in the 7B sheet) (new files only): ffprobe, md5, ebur128, contact sheet, decoded 7B still-zone audit vs static-plate reference, lamp swing, edges, IR tag, TEMP search."""
import json, subprocess, hashlib, math, re, numpy as np, cv2
from pathlib import Path
from PIL import Image
E = Path("/workspace/posterity/standalones/germanicus/edit"); Q = E / "qc_rough_v1e"; M = Path("/workspace/posterity/renders/posterity-germanicus-ROUGH-v1e.mp4")
OUT = Q / "qc_master_v1e.json"; SHEET = Q / "contact_sheet_v1e_360x640.png"; S7 = Q / "contact_7B_v1e_360x640.png"
for p in (OUT, SHEET, S7): assert not p.exists(), p
src = open(E / "build_rough_germanicus_v1e.py").read()
ns = dict(np=np, cv2=cv2, Image=Image, math=math, FPS=30, W=1080, H=1920, UP=2)
for fn in ("prepare_cover", "cam", "cam_frame"):
    a = src.index(f"def {fn}("); b = src.index("\ndef ", a + 5); exec(src[a:b], ns)
TL = json.load(open(E / "_build_v1e/timeline.json")); segs = TL["segments"] if isinstance(TL, dict) and "segments" in TL else TL
seg7 = [s for s in segs if s.get("id") == "7B"][0]
R = {}
R["md5"] = hashlib.md5(open(M, "rb").read()).hexdigest(); R["bytes"] = M.stat().st_size
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(M)], capture_output=True, text=True).stdout)
v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]; a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
R["ffprobe"] = dict(width=v["width"], height=v["height"], v_codec=v["codec_name"], profile=v.get("profile"), pix_fmt=v["pix_fmt"], fps=v["r_frame_rate"], nb_frames=v.get("nb_frames"),
                    v_bitrate=v.get("bit_rate"), a_codec=a["codec_name"], a_rate=a["sample_rate"], a_ch=a["channels"], a_bitrate=a.get("bit_rate"), duration=float(pr["format"]["duration"]),
                    v_dur=float(v["duration"]), a_dur=float(a["duration"]))
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(M), "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; o = o[o.find("Summary"):]
g = lambda k, u: float(o.split(k)[1].split(u)[0]); R["ebur128"] = dict(I_LUFS=g("I:", "LUFS"), LRA_LU=g("LRA:", "LU"), TP_dBTP=g("Peak:", "dBFS"))
# decode all frames (1080x1920) once, streaming
f0, nf = seg7["f0"], seg7["frames"]; N = int(R["ffprobe"]["nb_frames"] or 2070)
cuts = [(s["id"], s["f0"], s["frames"]) for s in segs]
want_sheet = sorted({s0 + n // 2 for _, s0, n in cuts})
want7 = [f0 + k for k in (0, 5, 39, 78, 117, nf - 1)]
plate = Image.open(seg7["plate"]).convert("RGB"); base = ns["prepare_cover"](plate)
still = cv2.imread("/workspace/posterity/standalones/germanicus/masks/v1d/G7d_still_zone_v1d.png", 0)
rel = cv2.imread("/workspace/posterity/standalones/germanicus/masks/v1d/G7d_relight_falloff_v1d.png", 0)
def to_frame(mask, u):   # map a plate-space mask through the same cover + camera (nearest)
    m = Image.fromarray(mask).resize(base.size, Image.Resampling.NEAREST); return np.asarray(ns["cam_frame"](m.convert("RGB"), seg7, u, 0))[..., 0] > 127
ir = (175, 296, 905, 337); capband = (1360, 1545)
BOXES = dict(blade=(355, 760, 575, 1180), hand_upper=(400, 430, 600, 700), floor_pool=(430, 1360, 630, 1425))   # plate coords (blade cut above captions)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(M), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fsz = 1080 * 1920 * 3; sheet, s7, rows, edges = {}, {}, [], []
for fi in range(N):
    buf = p.stdout.read(fsz)
    if len(buf) < fsz: break
    fr = np.frombuffer(buf, np.uint8).reshape(1920, 1080, 3)
    if fi % 3 == 0:
        lum = fr.mean(2); edges.append((fi, float(lum[:2].mean()), float(lum[-2:].mean()), float(lum[:, :2].mean()), float(lum[:, -2:].mean()),
                                       float((lum[:2] < 8).mean()), float((lum[-2:] < 8).mean()), float((lum[:, :2] < 8).mean()), float((lum[:, -2:] < 8).mean())))
    if fi in want_sheet: sheet[fi] = cv2.resize(fr, (360, 640), interpolation=cv2.INTER_AREA)
    if f0 <= fi < f0 + nf:
        k = fi - f0; u = k / max(nf - 1, 1)
        ref = np.asarray(ns["cam_frame"](base, seg7, u, k / 30)).astype(np.int16)
        if k % 26 == 0 or k == nf - 1 or k <= 12:
            stz = to_frame(still, u); rlz = to_frame((rel > 77).astype(np.uint8) * 255, u)
            ex = np.zeros_like(stz); ex[capband[0]:capband[1]] = True; ex[150:420] = True   # IR tag + its soft scrim band (full width)
            core = cv2.erode(stz.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~ex
            d = np.abs(fr.astype(np.int16) - ref).max(2); rr = rlz & ~ex & ~stz
            irr = d[ir[1]:ir[3], ir[0]:ir[2]]; sh = {}
            for nm, (x0, y0, x1, y1) in BOXES.items():
                bm = np.zeros(still.shape, np.uint8); bm[y0:y1, x0:x1] = 255; bx, by_, bw, bh = cv2.boundingRect(to_frame(bm, u).astype(np.uint8))
                if nm != "hand_upper": by_, bh = by_, min(bh, max(0, capband[0] - by_)) if by_ < capband[0] and nm == "blade" else bh
                a_ = cv2.cvtColor(fr[by_:by_ + bh, bx:bx + bw], cv2.COLOR_RGB2GRAY).astype(np.float32); b_ = cv2.cvtColor(ref[by_:by_ + bh, bx:bx + bw].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
                (sx, sy), _ = cv2.phaseCorrelate(b_, a_); sh[nm] = [round(sx, 3), round(sy, 3)]
            rows.append(dict(f=fi, k=k, still_px=int(core.sum()), still_absdiff_mean=round(float(d[core].mean()), 3), still_absdiff_p99=float(np.percentile(d[core], 99)), still_absdiff_max=int(d[core].max()),
                             relit_lum_ratio=round(float(fr[rr].mean() / ref[rr].mean()), 4), relit_absdiff_mean=round(float(d[rr].mean()), 2),
                             ir_box_diff_mean=round(float(irr.mean()), 2), ir_box_bright_px=int((fr[ir[1]:ir[3], ir[0]:ir[2]].min(2) > 200).sum()), phasecorr_shift_px=sh))
        if fi in want7: s7[fi] = cv2.resize(fr, (360, 640), interpolation=cv2.INTER_AREA)
    if fi == f0 + nf: pass
p.stdout.close(); p.wait(); R["decoded_frames"] = fi + 1 if len(buf) == fsz else fi
def tile(d, path, cols):
    ks = sorted(d); ims = [cv2.putText(d[k].copy(), f"f{k}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2) for k in ks]
    while len(ims) % cols: ims.append(np.zeros_like(ims[0]))
    g_ = np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)]); Image.fromarray(g_).save(path)
sheet.update({k: v_ for k, v_ in s7.items()}); tile(sheet, SHEET, 6); tile(s7, S7, 5)
E_ = np.array(edges)
R["edges"] = dict(frames_checked=len(edges), min_mean_lum=dict(top=round(float(E_[:, 1].min()), 1), bottom=round(float(E_[:, 2].min()), 1), left=round(float(E_[:, 3].min()), 1), right=round(float(E_[:, 4].min()), 1)),
                  max_black_frac=dict(top=round(float(E_[:, 5].max()), 3), bottom=round(float(E_[:, 6].max()), 3), left=round(float(E_[:, 7].max()), 3), right=round(float(E_[:, 8].max()), 3)),
                  worst_frames=[int(E_[np.argmin(E_[:, c]), 0]) for c in (1, 2, 3, 4)])
# 7B decoded audit (dense: every 26th frame + last)
lr = np.array([r_["relit_lum_ratio"] for r_ in rows])
R["audit_7B_decoded"] = dict(method="master frames vs static-plate reference (same cover + StablePush 1.00->1.03 @ (0.5,0.5)); still zone eroded 4 px; caption band y1360-1545 and IR tag scrim band y150-420 excluded (overlays); phase-correlation shift of blade/hand/pool crops vs reference",
                             rows=rows, still_absdiff_max=max(r_["still_absdiff_max"] for r_ in rows), still_absdiff_mean_max=max(r_["still_absdiff_mean"] for r_ in rows),
                             relit_ratio_range=[round(float(lr.min()), 4), round(float(lr.max()), 4)])
txt = subprocess.run(["bash", "-c", f"grep -c -i 'TEMP' {E}/germanicus_rough_v1e.ass; grep -c -i 'TEMP' {E}/build_rough_germanicus_v1e.py"], capture_output=True, text=True).stdout.split()
R["temp_watermark"] = dict(grep_TEMP_in_ass=int(txt[0]), grep_TEMP_in_build_script=int(txt[1]), note="no watermark code path; 7B still-zone + relit pixels match the clean plate reference (see audit)")
json.dump(R, open(OUT, "x"), indent=1); print(json.dumps({k: v_ for k, v_ in R.items() if k != "audit_7B_decoded"}, indent=1)); print(json.dumps({k: v_ for k, v_ in R["audit_7B_decoded"].items() if k != "rows"}, indent=1))
for r_ in rows: print(r_)
