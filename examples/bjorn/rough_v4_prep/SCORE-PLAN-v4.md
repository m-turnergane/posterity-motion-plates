# Björn: SCORE PLAN v4 (rough v4), 2026-11-03 EST

**Score:** "Uprising" by Scott Buckley, CC BY 4.0. Source `rough_v1/score_preview/source/Uprising.mp3`, md5 3218446ad0b0ebf17deb82e2ae88bb57, 205.66 s.

**Mixer:** `rough_v4/build/mix_bjorn_v4.py` (md5 b05dbac0dad6fd6eb787342bf6da058e).
- The chain is the rough_v2b chain, unchanged: VO chain, bed calibrated 12 LU under the VO, sidechain duck, bus compressor, 4× oversampled limiter.
- Output: `rough_v4/scratch/audio/mix_bjorn_v4.wav` (md5 1efbea4908321a6950917fcaf06a8dd1), 101.933 s.
  - WAV: −13.9 LUFS integrated, true peak −4.4 dBTP (target −14 LUFS / ≤ −1 dBTP once encoded).
  - VO −23.1 LUFS before master; bed −19.1 dB; master +10.2 dB.
- Logs: `rough_v4/logs/mix_v4_log.json`, `rough_v4/logs/margins_v4.json` (margins for all 244 words).

## 1. Owner directive (items 4 and 5): one continuous, ominous score

| # | Timeline (v4 s) | Track (s) | Level | Role |
|---|---|---|---|---|
| seg1 | 0.000 → 45.033 | 60.0 → 105.0 | 0 dB, fades 1.5 in / 1.2 out | v2b build-up (unchanged) |
| seg2 | 43.833 → 55.734 | 5.0 → 16.9 | −5 dB, fades 1.2 / 1.0 | v2b build-up (unchanged), the drop under P11 to P13 |
| seg3 | 54.767 → 101.933 | **121.5 → 168.7, ONE continuous run** | volume automation only | the "leapt" hit and the run to the outro |

- Seg2 and seg3 keep the v2b offsets from the cuts:
  - seg2 starts 0.1 s before P11
  - seg1 ends 1.1 s after P11
  - seg2 ends 0.967 s after seg3 starts
- **The "leapt" hit:**
  - Track **127.0 s sits exactly on the P14 hard cut at 60.267 s**. "leapt" starts at 60.294 s (+27 ms).
  - The un-ducked share rises over the 60 ms before the cut, **holds 0.2 s** (to 60.467), then eases back to a full duck by 60.722 (25 ms before "the coffin"). Same as v2b HOLD 0.2.
- **After the hit there are no more edits.** v2 seg4 (track 20.0) and seg5 (track 188.3) are removed. Level changes are volume automation only:
  - **−6 dB plateau** from P16 − 0.5 s (66.8 → 68.3 s, raised-cosine ramp) to P20 − 0.4 s. This matches the level of the old v2 seg4 through P16–P18.
  - Ramps back up over 91.767 → 92.967 to **−3 dB for P20 and the outro**. Run 1 at 0 dB left "Rome." at 4.6 dB and "We" at 1.4 dB (1–4 kHz), so the tail was lowered.
  - The bed fades out over the last 1.0 s (100.933 → 101.933).
- **Duck pick: xd6.**
  - Bed dip under "the victors." = −2 dB (v2b) − 6 dB = **−8 dB nominal**, measured **−8.0 dB** (bed RMS −36.84 vs −28.84 without the dip, span 98.492–99.508).
  - The dip is held through "We remember the rest." (to 101.598). FLAG: this extends xd6 past "the victors." The alternative is to end it at "victors." + 0.15.

## 2. Duck findings (xd6, same method as the examiner: VO-only and bed-only stems through the same chain)
- Hit:
  - Bed RMS in the 0.30 s hit window is −20.12 dB (−28.54 without the ease).
  - Bed peak in the window is −9.12 dB.
  - VO "leapt" RMS is −14.17 dB, so the **hit sits 5.95 dB under the VO**. In v2b it was 3.9 dB under.
  - VO over bed from "leapt" to "struck" is **11.72 dB**.
