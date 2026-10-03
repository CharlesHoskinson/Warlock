# Typed Elm recovery and correlated observations

Fresh V16 GUI derivative, using the immutable V15 native authority/core tuple.
Binding is opaque and typed. User actions use an Elm operation type, and Shell owns
pure update state for attachment, reconciliation, pending requests, disconnection
and explicit recovery. Main translates effects to ports and renders the view.

Projection replies now carry native binding and the originating refresh request.
Shell refuses replies for retired bindings, superseded requests and mismatched
context before enabling actions. Native receipts do not optimistically change
window state; effects wait for a correlated fresh observation. Disconnection marks
pending requests Unknown, disables window controls and labels retained information
as last known. Reconnect asks the native host to start a new authenticated broker,
only after the old subprocess and outstanding write are finished. Queued old
requests are discarded. A new binding and fresh snapshot precede new effects;
uncertain work is never automatically replayed.

The protected native runner uses actual button geometry and owned Wayland pointer
input. It SIGSTOPs the exact Python broker, clicks Minimize, observes Pending with
all actions disabled and native state unchanged, then intentionally SIGKILLs that
broker. It clicks Reconnect, verifies a new native session binding, fresh state and
no replay, submits a retired binding to native authority and verifies refusal, then
executes new minimize/restore requests. The interrupted broker has an intentional
signal exit; the replacement broker and webview have normal exit receipts.

Validation is bounded: 20 compiled effect checks, 27 compiled Shell checks, eight
actual named Quint runs, 1000 sampled invariant traces (40 steps), nine actual ITF
journals replayed against compiled Shell (75 transitions), and 21 private native
checks. This proves the broker recovery path, not renderer or compositor restart,
complete scene/paint/input ordering, GPU performance, AT/IME or release acceptance.
Canonical scene capability remains false; ActionProjection remains an enumeration.
Original initial-render and per-observation deadlines are retained. The render
watchdog is retired after the actual validated initial render, allowing the private
stay-open campaign to continue; individual native observation limits remain six
seconds.

All failures are preserved. The first native fault injection incorrectly selected
the host because its command line also contained the broker path. The corrected
selector requires the exact Python/-B/script argv prefix. Cleanup checks now finish
all retirement before reporting failures, preserving the original exception. A
second run reached recovery but expected a returned error where the authenticated
endpoint correctly raises native Refused; the runner now explicitly asserts the
binding-mismatch exception and unchanged state. Earlier model syntax failure is
also retained. No installed desktop or user drafts changed.
