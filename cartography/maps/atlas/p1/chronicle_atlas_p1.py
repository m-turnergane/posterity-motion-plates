#!/usr/bin/env python3
"""chronicle_atlas_p1 -- three strong-pigment palette concepts of the SAME map-2b frame (new file; p0/p0b untouched).

Everything geometric is imported unchanged from chronicle_atlas_p0b / p0: frame, projection, relief, routing, pins, label
placement (placed once -> identical in every treatment).  New here:
  * a CRISP painted partition of the REALMS-1327 field (argmax of the soft family weights + a little hand-brush noise):
    pigment is flat and full-strength inside a realm and stops cleanly at the border.  Where REALMS-1327 allows an ink line
    (pair confidence > 0) the pigment edge is pinned to the line (noise amp ~0.01).  Where it forbids one (France|Empire,
    Flanders) the two pigments interlock in a hand-stippled frontier band instead (no line, no gradient).  Neutral edges
    and Lombardy (Milan fringe) end in a broken brush edge onto bare relief parchment.
  * an opaque gouache painter: pigment coat over parchment, relief carried in CIELAB L* only (hue kept), brush / patch
    value variation, granulation, wear chips that show the parchment, darker pigment pooled along inked borders.  Age =
    texture (grain, chips, ink breaks), never desaturation.
  * route: deep oxblood core + restrained parchment keyline (dilated per dash, so gaps stay gaps), opacity adaptive to the
    luminance under it.  Documented solid, Fieschi-claimed broken + lighter brick.
"""
import copy, json, os, sys, math, argparse, hashlib
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); ATLAS = os.path.dirname(HERE); sys.path.insert(0, ATLAS)
import chronicle_atlas_p0b as B                                         # noqa: E402
A = B.A; R2, MM, V1, VR = A.R2, A.MM, A.V1, A.VR
sys.path.insert(0, ATLAS); import proof_atlas_p0 as PA                  # noqa: E402  (refusal test)

THR = 0.36                       # dominant soft weight below this -> neutral parchment (unclaimed / fading)
FAMS_ORDER = ["england", "england_light", "france", "france_fam", "flanders", "empire", "castile", "aragon",
              "scotland", "portugal"]

TREAT = {
 "heraldic": dict(
    concept="Royal Heraldic: flat armorial tinctures (gules, azure, or, purpure, tenne) laid edge-to-edge like a roll of arms; clean pale parchment, crisp sepia ink.",
    pal=dict(england=[176, 30, 40], england_light=[208, 112, 104], france=[32, 66, 158], france_fam=[126, 154, 206],
             empire=[208, 154, 42], castile=[114, 44, 106], aragon=[206, 108, 40], scotland=[38, 104, 86], portugal=[50, 118, 60]),
    flanders_mix=0.62, sea=[62, 92, 108], paper=[218, 198, 156], ink=[44, 30, 24], neutral_tint=[0, 0, 0],
    relief_L=21.0, ridge_L=6.0, var_L=4.0, gran=1.3, wear=0.55, band_L=5.0, band_w=5.0, band_c=1.06,
    border_w=1.9, border_op=0.95, coast_ink=0.80, gilt=0.0, fox=0.06, paper_grain=1.0),
 "illuminated": dict(
    concept="Illuminated Manuscript: ground mineral pigments on vellum -- cinnabar/vermilion, lapis ultramarine, gold ochre, folium purple, minium -- with gilt hairlines tracing every inked frontier and coast.",
    pal=dict(england=[200, 56, 36], england_light=[220, 134, 116], france=[34, 50, 134], france_fam=[122, 136, 194],
             empire=[204, 154, 58], castile=[126, 60, 112], aragon=[218, 118, 58], scotland=[60, 126, 106], portugal=[68, 128, 70]),
    flanders_mix=0.62, sea=[48, 96, 82], paper=[232, 216, 178], ink=[60, 38, 28], neutral_tint=[0, 0, 0],
    relief_L=21.0, ridge_L=6.0, var_L=5.0, gran=2.0, wear=0.75, band_L=4.0, band_w=4.0, band_c=1.08,
    border_w=1.7, border_op=0.92, coast_ink=0.75, gilt=0.85, gilt_col=[222, 178, 82], fox=0.05, paper_grain=1.2),
 "campaign": dict(
    concept="Campaign Chronicle: deep earth-weight grand-strategy colours -- oxblood, slate royal blue, antique gold, plum, sienna -- on darker worn parchment with heavy umber frontiers.",
    pal=dict(england=[126, 26, 30], england_light=[166, 96, 86], france=[50, 74, 124], france_fam=[148, 162, 184],
             empire=[130, 92, 30], castile=[98, 48, 66], aragon=[164, 92, 44], scotland=[70, 88, 58], portugal=[48, 96, 92],
             flanders=[180, 172, 186]),
    flanders_mix=0.62, sea=[24, 42, 58], paper=[204, 174, 126], ink=[30, 20, 14], neutral_tint=[0, 0, 0],
    relief_L=21.0, ridge_L=6.0, var_L=5.5, gran=1.8, wear=0.75, band_L=8.0, band_w=8.0, band_c=1.04,
    border_w=2.5, border_op=1.0, coast_ink=0.90, gilt=0.0, fox=0.08, paper_grain=1.4),
}
ROUTE_P1 = {   # identical in all treatments (isolates the palette)
    "documented": dict(col=[70, 10, 14], pool=[44, 6, 8], strength=0.97, grain=0.05, key_r=4.0, key_col=[244, 236, 210]),
    "claimed":    dict(col=[94, 22, 22], pool=[70, 14, 14], strength=0.96, grain=0.07, key_r=3.2, key_col=[244, 236, 210]),
}

