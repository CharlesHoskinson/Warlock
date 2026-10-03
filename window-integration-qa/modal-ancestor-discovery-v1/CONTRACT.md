# Modal ancestor press discovery

## Existing failure

Immutable Qt V8 supplies a valid owner button baseline callback, then a mapped same-QApplication WindowModal child and working independent peer. At the same owner button116,400, native hit and pointer owner are null, owner callback is correctly refused, and keyboard focus incorrectly remains the peer. The official Hyprland0.56.2 windowAt filters every ancestor with an XDG modal child when general:modal_parent_blocking is enabled. acceptsInput can remain true. Production v18's listener returns on that filtered null hit before its existing deepest-modal routing. This is a product integration gap; no fixture focus workaround or gate waiver is permitted.

## Press authority

Keep global core hit/hover filtering unchanged. During an ordinary button press only, discover the geometrically top eligible window under the actual native pointer using the exact upstream pinned/floating/tiled stacking, visible workspace/special/fullscreen priority, noFocus/ignored-window and input eligibility. Omit only modal-parent shadow filtering. Never search beneath a competing top ordinary window to find an ancestor. Recover only that winner's live visible same-workspace modal chain. Revalidate native mapped/input authority immediately before consumption.

For a client-body point, require actual windowSurfaceAt input-region acceptance. For a decoration point, require an explicit eligible decoration extent; do not pretend the client region covers it. A non-window pointer surface owns its input and refuses recovery. If pointer owner is an underlying window, it must equal the original filtered core hit; a different pointer owner refuses recovery. Preserve session lock, exclusive layer, click mode, constraint, held-button, seat grab, capture, DnD and active drag guards. Pointer presence never overrides those guards.

Consume the recovered ancestor's down and matching release, raise its existing family, and focus the existing deepest modal using the unchanged parent/history target. Do not deliver the ancestor callback. Valid ordinary peers/children retain core delivery, and modal destruction before release cannot leak a consumed release. No PID/class family inference, no main/native loading, and no changes to the nineteen toolkit oracles.

## Formal boundary

The model distinguishes a top eligible geometric winner from the filtered core winner, pointer-surface ownership, client-region/decoration authority and external input guards. It models the existing target chain independently of geometric discovery. Geometry/stacking adaptation requires source-backed tests and subsequent actual native evidence; passing this finite policy model does not establish native hit-test behavior. Preserve the legacy null-hit counterexample before correcting source.
