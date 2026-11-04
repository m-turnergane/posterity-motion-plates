#!/usr/bin/env python3
"""POSTERITY standalone "They Found His Name in the Walls" (Germanicus, AD 19) v5 ROUGH r1 (owner via Vellum, 2026-10-27 4:24 PM EDT).
Built from build_rough_germanicus_v1f.py (untouched). v5 changes:
 (1) VO = final-vo-oliver-germanicus-v5.wav (one whole-script Oliver take v5t3, 289 words, md5-locked) + script-vo-v5-DRAFT.txt (md5-locked).
 (2) New plate map retimed to the v5 words (see CUTS). Missing owner plates = dark neutral 1080x1920 PLACEHOLDER cards (small centred text),
     swappable with --plate-R/--plate-W/--plate-C/--plate-G/--plate-7B (no VO re-record). seq7b.png / seq7b-v2.png are never used.
     Reframes (Seq9B coin exchange, Seq7A accuser side / Piso, Seq2 face) are crops of the owner plates written into the build dir.
 (3) NO "ILLUSTRATIVE RECONSTRUCTION" tag anywhere (owner standing rule 2026-10-27): IR dict / ir_png / ir_layer / IR_FADE removed.
 (4) Chronicle Reveal title (v1f text) on the OPENING plate; caption hide rule = v1e (wholly under the title AND repeats >= 3 consecutive title words).
     Optional credit "Tacitus, Annals 2.55" during L02 (SeqR prompt Flags).
 (5) Bed: Ossuary 6 - Air, ONE continuous unlooped window (offset 120 s -> ~244 s, the cue's own end; the 171 s v1 window has only 79 s left),
     same chain as v1f (HPF/EQ, fade-in, 900-4500 Hz carve, L+R-average rider 1 s / 3 dB/s cap, norm, constant duck, limiter, -14 LUFS / TP <= -1),
     + a 3 dB bed tail dip ramped (<= 2 dB/s) into the L21->L22 gap so the VO's ending drop survives the mix; fade from speech end + 0.5 s.
     VO ending-drop restore: if the staging compressor shrinks the L22-L23 drop, a gap-only gain ramp restores the source delta.
 (6) Lean disk: intermediate clips are deleted (own fresh files) once picture_final is encoded; debug bed wavs not written.
Never deletes or overwrites anything else (ffmpeg -n, new() guard, build dir must be new or --resume)."""
from __future__ import annotations
import json, math, subprocess, hashlib, sys, os, argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np, soundfile as sf, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path("/workspace/posterity/standalones/germanicus")
EDIT, PLATES, PDER, SCORE, VODIR, CFG = ROOT / "edit", ROOT / "plates-owner", ROOT / "plates-derived", ROOT / "score", ROOT / "vo", ROOT / "motion" / "configs"
REND = Path("/workspace/posterity/renders")
sys.path.insert(0, str(EDIT)); import make_masks_germanicus_v1b as K
FONT_DIR = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/"
F_BOLD = FONT_DIR + "SourceSerifPro-Bold.ttf"

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="final", help="final -> posterity-germanicus-v5-ROUGH.mp4 (no tag)")
ap.add_argument("--no-sfx", action="store_true")
ap.add_argument("--sfx-rel-db", type=float, default=-4.0, help="SeqC war SFX level vs the bed (same window, LUFS)")
ap.add_argument("--sfx-carve-db", type=float, default=8.0)
ap.add_argument("--rider-mode", default="stereo", choices=["mix", "stereo"], help="v5: stereo = L+R-average rider (owner brief)")
ap.add_argument("--audio-dir", default=None)
ap.add_argument("--narrow", default="")
ap.add_argument("--rider-slope-db-s", type=float, default=3.0)
ap.add_argument("--word-check", default=None, help="v5: word indices that must clear --word-target; default = content words of L22+L23")
ap.add_argument("--word-target", type=float, default=12.0)
ap.add_argument("--resume", action="store_true")
ap.add_argument("--music", default="/workspace/posterity/standalones/germanicus/score/macleod_ossuary6_air_v1c.mp3")
ap.add_argument("--music-offset", type=float, default=120.0)
ap.add_argument("--bed-norm-lufs", type=float, default=-28.0)
ap.add_argument("--bed-step-db", type=float, default=0.5)
ap.add_argument("--murder-target", type=float, default=9.0, help="v5: margin target for the LAST word ('unproved.')")
ap.add_argument("--frame-target-pct", type=float, default=99.0)
ap.add_argument("--speech-dip-db", type=float, default=8.0)
ap.add_argument("--tail-dip-db", type=float, default=3.0)
ap.add_argument("--limit-db", type=float, default=-4.0)
ap.add_argument("--aac-bitrate", default="256k")
ap.add_argument("--picture-only", action="store_true")
ap.add_argument("--audio-only", action="store_true")
ap.add_argument("--keep-clips", action="store_true")
ap.add_argument("--no-credit", action="store_true")
ap.add_argument("--only", default=None)
ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--scratch", action="store_true")
for _k in ("R", "W", "C", "G", "7B"):
    ap.add_argument(f"--plate-{_k}", dest=f"plate_{_k}", default=None, help=f"owner plate for Seq{_k}; omitted -> PLACEHOLDER card")
    ap.add_argument(f"--b3-{_k}", dest=f"b3_{_k}", default=None, help=f"optional light config for --plate-{_k} (its plate must match)")
ap.add_argument("--test-frame", default=None)
ARGS = ap.parse_args()
VO_SRC = VODIR / "final-vo-oliver-germanicus-v5.wav"; WORDS_JSON = VODIR / "final-vo-oliver-germanicus-v5_words.json"; VO_MD5 = "f5e7ff9114722f371c0e68e014142d8a"
SCRIPT_DISP = ROOT / "raw" / "script-vo-v5-DRAFT.txt"; SCRIPT_MD5 = "393176a8f143111f0165d18b8b238783"
MUSIC_MD5 = "253813904704fb2ed3a4a468c3cc5605"
MASTER = REND / ("posterity-germanicus-v5-ROUGH.mp4" if ARGS.tag == "final" else f"posterity-germanicus-v5-ROUGH-{ARGS.tag}.mp4")
BUILD = (Path("/workspace/tmp/germ") if ARGS.scratch else EDIT) / f"_build_v5{ARGS.tag}"; AUDIO = Path(ARGS.audio_dir) if ARGS.audio_dir else BUILD / "audio"; WORK = BUILD / "picture"; CLIPS = WORK / "clips"; PREPPED = BUILD / "plates_cropped"
if MASTER.exists(): raise SystemExit(f"refusing to overwrite {MASTER}: use a new --tag")
if BUILD.exists() and not ARGS.resume: raise SystemExit(f"{BUILD} exists: use a new --tag or --resume")
FPS, W, H, UP, SR = 30, 1080, 1920, 2, 48000
HOLD_AFTER_SPEECH, OUTRO_S = 1.0, 3.5
BED_HPF_HZ, BED_FADEIN_S = 70, 2.5
BED_EQ = "equalizer=f=320:t=q:w=1.2:g=-2.5,equalizer=f=1800:t=q:w=1.0:g=-2.0"
VO_STAGE_LUFS, MASTER_TARGET_I, LIMIT_DB = -16.0, -14.0, ARGS.limit_db
PHRASE_GAP, RIDE_DB, RIDE_ATT, RIDE_REL, KEY_TARGET = 1.0, 3.5, 0.30, 1.2, 9.3
FADE_DEPTH_DB, TAPER_S = 30.0, 0.050
RIDER1_WIN, RIDER1_SIG, RIDER1_CLAMP, RIDER2_IT, RIDER2_SIG, RIDER2_CLAMP = 0.25, 0.06, 10.0, 30, 0.20, 6.0
VO_COMP = "acompressor=threshold=0.2:ratio=2.5:attack=10:release=150:knee=2.8:makeup=1"
ENC_INTER = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "8", "-preset", "fast",
              "-g", "30", "-keyint_min", "30", "-x264-params", "keyint=30:min-keyint=30:scenecut=0"]
ENC_FINAL = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-profile:v", "high"]
X_GOP30 = ["-g", "30", "-keyint_min", "30", "-x264-params", "keyint=30:min-keyint=30:scenecut=0"]
for d in (BUILD, AUDIO, WORK, CLIPS, PREPPED, REND): d.mkdir(parents=True, exist_ok=True)
def new(p):
    p = Path(p)
    if p.exists(): raise SystemExit(f"refusing to overwrite {p}")
    return p
def ffn(*a): subprocess.check_call(["ffmpeg", "-n", "-v", "error", *a])
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

# ------------------------------------------------------------------ words (ElevenLabs alignment of the ONE whole-script take v5t3; final gain only in gaps)
assert md5f(SCRIPT_DISP) == SCRIPT_MD5, "script md5 changed: STOP"
assert md5f(VO_SRC) == VO_MD5, "VO md5 changed: STOP"
WJ = json.load(open(WORDS_JSON)); words = [{"word": w["word"], "start": w["start"], "end": w["end"], "line": w["line"]} for w in WJ["words"]]
norm = lambda s: " ".join(s.split())
assert len(words) == 289, len(words)
assert norm(" ".join(w["word"] for w in words)) == norm(SCRIPT_DISP.read_text()), "words != script-vo-v5-DRAFT.txt"
DISP = SCRIPT_DISP.read_text().split(); assert len(DISP) == len(words)
def join_disp(idx): return " ".join(DISP[i_] for i_ in idx)
if not (BUILD / "vo_words.json").exists(): json.dump({"words": words}, open(BUILD / "vo_words.json", "x"), indent=1)
def fob(t): return int(math.floor(t * FPS + 1e-6))
def widx(seq, after=0):
    p = seq.split()
    for k in range(after, len(words)):
        if [w["word"] for w in words[k:k + len(p)]] == p: return k
    raise KeyError(seq)
def line_words(n): return [i for i, w in enumerate(words) if w["line"] == n]
def P(n): return PLATES / f"{n}.png"
def cfg(sid): return str(CFG / f"germ_{sid}_light_v1b.json")
C = (1.00, 1.04, (0.5, 0.5))

# ------------------------------------------------------------------ placeholder cards (dark neutral, small centred text) + owner-plate reframes
PH_TEXT = {"R": ("PLACEHOLDER SeqR", "storm rescue (owner plate pending)"),
           "W": ("PLACEHOLDER SeqW", "son warns Piso (owner plate pending)"),
           "C": ("PLACEHOLDER SeqC", "Celenderis battle (owner plate pending)"),
           "G": ("PLACEHOLDER SeqG", "statues dragged off (owner plate pending)"),
           "7B": ("PLACEHOLDER 7B", "Piso's room, sword on floor (owner plate pending)")}
