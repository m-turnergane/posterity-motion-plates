"""Plate-space iteration: render the forge crop for N frames through the locked engine with the animated plate, write strips + stats."""
import sys, json, time, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from flame import FlameSet; from specs import load_masks; from firestats import stats
from PIL import Image, ImageDraw, ImageFont
tag = sys.argv[1]; spec = json.load(open(sys.argv[2])); N = int(sys.argv[3]) if len(sys.argv) > 3 else 180
out = f"iter/{tag}"; import os; os.makedirs(out, exist_ok=True)
M = P.load_engine(); E = M.Engine(P.load_cfg()); masks = load_masks(); FS = FlameSet(E, masks, spec["flames"])
CX0, CY0, CX1, CY1 = 368, 672, 572, 962
frames = []; stat = []; t0 = time.time(); base = []
for fi in range(N):
    t = fi / 30; img = (E.render(t)[0] if spec.get('static') else FS.render(t)); frames.append(np.clip(np.rint(img[CY0:CY1, CX0:CX1]), 0, 255).astype(np.uint8))
    if not spec.get('static'): stat.append([round(f.last["A"], 3) for f in FS.fl] + [round(f.last["dmax"], 2) for f in FS.fl])
    if fi < 3 or fi % 60 == 0:
        b, _, _ = E.render(t); base.append(np.clip(np.rint(b[CY0:CY1, CX0:CX1]), 0, 255).astype(np.uint8))
print("render s/frame", round((time.time() - t0) / N, 3))
F = np.stack(frames); np.save(f"{out}/crop_frames.npy", F)
fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
def strip(idx, box, sc, cols, name):
    x0, y0, x1, y1 = box; w, h = (x1 - x0) * sc, (y1 - y0) * sc; rows = -(-len(idx) // cols)
    S = Image.new("RGB", (cols * (w + 4), rows * (h + 20)), (20, 20, 20)); d = ImageDraw.Draw(S)
    for k, i in enumerate(idx):
        im = Image.fromarray(F[i][y0:y1, x0:x1]).resize((w, h), Image.LANCZOS); X = (k % cols) * (w + 4); Y = (k // cols) * (h + 20)
        S.paste(im, (X, Y + 18)); d.text((X + 3, Y + 1), f"f{i} t={i/30:.2f}", fill=(255, 255, 255), font=fnt)
    S.save(f"{out}/{name}.png")
# crop-local boxes per flame (crop coords)
B0 = (383 - CX0 - 8, 680 - CY0 - 6, 423 - CX0 + 8, 757 - CY0 + 2); B1 = (431 - CX0 - 6, 788 - CY0 - 4, 488 - CX0 + 6, 862 - CY0 + 2); B2 = (500 - CX0 - 6, 873 - CY0 - 4, 557 - CX0 + 6, 952 - CY0 + 2)
st0 = 40
strip(list(range(st0, st0 + 12)), B0, 5, 6, "strip12_c0"); strip(list(range(st0, st0 + 12)), B1, 4, 6, "strip12_c1"); strip(list(range(st0, st0 + 12)), B2, 4, 6, "strip12_c2")
strip(list(range(0, N, 15))[:12], (0, 0, CX1 - CX0, CY1 - CY0), 2, 6, "strip_0p5s_forge")
# 360x640 view frames need the camera: approximate with plate->out scale (full frame at 360x640 done in final render); here: forge at output scale
strip(list(range(st0, st0 + 12, 1)), (0, 0, CX1 - CX0, CY1 - CY0), 1, 12, "strip12_forge_1x")
# stats per flame
res = {}
for i, (bx, mk) in enumerate(zip((B0, B1, B2), masks)):
    reg = mk[CY0:CY1, CX0:CX1] > 0.3; x0, y0, x1, y1 = bx
    fr = [f[y0:y1, x0:x1] for f in F]; rg = reg[y0:y1, x0:x1]
    st = stats(fr, 30.0, region=rg, thr=0.5, label=f"{tag}_c{i}")
    # per-frame change inside flame mask (fraction of mean level)
    L = F[:, y0:y1, x0:x1].astype(np.float32).mean(3); d = np.abs(np.diff(L, axis=0))[:, rg].mean(1) / L[:, rg].mean()
    st["perframe_change_mean_pct"] = round(100 * float(d.mean()), 2); st["perframe_change_max_pct"] = round(100 * float(d.max()), 2)
    res[f"c{i}"] = st
res["activity_disp_series_sample"] = stat[::15]
json.dump(res, open(f"{out}/stats.json", "w"), indent=1)
for k in ("c0", "c1", "c2"):
    s = res[k]; print(k, "H", s["flame_height_px"], "V/L", s["vert_lat_ratio"], "up", s["upward_fraction"], "sway", s["global_sway_index"], "rise", s["rise_speed_heights_per_s"], "prise", s["pattern_rise_heights_per_s"],
          "tipC", s["tip_spectrum"]["centroid_hz"], "tip0.3-.6", s["tip_spectrum"]["0.3-0.6"], "tip2-5", s["tip_spectrum"]["2-5"], "tipcv", s["tip_spectrum"]["cv"], "bodycv", s["body_spectrum"]["cv"], "wisp", s["wisp_births_per_s"], s["wisps_visible_mean"], "dF%", s["perframe_change_mean_pct"], s["perframe_change_max_pct"])
print("dmax", max(max(r[3:]) for r in stat) if stat else 0)
# kymographs: luminance along vertical lines through each flame vs time (upward travel = streaks rising to the right)
ky = []
for (bx, cxs) in ((B0, (406, 412)), (B1, (448, 470)), (B2, (515, 525))):
    x0, y0, x1, y1 = bx
    for cx in cxs:
        col = F[:, y0:y1, cx - CX0].astype(np.float32)          # N x h x 3
        im = np.transpose(col, (1, 0, 2)); im = cv2.resize(im, (N * 3, (y1 - y0) * 3), interpolation=cv2.INTER_NEAREST)
        ky.append(np.pad(im, ((0, 6), (0, 0), (0, 0))))
W_ = max(k.shape[1] for k in ky); ky = [np.pad(k, ((0, 0), (0, W_ - k.shape[1]), (0, 0))) for k in ky]
cv2.imwrite(f"{out}/kymo.png", cv2.cvtColor(np.clip(np.concatenate(ky, 0), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
