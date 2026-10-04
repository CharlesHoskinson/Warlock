# Full-surface coordinate candidate

Three owning translation units implement the464 contract for committed nonzero
root geometry. SurfacePass maps the complete logical surface quad, including
padding, with geometry-derived projection scale and origin translation; child
surface offsets share that mapping. Geometry-owned quads avoid the old oversized
squish that would truncate shadows. ElementRenderer keeps viewport source UVs and
bypasses size-ratio cropping for mapped root geometry. ViewHitTester uses the
inverse current render transform before native surface/input-region admission and
for explicit surface-local lookup. Zero-origin and X11 branches remain exact.

This is a candidate, not accepted production behavior. Popup-specific role
translation, damage/blur/opaque extents, viewport/transform and animation roles
need native qualification; guarded positive extents are assumed protocol-valid,
not a replacement hostile numeric decoder. Complete target/output/ACK mapping
lifetime and strict existing policy are unchanged. Nonzero geometry operations
remain refused by policy. No new installation or header ABI change.
