# Native geometry authority audit

This is an implementation design review, not model approval or native authority
acceptance. It examines the frozen V8 authority/adapter and the V28 direct-XDG
core qualification. No native source or model logic was changed for this audit.

## Established boundary

V28 `core/qa/native-1791098384319585553/report.json` passed 35 direct-XDG checks
and normal cleanup on the selected private core: explicit maximize, duplicate
maximize, explicit unmaximize, duplicate unmaximize, exact noncentered ordinary
placement, correlated server barriers, configure/ACK/buffer records and sampled
interior pixels. Its selected core is
`core/build-1791098117250155855/Hyprland`, SHA-256
`be47f319ca67ec9294d2d6940909fc9b8c31841ff11cdfbd5b235593f27486c2`.
This does not qualify a geometry plugin, menu, fixed-size client, modal family,
competing fullscreen workspace, output change or maximize/minimize composition.

The three core changes preserve the existing minimized input gate, interpret
client maximize requests as desired booleans, emit the distinct Wayland MAX flag
from the fullscreen controller, and stop forcing MAX merely because a surface
maps. Mapping must preserve an already-configured true or false MAX state.
`XDGDecoration.cpp` owns decoration negotiation separately. Clients that do not
negotiate server decorations can still self-decorate; suppressing their CSD by
fabricating maximization is not a valid replacement.

Rebuild the V35 plugin against the exact selected core/headers/policies, retain
its complete dependency inventory, and verify actual mapped core, AQ and plugin
hashes before native acceptance. Preserved exports/public headers are useful
closure evidence, not proof of semantic C++ ABI or operation compatibility.

## Actual insertion points

Paths below are relative to `implementation/elm-buffer-authority-pair-v8/`.

| Source anchor | Existing behavior | Required geometry addition |
| --- | --- | --- |
| `native/authority.cpp:40–47` | Native lifetime/member incarnations; per-peer sessions and one-request journals | Authority-owned bounded placement store and native workspace/workarea compatibility registry, outside `Session` |
| `native/authority.cpp:121–135` (`forget`, `birth`) | Draw identity retirement and fresh member incarnation | Retire the old placement entry before removing its member; never transfer it to a new incarnation |
| `native/authority.cpp:159–194` (`sceneFacts`) | Goal visual geometry and internal fullscreen mode | Versioned geometry facts including client mode, floating/root eligibility and explicit origin availability; do not reinterpret old fields |
| `native/authority.cpp:216–237` (`refreshOutputs`, `refreshFacts`) | Monitor configuration and scene dependency revisions | Include reserved workarea and native ownership compatibility dependencies; geometry capability/origin changes must advance facts revision |
| `native/authority.cpp:274–361` (`performEffect`) | Strict intent/context, exact retry journal, minimize/restore/activate | Closed geometry operations, independent geometry preflight/mutation/readback branch, preserving journal correlation |
| `native/authority.cpp:397–416` | Hello epochs and effect dispatch binding | Explicit versioned negotiated geometry capabilities and operation vocabulary |
| `native/authority.cpp:458–480` | Plugin init, window event subscriptions, unload | Initialize/clear placement and compatibility registries with native lifetime; exact retirement on close/rebirth |
| `adapter/effect_endpoint.py:5–80` | Active effect endpoint subclass; exact caps/facts/effect response checks | Strict new capability/fact/action schema and exact outcome correlation |
| `adapter/taskbar_projection.py:2–20` | Revision-bracketed join discards geometry/mode facts | Preserve validated geometry mode/eligibility/origin fields in a newly versioned projection |
| `adapter/daemon.py:35–64` | Effect protocol gate, one owned allocator stream, coherent projection | Negotiate the same version and forward only admitted closed geometry commands |

`adapter/endpoint.py` is the transport/read-only base. Its read-only handshake
expects effects unavailable and cannot accept the V8 effect handshake itself.
The actual daemon imports `effect_endpoint.Endpoint`. Updating the base alone
would leave the active handshake, fact decoder and operation allowlist broken.

## Wire and context contract

Do not silently append actions to an old exact handshake. Choose one explicit
versioned geometry capability/effect/projection contract and update native,
adapter and Elm decoders together. Preserve legacy `restore` as unminimize and
focus; a separate closed `restore-geometry` operation removes maximization.
Only advertise operations whose exact authority path and eligibility exist.

Add truthful observed internal/client modes and finite logical/visual geometry,
plus eligibility/origin availability with stable reason codes. Current facts
contain only internal mode and visual GOAL geometry: they do not prove ACK,
client buffer dimensions or presentation. Positive dimensions, finite endpoints,
closed mode enum and exact allowed fields must be validated by the adapter;
current `effect_endpoint.py` accepts any integer `fullscreenMode` and permits
nonpositive finite geometry dimensions. New geometry fields need stricter bounds.

The effect context remains native lifetime, frontend epoch, output dependency
generation and facts revision. Neither frontend epoch nor transport peer session
is a placement lifetime. `refreshOutputs()` currently omits monitor reserved
areas and workspace identity generations. A same-ID replacement workspace or
changed reserved workarea must invalidate compatibility even when monitor size,
position, scale and transform stay equal. Assign nonzero native workspace
ownership generations and include the relevant workarea in the owning revision;
never fabricate a generation from a label or caller integer.

The existing endpoint starts one three-second transport deadline per `request`.
Keep that original deadline across connect/send/read/validation and do not reset
it for geometry retries or async completion. The inherited implementation is
not a complete deadline oracle: connect/send use a fixed two-second socket
timeout, EOF breaks before the receive deadline check, and successful parsing
has no final deadline check. V35 must apply remaining-time budgets and reject
completion after the original deadline; it must not claim this stronger behavior
from the inherited source alone. Native effects run synchronously
without event-loop pumping; no deadline field currently exists in their wire
intent. Facts/context freshness is not a user-approval timeout. Do not claim an
unimplemented native expiration check. If asynchronous completion is added, it
requires its own explicit lifecycle contract and original correlated receipt.

