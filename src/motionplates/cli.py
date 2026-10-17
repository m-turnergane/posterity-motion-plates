import argparse, os, sys, json
from .core import engine
from .core import compare as cmp

def main(argv=None):
    ap = argparse.ArgumentParser(prog="motionplates"); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="render a recipe"); r.add_argument("recipe"); r.add_argument("--out", default="out"); r.add_argument("--plates", default=None, help="plates dir (default $MOTIONPLATES_PLATES)")
    r.add_argument("--seconds", type=float); r.add_argument("--frames", type=int); r.add_argument("--keep-lossless", action="store_true"); r.add_argument("--export-layers", default=None, help="dir for layer-stack PNGs")
    r.add_argument("--compare", action="store_true", help="also build side-by-side (static | animated) mp4 + labelled stills"); r.add_argument("--at", default=None, help="comma-separated seconds: render only these frames as stills (fast iteration)"); r.add_argument("--crf", type=int, default=14)
    a = ap.parse_args(argv)
    if a.cmd == "render":
        m = engine.render(a.recipe, a.out, a.plates, a.seconds, a.frames, a.keep_lossless, a.export_layers, a.crf, log=print, only_times=[float(x) for x in a.at.split(',')] if a.at else None)
        if m is None: return
        if a.compare: cmp.make_compare(m, a.out)
        if not a.keep_lossless:
            p = os.path.join(a.out, f"{m['name']}_lossless.mp4")
            if os.path.exists(p): os.remove(p)
        print(json.dumps({k: m[k] for k in ("name", "render_fps", "frame0", "motion", "mp4")}, indent=1))
