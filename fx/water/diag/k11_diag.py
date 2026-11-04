"""K11 fire-break diagnosis: numbers + crops (new files only)."""
import sys, json, numpy as np, cv2, importlib.util
s = importlib.util.spec_from_file_location('w', '/workspace/posterity/engine-rnd/water/water_v1.py'); W = importlib.util.module_from_spec(s); s.loader.exec_module(W)
cfg = W._cfg('configs/k11_fire_reflection_v1b.json'); sh = W.WaterShot(cfg); P = sh.P; H, Wd = P.shape[:2]
out = {}
s0 = max(1080 / Wd, 1920 / H); z = cfg['push'][0]; out.update(native=[Wd, H], cover_fit_scale=round(s0, 4), zoom=z, output_px_per_plate_px=round(s0 * z, 3),
    phone_px_per_plate_px=round(s0 * z / 3, 3), plate_px_visible_w=round(Wd / z, 1))
# sharpness: Laplacian variance at native res on fire rects (luma), compare to other locked fire plates
def lapv(img, rect):
    x0, y0, x1, y1 = rect; g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float64); return float(cv2.Laplacian(g, cv2.CV_64F).var())
def ten(img, rect):
    x0, y0, x1, y1 = rect; g = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_RGB2GRAY).astype(np.float64)
    return float(np.mean(cv2.Sobel(g, cv2.CV_64F, 1, 0) ** 2 + cv2.Sobel(g, cv2.CV_64F, 0, 1) ** 2))
rects = cfg['fire']['torch']; out['k11_fire_rect_lapvar'] = [round(lapv(P, r), 1) for r in rects]
FXm = W.FX()
others = {}
for k, path in [('b13', '/workspace/posterity/standalones/edward-ii/plates-v3b/b13_nottingham_seizure_OWNER.png'), ('b10', '/workspace/posterity/standalones/edward-ii/plates-v3b/b10_corfe_kent_hands_letter_OWNER.png')]:
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB); others[k] = [round(lapv(im, r), 1) for r in FXm.SPECS[k]['torch']]
out['ref_torch_rect_lapvar'] = others
# per-source geometry (plate px) and glow sigma vs source size
srcs = []
for sr in sh.fx.srcs:
    sg = float(np.clip(0.9 * sr['h'], 20, 120)); m = sr['mask']; x0, y0, x1, y1 = sr['bb']
    srcs.append(dict(bb=[int(v) for v in sr['bb']], h=round(float(sr['h']), 1), w=round(float(sr['w']), 1), glow_sigma_plate_px=round(sg, 1),
        glow_sigma_out_px=round(sg * s0 * z, 1), glow_sigma_phone_px=round(sg * s0 * z / 3, 1), mask_px=int((m > 0.05).sum())))
out['sources'] = srcs
# how much of the fx change is thrown away by the fire-pixel allow matte (glow/spill clipped at the mask edge)
t = 6.0 + 1.0
raw = sh.fx.render(t, 0.0).astype(np.float32); d = np.abs(raw - P.astype(np.float32)).max(-1)
keep = sh.keep; fz = sh.fire_zone
tot = float(d.sum()); inside = float((d * keep).sum())
out['fx_change_energy_kept_frac'] = round(inside / max(tot, 1e-6), 3)
out['fx_changed_px_raw'] = int((d >= 1).sum()); out['fx_changed_px_after_matte'] = int(((d * keep) >= 1).sum())
# edge: gradient of the per-frame change map at the matte boundary, in output px
D = np.abs(sh.frame(1.0).astype(np.float32) - P).max(-1)
edge = cv2.morphologyEx(fz.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
gy, gx = np.gradient(cv2.GaussianBlur(D, (0, 0), 0.7)); gm = np.hypot(gx, gy)
out['change_map_gradient_at_fire_matte_edge_mean'] = round(float(gm[edge].mean()), 2); out['change_map_gradient_elsewhere_in_allow_mean'] = round(float(gm[(~sh.protect) & ~edge].mean()), 2)
out['allow_feather_plate_px'] = cfg['protect_feather']; out['allow_feather_out_px'] = round(cfg['protect_feather'] * s0 * z, 1); out['mask_dilate_out_px'] = round(3 * s0 * z, 1)
# upscale filter: cubic overshoot on the fire edges (ringing) vs area/lanczos
crop = (700, 600, 941, 720); x0, y0, x1, y1 = crop; roi = sh.frame(1.0)[y0:y1, x0:x1]
up_c = cv2.resize(roi, None, fx=s0 * z, fy=s0 * z, interpolation=cv2.INTER_CUBIC)
up_l = cv2.resize(roi.astype(np.float32), None, fx=s0 * z, fy=s0 * z, interpolation=cv2.INTER_LINEAR)
out['cubic_overshoot_px_frac'] = round(float(((up_c.astype(np.int16) == 255) | (up_c.astype(np.int16) == 0)).any(-1).mean()), 4)
# crops: plate, fx raw (no matte), water_v1 frame, |diff|x4, all at native, then the same in output px
fr1 = sh.frame(1.0)
def C(a): return a[y0:y1, x0:x1]
diff = np.clip(np.abs(fr1.astype(np.int16) - P.astype(np.int16)) * 4, 0, 255).astype(np.uint8)
rawc = np.clip(raw, 0, 255).astype(np.uint8)
row = np.hstack([C(P), C(rawc), C(fr1), C(diff)]); row = cv2.resize(row, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
cv2.imwrite('diag/k11_fire_native_plate_fxraw_wv1_diff_x2.png', cv2.cvtColor(row, cv2.COLOR_RGB2BGR))
cz = tuple(cfg['push_center']); o = W.F3.push_frame(fr1, 0, 1080, 1920, z, z, center=cz); o1 = W.F3.push_frame(fr1, 0, 1080, 1920, 1.0, 1.0, center=(0.5, 0.5))
ph = cv2.resize(o, (360, 640), interpolation=cv2.INTER_AREA); ph1 = cv2.resize(o1, (360, 640), interpolation=cv2.INTER_AREA)
cv2.imwrite('diag/k11_output_1080_z2.2_firecrop.png', cv2.cvtColor(o[300:900, 300:1080], cv2.COLOR_RGB2BGR))
cv2.imwrite('diag/k11_phone_z2.2_vs_z1.0.png', cv2.cvtColor(np.hstack([ph, ph1]), cv2.COLOR_RGB2BGR))
# phone-level sharpness of the fire band: z2.2 vs native fill
out['phone_fire_band_tenengrad_z2.2'] = round(ten(ph, (150, 150, 360, 260)), 1)
json.dump(out, open('diag/k11_diag_numbers.json', 'x'), indent=1); print(json.dumps(out, indent=1))
