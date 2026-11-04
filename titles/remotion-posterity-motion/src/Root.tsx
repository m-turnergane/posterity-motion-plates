import "./index.css";
import { Composition } from "remotion";
import { staticFile } from "remotion";
import { ChronicleHook } from "./PosterityMotion/compositions/ChronicleHook";
import { ChronicleHookV2 } from "./PosterityMotion/compositions/ChronicleHookV2";
import { ChronicleHookV3 } from "./PosterityMotion/compositions/ChronicleHookV3";
import { ChronicleHookV3_1 } from "./PosterityMotion/compositions/ChronicleHookV3_1";
import { ChronicleHookV3_2 } from "./PosterityMotion/compositions/ChronicleHookV3_2";
import { ChronicleHookV3_2b } from "./PosterityMotion/compositions/ChronicleHookV3_2b";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ChronicleHook"
        component={ChronicleHook}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          fontSize: 56,
          color: "#F3EDE0",
          topPercent: 62,
          offsetX: -24,
        }}
      />
      <Composition
        id="ChronicleHookV2"
        component={ChronicleHookV2}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          shadowEnterStart: 6,
          shadowEnterEnd: 14,
          revealStart: 9,
          revealEnd: 29,
          fadeStart: 68,
          fadeEnd: 80,
          fontSize: 72,
          color: "#F3EDE0",
          topPercent: 61,
          offsetX: -20,
          showHairline: false,
          hairlineColor: "rgba(212, 175, 110, 0.65)",
          shadowPeakOpacity: 0.50,
          shadowBandHeightPercent: 16,
          staggerSpanFrames: 1.8,
        }}
      />
      <Composition
        id="ChronicleHookV3"
        component={ChronicleHookV3}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 6,
          strokeEnterEnd: 20,
          strokeClearStart: 63,
          strokeClearEnd: 77,
          manifestStart: 11,
          manifestEnd: 32,
          exitStart: 57,
          exitEnd: 71,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 61,
          offsetX: -16,
          strokeBandHeightPercent: 11,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
        }}
      />
      <Composition
        id="ChronicleHookV3-1"
        component={ChronicleHookV3_1}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 11,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
        }}
      />

      <Composition
        id="ChronicleHookV3-2"
        component={ChronicleHookV3_2}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 13,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: 0,
        }}
      />

      <Composition
        id="ChronicleHookV3-2b"
        component={ChronicleHookV3_2b}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* Extended StablePush for Day11 Ani OWNER-ROUGH v2: continuous push 0→7.533s @ same 1%/s rate as locked 100→104%/4s. Title timing/exit KEPT (clears ~4s). */}
      <Composition
        id="ChronicleHookV3-2b-ext"
        component={ChronicleHookV3_2b}
        durationInFrames={226}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_cathedral_hook_OWNER.png"),
          title: "CITY OF CHURCHES",
          fromScale: 1,
          toScale: 1.0753333333,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />


      {/* Day12 Cahokia OWNER-ROUGH: continuous StablePush Seq1 ~4.100s @1%/s; title MONKS MOUND CAPITAL; locked v3.2b knobs */}
      <Composition
        id="ChronicleHookV3-2b-ext-cahokia"
        component={ChronicleHookV3_2b}
        durationInFrames={123}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_monks_mound_HOOK_OWNER.png"),
          title: "MONKS MOUND CAPITAL",
          fromScale: 1,
          toScale: 1.041,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 60,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />


      {/* Day13 Hampi OWNER-ROUGH v2 chronology: OPEN on chariot street from frame one (NO pre-hook market); continuous StablePush ~5.000s @1%/s; title TALIKOTA FALL; locked v3.2b knobs */}
      <Composition
        id="ChronicleHookV3-2b-ext-hampi"
        component={ChronicleHookV3_2b}
        durationInFrames={150}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_temple_street_HOOK_OWNER.png"),
          title: "TALIKOTA FALL",
          fromScale: 1,
          toScale: 1.05,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* Day14 Ayutthaya OWNER-ROUGH: continuous StablePush Seq1 ~5.200s @1%/s; title AYUTTHAYA SACK; locked v3.2b knobs */}
      <Composition
        id="ChronicleHookV3-2b-ext-ayutthaya"
        component={ChronicleHookV3_2b}
        durationInFrames={156}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_prang_river_sack_HOOK_OWNER.png"),
          title: "AYUTTHAYA SACK",
          fromScale: 1,
          toScale: 1.052,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 64,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />


      {/* Day15 Persepolis OWNER-ROUGH v1: continuous StablePush Seq1 ~5.200s @1%/s; title PERSEPOLIS BURN; locked v3.2b knobs */}
      <Composition
        id="ChronicleHookV3-2b-ext-persepolis"
        component={ChronicleHookV3_2b}
        durationInFrames={156}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_persepolis_burn_HOOK_OWNER.png"),
          title: "PERSEPOLIS BURN",
          fromScale: 1,
          toScale: 1.052,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 64,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch I ROUGH v1: continuous StablePush Seq1 5.200s @1%/s; title THE BLOOD BEFORE TROY; locked v3.2b knobs; fontSize reduced if title overflows */}
      <Composition
        id="ChronicleHookV3-2b-ext-after-troy-ch1"
        component={ChronicleHookV3_2b}
        durationInFrames={156}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_after_troy_ch1_HOOK_KEEP.png"),
          title: "THE BLOOD\nBEFORE TROY",
          fromScale: 1,
          toScale: 1.052,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 108,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch I ROUGH v2: same locked v3.2b title. Optional kicker only on this id. */}
      <Composition
        id="ChronicleHookV3-2b-ext-after-troy-ch1-v2"
        component={ChronicleHookV3_2b}
        durationInFrames={156}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq01_after_troy_ch1_HOOK_v2_KEEP.png"),
          title: "THE BLOOD\nBEFORE TROY",
          kicker: "AFTER TROY · CHAPTER I",
          fromScale: 1,
          toScale: 1.052,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 108,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />



      {/* After Troy Ch II — faithful Chronicle Reveal v3.2b QC (THE DAUGHTER).
          Locked Ani knobs: band 14, topPercent 57, nudgeY -4, timing table, oxblood hex.
          Strike proportions NEVER stretched for copy. Param: title + durationInFrames.
          No kicker / chapter marker. Plate = Seq1 bride (public copy of plates/seq1-veil-shore.png). */}
      <Composition
        id="ChronicleHookV3-2b-after-troy-ch2-daughter"
        component={ChronicleHookV3_2b}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_after_troy_ch2_HOOK_KEEP.png"),
          // TITLE CONSTANT — swap this string only
          title: "THE DAUGHTER",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          // Compact two-word mark; size fits inside locked band 14 (do not thicken band)
          fontSize: 108,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch III — Chronicle Reveal v3.2b QC (THE KING COMES HOME).
          Locked Ani knobs: band 14, topPercent 57, nudgeY -4. Two-line title so
          strike stays natural (~9% optical), never stretched. */}
      <Composition
        id="ChronicleHookV3-2b-after-troy-ch3-king"
        component={ChronicleHookV3_2b}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1a_after_troy_ch3_HOOK_KEEP.png"),
          title: "THE KING\nCOMES HOME",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 92,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch III Seq1A assemble — same reveal knobs, longer push past title exit. */}
      <Composition
        id="ChronicleHookV3-2b-ext-after-troy-ch3-king"
        component={ChronicleHookV3_2b}
        durationInFrames={200}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1a_after_troy_ch3_HOOK_KEEP.png"),
          title: "THE KING\nCOMES HOME",
          fromScale: 1,
          toScale: 1.05,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 92,
          color: "#F3EDE0",
          topPercent: 57,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch II ROUGH v2 PRE: TITLE CONSTANT below — swap text only when mark changes.
          v1 used THE DAUGHTER @108 (archived hook in _rough_v1_work). Seq1 motion unchanged (StablePush 1→1.055). */}
      <Composition
        id="ChronicleHookV3-2b-ext-after-troy-ch2"
        component={ChronicleHookV3_2b}
        durationInFrames={590}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1_after_troy_ch2_HOOK_KEEP.png"),
          // === TITLE CONSTANT (single place to swap) ===
          title: "THE BRIDE\nWHO BOUGHT\nTHE FLEET’S WIND",
          fromScale: 1,
          toScale: 1.055,
          strokeEnterStart: 8,
          strokeEnterEnd: 28,
          strokeClearStart: 88,
          strokeClearEnd: 110,
          manifestStart: 14,
          manifestEnd: 48,
          exitStart: 78,
          exitEnd: 95,
          fontSize: 68,
          color: "#F3EDE0",
          // v2b: tall band + upward nudge so 3 lines clear jagged brush troughs; band bottom < caption top ~1390
          topPercent: 40,
          offsetX: -16,
          strokeBandHeightPercent: 56,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -20,
        }}
      />


      {/* After Troy Ch IV — Chronicle Reveal v3.2b QC (THE SON AND THE FURIES).
          Two-line lockup; strike upper-middle above statue head. */}
      <Composition
        id="ChronicleHookV3-2b-after-troy-ch4-son"
        component={ChronicleHookV3_2b}
        durationInFrames={120}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1a_after_troy_ch4_HOOK_KEEP.png"),
          title: "THE SON\nAND THE FURIES",
          fromScale: 1,
          toScale: 1.04,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 88,
          color: "#F3EDE0",
          topPercent: 34,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

      {/* After Troy Ch IV Seq1A assemble — longer push past title exit. */}
      <Composition
        id="ChronicleHookV3-2b-ext-after-troy-ch4-son"
        component={ChronicleHookV3_2b}
        durationInFrames={220}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          image: staticFile("plates/seq1a_after_troy_ch4_HOOK_KEEP.png"),
          title: "THE SON\nAND THE FURIES",
          fromScale: 1,
          toScale: 1.055,
          strokeEnterStart: 8,
          strokeEnterEnd: 26,
          strokeClearStart: 84,
          strokeClearEnd: 105,
          manifestStart: 14,
          manifestEnd: 42,
          exitStart: 75,
          exitEnd: 95,
          fontSize: 88,
          color: "#F3EDE0",
          topPercent: 34,
          offsetX: -16,
          strokeBandHeightPercent: 14,
          strokePeakOpacity: 0.92,
          strokeFillColor: "#5A1A18",
          strokeEdgeColor: "#3A0E0C",
          strokeMidColor: "#6E2A1C",
          letterScaleFrom: 0.92,
          letterScaleTo: 1.0,
          letterExitScaleTo: 0.94,
          settleYPx: 4,
          afterEdgeLagFrames: 2,
          letterSettleFrames: 12,
          titleAnchor: "center",
          titleAnchorNudgeYPx: -4,
        }}
      />

    </>
  );
};
