import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { StablePush } from "../StablePush";
import { ChronicleTitleReveal } from "../ChronicleTitleReveal";

export type ChronicleHookProps = {
  readonly image?: string;
  readonly title?: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  readonly revealStart?: number;
  readonly revealEnd?: number;
  readonly fadeStart?: number;
  readonly fadeEnd?: number;
  readonly fontSize?: number;
  readonly color?: string;
  readonly topPercent?: number;
  readonly offsetX?: number;
};

/**
 * Episode supplies image, title, timing, push amount via props.
 * No ravine line / pointer / ArchitectureTrace on this hook.
 */
export const ChronicleHook: React.FC<ChronicleHookProps> = ({
  image = staticFile("plates/seq1_cathedral_hook_OWNER.png"),
  title = "CITY OF CHURCHES",
  fromScale = 1,
  toScale = 1.04,
  revealStart,
  revealEnd,
  fadeStart,
  fadeEnd,
  fontSize = 56,
  color = "#F3EDE0",
  topPercent = 62,
  offsetX = -24,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <StablePush src={image} fromScale={fromScale} toScale={toScale}>
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
        />
      </StablePush>
    </AbsoluteFill>
  );
};
