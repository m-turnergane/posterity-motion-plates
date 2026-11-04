"""Sampler, ink, act card, and clip cadence for the opening's second pass."""

import numpy as np
import cv2

from motionplates.opening.camera import cover_sample, cover_window, legacy_window_sample
from motionplates.opening.clip import Clip
from motionplates.opening.intro import ACT_AT, InkMark, Intro, act_card


def _integer_sample(plate, z, cx, cy, out_w, out_h):
    h, w = plate.shape[:2]
    cw, ch = w / z, h / z
    x0 = min(max(cx * w - cw / 2.0, 0.0), w - cw)
    y0 = min(max(cy * h - ch / 2.0, 0.0), h - ch)
    crop = plate[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    return cv2.resize(crop, (out_w, out_h), interpolation=cv2.INTER_LINEAR)


def test_float_sample_moves_when_integer_crop_does_not():
    h, w = 180, 320
    yy, xx = np.mgrid[0:h, 0:w]
    plate = np.dstack([(xx * 3) % 256, (yy * 5) % 256, np.full((h, w), 40)]).astype(np.uint8)
    a = _integer_sample(plate, 1.2, 0.50, 0.50, 160, 90)
    b = _integer_sample(plate, 1.2, 0.5005, 0.50, 160, 90)
    c = legacy_window_sample(plate, 1.2, 0.50, 0.50, 160, 90)
    d = legacy_window_sample(plate, 1.2, 0.5005, 0.50, 160, 90)
    assert np.array_equal(a, b)
    assert not np.array_equal(c, d)


def test_cover_at_rest_does_not_upscale_a_large_plate():
    cam = cover_window(2752, 1536, 1.0, 0.5, 0.5)
    assert cam.cw >= 1920 - 1e-6
    assert cam.ch >= 1080 - 1e-6
    assert not cam.upscales
    tight = cover_window(2752, 1536, 1.0 / (1080 / 1536), 0.35, 0.65)
    assert abs(tight.cw - 1920) < 1.5
    assert abs(tight.ch - 1080) < 1.5


def test_cover_sample_is_deterministic():
    rng = np.random.default_rng(4)
    plate = rng.integers(0, 255, (90, 160, 3), dtype=np.uint8)
    a = cover_sample(plate, 1.0, 0.4, 0.6, 80, 45)
    b = cover_sample(plate, 1.0, 0.4, 0.6, 80, 45)
    assert np.array_equal(a, b)
    assert a.shape == (45, 80, 3)


def test_ink_settles_on_the_mask_and_the_front_is_ragged():
    alpha = np.zeros((90, 140), np.uint8)
    alpha[25:65, 20:120] = 255
    mark = InkMark(alpha, 1611)
    mid = mark.at(0.45)
    partial = ((mid > 0.05) & (mid < 0.85)).any(axis=0)
    assert int(partial.sum()) > 2
    done = mark.at(1.0)
    assert done[45, 70] > 0.8
    assert done[2, 2] == 0
    assert done[45, 10] == 0


def test_act_card_is_black_and_centred():
    early = act_card(0.0)
    assert early.sum() == 0
    held = act_card(1.0)
    assert held[0, 0].sum() == 0
    assert held[20, 20].sum() == 0
    assert held[:, :, 0].max() > 200
    mid = held[held.shape[0] // 2]
    inked = np.nonzero(mid[:, 0] > 40)[0]
    assert len(inked)
    centre = (inked[0] + inked[-1]) / 2
    assert abs(centre - held.shape[1] / 2) < 30


def test_intro_cuts_to_black_instead_of_staying_on_parchment():
    leaf = np.full((80, 140, 3), 180, np.uint8)
    word = np.zeros((20, 80, 4), np.uint8)
    word[4:16, 8:72, 3] = 255
    word[:, :, :3] = 240
    intro = Intro(leaf, word)
    before = intro.frame(ACT_AT - 0.05)
    after = intro.frame(ACT_AT + 0.8)
    assert before.mean() > 40
    assert after[0, 0].sum() == 0
    assert after.max() > 200


def test_clip_index_follows_presentation_time():
    frames = [np.full((4, 6, 3), i, np.uint8) for i in range(10)]
    clip = Clip(frames, 24.0, "memory")
    indexes = [clip.index_at(i / 30.0) for i in range(12)]
    assert indexes[0] == 0
    assert indexes == [int(round(i / 30.0 * 24.0)) for i in range(12)]
    assert clip.index_at(100.0) == 9