def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
def save(path, rgb): return A.save(path, rgb)

# ------------------------------------------------------------------------------------------ colour science
def to_lab(rgb):   # float RGB 0..255 -> CIELAB (L 0..100)
    return cv2.cvtColor(np.clip(np.float32(rgb) / 255.0, 0, 1), cv2.COLOR_RGB2LAB)
def from_lab(lab): return cv2.cvtColor(np.float32(lab), cv2.COLOR_LAB2RGB) * 255.0
def lab1(rgb): return to_lab(np.float32([[rgb]]))[0, 0].astype(np.float64)

def de2000(l1, l2):
    """CIEDE2000 between two CIELAB triples (numpy, float64)."""
    L1, a1, b1 = l1; L2, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G); C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp = L2 - L1; dCp = C2p - C1p
    if C1p * C2p == 0: dhp = 0
    else:
        dhp = h2p - h1p
        if dhp > 180: dhp -= 360
        elif dhp < -180: dhp += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2)
    Lbp = (L1 + L2) / 2; Cbp = (C1p + C2p) / 2
    if C1p * C2p == 0: hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180: hbp = (h1p + h2p) / 2
    elif h1p + h2p < 360: hbp = (h1p + h2p + 360) / 2
    else: hbp = (h1p + h2p - 360) / 2
    T = 1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp)) + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63))
    dth = 30 * math.exp(-((hbp - 275) / 25) ** 2); Rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2); Sc = 1 + 0.045 * Cbp; Sh = 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))

