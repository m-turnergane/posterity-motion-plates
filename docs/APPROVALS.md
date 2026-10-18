# Playback approval (human-only)

* The renderer produces **FAIL or REVIEW_REQUIRED, never PASS**. Manifests always carry `qc.playback_approved: false`, `mp4_sha256` (SHA-256 of the FINAL ENCODED MP4) and `frames_sha1` (raw frames; determinism only, it does not grant approval).
* Approval = a file `approvals/<mp4_sha256>.json` **committed by a human** after watching that exact MP4 at phone size:
  `{"mp4_sha256": "...", "approved_by": "<human name>", "approved_by_human": true, "approved_at": "<ISO8601>", "method": "playback_qc_mobile"}`
* **Agents (and the render step) must never create, edit or delete files in `approvals/`.** The renderer refuses to write into any directory named `approvals`; recipes may not contain `qc.playback_approved/approved_by/...` (validation error).
* `motionplates verify-approval FILE.mp4` (read-only) reports PASS only for a valid record of that exact file. Re-encoding changes the hash and voids the approval.
* CI (`motionplates check-manifests . --require-committed`) fails when a manifest claims approval/PASS with no matching, valid, git-tracked record, or when any record is malformed, misnamed, names an agent-like approver, or lacks `approved_by_human: true`.
* Limit of the design: a file check cannot prove who typed a record; the guard is review of the commit that adds it (require PR review/CODEOWNERS for `approvals/`, see docs/BRANCH-PROTECTION.md).
