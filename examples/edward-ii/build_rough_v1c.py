#!/workspace/mpvenv/bin/python
"""POSTERITY standalone -- Edward II v3b (Kent as protagonist) -- ROUGH v1c (from v1b: S03 Corfe removed from the opening -> S01/S02 split on 'his half-brother';
fire / candle light-spill + atmosphere animation per plate via fx_v1c.py (locked house-candle-lightspill-v1 maths); audio stream-copied from the v1b master).
Re-runnable: intermediate scratch lives in edit/_build_v3b_v1/ (re-used if present); final outputs are never overwritten
(the script refuses if the master/preview already exist, unless --tag gives a new name).
House pieces copied from germanicus/edit/build_rough_germanicus_v5b.py (prepare_cover, StablePush cam/cam_frame,
Chronicle Reveal title, auto_chunks/wrap_idx captions, ASS style). Run with /workspace/mpvenv/bin/python.
"""
import argparse, hashlib, json, math, subprocess, sys, os
from pathlib import Path
from multiprocessing import Pool
import numpy as np, cv2
sys.path.insert(0, str(Path(__file__).resolve().parent)); import fx_v1c as FX
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("--tag", default="v1c")
ap.add_argument("--tail", type=float, default=0.5, help="seconds held after speech energy ends (v1: 4.0)")
ap.add_argument("--title", default="THE LETTER TO\nA DEAD KING", help="Chronicle Reveal text; use \\n for the line break")
ap.add_argument("--title-top-pct", type=float, default=16.0, help="title band centre, % of frame height (v1: 32.5; v1b: 16-20 per Vellum)")
ap.add_argument("--test-frames", default="", help="comma list of global frame numbers -> PNG stills in /dev/shm/e2qc (no render)")
ap.add_argument("--jobs", type=int, default=6)
ap.add_argument("--audio-only", action="store_true")
ARGS = ap.parse_args()

E = Path("/workspace/posterity/standalones/edward-ii"); PL = E / "plates-v3b"; EDIT = E / "edit"; VOD = E / "vo"
REND = Path("/workspace/posterity/renders")
BUILD = EDIT / f"_build_v3b_{ARGS.tag}"; CLIPS = BUILD / "clips"; AUD = BUILD / "audio"
for d in (BUILD, CLIPS, AUD): d.mkdir(parents=True, exist_ok=True)
MASTER = REND / f"posterity-edward-ii-v3b-ROUGH-{ARGS.tag}.mp4"; PREVIEW = REND / f"posterity-edward-ii-v3b-ROUGH-{ARGS.tag}-preview.mp4"
W, H, FPS, UP = 1080, 1920, 30, 2
VO_SRC = VOD / "final-vo-oliver-edward-ii-v3b.wav"; VO_MD5 = "30e67dbdce08242d7e8a03e89cbff23d"
WORDS_JSON = VOD / "final-vo-oliver-edward-ii-v3b_words.json"
SCRIPT = E / "raw" / "script-vo-v3-DRAFT.txt"; SCRIPT_MD5 = "b30ce609e7ae1b62216e124ace1bdc94"
MUSIC = E / "score" / "macleod_gregorian_chant.mp3"; MUSIC_MD5 = "e25af185c7890ba1fdef695ae9b030b8"
SFX = Path("/workspace/posterity/sfx/battle/marching/_norm/marching_knight-footsteps_fs770083.wav")   # CC0 1.0 (Vrymaa, freesound 770083)
FONT_DIR = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/"; F_SEMI = FONT_DIR + "SourceSerifPro-Semibold.ttf"
ENC_INTER = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "8", "-preset", "fast"]
ENC_FINAL = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", "-profile:v", "high"]

