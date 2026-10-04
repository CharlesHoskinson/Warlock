# Current schema5 EOF and receipt fixture

This is a fresh source-only fixture. Acquisition is fixed to V144 actual captured adapter at `qa/build-1791121323616998481`, verified against V145 manifest SHA `65d6252dcd0d4b90ece6d67982e88b31bc010796b44c66483b0398ecc9d42fd8`. Core89/plugin90/AQ105 metadata is pinned through V336. Historical fixtures and all production source remain unchanged. Native assembly against newer source380/387 must independently bind that coherent source/build and verify the adapter/native journal bytes; this fixture does not transfer frontend native acceptance.

`qa/relay.py PRIVATE_CONFIG` accepts exactly the original two profiles:

```json
{"profile":"broker","authorityConfig":"/absolute/private/authority.json","controlDirectory":"/absolute/private/relay-control"}
```

```json
{"profile":"receipt","receiptConfig":"/absolute/private/receipt.json","controlDirectory":"/absolute/private/relay-control"}
```

The private receipt configuration has `authorityConfig`, `controlDirectory` for its own hold gate, `incarnation`, `effectOperation` (`maximize` or `restore-geometry`) and optional `selectorOrdinal` (1 or 2). The unchanged parser supplies no arbitrary code/argv/backend override. The broker profile selects the exact captured current daemon; the receipt profile selects this fixture's fixed `qa/broker-entrypoint.py`. `relay.close_stdin(control)` and `wrapper.write_release(control)` preserve original owned actor/gate PID/start/inode/flock checks.

V92's actual pump, frame forwarding, three-second EOF deadline, late-completion rejection, child normal stdin close and exact exit-status helpers are AST-identical. V82 ReceiptHold, supervisor, release writer and wrapper main are AST-identical; the host-compatible entrypoint is byte-identical. Receipt timeout remains five seconds; native transport remains three seconds; native scenario deadlines remain six seconds. No synthetic outcome, observer effect or native retry is added. The wrapper holds one actual matching Committed full receipt, forwards authenticated events/observations and passes Unknown/Refused unchanged. EOF with an unreleased held receipt fails instead of declaring success.

Protected CPU evidence is separate:

- Real owned relay subprocess/pipe controls:19; absolute late-completion with unsafe ancestor control:7; accepted-input cut/output backpressure edges:7.
- Closed current profiles/parser/source and unchanged AST:24.
- Current C durable schema5 host admission plus actual RecoveryStore:18. No native effect is dispatched and no receipt is fabricated. The same report verifies and replays the exact recorded real V100 receipt bytes (hash from that frozen native report), explicitly historical. Its actual current Pending store remains Pending; historical Committed replay never settles that current store. Private release emits the unchanged recorded receipt exactly once.
- Synthetic receipt selector52 and supervisor45 unit checks validate receipt filtering, Unknown forwarding, private release correlation, timeout and owned watcher/process cleanup. These counts prove CPU fixture behavior, not native effects or pixels.

All earlier failures are preserved. Old tests assume V74 manifest metadata, lack mandatory schema5 durable host admission, or expect the older policy to reject Unknown rather than forward it. `qa/legacy-staged-test.py` and `qa/legacy-receipt-test.py` retain those incompatible oracles; their failure snapshots are not patched into green native evidence. Selected current tests have explicit scopes and unchanged original pump/selector implementation.

Actual kernel SO_PEERCRED/core/session/runtime mapping remains enforced by the pinned production endpoint and owning V336 host. This packet does not claim a new native peer authentication run. Full native08 requires exact real actor normal childExit0/stdinClosed, C host normal0 and Elm Detached before physical reconnect with no old intent replay. Full09 requires one real current Committed receipt, authenticated notifications while Pending, actual ACK/buffer/pixels, exact original release and current full-key ledger behavior. Full10 retains normal target quit, original six-second deadline and real browser/controller disposition recovery. Independent primary Escape/publication fixes and coherent source assembly are separate prerequisites.

Native acceptance, full08/09/10 acceptance and release are false. No GUI, installation, upstream edits or Quint logic were performed.
