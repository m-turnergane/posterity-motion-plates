# Báthory Rough v3c QC (Sat Oct 31 2026, ~11:30 PM EDT)

**Render:** v3/renders/bathory_rough_v3c.mp4. md5 25d23e937c3a2022425b48bee41ddcc4, 113,074,131 B.
- 102.833 s, 1080×1920, 30 fps, 3085 frames.
- Audio: −14.1 LUFS integrated, −4.2 dBTP, LRA 3.7.

**Built from:** v3b (md5 63716245…).
**Scripts:** build_bathory_rough_v3c.py, mix_v3c.py, retime_v3c.py.
**Logs:** logs_v3c/.
**Sheet:** bathory_rough_v3c_contact_sheet.jpg.
**Captions:** bathory_rough_v3c_captions.ass, 46 lines.

## Outro (restored)
- **Plate:** v2/plates/outro_bathory_csejte_first_light_OWNER.png, md5 084f8354…, 942×1670.
- **Timing:** 94.433 → 102.833, so the outro runs **8.400 s**.
- **Motion:** F push 1.00→1.06. Peak density is 1.219 output px per source px (limit 1.5, checked with motion/guardrails.py).
- **Dust:** dust_v1 first-light motes, in the sky only. The wordmark, rule and tagline, the castle, the birds and the land are all protected.
- **Leak proof** (logs_v3c/outro_text_leak_proof_v3c.json) passes on 7 frames, using a lossless check at the render stage:
  - text region in plate space: 0 changed px
  - output frame compared with the pushed static plate inside the warped text box: 0 changed px
  - dust is active elsewhere: 3.3k–4.7k px change per frame
- **Tagline VO:** the gap before "History…" was widened from 0.859 s to 2.192 s (retime_v3c.py, which changes only that gap). No words were changed.
  - The tagline now plays from **95.436 to 100.187**: it starts 1.0 s after the outro cut and ends 2.65 s before the end of the cut.
  - The burned tagline caption was dropped (TAG_LINE excluded), so the tagline appears on screen only once, from the plate.
- **H04b** runs 87.333–94.433 (7.1 s). The push now reaches her eyes on the last frame. The last caption ("the Blood Countess.") ends at 93.494, which leaves 0.94 s with no caption at the end of H04b.

## Door beat
- **Cause:** v3b had no door animation code. The "closing" was the registered match cut from B13a (doors open) to B13b (doors shut), with B13b's push continuing B13a's. That reads as the doors swinging shut.
- **Fix:** B13a was **cut**. B13b (doors shut, Thurzó) is now a **fully static hold** at 52.933–58.033 (5.100 s), with no FX, no push and no registration. It covers "The king pressed for a trial. Thurzó prevented it." There is no door state change anywhere in the cut.
- **Door-impact SFX:** none exists. No door, impact or SFX layer is in the v3/v3b build or mix scripts; the mix is VO plus the Anabasis bed only. Nothing was added or removed.

## Mix
The v3b chain is unchanged:
- VO is at −12 LU over the bed (bed −16.6 dB), with the sidechain duck.
- L13 fix: −3.5 dB plus a 2 kHz −3 dB bell, ramped 71.498–72.498.
- "Blood Countess" ease: −3 dB, ramped 89.041–92.026.
- Bed window: track 256 → 345.23, with the crossfade unchanged.
- Bed fade: re-timed to **100.333–102.833**.
- Master: +11.4 dB, then the limiter.
- The audio stayed in scratch. No mp3 or other interim audio was made for the owner.

## Shots
- **Shortest:** h02 2.367 (locked exception), b05 2.533, b18 2.567, b01b 2.767, b15 2.800, b14 3.033. Every other shot is ≥2.5 s.
- **Order:** h01 h02 b06 b07 b04 b05 h03 b12 b01a_v1 b01b b17 **b13b** b08 b14 b16 b18 h04a b15 h04b **outro**.
- **H02 proofs** (logs_v3c) pass: face 0, outside 0, figure 0.
- **Locked items carried unchanged:** H02 v3 plate, the H04a ink copy, H01, and every other beat config.
- **Not added:** vignette, letterbox, watermark, LEGEND labels, depth_v1.

## Flags
- B13b is now 5.1 s of fully static plate. If it reads dead, a gentle push of 1.00→1.03 is the next option, but that push would scale the doors.
- SCORE-LOCK and the ledger were **not** edited for v3c.
