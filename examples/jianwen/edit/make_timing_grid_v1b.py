"""Jianwen v1b timing grid -> edit/timing_grid_v1b.json + edit/TIMING-GRID-v1b.md (Edward II v3b cut rule; refuses to overwrite).
v1b = v1 + Vellum 2026-10-30: J01 split into WIDE (S01A) + TIGHT reframe of the same plate (S01B) at the 'and called it' beat; title carries across the cut; outro motion approved."""
import json, hashlib, re, sys, math
from pathlib import Path
J = Path("/workspace/posterity/standalones/jianwen"); E = J / "edit"
WORDS = J / "vo/final-vo-oliver-jianwen-v1_words.json"; VO = J / "vo/final-vo-oliver-jianwen-v1.wav"
VO_MD5 = "6bd7b1c33777fc8ffff6be6ac9610d6a"; WORDS_MD5 = "32b2c98515e0018f3406c257cd091dc1"
FPS = 30; SPEECH_END = 91.50; TAIL = 0.50
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
assert md5(VO) == VO_MD5 and md5(WORDS) == WORDS_MD5, "VO / words md5 mismatch"
W = json.load(open(WORDS))["words"]; assert len(W) == 235
norm = lambda s: re.sub(r"[^a-z']", "", s.lower().replace("\u2019", "'"))
toks = [norm(w["word"]) for w in W]
def widx(phrase, after=0):
    p = [norm(x) for x in phrase.split()]
    for i in range(after, len(toks) - len(p) + 1):
        if toks[i:i + len(p)] == p: return i
    raise SystemExit(f"phrase not found: {phrase}")
fob = lambda t: int(math.floor(t * FPS + 1e-6))
# slot, plate file, cue phrase, motion plan, note
SL = [
 ("S01A", "j01_body_from_burning_palace.png", "They pulled", "WIDE: Chronicle Reveal title manifests (lock v3.2b, f0-118, carries across the cut); push 1.00->1.04 toward the litter; burning roof = BIG FIRE glow pulse + spill on bearers/robes (static flame shapes); soldiers' torches flicker+spill; embers rise off the roof; warm haze", "opening cut 1 of 2: wide"),
 ("S01B", "j01_body_from_burning_palace.png", "and called it", "TIGHT: reframe/crop of the SAME J01 plate on the shrouded litter (crop >= 70 % of frame, else fallback); push 1.00->1.04; same fx seed + global clock as S01A so fire/embers continue through the cut; title still holding, exits f88-108, clean f118", "opening cut 2 of 2: tight; cut on 'and' (0.21 s gap -> word-start frame)"),
 ("S02", "j02_yongle_searching_candle.png", "So why did", "push to his face; single tall candle: flame-shape sway + flicker + spill across face/robe; warm haze + lit motes", ""),
 ("S03", "j03_founder_and_grandson.png", "The emperor was", "slow drift founder->grandson; rows of candles on bronze stands: shape motion + grouped spill; haze", ""),
 ("S04", "j04_zhu_di_northern_wall_torches.png", "His uncles were", "push up to Zhu Di; wall torches: glow pulse + spill on armour/brick (torch shapes static); light snow-mist drift optional (no land warp)", ""),
 ("S05", "j05_jianwen_seals_edicts.png", "When Jianwen began", "push to edicts + courier; desk candles shape motion + spill; paper lantern flicker + gentle sway (pivot at cord)", ""),
 ("S06", "j06_nanjing_gate_opened_night.png", "After three years", "push through the gate; massed army torches glow pulse + spill on gate leaves/brick; faint smoke haze; NO war SFX (not a battle plate)", ""),
 ("S07", "j07_palace_roofs_aflame_wide.png", "Then the palace", "push toward the hall; BIG FIRE: static flame shapes, pulsing glow + spill on courtyard/roof edges; dense embers + smoke drift above roofline", ""),
 ("S08", "j08_night_burial_torches.png", "and he buried", "very slow push; pole torches glow pulse + spill on mourners/coffin (static torch shapes); faint smoke", "cut at L07b 'and he buried' (Edward rule); S09 cut moved to 'son,' so S08 >= 3 s"),
 ("S09", "j09_empty_childs_room.png", "son a small", "very slow push to the small shoes; single low candle shape motion + spill on floor/bedding; lit motes", "cut on 'son,' (override; 0.03 s word gap) so the empty room lands on the word 'son'"),
 ("S10", "j10_yongle_enthroned_calendar.png", "Zhu Di took", "push brazier->Yongle; candle rows shape motion; brazier = big-fire glow pulse + spill (static flame)", ""),
 ("S11", "j11_rumour_whispered_lantern.png", "But a rumour", "push to the two faces; hanging paper lantern flicker + spill on faces + gentle sway", ""),
 ("S12", "j12_hu_ying_search_campfire.png", "Yongle sent an", "push to Hu Ying; campfire glow pulse + spill (static flame) + REAL embers + smoke; temple lantern flicker + sway; valley mist drift", ""),
 ("S13", "j13_treasure_fleet_lanterns.png", "The official History", "push across the junks; deck lanterns flicker + small sway; quay torches glow + spill; water and its reflections held STATIC (masked out of spill/mist)", ""),
 ("S14", "j14_hu_ying_returns_night.png", "More than twenty", "push to Hu Ying at the gate; guards' torches glow pulse + spill on him/gate; dust haze", ""),
 ("S15", "j15_midnight_talk_one_candle.png", "and Yongle rose", "push between the two faces; single low candle: shape motion + strong local spill on both faces", "cut at L13b 'and Yongle rose' (0.15 s gap -> word-start frame)"),
 ("S16", "j16_closed_door_light_beneath.png", "Only then", "very slow push to the door gap; light under the door flicker + spill on floor only; small candle by blank page shape motion", ""),
 ("S17", "j17_figure_walking_from_fire.png", "Whether Jianwen died", "push following the figure; distant city = big-fire glow pulse (static); paper lantern flicker + sway; REAL embers drifting + smoke + ground mist", ""),
 ("OUTRO", "jianwen_outro_mountain_temple_lantern.png", "History remembers", "OutroHold (no text overlay, baked lettering untouched): temple lantern flicker + sway, mist + a few embers kept OUT of the lettering box; slow push only if lettering stays inside frame; music fades", "baked owner outro, used as-is"),
]
OPENING = ("S01A", "S01B")   # opening-only exception to the 3 s rule (1.5-2.5 s target)
starts = []
for i, (s, p, ph, mo, nt) in enumerate(SL):
    k = widx(ph, widx(SL[i - 1][2]) + 1 if i else 0)
    if i == 0: f0 = 0
    else:
        gap = W[k]["start"] - W[k - 1]["end"]
        f0 = fob(W[k]["start"] - 0.08) if gap >= 0.25 else fob(W[k]["start"])
    starts.append((k, f0))
