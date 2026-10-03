# Actual source and ABI mapping

This packet implements the approved core policy at official core revision `efb50993780079460b0cbed1363e2166a2de1d9f`. All runtime sources were fixed before final core and plugin compilation. The core executable was never run and the plugin was never loaded. Native acceptance is pending root review and the unchanged original 14 pin checks, plus MAX/restore/transfer/scroll/focus cases.

## Native mode and normal return

`CNativePinState` owns a weak exact native-window/layout-target record, complete ordered group members, space/output objects, normal logical/visual target boxes, floating origin and monotonic generation. `capture` runs before the owning controller publishes MAX. `snapshot` checks live/mapped owner, native target, selected layout/group target, exact group members, current space/output and finite return boxes. `restoreUsable` is latched metadata authority, separate from `pinOrigin`/`pinManaged` independent user intent. `ownedUnpinReady` requires the same live current selected owner/target and positive generation, and allows explicit intent clearing when return ownership is stale. It cannot supply new geometry or float/MAX authority.

`CFullscreenController` uses native handler requests and keeps native internal/client modes. Its narrow friendship allows `CNativePinState` to borrow the actual owning handler. `IFullscreenHandler` gains virtual `nativeMaxRestoreValid` and map-only `detachFullscreenRecord`. This changes its vtable: the matching rebuilt core is mandatory. Target `geometrySnapshot` returns actual `STargetBox`; this is not geometry synthesized from maximized client bounds. Generic fullscreen handling keeps native MAX records and permits protected MAX peers to coexist; exclusive fullscreen retains its separate policy.

The scrolling handler adds `optional<SNativeScrollRestore>` to `SFullscreenScrollState`. The return stores original column, ordered weak row objects and sizes, post-extraction surviving rows, column width and camera offset. Actual `nativeReturnValid` checks current registered owner/controller/column/selected row, exact peer order and sizes, finite positive width/row sizes and finite camera offset before `restoreNativeColumn` changes column membership, widths, sizes or camera. Invalid return latches authority failure; it does not invent a return column or fall back to a stale width. Existing ordinary non-native width handling is retained. Actual CPU adapters exercise these real objects, including independent peer preservation.

## Transfer and failure

`SNativeMaxTransfer` retains strong owner, native/layout targets, source algorithm/space, destination space and its original workspace/output, original modes/record generation, and a monotonic operation. The source algorithm keeps its uniquely owned handler alive; the weak handler is borrowed without `lock()`.

Both actual `CWindowTarget::assignToSpace` and `CWindowGroupTarget::assignToSpace` guard after workspace callbacks before layout continuation, and check `finishTransfer` after the owning assignment. Callback refusal invokes `finishTransfer` only to persist its observed failure, then unconditionally returns; its result cannot authorize continuation. The ordinary public assignment API remains void. A failed native destination admission is reported through `SNativeTransferOutcome`, warning and immediate return before target follow-ups. The outcome holds actual mode availability, actual native/internal modes, current target/space/workspace/output and reason. No synthetic float, unMAX/reMAX, geometry rollback or client success is performed. Old source handler retirement is map-only.

The exact captured record is marked unusable on refusal, including a temporarily reselected group owner and this operation's own rebound generation. A later reselect cannot revive it. An unrelated/replacement record is not invalidated. Actual partial state remains observable. Current same-owner explicit unpin clears independent intent only. This is the approved additive transfer refinement, including the final two original-reselection cases.

## Protected family and native focus

Native child creation no longer copies parent `m_pinned` in the two original XDG inheritance sites. `familyEdge` and `effective` derive family protection from actual parent relationships without fabricating child intent. Independently pinned children keep their own intent. Renderer and hit tester consume the same `band()` order; hit testing reverses it. `orderBand` refuses duplicate, cyclic, out-of-range or over-512 bands. Animations, decoration offsets, OpenGL and screenshare use the same derived effective protection.

