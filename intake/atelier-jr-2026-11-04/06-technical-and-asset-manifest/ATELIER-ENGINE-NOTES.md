# ATELIER ENGINE NOTES: Posterity animation and render engine (handoff to Atelier Jr)

## FIRST TASK: push the engine

The owner chose this route on 2026-11-04: Atelier Jr pushes the engine from the bundle in its own cloud environment. Nothing was pushed from the box. Push to the existing **private** repo only. Don't create a repo, change visibility, force-push, or push directly to master.

1. Get `engine.bundle` from this folder (md5 `5e8a9c2940bb02aea54e5e9d958600c7`) and verify it:
   ```bash
   md5sum engine.bundle
   git clone https://github.com/m-turnergane/posterity-motion-plates.git && cd posterity-motion-plates
   git bundle verify /path/to/engine.bundle
   ```
2. Fetch the branch and push it:
   ```bash
   git fetch /path/to/engine.bundle engine/consolidate-2026-11-04:engine/consolidate-2026-11-04
   git rev-parse engine/consolidate-2026-11-04   # expect c3a192dd240bd9c201a4eb7fa2e4abdd982be357
   git push origin engine/consolidate-2026-11-04
   ```
3. Open a PR from `engine/consolidate-2026-11-04` into `master` titled "Engine consolidation 2026-11-04". The branch is based on local `feature/cartography-v0.2` @ `4198b86` and has never been merged with the remote.
4. Report merge conflicts. In this order, check the branch against `master` (426f4b7), PR #3 torch_v1c (84f07f7), PR #4 water_v1 (3d7f809) and `cursor/engine-fixes-8e4d` (69fef53), for example with `git merge-tree --write-tree origin/master engine/consolidate-2026-11-04`, and the same for each ref. List each conflicting file per ref. Don't resolve conflicts without approval. Local-only commits `23f17bf`, `bad0503` and `4198b86` are also new to the remote; note this in the PR.
5. Apply the guardrails path fix as a separate commit on the branch: "fix(fx): point water_v1_1 and dust_v1 at engine/motion/guardrails.py". In the repo layout, guardrails lives at `engine/motion/guardrails.py`, but both modules still load it from the old box layout (`<repo>/motion/guardrails.py`):
   - `fx/water/water_v1_1.py` line 18
   - `fx/dust/dust_v1.py` line 36

   On both lines:
   ```python
   # before
   G = _load("guardrails", HERE.parent.parent / "motion" / "guardrails.py")
   # after
   G = _load("guardrails", HERE.parent.parent / "engine" / "motion" / "guardrails.py")
   ```
   Verify with `python3 -c "import runpy; runpy.run_path('fx/water/water_v1_1.py', run_name='x')"`, or with an import-only check that the module loads and finds guardrails.
6. Report back: the PR URL, the final head SHA, and the conflict list per ref (or "clean").


Written 2026-11-04, about 10:50 ET (America/Toronto, UTC-5), by the consolidation run.

Every fact here comes from files on the box. Anything that could not be recovered from files is marked **UNKNOWN**.

This document contains no secrets. The only credential the engine uses is the environment variable `ELEVENLABS_API_KEY`, and its value is not recorded anywhere here.

## 1. Repository

| | |
|---|---|
| Repo | https://github.com/m-turnergane/posterity-motion-plates (existing repo; visibility unchanged) |
| Local checkout | `/workspace/posterity-motion-plates` (remote `origin` added; nothing fetched or pushed) |
| Branch | `engine/consolidate-2026-11-04` |
| Commit | `c3a192dd240bd9c201a4eb7fa2e4abdd982be357` |
| Base | local `feature/cartography-v0.2` @ `4198b86` (newest local history) |
| Push status | **NOT PUSHED.** The box has no push credential: gh is not logged in, and there is no credential helper, SSH key or GitHub token env. |
| Bundle | `06-technical-and-asset-manifest/engine.bundle`, md5 `5e8a9c2940bb02aea54e5e9d958600c7`, 6,444,170 bytes. `git bundle verify` passes, the history is complete, and the single head is `refs/heads/engine/consolidate-2026-11-04`. |

### Getting the branch into GitHub
To push from a machine that has credentials:

```
git clone https://github.com/m-turnergane/posterity-motion-plates.git && cd posterity-motion-plates
git fetch /path/to/engine.bundle engine/consolidate-2026-11-04:engine/consolidate-2026-11-04
git push origin engine/consolidate-2026-11-04      # new branch only; never main/master, never --force
```

### Merge caveat: remote state was read, not fetched

| Ref | Commit | Notes |
|---|---|---|
| remote `master` | `426f4b7` | Includes PR #2 (smoke v2, fx_candle) as packaged code under `src/motionplates` |
| PR #3, open | `84f07f7` | torch v1c |
| PR #4, open | `3d7f809` | water v1 + guardrails |
| branch `cursor/engine-fixes-8e4d` | `69fef53` | No PR |
| local `master` | `b7269f9` | |

