"""Resample a decoded clip onto the 30 fps timeline.

Frames are read once, in order. Output time maps to a source presentation
time. There is no per-frame seek and no silent swap back to the still.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from motionplates.opening.camera import OUT_H, OUT_W


@dataclass
class Clip:
    frames: list[np.ndarray]
    fps: float
    path: str

    def __len__(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        if self.fps <= 0:
            return 0.0
        return len(self.frames) / self.fps

    def index_at(self, t: float) -> int:
        if not self.frames:
            raise RuntimeError(f"no frames decoded from {self.path}")
        idx = int(round(max(0.0, t) * self.fps))
        return min(idx, len(self.frames) - 1)

    def rgb_at(self, t: float) -> np.ndarray:
        frame = self.frames[self.index_at(t)]
        if frame.shape[1] == OUT_W and frame.shape[0] == OUT_H:
            return frame
        return cv2.resize(frame, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)


def load_clip(path: str) -> Clip:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"could not open clip {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frames: list[np.ndarray] = []
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    cap.release()
    if not frames:
        raise RuntimeError(f"clip decoded zero frames: {path}")
    if fps <= 0:
        raise RuntimeError(f"clip has no frame rate: {path}")
    return Clip(frames, fps, path)
