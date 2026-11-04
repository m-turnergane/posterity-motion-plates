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

export type ChronicleTitleRevealV3_1Props = {
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
   * Title may begin manifesting only after this frame (v3.1 default ~0.45s → 14 @30).
   * Letters still wait for the stroke edge to pass them.
   */
  readonly manifestStart?: number;
  /** Frame by which all letters must be fully settled (v3.1 default ~1.40s → 42). */
  readonly manifestEnd?: number;
  /** Title exit begin (v3.1 default ~2.50s → 75). */
  readonly exitStart?: number;
  /** Title fully gone (v3.1 default ~3.15s → 95). */
  readonly exitEnd?: number;
  readonly topPercent?: number;
  readonly offsetX?: number;
  /** Settle translateY start in px. Default 4. */
  readonly settleYPx?: number;
  /**
   * Soft scale-from on enter (material appear). Default 0.92 → 1.0.
   * Critical v3.1 lock: not opacity-only.
   */
  readonly scaleFrom?: number;
  /** Resolved scale. Default 1.0. */
  readonly scaleTo?: number;
  /** Exit scale target (shrink / dissolve). Default 0.94. */
  readonly exitScaleTo?: number;
  /**
   * Extra frames after stroke edge passes a letter before it begins
   * rising — “manifests inside” the strike. Default ~2.
   */
  readonly afterEdgeLagFrames?: number;
  /** Per-letter settle duration in frames. Default ~12 (~0.40s) for slower v3.1 settle. */
  readonly letterSettleFrames?: number;
  /** Tracking em when resolved. Default 0.02. */
  readonly trackingEm?: number;
  /**
   * Vertical anchor for `topPercent`.
   * - 'top' (default): CSS top of the text row — v3.1 behavior (title hangs under strike).
   * - 'center': optical vertical center of the title row at topPercent — nests inside
   *   PaintedArchivalStrike which also treats topPercent as band center.
   */
  readonly titleAnchor?: "top" | "center";
  /**
   * Extra translateY (px) after anchor. Negative = nudge up.
   * Fine-tune optical mid of serif caps into thickest pigment. Default 0.
   */
  readonly titleAnchorNudgeYPx?: number;
};

/**
 * Chronicle title letter-manifest v3.1.
 * Authored material appearance: soft scale 0.92→1.0 + opacity 0→1 +
 * tiny Y settle, gated by stroke leading edge. Exit reverses with
 * scale/Y character — NOT linear package fade.
 * Still bans: typewriter / karaoke / mask-only wipe / pointer / shake.
 * After resolve: STOP — stillness hold.
 */
export const ChronicleTitleRevealV3_1: React.FC<
  ChronicleTitleRevealV3_1Props
