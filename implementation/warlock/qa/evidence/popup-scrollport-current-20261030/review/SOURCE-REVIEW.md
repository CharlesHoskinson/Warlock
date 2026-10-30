# UI004 application-pin / native always-on-top source review

Disposition: source confirms separate policy/effect paths. No product defect demonstrated. The retained-peer-v2 fixture is not executable evidence for the current tuple: its historical wrapper is stale, and its keyboard/AT native-top branches invoke the stopped keyboard Menu opener. A new derivative must preserve that stopped history. No QA was run for this review.

## Original boundary

`docs/elm-roadmap/requirements.json:5089` ELM-UI-004 explicitly requires distinguishing application pin from always-on-top. Its six named primary-action scenarios do not exhaust the EARS clause. `INTERACTION.md:7` defines the application pin as a persistent launcher and native always-on-top as separate window state. Menu opening by secondary click is legitimate (`INTERACTION.md:37`). Secondary-click opening followed by keyboard or AT invocation proves that mixed route only; it does not close keyboard-only Menu/Shift-F10 opening. Explicit New instance and its stopped diagnostic remain separate. Persistent storage observation here does not establish restart/order coverage of UX004.

## Production ownership

* `src/Surface.elm:294` builds application Pin/Unpin controls with catalog desktop-entry identity. `Desktop.elm:1293` rechecks captured view, open Apps, writable Pins state and catalog membership for additions. `Desktop.elm:1342` emits only the revisioned `taskbar-pins-write` with current binding/request ID.
* `src/Pins.elm` bounds and de-duplicates identity lists, owns one pending request, and accepts Saved only for that request, matching proposed identities and a newer revision. Unknown does not authorize blind replay. `Desktop.elm:1041` checks incoming binding/status and delegates the exact request.
* `adapter/catalog_transport.py:96` verifies authority before and after preference save. `adapter/taskbar_preferences.py` owns private identity-only storage, exclusive locking, exact revision CAS, revision+1, fsync and atomic rename. A post-rename uncertainty is Unknown.
* `src/Provider.elm:418` derives the fixed label Always on top from observed native pin eligibility/state. `MenuBridge.elm:147` maps the typed desired boolean to Effects.Pin/Unpin; providerMatches checks current native binding/context/incarnation. `Effects.elm:211` rejects unavailable/already-requested pin state. This path is not a preference-store mutation or application launch.
* `Surface.elm:464` derives the menu checked state from current provider geometry/native window pin observation, with provider/menu/native binding checks. `assets/popup-adapter.js` already reports actual role and aria-checked alongside DOM identity, publication, lease and rectangle.

Existing `PinnedMenuReplay.elm` covers pinned context resolution, stale publication, absent/ambiguous catalog ownership and ordinary group fallback. `PinMaxReplay.elm` covers confirmed native pin/max state and pending/Unknown non-replay. These source references are not a fresh test result or complete native independence observation.

## Minimal current-tuple fixture

Reuse the reviewed attention-v5 composition mechanism, strict private AT/provider ownership and protected cleanup; do not reuse its old frontend eligibility after a static asset edit. Leave historical reports/helpers untouched. Route every native-top menu opener through one genuine current stamped bar secondary-click. Invoke the selected menu control separately by physical pointer, actual keyboard or real AT-SPI action. Record opener and action modalities independently.

Retain the useful old schedule: application pin/unpin while native state is false; native top on with saved pin; application unpin/re-pin while top remains true; native top off; analogous AT actions. Keep the same native incarnation/application and no launches throughout. For each application mutation require exactly one preference request, exact binding/request receipt, Saved revision equal request proposal revision+1, exact stored identities/revision, unchanged native state and no native effects. For each native mutation require exactly one matching native intent/outcome, exact incarnation/operation/binding/protocol, Committed plus independently observed target state, unchanged raw preference bytes/membership/order/revision, no preference-write request and no launch. Reopen the menu to check observed checked state as needed; do not infer checked state from a successful write.

Old fixture gaps to fix narrowly:

1. Remove invocation of the stopped keyboard opener, not its retained historical failure.
2. Match the whole current button record (not only identity), publication/lease, mode and enabled state immediately before input. Use actual viewport/scrollport clipping. The old popup pointer reads the last generic xdg_popup configure; this does not establish exact current popup provenance.
3. AT must bind unique owned PID/start identity, accessible ID, DOM ID, name, document/menu ancestry and actual check-menu role; require checked state equal the observed native pre-state. Existing at-action.py checks focused/enabled/visible/showing and executes a real action, but does not itself check checked state.
4. Add the precise storage/request assertions above. Old native-top checks stored equality but not preference-write count; old application checks Saved identities but not exact stored revision relation.

## Popup observation seam reviewed

Root's additive `assets/popup-adapter.js` edit stays within `if (window.elmHostQA)`. It computes the actual `.surface-popup` client scrollport as bounding-rect origin plus clientLeft/clientTop and clientWidth/clientHeight, and appends scrollport/mode to the same sampled body before existing dedup/post. Current `shell.css:1` makes this node the overflow:auto 100vh scroll container; no container/ancestor transform is present. Snap/checkmark pseudo-element transforms do not change this coordinate basis. Under the selected scale1/transform0 native environment, the source is READY for bounded QA observation. No control policy, input routing or lifecycle change occurs. Missing observations refuse qualification; do not substitute viewport assumptions.

This asset does not report native popup origin or own native view identity. Existing native sources provide partial joins: `shared-host.c:428` publication→popup owner; `host.c:737` lease-qualified current-popup configuration and dimensions. Existing measured_inspection.py validates the bar's exact live configured layer but still uses the last generic popup rectangle. A bounded private parser may join live wl_surface/xdg_surface/xdg_popup object creation epochs, current layer-parent association, configure/ack and destroy events, then require unique current candidate, exact lease/configuration dimensions, owner publication and before/after frame equality. It must fail ambiguity or missing association. This requires concrete source review before execution; this note does not declare such a parser implemented. A JS-only field cannot replace the native join. If logs cannot establish that join, a separately selected native QA observation seam is needed; no native policy relaxation follows.

## Frontend lock delta

Proposed lock `pin-scrollport-frontend-lock-root-v1.json` SHA256 `8f35f73022732f33f156f52488e327cf8cd5d6604be7d27cea0325ca2e054199` was compared recursively against current-build-lock-root-v5.json. Exactly two scalar values differ: the absolute popup-adapter input entry and static.popup-adapter.js. Both change from `050af2a6cfb58195f6999f126ab94f37573231007cb2fcd7d119873969365605` to actual source SHA256 `5bac00f28cabc0173be32d4c6178daada0c21ace19e68bd8e82a061cdde927d2`. All 99 source/project entries and remaining 229-input inventory/tool/cache/recipe metadata are unchanged. READY for the unchanged protected frontend build API; no build or native outcome inferred. New frontend receipt and current native composition must be reviewed before any new native run.

## Documentation

`docs/warlock/explanation/application-pin-and-always-on-top.md` is accepted as source-accurate Diataxis explanation. It explains identity, authority, persistence and evidence distinctions without becoming a test procedure. It explicitly leaves current native independence open and distinguishes pointer-opened keyboard actions. No change requested. No full UI004, UX004 restart, keyboard opener, New instance, release or installability acceptance is made by this review.