# ------------------------------------------------------------------------------------------ crisp partition
class Partition:
    """L (H,W) int: index into s.fams, -1 = neutral land, -2 = sea.  Drawn once (fixed seed), shared by all treatments."""
    def __init__(s, T, seed):
        rw = T.realm_weights(); H, W = T.lb.shape; rng = np.random.default_rng([seed, 501]); pn = MM.pn
        s.fams = [f for f in FAMS_ORDER if f in rw]
        st = np.stack([rw[f] for f in s.fams], 0); L0 = st.argmax(0); dom = st.max(0)
        L0 = np.where(dom > THR, L0, -1); land = T.lb > 0
        L0 = np.where(land, L0, -2)
        # pair class around every L0 boundary -> local noise amplitude
        k3 = np.ones((3, 3), np.uint8); far = 1e6
        d_line = np.full((H, W), far, np.float32); d_free = np.full((H, W), far, np.float32); d_neu = np.full((H, W), far, np.float32)
        s.pairs = {}
        for i, a in enumerate(s.fams):
            Ma = (L0 == i).astype(np.uint8)
            if Ma.sum() == 0: continue
            dil = cv2.dilate(Ma, k3) > 0
            for j, b in enumerate(s.fams):
                if j <= i: continue
                Bm = dil & (L0 == j)
                if Bm.sum() < 10: continue
                c = A.BORDER_CONF.get((a, b), A.BORDER_CONF.get((b, a), 0.0))
                d = cv2.distanceTransform((~Bm).astype(np.uint8), cv2.DIST_L2, 5)
                if c > 0: d_line = np.minimum(d_line, d)
                else: d_free = np.minimum(d_free, d)
                s.pairs[f"{a}|{b}"] = dict(conf=c, line=bool(c > 0), boundary_px=int(Bm.sum()))
            Bn = dil & (L0 == -1)
            if Bn.sum(): d_neu = np.minimum(d_neu, cv2.distanceTransform((~Bn).astype(np.uint8), cv2.DIST_L2, 5))
        g = lambda d, r: np.exp(-(d / r) ** 2)
        lomb = np.zeros((H, W), np.float32)
        for rid, pr in T.realm_meta.items():
            if pr.get("render") == "gaussian":
                lo, la = T.realm_pts[rid]; x0, y0 = T.geom.analytic(np.float64([lo]), np.float64([la]))[0]
                Y, X = np.mgrid[0:H, 0:W]; lomb = np.maximum(lomb, np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) * T.kmpp ** 2 / (2 * 160.0 ** 2)))
        wl, wf, wn = g(d_line, 14), g(d_free, 40), g(d_neu, 22)
        amp = 0.03 + 0.22 * wf + (0.09 + 0.10 * lomb) * wn
        amp = amp * (1 - wl) + 0.012 * wl          # pinned where an ink line will run
        s.amp = amp.astype(np.float32)
        sc = []
        for f in s.fams:
            n = 0.55 * pn(rng, H, W, 26, 2.0, 1.7, ax=0.6, ay=1.0) + 0.45 * pn(rng, H, W, 80, 4, 2.1)   # stipple + brush lobes
            sc.append(rw[f] + amp * n * np.clip(rw[f] / 0.15, 0, 1))        # noise only moves a realm that is present
        n0 = 0.55 * pn(rng, H, W, 26, 2.0, 1.7, ax=0.6, ay=1.0) + 0.45 * pn(rng, H, W, 80, 4, 2.1)
        sc.append(np.full((H, W), THR, np.float32) + (0.04 + (0.09 + 0.10 * lomb) * wn) * (1 - wl) * n0)
        sc = np.stack(sc, 0); L = sc.argmax(0); L = np.where(L == len(s.fams), -1, L)
        L = np.where(land, L, -2).astype(np.int16)
        # clean salt: median 3 twice on the label image (keeps hand-stipple, removes single px)
        for _ in range(2):                                                 # 3x3 MODE filter (never invents labels)
            labs = list(range(-1, len(s.fams)))
            cnt = np.stack([cv2.boxFilter((L == v).astype(np.float32), -1, (3, 3), normalize=False) for v in labs], 0)
            cnt += 0.5 * np.stack([(L == v) for v in labs], 0)               # ties keep the pixel's own label
            L = np.int16(labs)[cnt.argmax(0)]; L = np.where(land, L, -2).astype(np.int16)
        s.L = L
        # Flanders: dithered France-ish -> Empire across FLANDERS_LON (no line, no gradient)
        t = MM.smoothstep(MM.FLANDERS_LON[0], MM.FLANDERS_LON[1], T.lon)
        s.fl_emp = ((t + 0.35 * pn(rng, H, W, 14, 1.5, 1.6)) > 0.62)
        # per-feature constant strength (lower-alpha / coarse realms are a lighter tint, constant inside the realm)
        fa = np.ones((H, W), np.float32); best = np.zeros((H, W), np.float32)
        for rid, core in T._core.items():
            pr = T.realm_meta[rid]; up = core > best; fa = np.where(up, pr["alpha"], fa); best = np.maximum(best, core)
        s.feat_alpha = fa
        # ink-line geometry from the PAINTED partition (same field the pigment stops at)
        dist = np.full((H, W), far, np.float32); conf = np.zeros((H, W), np.float32)
        for i, a in enumerate(s.fams):
            dil = cv2.dilate((L == i).astype(np.uint8), k3) > 0
            for j, b in enumerate(s.fams):
                if j <= i: continue
                c = A.BORDER_CONF.get((a, b), A.BORDER_CONF.get((b, a), 0.0))
                if c <= 0: continue
                Bm = dil & (L == j) & (T.d_land > 3)
                if Bm.sum() < 20: continue
                d = cv2.distanceTransform((~Bm).astype(np.uint8), cv2.DIST_L2, 5) - 0.5
                near = d < dist; dist = np.where(near, d, dist); conf = np.where(near & (d < 6), c, conf)
        s.bdist = dist; s.bconf = cv2.GaussianBlur(conf, (0, 0), 2.0)
        # pigment edge distance (any painted -> different painted/neutral edge, on land) for the pooled-edge band
        edge = np.zeros((H, W), bool)                                     # inked frontiers + edges onto bare parchment;
        for dy, dx in ((0, 1), (1, 0)):                                     # NOT the unlined Franco-Imperial interlock
            a1 = L; a2 = np.roll(L, (-dy, -dx), (0, 1)); e = (a1 != a2) & (a1 > -2) & (a2 > -2) & ((a1 == -1) | (a2 == -1)); edge |= e
        edge |= (dist < 0.8) & (s.bconf > 0.02)
        s.d_edge = cv2.distanceTransform((~edge).astype(np.uint8), cv2.DIST_L2, 5)

    def onehot(s, k=5):
        """Painted family weights, box-averaged over k x k (what the eye sees at a checkpoint)."""
        out = {}
        for i, f in enumerate(s.fams):
            out[f] = cv2.blur((s.L == i).astype(np.float32), (k, k))
        return out