- Local commits `23f17bf`, `bad0503` and `4198b86` are not on the remote.
- This branch has **not** been merged with remote master or the PR branches. Conflicts are therefore **UNKNOWN**.
- To keep conflicts small, the consolidation adds only new top-level directories (`engine/ fx/ cartography/ titles/ templates/ examples/ fonts/ audio/`) plus `CONSOLIDATION.md`, `CONSOLIDATION-MANIFEST.json` and `BACKLOG-POC.md`. The root README and .gitignore are untouched.
- Expect duplicated logic between `fx/` and the remote `src/motionplates` package. The rule is that the locked md5s in section 6 win.

### Repo layout (this branch)

| Repo path | From (`/workspace/posterity/...`) |
|---|---|
| `engine/motion/` | `motion/`: guardrails.py, PRESETS.md, locked presets (`presets/locked/*.json` + frozen engine `animate_b3_cb9e2b88.py`), animate/qc tools |
| `engine/ledger/` | `ledger/MOTION-SYSTEM.md`, `ledger/STANDING-LAW-*.md` |
| `templates/` | `motion/templates/` (build_template_v1.py, README_build_template.md, tests) |
| `fx/<name>/` | `engine-rnd/{smoke,flames,water,dust,snow,depth,documents,hero}`, plus `fx/torch_v1c/fx_v1c.py` from `standalones/edward-ii/edit/fx_v1c.py` |
| `cartography/maps`, `cartography/research` | `engine-rnd/maps/` (no style/), `cartography/*.py, *.md` |
| `titles/remotion-posterity-motion/` | `motion/posterity-motion/` (no node_modules, public/fonts or public/plates) |
| `examples/bjorn/` | `standalones/bjorn/{map, raw/geo, rough_v1–v3/build, rough_v4, rough_v4_prep}` (code, md, json, ass only) |
| `examples/{edward-ii,jianwen,germanicus,bathory}/` | the edit and VO scripts for those shows |
| `fonts/ofl/` | `standalones/bjorn/rough_v4_prep/p05/fonts/` (each font has its OFL.txt) |
| `audio/` | `music-sources-2026-10-16.md` and README pointers |

Full copy list: `CONSOLIDATION-MANIFEST.json`, with every src→dst entry and every skip.

**Run-location caveat (verified):**
- The copied build scripts use absolute paths (`/workspace/posterity/...`, `/workspace/mpvenv/bin/python`).
- `fx/water/water_v1_1.py` and `fx/dust/dust_v1.py` resolve `../../motion/guardrails.py` relative to themselves, so they fail when run from the repo.
- Until the code is repathed (see BACKLOG-POC.md), **run engines from their originals under `/workspace/posterity`**.

## 2. Environment and dependencies (read from the box, 2026-11-04)

| Item | Version |
|---|---|
| Python (venv `/workspace/mpvenv`) | 3.13.5 |
| numpy | 2.5.4 |
| opencv-python-headless (cv2) | 5.0.0.93 (cv2 reports 5.0.0) |
| pillow | 12.3.0 |
| scipy | 1.18.1 |
| shapely | 2.2.0 |
| pyshp | 3.1.6 |
| onnxruntime (depth_v1 DA2 Small) | 1.31.1 |
| fonttools | 4.65.0 |
| scikit-learn | 1.9.1 |
| soundfile | 0.14.0 |
| librosa | 1.0.0 |
| torch | 2.14.1+cpu |
| requests (ElevenLabs calls) | 2.34.2 |
| pytest | 9.1.1 |
| ffmpeg / ffprobe | 7.1.5-0+deb13u1, with libass (`ass`/`subtitles`), `loudnorm`, `ebur128`, `sidechaincompress`, `alimiter` |
| node / npm | v24.22.1 / 11.21.1 |
| Remotion (package.json) | remotion, @remotion/cli, fonts, google-fonts and tailwind-v4 all 4.0.529; react / react-dom 19.2.3; typescript 5.9.3; tailwindcss 4.0.0 |

- `node_modules` is **not installed** in `motion/posterity-motion`. A package-lock.json is present.
- pyproj is not installed. Projections are hand-coded: `map/lcc.py`, plus the LAEA formulas in `make_refpack_p05.py`.

### Install

```
python3 -m venv /workspace/mpvenv     # already exists on the box
/workspace/mpvenv/bin/pip install numpy opencv-python-headless pillow scipy shapely pyshp onnxruntime fonttools scikit-learn soundfile requests pytest
cd titles/remotion-posterity-motion && npm ci
```

The pip line was NOT re-run; the box already had these packages. `npm ci` was NOT run because it needs network access and writes node_modules.

