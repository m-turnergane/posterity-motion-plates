# Báthory v3 · SCORE-LOCK-v3.md (Atelier, 31 Oct 2026)

**Score: LOCKED by the owner.** Scott Buckley, **"Anabasis I"**, from the album *The Weight of Air* (released 25 Sep 2026).
- Track page: https://www.scottbuckley.com.au/library/anabasis-i/
- The local master is `score_audition/anabasis_i.mp3` (320 kbps, 560.8 s; I −20.4 LUFS, TP −3.1 dBTP).
- The audition is in `score_audition/SCORE-AUDITION-v3.md`. Ignosi is retired.

> **Rev 3b — FINAL for Rough v3b (16:58 EDT).** This adds to Rev 3 and supersedes it for `renders/bathory_rough_v3b.mp4`; the Rev 3 box stays valid for the v3 render. Backup: `SCORE-LOCK-v3.md.bak-1646`. Source: `build_rough_v3/mix_v3b.py`, log `build_rough_v3/logs_v3b/mix_log.json`.
>
> **VO:** `vo/vo_oliver_v3b.mp3` (98.854 s). It was retimed from the raw read (98.128 s) by `vo/retime_v3b.py`; the words are sample-identical and only 11 gaps changed. The script is the same (md5 9db405e1…). Cut length is 101.5 s: VO ends at 98.854, then a 2.65 s hold on H04b.
>
> | Cut (s) | Track (s) | Map |
> |---|---|---|
> | 0–39.75 | 256.00–295.75 | cut t → track t+256 |
> | 37.25–39.75 | A 293.25–295.75 ⨯ B 279.65–282.15 | 2.5 s qsin crossfade centred at cut 38.5, inside the flat 275–300 s stretch (chroma sim 0.598, level diff 0.54 dB) |
> | 37.25–101.5 | 279.65–343.90 | cut t → track t+242.4 (13.6 s of plateau repeats) |
>
> **Landings:**
> - Priest line at cut **78.813** lands on track **321.213**, on the swell (v3: 321.20).
> - **L13 = script line 13, "She died in confinement."** ("She" at cut 72.098). The fix is −3.5 dB extra duck plus a 2 kHz −3 dB bell on the bed, ramp **71.498–72.498**, then held.
> - "The Blood Countess" at cut **92.176** lands on track 334.576, with the −3 dB ease **89.041–92.026**.
> - Bed fade **99.0–101.5**.
>
> **Mix:** same chain as Rev 3. Bed −16.5 dB (VO −12 LU), master +11.4 dB, limiter 0.85.
> **Final:** wav −14.1 LUFS / −4.4 dBTP. mp3 `vo/mix_v3b_final.mp3` −14.1 / −4.3. Render AAC −14.1 LUFS / −4.2 dBTP, LRA 3.5 LU.
>
> **Correction to Rev 3:** Rev 3 labels L13 as "Then someone added the detail" at 69.14. In the v3 cut, 69.14 was the start of **"She died in confinement."** (script line 13), and that is where the fix sat. "Then someone added the detail" followed at about 71.1. The Rev 3 numbers are right; only the quoted label was wrong.

