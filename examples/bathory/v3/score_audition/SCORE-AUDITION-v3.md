# Báthory v3 · SCORE-AUDITION-v3.md (Atelier, 31 Oct 2026)

Ignosi (Kevin MacLeod) is **retired**. The owner's pick is **Scott Buckley, "Anabasis I"**. Everything here is an audition: no cut render, no plates generated. The samples are **TEMP**. They use a TEMP Oliver read of the **unlocked** `v3/raw/script-vo-v3-DRAFT.txt` (205 words, as of 15:30 EDT, after the Vellum rulings).

## Ranked shortlist

| Rank | Track | Licence | Bed window (track time) | Arc vs the v3 VO (cut time) | VO-clash risk | Verdict |
|---|---|---|---|---|---|---|
| **1** | **Anabasis I**, Scott Buckley (owner pick) | CC BY 4.0, with the credit in the description | **W1 4:16–5:44 (256–344 s)** | Opens −23/−25 LUFS-S, a plateau around −21, then the swell from 320 s that peaks at −15.7 (321 s) to −16 (about 320–345 s). The swell lands at **≈64–88 s**, mid-L14 ("a priest wrote…") through "the Blood Countess" and the tagline. | **HIGH.** The 200 Hz–4 kHz share is 0.87, often 0.95–0.99: dense legato string mids sit right in Oliver's band. In the sample, the VO-vs-bed mid SNR is 23 dB at the opening but **6.5 dB at the swell** (10th percentile 2.8 dB). | Best tone and best fit for the owner's arc. It needs about 3–4 dB of extra duck, or a −3 dB dip at 1–3 kHz on the bed, from about 58 s to 85 s. |
| 1-alt | Anabasis I, W2 | same | 6:40–8:08 (400–488 s) | A very quiet start (−30), building to −19 at 455–460 s (**55–60 s**), then receding under M4 | high (same timbre) | The peak arrives at "She died in confinement", and the revelation plays on a fading bed. Use W2 only if the owner wants an unresolved, deflating M4. |
| **2** | **Katabasis I**, Scott Buckley (sibling track) | CC BY 4.0, same wording | **7:04–8:32 (424–512 s)** | Opens −24/−23, a dip at 450 s (−27), builds from 465 s (**41 s**, the confessions and executions) through 495 s, and peaks at −13.6 at 500–505 s (**76–81 s**), right on "the legend had its monster: **the Blood Countess**" (74.5–79.9 s). | **LOW–MODERATE.** Low strings are the spine (low share 0.35, mid 0.45, centroid 1.4 kHz). The sample's mid SNR is 26 / 7.6 dB. Tremolo pulses (onsets about 161/min) can tick under consonants. | The most VO-friendly Buckley option, and its climax sync is the best of the set. |
| **3** | **Dark Times**, Kevin MacLeod (ISRC USUAN1100747) | CC BY 4.0, incompetech | **1:06–2:34 (66–154 s)** | Opens −27/−25, a body of −25 to −28, then the payoff at 125–145 s (**59–79 s**), which is exactly M4 ("Then someone added…" at 58.1 s). The peak of −18.6 at 140 s lands at **74 s** ("But the legend…"). | **LOWEST.** Low share 0.72, mid 0.22, centroid 1.0 kHz, almost no onsets. The sample's mid SNR is 26.5 / 13.3 dB. | Cleanest under the voice, but static and funereal. Its build is weak, and bass-heavy beds thin out on phone speakers. It is the same library as the retired Ignosi (a different track), and the owner may not want MacLeod again. |
| **4** | **Eyes In The Void**, Scott Buckley | CC BY 4.0 | 0:00–1:28 (0–88 s) | Opens −25, building steadily to −13 by 75–90 s. The 119–209 s window ends at −10, far too hot. | **HIGH (rhythmic).** The percussive ratio is 0.19 (6× Anabasis), onsets about 150/min, the march grid fights the VO cadence, and the track is mastered hot (I −14.1, TP −1.0). | Tone is wrong: the composer calls it "cosmic horror", and the brief is a mystery thriller, not the supernatural. Last. |

Considered and dropped: Buckley "Incantation" (vocal choir that would clash with the VO) and "The Long Dark" (piano, more melancholy than thriller).

**Window length.** The TEMP VO runs 84.9 s, and the tagline ends at 84.9 s. With a 2–3 s outro hold, the cut is about 87–88 s, so every window above is trimmed to 88 s. If Vellum's pauses at L09, L13 and L15 lengthen the cut, slide the window *start* earlier rather than moving the payoff.

