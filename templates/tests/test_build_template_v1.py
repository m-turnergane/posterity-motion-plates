"""Tests for build_template_v1.py + motion/guardrails.py pixel-density rule (EIC ruling 2026-10-30).

Run:  cd /workspace/posterity/motion/templates && /workspace/mpvenv/bin/python -m pytest -q tests/
Everything runs with --check (nothing renders); test plates are tiny flat PNGs written to pytest's tmp_path.
"""
import importlib.util, json, shutil, subprocess, sys
from pathlib import Path
import numpy as np, pytest
from PIL import Image

HERE = Path(__file__).resolve().parent; TPL = HERE.parent / "build_template_v1.py"; GRP = HERE.parent.parent / "guardrails.py"
PY = sys.executable
P05 = "/workspace/posterity/micro-anomaly/ugarit/plates/p05_coastal_town_raid_v2_OWNER.png"

def _gr():
    s = importlib.util.spec_from_file_location("gr_test", GRP); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
GR = _gr()

def plate(tmp, name, w, h):
    p = tmp / name; Image.new("RGB", (w, h), (90, 70, 50)).save(p, optimize=True); return p

def run_check(tmp, plates, shots, size, target=None):
    """plates: {plate_id: (filename, [shot ids])}; shots: [(id, push, crop|None)]"""
    rows = [dict(plate_id=k, scene_id="SC", shot_ids=v[1], prompt="t", aspect="", target_resolution=target or "",
                 expected_filename=v[0], refs=[], notes="") for k, v in plates.items()]
    (tmp / "m.json").write_text(json.dumps({"plates_dir": str(tmp), "plates": rows}))
    tl = dict(name="t", fps=30, shots=[dict(id=i, seconds=1.0, push=list(p), **({"crop": c} if c else {})) for i, p, c in shots])
    (tmp / "t.json").write_text(json.dumps(tl))
    r = subprocess.run([PY, str(TPL), "--manifest", str(tmp / "m.json"), "--timeline", str(tmp / "t.json"), "--size", size,
                        "--build-dir", str(tmp / "build"), "--check"], capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr

# ---------------------------------------------------------------- guardrails.check_pixel_density (unit)
def test_portrait_plate_into_16x9_fails_204():
    d = GR.check_pixel_density((941, 1672), (1920, 1080), (1.0, 1.0), mode="measure")
    assert not d["pass"] and d["ratio"] == pytest.approx(2.040, abs=0.002)
    with pytest.raises(GR.GuardrailError, match=r"2\.040 output px per source px"):
        GR.check_pixel_density((941, 1672), (1920, 1080), (1.0, 1.0))            # default = refuse

def test_native_16x9_2560_push106_passes():
    d = GR.check_pixel_density((2560, 1440), (1920, 1080), (1.00, 1.06))
    assert d["pass"] and d["ratio"] == pytest.approx(0.795, abs=0.001)

def test_short_plate_1080x1920_push106_passes():
    d = GR.check_pixel_density((1080, 1920), (1080, 1920), (1.00, 1.06))
    assert d["pass"] and d["ratio"] == pytest.approx(1.06, abs=0.001)

def test_small_plate_fails_on_shorts():
    with pytest.raises(GR.GuardrailError):
        GR.check_pixel_density((640, 1138), (1080, 1920), (1.00, 1.06))   # 1.789

def test_max_push_and_both_axes_used():
    a = GR.check_pixel_density((1440, 1440), (1920, 1080), (1.06, 1.00), mode="measure")   # reversed push -> max 1.06
    assert a["ratio_x"] == pytest.approx(1920 / 1440 * 1.06, abs=1e-3) and a["ratio"] == a["ratio_x"] and a["ratio_x"] > a["ratio_y"] - 1e-9
    assert a["push_max"] == pytest.approx(1.06)

def test_real_file_size_not_nominal(tmp_path):
    p = plate(tmp_path, "nominal_2560.png", 941, 1672)                    # named / claimed 2560 but really 941x1672
    d = GR.check_pixel_density(str(p), (1920, 1080), (1.0, 1.06), mode="measure")
    assert d["plate_wh"] == [941, 1672] and not d["pass"]

def test_check_shot_and_check_crop_zoom_call_density():
    with pytest.raises(GR.GuardrailError, match="output px per source px"):
        GR.check_crop_zoom(1.0, plate_wh=(941, 1672), out_wh=(1920, 1080))
    with pytest.raises(GR.GuardrailError, match="output px per source px"):
        GR.check_shot(dict(name="x", push=[1.0, 1.06]), np.zeros((1672, 941, 3), np.uint8), out_wh=(1920, 1080))
    r = GR.check_shot(dict(name="x", push=[1.0, 1.06]), np.zeros((1672, 941, 3), np.uint8), out_wh=(1080, 1920))
    assert [c["check"] for c in r] == ["crop_zoom", "pixel_density"] and r[1]["ratio"] == pytest.approx(1.217, abs=0.001)

# ---------------------------------------------------------------- P05 locked exemption (exact shot only)
P05_CFG = dict(name="p05v2_sun_glitter_v1d", plate=P05, push=[1.6, 1.6])

@pytest.mark.skipif(not Path(P05).is_file(), reason="P05 OWNER plate not on this box")
def test_p05_exact_shot_density_waived_warn_only(capsys):
    r = GR.check_shot(dict(P05_CFG), None, mode="refuse", out_wh=(1080, 1920))     # must NOT raise
    d = [c for c in r if c["check"] == "pixel_density"][0]
    assert d["ratio"] == pytest.approx(1.6, abs=1e-3) and not d["pass"] and d.get("waived")
    assert "WAIVED" in capsys.readouterr().err

@pytest.mark.skipif(not Path(P05).is_file(), reason="P05 OWNER plate not on this box")
def test_p05_exemption_not_broadened(tmp_path):
    with pytest.raises(GR.GuardrailError):                                            # same shot, long-form frame
        GR.check_shot(dict(P05_CFG), None, out_wh=(1920, 1080))
    with pytest.raises(GR.GuardrailError):                                            # other name
        GR.check_shot(dict(P05_CFG, name="p05v2_sun_glitter_v1e"), None, out_wh=(1080, 1920))
    cp = tmp_path / "p05_copy.png"; Image.open(P05).save(cp)                          # other file (path/md5)
    with pytest.raises(GR.GuardrailError):
        GR.check_shot(dict(P05_CFG, plate=str(cp)), None, out_wh=(1080, 1920))

@pytest.mark.skipif(not Path(P05).is_file(), reason="P05 OWNER plate not on this box")
def test_template_refuses_p05_style_shot(tmp_path):
    rows = [dict(plate_id="P05", scene_id="SC", shot_ids=["p05v2_sun_glitter_v1d"], prompt="", aspect="", target_resolution="",
                 expected_filename=Path(P05).name, refs=[], notes="")]
    (tmp_path / "m.json").write_text(json.dumps({"plates_dir": str(Path(P05).parent), "plates": rows}))
    (tmp_path / "t.json").write_text(json.dumps(dict(name="t", fps=30, shots=[dict(id="p05v2_sun_glitter_v1d", seconds=1.0, push=[1.6, 1.6])])))
    r = subprocess.run([PY, str(TPL), "--manifest", str(tmp_path / "m.json"), "--timeline", str(tmp_path / "t.json"), "--size", "1080x1920",
                        "--build-dir", str(tmp_path / "b"), "--check"], capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "pixel density" in r.stderr and "1.600" in r.stderr      # no waiver path in the template

# ---------------------------------------------------------------- template integration (--check, nothing renders)
def test_template_refuses_portrait_plate_longform_lists_every_shot(tmp_path):
    plate(tmp_path, "a.png", 941, 1672); plate(tmp_path, "b.png", 2560, 1440); plate(tmp_path, "c.png", 941, 1672)
    rc, out = run_check(tmp_path, {"A": ("a.png", ["S01"]), "B": ("b.png", ["S02"]), "C": ("c.png", ["S03"])},
                        [("S01", (1.0, 1.0), None), ("S02", (1.0, 1.06), None), ("S03", (1.0, 1.06), None)], "1920x1080")
    assert rc != 0 and "GUARDRAIL REFUSED (pixel density" in out and "2/3 shot(s)" in out
    assert "S01 (A a.png): 2.040" in out and "S03 (C c.png): 2.163" in out and "S02 (" not in out
    assert not (tmp_path / "build").exists()                                                  # refused before anything rendered

def test_template_native_16x9_push106_passes(tmp_path):
    plate(tmp_path, "b.png", 2560, 1440)
    rc, out = run_check(tmp_path, {"B": ("b.png", ["S01"])}, [("S01", (1.0, 1.06), None)], "1920x1080", target="2560x1440")
    assert rc == 0 and "CHECK OK" in out and "density 0.795" in out

def test_template_short_1080x1920_push106_passes(tmp_path):
    plate(tmp_path, "s.png", 1080, 1920)
    rc, out = run_check(tmp_path, {"S": ("s.png", ["S01"])}, [("S01", (1.0, 1.06), None)], "1080x1920")
    assert rc == 0 and "CHECK OK" in out and "density 1.060" in out

def test_template_small_plate_fails_on_shorts(tmp_path):
    plate(tmp_path, "s.png", 640, 1138)
    rc, out = run_check(tmp_path, {"S": ("s.png", ["S01"])}, [("S01", (1.0, 1.06), None)], "1080x1920")
    assert rc != 0 and "pixel density" in out and "1.789" in out

def test_template_crop_counts_toward_density(tmp_path):
    plate(tmp_path, "b.png", 2560, 1440); plate(tmp_path, "s.png", 1280, 720)
    rc, out = run_check(tmp_path, {"B": ("b.png", ["S01"])}, [("S01", (1.0, 1.06), {"center": [0.5, 0.5], "frac": 0.8})], "1920x1080")
    assert rc == 0 and "zoom 1.325x density 0.994" in out
    rc, out = run_check(tmp_path, {"S": ("s.png", ["S01"])}, [("S01", (1.0, 1.06), {"center": [0.5, 0.5], "frac": 0.9})], "1920x1080")
    assert rc != 0 and "max crop/push zoom" not in out and "1.767" in out   # zoom 1.178 ok, density refuses

def test_examples_still_exit_2_on_missing_plates(tmp_path):
    ex = HERE.parent / "examples"
    r = subprocess.run([PY, str(TPL), "--manifest", str(ex / "example_manifest.json"), "--timeline", str(ex / "example_timeline.json"),
                        "--size", "1920x1080", "--build-dir", str(tmp_path / "b"), "--check"], capture_output=True, text=True, timeout=120)
    assert r.returncode == 2 and "3/3 manifest plate file(s) missing" in r.stderr
