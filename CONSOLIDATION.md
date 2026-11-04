# Engine consolidation (2026-11-04)

This branch copies the Posterity animation and render engine from the production working tree (`/workspace/posterity` on the agent box) into this repo. The **originals were left in place, unchanged**. Only source, docs, configs and small JSON were copied. Renders, plates, stems, scratch and raw source data were left out, and no file is over 1 MB.

| Repo path | Copied from (`/workspace/posterity/...`) | What |
|---|---|---|
| `engine/motion/` | `motion/` (PRESETS.md, guardrails.py, presets/locked, iterations-2026-10-22, rnd-2026-10-23-naturalfire tools, _skills) | House motion rules, locked presets, guardrails, battle-map/animate engines |
| `engine/ledger/` | `ledger/MOTION-SYSTEM.md`, `ledger/STANDING-LAW-retention-motion-score.md` | Standing motion and score law |
| `templates/` | `motion/templates/` | build_template_v1 (portrait Short template) and its tests |
| `fx/` | `engine-rnd/{smoke,flames,water,dust,snow,depth,documents,hero}`, plus `standalones/edward-ii/edit/fx_v1c.py` → `fx/torch_v1c/` | FX engines (smoke_v2, flames, water_v1/v1_1, dust_v1, snow_v1b, depth_v1, doc reveal, torch/candle fx_v1c) |
| `cartography/maps/` | `engine-rnd/maps/` (minus `sources/`, `style/`, `cache/`, `final/`) | Map route/modes engines, realms, Chronicle Atlas P0/P1, reference packs and registration |
| `cartography/research/` | `cartography/*.py, *.md` | haversine helper and geography notes |
| `titles/remotion-posterity-motion/` | `motion/posterity-motion/` (minus `public/plates`, `public/fonts`) | Remotion project: StablePush and Chronicle Title Reveal compositions |
| `fonts/ofl/` | `standalones/bjorn/rough_v4_prep/p05/fonts/` | OFL 1.1 map-label fonts, with their OFL.txt |
| `examples/bjorn/` | `standalones/bjorn/{map, raw/geo, rough_v1..v3/build, rough_v4, rough_v4_prep}` | The Björn Ironside v4 build: worked example (P05 atlas, captions, mix, VO) |
| `examples/{edward-ii,jianwen,germanicus,bathory}/` | the matching `standalones/<name>/{edit,vo,v2,v3}` | Earlier episode builds. The Chronicle Reveal title code is in `examples/jianwen/edit/build_final_jianwen_v2.py`. |
| `audio/` | `music-sources-2026-10-16.md` + README | Pointers to the VO and mix code |

Notes
- Build scripts still use absolute paths (`/workspace/posterity/...`, `/workspace/mpvenv/bin/python`). They were copied verbatim and **not** re-pathed, so they reproduce the box layout exactly.
- `src/motionplates/` on remote `master` and on the open PR branches already has packaged versions of smoke_v2, fx_candle, fx_torch (PR #3), fx_water and guardrails (PR #4). The copies here are the production originals. Merge with remote `master` before you de-duplicate them.
- The copy manifest (source → destination for every file) is in `CONSOLIDATION-MANIFEST.json`.

## Running the copies (verified 2026-11-04)
- Engines that locate siblings relative to their own folder fail when run from this repo's layout, because they expect the box tree. `fx/water/water_v1_1.py` and `fx/dust/dust_v1.py` load `HERE.parent.parent / "motion" / "guardrails.py"`, which is `engine-rnd/../motion` on the box. For now, run them from their originals under `/workspace/posterity/engine-rnd/...`. Repathing them belongs to the PoC/packaging backlog (see BACKLOG-POC.md).
- The scripts that work in place from the repo are:
  - `templates/build_template_v1.py --help`
  - `examples/bjorn/rough_v4/build/p05_rough_v4d.py --help`
  - imports of the guardrails functions
- `titles/remotion-posterity-motion` ships without `node_modules`. Run `npm ci` before `npx remotion studio` or `npx remotion render`.