# ------------------------------------------------------------------------------------------ painter
def pigment_rgb(Pt, Pa, f, n):
    pal = Pt["pal"]
    if f == "flanders" and "flanders" in pal:
        return np.float32(pal["flanders"])
    if f == "flanders":
        c = np.float32(pal["france"]) * (1 - Pt["flanders_mix"]) + np.float32(Pt["paper"]) * Pt["flanders_mix"]
        return c
    return np.float32(pal[f])

def paint_p1(T, F, Pa, Pt, seed):
    H, W = T.lb.shape; rng = np.random.default_rng([seed, 777]); pn = MM.pn
    # parchment (shared grain fields from p0 Fields, retinted)
    paper = F.paper / np.float32([192, 150, 104]) * np.float32(Pt["paper"])
    g = 1 + 0.035 * Pt["paper_grain"] * pn(rng, H, W, 3, 0.6, 1.1)
    paper = paper * g[..., None]
    # bare land: parchment + light hypsometric relief tint (only where no realm is painted)
    olive = np.float32([150, 140, 92]); brown = np.float32([132, 96, 62]); pale = np.float32([226, 210, 176])
    bare = paper * (1 - 0.22 * F.low) + olive * 0.22 * F.low * (paper / 190.0)
    bare = bare * (1 - 0.30 * F.hi) + brown * 0.30 * F.hi; bare = bare * (1 - 0.35 * F.top) + pale * 0.35 * F.top
    bare = bare * (1 - 0.22 * F.ridge) + brown * 0.22 * F.ridge
    bare = bare * (1 + 0.30 * np.clip(T.hs, -1, 1))[..., None]
    # pigment coat colour per pixel
    L = Pa.L; coat = np.zeros((H, W, 3), np.float32); painted = L >= 0
    for i, f in enumerate(Pa.fams):
        m = L == i
        if not m.any(): continue
        c = pigment_rgb(Pt, Pa, f, None)
        if f == "flanders":
            ce = np.float32(Pt["pal"]["empire"]); mm = m & Pa.fl_emp; coat[m] = c; coat[mm] = ce
        else: coat[m] = c
    # lighter tint for low-alpha / coarse features, constant inside each feature (not a gradient)
    lift = np.clip((1.0 - Pa.feat_alpha) * 0.55, 0, 0.30)[..., None]
    coat = coat * (1 - lift) + np.float32(Pt["paper"]) * lift
    lab = to_lab(coat); Lc = lab[..., 0]
    # relief in L* only (hue kept): hillshade + ridges, ~25 % of the value range
    Lc += Pt["relief_L"] * np.clip(T.hs, -1, 1) + Pt["ridge_L"] * (F.ridge[..., 0] - 0.2) * -1.0
    # brush value variation + patchy laydown + granulation
    Lc += Pt["var_L"] * ((F.patch - 0.78) / 0.11) * 0.5 + Pt["var_L"] * (F.brush - 1) / 0.10 * 0.12
    Lc += Pt["gran"] * np.clip(pn(rng, H, W, 2.5, 0.6, 1.0), -2.5, 2.5)
    # pooled pigment along the realm edge (darker, a touch richer), strongest along inked borders
    band = np.exp(-Pa.d_edge / Pt["band_w"]) * painted
    Lc -= Pt["band_L"] * band
    lab[..., 1:] *= (1 + (Pt["band_c"] - 1) * band)[..., None]
    lab[..., 0] = np.clip(Lc, 0, 100)
    coat = from_lab(lab)
    # wear: chips / scuffs that expose parchment (texture, not desaturation)
    chip = np.clip((F.chip - 2.0) * 1.4, 0, 1) * Pt["wear"]
    scuff = F.scuff * Pt["wear"] * 0.4
    worn = np.clip(chip + scuff, 0, 0.85)
    a = painted.astype(np.float32) * (1 - worn)
    a *= MM.smoothstep(0.3, 2.0, T.d_land)          # pigment stops at the coast ink
    a = a[..., None]
    land = bare * (1 - a) + coat * a
    rim = np.exp(-T.d_land / 2.5)[..., None] * (1 - a); land = land * (1 - 0.25 * rim) + pale * 0.25 * rim
    rel = F.sea / np.float32([52, 86, 98]); sea = (1 + 0.5 * (rel - 1)) * np.float32(Pt["sea"])   # calmer mottling
    al = T.land[..., None]; img = sea * (1 - al) + land * al
    riv = np.float32(Pt["sea"]) * 0.75 + np.float32([20, 20, 24])
    for m, kk in ((T.riv_major, 0.55), (T.riv_minor, 0.25)):
        img = img * (1 - kk * m[..., None]) + riv * kk * m[..., None]
    ew = T.edge * F.coast_w; ink = np.float32(Pt["ink"])
    if Pt.get("gilt", 0) > 0:   # gilt hairline just inland of the coast ink, only where the land is painted
        gl = np.exp(-((T.d_land - 2.4) / 1.1) ** 2) * T.land * (Pa.L >= 0) * Pt["gilt"] * 0.9
        gc = np.float32(Pt["gilt_col"]) * (1 + 0.10 * F.chip)[..., None]
        img = img * (1 - gl[..., None]) + gc * gl[..., None]
    img = img * (1 - Pt["coast_ink"] * ew[..., None]) + ink * Pt["coast_ink"] * ew[..., None]
    img *= (1 - Pt["fox"] * F.fox)[..., None]; img *= F.tooth[..., None]
    return np.clip(img, 0, 255).astype(np.float32)