> **Rev 3 — FINAL for Rough v3 (16:24 EDT).** Everything in this box is final and measured. The sections below it are the pre-L11 lock, kept for the record; their times are **superseded**. Backup: `SCORE-LOCK-v3.md.bak-1624`. Source: `build_rough_v3/mix_v3.py`, log `build_rough_v3/logs/mix_log.json`.
>
> **VO:** `vo/vo_oliver_v3_final_tight.mp3` (94.85 s; the raw read is 98.13 s, 3.28 s taken out over 18 gaps). Script `raw/script-vo-v3.txt`, md5 9db405e1fe6a02f5ec12626dd541db41, 230 words. Cut length 97.5 s: VO ends at 94.85, then a 2.65 s hold on H04b.
>
> **Final window map (two segments, one crossfade):**
>
> | Cut (s) | Track (s) | Map |
> |---|---|---|
> | 0–38.25 | 256.00–294.25 | cut t → track t+256 |
> | 35.75–38.25 | A 291.75–294.25 ⨯ B 281.75–284.25 | 2.5 s qsin crossfade centred at cut 37.0 s, inside the flat 275–300 s stretch (mel-spectral corr 0.78, level diff 0.13 dB) |
> | 35.75–97.5 | 281.75–343.50 | cut t → track t+246 (10 s of plateau repeats) |
>
> **Landings (final timings):**
> - L13 "Then someone added the detail" starts at cut **69.14 s** (track 315.1).
> - Priest line "A century later, a priest wrote…to keep her beauty" runs at cut **75.20–80.6 s**, which is track **321.2–326.6**: on the swell (track 320–322 is the hottest, −14.4 to −15.4 LUFS short-term).
> - "No court ever heard her." ends at 85.38. "The Blood Countess" sits at cut **88.34 s** (track 334.3), where the bed is still about −16 short-term, so an automated **−3 dB ease** runs from 85.38 to 88.19 and the bed is down before the name. The tagline follows from 90.2 s.
> - Bed fade: 95.0–97.5 s.
>
> **Mix as built:**
> - VO: +10 dB pre-gain, highpass 70 Hz, compressor −22 dB / 2.2:1 (+2 dB makeup), then a peak compressor −14 dB / 4:1 (2 ms / 60 ms). The tight VO was recorded very low (RMS −28 dB), so the pre-gain was needed.
> - Bed: calibrated to VO −12 LU (bed gain −16.6 dB), then the house sidechain duck (0.035 / 2.5:1 / 15 ms / 700 ms / knee 4).
> - L13 fix: an extra −3.5 dB bed duck plus a 2 kHz bell at −3 dB, Q1, on the bed only. The 1 s ramp runs from cut **68.54 to 69.54 s** and the fix holds to the end.
> - Master: glue compressor −16 dB / 1.6:1, +11.4 dB, then alimiter 0.85 at 192 kHz, out at 48 kHz.
> - **Final: −14.1 LUFS integrated, −4.4 dBTP** (wav). The mp3 `vo/mix_v3_final.mp3` measures −14.1 / −4.3. The render's AAC measures −14.1 LUFS, −4.3 dBTP, LRA 3.2 LU.
>
> The credit line below is unchanged and still mandatory.

> **(Superseded by Rev 3.) Timing status: APPROXIMATE.** The landings below come from the earlier TEMP Oliver read (84.9 s, `score_audition/TEMP_vo_sentences.json`). A pre-L11 read of the locked file gave identical sentence timings. **The owner has reopened L11, so re-time everything after L11 once the revision lands** (see "After the L11 revision").

## Window

**Window: track 256.0–344.0 s (4:16–5:44), 88 s.** VO time 0 sits at track 256 s.
- The VO runs about 84.9 s.
- Then a ~3 s outro hold, with a 2.5 s bed fade at the end.

## Where the bed lands against the VO

| Cut time (s) | Track (s) | Bed (5 s short-term LUFS, un-ducked) | VO over it (TEMP timings) | Beat / movement |
|---|---|---|---|---|
| 0–8 | 256–264 | −24.6, quiet opening | L01–L02: accusation | V01–V02 · M1 |
| 9–15 | 265–271 | small lift, −19.4 / −20.7 | L03 "He sent… György Thurzó, to investigate" (11.2–15.2) | V03 · M2 opens |
| 15–54 | 271–310 | plateau, −20.6 to −23.0 (momentary max to −15.3 at 49 s) | L04–L11: intrusion, arrest, reversal | V04–V11 · M2–M3 |
| 54–59 | 310–315 | rising, −19.3 / −19.9 | L12 "She died in confinement" (55.7–58.1) → L13 starts at 58.1 | V12 → V13 |
| **64–74** | **320–330** | **THE SWELL: −15.9 / −16.7 / −16.1 (momentary peak −12.4 at ≈64 s)** | **L14 "…a priest wrote that she bathed in murdered girls' blood to keep her beauty" (62.4–69.4)** and L15 "No witness against her had described that" (69.4–72.3) | **V13–V14 · M4 payoff** |
| 79–84 | 335–340 | easing, −17.6 / −18.6 | "…the Blood Countess" (77.7–79.9), then the tagline (79.9–84.9) | V15 → Outro |
| 84–88 | 340–344 | re-rising to about −15.5 at 345 s | outro hold, under the fade | Outro |

