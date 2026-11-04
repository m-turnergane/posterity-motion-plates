# Examiner — Germanicus v5b ROUGH, audio-only re-check (Tue 27 Oct 2026, ET)
Scripts: a1–a4.py, asr5.py; data: a1–a4.json, a2.out, asr_*.json; ear clip: ear_v5b_30-41s.wav (master 30–41 s, 16-bit).

## Integrity
- md5 9e696b000fdf183607613e38f6e22573: matches. Video packets: v5 and v5b both have MD5 1ccca41f0a4007fbe9222d431e9cbca3, so the video is IDENTICAL.
- Loudness: I -13.9 LUFS, LRA 2.9, TP -3.7 dBTP (same as v5).
- vo_staged null: bit-exact. Post-limiter VO stem: no global gain change, residual -47.6 dB.
  - The differences are inside 31–40 s only (limiter interaction): -0.27 dB max at 36.45 s, and ≤0.01 dB elsewhere.
- SFX stem: same shape (residual after gain -72.8 dB), -0.09 dB global, still only at 60.907–65.599 s.
- Bed outside 31–40 s: within ±0.69 dB of v5 (median -0.09).
- Master 112 s–end: null -35.2 dB rel. Last-line levels match v5: L22 -16.6, L23 -15.5, pause 0.545 s.
- ASR (small.en and medium.en): 289/289. Only diff is judgement/judgment.

## FIX-1 (dip at 29.5–38.8 s): RESOLVED
| | v5 | v5b | Atelier claim |
|---|---|---|---|
| 3 s ST range in window | 5.35 | 1.02 | 5.35→1.02 ✓ |
| mono 1 s min (below median) | -38.92 (6.79) | -33.47 (1.27) | -33.22 (1.04): close; my hop is 0.1 s |
| whole-cut 3 s ST range | 6.41 | 2.96 | 2.96 ✓ |
| mono 1 s range, 3–111.4 s | 10.87 | 7.90 | 7.36 (Atelier window and hop) |
- Events >2 dB within 3 s: only 44.5–49.6 s (+2.40). This was already in v5 and is the cue's own swell. The 12.3–15.6 s event is gone.
- Pumping: none.
  - Onset mean -0.39, absmax 3.36.
  - Offset mean -0.25, absmax 3.62.
  - Random |Δ| mean 1.23, p95 3.05.

## Repetition: NONE
- The splice source is cue 62.2–68.1 s. Xcorr places it at cue 62.7 s for package 33.0 s (r 1.00).
- The bed uses cue 120–244 s, so the source lies outside the rest of the bed.
- Bed xcorr of 32.5–38.4 s against the rest of the cut: max r 0.287 (at 97.8 s); the 99.9th percentile is 0.157.
- 1.5 s chunks: peaks of 0.45–0.56 all fall inside the splice itself (the cue's own internal figure). No match anywhere else.

## Splice edges
- Entry 32.2–32.8 s is a real harmony change. Chroma:
  - before: A# .62, A .17, B .17
  - during the crossfade: A# .40, B .29, A .13
  - after: B .31, F .22, D# .12
  - Adjacent-window cosine 0.31; v5 at the same spot was 0.97. Bed-wide p5 is 0.75. The only comparable change elsewhere is the cue's own change at about 14 s (0.08–0.31).
  - So for about 0.6 s, A#/B (a semitone) overlap. This is a possible mild rub. It sits under VO ("following of"), with the bed about 15–20 dB below the voice.
- Click: none.
  - High-frequency 5 ms jump: 4.6 at entry, 6.3 at exit. Bed-wide p99 is 4.2, p99.9 6.2, max 9.5.
  - The sample-diff peak near each edge is 0.67× (entry) and 0.37× (exit) of the bed-wide p99.99. No discontinuity.
- Level: smooth, no bump. Bed 400 ms: 32.0 -31.7, 32.5 -31.5, 33.0 -31.0, 34.0 -30.8, 35.0 -29.7.
- Exit at about 38.4 s: clean. Cosine 0.865 (B held). The level follows v5's own rise (38.5 s: -29.3 vs -27.5; 39.0 s: -28.1 vs -27.7).
- Beat/phrase continuity: not measured beyond level, HF and chroma. Judge it by ear using the clip.

## Margins
- Words inside the splice lose 2–5 dB because the hole is now filled. "of" 32.81: house 16.18 (v5 19.92), stereo-max 11.89 (v5 14.95). Atelier claimed 11.89 ✓.
- House <12 dB: a 32.26 (10.49), at 106.28 (11.31). Same as v5.
- Stereo-max <12 dB: 13 words (v5: 12; added "of" 32.81 at 11.89).
- Stereo-max <9 dB: of 18.49 (8.25), a 32.26 (8.14), in 100.09 (8.57), at 106.28 (8.32). Same as v5, all outside the splice.
- 1–4 kHz masking:
  - house: median 44.1, <6 dB 0.31%
  - stereo-max bed+SFX: median 40.3, <6 dB 1.01%, <0 dB 0.47% (v5: 44.3 / 0.31; 40.4 / 1.01 / 0.47)

## Verdict: PASS (FIX-1 closed)
Advisory, non-blocking: a quick ear check of ear_v5b_30-41s.wav at 32.2–32.8 s for the A#→B semitone overlap during the crossfade. If it rubs, a shorter crossfade (≤0.3 s) or a splice point about 0.5 s later at a cue chord boundary would remove it.
