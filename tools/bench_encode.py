"""Encode-pipeline benchmark: python tools/bench_encode.py <source.mp4 or dir of PNGs> --frames 90 --out /tmp/bench
Reference = decoded RGB frames of the source (treated as the lossless render). Each pipeline encodes it, is decoded back to RGB
(ffmpeg honours colour tags) and compared: mean/max abs error (0-255), PSNR, SSIM (mean over RGB, gaussian 11x11)."""
import argparse, json, os, subprocess, sys, time
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from motionplates.core.encode import FFmpegWriter, TAGS, EncodeError

def ssim(a, b):
    a = a.astype(np.float32); b = b.astype(np.float32); C1, C2 = 6.5025, 58.5225; g = lambda x: cv2.GaussianBlur(x, (11, 11), 1.5)
    mu1, mu2 = g(a), g(b); s11 = g(a * a) - mu1 ** 2; s22 = g(b * b) - mu2 ** 2; s12 = g(a * b) - mu1 * mu2
    return float((((2 * mu1 * mu2 + C1) * (2 * s12 + C2)) / ((mu1 ** 2 + mu2 ** 2 + C1) * (s11 + s22 + C2))).mean())

def load_ref(src, n, W, H):
    if src.lower().endswith(".png"):   # true-RGB reference: plate with slow sub-pixel pan/zoom (so inter prediction has something to do)
        im = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB); im = cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA) if im.shape[:2] != (H, W) else im; out = []
        for i in range(n):
            s = 1 + 0.03 * i / max(n - 1, 1); M = np.array([[s, 0, -(s - 1) * W / 2 + 0.3 * i], [0, s, -(s - 1) * H / 2 + 0.2 * i]], np.float32)
            out.append(cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE))
        return np.stack(out)
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3)

def decode(path, W, H):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3)

def synth_colour_frame(W, H):
    """saturated patches + gradients + thin lines: stresses chroma subsampling / matrix errors"""
    img = np.zeros((H, W, 3), np.uint8); cols = [(220, 20, 40), (20, 160, 60), (30, 60, 220), (240, 220, 40), (200, 40, 200), (20, 200, 220), (250, 250, 250), (128, 128, 128), (16, 16, 16), (235, 235, 235)]
    for i, c in enumerate(cols): img[:, i * W // len(cols):(i + 1) * W // len(cols)] = c
    for y in range(0, H, 24): img[y:y + 1] = (255 - np.array(cols[(y // 24) % len(cols)]))
    img[H // 2:, :] = (np.linspace(0, 255, W)[None, :, None] * np.array([1, .6, .3])[None, None, :]).astype(np.uint8)
    return img

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--frames", type=int, default=90); ap.add_argument("--out", default="/tmp/bench"); ap.add_argument("--W", type=int, default=1080); ap.add_argument("--H", type=int, default=1920)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); W, H, fps = a.W, a.H, 30
    ref = load_ref(a.src, a.frames, W, H); N = len(ref); print("reference frames", ref.shape)
    syn = synth_colour_frame(W, H)
    results = []
    def run_pipeline(name, make):
        for label, frames in (("real", ref), ("synthetic-colour", np.repeat(syn[None], 12, 0))):
            dst = os.path.join(a.out, f"{name}_{label}.mp4"); t0 = time.time(); make(dst, frames); et = time.time() - t0
            dec = decode(dst, W, H); n = min(len(dec), len(frames)); e = np.abs(dec[:n].astype(np.int16) - frames[:n].astype(np.int16))
            idx = np.linspace(0, n - 1, 6).astype(int); ss = float(np.mean([ssim(dec[i], frames[i]) for i in idx]))
            mse = float((e.astype(np.float64) ** 2).mean()); psnr = 10 * np.log10(255 ** 2 / mse) if mse > 0 else 99.0
            row = dict(pipeline=name, content=label, encode_s=round(et, 1), fps=round(n / et, 2), size_MB=round(os.path.getsize(dst) / 1e6, 2), mean_abs_err=round(float(e.mean()), 3),
                       max_abs_err=int(e.max()), p99_abs_err=int(np.percentile(e[::6], 99)), psnr_db=round(psnr, 2), ssim=round(ss, 5), decoded_frames=n)
            print(row, flush=True); results.append(row)
    def legacy(dst, frames):
        tmp = dst + ".inter.mp4"
        subprocess.run(["bash", "-c", f"ffmpeg -y -v error -f rawvideo -pix_fmt rgb24 -s {W}x{H} -r 30 -i - -c:v libx264 -crf 0 -preset veryfast -pix_fmt yuv420p -g 1 {tmp}"], input=frames.tobytes(), check=True)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", dst], check=True); os.remove(tmp)
    def raw_pipe(vf, tags, crf=14):
        def f(dst, frames):
            cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-"] + (["-vf", vf] if vf else []) + ["-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-pix_fmt", "yuv420p"] + (TAGS if tags else []) + ["-movflags", "+faststart", dst]
            subprocess.run(cmd, input=frames.tobytes(), check=True)
        return f
    def prod_writer(dst, frames):
        with FFmpegWriter(dst, W, H, fps) as w:
            for fr in frames: w.write(np.ascontiguousarray(fr))
            pass
        w.finalize()
    run_pipeline("legacy_2pass_untagged", legacy)
    run_pipeline("direct_untagged_default", raw_pipe(None, False))
    run_pipeline("direct_bt709_tagged_bicubic", raw_pipe("scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p", True))
    run_pipeline("direct_bt709_tagged_area", raw_pipe("scale=in_range=pc:out_range=tv:out_color_matrix=bt709:flags=area+accurate_rnd+full_chroma_int,format=yuv420p", True))
    run_pipeline("FFmpegWriter default (bt709 tagged, area+accurate_rnd)", prod_writer)
    json.dump(results, open(os.path.join(a.out, "bench.json"), "w"), indent=1)
main()
