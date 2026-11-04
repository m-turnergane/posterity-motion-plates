#!/usr/bin/env python3
"""v5 final master QC (from qc_master_v1e.py; new files only): ffprobe, md5, ebur128, 360x640 contact sheet, every plate >= 3 s, caption text == VO text,
zero-displacement audit on EVERY picture segment (master frames vs a static cam_frame reference of the clean plate, same cover + zoom), lit plates
(1A/4/6/7B): protect + persons masks (absdiff + phase-correlation), change confined to relight/flame zones; edges (vignette/letterbox), TEMP / IR grep."""
import json, subprocess, hashlib, math, re, numpy as np, cv2, sys
from pathlib import Path
from PIL import Image
G = Path("/workspace/posterity/standalones/germanicus"); E = G / "edit"; Q = E / "qc_rough_v5final"; M = Path("/workspace/posterity/renders/posterity-germanicus-v5-ROUGH.mp4")
B = E / "_build_v5final"; MK = G / "masks/v1b"
OUT = Q / "qc_master_v5final.json"; SHEET = Q / "contact_sheet_v5final_360x640.png"
for p in (OUT, SHEET): assert not p.exists(), p
src = open(E / "build_rough_germanicus_v5.py").read()
ns = dict(np=np, cv2=cv2, Image=Image, math=math, FPS=30, W=1080, H=1920, UP=2)
for fn in ("prepare_cover", "cam", "cam_frame"):
    a = src.index(f"def {fn}("); b = src.index("\ndef ", a + 5); exec(src[a:b], ns)
TL = json.load(open(B / "timeline.json")); segs = TL["segments"]; caps = TL["captions"]
R = {}
R["md5"] = hashlib.md5(open(M, "rb").read()).hexdigest(); R["bytes"] = M.stat().st_size
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(M)], capture_output=True, text=True).stdout)
v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]; a = [s for s in pr["streams"] if s["codec_type"] == "audio"][0]
R["ffprobe"] = dict(width=v["width"], height=v["height"], v_codec=v["codec_name"], profile=v.get("profile"), pix_fmt=v["pix_fmt"], fps=v["r_frame_rate"], nb_frames=v.get("nb_frames"),
                    v_bitrate=v.get("bit_rate"), a_codec=a["codec_name"], a_rate=a["sample_rate"], a_ch=a["channels"], a_bitrate=a.get("bit_rate"), duration=float(pr["format"]["duration"]),
                    v_dur=float(v["duration"]), a_dur=float(a["duration"]))
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(M), "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr; o = o[o.find("Summary"):]
g = lambda k, u: float(o.split(k)[1].split(u)[0]); R["ebur128"] = dict(I_LUFS=g("I:", "LUFS"), LRA_LU=g("LRA:", "LU"), TP_dBTP=g("Peak:", "dBFS"))
R["plates"] = [dict(id=s["id"], plate=Path(s["plate"]).name, start=round(s["start"], 3), end=round(s["end"], 3), dur=round(s["duration"], 3), placeholder=s.get("placeholder")) for s in segs]
R["plates_under_3s"] = [p for p in R["plates"] if p["dur"] < 3.0]
script = (G / "raw/script-vo-v5-DRAFT.txt").read_text(); n_ = lambda s: " ".join(s.split())
ass = (E / "germanicus_v5_rough_final.ass").read_text(); dlg = [ln.split(",,", 1)[1].split(",", 4)[-1] if False else ln for ln in ass.splitlines() if ln.startswith("Dialogue:")]
ass_txt = n_(" ".join(re.sub(r"\{[^}]*\}", "", re.sub(r"\\N", " ", ln.split(",", 9)[9])) for ln in dlg))
R["captions"] = dict(cues=len(caps), dialogue_lines=len(dlg), hidden=[c for c in caps if c["hidden_under_title"]], timeline_text_equals_script=n_(" ".join(c["text"] for c in caps)) == n_(script),
                     burnt_ass_text_equals_script=ass_txt == n_(script))
# ------------------------------------------------------------------ decode + audit
LIT = {"1A": "G1a", "4": "G4", "6": "G6", "7B": "G7b5"}; LITDIR = {"G7b5": (G / "masks/v5", "_v5")}; CAP = (1360, 1545); TOPBAND = (150, 480)
def to_frame(mask, seg, u):
    m = ns["prepare_cover"](Image.fromarray(mask).convert("RGB")); return np.asarray(ns["cam_frame"](m, seg, u, 0))[..., 0] > 127
