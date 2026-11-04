"""Tests for the OPT-IN depth_v1 layer in build_template_v1.py (depth_v1 LOCKED 2026-10-30 6:16pm ET).

Run:  cd /workspace/posterity/motion/templates && /workspace/mpvenv/bin/python -m pytest -q tests/
Renders are tiny (108x192 / 9-12 frames) and live in pytest's tmp_path. Synthetic plates use matte mode "poly" (no model);
tests on real locked configs (b05 / b01 / Hubert) skip when the plate is missing.
"""
import importlib.util, json, subprocess, sys, itertools
from pathlib import Path
import numpy as np, pytest, cv2
from PIL import Image

HERE = Path(__file__).resolve().parent; TPL = HERE.parent / "build_template_v1.py"; PY = sys.executable
ROOT = HERE.parent.parent.parent; DCFG = ROOT / "engine-rnd" / "depth" / "configs"
EDW = ROOT / "standalones" / "edward-ii" / "plates-v3b"
B05 = EDW / "b05_landing_1326_kent_OWNER.png"; B01 = EDW / "b01_gloucester_funeral_wide_kent_OWNER.png"
HUB = ROOT / "day3" / "nero-fiddle" / "assets" / "pd_hubert_robert_fire.jpg"
_n = itertools.count()

def tex_plate(tmp, name, w, h, seed=0):
    rng = np.random.default_rng(seed); a = cv2.GaussianBlur(rng.uniform(0, 255, (h, w, 3)).astype(np.float32), (0, 0), 3)
    p = tmp / name; Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p); return p

def inline_depth(travel=0.03, push=(1.0, 1.06)):
    return dict(matte=dict(mode="poly"), camera=dict(push=list(push), anchor=[0.5, 0.5], travel=travel, dir=[1, 0], pivot=0.5),
                layers=[dict(name="far", parallax=0.0, push_gain=0.4),
                        dict(name="near", parallax=1.0, push_gain=1.0, polys=[[[0.3, 0.55], [0.7, 0.55], [0.7, 0.95], [0.3, 0.95]]])])

def write_inputs(tmp, plates, shots, plates_dir=None, extra_rows=None):
    """plates: {plate_id: (filename, [shot ids])}; shots: list of timeline shot dicts."""
    rows = [dict(plate_id=k, scene_id="SC", shot_ids=v[1], prompt="t", aspect="", target_resolution="", expected_filename=v[0], refs=[], notes="",
                 **((extra_rows or {}).get(k, {}))) for k, v in plates.items()]
    (tmp / "m.json").write_text(json.dumps({"plates_dir": str(plates_dir or tmp), "plates": rows}))
    (tmp / "t.json").write_text(json.dumps(dict(name="t", fps=30, shots=shots)))
    return tmp / "m.json", tmp / "t.json"

def run(tmp, size, *extra):
    r = subprocess.run([PY, str(TPL), "--manifest", str(tmp / "m.json"), "--timeline", str(tmp / "t.json"), "--size", size,
                        "--build-dir", str(tmp / "build"), *extra], capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr

def load_tpl():
    s = importlib.util.spec_from_file_location(f"bt_depth_{next(_n)}", TPL); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def setup_inproc(tmp, size="108x192"):
    bt = load_tpl()
    bt.setup(bt.parse_args(["--manifest", str(tmp / "m.json"), "--timeline", str(tmp / "t.json"), "--size", size, "--build-dir", str(tmp / "build"), "--jobs", "1"]))
    return bt

def probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_frames",
                        "-of", "json", str(p)], capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]; return s["width"], s["height"], int(s["nb_read_frames"])

