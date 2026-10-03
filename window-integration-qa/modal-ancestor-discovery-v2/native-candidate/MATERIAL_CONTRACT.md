# Snapshot material capability and feedback isolation

An export that requires blurred decoration backdrop is unsupported. It must report failure without publishing a PNG or acknowledging image readiness. A direct hyprbars blurred rectangle must be rejected before its GL drawing, matching the existing texture-blur rejection; no partial atlas may be labelled whole/canonical. Opaque captions and native shadows remain supported and subject to exact pixel and normal-frame equality gates.

Atlas rendering blocks client-surface presentation feedback throughout its fake render, restoring the exact previous public block flag on success/failure. An export is not a native output presentation and must not insert client surface feedback into a later real output frame. Cache state and native client/focus/geometry remain unchanged. Core shouldBlur explicitly disables client background blur during snapshot; this raw-client material boundary is disclosed, and translucent blurred-client visual equivalence remains unproven.

Native styled fixture keeps complete fullRGBA controls and all transform/occlusion gates, separately tests explicit blurred-caption rejection with no artifact/native change plus normal rendering restoration. No production load or installed configuration mutation occurs in this stage.