masks = {}
for sid, mk in LIT.items():
    MKd, sfx_ = LITDIR.get(mk, (MK, "_v1b"))
    pro = cv2.imread(str(MKd / f"{mk}_protect.png"), 0); per = cv2.imread(str(MKd / f"{mk}_persons{sfx_}.png"), 0); rel = cv2.imread(str(MKd / f"{mk}_relight_falloff{sfx_}.png"), 0)
    fl = np.zeros_like(pro)
    for f in sorted(MKd.glob(f"{mk}_flame_c*.png")): fl = np.maximum(fl, cv2.imread(str(f), 0))
    masks[sid] = dict(protect=pro, persons=per, lightzone=((rel > 10) | (cv2.dilate(fl, np.ones((25, 25), np.uint8)) > 0)).astype(np.uint8) * 255, flame=fl)
bases = {}
def ref_frame(seg, k):
    if seg["id"] not in bases:
        p = Path(seg["plate"]); src_ = Path(seg["prepped"]) if Path(seg["prepped"]).exists() else p
        bases[seg["id"]] = ns["prepare_cover"](Image.open(src_).convert("RGB"))
    u = k / max(seg["frames"] - 1, 1); return np.asarray(ns["cam_frame"](bases[seg["id"]], seg, u, k / 30)).astype(np.int16), u
