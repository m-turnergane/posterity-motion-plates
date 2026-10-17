# Architecture

## Recipe schema (YAML)
```yaml
name: ...; plate: {file: <png in $MOTIONPLATES_PLATES>}; output: {width,height,fps,seconds}; seed: int
frame0_residual_fade_s: 0.7        # residual that makes frame 0 == plate fades out over this time
stills: [seconds...]               # labelled stills
safe_zones: [{name, box:[x0,y0,x1,y1], max_mean_delta}]   # caption/title areas that must stay calm (tested)
clean_plate: {method: telea_exclude, radius, texture, hole_grow, exclude: [polygon...]}
layers:   # back -> front. depth 0=far .. 1=near
  - {name, depth, polygons:[[x,y]...], grow, feather, refine: {band}}   # refine = GrabCut inside band
elements: # alpha elements pinned to bg depth, animated individually (banners)
  - {name, depth, polygons, grow, feather}
effects:  # each {type|preset, ...params}; presets in recipes/presets/*.yaml, recipe values override
```
## Effect primitives
| type | what it does | key params |
|---|---|---|
| `parallax_push` | eased scale about an anchor, per-layer amount (bg<mid<fg) -> differential parallax | anchor, end_scale{bg,mid,fg}, t0,t1 |
| `petal_fall` | cuts the plate's own suspended petals (ellipse seed + GrabCut or luma), removes them from the clean plate, re-animates them + seeded extra copies: fall with 3-D flutter (tilt/sx/sy/rot), flatten near the surface, bounce, slide, contact shadow clipped to the surface polygon, pall tint | cuts, release_s, surface{polygon,land_y}, extras, physics |
| `flame_flicker` | flame ROI warp (noise displacement, rising bias) + hot/cool colour shift + localized warm light with falloff on named layers; multi-band smooth-noise flicker (never a sine pulse) | flames[{x,y,rx,ry,layer,warp_px,rise_px,light_R,light_gain,light_layers}] |
| `torch_light` | wider torch light per source + keyframed low-frequency shadow noise (soft moving shadow modulation) limited to a region | sources, shadow{amount,light_mod,region,keyframe_s} |
| `banner_sway` | displacement of an alpha element pinned at the top, growing to the hem (travelling sine + noise), slight foreshortening | elements, amp_px, freq_hz |
| `fabric_ripple` | sub-pixel travelling wave + shading modulation inside a polygon | layer, region, amp_px, shade, wavelength_px |
| `dust_motes` | seeded lit dust, drifts with noise, parallax by depth, bright-shaft bias, twinkle, fade-in | count, size, depth, luma_bias, intensity |

## Frame-0 contract
Frame 0 = effects at zero + layers composed at identity + petals at their original pixel positions. The small remainder (feather rims, petal rims) is stored as a residual image and added back with weight `1 - smoothstep(t/fade)`, so frame 0 is bit-equal to the plate before encoding. Manifest records `pre_residual_*` (how large the swap diff is).

## Why not Remotion
Layered numpy compositing already gives per-pixel control, determinism and the same ffmpeg encode path as the editor. Remotion adds a browser runtime, lossy colour-matrix drift and a second engine for effects that are simple here; revisit only for shader-like effects (volumetric light, smoke).