def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
assert md5f(VO_SRC) == VO_MD5, "VO changed"; assert md5f(SCRIPT) == SCRIPT_MD5, "script changed"; assert md5f(MUSIC) == MUSIC_MD5
words = json.load(open(WORDS_JSON))["words"]
DISP = SCRIPT.read_text().split(); assert len(DISP) == len(words) == 222
def norm(s): return " ".join(x.strip(".,;:?!\"'").lower() for x in s.split())
assert norm(" ".join(DISP)) == norm(" ".join(w["word"] for w in words))
def join_disp(idx): return " ".join(DISP[i] for i in idx)
def widx(phrase, after=0):
    p = phrase.split()
    for i in range(after, len(words) - len(p) + 1):
        if [x.strip(".,").lower() for x in DISP[i:i + len(p)]] == [x.strip(".,").lower() for x in p]: return i
    raise KeyError(phrase)
def fob(t): return int(math.floor(t * FPS + 1e-6))
SPEECH_END = 88.045   # silencedetect -45 dB: last speech energy ends 88.045 s (alignment pads 'rest.' to the file end 88.793)
TAIL = ARGS.tail

# ------------------------------------------------------------------ slots: (id, plate, VO cue phrase (first word), crop box in plate px or None, anchor, cut override s)
P = lambda n: PL / n
SLOTS = [
 ("S01", "b01_gloucester_funeral_wide_kent_OWNER.png", "England buried", None, (0.5, 0.45), 0.0),
 ("S02", "b02_kent_bound_dawn_close_OWNER.png", "his half-brother", None, (0.5, 0.20), None),   # v1c: S03 (Corfe) removed; anchor high so the hairline stays put under the title
 ("S04", "b04_the_brothers_OWNER.png", "The king was", None, (0.80, 0.30), 7.05),   # opening ends 0.18 s after 'him.'; push drifts toward Kent (right)
 ("S05", "b05_landing_1326_kent_OWNER.png", "had helped Edward's", None, (0.35, 0.45), None),
 ("S06", "p04_berkeley_castle_dusk_OWNER.png", "Months later", None, (0.62, 0.40), None),
 ("S07", "b07_kent_at_funeral_close_OWNER.png", "Kent attended", None, (0.45, 0.35), None),
 ("S08", "b08_kent_hears_friars_OWNER.png", "his brother was alive", None, (0.40, 0.35), None),
 ("S09", "b09_kent_supporters_OWNER.png", "Around seventy", None, (0.5, 0.40), None),
 ("S10", "b10_corfe_kent_hands_letter_OWNER.png", "Kent handed", None, (0.45, 0.55), None),
 ("S11", "p07_mortimer_reads_letter_OWNER.png", "him. That man", None, (0.55, 0.55), 35.20),   # cut before 'him.' so S11 holds 3.0 s
 ("S12", "b12_winchester_after_OWNER.png", "Kent was beheaded", None, (0.5, 0.50), 38.20),
 ("S13", "b13_nottingham_seizure_OWNER.png", "and a few loyal", None, (0.5, 0.40), None),
 ("S14", "b14_mortimer_charged_OWNER.png", "Mortimer was hanged", None, (0.5, 0.40), None),
 ("S15", "b15_papal_notary_writes_OWNER.png", "Years later", None, (0.40, 0.50), None),
 ("S16", "p10_escape_servant_clothes_twilight_OWNER.png", "Edward had escaped", None, (0.55, 0.50), None),
 ("S17", "p14_corfe_dusk_single_light_OWNER.png", "He said Edward", None, (0.62, 0.22), None),
 ("S18", "b18_edward_hidden_at_corfe_OWNER.png", "And according to", None, (0.55, 0.30), None),
 ("S19", "b12_winchester_after_OWNER.png", "had been executed", (190, 520, 650, 1338), (0.45, 0.50), None),   # TIGHT block+mantle, executioner (x>=660) excluded
 ("S20", "p04_berkeley_castle_dusk_OWNER.png", "Most historians", (380, 250, 900, 1174), (0.55, 0.30), None),   # TIGHT keep + lit window
 ("S21", "b19_kent_empty_seat_OWNER.png", "if that letter", None, (0.5, 0.45), None),
 ("S22", "b20_kent_seals_letter_OWNER.png", "the brother who helped", None, (0.55, 0.45), None),
 ("OUTRO", "outro_edward_ii_gloucester_dusk_OWNER.png", "History remembers", None, (0.5, 0.40), None),
]
V1B_MASTER = REND / "posterity-edward-ii-v3b-ROUGH-v1b.mp4"; V1B_MD5 = "832e1160a3c30c9c556ad42d347a6c43"   # audio source (stream copy)
segs = []; after = 0
for sid, f, ph, crop, anc, ov in SLOTS:
    wi = widx(ph, after if sid != "S19" else widx("only after learning")); after = wi
    if ov is not None: f0 = fob(ov)
    else:
        gap = words[wi]["start"] - words[wi - 1]["end"] if wi else 1.0
        f0 = fob(words[wi]["start"] - 0.08) if gap >= 0.25 else fob(words[wi]["start"])
    segs.append(dict(id=sid, plate=str(P(f)), first_wi=wi, first_word=DISP[wi], crop=crop, anchor=anc, f0=f0, z_start=1.00, z_end=1.06))
