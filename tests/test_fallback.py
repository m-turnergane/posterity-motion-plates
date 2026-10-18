import os, json, shutil, pytest
from motionplates import fallback
from motionplates.core import approval
import test_hotfix as H

@pytest.fixture()
def kit(rendered, synth, tmp_path):
    m, out = rendered; d = tmp_path / "clips"; shutil.copytree(out, d); name = m["name"]
    mf = json.load(open(d / f"{name}_manifest.json")); mf["mp4"] = str(d / f"{name}_animated.mp4"); json.dump(mf, open(d / f"{name}_manifest.json", "w"))
    return dict(plate=os.path.join(synth, "synth.png"), dir=str(d), name=name, man=m, ad=str(tmp_path / "approvals"), size=tuple([m["output"]["W"], m["output"]["H"]]), fps=m["output"]["fps"])

def R(k, **kw): return fallback.resolve(k["plate"], k["dir"], k["name"], approvals_dir=k["ad"], size=k["size"], fps=k["fps"], **kw)

def test_unapproved_clip_falls_back_to_static_by_default(kit):
    r = R(kit); assert r["kind"] == "static" and "approval" in r["reason"] and r["path"] == kit["plate"]

def test_approved_clip_is_used(kit):
    H._write(kit["ad"], H._rec(kit["man"]["mp4_sha256"])); r = R(kit); assert r["kind"] == "clip" and r["approved"] is True

def test_preview_mode_uses_unapproved_but_flags_it(kit):
    r = R(kit, require_approval=False); assert r["kind"] == "clip" and r["approved"] is False

def test_missing_clip_falls_back(kit):
    os.remove(os.path.join(kit["dir"], kit["name"] + "_animated.mp4")); assert R(kit, require_approval=False)["kind"] == "static"

def test_corrupt_or_modified_clip_falls_back(kit):
    p = os.path.join(kit["dir"], kit["name"] + "_animated.mp4"); open(p, "ab").write(b"junk"); r = R(kit, require_approval=False); assert r["kind"] == "static" and "SHA-256" in r["reason"]

def test_truncated_clip_with_updated_hash_still_fails_verification(kit):
    p = os.path.join(kit["dir"], kit["name"] + "_animated.mp4"); data = open(p, "rb").read(); open(p, "wb").write(data[: len(data) // 2])
    mf = os.path.join(kit["dir"], kit["name"] + "_manifest.json"); j = json.load(open(mf)); j["mp4_sha256"] = approval.sha256_file(p); json.dump(j, open(mf, "w"))
    r = R(kit, require_approval=False); assert r["kind"] == "static" and "verification" in r["reason"]

def test_wrong_plate_falls_back(kit, tmp_path):
    other = tmp_path / "other.png"; shutil.copy(kit["plate"], other); open(other, "ab").write(b"x"); kit["plate"] = str(other); assert "different plate" in R(kit, require_approval=False)["reason"]

def test_slot_longer_than_clip_falls_back(kit):
    assert R(kit, require_approval=False, slot_seconds=99)["kind"] == "static"

def test_garbage_manifest_never_raises(kit):
    open(os.path.join(kit["dir"], kit["name"] + "_manifest.json"), "w").write("{nope"); assert R(kit, require_approval=False)["kind"] == "static"
