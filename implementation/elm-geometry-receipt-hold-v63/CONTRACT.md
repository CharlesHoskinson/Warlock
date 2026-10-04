# Private receipt-delivery hold fixture

This QA-only wrapper uses the frozen V59 captured broker, with its original endpoint deadline, framing and negotiation behavior. It holds one real `Committed` effect-protocol-2 `maximize` outcome for the supplied incarnation after native execution has returned. Refresh notifications and unrelated frames continue through the broker. This exercises delayed delivery to an Elm Pending transaction; it does not establish native Pending execution, native Unknown recovery, or complete roadmap acceptance.

The parent harness creates a canonical owned directory with mode 0700 and an owned regular single-link `gate.json` with mode 0600 containing `{"action":"hold"}`. The gate inode must remain unchanged. Launch under the protected QA scope:

```
python3 -B qa/wrapper.py run --control-directory /absolute/private-directory --incarnation DECIMAL --config /absolute/broker-config.json
```

When `held.json` appears, it records the wrapper PID/start-time, original full binding, protocol, intent and receipt. Release using the public helper, which verifies process identity and writes the same gate inode under a nonblocking exclusive flock:

```
python3 -B qa/wrapper.py release --control-directory /absolute/private-directory
```

The wrapper forwards the original receipt once, unchanged. Both captured records and gate packets are bounded to 4096 bytes. Release requires the exact original full binding, intent, protocol and wrapper process identity. Duplicate release, malformed packets, file replacement, timeout and unreleased EOF fail closed. A watchdog deadline of five seconds is independent of gate-lock contention. Timeout interrupts the broker main thread through a private SIGUSR1 handler; selector/socket contexts unwind, the watchdog stops, one `host-disconnected` frame is emitted and exit status is 1. Normal released EOF exits 0. The parent retains its original whole-transition six-second guard and owns process cleanup; this fixture does not extend it or automatically release/retry.

`qa/test.py` tests the actual wrapper and supervisor with synthetic transport receipts and CPU subprocesses. It verifies forwarding during a hold, exact unchanged release, schema and identity rejection, locked-gate timeout, malformed release, EOF and watchdog cleanup. These tests do not open a native compositor or prove native execution or rendering. Existing V59 broker framing limitations remain inherited; this wrapper does not merge later framing/refusal derivatives.
