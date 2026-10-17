"""Export the petal sprites cut for a recipe into a reusable pack: python tools/export_petal_pack.py recipe.yaml assets/packs/<name>   (needs $MOTIONPLATES_PLATES)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from motionplates.core import engine
from motionplates.effects.petal_fall import export_pack
ctx = engine.prepare(sys.argv[1], log=lambda *a: None); pf = [e for e in ctx.effects if e.type == "petal_fall"][0]
export_pack({k: v for k, v in pf.sources.items()}, sys.argv[2]); print("exported", len(pf.sources), "sprites ->", sys.argv[2])
