"""Layered cartography renderer. Recipe (YAML) -> frames. Layers, bottom to top:
 base (owner's painted map, untouched) -> tactical (route_reveal, marker; drawn on a 3x supersampled mask => smooth width/position under camera moves)
 -> annotation (label, compass, caption; subpixel-placed sprites) -> fx (focus, vignette).  Camera (camera_move) is a pure function of time.
All timing comes from recipe 'at' specs: seconds | {word, occ, edge, offset} (VO alignment words) | {after: event_id, gap}."""
import os, re, json, math, time
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

class RecipeError(ValueError):
    pass

PRIMS = {"camera_move", "route_reveal", "marker", "label", "compass", "focus", "vignette"}
FONT_DIRS = ["/usr/share/fonts/truetype/sand-box/google/IBM Plex Serif/", "/usr/share/fonts/truetype/dejavu/"]
FONTS = {"bold": ["IBMPlexSerif-SemiBold.ttf", "DejaVuSerif-Bold.ttf"], "italic": ["IBMPlexSerif-MediumItalic.ttf", "DejaVuSerif-Italic.ttf"]}

def font(kind, size):
    for d in FONT_DIRS:
        for f in FONTS[kind]:
            if os.path.exists(d + f): return ImageFont.truetype(d + f, int(size))
    return ImageFont.load_default()

def hexbgr(h): h = h.lstrip("#"); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
def smoother(x): x = np.clip(x, 0.0, 1.0); return x * x * x * (x * (x * 6 - 15) + 10)
def ease(name, x):
    x = float(np.clip(x, 0, 1))
    return {"linear": x, "inout": float(smoother(x)), "out": 1 - (1 - x) ** 3, "in": x ** 3}[name]

# ---------------------------------------------------------------- timing
def load_words(path):
    d = json.load(open(path)); out = []; cur = ""; st = 0.0; pe = 0.0
    for ch, a, b in zip(d["characters"], d["character_start_times_seconds"], d["character_end_times_seconds"]):
        if ch in " \n":
            if cur: out.append((cur, st, pe)); cur = ""
        else:
            if not cur: st = a
            cur += ch; pe = b
    if cur: out.append((cur, st, pe))
    return out

def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())

class Timing:
    def __init__(self, words, offset): self.words, self.offset, self.ends = words, offset, {}
    def word(self, word, occ=1, edge="start"):
        k = 0
        for w, a, b in self.words:
            if norm(w) == norm(word):
                k += 1
                if k == occ: return (a if edge == "start" else b) - self.offset
        raise RecipeError(f"word '{word}' (occurrence {occ}) not in alignment")
    def resolve(self, at, ev_end=None, default=None):
        if at is None: return default
        if isinstance(at, (int, float)): return float(at)
        if "word" in at: return self.word(at["word"], at.get("occ", 1), at.get("edge", "start")) + at.get("offset", 0.0)
        if "after" in at:
            if at["after"] not in ev_end: raise RecipeError(f"'after: {at['after']}' refers to an event that is not defined earlier")
            return ev_end[at["after"]] + at.get("gap", 0.0)
        raise RecipeError(f"bad time spec {at}")

# ---------------------------------------------------------------- recipe
def validate(R):
    for k in ("output", "base", "locations", "events"):
        if k not in R: raise RecipeError(f"missing '{k}'")
    ids = set()
    for e in R["events"]:
        if e.get("do") not in PRIMS: raise RecipeError(f"unknown primitive {e.get('do')!r}")
        if "id" in e:
            if e["id"] in ids: raise RecipeError(f"duplicate id {e['id']}")
            ids.add(e["id"])
    def loc(x, where):
        if isinstance(x, str) and x not in R["locations"]: raise RecipeError(f"{where}: unknown location '{x}'")
    for e in R["events"]:
        for k in ("from", "to", "at_loc", "center", "anchor"):
            if k in e and isinstance(e[k], str): loc(e[k], e.get("id", e["do"]))
        if e["do"] == "camera_move" and isinstance(e.get("to"), dict) and isinstance(e["to"].get("center"), str): loc(e["to"]["center"], "camera_move")
    return R

