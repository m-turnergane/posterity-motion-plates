# Posterity Motion

Remotion library for Atelier Posterity Chronicle motion primitives.

**Project path:** `/workspace/posterity/motion/posterity-motion`  
**Composition POC:** `ChronicleHook` (1080×1920 @ 30fps, 90 frames)

## PosterityMotion components

Episodes pass **props only** — do not fork component internals per episode.

| Component | Path | Role |
|---|---|---|
| `StablePush` | `src/PosterityMotion/StablePush.tsx` | Centre scale-only push (default 100→104%). No translation / shake. |
| `ChronicleTitleReveal` | `src/PosterityMotion/ChronicleTitleReveal.tsx` | L→R clip/mask + letter-wave title. No pointer / ravine line / rectangle. |
| `ChronicleHook` | `src/PosterityMotion/compositions/ChronicleHook.tsx` | Composes plate push + title reveal. |

Import:

```ts
import {
  StablePush,
  ChronicleTitleReveal,
  ChronicleHook,
} from "./PosterityMotion";
```

### Episode props pattern

```tsx
<ChronicleHook
  image={staticFile("plates/seq1_cathedral_hook_OWNER.png")}
  title="CITY OF CHURCHES"
  fromScale={1}
  toScale={1.04}
  // optional timing overrides in frames @ composition fps
  // revealStart / revealEnd / fadeStart / fadeEnd
/>
```

## Dev / render

```bash
npm i
npx remotion studio --no-open
npx remotion render src/index.ts ChronicleHook out.mp4 --codec=h264
npx remotion still src/index.ts ChronicleHook out.png --frame=20
```

## Out of scope (Phase 2+)
MapTrace, ArchitectureTrace, PhraseCaptions, ravine `line_trace` — not in this library yet. Chronicle Hook v1 deliberately **excludes** any pointer/line decoration.
