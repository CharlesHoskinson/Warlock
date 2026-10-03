# Controlled owned-buffer diagnostic V5

This is a fresh diagnostic derivative of immutable readback V4. No native
execution or production repair is accepted. The final scene shader, source
textures, geometry, filtering, blend equation, draw order and complete-scene
reference remain identical. Diagnostic mode never emits native ready/endpoint.

## Prefix observations

On the first held sample for each token/output generation/progress, observe the
entire RGBA8 buffer after each real ordered member draw. Observations are named
only after the final immutable frame has a ledger sequence. Every record binds
the complete scene token, ordered identity/digest/rectangle vector, output name
and generation, progress, logical extents, buffer size and exact prefix count.
It includes the exact prefix vector separately; a matching full-frame swap and
accepted presentation is a collector prerequisite to attributing it to the
held sample. A prefix itself was never committed and has no presentation proof.
The producer checks the final ledger frame against the actual drawn member
vector, captured token/generation and buffer extents before publishing prefixes.

Prefix readback does not draw, upload, alter the family, authorize callbacks or
change a texture. Pack alignment is restored. Failed reads/publications abort
the diagnostic producer; they cannot silently become missing successful data.
Full RGBA reference comparison uses the independently rendered prefix, with
the original declared zero/one quantization bounds and no region exclusions.

## Independent controls

Before the first scene sample on each output generation, draw predetermined
spatially constant premultiplied textures through the same shader, quad setup,
RGBA8 attachment, linear/clamp sampler and ONE/ONE_MINUS_SRC_ALPHA blend. These
observations separate gradients from blend/attachment behavior; they have no
snapshot/member provenance. Controls have their own immutable identifiers and
explicit source bytes/order. They are uploaded once for the diagnostic actor,
not per animation frame. The scene begins afterward with a complete transparent
clear and explicit scene shader/attributes/bindings. No control is swapped.

For each prefix/control, collect RGBA/UNSIGNED_BYTE and the implementation's
queried read format/type from the same unchanged buffer. Only RGBA or BGRA with
UNSIGNED_BYTE is supported by this diagnostic; any other pair refuses. Convert
BGRA by exact R/B permutation only. Record both read errors and both raw RGBA
digests, compare the entire images, and restore pack alignment after each read.
The implementation-supported pair is diagnostic evidence, not a permission to
change acceptance color math or relax pixels.

## Collection and lifetime

Files are exclusive private PNGs in an already owned 0700 directory, bounded
by existing buffer limits and an aggregate per-sample bound. Paths, full raw
digests, row orientation and metadata are independently checked by the root
collector. Diagnostic files cannot assert readiness, source upload or native
authority. Exact source freeze, matching successful swap/presentation and
normal producer shutdown remain mandatory. An image comparison failure may
retain subsequent independent diagnostic observations, but protocol/source/
identity/cleanup failures terminate collection. No diagnostic cadence claim.
