"""
Owner 11:52: the 0.35 s 'Zhu Di' caption is merged into the previous S10 cue, ending exactly at the K09->K10 cut.
Jianwen v2 timing grid -> edit/timing_grid_v2.json + edit/TIMING-GRID-v2.md (Edward II v3b cut rule; refuses to overwrite).
v2 = owner-locked narration (raw/script-vo-tts.txt v2, 204 words) on the MEASURED Oliver take t1 (vo/final-vo-oliver-jianwen-v2.wav, speech end 89.28 s).
Plate map = plate-prompts-v2b.md (owner notes 11:28: K10 block-erasure, K11 cool / K13 warm, Xuanfu lit-window outro, title 'DID THE EMPEROR WALK OUT OF THE FIRE?').
20 picture slots S01-S20 (K01-K19 + the K01 REPRISE at S09; S02 is split WIDE/TIGHT on one plate for the opening) + OUTRO. v1 / v1b files untouched.
Owner decision 11:46: K09 -> K10 cut moved onto 'took' (41.167 s) so 'Zhu Di' plays over the empty room: S10 3.13 s, S11 4.27 s; S09 reprise stays 2.33 s (flagged quick callback).
Previous grid (S11 on 'Zhu Di') archived in edit/superseded/2026-10-30_grid-v2_pre-took/."""
import json, hashlib, re, sys, math
from pathlib import Path
J = Path("/workspace/posterity/standalones/jianwen"); E = J / "edit"
WORDS = J / "vo/final-vo-oliver-jianwen-v2_words.json"; VO = J / "vo/final-vo-oliver-jianwen-v2.wav"; SCRIPT = J / "raw/script-vo-tts.txt"; PROMPTS = J / "plate-prompts-v2b.md"
VO_MD5 = "a9eb59d4c4cc4d69d5c5ef075d988140"; WORDS_MD5 = "5253aaec40374caae0ceb765085fb737"; SCRIPT_MD5 = "851ddfb4cafb463d292861f5215a6cff"
FPS = 30; SPEECH_END = 89.28; TAIL = 0.72          # 89.28 + 0.72 = 90.00 s -> outro 85.133-90.000 = 4.87 s (brief: 4.5-5 s, end 89.8-90.2)
TITLE_TEXT = "DID THE EMPEROR\nWALK OUT OF THE FIRE?"; TITLE_FONT = 78   # owner 11:28; line 2 = 951 px at 78 (limit 994 px = 92 % W; 80 -> 975, 84 -> 1024)
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(VO) == VO_MD5 and md5(WORDS) == WORDS_MD5 and md5(SCRIPT) == SCRIPT_MD5, "VO / words / script md5 mismatch"
W = json.load(open(WORDS))["words"]; assert len(W) == 204
DISP = SCRIPT.read_text().split(); assert len(DISP) == 204
norm = lambda s: re.sub(r"[^a-z']", "", s.lower().replace("\u2019", "'"))
assert [norm(x) for x in DISP] == [norm(w["word"]) for w in W]
toks = [norm(w["word"]) for w in W]
def widx(phrase, after=0):
    p = [norm(x) for x in phrase.split()]
    for i in range(after, len(toks) - len(p) + 1):
        if toks[i:i + len(p)] == p: return i
    raise SystemExit(f"phrase not found: {phrase}")