def border_alpha_p1(Pa, F, Pt, T, label_mask=None):
    w = Pt["border_w"] * (1 + 0.20 * np.clip(F.border_wob, -1.5, 1.5))
    a = (1 - A.smooth(w * 0.5 - 0.55, w * 0.5 + 0.55, Pa.bdist)) * np.clip(0.45 + 0.55 * Pa.bconf / 0.75, 0, 1) * (Pa.bconf > 0.02)
    a *= np.clip(0.80 + 0.25 * F.border_break, 0.40, 1.0) * (1 + 0.10 * np.clip(F.ink_grain, -1.5, 1.5))
    a *= Pt["border_op"] * T.land
    if label_mask is not None: a *= (1 - label_mask)
    return np.clip(a, 0, 1).astype(np.float32)

def gilt_alpha(Pa, F, Pt, ba):
    """Illuminated only: gold hairline running alongside each inked frontier (both sides, 1 px off the ink)."""
    off = Pt["border_w"] * 0.5 + 1.1
    g = np.exp(-((Pa.bdist - off) / 0.85) ** 2) * (Pa.bconf > 0.02) * Pt["gilt"]
    g *= np.clip(0.75 + 0.3 * F.border_break, 0.3, 1.0)
    return np.clip(g * (1 - ba), 0, 1).astype(np.float32)

