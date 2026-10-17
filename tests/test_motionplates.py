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
        assert z["mean_abs_frame_delta"] <= z["limit_mean_delta"], name

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
    assert not [t for t in tracked if t.lower().endswith((".png", ".jpg")) and not t.startswith(("tests/data/", "previews/thumbs/", "docs/img/"))]


# ---------------- v0.2.1 additions: encoding, failure handling, QC, frame-0 diagnostics, validation, CI hygiene ----------------
import yaml
from motionplates.core import encode as E, validate as V, qc as Q
from motionplates.cli import main as cli_main

def _recipe(tmp_path, **patch):
    r = yaml.safe_load(open(RECIPE))
    for k, v in patch.items():
        if v is None: r.pop(k, None)
        else: r[k] = v
    p = tmp_path / "r.yaml"; p.write_text(yaml.safe_dump(r)); return str(p)

def test_status_is_review_required_until_playback_approved(rendered):
    q = rendered[0]["qc"]
    assert q["status"] == "REVIEW_REQUIRED" and "approval" in q["reason"]
    assert not [c for c in q["checks"] if c["status"] == "FAIL"]

def test_playback_approval_bound_to_exact_render(synth, tmp_path, rendered):
    m = rendered[0]
    ok = _recipe(tmp_path, qc={"playback_approved": True, "approved_by": "editor", "approved_frames_sha1": m["frames_sha1"]})
    assert engine.render(ok, str(tmp_path / "a"), plates_dir=synth, log=lambda *a: None)["qc"]["status"] == "PASS"
    bad = _recipe(tmp_path, qc={"playback_approved": True, "approved_by": "editor", "approved_frames_sha1": "0" * 40})
    assert engine.render(bad, str(tmp_path / "b"), plates_dir=synth, log=lambda *a: None)["qc"]["status"] == "REVIEW_REQUIRED"

def test_qc_failure_rejects_output_and_exit_code(synth, tmp_path):
    r = yaml.safe_load(open(RECIPE)); r["safe_zones"] = [{"name": "tight", "box": [0, 0, 270, 480], "max_mean_delta": 0.0001}]
    p = tmp_path / "r.yaml"; p.write_text(yaml.safe_dump(r)); out = tmp_path / "o"
    rc = cli_main(["render", str(p), "--out", str(out), "--plates", synth])
    assert rc == 2
    assert not (out / "synth_test_animated.mp4").exists() and (out / "synth_test_REJECTED.mp4").exists()
    assert json.load(open(out / "synth_test_manifest.json"))["qc"]["status"] == "FAIL"

def test_no_tmp_files_left_and_output_verified(rendered):
    m, out = rendered
    assert not [f for f in os.listdir(out) if ".tmp" in f]
    assert m["verify"]["full_decode_ok"] and m["verify"]["frames"] == 30 and m["verify"]["color_space"] == "bt709"

def test_at_stills_leave_no_video(synth, tmp_path):
    out = tmp_path / "o"; engine.render(RECIPE, str(out), plates_dir=synth, only_times=[0.0, 0.5], log=lambda *a: None)
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(out) for f in fs]
    assert files and not [f for f in files if f.endswith((".mp4", ".tmp"))]

def test_writer_failure_cleans_up(tmp_path):
    dst = str(tmp_path / "x.mp4")
    with pytest.raises(RuntimeError):
        with E.FFmpegWriter(dst, 64, 64, 30) as w:
            w.write(np.zeros((64, 64, 3), np.uint8)); raise RuntimeError("boom")
    assert os.listdir(tmp_path) == []

def test_writer_bad_ffmpeg_args_raise(tmp_path):
    with pytest.raises(E.EncodeError):
        with E.FFmpegWriter(str(tmp_path / "x.mp4"), 64, 64, 30, preset="nope") as w:
            for _ in range(3): w.write(np.zeros((64, 64, 3), np.uint8))
    assert os.listdir(tmp_path) == []

def test_verify_detects_wrong_frame_count_and_truncation(tmp_path):
    dst = str(tmp_path / "x.mp4")
    with E.FFmpegWriter(dst, 64, 64, 30) as w:
        for _ in range(10): w.write(np.full((64, 64, 3), 100, np.uint8))
    w.finalize()
    with pytest.raises(E.EncodeError): E.verify_video(dst, 64, 64, 30, 12)
    with pytest.raises(E.EncodeError): E.verify_video(dst, 64, 64, 25, 10)
    bad = tmp_path / "t.mp4"; bad.write_bytes(open(dst, "rb").read()[:900])
    with pytest.raises(E.EncodeError): E.verify_video(str(bad), 64, 64, 30, 10)