## Measurements (full tracks; ffmpeg ebur128, librosa)

| Track | Duration | Integrated | LRA | True peak | Centroid (median) | Low <200 Hz share | Mid 200 Hz–4 kHz share | Onsets/min | Percussive ratio (HPSS) |
|---|---|---|---|---|---|---|---|---|---|
| Anabasis I | 560.8 s (9:21) | −20.4 LUFS | 10.3 LU | −3.1 dBTP | 2148 Hz (2.5–3 kHz after 320 s) | 0.058 | **0.871** | 49 (legato) | 0.033 |
| Katabasis I | 589.8 s (9:50) | −19.6 | 10.2 | −2.6 | 1409 Hz | 0.347 | 0.445 | 161 (tremolo/pulse) | 0.028 |
| Dark Times | 183.7 s (3:04) | −22.6 | 9.6 | −5.0 | 1014 Hz | 0.72 | 0.223 | ≈0 | ≈0 (silent first ≈3 s) |
| Eyes In The Void | 264.1 s (4:24) | −14.1 | 13.1 | −1.0 | — | 0.553 | — | 150 | **0.193** |

**Anabasis I in more detail.**
- Short-term peaks: 55 s at −15.1, 99 s at −17.3, 321 s at −15.7, 464 s at −18.4.
- Quietest stretch: 400–410 s at about −30.
- The 0–90 s window is rejected because it peaks at 55 s, which is too early.

The full 5 s curves and band data for each track are in `<track>_analysis.txt` and `<track>_analysis.json`.

## Licence check (quoted; all URLs re-fetched 31 Oct 2026, HTTP 200 unless noted)

### Scott Buckley: Anabasis I, Katabasis I, Eyes In The Void

**Track page.** https://www.scottbuckley.com.au/library/anabasis-i/. It was released 25 Sep 2026 on the album "The Weight of Air". The MP3 is at `…/library/wp-content/uploads/2026/09/Anabasis_I.mp3`.

> "This work is licensed under a Creative Commons Attribution 4.0 International License; meaning it's free for use in any project (including commercial) as long as I'm credited. For YouTube videos, credits must appear in the video description. If you don't, you will likely get a copyright claim from me."

