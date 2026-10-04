# EARS and OpenSpec: geometry/surface/output/input coordinates

When a committed XDG client has a nonzero effective window-geometry origin, the
renderer shall anchor that geometry origin at the authoritative native window
origin. When logical surface coordinates are presented, the renderer shall apply
projection scale and physical output scale once each, independently of buffer
scale. While client content exists outside window geometry, the renderer shall
preserve its surface extent and relative position, subject to ordinary scene
clipping and input-region policy. When physical pointer coordinates are mapped to
a surface, the input adapter shall invert the same admitted render transform.
When output/native/target/configure identities change, the implementation shall
invalidate the transform and require a fresh admitted mapping.

OpenSpec ADDED: XDG coordinate mapping
Given native geometry originN, committed surface geometry originG, projection
scaleQ, monitor originM and output scaleS, surface-local coordinateL maps to
P=(N+(L-G)*Q-M)*S. The inverse isL=G+((P/S)+M-N)/Q. Buffer scale converts buffer
texels to logical surface coordinates before this mapping. Surface padding/shadows
remain outside geometry; cropping to manufacture a matching rectangle is not an
implementation of this contract. Root, subsurface and popup roles require their
own committed role-local translations. Decorations and input regions remain
separate scene facts; painted shadows do not automatically admit pointer events.

The executable Quint abstraction models one axis of exact integer affine mapping,
scales1/2 and aligned integer pointer samples. It does not prove float rounding,
viewport/transform/subsurface/popup protocol integration or native rendering.
Named scenarios explicitly cover X/Y origins, zero preservation, separate output
and buffer scales, inverse pointer mapping, negative monitor origin and uncut
shadow placement. A real compiled implementation and same-tuple native renderer
and pointer qualification remain required.
