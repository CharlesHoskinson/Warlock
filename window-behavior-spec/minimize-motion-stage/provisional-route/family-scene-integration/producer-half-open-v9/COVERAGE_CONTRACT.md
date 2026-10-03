# Half-open pixel-center source coverage

This fresh diagnostic producer inherits frozen GPU V8 and retains native V10's
44 immutable oracle images and failed comparisons. The ordinary producer path,
original independent CPU oracle, tolerance and native-authority boundary remain
unchanged. A selected quantized-over pass covers the full owned output buffer;
member coverage is decided explicitly for each top-left pixel center.

The V10 first divergent pass is secondary output p=.35, prefix 2. All 83 failed
pixels occupy x20..102/y157, and each actual byte equals the preceding prefix.
The child top edge y105 projects to buffer y157.5. GPU polygon boundary rules
omitted this row, whereas the original oracle includes top/left edges and excludes
bottom/right edges. Sampling, over rounding and both readback formats are separate
from this observed coverage omission.

For each axis, a pixel is covered exactly when
`rectangleStart <= outputOrigin + (pixel + .5) * logicalExtent / bufferExtent < rectangleEnd`.
The CPU derives bounded integer first/last indices by monotonic binary searches
using that same double center expression. The search avoids ceil expressions
whose intermediate rounding can change a half-center boundary. Coverage is
clipped to the current output extent. Rectangles and output dimensions must be
finite, positive and bounded before any pass/configuration is appended.

Each pass uploads four exact integer coverage limits and four float sample-rect
coordinates in output-buffer units. The fragment shader obtains the exact
top-left half-center from gl_FragCoord, preserves the previous prefix outside
the explicit half-open limits, and obtains source UV from that center and the
sample rectangle. The existing manual four-nearest-center sampler and per-layer
RGBA8 source-over rounding remain in use. The full-screen primitive cannot lose
a member's interior half-center edge to polygon rasterization.

Actual queried coverage and sample uniforms, full-screen position vector,
logical rectangle/output, shader roles, immutable source texture/digest and
ordered prefix continuation must agree before a pass is accepted. Controls bind
the entire logical output; family passes bind each exact frame member rectangle.
These configuration gates grant no pixel, presentation or native authority.
Final and every causal prefix still require the unchanged full-image comparisons,
owned default-framebuffer read pair and exact original generation/sequence binds.
