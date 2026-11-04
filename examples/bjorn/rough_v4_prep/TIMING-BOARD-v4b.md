# Björn — TIMING BOARD v4b (rough v4b)

Written Tue 2026-11-03 (EST), derived from TIMING-BOARD-v4.md (left unchanged).

v4b = v4 with ONE timing change: +0.500 s (15 frames) of silence after "barred." (the gap is digital silence in the v4 VO; the local-noise fill therefore inserts silence) (VO 31.927 → "So" now 32.810 s). P07 1.767 → 2.267 s; every cut, word, caption, score cue, automation ramp and dip from P08 on moves +15 frames / +0.5 s. Nothing before 32.08 s changes.

Source of truth: `rough_v4/logs/cuts_v4b.json` + `rough_v4/logs/vo_bjorn_v4b_words.json` (voiced VO, word-aligned).
1080×1920, 30 fps, **3073 frames = 102.433 s (1:42.4)**. Frame ranges are f0–f1 (f1 exclusive). Times are timeline seconds.

| Shot | Frames | n | Start | End | Dur (s) | Cut on | Caption MarginV | Motion / source | VO under the shot |
|---|---|---|---|---|---|---|---|---|---|
| P01 | 0–82 | 82 | 0.000 | 2.733 | 2.733 | "A" | 400 | depth push | A coffin is carried into a Christian church. |
| P02 | 82–163 | 81 | 2.733 | 5.433 | 2.700 | hard, "Inside," | 400 | flat push 1.00→1.05 | Inside, the dead man is holding a sword. |
| P03 | 163–347 | 184 | 5.433 | 11.567 | 6.133 | "Legend" | 400 | depth push + **house title** (intro_v3b, top 31 %) local 0–172 = 5.433–11.167 s | Legend says Björn Ironside, son of Ragnar Lothbrok, led a fleet … |
| P04 | 347–463 | 116 | 11.567 | 15.433 | 3.867 | "His" | 400 | flat push | His tutor, the raider Hastein, planned to crown him emperor there. |
| P05 | 463–778 | 315 | 15.433 | 25.933 | 10.500 | "A" | 400 | clip: p05_rough_v4b/p05_test_v4b_silent, v4b phone-legible labels (map, offset 0.3767 s, no pause) | A Viking fleet really did sail, past Spain, into the Mediterranean, … |
| P06 | 778–913 | 135 | 25.933 | 30.433 | 4.500 | "At" | 400 | flat push 1.00→1.04, water-only glints (masked) | At a walled city by the sea, Hastein believed he had found Rome. |
| P07 | 913–981 | 68 | 30.433 | 32.700 | **2.267** | hard, "But" | 615 | flat push (same move over 68 frames; v4b +0.5 s silence after "barred.") | But the gates were barred. |
| P08 | 981–1127 | 146 | 32.700 | 37.567 | 4.867 | "So" | 400 | flat push | So Hastein sent word that he was dying, and wished to become a Christian. |
| P09 | 1127–1223 | 96 | 37.567 | 40.767 | 3.200 | "The" | 400 | flat push 1.00→1.04 | The bishop and count could have kept the gates shut. |
| P10 | 1223–1333 | 110 | 40.767 | 44.433 | 3.667 | hard, "They" | 400 | flat push | They chose mercy, and Hastein was baptised. |
| P11 | 1333–1459 | 126 | 44.433 | 48.633 | **4.200** | "Then," | 400 | flat push | Then, on Hastein's orders, his companions staged their grief. |
| P12 | 1459–1576 | 117 | 48.633 | 52.533 | 3.900 | "They" | 400 | flat push | They said he was dead, and wished to be buried in the city. |
| P13 | 1576–1823 | 247 | 52.533 | 60.767 | 8.233 | "The" | 860 | flat wide push 1.00→1.02, then **hard cut at frame 1714 (57.133 s, local 138)** to the mail detail z 1.300→1.305, no vertical move | The bishop let the funeral in. Behind the coffin, the mourners wore armour … |
| P14 | 1823–1916 | 93 | 60.767 | 63.867 | 3.100 | hard, "leapt" = score HIT | 400 | flat push, snap | leapt from the coffin and struck the bishop down. |
| P15 | 1916–2034 | 118 | 63.867 | 67.800 | 3.933 | "Only" | 400 | flat push | Only after the city fell did the raiders learn the truth. |
| P16 | 2034–2203 | 169 | 67.800 | 73.433 | 5.633 | hard, "This" | 400 | depth push | This wasn't Rome. It was Luna, an old Roman town. |
| P17A | 2203–2428 | 225 | 73.433 | 80.933 | 7.500 | "But" | 400 | clip: p17a_glints_only (KEEP plate, glints only) | But the strangest mistake may be the name. The fleet was real, but … |
| P17B | 2428–2654 | 226 | 80.933 | 88.467 | 7.533 | "The" | 400 | clip: p17b_proof (depth_v1 push 1.00→1.06, rel. parallax 1.46 px) | The oldest surviving funeral story, by the churchman Dudo, gave Hastein … |
| P18 | 2654–2780 | 126 | 88.467 | 92.667 | 4.200 | "Decades" | 400 | flat push (P18_KEEP untouched) | Decades later, a monk named William placed Björn aboard. |
| P20 | 2780–2938 | 158 | 92.667 | 97.933 | 5.267 | "They" | 400 | depth push | They conquered the wrong Rome. Perhaps history crowned the wrong Viking. |
| OUTRO | 2938–3073 | 135 | 97.933 | 102.433 | 4.500 | "History" | none | flat push 1.00→1.03 (outro as is) | History remembers the victors. We remember the rest. (tagline, NOT captioned) |

## Key sync points
- Coffin hook P01–P02 (0–5.433 s), then house title over P03 (5.433–11.167 s), placed 15 points lower than v3 (topPercent 16 → 31).
- "armour" 57.174 s → P13 internal hard cut 1 frame earlier at 57.133 s (frame 1714).
- "leapt" 60.794 s → P14 hard cut 60.767 s (frame 1823) = score hit (track 127.0 s exactly at the cut; verified in mix_v4b_log.json and by frame-diff on the render).
- Score: one continuous seg3 run from 55.267 s to the end (track 121.5 → 168.666 s, no joins after the hit); seg1 simply plays 0.5 s further into the cue across the inserted pause (no edit); see SCORE-PLAN-v4.md.
- Captions stop at the OUTRO cut (97.933 s).

## Flags
- P11 runs 4.200 s; the owner asked for about 3.5–4 s. It is held by the VO: "Then," 44.523 → "grief." 48.320 s (3.8 s of speech), next word "They" 48.720 s carries the P12 cut. Getting to ≤ 4.0 s needs a VO retime (tighter gap), not a picture trim. FLAG.
- P13 mail-detail zoom end reduced 1.31 → 1.305 so pixel density stays ≤ 1.5 (1.4995).
- P17B: optional sky drift through the arch NOT done (static sky).
