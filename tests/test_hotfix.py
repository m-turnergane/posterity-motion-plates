"""Regression tests for the v0.3.1 reliability hotfix (one or more per fix)."""
import os, sys, json, glob, shutil, subprocess, importlib, numpy as np, cv2, pytest, yaml
from motionplates.core import engine, approval, encode
from motionplates.core.validate import validate_recipe
from motionplates.core.recipe import load_recipe
HERE = os.path.dirname(__file__); RECIPE = os.path.join(HERE, "data", "test_recipe.yaml")

# ---- sklearn isolation -------------------------------------------------------------------------------------------------------------------
def test_missing_sklearn_gives_clear_error(monkeypatch):
    from motionplates.authoring import suggest as S
    monkeypatch.setitem(sys.modules, "sklearn", None); monkeypatch.setitem(sys.modules, "sklearn.cluster", None)
    img = np.full((120, 68, 3), 100, np.uint8)
    with pytest.raises(S.MissingOptionalDependency, match=r"motionplates\[masks\]"): S.superpixels(img)

def test_core_import_does_not_need_sklearn():
    code = "import sys; sys.modules['sklearn']=None; import motionplates.cli, motionplates.core.engine, motionplates.authoring.suggest"
    r = subprocess.run([sys.executable, "-c", code], env=dict(os.environ, PYTHONPATH=os.path.join(HERE, "..", "src")), capture_output=True, text=True); assert r.returncode == 0, r.stderr

def test_masks_extra_declared():
    t = open(os.path.join(HERE, "..", "pyproject.toml")).read(); assert "masks" in t and "scikit-learn" in t
    core = t.split("[project.optional-dependencies]")[0]; assert "scikit-learn" not in core

# ---- approvals ----------------------------------------------------------------------------------------------------------------------------
def _rec(sha, **kw):
    r = dict(mp4_sha256=sha, approved_by="Muhammad Gane", approved_by_human=True, approved_at="2026-10-18T12:00:00-04:00", method="playback_qc_mobile"); r.update(kw); return r

def _write(adir, rec):
    os.makedirs(adir, exist_ok=True); p = os.path.join(adir, rec["mp4_sha256"] + ".json"); json.dump(rec, open(p, "w")); return p

def test_renderer_never_sets_approval(rendered):
    m, out = rendered; q = m["qc"]
    assert q["status"] == "REVIEW_REQUIRED" and q["playback_approved"] is False and len(m["mp4_sha256"]) == 64
    assert m["mp4_sha256"] == approval.sha256_file(m["mp4"]) and m["frames_sha1"]       # raw-frame hash kept for determinism
    assert not os.path.exists("approvals") or not glob.glob("approvals/*.json")

def test_recipe_cannot_carry_approval():
    R = load_recipe(RECIPE); R["qc"] = {"playback_approved": True, "approved_by": "editor", "approved_frames_sha1": "x"}
    P = validate_recipe(R, None, check_assets=False); assert sum("not allowed in recipes" in x for x in P) == 3

def test_recipe_claim_does_not_flip_status(synth, tmp_path):
    R = yaml.safe_load(open(RECIPE)); R["qc"] = dict(R.get("qc") or {}, playback_approved=True, approved_by="editor"); p = tmp_path / "r.yaml"; p.write_text(yaml.safe_dump(R))
    from motionplates.core.validate import RecipeError
    with pytest.raises(RecipeError): engine.render(str(p), str(tmp_path / "o"), plates_dir=synth, log=lambda *a: None)

def test_approval_bound_to_final_mp4_sha256(rendered, tmp_path):
    m, out = rendered; ad = str(tmp_path / "approvals")
    assert approval.verify_approval(m["mp4"], ad)[0] == "REVIEW_REQUIRED"
    _write(ad, _rec(m["mp4_sha256"])); assert approval.verify_approval(m["mp4"], ad)[0] == "PASS"
    other = tmp_path / "other.mp4"; shutil.copy(m["mp4"], other); open(other, "ab").write(b"\0")         # a different encode of the same frames is NOT approved
    assert approval.verify_approval(str(other), ad)[0] == "REVIEW_REQUIRED"

@pytest.mark.parametrize("kw", [dict(approved_by="grok-bot"), dict(approved_by="Codex agent"), dict(approved_by=""), dict(approved_by_human=False), dict(approved_at="")])
def test_agent_like_or_incomplete_records_rejected(rendered, tmp_path, kw):
    m, _ = rendered; ad = str(tmp_path / "a"); _write(ad, _rec(m["mp4_sha256"], **kw)); assert approval.verify_approval(m["mp4"], ad)[0] == "REVIEW_REQUIRED"

def test_record_filename_must_match_hash(rendered, tmp_path):
    m, _ = rendered; ad = tmp_path / "a"; ad.mkdir(); json.dump(_rec(m["mp4_sha256"]), open(ad / ("0" * 64 + ".json"), "w"))
    assert approval.check_approvals_dir(str(ad)) and approval.verify_approval(m["mp4"], str(ad))[0] == "REVIEW_REQUIRED"

def test_manifest_claiming_approval_without_record_fails_ci_check(rendered, tmp_path):
    m, _ = rendered; ad = str(tmp_path / "ap"); bad = json.loads(json.dumps(m, default=str)); bad["qc"]["playback_approved"] = True
    assert approval.check_manifest(bad, ad)                                                                    # no record -> problem
    st = json.loads(json.dumps(m, default=str)); st["qc"]["status"] = "PASS"; assert approval.check_manifest(st, ad)
    _write(ad, _rec(m["mp4_sha256"])); assert approval.check_manifest(bad, ad) == []                           # human record present -> consistent
    assert approval.check_manifest(json.loads(json.dumps(m, default=str)), ad) == []                          # honest manifest always fine

