sys_keys = __import__("sys").argv[1:]
import sys; sys.argv=['x']; exec(open('build_bjorn_rough_v1.py').read())
for k in sys_keys:
    b = Beat(k, calib=False); DP.layers_sheet(b.dcfg, str(SCR / f'probe/{k}_layers.png')); print(k, b.log['face_layers'], b.log['density_max'], b.log['overscan'], flush=True)
