# Owned framebuffer attribution (diagnostics only)

This experiment changes neither source decode, geometry, shader, texture filter,
blending, compositor sampling nor the independent complete-image oracle.

The diagnostic-only raster producer may be launched with `--raster-fixture
--readback-dir PRIVATE_DIRECTORY`. It rejects readback on the normal authority
path. The existing directory must be owned by the current user, mode 0700, and
not a symlink. It reports actual EGL config component/buffer/sample sizes, EGL
surface dimensions, GL color component bits and GL implementation read format
and type for each current output before draw. No reported field is pixel proof.

For each held diagnostic scene token/output/progress, exactly one framebuffer
read is issued after the ordered GPU draw, before its swap, with
`glReadPixels(0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,...)`. GL_PACK_ALIGNMENT
is saved/restored. GL errors fail closed. Rows are vertically reversed exactly
once into top-left order. PNG channels retain raw premultiplied RGBA8 bytes,
without unpremultiplication, alpha flattening, color conversion or a mask.
The metadata names the immutable submitted local frame sequence, token, exact
identity/digest/member rectangles, output generation and buffer extent. It
records all actual GL/EGL fields and the raw top-left byte SHA256.

The PNG uses an exclusive 0600 new file under an open verified directory FD;
existing evidence cannot be overwritten. Output extent is bounded to 256MiB.
Each read is explicitly an observation of the producer framebuffer before
compositor composition. It cannot authorize readiness, native effects, endpoint
handover or timing/cadence acceptance. Successful swap/presentation retains its
existing independent ledger semantics. glReadPixels may stall the GPU; this
diagnostic run establishes no performance claim.

Attribution compares this raw premultiplied output against an independently
specified transparent-background producer reference, and separately compares
the composed screenshot with the unchanged black-background full-image oracle.
The same seven screenshot pixels are retained; no tolerance or region changes
are authorized. A producer readback match/failure locates a boundary, not a
repair.

Primary API: Khronos GLES2 glReadPixels defines lowest-left origin, RGBA
UNSIGNED_BYTE availability and pack alignment; eglGetConfigAttrib/eglQuerySurface
report actual selected configuration/surface values. Readback conversion to
UNSIGNED_BYTE itself is a distinct observable conversion boundary.