## 3. Commands, as verified on 2026-11-04 (read-only checks only; nothing was rendered)

Set `P=/workspace/mpvenv/bin/python`.

| Command | Result |
|---|---|
| `$P -c "import numpy,cv2,PIL,scipy,shapely,onnxruntime"` | OK |
| `$P templates/build_template_v1.py --help` (repo) | OK: shows usage (`--manifest --timeline --build-dir [--size 1080x1920] [--check] [--clips-only] ...`) |
| `cd motion/templates && $P -m pytest -q tests` (original) | **26 passed** in 44.9 s |
| `$P examples/bjorn/rough_v4/build/p05_rough_v4d.py --help` (repo) | OK: shows usage (`--slot --offset --pause-after --pause --variants --force --frames`) |
| `$P engine-rnd/smoke/smoke_v2.py --help` (original) | OK: `--plate/--config/--reel --out [--seconds --fps --preview --no-push --proof --grab --jobs]` |
| guardrails import + `check_pixel_density((941,1672),(1080,1920),(1.0,1.06))` | OK: ratio 1.217, pass |
| fx_v1c import by path (`importlib`) | OK: `PlateFX` present |
| `intro_v3b.py` import | OK: TITLE and CR dict load (file default topPercent 16; the Björn v4 build overrides it to 31) |
| `water_v1_1.py`, `dust_v1.py`, `snow_v1b.py`, `depth_v1.py` with no subcommand (originals) | The module and its imports load. Each then exits on the missing subcommand (`IndexError` at `a[0]`); these CLIs have **no --help**. |
| same four, run from the repo copy | water/dust **fail** at the relative guardrails load (see caveat above) |
| `build_bjorn_rough_v4b.py <bad>` | Loads, then raises `KeyError` on the unknown subcommand (dispatch verified) |
| `mix_bjorn_v4d.py` | Parses (ast). Not executed, because it writes output. |
| `guardrails.py --help` | **Not a help flag**: the CLI treats argv[1] as a config path. |

### Engine CLIs (from their READMEs; not executed beyond the checks above)

```
$P engine-rnd/water/water_v1_1.py overlay|proof|render --size 540x960|stats|reel  <config>    # never overwrites (-n)
$P engine-rnd/dust/dust_v1.py     grab|proof|stats|render|reel <config> [--size WxH]
$P engine-rnd/snow/snow_v1b.py    render b11 out.mp4 [--size 540x960]   # also presets/proof/stats/overlay/reel/sheet
$P engine-rnd/depth/depth_v1.py   layers|proof|stats|render|reel <config>
$P engine-rnd/smoke/smoke_v2.py   --config <cfg.json> --out <out.mp4> [--proof]
$P motion/guardrails.py <config.json> [--warn-only]        # refuses by default
$P motion/templates/build_template_v1.py --manifest M --timeline T --build-dir B [--check]   # --check = plan + guardrails only
```

### Björn v4 build (worked example; scripts in `standalones/bjorn/rough_v4/build/`)

```
$P build_bjorn_rough_v4b.py faces | still <P> <t> | clip <SHOT> | proofs | captions | final | sheet
$P p05_rough_v4d.py --variants b --offset 0.376667 --pause 0     # P05 atlas clip, writes rough_v4/scratch/p05_rough/
$P mix_bjorn_v4d.py                                              # 48 kHz mix, see section 9
$P ../vo/render_vo_bjorn_v4.py                                   # ElevenLabs; needs ELEVENLABS_API_KEY in env
```

- The v4d final = the v4b builder + `p05_rough_v4d.py` (P05D_PISA label at 866,822) + `scratch/clips_v4d/P05.mp4` + `concat_v4d.txt` + `mix_bjorn_v4d.py`.
- The exact command order for v4d is recorded in `QA_rough_v4d.md` and `logs/`. Where those do not spell it out, it is **UNKNOWN**.

### Encoding (Björn v4)
- Clips: libx264 crf 14, 1080x1920, 30 fps.
- Final: libx264 `-preset slow -crf 16 -pix_fmt yuv420p`, ASS burned in, AAC 256k at 48000 Hz, `+faststart`.
- ffmpeg always runs with `-n`: it never overwrites.

## 4. Fonts

