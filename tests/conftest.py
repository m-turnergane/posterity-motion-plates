import os, sys, numpy as np, cv2, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
HERE = os.path.dirname(__file__)

def make_synth_plate(path, W=270, H=480):
    """Small synthetic painted-ish plate: warm gradient, 'pall' band, bright flame, dark banner, 3 red petals. Generated, never committed."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.dstack([200 - 0.15 * yy + 10 * np.sin(xx / 17), 150 - 0.12 * yy + 8 * np.sin(yy / 23), 110 - 0.08 * yy]).astype(np.float32)
    rng = np.random.default_rng(0); img += cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 3)[..., None] * 6
    img = np.clip(img, 0, 255).astype(np.uint8)
    cv2.rectangle(img, (0, 300), (W, 380), (90, 30, 70), -1)                       # pall
    cv2.rectangle(img, (20, 40), (60, 140), (70, 25, 60), -1)                      # banner
    cv2.ellipse(img, (200, 150), (8, 12), 0, 0, 360, (255, 245, 200), -1)          # flame
    cv2.rectangle(img, (0, 400), (70, 480), (30, 20, 20), -1)                      # fg block
    for cx, cy in [(120, 200), (140, 220), (110, 235)]:
        cv2.ellipse(img, (cx, cy), (9, 7), 20, 0, 360, (170, 15, 40), -1)         # petals
    cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

@pytest.fixture(scope="session")
def synth(tmp_path_factory):
    d = tmp_path_factory.mktemp("plates"); make_synth_plate(str(d / "synth.png")); return str(d)

@pytest.fixture(scope="session")
def rendered(synth, tmp_path_factory):
    from motionplates.core import engine
    out = tmp_path_factory.mktemp("out")
    m = engine.render(os.path.join(HERE, "data", "test_recipe.yaml"), str(out), plates_dir=synth, log=lambda *a: None)
    return m, str(out)
