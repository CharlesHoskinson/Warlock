# Geometry transport audit

This is a design and source audit, not an implementation or model approval.
No Elm, adapter, native authority, or frozen parent source changed for this note.

## Actual baseline and transport owner

`elm-menu-parent-input-v13/qa/native.py` is a native-test wrapper, not a new Elm
application. Its `ROOT` is `elm-menu-native-pair-v8`; its `CORE` is
`elm-buffer-authority-pair-v8`. V13's frozen slice manifest binds the V8 menu
manifest and its passed native report with 68 checks. The actual integration
sources are V8 `src/`, `assets/`, `native/`, and `adapter/`.

The native runner imports V8 `adapter/effect_endpoint.py.Endpoint`.
`adapter/endpoint.py.Endpoint` is the intentionally read-only base: its strict
hello expects effects/minimizedState false. Extending that base handshake alone
will not enable the actual effects route. Its authenticated connection, process
start identity, socket/peer/path checks, canonical counters, and exact-field
validators must remain the foundation.

The effect endpoint's current hello requires precisely native protocol 3,
effectProtocol 1, taskbarProjectionProtocol 1, effectInvalidationProtocol 1,
operations `[minimize, restore, activate]`, observe/effects/minimizedState true,
and canonicalScene false. Old clients reject extra capability fields or a changed
operation list. Geometry facts and operations cannot be appended to this wire in
place and called backward compatible.

## Existing fact and operation path

1. V8 authority `native/authority.cpp` emits scene facts including finite goal
   geometry and integer internal `fullscreenMode`. Facts serialization contributes
   to its dependency revision. This is action context, not canonical scene,
   input, or paint admission.
2. `effect_endpoint.py.scene_facts` checks those records; it currently accepts any
   integer fullscreenMode, so a new typed mode must reject unknown enum values.
   Snapshot facts are separately bracketed by `taskbar_projection.coherent_scene`.
3. `taskbar_projection.py` deliberately drops geometry/fullscreenMode. It emits
   rows containing incarnation, application, label, minimized, owner, available.
   Available is workspace/hidden-state eligibility; it is not a geometry
   capability or proof of supported window protocol.
4. The real V8 `adapter/daemon.py` publishes `action-projection` and validates
   effectProtocol 1 before calling the endpoint. Events coalesce only a dirty
   refresh notice; they do not authorize an effect or provide replacement facts.
5. Elm `Shell.elm:81` admits only the expected request/binding/context.
   `Effects.apply` decodes `ActionProjection`, checks scene/context revision,
   rejects decreasing revisions and contradictory same-revision facts.
6. `NativeProvider.fromShell` requires admitted Ready facts and an explicit
   registered output/provider scope. It resolves `ActionProjection.rootOf`
   and advertises only Restore and Minimize. Output identity is distinct from
   context output generation.
7. `MenuBridge.menuEvent` obtains the real Shell-generated native command,
   freezes it into `ReceiptRouter.register`, then closes the menu before send.
   It rejects externally supplied Menu.Open and Menu.ReceiveFor.

Legacy wire `restore` and `Effects.Restore` mean **unminimize**. They must retain
that meaning even when the saved native mode is Maximized or Fullscreen.
`Menu.Maximize` already exists in the generic menu vocabulary, but the native
bridge maps only Menu.Minimize and Menu.Restore. The provider grammar accepting a
generic action is not native implementation support.
The existing visible `Close` control dismisses the popup; it is not a native
window Close capability. Preserve that distinction when adding standard rows.

## Proposed negotiated version branch

One concrete compatibility option is to retain protocolVersion 3 and add an
explicit extended hello request branch:

```json
{"protocolVersion":3,"kind":"hello","versions":{"effect":[2,1],"taskbarProjection":[2,1],"geometryFacts":[1]}}
```

Keep the original two-field hello request and original attached capability object
unchanged for legacy clients. Accept only exact, bounded, unique, known version
lists in the extended branch. Select a consistent tuple: effect 2 / projection 2 /
geometry facts 1, or the unchanged legacy tuple when explicitly offered. Refuse
unsupported mandatory versions; never infer compatibility from missing fields.
This proposal requires a new native and adapter implementation, not edits to
frozen V8. Alternatively, a fully separate native protocol version is valid;
the compatibility branch must be explicit either way.

For the geometry tuple, advertise `geometryFactsProtocol:1` plus effectProtocol
2 and taskbarProjectionProtocol 2 in its strict capability object. Support only
implemented operation names: existing minimize/restore/activate and new
`maximize` / `restore-geometry`. Do not advertise Move, Size, Close, or
ExitFullscreen from the existence of generic UI constructors. The adapter's
projection envelope should explicitly carry `projectionProtocol:2`; legacy
envelopes and strict six-field rows stay unchanged.

The effect-2 command retains the exact existing five-field envelope and intent
identity/context layout. Only the negotiated version and closed operation enum
extend. Maximize/restore-geometry need no position or size arguments from the AI.
Geometry restoration consumes the authority's saved ordinary placement; the
client must not supply or fabricate it.

## Typed geometry facts

For each projection-2 row retain all six legacy fields and add:

| Field | Type and meaning |
| --- | --- |
| nativeMode | Closed `ordinary`, `maximized`, `fullscreen`; authoritative internal mode |
| fixedSize | Native boolean size constraint, not an inference from current dimensions |
| geometryEligible | Native boolean current semantic target eligibility; capability support remains separate |
| ordinaryPlacementKnown | Native boolean for a trusted restorable ordinary placement belonging to this incarnation |
| capabilities | Exact booleans `restoreMinimized`, `restoreGeometry`, `move`, `size`, `minimize`, `maximize`, `close`, `exitFullscreen`, `activate` |