TOTAL_F = fob(SPEECH_END + TAIL)
for k, s in enumerate(segs):
    s["f1"] = segs[k + 1]["f0"] if k + 1 < len(segs) else TOTAL_F
    s["frames"] = s["f1"] - s["f0"]; s["start"] = s["f0"] / FPS; s["end"] = s["f1"] / FPS; s["duration"] = s["frames"] / FPS
    ws = [i for i, w in enumerate(words) if s["start"] - 1e-6 <= w["start"] < s["end"]]
    s["vo"] = join_disp(ws)
OPENING = {"S01", "S02"}
SHORT = [(s["id"], round(s["duration"], 3)) for s in segs if s["duration"] < 3.0 and s["id"] not in OPENING]
OPEN_BAD = [(s["id"], round(s["duration"], 3)) for s in segs if s["id"] in OPENING and not (3.0 <= s["duration"] <= 4.0)]
assert not SHORT, f"shots under 3 s outside the opening: {SHORT}"
assert not OPEN_BAD, OPEN_BAD
SEG = {s["id"]: s for s in segs}; OUTRO_T = SEG["OUTRO"]["start"]
for s in segs: print(f"  {s['id']:5} {Path(s['plate']).name:46} f{s['f0']:5d} {s['start']:7.3f}-{s['end']:7.3f} {s['duration']:6.3f}s  '{s['vo']}'")

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

