GUI110 implements native lifetime-safe URI read capabilities and a stable
reference-counted C router. The new WebKit dispatcher compiles and is inactive;
the existing shared-host legacy installation/activation remains unchanged.

A capability holds weak references to the original Shared state and a distinct
Endpoint lifetime, plus its exact Native binding, receiver identity and epoch.
Each open validates that domain under the original Shared mutex before creating
a reader. The Endpoint destructor revokes its lifetime under that same mutex.
Existing readers retain physical Shared/mapping storage, but their own lifetime
and receiver guards refuse bytes after destruction or replacement. Original
Broker token/nonce, native time/source/privacy, expiry, reader capacity and
physical/proof barriers remain in the common original open implementation.
Capabilities and router references cannot pin physical storage by themselves.

The C router retains its creator GThread identity, original binding and monotonic
realm frontier. Same exact live capability binding is idempotent. Clear retains
history; same/old or foreign realm binding refuses before changing the route.
A trusted greater epoch can bind a new capability. The context can hold its own
atomic reference independently of the native owner's reference; clear and owner
unref leave a valid denying callback object. Actual WebKit registration must
retain that independent reference and release it in its context destroy notify.
No raw Endpoint is needed by the new dispatcher. Current legacy handler remains
compatible and keeps its original clear/unregister-before-destruction contract.

Current evidence:
- 66 sanitizer-backed actual C router/read capability/Endpoint/Broker/GIO checks.
  Four real sealed memfd mappings close. Tests exercise stale receiver/URI,
  same-Shared receiver replacement, foreign Native binding and creator thread,
  Endpoint destruction with retained reader, byte revocation before physical
  close, expiry, router clear/frontier and independent callback reference.
  Three separately compiled unsafe variants fail exact original assertions:
  ignoring captured receiver epoch, resetting router frontier on clear, allowing
  existing reader bytes after Endpoint destruction. These are direct synthetic
  native scope/signature-byte fixtures, not actual compositor capture/WebKit.
- 16 explicitly selected Quint scenarios, 200 bounded invariant samples,
  24 actual compiled C traces and 320 state comparisons. Actual endpoint
  existence/receiver epoch, current callback open outcome, existing reader/epoch,
  returned byte count/EOF position, real FD ownership, expiry, owner-reference
  presence and operation result are compared after every event. Router route/
  through are protocol ghosts excluded from comparison. Every successful trace
  clears references and closes its actual mapped descriptors.
- The full host build passes96 commands: every original95 plus the new router
  translation unit. All original resource/capture/ticket/FD regressions pass
  against current changed URI source. Scoped detachment C77/resource60+64+51/cohort66/model21/33/715
  regressions also pass on this current changed URI source, retaining the two
  resource guard variants and five model guard variants.

Two failed model fixtures remain: the initial runner required a missing separate
named-test file, and its fresh replacement encountered nested main renaming and
an unqualified Wire name. Fresh immutable model/fixture derivatives retain those
failures and add explicit returned-byte/EOF comparisons. No product guard,
original assertion or deadline was relaxed.

Actual native baseline remains GUI92/native129/core16/plugin19,2517 checks/278
normal owned exits/full cleanup. GUI110 controlled path and its new router are
not activated in that baseline. Next qualify current compiled GUI110 legacy
routes on the same owning native tuple, then actual WebKit context callback
ownership/replacement with typed incoming/outgoing realm wrappers and retained
native renderer ticket outbox. Scoped Core/Wayland-window detachment/capture,
>256 real windows/Elm neighbors and all original preview13/restore38/recovery34/
case34/two-second/cursor/drag52/input/popup/hardware/output/AT/IME/budget/journey/
coherent release/reversible deployment gates remain. No installed config, main
desktop or drafts changed.
