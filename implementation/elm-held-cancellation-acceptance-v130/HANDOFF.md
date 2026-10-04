# Held-button cancellation on parent connection loss

The original AQ105 native held-loss test removed input devices but left Core89
reporting a held button. V116 retains that failure with normal cleanup. V115
retains the earlier fixture failure caused by GTK's extra double-click notification;
the subsequent physical-event oracle keeps that notification in the evidence.

AQ120 changes only `src/backend/Wayland.cpp` relative to frozen AQ105. On parent
transport failure it cancels previously admitted button presses before retiring
the pointers. It clears the private held records before callbacks and holds a
strong pointer snapshot through callbacks. It emits no new presses and emits
one frame per pointer with cancelled buttons. All prior failure, publication,
output, scheduling and poll-source fences remain. Public headers and every
AQ105 exported symbol are preserved by the complete library build.

The actual cancellation helper passed 152 C++ checks and five compiled mutation
controls. The original transport bodies passed 63 C++ checks and seven mutation
controls. Their transport fixture uses a typed no-op cancellation stub; the
separate actual helper tests and native campaigns establish the new wiring.
The corrected held model passed ten explicitly selected Quint scenarios,
1,000 sampled traces of up to 40 steps, and seven typechecked mutation controls.
Quint models one logical pointer and three button identities. C++ checks cover
callback reentry, strong ownership, multiple pointers and the 32-slot ledger;
this is separate evidence, not a model refinement proof. Failed V117/V118 model
attempts remain unchanged. V119 and AQ120 use the same corrected model source.

The owning native tuple is Core89, authority plugin90 where applicable, and the
AQ120 library. The read-only held-state observer114 was compiled against all
694 owning Core89 headers. The original six-second observation deadlines remain.
The fixture destroys only the exact PID/start-identified private child connection
while its press is held, before balancing the surviving parent's seat. The child
and parent processes remain alive. GTK receives exactly one balancing release
per admitted held button; Core clears its held state; devices, nested outputs and
the actual kernel poll registration retire. Later parent input causes no stale
child presses or revived holds. All seven nonempty left/right/middle masks pass.
Clients, observer/plugins, child, parent and private bus exit in order.

| Native campaign | Check executions |
| --- | ---: |
| Original held-loss oracle | 34 |
| Seven held masks, including exact per-button GTK releases | 245 |
| Original input and held capability/focus changes | 159 |
| Multiple windows | 51 |
| Capability burst | 35 |
| Geometry, including seven pixel stages | 96 |
| Menu | 68 |
| Cursor | 195 |
| Unheld parent loss | 26 |
| Total | 909 |

These are repeated check executions, not 909 unique scenarios or completed
requirements. Unchanged regression runners retain their historical baseline
scope strings; each derivative's frozen AQ descriptor and actual mapped-library
evidence identifies AQ120. The library SHA-256 is
`dea6036bc81a4798156e4e8672d99dd28679baa3dac8a7825893f07f46514a03`.

Held-key cancellation, hardware/device behavior, shared GUI integration, the
full S01-S16 and applicable C00-C06 gates, accessibility/IME, resource budgets,
user journeys and deployment/rollback remain open. Nothing was installed or
activated on the main desktop. Continue with held-key loss and share the AQ120
descriptor with the existing integration owner after its source review.
