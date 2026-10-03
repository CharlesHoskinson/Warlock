# Four texel-center bilinear experiment

This fresh diagnostic derivative retains immutable producer V5 and the complete
independent reference. It tests a causal hypothesis; no GPU cause or production
repair is established. The existing GPU path remains the default. An explicit
`--manual-bilinear-experiment` option requires raster diagnostic mode and causal
readback. Neither diagnostic variant can emit native ready/endpoint authority.

## Sampling semantics, specified before implementation

For each fragment, retain the original interpolated normalized UV and quad
geometry. Let `s = UV * sourcePixelExtent - 0.5`, `i = floor(s)` and
`f = s - i`. Fetch four immutable premultiplied RGBA texels at centers of
`clamp(i + (dx,dy), 0, extent - 1)` using NEAREST min/mag and CLAMP_TO_EDGE.
Compute their convex bilinear sum in explicitly highp floating point, using
weights `(1-f.x)*(1-f.y)`, `f.x*(1-f.y)`, `(1-f.x)*f.y`, `f.x*f.y`.
Do not round/interpolate source channels as integers before blending.

The source extent comes from the verified immutable PNG upload, not the native
window rectangle or inferred scaling. Missing, stale or invalid texture extent
fails the diagnostic. Texture replacement removes old extent associations.
Spatially constant controls use their actual one-by-one extent. Source uploads
remain once per immutable snapshot, with no CPU resize or frame reupload.

All other semantics remain fixed: exact source decode/premultiplication,
ordered family vector, current member rectangles, output buffer extents,
transparent clear, dithering disabled, ONE / ONE_MINUS_SRC_ALPHA fixed-function
source-over, RGBA8 per-draw quantization, read pair, own successful-swap ledger,
presentation authority and lifetime guards. Manual arithmetic replaces hardware
LINEAR filtering only. It does not eliminate interpolation, blend/attachment or
shader arithmetic uncertainty, and equal output would not independently prove
which hardware stage caused the old error.

## Acceptance and boundaries

Emit an actual sampling configuration event with mode, texture ID, immutable
source digest, source extent, queried min/mag/wrap states and GL inspection
status. The header defines the exact shader selected by the explicit mode;
source/binary freeze is mandatory. Configuration is not itself pixel proof.
Retain all complete prefix/control/raw/composed comparisons, original aligned
zero/fractional-one channel bounds, both progress samples and both outputs.
No tolerance change, reference fitting, pixel mask, endpoint/source reset or
cadence claim is permitted. Ordinary collector shutdown must remain normal.

This experiment is motivated by V7's equal complete read formats and constant
controls plus accumulation of small textured per-draw differences. Those
observations do not uniquely identify hardware sampling. A full native run and
source-bound comparison are required before considering integration.

## Primary rules

The Khronos OpenGL ES 3.2 specification, texture filtering and fragment/blend
chapters, defines nearest texel selection, center-relative linear weights and
normalized texture values. The shader spells out those weights while retaining
fixed-function source-over. It does not assume an unspecified GPU sampler
coefficient precision or a particular Mesa hardware blend branch.
https://registry.khronos.org/OpenGL/specs/es/3.2/es_spec_3.2.pdf
