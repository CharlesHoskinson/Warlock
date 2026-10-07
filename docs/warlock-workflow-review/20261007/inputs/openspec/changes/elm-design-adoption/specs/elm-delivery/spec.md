# elm-delivery — design adoption draft

## Purpose

Draft refinements for the existing in-flight `elm-delivery` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.

Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 or original deadlines. Native authority and no automatic replay of Unknown remain mandatory. C00–C06 compositor replacement remains conditional.

No new native, hardware, IME, AT or full-release evidence is supplied by this packet. Frozen component/model/CPU/compiled replay evidence is not production-provider or full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate owning ABI pairs. Implementation and qualification tasks remain unchecked.

## ADDED Requirements

### Requirement: ELM-ADOPT-003 — Coherent recovery checkpoints and interrupted migration qualification

WHEN recovery installs a checkpoint, the authority SHALL validate its coherent schema, lifetime, watermark and retained obligations before effect admission, reconcile uncertain outcomes without replay, and preserve each original deadline.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: P0.

Baseline mapping: ELM-ARC-010, ELM-ARC-014, ELM-REV-008, ELM-REV-012, ELM-QA-007.

Existing work mapping: W01, W02, W09, W10.

Source proposals: IMM-03.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Use existing durable ledger. Interrupted migration/write/fsync and storage-full are qualifying faults; coherent checkpoint is not proof that a window action completed.

Tradeoffs: Crash-barrier fixture maintenance and synchronous storage cost; a manifest over existing stores may suffice; database replacement is deferred.

Primary sources:

- <https://sqlite.org/atomiccommit.html>
- <https://doc.akka.io/libraries/akka-core/current/typed/persistence.html>

#### Scenario: ELM-ADOPT-003 Completed checkpoint

- **GIVEN** Synchronized checkpoint with Unknown and retired-request floors
- **WHEN** Frontend restarts
- **THEN** Coherent observation/reconciliation state is restored without old mutation dispatch

#### Scenario: ELM-ADOPT-003 Interrupted migration

- **GIVEN** Visible rename and incomplete synchronization/migration barrier
- **WHEN** Recovery sees newer scene plus late old-binding receipt
- **THEN** Validated recovery completes or remains fail-closed without mixed owners, lost Unknown, or reset deadline

### Requirement: ELM-ADOPT-013 — bounded allowlisted diagnostics independent of authority

WHILE ordinary diagnostics are enabled, the diagnostics subsystem SHALL admit only allowlisted bounded records and SHALL report record loss without collecting excluded content or altering native authority, operation outcomes or deadlines.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 2.

Baseline mapping: ELM-DEL-017, ELM-QA-021, ELM-QA-023, ELM-REV-020, ELM-REV-021.

Existing work mapping: W04, W11.

Source proposals: ERR-03, OPUS03-ER-03, OPUS01-IMM-5.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Secrets, credentials, draft contents and captured pixels are always excluded from ordinary diagnostics under ELM-DEL-017. Raw port bodies, titles, arguments and paths are also excluded by this ordinary allowlist. A different scoped mode requires a separate reviewed contract and is outside this draft. Retention/loss counters remain bounded. Saturation cannot block native control/cleanup or compact durable authority.

Tradeoffs: unrestricted verbose logs simplify one incident at privacy/resource cost; aggregate-only metrics lose sequence context. Cost: event schema, producer audits and saturation tests. A ring buffer and separate counters are possible implementations, not mandated architecture. Validation: sensitive canaries across nested values and error strings; resource saturation, failure to write and malformed events preserve controller decisions. Measure log-rate, whole-process CPU/wakeups/memory, export cost and retention against `elm-performance/spec.md` ELM-QA-021/023 and ELM-REV-020/021; the performance owner freezes numeric limits from P0 workloads before acceptance. Measure under the actual ELM-QA-021/023 and ELM-REV-020/021 budget contract.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://apalache-mc.org/docs/adr/015adr-trace.html>
- <https://arxiv.org/abs/2006.00915>
- <https://arxiv.org/abs/2104.01146>
- <https://arxiv.org/abs/2404.16075>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://immerjs.github.io/immer/patches/>
- <https://kafka.apache.org/43/design/design/>
- <https://lamport.azurewebsites.net/pubs/abadi-existence.pdf>
- <https://opentelemetry.io/docs/security/handling-sensitive-data/>
- <https://opentelemetry.io/docs/specs/otel/logs/data-model/>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://people.seas.harvard.edu/~chong/pubs/pldi13-elm.pdf>
- <https://quint.sh/docs/checking-properties>
- <https://raw.githubusercontent.com/avh4/elm-program-test/main/src/ProgramTest.elm>
- <https://raw.githubusercontent.com/elm/browser/master/src/Debugger/History.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Array.elm>
- <https://raw.githubusercontent.com/elm/core/1.0.5/src/Dict.elm>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://redux.js.org/style-guide/>
- <https://systemd.io/CATALOG/>
- <https://www.cs.cmu.edu/~rwh/students/okasaki.pdf>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-013 ERR-03-01

