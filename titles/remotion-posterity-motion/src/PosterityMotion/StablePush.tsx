import React from "react";
import {
  AbsoluteFill,
  CanvasImage,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type StablePushProps = {
  readonly src: string;
  readonly fromScale?: number;
  readonly toScale?: number;
  readonly durationInFrames?: number;
  readonly children?: React.ReactNode;
};

/**
 * Centre-anchored scale-only push. No x/y translation, shake, or zoompan.
 * Image fills AbsoluteFill with object-fit cover (CanvasImage fit="cover").
 */
export const StablePush: React.FC<StablePushProps> = ({
  src,
  fromScale = 1,
  toScale = 1.04,
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames: compositionDuration } = useVideoConfig();
  const duration = durationInFrames ?? compositionDuration;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill
        style={{
          transformOrigin: "center center",
          scale: interpolate(frame, [0, duration], [fromScale, toScale], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.linear,
            output: "perceptual-scale",
          }),
        }}
      >
        <CanvasImage
          src={src}
          fit="cover"
          style={{
            width: "100%",
            height: "100%",
          }}
        />
      </AbsoluteFill>
      {children ? <AbsoluteFill>{children}</AbsoluteFill> : null}
    </AbsoluteFill>
  );
};
