"""Research and development modules for motion-plates.

STATUS: R&D ONLY — SUPERSEDED FOR PRODUCTION (2026-10-30)

The flames R&D work (natural_fire, flame, and the flames_v1–v3 experiments) has been
superseded by torch_v1c, which is LOCKED as the house torch standard. The owner verdict
was that v3 "was distorting the things around it" while v1c is "more like a pulsing effect".

For production torch/cresset/brazier/larger-fire work, use:
    src/motionplates/standalone/fx_torch.py (torch_v1c)

This subpackage is preserved for reference and future R&D only.

Modules:
    natural_fire: Procedural fire animation with advected flame tongues (R&D only)
    flame: Core flame simulation primitives (R&D only)

See also:
    docs/TORCH-V1C.md — Production torch preset documentation
    docs/AUDIT-V1C-VS-V3.md — Measured comparison showing why v1c beat v3
"""
