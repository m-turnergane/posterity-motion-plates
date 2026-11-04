# Posterity Motion System

**Status:** Owner-locked 2026-09-27 · Phase 1 in flight  
**Owner:** Vellum (editorial) · Atelier (Remotion execution) · Posterity Motion (primitive pick — TBD bot/tool)

## Purpose
Remove discretionary effect generation from repetitive production. Motion is a **language** of approved Remotion primitives, not a freeform transition pack.

## Architecture
1. **Vellum** — editorial intent (which beat needs which motion class)
2. **Posterity Motion** — picks an **approved** primitive only
3. **Remotion** — executes deterministically
4. **Vellum** — visually QCs preview **before** assembly into full rough

## Phase 1 — Ani Day 11 Chronicle Reveal POC
- **Primitives:** `StablePush` + `ChronicleTitleReveal` (+ v2: `ArchivalShadowField`)
- **StablePush:** scale-only centre, 100→104%, zero jitter
- **ChronicleTitleReveal:** Posterity serif · L→R clip reveal · restrained letter settle + tracking · **NO** rect / pointer / bounce / fade-only
- **v1 timing @30fps (tech proof KEEP):** push 0–3s · title begin 0.15s · full 0.65s · hold 0.65–1.75 · out 1.75–2.15 · gone 2.15 · composition `ChronicleHook`
- **v2 in flight (channel signature):** see § Chronicle Reveal v2 · composition `ChronicleHookV2` · QC pack `day11/ani-bagratid/renders/hook-qc/v2/`
- **Deliverable:** 3s QC MP4 + stills → Vellum QC (v1 vs v2) → owner go
- **Freeze:** full Ani Oliver MUTE-READY rough stays parked until hook preview clears — **do not** assemble rough on v1 alone

## Phase 2 library (after Phase 1 clear)
| Primitive | Role |
|-----------|------|
| StablePush | Subtle centre scale push |
| ChronicleTitleReveal | Hook title L→R clip |
| PhraseCaptions | Spoken-word captions |
| HardCut | Default cut |
| ShortDissolve | Rare soft join |
| MapTrace | Informational map line only |
| ArchitectureTrace | Informational structure line only |
| OutroHold | Branded outro hold |
| RenderQC | QC / smoke renders |

HardCut is default. Traces are informational only (not decorative flourish).

## Phase 3
- Research narrow `posterity_render_*` tool surface
- Official Remotion skills / docs only
- **No** unreviewed third-party MCP auto-add

## Gate
Vellum PASS on preview → escalate to owner → only then reassemble affected rough.

## Standing additive rule (owner 2026-09-27 HARD FAIL)
Every motion primitive must have a **semantic or compositional reason**.
- MapTrace = geography
- ArchitectureTrace = architecture
- Never draw a line toward a subject merely because motion was requested

Default transition = **HardCut**. Dissolves exceptional, short, motivated.
Banned in assembly: pixelation, mosaic, warp, morph, slideshow packs, long double-exposure crossfades, micro-shake, decorative pointer lines.

## Pre-full-rough QC pack
Before another full owner rough, render short QC: (1) first 3s, (2) every non-hard-cut transition, (3) final outro. Vellum inspects before approving full rough.

## HARD FAIL addendum 2026-09-27
- Ani Oliver rough HARD FAIL; Hook v1 remains Phase 1 gate.
- **Ravine pointer / decorative line banned forever** on Chronicle Hook (title via clip+wave only).
- Post-hook-approve: HardCut default; dissolves exceptional; new short QC preview (open 3s + non-hardcut joins + outro) before full rough.

## Chronicle Reveal v2 (owner art-direction 2026-09-27)

v1 = Remotion tech proof (KEEP library StablePush + basic ChronicleTitleReveal).  
v2 = **channel signature** — do not ship rough on v1 alone.

**Mechanic (principle, not clone):** graphic field arrives → typography resolves through it → device clears. Translate Kings & Generals physical-arrival idea into Recovered Chronicle language. Ref: `brand/refs/kings-generals-title-device-PRINCIPLE-ONLY.png` — **do not** copy red banner.

**ArchivalShadowField:** charcoal/black wash, feathered irregular soft edges, low opacity, L→R enter ~0.20s; plate briefly falls into shadow — not a solid rect / gradient box.

**Title:** larger · Posterity serif · warm ivory/bone · clip L→R + subtle letter wave · STOP after resolve.

**Optional:** thin ivory/gold hairline under title lockup only (centre→out); never scene pointer. Omit if cheaper.

**Timing @30:** shadow 0.20 · type 0.30–0.95 · hold to 2.25 · exit done 2.65 · end 3.00.

**QC axes (Vellum v1 vs v2):** impact · type authority · authored motion · phone readability · reusable signature.

## Chronicle Reveal v3 (owner art-direction 2026-09-27 ~12:02 ET)

**Status:** IN FLIGHT — replaces v2 as channel-signature candidate.  
v1 = tech proof KEEP · v2 = charcoal field + L→R wipe — **owner REJECT for signature** (still reads “text over image”). Do not ship rough on v1/v2.

