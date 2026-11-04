#!/workspace/mpvenv/bin/python
"""POSTERITY standalone -- Jianwen ("DID THE EMPEROR WALK OUT OF THE FIRE?") -- ROUGH v2 build script (DRAFT, not yet run on plates).
COPY-ADAPTATION of build_rough_jianwen_v1.py (v1 untouched, stays reproducible), re-pointed at the owner-locked v2: VO vo/final-vo-oliver-jianwen-v2.wav (take t1),
narration raw/script-vo-tts.txt v2 (204 words), timing edit/timing_grid_v2.json (md5-locked; make_timing_grid_v2.py), plate map plate-prompts-v2b.md.
20 picture slots (K01-K19 + K01 REPRISE at S09) + the Xuanfu lit-window outro (baked title/tagline, used as-is). Opening: S01 K01 WIDE | S02A K02 WIDE | S02B K02 TIGHT
(title carried across both cuts, clean 2 f before K03); falls back to one wide S02 if the K02 tight crop would be < 70 % of the frame (FLAG). S09 = tight K01 crop
(falls back to a full-frame continued push 1.06->1.14, FLAG). S10/S11 cut on 'took' (owner 11:46). LEGEND label on S12 (K11) only. Fire / spill / atmosphere per plate via fx_jianwen_v2.py.
Audio: Oliver VO + Kevin MacLeod "Ripples" (CC BY 4.0) ducked, no SFX, -14 LUFS / TP <= -1.5 dBTP.
GUARDS: exits before ANY render if a plate is missing (exit 2) or its fx spec is still a template (exit 3); never overwrites the master/preview
(refuses, and ffmpeg runs with -n) or QC stills; checks disk free first (>= 4 GiB to render). Retired v1 title text is refused.
Plates dir: auto (plates-v2/ if it holds every plate, else plates-v1/) or --plates-dir. QC stills -> edit/qc/ (or --qc-dir).
2026-10-30 (owner 11:52 / 11:55): fx via fx_jianwen_v2b.py (real K01-K05 specs, framing, grade; fx_jianwen_v2.py untouched) + the LOCKED smoke_v2 layer
(engine-rnd/smoke/smoke_v2.py imported by path, md5-locked, never edited): per slot, in plate space, after PlateFX and before the grade/crop/cover/push, so it sits
ABOVE the plate and BELOW the title/LEGEND overlay and the ASS captions. Pre-rolled (established at frame 0), protect masks (faces, flames, water, land, lettering,
title band) at 0 px, per-slot zero-motion proof -> <build>/smoke_proof_<slot>.json. Smoke clock = per contiguous same-plate run (S02A->S02B continue; S09 restarts).
--smoke auto|on|off, --smoke-slots S09=off,..., --smoke-test CFG.json (2 s low-res check on any plate), --slots S01,S02A,.. (partial 360x640 previews of landed
slots only -> edit/previews_v2/<tag>/, never the master). Smoke templates still todo join the exit-3 refusal. Title band moved to topPercent 11 (K02 face at 20-40 %).
Captions: ASS start times ceil / end times floor to the centisecond + a frame-level check that no cue is on screen across a cut.
Run with /workspace/mpvenv/bin/python.
"""
import argparse, hashlib, json, math, subprocess, sys, os
from pathlib import Path
from multiprocessing import Pool
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).resolve().parent)); import fx_jianwen_v2b as FX   # v2b: real K01-K05 specs + smoke_v2 (locked, by path) + grade + framing; fx_jianwen_v2.py untouched
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="v2")
ap.add_argument("--tail", type=float, default=0.72, help="seconds held after speech end (89.28 + 0.72 = 90.00 s)")
ap.add_argument("--title", default="DID THE EMPEROR\nWALK OUT OF THE FIRE?", help="Chronicle Reveal text; use \\n for the line break (owner 11:31)")
ap.add_argument("--title-top-pct", type=float, default=FX.TITLE_TOP_PCT, help="title band centre, %% of frame height (v2b: 11 -- K02's face sits at 20-40 %%; band = +-7 %%)")
ap.add_argument("--title-font", type=int, default=78, help="line 2 'WALK OUT OF THE FIRE?' = 951 px at 78 (limit 994 px = 92 %% W)")
ap.add_argument("--title-anchor", type=int, default=0, help="title anchor frame (0 = grid: the K03 cut, f174)")
ap.add_argument("--title-test", action="store_true", help="title + LEGEND QC stills (1080x1920 + 360x640) on a dark card -> --qc-dir; needs no plates")
ap.add_argument("--qc-dir", default="", help="QC stills dir (default edit/qc); existing files are never overwritten")
ap.add_argument("--test-frames", default="", help="comma list of global frame numbers -> PNG stills in --qc-dir (no render; fx templates allowed)")
ap.add_argument("--fx-overlays", action="store_true", help="write fx source-detection overlays for every plate to --qc-dir (no render)")
ap.add_argument("--plates-dir", default="", help="plates folder (default auto: plates-v2/ if complete, else plates-v1/)")
ap.add_argument("--opening", choices=["auto", "split", "fallback"], default="auto", help="auto = split WIDE/TIGHT if the S02B crop is >= 70 %% of the K02 frame, else fallback")
ap.add_argument("--s02b-center", default="", help="override S02B crop centre 'x,y' (frame fractions of K02)"); ap.add_argument("--s02b-frac", type=float, default=0.0, help="override S02B crop fraction")
ap.add_argument("--reprise", choices=["auto", "crop", "fallback"], default="auto", help="auto = tight K01 crop at S09 if >= 70 %% of the frame, else full frame push 1.06->1.14")
ap.add_argument("--s09-center", default="", help="override S09 crop centre 'x,y'"); ap.add_argument("--s09-frac", type=float, default=0.0, help="override S09 crop fraction")
ap.add_argument("--legend-pos", default="", help="LEGEND cap-top position 'xPct,yPct' (v2b default 50,5.5 top-centre: xPct = label centre)")
ap.add_argument("--legend-size", type=int, default=0, help="LEGEND font px (grid default 36)")
ap.add_argument("--build-dir", default="", help="scratch dir (default edit/_build_v2_<tag>); use a FRESH dir for --audio-only (an existing mix.wav is reused)")
ap.add_argument("--jobs", type=int, default=6)
ap.add_argument("--audio-only", action="store_true", help="mix audio only (needs no plates)")
ap.add_argument("--bed-db", type=float, default=-17.5, help="bed gain before ducking")
ap.add_argument("--smoke", choices=["auto", "on", "off"], default="auto", help="smoke_v2 layer: auto = per plate/slot defaults (fx_jianwen_v2b.SMOKE/SLOT_SMOKE); on = also plates whose default is off (if they have emitters); off = none (FLAG)")
ap.add_argument("--smoke-slots", default="", help="per-slot override, e.g. 'S09=off,S02B=on'")
ap.add_argument("--smoke-test", default="", help="smoke_v2 config JSON (with 'plate'): 2 s low-res run of that plate through this build's pipeline (fx/smoke/cover/push/title/captions) -> --qc-dir")
ap.add_argument("--slots", default="", help="partial PREVIEW of these slots only (comma list or 'landed'): low-res per-slot mp4s -> edit/previews_v2/<tag>/ (never the master)")
ap.add_argument("--preview-size", default="360x640", help="preview size for --slots / --smoke-test")
ap.add_argument("--proof-every", type=int, default=15, help="smoke zero-motion proof every N frames")
ARGS = ap.parse_args()

E = Path("/workspace/posterity/standalones/jianwen"); EDIT = E / "edit"; VOD = E / "vo"
REND = E / "renders"   # owner 12:58: Rough v1 -> J/renders/ (never overwrites)
BUILD = Path(ARGS.build_dir) if ARGS.build_dir else EDIT / f"_build_v2_{ARGS.tag}"; CLIPS = BUILD / "clips"; AUD = BUILD / "audio"
QC = Path(ARGS.qc_dir) if ARGS.qc_dir else EDIT / "qc"
MASTER = REND / f"posterity-jianwen-v2-ROUGH-{ARGS.tag}.mp4"; PREVIEW = REND / f"posterity-jianwen-v2-ROUGH-{ARGS.tag}-preview.mp4"
GRID = EDIT / "timing_grid_v2.json"; GRID_MD5 = "3ac61225fd91c5fea1c1012f212c3e8a"   # 11:52: "Zhu Di" merged into the S10 cue
W, H, FPS, UP = 1080, 1920, 30, 2
VO_SRC = VOD / "final-vo-oliver-jianwen-v2.wav"; VO_MD5 = "a9eb59d4c4cc4d69d5c5ef075d988140"           # take t1, owner-locked
WORDS_JSON = VOD / "final-vo-oliver-jianwen-v2_words.json"; WORDS_MD5 = "5253aaec40374caae0ceb765085fb737"
SCRIPT = E / "raw" / "script-vo-tts.txt"; SCRIPT_MD5 = "851ddfb4cafb463d292861f5215a6cff"
MUSIC = E / "score" / "macleod_ripples.mp3"; MUSIC_MD5 = "39519d6e21a54a16d209619f27050da1"   # Kevin MacLeod "Ripples", CC BY 4.0 (edit/MUSIC-CREDIT.md)
# no SFX: no battle plates in this episode
FONT_DIR = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/"; F_SEMI = FONT_DIR + "SourceSerifPro-Semibold.ttf"
ENC_INTER = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "8", "-preset", "fast"]
ENC_FINAL = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-profile:v", "high"]