class Recipe:
    def __init__(self, R, root, vo_dir=None):
        self.R = validate(R); self.root = root
        o = R["output"]; self.W, self.H = o["size"]; self.fps = o.get("fps", 30); self.dur = o["duration"]
        self.loc = {k: np.array(v, np.float64) for k, v in R["locations"].items()}
        self.S = {"ink": hexbgr(R.get("style", {}).get("ink", "#24160c")), "ivory": hexbgr(R.get("style", {}).get("ivory", "#f4e8cb")),
                  "plate": hexbgr(R.get("style", {}).get("plate", "#1d130b"))}
        words = []; off = 0.0
        if "vo" in R:
            ap = R["vo"]["alignment"]; ap = ap if os.path.isabs(ap) else os.path.join(vo_dir or root, ap)
            if not os.path.exists(ap): raise RecipeError(f"VO alignment not found: {ap} (pass --vo-dir)")
            words = load_words(ap); off = R["vo"].get("offset_s", 0.0)
        self.timing = Timing(words, off); self.ev = []; ends = {}
        for e in R["events"]:
            t0 = self.timing.resolve(e.get("at"), ends, 0.0); d = float(e.get("dur", e.get("in", 0.5)))
            if e["do"] in ("label", "marker", "compass", "vignette", "focus") and "until" in e: tend = self.timing.resolve(e["until"], ends)
            else: tend = None
            e2 = dict(e); e2["t0"] = t0; e2["t1"] = t0 + d; e2["tend"] = tend
            self.ev.append(e2)
            if "id" in e: ends[e["id"]] = t0 + d
        moves = sorted([e for e in self.ev if e["do"] == "camera_move"], key=lambda e: e["t0"])
        for a, b in zip(moves, moves[1:]):
            if b["t0"] < a["t1"] - 1e-6: raise RecipeError(f"camera moves overlap: '{a.get('id')}' ends {a['t1']:.2f} > next start {b['t0']:.2f}")
        self.moves = moves

    def p(self, x):
        return self.loc[x] if isinstance(x, str) else np.array(x, np.float64)

# ---------------------------------------------------------------- camera
def camera_state(rc, t):
    c0 = rc.R.get("camera", {}); c = rc.p(c0.get("center", [0.5 * rc.base_w, 0.5 * rc.base_h])); z = float(c0.get("zoom", 1.0))
    for m in rc.moves:
        tgt = m["to"]; tc = rc.p(tgt["center"]) if "center" in tgt else c; tz = float(tgt.get("zoom", z))
        if t >= m["t1"]: c, z = tc, tz; continue
        if t > m["t0"]:
            e = ease(m.get("ease", "inout"), (t - m["t0"]) / max(m["t1"] - m["t0"], 1e-6))
            c = c + (tc - c) * e; z = math.exp(math.log(z) + (math.log(tz) - math.log(z)) * e)
        break
    return clamp_camera(rc, c, z)

def clamp_camera(rc, c, z):
    s = rc.cover; vw, vh = rc.W / (s * z), rc.H / (s * z)
    cx = min(max(c[0], vw / 2), rc.base_w - vw / 2) if vw < rc.base_w else rc.base_w / 2
    cy = min(max(c[1], vh / 2), rc.base_h - vh / 2) if vh < rc.base_h else rc.base_h / 2
    return np.array([cx, cy]), z

# ---------------------------------------------------------------- geometry
def catmull(pts, n=240):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for u in np.linspace(0, 1, n // max(len(pts) - 1, 1), endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    out.append(pts[-1]); return np.array(out)

class Route:
    def __init__(self, rc, e, seed):
        a, b = rc.p(e["from"]), rc.p(e["to"]); via = [rc.p(v) for v in e.get("via", [])]
        pts = [a] + via + [b]
        if not via and e.get("bow", 0):                      # simple bow: perpendicular offset of the midpoint
            d = b - a; nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9); pts = [a, (a + b) / 2 + nrm * e["bow"] * np.linalg.norm(d), b]
        self.pts = catmull(pts)
        rng = np.random.default_rng(int(seed * 100)); w = float(e.get("wobble_px", 1.6))       # hand-drawn wobble, fixed in map space (no temporal jitter)
        if w > 0:
            n = len(self.pts); ph = rng.uniform(0, 6.28, 2); tt = np.linspace(0, 1, n)
            nm = np.gradient(self.pts, axis=0); nm = np.stack([-nm[:, 1], nm[:, 0]], 1); nm /= (np.linalg.norm(nm, axis=1, keepdims=True) + 1e-9)
            off = w * (np.sin(tt * 17 + ph[0]) * .6 + np.sin(tt * 41 + ph[1]) * .4) * np.sqrt(np.sin(np.pi * tt))
            self.pts = self.pts + nm * off[:, None]
        seg = np.linalg.norm(np.diff(self.pts, axis=0), axis=1); self.s = np.concatenate([[0], np.cumsum(seg)]); self.L = self.s[-1]
        self.dash, self.gap = float(e.get("dash", 24)), float(e.get("gap", 15)); self.width = float(e.get("width", 5.0))
        self.seed = seed
    def at(self, s):
        return np.array([np.interp(s, self.s, self.pts[:, 0]), np.interp(s, self.s, self.pts[:, 1])])
    def dashes(self, s_head):
        """list of polylines (map px) for visible dashes, pattern fixed to arc length (no crawling)."""
        out = []; per = self.dash + self.gap; k = 0
        while k * per < min(s_head, self.L):
            a = k * per; b = min(a + self.dash, s_head, self.L)
            if b - a > 0.8:
                m = (self.s >= a) & (self.s <= b); seg = [self.at(a)] + [p for p in self.pts[m]] + [self.at(b)]
                # ink pressure: width factor per dash, deterministic
                f = 0.86 + 0.28 * ((math.sin(k * 12.9898 + self.seed) * 43758.5453) % 1.0)
                out.append((np.array(seg), f))
            k += 1
        return out

