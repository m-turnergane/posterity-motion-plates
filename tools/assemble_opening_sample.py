#!/usr/bin/env python3
"""Assemble the Edward II opening sample.

Pictures, voice and the finished film stay under var/. The wordmark master is
the dusk-outro lettering, reused as an ink mask. Motion is a deterministic
eased push or a fixed crop. The intro is last in the picture order and is
drawn by this script, not by an image model.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VAR = ROOT / "var/edward-ii-feature/opening-sample"
VO = VAR / "vo"
PLATES = VAR / "plates"
WORDMARK = ROOT / "var/edward-ii-feature/wordmark/posterity-master.png"
SCORE = ROOT / "var/edward-ii-feature/retrieved/score/Anabasis_I.mp3"
I2V = VAR / "plates/H06-i2v.mp4"
FONT = Path("/tmp/engine-wt/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf")

W, H, FPS = 1920, 1080, 30
GAP = 0.40
INTRO = 7.5
TAIL = 0.60
INK = np.array([48, 32, 20], np.float32) / 255.0
OXBLOOD = np.array([90, 26, 24], np.float32) / 255.0


def ease(u: float) -> float:
    u = min(1.0, max(0.0, u))
    return u * u * (3.0 - 2.0 * u)


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def alignment(line_id: str) -> dict:
    return json.loads((VO / f"{line_id}.alignment.json").read_text())


def words_of(line_id: str) -> list[tuple[float, float, str]]:
    al = alignment(line_id)["alignment"]
    chars = al["characters"]
    starts = al["character_start_times_seconds"]
    ends = al["character_end_times_seconds"]
    words: list[tuple[float, float, str]] = []
    buf: list[str] = []
    ws = we = None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if buf:
                words.append((ws, we, "".join(buf)))
                buf, ws, we = [], None, None
            continue
        if ws is None:
            ws = s
        we = e
        buf.append(ch)
    if buf:
        words.append((ws, we, "".join(buf)))
    return words


def speech_bounds(line_id: str) -> tuple[float, float]:
    words = words_of(line_id)
    return words[0][0], words[-1][1]


def build_timeline() -> tuple[list[dict], list[dict], float]:
    """Place each locked line, then the picture cuts that ride on it."""
    order = [
        ("L01", "S001", "H06-v2.png", {"z": (1.00, 1.06), "cx": (0.46, 0.46), "cy": (0.52, 0.54)}),
        ("L02", "S002", "H06-v2.png", {"z": (1.70, 1.78), "cx": (0.40, 0.40), "cy": (0.64, 0.64)}),
        ("L03", "S003", "H01.png", {"z": (1.02, 1.08), "cx": (0.56, 0.40), "cy": (0.48, 0.46)}),
        ("L04", "S004", "N14.png", {"z": (1.00, 1.06), "cx": (0.58, 0.60), "cy": (0.58, 0.58)}),
        ("L05", "S005", "DK1.png", {"z": (1.00, 1.08), "cx": (0.55, 0.55), "cy": (0.50, 0.50)}),
        ("L07", "S007", "N01.png", {"z": (2.05, 2.12), "cx": (0.84, 0.84), "cy": (0.30, 0.30)}),
        ("L07a", "S007a", "N01.png", {"z": (2.15, 2.20), "cx": (0.40, 0.40), "cy": (0.40, 0.40)}),
        ("L08", "S008", "N01.png", {"z": (1.48, 1.04), "cx": (0.70, 0.50), "cy": (0.42, 0.46)}),
        ("L08", "S008a", "N21.png", {"z": (1.04, 1.10), "cx": (0.62, 0.58), "cy": (0.42, 0.42)}),
        ("L09", "S009", "N01.png", {"z": (1.42, 1.50), "cx": (0.48, 0.48), "cy": (0.42, 0.42), "cool": True}),
    ]
    audio = []
    cursor = 0.0
    placed = {}
    for line_id, shot, plate, motion in order:
        if line_id in placed:
            continue
        first, last = speech_bounds(line_id)
        audio.append({
            "id": line_id,
            "path": VO / f"{line_id}.mp3",
            "file_at": cursor - first,
            "speech_start": cursor,
            "speech_end": cursor + (last - first),
        })
        placed[line_id] = audio[-1]
        gap = INTRO if line_id == "L05" else GAP
        cursor = audio[-1]["speech_end"] + gap
    end = placed["L09"]["speech_end"] + TAIL

    pictures = []
    for line_id, shot, plate, motion in order:
        seg = placed[line_id]
        start = seg["speech_start"]
        if line_id == "L08":
            words = words_of("L08")
            # First 26 words stay on N01. "even" is word 27.
            rel = words[26][0] - words[0][0]
            if shot == "S008":
                stop = start + rel
            else:
                start = start + rel
                stop = seg["speech_end"] + GAP
        elif line_id == "L05":
            stop = seg["speech_end"]
        elif line_id == "L09":
            stop = end
        else:
            nxt = {
                "L01": placed["L02"]["speech_start"],
                "L02": placed["L03"]["speech_start"],
                "L03": placed["L04"]["speech_start"],
                "L04": placed["L05"]["speech_start"],
                "L07": placed["L07a"]["speech_start"],
                "L07a": placed["L08"]["speech_start"],
            }[line_id]
            stop = nxt
        pictures.append({
            "shot": shot,
            "line": line_id,
            "plate": plate,
            "start": start,
            "stop": stop,
            **motion,
        })
    intro_start = placed["L05"]["speech_end"]
    intro_stop = placed["L07"]["speech_start"]
    pictures.append({
        "shot": "SC01",
        "line": "intro",
        "plate": "CB1.png",
        "start": intro_start,
        "stop": intro_stop,
        "intro": True,
    })
    pictures.sort(key=lambda s: s["start"])
    return audio, pictures, end


def sample(plate: np.ndarray, z: float, cx: float, cy: float) -> np.ndarray:
    h, w = plate.shape[:2]
    cw, ch = w / z, h / z
    x0 = min(max(cx * w - cw / 2.0, 0.0), w - cw)
    y0 = min(max(cy * h - ch / 2.0, 0.0), h - ch)
    crop = plate[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    if crop.size == 0:
        crop = plate
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_LINEAR)


def cool(frame: np.ndarray) -> np.ndarray:
    f = frame.astype(np.float32)
    f[:, :, 0] *= 0.92
    f[:, :, 2] = np.clip(f[:, :, 2] * 1.08, 0, 255)
    return f.astype(np.uint8)


def text_alpha(text: str, size: int, tracking: int = 0) -> np.ndarray:
    font = ImageFont.truetype(str(FONT), size)
    widths = []
    for ch in text:
        box = font.getbbox(ch)
        widths.append(box[2] - box[0] + tracking)
    width = sum(widths) + 8
    height = font.getbbox("Hg")[3] + 16
    img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(img)
    x = 4
    for ch, wch in zip(text, widths):
        draw.text((x, 4), ch, font=font, fill=255)
        x += wch
    return np.asarray(img)


def letter_spans(alpha: np.ndarray) -> list[tuple[int, int]]:
    cols = alpha.max(axis=0) > 16
    spans = []
    on = None
    for i, flag in enumerate(cols):
        if flag and on is None:
            on = i
        elif not flag and on is not None:
            if i - on > 2:
                spans.append((on, i))
            on = None
    if on is not None:
        spans.append((on, alpha.shape[1]))
    return spans


def stroke_alpha(alpha: np.ndarray, spans: list[tuple[int, int]], u: float) -> np.ndarray:
    """Reveal letter by letter. Inside a letter the ink travels from the left."""
    out = np.zeros(alpha.shape, np.float32)
    if not spans:
        return out
    pos = min(1.0, max(0.0, u)) * len(spans)
    xs = np.arange(alpha.shape[1])
    for i, (x0, x1) in enumerate(spans):
        local = pos - i
        if local <= 0:
            continue
        if local >= 1:
            out[:, x0:x1] = alpha[:, x0:x1] / 255.0
            continue
        cut = x0 + (x1 - x0) * local
        ramp = np.clip((cut - xs) / 7.0, 0.0, 1.0)
        out[:, x0:x1] = (alpha[:, x0:x1] / 255.0) * ramp[x0:x1]
    return out


def multiply(base: np.ndarray, alpha: np.ndarray, ink: np.ndarray, origin: tuple[int, int]) -> np.ndarray:
    ah, aw = alpha.shape
    y, x = origin
    y0, x0 = max(0, y), max(0, x)
    y1, x1 = min(H, y + ah), min(W, x + aw)
    if y1 <= y0 or x1 <= x0:
        return base
    sub_a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    if sub_a.max() <= 0:
        return base
    patch = base[y0:y1, x0:x1].astype(np.float32) / 255.0
    painted = patch * (1.0 - sub_a * (1.0 - ink))
    base[y0:y1, x0:x1] = np.clip(painted * 255.0, 0, 255).astype(np.uint8)
    return base


def bloom_field(t: float) -> np.ndarray:
    rng = np.random.default_rng([1611, 7])
    noise = rng.random((H // 2 + 40, W // 2 + 40)).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0, 0), 6)
    shift = int(t * 8)
    noise = noise[shift:shift + H // 2, 10:10 + W // 2]
    noise = cv2.resize(noise, (W, H), interpolation=cv2.INTER_LINEAR)
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    field = (yy > 0.28) & (yy < 0.74) & (xx > 0.18) & (xx < 0.82)
    # Feather the type field so bloom stays outside the letters.
    dist = cv2.distanceTransform((~field).astype(np.uint8), cv2.DIST_L2, 3)
    guard = np.clip(dist / 36.0, 0, 1)
    grow = ease(min(1.0, t / 1.6))
    dry = 1.0 if t < 4.4 else max(0.35, 1.0 - (t - 4.4) / 2.0)
    alpha = np.clip((noise - 0.36) * 2.6, 0, 1) * guard * grow * dry * 0.9
    return alpha.astype(np.float32)


class Intro:
    def __init__(self, leaf: np.ndarray, wordmark: np.ndarray):
        self.leaf = leaf
        wm = wordmark
        target_w = 1180
        scale = target_w / wm.shape[1]
        self.word = cv2.resize(wm[:, :, 3], (target_w, int(wm.shape[0] * scale)), interpolation=cv2.INTER_LANCZOS4)
        self.word_spans = letter_spans(self.word)
        self.title = text_alpha("The Letter for a Buried King", 46, tracking=1)
        self.title_spans = letter_spans(self.title)
        self.act = text_alpha("ACT I", 92, tracking=18)
        self.act_spans = letter_spans(self.act)

    def frame(self, local: float) -> np.ndarray:
        z = lerp(1.13, 1.155, ease(local / INTRO))
        frame = sample(self.leaf, z, 0.53, 0.50)
        bloom = bloom_field(local)
        ink = INK.reshape(1, 1, 3)
        f = frame.astype(np.float32) / 255.0
        f = f * (1.0 - bloom[..., None] * (1.0 - ink))
        frame = np.clip(f * 255.0, 0, 255).astype(np.uint8)

        def window(t0: float, t1: float, hold: float, gone: float) -> float:
            if local < t0:
                return 0.0
            if local < t1:
                return ease((local - t0) / (t1 - t0))
            if local < hold:
                return 1.0
            if local < gone:
                return 1.0 - ease((local - hold) / (gone - hold))
            return 0.0

        wm_u = window(1.15, 3.15, 4.55, 5.65)
        if wm_u > 0:
            write = min(1.0, max(0.0, (local - 1.15) / (3.15 - 1.15)))
            alpha = stroke_alpha(self.word, self.word_spans, write) * wm_u
            origin = ((H - self.word.shape[0]) // 2 - 70, (W - self.word.shape[1]) // 2)
            frame = multiply(frame, alpha, INK, origin)
        title_u = window(2.45, 4.15, 5.15, 5.75)
        if title_u > 0:
            write = min(1.0, max(0.0, (local - 2.45) / (4.15 - 2.45)))
            alpha = stroke_alpha(self.title, self.title_spans, write) * title_u
            origin = ((H - self.title.shape[0]) // 2 + 70, (W - self.title.shape[1]) // 2)
            frame = multiply(frame, alpha, INK, origin)
        act_u = window(5.15, 6.25, 7.5, 7.51)
        if act_u > 0:
            write = min(1.0, max(0.0, (local - 5.15) / (6.25 - 5.15)))
            alpha = stroke_alpha(self.act, self.act_spans, write) * act_u
            origin = ((H - self.act.shape[0]) // 2, (W - self.act.shape[1]) // 2)
            frame = multiply(frame, alpha, OXBLOOD, origin)
        return frame


def shot_at(pictures: list[dict], t: float) -> dict:
    for shot in pictures:
        if shot["start"] <= t < shot["stop"]:
            return shot
    return pictures[-1]


def render_frame(t: float, pictures: list[dict], plates: dict[str, np.ndarray], intro: Intro, video) -> np.ndarray:
    shot = shot_at(pictures, t)
    if shot.get("intro"):
        return intro.frame(t - shot["start"])
    local = 0.0 if shot["stop"] <= shot["start"] else (t - shot["start"]) / (shot["stop"] - shot["start"])
    u = ease(local)
    z = lerp(shot["z"][0], shot["z"][1], u)
    cx = lerp(shot["cx"][0], shot["cx"][1], u)
    cy = lerp(shot["cy"][0], shot["cy"][1], u)
    if video is not None and shot["shot"] == "S001":
        video.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t - shot["start"]) * 1000.0)
        ok, bgr = video.read()
        if ok:
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            return cv2.resize(rgb, (W, H), interpolation=cv2.INTER_CUBIC)
    frame = sample(plates[shot["plate"]], z, cx, cy)
    if shot.get("cool"):
        frame = cool(frame)
    return frame


def write_stills(pictures, plates, intro, duration) -> None:
    dest = VAR / "stills"
    dest.mkdir(parents=True, exist_ok=True)
    times = []
    for shot in pictures:
        times.append((shot["start"] + 0.05, f"{shot['shot']}-in"))
        times.append(((shot["start"] + shot["stop"]) / 2, f"{shot['shot']}-mid"))
    for t, name in times:
        frame = render_frame(min(t, duration - 0.04), pictures, plates, intro, None)
        Image.fromarray(frame).save(dest / f"{name}.jpg", quality=85)
        print(name, round(t, 2))


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr[-2000:])


def build_voice(audio: list[dict], duration: float, dest: Path) -> None:
    cmd = ["ffmpeg", "-y"]
    for seg in audio:
        cmd += ["-i", str(seg["path"])]
    parts = []
    labels = []
    for i, seg in enumerate(audio):
        delay = max(0, int(round(seg["file_at"] * 1000)))
        parts.append(
            f"[{i}:a]adelay={delay}:all=1,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
            f"apad=whole_dur={duration:.3f}[a{i}]"
        )
        labels.append(f"[a{i}]")
    graph = ";".join(parts) + ";" + "".join(labels) + f"amix=inputs={len(audio)}:normalize=0:duration=first[vo]"
    cmd += ["-filter_complex", graph, "-map", "[vo]", "-t", f"{duration:.3f}", str(dest)]
    run(cmd)


def mix(voice: Path, duration: float, dest: Path) -> dict:
    voiced = VAR / "build/vo-processed.wav"
    bed = VAR / "build/bed.wav"
    ducked = VAR / "build/mix.wav"
    VAR.joinpath("build").mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-i", str(voice), "-af",
        "highpass=f=70,volume=10dB,"
        "acompressor=threshold=-22dB:ratio=2.2:attack=6:release=140:makeup=2,"
        "acompressor=threshold=-14dB:ratio=4:attack=2:release=60:knee=3",
        "-ar", "48000", "-ac", "2", str(voiced),
    ])
    # 12 LU under the processed voice, before the sidechain. Measured and trimmed below.
    run([
        "ffmpeg", "-y", "-i", str(SCORE), "-af",
        f"atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,volume=-16dB,aformat=channel_layouts=stereo",
        "-ar", "48000", "-ac", "2", str(bed),
    ])
    vo_i, _vo_p = ebur(voiced)
    bed_i, _bed_p = ebur(bed)
    # Unducked bed sits 12 LU under the processed voice. The sidechain ducks it further.
    delta = (vo_i - 12.0) - bed_i
    if abs(delta) >= 0.8:
        run([
            "ffmpeg", "-y", "-i", str(bed), "-af", f"volume={delta:.2f}dB",
            "-ar", "48000", "-ac", "2", str(bed.with_suffix('.adj.wav')),
        ])
        bed.with_suffix('.adj.wav').replace(bed)
        bed_i += delta
    print("levels", {"vo_i": vo_i, "bed_i": bed_i, "delta": round(delta, 2)})
    run([
        "ffmpeg", "-y", "-i", str(voiced), "-i", str(bed), "-filter_complex",
        "[0:a]asplit=2[vo][sc];"
        "[1:a][sc]sidechaincompress=threshold=0.035:ratio=2.5:attack=15:release=700:knee=4[bed];"
        "[vo][bed]amix=inputs=2:normalize=0:duration=first,"
        "acompressor=threshold=-16dB:ratio=1.6:attack=20:release=250,alimiter=limit=0.85:level=false[mix]",
        "-map", "[mix]", "-ar", "48000", "-ac", "2", str(ducked),
    ])
    measure = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(ducked),
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    text = measure.stderr
    stats = json.loads(text[text.rfind("{"):text.rfind("}") + 1])
    af = (
        "loudnorm=I=-14:TP=-1.5:LRA=11:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    run(["ffmpeg", "-y", "-i", str(ducked), "-af", af, "-ar", "48000", "-ac", "2", str(dest)])
    return {"measured_I": stats["input_i"], "measured_TP": stats["input_tp"]}


def ebur(path: Path) -> tuple[float, float]:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    integrated = peak = None
    summary = False
    for ln in proc.stderr.splitlines():
        if "Summary" in ln:
            summary = True
        if not summary:
            continue
        if "I:" in ln and "LUFS" in ln:
            integrated = float(ln.split("I:")[1].split("LUFS")[0])
        if ln.strip().startswith("Peak:"):
            peak = float(ln.split("Peak:")[1].split("dB")[0])
    if integrated is None or peak is None:
        raise SystemExit(proc.stderr[-1500:])
    return integrated, peak


def write_captions(audio: list[dict], srt: Path, vtt: Path) -> int:
    cues = []
    for seg in audio:
        words = words_of(seg["id"])
        first = words[0][0]
        chunk: list[tuple[float, float, str]] = []
        for start, end, word in words:
            abs_s = seg["speech_start"] + (start - first)
            abs_e = seg["speech_start"] + (end - first)
            chunk.append((abs_s, abs_e, word))
            text = " ".join(c[2] for c in chunk)
            if word.endswith((".", "?", "!")) or len(chunk) >= 12 or len(text) > 72:
                cues.append(chunk)
                chunk = []
        if chunk:
            cues.append(chunk)
    merged: list[list[tuple[float, float, str]]] = []
    for cue in cues:
        if merged and len(cue) == 1 and len(cue[0][2]) < 12:
            merged[-1].extend(cue)
        else:
            merged.append(cue)
    cues = merged

    def ts(t: float, comma: str) -> str:
        t = max(0.0, t)
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", comma)

    srt_lines, vtt_lines = [], ["WEBVTT", ""]
    for i, cue in enumerate(cues, 1):
        text = " ".join(c[2] for c in cue)
        srt_lines += [str(i), f"{ts(cue[0][0], ',')} --> {ts(cue[-1][1], ',')}", text, ""]
        vtt_lines += [f"{ts(cue[0][0], '.')} --> {ts(cue[-1][1], '.')}", text, ""]
    srt.write_text("\n".join(srt_lines) + "\n")
    vtt.write_text("\n".join(vtt_lines) + "\n")
    return len(cues)


def encode(pictures, plates, intro, duration: float, audio: Path, dest: Path) -> None:
    n = int(round(duration * FPS))
    video = cv2.VideoCapture(str(I2V)) if I2V.exists() else None
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-i", str(audio),
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-t", f"{n / FPS:.3f}", "-movflags", "+faststart", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin
    try:
        for i in range(n):
            frame = render_frame(i / FPS, pictures, plates, intro, video)
            proc.stdin.write(np.ascontiguousarray(frame).tobytes())
            if i % 300 == 0:
                print("frame", i, "/", n, flush=True)
        proc.stdin.close()
    except BrokenPipeError:
        err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
        raise SystemExit(err[-2000:])
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    code = proc.wait()
    if video is not None:
        video.release()
    if code != 0:
        raise SystemExit(err[-2000:])


def main() -> None:
    if not FONT.exists():
        raise SystemExit(f"missing title font {FONT}")
    audio, pictures, duration = build_timeline()
    plates = {name: load_rgb(PLATES / name) for name in {p["plate"] for p in pictures}}
    intro = Intro(plates["CB1.png"], np.asarray(Image.open(WORDMARK).convert("RGBA")))
    print(json.dumps({
        "duration": round(duration, 3),
        "shots": [{k: (round(s[k], 3) if k in {"start", "stop"} else s[k]) for k in ("shot", "line", "start", "stop")} for s in pictures],
    }, indent=2))
    if "--stills" in sys.argv:
        write_stills(pictures, plates, intro, duration)
        return
    (VAR / "build").mkdir(parents=True, exist_ok=True)
    voice = VAR / "build/voice.wav"
    build_voice(audio, duration, voice)
    mixed = VAR / "build/mixed.wav"
    stats = mix(voice, duration, mixed)
    integrated, peak = ebur(mixed)
    print("loudness", integrated, peak, stats)
    if abs(integrated + 14) >= 0.2 and peak + (-14 - integrated) <= -1.0:
        gain = round(-14.0 - integrated, 2)
        tuned = VAR / "build/mixed-tuned.wav"
        run(["ffmpeg", "-y", "-i", str(mixed), "-af", f"volume={gain:.2f}dB", "-ar", "48000", "-ac", "2", str(tuned)])
        tuned.replace(mixed)
        integrated, peak = ebur(mixed)
        print("tuned", integrated, peak, gain)
    cues = write_captions(audio, VAR / "captions.srt", VAR / "captions.vtt")
    silent = VAR / "build/picture.mp4"
    encode(pictures, plates, intro, duration, mixed, silent)
    final = VAR / "opening-sample.mp4"
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(VAR / "captions.srt"),
        "-c", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
        "-movflags", "+faststart", str(final),
    ])
    integrated, peak = ebur(final)
    print(json.dumps({"file": str(final), "cues": cues, "lufs": integrated, "peak": peak}))


if __name__ == "__main__":
    main()