def test_encode_colour_roundtrip_is_accurate(tmp_path):
    """one conversion, bt709 tagged: flat patches survive within 2 levels (4:2:0 + crf14), no matrix shift."""
    dst = str(tmp_path / "c.mp4"); cols = [(200, 30, 40), (30, 160, 60), (40, 60, 210), (128, 128, 128), (235, 235, 235), (20, 20, 20)]
    fr = np.zeros((96, 192, 3), np.uint8)
    for i, c in enumerate(cols): fr[:, i * 32:(i + 1) * 32] = c
    with E.FFmpegWriter(dst, 192, 96, 30, crf=10) as w:
        for _ in range(6): w.write(fr)
    w.finalize()
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", dst, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    d = np.frombuffer(raw, np.uint8).reshape(96, 192, 3).astype(int)
    for i, c in enumerate(cols): assert np.abs(d[40:56, i * 32 + 8:i * 32 + 24] - np.array(c)).max() <= 3, c

def test_frame0_diagnostics_present(rendered):
    f0 = rendered[0]["frame0"]
    assert "concentration" in f0 and "elsewhere" in f0["concentration"] and f0["pre_correction"]["corrected_fraction"] < 0.1
    assert os.path.exists(os.path.join(rendered[1], "debug", "frame0_residual_map.png"))

def test_mask_diagnostics_recorded(rendered):
    md = rendered[0]["mask_diagnostics"]
    assert {"subject", "fg", "banner"} <= set(md) and all("rim_colour_diff_vs_plate" in v for k, v in md.items() if not k.startswith("_"))

def test_validate_ok_and_errors(synth, tmp_path):
    R = load_recipe(RECIPE); assert V.validate_recipe(R, synth) == []
    bad = load_recipe(RECIPE); bad["layers"][0]["polygons"] = [[[0, 0], [1, 1]]]; bad["effects"][3]["elements"] = ["nope"]; bad["output"]["fps"] = 0; bad["plate"]["file"] = "missing.png"
    bad["effects"].append({"type": "wobble"}); bad["layers"].append({"name": "subject", "polygons": [[[0, 0], [10, 0], [10, 10]]]})
    probs = " | ".join(V.validate_recipe(bad, synth))
    for needle in ("polygon needs", "element 'nope'", "fps invalid", "plate file not found", "unknown type 'wobble'", "duplicate"): assert needle in probs, needle
    with pytest.raises(V.RecipeError): V.check_recipe(bad, synth)

def test_invalid_recipe_exits_3_before_rendering(synth, tmp_path):
    r = yaml.safe_load(open(RECIPE)); r["layers"][0]["polygons"] = [[[0, 0]]]; p = tmp_path / "r.yaml"; p.write_text(yaml.safe_dump(r))
    assert cli_main(["render", str(p), "--out", str(tmp_path / "o"), "--plates", synth]) == 3 and not (tmp_path / "o").exists()

def test_plates_root_must_be_configured(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("MOTIONPLATES_PLATES", raising=False)
    assert cli_main(["render", RECIPE, "--out", str(tmp_path / "o")]) == 3
    assert "MOTIONPLATES_PLATES" in capsys.readouterr().err
    with pytest.raises(V.PlatesRootError): V.resolve_plates_root("/definitely/not/here")

def test_plates_root_from_env(monkeypatch, synth):
    monkeypatch.setenv("MOTIONPLATES_PLATES", synth); assert V.resolve_plates_root() == synth

def test_no_hardcoded_project_paths_in_source():
    root = os.path.abspath(os.path.join(HERE, "..", "src"))
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".py"): assert "/workspace/" not in open(os.path.join(dp, f)).read(), f

def test_every_recipe_validates_structurally():
    rdir = os.path.join(HERE, "..", "recipes")
    for f in os.listdir(rdir):
        if f.endswith(".yaml"):
            assert V.validate_recipe(load_recipe(os.path.join(rdir, f)), None, check_assets=False) == [], f