TOTAL_F = fob(SPEECH_END + TAIL)
lines = {}
for w in W: lines.setdefault(w["line"], []).append(w)
slots = []
for i, (s, p, ph, mo, nt) in enumerate(SL):
    k, f0 = starts[i]; f1 = starts[i + 1][1] if i + 1 < len(SL) else TOTAL_F
    k1 = starts[i + 1][0] if i + 1 < len(SL) else len(W)
    vo = " ".join(w["word"] for w in W[k:k1])
    slots.append(dict(slot=s, plate=p, framing=("tight" if s == "S01B" else "wide" if s == "S01A" else "full"),
                      crop=(dict(frac=0.75, center=[0.50, 0.55], min_frac=0.70, note="placeholder: set center/frac on the real J01 plate; frac = crop width/plate width (= height fraction, 9:16 kept)") if s == "S01B" else None), f0=f0, f1=f1, start=round(f0 / FPS, 3), end=round(f1 / FPS, 3), dur=round((f1 - f0) / FPS, 3),
                      first_word=W[k]["word"], first_word_t=W[k]["start"], vo=vo, motion=mo, note=nt,
                      under3=(f1 - f0) < 3 * FPS and s not in OPENING))

OP = [x for x in slots if x["slot"] in OPENING]
assert len(OP) == 2 and all(1.5 <= x["dur"] <= 2.65 for x in OP), [(x["slot"], x["dur"]) for x in OP]
FALLBACK = dict(trigger="S01B crop frac < 0.70 of the J01 frame (would go soft at 1080x1920)", slot="S01", plate=OP[0]["plate"], f0=0, f1=OP[1]["f1"],
                start=0.0, end=OP[1]["end"], dur=round(OP[1]["f1"] / FPS, 3), z_start=1.00, z_end=1.14,
                motion="single WIDE shot with a faster push 1.00->1.14 (v1 was 1.06) so the opening still moves; title unchanged; FLAG it in the report")