# ------------------------------------------------------------------------------------------ shot
class AtlasShotP1(B.AtlasShotB):
    def __init__(s, cfg_path):
        super().__init__(cfg_path)
        s.Pa = Partition(s.T, s.cfg["seed"])
        H, W = s.T.lb.shape; s.key = {}
        for st, R in ROUTE_P1.items():   # keyline footprint = dilated ink (per dash: gaps stay gaps)
            r = R["key_r"]; k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * math.ceil(r) + 1),) * 2)
            a = s.alpha[st]; d = cv2.distanceTransform((a < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
            s.key[st] = np.clip(r + 0.6 - d, 0, 1).astype(np.float32) * (cv2.dilate((a > 0.05).astype(np.uint8), k) > 0)
        s.LP = dict(label_region_alpha=1.0, label_place_alpha=1.0, label_halo=0.85)

    def basemap(s, name):
        Pt = TREAT[name]; T, F = s.T, s.F
        img = paint_p1(T, F, s.Pa, Pt, s.cfg["seed"])
        ba = border_alpha_p1(s.Pa, F, Pt, T, s.label_mask)
        if Pt.get("gilt", 0) > 0:
            ga = gilt_alpha(s.Pa, F, Pt, ba) * (1 - s.label_mask)
            gc = np.float32(Pt["gilt_col"]) * (1 + 0.10 * F.chip)[..., None]
            img = img * (1 - ga[..., None]) + gc * ga[..., None]
        img = img * (1 - ba[..., None]) + np.float32(Pt["ink"]) * ba[..., None]
        return img, ba

    def ink_route(s, img):
        T, F = s.T, s.F; H, W = T.lb.shape; ink_a = np.zeros((H, W), np.float32)
        lum = R2.rel_lum(cv2.GaussianBlur(img, (0, 0), 4.0))
        for st in ("claimed", "documented"):
            R = ROUTE_P1[st]; k = cv2.GaussianBlur(s.key[st], (0, 0), 0.6)
            op = np.clip(1.0 - 0.55 * MM.smoothstep(0.40, 0.65, lum), 0.45, 1.0)   # adaptive: strong on dark ground
            kk = (k * op)[..., None]; img = img * (1 - kk) + np.float32(R["key_col"]) * (1 + 0.03 * F.ink_grain)[..., None] * kk
        for st in ("claimed", "documented"):
            R = ROUTE_P1[st]; alpha = s.alpha[st]
            core = cv2.GaussianBlur(alpha, (0, 0), 0.6)
            grain = 1 + R["grain"] * np.clip(F.ink_grain, -1.5, 1.5) * (0.7 + 0.3 * np.clip(F.ink_fibre, -1, 1))
            a = np.clip(core ** 0.9 * R["strength"] * grain, 0, 0.97)
            edge = np.clip((alpha - cv2.GaussianBlur(alpha, (0, 0), 1.2)) * 2.5, 0, 1)
            col = np.float32(R["col"]) * (1 - edge[..., None] * 0.5) + np.float32(R["pool"]) * edge[..., None] * 0.5
            img = img * (1 - a[..., None]) + col * a[..., None]; ink_a = np.maximum(ink_a, a)
        return img, ink_a

    def render(s, name, routes=True):
        mapimg, ba = s.basemap(name); img = mapimg.copy(); ink_a = np.zeros_like(ba)
        if routes: img, ink_a = s.ink_route(img)
        inked = img.copy()
        s.draw_labels(img, s.LP)
        out = cv2.resize(np.clip(img + 0.5, 0, 255).astype(np.uint8), tuple(s.cfg["out_wh"]), interpolation=cv2.INTER_AREA)
        return out, dict(mapimg=mapimg, inked=inked, ba=ba, ink_a=ink_a, plate=img)

# ------------------------------------------------------------------------------------------ metrics
def de2000_v(l1, l2):
    """Vectorised CIEDE2000; l1, l2 (...,3) CIELAB float64."""
    L1, a1, b1 = l1[..., 0], l1[..., 1], l1[..., 2]; L2, a2, b2 = l2[..., 0], l2[..., 1], l2[..., 2]
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cb ** 7 / (Cb ** 7 + 25.0 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G); C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360; h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dLp = L2 - L1; dCp = C2p - C1p; dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh)); dh = np.where(C1p * C2p == 0, 0, dh)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh) / 2)
    Lbp = (L1 + L2) / 2; Cbp = (C1p + C2p) / 2; hs = h1p + h2p
    hbp = np.where(np.abs(h1p - h2p) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)); hbp = np.where(C1p * C2p == 0, hs, hbp)
    T = 1 - 0.17 * np.cos(np.radians(hbp - 30)) + 0.24 * np.cos(np.radians(2 * hbp)) + 0.32 * np.cos(np.radians(3 * hbp + 6)) - 0.20 * np.cos(np.radians(4 * hbp - 63))
    dth = 30 * np.exp(-((hbp - 275) / 25) ** 2); Rc = 2 * np.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / np.sqrt(20 + (Lbp - 50) ** 2); Sc = 1 + 0.045 * Cbp; Sh = 1 + 0.015 * Cbp * T
    Rt = -np.sin(np.radians(2 * dth)) * Rc
    return np.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))

