import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { StablePush } from "../StablePush";
import { PaintedArchivalStrike } from "../PaintedArchivalStrike";
import { ChronicleTitleRevealV3 } from "../ChronicleTitleRevealV3";

export type ChronicleHookV3Props = {
  readonly image?: string;
  readonly title?: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  /** Stroke enter start frame (default 0.20s → 6 @30) */
  readonly strokeEnterStart?: number;
  /** Stroke fully across (default 0.65s → 20 @30) */
  readonly strokeEnterEnd?: number;
  /** Stroke clear begin (default 2.10s → 63 @30) */
  readonly strokeClearStart?: number;
  /** Stroke gone (default 2.55s → 77 @30) */
  readonly strokeClearEnd?: number;
  /** Title manifest window open (default 0.35s → 11 @30) */
  readonly manifestStart?: number;
  /** Title fully settled (default 1.05s → 32 @30) */
  readonly manifestEnd?: number;
  /** Title exit begin (default 1.90s → 57 @30) */
  readonly exitStart?: number;
  /** Title gone (default 2.35s → 71 @30) */
  readonly exitEnd?: number;
  readonly fontSize?: number;
  readonly color?: string;
  readonly topPercent?: number;
  readonly offsetX?: number;
  readonly strokeBandHeightPercent?: number;
  readonly strokePeakOpacity?: number;
  readonly strokeFillColor?: string;
  readonly strokeEdgeColor?: string;
  readonly strokeMidColor?: string;
};

/**
 * Chronicle Reveal v3 — branded painted-strike graphic event.
 * StablePush plate + PaintedArchivalStrike + ChronicleTitleRevealV3.
 * Leaves v1/v2 + ArchivalShadowField untouched. NO pointer / shake /
 * letterbox / TEMP / bright modern red / K&G clone / typewriter / karaoke.
 */
export const ChronicleHookV3: React.FC<ChronicleHookV3Props> = ({
  image = staticFile("plates/seq1_cathedral_hook_OWNER.png"),
  title = "CITY OF CHURCHES",
  fromScale = 1,
  toScale = 1.04,
  strokeEnterStart = 6,
  strokeEnterEnd = 20,
  strokeClearStart = 63,
  strokeClearEnd = 77,
  manifestStart = 11,
  manifestEnd = 32,
  exitStart = 57,
  exitEnd = 71,
  fontSize = 68,
  color = "#F3EDE0",
  topPercent = 61,
  offsetX = -16,
  strokeBandHeightPercent = 11,
  strokePeakOpacity = 0.92,
  strokeFillColor = "#5A1A18",
  strokeEdgeColor = "#3A0E0C",
  strokeMidColor = "#6E2A1C",
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
        <ChronicleTitleRevealV3
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
          settleYPx={4}
          afterEdgeLagFrames={2}
          letterSettleFrames={8}
          trackingEm={0.02}
        />
      </StablePush>
    </AbsoluteFill>
  );
};
