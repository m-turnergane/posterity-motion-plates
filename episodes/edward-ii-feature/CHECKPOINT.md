# Edward II opening — checkpoint

Handoff record for the first opening sample. Written 4 Nov 2026, America/Toronto. This pass generated nothing, spent nothing, merged nothing, and did not start test two or the full film.

The first cut stays the comparison copy. Its production note is `OPENING-SAMPLE.md`. The pending second-pass brief is `OPENING-TEST-TWO.md`. Per-file sums for the recovery zip are `checkpoint/SHA256SUMS`. The shot clock is `checkpoint/timeline.json`.

## 1. What is accepted

Desk pack: VIDEO-PACK v2.1, in `inbox/VIDEO-PACK-v2/`, unchanged. Retrieval note: `PACK-RECEIPT.md`. Owner messages outrank the pack. The pilot override outranks the README. The README outranks the shot list and plate prompts. Shot intent governs a prompt. Map pack, registration, the intro brief, the score plan, and the style sample sit under those. Sources sit under those.

| Item | Locked value |
| --- | --- |
| Title | The Letter for a Buried King. Owner, 1:44 PM America/Toronto, 4 Nov 2026 |
| Script | `inbox/VIDEO-PACK-v2/sources/raw/script-vo-v3.2-LOCKED.txt`. 101 lines, 1,884 words, md5 `11f4e6f9ac7d640d006dac33533472f6`. Approved as written. Archivist countersigned. Do not edit it |
| Claim ledger | `sources/CLAIM-LEDGER-v3.2.md`, md5 prefix `8e824c98` |
| Keep out of narration | OPEN claims C02e, C11-b, C14b-b, C15, C16e-b, C17-b. C20 is disputed |
| Act I score | Anabasis I, from 0:00, no dip. This overrides the Penumbra recommendation. Credit: `'[Title]' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au` |
| Tagline | Spoken and written in the outro: "History remembers the victors. We remember the rest." The outro is outside this sample |
| Rest of the v2.1 yes/no plan | Approved as recommended at 1:44 PM |
| Wordmark | No master file was supplied. Two image-model tries were rejected. The master in the cut is the dusk-outro lettering, isolated as an alpha mask |
| Identity | Kent is Edmund, Earl of Kent. Edward II is the older half-brother. Do not relabel them as "king and advisor" |
| Maps | Engine only for routes, labels, and markers. I2V never draws them. Explorer's Chart is still a proposal. `depth_v1` stays off |
| Delivery | 1920×1080, 30 fps, stereo, −14 LUFS integrated, true peak at or under −1 dBTP, selectable captions, one brand outro on the full film |

Narration settings, from `config/narration.yaml`. Speed was not sent.

| Setting | Value |
| --- | --- |
| Voice | Oliver Silk — Deep Gravel Narrative 2, `jfIS2w2yJi0grJZPyEsk` |
| Model | `eleven_multilingual_v2` |
| Seed | 1611 |
| Format | `mp3_44100_128` |
| Endpoint | `POST /v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128` |
| stability / similarity_boost / style / use_speaker_boost | 0.5 / 0.75 / 0.0 / true |

Nine opening lines, one render each. L06 is cut in the locked file and has no take. L08 is one file, split at word 27, "even". The 70-character pipeline-test line is a separate earlier render and is not part of this film.

| Line | Request id | Characters | character-cost header | File duration s | Speech end s |
| --- | --- | --- | --- | --- | --- |
| L01 | `F6I8ZFZRZqVSf7kMUiOP` | 82 | 36 | 4.598 | 4.551 |
| L02 | `I3YBYULXjiRn9GKdNUvu` | 94 | 41 | 6.113 | 6.084 |
| L03 | `nTTJDIwMaLcaC3ANPM91` | 49 | 22 | 2.691 | 2.647 |
| L04 | `5U02QFBJyS0LuFQo2uK1` | 82 | 36 | 4.780 | 4.737 |
| L05 | `CA25htpTLkut42vnk8MP` | 87 | 38 | 4.859 | 4.830 |
| L07 | `SzZOoxSxwNysOJ2M3xQU` | 176 | 77 | 9.639 | 9.613 |
| L07a | `9R4gVzrEoa1bHFm2sahm` | 83 | 37 | 4.963 | 4.923 |
| L08 | `wcIpGqWggjKqeObdhRKp` | 197 | 87 | 11.833 | 11.796 |
| L09 | `dC6z0M5HixAhkTklhKni` | 163 | 72 | 9.691 | 9.659 |