def region_name(S, xi, yi):
    if S.T.lb[yi, xi] == 0: return "sea"
    v = int(S.Pa.L[yi, xi]); return "parchment(unpainted)" if v < 0 else S.Pa.fams[v]

def phone_contrast_p1(S, inked, mapimg, f, x_range=None):
    """Dash-only, phone-scale (f = phone px per plate px).  Per sample (inside a dash: leg alpha > 0.6 here and +-2 px):
    core = 25th pct lum in |d| <= max(hw-0.3, 0.7); keyline = 75th pct lum in hw+0.4..hk-0.3 (the parchment keyline that
    touches the core); map = median lum of the raw map (no ink, no keyline) in hk+0.8..hk+3.0.  Grouped by the realm
    painted under the sample.  line_vs_map = max(core_vs_map, keyline_vs_map): the better of the two edges the eye uses."""
    H, W = inked.shape[:2]; sz = (int(round(W * f)), int(round(H * f)))
    I = cv2.resize(inked, sz, interpolation=cv2.INTER_AREA); M = cv2.resize(mapimg, sz, interpolation=cv2.INTER_AREA)
    LI, LM = R2.rel_lum(I), R2.rel_lum(M)
    anyk = cv2.resize(np.maximum(S.key["documented"], S.key["claimed"]), sz, interpolation=cv2.INTER_AREA)
    acc = {}
    for li, lg in enumerate(S.legs):
        st = lg["style"]; R = ROUTE_P1[st]; af = S.leg_alpha[li]; Q = R2.resample(lg["Pt"], 2.0)
        m = np.ones(sz[::-1], np.uint8); cv2.polylines(m, [np.int32(np.round(lg["Pt"] * f * 4))], False, 0, 1, cv2.LINE_8, shift=2)
        d = cv2.distanceTransform(m, cv2.DIST_L2, 5); hw = lg["w0"] * f / 2; hk = (lg["w0"] / 2 + R["key_r"]) * f
        for k, q in enumerate(Q):
            if any(np.hypot(*(q - p["xy"])) < p["r_edge"] + 6 for p in S.pins): continue
            xi, yi = int(round(q[0])), int(round(q[1]))
            if not (0 <= xi < W and 0 <= yi < H): continue
            if x_range and not (x_range[0] <= xi < x_range[1]): continue
            nb = Q[max(0, k - 1):k + 2]
            if min(af[min(H - 1, int(round(p[1]))), min(W - 1, int(round(p[0])))] for p in nb) < 0.6: continue
            X, Y = int(round(q[0] * f)), int(round(q[1] * f)); r = int(hk + 5)
            y0, x0 = max(0, Y - r), max(0, X - r); y1, x1 = Y + r + 1, X + r + 1
            dd = d[y0:y1, x0:x1]
            core = dd <= max(hw - 0.3, 0.7); key = (dd >= hw + 0.4) & (dd <= hk - 0.3)
            ring = (dd >= hk + 0.8) & (dd <= hk + 3.0) & (anyk[y0:y1, x0:x1] < 0.03)
            if core.sum() < 2 or key.sum() < 2 or ring.sum() < 3: continue
            lc = float(np.percentile(LI[y0:y1, x0:x1][core], 25)); lk = float(np.percentile(LI[y0:y1, x0:x1][key], 75))
            lm = float(np.median(LM[y0:y1, x0:x1][ring]))
            rn = region_name(S, xi, yi); e = acc.setdefault((st, rn), dict(ck=[], cm=[], km=[], lm=[], legs=set()))
            e["ck"].append(R2.wcag(lc, lk)); e["cm"].append(R2.wcag(lc, lm)); e["km"].append(R2.wcag(lk, lm))
            e["lm"].append(max(R2.wcag(lc, lm), R2.wcag(lk, lm))); e["legs"].add(f"{lg['a']['row']}->{lg['b']['row']}")
    out = []
    for (st, rn), e in sorted(acc.items()):
        row = dict(style=st, realm=rn, n=len(e["ck"]), legs=sorted(e["legs"]))
        for k, nm in (("ck", "core_vs_keyline"), ("cm", "core_vs_pigment"), ("km", "keyline_vs_pigment"), ("lm", "line_vs_pigment")):
            v = np.array(e[k]); row[nm] = dict(median=round(float(np.median(v)), 2), p10=round(float(np.percentile(v, 10)), 2), min=round(float(v.min()), 2))
        row["pass_3to1_p10"] = bool(row["core_vs_keyline"]["p10"] >= 3 and row["line_vs_pigment"]["p10"] >= 3)
        out.append(row)
    return out

