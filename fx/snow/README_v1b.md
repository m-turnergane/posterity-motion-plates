# snow_v1b — snow_v1 turned up a notch (R&D, 2026-10-31)

Owner feedback via Vellum: v1 looked good but was a bit too subtle.
`snow_v1b.py` is a copy of `snow_v1.py` with different numbers only; the model, mattes, proofs and CLI are the same (see README.md).
snow_v1.py and the v1 outputs are untouched. As asked, there is no reel or contact sheet; this will be folded into the Báthory rough cut.

    P=/workspace/mpvenv/bin/python
    $P snow_v1b.py render b11 out.mp4 [--size 540x960]     # also: presets / proof / stats / overlay / reel / sheet

## Tier changes vs v1 (TIER_DEFAULTS)
| tier | sigma (out px) | opacity | default n |
|---|---|---|---|
| far | 1.2–1.6 (unchanged) | .50 (unchanged) | 110 -> 187 |
| mid | 1.9–2.5 -> 2.2–2.9 (+15%) | .58 -> .66 | 60 -> 102 |
| near | 3.6–5.0 -> 4.0–5.6 (+12%) | .55 -> .64 | 22 -> 37 |
Speeds, sway, life envelope, colour, feathers and the gate blur are unchanged.

## Presets
| preset | plate (md5 pinned) | n far/mid/near | on screen mean (min–max) far/mid/near | vs v1 |
|---|---|---|---|---|
| b11 | b11_bytca_door_shut.png **redo** 32aa34cb… | 300/152/58 (far depth .155, mid .175, depth_soft .025) | 191.6 (178–206) 110/56/26 | 1.79x of v1's 107.3 (v1 used the old empty-courtyard plate) |
| b12 | b12_taken_up_to_fortress.png 78699fc7… | 204/94/31 | 154.5 (146–165) 89/45/20 | 1.67x |
| b17 | b17_secondhand_witnesses.png b48467066… | 221/128/44 | 105.2 (95–117) 52/37/16 | 1.80x |

## B11 (redone plate: two carriers, covered body on a bier, brazier left, blood in the snow, lit doorway right)
Keep-outs, all 0 px changed (plate px; 40 px feather, then a hard reset):
- faces: YuNet auto (finds carrier 1), padded
- subjects (heads band): carrier 1 head and hat [392,700]-[505,825]; carrier 2 head and hat [672,805]-[772,912]
- keepout: bier + body cloth [420,885]-[775,1045]; brazier + flame + glow [85,985]-[295,1262]. These stay clean for the torch pulse.
- interior: lit doorway (candle, figure) [775,680]-[925,1100]
- land: [[0,1215],[942,1180],[942,1672],[0,1672]], feather 80. The snow, blood and steps foreground never move.
Occlusion: in this plate, DA2 depth reads arcade ~0.10–0.15, carriers/bier ~0.20–0.25, cart 0.3, ground 0.3–1.0.
Far (.155) and mid (.175) flakes are therefore gated to the arcade and sky, so they pass behind the carriers, bier and cart.
Only near flakes pass in front of the carriers' bodies, and never over heads or the bier.

**For the depth_v1 build on B11, reuse these:**
- The cached DA2 map `cache/da2s_32aa34cb6a207b5b2e2138d2c96d1c12.npy` (941x1672 float16, 0 far..1 near).
- The near/far split: D ≈ 0.18 separates the carriers/bier from the arcade.
  Note that the ground ramps 0.3–1.0, so the near layer needs the figures mask, not just a threshold.
- The polygons above: heads, bier, brazier, doorway and the land line at y≈1180–1215.

## QA (proofs/*_v1b_*, 540x960 stills and the B11 overlay)
- proof_v1b_*.json, all 3 plates:
  - keep-out changed px 0 at 6 times, and outside-matte changed px 0.
  - Two instances give identical frame md5s (deterministic).
  - Guardrails ok: 1.217–1.219 output px per source px (limit 1.5); snow is added after the push.
- stats_v1b_*.json (phone 360x640):
  - Per-flake alpha step per frame: p99 0.022–0.037, max 0.14–0.17. Checked on B11 and B17: every step >0.1 is a flake sliding in at the frame edge, not a pop.
  - The whole-frame 1 s swing is ≤0.8 % and energy above 5 Hz is ≤0.03.
  - The pop12 counter is 35–115 phone px. It is higher than v1 because there are more and bigger flakes crossing pixel edges, not spawns.
