"""water_v1_1: water_v1 (LOCKED 2026-10-30 4:53pm ET) + the shared crop/fire guardrails (motion/guardrails.py).

Rendering is delegated UNCHANGED to water_v1.py (imported by path, not copied), so every shot that passes the
guardrails renders bit-identically to water_v1 (verified on the locked shots 1 and 3, see README_v1_1.md).
Above 1.5x of native fill, or on soft / zoomed fire, the CLI REFUSES (default) or warns with --warn-only.

  water_v1_1.py render|proof|stats|overlay <cfg.json> <out> [...same options as water_v1...] [--warn-only]
  water_v1_1.py reel <reel.json> <out.mp4> [--warn-only]
  water_v1_1.py check <cfg.json|reel.json>          guardrail report only
"""
import sys, json, importlib.util
from pathlib import Path
import cv2
HERE = Path(__file__).resolve().parent
def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
W = _load("water_v1", HERE / "water_v1.py")
G = _load("guardrails", HERE.parent.parent / "motion" / "guardrails.py")

def guard(cfg, mode="refuse"):
    P = cv2.cvtColor(cv2.imread(cfg["plate"]), cv2.COLOR_BGR2RGB)
    w, h = W.out_size(cfg); return G.check_shot(cfg, P, mode=mode, out_wh=(w, h))

def guard_reel(reel_json, mode="refuse"):
    R = json.load(open(reel_json)); out = []
    for s in R["shots"]:
        cfg = W._cfg(HERE / s["config"]); cfg.update({k: v for k, v in s.items() if k != "config"})
        out.append(dict(shot=cfg["name"], checks=guard(cfg, mode)))
    return out

if __name__ == "__main__":
    a = sys.argv[1:]; mode = "warn" if "--warn-only" in a else "refuse"; a = [x for x in a if x != "--warn-only"]; cmd = a[0]
    if cmd == "check":
        R = json.load(open(a[1])); print(json.dumps(guard_reel(a[1], "warn") if "shots" in R else guard(W._cfg(a[1]), "warn"), indent=1)); sys.exit(0)
    if cmd == "reel": guard_reel(a[1], mode)
    else: guard(W._cfg(a[1]), mode)
    sys.argv = [str(HERE / "water_v1.py")] + a
    exec(compile(open(HERE / "water_v1.py").read().split('if __name__ == "__main__":', 1)[1].replace("\n    ", "\n"), "water_v1_main", "exec"), vars(W))
