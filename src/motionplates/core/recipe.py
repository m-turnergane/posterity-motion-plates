import os, yaml, zlib, json
import numpy as np

def load_recipe(path, presets_dir=None):
    r = yaml.safe_load(open(path)); presets_dir = presets_dir or os.path.join(os.path.dirname(os.path.abspath(path)), "presets")
    presets = {}
    if os.path.isdir(presets_dir):
        for fn in sorted(os.listdir(presets_dir)):
            if fn.endswith((".yaml", ".yml")): presets.update(yaml.safe_load(open(os.path.join(presets_dir, fn))) or {})
    eff = []
    for e in r.get("effects", []):
        e = dict(e)
        if "preset" in e:
            base = json.loads(json.dumps(presets[e.pop("preset")])); base = _merge(base, e); e = base
        eff.append(e)
    r["effects"] = eff
    return r

def _merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict): a[k] = _merge(a[k], v)
        else: a[k] = v
    return a

def make_rng_factory(seed):
    def rng(name, idx=0):
        return np.random.default_rng([int(seed), zlib.crc32(name.encode()), int(idx)])
    return rng
