# Retained action, modal routing and reload focus contract

Written before candidate edits. Frozen parent candidate and all negative observations remain evidence.

* Every native action (including focus and menus) and raw QML activation requires an existing enabled item, effective visible ancestors and mapped Qt window. Files modal owner must authorize the item. A modal prompt accepts its own text editing and controls; background commands/actions cannot move focus or mutate background state.
* A logical Home media item keeps its native peer while its path remains the same. A changed path creates a new item/peer and retires the old peer; valid new activation still works. Destroyed file/tree/menu references remain defunct. Delegate rebinds need a separate probe before claiming stable identity beyond media.
* Delayed reload restoration must cancel on any later input/focus intent or superseding request. Its target is tied to the current copied content lifetime; it cannot act after that content is replaced or hidden. The actual deferred-model counterexample is retained before this requirement was implemented.
* Reload records the focused logical control identity/path, restores after its model exists, and never maps a hidden window or activates native desktop focus. Text selection, menu/prompt payload, scroll and existing PersistentProperties state remain intact.
* File operations, scripts and their specification remain byte-identical.

Negative baseline evidence: ../retained-probe/report.json (actual offscreen Qt/V4, no reader claim). Same-PID focused reload is a required improvement, not existing product behavior.

Keyboard/reader focus on a tree row or chevron must reveal it within both the tree viewport and the compact parent sidebar scroller. Preflight at330×320 found row y394 with sidebarScroll0; preserving a focused offscreen row does not satisfy reachable visible focus.
