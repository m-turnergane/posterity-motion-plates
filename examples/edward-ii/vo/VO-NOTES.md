# Edward II v3b — VO notes (ROUGH v1, 2026-10-29)

**Voice:** Oliver (ElevenLabs voice `jfIS2w2yJi0grJZPyEsk`), model `eleven_multilingual_v2`.
**Settings (Germanicus house):** stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true, default speed.
Endpoint `/with-timestamps`, `mp3_44100_128`. The whole script went in **one request per take**, with an SSML break before L17 and `next_text` used as an unspoken guard against the voice winding down.
**Script:** `raw/script-vo-v3-DRAFT.txt` (md5 b30ce609e7ae1b62216e124ace1bdc94), 222 words.
**Generator:** `vo/render_vo_edward_ii_v3b.py`. Analysis is in `vo/analyze_vo_edward_ii_v3b.py` and `vo/asr_vo_edward_ii_v3b.py` (faster-whisper medium.en).

## Takes (3 of max 3)
| take | seed | dur s | body w/s | I LUFS | TP dBTP | ASR vs script |
|---|---|---|---|---|---|---|
| **t1 (CHOSEN)** | 11 | 88.79 | 2.58 | -29.1 | -4.1 | 222/224 tokens; the only diff is "the second" being written as "ii" (normalisation, not a misread) |
| t2 | 23 | 83.41 | 2.78 | -25.6 | -2.6 | same as t1, plus "seventy" written as "70" (normalisation) |
| t3 | 37 | 83.50 | 2.74 | -26.4 | -3.7 | same as t2, plus **"in" dropped** (real misread) |

**Why t1:** it has the cleanest ASR and the most measured documentary pacing (2.58 w/s, with about 0.8 s sentence gaps). The ending is not rushed. t2 and t3 are about 7% faster and feel hurried for a slow, unresolved close.
t1 note: the speech energy ends at about 88.05 s (silencedetect -45 dB). The alignment stretches "rest." to the file end at 88.79.

## Files and md5
| file | md5 |
|---|---|
| final-vo-oliver-edward-ii-v3b.wav (identical to cand t1) | 30e67dbdce08242d7e8a03e89cbff23d |
| final-vo-oliver-edward-ii-v3b_words.json | acce2b6e4065cdbd2e342195b41a40f0 |
| final-vo-oliver-edward-ii-v3b_alignment.json | aacaaab6f1382ddd5d401c23692d2248 |
| cand-vo-oliver-edward-ii-t2.wav | 137c1d8f372f916d992f1a7a8507e4c8 |
| cand-vo-oliver-edward-ii-t3.wav | 91634a9aa43845ec34004cc531522f2f |
| vo_edward_ii_oliver_t1.mp3 | 110a0206bcc7f0a3f65a804f6866fbd2 |
| vo_edward_ii_oliver_t2.mp3 | 94986a06665686045fb5007012bb7b94 |
| vo_edward_ii_oliver_t3.mp3 | 1805bb99e33d1fe589ebd79e1b8cee71 |
