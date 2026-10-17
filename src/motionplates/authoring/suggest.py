"""Automatic mask suggestions (authoring aid, classical CV only). The output is a *proposal list for human review*, never trusted automatically.
 methods: 'regions'  superpixels (k-means in Lab+xy) merged along weak edges (Felzenszwalb-like agglomeration) -> n depth-layer candidates
          'saliency' spectral-residual saliency (numpy FFT) -> salient blobs
          'box'      GrabCut seeded by a rough box [x0,y0,x1,y1] -> one refined polygon (the 'click-and-refine' path)
 every candidate carries cues useful for depth ordering: centroid y, sharpness (Laplacian variance), mean saliency, area."""
import cv2, numpy as np

def _lab_small(img, max_w=270):
    s = max_w / img.shape[1]; sm = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA); return sm, cv2.cvtColor(sm, cv2.COLOR_RGB2LAB).astype(np.float32), s

def superpixels(img, k=420, compact=3.5, seed=0):
    from sklearn.cluster import MiniBatchKMeans
    sm, lab, s = _lab_small(img); lab = cv2.GaussianBlur(lab, (0, 0), 1.6); h, w = lab.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    feat = np.dstack([lab, compact * xx * (255 / w) * 0.5, compact * yy * (255 / h) * 0.5]).reshape(-1, 5)
    km = MiniBatchKMeans(n_clusters=k, random_state=seed, n_init=1, batch_size=4096, max_iter=30).fit(feat)
    lab_img = km.labels_.reshape(h, w); n, cc = cv2.connectedComponents((lab_img >= 0).astype(np.uint8))      # make labels spatially connected
    out = np.zeros_like(lab_img); nxt = 0
    for l in np.unique(lab_img):
        m = (lab_img == l).astype(np.uint8); nn, c = cv2.connectedComponents(m)
        for j in range(1, nn): out[c == j] = nxt; nxt += 1
    return out, sm, lab

def merge_regions(labels, lab, n_target=10):
    """agglomerative merge: repeatedly join the pair of neighbouring regions with the weakest shared boundary (colour step + gradient)."""
    n = labels.max() + 1; g = cv2.Laplacian(cv2.GaussianBlur(lab[..., 0], (0, 0), 1.0), cv2.CV_32F); g = np.abs(g)
    area = np.bincount(labels.ravel(), minlength=n).astype(np.float64); mean = np.zeros((n, 3))
    for c in range(3): mean[:, c] = np.bincount(labels.ravel(), weights=lab[..., c].ravel(), minlength=n) / np.maximum(area, 1)
    edges = {}
    for dy, dx in ((0, 1), (1, 0)):
        a = labels[:labels.shape[0] - dy, :labels.shape[1] - dx]; b = labels[dy:, dx:]; d = a != b
        for p, q, gv in zip(a[d], b[d], np.maximum(g[:g.shape[0] - dy, :g.shape[1] - dx][d], g[dy:, dx:][d])):
            k = (min(p, q), max(p, q)); e = edges.setdefault(k, [0, 0.0]); e[0] += 1; e[1] += gv
    parent = list(range(n))
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    alive = n
    import heapq
    def w(p, q, e): return float(np.linalg.norm(mean[p] - mean[q]) + 0.6 * e[1] / max(e[0], 1)) * (1 + 6.0 / max(min(area[p], area[q]) ** 0.5, 1))
    heap = [(w(p, q, e), p, q) for (p, q), e in edges.items()]; heapq.heapify(heap)
    while alive > n_target and heap:
        wt, p, q = heapq.heappop(heap); rp, rq = find(p), find(q)
        if rp == rq: continue
        e = edges.get((min(rp, rq), max(rp, rq)));
        if e is None: continue
        if abs(wt - w(rp, rq, e)) > 1e-6 and (p != rp or q != rq): 
            heapq.heappush(heap, (w(rp, rq, e), rp, rq)); continue
        parent[rq] = rp; alive -= 1; tot = area[rp] + area[rq]; mean[rp] = (mean[rp] * area[rp] + mean[rq] * area[rq]) / tot; area[rp] = tot
        for (a_, b_), ee in list(edges.items()):
            if rq in (a_, b_):
                other = b_ if a_ == rq else a_; del edges[(a_, b_)]
                if other == rp: continue
                k = (min(rp, other), max(rp, other)); t = edges.setdefault(k, [0, 0.0]); t[0] += ee[0]; t[1] += ee[1]; heapq.heappush(heap, (w(rp, other, t), rp, other))
    roots = np.array([find(i) for i in range(n)]); return roots[labels]

def spectral_saliency(img):
    g = cv2.cvtColor(cv2.resize(img, (128, 228)), cv2.COLOR_RGB2GRAY).astype(np.float32); F = np.fft.fft2(g); A = np.abs(F); P = np.angle(F)
    L = np.log(A + 1e-6); R = L - cv2.blur(L, (3, 3)); S = np.abs(np.fft.ifft2(np.exp(R + 1j * P))) ** 2; S = cv2.GaussianBlur(S, (0, 0), 3); S = (S - S.min()) / (S.max() - S.min() + 1e-9)
    return cv2.resize(S, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)