## Placement lifetime and operation semantics

Reuse the reviewed V16 `candidate/PlacementPolicy.hpp` as a bounded private store
(256 entries), not as a liveness or authorization registry. Its key is native
`lifetime/incarnation`; scope is workspace identity/generation and output
identity/generation; it records both logical and visual original boxes.

- Capture an ordinary eligible origin before the first MAX mutation. Confirm
  exact live member identity, valid target/layout ownership and compatible scope.
  Capacity or invalid origin refuses before native mutation.
- An existing record remains immutable. `Capture::Duplicate` alone proves no
  scope compatibility: follow it with an exact compatible `read` before mutation.
- Records survive supported minimize/unminimize and frontend hello, adapter
  disconnect/reconnect and peer session replacement. `hello` resets that peer's
  effect journal, not the native window's original placement.
- Retirement/rebirth clears exactly the old identity. Plugin unload clears all
  records. Weak-member pruning must also retire abandoned entries.
- Unknown/partial effects retain their origin and block competing routes; never
  erase the evidence or recapture the maximized rectangle as an ordinary origin.
- After proven geometry restoration, retire the completed original so a later
  ordinary move/resize and new maximize captures the new placement. Explicitly
  invalidate external incompatible transitions rather than silently reuse an
  obsolete origin. Externally maximized windows without a known original have
  unavailable RestoreGeometry in this first scope.

Native monitor ID zero is valid. The owning monitor ID type is signed; reject
negative sentinels before converting to the helper's unsigned output identity.
Rounded logical target boxes and visual client boxes differ because of reserved
decoration geometry. Capture both, and compare each with its corresponding native
readback rather than applying the visual box as layout authority.

MAX must explicitly request internal/client MAX, preserving the original.
RestoreGeometry must explicitly request NONE/NONE, then verify the configured
floating algorithm restores the saved box. The default algorithm already keeps
`lastBox` (`DefaultFloatingAlgorithm.cpp:250–266`); avoid overwriting correct
layout state. If a reviewed correction is necessary, use the owning layout
`setTargetGeom` path so its private history updates. A direct target position
setter alone leaves layout history stale. These setters return void or can
silently decline; their calls cannot constitute a committed result.

## First native eligibility and side-effect guard

Begin with a mapped, ordinary, resizable Wayland floating canonical root and a
singleton family on a visible nonspecial workspace. Reject a child incarnation
even if `nativeFamily(child)` finds its root; that legacy function intentionally
accepts family members for minimize/restore, whereas geometry is root-only.
Refuse X11, grouped/tiled/modal families, pinned windows, true fullscreen,
internal/client disagreement, hidden/minimized targets, active move/resize,
session lock, exclusive layers and every seat grab in this first geometry scope.
Those are deferred product capabilities, not permanent acceptance exceptions.

Do not reuse the legacy `!minimize` path: it predicts restore focus, unminimizes
and focuses/raises a family. Geometry needs its own branch before that code.
Initially preserve actual focus and keyboard recipient. If geometry on an
inactive root must activate it, qualify that separately with the modal recipient
policy and native keyboard readback; do not silently inherit Activate semantics.

Enumerate every workspace peer with internal or client fullscreen state before
mutation. The controller can clear competing fullscreen state and alter pinned
state. Its synchronous event/rule/layout callbacks can replace identities or
change dependencies. Snapshot all potentially affected peer identities, modes,
minimized state, placement and focus/input state. Reacquire and compare them
after callbacks; only explicitly permitted peer changes are acceptable.

Validate min/max/fixed-size constraints and applicable window rules before
advertising MAX. Core floating size clamping is bypassed while fullscreen/MAX;
calling a setter does not enforce a fixed-size contract. In the first phase,
refuse constrained/fixed-size clients unless a precise workarea-compatible
policy has independently been qualified. Recheck constraints on restoration.

## Journal and acceptance oracles

Keep the current authenticated request/generation/binding/context fingerprint
and exact terminal reply. Establish provisional Unknown before mutation; exact
retry returns the original reply and never reapplies the command. Any new intent
field must participate in the fingerprint. Refused means no geometry mutation;
post-mutation exceptions or failed readback remain Unknown. The existing journal
is only the latest request per peer/epoch, not persistent cross-peer recovery.
Do not imply cross-peer automatic replay safety or global Unknown exclusion
without adding and qualifying that separate authority policy.

Read back exact live incarnation, workspace/output ownership, both native modes,
logical/visual placement, origin compatibility, unchanged minimized state,
permitted peers, actual focus/keyboard recipient and protected input state before
Committed. Refresh facts and emit the invalidation hint whenever dependencies
change. The hint is not a replacement for authenticated projection acquisition.

At minimum qualify: noncentered MAX→RestoreGeometry; duplicate desired requests
preserving the original; restored ordinary move/resize then fresh MAX origin;
MAX→Minimize→legacy Restore preserving MAX→RestoreGeometry; stale context and
capability, child/nonroot, retirement/replacement and workarea change refusals;
capacity exhaustion; fixed-size and competing fullscreen refusal; callback partial
mutation retaining Unknown; reconnect preserving origin without rebinding it to
a peer; separate client MAX configure/ACK/exact buffer and presented pixel proof.
State-applied effect receipts must not claim client configure or pixel completion.
Menu selection must still close the actual popup before one shared-allocator
dispatch, with every competing family route respecting pending/Unknown guards.

No Quint logic is authorized by this note. The formal type sketch still requires
the separate approval recorded by the model owner. Complete menu/window parity
remains open after this initial geometry operation slice.
