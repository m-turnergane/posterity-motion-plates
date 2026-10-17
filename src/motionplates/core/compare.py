import os, subprocess, glob, cv2, numpy as np

def make_compare(man, outdir):
    name = man["name"]; mp4 = man["mp4"]; static = os.path.join(outdir, f"{name}_static_plate.png")
    cmpf = os.path.join(outdir, f"{name}_compare_sidebyside.mp4"); fps = man["output"]["fps"]
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(fps), "-i", static, "-i", mp4,
        "-filter_complex", "[0:v]format=yuv420p[a];[1:v]format=yuv420p[b];[a][b]hstack=inputs=2,scale=1280:-2:flags=lanczos[v]", "-map", "[v]", "-frames:v", str(man["output"]["frames"]),
        "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", cmpf])
    base = cv2.imread(static)
    for p in sorted(glob.glob(os.path.join(outdir, "stills_raw", f"{name}_t*.png"))):
        t = os.path.basename(p).split("_t")[-1][:-4]; im = cv2.imread(p)
        lab = f"{name}  t={t}s  (1080x1920)"; im = im.copy(); cv2.rectangle(im, (0, 0), (im.shape[1], 44), (0, 0, 0), -1); cv2.putText(im, lab, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(os.path.join(outdir, f"{name}_still_t{t}.png"), im)
        # static | animated pair
        pair = np.hstack([base, cv2.imread(p)]); cv2.imwrite(os.path.join(outdir, f"{name}_pair_t{t}.jpg"), cv2.resize(pair, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 90])
