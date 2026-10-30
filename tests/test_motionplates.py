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
    repo_root = os.path.abspath(os.path.join(HERE, ".."))
    src_root = os.path.join(repo_root, "src")
    tools_root = os.path.join(repo_root, "tools")

    ALLOW_LIST = {
        "engine_loader.py",
    }

    for root_dir in (src_root, tools_root):
        if not os.path.exists(root_dir):
            continue
        for dp, _, fs in os.walk(root_dir):
            for f in fs:
                if not f.endswith(".py"):
                    continue
                if f in ALLOW_LIST:
                    continue
                filepath = os.path.join(dp, f)
                content = open(filepath).read()
                assert "/workspace/" not in content, f"hardcoded /workspace/ path in {f}"

def test_every_recipe_validates_structurally():
    rdir = os.path.join(HERE, "..", "recipes")
    for f in os.listdir(rdir):
        if f.endswith(".yaml"):
            assert V.validate_recipe(load_recipe(os.path.join(rdir, f)), None, check_assets=False) == [], f

# ---------------- v0.3: petals, proxy, suggestions, packs, ground ramp ----------------
from motionplates.core import proxy as PX
from motionplates.effects import petal_fall as PF

def _petal_effect(synth):
    ctx = engine.prepare(RECIPE, plates_dir=synth, log=lambda *a: None); return ctx, [e for e in ctx.effects if e.type == "petal_fall"][0]

def test_petal_sprites_distinct_and_not_mirrored_copies(synth):
    ctx, pf = _petal_effect(synth)
    ex = [i for i in pf.items if not i["original"]]; org = [i for i in pf.items if i["original"]]
    assert ex, "recipe has extras"
    for e in ex:
        assert max(PF.sprite_similarity(e["spr"], o["spr"]) for o in org) < 0.985          # variants are not (mirrored/scaled) copies of a source
    o = org[0]["spr"]; mir = dict(o, rgb=o["rgb"][:, ::-1].copy(), a=o["a"][:, ::-1].copy())
    assert PF.sprite_similarity(o, mir) > 0.985                                               # the metric does catch a mirrored copy

def test_petal_release_times_monotonic_and_bounded(synth):
    ctx, pf = _petal_effect(synth); ex = sorted([i["t_rel"] for i in pf.items if not i["original"]])
    assert ex == sorted(ex) and all(b - a >= 0.05 for a, b in zip(ex, ex[1:]))
    t0 = pf.p["extras"]["t0"]; assert min(ex) >= t0 - 1e-9 and max(ex) <= pf.p["extras"]["t1"] + 1e-9

def test_petals_land_on_plane_and_settle(synth):
    ctx, pf = _petal_effect(synth); q = pf.quad; xs, ys = q[:, 0], q[:, 1]
    for it in pf.items:
        assert xs.min() - 5 <= it["L"][0] <= xs.max() + 5 and ys.min() - 5 <= it["L"][1] <= ys.max() + 5
        late = pf._basis(it, it["tl"] + 1.5)
        if late: assert late["landed"] and abs(late["R"][2, 2]) > 0.95                          # lying flat after settling

def test_original_petals_present_before_release(rendered):
    assert rendered[0]["frame0"]["max_abs_diff_vs_plate"] == 0

def test_proxy_recipe_scaling_and_render(synth, tmp_path):
    R = load_recipe(RECIPE); S = PX.scale_recipe(R, 0.5)
    assert (S["output"]["width"], S["output"]["height"]) == (136, 240) and S["layers"][0]["polygons"][0][1] == [135.0, 150.0]
    m = engine.render(RECIPE, str(tmp_path), plates_dir=synth, proxy=0.5, log=lambda *a: None)
    assert m["qc"]["status"] == "PROXY_PREVIEW" and m["output"]["W"] == 136

def test_suggest_regions_finds_block(tmp_path):
    sklearn = pytest.importorskip("sklearn", reason="sklearn is optional for the suggest module")
    from motionplates.authoring import suggest as S
    img = np.full((480, 270, 3), 120, np.uint8); img[:, :, 0] = np.linspace(100, 140, 270).astype(np.uint8)[None, :]; cv2.rectangle(img, (40, 200), (200, 400), (30, 40, 150), -1)
    c = S.candidates(img, "regions", 6); tgt = np.zeros((480, 270), bool); tgt[200:401, 40:201] = True
    assert S.best_match(c, tgt)["union_iou"] > 0.85
    b = S.candidates(img, "box", 1, box=[20, 180, 220, 420]); assert S.iou(b[0]["mask"], tgt) > 0.85

