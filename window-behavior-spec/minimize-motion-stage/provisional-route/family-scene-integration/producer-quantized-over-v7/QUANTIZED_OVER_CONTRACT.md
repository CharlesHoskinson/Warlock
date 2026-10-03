# Per-layer shader source-over diagnostic V7

Specified before changing this derivative producer. Immutable V6/root V8 remain
unchanged. Explicit causal experiment, not production policy or accepted repair.

Keep all source bytes/premultiplication/order, original member quad positions and
UVs, output scales/extents, transparent clear, highp four nearest texel-center
sampling and every strict full-image comparison. For each covered fragment let
S be normalized premultiplied bilinear source, D the normalized exact prior
RGBA8 prefix. Compute C=clamp(S+D*(1-S.a),0,1), then independently emit
floor(C*255+0.5)/255 for RGBA after EACH layer. Outside the quad preserve D.
This is the unchanged oracle's per-draw nearest rule. GL_BLEND is disabled for
these shader passes; never blend twice or replace with one final quantization.

Each live output generation and extent owns two bounded RGBA8 textures and
separate framebuffer attachments. Copy the complete prior prefix NEAREST/clamp
into a DIFFERENT write attachment, then draw the original source quad sampling
prior prefix at gl_FragCoord pixel centers/exact buffer extent (no second flip).
Only successful passes swap read/write roles. Never sample current attachment.
Every scene/control starts transparent. Generation/extent changes reset and
output teardown retires resources. Two buffers/output; no CPU resize/frame PNG
upload. Exact component widths8/no multisampling, attached texture IDs, nearest
clamp state, sampler units, extent uniforms and disabled GL_BLEND must be
inspected before pass completion. Errors cancel; no incomplete authority.

Observe all existing full prefixes/read pairs after each layer. NEAREST-copy
last RGBA8 prefix to original EGL default target before unchanged named readback,
successful swap and presentation ledger. Diagnostic configuration must name
output/generation/extent/token, ordered source identities/digests, attachments
and actual queried GL state plus compiled shader hashes. Control textures carry
explicit control indices, not native-family provenance. Metadata is not pixels.

New flag requires raster-fixture+causal-readback. Default shader/service unchanged.
All44 original pixel comparisons/18 read pairs/constant controls/source binding/
normal shutdown gates remain strict. No region waiver, tolerance increase or
reference fit. Allocation/copy-pass cost is separate from cadence/physical240Hz.

Primary OpenGL ES3.2 texture/framebuffer/fragment/blend chapters: nearest returns
selected normalized texel; sampling an attached render target causes unsupported
feedback; disabled GL_BLEND removes fixed-function blend. Explicit nearest byte
math is the existing application reference, not an asserted old-driver rounding.
https://registry.khronos.org/OpenGL/specs/es/3.2/es_spec_3.2.pdf

Compiled over/copy program IDs must be positive, distinct integers. Each actual
over draw uses that compiled over program; every prefix and final copy uses
that compiled copy program. Source textures are distinct from both prefix
textures. Copy attachment ownership and nonfeedback are queried before copy
draw. Partial allocation retires all nonzero textures/framebuffers; invalid
generation/extent refuses allocation and failed teardown prevents reuse.
