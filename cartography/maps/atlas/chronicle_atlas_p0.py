#!/usr/bin/env python3
"""chronicle_atlas_p0 -- Chronicle Atlas P0 step 1 (owner brief OWNER-ATLAS-BRIEF-2026-10-31.md).  STILLS ONLY.

ONE parameterised renderer.  The three emphasis states (political-forward, terrain-forward, hybrid "Chronicle Atlas")
differ ONLY in the EMPHASIS dict below; framing, routing, noise fields, label placement and ink geometry are computed
once per map and shared, so any state in between is a plain linear interpolation of the parameters (lerp_state).

Reuses (read-only imports, files untouched): map_modes_v2 (Terrain, ETOPO1 relief, REALMS-1327 field), map_route_v2_r2
(router, spline fit + assertions, nib stamping, ring, label placement), map_route_v1 (MAP-PLACES-v1 authority check,
Wikidata P625, IM Fell fonts, density guardrail), verify_realms_1327 (raster checks).

Separate control groups: colours (pigment_*), relief (relief_*, rivers), borders (border_*), labels (label_*).
Route ink is NOT an emphasis parameter: the story line is identical in every state.
Evidence grammar: documented = solid oxblood/iron-red ink, filled pin; Fieschi-claimed = broken, thinner, paler ink,
open ring; approximate = soft shaded area ONLY for MAP-PLACES rows marked approximate/area (none on Map 2 -> none drawn).
Borders: fine ink hairlines derived from the REALMS-1327 field, weighted by REALMS confidence; forbidden hard lines
(Franco-Imperial, Flanders, Wales) are never drawn; borders to neutral ground are never drawn (no false precision).
House rules: place names are the only text; no legend, title, vignette, letterbox or watermark.
"""
import argparse, hashlib, json, math, os, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__)); MAPS = os.path.dirname(HERE); sys.path.insert(0, MAPS)
import map_route_v2_r2 as R2                                  # noqa: E402  (also sets the r2 realm palette in-process)
MM, V1, VR = R2.MM, R2.V1, R2.VR

# ------------------------------------------------------------------------------------------ emphasis states
EMPHASIS = {
    "political": dict(pigment_alpha=0.88, pigment_chroma=1.08, pigment_glaze=0.30,
                      relief_shade=0.12, relief_tint=0.40, relief_ridge=0.08, rivers=0.45,
                      border_alpha=0.70, border_width=1.7,
                      label_region_alpha=1.00, label_place_alpha=1.00, label_halo=0.80),
    "terrain":   dict(pigment_alpha=0.30, pigment_chroma=0.70, pigment_glaze=0.85,
                      relief_shade=0.50, relief_tint=1.30, relief_ridge=0.34, rivers=0.95,
                      border_alpha=0.16, border_width=1.0,
                      label_region_alpha=0.78, label_place_alpha=1.00, label_halo=0.80),
    "hybrid":    dict(pigment_alpha=0.64, pigment_chroma=0.92, pigment_glaze=0.62,
                      relief_shade=0.30, relief_tint=0.85, relief_ridge=0.20, rivers=0.70,
                      border_alpha=0.42, border_width=1.3,
                      label_region_alpha=0.88, label_place_alpha=1.00, label_halo=0.80),
}
STATE_FILE = {"political": "political_forward", "terrain": "terrain_forward", "hybrid": "chronicle_hybrid"}

def lerp_state(a, b, t):
    """Any in-between state: every emphasis parameter enters the painter continuously, so this IS the transition."""
    A, B = EMPHASIS[a], EMPHASIS[b]; return {k: A[k] + (B[k] - A[k]) * t for k in A}

