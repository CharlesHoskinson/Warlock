# Native PointerLocator v7 design before implementation

The reviewed root PointerLocator contract/helper are authoritative and remain unchanged. v6a sources and its accepted 35/14 attempt remain frozen.

Fresh queries resolve the actual current logical pointer and hovered client independently of keyboard focus. Native hit testing accounts for popup surfaces and refuses lock, unknown layer and IME targets. Coordinates are relative to the validated parent client surface origin; popup/subsurface offsets do not become fabricated accessibility toplevels. The actual double coordinates remain fractional and may be negative.

The bridge has no GTK Wayland D-Bus window-property protocol in this exact compositor ABI. It therefore obtains metadata from the actual separate accessibility bus: Registry.GetChildren yields application references; the accessibility bus daemon verifies the unique application's Unix PID; the real application Accessible.GetChildren must yield exactly one toplevel, and GetRole must confirm an actual window/frame/dialog. The hovered native PID must also have exactly one mapped native toplevel. This is a guarded unique correspondence; any multiple-window case returns UnknownToplevel rather than choosing an active sibling. No supplied PID/path is accepted from a test fixture or guessed from a title.

Accessibility queries are asynchronous, with bounded requests/deadlines and per-tick dispatch. The final method reply revalidates the native hovered identity, current coordinates and requesting registration epoch. A missing, disconnected, stale or ambiguous peer yields authorized UnknownToplevel and arms one later notification. Metadata is not persisted or inferred from a cached process name. The private fixture starts its own real accessibility registry on its own accessibility bus to avoid the retained v6 private registry-activation warnings.

The native motion hook is the single exact exported `_ZN7Pointer15CPointerManager13onCursorMovedEv`. It calls the original first, then supplies actual double pointer coordinates to the reviewed pure State helper. The existing mouse.move signal misses changes within the same floored pixel; polling alone misses a move away and back. The hook observes coordinate changes without cancelling input or modifying focus. Queries execute later through bounded control-plane dispatch and resolve fresh hit state.

Root confirmed the official Device constructor claims its registration and watches keyboard before pointer capability testing. A fresh process-only public capability adapter must release its own exact registration **after construction**, call the actual public set_capabilities(POINTER_MONITOR) while unregistered, then reclaim and explicitly replay Watch/selected/full requests. Stock libatspi accepts AccessDenied as an available interface; returning fake desktop metadata is forbidden. Factory creation itself does not set pointer capabilities.

The fresh Omarchy Orca compat package preserves all original signed-prefix files
and changes only the copied MouseReviewer implementation. Its public
refresh_device method owns lifecycle state, active flag, stale queue retirement,
and explicitly requested intent. Accepted v2 keeps disable/toggle intent mutable
through capability loss. The fresh reconnect adapter invokes that public method
before public key binding and full-grab replay. Actual Atspi backend and pointer
callback remain official. No external private-field assignment is used.

After the same fresh device successfully enables POINTER_MONITOR, its official
GDBus callback is already connected. The adapter reclaims the exact registration,
explicitly watches and calls truthful QueryPointer to prime the first real motion.
Missing pointer capability refuses recovery without priming. A native first-motion
before GObject observer test must prove official callback rearming, independent
of MouseReviewer hookup timing. The reader callback casts protocol doubles to
integers; fractional query evidence is a separate protocol property.

Native gates include fractional/client-relative coordinates, hover independent of keyboard focus, moved windows and popup origins, exact actual accessible bus/object identity, guarded same-PID multiwindow rejection, unknown targets, directed/coalesced one-shot signals, owner churn/disconnect, retirement/restart, actual official pointer-moved and actual Orca mouse navigation. All 14 strengthened main preservation gates remain required. No new GUI run or main load is authorized by this design.
