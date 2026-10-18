"""Narration-aware storyboard checks for cartography recipes (schema 2).  Pipeline:  Vellum narrative intent -> Archivist historical verification -> structured
storyboard (this YAML) -> renderer.  These checks validate STRUCTURE, TIMING and LEGIBILITY.  They do NOT check historical truth: accuracy belongs to the Archivist;
a claim's `status` (DRAFT | VERIFIED) is a human-set field that this code only reports.

Schema 2 additions (all under the recipe root):
  sources: [{id, title, url, retrieved, license}]
  claims:  [{id, text, band: DOCUMENTED|QUALIFIED|UNKNOWN, confidence: high|medium|low, approximate: bool, sources: [source ids], status: DRAFT|VERIFIED}]
  limits:  {max_labels, max_annotations, max_titles, anchor_window_s: [before, after], tail_margin_s, tail_fade_s}
  every event (except 'camera_move' purely framing 'focus'...: see ANCHORED) carries:  claim: <claim id>,  purpose: <why this geographic/historical action exists>,
        anchor: {word, occ?}  (or its `at` is a word spec),  and labels carry kind: geo | event | title and `until`.
Issues are (level, code, message); level 'error' fails CI/render, 'warning' is reported."""
import os, math
from collections import namedtuple

Issue = namedtuple("Issue", "level code msg")
BANDS = {"DOCUMENTED", "QUALIFIED", "UNKNOWN"}; CONF = {"high", "medium", "low"}; STATUS = {"DRAFT", "VERIFIED"}
KINDS = {"geo", "event", "title"}
ANCHORED = {"route_reveal", "marker", "label", "camera_move", "focus"}     # every one needs claim + purpose + narration anchor in schema 2
DEFAULT_LIMITS = dict(max_labels=3, max_annotations=4, max_titles=1, anchor_window_s=[0.7, 1.0], tail_margin_s=0.25, tail_fade_s=0.35, safe_x=[0.05, 0.95], safe_y=[0.14, 0.78], max_dominant=1)

def limits(R): d = dict(DEFAULT_LIMITS); d.update(R.get("limits", {}) or {}); return d

def anchor_spec(e):
    a = e.get("anchor_word") or e.get("anchor_at")
    if a: return a
    at = e.get("at")
    return at if isinstance(at, dict) and "word" in at else None

def static_issues(R):
    """schema-2 structure checks that need no VO alignment, map or renderer (safe for CI with synthetic assets)."""
    out = []; E = lambda c, m: out.append(Issue("error", c, m)); W = lambda c, m: out.append(Issue("warning", c, m))
    if R.get("schema", 1) != 2: return out
    src = {s.get("id"): s for s in R.get("sources", []) or []}
    if len(src) != len(R.get("sources", []) or []): E("sources.duplicate", "duplicate source id")
    for s in src.values():
        for k in ("id", "title", "retrieved", "license"):
            if not s.get(k): E("sources.field", f"source {s.get('id')!r}: missing '{k}'")
        if not (s.get("url") or s.get("ref")): E("sources.field", f"source {s.get('id')!r}: needs url or ref")
    claims = {}
    for c in R.get("claims", []) or []:
        cid = c.get("id")
        if cid in claims: E("claims.duplicate", f"duplicate claim id {cid}")
        claims[cid] = c
        if not c.get("text"): E("claims.field", f"claim {cid}: text required")
        if c.get("band") not in BANDS: E("claims.band", f"claim {cid}: band must be one of {sorted(BANDS)}")
        if c.get("confidence") not in CONF: E("claims.confidence", f"claim {cid}: confidence must be one of {sorted(CONF)}")
        if not isinstance(c.get("approximate"), bool): E("claims.approximate", f"claim {cid}: approximate must be true/false")
        if c.get("status", "DRAFT") not in STATUS: E("claims.status", f"claim {cid}: status must be DRAFT or VERIFIED")
        ss = c.get("sources") or []
        if not ss and c.get("band") != "UNKNOWN": E("claims.sources", f"claim {cid}: band {c.get('band')} needs >= 1 source id")
        for sid in ss:
            if sid not in src: E("claims.sources", f"claim {cid}: unknown source '{sid}'")
    used = set(); lim = limits(R)
    for e in R["events"]:
        who = e.get("id") or e["do"]
        if e["do"] in ANCHORED:
            if e.get("claim") not in claims: E("event.claim", f"{who}: needs claim: <id> from claims (got {e.get('claim')!r})")
            else: used.add(e["claim"])
            if not (e.get("purpose") or "").strip(): E("event.purpose", f"{who}: purpose (geographic/historical reason) required")
            if anchor_spec(e) is None: E("event.anchor", f"{who}: no narration anchor (give `at: {{word: ...}}` or `anchor_word: {{word: ...}}`)")
        if e["do"] == "label":
            if e.get("kind") not in KINDS: E("label.kind", f"{who}: kind must be one of {sorted(KINDS)}")
            if "until" not in e: W("label.until", f"{who}: label has no `until` and would stay to the end of the clip")
        if e["do"] == "compass": W("decor.compass", f"{who}: compass is decoration with no narration anchor; avoid in schema 2")
    for cid in set(claims) - used: W("claims.unused", f"claim {cid} is not used by any event")
    labels = [e for e in R["events"] if e["do"] == "label"]
    if len(labels) > lim["max_labels"] + lim["max_titles"] + 2: W("label.count", f"{len(labels)} labels in one clip (soft limit {lim['max_labels'] + lim['max_titles'] + 2}); simplify")
    unver = [c for c in claims if claims[c].get("status", "DRAFT") != "VERIFIED"]
    if unver: W("claims.unverified", f"{len(unver)} claim(s) not VERIFIED by the Archivist: {unver} -> clip is DRAFT / internal only")
    for k, v in R["locations"].items():
        if not isinstance(v, dict): W("location.hand_placed", f"location '{k}' is hand-placed pixels; use {{lonlat: [lon, lat]}} through the georef")
    return out

