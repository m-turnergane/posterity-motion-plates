#!/usr/bin/env python3
"""Second pass of the Edward II opening.

The nine accepted Oliver takes stay. The beheading line and the spoken
title may be replaced in this cut's voice directory when a calmer take
wins the comparison. The Act I bed is Penumbra from 0:30. The picture
path is a float resample, a scale-only push of a few percent, house flame
and smoke painted on the plate before that resample, a black-ink wordmark,
and a black ACT I card. Depth is not used on these shots, so the push is
the only camera move.

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

import copy
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

from motionplates.opening.camera import OUT_H, OUT_W, cover_window, smoothstep, warp  # noqa: E402
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
    # Rects below are pixels of the 2688x1520 replacement plates.
    "S003": {
        "native": True,
        "torches": [
            (2399, 304, 2470, 480),
            (2060, 400, 2110, 470),
            (1960, 590, 2020, 680),
            (1440, 350, 1500, 470),
            (840, 270, 900, 390),
            (510, 300, 640, 380),
            (60, 920, 180, 1070),
            (230, 1040, 320, 1220),
        ],
        "smoke": [
            {"type": "candle", "src": (2430, 340), "height": 80, "w1": 14, "w0": 3,
             "opacity": 0.16, "rise": 22, "lean": -4},
            {"type": "candle", "src": (120, 960), "height": 70, "w1": 12, "w0": 3,
             "opacity": 0.14, "rise": 20, "lean": 4},
        ],
        "protect": [[(60, 40), (820, 40), (820, 780), (60, 780)]],
        "spill_amp": 0.42,
        "radius_mult": 0.45,
    },
    "S007": {
        "native": True,
        "torches": [(970, 130, 1070, 270)],
        "smoke": [{"type": "torch", "src": (1015, 170), "height": 120, "w1": 18, "w0": 4,
                   "opacity": 0.22, "rise": 30, "lean": 4}],
        "protect": [[(1180, 80), (2100, 80), (2100, 980), (1180, 980)]],
        "spill_amp": 0.4,
        "radius_mult": 0.4,
    },
    "S007a": {
        "native": True,
        "torches": [(2500, 100, 2670, 340)],
        "smoke": [{"type": "torch", "src": (2590, 150), "height": 100, "w1": 16, "w0": 4,
                   "opacity": 0.18, "rise": 26, "lean": -6}],
        "protect": [[(700, 80), (2100, 80), (2100, 1400), (700, 1400)]],
        "spill_amp": 0.35,
        "radius_mult": 0.35,
    },
    "S009": {
        "native": True,
        "torches": [(790, 180, 870, 300), (1960, 390, 2030, 480)],
        "smoke": [
            {"type": "torch", "src": (825, 210), "height": 70, "w1": 12, "w0": 3,
             "opacity": 0.16, "rise": 20},
            {"type": "torch", "src": (1990, 420), "height": 60, "w1": 10, "w0": 3,
             "opacity": 0.14, "rise": 18},
        ],
        "protect": [
            [(40, 150), (720, 150), (720, 1450), (40, 1450)],
            [(1400, 500), (2400, 500), (2400, 1450), (1400, 1450)],
        ],
        "spill_amp": 0.35,
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
    if spec.get("native"):
        return spec
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


# Scale-only. z is (start, end). Absent shots ease 1.00 to 1.04 around the centre.
# S002 holds Kent's face and signet hand. S002b is the accepted Edward medium,
# shown when the second sentence of L02 names him. Neither window upscales.
FRAMING = {
    "S002": {"z": (1.25, 1.28), "cx": 0.38, "cy": 0.48},
    "S002b": {"z": (1.00, 1.025), "cx": 0.50, "cy": 0.50},
}
DEFAULT_Z = (1.00, 1.04)


def framing_at(plate: np.ndarray, shot: str, local: float, duration: float):
    spec = FRAMING.get(shot, {})
    z0, z1 = spec.get("z", DEFAULT_Z)
    cx = float(spec.get("cx", 0.5))
    cy = float(spec.get("cy", 0.5))
    span = duration if duration > 1e-6 else 1.0
    z = z0 + (z1 - z0) * smoothstep(local / span)
    h, w = plate.shape[:2]
    cam = cover_window(w, h, z, cx, cy)
    if cam.upscales:
        raise ValueError(f"{shot} zoom {z:.3f} upscales a {w}x{h} plate")
    return cam


def plate_cover(plate: np.ndarray):
    """Identity window: one plate pixel in, one plate pixel out."""
    h, w = plate.shape[:2]
    return cover_window(w, h, 1.0, 0.5, 0.5, out_w=w, out_h=h)


def _scale_delivery_sizes(spec: dict, k: float) -> dict:
    """Sizes authored against the 1080 frame, expressed in plate pixels.

    Positions are already plate pixels. Scaling the sizes by the rest
    window's plate-pixels-per-frame keeps the accepted flame size at the
    start of the shot, and the later warp carries them with the painting.
    """
    spec = copy.deepcopy(spec)
    for src in spec.get("offscreen", []):
        src["h"] = float(src.get("h", 70)) * k
        src["radius"] = float(src.get("radius", 900)) * k
    for src in spec.get("smoke", []):
        for key in ("height", "w0", "w1", "rise"):
            if key in src:
                src[key] = float(src[key]) * k
    if "protect_feather" in spec:
        spec["protect_feather"] = float(spec["protect_feather"]) * k
    return spec


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
        views[name] = {
            "plate": img,
            "shot": name,
            "name": plate_name if name in REQUIRED else shot["plate"],
            "duration": shot["stop"] - shot["start"],
        }
    return views


def render_still(view, fx, t: float) -> np.ndarray:
    return moving_frame(view, fx, t, view["duration"])


def fx_source(name: str) -> dict | None:
    if name == "S002b":
        return FX["S007a"]
    return FX.get(name)


def build_lights(views) -> dict:
    """Flame and smoke on the plate, then the camera resamples that plate."""
    lights = {}
    work = OUT / "build" / "fx"
    for name, view in views.items():
        source = fx_source(name)
        if source is None:
            continue
        rest = framing_at(view["plate"], name, 0.0, view["duration"])
        spec = _scale_delivery_sizes(scale_fx(source, *view["plate"].shape[1::-1]), rest.cw / rest.out_w)
        spec["cam"] = plate_cover(view["plate"])
        lights[name] = HouseLight(view["plate"], spec, seed=1611, work=work, key=name.lower())
    return lights


def moving_frame(view, light, local: float, duration: float) -> np.ndarray:
    local = max(0.0, local)
    cam = framing_at(view["plate"], view["shot"], local, duration)
    if light is not None and light.active:
        return warp(light.render(local), cam)
    return warp(view["plate"], cam)


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
    pictures = revise_pictures(audio_mod, audio, pictures)
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
        rest = framing_at(view["plate"], name, 0.0, view["duration"])
        base = moving_frame(view, None, 0.0, view["duration"])
        for t in local_times:
            frame = moving_frame(view, light, t, view["duration"])
            save(frame, dest / f"{name}-{t:.1f}.jpg")
            effect_frames.append((f"{name} {t:.1f}s", frame))
        moved = moving_frame(view, light, 1.25, view["duration"])
        diff = np.abs(moved.astype(np.int16) - base.astype(np.int16)).max(axis=2)
        thirds = diff.shape[1] // 3
        report[name] = {
            "source_wh": [round(rest.cw, 2), round(rest.ch, 2)],
            "upscales": rest.upscales,
            "z": round(rest.z, 4),
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
        "push": "none on the clip",
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


def revise_pictures(mod, audio, pictures):
    """Kent's face while he is named, then Edward when the line names Edward.

    The sealing clip is not extended. The second picture is the accepted
    throne medium already used later in the cut.
    """
    words = mod.words_of("L02")
    line = next(item for item in audio if item["id"] == "L02")
    split_rel = None
    seen_kent = False
    for start, _end, word in words:
        if word.startswith("Kent"):
            seen_kent = True
        elif seen_kent and word == "The":
            split_rel = start
            break
    if split_rel is None:
        raise SystemExit("L02 has no second sentence to cut on")
    split = line["speech_start"] + (split_rel - words[0][0])
    revised = []
    for shot in pictures:
        if shot["shot"] != "S002":
            revised.append(shot)
            continue
        if not (shot["start"] < split < shot["stop"]):
            raise SystemExit(f"L02 split {split:.3f} falls outside S002")
        kent = dict(shot)
        edward = dict(shot)
        kent["stop"] = split
        edward["start"] = split
        edward["shot"] = "S002b"
        edward["plate"] = "S007a.png"
        revised.extend((kent, edward))
    return revised


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
    return moving_frame(view, lights.get(name), local, shot["stop"] - shot["start"])


def prepare_vo() -> Path:
    """Nine locked takes, plus the title line that speaks only over the intro."""
    dest = OUT / "vo"
    dest.mkdir(parents=True, exist_ok=True)
    for src in (CUT1 / "vo").iterdir():
        link = dest / src.name
        if link.exists() or link.is_symlink():
            continue
        link.symlink_to(src)
    return dest


def attach_title_line(mod, audio: list, pictures: list, duration: float) -> tuple[list, float, float]:
    """Speak the brand and the title, then cut to the act card after the line.

    The nine accepted lines stay where they are. A longer title holds the
    parchment and pushes the card, and the shots after the card, so the
    line does not run under ACT I. The hyphen in the owner's wording is a
    pause, so the spoken text is two sentences.
    """
    title = OUT / "vo" / "TITLE.mp3"
    if not title.exists() or not (OUT / "vo" / "TITLE.alignment.json").exists():
        raise SystemExit("missing the title line in opening-sample-test-two/vo")
    intro = next(shot for shot in pictures if shot.get("intro"))
    words = mod.words_of("TITLE")
    first = words[0][0]
    spoken = words[-1][1] - first
    lead = 0.40
    start = intro["start"] + lead
    end = start + spoken
    card_local = (end - intro["start"]) + 0.25
    need = card_local + 1.80
    have = intro["stop"] - intro["start"]
    extra = max(0.0, need - have)
    if extra:
        boundary = intro["stop"]
        for item in audio:
            if item["speech_start"] >= boundary - 1e-3:
                item["speech_start"] += extra
                item["speech_end"] += extra
                item["file_at"] += extra
        for shot in pictures:
            if shot.get("intro"):
                shot["stop"] += extra
            elif shot["start"] >= boundary - 1e-3:
                shot["start"] += extra
                shot["stop"] += extra
        duration += extra
    if end > intro["start"] + card_local - 0.15:
        raise SystemExit(f"title line runs to {end:.2f}s, into the act card")
    audio.append({
        "id": "TITLE",
        "path": title,
        "file_at": start - first,
        "speech_start": start,
        "speech_end": end,
    })
    return audio, duration, card_local


def encode_full(mod) -> None:
    missing = missing_plates()
    if missing:
        raise SystemExit(
            "Not encoding opening-sample-test-two.mp4. These plates are still the wrong picture: "
            + ", ".join(f"{name} ({REQUIRED[name]})" for name in missing)
        )
    mod.VO = prepare_vo()
    mod.VAR = OUT
    # Penumbra, the Act I alternate. The first 30 s is a near-silent entry, so
    # the bed starts at the point named in SCORE-PLAN.
    mod.SCORE = VAR / "retrieved/score/Penumbra.mp3"
    mod.SCORE_START = 30.0
    audio, pictures, duration = mod.build_timeline()
    pictures = revise_pictures(mod, audio, pictures)
    audio, duration, card_at = attach_title_line(mod, audio, pictures, duration)
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
        views[name] = {
            "plate": img,
            "shot": name,
            "name": plate_name,
            "duration": shot["stop"] - shot["start"],
        }
    lights = build_lights(views)
    intro = Intro(plates["CB1.png"], np.asarray(Image.open(WORDMARK).convert("RGBA")), act_at=card_at)
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


def write_review() -> None:
    """Smaller review file. The crf-16 master is left where it is.

    Uncapped crf 18 of this cut is about 122 MB and does not fit the review
    volume. The rate cap keeps a high-quality 1080p file under that limit.
    """
    master = OUT / "opening-sample-test-two.mp4"
    dest = OUT / "opening-sample-test-two-review.mp4"
    if not master.exists():
        raise SystemExit(f"missing master {master}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(master),
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-maxrate", "8000k", "-bufsize", "16000k", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-c:s", "copy",
            "-movflags", "+faststart",
            str(dest),
        ],
        check=True,
    )
    print(dest)


def main() -> None:
    mod = cut_one()
    if "--timeline" in sys.argv:
        mod.VO = prepare_vo()
        audio, pictures, duration = mod.build_timeline()
        pictures = revise_pictures(mod, audio, pictures)
        audio, duration, card_at = attach_title_line(mod, audio, pictures, duration)
        title = next(item for item in audio if item["id"] == "TITLE")
        print(json.dumps({
            "duration": round(duration, 3),
            "act_card_at": round(card_at, 3),
            "title": {"start": round(title["speech_start"], 3), "end": round(title["speech_end"], 3)},
            "shots": [
                {"shot": p["shot"], "start": round(p["start"], 3), "stop": round(p["stop"], 3)}
                for p in pictures
            ],
        }, indent=2))
        return
    if "--full" in sys.argv:
        encode_full(mod)
        return
    if "--review" in sys.argv:
        write_review()
        return
    proofs(mod)


if __name__ == "__main__":
    main()