fob = lambda t: int(math.floor(t * FPS + 1e-6))
TAG_LINE = 14; TAG_I = next(i for i, w in enumerate(W) if w["line"] == TAG_LINE); assert abs(W[TAG_I]["start"] - 85.23) < 0.01
K01 = "k01_night_burial_as_emperor.png"; K02 = "k02_uncle_still_searching.png"
# slot, plate, cue phrase, framing, push anchor (x,y frame fraction, placeholder from the v2b composition notes), z_end, motion plan, note
SL = [
 ("S01",  K01, "They buried", "wide", (0.50, 0.55), 1.04, "WIDE: title lockup manifests; push 1.00->1.04 to the yellow-draped coffin; tall pole torches = glow pulse + spill on robes/coffin/faces (torch shapes static); faint smoke drifting off the torches; a few embers; cool night haze", "opening cut 1/3"),
 ("S02A", K02, "His own uncle", "wide", (0.50, 0.48), 1.04, "WIDE: title holding; push 1.00->1.04 toward his face; single tall candle = flame-shape sway + flicker + warm spill across face/robe/map; warm haze + lit motes", "opening cut 2/3: cut in the 0.81 s pause, 0.08 s after 'emperor.' ends (2.252 s)"),
 ("S02B", K02, "kept searching", "tight", (0.50, 0.47), 1.04, "TIGHT: crop of the SAME K02 plate on his eyes (>= 70 % frame, else fallback); push 1.00->1.04; same fx seed + global clock as S02A (candle continues through the cut); title exits, clean 2 f before K03", "opening cut 3/3: cut on 'kept' (0.06 s gap -> word-start frame)"),
 ("S03",  "k03_founder_and_grandson.png", "The missing emperor", "full", (0.55, 0.45), 1.06, "slow drift founder->grandson; rows of candles on bronze stands = shape motion + grouped spill; warm haze, lit motes", ""),
 ("S04",  "k04_uncle_with_armies.png", "But Jianwen inherited", "full", (0.62, 0.45), 1.06, "slow push up to Zhu Di; sea of soldiers' torches = glow pulse + spill on armour (torch shapes static); smoke haze + a few embers", ""),
 ("S05",  "k05_zhu_di_rebels_edict_cast_down.png", "When he tried", "full", (0.50, 0.50), 1.06, "slow push from the fallen edict up to Zhu Di; brazier = BIG-FIRE glow pulse + spill (flame static) + embers; commanders' torches glow + spill", ""),
 ("S06",  "k06_army_before_nanjing_walls.png", "Three years later", "full", (0.50, 0.42), 1.06, "slow push toward the walls/gate; river of torches = glow pulse + spill on ranks/wall (static shapes); smoke haze; NO war SFX (not a battle)", ""),
 ("S07",  "k07_commander_opens_the_gate.png", "A commander who", "full", (0.50, 0.45), 1.06, "slow push past the general into the torchlit arch; torches pouring through the gate = glow pulse + spill on the gate leaves/paving; smoke haze", ""),
 ("S08",  "k08_palace_fire_body_carried_out.png", "Then the palace", "full", (0.50, 0.56), 1.06, "slow push to the litter; burning roof = BIG FIRE (flame shapes static, glow + spill pulse) + dense embers + smoke above the roofline; soldiers' torches glow; wet-paving reflections STATIC (no water motion)", ""),
 ("S09",  K01, "He had it", "reprise", (0.50, 0.55), 1.06, "K01 REPRISE, TIGHT crop on the coffin and Zhu Di at the grave head (different framing from the S01 wide); push 1.00->1.06; same K01 fx (pole torches glow/spill, faint smoke, embers)", "callback to the hook; flagged quick callback 2.33 s (owner 11:46: keep)"),
 ("S10",  "k09_empty_childs_room.png", "Jianwen's small son", "full", (0.50, 0.60), 1.06, "very slow push to the small shoes; single candle = shape motion + local spill on floor/bedding; dust motes", "runs through 'Zhu Di' (owner 11:46) so it holds 3.13 s"),
 ("S11",  "k10_yongle_enthroned_calendar.png", "took the throne", "full", (0.50, 0.55), 1.06, "v2b K10 = craftsmen chiselling the old calendar blocks: slow push to the chisel/block; bronze brazier = glow pulse + warm spill on craftsmen/blocks (flame/coal shape static) + a few embers; distant hall candles flicker; wood chips static", "owner 11:28: new K10; owner 11:46: cut on 'took' (0.07 s gap -> word-start frame), 'Zhu Di' stays on K09"),
 ("S12",  "k11_LEGEND_monk_leaves_burning_city.png", "But rumours said", "full", (0.45, 0.56), 1.06, "COOL moon-blue: slow push following the figure; moonlit dreamlike mist drifting at the edges, cool ambience; small paper lantern = flicker + gentle sway + small local warm spill ONLY around the lantern; distant city = big-fire glow pulse on the horizon (static) + slow smoke; NO broad warm spill pumping; LEGEND label upper-left", "LEGEND label on this plate only"),
 ("S13",  "k12_covert_orders_to_hu_ying.png", "Yongle sent an", "full", (0.50, 0.50), 1.06, "slow push to the sealed orders between them; candle lamp-stand = shape motion + spill on both faces; warm haze", ""),
 ("S14",  "k13_hu_ying_searching_daoist_temple.png", "Officially he was", "full", (0.40, 0.47), 1.06, "WARM amber: slow push to Hu Ying's searching eyes; eave paper lanterns = amber flicker + gentle sway + warm spill on faces/gate posts; incense smoke curling from the burner", "K13 warm vs K11 cool (owner 11:28)"),
 ("S15",  "k14_mourning_leave_refused.png", "When Hu Ying's", "full", (0.50, 0.50), 1.06, "slow push to his bowed face; single candle on the low table = shape motion + spill on face/letter; warm haze", ""),
 ("S16",  "k15_xuanfu_night_arrival.png", "More than twenty", "full", (0.35, 0.48), 1.06, "slow push to Hu Ying at the gate; guards' torches = glow pulse + spill (static shapes); dust haze, a few embers", "Xuanfu 1/4"),
 ("S17",  "k16_emperor_rises_from_bed.png", "Yongle was already", "full", (0.50, 0.46), 1.06, "push in as he sits up; eunuch's oil lamp = flame-shape motion + spill across bed/face; warm haze", "Xuanfu 2/4"),
 ("S18",  "k17_one_candle_long_talk.png", "summoned the official", "full", (0.50, 0.48), 1.06, "very slow push between the two faces; single low candle = shape motion + strong local spill on both faces", "Xuanfu 3/4"),
 ("S19",  "k18_suspicions_end_alone.png", "The later History", "full", (0.50, 0.46), 1.06, "very slow push to Yongle's face; guttering candle stub = shape motion + flicker + spill; thin smoke curl off the wick", "Xuanfu 4/4"),
 ("S20",  "k19_the_unwritten_record.png", "It never says", "full", (0.50, 0.55), 1.06, "very slow push to the blank page; desk candle = shape motion + spill across page/desk; dust motes", "cut moved 0.21 s into the 0.67 s pause so S20 = 3.00 s"),
 ("OUTRO", "jianwen_outro_xuanfu_lit_window.png", "History remembers", "outro", (0.50, 0.50), 1.02, "v2b Xuanfu outro, used AS-IS (no overlay text): the one lit window = warm flicker + glow; faint wall-walk torches = glow pulse (shape static); thin moonlit mist drifting; all kept OFF the baked lettering (30-70 % band); push 1.00->1.02 only if the lettering stays in frame; music fades", "baked title + tagline"),
]
OPENING = ("S01", "S02A", "S02B")
OVR = {"S02A": lambda k: fob(W[k - 1]["end"] + 0.08)}   # opening beat: sentence end of L01a
starts = []
for i, (s, p, ph, *_r) in enumerate(SL):
    k = widx(ph, starts[-1][0] + 1 if i else 0)
    if i == 0: f0 = 0
    elif s in OVR: f0 = OVR[s](k)
    else:
        gap = W[k]["start"] - W[k - 1]["end"]
        f0 = fob(W[k]["start"] - 0.08) if gap >= 0.25 else fob(W[k]["start"])
    starts.append([k, f0])