def timing_issues(rc, words=None):
    """checks that need resolved event times (Recipe built from the VO alignment)."""
    R = rc.R; out = []; E = lambda c, m: out.append(Issue("error", c, m)); W = lambda c, m: out.append(Issue("warning", c, m))
    if R.get("schema", 1) != 2: return out
    lim = limits(R); before, after = lim["anchor_window_s"]; T = rc.dur
    for e in rc.ev:
        who = e.get("id") or e["do"]; a = anchor_spec(e)
        if e["t0"] < -1e-6 or e["t0"] > T + 1e-6: E("time.range", f"{who}: starts at {e['t0']:.2f}s outside the clip (0..{T:.2f})")
        if e["do"] == "route_reveal" and e["t1"] > T + 1e-6: E("time.range", f"{who}: route ends {e['t1']:.2f}s after the clip end {T:.2f}s")
        if a is not None and e["do"] in ANCHORED:
            try: ta = rc.timing.word(a["word"], a.get("occ", 1), a.get("edge", "start"))
            except Exception as ex: E("anchor.word", f"{who}: anchor word not in the alignment: {ex}"); continue
            if not (ta - before <= e["t0"] <= ta + after): E("anchor.sync", f"{who}: starts {e['t0'] - ta:+.2f}s from its anchor word '{a['word']}' (allowed -{before}..+{after})")
    # conflicting camera actions
    moves = sorted([e for e in rc.ev if e["do"] == "camera_move"], key=lambda e: e["t0"])
    for a, b in zip(moves, moves[1:]):
        if b["t0"] < a["t1"] - 1e-6: E("camera.overlap", f"camera moves overlap: {a.get('id')} ends {a['t1']:.2f} > {b.get('id')} starts {b['t0']:.2f}")
        elif b["t0"] - a["t1"] < 0.25 and (a.get("to", {}).get("center") != b.get("to", {}).get("center")): W("camera.back_to_back", f"{a.get('id')} -> {b.get('id')} nearly back-to-back with a change of target (reads as a lurch)")
    # one dominant geographic action at a time (camera move or route reveal)
    dom = [(e["t0"], e["t1"], e.get("id") or e["do"]) for e in rc.ev if e["do"] in ("camera_move", "route_reveal")]
    for i in range(len(dom)):
        for j in range(i + 1, len(dom)):
            ov = min(dom[i][1], dom[j][1]) - max(dom[i][0], dom[j][0])
            if ov > 0.15: W("dominant.overlap", f"{dom[i][2]} and {dom[j][2]} overlap {ov:.2f}s (one dominant geographic action at a time)")
    # simultaneous annotations
    tl = []
    for e in rc.ev:
        if e["do"] in ("label", "marker", "focus"):
            end = e["tend"] if e.get("tend") is not None else T
            tl.append((e["t0"], end + (0.45 if e["do"] == "label" else 0.4), e))
    peak = 0; peak_t = 0; peak_l = 0; peak_title = 0
    for t in [i * 0.05 for i in range(int(T / 0.05) + 1)]:
        act = [x for (a, b, x) in tl if a <= t < b]; lab = [x for x in act if x["do"] == "label" and x.get("kind") != "title"]; ti = [x for x in act if x["do"] == "label" and x.get("kind") == "title"]
        n = len(act)
        if n > peak: peak, peak_t = n, t
        peak_l = max(peak_l, len(lab)); peak_title = max(peak_title, len(ti))
    if peak_l > lim["max_labels"]: E("annot.labels", f"{peak_l} non-title labels visible at once (max {lim['max_labels']})")
    if peak > lim["max_annotations"]: E("annot.simultaneous", f"{peak} annotations (labels+markers+focus) visible at t={peak_t:.2f}s (max {lim['max_annotations']})")
    if peak_title > lim["max_titles"]: E("annot.titles", f"{peak_title} titles at once (max {lim['max_titles']})")
    return out

