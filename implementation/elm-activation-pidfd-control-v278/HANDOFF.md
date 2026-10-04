# Actual kernel-bound process signaling control

Private activation cancellation must target the same recorded process lifetime.
A numeric PID plus a preceding proc check leaves a reuse interval before kill.
Linux pidfds bind signaling to the opened process; a retired fd must refuse a
subsequent signal rather than redirecting it to another numeric-PID incarnation.

The protected CPU control opens actual pidfds for owned disposable children,
captures their kernel fdinfo and PID/start, observes a real SIGTERM wait status,
then tests actual normal retirement and signal refusal on the retained pidfd.
Descriptors close on all paths. No privileged process or desktop is signalled.

This qualifies the available kernel/Python primitive on these actual children.
It does not prove arbitrary PID reuse, cross-UID authorization, complete service
supervision, private-bus/native toolkit behavior, or desktop acceptance. Production
integration must still correlate the opened fd with current exact PID/start and
credential policy, retain deadlines, and prove complete closure.
