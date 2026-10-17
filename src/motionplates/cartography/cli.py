"""python -m motionplates.cartography render RECIPE --out DIR [--assets ROOT] [--vo-dir DIR] [--wav WAV] [--at T ...] [--proxy S]
exit codes: 0 ok, 3 invalid recipe / missing asset, 4 encode"""
import argparse, os, sys, json, time, hashlib, subprocess, yaml
import numpy as np, cv2
from .engine import Recipe, Renderer, RecipeError
from ..core.encode import FFmpegWriter, EncodeError, verify_video

def main(argv=None):
    ap = argparse.ArgumentParser(prog="motionplates.cartography"); sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render"); r.add_argument("recipe"); r.add_argument("--out", required=True); r.add_argument("--assets", default=os.environ.get("MOTIONPLATES_ASSETS", "."))
    r.add_argument("--vo-dir", default=os.environ.get("MOTIONPLATES_VO_DIR")); r.add_argument("--wav"); r.add_argument("--at", type=float, nargs="*"); r.add_argument("--seconds", type=float); r.add_argument("--proxy", type=float)
    r.add_argument("--crf", type=int, default=14)
    a = ap.parse_args(argv)
    try:
        R = yaml.safe_load(open(a.recipe)); name = R.get("name", "carto")
        if a.proxy: s = a.proxy; R["output"]["size"] = [int(R["output"]["size"][0] * s) // 2 * 2, int(R["output"]["size"][1] * s) // 2 * 2]
        if a.seconds: R["output"]["duration"] = a.seconds
        rc = Recipe(R, os.path.dirname(os.path.abspath(a.recipe)), a.vo_dir); rd = Renderer(rc, os.path.join(a.assets, R["base"]["file"]))
    except (RecipeError, FileNotFoundError) as e:
        print("recipe error:", e, file=sys.stderr); return 3
    os.makedirs(a.out, exist_ok=True)
    if a.at is not None:
        for t in a.at: cv2.imwrite(os.path.join(a.out, f"{name}_still_t{t:05.2f}.png"), rd.frame(t)[..., ::-1])
        return 0
    n = rd.duration_frames(); mp4 = os.path.join(a.out, f"{name}_silent.mp4"); h = hashlib.sha1(); t0 = time.time()
    try:
        with FFmpegWriter(mp4, rc.W, rc.H, rc.fps, crf=a.crf) as w:
            for i in range(n):
                f = rd.frame(i / rc.fps); h.update(f.tobytes()); w.write(f)
        w.finalize(dict(W=rc.W, H=rc.H, fps=rc.fps, frames=n))
    except EncodeError as e:
        print("encode error:", e, file=sys.stderr); return 4
    dt = time.time() - t0
    man = dict(name=name, frames=n, size=[rc.W, rc.H], fps=rc.fps, duration_s=rc.dur, render_s=round(dt, 1), render_fps=round(n / dt, 2), render_s_per_video_second=round(dt / rc.dur, 2),
               frames_sha1=h.hexdigest(), events=[dict(id=e.get("id"), do=e["do"], t0=round(e["t0"], 3), t1=round(e["t1"], 3)) for e in rc.ev], status="INTERNAL_POC_NOT_FOR_PUBLICATION")
    json.dump(man, open(os.path.join(a.out, f"{name}_manifest.json"), "w"), indent=1)
    if a.wav:
        off = R["vo"].get("offset_s", 0.0); out = os.path.join(a.out, f"{name}_with_vo.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-ss", str(off), "-t", str(rc.dur), "-i", a.wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", f"afade=t=out:st={rc.dur-0.35}:d=0.35", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print(json.dumps({k: man[k] for k in ("frames", "render_s", "render_fps", "render_s_per_video_second", "frames_sha1")})); return 0

if __name__ == "__main__": sys.exit(main())
