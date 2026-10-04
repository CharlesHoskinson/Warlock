# Independent measured Qt translation source review

Root inspected the actual308 producer surfaceTransform and309 geometry consumer. Producer uses the current QWindow private Wayland handle, actual mapFromWlSurface(0,0), clientSideMargins and current wl_surface ID; unavailable handles/resources emit unavailable. Consumer requires an explicit measurement matching the exact current resource, finite bounded coordinates, nonnegative bounded margins and method/margin agreement, then inverts surface-to-window translation before applying independent native/xdg origins. Marker and QAction whole rectangles retain window/surface/global coordinates. No DPR multiplication, default zero, globalQt desktop authority or effect-grant bypass was found.

Actual journal parsing permits bounded flat extra producer fields; geometry validation subsequently checks exact transform fields. Existing current identity/native/protocol snapshot requirements remain in scene.py. Full input locals require313 adoption and an actual native round trip; this review does not qualify those or any pixels.

Fixture compilation links the actual private API. The16-case method harness substitutes a margin supplier and does not instantiate a display/QWaylandWindow;309 controls use synthetic measured inputs. Toolkit/live measurement correspondence, configure/commit/pixels/full input intervals, hidden/modal/family/reconnect cases and known297 shell blocker remain open. Official Qt source body is versioned upstream reference, not proof of distribution build-source identity.

The protected verifier independently binds all actual held own/external rows and selected reports for both components. No new native/full acceptance is asserted.
