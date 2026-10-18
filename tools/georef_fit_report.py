"""Fit candidate projection+warp models to a control-point file; report residuals, leave-one-out error and pin deviation (painted map vs real geography).
usage: georef_fit_report.py CONTROL_POINTS.json OUT_DIR   -> OUT_DIR/georef_<model>.json for each model + fit_report.json"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from motionplates.cartography import georef as G

def run(cpfile, out):
    d = json.load(open(cpfile)); os.makedirs(out, exist_ok=True); size = d["size"]
    pts = d["points"]; lm = [dict(p) for p in pts if p["type"] == "landmark"]; pins = [dict(p) for p in pts if p["type"] == "pin"]
    base = d["projection"]; models = []
    for pk in ("equirect", "mercator", "lcc"):
        pr = dict(base, kind=pk)
        if pk == "lcc": pr.update(p1=30.0, p2=55.0)
        for w in ("affine", "poly2", "tps"):
            models.append((pk, w, pr))
    rep = []
    for pk, w, pr in models:
        try: g = G.fit(lm, size, pr, w, smooth=0.0 if w != "tps" else 50.0)
        except ValueError as e: continue
        res = G.residuals(g, lm); lo = G.loo(lm, size, pr, w, 0.0 if w != "tps" else 50.0)
        pe = [float(np.linalg.norm(g.to_px([p["lon"], p["lat"]]) - np.array(p["px"], float))) for p in pins]
        # pin deviation in km using the local scale of the fit
        pkm = []
        for p, e in zip(pins, pe):
            sx, sy = G.px_per_km(g, (p["lon"], p["lat"])); pkm.append(e / (0.5 * (sx + sy)))
        row = dict(projection=pk, warp=w, n_landmarks=len(lm), rms_px=float(np.sqrt((res ** 2).mean())), max_px=float(res.max()), loo_rms_px=float(np.sqrt(np.nanmean(np.array(lo) ** 2))), loo_max_px=float(np.nanmax(lo)),
                   pins={p["id"]: dict(err_px=round(e, 1), err_km=round(k)) for p, e, k in zip(pins, pe, pkm)}, pin_rms_px=float(np.sqrt(np.mean(np.square(pe)))), pin_rms_km=float(np.sqrt(np.mean(np.square(pkm)))),
                   landmark_residuals_px={p["id"]: round(float(r), 1) for p, r in zip(lm, res)})
        rep.append(row)
        gd = dict(size=size, proj=pr, warp=w, smooth=0.0 if w != "tps" else 50.0, control_points=lm + pins if False else lm); json.dump(gd, open(os.path.join(out, f"georef_{pk}_{w}.json"), "w"), indent=1)
    json.dump(rep, open(os.path.join(out, "fit_report.json"), "w"), indent=1)
    for r in sorted(rep, key=lambda r: r["loo_rms_px"]): print(f"{r['projection']:9s} {r['warp']:7s} fit_rms={r['rms_px']:6.1f}px loo_rms={r['loo_rms_px']:6.1f}px pins_rms={r['pin_rms_px']:6.1f}px (~{r['pin_rms_km']:.0f} km)")
    return rep
if __name__ == "__main__": run(sys.argv[1], sys.argv[2])
