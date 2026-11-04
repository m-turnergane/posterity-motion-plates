import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type ArchivalShadowFieldProps = {
  /** Frame when L→R wash begins (default ~0.20s @30fps → 6) */
  readonly enterStart?: number;
  /** Frame when wash is fully present (default ~0.45s → 13.5 ≈ 14) */
  readonly enterEnd?: number;
  /** Frame when exit fade begins (default ~2.25s → 67.5 ≈ 68) */
  readonly fadeStart?: number;
  /** Frame when field is fully gone (default ~2.65s → 79.5 ≈ 80) */
  readonly fadeEnd?: number;
  /** Vertical centre of wash band as % from top. Default 62. */
  readonly topPercent?: number;
  /** Band height as % of frame height. Default 16. */
  readonly bandHeightPercent?: number;
  /** Peak opacity of the charcoal wash (0–1). Default 0.50. */
  readonly peakOpacity?: number;
  /** Horizontal width of wash as % of frame. Default 92. */
  readonly widthPercent?: number;
  /** Horizontal nudge in px (negative = left). Default -16. */
  readonly offsetX?: number;
};

/**
 * Restrained horizontal charcoal archival wash behind title area only.
 * Feathered / irregular soft edges via layered radial+linear gradients.
 * Subtle L→R reveal. Plate briefly falls into shadow — NOT a solid rect /
 * Photoshop gradient-box / UI card. No pointer, glow bloom, or full-screen crush.
 */
export const ArchivalShadowField: React.FC<ArchivalShadowFieldProps> = ({
  enterStart: enterStartProp,
  enterEnd: enterEndProp,
  fadeStart: fadeStartProp,
  fadeEnd: fadeEndProp,
  topPercent = 62,
  bandHeightPercent = 16,
  peakOpacity = 0.50,
  widthPercent = 92,
  offsetX = -16,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enterStart = enterStartProp ?? 0.2 * fps;
  const enterEnd = enterEndProp ?? 0.45 * fps;
  const fadeStart = fadeStartProp ?? 2.25 * fps;
  const fadeEnd = fadeEndProp ?? 2.65 * fps;

  if (frame < enterStart || frame >= fadeEnd) {
    return null;
  }

  // L→R reveal: clip widens left→right
  const reveal = interpolate(frame, [enterStart, enterEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.25, 0.1, 0.25, 1),
  });
  const clipRightPercent = (1 - reveal) * 100;

  // Soft opacity ramp on enter + exit (independent of clip)
  const enterOpacity = interpolate(
    frame,
    [enterStart, enterStart + (enterEnd - enterStart) * 0.55],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    },
  );
  const exitOpacity = interpolate(frame, [fadeStart, fadeEnd], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });
  const fieldOpacity = peakOpacity * enterOpacity * exitOpacity;

  // Band geometry — centred on topPercent
  const bandTop = topPercent - bandHeightPercent / 2;

  // Irregular soft wash: layered radial spots + horizontal linear falloff.
  // Avoids a single hard rect / card silhouette.
  const washBackground = [
    // Core horizontal charcoal band (soft vertical feather)
    `linear-gradient(
      180deg,
      rgba(8, 7, 6, 0) 0%,
      rgba(10, 9, 8, 0.55) 18%,
      rgba(6, 5, 4, 0.78) 42%,
      rgba(8, 7, 6, 0.72) 58%,
      rgba(10, 9, 8, 0.45) 82%,
      rgba(8, 7, 6, 0) 100%
    )`,
    // Soft elliptical darken pools for irregular edge feel
    `radial-gradient(
      ellipse 42% 70% at 28% 48%,
      rgba(0, 0, 0, 0.55) 0%,
      rgba(0, 0, 0, 0) 72%
    )`,
    `radial-gradient(
      ellipse 38% 65% at 72% 52%,
      rgba(0, 0, 0, 0.48) 0%,
      rgba(0, 0, 0, 0) 70%
    )`,
    `radial-gradient(
      ellipse 55% 80% at 50% 50%,
      rgba(12, 10, 8, 0.35) 0%,
      rgba(0, 0, 0, 0) 78%
    )`,
    // Horizontal edge feather (ends dissolve)
    `linear-gradient(
      90deg,
      rgba(0, 0, 0, 0) 0%,
      rgba(0, 0, 0, 0.5) 8%,
      rgba(0, 0, 0, 0.55) 50%,
      rgba(0, 0, 0, 0.5) 92%,
      rgba(0, 0, 0, 0) 100%
    )`,
  ].join(", ");

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: `${bandTop}%`,
          left: "50%",
          width: `${widthPercent}%`,
          height: `${bandHeightPercent}%`,
          translate: `calc(-50% + ${offsetX}px) 0px`,
          opacity: fieldOpacity,
          clipPath: `inset(0 ${clipRightPercent}% 0 0)`,
          WebkitClipPath: `inset(0 ${clipRightPercent}% 0 0)`,
          background: washBackground,
          // Soft mask so vertical edges never read as a card
          maskImage:
            "linear-gradient(90deg, transparent 0%, black 6%, black 94%, transparent 100%), linear-gradient(180deg, transparent 0%, black 22%, black 78%, transparent 100%)",
          WebkitMaskImage:
            "linear-gradient(90deg, transparent 0%, black 6%, black 94%, transparent 100%), linear-gradient(180deg, transparent 0%, black 22%, black 78%, transparent 100%)",
          maskComposite: "intersect",
          WebkitMaskComposite: "source-in",
          filter: "blur(1.2px)",
        }}
      />
    </AbsoluteFill>
  );
};