def _poly(mask, eps=2.0, min_area=300):
    cnt, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnt: return None
    c = max(cnt, key=cv2.contourArea)
    if cv2.contourArea(c) < min_area: return None
    return cv2.approxPolyDP(c, eps, True).reshape(-1, 2).tolist()

def candidates(img, method="regions", n=10, **kw):
    H, W = img.shape[:2]; sal = spectral_saliency(img); gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); lap = np.abs(cv2.Laplacian(gray, cv2.CV_32F)); out = []
    if method == "regions":
        lab_, sm, lab = superpixels(img, kw.get("k", 420)); mg = merge_regions(lab_, lab, n_target=n); mg = cv2.resize(mg.astype(np.int32).astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST).astype(np.int32)
        masks = [(mg == r) for r in np.unique(mg)]
    elif method == "saliency":
        t = float(np.percentile(sal, 100 - kw.get("top_percent", 30))); b = (sal > t).astype(np.uint8); b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8)); nn, c, st, _ = cv2.connectedComponentsWithStats(b)
        masks = [c == i for i in np.argsort(-st[1:, 4])[:n] + 1]
    elif method == "box":
        x0, y0, x1, y1 = kw["box"]; gc = np.full((H, W), cv2.GC_BGD, np.uint8); gc[y0:y1, x0:x1] = cv2.GC_PR_FGD; pad = int(0.15 * min(x1 - x0, y1 - y0)); gc[y0 + pad:y1 - pad, x0 + pad:x1 - pad] = cv2.GC_PR_FGD
        cv2.setRNGSeed(1234); cv2.grabCut(np.ascontiguousarray(img[..., ::-1]), gc, None, np.zeros((1, 65)), np.zeros((1, 65)), 5, cv2.GC_INIT_WITH_MASK); masks = [(gc == 1) | (gc == 3)]
    else: raise ValueError(method)
    for i, m in enumerate(masks):
        a = float(m.mean())
        if a < 0.004: continue
        p = _poly(m);
        if p is None: continue
        ys, xs = np.nonzero(m)
        out.append(dict(id=f"{method}_{i}", polygon=p, mask=m, area_frac=round(a, 4), centroid=[float(xs.mean()), float(ys.mean())], sharpness=float(lap[m].mean()), saliency=float(sal[m].mean()), method=method))
    return out

def iou(a, b): return float((a & b).sum() / max((a | b).sum(), 1))

def best_match(cands, target):
    """best single candidate and greedy union (<=4 regions) IoU against a target boolean mask (used to evaluate the suggester against hand-authored masks)."""
    singles = sorted(((iou(c["mask"], target), c["id"]) for c in cands), reverse=True)[:1]
    cur = np.zeros_like(target); chosen = []; best = 0.0
    for _ in range(4):
        gain = [(iou(cur | c["mask"], target), c["id"]) for c in cands if c["id"] not in chosen]
        if not gain: break
        g, cid = max(gain)
        if g <= best + 1e-4: break
        best = g; chosen.append(cid); cur |= next(c["mask"] for c in cands if c["id"] == cid)
    return dict(best_single_iou=round(singles[0][0], 3) if singles else 0, best_single=singles[0][1] if singles else None, union_iou=round(best, 3), union_of=chosen)

def overlay(img, cands, path):
    o = img.copy().astype(np.float32); rng = np.random.default_rng(3); H, W = img.shape[:2]
    for c in cands:
        col = rng.uniform(60, 255, 3); m = c["mask"]; o[m] = o[m] * 0.55 + col * 0.45
    o = np.clip(o, 0, 255).astype(np.uint8)
    for c in cands:
        cv2.polylines(o, [np.array(c["polygon"], np.int32)], True, (255, 255, 255), 2); cx, cy = map(int, c["centroid"]); cv2.putText(o, c["id"].split("_")[-1], (cx - 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 5); cv2.putText(o, c["id"].split("_")[-1], (cx - 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2)
    cv2.imwrite(path, cv2.cvtColor(o, cv2.COLOR_RGB2BGR))

def to_yaml_snippet(cands):
    """review-ready YAML: layers sorted far->near by (sharpness, centroid y) cue; every entry marked `review: true`."""
    lines = ["# SUGGESTED layer candidates — review every polygon, delete what you do not need, set depth by eye", "layers:"]
    for c in sorted(cands, key=lambda c: (c["centroid"][1] * 0.0 + c["sharpness"])):
        lines.append(f"  - name: {c['id']}   # area {c['area_frac']*100:.1f}%  sharpness {c['sharpness']:.1f}  saliency {c['saliency']:.2f}  review: true"); lines.append(f"    depth: {0.3 if c['centroid'][1] < 1000 else 0.8}"); lines.append("    polygons:"); lines.append("      - " + str([[int(x), int(y)] for x, y in c["polygon"]]).replace(" ", ""))
    return "\n".join(lines)