Unknown mode values, missing facts, unsupported protocol/version pairs, malformed
booleans, or contradictory ownership facts must reject the whole projection and
preserve the previous admitted state. Never default missing geometry facts to
Ordinary or native support to true. Ordinary placement availability is a state
condition, distinct from implemented RestoreGeometry support: an externally
maximized window can lack an owned restore record. The pure policy will need that
additional availability guard before actual integration.

Native facts fingerprinting, the before/after bracket, and
`ActionProjection.sameState` must include all mode, constraint, eligibility,
placement-availability, and capability fields. Otherwise a same-revision
geometry/capability change could be admitted or leave a stale enabled row.
Preserve decimal UInt64 identities throughout; never convert them to Elm/JS Int.

## Elm insertion points and invariants

* `ActionProjection.Window/windowDecoder/sameState`: strict versioned row types
  and typed geometry facts. Preserve ownership-cycle, root, family-minimized,
  duplicate-identity, focus, and text bounds. Extend separate versioned decoders
  rather than accepting arbitrary optional fields in legacy rows.
* `Effects.Operation/operationDecoder/operationName` and `begin`: distinct
  Maximize/RestoreGeometry, with native-mode, minimized, fixed-size, trusted
  restore, and current eligibility checks before allocating request/generation.
  Explicit restore first: minimized Maximize stays disabled. Fullscreen Restore
  must not implicitly exit fullscreen. Receipts never update observed geometry.
* `Shell`: retain negotiated effect/projection versions from admitted hello;
  stamp captures binding plus full observed context. Carry exact selected version
  on commands and admit only the corresponding projection decoder.
* `NativeProvider`: apply `WindowGeometry` to the same admitted **root** facts;
  supported but state-ineligible rows remain visible disabled. Preserve disabled
  legacy Restore when only unminimize is supported. Introduce distinct
  RestoreGeometry provider/Menu action; keep Menu.Restore as legacy unminimize.
* `Provider`: explicit versioned envelope/action grammar. Generic Maximize is
  currently legal under provider 1, but new RestoreGeometry and negotiated native
  protocol metadata need a deliberate new branch. Include capability version in
  the frozen provider authority, not only presentation labels.
* `MenuBridge.operation/providerMatches/reconcileWithShell`: map new actions to
  typed native operations, enforce fresh full root/context/capabilities, and
  invalidate on actual mode/eligibility changes. Focus-only revision refresh is
  allowed only when the exact action/enabled table remains unchanged.
* `NativeOutcome.valid`, `ReceiptRouter.command/receipt/key/register`,
  `Effects.intentDecoder`, and Shell receipt decoding: extend together. Bind
  effect version into the registry key alongside the original complete native
  binding and intent. A receipt with the right local ID but wrong version,
  operation, context, generation, incarnation, or native binding is ignored.

`TaskbarShell.native` currently shape-gates the outcome, routes the menu registry
first, then lets Shell check its own singleton transaction. Preserve that order:
a late operation-A receipt must reach A's registry entry even after B replaces
the Shell transaction or the current binding. Unknown retains the original
mapping; a definitive exact receipt releases it once. Revision/output hints on
the receipt are not a fresh projection.

`MenuBridge.blockedFor/guardedAct` canonicalize family roots and guard every
ordinary taskbar route too. The Menu ledger guards Pending/Unknown by stable
native window identity, including fresh revisions/frontends. Do not let a new
geometry button or family coalescing bypass that guard. The native authority
still independently revalidates the exact intended root and current dependency
context; it must not silently retarget a child intent after issuance.

## Regression sources and observable integration views

The actual CPU worker is `src/MenuSurfaceReplay.elm`, compiled by V8
`qa/replay.py` with Main and Popup compatibility gates. It drives production
SurfaceController/Desktop/TaskbarShell/MenuBridge/Shell/Effects and exposes frame,
menu ID/status/selection, shell state/transaction, outgoing requests, registry,
outstanding count, provider/owner scope, and focus effects. Use that worker for
new projection/receipt interleavings, not a JS policy reimplementation.

Preserve V8 `qa/menu.cjs` identities including `disabled Restore cannot allocate
an operation`, `Minimize closes publication before exactly one real full intent`,
`correlated receipt clears ledger without optimistic observation`, `Unknown
survives reflow without replaying a native operation`, `wrong full receipt binding
cannot reconcile after reflow`, and `original bound receipt still resolves
exactly once after reflow`. Preserve non-1 owner scope and stale lease/publication
tests. Add version mismatch, legacy/new mixed-capability, root/child eligibility,
same-revision geometry contradiction, delayed A after B, unsupported action, and
Unknown geometry/taskbar retry cases.

For native integration, V13 joins `surface-inspection` with DOM reports and real
popup configure rectangles. `Inspection.elm` exposes native menu incarnation,
transaction status, registry/outstanding, and row action IDs. The runner reads
actual `frontend-request` and backend outcome/projection logs; its original
identities include `singleCorrelatedIntentWhileBrokerStopped`,
`pendingCommandClosesActualNativePopupBeforeSend`,
`minimizeHasOneCorrelatedIntentAndReceipt`,
`restoreHasOneCorrelatedIntentAndReceipt`, and
`menuReflowResizedAuthorityRetiresProviderWithoutEffect`.
Retain these and their original deadlines. Geometry-native state, actual client
configure/ACK/buffers, and pixels require new evidence; generic constructor or
successful pure-policy tests cannot qualify them.
