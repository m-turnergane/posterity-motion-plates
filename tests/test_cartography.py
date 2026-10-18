import os, json, copy, numpy as np, cv2, pytest, yaml
from motionplates.cartography.engine import Recipe, Renderer, RecipeError, load_words, camera_state, Route

def mini(tmp_path, events=None):
    H, W = 200, 112; im = np.zeros((H, W, 3), np.uint8); im[:] = (60, 120, 160); cv2.circle(im, (50, 100), 10, (0, 0, 255), -1)
    base = tmp_path / "base.png"; cv2.imwrite(str(base), im)
    al = {"characters": list("go now"), "character_start_times_seconds": [0, .1, .2, .3, .4, .5], "character_end_times_seconds": [.1, .2, .3, .4, .5, .6]}
    (tmp_path / "al.json").write_text(json.dumps(al))
    R = {"output": {"size": [56, 100], "fps": 10, "duration": 1.0}, "base": {"file": "base.png"}, "vo": {"alignment": "al.json", "offset_s": 0.1},
         "locations": {"a": [30, 60], "b": [80, 140]},
         "events": events or [{"id": "m", "do": "marker", "at": {"word": "now"}, "at_loc": "a"},
                              {"id": "r", "do": "route_reveal", "at": 0.1, "from": "a", "to": "b", "dur": 0.5, "head": True},
                              {"id": "l", "do": "label", "at": {"word": "now"}, "anchor": "a", "text": "A"},
                              {"id": "c", "do": "camera_move", "at": 0.0, "dur": 0.6, "to": {"center": "a", "zoom": 1.5}}]}
    return R, str(base)

def test_word_timing_and_offset(tmp_path):
    R, b = mini(tmp_path); rc = Recipe(R, str(tmp_path))
    m = [e for e in rc.ev if e["id"] == "m"][0]; assert abs(m["t0"] - (0.3 - 0.1)) < 1e-6      # word 'now' starts at 0.3, clip offset 0.1
    assert abs(rc.timing.word("go", edge="end") - 0.1) < 1e-6

def test_unknown_primitive_location_word(tmp_path):
    R, b = mini(tmp_path); R["events"].append({"do": "wibble"}); 
    with pytest.raises(RecipeError): Recipe(R, str(tmp_path))
    R, b = mini(tmp_path); R["events"][0]["at_loc"] = "zzz"
    with pytest.raises(RecipeError): Recipe(R, str(tmp_path))
    R, b = mini(tmp_path); R["events"][0]["at"] = {"word": "absent"}
    with pytest.raises(RecipeError): Recipe(R, str(tmp_path))

def test_camera_overlap_rejected(tmp_path):
    R, b = mini(tmp_path); R["events"].append({"do": "camera_move", "at": 0.3, "dur": 0.5, "to": {"zoom": 1.2}})
    with pytest.raises(RecipeError): Recipe(R, str(tmp_path))

def test_camera_continuous_clamped_and_monotone_zoom(tmp_path):
    R, b = mini(tmp_path); rc = Recipe(R, str(tmp_path)); Renderer(rc, b)
    zs = []; prev = None
    for t in np.linspace(0, 1, 41):
        c, z = camera_state(rc, t); zs.append(z)
        vw = rc.W / (rc.cover * z); assert c[0] >= vw / 2 - 1e-6 and c[0] <= rc.base_w - vw / 2 + 1e-6
        if prev is not None: assert np.linalg.norm(c - prev) < 6      # no jumps
        prev = c
    assert all(b2 >= a - 1e-9 for a, b2 in zip(zs, zs[1:])) and zs[-1] == pytest.approx(1.5)

def test_route_dash_pattern_fixed_to_arclength(tmp_path):
    R, b = mini(tmp_path); rc = Recipe(R, str(tmp_path)); rc.loc  # noqa
    r = Route(rc, R["events"][1], 1.0); d1 = r.dashes(r.L * .5); d2 = r.dashes(r.L * .9)
    for (a, _), (b2, _) in zip(d1[:-1], d2):      # earlier dashes identical when the head advances (no crawling)
        assert np.allclose(a, b2)

def test_render_deterministic_and_nonblank(tmp_path):
    R, b = mini(tmp_path); rc = Recipe(R, str(tmp_path)); rd = Renderer(rc, b)
    f1, f2 = rd.frame(0.5), rd.frame(0.5); assert (f1 == f2).all() and f1.shape == (100, 56, 3)
    assert np.abs(f1.astype(int) - rd.frame(0.0).astype(int)).mean() > 0.3

def test_missing_base_is_clear_error(tmp_path):
    R, b = mini(tmp_path); rc = Recipe(R, str(tmp_path))
    with pytest.raises(RecipeError, match="base map not found"): Renderer(rc, str(tmp_path / "nope.png"))

def test_cli_render_writes_verified_mp4(tmp_path):
    from motionplates.cartography.cli import main
    R, b = mini(tmp_path); yp = tmp_path / "r.yaml"; yp.write_text(yaml.safe_dump(R))
    rc = main(["render", str(yp), "--out", str(tmp_path / "o"), "--assets", str(tmp_path)]); assert rc == 0
    assert (tmp_path / "o" / "carto_silent.mp4").exists() and not [f for f in os.listdir(tmp_path / "o") if ".tmp" in f]
    assert main(["render", str(yp), "--out", str(tmp_path / "o2"), "--assets", str(tmp_path / "nowhere")]) == 3

def test_real_recipe_validates_without_map():
    here = os.path.dirname(os.path.dirname(__file__)); R = yaml.safe_load(open(os.path.join(here, "recipes/poc_c/tamerlane_hinge.yaml")))
    from motionplates.cartography.engine import validate; validate(R)
