# Native shared-output host

V150 runs one hidden Elm Main/OutputController and one authenticated backend.
Each live GdkMonitor gets a native 48px layer bar containing only Elm.Bar's
Presentation cache. The shared popup engine is reparented into a lease-owned
native wrapper under the selected bar. Engine settings preserve ephemeral local
assets, sandboxing, disabled developer extras and the acceleration policy.

The C registry issues monotonic uint64 view IDs, retains each owning monitor,
and binds callbacks to immutable manager/widget identity. A display view cannot
post an outer scope, arbitrary backend requests or a controller commit. It sends
only a validated enabled Surface action; native code stamps the originating
scope. Popup callbacks additionally require current native readiness and lease.
Retirement disconnects callbacks, destroys the bar and releases its manager and
monitor. A replug gets a fresh ID. Removed views do not retire the global backend.

Controller commits validate the exact native topology, popup/focus owners,
complete frame, publication/lease, queue budget and allowlisted effects before
mutating surfaces. A topology-only commit may reuse the identical accepted frame
with no effects; it seeds a newly created presenter without replaying a command.
Popup relocation retires the old wrapper before using a fresh lease and new
anchor. Geometry reflow keeps the engine and asks Elm for a fresh scoped lease.
Duplicate object members, including decoded escaped names, are rejected before
schema admission; identical field names in distinct nested objects are allowed.

## Qualification

V151 passes135 native checks including the original91 scenario assertions and
unchanged check/wait/click/choose/key helper AST and deadlines. One actual host
PID owns both bars; exactly one matching backend process is observed. Existing
window activation/minimize/restore, actual keyboard recipients, popup navigation,
viewport reveal, stopped/killed broker Unknown retention and fresh-binding
recovery remain in the campaign.

A second private output exercises 640x480, live480x320 resize, 960x640 buffers at
scale2 and transform1, native keyboard readiness, Escape/reopen, per-output top48
reservation and owner removal. Replug creates native view3 after retiring view2;
its popup actually configures within the current640x480 viewport. The backend PID
and authority binding stay unchanged. The host/backend exit normally; protected
ordered cleanup passes. Parent1600x1000 retains the fixture bounds correction
qualified in V140, while the original primary child remains800x600.

V150 builds the actual optimized Main, Bar, Popup and C shared host. Eleven host
unit groups and four surface groups pass. Every Elm module matches frozen V145,
retaining37 shared-controller,58 controller and12 presenter checks. V143's ten
explicit named Quint scenarios and1,000 invariant traces remain abstract model
evidence; there is no automatic C/Elm refinement claim.

V146's compiler failures (indentation and goto/cleanup initialization) are retained.
V148 compiles but its new scope unit test aborts on an incorrectly typed JSON node.
V149 fixes it and passes the original shared campaign127 in V147. V150 adds the
duplicate-field guard and V151 adds actual single-backend/replug observations.
All packets and current hashes are frozen in qa/slice-manifest.json.

## Remaining gates

This establishes the shared controller/backend architecture for the tested output
and window flows. It does not accept the full desktop or close any baseline
requirement/sprint. Integrate the reviewed menu-reflow lane into these actual
shared scopes; continue missing native Maximize/geometry/Pin/Close/Move/Size flows,
all-origin Unknown/recovery, canonical scene/fullscreen/lock and workspace policy.
Actual zero-output suspension/recovery, all transforms, fractional scale/negative
origins/workarea, renderer/view failure, full AT/IME/human journeys, measured
hardware/GPU/WebGPU/resource budgets, C00 and coherent release remain open.

The inherited host.c is compiled as comparison functions; shared-host.c supplies
the actual entry point. The installed desktop and user's drafts are unchanged.
