"""Jianwen v2c -- FINAL candidate fx (owner 13:30). Layered on fx_jianwen_v2b.py (Rough v1, NOT edited) exactly like v2b sits on fx_jianwen_v2.py.
Only two changes vs Rough v1:
 (2) TITLE_TOP_PCT 10.0 -> 7.5 (the K02 hat crown/ornament clears the strike band + letters in every S01/S02A/S02B frame; qc/v2-final-cand-v1/titlegap_*).
     The k01 smoke title-protect band (computed inside v2b at import) is left EXACTLY as in Rough v1 -> the smoke layer is unchanged.
 (3) K01-K11 candle + lantern flames get the K12-K19 flame-shape motion = the locked flame_warp (LWARP sway_px 3.0, sway_hz 0.8/2.1, stretch 0.45, zone_px 6,
     same formula, displacement only inside the flame mask dilated by the zone). Torches / braziers / K08 roof fire / palace + city fires stay static.
       k02 (1 candle), k03 (13 auto candles), k09 (1 candle): warp_candles=True (the warp dicts were always built from the plate rng; v2b just dropped
           them -> turning them on changes no rng stream, so glow / spill / atmos / motes / embers are bit-identical).
       k10: the hall candles (torch-kind sources in Rough v1: glow/spill/flicker unchanged) get the same warp from a SEPARATE rng (seed 7710) and driven by
           each source's own flicker; rects whose warp zone would touch a FACES/LAND rect are skipped (1: the throne-side glow inside the Yongle box),
           as are sources with h < 5 or w < 8 px (candlestick glints, not flames).
       k11: the monk's lantern keeps its Rough v1 glow/spill; its small inner flame (plate ~(236,1040)) gets a WARP-ONLY twin (kind 'offscreen' -> no
           extra halo/teardrop/spill) driven by the lantern's own flicker. NO pendulum sway (it would move the lantern body inside the K11 monk box).
K06 gate-arch lamps stay excluded (push target kept still, as in Rough v1).
"""
import numpy as np, cv2
import fx_jianwen_v2b as B
from fx_jianwen_v2b import *          # noqa: F401,F403  (FRAMING, GRADE, SMOKE, FACES, LAND, PULSE, grade, smoke_config, ...)
V2 = B.V2
TITLE_TOP_PCT = 7.5                    # owner 13:30: nudged up from 10.0 (Rough v1) -- see module doc
WARP_SEED = 7710
SPECS_ROUGH_V1 = B.SPECS            # the Rough v1 dict object (kept for the confinement proof)
SPECS = dict(B.SPECS)
for k in ("k02", "k03", "k09"): SPECS[k] = dict(B.SPECS[k], warp_candles=True)
SPECS["k10"] = dict(B.SPECS["k10"], warp_torch_rects=True)
SPECS["k11"] = dict(B.SPECS["k11"], warp_inner=[dict(rect=(231, 1033, 246, 1050), thr=188.0, drive_rect=B.K11_LANTERN[0])])
V2.SPECS = SPECS                       # rebind (fx_jianwen_v2.py + v2b untouched)
B.SPECS = SPECS

def _guard(key, H, W):
    g = np.zeros((H, W), np.uint8)
    for r in B.FACES.get(key, []) + B.LAND.get(key, []): g[r[1]:r[3], r[0]:r[2]] = 1
    return g

def _add_warp(fx, s, rng):
    hn = s["h"] / 26.0; LW = V2.LWARP
    s["warp"] = dict(sway=float(np.clip(LW["sway_px"] * hn, 0.5, LW["sway_px"])), height=s["h"] * 1.4,
                     zone=int(np.clip(round(LW["zone_px"] * hn), 2, LW["zone_px"])), fr=rng.uniform(0, 6.28, 2), nz=rng.standard_normal(4096))
    fx._prep_warp(s)

def _zone_hits_guard(s, g):
    X0, Y0, X1, Y1 = s["warp"]["roi"]; return bool((g[Y0:Y1, X0:X1] * (s["warp"]["zone_m"] > 0)).any())

class PlateFX(B.PlateFX):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        sp = V2.SPECS.get(self.key, {}); self.warp_log = []
        if not (sp.get("warp_torch_rects") or sp.get("warp_inner")): return
        rng = np.random.default_rng(WARP_SEED + sum(map(ord, self.key)))   # separate stream: the Rough v1 rng draws are untouched
        g = _guard(self.key, self.H, self.W)
        if sp.get("warp_torch_rects"):
            for s in [s for s in self.srcs if s["kind"] == "torch"]:
                x0, y0, x1, y1 = s["bb"]
                if s["h"] < 5 or (x1 - x0) < 8: self.warp_log.append((s["bb"], "skip: hairline/small")); rng.uniform(0, 1, 4098); continue
                _add_warp(self, s, rng)
                if _zone_hits_guard(s, g): s.pop("warp"); self.warp_log.append((s["bb"], "skip: zone touches FACES/LAND")); continue
                self.warp_log.append((s["bb"], "warp"))
        for q in sp.get("warp_inner", []):
            x0, y0, x1, y1 = q["rect"]; L = self.P[y0:y1, x0:x1].astype(np.float32).mean(2); keep = L >= q["thr"]
            m = cv2.GaussianBlur(cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.0)
            ys, xs = np.nonzero(keep)
            drv = [s for s in self.srcs if s.get("bb") == tuple(q["drive_rect"])][0]
            s = dict(kind="offscreen", bb=(x0, y0, x1, y1), mask=m, x=x0 + float(xs.mean()), base=float(y0 + ys.max() + 1), h=float(ys.max() - ys.min() + 1),
                     w=float(xs.max() - xs.min() + 1), F=drv["F"], radius=0.0, weight=0.0, warp_only=True)
            _add_warp(self, s, rng); s["mask"] = None    # mask only for the warp zone; no flame-mod / halo / spill for the twin
            self.srcs.append(s); self.warp_log.append((s["bb"], f"warp-only inner flame h={s['h']:.0f} zone={s['warp']['zone']} sway={s['warp']['sway']:.2f}px"))
    def info(self):
        d = super().info(); d["warp_log"] = self.warp_log; return d