`fullWindowFocus` retains its void interface as a wrapper. New `fullWindowFocusResult` resolves only explicit owner-family requests to a current deepest visible modal before the existing modal guard. Unrelated and ordinary no-modal requests remain their own target. Native lock, exclusive layer, nofocus, X11, Seat grab, keyboard, visible workspace and fullscreen decisions remain in the native path. `SWindowFocusResult` records requested/routed owner, before/after core and Seat, expected surface, keyboard, accepted and partial. `acceptsResult` rechecks current owner/lifetime/route/surface and native policies, and requires actual core owner plus core surface plus Seat surface equality. Core-only changes after Seat refusal are retained as partial observations, never rolled back or accepted.

`switchToWindow` uses the returned accepted target and rechecks before cursor warp, forced focus and monitor follow-up. Other stock void focus callers are retained; this packet does not claim they were converted. Monitor/workspace movement retains actual native owning target and checked transfer/return ownership. Pure model geometry and peer tokens do not replace these concrete native guards.

## Plugin and helper boundary

The plugin keeps original Hyprland API hash validation, and adds policy capability 1 and exact core policy source ID validation. PinAction's native path calls native pin/raise without floating. Ordinary pin still uses the original float/pin/raise behavior. Stale same-owner explicit unpin neither floats nor supplies restore authority. PinBoundary, PinLifetime and PinJson sources are unchanged.

Schema 2 observations include exact core source ID; native/internal/client modes; typed live, normal, floating, pinned, admission and return/intent flags; positive generation when authority is needed; exact native/layout/space/workspace/output pointer strings; actual geometry and return-box decimal strings. The decoder rejects bool/int aliases, nonfinite or malformed numbers, duplicate/extra/missing keys and wrong core IDs. Full field lists and predicates are captured by the complete source inverse and tests. Reports are observations; no decoder changes native state.

The fresh CLI embeds the exact decoder, requires the selected core ID in config and passes it to the result validator. Original helper process/environment/source/argv/peer/socket/EOF/absolute two-second deadline/durability functions are AST exact. The original result is retained as `_legacy_result`; only original negative results without schema use it. Legacy positive results never become completion authority. All 32 original test bodies/assertions/deadlines are AST exact; only schema/config fixture builders add the exact selected pair.

## Exact ABI/build scope

`actual-core-policy-run.log` records compiled sizes/alignments of the new restore, transfer, outcome, projection, focus result and handler records. `core-object-freshness.json` records 448 compiler-emitted object dependency lists and 2,211 actual dependency hashes/modes; no dependency is newer than its object. Plugin dependency verification records the actual ten source units and 799 source/header dependencies. Build closure records core/static library/plugin hashes, compiler/linker/build tools, flags, linked inputs and actual exported symbols. These are local build provenance and CPU acceptance, not native ABI/load reachability proof.

## Preserved failures and limits

All earlier configure/build/link errors, the schema ordinary-fullscreen guard failure, the original-record refusal-latch counterexample, and the CPU wrapper's renamed-main undefined-behavior SIGABRT are retained with exact preimages and logs. Earlier builds are diagnostic. The final build begins after all runtime source fixes. Models, CPU adapters and full upstream CPU regressions do not establish physical cadence, rendered pixel correctness, focus/transfer reachability, deployment or full parity. Root retains exclusive native ownership and the original Pin14 predicates/deadlines.

## V3 exact hit refinement

The complete V2 mapping and field ABI remain inherited. Two existing owning function bodies are corrected without changing fields or layouts: CViewHitTester::windowAt reaches its original ordinary eligible scans after a protected native MAX band miss; InputManager::mouseMoveUnified preserves a protected ideal in its existing non-special MAX exemption and never revives an excluded protected fullscreen owner. The new NativePinState include binds the owning policy API. Special/exclusive/layer/priority/input masks and all existing owner fields remain exact.

CorePolicyBuild.hpp and helper EXPECTED_CORE_SOURCE_ID bind 59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3. Plugin implementation is byte-identical to V2 and is rebuilt from these owning headers. These source/schema IDs are pairing evidence; native MAX/input reachability remains pending. The full V2 original-source inverse and the new complete two-function preimages/intended diff are retained.

Proof: retained-approved-hit-audit/formal-before-runtime-v3.json (24 named and 2,000 bounded traces), exact original/proposed owning body adapter matrix (26 rows each, 8 required fixes and 18 conservation rows), and whole proposed TUs compiled before runtime. The fresh full core build, actual owning adapters and original CPU suites supply matching executable evidence.