# ------------------------------------------------------------------ Chronicle Reveal (Germanicus v5b lines 294-510, verbatim except text/position/timing)
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
_S04 = SEG["S04"]["f0"]   # the title carries S01-S02 and is fully gone 2 frames before the S04 cut
CR = dict(title=ARGS.title.replace("\\n", "\n"), fontSize=88, color=(243, 237, 224), topPercent=ARGS.title_top_pct, offsetX=-16,
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
def overlay_for(gf):
    if gf >= CR["strokeClearEnd"] and gf >= CR["exitEnd"]: return None
    ls = [l for l in (strike_layer(gf), title_layer(gf)) if l is not None]
    if not ls: return None
    out = ls[0].copy()
    for x in ls[1:]: out.alpha_composite(x)
    return out

# ------------------------------------------------------------------ v1c: per-plate fire / spill / atmosphere (plate space) -> crop -> house cover -> StablePush
def make_fx(seg):
    if seg["id"] == "OUTRO": return None   # baked-text outro stays as v1b
    fx = FX.PlateFX(seg["plate"], seed=int(seg["id"][1:]) if seg["id"][1:].isdigit() else 0)
    return fx if fx.active() else None
def fx_base(fx, seg, gf, u):
    im = Image.fromarray(fx.render(gf / FPS, u))
    if seg["crop"]: im = im.crop(seg["crop"])
    return prepare_cover(im)

def render_segment(sid):
    seg = SEG[sid]; dst = CLIPS / f"{sid}.mp4"
    if dst.exists(): return sid, -1
    tmp = CLIPS / f"{sid}.part.mp4"
    if tmp.exists(): tmp.unlink()   # own scratch from an interrupted run
    nfr = seg["frames"]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-frames:v", str(nfr), "-an", *ENC_INTER, "-r", str(FPS), str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fx = make_fx(seg); base = None if fx else base_2x(seg)
    for fi in range(nfr):
        u = fi / max(nfr - 1, 1); t = fi / FPS; gf = seg["f0"] + fi
        b = base if fx is None else fx_base(fx, seg, gf, u)
        frame = cam_frame(b, seg, u, t); ov = overlay_for(gf)
        if ov is not None: fr = frame.convert("RGBA"); fr.alpha_composite(ov); frame = fr.convert("RGB")
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait(): raise SystemExit(f"encode fail {sid}")
    tmp.rename(dst); return sid, nfr

# ------------------------------------------------------------------ captions (house: auto_chunks <=7 words, wrap 24, DejaVu Sans 54); the tagline (L17) is NOT captioned: it is baked into the outro plate
def auto_chunks(ws, max_words=7):
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
def wrap_idx(tok_idx, maxc=24):
    if len(join_disp(tok_idx)) <= maxc: return [tok_idx]
    best = None
    for k in range(1, len(tok_idx)):
        sc = max(len(join_disp(tok_idx[:k])), len(join_disp(tok_idx[k:])))
        if best is None or sc < best[0]: best = (sc, k)
    return [tok_idx[:best[1]], tok_idx[best[1]:]]
def ass_time(t):
    cs = int(round(max(0.0, t) * 100)); s, cs = divmod(cs, 100); m, s = divmod(s, 60); h, m = divmod(m, 60); return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
L17 = [i for i, w in enumerate(words) if w["line"] == 17]; CAP_N = L17[0]
spans = []; wi = 0
for ch in auto_chunks(DISP[:CAP_N]):
    toks = ch.split(); assert DISP[wi:wi + len(toks)] == toks; spans.append((wi, wi + len(toks) - 1)); wi += len(toks)
assert wi == CAP_N
TITLE_ON_S, TITLE_OFF_S = CR["strokeEnterStart"] / FPS, CR["exitEnd"] / FPS
ass = ["[Script Info]", f"Title: Posterity Edward II v3b ROUGH {ARGS.tag}", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Default,DejaVu Sans,54,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,400,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
cap_events = []; ttl = " " + norm(CR["title"].replace("\n", " ")) + " "
for k, (a, b) in enumerate(spans):
    st = 0.0 if k == 0 else words[a]["start"]; en = words[b]["end"] + 0.30
    if k + 1 < len(spans): en = min(en, words[spans[k + 1][0]]["start"] - 0.04)
    en = min(en, OUTRO_T); cw = norm(join_disp(range(a, b + 1))).split()
    rep = any(" " + " ".join(cw[i:i + 3]) + " " in ttl for i in range(max(len(cw) - 2, 0)))
    hidden = st >= TITLE_ON_S - 0.3 and en <= TITLE_OFF_S and rep
    txt = r"\N".join(join_disp(ln) for ln in wrap_idx(list(range(a, b + 1))))
    ass.append(f"{'Comment' if hidden else 'Dialogue'}: 0,{ass_time(st)},{ass_time(en)},Default,,0,0,0,,{txt}")
    cap_events.append(dict(start=round(st, 3), end=round(en, 3), text=join_disp(range(a, b + 1)), hidden=hidden))
assert norm(" ".join(e["text"] for e in cap_events)) == norm(" ".join(DISP[:CAP_N]))
ASS = BUILD / f"edward_ii_v3b_rough_{ARGS.tag}.ass"; ASS.write_text("\n".join(ass) + "\n")
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
S12_T, S13_T, S14_T = SEG["S12"]["start"], SEG["S13"]["start"], SEG["S14"]["start"]
L16_T = words[[i for i, w in enumerate(words) if w["line"] == 16][0]]["start"]
FADE1 = DUR - 0.05; FADE0 = min(SPEECH_END + 1.4, FADE1 - 1.35)   # short tail: 1.35 s fade to silence, never a hard cut
def env_db(t):   # bed level automation (dB, before ducking): dread rises through S12 (Kent's execution) and S13 (Nottingham), eases, ends quiet
    pts = [(0, 0.0), (S12_T - 0.5, 0.0), (S13_T, 4.5), (S14_T - 0.3, 6.5), (S14_T + 2.5, 1.0), (L16_T, 0.0), (OUTRO_T, -1.5)] + ([(SPEECH_END, -1.5), (FADE0, -1.0)] if FADE0 > SPEECH_END + 0.05 else [(FADE0, -1.5)]) + [(FADE1, -40.0)]
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
def low_gain(t):   # parallel <160 Hz layer (weight under the dread)
    return np.interp(t, [0, S12_T - 0.5, S13_T, S14_T - 0.3, S14_T + 2.0, DUR], [0, 0, 0.7, 1.0, 0, 0])
def build_audio():
    mix = AUD / "mix.wav"
    if mix.exists(): return mix
    vo = AUD / "vo_proc.wav"; ff("-i", str(VO_SRC), "-af", "highpass=f=80,acompressor=threshold=0.125:ratio=3:attack=8:release=140:knee=3:makeup=1,aresample=48000", "-ac", "1", "-c:a", "pcm_f32le", str(vo))
    flat = AUD / "bed_flat.wav"; low = AUD / "bed_low.wav"
    ff("-i", str(MUSIC), "-t", f"{DUR:.3f}", "-af", "aresample=48000,highpass=f=70,highpass=f=70,equalizer=f=320:t=q:w=1.2:g=-2.5,equalizer=f=1800:t=q:w=1.0:g=-2.0,equalizer=f=3000:t=q:w=1.2:g=-3.0,afade=t=in:d=1.2", "-ac", "2", "-c:a", "pcm_f32le", str(flat))
    ff("-i", str(MUSIC), "-t", f"{DUR:.3f}", "-af", "aresample=48000,highpass=f=40,lowpass=f=160,lowpass=f=160", "-ac", "2", "-c:a", "pcm_f32le", str(low))
    t = np.arange(N) / SR; fl = read_wav(flat, 2); lo = read_wav(low, 2)
    fl = np.pad(fl, ((0, max(0, N - len(fl))), (0, 0)))[:N]; lo = np.pad(lo, ((0, max(0, N - len(lo))), (0, 0)))[:N]
    bed = (fl + lo * low_gain(t)[:, None]) * (10 ** (env_db(t) / 20))[:, None]
    # subtle CC0 footsteps (knights, castle hall) under Nottingham only
    sf = read_wav(SFX, 2); off = int(12.0 * SR); seg_n = int((S14_T - S13_T) * SR); s = sf[off:off + seg_n].copy()
    fade = int(0.5 * SR); s[:fade] *= np.linspace(0, 1, fade)[:, None]; s[-fade:] *= np.linspace(1, 0, fade)[:, None]
    sfx = np.zeros_like(bed); i0 = int(S13_T * SR); sfx[i0:i0 + len(s)] = s[:len(sfx) - i0]
    write_wav(AUD / "bed_auto.wav", bed); write_wav(AUD / "sfx.wav", sfx)
    pre = AUD / "premix.wav"
    def mk(bg, sg):
        ff("-i", str(vo), "-i", str(AUD / "bed_auto.wav"), "-i", str(AUD / "sfx.wav"), "-filter_complex",
           "[0:a]pan=stereo|c0=c0|c1=c0,asplit=2[v][k];"
           f"[1:a]volume={bg}dB[b];[b][k]sidechaincompress=threshold=0.02:ratio=4:attack=25:release=450:knee=4:makeup=1[bd];"
           f"[2:a]volume={sg}dB[s];[v][bd][s]amix=inputs=3:normalize=0:duration=first,apad=whole_len={N}", "-t", f"{DUR:.4f}", "-c:a", "pcm_f32le", str(pre))
    BG, SG = -21.0, -38.0
    mk(BG, SG); I0, _ = ebur(pre); Iv, _ = ebur(vo)
    gain = -14.0 - I0
    for it in range(8):
        ff("-i", str(pre), "-af", f"volume={gain:.3f}dB,aresample=192000,alimiter=limit=0.8:attack=3:release=60:level=false:asc=1,aresample=48000", "-c:a", "pcm_s24le", str(mix))
        I1, TP1 = ebur(mix)
        if abs(I1 + 14.0) <= 0.1 and TP1 <= -1.5: break
        gain += (-14.0 - I1)
    json.dump(dict(premix_I=I0, vo_I=Iv, gain=gain, mix_I=I1, mix_TP=TP1, bed_gain_db=BG, sfx_gain_db=SG), open(AUD / "mix_stats.json", "w"), indent=1)
    return mix

def stats_report(path):
    I, TP = ebur(path); return I, TP

if __name__ == "__main__":
    json.dump(dict(segs=[{k: v for k, v in s.items()} for s in segs], cr={k: v for k, v in CR.items()}, captions=cap_events), open(BUILD / "timeline.json", "w"), indent=1, default=str)
    if ARGS.test_frames:
        out = Path("/dev/shm/e2qc"); out.mkdir(exist_ok=True)
        for gf in [int(x) for x in ARGS.test_frames.split(",")]:
            seg = [s for s in segs if s["f0"] <= gf < s["f1"]][0]; fi = gf - seg["f0"]
            fx = make_fx(seg); u = fi / max(seg["frames"] - 1, 1)
            fr = cam_frame(base_2x(seg) if fx is None else fx_base(fx, seg, gf, u), seg, u, fi / FPS); ov = overlay_for(gf)
            if ov is not None: fr = fr.convert("RGBA"); fr.alpha_composite(ov); fr = fr.convert("RGB")
            fr.save(out / f"test_{gf:05d}_{seg['id']}.png"); print("wrote", out / f"test_{gf:05d}_{seg['id']}.png")
        sys.exit(0)
    assert md5f(V1B_MASTER) == V1B_MD5, "v1b master changed"   # v1c audio = v1b master audio, stream-copied (no re-mix)
    if ARGS.audio_only: sys.exit(0)
    for p in (MASTER, PREVIEW): assert not p.exists(), f"{p} exists: refusing to overwrite (use a new --tag)"
    with Pool(ARGS.jobs) as pool:
        for sid, n in pool.imap_unordered(render_segment, [s["id"] for s in sorted(segs, key=lambda s: -s["frames"])]): print("clip", sid, n, flush=True)
    cl = BUILD / "concat.txt"; cl.write_text("".join(f"file '{CLIPS / (s['id'] + '.mp4')}'\n" for s in segs))
    e = str(ASS).replace(":", "\\:")
    subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(cl), "-i", str(V1B_MASTER), "-map", "0:v", "-map", "1:a",
                           "-vf", f"ass='{e}'", *ENC_FINAL, "-r", str(FPS), "-c:a", "copy", "-t", f"{DUR:.4f}", "-movflags", "+faststart", str(MASTER)])
    subprocess.check_call(["ffmpeg", "-n", "-v", "error", "-i", str(MASTER), "-vf", "scale=720:1280:flags=lanczos", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-b:v", "2600k", "-maxrate", "3500k", "-bufsize", "7000k",
                           "-c:a", "copy", "-movflags", "+faststart", str(PREVIEW)])
    for p in (MASTER, PREVIEW):
        I, TP = ebur(p); print(p, md5f(p), p.stat().st_size, "I", I, "TP", TP)
