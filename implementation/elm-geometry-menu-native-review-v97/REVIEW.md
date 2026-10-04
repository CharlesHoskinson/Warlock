# V96 source review

This is a read-only review of the exact files in `reviewed-inputs.json`. No native
GUI or subprocess campaign was run, and no V96/V90/V82/V91 source was changed.
Any later source correction requires a fresh reviewed hash. Full09, native and
release acceptance remain false.

The principal receipt-hold design is coherent. ActorA's ordinal2 selector forwards
the first RestoreGeometry06 receipt. Reconnect08 proves the exact owned relay and
child PID/start, stdin closure, child normal0, host-observed relay normal0 and both
original actors retired before replacing either private configuration. ActorB is
fresh and uses ordinal1; the old live actor cannot be retargeted. The V90 profile
launches only the exact held V82 entrypoint. V82 counts distinct full keys and never
counts Unknown, Refused or other targets/operations. Full09 uses no SIGSTOP: the
older dormant `settle_menu(held=True)` branch is not invoked by any scenario.

Full09 correlates the private held marker's wrapper owner with actorB, and its
protocol2, full original binding and every intent field with the actual issued
command. It checks Elm Pending, outstanding1/registry1, closed menu and absence of
the matching outcome while the native window has already restored. Client evidence
requires a new buffer, matching configure/ACK, native geometry, and independent
serial-derived interior RGB. The release helper validates the exact original key
and sends the original packet once; the runner compares the delivered packet and
expects definitive ledger/registry retirement plus separate fresh Elm facts.

The observer cannot rebind the Elm broker. Actual V75 authority sessions are keyed
by authenticated peer PID, validated process start, and independent frontend epoch.
The observer runs in the runner process; the broker runs in the receipt child.
Observer hello/geometry-attach touches only that observer session, and its subsequent
call requests facts without invoking an effect. Its snapshots are separately
labeled and never injected into Elm. Add an explicit assertion that observer and
Elm session bindings differ while lifetime matches to make this evidence direct.

Notification evidence is stronger than an arbitrary injected hint. The captured
broker executes handle_request serially; the intercepted matching receipt is
written to held.json before returning from that operation. Only then can its main
loop forward native event notifications. The runner requires a real host-refresh
after the issued command while the exact outcome remains absent and Pending stays
live. No synthetic host-refresh or native receipt is produced by the runner.

Two runtime obligations need correction or explicit qualification before launch:

1. The independent observer's facts RPC starts its own three-second transport
   deadline regardless of how much remains of scenario09's absolute six seconds.
   The runner's wait checks time after the predicate, so it cannot falsely accept
   a late result, but the blocked call can overrun the original scenario duration.
   Bound that QA observer call by the remaining original deadline without resetting
   or extending the frozen endpoint's maximum transport budget.
2. Cleanup proves normal fixture quit, but does not explicitly wait for native
   fixture clients to retire before unloading the plugin. Observe the owned native
   clients gone, then unload; process exit alone is not the retirement readback.

The source currently does not claim full contract or roadmap completion. Native
acceptance additionally requires the actual frozen tuple's normal lifecycle,
unchanged scenario deadlines, original scenario identities, pixel/input receipts,
artifact closure and cleanup to pass. These source findings do not replace that run.
