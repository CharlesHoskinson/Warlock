# Error reporting, Unknown outcomes, recovery and diagnostics: review of the frozen Elm shell source (reviewer opus-03-error-reporting)

**What this covers.** I read the frozen snapshot at head `7acf7a7`, as listed in `source-manifest.json` (338 files, baseline 242 requirements / 417 scenarios). Every claim about current behaviour comes from reading source. None of it comes from a native, GUI or assistive-technology run. Everything below is a draft, and none of it is accepted behaviour. This is one independent review, not consensus. I made no edits, compiled nothing and started no agents.

---

## 1. Current-design findings

### 1a. Implemented behaviour worth keeping (source-level only)

- **K1. Outcome types are complete and kept separate.** `Effects.elm:11` defines `Pending | Committed | Refused | Cancelled | Unknown`.
  - `statusDecoder` (`Effects.elm:40-46`) only accepts terminal states from native.
  - A disconnect turns Pending into Unknown (`Effects.elm:127`). So does a change of authority context in a snapshot (`Effects.elm:83`).
  - `blocked` (`Effects.elm:169-170`) stops new work on any incarnation that has a Pending or Unknown operation.
  - Refused is never invented. `locallyRefuseUnsent` (`Effects.elm:189-205`) needs an exact preflight-unsent certificate, which is the workplan rule at `FRP-ELM-WORKPLAN.md:93-94`.
- **K2. Unknown is cleared only by reconciliation, never by replay.**
  - `ReconciliationTracking.release` (`ReconciliationTracking.elm:67-79`) needs a retirement proof plus both the action and geometry observations, all correlated by `ReconciliationFrame.decodeReleased` (`ReconciliationFrame.elm:55-69`).
  - The Python side, `reconciliation.py:1-6, 28-36`, "never makes an effect". On reconnect it re-announces the exact durable history.
- **K3. Recovery-storage failures already map to fixed, actionable messages.**
  - `recovery_journal.py:17-20` reduces OS errors to `busy | full | unavailable | legacy-owner | unverified`.
  - `Shell.elm:12-29` decodes that closed set and shows a sentence that names the cause and the fix ("Free space, then reconnect.").
  - `daemon.py:199-202` sends `host-recovery-failed` before `host-disconnected`. This is the closest existing match to the taxonomy I propose below.
- **K4. Startup and recovery are the same code path.** `publish_startup` (`daemon.py:~150-159`) sends settlements, recovered Unknowns and staged frames every time it starts. This is the crash-only principle (S2).
- **K5. Backend crash output carries little private data.** For any error that is not `Refused`, `daemon.py:205` prints only the exception class name, not its message.

### 1b. Gaps

These are current behaviour confirmed by reading source; none was observed on a GUI.

- **G1. All user-facing status shares one free-text slot, filled by a priority ladder.** `Surface.notice` (`Surface.elm:103-119`) picks menu → choice → launch → catalog → … and only then falls back to `Shell.status` (`Shell.elm:68-76`). Consequences:
  - **Unknown can be hidden.** A stale launch status such as "Launch submitted." (`Surface.elm:115`) wins over a window Unknown. The bar control still says "Awaiting native confirmation" (`Surface.elm:98`), but the live region does not.
  - **Broken sentences.** `Shell.status` appends a suffix to whatever `notice` holds. After a snapshot sets `notice = "Connected"` (`Shell.elm:189`), a Refused receipt produces "Connected The window change was refused." (`Shell.elm:75`).
  - **Cancelled has no message** (`Shell.elm:72-76`).
- **G2. Internal and native text reaches users.**
  - `Shell.elm:147` copies the reducer's refusal string straight into `notice`. Examples: "Locked or unmapped target", "Unresolved native operation" (`Effects.elm:89-98`) and "Geometry observation unavailable" (`Shell.elm:140`).
  - Menu refusals show native free text verbatim (`Surface.elm:107`). The only guard is a 256-codepoint truncation (`Menu.elm:373-396`).
  - Heuristic #9 (S4) and AIP-193 (S8) both argue against showing this kind of text. Its privacy has not been shown either way.
