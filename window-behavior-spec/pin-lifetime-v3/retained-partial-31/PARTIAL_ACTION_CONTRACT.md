# Pin callbacks, partial outcomes and owned feedback

The V1/V23 subset and its fourteen proofs are preserved byte for byte outside
this fresh derivative. The native core operations emit synchronous callbacks.
Floating may already change before a later pin refusal; pin may already change
before raise refusal or closure/minimize. A false result therefore means the
requested complete operation was not verified. It does not assert no mutation.
The candidate reports the reached phase, exact captured identity, initial and
current pin/float state and backend error rather than rolling back callback
changes or emitting successful feedback for a partial result.

Each operation captures a strong owning window, native address/stableID/PID,
current compositor signature/PID/start and separate configuration epoch. Same
owner reentry refuses while that operation is active. Other family owners remain
independent. Float, pin and conditional raise use explicit owning core APIs;
after every call the same strong object must remain mapped, visible, on a normal
workspace, supported by the explicit fullscreen policy and identity/epoch/pin
intent unchanged. After raise the final state is checked again. Reload retires
the operation epoch and feedback; it does not invent a new compositor session.
No later failure rolls back a legitimate callback's minimize, close, workspace,
pin or opacity change. A subsequent genuine click samples current state anew.

Delayed external product requests require the full captured native window tuple
and compositor session plus current configuration epoch. Missing fields, unknown
wrapper, stale address/stableID/PID/session/epoch, closed or reused lifetimes
refuse before any action. There is no active-window fallback. Native titlebar
dispatch is synchronous on the retained owning window and never execs an
address-only shell command. Staged keyboard/menu helpers must capture identity
before queuing and submit that exact tuple. Installed main helpers stay unchanged.

Feedback must not mutate the user's window opacity override. The installed Lua
effect writes PRIORITY_SET_PROP opacity and resets it to1, which neither restores
the prior priority state nor distinguishes an external same-value write. The
proposed candidate instead owns a titlebar draw multiplier, independent of core
window alpha/opacity rules. It fades its own titlebar feedback over220ms, with
exact window lifetime, operation/configuration generation and a weak window
reference. It emits feedback only after a fully verified action. New operations
replace the previous generation; old timer/draw observations have no authority.
Close, minimize, reload, unload and reduced motion remove this independent lease
without changing any window property. Whole-window opacity fading is not claimed.

The native product routes must expose actual errors and partial outcomes to the
caller; logs alone do not turn failure into success. Unsupported maximized or
fullscreen state refuses before floating or mutation. The separate supported
maximized policy remains open. Legacy pre-plugin windows require native lifetime
discovery from the live window registry, preserving their actual current pin and
float state; no ownership is inferred from an old two-field minimize record.

Private QA must exercise real titlebar clicks and product keyboard/menu request
routes, windows created before plugin/service as well as fresh lifetimes, reload,
minimize/restore, normal workspace/monitor transfers, independently pinned family
members, stale tokens, callback close/minimize/reload and rapid ordering. Exact
public native state and lifetime observations decide results; model/source tests
cannot claim actual native correctness. Root alone launches native QA.
