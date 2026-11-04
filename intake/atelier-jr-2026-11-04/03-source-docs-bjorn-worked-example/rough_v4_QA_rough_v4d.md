# QA — Björn rough v4d (short, per SPEED update)

**File:** `renders/bjorn_rough_v4d.mp4`, md5 `a6635ca499b8d3086c52496c812ba004`. Built from v4c (md5 `24bb62acc5a217eca01dcd515912873f`, unchanged).

## Sanity checks
| Check | Result |
|---|---|
| Full decode (`ffmpeg -v error -f null`) | 0 errors |
| Video | h264, 3073 frames, 102.433 s, 30 fps |
| Audio | AAC 256k 48 kHz, 4803 packets, 102.433 s, start 0, 0 pts gaps; quietest 50 ms window after 0.3 s = −52.1 dBFS at 62.95 s (breakdown, not silence) |
| Loudness (ebur128 on the final AAC) | I −14.0 LUFS, TP −4.2 dBTP, LRA 2.6 LU |
| framemd5 vs v4c | 3073 vs 3073; changed frames 623–777 only (all inside P05 463–777; the 463–622 re-encode decodes bit-identical) |
| Keyframes | unchanged from v4c: 0 82 163 347 463 713 778 … 2938 |

## Audio (owner override)
- One continuous Uprising run from track offset **60.0 s** (= v4c seg1 start; same start point and 1.5 s fade-in), to 162.4 s at the end; cosine fade over the last 1 s. No splices, crossfades or automation; v4c duck chain (sidechaincompress 0.035/2.5/15/700/4), bus comp and limiter unchanged.
- Bed calibrated 12 LU under VO as before → bed gain −21.3 dB (v4c −19.1), because the continuous run is louder on average.
- VO margins (rendered stems, worst words): 1–4 kHz "aboard." 3.9 dB; house "But" 7.6; phone "But" 7.3. All ≥3 dB. (Full sweep skipped.)
- Around 'leapt' (60.767): the track is at 120.77 s, the end of its climax; the music decays into the breakdown under P14/P15 (timeline ~61.0–66.8) and the track's hit lands at timeline ~67.0, 0.8 s before the P16 cut.

### Ducked bed RMS per shot (dBFS, at mix level)
| Shot | v4c | v4d |
|---|---|---|
| P08 | −31.4 | −33.6 |
| P09 | −31.2 | −33.4 |
| P10 | −31.6 | −33.8 |
| P11 | −39.6 | −33.5 |
| P12 | −41.4 | −32.8 |
| P13 | −39.7 | −32.4 |
| P14 | −26.7 | −40.7 |
| OUTRO | −35.1 | −29.2 |

P11–P13 are now ≥ P08–P10 and rising. Everything before P11 is ~2.2 dB lower than v4c (calibration). P14 is the quiet one now (breakdown).

## Picture (P05 Pisa)
- Label centre (864,800) → (866,822) ref px: below-right of the dot instead of right. Literal west is under the held ship; north hits the sword.
- Min ink gap (arrival−3 → end): ship 6.3 → 22.3, sword 9.0 → 26.2. Clear of route, other labels and frame edge.
- Crops: `qa_v4d/p05_pisa_f760_v4c_vs_v4d.png`, `qa_v4d/p05_v4d_f760_phone390.png`.

Build: `build/mix_bjorn_v4d.py`, `build/p05_rough_v4d.py` (P05D_PISA default 866,822), `scratch/clips_v4d/P05.mp4`, `scratch/concat_v4d.txt`.
