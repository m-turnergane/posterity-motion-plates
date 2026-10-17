"""QC enforcement: individual checks -> overall status. Automated checks can FAIL a render or demand review; they can never approve it.
Status values: FAIL (output rejected, nonzero exit) | REVIEW_REQUIRED (automated checks passed or have warnings; human playback QC pending) | PASS (only when
the recipe carries qc.playback_approved: true bound to the exact render via qc.approved_frames_sha1)."""
import cv2, numpy as np

PASS, REVIEW, FAIL = "PASS", "REVIEW_REQUIRED", "FAIL"
_ORDER = {PASS: 0, REVIEW: 1, FAIL: 2}

class QC:
    def __init__(self): self.checks = []
    def add(self, name, status, value=None, limit=None, note=""):
        self.checks.append(dict(name=name, status=status, value=value, limit=limit, note=note))
    def check_max(self, name, value, review=None, fail=None, note=""):
        s = PASS
        if review is not None and value > review: s = REVIEW
        if fail is not None and value > fail: s = FAIL
        self.add(name, s, value, dict(review=review, fail=fail), note)
    def check_min(self, name, value, review=None, fail=None, note=""):
        s = PASS
        if review is not None and value < review: s = REVIEW
        if fail is not None and value < fail: s = FAIL
        self.add(name, s, value, dict(review_below=review, fail_below=fail), note)
    def worst(self): return max((c["status"] for c in self.checks), key=lambda s: _ORDER[s], default=PASS)
    def final(self, recipe, frames_sha1, motion_plate=True):
        """Final status. motion plates are capped at REVIEW_REQUIRED until playback QC approval bound to this exact render."""
        w = self.worst(); q = (recipe.get("qc") or {})
        if w == FAIL: return FAIL, "automated check failed"
        approved = q.get("playback_approved") is True and q.get("approved_frames_sha1") == frames_sha1 and bool(q.get("approved_by"))
        warns = [c["name"] for c in self.checks if c["status"] == REVIEW]
        if approved: return PASS, "playback QC approved for this exact render" + (f" (automated warnings acknowledged: {len(warns)})" if warns else "")
        why = "no playback-QC approval" if not q.get("playback_approved") else "approval does not match this render (approved_frames_sha1 differs) or approved_by missing"
        return REVIEW, why + (f"; {len(warns)} automated warning(s)" if warns else "") + " - automated metrics never count as visual approval"

def mask_diagnostics(stack, base, qc):
    """Per layer/element: coverage, holes in the matte, edge-halo score (rim colour vs plate), overlap with other layers, disocclusion fill area."""
    H, W = base.shape[:2]; out = {}; bf = base.astype(np.float32); names = [l.name for l in stack.layers if l.kind != "bg"]
    hard = {l.name: (l.alpha > 0.5) for l in stack.layers if l.kind != "bg"}
    for l in stack.layers:
        if l.kind == "bg": continue
        a = l.alpha; m = a > 0.5; cov = float(m.mean())
        filled = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); filled = _fill_holes(filled)
        holes = (filled > 0) & (~m); n, lab, st, _ = cv2.connectedComponentsWithStats(holes.astype(np.uint8)); big = [int(s[4]) for s in st[1:] if s[4] >= 25]
        rim = (a > 0.05) & (a < 0.95); rim_px = int(rim.sum())
        # halo: how far the rim pixels of this layer differ from the plate (the clean plate / layer rgb is sampled at the same place)
        halo = float(np.abs(l.rgb[rim] - bf[rim]).mean()) if rim_px else 0.0
        ov = {n2: float((hard[l.name] & hard[n2]).sum() / max(hard[l.name].sum(), 1)) for n2 in names if n2 != l.name and l.kind == "layer" and (hard[l.name] & hard[n2]).any()}
        # thin slivers: parts of the matte narrower than 3px (jagged / broken edges)
        er = cv2.erode(m.astype(np.uint8), np.ones((3, 3), np.uint8)); sliver = float(((m) & (cv2.dilate(er, np.ones((3, 3), np.uint8)) == 0)).sum() / max(m.sum(), 1))
        out[l.name] = dict(kind=l.kind, coverage=round(cov, 4), matte_holes=len(big), matte_hole_px=sum(big), rim_px=rim_px, rim_colour_diff_vs_plate=round(halo, 2), overlap_with=ov, sliver_fraction=round(sliver, 4))
        if cov < 0.0005: qc.add(f"mask:{l.name}:coverage", FAIL, cov, ">0.0005", "mask is (almost) empty")
        elif cov > 0.85: qc.add(f"mask:{l.name}:coverage", REVIEW, cov, "<0.85", "mask covers most of the frame")
        qc.check_max(f"mask:{l.name}:matte_holes", len(big), review=0, note="enclosed holes in the matte (px>=25)")
        qc.check_max(f"mask:{l.name}:halo", halo, review=14.0, fail=40.0, note="mean |layer rgb - plate| on the feather rim; high = visible halo risk when the layer moves")
        qc.check_max(f"mask:{l.name}:sliver_fraction", out[l.name]["sliver_fraction"], review=0.12, note="share of matte thinner than 3 px")
        for n2, f in ov.items():
            if f > 0.6: qc.add(f"mask:{l.name}:overlap:{n2}", REVIEW, round(f, 3), "<0.6", "layers overlap strongly (check depth ordering)")
    bh = stack.masks.get("bg_hole"); out["_disocclusion_bg_hole_fraction"] = float(bh.mean()) if bh is not None else 0.0
    if bh is not None: qc.check_max("disocclusion:bg_hole_fraction", out["_disocclusion_bg_hole_fraction"], review=0.5, note="area of the background that is inpainted (revealed only by parallax)")
    return out

def _fill_holes(m):
    h, w = m.shape; ff = np.pad(m, 1).copy(); mask = np.zeros((h + 4, w + 4), np.uint8); cv2.floodFill(ff, mask, (0, 0), 2)
    return ((ff[1:-1, 1:-1] != 2) | (m > 0)).astype(np.uint8)
