# Draw-time surface and output facts

V20 captures stable weak-resource surface tokens, draw boxes, effective alpha and
surface-local effective input rectangles at native draw dispatch. Each frame
captures output logical geometry, scale, transform and a core-owned configuration
generation at frame start. These are diagnostic facts, not an admitted scene.

The ordinary private native regression passed 63 checks. The continuous full-redraw
diagnostic passed 84 checks, including retained geometry remaining unchanged after
an actual resize, fresh geometry becoming `[560,80,180,140]` with the same surface
token, output configuration capture, and earlier unmap/remap identity checks. Both
campaigns passed cleanup. This redraw configuration has no production performance
or power qualification. The selected final core build uses a global configuration
serial; the earlier per-slot build is preserved but is not the accepted pair.

The compiled Elm decoder passed 28 checks, including 18 actual native packets.
Quint executed six explicitly selected named cases and 1,000 invariant samples of
40 steps. An unsafe query that substitutes live geometry for retained geometry
fails the retained-history oracle. This abstract model does not establish native
refinement or real output-change behavior.

Draw boxes use output pixels before output transform; input rectangles use surface
local coordinates. Viewport, buffer generation, paint clips, opaque masks and
native seat routing still need qualification. The core configuration generation
and outer plugin output generation are independent counter namespaces. Comparing
their values does not prove scene coherence. Monitor commit is not presentation.
Prototype capacity limits are not approved product or performance budgets.

Evidence and exact source/ABI closure are in `qa/slice-manifest.json`. No entire
requirement, build cycle or release gate is accepted and nothing is installed on
the user's live desktop. Next: strict diagnostic decoding, then an actual input
hole and output-change fixture with pixel, pointer and keyboard receipts.