TOTAL_F = fob(SPEECH_END + TAIL)
OUT_I = [i for i, x in enumerate(SL) if x[0] == "OUTRO"][0]; S20_I = OUT_I - 1
if starts[OUT_I][1] - starts[S20_I][1] < 3 * FPS:            # S20 'It never says' (0.67 s gap before it): cut earlier inside the pause
    rule_f = starts[S20_I][1]; starts[S20_I][1] = starts[OUT_I][1] - 3 * FPS
    assert W[starts[S20_I][0] - 1]["end"] + 0.25 < starts[S20_I][1] / FPS < rule_f / FPS
assert starts[OUT_I][0] == TAG_I
slots = []
for i, (s, p, ph, fr, anc, ze, mo, nt) in enumerate(SL):
    k, f0 = starts[i]; f1 = starts[i + 1][1] if i + 1 < len(SL) else TOTAL_F
    k1 = starts[i + 1][0] if i + 1 < len(SL) else len(W)
    vo = " ".join(DISP[k:k1]); crop = None
    if s == "S02B": crop = dict(frac=0.75, center=[0.50, 0.47], min_frac=0.70, note="placeholder: on his eyes (face at 42-55 % height); set on the real K02 plate")
    if s == "S09": crop = dict(frac=0.75, center=[0.50, 0.52], min_frac=0.70, note="placeholder: coffin (50-60 % height, centre) + Zhu Di at the grave head; set on the real K01 plate")
    slots.append(dict(slot=s, plate=p, framing=fr, crop=crop, anchor=list(anc), z_start=1.00, z_end=ze, f0=f0, f1=f1, start=round(f0 / FPS, 3), end=round(f1 / FPS, 3), dur=round((f1 - f0) / FPS, 3),
                      first_word=DISP[k], first_word_t=W[k]["start"], vo=vo, motion=mo, note=nt, under3=(f1 - f0) < 3 * FPS and s not in OPENING))
