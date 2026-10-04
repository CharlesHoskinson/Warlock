# Durable host admission before broker read

V211 closes the selected host-to-broker process-loss gap. The actual GTK host
validates the single window intent against the authenticated backend binding and
atomically persists host-intent.json before mutating its accepted surface frame,
publishing Pending to the bar, or queuing the backend write. A separate held
host-writer flock admits one host; the existing broker owns its separate settlement
journal. Both live under the private runtime's0700 recovery directory, use0600
regular single-link files, reject symlink ancestry and canonicalize typed uint64
identities. Writes fsync the temporary file, rename it and fsync the directory.
A failed admission refuses the frame and withholds forwarding. Multi-effect
batches are refused before persistence; this remains a single-inflight design.

The host captures binding only from its selected broker's authenticated attached
frame and clears it on broker exit. An absent/retired binding cannot become host
recovery state. The broker's recovered state prefers the latest admitted host
intent. Only an exact binding+intent match in its durable terminal settlement can
resolve that Pending record. An older Committed receipt cannot resolve a newer
host intent. The recovery records are informational, never an executable retry
queue. Native/Elm authority still decides whether a forwarded effect commits.

V201 preserves the initial unbound journal implementation/build. V202 adds bound
admission and passes22 actual compiled-C/filesystem/broker-correlation checks.
V204/V205 retain fixture failures from selecting both the host (whose argv contains
the broker path) and broker as candidate senders; V205 captures the actual tree/argv
that explains the error. V206 fixes sender selection, but stopping the broker before
picker selection prevented its required fresh snapshot, so no effect existed.
V208 adds a protected projection-response stop hook; V210 retains its failure:
a refresh advanced the expected snapshot ID before the intercepted older response,
and Elm correctly remained Awaiting. Original deadlines are unchanged throughout.

V211 instead adds an inert, explicitly armed protected-QA host queue hook. After
durable admission and publication, before write_next sends the actual effect, the
host creates/fsyncs an O_EXCL marker and holds that queue. It requires the native
QA flag, explicit before-effect-write environment selection, private0600 arm file,
protected QA cgroup and inherited exact core limit1. Ordinary operation bypasses
it. It neither fabricates native receipts nor bypasses fresh-snapshot reconciliation.
The fault fixture verifies the native host and actual broker PID/start and then
SIGSTOPs/SIGKILLs that original broker. No effect request reaches it.

V213 passes57 protected native checks against the actual V211 ELF and V21220-file
sealed runtime capsule. The latest host intent exists while the stopped broker's
journal still contains the previous committed request. Trace order verifies durable
admission before backend-forward logging and the actual Pending bar DOM publication.
Broker loss displays Unknown in existing Elm/DOM. Actual renderer failure then keeps
native recovery bars/reservation, and a real Restart causes the same supervisor to
own a replacement host. Its fresh coherent snapshot preserves the original uncertain
intent and actual Unknown DOM; no automatic effect appears during the selected500ms
observation. A later explicit user selection advances request/generation and commits
under the fresh binding with the expected actual keyboard recipient. Geometry,
incarnations/compositor identity and serial ordered/scope cleanup pass.

The recipient before delivery loss is established from native focused incarnation
and an actual keyboard receipt, then must survive renderer failure. This records
popup-close focus as observed native behavior; it does not silently assume that an
unread activation changed focus. Original key/click/wait/choose/check helper ASTs
remain unchanged. The injected broker kill is explicitly abnormal, not a normal exit.

V214 runs the same actual source/capsule without arming the hook and passes43 native
checks. The host's Pending admission exactly matches its broker's durable Committed
record. Actual renderer failure/native Restart/fresh coherent snapshot recover
without host-uncertain, so the dual records do not generate a false Unknown.
Ordinary activation, keyboard recipient, recovery cancellation and cleanup pass.

V211 reruns22 actual C/filesystem/correlation checks,19 existing journal checks,
optimized Main/Bar/Popup and GTK builds,20 reducer+27 shell+30 recovery checks.
V207 executes8 exact named Quint scenarios and1000 sampled40-step invariant traces
for host admission/publication, correlated settlement, old receipts, unread recovery,
no automatic replay and fresh explicit action. This is an abstract contract, not
automatic C/filesystem/Elm refinement. Historical native91/full137, hardware graphics
and same-sender rehandshake55 remain retained, not newly repeated by these campaigns.

The selected admitted-action/unread-broker recovery gap now has real native evidence.
Loss before the native host accepts a renderer commit cannot have forwarded an effect
through this host; it is not relabeled an admitted Pending action. Storage-error UX,
compositor-lifetime/instance journal namespace and migration, global former-live-broker
revocation, interrupted minimize/restore, multi/dependent intents, atomic reservation
handoff, wrapper startup/death ownership, separately scoped application launch,
recovery hotplug/zero outputs/AT/IME, coherent new core/menu/GPU tuple, full native
operations, devices/usability/resource budgets/soak, C00 and all release obligations
remain open. No complete requirement or sprint is closed. Installed desktop and
configuration are unchanged.