| Font | Path | License | In git? |
|---|---|---|---|
| Source Serif Pro Regular/Semibold/Bold (title; Semibold 78 px) | `/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/`; also `motion/posterity-motion/public/fonts/` | SIL OFL 1.1, per the font's embedded name table (ID 13/14, v3.001). No OFL.txt on disk. | No: documented only |
| IM Fell English SC (P05 realm labels) | `/usr/share/fonts/truetype/sand-box/google/IM Fell English SC/IMFellEnglishSC-Regular.ttf` | SIL OFL 1.1 (embedded name table). POST-PACK-CREDITS also says Google Fonts OFL. No OFL.txt on disk. | No |
| IM Fell French Canon Regular/Italic | `/usr/share/fonts/truetype/sand-box/google/IM Fell French Canon/` | SIL OFL 1.1 (embedded name table) | No |
| IM Fell DW Pica (IMFePIrm28P / IMFePIit28P; water labels, italic) | `standalones/bjorn/rough_v4_prep/p05/fonts/imfelldwpica/` | OFL 1.1, with OFL.txt | **Yes**, `fonts/ofl/` |
| EagleLake-Regular, MedievalSharp, UncialAntiqua-Regular | `.../rough_v4_prep/p05/fonts/` | OFL 1.1, with OFL.txt | **Yes**, `fonts/ofl/` |
| DejaVu Sans (captions, bold) | `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` (v2.37) | Bitstream Vera license + public-domain DejaVu changes (`/usr/share/doc/fonts-dejavu-core/copyright`) | No (system font) |

## 5. Map layer and registration pipeline (worked example: Björn P05 atlas)

Files:
- `standalones/bjorn/map/` (repo copy: `examples/bjorn/map/`)
- `rough_v4/build/p05_rough_v4d.py`
- `rough_v4_prep/p05/P05-SHIP-TIMING.md`

### 1. Reference pack and LAEA registration
`map/refpack_p05/make_refpack_p05.py` is deterministic and refuses to overwrite without `--force`.

- **Projection:** proj4 `+proj=laea +lat_0=40.7 +lon_0=3.0 +x_0=0 +y_0=0 +R=6371000 +units=m +no_defs` (spherical, north up).
- **Frame:** out 1080x1920 at 2.09259 km/px; plate 2160x3840. `x = X/2092.59 + 540`, `y = 960 − Y/2092.59`.
- **Corner lon/lat:**

  | Corner | lon | lat |
  |---|---|---|
  | TL | −16.011 | 57.622 |
  | TR | 22.011 | 57.622 |
  | BL | −7.843 | 21.982 |
  | BR | 13.843 | 21.982 |

- **Sources:**
  - Natural Earth (`engine-rnd/maps/sources/naturalearth`): coast and rivers
  - OHM (CC0) c. 860 realm polygons, checked against Shepherd 1911/1923
  - place coordinates verbatim from `map-reference-data.md`
  - No AI imagery.
- **Zones:**
  - title_safe [54,96,1026,1824]
  - pin_safe [64,96,1015,1824]
  - push-adjusted title-safe in source px [81.5,144.9,998.5,1775.1]
  - caption line: nothing at or below out y 1280 after the push, which is source y 1261.9
  - compass reserved [89,576,279,766]
- **Outputs:**
  - `img/bjorn_p05_9x16_ref_clean.png`: image-model input
  - `_annotated.png`
  - `_zones_overlay.png`
  - `_realm_ids.png`
  - `route_places_p05.json`
  - `PLATE-PROMPT_p05.md`
- The older `map/make_p05_reference.py` uses LCC(37, 46, 41.25, 2.25) from `map/lcc.py`. That file is superseded for P05 by the LAEA refpack.

### 2. Realm masks
- Each OHM realm polygon is rasterised to a realm-id image (0 = sea/no data).
- Where realms overlap, the smaller realm wins. Balearics are removed from both claimants.
- Coastal snap: unassigned land within 3 out px of both sea and a realm is assigned to the nearest realm, to absorb NE/OHM coastline mismatch.
- Borders are drawn where the realm id changes on land.
- Tints are LAND·0.55 + pigment·0.45.
- Land with no c. 860 realm gets a hatch.
- The `realm_ids` raster is used for registration QA. The tints themselves are painted into the plate.

### 3. Plate registration
`map/p05_anim/p05_build_v2.py` writes `p05_transform_v2.json`.

- The plate `standalones/bjorn/plates/P05_KEEP.png` (941x1672, md5 `4ef7ca5fdd0010a3f0825ae3eacb68b6`) is fitted to the reference by **automatic coastline ICP**.
  - The ref coast is the boundary of the refpack's clean sea colour (every 3rd px). The plate coast is the boundary of its sea segmentation.
  - A 24 px border and the compass zone (+20 px) are excluded.
  - Trimmed nearest-neighbour ICP, LMedS fit; the trim radius anneals from 12 to 4 px over 30 iterations.
- Similarity and affine fits are both computed; **similarity was chosen** (uniform scale + rotation + shift, no TPS).
  - scale 1.14833, rotation −0.0116°
  - residuals: median 1.32 px, p95 5.79 px
- Output: `P05_KEEP_registered_1080x1920.png`.
- Pixel density at push 1.06 is 1.217, which passes the ≤1.5 rule.