picture = [x for x in slots if x["slot"] != "OUTRO"]
assert len({x["slot"][:3] for x in picture}) == 20 and len({x["plate"] for x in picture}) == 19
OP = [x for x in slots if x["slot"] in OPENING]
assert all(1.5 <= x["dur"] <= 2.5 for x in OP) and OP[-1]["f1"] / FPS > 5.0 and OP[1]["f0"] < 5 * FPS and OP[2]["f0"] < 5 * FPS, [(x["slot"], x["dur"]) for x in OP]
OUT = slots[-1]; assert 4.5 <= OUT["dur"] <= 5.0 and 89.8 <= OUT["end"] <= 90.2, OUT
K03_F = slots[3]["f0"]
TITLE = dict(text=TITLE_TEXT, slots=list(OPENING), fontSize=TITLE_FONT, topPercent=32.5, start_f=0, anchor_f=K03_F, clean_by_f=K03_F - 2,
             strokeEnter=[8, 26], manifest=[14, 42], hold=[42, K03_F - 32], exit=[K03_F - 32, K03_F - 12], strokeClear=[K03_F - 23, K03_F - 2],
             carries_cuts_f=[OP[1]["f0"], OP[2]["f0"]],
             note=f"Chronicle Reveal v3.2b enter/exit unchanged; anchor = the K03 cut (Edward v3 rule: title carries across all opening cuts, clean 2 f before the next plate), so the hold runs f42-{K03_F - 32} (lock 4.0 s -> {K03_F / FPS - 0.07:.2f} s). Both opening cuts land in the hold. fontSize {TITLE_FONT}: line 2 'WALK OUT OF THE FIRE?' 951 px (<= 994 px). K01 and K02 both keep 25-40 % calm for the band.")
for x in slots: assert not (TITLE["exit"][0] <= x["f0"] < TITLE["strokeClear"][1] and x["f0"] != K03_F), f"cut inside the title exit: {x['slot']}"
S12 = next(x for x in slots if x["slot"] == "S12")
LEGEND = dict(slot="S12", plate=S12["plate"], text="LEGEND", font="SourceSerifPro-Semibold.ttf", fontSize=36, trackingEm=0.30, color=[243, 237, 224], opacity=0.80,
              xPct=8.0, yPct=11.0, anchor="top-left (cap top)", rule=dict(px=2, opacity=0.45, gap_px=10, width="text width"), shadow=dict(blur=3, alpha=110),
              in_f=[S12["f0"] + 10, S12["f0"] + 25], out_f=[S12["f1"] - 22, S12["f1"] - 9], rise_px=6, ease="smoothstep",
              note="small, quiet, upper-left (v2b keeps that corner calm + dark on K11); fades in 0.33-0.83 s after the cut with a 6 px rise, out 0.73-0.30 s before the next cut; no slam. Adjustable per plate in the build (--legend-pos x,y / --legend-size).")
