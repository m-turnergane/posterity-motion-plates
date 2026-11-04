# QA: Björn ROUGH v4 (Tue 2026-11-03, EST)

Authorised by the parent's 11:03 EST relay of Vellum ("carry on through the full list, in order"). All work ran on the box; the user's computer was offline and no browser was used. The only external calls were to ElevenLabs (VO).

## Deliverable
- `rough_v4/renders/bjorn_rough_v4.mp4`, md5 **1a4b5920021cdaae03876e3f69eca28c**
  - H.264 1080×1920, 30 fps, 3058 frames, **101.933 s (1:41.9)**; AAC 48 kHz stereo, 256 kb/s
- Loudness (ffmpeg ebur128): **−13.9 LUFS integrated** (target −14), **true peak −4.3 dBTP** (≤ −1), LRA 2.6 LU. PASS.
- Captions: `bjorn_rough_v4_captions.ass` (md5 1f910f05…), burned in. 49 chunks with no overlong lines. Caption text equals the VO words (asserted). The tagline is NOT captioned; nothing on screen over the OUTRO.
- Contact sheet: `bjorn_rough_v4_contact_sheet.jpg` (md5 57f89fbc…)
- Timing: `rough_v4_prep/TIMING-BOARD-v4.md` (md5 878b981f…)
- Score plan: `rough_v4_prep/SCORE-PLAN-v4.md` (md5 f858474e…)

## Inputs
| Item | Path | md5 |
|---|---|---|
| VO script (LOCKED) | raw/script-vo-v4-LOCKED.txt | ff97caaa20d2238fddc30c7bdb4a0c8a (verified) |
| VO (voiced, ElevenLabs) | rough_v4/scratch/vo_bjorn_v4.wav | 1195b04c1092455cbfb52c4fb5bdb487 |
| VO words | rough_v4/logs/vo_bjorn_v4_words.json | 1422e211f93040cc65e2d3764d4850db |
| Mix (VO + Uprising) | rough_v4/scratch/audio/mix_bjorn_v4.wav | 1efbea4908321a6950917fcaf06a8dd1 |
| Cuts | rough_v4/logs/cuts_v4.json | dc2529be79f1c706cc9ab4b0e6ba04a9 |
| Builder | rough_v4/build/build_bjorn_rough_v4.py | d112a9fe236f06d9b4ce10205389e94d |
| P05 clip | rough_v4/scratch/p05_rough/p05_test_v4b_silent.mp4 | 66fabd8fb698182253cdd35d0a5b8f87 |
| P17A clip | rough_v4_prep/p17a/p17a_glints_only.mp4 | 55a2a39a2d85d83dd249d9a9a150d0ae |
| P17B clip | rough_v4_prep/p17b/p17b_proof.mp4 | 2b1bd204801b907d41b55b4527f85c60 |

All 21 shot clips were checked: 1080×1920, 30 fps, frame counts equal to cuts_v4.json (0 mismatches).

## Proofs
- **P06** (water-only): rough_v4_prep/p06/p06_proof.mp4, md5 14c3ef3c…, 135 frames. Masks are in p06/masks/. Changed px outside water 0, in Hastein 0, in the rail 0, output-space Hastein 0. Density 1.194. PASS.
- **P11**: 126 frames (4.200 s). Face leak 0 in plate and output. Density 1.219. PASS (duration flag below).
- **P13**:
  - Hard cut at absolute frame 1699 (56.633 s), 1 frame before "armour" (56.674). The frame diff is 0.16 before the cut and 35.4 at it.
  - Mail detail z 1.300→1.305. Density **1.4995** (z end lowered from 1.31, which gave 1.5052 and failed the 1.5 guardrail).
  - Face leak: plate 0, output 0 (5 px erode). The 4 px erode shows 17/18 px at the last two samples. This is the LANCZOS footprint at 1.5× next to the candle FX (plate-space face px changed = 0).
  - Caption MarginV 860 sits above the mail in both framings.
  - See logs/proofs_P13.json. logs/proofs_P11_P13.json holds the superseded z 1.31 P13 run.
- **Intro**: house title (intro_v3b, read-only) over P03 at topPercent 31, local frames 0–172 (5.433–11.167 s), after the coffin hook. It clears Björn's face.
- **P17A**: KEEP plate, glints only, edge-slack fix. No column seam found in the f000 right-edge check: the gradient peak is 8.1 against a median of 4.1, the same as the plate texture.
- **P17B**:
  - depth_v1, 2 layers, push 1.00→1.06 about (0.40, 0.30), far push gain 0.9827. Relative parallax **1.456 px** (≤ 1.5).
  - Warp check PASS: recon PSNR 50.4 dB, single transform, dot test, uniform scale, 0 disocclusion holes, rigidity face 0.9999 and sword 1.0 in the near card. Density 1.06.
  - 226 frames. Plate md5 unchanged.
- **Type card**: rough_v4_prep/type_card/type_card_v4.png (a408d4d4…) and font_strip_v4.png (0df38e2e…). Rough uses IM Fell English SC (realms) and IM Fell DW Pica (water, italic).
- **Captions over the atlas and the armour** (directive 19): checked on final frames at 19.0, 24.0, 53.0 and 57.5 s; they are clear. P05 overlay extent ends at y 1318; caption block bottom is at y 1520.

## Flags
1. **P11 is 4.200 s**, not the owner's ~3.5–4 s. The VO line runs 44.023–47.820, and "They" at 48.220 carries the P12 cut. Shortening it needs a VO retime.
2. **P05 labels are at the tested sizes**, which may be small on a phone (directive 16). The P05 overlay extent (y 1318) is below the 1280 safe line, but no caption collides with it.
3. **Score** (see SCORE-PLAN-v4):
   - The build-up is two v2b sections joined by crossfades before the one continuous run from 54.767 s.
   - The xd6 dip is held to the end, with a −3 dB tail.
   - Line L12 opens P17A on "But".
4. **P17A**: the rough uses glints only; the new motion is awaiting approval.
5. **P17B**: the optional sky drift in the arch was not done.
6. **P13**: the detail framing keeps a 0.4 % push (z 1.300→1.305, top 345→347.5 plate px) with no vertical move to speak of.
7. **House title**: topPercent 31 reads "15 %" as +15 points. The alternative reading (16 × 1.15 = 18.4 %) is not used.
8. **Cover**: owner's choice (pending).

## Protected files (verified unchanged)
| File | md5 |
|---|---|
| rough_v2/renders/bjorn_rough_v2b.mp4 | 86e54c8e1a6defdbaa0b4d855c7cacf1 |
| rough_v2/renders/bjorn_rough_v2.mp4 | ef5e13b77522373cb6f78ed590f684b9 |
| map/p05_anim/p05_test_v1.mp4 | 261c74000a140e7d7f75bdfebba1c7a9 |
| map/p05_anim/p05_test_v2.mp4 | 08e03ef430574d289414030c5302c270 |
| plates/P05_KEEP.png | 4ef7ca5fdd0010a3f0825ae3eacb68b6 |
| rough_v3/renders/bjorn_v3_intro_proof_P01.mp4 | eeea657157852f4ed2f2233feac6441b |
| rough_v3/renders/bjorn_v3_intro_proof_v2.mp4 | 4c846879ced1beb333bc00b7ead25dcc |
| plates/P17B_dudo_open_bier.png | 891449efff6d3ca87dfca2bec6a0fe6d |
| plates/P06_KEEP.png | 1b3342b75fbe68a7fe91892bca31cdbb |
| engine-rnd/water/water_v1.py | 811734e9e3919bddbe3ef22022203d5f |
