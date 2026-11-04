import sys, subprocess, numpy as np, json; sys.path.insert(0, 'tools'); import prod as P
M = P.load_engine(); cfg = P.load_cfg(); E = M.Engine(cfg); box = P.plate_box(); print("box", box, "plate", E.plate.shape)
idx = [0, 1, 76, 152]; frames = []
for fi in idx:
    img, dx, dy = E.render(fi / P.FPS); frames.append(np.asarray(P.frame_out(img, box, P.SEG_P05, fi)))
tmp = 'work/verify_static_tmp.mp4'
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{P.W}x{P.H}", "-r", "30", "-i", "pipe:0", "-an", *P.ENC_INTER, tmp], stdin=subprocess.PIPE)
for f in frames: p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
def dec(path, sel):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-vf", "select='" + "+".join(f"eq(n\\,{i})" for i in sel) + "'", "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, P.H, P.W, 3)
A = dec(str(P.ROOT / "edit/_build_v2c_P05STATIC_PREPCHECK/p05static/P05_static.mp4"), idx); B = dec(tmp, range(4))
res = [dict(frame=i, max_abs=int(np.abs(a.astype(int) - b).max()), identical=bool((a == b).all())) for i, a, b in zip(idx, A, B)]
print(json.dumps(res)); json.dump(res, open('qc/verify_static_vs_prod.json', 'w'))