def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
assert md5f(VO_SRC) == VO_MD5, "VO changed"; assert md5f(SCRIPT) == SCRIPT_MD5, "script changed"; assert md5f(MUSIC) == MUSIC_MD5
assert md5f(WORDS_JSON) == WORDS_MD5, "alignment changed"; assert md5f(GRID) == GRID_MD5, "timing grid changed (regenerate + update GRID_MD5)"
G = json.load(open(GRID)); assert G["version"] == "v2"
words = json.load(open(WORDS_JSON))["words"]
DISP = SCRIPT.read_text().split(); assert len(DISP) == len(words) == 204
def norm(s): return " ".join(x.strip(".,;:?!\"'").lower() for x in s.split())
assert norm(" ".join(DISP)) == norm(" ".join(w["word"] for w in words))
def join_disp(idx): return " ".join(DISP[i] for i in idx)
def fob(t): return int(math.floor(t * FPS + 1e-6))
SPEECH_END = 89.28   # measured on take t1; = G["speech_end"]
assert SPEECH_END == G["speech_end"] and abs(ARGS.tail - G["tail"]) < 1e-9, "tail / speech end differ from grid v2"
TAIL = ARGS.tail

# ------------------------------------------------------------------ retired-title guard (owner 11:31: NEVER use the v1 title anywhere)
_BANNED_MD5 = "301e757783cb3cc5ef79030a79167800"   # md5 of the retired v1 title (lower-case words, no punctuation)
_t = norm(ARGS.title.replace("\\n", " ").replace("\n", " "))
assert hashlib.md5(_t.encode()).hexdigest() != _BANNED_MD5 and "walked" not in _t, "retired title text: not allowed (owner 11:31)"

# ------------------------------------------------------------------ plates dir: auto-detect (owner: plates land in plates-v1/)
PLATE_NAMES = sorted({g["plate"] for g in G["slots"]})
def pick_plates():
    if ARGS.plates_dir: return Path(ARGS.plates_dir), "--plates-dir"
    for d in (E / "plates-v2", E / "plates-v1"):
        if d.is_dir() and all((d / n).is_file() for n in PLATE_NAMES): return d, "auto: complete"
    for d in (E / "plates-v2", E / "plates-v1"):
        if d.is_dir(): return d, "auto: INCOMPLETE"
    return E / "plates-v1", "auto: no plates folder yet"
PL, PL_WHY = pick_plates(); print(f"plates dir: {PL} ({PL_WHY})")

# ------------------------------------------------------------------ slots from timing_grid_v2.json (cut rule applied there); anchors / z from the grid (placeholders until plates land)
P = lambda n: PL / n
MIN_CROP = 0.70                                     # a tight crop below ~70 % of the plate frame goes soft at 1080x1920
GS = {g["slot"]: g for g in G["slots"]}
def crop_arg(base, c_arg, f_arg):
    c = dict(base)
    if c_arg: c["center"] = [float(v) for v in c_arg.split(",")]
    if f_arg: c["frac"] = f_arg
    return c
FRM = FX.FRAMING   # v2b: anchors + crops set on the real plates (grid values were placeholders)
S02B_CROP = crop_arg({**GS["S02B"]["crop"], **FRM.get("S02B", {}).get("crop", {})}, ARGS.s02b_center, ARGS.s02b_frac)
S09_CROP = crop_arg({**GS["S09"]["crop"], **FRM.get("S09", {}).get("crop", {})}, ARGS.s09_center, ARGS.s09_frac)
OPENING_MODE = ARGS.opening if ARGS.opening != "auto" else ("split" if S02B_CROP["frac"] >= MIN_CROP else "fallback")
REPRISE_MODE = ARGS.reprise if ARGS.reprise != "auto" else ("crop" if S09_CROP["frac"] >= MIN_CROP else "fallback")
FLAGS = []
FB = G["fallback"]
grid_slots = [dict(g) for g in G["slots"]]
if OPENING_MODE == "fallback":
    why = "forced by --opening fallback" if ARGS.opening == "fallback" else f"S02B crop frac {S02B_CROP['frac']:.2f} < {MIN_CROP}"
    FLAGS.append(f"FLAG opening FALLBACK ({why}): one WIDE K02 S02 {FB['opening']['S02']['f0'] / FPS:.3f}-{FB['opening']['S02']['f1'] / FPS:.3f} s, push 1.00->{FB['opening']['S02']['z_end']}; only ONE cut in the first 5 s")
    a = GS["S02A"]
    s02 = dict(a, slot="S02", f0=FB["opening"]["S02"]["f0"], f1=FB["opening"]["S02"]["f1"], z_end=FB["opening"]["S02"]["z_end"], framing="wide", crop=None)
    i = [k for k, g in enumerate(grid_slots) if g["slot"] == "S02A"][0]; grid_slots[i:i + 2] = [s02]
CROPS = {"S02B": S02B_CROP} if OPENING_MODE == "split" else {}
if REPRISE_MODE == "crop": CROPS["S09"] = S09_CROP
else:
    why = "forced by --reprise fallback" if ARGS.reprise == "fallback" else f"S09 crop frac {S09_CROP['frac']:.2f} < {MIN_CROP}"
    FLAGS.append(f"FLAG S09 reprise FALLBACK ({why}): full K01 frame, push {FB['reprise']['z_start']}->{FB['reprise']['z_end']}")
    i = [k for k, g in enumerate(grid_slots) if g["slot"] == "S09"][0]
    grid_slots[i] = dict(grid_slots[i], crop=None, framing="full", z_start=FB["reprise"]["z_start"], z_end=FB["reprise"]["z_end"])
def crop_box(plate_size, c):   # relative crop (frac of the plate frame, 9:16 kept) -> pixel box, clamped inside the plate
    pw, ph = plate_size; cw, ch = pw * c["frac"], ph * c["frac"]; cx, cy = c["center"][0] * pw, c["center"][1] * ph
    l = min(max(cx - cw / 2, 0), pw - cw); t = min(max(cy - ch / 2, 0), ph - ch)
    return (int(round(l)), int(round(t)), int(round(l + cw)), int(round(t + ch)))
segs = []
for g in grid_slots:
    wi = [i for i, w in enumerate(words) if abs(w["start"] - g["first_word_t"]) < 1e-6][0]
    segs.append(dict(id=g["slot"], plate=str(P(g["plate"])), first_wi=wi, first_word=DISP[wi], crop=None, crop_rel=CROPS.get(g["slot"]),
                     framing=g.get("framing", "full"), anchor=tuple(FRM.get(g["slot"], FRM.get("S02A", {}) if g["slot"] == "S02" else {}).get("anchor", g["anchor"])), f0=g["f0"], f1=g["f1"], z_start=FRM.get(g["slot"], {}).get("z_start", g["z_start"]), z_end=FRM.get(g["slot"], {}).get("z_end", g["z_end"]), motion=g["motion"]))   # owner 12:58: v2b FRAMING may override z (OUTRO static hold)
TOTAL_F = fob(SPEECH_END + TAIL); assert TOTAL_F == G["total_f"] == segs[-1]["f1"] == 2700
for k, s in enumerate(segs):
    assert s["f1"] == (segs[k + 1]["f0"] if k + 1 < len(segs) else TOTAL_F)
    s["frames"] = s["f1"] - s["f0"]; s["start"] = s["f0"] / FPS; s["end"] = s["f1"] / FPS; s["duration"] = s["frames"] / FPS
    ws = [i for i, w in enumerate(words) if s["start"] - 1e-6 <= w["start"] < s["end"]]
    s["vo"] = join_disp(ws)
SEG = {s["id"]: s for s in segs}; OUTRO_T = SEG["OUTRO"]["start"]
for k, s in enumerate(segs):   # smoke clock: per contiguous same-plate run (S02A -> S02B continues; S09 restarts)
    s["run_f0"] = segs[k - 1]["run_f0"] if k and segs[k - 1]["plate"] == s["plate"] else s["f0"]
