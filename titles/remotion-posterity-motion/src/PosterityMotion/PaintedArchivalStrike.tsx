import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type PaintedArchivalStrikeProps = {
  /** Frame when painted drag begins (default ~0.20s → 6 @30) */
  readonly enterStart?: number;
  /** Frame when stroke is fully across (default ~0.65s → 20 @30) */
  readonly enterEnd?: number;
  /** Frame when clear begins (default ~2.10s → 63 @30) */
  readonly clearStart?: number;
  /** Frame when stroke is fully gone (default ~2.55s → 77 @30) */
  readonly clearEnd?: number;
  /** Vertical centre of strike as % from top. Default 61. */
  readonly topPercent?: number;
  /** Band height as % of frame height. Soft irregular ~8–14. Default 11. */
  readonly bandHeightPercent?: number;
  /** Horizontal width as % of frame. Default 94. */
  readonly widthPercent?: number;
  /** Horizontal nudge in px (negative = left). Default -16. */
  readonly offsetX?: number;
  /**
   * Peak opacity of the painted body (0–1). Default 0.92 —
   * opaque enough to read as painted pigment, not a translucent UI band.
   */
  readonly peakOpacity?: number;
  /** Base oxblood / iron-oxide fill. Default #5A1A18. */
  readonly fillColor?: string;
  /** Darker edge / dried-blood shadow. Default #3A0E0C. */
  readonly edgeColor?: string;
  /** Mid iron-oxide accent. Default #6E2A1C. */
  readonly midColor?: string;
};

/**
 * Shared leading-edge progress (0→1) across the enter window.
 * Title letter-manifest gates on this — same easing as the visual drag.
 */
export function getStrokeLeadingEdgeProgress(
  frame: number,
  enterStart: number,
  enterEnd: number,
): number {
  return interpolate(frame, [enterStart, enterEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    // Drag-on: starts with weight, eases out like a loaded brush
    easing: Easing.bezier(0.33, 0.0, 0.2, 1),
  });
}

/** Deterministic irregular brush silhouette (viewBox 0..1000 × 0..200). */
function buildBrushEdgePath(): string {
  const topY = [
    78, 62, 71, 55, 68, 48, 60, 52, 70, 58, 65, 50, 72, 56, 64, 54, 75, 60, 70,
    66, 80,
  ];
  const botY = [
    128, 142, 135, 150, 138, 155, 140, 148, 132, 145, 138, 152, 130, 144, 136,
    150, 125, 140, 134, 138, 122,
  ];
  const n = topY.length;
  let d = `M 0 ${topY[0]}`;
  for (let i = 1; i < n; i++) {
    const x = (i / (n - 1)) * 1000;
    const prevX = ((i - 1) / (n - 1)) * 1000;
    const cpx = (prevX + x) / 2;
    d += ` Q ${cpx} ${topY[i - 1]} ${x} ${topY[i]}`;
  }
  d += ` L 1000 ${botY[n - 1]}`;
  for (let i = n - 2; i >= 0; i--) {
    const x = (i / (n - 1)) * 1000;
    const prevX = ((i + 1) / (n - 1)) * 1000;
    const cpx = (prevX + x) / 2;
    d += ` Q ${cpx} ${botY[i + 1]} ${x} ${botY[i]}`;
  }
  d += " Z";
  return d;
}

const BRUSH_EDGE_PATH = buildBrushEdgePath();

/**
 * Weathered oxblood / iron-oxide distressed painted horizontal strike.
 * Rough edges + pigment texture + visible drag-on arrival.
 * NOT a clean rect, flat opacity band, grey charcoal field, or K&G clone.
 */
