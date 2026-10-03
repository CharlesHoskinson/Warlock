# Exact source mapping for the unapplied three-file proposal

## Scope

`intended/intended.patch` is unapplied. The existing V27 sources, B13 failure, original baseline38/fault34, D3 helper drain, V21/core tuple and every original budget remain unchanged. Intended whole-file inverses reconstruct V27 exactly. All16 existing NativeDesktop methods,7 of8 OwnedCommands methods and17 of18 SceneController methods are byte exact; the two replaced preparation blocks reconstruct the complete original prepare body. New `_guard_destination` is byte equal to the original apply_destination pre-effect guard. The original planning, refresh_destination, validation, three captures, finisher, outputs/fresh family/geometry/source checks, seed, fallback/reduction/atomic deadline and cleanup bodies remain unchanged.

## Real durable admission before stdin

The new `record.profile['ownedDestinationTransaction']` assignment is MEMORY, not by itself durable intent. It is added to the exact current Scene, under the same existing scene/manager reservation RLock. The new commands method places the complete ordered expressions, expression SHA vector, nonce, expected count and original receipt deadline there BEFORE constructing OwnedLaunch.

The unchanged owning chain is:

1. `OwnedLaunch.__init__` registers its one actual gated PID/start/sealed producer and actual targetArgv `[selected-hyprctl,'repl']` through `Keeper.register`. Register adds that real native-effect job and `Keeper.publish()` invokes the factory's exact writer.
2. `NativeFactory.bind_journal` binds `Keeper.record=self.helper_changed` and its reservation lock to `writer.__self__.manager.lock`. `helper_changed` stores the real helperOwnership and `publish_resource` calls the bound RuntimeService.persist.
3. `RuntimeService.persist` verifies the real held RuntimeLease, then `snapshot()` includes each CURRENT actor Scene's profile (including the transaction expressions/nonce) and helperOwnership in the same snapshot. `JournalStore.write` serializes with checksum/allow_nan=False. `atomic_write` writes a fresh0600 no-follow staging file, fsyncs it, replaces journal.json and fsyncs the directory. Failure latches persistence_failed/manager.closed and raises, so no successful registration/release admission follows.
4. `Keeper.released` writes the release phase through that same fsync chain BEFORE OwnedLaunch sends `G`. There is one real job, not six fabricated jobs. The CLI may exec after G, but no Lua request has been sent yet.
5. After the constructor returns, memory packet.job and packet.ownership are attached. Before the FIRST stdin request, canonical `_guard_destination` performs the unchanged actual fresh `base.clients()` call. In the actual PinnedNativeDesktop assembly its OwnedCommands uses the same canonical ReadonlyIPC. Its register/finish/publish callbacks invoke NativeFactory.readonly_changed -> publish_resource -> the SAME RuntimeService.persist/snapshot/JournalStore/fsync chain. Thus the full intent AND real job link are persisted before the original client guard returns and before the first stdin write. This is a concrete production wiring property, not granted by the CPU fixture's journal list.

The current scene was already durably written by original SceneController.prepare after resolving operation/claiming complete members, before planning. Same reservation RLock serializes these publications with scene ownership. Memory record.current assertions alone cannot establish persistence.

Exact unchanged owning files: owned_launch.py, helper_supervisor.py, native_runtime.py, service_runtime.py, scene_manager.py, readonly_ipc.py and recovery_runtime.py; their bytes/modes are explicit handoff inputs and the complete V27 manifest remains the future ancestor.

## Returned completion and uncertainty

Canonical per-pair Python guards precede each send. For actual PinnedNativeDesktop the existing NativeSession.verify source runs before/after every pair; new selected/sealed CLI material must also match the canonical ReadonlyIPC issuer. The receipt parser requires exact echo + one typed fresh nonce/next-prefix JSON + exact next prompt. Six focus dispatcher returns are known only after prefixes2/4/6 (not CLI exit0). After each pair, native window/output guards recheck immediately before each action and after the second action; the final parent repeats original member/material guards and observes one fresh canonical monitors vector before Keeper.complete.

Normal Keeper.complete still requires the exact exited direct helper and genuine kernel group-empty proof and publishes closed phase through the same journal chain before removing the job. Raw transcript is in the private profile; its final in-memory update is not described as a separate fsynced acknowledgment. The durable native completion boundary remains the actual successful Keeper complete publication, reached ONLY after receipt/EOF/normal-exit/current/material/output checks. A crash before that leaves gated/released native-effect provenance. Original RecoveryCoordinator.preflight rejects EVERY native-export/native-effect whose phase is not closed, even if process/group later disappears; normal NativeFactory.close refuses outstanding jobs after keeper abort. No partial prefix, generic error, zero exit or gone PID waives uncertainty.

## Owning native API and CLI framing

The primary official efb5099 snapshot and actual B13 clean version/core SHA mapping are retained. This is source/version correspondence, not reproducible compiler proof. Installed core's ELF needs liblua.so.5.5. Original native focus helper limit is2s; original motionRefresh IPC limit is1s. Parent remaining=min(2, original receipt deadline-now) bounds write/read/receipt admission; the CLI's internal5s socket timeout does not extend scene authority.

`hl.get_window` -> Internal.windowFromLuaSelectorOrObject -> ViewQuery.selector('address:0x...') validates mapped address/stable_id/PID. ViewQuery.cpp explicitly implements address: matching. LuaMonitor width/height use m_pixelSize; HyprCtl's monitor JSON uses the same fields, as do x/y/scale/transform/id/name. `hl.dispatch(hl.dsp.focus(...))` invokes the SAME monitor/workspace owning dispatcher functions used by original dispatchLua, in original order. The Lua pair checks returned table and exact Boolean ok; its pcall receipt cannot turn a failed or unknown prefix into success. No compositor file IO and no caller Boolean asserting native safety.

Actual unchanged hyprctl repl uses readline and complete per-request server EOF. The first recorded CLI replay used needle matching and proves only fixture framing. The new parser tests consume the actual retained byte stream with exact echo/prompt rules, plus echo forgery/ANSI/duplicate keys/duplicate or prior/out-of-order prefix/partial/refusal cases. Seven actual sealed OwnedLaunch/Keeper CPU cases prove one process/three requests and durable job retention on errors; they do NOT execute owning native Lua. Seven Lua5.5 fixtures prove expression syntax and guard/typed-result behavior against explicit stub APIs; they also do NOT prove compositor effects. The proposal fixture loader compiles proposed source bytes in an isolated module namespace while retaining the original relative-source parent; this CPU setup is not production module-mapping proof. The future frozen actual module binder/real baseline remain required.

## Three genuine refresh calls

The original refresh_destination body remains exact, including actual PinnedNativeDesktop wrapper/session guards. Frozen Windows.qml motionRefresh broadcasts refresh; refresh only starts snapshotProcess if idle, and BarWidget.broadcast invokes the existing live widgets. These source bodies have no new native-write action. The proposal uses max3 bounded observation workers and calls that original method once PER plan (three actual helpers), preserving each original1s IPC. Currency/deadline are checked pre/post; stop/drain is outside the scene lock. Ordered results do not themselves grant validation, captures, seed or baseline acceptance.

## Proof status

V5 formal45 named +2,000×100 PASS. Focused19 parser/real owned CPU cases PASS; Lua5.5 fixture7 PASS. Original first focused fixture projection failure17/18 and both intervening source/proof epochs remain retained. Full original source suite and native acceptance are NOT run or claimed. After root source review, application/full original proof and a fresh UNPROFILED original observer pairing are separate steps; B13 diagnostic/profiler/failure ancestry remains retained.
