"""Final deliverables from the lossless renders: final-encoded POC + side-by-side, md5s, strips, output-space QC. Never overwrites."""
import sys, os, json, subprocess, hashlib, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from specs import load_masks
tag = sys.argv[1]; OUT = "."
poc_l, st_l = f"work/{tag}_poc_lossless.mp4", f"work/{tag}_v2cstatic_lossless.mp4"
poc_f, sbs_f = f"P05_naturalfire_poc_{tag}.mp4", f"P05_naturalfire_vs_v2cstatic_sbs_{tag}.mp4"
outs = [poc_f, sbs_f, poc_f + ".md5", sbs_f + ".md5", f"qc/{tag}_output_qc.json"] + [f"strips/{tag}_{n}.png" for n in ("flame4_0p25s_fullres", "full_360x640", "flame30_consec_1s_fullres", "flame12_consec_fullres", "flame_0p5s_fullres")]
for f in outs: assert not os.path.exists(f), f
os.makedirs("strips", exist_ok=True)
def run(c): subprocess.run(c, check=True)
run(["ffmpeg", "-n", "-v", "error", "-i", poc_l, "-an", *P.ENC_FINAL, "-r", "30", poc_f])
run(["ffmpeg", "-n", "-v", "error", "-i", poc_l, "-i", st_l, "-filter_complex", "[0:v][1:v]hstack=inputs=2[v]", "-map", "[v]", "-an", *P.ENC_FINAL, "-r", "30", sbs_f])
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
for p in (poc_f, sbs_f): open(p + ".md5", "w").write(f"{md5(p)}  {p}\n")
def dec(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, P.H, P.W, 3)
A, S, Fz = dec(poc_l), dec(st_l), dec(poc_f)
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", poc_f], capture_output=True).stdout)
vs = [s for s in probe["streams"] if s["codec_type"] == "video"][0]
# output-space masks per frame (camera-mapped plate masks)
masks = load_masks(); box = P.plate_box(); seg = dict(P.SEG_POC); seg["frames"] = 180
def omask(m, fi): return np.asarray(P.frame_out(np.repeat((m * 255).astype(np.float32)[..., None], 3, 2), box, seg, fi))[..., 0]
union = np.maximum.reduce(masks)
q = dict(tag=tag, poc_file=dict(name=poc_f, md5=md5(poc_f), w=vs["width"], h=vs["height"], fps=vs["r_frame_rate"], frames=int(vs.get("nb_frames", len(Fz))), dur=probe["format"]["duration"], audio_streams=sum(s["codec_type"] == "audio" for s in probe["streams"])),
         sbs_file=dict(name=sbs_f, md5=md5(sbs_f), layout="left = natural-fire POC, right = v2c static (same 6 s, same push)"))
L = lambda X: X.astype(np.float32).mean(-1)
chg_outside, codec_out = 0, []
per = {f"c{i}": dict(dF_poc=[], dF_static=[], sharp=[]) for i in range(3)}
for fi in range(len(A)):
    sup = cv2.dilate((omask(union, fi) > 0).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    chg_outside += int((np.abs(A[fi].astype(int) - S[fi]).max(-1)[~sup] > 0).sum())
    codec_out.append(float(np.abs(Fz[fi].astype(np.float32) - A[fi])[~sup].mean()))
    for i, m in enumerate(masks):
        om = omask(m, fi) > 127
        if fi > 0:
            per[f"c{i}"]["dF_poc"].append(float(np.abs(L(A[fi]) - L(A[fi - 1]))[om].mean() / L(A[fi])[om].mean()))
            per[f"c{i}"]["dF_static"].append(float(np.abs(L(S[fi]) - L(S[fi - 1]))[om].mean() / L(S[fi])[om].mean()))
        lv = lambda X: cv2.Laplacian(L(X), cv2.CV_32F)[om].var()
        per[f"c{i}"]["sharp"].append(float(lv(A[fi]) / lv(S[fi])))
q["decoded_lossless_outside_flame_support_px_changed"] = chg_outside
q["final_encode_vs_lossless_mean_abs_outside_support"] = round(float(np.mean(codec_out)), 3)
q["per_flame_output"] = {k: dict(dF_pct_mean=round(100 * np.mean(v["dF_poc"]), 2), dF_pct_p95=round(100 * np.percentile(v["dF_poc"], 95), 2), dF_pct_max=round(100 * np.max(v["dF_poc"]), 2),
                                 static_dF_pct_mean=round(100 * np.mean(v["dF_static"]), 2), static_dF_pct_max=round(100 * np.max(v["dF_static"]), 2),
                                 sharp_ratio_mean=round(float(np.mean(v["sharp"])), 3), sharp_ratio_min=round(float(np.min(v["sharp"])), 3)) for k, v in per.items()}
json.dump(q, open(f"qc/{tag}_output_qc.json", "w"), indent=1)
# strips (decoded FINAL encode = what the owner will see). Output crop around the forge flames, native pixels (1x).
X0, Y0, X1, Y1 = 400, 740, 690, 1140
def lab(im, s):
    im = np.ascontiguousarray(im); cv2.rectangle(im, (0, 0), (len(s) * 9 + 6, 18), (0, 0, 0), -1); cv2.putText(im, s, (3, 13), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA); return im
def strip(idx, crop=True, scale=1, cols=None, name=""):
    tiles = []
    for i in idx:
        im = Fz[i][Y0:Y1, X0:X1] if crop else cv2.resize(Fz[i], (360, 640), interpolation=cv2.INTER_AREA)
        if scale != 1: im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        tiles.append(lab(im.copy(), f"f{i} t={i / 30:.2f}s"))
    cols = cols or len(tiles); rows = [np.hstack(tiles[r:r + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r:r + cols]))) for r in range(0, len(tiles), cols)]
    cv2.imwrite(f"strips/{tag}_{name}.png", cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
strip([60, 68, 75, 83], name="flame4_0p25s_fullres")
strip([0, 36, 72, 108, 144, 179], crop=False, name="full_360x640")
strip(list(range(90, 120)), cols=10, name="flame30_consec_1s_fullres")
strip(list(range(40, 52)), cols=6, name="flame12_consec_fullres")
strip(list(range(0, 180, 15)), cols=6, name="flame_0p5s_fullres")
print(json.dumps(q, indent=1))
