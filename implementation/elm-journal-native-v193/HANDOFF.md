# Durable window-action recovery candidate

V188 adds a single-record recovery journal to the native authority broker. Before
submitting a window effect, it validates and atomically persists the authenticated
binding and typed intent, fsyncs the record and directory, then calls the existing
native endpoint. A validated correlated terminal receipt is persisted before it
is sent to the host. Pending/Unknown records are informational on recovery: they
never form a retry queue. The journal lives under the verified private compositor
runtime, has0700 directory/0600 regular single-link files, bounded4096-byte records,
strict schema/canonical identities and a lifetime check. A held nonblocking flock
admits one broker writer. Persist failures prevent subsequent native submission.

A replacement broker emits attached, then host-uncertain under its fresh binding
for an old pending intent. The typed Elm reducer preserves Unknown through the
fresh authoritative snapshot and rejects stale terminal receipts. It emits no
recovered action. A later explicit user action uses advanced request/generation
counters and the fresh observed native authority. Binding remains an opaque Elm
type; a pure sameLifetime predicate admits matching recovery scope.

V187 retains the first build failure (attempted record access on opaque Binding).
V188 compiles optimized Main/Bar/Popup and the actual GTK host; inherited20 reducer
and27 shell checks pass, plus30 compiled recovery checks. Its journal QA passes19
checks, including actual abrupt writer SIGKILL, new-writer Unknown recovery,
concurrent-writer refusal, malformed/duplicate/public/symlink/oversize records,
correlation and terminal persistence. These are actual filesystem/subprocess
checks and pure compiled policy checks, not full native pending-action acceptance.

V189 seals the actual candidate native binary/assets/adapters (19 files). V190's
native run verified durable authenticated native receipt settlement, actual
renderer recovery and supervised replacement, then failed a preexisting wrapper
race: the empty transient cgroup disappeared during member enumeration. V192
handles only FileNotFound disappearance while observing that kernel-owned group;
other errors still propagate. The failed campaign and its cleanup are retained.
V193 repeats the same protected workload against V192. Original helper ASTs and
all inherited observation deadlines remain unchanged.

V191 retains a model parse failure from redefining Quint's built-in fail name.
V194 renames that action and explicitly executes6 named scenarios and1000 sampled
40-step invariant traces. This abstract durable-intent/Unknown/no-auto-replay model
is separate evidence, not automatic refinement of filesystem ordering or C/Elm.

The compositor/plugin owning tuple remains V89. V171 full137/original91 and previous
GPU qualification are retained, not rerun by this journal workload. No WebGPU,
accessibility/IME, full scene, physical device, resource budget or release claim is
added. The live desktop/configuration is unchanged.

Native effect submission with an interrupted/lost receipt and actual replacement
Unknown display still require a real fault campaign. Former authenticated sender
reuse must be tested from that sender PID/start, because command sockets are
per-request; replaying its packet from a separate QA process is weaker evidence.
Intent loss between frontend admission and broker journal.begin remains a gap;
window-action delivery/acknowledgement must close it before release. Whole-shell
restart reservation continuity, recovery hotplug/AT, independently owned app launch
scopes, wrapper startup/death ownership, coherent new core/menu/GPU tuple and all
remaining S01-S16/C00/release obligations remain open. No requirement is closed.