# ---------------------------------------------------------------- sprites
def text_plate(lines, scale, style):
    """premultiplied BGRA float sprite: ivory serif on dark ink plate. lines: [(text, kind, size)]"""
    SS = 3; pad = int(14 * scale); gap = int(6 * scale)
    fs = [(t, k, sz * scale) for t, k, sz in lines]
    d0 = ImageDraw.Draw(Image.new("L", (4, 4))); bx = [d0.textbbox((0, 0), t, font=font(k, sz)) for t, k, sz in fs]
    w = max(b[2] for b in bx) + 2 * pad; h = sum(b[3] - b[1] for b in bx) + pad * 2 + gap * (len(fs) - 1)
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    iv = tuple(int(v) for v in style["ivory"][::-1]); pl = tuple(int(v) for v in style["plate"][::-1])
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=int(9 * scale * SS), fill=(*pl, 214), outline=(*iv, 150), width=SS * 2)
    y = pad
    for (t, k, sz), b in zip(fs, bx):
        d.text((pad * SS, (y - b[1]) * SS), t, font=font(k, sz * SS), fill=(*iv, 255)); y += b[3] - b[1] + gap
    im = im.resize((w, h), Image.LANCZOS); a = np.asarray(im).astype(np.float32) / 255.0
    return np.dstack([a[..., 2::-1] * a[..., 3:4] * 255.0, a[..., 3:4]])

def compass_sprite(size, style):
    SS = 4; n = size * SS; im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = n // 2
    iv = tuple(int(v) for v in style["ivory"][::-1]); pl = tuple(int(v) for v in style["plate"][::-1])
    d.ellipse([2, 2, n - 3, n - 3], fill=(*pl, 205), outline=(*iv, 170), width=SS * 2)
    r = c * 0.72; d.polygon([(c, c - r), (c + r * .2, c), (c, c + r * .45), (c - r * .2, c)], fill=(*iv, 255)); d.polygon([(c, c - r), (c + r * .2, c), (c, c)], fill=(*iv, 120))
    d.line([(c - r * .5, c), (c + r * .5, c)], fill=(*iv, 130), width=SS)
    f = font("bold", size * 0.2 * SS); d.text((c, c - r - size * 0.01 * SS), "N", font=f, fill=(*iv, 255), anchor="mb")
    im = im.resize((size, size), Image.LANCZOS); a = np.asarray(im).astype(np.float32) / 255.0
    return np.dstack([a[..., 2::-1] * a[..., 3:4] * 255.0, a[..., 3:4]])

def paste(frame, spr, x, y, alpha):
    """subpixel paste of premultiplied BGRA float sprite with alpha factor"""
    if alpha <= 0.002: return
    h, w = spr.shape[:2]; ix, iy = int(math.floor(x)), int(math.floor(y)); fx, fy = x - ix, y - iy
    M = np.float32([[1, 0, fx], [0, 1, fy]]); sp = cv2.warpAffine(spr, M, (w + 2, h + 2), flags=cv2.INTER_LINEAR)
    x0, y0 = max(ix, 0), max(iy, 0); x1, y1 = min(ix + w + 2, frame.shape[1]), min(iy + h + 2, frame.shape[0])
    if x1 <= x0 or y1 <= y0: return
    sp = sp[y0 - iy:y1 - iy, x0 - ix:x1 - ix]; a = sp[..., 3:4] * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sp[..., :3] * alpha

