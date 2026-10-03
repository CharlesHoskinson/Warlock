# Qt frame telemetry boundary

This module is an offline prototype. It does not authorize native operations or change the route. Each probe attaches to exactly one QQuickWindow and snapshots its own bound identity/token/geometry/digest/output/progress fields at `beforeSynchronizing`, with Qt blocking the GUI thread during scene graph synchronization. A monotonic process clock and window generation tag accompany the snapshot.

`frameSwapped` records the captured synchronized fields, never a later GUI read of the animated rectangle. Records are bounded to512. Window replacement retires the generation so an old window's queued frame cannot be attributed to the new one. Each synchronization consumes a new sequence even if a prior frame never swaps; duplicate swaps cannot duplicate a record. Phase changes between synchronization and swap do not rewrite history. Observations remain associated with the original token and must pass coordinator epoch/identity validation before use.

Qt's `frameSwapped` means a frame was queued for presentation. It does not prove compositor presentation, output scanout, the content of a rendered texture, or cross-output seam timing. `digest` and `imageReady` are synchronized input metadata, not independent pixel observations. This telemetry can measure animation cadence and metadata pause on actual Qt render frames. It must not be passed to the route's native-ready authority as proof of displayed pixels. Wayland presentation feedback and the gold/red pixel oracle remain separate integration gates.

The item accepts no focus/input, adds no painted content, has no native operation API, and uses only public Qt Quick/QML APIs. It does not modify the reader accessibility module or production QML. Native tests require a separate coordinated GUI slot.
