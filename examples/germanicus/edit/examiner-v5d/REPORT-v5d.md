# Examiner — Germanicus v5d ROUGH preview (audio-focused quick check)
File: `/workspace/posterity/renders/posterity-germanicus-v5d-ROUGH-preview.mp4` (not under standalones/…/renders).
Method: stems `_build_v5c/audio/*` + preview AAC piped to numpy; BS.1770 K-weighting; phone proxy = 300 Hz–8 kHz; masking = 1–4 kHz band; word times `_build_v5final/vo_words.json` (v5c VO lag 0.0 s). No files written except this report.

**Verdict: PASS WITH NOTES** (no revision needed; three notes for Vellum/Atelier).

## Integrity — all claims verified
- md5 `b0cede037e56e9f3ffb73a34000e09b2` ✓; duration 125.248 s (audio 125.248, video 125.233) ✓
- Audio packet md5 identical to v5c preview ✓; mix.flac − stems residual −126.8 dB (stems exact)
- Preview: −14.2 LUFS I, LRA 2.8, TP −3.7 dBTP (mix.flac −14.1 / −4.0; claim −14.1/−3.8 within AAC tolerance). Sample peak −3.67 dBFS, 0 clipped samples.

## (a) Score ("Crusade") audibility — PASS, with arc note
| Segment | gaps: score below VO | under speech | phone gaps / under | 3 s ST range |
|---|---|---|---|---|
| Mercy 0–10 | 17.2 | 18.8 | 14.3 / 15.9 | 5.95 (fade-in) |
| Rivalry 10–40 | 18.3 | 18.1 | 17.0 / 16.3 | 1.35 |
| Dread 40–51 | 18.5 | 17.6 | 17.3 / 16.1 | 1.17 |
| Son 51–60.9 | 17.5 | 17.9 | 14.9 / 16.5 | 1.95 |
| SeqC 60.9–65.6 | 17.0 | 15.4 | 13.8 / 11.6 | 1.76 |
| Accusation 65.6–88 | 13.2 | 13.9 | 9.8 / 11.1 | 2.09 |
| Reckoning 88–108 | 13.5 | 14.3 | 11.2 / 11.5 | 2.90 |
| Ending 108–120.5 | 23.6 | 21.6 | 25.3 / 23.7 | 12.78 |
| Outro 120.6–124.7 | 28.8 | 26.2 | 28.0 / 24.2 | 2.75 |

- Bed 3 s ST: body 4.5–108 s range 6.96 dB (p95–p5 5.32), median −31.4 LUFS; ~−32 to 56 s, ~−26.3…−29 over 66–108 s.
- Never inaudible in the body (worst 18.5 dB below VO; phone ≤17.3). Frames >25 dB below VO = 6.4% (phone 8.2%), all after 112 s.
- Never masks VO overall: 1–4 kHz voiced-frame margin vs score+SFX median 21.5 dB for 0–60.9 s, 16.9 dB for 65.6–108 s.
- **House-law note 1 (swell):** the rider arc lifts the bed +4.5 dB from 60.93 s and holds it to 108 s. ST shows +3.58 dB within 3 s at 63.8–67.8 s, and gap level goes from ~−32 to ~−27.5. That is a deliberate swell, not ducking (Atelier intends it for "Piso chose force"/accusation). It is >3 dB, so it is a **Vellum call**. It is also what makes the accusation build audible on a phone.
- **Note 2 (ending):** splice/tail dip −6.2 dB at 105.9–112.6 s, then −5.6 dB at 112.3–118.8 s; the bed reaches −40…−41.5 LUFS ST at 116–122 s. Under the last lines and the outro the score is 22–29 dB below VO, which is at or below the inaudibility line on a phone. It reads as an intentional quiet ending. No push is recommended in the body (Vellum ruling holds). If Vellum wants the score felt under the outro, +3–4 dB there only.

## (b) Outro VO — PASS
- small.en and medium.en: exactly "History remembers the victors. We remember the rest." (p 0.78–0.999).
- Level: integrated VO outro −13.4 vs body −14.1 (**+0.7 dB, within ±1.5**). By per-word median it is +1.6 dB (−14.75 vs −16.37), a hair over the line, so not significant. It is ~+3 dB above lines 22–23, as briefed.
- Entry: v5c/outro join at 120.47 s is smooth (−40…−47 dB) before VO onset at 120.65 s; no glitch.
- Exit: "rest." ends ~124.71 s, the tail decays to −51 dB by 125.05 s and −95 dB by 125.2 s, and the last sample is silent. Not cut off. The end taper (124.60–125.20) only touches the release.
- No masking: outro words are 17.0–40.7 dB over the score in 1–4 kHz. No clipping.
- No caption: intentional, **Vellum call only**.

## (c) War SFX — PASS on placement/audibility; intelligibility note
- SFX stem is non-zero only at 60.904–65.601 s (outside it: max −76.7 dBFS; mix residual −120 dB). ✓
- 3 s ST at 62/63/64 s: SFX −22.5/−21.1/−19.8, VO −15.4/−15.7/−15.7, score −30.3/−30.2/−30.9 LUFS. Phone band: SFX −21.5 (−18.5 in VO gaps) vs score −31.5 and VO −18.4. **Clearly audible on a phone.**
- Per-word 1–4 kHz margins reproduce Atelier exactly (vs score / vs SFX / vs score+SFX):
  - Piso 20.0/10.8/10.3; chose 23.4/12.0/11.6; force. 9.1/9.4/6.1; **His 14.4/6.4/5.77**; men 25.4/12.2/12.0; **fought 5.4/6.4/2.93**; Roman 19.5/9.6/9.1; troops. 14.6/9.5/8.3; He 19.5/8.1/7.8; lost. 14.3/9.4/8.2.
- In SeqC, 6/10 words are under the ~9 dB comfort line. Voiced frames: median 6.3–7.2 dB, 43–47% <6 dB, 26–28% <0 dB.
- **Intelligibility:** "fought" is fine full-band vs score (+17.3 dB); its low margin is all SFX. ASR on 58–68 s and 60.7–65.8 s recognises all 10 words with both models. "fought" scores medium 0.998/0.997 and small 0.977/0.979; "His" 0.97–0.996. Lowest are "Piso" (medium 0.89) and "Roman" (medium 0.89, small 0.75).
- Judgement: intelligible, but tight on a phone. **Optional** fix (not required): 2–3 dB extra SFX duck under "His" (62.45) and "fought" (63.04–63.31) only.

## Other observations
- "war." at 106.82 s ("…attempt at civil war."): 1–4 kHz band is −8.9 dB vs bed, because the word has little 1–4 kHz energy and the brass sits there. Full-band it is +15.3 dB and phone +14.0 dB, and medium.en hears it. Worth an ear check, not a fix.
- "him." at 92.38 s: phone-band margin only +1.4 dB (full-band +8.3). Ear check.
- Full-cut ASR: small.en gives 296 words vs 297 for script+outro. Its two real-looking diffs ("accused of"→"had" at ~1.8 s; "Germanicus"→"lecus" at 44.4 s, a chunk-boundary artefact) are both correct with medium.en on 0–10 s and 39.5–51 s. Remaining diffs are spelling only (judgement/judgment, Germanicus's). Effectively exact.

Disk: 138 MB free before and after. No existing files touched.