`characters_sent` in `config/budget.yaml` is 1,083 (the 70-character test line plus 1,013 characters of opening VO). The character-cost header on these nine lines sums to 446. That header is not a credit balance. `GET /v1/user/subscription` returned 401, so `spent_credits` stays 0. MP3s are 44100 Hz mono and start near 0.025 s. The gap from one speech end to the next speech start is 0.40 s, except the 7.5 s intro between L05 and L07. The tail after L09 is 0.60 s.

Intro, as this cut actually drew it, local to SC01 (absolute start 24.449 s):

| Element | Write | Hold until | Gone by |
| --- | --- | --- | --- |
| POSTERITY wordmark | 1.15–3.15 | 4.55 | 5.65 |
| Title | 2.45–4.15 | 5.15 | 5.75 |
| ACT I | 5.15–6.25 | 7.50 | 7.51 |

Ink RGB is (48, 32, 20). ACT I is oxblood (90, 26, 24), `#5A1A18`. Title is IM Fell DW Pica at 46 px, tracking 1. ACT I is 92 px, tracking 18. Wordmark target width is 1180 px. Test two asks for a different brand passage. Those numbers describe this cut only.

## 2. What was generated

Image model on every still: `nano_banana_pro`, aspect `16:9`, resolution `2k`, count 1, `use_unlim` false. No seed was sent, and `job_status` did not return one. Output plates are 2752×1536. The account ledger names the charge "Nano Banana Pro" at −2. The job record's `job_set_type` is `nano_banana_2`. The request model and the ledger name are the ones to trust. Ten stills cost 20 credits.

Video: one clip. Model `seedance_2_5`, mode `omni_reference`, duration 6, resolution `720p`, aspect `16:9`, `generate_audio` false, `use_unlim` false. Start image role was the accepted H06 v2 job. Quoted 42 credits and charged 42. No seed was sent. Output is 1280×720, 24 fps, 6.041667 s, 529,457 bytes. The assembler scales it with `INTER_CUBIC` to 1920×1080, exactly 1.5×. It is used only on S001.

| Plate | Job id | In the cut | md5 of the local file |
| --- | --- | --- | --- |
| H06 v1 | `6aa512fa-5bf0-4396-b056-e7a8b83a4d42` | Rejected. Open letter with writing, wrong brooch | `c8aff963ec69ed0ab2c3d717d6833b13` |
| H01 | `c97894ad-0629-40d5-a2be-a39bfde6f2f9` | S003. Effigy can read as a body. A background mourner wears a crown | `a1c7ba0948f7a296217a59a09e293205` |
| N14 | `583cf114-ab6a-4675-94b9-52fa9d18b71c` | S004. Empty platform and mantle. Test two says this is the wrong image | `80dda3a50c8f88d271727c0fdde340bf` |
| DK1 | `131d5cd3-2e4e-46b4-a317-f08c292eb555` | S005. Closed blank sealed letter. Candle is partial at the left edge | `6086cd0fa1e359534b227bf4378c395a` |
| N01 | `70d469cb-49e9-4215-911d-7ee6c3ed398b` | S007, S007a, S008, S009. Extra fleurs on the robe. Hand-on-chin pose | `606d1c52bdef4d8f8b92706bfef52346` |
| N21 | `b6d67727-aec5-4ce9-ba0d-09e0b501e2c7` | S008a, the Gascony half of L08 | `e7fa742791c66ce1edc8e52fd7594fb8` |
| CB1 | `9f09e2a8-0ae5-416d-b6c2-705f47082feb` | SC01 leaf. A candle sits in the extreme left of the plate. The intro crop pushes it out | `2d7f9e01c3671c33014441a6da2e8952` |
| Wordmark v1 | `954a840b-ddf0-420a-9f7e-b3ad65a539c2` | Rejected. Nearly black, max pixel 18 | `5fb3cbc62ae86daf645a303a247ad3c3` |
| Wordmark v2 | `b76ec6f6-43f8-428a-9a88-cfb0e124153b` | Rejected. Spells POSTERITY in a boxed bold serif, not the outro face | `92e0ce63f57f1163fda4d1bc1e36165f` |
| H06 v2 | `4ddad053-9c56-4da8-a5c8-40839521644a` | Accepted still and the I2V start image. Folded blank letter, ring brooch, signet on the right forefinger | `3c840af543ce4b4e57e3ae56d76ebaa8` |
| H06 I2V | `cfb8a03b-ae91-44d8-ab8d-f954ff317be6` | Accepted for S001 only. Hand lifts, wax settles, letter stays blank | `d4f222dc6394f285e5adaa6be23af37b` |