### 4. Sea mask and route
- The sea mask comes from colour segmentation. A distance-transform push keeps the route line off land.
- Route ink is house oxblood `#701A14` (112,26,20) with a parchment keyline.
- Leg styles:
  - documented legs: solid
  - other legs: dotted (1, 10)
  - legendary tail toward Rome: dashed (10, 6.5), broken and lighter
- A nameless fleet marker (sails only) rides the line.
- There is no Luna label or mark.

### 5. Word-locked ship solver (`p05_rough_v4d.py`)
- Leg onsets are locked to the VO word times of "Spain", "France", "Italy" and "Mediterranean" (`vo_bjorn_v4b_words.json`).
- Speed profile:
  - seg0: power ramp
  - seg1: cruise with a cosine ramp-down
  - seg2: cosine ramps, RAMP2 0.22
- **Calm peak ≤ 240 frame px/s.** P05-SHIP-TIMING.md recommends ≤240 px/s, minimum ≤320; easing 50 % linear + 50 % cosine, so peak = 1.285 × average.
- Holds 0.5 s. Slot 10.5 s (9.3 s minimum).
- Run: `--variants b --offset 0.376667 --pause 0`.

### 6. Sword icons (battle marks)
- Camargue: on "France"
- Valence: +0.25 s
- Pisa: on "Italy"
- None in Spain, nothing at Luna.

### 7. Label placement
Realm labels use IM Fell English SC. The sizes recorded in the build are:

| Label | Size |
|---|---|
| WEST FRANCIA | 38 |
| PROVENCE | 33 |
| EMIRATE OF CÓRDOBA | 38 |
| KINGDOM OF ITALY | 36 |

- Labels are tracked, split over two lines, and placed by an obstacle/clearance search.
- Each label records a status (CONFIRMED / interpretation) and a source line in `ARCHIVIST-v4-CHECK.md`.
- Water labels use IM Fell DW Pica Italic.
- The v4d Pisa label is at (866,822). The build asserts clearance ≥4 px from the ship and ≥3 px from the sword.
- QA flagged that the labels may read small on a phone.

### 8. Route styles across shows
`engine/motion` locks `house-map-inknib-dashed-v1`:
- width 7.2 px, dash [24,11]
- wet ink [62,10,6] drying to [142,46,26]
- nib bead .85, bloom .55, sheen .4, wobble 1.2 px @ 5 Hz
- markers with bloom

Recipe-driven cartography (Chronicle Atlas P0/P1, PoC C) is in `cartography/` and the local branch `dev/poc-c-cartography`. **Not production-locked.**

## 6. House motion rules and locked FX presets

Source of truth: `motion/PRESETS.md` (repo: `engine/motion/PRESETS.md`) and `ledger/STANDING-LAW-longform.md` §7.

### Camera
- **Push 1.00→1.06**: scale-only, centred, zero jitter.
  - Björn CAM default: push (1.0, 1.06), travel 0.02, ease ramp 0.5/0.5, v_end 0.35.
  - The older StablePush spec was 100→104 %.
  - The Björn OUTRO uses 1.0→1.03.

### Guardrails (`motion/guardrails.py`, refuse by default)
- **Pixel density:** refuse more than **1.5 output px per real source px**. The ratio is cover-fit × peak push × crop zoom, measured on the actual plate file.
  - 941x1672 → 1080x1920 @1.06 = 1.217 (pass)
  - 941x1672 → 1920x1080 = 2.04 (refuse)
  - Long-form at 1.06 needs ≥1357x763 (house target 2560x1440).
- **Crop/zoom:** never zoom more than ~1.5× native fill.
- **Fire sharpness:** torch and fire FX only on sharp native fire. Laplacian variance ≥100, zoom ≤1.5.
- **The one waiver:** `p05v2_sun_glitter_v1d`, 1.6, warn-only, exact name + plate md5 + output. Add no new waivers.

### Locked presets