export const PaintedArchivalStrike: React.FC<PaintedArchivalStrikeProps> = ({
  enterStart: enterStartProp,
  enterEnd: enterEndProp,
  clearStart: clearStartProp,
  clearEnd: clearEndProp,
  topPercent = 61,
  bandHeightPercent = 11,
  widthPercent = 94,
  offsetX = -16,
  peakOpacity = 0.92,
  fillColor = "#5A1A18",
  edgeColor = "#3A0E0C",
  midColor = "#6E2A1C",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enterStart = enterStartProp ?? 0.2 * fps;
  const enterEnd = enterEndProp ?? 0.65 * fps;
  const clearStart = clearStartProp ?? 2.1 * fps;
  const clearEnd = clearEndProp ?? 2.55 * fps;

  if (frame < enterStart || frame >= clearEnd) {
    return null;
  }

  const leadingEdge = getStrokeLeadingEdgeProgress(frame, enterStart, enterEnd);

  // Exit: reverse drag clear (leading edge retreats L←R) + soft opacity
  const clearProgress = interpolate(frame, [clearStart, clearEnd], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });
  const visibleSpan = leadingEdge * (1 - clearProgress);
  const clearOpacity = interpolate(frame, [clearStart, clearEnd], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.4, 0, 0.2, 1),
  });

  // Soft tip bloom while dragging on (dies once fully across)
  const tipBloom =
    leadingEdge > 0 && leadingEdge < 1
      ? interpolate(leadingEdge, [0, 0.15, 0.85, 1], [0.35, 0.55, 0.4, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;

  const bandTop = topPercent - bandHeightPercent / 2;
  const edgePath = BRUSH_EDGE_PATH;

  // SVG noise as feTurbulence (pigment grain) — rendered inside SVG
  const clipRightPercent = (1 - visibleSpan) * 100;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: `${bandTop}%`,
          left: "50%",
          width: `${widthPercent}%`,
          height: `${bandHeightPercent}%`,
          translate: `calc(-50% + ${offsetX}px) 0px`,
          opacity: peakOpacity * clearOpacity,
          // Leading-edge reveal — drag across frame
          clipPath: `inset(0 ${clipRightPercent}% 0 0)`,
          WebkitClipPath: `inset(0 ${clipRightPercent}% 0 0)`,
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 1000 200"
          preserveAspectRatio="none"
          style={{ display: "block", overflow: "visible" }}
        >
          <defs>
            <filter
              id="paintGrain"
              x="-5%"
              y="-15%"
              width="110%"
              height="130%"
              filterUnits="objectBoundingBox"
            >
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.9 0.55"
                numOctaves={4}
                seed={7}
                result="noise"
              />
              <feColorMatrix
                in="noise"
                type="matrix"
                values="0 0 0 0 0.15
                        0 0 0 0 0.04
                        0 0 0 0 0.03
                        0 0 0 0.55 0"
                result="grain"
              />
              <feBlend in="SourceGraphic" in2="grain" mode="multiply" />
            </filter>
            <filter
              id="edgeRough"
              x="-4%"
              y="-20%"
              width="108%"
              height="140%"
            >
              <feTurbulence
                type="turbulence"
                baseFrequency="0.035 0.08"
                numOctaves={3}
                seed={3}
                result="edgeNoise"
              />
              <feDisplacementMap
                in="SourceGraphic"
                in2="edgeNoise"
                scale={6.5}
                xChannelSelector="R"
                yChannelSelector="G"
              />
            </filter>
            <linearGradient id="pigmentGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={edgeColor} stopOpacity={0.55} />
              <stop offset="18%" stopColor={midColor} stopOpacity={0.95} />
              <stop offset="42%" stopColor={fillColor} stopOpacity={1} />
              <stop offset="58%" stopColor={fillColor} stopOpacity={1} />
              <stop offset="78%" stopColor={midColor} stopOpacity={0.92} />
              <stop offset="100%" stopColor={edgeColor} stopOpacity={0.5} />
            </linearGradient>
            <linearGradient id="lengthGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#2A0A08" stopOpacity={0.35} />
              <stop offset="8%" stopColor={fillColor} stopOpacity={0} />
              <stop offset="50%" stopColor="#7A3220" stopOpacity={0.12} />
              <stop offset="92%" stopColor={fillColor} stopOpacity={0} />
              <stop offset="100%" stopColor="#2A0A08" stopOpacity={0.4} />
            </linearGradient>
            {/* Dry-brush mottling spots */}
            <radialGradient id="mottleA" cx="28%" cy="45%" r="38%">
              <stop offset="0%" stopColor="#2E0C0A" stopOpacity={0.45} />
              <stop offset="100%" stopColor={fillColor} stopOpacity={0} />
            </radialGradient>
            <radialGradient id="mottleB" cx="68%" cy="58%" r="32%">
              <stop offset="0%" stopColor="#8A3A28" stopOpacity={0.28} />
              <stop offset="100%" stopColor={fillColor} stopOpacity={0} />
            </radialGradient>
            <radialGradient id="mottleC" cx="48%" cy="40%" r="55%">
              <stop offset="0%" stopColor="#4A1410" stopOpacity={0.2} />
              <stop offset="100%" stopColor={fillColor} stopOpacity={0} />
            </radialGradient>
          </defs>

          <g filter="url(#edgeRough)">
            <path
              d={edgePath}
              fill="url(#pigmentGrad)"
              filter="url(#paintGrain)"
            />
            <path d={edgePath} fill="url(#lengthGrad)" />
            <path d={edgePath} fill="url(#mottleA)" />
            <path d={edgePath} fill="url(#mottleB)" />
            <path d={edgePath} fill="url(#mottleC)" />
          </g>

          {/* Soft leading-edge tip bloom while dragging */}
          {tipBloom > 0.01 ? (
            <ellipse
              cx={leadingEdge * 1000}
              cy={100}
              rx={28}
              ry={42}
              fill={midColor}
              opacity={tipBloom * 0.55}
              filter="url(#edgeRough)"
            />
          ) : null}
        </svg>

        {/* Extra CSS noise veil for tactile grit Remotion SVG alone won't give */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            opacity: 0.22,
            mixBlendMode: "multiply",
            pointerEvents: "none",
            backgroundImage: NOISE_DATA_URI,
            backgroundSize: "180px 180px",
            // Softly mask to stroke band so grit doesn't read as a card
            maskImage:
              "linear-gradient(90deg, transparent 0%, black 4%, black 96%, transparent 100%), linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)",
            WebkitMaskImage:
              "linear-gradient(90deg, transparent 0%, black 4%, black 96%, transparent 100%), linear-gradient(180deg, transparent 0%, black 18%, black 82%, transparent 100%)",
            maskComposite: "intersect",
            WebkitMaskComposite: "source-in",
          }}
        />
      </div>

      {/* Slight vertical irregularity: a faint secondary drag ridge */}
      <div
        style={{
          position: "absolute",
          top: `${bandTop + bandHeightPercent * 0.62}%`,
          left: "50%",
          width: `${widthPercent * 0.88}%`,
          height: `${bandHeightPercent * 0.22}%`,
          translate: `calc(-50% + ${offsetX + 12}px) 0px`,
          opacity: peakOpacity * 0.28 * clearOpacity * leadingEdge,
          clipPath: `inset(0 ${clipRightPercent}% 0 0)`,
          WebkitClipPath: `inset(0 ${clipRightPercent}% 0 0)`,
          background: `linear-gradient(90deg, transparent 0%, ${edgeColor} 12%, ${midColor} 50%, ${edgeColor} 88%, transparent 100%)`,
          filter: "blur(1.4px)",
          borderRadius: "40% 60% 55% 45% / 70% 40% 60% 30%",
        }}
      />
    </AbsoluteFill>
  );
};

/** Tiny procedural noise PNG as data-URI (deterministic grit). */
const NOISE_DATA_URI =
  "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.9'/%3E%3C/svg%3E\")";