# captions: Edward auto_chunks (<=7 words, break at punctuation), tagline (L16 'History remembers... rest.') not captioned (baked on outro)
CUTW = {k for k, _ in starts}
def chunks(ws, base):
    groups, cur = [], []
    for j, w in enumerate(ws):
        if cur and base + j in CUTW: groups.append(cur); cur = []      # never let a caption straddle a picture cut
        cur.append(w)
        if re.search(r"[.,?!;:]$", w["word"]): groups.append(cur); cur = []
    if cur: groups.append(cur)
    gi = 0                                                             # merge 1-2 word fragments forward (same shot, <= 7 words)
    while gi < len(groups) - 1:
        a, b = groups[gi], groups[gi + 1]
        if len(a) <= 2 and len(a) + len(b) <= 7 and base + ws.index(b[0]) not in CUTW: groups[gi] = a + b; del groups[gi + 1]
        else: gi += 1
    SOFT = {"and", "who", "that", "as", "to", "from", "of", "with", "or", "but", "the"}
    def split(g):
        if len(g) <= 7: return [g]
        mid = len(g) / 2; cand = [i for i in range(2, len(g) - 1) if norm(g[i]["word"]) in SOFT and i <= 7 and len(g) - i <= 7]
        i = min(cand, key=lambda i: abs(i - mid)) if cand else math.ceil(len(g) / 2)
        return split(g[:i]) + split(g[i:])
    out = []
    for g in groups: out += split(g)
    return out
caps = []
for ln in sorted(lines):
    if ln == 16: continue
    base = next(i for i, w in enumerate(W) if w["line"] == ln)
    for c in chunks(lines[ln], base):
        caps.append(dict(line=ln, start=round(c[0]["start"], 3), end=round(c[-1]["end"], 3), text=" ".join(w["word"] for w in c)))
for a, b in zip(caps, caps[1:]): a["end"] = round(min(max(a["end"] + 0.25, a["end"]), b["start"] - 0.02), 3)
G = dict(version="v1b", fps=FPS, vo=str(VO), vo_md5=VO_MD5, words=str(WORDS), words_md5=WORDS_MD5, speech_end=SPEECH_END, tail=TAIL,
         total_f=TOTAL_F, total_s=round(TOTAL_F / FPS, 3), plates_dir=str(J / "plates-v1"),
         title=dict(text="THE EMPEROR WHO\nWALKED OUT OF THE FIRE", slots=list(OPENING), start_f=0, clean_by_f=118, topPercent=32.5, fontSize=74,
                    carries_cut_f=OP[1]["f0"],
                    note="lock v3.2b 4.0 s across S01A+S01B (cut f78 lands in the hold f42-88, as Edward v3 carried the title across its opening cuts); fontSize 74 (house 88) because line 2 is 1151 px at 88 > 92% width; bandHeightPercent 14 kept; check height vs faces on J01 with --test-frames"),
         opening_fallback=FALLBACK, outro=dict(approved="Vellum 2026-10-30", dur=slots[-1]["dur"], motion="light lantern sway + mist + few embers, all kept off the lettering"),
         slots=slots, captions=caps,
         flags=[s["slot"] + f" {s['dur']}s < 3 s" for s in slots if s["under3"]])
oj, om = E / "timing_grid_v1b.json", E / "TIMING-GRID-v1b.md"
if "--print" in sys.argv:
    for s in slots: print(s["slot"], s["f0"], s["f1"], s["start"], s["end"], s["dur"], s["first_word"], s["under3"])
    print("TOTAL", TOTAL_F, TOTAL_F / FPS, "caps", len(caps)); sys.exit()