# ---------------------------------------------------------------- renderer
class Renderer:
    SS = 3
    def __init__(self, rc, base_path):
        self.rc = rc; R = rc.R
        if not os.path.exists(base_path): raise RecipeError(f"base map not found: {base_path} (owner-supplied, gitignored; see assets/basemaps/README.md)")
        src = cv2.imread(base_path); rc.base_h, rc.base_w = src.shape[:2]; rc.cover = max(rc.W / rc.base_w, rc.H / rc.base_h)
        self.U = 2.0 * rc.cover                                        # base cached at 2x of the 1.0-zoom output scale; sampling is then a mild downscale (no upscale seams while zooming)
        self.base = cv2.resize(src, None, fx=self.U, fy=self.U, interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        self.routes = {}; self.sprites = {}; self.rseed = 0
        for e in rc.ev:
            if e["do"] == "route_reveal": self.rseed += 1; self.routes[e["id"]] = Route(rc, e, self.rseed * 7.31)
            if e["do"] == "label":
                lines = [(e["text"], "bold", e.get("size", 40))] + ([(e["sub"], "italic", e.get("sub_size", 28))] if "sub" in e else [])
                self.sprites[id(e)] = text_plate(lines, rc.W / 1080.0, rc.S)
            if e["do"] == "compass": self.sprites[id(e)] = compass_sprite(int(e.get("size", 120) * rc.W / 1080), rc.S)
        vg = R.get("vignette_default", 0.0)
        yy, xx = np.mgrid[0:rc.H, 0:rc.W].astype(np.float32); r = np.sqrt(((xx / rc.W - .5) * 1.0) ** 2 + ((yy / rc.H - .5) * 0.56) ** 2) / 0.5
        self.vig = np.clip(1 - 0.32 * np.clip(r - 0.55, 0, 1) ** 1.6 * 2.2, 0.55, 1.0)[..., None].astype(np.float32)
        self.yy, self.xx = yy, xx

    def to_screen(self, p, c, z):
        k = self.rc.cover * z; return (np.asarray(p, np.float64) - c) * k + np.array([self.rc.W / 2, self.rc.H / 2])

    def frame(self, t):
        rc = self.rc; W, H = rc.W, rc.H; c, z = camera_state(rc, t); k = rc.cover * z
        # base: screen = (k/U) * (q - c*U) + ctr, q in base px
        sc = k / self.U; M = np.float32([[sc, 0, W / 2 - sc * c[0] * self.U], [0, sc, H / 2 - sc * c[1] * self.U]])
        img = cv2.warpAffine(self.base, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        SS = self.SS; under = None; ink = None
        def canv():
            return np.zeros((H * SS, W * SS), np.uint8)
        def ss(pt): return (int(round(pt[0] * SS * 16)), int(round(pt[1] * SS * 16)))
        marks = []; labels = []
        for e in rc.ev:
            if t < e["t0"] and e["do"] != "route_reveal": continue
            if e["do"] == "route_reveal" and t >= e["t0"]:
                R_ = self.routes[e["id"]]; u = ease(e.get("ease", "inout"), (t - e["t0"]) / max(e["dur"], 1e-6)); sh = u * R_.L
                rest = e.get("rest_opacity", 1.0); fade = 1.0 if u < 1 else 1.0 - (1 - rest) * float(smoother((t - e["t1"]) / 0.8))
                if under is None: under, ink = canv(), canv()
                lw = R_.width * k * SS
                for seg, f in R_.dashes(sh):
                    P = np.array([ss(self.to_screen(p, c, z)) for p in seg], np.int32).reshape(-1, 1, 2)
                    cv2.polylines(under, [P], False, int(255 * fade), max(1, int(round(lw * f + 5.5 * SS * z ** 0.5))), cv2.LINE_AA, 4)
                    cv2.polylines(ink, [P], False, int(255 * fade), max(1, int(round(lw * f))), cv2.LINE_AA, 4)
                if u < 1 and e.get("head"):                     # moving marker at the head (army token)
                    hp = ss(self.to_screen(R_.at(sh), c, z)); r = 9.5 * k * SS
                    cv2.circle(under, hp, int(r * 16 + 3.4 * SS * 16), 255, -1, cv2.LINE_AA, 4); cv2.circle(ink, hp, int(r * 16), 255, -1, cv2.LINE_AA, 4)
                    cv2.circle(under, hp, int(r * 0.38 * 16), 0, -1, cv2.LINE_AA, 4); cv2.circle(ink, hp, int(r * 0.38 * 16), 0, -1, cv2.LINE_AA, 4)
                    marks.append(("headdot", hp))
            elif e["do"] == "marker":
                a = float(smoother((t - e["t0"]) / 0.35))
                if e.get("tend") is not None and t > e["tend"]: a *= 1 - float(smoother((t - e["tend"]) / 0.4))
                if under is None: under, ink = canv(), canv()
                sp = ss(self.to_screen(rc.p(e["at_loc"]), c, z)); r = float(e.get("r", 13)) * k * SS
                cv2.circle(under, sp, int(r * 16), int(255 * a), max(1, int(round(6.8 * SS * z ** .5))), cv2.LINE_AA, 4)
                cv2.circle(ink, sp, int(r * 16), int(255 * a), max(1, int(round(3.4 * SS * z ** .5))), cv2.LINE_AA, 4)
                pt = (t - e["t0"]) / float(e.get("pulse_s", 1.3))
                if e.get("pulse", True) and 0 <= pt < 1:        # expanding ink ring
                    pr = r * (1 + 2.6 * ease("out", pt)); pa = int(255 * (1 - pt) ** 1.5 * 0.9)
                    cv2.circle(under, sp, int(pr * 16), pa, max(1, int(round(5.6 * SS))), cv2.LINE_AA, 4); cv2.circle(ink, sp, int(pr * 16), pa, max(1, int(round(2.6 * SS))), cv2.LINE_AA, 4)
            elif e["do"] in ("label", "compass"):
                labels.append(e)
        if under is not None:
            ua = cv2.resize(under, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255.0
            ia = cv2.resize(ink, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32)[..., None] / 255.0
            img = img * (1 - 0.82 * ua) + rc.S["ivory"] * 0.82 * ua
            img = img * (1 - 0.94 * ia) + rc.S["ink"] * 0.94 * ia
        # fx: focus (dim outside a soft circle around a point)
        for e in rc.ev:
            if e["do"] == "focus" and t >= e["t0"]:
                a = float(smoother((t - e["t0"]) / max(e["dur"], 1e-6))) * float(e.get("strength", 0.35))
                if e.get("tend") is not None and t > e["tend"]: a *= 1 - float(smoother((t - e["tend"]) / 0.8))
                sp = self.to_screen(rc.p(e["center"]), c, z); rad = float(e.get("radius", 260)) * k
                d = np.sqrt((self.xx - sp[0]) ** 2 + (self.yy - sp[1]) ** 2) / rad; m = np.clip((d - 0.7) / 0.9, 0, 1)[..., None]
                m = m * m * (3 - 2 * m); img = img * (1 - a * m)
        img = img * (self.vig ** float(rc.R.get("vignette", 1.0)))
        for e in labels:                                              # annotation layer on top of fx
            if t < e["t0"]: continue
            inn = float(smoother((t - e["t0"]) / 0.45)); a = inn
            if e.get("tend") is not None and t > e["tend"]: a *= 1 - float(smoother((t - e["tend"]) / 0.45))
            spr = self.sprites[id(e)]; h, w = spr.shape[:2]
            if e["do"] == "compass": pos = np.array([e["screen"][0] * W - w / 2, e["screen"][1] * H - h / 2]); paste(img, spr, pos[0], pos[1], a); continue
            if "screen" in e:
                pos = np.array([e["screen"][0] * W - w / 2, e["screen"][1] * H - h / 2 + (1 - inn) * 14])
            else:
                sp = self.to_screen(rc.p(e["anchor"]), c, z); dx, dy = e.get("offset", [0, 60])
                pos = sp + np.array([dx * W / 1080 - (w / 2 if e.get("center", True) else 0), dy * W / 1080 - h / 2 + (1 - inn) * 10])
            pos[1] = float(np.clip(pos[1], 0.145 * H, 0.78 * H - h)) if "screen" not in e else pos[1]; pos[0] = float(np.clip(pos[0], 0.03 * W, 0.97 * W - w))
            paste(img, spr, pos[0], pos[1], a)
        return np.clip(img, 0, 255).astype(np.uint8)[..., ::-1].copy()      # BGR->RGB for the writer

    def duration_frames(self): return int(round(self.rc.dur * self.rc.fps))
