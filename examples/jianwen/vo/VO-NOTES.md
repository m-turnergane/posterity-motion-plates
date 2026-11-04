# Jianwen "The Emperor Who Walked Out of the Fire": VO notes v1 (Fri 30 Oct 2026)

**FINAL:** `vo/final-vo-oliver-jianwen-v1.wav`, md5 `6bd7b1c33777fc8ffff6be6ac9610d6a`, pcm_s16le 48 kHz mono, **92.694 s**, speech end **91.50 s** (10 ms RMS > -45 dB; the 1.19 s tail is too short for silencedetect). Loudness raw: -27.7 LUFS integrated, -6.4 dBTP (mix normalises).
Word alignment: `vo/final-vo-oliver-jianwen-v1_words.json` (md5 `32b2c98515e0018f3406c257cd091dc1`; 235 words `{word,start,end,line}`, matches the script one-to-one). Raw ElevenLabs character alignment: `vo/final-vo-oliver-jianwen-v1_alignment.json` (md5 `14fc1ef7a2c5f32d6782bc0f734db8a1`).

## Source text
`raw/script-vo-tts.txt` (md5 `3b027865e5549fad6790de43668c6f08`, 16 lines, 235 words), wording unchanged and no respellings. Sent as ONE request with Edward II's `<break time="0.8s"/>` before L16 and Edward's unspoken previous_text/next_text continuity text ("Tomorrow, we open another forgotten page of history, and we follow the people who lived it.").

## Voice and settings (same as Edward II)
ElevenLabs **Oliver** `jfIS2w2yJi0grJZPyEsk`, model `eleven_multilingual_v2`, stability 0.50, similarity_boost 0.75, style 0.00, use_speaker_boost true, default speed, `/v1/text-to-speech/{voice}/with-timestamps`, output mp3_44100_128, then decoded to 48 kHz s16 WAV. Script: `vo/render_vo_jianwen_v1.py` (md5 `6e042205d68c5901ce96145ffea0dfb1`). The API key was read from the environment and is not written anywhere.

## Takes
| take | seed | length | speech end | ASR check (faster-whisper medium.en) | verdict |
|---|---|---|---|---|---|
| **t1** | **11** | 92.69 s | 91.50 s | all 235 words present; only spelling-level diffs (Zhu Di -> "zhudi"/"Judy", reign -> "rain", rumour -> "rumor", 20 for twenty) | **CHOSEN**: complete, natural pace, clean hook, no glitches |
| t2 | 23 | 91.72 s | 90.48 s | L13 read as "and rose from bed", so "Yongle" may be swallowed; "sailed" -> "sail" | rejected |
| t3 | 37 | 93.67 s | 92.12 s | opening L01-L04 garbled in ASR ("new empire", "zh de"); 1.3 s gaps drag | rejected |

Candidate md5s: wav t2 `d2afd6d6e7efb9d0aee60ddefb51af9b`, t3 `3dc5a403332aabf609b8ab4cbc62bf13`; mp3 t1 `3f4c52cb0df1867165ee5309e8dc39f1`, t2 `0eb48eabe6ca3e84300a5f68488fb32b`, t3 `9fe1e15615669184efb02aeb6131448d`. ASR: `vo/asr_t1/2/3.json`; metrics `vo/vo_metrics_t*.json`. All kept.

t1 pauses >= 0.6 s fall only at sentence ends (longest 1.34 s after L03 "guarded the north", 1.1 s before the tagline).

## Pronunciation
- **Jianwen** (x5): consistent "Jyen-wen"; transcribed correctly every time. OK.
- **Zhu Di** (x5): "Joo-Dee", which ASR hears as "Judy" / "zhudi". Acceptable (close to Mandarin "Jōo Dee"); flag only if the owner wants a harder "Jr".
- **Yongle** (x5): "Yong-luh", correct each time in t1.
- **Nanjing**, **Ming**: correct.
- **Zhu Yunwen**: not in the script, so not spoken.
- Minor: "reign" sounds right; ASR's "rain" is a homophone.

---

# VO notes v2 (owner narration, Fri 30 Oct 2026, 11:15-11:30 ET)

**FINAL v2:** `vo/final-vo-oliver-jianwen-v2.wav`, md5 `a9eb59d4c4cc4d69d5c5ef075d988140`, pcm_s16le 48 kHz mono, **90.836 s**, speech end **89.28 s** (10 ms RMS > -45 dB; the alignment pads "rest." to the file end at 90.84). Loudness raw: -27.1 LUFS integrated, -2.9 dBTP. The peak is the stressed onset of "Uncles" at 14.22 s and decays over about 40 ms. It is not a click: the largest sample jumps sit inside normal speech. The mix normalises.
Word alignment: `vo/final-vo-oliver-jianwen-v2_words.json` (md5 `5253aaec40374caae0ceb765085fb737`; 204 words `{word,start,end,line}`, one-to-one with the script, assert-checked). Raw character alignment: `vo/final-vo-oliver-jianwen-v2_alignment.json` (md5 `274a346e55bf21ef1e813b6a1ae12576`). Byte-identical copies of take t1. The v1 files are untouched.

## Source text
`raw/script-vo-tts.txt` (md5 `851ddfb4cafb463d292861f5215a6cff`, identical to `raw/script-vo.txt` (same md5, `diff` clean), 14 lines, 204 words by wc including the 8-word tagline). Wording unchanged and no respellings. Sent as ONE request. Same recipe as v1: `<break time="0.8s"/>` before the tagline (now L14) and the same unspoken next_text continuity guard. The alignment text equals the text sent for all three takes.