# ------------------------------------------------------------------------------------------ route ink (all states)
# r2 claimed vermilion was [252,102,46] (HSV S 0.82, chroma 206).  P0: oxblood/iron-red, less saturated, + dark halo.
ROUTE = {
    "documented": dict(col=[206, 78, 54], pool=[128, 36, 28], strength=0.97, halo_col=[16, 8, 8], halo_opacity=0.80,
                       halo_dilate=4, grain=0.12),
    "claimed":    dict(col=[222, 138, 108], pool=[150, 72, 54], strength=0.90, halo_col=[16, 8, 8], halo_opacity=0.64,
                       halo_dilate=3, grain=0.16),
}
# label hierarchy (kingdom tier exists but is empty: REALMS-1327-v1 must-not 1 forbids realm names on screen)
TIERS = {"kingdom": dict(px=56, italic=False, ink=[60, 34, 24]),
         "region":  dict(px=40, italic=True,  ink=[96, 60, 42]),
         "city":    dict(px=47, italic=False, ink=[44, 24, 16]),
         "castle":  dict(px=40, italic=False, ink=[60, 34, 24])}
BORDER_INK = [58, 40, 30]
# REALMS-1327 confidence per family pair (0 = never a line).  Rules cited from REALMS-1327-v1.md §2/§3.
BORDER_CONF = {("france", "empire"): 0.0,       # must-not 3: no hard Franco-Imperial line
               ("france", "flanders"): 0.0, ("empire", "flanders"): 0.0, ("france_fam", "flanders"): 0.0,  # must-not 3
               ("france_fam", "empire"): 0.0,   # Duchy|County of Burgundy is a Franco-Imperial edge too
               ("england", "scotland"): 0.35,   # §2.5 soft
               ("england", "france"): 0.40, ("england", "france_fam"): 0.40,   # Gascony COARSE
               ("france", "france_fam"): 0.40,  # Brittany / Duchy of Burgundy COARSE
               ("castile", "aragon"): 0.75, ("castile", "portugal"): 0.75, ("castile", "france_fam"): 0.6,
               ("aragon", "france_fam"): 0.6, ("aragon", "france"): 0.45, ("castile", "france"): 0.45, ("aragon", "empire"): 0.0}

def md5(p):
    h = hashlib.md5(); h.update(open(p, "rb").read()); return h.hexdigest()

def smooth(a, b, x): return np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))

# ------------------------------------------------------------------------------------------ shared, state-free fields
class Fields:
    """Every noise / texture / mask the painter needs, drawn ONCE per map with fixed seeds (no state dependence)."""
    def __init__(s, T, seed):
        H, W = T.geom.H, T.geom.W; rng = np.random.default_rng([seed, 11]); pn = MM.pn
        deep = np.float32([30, 62, 76]); mid = np.float32([52, 86, 98]); shallow = np.float32([92, 126, 124])
        off = MM.smoothstep(0, 140, T.d_sea)[..., None]; sea = mid * (1 - off) + deep * off
        sea = sea * (1 + 0.09 * pn(rng, H, W, 380, 14, 2.6)[..., None] + 0.05 * pn(rng, H, W, 120, 6, 2.2)[..., None])
        sh = np.exp(-T.d_sea / 9.0)[..., None]; sea = sea * (1 - 0.75 * sh) + shallow * 0.75 * sh
        s.sea = sea * (1 + 0.055 * pn(rng, H, W, 5, 0.7, 1.3)[..., None])
        s.paper = MM.paper(rng, H, W, [192, 150, 104], 15, stains=0.09)
        s.patch = 0.78 + 0.22 * np.clip(pn(rng, H, W, 260, 18, 2.4), -2, 2) / 2
        s.brush = 1 + 0.10 * pn(rng, H, W, 90, 2, 1.8, ax=0.15, ay=1.0) * pn(rng, H, W, 400, 60, 2.0)
        s.chip = pn(rng, H, W, 70, 2.0, 1.9)
        s.scuff = np.clip((pn(rng, H, W, 30, 1.0, 1.7) - 1.6) * 2.0, 0, 1) * 0.6
        s.coast_w = np.clip(0.75 + 0.3 * pn(rng, H, W, 80, 4), 0.35, 1.0)
        s.fox = MM.foxing(rng, H, W, 40); s.tooth = 1 + 0.045 * pn(rng, H, W, 3, 0.6, 1.0)
        s.border_wob = pn(rng, H, W, 40, 3, 1.8); s.border_break = pn(rng, H, W, 160, 12, 2.2)
        s.ink_grain = pn(rng, H, W, 3, 0.6, 1.2); s.ink_fibre = pn(rng, H, W, 18, 1.0, 1.5, ax=0.3, ay=1.0)
        e = T.elev_land
        s.low = (MM.smoothstep(220, 0, e) * MM.smoothstep(0.0, 8.0, T.d_land))[..., None]
        s.hi = MM.smoothstep(500, 2200, e)[..., None]; s.top = MM.smoothstep(2600, 3600, e)[..., None]
        s.ridge = np.clip(T.local_relief / 250.0, 0, 1)[..., None]
        s.rc, s.cov = T.realm_colour(R2.REALM_COL_A_R2)
        s.borders = border_field(T)