assert sum(1 for s in segs if s["id"] != "OUTRO") == (21 if OPENING_MODE == "split" else 20)
# ---- duration rules: opening 1.5-2.5 s per cut with >= 2 cuts in the first 5 s (split); every other shot >= 3 s except the flagged S09 quick callback; outro 4.5-5 s ending 89.8-90.2 s
OPENING = {"S01", "S02A", "S02B"} if OPENING_MODE == "split" else {"S01", "S02"}
KNOWN_SHORT = {"S09"}   # owner 11:46: K01 reprise stays a 2.33 s quick callback (flagged)
SHORT = [(s["id"], round(s["duration"], 3)) for s in segs if s["duration"] < 3.0 and s["id"] not in OPENING and s["id"] != "OUTRO"]
assert all(sid in KNOWN_SHORT for sid, _ in SHORT), f"shots under 3 s outside the opening: {SHORT}"
for sid, d in SHORT: FLAGS.append(f"FLAG {sid} {d:.3f} s < 3 s (known: quick K01 callback, owner 11:46)")
assert SEG["S10"]["duration"] >= 3.0 and SEG["S11"]["duration"] >= 3.0 and SEG["S11"]["first_word"] == "took", "S10/S11 must cut on 'took' (owner 11:46)"
if OPENING_MODE == "split":
    OPEN_BAD = [(s["id"], round(s["duration"], 3)) for s in segs if s["id"] in OPENING and not (1.5 <= s["duration"] <= 2.5)]
    assert not OPEN_BAD, f"opening shots outside 1.5-2.5 s: {OPEN_BAD}"
    assert sum(1 for s in segs if 0 < s["f0"] < 5 * FPS) >= 2, "need >= 2 cuts in the first 5 s"
OUT = SEG["OUTRO"]; assert 4.5 <= OUT["duration"] <= 5.0 and 89.8 <= OUT["end"] <= 90.2, (OUT["duration"], OUT["end"])
print(f"opening mode: {OPENING_MODE}" + (f" (S02B crop centre {S02B_CROP['center']}, frac {S02B_CROP['frac']})" if OPENING_MODE == "split" else "")
      + f" | reprise mode: {REPRISE_MODE}" + (f" (S09 crop centre {S09_CROP['center']}, frac {S09_CROP['frac']})" if REPRISE_MODE == "crop" else ""))
for s in segs: print(f"  {s['id']:5} {Path(s['plate']).name:42} f{s['f0']:5d} {s['start']:7.3f}-{s['end']:7.3f} {s['duration']:6.3f}s  '{s['vo']}'")