PH_BG, PH_FG = (30, 29, 28), (150, 146, 140)
def placeholder_png(k):
    dst = PREPPED / f"placeholder_{k}.png"
    if dst.exists(): return dst
    im = Image.new("RGB", (W, H), PH_BG); d = ImageDraw.Draw(im); f1 = ImageFont.truetype(F_BOLD, 34); f2 = ImageFont.truetype(FONT_DIR + "SourceSerifPro-Regular.ttf", 30)
    for txt, f, y in ((PH_TEXT[k][0], f1, 920), (PH_TEXT[k][1], f2, 972)):
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=PH_FG)
    im.save(dst); return dst
REFRAMES = {   # name: (owner plate, crop box in plate px (941x1672), 9:16) -- sharpness checked at 1080 (see report)
    "seq9b_coin": ("seq9b", (160, 440, 800, 1578)),     # 640 px wide -> 1.69x; coin drop + hands, Piso's head in frame
    "seq7a_accuser": ("seq7a", (0, 380, 620, 1482)),    # 620 -> 1.74x; accuser's back + pointing arm, senators left
    "seq7a_piso": ("seq7a", (361, 380, 941, 1411)),     # 580 -> 1.86x; Piso alone on the floor (accuser fingertip at the left edge)
    "seq2_face": ("seq2", (220, 80, 820, 1147)),        # 600 -> 1.80x; Germanicus head + shoulders
}
def reframe_png(name):
    src, box = REFRAMES[name]; dst = PREPPED / f"{name}.png"
    assert abs((box[3] - box[1]) / (box[2] - box[0]) - 16 / 9) < 0.01, (name, box)
    if not dst.exists(): Image.open(P(src)).convert("RGB").crop(box).save(dst)
    return dst
PLACEHOLDERS = {}
def slot(k, anchor=(0.5, 0.5)):
    p = getattr(ARGS, f"plate_{k}"); b3 = getattr(ARGS, f"b3_{k}")
    if p is None: PLACEHOLDERS[k] = True; return (placeholder_png(k), 1.00, 1.00, (0.5, 0.5), None)
    assert Path(p).exists(), p; assert Path(p).name not in ("seq7b.png", "seq7b-v2.png"), "seq7b/seq7b-v2 are not to be used"
    if b3: assert Path(json.load(open(b3))["plate"]) == Path(p), (k, b3)
    PLACEHOLDERS[k] = False; return (Path(p), *C[:2], anchor, b3)
# (id, plate, first word idx, z0, z1, anchor, b3 light cfg)
CUTS = [
    ("R",   *slot("R")[:1], 0, *slot("R")[1:]),                                                    # L01-02 storm rescue + Chronicle Reveal + Tacitus credit
    ("2",   P("seq2"), widx("He was the emperor's"),           *C, None),                          # L03
    ("3",   P("seq3"), widx("Piso, appointed governor"),       *C, None),                          # L04
    ("9Bc", reframe_png("seq9b_coin"), widx("Instead, he gave"), *C, None),                        # L05 gifts to soldiers (Seq9B foreground crop)
    ("3b",  P("seq3"), widx("The emperor's son held"),         1.04, 1.07, (0.5, 0.5), None),      # L06 back to Seq3 (zoom continues)
    ("4",   P("seq4"), widx("Then Germanicus fell"),           *C, cfg("G4")),                     # L07 + L08 head
    ("1A",  P("seq1a"), widx("lead tablets bearing"),          *C, cfg("G1a")),                    # L08 from "lead tablets" (mid-sentence, by brief)
    ("6",   P("seq6"), widx("Germanicus believed Piso"),       *C, cfg("G6")),                     # L09
    ("W",   *slot("W")[:1], widx("After Germanicus died,"), *slot("W")[1:]),                       # L10-11
    ("C",   *slot("C")[:1], widx("Piso chose force."), *slot("C")[1:]),                            # L12
    ("7A",  P("seq7a"), widx("Now he had to face"),            *C, None),                          # L13 wide (runs to "Outside," -> 3.46 s)
    ("G",   *slot("G")[:1], widx("crowds dragged off"), *slot("G")[1:]),                           # L14 from "crowds"
    ("7Aa", reframe_png("seq7a_accuser"), widx("Inside, his accusers"), *C, None),                 # L15-16 accuser's side
    ("7Ap", reframe_png("seq7a_piso"), widx("He could be condemned"), *C, None),                   # L17 Piso isolated
    ("7B",  *slot("7B")[:1], widx("Before judgement,"), *slot("7B")[1:]),                          # L18
    ("8",   P("seq8"), widx("The Senate condemned him"),       *C, None),                          # L19
    ("9A",  P("seq9a"), widx("Copies survive in"),             *C, None),                          # L20
    ("10",  PDER / "seq10_softcaps_v1c.png", widx("They repeat Germanicus's"), *C, None),          # L21
    ("2f",  reframe_png("seq2_face"), widx("The man Germanicus saved"), *C, None),                 # L22-23 face, then outro
]
for c_ in CUTS: assert Path(c_[1]).name not in ("seq7b.png", "seq7b-v2.png")
t_speech_end = words[-1]["end"]
OUTRO_F0 = int(math.ceil((t_speech_end + HOLD_AFTER_SPEECH) * FPS - 1e-6))
FORCED_F0 = {}
total_frames = OUTRO_F0 + int(round(OUTRO_S * FPS)); package = total_frames / FPS
GAP_EXCEPTION = {widx("lead tablets bearing"), widx("crowds dragged off")}   # brief: cut on "lead tablets"; G cut on "crowds" (after "Outside,") keeps 7A wide >= 3 s
def cutframe(wi):
    t = words[wi]["start"]; pe = words[wi - 1]["end"]; f = fob(t)
    if wi in GAP_EXCEPTION or f / FPS - pe >= 0.1 - 1e-9: return f
    return f + 1
segs = []
for k, (sid, plate, wi, z0, z1, anc, c3) in enumerate(CUTS):
    segs.append({"id": sid, "plate": str(plate), "z_start": z0, "z_end": z1, "anchor": anc, "f0": 0 if k == 0 else FORCED_F0.get(sid, cutframe(wi)), "first_word_idx": wi, "b3": c3})
segs.append({"id": "OUTRO", "plate": str(P("outro")), "z_start": 1.00, "z_end": 1.02, "anchor": (0.5, 0.5), "f0": OUTRO_F0, "first_word_idx": None, "b3": None})
for a, b in zip(segs, segs[1:]): a["f1"] = b["f0"]
segs[-1]["f1"] = total_frames
for s in segs: s["frames"] = s["f1"] - s["f0"]; s["start"] = s["f0"] / FPS; s["end"] = s["f1"] / FPS; s["duration"] = s["frames"] / FPS
for s in segs: s["placeholder"] = Path(s["plate"]).name.startswith("placeholder_")
for s in segs: s["reframe"] = REFRAMES.get(Path(s["plate"]).stem)
GAPS = []
for s_ in segs[1:-1]:
    w = words[s_["first_word_idx"]]; pw = words[s_["first_word_idx"] - 1]
    s_["first_word"] = w["word"]; s_["word_start"] = w["start"]; s_["cut_to_word_start_s"] = round(w["start"] - s_["start"], 4)
    s_["gap_after_prev_word_end"] = round(s_["start"] - pw["end"], 3); GAPS.append((s_["id"], s_["gap_after_prev_word_end"], s_["cut_to_word_start_s"]))
segs[0]["first_word"] = words[0]["word"]; segs[-1]["first_word"] = None
GAP_FLAGS = [(sid, g) for sid, g, _ in GAPS if g < 0.1]
assert all(sid in ("1A", "G") for sid, _ in GAP_FLAGS), GAP_FLAGS   # only "lead tablets" and "crowds" cuts are mid-sentence
assert all(-0.034 < d < 0.034 for sid, _, d in GAPS if sid not in FORCED_F0), GAPS
SHORT = [(s["id"], round(s["duration"], 3)) for s in segs if s["duration"] < 3.0]
print("cut gaps:", GAPS); print("mid-sentence cuts (gap < 0.1 s):", GAP_FLAGS); print("shots under 3 s (FLAG):", SHORT)
SEG_BY_ID = {x["id"]: x for x in segs}
assert not SHORT, SHORT   # every plate >= 3.0 s
L22_I, L23_I = line_words(22), line_words(23); L21_I = line_words(21)
fade_start = t_speech_end + 0.5; fade_end = package - 0.03
TAILDIP_T0 = words[L21_I[-1]]["end"] - 1.0; TAILDIP_T1 = words[L22_I[0]]["start"] + 0.5   # ~1.9 s ramp, ~1.6 dB/s

# ------------------------------------------------------------------ helpers (Croatoan Ch III v1b_r2 lines 152-239, verbatim)
def detect_bars(arr, maxscan=40, margin=4):   # verbatim
    lum = arr.astype(np.float32).mean(2); res, info = {}, {}
    for side in "LRTB":
        L = {"L": lum.T, "R": lum.T[::-1], "T": lum, "B": lum[::-1]}[side]
        nn = min(200, len(L)); m = L[:nn].mean(1); s = L[:nn].std(1); br = (L[:nn] > 225).mean(1)
        d = np.abs(np.diff(L[:nn], axis=0)).mean(1); ref_m = float(np.median(m[60:120])); ref_d = float(np.median(d[20:150]))
        k = 0
        while k < maxscan and (br[k] > 0.35 or (s[k] < 5 and abs(m[k] - ref_m) > 20)): k += 1
        ext = k; c = int(np.argmax(d[:30]))
        if d[c] > 4 * ref_d and (m[:c + 1] > ref_m + 25).all(): ext = max(ext, c + 1)
        res[side] = ext + margin if ext else 0
        info[side] = {"bar_px": ext, "crop_px": res[side]}
    return res, info
def prepare_cover(im, up=UP):   # verbatim
    im = im.convert("RGB"); tw, th = W * up, H * up; sw, sh = im.size
    sc = max(tw / sw, th / sh); nw, nh = int(math.ceil(sw * sc)), int(math.ceil(sh * sc))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS); l, t = (nw - tw) // 2, (nh - th) // 2
    return im.crop((l, t, l + tw, t + th))