CUTW = {k for k, _ in starts}
# reading breaks (caption chunks start at these words; <= 7 words each)
BRK = {widx(p_) for p_ in ("fought for Jianwen helped", "helped open a city", "says Yongle's suspicions", "what Hu Ying told", "named Hu Ying across")}
lines = {}
for i, w in enumerate(W): lines.setdefault(w["line"], []).append(i)
def chunks(idx):
    groups, cur = [], []
    for i in idx:
        if cur and (i in CUTW or i in BRK): groups.append(cur); cur = []
        cur.append(i)
        if re.search(r"[.,?!;:]$", DISP[i]): groups.append(cur); cur = []
    if cur: groups.append(cur)
    gi = 0
    while gi < len(groups) - 1:
        a, b = groups[gi], groups[gi + 1]
        if len(a) <= 2 and len(a) + len(b) <= 7 and b[0] not in CUTW and b[0] not in BRK: groups[gi] = a + b; del groups[gi + 1]
        else: gi += 1
    SOFT = {"and", "who", "that", "as", "to", "from", "of", "with", "or", "but", "the"}
    def split(g):
        if len(g) <= 7: return [g]
        mid = len(g) / 2; cand = [j for j in range(2, len(g) - 1) if norm(DISP[g[j]]) in SOFT and j <= 7 and len(g) - j <= 7]
        j = min(cand, key=lambda j: abs(j - mid)) if cand else math.ceil(len(g) / 2)
        return split(g[:j]) + split(g[j:])
    out = []
    for g in groups: out += split(g)
    return out
caps = []
for ln in sorted(lines):
    if ln == TAG_LINE: continue
    for c in chunks(lines[ln]):
        caps.append(dict(line=ln, start=round(W[c[0]]["start"], 3), end=round(W[c[-1]]["end"], 3), text=" ".join(DISP[i] for i in c), i0=c[0], i1=c[-1]))
for a, b in zip(caps, caps[1:]): a["end"] = round(min(a["end"] + 0.25, b["start"] - 0.02), 3)
caps[-1]["end"] = round(min(caps[-1]["end"] + 0.25, OUT["start"]), 3)
cut_t = [x["f0"] / FPS for x in slots[1:]]
for c in caps:   # a cue never stays up across a cut: clear it 1 frame before the next cut after its start
    nxt = [t for t in cut_t if t > c["start"] + 1e-6]
    if nxt: c["end"] = round(min(c["end"], nxt[0] - 1 / FPS), 3)
    assert c["end"] > W[c["i1"]]["end"] - 0.25, c
# owner 11:52: the 0.35 s 'Zhu Di' cue is too short to read -> merged into the previous S10 cue, which now ends exactly at the K09->K10 cut ('took')
_zi = [k for k, c in enumerate(caps) if c["text"] == "Zhu Di"]; assert len(_zi) == 1
_k = _zi[0]; _p, _z = caps[_k - 1], caps[_k]; assert _p["text"] == "Jianwen's small son vanished too." and _p["i1"] + 1 == _z["i0"]
_cut = [t for t in cut_t if t > _z["start"]][0]; assert abs(_cut - W[_z["i1"] + 1]["start"]) < 1 / FPS   # the cut on 'took'
_p.update(text=_p["text"] + " " + _z["text"], i1=_z["i1"], end=math.floor(_cut * 1000) / 1000); del caps[_k]   # floor to the ms: last frame shown = the last S10 frame
assert len(_p["text"].split()) <= 7
assert " ".join(c["text"] for c in caps) == " ".join(DISP[:TAG_I])
for c in caps: assert not any(c["start"] < t < c["end"] for t in cut_t), f"caption straddles a cut: {c['text']}"
for c in caps: assert not any(c["start"] < t < W[c["i1"]]["start"] + 1e-6 for t in cut_t if t > c["start"] + 1e-6), f"caption straddles a cut: {c['text']}"
FALLBACK = dict(opening=dict(trigger="S02B crop frac < 0.70 of the K02 frame", slots=["S01", "S02"], S02=dict(plate=K02, f0=OP[1]["f0"], f1=OP[2]["f1"], z_end=1.10),
                             motion="S02 one WIDE K02 shot with a faster push 1.00->1.10; only ONE cut in the first 5 s (FLAG)"),
                reprise=dict(trigger="S09 crop frac < 0.70 of the K01 frame", z_start=1.06, z_end=1.14, motion="full K01 frame starting where S01's push ended (1.06) and pushing on to 1.14 on the coffin/Zhu Di: still a different framing from the opening wide (FLAG)"))
