# Document reveals - PAUSED checkpoint (2026-10-30 ~7:35pm ET, owner priority change to maps v2)

## State
- Code: `doc_reveal_v1.py` (+ `legibility_control.py`, not yet run). Configs: `configs/dr01..dr05`.
- A full render finished: `final/doc_reveal_v1_reel_9x16.mp4` md5 2cc402ea59b12ca38a489a48b7bd466d, 21.5 s, hard cuts
  p07 -> b20 -> b10 (DOC-K1) | b15 reveal -> b15 later copy (DOC-F1). POCs in `poc/`, stills in `final/`, proofs in `proofs/`.
- Those proofs were written with the OLD gate (Canny new-edge count gated on reveals): dr01 + dr04 FAIL only on that.
  The gate has since been changed (code edited after the run started; pixels unaffected):
  reveal -> hp_logratio_p99 <= 0.02 (ref luma 40..250), lapvar <= 1.05, NCC >= 0.9; copy -> lapvar <= 1.0, NCC, new edges.
  Reason: a positive control (painted word on the page) showed Canny counts do not separate real from fake
  (8-bit threshold flips under dimming); hp does (real <= ~0.018, painted 0.023-0.29).
- dr04 effect-only swing was 8.6% (gate 8%) in the earlier proof-only run; reveal dur raised 2.0 -> 2.6 s before this render.
- dr03 (b10) now follows the LOCKED PRESETS 'Stacking: depth_v1 + torch_v1c + smoke_v2' via engine-rnd/hero/fullstack_v1.Stack
  (read-only import): torch face keep-out, smoke x0.4 on the near layer, mist as locked; left soldier face gets the same keep-out (24 px).

## To resume
1. `python legibility_control.py` -> proofs/legibility_positive_control.json (check summary: all real pass, all painted caught).
2. Proof-only rerun with the new gate: `python doc_reveal_v1.py configs/*.json --no-poc` (rewrites proofs/ and stills; check
   still md5s are unchanged vs the reel run = deterministic). Reel needs no re-render unless a config changes.
3. Check every shot PASS (esp. dr04 swing with dur 2.6), then write README.md and report (reel md5, shots, density, critique).
4. Delete /tmp/dr scratch.
