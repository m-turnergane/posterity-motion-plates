import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { StablePush } from "../StablePush";
import { ArchivalShadowField } from "../ArchivalShadowField";
import { ChronicleTitleReveal } from "../ChronicleTitleReveal";

export type ChronicleHookV2Props = {
  readonly image?: string;
  readonly title?: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  /** Shadow field enter start frame (default 0.20s → 6 @30) */
  readonly shadowEnterStart?: number;
  readonly shadowEnterEnd?: number;
  /** Title reveal start frame (default 0.30s → 9 @30) */
  readonly revealStart?: number;
  /** Title fully resolved (default 0.95s → 28.5 ≈ 29 @30) */
  readonly revealEnd?: number;
  /** Exit begin (default 2.25s → 67.5 ≈ 68 @30) */
  readonly fadeStart?: number;
  /** Title+field gone (default 2.65s → 79.5 ≈ 80 @30) */
  readonly fadeEnd?: number;
  readonly fontSize?: number;
  readonly color?: string;
  readonly topPercent?: number;
  readonly offsetX?: number;
  readonly showHairline?: boolean;
  readonly hairlineColor?: string;
  readonly shadowPeakOpacity?: number;
  readonly shadowBandHeightPercent?: number;
  readonly staggerSpanFrames?: number;
};

/**
 * Chronicle Reveal v2 — Recovered Chronicle signature.
 * StablePush plate + ArchivalShadowField wash + ChronicleTitleReveal.
 * NO ravine pointer / solid rect / glow / bounce / typewriter / shimmer.
 * Props-only for image/title/timing/placement.
 */
export const ChronicleHookV2: React.FC<ChronicleHookV2Props> = ({
  image = staticFile("plates/seq1_cathedral_hook_OWNER.png"),
  title = "CITY OF CHURCHES",
  fromScale = 1,
  toScale = 1.04,
  shadowEnterStart = 6,
  shadowEnterEnd = 14,
  revealStart = 9,
  revealEnd = 29,
  fadeStart = 68,
  fadeEnd = 80,
  fontSize = 72,
  color = "#F3EDE0",
  topPercent = 61,
  offsetX = -20,
  showHairline = false,
  hairlineColor = "rgba(212, 175, 110, 0.65)",
  shadowPeakOpacity = 0.50,
  shadowBandHeightPercent = 16,
  staggerSpanFrames = 1.8,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <StablePush src={image} fromScale={fromScale} toScale={toScale}>
        <ArchivalShadowField
          enterStart={shadowEnterStart}
          enterEnd={shadowEnterEnd}
          fadeStart={fadeStart}
          fadeEnd={fadeEnd}
          topPercent={topPercent}
          bandHeightPercent={shadowBandHeightPercent}
          peakOpacity={shadowPeakOpacity}
          offsetX={offsetX}
        />
        <ChronicleTitleReveal
          title={title}
          revealStart={revealStart}
          revealEnd={revealEnd}
          fadeStart={fadeStart}
          fadeEnd={fadeEnd}
          fontSize={fontSize}
          color={color}
          topPercent={topPercent}
          offsetX={offsetX}
          staggerSpanFrames={staggerSpanFrames}
          settleYPx={4}
          trackingFrom={0.07}
          trackingTo={0.015}
          showHairline={showHairline}
          hairlineColor={hairlineColor}
        />
      </StablePush>
    </AbsoluteFill>
  );
};
