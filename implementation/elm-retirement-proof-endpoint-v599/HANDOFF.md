# Held strict native retirement proof consumer

Actual API: `from grant_endpoint import GrantEndpoint, RetirementProof, NativeBinding`.

Use `endpoint.observe(request_id, queried_binding)` for Registered/Future/Retired state and `endpoint.retire(...)` for a strictly correlated Retired-only proof. Caller/target bindings in the frozen result expose `.as_dict()`; `.allows_release` is false for Registered/Future. The caller binding is captured before the unchanged authenticated transport, compared again afterward and checked against the exact reply. A same-lifetime frontend change never resets the proof sequence watermark.

Protected CPU acceptance:

- `qa/test-1791147297220045657/report.json`:625 assertions;9 immutable native596 wire fixtures plus explicitly synthetic malformed/in-flight/freshness controls.
- `qa/mutations-1791147297213647348/report.json`:9 syntax-valid guard mutations rejected by their behavior tests.
- `origin.json`: copied endpoint/effect endpoint are byte-exact current521, also matching567/589; raw native596 producer report hash retained.

No native GUI, ledger or frontend changes. No commit. The synthetic transport is not a new kernel authentication result. Native594/596 grant retirement qualification and inherited transport checks remain separate antecedent evidence.600 must qualify target/caller/journal correlation and durable reservation release in its own derivative; this adapter alone never clears Unknown or unlinks data.

Frozen source/evidence is bound by `component-manifest.json`. Preserve all reports and use fresh derivatives for changes.