N22 was never submitted. It has no job id, no file, and no pixels. S009 is an N01 crop with a cool grade (R×0.92, B×1.08). The approved v2.1 plan allowed that fallback. The pending brief says a grade change is not fresh coverage, and it does not automatically approve an N22 generation.

The wordmark master used in the cut is not one of the jobs above. It was isolated from the dusk outro: luma greater than 125 and red greater than blue plus 15, components larger than 40 pixels. Nine components spell POSTERITY. Counters of P, O, and R are open. Raster size 689×92. sha256 `ccd67ec31c0315ede5bce14ffaaa366d3bec7611a962514d29f75033baddfead`. The intro uses it as an ink mask, not as cream pixels.

Reference uploads used as generation inputs, not as new pictures: b20 `2e21d129-b125-4989-9946-d8d297a67ebe`, b01 `93004f7d-9a93-4f1e-b2d7-8be7ac2e1d95`, b12 `c3d470cc-d272-4c51-85c3-d4c1c4dcd6c8`, b07 `8211016d-4d92-4bd9-b9e1-15a51d811747`, b04 `e9a09c0f-f985-4e06-82ee-567c6627a082`, dusk outro `ba213dc2-0087-4533-8eda-c6ada6051d31`.

Shot clock from `tools/assemble_opening_sample.py` `build_timeline()`, re-run for this checkpoint. Times are seconds.

| Shot | Start | Stop | Plate | Crop |
| --- | --- | --- | --- | --- |
| S001 | 0.000 | 4.951 | H06-v2, the clip | Still-path zoom 1.00–1.06 is ignored. The clip is scaled to the frame |
| S002 | 4.951 | 11.435 | H06-v2 still | z 1.70–1.78, cx 0.40, cy 0.64 |
| S003 | 11.435 | 14.482 | H01 | z 1.02–1.08, cx 0.56→0.40, cy 0.48→0.46 |
| S004 | 14.482 | 19.619 | N14 | z 1.00–1.06, cx 0.58→0.60, cy 0.58 |
| S005 | 19.619 | 24.449 | DK1 | z 1.00–1.08, cx 0.55, cy 0.50 |
| SC01 | 24.449 | 31.949 | CB1 | z 1.13–1.155, cx 0.53, cy 0.50 |
| S007 | 31.949 | 41.962 | N01 | z 2.05–2.12, cx 0.84, cy 0.30 |
| S007a | 41.962 | 47.285 | N01 | z 2.15–2.20, cx 0.40, cy 0.40 |
| S008 | 47.285 | 54.901 | N01 | z 1.48–1.04, cx 0.70→0.50, cy 0.42→0.46 |
| S008a | 54.901 | 59.481 | N21 | z 1.04–1.10, cx 0.62→0.58, cy 0.42 |
| S009 | 59.481 | 69.740 | N01, cooled | z 1.42–1.50, cx 0.48, cy 0.42 |

Timeline end is 69.740 s. The encoded file is 69.733333 s, 2092 frames at 30 fps. The file duration is the one to quote. L08 splits when "even" starts: word 26 "realm" ends at 7.5 s into the file, word 27 starts at 7.616 s.

## 3. Where the bytes are

### Recovery zip, verified this session

Higgsfield media id `aa75b380-355d-436f-a9e5-447703c1aed5`. Type `file`. Size 156,284,214 bytes. sha256 `6d0708c38a6a49d4c74022941477dbd9b4d6ef8382e4e4c61517464746275986`.

A full download of this URL returned HTTP 200 and the same sha256:

`https://d2ol7oe51mr4n9.cloudfront.net/user_3Lbrwnemvw3b6zIMpp3eP4wjBUF/aa75b380-355d-436f-a9e5-447703c1aed5.zip`

The URL has no credential query. It is still a provider CDN path. It worked on 4 Nov 2026 around 3:08 PM America/Toronto. Treat a later 404 as expiry, and keep the media id. Unzip root: `edward-checkpoint-stage/`. It contains the finished film, every generated plate including the rejected ones and the I2V, the nine MP3s and their alignment JSON, captions, Anabasis I, the wordmark master, and IM Fell DW Pica plus its OFL file. `checkpoint/SHA256SUMS` lists each file.

The signed upload URL used to put the zip on that slot expired with the upload and is not recorded here.

### Drive

Checkpoint folder, private, parent is the post-1 Edward pack `1mXJMAlaffw-n0UYBfnboj5xE_ZYEMRzG`:

`https://drive.google.com/drive/folders/1q4RLzfehrHjbH48o6z06coLf1EQRWd-S`

| File | Drive id | What was verified |
| --- | --- | --- |
| `posterity-master.png` | `1OXkGrIUOOvoVtW0GEYfacmq_fEnSQEhT` | Uploaded, then `download_file` returned the same PNG. sha256 `ccd67ec31c0315ede5bce14ffaaa366d3bec7611a962514d29f75033baddfead` |
| Retrieval note | `1RPw7RqaCNGpeDXpCmOebwNopOQysR8VkHbtlo7j6a10` | Stored as a Google Doc named RETRIEVAL. The git checkpoint is the authority if the doc export differs |

`download_file` on this connector caps at 10 MB. `create_file` base64 content caps at 1,000,000 characters, about 750 KB of binary. The 65 MB film cannot be uploaded or downloaded through those two calls as one object. Files in the pack are `shared: false`. An anonymous fetch of `webContentLink` fails. A fresh agent needs the same Google Drive connection.

Image parts, each under 9 MB, same parent folder. Part 01 was downloaded this session and matched the local zip md5 `a886863b8ba063230401837915e40091`, size 6,439,468. Parts 02–10 were listed and are under the cap. They were not re-downloaded today.

| Part | Drive id | Bytes |
| --- | --- | --- |
| 01 | `1LP4JMykiQ1sH6KjBvVF5EYKDTP0DCycr` | 6439468 |
| 02 | `1VTVTICUVEUvGLwqWOWdxmsScXQp68_Qm` | 8737570 |
| 03 | `1j0OCo6RLzNT1JhkscwnnDtFIlvT6b_Ev` | 7771482 |
| 04 | `1gPiqGtp-_0MvkC7Wq7GjhvFzw5hv9DDB` | 7717562 |
| 05 | `1NIoZfaqnJF6Hwc825OlcI-xdzftvAHMI` | 7160181 |
| 06 | `14Ksf3djOLv6IHP7SICH0ufGCyUEdj0A5` | 8228173 |
| 07 | `1J8Z8vz4Rv8IkNugZW5ZHVtbh1KIUzGei` | 8890183 |
| 08 | `10_Grc8P1qneNKS-vrqALcCDhclPBFlXQ` | 8582584 |
| 09 | `1CrL8bf_h5cN3K7srgthU6xnkPjVBy8qi` | 8845892 |
| 10 | `1aWuP0BSKubtQydvBvkGTyuFIupCIovqz` | 3160681 |

The older `EDWARD-II-VIDEO-PACK-v2-MEDIA` parts are 13–25 MB. This connector cannot download them. The two coordinate files that never landed, `waypoint_coords_wikidata_2026-10-30.json` and `wikipedia_coords_2026-10-30.json`, are still only inside those oversized parts. Short plate b06 is not in this pack.

### Higgsfield CDN for the original jobs

`job_status` on the accepted H06 v2 job returned a download URL. Every generated file below was fetched again and matched the local md5. Same caveat as the zip: provider CDN, no query credentials, verified 4 Nov 2026, expiry not promised. Host `https://d8j0ntlcm91z4.cloudfront.net/user_3Lbrwnemvw3b6zIMpp3eP4wjBUF/`.