def border_field(T):
    """Per-pixel border geometry from the REALMS-1327 painted field: distance (plate px) to a dominance change between
    two painted families, and the REALMS confidence of that pair.  Neutral ground never gets a line."""
    rw = T.realm_weights(); fams = sorted(rw); H, W = T.lb.shape
    stack = np.stack([rw[f] for f in fams], 0); tot = stack.sum(0); dom = stack.argmax(0)
    dom = np.where((tot > 0.35) & (T.lb > 0), dom, -1)
    dist = np.full((H, W), 1e6, np.float32); conf = np.zeros((H, W), np.float32); pairs = {}
    k3 = np.ones((3, 3), np.uint8)
    for i, a in enumerate(fams):
        for j, b in enumerate(fams):
            if j <= i: continue
            c = BORDER_CONF.get((a, b), BORDER_CONF.get((b, a), 0.0))
            if c <= 0: continue
            B = (dom == i) & (cv2.dilate((dom == j).astype(np.uint8), k3) > 0)
            B &= (T.d_land > 3) & (np.minimum(rw[a], rw[b]) > 0.12)         # both genuinely present, off the coast
            if B.sum() < 20: continue
            d = cv2.distanceTransform((~B).astype(np.uint8), cv2.DIST_L2, 5)
            near = d < dist; dist = np.where(near, d, dist); conf = np.where(near & (d < 6), c, conf)
            pairs[f"{a}|{b}"] = dict(conf=c, boundary_px=int(B.sum()))
    return dict(dist=dist, conf=cv2.GaussianBlur(conf, (0, 0), 2.0), pairs=pairs)