def test_petal_pack_roundtrip(synth, tmp_path):
    ctx, pf = _petal_effect(synth); PF.export_pack(pf.sources, str(tmp_path / "pack")); back = PF.load_pack(str(tmp_path / "pack"))
    assert len(back) == len(pf.sources) and all(v["a"].max() > 0.9 for v in back.values())

def test_templates_are_valid_yaml_with_placeholders():
    d = os.path.join(HERE, "..", "recipes", "templates")
    for f in os.listdir(d):
        txt = open(os.path.join(d, f)).read(); assert "__NAME__" in txt and "__PLATE__" in txt; yaml.safe_load(txt.replace("__NAME__", "t").replace("__PLATE__", "p.png"))

def test_ground_ramp_is_continuous_and_identity_at_t0(synth):
    from motionplates.effects.parallax_push import ParallaxPush
    ctx = engine.prepare(RECIPE, plates_dir=synth, log=lambda *a: None)
    pp = [e for e in ctx.effects if e.type == "parallax_push"][0]; pp.p["ground_ramp"] = {"y0": 200, "y1": 440, "end_scale": 1.03}; pp.setup(ctx)
    mx, my = ctx.ground_warp(ctx, 0.0); H, W = mx.shape
    assert np.abs(mx - np.arange(W)[None, :]).max() < 1e-3 and np.abs(my - np.arange(H)[:, None]).max() < 1e-3
    mx, my = ctx.ground_warp(ctx, 1.0); assert np.all(np.diff(my[:, 0]) > 0)                    # monotonic: no folds => no disocclusion


# ---------------- smoke_v2 tests ----------------
def test_smoke_v2_module_structure():
    """Verify smoke_v2 module exports expected classes and functions."""
    from motionplates.effects import smoke_v2
    assert hasattr(smoke_v2, 'periodic_noise')
    assert hasattr(smoke_v2, 'smoothstep')
    assert hasattr(smoke_v2, 'Flicker')
    assert hasattr(smoke_v2, 'ease')


def test_smoke_v2_periodic_noise_properties():
    """periodic_noise produces zero-mean unit-std noise that tiles seamlessly."""
    from motionplates.effects.smoke_v2 import periodic_noise
    rng = np.random.default_rng(42)
    h, w = 128, 128
    n = periodic_noise(rng, h, w, lo=32, hi=4)
    assert n.shape == (h, w)
    assert abs(n.mean()) < 0.1
    assert 0.5 < n.std() < 1.5
    assert np.allclose(n[0, :], n[0, :])


def test_smoke_v2_flicker_range():
    """Flicker output stays within expected bounds."""
    from motionplates.effects.smoke_v2 import Flicker
    rng = np.random.default_rng(123)
    fl = Flicker(rng, amp=0.2)
    vals = [fl(t * 0.01) for t in range(500)]
    assert all(-1 < v < 2 for v in vals)
    assert np.std(vals) > 0.05


def test_smoke_v2_smoothstep():
    """smoothstep produces expected S-curve values."""
    from motionplates.effects.smoke_v2 import smoothstep
    x = np.linspace(-1, 2, 100)
    y = smoothstep(0, 1, x)
    assert np.all(y[:10] < 0.01)
    assert np.all(y[-10:] > 0.99)
    assert 0.4 < y[50] < 0.6


def test_smoke_v2_ease():
    """ease function works as expected."""
    from motionplates.effects.smoke_v2 import ease
    assert ease(0.0, 0.0, 1.0) < 0.01
    assert ease(1.0, 0.0, 1.0) > 0.99
    assert 0.4 < ease(0.5, 0.0, 1.0) < 0.6


# ---------------- smoke_v2 render fixes ----------------

def test_smoke_v2_render_requires_output():
    """render() raises ValueError when given neither out_path nor writer."""
    from motionplates.effects.smoke_v2 import render, SmokeScene
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, np.full((100, 100, 3), 128, np.uint8))
        plate_path = f.name
    try:
        with pytest.raises(ValueError, match="requires either out_path or writer"):
            render(plate_path, {"emitters": []}, None, seconds=0.1, fps=10, size=(64, 64))
    finally:
        os.unlink(plate_path)


def test_smoke_v2_parse_size():
    """parse_size correctly parses WxH strings."""
    from motionplates.effects.smoke_v2 import parse_size
    assert parse_size("1080x1920") == (1080, 1920)
    assert parse_size("1920x1080") == (1920, 1080)
    assert parse_size("360x640") == (360, 640)
    with pytest.raises(Exception):
        parse_size("invalid")
    with pytest.raises(Exception):
        parse_size("100")
    with pytest.raises(Exception):
        parse_size("-100x200")