| File | Object name |
| --- | --- |
| H06 v1 | `hf_20261104_185005_6aa512fa-5bf0-4396-b056-e7a8b83a4d42.png` |
| H01 | `hf_20261104_185009_c97894ad-0629-40d5-a2be-a39bfde6f2f9.png` |
| N14 | `hf_20261104_185011_583cf114-ab6a-4675-94b9-52fa9d18b71c.png` |
| DK1 | `hf_20261104_185012_131d5cd3-2e4e-46b4-a317-f08c292eb555.png` |
| N01 | `hf_20261104_185042_70d469cb-49e9-4215-911d-7ee6c3ed398b.png` |
| N21 | `hf_20261104_185044_b6d67727-aec5-4ce9-ba0d-09e0b501e2c7.png` |
| CB1 | `hf_20261104_185046_9f09e2a8-0ae5-416d-b6c2-705f47082feb.png` |
| Wordmark v1 | `hf_20261104_185051_954a840b-ddf0-420a-9f7e-b3ad65a539c2.png` |
| Wordmark v2 | `hf_20261104_185516_b76ec6f6-43f8-428a-9a88-cfb0e124153b.png` |
| H06 v2 | `hf_20261104_185521_4ddad053-9c56-4da8-a5c8-40839521644a.png` |
| I2V | `hf_20261104_185920_cfb8a03b-ae91-44d8-ab8d-f954ff317be6.mp4` |

### Public sources

Anabasis I was downloaded again from `https://www.scottbuckley.com.au/library/wp-content/uploads/2026/09/Anabasis_I.mp3` and matched md5 `eb524bf636a1a563a33e1d257aea220a`. It is also inside the recovery zip.

Unused scores, on this VM only, not re-fetched today. Publisher links are in the licence HTML under `inbox/VIDEO-PACK-v2/score/licence_evidence/`.

| File | md5 | Publisher path |
| --- | --- | --- |
| Katabasis I | `793f064af7c20f8a12efb62ca9fd7cd7` | `.../2026/09/Katabasis_I.mp3` |
| Unraveling | `fad860bf48863a78b15b8988963c426e` | `.../2026/05/Unraveling.mp3` |
| Penumbra | `2acea4098213d02c944d57a2faa19a51` | `.../2025/07/Penumbra.mp3` |
| Memories Of Stone | `079ab0396952684311318f74da63fd57` | `.../2026/02/MemoriesOfStone.mp3` |

Tomb photos are CC0, on this VM at `var/edward-ii-feature/retrieved/T01/`, and not required to rebuild the opening. sha1 matches the pack receipt: 01 `2c7c5d23e8fcde62cabc0560774b1864fa9015e9` (5,093,908 bytes), 03 `2fece597431f1a86fbb315a1bdcd6de098db5491` (5,288,271), 04 `20f573d3180441bb8404c0ab1f5a76b8b5c16f83` (1,881,548). They are not in the recovery zip. The imageinfo JSON in git is the source note.

### Test-two reference paintings

Both were downloaded and hashed. The brief's "(1)" filenames were not separate files.

| Brief name | Drive id | Bytes | md5 |
| --- | --- | --- | --- |
| Nobleman Sealing a Letter by Candlelight.png | `1seSj9h0l9gIMCoK0AQ6KK6GwmBq5sJKi` | 1,940,176 | `c275fb6ecb608cfb5331966db88b81e1` |
| Rain-Swept Medieval Castle Execution.png | `1SbZwTzwvXEcN67LuOFfMttXg_ezmE9rT` | 2,653,328 | `bec1d228c491fdc0ae2f6f561a5affeb` |

The candlelight file is byte-identical to short plate `b20_kent_seals_letter_OWNER.png` inside image part set. The ink-on-paper inspiration images mentioned in the brief were not attached to this session and were not found by title. That is a gap. Do not generate stand-ins.

### This machine, and this agent

These paths die with the VM:

- `var/edward-ii-feature/` holds the working tree the assembler reads
- `/tmp/engine-wt/` is the engine checkout
- `/tmp/edward-img/` holds the image-part zips
- `/tmp/edward-checkpoint-stage/` and `/tmp/edward-ii-opening-checkpoint-2026-11-04.zip` are the staging copies