## Voice and settings: identical to v1
Oliver `jfIS2w2yJi0grJZPyEsk`, `eleven_multilingual_v2`, stability 0.50, similarity_boost 0.75, style 0.00, use_speaker_boost true, default speed, `/with-timestamps`, mp3_44100_128, then decoded to 48 kHz s16 WAV. Script: `vo/render_vo_jianwen_v2.py` (md5 `b1777faaf186ab173b96800ac67c59b0`; a sed copy of v1 with the new md5 lock, 14 lines and the L14 break, and it refuses to overwrite). Words and metrics: `vo/analyze_vo_jianwen_v2.py`. The API key was read from the environment and is not written anywhere.

## Takes
| take | seed | length | speech end | tagline start | body pace | verdict |
|---|---|---|---|---|---|---|
| **t1** | **11** | 90.84 s | 89.28 s | 85.23 s | 2.32 w/s | **CHOSEN**: same seed as v1, complete, clean opening, unhurried, longest runtime (inside the target) |
| t2 | 23 | 86.61 s | 85.81 s | 82.05 s | 2.42 w/s | complete, but the quickest read; "Yongle" at L10 was heard as "Yonglei"; the cut lands near the 85 s floor (86.3 s) |
| t3 | 37 | 88.19 s | 86.74 s | 82.59 s | 2.40 w/s | complete and clean; a valid alternate (cut about 87.2 s) |

ASR checks (faster-whisper medium.en):
- Whole-file without VAD (`asr_v2_t*.json`) is **unreliable**: Whisper skipped whole 30 s windows (t2 heard only 88 words). Ignore it.
- Whole-file with VAD (`asr_v2vad_t*.json`, `asr_vad_vo_jianwen_v2.py`): t1 190/204, t2 197/204, t3 190/204 matched. The residual diffs are spelling-level (Zhu Di -> "Judy", rumours -> "rumors", Daoist -> "Taoist", twenty -> 20, Hu Ying -> "Huying"). The one exception is t1 "the Ming dynasty", which VAD trimmed.
- Per-line clips (`asr_lines_v2_t*.json`, `asr_lines_vo_jianwen_v2.py`) produce false drops on very short clips.
- Re-transcribed with context: t1 30.5-45.6 s gives every word of L05-L08, including "Then" and "Jianwen's small son vanished too". t1 0-16.5 s gives every word of L01-L02 ("...founded the Ming Dynasty..."). The t2 L10 window gives "Officially".
- Net result: **all 204 words are present in every take**. There are no dropped words, no garbled openings (L01-L02 is word-perfect in all three) and no glitches.

Candidate md5s: wav t2 `0e0995f15ca29ac6765fccffcf785e06`, t3 `1b56dccd58c59ba1f9a172da45ef7c9e`; mp3 t1 `20fdbfa55e090e0bdd71039d099d31a5`, t2 `614ace703edecdeee5c349e0c04768a5`, t3 `0d0f97d6c7d80d7939c3984c191a71eb`. Metrics are in `vo/vo_metrics_v2_t*.json`. All files are kept.

t1 pauses: 1.30 s after "armies." (L02 to L03) and after "rebelled." (L03 to L04). There are 0.92 s pauses after "night." and between "victors." and "We", 0.85 s before the tagline ("him." -> "History"), and 0.81 s after L01 "emperor.". Every pause of 0.6 s or more falls at a sentence end.
t1 line starts (s): L01 0.00, L02 5.89, L03 16.82, L04 22.79, L05 31.08, L06 33.35, L07 38.12, L08 40.79, L09 45.52, L10 49.85, L11 60.13, L12 65.53, L13 77.10, L14 85.23.

## Pronunciation (t1)
- **Zhu Di** (x5 incl. "Zhu Di's"): "Joo-Dee", as in v1. ASR hears "Judy". Acceptable, and consistent with v1.
- **Jianwen** (x8): "Jyen-wen". ASR has it right in context; isolated short clips sometimes give "Janwen"/"Yanwen's", which is clip-edge noise.
- **Yongle** (x7): "Yong-luh", correct in t1.
- **Hu Ying** (x5): "Hoo Ying". ASR writes "Hu Ying"/"Huying", which is fine.
- **Daoist**: ASR writes "Taoist", which is the same spoken word ("Dow-ist"). OK.
- **Nanjing**, **Ming**, **History of Ming**: correct.

## Estimated finished-cut runtime (v1 rule: the outro starts at the tagline, because the tagline is IN the VO and baked on the outro plate, and holds 0.5 s past speech end)
- t1: speech end 89.28 + 0.5 tail = **~89.8 s**. The outro runs 85.23 -> 89.78 = **4.55 s**, inside the 4.5-5.0 s outro rule, though shorter than v1's 4.97 s.
- To match 4.97 s, either start the outro about 0.42 s earlier, inside the 0.85 s pre-tagline pause after "him." ends at about 84.38 (84.81 -> 89.78), or hold to about 90.2 s.
- Either way the cut is **~89.8-90.2 s, inside the 85-92 s target**. Not short. No speed, pause or hold changes are needed.
- For reference: t2 would cut at about 86.3 s and t3 at about 87.2 s.
