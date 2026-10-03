# Retained V6 causal boundaries

## Established observations

Root's complete raw/composed comparisons bind the exact token, generation,
successful swap and immutable member vector. All four composed images equal
raw RGB over opaque black at every pixel. Seven scaled-origin pixels and two
scaled-interior pixels fail the unchanged one-channel quantization bound in
both images. The actual producer buffer is RGBA8, without multisampling.

The actual frozen upload method, executed with CPU stubs only for texture GL
calls, emits bytes equal to the independent decode and premultiplication for
all three complete source textures. This observes bytes passed to the texture
upload boundary, not the GPU's stored texture. Exact rational bilinear and
ordered source-over agree with the unchanged reference at all nine failed
pixels. Reconstructing the CPU's float32 quad corners also yields the same
ideal RGBA there. None of these calculations uses actual pixels as input.

These observations exclude source CPU decode/premultiplication, reference
double arithmetic, CPU float32 corner conversion alone, and compositor
composition as sufficient explanations of these retained failures. Dither
disabled and explicit highp experiments previously left the failures intact.
Hardware sampling/interpolation, blend arithmetic, attachment conversion and
readback conversion are not independently localized yet.

## Specification and exact implementation

The actual version is OpenGL ES 3.2. Its texture filtering and blending rules
describe interpolation and source-over, while allowing internal representations
within their precision rules. Section 15.1.5.1 treats fragment input as floating
point, with separate interpretation if represented internally as fixed point.
Thus earlier ES2 wording is not proof of a particular source quantization stage.
Framebuffer component bits do not establish sampler or blend precision.
[Khronos OpenGL ES 3.2 specification](https://registry.khronos.org/OpenGL/specs/es/3.2/es_spec_3.2.pdf)

The retained exact Mesa 26.2.2 archive supplies the primary code copied under
primary/. iris_state.c programs min/mag filter and hardware blend factors,
pre/post clamps and render-target format clamping. It does not expose an
effective coefficient precision in these functions. A generation-conditional
floating blend flag does not establish the active hardware branch from the
renderer string alone. st_cb_readpixels.c supports matching-format direct
copies, conversion blits and fallback paths; the observed format query alone
does not identify which path executed. No driver precision conclusion follows.
[Mesa 26.2.2 source archive](https://archive.mesa3d.org/mesa-26.2.2.tar.xz)

## Next controlled diagnostic, proposed only

Keep the current shader, textures, order, rectangles and final four whole-image
acceptance comparisons unchanged. In a fresh diagnostic candidate only:

1. Read back the complete transparent buffer after each ordered member draw.
   Bind each prefix to its exact scene vector, member count and token. Compare
   against independent complete-prefix reference pixels. Prefixes are not
   committed scenes and must never emit presentation or native authority.
2. For the first divergent prefix, distinguish nearest texture-center samples
   from linear samples using predetermined asymmetric texture controls. Verify
   uploaded texels at exact centers before attributing interpolation.
3. Use predetermined spatially constant premultiplied source/destination
   controls to test blend/attachment quantization without sampling gradients.
4. Compare RGBA and supported implementation-native read format, with explicit
   component reordering only, before attributing an observed prefix difference
   solely to sampling or blending.

All controls require declared pixel math and full-image comparisons. Timing
from readback cannot establish production cadence. No repair, tolerance change,
region exclusion, source re-upload per frame, or compositor mutation is proposed
in this packet. Manual bilinear sampling is an option only after a controlled
sampling boundary is established; it does not itself resolve blend uncertainty.
