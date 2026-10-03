# V22: native main-surface input-region qualification

This derivative preserves the exact V20 compositor/authority pair and exercises a
real GTK/GDK input-region hole. It makes no installed desktop changes and does
not establish canonical scene admission or full window-system parity.

The campaign leaves the peer visibly opaque green, pins it over the red
maximized window, and removes the peer's surface-local rectangle
`[80,80,80,80]` from its input region. The global hole probe is `[300,300]`,
corresponding to peer-local `[100,120]`; the outside probe is `[450,300]`.
Actual application pointer and keyboard receipts are independent of pixels,
focus metadata, the fixture's request receipt, and recorded draw facts.

The retained native packet
[`qa/native-1791066600635179376/report.json`](qa/native-1791066600635179376/report.json)
**failed** `inputHolePassesPointerToUnderlyingMAX`. The committed main-surface
draw recorded the hole, and the peer remained green at the hole, but actual GTK
pressed/released events went to `SCENE-PEER` at local `[100,120]`. Thus visible
pixels and input-region diagnostics did not establish correct event routing.
The packet records `cleanupPassed=true`; its failure and evidence are preserved.

The owning V14 `ViewHitTester` selected a pinned peer by its bounding box without
checking the client input region. `windowSurfaceAt(..., true)` subsequently
found no eligible main surface, but the input manager's main-surface fallback
still delivered the events to that peer. V23 fixes selection for this bounded
case, using a new candidate rather than changing this failed packet or V20.

Original regression identities and observation/helper deadlines are retained.
Use the protected `qa_run.py` launcher for any new serial native campaign.
Fullscreen main-surface fallback, popup input masks, animated coordinate
mapping, border/decoration behavior, scale/rotation and multi-output admission
remain separate acceptance gates.