want_sheet = sorted({s["f0"] + s["frames"] // 2 for s in segs} | {60, 150})
N = int(R["ffprobe"]["nb_frames"]); p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(M), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
fsz = 1080 * 1920 * 3; sheet, rows, edges = {}, [], []; seg_at = lambda f: [s for s in segs if s["f0"] <= f < s["f1"]][0]; mcache = {}
for fi in range(N):
    buf = p.stdout.read(fsz)
    if len(buf) < fsz: break
    fr = np.frombuffer(buf, np.uint8).reshape(1920, 1080, 3)
    if fi % 3 == 0:
        lum = fr.mean(2); edges.append((fi, float(lum[:2].mean()), float(lum[-2:].mean()), float(lum[:, :2].mean()), float(lum[:, -2:].mean()),
                                       float((lum[:2] < 8).mean()), float((lum[-2:] < 8).mean()), float((lum[:, :2] < 8).mean()), float((lum[:, -2:] < 8).mean())))
    if fi in want_sheet: sheet[fi] = cv2.resize(fr, (360, 640), interpolation=cv2.INTER_AREA)
    s = seg_at(fi); k = fi - s["f0"]
    if s["id"] == "OUTRO": continue
    if not (k % 15 == 0 or k == s["frames"] - 1 or k in (1, 2)): continue
    ref, u = ref_frame(s, k); d = np.abs(fr.astype(np.int16) - ref).max(2)
    ex = np.zeros((1920, 1080), bool); ex[CAP[0]:CAP[1]] = True
    if s["id"] == segs[0]["id"]: ex[TOPBAND[0]:TOPBAND[1]] = True   # title + credit overlays on the opener
    row = dict(f=fi, seg=s["id"], k=k)
    if s["id"] in LIT:
        mm = masks[s["id"]]; key = (s["id"], k)
        lz = to_frame(mm["lightzone"], s, u); pro = to_frame(mm["protect"], s, u); per = to_frame(mm["persons"], s, u)
        outside = ~lz & ~ex; core = cv2.erode((pro | per).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool) & ~ex
        row.update(outside_light_absdiff_mean=round(float(d[outside].mean()), 3), outside_light_p99=float(np.percentile(d[outside], 99)), outside_light_max=int(d[outside].max()),
                   protect_persons_absdiff_mean=round(float(d[core].mean()), 3), protect_persons_p99=float(np.percentile(d[core], 99)),
                   protect_persons_lum_ratio=round(float(fr[core].mean() / max(ref[core].mean(), 1e-6)), 4))
        y, x = np.where(per & ~ex)
        if len(y) > 500:
            y0, y1, x0, x1 = y.min(), y.max() + 1, x.min(), x.max() + 1
            a_ = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float32); b_ = cv2.cvtColor(ref[y0:y1, x0:x1].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
            (sx, sy), _ = cv2.phaseCorrelate(b_, a_); row["persons_phasecorr_shift_px"] = [round(sx, 3), round(sy, 3)]
        y, x = np.where(pro & ~ex)
        if len(y) > 500:
            y0, y1, x0, x1 = y.min(), y.max() + 1, x.min(), x.max() + 1
            a_ = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float32); b_ = cv2.cvtColor(ref[y0:y1, x0:x1].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
            (sx, sy), _ = cv2.phaseCorrelate(b_, a_); row["protect_phasecorr_shift_px"] = [round(sx, 3), round(sy, 3)]
    else:
        m = ~ex; row.update(absdiff_mean=round(float(d[m].mean()), 3), absdiff_p99=float(np.percentile(d[m], 99)), absdiff_max=int(d[m].max()))
        a_ = cv2.cvtColor(fr[200:1350], cv2.COLOR_RGB2GRAY).astype(np.float32); b_ = cv2.cvtColor(ref[200:1350].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
        (sx, sy), _ = cv2.phaseCorrelate(b_, a_); row["phasecorr_shift_px"] = [round(sx, 3), round(sy, 3)]
    rows.append(row)
p.stdout.close(); p.wait(); R["decoded_frames"] = fi + 1 if len(buf) == fsz else fi
def tile(d, path, cols):
    ks = sorted(d); ims = [cv2.putText(d[k].copy(), f"f{k} {seg_at(k)['id']}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2) for k in ks]
    while len(ims) % cols: ims.append(np.zeros_like(ims[0]))
    g_ = np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)]); Image.fromarray(g_).save(path)
tile(sheet, SHEET, 6)
E_ = np.array(edges)
R["edges"] = dict(frames_checked=len(edges), min_mean_lum=dict(top=round(float(E_[:, 1].min()), 1), bottom=round(float(E_[:, 2].min()), 1), left=round(float(E_[:, 3].min()), 1), right=round(float(E_[:, 4].min()), 1)),
                  max_black_frac=dict(top=round(float(E_[:, 5].max()), 3), bottom=round(float(E_[:, 6].max()), 3), left=round(float(E_[:, 7].max()), 3), right=round(float(E_[:, 8].max()), 3)),
                  worst_frames=[int(E_[np.argmin(E_[:, c]), 0]) for c in (1, 2, 3, 4)],
                  note="placeholder cards are dark (30,29,28) by design; edge black fraction counts lum < 8")
lit = [r for r in rows if r["seg"] in LIT]; stat = [r for r in rows if r["seg"] not in LIT]
R["audit"] = dict(method="master frames vs static cam_frame reference of the clean plate (same cover + zoom); caption band y1360-1545 (+ y150-480 title/credit on the opener) excluded; lit: masks mapped through the same cover+camera",
                  static_segments=dict(n=len(stat), absdiff_mean_max=max(r["absdiff_mean"] for r in stat), absdiff_p99_max=max(r["absdiff_p99"] for r in stat),
                                       max_abs_shift_px=max(max(abs(x) for x in r["phasecorr_shift_px"]) for r in stat), per_seg={sid: max(r["absdiff_mean"] for r in stat if r["seg"] == sid) for sid in dict.fromkeys(r["seg"] for r in stat)}),
                  lit_segments=dict(n=len(lit), outside_light_absdiff_mean_max=max(r["outside_light_absdiff_mean"] for r in lit), outside_light_p99_max=max(r["outside_light_p99"] for r in lit),
                                    protect_persons_absdiff_mean_max=max(r["protect_persons_absdiff_mean"] for r in lit),
                                    persons_max_abs_shift_px=max(max(abs(x) for x in r.get("persons_phasecorr_shift_px", [0, 0])) for r in lit),
                                    protect_max_abs_shift_px=max(max(abs(x) for x in r.get("protect_phasecorr_shift_px", [0, 0])) for r in lit),
                                    lum_ratio_range=[min(r["protect_persons_lum_ratio"] for r in lit), max(r["protect_persons_lum_ratio"] for r in lit)]), rows=rows)
gr = lambda pat, f: int(subprocess.run(["grep", "-c", "-i", "-E", pat, str(f)], capture_output=True, text=True).stdout.strip() or 0)
R["markings"] = dict(TEMP_in_ass=gr("TEMP", E / "germanicus_v5_rough_final.ass"), ILLUSTRATIVE_in_ass=gr("ILLUSTRATIVE|RECONSTRUCTION", E / "germanicus_v5_rough_final.ass"),
                     TEMP_in_build=gr("TEMP", E / "build_rough_germanicus_v5.py"), IR_code_in_build=gr("ir_png|ir_layer|IR_FADE|IR\\[", E / "build_rough_germanicus_v5.py"),
                     ILLUSTRATIVE_mentions_in_build=gr("ILLUSTRATIVE", E / "build_rough_germanicus_v5.py"), note="build mention is the docstring line stating the tag was removed; overlays = title + credit only")
json.dump(R, open(OUT, "x"), indent=1, default=float); print(json.dumps({k: v_ for k, v_ in R.items() if k != "audit"}, indent=1, default=float)); print(json.dumps({k: v_ for k, v_ in R["audit"].items() if k != "rows"}, indent=1, default=float))