# ---------------------------------------------------------------- 1. tiny 9:16 depth render (real locked b05 config, by reference)
@pytest.mark.skipif(not B05.is_file(), reason="b05 plate missing")
def test_depth_shot_9x16_renders_tiny_clip(tmp_path):
    write_inputs(tmp_path, {"b05": (B05.name, ["S01"])},
                 [dict(id="S01", frames=9, depth=str(DCFG / "b05_landing_push_v1.json"), scene_action="landing: boats beach, men wade ashore")], plates_dir=EDW)
    rc, out = run(tmp_path, "108x192", "--clips-only", "--no-phone-qc", "--jobs", "1")
    assert rc == 0, out
    clip = tmp_path / "build" / "clips" / "S01.mp4"; assert probe(clip) == (108, 192, 9)
    pr = json.load(open(tmp_path / "build" / "clips" / "S01.depth_proof.json"))
    assert pr["single_transform_ok"] and pr["warps_logged"] == 9 * len(pr["layers"]) and pr["template_cam_calls"] == 0
    assert "DEPTH" in out and "template push skipped" in out
    rc2, out2 = run(tmp_path, "108x192", "--clips-only", "--no-phone-qc", "--jobs", "1")   # second run: content-hash cache hit
    assert rc2 == 0 and "clip S01: CACHE HIT" in out2, out2

# ---------------------------------------------------------------- 2. 16:9 depth on a 941x1672 plate refused (per-layer density)
def test_depth_16x9_on_941x1672_plate_refused(tmp_path):
    tex_plate(tmp_path, "edw.png", 941, 1672)
    write_inputs(tmp_path, {"P1": ("edw.png", ["S01"])}, [dict(id="S01", seconds=1.0, depth=inline_depth(), scene_action="procession")])
    rc, out = run(tmp_path, "1920x1080", "--check")
    assert rc != 0 and "GUARDRAIL REFUSED (pixel density" in out and "S01 (depth, larger layer scale = near)" in out, out
    assert "CHECK OK" not in out

# ---------------------------------------------------------------- 3. Hubert native landscape passes at 16:9 (real locked config)
@pytest.mark.skipif(not HUB.is_file(), reason="Hubert plate missing")
def test_hubert_native_plate_passes_16x9(tmp_path):
    write_inputs(tmp_path, {"hub": (HUB.name, ["S01"])},
                 [dict(id="S01", seconds=6.0, depth=str(DCFG / "hubert_fire_arch_push_v1.json"), scene_action="crowd flees the fire")], plates_dir=HUB.parent)
    rc, out = run(tmp_path, "1920x1080", "--check")
    assert rc == 0 and "CHECK OK" in out and "DEPTH 2 layers" in out, out
    line = [l for l in out.splitlines() if l.strip().startswith("S01")][0]
    assert "density 1.100" in line, line

# ---------------------------------------------------------------- 4. exactly one transform per layer per frame; template push never runs
def test_single_transform_template_push_skipped(tmp_path):
    tex_plate(tmp_path, "p.png", 270, 480)
    write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=6, push=[1.0, 1.10], depth=inline_depth(), scene_action="journey")])
    bt = setup_inproc(tmp_path)
    def boom(*a, **k): raise AssertionError("template cam_frame called on a depth shot")
    bt.cam_frame = boom; bt.prepare_cover = boom
    for d in (bt.CLIPS, bt.AUD, bt.QC): d.mkdir(parents=True, exist_ok=True)
    sid, st, n, _ = bt.render_segment("S01"); assert st == "render" and n == 6
    pr = json.load(open(bt.CLIPS / "S01.depth_proof.json"))
    assert pr["warps_logged"] == 6 * 2 == pr["expected"] and pr["max_warps_per_layer_frame"] == 1 and pr["template_cam_calls"] == 0
    assert bt.SEG["S01"]["depth"]["camera"]["push"] == [1.0, 1.06]            # depth cfg push wins; shot push NOT stacked on top
    assert probe(bt.CLIPS / "S01.mp4") == (108, 192, 6)

