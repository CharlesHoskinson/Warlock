# Typed native source boundary

Run the actual optimized provider-v7 `NativePreviewSourceReplay` compiled from
the held Elm source and toolchain. Seed it with the own provider's real native
client-scope observation from native-v1, including its lossless uint64 lifetime.

- SOURCE-DECODE-01: WHEN a client or monitor observation is admitted, the decoder
  SHALL retain its exact typed source, original scope, request and byte budget.
- SOURCE-DECODE-02: IF source kind/label, grant/context/clock, protocol, eligibility,
  canonical uint64, aligned budget or strict schema is malformed, the decoder
  SHALL refuse the observation without manufacturing a capture permission.
- SOURCE-DECODE-03: WHEN this check is reported, compiled boundary evidence SHALL
  remain distinct from native capture, physical presentation and full release.

This worker uses the same module compiled into provider-v7 assets. It does not
establish active Popup source consumption; full WebKit integration remains open.
