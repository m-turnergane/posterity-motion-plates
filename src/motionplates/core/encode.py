import subprocess, os

class LosslessWriter:
    """Pipes RGB frames to ffmpeg -> lossless x264 (yuv444 not needed; intra-only crf0 yuv420p) intermediate."""
    def __init__(self, path, W, H, fps):
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                                   "-i", "-", "-c:v", "libx264", "-crf", "0", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "1", path], stdin=subprocess.PIPE)
    def write(self, frame):
        self.p.stdin.write(frame.tobytes())
    def close(self):
        self.p.stdin.close(); self.p.wait()

def final_encode(src, dst, crf=14):
    """Delivery encode. Deliberately NO colour tagging/conversion so pixels go through exactly the same implicit RGB->yuv420p path as the editor (ENC_INTER/ENC_FINAL)."""
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", "-an", dst])
