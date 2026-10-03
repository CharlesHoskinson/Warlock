# Private causal telemetry proposal

No native execution or product repair is authorized by this proposal.

Retain the current client/control sequence, with automatic private file logging:

- Actual GDBus message filter logs incoming/outgoing type, serial/reply serial,
  sender/destination/interface/member, actual own-name owner changes and
  monotonic timestamp. Each PointerPositionChanged arrival is recorded before
  the GLib subscription callback observes it. This is real wire metadata.
- Existing actual subscription callback records its monotonic dispatch time,
  cumulative callback count and wire-arrival snapshot. Do not pump/drain signals
  merely to make the failure disappear, invent a serial, or clear history.
- Each actual command records begin/end, arguments and response. The replacement
  case retains full prior/after signal history, release/reclaim replies, current
  cursor, input command times and service State snapshots.
- An independent private dbus-monitor captures actual session wire traffic before
  the scenario. Its PID is scenario-owned; its environment must use only the
  already owned private runtime/bus. Never monitor the main user's session.

Interpretation requires a causal packet, not just count equality:

- Wire arrival before release/reclaim, later callback dispatch, and no new wire
  pointer signal identifies a previously queued caller callback.
- A newly emitted pointer signal after owner loss/reclaim, without another
  authorized QueryPointer, violates retirement of the prior epoch.
- Ambiguous ordering remains a failed or unresolved gate. No timing sleeps or
  service barrier may replace the original churn assertion as the sole test.

If the cached epoch flaw is accepted for repair, stage a separate lifecycle
model first. Actual motion may capture a bounded deferred notification; known
owner events must be drained and epochs revalidated before emission. Old epoch,
retirement, bus loss and exhausted budgets must never emit a stale signal.
Input callbacks must not perform synchronous D-Bus calls. Preserve fractional
motion, directed notification, one-shot/coalescing and normal quiescent unload.
