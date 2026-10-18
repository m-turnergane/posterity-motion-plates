"""Playback approval records. AGENTS MUST NOT CREATE OR EDIT THESE FILES; the renderer never writes or sets them.

An approval is a file  approvals/<mp4_sha256>.json  committed to git by a HUMAN (owner/editor) AFTER watching that exact encoded MP4 at phone size:
  {"mp4_sha256": "<64 hex, SHA-256 of the FINAL ENCODED MP4>", "approved_by": "<human name>", "approved_by_human": true,
   "approved_at": "<ISO8601>", "method": "playback_qc_mobile", "frames_sha1": "<optional raw-frame hash, informational>"}
The file name must equal mp4_sha256. frames_sha1 (raw frames, determinism) is kept in the manifest but does not grant approval: re-encoding changes the MP4 hash.
Validation fails when a manifest claims playback_approved / status PASS without a matching, valid record."""
import os, re, json, hashlib

APPROVALS_DIR = "approvals"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_AGENT_NAMES = re.compile(r"(agent|bot\b|grok|codex|gpt|claude|renderer|automat|pipeline|ci\b|script|motionplates|vellum|system)", re.I)

def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""): h.update(b)
    return h.hexdigest()

def record_problems(rec, expect_sha256=None, filename=None):
    P = []
    if not isinstance(rec, dict): return ["record is not a JSON object"]
    sha = rec.get("mp4_sha256")
    if not (isinstance(sha, str) and _SHA256.match(sha)): P.append("mp4_sha256 must be 64 lowercase hex chars (SHA-256 of the final encoded MP4)")
    if filename and sha and os.path.splitext(os.path.basename(filename))[0] != sha: P.append(f"file name must be <mp4_sha256>.json (got {os.path.basename(filename)})")
    if expect_sha256 and sha != expect_sha256: P.append("record is for a different MP4")
    who = rec.get("approved_by")
    if not (isinstance(who, str) and len(who.strip()) >= 3): P.append("approved_by must name a human approver")
    elif _AGENT_NAMES.search(who): P.append(f"approved_by {who!r} looks like an agent/automation, not a human")
    if rec.get("approved_by_human") is not True: P.append("approved_by_human must be true")
    if not rec.get("approved_at"): P.append("approved_at required")
    return P

def find_record(mp4_sha256, approvals_dir=APPROVALS_DIR):
    p = os.path.join(approvals_dir, mp4_sha256 + ".json")
    if not os.path.isfile(p): return None, ["no approval record " + p]
    try: rec = json.load(open(p))
    except Exception as e: return None, [f"unreadable approval record: {e!r}"]
    pr = record_problems(rec, mp4_sha256, p)
    return (rec if not pr else None), pr

def verify_approval(mp4_path, approvals_dir=APPROVALS_DIR):
    """-> (status, reason). PASS only with a valid record for the SHA-256 of this exact file. Read-only."""
    sha = sha256_file(mp4_path); rec, pr = find_record(sha, approvals_dir)
    if rec: return "PASS", f"playback approved by {rec['approved_by']} for mp4_sha256 {sha[:12]}"
    return "REVIEW_REQUIRED", "; ".join(pr)

def is_committed(path):
    """True if git tracks the file (approval must be committed by a human outside the render step)."""
    import subprocess
    try: return subprocess.run(["git", "ls-files", "--error-unmatch", path], capture_output=True, cwd=os.path.dirname(os.path.abspath(path)) or ".").returncode == 0
    except Exception: return False

def check_manifest(man, approvals_dir=APPROVALS_DIR, require_committed=False):
    """Problems list for a renderer-produced manifest: it must never claim approval without a matching record for ITS mp4_sha256."""
    P = []; q = man.get("qc", {}) or {}
    claims = q.get("playback_approved") is True or q.get("status") == "PASS" or man.get("status") == "PASS"
    if claims:
        sha = man.get("mp4_sha256")
        if not sha: return ["manifest claims approval but has no mp4_sha256"]
        rec, pr = find_record(sha, approvals_dir)
        if not rec: P += ["manifest claims playback approval without a valid approval record: " + "; ".join(pr)]
        elif require_committed and not is_committed(os.path.join(approvals_dir, sha + ".json")): P.append("approval record is not committed to git")
    return P

def check_approvals_dir(approvals_dir=APPROVALS_DIR, require_committed=False):
    P = []
    if not os.path.isdir(approvals_dir): return P
    for f in sorted(os.listdir(approvals_dir)):
        if not f.endswith(".json"): continue
        p = os.path.join(approvals_dir, f)
        try: rec = json.load(open(p))
        except Exception as e: P.append(f"{p}: unreadable ({e!r})"); continue
        P += [f"{p}: {x}" for x in record_problems(rec, filename=p)]
        if require_committed and not is_committed(p): P.append(f"{p}: not committed to git")
    return P

def assert_not_approvals_path(outdir, approvals_dir=APPROVALS_DIR):
    """The renderer refuses to write inside an approvals directory."""
    o = os.path.realpath(outdir)
    if os.path.basename(o) == APPROVALS_DIR or os.path.sep + APPROVALS_DIR + os.path.sep in o + os.path.sep or o.startswith(os.path.realpath(approvals_dir) + os.path.sep) or o == os.path.realpath(approvals_dir):
        raise PermissionError(f"renderer must not write into an approvals directory: {outdir}")