> = ({
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
  topPercent = 57,
  offsetX = -16,
  settleYPx = 4,
  scaleFrom = 0.92,
  scaleTo = 1.0,
  exitScaleTo = 0.94,
  afterEdgeLagFrames = 2,
  letterSettleFrames = 12,
  trackingEm = 0.02,
  titleAnchor = "top",
  titleAnchorNudgeYPx = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const strokeEnterStart = strokeEnterStartProp ?? 0.25 * fps;
  const strokeEnterEnd = strokeEnterEndProp ?? 0.85 * fps;
  const manifestStart = manifestStartProp ?? 0.45 * fps;
  const manifestEnd = manifestEndProp ?? 1.4 * fps;
  const exitStart = exitStartProp ?? 2.5 * fps;
  const exitEnd = exitEndProp ?? 3.15 * fps;

  // Newline splits a stronger two-line lockup. Single-line titles stay one row.
  const lineGroups = title.split("\n").map((line) => Array.from(line));
  const flatCount = lineGroups.reduce((n, g) => n + g.length, 0);
  const lastIndex = Math.max(flatCount - 1, 1);
  const multi = lineGroups.length > 1;

  const strokeProgress = getStrokeLeadingEdgeProgress(
    frame,
    strokeEnterStart,
    strokeEnterEnd,
  );

  if (frame >= exitEnd) {
    return null;
  }

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
          // 'center' shares PaintedArchivalStrike's topPercent-as-mid semantics
          translate:
            titleAnchor === "center"
              ? `calc(-50% + ${offsetX}px) calc(-50% + ${titleAnchorNudgeYPx}px)`
              : `calc(-50% + ${offsetX}px) ${titleAnchorNudgeYPx}px`,
          display: "flex",
          flexDirection: multi ? "column" : "row",
          alignItems: multi ? "center" : titleAnchor === "center" ? "center" : "baseline",
          gap: multi ? Math.round(fontSize * 0.04) : undefined,
          lineHeight: titleAnchor === "center" ? (multi ? 0.92 : 1) : undefined,
          whiteSpace: "nowrap",
          fontFamily,
          fontWeight: 600,
          fontSize,
          color,
          letterSpacing: `${trackingEm}em`,
          textShadow: "0 2px 2px rgba(0,0,0,0.45)",
        }}
      >
        {lineGroups.map((chars, lineIdx) => {
          const lineOffset = lineGroups.slice(0, lineIdx).reduce((n, g) => n + g.length, 0);
          const row = chars.map((ch, j) => {
          const i = lineOffset + j;
          const letterX = i / lastIndex;

          const edgePassFrame =
            strokeEnterStart +
            letterX * (strokeEnterEnd - strokeEnterStart);

          const letterInStart = Math.max(
            manifestStart,
            edgePassFrame + afterEdgeLagFrames,
          );
          const letterInEnd = Math.min(
            manifestEnd,
            letterInStart + letterSettleFrames,
          );

          const inHold = frame >= manifestEnd && frame < exitStart;

          // --- ENTER: scale + opacity + Y (material appear inside paint) ---
          const easeIn = Easing.bezier(0.22, 1, 0.36, 1);
          let enterOp = interpolate(
            frame,
            [letterInStart, letterInEnd],
            [0, 1],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeIn,
            },
          );
          let enterY = interpolate(
            frame,
            [letterInStart, letterInEnd],
            [settleYPx, 0],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeIn,
            },
          );
          let enterScale = interpolate(
            frame,
            [letterInStart, letterInEnd],
            [scaleFrom, scaleTo],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeIn,
            },
          );

          if (inHold) {
            enterOp = 1;
            enterY = 0;
            enterScale = scaleTo;
          }

          // --- EXIT: reverse-manifest R→L with scale shrink + Y lift ---
          const exitOrder = 1 - letterX;
          const exitSpan = exitEnd - exitStart;
          const letterExitStart =
            exitStart + exitOrder * exitSpan * 0.45;
          const letterExitEnd = Math.min(
            exitEnd,
            letterExitStart + exitSpan * 0.55,
          );

          const easeOut = Easing.bezier(0.4, 0, 0.2, 1);
          const exitOp = interpolate(
            frame,
            [letterExitStart, letterExitEnd],
            [1, 0],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeOut,
            },
          );
          const exitY = interpolate(
            frame,
            [letterExitStart, letterExitEnd],
            [0, -settleYPx * 0.85],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeOut,
            },
          );
          const exitScale = interpolate(
            frame,
            [letterExitStart, letterExitEnd],
            [scaleTo, exitScaleTo],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: easeOut,
            },
          );

          const inExit = frame >= exitStart;
          const opacity = inExit ? enterOp * exitOp : enterOp;
          const y = inExit ? exitY : enterY;
          const scale = inExit ? exitScale : enterScale;

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
                transform: `translateY(${y}px) scale(${scale})`,
                transformOrigin: "50% 70%",
                whiteSpace: ch === " " ? "pre" : undefined,
              }}
            >
              {ch === " " ? "\u00A0" : ch}
            </span>
          );
          });
          return (
            <div
              key={lineIdx}
              style={{
                display: "flex",
                flexDirection: "row",
                alignItems: titleAnchor === "center" ? "center" : "baseline",
                justifyContent: "center",
                lineHeight: multi ? 0.92 : undefined,
                whiteSpace: "nowrap",
              }}
            >
              {row}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
