"""v09 plate-space iteration (new R&D masks with extension zones). Usage: iterate_v09.py tag spec.json [N]
Writes iter/<tag>/ (never overwrites an existing tag dir): crop_frames.npy, strips, stats.json."""
import sys, os, json, time, numpy as np, cv2
sys.path.insert(0, 'tools'); import prod as P; from flame_v09 import FlameSetX, load_masks_v09; from specs import load_masks
from firestats import stats; from hprise import hp_metrics
tag = sys.argv[1]; spec = json.load(open(sys.argv[2])); N = int(sys.argv[3]) if len(sys.argv) > 3 else 180
out = f"iter/{tag}"; os.makedirs(out, exist_ok=False)
CX0, CY0, CX1, CY1 = 366, 540, 574, 962
if spec.get("model") == "tongue": from flame_v09t import FlameSetX
M = P.load_engine(); E = M.Engine(P.load_cfg()); cores, exts = load_masks_v09(); FS = FlameSetX(E, cores, exts, spec["flames"])
st_path = "iter/v09_static/crop_frames.npy"
if not os.path.exists(st_path):
    os.makedirs("iter/v09_static", exist_ok=True); S = []
    for fi in range(180): S.append(np.clip(np.rint(E.render(fi / 30)[0][CY0:CY1, CX0:CX1]), 0, 255).astype(np.uint8))
    np.save(st_path, np.stack(S))
S = np.load(st_path)[:N]
frames, stat = [], []; t0 = time.time()
for fi in range(N):
    img = FS.render(fi / 30); frames.append(np.clip(np.rint(img[CY0:CY1, CX0:CX1]), 0, 255).astype(np.uint8))
    stat.append([round(f.last["A"], 3) for f in FS.fl] + [round(f.last["dmax"], 2) for f in FS.fl] + [round(f.last["ext_w"], 2) for f in FS.fl])
print("render s/frame", round((time.time() - t0) / N, 3)); F = np.stack(frames); np.save(f"{out}/crop_frames.npy", F)
def lab(im, s):
    im = np.ascontiguousarray(im); cv2.rectangle(im, (0, 0), (len(s) * 7 + 4, 13), (0, 0, 0), -1); cv2.putText(im, s, (2, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255), 1, cv2.LINE_AA); return im