- The weakest words (1–4 kHz band) are all at the designed hit:

| Word | v4 time | 1–4 kHz | house | phone |
|---|---|---|---|---|
| "the" (coffin) | 60.747 | 6.8 | 17.2 | 10.3 |
| "Rome." (P20) | 93.431 | 6.9 | 13.6 | 13.6 |
| "leapt" | 60.294 | 7.2 | 6.7 | 7.4 |

- No word is under 6.8 dB in the 1–4 kHz band. v2b had −6.2 dB at its worst "a".
- **The two "a" words (FLAG):**
  - In v2b, the weakest words in the whole cut were "**a**@81.189" (1–4 kHz −6.2, phone −4.3) and "**a**@81.991" (+2.2), in "in **a** chronicle by **a** monk". The v4 script no longer has that phrase.
  - The weakest "a" words in v4 are:
    - "**a** walled city" @26.214 (P06): 1–4 kHz **7.9**, house 20.1, phone 21.1
    - "become **a** Christian" @36.013 (P08): 1–4 kHz **12.1**
    - "**a** monk named William" @89.348: 12.7
  - All are positive margins. "a walled" is the one to listen to: a short, unstressed article under the seg1 build.

## 3. Restart audit (raw bed, before the duck and automation)
Mean-channel RMS in 0.5 s windows either side of each crossfade:

| Join | Crossfade (v4 s) | Before | During | After |
|---|---|---|---|---|
| seg1 → seg2 (P11) | 43.833–45.033 | −19.97 | −23.91 | −33.64 dB |
| seg2 → seg3 (P13, 5.5 s before the hit) | 54.767–55.734 | −31.31 | −28.30 | −34.25 dB |

- **Joins after the hit: none.** Track time runs 121.5 → 168.666 without a break.
- Both joins are in the owner-kept v2b build-up, under VO, with crossfades of 1.0 s or more. Neither is a hard restart.
- Mixed bed RMS per shot (dB, after duck and automation):

| Shot | Bed RMS | Shot | Bed RMS | Shot | Bed RMS |
|---|---|---|---|---|---|
| P01 | −37.4 | P08 | −31.4 | P15 | −27.9 |
| P02 | −36.1 | P09 | −30.5 | P16 | −31.5 |
| P03 | −36.4 | P10 | −31.1 | P17A | −33.8 |
| P04 | −34.4 | P11 | −39.5 | P17B | −33.3 |
| P05 | −31.5 | P12 | −41.4 | P18 | −32.8 |
| P06 | −33.5 | P13 | −39.7 | P20 | −29.1 |
| P07 | −32.1 | P14 | −26.7 | OUTRO | −34.9 |

## 4. Cue points (v4 timeline)

| Time (s) | Cue |
|---|---|
| 0.000 | seg1 in (1.5 s fade), track 60.0 |
| 43.833 | P11 − 0.1: seg2 in (−5 dB); seg1 out by 45.033 |
| 54.767 | seg3 in (track 121.5, 1.0 s fade); seg2 out by 55.734 |
| 56.633 | P13 internal hard cut (wide → mail detail, 1 frame before "armour" at 56.674); no music event |
| 60.267 | **P14 hard cut = track 127.0 = HIT** ("leapt" 60.294); un-ducked to 60.467, full duck by 60.722 |
| 66.8 → 68.3 | automation down to −6 dB (P16 "wasn't Rome.") |
| 91.767 → 92.967 | automation up to −3 dB (P20) |
| 98.492 → 101.598 | xd6 dip −8 dB ("the victors. We remember the rest.") |
| 100.933 → 101.933 | bed fade out; picture ends 101.933 (3058 frames) |

## 5. Not done / approvals
- No new music, no stems, and no EQ on the score. Only gain automation and the existing duck.
- The tail at −3 dB (instead of 0) and the xd6 dip held to the end are the two deviations from the literal plan. Both are FLAGGED above.