**Reading the table.**
- The swell blooms on the **priest's claim** (L14) and holds through L15.
- It is already easing by "the Blood Countess" and the tagline.
- If the owner wants the peak *on* "the Blood Countess" instead, start the window about 8–10 s earlier, at ≈247 s. The cost is a louder opening: 255 s is −22.8, and 250 s needs checking. The current 256 s start is the recommendation.

## Mix spec (for the cut mix)

**Bed level and ducking**
- The bed sits at VO −12 LU before ducking.
- Sidechain duck, house v2: attack 15 ms, ratio 2.5, release 700 ms, knee 4. That gives about 13–14 LU of VO over the ducked bed.

**The fix, from 58 s (start of L13) to the end**, with a ~1 s ramp in at 57.4–58.4 s:
- **3–4 dB extra bed duck**, and
- **a gentle ~2 kHz dip on the bed only**: a bell at −3 dB, Q≈1.
- Why: Anabasis I is dense in the 200 Hz–4 kHz band (0.87 share, centroid 2.1–2.5 kHz in this window). Without the fix, the VO is only about 6.5 dB clear of the bed in that band at the swell, and about 2.8 dB at the worst moments.
- Let the swell open up in the VO gaps: after L15 (≈72.3 s), after "monster:" (≈77.7 s), and in the 0.8 s break before the tagline.

**Master:** −14 LUFS integrated, ≤ −1 dBTP (target −1.5).

**Provisional reference.** `score_audition/preview_full_anabasis_v3c.mp3` (88.1 s, −14.2 LUFS, −1.3 dBTP) uses exactly this spec. It shows 16.5 LU of VO over the ducked bed overall with the fix. It was mixed on the pre-L11 read before the stop order, so it is **provisional**.

## After the L11 revision

L11 currently sits at about 49.3–55.7 s. When the new L11 changes length by Δ seconds, every line after it moves by Δ, while the swell stays fixed at cut ≈64 s.
- **Preferred:** keep the 256 s start and absorb Δ inside the plateau, with a 2–3 s crossfade edit in the bed at track ≈275–300 s (the flat −21 to −23 stretch). That keeps the swell on L14.
- **Or** move the window start to 256 − Δ. That is fine for |Δ| ≤ 3 s: 253–259 s stays −22 to −25.
- Re-record Oliver from `v3/raw/script-vo-v3.txt` once it is relocked, then re-time this table and the 58 s fix point (which becomes 58 + Δ).

## Licence: CC BY 4.0, OK for monetised YouTube Shorts, TikTok and IG Reels

**Credit line for the post pack (verbatim):**

`'Anabasis I' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`

**Where to put it**
- **YouTube Shorts:** in the **description**, from the first publish. It is mandatory: Buckley's "Smart Content ID" (claimant We Are Era Music BV) "scans the description of videos using my music looking for a credit. If no credit is found, the system places a copyright claim on the video."
  - The scan looks for "Scott Buckley", "@ScottBuckley" or "musicbyscottb".
  - Claims are released via https://www.scottbuckley.com.au/library/copyright-claims-release/ (within 1 business day).
- **TikTok and IG Reels:** the full line in the caption. The track page has no platform rule for them; CC BY requires credit, and the free tier covers "Social Media".

**Source quote** (track page): "free for use in any project (including commercial) as long as I'm credited. For YouTube videos, credits must appear in the video description."

**Other notes**
- The FAQ confirms monetised YouTube is fine with the credit in the description.
- Do not upload the bare track to a music or streaming service.
- A paid licence (from AUD 40) adds YouTube whitelisting if claims become a nuisance.
