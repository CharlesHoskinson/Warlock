# Held pointer cancellation on parent transport loss

AQ120 fixes the reproduced stuck-button state after a held press loses its parent
display connection. Only Wayland.cpp changes relative to AQ105. It balances
previously admitted buttons before pointer retirement, clears private records
before callbacks, and retains pointer ownership through reentry. The owning
library builds with all parent headers and exports intact.

The accepted tuple is Core89, plugin90 where applicable, and AQ120. Native GTK
receipts and the read-only owning Core observer verify balanced releases and
cleared held state for all seven nonempty left/right/middle combinations.
Original deadlines, PID/start/socket joins, kernel poll-source retirement,
post-fault stale-input refusal and ordered normal cleanup remain intact.

The qualification executed 909 native checks: the original held-loss oracle34,
seven mask executions35 each, and the original normal input159, multi-window51,
capability-burst35, geometry96 with seven pixel stages, menu68, cursor195 and
unheld-loss26 regressions. These are check executions, not unique scenarios.
The actual C++ helper152 and transport63 checks, twelve compiled mutation
controls, ten explicitly selected Quint scenarios, 1,000x40 sampled traces and
seven model mutation controls passed separately.

The failed V115 fixture, V116 real stuck-state reproduction, V117/V118 model
attempts and V129 freezer attempt remain. V130 corrects only the freezer's
selection of the original cursor report field `sourceInputs`; native code,
reports and acceptance oracles are unchanged. The freezer attempt retains its
exact source and observed error summary.

The acceptance manifest is
[acceptance-manifest.json](../../../implementation/elm-held-cancellation-acceptance-v130/acceptance-manifest.json),
SHA-256 `615501960a091d87162aebc1242f02f367f1d96ad423ffe8484edfc5d646b32d`.
The source/build component is
[AQ120](../../../implementation/elm-parent-held-cancellation-v120/component-manifest.json),
SHA-256 `d85ea29ed83015dc3a4180074386095c9d62b2452cab6c968e6957b7128f315d`.
The library SHA-256 is
`dea6036bc81a4798156e4e8672d99dd28679baa3dac8a7825893f07f46514a03`.

Full S01-S16 and applicable C00-C06 acceptance remains open. Continue held-key
loss, coherent shared-GUI integration, hardware/device and accessibility/IME
qualification, resource budgets, representative journeys, and deployment/rollback.
This change installs or activates nothing on the main desktop.