- **G3. Two live regions show the same text.** `SurfaceRenderer.elm:60` (popup `<p>`) and `:61` (bar `<span>`) are both `role="status" aria-live="polite"` and render the same `snapshot.status`.
  - Under WAI-ARIA, `status` implies `aria-atomic=true` (S5), so any change to the joined string re-reads all of it.
  - Nothing deduplicates by outcome identity, yet ELM-UI-010 requires it. ELM-UX-026 and W08 ask for one announcement owner.
- **G4. Rejected frames disappear without trace.** Malformed or uncorrelated frames are correctly ignored with no effect: `Shell.elm:158, 163, 177, 190-191, 194, 201, 211, 216, 229, 239, 257-258`. But nothing counts them, so a stuck or hostile peer cannot be seen. W11 asks for "diagnostics/reconciliation" and specifies no format.
- **G5. Backend diagnostics are unstructured.**
  - `daemon.py:204` prints `file:line:function` to stderr. Those positions shift between builds; WER's permanent assert tags (S3, §3.1 L15) exist to avoid exactly that.
  - There is no stable reason code, no severity, no correlation to binding, lifetime or request, and no rate bound.
- **G6. Test fault markers contain full authority data.** `recovery_fault.py:27-29` and `host-fault.h:19` write the full request, binding and PIDs. These run only in protected QA, which is fine, but it shows that any diagnostics written naively will contain authority identities.
- **G7. Terminal phases leave the user stuck.** `Shell.elm:61` ("Restart the shell to continue.") and `:70` (reconciliation full) offer no in-shell way out. The v814 handoff, `HANDOFF.md:27-31`, already lists this as an open product gap (816).

---

## 2. Sources

All retrieved 2026-10-05 and read directly.