flags = [f"{x['slot']} ({x['plate'][:3].upper()}{' reprise' if x['slot'] == 'S09' else ''}) {x['dur']:.3f} s < 3 s" for x in slots if x["under3"]]
G = dict(version="v2", fps=FPS, vo=str(VO), vo_md5=VO_MD5, words=str(WORDS), words_md5=WORDS_MD5, script=str(SCRIPT), script_md5=SCRIPT_MD5, plate_map=str(PROMPTS), plate_map_md5=md5(PROMPTS),
         speech_end=SPEECH_END, tail=TAIL, total_f=TOTAL_F, total_s=round(TOTAL_F / FPS, 3), tagline_line=TAG_LINE, tagline_start=W[TAG_I]["start"],
         plates_dir="auto: plates-v2/ if it holds the plates, else plates-v1/ (owner: plates land in plates-v1/)", title=TITLE, legend=LEGEND, fallback=FALLBACK,
         outro=dict(plate=OUT["plate"], start=OUT["start"], end=OUT["end"], dur=OUT["dur"], motion=OUT["motion"]), slots=slots, captions=caps, flags=flags)
oj, om = E / "timing_grid_v2.json", E / "TIMING-GRID-v2.md"
if "--print" in sys.argv:
    for s in slots: print(f"{s['slot']:5} {s['plate'][:40]:40} f{s['f0']:5}-{s['f1']:5} {s['start']:7.3f}-{s['end']:7.3f} {s['dur']:6.3f} {'<3' if s['under3'] else '  '} {s['vo'][:60]}")
    print("TOTAL", TOTAL_F, TOTAL_F / FPS, "caps", len(caps), flags); sys.exit()
assert not oj.exists() and not om.exists(), "refusing to overwrite existing grid v2"
json.dump(G, open(oj, "w"), indent=1, ensure_ascii=False)
R = ["# Jianwen standalone: TIMING GRID v2 (owner-locked narration, measured Oliver t1)", "",
     f"Generated by `edit/make_timing_grid_v2.py` from `vo/final-vo-oliver-jianwen-v2_words.json` (md5 {WORDS_MD5}; VO md5 {VO_MD5}; script md5 {SCRIPT_MD5}). Plate map: `plate-prompts-v2b.md` (md5 {md5(PROMPTS)}; owner notes 11:28 supersede v2).",
     f"30 fps. Every shot is timed to the MEASURED VO, not the storyboard's 80 s estimate. Cut rule = Edward II v3b: 0.08 s before the cue word when the gap before it is >= 0.25 s, else the word-start frame; 3 noted overrides (S02A, S11 on 'took', S20). "
     f"Speech end {SPEECH_END} s + {TAIL} s tail = **{G['total_s']} s ({TOTAL_F} f)**. v1/v1b files are kept as they were.", "",
     "| Slot | Plate | Start | End | Dur | VO cue (first words) | Motion plan |", "|---|---|---|---|---|---|---|"]
for x in slots:
    cue = " ".join(x["vo"].split()[:7]) + (" ..." if len(x["vo"].split()) > 7 else "")
    tag = {"wide": " (WIDE)", "tight": " (TIGHT crop)", "reprise": " (REPRISE, tight crop)"}.get(x["framing"], "")
    R.append(f"| {x['slot']} | `{x['plate']}`{tag} | {x['start']:.3f} | {x['end']:.3f} | {x['dur']:.2f}{' **<3**' if x['under3'] else ''} | {cue} | {x['motion']}{(' *' + x['note'] + '*') if x['note'] else ''} |")
