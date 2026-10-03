# Frozen private PointerLocator v7 review

This is staged **Omarchy Orca compat** plus the unchanged installed public
libatspi backend. It has not run native pointer acceptance and has never been
loaded on the main compositor. Original signed Orca files, accepted v6a and
the first mouse-review candidate/counterexample remain intact.

## Source and contract

- Root PointerLocator contract/helper remain authoritative and copied exactly.
  QueryPointer has `a{sv}dd`, directed no-argument PointerPositionChanged and
  one explicit query per later coordinate change. Unknown is truthful and arms
  only after an authorized error reply is queued.
- New AX_MAPPING_CONTRACT and model require actual unique native/AX singleton
  correspondence, actual AX peer PID and role verification, live process/window
  identity and caller epochs. Multiple native or AX windows refuse ambiguity.
- New CAPABILITY_CONTRACT/model cover the actual constructor-before-test order,
  verified own-name release/reclaim with DO_NOT_QUEUE, zero interception
  policies before probe, quiescence, exceptions, owner churn, and an explicit
  truthful authorized bootstrap query. Unknown arms; AccessDenied/transport/
  epoch failure does not count as recovery.
- `native/plugin-v7.cpp` and `pointer_native.hpp` retain v6a keyboard policy and
  exact ABI hooks. Motion adds the one exported PointerManager::onCursorMoved
  hook, calls original first, and reads actual doubles. Async AX requests are
  capped at 16 queries, 64 registry apps/query, 1500ms deadline, 500ms per call,
  and 32 dispatches/tick. Final AX responses wait for queued session owner
  changes. Bus loss/retirement cancels pointer work. Private accessibility
  socket ownership/canonical location and exact compositor ABI are guarded.
- `mouse-review-v2` changes only actual mouse_review.py in a copied 165-file
  Orca package: public refresh_device, actual active flag, class-owned stale
  timeout/device guards, and explicit enable/disable/toggle intent across
  outages. No adapter assigns private reader fields or replaces command refs.
- Reconnect negotiates on the same fresh device before public modifiers/binding/
  requested full-grab replay and invokes the new public refresh method.

## Planned actual native oracle

`native-fixture/pointer_cases.py` uses a private actual compositor, native
Wayland virtual keyboard/pointer, real Foot bytes, actual accessibility Registry,
real GTK4 peers, actual public Atspi pointer-moved and the real compat reader.
Independent generic protocol callers test authority/notification rules; their
success is never substituted for GTK or reader verification.

1. Actual fresh public Device refuses capability probing during a real captured
   held key without releasing registration. The real paired release keeps
   Foot bytes suppressed; the same fresh device probes after reconciliation.
2. Real compat Orca predates service availability as Legacy with review disabled,
   reconstructs the official Manager backend and same-device capabilities.
3. Actual GTK AX application/frame bus/path are independently observed, never
   supplied to the bridge. Hover mapping is independent of keyboard focus.
4. Fractional logical coordinates at private output scale 1.25; actual same-pixel
   fractional motion; directed one shot, no unsolicited repeat, coalescing,
   owner replacement and truthful unknown-target arming.
5. Real same-PID second native/AX window returns Unknown; closing it restores a
   unique actual mapping. Moved-window origin is recomputed.
6. Actual official pointer-moved carries the real frame; actual reviewer current
   item becomes the real named GTK child and the silent speech observer records
   its utterance. A decorated CSD peer has compact distinct adjacent buttons;
   real toolkit motion/pick and reader AX leaf must agree independently of
   native origin arithmetic. A real popup similarly checks the actual GTK child,
   parent AX frame and negative logical parent-relative coordinate.
7. Public false/true/toggle lifecycle, no item after disable, real quiescent
   retirement/restart, outage-disable cancellation, enabled restart, all 219
   actual command definitions/configuration, and restored real hovered item.

Every native failure must be retained before any source/fixture repair. These
gates are planned, not yet passed. Strict multiwindow refusal is an explicit
compatibility boundary; physical hardware/general keymaps are not claimed.

## Isolation and cleanup

Exact command after root review and an exclusive GUI grant:

```
python3 /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/pointer-v7c/native_probe_pointer.py --execute --output /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/pointer-v7c/native-pointer-attempt-3
```

Fresh attempt directories are exclusive 0700, exact source copies private, and
the command and manifest hash are written before launch. The runtime is a fresh
owned 0700 `/tmp/kbn-*` directory established before private D-Bus. Private Bus
and actual Registry are started explicitly before GTK/reader; their socket must
resolve inside that runtime. No host input, main reader enable, settings or
main plugin load is performed. The current v18 main plugin is a frozen external
reference; the actual dynamic main plugin list is snapshotted/restored.

Normal unload requires true PrepareUnload. EOF is delivered to fixture pipes
first so the native keyboard emits real paired releases. No forced loaded
callback unload occurs. Remaining private descendants are identified by own
UID, exact runtime and PID/start, then terminated only within that scope.

All 14 strengthened restoration gates remain: exact original hidden Files
PID/start/responsive full public/UI state; all frozen actual dependencies;
keyboards/locks; full original client set and states including monitor; plugin
list; focus; cursor; main a11y socket inode/connectivity; reader disabled;
exact catalog bytes/private backups with settle and no historical rewrite;
exact output set; fixture/descendant exit; no config errors. Runtime removal
and process handles are reported separately. No physical hotplug or main
compositor restart is implied.

Production remains a separate later build without private Probe D-Bus and with
exact-instance Lua maintenance. Main reader remains disabled by default.

## Final capability result and early motion gates

An unsupported actual returned capability is refused after restoring this own
registration/Watch, without QueryPointer priming or enabled report. Exact official
libatspi enable_pointer_monitor connects its GDBus handler before returning; the
first and second private real motions before any GObject observer must demonstrate
its actual asynchronous QueryPointer rearming through read-only pending count.
This is separate from later actual accessible pointer-moved and mouse navigation.

Fresh v7b changes only fixture oracle/cleanup. RETRY_CONTRACT.md and exact
primary/HyprCtl.cpp retain the IPC precision diagnosis. Original pointer-v7
attempt-1 remains failed; product/SO unchanged. Integer early cursor targets and
consumed0→officialpump1 precede unchanged fractional protocol/reader gates.

V7c preserves both failures and moves the actual native pointer to A AFTER
focus dispatch B, validating actual activewindow B and IPC cursor A before
QueryPointer. Exact primary ConfigActions focus warp source is retained.
The product, bridge SO, reader package and capability adapter are unchanged.
