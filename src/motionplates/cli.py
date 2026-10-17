import argparse, os, sys, json
from .core import engine, compare as cmp
from .core.validate import RecipeError, PlatesRootError, resolve_plates_root, validate_recipe
from .core.encode import EncodeError
from .core.recipe import load_recipe

EXIT = dict(ok=0, rejected=2, invalid=3, encode=4, usage=64)

def main(argv=None):
    ap = argparse.ArgumentParser(prog="motionplates"); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="render a recipe"); r.add_argument("recipe"); r.add_argument("--out", default="out"); r.add_argument("--plates", default=None, help="plates dir (or $MOTIONPLATES_PLATES); no default")
    r.add_argument("--seconds", type=float); r.add_argument("--frames", type=int); r.add_argument("--export-layers", default=None, help="dir for layer-stack PNGs")
    r.add_argument("--compare", action="store_true", help="also build side-by-side (static | animated) mp4 + labelled stills"); r.add_argument("--at", default=None, help="comma-separated seconds: render only these frames as stills (no video written)")
    r.add_argument("--proxy", type=float, default=None, help="fast low-res preview scale (e.g. 0.25 = 270x480); never for delivery"); r.add_argument("--crf", type=int, default=14); r.add_argument("--profile", default="direct", choices=["direct"]); r.add_argument("--threads", type=int, default=0)
    v = sub.add_parser("validate", help="validate a recipe (structure, polygons, references, assets) without rendering"); v.add_argument("recipe"); v.add_argument("--plates", default=None); v.add_argument("--no-assets", action="store_true")
    g = sub.add_parser("suggest", help="propose mask/layer candidates for review (writes overlay PNG + YAML snippet)"); g.add_argument("recipe_or_plate"); g.add_argument("--plates", default=None)
    g.add_argument("--method", default="regions", choices=["regions", "saliency", "box"]); g.add_argument("-n", type=int, default=10); g.add_argument("--box", default=None, help="x0,y0,x1,y1 for method=box"); g.add_argument("--out", default="suggestions")
    nw = sub.add_parser("new", help="create a recipe from a template"); nw.add_argument("--template", required=True); nw.add_argument("--plate", required=True); nw.add_argument("--name", required=True); nw.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "new":
            tdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "recipes", "templates"); tp = os.path.join(tdir, a.template + ".yaml")
            if not os.path.isfile(tp): print("unknown template; available:", sorted(f[:-5] for f in os.listdir(tdir)), file=sys.stderr); return EXIT["usage"]
            txt = open(tp).read().replace("__NAME__", a.name).replace("__PLATE__", a.plate); out = a.out or f"recipes/{a.name}.yaml"; open(out, "w").write(txt); print("wrote", out); return 0
        if a.cmd == "suggest":
            from .authoring import suggest as S
            from .core import plate as P
            import yaml as _y
            root = resolve_plates_root(a.plates); fn = a.recipe_or_plate
            if fn.endswith((".yaml", ".yml")): fn = _y.safe_load(open(fn))["plate"]["file"]
            img, _ = P.load_cover(os.path.join(root, fn)); os.makedirs(a.out, exist_ok=True)
            kw = dict(box=[int(v) for v in a.box.split(",")]) if a.box else {}
            c = S.candidates(img, a.method, a.n, **kw); S.overlay(img, c, os.path.join(a.out, f"suggest_{a.method}.png")); open(os.path.join(a.out, f"suggest_{a.method}.yaml"), "w").write(S.to_yaml_snippet(c))
            print(f"{len(c)} candidates -> {a.out}"); return 0
        if a.cmd == "validate":
            R = load_recipe(a.recipe); root = None if a.no_assets else resolve_plates_root(a.plates)
            probs = validate_recipe(R, root, check_assets=not a.no_assets)
            print("OK" if not probs else "INVALID:\n  - " + "\n  - ".join(probs)); return 0 if not probs else EXIT["invalid"]
        m = engine.render(a.recipe, a.out, a.plates, a.seconds, a.frames, False, a.export_layers, a.crf, log=print, only_times=[float(x) for x in a.at.split(",")] if a.at else None, profile=a.profile, threads=a.threads, proxy=a.proxy)
        if m is None: return 0
        if a.compare: cmp.make_compare(m, a.out)
        print(json.dumps({"name": m["name"], "status": m["qc"]["status"], "reason": m["qc"]["reason"], "render_fps": m["render_fps"], "frame0": {k: m["frame0"][k] for k in ("max_abs_diff_vs_plate", "mean_abs_diff_vs_plate")}, "motion": m["motion"], "frames_sha1": m["frames_sha1"], "mp4": m["mp4"]}, indent=1))
        return 0
    except PlatesRootError as e: print("ERROR (plates root):", e, file=sys.stderr); return EXIT["invalid"]
    except RecipeError as e: print("ERROR (recipe):", e, file=sys.stderr); return EXIT["invalid"]
    except EncodeError as e: print("ERROR (encode/verify):", e, file=sys.stderr); return EXIT["encode"]
    except engine.RenderRejected as e: print("REJECTED:", e, file=sys.stderr); return EXIT["rejected"]

if __name__ == "__main__": sys.exit(main())
