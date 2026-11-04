import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { StablePush } from "../StablePush";
import { PaintedArchivalStrike } from "../PaintedArchivalStrike";
import { ChronicleTitleRevealV3_1 } from "../ChronicleTitleRevealV3_1";

export type ChronicleHookV3_2Props = {
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
   * Strike band height %. v3.1 used 11; v3.2 default 13 for nest margin
   * once title is center-anchored into the pigment body.
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
   * Title vertical anchor. v3.2 default 'center' so topPercent matches
   * PaintedArchivalStrike's band-center semantics (v3.1 used implicit 'top').
   */
  readonly titleAnchor?: "top" | "center";
  /** Optical nudge after anchor (px). Negative = up into thickest pigment. */
  readonly titleAnchorNudgeYPx?: number;
};

/**
 * Chronicle Reveal v3.2 — ONE FIX: nest title glyphs inside oxblood strike.
 * Shares v3.1 timing / manifest / exit / StablePush / oxblood look.
 * Difference: titleAnchor 'center' + slightly thicker band for margin.
 * Leaves ChronicleHookV3_1 intact for archived QC reproducibility.
 */
export const ChronicleHookV3_2: React.FC<ChronicleHookV3_2Props> = ({
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
  strokeBandHeightPercent = 13,
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
  titleAnchorNudgeYPx = 0,
}) => {
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
      </StablePush>
    </AbsoluteFill>
  );
};
