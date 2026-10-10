# MAX no-activation input

When the committed MAX traversal finds no eligible window, the ordinary native button handler now suppresses the new press before decoration, resize, focus, raise or cached seat delivery. Its matching release is swallowed. Accepted presses retain the existing release path. Native layers, locks, grabs and constraints keep their existing branches.

The protected recording preserves the original `ELM-REN-015/max-input-region` oracle: both MAX roots coexist, upper pixels remain at the input hole, the eligible lower GTK root receives the press and release, and paint/hit revisions agree. The additional both-excluded point retains native pixels and a ready committed scene with a null hit recipient. Through the original six-second observation window it delivers no GTK press or orphan release and changes neither focus, stacking, geometry nor the effect journal. Restoring the primary input region permits exactly one actual GTK press/release pair on the next click. Both original return placements recover; the unchanged pin/MAX pointer and physical keyboard regression passes. Native cleanup passes in both recordings.

## Quint model and implementation map

The installed quint-llm-kit modeling/execution skills guide executable initialization, pure decisions, named tests, positive witnesses and sampled safety runs. `committed-press.qnt` adds a scoped model rather than weakening `max-overlap.qnt`. Both model snapshots pass seven named tests, four positive witnesses and 1,000 sampled 30-step safety traces. The unchanged original model also passes its own named tests, witnesses and safety after the native change.

| Model | Native mapping / boundary |
| --- | --- |
| `ready`, `recipient`, `refuse`, `pressUpdate` | `CommittedScene::inputOrder` and `ViewHitTester::windowAt`; `InputManager::processMouseDownNormal` suppresses stale or null-hit ordinary MAX presses. |
| `suppressed`, `releaseUpdate` | Existing bounded button suppression bitset; rejected presses consume their release before refocus/seat delivery. |
| `owner`, accepted release | Existing native seat path retained; actual ordinary GTK press/release owners observed. A release concurrent with a shape/device change remains native-unqualified. |
| `shape`, `commit`, cached recipient | Abstract atomic shape/commit operations. The old ready/no-hit cache fallthrough explicitly violates safety in a named counterexample test. No claim that this recording retained cached focus through shape commit. |

Assumptions are one serialized ordinary MAX seat, two roots, one button and an already-correct eligible refocus path. Layers, locks, grabs, constraints, popups, transforms, output presentation, timing and ABI are outside the model. The model's accepted eligible recipient is an assumption verified only for the recorded native points; it does not prove every cache mismatch or race.

## Acceptance

`manifest.json` binds exact source, reports and matched core/plugin/aquamarine. The immutable prior committed-scene evidence remains unchanged. Only the owning InputManager source behavior changes in this slice; the existing scene builder rebuilds its three owning units and preserves all other archive members, public headers/layouts and strong exports. The existing compiled Elm/host output remains unchanged and source-verified by the native launcher.

ELM-REN-015 remains **partial**. Independent acceptance, full presentation, actual cached-focus/commit and button races, stale/failed frames, transformed/modal/grab/layer/fullscreen/multi-output qualification, native AT, resource budgets and package/rollback remain open. No deployment or main desktop modification occurred.