**Attribution strings**, verbatim from each track page:
- `'Anabasis I' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`
- `'Katabasis I' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au` (https://www.scottbuckley.com.au/library/katabasis-i/)
- `'Eyes In The Void' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au` (https://www.scottbuckley.com.au/library/eyes-in-the-void/)

**FAQ.** https://www.scottbuckley.com.au/library/faq/
> "Can I use your music for free in videos released on my monetised YouTube channel? Yes – as long as you credit me… (at least stating my name 'Scott Buckley) in the description below the video."

**Licensing.** https://www.scottbuckley.com.au/library/licensing/
- The free CC-BY tier covers "Online Multimedia – YouTube, Vimeo & Social Media, Website Background Music, Animation, Film etc."
- Paid tiers (AUD 40, 75 or 300) add "(incl. YouTube whitelisting)".
- Restrictions:
  > "This music cannot be resold in isolation – any resale must have the music synchronised with other media."
  > "Music cannot be redistributed through music distribution services (e.g. DistroKid, Artist.io, CDBaby), or submitted in any way to streaming services (e.g. Spotify) or online stores (e.g. iTunes)."

**Content ID.** https://www.scottbuckley.com.au/library/copyright-claims-release/
> "I have implemented a 'Smart Content ID' system … This system scans the description of videos using my music looking for a credit. If no credit is found, the system places a copyright claim on the video."

- Claimant: "We Are Era Music BV, claimed on behalf of Scott Buckley".
- The system looks for "Scott Buckley", "@ScottBuckley" or "musicbyscottb" in the description.
- There is a release form for claims ("within 1 business day").
- Sentric Music Publishing claims are false and are handled through the same form, via his publisher, Frequency Music.

**Verdict for Anabasis I: OK** for monetised YouTube Shorts, TikTok and IG Reels under CC BY 4.0. "free for use in any project (including commercial) as long as I'm credited", and the free tier explicitly includes "Social Media".
- **YouTube:** the credit is mandatory *in the description*, and it should be there from the first publish. Otherwise the Smart Content ID claims the Short, and that claim can be released.
- **TikTok and IG:** his pages give no platform-specific rule. By inference from CC BY, put the full attribution string in the caption, with a pinned comment as backup.
- Don't upload the bare track to any music service.
- A paid licence (from AUD 40) buys whitelisting if claims become a nuisance.
- The same verdict applies to Katabasis I and Eyes In The Void.

### Kevin MacLeod: Dark Times

**Sources.**
- Track page: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100747 (200, but the page is rendered by JS).
- MP3: https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Times.mp3 (206 OK). The ID3 tags read title "Dark Times", artist "Kevin MacLeod".
- filmmusic.io: https://incompetech.filmmusic.io/song/3611-dark-times/ (**503 on re-check**; it had loaded earlier).
- The composer's description: "Deeply troubling and somber… heavy on the bass strings… funereal".

**FAQ.** https://incompetech.com/music/royalty-free/faq.html
> "for YouTube videos? Yes, AND you can monetize the videos. Be sure to credit me."

**Credit line:**
`Dark Times Kevin MacLeod (incompetech.com) / Licensed under Creative Commons: By Attribution 4.0 / https://creativecommons.org/licenses/by/4.0/`

**Content ID.** https://incompetech.com/music/royalty-free/youtube-contentid.html
- The music is pre-registered, so a missing credit means a claim.
- Fix it by adding the credit and disputing; the claim is released within about 72 h.

**Verdict:** OK for monetised use on all three platforms, with the credit in the description or caption.

## VO-clash risks and mix notes (for whoever mixes the cut)

- **Anabasis I:**
  - Its mid density matches Oliver's formant band. At the 320 s swell, the bed comes within about 3–7 dB of the VO in 200 Hz–4 kHz.
  - Plan: a ducking automation of about −3 to −4 dB extra from 58 s to 85 s, and/or a gentle −3 dB bell at 2 kHz (Q≈1) on the bed during VO only.
  - Let the swell bloom in the gaps: after L15 at about 72.3 s, after "monster:" at about 77.7 s, and in the 0.8 s break before the tagline.
- **Katabasis I:** the tremolo low strings are safe in level but can pulse against plosives. Keep the duck release at 700 ms or longer so the bed doesn't pump.
- **Dark Times:** no clash. The risk is the opposite: under −25 LUFS-S with almost no mids, it vanishes on phones. Allow +2 dB over the other beds, or a low-mid lift.
- **Eyes In The Void:** percussive hits and glitches cut through any duck. It would need heavy automation and still fights the cadence.

## TEMP samples (audio only; not a cut)

All four samples are in `v3/score_audition/`:

| Sample | Window used | Integrated | True peak | VO over ducked bed | Mid SNR, opening / payoff |
|---|---|---|---|---|---|
| `sample_anabasis_i.mp3` | 256 s | −14.1 LUFS | −1.8 dBTP | 13.9 LU | 23.4 / 6.5 dB |
| `sample_katabasis_i.mp3` | 424 s | −14.1 | −1.2 | 14.8 | 26.2 / 7.6 |
| `sample_dark_times.mp3` | 66 s | −14.2 | −1.3 | 14.7 | 26.5 / 13.3 |
| `sample_eyes_in_the_void.mp3` | 0 s | −14.2 | −1.3 | 13.9 | 28.9 / 10.3 |

**What each sample contains.** Each is 29.2 s, 128 kbps, 44.1 kHz, about 470 KB, and has TEMP in its ID3 title and comment.
- **Part A, the opening:** VO 0.0–15.4 s (L01–L03) over bed window +0.0–15.4 s.
- **0.8 s crossfade.**
- **Part B, the build and payoff (the M4 turn):** VO 57.9–72.5 s (L13–L15) over bed window +57.9–72.5 s, i.e. the exact bed the cut would have under those lines.

**Mix chain**, identical for all four beds, with no EQ:
- The bed is set pre-duck at VO −12 LU.
- Sidechain duck as in v2: attack 15 ms, ratio 2.5, release 700 ms, knee 4.
- Master: a 3:1 bus compressor, gain to −14 LUFS, and a 4×-oversampled limiter.
- Verified by ebur128. Numbers are in `samples_TEMP_measurements.json`.

**TEMP VO.**
- File: `TEMP_vo_oliver_v3_scriptorDRAFT.mp3` (84.9 s, 207 words). The script is `render_tempvo_v3_scriptor_DRAFT.py`.
- House Oliver settings: voice jfIS2w2yJi0grJZPyEsk, eleven_multilingual_v2, stability 0.5, similarity 0.75, style 0, speaker boost on, seed 1611.
- Sentence timings are in `TEMP_vo_sentences.json`.
- Re-render once the VO locks.
- Superseded: `tempvo_oliver_v3_owner_AUDITION.mp3`, which read the owner text.

Scripts: `analyze.py`, `mix_samples.py`.
