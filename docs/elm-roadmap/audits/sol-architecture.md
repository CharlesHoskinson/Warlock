# Sol architecture audit

Input SHA-256: `9b7f47af2664ab40322cf40241d04f69348a0a6064b20b1cec34a37713436b6b`.

Verdict: Changes required to reconcile two normative layering contradictions; core native/Elm ownership and GPU qualification architecture is otherwise defensible at planning level.

Counts: critical 0, high 0, medium 2, low 1.

## Findings

### SOL-A-001 — medium

Requirements: ELM-GNO-002, ELM-LAY-001, ELM-KDE-005.

Location: docs/elm-roadmap/requirements.json / ELM-GNO-002; LAYERING.md / Proposed native authority.

The normative inactive-workspace rule omits the nonsticky qualification used by ELM-LAY-001, although LAYERING.md explicitly supports workspace-independent visibility. A supported sticky window retains an originating workspace that becomes inactive: GNO-002 demands its exclusion while LAY-001 and the documented visibility policy permit it. Both generated contracts cannot describe that same scene consistently. KWin Window::isOnDesktop explicitly accepts isOnAllDesktops before testing desktop membership.

Correction: Qualify GNO-002 with inactive nonsticky workspace, or define eligibility in terms of absence from the current output effective workspace set including explicitly supported sticky state. Keep minimized exclusion unconditional. Add one sticky workspace-switch scenario and a separate pinned-but-nonsticky exclusion scenario; propagate the correction into the registry and generated OpenSpec.

Blocks planning: true.

### SOL-A-002 — medium

Requirements: ELM-REN-015, ELM-GNO-006, ELM-KDE-001.

Location: docs/elm-roadmap/requirements.json / ELM-REN-015; LAYERING.md / Proposed native authority.

REN-015 unconditionally requires painted ordering, hit testing and committed focus to agree for overlapping floating maximized windows. The same packet explicitly permits painted input-transparent surfaces and modal redirection. For two overlapping MAX windows with the upper input region excluding the clicked point, the painted upper surface remains visible but hit testing correctly chooses the lower one; its modal can be the committed focus recipient. REN-015 would fail that correct native result, while GNO-006 explicitly allows it. KWin findToplevel walks the stack but then applies hitTest, demonstrating why a stack alone does not equate these three outcomes.

Correction: State that paint and hit traverse the same committed constrained scene with documented input-region and transform exceptions, and that a qualifying activation commits the documented native modal recipient. Add MAX overlap fixtures for input-transparent regions and modal redirects alongside the ordinary pixel/click agreement case. Avoid requiring the currently focused window to equal the top painted surface absent a focus-triggering action.

Blocks planning: true.

### SOL-A-003 — low

Requirements: ELM-ARC-005, ELM-ARC-006, ELM-ARC-008, ELM-KDE-009.

Location: docs/elm-roadmap/ROADMAP.md / Architecture and data flow; requirements.json / expected-native-revision guards.

The packet requires exact expected native revision matching, and describes one scene revision containing geometry and focus, but does not define revision scope or a liveness rule after safe rejection. If unrelated window B changes geometry between every snapshot and A activation, every A intent can be refused even though A incarnation, eligibility and relevant constraints remain stable. Safety can pass while the requested reliable click-to-focus never completes. This is a missing progress requirement, not a claim that a future implementation already behaves this way.

Correction: Propose new EARS coverage: WHEN an otherwise valid user activation is refused solely for a stale scene revision, the native authority SHALL reconcile against current target/output/family dependencies and produce a bounded terminal result without requiring unrelated scene activity to stop. At the P0/P2 protocol gate choose global or dependency-scoped revisions and a safe native revalidation policy; test continuous unrelated geometry changes and real target invalidation. Do not blindly refresh and replay a stale mutating request.

Blocks planning: false.

## Coverage and non-findings

The ownership boundary is explicit and sound: Elm owns presentation, desired state and policy proposals; native components own scene commitment, input, capture buffers, GPU objects, motion scheduling and physical-presentation evidence. Cross-output views receive projections rather than independent effect authority. Cancellation checks at final mutation/submission boundaries, unknown-outcome reconciliation, distinct commit/presentation receipts, epoch invalidation, source-incarnation leases and generation-specific resource retirement address the principal asynchronous hazards. The renderer contribution explicitly separates logical window retirement from temporary source-context shutdown.

Mutter/KWin evidence is presented as an architecture reference rather than a copied Windows policy. The packet correctly distinguishes MAX from true fullscreen, rejects cached priority as eligibility, treats effect visuals separately from application input, and requires explicit per-output fullscreen/pin decisions. The inherited matrix and P0 precedence freeze are valid gates; future native acceptance being pending is not a defect.

GPU and WebGPU claims are appropriately bounded. Hardware discovery does not establish accelerated host rendering; secure-origin and sandbox qualification, actual hardware classification, deterministic workloads, independently observed presentation, bounded GPU ownership, device-loss generation invalidation, measured copies/fences and fallback admission are explicit. No zero-copy claim or unsupported Elm GPU binding is made. Capture transport and copy budgets remain owned experiments with stop conditions rather than asserted capabilities.

The cycle-refusal and reserved-control-capacity contracts require careful lifecycle/overload implementation, but the frozen packet does not establish an erroneous implementation; they are not findings here. Numerical encoding, queue budgets, host choice and native interoperability are explicitly deferred to owned phase gates.

## Limitations

Offline planning/source audit only. Verified packet SHA-256 and all 36 frozen draft-manifest artifact copies. Examined complete frozen packet and registry, plus targeted retained KWin input/window/workspace and Mutter window source. Did not execute native GUI, validate GPU paths, exhaustively review whole upstream compositor corpora, or claim implementation acceptance.
