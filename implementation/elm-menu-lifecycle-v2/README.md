# Bounded menus and correlated native receipts

Fresh derivative of the frozen V1 context-menu component. It addresses resource
and correlation gaps while the separate integration lane owns the live shared
Elm controller and native bar/popup. This does not replace that controller or
claim complete right-click/native acceptance.

`Menu.elm` retains at most 64 rows, 256 UTF-16 units per label, 64 unresolved
commands, and 128 combined distinct binding/output retirements. Duplicate actions
are refused. Malformed opens preserve the last admitted view. A 65th unresolved
command refuses without eviction. A 129th unique retirement permanently exhausts
the instance and closes its view, preserving every outstanding command; valid
correlated receipts can still drain it. Duplicate retirement consumes no slot.
Refusal feedback is clipped without splitting valid surrogate pairs.

`Provider.elm` validates a closed protocol-1 window-provider envelope with a raw
16 KiB UTF-8 bound, canonical nonzero uint64 identities, explicit capabilities,
valid Unicode labels, and distinct row IDs/actions. Strict bounded shapes are
checked before encoding a value; error descriptions never serialize rejected
values. JSON parsing cannot recover duplicate raw object keys; the schema checks
the decoded object and rejects duplicate item/capability identities. Raw string
and already-decoded value entry points have different transport guarantees.

The provider schema supports eight window-action kinds (AlwaysOnTop has two typed
boolean values), so this window-only schema admits at most nine distinct actions.
The generic core's 64-row capacity also supports separately declared action IDs;
it does not advertise 64 different native window operations. App, Files and
background provider schemas remain separate work.

Menu binding authority includes the full native lifetime/session/frontend tuple
and provider/capability generation. Stable window identity excludes frontend and
provider generation, preserving Unknown across rebinds for the same window.
Exact full original binding is required by `ReceiveFor`.

`ReceiptRouter.elm` retains up to 64 mappings from the local menu intent to the
actual native command. Registration verifies the frozen provider/action, complete
native binding, context, incarnation, operation, request and generation. It does
not allocate native IDs or send/retry commands. Minimize/Restore match the existing
effect protocol; other native operations require qualified authority extensions.
Late outcomes update the original mapping after another window completes.
Unknown remains registered; terminal outcomes remove a mapping once. Receipt
revision/output hints never manufacture a native observation.

## Integration contract

Decode provider data with `Provider.decode`/`decodeString`, then admit its menu.
Replace the retained provider only if `Menu.Open` actually admits a new view.
Render labels as text. For a fresh `Menu.Dispatch`, generate the command through
the existing authority engine, register its full tuple before forwarding, and
forward once. Register failure for a new, unsent intent can yield local refusal;
duplicate registration of an existing intent must preserve that pending command.
Never interpret registration failure as proof that an already forwarded command
did not run. Only authenticated broker frames reach `ReceiptRouter.accept`;
decoding a JSON frame does not authenticate its sender.

Apply its correlated `Menu.Msg` and request fresh native observation separately.
Do not resolve Unknown from guessed application state, a refreshed capability
table, or a title match. A real journal/reconciliation producer and combined
controller integration still need native qualification. On terminal retirement
exhaustion, recreate only through the reviewed recovery path; resetting the
component alone would discard unresolved operation protection.

## Evidence

Run QA through the original protected launcher. `qa/replay.py` compiles the actual
core/provider and receipt worker against external fixtures. `qa/mutations.py`
compiles deliberately unsafe implementations and requires the fixtures to reject
them. `qa/model.py` runs the approved bounded abstraction with named witnesses.
`qa/historical.py` feeds captured authentic V1 command/outcome frames through V2;
it is historical protocol compatibility evidence, not a new native execution.

The test-only `RouterReplay.local_receipt` creates a deliberately inconsistent
ledger to test the registry's independent capacity guard. It is not a production
receipt or an accepted native workflow. Final results and remaining gates are in
`HANDOFF.md` and the frozen implementation manifest.