Mix products `build/voice.wav`, `vo-processed.wav`, `bed.wav`, `mix.wav`, and `mixed.wav` are about 13 MB each and are only on this VM. They are outputs of the mix command. The recovery zip has the MP3s and Anabasis I, which are the inputs. `build/picture.mp4` is the encode from before the caption remux and is superseded by `opening-sample.mp4`.

This cloud agent is `bc-25707c80-098e-43ea-9a13-0751a119596c`. An anonymous GET of its artifact URL returns an HTML page, not the file. That path is tied to this agent run. On this agent's disk, `/opt/cursor/artifacts/edward-checkpoint/` has the film (md5 `3ee1544ba65bc1d63d7eb51dc93fe076`), the plates, Anabasis I, and `edward-checkpoint-vo-wordmark-font.zip`. The 156 MB combined zip could not be copied onto that artifact volume. It was removed after a 0-byte copy. Use the Higgsfield zip URL above.

### Git, text only

On this branch, and small enough to keep: captions (21 cues), alignment JSON, `timeline.json`, and `SHA256SUMS`. The film, plates, MP3s, and fonts stay out of git.

## 4. How the cut was built

From the repo, with `.venv` and `ffmpeg` on `PATH`:

```bash
.venv/bin/python -u tools/assemble_opening_sample.py
```

That command does not call ElevenLabs or Higgsfield. It reads plates, voice, score, and the wordmark from `var/edward-ii-feature/`, and it opens the font at the absolute path `/tmp/engine-wt/fonts/ofl/imfelldwpica/IMFePIrm28P.ttf`. Replace that path on a new machine. The same font, the italic sibling, and `OFL.txt` are in the recovery zip and on `engine/consolidate-2026-11-04` at commit `1cf564e50e4a82460682534ef7ea59514f26c116`, path `fonts/ofl/imfelldwpica/`. Source Serif Pro is not on this machine.

What actually ran:

1. `.venv/bin/python -u tools/assemble_opening_sample.py --stills` wrote shot stills. S001 stills are the still plate, because `write_stills()` passes `video=None`.
2. The first full run failed: `var/edward-ii-feature/opening-sample/build/` did not exist. The script now creates that directory before `build_voice`.
3. The second full run succeeded. Printed levels: processed voice −19.2 LUFS, bed −31.2 after a +4.4 dB trim, so the unducked bed sat 12 LU under the voice. Two-pass loudnorm target I=-14, TP=-1.5, LRA=11, linear=true. The wav landed at −14.0 / −1.5. The mp4 measured −14.0 LUFS and −1.3 dBTP.
4. Captions were remuxed with `ffmpeg -c copy -c:s mov_text` from `build/picture.mp4` plus `captions.srt` onto `opening-sample.mp4`. 21 cues. The picture was not re-encoded for that remux.
5. `python -m pytest tests/test_motionplates.py::test_plate_never_in_repo -q` passed after the sample commit.

Encode: libx264 medium, crf 16, yuv420p, AAC 256k, 48 kHz stereo. Do not use `-shortest`. `alimiter` `level` is a boolean; the script uses `level=false`.

Mix chain inside `mix()`: voice highpass 70 Hz, +10 dB, compressor −22 dB 2.2:1 attack 6 release 140 makeup 2, then −14 dB 4:1 attack 2 release 60 knee 3. Bed starts at `atrim` plus `volume=-16dB`, then the measured trim. Sidechain threshold 0.035, ratio 2.5, attack 15, release 700, knee 4. Bus compressor −16 dB 1.6:1 attack 20 release 250, then the limiter at 0.85.

Imports the assembler actually needs: `cv2`, `numpy`, `PIL`, and the stdlib. `ffmpeg` and `ffprobe` must be on `PATH`. This VM had Python 3.12.3, ffmpeg 6.1.1, and Node v22.23.4. Node is not used by this cut.

### Defects in this cut

These are in `tools/assemble_opening_sample.py` as committed. Test two is the place to change them. This checkpoint does not.

