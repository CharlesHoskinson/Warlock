# Actual lost-receipt and original-sender recovery

V195/V198 retain the V188 pure Elm and durable journal implementation. Their only
new runtime behavior is a one-shot, explicitly armed protected-QA fault hook after
an actual native terminal receipt and before journal settlement/frontend delivery.
It is inert without ELM_WINDOW_RECOVERY_FAULT=after-submit and an owned0600 arm
file. Activation requires the protected qa-harness scope and inherited core limit1.
A nonce-free fixed marker under the already private journal directory is created
O_EXCL once, fsynced, then the actual broker suspends itself with SIGSTOP. This
provides a reproducible real lost-receipt boundary; no native receipt is fabricated.

V197 passes52 serial protected native checks against the actual V195 ELF/capsule.
An ordinary activation first completes. The second real pointer selection commits
an actual native activation; its validated Committed receipt and actual application
keyboard recipient are observed while the journal remains Pending and Elm has
received no matching terminal receipt. The verified original broker PID/start is
SIGKILLed. Existing Elm and the actual bar DOM explain Unknown. Renderer failure
then reaches reservation-preserving native GTK fallback; a real Restart click
causes the same supervisor to own a fresh native host and broker.

The replacement broker reports the original uncertain intent under its fresh
binding. The actual replacement Elm projection stays Unknown through a coherent
native snapshot; its bar DOM explains the uncertainty. No window-effect request
is emitted during the observed500ms post-reconciliation interval. A later explicit
pointer selection advances request/generation by1 under the fresh binding and
commits with the expected keyboard recipient. No automatic resubmission/retry
queue exists. Failure/final geometry, application incarnations, compositor identity
and subsequent orderly recovery cancellation/scope cleanup pass. The injected
broker SIGKILL is explicitly recorded as abnormal (normal=0/code=-1), not normal
teardown. Replacement broker and remaining clients exit normally.

V198 strengthens the authority check at that same injected boundary. The original
broker re-handshakes from its original PID/start, advancing its frontend epoch
while retaining its authority session. It replays its own original window-effect
packet from that same authenticated sender and observes binding-mismatch. Native
scene facts/revision/output generation before and after replay agree. It then
suspends at the same lost-receipt boundary. V200 repeats all recovery behavior and
passes55 native checks, including these3 stronger sender checks. This replaces the
indirect evidence of replaying a foreign packet from a separate QA process for
same-sender rehandshake invalidation. It does not assert global revocation of a
still-live separate former broker by another process's handshake.

V196/V199 use the event-driven, source-sealed supervisor/cohort wrapper. Their
capsules each contain20 actual compiled native/asset/adapter files, including the
inert QA hook. The owning core/plugin tuple is still V89, separate from concurrent
cursor/menu core work. Both changed sources compile optimized Main/Bar/Popup and
the GTK host, rerun20 reducer+27 shell checks and30 recovery checks, and each pass19
actual filesystem/subprocess journal checks. Counts are per campaign, not unique
scenario totals. Original check/wait/click/choose/key helper ASTs and observation
bounds are unchanged; new selected fault assertions do not replace original91.

V194's6 exact selected Quint runs/1000 sampled40-step invariant traces and V171's
full137/original91 native regression are retained, not newly rerun. Native fault
results, compiled Elm policy, filesystem tests and abstract model remain separate
claims. No automated Quint/filesystem/C/Elm refinement is asserted.

The frontend-to-broker durable admission gap remains open: an action can be lost
before Journal.begin if the broker never reads it. A fresh host then lacks its
uncertainty record. Durable admission/publication must close this at the host
boundary before release. Global former-session revocation, interrupted native
minimize/restore variants, multiple concurrent/dependent intents, atomic restart
reservation handoff, wrapper startup/death ownership, independently scoped real
application launches, recovery hotplug/zero outputs/keyboard accessibility/IME,
coherent corrected-core/menu/GPU tuple, all window operations, hardware/usability/
resource budgets/soak, C00 and full release gates remain open. No complete
requirement or sprint is closed and the installed desktop/configuration is unchanged.
