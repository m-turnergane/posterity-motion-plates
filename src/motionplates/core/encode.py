"""Video encoding with failure handling.

Profiles (see docs/ENCODING.md for the measured benchmark):
  direct      (default) raw RGB frames piped into ONE ffmpeg: RGB->yuv420p conversion done once by swscale (bt709 matrix, full->tv range,
              accurate rounding + full chroma interpolation) and encoded straight to the final H.264 settings. Colour tags are explicit.
  legacy2pass old behaviour: CRF0 4:2:0 intra intermediate, then a second lossy encode (kept for benchmark/comparison only).

All writers are context managers: output goes to <dst>.tmp.mp4 and is atomically renamed only after ffmpeg exits 0 AND (optionally) the
caller verifies the file. On any exception the temp file is removed and ffmpeg is terminated."""
import json, os, shutil, subprocess, tempfile

TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
SCALE_DIRECT = "scale=in_range=pc:out_range=tv:out_color_matrix=bt709:flags=area+accurate_rnd+full_chroma_int,format=yuv420p"

class EncodeError(RuntimeError):
    pass

def tmp_path(dst):
    root, ext = os.path.splitext(dst)
    return root + ".tmp" + ext

class FFmpegWriter:
    """with FFmpegWriter(dst, W, H, fps) as w: w.write(rgb_uint8_frame)  -> dst appears only on clean exit."""
    def __init__(self, dst, W, H, fps, crf=14, preset="slow", profile="direct", threads=0):
        self.dst, self.W, self.H, self.fps, self.crf, self.preset, self.profile = dst, W, H, fps, crf, preset, profile
        self.tmp = tmp_path(dst); self.n = 0; self.p = None; self._err = None; self.threads = threads
    def _cmd(self):
        base = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{self.W}x{self.H}", "-r", str(self.fps), "-i", "-", "-an"]
        if self.profile == "direct":
            enc = ["-vf", SCALE_DIRECT, "-c:v", "libx264", "-crf", str(self.crf), "-preset", self.preset, "-pix_fmt", "yuv420p", *TAGS]
        elif self.profile == "intra_lossless":   # scratch intermediate only
            enc = ["-c:v", "libx264", "-crf", "0", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "1"]
        else:
            raise ValueError(self.profile)
        if self.threads: enc += ["-threads", str(self.threads)]
        return base + enc + ["-movflags", "+faststart", "-f", "mp4", self.tmp]
    def __enter__(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.dst)), exist_ok=True)
        self._err = tempfile.TemporaryFile()
        self.p = subprocess.Popen(self._cmd(), stdin=subprocess.PIPE, stderr=self._err)
        return self
    def write(self, frame):
        try:
            self.p.stdin.write(memoryview(frame).cast("B") if frame.flags["C_CONTIGUOUS"] else frame.tobytes())
        except (BrokenPipeError, OSError) as e:
            raise EncodeError("ffmpeg closed its input: " + self._stderr()) from e
        self.n += 1
    def _stderr(self):
        try:
            self._err.seek(0); return self._err.read().decode(errors="replace")[-1500:]
        except Exception:
            return ""
    def __exit__(self, et, ev, tb):
        try:
            if self.p.stdin and not self.p.stdin.closed:
                try: self.p.stdin.close()
                except Exception: pass
            if et is not None:
                self.p.kill(); self.p.wait(); self._cleanup(); return False
            rc = self.p.wait()
            if rc != 0:
                msg = self._stderr(); self._cleanup(); raise EncodeError(f"ffmpeg exited {rc}: {msg}")
            if not os.path.exists(self.tmp) or os.path.getsize(self.tmp) == 0:
                self._cleanup(); raise EncodeError("ffmpeg produced no output")
        finally:
            try: self._err.close()
            except Exception: pass
        return False
    def _cleanup(self):
        if os.path.exists(self.tmp): os.remove(self.tmp)
    def finalize(self, expect=None):
        """Verify the temp file (ffprobe + full decode) and atomically move it to dst. expect: dict(W,H,fps,frames)."""
        info = verify_video(self.tmp, **(expect or dict(W=self.W, H=self.H, fps=self.fps, frames=self.n)))
        os.replace(self.tmp, self.dst); return info

def ffprobe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate,avg_frame_rate,nb_read_packets,pix_fmt,codec_name,color_space,color_range,color_primaries,color_transfer,duration:format=duration", "-of", "json", path],
        capture_output=True, text=True)
    if out.returncode != 0: raise EncodeError("ffprobe failed: " + out.stderr[-500:])
    j = json.loads(out.stdout); s = j["streams"][0]; s["format_duration"] = float(j["format"].get("duration", 0)); return s

def verify_video(path, W, H, fps, frames, full_decode=True, dur_tol=0.05):
    """Raise EncodeError unless resolution, fps, frame count/duration match and the whole file decodes without error."""
    try: s = ffprobe(path); s["nb_read_packets"]; s["r_frame_rate"]; s["width"]
    except (KeyError, IndexError, ValueError) as e: raise EncodeError(f"unreadable video (ffprobe incomplete): {e!r}")
    num, den = (int(x) for x in s["r_frame_rate"].split("/")); got_fps = num / den
    problems = []
    if (int(s["width"]), int(s["height"])) != (W, H): problems.append(f"resolution {s['width']}x{s['height']} != {W}x{H}")
    if abs(got_fps - fps) > 1e-3: problems.append(f"fps {got_fps} != {fps}")
    if int(s["nb_read_packets"]) != frames: problems.append(f"frames {s['nb_read_packets']} != {frames}")
    if abs(s["format_duration"] - frames / fps) > dur_tol: problems.append(f"duration {s['format_duration']:.3f} != {frames / fps:.3f}")
    if s["pix_fmt"] != "yuv420p": problems.append("pix_fmt " + s["pix_fmt"])
    dec_frames = None
    if full_decode:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
        if r.returncode != 0 or r.stderr.strip(): problems.append("decode errors: " + r.stderr.strip()[-300:])
        r2 = subprocess.run(["ffmpeg", "-i", path, "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
        import re
        m = re.findall(r"frame=\s*(\d+)", r2.stderr); dec_frames = int(m[-1]) if m else None
        if dec_frames is not None and dec_frames != frames: problems.append(f"decoded {dec_frames} frames != {frames}")
    if problems: raise EncodeError("verification failed: " + "; ".join(problems))
    return dict(width=int(s["width"]), height=int(s["height"]), fps=got_fps, frames=int(s["nb_read_packets"]), duration_s=s["format_duration"], pix_fmt=s["pix_fmt"],
                color_space=s.get("color_space"), color_range=s.get("color_range"), decoded_frames=dec_frames, full_decode_ok=bool(full_decode))

def reencode_atomic(src, dst, crf=17, preset="slow", extra_vf=None, frames=None):
    """Generic lossy re-encode (used for comparison videos) with temp+rename and exit-code check."""
    tmp = tmp_path(dst); vf = extra_vf
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src] + (["-vf", vf] if vf else []) + ["-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p", *TAGS, "-an", "-movflags", "+faststart", "-f", "mp4", tmp]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.replace(tmp, dst)
    except subprocess.CalledProcessError as e:
        if os.path.exists(tmp): os.remove(tmp)
        raise EncodeError("ffmpeg failed: " + e.stderr.decode(errors="replace")[-500:]) from e
