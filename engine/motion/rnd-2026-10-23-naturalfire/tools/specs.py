import json, cv2, numpy as np
from pathlib import Path
MASKS = Path("/workspace/posterity/day21/atahualpa/masks_v2b2")
def load_masks():
    return [cv2.imread(str(MASKS / f"P05_flame_c{i}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255.0 for i in range(3)]
def load_specs(path):
    return json.load(open(path))
