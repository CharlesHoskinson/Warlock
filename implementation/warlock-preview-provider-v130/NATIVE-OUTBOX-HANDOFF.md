GUI111 adds `assets/native-preview-control-outbox.js`, a transport for exact
native-issued tickets. It never constructs a control command or assigns an
ordinal. Native purpose reservation/admission, immutable ticket issuance and
the existing controlled dispatcher remain the only effect admission route.

The outbox checks the exact original Native binding, receiver epoch, canonical
uint64 strings, native ticket/enclosed packet correspondence, original4096-byte
UTF8 bound and reserved queue capacity. It retains contiguous issued tickets
as immutable raw strings. Retry posts only the oldest packet. Changed bytes,
gaps, foreign domains and invalid receipts cannot advance its frontier.
Repeated proposal advisories never remove a pending row. A trusted matching
head receipt advances only transport delivery and prepares an exact independent
confirmation string. Confirmation retries remain possible after the data queue
empties. Callback guards avoid recursive data posts; the next host poll supplies
progress. No transport method certifies effect, physical or Elm settlement.

The constructor describes an empty fresh realm. The host must retain native
ownership across renderer reload and recover its exact retained tickets and
prefix before resuming. A JavaScript object cannot survive destruction of its
WebKit context; the source comment about retaining an object across reload is
an integration obligation, not implemented reload recovery. Recovery remains
an explicit unchecked OpenSpec task. This file is not loaded by popup.html.

Current qualification:

- `qa/native-outbox-check-v4-1791354355501494232/report.json`:93 sanitizer-backed
  actual controlled C/Bootstrap/Native authenticated socket/Broker/ReceiptDelivery
  checks through the actual JS transport. Two same-subject realm epochs use one
  unchanged Native grant. Application-boundary lost posts, receipts and
  confirmations retain original bytes. Actual native modified-ticket refusal,
  exact duplicate receipt, physical job retained after delivery/confirmation,
  native polling/proofs, terminal ACK, distinct scoped readiness/completion/final
  processing/independent confirmation and strict close all pass. Old epoch
  ticket refuses against the actual replacement C owner. Synthetic Native
  subject21 remains Active; native peer and fixture exit normally.
- `qa/native-outbox-protocol-check-1791354413823194560/report.json`:47 adversarial
  protocol controls cover full uint64 binding/epoch beyond JS safe integers,
  malformed/foreign/gap/changed tickets, UTF8 byte bound, capacity, immutable
  retention, stale receipts, independent compact prefix and synchronous
  callback reentry. Maximum data-post depth is1. Issuer is a synthetic fixture.
- `qa/native-outbox-model-check-1791354287844124126/report.json`:14 explicitly
  selected Quint scenarios,200 bounded samples,26 actual JS traces and463 state
  comparisons. Retained frontier/observed receipt/queue occupancy, exact ordered
  data attempts, independent confirmation attempts and operation results are
  compared. Native issue/history/failure controls are trace-driver inputs and
  are not reported as a second application policy or actual native issuer.
  Six executable JS variants fail exact observations: changed bytes accepted,
  advisory drains row, future receipt, dropped-post forget, dropped-confirmation
  forget and capacity ignored. Actual C issuance is qualified separately above.

Three failed fixture reports remain immutable: an unused shared fixture helper
failed `-Werror`; a diagnostic status used positive-wire counters for zero
values and exited with retained ownership; a test mistook an unconfirmed native
proposal for independently confirmed delivery. Fresh fixture derivatives use
the helper, encode zero-valued diagnostic counts as decimal strings, and test
the native distinction before/after actual independent confirmation. No product
guard, native purpose, physical/proof barrier or original deadline was relaxed.

Existing product native/src/adapter/assets files are byte-identical to held110
except the added inactive outbox. Held110 resource/capture/control/FD/scoped
detachment evidence retains that parent source identity. Native130 current110
legacy host qualification passes2518/278/full cleanup and is public79
48451e88124dd0ae9aa8e69f25e25c7ba8e82e05. This GUI111 component does not activate
controlled host/Core/WebKit routes or establish actual Wayland-window, renderer
reload, ordinary capture eligibility or full release acceptance.