def test_smoke_v2_grab_size():
    """grab_size computes correct phone sizes for portrait and landscape."""
    from motionplates.effects.smoke_v2 import grab_size
    assert grab_size((1080, 1920)) == (360, 640)
    assert grab_size((1920, 1080)) == (640, 360)
    assert grab_size((720, 1280)) == (360, 640)
    gw, gh = grab_size((1920, 1200))
    assert gw == 640
    assert 350 < gh < 450


def test_smoke_v2_emitter_validation_missing_src():
    """Emitter validation catches missing 'src' key."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="'src'"):
        validate_emitter_spec({"type": "candle", "height": 100})


def test_smoke_v2_emitter_validation_missing_height():
    """Emitter validation catches missing 'height' key."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="'height'"):
        validate_emitter_spec({"type": "candle", "src": [100, 200]})


def test_smoke_v2_emitter_validation_bad_src_type():
    """Emitter validation catches invalid 'src' type."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="'src' must be"):
        validate_emitter_spec({"type": "candle", "src": "invalid", "height": 100})


def test_smoke_v2_emitter_validation_haze_missing_rect():
    """Emitter validation catches missing 'rect' for haze type."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="'rect'"):
        validate_emitter_spec({"type": "haze"})


def test_smoke_v2_emitter_validation_unknown_type():
    """Emitter validation catches unknown emitter type."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="unknown type"):
        validate_emitter_spec({"type": "invalid_type", "src": [100, 200], "height": 100})


def test_smoke_v2_emitter_validation_opacity_range():
    """Emitter validation catches out-of-range opacity."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    with pytest.raises(ValueError, match="opacity"):
        validate_emitter_spec({"type": "candle", "src": [100, 200], "height": 100, "opacity": 1.5})


def test_smoke_v2_emitter_validation_valid_spec():
    """Emitter validation passes for valid specs."""
    from motionplates.effects.smoke_v2 import validate_emitter_spec
    validate_emitter_spec({"type": "candle", "src": [100, 200], "height": 100})
    validate_emitter_spec({"type": "torch", "src": [50, 75], "height": 200, "opacity": 0.8})
    validate_emitter_spec({"type": "haze", "rect": [0, 0, 100, 100]})


def test_smoke_v2_render_reel_jobs1_writes_frames(tmp_path):
    """render_reel with jobs=1 writes the expected number of frames."""
    from motionplates.effects.smoke_v2 import render_reel, ffmpeg_writer
    import shutil

    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg not available")

    plate = tmp_path / "plate.png"
    cv2.imwrite(str(plate), np.full((100, 100, 3), 128, np.uint8))

    cfg = tmp_path / "shot.json"
    cfg.write_text(json.dumps({"plate": str(plate), "emitters": []}))

    reel_dir = tmp_path / "reel"
    reel_dir.mkdir()
    reel_json = reel_dir / "shots" / "reel.json"
    reel_json.parent.mkdir(parents=True, exist_ok=True)
    reel_json.write_text(json.dumps({"shots": [{"config": str(cfg), "seconds": 0.1}]}))

    out = tmp_path / "out.mp4"
    render_reel(json.loads(reel_json.read_text()), str(out), size=(64, 64), fps=30, base_dir=".", jobs=1)

    assert out.exists()
    cap = cv2.VideoCapture(str(out))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    assert frame_count == 3


# ---------------- build cache tests ----------------

def test_cache_compute_key_deterministic(tmp_path):
    """compute_cache_key produces consistent hashes for same inputs."""
    from motionplates.build.cache import compute_cache_key

    plate = tmp_path / "plate.png"
    cv2.imwrite(str(plate), np.full((50, 50, 3), 100, np.uint8))

    seg = {"id": "S01", "start": 0.0, "end": 1.0}
    fx = {"smoke": True}

    k1 = compute_cache_key(plate, seg, fx)
    k2 = compute_cache_key(plate, seg, fx)
    assert k1 == k2


def test_cache_compute_key_changes_with_plate(tmp_path):
    """compute_cache_key changes when plate content changes."""
    from motionplates.build.cache import compute_cache_key

    plate1 = tmp_path / "plate1.png"
    plate2 = tmp_path / "plate2.png"
    cv2.imwrite(str(plate1), np.full((50, 50, 3), 100, np.uint8))
    cv2.imwrite(str(plate2), np.full((50, 50, 3), 200, np.uint8))

    seg = {"id": "S01"}
    k1 = compute_cache_key(plate1, seg)
    k2 = compute_cache_key(plate2, seg)
    assert k1 != k2