# ---------------------------------------------------------------- 4b. dust_v1 composes as plate_fx inside the layer matrix; its camera never runs
@pytest.mark.skipif(not B01.is_file(), reason="b01 plate missing")
def test_dust_composes_inside_depth_layers_without_its_camera(tmp_path):
    write_inputs(tmp_path, {"b01": (B01.name, ["S01"])},
                 [dict(id="S01", frames=4, depth=str(DCFG / "b01_gloucester_kent_drift_v1.json"), dust=str(DCFG / "compose_b01_dust_test.json"),
                       depth_ok_reason="technical showcase only")], plates_dir=EDW)
    bt = setup_inproc(tmp_path); bt.cam_frame = None
    for d in (bt.CLIPS, bt.AUD, bt.QC): d.mkdir(parents=True, exist_ok=True)
    bt.render_segment("S01"); pr = json.load(open(bt.CLIPS / "S01.depth_proof.json"))
    assert pr["single_transform_ok"] and pr["effect_camera_calls"] == 0 and "dust" in pr["plate_fx"], pr

# ---------------------------------------------------------------- 5. the depth config joins the content-hash key
def test_cache_key_changes_when_depth_config_changes(tmp_path):
    tex_plate(tmp_path, "p.png", 270, 480)
    keys = []
    for travel in (0.03, 0.03, 0.05):
        write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=6, depth=inline_depth(travel=travel), scene_action="x")])
        bt = setup_inproc(tmp_path); keys.append((bt.shot_key_parts(bt.SEG["S01"]), bt.md5j(bt.shot_key_parts(bt.SEG["S01"]))))
    assert keys[0][1] == keys[1][1] and keys[0][1] != keys[2][1]
    assert keys[0][0]["depth"] != keys[2][0]["depth"] and keys[0][0]["engine"]["depth_engine"] == "dd5cd5011c88b3b56528b96fedae5494"
    # a referenced config file: editing the file changes the key too
    cfg = inline_depth(); cfg["plate"] = str(tmp_path / "p.png"); cf = tmp_path / "d.json"; ks = []
    for tr in (0.03, 0.04):
        cfg["camera"]["travel"] = tr; cf.write_text(json.dumps(cfg))
        write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=6, depth="d.json", scene_action="x")])
        bt = setup_inproc(tmp_path); ks.append(bt.md5j(bt.shot_key_parts(bt.SEG["S01"])))
    assert ks[0] != ks[1]

# ---------------------------------------------------------------- 6. depth is OFF by default (opt-in per shot)
def test_depth_off_by_default(tmp_path):
    tex_plate(tmp_path, "p.png", 270, 480)
    (tmp_path / "unused_depth.json").write_text(json.dumps(inline_depth()))     # a depth config lying next to the timeline is NOT picked up
    write_inputs(tmp_path, {"P1": ("p.png", ["S01", "S02", "S03"])},
                 [dict(id="S01", frames=3), dict(id="S02", frames=3, depth=None), dict(id="S03", frames=3, depth=False)])
    bt = setup_inproc(tmp_path)
    assert all(bt.SEG[s]["depth"] is None for s in ("S01", "S02", "S03")) and bt.DP is None and "depth_engine" not in bt.ENGINE_MD5
    assert bt.shot_key_parts(bt.SEG["S01"])["depth"] is None
    for d in (bt.CLIPS, bt.AUD, bt.QC): d.mkdir(parents=True, exist_ok=True)
    c0 = bt.TEMPLATE_CAM_CALLS[0]; bt.render_segment("S01")
    assert bt.TEMPLATE_CAM_CALLS[0] - c0 == 3 and not (bt.CLIPS / "S01.depth_proof.json").exists()   # flat path = template push
    rc, out = run(tmp_path, "108x192", "--check"); assert rc == 0 and "DEPTH" not in out, out