# ------------------------------------------------------------------------------------------ painter
def paint(T, F, P):
    """Static basemap for emphasis parameters P (dict).  Order: paper + ETOPO1 relief tint -> translucent realm pigment
    (glaze keeps the relief value under it) -> hillshade through the paint -> rivers, coast -> fine borders."""
    ldp = F.paper.copy()
    olive = np.float32([150, 138, 84]); brown = np.float32([128, 88, 54]); pale = np.float32([214, 190, 150])
    k = P["relief_tint"]
    ldp = ldp * (1 - 0.30 * k * F.low) + olive * (0.30 * k * F.low) * (ldp / 180.0)
    ldp = ldp * (1 - 0.35 * k * F.hi) + brown * 0.35 * k * F.hi
    ldp = ldp * (1 - 0.35 * k * F.top) + pale * 0.35 * k * F.top
    r = P["relief_ridge"]; ldp = ldp * (1 - r * F.ridge) + brown * r * F.ridge
    # realm pigment: chroma around its own luma; opaque coat <-> multiply glaze (relief value stays visible)
    rc = F.rc; lum = (rc @ np.float32([0.299, 0.587, 0.114]))[..., None]; rc = np.clip(lum + (rc - lum) * P["pigment_chroma"], 0, 255)
    wear = np.clip((F.chip * 0.55 + 2.0 * F.cov - 0.55) * 2.5, 0, 1)
    a = np.clip(F.cov ** 0.7 * wear * F.patch * F.brush * (1 - F.scuff), 0, 1) * P["pigment_alpha"] * MM.smoothstep(0.5, 3.0, T.d_land)
    pool = np.clip(cv2.GaussianBlur(np.abs(cv2.Laplacian(a, cv2.CV_32F, ksize=3)), (0, 0), 1.0) * 5.0, 0, 0.25)
    opaque = 0.6 * rc + 0.4 * ldp * rc / 200.0
    glaze = rc * np.clip(ldp / 165.0, 0.4, 1.6) * 1.12
    coat = (opaque * (1 - P["pigment_glaze"]) + glaze * P["pigment_glaze"]) * (1 - pool)[..., None]
    ldp = ldp * (1 - a[..., None]) + coat * a[..., None]
    ldp = ldp * (1 + P["relief_shade"] * np.clip(T.hs, -1, 1))[..., None]          # ETOPO1 hillshade THROUGH the paint
    rim = np.exp(-T.d_land / 3.0)[..., None]; ldp = ldp * (1 - 0.35 * rim) + np.float32([214, 188, 140]) * 0.35 * rim
    al = T.land[..., None]; img = F.sea * (1 - al) + ldp * al
    for m, kk in ((T.riv_major, 0.70), (T.riv_minor, 0.35)):
        kk = kk * P["rivers"]; img = img * (1 - kk * m[..., None]) + np.float32([66, 96, 108]) * kk * m[..., None]
    ew = T.edge * F.coast_w; img = img * (1 - 0.8 * ew[..., None]) + np.float32([40, 34, 26]) * 0.8 * ew[..., None]
    img *= (1 - 0.10 * F.fox)[..., None]; img *= F.tooth[..., None]
    return np.clip(img, 0, 255).astype(np.float32)

def border_alpha(F, P, label_mask=None):
    """Fine ink hairline: width = border_width (plate px, continuous), opacity = border_alpha x REALMS confidence;
    a slow pen-pressure wobble so it reads as ink, not vector."""
    B = F.borders; w = P["border_width"] * (1 + 0.18 * np.clip(F.border_wob, -1.5, 1.5))
    a = (1 - smooth(w * 0.5 - 0.6, w * 0.5 + 0.6, B["dist"])) * B["conf"] * P["border_alpha"]
    a *= np.clip(0.78 + 0.22 * F.border_break, 0.45, 1.0)
    if label_mask is not None: a *= (1 - label_mask)
    return np.clip(a, 0, 1).astype(np.float32)

# ------------------------------------------------------------------------------------------ route ink
def composite_route(img, alpha, st, F):
    R = ROUTE[st]; core = cv2.GaussianBlur(alpha, (0, 0), 0.7); bleed = cv2.GaussianBlur(alpha, (0, 0), 2.0) * 0.12
    grain = 1 + R["grain"] * np.clip(F.ink_grain, -1.5, 1.5) * (0.7 + 0.3 * np.clip(F.ink_fibre, -1, 1))
    a = np.clip(core ** 0.9 * R["strength"] * grain + bleed, 0, 0.97)
    edge = np.clip((alpha - cv2.GaussianBlur(alpha, (0, 0), 1.2)) * 2.5, 0, 1)        # ink pools at the stroke margin only
    col = np.float32(R["col"]) * (1 - edge[..., None] * 0.55) + np.float32(R["pool"]) * edge[..., None] * 0.55   # ink pools at edges
    return img * (1 - a[..., None]) + col * a[..., None] * (0.92 + 0.08 * img / 200.0), a

