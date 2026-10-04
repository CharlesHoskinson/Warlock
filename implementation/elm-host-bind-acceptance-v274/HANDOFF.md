# Retain instance context after a failed host lifetime lock

V266 compiles the actual V256 admission header and reproduces the defect using a
real competing host-writer flock: after refusal, releasing the competing lock and
retrying the same binding still fails because admission_close retired the verified
instance descriptor. The failed report records normal child failure exit and
preserves source/compiler inputs.

V267 changes only host-journal.h's failed lifetime-lock cleanup. It closes and
resets the failed directory/lock descriptors while retaining the verified instance
descriptor for explicit retry. Final admission_close still retires all resources;
the live bound lifetime cannot be replaced by a foreign lifetime. V267's actual
host/Elm build and 22 admission checks pass. Its retry fixture then fails an
independent idempotence assertion: json_node_copy shares its object, so changing
the fixture's foreign binding also changed its original binding. This failed
fixture/report is retained. V268 reparses independent binding JSON in the fixture;
its production native header is byte-identical to V267.

V268 passes 14 actual compiled-C filesystem/flock checks for held and public locks:
first refusal, retry after correction, retained instance descriptor, retired failed
lifetime resources, refusal of foreign lifetime, idempotent same lifetime and final
complete retirement. The real host and optimized Elm programs compile; inherited
20/27/30 compiled replay checks pass. V272 executes eight named Quint contracts and
1,000 invariant samples up to 40 steps for resource ownership and explicit retry.
The model is abstract; this is not automatic implementation refinement.

V269 seals V268's actual ELF, assets and broker into a 20-file capsule on the exact
V89 native core/plugin. V270 and V271 each pass 22 actual native checks for public
and externally held host-writer locks respectively. The broker's attached frame
is withheld because the host cannot bind its lifetime lock. The real bar explains
unavailable recovery data, owned broker retirement is recorded, and application
identity/state and the original lock file remain unchanged. Correcting permissions
or releasing the held lock causes no auto retry during 500 ms. A real pointer
Reconnect retains the same host, obtains a fresh authenticated broker binding,
publishes a coherent snapshot and allows a new committed minimize. Both preserve
screenshots, pointer exits, one shell generation, empty cohorts and normal cleanup.
The held lock belongs to the protected QA owner; this is not a two-production-shell
campaign. The conservative host explanation does not distinguish errno classes.

V273 passes the unchanged original 137-check V171 GUI campaign on V268/V89, including
the original 91-check sequence, renderer recovery and dual-output popup/resize/
removal/replug behavior. Its check/wait call sequences and five helper ASTs remain
identical. The original fixture owns the direct host lifetime in this campaign;
production supervisor behavior is separately observed by V270/V271. Full source,
compiler and native ABI hashes identify the participating artifacts. Normal cleanup
passes. No installed config, main compositor or user drafts changed.

V262/V265's stale-storage, busy/legacy, settlement pixel/input and other recovery
evidence remains retained on its original source, not rerun by these workloads.
Elm, broker and supervisor implementations are unchanged; only failed admission
resource retirement changes. No requirement, sprint or release is completed by
the component/test counts.

Next integration requires combining this production recovery host/broker with the
reviewed newer geometry/menu work. The current geometry broker V56 dispatches both
effect protocols without this durable journal; it must not silently supersede the
accepted recovery path. Generalize strict durable intent encoding for legacy and
geometry effects, preserve one authenticated broker/allocator, define per-operation
Unknown reconciliation, and qualify one coherent tuple after reviewed source
closure. Keep other workers' paths and accepted ABI pairs unchanged. Final recovery
matrix, native full/readonly/later-fsync failures, production legacy provisioning,
global old-live-broker revocation, original restore timing, integrated GPU, AT/IME,
hotplug/zero-output, full operations, physical/human UX, budgets/soak, C00 and release
remain open.
