# Application pinning and always-on-top

Warlock uses two separate meanings of pinning. An application pin keeps a launcher entry in the taskbar's saved order. Always-on-top is an observed native state of a particular window. The [original interaction contract](../../elm-roadmap/INTERACTION.md) requires these to remain independent.

| Control | Identity and owner | Intended effect |
| --- | --- | --- |
| Pin / Unpin an application | Catalog desktop-entry identity; Elm `Pins` state and adapter preference store | Change saved taskbar membership while preserving other entries' order |
| Always on top | Current native window incarnation and effect authority | Request native pin/unpin and observe the corresponding outcome |

Pinning an application must not make its windows always-on-top. Unpinning an application must not clear an existing window's top state. Changing a window's top state must leave saved launcher membership and order alone. Ordinary activation and either pin operation must not silently become a New instance launch.

## Separate state and effects

Application controls in `Surface` dispatch `Desktop.TogglePin` with a captured view and catalog identity. `Desktop` proposes a `taskbar-pins-write`; the adapter store uses a revision check and atomic save in its selected state directory. The pin list stores identities rather than window handles or top-state flags. A pending or uncertain write needs its own outcome handling.

The window control is labeled **Always on top** and follows the native window-effect path. Its target is the current window incarnation. Native state and the correlated effect outcome establish what happened; saving an application preference cannot establish native success. Likewise, a committed native pin is not evidence that a launcher preference was saved.

This distinction also governs refactoring: preserve the two owners, the two admission paths and the two receipt kinds. Sharing presentation helpers must not merge their authority or persistence semantics.

## Evidence needed for independence

The native journey must observe application pin/unpin while native top state is both false and true, and native pin/unpin while saved application membership and order remain unchanged. Correlate each Saved or Committed receipt to its exact request and authority. Verify the actual labels and applicable pointer, keyboard and AT actions, absence of duplicate launches, and normal owned cleanup.

How a menu is opened is a separate observation from how its control is invoked. A pointer-opened menu followed by keyboard activation demonstrates that control route; it does not prove keyboard-only menu opening. Keep stopped or failed opener routes visible in the evidence.

Current source implements separate routes, but the complete current-tuple native independence observation remains open. Older partial fixtures and source structure do not close the whole UI004 requirement. Consult the [status reference](../reference/status-and-evidence.md), [original acceptance ledger](../../warlock-build-loop/v2/requirement-ledger.json) and [protected verification guide](../how-to/verify-selected-change.md) before relying on a particular result.