R += ["", "## VO per slot (exact)", ""] + [f"- **{x['slot']}** ({x['start']:.2f}-{x['end']:.2f}): {x['vo']}" for x in slots]
R += ["", f"## Captions ({len(caps)} cues; word for word; <= 7 words; never straddle a cut; L14 tagline NOT captioned, it is baked on the outro)", "", "| # | Start | End | Text |", "|---|---|---|---|"]
R += [f"| {i+1} | {c['start']:.3f} | {c['end']:.3f} | {c['text']} |" for i, c in enumerate(caps)]
R += ["", "## Opening", "", f"- S01 K01 WIDE {OP[0]['start']:.3f}-{OP[0]['end']:.3f} ({OP[0]['dur']:.2f} s) / S02A K02 WIDE {OP[1]['start']:.3f}-{OP[1]['end']:.3f} ({OP[1]['dur']:.2f} s) / S02B K02 TIGHT {OP[2]['start']:.3f}-{OP[2]['end']:.3f} ({OP[2]['dur']:.2f} s). Two cuts in the first 5 s (f{OP[1]['f0']}, f{OP[2]['f0']}), both on VO beats: the end of 'emperor.' and 'kept'. Both hook sides are on screen by 2.3 s.",
      f"- Fallback if the K02 tight crop would be < 70 % of the frame: one WIDE S02 {OP[1]['start']:.3f}-{OP[2]['end']:.3f} s pushing 1.00->1.10, FLAG (then only one cut in the first 5 s).",
      "", "## Title", "", f"- `{TITLE_TEXT.replace(chr(10), ' / ')}` (owner 11:28). Chronicle Reveal v3.2b at fontSize {TITLE_FONT}, topPercent 32.5: stroke f8-26, letters f14-42, hold f42-{TITLE['hold'][1]}, exit f{TITLE['exit'][0]}-{TITLE['exit'][1]}, stroke clears f{TITLE['strokeClear'][0]}-{TITLE['strokeClear'][1]} (clean {TITLE['clean_by_f'] / FPS:.2f} s; K03 cut {K03_F / FPS:.3f} s). Cuts f{OP[1]['f0']} and f{OP[2]['f0']} both land in the hold. {TITLE['note']}",
      "", "## K01 reprise (S09)", "", "- S01 = full-frame WIDE of K01, push 1.00->1.04 to the coffin. S09 = TIGHT crop of K01 (placeholder centre 0.50/0.52, frac 0.75) on the coffin and Zhu Di at the grave head, push 1.00->1.06, same K01 fx seed (torches, smoke, embers).",
      f"- If the crop would be < 70 % of the frame: {FALLBACK['reprise']['motion']}.",
      "", "## LEGEND (S12 / K11 only)", "", f"- `LEGEND` in Source Serif Pro Semibold {LEGEND['fontSize']} px, tracking {LEGEND['trackingEm']} em, cream {tuple(LEGEND['color'])} at {LEGEND['opacity']} opacity, soft shadow, a 2 px hairline under it at 0.45. Cap top at x {LEGEND['xPct']} % / y {LEGEND['yPct']} % (the calm upper-left corner). In f{LEGEND['in_f'][0]}-{LEGEND['in_f'][1]}, out f{LEGEND['out_f'][0]}-{LEGEND['out_f'][1]} (smoothstep, 6 px rise). {LEGEND['note']}",
      "", "## Flags", ""] + [f"- {f}" for f in flags] + [
      "- S09 (K01 reprise) stays a deliberate quick callback, 2.33 s on 'He had it buried as his nephew.' (owner 11:46).",
      "- S10/S11 (owner 11:46): the K09 -> K10 cut is on 'took' (41.167 s, word-start frame; 0.07 s gap after 'Di'), so 'Zhu Di' plays over the empty room: S10 3.13 s, S11 4.27 s. Owner 11:52: 'Zhu Di' is merged into the S10 cue ('Jianwen\'s small son vanished too. Zhu Di'), which ends exactly at the cut; the S11 cue starts on 'took'.",
      "- S20 cut is 0.21 s before 'It' (Edward rule gives 82.233 s -> 2.90 s); now exactly 3.00 s. Overrides: S02A, S11 (cue word 'took'), S20.",
      "- Tightest non-flag holds: S20 3.00 s, S17 3.10 s (opening sub-shots S01/S02A/S02B are the brief's deliberate 1.5-2.5 s cuts).",
      "- No battle plates, no war SFX. Wet paving (K08) and any water: reflections stay static. K11 stays COOL (moon-blue, warm spill only round the lantern); K13 stays WARM amber.",
      "- Outro: v2b `jianwen_outro_xuanfu_lit_window.png` with the title + tagline baked in, used as-is, no overlay text; motion kept off the lettering band."]
open(om, "w").write("\n".join(R) + "\n")
print("wrote", oj, om)