| Preset | Source and lock | Rules |
|---|---|---|
| **torch_v1c** (LOCKED 2026-10-30) | `standalones/edward-ii/edit/fx_v1c.py`, md5 `f31394f82a890b94d7670b009e984ce8`. Import by path; never edit. | Painted flame shape holds (tongue 0, no warp). Pulse-only halo σ=clip(0.9h,20,120). Spill reach ~330–570 px, spill_amp 1.8. Flicker amps ×1.5, freqs .55/1.3/2.6/4.4 Hz. Whole-frame 1 s swing 10–14 %, near-torch 20–45 %. 0 px displacement anywhere. Render before the camera push. Reference: `renders/posterity-edward-ii-v3b-ROUGH-v1c.mp4` (md5 b4f0aa7a…). |
| **fx_candle** (`house-candle-lightspill-v1`, APPROVED-DEFAULT 2026-10-22) | `motion/presets/locked/house-candle-lightspill-v1.json` (md5 `0591d4c770c5363f1ca6135a5d961d17`). Frozen engine `animate_b3_cb9e2b88.py` (`cb9e2b880ab7b6940043ce3723de590a`). | Candles only. flame_warp inside the flame mask (sway 3 px) is the only displacement. Light spill r 800, amp 1.35. Face/paper swing ±20–30 %, ≤5 %/frame. Pair with subtle smoke_v2 wisps. torch_v1c does NOT apply to candles. |
| **smoke_v2** | `engine-rnd/smoke/smoke_v2.py`, md5 `80bb28695757f7568b005e8ba8327bde`, verified on the box and asserted by build_template_v1. | Procedural FFT plumes; the plate never moves. Bit-exact outside the emitter footprints. Stacked with torch_v1c + depth_v1, set alpha ×0.4. When stacked, its own camera is never called. |
| **dust_v1** (LOCKED 2026-10-30) | `engine-rnd/dust/dust_v1.py`, current md5 `c0ad4ef55357ddd47ca73b9a93ffc760` (size-density fix; renders byte-identical to the lock `9ea7ab68…`) | Shaft motes or ground sheets, matte-only, nothing displaces. Protect 0 px. Whole-frame swing <8 %. |
| **snow_v1b** | `engine-rnd/snow/snow_v1b.py`: snow_v1 numbers turned up (R&D 2026-10-31, made for Báthory). Its README says R&D, and no owner LOCK line was found, so **lock status UNKNOWN**. | Matte-only screen-space flakes in three tiers (far/mid/near). Keep-outs (faces via YuNet, subjects, braziers) are 0 px changed. |
| **water_v1** (LOCKED 2026-10-30) | `engine-rnd/water/water_v1.py`, md5 `811734e9e3919bddbe3ef22022203d5f`. Guarded entry `water_v1_1.py` (`0afcfc06…`). | The sea never displaces. **Glints** are fixed sites from a high-pass (σ4, thresh 10, min_dist 8, sigma 2.0, star .55/len 9, add .7, twinkle .35–.9 / .9–2.2 Hz) that twinkle in place. Slow breathe amp .06–.07. Fire reflections driven by `fx_v1c.flick()`. KNOWN BAD: the K11 crop. |
| **depth_v1** (LOCKED 2026-10-30, **opt-in, OFF by default**) | `engine-rnd/depth/depth_v1.py`, md5 `dd5cd5011c88b3b56528b96fedae5494`. Model `engine-rnd/depth/models/da2_small.onnx` (Apache-2.0, ~99 MB, not in git). | Two rigid layers, one transform per layer per frame. Folds in the 1.00→1.06 push; there is no global push. Use only on motion/action plates, never on back-to-back character plates. Faces, hands and letters stay inside one layer. In `build_template_v1.py`, set `"depth": "<cfg>"` per shot. |
| Stacking depth_v1 + torch_v1c + smoke_v2 (LOCKED 2026-10-30) | `engine-rnd/hero/fullstack_v1.py`. Reference `hero/final/b10_corfe_fullstack_v1_restrained.mp4` (md5 3ae1ae4d…). | depth is the only camera. Torch delta is zeroed on faces. |
| Map ink | `house-map-inknib-dashed-v1` | See section 5.8. |

Other standing rules:
- No "ILLUSTRATIVE RECONSTRUCTION" text anywhere (owner, 2026-10-27).
- flames_v1–v3b are R&D only.
- Any shot that falls back to a lesser treatment is flagged by shot ID in QA.

## 7. Title intro (Chronicle Reveal v3.2b) and outro

**Spec:** `ledger/MOTION-SYSTEM.md`, "STANDING LOCK 2026-09-27": composition `ChronicleHookV3-2b`.
- Oxblood PaintedArchivalStrike.
- Stroke-gated scale + opacity + Y letter-manifest, then an authored reverse-manifest exit.
- About 4 s at 30 fps.
- Banned: pointer, shake, flat band, typewriter.

**Remotion source:** `titles/remotion-posterity-motion/src/Root.tsx`, compositions `ChronicleHookV3-2b`, `-ext` and `-ext-cahokia`.
- Render command: `npx remotion render src/index.ts ChronicleHookV3-2b out.mp4`, after `npm ci`. **NOT VERIFIED**: node_modules is absent and was not installed. The entry file `src/index.ts` exists.

**Python port used in Shorts builds:**
- `standalones/bjorn/rough_v3/build/intro_v3b.py` execs the v3.2b code span verbatim from `standalones/jianwen/edit/build_final_jianwen_v2.py` (lines 197–214 and 225–329). That code originated in Germanicus v5b.

**Björn v4 parameters:**