assert ("--replace-own-draft" in sys.argv) or (not oj.exists() and not om.exists()), "refusing to overwrite existing grid"
json.dump(G, open(oj, "w"), indent=1, ensure_ascii=False)
R = ["# Jianwen \"The Emperor Who Walked Out of the Fire\": TIMING GRID v1b", "",
     "v1b = v1 + Vellum's calls (2026-10-30): J01 split into a WIDE and a TIGHT reframe of the same plate at 2.600 s ('and called it the emperor'); the title carries across the cut; outro motion approved at 4.97 s; VO + Ripples unchanged. v1 files kept as they were.", "",
     f"Generated by `edit/make_timing_grid_v1b.py` from `vo/final-vo-oliver-jianwen-v1_words.json` (md5 {WORDS_MD5}; VO md5 {VO_MD5}).",
     f"30 fps. Cut rule = Edward II v3b: cut 0.08 s before the cue word when the gap before it is >= 0.25 s, else on the word-start frame. "
     f"Speech end {SPEECH_END} s (10 ms RMS > -45 dB) + {TAIL} s tail = **{G['total_s']} s ({TOTAL_F} f)**. Machine-readable twin: `edit/timing_grid_v1b.json` (the build script reads it).", "",
     "| Slot | Plate | Start | End | Dur | VO cue (first words) | Motion plan |", "|---|---|---|---|---|---|---|"]
for x in slots:
    cue = " ".join(x["vo"].split()[:7]) + (" ..." if len(x["vo"].split()) > 7 else "")
    R.append(f"| {x['slot']} | `{x['plate']}`{' (TIGHT crop)' if x['framing'] == 'tight' else ' (WIDE)' if x['framing'] == 'wide' else ''} | {x['start']:.3f} | {x['end']:.3f} | {x['dur']:.2f}{' **<3**' if x['under3'] else ''} | {cue} | {x['motion']}{(' *' + x['note'] + '*') if x['note'] else ''} |")
R += ["", "## VO per slot (exact)", ""] + [f"- **{x['slot']}** ({x['start']:.2f}-{x['end']:.2f}): {x['vo']}" for x in slots]
R += ["", "## Captions (repeat the VO word for word; <= 7 words; L16 tagline not captioned because it is baked on the outro)", "",
      "| # | Start | End | Text |", "|---|---|---|---|"] + [f"| {i+1} | {c['start']:.3f} | {c['end']:.3f} | {c['text']} |" for i, c in enumerate(caps)]
R += ["", "## Title", "", f"- `{G['title']['text'].replace(chr(10), ' / ')}` - Chronicle Reveal v3.2b across S01A (wide) + S01B (tight), frames 0-118: stroke f8-26, letters manifest f14-42, full hold f42-88 (the cut at f78 lands inside the hold), letters exit f88-108, stroke clears f97-118 (clean by 3.93 s, S02 cut at 4.93 s). {G['title']['note']}. topPercent {G['title']['topPercent']} (prompts reserve a calm 25-40 % band on J01) - confirm on the real plate with --test-frames.",
      "", "## Flags", "",
      "- No shot after the opening is under 3 s. S08 (prompts: 2.8 s) is fixed by moving the S09 cut from 'Jianwen's' to 'son,' (S08 3.30 s, S09 3.33 s).",
      f"- Opening (Vellum): S01A WIDE {OP[0]['start']:.3f}-{OP[0]['end']:.3f} ({OP[0]['dur']:.2f} s) + S01B TIGHT {OP[1]['start']:.3f}-{OP[1]['end']:.3f} ({OP[1]['dur']:.2f} s), cut on 'and' (gap 0.21 s < 0.25 -> word-start frame 78). S01A is 0.10 s over the 2.5 s target; the next earlier beat ('body' 0.78 s / 'from' 1.60 s) would leave S01B > 3 s, so 2.60 is the closest VO beat to Vellum's 2.6. Opening = 2 cuts in the first 5 s (f78, f148).",
      f"- S01B is a crop of J01 (placeholder centre 0.50/0.55, frac 0.75). If the real plate cannot hold a clean tight shot at >= 70 % of the frame, the build falls back to ONE wide S01 0-{FALLBACK['end']:.3f} s with a faster push 1.00->1.14 and prints a FLAG.",
      "- Outro 4.97 s (prompts said 3.2 s; brief asks 4.5-5 s): met by starting at 'History remembers' and holding 0.5 s past speech end. Motion APPROVED by Vellum: light lantern sway + mist + few embers, all off the lettering.",
      "- No battle plates, so no war SFX anywhere (S06 is a gate opening, not combat).",
      "- J13 water: reflections must stay static; mask the water out of mist and spill.",
      "- Motion read at 360x640: embers/motes >= 2.5 plate px, near-source pulse ~30 % p-p (Edward sizes 0.9-1.7 px vanish at phone size)."]
open(om, "w").write("\n".join(R) + "\n")
print("wrote", oj, om)
