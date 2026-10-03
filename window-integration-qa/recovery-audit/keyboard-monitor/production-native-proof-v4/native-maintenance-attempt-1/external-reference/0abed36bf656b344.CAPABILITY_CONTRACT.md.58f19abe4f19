# Public pointer capability negotiation

The installed libatspi 2.60.6 Manager constructor claims the actual device's
`<app_id>.KeyboardMonitor` name and calls WatchKeyboard before pointer testing.
Its `test_pointer_locator()` accepts AccessDenied as interface availability;
UnknownToplevel permanently marks that device unsupported. The service must
continue returning truthful UnknownToplevel for authorized unknown targets.

A private process adapter may negotiate a **fresh actual device** as follows:

1. A wrapped public AXDeviceManager.activate records a new actual device only
   when the manager had no device before the factory call. The adapter never
   infers freshness from an owned name.
2. The device must still be the public AX manager's current object, have the
   actual Manager GType, and expose its real readable session-bus property.
   That connection's unique name must own the device's public app_id plus
   `.KeyboardMonitor` registration. No third-party registration is released.
3. Before release, require exact compositor read-only quiescence: no captured
   held route and no surviving virtual lock correction. A held/dirty/unknown
   result refuses negotiation without changing name ownership or policies.
4. Release that exact registration after factory construction. Call the
   original public set_capabilities on the same fresh object while unregistered.
   Reclaim with DO_NOT_QUEUE, require primary/already-owner response, verify
   ownership, then explicitly WatchKeyboard. If the returned capability mask lacks
   POINTER_MONITOR, refuse pointer recovery without querying or reporting enabled.
   Only a successful result may issue one authorized public
   QueryPointer. The earlier AccessDenied availability test did not arm a
   notification, and stock enable_pointer_monitor only connects its handler.
   This initial query bootstraps the first real motion; its truthful authorized
   UnknownToplevel is accepted because it arms by the pointer contract. Other
   errors or a replaced owner refuse replay. No fake initial event is emitted.
   Restore the registration even
   if the capability method raises, and propagate the failure.
5. A fresh device has no previously requested selected/full policies. The
   reconnect adapter must perform negotiation before rebuilding public binding
   definitions and requested full grab. Existing pointer-capable devices do
   not release registration again. Retire the fresh marker after negotiation.
6. Capture can occur only through later explicitly replayed definitions.
   Epoch changes invalidate fresh markers. A failed/held gate must not silently
   discard routes; no synthetic key releases are permitted.

The private proof uses the bridge's read-only Probe.State only inside its
isolated runtime. Production excludes that interface and must supply an exact
compositor-instance Lua state callback. This stage provides no main owner or
production reader integration. Actual native same-device ordering and held
refusal remain acceptance gates; controlled adapter tests are not that proof.

The original enable_pointer_monitor connects its official GDBus pointer callback
before set_capabilities returns. Priming occurs after that return. Even before
MouseReviewer connects its GObject handler, the official callback performs its
real asynchronous QueryPointer, which rearms a later motion. Native evidence
must cover this timing; the public reader callback truncates doubles to gint,
so fractional protocol proof does not imply fractional reader coordinates.
