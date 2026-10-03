# V8: bounded async pointer notification owner fence

The frozen v7d attempt4 remains a real stale-registration failure: independent
wire evidence proves a new notification after loss/reclaim/reclaim reply and no
new query. This fresh candidate repairs native control integration. Root's pure
PointerLocator State, signed libatspi/Orca prefix, MouseReviewer compat v2,
capability adapter, and all v6a keyboard policy are unchanged.

## Actual source and bounds

- `native/plugin-v8.cpp`: relevant monitor NameOwnerChanged rotates old/new
  pointer principal epochs, including alias transitions. Keyboard definitions
  and balanced captured releases retain their existing semantics.
- `native/pointer_native-v8.hpp`: motion records actual changed position into a
  deferred note; it performs no D-Bus RPC or signal emission. Bounded control
  ticks issue SAME-CONNECTION asynchronous GetNameOwner, ordinary dispatch
  handles preceding owner packets, and final drained-state validation checks
  captured sender/name/principal epoch and daemon owner snapshot.
- `native/PointerNotificationFence.hpp`: 512 notes, 16 concurrent calls, 500ms
  call timeout and 1500ms total note deadline. New query capacity includes
  existing arms and accepted AX queries; refusal preserves all prior notes.
  Deadline cancellation continues during saturated control queues. No late
  reply emits after bus loss or irreversible retirement.
- No name ownership lease is claimed: authorization linearizes at the daemon
  reply snapshot plus local epoch revalidation. A future external change after
  that snapshot can leave a valid packet in flight. Pre-snapshot obsolete owner
  history, including same-unique reclaim, cannot authorize an old note.

## Evidence before native run

Contract/model were written and passed before implementation: 15 named cases,
2,000 randomized traces ×100 steps, seed20460901. Exact extracted staged native
functions pass 15 deterministic scenarios with a controlled transport adapter.
Those SAME functions additionally pass a real PRIVATE dbus-daemon transport
trial: valid directed notification plus20 actual loss/reclaim/fresh-rearm cycles.
This is transport evidence, not a compositor/GTK/official-reader acceptance.
All43 existing Python source/preservation/cleanup/compat gates pass. Exact ABI
shared object built with Werror. Primary daemon/broker/libdbus sources and
provenance are pinned under `owner-lifecycle-v2/primary`.

## Frozen private native oracle

Keep the existing exact baseline, causal wire/client telemetry and all original
fractional, GTK CSD/popup, real AX leaf, official libatspi pointer callback,
Omarchy Orca compat navigation/intent/restart gates. Wait for actual bridge
Deferred/Fences counters to reach0 before checking old registration baseline;
reader's independent automatic pending arm may remain. Add8 actual same-unique
owner loss/reclaim cycles, each exact previous history unchanged followed by a
fresh explicit query that rearms once; add4 alias owner loss/reclaim cycles
while the main registration survives. Independent dbus-monitor now includes
actual GetNameOwner calls. Timing sleep is not the repair oracle.

The fixture captures current main plugin/client/output/catalog/a11y/focus/cursor
and hidden Files exact PID/start/full public+UI hashes immediately before run.
It does not pin a historical Files UI hash; current Files deployed15 state is
preserved. All14 preservation gates remain, exact private-runtime/AX isolation,
paired EOF release, scenario-owned cleanup, true PrepareUnload then normal API
unload with Bus/AX/Foot alive, followed by all private infra teardown.

No main plugin load, reader enable, autostart/config change or physical input.
All previous failed packets and attempts remain intact. Native acceptance remains
pending the parent's source review and exclusive GUI grant.
