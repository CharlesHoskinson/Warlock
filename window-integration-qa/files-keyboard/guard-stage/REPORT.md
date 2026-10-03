# Files V5 guarded accessibility candidate

This is a copied QA candidate, not deployed. Original Files PID 667402 stays hidden with live operations/scripts untouched. Source contract precedes implementation: `contract.md`. Fresh source lock is `source-hashes.json`; package/plan is `deployment-prepared/plan.json`; actual native runner and dependency hashes are `native-runner-manifest.json`.

## Proven copied Qt behavior

Final actual offscreen checks pass: 58 keyboard events/outcomes, 120 geometry scenarios, 26 QML parse checks and 20 recorded retained-action/reload/compact-tree outcome gates. All copied offscreen applications use nonexistent private session D-Bus sockets; no compositor input or Orca claim follows from these runs.

The old V4 candidate actually accepted hidden native/raw actions, background prompt actions/shortcuts, rebound Home media through the same logical peer and lost focused file identity on same-PID reload. The frozen baseline reports remain in `../retained-probe/`. V5 puts enabled/effective-visible/mapped/modal authority in the shared native action dispatcher and shared QML activation API; Home media changes retire old peers. Qt native text interfaces remain native. Editable-text mutation interfaces are not separately covered by the action-dispatch guard evidence.

The first delayed V5 restoration actually stole newer Sort focus back to the saved file. `retained-probe/newer-focus-counterexample.json` preserves it. Final C++ restoration uses content/window lifetime, request generation and input/focus epochs; recorded actual replay now preserves newer Sort, Tab and prompt focus. Ordinary mapped reload restores the real file identity; hidden reload preserves the token without mapping. A new prompt also has its own text focus preserved.

Compact tree focus previously landed y394 outside height320. The parent sidebar now reveals both tree viewport and parent scroll position on actual row/chevron focus. Final preflight verifies Home and expanded nonroot `fixture/subfolder` at y268+height26, inside the 330×320 window; actual Qt Right/Down events select the deep row.

## Formal evidence

`../keyboard_focus.qnt` and its named suite pass 21 scenarios, 2,000 samples ×100 steps, seed20260930. Independent file peer paths do not follow selected file; current/stale epochs remain generated after long rebuild sequences. Deferred model materialization, newer toolbar/Tab/modal intent, hidden and superseding requests are explicit. A found delayed-modal model counterexample and historical models remain preserved. See `../MODEL.md`; model success is distinct from implementation evidence.

## Native reader proof still pending

`native-qa/run_native.py` stages real silent Orca on a copied native Files window at330×320: gallery, expanded tree, Home collections/pins/media/recent/storage, details and menus, plus unchanged real sandbox rename. ObjectNavigator actions match exact real AT-SPI bus/path peers. Private opener records actual sandbox file bytes; it proves existing xdg-open dispatch, not a default association application launch. Shared reader wrappers/profile stay unchanged. Global compositor keyboard interception, audible/braille quality and any delegate virtualization outside the tested destruction/media cases are not claimed.

The runner requires an explicit root GUI grant and refuses an existing Orca owner or foreign input grab. It retains private backups of all four catalog files, checks full canonical stable clients, original public/full UI state/PID start/hidden, focus/cursor/layers, typed clipboard/primary byte hashes, dashboard, flags/socket and shared reader profile. These native preservation gates are prepared, not passed yet.

## Deployment boundary

All 15 changed QML files and the exact fresh V5 binary are frozen; all ten scripts plus fileops.qnt remain byte-identical to original. Fresh durable URL package is prepared, not installed. Copied durable URL resolution/reload and broad native reader proof are required before root-owned guarded same-PID deployment. Current PersistentProperties transfer is retained; no legacy migration or FILES_OPEN initialization may run. Original hidden state allows only an explicit new empty focusIdentity field; other public/UI state must be canonically equal. Private rollback sources/state remain available after success.

Implementation uses installed official Qt6.11.2 native Quick accessibility interfaces and public QQuickWindow focus events; Quickshell PersistentProperties/ProxyWindow reload behavior is tested on actual copied processes. The code derives from the separately frozen V4 source, without overwriting any loaded V4 module.
