# Explicit shader precision causal candidate

Retain V3/V4 actual failures,77 original inputs and108 no-dither inputs. V4
confirmed actual DITHER true→false/error0 and private cursor invisible, removing
all369 cursor failures. Its identical seven member errors disprove dithering as
their cause. No error coordinate is masked, and tolerance0/1 remains unchanged.

The fresh candidate declares highp on float computation, the varying in both
stages and the sampler2D. Before compiling the shaders it inspects actual low,
medium and high float precision in vertex/fragment stages and records ranges,
precision and GL error. Require at least23 high precision bits/range127 in both
stages for this pinned-hardware experiment; unsupported capability fails before
source upload/readiness. Shader compile/link failures also fail closed. This
removes an allowed low-precision sample/interpolation boundary without altering
linear filtering, blending, alpha, geometry, source bytes or presentation ledger.

GLSL ES1.00§4.5.3 defines default sampler2D as lowp independently of default
float;§8 says a texture lookup's result precision follows its sampler. Existing
fragment code only set mediump float, so sampler results had an implicit lowp
contract. Making just default float highp would not remove that result boundary.
Primary https://registry.khronos.org/OpenGL/specs/es/2.0/GLSL_ES_Specification_1.00.pdf .
Exact Mesa26.2.2 shaderapi.c2297–2345 supplies the actual queried precision from
context program limits; hardware sampler quantization remains implementation
specific. Reported precision and a compiled highp shader do not prove that
fixed-function filtering/blending produces the independent oracle within one.

This is a causal experiment with no predicted PASS: if the seven errors remain,
retain that outcome and investigate sampler/filter/output blend quantization
with independent controls. Do not fit CPU rounding to measured screenshots or
relax full-raster acceptance. Physical240Hz/service/native-family acceptance is
separate and still open. Offline shader syntax is not native Mesa compilation.
