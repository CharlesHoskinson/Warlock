# Approved context-menu model

The user approved `menu-sketch.qnt` before transition logic was written. That
original is unchanged. Quint reserves `action`, so the first typecheck failed on
the sketch's `Intent.action` field. `menu-types.qnt` is its syntax-only derivative:
module name changed and `action` renamed to `actionId`. The original failed report
remains preserved at `qa/model-1791068438698777553/report.json`.

The model imports those types and state directly. One actor receives menu events,
authority-issued identity/capability/output facts, and delayed correlated receipts.
Atomic grain is one event. Environment facts may change between events. Receipts
may be uncertain, stale, duplicated, refused, committed, or cancelled. There is
no time/fairness claim. Identities are small opaque symbolic integers here; the
separate compiled Elm decoder checks their real uint64 transport representation.

`monitor` adds an auxiliary unresolved-operation ledger and proof evidence. The
root explicitly approved this conservative restriction: one unresolved operation
globally for the single modeled target. Production can retain operations for
multiple independent targets; this model does not qualify that concurrency. Its
`before*` fields, event labels, and witness counters are monitors, not product
state. They record pre-event authorization and observation facts independently
of later native updates. Dismissing/reopening never clears the ledger.

| Requirement | Abstract check |
| --- | --- |
| ELM-RC-004, nonmutating open | Opening emits no intent; no native fact change |
| ELM-RC-006, supported enablement | Disabled/all-disabled commands emit no intent |
| ELM-RC-011/012, retired context | Exact full target, output and capability generation required |
| ELM-RC-016/017, dismiss/navigation | No intent from dismiss, arrows, Home or End |
| ELM-RC-018, intent lifecycle | One correlated intent, pending/Unknown suppress duplicate retry |
| Architecture receipt/observation separation | Receipt cannot manufacture observation or native state |
| Architecture stale event guard | Old menu IDs/receipts cannot authorize or clear a newer operation |

Named positive scenarios make dispatch, refusal/retry and separate observation
nonvacuous. Sampled runs assert all major action witnesses occur in at least one
trace, as well as safety invariants and full requested trace lengths. Tests live
in `menu_test.qnt`; production-model actions and tests are separate. Every action
assigns both state variables. Rejected/stale events are explicit external inputs,
not a generic no-op fallback.

This is sampled abstract safety evidence, not exhaustive verification, liveness,
or native GUI acceptance. It omits submenus, group/provider membership, selection
revision/clipboard, opener/focus restoration, geometry, pointer delivery, pixels,
accessibility, shutdown/reload integration, and multi-target concurrency. Receipt
cancellation closes this abstract menu; the Elm reducer may retain its cancelled
view while permitting an explicit retry. No existing Files semantics are changed.

Run `qa/model.py` through the protected `qa_run.py` launcher. It preserves the
exact source copies, command outputs and failures. Use `--stage sketch` or
`--stage smoke` for incremental checks. The final stage executes exact named
scenario selection and 1,000 sampled traces of 40 steps. Never run `quint verify`
for this workflow. Update and review this model before future semantic changes;
do not change it merely to match broken code.