# ------------------------------------------------------------------ house helpers (Germanicus v5b, verbatim)
def prepare_cover(im, up=UP):
    im = im.convert("RGB"); tw, th = W * up, H * up; sw, sh = im.size
    sc = max(tw / sw, th / sh); nw, nh = int(math.ceil(sw * sc)), int(math.ceil(sh * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS); l, t = (nw - tw) // 2, (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))
def cam(seg, u, t):
    z0, z = seg["z_start"], seg["z_end"]; s = z0 * (z / z0) ** u; ax, ay = seg["anchor"]
    cx = ax * W * (1 - 1 / s) + W / (2 * s); cy = ay * H * (1 - 1 / s) + H / (2 * s); hw, hh = W / (2 * s), H / (2 * s)
    return s, min(max(cx, hw), W - hw), min(max(cy, hh), H - hh)
def cam_frame(base, seg, u, t):
    bw, bh = base.size; s, cx, cy = cam(seg, u, t); k = bw / W; ww, wh = bw / s, bh / s; l, tp = cx * k - ww / 2, cy * k - wh / 2
    big = base.transform((W * 2, H * 2), Image.Transform.AFFINE, (ww / (2 * W), 0, l, 0, wh / (2 * H), tp), resample=Image.Resampling.BICUBIC)
    return Image.fromarray(cv2.resize(np.asarray(big), (W, H), interpolation=cv2.INTER_AREA))
def base_2x(seg):
    im = Image.open(seg["plate"]).convert("RGB")
    if seg["crop"]: im = im.crop(seg["crop"])
    return prepare_cover(im)
def _ss(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ Chronicle Reveal (Germanicus v5b, verbatim except text/position/timing; via Jianwen v1)
TITLE_LINE_H = 0.84
def cubic_bezier(x1, y1, x2, y2):
    def bez(t, a, b): return 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3
    def f(x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if bez(mid, x1, x2) < x: lo = mid
            else: hi = mid
        return bez((lo + hi) / 2, y1, y2)
    return f
E_DRAG = cubic_bezier(0.33, 0.0, 0.2, 1); E_IN = cubic_bezier(0.22, 1, 0.36, 1); E_OUT = cubic_bezier(0.4, 0, 0.2, 1)
LIN = lambda x: min(max(x, 0.0), 1.0)
def interp(f, a, b, v0, v1, ease=LIN):
    p = (1.0 if f >= b else 0.0) if b <= a else min(max((f - a) / (b - a), 0.0), 1.0)
    return v0 + (v1 - v0) * ease(p)
_S04 = ARGS.title_anchor or G["title"]["anchor_f"]   # v2: Chronicle Reveal v3.2b anchored on the K03 cut (f174): hold f42-142, exit f142-162, stroke clears f151-172
assert _S04 - 2 < SEG["S03"]["f0"] + 1 and _S04 <= SEG["S03"]["f0"], "title must be clean before the K03 cut"
_OPEN_CUTS = [s["f0"] for s in segs if s["id"] in OPENING and s["f0"] > 0]
assert all(42 <= f < _S04 - 32 for f in _OPEN_CUTS), f"opening cuts {_OPEN_CUTS} must land inside the title hold f42-{_S04 - 32}"
CR = dict(title=ARGS.title.replace("\\n", "\n"), fontSize=ARGS.title_font, color=(243, 237, 224), topPercent=ARGS.title_top_pct, offsetX=-16,
          strokeEnterStart=8, strokeEnterEnd=26, strokeClearStart=_S04 - 23, strokeClearEnd=_S04 - 2,
          manifestStart=14, manifestEnd=42, exitStart=_S04 - 32, exitEnd=_S04 - 12, bandHeightPercent=14,
          widthPercent=94, peakOpacity=0.92, fill="#5A1A18", edge="#3A0E0C", mid="#6E2A1C",
          scaleFrom=0.92, scaleTo=1.0, exitScaleTo=0.94, settleYPx=4, afterEdgeLagFrames=2,
          letterSettleFrames=12, trackingEm=0.02, nudgeY=-4)
def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
def smooth_noise(h, w, cell_y, cell_x, seed):
    rng = np.random.default_rng(seed); gh, gw = max(2, int(h / cell_y) + 3), max(2, int(w / cell_x) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC), np.float32) / 255.0
def build_strike_rgba():
    bw = int(round(W * CR["widthPercent"] / 100)); bh = int(round(H * CR["bandHeightPercent"] / 100))
    topY = [78, 62, 71, 55, 68, 48, 60, 52, 70, 58, 65, 50, 72, 56, 64, 54, 75, 60, 70, 66, 80]
    botY = [128, 142, 135, 150, 138, 155, 140, 148, 132, 145, 138, 152, 130, 144, 136, 150, 125, 140, 134, 138, 122]
    def chain(ys):
        m = len(ys); xs_out, ys_out = [], []
        for k in range(1, m):
            x0, x1 = (k - 1) / (m - 1) * 1000, k / (m - 1) * 1000; cx, cy = (x0 + x1) / 2, ys[k - 1]
            for t in np.linspace(0, 1, 40):
                xs_out.append((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1); ys_out.append((1 - t) ** 2 * ys[k - 1] + 2 * (1 - t) * t * cy + t * t * ys[k])
        return np.array(xs_out), np.array(ys_out)
    xt, yt = chain(topY); xb, yb = chain(botY); xs = np.arange(bw) / bw * 1000
    top = np.interp(xs, xt, yt) / 200 * bh; bot = np.interp(xs, xb, yb) / 200 * bh
    yy = np.arange(bh)[:, None].astype(np.float32)
    dy = (smooth_noise(bh, bw, 17, 29, 3) - 0.5) * 2 * 4.4; dx_n = (smooth_noise(bh, bw, 17, 29, 4) - 0.5) * 2 * 3.3; yyd = yy + dy
    fringe = smooth_noise(bh, bw, 3, 9, 7)
    m_top = np.clip((yyd - top[None, :]) / 2.0 + 0.5, 0, 1); m_bot = np.clip((bot[None, :] - yyd) / 2.0 + 0.5, 0, 1); mask = m_top * m_bot
    edge_zone = np.clip(1 - np.minimum(np.abs(yyd - top[None, :]), np.abs(yyd - bot[None, :])) / 10.0, 0, 1)
    mask = mask * (1 - edge_zone * 0.55 * (fringe > 0.62))
    xx = np.arange(bw)[None, :].astype(np.float32) + dx_n; endfade = np.clip(xx / 6.0, 0, 1) * np.clip((bw - 1 - xx) / 6.0, 0, 1); mask = mask * endfade
    t = np.clip((yy / bh * 200 - 48) / (155 - 48), 0, 1)
    stops = [(0.0, CR["edge"], 0.55), (0.18, CR["mid"], 0.95), (0.42, CR["fill"], 1.0), (0.58, CR["fill"], 1.0), (0.78, CR["mid"], 0.92), (1.0, CR["edge"], 0.5)]
    so = np.array([s[0] for s in stops]); sc = np.stack([hexrgb(s[1]) for s in stops]); sa = np.array([s[2] for s in stops]); tt = t[:, 0]
    col = np.stack([np.interp(tt, so, sc[:, c]) for c in range(3)], -1)[:, None, :].repeat(bw, 1); alp = np.interp(tt, so, sa)[:, None].repeat(bw, 1)
    u = np.arange(bw) / (bw - 1)
    lg_c = np.stack([np.interp(u, [0, .08, .5, .92, 1], [0x2A, 0x5A, 0x7A, 0x5A, 0x2A]), np.interp(u, [0, .08, .5, .92, 1], [0x0A, 0x1A, 0x32, 0x1A, 0x0A]),
                     np.interp(u, [0, .08, .5, .92, 1], [0x08, 0x18, 0x20, 0x18, 0x08])], -1)
    lg_a = np.interp(u, [0, .08, .5, .92, 1], [0.35, 0, 0.12, 0, 0.4]); col = col * (1 - lg_a[None, :, None]) + lg_c[None, :, :] * lg_a[None, :, None]
    Y, X = np.mgrid[0:bh, 0:bw].astype(np.float32)
    for cx, cy, r, c, a in [(0.28, 0.45, 0.38, "#2E0C0A", 0.45), (0.68, 0.58, 0.32, "#8A3A28", 0.28), (0.48, 0.40, 0.55, "#4A1410", 0.20)]:
        d = np.sqrt(((X / bw - cx) / r) ** 2 + ((Y / bh - cy) / r) ** 2); k = np.clip(1 - d, 0, 1) * a
        col = col * (1 - k[..., None]) + hexrgb(c)[None, None, :] * k[..., None]
    rng = np.random.default_rng(11); grain = rng.random((bh, bw)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    streak = smooth_noise(bh, bw, 2.5, 90, 21); mult = 1 - 0.22 * (grain - 0.5) * 2 * 0.5 - 0.18 * (streak - 0.5)
    col = np.clip(col * mult[..., None], 0, 255); a = np.clip(mask * alp, 0, 1)
    return Image.fromarray(np.dstack([col, a * 255]).astype(np.uint8), "RGBA"), bw, bh
_STRIKE = None
def strike_layer(frame):
    global _STRIKE
    s0, s1, c0, c1 = CR["strokeEnterStart"], CR["strokeEnterEnd"], CR["strokeClearStart"], CR["strokeClearEnd"]
    if frame < s0 or frame >= c1: return None
    if _STRIKE is None: _STRIKE = build_strike_rgba()
    img, bw, bh = _STRIKE
    lead = interp(frame, s0, s1, 0, 1, E_DRAG); clr = interp(frame, c0, c1, 0, 1, E_OUT); vis = lead * (1 - clr)
    op = CR["peakOpacity"] * interp(frame, c0, c1, 1, 0, E_OUT)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); vw = int(round(bw * vis))
    if vw <= 0: return None
    piece = img.crop((0, 0, vw, bh)); a = np.asarray(piece.getchannel("A"), np.float32) * op; piece.putalpha(Image.fromarray(a.astype(np.uint8)))
    x0 = int(round((W - bw) / 2 + CR["offsetX"])); y0 = int(round(H * CR["topPercent"] / 100 - bh / 2)); layer.alpha_composite(piece, (x0, y0))
    if 0 < lead < 1:
        tip = interp(lead, 0, 0.15, 0.35, 0.55) if lead < 0.15 else (interp(lead, 0.15, 0.85, 0.55, 0.4) if lead < 0.85 else interp(lead, 0.85, 1, 0.4, 0))
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(bl)
        cx = x0 + vw; cy = y0 + bh / 2; rx = 28 / 1000 * bw; ry = 42 / 200 * bh
        dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=tuple(hexrgb(CR["mid"]).astype(int)) + (int(255 * tip * 0.55 * op),))
        layer.alpha_composite(bl.filter(ImageFilter.GaussianBlur(6)))
    return layer
_GLYPHS = None
def title_layout():
    global _GLYPHS
    if _GLYPHS is not None: return _GLYPHS
    fs = CR["fontSize"]; font = ImageFont.truetype(F_SEMI, fs); lines = CR["title"].split("\n"); track = CR["trackingEm"] * fs
    asc, desc = font.getmetrics(); line_h = TITLE_LINE_H * fs; gap = round(fs * 0.04); block_h = len(lines) * line_h + (len(lines) - 1) * gap
    cy = H * CR["topPercent"] / 100 + CR["nudgeY"]; top = cy - block_h / 2
    flat = sum(len(l) for l in lines); last = max(flat - 1, 1); glyphs = []; gi = 0; cap_h = font.getbbox("H")[3] - font.getbbox("H")[1]
    for li, line in enumerate(lines):
        widths = [font.getlength(ch) for ch in line]; total = sum(widths) + track * (len(line) - 1)
        assert total <= W * 0.92, f"title line too wide: {line}"
        x = W / 2 + CR["offsetX"] - total / 2; line_mid = top + li * (line_h + gap) + line_h / 2
        for ch, wch in zip(line, widths):
            if ch != " ":
                pad = 12; spr = Image.new("RGBA", (int(wch + 2 * pad), asc + desc + 2 * pad), (0, 0, 0, 0)); sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
                ImageDraw.Draw(sh).text((pad, pad + 2), ch, font=font, fill=(0, 0, 0, 115)); spr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.0)))
                ImageDraw.Draw(spr).text((pad, pad), ch, font=font, fill=CR["color"] + (255,))
                hb = font.getbbox("H"); y_img = line_mid - (hb[1] + cap_h / 2) - pad
                glyphs.append({"spr": spr, "x": x - pad, "y": y_img, "lx": gi / last})
            x += wch + track; gi += 1
    _GLYPHS = glyphs; return glyphs
def title_layer(frame):
    c = CR
    if frame >= c["exitEnd"]: return None
    lead = interp(frame, c["strokeEnterStart"], c["strokeEnterEnd"], 0, 1, E_DRAG)
    if frame < c["manifestStart"] and lead <= 0: return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); any_on = False
    for g in title_layout():
        lx = g["lx"]; edge_pass = c["strokeEnterStart"] + lx * (c["strokeEnterEnd"] - c["strokeEnterStart"])
        li0 = max(c["manifestStart"], edge_pass + c["afterEdgeLagFrames"]); li1 = min(c["manifestEnd"], li0 + c["letterSettleFrames"])
        op = interp(frame, li0, li1, 0, 1, E_IN); y = interp(frame, li0, li1, c["settleYPx"], 0, E_IN); sc = interp(frame, li0, li1, c["scaleFrom"], c["scaleTo"], E_IN)
        if c["manifestEnd"] <= frame < c["exitStart"]: op, y, sc = 1.0, 0.0, c["scaleTo"]
        if frame >= c["exitStart"]:
            span = c["exitEnd"] - c["exitStart"]; le0 = c["exitStart"] + (1 - lx) * span * 0.45; le1 = min(c["exitEnd"], le0 + span * 0.55)
            op = op * interp(frame, le0, le1, 1, 0, E_OUT); y = interp(frame, le0, le1, 0, -c["settleYPx"] * 0.85, E_OUT); sc = interp(frame, le0, le1, c["scaleTo"], c["exitScaleTo"], E_OUT)
        if op < 0.01: continue
        spr = g["spr"]; sw, sh = spr.size
        if abs(sc - 1) > 1e-3:
            nw, nh = max(1, round(sw * sc)), max(1, round(sh * sc)); spr2 = spr.resize((nw, nh), Image.Resampling.LANCZOS); ox = g["x"] + (sw - nw) * 0.5; oy = g["y"] + (sh - nh) * 0.7
        else: spr2 = spr; ox, oy = g["x"], g["y"]
        a = np.asarray(spr2.getchannel("A"), np.float32) * op; spr2 = spr2.copy(); spr2.putalpha(Image.fromarray(a.astype(np.uint8)))
        layer.alpha_composite(spr2, (int(round(ox)), int(round(oy + y)))); any_on = True
    return layer if any_on else None
