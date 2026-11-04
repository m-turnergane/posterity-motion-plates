# Björn — TIMING BOARD v4 (rough v4)

Written Tue 2026-11-03 (EST). Source of truth: `rough_v4/logs/cuts_v4.json` + `rough_v4/logs/vo_bjorn_v4_words.json` (voiced VO, word-aligned).
1080×1920, 30 fps, **3058 frames = 101.933 s**. Frame ranges are f0–f1 (f1 exclusive). Times are timeline seconds.

| Shot | Frames | n | Start | End | Dur (s) | Cut on | Caption MarginV | Motion / source | VO under the shot |
|---|---|---|---|---|---|---|---|---|---|
| P01 | 0–82 | 82 | 0.000 | 2.733 | 2.733 | "A" | 400 | depth push | A coffin is carried into a Christian church. |
| P02 | 82–163 | 81 | 2.733 | 5.433 | 2.700 | hard, "Inside," | 400 | flat push 1.00→1.05 | Inside, the dead man is holding a sword. |
| P03 | 163–347 | 184 | 5.433 | 11.567 | 6.133 | "Legend" | 400 | depth push + **house title** (intro_v3b, top 31 %) local 0–172 = 5.433–11.167 s | Legend says Björn Ironside, son of Ragnar Lothbrok, led a fleet … |
| P04 | 347–463 | 116 | 11.567 | 15.433 | 3.867 | "His" | 400 | flat push | His tutor, the raider Hastein, planned to crown him emperor there. |
| P05 | 463–778 | 315 | 15.433 | 25.933 | 10.500 | "A" | 400 | clip: p05_test_v4b_silent (map, offset 0.3767 s, no pause) | A Viking fleet really did sail, past Spain, into the Mediterranean, … |
| P06 | 778–913 | 135 | 25.933 | 30.433 | 4.500 | "At" | 400 | flat push 1.00→1.04, water-only glints (masked) | At a walled city by the sea, Hastein believed he had found Rome. |
| P07 | 913–966 | 53 | 30.433 | 32.200 | 1.767 | hard, "But" | 615 | flat push | But the gates were barred. |
| P08 | 966–1112 | 146 | 32.200 | 37.067 | 4.867 | "So" | 400 | flat push | So Hastein sent word that he was dying, and wished to become a Christian. |
| P09 | 1112–1208 | 96 | 37.067 | 40.267 | 3.200 | "The" | 400 | flat push 1.00→1.04 | The bishop and count could have kept the gates shut. |
| P10 | 1208–1318 | 110 | 40.267 | 43.933 | 3.667 | hard, "They" | 400 | flat push | They chose mercy, and Hastein was baptised. |
| P11 | 1318–1444 | 126 | 43.933 | 48.133 | **4.200** | "Then," | 400 | flat push | Then, on Hastein's orders, his companions staged their grief. |
| P12 | 1444–1561 | 117 | 48.133 | 52.033 | 3.900 | "They" | 400 | flat push | They said he was dead, and wished to be buried in the city. |
| P13 | 1561–1808 | 247 | 52.033 | 60.267 | 8.233 | "The" | 860 | flat wide push 1.00→1.02, then **hard cut at frame 1699 (56.633 s, local 138)** to the mail detail z 1.300→1.305, no vertical move | The bishop let the funeral in. Behind the coffin, the mourners wore armour … |
| P14 | 1808–1901 | 93 | 60.267 | 63.367 | 3.100 | hard, "leapt" = score HIT | 400 | flat push, snap | leapt from the coffin and struck the bishop down. |
| P15 | 1901–2019 | 118 | 63.367 | 67.300 | 3.933 | "Only" | 400 | flat push | Only after the city fell did the raiders learn the truth. |
| P16 | 2019–2188 | 169 | 67.300 | 72.933 | 5.633 | hard, "This" | 400 | depth push | This wasn't Rome. It was Luna, an old Roman town. |
| P17A | 2188–2413 | 225 | 72.933 | 80.433 | 7.500 | "But" | 400 | clip: p17a_glints_only (KEEP plate, glints only) | But the strangest mistake may be the name. The fleet was real, but … |
| P17B | 2413–2639 | 226 | 80.433 | 87.967 | 7.533 | "The" | 400 | clip: p17b_proof (depth_v1 push 1.00→1.06, rel. parallax 1.46 px) | The oldest surviving funeral story, by the churchman Dudo, gave Hastein … |
| P18 | 2639–2765 | 126 | 87.967 | 92.167 | 4.200 | "Decades" | 400 | flat push (P18_KEEP untouched) | Decades later, a monk named William placed Björn aboard. |
| P20 | 2765–2923 | 158 | 92.167 | 97.433 | 5.267 | "They" | 400 | depth push | They conquered the wrong Rome. Perhaps history crowned the wrong Viking. |
| OUTRO | 2923–3058 | 135 | 97.433 | 101.933 | 4.500 | "History" | none | flat push 1.00→1.03 (outro as is) | History remembers the victors. We remember the rest. (tagline, NOT captioned) |

## Key sync points
- Coffin hook P01–P02 (0–5.433 s), then house title over P03 (5.433–11.167 s), placed 15 points lower than v3 (topPercent 16 → 31).
- "armour" 56.674 s → P13 internal hard cut 1 frame earlier at 56.633 s (frame 1699).
- "leapt" 60.294 s → P14 hard cut 60.267 s = score hit (track 127.0 s).
- Score: one continuous seg3 run from 54.767 s to the end; see SCORE-PLAN-v4.md.
- Captions stop at the OUTRO cut (97.433 s).

## Flags
- P11 runs 4.200 s; the owner asked for about 3.5–4 s. It is held by the VO: "Then," 44.023 → "grief." 47.820 s (3.8 s of speech), next word "They" 48.220 s carries the P12 cut. Getting to ≤ 4.0 s needs a VO retime (tighter gap), not a picture trim. FLAG.
- P13 mail-detail zoom end reduced 1.31 → 1.305 so pixel density stays ≤ 1.5 (1.4995).
- P17B: optional sky drift through the arch NOT done (static sky).