def test_check_manifests_cli(rendered, tmp_path):
    from motionplates.cli import main
    m, out = rendered; d = tmp_path / "ms"; d.mkdir(); bad = json.loads(json.dumps(m, default=str)); bad["qc"]["playback_approved"] = True; json.dump(bad, open(d / "x_manifest.json", "w"))
    assert main(["check-manifests", str(d), "--approvals", str(tmp_path / "none")]) == 3
    json.dump(m, open(d / "x_manifest.json", "w"), default=str); assert main(["check-manifests", str(d), "--approvals", str(tmp_path / "none")]) == 0

def test_renderer_refuses_to_write_into_approvals_dir(synth, tmp_path):
    with pytest.raises(PermissionError): engine.render(RECIPE, str(tmp_path / "approvals"), plates_dir=synth, log=lambda *a: None)
    assert not (tmp_path / "approvals").exists()

# ---- no orphaned temp files on failed verification ------------------------------------------------------------------------------------------
def test_failed_verification_leaves_no_tmp(tmp_path, monkeypatch):
    dst = str(tmp_path / "v.mp4")
    def boom(*a, **k): raise encode.EncodeError("injected verification failure")
    monkeypatch.setattr(encode, "verify_video", boom)
    with pytest.raises(encode.EncodeError):
        with encode.FFmpegWriter(dst, 64, 64, 10, preset="ultrafast") as w:
            for i in range(10): w.write(np.full((64, 64, 3), i * 10, np.uint8))
        w.finalize()
    assert os.listdir(tmp_path) == []

def test_engine_failed_verification_leaves_no_tmp(synth, tmp_path, monkeypatch):
    def boom(*a, **k): raise encode.EncodeError("injected")
    monkeypatch.setattr(encode, "verify_video", boom)
    with pytest.raises(encode.EncodeError): engine.render(RECIPE, str(tmp_path / "o"), plates_dir=synth, frames=6, log=lambda *a: None)
    assert not [f for f in os.listdir(tmp_path / "o") if ".tmp" in f or f.endswith("_animated.mp4")]

def test_midstream_failure_leaves_no_tmp(tmp_path):
    dst = str(tmp_path / "v.mp4")
    with pytest.raises(RuntimeError):
        with encode.FFmpegWriter(dst, 64, 64, 10, preset="ultrafast") as w:
            w.write(np.zeros((64, 64, 3), np.uint8)); raise RuntimeError("render crashed")
    assert os.listdir(tmp_path) == []

# ---- recursive validation --------------------------------------------------------------------------------------------------------------------
def test_validate_tree_recursive_finds_nested_bad_recipe(tmp_path):
    from motionplates.cli import validate_tree
    shutil.copytree(os.path.join(HERE, "..", "recipes"), tmp_path / "recipes"); n0, bad0 = validate_tree(str(tmp_path / "recipes")); assert bad0 == [] and n0 >= 6
    (tmp_path / "recipes" / "nested" / "deep").mkdir(parents=True); (tmp_path / "recipes" / "nested" / "deep" / "x.yaml").write_text("name: x\nplate: {file: a.png}\neffects: [{type: nope}]\n")
    n, bad = validate_tree(str(tmp_path / "recipes")); assert n == n0 + 1 and any("deep" in b and "unknown type" in b for b in bad)

# ---- cartography: edge labels fade, vignette events ---------------------------------------------------------------------------------------
def test_edge_fade_function():
    from motionplates.cartography.engine import edge_fade
    assert edge_fade((540, 960), 1080, 1920) == 1.0 and edge_fade((-50, 960), 1080, 1920) == 0.0 and edge_fade((1130, 100), 1080, 1920) == 0.0
    assert 0 < edge_fade((20, 960), 1080, 1920) < 1

def _carto_mini(tmp_path, anchor):
    from test_cartography import mini
    R, b = mini(tmp_path, [{"id": "l", "do": "label", "at": 0.0, "anchor": "a", "text": "ZZZZ", "size": 30, "offset": [0, 0]}]); R["locations"]["a"] = anchor; return R, b

def test_offscreen_label_disappears_not_clamped(tmp_path):
    from motionplates.cartography.engine import Recipe, Renderer
    R, b = _carto_mini(tmp_path, [28, 50]); rc = Recipe(R, str(tmp_path)); rd = Renderer(rc, b); on = rd.frame(0.9).astype(int)
    R2, b2 = _carto_mini(tmp_path, [28, 50]); R2["locations"]["a"] = [-400, 50]; rc2 = Recipe(R2, str(tmp_path)); rd2 = Renderer(rc2, b2); rc2.base_w  # anchor far left of the map
    off = rd2.frame(0.9).astype(int); bare = rd2.frame(0.0).astype(int)
    assert np.abs(on - rd.frame(0.0).astype(int)).max() > 20                 # visible when the anchor is on screen
    assert np.abs(off - bare).max() <= 2                                      # gone when the anchor is off screen (previously clamped to the edge)

def test_vignette_event_no_longer_accepted(tmp_path):
    from test_cartography import mini
    from motionplates.cartography.engine import Recipe, RecipeError
    R, b = mini(tmp_path); R["events"].append({"do": "vignette", "at": 0.1, "dur": 0.3})
    with pytest.raises(RecipeError, match="unknown primitive"): Recipe(R, str(tmp_path))
