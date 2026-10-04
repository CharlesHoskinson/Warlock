# V71 independent post-close CPU qualification

The accepted suite compiles the actual held V69 MenuBridge, Shell, Effects, ReceiptRouter and surface controller with a QA-only worker derivative. The worker adds preparation metadata and explicit expiry/cancel inputs; it does not change production reducers. The original worker is retained in each input capture. Production Main and Popup also compile.

The 59 independent cases distinguish a local Menu reservation from a native operation. Selection closes the popup and requests observations while native request/generation stay zero and the receipt registry stays empty. Correlated observations in either order permit exactly one fresh-context operation; focus and observation revisions may advance. Tests cover Maximize, legacy Minimize, legacy Restore from minimized MAX, unsupported geometry fallback, authentic partial-stream readiness, wrong/invalid correlations, valid admitted scope/state/ownership/workarea changes, cancellation/deadline/owner conflict, app and taskbar interaction guards, bounded single-slot callbacks, notification dirtiness, and an unrelated original sent Unknown key surviving another preparation/cancellation/dispatch.

Five actual compiled unsafe production derivatives are rejected by named external trace oracles: stale timers canceling current selection, new preparation discarding the original receipt registry, changed geometry records being retargeted, notifications replacing prepared correlations, and application popup opening during preparation. Both geometry-record guards are weakened in that mutant because registration independently checks the same records.

Original V58 menu/geometry/refresh suites and fixtures are copied byte-for-byte. Their results remain separate: menu 64 of 78 pass; refresh 18 of 21 pass; the geometry suite stops at its old immediate-dispatch setup assumption without completing its 53-case report. These failures are preserved and are not renamed or counted as new protocol passes. All 78/53/21 acceptance remains ancestral V58 evidence, not new-protocol regression acceptance. The initial harness missing-result failure and an invalid observe-only dual-stream QA assumption are also retained.

Run through the protected CPU launcher:

```
python3 -B qa/replay.py --source /absolute/implementation/elm-menu-post-close-selection-v69
python3 -B qa/mutations.py
```

The standalone new oracle receives `replay.js`, `qa/original/fixtures.json`, `qa/original/geometry-fixtures.json`, and an output JSON path, in that order. The compiled worker must expose `preparedToken` and the authentic preparation record, as the owned worker does.

This qualifies synthetic compiled controller behavior and evidence integrity. It does not establish native execution, physical menu behavior, timing under load, rendering, native Unknown recovery, a new Quint model, installation, release readiness, or full Windows parity. The next native campaign must use the exact coherent tuple and the original six-second transition deadline.