# ------------------------------------------------------------------ LEGEND label (S12 / K11 only): small, quiet, TOP-CENTRE (owner 12:13); smoothstep fade + 6 px rise
LG = dict(G["legend"]); assert LG["slot"] == "S12" and LG["text"] == "LEGEND"
LG.update(getattr(FX, "LEGEND", {}))   # owner 12:13: v2b sets TOP-CENTRE (align=center -> xPct is the label CENTRE)
if ARGS.legend_pos: LG["xPct"], LG["yPct"] = [float(v) for v in ARGS.legend_pos.split(",")]
if ARGS.legend_size: LG["fontSize"] = ARGS.legend_size
_LEG = None
LEGEND_ON = bool(LG.get("enabled", True))   # owner 12:59: LEGEND removed from the cut -> False: no sprite is built, no layer composited (no text pixels)
def legend_sprite():
    global _LEG
    assert LEGEND_ON, "LEGEND is disabled (owner 12:59)"
    if _LEG is not None: return _LEG
    fs = LG["fontSize"]; font = ImageFont.truetype(FONT_DIR + LG["font"], fs); track = LG["trackingEm"] * fs; txt = LG["text"]
    widths = [font.getlength(ch) for ch in txt]; total = sum(widths) + track * (len(txt) - 1)
    hb = font.getbbox("H"); cap_h = hb[3] - hb[1]; pad = 16; rule_y = pad + cap_h + LG["rule"]["gap_px"]
    sw, sh = int(math.ceil(total + 2 * pad)), int(rule_y + LG["rule"]["px"] + pad + 4)
    def draw(col, a_txt, a_rule, dy=0):
        im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = pad
        for ch, wch in zip(txt, widths): d.text((x, pad - hb[1] + dy), ch, font=font, fill=tuple(col) + (a_txt,)); x += wch + track
        d.rectangle((pad, rule_y + dy, pad + total - track * 0, rule_y + dy + LG["rule"]["px"] - 1), fill=tuple(col) + (a_rule,))
        return im
    rule_a = int(round(255 * min(1.0, LG["rule"]["opacity"] / LG["opacity"])))   # rule lands at 0.45 after the 0.80 layer opacity
    spr = draw((0, 0, 0), LG["shadow"]["alpha"], LG["shadow"]["alpha"], dy=2).filter(ImageFilter.GaussianBlur(LG["shadow"]["blur"]))
    spr.alpha_composite(draw(LG["color"], 255, rule_a)); _LEG = (spr, pad, total); return _LEG
