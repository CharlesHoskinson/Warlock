# V665 atomic admission authority prototype

Status: **bounded storage-only CPU prototype accepted; no effect/native/C,
completion, migration or S15 acceptance**. Frozen647 and661 remain unchanged.
The fresh EARS/OpenSpec refinement and Quint source preceded authority semantics;
root reviewed the short API and atomic-root approach before final freeze.

`adapter/archive_base.py` is byte-exact V647. `adapter/authority.py` privately
refines publication to include one exact Admission event, its17 COW history-index
pages and one validated authority page. One CURRENT selects both the Admission
history and typed authority. The authority page contains separate per-binding
request and generation maxima and per-origin live completion reservations.
Archive publication count/generation never authorizes native replay.

API: `Authority(path, native_lifetime)`; `commitAdmission(exactPendingJsonBytes)`;
`readAuthority(fullBinding)`. Record schema matches V630 schema2 Pending with
complete binding/intent, effect protocol and context. Every native counter uses
positive canonical UInt64 strings. Caller/native-lifetime authentication is an
explicit external assumption, not implemented by this API. A new successful
commit returns `{newAdmission: true, completionReserved: true}`; duplicate exact
bytes return `newAdmission: false`, never a retry authorization. There is no
native invoker or completion method. Opaque append is disabled.

Before pages, QUOTA durably charges admission publication plus four conservative
future publications: Unknown receipt, Prepared, Released and first delivery
certificate. Each future publication reserves one64KiB event,18×16KiB event-index
and authority pages, one16KiB root,4KiB overhead and23 inode slots. Per-origin
completion reserve is **1,523,712 bytes and92 inode slots**. Later retry delivery
certificates need new quota before wire; no old effect replay is authorized.
Capacity accounting is not physical preallocation. Actual ENOSPC can still poison
and refuse; no positive native effect is performed in this prototype.

Final executable evidence, held against final source:

- `qa/tests-1791156450215833695/report.json`:462 checks passed;58 before/after
  filesystem-boundary faults (including10 specifically targeting the LAST typed
  authority page), five actual abrupt child-process exits, separate stale replay
  domains, exact bytes, same-target/full-origin conflicts, duplicate no-retry,
  independent binding maxima, UInt64 canonical/exhaustion controls, quota refusal
  before write, actual short writes, cold barriers and incomplete647-root refusal.
- `qa/model-1791156437536198594/report.json`: four named Quint scenarios,
  500 sampled50-step traces and three detected typechecking mutants. Stale
  generation has an explicit deterministic witness; initial sampling miss is
  retained in `qa/model-1791155959999744364/`.
- `qa/mutations-1791156450199634567/report.json`: three actual Python authority
  mutations produce specific assertion failures; each identical original-source
  oracle passes (generation replay, completion charge and final cold barrier).

Initial three-publication budget omitted Unknown receipt from the proposed future
sequence. Before final source, the refinement was corrected to four. Superseded
exact adapter/spec/runner sources are retained in
`ancestry/superseded-three-budget/` and earlier passing reports remain historical;
they do not establish a complete completion guarantee. No completion pipeline was
implemented or executed, so four-publication budget remains a bounded design
reservation needing review against actual future code.

Cold-open validates typed page, all≤64 live Admission references, authority/history
correlation and direct predecessor conservation, then reestablishes directory
persistence before exposing a handle. Visible-current process interruption may
recover the complete new root; power loss is only symbolically modeled. Invalid
visible/incomplete roots refuse without fallback. Publication errors poison the
handle; input/replay/quota refusals before writes preserve the old usable root.

Bounds: live≤64, scopes≤64, authority page≤16KiB, history depth16, cache≤64.
Authority page-size refusal may occur before these count maxima; nineteen live
admissions were actually measured, not64 guaranteed usable admissions. Every
admission remains live here; no terminal freeing,1026 terminal-cycle campaign,
retired scope or proof maxima, legacy migration, common C locks, native grant
history or frontend cohort protocol is implemented. Full S15 remains open.
Source hashes and tool executable metadata establish bounded local provenance,
not a fully pinned Python/Quint dependency or hardware durability proof.

Reproduce only through the protected CPU launcher, substituting `qa/model.py` or
`qa/mutations.py` for the filesystem runner as needed:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-atomic-admission-authority-v665/qa/tests.py
```

Next independent slice: reviewed terminal/Unknown receipt semantics consuming
reserved budget while conserving original Admission and independent maxima.
Then exact migration and paired C/grant/cohort integration; none should be inferred
from this admission-only acceptance.