def realm_separability(S, mapimg, ba):
    """CIEDE2000 between neighbouring painted realms on the rendered map (no route): median CIELAB of each side, sampled
    3..14 plate px from the shared boundary, off border ink and coast.  Also each realm vs sea / bare parchment."""
    T, Pa = S.T, S.Pa; lab = to_lab(mapimg).astype(np.float64); L = Pa.L
    ok = (ba < 0.05) & (T.d_land > 3)
    regs = {f: (L == i) for i, f in enumerate(Pa.fams)}; regs["parchment(unpainted)"] = (L == -1); regs["sea"] = (T.lb == 0)
    dist = {k: cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 5) for k, m in regs.items() if m.any()}
    k3 = np.ones((3, 3), np.uint8); out = []
    names = list(dist)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a == "sea" and b == "parchment(unpainted)": continue
            shared = int(((cv2.dilate(regs[a].astype(np.uint8), k3) > 0) & regs[b]).sum())
            if shared < 40: continue
            okk = ok if "sea" not in (a, b) else (ba < 0.05)
            sa = regs[a] & (dist[b] >= 3) & (dist[b] <= 14); sb = regs[b] & (dist[a] >= 3) & (dist[a] <= 14)
            if a != "sea": sa &= okk
            if b != "sea": sb &= okk
            if sa.sum() < 30 or sb.sum() < 30: continue
            ma, mb = np.median(lab[sa], 0), np.median(lab[sb], 0)
            line = A.BORDER_CONF.get((a, b), A.BORDER_CONF.get((b, a), None))
            out.append(dict(a=a, b=b, shared_boundary_px=shared, ink_line=(bool(line) if line is not None else False),
                            dE00=round(float(de2000_v(ma, mb)), 1), lab_a=[round(float(v), 1) for v in ma], lab_b=[round(float(v), 1) for v in mb]))
    return out

def within_realm_spread(S, mapimg):
    """Texture + relief variation inside each realm: CIEDE2000 of pixels vs the realm median (p50, p90)."""
    lab = to_lab(mapimg).astype(np.float64); rng = np.random.default_rng(5); out = {}
    for i, f in enumerate(S.Pa.fams):
        m = (S.Pa.L == i) & (S.T.d_land > 4)
        ys, xs = np.nonzero(m)
        if len(ys) < 200: continue
        sel = rng.choice(len(ys), min(20000, len(ys)), replace=False); px = lab[ys[sel], xs[sel]]; med = np.median(px, 0)
        dv = de2000_v(px, med[None, :]); out[f] = dict(n_px=int(m.sum()), dE00_p50=round(float(np.percentile(dv, 50)), 1), dE00_p90=round(float(np.percentile(dv, 90)), 1),
                                                       median_rgb=[int(round(v)) for v in from_lab(np.float32([[med]]))[0, 0]])
    return out
