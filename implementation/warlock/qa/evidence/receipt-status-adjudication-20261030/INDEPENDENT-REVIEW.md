# Separate retained-trace adjudications for ARC007

Independent read-only adjudication of existing executed evidence; no new QA, implementation, model execution or changed oracle. These three findings extend the earlier explicitly limited receipt-committed review only after separate given/when/then inspection. Cancelled remains excluded. Whole ELM-ARC-007 and actual native delivery remain unaccepted.

Evidence is the same actual optimized production bridge run: receipt-output-candidate-cpu-1793333313793450484/report.json SHA256 2a667210050298c85af095bc61d0bdfe580750124ac36d77a5cb421e4932d807; receipt-output.json SHA256 97776dd3fe05a68f14805e589afbbc7720daf5e5271be8395466712459a3f1db. The complete representative result is index 0, seed 689452769. Original scenario wording is unchanged in docs/elm-roadmap/requirements.json. Matching source, build, bounded model and failure-history identities are recorded in FINAL-DISPOSITION.md, SHA256 c5515e797b48381203510d2b322c27401c5a8a01a5ab6d484fefbff9e1fff993. Root published the full source as a4168e633 and committed the prior bounded acceptance separately; these findings require their own ledger recording, not reinterpretation of that prior verdict.

## architecture-007: ACCEPTED through bridge fixture

Given: a request whose connection drops. The worker actually issues Minimize through captured production controller input. `case.pending` records full request 1/generation 1/incarnation 1/context identity, status Pending, matching issued binding and unresolved record; its reachability assertion confirms exactly one window-effect emitted.

When: its final effect cannot be proven. The disconnected branch starts directly from that Pending model and passes only protocolVersion 3 / kind host-disconnected through Desktop.Incoming and Shell. It does not apply any terminal receipt or reconciliation proof before recording `case.disconnected`. This establishes the fixture's unproven final outcome, without pretending to observe a physical compositor disconnect.

Then: its state is Unknown rather than Committed. The retained disconnected transaction has the same full identity and protocol, status Unknown, observed connected=false, and matching unresolved Unknown; issued correlation remains retained. The executed `disconnectMakesUnknownWithoutEffect` check requires Unknown and zero emitted window mutations. The explicit retained string Unknown also excludes Committed. Later receipt branches are separate model values and do not precede this recorded checkpoint. The native-or-bridge verification permits this actual bridge fixture; no GUI prerequisite is added.

## receipt-pending: ACCEPTED through bridge fixture

Given: a request with unique identity and a fixture for Pending. The actual initial captured action creates request 1/generation 1 and recorded Pending. A second non-vacuous fixture transition is also retained: `case.projected` contains the original unresolved and issued request; `case.newer` is produced by another captured production action for incarnation 2 on output 2.

When: the fixture transition occurs. The second action actually emits one new window-effect. The executed newerDifferentIncarnationActuallyPending check requires a different full intent and Pending status, with the old request still represented in both unresolved and issued collections.

Then: the correlated request has exactly Pending and no other request changes. The retained newer transaction has request 2/generation 2/incarnation 2/output 2/revision 2, protocol 1 and Pending; its new unresolved and issued records match. Independently comparing the complete old-key unresolved and issued entries in projected and newer finds value equality, including old status, full intent, protocol and binding. There is a real other request, not an empty comparison. Shared current-transaction selection and allocation counters move to request 2 as part of creating it; this is not a mutation of request 1's retained records.

The full-old-record equality is an independent adjudication of the already retained representative trace, not a named assertion newly run across all 200 variants. The executed check establishes old-record presence across those variants. Do not inflate this into 200 newly executed preservation assertions or arbitrary interleaving coverage. One actual complete fixture trace meets the literal scenario oracle.

## receipt-refused: ACCEPTED through bridge fixture

Given: a unique request and a Refused fixture. `case.receipts.Refused.wire` carries the exact full original intent, binding and effect protocol with status Refused, through the actual NativeOutcome/Shell/Effects production route.

When: that fixture transition occurs. Same-authority, post-output-change and post-disconnect branches receive this exact wire outcome. The recorded current transaction becomes Refused and only its terminal unresolved/issued entries are removed.

Then: the correlated request is exactly Refused and no other request changes. Those exact-status assertions pass. A separate branch receives the old Refused outcome while a different request is Pending: the complete newer transaction, all other unresolved and issued records, observed scene and allocation counters remain equal, with zero new window mutation. The terminal duplicate is a no-op and all eleven malformed/foreign correlation controls pass. This combines actual exact-status evidence with non-vacuous preservation of another request, as the prior Committed adjudication did. The fixture reason string applied is retained as supplied; this verdict concerns the explicit Refused state and correlation, not a real native refusal reason or native operation result.

## Limits and remaining status

These are three individually justified fixture acceptances from already executed evidence, not bulk inference from a green check count. No new runtime observations occurred during review. They do not accept receipt-cancelled: the public NativeOutcome shape does not admit that status and this trace's cancelledShapeDiagnosticOnly is not a successful cancellation transition. The full retirement/action/geometry recovery-release proof remains outside coverage. No whole ARC007, native composition/runtime, accessibility, delivery or release acceptance follows. Preserve all original source, baseline and failed-compile history and avoid relabeling the fixed-route parameter variation as randomized event-interleaving verification.
