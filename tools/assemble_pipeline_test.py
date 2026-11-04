#!/usr/bin/env python3
"""Synthetic 16:9 pipeline test. Not an episode. Does not call Higgsfield.

Plate is drawn here. Motion is the house scale-only push, 1.00 to 1.06,
geometric in u. Guardrails are imported from the engine worktree when present.
Narration runs only if ELEVENLABS_API_KEY is set, using config/narration.yaml,
and the key is never printed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "var" / "pipeline-test"
W, H, FPS = 1920, 1080, 30
SECONDS = 6
PUSH = (1.0, 1.06)
ENGINE = Path(os.environ.get("ENGINE_WT", "/tmp/engine-wt"))
FONT = ENGINE / "fonts/ofl/imfelldwpica/IMFePIrm28P.ttf"
LINE = "This is a technical test of the archive voice. No story is being told."


def draw_plate() -> np.ndarray:
    yy, xx = np.mgrid[0:H, 0:W]
    parchment = np.zeros((H, W, 3), np.uint8)
    parchment[..., 0] = 196 + (xx / W * 28).astype(np.uint8)
    parchment[..., 1] = 176 + ((yy / H) * 22).astype(np.uint8)
    parchment[..., 2] = 148
    # A dark arch and a bronze rail. No letters on the master.
    arch = ((xx - W * 0.5) / 520) ** 2 + ((yy - H * 0.15) / 780) ** 2
    parchment[arch < 1.0] = (72, 58, 48)
    parchment[arch < 0.55] = (214, 196, 168)
    parchment[yy > int(H * 0.78)] = (90, 62, 42)
    parchment[yy > int(H * 0.84)] = (128, 86, 48)
    return parchment


def push_frame(plate: np.ndarray, u: float) -> np.ndarray:
    z0, z1 = PUSH
    scale = z0 * (z1 / z0) ** u
    cw = max(2, int(round(W / scale)))
    ch = max(2, int(round(H / scale)))
    x0 = (W - cw) // 2
    y0 = (H - ch) // 2
    crop = plate[y0:y0 + ch, x0:x0 + cw]
    return cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA)


def title_overlay(frame: np.ndarray, text: str) -> np.ndarray:
    im = Image.fromarray(frame)
    draw = ImageDraw.Draw(im, "RGBA")
    font = ImageFont.truetype(str(FONT), 78) if FONT.exists() else ImageFont.load_default()
    band_top = int(H * 0.16) - 40
    draw.rectangle((160, band_top, W - 160, band_top + 120), fill=(90, 26, 24, 210))
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((W - tw) / 2, band_top + (120 - th) / 2), text, font=font, fill=(243, 237, 224, 255))
    return np.asarray(im.convert("RGB"))


def guardrail_report(plate_wh: tuple[int, int]) -> dict:
    path = ENGINE / "engine/motion/guardrails.py"
    if not path.exists():
        return {"status": "SKIPPED", "reason": f"missing {path}"}
    import importlib.util
    spec = importlib.util.spec_from_file_location("house_guardrails", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rep = mod.check_pixel_density(plate_wh, (W, H), PUSH, mode="refuse", name="synthetic-16x9")
    return {"status": "PASS" if rep.get("pass") else "FAIL", "report": rep}


def synthesize_voice(dest_mp3: Path, alignment_path: Path) -> dict:
    cfg = yaml.safe_load((ROOT / "config/narration.yaml").read_text())
    key = os.environ.get(cfg["secret_env"], "")
    if not key:
        return {"status": "ABSENT"}
    voice = cfg["voice_id"]
    fmt = cfg["output_format"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format={fmt}"
    settings = dict(cfg["voice_settings"])
    body = {"text": LINE, "model_id": cfg["model_id"], "seed": cfg["seed"], "voice_settings": settings}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
            headers = {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        return {"status": "HTTP_ERROR", "code": exc.code, "detail": detail}
    audio_b64 = payload.get("audio_base64") or ""
    dest_mp3.write_bytes(__import__("base64").b64decode(audio_b64))
    alignment = payload.get("alignment") or payload.get("normalized_alignment") or {}
    alignment_path.write_text(json.dumps({"text": LINE, "alignment": alignment}, indent=2))
    return {
        "status": "OK",
        "characters": len(LINE),
        "bytes": dest_mp3.stat().st_size,
        "request_id": headers.get("request-id") or headers.get("x-request-id"),
        "character_cost": headers.get("character-cost") or headers.get("x-character-count"),
        "has_alignment": bool(alignment),
    }


def words_from_alignment(path: Path) -> list[tuple[float, float, str]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    al = data.get("alignment") or {}
    chars = al.get("characters") or []
    starts = al.get("character_start_times_seconds") or []
    ends = al.get("character_end_times_seconds") or []
    words = []
    buf, ws, we = [], None, None
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


def write_captions(words: list[tuple[float, float, str]], srt: Path, vtt: Path) -> int:
    cues = []
    chunk = []
    for start, end, word in words:
        chunk.append((start, end, word))
        if len(chunk) == 6:
            cues.append(chunk)
            chunk = []
    if chunk:
        cues.append(chunk)
    if not cues:
        cues = [[(0.4, 3.5, LINE)]]

    def ts(t: float, comma: str) -> str:
        t = max(0.0, t)
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = t % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", comma)

    srt_lines, vtt_lines = [], ["WEBVTT", ""]
    for i, cue in enumerate(cues, 1):
        text = " ".join(c[2] if isinstance(c, tuple) else c for c in cue)
        if isinstance(cue[0], tuple) and len(cue[0]) == 3 and cue[0][2] != LINE:
            a, b = cue[0][0], cue[-1][1]
            text = " ".join(c[2] for c in cue)
        else:
            a, b, text = cue[0]
        srt_lines += [str(i), f"{ts(a, ',')} --> {ts(b, ',')}", text, ""]
        vtt_lines += [f"{ts(a, '.')} --> {ts(b, '.')}", text, ""]
    srt.write_text("\n".join(srt_lines) + "\n")
    vtt.write_text("\n".join(vtt_lines) + "\n")
    return len(cues)


def loudnorm(src: Path, wav: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-ar", "48000", "-ac", "2", str(wav)],
        check=True, capture_output=True,
    )


def encode(frames_iter, n: int, audio: Path | None, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
    ]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-r", str(FPS)]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", str(dest)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin
    for frame in frames_iter:
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    code = proc.wait()
    if code != 0:
        raise SystemExit(err[-2000:])


def probe(dest: Path) -> dict:
    raw = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_name,width,height,avg_frame_rate,channels,sample_rate,codec_type",
         "-of", "json", str(dest)],
        text=True,
    )
    return json.loads(raw)


def ebur(dest: Path) -> str:
    proc = subprocess.run(
        ["ffmpeg", "-i", str(dest), "-filter_complex", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    lines = [ln for ln in proc.stderr.splitlines() if "I:" in ln or "Peak:" in ln or "True peak" in ln]
    return "\n".join(lines[-8:])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plate = draw_plate()
    Image.fromarray(plate).save(OUT / "plate.png")
    guards = guardrail_report((W, H))
    if guards.get("status") == "FAIL":
        raise SystemExit(json.dumps(guards))
    voice = synthesize_voice(OUT / "voice.mp3", OUT / "alignment.json")
    audio = None
    if voice.get("status") == "OK":
        loudnorm(OUT / "voice.mp3", OUT / "voice.wav")
        audio = OUT / "voice.wav"
    words = words_from_alignment(OUT / "alignment.json")
    cues = write_captions(words, OUT / "captions.srt", OUT / "captions.vtt")
    n = SECONDS * FPS

    def frames():
        for i in range(n):
            u = i / max(n - 1, 1)
            frame = push_frame(plate, u)
            if i < FPS * 2:
                frame = title_overlay(frame, "TECHNICAL TEST")
            yield frame

    dest = OUT / "pipeline-test.mp4"
    encode(frames(), n, audio, dest)
    still = OUT / "frame-mid.png"
    mid = push_frame(plate, 0.5)
    Image.fromarray(mid).save(still)
    report = {
        "label": "synthetic technical test, not the Edward feature",
        "mp4": str(dest),
        "md5": subprocess.check_output(["md5sum", str(dest)], text=True).split()[0],
        "guardrails": guards,
        "voice": {k: v for k, v in voice.items() if k != "detail"} if voice.get("status") != "HTTP_ERROR" else voice,
        "caption_cues": cues,
        "title": "PIL stand-in. ChronicleHookV3-2b is 1080x1920 and its default plate is not in the bundle.",
        "probe": probe(dest),
        "ebur128_tail": ebur(dest) if audio else "no audio stream",
        "higgsfield_calls": 0,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ("md5", "voice", "caption_cues", "ebur128_tail")}, indent=2))


if __name__ == "__main__":
    main()