**Core fail of v2:** translucent dark field has no character; title resolves like a simple L→R wipe — functional, not designed.

**Mechanic (branded graphic event):**
1. textured field arrives  
2. title manifests **inside** it  
3. title exits with authorship  

**NOT:** clean rectangle · flat opacity band · basic wipe · generic grey/black translucent field · bright modern red · Kings & Generals red-banner clone · typewriter · karaoke · mask-only wipe · pointer · shake.

**TITLE FIELD — PaintedArchivalStrike (new primitive):**
- Weathered **oxblood / iron-oxide** painted strike (muted dark red; dried-blood / historical manuscript energy)  
  Alt OK if needed: burnt-umber archival stroke — same tactile brief  
- Rough-edged horizontal painted stroke · textured / distressed · visible arrival across frame  
- Motion duration **~0.35–0.50s** · feel physically painted / dragged on  

**TITLE TEXT — ChronicleTitleReveal v3 (letter-manifest):**
- Letters manifest **progressively after the stroke passes them**  
- Per letter: slight opacity rise · tiny vertical settle · subtle stagger  
- Not typewriter / karaoke / basic mask-only wipe  

**BACKGROUND:** StablePush unchanged · no shake · no pointer  

**Timing @30fps / ~3.00s total:**
| Window | Event |
|--------|--------|
| 0.00–0.20 | image only |
| 0.20–0.65 | painted stroke enters |
| 0.35–1.05 | title manifests inside stroke |
| 1.05–1.90 | hold |
| 1.90–2.35 | title exits with stagger / grouped dissolve (not one-block fade) |
| 2.10–2.55 | painted stroke clears |
| 2.55–3.00 | clean plate before cut |

**EXIT:** title exit has character (grouped fade, letter dissolve, or reverse manifestation) — not whole package as one block.

**Bar:** repeatable Posterity signature with human-level care — branded motion-design element, not readable overlay.

**Deliverable:** composition `ChronicleHookV3` · QC pack under `day11/ani-bagratid/renders/hook-qc/v3/` (MP4 + stills at key beats + notes) → Vellum QC → owner. Full rough FROZEN until owner clears.

**Principle ref (do not clone):** `brand/refs/kings-generals-title-device-PRINCIPLE-ONLY.png`

## Chronicle Reveal v3.1 (owner notes 2026-09-27 ~12:12 ET)

Owner on v3: **better** — not yet clear. Fixes:
1. Lift title + strike corridor **up marginally** (more centered on plate art).
2. **Manifest emphasis:** authored letter arrival (scale+opacity+Y / ink resolve) — **not** linear fade-in/out.
3. Slow overall ~**+1.0s** → target **~4.0s** composition (see `hook-qc/v3.1/BRIEF-v3.1.md`).

Keep oxblood PaintedArchivalStrike + stroke-gated letter-manifest. Full rough FROZEN until owner clears v3.1+.

**v3.1 build (2026-09-27):** composition id `ChronicleHookV3-1` (120f / 4.00s) · `topPercent=57` · manifest = scale 0.92→1.0 + opacity + Y settle, stroke-gated · QC pack `day11/ani-bagratid/renders/hook-qc/v3.1/` · prior `ChronicleHookV3` 90f pack archived untouched.

## Chronicle Reveal v3.2 (owner 2026-09-27 ~12:19 ET)

Owner on v3.1: **directionally better — we can work with this.** Single fix: title was hanging **under** oxblood strike; must be **vertically centered inside** the painted strike body. All else constant (4s, scale-manifest, oxblood, lift vs plate). Ref: `hook-qc/v3.2/OWNER-ALIGN-REF.png`. Full rough FROZEN until clear.


## Chronicle Reveal STANDING LOCK (owner 2026-09-27 ~12:34 ET)

**CLEARED signature:** Chronicle Reveal **v3.2b** (`ChronicleHookV3-2b`).

**Standing Seq1 requirement — Day 11 Ani and every episode onward** (unless owner revises):
- Composition / primitive pack: `StablePush` + `PaintedArchivalStrike` (oxblood/iron-oxide distressed) + `ChronicleTitleRevealV3_1` with `titleAnchor: 'center'`, `titleAnchorNudgeYPx: -4`, stroke-gated **scale+opacity+Y** letter-manifest (not linear fade), authored reverse-manifest exit
- Timing: **~4.00s** @30fps (120f) windows per v3.1 table (enter 0.25–0.85 · manifest 0.45–1.40 · hold →2.50 · exit/clear · clean 3.50–4.00)
- Lockup: title optically nested inside strike (equal margin); corridor `topPercent≈57`; `bandHeightPercent=14`
- Bans unchanged: no pointer · no shake · no flat charcoal band · no bright K&G red-banner clone · no typewriter/karaoke/mask-only wipe

**Canonical QC proof:** `/workspace/posterity/day11/ani-bagratid/renders/hook-qc/v3.2b/`  
Prior packs (v1 tech proof, v2–v3.2) archived — do not ship as signature.

**Post-clear:** Ani Day 11 full rough unfreeze for HARD FAIL reassemble (hook integrate + remaining HARD FAIL package). Phase 2 library may proceed after Ani reassemble gate.
