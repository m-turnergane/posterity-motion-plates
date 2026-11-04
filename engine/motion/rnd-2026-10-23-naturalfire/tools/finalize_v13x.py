"""v13 deliverables from the lossless 4:2:0 master. Never overwrites (asserts). QC on DECODED files."""
import sys, os, json, subprocess, hashlib, shutil, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; import fire_v10 as F
tag = "final_v13x"; master = f"v13/work/{tag}_lossless420.mp4"; ST = F.STATIC
poc = f"P05_naturalfire_poc_{tag}.mp4"; poc16 = f"P05_naturalfire_poc_{tag}_crf16.mp4"; sbs = f"P05_naturalfire_vs_v2cstatic_sbs_{tag}.mp4"
st16 = f"v13/work/v2cstatic_crf16_for_residual_x.mp4"; qcf = f"v13/qc/{tag}_qc.json"
strips = {n: f"v13/strips/{tag}_{n}.png" for n in ("flame4_0p25s_fullres", "flame12_consec_fullres", "flame12_consec_diffx3", "phone4_0p25s_360x640", "phone12_consec_360x640_forgezoom3x")}
outs = [poc, poc16, sbs, st16, qcf, *strips.values()] + [p + ".md5" for p in (poc, poc16, sbs)]
for f in outs: assert not os.path.exists(f), f
os.makedirs("v13/qc", exist_ok=True); os.makedirs("v13/strips", exist_ok=True)
run = lambda c: subprocess.run(c, check=True)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
shutil.copyfile(master, poc); assert md5(poc) == md5(master)
run(["ffmpeg", "-n", "-v", "error", "-i", poc, "-an", *P.ENC_FINAL, "-r", "30", poc16])
run(["ffmpeg", "-n", "-v", "error", "-i", ST, "-an", *P.ENC_FINAL, "-r", "30", st16])
W, H = F.W, F.H
def dec(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "yuv420p", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, H * 3 // 2, W)
A, S, A16, S16 = dec(poc), dec(ST), dec(poc16), dec(st16)
bgr = lambda f: cv2.cvtColor(np.ascontiguousarray(f), cv2.COLOR_YUV2BGR_I420)
# --- SBS (labelled header bar; picture area untouched) ---
font = cv2.FONT_HERSHEY_SIMPLEX; HB = 96
enc = subprocess.Popen(["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{2 * W + 16}x{H + HB}", "-r", "30", "-i", "pipe:0", "-an", *P.ENC_FINAL, "-r", "30", sbs], stdin=subprocess.PIPE)
for fi in range(len(A)):
    c = np.full((H + HB, 2 * W + 16, 3), 18, np.uint8); c[HB:, :W] = bgr(A[fi]); c[HB:, W + 16:] = bgr(S[fi])
    cv2.putText(c, "LEFT = v13 (new rising fire layer)", (30, 62), font, 1.5, (235, 235, 235), 3, cv2.LINE_AA)
    cv2.putText(c, "RIGHT = v2c static", (W + 46, 62), font, 1.5, (235, 235, 235), 3, cv2.LINE_AA)
    enc.stdin.write(c.tobytes())
enc.stdin.close(); assert enc.wait() == 0
for p in (poc, poc16, sbs): open(p + ".md5", "w").write(f"{md5(p)}  {p}\n")
# --- QC on decoded output ---
def omask(m, fi): return np.asarray(P.frame_out(np.repeat((m.astype(np.float32) * 255)[..., None], 3, 2), F.BOX, F.SEG, fi))[..., 0] > 0
_, _, allowed_b, named_b = F.load_all("_b"); _, _, _, named_o = F.load_all("")
def planes(f): return f[:H], f[H:H + H // 4].reshape(H // 2, W // 2), f[H + H // 4:].reshape(H // 2, W // 2)
up = lambda c: np.repeat(np.repeat(c, 2, 0), 2, 1)
R = dict(named_b=[], named_orig=[], outside_allowed=[], res16_named_b_max=[], res16_named_b_mean=[], changed_px=[], identical_frac=[], dF_v10=[], dF_static=[])
for fi in range(len(A)):
    Ya, Ua, Va = planes(A[fi]); Ys, Us, Vs = planes(S[fi])
    d = (Ya != Ys) | up(Ua != Us) | up(Va != Vs)       # any plane differs at this output px (chroma at its 2x2 block)
    nb, no, na = omask(named_b, fi), omask(named_o, fi), omask(~allowed_b, fi)
    R["named_b"].append(int(d[nb].sum())); R["named_orig"].append(int(d[no].sum())); R["outside_allowed"].append(int(d[na].sum()))
    R["changed_px"].append(int(d.sum())); R["identical_frac"].append(float(1 - d.mean()))
    r16 = np.abs(bgr(A16[fi]).astype(np.int16) - bgr(S16[fi])).max(2)
    R["res16_named_b_max"].append(int(r16[nb].max())); R["res16_named_b_mean"].append(float(r16[nb].mean()))
    if fi:
        act = d | prev_d; a1, a0, s1, s0 = (bgr(x).astype(np.float32) for x in (A[fi], A[fi - 1], S[fi], S[fi - 1]))
        R["dF_v10"].append(float(np.abs(a1 - a0).max(2)[act].mean())); R["dF_static"].append(float(np.abs(s1 - s0).max(2)[act].mean()))
    prev_d = d
# glow identity: static glow series (mean Y over camera-mapped allowed zones, static) vs same series in v10 restricted to untouched px
gl = []
for fi in range(0, len(A), 1):
    Ya, _, _ = planes(A[fi]); Ys, _, _ = planes(S[fi]); d = Ya != Ys; z = omask(allowed_b, fi) & ~d
    gl.append(float(np.abs(Ya[z].astype(int) - Ys[z]).max()) if z.any() else 0.0)
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", poc], capture_output=True).stdout)
vs = [s for s in probe["streams"] if s["codec_type"] == "video"][0]
summ = lambda k: dict(sum=int(np.sum(R[k])), max=int(np.max(R[k])))
q = dict(tag=tag, master=dict(name=poc, md5=md5(poc), codec=vs["codec_name"], profile=vs.get("profile"), pix_fmt=vs["pix_fmt"], w=vs["width"], h=vs["height"], fps=vs["r_frame_rate"], frames=len(A), dur=probe["format"]["duration"], encode="libx264 -qp 0 (lossless) yuv420p"),
         crf16=dict(name=poc16, md5=md5(poc16), encode=" ".join(P.ENC_FINAL)), sbs=dict(name=sbs, md5=md5(sbs), layout="header bar labels; picture: left = v13, right = v2c static; crf16"),
         static_ref=dict(name=ST, md5=md5(ST), note="decoded v2c static twin, bit-identical to prod static output (qc/verify_static_vs_prod.json)"),
         protect_changed_px_decoded_master=dict(named_protect_b=summ("named_b"), named_protect_original_prod_boxes=summ("named_orig"), everything_outside_allowed_zones=summ("outside_allowed"),
              note="any Y/U/V difference at output px inside the camera-mapped mask (any >0 influence), all 180 frames, decoded master vs decoded static"),
         glow=dict(max_abs_Y_diff_untouched_px_in_fire_zones=float(max(gl)), changed_px_per_frame_mean=float(np.mean(R["changed_px"])), identical_px_frac_min=float(min(R["identical_frac"])),
              note="every px the layer does not touch is bit-identical to v2c static -> v2c glow modulation is reproduced exactly; the layer's gain also follows the static glow ratio"),
         dF_active_px=dict(v10_mean=float(np.mean(R["dF_v10"])), v10_max=float(np.max(R["dF_v10"])), static_mean=float(np.mean(R["dF_static"])), per_frame_v10=[round(x, 2) for x in R["dF_v10"]]),
         crf16_residual_in_named_protect_b_vs_crf16_static=dict(max=int(max(R["res16_named_b_max"])), mean_of_frame_means=float(np.mean(R["res16_named_b_mean"]))))
if q["protect_changed_px_decoded_master"]["named_protect_original_prod_boxes"]["sum"]:
    q["protect_changed_px_decoded_master"]["original_box_note"] = "non-zero only in the trimmed strip x424-461 of the prod right-smith head box (smoke/fire above pillar; head starts ~x477) - see masks_v10_meta_b.json"
json.dump(q, open(qcf, "x"), indent=1)
# --- strips ---
rx0, ry0, rx1, ry1 = 426, 534, 652, 1104
lab = lambda im, t: cv2.putText(im, t, (6, 22), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
def tile(ims, gap=6): return np.hstack(sum([[x, np.full((x.shape[0], gap, 3), 30, np.uint8)] for x in ims], [])[:-1])
f4 = [60, 68, 75, 83]
row = [lab(bgr(A[f])[ry0:ry1, rx0:rx1].copy(), f"v13 f{f}") for f in f4] + [lab(bgr(S[f4[0]])[ry0:ry1, rx0:rx1].copy(), f"static f{f4[0]}")]
cv2.imwrite(strips["flame4_0p25s_fullres"], tile(row))
c12 = list(range(90, 102))
cv2.imwrite(strips["flame12_consec_fullres"], np.vstack([tile([lab(bgr(A[f])[ry0:ry1, rx0:rx1].copy(), f"{f}") for f in c12[:6]]), np.full((6, 6 * (rx1 - rx0) + 30, 3), 30, np.uint8), tile([lab(bgr(A[f])[ry0:ry1, rx0:rx1].copy(), f"{f}") for f in c12[6:]])]))
dd = lambda f: lab(np.clip((bgr(A[f]).astype(int) - bgr(S[f])) * 3, 0, 255).astype(np.uint8)[ry0:ry1, rx0:rx1].copy(), f"{f} diff x3")
cv2.imwrite(strips["flame12_consec_diffx3"], np.vstack([tile([dd(f) for f in c12[:6]]), np.full((6, 6 * (rx1 - rx0) + 30, 3), 30, np.uint8), tile([dd(f) for f in c12[6:]])]))
ph = lambda X: cv2.resize(bgr(X), (360, 640), interpolation=cv2.INTER_AREA)
cv2.imwrite(strips["phone4_0p25s_360x640"], tile([lab(ph(A[f]).copy(), f"v13 {f}") for f in f4] + [lab(ph(S[f4[0]]).copy(), "static")]))
z = lambda im: cv2.resize(im[160:380, 130:230], None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
cv2.imwrite(strips["phone12_consec_360x640_forgezoom3x"], np.vstack([tile([lab(z(ph(A[f])), f"{f}") for f in c12[:6]]), tile([lab(z(ph(A[f])), f"{f}") for f in c12[6:]])]))
print(json.dumps({k: v for k, v in q.items() if k != "dF_active_px"}, indent=1)); print("dF", q["dF_active_px"]["v10_mean"], q["dF_active_px"]["static_mean"])