- **GIVEN** a decoder failure containing a secret canary and window title
- **WHEN** a diagnostic record is produced
- **THEN** only allowed category/context fields appear and neither canary nor title is retained.

#### Scenario: ELM-ADOPT-013 ERR-03-02

- **GIVEN** diagnostic capacity is exhausted during a pending effect
- **WHEN** further records arrive and a terminal receipt races
- **THEN** loss is observable, memory stays within the frozen budget and receipt settlement is identical to diagnostics-disabled execution.

### Requirement: ELM-ADOPT-014 — recovery evidence distinguishes restored availability from past success

WHEN a failed frontend or authority recovers, the shell SHALL report verified current availability separately from unresolved historical outcomes and SHALL admit new effects only after native reconciliation under the original deadline and identity contracts.

Status: consensus-draft-implementation-and-qualification-open. Classification: draft-refinement; original research classification: refinement. Priority: 1.

Baseline mapping: ELM-ARC-014, ELM-ARC-026, ELM-QA-002, ELM-QA-003.

Existing work mapping: W05, W10, W11.

Source proposals: ERR-04, OPUS03-ER-05.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Recovery action must preserve durable Unknown, replay floors, held resources and original clocks. Generic restart guidance is not acceptance. Compositor replacement is not an incidental recovery action.

Tradeoffs: automatic retries may appear faster but are prohibited here; generic “recovered” banners omit the critical uncertainty. Cost: recovery phase/report integration and protected fault campaign evidence. Validation: original restore38/recovery34 with unchanged identity/oracle/deadline, held effects, missing/corrupt journal, unavailable storage, frontend/authority epoch replacement and stale proof. Component replay supplements rather than replaces native acceptance.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-coredump.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>
- <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2002/Archive/CSD-02-1175.pdf>

#### Scenario: ELM-ADOPT-014 ERR-04-01

- **GIVEN** an admitted effect and crash before durable settlement
- **WHEN** a fresh epoch receives a coherent snapshot
- **THEN** availability may recover while the previous effect remains unconfirmed and is never replayed.

#### Scenario: ELM-ADOPT-014 ERR-04-02

- **GIVEN** a storage-full recovery failure and matching-looking geometry from a replacement incarnation
- **WHEN** reconciliation is attempted
- **THEN** geometry alone cannot clear the historical reservation, no new dependent effect is admitted and each affected operation's original deadline is unchanged and is not renewed by recovery.

### Requirement: ELM-ADOPT-015 — explicit diagnostics export boundary

WHERE local diagnostic export is selected, WHEN the user requests an export, the shell SHALL produce an inspectable local bundle of validated export-allowed evidence and declared omissions, preserving recovery authority and sending nothing externally.

Status: deferred-conditional-draft. Classification: deferred-conditional-export; original research classification: conditional-new. Priority: deferred.

Baseline mapping: ELM-DEL-017.

Existing work mapping: W11.

Source proposals: ERR-05, OPUS03-ER-04.

Owner: Release integration lead. Verifier: Independent acceptance reviewer.

Guardrails: Conditional/deferrable feature; not a new mandatory release blocker. No default cores, screenshots, environment, unrestricted journals or uploads. Explicit local user request; cancellation/disk-full has truthful partial-artifact outcome.

Tradeoffs: copying a journal manually is cheaper but produces unreviewable privacy and scope surprises; automated cloud uploads introduce unsupported product scope. Cost: bundle builder, accessible review and export fault testing. Validation: unpack and schema-check artifacts; canary and content scans; stale-epoch snapshot race, cancellation, disk-full and symlink/path defenses; measured export overhead must meet frozen performance budgets.

Disposition: deferred conditional export. This adds no mandatory release blocker. Product selection, destination/privacy policy and measured budgets require separate review before implementation.

Primary sources:

- <http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf>
- <https://docs.gtk.org/glib/logging.html>
- <https://docs.sentry.io/platforms/python/data-management/sensitive-data/>
- <https://google.aip.dev/193>
- <https://opentelemetry.io/docs/security/handling-sensitive-data/>
- <https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/>
- <https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md>
- <https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-coredump.xml>
- <https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml>
- <https://systemd.io/CATALOG/>
- <https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf>
- <https://www.nngroup.com/articles/ten-usability-heuristics/>
- <https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html>

#### Scenario: ELM-ADOPT-015 ERR-05-01

- **GIVEN** diagnostics and an available core dump containing private memory
- **WHEN** the user requests the ordinary bundle
- **THEN** the bundle includes allowed metadata and states that core/pixels/content are omitted.

#### Scenario: ELM-ADOPT-015 ERR-05-02

- **GIVEN** export is assembling records while frontend epoch changes
- **WHEN** cancellation or disk-full occurs
- **THEN** no success is reported, partial-artifact disposition is explicit, and neither old nor fresh recovery reservation is changed.
