import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";
import { getStrokeLeadingEdgeProgress } from "./PaintedArchivalStrike";

const { fontFamily: sourceSerif4 } = loadFont("normal", {
  weights: ["600"],
  subsets: ["latin"],
});

export type ChronicleTitleRevealV3Props = {
  readonly title: string;
  readonly fontFamily?: string;
  readonly color?: string;
  /** Authority size ~64–72 @1080w. Default 68. */
  readonly fontSize?: number;
  /**
   * Stroke enter window — must match PaintedArchivalStrike so letter
   * gates sync to the same leading-edge progress.
   */
  readonly strokeEnterStart?: number;
  readonly strokeEnterEnd?: number;
  /**
   * Title may begin manifesting only after this frame (default ~0.35s → 11).
   * Letters still wait for the stroke edge to pass them.
   */
  readonly manifestStart?: number;
  /** Frame by which all letters must be fully settled (default ~1.05s → 32). */
  readonly manifestEnd?: number;
  /** Title exit begin (default ~1.90s → 57). */
  readonly exitStart?: number;
  /** Title fully gone (default ~2.35s → 71). */
  readonly exitEnd?: number;
  readonly topPercent?: number;
  readonly offsetX?: number;
  /** Settle translateY start in px. Default 4. */
  readonly settleYPx?: number;
  /**
   * Extra frames after stroke edge passes a letter before it begins
   * rising — “manifests inside” the strike. Default ~2.
   */
  readonly afterEdgeLagFrames?: number;
  /** Per-letter settle duration in frames. Default ~8 (~0.27s). */
  readonly letterSettleFrames?: number;
  /** Tracking em when resolved. Default 0.02. */
  readonly trackingEm?: number;
};

/**
 * Chronicle title letter-manifest v3.
 * Primary driver = stroke leading-edge progress across letter X positions.
 * Per letter: opacity 0→1 + tiny Y settle. NOT typewriter / karaoke /
 * mask-only wipe. Authored reverse-manifest exit (not one-block fade).
 * After resolve: STOP — stillness hold.
 */
export const ChronicleTitleRevealV3: React.FC<ChronicleTitleRevealV3Props> = ({
  title,
  fontFamily = sourceSerif4,
  color = "#F3EDE0",
  fontSize = 68,
  strokeEnterStart: strokeEnterStartProp,
  strokeEnterEnd: strokeEnterEndProp,
  manifestStart: manifestStartProp,
  manifestEnd: manifestEndProp,
  exitStart: exitStartProp,
  exitEnd: exitEndProp,
  topPercent = 61,
  offsetX = -16,
  settleYPx = 4,
  afterEdgeLagFrames = 2,
  letterSettleFrames = 8,
  trackingEm = 0.02,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const strokeEnterStart = strokeEnterStartProp ?? 0.2 * fps;
  const strokeEnterEnd = strokeEnterEndProp ?? 0.65 * fps;
  const manifestStart = manifestStartProp ?? 0.35 * fps;
  const manifestEnd = manifestEndProp ?? 1.05 * fps;
  const exitStart = exitStartProp ?? 1.9 * fps;
  const exitEnd = exitEndProp ?? 2.35 * fps;

  const chars = Array.from(title);
  const lastIndex = Math.max(chars.length - 1, 1);

  const strokeProgress = getStrokeLeadingEdgeProgress(
    frame,
    strokeEnterStart,
    strokeEnterEnd,
  );

  // Fully absent after exitEnd
  if (frame >= exitEnd) {
    return null;
  }

  // Before any letter can appear
  if (frame < manifestStart && strokeProgress <= 0) {
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
          display: "flex",
          flexDirection: "row",
          alignItems: "baseline",
          whiteSpace: "nowrap",
          fontFamily,
          fontWeight: 600,
          fontSize,
          color,
          letterSpacing: `${trackingEm}em`,
          textShadow: "0 1px 1px rgba(0,0,0,0.4)",
        }}
      >
        {chars.map((ch, i) => {
          // Normalized letter X across title (spaces count — visual corridor)
          const letterX = i / lastIndex;

          // Frame when stroke leading edge reaches this letter
          const edgePassFrame =
            strokeEnterStart +
            letterX * (strokeEnterEnd - strokeEnterStart);

          // Letter may start only after: title window open AND edge passed + lag
          const letterInStart = Math.max(
            manifestStart,
            edgePassFrame + afterEdgeLagFrames,
          );
          const letterInEnd = Math.min(
            manifestEnd,
            letterInStart + letterSettleFrames,
          );

          // Hold: fully settled between manifestEnd and exitStart
          const inHold = frame >= manifestEnd && frame < exitStart;

          // --- ENTER (letter-manifest gated by stroke) ---
          let enterOp = interpolate(
            frame,
            [letterInStart, letterInEnd],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.22, 1, 0.36, 1),
            },
          );
          let enterY = interpolate(
            frame,
            [letterInStart, letterInEnd],
            [settleYPx, 0],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.22, 1, 0.36, 1),
            },
          );

          if (inHold) {
            enterOp = 1;
            enterY = 0;
          }

          // --- EXIT: reverse-manifest (last → first), not one-block fade ---
          // Outer letters leave first; centre holds slightly longer.
          const exitOrder = 1 - letterX; // rightmost exits first
          const exitSpan = exitEnd - exitStart;
          const letterExitStart =
            exitStart + exitOrder * exitSpan * 0.45;
          const letterExitEnd = Math.min(
            exitEnd,
            letterExitStart + exitSpan * 0.55,
          );

          const exitOp = interpolate(
            frame,
            [letterExitStart, letterExitEnd],
            [1, 0],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.4, 0, 0.2, 1),
            },
          );
          const exitY = interpolate(
            frame,
            [letterExitStart, letterExitEnd],
            [0, -settleYPx * 0.75],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.4, 0, 0.2, 1),
            },
          );

          const inExit = frame >= exitStart;
          const opacity = inExit ? enterOp * exitOp : enterOp;
          const y = inExit ? exitY : enterY;

          if (opacity < 0.01) {
            return (
              <span
                key={`${i}-${ch}`}
                style={{
                  display: "inline-block",
                  opacity: 0,
                  whiteSpace: ch === " " ? "pre" : undefined,
                }}
              >
                {ch === " " ? "\u00A0" : ch}
              </span>
            );
          }

          return (
            <span
              key={`${i}-${ch}`}
              style={{
                display: "inline-block",
                opacity,
                translate: `0px ${y}px`,
                whiteSpace: ch === " " ? "pre" : undefined,
              }}
            >
              {ch === " " ? "\u00A0" : ch}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
