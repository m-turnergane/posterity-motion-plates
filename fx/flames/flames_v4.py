"""flames_v4 — every fire gets the LOCKED torch_v1c treatment (Edward II fx_v1c.py, imported by path, NOT edited).

What v4 does per fire: the painted flame shape holds (no tongue, no warp, no displacement); the flame pixels, a soft
gaussian halo and the grouped local light-spill pulse with the v1c flicker clock at v1c strength; v1c embers where the
Edward spec has them.  Everything is per-pixel light (multiplicative gain / additive glow) — no resampling anywhere.

Runtime-only adjustments (module objects, not the file):
  * candle flame_warp removed (s.pop('warp')) and candles rendered with the torch branch (no scrolling teardrop/tongue)
  * B13 foreground parallax off (it is an affine displacement of the soldier layer)
  * haze / mist / motes KEPT as shipped (screen-blend light, no resampling); without them the B13 dark walls swing
    ~10-15 points harder than the Edward master, so keeping them is what matches v1c strength ('atmos': false drops them)
  * P05 (no Edward spec) gets a spec built from the flames_v2b town keying: every keyed fire = a v1c 'torch' source,
    spill relight mask = the P05 protects (sky, sea, ships, glitter) and a feathered keep-out so protects stay 0 px.
  * PULSE['p05'] is set from the v4 config (calibrated so P05 swing sits inside the measured v1c B13/B10 range).
No smoke, no sky billow in v4 (see README_v4.md for the reasoning)."""
import importlib.util, json, math, sys, subprocess
from pathlib import Path
import numpy as np, cv2
HERE = Path(__file__).resolve().parent
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
FX_PATH = "/workspace/posterity/standalones/edward-ii/edit/fx_v1c.py"
FX = _load("fx_v1c", FX_PATH)
F3 = _load("flames_v3", HERE / "flames_v3.py")      # helpers only: load_plate, poly_mask, keepout_fade, push_frame, ffmpeg_writer, FlameScene (keying)


class V1CShot:
    def __init__(self, shot):
        self.shot = shot; plate = shot["plate"]; key = FX.plate_key(plate)
        self.keep = None
        if shot.get("p05_from_flames_cfg"):
            cfg = json.load(open(HERE / shot["p05_from_flames_cfg"])); P = F3.load_plate(plate)
            fl = F3.FlameScene(P, cfg, sparks=False, spill=False)
            rects = [tuple(int(v) for v in c.bb) for c in fl.comps]
            FX.SPECS[key] = dict(torch=rects, relight_poly=cfg["protect"], spill_amp=shot.get("spill_amp", 1.8))
            prot = F3.poly_mask(P.shape[:2], cfg["protect"]) > 0
            self.protect_bin = prot
            self.keep = F3.keepout_fade(prot.astype(np.uint8), float(cfg.get("protect_feather", 24)))[..., None]
            self.guards = cfg.get("guards", {})
        if "pulse" in shot: FX.PULSE[key] = float(shot["pulse"])
        fx = FX.PlateFX(plate, seed=int(shot["seed"]))
        for s in fx.srcs:
            s.pop("warp", None)
            if s["kind"] == "candle": s["kind"] = "torch"
        fx.par = None; fx.smoke = []
        if not shot.get("atmos", True): fx.layers = []; fx.motes = []   # v1c haze/mist/motes are screen-blend light, kept as shipped by default
        if not shot.get("embers", True): fx.embers = []
        self.fx = fx; self.P = fx.P; self.t0 = float(shot.get("t0", 6.0))
    def frame(self, t, want_disp=False):
        o, d = self.fx.render(self.t0 + t, 0.0, want_disp=True)
        if self.keep is not None:
            o = np.clip(self.P + (o.astype(np.float32) - self.P) * self.keep + 0.5, 0, 255).astype(np.uint8)
            o[self.protect_bin] = self.P[self.protect_bin]
        return (o, d) if want_disp else o
    def summary(self):
        s = self.fx.info(); s.update(warped=sum(1 for q in self.fx.srcs if "warp" in q), parallax=self.fx.par is not None,
                                        haze_layers=len(self.fx.layers), pulse=FX.PULSE.get(self.fx.key, 1.0)); return s


def render_reel(reel_path, out_path, fps=30, size=(1080, 1920)):
    reel = json.load(open(reel_path)); w, h = size
    p = F3.ffmpeg_writer(out_path, w, h, fps, crf=int(reel.get("crf", 22)))
    for shot in reel["shots"]:
        sc = V1CShot(shot); n = int(round(shot["seconds"] * fps)); z0, z1 = shot.get("push", (1.0, 1.06)); c = tuple(shot.get("push_center", (0.5, 0.5)))
        print("shot", shot["name"], shot["seconds"], json.dumps(sc.summary()), file=sys.stderr, flush=True)
        for i in range(n):
            f, d = sc.frame(i / fps, want_disp=True); assert d["warp_max_px"] == 0.0
            p.stdin.write(F3.push_frame(f, i / max(n - 1, 1), w, h, z0, z1, center=c).tobytes())
    p.stdin.close(); assert p.wait() == 0


if __name__ == "__main__":
    out = Path(sys.argv[2]); assert not out.exists(), "never overwrite"
    render_reel(sys.argv[1], out)