def auto_chunks(ws, max_words=7):   # Day 17, verbatim
    out, cur = [], []
    def flush():
        nonlocal cur
        WEAK = {"the", "a", "an", "and", "by", "in", "to", "of", "his", "her", "their", "he", "who", "was", "were", "on", "at", "for"}
        while len(cur) > max_words:
            n = len(cur); parts = math.ceil(n / max_words); ideal = n / parts
            cands = [k for k in range(2, min(max_words, n - 2) + 1)]
            k = min(cands, key=lambda k: abs(k - ideal) + (3 if cur[k - 1].lower().strip(",") in WEAK else 0))
            out.append(cur[:k]); cur = cur[k:]
        if cur: out.append(cur)
        cur = []
    for w in ws:
        cur.append(w)
        if w.endswith((".", "?", "!")): flush()
        elif w.endswith(",") and len(cur) >= 3: flush()
    flush()
    merged = []
    for c in out:
        if merged and len(c) == 1 and len(merged[-1]) < max_words + 1 and not merged[-1][-1].endswith((".", "?", "!")): merged[-1] = merged[-1] + c
        elif merged and len(merged[-1]) == 1 and not merged[-1][-1].endswith((".", "?", "!")): merged[-1] = merged[-1] + c
        else: merged.append(c)
    return [" ".join(c) for c in merged]
def ebur(path, ss=None, dur=None):   # verbatim
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if ss is not None: cmd += ["-ss", f"{ss:.3f}"]
    cmd += ["-i", str(path)]
    if dur is not None: cmd += ["-t", f"{dur:.3f}"]
    cmd += ["-af", "ebur128=peak=true", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True); Iv = TP = None; summ = False
    for ln in p.stderr.splitlines():
        if "Summary:" in ln: summ = True
        if summ and ln.strip().startswith("I:"): Iv = float(ln.split("I:")[1].split("LUFS")[0])
        if summ and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return Iv, TP
def wrap_idx(tok_idx, maxc=24):   # verbatim, on the display tokens
    if len(join_disp(tok_idx)) <= maxc: return [tok_idx]
    best = None
    for k in range(1, len(tok_idx)):
        sc = max(len(join_disp(tok_idx[:k])), len(join_disp(tok_idx[k:])))
        if best is None or sc < best[0]: best = (sc, k)
    return [tok_idx[:best[1]], tok_idx[best[1]:]]
def ass_line(tok_idx): return r"\N".join(join_disp(ln) for ln in wrap_idx(tok_idx))
def ass_time(t):
    cs = int(round(max(0.0, t) * 100)); s, cs = divmod(cs, 100); m, s = divmod(s, 60); h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
