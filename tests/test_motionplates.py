import os, numpy as np, cv2, json, subprocess
import pytest
from motionplates.core import engine, plate as P
from motionplates.core.recipe import load_recipe

HERE = os.path.dirname(__file__)
RECIPE = os.path.join(HERE, "data", "test_recipe.yaml")

def decode(mp4):
    c = cv2.VideoCapture(mp4); fr = []
    while True:
        ok, f = c.read()
        if not ok: break
        fr.append(f)
    return fr

def test_frame0_equals_plate(rendered, synth):
    """frame 0 of the lossless pipeline must equal the cover-fit plate exactly (clean-plate swap is corrected by the fading residual)."""
    m, out = rendered
    assert m["frame0"]["max_abs_diff_vs_plate"] == 0

def test_frame0_delivery_close_to_plate(rendered, synth):
    m, out = rendered
    base, _ = P.load_cover(os.path.join(synth, "synth.png"), 270, 480)
    f0 = cv2.cvtColor(decode(m["mp4"])[0], cv2.COLOR_BGR2RGB).astype(int)
    assert np.abs(f0 - base.astype(int)).mean() < 2.0     # delivery encode (lossy crf14) is allowed to differ slightly

def test_determinism_same_seed(synth, tmp_path, rendered):
    m1, _ = rendered
    m2 = engine.render(RECIPE, str(tmp_path), plates_dir=synth, log=lambda *a: None)
    assert m1["frames_sha1"] == m2["frames_sha1"]

def test_seed_changes_output(synth, tmp_path, rendered, tmp_path_factory):
    import yaml
    r = yaml.safe_load(open(RECIPE)); r["seed"] = 99
    p = tmp_path / "r2.yaml"; p.write_text(yaml.safe_dump(r))
    m2 = engine.render(str(p), str(tmp_path / "o"), plates_dir=synth, log=lambda *a: None)
    assert rendered[0]["frames_sha1"] != m2["frames_sha1"]

def test_motion_cap_and_floor(rendered):
    mo = rendered[0]["motion"]
    assert 0.02 < mo["mean_abs_frame_delta"] < 2.5            # restrained: not frozen, not frantic (0-255 scale)
    assert mo["max_changed_pixel_fraction"] < 0.6

def test_safe_zone_quiet(rendered):
    for name, z in rendered[0]["safe_zones"].items():
        assert z["mean_abs_frame_delta"] <= z["max_mean_delta_allowed"], name

def test_no_white_bars_or_edge_seams(rendered):
    assert rendered[0]["edge_bar_scan"]["any_bar_detected"] is False
    fr = decode(rendered[0]["mp4"])
    for f in (fr[0], fr[len(fr) // 2], fr[-1]):
        rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        assert not any(P.detect_bars(rgb).values())
        for edge in (rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]):
            assert (edge.mean(1) > 240).mean() < 0.3         # no near-white edge line

def test_manifest_has_provenance(rendered, synth):
    m = rendered[0]
    assert len(m["plate"]["md5"]) == 32 and m["seed"] == 3 and m["recipe_md5"] and m["frames_sha1"]

def test_resolution_and_fps(rendered):
    m = rendered[0]; c = cv2.VideoCapture(m["mp4"])
    assert (int(c.get(3)), int(c.get(4))) == (270, 480) and abs(c.get(5) - 30) < 0.01

def test_presets_resolve():
    r = load_recipe(os.path.join(HERE, "..", "recipes", "poc_a_augustus.yaml"))
    assert all("type" in e for e in r["effects"])
    assert {e["type"] for e in r["effects"]} >= {"parallax_push", "petal_fall", "flame_flicker", "banner_sway", "fabric_ripple", "dust_motes"}

def test_plate_never_in_repo():
    root = os.path.abspath(os.path.join(HERE, ".."))
    tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout.split()
    assert not [t for t in tracked if t.lower().endswith((".mp4", ".mov")) or "OWNER" in t]
    assert not [t for t in tracked if t.lower().endswith(".png") and not t.startswith("tests/data/")]
