import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";

const { fontFamily: sourceSerif4 } = loadFont("normal", {
  weights: ["600"],
  subsets: ["latin"],
});

export type ChronicleTitleRevealProps = {
  readonly title: string;
  readonly fontFamily?: string;
  readonly color?: string;
  readonly fontSize?: number;
  /** Frame at which L→R reveal begins (default ~0.15s @30fps → 4.5 ≈ 5) */
  readonly revealStart?: number;
  /** Frame at which title is fully resolved (default ~0.65s → 19.5 ≈ 20) */
  readonly revealEnd?: number;
  /** Frame at which opacity fade-out begins (default ~1.75s → 52.5 ≈ 53) */
  readonly fadeStart?: number;
  /** Frame at which title is fully gone (default ~2.15s → 64.5 ≈ 65) */
  readonly fadeEnd?: number;
  /** Vertical placement as % from top (lower-mid title-safe). Default 58. */
  readonly topPercent?: number;
  /** Horizontal nudge in px (negative = left of center). Default -24. */
  readonly offsetX?: number;
  /**
   * Frames of delay between first and last letter start (spread across
   * the title). Default 2.2 ≈ v1 subtle wave. Aim 1–2 for v2 feel.
   */
  readonly staggerSpanFrames?: number;
  /** Settle translateY start in px. Default 4. */
  readonly settleYPx?: number;
  /** Tracking em at reveal start. Default 0.08. */
  readonly trackingFrom?: number;
  /** Tracking em when resolved. Default 0.02. */
  readonly trackingTo?: number;
  /**
   * Optional thin hairline under title lockup only (centre→out after resolve).
   * Never a scene pointer. Default false (v1).
   */
  readonly showHairline?: boolean;
  /** Hairline color. Default warm ivory/gold. */
  readonly hairlineColor?: string;
  /** Hairline draw duration in frames after revealEnd. Default ~0.25s → 7.5. */
  readonly hairlineDurationFrames?: number;
};

const DEFAULT_STAGGER_SPAN = 2.2; // v1: (i/last)*0.55*4 → ~2.2
const DEFAULT_SETTLE_Y = 4;

/**
 * Restrained L→R clip/mask reveal + subtle per-letter wave settle.
 * NO pointer, ravine line, rectangle, bounce, typewriter, glow, blur, shake.
 * After revealEnd typography is motionless until fade.
 */
export const ChronicleTitleReveal: React.FC<ChronicleTitleRevealProps> = ({
  title,
  fontFamily = sourceSerif4,
  color = "#F3EDE0",
  fontSize = 56,
  revealStart: revealStartProp,
  revealEnd: revealEndProp,
  fadeStart: fadeStartProp,
  fadeEnd: fadeEndProp,
  topPercent = 62,
  offsetX = -24,
  staggerSpanFrames = DEFAULT_STAGGER_SPAN,
  settleYPx = DEFAULT_SETTLE_Y,
  trackingFrom = 0.08,
  trackingTo = 0.02,
  showHairline = false,
  hairlineColor = "rgba(212, 175, 110, 0.72)",
  hairlineDurationFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const revealStart = revealStartProp ?? 0.15 * fps;
  const revealEnd = revealEndProp ?? 0.65 * fps;
  const fadeStart = fadeStartProp ?? 1.75 * fps;
  const fadeEnd = fadeEndProp ?? 2.15 * fps;
  const hairlineDur = hairlineDurationFrames ?? 0.25 * fps;

  const chars = Array.from(title);
  const lastIndex = Math.max(chars.length - 1, 1);

  // Whole-title L→R clip widen during reveal window
  const clipReveal = interpolate(frame, [revealStart, revealEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.22, 1, 0.36, 1),
  });
  const clipRightPercent = (1 - clipReveal) * 100;

  // Tracking contracts across the reveal window, then holds
  const trackingEm = interpolate(
    frame,
    [revealStart, revealEnd],
    [trackingFrom, trackingTo],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    },
  );

  // Global fade out after hold
  const fadeOut = interpolate(frame, [fadeStart, fadeEnd], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });

  // Hairline: centre → out after resolve only (lockup member, not pointer)
  const hairlineProgress =
    showHairline && frame >= revealEnd
      ? interpolate(frame, [revealEnd, revealEnd + hairlineDur], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.22, 1, 0.36, 1),
        })
      : 0;

  // Fully absent after fadeEnd — skip render for cleanliness
  if (frame >= fadeEnd) {
    return null;
  }

  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        justifyContent: "flex-start",
        alignItems: "center",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: `${topPercent}%`,
          left: "50%",
          translate: `calc(-50% + ${offsetX}px) 0px`,
          opacity: fadeOut,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div
          style={{
            clipPath: `inset(0 ${clipRightPercent}% 0 0)`,
            WebkitClipPath: `inset(0 ${clipRightPercent}% 0 0)`,
            overflow: "hidden",
            whiteSpace: "nowrap",
            fontFamily,
            fontWeight: 600,
            fontSize,
            color,
            letterSpacing: `${trackingEm}em`,
            // 1px contact shadow only — no glow bloom
            textShadow: "0 1px 1px rgba(0,0,0,0.35)",
            display: "flex",
            flexDirection: "row",
            alignItems: "baseline",
          }}
        >
          {chars.map((ch, i) => {
            const letterStart =
              revealStart + (i / lastIndex) * staggerSpanFrames;
            const letterEnd = Math.min(
              revealEnd,
              letterStart + (revealEnd - revealStart) * 0.55,
            );

            const letterOpacity = interpolate(
              frame,
              [letterStart, letterEnd],
              [0, 1],
              {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
                easing: Easing.bezier(0.22, 1, 0.36, 1),
              },
            );

            const letterY = interpolate(
              frame,
              [letterStart, letterEnd],
              [settleYPx, 0],
              {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
                easing: Easing.bezier(0.22, 1, 0.36, 1),
              },
            );

            // After revealEnd, force settled state (no residual motion)
            const settled = frame >= revealEnd;
            const op = settled ? 1 : letterOpacity;
            const y = settled ? 0 : letterY;

            return (
              <span
                key={`${i}-${ch}`}
                style={{
                  display: "inline-block",
                  opacity: op,
                  translate: `0px ${y}px`,
                  whiteSpace: ch === " " ? "pre" : undefined,
                }}
              >
                {ch === " " ? "\u00A0" : ch}
              </span>
            );
          })}
        </div>
        {showHairline && hairlineProgress > 0 ? (
          <div
            style={{
              marginTop: Math.round(fontSize * 0.18),
              height: 1,
              width: `${hairlineProgress * 100}%`,
              maxWidth: "100%",
              backgroundColor: hairlineColor,
              opacity: 0.85 * fadeOut,
              // Soft ends so it never reads as a hard UI rule
              maskImage:
                "linear-gradient(90deg, transparent 0%, black 12%, black 88%, transparent 100%)",
              WebkitMaskImage:
                "linear-gradient(90deg, transparent 0%, black 12%, black 88%, transparent 100%)",
            }}
          />
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
