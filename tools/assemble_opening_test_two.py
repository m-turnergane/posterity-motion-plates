#!/usr/bin/env python3
"""Second pass of the Edward II opening.

Same Oliver takes, same Anabasis I, same line timing as the first cut.
The picture path is different: a locked camera, one float resample, the
house flame and smoke on the shots that already have a usable plate, a
black-ink wordmark, and a black ACT I card.

Replacement plates, when they exist, live in
``var/edward-ii-feature/opening-sample-test-two/plates`` and override the
recovered stills. ``--full`` refuses to encode while a required plate is
missing, so the wrong execution image and the repeated hall crops are not
written out as the review film.

``--proofs`` renders the intro, the sealing insert, the letter spill, the
hall torches, and a contact of the raw sealing clip. It does not call
Higgsfield or ElevenLabs.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from motionplates.opening.camera import OUT_H, OUT_W, cover_sample, cover_window  # noqa: E402
from motionplates.opening.clip import load_clip  # noqa: E402
from motionplates.opening.effects import HouseLight  # noqa: E402
from motionplates.opening.intro import Intro  # noqa: E402

VAR = ROOT / "var/edward-ii-feature"
CUT1 = VAR / "opening-sample"
OUT = VAR / "opening-sample-test-two"
PLATES = CUT1 / "plates"
WORDMARK = VAR / "wordmark/posterity-master.png"
CLIP = PLATES / "H06-i2v.mp4"
REF_W, REF_H = 2752, 1536

# Plate-pixel rects measured on the recovered 2752x1536 stills.
FX = {
    "S002": {
        "candles": [(410, 630, 530, 800)],
        "smoke": [{
            "type": "candle", "src": (468, 690), "height": 100, "w1": 14, "w0": 2.0,
            "opacity": 0.38, "lean": -10, "meander": 0.1, "rise": 28,
        }],
        "protect": [[(700, 280), (1280, 280), (1280, 860), (700, 860)]],
        "spill_amp": 0.5,
        "radius_mult": 0.6,
    },
    "S005": {
        "offscreen": [{"xy": (260, -30), "h": 90, "radius": 2200}],
        "spill_amp": 1.15,
        "radius_mult": 0.5,
        "pulse": 2.4,
    },
    "S008": {
        "torches": [(990, 170, 1080, 360), (2340, 90, 2470, 300)],
        "smoke": [
            {"type": "torch", "src": (1024, 230), "height": 150, "w1": 26, "w0": 6,
             "opacity": 0.28, "rise": 36, "meander": 0.15},
            {"type": "torch", "src": (2406, 160), "height": 140, "w1": 24, "w0": 6,
             "opacity": 0.26, "rise": 34, "meander": 0.12},
        ],
        "protect": [
            [(900, 360), (1500, 360), (1500, 820), (900, 820)],
            [(1700, 300), (2300, 300), (2300, 760), (1700, 760)],
        ],
        "spill_amp": 0.45,
        "radius_mult": 0.4,
    },
}

# These five are the paid replacements. The recovered plates do not satisfy them.
REQUIRED = {
    "S003": "Gloucester funeral. No extra crown. The effigy reads as a carved figure.",
    "S004": "Pre-strike tableau. Kent at the block, axe raised, no impact.",
    "S007": "Kent, medium, in the hall. The king is not in frame.",
    "S007a": "Edward, medium. Kent is not in frame.",
    "S009": "The reign turns. A new picture, not a grade of N01.",
}


def cut_one():
    path = ROOT / "tools/assemble_opening_sample.py"
    spec = importlib.util.spec_from_file_location("opening_cut_one", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scale_rect(rect, w, h):
    x0, y0, x1, y1 = rect
    return (x0 * w / REF_W, y0 * h / REF_H, x1 * w / REF_W, y1 * h / REF_H)


def scale_fx(spec, w, h):
    out = dict(spec)
    for key in ("candles", "torches"):
        out[key] = [scale_rect(r, w, h) for r in spec.get(key, [])]
    out["smoke"] = []
    for src in spec.get("smoke", []):
        item = dict(src)
        sx, sy = src["src"]
        item["src"] = (sx * w / REF_W, sy * h / REF_H)
        out["smoke"].append(item)
    out["offscreen"] = []
    for src in spec.get("offscreen", []):
        item = dict(src)
        x, y = src["xy"]
        item["xy"] = (x * w / REF_W, y * h / REF_H)
        out["offscreen"].append(item)
    out["protect"] = [
        [(x * w / REF_W, y * h / REF_H) for x, y in poly]
        for poly in spec.get("protect", [])
    ]
    return out


def plate_path(name: str) -> Path:
    override = OUT / "plates" / name
    if override.exists():
        return override
    return PLATES / name


def camera_for(shot: str, plate: np.ndarray):
    h, w = plate.shape[:2]
    if shot == "S002":
        # Left-hand 1920x1080 of the sealing still: candle, hands, blank letter.
        # One source pixel per output pixel on a 2752x1536 plate.
        z_cap = 1.0 / max(OUT_W / w, OUT_H / h)
        cx, cy = 960 / REF_W, 996 / REF_H
        return cover_window(w, h, z_cap, cx, cy)
    return cover_window(w, h, 1.0, 0.5, 0.5)


def load_plates(names: set[str]) -> dict[str, np.ndarray]:
    plates = {}
    for name in names:
        path = plate_path(name)
        img = np.asarray(Image.open(path).convert("RGB"))
        plates[name] = img
    return plates


def shot_views(pictures, plates):
    """Locked cameras for the still shots this pass can already render."""
    views = {}
    for shot in pictures:
        name = shot["shot"]
        if shot.get("intro") or name == "S001":
            continue
        if name in REQUIRED and not (OUT / "plates" / f"{name}.png").exists():
            continue
        plate_name = f"{name}.png" if name in REQUIRED else shot["plate"]
        if name in REQUIRED:
            img = plates[plate_name]
        else:
            img = plates[shot["plate"]]
        cam = camera_for(name, img)
        views[name] = {"plate": img, "cam": cam, "name": plate_name if name in REQUIRED else shot["plate"]}
    return views


def render_still(view, fx, t: float) -> np.ndarray:
    if fx is not None and fx.active:
        return fx.render(t)
    return cover_sample(view["plate"], view["cam"].z, view["cam"].cx, view["cam"].cy)


def build_lights(views) -> dict:
    lights = {}
    work = OUT / "build" / "fx"
    for name, view in views.items():
        if name not in FX:
            continue
        spec = scale_fx(FX[name], *view["plate"].shape[1::-1])
        base = cover_sample(view["plate"], view["cam"].z, view["cam"].cx, view["cam"].cy)
        spec["cam"] = view["cam"]
        lights[name] = HouseLight(base, spec, seed=1611, work=work, key=name.lower())
    return lights


def save(frame: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(frame).save(path, quality=90)


def write_contact(frames: list[tuple[str, np.ndarray]], path: Path, cols: int = 3) -> None:
    if not frames:
        return
    thumb_w = 640
    labeled = []
    for title, frame in frames:
        scale = thumb_w / frame.shape[1]
        thumb = cv2.resize(frame, (thumb_w, int(round(frame.shape[0] * scale))), interpolation=cv2.INTER_AREA)
        bar = np.zeros((36, thumb.shape[1], 3), np.uint8)
        cv2.putText(bar, title, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (235, 230, 220), 1, cv2.LINE_AA)
        labeled.append(np.vstack([bar, thumb]))
    rows = []
    blank = np.zeros_like(labeled[0])
    for i in range(0, len(labeled), cols):
        chunk = labeled[i:i + cols]
        while len(chunk) < cols:
            chunk.append(blank)
        rows.append(np.hstack(chunk))
    sheet = np.vstack(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(sheet).save(path, quality=88)


def proofs(audio_mod) -> dict:
    audio, pictures, duration = audio_mod.build_timeline()
    names = {p["plate"] for p in pictures if not p.get("intro")}
    names.add("CB1.png")
    plates = load_plates(names)
    views = shot_views(pictures, plates)
    lights = build_lights(views)
    dest = OUT / "proofs"
    intro = Intro(plates["CB1.png"], np.asarray(Image.open(WORDMARK).convert("RGBA")))
    times = [0.2, 1.2, 2.4, 3.6, 4.8, 5.35, 6.6]
    intro_frames = []
    for t in times:
        frame = intro.frame(t)
        save(frame, dest / f"intro-{t:.2f}.jpg")
        intro_frames.append((f"intro {t:.2f}s", frame))
    write_contact(intro_frames, dest / "intro-contact.jpg", cols=4)
    intro_path = dest / "intro-preview.mp4"
    n_intro = int(round(7.5 * 30))
    writer = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{OUT_W}x{OUT_H}", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(intro_path),
    ], stdin=subprocess.PIPE)
    assert writer.stdin
    for i in range(n_intro):
        writer.stdin.write(np.ascontiguousarray(intro.frame(i / 30.0)).tobytes())
    writer.stdin.close()
    if writer.wait() != 0:
        raise SystemExit("intro preview encode failed")

    effect_frames = []
    report = {}
    for name, local_times in (("S002", (0.0, 0.6, 1.4)), ("S005", (0.0, 0.7, 1.6)), ("S008", (0.0, 0.8, 1.8))):
        view = views[name]
        light = lights.get(name)
        base = cover_sample(view["plate"], view["cam"].z, view["cam"].cx, view["cam"].cy)
        for t in local_times:
            frame = light.render(t) if light is not None else base
            save(frame, dest / f"{name}-{t:.1f}.jpg")
            effect_frames.append((f"{name} {t:.1f}s", frame))
        moved = light.render(1.25) if light is not None else base
        diff = np.abs(moved.astype(np.int16) - base.astype(np.int16)).max(axis=2)
        thirds = diff.shape[1] // 3
        report[name] = {
            "source_wh": [round(view["cam"].cw, 2), round(view["cam"].ch, 2)],
            "upscales": view["cam"].upscales,
            "z": round(view["cam"].z, 4),
            "mean_abs_diff_at_1.25s": round(float(diff.mean()), 3),
            "max_abs_diff_at_1.25s": int(diff.max()),
            "mean_abs_diff_thirds": [
                round(float(diff[:, :thirds].mean()), 2),
                round(float(diff[:, thirds:2 * thirds].mean()), 2),
                round(float(diff[:, 2 * thirds:].mean()), 2),
            ],
            "effects": light.active if light is not None else False,
        }
    write_contact(effect_frames, dest / "effects-contact.jpg", cols=3)

    clip = load_clip(str(CLIP))
    clip_frames = []
    for t in (0.0, 1.5, 3.0, 4.5):
        raw = clip.frames[clip.index_at(t)]
        fitted = clip.rgb_at(t)
        raw_up = cv2.resize(raw, (OUT_W, OUT_H), interpolation=cv2.INTER_NEAREST)
        pair = np.hstack([raw_up, fitted])
        save(pair, dest / f"s001-raw-vs-fit-{t:.1f}.jpg")
        clip_frames.append((f"S001 {t:.1f}s raw | fitted", pair))
    write_contact(clip_frames, dest / "s001-contact.jpg", cols=1)
    report["S001"] = {
        "decoded_frames": len(clip),
        "fps": clip.fps,
        "duration": round(clip.duration, 3),
        "size": list(clip.frames[0].shape[1::-1]),
        "camera": "source clip, no second move",
    }
    manifest = {
        "duration": round(duration, 3),
        "shots": [
            {"shot": p["shot"], "start": round(p["start"], 3), "stop": round(p["stop"], 3), "plate": p["plate"]}
            for p in pictures
        ],
        "proof": report,
        "required_replacements": REQUIRED,
        "missing": [k for k in REQUIRED if not (OUT / "plates" / f"{k}.png").exists()],
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return manifest


def missing_plates() -> list[str]:
    return [name for name in REQUIRED if not (OUT / "plates" / f"{name}.png").exists()]


def picture_at(t, pictures, views, lights, intro, clip):
    shot = pictures[-1]
    for item in pictures:
        if item["start"] <= t < item["stop"]:
            shot = item
            break
    name = shot["shot"]
    if shot.get("intro"):
        return intro.frame(t - shot["start"])
    local = t - shot["start"]
    if name == "S001":
        return clip.rgb_at(max(0.0, local))
    view = views[name]
    light = lights.get(name)
    if light is not None and light.active:
        return light.render(max(0.0, local))
    return cover_sample(view["plate"], view["cam"].z, view["cam"].cx, view["cam"].cy)


def encode_full(mod) -> None:
    missing = missing_plates()
    if missing:
        raise SystemExit(
            "Not encoding opening-sample-test-two.mp4. These plates are still the wrong picture: "
            + ", ".join(f"{name} ({REQUIRED[name]})" for name in missing)
        )
    mod.VO = CUT1 / "vo"
    mod.VAR = OUT
    mod.SCORE = VAR / "retrieved/score/Anabasis_I.mp3"
    audio, pictures, duration = mod.build_timeline()
    names = set()
    for shot in pictures:
        if shot.get("intro") or shot["shot"] == "S001":
            continue
        names.add(f"{shot['shot']}.png" if shot["shot"] in REQUIRED else shot["plate"])
    names.add("CB1.png")
    plates = load_plates(names)
    views = {}
    for shot in pictures:
        name = shot["shot"]
        if shot.get("intro") or name == "S001":
            continue
        plate_name = f"{name}.png" if name in REQUIRED else shot["plate"]
        img = plates[plate_name]
        views[name] = {"plate": img, "cam": camera_for(name, img), "name": plate_name}
    lights = build_lights(views)
    intro = Intro(plates["CB1.png"], np.asarray(Image.open(WORDMARK).convert("RGBA")))
    clip = load_clip(str(CLIP))
    (OUT / "build").mkdir(parents=True, exist_ok=True)
    voice = OUT / "build/voice.wav"
    mixed = OUT / "build/mixed.wav"
    mod.build_voice(audio, duration, voice)
    mod.mix(voice, duration, mixed)
    cues = mod.write_captions(audio, OUT / "captions.srt", OUT / "captions.vtt")
    silent = OUT / "build/picture.mp4"
    n = int(round(duration * 30))
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
        "-r", "30", "-i", "-", "-i", str(mixed),
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-t", f"{n / 30:.3f}", "-movflags", "+faststart", str(silent),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin
    try:
        for i in range(n):
            frame = picture_at(i / 30.0, pictures, views, lights, intro, clip)
            proc.stdin.write(np.ascontiguousarray(frame).tobytes())
            if i % 300 == 0:
                print("frame", i, "/", n, flush=True)
        proc.stdin.close()
    except BrokenPipeError:
        err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
        raise SystemExit(err[-2000:])
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise SystemExit(err[-2000:])
    final = OUT / "opening-sample-test-two.mp4"
    mod.run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(OUT / "captions.srt"),
        "-c", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
        "-movflags", "+faststart", str(final),
    ])
    integrated, peak = mod.ebur(final)
    print(json.dumps({"file": str(final), "cues": cues, "lufs": integrated, "peak": peak}))


def main() -> None:
    mod = cut_one()
    if "--timeline" in sys.argv:
        _audio, pictures, duration = mod.build_timeline()
        print(json.dumps({
            "duration": round(duration, 3),
            "shots": [
                {"shot": p["shot"], "start": round(p["start"], 3), "stop": round(p["stop"], 3)}
                for p in pictures
            ],
        }, indent=2))
        return
    if "--full" in sys.argv:
        encode_full(mod)
        return
    proofs(mod)


if __name__ == "__main__":
    main()