- `sample()` takes integer crop bounds every frame and resizes with `INTER_LINEAR` (about lines 165–173). That reads as edge jitter and soft detail. N01 zooms 2.05–2.20 keep about 45–49% of the source width.
- The still path never calls house `fx_candle`, `torch_v1c`, or `smoke_v2`.
- S001 seeks the clip with `CAP_PROP_POS_MSEC` per frame and, if the read fails, silently falls back to the still.
- `write_stills()` passes `video=None`, so S001 previews are the still.
- `stroke_alpha()` reveals letter spans from left to right. `bloom_field()` keeps bloom out of the central text rectangle. The bloom RNG is `default_rng([1611, 7])`, fixed, and separate from the motion-plates `ctx.rng`.
- The font path is absolute and points at a checkout that a new VM will not have.
- `templates/build_template_v1.py --check` still looks for `guardrails.py` at the production repo root. That failure is known and was not retargeted.
- The opening sample does not use the house push formula. It uses a smoothstep center crop.

## 5. Branch, money, jobs, blockers

| Item | Value |
| --- | --- |
| Production branch | `cursor/atelier-jr-intake-596c` |
| Sample commit, before this checkpoint | `0b2f0efb96337765f3207e5a9f23a5bfd313795a` |
| Pull request | https://github.com/m-turnergane/posterity-motion-plates/pull/6 into `master`. Not merged |
| Engine branch | `engine/consolidate-2026-11-04` at `1cf564e50e4a82460682534ef7ea59514f26c116` |
| Engine pull request | https://github.com/m-turnergane/posterity-motion-plates/pull/5. Conflicts in `tests/test_motionplates.py` stay unresolved. Do not merge |
| Higgsfield plan | Plus |
| Balance | 48 credits |
| Balance read | 4 Nov 2026, 3:04 PM America/Toronto (`2026-11-04T20:04:00Z`). Same 48 as the 2:10 PM read. This checkpoint spent 0 |
| Spent on the sample | 62 = 20 for ten stills + 42 for one Seedance clip. Started from 110 |
| Outstanding jobs | None. `queued_credits` is 0. Every job above is `completed` |
| Numeric cap for test two | None. A $49 / 1,000-credit plan was being considered and is not in effect |
| ElevenLabs live balance | Unknown. Subscription endpoint returned 401 |

### Pending, not started

`OPENING-TEST-TWO.md` is the brief. Preserve this cut and write a separate `opening-sample-test-two.mp4` only after a numeric cap exists and the pass is authorized. Before any paid test-two submission, prepare one aggregate plan and ask once. Website "unlimited" does not apply to MCP. The help page checked 4 Nov 2026 is https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work. If a replacement Seedance clip is even a candidate, compare the raw 6 s 720p clip with the assembly first, then quote settings and cost. The owner is open to `gpt_image_2_5` for a future anchor. Verify the catalog id at call time. One native-resolution anchor first. Seedance 2.5 stays the video model. Do not re-synthesize the nine Oliver takes to change pictures.

Corrections waiting in that brief: locked camera on S001 unless a quoted replacement is approved; a crisp S002 insert with local flame, smoke, and candle spill; S003 without the lateral pan and without the extra crown, the effigy reading as a crafted figure; S004 restored to a pre-strike Kent-at-the-block tableau from the rain-swept reference, no impact and no new narration; S005 warmth limited to paper and desk; the brand passage rebuilt as wet black ink along the existing POSTERITY letterforms, then a separate solid-black ACT I card in cream type; S007 through S009 covered by visually distinct pictures rather than repeated enlargements of N01. Keep N21 if it still meets the Gascony beat. N22 is not an asset and is not automatically required.

### Secrets for a new session

`ELEVENLABS_API_KEY` goes in the session secret field. Never in chat, never in the repo, never on a command line. The header name is `xi-api-key`. Higgsfield is the connected MCP account on this user's Cursor account, not a key in the repo. Drive is the connected Google Drive MCP. Do not commit signed upload URLs.

### What a fresh session still needs

1. This branch, and the recovery zip (media id or the CDN URL above). Confirm the zip sha256 before using it.
2. A font path that exists. The assembler still points at `/tmp/engine-wt/...`.
3. The ElevenLabs secret, only if a new line is actually authorized. The nine takes are in the zip. Do not re-render them.
4. The Drive connection, for image parts and the two reference paintings.
5. A numeric spending cap, asked once, before any test-two generation.
6. The ink-inspiration images, if the owner still wants them. They were not found.
7. The two coordinate JSON files, only when map registration starts. They sit in Drive zips this connector cannot download.
8. Leave PR #5 unmerged. Leave the first `opening-sample.mp4` untouched.