| Parameter | Value |
|---|---|
| Plate / placement | Over P03, after the coffin hook (P01–P02) |
| Local frames | 0–172 (5.433–11.167 s) |
| TITLE | "THE KING WHO SACKED\nTHE WRONG ROME" |
| Font | Source Serif Pro Semibold 78 px, tracking 0.02 em |
| Colour | (243,237,224) |
| Strike | fill #5A1A18, edge #3A0E0C, mid #6E2A1C |
| Layout | topPercent **31** (owner "move title down 15%", 16→31), offsetX −16, bandHeight 14 %, width 94 % |
| Strike enter | 8–26 |
| Manifest | 14–42 |
| Hold | 42–142 |
| Exit | 142–162 |
| Clear | 151–172 |
| Opacity / scale | peakOpacity .92, scale .92→1.0, exitScaleTo .94, letterSettleFrames 12 |
| Anchor | f174 |

Báthory v3c has no title intro.

**Outro (Björn):**
- The OUTRO plate stays flat with push 1.0→1.03 (centre 0.5, 0.3).
- A protected text rect (40,60,900,420) holds the tagline "History remembers the victors. We remember the rest.", which is painted into the sky and narrated, after `<break time="0.8s"/>`.
- No caption is shown over the OUTRO.
- A brand card or end-slate standard across shows is **UNKNOWN** (not found in files).

## 8. Subtitles and captions (Björn v4, "Bathory v3 style")

Captions are an ASS file burned in by ffmpeg libass. Example: `rough_v4/bjorn_rough_v4b_captions.ass`.

**Style:**
- PlayRes 1080x1920
- DejaVu Sans 54, bold, white, black outline 4, shadow 2
- Alignment 2 (bottom centre), MarginV 400
- Per-shot MarginV overrides (`logs/margins_v4*.json`): P07 615, P13 860

**Chunking:**
- Words come from the ElevenLabs alignment (`vo_*_words.json`).
- A new chunk starts on a line change, a cut, or ending punctuation.
- At most 7 words per chunk, in 2 lines of ≤24 characters each.

**Timing:**
- Start = the first word's start.
- End = the last word's end + 0.25 s, clamped to the next chunk's start.
- The build asserts that caption text equals the VO words.
- Nothing is shown over the OUTRO, and the tagline is not captioned.
- Captions must clear the caption-safe band (out y ≥1280 is caption territory on maps).

## 9. Audio chain

### ElevenLabs VO (`standalones/bjorn/rough_v4/vo/render_vo_bjorn_v4.py`)

| Setting | Value |
|---|---|
| Endpoint | text-to-speech with-timestamps (character alignment) |
| Key | env `ELEVENLABS_API_KEY`, sent as the `xi-api-key` header. All 22 VO scripts read it from env. |
| Voice | "Oliver Silk — Deep Gravel Narrative 2", voice_id `jfIS2w2yJi0grJZPyEsk` |
| Model | `eleven_multilingual_v2` |
| voice_settings | stability 0.5, similarity_boost 0.75, style 0.0, use_speaker_boost true |
| Seed | 1611 |
| Output | `mp3_44100_128` |
| Speed | **Not set in the request.** The effective API default value is **UNKNOWN** from files. Any pacing change is done afterwards by silence retiming. |
| Script gate | `raw/script-vo-v4-LOCKED.txt`, md5 `ff97caaa20d2238fddc30c7bdb4a0c8a` (asserted) |
| Pronunciation method | Plain script spelling (for example "Björn"). There is **no pronunciation dictionary and no SSML phoneme tags**. The only SSML is `<break time="0.8s"/>` before the tagline. The reference guide in `script-final.md` (Björn BYURN, Ironside EYE-ern-side, Ragnar Lothbrok RAG-nar LOTH-brok, Hastein HAH-stain, Luna LOO-nah) is for review only. |

### Retime (`retime_vo_v4.py`, 48 kHz)
- Only silences are edited: comma ≤0.22 s, sentence ≤0.40 s, line ≤0.45 s.
- The P05 slot is 10.5 s.
- v4b adds 0.5 s of room tone after "barred.".

### Mix (`mix_bjorn_v4d.py`, 48 000 Hz)
1. **VO:** `highpass 70` → `volume +10dB` → `acompressor -22dB/2.2:1/6/140/makeup 2` → `acompressor -14dB/4:1/2/60/knee 3`
2. **Score bed:** one continuous run from offset 60.0 s, with a 1.5 s sine fade-in and a 1 s cosine end fade. Gain is calibrated so the bed sits 12 LU under the VO (bed −21.3 dB).
3. **Ducking:** `sidechaincompress threshold 0.035 ratio 2.5 attack 15 release 700 knee 4`, keyed by the VO.
4. `amix` → bus `acompressor -16dB/1.6/20/250` → master gain → `alimiter limit 0.85` at 192 kHz oversampling → s16 stereo at 48 kHz.