def _ss(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

PLATE_CROP = {}
def cropped_plate(path):
    path = Path(path); im = Image.open(path).convert("RGB"); arr = np.asarray(im); crop, info = detect_bars(arr); w, h = im.size
    box = (crop["L"], crop["T"], w - crop["R"], h - crop["B"]); out = im.crop(box)
    recheck, _ = detect_bars(np.asarray(out)); assert not any(recheck.values()), (path.name, recheck)
    dst = PREPPED / path.name; out.save(dst)
    return dst, {"src_size": [w, h], "crop_px": crop, "box": box, "cropped_size": list(out.size)}
def base_2x(seg): return prepare_cover(Image.open(seg["prepped"]))
def cam(seg, u, t):   # StablePush (scale about the anchor), as Ugarit cam() 'else' branch
    z0, z = seg["z_start"], seg["z_end"]; s = z0 * (z / z0) ** u; ax, ay = seg["anchor"]
    cx = ax * W * (1 - 1 / s) + W / (2 * s); cy = ay * H * (1 - 1 / s) + H / (2 * s); hw, hh = W / (2 * s), H / (2 * s)
    return s, min(max(cx, hw), W - hw), min(max(cy, hh), H - hh)
def cam_frame(base, seg, u, t):   # B5 jitter fix: affine onto a 2x grid, INTER_AREA down once
    bw, bh = base.size; s, cx, cy = cam(seg, u, t); k = bw / W; ww, wh = bw / s, bh / s; l, tp = cx * k - ww / 2, cy * k - wh / 2
    big = base.transform((W * 2, H * 2), Image.Transform.AFFINE, (ww / (2 * W), 0, l, 0, wh / (2 * H), tp), resample=Image.Resampling.BICUBIC)
    return Image.fromarray(cv2.resize(np.asarray(big), (W, H), interpolation=cv2.INTER_AREA))
def to_out(seg, x, y, u, t):
    s, cx, cy = cam(seg, u, t); return (x - (cx - W / (2 * s))) * s, (y - (cy - H / (2 * s))) * s

# ------------------------------------------------------------------ Chronicle Reveal (Croatoan Ch III v1b_r2 lines 240-457, verbatim; title text = Germanicus, TITLE_TOP_PCT 19.0)
F_SEMI = FONT_DIR + "SourceSerifPro-Semibold.ttf"; TITLE_TOP_PCT = 17.94; TITLE_LINE_H = 0.84   # v1b: was 19.0 / 0.92.  v1 note: Germanicus: 2-line block text ~274-440 px (below the ~270 px line), lamp flame above it (~70-207 px), GERMANICVS ~800 px clear
# ------------------------------------------------------------------ easing helpers
def cubic_bezier(x1, y1, x2, y2):
    def bez(t, a, b):
        return 3 * a * t * (1 - t) ** 2 + 3 * b * t * t * (1 - t) + t ** 3
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
E_DRAG = cubic_bezier(0.33, 0.0, 0.2, 1)
E_IN = cubic_bezier(0.22, 1, 0.36, 1)
E_OUT = cubic_bezier(0.4, 0, 0.2, 1)
LIN = lambda x: min(max(x, 0.0), 1.0)

def interp(f, a, b, v0, v1, ease=LIN):
    if b <= a:
        p = 1.0 if f >= b else 0.0
    else:
        p = min(max((f - a) / (b - a), 0.0), 1.0)
    return v0 + (v1 - v0) * ease(p)

# ------------------------------------------------------------------ Chronicle Reveal v3.2b (PIL port)
CR = dict(title="THEY FOUND HIS\nNAME IN THE WALLS", fontSize=88, color=(243, 237, 224), topPercent=TITLE_TOP_PCT, offsetX=-16,
          strokeEnterStart=8, strokeEnterEnd=26, strokeClearStart=84, strokeClearEnd=105,
          manifestStart=14, manifestEnd=42, exitStart=75, exitEnd=95, bandHeightPercent=14,
          widthPercent=94, peakOpacity=0.92, fill="#5A1A18", edge="#3A0E0C", mid="#6E2A1C",
          scaleFrom=0.92, scaleTo=1.0, exitScaleTo=0.94, settleYPx=4, afterEdgeLagFrames=2,
          letterSettleFrames=12, trackingEm=0.02, nudgeY=-4)

def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

def smooth_noise(h, w, cell_y, cell_x, seed):
    rng = np.random.default_rng(seed)
    gh, gw = max(2, int(h / cell_y) + 3), max(2, int(w / cell_x) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC)
    return np.asarray(im, np.float32) / 255.0

def build_strike_rgba():
    bw = int(round(W * CR["widthPercent"] / 100)); bh = int(round(H * CR["bandHeightPercent"] / 100))
    topY = [78, 62, 71, 55, 68, 48, 60, 52, 70, 58, 65, 50, 72, 56, 64, 54, 75, 60, 70, 66, 80]
    botY = [128, 142, 135, 150, 138, 155, 140, 148, 132, 145, 138, 152, 130, 144, 136, 150, 125, 140, 134, 138, 122]
    def chain(ys):
        m = len(ys); xs_out, ys_out = [], []
        for k in range(1, m):
            x0, x1 = (k - 1) / (m - 1) * 1000, k / (m - 1) * 1000
            cx, cy = (x0 + x1) / 2, ys[k - 1]
            for t in np.linspace(0, 1, 40):
                xs_out.append((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1)
                ys_out.append((1 - t) ** 2 * ys[k - 1] + 2 * (1 - t) * t * cy + t * t * ys[k])
        return np.array(xs_out), np.array(ys_out)
    xt, yt = chain(topY); xb, yb = chain(botY)
    xs = np.arange(bw) / bw * 1000
    top = np.interp(xs, xt, yt) / 200 * bh
    bot = np.interp(xs, xb, yb) / 200 * bh
    yy = np.arange(bh)[:, None].astype(np.float32)
    dy = (smooth_noise(bh, bw, 17, 29, 3) - 0.5) * 2 * 4.4
    dx_n = (smooth_noise(bh, bw, 17, 29, 4) - 0.5) * 2 * 3.3
    yyd = yy + dy
    # soft anti-aliased mask with ragged dry-brush fringe
    fringe = smooth_noise(bh, bw, 3, 9, 7)
    m_top = np.clip((yyd - top[None, :]) / 2.0 + 0.5, 0, 1)
    m_bot = np.clip((bot[None, :] - yyd) / 2.0 + 0.5, 0, 1)
    mask = m_top * m_bot
    edge_zone = np.clip(1 - np.minimum(np.abs(yyd - top[None, :]), np.abs(yyd - bot[None, :])) / 10.0, 0, 1)
    mask = mask * (1 - edge_zone * 0.55 * (fringe > 0.62))
    # horizontal ends: ragged brush start/stop (displacement only)
    xx = np.arange(bw)[None, :].astype(np.float32) + dx_n
    endfade = np.clip(xx / 6.0, 0, 1) * np.clip((bw - 1 - xx) / 6.0, 0, 1)
    mask = mask * endfade
    # pigment vertical gradient (objectBoundingBox of path: y 48..155)
    t = np.clip((yy / bh * 200 - 48) / (155 - 48), 0, 1)
    stops = [(0.0, CR["edge"], 0.55), (0.18, CR["mid"], 0.95), (0.42, CR["fill"], 1.0),
             (0.58, CR["fill"], 1.0), (0.78, CR["mid"], 0.92), (1.0, CR["edge"], 0.5)]
    so = np.array([s[0] for s in stops]); sc = np.stack([hexrgb(s[1]) for s in stops]); sa = np.array([s[2] for s in stops])
    tt = t[:, 0]
    col = np.stack([np.interp(tt, so, sc[:, c]) for c in range(3)], -1)[:, None, :].repeat(bw, 1)
    alp = np.interp(tt, so, sa)[:, None].repeat(bw, 1)
    # length gradient: dark ends, warm centre
    u = np.arange(bw) / (bw - 1)
    lg_c = np.stack([np.interp(u, [0, .08, .5, .92, 1], [0x2A, 0x5A, 0x7A, 0x5A, 0x2A]),
                     np.interp(u, [0, .08, .5, .92, 1], [0x0A, 0x1A, 0x32, 0x1A, 0x0A]),
                     np.interp(u, [0, .08, .5, .92, 1], [0x08, 0x18, 0x20, 0x18, 0x08])], -1)
    lg_a = np.interp(u, [0, .08, .5, .92, 1], [0.35, 0, 0.12, 0, 0.4])
    col = col * (1 - lg_a[None, :, None]) + lg_c[None, :, :] * lg_a[None, :, None]
    # mottles
    Y, X = np.mgrid[0:bh, 0:bw].astype(np.float32)
    for cx, cy, r, c, a in [(0.28, 0.45, 0.38, "#2E0C0A", 0.45), (0.68, 0.58, 0.32, "#8A3A28", 0.28), (0.48, 0.40, 0.55, "#4A1410", 0.20)]:
        d = np.sqrt(((X / bw - cx) / r) ** 2 + ((Y / bh - cy) / r) ** 2)
        k = np.clip(1 - d, 0, 1) * a
        col = col * (1 - k[..., None]) + hexrgb(c)[None, None, :] * k[..., None]
    # pigment grain + dry-brush streaks (multiply)
    rng = np.random.default_rng(11)
    grain = rng.random((bh, bw)).astype(np.float32)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    streak = smooth_noise(bh, bw, 2.5, 90, 21)
    mult = 1 - 0.22 * (grain - 0.5) * 2 * 0.5 - 0.18 * (streak - 0.5)
    col = np.clip(col * mult[..., None], 0, 255)
    a = np.clip(mask * alp, 0, 1)
    rgba = np.dstack([col, a * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA"), bw, bh

_STRIKE = None
def strike_layer(frame):
    global _STRIKE
    s0, s1, c0, c1 = CR["strokeEnterStart"], CR["strokeEnterEnd"], CR["strokeClearStart"], CR["strokeClearEnd"]
    if frame < s0 or frame >= c1:
        return None
    if _STRIKE is None:
        _STRIKE = build_strike_rgba()
    img, bw, bh = _STRIKE
    lead = interp(frame, s0, s1, 0, 1, E_DRAG)
    clr = interp(frame, c0, c1, 0, 1, E_OUT)
    vis = lead * (1 - clr)
    op = CR["peakOpacity"] * interp(frame, c0, c1, 1, 0, E_OUT)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vw = int(round(bw * vis))
    if vw <= 0:
        return None
    piece = img.crop((0, 0, vw, bh))
    a = np.asarray(piece.getchannel("A"), np.float32) * op
    piece.putalpha(Image.fromarray(a.astype(np.uint8)))
    x0 = int(round((W - bw) / 2 + CR["offsetX"])); y0 = int(round(H * CR["topPercent"] / 100 - bh / 2))
    layer.alpha_composite(piece, (x0, y0))
    # soft leading-edge tip bloom while dragging
    if 0 < lead < 1:
        tip = interp(lead, 0, 0.15, 0.35, 0.55) if lead < 0.15 else (interp(lead, 0.15, 0.85, 0.55, 0.4) if lead < 0.85 else interp(lead, 0.85, 1, 0.4, 0))
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(bl)
        cx = x0 + vw; cy = y0 + bh / 2; rx = 28 / 1000 * bw; ry = 42 / 200 * bh
        dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=tuple(hexrgb(CR["mid"]).astype(int)) + (int(255 * tip * 0.55 * op),))
        bl = bl.filter(ImageFilter.GaussianBlur(6))
        layer.alpha_composite(bl)
    return layer

_GLYPHS = None
def title_layout():
    global _GLYPHS
    if _GLYPHS is not None:
        return _GLYPHS
    fs = CR["fontSize"]; font = ImageFont.truetype(F_SEMI, fs)
    lines = CR["title"].split("\n"); track = CR["trackingEm"] * fs
    asc, desc = font.getmetrics()
    line_h = TITLE_LINE_H * fs; gap = round(fs * 0.04)
    block_h = len(lines) * line_h + (len(lines) - 1) * gap
    cy = H * CR["topPercent"] / 100 + CR["nudgeY"]
    top = cy - block_h / 2
    flat = sum(len(l) for l in lines); last = max(flat - 1, 1)
    glyphs = []; gi = 0
    cap_h = font.getbbox("H")[3] - font.getbbox("H")[1]
    for li, line in enumerate(lines):
        widths = [font.getlength(ch) for ch in line]
        total = sum(widths) + track * (len(line) - 1)
        x = W / 2 + CR["offsetX"] - total / 2
        line_mid = top + li * (line_h + gap) + line_h / 2
        for ch, wch in zip(line, widths):
            if ch != " ":
                pad = 12
                spr = Image.new("RGBA", (int(wch + 2 * pad), asc + desc + 2 * pad), (0, 0, 0, 0))
                sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
                ImageDraw.Draw(sh).text((pad, pad + 2), ch, font=font, fill=(0, 0, 0, 115))
                sh = sh.filter(ImageFilter.GaussianBlur(1.0))
                spr.alpha_composite(sh)
                ImageDraw.Draw(spr).text((pad, pad), ch, font=font, fill=CR["color"] + (255,))
                # place so cap-height centre sits on line_mid
                hb = font.getbbox("H")
                y_img = line_mid - (hb[1] + cap_h / 2) - pad
                glyphs.append({"spr": spr, "x": x - pad, "y": y_img, "lx": gi / last})
            x += wch + track; gi += 1
    _GLYPHS = glyphs
    return glyphs

def title_layer(frame):
    c = CR
    if frame >= c["exitEnd"]:
        return None
    lead = interp(frame, c["strokeEnterStart"], c["strokeEnterEnd"], 0, 1, E_DRAG)
    if frame < c["manifestStart"] and lead <= 0:
        return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); any_on = False
    for g in title_layout():
        lx = g["lx"]
        edge_pass = c["strokeEnterStart"] + lx * (c["strokeEnterEnd"] - c["strokeEnterStart"])
        li0 = max(c["manifestStart"], edge_pass + c["afterEdgeLagFrames"])
        li1 = min(c["manifestEnd"], li0 + c["letterSettleFrames"])
        op = interp(frame, li0, li1, 0, 1, E_IN); y = interp(frame, li0, li1, c["settleYPx"], 0, E_IN)
        sc = interp(frame, li0, li1, c["scaleFrom"], c["scaleTo"], E_IN)
        if c["manifestEnd"] <= frame < c["exitStart"]:
            op, y, sc = 1.0, 0.0, c["scaleTo"]
        if frame >= c["exitStart"]:
            span = c["exitEnd"] - c["exitStart"]
            le0 = c["exitStart"] + (1 - lx) * span * 0.45; le1 = min(c["exitEnd"], le0 + span * 0.55)
            op = op * interp(frame, le0, le1, 1, 0, E_OUT)
            y = interp(frame, le0, le1, 0, -c["settleYPx"] * 0.85, E_OUT)
            sc = interp(frame, le0, le1, c["scaleTo"], c["exitScaleTo"], E_OUT)
        if op < 0.01:
            continue
        spr = g["spr"]; sw, sh = spr.size
        if abs(sc - 1) > 1e-3:
            nw, nh = max(1, round(sw * sc)), max(1, round(sh * sc))
            spr2 = spr.resize((nw, nh), Image.Resampling.LANCZOS)
            ox = g["x"] + (sw - nw) * 0.5; oy = g["y"] + (sh - nh) * 0.7
        else:
            spr2 = spr; ox, oy = g["x"], g["y"]
        a = np.asarray(spr2.getchannel("A"), np.float32) * op
        spr2 = spr2.copy(); spr2.putalpha(Image.fromarray(a.astype(np.uint8)))
        layer.alpha_composite(spr2, (int(round(ox)), int(round(oy + y))))
        any_on = True
    return layer if any_on else None


# ------------------------------------------------------------------ credit (house credit card type, v1 builder), text per SeqR prompt Flags: "Tacitus, Annals 2.55" during L02 on the opener
F_SEMI_CR = FONT_DIR + "SourceSerifPro-Semibold.ttf"
CREDIT = dict(lines=["Tacitus, Annals 2.55"], fs=44, y0=300.0, gap=60.0, scrim_a=0.42, scrim_blur=26, fade_in_f=12, fade_out_f=10, delay_f=0,
              seg="R", on_word=widx("According to Tacitus,"), enabled=not ARGS.no_credit)
_CR = {}
def credit_png():
    if "c" in _CR: return _CR["c"]
    font = ImageFont.truetype(F_SEMI_CR, CREDIT["fs"]); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pos = []
    for k, ln in enumerate(CREDIT["lines"]):
        tw = font.getlength(ln); pos.append((ln, (W - tw) / 2.0, CREDIT["y0"] + k * CREDIT["gap"], tw))
    x0 = min(p[1] for p in pos); x1 = max(p[1] + p[3] for p in pos); y0 = pos[0][2]; y1 = pos[-1][2] + CREDIT["fs"] * 1.15
    sm = Image.new("L", (W, H), 0); ImageDraw.Draw(sm).rounded_rectangle((x0 - 40, y0 - 16, x1 + 40, y1 + 14), radius=36, fill=int(255 * CREDIT["scrim_a"]))
    sm = sm.filter(ImageFilter.GaussianBlur(CREDIT["scrim_blur"])); ov = Image.merge("RGBA", [Image.new("L", (W, H), v) for v in (14, 11, 9)] + [sm])
    for blur, alpha, oy in [(10, 0.55, 3), (5, 0.45, 2)]:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        for ln, x, y, _ in pos: d.text((x, y + oy), ln, font=font, fill=(0, 0, 0, int(255 * alpha)))
        ov = Image.alpha_composite(ov, sh.filter(ImageFilter.GaussianBlur(blur)))
    d = ImageDraw.Draw(ov)
    for ln, x, y, _ in pos:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: d.text((x + dx, y + dy), ln, font=font, fill=(0, 0, 0, 105))
        d.text((x, y), ln, font=font, fill=(243, 237, 224, 240))
    CREDIT["box"] = [round(x0 - 40), round(y0 - 16), round(x1 + 40), round(y1 + 14)]
    _CR["c"] = ov; return ov
def credit_layer(seg, fi):
    if not CREDIT["enabled"] or seg["id"] != CREDIT["seg"]: return None
    g0 = fob(words[CREDIT["on_word"]]["start"]); assert g0 >= CR["exitEnd"], "credit would overlap the title"
    k = seg["f0"] + fi - g0
    if k < 0: return None
    a = _ss((k + 1) / CREDIT["fade_in_f"]) * _ss((seg["frames"] - fi) / CREDIT["fade_out_f"])
    if a <= 0.0: return None
    ov = credit_png()
    if a >= 1.0: return ov
    al = np.asarray(ov.getchannel("A"), np.float32) * a; ov = ov.copy(); ov.putalpha(Image.fromarray(al.astype(np.uint8))); return ov
TITLE_SEG = segs[0]["id"]   # Chronicle Reveal on the OPENING plate
def overlay_for(seg, gf):
    fi = gf - seg["f0"]
    layers = [x for x in (credit_layer(seg, fi),) if x is not None]
    if seg["id"] == TITLE_SEG: layers += [l for l in (strike_layer(gf), title_layer(gf)) if l is not None]
    if not layers: return None
    out = layers[0].copy()
    for x in layers[1:]: out.alpha_composite(x)
    return out

# ------------------------------------------------------------------ engine (LOCKED b3 file untouched; configs from make_masks_germanicus_v1b.py)
def render_segment(seg):
    sid, nfr = seg["id"], seg["frames"]; dst = CLIPS / f"{sid}.mp4"
    if dst.exists(): return sid, -1
    cmd = ["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-frames:v", str(nfr), "-an", *ENC_INTER, "-r", str(FPS), str(dst)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    e3 = K.MM_engine().Engine(json.load(open(seg["b3"]))) if seg["b3"] else None
    if e3 is not None: assert Path(json.load(open(seg["b3"]))["plate"]) == Path(seg["plate"]), (sid, seg["plate"])
    box = PLATE_CROP[seg["plate"]]["box"]
    base = None if e3 else base_2x(seg)
    for fi in range(nfr):
        u = fi / max(nfr - 1, 1); t = fi / FPS; gf = seg["f0"] + fi
        if base is None:
            img = Image.fromarray(np.clip(np.rint(e3.render(t)[0]), 0, 255).astype(np.uint8))
            frame = cam_frame(prepare_cover(img.crop(box)), seg, u, t)
        else: frame = cam_frame(base, seg, u, t)
        ov = overlay_for(seg, gf)
        if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait(): raise SystemExit(f"encode fail {sid}")
    return sid, nfr

# ------------------------------------------------------------------ captions: Day 17 auto_chunks on the script tokens, word for word; all speech ends before the outro
spans = []; wi = 0
for ch in auto_chunks(DISP):
    toks = ch.split(); assert DISP[wi:wi + len(toks)] == toks; spans.append((wi, wi + len(toks) - 1)); wi += len(toks)
assert wi == len(DISP)
OUTRO_T = SEG_BY_ID["OUTRO"]["start"]
def seg_of(t):
    for s in segs:
        if s["start"] - 1e-6 <= t < s["end"]: return s["id"]
    return segs[-1]["id"]
TITLE_ON_S, TITLE_OFF_S = CR["strokeEnterStart"] / FPS, CR["exitEnd"] / FPS
ass = ["[Script Info]", f"Title: Posterity Germanicus v5 ROUGH {ARGS.tag}", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Default,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,400,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def srt_time(t):
    ms = int(round(max(0.0, t) * 1000)); s, ms = divmod(ms, 1000); m, s = divmod(s, 60); h, m = divmod(m, 60); return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
cap_events = []; srt = []; srt_full = []
for k, (a, b) in enumerate(spans):
    st = 0.0 if k == 0 else words[a]["start"]
    en = words[b]["end"] + 0.30
    if k + 1 < len(spans): en = min(en, words[spans[k + 1][0]]["start"] - 0.04)
    en = min(en, OUTRO_T); txt = ass_line(list(range(a, b + 1)))
    _cw = [x.strip(",.").upper() for x in join_disp(range(a, b + 1)).split()]; _tt = " " + norm(CR["title"].replace("\n", " ")) + " "
    _rep = any(" " + " ".join(_cw[i_:i_ + 3]) + " " in _tt for i_ in range(max(len(_cw) - 2, 0)))
    hidden = st >= TITLE_ON_S - 0.3 and en <= TITLE_OFF_S and _rep   # v1e rule
    ass.append(f"{'Comment' if hidden else 'Dialogue'}: 0,{ass_time(st)},{ass_time(en)},Default,,0,0,0,,{txt}")
    srt_full.append(f"{k + 1}\n{srt_time(st)} --> {srt_time(en)}\n{join_disp(range(a, b + 1))}\n")
    if not hidden: srt.append(f"{len(srt) + 1}\n{srt_time(st)} --> {srt_time(en)}\n{join_disp(range(a, b + 1))}\n")
    cap_events.append({"start": st, "end": en, "seg": seg_of(st + 0.01), "first_wi": a, "last_wi": b, "text": join_disp(range(a, b + 1)), "ass": txt, "hidden_under_title": hidden})
_CAPDIR = BUILD if ARGS.scratch else EDIT
ASS_OUT = _CAPDIR / f"germanicus_v5_rough_{ARGS.tag}.ass"; SRT_OUT = _CAPDIR / f"germanicus_v5_rough_{ARGS.tag}.srt"; SRT_FULL = _CAPDIR / f"germanicus_v5_rough_{ARGS.tag}_full.srt"
ass_txt = "\n".join(ass) + "\n"; srt_txt = "\n".join(srt); srt_full_txt = "\n".join(srt_full)
for pth, txt in ((ASS_OUT, ass_txt), (SRT_OUT, srt_txt), (SRT_FULL, srt_full_txt)):
    if pth.exists(): assert pth.read_text() == txt, f"{pth} exists with different content: use a new --tag"
    else: pth.write_text(txt)
def ass_filter():
    e = str(ASS_OUT).replace("\\", "/").replace(":", "\\:").replace("'", "\\'"); return f"ass='{e}'"
cap_words = " ".join(e["text"] for e in cap_events)
assert norm(cap_words) == norm(SCRIPT_DISP.read_text()), "captions != narration"
HIDDEN_CUES = [k for k, e in enumerate(cap_events) if e["hidden_under_title"]]
print("caption cues:", len(cap_events), "hidden under title:", HIDDEN_CUES, [cap_events[k]["text"] for k in HIDDEN_CUES])
for e in cap_events: assert e["start"] <= words[e["first_wi"]]["start"] + 1e-6 and e["end"] > words[e["first_wi"]]["start"], e
assert cap_events[-1]["end"] <= OUTRO_T + 1e-6
print(f"speech_end={t_speech_end:.3f} package={package:.3f} frames={total_frames} outro_f0={OUTRO_F0}")
for s in segs: print(f"  {s['id']:5} {Path(s['plate']).name:28} {s['f0']:5d} {s['start']:7.3f}-{s['end']:7.3f} {s['duration']:6.3f}s {s['frames']:4d}f first='{s['first_word']}'")

PLATE_CROP = {}
for s in segs:
    if s["plate"] not in PLATE_CROP:
        if Path(s["plate"]).parent == PREPPED:   # placeholder cards + reframes: made here, no bars
            w_, h_ = Image.open(s["plate"]).size; PLATE_CROP[s["plate"]] = {"crop_px": {"L": 0, "R": 0, "T": 0, "B": 0}, "box": (0, 0, w_, h_)}
        elif (PREPPED / Path(s["plate"]).name).exists():
            im = Image.open(s["plate"]); _, info = detect_bars(np.asarray(im.convert("RGB"))); w_, h_ = im.size
            PLATE_CROP[s["plate"]] = {"crop_px": {k: v["crop_px"] for k, v in info.items()}, "box": (info["L"]["crop_px"], info["T"]["crop_px"], w_ - info["R"]["crop_px"], h_ - info["B"]["crop_px"])}
        else: _, PLATE_CROP[s["plate"]] = cropped_plate(s["plate"])
    s["prepped"] = s["plate"] if Path(s["plate"]).parent == PREPPED else str(PREPPED / Path(s["plate"]).name); s["plate_md5"] = md5f(s["plate"])
for p, c in PLATE_CROP.items():
    if any(c["crop_px"].values()): print("  bar crop", Path(p).name, c["crop_px"])
TL = BUILD / "timeline.json"
if not TL.exists():
    json.dump({"segments": segs, "captions": cap_events, "speech_end": t_speech_end, "package": package, "frames": total_frames, "short_shots": SHORT, "gap_flags": GAP_FLAGS,
               "plate_crops": PLATE_CROP, "credit": CREDIT, "title": CR, "reframes": REFRAMES, "placeholders": PLACEHOLDERS, "hidden_cues": HIDDEN_CUES,
               "taildip": [TAILDIP_T0, TAILDIP_T1, ARGS.tail_dip_db], "fade": [fade_start, fade_end]}, open(TL, "x"), indent=1, default=str)

KEY_NAMES = {"germanicus", "piso", "tacitus", "antioch", "armenia", "syria", "rome", "rome's", "senate", "spain", "bronze", "murder", "poisoned", "poisoning", "spells", "lead", "tablets",
             "walls", "sword", "dead", "rebel", "unproved", "killer", "accusers", "condemned", "judgement", "warships", "storm"}
KEY_WORDS = sorted(set([i for i, w in enumerate(words) if w["word"].endswith((".", "?", "!", ":"))] + [i for i, w in enumerate(words) if w["word"].strip(".,:;?!").lower() in KEY_NAMES]))
FUNC = {"the", "a", "was", "as", "he", "had", "his", "been"}
WORD_CHECK = [int(i) for i in ARGS.word_check.split(",")] if ARGS.word_check else [i for i in L22_I + L23_I if words[i]["word"].strip(".,").lower() not in FUNC]
DIP_LO, DIP_HI, DIP_REL = 900.0, 4500.0, 0.25
from scipy.signal import butter as _bt; SOS_BAND = _bt(4, [1000, 4000], "bandpass", fs=SR, output="sos")
def ebur_arr(x):
    x = np.asarray(x, np.float32); x = x[:, None] if x.ndim == 1 else x
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[1]), "-i", "pipe:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       input=np.ascontiguousarray(x, np.float32).tobytes(), capture_output=True); Iv = TP = None; summ = False
    for ln in p.stderr.decode().splitlines():
        if "Summary:" in ln: summ = True
        if summ and ln.strip().startswith("I:"): Iv = float(ln.split("I:")[1].split("LUFS")[0])
        if summ and ln.strip().startswith("Peak:"): TP = float(ln.split("Peak:")[1].split("dBFS")[0])
    return Iv, TP
END_A, END_B = words[L22_I[0]]["start"] - 0.05, t_speech_end + 0.05   # L22+L23
BODY_A, BODY_B = 0.0, words[L21_I[-1]]["end"] + 0.05                   # L01-L21
def ending_delta(x):
    x = np.asarray(x); bI, _ = ebur_arr(x[int(BODY_A * SR):int(BODY_B * SR)]); eI, _ = ebur_arr(x[int(END_A * SR):int(END_B * SR)]); return eI - bI, bI, eI
SFX_DIR = ROOT / "sfx"
SFX_SRC = {"shouts": {"file": str(SFX_DIR / "oga_starninjas_crowd_shouting_CC0.ogg"), "md5": "8ed53bd014f92a59eb4a93467df3a059", "page": "https://opengameart.org/content/crowd-shoutingspeaking-ambience", "author": "StarNinjas", "licence": "CC0 1.0"},
           "clashes": {"file": str(SFX_DIR / "oga_starninjas_sword_clash_CC0.zip") + " -> sfx/sword_clash/*.ogg", "md5": "3b82c7072f96dcec53d24072bf74a7b9", "page": "https://opengameart.org/content/20-sword-sound-effects-attacks-and-clashes", "author": "StarNinjas", "licence": "CC0 1.0"}}
def build_sfx(nb, t0, t1, fade=0.3):
    # v5: distant battle ambience for SeqC only: crowd shouts + sparse sword clashes, HPF 150 / LPF 2.8 kHz, small room tail, 1-4 kHz carve, raised-cosine fades at the cuts
    from scipy.signal import butter, sosfiltfilt, resample_poly
    assert md5f(SFX_DIR / "oga_starninjas_crowd_shouting_CC0.ogg") == SFX_SRC["shouts"]["md5"] and md5f(SFX_DIR / "oga_starninjas_sword_clash_CC0.zip") == SFX_SRC["clashes"]["md5"]
    def rd(f):
        y, sr = sf.read(str(f), dtype="float64", always_2d=True); y = y[:, :2] if y.shape[1] >= 2 else np.repeat(y, 2, 1)
        gq = math.gcd(SR, sr); return y if sr == SR else resample_poly(y, SR // gq, sr // gq, axis=0)
    L = int((t1 - t0) * SR); out = np.zeros((L + SR, 2))
    sh = rd(SFX_DIR / "oga_starninjas_crowd_shouting_CC0.ogg"); a = int(3.0 * SR); sh = sh[a:a + L + SR]; out[:len(sh)] += sh / np.sqrt((sh ** 2).mean())
    rng = np.random.default_rng(55); hits = [(0.25, 1), (0.95, 2), (1.6, 5), (2.3, 3), (2.85, 1), (3.5, 2), (4.15, 5)]
    for (dt, k) in hits:
        c = rd(SFX_DIR / "sword_clash" / f"sword_clash.{k}.ogg"); c = c / np.abs(c).max(); g_ = 10 ** (rng.uniform(-9, -4) / 20); pan = rng.uniform(-0.35, 0.35)
        i0 = int(dt * SR); n_ = min(len(c), len(out) - i0); out[i0:i0 + n_, 0] += c[:n_, 0] * g_ * (1 - pan); out[i0:i0 + n_, 1] += c[:n_, 1] * g_ * (1 + pan)
    out = sosfiltfilt(butter(2, 150, "highpass", fs=SR, output="sos"), out, axis=0); out = sosfiltfilt(butter(4, 2800, "lowpass", fs=SR, output="sos"), out, axis=0)
    ir = rng.standard_normal((int(0.9 * SR), 2)) * np.exp(-np.arange(int(0.9 * SR)) / (0.22 * SR))[:, None]; ir /= np.sqrt((ir ** 2).sum(0))
    from scipy.signal import fftconvolve
    wet = np.stack([fftconvolve(out[:, ch], ir[:, ch])[:len(out)] for ch in range(2)], 1); out = 0.65 * out + 0.55 * wet
    kc = 1 - 10 ** (-ARGS.sfx_carve_db / 20); out = out - kc * sosfiltfilt(butter(2, [1000, 4000], "bandpass", fs=SR, output="sos"), out, axis=0)
    out = out[:L]; tt = np.arange(L) / SR; w = np.clip(tt / fade, 0, 1) * np.clip((t1 - t0 - tt) / fade, 0, 1); out = out * (0.5 - 0.5 * np.cos(np.pi * w))[:, None]
    full = np.zeros((nb, 2)); i0 = int(round(t0 * SR)); full[i0:i0 + L] = out[:max(0, min(L, nb - i0))]
    return full
def build_audio():
    AAC = AUDIO / "mix_aac256.m4a"; AMETA = AUDIO / "audio_meta.json"
    if AAC.exists() and AMETA.exists(): return AAC, json.load(open(AMETA))
    assert md5f(ARGS.music) == MUSIC_MD5
    mdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ARGS.music)], capture_output=True, text=True).stdout)
    assert ARGS.music_offset + package <= mdur - 0.5, ("bed window runs past the cue", ARGS.music_offset, package, mdur)
    vo_pad = new(AUDIO / "vo_package.wav")
    ffn("-i", str(VO_SRC), "-af", f"aresample={SR},apad=whole_dur={package:.6f},atrim=0:{package:.6f},aformat=sample_fmts=fltp:channel_layouts=mono", "-c:a", "pcm_s24le", str(vo_pad))
    src_delta = ending_delta(sf.read(vo_pad, dtype="float64")[0])
    vo_I, _ = ebur(vo_pad, None, t_speech_end + 0.05); vo_comp = new(AUDIO / "vo_comp.wav")
    ffn("-i", str(vo_pad), "-af", f"volume={VO_STAGE_LUFS - vo_I:.3f}dB,{VO_COMP}", "-c:a", "pcm_f32le", str(vo_comp))
    vc, _ = sf.read(vo_comp, dtype="float64"); comp_delta = ending_delta(vc)
    # v5: restore the source ending drop if the compressor shrank it -- gain change ONLY inside the silent L21->L22 gap (raised cosine), held to the end
    g0, g1 = words[L21_I[-1]]["end"] + 0.04, words[L22_I[0]]["start"] - 0.04; corr = src_delta[0] - comp_delta[0]
    tt = np.arange(len(vc)) / SR; rr = np.clip((tt - g0) / (g1 - g0), 0, 1); vc = vc * 10 ** (corr * (0.5 - 0.5 * np.cos(np.pi * rr)) / 20)
    cI, _ = ebur_arr(vc[: int((t_speech_end + 0.05) * SR)]); vc = vc * 10 ** ((VO_STAGE_LUFS - cI) / 20)
    vo_staged = new(AUDIO / "vo_staged.wav"); sf.write(vo_staged, vc.astype(np.float32), SR, subtype="FLOAT"); staged_delta = ending_delta(vc)
    print(f"  VO ending delta: source {src_delta[0]:.2f}  after comp {comp_delta[0]:.2f}  restore {corr:+.2f} dB in gap {g0:.3f}-{g1:.3f}  staged {staged_delta[0]:.2f}", flush=True)
    music = new(AUDIO / "music_seg.wav")
    ffn("-ss", f"{ARGS.music_offset}", "-t", f"{package + 1:.3f}", "-i", str(ARGS.music), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_f32le", str(music))
    bed_flat = new(AUDIO / "bed_flat.wav")
    ffn("-i", str(music), "-af",
        f"atrim=start=0:duration={package:.6f},asetpts=PTS-STARTPTS,aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"highpass=f={BED_HPF_HZ},highpass=f={BED_HPF_HZ},{BED_EQ},afade=t=in:st=0:d={BED_FADEIN_S:g}:curve=cub,aresample={SR},apad=whole_dur={package:.6f}",
        "-t", f"{package:.6f}", "-c:a", "pcm_f32le", str(bed_flat))
    b, _ = sf.read(bed_flat, dtype="float64"); nb = len(b); t = np.arange(nb) / SR
    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import butter, sosfiltfilt
    def rc(x): x = np.clip(x, 0, 1); return 0.5 - 0.5 * np.cos(np.pi * x)
    sp_t0, sp_t1 = words[0]["start"], t_speech_end
    env = np.where(t < sp_t0, rc((t - (sp_t0 - DIP_REL)) / DIP_REL), 1.0)
    kdip = 1 - 10 ** (-ARGS.speech_dip_db / 20)
    b = b - kdip * sosfiltfilt(butter(2, [DIP_LO, DIP_HI], "bandpass", fs=SR, output="sos"), b, axis=0) * env[:, None]
    D = SR // 100; tk = np.arange(0, nb, D) / SR; live = (tk >= BED_FADEIN_S) & (tk <= fade_start)
    i_live0, i_live1 = int(np.argmax(live)), int(np.where(live)[0][-1])
    def cenv(x, win):
        m = x.mean(1); c = np.concatenate([[0], np.cumsum(m ** 2)]); k = np.arange(0, nb, D); h = int(win * SR / 2); a_ = np.clip(k - h, 0, nb); z_ = np.clip(k + h, 0, nb)
        return 10 * np.log10((c[z_] - c[a_]) / np.maximum(z_ - a_, 1) + 1e-12)
    def hold(gk): gk = gk.copy(); gk[:i_live0] = gk[i_live0]; gk[i_live1 + 1:] = gk[i_live1]; return gk
    def apply(x, gk): return x * (10 ** (np.interp(t, tk, gk) / 20))[:, None]
    def cenv_ch(x, win):
        out = []
        for ch in range(x.shape[1]):
            c = np.concatenate([[0], np.cumsum(x[:, ch] ** 2)]); k = np.arange(0, nb, D); h = int(win * SR / 2); a_ = np.clip(k - h, 0, nb); z_ = np.clip(k + h, 0, nb)
            out.append(10 * np.log10((c[z_] - c[a_]) / np.maximum(z_ - a_, 1) + 1e-12))
        return np.array(out)
    SL = ARGS.rider_slope_db_s / 100.0
    def ratelim(gk):
        y = gk.copy()
        for i in range(1, len(y)): y[i] = min(max(y[i], y[i - 1] - SL), y[i - 1] + SL)
        for i in range(len(y) - 2, -1, -1): y[i] = min(max(y[i], y[i + 1] - SL), y[i + 1] + SL)
        return y
    for spec_ in [x for x in ARGS.narrow.split(",") if x]:
        t0n, t1n, dbn = map(float, spec_.split(":")); wn = rc((t - t0n) / 0.3) * rc((t1n - t) / 0.3); ks = 1 - (1 - 10 ** (-dbn / 20)) * wn
        Mn = 0.5 * (b[:, 0] + b[:, 1]); Sn = 0.5 * (b[:, 0] - b[:, 1]) * ks; b = np.stack([Mn + Sn, Mn - Sn], 1)
    g1 = np.zeros(len(tk)); g2 = np.zeros(len(tk))
    for _ in range(RIDER2_IT + 10):
        ec = cenv_ch(apply(b, g2), 1.0); dev = ec - np.median(ec[:, live], axis=1, keepdims=True); err = -dev.mean(0)
        if ARGS.rider_mode == "mix": em = cenv(apply(b, g2), 1.0); err = 0.5 * (err - (em - np.median(em[live])))
        err[~live] = 0.0
        g2 = ratelim(np.clip(gaussian_filter1d(hold(g2 + 0.7 * err), RIDER2_SIG * 100, mode="nearest"), -RIDER2_CLAMP, RIDER2_CLAMP))
    g2 = ratelim(g2); b1 = b; tgt_db = float(np.median(cenv_ch(apply(b, g2), 1.0)[:, live]))
    b = apply(b1, g2); lev_db = g1 + g2
    np.save(new(AUDIO / "bed_rider_db_100hz.npy"), np.stack([tk, g1, g2]).astype(np.float32))
    bI, _ = ebur_arr(b[int(BED_FADEIN_S * SR):int(fade_start * SR)]); b = b * 10 ** ((ARGS.bed_norm_lufs - bI) / 20)
    phrases = []
    depth = np.full(nb, RIDE_DB); depth_v1 = depth.copy()
    def fade_g(gg):
        gg = gg.copy()
        gg *= 10 ** (-ARGS.tail_dip_db * rc((t - TAILDIP_T0) / (TAILDIP_T1 - TAILDIP_T0)) / 20)   # v5 tail dip follows the VO ending drop
        mk = (t >= fade_start) & (t < fade_end - TAPER_S); gg[mk] *= 10 ** (-FADE_DEPTH_DB * (t[mk] - fade_start) / (fade_end - TAPER_S - fade_start) / 20)
        tp = (t >= fade_end - TAPER_S) & (t < fade_end); gg[tp] *= 10 ** (-FADE_DEPTH_DB / 20) * 0.5 * (1 + np.cos(np.pi * (t[tp] - (fade_end - TAPER_S)) / TAPER_S)); gg[t >= fade_end] = 0.0
        return gg
    g = fade_g(10 ** (-depth_v1 / 20))
    SC0, SC1 = SEG_BY_ID["C"]["start"], SEG_BY_ID["C"]["end"]; sfx_meta = {"used": False}
    if ARGS.no_sfx: sfx = np.zeros((nb, 2)); sfx_meta["note"] = "skipped (--no-sfx)"
    else:
        sfx = build_sfx(nb, SC0, SC1); a_, z_ = int((SC0 + 0.3) * SR), int((SC1 - 0.3) * SR)
        bw = (b * g[:, None])[a_:z_]; bwI = 10 * np.log10((bw ** 2).mean() + 1e-20); swI = 10 * np.log10((sfx[a_:z_] ** 2).mean() + 1e-20)
        sfx = sfx * 10 ** ((bwI + ARGS.sfx_rel_db - swI) / 20)
        sfx_meta = {"used": True, "window_s": [SC0, SC1], "fade_s": 0.3, "rel_to_bed_db_rms": ARGS.sfx_rel_db, "carve_1_4k_db": ARGS.sfx_carve_db, "sources": SFX_SRC,
                    "chain": "shouts 3.0 s excerpt + 7 clashes (-9..-4 dB, pan +-0.35) -> HPF150 -> LPF2.8k -> 0.9 s room tail -> 1-4 kHz carve -> level -> raised-cosine 0.3 s fades"}
    assert not np.any(sfx[: int(SC0 * SR) - 1]) and not np.any(sfx[int(SC1 * SR) + 1:]), "SFX outside SeqC"
    vo, _ = sf.read(vo_staged, dtype="float64"); nmin = min(len(vo), nb); vo = vo[:nmin]
    def run(bed_db, mgain):
        bed = (b[:nmin] * g[:nmin, None]) * 10 ** (bed_db / 20); sx = sfx[:nmin] * 10 ** (bed_db / 20)
        pre = 0.70710678 * vo[:, None].repeat(2, 1) + bed + sx
        six = np.concatenate([pre, 0.70710678 * vo[:, None] * 1e-3, bed * 1e-3, sx * 1e-3], 1).astype(np.float32)
        p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "7", "-i", "pipe:0", "-af",
                            f"volume={mgain:.3f}dB,aresample=192000,alimiter=limit={10 ** (LIMIT_DB / 20):.4f}:attack=3:release=60:level=disabled:asc=1,aresample={SR}",
                            "-f", "f32le", "-ac", "7", "pipe:1"], input=six.tobytes(), capture_output=True, check=True)
        o = np.frombuffer(p.stdout, np.float32).reshape(-1, 7).astype(np.float64)[:nmin]; run.sfx_post = o[:, 5:7] * 1e3; mix = o[:, :2]; vL = o[:, 2] * 1e3; bL = np.abs(o[:, 3:5]).max(1) * 1e3
        rows = []
        for i, w in enumerate(words):
            a_, z_ = int(w["start"] * SR), int(w["end"] * SR); a2, z2 = max(0, int((w["start"] - 0.3) * SR)), int((w["end"] + 0.3) * SR)
            rows.append((i, w["word"], round(w["start"], 3), round(float(20 * np.log10(np.abs(vL[a_:z_]).max() + 1e-12) - 20 * np.log10(np.abs(bL[a2:z2]).max() + 1e-12)), 2)))
        return mix, rows, pre, bed, vL, o[:, 3:5] * 1e3
    def band_rows(vL, bL):
        vb = sosfiltfilt(SOS_BAND, vL); bb2 = sosfiltfilt(SOS_BAND, bL, axis=0); bbp = (bb2 ** 2).mean(1); out = []
        for i, w in enumerate(words):
            a_, z_ = int(w["start"] * SR), int(w["end"] * SR)
            out.append((i, w["word"], round(w["start"], 3), round(float(10 * np.log10((vb[a_:z_] ** 2).mean() + 1e-20) - 10 * np.log10(bbp[a_:z_].mean() + 1e-20)), 2)))
        return out
    M_I = len(words) - 1
    def frame_stats(vL, bL):
        vb = sosfiltfilt(SOS_BAND, vL); bb2 = sosfiltfilt(SOS_BAND, bL, axis=0); bbp = (bb2 ** 2).mean(1); vbp = vb ** 2 * 1.0
        hop = int(0.05 * SR); fr = []
        for w in words:
            for k in range(int(w["start"] * SR), int(w["end"] * SR) - hop + 1, hop): fr.append((vbp[k:k + hop].mean(), bbp[k:k + hop].mean()))
        fr = np.array(fr); vdb = 10 * np.log10(fr[:, 0] + 1e-20); bdb = 10 * np.log10(fr[:, 1] + 1e-20)
        voiced = vdb >= np.percentile(vdb, 99) - 35.0; m = (vdb - bdb)[voiced]
        return dict(n_frames=int(voiced.sum()), pct_ge_6db=round(100 * float((m >= 6).mean()), 2), pct_lt_0db=round(100 * float((m < 0).mean()), 2),
                    median=round(float(np.median(m)), 2), p10=round(float(np.percentile(m, 10)), 2), p5=round(float(np.percentile(m, 5)), 2))
    def bed_1s(bst):
        m = bst.mean(1); c = np.concatenate([[0], np.cumsum(m ** 2)]); idx = np.arange(0, len(m) - SR, SR // 4)
        return idx / SR, 10 * np.log10((c[idx + SR] - c[idx]) / SR + 1e-20)
    def bed_const(bst):   # v5: window ends 1 s before the deliberate tail dip
        T1, L1 = bed_1s(bst); mk = (T1 >= BED_FADEIN_S) & (T1 + 1.0 <= TAILDIP_T0 + 1e-9); Ts, Ls = T1[mk], L1[mk]; med = float(np.median(Ls))
        rise1 = Ls[4:] - Ls[:-4]; hop = np.diff(Ls) * 4
        return dict(window="1 s RMS, 0.25 s hop, window start t in [2.5, taildip_t0-1]", n=int(mk.sum()), median_db=round(med, 2), max_dev_db=round(float(np.abs(Ls - med).max()), 2),
                    max_dev_at_s=float(Ts[np.argmax(np.abs(Ls - med))]), range_db=[round(float(Ls.min()), 2), round(float(Ls.max()), 2)],
                    max_rise_per_1s_db=round(float(rise1.max()), 2), max_rise_per_1s_at_s=float(Ts[np.argmax(rise1)]),
                    max_hop_slope_db_per_s=round(float(hop.max()), 2), max_hop_slope_at_s=float(Ts[np.argmax(hop)]),
                    PASS=bool(np.abs(Ls - med).max() <= 1.0 and rise1.max() <= 1.5 and hop.max() <= 1.5))
    bed_db = 0.0; mgain = 3.0; log = []
    while True:
        for it in range(16):
            mix, rows, pre, bed, vL, bL = run(bed_db, mgain); mI, mTP = ebur_arr(mix)
            if abs(mI - MASTER_TARGET_I) <= 0.15: break
            mgain += MASTER_TARGET_I - mI
        br = band_rows(vL, bL); fs_ = frame_stats(vL, bL); mur_full = rows[M_I][3]; mur_band = br[M_I][3]
        km = [r for r in rows if r[0] in KEY_WORDS]; kmin = min(r[3] for r in km)
        log.append({"bed_db": round(bed_db, 2), "master_gain": round(mgain, 3), "I": mI, "TP": mTP, "last_word_full_peak_db": mur_full, "last_word_band_rms_db": mur_band,
                    "frames": fs_, "key_min": kmin, "bed_const": bed_const(bL)}); print("  bed try", log[-1], flush=True)
        wchk = {int(i): rows[int(i)][3] for i in WORD_CHECK}; log[-1]["word_check"] = wchk
        if mur_full >= ARGS.murder_target and mur_band >= ARGS.murder_target and fs_["pct_ge_6db"] >= ARGS.frame_target_pct and min(wchk.values(), default=99) >= ARGS.word_target: break
        assert bed_db > -24, "bed level loop did not converge"
        bed_db = round(bed_db - ARGS.bed_step_db, 2)
    mix_wav = new(AUDIO / "mix.wav"); sf.write(mix_wav, mix.astype(np.float32), SR, subtype="FLOAT"); mI, mTP = ebur(mix_wav)
    sf.write(new(AUDIO / "stem_vo_postlim.wav"), vL.astype(np.float32), SR, subtype="FLOAT"); sf.write(new(AUDIO / "stem_bed_postlim.wav"), bL.astype(np.float32), SR, subtype="FLOAT")
    sxL = run.sfx_post; sf.write(new(AUDIO / "stem_sfx_postlim.wav"), sxL.astype(np.float32), SR, subtype="FLOAT")
    if sfx_meta["used"]:
        a_, z_ = int((SC0 + 0.3) * SR), int((SC1 - 0.3) * SR); sb = sosfiltfilt(SOS_BAND, sxL, axis=0); vb_ = sosfiltfilt(SOS_BAND, vL)
        sfx_meta.update(sfx_minus_bed_db_rms=round(float(10 * np.log10((sxL[a_:z_] ** 2).mean() / (bL[a_:z_] ** 2).mean())), 2),
                        sfx_minus_vo_db_rms=round(float(10 * np.log10((sxL[a_:z_] ** 2).mean() / (vL[a_:z_] ** 2).mean() * 2)), 2),
                        word_margins_vs_sfx_1_4k=[(i, w["word"], round(float(10 * np.log10((vb_[int(w["start"] * SR):int(w["end"] * SR)] ** 2).mean() + 1e-20) - 10 * np.log10((sb[int(w["start"] * SR):int(w["end"] * SR)] ** 2).mean(1).mean() + 1e-20)), 2))
                                                  for i, w in enumerate(words) if SC0 <= w["start"] < SC1],
                        outside_window_max_abs=float(np.abs(np.concatenate([sxL[: int(SC0 * SR) - 1], sxL[int(SC1 * SR) + 1:]])).max()))
        print("  SFX", {k: v for k, v in sfx_meta.items() if k != "sources"}, flush=True)
    np.save(new(AUDIO / "bed_gain_curve_db.npy"), (20 * np.log10(g + 1e-12)).astype(np.float32))
    br = band_rows(vL, bL)
    vo_speech_I, _ = ebur(vo_staged, None, t_speech_end); BED_I, _ = ebur_arr(bL[: int(t_speech_end * SR)])
    ffn("-i", str(mix_wav), "-c:a", "aac", "-b:a", ARGS.aac_bitrate, "-ar", "48000", "-ac", "2", str(new(AAC)))
    km = [r for r in rows if r[0] in KEY_WORDS]
    mix_end = ending_delta(mix); vo_end = ending_delta(vL)
    AM = {"music": str(ARGS.music), "music_md5": MUSIC_MD5, "music_offset_s": ARGS.music_offset, "music_window_s": [ARGS.music_offset, ARGS.music_offset + package], "music_duration_s": mdur,
          "sfx_seqC": sfx_meta, "bed_loop": "none: one continuous window of the cue (no loop, no splice)", "bed_level_db": bed_db, "bed_norm_lufs": ARGS.bed_norm_lufs,
          "rider": {"type": "closed-loop 1 s RMS; mode=" + ARGS.rider_mode + " (stereo = mean of L and R dB deviations)", "win_s": 1.0, "iterations": RIDER2_IT + 10, "sigma_s": RIDER2_SIG, "clamp_db": RIDER2_CLAMP, "slope_cap_db_s": ARGS.rider_slope_db_s, "narrow": ARGS.narrow, "max_slope_db_s": float(np.abs(np.diff(lev_db)).max() * 100),
                    "target_env_db": tgt_db, "gain_range_db": [float(lev_db.min()), float(lev_db.max())], "live_s": [BED_FADEIN_S, fade_start], "order": "HPF/EQ -> fade-in -> speech dip (900-4500 Hz) -> rider -> norm -28 LUFS -> constant duck -> tail dip -> fade -> limiter"},
          "bed_constancy_post_limiter": bed_const(bL), "bed_constancy_per_channel": {"L": bed_const(bL[:, [0, 0]]), "R": bed_const(bL[:, [1, 1]])}, "duck": {"depth_db": RIDE_DB, "note": "constant for the whole package"},
          "tail_dip": {"db": ARGS.tail_dip_db, "t0": TAILDIP_T0, "t1": TAILDIP_T1, "max_slope_db_s": round(math.pi / 2 * ARGS.tail_dip_db / (TAILDIP_T1 - TAILDIP_T0), 2)},
          "vo_ending_delta": {"source": src_delta, "after_comp": comp_delta, "restore_db": corr, "staged": staged_delta, "vo_postlim": vo_end, "mix": mix_end, "ranges": {"body": [BODY_A, BODY_B], "end": [END_A, END_B]}},
          "word_check": {"words": {int(i): words[int(i)]["word"] for i in WORD_CHECK}, "target_db": ARGS.word_target, "margins": {int(i): rows[int(i)][3] for i in WORD_CHECK}},
          "last_word": {"word": words[M_I]["word"], "full_peak_margin_db": rows[M_I][3], "band_rms_margin_db": br[M_I][3], "target": ARGS.murder_target},
          "frames_1_4k": frame_stats(vL, bL), "vo": str(VO_SRC), "vo_md5": VO_MD5, "vo_over_bed_LU": vo_speech_I - BED_I,
          "master_gain_db": mgain, "limit_db": LIMIT_DB, "mix_I": mI, "mix_TP": mTP,
          "key_word_count": len(km), "key_word_min_margin_db_post_limiter": min(r[3] for r in km), "key_words_under_9db": [r for r in km if r[3] < 9.0],
          "key_word_margins_post_limiter": km, "lowest10_all_words": sorted(rows, key=lambda r: r[3])[:10], "iterations": log,
          "bed_fade": {"start": fade_start, "end": fade_end, "depth_db": FADE_DEPTH_DB}, "package": package, "speech_end": t_speech_end,
          "speech_dip": {"nominal_db": ARGS.speech_dip_db, "band_hz": [DIP_LO, DIP_HI], "filter": "butter2 bandpass, sosfiltfilt", "env": [sp_t0, sp_t1], "release_s": DIP_REL},
          "band_margins_1_4k_post_limiter_all_words": br}
    json.dump(AM, open(new(AMETA), "x"), indent=1, default=float)
    return AAC, AM

def test_frame(spec):
    sid, fi = spec.split(":"); fi = int(fi); seg = SEG_BY_ID[sid]; assert 0 <= fi < seg["frames"]; gf = seg["f0"] + fi
    qd = EDIT / f"qc_rough_v5{ARGS.tag}"; qd.mkdir(exist_ok=True); full = BUILD / f"testframe_{sid}_f{gf}_1080.png"; out = new(qd / f"testframe_{sid}_f{gf}_360x640.png")
    u = fi / max(seg["frames"] - 1, 1); t = fi / FPS
    if seg["b3"]:
        e3 = K.MM_engine().Engine(json.load(open(seg["b3"]))); img = Image.fromarray(np.clip(np.rint(e3.render(t)[0]), 0, 255).astype(np.uint8))
        frame = cam_frame(prepare_cover(img.crop(PLATE_CROP[seg["plate"]]["box"])), seg, u, t)
    else: frame = cam_frame(base_2x(seg), seg, u, t)
    ov = overlay_for(seg, gf)
    if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
    frame.save(full)
    ffn("-loop", "1", "-framerate", str(FPS), "-i", str(full), "-vf", f"setpts=PTS+{gf / FPS:.6f}/TB,{ass_filter()},scale=360:640:flags=area", "-frames:v", "1", str(out))
    full.unlink()   # own fresh scratch
    print("TEST FRAME", out, "t=%.3f" % (gf / FPS), "credit box", CREDIT.get("box"))

if __name__ == "__main__":
    if ARGS.test_frame:
        for spec in ARGS.test_frame.split(","): test_frame(spec)
        sys.exit(0)
    picture_final = WORK / "picture_final.mp4"
    if not ARGS.audio_only:
        jobs = [s for s in segs if (not ARGS.only or s["id"] in ARGS.only.split(","))]
        if not picture_final.exists():
            jobs = sorted(jobs, key=lambda s: -s["frames"] * (4 if s["b3"] else 1))
            with ProcessPoolExecutor(max_workers=ARGS.workers) as ex:
                for sid, nfr in ex.map(render_segment, jobs): print("clip", sid, nfr, flush=True)
        if ARGS.only or ARGS.scratch: sys.exit(0)
        concat = WORK / "concat.txt"
        ctxt = "".join(f"file '{CLIPS / (s['id'] + '.mp4')}'\n" for s in segs)
        if not concat.exists(): concat.write_text(ctxt)
        if not picture_final.exists():
            tmp = WORK / "picture_final.partial.mp4"
            ffn("-f", "concat", "-safe", "0", "-i", str(concat), "-vf", ass_filter(), "-an", "-frames:v", str(total_frames), *ENC_FINAL, *X_GOP30, "-r", str(FPS), str(tmp)); tmp.rename(picture_final)
        print("picture_final encoded", flush=True)
        if not ARGS.keep_clips:   # lean disk: these clips were written by THIS build into its own new build dir
            freed = 0
            for s in segs:
                c_ = CLIPS / f"{s['id']}.mp4"
                if c_.exists(): freed += c_.stat().st_size; c_.unlink()
            print(f"  deleted own intermediate clips: {freed / 1e6:.0f} MB", flush=True)
        if ARGS.picture_only: sys.exit(0)
    AAC, AM = build_audio()
    print("  BED CONSTANCY", AM["bed_constancy_post_limiter"], flush=True)
    print("  ENDING", AM["vo_ending_delta"], flush=True)
    print(f"  VO over bed {AM['vo_over_bed_LU']:.2f} LU; key-word min (post-limiter) {AM['key_word_min_margin_db_post_limiter']} dB; under 9: {AM['key_words_under_9db']}", flush=True)
    if ARGS.audio_only: sys.exit(0)
    ffn("-i", str(picture_final), "-i", str(AAC), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy", "-t", f"{package:.6f}", "-movflags", "+faststart", str(new(MASTER)))
    fI, fTP = ebur(MASTER); print(f"  muxed AAC: I={fI} TP={fTP}", flush=True); assert fTP is not None and fTP <= -1.0, fTP
    md5 = md5f(MASTER); print("MASTER", MASTER, md5, flush=True)
    json.dump({"master": str(MASTER), "md5": md5, "package": package, "frames": total_frames, "speech_end": t_speech_end, "final_I": fI, "final_TP": fTP, "audio": AM,
               "segments": segs, "captions": cap_events, "credit": CREDIT, "vo": str(VO_SRC), "vo_md5": md5f(VO_SRC), "title_top_pct": TITLE_TOP_PCT, "placeholders": PLACEHOLDERS,
               "reframes": REFRAMES, "ass": str(ASS_OUT), "srt": str(SRT_OUT), "b3_configs": {s["id"]: s["b3"] for s in segs}}, open(new(BUILD / "rough_meta.json"), "x"), indent=1, default=str)
    print("BUILD DONE")
