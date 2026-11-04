import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import { loadFont } from "@remotion/google-fonts/SourceSerif4";

const { fontFamily: kickerSerif } = loadFont("normal", {
  weights: ["600"],
  subsets: ["latin"],
});
import { StablePush } from "../StablePush";
import { PaintedArchivalStrike } from "../PaintedArchivalStrike";
import { ChronicleTitleRevealV3_1 } from "../ChronicleTitleRevealV3_1";

export type ChronicleHookV3_2bProps = {
  readonly image?: string;
  readonly title?: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  readonly strokeEnterStart?: number;
  readonly strokeEnterEnd?: number;
  readonly strokeClearStart?: number;
  readonly strokeClearEnd?: number;
  readonly manifestStart?: number;
  readonly manifestEnd?: number;
  readonly exitStart?: number;
  readonly exitEnd?: number;
  readonly fontSize?: number;
  readonly color?: string;
  /** Corridor lockup mid. Default 57 — same as v3.1. */
  readonly topPercent?: number;
  readonly offsetX?: number;
  /**
   * Strike band height %. v3.2 used 13; v3.2b default 14 for equal
   * optical margin above/below caps in dense pigment body.
   */
  readonly strokeBandHeightPercent?: number;
  readonly strokePeakOpacity?: number;
  readonly strokeFillColor?: string;
  readonly strokeEdgeColor?: string;
  readonly strokeMidColor?: string;
  readonly letterScaleFrom?: number;
  readonly letterScaleTo?: number;
  readonly letterExitScaleTo?: number;
  readonly settleYPx?: number;
  readonly afterEdgeLagFrames?: number;
  readonly letterSettleFrames?: number;
  /**
   * Title vertical anchor. Keep 'center' (v3.2 semantics).
   */
  readonly titleAnchor?: "top" | "center";
  /** Optical nudge after anchor (px). Negative = up. v3.2b default -4. */
  readonly titleAnchorNudgeYPx?: number;
  /**
   * Optional small chapter line above the title. Unset by default so
   * existing compositions render exactly as before. Must not compete
   * with the title and must not sit inside the oxblood stroke.
   */
  readonly kicker?: string;
};

/**
 * Chronicle Reveal v3.2b — residual optical nest polish on v3.2.
 * Shares v3.2 timing / manifest / exit / StablePush / oxblood look / corridor.
 * Difference vs v3.2: titleAnchorNudgeYPx upward + optional band thicken.
 * Leaves ChronicleHookV3_2 intact for archived QC reproducibility.
 */
export const ChronicleHookV3_2b: React.FC<ChronicleHookV3_2bProps> = ({
  image = staticFile("plates/seq1_cathedral_hook_OWNER.png"),
  title = "CITY OF CHURCHES",
  fromScale = 1,
  toScale = 1.04,
  strokeEnterStart = 8,
  strokeEnterEnd = 26,
  strokeClearStart = 84,
  strokeClearEnd = 105,
  manifestStart = 14,
  manifestEnd = 42,
  exitStart = 75,
  exitEnd = 95,
  fontSize = 68,
  color = "#F3EDE0",
  topPercent = 57,
  offsetX = -16,
  strokeBandHeightPercent = 14,
  strokePeakOpacity = 0.92,
  strokeFillColor = "#5A1A18",
  strokeEdgeColor = "#3A0E0C",
  strokeMidColor = "#6E2A1C",
  letterScaleFrom = 0.92,
  letterScaleTo = 1.0,
  letterExitScaleTo = 0.94,
  settleYPx = 4,
  afterEdgeLagFrames = 2,
  letterSettleFrames = 12,
  titleAnchor = "center",
  titleAnchorNudgeYPx = -4,
  kicker,
}) => {
  const frame = useCurrentFrame();
  const kickerInEnd = manifestStart + 14;
  let kickerOpacity = 0;
  if (kicker && frame >= manifestStart && frame < exitEnd) {
    const enter = interpolate(frame, [manifestStart, kickerInEnd], [0, 0.7], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.22, 1, 0.36, 1),
    });
    const exit = interpolate(frame, [exitStart, exitEnd], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.4, 0, 0.2, 1),
    });
    kickerOpacity = frame >= exitStart ? enter * exit : enter;
  }
  const bandTop = topPercent - strokeBandHeightPercent / 2;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <StablePush src={image} fromScale={fromScale} toScale={toScale}>
        <PaintedArchivalStrike
          enterStart={strokeEnterStart}
          enterEnd={strokeEnterEnd}
          clearStart={strokeClearStart}
          clearEnd={strokeClearEnd}
          topPercent={topPercent}
          bandHeightPercent={strokeBandHeightPercent}
          peakOpacity={strokePeakOpacity}
          offsetX={offsetX}
          fillColor={strokeFillColor}
          edgeColor={strokeEdgeColor}
          midColor={strokeMidColor}
        />
        <ChronicleTitleRevealV3_1
          title={title}
          strokeEnterStart={strokeEnterStart}
          strokeEnterEnd={strokeEnterEnd}
          manifestStart={manifestStart}
          manifestEnd={manifestEnd}
          exitStart={exitStart}
          exitEnd={exitEnd}
          fontSize={fontSize}
          color={color}
          topPercent={topPercent}
          offsetX={offsetX}
          settleYPx={settleYPx}
          scaleFrom={letterScaleFrom}
          scaleTo={letterScaleTo}
          exitScaleTo={letterExitScaleTo}
          afterEdgeLagFrames={afterEdgeLagFrames}
          letterSettleFrames={letterSettleFrames}
          trackingEm={0.02}
          titleAnchor={titleAnchor}
          titleAnchorNudgeYPx={titleAnchorNudgeYPx}
        />
        {kicker && kickerOpacity > 0.01 ? (
          <AbsoluteFill style={{ pointerEvents: "none" }}>
            <div
              style={{
                position: "absolute",
                top: `calc(${bandTop}% - 52px)`,
                left: 0,
                right: 0,
                textAlign: "center",
                fontFamily: kickerSerif,
                fontWeight: 600,
                fontSize: 28,
                letterSpacing: "0.32em",
                color: `rgba(243, 237, 224, ${kickerOpacity})`,
                textShadow: "0 1px 2px rgba(0,0,0,0.5)",
                whiteSpace: "nowrap",
                textIndent: "0.32em",
              }}
            >
              {kicker}
            </div>
          </AbsoluteFill>
        ) : null}
      </StablePush>
    </AbsoluteFill>
  );
};
