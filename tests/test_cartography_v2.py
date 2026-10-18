"""Cartography v0.2: georeferencing, clean base map, storyboard/QC, narration tail, schema-2 recipe."""
import os, json, copy, numpy as np, cv2, pytest, yaml
from motionplates.cartography import georef as G, cleanmap as CM, storyboard as SB
from motionplates.cartography.engine import Recipe, Renderer, RecipeError, validate
HERE = os.path.dirname(__file__); ROOT = os.path.join(HERE, "..")

# ------------------------------------------------------------------ georef
def _cp(fn, pts, proj=None):
    return [dict(id=f"p{i}", lon=lo, lat=la, px=list(map(float, fn(lo, la)))) for i, (lo, la) in enumerate(pts)]
PTS = [(30, 30), (60, 30), (90, 30), (30, 55), (60, 55), (90, 55), (45, 42), (75, 42), (60, 40)]

def test_affine_fit_recovers_known_transform():
    f = lambda lo, la: (400 + 7.0 * (lo - 60) * np.cos(np.radians(40)), 800 - 9.0 * (la - 40))
    cp = _cp(f, PTS); g = G.fit(cp, (941, 1672), {"kind": "equirect", "lat0": 40, "lon0": 60}, "affine")
    assert G.residuals(g).max() < 1e-6 and np.allclose(g.to_px([70, 35]), f(70, 35), atol=1e-6)

def test_poly2_and_lcc_and_mercator_fit_and_inverse():
    for kind in ("equirect", "mercator", "lcc"):
        pr = {"kind": kind, "lat0": 40, "lon0": 60, "p1": 30, "p2": 55}
        P = G.project(np.array([c[0] for c in PTS], float), np.array([c[1] for c in PTS], float), **pr)
        cp = [dict(id=str(i), lon=lo, lat=la, px=[500 + 300 * p[0], 800 - 300 * p[1]]) for i, ((lo, la), p) in enumerate(zip(PTS, P))]
        g = G.fit(cp, (941, 1672), pr, "poly2"); assert G.residuals(g).max() < 1e-4
        ll = g.to_lonlat(g.to_px([70.0, 38.0])); assert np.allclose(ll[0], [70.0, 38.0], atol=1e-3)

def test_tps_interpolates_control_points_and_fit_needs_enough_points():
    rng = np.random.default_rng(1); cp = [dict(id=str(i), lon=lo, lat=la, px=[lo * 5 + rng.normal(0, 3), la * -6 + 900 + rng.normal(0, 3)]) for i, (lo, la) in enumerate(PTS)]
    g = G.fit(cp, (941, 1672), {"kind": "equirect"}, "tps"); assert G.residuals(g).max() < 1e-3
    with pytest.raises(ValueError): G.fit(cp[:4], (1, 1), {"kind": "equirect"}, "poly2")

def test_loo_is_worse_than_fit_residual_for_noisy_points():
    rng = np.random.default_rng(2); cp = [dict(id=str(i), lon=lo, lat=la, px=[lo * 5 + rng.normal(0, 8), -la * 6 + 900 + rng.normal(0, 8)]) for i, (lo, la) in enumerate(PTS)]
    g = G.fit(cp, (941, 1672), {"kind": "equirect"}, "affine"); lo_ = G.loo(cp, (941, 1672), {"kind": "equirect"}, "affine")
    assert np.sqrt(np.mean(np.square(lo_))) > np.sqrt(np.mean(G.residuals(g) ** 2))

def test_geodesic_and_distance_and_clip():
    assert abs(G.haversine_km((66.97583, 39.65472), (13.405, 52.52)) - 4260.4) < 1.0            # Archivist's computed Berlin-Samarkand distance
    gd = G.geodesic((66.97583, 39.65472), (13.405, 52.52), 50); assert np.allclose(gd[0], [66.97583, 39.65472], atol=1e-6) and np.allclose(gd[-1], [13.405, 52.52], atol=1e-6)
    pts = np.array([[100.0, 100.0], [10.0, 100.0], [-300.0, 100.0]]); c = G.clip_polyline_to_rect(pts, 941, 1672, 50)
    assert c[-1][0] == pytest.approx(50, abs=0.01) and (c[:, 0] >= 49.99).all()

