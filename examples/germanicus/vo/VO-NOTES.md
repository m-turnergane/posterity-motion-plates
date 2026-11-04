# Germanicus "They Found His Name in the Walls": VO notes (v1)

Recorded 26 Oct 2026, ~5:35–5:45pm ET. Script: raw/script-vo-tts.txt (identical to raw/script-vo.txt, LOCKED 5:34pm ET). 11 lines, 146 words.

## FINAL
- **vo/final-vo-oliver-germanicus-v1.wav**: 48 kHz mono PCM 24-bit, 57.404 s. md5 `5af6bc59aa9cce2becb13be845560416`
- Word timings: **vo/final-vo-oliver-germanicus-v1_words.json** (146 words, display spelling, with line index). Char-level: final-vo-oliver-germanicus-v1_alignment.json
- Metrics: vo_metrics_final-v1.json. ASR check: asr_t2.json
- Source take: **t2** (seed 23). One single full-script request, so no splicing and no per-line retakes. vo_germanicus_oliver_t2.mp3 is the raw API output (md5 263ac98a564309f70e7d5bfe090ecdfd).

## Settings (copied from Croatoan ch3 v4d / Atahualpa v2a)
ElevenLabs Oliver `jfIS2w2yJi0grJZPyEsk`, `eleven_multilingual_v2`, stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true, `/with-timestamps`, mp3_44100_128, default speed (natural pace, no speed-up). `next_text` is used as anti-wind-down context. It is NOT spoken and NOT in the audio. Key from env `ELEVENLABS_API_KEY`. Post: the end is clamped at RMS > -45 dBFS, trimmed at decay < -50 dBFS, 15 ms fade, +0.25 s silence. There is no loudness normalisation or gain, which matches the earlier builds.
Scripts: render_vo_germanicus_v1.py, analyze_vo_germanicus_v1.py, asr_vo_germanicus_v1.py.

## Checks (final = t2)
- Duration 57.404 s. Speech is 0.000 to **57.164 s**. That's 2.55 words/s.
- Integrated **-26.7 LUFS**, true peak **-5.2 dBTP**
- Body L01–L09 -27.1 LUFS. L10+L11 -23.8 (**+3.3 LU**). Final line L11 alone -24.4 (**+2.7 LU**). The ending does NOT duck and is not whispered. It builds slightly louder into the twist, so there is no flag for a drop. Note it in the mix if you want it flatter.
- Pauses > 1.2 s: **none**. The longest gap is 0.60 s, after "murder?" in L01. RMS silence > 1.2 s: none.
- Word count from the alignment is **146 = 146**. There are no numerals or abbreviations.
- ASR (faster-whisper small.en): 146/146 words. The diffs are only "favourite"→"favorite" (spelling) and "curse"→"cursed" (the s+t elision in "curse tablets"). Unprompted, the names Germanicus, Tiberius, Piso, Syria and Tacitus all transcribed correctly. One unprompted full-file small.en pass heard the last line as "Piso is not one of them". Re-checks on the isolated tail with small.en and medium.en both heard "Murder is not one of them" (p=0.98), so that was a language-model hallucination. **Still worth one human listen to the last line.**
- Pronunciation respellings: **none used**. The TTS input is the display script as written. Captions use raw/script-vo.txt.

## Timing vs script-final.md
The real take runs **~6 s shorter** than the planned 63.2 s, because Oliver's natural pace here is 2.55 w/s, not 2.31. Line starts (s): L01 0.00, L02 8.15, L03 13.07, L04 20.85, L05 23.43, L06 33.45, L07 38.14, L08 40.41, L09 46.43, L10 52.71, L11 55.59. Use the words JSON for cuts and not the planned per-line times.

## Other take (kept, not used)
- t1 (seed 11): cand-vo-oliver-germanicus-t1.wav, 56.513 s, speech ends 56.253. -31.3 LUFS, -9.7 dBTP. End -0.9 LU and L11 -0.4 LU. No pauses > 1.2 s. ASR is 146/146. Not chosen: the final line is rushed (~1.1 s for "Murder is not one of them."), and it's quieter with an L06 dip (-33.7).
- cand-vo-oliver-germanicus-t2.wav is byte-identical to the final (same md5).