def test_flat_output_unchanged_by_refactor(tmp_path):
    """the plate_frame refactor must not change a flat shot's pixels: same clip bytes as the pre-depth template backup."""
    old = ROOT / "motion" / "superseded" / "build_template_v1.py.pre-depth-layer-2026-10-30"
    if not old.is_file(): pytest.skip("pre-depth backup missing")
    tex_plate(tmp_path, "p.png", 270, 480)
    write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=4, push=[1.0, 1.06])])
    outs = []
    for i, t in enumerate((old, TPL)):
        r = subprocess.run([PY, str(t), "--manifest", str(tmp_path / "m.json"), "--timeline", str(tmp_path / "t.json"), "--size", "108x192",
                            "--build-dir", str(tmp_path / f"b{i}"), "--clips-only", "--no-phone-qc", "--jobs", "1"], capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stdout + r.stderr
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tmp_path / f"b{i}" / "clips" / "S01.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        outs.append(raw)
    assert outs[0] == outs[1]

# ---------------------------------------------------------------- 7. planning WARN: back-to-back depth touching a character plate
def test_consecutive_depth_character_warning_fires(tmp_path):
    tex_plate(tmp_path, "a.png", 270, 480, 1); tex_plate(tmp_path, "b.png", 270, 480, 2); tex_plate(tmp_path, "c.png", 270, 480, 3)
    plates = {"A": ("a.png", ["S01"]), "B": ("b.png", ["S02"]), "C": ("c.png", ["S03"])}
    # (a) S01 depth -> S02 depth on a character plate (tagged in the MANIFEST) -> WARN, still plans (not a refusal)
    write_inputs(tmp_path, plates, [dict(id="S01", frames=3, depth=inline_depth(), scene_action="arrival"),
                                    dict(id="S02", frames=3, depth=inline_depth(), depth_ok_reason="owner asked"), dict(id="S03", frames=3)],
                 extra_rows={"B": dict(plate_type="character")})
    rc, out = run(tmp_path, "108x192", "--check")
    assert rc == 0 and "CHECK OK" in out and "WARN depth back-to-back on character plate(s): S01 -> S02 (character: ['S02'])" in out, out
    # (b) timeline-level character tag also counts
    write_inputs(tmp_path, plates, [dict(id="S01", frames=3, depth=inline_depth(), scene_action="arrival", character=True),
                                    dict(id="S02", frames=3, depth=inline_depth(), scene_action="escape"), dict(id="S03", frames=3)])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc == 0 and "WARN depth back-to-back" in out, out
    # (c) no warning: depth shots not adjacent, or adjacent but neither is a character plate
    write_inputs(tmp_path, plates, [dict(id="S01", frames=3, depth=inline_depth(), scene_action="arrival", character=True),
                                    dict(id="S02", frames=3), dict(id="S03", frames=3, depth=inline_depth(), scene_action="escape", character=True)])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc == 0 and "WARN depth back-to-back" not in out, out
    write_inputs(tmp_path, plates, [dict(id="S01", frames=3, depth=inline_depth(), scene_action="arrival"),
                                    dict(id="S02", frames=3, depth=inline_depth(), scene_action="escape"), dict(id="S03", frames=3)])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc == 0 and "WARN depth back-to-back" not in out, out
    # (d) a depth shot with no scene_action / depth_ok_reason gets a soft WARN
    write_inputs(tmp_path, plates, [dict(id="S01", frames=3, depth=inline_depth()), dict(id="S02", frames=3), dict(id="S03", frames=3)])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc == 0 and "WARN depth on S01 without scene_action / depth_ok_reason" in out, out

# ---------------------------------------------------------------- refusals that keep the single-camera rule honest
def test_depth_refuses_template_crop_and_foreign_plate_config(tmp_path):
    tex_plate(tmp_path, "p.png", 270, 480, 1); tex_plate(tmp_path, "q.png", 270, 480, 2)
    write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=3, depth=inline_depth(), crop={"center": [0.5, 0.5], "frac": 0.8})])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc != 0 and "template 'crop' + depth" in out, out
    cfg = inline_depth(); cfg["plate"] = str(tmp_path / "q.png"); (tmp_path / "d.json").write_text(json.dumps(cfg))
    write_inputs(tmp_path, {"P1": ("p.png", ["S01"])}, [dict(id="S01", frames=3, depth="d.json")])
    rc, out = run(tmp_path, "108x192", "--check"); assert rc != 0 and "points at another plate" in out, out
