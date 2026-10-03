# Frozen quantized source-over V7 proposal

This derivative is an explicit offline-reviewed diagnostic. Root retains the
exclusive native slot. No native or GPU acceptance is supplied by this packet.

Exact launch, only under a fresh root private native grant:

```
hypr-motion-renderer-staged --raster-fixture --causal-readback-dir PRIVATE_EXISTING_0700_DIRECTORY --quantized-over-experiment
```

Every source, quad, UV, scale, extent, seed and readback comparison is unchanged.
The selected highp shader samples four nearest texel centers, explicitly computes
premultiplied source-over, and rounds to nearest RGBA8 after each layer. Two
separate textures/framebuffers per current output generation carry the prefix.
Each layer copies the previous full prefix, writes the original quad, then swaps
roles only after successful actual state inspection and draw. The final exact
nearest prefix copy targets the original EGL surface before the unchanged swap
and presentation ledger. Default fixed-function rendering remains unchanged.

`quantizedOverExperiment` binds exact raw over/copy fragment SHA256 digests and
positive distinct compiled `overProgram`/`copyProgram` IDs. `samplingConfigured`
binds each immutable family upload and each 1x1 control to actual nearest/clamp
state and queried source extent. `quantizedOverFrameConfigured` binds the token,
sequence, output, generation, buffer extent and ordered immutable member vector
to actual pass/copy records. Every actual over pass must use `overProgram`, and
every prefix/final copy must use `copyProgram`. Source/read/write texture IDs
must differ; queried prefix copy attachments must belong to the exact output
and differ from sampled prefix. Every over pass requires RGBA8, no multisampling,
disabled blend, correct texture bindings/units/uniforms and no GL errors.

Independent `verify_quantized_over.verify(events, readback, source_material,
shader_digests(frozen_header_text))` rejects stale, partial, reordered, aliased,
unknown-program or differently configured observations. It supplies no pixel,
native readiness or endpoint authority. Constant control groups are separate
from family provenance; later frames retain all family passes without redoing
the once-per-generation controls.

Root must independently retain all44 full-image comparisons, all18 complete
native/RGBA read-pair equalities, controls/source binding and each observation's
own successful swap/accepted presentation. Tolerance remains1. Frozen V6/V8
failures remain failures (scaled p0:10 pixels maximum2; p.35:1 pixel maximum2).
No region waiver, relaxed comparison, fitted reference, cadence or physical
240Hz claim follows from this experiment.

Normal exit zero, full event EOF/drain, immutable source/header/binary/mode
closure, private session/parent/process/cleanup and all dynamic main read-only
preservation gates remain mandatory. Generation/extent changes reset transparent
prefixes; partial allocation retires every nonzero resource and failed cleanup
prevents reuse. Native campaign and later continuous reversal/recovery remain
pending root review/grant.