def strip(X, idx, sc, cols, name, box=None, interp=cv2.INTER_LANCZOS4, label=True):
    tiles = []
    for i in idx:
        im = X[i] if box is None else X[i][box[1]:box[3], box[0]:box[2]]
        im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=interp); tiles.append(lab(im.copy(), f"f{i}") if label else im)
    rows = [np.hstack(tiles[r:r + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[r:r + cols]))) for r in range(0, len(tiles), cols)]
    cv2.imwrite(f"{out}/{name}.png", cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
strip(F, list(range(0, N, 15))[:12], 1, 12, "strip_0p5s_forge")
strip(F, list(range(40, 52)), 2, 6, "strip12_forge_2x", box=(20, 30, 200, 410))
ph = 0.383   # plate px -> 360x640 phone px (cover scale ~1.148 x 1/3)
strip(F, list(range(40, 48)), ph, 8, "phone8_native", interp=cv2.INTER_AREA, label=False)
ph8 = [cv2.resize(cv2.resize(F[i], None, fx=ph, fy=ph, interpolation=cv2.INTER_AREA), None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) for i in range(40, 48)]
cv2.imwrite(f"{out}/phone8_x3.png", cv2.cvtColor(np.hstack(ph8), cv2.COLOR_RGB2BGR))
# per-flame stats on: core (new), prod (v2b2, comparable with v08), ext
prodm = load_masks(); res = {}
Lp, Ls = F.astype(np.float32).mean(3), S.astype(np.float32).mean(3)
for i in range(3):
    r = {}
    for nm, mk, thr in (("core", cores[i], 0.5), ("prod", prodm[i], 0.5), ("ext", exts[i], 0.3)):
        reg = mk[CY0:CY1, CX0:CX1] > thr
        if reg.sum() < 20: continue
        d = np.abs(np.diff(Lp, axis=0))[:, reg].mean(1) / Lp[1:, reg].mean(1); ds = np.abs(np.diff(Ls, axis=0))[:, reg].mean(1) / Ls[1:, reg].mean(1)
        ys = np.nonzero(reg.any(1))[0]; Hf = float(ys.max() - ys.min() + 1)
        e = dict(dF_mean=round(100 * float(d.mean()), 2), dF_p95=round(100 * float(np.percentile(d, 95)), 2), dF_max=round(100 * float(d.max()), 2), static_dF_mean=round(100 * float(ds.mean()), 2), static_dF_max=round(100 * float(ds.max()), 2))
        if nm != "ext":
            e["hp"] = hp_metrics(list(F), 30.0, reg, Hf if nm == "core" else (64, 62, 60)[i]); e["hp_static"] = hp_metrics(list(S), 30.0, reg, Hf if nm == "core" else (64, 62, 60)[i])["hp_energy"]
            lap = lambda X: np.array([cv2.Laplacian(x, cv2.CV_32F)[reg].var() for x in X]); sh = lap(Lp) / lap(Ls); e["sharp_mean"] = round(float(sh.mean()), 3); e["sharp_min"] = round(float(sh.min()), 3)
        else:
            ch = (np.abs(Lp - Ls)[:, reg] > 8).mean(1); e["ext_px_lit_frac_mean"] = round(float(ch.mean()), 3); e["ext_px_lit_frac_max"] = round(float(ch.max()), 3)
            e["ext_frames_with_wisp_frac"] = round(float((ch > 0.03).mean()), 3)
        r[nm] = e
    ys, xs = np.nonzero(cores[i][CY0:CY1, CX0:CX1] > 0.3); bx = (max(0, xs.min() - 4), max(0, ys.min() - 25), xs.max() + 5, ys.max() + 3)
    reg = (cores[i] > 0.3)[CY0:CY1, CX0:CX1][bx[1]:bx[3], bx[0]:bx[2]]
    fs = stats([f[bx[1]:bx[3], bx[0]:bx[2]] for f in F], 30.0, region=reg, thr=0.5, label=f"{tag}_c{i}")
    r["flow"] = {k: fs[k] for k in ("vert_lat_ratio", "upward_fraction", "global_sway_index", "rise_speed_heights_per_s", "pattern_rise_heights_per_s", "wisp_births_per_s") if k in fs}
    r["flow"]["rotation"] = fs.get("rotation_shear_std"); res[f"c{i}"] = r
    c, p_ = r["core"], r["prod"]
    print(f"c{i} core dF {c['dF_mean']}/{c['dF_p95']}/{c['dF_max']} (st {c['static_dF_mean']}/{c['static_dF_max']}) hpE {c['hp']['hp_energy']} (st {c['hp_static']}) rise {c['hp']['hp_rise_hps']} vl {c['hp']['hp_vl']} corr {c['hp']['corr_0p5to3s_max']} sharp {c['sharp_mean']}/{c['sharp_min']}"
          f" | prod dF {p_['dF_mean']}/{p_['dF_max']} hpE {p_['hp']['hp_energy']} rise {p_['hp']['hp_rise_hps']} | ext {r.get('ext', {})} | flow {r['flow']}")
res["series"] = stat[::10]; json.dump(res, open(f"{out}/stats.json", "w"), indent=1)
php = [cv2.resize(cv2.resize(F[i], None, fx=ph, fy=ph, interpolation=cv2.INTER_AREA), None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST) for i in range(30, 78, 6)]
cv2.imwrite(f"{out}/phone_0p2s_x3.png", cv2.cvtColor(np.hstack(php), cv2.COLOR_RGB2BGR))
dm = np.abs(Lp - Ls).max(0); dmp = cv2.resize(dm, None, fx=ph, fy=ph, interpolation=cv2.INTER_AREA)
cv2.imwrite(f"{out}/phone_maxdiff_vs_static_x3.png", cv2.resize(np.clip(dmp * 4, 0, 255).astype(np.uint8), None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))