# ------------------------------------------------------------------------------------------ contrast
def contrast_unit(img, base, alpha, Pt, w0, pins, step=3.0):
    """R2.contrast_along (core vs raw basemap under it; core vs rendered edge just outside the stroke) PLUS
    stroke-vs-map: core vs the rendered map 6..10 px outside the stroke edge (beyond the halo), what the eye reads."""
    out = R2.contrast_along(img, base, alpha, Pt, w0, pins, step)
    H, W = alpha.shape; m = np.ones((H, W), np.uint8); cv2.polylines(m, [np.int32(np.round(Pt * 4))], False, 0, 1, cv2.LINE_8, shift=2)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5); Lr = R2.rel_lum(img); Q = R2.resample(Pt, step); RR = int(w0 / 2 + 12); cs = []
    for q in Q:
        if any(np.hypot(*(q - p["xy"])) < p["r_edge"] + 4 for p in pins): continue
        x, y = int(round(q[0])), int(round(q[1])); x0, y0, x1, y1 = max(0, x - RR), max(0, y - RR), min(W, x + RR + 1), min(H, y + RR + 1)
        a = alpha[y0:y1, x0:x1]; d = dist[y0:y1, x0:x1]; core = (a > 0.75) & (d <= max(0.4 * w0, 0.8))
        ring = (d >= w0 / 2 + 6) & (d <= w0 / 2 + 10) & (a < 0.05)
        if core.sum() < 2 or ring.sum() < 3: continue
        cs.append(R2.wcag(float(np.median(Lr[y0:y1, x0:x1][core])), float(np.median(Lr[y0:y1, x0:x1][ring]))))
    if cs:
        cs = np.array(cs); out["core_vs_map_beyond_halo"] = dict(min=round(float(cs.min()), 2), p5=round(float(np.percentile(cs, 5)), 2), median=round(float(np.median(cs)), 2))
    return out

def colour_stats(rgb):
    c = np.float32(rgb); mx, mn = c.max(), c.min(); lab = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2LAB)[0, 0].astype(float)
    return dict(rgb=list(map(int, rgb)), hsv_s=round(float((mx - mn) / mx), 3), chroma_rgb=int(mx - mn),
                lab_chroma=round(float(math.hypot(lab[1] - 128, lab[2] - 128)), 1), rel_lum=round(float(R2.rel_lum(c)), 4))

# ------------------------------------------------------------------------------------------ authority extras
def check_approx_areas(cfg, rows):
    """Approximate-area shading only for MAP-PLACES rows whose status marks an area/approximate place."""
    out = []
    for ar in cfg.get("approx_areas", []):
        r = rows.get(ar["row"]); assert r and r["qid"] == ar["qid"], f"approx area {ar['row']} not in MAP-PLACES-v1"
        assert ("area" in r["status"].lower() or "approx" in r["status"].lower()), f"{ar['row']} ({r['status']}) is not marked approximate"
        out.append(ar)
    return out

def tier_of(row, isreg, rows):
    if isreg: return "region"
    return "castle" if "castle" in rows[row]["site"].lower() else "city"

