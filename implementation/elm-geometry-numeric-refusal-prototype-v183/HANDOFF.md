# Isolated Python numeric refusal prototype

The protected actual-decoder run `qa/numeric-1791127799736899141/report.json` passes190 cases. It imports copied production GeometryEndpoint.geometry_facts and geometry_size_policy; only the request method returns a synthetic already-received envelope. It does not open a socket or assert authentication/native behavior.

All14 Python modules are copied from immutable410 build1791125993387778780 inputs and individually match the corresponding held415 SHA-256 entries. The candidate differs only in geometry_size_policy.py: catch OverflowError while checking whether monitorScale is an exact int/float, finite and positive, then raise the existing Refused('Geometry scale') if invalid. Other numeric paths retain their original checks.

The unchanged original actually raises OverflowError for monitorScale ±10**400; these values fit the existing wire bound. Successful candidate assertions require Refused instead. Original failing case results are retained in original.json. The actual finite-check-bypass control is retained and accepts infinity, which the same external refusal oracle detects. Neither negative control is labeled successful behavior.

The190 cases include all68 byte-preserved held412 samples, invalid/valid scale values, oversized/nonfinite/bool values in every observed size vector, existing geometry rectangles and prospective projections, exact observation version/request/full binding checks, projection capability/profile coherence and strict fields. They show deterministic decoder behavior and preserve prior accepted samples; they do not qualify broker delivery, protocol authentication, full effect state transitions, native bounds or presentation.

No frozen410/414/415, model, native source, installed configuration or current production was changed. Candidate source is a prototype, not adopted production. Broader strict-wire, receipt/Unknown/menu, actual GTK configure/ACK/serial RGB, peer/focus, shared multi-action and original08/09/10 requirements remain open.