def legend_layer(gf):
    if not LEGEND_ON: return None
    s = SEG["S12"]
    if not (s["f0"] <= gf < s["f1"]): return None
    i0, i1 = LG["in_f"]; o0, o1 = LG["out_f"]
    a_in = _ss((gf - i0) / max(i1 - i0, 1)); a = a_in * (1 - _ss((gf - o0) / max(o1 - o0, 1))) * LG["opacity"]
    if a < 0.005: return None
    spr, pad, _ = legend_sprite(); spr = spr.copy(); al = np.asarray(spr.getchannel("A"), np.float32) * a; spr.putalpha(Image.fromarray(al.astype(np.uint8)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x_left = W * LG["xPct"] / 100 - (_ / 2 if LG.get("align") == "center" else 0)
    layer.alpha_composite(spr, (int(round(x_left - pad)), int(round(H * LG["yPct"] / 100 - pad + LG["rise_px"] * (1 - a_in)))))
    return layer
def overlay_for(gf):
    ls = [l for l in (strike_layer(gf), title_layer(gf), legend_layer(gf)) if l is not None]
    if not ls: return None
    out = ls[0].copy()
    for x in ls[1:]: out.alpha_composite(x)
    return out

# ------------------------------------------------------------------ v1c: per-plate fire / spill / atmosphere (plate space) -> crop -> house cover -> StablePush
def make_fx(seg):
    seed = int(hashlib.md5(Path(seg["plate"]).name.encode()).hexdigest()[:6], 16)   # per PLATE: S02A + S02B (and S01 + S09 on K01) share fx seed + global clock -> fire/embers continue through the cut
    fx = FX.PlateFX(seg["plate"], seed=seed)   # Jianwen: the outro gets fx too (lettering excluded in its spec)
    return fx if fx.active() else None
def fx_base(fx, seg, gf, u):   # kept for reference (pre-smoke path); the build uses plate_frame()
    im = Image.fromarray(fx.render(gf / FPS, u))
    if seg["crop"]: im = im.crop(seg["crop"])
    return prepare_cover(im)

# ------------------------------------------------------------------ smoke_v2 layer (owner 11:52): plate space, after PlateFX, before grade/crop/cover/push -> under the title + captions
SMOKE_SLOT = {}
for kv in [x for x in ARGS.smoke_slots.split(",") if x.strip()]:
    k, v = kv.split("="); assert v.strip() in ("on", "off"), kv; SMOKE_SLOT[k.strip()] = v.strip() == "on"
if ARGS.smoke == "off": FLAGS.append("FLAG --smoke off: smoke_v2 layer disabled on every slot")
for k in SMOKE_SLOT: FLAGS.append(f"FLAG --smoke-slots {k}={'on' if SMOKE_SLOT[k] else 'off'}")
def smoke_status(seg):
    """('on'|'off'|'todo', why)"""
    if seg.get("smoke_cfg"): return "on", "--smoke-test"
    key = FX.plate_key(seg["plate"]); st, why = FX.smoke_state(key, seg["id"])
    if st == "todo": return ("off", "--smoke off") if ARGS.smoke == "off" else ("todo", why)
    if ARGS.smoke == "off": return "off", "--smoke off"
    on = st == "on" or (ARGS.smoke == "on" and bool(FX.SMOKE.get(key, {}).get("emitters")))
    if seg["id"] in SMOKE_SLOT: on = SMOKE_SLOT[seg["id"]]
    return ("on", "") if on and FX.SMOKE.get(key, {}).get("emitters") else ("off", why or "no emitters")
_CACHE = {}
def plate_rgb(path):
    if ("P", path) not in _CACHE: _CACHE[("P", path)] = np.ascontiguousarray(cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB))
    return _CACHE[("P", path)]
def get_fx(seg):
    k = ("fx", seg["id"])
    if k not in _CACHE: _CACHE[k] = make_fx(seg)
    return _CACHE[k]
def get_smoke(seg):
    k = ("sm", seg["id"])
    if k in _CACHE: return _CACHE[k]
    st, _ = smoke_status(seg)
    if st != "on": _CACHE[k] = None; return None
    sp = FX.SPECS.get(FX.plate_key(seg["plate"]), {})
    assert not sp.get("smoke"), f"double smoke: fx spec of {seg['plate']} has a legacy 'smoke' key and smoke_v2 is on"
    P0 = plate_rgb(seg["plate"]); Hh, Ww = P0.shape[:2]
    cfg = seg["smoke_cfg"] if seg.get("smoke_cfg") else FX.smoke_config(FX.plate_key(seg["plate"]), seg["id"], Ww, Hh)
    sc = FX.SM.SmokeScene(P0, cfg)
    guards = {n: FX.SM.poly_mask((Hh, Ww), [p], 0) > 0.5 for n, p in (cfg.get("guards") or {}).items()}
    _CACHE[k] = dict(sc=sc, allow=sc.allow_mask(), prot=sc.protect_bin > 0.5, guards=guards, n_em=len(sc.emitters)); return _CACHE[k]
def apply_smoke(S, img, t):
    sc = S["sc"]; keep = sc.Pf; sc.Pf = img.astype(np.float32)   # composite the locked emitters over the fx frame (emitters never read the plate)
    try: return sc.frame(t)
    finally: sc.Pf = keep
def plate_frame(seg, gf, u, proof=None, smoke=True):
    """plate-space frame: PlateFX -> smoke_v2 -> grade -> crop -> house cover (2x). proof: dict collecting zero-motion maxima."""
    fx = get_fx(seg); S = get_smoke(seg) if smoke else None; key = FX.plate_key(seg["plate"])
    if fx is None and S is None:
        k = ("static", seg["id"])
        if k not in _CACHE:
            im = Image.fromarray(FX.grade(plate_rgb(seg["plate"]), key))
            _CACHE[k] = prepare_cover(im.crop(seg["crop"]) if seg["crop"] else im)
        return _CACHE[k]
    img = fx.render(gf / FPS, u) if fx is not None else plate_rgb(seg["plate"])
    if S is not None:
        out = apply_smoke(S, img, (gf - seg["run_f0"]) / FPS)
        if proof is not None:
            d = np.abs(out.astype(np.int16) - img.astype(np.int16)).max(-1)
            proof["frames"] += 1; proof["max_outside_allow"] = max(proof["max_outside_allow"], int(d[~S["allow"]].max(initial=0)))
            proof["max_in_protect"] = max(proof["max_in_protect"], int(d[S["prot"]].max(initial=0)))
            proof["max_changed"] = max(proof["max_changed"], int(d.max()))
            for n, m in S["guards"].items(): proof["guards"][n] = max(proof["guards"].get(n, 0), int(d[m].max(initial=0)))
        img = out
    im = Image.fromarray(FX.grade(img, key))
    if seg["crop"]: im = im.crop(seg["crop"])
    return prepare_cover(im)

def render_segment(sid, clips=None, enc=None, proof_dir=None):
    seg = SEG[sid]; clips = clips or CLIPS; enc = enc or ENC_INTER; proof_dir = proof_dir or BUILD; dst = clips / f"{sid}.mp4"; CLIPS_ = clips
    if dst.exists(): return sid, -1
    tmp = CLIPS_ / f"{sid}.part.mp4"
    if tmp.exists(): tmp.unlink()   # own scratch from an interrupted run
    nfr = seg["frames"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-frames:v", str(nfr), "-an", *enc, "-r", str(FPS), str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    st, why = smoke_status(seg); proof = dict(slot=sid, plate=Path(seg["plate"]).name, smoke=st, why=why, every=ARGS.proof_every, frames=0, max_outside_allow=0, max_in_protect=0, max_changed=0, guards={})
    for fi in range(nfr):
        u = fi / max(nfr - 1, 1); t = fi / FPS; gf = seg["f0"] + fi
        b = plate_frame(seg, gf, u, proof if (st == "on" and fi % ARGS.proof_every == 0) else None)
        frame = cam_frame(b, seg, u, t); ov = overlay_for(gf)
        if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait(): raise SystemExit(f"encode fail {sid}")
    tmp.rename(dst)
    if st == "on":
        proof["zero_motion_ok"] = proof["max_outside_allow"] == 0 and proof["max_in_protect"] == 0 and all(v == 0 for v in proof["guards"].values())
        S = get_smoke(seg); proof["emitter_layers"] = S["n_em"]
        pj = Path(proof_dir) / f"smoke_proof_{sid}.json"; assert not pj.exists(), pj
        json.dump(proof, open(pj, "w"), indent=1)
        if not proof["zero_motion_ok"]: raise SystemExit(f"SMOKE ZERO-MOTION FAIL {sid}: {proof}")
    return sid, nfr

# ------------------------------------------------------------------ captions: grid v2 cues (word for word, <= 7 words, each clears 1 frame before the next cut); the L14 tagline is NOT captioned (baked on the outro)
def wrap_idx(tok_idx, maxc=24):
    if len(join_disp(tok_idx)) <= maxc: return [tok_idx]
    best = None
    for k in range(1, len(tok_idx)):
        sc = max(len(join_disp(tok_idx[:k])), len(join_disp(tok_idx[k:])))
        if best is None or sc < best[0]: best = (sc, k)
    return [tok_idx[:best[1]], tok_idx[best[1]:]]
def ass_cs(t, end=False):   # start -> ceil, end -> floor (centiseconds): a cue can only shrink inside its own shot, never cross a cut
    x = max(0.0, t) * 100; return int(math.floor(x + 1e-6)) if end else int(math.ceil(x - 1e-6))
def ass_time(t, end=False):
    cs = ass_cs(t, end); s, cs = divmod(cs, 100); m, s = divmod(s, 60); h, m = divmod(m, 60); return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
TAG_LINE = G["tagline_line"]; CAP_N = [i for i, w in enumerate(words) if w["line"] == TAG_LINE][0]; TAG_T = words[CAP_N]["start"]
assert abs(TAG_T - 85.23) < 0.01
spans = []; wi = 0
for c in G["captions"]:
    toks = c["text"].split(); assert DISP[wi:wi + len(toks)] == toks; spans.append((wi, wi + len(toks) - 1, c["start"], c["end"])); wi += len(toks)
assert wi == CAP_N, "captions must cover the VO exactly up to the tagline"
CUT_T = [s["start"] for s in segs[1:]]
TITLE_ON_S, TITLE_OFF_S = CR["strokeEnterStart"] / FPS, CR["exitEnd"] / FPS
ass = ["[Script Info]", f"Title: Posterity Jianwen v2 ROUGH {ARGS.tag}", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Default,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,400,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
cap_events = []; ttl = " " + norm(CR["title"].replace("\n", " ")) + " "
for a, b, st, en in spans:
    en = min(en, OUTRO_T)
    assert not any(st + 1e-6 < t < en - 1e-6 for t in CUT_T), f"caption straddles a cut: {join_disp(range(a, b + 1))}"
    cw = norm(join_disp(range(a, b + 1))).split()
    rep = any(" " + " ".join(cw[i:i + 3]) + " " in ttl for i in range(max(len(cw) - 2, 0)))
    hidden = st >= TITLE_ON_S - 0.3 and en <= TITLE_OFF_S and rep
    txt = r"{\fad(120,80)}" + r"\N".join(join_disp(ln) for ln in wrap_idx(list(range(a, b + 1))))   # ease in/out, never slammed
    ass.append(f"{'Comment' if hidden else 'Dialogue'}: 0,{ass_time(st)},{ass_time(en, True)},Default,,0,0,0,,{txt}")
    if not hidden:   # frame-level: every frame that shows this cue (start <= k/30 < end, libass rule) belongs to ONE shot
        c0, c1 = ass_cs(st), ass_cs(en, True); fr = [k for k in range(int(c0 * FPS / 100) - 1, int(c1 * FPS / 100) + 2) if c0 <= k * 100 / FPS < c1]
        shots = {s["id"] for k in fr for s in segs if s["f0"] <= k < s["f1"]}
        assert len(shots) == 1, f"caption on screen across a cut: '{join_disp(range(a, b + 1))}' frames {fr[0]}-{fr[-1]} shots {shots}"
    cap_events.append(dict(start=round(st, 3), end=round(en, 3), text=join_disp(range(a, b + 1)), hidden=hidden))
assert " ".join(e["text"] for e in cap_events) == " ".join(DISP[:CAP_N])
ASS = BUILD / f"jianwen_v2_rough_{ARGS.tag}.ass"
print("caption cues:", len(cap_events), "hidden:", [e["text"] for e in cap_events if e["hidden"]])

# ------------------------------------------------------------------ audio
def ff(*a): subprocess.check_call(["ffmpeg", "-y", "-v", "error", *a])
def ebur(path, ss=None, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"] + (["-ss", f"{ss:.3f}"] if ss is not None else []) + ["-i", str(path)] + (["-t", f"{dur:.3f}"] if dur is not None else []) + ["-af", "ebur128=peak=true", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True); Iv = TP = None; summ = False
    for ln in p.stderr.splitlines():
        if "Summary:" in ln: summ = True
        if summ and ln.strip().startswith("I:"): Iv = float(ln.split("I:")[1].split("LUFS")[0])
        if summ and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return Iv, TP
def read_wav(p, ch):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", str(ch), "-ar", "48000", "-"]); return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()
def write_wav(p, x):
    pr = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ac", str(x.shape[1]), "-ar", "48000", "-i", "-", "-c:a", "pcm_f32le", str(p)], stdin=subprocess.PIPE)
    pr.stdin.write(x.astype(np.float32).tobytes()); pr.stdin.close(); assert pr.wait() == 0
DUR = TOTAL_F / FPS; SR = 48000; N = int(round(DUR * SR))
FADE1 = DUR - 0.05; FADE0 = min(SPEECH_END + 1.4, FADE1 - 1.35)   # 1.35 s fade to silence (88.60-89.95 s), never a hard cut
def env_db(t):   # bed automation (dB, before ducking): flat and quiet; slight lift into the open question (S20 'It never says...'), eases under the tagline, fades out
    S20_T = SEG["S20"]["start"]
    pts = [(0, 0.0), (S20_T - 0.5, 0.0), (S20_T + 1.5, 1.5), (TAG_T, 0.5), (OUTRO_T + 1.0, -1.0)] + [(FADE0, -1.0), (FADE1, -40.0)]
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
def build_audio():
    mix = AUD / "mix.wav"
    if mix.exists(): return mix
    vo = AUD / "vo_proc.wav"; ff("-i", str(VO_SRC), "-af", "highpass=f=80,acompressor=threshold=0.125:ratio=3:attack=8:release=140:knee=3:makeup=1,aresample=48000", "-ac", "1", "-c:a", "pcm_f32le", str(vo))
    flat = AUD / "bed_flat.wav"   # guzheng: trim sub-lows, carve 2-4 kHz so plucks sit under consonants, soften pick attack slightly
    ff("-i", str(MUSIC), "-t", f"{DUR:.3f}", "-af", "aresample=48000,highpass=f=70,equalizer=f=320:t=q:w=1.2:g=-1.5,equalizer=f=2500:t=q:w=1.0:g=-3.0,equalizer=f=4500:t=q:w=1.2:g=-2.0,afade=t=in:d=1.2", "-ac", "2", "-c:a", "pcm_f32le", str(flat))
    t = np.arange(N) / SR; fl = read_wav(flat, 2); fl = np.pad(fl, ((0, max(0, N - len(fl))), (0, 0)))[:N]
    write_wav(AUD / "bed_auto.wav", fl * (10 ** (env_db(t) / 20))[:, None])
    pre = AUD / "premix.wav"
    def mk(bg):
        ff("-i", str(vo), "-i", str(AUD / "bed_auto.wav"), "-filter_complex",
           "[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][k];"
           f"[1:a]volume={bg}dB[b];[b][k]sidechaincompress=threshold=0.02:ratio=4:attack=25:release=450:knee=4:makeup=1[bd];"
           f"[v][bd]amix=inputs=2:normalize=0:duration=first,apad=whole_len={N}", "-t", f"{DUR:.4f}", "-c:a", "pcm_f32le", str(pre))
    BG = ARGS.bed_db
    mk(BG); I0, _ = ebur(pre); Iv, _ = ebur(vo)
    gain = -14.0 - I0
    for it in range(8):
        if mix.exists(): mix.unlink()   # own scratch from the previous iteration
        ff("-i", str(pre), "-af", f"volume={gain:.3f}dB,aresample=192000,alimiter=limit=0.8:attack=3:release=60:level=false:asc=1,aresample=48000", "-c:a", "pcm_s24le", str(mix))
        I1, TP1 = ebur(mix)
        if abs(I1 + 14.0) <= 0.1 and TP1 <= -1.5: break
        gain += (-14.0 - I1)
    Ib, _ = ebur(AUD / "bed_auto.wav")
    json.dump(dict(premix_I=I0, vo_I=Iv, bed_I_pre_gain=Ib, gain=gain, mix_I=I1, mix_TP=TP1, bed_gain_db=BG, sfx="none"), open(AUD / "mix_stats.json", "w"), indent=1)
    return mix

def stats_report(path):
    I, TP = ebur(path); return I, TP


def plate_guard(partial=False):
    miss = sorted({s["plate"] for s in segs if not Path(s["plate"]).is_file()}); nplates = len({s["plate"] for s in segs})
    if miss and partial:
        print(f"PARTIAL: {len(miss)}/{nplates} plates not landed yet (no master; only landed slots can be previewed)")
    elif miss:
        print(f"REFUSING: {len(miss)}/{nplates} plates missing in {PL} -> nothing rendered:"); [print("   missing", m) for m in miss]; sys.exit(2)
    for s in segs:
        if s["crop_rel"] and Path(s["plate"]).is_file():
            sz = Image.open(s["plate"]).size; s["crop"] = crop_box(sz, s["crop_rel"]); cw = s["crop"][2] - s["crop"][0]
            print(f"{s['id']} tight crop {s['crop']} = {s['crop_rel']['frac']:.0%} of {Path(s['plate']).name} {sz[0]}x{sz[1]} -> source {cw} px wide for 1080 out ({1080 / cw:.2f}x upscale)")
            if cw < 0.70 * 1080: FLAGS.append(f"FLAG {s['id']}: crop is only {cw} px wide (< 756) -> upscale {1080 / cw:.2f}x may read soft; consider --{'opening' if s['id'] == 'S02B' else 'reprise'} fallback")
    todo = sorted({Path(s["plate"]).name for s in segs if FX.spec_todo(s["plate"])})
    stodo = sorted({Path(s["plate"]).name for s in segs if smoke_status(s)[0] == "todo"})
    return sorted(set(todo) | set(stodo)), stodo

def qc_path(name):
    QC.mkdir(parents=True, exist_ok=True); p = QC / name
    if p.exists(): raise SystemExit(f"REFUSING: {p} exists (QC stills are never overwritten; use --qc-dir)")
    return p

if __name__ == "__main__":
    import shutil
    print("FLAGS:" if FLAGS else "FLAGS: none")
    for f in FLAGS: print(f)
    free = shutil.disk_usage("/workspace").free / 2 ** 30; print(f"disk free /workspace: {free:.1f} GiB")
    if ARGS.title_test:   # needs no plates: title over a dark card at the title frames + LEGEND on S12, full size and 360x640
        names = []
        for gf in (30, 60, 100, 140, SEG["S12"]["f0"] + 40):
            ov = overlay_for(gf); card = Image.new("RGBA", (W, H), (22, 20, 26, 255))
            if ov is not None: card.alpha_composite(ov)
            p = qc_path(f"titletest_{gf:05d}.png"); p360 = qc_path(f"titletest_{gf:05d}_360.png")
            card.convert("RGB").save(p); card.convert("RGB").resize((360, 640), Image.Resampling.LANCZOS).save(p360); print("wrote", p, p360)
        f = ImageFont.truetype(F_SEMI, CR["fontSize"])
        for l in CR["title"].split("\n"):
            print(f"title line '{l}': {sum(f.getlength(c) for c in l) + CR['trackingEm'] * CR['fontSize'] * (len(l) - 1):.0f} px (limit {W * 0.92:.0f})")
        title_layout(); sys.exit(0)
    if ARGS.audio_only:
        for d in (BUILD, AUD): d.mkdir(parents=True, exist_ok=True)
        m = build_audio(); print("mix", m, json.load(open(AUD / "mix_stats.json"))); sys.exit(0)
    PW, PH = [int(v) for v in ARGS.preview_size.split("x")]
    if ARGS.smoke_test:   # 2 s low-res run of any plate through THIS pipeline: fx (none unless keyed) -> smoke_v2 -> grade -> cover -> push -> title/LEGEND -> captions
        cfg = json.load(open(ARGS.smoke_test)); n = 2 * FPS
        c = cfg.get("push_center", [0.5, 0.5]); z = cfg.get("push", [1.0, 1.06])
        seg = dict(id="SMOKETEST", plate=cfg["plate"], crop=None, anchor=tuple(c), z_start=z[0], z_end=z[1], f0=0, f1=n, frames=n, run_f0=0,
                   smoke_cfg={k: v for k, v in cfg.items() if k not in ("plate", "note", "push", "push_center")})
        SEG["SMOKETEST"] = seg; tag = Path(ARGS.smoke_test).stem
        out = qc_path(f"smoketest_{tag}_{PW}x{PH}.mp4"); pj = qc_path(f"smoketest_{tag}_proof.json"); still = qc_path(f"smoketest_{tag}_layers_f050.png")
        tmpd = BUILD / "smoketest"; assert not tmpd.exists(), f"{tmpd} exists: use a new --build-dir/--tag"; tmpd.mkdir(parents=True)
        sid, nf = render_segment("SMOKETEST", clips=tmpd, enc=["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "veryfast"], proof_dir=tmpd)
        proof = json.load(open(tmpd / "smoke_proof_SMOKETEST.json"))
        # layer order: smoke under the opaque title pixels -> identical with smoke on/off; captions are burned after (libass) so always on top
        gfx = 50; ov = overlay_for(gfx); a = np.asarray(ov.getchannel("A")) if ov is not None else None
        def comp(sm):
            fr = cam_frame(plate_frame(seg, gfx, gfx / (n - 1), smoke=sm), seg, gfx / (n - 1), gfx / FPS).convert("RGBA"); fr.alpha_composite(ov); return np.asarray(fr.convert("RGB")).astype(np.int16)
        on, off = comp(True), comp(False); opaque = a == 255
        diff_all = np.abs(on - off).max(-1); lay = dict(frame=gfx, opaque_title_px=int(opaque.sum()), max_diff_under_opaque_title=int(diff_all[opaque].max(initial=0)),
                                                     max_diff_elsewhere=int(diff_all.max()), smoke_changes_px=int((diff_all > 0).sum()))
        Image.fromarray(np.concatenate([off, on], 1).astype(np.uint8)).resize((2 * PW, PH), Image.Resampling.LANCZOS).save(still)
        assp = tmpd / "smoketest.ass"; assp.write_text("\n".join(ass) + "\n"); e = str(assp).replace(":", "\\:")
        subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(tmpd / "SMOKETEST.mp4"), "-vf", f"ass='{e}',scale={PW}:{PH}:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-an", str(out)])
        json.dump(dict(config=ARGS.smoke_test, config_md5=md5f(ARGS.smoke_test), smoke_v2_md5=FX.SMOKE_V2_MD5, frames=nf, proof=proof, layer_order=lay, out=str(out), md5=md5f(out)), open(pj, "w"), indent=1)
        print("smoke test:", out, md5f(out)); print(" proof:", proof); print(" layer order:", lay); print(" still (off | on):", still); sys.exit(0)
    SLOTS = []
    if ARGS.slots:
        landed = [s["id"] for s in segs if Path(s["plate"]).is_file()]
        SLOTS = landed if ARGS.slots == "landed" else [x.strip() for x in ARGS.slots.split(",") if x.strip()]
        bad = [x for x in SLOTS if x not in SEG]; assert not bad, f"unknown slots {bad}"
        nl = [x for x in SLOTS if x not in landed]
        if nl: print("REFUSING --slots: plates not landed for", nl); sys.exit(2)
    n0 = len(FLAGS); todo, stodo = plate_guard(partial=bool(SLOTS) or ARGS.fx_overlays or bool(ARGS.test_frames))
    for f in FLAGS[n0:]: print(f)   # crop-softness flags added by the guard
    LANDED = [s for s in segs if Path(s["plate"]).is_file() and (not SLOTS or s["id"] in SLOTS)]
    if ARGS.fx_overlays or ARGS.test_frames:
        if ARGS.fx_overlays:
            for seg in LANDED:
                fx = make_fx(seg); po = qc_path(f"overlay_{seg['id']}.png")
                if fx is not None: FX.overlay(fx, po)
                else: cv2.imwrite(str(po), cv2.cvtColor(plate_rgb(seg["plate"]), cv2.COLOR_RGB2BGR))
                st, why = smoke_status(seg); o = cv2.imread(str(po))
                if st == "on":   # smoke layer placement: protect (cyan), emitter sources (white dot) + footprint (yellow)
                    S = get_smoke(seg); cfg = S["sc"].cfg
                    for pg in cfg["protect"]: cv2.polylines(o, [np.int32(pg)], True, (255, 255, 0), 1)
                    for e in S["sc"].emitters:
                        x0, y0, x1, y1 = e.bb; cv2.rectangle(o, (x0, y0), (x1, y1), (0, 255, 255), 1)
                    for e in cfg["emitters"]: cv2.circle(o, tuple(int(v) for v in e["src"]), 4, (255, 255, 255), -1)
                if seg["crop"]: x0, y0, x1, y1 = seg["crop"]; cv2.rectangle(o, (x0, y0), (x1 - 1, y1 - 1), (255, 0, 255), 2)
                cv2.imwrite(str(po), o)
                print(seg["id"], fx.info() if fx else "no fx", "| smoke", st, why, "| TODO" if FX.spec_todo(seg["plate"]) else "")
        for gf in [int(x) for x in ARGS.test_frames.split(",") if x]:
            seg = [s for s in segs if s["f0"] <= gf < s["f1"]][0]; fi = gf - seg["f0"]
            if seg not in LANDED: print(f"skip f{gf}: {seg['id']} plate not landed"); continue
            if smoke_status(seg)[0] == "todo": print(f"note f{gf}: {seg['id']} smoke still a template -> rendered without smoke")
            u = fi / max(seg["frames"] - 1, 1)
            fr = cam_frame(plate_frame(seg, gf, u), seg, u, fi / FPS); ov = overlay_for(gf)
            if ov is not None: fr = fr.convert("RGBA"); fr.alpha_composite(ov); fr = fr.convert("RGB")
            p = qc_path(f"test_{gf:05d}_{seg['id']}.png"); fr.save(p); fr.resize((PW, PH), Image.Resampling.LANCZOS).save(qc_path(f"test_{gf:05d}_{seg['id']}_{PW}.png")); print("wrote", p)
        sys.exit(0)
    if SLOTS:   # partial low-res previews (landed slots only; never the master)
        tdo = [x for x in SLOTS if FX.spec_todo(SEG[x]["plate"]) or smoke_status(SEG[x])[0] == "todo"]
        if tdo: print("REFUSING --slots: fx/smoke still templates for", tdo); sys.exit(3)
        PV = EDIT / "previews_v2" / ARGS.tag; assert not PV.exists(), f"{PV} exists: previews are never overwritten (use a new --tag)"
        PB = Path(ARGS.build_dir) if ARGS.build_dir else EDIT / f"_preview_v2_{ARGS.tag}"; assert not PB.exists(), f"{PB} exists (use a new --tag)"
        assert free >= 4.0, f"only {free:.1f} GiB free on /workspace"
        PV.mkdir(parents=True); (PB / "clips").mkdir(parents=True); ASSP = PB / f"jianwen_v2_{ARGS.tag}.ass"; ASSP.write_text("\n".join(ass) + "\n"); e = str(ASSP).replace(":", "\\:")
        ENC_PV = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "14", "-preset", "veryfast"]
        with Pool(min(ARGS.jobs, len(SLOTS))) as pool:
            for sid, n in pool.starmap(render_segment, [(x, PB / "clips", ENC_PV, PB) for x in SLOTS]): print("clip", sid, n, flush=True)
        outs = []
        for x in SLOTS:
            s = SEG[x]; o = PV / f"{x}_{PW}x{PH}.mp4"; st = s["start"]
            subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(PB / "clips" / f"{x}.mp4"), "-ss", f"{st:.4f}", "-t", f"{s['duration']:.4f}", "-i", str(VO_SRC),
                                   "-vf", f"setpts=PTS+{st:.4f}/TB,ass='{e}',setpts=PTS-STARTPTS,scale={PW}:{PH}:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                                   "-c:a", "aac", "-b:a", "128k", "-shortest", str(o)]); outs.append(o)
        ids = [s["id"] for s in segs]; ix = sorted(ids.index(x) for x in SLOTS)
        if len(ix) > 1 and ix == list(range(ix[0], ix[-1] + 1)):   # contiguous run -> one joined preview with VO (raw VO, not the final mix)
            cl = PB / "concat.txt"; cl.write_text("".join(f"file '{PB / 'clips' / (ids[i] + '.mp4')}'\n" for i in ix)); a0 = segs[ix[0]]["start"]; dd = segs[ix[-1]]["end"] - a0
            o = PV / f"{ids[ix[0]]}-{ids[ix[-1]]}_{PW}x{PH}.mp4"
            subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(cl), "-ss", f"{a0:.4f}", "-t", f"{dd:.4f}", "-i", str(VO_SRC),
                                   "-vf", f"setpts=PTS+{a0:.4f}/TB,ass='{e}',setpts=PTS-STARTPTS,scale={PW}:{PH}:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                                   "-c:a", "aac", "-b:a", "128k", "-shortest", str(o)]); outs.append(o)
        for o in outs: print("preview", o, md5f(o))
        sys.exit(0)
    if todo: print("REFUSING: fx/smoke specs are still templates for:", todo, "| smoke templates:", stodo, "(fill fx_jianwen_v2b from --fx-overlays first)"); sys.exit(3)
    for p in (MASTER, PREVIEW): assert not p.exists(), f"{p} exists: refusing to overwrite (use a new --tag)"
    assert free >= 4.0, f"only {free:.1f} GiB free on /workspace: need >= 4 GiB for clips + master"
    for d in (BUILD, CLIPS, AUD): d.mkdir(parents=True, exist_ok=True)
    ASS.write_text("\n".join(ass) + "\n")
    json.dump(dict(segs=[{k: v for k, v in s.items()} for s in segs], cr={k: v for k, v in CR.items()}, legend=(LG if LEGEND_ON else dict(enabled=False, removed="owner 12:59")), captions=cap_events), open(BUILD / "timeline.json", "w"), indent=1, default=str)
    MIX = build_audio()
    with Pool(ARGS.jobs) as pool:
        for sid, n in pool.imap_unordered(render_segment, [s["id"] for s in sorted(segs, key=lambda s: -s["frames"])]): print("clip", sid, n, flush=True)
    cl = BUILD / "concat.txt"; cl.write_text("".join(f"file '{CLIPS / (s['id'] + '.mp4')}'\n" for s in segs))
    e = str(ASS).replace(":", "\\:")
    subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(cl), "-i", str(MIX), "-map", "0:v", "-map", "1:a",
                           "-vf", f"ass='{e}'", *ENC_FINAL, "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", f"{DUR:.4f}", "-movflags", "+faststart", str(MASTER)])
    subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(MASTER), "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-b:v", "2600k", "-maxrate", "3500k", "-bufsize", "7000k",
                           "-c:a", "copy", "-movflags", "+faststart", str(PREVIEW)])
    for p in (MASTER, PREVIEW):
        I, TP = ebur(p); print(p, md5f(p), p.stat().st_size, "I", I, "TP", TP)
        if TP is not None and TP > -1.0: print("WARNING: true peak above -1 dBTP after AAC:", p)
