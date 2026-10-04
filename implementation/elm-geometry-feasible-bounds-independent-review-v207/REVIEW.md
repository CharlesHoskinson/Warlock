# Independent V204 diagnostic source review

Scoped clear for root's serialized diagnostic launch on the held tuple. This review does not establish native profile outcomes, pixels, input, GTK or full menu recovery. Source ca4b37efeaba17152b834c3faa8913c6cfaba1f5775fe9dfdf55adb4c06d8c2a; V204 manifest909dbbf0c2b0b12c80829e205942fa5412063fbd7802ff857d49735f36299cd3. qa/reviewed-native.py captures final held bytes; it was copied after the author applied review fixes, not an unsafe ancestor control.

## Findings addressed before hold

The initial read lacked an independent connection between selected client ACK geometry and native size, and MAX only checked modes/workarea/restore equality. Held snapshot169–198 now waits for a coherent selected commit/native size+mode, validates the strict journal, compares exact selected geometry to native size (190), and records actual native ownership. Held MAX230–235 binds actual native real rectangle, selected buffer extent and proposed configure dimensions to the ORIGINAL pre-effect prospective projection. This directly checks the monitor-scale conversion rather than trusting only the producer's capability/mode.

The final monitor read formerly could finish after the original transition deadline without a new gate. Held snapshot192/196 now gates immediately after that read and before return; ordinary observation221, MAX235, restore242 and refusal250 use the same original stage deadline. No budget is refreshed inside those snapshot calls. Actual snapshot CPU report1791131747539256302 tests output dimensions/scale and a delayed last monitor read using frozen native data plus an explicitly synthetic carrier. It does not simulate native effect execution.

## Protocol choice, scale and restoration

Held V197 ordinary configure dimensions are proposals; choices obey raw hints. Nonzero MAX dimensions remain mandatory and incompatible proposals refuse before ACK/commit. Fullscreen/resizing proposals are upper bounds, with resizing now journaled. V194 enforces exact configure→ACK→buffer chronology and PID/sequence/current serial/geometry/profile bounds. V204 checks matching selected buffer/native dimensions separately, preserving the distinction between internal journal consistency and native conversion evidence.

V204 uses actual settled ordinary geometry, not --width/height preferences. The initial profile deadline includes ready, native identity, floating setup, processing barriers and coherent native/client snapshot. Restore binds actual original native position/size and chosen geometry, incarnation and owner/workarea dependencies. This tests the ordinary placement actually adopted; it does NOT claim an exact700×500 restore solely because the high-min CLI preferred700×500. A future specifically700×500 acceptance still needs real private resize/ACK/capture.

Monitor1/physical800×600, monitor2/physical1600×1200 and monitor2/physical800×600 run as distinct sessions. Before each intent, output dimensions/scale and actual logical workarea must match the requested profile; buffer scale remains a separate client input. The exact435 runtime descriptor still selects core89/plugin409, with AQ155. No inference transfers from AQ105 source-only preparation. Full runtime/preflight/mapped plugin loading/unloading remains the runner's responsibility and is explicitly tested.

## Receipts, stale data and lifecycle

The strict pinned183 endpoint remains responsible for authenticated process/start/socket identity, exact full intent/binding/protocol/request correlation and dependency validation. Each effect uses a fresh explicit request/generation and context from an admitted observation; the runner checks exact receipt intent/status. MAX must yield a new post-baseline committed client generation and both native/client MAX state, then an admitted projection agreeing with actual geometry. Refusal must preserve the complete fact payload, selected buffer, configure count, native address/position/size/modes and original placement state after a real correlated processing barrier. No retry or synthetic native receipt exists in this runner.

Every profile uses one owned PID-qualified title, exact pinned address and distinct admitted native incarnation. Complete JSON journal prefixes cannot change; fixture refusal is fatal. Cleanup quits each client normally with the original5s exit budget, validates terminal journal and actual empty native census before plugin unload. Cleanup cannot turn the primary failure green. Native transport3s and each action's original absolute6s remain explicit.

## Remaining qualifications

Screenshots/physical-input/GTK/contradictory normalized-rule cases/full08–10 remain open. Journal commits and processing barriers are not presentation receipts. A CLI preference is not geometry evidence. The runner's strict client/native size equality can honestly fail if a future fractional native rectangle is represented differently by integer hyprctl size; preserve and diagnose that failure rather than weakening the oracle. No fractional presentation profile is accepted here. Protocol serial/RGB aliases are rejected among selected serials, but native lifetime/buffer identity still comes from process/role/sequence correlation rather than color alone.

Protected integrity verification binds the entire held V204 inventory, final preflight source/import closure, current CPU reports, profiles and exact core/plugin/AQ/client artifacts. This is evidence integrity/source review, not a new native test.