def tail_plan(words, offset, dur, margin=0.25, fade=0.35, lead_fade=0.12):
    """Audio window [offset, offset+dur]. Returns dict(fade_start, fade_dur, last_word, last_end, next_word_start, ok, problems).
    The fade-out must START at/after the last included word's end + margin and END before the next word starts (nothing truncated); the window must not start or end inside a word."""
    t0, t1 = offset, offset + dur; prob = []
    inside = [w for w in words if w[1] >= t0 - 1e-6 and w[2] <= t1 + 1e-6]
    straddle = [w for w in words if (w[1] < t0 - 1e-6 < w[2]) or (w[1] < t1 - 1e-6 < w[2])]
    for w in straddle: prob.append(f"window boundary cuts the word '{w[0]}' ({w[1]:.2f}-{w[2]:.2f})")
    if not inside: return dict(ok=False, problems=prob + ["no complete words in the window"], fade_start=None, fade_dur=fade)
    last = inside[-1]; nxt = [w for w in words if w[1] >= t1 - 1e-6]; ns = nxt[0][1] if nxt else None
    fs = last[2] + margin - offset
    if fs + fade > dur + 1e-6: prob.append(f"clip too short: fade {fs:.2f}+{fade:.2f}s exceeds the clip end {dur:.2f}s (last word '{last[0]}' ends {last[2] - offset:.2f}s)")
    if ns is not None and (offset + fs + fade) > ns - 0.03: prob.append(f"fade would reach the next word '{nxt[0][0]}' (starts {ns - offset:.2f}s)")
    first = inside[0]
    if first[1] - t0 < lead_fade: prob.append(f"first word '{first[0]}' starts {first[1] - t0:.2f}s after the window start; a {lead_fade}s fade-in would clip it")
    return dict(ok=not prob, problems=prob, fade_start=round(fs, 3), fade_dur=fade, last_word=last[0], last_end=round(last[2] - offset, 3), next_word_start=None if ns is None else round(ns - offset, 3))

def render_issues(rd, step=0.1):
    """legibility checks that need the Renderer (sprite sizes + camera): labels inside caption-safe area, label overlap, route endpoints inside the map, baked-text warning."""
    rc = rd.rc; R = rc.R; out = []; E = lambda c, m: out.append(Issue("error", c, m)); W = lambda c, m: out.append(Issue("warning", c, m))
    if R.get("schema", 1) != 2: return out
    from .engine import camera_state, edge_fade
    lim = limits(R); sx, sy = lim["safe_x"], lim["safe_y"]; Wd, Hd = rc.W, rc.H
    for e in rc.ev:
        if e["do"] == "route_reveal":
            Rt = rd.routes[e["id"]]
            for p in (Rt.pts[0], Rt.pts[-1]):
                if not (0 <= p[0] <= rc.base_w and 0 <= p[1] <= rc.base_h): E("route.endpoint", f"{e['id']}: endpoint {p.round(1).tolist()} outside the map")
    bad = {}; ovl = {}
    labels = [e for e in rc.ev if e["do"] == "label"]
    for t in [i * step for i in range(int(rc.dur / step) + 1)]:
        c, z = camera_state(rc, t); rects = []
        for e in labels:
            end = (e["tend"] + 0.45) if e.get("tend") is not None else rc.dur
            if not (e["t0"] + 0.2 <= t < end - 0.2): continue
            spr = rd.sprites[id(e)]; h, w = spr.shape[:2]
            if "screen" in e: pos = (e["screen"][0] * Wd - w / 2, e["screen"][1] * Hd - h / 2); vis = 1.0
            else:
                sp = rd.to_screen(rc.p(e["anchor"]), c, z); dx, dy = e.get("offset", [0, 60]); pos = (sp[0] + dx * Wd / 1080 - (w / 2 if e.get("center", True) else 0), sp[1] + dy * Wd / 1080 - h / 2); vis = edge_fade(sp, Wd, Hd)
            if vis < 0.5: continue
            if pos[0] < sx[0] * Wd - 1 or pos[0] + w > sx[1] * Wd + 1 or pos[1] < sy[0] * Hd - 1 or pos[1] + h > sy[1] * Hd + 1: bad.setdefault(e.get("id") or e["text"], t)
            rects.append((e.get("id") or e["text"], pos[0], pos[1], pos[0] + w, pos[1] + h))
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                if min(a[3], b[3]) - max(a[1], b[1]) > 4 and min(a[4], b[4]) - max(a[2], b[2]) > 4: ovl.setdefault((a[0], b[0]), t)
    for k, t in bad.items(): E("label.safe_area", f"label {k} leaves the caption-safe area (first at t={t:.1f}s)")
    for (a, b), t in ovl.items(): E("label.overlap", f"labels {a} and {b} overlap on screen (first at t={t:.1f}s)")
    if os.path.exists(getattr(rd, "base_path", "")):
        from .cleanmap import detect_baked
        import cv2
        d = detect_baked(cv2.imread(rd.base_path))
        if d["score"] > 0: W("base.baked_text", f"base map looks like it carries baked pins/labels ({d}); use the clean base and draw annotations as layers")
    return out

def summarize(issues):
    return dict(errors=[i._asdict() for i in issues if i.level == "error"], warnings=[i._asdict() for i in issues if i.level == "warning"])