def test_committed_georef_is_sane_for_the_tamerlane_map():
    g = G.load(os.path.join(ROOT, "assets", "georef", "tamerlane_eurasia.georef.json"))
    assert G.residuals(g).mean() < 20
    sam = g.to_px([66.97583, 39.65472]); assert np.linalg.norm(sam - np.array([583, 672])) < 30       # painter's own pin (not used in the fit) is within 30 px
    assert 0 < sam[0] < 941 and 0 < sam[1] < 1672
    cps = json.load(open(os.path.join(ROOT, "assets", "georef", "tamerlane_eurasia.control_points.json"))); assert {p["type"] for p in cps["points"]} == {"landmark", "pin"}

# ------------------------------------------------------------------ clean base map
def _baked(path=None):
    rng = np.random.default_rng(0); img = np.full((300, 400, 3), (60, 140, 190), np.uint8); img = np.clip(img + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)
    cv2.circle(img, (80, 80), 22, (40, 150, 255), -1); cv2.circle(img, (80, 80), 8, (250, 252, 255), -1)       # orange glow + white core
    cv2.rectangle(img, (110, 68), (250, 94), (30, 40, 60), -1); cv2.putText(img, "SAMARKAND", (114, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (245, 245, 245), 1, cv2.LINE_AA)
    return img

def test_detect_baked_and_remove_items_leaves_rest_untouched():
    img = _baked(); d0 = CM.detect_baked(img); assert d0["pins"] >= 1 and d0["text_components"] >= 1
    orig = img.copy(); clean, mask = CM.remove_items(img, [dict(pin=[80, 80, 8], glow=26, label=[106, 64, 254, 98])])
    assert (img == orig).all()                                                              # input never modified
    d1 = CM.detect_baked(clean); assert d1["score"] == 0, d1
    far = np.ones(img.shape[:2], bool); far[20:150, 20:290] = False
    assert np.abs(clean.astype(int) - img.astype(int))[far].max() == 0                      # nothing outside the item boxes changed

def test_remove_items_is_deterministic():
    a, _ = CM.remove_items(_baked(), [dict(pin=[80, 80, 8], glow=26, label=[106, 64, 254, 98])]); b, _ = CM.remove_items(_baked(), [dict(pin=[80, 80, 8], glow=26, label=[106, 64, 254, 98])]); assert (a == b).all()

# ------------------------------------------------------------------ recipes
WORDS = [("a", 0.2, 0.5), ("Samarkand", 1.0, 1.6), ("lay", 1.7, 1.9), ("east", 2.6, 2.9), ("Berlin.", 3.0, 3.6), ("Later", 4.4, 4.8)]

def mk(tmp_path, events=None, **kw):
    img = np.full((334, 188, 3), (70, 120, 160), np.uint8); cv2.imwrite(str(tmp_path / "base.png"), img)
    al = {"characters": [], "character_start_times_seconds": [], "character_end_times_seconds": []}
    for w, a, b in WORDS:
        for i, ch in enumerate(w): al["characters"].append(ch); al["character_start_times_seconds"].append(a + (b - a) * i / len(w)); al["character_end_times_seconds"].append(a + (b - a) * (i + 1) / len(w))
        al["characters"].append(" "); al["character_start_times_seconds"].append(b); al["character_end_times_seconds"].append(b)
    (tmp_path / "al.json").write_text(json.dumps(al))
    cp = [dict(id=str(i), lon=lo, lat=la, px=[100 + 1.6 * (lo - 40), 160 - 2.0 * (la - 40)]) for i, (lo, la) in enumerate(PTS)]
    (tmp_path / "g.json").write_text(json.dumps(dict(size=[188, 334], proj={"kind": "equirect", "lat0": 40, "lon0": 60}, warp="affine", control_points=cp)))
    R = {"schema": 2, "output": {"size": [108, 192], "fps": 10, "duration": 4.25}, "base": {"file": "base.png"}, "georef": {"file": "g.json"}, "vo": {"alignment": "al.json", "offset_s": 0.0},
         "limits": {"max_labels": 2, "max_annotations": 3},
         "sources": [{"id": "s1", "title": "t", "url": "http://x", "retrieved": "2026-10-18", "license": "PD"}],
         "claims": [{"id": "c1", "text": "x", "band": "DOCUMENTED", "confidence": "high", "approximate": False, "sources": ["s1"], "status": "DRAFT"}],
         "locations": {"a": {"lonlat": [66.9, 39.6]}, "b": {"lonlat": [50.0, 45.0]}},
         "events": events or [{"id": "m", "do": "marker", "at": {"word": "Samarkand"}, "claim": "c1", "purpose": "locate", "at_loc": "a"},
                              {"id": "l", "do": "label", "kind": "geo", "at": {"word": "Samarkand", "offset": 0.1}, "until": {"word": "east"}, "claim": "c1", "purpose": "name", "anchor": "a", "offset": [0, 40], "text": "A"}]}
    R.update(kw); return R

def build(tmp_path, R): rc = Recipe(R, str(tmp_path)); rd = Renderer(rc, str(tmp_path / "base.png")); return rc, rd
def codes(iss, level=None): return {i.code for i in iss if level is None or i.level == level}

def test_valid_schema2_recipe_has_no_errors(tmp_path):
    rc, rd = build(tmp_path, mk(tmp_path)); iss = SB.static_issues(rc.R) + SB.timing_issues(rc) + SB.render_issues(rd)
    assert not [i for i in iss if i.level == "error"], iss; assert "claims.unverified" in codes(iss)

def test_lonlat_location_requires_georef(tmp_path):
    R = mk(tmp_path); del R["georef"]
    with pytest.raises(RecipeError, match="georef"): Recipe(R, str(tmp_path))

def test_event_without_anchor_claim_or_purpose_is_an_error(tmp_path):
    R = mk(tmp_path); R["events"][0] = {"id": "m", "do": "marker", "at": 1.0, "at_loc": "a"}
    with pytest.raises(RecipeError) as ei: Recipe(R, str(tmp_path))
    for c in ("event.claim", "event.purpose", "event.anchor"): assert c in str(ei.value)

def test_unknown_source_and_bad_claim_fields(tmp_path):
    R = mk(tmp_path); R["claims"][0].update(band="MAYBE", approximate="no", sources=["zzz"], confidence="sure")
    with pytest.raises(RecipeError) as ei: Recipe(R, str(tmp_path))
    for c in ("claims.band", "claims.approximate", "claims.sources", "claims.confidence"): assert c in str(ei.value)

def test_documented_claim_needs_a_source_but_unknown_does_not(tmp_path):
    R = mk(tmp_path); R["claims"][0]["sources"] = []
    with pytest.raises(RecipeError, match="claims.sources"): Recipe(R, str(tmp_path))
    R["claims"][0]["band"] = "UNKNOWN"; Recipe(R, str(tmp_path))

def test_anchor_sync_window(tmp_path):
    R = mk(tmp_path); R["events"][0]["at"] = {"word": "Samarkand", "offset": 1.8}
    rc, rd = build(tmp_path, R); assert "anchor.sync" in codes(SB.timing_issues(rc), "error")
    R = mk(tmp_path); R["events"][0]["at"] = {"word": "Samarkand", "offset": 0.0}; R["events"][0]["anchor_word"] = {"word": "Berlin."}
    rc, rd = build(tmp_path, R); assert "anchor.sync" in codes(SB.timing_issues(rc), "error")
    R = mk(tmp_path); R["events"][0]["at"] = {"word": "nonexistent"}
    with pytest.raises(RecipeError): Recipe(R, str(tmp_path))

def test_camera_overlap_and_dominant_actions(tmp_path):
    ev = mk(tmp_path)["events"] + [
        {"id": "c1", "do": "camera_move", "at": {"word": "Samarkand"}, "dur": 1.0, "claim": "c1", "purpose": "p", "to": {"zoom": 1.2}},
        {"id": "r", "do": "route_reveal", "at": {"word": "Samarkand", "offset": 0.4}, "dur": 1.2, "claim": "c1", "purpose": "p", "from": "a", "to": "b"}]
    rc, rd = build(tmp_path, mk(tmp_path, ev)); assert "dominant.overlap" in codes(SB.timing_issues(rc), "warning")
    ev2 = mk(tmp_path)["events"] + [{"id": "c1", "do": "camera_move", "at": {"word": "Samarkand"}, "dur": 1.0, "claim": "c1", "purpose": "p", "to": {"zoom": 1.2}},
                                    {"id": "c2", "do": "camera_move", "at": {"word": "Samarkand", "offset": 0.5}, "dur": 1.0, "claim": "c1", "purpose": "p", "to": {"zoom": 1.4}}]
    with pytest.raises(RecipeError, match="camera moves overlap"): Recipe(mk(tmp_path, ev2), str(tmp_path))

def test_too_many_simultaneous_annotations(tmp_path):
    ev = mk(tmp_path)["events"] + [{"id": f"x{i}", "do": "label", "kind": "geo", "at": {"word": "Samarkand", "offset": 0.1}, "until": {"word": "east"}, "claim": "c1", "purpose": "p", "anchor": "b", "offset": [0, 30 * i], "text": f"L{i}"} for i in range(3)]
    rc, rd = build(tmp_path, mk(tmp_path, ev)); c = codes(SB.timing_issues(rc), "error"); assert "annot.labels" in c and "annot.simultaneous" in c

def test_label_overlap_and_safe_area_detected(tmp_path):
    ev = mk(tmp_path)["events"] + [{"id": "y", "do": "label", "kind": "geo", "at": {"word": "Samarkand", "offset": 0.1}, "until": {"word": "east"}, "claim": "c1", "purpose": "p", "anchor": "a", "offset": [0, 40], "text": "A"}]
    rc, rd = build(tmp_path, mk(tmp_path, ev)); assert "label.overlap" in codes(SB.render_issues(rd), "error")
    ev = [mk(tmp_path)["events"][0], {"id": "l", "do": "label", "kind": "title", "at": {"word": "Samarkand", "offset": 0.1}, "until": {"word": "east"}, "claim": "c1", "purpose": "p", "text": "T", "screen": [0.5, 0.02]}]
    rc, rd = build(tmp_path, mk(tmp_path, ev)); assert "label.safe_area" in codes(SB.render_issues(rd), "error")

def test_route_endpoint_inside_map_for_geodesic(tmp_path):
    R = mk(tmp_path); R["locations"]["far"] = {"lonlat": [-120.0, 45.0]}      # far outside the toy map
    R["events"].append({"id": "g", "do": "route_reveal", "at": {"word": "Samarkand"}, "dur": 1.0, "claim": "c1", "purpose": "p", "geodesic": ["a", "far"], "edge_margin": 10})
    rc, rd = build(tmp_path, R); r = rd.routes["g"]
    assert 9.9 <= r.end[0] <= 188 and 0 <= r.end[1] <= 334 and not [i for i in SB.render_issues(rd) if i.code == "route.endpoint"]
    assert "g_end" in rc.loc

def test_baked_text_warning_on_a_baked_base(tmp_path):
    R = mk(tmp_path); rc, rd = build(tmp_path, R); cv2.imwrite(str(tmp_path / "base.png"), cv2.resize(_baked(), (188, 334)))
    cv2.imwrite(str(tmp_path / "baked.png"), _baked()); rd.base_path = str(tmp_path / "baked.png"); assert "base.baked_text" in codes(SB.render_issues(rd), "warning")

def test_narration_tail_plan():
    ok = SB.tail_plan(WORDS, 0.55, 3.7, margin=0.2, fade=0.3)           # window 0.55..4.25 starts between words; last word 'Berlin.' ends 3.6; next word 'Later' 4.4
    assert ok["ok"], ok; assert ok["fade_start"] >= 3.6 - 0.55 + 0.2 - 1e-6 and ok["last_word"] == "Berlin." and ok["fade_start"] + ok["fade_dur"] <= 3.7
    cut = SB.tail_plan(WORDS, 0.55, 2.9, margin=0.2, fade=0.3); assert not cut["ok"] and any("cuts the word 'Berlin.'" in p for p in cut["problems"])
    short = SB.tail_plan(WORDS, 0.55, 3.4, margin=0.2, fade=0.3); assert not short["ok"] and any("too short" in p for p in short["problems"])
    start_cut = SB.tail_plan(WORDS, 0.45, 3.7, margin=0.2, fade=0.3); assert not start_cut["ok"] and any("cuts the word 'a'" in p for p in start_cut["problems"])
    assert not SB.tail_plan(WORDS, 0.55, 3.84, margin=0.3, fade=0.5)["ok"]

def test_old_behaviour_would_truncate_a_word():
    # regression: the previous CLI faded over the last 0.35 s of the clip regardless of speech
    dur, offset = 3.3, 0.55; old_fade_start = dur - 0.35; last_end = 3.6 - offset
    assert old_fade_start < last_end                                         # the old rule starts fading while 'Berlin.' is still being spoken
    assert not SB.tail_plan(WORDS, offset, dur, 0.2, 0.35)["ok"]            # new planner refuses this window
    p = SB.tail_plan(WORDS, offset, 3.7, 0.2, 0.35); assert p["ok"] and p["fade_start"] >= last_end + 0.2 - 1e-6

def test_c1_recipe_static_validation_and_tail_with_real_alignment_if_present():
    R = yaml.safe_load(open(os.path.join(ROOT, "recipes", "cartography", "c1_samarkand_hinge.yaml"))); validate(R)
    iss = SB.static_issues(R); assert not [i for i in iss if i.level == "error"] and "claims.unverified" in codes(iss)
    al = "/workspace/posterity/micro-anomaly/tamerlane/raw/vo_alignment_tamerlane_rev6.json"
    if os.path.exists(al):
        from motionplates.cartography.engine import load_words
        t = SB.tail_plan(load_words(al), R["vo"]["offset_s"], R["output"]["duration"], R["limits"]["tail_margin_s"], R["limits"]["tail_fade_s"]); assert t["ok"], t
        assert t["last_word"] == "Berlin." and t["fade_start"] >= t["last_end"] + 0.25 - 1e-6

def test_cli_check_and_render_gate(tmp_path):
    from motionplates.cartography.cli import main
    R = mk(tmp_path); yp = tmp_path / "r.yaml"; yp.write_text(yaml.safe_dump(R))
    assert main(["check", str(yp), "--assets", str(tmp_path)]) == 0
    R2 = mk(tmp_path); R2["events"][1]["at"] = {"word": "Samarkand", "offset": 2.5}; (tmp_path / "bad.yaml").write_text(yaml.safe_dump(R2))
    assert main(["check", str(tmp_path / "bad.yaml"), "--assets", str(tmp_path)]) == 5
    assert main(["render", str(tmp_path / "bad.yaml"), "--out", str(tmp_path / "o"), "--assets", str(tmp_path)]) == 5 and not os.path.exists(tmp_path / "o" / "c1_silent.mp4")
    assert main(["render", str(yp), "--out", str(tmp_path / "ok"), "--assets", str(tmp_path)]) == 0
    m = json.load(open(next(os.path.join(tmp_path, "ok", f) for f in os.listdir(tmp_path / "ok") if f.endswith("manifest.json"))))
    assert m["status"] == "INTERNAL_POC_DRAFT_UNVERIFIED_CLAIMS" and m["narration_tail"]["ok"] and m["schema"] == 2

def test_text_halo_sprites_have_no_box():
    from motionplates.cartography.engine import text_halo, hexbgr
    st = {"ink": hexbgr("#24160c"), "ivory": hexbgr("#f4e8cb"), "plate": hexbgr("#1d130b")}
    for kind in ("geo", "event", "title"):
        s = text_halo([("TEST", "bold", 40)], 1.0, st, kind); a = s[..., 3]
        assert s.dtype == np.float32 and a.max() > 0.9 and a[0, :].max() < 0.35 and a[-1, :].max() < 0.35 and a[:, 0].max() < 0.35 and a[0, 0] < 0.1      # fades to nothing at the sprite edges (no rectangle)
        assert (a > 0.5).mean() < 0.5                                                                                       # not a filled plate
