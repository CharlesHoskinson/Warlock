# Corrected private ABI proof route

Fresh revision; all three original ABI sources and their prior reports remain immutable. No GUI/compositor/D-Bus proof executed during this preparation.

Future review/grant command:

```bash
python3 /home/hoskinson/window-integration-qa/qa_run.py -- python3 /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/abi-safe-v2/private_abi_proof.py --attempt /home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/abi-safe-v2/attempt-1
```

The shared wrapper launches an isolated qa-harness.slice scope and applies inherited soft/hard core limits1:1 through prlimit (systemd261 does not accept LimitCORE as a scope property). Scope is required before private runtime/bus creation. Runtime comes from the shared four-hex `/run/user/$UID/wqa` helper.

The client verifies live owned private session transport, exact Manager owner/interface, any explicitly supplied/already-owned AT-SPI transport, and actual returned Manager backend before key calls. It refuses X11/Legacy fallback. Pure-Wayland Manager works without DISPLAY or an X conversion; the separate registry bus is not required for its direct session-bus ABI and is never implicitly activated. Bus/owner checks repeat per operation and timer. Intentional X11 tests are outside this fixture.

Normal and failure cleanup stop exact owned clients before the service and private session; outer timeout uses recorded PID/start/PGID identities in the same order. Unresolved owned processes retain their private runtime for recovery. Original main a11y socket/reader state are observed read-only; no global reader/flag changes or input is sent.

Ten offline tests pass: permitted Manager guard with no X, backend fallback refusals, owner/connection loss, owned Unix transport and invalid transport, subprocess offscope refusal, stale-PID refusal, actual disposable subprocess clients-before-service cleanup, unchanged original hashes. Their permitted-backend case is a guard unit test, not real AT-SPI success. Actual public fabricated-packet ABI execution remains unverified for this revision until the frozen command is authorized.

All proof outputs use a fresh exclusive0700 attempt directory. Input hashes are checked before and after actual proof. NativeInputProved remains false even if future ABI proof passes.