def test_cache_compute_key_changes_with_config(tmp_path):
    """compute_cache_key changes when segment config changes."""
    from motionplates.build.cache import compute_cache_key

    plate = tmp_path / "plate.png"
    cv2.imwrite(str(plate), np.full((50, 50, 3), 100, np.uint8))

    seg1 = {"id": "S01", "start": 0.0}
    seg2 = {"id": "S01", "start": 1.0}
    k1 = compute_cache_key(plate, seg1)
    k2 = compute_cache_key(plate, seg2)
    assert k1 != k2


def test_shot_cache_is_valid(tmp_path):
    """ShotCache.is_valid returns correct status."""
    from motionplates.build.cache import ShotCache

    cache = ShotCache(tmp_path / "cache")

    assert not cache.is_valid("shot1", "abc123")

    (tmp_path / "cache" / "shot1.mp4").write_bytes(b"video data")
    assert not cache.is_valid("shot1", "abc123")

    cache.mark_valid("shot1", "abc123")
    assert cache.is_valid("shot1", "abc123")
    assert not cache.is_valid("shot1", "different_key")


def test_shot_cache_mark_stale(tmp_path):
    """ShotCache.mark_stale renames clips correctly."""
    from motionplates.build.cache import ShotCache

    cache = ShotCache(tmp_path / "cache")
    clip = tmp_path / "cache" / "shot1.mp4"
    clip.write_bytes(b"video data")
    cache.mark_valid("shot1", "key1")

    stale_path = cache.mark_stale("shot1")
    assert stale_path is not None
    assert stale_path.exists()
    assert ".stale-" in stale_path.name
    assert not clip.exists()
    assert not cache._key_path("shot1").exists()


def test_shot_cache_invalidate_if_stale(tmp_path):
    """ShotCache.invalidate_if_stale correctly detects and marks stale clips."""
    from motionplates.build.cache import ShotCache

    cache = ShotCache(tmp_path / "cache")

    assert cache.invalidate_if_stale("shot1", "key1")

    clip = tmp_path / "cache" / "shot1.mp4"
    clip.write_bytes(b"video data")
    cache.mark_valid("shot1", "key1")
    assert not cache.invalidate_if_stale("shot1", "key1")

    assert cache.invalidate_if_stale("shot1", "different_key")
    assert not clip.exists()


# ---------------- engine loader tests ----------------

def test_engine_loader_get_root(monkeypatch):
    """engine_loader.get_root respects MOTIONPLATES_ROOT env var."""
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "tools", "qc"))
    from engine_loader import get_root

    monkeypatch.delenv("MOTIONPLATES_ROOT", raising=False)
    assert get_root() == "/workspace/posterity"

    monkeypatch.setenv("MOTIONPLATES_ROOT", "/custom/path")
    assert get_root() == "/custom/path"


def test_engine_loader_load_animate():
    """engine_loader can load the locked animate engine."""
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "tools", "qc"))
    from engine_loader import load_animate

    animate = load_animate()
    assert hasattr(animate, "Engine")


def test_engine_loader_custom_engine(tmp_path, monkeypatch):
    """engine_loader respects MOTIONPLATES_ENGINE env var."""
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "tools", "qc"))

    custom_engine = tmp_path / "custom_animate.py"
    custom_engine.write_text("ENGINE_VERSION = 'custom'\nclass Engine: pass")

    monkeypatch.setenv("MOTIONPLATES_ENGINE", str(custom_engine))

    if "animate" in sys.modules:
        del sys.modules["animate"]

    from engine_loader import load_animate
    animate = load_animate()
    assert animate.ENGINE_VERSION == "custom"


def test_engine_loader_missing_engine(tmp_path, monkeypatch):
    """engine_loader raises FileNotFoundError for missing custom engine."""
    import sys
    sys.path.insert(0, os.path.join(HERE, "..", "tools", "qc"))

    monkeypatch.setenv("MOTIONPLATES_ENGINE", str(tmp_path / "nonexistent.py"))

    if "animate" in sys.modules:
        del sys.modules["animate"]

    from engine_loader import load_animate
    with pytest.raises(FileNotFoundError, match="MOTIONPLATES_ENGINE"):
        load_animate()


# ---------------- landscape size tests (1920x1080) ----------------

def test_smoke_v2_landscape_size():
    """smoke_v2 functions work with landscape 1920x1080 size."""
    from motionplates.effects.smoke_v2 import parse_size, grab_size

    w, h = parse_size("1920x1080")
    assert (w, h) == (1920, 1080)

    gw, gh = grab_size((1920, 1080))
    assert gw == 640
    assert gh == 360