| ID | Source (type, year) | Link | Claim I rely on | Limitations |
|---|---|---|---|---|
| S1 | Birrell & Nelson, *Implementing Remote Procedure Calls*, Xerox PARC CSL-83-7, Dec 1983 (TOCS 2(1), 1984). Academic. | [bitsavers scan](http://www.bitsavers.org/pdf/xerox/parc/techReports/CSL-83-7_Implementing_Remote_Procedure_Calls.pdf) | p.11: if the call returns, the server ran "precisely once. Otherwise, an exception is reported… invoked either once or not at all - the user is not told which." p.12-13: call IDs with monotonic sequence numbers plus a conversation ID per incarnation remove duplicates. | 1983 LAN RPC with no durable journal. Supports keeping Unknown as its own state; says nothing about UI. |
| S2 | Candea & Fox, *Crash-Only Software*, HotOS IX, 2003. Academic. | [USENIX PDF](https://www.usenix.org/events/hotos03/tech/full_papers/candea/candea.pdf) | p.68: "recovery code is exercised every time the system starts up". p.70: requests "carry information on whether they are idempotent"; non-idempotent operations need "roll… back, apply compensating operations, or tolerate the inconsistency". p.71: the restart/retry design needs most requests to be idempotent. | Written for Internet services. Its transparent-retry assumption does **not** hold for non-idempotent window effects, which supports *not* retrying here. |
| S3 | Glerum et al., *Debugging in the (Very) Large*, SOSP 2009. Academic. | [MSR PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/sosp153-glerum-web.pdf) | §2.1 bucketing. §2.2: "Most error reports consist of no more than a simple bucket identifier". §2.4: consent "default[s] to negative"; client "zeros serial numbers". §3.1 L15: permanent assert tags keep one bucket "even as the assert moves in the source". | Remote, billion-machine, proprietary. I take only the local principles. |
| S4 | Nielsen, *10 Usability Heuristics*, 1994 (updated 2024-01-30). Author material. | [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/) | #1 visibility of system status. #9: "plain language (no error codes), precisely indicate the problem, and constructively suggest a solution." | Heuristic guidance, not an assistive-technology study. |
| S5 | W3C WAI-ARIA 1.2 Recommendation, 2023-06-06. Standard. | [w3.org](https://www.w3.org/TR/wai-aria-1.2/) | `status` role: implicit `aria-live=polite`, `aria-atomic=true`. `polite` waits for current speech to end. | Specification only; WebKitGTK→AT-SPI→Orca behaviour is unproven. |
| S6 | W3C *Understanding WCAG 2.2 SC 4.1.3*. Standard. | [w3.org](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Status messages include "the existence of errors" and are presented "without receiving focus". Warns against being "too 'chatty'". | Written for web content; does not prove behaviour on this host. |
| S7 | gRPC `statuscodes.md`. Maintained OSS. | [GitHub](https://raw.githubusercontent.com/grpc/grpc/master/doc/statuscodes.md) | DEADLINE_EXCEEDED: the operation "may [have] completed successfully". UNAVAILABLE: "not always safe to retry non-idempotent operations". Separates FAILED_PRECONDITION, ABORTED and UNAVAILABLE by who may retry. | RPC status vocabulary; no UI guidance. |
| S8 | Google AIP-193 *Errors* (updated 2024-10-18). Maintained open docs. | [aip.dev](https://google.aip.dev/193) | The same (reason, domain) pair "must" be used for the same error; reason is UPPER_SNAKE, ≤63 characters. Request-specific data goes in `metadata`. Messages are brief and actionable. | Aimed at API developers, not end users. |
| S9 | systemd `systemd.journal-fields` (man source) and *Journal Message Catalogs*. Maintained OSS. | [man XML](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.journal-fields.xml), [CATALOG](https://systemd.io/CATALOG/) | 128-bit `MESSAGE_ID`; `PRIORITY` 0-7; underscore fields are "trusted… cannot be altered by client code". Catalog keyed by MESSAGE_ID, localizable, with Subject and Documentation fields. | Assumes journald on the target session; journal entries are readable locally. |
| S10 | GLib *Logging* docs. Maintained OSS. | [docs.gtk.org](https://docs.gtk.org/glib/logging.html) | Structured key–value logging. Debug messages are dropped unless `G_MESSAGES_DEBUG` is set. Private data is redacted in a wrapper or in "the single log writer function". | "Should" guidance only; nothing enforces it. |
| S11 | Mozilla `CrashAnnotations.yaml`. Maintained OSS. | [GitHub](https://raw.githubusercontent.com/mozilla/gecko-dev/master/toolkit/crashreporter/CrashAnnotations.yaml) | Every annotation is declared in a registry with a type and a scope. `"client"` means "never sent remotely (the default if unspecified)". | Firefox-specific; the review process is not described in the file. |
| S12 | OpenTelemetry `error.type` (Stable). Maintained spec. | [opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/attributes-registry/error/) | "SHOULD be predictable, and SHOULD have low cardinality". Instrumentations should document the list. `_OTHER` is the fallback. | Telemetry convention; adoption here would be partial. |
| S13 | Sentry Python *Sensitive data*. Maintained OSS docs. | [docs.sentry.io](https://docs.sentry.io/platforms/python/data-management/sensitive-data/) | Scrub "before it is sent… sensitive data never leaves the local environment". Server-side scrubbing happens after receipt. | Relies on denylists. I recommend an allowlist instead (S11, S8). |

---

## 3. Adoption proposals (all drafts)

### OPUS03-ER-01 — Closed, typed set of user-facing outcome messages (priority P1)

- **Why:** G1 and G2. S4 #9, S8 (stable reason separate from the message), S12 (`_OTHER` fallback), S7 (outcome class implies the next action).
- **Maps to:** ELM-ARC-007, ELM-UI-007, ELM-UI-010, `INTERACTION.md:41` ("Refused menus remain open with the reason and reachable next action") and W04 (typed internal messages).
- **Classification:** a **refinement** of UI text and typing. The native reason-*code* enum is **new**, and that protocol change belongs to the typed-events reviewers.
- **Requirement:** every visible status comes from a closed, versioned catalog keyed by (outcome class, operation, next action). Unknown is worded as "unconfirmed", never "failed". Cancelled has its own text. Reducer, decoder and native free-text strings are never shown.
- **Implementation choice (not a requirement):** an Elm `Notice` custom type with one `noticeText` function, composed when rendering rather than by string concatenation. Native sends `reasonCode`, and any free text goes to diagnostics only.
- **Alternatives considered:** localize the native strings (rejected: unbounded and leaks implementation detail); keep strings but filter them (rejected: fragile).
- **Cost:** touches Shell, Surface, Menu and the replay oracles, and needs requalification of compiled assets.
- **Validation:**
  - An exhaustive replay of every (status × operation × surface mode) shows a catalog entry for each.
  - A mutant that puts any `Effects.apply` refusal literal into output fails.
  - The "Connected The window…" sentence regression has a test.
  - Cancelled is covered.

**EARS:** The Elm desktop SHALL derive every user-visible action status from a closed, versioned outcome catalog keyed by outcome class, operation and next action, and SHALL NOT display decoder, reducer or native free-text reason strings. IF a native refusal code is not in the catalog, THEN the Elm desktop SHALL display the class-generic Refused text with a reachable next action and record the unmapped code in bounded diagnostics.

**Scenarios:**
- GIVEN a Pending Activate WHEN a correlated `Unknown` outcome arrives THEN the status says the change could not be confirmed and offers refresh/observe, the text does not contain "failed" or "refused", AND no `window-effect` command is emitted.
- GIVEN a menu Refused outcome whose native reason contains `lifetime=42 EINVAL` WHEN the popup renders THEN it shows the generic refused text and a next action, the raw reason is absent, AND diagnostics count `_OTHER`.
- *(Negative)* GIVEN `notice="Connected"` WHEN a Refused receipt settles THEN the status is one well-formed catalog sentence with no concatenated suffix.
- *(Negative)* GIVEN `Act` is refused locally because the target is locked THEN no internal literal ("Locked or unmapped target") appears.

### OPUS03-ER-02 — One announcement per outcome identity, and Unknown is never hidden (priority P1)

- **Why:** G1 and G3. S5 (atomic status re-reads), S6 ("too chatty"), S1 (outcome identity is the call ID).
- **Maps to:** ELM-UI-010, ELM-UX-026, and W08 ("one announcement owner/outcome identity").
- **Classification:** largely a **duplicate** of W08. The precedence rule that Unknown cannot be masked is a **refinement**. I vote to merge it into W08.
- **Requirement:**
  - The controller alone emits announcement events keyed by (binding, effect protocol, intent, outcome class). Projections only render them.
  - No key is ever announced twice.
  - Unknown, Exhausted and recovery-failure states rank above informational and launch messages.
  - The per-control "Awaiting native confirmation" (`Surface.elm:98`) stays until a release is validated.
  - Announcements are polite by default (`INTERACTION.md:43`).
- **Implementation choice:** one live region on the surface that owns focus, with the other surface showing the status visibly but not as a live region. An alternative is a per-surface region gated by an announcement token.
- **Rejected alternatives:** `role=alert` for Unknown (breaks the polite default policy); toasts (deferred).
- **Cost:** a small model change, plus an assistive-technology session.
- **Validation:**
  - CPU replay counts exactly one announcement event per key.
  - A masking test covers "Submitted" followed by a window Unknown.
  - An Orca/braille transcript is taken under P5-ELM-QA-019.

**EARS:** WHEN a correlated outcome changes class, the controller SHALL emit at most one accessible announcement for that outcome identity across all shell surfaces; WHILE any operation remains Unknown, the shell SHALL keep that unconfirmed state perceivable on its control and rank it above informational status.

**Scenarios:**
- GIVEN an Unknown record re-announced after a same-view reconnect (`reconciliation.py:28-31`) WHEN the identical frame arrives again THEN no second announcement occurs.
- *(Race)* GIVEN bar and popup both mapped WHEN one Refused outcome settles THEN the assistive-technology transcript contains it exactly once.
- *(Negative)* GIVEN launch status "Submitted" WHEN a window operation becomes Unknown THEN the status shows the Unknown message, not "Launch submitted."

### OPUS03-ER-03 — Bounded, privacy-preserving diagnostic records with stable reason codes (priority P1)

- **Why:** G4, G5 and G6. S3 (bucket IDs, permanent tags, minimal data first), S8 (stable reason/domain), S9 (MESSAGE_ID, PRIORITY), S10 (redaction in one writer), S11 (declared registry), S12 (low cardinality).
- **Maps to:** W11, ELM-DEL-017 (redaction; task P2-ELM-DEL-017), ELM-ARC-015 and ELM-ARC-016 (bounds and reserved control capacity), ELM-QA-012.
- **Classification:** the record schema and store are **new**; the rest is a **refinement** of W11.
- **Requirement:**
  - Each component (Elm controller, Python adapter, native host) records refused, rejected and uncertain boundary events.
  - Records live in a bounded store and use an allowlisted schema: stable reason code, component, severity, native monotonic time, authority counters, and a counter per rejected-frame kind.
  - Excluded: titles, application IDs and argv, paths, secrets, drafts, pixels and payload bodies.
  - When the store is full, a drop counter increments. Recording never delays control, receipt or retirement traffic.
  - Diagnostics are never authority: they cannot trigger effects or reconciliation.
- **Implementation choice:** journald structured fields with one MESSAGE_ID per reason code (S9). Native uses a GLib structured log writer that applies redaction (S10). Python emits structured JSON on stderr. Elm keeps counters in its model so replay can compare them. No native safety logic moves to JavaScript.
- **Drop policy (open):** keep the first cause plus a recent ring, or keep newest only. To be decided in round two.
- **Budgets:** capacity and record size come from the frozen budget contract (ELM-QA-021, ELM-REV-021 `budgets.json`). The task is to measure under the S02 and soak workloads and freeze the values before acceptance. I propose no numbers.
- **Validation:**
  - ELM-DEL-017 synthetic-secret injection (into titles, app IDs, paths and malformed frames) finds zero matches in the store and the journal.
  - Fuzz counters exactly equal the number of injected frames.
  - Whole-tree memory stays inside the frozen bounds (ELM-QA-023).
  - Replay state and commands are unchanged apart from the diagnostic counters.

**EARS:** The shell SHALL record each refused, rejected or uncertain boundary event as an allowlisted diagnostic record with a stable reason code in a bounded per-component store, excluding titles, application arguments, paths, secrets, draft contents and pixels. IF a diagnostic store is full, THEN the component SHALL increment a dropped-record counter without delaying or refusing control, receipt or retirement traffic.

**Scenarios:**
- GIVEN a malformed `effect-outcome` frame WHEN it is rejected THEN the model and commands are unchanged AND `REJECTED_FRAME{kind=effect-outcome}` increments with no payload stored.
- *(Race)* GIVEN a flood of diagnostics WHEN a cancellation arrives THEN it is processed within its original frozen deadline and the drop counter is accurate.
- *(Negative)* GIVEN a snapshot whose window title carries a synthetic secret and which fails to decode THEN the secret is absent from every diagnostic sink.

### OPUS03-ER-05 — Report the restart class, and give terminal phases a reachable recovery (priority P2)

- **Why:** G7 and K4. S2 (start = recover), S1 (incarnation IDs separate restarts), S7 (FAILED_PRECONDITION: no retry until state is fixed).
- **Maps to:** ELM-UI-007, ELM-ARC-013, ELM-ARC-014, ELM-QA-012, ELM-REN-030 (conditional), restore38/recovery34, v814 `HANDOFF.md:27-31` (816), and W01/W02 exhaustion.
- **Classification:** the reporting part is a **refinement**. The recovery action duplicates 816/W02, so merge it there.
- **Requirement:**
  - On resume, report which restart happened (frontend reload, adapter, host, or compositor lifetime change), derived from the existing lifetime, epoch and binding counters, together with the number of operations still Unknown.
  - Resume goes through the normal startup reconciliation path and replays nothing.
  - Exhausted and reconciliation-full states offer a recovery action reachable by keyboard and assistive technology. It preserves durable Unknown history, watermarks (`Effects.elm:114-117`) and original deadlines.
- **Cost:** reuses the existing protected fault harnesses (`recovery_fault.py`, `host-fault.h`).
- **Validation:**
  - Kill at the existing stages (`after-native-receipt-before-durable-settlement`, `after-durable-admission…before-broker-write`), then check the reported class and Unknown count.
  - No effect is sent before release.
  - Deadlines are unchanged.
  - restore38/recovery34 are rerun.

**EARS:** WHEN the shell resumes after a frontend, adapter, host or compositor-lifetime restart, the controller SHALL report the restart class and the count of operations still Unknown through the normal startup reconciliation path without replaying any Unknown operation. WHILE the controller is Exhausted or reconciliation history is full, the shell SHALL present a keyboard- and AT-reachable recovery action that preserves durable Unknown history, allocation watermarks and original deadlines.

**Scenarios:**
- GIVEN the adapter is stopped after a native receipt and before durable settlement WHEN it restarts THEN the status reports one unconfirmed earlier change, the control stays blocked until a validated release, AND no `window-effect` is sent.
- *(Race)* GIVEN the compositor lifetime changes during a frontend reload THEN the class is "compositor lifetime change", and Unknowns under the old lifetime are reported as historical and not retried.
- *(Negative)* GIVEN Exhausted WHEN recovery is invoked THEN request and generation counters never go below the recovered watermarks.

### OPUS03-ER-04 — User-initiated, local-only diagnostics export (priority P3; deferrable)

- **Why:** S3 (consent defaults to no; collect the minimum first), S11 (`client` scope by default), S13 (scrub before data leaves the device), S9 (catalog documentation).
- **Maps to:** ELM-DEL-017 and ELM-UI-009. No existing workplan item covers it.
- **Classification:** **new**.
- **Requirement:**
  - Only an explicit user action creates a local bundle, made of ER-03 records plus build, source and ABI hashes.
  - The user sees a summary of its fields first.
  - Nothing is ever transmitted.
  - Export works while Detached or Exhausted and never changes authority state.
- **Rejected alternative:** automatic or remote upload.
- **Cost:** a new UI control, file writing through the native/Python side, and a check of the bundle schema against the allowlist.
- **Validation:**
  - Secret-injection scan of the bundle.
  - Bundle fields are a subset of the allowlist.
  - Reachable with keyboard and assistive technology.
  - Export during reconciliation emits no messages.

**EARS:** WHEN the user requests a diagnostics export, the shell SHALL write a local bundle containing only allowlisted diagnostic fields and build/source identities after presenting its field summary, and SHALL NOT transmit it.

**Scenarios:**
- GIVEN Exhausted WHEN export is invoked by keyboard THEN the bundle is written.
- *(Race)* GIVEN a reconciliation is in progress WHEN export runs THEN no effect or reconciliation message is emitted and the release result is unchanged.
- *(Negative)* GIVEN injected secrets THEN none appear in the bundle.

---

## 4. Rejected and deferred alternatives

- **Rejected: automatically retrying Unknown operations with idempotency keys** (gRPC-style UNAVAILABLE retry, S7; restart/retry, S2). Window effects are not idempotent, and S2's own limitation section says so. This also breaks the scope rules.
- **Rejected: moving reason mapping or redaction into JavaScript.** Redaction belongs in each component's writer (S10), and native safety stays native.
- **Rejected: `role=alert` or assertive announcements for Unknown.** They conflict with `INTERACTION.md:43`.
- **Rejected: denylist-only scrubbing** (Sentry's default, S13). Allowlists are safer here (S8 metadata, S11 registry).
- **Deferred: remote crash or telemetry upload in WER or Sentry style.** It needs a consent and privacy policy that is outside this baseline.
- **Deferred: privacy-preserving aggregate telemetry.** I verified no primary source for it in this pass.
- **Deferred: distributed tracing in Dapper style.** I saw only the abstract (sampling, low overhead). This is a single host and the gain is unproven.

## 5. Open research questions

1. Does WebKitGTK expose `role=status` live regions through AT-SPI in a way Orca speaks once per change, and do two surfaces double-announce? This needs the P5-ELM-QA-019 sessions.
2. Is journald available and readable in the target session, and should shell diagnostics stay out of the system journal altogether?
3. Is the native menu `Refusal` text already drawn from a fixed set? I could not tell from the Elm side.
4. The frozen baseline does not state a localization requirement. If ER-01 is adopted, it would need a scope decision.
5. Drop policy for ER-03 (first cause vs newest) and its budgets. These must be measured and frozen under ELM-QA-021, and no number is proposed here.

## 6. For the second round

Merges I would vote for: ER-02 into W08, and the recovery action in ER-05 into 816/W02. ER-01 and ER-03 are the substantive new obligations. ER-04 is the one I would accept deferring. Agreement between independent reviewers on these points still needs explicit votes, and any disagreement should stay on the record.
