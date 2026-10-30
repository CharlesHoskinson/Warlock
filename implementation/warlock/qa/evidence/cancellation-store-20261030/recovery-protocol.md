# Historical cancellation reporting, protocol 1

New informational DTO, not an existing accepted C/Elm transport. Exact fields:

```
{
  "protocolVersion": 3,
  "kind": "host-cancellation-recovery",
  "cancellationRecoveryProtocol": 1,
  "binding": CURRENT_DELIVERY_BINDING,
  "recoveryState": "Unknown" | "Terminal",
  "executionAuthorized": false,
  "record": EXACT_VALIDATED_V7_CANCELLATION_RECORD
}
```

Both version fields are integer literals, never booleans. `binding` is the validated current recipient binding with the same compositor lifetime as the store. `record` preserves the original admission binding, complete intent/key, original deadline, attemptedKinds/commitAttempted, prepared/lastObserved, certificate, stage and ACK information exactly as stored. `recoveryState` is Terminal iff the full validated immutable terminal certificate is present; all other records, including locally recorded Prepared, report Unknown. TerminalStored versus AdmissionRetired remains visible in record; this DTO never asserts native resource retirement.

The source emits at most64 independently bounded frames after validating the entire snapshot under one host_guard. Every frame is <=the existing one-MiB daemon output-frame limit. No mutation attempt, native call, ACK, admission unlink, live attach or counter allocation occurs in reporting. A same-binding report also grants no permission. The historical terminal is nested evidence, not a newly delivered current native effect-outcome, host-admission-settled or forged Refused.

Existing private CancellationCoordinator.startup returns these frames through its existing recovery-store API, and its daemon proposal queues/sends them. Current production native/host.c has no distinct cancellation recovery handler and current Elm incoming/ports routing has no decoder for this DTO. It may be dropped/ignored or remain unusable at those boundaries. This patch solves the store/reporting API only, not end-to-end historical certificate delivery. Future typed C/Elm integration must explicitly validate this schema, preserve original binding, and avoid routing nested certificate fields as a new effect outcome or execution permission. No generic NativeOutcome or legacy settlement status expansion is proposed here.
