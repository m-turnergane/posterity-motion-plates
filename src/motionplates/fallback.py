"""Editor build helper: swap a static plate for its motion clip with AUTOMATIC fallback to the static PNG.
resolve(plate_png, clip_dir, name, ...) NEVER raises and never returns a clip that fails any check; every refusal is reported in `reason`.
A clip is used only if: manifest + mp4 exist; mp4 SHA-256 == manifest.mp4_sha256 (untouched since render); the manifest's plate md5 == the md5 of the plate
you are swapping (clip was baked on THIS plate); status is not FAIL/PROXY; ffprobe+full decode verify (size, fps, frames, yuv420p); duration >= the slot you need;
and (default) a valid human approval record approvals/<mp4_sha256>.json exists (owner playback QC). With require_approval=False (preview builds only) a
REVIEW_REQUIRED clip may be used, and the result is flagged approved=False so the build can refuse to publish."""
import os, json, hashlib
from .core.encode import verify_video, EncodeError
from .core.approval import sha256_file, verify_approval

def _md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def resolve(plate_png, clip_dir, name, slot_seconds=None, require_approval=True, approvals_dir="approvals", size=(1080, 1920), fps=30):
    static = dict(kind="static", path=plate_png, approved=None, reason="")
    def fallback(why): d = dict(static); d["reason"] = why; return d
    try:
        if not os.path.isfile(plate_png): return fallback("static plate missing (build must fail loudly, there is no fallback)") | dict(kind="MISSING")
        mp4 = os.path.join(clip_dir, f"{name}_animated.mp4"); mf = os.path.join(clip_dir, f"{name}_manifest.json")
        if not os.path.isfile(mp4) or not os.path.isfile(mf): return fallback("no clip/manifest")
        man = json.load(open(mf)); q = man.get("qc", {}) or {}
        if q.get("status") not in ("REVIEW_REQUIRED", "PASS"): return fallback(f"manifest status {q.get('status')!r}")
        if man.get("mp4_sha256") != sha256_file(mp4): return fallback("mp4 SHA-256 differs from manifest (file changed after render)")
        if (man.get("plate") or {}).get("md5") != _md5(plate_png): return fallback("plate md5 differs: clip was baked on a different plate")
        o = man.get("output", {}); n = int(o.get("frames", 0))
        try: verify_video(mp4, size[0], size[1], fps, n)
        except EncodeError as e: return fallback(f"clip failed verification: {str(e)[:160]}")
        if slot_seconds is not None and n / fps + 1e-6 < slot_seconds: return fallback(f"clip {n / fps:.2f}s shorter than slot {slot_seconds:.2f}s")
        st, why = verify_approval(mp4, approvals_dir)
        if require_approval and st != "PASS": return fallback("no valid human approval record: " + why)
        return dict(kind="clip", path=mp4, approved=(st == "PASS"), reason=("approved: " if st == "PASS" else "UNAPPROVED preview only: ") + why, frames=n, mp4_sha256=man["mp4_sha256"])
    except Exception as e:     # any surprise -> static plate
        return fallback(f"unexpected {type(e).__name__}: {e}")
