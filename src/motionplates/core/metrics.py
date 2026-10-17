import numpy as np

class MotionMeter:
    def __init__(self, thr=2):
        self.prev = None; self.mean = []; self.frac = []; self.thr = thr
    def push(self, f):
        cur = f.astype(np.int16)
        if self.prev is not None:
            d = np.abs(cur - self.prev); self.mean.append(float(d.mean())); self.frac.append(float((d.max(2) > self.thr).mean()))
        self.prev = cur
    def summary(self):
        return dict(mean_abs_frame_delta=float(np.mean(self.mean)), max_mean_abs_frame_delta=float(np.max(self.mean)),
                    mean_changed_pixel_fraction=float(np.mean(self.frac)), max_changed_pixel_fraction=float(np.max(self.frac)),
                    frames=len(self.mean) + 1, changed_threshold=self.thr)