**Targets:**
- Mix WAV −13.9 LUFS, TP ≤ −1.1.
- Final **−14 LUFS ±0.5, ≤ −1 dBTP**.
- Measured v4d final: I −14.0 LUFS, TP −4.2 dBTP, LRA 2.6, AAC 256k, 48 kHz.

### Score provenance
- Track: "Uprising" by Scott Buckley, CC BY 4.0.
- File: `standalones/bjorn/rough_v1/score_preview/source/Uprising.mp3` (8,229,845 bytes, md5 prefix 3218446a). Track page: https://www.scottbuckley.com.au/library/uprising/
- **Required credit, verbatim:** `'Uprising' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au`. It goes in the YouTube description and the TikTok/IG captions (`rough_v4/POST-PACK-CREDITS.md`).
- Other music sources: `audio/music-sources-2026-10-16.md`.

## 10. Known limitations
- **Not pushed.** The branch exists only locally and in the bundle, and has not been reconciled with remote master or PRs #3/#4 (section 1).
- **Paths:**
  - Copied scripts are verbatim, with absolute `/workspace/posterity` paths.
  - water_v1_1 and dust_v1 cannot run from the repo layout.
  - Repathing and packaging are in BACKLOG-POC.md.
- **CLIs:** most engine CLIs have no `--help`, and `guardrails.py` treats argv[1] as a config path.
- **Remotion:** node_modules is not installed, so the Remotion render is unverified on this run.
- **Fonts:** Source Serif Pro and the IM Fell English SC / French Canon fonts are OFL per their metadata, but they have no OFL.txt on disk. They are not committed; install them from upstream with their license files.
- **Björn P05:** labels may read small on a phone (QA). The registration p95 residual is 5.79 px.
- **depth_v1:** revealed strips read slightly smeared (hf ratio .49–.86), and the move lands about 1–2 s late on a phone because of the ease. 16:9 refuses 941x1672 plates.
- **Status UNKNOWN:** snow_v1b lock status, and the ElevenLabs default speed.
- **Assets not in git:** `engine-rnd/maps/sources/ohm.json` (2.25 MB) and all media are excluded. `engine-rnd/diag` and `standalones/bathory/vo` did not exist at copy time.

## 11. Large assets (not in git; sizes from `du -sh` / `ls`, 2026-11-04)

| Path (`/workspace/posterity/...`) | Size |
|---|---|
| whole tree | 54G |
| `standalones/bjorn` | 1.9G |
| `standalones/bjorn/rough_v4` | 1.3G (renders 459M, scratch 740M) |
| `standalones/bjorn/rough_v4/renders/bjorn_rough_v4d.mp4` (latest) | 120,521,939 B, md5 a6635ca499b8d3086c52496c812ba004, 1080x1920, 30 fps, 3073 frames, 102.433 s |
| `standalones/bjorn/rough_v4/renders/bjorn_rough_v4.mp4` / `v4b` / `v4c` | 119.5 MB / 120.2 MB / 120.6 MB |
| `standalones/bjorn/rough_v4/scratch/audio/*.wav` (mix + stems) | ~19.6 MB each |
| `standalones/bjorn/rough_v4/vo/vo_oliver_bjorn_v4.mp3` | 1,654,325 B |
| `standalones/bjorn/rough_v4_prep` | 146M |
| `standalones/bjorn/plates` (P01–P20 + OUTRO `_KEEP.png`, 2–3.9 MB each) | 72M |
| `standalones/bjorn/map` | 50M |
| `standalones/bjorn/rough_v1` (incl. score) | 121M |
| `engine-rnd` | 1.1G (smoke 131M, flames/scratch 165M, depth/models 95M, water 78M, dust 62M, maps/sources 41M, hero 25M, snow 24M) |
| `motion/presets` | 42M |
| `motion/posterity-motion/public` | 25M |
| `standalones/germanicus` | 4.2G |
| `standalones/jianwen` | 1.6G |
| `standalones/bathory` | 742M |
| `standalones/edward-ii` | 102M |

The per-file manifest of all plates, outros and renders is the sibling `ASSET-MANIFEST-all-plates-outros-renders.csv`, written by another handoff task.

## 12. UNKNOWN list
1. Conflicts and merge result between this branch and remote `master` (426f4b7), PR #3, PR #4 and `cursor/engine-fixes-8e4d`: the remote could not be fetched.
2. The effective ElevenLabs `speed` value (not set in the request).
3. snow_v1b owner lock status.
4. The exact command sequence for the v4d final, beyond the scripts named and `QA_rough_v4d.md`.
5. Whether the Remotion render command works on this box (npm deps not installed).
6. A cross-show brand card / end-slate standard for outros.
