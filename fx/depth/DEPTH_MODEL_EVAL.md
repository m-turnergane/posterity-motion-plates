# Depth model eval — one free CPU model vs hand masks (one plate)

**Verdict: KEEP the model (DA2-Small hybrid).** On edges and authoring it is clearly better than hand polygons. Ordering is the same, and so are disocclusion and fill. It is still a *hybrid*: depth sets the cut, and a few hand boxes (region / exclude / seams / protect) fix the cases the model gets wrong.

- **Model:** Depth Anything V2 Small, onnx-community fp32 ONNX, Apache-2.0.
- **Runtime:** onnxruntime CPU, already in the venv, so nothing was installed.
- **Plate:** `standalones/edward-ii/plates-v3b/b10_*` (Corfe letter: Kent, horse, hand holding the letter), 941x1672.
- **Compared configs:** hand masks are `configs/b10_corfe_letter_drift_HANDPOLY_eval.json` (2 traced polys, 44 vertices). The model is `configs/b10_corfe_letter_drift_v1.json`, using `depth_min 0.32` plus one floor-seam box.
- **Same everywhere else:** camera, layer params, guided-filter refinement, inpaint and renderer are identical. Only the near-layer matte differs.

| | hand polys | DA2 hybrid |
|---|---|---|
| matte contour on strong image edges | 22.7 % | **79 %** |
| image gradient on contour / plate median | 1.81x | **4.72x** |
| soft band width | 5.32 px | 5.87 px |
| revealed at max offset (e=1) | 0.95 % | 1.08 % |
| holes at max offset | 0 | 0 |
| fill texture (hf revealed / ring) | 0.62 | 0.49 |
| rigidity (faces/hands/letter) | pass | pass |
| build time per render setup | 3.85 s | 4.14 s |
| authoring | ~15 min, still misses hair curls, horse ears, fur, spear tips | ~3 min |

- **Ordering:** labels disagree on 2.1 % of pixels. All disagreements are at silhouettes; no layer swaps.
- **Halos:** the hand polys carry a sky patch around Kent's hair, cut off the horse's ears and pull background wall and soldiers in next to the letter. All three show as moving halos in the side-by-side. The hybrid follows the painted silhouette.
- **Weak spot of the model:** fill texture is smoother (hf_ratio 0.49). This is because it reveals slightly more along real detail edges, and TELEA smears there. It is visible only at max offset, in strips about 15 px wide.
- **Model failures that need hand fixes:**
  - Continuous floors and ground get cut by a threshold, so they need a `seams` box.
  - A head can land in a different depth band from its body (b05 left man), so `depth_min` needs tuning and a `protect` check.
  - In paintings with sky, the sky must be far (no issue so far).
- **Runtime:** session load 0.37 s, inference 0.89 s at 518x924. The result is cached per plate as `.npy`.
- **Disk:** weights 95–99 MB (`models/da2_small.onnx`). Cache is ~2.9 MB per plate; `cache/` is 20 MB for 7 plates.

Artifacts:
- `eval/depth_model_eval_still.jpg`: hand vs DA2 crops of hair, horse head and hand+letter at max offset.
- `eval/depth_model_eval_sbs_540p.mp4`: LEFT is hand poly, RIGHT is DA2 hybrid.
- `eval/depth_model_eval.json`: all numbers.
- `eval/depth_model_eval.py`: reproduces the numbers.
