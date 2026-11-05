# REGISTRATION-PLAN v2.1: the ACTIVE atlas registration authority (VIDEO-PACK-v2)

Written 2026-11-04 in response to review item D3. This plan supersedes `sources/atlas-refpack-v2/REGISTRATION-PLAN-v2.md` (b8002aff) **only on the global-transform step**. Every other part of the old plan still stands: the control points, the NCC refinement, the TPS, the QA thresholds and the clean-plate rule. The old file is kept unchanged.

## Single authority, in this order
1. **Primary: ORB + RANSAC homography.**
   - Detector: ORB with 6000 keypoints, brute-force Hamming matching with cross-check.
   - Fit: `cv2.findHomography(..., RANSAC, 6.0)`.
2. **Sanity gate on the homography.** The fit is accepted only if all of these hold:
   - projective strength |h31|,|h32|·max(W,H) < 0.05
   - √|det A| between 0.5 and 2.5
   - cond(A) < 1.3
   - at least 40 inliers
   
   A generated top-down map should be close to affine. A strong perspective term means a bad fit.
3. **Fallback 1: RANSAC affine.** Used when the gate fails. Fit with `cv2.estimateAffine2D` (RANSAC, 6 px, at least 30 inliers).
4. **Fallback 2: manual 4-point registration.** This deterministic route is used when the affine fit fails, or when control-point QA still fails after refinement.
   - Pick 4 unambiguous coastal or city control points that are well spread.
   - Fit with `cv2.getPerspectiveTransform`.
   - Log the points.
5. **Then, unchanged from v2:**
   - NCC refinement on the control points (accept at NCC ≥ 0.6)
   - thin-plate spline, smoothing 5
   - warp limit 0.025 × min side
   - QA thresholds per REGISTRATION-PLAN-v2 / MAP-PACK §2.3
   - Failed plate → refpack tinted render

## Reference script
`registration/register_atlas_h.py`. Run it with `/workspace/mpvenv/bin/python` (cv2 5.0.0). It never overwrites existing outputs and writes `<prefix>_transform.json` and `<prefix>_registered.png`.

Test on 2026-11-04, comparing the refpack `*_ref_tinted_notext.png` against `*_regproto_synthetic_plate.png`. The residuals are for the global stage only, before NCC/TPS; the synthetic plate also carries a non-rigid field.

| frame | matches | H inliers | gate | method | inlier resid median / p95 |
|---|---|---|---|---|---|
| euro_16x9 | 4020 | 3789 | persp 0.0130, scale 0.967, cond 1.017 | HOMOGRAPHY | 2.47 / 5.22 px |
| britain_16x9 | 3349 | 2651 | persp 0.0335, scale 0.951, cond 1.026 | HOMOGRAPHY | 2.10 / 5.15 px |

**Not yet validated on a real generated map.** That validation is required before production: run on the first AB/AE plate, and fall back to the manual 4-point route if needed.