# ------------------------------------------------------------------------------------------ shot
class AtlasShot(R2.StillShot):
    def __init__(s, cfg_path):
        super().__init__(cfg_path)                                     # authority check + routing + spline assertions
        s.rows = V1.read_places_md(); s.approx = check_approx_areas(s.cfg, s.rows)
        s.F = Fields(s.T, s.cfg["seed"]); s._build_ink(); s._place_labels()

    def _build_ink(s):
        cfg, T = s.cfg, s.T; H, W = T.lb.shape; s.alpha = {"documented": np.zeros((H, W), np.float32), "claimed": np.zeros((H, W), np.float32)}
        s.leg_alpha = {}
        for li, lg in enumerate(s.legs):
            cv = R2.Canvas(H, W)                                      # documented: solid (no dash); claimed: broken
            R2.ink_leg(cv, lg["Pt"], lg["w0"], lg["style"], np.random.default_rng([cfg["seed"], 100 + li]), arrow=True,
                       dash=(lg.get("dash") if lg["style"] == "claimed" else None))
            a = cv.alpha(); s.leg_alpha[li] = a; s.alpha[lg["style"]] = np.maximum(s.alpha[lg["style"]], a)
        for pi, p in enumerate(s.pins):
            cv = R2.Canvas(H, W); p["r_outer_max"] = R2.ring(cv, p["xy"], p["rc"], p["wr"], np.random.default_rng([cfg["seed"], 300 + pi]))[0]
            if p["style"] == "documented": cv.stamp([p["xy"]], [p["rc"] * 0.9])     # documented stop: filled
            s.alpha[p["style"]] = np.maximum(s.alpha[p["style"]], cv.alpha())
        s.halo = {}
        for st, a in s.alpha.items():
            R = ROUTE[st]; kh = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * R["halo_dilate"] + 1,) * 2)
            s.halo[st] = np.clip(cv2.GaussianBlur(cv2.dilate(a, kh), (0, 0), R2.HALO_SIGMA) * 1.15, 0, 1) * R["halo_opacity"]

    def _place_labels(s):
        """Placed ONCE (identical in every state).  Block = all route ink + halos + pin discs + every border pixel any
        state could draw (geometry is state-free) + earlier labels.  A placement with any hit is refused."""
        T = s.T; H, W = T.lb.shape; frame = (70, 50, W - 70, H - 50)
        anyink = np.maximum.reduce([s.alpha["documented"], s.alpha["claimed"], s.halo["documented"], s.halo["claimed"]])
        block = (cv2.dilate((anyink > 0.04).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0).astype(np.uint8)
        for p in s.pins: cv2.circle(block, (int(round(p["xy"][0])), int(round(p["xy"][1]))), int(p["r_edge"] + 4), 1, -1)
        soft = (anyink > 0.02).astype(np.uint8)
        s.border_any = (s.F.borders["dist"] < 2.0) & (s.F.borders["conf"] > 0.02)
        soft = np.maximum(soft, s.border_any.astype(np.uint8))           # borders: prefer to avoid; masked under labels anyway
        items = [(p, False) for p in s.pins if p.get("label")] + [(r, True) for r in s.regions]
        s.labels = []
        for p, isreg in items:
            tier = tier_of(p["row"], isreg, s.rows); px = TIERS[tier]["px"]
            best = R2.place_label(p["label"], p["xy"], (6.0 if isreg else p["r_edge"]), block, frame, px, [p["side"]] if p.get("side") else [],
                                  H, W, other_pins=[q["xy"] for q in s.pins if q is not p], region=isreg, soft=soft)
            assert best is not None and best[5] == 0, f"label {p['label']}: no collision-free in-frame spot ({best and best[5]})"
            sc, L, bb, sd, gap, hit = best; x0, y0, x1, y1 = bb; block[max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = 1
            s.labels.append(dict(L=L, bb=bb, tier=tier, text=p["label"], row=p["row"], side=sd, gap=gap, px=px, hit=hit))
        lm = np.zeros((H, W), np.float32)
        for l in s.labels:
            L = l["L"]; x0, y0, x1, y1 = L.bbox(); cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            lm[cy0:cy1, cx0:cx1] = np.maximum(lm[cy0:cy1, cx0:cx1], np.clip(L.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * 2, 0, 1))
            bx0, by0, bx1, by1 = l["bb"]; lm[max(0, by0 - 3):by1 + 3, max(0, bx0 - 3):bx1 + 3] = 1.0
        s.label_mask = cv2.GaussianBlur(lm, (0, 0), 1.5); s.label_mask = np.maximum(s.label_mask, (lm >= 1).astype(np.float32))

    def render(s, P):
        T, F = s.T, s.F; H, W = T.lb.shape
        base = paint(T, F, P); img = base.copy()
        ba = border_alpha(F, P, s.label_mask) * T.land
        img = img * (1 - ba[..., None]) + np.float32(BORDER_INK) * ba[..., None]
        mapimg = img.copy()                                              # basemap + borders, before route ink
        ink_a = np.zeros((H, W), np.float32)
        for st in ("claimed", "documented"):                             # documented ink on top
            h = s.halo[st]; img = img * (1 - h[..., None]) + np.float32(ROUTE[st]["halo_col"]) * h[..., None]
        for st in ("claimed", "documented"):
            img, a = composite_route(img, s.alpha[st], st, F); ink_a = np.maximum(ink_a, a)
        inked = img.copy(); s._last = (inked, mapimg)                      # kept for the phone-scale contrast proof
        for l in s.labels:                                               # labels: tiered ink, state alpha
            L = l["L"]; x0, y0, x1, y1 = L.bbox(); cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
            roi = img[cy0:cy1, cx0:cx1]; a = L.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            la = P["label_region_alpha"] if l["tier"] == "region" else P["label_place_alpha"]
            hl = L.halo[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * P["label_halo"] * la
            roi[...] = roi * (1 - hl[..., None]) + np.float32(R2.LABEL_HALO_COL) * hl[..., None]
            roi[...] = roi * (1 - 0.94 * la * a[..., None]) + np.float32(TIERS[l["tier"]]["ink"]) * 0.94 * la * a[..., None]
        out = cv2.resize(np.clip(img + 0.5, 0, 255).astype(np.uint8), tuple(s.cfg["out_wh"]), interpolation=cv2.INTER_AREA)
        pr = dict(params=P, legs=[], labels=[])
        for li, lg in enumerate(s.legs):
            pr["legs"].append(dict(leg=f"{lg['a']['row']}->{lg['b']['row']}", style=lg["style"], w0=lg["w0"], dash=lg.get("dash") if lg["style"] == "claimed" else None,
                                   fit=lg["fit"], sigma=lg["sigma"], checks=lg["check"],
                                   contrast=contrast_unit(inked, mapimg, s.leg_alpha[li], lg["Pt"], lg["w0"], s.pins)))
        for l in s.labels:
            x0, y0, x1, y1 = l["bb"]
            pr["labels"].append(dict(text=l["text"], row=l["row"], tier=l["tier"], px=l["px"], side=l["side"], bbox=[int(v) for v in l["bb"]],
                                     placement_hits=l["hit"],
                                     route_ink_px_in_bbox=int((ink_a[max(0, y0):y1, max(0, x0):x1] > 0.02).sum()),
                                     route_halo_px_in_bbox=int((np.maximum(s.halo["documented"], s.halo["claimed"])[max(0, y0):y1, max(0, x0):x1] > 0.02).sum()),
                                     border_ink_px_in_bbox=int((ba[max(0, y0):y1, max(0, x0):x1] > 0.02).sum())))
        bbs = [l["bb"] for l in s.labels]
        pr["label_pair_overlaps"] = sum(1 for i in range(len(bbs)) for j in range(i + 1, len(bbs))
                                        if not (bbs[i][2] <= bbs[j][0] or bbs[j][2] <= bbs[i][0] or bbs[i][3] <= bbs[j][1] or bbs[j][3] <= bbs[i][1]))
        pr["border_px_gt0.05"] = int((ba > 0.05).sum()); pr["border_pairs"] = F.borders["pairs"]
        return out, pr

def phone_x0(out_w, out_h, legs, labels, plate_w):
    """R2.phone_crop rule, but no label may be cut by the crop edge, then stop names outrank region names (most stop labels whole, then all labels, then route ink, then centred); chosen once, used for all states."""
    sx = out_w / plate_w; P = np.concatenate([lg["Pt"] for lg in legs]) * sx; cx = 0.5 * (P[:, 0].min() + P[:, 0].max())
    cw = int(round(out_h * 9 / 16)); best = None
    for x0 in range(0, out_w - cw + 1, 4):
        inside = [l for l in labels if x0 <= l["bbox"][0] * sx and l["bbox"][2] * sx <= x0 + cw]
        npin = sum(1 for l in inside if l["tier"] != "region")      # pin (stop) names first, then region names
        ni = int(((P[:, 0] >= x0) & (P[:, 0] <= x0 + cw)).sum()); ncut = sum(1 for l in labels if l["bbox"][0] * sx < x0 + cw and l["bbox"][2] * sx > x0 and l not in inside)
        key = (-ncut, npin, len(inside), ni // 200, -abs(x0 + cw / 2 - cx))
        if best is None or key > best[0]: best = (key, x0)
    x0 = best[1]; whole = [l["text"] for l in labels if x0 <= l["bbox"][0] * sx and l["bbox"][2] * sx <= x0 + cw]
    cut = [l["text"] for l in labels if l["bbox"][0] * sx < x0 + cw and l["bbox"][2] * sx > x0 and l["text"] not in whole]
    return x0, cw, whole, cut

def save(path, rgb):
    assert not os.path.exists(path), f"refusing to overwrite {path}"
    cv2.imwrite(path, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 9]); return md5(path)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--tag", required=True)
    ap.add_argument("--outdir", default=HERE); a = ap.parse_args()
    S = AtlasShot(a.config); od = a.outdir; os.makedirs(f"{od}/stills", exist_ok=True); os.makedirs(f"{od}/phone", exist_ok=True)
    os.makedirs(f"{od}/sheets", exist_ok=True); os.makedirs(f"{od}/proofs", exist_ok=True)
    allp = dict(shot=S.name, config=a.config, density=S.density, authority=S.authority, approx_areas=S.approx,
                control_points={k: v for k, v in S.cp.items() if k != "points"}, route_ink={k: dict(v, col_stats=colour_stats(v["col"])) for k, v in ROUTE.items()},
                r2_vermilion=colour_stats([252, 102, 46]), states={})
    outs = {}
    for st in ("political", "terrain", "hybrid"):
        out, pr = S.render(EMPHASIS[st]); outs[st] = out
        p = f"{od}/stills/{a.tag}_atlas_p0_{STATE_FILE[st]}_16x9.png"; pr["png"] = p; pr["md5"] = save(p, out)
        allp["states"][st] = pr; print(p, pr["md5"], flush=True)
    labs = allp["states"]["hybrid"]["labels"]; H, W = outs["hybrid"].shape[:2]
    x0, cw, whole, cut = phone_x0(W, H, S.legs, labs, S.cfg["plate_wh"][0]); allp["phone"] = dict(x0=x0, crop_w=cw, labels_whole=whole, labels_cut=cut, files={})
    phones = {}
    for st in ("political", "terrain", "hybrid"):
        ph = cv2.resize(outs[st][:, x0:x0 + cw], (360, 640), interpolation=cv2.INTER_AREA); phones[st] = ph
        p = f"{od}/phone/{a.tag}_atlas_p0_{STATE_FILE[st]}_phone360x640.png"; allp["phone"]["files"][st] = dict(path=p, md5=save(p, ph)); print(p, flush=True)
    # sheet: political | terrain | hybrid at 960x540, phone crops centred beneath each (no text)
    gap = 8; sheet = np.full((540 + gap + 640, 3 * 960 + 2 * gap, 3), 24, np.uint8)
    for i, st in enumerate(("political", "terrain", "hybrid")):
        x = i * (960 + gap); sheet[:540, x:x + 960] = cv2.resize(outs[st], (960, 540), interpolation=cv2.INTER_AREA)
        sheet[540 + gap:, x + 300:x + 660] = phones[st]
    p = f"{od}/sheets/{a.tag}_atlas_p0_sheet_political_terrain_hybrid.png"; allp["sheet"] = dict(path=p, md5=save(p, sheet), order="political | terrain | hybrid; phone crops beneath")
    rw = S.T.realm_weights()
    allp["realms_raster"] = VR.check_raster(rw, lambda lo, la: S.geom.analytic(np.float64([lo]), np.float64([la]))[0], S.T.lb.shape,
                                            [l["text"] for l in labs], R2.REALM_WORDS)
    pj = f"{od}/proofs/{a.tag}_atlas_p0_proofs.json"; assert not os.path.exists(pj)
    json.dump(allp, open(pj, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)); print(pj)

if __name__ == "__main__":
    main()
