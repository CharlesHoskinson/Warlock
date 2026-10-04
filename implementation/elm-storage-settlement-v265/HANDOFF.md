# Storage refusal after a real native commit

V263 and V264 qualify actual minimize and restore respectively when native authority
commits but durable broker settlement cannot read its journal. They use unchanged
V256 host/assets/broker, V257's sealed supervisor/runtime, and the exact V89
core/plugin ABI pair. No production source changes are made by this packet.

The existing inert protected-QA after-submit hook pauses the actual owned broker
after an actual Committed native receipt and before durable settlement/frontend
delivery. Its marker contains the actual receipt, Pending journal, PID/start and
documented same-sender rehandshake/stale-request refusal proof. The fixture changes
only its private intent.json permissions from 0600 to 0644, verifies the owned
stopped broker, and resumes it. Journal.read refuses the real public record;
guarded settlement classifies unverified recovery data, sends the typed error and
disconnection, and the broker exits normally with failure code 1. The frontend
never receives the terminal window receipt.

The real bar shows repair guidance and unconfirmed-action text. Pending becomes
Unknown without changing actual native state. The original Pending bytes remain
unchanged. Restoring permissions causes neither automatic reconnect nor replay
during 500 ms. A real pointer Reconnect retains the same host/compositor and gets
a fresh authenticated broker binding in the same instance/lifetime namespace.
Its host-uncertain frame is informational; a current snapshot retains Unknown and
the actual committed minimized/visible state. A fresh explicit primary action
performs the opposite current-state operation with advanced request/generation,
receives its own commit, and preserves application incarnation and compositor.

V263 passes 45 native checks; V264 passes 47 (including actual minimize setup for
Restore). Each verifies six actual screenshot/body-pixel stages: before fault,
after native commit, at settlement failure, after correction before retry, after
explicit reconnect, and after a fresh explicit action. Visible stages prove the
real fixture keyboard recipient; minimized stages prove it receives no key.
Owned pointer commands, broker failure exit, one shell generation, normal host
and fixture exits, empty cohorts, plugin unload and private-session cleanup are
recorded. Original six helper ASTs and observation/input deadlines are unchanged.
No installed desktop, main compositor or user drafts change.

V262's actual host/Elm builds, 47 stale/55 storage/20+27+30 inherited compiled
checks, Quint10 named/1000 samples, busy/legacy native22/23 and original137 native
regression remain retained on this same source but are not rerun by these selected
workloads. V254/V247 historical storage and interrupted recovery packets remain
on their original source tuples. Do not aggregate counts into distinct baseline
scenarios or mark a whole requirement, sprint or release complete.

This proves post-commit settlement-read refusal, not an actual disk-full or
post-rename directory-fsync failure. Host binding/lock failure and native full/
readonly storage remain open, as does production legacy provisioning. Source
review found a concrete next defect: admission_bind calls admission_close on a
lock/privacy failure, which also retires its instance descriptor. Same-host retry
then lacks that descriptor. Reproduce this path, preserve the failure, retain the
instance context while retiring only the failed lifetime lock, and qualify actual
correction/retry. Then rerun the complete final recovery matrix and integrate the
newer geometry/menu pair. Global old-live-broker revocation, original restore
timing, coherent GPU, AT/IME, hotplug/zero-output, operations, physical/human UX,
budgets/soak, C00 and release remain open.
