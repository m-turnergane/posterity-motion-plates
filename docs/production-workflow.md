# Production workflow

Commands below are marked **verified here** only when this cloud session ran them. Desk commands that were not re-run are marked **desk**. Paths assume the repo root. The consolidated engine is branch `engine/consolidate-2026-11-04` (PR #5), not the tree of `cursor/atelier-jr-intake-596c`.

## Intake

1. Read [`knowledge-index.md`](knowledge-index.md), [`decisions.md`](decisions.md), and `episodes/<id>/STATUS.md`.
2. Copy a new desk pack into `episodes/<id>/inbox/` without editing it. Update STATUS with the file names and checksums.
3. Normalize a shot manifest only from files that are actually in the pack. Dry-run before any paid call.

## Engine branch (verified here, 4 Nov 2026)

```bash
md5sum path/to/engine.bundle
# expected 5e8a9c2940bb02aea54e5e9d958600c7
git bundle verify path/to/engine.bundle
git fetch path/to/engine.bundle engine/consolidate-2026-11-04:engine/consolidate-2026-11-04
git rev-parse engine/consolidate-2026-11-04
# fetched head c3a192dd240bd9c201a4eb7fa2e4abdd982be357
git push origin engine/consolidate-2026-11-04
```

Guardrails import, verified after commit `1cf564e`:

```bash
python -c "import runpy; runpy.run_path('fx/water/water_v1_1.py', run_name='x')"
python -c "import runpy; runpy.run_path('fx/dust/dust_v1.py', run_name='x')"
```

Conflict check, verified, not resolved:

```bash
git merge-tree --write-tree <ref> engine/consolidate-2026-11-04
```

Conflict file against master, PR #3, PR #4, and `cursor/engine-fixes-8e4d`: `tests/test_motionplates.py` only.

## This branch's motion-plates package (desk + repo tests)

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

`pytest -q` was run on this branch on 4 Nov 2026 after the test-two renderer: 57 passed, 1 skipped. It does not render the feature. `test_plate_never_in_repo` allows `OWNER` in filenames under `intake/` only.

## Opening test two (encoded here, 4 Nov 2026, about 5:58 PM America/Toronto)

```bash
python tools/assemble_opening_test_two.py --timeline
python tools/assemble_opening_test_two.py
python tools/assemble_opening_test_two.py --full
```

The first command prints the locked 69.740 s clock. The second writes intro and effect proofs under `var/edward-ii-feature/opening-sample-test-two/proofs/` and does not call Higgsfield or ElevenLabs. The third writes `opening-sample-test-two.mp4` once `S003.png`, `S004.png`, `S007.png`, `S007a.png`, and `S009.png` are in `var/edward-ii-feature/opening-sample-test-two/plates/`, and refuses while any of them is missing. It was run after those five files existed. The export measured −14.0 LUFS and −1.3 dBTP. Rebuilding the comparison cut takes `python tools/assemble_opening_sample.py --rebuild-first-cut` and overwrites `opening-sample.mp4`.

## House build template (desk, not verified as a feature render)

On the engine branch the template is `templates/build_template_v1.py`. It defaults to 1080×1920 and takes `--size 1920x1080`. `--check` plans and runs guardrails without rendering. Its guardrails import still points at `<repo>/guardrails.py`, which is not where this repo stores `engine/motion/guardrails.py`. On 4 Nov 2026 `--check --size 1920x1080` raised `FileNotFoundError` for that path. Do not treat the failure as a passed check, and do not retarget it without an approved commit.

Desk shape:

```bash
python templates/build_template_v1.py \
  --manifest M --timeline T --build-dir B \
  --size 1920x1080 --check
```

## Title

Chronicle Reveal v3.2b is Remotion composition `ChronicleHookV3-2b` in `titles/remotion-posterity-motion` on the engine branch. It is authored at **1080×1920**. The default plate `public` file is not in the bundle. A 16:9 feature title is still to be composed. Do not stretch the Shorts composition.

## Narration (desk settings; call only after the secret exists)

Environment name: `ELEVENLABS_API_KEY`. Do not print it. The locked spoken script is `episodes/edward-ii-feature/inbox/VIDEO-PACK-v2/sources/raw/script-vo-v3.2-LOCKED.txt`. The opening lines are already rendered. Do not render the rest until the full film is the active task. Stop and ask before about 30,000 credits on this draft.

## Higgsfield

MCP is connected. The test-two cap is spent and the hold is `owner-review`. Name `nano_banana_pro` for stills, except the opening test-two replacements named in [`model-policy.md`](model-policy.md). Do not switch to the developer API. Ask before a plan upgrade, the full film, or any spend that would exhaust the account. Balance at 6:01 PM America/Toronto was 31.5.

## Assembly checks

For any MP4, verified tools on this machine:

```bash
ffprobe -hide_banner -show_streams -show_format FILE
ffmpeg -i FILE -filter_complex ebur128 -f null -
```

Pass means 1920×1080, 30 fps, stereo, duration matches the timeline, selectable captions exist as sidecar files, integrated loudness and true peak meet `config/delivery.yaml`, and the picture was looked at. A clean encode exit is not a pass.

## Publish

There is no publish command. The owner posts.
