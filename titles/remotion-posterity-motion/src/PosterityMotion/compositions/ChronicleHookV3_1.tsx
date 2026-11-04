import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { StablePush } from "../StablePush";
import { PaintedArchivalStrike } from "../PaintedArchivalStrike";
import { ChronicleTitleRevealV3_1 } from "../ChronicleTitleRevealV3_1";

export type ChronicleHookV3_1Props = {
  readonly image?: string;
  readonly title?: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  /** Stroke enter start frame (v3.1 default 0.25s → 8 @30) */
  readonly strokeEnterStart?: number;
  /** Stroke fully across (v3.1 default 0.85s → 26 @30) */
  readonly strokeEnterEnd?: number;
  /** Stroke clear begin (v3.1 default 2.80s → 84 @30) */
  readonly strokeClearStart?: number;
  /** Stroke gone (v3.1 default 3.50s → 105 @30) */
  readonly strokeClearEnd?: number;
  /** Title manifest window open (v3.1 default 0.45s → 14 @30) */
  readonly manifestStart?: number;
  /** Title fully settled (v3.1 default 1.40s → 42 @30) */
  readonly manifestEnd?: number;
  /** Title exit begin (v3.1 default 2.50s → 75 @30) */
  readonly exitStart?: number;
  /** Title gone (v3.1 default 3.15s → 95 @30) */
  readonly exitEnd?: number;
  readonly fontSize?: number;
  readonly color?: string;
  /** Lifted corridor vs v3's 61. Default 57. */
  readonly topPercent?: number;
  readonly offsetX?: number;
  readonly strokeBandHeightPercent?: number;
  readonly strokePeakOpacity?: number;
  readonly strokeFillColor?: string;
  readonly strokeEdgeColor?: string;
  readonly strokeMidColor?: string;
  /** Soft scale-from on letter enter. Default 0.92. */
  readonly letterScaleFrom?: number;
  readonly letterScaleTo?: number;
  readonly letterExitScaleTo?: number;
  readonly settleYPx?: number;
  readonly afterEdgeLagFrames?: number;
  readonly letterSettleFrames?: number;
};

/**
 * Chronicle Reveal v3.1 — lifted corridor + authored scale/Y/opacity
 * letter-manifest + ~4.0s / 120f retiming.
 * Leaves ChronicleHookV3 (90f) intact for archived QC reproducibility.
 * StablePush unchanged. NO pointer / shake / letterbox / TEMP /
 * bright modern red / K&G clone / typewriter / karaoke / fade-only.
 */
export const ChronicleHookV3_1: React.FC<ChronicleHookV3_1Props> = ({
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
  strokeBandHeightPercent = 11,
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
        />
      </StablePush>
    </AbsoluteFill>
  );
};
